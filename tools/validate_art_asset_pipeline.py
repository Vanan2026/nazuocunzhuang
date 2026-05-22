from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/14_ART_ASSET_PIPELINE.md"
AUDIT_SCRIPT = ROOT / "tools/audit_art_asset_inventory.py"
INVENTORY = ROOT / "production/assets/art_asset_inventory_2026-05-20.json"
PROJECT_MANIFEST = ROOT / "production/assets/project_art_production_manifest_2026-05-19.json"
EXPECTED_P0_ITEM_CATEGORIES = {"seed", "material", "forage", "fish", "food", "key"}
EXPECTED_P0_NPCS = {"aoi", "gen", "mika", "hana"}
MAX_INVENTORY_BYTES = 5_000_000


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path, label: str) -> Any:
    require(path.exists(), f"missing {label}: {path.relative_to(ROOT).as_posix()}")
    return json.loads(path.read_text(encoding="utf-8"))


def as_dict(value: Any, label: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"{label} must be an object")
    return value


def run_audit() -> None:
    result = subprocess.run([sys.executable, str(AUDIT_SCRIPT)], cwd=ROOT, text=True, capture_output=True)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        fail("audit_art_asset_inventory.py failed")


def validate_doc() -> None:
    require(DOC.exists(), "missing docs/14_ART_ASSET_PIPELINE.md")
    text = DOC.read_text(encoding="utf-8")
    for token in [
        "source-first",
        "production/assets/art_asset_inventory_2026-05-20.json",
        "draft / usable / approved / rejected / archived",
        "不要围绕单个场景反复 patch",
        "完整 P0 NPC",
        "强清理",
        "P0",
    ]:
        require(token in text, f"pipeline doc missing required token: {token}")
    require("Hana 最小" not in text and "最小 NPC" not in text, "pipeline doc must not describe Hana/NPC art as minimum")


def validate_project_manifest() -> None:
    manifest = as_dict(read_json(PROJECT_MANIFEST, "project art manifest"), "project art manifest")
    inventory = as_dict(manifest.get("asset_inventory"), "asset_inventory")
    require(inventory.get("current_inventory") == "production/assets/art_asset_inventory_2026-05-20.json", "manifest inventory path mismatch")
    require(inventory.get("audit_script") == "tools/audit_art_asset_inventory.py", "manifest audit script mismatch")
    require(inventory.get("validator") == "tools/validate_art_asset_pipeline.py", "manifest validator mismatch")
    require("data_backlogs.npc_complete_runtime_art" in inventory.get("primary_outputs", []), "manifest must expose complete NPC art backlog")
    require("npc_minimum_runtime_art" not in inventory.get("primary_outputs", []), "manifest must not expose minimum NPC backlog")
    entrypoints = manifest.get("validation_entrypoints", [])
    require("tools/validate_art_asset_pipeline.py" in entrypoints, "project manifest must list art pipeline validator")

    character_assets = as_dict(manifest.get("character_assets"), "character_assets")
    mvp_npcs = as_dict(character_assets.get("mvp_npcs"), "mvp_npcs")
    require(mvp_npcs.get("status") in {"complete_runtime_package_backlog", "complete_runtime_package_usable"}, "MVP NPC status must require or provide complete runtime packages")
    required_ids = set(mvp_npcs.get("required_npc_ids", []))
    require(EXPECTED_P0_NPCS <= required_ids, f"manifest missing P0 NPC ids: {sorted(EXPECTED_P0_NPCS - required_ids)}")


def validate_inventory() -> None:
    require(INVENTORY.stat().st_size < MAX_INVENTORY_BYTES, "art inventory file is unexpectedly large; audit output may be recursively scanning itself")
    data = as_dict(read_json(INVENTORY, "art inventory"), "art inventory")
    require(data.get("schema_version") == 1, "inventory schema version mismatch")
    require(data.get("generated_by") == "tools/audit_art_asset_inventory.py", "inventory generated_by mismatch")
    summary = as_dict(data.get("summary"), "summary")
    require(summary.get("image_file_count", 0) > 0, "inventory did not find image files")
    require(summary.get("runtime_art_image_count", 0) > 0, "inventory did not find runtime art images")
    require(summary.get("manifest_file_count", 0) > 0, "inventory did not find manifest files")

    references = as_dict(data.get("references"), "references")
    grouped_refs = as_dict(references.get("unresolved_res_refs_by_category"), "unresolved_res_refs_by_category")
    require("template_or_regex_literal" in grouped_refs, "template/regex unresolved refs must be grouped separately")

    data_backlogs = as_dict(data.get("data_backlogs"), "data_backlogs")
    item_icons = as_dict(data_backlogs.get("item_icons"), "item_icons")
    missing_count = int(item_icons.get("missing_count", 0))
    missing_categories = set(item_icons.get("expected_p0_categories_still_missing", []))
    if missing_count > 0:
        require(bool(missing_categories), "P0 item icon backlog categories must be explicit when icons are missing")
        require(item_icons.get("missing_by_category"), "P0 item icon missing_by_category must be populated when icons are missing")
    else:
        require(not missing_categories, "P0 item icon missing categories should be empty after backlog is resolved")
        require(not item_icons.get("missing_by_category"), "P0 item icon missing_by_category should be empty after backlog is resolved")

    complete_npc = as_dict(data_backlogs.get("npc_complete_runtime_art"), "npc_complete_runtime_art")
    require(set(complete_npc.get("required_npc_ids", [])) == EXPECTED_P0_NPCS, "complete NPC backlog must cover Aoi/Gen/Mika/Hana")
    require(complete_npc.get("required_count") == 44, "complete NPC package should require 44 runtime assets for 4 P0 NPCs")
    npc_missing_count = int(complete_npc.get("missing_count", 0))
    missing_by_npc = as_dict(complete_npc.get("missing_by_npc"), "missing_by_npc")
    if npc_missing_count > 0:
        require(set(missing_by_npc).issubset(EXPECTED_P0_NPCS), f"complete NPC backlog has unknown NPC ids: {sorted(set(missing_by_npc) - EXPECTED_P0_NPCS)}")
        require(sum(int(value) for value in missing_by_npc.values()) == npc_missing_count, "complete NPC missing_by_npc does not match missing_count")
    else:
        require(not missing_by_npc, "complete NPC missing_by_npc should be empty after backlog is resolved")

    require("npc_minimum_runtime_art" not in data_backlogs, "inventory must not use minimum NPC backlog key")

    dirty = as_dict(data.get("dirty_data"), "dirty_data")
    backup_scenes = as_dict(dirty.get("importable_backup_scenes"), "importable_backup_scenes")
    require(backup_scenes.get("count", 0) == 0, "importable HomeArea backup scenes must be deleted after hard cleanup")
    legacy_dirs = as_dict(dirty.get("legacy_tool_dirs"), "legacy_tool_dirs")
    require(legacy_dirs.get("count", 0) == 0, "legacy Homeyard tool dirs must be deleted after hard cleanup")
    stale_tools = as_dict(dirty.get("stale_home_area_tool_candidates"), "stale_home_area_tool_candidates")
    require(stale_tools.get("count", 0) == 0, "obsolete HomeArea route tools must be deleted after hard cleanup")
    active_forbidden = as_dict(dirty.get("active_scene_forbidden_refs"), "active_scene_forbidden_refs")
    require(active_forbidden.get("count", 0) == 0, "active scenes still reference forbidden art source dirs")

    package_gaps = [pkg for pkg in data.get("production_packages", []) if isinstance(pkg, dict) and pkg.get("needs_manifest_review")]
    require(not package_gaps, f"versioned production package roots without manifests: {[pkg.get('dir') for pkg in package_gaps]}")

    backlog = data.get("prioritized_backlog", [])
    require(isinstance(backlog, list) and len(backlog) >= 5, "prioritized backlog must contain the current production queue")
    backlog_ids = {item.get("id") for item in backlog if isinstance(item, dict)}
    for required in ["item_icon_backlog", "p0_npc_complete_runtime_art", "home_area_capture_review", "hard_cleanup_obsolete_home_area_routes"]:
        require(required in backlog_ids, f"prioritized backlog missing {required}")
    require("hana_npc_minimum_art" not in backlog_ids, "prioritized backlog must not use old Hana minimum target")


def main() -> None:
    require(AUDIT_SCRIPT.exists(), "missing tools/audit_art_asset_inventory.py")
    run_audit()
    validate_doc()
    validate_project_manifest()
    validate_inventory()
    print("OK: art asset pipeline validates complete P0 NPC backlog, hard-cleaned dirty data, and P0 item gates")


if __name__ == "__main__":
    main()
