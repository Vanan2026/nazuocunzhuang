from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "production" / "assets" / "regions" / "home_area_art" / "v002"
CANVAS = (6144, 4096)
PREVIEW_SIZE = (1536, 1024)

RAW_SOURCE = "region_home_area_art_v002_generated_source.png"
BASE_FULL = "region_home_area_base_full_v002.png"
PREVIEW = "region_home_area_art_v002_preview.png"
MANIFEST = "region_home_area_art_v002_manifest.json"
PROMPT_FILE = "region_home_area_art_v002_prompt.md"

PROMPT = """Use case: stylized-concept
Asset type: production-bound full-scene base plate / terrain mother map for a Godot 2D/2.5D game region, Region_HomeArea. Landscape 3:2 composition intended to be resized to 6144x4096.
Primary request: Create a single coherent high-quality full-scene background plate for a quiet Japanese countryside home yard. This is a visual review mother map only, before splitting ground/path/house/occluder layers.
Scene/backdrop: oblique 3/4 top-down exploration map view, wide playable yard, warm rural Japanese home at upper center, north village road across the upper area, southeast footpath leading behind the house toward a back farm, west garden/flower beds, left shade tree, right fruit tree, foreground grass and leaf framing at lower edge.
Subject: the ground and terrain must be the strongest part: authored grass variation, natural dirt/stone path blending, irregular worn edges, moss, small pebbles, sparse wildflowers, softened yard transitions, believable material texture, no flat procedural fills.
Style/medium: premium hand-painted anime countryside background, soft painterly brushwork, production game background, natural perspective and scale suitable for a 192x288 pixel 2D character, detailed but readable.
Composition/framing: keep the central front yard clear and readable for player movement; house/veranda in the upper center; left tree root around upper-left; right tree around upper-right; north road readable as an exit; southeast path clearly readable as BackFarm exit; foreground grass frames edges but does not cover main paths.
Lighting/mood: late morning warm sunlight, soft dappled tree shadows, calm healing rural mood, gentle depth, no harsh contrast.
Color palette: low-saturation warm greens, straw dirt, soft wood browns, muted slate roof, subtle seasonal warm accents.
Materials/textures: hand-authored grass clumps, worn packed earth, stepping stones, wooden veranda, clay/stone path edges, hedges and garden details; avoid clean geometric polygons.
Constraints: no characters, no UI, no labels, no text, no watermark; not a close-up veranda illustration; not a single object sheet; preserve clear gameplay space and exits; no visible tile grid; no flat vector/procedural look; no dark fantasy; no photorealism.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare the Region_HomeArea art v002 full-scene/base-ground review plate."
    )
    parser.add_argument("source", type=Path, help="Generated source image to ingest.")
    return parser.parse_args()


def load_rgba(path: Path) -> Image.Image:
    if not path.exists():
        raise FileNotFoundError(f"missing source image: {path}")
    with Image.open(path) as image:
        return image.convert("RGBA")


def resize_cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    src_w, src_h = image.size
    dst_w, dst_h = size
    scale = max(dst_w / src_w, dst_h / src_h)
    scaled = image.resize((round(src_w * scale), round(src_h * scale)), Image.Resampling.LANCZOS)
    left = (scaled.width - dst_w) // 2
    top = (scaled.height - dst_h) // 2
    return scaled.crop((left, top, left + dst_w, top + dst_h))


def write_manifest(source_image: Image.Image) -> None:
    manifest = {
        "region_id": "Region_HomeArea",
        "package_id": "home_area_art_v002",
        "status": "visual_review_required_before_layer_split",
        "runtime_replacement": False,
        "layer_split_ready": False,
        "canvas_px": {"width": CANVAS[0], "height": CANVAS[1]},
        "design_contract": "production/assets/regions/home_area_design/region_home_area_layout_v001.json",
        "composition_source": "built_in_imagegen_full_scene_plate_2026_05_14",
        "prompt_file": PROMPT_FILE,
        "assets": [
            {
                "asset_id": "generated_source",
                "file": RAW_SOURCE,
                "size_px": {"width": source_image.width, "height": source_image.height},
                "role": "Original built-in image generation output preserved for review provenance.",
                "target_parent": "art_review_only",
            },
            {
                "asset_id": "base_full",
                "file": BASE_FULL,
                "origin_px": {"x": 0, "y": 0},
                "size_px": {"width": CANVAS[0], "height": CANVAS[1]},
                "anchor_px": {"x": 0, "y": 0},
                "target_parent": "art_review_only",
                "z_index": 0,
                "role": "Full-scene/base-ground mother plate for visual review before layer splitting.",
                "integration_note": "Do not wire this single plate into runtime; split approved ground/path/house/occluder layers first.",
            },
            {
                "asset_id": "review_preview",
                "file": PREVIEW,
                "size_px": {"width": PREVIEW_SIZE[0], "height": PREVIEW_SIZE[1]},
                "role": "Downscaled visual review preview.",
                "target_parent": "art_review_only",
            },
        ],
        "visual_gate": [
            "Ground and path material must pass visual review before any split work.",
            "Do not continue v001 post-processing as the mainline.",
            "After acceptance, split ground/path first, then house/veranda, then occluders/foreground/light.",
        ],
        "next_split_candidates": [
            "region_home_area_ground_yard_v002.png",
            "region_home_area_path_village_road_v002.png",
            "region_home_area_path_back_farm_v002.png",
            "region_home_area_house_body_v002.png",
            "region_home_area_house_roof_occluder_v002.png",
            "region_home_area_veranda_floor_v002.png",
            "region_home_area_tree_left_canopy_occluder_v002.png",
            "region_home_area_tree_right_canopy_occluder_v002.png",
        ],
    }
    (ART_DIR / MANIFEST).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    ART_DIR.mkdir(parents=True, exist_ok=True)

    source = load_rgba(args.source)
    source.save(ART_DIR / RAW_SOURCE)

    base = resize_cover(source, CANVAS)
    base.save(ART_DIR / BASE_FULL)

    preview = resize_cover(base, PREVIEW_SIZE)
    preview.save(ART_DIR / PREVIEW)

    (ART_DIR / PROMPT_FILE).write_text("# Region_HomeArea Art v002 Prompt\n\n```text\n" + PROMPT + "```\n", encoding="utf-8")
    write_manifest(source)
    print(f"OK: prepared Region_HomeArea art v002 base plate in {ART_DIR}")


if __name__ == "__main__":
    main()
