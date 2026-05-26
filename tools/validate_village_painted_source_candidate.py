from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageStat


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production" / "assets" / "regions" / "village_world2d" / "v001"
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
LAYOUT_LOCK = PACKAGE_DIR / "01_layout_lock" / "layout_lock.json"
LAYER_CONTRACT = PACKAGE_DIR / "03_layer_export" / "layer_contract.json"
SOURCE_IMAGE = PACKAGE_DIR / "02_source_generation" / "village_painted_source.png"
LAYOUT_DRAFT_IMAGE = PACKAGE_DIR / "02_source_generation" / "layout_structure_drafts" / "village_layout_structure_draft_v001.png"
ACCEPTANCE = PACKAGE_DIR / "02_source_generation" / "source_acceptance.json"
LAYOUT_DRAFT_ACCEPTANCE = PACKAGE_DIR / "02_source_generation" / "layout_structure_drafts" / "village_layout_structure_draft_v001_acceptance.json"
REVIEW_OVERLAY = PACKAGE_DIR / "05_review_and_qa" / "village_painted_source_review_overlay_v001.png"
REVIEW_MD = PACKAGE_DIR / "05_review_and_qa" / "source_candidate_review.md"
GENERATOR = ROOT / "tools" / "generate_village_painted_source_candidate.py"

CANVAS = (1800, 1200)
REQUIRED_ANCHORS = [
    "VillageNotice",
    "SeedStallProxy",
    "OldMapleClue",
    "VillageReturnPath",
    "AoiVillageStandLateMorning",
    "BenchRestProp",
]
LAYOUT_DRAFT_ID = "village_layout_structure_draft_v001"


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read(path: Path) -> str:
    require(path.is_file(), f"missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(read(path))
    except json.JSONDecodeError as exc:
        fail(f"invalid json in {path.relative_to(ROOT)}: {exc}")
    require(isinstance(value, dict), f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _validate_image(path: Path, *, opaque: bool) -> Image.Image:
    require(path.is_file(), f"missing image: {path.relative_to(ROOT)}")
    image = Image.open(path)
    require(image.size == CANVAS, f"{path.relative_to(ROOT)} must be {CANVAS}, got {image.size}")
    require(image.mode in {"RGB", "RGBA"}, f"{path.relative_to(ROOT)} must be RGB/RGBA, got {image.mode}")
    if opaque and image.mode == "RGBA":
        alpha = image.getchannel("A")
        extrema = alpha.getextrema()
        require(extrema == (255, 255), f"{path.relative_to(ROOT)} must be fully opaque")
    return image.convert("RGB")


def _validate_candidate_has_visual_content(image: Image.Image, layout: dict[str, Any]) -> None:
    stat = ImageStat.Stat(image)
    channel_ranges = [high - low for low, high in image.getextrema()]
    require(max(channel_ranges) > 90, "candidate image should have enough color/value range for visual review")
    # The source intentionally has broad low-saturation grass areas, so use a
    # modest global variance threshold and rely on anchor crops below for detail.
    require(sum(stat.var) > 1000, "candidate image variance too low; it may be blank or flat")

    zones = {str(zone.get("id")): zone for zone in layout.get("object_zones", []) if isinstance(zone, dict)}
    for anchor_id in REQUIRED_ANCHORS:
        require(anchor_id in zones, f"layout missing anchor {anchor_id}")
        zone = zones[anchor_id]
        if "source_rect" not in zone:
            continue
        x, y, w, h = [int(v) for v in zone["source_rect"]]
        crop = image.crop((max(0, x), max(0, y), min(CANVAS[0], x + w), min(CANVAS[1], y + h)))
        crop_stat = ImageStat.Stat(crop)
        require(sum(crop_stat.var) > 250, f"anchor area appears too flat: {anchor_id}")


def _validate_acceptance(workflow: dict[str, Any]) -> None:
    acceptance = load_json(LAYOUT_DRAFT_ACCEPTANCE)
    require(acceptance.get("candidate_id") == LAYOUT_DRAFT_ID, "acceptance candidate_id mismatch")
    require(acceptance.get("status") == "layout_structure_draft_pending_seamless_master_review", "acceptance status must remain a layout draft")
    require(acceptance.get("candidate_type") == "layout_structure_draft", "acceptance candidate_type must be layout_structure_draft")
    require(acceptance.get("not_final_painted_source") is True, "acceptance must mark this image as not final painted_source")
    require(acceptance.get("do_not_split_layers_from_this_image") is True, "acceptance must block layer splitting from this image")
    require(acceptance.get("source_image") == rel(LAYOUT_DRAFT_IMAGE), "acceptance source path mismatch")
    require(acceptance.get("review_overlay") == rel(REVIEW_OVERLAY), "acceptance overlay path mismatch")
    require(acceptance.get("runtime_replacement") is False, "acceptance must keep runtime_replacement=false")
    require(acceptance.get("launch_quality_approved") is False, "acceptance must keep launch_quality_approved=false")
    require(acceptance.get("human_visual_approval") is False, "acceptance must keep human_visual_approval=false")
    require(acceptance.get("layer_export_approved") is False, "acceptance must keep layer_export_approved=false")
    precheck = acceptance.get("codex_visual_precheck")
    require(isinstance(precheck, dict), "acceptance must include codex_visual_precheck")
    require(precheck.get("status") == "passed_readability_precheck", "codex visual precheck status mismatch")
    require(precheck.get("not_human_visual_approval") is True, "codex precheck must not be treated as human approval")
    precheck_text = json.dumps(precheck, ensure_ascii=False).lower()
    for token in ["west, north, east, and south", "aoi standing pocket", "blocking_note"]:
        require(token in precheck_text, f"codex visual precheck missing token: {token}")

    source_candidate = workflow.get("source_candidate", {})
    require(isinstance(source_candidate, dict), "workflow missing source_candidate object")
    require(source_candidate.get("source_image") == rel(LAYOUT_DRAFT_IMAGE), "workflow source candidate path mismatch")
    require(source_candidate.get("review_overlay") == rel(REVIEW_OVERLAY), "workflow review overlay path mismatch")
    require(source_candidate.get("acceptance_record") == rel(LAYOUT_DRAFT_ACCEPTANCE), "workflow acceptance record path mismatch")
    require(source_candidate.get("candidate_type") == "layout_structure_draft", "workflow source_candidate must now be a layout draft")
    require(source_candidate.get("not_final_painted_source") is True, "workflow must mark source_candidate as not final painted_source")
    require(source_candidate.get("do_not_split_layers_from_this_image") is True, "workflow must block splitting from the layout draft")
    for key in ["human_visual_approval", "layer_export_approved", "runtime_replacement"]:
        require(source_candidate.get(key) is False, f"workflow source_candidate must keep {key}=false")


def _validate_contract_links() -> None:
    contract = load_json(LAYER_CONTRACT)
    source_image = contract.get("source_image", {})
    require(isinstance(source_image, dict), "layer contract missing source_image")
    require(source_image.get("path") == rel(SOURCE_IMAGE), "layer contract source image path should point at the future true source path")
    require(source_image.get("required_before_layer_export") is True, "layer contract must still require source before layer export")
    require(
        source_image.get("current_file_status") in {"layout_structure_draft_only", "accepted_true_painted_source"},
        "layer contract source status mismatch",
    )
    if source_image.get("current_file_status") == "layout_structure_draft_only":
        require(source_image.get("do_not_split_current_file") is True, "layer contract must block splitting the current layout draft")
    else:
        require(source_image.get("do_not_split_current_file") is False, "accepted source should be allowed for layer export")


def _validate_connector_paths(layout: dict[str, Any]) -> None:
    connector_paths = layout.get("seam_connector_paths")
    require(isinstance(connector_paths, list), "layout must include seam_connector_paths")
    connector_ids = {str(path.get("id", "")) for path in connector_paths if isinstance(path, dict)}
    require("west_east_connector_spine" in connector_ids, "layout missing west_east_connector_spine")
    require("north_south_connector_spine" in connector_ids, "layout missing north_south_connector_spine")
    for raw_connector in connector_paths:
        require(isinstance(raw_connector, dict), "connector path must be an object")
        points = raw_connector.get("source_points")
        require(isinstance(points, list) and len(points) >= 4, f"{raw_connector.get('id')} must define at least four source points")
        require(float(raw_connector.get("source_width", 0)) >= 40, f"{raw_connector.get('id')} source_width too narrow for review")


def _validate_review_overlay(source: Image.Image) -> None:
    overlay = _validate_image(REVIEW_OVERLAY, opaque=True)
    diff = ImageChops.difference(source, overlay)
    stat = ImageStat.Stat(diff)
    require(sum(stat.sum) > 1_000_000, "review overlay should visibly differ from source")
    review_text = read(REVIEW_MD)
    for token in [
        "Codex visual precheck",
        "not human visual approval",
        "not final painted source",
        "Do not split layers from this structure draft",
        "west return road and north/east/south future connector roads",
        "Aoi standing pocket",
        "human visual approval",
        "layer export",
        "runtime replacement",
        "VillageNotice",
        "SeedStallProxy",
        "OldMapleClue",
    ]:
        require(token in review_text, f"review markdown missing token: {token}")


def _validate_generator_contract() -> None:
    text = read(GENERATOR)
    for token in ["LAYOUT_LOCK", "village_painted_source.png", "source_acceptance.json", "runtime_replacement", "launch_quality_approved"]:
        require(token in text, f"generator missing token: {token}")
    require("draw_source" in text and "draw_review_overlay" in text, "generator should keep source and overlay drawing separate")


def main() -> None:
    workflow = load_json(WORKFLOW)
    require(
        workflow.get("status")
        in {
            "layout_structure_draft_pending_seamless_master_review",
            "true_painted_source_candidate_pending_human_visual_review",
            "accepted_source_layers_exported_pending_layer_review",
        },
        "workflow status should preserve the layout draft or true-candidate review state",
    )
    require(
        workflow.get("current_phase") in {"01_world_continuity_review", "02_source_generation_review", "03_layer_export_review"},
        "workflow current phase should be a source-review phase",
    )
    require(workflow.get("runtime_replacement") is False, "workflow must keep runtime_replacement=false")
    require(workflow.get("launch_quality_approved") is False, "workflow must keep launch_quality_approved=false")
    phase_status = workflow.get("phase_status", {})
    require(isinstance(phase_status, dict), "workflow phase_status must be an object")
    require(
        phase_status.get("03_layer_export") in {"blocked_until_true_painted_source_human_visual_review", "exported_pending_layer_review"},
        "layer export phase mismatch",
    )

    layout = load_json(LAYOUT_LOCK)
    _validate_connector_paths(layout)
    source = _validate_image(LAYOUT_DRAFT_IMAGE, opaque=True)
    _validate_candidate_has_visual_content(source, layout)
    _validate_acceptance(workflow)
    _validate_contract_links()
    _validate_review_overlay(source)
    _validate_generator_contract()
    print("OK: Village painted source candidate validated")


if __name__ == "__main__":
    main()
