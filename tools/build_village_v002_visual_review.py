from __future__ import annotations

import json
from pathlib import Path
from typing import Any


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

VISUAL_REVIEW_STATUS = "accepted_for_semantic_layer_export_review"
VISUAL_PHASE = "v002_codex_visual_accepted_for_semantic_layer_export"
ACCEPTANCE_STATUS = "v002_accepted_for_semantic_layer_export_review"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_visual_review() -> None:
    quality = read_json(V002_QUALITY)
    metrics = quality.get("metrics", {})
    review = {
        "review_id": "village_v002_visual_review",
        "reviewed_at": "2026-05-26",
        "status": VISUAL_REVIEW_STATUS,
        "source_image": rel(V002_SOURCE),
        "quality_review": rel(V002_QUALITY),
        "review_contact_sheet": rel(V002_CONTACT),
        "v002_visual_accepted_for_layer_export_review": True,
        "human_visual_approval": False,
        "layer_export_approved": False,
        "runtime_replacement": False,
        "launch_quality_approved": False,
        "acceptance_scope": "Codex visual acceptance for semantic layer export review only; this is not human/art approval.",
        "review_notes": [
            "Codex review accepts v002 for semantic layer export review because the center village detail reaches the old-source quality target while the outer edge bands remain inherited from the world-base crop.",
            "The soft inherited edge is intentional continuity padding for the OutdoorWorld crop and must be checked again in Godot screenshot review before runtime promotion.",
            "Semantic layer export should derive from this exact full-canvas source; do not regenerate independent layer compositions or crop transparent layers.",
            "Godot screenshot review and human/art review remain required before any runtime replacement or launch approval.",
        ],
        "metrics_snapshot": {
            "edge_diff_from_base_crop": metrics.get("edge_diff_from_base_crop"),
            "detail_ratio_vs_old_source": metrics.get("detail_ratio_vs_old_source"),
            "variance_ratio_vs_old_source": metrics.get("variance_ratio_vs_old_source"),
        },
        "next_required_step": "export_v002_semantic_layers_from_exact_source",
    }
    write_json(VISUAL_REVIEW, review)


def update_acceptance() -> None:
    data = read_json(V002_ACCEPTANCE)
    data["status"] = ACCEPTANCE_STATUS
    data["visual_review"] = rel(VISUAL_REVIEW)
    data["human_visual_approval"] = False
    data["layer_export_approved"] = False
    data["runtime_replacement"] = False
    data["launch_quality_approved"] = False
    data["codex_visual_review"] = {
        "status": VISUAL_REVIEW_STATUS,
        "review": rel(VISUAL_REVIEW),
        "not_human_visual_approval": True,
        "v002_visual_accepted_for_layer_export_review": True,
        "next_required_step": "export_v002_semantic_layers_from_exact_source",
    }
    write_json(V002_ACCEPTANCE, data)


def update_workflow() -> None:
    data = read_json(WORKFLOW)
    data["status"] = VISUAL_PHASE
    data["current_phase"] = "02_source_visual_review_v002"
    data["runtime_replacement"] = False
    data["next_art_step"] = "export v002 semantic layers from the exact inherited source before any Godot screenshot review or runtime replacement."
    data["v002_visual_review"] = {
        "status": VISUAL_REVIEW_STATUS,
        "review": rel(VISUAL_REVIEW),
        "source_image": rel(V002_SOURCE),
        "human_visual_approval": False,
        "layer_export_approved": False,
        "runtime_replacement": False,
        "launch_quality_approved": False,
    }
    phase_status = data.setdefault("phase_status", {})
    phase_status["02_source_visual_review_v002"] = VISUAL_REVIEW_STATUS
    phase_status["03_layer_export_v002"] = "accepted_source_pending_v002_layer_export"
    phase_status["04_godot_integration_v002"] = "blocked_until_v002_layer_export_and_godot_screenshot"
    validation = data.setdefault("validation", {})
    validation["v002_visual_review_validator"] = "tools/validate_village_v002_visual_review.py"
    write_json(WORKFLOW, data)


def update_layer_contract() -> None:
    data = read_json(LAYER_CONTRACT)
    source = data.setdefault("source_image", {})
    source["v002_current_file_status"] = VISUAL_PHASE
    source["v002_visual_review"] = rel(VISUAL_REVIEW)
    source["v002_layer_export_status"] = "accepted_source_pending_v002_layer_export"
    source["v002_required_next_step"] = "Export v002 semantic layers from village_painted_source_v002 before Godot screenshot validation."
    source["v002_human_visual_approval"] = False
    source["v002_layer_export_approved"] = False
    data["runtime_replacement"] = False
    write_json(LAYER_CONTRACT, data)


def update_project_manifest() -> None:
    data = read_json(PROJECT_MANIFEST)
    for record in data.get("current_runtime_regions", []):
        if not isinstance(record, dict) or record.get("region_id") != "Region_Village":
            continue
        record["phase"] = VISUAL_PHASE
        record["active_v002_visual_review"] = rel(VISUAL_REVIEW)
        record["runtime_replacement"] = False
        record["launch_quality_approved"] = False
        record["human_visual_approval_required"] = True
        record["next_art_step"] = "Export Village v002 semantic layers, then run Village and OutdoorWorld Godot screenshot review before runtime replacement."
        break
    write_json(PROJECT_MANIFEST, data)


def write_report() -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        f"""# Village v002 Visual Review - 2026-05-26

Status: {VISUAL_REVIEW_STATUS}

## Verdict

`village_painted_source_v002` is accepted for Codex semantic layer export review.

This is not human/art approval. runtime replacement remains blocked, layer export is not final-approved, and launch-quality approval remains false.

## Notes

- Center detail, house/notice/seed-stall readability, road shoulders, grass, and flowers are strong enough for a review-only semantic split.
- The soft inherited edge is intentional world-base continuity padding and must be judged again in Godot screenshots.
- All v002 layers must derive from this exact full-canvas source.

## Next

Export v002 semantic layers into a branch-specific layer package, then review that layer package before any Godot runtime replacement.
""",
        encoding="utf-8",
    )


def main() -> None:
    write_visual_review()
    update_acceptance()
    update_workflow()
    update_layer_contract()
    update_project_manifest()
    write_report()
    print(f"OK: wrote {rel(VISUAL_REVIEW)}")


if __name__ == "__main__":
    main()
