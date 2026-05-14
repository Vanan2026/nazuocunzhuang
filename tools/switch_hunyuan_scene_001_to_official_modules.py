from __future__ import annotations

import json
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "assets" / "3d" / "modules" / "hunyuan_scene_001" / "manifest.json"
OFFICIAL_DIR = ROOT / "assets" / "3d" / "modules" / "hunyuan_scene_001" / "official"
AUTHORED_RUNTIME_JSON = OFFICIAL_DIR / "hunyuan_scene_001_authored_runtime.json"

GLB_MAGIC = 0x46546C67
JSON_CHUNK = 0x4E4F534A


def fail(msg: str) -> None:
    raise SystemExit(f"FAIL: {msg}")


def read_glb_json(path: Path) -> dict:
    data = path.read_bytes()
    if len(data) < 20:
        fail(f"{path} too short")
    magic, _version, total_len = struct.unpack_from("<III", data, 0)
    if magic != GLB_MAGIC or total_len != len(data):
        fail(f"{path} invalid GLB header")
    offset = 12
    while offset + 8 <= len(data):
        chunk_len, chunk_type = struct.unpack_from("<II", data, offset)
        offset += 8
        chunk = data[offset : offset + chunk_len]
        offset += chunk_len
        if chunk_type == JSON_CHUNK:
            return json.loads(chunk.decode("utf-8"))
    fail(f"{path} missing JSON chunk")


def extract_bounds(gltf: dict) -> tuple[list[float], list[float], int]:
    meshes = gltf.get("meshes", [])
    accessors = gltf.get("accessors", [])
    if not meshes:
        fail("GLB has no meshes")
    mins: list[list[float]] = []
    maxs: list[list[float]] = []
    tri_count = 0
    for mesh in meshes:
        for prim in mesh.get("primitives", []):
            pos_accessor_idx = prim.get("attributes", {}).get("POSITION")
            if pos_accessor_idx is None:
                continue
            accessor = accessors[pos_accessor_idx]
            if "min" in accessor and "max" in accessor:
                mins.append([float(v) for v in accessor["min"]])
                maxs.append([float(v) for v in accessor["max"]])
            idx_accessor_idx = prim.get("indices")
            if idx_accessor_idx is not None:
                idx_accessor = accessors[idx_accessor_idx]
                tri_count += int(idx_accessor.get("count", 0)) // 3
    if not mins:
        fail("GLB has no POSITION bounds")
    min_bound = [min(v[i] for v in mins) for i in range(3)]
    max_bound = [max(v[i] for v in maxs) for i in range(3)]
    return min_bound, max_bound, tri_count


def main() -> None:
    if not MANIFEST_PATH.exists():
        fail(f"missing manifest: {MANIFEST_PATH}")
    if not OFFICIAL_DIR.exists():
        fail(f"missing official directory: {OFFICIAL_DIR}")

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    files = sorted(OFFICIAL_DIR.glob("hunyuan_scene_001_module_*.glb"))
    if not files:
        fail("no official module GLBs found")

    modules = []
    total_tri = 0
    for file in files:
        gltf = read_glb_json(file)
        min_bound, max_bound, tri_count = extract_bounds(gltf)
        total_tri += tri_count
        modules.append(
            {
                "name": file.stem,
                "path": f"res://assets/3d/modules/hunyuan_scene_001/official/{file.name}",
                "vertex_count": None,
                "triangle_count": tri_count,
                "source_triangle_count": tri_count,
                "decimate_stride": 1,
                "min_bound": min_bound,
                "max_bound": max_bound,
            }
        )

    overall = manifest.get("overall", {})
    overall["official_module_count"] = len(modules)
    overall["official_triangles_total"] = total_tri
    if AUTHORED_RUNTIME_JSON.exists():
        authored = json.loads(AUTHORED_RUNTIME_JSON.read_text(encoding="utf-8"))
        if "ground_y" in authored:
            overall["ground_y"] = float(authored["ground_y"])
        overall["authored_runtime_source"] = "res://assets/3d/modules/hunyuan_scene_001/official/hunyuan_scene_001_authored_runtime.json"
    manifest["active_module_pack"] = "official"
    manifest["modules"] = modules
    manifest["overall"] = overall

    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: switched manifest to official modules ({len(modules)} files)")
    print(f"OK: total official triangles={total_tri}")


if __name__ == "__main__":
    main()
