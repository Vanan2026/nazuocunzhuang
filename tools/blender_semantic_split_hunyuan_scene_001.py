"""
Round-2 Blender semantic split for hunyuan_scene_001.

Goals:
- face-level non-overlap split for semantic modules
- stronger decimation pass
- authored walk/nav data + blocker collider data output

Usage:
  blender --background --python tools/blender_semantic_split_hunyuan_scene_001.py -- \
    --input "D:/那个村庄/assets/3d/raw/hunyuan_scene_001/hunyuan_scene_001_raw.ply" \
    --output-dir "D:/那个村庄/assets/3d/modules/hunyuan_scene_001/official"
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import deque
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector


MODULE_SPECS = (
    ("ground", 0.22),
    ("architecture", 0.20),
    ("vegetation", 0.18),
    ("props", 0.16),
)

NAV_CELL_SIZE = 0.6
BLOCKER_CELL_SIZE = 0.8
BLOCKER_HEIGHT = 2.4
BLOCKER_Y_OFFSET = 1.2
BLOCKER_MAX_COUNT = 16
BLOCKER_MIN_COMPONENT_CELLS = 2
BLOCKER_MAX_SPAN_CELLS = 3
BLOCKER_MAX_CELLS_PER_BOX = 8


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args(argv)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for coll in list(bpy.data.collections):
        if coll.users == 0:
            bpy.data.collections.remove(coll)


def import_source(path: Path) -> None:
    ext = path.suffix.lower()
    if ext == ".ply":
        bpy.ops.wm.ply_import(filepath=str(path))
    elif ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=str(path))
    else:
        raise ValueError(f"unsupported input extension: {ext}")


def collect_mesh_objects() -> list[bpy.types.Object]:
    return [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]


def merge_meshes(objects: list[bpy.types.Object]) -> bpy.types.Object:
    if not objects:
        raise ValueError("no mesh objects to merge")
    if len(objects) == 1:
        merged = objects[0]
        merged.name = "hunyuan_scene_001_merged"
        return merged
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    merged = bpy.context.view_layer.objects.active
    if merged is None:
        raise RuntimeError("failed to join source meshes")
    merged.name = "hunyuan_scene_001_merged"
    return merged


def apply_object_transform(obj: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    obj.select_set(False)


def triangulate_object(obj: bpy.types.Object) -> None:
    mod = obj.modifiers.new(name="Triangulate", type="TRIANGULATE")
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)


def build_face_tables(mesh: bpy.types.Mesh) -> tuple[list[dict], float, float, Vector, Vector]:
    mesh.update()
    polys = mesh.polygons
    if not polys:
        raise RuntimeError("mesh has zero polygons")

    mins = [Vector((1e9, 1e9, 1e9))]
    maxs = [Vector((-1e9, -1e9, -1e9))]
    areas: list[float] = []
    rows: list[dict] = []

    for poly in polys:
        c = poly.center
        n = poly.normal
        a = float(poly.area)
        rows.append(
            {
                "idx": int(poly.index),
                "center": Vector((c.x, c.y, c.z)),
                "normal_y": abs(float(n.y)),
                "area": a,
            }
        )
        areas.append(a)
        mins.append(c)
        maxs.append(c)

    min_bound = Vector((min(v.x for v in mins), min(v.y for v in mins), min(v.z for v in mins)))
    max_bound = Vector((max(v.x for v in maxs), max(v.y for v in maxs), max(v.z for v in maxs)))
    scene_height = max(0.001, max_bound.y - min_bound.y)
    area_sorted = sorted(areas)
    area_median = area_sorted[len(area_sorted) // 2]
    return rows, scene_height, area_median, min_bound, max_bound


def classify_faces(
    face_rows: list[dict],
    scene_height: float,
    area_median: float,
    min_bound: Vector,
) -> dict[str, list[int]]:
    groups: dict[str, list[int]] = {name: [] for name, _ratio in MODULE_SPECS}
    ground_y = min_bound.y

    for row in face_rows:
        cy = row["center"].y
        ny = row["normal_y"]
        area = row["area"]
        idx = row["idx"]
        rel_h = (cy - ground_y) / scene_height

        if ny >= 0.92 and rel_h <= 0.34:
            groups["ground"].append(idx)
        elif ny <= 0.35 and rel_h <= 0.88:
            groups["architecture"].append(idx)
        elif rel_h >= 0.40 and area <= area_median * 1.75:
            groups["vegetation"].append(idx)
        else:
            groups["props"].append(idx)

    fallback_pool = groups["props"][:]
    for name, _ratio in MODULE_SPECS:
        if groups[name]:
            continue
        take = max(128, len(fallback_pool) // 20)
        groups[name] = fallback_pool[:take]
        fallback_pool = fallback_pool[take:]
    return groups


def clone_faces_as_object(base_obj: bpy.types.Object, keep_face_indices: list[int], out_name: str) -> bpy.types.Object:
    keep = set(keep_face_indices)
    if not keep:
        raise RuntimeError(f"{out_name}: empty face selection")

    dup = base_obj.copy()
    dup.data = base_obj.data.copy()
    dup.name = out_name
    bpy.context.collection.objects.link(dup)

    bm = bmesh.new()
    bm.from_mesh(dup.data)
    bm.faces.ensure_lookup_table()

    to_delete = [face for face in bm.faces if face.index not in keep]
    if to_delete:
        bmesh.ops.delete(bm, geom=to_delete, context="FACES")
    if not bm.faces:
        bm.free()
        raise RuntimeError(f"{out_name}: no faces remained after split")
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    bm.to_mesh(dup.data)
    bm.free()
    dup.data.update()
    return dup


def decimate_object(obj: bpy.types.Object, ratio: float) -> None:
    ratio = max(0.01, min(1.0, ratio))
    mod = obj.modifiers.new(name="Decimate", type="DECIMATE")
    mod.ratio = ratio
    mod.use_collapse_triangulate = True
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)


def set_unified_pivot(obj: bpy.types.Object, pivot_world: Vector) -> None:
    bpy.context.scene.cursor.location = pivot_world
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    obj.select_set(False)


def export_glb(obj: bpy.types.Object, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.gltf(
        filepath=str(out_path),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_texcoords=True,
        export_normals=True,
        export_materials="EXPORT",
    )
    obj.select_set(False)


def tri_count(obj: bpy.types.Object) -> int:
    return int(sum(max(1, len(poly.vertices) - 2) for poly in obj.data.polygons))


def connected_components(cells: set[tuple[int, int]]) -> list[set[tuple[int, int]]]:
    unseen = set(cells)
    comps: list[set[tuple[int, int]]] = []
    while unseen:
        seed = unseen.pop()
        comp = {seed}
        q: deque[tuple[int, int]] = deque([seed])
        while q:
            i, j = q.popleft()
            for nb in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                if nb in unseen:
                    unseen.remove(nb)
                    comp.add(nb)
                    q.append(nb)
        comps.append(comp)
    return comps


def select_walk_face_indices(face_rows: list[dict], ground_y: float) -> list[int]:
    primary = [
        r["idx"]
        for r in face_rows
        if r["normal_y"] >= 0.92 and (ground_y - 0.2) <= r["center"].y <= (ground_y + 1.4)
    ]
    if primary:
        return primary

    sorted_rows = sorted(face_rows, key=lambda r: r["center"].y)
    low_band = sorted_rows[: max(2000, len(sorted_rows) // 5)]
    relaxed = [r["idx"] for r in low_band if r["normal_y"] >= 0.55]
    if relaxed:
        return relaxed
    return [r["idx"] for r in sorted_rows[: max(2000, len(sorted_rows) // 8)]]


def build_walk_nav(face_rows: list[dict], ground_y: float) -> tuple[list[float], list[list[int]], list[dict], Vector]:
    walk_indices = set(select_walk_face_indices(face_rows, ground_y))
    walk_rows = [r for r in face_rows if r["idx"] in walk_indices]
    if not walk_rows:
        raise RuntimeError("walkable face extraction produced zero samples after fallback")

    min_x = min(r["center"].x for r in walk_rows)
    min_z = min(r["center"].z for r in walk_rows)

    counts: dict[tuple[int, int], int] = {}
    y_acc: dict[tuple[int, int], float] = {}
    for row in walk_rows:
        i = int(math.floor((row["center"].x - min_x) / NAV_CELL_SIZE))
        j = int(math.floor((row["center"].z - min_z) / NAV_CELL_SIZE))
        cell = (i, j)
        counts[cell] = counts.get(cell, 0) + 1
        y_acc[cell] = y_acc.get(cell, 0.0) + row["center"].y

    raw_cells = {cell for cell, count in counts.items() if count >= 2}
    if not raw_cells:
        raw_cells = set(counts.keys())
    if not raw_cells:
        raise RuntimeError("walkable cell extraction produced zero cells")
    comps = connected_components(raw_cells)
    walk_cells = max(comps, key=len)

    nav_vertices: list[float] = []
    nav_polygons: list[list[int]] = []
    floor_boxes: list[dict] = []
    cell_keys = sorted(walk_cells, key=lambda c: (c[0], c[1]))
    for cell in cell_keys:
        i, j = cell
        x0 = min_x + i * NAV_CELL_SIZE
        z0 = min_z + j * NAV_CELL_SIZE
        x1 = x0 + NAV_CELL_SIZE
        z1 = z0 + NAV_CELL_SIZE
        y = y_acc[cell] / max(1, counts[cell])

        base = len(nav_vertices) // 3
        nav_vertices.extend([x0, y, z0, x1, y, z0, x1, y, z1, x0, y, z1])
        nav_polygons.append([base, base + 1, base + 2, base + 3])
        floor_boxes.append(
            {
                "center": [0.5 * (x0 + x1), ground_y - 0.25, 0.5 * (z0 + z1)],
                "size": [NAV_CELL_SIZE, 0.5, NAV_CELL_SIZE],
            }
        )

    cx = sum(nav_vertices[0::3]) / max(1, len(nav_vertices) // 3)
    cz = sum(nav_vertices[2::3]) / max(1, len(nav_vertices) // 3)
    spawn = Vector((cx, ground_y + 0.1, cz))
    return nav_vertices, nav_polygons, floor_boxes, spawn


def build_blocker_boxes(face_rows: list[dict], ground_y: float) -> list[dict]:
    blocker_rows = [
        r
        for r in face_rows
        if r["normal_y"] <= 0.35 and (ground_y - 0.4) <= r["center"].y <= (ground_y + 3.2)
    ]
    if not blocker_rows:
        return []

    min_x = min(r["center"].x for r in blocker_rows)
    min_z = min(r["center"].z for r in blocker_rows)
    counts: dict[tuple[int, int], int] = {}
    for row in blocker_rows:
        i = int(math.floor((row["center"].x - min_x) / BLOCKER_CELL_SIZE))
        j = int(math.floor((row["center"].z - min_z) / BLOCKER_CELL_SIZE))
        cell = (i, j)
        counts[cell] = counts.get(cell, 0) + 1

    dense_cells = {cell for cell, count in counts.items() if count >= 10}
    if not dense_cells:
        return []

    boxes: list[dict] = []
    for comp in sorted(connected_components(dense_cells), key=len, reverse=True):
        if len(comp) < BLOCKER_MIN_COMPONENT_CELLS:
            continue

        remaining = set(comp)
        while remaining and len(boxes) < BLOCKER_MAX_COUNT:
            seed = min(remaining)
            chunk = {seed}
            remaining.remove(seed)
            q: deque[tuple[int, int]] = deque([seed])

            min_i = max_i = seed[0]
            min_j = max_j = seed[1]

            while q and len(chunk) < BLOCKER_MAX_CELLS_PER_BOX:
                i, j = q.popleft()
                for nb in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                    if nb not in remaining:
                        continue
                    cand_min_i = min(min_i, nb[0])
                    cand_max_i = max(max_i, nb[0])
                    cand_min_j = min(min_j, nb[1])
                    cand_max_j = max(max_j, nb[1])
                    if (cand_max_i - cand_min_i + 1) > BLOCKER_MAX_SPAN_CELLS:
                        continue
                    if (cand_max_j - cand_min_j + 1) > BLOCKER_MAX_SPAN_CELLS:
                        continue
                    remaining.remove(nb)
                    chunk.add(nb)
                    q.append(nb)
                    min_i, max_i = cand_min_i, cand_max_i
                    min_j, max_j = cand_min_j, cand_max_j
                    if len(chunk) >= BLOCKER_MAX_CELLS_PER_BOX:
                        break

            if len(chunk) < BLOCKER_MIN_COMPONENT_CELLS:
                continue

            i_values = [c[0] for c in chunk]
            j_values = [c[1] for c in chunk]
            i0, i1 = min(i_values), max(i_values)
            j0, j1 = min(j_values), max(j_values)
            x0 = min_x + i0 * BLOCKER_CELL_SIZE
            x1 = min_x + (i1 + 1) * BLOCKER_CELL_SIZE
            z0 = min_z + j0 * BLOCKER_CELL_SIZE
            z1 = min_z + (j1 + 1) * BLOCKER_CELL_SIZE
            boxes.append(
                {
                    "center": [0.5 * (x0 + x1), ground_y + BLOCKER_Y_OFFSET, 0.5 * (z0 + z1)],
                    "size": [max(0.5, x1 - x0), BLOCKER_HEIGHT, max(0.5, z1 - z0)],
                    "cells": len(chunk),
                }
            )
    return boxes


def build_blocker_mesh(boxes: list[dict], name: str) -> bpy.types.Object:
    if not boxes:
        raise RuntimeError("no blocker boxes to build")
    created: list[bpy.types.Object] = []
    for idx, box in enumerate(boxes, start=1):
        center = box["center"]
        size = box["size"]
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(center[0], center[1], center[2]))
        cube = bpy.context.active_object
        if cube is None:
            continue
        cube.name = f"{name}_cube_{idx}"
        cube.scale = Vector((size[0] * 0.5, size[1] * 0.5, size[2] * 0.5))
        created.append(cube)

    if not created:
        raise RuntimeError("blocker cube generation failed")
    bpy.ops.object.select_all(action="DESELECT")
    for obj in created:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = created[0]
    bpy.ops.object.join()
    joined = bpy.context.view_layer.objects.active
    if joined is None:
        raise RuntimeError("failed to join blocker cubes")
    joined.name = name
    apply_object_transform(joined)
    return joined


def main() -> None:
    args = parse_args()
    source = Path(args.input).resolve()
    out_dir = Path(args.output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        raise SystemExit(f"FAIL: input file not found: {source}")

    clear_scene()
    import_source(source)
    meshes = collect_mesh_objects()
    if not meshes:
        raise SystemExit("FAIL: no mesh objects after import")

    merged = merge_meshes(meshes)
    apply_object_transform(merged)
    triangulate_object(merged)

    rows, scene_height, area_median, min_bound, max_bound = build_face_tables(merged.data)
    groups = classify_faces(rows, scene_height, area_median, min_bound)
    ground_y = min_bound.y
    pivot = Vector(((min_bound.x + max_bound.x) * 0.5, ground_y, (min_bound.z + max_bound.z) * 0.5))

    exports: list[dict] = []
    module_objects: dict[str, bpy.types.Object] = {}
    for name, ratio in MODULE_SPECS:
        keep_faces = groups[name]
        obj = clone_faces_as_object(merged, keep_faces, f"hunyuan_scene_001_module_{name}")
        decimate_object(obj, ratio)
        set_unified_pivot(obj, pivot)
        out_path = out_dir / f"hunyuan_scene_001_module_{name}.glb"
        export_glb(obj, out_path)
        module_objects[name] = obj
        exports.append(
            {
                "name": name,
                "path": str(out_path),
                "decimate_ratio": ratio,
                "triangles": tri_count(obj),
                "faces_selected": len(keep_faces),
            }
        )

    nav_vertices, nav_polygons, floor_boxes, spawn = build_walk_nav(rows, ground_y)
    blocker_boxes = build_blocker_boxes(rows, ground_y)

    walk_obj = clone_faces_as_object(merged, select_walk_face_indices(rows, ground_y), "hunyuan_scene_001_walkable_nav")
    decimate_object(walk_obj, 0.08)
    set_unified_pivot(walk_obj, pivot)
    walk_path = out_dir / "hunyuan_scene_001_walkable_nav.glb"
    export_glb(walk_obj, walk_path)

    blocker_mesh_path = None
    blocker_triangles = 0
    if blocker_boxes:
        blocker_obj = build_blocker_mesh(blocker_boxes, "hunyuan_scene_001_blockers")
        set_unified_pivot(blocker_obj, pivot)
        blocker_mesh_path = out_dir / "hunyuan_scene_001_blockers.glb"
        export_glb(blocker_obj, blocker_mesh_path)
        blocker_triangles = tri_count(blocker_obj)

    runtime_data = {
        "scene_id": "hunyuan_scene_001",
        "mode": "authored_round2",
        "ground_y": ground_y,
        "pivot_world": [pivot.x, pivot.y, pivot.z],
        "nav_cell_size": NAV_CELL_SIZE,
        "nav_vertices": nav_vertices,
        "nav_polygons": nav_polygons,
        "floor_boxes": floor_boxes,
        "blocker_boxes": blocker_boxes,
        "spawn": [spawn.x, spawn.y, spawn.z],
    }
    runtime_path = out_dir / "hunyuan_scene_001_authored_runtime.json"
    runtime_path.write_text(json.dumps(runtime_data, ensure_ascii=False, indent=2), encoding="utf-8")

    report = {
        "source": str(source),
        "output_dir": str(out_dir),
        "pivot_world": [pivot.x, pivot.y, pivot.z],
        "scene_bounds": {"min": [min_bound.x, min_bound.y, min_bound.z], "max": [max_bound.x, max_bound.y, max_bound.z]},
        "exports": exports,
        "walkable_nav_glb": {"path": str(walk_path), "triangles": tri_count(walk_obj)},
        "blocker_mesh_glb": {"path": str(blocker_mesh_path) if blocker_mesh_path else None, "triangles": blocker_triangles},
        "authored_runtime_json": str(runtime_path),
        "authored_runtime_stats": {
            "nav_vertices": len(nav_vertices) // 3,
            "nav_polygons": len(nav_polygons),
            "floor_boxes": len(floor_boxes),
            "blocker_boxes": len(blocker_boxes),
        },
    }
    (out_dir / "semantic_export_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: semantic round-2 export completed -> {out_dir}")
    print(f"OK: modules={len(exports)}, nav_polygons={len(nav_polygons)}, blocker_boxes={len(blocker_boxes)}")


if __name__ == "__main__":
    main()
