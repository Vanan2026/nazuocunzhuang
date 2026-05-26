from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageStat


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production/assets/regions/mountain_hut_world2d/v001"
SOURCE_DIR = PACKAGE_DIR / "02_source_generation"
REVIEW_DIR = PACKAGE_DIR / "05_review_and_qa"
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
LAYER_CONTRACT = PACKAGE_DIR / "03_layer_export/layer_contract.json"
ACCEPTANCE = SOURCE_DIR / "source_acceptance.json"
V002_SOURCE = SOURCE_DIR / "v002/mountain_hut_painted_source_v002.png"
V002_QUALITY = REVIEW_DIR / "source_quality_review_v002.json"
SOURCE_REVIEW = REVIEW_DIR / "source_candidate_review.md"
REVIEW_GATE = REVIEW_DIR / "review_gate.md"
QUALITY_JSON = REVIEW_DIR / "source_quality_review_v001.json"
REFERENCE_BOARD = REVIEW_DIR / "mountain_hut_repaint_v002_reference_board.png"
REPAINT_BRIEF = SOURCE_DIR / "mountain_hut_repaint_v002_brief.md"
PROJECT_MANIFEST = ROOT / "production/assets/project_art_production_manifest_2026-05-19.json"
BUILDER = ROOT / "tools/build_mountain_hut_source_quality_review.py"
STATUS = "needs_repaint_before_layer_export"
V002_VISUAL_REVIEW_PHASE = "mountain_hut_v002_visual_review_rejected_needs_v003_repaint"
V003_PHASE = "mountain_hut_v003_candidate_ready_for_visual_review"
V004_PHASE = "mountain_hut_v004_candidate_ready_for_visual_review"
V004_LAYER_PHASE = "v004_semantic_layers_exported_pending_review"
CANVAS = (1800, 1200)
BOARD_SIZE = (1800, 1500)


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
    require(isinstance(value, dict), f"{rel(path)} must be a JSON object")
    return value


def validate_image(path: Path, expected_size: tuple[int, int], label: str) -> None:
    require(path.is_file(), f"missing image: {rel(path)}")
    image = Image.open(path).convert("RGB")
    require(image.size == expected_size, f"{label} size mismatch: {image.size}")
    stat = ImageStat.Stat(image)
    require(sum(stat.var) > 500, f"{label} appears blank or too flat")


def require_false_flags(record: dict[str, Any], label: str) -> None:
    for key in ["human_visual_approval", "layer_export_approved", "runtime_replacement", "launch_quality_approved"]:
        require(record.get(key) is False, f"{label} must keep {key}=false")


def validate_quality_json() -> dict[str, Any]:
    data = load_json(QUALITY_JSON)
    require(data.get("status") == STATUS, "quality review status mismatch")
    require(data.get("source_candidate") == "production/assets/regions/mountain_hut_world2d/v001/02_source_generation/mountain_hut_painted_source.png", "quality source candidate mismatch")
    require(data.get("quality_reference_source") == "production/assets/regions/village_world2d/v001/02_source_generation/village_painted_source.png", "quality reference source mismatch")
    require(data.get("reference_board") == rel(REFERENCE_BOARD), "quality reference board mismatch")
    require(data.get("repaint_brief") == rel(REPAINT_BRIEF), "quality repaint brief mismatch")
    metrics = data.get("metrics")
    require(isinstance(metrics, dict), "quality metrics must be an object")
    detail_ratio = float(metrics.get("detail_ratio", 0.0))
    target_ratio = float(metrics.get("minimum_detail_ratio_for_repaint_ready", 0.0))
    require(detail_ratio > 0.0, "detail ratio must be positive")
    require(target_ratio >= 0.65, "quality gate target ratio too low")
    require(detail_ratio < target_ratio, "current candidate should remain below repaint-readiness target")
    require(metrics.get("seam_color_precheck_passed") is True, "seam color precheck should remain a useful preserved improvement")
    require(float(metrics.get("seam_edge_average_channel_delta", 999.0)) <= float(metrics.get("maximum_preferred_seam_delta_for_precheck", 0.0)), "seam delta should match the recorded color precheck")
    flags = data.get("hard_approval_flags")
    require(isinstance(flags, dict), "quality review must record hard approval flags")
    require_false_flags(flags, "quality review hard flags")
    findings = data.get("blocking_findings")
    require(isinstance(findings, list) and len(findings) >= 3, "quality review must list blocking findings")
    return data


def validate_reference_board_and_brief() -> None:
    validate_image(REFERENCE_BOARD, BOARD_SIZE, "reference board")
    text = read(REPAINT_BRIEF)
    normalized = text.lower()
    for token in [
        "v002_repaint_required_before_layer_export",
        "1800x1200",
        "west seam",
        "registration-perfect layer alignment",
        "natural painted variation",
        "do not make independent runtime layers",
        "must avoid",
        "combat",
        "acceptance before layer export",
    ]:
        require(token in normalized, f"repaint brief missing token: {token}")


def validate_package_records() -> None:
    acceptance = load_json(ACCEPTANCE)
    require_false_flags(acceptance, "source acceptance")
    quality = acceptance.get("codex_source_quality_review")
    require(isinstance(quality, dict), "acceptance missing codex_source_quality_review")
    require(quality.get("status") == STATUS, "acceptance quality status mismatch")
    require(quality.get("review_record") == rel(QUALITY_JSON), "acceptance quality review path mismatch")
    require(quality.get("reference_board") == rel(REFERENCE_BOARD), "acceptance reference board path mismatch")
    require(quality.get("repaint_brief") == rel(REPAINT_BRIEF), "acceptance repaint brief path mismatch")
    require(quality.get("not_human_visual_approval") is True, "quality gate cannot be human approval")

    workflow = load_json(WORKFLOW)
    require(workflow.get("runtime_replacement") is False, "workflow must keep runtime_replacement=false")
    require(workflow.get("launch_quality_approved") is False, "workflow must keep launch_quality_approved=false")
    validation = workflow.get("validation")
    require(isinstance(validation, dict), "workflow validation must be an object")
    require(validation.get("source_quality_gate") == "tools/validate_mountain_hut_source_quality_gate.py", "workflow missing source quality gate")
    phase = workflow.get("phase_status")
    require(isinstance(phase, dict), "workflow phase_status must be an object")
    require(
        phase.get("03_layer_export")
        in {
            "blocked_until_source_acceptance",
            "blocked_until_v003_visual_acceptance",
            "blocked_until_v004_visual_acceptance",
            V004_LAYER_PHASE,
        },
        "workflow must keep layer export blocked",
    )
    require(phase.get("02_source_quality_review") == STATUS, "workflow quality phase mismatch")
    source = workflow.get("source_candidate")
    require(isinstance(source, dict), "workflow missing source_candidate")
    require_false_flags(source, "workflow source_candidate")
    require(source.get("quality_review_status") == STATUS, "workflow source quality status mismatch")
    require(source.get("quality_review_record") == rel(QUALITY_JSON), "workflow source quality path mismatch")
    require(source.get("repaint_reference_board") == rel(REFERENCE_BOARD), "workflow source board path mismatch")
    require(source.get("v002_repaint_brief") == rel(REPAINT_BRIEF), "workflow source repaint brief path mismatch")

    contract = load_json(LAYER_CONTRACT)
    source_image = contract.get("source_image")
    require(isinstance(source_image, dict), "layer contract missing source_image")
    require(source_image.get("quality_review_status") == STATUS, "layer contract quality status mismatch")
    require(source_image.get("quality_review_record") == rel(QUALITY_JSON), "layer contract quality path mismatch")
    require(source_image.get("v002_repaint_brief") == rel(REPAINT_BRIEF), "layer contract repaint brief path mismatch")
    require(source_image.get("human_visual_approval") is False, "layer contract must keep human approval false")
    require(source_image.get("layer_export_approved") is False, "layer contract must keep layer export approval false")
    require(
        contract.get("layer_export_status") in {
            "blocked_until_v002_source_quality_acceptance",
            "blocked_until_v002_human_art_acceptance",
            "blocked_until_v003_source_acceptance",
            "blocked_until_v003_visual_acceptance",
            "blocked_until_v004_visual_acceptance",
            V004_LAYER_PHASE,
        },
        "layer export status must keep MountainHut blocked after source-quality review",
    )
    require(contract.get("runtime_replacement") is False, "layer contract must keep runtime_replacement=false")


def validate_project_manifest() -> None:
    manifest = load_json(PROJECT_MANIFEST)
    regions = manifest.get("current_runtime_regions")
    require(isinstance(regions, list), "project manifest current_runtime_regions must be a list")
    hut = next((entry for entry in regions if isinstance(entry, dict) and entry.get("region_id") == "Region_MountainHut"), None)
    require(isinstance(hut, dict), "project manifest missing Region_MountainHut")
    phase = hut.get("phase")
    require(
        phase in {
            "mountain_hut_source_candidate_needs_repaint",
            "mountain_hut_v002_candidate_ready_for_human_art_review",
            V002_VISUAL_REVIEW_PHASE,
            V003_PHASE,
            V004_PHASE,
            V004_LAYER_PHASE,
        },
        "project manifest MountainHut phase must record repaint need, v002 review-ready state, v003 handoff state, or v003 candidate state",
    )
    require(hut.get("runtime_replacement") is False, "project manifest MountainHut must keep runtime_replacement=false")
    require(hut.get("launch_quality_approved") is False, "project manifest MountainHut must keep launch_quality_approved=false")
    require(hut.get("human_visual_approval_required") is True, "project manifest MountainHut must require human review")
    if phase == "mountain_hut_source_candidate_needs_repaint":
        require(hut.get("active_source_quality_review") == rel(QUALITY_JSON), "project manifest quality review pointer mismatch")
        require(hut.get("active_repaint_reference_board") == rel(REFERENCE_BOARD), "project manifest board pointer mismatch")
        require(hut.get("active_repaint_brief") == rel(REPAINT_BRIEF), "project manifest brief pointer mismatch")
        require("v002 repaint" in str(hut.get("next_art_step", "")), "project manifest next_art_step should point to v002 repaint")
    elif phase == "mountain_hut_v002_candidate_ready_for_human_art_review":
        require(hut.get("active_v002_source_candidate") == rel(V002_SOURCE), "project manifest v002 source pointer mismatch")
        require(hut.get("active_v002_quality_review") == rel(V002_QUALITY), "project manifest v002 quality pointer mismatch")
        require("human/art review" in str(hut.get("next_art_step", "")), "project manifest next_art_step should point to v002 human/art review")
    elif phase == V002_VISUAL_REVIEW_PHASE:
        require(hut.get("active_v002_source_candidate") == rel(V002_SOURCE), "project manifest v002 source pointer mismatch")
        require(hut.get("active_v002_quality_review") == rel(V002_QUALITY), "project manifest v002 quality pointer mismatch")
        require(
            hut.get("active_v002_visual_review")
            == "production/assets/regions/mountain_hut_world2d/v001/05_review_and_qa/source_visual_review_v002.json",
            "project manifest v002 visual review pointer mismatch",
        )
        require(
            hut.get("active_v003_repaint_brief")
            == "production/assets/regions/mountain_hut_world2d/v001/02_source_generation/v003/mountain_hut_repaint_v003_brief.md",
            "project manifest v003 brief pointer mismatch",
        )
        require("v003" in str(hut.get("next_art_step", "")), "project manifest next_art_step should point to v003 repaint")
    elif phase == V003_PHASE:
        require(hut.get("active_v002_source_candidate") == rel(V002_SOURCE), "project manifest v002 source pointer mismatch")
        require(hut.get("active_v002_quality_review") == rel(V002_QUALITY), "project manifest v002 quality pointer mismatch")
        require(
            hut.get("active_v003_source_candidate")
            == "production/assets/regions/mountain_hut_world2d/v001/02_source_generation/v003/mountain_hut_painted_source_v003.png",
            "project manifest v003 source pointer mismatch",
        )
        require("visual review" in str(hut.get("next_art_step", "")), "project manifest next_art_step should point to v003 visual review")
    elif phase == V004_PHASE:
        require(
            hut.get("active_v003_visual_review")
            == "production/assets/regions/mountain_hut_world2d/v001/05_review_and_qa/source_visual_review_v003.json",
            "project manifest v003 visual review pointer mismatch",
        )
        require(
            hut.get("active_v004_source_candidate")
            == "production/assets/regions/mountain_hut_world2d/v001/02_source_generation/v004/mountain_hut_painted_source_v004.png",
            "project manifest v004 source pointer mismatch",
        )
        require("visual review" in str(hut.get("next_art_step", "")), "project manifest next_art_step should point to v004 visual review")
    else:
        require(
            hut.get("active_v004_visual_review")
            == "production/assets/regions/mountain_hut_world2d/v001/05_review_and_qa/source_visual_review_v004.json",
            "project manifest v004 visual review pointer mismatch",
        )
        require(
            hut.get("active_layer_manifest")
            == "production/assets/regions/mountain_hut_world2d/v001/03_layer_export/layer_export_manifest.json",
            "project manifest v004 layer manifest pointer mismatch",
        )
        require("semantic layers" in str(hut.get("next_art_step", "")), "project manifest next_art_step should point to semantic layer review")


def validate_review_docs() -> None:
    report = read(ROOT / ".codex/reports/mountain_hut_source_quality_review_2026-05-24.md")
    for token in [STATUS, "Detail ratio", "Do not export runtime layers"]:
        require(token in report, f"quality report missing token: {token}")
    review = read(SOURCE_REVIEW)
    for token in ["Source Quality Gate", STATUS, rel(QUALITY_JSON), rel(REFERENCE_BOARD), rel(REPAINT_BRIEF)]:
        require(token in review, f"source review missing token: {token}")
    gate = read(REVIEW_GATE)
    for token in ["Source Quality Gate Extension", STATUS, "not enough to export layers", "Runtime layers still must derive"]:
        require(token in gate, f"review gate missing token: {token}")


def validate_builder_contract() -> None:
    text = read(BUILDER)
    for token in ["edge_detail_score", "mountain_hut_repaint_v002_reference_board.png", "source_quality_review_v001.json", "mountain_hut_source_candidate_needs_repaint"]:
        require(token in text, f"builder missing token: {token}")


def main() -> None:
    validate_image(PACKAGE_DIR / "02_source_generation/mountain_hut_painted_source.png", CANVAS, "MountainHut source")
    validate_quality_json()
    validate_reference_board_and_brief()
    validate_package_records()
    validate_project_manifest()
    validate_review_docs()
    validate_builder_contract()
    print("OK: MountainHut source quality gate validates repaint-blocked state")


if __name__ == "__main__":
    main()
