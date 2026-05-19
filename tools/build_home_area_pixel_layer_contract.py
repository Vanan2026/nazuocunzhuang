from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "production/assets/regions/home_area_formal/v001"
SOURCE = PKG / "source/region_home_area_formal_full_source_v001.png"
CONTRACT = PKG / "home_area_formal_v001_pixel_layer_contract.json"
REPORT = ROOT / ".codex/reports/home_area_formal_v001_pixel_layer_contract.md"
OVERLAY = PKG / "review/home_area_formal_v001_pixel_layer_contract_overlay.png"
CANVAS = {"width": 6144, "height": 4096}


def rect(x: int, y: int, width: int, height: int) -> dict[str, int]:
    return {"x": x, "y": y, "width": width, "height": height}


def point(x: int, y: int) -> dict[str, int]:
    return {"x": x, "y": y}


def layer(scene_node: str, role: str, z: int, layer_asset_id: str, rule: str) -> dict[str, Any]:
    return {"scene_node": scene_node, "role": role, "z_index": z, "layer_asset_id": layer_asset_id, "rule": rule}


def blocker(scene_node: str, x: int, y: int, width: int, height: int, rule: str) -> dict[str, Any]:
    return {"scene_node": scene_node, "rect_px": rect(x, y, width, height), "rule": rule}


def interaction(scene_node: str, x: int, y: int, width: int, height: int, sx: int, sy: int, hint: str, rule: str) -> dict[str, Any]:
    return {"scene_node": scene_node, "hotspot_rect_px": rect(x, y, width, height), "stand_point_px": point(sx, sy), "hint": hint, "rule": rule}


OBJECTS: list[dict[str, Any]] = [
    {
        "object_id": "house_body",
        "display_name": "house wall and base",
        "source_rect_px": rect(1810, 900, 2330, 1030),
        "render_layers": [layer("HouseBodyArtV007", "ysort_visual", 40, "house_body", "wall/body renders in YSort so actors remain readable in front")],
        "blockers": [blocker("HouseBlocker", 2025, 1425, 2020, 190, "block only physical wall/base; do not cover grass, step, veranda approach, or front path")],
        "interactions": [],
        "qa_points": [point(3160, 1830), point(3160, 1940), point(2860, 1835)],
        "logic_notes": ["The house is not one gameplay rectangle; body, roof, veranda, door, and steps are separate contracts."]
    },
    {
        "object_id": "house_roof",
        "display_name": "roof visual occluder",
        "source_rect_px": rect(1680, 235, 2760, 960),
        "render_layers": [layer("HouseRoofOccluderArtV007", "foreground_occluder", 180, "house_roof_occluder", "roof is visual occlusion only; no interaction and no walking blocker")],
        "blockers": [],
        "interactions": [],
        "qa_points": [point(3160, 1180), point(3160, 1530)],
        "logic_notes": ["Roof can hide upper body only when actor is visually behind it; it must not block the front steps."]
    },
    {
        "object_id": "veranda_floor",
        "display_name": "veranda floor",
        "source_rect_px": rect(1890, 1350, 2080, 410),
        "render_layers": [layer("VerandaFloorArtV007", "detail", 60, "veranda_floor", "floor is a walkable detail layer below actors")],
        "blockers": [],
        "interactions": [],
        "qa_points": [point(3160, 1760), point(2650, 1740), point(3650, 1740)],
        "logic_notes": ["Veranda/floor pixels are visual guidance, not collision."]
    },
    {
        "object_id": "front_steps",
        "display_name": "front steps and stone approach",
        "source_rect_px": rect(2670, 1690, 910, 420),
        "render_layers": [layer("GroundYardArtV007", "ground", 30, "ground_yard", "steps remain part of source underpaint until a dedicated step layer is split")],
        "blockers": [],
        "interactions": [],
        "qa_points": [point(3160, 1835), point(3160, 1995), point(3430, 1950)],
        "logic_notes": ["These pixels must stay walkable; blockers come from objects, not from the step texture."]
    },
    {
        "object_id": "house_door",
        "display_name": "house door interaction",
        "source_rect_px": rect(2935, 1090, 460, 760),
        "render_layers": [layer("HouseBodyArtV007", "ysort_visual", 40, "house_body", "door is painted into house body but has independent interaction logic")],
        "blockers": [],
        "interactions": [interaction("HouseDoorEntrance", 3070, 1765, 180, 130, 3160, 1895, "按 E 查看屋檐", "door hotspot sits below body blocker so the front approach remains reachable")],
        "qa_points": [point(3160, 1830), point(3160, 1900)],
        "logic_notes": ["Door interaction is object-specific; it must not be inferred from house distance alone."]
    },
    {
        "object_id": "left_shade_tree",
        "display_name": "left shade tree",
        "source_rect_px": rect(0, 0, 2360, 1920),
        "render_layers": [
            layer("TreeLeftTrunkArtV007", "ysort_visual", 55, "tree_left_trunk", "trunk/root pixels participate in YSort"),
            layer("TreeLeftCanopyOccluderArtV007", "foreground_occluder", 190, "tree_left_canopy_occluder", "canopy is visual occlusion only")
        ],
        "blockers": [
            blocker("BigShadeRootBlocker", 625, 1774, 190, 82, "root base blocks walking"),
            blocker("TreeBlocker", 674, 1497, 92, 76, "trunk core blocks walking")
        ],
        "interactions": [],
        "qa_points": [point(980, 1880), point(1220, 2020), point(720, 1855)],
        "logic_notes": ["Canopy overlap is not a blocker; only root/trunk rectangles block movement."]
    },
    {
        "object_id": "right_persimmon_tree",
        "display_name": "right persimmon tree",
        "source_rect_px": rect(3710, 0, 2240, 2220),
        "render_layers": [
            layer("TreeRightTrunkArtV007", "ysort_visual", 55, "tree_right_trunk", "trunk/root pixels participate in YSort"),
            layer("TreeRightCanopyOccluderArtV007", "foreground_occluder", 188, "tree_right_canopy_occluder", "canopy is visual occlusion only")
        ],
        "blockers": [
            blocker("PersimmonRootBlocker", 4372, 2142, 176, 76, "root base blocks walking"),
            blocker("TreeBlocker", 4414, 1862, 92, 76, "trunk core blocks walking")
        ],
        "interactions": [],
        "qa_points": [point(4460, 2220), point(4580, 2340), point(4300, 2300)],
        "logic_notes": ["Right tree is two visual layers plus two physical blockers; no generic tree interaction in this pass."]
    },
    {
        "object_id": "mailbox",
        "display_name": "mailbox",
        "source_rect_px": rect(1760, 1180, 560, 660),
        "render_layers": [layer("MailboxArt", "ysort_visual", 60, "prop_mailbox", "mailbox is independent prop art, not part of bushes or house")],
        "blockers": [blocker("Mailbox/PropBlocker", 1944, 1714, 72, 52, "only post/base blocks walking")],
        "interactions": [interaction("MailboxInteract", 1890, 1755, 180, 130, 1980, 1868, "按 E 查看信箱", "front hotspot is separate from prop blocker and nearby bush pixels")],
        "qa_points": [point(1980, 1760), point(1980, 1820), point(1980, 1868)],
        "logic_notes": ["Nearby plant occlusion can overlap legs but must not become the interaction target."]
    },
    {
        "object_id": "well",
        "display_name": "old well",
        "source_rect_px": rect(4190, 2030, 780, 850),
        "render_layers": [layer("WellArt", "ysort_visual", 62, "prop_well", "well prop is independent from path and surrounding flower pots")],
        "blockers": [blocker("Well/PropBlocker", 4430, 2735, 300, 170, "stone base blocks walking; roof art does not add collision")],
        "interactions": [interaction("WellInteract", 4490, 2875, 180, 130, 4580, 2980, "按 E 查看水井", "south/front hotspot must be reachable from path")],
        "qa_points": [point(4580, 2840), point(4580, 2940), point(4580, 2980)],
        "logic_notes": ["Well roof is drawn above the base but gameplay collision is base-only."]
    },
    {
        "object_id": "bench_left_fence",
        "display_name": "left fence bench",
        "source_rect_px": rect(520, 1340, 850, 760),
        "render_layers": [layer("BenchArt", "ysort_visual", 61, "prop_bench", "bench is independent from fence, tree, and ground")],
        "blockers": [blocker("Bench/PropBlocker", 560, 1960, 760, 120, "seat/base blocks movement while front standing point remains available")],
        "interactions": [interaction("BenchRestInteract", 850, 2035, 180, 130, 940, 2148, "按 E 坐下休息", "rest hotspot is in front of bench, not inside fence")],
        "qa_points": [point(940, 2020), point(940, 2100), point(940, 2148)],
        "logic_notes": ["Rest anchor is gameplay state, separate from visual prop origin."]
    },
    {
        "object_id": "road_sign",
        "display_name": "road sign",
        "source_rect_px": rect(4850, 2860, 520, 520),
        "render_layers": [layer("RoadSignArt", "ysort_visual", 58, "prop_road_sign", "road sign is separate from back-farm path and foreground grass")],
        "blockers": [blocker("RoadSign/PropBlocker", 5049, 3232, 72, 52, "post/base blocks movement only")],
        "interactions": [interaction("RoadSignInteract", 4995, 3275, 180, 130, 5085, 3396, "按 E 查看路牌", "front hotspot follows the sign after source correction")],
        "qa_points": [point(5085, 3270), point(5085, 3340), point(5085, 3396)],
        "logic_notes": ["The sign direction is art; navigation target stays on the explicit exit nodes."]
    },
    {
        "object_id": "left_fence",
        "display_name": "left fence",
        "source_rect_px": rect(0, 1500, 1180, 1200),
        "render_layers": [layer("FenceLeftGuide", "ysort_visual", 58, "hidden_blockout_guide", "visual is currently in source/ground; guide stays hidden")],
        "blockers": [blocker("FenceLeftBlocker", 640, 1956, 520, 46, "fence rail blocks crossing but does not handle bench interaction")],
        "interactions": [],
        "qa_points": [point(900, 1980), point(620, 2120)],
        "logic_notes": ["Fence is a barrier only; it must not be merged with bench or tree blockers."]
    },
    {
        "object_id": "right_fence",
        "display_name": "right fence",
        "source_rect_px": rect(4890, 740, 1250, 2100),
        "render_layers": [layer("FenceRightGuide", "ysort_visual", 58, "hidden_blockout_guide", "visual is currently in source/ground; guide stays hidden")],
        "blockers": [blocker("FenceRightBlocker", 4930, 2111, 560, 46, "right fence rail blocks crossing near tree/path edge")],
        "interactions": [],
        "qa_points": [point(5200, 2160), point(5400, 2300)],
        "logic_notes": ["Fence blocker is directional boundary, not path navigation."]
    },
    {
        "object_id": "back_farm_rail",
        "display_name": "back farm rail",
        "source_rect_px": rect(3880, 2740, 700, 380),
        "render_layers": [layer("BackFarmRailGuide", "ysort_visual", 59, "hidden_blockout_guide", "visual is currently in source/ground; guide stays hidden")],
        "blockers": [blocker("BackFarmRailBlocker", 4046, 2916, 430, 42, "rail blocks the edge while the exit hotspot remains reachable")],
        "interactions": [],
        "qa_points": [point(4200, 3020), point(4300, 3140)],
        "logic_notes": ["Back-farm rail is not the exit; exit is its own Area2D below/right of the rail."]
    },
    {
        "object_id": "local_foreground_plants",
        "display_name": "local foreground plant cutouts",
        "source_rect_px": rect(180, 1300, 5820, 2760),
        "render_layers": [
            layer("HouseFrontBushOccluder", "foreground_occluder", 204, "fg_house_front_bush", "small local cutout only"),
            layer("MailboxGrassOccluder", "foreground_occluder", 205, "fg_mailbox_grass", "small local cutout only"),
            layer("BenchFlowerOccluder", "foreground_occluder", 206, "fg_bench_flowers", "small local cutout only"),
            layer("SouthEdgeFlowerOccluder", "foreground_occluder", 207, "fg_south_edge_flowers", "small local cutout only")
        ],
        "blockers": [],
        "interactions": [],
        "qa_points": [point(2280, 1970), point(1980, 1868), point(940, 2148), point(4880, 3600)],
        "logic_notes": ["Broad foreground_grass remains disabled; local cutouts can only provide visual leg occlusion."]
    },
    {
        "object_id": "back_farm_exit",
        "display_name": "back farm exit",
        "source_rect_px": rect(3980, 3060, 520, 520),
        "render_layers": [layer("BackFarmPathArtV007", "ground", 41, "path_back_farm", "path art suggests exit direction but does not own navigation")],
        "blockers": [],
        "interactions": [interaction("BackyardFarmEntrance", 4110, 3305, 180, 130, 4200, 3435, "按 E 前往后院菜地", "exit uses explicit target region/spawn contract")],
        "qa_points": [point(4200, 3370), point(4200, 3435)],
        "logic_notes": ["Navigation is explicit data; do not infer region transition from path pixels."]
    },
    {
        "object_id": "player_yard_exit",
        "display_name": "player yard exit",
        "source_rect_px": rect(4150, 3120, 420, 420),
        "render_layers": [layer("BackFarmPathArtV007", "ground", 41, "path_back_farm", "shares path art but has separate scene-switch logic")],
        "blockers": [],
        "interactions": [interaction("PlayerYardEntrance", 4210, 3175, 180, 130, 4300, 3305, "按 E 前往后屋", "scene-switch hotspot remains separate from BackFarm region exit")],
        "qa_points": [point(4300, 3240), point(4300, 3305)],
        "logic_notes": ["Two exits can overlap visually with the same path, but interaction targets must stay distinct."]
    },
]


def build_contract() -> dict[str, Any]:
    return {
        "region_id": "Region_HomeArea",
        "package_id": "home_area_formal_v001",
        "source_asset": "source/region_home_area_formal_full_source_v001.png",
        "canvas_px": CANVAS,
        "coordinate_space": "source_pixels_equal_region_local_pixels",
        "world_offset_px": {"x": 4000, "y": 6000},
        "approval_boundary": "design_contract_not_launch_approval",
        "design_rules": [
            "Do not combine visually distinct objects into one gameplay contract.",
            "Ground/detail pixels can guide movement but cannot create blockers by themselves.",
            "YSort visuals, foreground occluders, blockers, and interaction hotspots are separate data even when derived from the same source object.",
            "All source-pixel rectangles use Region_HomeArea local coordinates; world coordinates add world_offset_px.",
            "Broad foreground plates stay disabled; only local cutouts can occlude the player.",
        ],
        "objects": OBJECTS,
    }


def draw_overlay(contract: dict[str, Any]) -> None:
    source = Image.open(SOURCE).convert("RGBA")
    review = source.resize((1536, 1024), Image.Resampling.LANCZOS)
    overlay = Image.new("RGBA", review.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    scale = 0.25
    colors = {
        "house": (255, 190, 70, 180),
        "tree": (70, 200, 90, 170),
        "prop": (90, 170, 255, 180),
        "barrier": (255, 90, 90, 170),
        "exit": (200, 90, 255, 180),
        "foreground": (255, 255, 90, 150),
    }
    for obj in contract["objects"]:
        oid = obj["object_id"]
        group = "prop"
        if "house" in oid or oid in {"veranda_floor", "front_steps"}:
            group = "house"
        elif "tree" in oid:
            group = "tree"
        elif "fence" in oid or "rail" in oid:
            group = "barrier"
        elif "exit" in oid:
            group = "exit"
        elif "foreground" in oid:
            group = "foreground"
        c = colors[group]
        r = obj["source_rect_px"]
        box = [int(r["x"]*scale), int(r["y"]*scale), int((r["x"]+r["width"])*scale), int((r["y"]+r["height"])*scale)]
        draw.rectangle(box, outline=c, width=3)
        draw.text((box[0]+4, box[1]+4), oid, fill=c)
        for b in obj.get("blockers", []):
            br = b["rect_px"]
            bbox = [int(br["x"]*scale), int(br["y"]*scale), int((br["x"]+br["width"])*scale), int((br["y"]+br["height"])*scale)]
            draw.rectangle(bbox, outline=(255, 40, 40, 230), width=2)
        for it in obj.get("interactions", []):
            hr = it["hotspot_rect_px"]
            hbox = [int(hr["x"]*scale), int(hr["y"]*scale), int((hr["x"]+hr["width"])*scale), int((hr["y"]+hr["height"])*scale)]
            draw.rectangle(hbox, outline=(60, 210, 255, 230), width=2)
            sp = it["stand_point_px"]
            sx, sy = int(sp["x"]*scale), int(sp["y"]*scale)
            draw.ellipse((sx-4, sy-4, sx+4, sy+4), fill=(60, 210, 255, 230))
    composed = Image.alpha_composite(review, overlay)
    OVERLAY.parent.mkdir(parents=True, exist_ok=True)
    composed.convert("RGB").save(OVERLAY)


def write_report(contract: dict[str, Any]) -> None:
    lines = [
        "# HomeArea formal/v001 Pixel Layer And Interaction Contract",
        "",
        "Coordinate space: 6144x4096 source pixels, equal to Region_HomeArea local pixels. World coordinates add `(4000, 6000)`.",
        "",
        "This is a design and verification contract, not launch-quality approval.",
        "",
        "| Object | Source Rect | Render Layers | Blockers | Interactions | QA Points |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for obj in contract["objects"]:
        r = obj["source_rect_px"]
        source_rect = f"{r['x']},{r['y']} {r['width']}x{r['height']}"
        layers = "<br>".join(f"{l['scene_node']} ({l['role']} z{l['z_index']})" for l in obj["render_layers"])
        blockers = "<br>".join(f"{b['scene_node']} {b['rect_px']['x']},{b['rect_px']['y']} {b['rect_px']['width']}x{b['rect_px']['height']}" for b in obj["blockers"]) or "none"
        interactions = "<br>".join(f"{i['scene_node']} hot={i['hotspot_rect_px']['x']},{i['hotspot_rect_px']['y']} {i['hotspot_rect_px']['width']}x{i['hotspot_rect_px']['height']} stand={i['stand_point_px']['x']},{i['stand_point_px']['y']}" for i in obj["interactions"]) or "none"
        qa = "<br>".join(f"{p['x']},{p['y']}" for p in obj["qa_points"])
        lines.append(f"| {obj['object_id']} | {source_rect} | {layers} | {blockers} | {interactions} | {qa} |")
    lines.extend([
        "",
        "## Implementation Notes",
        "",
        "- Red rectangles in the overlay are blockers; cyan rectangles/dots are interaction hotspots and stand points.",
        "- Object source rectangles are deliberately broader than exact masks where the art object includes leaves, shadows, or approach pixels; blocker/hotspot rectangles are the gameplay truth.",
        "- The contract intentionally keeps `front_steps`, `house_door`, and `back_farm_exit` separate from their surrounding art layers because they have different gameplay meaning.",
    ])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"missing source: {SOURCE}")
    contract = build_contract()
    CONTRACT.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    draw_overlay(contract)
    write_report(contract)
    print(f"OK: wrote {CONTRACT.relative_to(ROOT).as_posix()}")
    print(f"OK: wrote {REPORT.relative_to(ROOT).as_posix()}")
    print(f"OK: wrote {OVERLAY.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()