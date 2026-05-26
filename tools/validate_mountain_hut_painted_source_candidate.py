from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageStat


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production" / "assets" / "regions" / "mountain_hut_world2d" / "v001"
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
LAYOUT_LOCK = PACKAGE_DIR / "01_layout_lock" / "layout_lock.json"
LAYER_CONTRACT = PACKAGE_DIR / "03_layer_export" / "layer_contract.json"
SOURCE_IMAGE = PACKAGE_DIR / "02_source_generation" / "mountain_hut_painted_source.png"
ACCEPTANCE = PACKAGE_DIR / "02_source_generation" / "source_acceptance.json"
REVIEW_OVERLAY = PACKAGE_DIR / "05_review_and_qa" / "mountain_hut_painted_source_review_overlay_v001.png"
REVIEW_MD = PACKAGE_DIR / "05_review_and_qa" / "source_candidate_review.md"
GENERATOR = ROOT / "tools" / "generate_mountain_hut_painted_source_candidate.py"

CANVAS = (1800, 1200)
REQUIRED_ANCHORS = [
    "MountainHutExterior",
    "HutDoor",
    "HutApproachPath",
    "VillageConnectorPath",
]
CANDIDATE_ID = "mountain_hut_painted_source_candidate_v001"


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read(path: Path) -> str:
    require(path.is_file(), f"missing required file: {rel(path)}")
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(read(path))
    except json.JSONDecodeError as exc:
        fail(f"invalid json in {rel(path)}: {exc}")
    require(isinstance(value, dict), f"{rel(path)} must contain a JSON object")
    return value


def validate_image(path: Path, *, opaque: bool) -> Image.Image:
    require(path.is_file(), f"missing image: {rel(path)}")
    image = Image.open(path)
    require(image.size == CANVAS, f"{rel(path)} must be {CANVAS}, got {image.size}")
    require(image.mode in {"RGB", "RGBA"}, f"{rel(path)} must be RGB/RGBA, got {image.mode}")
    if opaque and image.mode == "RGBA":
        require(image.getchannel("A").getextrema() == (255, 255), f"{rel(path)} must be fully opaque")
    return image.convert("RGB")


def validate_visual_content(image: Image.Image, layout: dict[str, Any]) -> None:
    ranges = [high - low for low, high in image.getextrema()]
    stat = ImageStat.Stat(image)
    require(max(ranges) > 90, "candidate should have enough color/value range for visual review")
    require(sum(stat.var) > 900, "candidate image variance too low; it may be blank or flat")

    zones = {str(zone.get("id")): zone for zone in layout.get("object_zones", []) if isinstance(zone, dict)}
    for anchor_id in REQUIRED_ANCHORS:
        require(anchor_id in zones, f"layout missing anchor {anchor_id}")
        x, y, w, h = [int(v) for v in zones[anchor_id]["source_rect"]]
        crop = image.crop((max(0, x), max(0, y), min(CANVAS[0], x + w), min(CANVAS[1], y + h)))
        crop_stat = ImageStat.Stat(crop)
        require(sum(crop_stat.var) > 180, f"anchor area appears too flat: {anchor_id}")


def validate_layout(layout: dict[str, Any]) -> None:
    require(layout.get("parent_connection_id") == "village_to_mountain_hut", "layout must bind to village_to_mountain_hut")
    seams = layout.get("seam_connectors")
    require(isinstance(seams, list), "layout seam_connectors must be a list")
    west = next((item for item in seams if isinstance(item, dict) and item.get("edge") == "west"), None)
    require(west is not None, "layout must keep west seam connector")
    require(west.get("connection_id") == "village_to_mountain_hut", "west seam connection mismatch")

    roads = layout.get("road_paths")
    require(isinstance(roads, list), "layout road_paths must be a list")
    road_ids = {str(item.get("id")) for item in roads if isinstance(item, dict)}
    require("village_connector_path" in road_ids, "layout missing village_connector_path")
    require("hut_door_spur" in road_ids, "layout missing hut_door_spur")


def validate_acceptance(workflow: dict[str, Any]) -> None:
    acceptance = load_json(ACCEPTANCE)
    require(acceptance.get("candidate_id") == CANDIDATE_ID, "acceptance candidate_id mismatch")
    require(acceptance.get("status") == "pending_human_visual_review", "acceptance status mismatch")
    require(acceptance.get("candidate_type") == "true_storybook_painted_source_candidate", "acceptance candidate_type mismatch")
    require(acceptance.get("source_image") == rel(SOURCE_IMAGE), "acceptance source path mismatch")
    require(acceptance.get("review_overlay") == rel(REVIEW_OVERLAY), "acceptance overlay path mismatch")
    for key in ["human_visual_approval", "layer_export_approved", "runtime_replacement", "launch_quality_approved"]:
        require(acceptance.get(key) is False, f"acceptance must keep {key}=false")

    precheck = acceptance.get("codex_visual_precheck")
    require(isinstance(precheck, dict), "acceptance must include codex_visual_precheck")
    require(precheck.get("not_human_visual_approval") is True, "Codex precheck is not human visual approval")
    require(
        precheck.get("quality_status") == "improved_programmatic_storybook_candidate_not_final_art",
        "precheck quality status should mark improved candidate but not final art",
    )
    precheck_text = json.dumps(precheck, ensure_ascii=False).lower()
    for token in ["west road", "hut door", "no combat", "improved storybook texture", "layer export remains blocked"]:
        require(token in precheck_text, f"precheck missing token: {token}")

    source_candidate = workflow.get("source_candidate")
    require(isinstance(source_candidate, dict), "workflow missing source_candidate")
    require(source_candidate.get("candidate_id") == CANDIDATE_ID, "workflow candidate id mismatch")
    require(source_candidate.get("image") == rel(SOURCE_IMAGE), "workflow candidate image mismatch")
    require(source_candidate.get("review_overlay") == rel(REVIEW_OVERLAY), "workflow review overlay mismatch")
    require(source_candidate.get("acceptance_record") == rel(ACCEPTANCE), "workflow acceptance record mismatch")
    for key in ["human_visual_approval", "layer_export_approved", "runtime_replacement", "launch_quality_approved"]:
        require(source_candidate.get(key) is False, f"workflow source_candidate must keep {key}=false")


def validate_workflow_and_contract() -> None:
    workflow = load_json(WORKFLOW)
    require(
        workflow.get("status") in {
            "true_painted_source_candidate_pending_human_visual_review",
            "v002_source_candidate_ready_for_human_art_review",
            "mountain_hut_v002_visual_review_rejected_needs_v003_repaint",
            "mountain_hut_v003_candidate_ready_for_visual_review",
            "mountain_hut_v004_candidate_ready_for_visual_review",
            "v004_semantic_layers_exported_pending_review",
        },
        "workflow status mismatch",
    )
    require(
        workflow.get("current_phase") in {
            "02_source_generation_review",
            "02_source_generation_v002_review",
            "02_source_generation_v003_handoff",
            "02_source_generation_v003_review",
            "02_source_generation_v004_review",
            "03_layer_export_v004_semantic_review",
        },
        "workflow current_phase mismatch",
    )
    require(workflow.get("runtime_replacement") is False, "workflow must keep runtime_replacement=false")
    require(workflow.get("launch_quality_approved") is False, "workflow must keep launch_quality_approved=false")
    phase_status = workflow.get("phase_status")
    require(isinstance(phase_status, dict), "workflow phase_status must be object")
    require(phase_status.get("02_source_generation") == "candidate_generated_pending_human_visual_review", "source phase mismatch")
    require(
        phase_status.get("03_layer_export")
        in {
            "blocked_until_source_acceptance",
            "blocked_until_v003_visual_acceptance",
            "blocked_until_v004_visual_acceptance",
            "v004_semantic_layers_exported_pending_review",
        },
        "layer export must stay blocked",
    )
    validation = workflow.get("validation")
    require(isinstance(validation, dict), "workflow validation must be object")
    require(validation.get("source_candidate_validator") == "tools/validate_mountain_hut_painted_source_candidate.py", "workflow source validator mismatch")

    contract = load_json(LAYER_CONTRACT)
    source_image = contract.get("source_image")
    require(isinstance(source_image, dict), "layer contract missing source_image")
    require(source_image.get("id") == "mountain_hut_painted_source", "layer contract source id mismatch")
    require(source_image.get("path") == rel(SOURCE_IMAGE), "layer contract source path mismatch")
    require(
        source_image.get("current_file_status") in {
            "candidate_pending_human_visual_review",
            "v002_visual_review_rejected",
            "v003_candidate_pending_visual_review",
            "v004_candidate_pending_visual_review",
            "v004_codex_visual_accepted_for_semantic_layer_export",
        },
        "layer contract source status mismatch",
    )
    require(source_image.get("human_visual_approval") is False, "layer contract must keep source human approval false")
    require(source_image.get("layer_export_approved") is False, "layer contract must keep layer export approval false")
    require(contract.get("runtime_replacement") is False, "layer contract must keep runtime_replacement=false")

    validate_acceptance(workflow)


def validate_review_overlay(source: Image.Image) -> None:
    overlay = validate_image(REVIEW_OVERLAY, opaque=True)
    diff = ImageChops.difference(source, overlay)
    stat = ImageStat.Stat(diff)
    require(sum(stat.sum) > 1_000_000, "review overlay should visibly differ from source")
    review_text = read(REVIEW_MD)
    for token in [
        CANDIDATE_ID,
        "pending_human_visual_review",
        "not human visual approval",
        "Do not export runtime layers",
        "Do not replace runtime art",
        "village_to_mountain_hut",
        "MountainHut exterior",
        "HutDoor",
        "HutApproachPath",
        "improved programmatic storybook candidate",
        "not launch-quality approval",
    ]:
        require(token in review_text, f"review markdown missing token: {token}")


def validate_generator_contract() -> None:
    text = read(GENERATOR)
    for token in [
        "LAYOUT_LOCK",
        "mountain_hut_painted_source.png",
        "source_acceptance.json",
        "runtime_replacement",
        "launch_quality_approved",
    ]:
        require(token in text, f"generator missing token: {token}")
    require("draw_source" in text and "draw_review_overlay" in text, "generator should keep source and overlay drawing separate")


def main() -> None:
    layout = load_json(LAYOUT_LOCK)
    validate_layout(layout)
    source = validate_image(SOURCE_IMAGE, opaque=True)
    validate_visual_content(source, layout)
    validate_workflow_and_contract()
    validate_review_overlay(source)
    validate_generator_contract()
    print("OK: MountainHut painted source candidate validates")


if __name__ == "__main__":
    main()
