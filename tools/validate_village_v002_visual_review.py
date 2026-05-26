from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production/assets/regions/village_world2d/v001"
V002_DIR = PACKAGE_DIR / "02_source_generation/v002_inherited_world_base_repaint"
V002_SOURCE = V002_DIR / "village_painted_source_v002.png"
V002_ACCEPTANCE = V002_DIR / "source_acceptance_v002.json"
V002_QUALITY = V002_DIR / "source_quality_review_v002.json"
V002_CONTACT = V002_DIR / "village_v002_source_review_contact_sheet.png"
VISUAL_REVIEW = V002_DIR / "source_visual_review_v002.json"
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
LAYER_CONTRACT = PACKAGE_DIR / "03_layer_export/layer_contract.json"
PROJECT_MANIFEST = ROOT / "production/assets/project_art_production_manifest_2026-05-19.json"
REPORT = ROOT / ".codex/reports/village_v002_visual_review_2026-05-26.md"

CANVAS = (1800, 1200)
VISUAL_REVIEW_STATUS = "accepted_for_semantic_layer_export_review"
VISUAL_PHASE = "v002_codex_visual_accepted_for_semantic_layer_export"
LAYER_STATUS = "v002_semantic_layers_exported_pending_review"
ACCEPTANCE_STATUS = "v002_accepted_for_semantic_layer_export_review"


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
    return path.read_text(encoding="utf-8-sig")


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(read(path))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {rel(path)}: {exc}")
    require(isinstance(data, dict), f"{rel(path)} must contain a JSON object")
    return data


def as_dict(value: Any, label: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"{label} must be an object")
    return value


def validate_source_artifacts() -> None:
    image = Image.open(V002_SOURCE).convert("RGBA")
    require(image.size == CANVAS, f"v002 source canvas mismatch: {image.size}")
    require(image.getchannel("A").getextrema() == (255, 255), "v002 source must be opaque")
    contact = Image.open(V002_CONTACT).convert("RGB")
    require(contact.size == (2400, 1500), f"v002 contact sheet size mismatch: {contact.size}")
    quality = load_json(V002_QUALITY)
    require(quality.get("status") == "v002_inherited_crop_candidate_ready_for_visual_review", "quality review status mismatch")
    metrics = as_dict(quality.get("metrics"), "quality.metrics")
    require(float(metrics.get("edge_diff_from_base_crop", 999.0)) <= 1.0, "v002 edge bands must stay inherited from base crop")
    require(float(metrics.get("detail_ratio_vs_old_source", 0.0)) >= 1.0, "v002 should meet old-source detail target")


def validate_visual_review_record() -> None:
    review = load_json(VISUAL_REVIEW)
    require(review.get("review_id") == "village_v002_visual_review", "visual review id mismatch")
    require(review.get("status") == VISUAL_REVIEW_STATUS, "visual review status mismatch")
    require(review.get("v002_visual_accepted_for_layer_export_review") is True, "v002 must be accepted for semantic layer export review")
    require(review.get("source_image") == rel(V002_SOURCE), "visual review source path mismatch")
    require(review.get("quality_review") == rel(V002_QUALITY), "visual review quality path mismatch")
    require(review.get("review_contact_sheet") == rel(V002_CONTACT), "visual review contact sheet path mismatch")
    for key in ["human_visual_approval", "layer_export_approved", "runtime_replacement", "launch_quality_approved"]:
        require(review.get(key) is False, f"visual review must keep {key}=false")
    notes = "\n".join(str(item) for item in review.get("review_notes", []))
    for token in ["Codex", "soft inherited edge", "semantic layer export", "Godot screenshot"]:
        require(token in notes, f"visual review notes missing {token!r}")
    require("human" in str(review.get("acceptance_scope", "")).lower(), "visual review scope must state it is not human approval")

    report = read(REPORT)
    for token in [VISUAL_REVIEW_STATUS, "not human/art approval", "runtime replacement remains blocked"]:
        require(token in report, f"visual review report missing {token!r}")


def validate_acceptance_workflow_contract_project() -> None:
    acceptance = load_json(V002_ACCEPTANCE)
    require(acceptance.get("candidate_id") == "village_painted_source_v002", "acceptance candidate id mismatch")
    require(acceptance.get("status") == ACCEPTANCE_STATUS, "acceptance status mismatch")
    require(acceptance.get("visual_review") == rel(VISUAL_REVIEW), "acceptance visual review pointer mismatch")
    visual = as_dict(acceptance.get("codex_visual_review"), "acceptance.codex_visual_review")
    require(visual.get("status") == VISUAL_REVIEW_STATUS, "acceptance visual status mismatch")
    require(visual.get("not_human_visual_approval") is True, "acceptance must mark Codex review as not human approval")
    for key in ["human_visual_approval", "layer_export_approved", "runtime_replacement", "launch_quality_approved"]:
        require(acceptance.get(key) is False, f"acceptance must keep {key}=false")

    workflow = load_json(WORKFLOW)
    require(workflow.get("status") in {VISUAL_PHASE, LAYER_STATUS}, "workflow v002 status mismatch")
    require(
        workflow.get("current_phase") in {"02_source_visual_review_v002", "03_layer_export_v002_semantic_review"},
        "workflow current phase mismatch",
    )
    require(workflow.get("runtime_replacement") is False, "workflow must keep runtime_replacement=false")
    workflow_review = as_dict(workflow.get("v002_visual_review"), "workflow.v002_visual_review")
    require(workflow_review.get("status") == VISUAL_REVIEW_STATUS, "workflow visual review status mismatch")
    require(workflow_review.get("review") == rel(VISUAL_REVIEW), "workflow visual review pointer mismatch")
    require(workflow_review.get("human_visual_approval") is False, "workflow must not claim human approval")
    phase_status = as_dict(workflow.get("phase_status"), "workflow.phase_status")
    require(phase_status.get("02_source_visual_review_v002") == VISUAL_REVIEW_STATUS, "workflow visual phase status mismatch")
    require(
        phase_status.get("03_layer_export_v002")
        in {"accepted_source_pending_v002_layer_export", LAYER_STATUS},
        "workflow v002 layer export phase mismatch",
    )
    require(
        phase_status.get("04_godot_integration_v002")
        in {
            "blocked_until_v002_layer_export_and_godot_screenshot",
            "blocked_until_v002_semantic_layer_review_and_godot_screenshot",
        },
        "workflow v002 Godot gate mismatch",
    )

    contract = load_json(LAYER_CONTRACT)
    source = as_dict(contract.get("source_image"), "layer_contract.source_image")
    require(source.get("v002_visual_review") == rel(VISUAL_REVIEW), "layer contract visual review pointer mismatch")
    require(
        source.get("v002_current_file_status")
        in {VISUAL_PHASE, "v002_codex_visual_accepted_for_semantic_layer_export_review", LAYER_STATUS},
        "layer contract v002 current status mismatch",
    )
    require(
        source.get("v002_layer_export_status") in {"accepted_source_pending_v002_layer_export", LAYER_STATUS},
        "layer contract v002 layer status mismatch",
    )
    require(contract.get("runtime_replacement") is False, "layer contract must keep runtime_replacement=false")

    project = load_json(PROJECT_MANIFEST)
    regions = project.get("current_runtime_regions")
    require(isinstance(regions, list), "project regions must be a list")
    village = next((item for item in regions if isinstance(item, dict) and item.get("region_id") == "Region_Village"), None)
    require(isinstance(village, dict), "project manifest missing Region_Village")
    require(village.get("phase") in {VISUAL_PHASE, LAYER_STATUS}, "project Village v002 phase mismatch")
    require(village.get("active_v002_visual_review") == rel(VISUAL_REVIEW), "project visual review pointer mismatch")
    require(village.get("runtime_replacement") is False, "project Village must keep runtime_replacement=false")
    require(village.get("launch_quality_approved") is False, "project Village must keep launch approval false")
    require(village.get("human_visual_approval_required") is True, "project Village must require human review")


def main() -> None:
    validate_source_artifacts()
    validate_visual_review_record()
    validate_acceptance_workflow_contract_project()
    print("OK: Village v002 Codex visual review validates")


if __name__ == "__main__":
    main()
