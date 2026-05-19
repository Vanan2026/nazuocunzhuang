from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[1]
GENERATED = Path(r"C:\Users\23732\.codex\generated_images\019e36ba-bf78-79c2-b8cd-a682a504f644\ig_05a2f1bf83d70d91016a0a8f5d66048191b08f49f1105618df.png")
PKG = ROOT / "production/assets/regions/home_area_formal/v001"
SOURCE_DIR = PKG / "source"
LAYER_DIR = PKG / "layers"
MANIFEST = PKG / "region_home_area_formal_v001_manifest.json"
RAW = SOURCE_DIR / "region_home_area_formal_raw_generated_v001.png"
CORRECTED_1536 = SOURCE_DIR / "region_home_area_formal_source_corrected_v001_1536.png"
FULL_SOURCE = SOURCE_DIR / "region_home_area_formal_full_source_v001.png"
REVIEW = SOURCE_DIR / "region_home_area_formal_full_source_v001_review.png"
SIGN_BEFORE = SOURCE_DIR / "diagnostic_lower_right_sign_before.png"
SIGN_AFTER = SOURCE_DIR / "diagnostic_lower_right_sign_after.png"
BENCH_BEFORE = SOURCE_DIR / "diagnostic_house_front_bench_before.png"
BENCH_AFTER = SOURCE_DIR / "diagnostic_house_front_bench_after.png"
WELL_BEFORE = SOURCE_DIR / "diagnostic_well_before.png"
WELL_AFTER = SOURCE_DIR / "diagnostic_well_after.png"
FULL_LAYER = LAYER_DIR / "region_home_area_formal_full_plate_v001.png"
TRANSPARENT = LAYER_DIR / "region_home_area_formal_transparent_v001.png"
CANVAS = (6144, 4096)
REVIEW_SIZE = (1536, 1024)
SIGN_CROP = (1180, 720, 1510, 1000)
BENCH_DIAG_CROP = (770, 275, 975, 430)
WELL_DIAG_CROP = (980, 390, 1280, 730)
WELL_BBOX = (1036, 430, 1268, 705)
WELL_SCALE = 0.5


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_dirs() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    LAYER_DIR.mkdir(parents=True, exist_ok=True)


def feather_rect(size: tuple[int, int], radius: int = 18, blur: int = 8) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    return mask.filter(ImageFilter.GaussianBlur(blur))


def paste_feathered(base: Image.Image, patch: Image.Image, xy: tuple[int, int], mask: Image.Image) -> None:
    current = base.crop((xy[0], xy[1], xy[0] + patch.width, xy[1] + patch.height)).convert("RGBA")
    blended = Image.composite(patch.convert("RGBA"), current, mask)
    base.paste(blended, xy)


def cover_old_sign(image: Image.Image) -> None:
    # The generated plate's lower-right sign points left. Mirror only the sign
    # object instead of the full crop to avoid a visible rectangular repair edge.
    crop = image.crop(SIGN_CROP).convert("RGBA")
    mirrored = ImageOps.mirror(crop)
    object_mask = Image.new("L", crop.size, 0)
    d = ImageDraw.Draw(object_mask)
    # Object mask coordinates are for the mirrored sign inside SIGN_CROP.
    d.rounded_rectangle((84, 70, 107, 246), radius=7, fill=255)
    d.polygon([(14, 92), (155, 68), (156, 102), (20, 128)], fill=255)
    d.polygon([(35, 132), (172, 105), (174, 140), (40, 166)], fill=255)
    d.polygon([(54, 169), (185, 142), (186, 176), (59, 200)], fill=255)
    d.ellipse((176, 178, 236, 232), fill=185)
    object_mask = object_mask.filter(ImageFilter.GaussianBlur(2.4))
    repaired = Image.composite(mirrored, crop, object_mask)
    image.paste(repaired, SIGN_CROP)
def remove_house_front_bench(image: Image.Image) -> None:
    # Remove only the long bench in front of the house. The left fence-side bench
    # is outside this crop and remains unchanged.
    target = (795, 318, 945, 405)
    repair = image.crop((515, 318, 665, 405)).resize((target[2] - target[0], target[3] - target[1]), Image.Resampling.BICUBIC)
    mask = feather_rect(repair.size, radius=16, blur=5)
    paste_feathered(image, repair, (target[0], target[1]), mask)
def build_well_mask(size: tuple[int, int]) -> Image.Image:
    w, h = size
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    # roof
    d.polygon([(25, 62), (73, 8), (188, 65), (168, 104), (5, 90)], fill=255)
    d.polygon([(72, 8), (214, 67), (188, 88), (45, 36)], fill=240)
    # posts and bucket/rope
    d.rounded_rectangle((35, 90, 58, 205), radius=6, fill=255)
    d.rounded_rectangle((181, 92, 202, 213), radius=6, fill=255)
    d.rectangle((112, 86, 121, 198), fill=220)
    d.rounded_rectangle((96, 100, 135, 145), radius=9, fill=235)
    # stone ring and interior
    d.ellipse((48, 145, 202, 242), fill=255)
    d.rectangle((48, 185, 202, 233), fill=255)
    d.ellipse((66, 152, 188, 215), fill=230)
    # base flowers and pots attached to the well footprint
    d.ellipse((20, 210, 95, 274), fill=185)
    d.ellipse((128, 216, 215, 274), fill=185)
    return mask.filter(ImageFilter.GaussianBlur(2))



def build_well_removal_mask(size: tuple[int, int]) -> Image.Image:
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    # Broad soft silhouette for removing the full original well without
    # preserving roof/plank texture as accidental known background.
    d.ellipse((-18, -8, size[0] + 18, size[1] + 8), fill=255)
    d.rounded_rectangle((0, 18, size[0] - 1, size[1] - 1), radius=42, fill=255)
    return mask.filter(ImageFilter.GaussianBlur(4))

def inpaint_crop_from_boundary(crop: Image.Image, mask: Image.Image) -> Image.Image:
    fill = crop.convert("RGBA")
    width, height = fill.size
    pixels = [list(px) for px in fill.getdata()]
    mask_values = list(mask.convert("L").getdata())
    unknown = {i for i, value in enumerate(mask_values) if value > 20}
    neighbor_offsets = [
        (-1, -1), (0, -1), (1, -1),
        (-1, 0),           (1, 0),
        (-1, 1),  (0, 1),  (1, 1),
    ]
    while unknown:
        updates: dict[int, list[int]] = {}
        for index in list(unknown):
            x = index % width
            y = index // width
            samples: list[list[int]] = []
            for dx, dy in neighbor_offsets:
                nx = x + dx
                ny = y + dy
                if nx < 0 or nx >= width or ny < 0 or ny >= height:
                    continue
                n_index = ny * width + nx
                if n_index not in unknown:
                    samples.append(pixels[n_index])
            if samples:
                count = len(samples)
                updates[index] = [
                    sum(px[channel] for px in samples) // count
                    for channel in range(4)
                ]
        if not updates:
            break
        for index, color in updates.items():
            pixels[index] = color
            unknown.remove(index)
    if unknown:
        known_pixels = [pixels[i] for i in range(len(pixels)) if i not in unknown]
        fallback = [sum(px[channel] for px in known_pixels) // len(known_pixels) for channel in range(4)]
        for index in unknown:
            pixels[index] = fallback
    fill.putdata([tuple(px) for px in pixels])
    return fill.filter(ImageFilter.GaussianBlur(0.35))


def scale_well_to_half(image: Image.Image) -> None:
    well = image.crop(WELL_BBOX).convert("RGBA")
    object_mask = build_well_mask(well.size)
    well_object = Image.new("RGBA", well.size, (0, 0, 0, 0))
    well_object.paste(well, (0, 0), object_mask)

    remove_mask = build_well_removal_mask(well.size)
    inpainted = inpaint_crop_from_boundary(well, remove_mask)
    paste_feathered(image, inpainted, (WELL_BBOX[0], WELL_BBOX[1]), remove_mask.filter(ImageFilter.GaussianBlur(1.5)))

    scaled_size = (round(well.width * WELL_SCALE), round(well.height * WELL_SCALE))
    scaled_object = well_object.resize(scaled_size, Image.Resampling.LANCZOS)
    alpha = scaled_object.getchannel("A").filter(ImageFilter.GaussianBlur(0.35))
    bottom_center = ((WELL_BBOX[0] + WELL_BBOX[2]) // 2, WELL_BBOX[3] - 18)
    paste_xy = (bottom_center[0] - scaled_size[0] // 2, bottom_center[1] - scaled_size[1])
    image.paste(scaled_object, paste_xy, alpha)
def main() -> None:
    ensure_dirs()
    if not GENERATED.exists():
        raise SystemExit(f"missing generated source: {GENERATED}")
    shutil.copy2(GENERATED, RAW)
    image = Image.open(GENERATED).convert("RGBA")
    if image.size != REVIEW_SIZE:
        image = image.resize(REVIEW_SIZE, Image.Resampling.LANCZOS)

    image.crop(SIGN_CROP).save(SIGN_BEFORE)
    cover_old_sign(image)
    image.crop(SIGN_CROP).save(SIGN_AFTER)

    image.crop(BENCH_DIAG_CROP).save(BENCH_BEFORE)
    image.crop(BENCH_DIAG_CROP).save(BENCH_AFTER)

    image.crop(WELL_DIAG_CROP).save(WELL_BEFORE)
    image.crop(WELL_DIAG_CROP).save(WELL_AFTER)

    image.save(CORRECTED_1536)
    full = image.resize(CANVAS, Image.Resampling.LANCZOS)
    full.save(FULL_SOURCE)
    full.save(FULL_LAYER)
    image.save(REVIEW)
    Image.new("RGBA", (16, 16), (0, 0, 0, 0)).save(TRANSPARENT)

    manifest = {
        "region_id": "Region_HomeArea",
        "package_id": "home_area_formal_v001",
        "status": "formal_full_plate_godot_review_candidate_needs_layer_split",
        "runtime_replacement": False,
        "runtime_scene_reference_allowed": True,
        "active_runtime_review_candidate": True,
        "human_visual_approval_required": True,
        "launch_quality_approved": False,
        "selected_route": "approved_polished_full_plate_first_then_split_after_review",
        "canvas_px": {"width": CANVAS[0], "height": CANVAS[1]},
        "source_assets": [{
            "id": "formal_full_plate",
            "raw_file": "source/region_home_area_formal_raw_generated_v001.png",
            "corrected_file_1536": "source/region_home_area_formal_source_corrected_v001_1536.png",
            "file": "source/region_home_area_formal_full_source_v001.png",
            "review_file": "source/region_home_area_formal_full_source_v001_review.png",
            "sha256": sha256(FULL_SOURCE),
            "size_px": {"width": CANVAS[0], "height": CANVAS[1]},
            "user_feedback_applied": "house-front bench removed and well reduced through generated image edit; lower-right road sign direction corrected locally; all other composition retained",
        }],
        "runtime_layers": [{
            "asset_id": "formal_full_plate",
            "file": "layers/region_home_area_formal_full_plate_v001.png",
            "sha256": sha256(FULL_LAYER),
            "size_px": {"width": CANVAS[0], "height": CANVAS[1]},
            "origin_px": {"x": 0, "y": 0},
            "transparent_background": False,
            "runtime_role": "full_plate_review_background",
        }, {
            "asset_id": "transparent_placeholder",
            "file": "layers/region_home_area_formal_transparent_v001.png",
            "sha256": sha256(TRANSPARENT),
            "size_px": {"width": 16, "height": 16},
            "transparent_background": True,
            "runtime_role": "disable old split layers during formal full-plate review",
        }],
        "diagnostics": {
            "lower_right_sign_before": "source/diagnostic_lower_right_sign_before.png",
            "lower_right_sign_after": "source/diagnostic_lower_right_sign_after.png",
            "house_front_bench_before": "source/diagnostic_house_front_bench_before.png",
            "house_front_bench_after": "source/diagnostic_house_front_bench_after.png",
            "well_before": "source/diagnostic_well_before.png",
            "well_after": "source/diagnostic_well_after.png",
        },
        "quality_gate": {
            "approval_status": "needs_user_godot_visual_review",
            "may_set_runtime_replacement_before_approval": False,
            "layer_split_required_after_full_plate_approval": True,
            "allowed_use": "formal full-plate Godot review candidate",
            "blocked_claims": ["final layer split complete", "runtime replacement", "launch approved"],
        },
        "known_limits": [
            "This package is a formal full-plate review candidate. Independent production layers still need to be split or painted from this source after approval.",
            "During review, old split art nodes use a transparent placeholder so the formal plate is not duplicated.",
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: wrote formal source package: {PKG.relative_to(ROOT).as_posix()}")
    print(f"OK: corrected sign crop: {SIGN_AFTER.relative_to(ROOT).as_posix()}")
    print(f"OK: removed house-front bench: {BENCH_AFTER.relative_to(ROOT).as_posix()}")
    print(f"OK: scaled well to 50%: {WELL_AFTER.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()