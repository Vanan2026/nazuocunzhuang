from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import json
import re

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FRAME_DIR = ROOT / "sprites" / "characters" / "protagonist" / "frames"
FINAL_STRIP_DIR = ROOT / "production" / "assets" / "protagonist" / "final_source_strips"
REPORT_DIR = ROOT / ".codex" / "reports"
JSON_REPORT = REPORT_DIR / "protagonist_walk_frame_diagnostics.json"
MD_REPORT = REPORT_DIR / "protagonist_walk_frame_diagnostics.md"

FRAME_SIZE = (192, 288)
SOURCE_SLOT_SIZE = (384, 576)
FOOT_BAND_Y1 = 236
FOOT_BAND_Y2 = 271
ALPHA_THRESHOLD = 10

WALK_ANIMS = [
    "player_walk_down",
    "player_walk_down_left",
    "player_walk_left",
    "player_walk_up_left",
    "player_walk_up",
    "player_walk_up_right",
    "player_walk_right",
    "player_walk_down_right",
]

DIAGONAL_PARENTS = {
    "player_walk_down_left": "player_walk_left",
    "player_walk_up_left": "player_walk_left",
    "player_walk_up_right": "player_walk_right",
    "player_walk_down_right": "player_walk_right",
}

SIT_ANIMS = [
    "player_sit_down_side",
    "player_sit_down_down",
    "player_sit_down_up",
    "player_sit_idle_side",
    "player_sit_idle_down",
    "player_sit_idle_up",
    "player_stand_up_side",
    "player_stand_up_down",
    "player_stand_up_up",
]


@dataclass(frozen=True)
class FrameMetric:
    frame: int
    bbox: tuple[int, int, int, int]
    width: int
    height: int
    area: int
    center_x: float
    center_y: float
    foot_bbox: tuple[int, int, int, int] | None
    foot_area: int
    foot_width: int
    foot_center_x: float | None
    sha256_12: str


@dataclass(frozen=True)
class AdjacentMetric:
    pair: str
    alpha_xor: int
    foot_xor: int
    rgba_mean_abs: float
    alpha_iou: float
    similarity: float


@dataclass(frozen=True)
class AnimationReport:
    animation: str
    frame_count: int
    expected_count: int
    contiguous: bool
    missing_indices: list[int]
    source_strip_exists: bool
    source_strip_size: tuple[int, int] | None
    duplicate_pairs: list[str]
    near_duplicate_pairs: list[str]
    frame_metrics: list[FrameMetric]
    adjacent_metrics: list[AdjacentMetric]
    summary: dict[str, float]
    warnings: list[str]


def image_hash(image: Image.Image) -> str:
    return hashlib.sha256(image.tobytes()).hexdigest()[:12]


def frame_paths(animation: str) -> list[tuple[int, Path]]:
    pattern = re.compile(rf"^{re.escape(animation)}_(\d{{2}})\.png$")
    indexed: list[tuple[int, Path]] = []
    for path in FRAME_DIR.glob(f"{animation}_*.png"):
        match = pattern.match(path.name)
        if match:
            indexed.append((int(match.group(1)), path))
    indexed.sort(key=lambda item: item[0])
    return indexed


def visible_bounds(mask: np.ndarray) -> tuple[int, int, int, int] | None:
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def frame_metric(idx: int, image: Image.Image) -> FrameMetric:
    rgba = np.array(image.convert("RGBA"))
    alpha = rgba[:, :, 3]
    visible = alpha > ALPHA_THRESHOLD
    bbox = visible_bounds(visible)
    if bbox is None:
        bbox = (0, 0, 0, 0)
        width = 0
        height = 0
        area = 0
        center_x = 0.0
        center_y = 0.0
    else:
        x1, y1, x2, y2 = bbox
        ys, xs = np.where(visible)
        width = x2 - x1 + 1
        height = y2 - y1 + 1
        area = int(visible.sum())
        center_x = float(xs.mean())
        center_y = float(ys.mean())

    foot = alpha[FOOT_BAND_Y1:FOOT_BAND_Y2, :] > ALPHA_THRESHOLD
    foot_bbox_local = visible_bounds(foot)
    if foot_bbox_local is None:
        foot_bbox = None
        foot_area = 0
        foot_width = 0
        foot_center_x = None
    else:
        fx1, fy1, fx2, fy2 = foot_bbox_local
        foot_bbox = (fx1, fy1 + FOOT_BAND_Y1, fx2, fy2 + FOOT_BAND_Y1)
        _fys, fxs = np.where(foot)
        foot_area = int(foot.sum())
        foot_width = fx2 - fx1 + 1
        foot_center_x = float(fxs.mean())

    return FrameMetric(
        frame=idx,
        bbox=bbox,
        width=width,
        height=height,
        area=area,
        center_x=center_x,
        center_y=center_y,
        foot_bbox=foot_bbox,
        foot_area=foot_area,
        foot_width=foot_width,
        foot_center_x=foot_center_x,
        sha256_12=image_hash(image),
    )


def adjacent_metric(left: Image.Image, right: Image.Image, pair: str) -> AdjacentMetric:
    a = np.array(left.convert("RGBA"))
    b = np.array(right.convert("RGBA"))
    alpha_a = a[:, :, 3] > ALPHA_THRESHOLD
    alpha_b = b[:, :, 3] > ALPHA_THRESHOLD
    foot_a = alpha_a[FOOT_BAND_Y1:FOOT_BAND_Y2, :]
    foot_b = alpha_b[FOOT_BAND_Y1:FOOT_BAND_Y2, :]
    union = np.logical_or(alpha_a, alpha_b)
    intersection = np.logical_and(alpha_a, alpha_b)
    alpha_iou = float(intersection.sum()) / max(1.0, float(union.sum()))
    diff = np.abs(a.astype(np.int16) - b.astype(np.int16))
    rgba_mean_abs = float(diff.mean())
    similarity = 1.0 - min(1.0, rgba_mean_abs / 255.0)
    return AdjacentMetric(
        pair=pair,
        alpha_xor=int(np.logical_xor(alpha_a, alpha_b).sum()),
        foot_xor=int(np.logical_xor(foot_a, foot_b).sum()),
        rgba_mean_abs=rgba_mean_abs,
        alpha_iou=alpha_iou,
        similarity=similarity,
    )


def pair_similarity(left: Image.Image, right: Image.Image) -> float:
    a = np.array(left.convert("RGBA")).astype(np.int16)
    b = np.array(right.convert("RGBA")).astype(np.int16)
    return 1.0 - min(1.0, float(np.abs(a - b).mean()) / 255.0)


def source_strip_info(animation: str, expected_count: int) -> tuple[bool, tuple[int, int] | None]:
    path = FINAL_STRIP_DIR / f"{animation}_source_strip.png"
    if not path.exists():
        return False, None
    with Image.open(path) as image:
        return True, image.size


def animation_report(animation: str, expected_count: int = 8) -> AnimationReport:
    indexed_paths = frame_paths(animation)
    indices = [idx for idx, _path in indexed_paths]
    missing = [idx for idx in range(expected_count) if idx not in indices]
    contiguous = indices == list(range(expected_count))
    images = [Image.open(path).convert("RGBA") for _idx, path in indexed_paths]
    metrics = [frame_metric(idx, image) for (idx, _path), image in zip(indexed_paths, images)]

    adjacent = [
        adjacent_metric(images[idx - 1], images[idx], f"{indices[idx - 1]:02d}-{indices[idx]:02d}")
        for idx in range(1, len(images))
    ]

    duplicate_pairs: list[str] = []
    near_duplicate_pairs: list[str] = []
    for left_idx in range(len(images)):
        for right_idx in range(left_idx + 1, len(images)):
            left_name = f"{indices[left_idx]:02d}"
            right_name = f"{indices[right_idx]:02d}"
            sim = pair_similarity(images[left_idx], images[right_idx])
            if metrics[left_idx].sha256_12 == metrics[right_idx].sha256_12:
                duplicate_pairs.append(f"{left_name}-{right_name}")
            elif sim >= 0.995:
                near_duplicate_pairs.append(f"{left_name}-{right_name}:{sim:.4f}")

    source_exists, source_size = source_strip_info(animation, expected_count)
    foot_areas = [metric.foot_area for metric in metrics]
    foot_centers = [metric.foot_center_x for metric in metrics if metric.foot_center_x is not None]
    foot_widths = [metric.foot_width for metric in metrics]
    bbox_widths = [metric.width for metric in metrics]
    bbox_heights = [metric.height for metric in metrics]
    adjacent_foot = [metric.foot_xor for metric in adjacent]
    adjacent_rgba = [metric.rgba_mean_abs for metric in adjacent]
    summary = {
        "bbox_width_range": float(max(bbox_widths) - min(bbox_widths)) if bbox_widths else 0.0,
        "bbox_height_range": float(max(bbox_heights) - min(bbox_heights)) if bbox_heights else 0.0,
        "foot_area_min": float(min(foot_areas)) if foot_areas else 0.0,
        "foot_area_max": float(max(foot_areas)) if foot_areas else 0.0,
        "foot_area_range": float(max(foot_areas) - min(foot_areas)) if foot_areas else 0.0,
        "foot_width_range": float(max(foot_widths) - min(foot_widths)) if foot_widths else 0.0,
        "foot_center_range": float(max(foot_centers) - min(foot_centers)) if foot_centers else 0.0,
        "adjacent_foot_xor_min": float(min(adjacent_foot)) if adjacent_foot else 0.0,
        "adjacent_foot_xor_mean": float(sum(adjacent_foot) / len(adjacent_foot)) if adjacent_foot else 0.0,
        "adjacent_rgba_mean_abs_min": float(min(adjacent_rgba)) if adjacent_rgba else 0.0,
        "adjacent_rgba_mean_abs_mean": float(sum(adjacent_rgba) / len(adjacent_rgba)) if adjacent_rgba else 0.0,
    }

    warnings: list[str] = []
    if missing:
        warnings.append(f"missing runtime frame indices: {missing}")
    if not contiguous:
        warnings.append(f"non-contiguous runtime indices: {indices}")
    if not source_exists:
        warnings.append("missing final source strip")
    elif source_size != (SOURCE_SLOT_SIZE[0] * expected_count, SOURCE_SLOT_SIZE[1]):
        warnings.append(f"source strip size mismatch: {source_size}")
    if duplicate_pairs:
        warnings.append(f"exact duplicate runtime frame pairs: {', '.join(duplicate_pairs)}")
    if near_duplicate_pairs:
        warnings.append(f"near-duplicate runtime frame pairs: {', '.join(near_duplicate_pairs[:8])}")
    if summary["adjacent_foot_xor_min"] < 120.0:
        warnings.append("at least one adjacent pair has weak foot-region change")
    if summary["foot_area_range"] < 90.0:
        warnings.append("foot-region area range is low")

    return AnimationReport(
        animation=animation,
        frame_count=len(indexed_paths),
        expected_count=expected_count,
        contiguous=contiguous,
        missing_indices=missing,
        source_strip_exists=source_exists,
        source_strip_size=source_size,
        duplicate_pairs=duplicate_pairs,
        near_duplicate_pairs=near_duplicate_pairs,
        frame_metrics=metrics,
        adjacent_metrics=adjacent,
        summary=summary,
        warnings=warnings,
    )


def diagonal_parent_similarity() -> dict[str, list[dict[str, float | int]]]:
    output: dict[str, list[dict[str, float | int]]] = {}
    loaded: dict[str, list[Image.Image]] = {}
    for animation in set(DIAGONAL_PARENTS) | set(DIAGONAL_PARENTS.values()):
        loaded[animation] = [Image.open(path).convert("RGBA") for _idx, path in frame_paths(animation)]
    for diagonal, parent in DIAGONAL_PARENTS.items():
        rows: list[dict[str, float | int]] = []
        for idx, (diag, base) in enumerate(zip(loaded[diagonal], loaded[parent])):
            rows.append({"frame": idx, "similarity_to_parent": pair_similarity(diag, base)})
        output[diagonal] = rows
    return output


def sit_coverage() -> dict[str, object]:
    available = {animation: len(frame_paths(animation)) for animation in SIT_ANIMS if frame_paths(animation)}
    expected_directional = [
        "player_sit_down_down",
        "player_sit_down_up",
        "player_sit_idle_down",
        "player_sit_idle_up",
        "player_stand_up_down",
        "player_stand_up_up",
    ]
    directional_present = [name for name in expected_directional if frame_paths(name)]
    return {
        "available_animations": available,
        "front_back_directional_present": directional_present,
        "front_back_directional_missing": [name for name in expected_directional if name not in directional_present],
    }


def write_markdown(payload: dict[str, object]) -> None:
    lines: list[str] = []
    lines.append("# Protagonist Walk Frame Diagnostics")
    lines.append("")
    lines.append("## Evidence Scan")
    evidence = payload["evidence_scan"]
    assert isinstance(evidence, dict)
    for key, value in evidence.items():
        lines.append(f"- {key}: {value}")
    lines.append("")

    lines.append("## Walk Summary")
    lines.append(
        "| animation | frames | contiguous | foot area | foot center range | min adjacent foot xor | mean adjacent rgba diff | warnings |"
    )
    lines.append("| --- | ---: | --- | --- | ---: | ---: | ---: | --- |")
    for report in payload["walk_reports"]:
        assert isinstance(report, dict)
        summary = report["summary"]
        assert isinstance(summary, dict)
        warnings = report["warnings"]
        assert isinstance(warnings, list)
        lines.append(
            "| {animation} | {frame_count}/{expected_count} | {contiguous} | {foot_area_min:.0f}-{foot_area_max:.0f} | {foot_center_range:.2f} | {adjacent_foot_xor_min:.0f} | {adjacent_rgba_mean_abs_mean:.2f} | {warnings} |".format(
                animation=report["animation"],
                frame_count=report["frame_count"],
                expected_count=report["expected_count"],
                contiguous=str(report["contiguous"]).lower(),
                foot_area_min=summary["foot_area_min"],
                foot_area_max=summary["foot_area_max"],
                foot_center_range=summary["foot_center_range"],
                adjacent_foot_xor_min=summary["adjacent_foot_xor_min"],
                adjacent_rgba_mean_abs_mean=summary["adjacent_rgba_mean_abs_mean"],
                warnings=", ".join(warnings) if warnings else "none",
            )
        )
    lines.append("")

    lines.append("## Diagonal Parent Similarity")
    lines.append("| diagonal | parent | min similarity | max similarity | mean similarity |")
    lines.append("| --- | --- | ---: | ---: | ---: |")
    parent_similarity = payload["diagonal_parent_similarity"]
    assert isinstance(parent_similarity, dict)
    for diagonal, rows in parent_similarity.items():
        parent = DIAGONAL_PARENTS[str(diagonal)]
        assert isinstance(rows, list)
        values = [float(row["similarity_to_parent"]) for row in rows]
        lines.append(
            f"| {diagonal} | {parent} | {min(values):.4f} | {max(values):.4f} | {sum(values) / len(values):.4f} |"
        )
    lines.append("")

    lines.append("## Sit Coverage")
    sit = payload["sit_coverage"]
    assert isinstance(sit, dict)
    for key, value in sit.items():
        lines.append(f"- {key}: {value}")
    lines.append("")

    lines.append("## Per-Frame Diagonal Metrics")
    for report in payload["walk_reports"]:
        assert isinstance(report, dict)
        animation = str(report["animation"])
        if animation not in DIAGONAL_PARENTS:
            continue
        lines.append(f"### {animation}")
        lines.append("| frame | bbox | foot bbox | foot area | foot center x | hash |")
        lines.append("| ---: | --- | --- | ---: | ---: | --- |")
        for metric in report["frame_metrics"]:
            assert isinstance(metric, dict)
            lines.append(
                "| {frame:02d} | {bbox} | {foot_bbox} | {foot_area} | {foot_center_x} | {sha256_12} |".format(
                    frame=metric["frame"],
                    bbox=metric["bbox"],
                    foot_bbox=metric["foot_bbox"],
                    foot_area=metric["foot_area"],
                    foot_center_x="none" if metric["foot_center_x"] is None else f"{float(metric['foot_center_x']):.2f}",
                    sha256_12=metric["sha256_12"],
                )
            )
        lines.append("")
        lines.append("| adjacent pair | alpha xor | foot xor | rgba mean abs | alpha IoU | similarity |")
        lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
        for metric in report["adjacent_metrics"]:
            assert isinstance(metric, dict)
            lines.append(
                "| {pair} | {alpha_xor} | {foot_xor} | {rgba_mean_abs:.2f} | {alpha_iou:.4f} | {similarity:.4f} |".format(
                    pair=metric["pair"],
                    alpha_xor=metric["alpha_xor"],
                    foot_xor=metric["foot_xor"],
                    rgba_mean_abs=metric["rgba_mean_abs"],
                    alpha_iou=metric["alpha_iou"],
                    similarity=metric["similarity"],
                )
            )
        lines.append("")

    MD_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    walk_reports = [animation_report(animation) for animation in WALK_ANIMS]
    evidence_scan = {
        "runtime_frame_dir": str(FRAME_DIR.relative_to(ROOT)),
        "final_source_strip_dir": str(FINAL_STRIP_DIR.relative_to(ROOT)),
        "preview_files_checked": [
            ".codex/protagonist_launch_quality_full_preview.png",
            ".codex/protagonist_redesign_motion_preview.png",
            ".codex/protagonist_redesign_runtime_scene_preview.png",
            ".codex/region_home_area_walk_01_default_spawn.png",
        ],
        "existing_quality_gate_scope": "validate_protagonist_final_asset_quality.py validates source strip coverage, diagonal ghost ratio, and side left/right lower-body motion; it does not score diagonal gait richness.",
    }
    payload = {
        "evidence_scan": evidence_scan,
        "walk_reports": [asdict(report) for report in walk_reports],
        "diagonal_parent_similarity": diagonal_parent_similarity(),
        "sit_coverage": sit_coverage(),
    }
    JSON_REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(payload)

    warnings = [
        f"{report.animation}: {'; '.join(report.warnings)}"
        for report in walk_reports
        if report.warnings
    ]
    print(f"OK: wrote {JSON_REPORT.relative_to(ROOT)}")
    print(f"OK: wrote {MD_REPORT.relative_to(ROOT)}")
    if warnings:
        print("WARNINGS:")
        for warning in warnings:
            print(f"- {warning}")
    else:
        print("OK: no missing, non-contiguous, duplicate, or weak-foot-change walk frames detected")


if __name__ == "__main__":
    main()
