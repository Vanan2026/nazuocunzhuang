from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "production" / "assets" / "base_asset_pack" / "v001"
WORKFLOW_MANIFEST = PACKAGE / "workflow_manifest.json"
HANDOFF = ROOT / "production" / "assets" / "external_gpt_handoff" / "greenfield_p0" / "v001"
INCOMING = HANDOFF / "incoming"

STYLE_LOCK = (
    "Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, "
    "clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, "
    "cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD."
)

NEGATIVE_PROMPT = (
    "Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, "
    "no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, "
    "no heavy black shadows, no random crop, no wrong perspective, no visible watermark."
)


def load_manifest() -> dict:
    if not WORKFLOW_MANIFEST.exists():
        raise SystemExit(f"missing workflow manifest: {WORKFLOW_MANIFEST}")
    return json.loads(WORKFLOW_MANIFEST.read_text(encoding="utf-8"))


def ensure_dirs() -> None:
    for relative in [
        "01_mother_images/style",
        "01_mother_images/characters",
        "01_mother_images/props",
        "01_mother_images/ui/screens",
        "01_mother_images/regions",
        "02_runtime_exports/characters/player",
        "02_runtime_exports/characters/npc",
        "02_runtime_exports/portraits",
        "02_runtime_exports/regions",
        "02_runtime_exports/tiles",
        "02_runtime_exports/crops",
        "02_runtime_exports/items",
        "02_runtime_exports/props",
        "02_runtime_exports/ui",
        "02_runtime_exports/fx",
    ]:
        (INCOMING / relative).mkdir(parents=True, exist_ok=True)


def png_size(path: Path) -> tuple[list[int], str]:
    try:
        from PIL import Image
    except Exception as exc:  # pragma: no cover - environment diagnostic
        raise SystemExit(f"Pillow is required to inspect package images: {exc}") from exc
    with Image.open(path) as image:
        return list(image.size), image.mode


def incoming_path_for(package_relative_path: str) -> str:
    marker = "base_asset_pack/v001/"
    if marker in package_relative_path:
        return package_relative_path.split(marker, 1)[1]
    return package_relative_path


def prompt_for(asset_id: str, category: str, size: list[int], transparent: bool) -> str:
    alpha_note = "transparent background with clean alpha" if transparent else "fully opaque complete review image"
    size_note = f"exact canvas {size[0]}x{size[1]} px"
    if category == "region_layer":
        return (
            f"{STYLE_LOCK} Paint one modular region runtime layer for {asset_id}; {size_note}; "
            f"{alpha_note}; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text."
        )
    if category == "region_mother":
        return (
            f"{STYLE_LOCK} Paint a complete region source/review mother for {asset_id}; {size_note}; "
            f"{alpha_note}; believable village-space layout, readable roads, props beside paths, no impossible overlaps."
        )
    if category == "character":
        return (
            f"{STYLE_LOCK} Create compact 3.5 to 4-head gameplay character sprite asset for {asset_id}; "
            f"{size_note}; {alpha_note}; stable foot anchor, simple rounded shapes, readable at small size."
        )
    if category == "portrait":
        return (
            f"{STYLE_LOCK} Create a dialogue portrait for {asset_id}; {size_note}; {alpha_note}; "
            "gentle expression, clear face, same character identity as the sprite set."
        )
    if category == "tile":
        return (
            f"{STYLE_LOCK} Create a seamless or edge-safe ground tile for {asset_id}; {size_note}; "
            f"{alpha_note}; readable material pattern without noisy detail."
        )
    if category == "crop":
        return (
            f"{STYLE_LOCK} Create a crop growth-stage sprite for {asset_id}; {size_note}; "
            f"{alpha_note}; readable plant stage, centered on tile footprint."
        )
    if category == "item":
        return (
            f"{STYLE_LOCK} Create an inventory item icon for {asset_id}; {size_note}; "
            f"{alpha_note}; simple object silhouette, readable at 64 px."
        )
    if category == "ui":
        return (
            f"{STYLE_LOCK} Create hand-drawn paper/wood UI asset for {asset_id}; {size_note}; "
            f"{alpha_note}; quiet utilitarian game UI, no baked text unless explicitly requested."
        )
    if category == "ui_screen":
        return (
            f"{STYLE_LOCK} Create a UI screen mother layout for {asset_id}; {size_note}; "
            f"{alpha_note}; paper/wood diary style, dense but readable game interface, no real text labels required."
        )
    if category == "prop":
        return (
            f"{STYLE_LOCK} Create a reusable world prop for {asset_id}; {size_note}; "
            f"{alpha_note}; bottom-center anchor, clear physical base, 3/4 top-down rural object."
        )
    if category == "fx":
        return (
            f"{STYLE_LOCK} Create a soft environmental FX overlay for {asset_id}; {size_note}; "
            f"{alpha_note}; subtle and reusable, suitable for compositing."
        )
    return f"{STYLE_LOCK} Create {asset_id}; {size_note}; {alpha_note}."


def infer_category(path: str) -> str:
    if "/regions/" in path and "/layers/" in path:
        return "region_layer"
    if "/01_mother_images/regions/" in path:
        return "region_mother"
    if "/characters/" in path:
        return "character"
    if "/portraits/" in path:
        return "portrait"
    if "/tiles/" in path:
        return "tile"
    if "/crops/" in path:
        return "crop"
    if "/items/" in path:
        return "item"
    if "/ui/screens/" in path:
        return "ui_screen"
    if "/ui/" in path:
        return "ui"
    if "/props/" in path:
        return "prop"
    if "/fx/" in path:
        return "fx"
    return "support"


def append_asset(assets: list[dict], *, asset_id: str, package_path: str, transparent: bool, priority: str, notes: str = "") -> None:
    source = ROOT / package_path
    size, mode = png_size(source)
    category = infer_category(package_path)
    target = incoming_path_for(package_path)
    assets.append({
        "asset_id": asset_id,
        "category": category,
        "priority": priority,
        "incoming_path": target,
        "reference_package_path": package_path,
        "expected_size": size,
        "expected_mode": "RGBA",
        "transparent": transparent,
        "prompt": prompt_for(asset_id, category, size, transparent),
        "negative_prompt": NEGATIVE_PROMPT,
        "acceptance": [
            "Exact PNG filename and relative directory path.",
            "Exact canvas size.",
            "Correct alpha rule for transparent versus opaque asset.",
            "Fixed 3/4 top-down cozy rural storybook style.",
            "Readable at the intended runtime scale.",
            "No copied named franchise, no watermark, no baked unwanted text.",
        ],
        "notes": notes,
    })


def build_assets(manifest: dict) -> list[dict]:
    assets: list[dict] = []
    append_asset(
        assets,
        asset_id="greenfield_p0_style_mother",
        package_path=manifest["source_mothers"]["style"]["path"],
        transparent=False,
        priority="batch_a_style_lock",
        notes="Use this to establish the shared palette, line weight, brush texture, and shape language.",
    )
    for screen in manifest.get("ui_screens", []):
        append_asset(
            assets,
            asset_id=f"ui_screen_{screen['id']}",
            package_path=screen["production_path"],
            transparent=False,
            priority="batch_a_style_lock",
            notes="Screen mother for UI layout direction. It is not a final interactive scene.",
        )
    for region in manifest["regions"]:
        append_asset(
            assets,
            asset_id=f"{region['region_id']}_painted_source",
            package_path=region["painted_source"],
            transparent=False,
            priority="batch_b_regions",
            notes="Primary region source/review image. Preserve spatial logic from the manifest layout profile.",
        )
        for layer_id, record in region["layers"].items():
            if layer_id == "light_weather_overlays":
                for overlay in record:
                    append_asset(
                        assets,
                        asset_id=f"{region['region_id']}_light_weather_overlay_{overlay['season']}",
                        package_path=overlay["production_path"],
                        transparent=True,
                        priority="batch_b_regions",
                    )
                continue
            append_asset(
                assets,
                asset_id=f"{region['region_id']}_{layer_id}",
                package_path=record["production_path"],
                transparent=layer_id != "base_ground",
                priority="batch_b_regions",
            )
    for record in manifest["characters"]["player_records"]:
        append_asset(
            assets,
            asset_id=f"player_{record['action']}_{record['direction']}",
            package_path=record["production_path"],
            transparent=True,
            priority="batch_c_characters",
        )
    for record in manifest["characters"]["npc_records"]:
        if "portrait" in record:
            asset_id = f"npc_{record['id']}_portrait_{record['portrait']}"
            transparent = False
        else:
            asset_id = f"npc_{record['id']}_{record['action']}_{record['direction']}"
            transparent = True
        append_asset(
            assets,
            asset_id=asset_id,
            package_path=record["production_path"],
            transparent=transparent,
            priority="batch_c_characters",
        )
    for group, priority in [
        ("tiles", "batch_d_system_assets"),
        ("crops", "batch_d_system_assets"),
        ("items", "batch_d_system_assets"),
        ("props", "batch_d_system_assets"),
        ("ui", "batch_d_system_assets"),
        ("fx", "batch_d_system_assets"),
    ]:
        records = manifest[group]["records"] if group == "tiles" else manifest[group]
        for index, record in enumerate(records):
            asset_id = record.get("id") or record.get("crop_id") or Path(record["production_path"]).stem
            append_asset(
                assets,
                asset_id=str(asset_id),
                package_path=record["production_path"],
                transparent=True,
                priority=priority,
            )
    return assets


def write_request_manifest(assets: list[dict]) -> None:
    payload = {
        "package_id": "greenfield_p0_external_gpt_asset_request_v001",
        "source_package_id": "greenfield_p0_base_asset_pack_v001",
        "status": "ready_for_external_generation",
        "incoming_root": str(INCOMING.relative_to(ROOT)).replace("\\", "/"),
        "style_lock": STYLE_LOCK,
        "negative_prompt": NEGATIVE_PROMPT,
        "batch_order": [
            "batch_a_style_lock",
            "batch_b_regions",
            "batch_c_characters",
            "batch_d_system_assets",
        ],
        "assets": assets,
    }
    (HANDOFF / "asset_request_manifest.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(assets: list[dict]) -> None:
    with (HANDOFF / "asset_request_table.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "priority",
            "category",
            "asset_id",
            "incoming_path",
            "expected_size",
            "transparent",
            "prompt",
            "negative_prompt",
        ])
        writer.writeheader()
        for asset in assets:
            writer.writerow({
                "priority": asset["priority"],
                "category": asset["category"],
                "asset_id": asset["asset_id"],
                "incoming_path": asset["incoming_path"],
                "expected_size": f"{asset['expected_size'][0]}x{asset['expected_size'][1]}",
                "transparent": asset["transparent"],
                "prompt": asset["prompt"],
                "negative_prompt": asset["negative_prompt"],
            })


def write_prompt_briefs(assets: list[dict]) -> None:
    grouped: dict[str, list[dict]] = {}
    for asset in assets:
        grouped.setdefault(asset["priority"], []).append(asset)
    lines = [
        "# Greenfield P0 External GPT Asset Request",
        "",
        "Do not mention or depend on a specific generation model. Use the prompt and file contract only.",
        "",
        "## Shared Style Lock",
        STYLE_LOCK,
        "",
        "## Global Negative Prompt",
        NEGATIVE_PROMPT,
        "",
        "## Incoming Root",
        f"`{INCOMING.relative_to(ROOT)}`",
        "",
        "Keep every generated PNG at the exact relative path listed below.",
        "",
    ]
    for priority, group_assets in grouped.items():
        lines.extend([f"## {priority}", ""])
        for asset in group_assets:
            size = asset["expected_size"]
            lines.extend([
                f"### {asset['asset_id']}",
                f"- Path: `{asset['incoming_path']}`",
                f"- Size: `{size[0]}x{size[1]}`",
                f"- Transparent: `{asset['transparent']}`",
                f"- Prompt: {asset['prompt']}",
                f"- Negative: {asset['negative_prompt']}",
                "",
            ])
    (HANDOFF / "prompt_briefs.md").write_text("\n".join(lines), encoding="utf-8")


def write_readme(assets: list[dict]) -> None:
    batch_counts: dict[str, int] = {}
    for asset in assets:
        batch_counts[asset["priority"]] = batch_counts.get(asset["priority"], 0) + 1
    lines = [
        "# Greenfield P0 External Asset Handoff",
        "",
        "This folder is the handoff contract for externally generated Greenfield P0 art assets.",
        "",
        "Workflow:",
        "1. Codex writes detailed asset requests and exact incoming paths here.",
        "2. The user generates PNGs externally from the request.",
        "3. The user drops PNGs under `incoming/` with the exact relative paths.",
        "4. Codex runs the intake validator, imports accepted assets, regenerates contact sheets/review scenes, and continues Godot development.",
        "",
        "No generation model is named or required by this contract. The contract is path, size, alpha, style, and gameplay-readability based.",
        "",
        "## Files",
        "- `asset_request_manifest.json`: machine-readable full request and acceptance contract.",
        "- `asset_request_table.csv`: spreadsheet-friendly request table.",
        "- `prompt_briefs.md`: human-readable prompt list grouped by batch.",
        "- `incoming/`: drop generated PNGs here, preserving listed paths.",
        "",
        "## Batch Counts",
    ]
    for priority, count in sorted(batch_counts.items()):
        lines.append(f"- `{priority}`: {count} assets")
    lines.extend([
        "",
        "## Validate Intake",
        "",
        "Partial batch:",
        "```powershell",
        "py -3.12 tools\\validate_greenfield_p0_external_asset_intake.py --allow-partial",
        "```",
        "",
        "Strict full package:",
        "```powershell",
        "py -3.12 tools\\validate_greenfield_p0_external_asset_intake.py",
        "```",
        "",
        "Use any Python that has Pillow installed; on this machine `py -3.12` is the verified command.",
    ])
    (HANDOFF / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    manifest = load_manifest()
    HANDOFF.mkdir(parents=True, exist_ok=True)
    ensure_dirs()
    assets = build_assets(manifest)
    write_request_manifest(assets)
    write_csv(assets)
    write_prompt_briefs(assets)
    write_readme(assets)
    print(f"OK: wrote external asset request for {len(assets)} assets")
    print(HANDOFF)


if __name__ == "__main__":
    main()
