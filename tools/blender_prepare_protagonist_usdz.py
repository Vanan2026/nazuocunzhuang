from __future__ import annotations

import argparse
import sys
from math import pi, sin
from pathlib import Path

import bpy
from mathutils import Euler


def parse_args() -> argparse.Namespace:
    argv = []
    if "--" in sys.argv:
        argv = sys.argv[sys.argv.index("--") + 1 :]
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input USDZ path")
    parser.add_argument("--output", required=True, help="Output GLB path")
    return parser.parse_args(argv)


def reset_scene() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)


def import_usdz(path: Path) -> None:
    if not path.exists():
        raise RuntimeError(f"input not found: {path}")
    bpy.ops.wm.usd_import(
        filepath=str(path),
        import_usd_preview=True,
        import_guide=False,
        import_proxy=False,
        import_render=True,
    )


def get_armature() -> bpy.types.Object:
    armatures = [obj for obj in bpy.context.scene.objects if obj.type == "ARMATURE"]
    if not armatures:
        raise RuntimeError("no armature found")
    return armatures[0]


def make_action(armature: bpy.types.Object, name: str, frame_end: int) -> bpy.types.Action:
    act = bpy.data.actions.new(name=name)
    armature.animation_data_create()
    armature.animation_data.action = act
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = frame_end
    return act


def set_pose_bone_rotation(armature: bpy.types.Object, bone_name: str, euler_xyz: tuple[float, float, float]) -> None:
    pb = armature.pose.bones.get(bone_name)
    if pb is None:
        return
    pb.rotation_mode = "XYZ"
    pb.rotation_euler = Euler(euler_xyz, "XYZ")
    pb.keyframe_insert(data_path="rotation_euler")


def set_pose_bone_location(armature: bpy.types.Object, bone_name: str, loc_xyz: tuple[float, float, float]) -> None:
    pb = armature.pose.bones.get(bone_name)
    if pb is None:
        return
    pb.location = loc_xyz
    pb.keyframe_insert(data_path="location")


def clear_pose(armature: bpy.types.Object) -> None:
    for pb in armature.pose.bones:
        pb.location = (0.0, 0.0, 0.0)
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = (0.0, 0.0, 0.0)
        pb.scale = (1.0, 1.0, 1.0)


def build_idle(armature: bpy.types.Object) -> None:
    frame_end = 48
    make_action(armature, "idle", frame_end)
    clear_pose(armature)
    for frame in range(1, frame_end + 1):
        phase = (frame - 1) / float(frame_end - 1) * 2.0 * pi
        breath = sin(phase)
        sway = sin(phase * 0.5)
        bpy.context.scene.frame_set(frame)
        set_pose_bone_location(armature, "Hips", (0.0, 0.01 * breath, 0.0))
        set_pose_bone_rotation(armature, "Hips", (0.0, 0.035 * sway, 0.0))
        set_pose_bone_rotation(armature, "Spine", (0.08 + 0.03 * breath, 0.0, 0.0))
        set_pose_bone_rotation(armature, "Spine1", (0.05 + 0.02 * breath, 0.0, 0.0))
        set_pose_bone_rotation(armature, "Spine2", (0.02 + 0.02 * breath, 0.0, 0.0))
        set_pose_bone_rotation(armature, "Neck", (-0.02 * breath, 0.0, 0.0))
        set_pose_bone_rotation(armature, "Head", (-0.01 * breath, 0.0, 0.0))
        set_pose_bone_rotation(armature, "LeftShoulder", (0.0, 0.0, 0.18))
        set_pose_bone_rotation(armature, "RightShoulder", (0.0, 0.0, -0.18))
        set_pose_bone_rotation(armature, "LeftArm", (0.22 + 0.04 * breath, 0.0, 0.14))
        set_pose_bone_rotation(armature, "RightArm", (0.22 + 0.04 * breath, 0.0, -0.14))
        set_pose_bone_rotation(armature, "LeftForeArm", (-0.12, 0.0, 0.0))
        set_pose_bone_rotation(armature, "RightForeArm", (-0.12, 0.0, 0.0))
        set_pose_bone_rotation(armature, "LeftUpLeg", (-0.03, 0.0, 0.0))
        set_pose_bone_rotation(armature, "RightUpLeg", (-0.03, 0.0, 0.0))
        set_pose_bone_rotation(armature, "LeftLeg", (0.06, 0.0, 0.0))
        set_pose_bone_rotation(armature, "RightLeg", (0.06, 0.0, 0.0))


def build_walk(armature: bpy.types.Object) -> None:
    frame_end = 24
    make_action(armature, "walk", frame_end)
    clear_pose(armature)
    for frame in range(1, frame_end + 1):
        phase = (frame - 1) / float(frame_end - 1) * 2.0 * pi
        step = sin(phase)
        lift = max(0.0, -step)
        drop = max(0.0, step)
        sway = sin(phase + pi * 0.5)
        bpy.context.scene.frame_set(frame)
        set_pose_bone_location(armature, "Hips", (0.0, 0.02 * abs(sway) - 0.005, 0.0))
        set_pose_bone_rotation(armature, "Hips", (0.02, 0.08 * step, 0.03 * sway))
        set_pose_bone_rotation(armature, "Spine", (0.09, -0.03 * step, -0.02 * sway))
        set_pose_bone_rotation(armature, "Spine1", (0.05, -0.02 * step, -0.01 * sway))
        set_pose_bone_rotation(armature, "Spine2", (0.03, -0.01 * step, 0.0))
        set_pose_bone_rotation(armature, "LeftShoulder", (0.0, 0.0, 0.18))
        set_pose_bone_rotation(armature, "RightShoulder", (0.0, 0.0, -0.18))
        set_pose_bone_rotation(armature, "LeftArm", (-0.55 * step + 0.15, 0.0, 0.12))
        set_pose_bone_rotation(armature, "RightArm", (0.55 * step + 0.15, 0.0, -0.12))
        set_pose_bone_rotation(armature, "LeftForeArm", (-0.15 - 0.15 * drop, 0.0, 0.0))
        set_pose_bone_rotation(armature, "RightForeArm", (-0.15 - 0.15 * lift, 0.0, 0.0))
        set_pose_bone_rotation(armature, "LeftUpLeg", (0.85 * step, 0.0, 0.02 * sway))
        set_pose_bone_rotation(armature, "RightUpLeg", (-0.85 * step, 0.0, -0.02 * sway))
        set_pose_bone_rotation(armature, "LeftLeg", (1.05 * lift - 0.25 * drop, 0.0, 0.0))
        set_pose_bone_rotation(armature, "RightLeg", (1.05 * drop - 0.25 * lift, 0.0, 0.0))
        set_pose_bone_rotation(armature, "LeftFoot", (-0.3 * lift + 0.22 * drop, 0.0, 0.0))
        set_pose_bone_rotation(armature, "RightFoot", (-0.3 * drop + 0.22 * lift, 0.0, 0.0))


def build_interact(armature: bpy.types.Object) -> None:
    make_action(armature, "interact", 30)
    clear_pose(armature)
    keys = (
        (1, 0.0, 0.0, 0.0),
        (8, 0.45, -0.9, 0.12),
        (16, 0.35, -0.65, 0.08),
        (24, 0.55, -1.1, 0.16),
        (30, 0.0, 0.0, 0.0),
    )
    for frame, arm_lift, forearm_bend, spine_bend in keys:
        bpy.context.scene.frame_set(frame)
        set_pose_bone_rotation(armature, "Spine", (0.10 + spine_bend, 0.0, 0.0))
        set_pose_bone_rotation(armature, "Spine1", (0.05 + spine_bend * 0.7, 0.0, 0.0))
        set_pose_bone_rotation(armature, "RightArm", (arm_lift, 0.0, -0.1))
        set_pose_bone_rotation(armature, "RightForeArm", (forearm_bend, 0.0, 0.0))
        set_pose_bone_rotation(armature, "RightHand", (0.2, 0.0, 0.0))
        set_pose_bone_rotation(armature, "LeftArm", (0.18, 0.0, 0.12))
        set_pose_bone_rotation(armature, "LeftForeArm", (-0.2, 0.0, 0.0))


def build_sit_down(armature: bpy.types.Object) -> None:
    make_action(armature, "sit_down", 20)
    clear_pose(armature)
    for frame, hip_drop, leg_bend in ((1, 0.0, 0.0), (10, -0.08, -0.7), (20, -0.16, -1.25)):
        bpy.context.scene.frame_set(frame)
        set_pose_bone_location(armature, "Hips", (0.0, hip_drop, 0.0))
        set_pose_bone_rotation(armature, "Hips", (0.03, 0.0, 0.0))
        set_pose_bone_rotation(armature, "LeftUpLeg", (leg_bend, 0.0, 0.0))
        set_pose_bone_rotation(armature, "RightUpLeg", (leg_bend, 0.0, 0.0))
        set_pose_bone_rotation(armature, "LeftLeg", (abs(leg_bend) * 0.95, 0.0, 0.0))
        set_pose_bone_rotation(armature, "RightLeg", (abs(leg_bend) * 0.95, 0.0, 0.0))
        set_pose_bone_rotation(armature, "Spine", (0.24, 0.0, 0.0))
        set_pose_bone_rotation(armature, "LeftArm", (0.12, 0.0, 0.06))
        set_pose_bone_rotation(armature, "RightArm", (0.12, 0.0, -0.06))


def build_sit_idle(armature: bpy.types.Object) -> None:
    frame_end = 40
    make_action(armature, "sit_idle", frame_end)
    clear_pose(armature)
    for frame in range(1, frame_end + 1):
        phase = (frame - 1) / float(frame_end - 1) * 2.0 * pi
        breath = sin(phase)
        bpy.context.scene.frame_set(frame)
        set_pose_bone_location(armature, "Hips", (0.0, -0.16 + 0.01 * breath, 0.0))
        set_pose_bone_rotation(armature, "Hips", (0.03, 0.03 * breath, 0.0))
        set_pose_bone_rotation(armature, "LeftUpLeg", (-1.25, 0.0, 0.0))
        set_pose_bone_rotation(armature, "RightUpLeg", (-1.25, 0.0, 0.0))
        set_pose_bone_rotation(armature, "LeftLeg", (1.15, 0.0, 0.0))
        set_pose_bone_rotation(armature, "RightLeg", (1.15, 0.0, 0.0))
        set_pose_bone_rotation(armature, "Spine", (0.24 + 0.03 * breath, 0.0, 0.0))
        set_pose_bone_rotation(armature, "Spine1", (0.14 + 0.02 * breath, 0.0, 0.0))
        set_pose_bone_rotation(armature, "Head", (-0.06 - 0.02 * breath, 0.0, 0.0))
        set_pose_bone_rotation(armature, "LeftArm", (0.22, 0.0, 0.10))
        set_pose_bone_rotation(armature, "RightArm", (0.22, 0.0, -0.10))


def build_stand_up(armature: bpy.types.Object) -> None:
    make_action(armature, "stand_up", 20)
    clear_pose(armature)
    for frame, hip_drop, leg_bend, spine in ((1, -0.16, -1.25, 0.24), (10, -0.08, -0.7, 0.16), (20, 0.0, 0.0, 0.0)):
        bpy.context.scene.frame_set(frame)
        set_pose_bone_location(armature, "Hips", (0.0, hip_drop, 0.0))
        set_pose_bone_rotation(armature, "LeftUpLeg", (leg_bend, 0.0, 0.0))
        set_pose_bone_rotation(armature, "RightUpLeg", (leg_bend, 0.0, 0.0))
        set_pose_bone_rotation(armature, "LeftLeg", (abs(leg_bend) * 0.95, 0.0, 0.0))
        set_pose_bone_rotation(armature, "RightLeg", (abs(leg_bend) * 0.95, 0.0, 0.0))
        set_pose_bone_rotation(armature, "Spine", (spine, 0.0, 0.0))


def tune_animation_curves() -> None:
    for action in bpy.data.actions:
        for fcurve in action.fcurves:
            for kp in fcurve.keyframe_points:
                kp.interpolation = "LINEAR"


def export_glb(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        export_yup=True,
        export_animations=True,
        export_nla_strips=False,
        export_force_sampling=True,
        export_frame_step=1,
        export_skins=True,
        export_all_influences=True,
        export_materials="EXPORT",
    )


def main() -> None:
    args = parse_args()
    inp = Path(args.input).resolve()
    out = Path(args.output).resolve()
    reset_scene()
    import_usdz(inp)
    armature = get_armature()
    build_idle(armature)
    build_walk(armature)
    build_interact(armature)
    build_sit_down(armature)
    build_sit_idle(armature)
    build_stand_up(armature)
    tune_animation_curves()
    export_glb(out)
    print(f"OK: exported protagonist glb -> {out}")
    print(f"OK: actions={','.join(sorted(a.name for a in bpy.data.actions))}")


if __name__ == "__main__":
    main()
