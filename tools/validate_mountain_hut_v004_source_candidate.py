from __future__ import annotations

import json
import math
import struct
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageFilter, ImageStat


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production/assets/regions/mountain_hut_world2d/v001"
SOURCE_DIR = PACKAGE_DIR / "02_source_generation"
V003_DIR = SOURCE_DIR / "v003"
V004_DIR = SOURCE_DIR / "v004"
REVIEW_DIR = PACKAGE_DIR / "05_review_and_qa"
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
LAYER_CONTRACT = PACKAGE_DIR / "03_layer_export/layer_contract.json"
PROJECT_MANIFEST = ROOT / "production/assets/project_art_production_manifest_2026-05-19.json"
LAYOUT_LOCK = PACKAGE_DIR / "01_layout_lock/layout_lock.json"
VILLAGE_SOURCE = ROOT / "production/assets/regions/village_world2d/v001/02_source_generation/village_painted_source.png"
V003_SOURCE = V003_DIR / "mountain_hut_painted_source_v003.png"
V003_ACCEPTANCE = V003_DIR / "source_acceptance_v003.json"
V003_VISUAL_REVIEW = REVIEW_DIR / "source_visual_review_v003.json"
V003_REPORT = ROOT / ".codex/reports/mountain_hut_v003_visual_review_2026-05-25.md"
V004_SOURCE = V004_DIR / "mountain_hut_painted_source_v004.png"
V004_ACCEPTANCE = V004_DIR / "source_acceptance_v004.json"
V004_QUALITY = REVIEW_DIR / "source_quality_review_v004.json"
V004_CONTACT = REVIEW_DIR / "mountain_hut_v004_review_contact_sheet.png"
V004_REPORT = ROOT / ".codex/reports/mountain_hut_v004_source_candidate_review_2026-05-25.md"
GENERATOR = ROOT / "tools/generate_mountain_hut_painted_source_v004.py"

CANVAS = (1800, 1200)
CONTACT_SIZE = (1800, 1500)
V003_REJECT_STATUS = "needs_v004_repaint_before_layer_export"
V003_REJECT_PHASE = "mountain_hut_v003_visual_review_rejected_needs_v004_repaint"
V004_STATUS = "v004_candidate_ready_for_visual_review"
V004_PHASE = "mountain_hut_v004_candidate_ready_for_visual_review"
V004_CANDIDATE_ID = "mountain_hut_painted_source_candidate_v004"
LAYER_STATUS = "v004_semantic_layers_exported_pending_review"
MIN_DETAIL_RATIO = 0.74
MIN_VARIANCE_RATIO = 0.62
MAX_SEAM_DELTA = 24.0
MIN_V003_DIFF = 8.0
MAX_HARD_VECTOR_ROAD_RATIO = 0.012


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read(path: Path) -> str:
    require(path.exists(), f"missing {rel(path)}")
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> Any:
    return json.loads(read(path))


def png_size(path: Path) -> tuple[int, int]:
    require(path.exists(), f"missing {rel(path)}")
    with path.open("rb") as handle:
        data = handle.read(24)
    require(data[:8] == b"\x89PNG\r\n\x1a\n", f"not png: {rel(path)}")
    return struct.unpack(">II", data[16:24])


def load_image(path: Path, expected_size: tuple[int, int], label: str) -> Image.Image:
    require(path.exists(), f"missing {label}: {rel(path)}")
    image = Image.open(path)
    require(image.size == expected_size, f"{label} size mismatch: {image.size}, expected {expected_size}")
    return image.convert("RGBA")


def edge_detail_score(image: Image.Image) -> float:
    gray = image.convert("L")
    edges = ImageChops.difference(gray, gray.filter(ImageFilter.GaussianBlur(2.2)))
    return float(sum(ImageStat.Stat(edges).mean))


def gray_variance(image: Image.Image) -> float:
    return float(ImageStat.Stat(image.convert("L")).var[0])


def seam_delta(village: Image.Image, candidate: Image.Image) -> float:
    village_edge = village.convert("RGB").crop((1600, 420, 1800, 820)).resize((220, 400), Image.Resampling.LANCZOS)
    candidate_edge = candidate.convert("RGB").crop((0, 467, 220, 867)).resize((220, 400), Image.Resampling.LANCZOS)
    diff = ImageChops.difference(village_edge, candidate_edge)
    return float(sum(ImageStat.Stat(diff).mean) / 3.0)


def mean_diff(a: Image.Image, b: Image.Image) -> float:
    diff = ImageChops.difference(a.convert("RGB"), b.convert("RGB"))
    return float(sum(ImageStat.Stat(diff).mean) / 3.0)


def hard_vector_road_ratio(image: Image.Image) -> float:
    count = 0
    rgb = image.convert("RGB")
    for r, g, b in rgb.getdata():
        if r > 205 and g > 165 and 70 < b < 150 and (r - b) > 70 and (g - b) > 45:
            count += 1
    return count / float(rgb.width * rgb.height)


def validate_source_image() -> dict[str, float]:
    village = load_image(VILLAGE_SOURCE, CANVAS, "accepted Village source")
    v003 = load_image(V003_SOURCE, CANVAS, "MountainHut v003 source")
    v004 = load_image(V004_SOURCE, CANVAS, "MountainHut v004 source")
    require(v004.getchannel("A").getextrema() == (255, 255), "v004 source must be fully opaque")

    detail_ratio = edge_detail_score(v004) / max(edge_detail_score(village), 0.0001)
    variance_ratio = gray_variance(v004) / max(gray_variance(village), 0.0001)
    seam = seam_delta(village, v004)
    v003_diff = mean_diff(v003, v004)
    v003_hard = hard_vector_road_ratio(v003)
    v004_hard = hard_vector_road_ratio(v004)

    require(detail_ratio >= MIN_DETAIL_RATIO, f"v004 detail ratio too low: {detail_ratio:.4f}")
    require(variance_ratio >= MIN_VARIANCE_RATIO, f"v004 variance ratio too low: {variance_ratio:.4f}")
    require(seam <= MAX_SEAM_DELTA, f"v004 seam delta too high: {seam:.4f}")
    require(v003_diff >= MIN_V003_DIFF, f"v004 is too close to rejected v003: {v003_diff:.4f}")
    require(v004_hard <= MAX_HARD_VECTOR_ROAD_RATIO, f"v004 still has too much hard vector-road color: {v004_hard:.4f}")
    require(v003_hard > v004_hard * 3.0, "v004 must materially reduce the v003 hard vector-road signature")

    layout = read_json(LAYOUT_LOCK)
    west = layout.get("seam_connectors", [])[0]
    require(west.get("source_point") == [0, 667], "layout west seam source point changed unexpectedly")
    seam_crop = v004.convert("RGB").crop((0, 590, 160, 745))
    door_crop = v004.convert("RGB").crop((780, 250, 1040, 520))
    require(gray_variance(seam_crop) > 180.0, "v004 west seam crop is too flat")
    require(gray_variance(door_crop) > 420.0, "v004 hut crop is too flat or missing")

    return {
        "detail_ratio": detail_ratio,
        "variance_ratio": variance_ratio,
        "seam_edge_average_channel_delta": seam,
        "v003_mean_diff": v003_diff,
        "v003_hard_vector_road_ratio": v003_hard,
        "v004_hard_vector_road_ratio": v004_hard,
    }


def validate_v003_rejection() -> None:
    review = read_json(V003_VISUAL_REVIEW)
    require(review.get("status") == V003_REJECT_STATUS, "v003 visual review status mismatch")
    require(review.get("v003_visual_accepted") is False, "v003 must remain visually rejected")
    require(review.get("layer_export_approved") is False, "v003 review must block layer export")
    reasons = "\n".join(str(item) for item in review.get("rejection_reasons", []))
    for token in ["hard-edged", "vector-road", "pasted", "metrics"]:
        require(token in reasons, f"v003 rejection missing token {token!r}")
    acceptance = read_json(V003_ACCEPTANCE)
    require(acceptance.get("status") == V003_REJECT_PHASE, "v003 acceptance must record rejection phase")
    visual = acceptance.get("codex_visual_review", {})
    require(visual.get("status") == V003_REJECT_STATUS, "v003 acceptance visual status mismatch")
    report = read(V003_REPORT)
    for token in [V003_REJECT_STATUS, "v003 rejected", "vector-road", "runtime replacement remain blocked"]:
        require(token in report, f"v003 visual report missing token: {token}")


def validate_quality_json(metrics: dict[str, float]) -> None:
    data = read_json(V004_QUALITY)
    require(data.get("review_id") == "mountain_hut_source_quality_review_v004", "v004 quality review id mismatch")
    require(data.get("status") == V004_STATUS, "v004 quality status mismatch")
    require(data.get("source_candidate") == rel(V004_SOURCE), "v004 quality source path mismatch")
    quality_metrics = data.get("metrics", {})
    require(float(quality_metrics.get("detail_ratio", 0.0)) >= MIN_DETAIL_RATIO, "v004 quality detail ratio too low")
    require(float(quality_metrics.get("variance_ratio", 0.0)) >= MIN_VARIANCE_RATIO, "v004 quality variance ratio too low")
    require(float(quality_metrics.get("seam_edge_average_channel_delta", 999.0)) <= MAX_SEAM_DELTA, "v004 quality seam delta too high")
    require(float(quality_metrics.get("v004_hard_vector_road_ratio", 999.0)) <= MAX_HARD_VECTOR_ROAD_RATIO, "v004 quality hard road ratio too high")
    for key, expected in metrics.items():
        actual = float(quality_metrics.get(key, -999.0))
        require(math.isclose(actual, expected, rel_tol=0.03, abs_tol=0.08), f"v004 quality metric {key} mismatch")
    flags = data.get("hard_approval_flags", {})
    for key in ["human_visual_approval", "layer_export_approved", "runtime_replacement", "launch_quality_approved"]:
        require(flags.get(key) is False, f"v004 quality must keep {key}=false")


def validate_acceptance_and_manifests() -> None:
    acceptance = read_json(V004_ACCEPTANCE)
    require(acceptance.get("candidate_id") == V004_CANDIDATE_ID, "v004 acceptance candidate id mismatch")
    require(
        acceptance.get("status") in {V004_STATUS, "v004_accepted_for_semantic_layer_export_review"},
        "v004 acceptance status mismatch",
    )
    require(acceptance.get("source_image") == rel(V004_SOURCE), "v004 acceptance source path mismatch")
    for key in ["human_visual_approval", "layer_export_approved", "runtime_replacement", "launch_quality_approved"]:
        require(acceptance.get(key) is False, f"v004 acceptance must keep {key}=false")

    workflow = read_json(WORKFLOW)
    require(workflow.get("status") in {V004_PHASE, LAYER_STATUS}, "workflow status mismatch")
    require(
        workflow.get("current_phase") in {"02_source_generation_v004_review", "03_layer_export_v004_semantic_review"},
        "workflow current phase mismatch",
    )
    phase_status = workflow.get("phase_status", {})
    require(phase_status.get("02_source_visual_review_v003") == V003_REJECT_STATUS, "workflow v003 review phase mismatch")
    require(phase_status.get("02_source_generation_v004") == V004_STATUS, "workflow v004 phase mismatch")
    require(
        phase_status.get("03_layer_export") in {"blocked_until_v004_visual_acceptance", LAYER_STATUS},
        "workflow layer export status mismatch",
    )
    v004 = workflow.get("v004_source_candidate", {})
    require(v004.get("candidate_id") == V004_CANDIDATE_ID, "workflow v004 candidate id mismatch")
    require(v004.get("image") == rel(V004_SOURCE), "workflow v004 image mismatch")
    for key in ["human_visual_approval", "layer_export_approved", "runtime_replacement", "launch_quality_approved"]:
        require(v004.get(key) is False, f"workflow v004 must keep {key}=false")

    contract = read_json(LAYER_CONTRACT)
    source = contract.get("source_image", {})
    require(
        source.get("current_file_status")
        in {"v004_candidate_pending_visual_review", "v004_codex_visual_accepted_for_semantic_layer_export"},
        "layer contract source status mismatch",
    )
    require(source.get("v003_visual_review") == rel(V003_VISUAL_REVIEW), "layer contract v003 review mismatch")
    require(source.get("v004_candidate") == rel(V004_SOURCE), "layer contract v004 source mismatch")
    require(source.get("v004_quality_review") == rel(V004_QUALITY), "layer contract v004 quality mismatch")
    require(
        contract.get("layer_export_status") in {"blocked_until_v004_visual_acceptance", LAYER_STATUS},
        "layer contract export status mismatch",
    )
    require(contract.get("runtime_replacement") is False, "layer contract must keep runtime_replacement=false")

    manifest = read_json(PROJECT_MANIFEST)
    regions = manifest.get("current_runtime_regions", [])
    hut = next((item for item in regions if isinstance(item, dict) and item.get("region_id") == "Region_MountainHut"), None)
    require(isinstance(hut, dict), "project manifest missing Region_MountainHut")
    require(hut.get("phase") in {V004_PHASE, LAYER_STATUS}, "project manifest MountainHut phase mismatch")
    require(hut.get("active_v003_visual_review") == rel(V003_VISUAL_REVIEW), "project manifest v003 visual review mismatch")
    require(hut.get("active_v004_source_candidate") == rel(V004_SOURCE), "project manifest v004 source mismatch")
    require(hut.get("active_v004_quality_review") == rel(V004_QUALITY), "project manifest v004 quality mismatch")
    require(hut.get("runtime_replacement") is False, "project manifest must keep runtime_replacement=false")
    require(hut.get("launch_quality_approved") is False, "project manifest must keep launch_quality_approved=false")
    next_step = str(hut.get("next_art_step", ""))
    require(
        "visual review" in next_step or "semantic layers" in next_step,
        "project manifest next step must point to v004 visual or semantic layer review",
    )


def validate_docs_and_artifacts() -> None:
    require(png_size(V004_CONTACT) == CONTACT_SIZE, "v004 contact sheet size mismatch")
    report = read(V004_REPORT)
    for token in [V004_CANDIDATE_ID, V004_STATUS, "not human/art approval", "runtime replacement remains blocked"]:
        require(token in report, f"v004 report missing token: {token}")
    generator = read(GENERATOR)
    for token in ["EXTERNAL_REFERENCE", "V004_SOURCE", "hard_vector_road_ratio", "not a new road drawing layer"]:
        require(token in generator, f"v004 generator missing token: {token}")


def main() -> None:
    metrics = validate_source_image()
    validate_v003_rejection()
    validate_quality_json(metrics)
    validate_acceptance_and_manifests()
    validate_docs_and_artifacts()
    print("OK: MountainHut v004 source candidate validates")


if __name__ == "__main__":
    main()
