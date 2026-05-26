from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageFilter, ImageStat


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production" / "assets" / "regions" / "village_world2d" / "v001"
V002_DIR = PACKAGE_DIR / "02_source_generation" / "v002_inherited_world_base_repaint"
V002_SOURCE = V002_DIR / "village_painted_source_v002.png"
V002_ACCEPTANCE = V002_DIR / "source_acceptance_v002.json"
V002_QUALITY = V002_DIR / "source_quality_review_v002.json"
V002_CONTACT = V002_DIR / "village_v002_source_review_contact_sheet.png"
HANDOFF_JSON = V002_DIR / "village_inherited_repaint_handoff_v002.json"
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
PROJECT_MANIFEST = ROOT / "production" / "assets" / "project_art_production_manifest_2026-05-19.json"
LAYER_CONTRACT = PACKAGE_DIR / "03_layer_export" / "layer_contract.json"
REPORT = ROOT / ".codex" / "reports" / "village_v002_inherited_source_candidate_review_2026-05-26.md"
GENERATOR = ROOT / "tools" / "generate_village_painted_source_v002.py"
BASE_CROP = ROOT / "production" / "assets" / "outdoor_world_world2d" / "v001" / "02_world_base_no_foreground" / "region_base_crops" / "village_base_no_foreground.png"
OLD_SOURCE = PACKAGE_DIR / "02_source_generation" / "village_painted_source.png"

CANVAS = (1800, 1200)
CONTACT_SIZE = (2400, 1500)
STATUS = "v002_inherited_crop_candidate_ready_for_visual_review"
VISUAL_STATUS = "v002_accepted_for_semantic_layer_export_review"
LAYER_STATUS = "v002_semantic_layers_exported_pending_review"
CANDIDATE_ID = "village_painted_source_v002"
MAX_EDGE_DIFF_FROM_BASE = 10.0
MIN_DIFF_FROM_BASE = 22.0
MIN_DIFF_FROM_OLD = 9.0
MIN_DETAIL_RATIO_VS_OLD = 0.58
MIN_VARIANCE_RATIO_VS_OLD = 0.42


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


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(read(path))
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


def load_image(path: Path, label: str) -> Image.Image:
    require(path.is_file(), f"missing {label}: {rel(path)}")
    image = Image.open(path).convert("RGBA")
    require(image.size == CANVAS, f"{label} size mismatch: {image.size}")
    return image


def edge_detail_score(image: Image.Image) -> float:
    gray = image.convert("L")
    edges = ImageChops.difference(gray, gray.filter(ImageFilter.GaussianBlur(2.2)))
    return float(sum(ImageStat.Stat(edges).mean))


def gray_variance(image: Image.Image) -> float:
    return float(ImageStat.Stat(image.convert("L")).var[0])


def mean_diff(left: Image.Image, right: Image.Image) -> float:
    diff = ImageChops.difference(left.convert("RGB"), right.convert("RGB"))
    return float(sum(ImageStat.Stat(diff).mean) / 3.0)


def edge_band(image: Image.Image) -> Image.Image:
    rgb = image.convert("RGB")
    band = Image.new("RGB", (CANVAS[0], 240), (0, 0, 0))
    strips = [
        rgb.crop((0, 0, CANVAS[0], 60)),
        rgb.crop((0, CANVAS[1] - 60, CANVAS[0], CANVAS[1])),
        rgb.crop((0, 60, 60, CANVAS[1] - 60)).resize((CANVAS[0] // 2, 60), Image.Resampling.LANCZOS),
        rgb.crop((CANVAS[0] - 60, 60, CANVAS[0], CANVAS[1] - 60)).resize((CANVAS[0] // 2, 60), Image.Resampling.LANCZOS),
    ]
    band.paste(strips[0], (0, 0))
    band.paste(strips[1], (0, 60))
    band.paste(strips[2], (0, 140))
    band.paste(strips[3], (CANVAS[0] // 2, 140))
    return band


def validate_source_metrics() -> dict[str, float]:
    candidate = load_image(V002_SOURCE, "v002 source candidate")
    base = load_image(BASE_CROP, "inherited base crop")
    old = load_image(OLD_SOURCE, "old Village quality reference")
    require(candidate.getchannel("A").getextrema() == (255, 255), "v002 source must be fully opaque")

    edge_diff = mean_diff(edge_band(candidate), edge_band(base))
    diff_from_base = mean_diff(candidate, base)
    diff_from_old = mean_diff(candidate, old)
    detail_ratio = edge_detail_score(candidate) / max(edge_detail_score(old), 0.0001)
    variance_ratio = gray_variance(candidate) / max(gray_variance(old), 0.0001)
    center = candidate.crop((360, 210, 1440, 980))
    center_base = base.crop((360, 210, 1440, 980))
    center_old = old.crop((360, 210, 1440, 980))
    center_diff_from_base = mean_diff(center, center_base)
    center_diff_from_old = mean_diff(center, center_old)

    require(edge_diff <= MAX_EDGE_DIFF_FROM_BASE, f"v002 edge bands drift from inherited base crop: {edge_diff:.4f}")
    require(diff_from_base >= MIN_DIFF_FROM_BASE, f"v002 is too close to flat inherited base crop: {diff_from_base:.4f}")
    require(diff_from_old >= MIN_DIFF_FROM_OLD, f"v002 is too close to old isolated Village source: {diff_from_old:.4f}")
    require(detail_ratio >= MIN_DETAIL_RATIO_VS_OLD, f"v002 detail ratio too low vs old source: {detail_ratio:.4f}")
    require(variance_ratio >= MIN_VARIANCE_RATIO_VS_OLD, f"v002 variance ratio too low vs old source: {variance_ratio:.4f}")
    require(center_diff_from_base >= diff_from_base * 1.10, "v002 center should carry more repaint detail than edge bands")
    require(center_diff_from_old < center_diff_from_base, "v002 center should use old source as quality reference")

    return {
        "edge_diff_from_base_crop": edge_diff,
        "mean_diff_from_base_crop": diff_from_base,
        "mean_diff_from_old_source": diff_from_old,
        "detail_ratio_vs_old_source": detail_ratio,
        "variance_ratio_vs_old_source": variance_ratio,
        "center_diff_from_base_crop": center_diff_from_base,
        "center_diff_from_old_source": center_diff_from_old,
    }


def validate_acceptance_and_quality(metrics: dict[str, float]) -> None:
    acceptance = read_json(V002_ACCEPTANCE)
    require(acceptance.get("candidate_id") == CANDIDATE_ID, "acceptance candidate id mismatch")
    require(acceptance.get("status") in {STATUS, VISUAL_STATUS}, "acceptance status mismatch")
    require(acceptance.get("source_image") == rel(V002_SOURCE), "acceptance source path mismatch")
    require(acceptance.get("inherits_from_world_base_crop") == rel(BASE_CROP), "acceptance inherited crop path mismatch")
    require(acceptance.get("old_source_policy") == "quality_reference_only", "acceptance old source policy mismatch")
    for key in ["human_visual_approval", "layer_export_approved", "runtime_replacement", "launch_quality_approved"]:
        require(acceptance.get(key) is False, f"acceptance must keep {key}=false")

    quality = read_json(V002_QUALITY)
    require(quality.get("review_id") == "village_v002_inherited_source_quality_review", "quality review id mismatch")
    require(quality.get("status") == STATUS, "quality review status mismatch")
    require(quality.get("source_candidate") == rel(V002_SOURCE), "quality source path mismatch")
    quality_metrics = as_dict(quality.get("metrics"), "quality.metrics")
    for key, expected in metrics.items():
        actual = float(quality_metrics.get(key, -999.0))
        require(math.isclose(actual, expected, rel_tol=0.03, abs_tol=0.08), f"quality metric {key} mismatch")
    flags = as_dict(quality.get("hard_approval_flags"), "quality.hard_approval_flags")
    for key in ["human_visual_approval", "layer_export_approved", "runtime_replacement", "launch_quality_approved"]:
        require(flags.get(key) is False, f"quality flags must keep {key}=false")


def validate_links() -> None:
    handoff = read_json(HANDOFF_JSON)
    require(handoff.get("handoff_id") == "village_inherited_world_base_repaint_v002", "handoff id mismatch")
    output_contract = as_dict(handoff.get("output_contract"), "handoff.output_contract")
    require(output_contract.get("target_source_id") == CANDIDATE_ID, "handoff target source mismatch")

    workflow = read_json(WORKFLOW)
    block = as_dict(workflow.get("v002_inherited_source_candidate"), "workflow.v002_inherited_source_candidate")
    require(block.get("candidate_id") == CANDIDATE_ID, "workflow v002 candidate id mismatch")
    require(block.get("status") == STATUS, "workflow v002 candidate status mismatch")
    require(block.get("image") == rel(V002_SOURCE), "workflow v002 source path mismatch")
    require(block.get("quality_review") == rel(V002_QUALITY), "workflow v002 quality path mismatch")
    require(block.get("inherits_from_world_base_crop") == rel(BASE_CROP), "workflow v002 inherited crop mismatch")
    require(block.get("old_source_policy") == "quality_reference_only", "workflow v002 old source policy mismatch")
    for key in ["human_visual_approval", "layer_export_approved", "runtime_replacement", "launch_quality_approved"]:
        require(block.get(key) is False, f"workflow v002 must keep {key}=false")
    phase_status = as_dict(workflow.get("phase_status"), "workflow.phase_status")
    require(phase_status.get("02_source_generation_v002_inherited") == STATUS, "workflow v002 phase status mismatch")
    require(
        phase_status.get("03_layer_export_v002")
        in {
            "blocked_until_v002_visual_acceptance",
            "accepted_source_pending_v002_layer_export",
            LAYER_STATUS,
        },
        "workflow v002 layer export status mismatch",
    )

    contract = read_json(LAYER_CONTRACT)
    source = as_dict(contract.get("source_image"), "layer_contract.source_image")
    require(source.get("v002_candidate") == rel(V002_SOURCE), "layer contract v002 source path mismatch")
    require(source.get("old_source_policy_for_v002") == "quality_reference_only", "layer contract v002 old source policy mismatch")
    require(
        source.get("v002_layer_export_status")
        in {
            "blocked_until_v002_visual_acceptance",
            "accepted_source_pending_v002_layer_export",
            LAYER_STATUS,
        },
        "layer contract v2 export status mismatch",
    )
    require(contract.get("runtime_replacement") is False, "layer contract must keep runtime_replacement=false")

    project = read_json(PROJECT_MANIFEST)
    regions = as_list(project.get("current_runtime_regions"), "project.current_runtime_regions")
    village = None
    for record in regions:
        item = as_dict(record, "project region")
        if item.get("region_id") == "Region_Village":
            village = item
            break
    require(village is not None, "project manifest missing Region_Village")
    assert village is not None
    require(village.get("active_v002_source_candidate") == rel(V002_SOURCE), "project manifest v002 source path mismatch")
    require(village.get("active_v002_quality_review") == rel(V002_QUALITY), "project manifest v002 quality path mismatch")
    require(village.get("runtime_replacement") is False, "project Village must keep runtime_replacement=false")
    require(village.get("launch_quality_approved") is False, "project Village must keep launch_quality_approved=false")


def validate_artifacts_and_generator() -> None:
    contact = Image.open(V002_CONTACT).convert("RGB")
    require(contact.size == CONTACT_SIZE, f"contact sheet size mismatch: {contact.size}")
    require(sum(ImageStat.Stat(contact).var) > 500.0, "contact sheet appears blank")
    report = read(REPORT)
    for token in [CANDIDATE_ID, STATUS, "not human/art approval", "runtime replacement remains blocked"]:
        require(token in report, f"report missing token: {token}")
    generator = read(GENERATOR)
    for token in ["BASE_CROP", "OLD_SOURCE", "preserve_edges_from_base", "quality reference only"]:
        require(token in generator, f"generator missing token: {token}")


def main() -> None:
    metrics = validate_source_metrics()
    validate_acceptance_and_quality(metrics)
    validate_links()
    validate_artifacts_and_generator()
    print("OK: Village v002 inherited source candidate validates")


if __name__ == "__main__":
    main()
