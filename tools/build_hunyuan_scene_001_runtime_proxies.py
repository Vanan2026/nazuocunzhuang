from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "assets" / "3d" / "modules" / "hunyuan_scene_001" / "manifest.json"
PREVIEW_SCENE = ROOT / "scenes" / "dev" / "hunyuan_scene_001_preview.tscn"
RUNTIME_PROXY_JSON = ROOT / "assets" / "3d" / "modules" / "hunyuan_scene_001" / "runtime_proxies.json"
AUTHORED_RUNTIME_JSON = ROOT / "assets" / "3d" / "modules" / "hunyuan_scene_001" / "official" / "hunyuan_scene_001_authored_runtime.json"

FLOOR_COLLISION_LAYER = 2
BLOCKER_COLLISION_LAYER = 4


@dataclass
class BoxProxy:
    center: tuple[float, float, float]
    size: tuple[float, float, float]


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def require(cond: bool, message: str) -> None:
    if not cond:
        fail(message)


def parse_manifest() -> tuple[list[dict], float]:
    require(MANIFEST_PATH.exists(), f"manifest not found: {MANIFEST_PATH}")
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    modules = data.get("modules", [])
    require(bool(modules), "manifest has no modules")
    overall = data.get("overall", {})
    ground_y = float(overall.get("ground_y", 0.0))
    return modules, ground_y


def parse_box_list(items: list[dict], field_name: str) -> list[BoxProxy]:
    boxes: list[BoxProxy] = []
    for idx, item in enumerate(items, start=1):
        center = item.get("center")
        size = item.get("size")
        require(isinstance(center, list) and len(center) == 3, f"{field_name}[{idx}] center is invalid")
        require(isinstance(size, list) and len(size) == 3, f"{field_name}[{idx}] size is invalid")
        boxes.append(
            BoxProxy(
                center=(float(center[0]), float(center[1]), float(center[2])),
                size=(max(0.1, float(size[0])), max(0.1, float(size[1])), max(0.1, float(size[2]))),
            )
        )
    return boxes


def median(values: list[float]) -> float:
    require(bool(values), "median requires non-empty list")
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return float(ordered[mid])
    return float((ordered[mid - 1] + ordered[mid]) * 0.5)


def align_runtime_vertical_space(
    nav_vertices: list[float],
    floor_boxes: list[BoxProxy],
    blocker_boxes: list[BoxProxy],
    spawn: tuple[float, float, float],
    ground_y: float,
) -> tuple[list[BoxProxy], list[BoxProxy], tuple[float, float, float], float, float]:
    nav_ys = [float(v) for v in nav_vertices[1::3]]
    floor_ys = [box.center[1] for box in floor_boxes]
    require(bool(nav_ys), "nav y-values missing")
    require(bool(floor_ys), "floor box y-values missing")

    nav_y_median = median(nav_ys)
    floor_y_median = median(floor_ys)
    y_shift = nav_y_median - floor_y_median

    if abs(y_shift) < 0.01:
        return floor_boxes, blocker_boxes, spawn, ground_y, 0.0

    shifted_floor: list[BoxProxy] = []
    for box in floor_boxes:
        cx, cy, cz = box.center
        shifted_floor.append(BoxProxy(center=(cx, cy + y_shift, cz), size=box.size))

    shifted_blockers: list[BoxProxy] = []
    for box in blocker_boxes:
        cx, cy, cz = box.center
        shifted_blockers.append(BoxProxy(center=(cx, cy + y_shift, cz), size=box.size))

    spawn_x, spawn_y, spawn_z = spawn
    shifted_spawn = (spawn_x, spawn_y + y_shift, spawn_z)
    shifted_ground_y = ground_y + y_shift
    return shifted_floor, shifted_blockers, shifted_spawn, shifted_ground_y, y_shift


def load_authored_runtime() -> tuple[list[float], list[list[int]], list[BoxProxy], list[BoxProxy], tuple[float, float, float], float]:
    require(AUTHORED_RUNTIME_JSON.exists(), f"missing authored runtime json: {AUTHORED_RUNTIME_JSON}")
    data = json.loads(AUTHORED_RUNTIME_JSON.read_text(encoding="utf-8"))
    nav_vertices = data.get("nav_vertices", [])
    nav_polygons = data.get("nav_polygons", [])
    floor_boxes_raw = data.get("floor_boxes", [])
    blocker_boxes_raw = data.get("blocker_boxes", [])
    spawn = data.get("spawn", [0.0, 0.1, 0.0])
    ground_y = float(data.get("ground_y", 0.0))

    require(isinstance(nav_vertices, list) and len(nav_vertices) >= 12 and len(nav_vertices) % 3 == 0, "authored nav_vertices invalid")
    require(isinstance(nav_polygons, list) and len(nav_polygons) > 0, "authored nav_polygons invalid")
    for i, poly in enumerate(nav_polygons, start=1):
        require(isinstance(poly, list) and len(poly) >= 3, f"nav_polygons[{i}] invalid")
    require(isinstance(spawn, list) and len(spawn) == 3, "authored spawn invalid")

    floor_boxes = parse_box_list(floor_boxes_raw, "floor_boxes")
    blocker_boxes = parse_box_list(blocker_boxes_raw, "blocker_boxes")
    require(bool(floor_boxes), "authored floor_boxes is empty")

    return (
        [float(v) for v in nav_vertices],
        [[int(x) for x in poly] for poly in nav_polygons],
        floor_boxes,
        blocker_boxes,
        (float(spawn[0]), float(spawn[1]), float(spawn[2])),
        ground_y,
    )


def fmt(value: float) -> str:
    s = f"{value:.6f}"
    return s.rstrip("0").rstrip(".") if "." in s else s


def write_preview_scene(
    modules: list[dict],
    nav_vertices: list[float],
    nav_polygons: list[list[int]],
    floor_boxes: list[BoxProxy],
    blocker_boxes: list[BoxProxy],
    ground_y: float,
    spawn: tuple[float, float, float],
) -> None:
    ext_lines = []
    for idx, module in enumerate(modules, start=1):
        path = module.get("path")
        require(isinstance(path, str) and path.startswith("res://"), f"invalid module path at {idx}")
        ext_lines.append(f'[ext_resource type="PackedScene" path="{path}" id="{idx}_module"]')

    nav_vertices_text = ", ".join(fmt(v) for v in nav_vertices)
    nav_poly_text = ", ".join("PackedInt32Array(" + ", ".join(str(i) for i in poly) + ")" for poly in nav_polygons)

    lines: list[str] = []
    lines.append("[gd_scene load_steps=128 format=3]")
    lines.append("")
    lines.extend(ext_lines)
    lines.append("")
    lines.append("[sub_resource type=\"NavigationMesh\" id=\"NavigationMesh_1\"]")
    lines.append(f"vertices = PackedVector3Array({nav_vertices_text})")
    lines.append(f"polygons = [{nav_poly_text}]")
    lines.append("")
    lines.append("[sub_resource type=\"Environment\" id=\"Environment_1\"]")
    lines.append("background_mode = 1")
    lines.append("background_color = Color(0.58, 0.68, 0.78, 1)")
    lines.append("ambient_light_source = 1")
    lines.append("ambient_light_color = Color(0.86, 0.9, 0.95, 1)")
    lines.append("ambient_light_energy = 1.35")
    lines.append("tonemap_mode = 2")
    lines.append("ssao_enabled = false")
    lines.append("ssil_enabled = false")
    lines.append("")

    for idx, box in enumerate(floor_boxes, start=1):
        sx, sy, sz = box.size
        lines.append(f'[sub_resource type="BoxShape3D" id="FloorBox_{idx}"]')
        lines.append(f"size = Vector3({fmt(sx)}, {fmt(sy)}, {fmt(sz)})")
        lines.append("")
    for idx, box in enumerate(blocker_boxes, start=1):
        sx, sy, sz = box.size
        lines.append(f'[sub_resource type="BoxShape3D" id="BlockerBox_{idx}"]')
        lines.append(f"size = Vector3({fmt(sx)}, {fmt(sy)}, {fmt(sz)})")
        lines.append("")

    lines.append('[node name="HunyuanScene001Preview" type="Node3D"]')
    lines.append("")
    lines.append('[node name="ImportedVisualRoot" type="Node3D" parent="."]')
    lines.append("")
    for idx, module in enumerate(modules, start=1):
        module_name = module.get("name", f"Module_{idx}")
        lines.append(f'[node name="{module_name}" parent="ImportedVisualRoot" instance=ExtResource("{idx}_module")]')
        lines.append("")

    lines.append('[node name="CollisionProxy" type="Node3D" parent="."]')
    lines.append("")
    for idx, box in enumerate(floor_boxes, start=1):
        cx, cy, cz = box.center
        lines.append(f'[node name="FloorBody_{idx}" type="StaticBody3D" parent="CollisionProxy"]')
        lines.append(f"collision_layer = {FLOOR_COLLISION_LAYER}")
        lines.append("collision_mask = 1")
        lines.append("")
        lines.append(f'[node name="CollisionShape3D" type="CollisionShape3D" parent="CollisionProxy/FloorBody_{idx}"]')
        lines.append(f'shape = SubResource("FloorBox_{idx}")')
        lines.append(f"position = Vector3({fmt(cx)}, {fmt(cy)}, {fmt(cz)})")
        lines.append("")

    lines.append('[node name="BlockerLayer" type="Node3D" parent="."]')
    lines.append("")
    for idx, box in enumerate(blocker_boxes, start=1):
        cx, cy, cz = box.center
        lines.append(f'[node name="BlockerBody_{idx}" type="StaticBody3D" parent="BlockerLayer"]')
        lines.append(f"collision_layer = {BLOCKER_COLLISION_LAYER}")
        lines.append("collision_mask = 1")
        lines.append("")
        lines.append(f'[node name="CollisionShape3D" type="CollisionShape3D" parent="BlockerLayer/BlockerBody_{idx}"]')
        lines.append(f'shape = SubResource("BlockerBox_{idx}")')
        lines.append(f"position = Vector3({fmt(cx)}, {fmt(cy)}, {fmt(cz)})")
        lines.append("")

    spawn_x, spawn_y, spawn_z = spawn
    lines.append('[node name="NavigationRegion3D" type="NavigationRegion3D" parent="."]')
    lines.append('navigation_mesh = SubResource("NavigationMesh_1")')
    lines.append("")
    lines.append('[node name="PlayerSpawn" type="Marker3D" parent="."]')
    lines.append(f"position = Vector3({fmt(spawn_x)}, {fmt(spawn_y)}, {fmt(spawn_z)})")
    lines.append("")
    lines.append('[node name="PreviewCamera" type="Camera3D" parent="."]')
    lines.append(f"position = Vector3({fmt(spawn_x + 6.0)}, {fmt(ground_y + 6.8)}, {fmt(spawn_z + 12.0)})")
    lines.append("rotation_degrees = Vector3(-20, 28, 0)")
    lines.append("current = true")
    lines.append("")
    lines.append('[node name="SunLight" type="DirectionalLight3D" parent="."]')
    lines.append("rotation_degrees = Vector3(-48, 34, 0)")
    lines.append("light_color = Color(1, 0.95, 0.87, 1)")
    lines.append("light_energy = 1.25")
    lines.append("shadow_enabled = true")
    lines.append("")
    lines.append('[node name="WorldEnvironment" type="WorldEnvironment" parent="."]')
    lines.append('environment = SubResource("Environment_1")')
    lines.append("")

    PREVIEW_SCENE.write_text("\n".join(lines), encoding="utf-8")


def write_runtime_proxy_json(
    nav_vertices: list[float],
    nav_polygons: list[list[int]],
    floor_boxes: list[BoxProxy],
    blocker_boxes: list[BoxProxy],
    ground_y: float,
) -> None:
    data = {
        "mode": "authored_round2",
        "ground_y": ground_y,
        "nav_vertex_count": len(nav_vertices) // 3,
        "nav_polygon_count": len(nav_polygons),
        "floor_box_count": len(floor_boxes),
        "blocker_count": len(blocker_boxes),
        "collision_layers": {
            "floor": FLOOR_COLLISION_LAYER,
            "blocker": BLOCKER_COLLISION_LAYER,
        },
        "source": f"res://{AUTHORED_RUNTIME_JSON.relative_to(ROOT).as_posix()}",
    }
    RUNTIME_PROXY_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    modules, fallback_ground_y = parse_manifest()
    nav_vertices, nav_polygons, floor_boxes, blocker_boxes, spawn, authored_ground_y = load_authored_runtime()
    ground_y = authored_ground_y if authored_ground_y != 0.0 else fallback_ground_y
    floor_boxes, blocker_boxes, spawn, ground_y, y_shift = align_runtime_vertical_space(
        nav_vertices=nav_vertices,
        floor_boxes=floor_boxes,
        blocker_boxes=blocker_boxes,
        spawn=spawn,
        ground_y=ground_y,
    )

    write_preview_scene(
        modules=modules,
        nav_vertices=nav_vertices,
        nav_polygons=nav_polygons,
        floor_boxes=floor_boxes,
        blocker_boxes=blocker_boxes,
        ground_y=ground_y,
        spawn=spawn,
    )
    write_runtime_proxy_json(
        nav_vertices=nav_vertices,
        nav_polygons=nav_polygons,
        floor_boxes=floor_boxes,
        blocker_boxes=blocker_boxes,
        ground_y=ground_y,
    )
    print(f"OK: authored runtime preview built -> {PREVIEW_SCENE}")
    print(
        "OK: nav vertices=%d, polygons=%d, floor_boxes=%d, blockers=%d"
        % (len(nav_vertices) // 3, len(nav_polygons), len(floor_boxes), len(blocker_boxes))
    )
    if abs(y_shift) >= 0.01:
        print(f"OK: applied runtime vertical alignment shift y={y_shift:.4f}")
    print(f"OK: runtime proxy summary -> {RUNTIME_PROXY_JSON}")


if __name__ == "__main__":
    main()
