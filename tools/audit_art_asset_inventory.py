from __future__ import annotations

import json
import re
import struct
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "production/assets/art_asset_inventory_2026-05-20.json"
PROJECT_MANIFEST = ROOT / "production/assets/project_art_production_manifest_2026-05-19.json"
SCAN_ROOTS = ["assets", "production/assets", "game/data", "scenes", "tools"]
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
TEXT_EXTENSIONS = {".tscn", ".gd", ".json", ".tres", ".md", ".py", ".cfg"}
IGNORED_SCAN_SUFFIXES = {".import"}
ACTIVE_SCENES = [
    "scenes/world/world.tscn",
    "scenes/regions/region_home_area.tscn",
    "scenes/regions/region_back_farm.tscn",
]
EXPECTED_P0_ITEM_ICON_CATEGORIES = ["seed", "material", "forage", "fish", "food", "key"]
P0_NPC_IDS = ["aoi", "gen", "mika", "hana"]
NPC_IDLE_DIRECTIONS = ["down", "up", "left", "right"]
NPC_WALK_DIRECTIONS = ["down", "up", "left", "right"]
NPC_PORTRAIT_EXPRESSIONS = ["neutral", "happy", "thinking"]
OBSOLETE_HOME_AREA_TOOL_PATHS = [
    "tools/build_region_home_area_launch_art_package.py",
    "tools/integrate_home_area_formal_v001_split_scene.py",
    "tools/prepare_home_area_formal_v001_source.py",
    "tools/run_home_area_v006_first_batch_pipeline.ps1",
    "tools/split_home_area_formal_v001_layers.py",
    "tools/split_home_area_launch_quality_v001_layers.py",
    "tools/test_region_home_area_launch_art_package.py",
    "tools/validate_home_area_launch_quality_v001_package.py",
    "tools/validate_home_area_launch_quality_v001_visual_sanity.py",
    "tools/validate_region_home_area_launch_art_package.py",
]
VERSION_DIR_PATTERN = re.compile(r"^v\d+$")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="ignore")


def png_dimensions(path: Path) -> dict[str, int] | None:
    try:
        with path.open("rb") as handle:
            header = handle.read(24)
        if header[:8] != b"\x89PNG\r\n\x1a\n":
            return None
        width, height = struct.unpack(">II", header[16:24])
        return {"width": int(width), "height": int(height)}
    except OSError:
        return None


def collect_files() -> list[Path]:
    files: list[Path] = []
    for root_name in SCAN_ROOTS:
        root = ROOT / root_name
        if root.exists():
            files.extend(path for path in root.rglob("*") if should_scan_file(path))
    return sorted(files, key=rel)


def should_scan_file(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.resolve() == OUTPUT.resolve():
        return False
    if path.suffix in IGNORED_SCAN_SUFFIXES:
        return False
    if path.suffix == ".translation" and path.is_relative_to(ROOT / "production"):
        return False
    return True


def classify_image(path: Path) -> str:
    parts = path.relative_to(ROOT).parts
    if len(parts) >= 3 and parts[0] == "assets" and parts[1] == "art":
        return f"runtime_art/{parts[2]}"
    if len(parts) >= 4 and parts[0] == "production" and parts[1] == "assets" and parts[2] == "regions":
        return f"production_region/{parts[3]}"
    if len(parts) >= 3 and parts[0] == "production" and parts[1] == "assets":
        return f"production_asset/{parts[2]}"
    return "other_art"


def extract_res_refs(files: list[Path]) -> dict[str, list[str]]:
    refs: dict[str, list[str]] = {}
    pattern = re.compile(r"res://[^\"'\]\)\s]+")
    for path in files:
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        text = read_text(path)
        matches = sorted(set(pattern.findall(text)))
        if matches:
            refs[rel(path)] = matches
    return refs


def existing_res_path(res_path: str) -> bool:
    if not res_path.startswith("res://"):
        return False
    return (ROOT / res_path.removeprefix("res://")).exists()


def classify_unresolved_ref(ref: str) -> str:
    if "{" in ref or "}" in ref or "[" in ref or "]" in ref or "%s" in ref or ref.endswith("\\"):
        return "template_or_regex_literal"
    if not Path(ref.removeprefix("res://")).suffix:
        return "template_or_regex_literal"
    if ref.startswith("res://assets/art/items/"):
        return "data_backlog_item_icon"
    if ref.startswith("res://assets/art/portraits/npc_") or ref.startswith("res://assets/art/characters/npc/npc_"):
        return "data_backlog_complete_npc_art"
    if ref.startswith("res://production/assets/regions/home_area_formal/"):
        return "rejected_home_area_formal_reference"
    if ref.startswith("res://production/assets/regions/home_area_launch"):
        return "rejected_home_area_launch_reference"
    if ref.startswith("res://game/scenes/world/"):
        return "planned_forward_scene_backlog"
    if ref.startswith("res://assets/3d/") or ref.startswith("res://.codex/"):
        return "non_current_pipeline_reference"
    return "missing_or_external_reference"


def group_unresolved_refs(unresolved_refs: list[str]) -> dict[str, Any]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for ref in unresolved_refs:
        grouped[classify_unresolved_ref(ref)].append(ref)
    return {
        category: {
            "count": len(refs),
            "refs": refs[:120],
        }
        for category, refs in sorted(grouped.items())
    }


def collect_complete_npc_art_backlog() -> dict[str, Any]:
    missing: list[dict[str, str]] = []
    required_assets: list[dict[str, str]] = []
    for npc_id in P0_NPC_IDS:
        for direction in NPC_IDLE_DIRECTIONS:
            asset = f"assets/art/characters/npc/npc_{npc_id}_idle_{direction}_128.png"
            required_assets.append({"npc_id": npc_id, "kind": "idle", "direction": direction, "asset": asset})
        for direction in NPC_WALK_DIRECTIONS:
            asset = f"assets/art/characters/npc/npc_{npc_id}_walk_{direction}_4x128.png"
            required_assets.append({"npc_id": npc_id, "kind": "walk", "direction": direction, "asset": asset})
        for expression in NPC_PORTRAIT_EXPRESSIONS:
            asset = f"assets/art/portraits/npc_{npc_id}_portrait_{expression}_512.png"
            required_assets.append({"npc_id": npc_id, "kind": "portrait", "expression": expression, "asset": asset})

    for record in required_assets:
        if not (ROOT / record["asset"]).exists():
            missing.append(record)

    by_npc: dict[str, int] = defaultdict(int)
    by_kind: dict[str, int] = defaultdict(int)
    for record in missing:
        by_npc[record["npc_id"]] += 1
        by_kind[record["kind"]] += 1

    return {
        "required_npc_ids": P0_NPC_IDS,
        "required_idle_directions": NPC_IDLE_DIRECTIONS,
        "required_walk_directions": NPC_WALK_DIRECTIONS,
        "required_portrait_expressions": NPC_PORTRAIT_EXPRESSIONS,
        "required_count": len(required_assets),
        "missing_count": len(missing),
        "missing_by_npc": dict(sorted(by_npc.items())),
        "missing_by_kind": dict(sorted(by_kind.items())),
        "missing": missing,
    }


def collect_data_backlogs() -> dict[str, Any]:
    items = read_json(ROOT / "game/data/items.json", [])
    item_missing: list[dict[str, Any]] = []
    category_counter: Counter[str] = Counter()
    if isinstance(items, list):
        for item in items:
            if not isinstance(item, dict):
                continue
            icon = str(item.get("icon", ""))
            category = str(item.get("category", "unknown"))
            if icon and not existing_res_path(icon):
                item_missing.append({
                    "item_id": item.get("item_id"),
                    "category": category,
                    "icon": icon,
                })
                category_counter[category] += 1

    crops = read_json(ROOT / "game/data/crops.json", [])
    crop_missing: list[dict[str, str]] = []
    if isinstance(crops, list):
        for crop in crops:
            if not isinstance(crop, dict):
                continue
            for sprite in crop.get("stage_sprites", []):
                sprite_path = str(sprite)
                if sprite_path and not existing_res_path(sprite_path):
                    crop_missing.append({"crop_id": str(crop.get("crop_id", "")), "sprite": sprite_path})

    return {
        "item_icons": {
            "missing_count": len(item_missing),
            "missing_by_category": dict(sorted(category_counter.items())),
            "expected_p0_categories": EXPECTED_P0_ITEM_ICON_CATEGORIES,
            "expected_p0_categories_still_missing": [cat for cat in EXPECTED_P0_ITEM_ICON_CATEGORIES if category_counter.get(cat, 0) > 0],
            "missing": item_missing,
        },
        "crop_stage_sprites": {
            "missing_count": len(crop_missing),
            "missing": crop_missing,
        },
        "npc_complete_runtime_art": collect_complete_npc_art_backlog(),
    }


def collect_production_packages() -> list[dict[str, Any]]:
    packages: list[dict[str, Any]] = []
    regions_root = ROOT / "production/assets/regions"
    if not regions_root.exists():
        return packages
    package_dirs = sorted(
        (path for path in regions_root.rglob("*") if path.is_dir() and VERSION_DIR_PATTERN.match(path.name)),
        key=rel,
    )
    for package_dir in package_dirs:
        files = [path for path in package_dir.rglob("*") if path.is_file()]
        if not files:
            continue
        manifests = sorted(path for path in files if "manifest" in path.name.lower() and path.suffix.lower() == ".json")
        images = [path for path in files if path.suffix.lower() in IMAGE_EXTENSIONS]
        packages.append({
            "dir": rel(package_dir),
            "file_count": len(files),
            "image_count": len(images),
            "manifest_count": len(manifests),
            "manifests": [rel(path) for path in manifests[:12]],
            "needs_manifest_review": len(manifests) == 0,
        })
    return packages


def collect_dirty_data(files: list[Path], refs_by_file: dict[str, list[str]]) -> dict[str, Any]:
    backup_scenes = sorted(rel(path) for path in ROOT.glob("scenes/regions/region_home_area.before_*.tscn"))
    project_manifest = read_json(PROJECT_MANIFEST, {})
    forbidden = []
    if isinstance(project_manifest, dict):
        rules = project_manifest.get("rules", {})
        if isinstance(rules, dict):
            forbidden = list(rules.get("forbidden_final_sources", []))
    existing_forbidden_dirs = []
    for token in forbidden:
        clean = str(token).rstrip("/")
        candidate = ROOT / clean
        if candidate.exists():
            existing_forbidden_dirs.append(clean)

    active_scene_forbidden_refs: list[dict[str, str]] = []
    for scene in ACTIVE_SCENES:
        scene_path = ROOT / scene
        if not scene_path.exists():
            continue
        text = read_text(scene_path)
        for token in forbidden:
            if token in text:
                active_scene_forbidden_refs.append({"scene": scene, "token": token})

    legacy_dirs = [path for path in [ROOT / "tools/legacy_homeyard"] if path.exists()]
    stale_home_area_tools = [path for path in OBSOLETE_HOME_AREA_TOOL_PATHS if (ROOT / path).exists()]

    return {
        "importable_backup_scenes": {
            "count": len(backup_scenes),
            "risk": "Godot can still import these scene backups and report duplicate UID or stale references.",
            "recommendation": "Hard cleanup target is zero importable HomeArea backup scenes; rely on git history for rollback.",
            "paths": backup_scenes,
        },
        "existing_forbidden_source_dirs": {
            "count": len(existing_forbidden_dirs),
            "paths": existing_forbidden_dirs,
        },
        "active_scene_forbidden_refs": {
            "count": len(active_scene_forbidden_refs),
            "refs": active_scene_forbidden_refs,
        },
        "legacy_tool_dirs": {
            "count": len(legacy_dirs),
            "paths": [rel(path) for path in legacy_dirs],
        },
        "stale_home_area_tool_candidates": {
            "count": len(stale_home_area_tools),
            "note": "Hard cleanup target is zero for the explicit obsolete HomeArea tool allowlist.",
            "paths": stale_home_area_tools,
        },
    }


def build_inventory() -> dict[str, Any]:
    files = collect_files()
    refs_by_file = extract_res_refs(files)
    all_refs = sorted(set(ref for refs in refs_by_file.values() for ref in refs))
    unresolved_refs = [ref for ref in all_refs if ref.startswith("res://") and not existing_res_path(ref)]

    image_files = [path for path in files if path.suffix.lower() in IMAGE_EXTENSIONS]
    group_counter: Counter[str] = Counter(classify_image(path) for path in image_files)
    runtime_images = [path for path in image_files if rel(path).startswith("assets/art/")]
    referenced_runtime = {ref.removeprefix("res://") for ref in all_refs if ref.startswith("res://assets/art/")}
    unreferenced_runtime = [rel(path) for path in runtime_images if rel(path) not in referenced_runtime]

    png_dimension_samples: dict[str, dict[str, int]] = {}
    for path in image_files:
        if path.suffix.lower() == ".png":
            dims = png_dimensions(path)
            if dims:
                png_dimension_samples[rel(path)] = dims

    production_packages = collect_production_packages()
    manifest_files = sorted(rel(path) for path in files if "manifest" in path.name.lower() and path.suffix.lower() == ".json")

    data_backlogs = collect_data_backlogs()
    dirty_data = collect_dirty_data(files, refs_by_file)
    npc_complete = data_backlogs["npc_complete_runtime_art"]

    prioritized_backlog = [
        {
            "priority": "P0",
            "id": "item_icon_backlog",
            "reason": "game/data/items.json still references icons that do not exist in assets/art/items.",
            "count": data_backlogs["item_icons"]["missing_count"],
            "next_step": "Create the missing 64px runtime icons through a batch icon package and rerun this audit.",
        },
        {
            "priority": "P0",
            "id": "p0_npc_complete_runtime_art",
            "reason": "P0 NPCs require complete runtime packages, not minimum idle/portrait placeholders.",
            "count": npc_complete["missing_count"],
            "next_step": "Produce all missing 4-direction idle sprites, 4-direction walk sheets, and neutral/happy/thinking portraits for Aoi, Gen, Mika, and Hana.",
        },
        {
            "priority": "P0",
            "id": "home_area_capture_review",
            "reason": "HomeArea world2d/v001 is integrated but still needs Godot capture and human review before polish or regeneration.",
            "count": 1,
            "next_step": "Run the HomeArea capture review from the actual world.tscn route.",
        },
        {
            "priority": "P1",
            "id": "hard_cleanup_obsolete_home_area_routes",
            "reason": "Obsolete importable backup scenes and old HomeArea route tools must stay absent after strong cleanup.",
            "count": dirty_data["importable_backup_scenes"]["count"] + dirty_data["legacy_tool_dirs"]["count"] + dirty_data["stale_home_area_tool_candidates"]["count"],
            "next_step": "Keep this count at 0; use git history for rollback instead of reintroducing importable backups.",
        },
        {
            "priority": "P1",
            "id": "production_package_manifest_review",
            "reason": "Versioned production package roots should have at least one manifest in their package tree.",
            "count": len([pkg for pkg in production_packages if pkg.get("needs_manifest_review")]),
            "next_step": "Add a manifest or explicitly remove the package root if this count becomes non-zero.",
        },
    ]

    return {
        "schema_version": 1,
        "generated_at": "2026-05-20",
        "generated_by": "tools/audit_art_asset_inventory.py",
        "project": "The Village",
        "scan_roots": SCAN_ROOTS,
        "summary": {
            "scanned_file_count": len(files),
            "image_file_count": len(image_files),
            "runtime_art_image_count": len(runtime_images),
            "manifest_file_count": len(manifest_files),
            "res_reference_count": len(all_refs),
            "unresolved_res_reference_count": len(unresolved_refs),
        },
        "image_groups": dict(sorted(group_counter.items())),
        "png_dimension_samples": dict(sorted(list(png_dimension_samples.items())[:120])),
        "manifest_files": manifest_files,
        "production_packages": production_packages,
        "references": {
            "files_with_res_refs": len(refs_by_file),
            "unresolved_res_refs": unresolved_refs,
            "unresolved_res_refs_by_category": group_unresolved_refs(unresolved_refs),
            "unreferenced_runtime_art_images": {
                "count": len(unreferenced_runtime),
                "note": "Unreferenced does not mean invalid; it means not currently found in scanned text/data references.",
                "paths": unreferenced_runtime[:120],
            },
        },
        "data_backlogs": data_backlogs,
        "dirty_data": dirty_data,
        "prioritized_backlog": prioritized_backlog,
    }


def main() -> None:
    inventory = build_inventory()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: wrote {OUTPUT.relative_to(ROOT).as_posix()}")
    print(json.dumps(inventory["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
