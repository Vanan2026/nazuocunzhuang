"""
Blender helper for offline conversion/cleanup:

Usage:
  blender --background --python tools/blender_convert_hunyuan_scene_001.py -- \
    --input "D:/那个村庄/assets/3d/raw/hunyuan_scene_001/hunyuan_scene_001_raw.ply" \
    --output "D:/那个村庄/assets/3d/processed/hunyuan_scene_001.glb"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import bpy


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args(argv)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)


def import_mesh(path: Path) -> None:
    ext = path.suffix.lower()
    if ext == ".ply":
        bpy.ops.wm.ply_import(filepath=str(path))
    elif ext == ".obj":
        bpy.ops.wm.obj_import(filepath=str(path))
    elif ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(path))
    elif ext in {".glb", ".gltf"}:
        bpy.ops.import_scene.gltf(filepath=str(path))
    else:
        raise ValueError(f"unsupported input extension: {ext}")


def export_glb(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        export_apply=True,
        export_texcoords=True,
        export_normals=True,
        export_colors=True,
        export_materials="EXPORT",
        use_selection=False,
    )


def main() -> None:
    args = parse_args()
    source = Path(args.input).resolve()
    target = Path(args.output).resolve()
    if not source.exists():
        raise SystemExit(f"FAIL: input not found: {source}")

    clear_scene()
    import_mesh(source)
    export_glb(target)
    print(f"OK: converted {source} -> {target}")


if __name__ == "__main__":
    main()
