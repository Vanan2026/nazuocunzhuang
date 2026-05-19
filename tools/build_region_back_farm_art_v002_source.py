from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageStat

import build_region_back_farm_art_v001_formal_assets as v001_builder

ROOT = Path(__file__).resolve().parents[1]
V001_DIR = ROOT / "production/assets/regions/back_farm_art/v001"
V001_MANIFEST = V001_DIR / "region_back_farm_art_v001_manifest.json"
V002_DIR = ROOT / "production/assets/regions/back_farm_art/v002"
SOURCE_DIR = V002_DIR / "source"
MASK_DIR = SOURCE_DIR / "masks"
LAYER_DIR = V002_DIR / "layers"
MANIFEST = V002_DIR / "region_back_farm_art_v002_manifest.json"
SOURCE = SOURCE_DIR / "region_back_farm_full_composition_v002.png"
REVIEW = SOURCE_DIR / "region_back_farm_full_composition_v002_review.png"
PREVIEW = V002_DIR / "region_back_farm_art_v002_runtime_preview.png"
CONTACT = V002_DIR / "region_back_farm_art_v002_layer_contact_sheet.png"
CANVAS = (2000, 2000)
LAYER_ORDER = ["ground", "path", "field_rows", "fence", "pond", "shed", "foreground_grass", "shadow", "light"]
EXPECTED_IDS = set(LAYER_ORDER)
FILE_MAP = {
    "ground": "region_back_farm_ground_v002.png",
    "path": "region_back_farm_path_v002.png",
    "field_rows": "region_back_farm_field_rows_v002.png",
    "shed": "region_back_farm_shed_v002.png",
    "pond": "region_back_farm_pond_v002.png",
    "fence": "region_back_farm_fence_v002.png",
    "foreground_grass": "region_back_farm_foreground_grass_v002.png",
    "shadow": "region_back_farm_shadow_overlay_v002.png",
    "light": "region_back_farm_light_overlay_v002.png",
}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_dirs() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    MASK_DIR.mkdir(parents=True, exist_ok=True)
    LAYER_DIR.mkdir(parents=True, exist_ok=True)


def build_full_layers() -> dict[str, Image.Image]:
    return {
        "ground": v001_builder.build_ground(),
        "path": v001_builder.build_path(),
        "field_rows": v001_builder.build_field_rows(),
        "shed": v001_builder.build_shed(),
        "pond": v001_builder.build_pond(),
        "fence": v001_builder.build_fence(),
        "foreground_grass": v001_builder.build_foreground(),
        "shadow": v001_builder.build_shadow(),
        "light": v001_builder.build_light(),
    }


def composite(layers: dict[str, Image.Image]) -> Image.Image:
    out = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    for asset_id in LAYER_ORDER:
        out.alpha_composite(layers[asset_id])
    return out


def alpha_metrics(image: Image.Image) -> dict:
    alpha = image.getchannel("A")
    hist = alpha.histogram()
    total = image.width * image.height
    return {
        "alpha_bbox": list(alpha.getbbox() or (0, 0, 0, 0)),
        "transparent_ratio": round(hist[0] / total, 5),
        "semi_ratio": round(sum(hist[1:255]) / total, 5),
        "opaque_ratio": round(hist[255] / total, 5),
    }


def make_contact(records: list[dict]) -> None:
    cols = 3
    tile_w, tile_h = 420, 320
    rows = (len(records) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * tile_w, rows * tile_h), (244, 239, 226, 255))
    draw = ImageDraw.Draw(sheet)
    for idx, rec in enumerate(records):
        x = (idx % cols) * tile_w
        y = (idx // cols) * tile_h
        image = Image.open(V002_DIR / rec["file"]).convert("RGBA")
        image.thumbnail((tile_w - 36, tile_h - 58), Image.Resampling.LANCZOS)
        sheet.alpha_composite(image, (x + (tile_w - image.width) // 2, y + 38))
        draw.text((x + 10, y + 10), rec["asset_id"], fill=(40, 35, 29, 255))
        draw.text((x + 10, y + tile_h - 28), f"{rec['size_px']['width']}x{rec['size_px']['height']} z{rec['z_index']}", fill=(78, 68, 58, 255))
        draw.rectangle((x, y, x + tile_w - 1, y + tile_h - 1), outline=(180, 170, 150, 160))
    sheet.save(CONTACT)


def validate_nonblank(path: Path, size: tuple[int, int]) -> None:
    require(path.exists(), f"missing image: {path.relative_to(ROOT).as_posix()}")
    img = Image.open(path).convert("RGBA")
    require(img.size == size, f"image size mismatch for {path.name}: {img.size}")
    stat = ImageStat.Stat(img.convert("L"))
    require(stat.extrema[0][0] != stat.extrema[0][1], f"image must be non-blank: {path.name}")


def main() -> None:
    ensure_dirs()
    require(V001_MANIFEST.exists(), "missing BackFarm v001 manifest for spatial contract")
    v001 = json.loads(V001_MANIFEST.read_text(encoding="utf-8"))
    contract = {layer["asset_id"]: layer for layer in v001.get("required_layers", [])}
    require(set(contract) == EXPECTED_IDS, "BackFarm v001 layer contract mismatch")
    layers = build_full_layers()
    full = composite(layers)
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    full.save(SOURCE)
    full.resize((1000, 1000), Image.Resampling.LANCZOS).save(REVIEW)
    source_hash = sha256(SOURCE)
    records: list[dict] = []
    preview = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    for asset_id in LAYER_ORDER:
        rec = contract[asset_id]
        origin = rec["origin_px"]
        size = rec["size_px"]
        box = (origin["x"], origin["y"], origin["x"] + size["width"], origin["y"] + size["height"])
        layer = layers[asset_id]
        mask = layer.getchannel("A")
        mask.save(MASK_DIR / f"{asset_id}_mask.png")
        crop = layer.crop(box)
        out_file = FILE_MAP[asset_id]
        out_path = LAYER_DIR / out_file
        crop.save(out_path)
        preview.alpha_composite(crop, (origin["x"], origin["y"]))
        records.append({
            "asset_id": asset_id,
            "file": f"layers/{out_file}",
            "sha256": sha256(out_path),
            "origin_px": origin,
            "size_px": {"width": crop.width, "height": crop.height},
            "target_parent": rec["target_parent"],
            "z_index": rec["z_index"],
            "occlusion_rule": rec["occlusion_rule"],
            "derived_from_source": True,
            "source_asset_id": "full_composition",
            "source_sha256": source_hash,
            "source_rect_px": {"x": box[0], "y": box[1], "width": crop.width, "height": crop.height},
            "mask_file": f"source/masks/{asset_id}_mask.png",
            **alpha_metrics(crop),
        })
    preview.save(PREVIEW)
    make_contact(records)
    manifest = {
        "region_id": "Region_BackFarm",
        "package_id": "back_farm_art_v002",
        "status": "runtime_structural_placeholder_not_launch_quality_v002",
        "runtime_replacement": False,
        "runtime_scene_reference_allowed": True,
        "active_runtime_placeholder": True,
        "human_visual_approval_required": True,
        "launch_quality_approved": False,
        "launch_quality_blockers": [
            "Current package is deterministic/source-first structural art, not final painted production art.",
            "User rejected current visual quality as not launch-level on 2026-05-18.",
            "Composition and asset polish require a real launch-quality source pass before final promotion.",
        ],
        "quality_gate": {
            "launch_status": "rejected_not_launch_quality",
            "allowed_use": "active Godot structural placeholder for scene opening and layer adjustment",
            "blocked_use": "launch-ready art or final runtime replacement",
        },
        "canvas_px": {"width": CANVAS[0], "height": CANVAS[1]},
        "selected_route": "single_full_source_then_split_layers",
        "source_assets": [{
            "id": "full_composition",
            "file": "source/region_back_farm_full_composition_v002.png",
            "review_file": "source/region_back_farm_full_composition_v002_review.png",
            "sha256": source_hash,
            "size_px": {"width": CANVAS[0], "height": CANVAS[1]},
        }],
        "required_layers": records,
        "runtime_preview": "region_back_farm_art_v002_runtime_preview.png",
        "contact_sheet": "region_back_farm_art_v002_layer_contact_sheet.png",
        "source_policy": "Source-first BackFarm package: one shared 2000x2000 composition/layer stack, then cropped runtime layers with masks and source provenance.",
        "promotion_note": "Promoted by user command '继续' after HomeArea v007; preserves existing BackFarm gameplay nodes and scene anchors.",
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    validate_nonblank(SOURCE, CANVAS)
    validate_nonblank(REVIEW, (1000, 1000))
    print(f"OK: generated BackFarm v002 source-first package -> {V002_DIR.relative_to(ROOT).as_posix()}")
    print(f"OK: source_sha256 {source_hash}")


if __name__ == "__main__":
    main()
