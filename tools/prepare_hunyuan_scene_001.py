from __future__ import annotations

import json
import shutil
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ASSET_DIR = ROOT / "scenes" / "3d"
RAW_TARGET_DIR = ROOT / "assets" / "3d" / "raw" / "hunyuan_scene_001"
PROCESSED_FILE = ROOT / "assets" / "3d" / "processed" / "hunyuan_scene_001.glb"

GLB_MAGIC = 0x46546C67
JSON_CHUNK = 0x4E4F534A
BIN_CHUNK = 0x004E4942

PLY_SCALAR_TYPES = {
    "char": ("b", 1),
    "uchar": ("B", 1),
    "short": ("h", 2),
    "ushort": ("H", 2),
    "int": ("i", 4),
    "uint": ("I", 4),
    "float": ("f", 4),
    "double": ("d", 8),
}


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def pick_source() -> Path:
    if not SOURCE_ASSET_DIR.exists():
        fail(f"source asset path missing: {SOURCE_ASSET_DIR}")

    candidates = [p for p in SOURCE_ASSET_DIR.iterdir() if p.is_file() and p.suffix.lower() in {".ply", ".glb", ".gltf"}]
    if not candidates:
        fail(f"no source mesh found in {SOURCE_ASSET_DIR}")

    # Prefer PLY from Hunyuan scene dumps; fallback to latest GLB/GLTF.
    candidates.sort(key=lambda p: (0 if p.suffix.lower() == ".ply" else 1, -p.stat().st_mtime))
    return candidates[0]


def pad4(data: bytes, filler: bytes) -> bytes:
    rem = len(data) % 4
    return data if rem == 0 else data + filler * (4 - rem)


def read_glb_json_bin(path: Path) -> tuple[int, dict, bytes | None]:
    data = path.read_bytes()
    if len(data) < 20:
        fail(f"{path.name} too short")
    magic, version, total_len = struct.unpack_from("<III", data, 0)
    if magic != GLB_MAGIC:
        fail(f"{path.name} invalid GLB magic")
    if total_len != len(data):
        fail(f"{path.name} length mismatch")

    offset = 12
    gltf_json: dict | None = None
    bin_chunk: bytes | None = None
    while offset + 8 <= len(data):
        chunk_len, chunk_type = struct.unpack_from("<II", data, offset)
        offset += 8
        chunk = data[offset : offset + chunk_len]
        offset += chunk_len
        if chunk_type == JSON_CHUNK:
            gltf_json = json.loads(chunk.decode("utf-8"))
        elif chunk_type == BIN_CHUNK:
            bin_chunk = chunk
    if gltf_json is None:
        fail(f"{path.name} missing JSON chunk")
    return version, gltf_json, bin_chunk


def write_glb(path: Path, version: int, gltf_json: dict, bin_chunk: bytes | None) -> None:
    json_bytes = json.dumps(gltf_json, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    json_bytes = pad4(json_bytes, b" ")
    body = struct.pack("<II", len(json_bytes), JSON_CHUNK) + json_bytes
    if bin_chunk is not None:
        bin_bytes = pad4(bin_chunk, b"\x00")
        body += struct.pack("<II", len(bin_bytes), BIN_CHUNK) + bin_bytes
    header = struct.pack("<III", GLB_MAGIC, version, 12 + len(body))
    path.write_bytes(header + body)


def ensure_firstpass_material(gltf_json: dict) -> int:
    mats = gltf_json.setdefault("materials", [])
    idx = len(mats)
    mats.append(
        {
            "name": "HunyuanScene001_FirstPass",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.84, 0.78, 0.71, 1.0],
                "metallicFactor": 0.0,
                "roughnessFactor": 0.94,
            },
        }
    )
    return idx


def bind_material(gltf_json: dict, material_index: int) -> None:
    for mesh in gltf_json.get("meshes", []):
        for prim in mesh.get("primitives", []):
            prim["material"] = material_index


def scalar_from(data: bytes, offset: int, scalar_type: str) -> tuple[int | float, int]:
    if scalar_type not in PLY_SCALAR_TYPES:
        fail(f"unsupported PLY scalar type: {scalar_type}")
    fmt, size = PLY_SCALAR_TYPES[scalar_type]
    value = struct.unpack_from("<" + fmt, data, offset)[0]
    return value, offset + size


def parse_ply_binary(path: Path) -> tuple[list[float], list[int], list[int], list[int]]:
    data = path.read_bytes()
    header_end = data.find(b"end_header\n")
    if header_end == -1:
        fail(f"{path.name} missing PLY end_header")

    header_blob = data[: header_end + len(b"end_header\n")]
    body = data[header_end + len(b"end_header\n") :]
    lines = header_blob.decode("ascii", errors="ignore").splitlines()

    if len(lines) < 2 or lines[0].strip() != "ply":
        fail(f"{path.name} is not a valid PLY file")
    if not any(line.startswith("format binary_little_endian") for line in lines):
        fail(f"{path.name} format must be binary_little_endian")

    vertex_count = 0
    face_count = 0
    current_element = ""
    vertex_props: list[tuple[str, str]] = []
    face_list_prop: tuple[str, str, str] | None = None
    for raw in lines:
        tokens = raw.strip().split()
        if not tokens:
            continue
        if tokens[0] == "element" and len(tokens) == 3:
            current_element = tokens[1]
            if current_element == "vertex":
                vertex_count = int(tokens[2])
            elif current_element == "face":
                face_count = int(tokens[2])
        elif tokens[0] == "property":
            if current_element == "vertex" and len(tokens) == 3:
                vertex_props.append((tokens[1], tokens[2]))
            elif current_element == "face" and len(tokens) == 5 and tokens[1] == "list":
                face_list_prop = (tokens[2], tokens[3], tokens[4])

    if vertex_count <= 0 or face_count <= 0:
        fail(f"{path.name} missing vertex/face data")
    if face_list_prop is None:
        fail(f"{path.name} missing face list property")

    vx_idx = next((i for i, (_, n) in enumerate(vertex_props) if n == "x"), -1)
    vy_idx = next((i for i, (_, n) in enumerate(vertex_props) if n == "y"), -1)
    vz_idx = next((i for i, (_, n) in enumerate(vertex_props) if n == "z"), -1)
    if vx_idx == -1 or vy_idx == -1 or vz_idx == -1:
        fail(f"{path.name} vertex properties must include x/y/z")

    cr_idx = next((i for i, (_, n) in enumerate(vertex_props) if n in {"red", "r"}), -1)
    cg_idx = next((i for i, (_, n) in enumerate(vertex_props) if n in {"green", "g"}), -1)
    cb_idx = next((i for i, (_, n) in enumerate(vertex_props) if n in {"blue", "b"}), -1)

    positions: list[float] = []
    colors: list[int] = []
    indices: list[int] = []
    offset = 0

    for _ in range(vertex_count):
        values: list[int | float] = []
        for scalar_type, _name in vertex_props:
            value, offset = scalar_from(body, offset, scalar_type)
            values.append(value)
        positions.extend([float(values[vx_idx]), float(values[vy_idx]), float(values[vz_idx])])
        if cr_idx != -1 and cg_idx != -1 and cb_idx != -1:
            colors.extend([int(values[cr_idx]) & 0xFF, int(values[cg_idx]) & 0xFF, int(values[cb_idx]) & 0xFF])
        else:
            colors.extend([214, 196, 176])

    count_type, index_type, _prop_name = face_list_prop
    for _ in range(face_count):
        vert_count_raw, offset = scalar_from(body, offset, count_type)
        vert_count = int(vert_count_raw)
        face: list[int] = []
        for _i in range(vert_count):
            idx, offset = scalar_from(body, offset, index_type)
            face.append(int(idx))
        if len(face) >= 3:
            for i in range(1, len(face) - 1):
                indices.extend([face[0], face[i], face[i + 1]])

    return positions, colors, indices, [vertex_count, len(indices) // 3]


def build_glb_from_mesh(positions: list[float], colors: list[int], indices: list[int]) -> tuple[dict, bytes]:
    pos_bytes = struct.pack("<" + "f" * len(positions), *positions)
    color_bytes = bytes(colors)
    idx_bytes = struct.pack("<" + "I" * len(indices), *indices)

    offset = 0
    pos_off = offset
    offset += len(pos_bytes)
    offset = (offset + 3) & ~3
    color_off = offset
    offset += len(color_bytes)
    offset = (offset + 3) & ~3
    idx_off = offset
    offset += len(idx_bytes)

    bin_blob = bytearray(offset)
    bin_blob[pos_off : pos_off + len(pos_bytes)] = pos_bytes
    bin_blob[color_off : color_off + len(color_bytes)] = color_bytes
    bin_blob[idx_off : idx_off + len(idx_bytes)] = idx_bytes

    xyz = list(zip(positions[0::3], positions[1::3], positions[2::3]))
    min_xyz = [min(c[i] for c in xyz) for i in range(3)]
    max_xyz = [max(c[i] for c in xyz) for i in range(3)]

    gltf_json = {
        "asset": {"version": "2.0", "generator": "prepare_hunyuan_scene_001.py"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": "hunyuan_scene_001"}],
        "buffers": [{"byteLength": len(bin_blob)}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": pos_off, "byteLength": len(pos_bytes), "target": 34962},
            {"buffer": 0, "byteOffset": color_off, "byteLength": len(color_bytes), "target": 34962},
            {"buffer": 0, "byteOffset": idx_off, "byteLength": len(idx_bytes), "target": 34963},
        ],
        "accessors": [
            {
                "bufferView": 0,
                "componentType": 5126,
                "count": len(positions) // 3,
                "type": "VEC3",
                "min": min_xyz,
                "max": max_xyz,
            },
            {
                "bufferView": 1,
                "componentType": 5121,
                "count": len(colors) // 3,
                "type": "VEC3",
                "normalized": True,
            },
            {"bufferView": 2, "componentType": 5125, "count": len(indices), "type": "SCALAR"},
        ],
        "materials": [
            {
                "name": "HunyuanScene001_FirstPass",
                "pbrMetallicRoughness": {
                    "baseColorFactor": [0.84, 0.78, 0.71, 1.0],
                    "metallicFactor": 0.0,
                    "roughnessFactor": 0.94,
                }
            }
        ],
        "meshes": [
            {
                "name": "hunyuan_scene_001_mesh",
                "primitives": [
                    {"attributes": {"POSITION": 0, "COLOR_0": 1}, "indices": 2, "mode": 4, "material": 0}
                ],
            }
        ],
    }
    return gltf_json, bytes(bin_blob)


def process_source(source: Path) -> Path:
    RAW_TARGET_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)

    raw_target_file = RAW_TARGET_DIR / f"hunyuan_scene_001_raw{source.suffix.lower()}"
    shutil.copy2(source, raw_target_file)

    if source.suffix.lower() == ".ply":
        positions, colors, indices, stats = parse_ply_binary(source)
        gltf_json, bin_blob = build_glb_from_mesh(positions, colors, indices)
        write_glb(PROCESSED_FILE, version=2, gltf_json=gltf_json, bin_chunk=bin_blob)
        print(
            "OK: converted PLY -> GLB "
            f"(vertices={stats[0]}, triangles={stats[1]})"
        )
    else:
        version, gltf_json, bin_chunk = read_glb_json_bin(source)
        mat_index = ensure_firstpass_material(gltf_json)
        bind_material(gltf_json, mat_index)
        write_glb(PROCESSED_FILE, version=version, gltf_json=gltf_json, bin_chunk=bin_chunk)
        print("OK: first-pass material bound to GLB source")

    return raw_target_file


def main() -> None:
    source = pick_source()
    raw_target_file = process_source(source)

    print(f"OK: source -> {source}")
    print(f"OK: copied raw -> {raw_target_file}")
    print(f"OK: wrote processed -> {PROCESSED_FILE}")


if __name__ == "__main__":
    main()
