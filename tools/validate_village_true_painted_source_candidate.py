from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageStat


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production" / "assets" / "regions" / "village_world2d" / "v001"
CANDIDATE_DIR = PACKAGE_DIR / "02_source_generation" / "true_source_candidates"
CANDIDATE_ID = "village_true_painted_source_candidate_v001"
METADATA = CANDIDATE_DIR / f"{CANDIDATE_ID}.json"
NORMALIZED_IMAGE = CANDIDATE_DIR / f"{CANDIDATE_ID}.png"
ORIGINAL_IMAGE = CANDIDATE_DIR / f"{CANDIDATE_ID}_original.png"
PROMPT_FILE = CANDIDATE_DIR / f"{CANDIDATE_ID}_prompt.md"
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
OUTDOOR_MASTER = ROOT / "production" / "assets" / "outdoor_world_world2d" / "v001" / "workflow_manifest.json"
LAYOUT_DRAFT_ACCEPTANCE = (
    PACKAGE_DIR
    / "02_source_generation"
    / "layout_structure_drafts"
    / "village_layout_structure_draft_v001_acceptance.json"
)
REVIEW_MD = PACKAGE_DIR / "05_review_and_qa" / "true_painted_source_candidate_review.md"

TARGET_SIZE = (1800, 1200)


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read(path: Path) -> str:
    require(path.is_file(), f"missing required file: {path.relative_to(ROOT).as_posix()}")
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(read(path))
    except json.JSONDecodeError as exc:
        fail(f"invalid json in {path.relative_to(ROOT).as_posix()}: {exc}")
    require(isinstance(value, dict), f"{path.relative_to(ROOT).as_posix()} must contain a JSON object")
    return value


def validate_image(path: Path, expected_size: tuple[int, int] | None) -> None:
    require(path.is_file(), f"missing image: {path.relative_to(ROOT).as_posix()}")
    image = Image.open(path)
    if expected_size is not None:
        require(image.size == expected_size, f"{path.relative_to(ROOT).as_posix()} size mismatch: {image.size}")
    require(image.mode in {"RGB", "RGBA"}, f"{path.relative_to(ROOT).as_posix()} must be RGB/RGBA, got {image.mode}")
    if image.mode == "RGBA":
        require(image.getchannel("A").getextrema() == (255, 255), f"{path.relative_to(ROOT).as_posix()} must be opaque")
    rgb = image.convert("RGB")
    ranges = [high - low for low, high in rgb.getextrema()]
    stat = ImageStat.Stat(rgb)
    require(max(ranges) > 90, f"{path.relative_to(ROOT).as_posix()} should have painted value/color range")
    require(sum(stat.var) > 1000, f"{path.relative_to(ROOT).as_posix()} appears too flat")


def validate_metadata() -> None:
    metadata = load_json(METADATA)
    require(metadata.get("candidate_id") == CANDIDATE_ID, "candidate_id mismatch")
    require(
        metadata.get("status") in {"true_painted_source_candidate_pending_human_visual_review", "accepted_for_layer_export"},
        "candidate status mismatch",
    )
    require(metadata.get("candidate_type") == "true_storybook_painted_source_candidate", "candidate_type mismatch")
    if metadata.get("status") == "accepted_for_layer_export":
        require(metadata.get("human_visual_approval") is True, "accepted metadata must record human approval")
        require(metadata.get("layer_export_approved") is True, "accepted metadata must approve layer export")
    else:
        require(metadata.get("human_visual_approval") is False, "pending metadata must keep human_visual_approval=false")
        require(metadata.get("layer_export_approved") is False, "pending metadata must keep layer_export_approved=false")
    for key in ["runtime_replacement", "launch_quality_approved"]:
        require(metadata.get(key) is False, f"metadata must keep {key}=false")
    require(metadata.get("normalized_size") == [1800, 1200], "metadata normalized size mismatch")
    refs = metadata.get("references")
    require(isinstance(refs, dict), "metadata references must be object")
    require(refs.get("outdoor_world_master") == "production/assets/outdoor_world_world2d/v001/workflow_manifest.json", "missing outdoor master reference")
    require(refs.get("village_layout_lock") == "production/assets/regions/village_world2d/v001/01_layout_lock/layout_lock.json", "missing Village layout lock reference")


def validate_workflow_links() -> None:
    workflow = load_json(WORKFLOW)
    true_candidate = workflow.get("true_painted_source_candidate")
    require(isinstance(true_candidate, dict), "workflow missing true_painted_source_candidate")
    require(true_candidate.get("candidate_id") == CANDIDATE_ID, "workflow true candidate id mismatch")
    require(
        true_candidate.get("status") in {"true_painted_source_candidate_pending_human_visual_review", "accepted_for_layer_export"},
        "workflow true candidate status mismatch",
    )
    require(true_candidate.get("image") == "production/assets/regions/village_world2d/v001/02_source_generation/true_source_candidates/village_true_painted_source_candidate_v001.png", "workflow true candidate image path mismatch")
    if true_candidate.get("status") == "accepted_for_layer_export":
        require(true_candidate.get("human_visual_approval") is True, "workflow accepted candidate must record human approval")
        require(true_candidate.get("layer_export_approved") is True, "workflow accepted candidate must approve layer export")
    else:
        require(true_candidate.get("human_visual_approval") is False, "workflow pending candidate must keep human_visual_approval=false")
        require(true_candidate.get("layer_export_approved") is False, "workflow pending candidate must keep layer_export_approved=false")
    require(true_candidate.get("runtime_replacement") is False, "workflow true candidate must keep runtime_replacement=false")
    phase_status = workflow.get("phase_status")
    require(isinstance(phase_status, dict), "workflow phase_status must be object")
    require(
        phase_status.get("03_layer_export")
        in {
            "blocked_until_true_painted_source_human_visual_review",
            "exported_pending_layer_review",
            "semantic_rework_exported_pending_review",
        },
        "layer export phase mismatch",
    )


def validate_blocking_context() -> None:
    outdoor = load_json(OUTDOOR_MASTER)
    require(outdoor.get("runtime_replacement") is False, "Outdoor master must block runtime replacement")
    layout_draft = load_json(LAYOUT_DRAFT_ACCEPTANCE)
    require(layout_draft.get("not_final_painted_source") is True, "layout draft must stay marked not final")
    require(layout_draft.get("do_not_split_layers_from_this_image") is True, "layout draft must stay blocked from splitting")
    prompt = read(PROMPT_FILE)
    for token in ["storybook", "No readable text", "no UI", "no labels", "no characters", "Aoi"]:
        require(token in prompt, f"prompt missing token: {token}")
    review = read(REVIEW_MD)
    for token in [
        CANDIDATE_ID,
        "accepted for layer export",
        "not runtime replacement",
        "1800x1200",
        "Do not replace runtime art",
    ]:
        require(token in review, f"review markdown missing token: {token}")


def main() -> None:
    validate_image(ORIGINAL_IMAGE, None)
    validate_image(NORMALIZED_IMAGE, TARGET_SIZE)
    validate_metadata()
    validate_workflow_links()
    validate_blocking_context()
    print("OK: Village true painted source candidate validates")


if __name__ == "__main__":
    main()
