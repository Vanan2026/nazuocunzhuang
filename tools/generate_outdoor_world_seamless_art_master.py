from __future__ import annotations

import json
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "production" / "assets" / "outdoor_world_world2d" / "v001"
LAYOUT_DIR = PACKAGE_DIR / "01_world_layout"
SOURCE_DIR = PACKAGE_DIR / "02_source_strategy"
CONTRACT_DIR = PACKAGE_DIR / "03_region_contracts"
REVIEW_DIR = PACKAGE_DIR / "04_review_and_qa"

WORKFLOW = PACKAGE_DIR / "workflow_manifest.json"
README = PACKAGE_DIR / "README.md"
LAYOUT_LOCK = LAYOUT_DIR / "outdoor_world_layout_lock.json"
BLUEPRINT_SVG = LAYOUT_DIR / "outdoor_world_seamless_blueprint.svg"
BLUEPRINT_PNG = LAYOUT_DIR / "outdoor_world_seamless_blueprint.png"
BLUEPRINT_MD = LAYOUT_DIR / "outdoor_world_seamless_blueprint.md"
SOURCE_STRATEGY = SOURCE_DIR / "source_generation_strategy.md"
CHUNK_CONTRACT = CONTRACT_DIR / "region_chunk_contract.json"
REVIEW_GATE = REVIEW_DIR / "review_gate.md"

RUNTIME_SCALE = 0.18
GENERATED_SOURCE_CANVAS = [1800, 1200]
GENERATED_RUNTIME_SIZE = [320, 240]


REGIONS = [
    {
        "region_id": "player_yard",
        "display_name": "PlayerYard",
        "offset": [0, 0],
        "bounds": [-40, -96, 372, 408],
        "status": "active_authored_blockout",
        "source_status": "separate_home_area_chain",
        "priority": "P0",
    },
    {
        "region_id": "forest_edge",
        "display_name": "ForestEdge",
        "offset": [380, -12],
        "bounds": [332, -108, 340, 320],
        "status": "active_authored_blockout",
        "source_status": "needs_future_world2d_source",
        "priority": "P1",
    },
    {
        "region_id": "village",
        "display_name": "Village",
        "offset": [720, -12],
        "bounds": [720, -12, 320, 240],
        "status": "active_authored_slice_plus_generated_layers",
        "source_status": "layout_draft_only_not_final_painted_source",
        "priority": "P0",
    },
    {
        "region_id": "back_farm",
        "display_name": "BackFarm",
        "offset": [0, 324],
        "bounds": [0, 324, 320, 240],
        "status": "generated_shell_deferred",
        "source_status": "defer_until_player_verb_lock",
        "priority": "P2",
    },
    {
        "region_id": "orchard",
        "display_name": "Orchard",
        "offset": [380, 324],
        "bounds": [380, 324, 320, 240],
        "status": "generated_shell_deferred",
        "source_status": "defer_until_daily_loop",
        "priority": "P2",
    },
    {
        "region_id": "pond",
        "display_name": "Pond",
        "offset": [720, 324],
        "bounds": [720, 324, 320, 240],
        "status": "generated_shell_deferred",
        "source_status": "defer_until_daily_activity_loop",
        "priority": "P2",
    },
    {
        "region_id": "mountain_path",
        "display_name": "MountainPath",
        "offset": [720, -316],
        "bounds": [720, -316, 320, 240],
        "status": "generated_shell_deferred",
        "source_status": "defer_until_exploration_escalation_loop",
        "priority": "P2",
    },
    {
        "region_id": "mountain_hut",
        "display_name": "MountainHut",
        "offset": [1060, -12],
        "bounds": [1060, -12, 320, 240],
        "status": "generated_shell_deferred",
        "source_status": "defer_until_mountain_route_lock",
        "priority": "P3",
    },
    {
        "region_id": "mountain",
        "display_name": "Mountain",
        "offset": [1060, -316],
        "bounds": [1060, -316, 320, 240],
        "status": "generated_shell_deferred",
        "source_status": "defer_until_route_lock",
        "priority": "P3",
    },
    {
        "region_id": "cliff_view",
        "display_name": "CliffView",
        "offset": [1400, -316],
        "bounds": [1400, -316, 320, 240],
        "status": "generated_shell_deferred",
        "source_status": "defer_until_discovery_location_lock",
        "priority": "P3",
    },
]


CONNECTIONS = [
    {
        "id": "yard_to_forest_edge",
        "from": "player_yard",
        "to": "forest_edge",
        "points": [[300, 96], [332, 96], [380, 110]],
        "role": "current_first_week_forest_route",
    },
    {
        "id": "yard_to_village",
        "from": "player_yard",
        "to": "village",
        "points": [[300, 132], [500, 132], [720, 120]],
        "role": "current_village_entry_route",
    },
    {
        "id": "yard_to_back_farm",
        "from": "player_yard",
        "to": "back_farm",
        "points": [[150, 280], [150, 324]],
        "role": "future_farm_work_route",
    },
    {
        "id": "back_farm_to_orchard",
        "from": "back_farm",
        "to": "orchard",
        "points": [[320, 444], [380, 444]],
        "role": "future_workland_lane",
    },
    {
        "id": "orchard_to_pond",
        "from": "orchard",
        "to": "pond",
        "points": [[700, 444], [720, 444]],
        "role": "future_daily_activity_lane",
    },
    {
        "id": "village_to_pond",
        "from": "village",
        "to": "pond",
        "points": [[880, 228], [880, 324]],
        "role": "future_south_village_exit",
    },
    {
        "id": "village_to_mountain_path",
        "from": "village",
        "to": "mountain_path",
        "points": [[880, -12], [880, -76]],
        "role": "future_north_village_exit",
    },
    {
        "id": "village_to_mountain_hut",
        "from": "village",
        "to": "mountain_hut",
        "points": [[1040, 108], [1060, 108]],
        "role": "future_east_village_extension",
    },
    {
        "id": "mountain_path_to_mountain",
        "from": "mountain_path",
        "to": "mountain",
        "points": [[1040, -196], [1060, -196]],
        "role": "future_exploration_lane",
    },
    {
        "id": "mountain_to_cliff_view",
        "from": "mountain",
        "to": "cliff_view",
        "points": [[1380, -196], [1400, -196]],
        "role": "future_discovery_overlook_lane",
    },
    {
        "id": "mountain_to_hut",
        "from": "mountain",
        "to": "mountain_hut",
        "points": [[1220, -76], [1220, -12]],
        "role": "future_hut_return_lane",
    },
]


def ensure_dirs() -> None:
    for path in [PACKAGE_DIR, LAYOUT_DIR, SOURCE_DIR, CONTRACT_DIR, REVIEW_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def world_bounds() -> dict[str, int]:
    min_x = min(region["bounds"][0] for region in REGIONS)
    min_y = min(region["bounds"][1] for region in REGIONS)
    max_x = max(region["bounds"][0] + region["bounds"][2] for region in REGIONS)
    max_y = max(region["bounds"][1] + region["bounds"][3] for region in REGIONS)
    return {
        "min_x": min_x,
        "min_y": min_y,
        "max_x": max_x,
        "max_y": max_y,
        "width": max_x - min_x,
        "height": max_y - min_y,
    }


def region_center(region_id: str) -> list[int]:
    region = next(item for item in REGIONS if item["region_id"] == region_id)
    x, y, w, h = region["bounds"]
    return [int(x + w / 2), int(y + h / 2)]


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_workflow() -> None:
    payload = {
        "package_id": "outdoor_world_world2d_v001",
        "status": "master_blueprint_ready_not_runtime_replacement",
        "created_at": "2026-05-24",
        "active_runtime_scene": "res://game/scenes/world/OutdoorWorld.tscn",
        "active_runtime_source": "game/scenes/world/OutdoorWorld.gd",
        "runtime_replacement": False,
        "launch_quality_approved": False,
        "human_visual_approval_required": True,
        "current_phase": "01_world_layout",
        "purpose": "Global seamless 2D art contract for current OutdoorWorld before final per-region painted sources.",
        "coordinate_policy": {
            "world_space": "Godot runtime coordinates from OutdoorWorld REGION_OFFSETS and REGION_SIZES",
            "generated_region_source_canvas": GENERATED_SOURCE_CANVAS,
            "generated_region_runtime_size": GENERATED_RUNTIME_SIZE,
            "runtime_texture_scale": RUNTIME_SCALE,
            "registration_target": "registration-perfect layer alignment, not pixel-perfect brush tracing",
            "single_region_source_rule": "Each approved region painted_source is the single composition source for that region's layers.",
            "seam_rule": "Adjacent region sources must preserve shared road width, ground color, lighting direction, perspective, and edge continuation."
        },
        "art_pipeline_decision": {
            "previous_village_candidate_status": "layout_structure_draft_only",
            "do_not_split_previous_village_candidate": True,
            "next_village_step": "Generate a true storybook painted source only after this OutdoorWorld master blueprint is accepted."
        },
        "artifacts": {
            "layout_lock": "production/assets/outdoor_world_world2d/v001/01_world_layout/outdoor_world_layout_lock.json",
            "blueprint_svg": "production/assets/outdoor_world_world2d/v001/01_world_layout/outdoor_world_seamless_blueprint.svg",
            "blueprint_png": "production/assets/outdoor_world_world2d/v001/01_world_layout/outdoor_world_seamless_blueprint.png",
            "blueprint_md": "production/assets/outdoor_world_world2d/v001/01_world_layout/outdoor_world_seamless_blueprint.md",
            "source_strategy": "production/assets/outdoor_world_world2d/v001/02_source_strategy/source_generation_strategy.md",
            "chunk_contract": "production/assets/outdoor_world_world2d/v001/03_region_contracts/region_chunk_contract.json",
            "review_gate": "production/assets/outdoor_world_world2d/v001/04_review_and_qa/review_gate.md"
        },
        "validation": {
            "static_validator": "tools/validate_outdoor_world_seamless_art_master.py",
            "runtime_context_validator": "tools/validate_outdoor_world_assembly.py"
        }
    }
    write_json(WORKFLOW, payload)


def write_layout_lock() -> None:
    payload = {
        "layout_id": "outdoor_world_seamless_layout_lock_v001",
        "status": "master_blueprint_ready_for_visual_review",
        "active_runtime_scene": "res://game/scenes/world/OutdoorWorld.tscn",
        "source_runtime_file": "game/scenes/world/OutdoorWorld.gd",
        "world_bounds": world_bounds(),
        "runtime_scale_reference": RUNTIME_SCALE,
        "generated_region_source_canvas": GENERATED_SOURCE_CANVAS,
        "generated_region_runtime_size": GENERATED_RUNTIME_SIZE,
        "regions": REGIONS,
        "connections": CONNECTIONS,
        "global_art_rules": [
            "Produce a seamless world read first; do not approve isolated region art that breaks roads, ground color, lighting, or perspective at seams.",
            "Use the master blueprint as a spatial guide, not a pixel-perfect brush trace.",
            "Per-region layer PNGs must keep full region canvas and shared origin.",
            "Runtime layers derive from one accepted painted_source per region.",
            "Weather, season, and time-of-day overlays stay global Godot/system-level until base seam continuity is stable."
        ],
        "deferred_until_master_review": [
            "Village final painted_source generation",
            "Village layer export",
            "Runtime art replacement",
            "High-volume region batch generation"
        ]
    }
    write_json(LAYOUT_LOCK, payload)


def svg_polyline(points: list[list[int]], color: str, width: int, dash: str = "") -> str:
    coords = " ".join(f"{x},{y}" for x, y in points)
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"{dash_attr}/>'


def write_svg() -> None:
    bounds = world_bounds()
    margin = 120
    view_x = bounds["min_x"] - margin
    view_y = bounds["min_y"] - margin
    view_w = bounds["width"] + margin * 2
    view_h = bounds["height"] + margin * 2
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="2200" height="1300" viewBox="{view_x} {view_y} {view_w} {view_h}">',
        "  <title>OutdoorWorld seamless art master blueprint v001</title>",
        f'  <rect x="{view_x}" y="{view_y}" width="{view_w}" height="{view_h}" fill="#d9e2c2"/>',
        f'  <rect x="{bounds["min_x"]}" y="{bounds["min_y"]}" width="{bounds["width"]}" height="{bounds["height"]}" fill="#a8bb7c" fill-opacity="0.28" stroke="#50613d" stroke-width="4"/>',
        '  <g id="connections">',
    ]
    for connection in CONNECTIONS:
        lines.append("    " + svg_polyline(connection["points"], "#9a7a46", 32))
        lines.append("    " + svg_polyline(connection["points"], "#d0b66f", 18))
    lines.append("  </g>")
    lines.append('  <g id="regions">')
    fill_by_priority = {"P0": "#d8bb75", "P1": "#b7c985", "P2": "#9fc3a0", "P3": "#9eb4c3"}
    for region in REGIONS:
        x, y, w, h = region["bounds"]
        fill = fill_by_priority.get(region["priority"], "#b8c6a0")
        stroke = "#694d30" if region["priority"] == "P0" else "#41513b"
        lines.append(f'    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" fill-opacity="0.55" stroke="{stroke}" stroke-width="5"/>')
        lines.append(f'    <text x="{x + 12}" y="{y + 32}" font-family="Arial" font-size="30" fill="#26331f">{escape(region["display_name"])}</text>')
        lines.append(f'    <text x="{x + 12}" y="{y + 62}" font-family="Arial" font-size="18" fill="#41513b">{escape(region["source_status"])}</text>')
    lines.append("  </g>")
    lines.append('  <g id="anchors">')
    for region in REGIONS:
        cx, cy = region_center(region["region_id"])
        lines.append(f'    <circle cx="{cx}" cy="{cy}" r="8" fill="#273b45"/>')
    lines.append("  </g>")
    lines.append(f'  <text x="{view_x + 24}" y="{view_y + 52}" font-family="Arial" font-size="30" fill="#26331f">OutdoorWorld seamless art master - structure guide, not final art</text>')
    lines.append(f'  <text x="{view_x + 24}" y="{view_y + 88}" font-family="Arial" font-size="22" fill="#26331f">Final region sources must preserve shared roads, color, lighting, perspective, and full-canvas layer alignment.</text>')
    lines.append("</svg>")
    BLUEPRINT_SVG.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_png() -> None:
    bounds = world_bounds()
    view_x = bounds["min_x"] - 120
    view_y = bounds["min_y"] - 120
    offset_x = 100
    offset_y = 90
    scale = 1.0

    def tx(point: list[int]) -> tuple[int, int]:
        return (
            int(round((point[0] - view_x) * scale + offset_x)),
            int(round((point[1] - view_y) * scale + offset_y)),
        )

    image = Image.new("RGB", (2200, 1300), (217, 226, 194))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    title_font = ImageFont.load_default()

    world_start = tx([bounds["min_x"], bounds["min_y"]])
    world_end = tx([bounds["max_x"], bounds["max_y"]])
    draw.rectangle([world_start, world_end], fill=(174, 191, 130), outline=(80, 97, 61), width=4)

    for connection in CONNECTIONS:
        points = [tx(point) for point in connection["points"]]
        draw.line(points, fill=(154, 122, 70), width=32, joint="curve")
        draw.line(points, fill=(208, 182, 111), width=18, joint="curve")

    fill_by_priority = {
        "P0": (216, 187, 117),
        "P1": (183, 201, 133),
        "P2": (159, 195, 160),
        "P3": (158, 180, 195),
    }
    for region in REGIONS:
        x, y, w, h = region["bounds"]
        start = tx([x, y])
        end = tx([x + w, y + h])
        fill = fill_by_priority.get(region["priority"], (184, 198, 160))
        outline = (105, 77, 48) if region["priority"] == "P0" else (65, 81, 59)
        draw.rounded_rectangle([start, end], radius=8, fill=fill, outline=outline, width=5)
        draw.text((start[0] + 12, start[1] + 12), region["display_name"], fill=(38, 51, 31), font=font)
        draw.text((start[0] + 12, start[1] + 34), region["source_status"], fill=(65, 81, 59), font=font)
        cx, cy = tx(region_center(region["region_id"]))
        draw.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=(39, 59, 69))

    draw.text((80, 40), "OutdoorWorld seamless art master - structure guide, not final art", fill=(38, 51, 31), font=title_font)
    draw.text((80, 64), "Review route continuity before final per-region painted_source generation.", fill=(38, 51, 31), font=font)
    image.save(BLUEPRINT_PNG)


def write_blueprint_md() -> None:
    region_rows = "\n".join(
        f"| `{region['region_id']}` | `{region['bounds']}` | {region['priority']} | {region['source_status']} |"
        for region in REGIONS
    )
    connection_rows = "\n".join(
        f"| `{connection['id']}` | `{connection['from']}` -> `{connection['to']}` | {connection['role']} |"
        for connection in CONNECTIONS
    )
    BLUEPRINT_MD.write_text(
        f"""# OutdoorWorld Seamless Art Master Blueprint

This is the global spatial contract for the current seamless 2D `OutdoorWorld`.
It is a structure guide, not final art and not runtime replacement.

## Runtime Coordinate Basis

- Active scene: `res://game/scenes/world/OutdoorWorld.tscn`
- Runtime source: `game/scenes/world/OutdoorWorld.gd`
- Generated region runtime size: `{GENERATED_RUNTIME_SIZE[0]}x{GENERATED_RUNTIME_SIZE[1]}`
- Generated region source canvas reference: `{GENERATED_SOURCE_CANVAS[0]}x{GENERATED_SOURCE_CANVAS[1]}`
- Runtime texture scale: `{RUNTIME_SCALE}`
- World bounds: `{world_bounds()}`

## Region Layout

| Region | Runtime bounds | Priority | Source status |
| --- | --- | --- | --- |
{region_rows}

## Seam Connections

| Connection | Regions | Role |
| --- | --- | --- |
{connection_rows}

## Art Direction Rules

- Treat the world as one continuous countryside map before approving any single region.
- Match ground hue, road width, road material, lighting direction, and perspective at every seam.
- Region chunks may be produced one at a time, but their edges must respect this master blueprint.
- Use blueprint geometry as layout guidance, not pixel-perfect brush tracing.
- Do not split layers from the current Village structure draft.
""",
        encoding="utf-8",
    )


def write_source_strategy() -> None:
    SOURCE_STRATEGY.write_text(
        """# Source Generation Strategy

## Corrected Pipeline

The current project uses one seamless 2D `OutdoorWorld`, so art production must start from a world-level master blueprint.

1. Review this master blueprint for world continuity.
2. Produce one true storybook `painted_source` per approved region chunk.
3. Keep each region source on its full source canvas.
4. Split runtime layers only from that accepted source.
5. Validate layer registration and Godot screenshots before runtime replacement.

## Village Correction

The existing Village generated image is a structure/layout draft. It proves plaza placement, road continuity, and gameplay anchor readability. It is not final `village_painted_source` and must not be split into runtime layers.

The next Village image request should use this master blueprint plus the Village layout lock as references, and should ask for a real warm low-saturation storybook scene without labels, engineering rectangles, or diagrammatic road rendering.

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


def write_chunk_contract() -> None:
    payload = {
        "contract_id": "outdoor_world_region_chunk_contract_v001",
        "status": "seamless_mvp_layer_scope_locked",
        "active_runtime_scene": "res://game/scenes/world/OutdoorWorld.tscn",
        "per_region_source_rule": {
            "source_canvas": GENERATED_SOURCE_CANVAS,
            "runtime_size_reference": GENERATED_RUNTIME_SIZE,
            "runtime_texture_scale": RUNTIME_SCALE,
            "opaque_source_required": True,
            "single_painted_source_per_region": True,
            "layers_derive_from_source": True,
            "transparent_layers_full_canvas": True,
            "no_cropped_layers": True
        },
        "mvp_layers": [
            {"id": "base_ground", "alpha": "opaque", "z_index": -30},
            {"id": "terrain_details", "alpha": "transparent_full_canvas", "z_index": -25},
            {"id": "behind_player_structures", "alpha": "transparent_full_canvas", "z_index": -10},
            {"id": "ysort_props_structures", "alpha": "transparent_full_canvas", "z_index": 8},
            {"id": "foreground_occlusion", "alpha": "transparent_full_canvas", "z_index": 40}
        ],
        "deferred_layers": [
            "shadow_overlay",
            "light_weather_overlay_spring",
            "light_weather_overlay_summer",
            "light_weather_overlay_autumn",
            "light_weather_overlay_winter"
        ],
        "seam_acceptance": [
            "Roads continue across connected regions without width jumps.",
            "Ground color and texture density do not visibly reset at region boundaries.",
            "Foreground occlusion does not hide seam travel prompts or NPC standing pockets.",
            "No layer is independently recomposed from a new prompt."
        ]
    }
    write_json(CHUNK_CONTRACT, payload)


def write_review_gate() -> None:
    REVIEW_GATE.write_text(
        """# OutdoorWorld Seamless Art Review Gate

This package does not approve launch-quality art and does not replace runtime art.

## Before Region Source Generation

- Human review confirms world-level region placement and route continuity.
- Village current structure draft is treated only as a layout reference.
- Region source requests include this master blueprint plus local layout locks.

## Before Layer Export

- One true opaque `painted_source` exists for the region.
- The source reads as final storybook scene art, not a structure diagram.
- Layer export uses only that source composition.

## Before Runtime Replacement

- Full-canvas layers validate.
- Godot screenshot review confirms seams, prompts, NPC standing pockets, and player occlusion.
- `launch_quality_approved` remains false until explicit human visual approval.
""",
        encoding="utf-8",
    )


def write_readme() -> None:
    README.write_text(
        """# OutdoorWorld World2D v001

This package is the seamless 2D art master for the current `OutdoorWorld`.

It exists because outdoor gameplay now runs inside one continuous scene. Region art can still be produced in small chunks, but every chunk must obey this world-level layout, seam, color, perspective, and layer-registration contract.

This package is not runtime replacement and not launch-quality approval.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    write_workflow()
    write_layout_lock()
    write_svg()
    write_png()
    write_blueprint_md()
    write_source_strategy()
    write_chunk_contract()
    write_review_gate()
    write_readme()
    print(f"OK: wrote {PACKAGE_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
