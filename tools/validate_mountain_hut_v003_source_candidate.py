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
V002_DIR = SOURCE_DIR / "v002"
V003_DIR = SOURCE_DIR / "v003"
REVIEW_DIR = PACKAGE_DIR / "05_review_and_qa"
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
LAYER_CONTRACT = PACKAGE_DIR / "03_layer_export/layer_contract.json"
PROJECT_MANIFEST = ROOT / "production/assets/project_art_production_manifest_2026-05-19.json"
LAYOUT_LOCK = PACKAGE_DIR / "01_layout_lock/layout_lock.json"
VILLAGE_SOURCE = ROOT / "production/assets/regions/village_world2d/v001/02_source_generation/village_painted_source.png"
V002_SOURCE = V002_DIR / "mountain_hut_painted_source_v002.png"
V003_SOURCE = V003_DIR / "mountain_hut_painted_source_v003.png"
V003_ACCEPTANCE = V003_DIR / "source_acceptance_v003.json"
V003_QUALITY = REVIEW_DIR / "source_quality_review_v003.json"
V003_CONTACT = REVIEW_DIR / "mountain_hut_v003_review_contact_sheet.png"
V003_REPORT = ROOT / ".codex/reports/mountain_hut_v003_source_candidate_review_2026-05-25.md"
GENERATOR = ROOT / "tools/generate_mountain_hut_painted_source_v003.py"

CANVAS = (1800, 1200)
CONTACT_SIZE = (1800, 1500)
CANDIDATE_ID = "mountain_hut_painted_source_candidate_v003"
STATUS = "v003_candidate_ready_for_visual_review"
PHASE = "mountain_hut_v003_candidate_ready_for_visual_review"
REJECT_PHASE = "mountain_hut_v003_visual_review_rejected_needs_v004_repaint"
V004_PHASE = "mountain_hut_v004_candidate_ready_for_visual_review"
V004_LAYER_PHASE = "v004_semantic_layers_exported_pending_review"
MIN_DETAIL_RATIO = 0.74
MIN_VARIANCE_RATIO = 0.62
MAX_SEAM_DELTA = 24.0
MIN_V002_DIFF = 8.0


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


def validate_source_image() -> dict[str, float]:
    village = load_image(VILLAGE_SOURCE, CANVAS, "accepted Village source")
    v002 = load_image(V002_SOURCE, CANVAS, "MountainHut v002 source")
    v003 = load_image(V003_SOURCE, CANVAS, "MountainHut v003 source")
    require(v003.mode == "RGBA", "v003 source must be loadable as RGBA")
    alpha = v003.getchannel("A")
    require(alpha.getextrema() == (255, 255), "v003 source must be fully opaque")

    detail_ratio = edge_detail_score(v003) / max(edge_detail_score(village), 0.0001)
    variance_ratio = gray_variance(v003) / max(gray_variance(village), 0.0001)
    seam = seam_delta(village, v003)
    v002_diff = mean_diff(v002, v003)
    require(detail_ratio >= MIN_DETAIL_RATIO, f"v003 detail ratio too low: {detail_ratio:.4f}")
    require(variance_ratio >= MIN_VARIANCE_RATIO, f"v003 variance ratio too low: {variance_ratio:.4f}")
    require(seam <= MAX_SEAM_DELTA, f"v003 seam delta too high: {seam:.4f}")
    require(v002_diff >= MIN_V002_DIFF, f"v003 is too close to rejected v002: {v002_diff:.4f}")

    # Spatial lock checks: the west seam and hut door zones should contain visible non-flat content.
    layout = read_json(LAYOUT_LOCK)
    west = layout.get("seam_connectors", [])[0]
    require(west.get("source_point") == [0, 667], "layout west seam source point changed unexpectedly")
    seam_crop = v003.convert("RGB").crop((0, 590, 160, 745))
    door_crop = v003.convert("RGB").crop((932, 338, 1082, 508))
    require(gray_variance(seam_crop) > 180.0, "v003 west seam crop is too flat")
    require(gray_variance(door_crop) > 420.0, "v003 hut door crop is too flat or missing")

    return {
        "detail_ratio": detail_ratio,
        "variance_ratio": variance_ratio,
        "seam_delta": seam,
        "v002_mean_diff": v002_diff,
    }


def validate_quality_json(metrics: dict[str, float]) -> None:
    data = read_json(V003_QUALITY)
    require(data.get("review_id") == "mountain_hut_source_quality_review_v003", "v003 quality review id mismatch")
    require(data.get("status") == STATUS, "v003 quality status mismatch")
    require(data.get("source_candidate") == rel(V003_SOURCE), "v003 quality source path mismatch")
    require(data.get("review_contact_sheet") == rel(V003_CONTACT), "v003 contact sheet pointer mismatch")
    quality_metrics = data.get("metrics", {})
    require(float(quality_metrics.get("detail_ratio", 0.0)) >= MIN_DETAIL_RATIO, "v003 quality detail ratio too low")
    require(float(quality_metrics.get("variance_ratio", 0.0)) >= MIN_VARIANCE_RATIO, "v003 quality variance ratio too low")
    require(float(quality_metrics.get("seam_edge_average_channel_delta", 999.0)) <= MAX_SEAM_DELTA, "v003 quality seam delta too high")
    for key, expected in metrics.items():
        actual = float(quality_metrics.get(key, -999.0))
        require(math.isclose(actual, expected, rel_tol=0.03, abs_tol=0.08), f"v003 quality metric {key} mismatch")
    flags = data.get("hard_approval_flags", {})
    for key in ["human_visual_approval", "layer_export_approved", "runtime_replacement", "launch_quality_approved"]:
        require(flags.get(key) is False, f"v003 quality must keep {key}=false")


def validate_acceptance_and_manifests() -> None:
    acceptance = read_json(V003_ACCEPTANCE)
    require(acceptance.get("candidate_id") == CANDIDATE_ID, "v003 acceptance candidate id mismatch")
    require(acceptance.get("status") in {STATUS, REJECT_PHASE}, "v003 acceptance status mismatch")
    require(acceptance.get("source_image") == rel(V003_SOURCE), "v003 acceptance source path mismatch")
    require(acceptance.get("quality_review") == rel(V003_QUALITY), "v003 acceptance quality path mismatch")
    require(acceptance.get("review_contact_sheet") == rel(V003_CONTACT), "v003 acceptance contact path mismatch")
    for key in ["human_visual_approval", "layer_export_approved", "runtime_replacement", "launch_quality_approved"]:
        require(acceptance.get(key) is False, f"v003 acceptance must keep {key}=false")

    workflow = read_json(WORKFLOW)
    require(workflow.get("status") in {PHASE, V004_PHASE, V004_LAYER_PHASE}, "workflow status mismatch")
    require(
        workflow.get("current_phase")
        in {"02_source_generation_v003_review", "02_source_generation_v004_review", "03_layer_export_v004_semantic_review"},
        "workflow current phase mismatch",
    )
    require(workflow.get("runtime_replacement") is False, "workflow must keep runtime_replacement=false")
    require(workflow.get("launch_quality_approved") is False, "workflow must keep launch_quality_approved=false")
    phase_status = workflow.get("phase_status", {})
    require(phase_status.get("02_source_generation_v003") == STATUS, "workflow v003 phase mismatch")
    require(
        phase_status.get("03_layer_export")
        in {"blocked_until_v003_visual_acceptance", "blocked_until_v004_visual_acceptance", V004_LAYER_PHASE},
        "workflow layer export status mismatch",
    )
    v003 = workflow.get("v003_source_candidate", {})
    require(v003.get("candidate_id") == CANDIDATE_ID, "workflow v003 candidate id mismatch")
    require(v003.get("image") == rel(V003_SOURCE), "workflow v003 image mismatch")
    require(v003.get("acceptance_record") == rel(V003_ACCEPTANCE), "workflow v003 acceptance mismatch")
    for key in ["human_visual_approval", "layer_export_approved", "runtime_replacement", "launch_quality_approved"]:
        require(v003.get(key) is False, f"workflow v003 must keep {key}=false")

    contract = read_json(LAYER_CONTRACT)
    source = contract.get("source_image", {})
    require(source.get("v003_candidate") == rel(V003_SOURCE), "layer contract v003 source mismatch")
    require(source.get("v003_quality_review") == rel(V003_QUALITY), "layer contract v003 quality mismatch")
    require(
        source.get("current_file_status")
        in {
            "v003_candidate_pending_visual_review",
            "v004_candidate_pending_visual_review",
            "v004_codex_visual_accepted_for_semantic_layer_export",
        },
        "layer contract source status mismatch",
    )
    require(
        contract.get("layer_export_status")
        in {"blocked_until_v003_visual_acceptance", "blocked_until_v004_visual_acceptance", V004_LAYER_PHASE},
        "layer contract export status mismatch",
    )
    require(contract.get("runtime_replacement") is False, "layer contract must keep runtime_replacement=false")

    manifest = read_json(PROJECT_MANIFEST)
    regions = manifest.get("current_runtime_regions", [])
    hut = next((item for item in regions if isinstance(item, dict) and item.get("region_id") == "Region_MountainHut"), None)
    require(isinstance(hut, dict), "project manifest missing Region_MountainHut")
    require(hut.get("phase") in {PHASE, V004_PHASE, V004_LAYER_PHASE}, "project manifest MountainHut phase mismatch")
    require(hut.get("active_v003_source_candidate") == rel(V003_SOURCE), "project manifest v003 source mismatch")
    require(hut.get("active_v003_quality_review") == rel(V003_QUALITY), "project manifest v003 quality mismatch")
    require(hut.get("runtime_replacement") is False, "project manifest must keep runtime_replacement=false")
    require(hut.get("launch_quality_approved") is False, "project manifest must keep launch_quality_approved=false")
    next_step = str(hut.get("next_art_step", ""))
    require(
        "visual review" in next_step or "semantic layers" in next_step,
        "project manifest next step must point to visual or semantic layer review",
    )


def validate_docs_and_artifacts() -> None:
    require(png_size(V003_CONTACT) == CONTACT_SIZE, "v003 contact sheet size mismatch")
    report = read(V003_REPORT)
    for token in [CANDIDATE_ID, STATUS, "not human/art approval", "runtime replacement remains blocked"]:
        require(token in report, f"v003 report missing token: {token}")
    generator = read(GENERATOR)
    for token in ["EXTERNAL_REFERENCE", "VILLAGE_SOURCE", "V003_SOURCE", "source point", "single full-canvas"]:
        require(token in generator, f"v003 generator missing token: {token}")


def main() -> None:
    metrics = validate_source_image()
    validate_quality_json(metrics)
    validate_acceptance_and_manifests()
    validate_docs_and_artifacts()
    print("OK: MountainHut v003 source candidate validates")


if __name__ == "__main__":
    main()
