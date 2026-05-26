from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageStat


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production" / "assets" / "regions" / "village_world2d" / "v001"
HANDOFF_DIR = PACKAGE_DIR / "02_source_generation" / "v002_inherited_world_base_repaint"
HANDOFF_JSON = HANDOFF_DIR / "village_inherited_repaint_handoff_v002.json"
HANDOFF_BRIEF = HANDOFF_DIR / "village_inherited_repaint_brief_v002.md"
REFERENCE_SHEET = HANDOFF_DIR / "village_inherited_repaint_reference_sheet_v002.png"
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
PROJECT_MANIFEST = ROOT / "production" / "assets" / "project_art_production_manifest_2026-05-19.json"
WORLD_BASE_MANIFEST = ROOT / "production" / "assets" / "outdoor_world_world2d" / "v001" / "02_world_base_no_foreground" / "world_base_manifest.json"
WORLD_BASE_CROP = ROOT / "production" / "assets" / "outdoor_world_world2d" / "v001" / "02_world_base_no_foreground" / "region_base_crops" / "village_base_no_foreground.png"
OLD_ACCEPTED_SOURCE = PACKAGE_DIR / "02_source_generation" / "village_painted_source.png"
LAYOUT_LOCK = PACKAGE_DIR / "01_layout_lock" / "layout_lock.json"
OUTDOOR_WORKFLOW = ROOT / "production" / "assets" / "outdoor_world_world2d" / "v001" / "workflow_manifest.json"

HANDOFF_ID = "village_inherited_world_base_repaint_v002"
STATUS = "handoff_ready_for_artist_repaint_not_source_accepted"
CANVAS = [1800, 1200]
REFERENCE_SHEET_SIZE = (2400, 1500)


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_text(path: Path) -> str:
    require(path.is_file(), f"missing required file: {rel(path)}")
    return path.read_text(encoding="utf-8-sig")


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {rel(path)}: {exc}")
    require(isinstance(data, dict), f"{rel(path)} must contain a JSON object")
    return data


def as_dict(value: Any, label: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"{label} must be an object")
    return value


def as_list(value: Any, label: str) -> list[Any]:
    require(isinstance(value, list), f"{label} must be a list")
    return value


def validate_handoff_json() -> dict[str, Any]:
    handoff = load_json(HANDOFF_JSON)
    require(handoff.get("handoff_id") == HANDOFF_ID, "handoff id mismatch")
    require(handoff.get("status") == STATUS, "handoff status mismatch")
    require(handoff.get("region_id") == "village", "handoff region mismatch")
    require(handoff.get("runtime_replacement") is False, "handoff must keep runtime_replacement=false")
    require(handoff.get("launch_quality_approved") is False, "handoff must keep launch_quality_approved=false")
    require(handoff.get("human_visual_approval") is False, "handoff must not claim human visual approval")
    require(handoff.get("layer_export_approved") is False, "handoff must not approve layer export")

    refs = as_dict(handoff.get("references"), "handoff.references")
    expected_refs = {
        "world_base_manifest": WORLD_BASE_MANIFEST,
        "inherited_world_base_crop": WORLD_BASE_CROP,
        "old_village_quality_reference_only": OLD_ACCEPTED_SOURCE,
        "village_layout_lock": LAYOUT_LOCK,
        "outdoor_world_workflow": OUTDOOR_WORKFLOW,
        "brief": HANDOFF_BRIEF,
        "reference_sheet": REFERENCE_SHEET,
    }
    for key, path in expected_refs.items():
        require(refs.get(key) == rel(path), f"reference path mismatch for {key}")
        require(path.exists(), f"referenced artifact missing for {key}: {rel(path)}")

    contract = as_dict(handoff.get("output_contract"), "handoff.output_contract")
    require(contract.get("target_source_id") == "village_painted_source_v002", "target source id mismatch")
    require(contract.get("canvas") == CANVAS, "target canvas mismatch")
    require(contract.get("must_inherit_composition_from_world_base_crop") is True, "must inherit composition from world-base crop")
    require(contract.get("old_source_is_quality_reference_only") is True, "old source must be quality reference only")
    require(contract.get("full_canvas_layers_required_after_acceptance") is True, "future layers must keep full canvas")
    require(contract.get("foreground_occlusion_after_base_acceptance_only") is True, "foreground must wait for base acceptance")
    require("registration-perfect" in str(contract.get("registration_target")), "registration target wording mismatch")

    forbidden = as_list(handoff.get("forbidden_actions"), "handoff.forbidden_actions")
    for token in [
        "Do not use the old isolated Village source as runtime replacement.",
        "Do not split foreground layers before the inherited base repaint is accepted.",
        "Do not crop transparent runtime layers to object bounds.",
    ]:
        require(token in forbidden, f"missing forbidden action: {token}")
    return handoff


def validate_brief_text() -> None:
    text = read_text(HANDOFF_BRIEF).lower()
    for token in [
        "inherited world-base crop",
        "registration-perfect",
        "full-canvas",
        "foreground_occlusion",
        "quality reference only",
        "not runtime replacement",
        "not final art approval",
        "no combat",
    ]:
        require(token in text, f"brief missing token: {token}")


def validate_reference_sheet() -> None:
    require(REFERENCE_SHEET.is_file(), f"missing reference sheet: {rel(REFERENCE_SHEET)}")
    image = Image.open(REFERENCE_SHEET).convert("RGB")
    require(image.size == REFERENCE_SHEET_SIZE, f"reference sheet size mismatch: {image.size}")
    require(sum(ImageStat.Stat(image).var) > 500.0, "reference sheet appears blank or too flat")


def validate_workflow_and_project_links(handoff: dict[str, Any]) -> None:
    workflow = load_json(WORKFLOW)
    block = as_dict(workflow.get("inherited_world_base_repaint_handoff"), "workflow.inherited_world_base_repaint_handoff")
    require(block.get("handoff_id") == HANDOFF_ID, "workflow handoff id mismatch")
    require(block.get("status") == STATUS, "workflow handoff status mismatch")
    require(block.get("manifest") == rel(HANDOFF_JSON), "workflow handoff manifest path mismatch")
    require(block.get("brief") == rel(HANDOFF_BRIEF), "workflow handoff brief path mismatch")
    require(block.get("reference_sheet") == rel(REFERENCE_SHEET), "workflow handoff reference sheet path mismatch")
    require(block.get("inherits_from_world_base_crop") == rel(WORLD_BASE_CROP), "workflow inherited crop path mismatch")
    require(block.get("old_source_policy") == "quality_reference_only", "workflow old source policy mismatch")
    for key in ["runtime_replacement", "launch_quality_approved", "human_visual_approval", "layer_export_approved"]:
        require(block.get(key) is False, f"workflow handoff must keep {key}=false")
    require(handoff.get("status") == block.get("status"), "workflow and handoff status diverge")

    project = load_json(PROJECT_MANIFEST)
    regions = as_list(project.get("current_runtime_regions"), "project.current_runtime_regions")
    village = None
    for record in regions:
        item = as_dict(record, "project region")
        if item.get("region_id") == "Region_Village":
            village = item
            break
    require(village is not None, "project manifest missing Region_Village")
    assert village is not None
    require(village.get("active_inherited_repaint_handoff") == rel(HANDOFF_JSON), "project manifest handoff pointer mismatch")
    require(village.get("runtime_replacement") is False, "project Village must keep runtime_replacement=false")
    next_step = str(village.get("next_art_step", "")).lower()
    require(
        "inherited" in next_step or "semantic layers" in next_step,
        "project Village next step must mention inherited repaint or semantic layers",
    )


def validate_world_crop_contract() -> None:
    manifest = load_json(WORLD_BASE_MANIFEST)
    crops = as_list(manifest.get("region_crops"), "world base region crops")
    village_crop = None
    for crop in crops:
        record = as_dict(crop, "world base crop")
        if record.get("region_id") == "village":
            village_crop = record
            break
    require(village_crop is not None, "world base manifest missing village crop")
    assert village_crop is not None
    require(village_crop.get("path") == rel(WORLD_BASE_CROP), "world base manifest Village crop path mismatch")
    require(village_crop.get("canvas") == CANVAS, "world base Village crop canvas mismatch")
    require(village_crop.get("foreground_removed") is True, "world base Village crop must be foreground removed")


def main() -> None:
    handoff = validate_handoff_json()
    validate_brief_text()
    validate_reference_sheet()
    validate_workflow_and_project_links(handoff)
    validate_world_crop_contract()
    print("OK: Village inherited-crop repaint handoff validates")


if __name__ == "__main__":
    main()
