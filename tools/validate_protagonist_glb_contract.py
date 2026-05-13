from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIR = ROOT / "assets" / "3d" / "processed"
LEGACY_DIR = ROOT / "production" / "assets" / "protagonist_3d" / "recolored"

REQUIRED_CLIPS = ("idle", "walk", "interact", "sit_down", "sit_idle", "stand_up")


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def load_glb_json(path: Path) -> dict:
    data = path.read_bytes()
    require(len(data) >= 20, f"{path.name} is too short")
    magic, _version, total_len = struct.unpack_from("<III", data, 0)
    require(magic == 0x46546C67, f"{path.name} invalid GLB magic")
    require(total_len == len(data), f"{path.name} header length mismatch")
    offset = 12
    chunk_len, chunk_type = struct.unpack_from("<II", data, offset)
    offset += 8
    require(chunk_type == 0x4E4F534A, f"{path.name} first chunk is not JSON")
    return json.loads(data[offset : offset + chunk_len].decode("utf-8"))


def has_attr(gltf: dict, attr_name: str) -> bool:
    for mesh in gltf.get("meshes", []):
        for prim in mesh.get("primitives", []):
            if attr_name in prim.get("attributes", {}):
                return True
    return False


def clip_names(gltf: dict) -> list[str]:
    names: list[str] = []
    for i, clip in enumerate(gltf.get("animations", [])):
        raw = str(clip.get("name", "")).strip().lower()
        names.append(raw if raw else f"unnamed_{i}")
    return names


def validate_single(path: Path) -> list[str]:
    gltf = load_glb_json(path)
    issues: list[str] = []

    if len(gltf.get("meshes", [])) == 0:
        issues.append("no meshes")
    if len(gltf.get("skins", [])) == 0:
        issues.append("no skin rig")
    if len(gltf.get("animations", [])) == 0:
        issues.append("no animation clip")
    if len(gltf.get("materials", [])) == 0:
        issues.append("no material")
    if len(gltf.get("textures", [])) == 0:
        issues.append("no texture payload")
    if not has_attr(gltf, "TEXCOORD_0"):
        issues.append("missing TEXCOORD_0")
    if not has_attr(gltf, "POSITION"):
        issues.append("missing POSITION")
    if not has_attr(gltf, "NORMAL"):
        issues.append("missing NORMAL")
    if not has_attr(gltf, "JOINTS_0"):
        issues.append("missing JOINTS_0")
    if not has_attr(gltf, "WEIGHTS_0"):
        issues.append("missing WEIGHTS_0")

    names = clip_names(gltf)
    if any(name == "armature" for name in names):
        issues.append("generic animation name 'Armature'")

    return issues


def validate_clip_pack(paths: list[Path]) -> list[str]:
    found_names: set[str] = set()
    for path in paths:
        names = clip_names(load_glb_json(path))
        found_names.update(names)

    missing = [name for name in REQUIRED_CLIPS if name not in found_names]
    return [f"missing required clip name '{name}' in current pack" for name in missing]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", dest="target_dir", default="", help="Directory containing GLB files")
    parser.add_argument("--pattern", dest="pattern", default="*.glb", help="Glob pattern for GLB selection")
    args = parser.parse_args()

    if args.target_dir:
        target_dir = Path(args.target_dir).resolve()
    elif DEFAULT_DIR.exists():
        target_dir = DEFAULT_DIR
    else:
        target_dir = LEGACY_DIR

    paths = sorted(target_dir.glob(args.pattern))
    require(paths, f"no GLBs found in {target_dir} with pattern {args.pattern}")

    has_error = False
    for path in paths:
        issues = validate_single(path)
        if issues:
            has_error = True
            print(f"FILE {path.name}")
            for issue in issues:
                print(f"  - {issue}")

    pack_issues = validate_clip_pack(paths)
    if pack_issues:
        has_error = True
        print("PACK")
        for issue in pack_issues:
            print(f"  - {issue}")

    if has_error:
        raise SystemExit(1)

    print(f"OK: protagonist GLB contract validated ({target_dir})")


if __name__ == "__main__":
    main()
