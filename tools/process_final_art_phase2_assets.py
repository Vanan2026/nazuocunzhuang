from __future__ import annotations

import json
import shutil
import colorsys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_ROOT = ROOT / "production" / "assets" / "final_art"
SOURCE_DIR = OUT_ROOT / "generated_sources" / "phase2"
PROP_DIR = OUT_ROOT / "home_area" / "props"
NPC_DIR = OUT_ROOT / "characters" / "npc"
REPORT_DIR = ROOT / ".codex" / "reports"
SNAPSHOT_DIR = ROOT / ".codex"

MAGENTA_KEY = (255, 0, 255)


SOURCE_IMAGES = {
    "props": Path(
        r"C:\Users\23732\.codex\generated_images\019e2a26-d477-7f93-90fa-6c710230ada6"
        r"\ig_0d8abd327656471e016a06b74ba198819196fdc7a988f60e84.png"
    ),
    "aoi": Path(
        r"C:\Users\23732\.codex\generated_images\019e2a26-d477-7f93-90fa-6c710230ada6"
        r"\ig_0d8abd327656471e016a06b7c8cd3c8191a02e93465260764e.png"
    ),
    "gen": Path(
        r"C:\Users\23732\.codex\generated_images\019e2a26-d477-7f93-90fa-6c710230ada6"
        r"\ig_0d8abd327656471e016a06b800ab4081918c573787a18dbd9b.png"
    ),
    "mika": Path(
        r"C:\Users\23732\.codex\generated_images\019e2a26-d477-7f93-90fa-6c710230ada6"
        r"\ig_0d8abd327656471e016a06b840f80081918fcd63ec9168025e.png"
    ),
}


@dataclass(frozen=True)
class AssetSpec:
    source_sheet: str
    cell_index: int
    filename: str
    target_dir: Path
    width: int
    height: int
    anchor: str
    runtime_layer: str
    role: str
    source_prompt: str


PROP_SPECS = [
    AssetSpec("props", 0, "region_home_area_prop_mailbox_v001.png", PROP_DIR, 256, 256, "bottom_center", "YSortWorld/Props", "inspect_mailbox", "batch_c_interactable_props_v001.md"),
    AssetSpec("props", 1, "region_home_area_prop_well_broken_v001.png", PROP_DIR, 384, 384, "bottom_center", "YSortWorld/Props", "old_well_broken", "batch_c_interactable_props_v001.md"),
    AssetSpec("props", 2, "region_home_area_prop_well_repaired_v001.png", PROP_DIR, 384, 384, "bottom_center", "YSortWorld/Props", "old_well_repaired", "batch_c_interactable_props_v001.md"),
    AssetSpec("props", 3, "region_home_area_prop_bench_v001.png", PROP_DIR, 256, 192, "bottom_center", "YSortWorld/Props", "rest_bench", "batch_c_interactable_props_v001.md"),
    AssetSpec("props", 4, "region_home_area_prop_road_sign_v001.png", PROP_DIR, 256, 256, "bottom_center", "YSortWorld/Props", "read_sign", "batch_c_interactable_props_v001.md"),
]


NPC_SPECS = []
for npc_id in ["aoi", "gen", "mika"]:
    NPC_SPECS.extend(
        [
            AssetSpec(npc_id, 0, f"npc_{npc_id}_idle_down_128.png", NPC_DIR, 128, 128, "bottom_center", "YSortWorld/NPCs", f"{npc_id}_idle_down", "batch_d_npc_p0_v001.md"),
            AssetSpec(npc_id, 1, f"npc_{npc_id}_portrait_neutral_512.png", NPC_DIR, 512, 512, "center", "DialogueBox/Portrait", f"{npc_id}_portrait_neutral", "batch_d_npc_p0_v001.md"),
            AssetSpec(npc_id, 2, f"npc_{npc_id}_portrait_happy_512.png", NPC_DIR, 512, 512, "center", "DialogueBox/Portrait", f"{npc_id}_portrait_happy", "batch_d_npc_p0_v001.md"),
            AssetSpec(npc_id, 3, f"npc_{npc_id}_portrait_thinking_512.png", NPC_DIR, 512, 512, "center", "DialogueBox/Portrait", f"{npc_id}_portrait_thinking", "batch_d_npc_p0_v001.md"),
        ]
    )


def ensure_dirs() -> None:
    for directory in [SOURCE_DIR, PROP_DIR, NPC_DIR, REPORT_DIR, SNAPSHOT_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def copy_sources() -> dict[str, Path]:
    copied: dict[str, Path] = {}
    for key, source in SOURCE_IMAGES.items():
        destination = SOURCE_DIR / f"{key}_source_sheet.png"
        if not destination.exists():
            if not source.exists():
                raise FileNotFoundError(f"Missing source image for {key}: {source}")
            shutil.copy2(source, destination)
        copied[key] = destination
    return copied


def remove_chroma_key(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    pixels = rgba.load()
    width, height = rgba.size
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            magenta_distance = abs(r - MAGENTA_KEY[0]) + abs(g - MAGENTA_KEY[1]) + abs(b - MAGENTA_KEY[2])
            is_key = (r > 185 and b > 185 and g < 135) or (r > 210 and b > 210 and g < 150 and magenta_distance < 220)
            if is_key:
                pixels[x, y] = (r, g, b, 0)
            elif r > 150 and b > 150 and g < 120:
                pixels[x, y] = (r, g, b, min(a, 80))
    return rgba


def despill_magenta(image: Image.Image) -> Image.Image:
    output = image.copy()
    pixels = output.load()
    width, height = output.size
    outline = (90, 59, 42)
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if a == 0:
                continue
            hue, saturation, value = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
            degrees = hue * 360.0
            is_magenta = 285.0 <= degrees <= 335.0 and saturation > 0.28 and value > 0.18
            if is_magenta:
                if a < 180:
                    pixels[x, y] = (r, g, b, 0)
                else:
                    pixels[x, y] = (outline[0], outline[1], outline[2], a)
    return output


def keep_primary_components(image: Image.Image, min_fraction: float = 0.03) -> Image.Image:
    alpha = image.getchannel("A")
    width, height = image.size
    visited = bytearray(width * height)
    components: list[list[int]] = []

    def offset(px: int, py: int) -> int:
        return py * width + px

    for y in range(height):
        for x in range(width):
            start = offset(x, y)
            if visited[start] or alpha.getpixel((x, y)) == 0:
                continue
            stack = [(x, y)]
            visited[start] = 1
            current: list[int] = []
            while stack:
                cx, cy = stack.pop()
                current.append(offset(cx, cy))
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if nx < 0 or ny < 0 or nx >= width or ny >= height:
                        continue
                    item = offset(nx, ny)
                    if not visited[item] and alpha.getpixel((nx, ny)) > 0:
                        visited[item] = 1
                        stack.append((nx, ny))
            components.append(current)

    if not components:
        return image
    largest = max(len(component) for component in components)
    threshold = max(12, int(largest * min_fraction))
    keep = set()
    for component in components:
        if len(component) >= threshold:
            keep.update(component)

    output = image.copy()
    pixels = output.load()
    for y in range(height):
        for x in range(width):
            if offset(x, y) not in keep:
                r, g, b, _ = pixels[x, y]
                pixels[x, y] = (r, g, b, 0)
    return output


def alpha_bbox(image: Image.Image) -> tuple[int, int, int, int] | None:
    alpha = image.getchannel("A")
    return alpha.getbbox()


def split_sheet(sheet: Image.Image, count: int) -> list[Image.Image]:
    width, height = sheet.size
    cell_width = width // count
    cells: list[Image.Image] = []
    for index in range(count):
        left = index * cell_width
        right = width if index == count - 1 else (index + 1) * cell_width
        cells.append(sheet.crop((left, 0, right, height)))
    return cells


def fit_to_canvas(image: Image.Image, width: int, height: int, padding_ratio: float, component_fraction: float) -> tuple[Image.Image, dict]:
    image = despill_magenta(keep_primary_components(image, component_fraction))
    bbox = alpha_bbox(image)
    if bbox is None:
        raise ValueError("Cannot fit empty transparent image")
    cropped = image.crop(bbox)
    max_width = max(1, int(width * (1.0 - padding_ratio)))
    max_height = max(1, int(height * (1.0 - padding_ratio)))
    scale = min(max_width / cropped.width, max_height / cropped.height)
    resized = cropped.resize((max(1, int(cropped.width * scale)), max(1, int(cropped.height * scale))), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    x = (width - resized.width) // 2
    y = height - resized.height - max(4, int(height * 0.04))
    if height == width and width >= 512:
        y = (height - resized.height) // 2
    canvas.alpha_composite(resized, (x, y))
    return canvas, {
        "source_bbox": list(bbox),
        "trimmed_size": [cropped.width, cropped.height],
        "scale": scale,
        "placed_at": [x, y],
        "placed_size": [resized.width, resized.height],
    }


def analyze_image(path: Path) -> dict:
    image = Image.open(path).convert("RGBA")
    alpha = image.getchannel("A")
    alpha_values = alpha.getdata()
    transparent = sum(1 for value in alpha_values if value == 0)
    translucent = sum(1 for value in alpha_values if 0 < value < 255)
    opaque = sum(1 for value in alpha_values if value == 255)
    corners = [alpha.getpixel((0, 0)), alpha.getpixel((image.width - 1, 0)), alpha.getpixel((0, image.height - 1)), alpha.getpixel((image.width - 1, image.height - 1))]
    bbox = alpha_bbox(image)
    return {
        "width": image.width,
        "height": image.height,
        "mode": image.mode,
        "has_alpha": True,
        "transparent_pixels": transparent,
        "translucent_pixels": translucent,
        "opaque_pixels": opaque,
        "transparent_corners": all(value == 0 for value in corners),
        "alpha_bbox": list(bbox) if bbox else None,
    }


def process_assets(sources: dict[str, Path]) -> list[dict]:
    sheets = {key: remove_chroma_key(Image.open(path)) for key, path in sources.items()}
    cells = {"props": split_sheet(sheets["props"], 5)}
    for npc_id in ["aoi", "gen", "mika"]:
        cells[npc_id] = split_sheet(sheets[npc_id], 4)

    records: list[dict] = []
    for spec in PROP_SPECS + NPC_SPECS:
        padding = 0.16 if spec.width <= 256 else 0.08
        if "portrait" in spec.filename:
            padding = 0.04
        component_fraction = 0.12 if spec.target_dir == PROP_DIR else 0.03
        canvas, fit_meta = fit_to_canvas(cells[spec.source_sheet][spec.cell_index], spec.width, spec.height, padding, component_fraction)
        output = spec.target_dir / spec.filename
        canvas.save(output)
        analysis = analyze_image(output)
        records.append(
            {
                "file": str(output.relative_to(ROOT)).replace("\\", "/"),
                "status": "generated_phase2",
                "source_sheet": str(sources[spec.source_sheet].relative_to(ROOT)).replace("\\", "/"),
                "source_prompt": f"production/assets/final_art/prompts/{spec.source_prompt}",
                "size_px": {"width": spec.width, "height": spec.height},
                "anchor": spec.anchor,
                "anchor_px": {"x": spec.width // 2, "y": spec.height - 1} if spec.anchor == "bottom_center" else {"x": spec.width // 2, "y": spec.height // 2},
                "target_parent": spec.runtime_layer,
                "role": spec.role,
                "fit": fit_meta,
                "alpha_check": analysis,
            }
        )
    return records


def create_contact_sheet(records: list[dict], suffix: str, scale: float) -> Path:
    thumbs: list[tuple[str, Image.Image]] = []
    for record in records:
        path = ROOT / record["file"]
        image = Image.open(path).convert("RGBA")
        thumb = image.resize((max(1, int(image.width * scale)), max(1, int(image.height * scale))), Image.Resampling.LANCZOS)
        thumbs.append((Path(record["file"]).name, thumb))

    cell_w = 180 if scale <= 0.5 else 560
    cell_h = 180 if scale <= 0.5 else 560
    if suffix == "gameplay":
        cell_w, cell_h = 128, 128
    cols = 5
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cell_w, rows * cell_h), (243, 231, 209, 255))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 11)
    except OSError:
        font = ImageFont.load_default()

    for index, (name, thumb) in enumerate(thumbs):
        col = index % cols
        row = index // cols
        x = col * cell_w + (cell_w - thumb.width) // 2
        y = row * cell_h + 10
        checker = Image.new("RGBA", (cell_w - 12, cell_h - 34), (255, 255, 255, 255))
        checker_draw = ImageDraw.Draw(checker)
        step = 12
        for cy in range(0, checker.height, step):
            for cx in range(0, checker.width, step):
                if (cx // step + cy // step) % 2 == 0:
                    checker_draw.rectangle((cx, cy, cx + step - 1, cy + step - 1), fill=(225, 218, 205, 255))
        sheet.alpha_composite(checker, (col * cell_w + 6, row * cell_h + 6))
        sheet.alpha_composite(thumb, (x, y))
        draw.text((col * cell_w + 8, row * cell_h + cell_h - 24), name[:28], fill=(90, 59, 42, 255), font=font)
    path = SNAPSHOT_DIR / f"final_art_phase2_contact_sheet_{suffix}.png"
    sheet.convert("RGB").save(path)
    return path


def write_manifest(records: list[dict]) -> None:
    manifest = {
        "package_id": "final_art_phase2_batch_c_d",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "runtime_replacement": False,
        "source_mode": "built_in_imagegen_chroma_key_removed_locally",
        "batches": {
            "batch_c_interactable_props": [record for record in records if "/home_area/props/" in record["file"]],
            "batch_d_npc_p0": [record for record in records if "/characters/npc/" in record["file"]],
        },
    }
    (OUT_ROOT / "final_art_phase2_batch_c_d_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def write_report(records: list[dict], contact_sheets: list[Path]) -> None:
    godot_snapshot = SNAPSHOT_DIR / "final_art_phase2_godot_snapshot.png"
    lines = [
        "# Final Art Phase 2 Validation Report",
        "",
        f"更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Summary",
        "",
        f"- Generated assets: {len(records)}",
        "- Source mode: built-in imagegen chroma-key sheets, local alpha extraction and crop normalization",
        "- Runtime references changed: no",
        "",
        "## Contact Sheets",
        "",
    ]
    for path in contact_sheets:
        lines.append(f"- `{str(path.relative_to(ROOT)).replace('\\', '/')}`")
    if godot_snapshot.exists():
        lines.append(f"- `{str(godot_snapshot.relative_to(ROOT)).replace('\\', '/')}`")
    lines.extend(["", "## Asset Checks", "", "| File | Size | Alpha | Transparent corners | BBox |", "|---|---:|---|---|---|"])
    for record in records:
        check = record["alpha_check"]
        lines.append(
            f"| `{record['file']}` | {check['width']}x{check['height']} | yes | {check['transparent_corners']} | {check['alpha_bbox']} |"
        )
    lines.extend(
        [
            "",
            "## Known Limits",
            "",
            "- These assets are generated production candidates, not wired into runtime scenes yet.",
            "- Visual quality was checked by source/contact sheet review, alpha metadata, and the Godot preview snapshot when present.",
        ]
    )
    (REPORT_DIR / "final_art_phase2_validation_2026-05-15.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ensure_dirs()
    sources = copy_sources()
    records = process_assets(sources)
    write_manifest(records)
    contact_sheets = [
        create_contact_sheet(records, "100", 1.0),
        create_contact_sheet(records, "50", 0.5),
        create_contact_sheet(records, "gameplay", 0.25),
    ]
    write_report(records, contact_sheets)
    print(json.dumps({"generated": len(records), "manifest": str((OUT_ROOT / "final_art_phase2_batch_c_d_manifest.json").relative_to(ROOT))}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
