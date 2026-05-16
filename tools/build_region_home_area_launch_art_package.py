from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "sprites" / "environments" / "homeyard"
PROMPT_ROOT = ROOT / "production" / "assets" / "homeyard" / "prompts"
OUT_ROOT = ROOT / "production" / "assets" / "regions" / "home_area_launch" / "v001"
MANIFEST = OUT_ROOT / "region_home_area_launch_art_manifest.json"
PREVIEW = OUT_ROOT / "region_home_area_launch_preview.png"

LAYER_ORDER = {
    "bg": 0,
    "mid": 10,
    "props": 40,
    "fg": 80,
    "fx": 95,
}

EXCLUDED_DIRS = {"atlases", "previews", "source"}


def prompt_metadata(asset_id: str) -> dict[str, str | None]:
    prompt_path = PROMPT_ROOT / f"{asset_id}.md"
    if not prompt_path.exists():
        return {"prompt_file": None, "generated_source": None}

    text = prompt_path.read_text(encoding="utf-8")
    source_match = re.search(r"Generated formal image source:\s*`([^`]+)`", text)
    return {
        "prompt_file": prompt_path.relative_to(ROOT).as_posix(),
        "generated_source": source_match.group(1) if source_match else None,
    }


def source_assets() -> list[Path]:
    assets: list[Path] = []
    for path in SOURCE_ROOT.rglob("*.png"):
        relative_parts = set(path.relative_to(SOURCE_ROOT).parts)
        if relative_parts & EXCLUDED_DIRS:
            continue
        assets.append(path)
    return sorted(assets)


def copy_asset(path: Path) -> dict[str, Any]:
    category = path.parent.name
    asset_id = path.stem
    target_dir = OUT_ROOT / category
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / path.name
    shutil.copy2(path, target)

    with Image.open(target) as image:
        alpha = False
        bbox = None
        if image.mode == "RGBA":
            channel = image.getchannel("A")
            alpha = channel.getextrema()[0] < 255
            bbox = channel.getbbox()
        width, height = image.size

    metadata = prompt_metadata(asset_id)
    return {
        "id": asset_id,
        "category": category,
        "source": path.relative_to(ROOT).as_posix(),
        "file": target.relative_to(OUT_ROOT).as_posix(),
        "width": width,
        "height": height,
        "mode": image.mode,
        "has_alpha": alpha,
        "alpha_bbox": list(bbox) if bbox else None,
        "z_family": LAYER_ORDER.get(category, 50),
        "source_kind": "formal_homeyard_generated_or_source_derived",
        **metadata,
    }


def make_preview(layers: list[dict[str, Any]]) -> None:
    sky = OUT_ROOT / "bg" / "homeyard_bg_sky_01.png"
    if sky.exists():
        canvas = Image.open(sky).convert("RGBA")
    else:
        canvas = Image.new("RGBA", (1920, 1080), (226, 234, 210, 255))

    ordered = sorted(layers, key=lambda layer: (layer["z_family"], layer["id"]))
    for layer in ordered:
        if layer["id"] == "homeyard_bg_sky_01":
            continue
        path = OUT_ROOT / layer["file"]
        image = Image.open(path).convert("RGBA")
        if image.size == canvas.size:
            canvas.alpha_composite(image)

    canvas.save(PREVIEW)


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    layers = [copy_asset(path) for path in source_assets()]
    make_preview(layers)

    manifest = {
        "region_id": "Region_HomeArea",
        "package_id": "home_area_launch_v001",
        "status": "rejected_composition_source_pool",
        "source_policy": "formal generated/source-derived assets only; procedural engineering candidates excluded; current composite is not approved for runtime integration",
        "runtime_replacement": False,
        "source_root": SOURCE_ROOT.relative_to(ROOT).as_posix(),
        "layers": layers,
        "preview": PREVIEW.relative_to(OUT_ROOT).as_posix(),
        "notes": [
            "This package is a source asset pool and rejected composition reference, not an approved launch scene.",
            "The previous home_area_bake/candidates/v001 procedural output is retained only as coordinate/reference evidence.",
            "Runtime scene references are not changed by this packaging step.",
            "Next production must start from a Region_HomeArea design brief and produce scene-specific launch art."
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"OK: packaged {len(layers)} HomeArea source-pool assets; composition remains rejected")


if __name__ == "__main__":
    main()
