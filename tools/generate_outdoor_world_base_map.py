from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production" / "assets" / "outdoor_world_world2d" / "v001"
LAYOUT_LOCK = PACKAGE_DIR / "01_world_layout" / "outdoor_world_layout_lock.json"
WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
SOURCE_STRATEGY = PACKAGE_DIR / "02_source_strategy" / "source_generation_strategy.md"
BASE_DIR = PACKAGE_DIR / "02_world_base_no_foreground"
REGION_CROP_DIR = BASE_DIR / "region_base_crops"
WORLD_BASE = BASE_DIR / "outdoor_world_base_no_foreground.png"
WORLD_BASE_PREVIEW = BASE_DIR / "outdoor_world_base_no_foreground_review.png"
BASE_MANIFEST = BASE_DIR / "world_base_manifest.json"
PROJECT_MANIFEST = ROOT / "production" / "assets" / "project_art_production_manifest_2026-05-19.json"

WORLD_CANVAS = (9900, 4950)
PREVIEW_CANVAS = (2200, 1100)
REGION_CANVAS = (1800, 1200)
RNG = random.Random(260526)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ensure_dirs() -> None:
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    REGION_CROP_DIR.mkdir(parents=True, exist_ok=True)


def load_layout() -> dict[str, Any]:
    return read_json(LAYOUT_LOCK)


def world_bounds(layout: dict[str, Any]) -> dict[str, float]:
    return layout["world_bounds"]


def world_to_px(point: tuple[float, float], bounds: dict[str, float]) -> tuple[int, int]:
    x = (point[0] - float(bounds["min_x"])) / float(bounds["width"])
    y = (point[1] - float(bounds["min_y"])) / float(bounds["height"])
    return (
        int(round(x * (WORLD_CANVAS[0] - 1))),
        int(round(y * (WORLD_CANVAS[1] - 1))),
    )


def rect_to_px(rect: list[float], bounds: dict[str, float]) -> tuple[int, int, int, int]:
    x, y, width, height = rect
    left, top = world_to_px((x, y), bounds)
    right, bottom = world_to_px((x + width, y + height), bounds)
    left = max(0, min(WORLD_CANVAS[0] - 1, left))
    top = max(0, min(WORLD_CANVAS[1] - 1, top))
    right = max(left + 1, min(WORLD_CANVAS[0], right))
    bottom = max(top + 1, min(WORLD_CANVAS[1], bottom))
    return (left, top, right, bottom)


def draw_textured_ground(image: Image.Image) -> None:
    pixels = image.load()
    width, height = image.size
    for y in range(height):
        y_mix = y / max(height - 1, 1)
        for x in range(width):
            x_mix = x / max(width - 1, 1)
            wave = math.sin(x * 0.006) * 5 + math.sin((x + y) * 0.003) * 4
            noise = RNG.randint(-8, 8)
            green_shift = int(18 * (1.0 - y_mix) + 10 * math.sin(x_mix * math.pi))
            base = (
                126 + int(wave) + noise,
                148 + green_shift + noise // 2,
                86 + noise // 3,
            )
            pixels[x, y] = base


def draw_region_atmosphere(draw: ImageDraw.ImageDraw, layout: dict[str, Any]) -> None:
    bounds = world_bounds(layout)
    colors = {
        "player_yard": (174, 166, 105, 120),
        "forest_edge": (93, 132, 86, 135),
        "village": (170, 151, 95, 115),
        "back_farm": (150, 134, 83, 110),
        "orchard": (102, 142, 91, 125),
        "pond": (92, 132, 129, 120),
        "mountain_path": (100, 127, 88, 135),
        "mountain_hut": (101, 121, 79, 135),
        "mountain": (90, 108, 97, 140),
        "cliff_view": (118, 126, 121, 130),
    }
    for region in layout["regions"]:
        rect = rect_to_px(region["bounds"], bounds)
        overlay = Image.new("RGBA", WORLD_CANVAS, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rounded_rectangle(rect, radius=80, fill=colors.get(region["region_id"], (120, 140, 100, 105)))
        draw.bitmap((0, 0), overlay)


def draw_roads(image: Image.Image, layout: dict[str, Any]) -> None:
    bounds = world_bounds(layout)
    road_layer = Image.new("RGBA", WORLD_CANVAS, (0, 0, 0, 0))
    road = ImageDraw.Draw(road_layer)
    for connection in layout["connections"]:
        points = [world_to_px((float(x), float(y)), bounds) for x, y in connection["points"]]
        road.line(points, fill=(128, 102, 62, 170), width=210, joint="curve")
        road.line(points, fill=(198, 174, 111, 235), width=130, joint="curve")
        road.line(points, fill=(226, 203, 140, 90), width=58, joint="curve")
    road_layer = road_layer.filter(ImageFilter.GaussianBlur(radius=3.2))
    image.alpha_composite(road_layer)


def draw_region_landmarks(image: Image.Image, layout: dict[str, Any]) -> None:
    bounds = world_bounds(layout)
    layer = Image.new("RGBA", WORLD_CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for region in layout["regions"]:
        region_id = region["region_id"]
        left, top, right, bottom = rect_to_px(region["bounds"], bounds)
        cx = (left + right) // 2
        cy = (top + bottom) // 2
        if region_id == "village":
            draw.ellipse((cx - 250, cy - 160, cx + 250, cy + 150), fill=(166, 141, 86, 150))
            for dx, dy in [(-210, -80), (180, -60), (-40, 110)]:
                draw.rounded_rectangle((cx + dx - 62, cy + dy - 38, cx + dx + 62, cy + dy + 38), radius=16, fill=(125, 91, 57, 180))
        elif region_id == "mountain_hut":
            draw.rounded_rectangle((cx - 120, cy - 70, cx + 125, cy + 78), radius=24, fill=(108, 82, 52, 185))
            draw.polygon([(cx - 155, cy - 55), (cx, cy - 160), (cx + 160, cy - 55)], fill=(62, 79, 72, 190))
        elif region_id == "pond":
            draw.ellipse((cx - 250, cy - 130, cx + 250, cy + 130), fill=(77, 128, 130, 165))
        elif region_id == "back_farm":
            for i in range(4):
                draw.rounded_rectangle((left + 200 + i * 245, top + 240, left + 380 + i * 245, top + 690), radius=18, fill=(130, 105, 66, 140))
        elif region_id in {"forest_edge", "orchard", "mountain_path", "mountain", "cliff_view"}:
            for _ in range(24):
                x = RNG.randint(left + 60, max(left + 61, right - 60))
                y = RNG.randint(top + 60, max(top + 61, bottom - 60))
                r = RNG.randint(38, 78)
                draw.ellipse((x - r, y - r, x + r, y + r), fill=(56, RNG.randint(95, 132), 61, 145))
    image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(radius=1.4)))


def draw_detail_speckles(image: Image.Image) -> None:
    layer = Image.new("RGBA", WORLD_CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for _ in range(9000):
        x = RNG.randrange(WORLD_CANVAS[0])
        y = RNG.randrange(WORLD_CANVAS[1])
        color = RNG.choice([
            (209, 198, 126, 70),
            (93, 120, 66, 70),
            (158, 133, 77, 55),
            (226, 199, 162, 45),
        ])
        radius = RNG.randint(2, 7)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(radius=0.4)))


def write_world_base(layout: dict[str, Any]) -> Image.Image:
    image = Image.new("RGBA", WORLD_CANVAS, (0, 0, 0, 255))
    rgb = Image.new("RGB", WORLD_CANVAS)
    draw_textured_ground(rgb)
    image = rgb.convert("RGBA")
    draw_region_atmosphere(ImageDraw.Draw(image, "RGBA"), layout)
    draw_roads(image, layout)
    draw_region_landmarks(image, layout)
    draw_detail_speckles(image)
    # No foreground tree crowns or near-camera occluders are drawn here by design.
    image.convert("RGB").save(WORLD_BASE)
    preview = image.resize(PREVIEW_CANVAS, Image.Resampling.BICUBIC)
    preview.save(WORLD_BASE_PREVIEW)
    return image.convert("RGB")


def write_region_crops(layout: dict[str, Any], world_image: Image.Image) -> list[dict[str, Any]]:
    bounds = world_bounds(layout)
    crops: list[dict[str, Any]] = []
    for region in layout["regions"]:
        region_id = region["region_id"]
        crop_box = rect_to_px(region["bounds"], bounds)
        crop = world_image.crop(crop_box).resize(REGION_CANVAS, Image.Resampling.BICUBIC)
        path = REGION_CROP_DIR / f"{region_id}_base_no_foreground.png"
        crop.save(path)
        crops.append(
            {
                "region_id": region_id,
                "display_name": region["display_name"],
                "path": rel(path),
                "derived_from": rel(WORLD_BASE),
                "canvas": list(REGION_CANVAS),
                "world_base_crop_box": list(crop_box),
                "runtime_bounds": region["bounds"],
                "foreground_removed": True,
                "repaint_status": "base_crop_only_not_final_scene_art",
                "next_step": "Use this inherited crop as the first layer/reference for high-quality region repaint.",
            }
        )
    return crops


def write_base_manifest(region_crops: list[dict[str, Any]]) -> None:
    write_json(
        BASE_MANIFEST,
        {
            "package_id": "outdoor_world_base_no_foreground_v001",
            "status": "world_base_no_foreground_ready_for_region_crop_review",
            "world_base_image": rel(WORLD_BASE),
            "review_preview": rel(WORLD_BASE_PREVIEW),
            "world_canvas": list(WORLD_CANVAS),
            "region_canvas": list(REGION_CANVAS),
            "runtime_replacement": False,
            "launch_quality_approved": False,
            "foreground_policy": "foreground_occlusion_is_per_region_separate_layer",
            "high_quality_region_rule": "region repaint starts from inherited world_base crop",
            "region_crops": region_crops,
            "notes": [
                "This whole-world base is a no-foreground continuity scaffold, not final art.",
                "Per-region high-quality scene work must inherit roads, terrain hue, lighting, and edge continuity from these crops.",
                "Foreground occlusion remains a separate per-region layer produced after the base scene is accepted.",
            ],
        },
    )


def update_workflow() -> None:
    workflow = read_json(WORKFLOW)
    workflow["current_phase"] = "02_world_base_no_foreground"
    workflow["purpose"] = "Global seamless 2D art contract and rough whole-world no-foreground base before final per-region painted sources."
    workflow.setdefault("artifacts", {})["world_base_no_foreground"] = rel(WORLD_BASE)
    workflow.setdefault("artifacts", {})["world_base_review_preview"] = rel(WORLD_BASE_PREVIEW)
    workflow.setdefault("artifacts", {})["world_base_manifest"] = rel(BASE_MANIFEST)
    workflow.setdefault("artifacts", {})["region_base_crops_dir"] = rel(REGION_CROP_DIR)
    decision = workflow.setdefault("art_pipeline_decision", {})
    decision["pipeline"] = "world_blueprint_to_world_base_to_region_crops_to_foreground_layers"
    decision["reason"] = "Isolated high-quality regions produced obvious seams; the base world must read as one map before region detail passes."
    decision["world_base_rule"] = "Produce the whole no-foreground map first, even if rough."
    decision["single_region_repaint_rule"] = "must inherit from world_base crop"
    decision["foreground_rule"] = "foreground occlusion is authored per region only after base continuity is accepted"
    workflow.setdefault("validation", {})["world_base_validator"] = "tools/validate_outdoor_world_base_map_pipeline.py"
    write_json(WORKFLOW, workflow)


def update_source_strategy() -> None:
    SOURCE_STRATEGY.write_text(
        """# Source Generation Strategy

## Corrected Pipeline

The current project uses one seamless 2D `OutdoorWorld`, so art production must start from world continuity rather than isolated region beauty.

1. Keep the world blueprint as the spatial contract.
2. Produce one `world_base_no_foreground` whole-world base. It may be lower precision, but it must unify roads, ground hue, lighting, and region relationships.
3. Export `region crop` base images from that whole-world base.
4. Every high-quality region repaint must start from the inherited crop and must not independently recompose region bases.
5. Add `foreground_occlusion` as a separate per-region layer only after the region base is accepted.
6. Validate layer registration and Godot screenshots before runtime replacement.

## Current Base-Map Artifacts

- Whole-world base: `production/assets/outdoor_world_world2d/v001/02_world_base_no_foreground/outdoor_world_base_no_foreground.png`
- Review preview: `production/assets/outdoor_world_world2d/v001/02_world_base_no_foreground/outdoor_world_base_no_foreground_review.png`
- Region crops: `production/assets/outdoor_world_world2d/v001/02_world_base_no_foreground/region_base_crops/`
- Manifest: `production/assets/outdoor_world_world2d/v001/02_world_base_no_foreground/world_base_manifest.json`

## Village And MountainHut Correction

The existing Village and MountainHut high-detail images are useful review references, but they came from isolated region production. Future promotion should inherit from the whole-world base crop first, then repaint detail inside that inherited composition.

The previous Village layout draft remains a layout draft only. It is not final `village_painted_source` art and should not be split or promoted ahead of the world-base inheritance review.

Do not independently recompose region bases. If a region needs higher quality, repaint over the inherited crop while preserving roads, terrain color, lighting, edge continuation, and camera perspective.

## Layer Scope For Seamless MVP

Use this smaller layer stack until world continuity is stable:

- `base_ground`
- `terrain_details`
- `behind_player_structures`
- `ysort_props_structures`
- `foreground_occlusion`

Keep weather, season, and time-of-day in Godot/system-level tinting first. Avoid per-region weather overlays until base seams pass review.
""",
        encoding="utf-8",
    )


def update_project_manifest() -> None:
    project = read_json(PROJECT_MANIFEST)
    master = project.setdefault("seamless_outdoor_world", {})
    master["phase"] = "02_world_base_no_foreground"
    master["status"] = "world_base_no_foreground_ready_for_region_crop_review"
    master["world_base_no_foreground"] = rel(WORLD_BASE)
    master["world_base_manifest"] = rel(BASE_MANIFEST)
    master["region_base_crops_dir"] = rel(REGION_CROP_DIR)
    master["runtime_replacement"] = False
    master["launch_quality_approved"] = False
    master["next_art_step"] = "Review the whole-world no-foreground base and inherited region crops before any high-quality region repaint or runtime replacement."
    write_json(PROJECT_MANIFEST, project)


def main() -> None:
    ensure_dirs()
    layout = load_layout()
    world_image = write_world_base(layout)
    region_crops = write_region_crops(layout, world_image)
    write_base_manifest(region_crops)
    update_workflow()
    update_source_strategy()
    update_project_manifest()
    print(f"OK: generated {rel(WORLD_BASE)} and {len(region_crops)} region crops")


if __name__ == "__main__":
    main()
