from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageFilter, ImageStat


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production/assets/regions/village_world2d/v001"
V003_DIR = PACKAGE_DIR / "02_source_generation/v003_edge_continuity_repaint"
V003_SOURCE = V003_DIR / "village_painted_source_v003.png"
V003_ACCEPTANCE = V003_DIR / "source_acceptance_v003.json"
V003_QUALITY = V003_DIR / "source_quality_review_v003.json"
V003_CONTACT = V003_DIR / "village_v003_edge_continuity_contact_sheet.png"
V002_SOURCE = PACKAGE_DIR / "02_source_generation/v002_inherited_world_base_repaint/village_painted_source_v002.png"
OLD_SOURCE = PACKAGE_DIR / "02_source_generation/village_painted_source.png"
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
LAYER_CONTRACT = PACKAGE_DIR / "03_layer_export/layer_contract.json"
PROJECT_MANIFEST = ROOT / "production/assets/project_art_production_manifest_2026-05-19.json"
REPORT = ROOT / ".codex/reports/village_v003_edge_continuity_source_review_2026-05-26.md"
GENERATOR = ROOT / "tools/generate_village_painted_source_v003.py"

CANVAS = (1800, 1200)
CONTACT_SIZE = (2400, 1500)
STATUS = "v003_edge_continuity_candidate_ready_for_visual_review"
CANDIDATE_ID = "village_painted_source_v003"


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


def load_image(path: Path, label: str) -> Image.Image:
    require(path.is_file(), f"missing {label}: {rel(path)}")
    image = Image.open(path).convert("RGBA")
    require(image.size == CANVAS, f"{label} size mismatch: {image.size}")
    return image


def edge_detail_score(image: Image.Image) -> float:
    gray = image.convert("L")
    edges = ImageChops.difference(gray, gray.filter(ImageFilter.GaussianBlur(2.2)))
    return float(sum(ImageStat.Stat(edges).mean))


def mean_rgb_diff(left: Image.Image, right: Image.Image) -> float:
    diff = ImageChops.difference(left.convert("RGB"), right.convert("RGB"))
    return float(sum(ImageStat.Stat(diff).mean) / 3.0)


def edge_review_band(image: Image.Image) -> Image.Image:
    rgb = image.convert("RGB")
    band = Image.new("RGB", (1800, 960), (0, 0, 0))
    band.paste(rgb.crop((0, 0, 1800, 220)), (0, 0))
    band.paste(rgb.crop((0, 980, 1800, 1200)), (0, 240))
    band.paste(rgb.crop((0, 120, 260, 1080)).resize((900, 240), Image.Resampling.LANCZOS), (0, 500))
    band.paste(rgb.crop((1540, 120, 1800, 1080)).resize((900, 240), Image.Resampling.LANCZOS), (900, 500))
    return band


def edge_luminance(image: Image.Image) -> float:
    return float(ImageStat.Stat(edge_review_band(image).convert("L")).mean[0])


def validate_metrics() -> dict[str, float]:
    v003 = load_image(V003_SOURCE, "v003 source")
    v002 = load_image(V002_SOURCE, "v002 source")
    old = load_image(OLD_SOURCE, "old Village source")
    require(v003.getchannel("A").getextrema() == (255, 255), "v003 source must be fully opaque")

    edge_detail_v003 = edge_detail_score(edge_review_band(v003))
    edge_detail_v002 = edge_detail_score(edge_review_band(v002))
    edge_luma_v003 = edge_luminance(v003)
    edge_luma_v002 = edge_luminance(v002)
    center_v003 = v003.crop((360, 210, 1440, 930))
    center_v002 = v002.crop((360, 210, 1440, 930))
    center_old = old.crop((360, 210, 1440, 930))
    center_diff_from_v002 = mean_rgb_diff(center_v003, center_v002)
    center_diff_from_old = mean_rgb_diff(center_v003, center_old)
    edge_diff_from_v002 = mean_rgb_diff(edge_review_band(v003), edge_review_band(v002))

    require(edge_luma_v003 <= edge_luma_v002 - 18.0, f"v003 edge luminance not reduced enough: {edge_luma_v003:.4f} vs {edge_luma_v002:.4f}")
    require(edge_detail_v003 >= edge_detail_v002 * 1.18, f"v003 edge detail not improved enough: {edge_detail_v003:.4f} vs {edge_detail_v002:.4f}")
    require(center_diff_from_v002 <= 14.0, f"v003 center drift from v002 should stay small for edge-only repair: {center_diff_from_v002:.4f}")
    require(center_diff_from_old < 24.0, f"v003 center should still retain accepted Village quality reference: {center_diff_from_old:.4f}")
    require(edge_diff_from_v002 >= 24.0, f"v003 edge should materially differ from the soft v002 edge: {edge_diff_from_v002:.4f}")

    return {
        "edge_luminance_v003": round(edge_luma_v003, 4),
        "edge_luminance_v002": round(edge_luma_v002, 4),
        "edge_detail_v003": round(edge_detail_v003, 4),
        "edge_detail_v002": round(edge_detail_v002, 4),
        "edge_diff_from_v002": round(edge_diff_from_v002, 4),
        "center_diff_from_v002": round(center_diff_from_v002, 4),
        "center_diff_from_old_source": round(center_diff_from_old, 4),
    }


def validate_records(metrics: dict[str, float]) -> None:
    acceptance = read_json(V003_ACCEPTANCE)
    require(acceptance.get("candidate_id") == CANDIDATE_ID, "acceptance candidate id mismatch")
    require(acceptance.get("status") == STATUS, "acceptance status mismatch")
    require(acceptance.get("source_image") == rel(V003_SOURCE), "acceptance source path mismatch")
    require(acceptance.get("repair_scope") == "edge_continuity_only", "acceptance repair scope mismatch")
    for key in ["human_visual_approval", "layer_export_approved", "runtime_replacement", "launch_quality_approved"]:
        require(acceptance.get(key) is False, f"acceptance must keep {key}=false")

    quality = read_json(V003_QUALITY)
    require(quality.get("status") == STATUS, "quality status mismatch")
    quality_metrics = as_dict(quality.get("metrics"), "quality.metrics")
    for key, expected in metrics.items():
        actual = float(quality_metrics.get(key, -999.0))
        require(math.isclose(actual, expected, rel_tol=0.03, abs_tol=0.08), f"quality metric {key} mismatch")

    workflow = read_json(WORKFLOW)
    block = as_dict(workflow.get("v003_edge_continuity_source_candidate"), "workflow.v003_edge_continuity_source_candidate")
    require(block.get("candidate_id") == CANDIDATE_ID, "workflow v003 candidate id mismatch")
    require(block.get("image") == rel(V003_SOURCE), "workflow v003 image path mismatch")
    require(block.get("status") == STATUS, "workflow v003 status mismatch")
    for key in ["human_visual_approval", "layer_export_approved", "runtime_replacement", "launch_quality_approved"]:
        require(block.get(key) is False, f"workflow v003 must keep {key}=false")

    contract = read_json(LAYER_CONTRACT)
    source = as_dict(contract.get("source_image"), "layer_contract.source_image")
    require(source.get("v003_candidate") == rel(V003_SOURCE), "layer contract v003 source path mismatch")
    require(
        source.get("v003_layer_export_status")
        in {"blocked_until_v003_visual_acceptance", "v003_semantic_layers_exported_pending_review"},
        "layer contract v003 export status mismatch",
    )
    require(contract.get("runtime_replacement") is False, "layer contract must keep runtime_replacement=false")

    project = read_json(PROJECT_MANIFEST)
    regions = project.get("current_runtime_regions", [])
    village = next((item for item in regions if isinstance(item, dict) and item.get("region_id") == "Region_Village"), None)
    require(isinstance(village, dict), "project manifest missing Region_Village")
    require(
        village.get("phase") in {STATUS, "v003_semantic_layers_exported_pending_review"},
        "project manifest Village phase mismatch",
    )
    require(village.get("active_v003_source_candidate") == rel(V003_SOURCE), "project manifest v003 source path mismatch")
    require(village.get("runtime_replacement") is False, "project manifest must keep runtime_replacement=false")
    require(village.get("launch_quality_approved") is False, "project manifest must keep launch_quality_approved=false")


def validate_artifacts() -> None:
    contact = Image.open(V003_CONTACT).convert("RGB")
    require(contact.size == CONTACT_SIZE, f"contact sheet size mismatch: {contact.size}")
    require(sum(ImageStat.Stat(contact).var) > 500.0, "contact sheet appears blank")
    report = read(REPORT)
    for token in [CANDIDATE_ID, STATUS, "not runtime replacement", "edge continuity"]:
        require(token in report, f"report missing token: {token}")
    generator = read(GENERATOR)
    for token in ["edge_continuity_only", "V002_SOURCE", "OLD_SOURCE", "edge_mask"]:
        require(token in generator, f"generator missing token: {token}")


def main() -> None:
    metrics = validate_metrics()
    validate_records(metrics)
    validate_artifacts()
    print("OK: Village v003 edge-continuity source candidate validates")


if __name__ == "__main__":
    main()
