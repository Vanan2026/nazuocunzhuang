from __future__ import annotations

import json
import struct
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production/assets/regions/mountain_hut_world2d/v001"
SOURCE_DIR = PACKAGE_DIR / "02_source_generation"
V002_DIR = SOURCE_DIR / "v002"
V003_DIR = SOURCE_DIR / "v003"
REVIEW_DIR = PACKAGE_DIR / "05_review_and_qa"
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
LAYER_CONTRACT = PACKAGE_DIR / "03_layer_export/layer_contract.json"
PROJECT_MANIFEST = ROOT / "production/assets/project_art_production_manifest_2026-05-19.json"
V002_ACCEPTANCE = V002_DIR / "source_acceptance_v002.json"
VISUAL_REVIEW = REVIEW_DIR / "source_visual_review_v002.json"
V003_BRIEF = V003_DIR / "mountain_hut_repaint_v003_brief.md"
V003_REFERENCE_SHEET = REVIEW_DIR / "mountain_hut_v003_repaint_reference_sheet.png"
V002_REPORT = ROOT / ".codex/reports/mountain_hut_v002_visual_review_2026-05-25.md"

STATUS = "needs_v003_repaint_before_layer_export"
PHASE = "mountain_hut_v002_visual_review_rejected_needs_v003_repaint"
V003_PHASE = "mountain_hut_v003_candidate_ready_for_visual_review"
V004_PHASE = "mountain_hut_v004_candidate_ready_for_visual_review"
V004_LAYER_PHASE = "v004_semantic_layers_exported_pending_review"


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path) -> Any:
    require(path.exists(), f"missing {path.relative_to(ROOT).as_posix()}")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_text(path: Path) -> str:
    require(path.exists(), f"missing {path.relative_to(ROOT).as_posix()}")
    return path.read_text(encoding="utf-8-sig")


def png_size(path: Path) -> tuple[int, int]:
    require(path.exists(), f"missing {path.relative_to(ROOT).as_posix()}")
    with path.open("rb") as handle:
        data = handle.read(24)
    require(data[:8] == b"\x89PNG\r\n\x1a\n", f"not png: {path.relative_to(ROOT).as_posix()}")
    return struct.unpack(">II", data[16:24])


def validate_visual_review() -> None:
    data = read_json(VISUAL_REVIEW)
    require(data.get("review_id") == "mountain_hut_v002_visual_review", "visual review id mismatch")
    require(data.get("status") == STATUS, "visual review status mismatch")
    require(data.get("v002_visual_accepted") is False, "v002 must not be visually accepted")
    require(data.get("layer_export_approved") is False, "visual review must keep layer export blocked")
    require(data.get("runtime_replacement") is False, "visual review must keep runtime replacement blocked")
    require(data.get("launch_quality_approved") is False, "visual review must keep launch approval false")
    reasons = "\n".join(str(item) for item in data.get("rejection_reasons", []))
    for token in [
        "programmatic",
        "accepted Village",
        "tree canopy",
        "roof line",
        "external handoff",
        "dimension",
        "layout",
    ]:
        require(token in reasons, f"visual review rejection reasons missing {token!r}")
    require(data.get("next_required_step") == "produce_v003_full_canvas_repaint", "next required step mismatch")


def validate_v003_handoff() -> None:
    text = read_text(V003_BRIEF)
    for token in [
        "1800x1200",
        "source point `[0, 667]`",
        "registration-perfect layer alignment",
        "single full-canvas painted source",
        "accepted Village source",
        "external handoff",
        "no combat",
        "Do not crop",
    ]:
        require(token in text, f"v003 brief missing {token!r}")
    require(png_size(V003_REFERENCE_SHEET) == (1800, 1400), "v003 reference sheet size mismatch")
    report = read_text(V002_REPORT)
    for token in [STATUS, "v002 rejected", "v003", "runtime replacement remains blocked"]:
        require(token in report, f"visual review report missing {token!r}")


def validate_manifests() -> None:
    workflow = read_json(WORKFLOW)
    require(workflow.get("status") in {PHASE, V003_PHASE, V004_PHASE, V004_LAYER_PHASE}, "workflow status mismatch")
    require(
        workflow.get("current_phase") in {
            "02_source_generation_v003_handoff",
            "02_source_generation_v003_review",
            "02_source_generation_v004_review",
            "03_layer_export_v004_semantic_review",
        },
        "workflow current phase mismatch",
    )
    phase_status = workflow.get("phase_status", {})
    require(phase_status.get("02_source_visual_review_v002") == STATUS, "workflow visual review phase mismatch")
    require(
        phase_status.get("02_source_generation_v003")
        in {
            "handoff_ready_for_external_or_manual_repaint",
            "v003_candidate_ready_for_visual_review",
        },
        "workflow v003 phase mismatch",
    )
    require(
        workflow.get("next_art_step")
        in {
            "produce a v003 full-canvas repaint before layer export or runtime replacement.",
            "visual review the v003 source candidate before any layer export or runtime replacement.",
            "visual review the v004 source candidate before any layer export or runtime replacement.",
            "review v004 semantic layers before any runtime replacement.",
        },
        "workflow next step mismatch",
    )
    v003 = workflow.get("v003_repaint_handoff", {})
    require(v003.get("brief") == "production/assets/regions/mountain_hut_world2d/v001/02_source_generation/v003/mountain_hut_repaint_v003_brief.md", "workflow v003 brief pointer mismatch")
    require(v003.get("reference_sheet") == "production/assets/regions/mountain_hut_world2d/v001/05_review_and_qa/mountain_hut_v003_repaint_reference_sheet.png", "workflow v003 reference pointer mismatch")

    contract = read_json(LAYER_CONTRACT)
    require(
        contract.get("layer_export_status") in {
            "blocked_until_v003_source_acceptance",
            "blocked_until_v003_visual_acceptance",
            "blocked_until_v004_visual_acceptance",
            V004_LAYER_PHASE,
        },
        "layer contract export status mismatch",
    )
    source = contract.get("source_image", {})
    require(
        source.get("current_file_status")
        in {
            "v002_visual_review_rejected",
            "v003_candidate_pending_visual_review",
            "v004_candidate_pending_visual_review",
            "v004_codex_visual_accepted_for_semantic_layer_export",
        },
        "layer contract source status mismatch",
    )
    require(
        source.get("required_next_step")
        in {
            "Produce a v003 full-canvas repaint before layer export.",
            "Visual review the v003 full-canvas source candidate before layer export.",
            "Visual review the v004 full-canvas source candidate before layer export.",
            "Review v004 semantic layer export, then run Godot screenshot validation before runtime replacement.",
        },
        "layer contract next step mismatch",
    )
    require(source.get("v002_visual_review") == "production/assets/regions/mountain_hut_world2d/v001/05_review_and_qa/source_visual_review_v002.json", "layer contract visual review pointer mismatch")
    require(source.get("v003_repaint_brief") == "production/assets/regions/mountain_hut_world2d/v001/02_source_generation/v003/mountain_hut_repaint_v003_brief.md", "layer contract v003 brief pointer mismatch")

    acceptance = read_json(V002_ACCEPTANCE)
    require(acceptance.get("status") == PHASE, "v002 acceptance status mismatch")
    visual = acceptance.get("codex_visual_review", {})
    require(visual.get("status") == STATUS, "v002 acceptance visual review status mismatch")
    require(visual.get("not_human_visual_approval") is True, "v002 acceptance must state this is not approval")

    project = read_json(PROJECT_MANIFEST)
    regions = project.get("current_runtime_regions", [])
    hut = next((item for item in regions if isinstance(item, dict) and item.get("region_id") == "Region_MountainHut"), None)
    require(isinstance(hut, dict), "project manifest missing Region_MountainHut")
    require(hut.get("phase") in {PHASE, V003_PHASE, V004_PHASE, V004_LAYER_PHASE}, "project manifest MountainHut phase mismatch")
    require(hut.get("runtime_replacement") is False, "project manifest must keep runtime_replacement=false")
    require(hut.get("launch_quality_approved") is False, "project manifest must keep launch_quality_approved=false")
    require(hut.get("human_visual_approval_required") is True, "project manifest must keep human review required")
    require(hut.get("active_v002_visual_review") == "production/assets/regions/mountain_hut_world2d/v001/05_review_and_qa/source_visual_review_v002.json", "project manifest visual review pointer mismatch")
    require(hut.get("active_v003_repaint_brief") == "production/assets/regions/mountain_hut_world2d/v001/02_source_generation/v003/mountain_hut_repaint_v003_brief.md", "project manifest v003 brief pointer mismatch")
    if hut.get("phase") == V003_PHASE:
        require(
            hut.get("active_v003_source_candidate")
            == "production/assets/regions/mountain_hut_world2d/v001/02_source_generation/v003/mountain_hut_painted_source_v003.png",
            "project manifest v003 source pointer mismatch",
        )
    if hut.get("phase") == V004_PHASE:
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
    if hut.get("phase") == V004_LAYER_PHASE:
        require(
            hut.get("active_layer_manifest")
            == "production/assets/regions/mountain_hut_world2d/v001/03_layer_export/layer_export_manifest.json",
            "project manifest layer manifest pointer mismatch",
        )
    next_step = str(hut.get("next_art_step", ""))
    require("v003" in next_step or "v004" in next_step, "project manifest next step must point to v003 or v004")


def main() -> None:
    validate_visual_review()
    validate_v003_handoff()
    validate_manifests()
    print("OK: MountainHut v002 visual review and v003 repaint handoff validate")


if __name__ == "__main__":
    main()
