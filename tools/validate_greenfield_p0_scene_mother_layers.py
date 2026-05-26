from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

from process_greenfield_p0_scene_mother_layers import (
    DEFAULT_INCOMING,
    DEFAULT_SOURCE,
    MASKS,
    ROOT,
    composite_mean_diff,
    sha16,
)


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()


def load_rgba(path: Path) -> Image.Image:
    if not path.exists():
        fail(f"missing PNG: {path}")
    image = Image.open(path)
    if image.format != "PNG":
        fail(f"not a PNG: {path}")
    return image.convert("RGBA")


def validate(incoming: Path, expect_source_deleted: bool = False, write_audit: bool = False) -> dict:
    mother_root = incoming / "01_scene_mothers" / "regions"
    base_root = incoming / "02_scene_base" / "regions"
    foreground_root = incoming / "03_foreground_occlusion" / "regions"
    audit_root = incoming / "04_audit"
    expected_regions = sorted(MASKS)
    deprecated_top_level = [
        incoming / "01_mother_images",
        incoming / "02_runtime_exports",
        incoming / "audit_previews",
        incoming / "audit_scene_mother_layers.json",
    ]

    for root in (mother_root, base_root, foreground_root):
        if not root.exists():
            fail(f"missing required directory: {root}")

    regions = {}
    errors: list[str] = []
    for deprecated in deprecated_top_level:
        if deprecated.exists():
            errors.append(f"deprecated top-level incoming item should be archived: {relative(deprecated)}")

    existing_audit = {}
    existing_audit_path = audit_root / "scene_mother_layers.json"
    if not existing_audit_path.exists():
        existing_audit_path = incoming / "audit_scene_mother_layers.json"
    if existing_audit_path.exists():
        try:
            existing_audit = json.loads(existing_audit_path.read_text(encoding="utf-8")).get("regions", {})
        except json.JSONDecodeError:
            existing_audit = {}

    for region in expected_regions:
        mother_path = mother_root / region / f"{region}_scene_mother.png"
        base_path = base_root / region / f"{region}_base.png"
        foreground_path = foreground_root / region / f"{region}_foreground_occlusion.png"

        mother = load_rgba(mother_path)
        base = load_rgba(base_path)
        foreground = load_rgba(foreground_path)
        alpha = foreground.getchannel("A")
        alpha_array = np.array(alpha)
        alpha_extrema = alpha.getextrema()
        foreground_pixels = int(np.count_nonzero(alpha_array))
        mean_diff = composite_mean_diff(mother, base, foreground)
        visible = alpha_array > 0
        mother_rgb = np.array(mother.convert("RGB"))
        foreground_rgb = np.array(foreground.convert("RGB"))
        rgb_matches_mother = bool(np.array_equal(mother_rgb[visible], foreground_rgb[visible]))

        preserved_pixel_regions = existing_audit.get(region, {}).get("foreground_pixel_regions", [])
        categories = sorted(
            {
                item.get("category", "unknown")
                for item in preserved_pixel_regions
            }
            or {shape.category for shape in MASKS[region]}
        )
        checks = {
            "same_size": mother.size == base.size == foreground.size,
            "mother_opaque": mother.getchannel("A").getextrema() == (255, 255),
            "base_opaque": base.getchannel("A").getextrema() == (255, 255),
            "foreground_rgba": foreground.mode == "RGBA",
            "foreground_alpha_effective": alpha_extrema[0] == 0 and alpha_extrema[1] == 255 and foreground_pixels > 0,
            "foreground_full_canvas": foreground.size == mother.size,
            "foreground_visible_rgb_matches_mother": rgb_matches_mother,
            "foreground_pixel_regions_listed": bool(preserved_pixel_regions),
            "composite_mean_diff_under_2": mean_diff < 2.0,
        }
        for name, passed in checks.items():
            if not passed:
                errors.append(f"{region}: {name} failed")

        regions[region] = {
            "region": region,
            "image_size": list(mother.size),
            "files": {
                "scene_mother": relative(mother_path),
                "base": relative(base_path),
                "foreground_occlusion": relative(foreground_path),
            },
            "sha16": {
                "scene_mother": sha16(mother_path),
                "base": sha16(base_path),
                "foreground_occlusion": sha16(foreground_path),
            },
            "foreground_pixel_categories": categories,
            "foreground_pixel_regions": preserved_pixel_regions,
            "foreground_nontransparent_pixels": foreground_pixels,
            "foreground_alpha_range": list(alpha_extrema),
            "composite_mean_rgb_diff": round(mean_diff, 4),
            "checks": checks,
            "known_issues": [
                "Generated by deterministic technical masking from the supplied scene mother; final art approval still requires human visual review.",
                "Base repair is localized under the foreground mask and is intended to be viewed with the foreground occlusion layer recomposited.",
            ],
        }

    extra_pngs = []
    for root in (mother_root, base_root, foreground_root):
        for path in sorted(root.rglob("*.png")):
            region = path.parent.name
            if region not in expected_regions:
                extra_pngs.append(relative(path))

    if extra_pngs:
        errors.append(f"unexpected region PNGs: {extra_pngs}")
    if expect_source_deleted and DEFAULT_SOURCE.exists():
        errors.append(f"temporary source directory still exists: {DEFAULT_SOURCE}")

    audit = {
        "package": "greenfield_p0_v001_scene_mother_layers",
        "incoming_dir": relative(incoming),
        "region_count": len(regions),
        "checks_summary": {
            "all_same_size_per_region": all(item["checks"]["same_size"] for item in regions.values()),
            "all_mothers_opaque": all(item["checks"]["mother_opaque"] for item in regions.values()),
            "all_bases_opaque": all(item["checks"]["base_opaque"] for item in regions.values()),
            "all_foregrounds_rgba_effective": all(
                item["checks"]["foreground_rgba"] and item["checks"]["foreground_alpha_effective"]
                for item in regions.values()
            ),
            "all_foreground_visible_rgb_matches_mother": all(
                item["checks"]["foreground_visible_rgb_matches_mother"] for item in regions.values()
            ),
            "all_foreground_pixel_regions_listed": all(
                item["checks"]["foreground_pixel_regions_listed"] for item in regions.values()
            ),
            "all_composites_close": all(item["checks"]["composite_mean_diff_under_2"] for item in regions.values()),
            "incoming_layout_clean": not any(path.exists() for path in deprecated_top_level),
            "temporary_source_deleted": not DEFAULT_SOURCE.exists(),
        },
        "regions": regions,
        "known_issues": sorted(
            {
                issue
                for region_audit in regions.values()
                for issue in region_audit["known_issues"]
            }
        ),
    }
    if write_audit:
        audit_root.mkdir(parents=True, exist_ok=True)
        (audit_root / "scene_mother_layers.json").write_text(
            json.dumps(audit, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    if errors:
        for error in errors[:20]:
            print(f"INVALID: {error}")
        if len(errors) > 20:
            print(f"... {len(errors) - 20} more errors")
        fail(f"{len(errors)} scene mother layer validation errors")

    return audit


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--incoming", type=Path, default=DEFAULT_INCOMING)
    parser.add_argument("--expect-source-deleted", action="store_true")
    parser.add_argument("--write-audit", action="store_true")
    args = parser.parse_args()

    audit = validate(args.incoming, args.expect_source_deleted, args.write_audit)
    print(
        "OK: greenfield P0 scene mother layers validate "
        f"regions={audit['region_count']} source_deleted={audit['checks_summary']['temporary_source_deleted']}"
    )


if __name__ == "__main__":
    main()
