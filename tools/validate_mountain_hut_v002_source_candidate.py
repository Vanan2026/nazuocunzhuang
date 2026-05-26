from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageFilter, ImageStat


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production/assets/regions/mountain_hut_world2d/v001"
SOURCE_DIR = PACKAGE_DIR / "02_source_generation"
V002_DIR = SOURCE_DIR / "v002"
REVIEW_DIR = PACKAGE_DIR / "05_review_and_qa"
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
LAYER_CONTRACT = PACKAGE_DIR / "03_layer_export/layer_contract.json"
PROJECT_MANIFEST = ROOT / "production/assets/project_art_production_manifest_2026-05-19.json"
LAYOUT_LOCK = PACKAGE_DIR / "01_layout_lock/layout_lock.json"
VILLAGE_SOURCE = ROOT / "production/assets/regions/village_world2d/v001/02_source_generation/village_painted_source.png"
V001_SOURCE = SOURCE_DIR / "mountain_hut_painted_source.png"
V002_SOURCE = V002_DIR / "mountain_hut_painted_source_v002.png"
V002_OVERLAY = REVIEW_DIR / "mountain_hut_painted_source_review_overlay_v002.png"
V002_CONTACT = REVIEW_DIR / "mountain_hut_v002_review_contact_sheet.png"
V002_QUALITY = REVIEW_DIR / "source_quality_review_v002.json"
V002_ACCEPTANCE = V002_DIR / "source_acceptance_v002.json"
V002_REPORT = ROOT / ".codex/reports/mountain_hut_v002_source_candidate_review_2026-05-25.md"
GENERATOR = ROOT / "tools/generate_mountain_hut_painted_source_v002.py"

CANVAS = (1800, 1200)
CONTACT_SIZE = (1800, 1500)
CANDIDATE_ID = "mountain_hut_painted_source_candidate_v002"
STATUS = "v002_candidate_ready_for_human_art_review"
VISUAL_REVIEW_STATUS = "needs_v003_repaint_before_layer_export"
VISUAL_REVIEW_PHASE = "mountain_hut_v002_visual_review_rejected_needs_v003_repaint"
V003_PHASE = "mountain_hut_v003_candidate_ready_for_visual_review"
MIN_DETAIL_RATIO = 0.68
MIN_VARIANCE_RATIO = 0.62
MAX_SEAM_DELTA = 24.0
MAX_DETAIL_RATIO = 1.45
REQUIRED_ANCHORS = [
    "MountainHutExterior",
    "HutDoor",
    "HutApproachPath",
    "VillageConnectorPath",
]


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


def load_image(path: Path, size: tuple[int, int], label: str, *, opaque: bool = True) -> Image.Image:
    require(path.is_file(), f"missing image: {rel(path)}")
    image = Image.open(path)
    require(image.size == size, f"{label} must be {size}, got {image.size}")
    require(image.mode in {"RGB", "RGBA"}, f"{label} must be RGB/RGBA, got {image.mode}")
    if opaque and image.mode == "RGBA":
        require(image.getchannel("A").getextrema() == (255, 255), f"{label} must be fully opaque")
    return image.convert("RGB")


def edge_detail_score(image: Image.Image) -> float:
    edge = image.convert("L").filter(ImageFilter.FIND_EDGES)
    return float(ImageStat.Stat(edge).mean[0])


def gray_variance(image: Image.Image) -> float:
    return float(ImageStat.Stat(image.convert("L")).var[0])


def edge_rgb_mean(image: Image.Image, edge: str, width: int = 56) -> tuple[float, float, float]:
    if edge == "west":
        crop = image.crop((0, 0, width, image.height))
    elif edge == "east":
        crop = image.crop((image.width - width, 0, image.width, image.height))
    else:
        raise ValueError(edge)
    return tuple(float(value) for value in ImageStat.Stat(crop).mean[:3])


def average_delta(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return sum(abs(a[index] - b[index]) for index in range(3)) / 3.0


def require_false_flags(record: dict[str, Any], label: str) -> None:
    for key in ["human_visual_approval", "layer_export_approved", "runtime_replacement", "launch_quality_approved"]:
        require(record.get(key) is False, f"{label} must keep {key}=false")


def validate_metrics(v002: Image.Image) -> dict[str, float]:
    village = load_image(VILLAGE_SOURCE, CANVAS, "Village reference")
    v001 = load_image(V001_SOURCE, CANVAS, "MountainHut v001 source")

    village_detail = edge_detail_score(village)
    v001_detail = edge_detail_score(v001)
    v002_detail = edge_detail_score(v002)
    village_variance = gray_variance(village)
    v002_variance = gray_variance(v002)

    detail_ratio = v002_detail / village_detail
    variance_ratio = v002_variance / village_variance
    improvement_ratio = v002_detail / max(0.001, v001_detail)
    seam_delta = average_delta(edge_rgb_mean(village, "east"), edge_rgb_mean(v002, "west"))

    require(detail_ratio >= MIN_DETAIL_RATIO, f"v002 detail ratio too low: {detail_ratio:.4f} < {MIN_DETAIL_RATIO}")
    require(detail_ratio <= MAX_DETAIL_RATIO, f"v002 detail ratio too high/noisy: {detail_ratio:.4f} > {MAX_DETAIL_RATIO}")
    require(variance_ratio >= MIN_VARIANCE_RATIO, f"v002 variance ratio too low: {variance_ratio:.4f} < {MIN_VARIANCE_RATIO}")
    require(improvement_ratio >= 1.20, f"v002 should materially improve v001 detail: {improvement_ratio:.4f}")
    require(seam_delta <= MAX_SEAM_DELTA, f"v002 west seam color delta too high: {seam_delta:.4f} > {MAX_SEAM_DELTA}")

    return {
        "village_detail_edge_mean": village_detail,
        "v001_detail_edge_mean": v001_detail,
        "v002_detail_edge_mean": v002_detail,
        "detail_ratio": detail_ratio,
        "village_gray_variance": village_variance,
        "v002_gray_variance": v002_variance,
        "variance_ratio": variance_ratio,
        "detail_improvement_over_v001": improvement_ratio,
        "seam_edge_average_channel_delta": seam_delta,
    }


def validate_anchor_readability(v002: Image.Image) -> None:
    layout = load_json(LAYOUT_LOCK)
    zones = {str(zone.get("id")): zone for zone in layout.get("object_zones", []) if isinstance(zone, dict)}
    for anchor_id in REQUIRED_ANCHORS:
        require(anchor_id in zones, f"layout missing anchor {anchor_id}")
        x, y, w, h = [int(value) for value in zones[anchor_id]["source_rect"]]
        crop = v002.crop((max(0, x), max(0, y), min(CANVAS[0], x + w), min(CANVAS[1], y + h)))
        crop_detail = edge_detail_score(crop)
        crop_variance = gray_variance(crop)
        require(crop_detail > 5.0, f"anchor detail too low: {anchor_id}")
        require(crop_variance > 220.0, f"anchor variance too low: {anchor_id}")


def validate_overlay_and_contact(v002: Image.Image) -> None:
    overlay = load_image(V002_OVERLAY, CANVAS, "v002 review overlay")
    diff = ImageChops.difference(v002, overlay)
    require(sum(ImageStat.Stat(diff).sum) > 1_000_000, "v002 review overlay should visibly differ from source")
    load_image(V002_CONTACT, CONTACT_SIZE, "v002 review contact sheet")


def validate_quality_record(expected_metrics: dict[str, float]) -> None:
    quality = load_json(V002_QUALITY)
    require(quality.get("review_id") == "mountain_hut_source_quality_review_v002", "v002 quality review id mismatch")
    require(quality.get("status") == STATUS, "v002 quality status mismatch")
    require(quality.get("source_candidate") == rel(V002_SOURCE), "v002 quality source path mismatch")
    require(quality.get("quality_reference_source") == rel(VILLAGE_SOURCE), "v002 quality reference path mismatch")
    require(quality.get("source_candidate_review") == rel(V002_REPORT), "v002 quality report path mismatch")
    require(quality.get("review_contact_sheet") == rel(V002_CONTACT), "v002 quality contact path mismatch")
    require_false_flags(quality.get("hard_approval_flags", {}), "v002 quality hard flags")
    metrics = quality.get("metrics")
    require(isinstance(metrics, dict), "v002 quality metrics must be an object")
    for key, expected in expected_metrics.items():
        actual = float(metrics.get(key, -1.0))
        require(abs(actual - expected) < 0.02, f"v002 quality metric mismatch for {key}: {actual} vs {expected}")
    require(float(metrics.get("minimum_detail_ratio_for_review_ready", 0.0)) >= MIN_DETAIL_RATIO, "v002 quality target too low")
    require(float(metrics.get("minimum_variance_ratio_for_review_ready", 0.0)) >= MIN_VARIANCE_RATIO, "v002 variance target too low")
    require(float(metrics.get("maximum_preferred_seam_delta_for_precheck", 999.0)) <= MAX_SEAM_DELTA, "v002 seam target too loose")
    findings = quality.get("remaining_review_notes")
    require(isinstance(findings, list) and len(findings) >= 2, "v002 quality should keep human review notes")


def validate_acceptance_and_manifests() -> None:
    acceptance = load_json(V002_ACCEPTANCE)
    require(acceptance.get("candidate_id") == CANDIDATE_ID, "v002 acceptance candidate id mismatch")
    require(acceptance.get("status") in {STATUS, VISUAL_REVIEW_PHASE}, "v002 acceptance status mismatch")
    require(acceptance.get("candidate_type") == "v002_full_canvas_storybook_source_candidate", "v002 candidate type mismatch")
    require(acceptance.get("source_image") == rel(V002_SOURCE), "v002 acceptance source path mismatch")
    require(acceptance.get("review_overlay") == rel(V002_OVERLAY), "v002 acceptance overlay path mismatch")
    require(acceptance.get("quality_review") == rel(V002_QUALITY), "v002 acceptance quality path mismatch")
    require_false_flags(acceptance, "v002 acceptance")

    precheck = acceptance.get("codex_visual_precheck")
    require(isinstance(precheck, dict), "v002 acceptance missing precheck")
    require(precheck.get("not_human_visual_approval") is True, "v002 precheck must not be human approval")
    precheck_text = json.dumps(precheck, ensure_ascii=False).lower()
    for token in ["registration-perfect", "single painted source", "full canvas", "no runtime replacement", "human/art review"]:
        require(token in precheck_text, f"v002 precheck missing token: {token}")

    workflow = load_json(WORKFLOW)
    require(workflow.get("runtime_replacement") is False, "workflow must keep runtime_replacement=false")
    require(workflow.get("launch_quality_approved") is False, "workflow must keep launch_quality_approved=false")
    phase = workflow.get("phase_status")
    require(isinstance(phase, dict), "workflow phase_status must be object")
    require(
        phase.get("03_layer_export")
        in {
            "blocked_until_source_acceptance",
            "blocked_until_v003_visual_acceptance",
            "blocked_until_v004_visual_acceptance",
            "v004_semantic_layers_exported_pending_review",
        },
        "workflow must keep layer export blocked",
    )
    v002 = workflow.get("v002_source_candidate")
    require(isinstance(v002, dict), "workflow missing v002_source_candidate")
    require(v002.get("candidate_id") == CANDIDATE_ID, "workflow v002 candidate id mismatch")
    require(v002.get("status") == STATUS, "workflow v002 status mismatch")
    require(v002.get("image") == rel(V002_SOURCE), "workflow v002 image mismatch")
    require(v002.get("acceptance_record") == rel(V002_ACCEPTANCE), "workflow v002 acceptance mismatch")
    require(v002.get("quality_review_record") == rel(V002_QUALITY), "workflow v002 quality mismatch")
    require_false_flags(v002, "workflow v002 source candidate")

    contract = load_json(LAYER_CONTRACT)
    require(contract.get("runtime_replacement") is False, "layer contract must keep runtime_replacement=false")
    source_image = contract.get("source_image")
    require(isinstance(source_image, dict), "layer contract missing source_image")
    require(source_image.get("v002_candidate") == rel(V002_SOURCE), "layer contract v002 source path mismatch")
    require(source_image.get("v002_quality_review") == rel(V002_QUALITY), "layer contract v002 quality path mismatch")
    require(source_image.get("human_visual_approval") is False, "layer contract must keep human approval false")
    require(source_image.get("layer_export_approved") is False, "layer contract must keep layer export approval false")
    require(
        contract.get("layer_export_status") in {
            "blocked_until_v002_human_art_acceptance",
            "blocked_until_v003_source_acceptance",
            "blocked_until_v003_visual_acceptance",
            "blocked_until_v004_visual_acceptance",
            "v004_semantic_layers_exported_pending_review",
        },
        "layer contract must block MountainHut layer export",
    )

    manifest = load_json(PROJECT_MANIFEST)
    regions = manifest.get("current_runtime_regions")
    require(isinstance(regions, list), "project manifest current_runtime_regions must be a list")
    hut = next((entry for entry in regions if isinstance(entry, dict) and entry.get("region_id") == "Region_MountainHut"), None)
    require(isinstance(hut, dict), "project manifest missing Region_MountainHut")
    require(hut.get("runtime_replacement") is False, "project manifest MountainHut must keep runtime_replacement=false")
    require(hut.get("active_v002_source_candidate") == rel(V002_SOURCE), "project manifest missing active v002 candidate")
    require(hut.get("active_v002_quality_review") == rel(V002_QUALITY), "project manifest missing v002 quality review")
    next_step = str(hut.get("next_art_step", ""))
    require(
        "human/art review" in next_step or "v003" in next_step or "v004" in next_step or "semantic layers" in next_step,
        "project manifest next step should name human/art review, v003 repaint, v004 review, or semantic layers",
    )


def validate_docs_and_generator() -> None:
    report = read(V002_REPORT)
    for token in [
        CANDIDATE_ID,
        STATUS,
        "Detail ratio",
        "Runtime replacement remains blocked",
        "not human/art approval",
    ]:
        require(token in report, f"v002 report missing token: {token}")
    generator = read(GENERATOR)
    for token in [
        "draw_source_v002",
        "mountain_hut_painted_source_v002.png",
        "source_acceptance_v002.json",
        "source_quality_review_v002.json",
        "registration-perfect",
    ]:
        require(token in generator, f"v002 generator missing token: {token}")


def main() -> None:
    v002 = load_image(V002_SOURCE, CANVAS, "MountainHut v002 source")
    metrics = validate_metrics(v002)
    validate_anchor_readability(v002)
    validate_overlay_and_contact(v002)
    validate_quality_record(metrics)
    validate_acceptance_and_manifests()
    validate_docs_and_generator()
    print("OK: MountainHut v002 source candidate validates")


if __name__ == "__main__":
    main()
