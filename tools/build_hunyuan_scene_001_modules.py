from __future__ import annotations

import json
import math
import struct
from dataclasses import dataclass
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RAW_PLY = ROOT / "assets" / "3d" / "raw" / "hunyuan_scene_001" / "hunyuan_scene_001_raw.ply"
MODULE_DIR = ROOT / "assets" / "3d" / "modules" / "hunyuan_scene_001"
MANIFEST_PATH = MODULE_DIR / "manifest.json"
PREVIEW_SCENE = ROOT / "scenes" / "dev" / "hunyuan_scene_001_preview.tscn"

GRID_ROWS = 2
GRID_COLS = 2
MAX_TRIANGLES_PER_MODULE = 120_000

GLB_MAGIC = 0x46546C67
JSON_CHUNK = 0x4E4F534A
BIN_CHUNK = 0x004E4942

PLY_NUMPY_TYPES = {
    "char": "i1",
    "uchar": "u1",
    "short": "<i2",
    "ushort": "<u2",
    "int": "<i4",
    "uint": "<u4",
    "float": "<f4",
    "double": "<f8",
}


@dataclass
class ModuleBuild:
    name: str
    rel_path: str
    vertex_count: int
    triangle_count: int
    source_triangle_count: int
    decimate_stride: int
    min_bound: list[float]
    max_bound: list[float]


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def parse_ply_header(data: bytes) -> tuple[dict, int]:
    header_end = data.find(b"end_header\n")
    if header_end == -1:
        fail("PLY missing end_header")
    header_bytes = data[: header_end + len(b"end_header\n")]
    lines = header_bytes.decode("ascii", errors="ignore").splitlines()

    if not lines or lines[0].strip() != "ply":
        fail("invalid PLY header")
    if not any(line.startswith("format binary_little_endian") for line in lines):
        fail("only binary_little_endian PLY is supported")

    vertex_count = 0
    face_count = 0
    vertex_props: list[tuple[str, str]] = []
    current_element = ""
    face_list_prop: tuple[str, str] | None = None

    for line in lines:
        parts = line.strip().split()
        if not parts:
            continue
        if parts[0] == "element" and len(parts) == 3:
            current_element = parts[1]
            if current_element == "vertex":
                vertex_count = int(parts[2])
            elif current_element == "face":
                face_count = int(parts[2])
        elif parts[0] == "property":
            if current_element == "vertex" and len(parts) == 3:
                vertex_props.append((parts[1], parts[2]))
            elif current_element == "face" and len(parts) == 5 and parts[1] == "list":
                face_list_prop = (parts[2], parts[3])

    if vertex_count <= 0 or face_count <= 0:
        fail("vertex or face count is zero")
    if not vertex_props:
        fail("missing vertex properties")
    if face_list_prop is None:
        fail("missing face list property")
    if face_list_prop != ("uchar", "uint"):
        fail(f"unsupported face list scalar/index types: {face_list_prop}")

    return {
        "vertex_count": vertex_count,
        "face_count": face_count,
        "vertex_props": vertex_props,
    }, header_end + len(b"end_header\n")


def load_ply(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if not path.exists():
        fail(f"raw PLY not found: {path}")

    data = path.read_bytes()
    header, offset = parse_ply_header(data)
    vertex_count = header["vertex_count"]
    face_count = header["face_count"]
    vertex_props = header["vertex_props"]

    dtype_items = []
    for scalar_type, prop_name in vertex_props:
        np_type = PLY_NUMPY_TYPES.get(scalar_type)
        if np_type is None:
            fail(f"unsupported vertex scalar type: {scalar_type}")
        dtype_items.append((prop_name, np_type))
    vertex_dtype = np.dtype(dtype_items)

    vertices = np.frombuffer(data, dtype=vertex_dtype, count=vertex_count, offset=offset)
    offset += vertex_count * vertex_dtype.itemsize

    face_dtype = np.dtype([("n", "u1"), ("i0", "<u4"), ("i1", "<u4"), ("i2", "<u4")])
    faces_raw = np.frombuffer(data, dtype=face_dtype, count=face_count, offset=offset)
    if np.any(faces_raw["n"] != 3):
        fail("non-triangle faces detected; expected triangulated mesh")

    positions = np.column_stack([vertices["x"], vertices["y"], vertices["z"]]).astype(np.float32, copy=False)

    if {"red", "green", "blue"}.issubset(vertices.dtype.names):
        colors = np.column_stack([vertices["red"], vertices["green"], vertices["blue"]]).astype(np.uint8, copy=False)
    else:
        colors = np.full((positions.shape[0], 3), [214, 196, 176], dtype=np.uint8)

    faces = np.column_stack([faces_raw["i0"], faces_raw["i1"], faces_raw["i2"]]).astype(np.uint32, copy=False)
    return positions, colors, faces


def pad4(blob: bytes, fill: bytes) -> bytes:
    rem = len(blob) % 4
    if rem == 0:
        return blob
    return blob + fill * (4 - rem)


def write_glb(path: Path, gltf_json: dict, bin_blob: bytes) -> None:
    json_blob = json.dumps(gltf_json, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    json_blob = pad4(json_blob, b" ")
    bin_blob = pad4(bin_blob, b"\x00")

    body = struct.pack("<II", len(json_blob), JSON_CHUNK) + json_blob
    body += struct.pack("<II", len(bin_blob), BIN_CHUNK) + bin_blob
    header = struct.pack("<III", GLB_MAGIC, 2, 12 + len(body))
    path.write_bytes(header + body)


def build_glb_arrays(positions: np.ndarray, colors: np.ndarray, faces: np.ndarray) -> tuple[dict, bytes]:
    pos = positions.astype("<f4", copy=False)
    col = colors.astype(np.uint8, copy=False)
    idx = faces.astype("<u4", copy=False).reshape(-1)

    pos_bytes = pos.tobytes()
    col_bytes = col.tobytes()
    idx_bytes = idx.tobytes()

    pos_offset = 0
    col_offset = (pos_offset + len(pos_bytes) + 3) & ~3
    idx_offset = (col_offset + len(col_bytes) + 3) & ~3
    total_len = idx_offset + len(idx_bytes)

    bin_blob = bytearray(total_len)
    bin_blob[pos_offset : pos_offset + len(pos_bytes)] = pos_bytes
    bin_blob[col_offset : col_offset + len(col_bytes)] = col_bytes
    bin_blob[idx_offset : idx_offset + len(idx_bytes)] = idx_bytes

    min_bound = pos.min(axis=0).tolist()
    max_bound = pos.max(axis=0).tolist()

    gltf_json = {
        "asset": {"version": "2.0", "generator": "build_hunyuan_scene_001_modules.py"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": "hunyuan_scene_001_module"}],
        "buffers": [{"byteLength": total_len}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": pos_offset, "byteLength": len(pos_bytes), "target": 34962},
            {"buffer": 0, "byteOffset": col_offset, "byteLength": len(col_bytes), "target": 34962},
            {"buffer": 0, "byteOffset": idx_offset, "byteLength": len(idx_bytes), "target": 34963},
        ],
        "accessors": [
            {
                "bufferView": 0,
                "componentType": 5126,
                "count": int(pos.shape[0]),
                "type": "VEC3",
                "min": min_bound,
                "max": max_bound,
            },
            {
                "bufferView": 1,
                "componentType": 5121,
                "count": int(col.shape[0]),
                "type": "VEC3",
                "normalized": True,
            },
            {
                "bufferView": 2,
                "componentType": 5125,
                "count": int(idx.shape[0]),
                "type": "SCALAR",
            },
        ],
        "materials": [
            {
                "name": "HunyuanScene001_ModuleMaterial",
                "pbrMetallicRoughness": {
                    "baseColorFactor": [0.84, 0.78, 0.71, 1.0],
                    "metallicFactor": 0.0,
                    "roughnessFactor": 0.94,
                },
            }
        ],
        "meshes": [
            {
                "name": "hunyuan_scene_001_module_mesh",
                "primitives": [
                    {"attributes": {"POSITION": 0, "COLOR_0": 1}, "indices": 2, "mode": 4, "material": 0}
                ],
            }
        ],
    }
    return gltf_json, bytes(bin_blob)


def split_to_modules(positions: np.ndarray, colors: np.ndarray, faces: np.ndarray) -> tuple[list[ModuleBuild], dict]:
    MODULE_DIR.mkdir(parents=True, exist_ok=True)

    centroids = positions[faces].mean(axis=1)
    min_bound = positions.min(axis=0)
    max_bound = positions.max(axis=0)
    extent = np.maximum(max_bound - min_bound, np.array([1e-4, 1e-4, 1e-4], dtype=np.float32))

    u = (centroids[:, 0] - min_bound[0]) / extent[0]
    v = (centroids[:, 2] - min_bound[2]) / extent[2]
    cols = np.minimum(GRID_COLS - 1, (u * GRID_COLS).astype(np.int32))
    rows = np.minimum(GRID_ROWS - 1, (v * GRID_ROWS).astype(np.int32))
    module_ids = rows * GRID_COLS + cols

    builds: list[ModuleBuild] = []
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            mod_id = row * GRID_COLS + col
            face_mask = module_ids == mod_id
            mod_faces = faces[face_mask]
            source_tri_count = int(mod_faces.shape[0])
            if source_tri_count == 0:
                continue

            stride = max(1, int(math.ceil(source_tri_count / MAX_TRIANGLES_PER_MODULE)))
            mod_faces = mod_faces[::stride]
            if mod_faces.size == 0:
                continue

            unique_vertices, inverse = np.unique(mod_faces.reshape(-1), return_inverse=True)
            remapped_faces = inverse.reshape(-1, 3).astype(np.uint32, copy=False)
            mod_positions = positions[unique_vertices]
            mod_colors = colors[unique_vertices]

            mod_name = f"hunyuan_scene_001_module_r{row}_c{col}"
            out_file = MODULE_DIR / f"{mod_name}.glb"
            gltf_json, bin_blob = build_glb_arrays(mod_positions, mod_colors, remapped_faces)
            write_glb(out_file, gltf_json, bin_blob)

            mod_min = mod_positions.min(axis=0).astype(float).tolist()
            mod_max = mod_positions.max(axis=0).astype(float).tolist()
            builds.append(
                ModuleBuild(
                    name=mod_name,
                    rel_path=f"res://assets/3d/modules/hunyuan_scene_001/{mod_name}.glb",
                    vertex_count=int(mod_positions.shape[0]),
                    triangle_count=int(remapped_faces.shape[0]),
                    source_triangle_count=source_tri_count,
                    decimate_stride=stride,
                    min_bound=mod_min,
                    max_bound=mod_max,
                )
            )

    overall = {
        "min_bound": min_bound.astype(float).tolist(),
        "max_bound": max_bound.astype(float).tolist(),
        "ground_y": float(np.percentile(positions[:, 1], 50.0)),
        "source_vertices": int(positions.shape[0]),
        "source_triangles": int(faces.shape[0]),
        "grid_rows": GRID_ROWS,
        "grid_cols": GRID_COLS,
        "max_triangles_per_module": MAX_TRIANGLES_PER_MODULE,
    }
    return builds, overall


def write_manifest(modules: list[ModuleBuild], overall: dict) -> None:
    data = {
        "scene_id": "hunyuan_scene_001",
        "overall": overall,
        "modules": [
            {
                "name": m.name,
                "path": m.rel_path,
                "vertex_count": m.vertex_count,
                "triangle_count": m.triangle_count,
                "source_triangle_count": m.source_triangle_count,
                "decimate_stride": m.decimate_stride,
                "min_bound": m.min_bound,
                "max_bound": m.max_bound,
            }
            for m in modules
        ],
    }
    MANIFEST_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def format_f(value: float) -> str:
    return f"{value:.4f}"


def build_preview_scene(modules: list[ModuleBuild], overall: dict) -> str:
    ext_lines = []
    box_subres = []
    box_id_by_module = []
    load_steps = 5 + len(modules) + len(modules)

    for i, mod in enumerate(modules, start=1):
        ext_lines.append(
            f'[ext_resource type="PackedScene" path="{mod.rel_path}" id="{i}_module"]'
        )

    for i, mod in enumerate(modules, start=1):
        min_b = np.array(mod.min_bound, dtype=np.float32)
        max_b = np.array(mod.max_bound, dtype=np.float32)
        footprint = np.maximum(max_b - min_b, np.array([0.2, 0.2, 0.2], dtype=np.float32))
        size = np.array([float(footprint[0]), 0.5, float(footprint[2])], dtype=np.float32)
        box_id = f"BoxShape3D_{i}"
        box_id_by_module.append(box_id)
        box_subres.append(
            "\n".join(
                [
                    f'[sub_resource type="BoxShape3D" id="{box_id}"]',
                    f"size = Vector3({format_f(float(size[0]))}, {format_f(float(size[1]))}, {format_f(float(size[2]))})",
                ]
            )
        )

    min_b = np.array(overall["min_bound"], dtype=np.float32)
    max_b = np.array(overall["max_bound"], dtype=np.float32)
    nav_y = float(overall.get("ground_y", (min_b[1] + max_b[1]) * 0.5))
    nav_min_x = float(min_b[0])
    nav_max_x = float(max_b[0])
    nav_min_z = float(min_b[2])
    nav_max_z = float(max_b[2])

    lines = [
        f"[gd_scene load_steps={load_steps} format=3]",
        "",
        *ext_lines,
        "",
        '[sub_resource type="ProceduralSkyMaterial" id="ProceduralSkyMaterial_1"]',
        "sky_top_color = Color(0.8, 0.88, 0.95, 1)",
        "sky_horizon_color = Color(0.96, 0.91, 0.82, 1)",
        "ground_horizon_color = Color(0.62, 0.66, 0.58, 1)",
        "ground_bottom_color = Color(0.48, 0.5, 0.43, 1)",
        "",
        '[sub_resource type="Sky" id="Sky_1"]',
        'sky_material = SubResource("ProceduralSkyMaterial_1")',
        "",
        '[sub_resource type="Environment" id="Environment_1"]',
        "background_mode = 2",
        'sky = SubResource("Sky_1")',
        "ambient_light_source = 3",
        "ambient_light_color = Color(1, 0.97, 0.91, 1)",
        "ambient_light_energy = 0.72",
        "",
    ]

    for block in box_subres:
        lines.extend([block, ""])

    lines.extend(
        [
            '[sub_resource type="NavigationMesh" id="NavigationMesh_1"]',
            "vertices = PackedVector3Array("
            f"{format_f(nav_min_x)}, {format_f(nav_y)}, {format_f(nav_min_z)}, "
            f"{format_f(nav_max_x)}, {format_f(nav_y)}, {format_f(nav_min_z)}, "
            f"{format_f(nav_max_x)}, {format_f(nav_y)}, {format_f(nav_max_z)}, "
            f"{format_f(nav_min_x)}, {format_f(nav_y)}, {format_f(nav_max_z)})",
            "polygons = [PackedInt32Array(0, 1, 2, 3)]",
            "",
            '[node name="HunyuanScene001Preview" type="Node3D"]',
            "",
            '[node name="ImportedVisualRoot" type="Node3D" parent="."]',
            "",
        ]
    )

    for i, mod in enumerate(modules, start=1):
        lines.append(
            f'[node name="{mod.name}" parent="ImportedVisualRoot" instance=ExtResource("{i}_module")]'
        )
        lines.append("")

    lines.extend(
        [
            '[node name="CollisionProxy" type="Node3D" parent="."]',
            "",
        ]
    )

    for i, mod in enumerate(modules, start=1):
        min_m = np.array(mod.min_bound, dtype=np.float32)
        max_m = np.array(mod.max_bound, dtype=np.float32)
        center = (min_m + max_m) * 0.5
        center[1] = nav_y - 0.25
        lines.extend(
            [
                f'[node name="CollisionBody_{i}" type="StaticBody3D" parent="CollisionProxy"]',
                "",
                f'[node name="CollisionShape3D" type="CollisionShape3D" parent="CollisionProxy/CollisionBody_{i}"]',
                f'shape = SubResource("{box_id_by_module[i - 1]}")',
                "position = Vector3("
                f"{format_f(float(center[0]))}, {format_f(float(center[1]))}, {format_f(float(center[2]))})",
                "",
            ]
        )

    spawn_x = float((nav_min_x + nav_max_x) * 0.5)
    spawn_z = float(nav_min_z + (nav_max_z - nav_min_z) * 0.65)
    cam_x = float(nav_max_x)
    cam_y = float(nav_y + 7.0)
    cam_z = float(nav_max_z + 10.0)

    lines.extend(
        [
            '[node name="NavigationRegion3D" type="NavigationRegion3D" parent="."]',
            'navigation_mesh = SubResource("NavigationMesh_1")',
            "",
            '[node name="PlayerSpawn" type="Marker3D" parent="."]',
            f"position = Vector3({format_f(spawn_x)}, {format_f(nav_y + 0.05)}, {format_f(spawn_z)})",
            "",
            '[node name="PreviewCamera" type="Camera3D" parent="."]',
            f"position = Vector3({format_f(cam_x)}, {format_f(cam_y)}, {format_f(cam_z)})",
            "rotation_degrees = Vector3(-20, 28, 0)",
            "current = true",
            "",
            '[node name="SunLight" type="DirectionalLight3D" parent="."]',
            "rotation_degrees = Vector3(-48, 34, 0)",
            "light_color = Color(1, 0.95, 0.87, 1)",
            "light_energy = 1.25",
            "shadow_enabled = true",
            "",
            '[node name="WorldEnvironment" type="WorldEnvironment" parent="."]',
            'environment = SubResource("Environment_1")',
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> None:
    positions, colors, faces = load_ply(RAW_PLY)
    modules, overall = split_to_modules(positions, colors, faces)
    if not modules:
        fail("module split produced zero modules")

    write_manifest(modules, overall)
    preview_text = build_preview_scene(modules, overall)
    PREVIEW_SCENE.write_text(preview_text, encoding="utf-8")

    total_mod_tri = sum(m.triangle_count for m in modules)
    print(f"OK: built {len(modules)} modules")
    print(f"OK: source triangles={overall['source_triangles']}, module triangles={total_mod_tri}")
    print(f"OK: manifest -> {MANIFEST_PATH}")
    print(f"OK: preview scene -> {PREVIEW_SCENE}")


if __name__ == "__main__":
    main()
