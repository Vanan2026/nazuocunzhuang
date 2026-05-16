from __future__ import annotations

import json
import struct
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / ".codex" / "reports"


SEARCH_ROOTS = [
    ROOT / "production" / "assets" / "regions" / "home_area_art",
    ROOT / "production" / "assets" / "regions" / "home_area_launch",
    ROOT / "sprites" / "environments" / "homeyard",
    ROOT / "sprites" / "environments" / "regions" / "home_area",
    ROOT / "production" / "assets" / "protagonist",
    ROOT / "sprites" / "characters" / "protagonist",
    ROOT / "assets" / "art",
    ROOT / "production" / "assets" / "final_art",
]


EXPECTED_BATCHES = {
    "home_area_foundation": [
        "region_home_area_base_full_v001.png",
        "region_home_area_ground_yard_v001.png",
        "region_home_area_path_village_road_v001.png",
        "region_home_area_path_back_farm_v001.png",
        "region_home_area_house_body_v001.png",
        "region_home_area_house_roof_occluder_v001.png",
        "region_home_area_veranda_floor_v001.png",
    ],
    "home_area_depth": [
        "region_home_area_tree_left_trunk_v001.png",
        "region_home_area_tree_left_canopy_occluder_v001.png",
        "region_home_area_tree_right_trunk_v001.png",
        "region_home_area_tree_right_canopy_occluder_v001.png",
        "region_home_area_foreground_grass_v001.png",
        "region_home_area_shadow_dappled_v001.png",
        "region_home_area_light_overlay_v001.png",
    ],
    "home_area_props": [
        "region_home_area_prop_mailbox_v001.png",
        "region_home_area_prop_well_broken_v001.png",
        "region_home_area_prop_well_repaired_v001.png",
        "region_home_area_prop_bench_v001.png",
        "region_home_area_prop_road_sign_v001.png",
    ],
    "npc_p0": [
        "npc_aoi_idle_down_128.png",
        "npc_aoi_portrait_neutral_512.png",
        "npc_aoi_portrait_happy_512.png",
        "npc_aoi_portrait_thinking_512.png",
        "npc_gen_idle_down_128.png",
        "npc_gen_portrait_neutral_512.png",
        "npc_gen_portrait_happy_512.png",
        "npc_gen_portrait_thinking_512.png",
        "npc_mika_idle_down_128.png",
        "npc_mika_portrait_neutral_512.png",
        "npc_mika_portrait_happy_512.png",
        "npc_mika_portrait_thinking_512.png",
    ],
    "ui_and_crops": [
        "ui_icon_weather_sunny_64.png",
        "ui_icon_weather_cloudy_64.png",
        "ui_icon_weather_rainy_64.png",
        "crop_turnip_stage_00_64.png",
        "crop_turnip_stage_01_64.png",
        "crop_turnip_stage_02_64.png",
        "crop_turnip_stage_03_64.png",
        "crop_strawberry_stage_00_64.png",
        "crop_strawberry_stage_01_64.png",
        "crop_strawberry_stage_02_64.png",
        "crop_strawberry_stage_03_64.png",
        "ui_panel_paper_9slice.png",
        "ui_button_default.png",
    ],
}


@dataclass(frozen=True)
class PngInfo:
    path: Path
    width: int
    height: int
    color_type: int
    size_bytes: int

    @property
    def has_alpha(self) -> bool:
        return self.color_type in {4, 6}


def read_png_info(path: Path) -> PngInfo | None:
    try:
        with path.open("rb") as file:
            header = file.read(33)
    except OSError:
        return None
    if len(header) < 33 or header[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    width, height = struct.unpack(">II", header[16:24])
    color_type = header[25]
    return PngInfo(
        path=path,
        width=width,
        height=height,
        color_type=color_type,
        size_bytes=path.stat().st_size,
    )


def normalize_key(filename: str) -> str:
    key = filename.lower().removesuffix(".png")
    for token in ["_v001", "_v002", "_01", "_default", "_preview"]:
        key = key.replace(token, "")
    return key


def collect_pngs() -> list[PngInfo]:
    results: list[PngInfo] = []
    for root in SEARCH_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*.png"):
            if path.name.endswith(".import"):
                continue
            info = read_png_info(path)
            if info is not None:
                results.append(info)
    return sorted(results, key=lambda item: str(item.path.relative_to(ROOT)).lower())


def find_candidates(expected: str, pngs: list[PngInfo]) -> list[PngInfo]:
    expected_key = normalize_key(expected)
    expected_tokens = [token for token in expected_key.split("_") if token not in {"region", "home", "area"}]
    candidates: list[tuple[int, PngInfo]] = []
    for png in pngs:
        key = normalize_key(png.path.name)
        score = 0
        if key == expected_key:
            score += 100
        if expected_key in key or key in expected_key:
            score += 40
        score += sum(1 for token in expected_tokens if token and token in key) * 8
        if "rejected" in str(png.path).lower() or "launch\\v001" in str(png.path).lower():
            score -= 20
        if score >= 24:
            candidates.append((score, png))
    return [png for _, png in sorted(candidates, key=lambda item: (-item[0], str(item[1].path)))[:5]]


def classify(expected: str, candidates: list[PngInfo]) -> str:
    if not candidates:
        return "regenerate"
    best = candidates[0]
    path_text = str(best.path).replace("/", "\\").lower()
    if "production\\assets\\final_art" in path_text and best.path.name.lower() == expected.lower():
        return "generated_candidate"
    if "home_area_art\\v001" in path_text or "home_area_art\\v002" in path_text:
        return "reuse_or_repair"
    if "home_area_launch\\v001" in path_text:
        return "repair_only_rejected_composition_source"
    if expected.startswith(("npc_", "crop_", "ui_icon_weather")):
        return "regenerate"
    return "repair"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def build_report() -> tuple[dict, str]:
    pngs = collect_pngs()
    batches: dict[str, list[dict]] = {}
    for batch, expected_assets in EXPECTED_BATCHES.items():
        rows: list[dict] = []
        for expected in expected_assets:
            candidates = find_candidates(expected, pngs)
            rows.append(
                {
                    "asset": expected,
                    "status": classify(expected, candidates),
                    "candidates": [
                        {
                            "path": rel(candidate.path),
                            "width": candidate.width,
                            "height": candidate.height,
                            "has_alpha": candidate.has_alpha,
                            "size_bytes": candidate.size_bytes,
                        }
                        for candidate in candidates
                    ],
                }
            )
        batches[batch] = rows

    summary = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pngs_scanned": len(pngs),
        "batches": batches,
    }

    lines = [
        "# Final Art Asset Audit",
        "",
        f"更新时间：{summary['timestamp']}",
        "",
        f"- PNG scanned: {len(pngs)}",
        "- Status meanings: `generated_candidate` = exact final_art candidate exists; `reuse_or_repair` = likely usable source but still needs visual gate; `repair` = candidate exists but naming/layer contract likely needs work; `regenerate` = no reliable final candidate found.",
        "",
    ]
    for batch, rows in batches.items():
        lines.append(f"## {batch}")
        lines.append("")
        lines.append("| Asset | Status | Best candidates |")
        lines.append("|---|---|---|")
        for row in rows:
            candidates = row["candidates"]
            if candidates:
                candidate_text = "<br>".join(
                    f"`{item['path']}` ({item['width']}x{item['height']}, alpha={item['has_alpha']})"
                    for item in candidates[:3]
                )
            else:
                candidate_text = "None"
            lines.append(f"| `{row['asset']}` | {row['status']} | {candidate_text} |")
        lines.append("")

    return summary, "\n".join(lines).rstrip() + "\n"


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    summary, markdown = build_report()
    (REPORT_DIR / "final_art_asset_audit_2026-05-15.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (REPORT_DIR / "final_art_asset_audit_2026-05-15.md").write_text(markdown, encoding="utf-8")
    print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
