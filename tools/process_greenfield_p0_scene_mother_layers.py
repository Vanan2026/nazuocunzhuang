from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageStat


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = (
    ROOT
    / "production"
    / "assets"
    / "external_gpt_handoff"
    / "greenfield_p0_v001_qualified_scenes_partial"
)
DEFAULT_INCOMING = (
    ROOT
    / "production"
    / "assets"
    / "external_gpt_handoff"
    / "greenfield_p0"
    / "v001"
    / "incoming"
)


@dataclass(frozen=True)
class Shape:
    kind: str
    category: str
    points: tuple[tuple[float, float], ...] = ()
    box: tuple[float, float, float, float] | None = None
    width: float = 0.0


MASKS: dict[str, tuple[Shape, ...]] = {
    "back_farm": (
        Shape("polygon", "house_front_eave", ((0.42, 0.165), (0.57, 0.19), (0.56, 0.245), (0.405, 0.225))),
        Shape("polygon", "tree_canopy_front_edge", ((0.03, 0.16), (0.22, 0.13), (0.27, 0.25), (0.15, 0.32), (0.02, 0.29))),
        Shape("polygon", "tree_canopy_front_edge", ((0.80, 0.06), (0.97, 0.11), (0.95, 0.25), (0.79, 0.24))),
        Shape("line", "fence_front_rail", ((0.55, 0.47), (0.78, 0.44), (0.91, 0.51)), width=0.018),
        Shape("line", "fence_front_rail", ((0.19, 0.71), (0.44, 0.72), (0.56, 0.79)), width=0.018),
        Shape("line", "crop_bed_front_edge", ((0.17, 0.55), (0.39, 0.57)), width=0.016),
        Shape("line", "crop_bed_front_edge", ((0.47, 0.55), (0.70, 0.56)), width=0.016),
        Shape("ellipse", "well_front_rim", box=(0.66, 0.58, 0.73, 0.66)),
        Shape("line", "bridge_front_rail", ((0.88, 0.54), (0.97, 0.47)), width=0.018),
        Shape("polygon", "shrub_front_edge", ((0.00, 0.83), (0.22, 0.80), (0.30, 0.96), (0.04, 0.98))),
    ),
    "cliff_view": (
        Shape("line", "cliff_front_edge", ((0.00, 0.58), (0.25, 0.55), (0.46, 0.54), (0.70, 0.56), (1.00, 0.59)), width=0.035),
        Shape("polygon", "wood_platform_front_edge", ((0.64, 0.53), (0.83, 0.54), (0.84, 0.64), (0.64, 0.63))),
        Shape("line", "fence_front_rail", ((0.02, 0.51), (0.22, 0.49), (0.46, 0.50), (0.65, 0.52)), width=0.015),
        Shape("polygon", "tree_canopy_front_edge", ((0.00, 0.06), (0.19, 0.04), (0.22, 0.20), (0.02, 0.24))),
        Shape("polygon", "tree_canopy_front_edge", ((0.79, 0.07), (1.00, 0.07), (1.00, 0.25), (0.80, 0.24))),
        Shape("polygon", "tall_grass_front_edge", ((0.70, 0.45), (0.86, 0.44), (0.91, 0.52), (0.75, 0.53))),
        Shape("line", "bench_or_prop_front_edge", ((0.53, 0.53), (0.61, 0.53)), width=0.014),
    ),
    "forest_edge": (
        Shape("polygon", "tree_canopy_front_edge", ((0.00, 0.07), (0.23, 0.05), (0.27, 0.22), (0.07, 0.28), (0.00, 0.22))),
        Shape("polygon", "tree_canopy_front_edge", ((0.68, 0.05), (1.00, 0.05), (0.99, 0.26), (0.73, 0.28))),
        Shape("polygon", "tree_canopy_front_edge", ((0.61, 0.75), (0.93, 0.73), (1.00, 0.93), (0.71, 0.98))),
        Shape("polygon", "shrub_front_edge", ((0.37, 0.15), (0.57, 0.14), (0.60, 0.25), (0.39, 0.27))),
        Shape("polygon", "shrub_front_edge", ((0.29, 0.59), (0.48, 0.60), (0.53, 0.72), (0.33, 0.74))),
        Shape("line", "fence_front_rail", ((0.00, 0.69), (0.16, 0.62), (0.29, 0.60)), width=0.016),
        Shape("line", "log_front_edge", ((0.60, 0.73), (0.78, 0.76)), width=0.025),
        Shape("ellipse", "rock_front_edge", box=(0.72, 0.52, 0.80, 0.60)),
        Shape("line", "sign_front_edge", ((0.17, 0.49), (0.23, 0.50)), width=0.018),
    ),
    "home_area": (
        Shape("polygon", "house_front_eave", ((0.42, 0.17), (0.58, 0.20), (0.565, 0.255), (0.405, 0.23))),
        Shape("polygon", "tree_canopy_front_edge", ((0.04, 0.13), (0.24, 0.08), (0.28, 0.24), (0.09, 0.31), (0.00, 0.25))),
        Shape("polygon", "tree_canopy_front_edge", ((0.82, 0.05), (1.00, 0.10), (0.98, 0.31), (0.82, 0.27))),
        Shape("line", "fence_front_rail", ((0.56, 0.49), (0.75, 0.47), (0.88, 0.55)), width=0.018),
        Shape("line", "fence_front_rail", ((0.19, 0.71), (0.41, 0.72), (0.53, 0.78)), width=0.018),
        Shape("line", "crop_bed_front_edge", ((0.43, 0.58), (0.65, 0.59)), width=0.016),
        Shape("ellipse", "well_front_rim", box=(0.65, 0.56, 0.73, 0.65)),
        Shape("line", "bridge_front_rail", ((0.88, 0.53), (0.97, 0.46)), width=0.018),
        Shape("line", "bench_or_prop_front_edge", ((0.11, 0.63), (0.24, 0.62)), width=0.018),
        Shape("polygon", "shrub_front_edge", ((0.00, 0.82), (0.20, 0.78), (0.28, 0.94), (0.04, 0.98))),
    ),
    "mountain": (
        Shape("polygon", "tree_canopy_front_edge", ((0.00, 0.08), (0.24, 0.06), (0.28, 0.24), (0.07, 0.30), (0.00, 0.24))),
        Shape("polygon", "tree_canopy_front_edge", ((0.67, 0.06), (1.00, 0.04), (1.00, 0.24), (0.73, 0.27))),
        Shape("polygon", "tree_canopy_front_edge", ((0.00, 0.76), (0.23, 0.71), (0.29, 0.92), (0.03, 0.99))),
        Shape("line", "bridge_front_rail", ((0.82, 0.56), (0.94, 0.48)), width=0.019),
        Shape("line", "rock_front_edge", ((0.62, 0.65), (0.75, 0.62), (0.86, 0.67)), width=0.025),
        Shape("polygon", "shrub_front_edge", ((0.34, 0.58), (0.50, 0.58), (0.55, 0.70), (0.38, 0.72))),
        Shape("line", "stream_bank_front_edge", ((0.76, 0.51), (0.86, 0.48), (0.94, 0.43)), width=0.018),
        Shape("line", "sign_front_edge", ((0.35, 0.47), (0.42, 0.48)), width=0.016),
    ),
    "mountain_hut": (
        Shape("polygon", "house_front_eave", ((0.43, 0.17), (0.59, 0.20), (0.58, 0.27), (0.42, 0.25))),
        Shape("polygon", "tree_canopy_front_edge", ((0.00, 0.08), (0.22, 0.05), (0.27, 0.24), (0.07, 0.30), (0.00, 0.23))),
        Shape("polygon", "tree_canopy_front_edge", ((0.70, 0.06), (1.00, 0.05), (1.00, 0.27), (0.73, 0.29))),
        Shape("polygon", "shrub_front_edge", ((0.18, 0.62), (0.38, 0.62), (0.43, 0.75), (0.22, 0.77))),
        Shape("line", "woodpile_front_edge", ((0.61, 0.68), (0.78, 0.70)), width=0.026),
        Shape("line", "fence_front_rail", ((0.03, 0.66), (0.20, 0.61), (0.35, 0.61)), width=0.017),
        Shape("line", "rock_front_edge", ((0.73, 0.55), (0.88, 0.58)), width=0.024),
    ),
    "mountain_path": (
        Shape("polygon", "tree_canopy_front_edge", ((0.00, 0.08), (0.22, 0.05), (0.27, 0.24), (0.07, 0.31), (0.00, 0.23))),
        Shape("polygon", "tree_canopy_front_edge", ((0.68, 0.06), (1.00, 0.05), (1.00, 0.26), (0.72, 0.29))),
        Shape("polygon", "tree_canopy_front_edge", ((0.00, 0.76), (0.24, 0.70), (0.29, 0.91), (0.03, 0.99))),
        Shape("line", "cliff_front_edge", ((0.58, 0.53), (0.70, 0.50), (0.84, 0.56), (0.96, 0.66)), width=0.03),
        Shape("line", "rock_front_edge", ((0.56, 0.76), (0.75, 0.78), (0.90, 0.83)), width=0.026),
        Shape("polygon", "shrub_front_edge", ((0.35, 0.57), (0.50, 0.57), (0.55, 0.70), (0.38, 0.72))),
        Shape("line", "sign_front_edge", ((0.36, 0.47), (0.43, 0.48)), width=0.016),
    ),
    "orchard": (
        Shape("polygon", "tree_canopy_front_edge", ((0.10, 0.08), (0.34, 0.06), (0.38, 0.28), (0.17, 0.31))),
        Shape("polygon", "tree_canopy_front_edge", ((0.55, 0.06), (0.82, 0.08), (0.84, 0.31), (0.58, 0.30))),
        Shape("polygon", "tree_canopy_front_edge", ((0.12, 0.40), (0.38, 0.39), (0.40, 0.64), (0.15, 0.66))),
        Shape("polygon", "tree_canopy_front_edge", ((0.54, 0.39), (0.82, 0.39), (0.84, 0.66), (0.56, 0.65))),
        Shape("polygon", "tree_canopy_front_edge", ((0.25, 0.70), (0.50, 0.68), (0.53, 0.92), (0.28, 0.95))),
        Shape("polygon", "tree_canopy_front_edge", ((0.70, 0.72), (0.98, 0.70), (1.00, 0.95), (0.75, 0.98))),
        Shape("line", "fence_front_rail", ((0.00, 0.71), (0.23, 0.68), (0.40, 0.72)), width=0.015),
        Shape("line", "crate_or_basket_front_edge", ((0.44, 0.46), (0.50, 0.47)), width=0.018),
        Shape("ellipse", "well_front_rim", box=(0.07, 0.72, 0.15, 0.80)),
    ),
    "pond": (
        Shape("line", "dock_front_edge", ((0.58, 0.25), (0.72, 0.18)), width=0.025),
        Shape("polygon", "tall_grass_front_edge", ((0.00, 0.78), (0.25, 0.75), (0.31, 0.95), (0.02, 0.99))),
        Shape("polygon", "tall_grass_front_edge", ((0.71, 0.73), (1.00, 0.72), (1.00, 0.96), (0.76, 0.98))),
        Shape("line", "rock_front_edge", ((0.06, 0.54), (0.18, 0.59), (0.28, 0.62)), width=0.022),
        Shape("line", "rock_front_edge", ((0.61, 0.66), (0.78, 0.64), (0.93, 0.68)), width=0.022),
        Shape("line", "reed_front_edge", ((0.13, 0.39), (0.22, 0.41)), width=0.02),
        Shape("line", "reed_front_edge", ((0.77, 0.44), (0.89, 0.45)), width=0.02),
        Shape("polygon", "shrub_front_edge", ((0.00, 0.06), (0.16, 0.04), (0.22, 0.18), (0.02, 0.23))),
    ),
    "village": (
        Shape("polygon", "house_front_eave", ((0.13, 0.19), (0.26, 0.22), (0.25, 0.30), (0.12, 0.28))),
        Shape("polygon", "house_front_eave", ((0.49, 0.16), (0.62, 0.19), (0.61, 0.27), (0.48, 0.25))),
        Shape("polygon", "house_front_eave", ((0.80, 0.30), (0.94, 0.33), (0.93, 0.43), (0.79, 0.41))),
        Shape("polygon", "house_front_eave", ((0.19, 0.71), (0.34, 0.73), (0.33, 0.84), (0.18, 0.82))),
        Shape("line", "fence_front_rail", ((0.13, 0.43), (0.31, 0.43), (0.43, 0.50)), width=0.017),
        Shape("line", "fence_front_rail", ((0.43, 0.76), (0.61, 0.78), (0.72, 0.86)), width=0.017),
        Shape("line", "bridge_front_rail", ((0.00, 0.79), (0.12, 0.71)), width=0.02),
        Shape("ellipse", "well_front_rim", box=(0.49, 0.50, 0.58, 0.60)),
        Shape("line", "crop_bed_front_edge", ((0.46, 0.79), (0.65, 0.81)), width=0.016),
        Shape("polygon", "tree_canopy_front_edge", ((0.30, 0.00), (0.48, 0.04), (0.47, 0.20), (0.31, 0.20))),
        Shape("polygon", "tree_canopy_front_edge", ((0.00, 0.59), (0.15, 0.54), (0.22, 0.71), (0.04, 0.78))),
    ),
}


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def sha16(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def opaque_rgba(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    if alpha.getextrema() != (255, 255):
        base = Image.new("RGBA", rgba.size, (0, 0, 0, 255))
        base.alpha_composite(rgba)
        return base
    return rgba


def scaled_points(points: Iterable[tuple[float, float]], size: tuple[int, int], scale: int) -> list[tuple[int, int]]:
    width, height = size
    return [(round(x * width * scale), round(y * height * scale)) for x, y in points]


def scaled_box(box: tuple[float, float, float, float], size: tuple[int, int], scale: int) -> tuple[int, int, int, int]:
    width, height = size
    x0, y0, x1, y1 = box
    return (
        round(x0 * width * scale),
        round(y0 * height * scale),
        round(x1 * width * scale),
        round(y1 * height * scale),
    )


def draw_mask(region: str, size: tuple[int, int], scale: int = 3) -> tuple[Image.Image, dict[str, int], list[dict]]:
    shapes = MASKS.get(region)
    if not shapes:
        fail(f"missing mask definitions for region: {region}")

    big = Image.new("L", (size[0] * scale, size[1] * scale), 0)
    category_count: dict[str, int] = {}
    pixel_regions: list[dict] = []

    def front_edge_width(category: str) -> float:
        return {
            "house_front_eave": 0.014,
            "tree_canopy_front_edge": 0.018,
            "shrub_front_edge": 0.014,
            "tall_grass_front_edge": 0.012,
            "wood_platform_front_edge": 0.014,
        }.get(category, 0.014)

    def polygon_front_edge(points: list[tuple[int, int]]) -> list[tuple[int, int]]:
        y_values = [point[1] for point in points]
        y0 = min(y_values)
        y1 = max(y_values)
        threshold = y0 + (y1 - y0) * 0.60
        front_points = [point for point in points if point[1] >= threshold]
        if len(front_points) < 2:
            front_points = sorted(points, key=lambda point: point[1], reverse=True)[:2]
        return sorted(front_points, key=lambda point: point[0])

    for shape_index, shape in enumerate(shapes):
        category_count[shape.category] = category_count.get(shape.category, 0) + 1
        shape_layer = Image.new("L", big.size, 0)
        draw = ImageDraw.Draw(shape_layer)
        if shape.kind == "polygon":
            points = scaled_points(shape.points, size, scale)
            front_points = polygon_front_edge(points)
            if len(front_points) >= 2:
                draw.line(
                    front_points,
                    fill=255,
                    width=max(1, round(front_edge_width(shape.category) * size[1] * scale)),
                    joint="curve",
                )
        elif shape.kind == "line":
            draw.line(
                scaled_points(shape.points, size, scale),
                fill=255,
                width=max(1, round(shape.width * size[1] * scale)),
                joint="curve",
            )
        elif shape.kind == "ellipse":
            if shape.box is None:
                fail(f"ellipse without box for {region}")
            draw.ellipse(scaled_box(shape.box, size, scale), fill=255)
            x0, y0, x1, y1 = scaled_box(shape.box, size, scale)
            draw.rectangle((x0, y0, x1, round((y0 + y1) / 2)), fill=0)
        else:
            fail(f"unknown mask shape kind: {shape.kind}")
        small_shape = shape_layer.resize(size, Image.Resampling.LANCZOS)
        bbox = small_shape.getbbox()
        pixel_count = int(np.count_nonzero(np.array(small_shape)))
        if bbox and pixel_count > 0:
            pixel_regions.append(
                {
                    "index": shape_index,
                    "category": shape.category,
                    "bbox": list(bbox),
                    "nontransparent_pixels": pixel_count,
                }
            )
        big = ImageChops.lighter(big, shape_layer)

    mask = big.resize(size, Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(0.8))
    mask = mask.point(lambda value: 0 if value < 20 else min(255, int(value * 1.08)))
    return mask, category_count, pixel_regions


def inpaint_base(mother: Image.Image, mask: Image.Image) -> Image.Image:
    rgb = mother.convert("RGB")
    arr = np.array(rgb).astype(np.float32)
    mask_arr = np.array(mask).astype(np.float32) / 255.0
    height, width = mask_arr.shape

    yy = np.arange(height)[:, None]
    xx = np.arange(width)[None, :]
    offsets = [22, 36, 52, -24, 0]
    samples = []
    weights = []
    binary = mask_arr > 0.02
    for index, offset in enumerate(offsets):
        sy = np.clip(yy + offset, 0, height - 1)
        sample = arr[sy, xx]
        valid = (~binary[sy, xx]).astype(np.float32)
        weight = valid * (1.0 / (index + 1))
        samples.append(sample * weight[..., None])
        weights.append(weight)

    sample_sum = np.sum(samples, axis=0)
    weight_sum = np.sum(weights, axis=0)
    fallback = np.array(rgb.filter(ImageFilter.GaussianBlur(14))).astype(np.float32)
    filled = np.where(weight_sum[..., None] > 0.0, sample_sum / np.maximum(weight_sum[..., None], 1e-6), fallback)
    filled_img = Image.fromarray(np.clip(filled, 0, 255).astype(np.uint8), "RGB").filter(ImageFilter.GaussianBlur(1.2))
    filled_arr = np.array(filled_img).astype(np.float32)

    blend = np.clip(mask_arr[..., None], 0.0, 1.0)
    out = arr * (1.0 - blend) + filled_arr * blend
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def composite_mean_diff(mother: Image.Image, base: Image.Image, foreground: Image.Image) -> float:
    comp = Image.alpha_composite(base.convert("RGBA"), foreground.convert("RGBA"))
    diff = ImageChops.difference(mother.convert("RGB"), comp.convert("RGB"))
    stat = ImageStat.Stat(diff)
    return float(sum(stat.mean) / 3.0)


def save_checker_preview(
    region: str,
    mother: Image.Image,
    base: Image.Image,
    foreground: Image.Image,
    destination: Path,
) -> None:
    checker = Image.new("RGBA", mother.size, (238, 238, 238, 255))
    pixels = checker.load()
    step = 32
    for y in range(0, mother.size[1], step):
        for x in range(0, mother.size[0], step):
            if (x // step + y // step) % 2:
                for yy in range(y, min(y + step, mother.size[1])):
                    for xx in range(x, min(x + step, mother.size[0])):
                        pixels[xx, yy] = (202, 202, 202, 255)

    panels = []
    for label, image in (
        ("mother", mother),
        ("base", base),
        ("foreground", Image.alpha_composite(checker, foreground)),
        ("composite", Image.alpha_composite(base, foreground)),
    ):
        thumb = image.convert("RGB")
        thumb.thumbnail((320, 220), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (340, 260), "white")
        tile.paste(thumb, ((340 - thumb.width) // 2, 10))
        draw = ImageDraw.Draw(tile)
        draw.text((10, 235), f"{region} {label}", fill=(20, 20, 20))
        panels.append(tile)

    sheet = Image.new("RGB", (len(panels) * 340, 260), (230, 230, 230))
    for index, tile in enumerate(panels):
        sheet.paste(tile, (index * 340, 0))
    sheet.save(destination)


def process(source: Path) -> dict:
    mothers = sorted((source / "01_scene_mothers" / "regions").glob("*/*_scene_mother.png"))
    if len(mothers) != 10:
        fail(f"expected 10 scene mothers, found {len(mothers)}")

    base_root = source / "02_scene_base" / "regions"
    foreground_root = source / "03_foreground_occlusion" / "regions"
    audit_root = source / "04_audit"
    preview_root = audit_root / "previews"
    base_root.mkdir(parents=True, exist_ok=True)
    foreground_root.mkdir(parents=True, exist_ok=True)
    audit_root.mkdir(parents=True, exist_ok=True)
    preview_root.mkdir(parents=True, exist_ok=True)

    regions = {}
    for mother_path in mothers:
        region = mother_path.parent.name
        mother = opaque_rgba(Image.open(mother_path))
        mask, category_count, pixel_regions = draw_mask(region, mother.size)

        foreground = mother.copy()
        foreground.putalpha(mask)
        base = inpaint_base(mother, mask)

        base_path = base_root / region / f"{region}_base.png"
        foreground_path = foreground_root / region / f"{region}_foreground_occlusion.png"
        base_path.parent.mkdir(parents=True, exist_ok=True)
        foreground_path.parent.mkdir(parents=True, exist_ok=True)
        base.save(base_path)
        foreground.save(foreground_path)

        alpha = foreground.getchannel("A")
        alpha_extrema = alpha.getextrema()
        foreground_pixels = int(np.count_nonzero(np.array(alpha)))
        mean_diff = composite_mean_diff(mother, base, foreground)

        checks = {
            "same_size": mother.size == base.size == foreground.size,
            "mother_opaque": mother.getchannel("A").getextrema() == (255, 255),
            "base_opaque": base.getchannel("A").getextrema() == (255, 255),
            "foreground_rgba": foreground.mode == "RGBA",
            "foreground_alpha_effective": alpha_extrema[0] == 0 and alpha_extrema[1] == 255 and foreground_pixels > 0,
            "foreground_full_canvas": foreground.size == mother.size,
            "composite_mean_diff_under_2": mean_diff < 2.0,
        }

        preview_path = preview_root / f"{region}_scene_layer_preview.png"
        save_checker_preview(region, mother, base, foreground, preview_path)

        regions[region] = {
            "region": region,
            "image_size": list(mother.size),
            "files": {
                "scene_mother": str(mother_path.relative_to(source)).replace("\\", "/"),
                "base": str(base_path.relative_to(source)).replace("\\", "/"),
                "foreground_occlusion": str(foreground_path.relative_to(source)).replace("\\", "/"),
                "preview": str(preview_path.relative_to(source)).replace("\\", "/"),
            },
            "sha16": {
                "scene_mother": sha16(mother_path),
                "base": sha16(base_path),
                "foreground_occlusion": sha16(foreground_path),
            },
            "foreground_pixel_categories": sorted(category_count),
            "foreground_pixel_regions": pixel_regions,
            "foreground_shape_counts": category_count,
            "foreground_nontransparent_pixels": foreground_pixels,
            "foreground_alpha_range": list(alpha_extrema),
            "composite_mean_rgb_diff": round(mean_diff, 4),
            "checks": checks,
            "known_issues": [
                "Foreground/base are deterministic technical masks from the supplied scene mother, not a hand-painted semantic split; human art review is still required.",
                "Base inpaint only covers the removed occlusion pixels and is optimized for runtime recomposition with foreground enabled.",
            ],
        }

    audit = {
        "package": "greenfield_p0_v001_scene_mother_layers",
        "source_dir": source.relative_to(ROOT).as_posix() if source.is_relative_to(ROOT) else source.name,
        "region_count": len(regions),
        "checks_summary": {
            "all_same_size_per_region": all(item["checks"]["same_size"] for item in regions.values()),
            "all_mothers_opaque": all(item["checks"]["mother_opaque"] for item in regions.values()),
            "all_bases_opaque": all(item["checks"]["base_opaque"] for item in regions.values()),
            "all_foregrounds_rgba_effective": all(
                item["checks"]["foreground_rgba"] and item["checks"]["foreground_alpha_effective"]
                for item in regions.values()
            ),
            "all_composites_close": all(item["checks"]["composite_mean_diff_under_2"] for item in regions.values()),
        },
        "regions": regions,
    }
    audit_path = audit_root / "scene_mother_layers.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    return audit


def move_to_incoming(source: Path, incoming: Path) -> None:
    moved_items = [
        "01_scene_mothers",
        "02_scene_base",
        "03_foreground_occlusion",
        "04_audit",
    ]
    incoming.mkdir(parents=True, exist_ok=True)
    for item in moved_items:
        src = source / item
        dst = incoming / item
        if not src.exists():
            fail(f"cannot move missing generated item: {src}")
        if dst.exists():
            fail(f"target already exists, refusing to overwrite: {dst}")
        shutil.move(str(src), str(dst))

    if source.exists():
        shutil.rmtree(source)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--incoming", type=Path, default=DEFAULT_INCOMING)
    parser.add_argument("--move", action="store_true", help="move generated assets to the incoming contract folder and delete source")
    args = parser.parse_args()

    source = args.source
    if source == DEFAULT_SOURCE and not source.exists():
        source = DEFAULT_INCOMING

    audit = process(source)
    print(
        "OK: processed scene mother layers "
        f"regions={audit['region_count']} all_close={audit['checks_summary']['all_composites_close']}"
    )
    if args.move:
        move_to_incoming(source, args.incoming)
        print(f"OK: moved final scene layer assets to {args.incoming} and deleted {source}")


if __name__ == "__main__":
    main()
