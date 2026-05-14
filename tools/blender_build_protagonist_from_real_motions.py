from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import bpy
from mathutils import Quaternion


@dataclass
class ClipSpec:
    name: str
    source_path: Path
    source_start: int
    source_end: int
    in_place: bool
    loop: bool


def parse_args() -> argparse.Namespace:
    argv = []
    if "--" in sys.argv:
        argv = sys.argv[sys.argv.index("--") + 1 :]
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-usdz", required=True, help="Target protagonist USDZ")
    parser.add_argument("--motions-dir", required=True, help="Directory containing source motion GLBs")
    parser.add_argument("--output", required=True, help="Output GLB path")
    return parser.parse_args(argv)


def reset_scene() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)


def import_target_usdz(path: Path) -> bpy.types.Object:
    bpy.ops.wm.usd_import(
        filepath=str(path),
        import_usd_preview=True,
        import_guide=False,
        import_proxy=False,
        import_render=True,
    )
    arms = [obj for obj in bpy.context.scene.objects if obj.type == "ARMATURE"]
    if not arms:
        raise RuntimeError("no armature found in target usdz")
    return arms[0]


def import_source_armature(path: Path) -> tuple[bpy.types.Object, bpy.types.Action]:
    before = {obj.name for obj in bpy.context.scene.objects}
    bpy.ops.import_scene.gltf(filepath=str(path))
    new_objs = [obj for obj in bpy.context.scene.objects if obj.name not in before]
    arms = [obj for obj in new_objs if obj.type == "ARMATURE"]
    if not arms:
        raise RuntimeError(f"no armature found in source glb: {path}")
    arm = arms[0]
    acts = list(bpy.data.actions)
    if not acts:
        raise RuntimeError(f"no action found in source glb: {path}")
    action = acts[-1]
    arm.animation_data_create()
    arm.animation_data.action = action
    return arm, action


def clear_target_pose(target_arm: bpy.types.Object) -> None:
    for pb in target_arm.pose.bones:
        pb.location = (0.0, 0.0, 0.0)
        pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = Quaternion((1.0, 0.0, 0.0, 0.0))
        pb.scale = (1.0, 1.0, 1.0)


def retarget_clip(target_arm: bpy.types.Object, source_arm: bpy.types.Object, spec: ClipSpec) -> bpy.types.Action:
    frame_count = spec.source_end - spec.source_start + 1
    if frame_count < 2:
        raise RuntimeError(f"clip too short: {spec.name}")

    action = bpy.data.actions.new(name=spec.name)
    target_arm.animation_data_create()
    target_arm.animation_data.action = action
    clear_target_pose(target_arm)

    src_hips = source_arm.pose.bones.get("Hips")
    baseline_hips = None
    if src_hips is not None:
        bpy.context.scene.frame_set(spec.source_start)
        baseline_hips = src_hips.location.copy()

    common_names = [pb.name for pb in target_arm.pose.bones if source_arm.pose.bones.get(pb.name) is not None]
    for dst_idx, src_frame in enumerate(range(spec.source_start, spec.source_end + 1), start=1):
        bpy.context.scene.frame_set(src_frame)
        for bone_name in common_names:
            src_pb = source_arm.pose.bones[bone_name]
            dst_pb = target_arm.pose.bones[bone_name]

            dst_pb.rotation_mode = "QUATERNION"
            dst_pb.rotation_quaternion = src_pb.rotation_quaternion.copy()
            dst_pb.scale = src_pb.scale.copy()

            loc = src_pb.location.copy()
            if spec.in_place and bone_name == "Hips" and baseline_hips is not None:
                loc.x -= baseline_hips.x
                loc.z -= baseline_hips.z
            dst_pb.location = loc

            dst_pb.keyframe_insert(data_path="location", frame=dst_idx)
            dst_pb.keyframe_insert(data_path="rotation_quaternion", frame=dst_idx)
            dst_pb.keyframe_insert(data_path="scale", frame=dst_idx)

    for fcurve in action.fcurves:
        for kp in fcurve.keyframe_points:
            kp.interpolation = "LINEAR"

    if spec.loop:
        frame_end = frame_count
        for fcurve in action.fcurves:
            if "pose.bones" not in fcurve.data_path:
                continue
            first = fcurve.evaluate(1.0)
            fcurve.keyframe_points.insert(frame_end, first, options={"FAST"})
            for kp in fcurve.keyframe_points:
                kp.interpolation = "LINEAR"

    return action


def get_target_export_nodes(target_arm: bpy.types.Object) -> list[bpy.types.Object]:
    export_nodes = [target_arm]
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH":
            continue
        for mod in obj.modifiers:
            if mod.type == "ARMATURE" and mod.object == target_arm:
                export_nodes.append(obj)
                break
    return export_nodes


def export_target_glb(output: Path, target_arm: bpy.types.Object) -> None:
    nodes = get_target_export_nodes(target_arm)
    if len(nodes) < 2:
        raise RuntimeError("target mesh objects bound to armature not found")

    bpy.ops.object.select_all(action="DESELECT")
    for node in nodes:
        node.select_set(True)
    bpy.context.view_layer.objects.active = target_arm

    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(output),
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_animations=True,
        export_nla_strips=False,
        export_force_sampling=True,
        export_frame_step=1,
        export_skins=True,
        export_all_influences=True,
        export_materials="EXPORT",
    )


def build_clip_specs(motions_dir: Path) -> list[ClipSpec]:
    walk_src = motions_dir / "5571ddffb0e493df35384702913f5f41_tinted.glb"
    long_src = motions_dir / "cb790243ea4e7e4dbf40fc8d995eff5d_tinted.glb"
    sit_src = motions_dir / "effad4009179ed5681340ba9adc2b0a0_tinted.glb"
    missing = [p for p in (walk_src, long_src, sit_src) if not p.exists()]
    if missing:
        raise RuntimeError("missing source motion glb: " + ", ".join(str(p) for p in missing))

    return [
        ClipSpec("idle", long_src, 2, 49, in_place=True, loop=True),
        ClipSpec("walk", walk_src, 1, 37, in_place=True, loop=True),
        ClipSpec("interact", long_src, 185, 222, in_place=True, loop=False),
        ClipSpec("sit_down", sit_src, 50, 71, in_place=True, loop=False),
        ClipSpec("sit_idle", sit_src, 71, 82, in_place=True, loop=True),
        ClipSpec("stand_up", sit_src, 71, 93, in_place=True, loop=False),
    ]


def main() -> None:
    args = parse_args()
    target_usdz = Path(args.target_usdz).resolve()
    motions_dir = Path(args.motions_dir).resolve()
    output = Path(args.output).resolve()

    if not target_usdz.exists():
        raise RuntimeError(f"target usdz not found: {target_usdz}")
    if not motions_dir.exists():
        raise RuntimeError(f"motions dir not found: {motions_dir}")

    reset_scene()
    target_arm = import_target_usdz(target_usdz)
    clips = build_clip_specs(motions_dir)

    generated_names: list[str] = []
    for clip in clips:
        source_arm, _source_action = import_source_armature(clip.source_path)
        retarget_clip(target_arm, source_arm, clip)
        generated_names.append(clip.name)

    export_target_glb(output, target_arm)
    print(f"OK: exported protagonist from real motions -> {output}")
    print("OK: clips=" + ",".join(generated_names))


if __name__ == "__main__":
    main()
