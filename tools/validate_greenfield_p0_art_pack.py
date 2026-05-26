from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "production" / "assets" / "base_asset_pack" / "v001"
RUNTIME = ROOT / "assets" / "art" / "greenfield_p0"
MANIFEST = PACKAGE / "workflow_manifest.json"

SEASONS = ["spring", "summer", "autumn", "winter"]
DIRECTIONS = ["down", "down_right", "right", "up_right", "up", "up_left", "left", "down_left"]
PROTAGONIST_ACTIONS = ["idle", "walk", "interact", "water", "pickup"]
NPC_IDS = ["aoi", "gen", "mika", "hana"]
PORTRAITS = ["neutral", "happy", "thinking"]
REGIONS = ["home_area", "village", "back_farm", "forest_edge", "orchard", "pond", "mountain_path", "mountain_hut", "mountain", "cliff_view"]
REGION_LAYERS = ["base_ground", "terrain_details", "behind_player_structures", "ysort_props_structures", "foreground_occlusion", "shadow_overlay"]
UI_SCREEN_IDS = ["hud", "inventory", "journal_map", "dialogue_gift", "pause_settings"]
REQUIRED_CONTACT_SHEETS = {
    "region_painted_sources",
    "season_tiles",
    "props",
    "item_icons",
    "crop_stages",
    "player_motion",
    "npc_motion",
    "npc_portraits",
    "ui_pieces",
    "ui_screens",
    "region_runtime_composites",
}
EXPECTED_ROAD_SIGNATURES = {
    "home_area": "home_public_lane_private_yard_spurs",
    "village": "village_plaza_lane_doorstep_spurs",
    "back_farm": "farm_service_lane_fields_shed_gate",
    "forest_edge": "forest_broken_moss_trail_west_north",
    "orchard": "orchard_diagonal_service_rows",
    "pond": "pond_crescent_bank_path",
    "mountain_path": "mountain_switchback_southwest_northeast",
    "mountain_hut": "hut_curved_arrival_west_south",
    "mountain": "mountain_uneven_trail_stream_crossing",
    "cliff_view": "cliff_contour_ledge_path",
}
REQUIRED_OBJECT_ZONE_IDS = {
    "home_area": {"house", "mailbox", "well", "bench"},
    "village": {"house_a", "house_b", "shrine", "bench"},
    "back_farm": {"shed", "field_block_west", "field_block_east"},
}
REQUIRED_ROAD_ROLES = {
    "home_area": {"public_lane", "home_access", "utility_footpath", "rest_access"},
    "village": {"village_through_lane", "plaza_edge", "doorstep", "landmark_access"},
    "back_farm": {"farm_access_lane", "farm_service_lane", "field_service_path"},
}
EXPECTED_WORLD_GRID = {
    "mountain_path": [1, 0],
    "mountain": [2, 0],
    "cliff_view": [3, 0],
    "forest_edge": [0, 1],
    "village": [1, 1],
    "mountain_hut": [2, 1],
    "orchard": [0, 2],
    "home_area": [1, 2],
    "pond": [2, 2],
    "back_farm": [1, 3],
}
EXPECTED_WORLD_ADJACENCIES = {
    ("village", "north", "mountain_path", "south"),
    ("mountain_path", "east", "mountain", "west"),
    ("mountain", "east", "cliff_view", "west"),
    ("forest_edge", "east", "village", "west"),
    ("forest_edge", "south", "orchard", "north"),
    ("orchard", "east", "home_area", "west"),
    ("village", "south", "home_area", "north"),
    ("home_area", "south", "back_farm", "north"),
    ("home_area", "east", "pond", "west"),
    ("village", "east", "mountain_hut", "west"),
    ("mountain", "south", "mountain_hut", "north"),
    ("mountain_hut", "south", "pond", "north"),
}
OPPOSITE_EDGE = {"north": "south", "south": "north", "west": "east", "east": "west"}
BANNED_SOURCE_STRINGS = [
    "home_area_world2d/v001",
    "home_area_formal",
    "home_area_launch",
    "home_area_art/v",
    "region_home_area.before_",
    "manual_foreground_slices",
    "foreground_full_canvas",
]


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def load_manifest() -> dict:
    require(MANIFEST.exists(), "missing workflow_manifest.json")
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def require_png(path: Path, min_size: tuple[int, int] = (1, 1), alpha_allowed: bool = True, opaque_required: bool = False) -> tuple[int, int]:
    require(path.exists(), f"missing PNG: {path}")
    with Image.open(path) as image:
        require(image.format == "PNG", f"not a PNG: {path}")
        require(image.width >= min_size[0] and image.height >= min_size[1], f"PNG too small: {path} {image.size}")
        if alpha_allowed:
            require(image.mode in {"RGBA", "LA", "P"}, f"PNG should preserve alpha-capable mode: {path} mode={image.mode}")
        if opaque_required and image.mode in {"RGBA", "LA"}:
            alpha = image.getchannel("A")
            min_alpha, max_alpha = alpha.getextrema()
            require(min_alpha == 255 and max_alpha == 255, f"PNG should be fully opaque: {path} alpha={min_alpha}-{max_alpha}")
        return image.size


def require_runtime(rel_path: str, min_size: tuple[int, int] = (1, 1)) -> None:
    require_png(PACKAGE / "02_runtime_exports" / rel_path, min_size=min_size)
    require_png(RUNTIME / rel_path, min_size=min_size)


def expand_rect(rect: list[int], amount: int) -> tuple[int, int, int, int]:
    return (rect[0] - amount, rect[1] - amount, rect[2] + amount, rect[3] + amount)


def point_in_rect(point: tuple[float, float], rect: tuple[int, int, int, int]) -> bool:
    return rect[0] <= point[0] <= rect[2] and rect[1] <= point[1] <= rect[3]


def orientation(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]) -> float:
    return (b[1] - a[1]) * (c[0] - b[0]) - (b[0] - a[0]) * (c[1] - b[1])


def segments_intersect(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float], d: tuple[float, float]) -> bool:
    def on_segment(p: tuple[float, float], q: tuple[float, float], r: tuple[float, float]) -> bool:
        return min(p[0], r[0]) <= q[0] <= max(p[0], r[0]) and min(p[1], r[1]) <= q[1] <= max(p[1], r[1])

    o1 = orientation(a, b, c)
    o2 = orientation(a, b, d)
    o3 = orientation(c, d, a)
    o4 = orientation(c, d, b)
    if (o1 > 0 > o2 or o1 < 0 < o2) and (o3 > 0 > o4 or o3 < 0 < o4):
        return True
    if o1 == 0 and on_segment(a, c, b):
        return True
    if o2 == 0 and on_segment(a, d, b):
        return True
    if o3 == 0 and on_segment(c, a, d):
        return True
    if o4 == 0 and on_segment(c, b, d):
        return True
    return False


def segment_intersects_rect(a: tuple[float, float], b: tuple[float, float], rect: tuple[int, int, int, int]) -> bool:
    if point_in_rect(a, rect) or point_in_rect(b, rect):
        return True
    x1, y1, x2, y2 = rect
    edges = [
        ((x1, y1), (x2, y1)),
        ((x2, y1), (x2, y2)),
        ((x2, y2), (x1, y2)),
        ((x1, y2), (x1, y1)),
    ]
    return any(segments_intersect(a, b, edge[0], edge[1]) for edge in edges)


def validate_functional_layout(region_id: str, layout_profile: dict) -> None:
    zones = layout_profile.get("object_zones", [])
    zone_ids = {zone.get("id") for zone in zones}
    required = REQUIRED_OBJECT_ZONE_IDS.get(region_id, set())
    require(required.issubset(zone_ids), f"{region_id} missing object zones: {required - zone_ids}")
    road_roles = {road.get("role") for road in layout_profile.get("road_paths", [])}
    required_roles = REQUIRED_ROAD_ROLES.get(region_id, set())
    require(required_roles.issubset(road_roles), f"{region_id} missing road roles: {required_roles - road_roles}")
    for zone in zones:
        rect = zone.get("rect")
        require(isinstance(rect, list) and len(rect) == 4, f"{region_id}/{zone.get('id')} invalid object zone rect")
        require(rect[0] < rect[2] and rect[1] < rect[3], f"{region_id}/{zone.get('id')} inverted object zone rect")
        require(str(zone.get("relation", "")).strip() != "", f"{region_id}/{zone.get('id')} missing relation note")
    for road in layout_profile.get("road_paths", []):
        points = [tuple(point) for point in road.get("pixel_points", [])]
        require(len(points) >= 2, f"{region_id}/{road.get('id')} missing pixel road points")
        half_width = max(10, int(road.get("width_px", 20)) // 2)
        for start, end in zip(points, points[1:]):
            for zone in zones:
                inflated = expand_rect(zone["rect"], half_width + 6)
                require(
                    not segment_intersects_rect(start, end, inflated),
                    f"{region_id}/{road.get('id')} intersects object zone {zone.get('id')}",
                )


def validate_world_layout(manifest: dict) -> None:
    world_layout = manifest.get("world_layout", {})
    require(world_layout.get("status") == "review_candidate", "world layout status must be review_candidate")
    require_png(ROOT / world_layout.get("preview", ""), min_size=(1000, 700), alpha_allowed=True, opaque_required=True)
    tiles = world_layout.get("tiles", [])
    require(len(tiles) == len(REGIONS), "world layout must include all P0 regions")
    tile_by_region = {tile.get("region_id"): tile for tile in tiles}
    require(set(tile_by_region) == set(REGIONS), "world layout region set mismatch")
    grids = [tuple(tile.get("grid", [])) for tile in tiles]
    require(len(set(grids)) == len(grids), "world layout grid positions must be unique")
    for region_id, expected_grid in EXPECTED_WORLD_GRID.items():
        require(tile_by_region[region_id].get("grid") == expected_grid, f"{region_id} world grid mismatch")
        require(str(tile_by_region[region_id].get("world_role", "")).strip() != "", f"{region_id} missing world_role")

    adjacencies = world_layout.get("adjacencies", [])
    adjacency_keys = {(item.get("from"), item.get("from_edge"), item.get("to"), item.get("to_edge")) for item in adjacencies}
    require(adjacency_keys == EXPECTED_WORLD_ADJACENCIES, "world adjacency graph mismatch")
    for item in adjacencies:
        from_grid = tile_by_region[item["from"]]["grid"]
        to_grid = tile_by_region[item["to"]]["grid"]
        dx = to_grid[0] - from_grid[0]
        dy = to_grid[1] - from_grid[1]
        expected_direction = {
            (0, -1): "north",
            (0, 1): "south",
            (-1, 0): "west",
            (1, 0): "east",
        }.get((dx, dy))
        require(expected_direction == item["from_edge"], f"{item['id']} grid direction does not match from_edge")
        require(OPPOSITE_EDGE[item["from_edge"]] == item["to_edge"], f"{item['id']} has non-opposite edges")
        require(str(item.get("route_role", "")).strip() != "", f"{item['id']} missing route_role")
        require(item.get("traversal") in {"walk", "walk_cart"}, f"{item['id']} invalid traversal")

    sockets = world_layout.get("sockets", [])
    require(len(sockets) == len(adjacencies) * 2, "world layout must expose two sockets per adjacency")
    socket_keys = {(socket.get("connection_id"), socket.get("region_id"), socket.get("edge")) for socket in sockets}
    for item in adjacencies:
        require((item["id"], item["from"], item["from_edge"]) in socket_keys, f"{item['id']} missing from socket")
        require((item["id"], item["to"], item["to_edge"]) in socket_keys, f"{item['id']} missing to socket")
    road_roles = set()
    for region in manifest["regions"]:
        for road in region["layout_profile"].get("road_paths", []):
            role = road.get("role")
            require(role != "path", f"{region['region_id']}/{road.get('id')} must not use default path role")
            road_roles.add(role)
    role_rules = manifest.get("road_role_rules", {})
    require(road_roles.issubset(set(role_rules)), f"missing road role rules: {road_roles - set(role_rules)}")


def validate_manifest_basics(manifest: dict) -> None:
    require(manifest.get("package_id") == "greenfield_p0_base_asset_pack_v001", "wrong package_id")
    require(manifest.get("status") == "usable", "package status must be usable")
    require(manifest.get("source_first") is True, "source_first must be true")
    require(manifest.get("runtime_replacement") is False, "runtime_replacement must remain false")
    require(manifest.get("launch_quality_approved") is False, "launch_quality_approved must remain false")
    require(manifest.get("human_visual_approval_required") is True, "human visual approval must remain required")
    completion = manifest.get("package_completion", {})
    require(completion.get("status") == "complete_review_candidate", "package completion status must be complete_review_candidate")
    require(completion.get("scope") == "greenfield_p0_art_asset_package", "package completion scope mismatch")
    require(completion.get("launch_quality_approved") is False, "package completion must not approve launch quality")
    require(completion.get("human_visual_approval_required") is True, "package completion must require human visual approval")
    require(manifest.get("seasons") == SEASONS, "season list mismatch")
    require(manifest.get("directions") == DIRECTIONS, "direction list mismatch")
    text = json.dumps(manifest, ensure_ascii=False)
    for banned in BANNED_SOURCE_STRINGS:
        require(banned not in text, f"manifest references banned old HomeArea source: {banned}")


def validate_style_and_ui(manifest: dict) -> None:
    require_png(PACKAGE / "01_mother_images" / "style" / "greenfield_p0_style_mother.png", min_size=(1000, 600), alpha_allowed=False)
    require_png(PACKAGE / "01_mother_images" / "ui" / "ui_layout_mother_board.png", min_size=(1000, 700), alpha_allowed=False)
    screens = {}
    for screen in manifest.get("ui_screens", []):
        screens[screen.get("id")] = screen
    require(set(screens) == set(UI_SCREEN_IDS), "UI screen mother set mismatch")
    for screen_id in UI_SCREEN_IDS:
        require_png(ROOT / screens[screen_id].get("production_path", ""), min_size=(1280, 720), alpha_allowed=False, opaque_required=True)
    for name, size in [
        ("panel_frame", (512, 320)),
        ("hud_panel", (512, 128)),
        ("dialogue_frame", (1024, 256)),
        ("button", (256, 96)),
        ("prompt_marker", (128, 128)),
        ("journal_tab", (256, 128)),
    ]:
        require_runtime(f"ui/ui_{name}_{size[0]}x{size[1]}.png", min_size=size)


def validate_tiles_and_crops() -> None:
    tile_types = ["grass_a", "grass_b", "dirt", "stone_path", "field_tilled_dry", "field_tilled_wet", "water_edge", "wood_floor", "shadow_soft"]
    for season in SEASONS:
        for tile_type in tile_types:
            require_runtime(f"tiles/{season}/tile_{tile_type}_{season}_64.png", min_size=(64, 64))

    crops_path = ROOT / "game" / "data" / "crops.json"
    crops = json.loads(crops_path.read_text(encoding="utf-8")) if crops_path.exists() else []
    for crop in crops:
        crop_id = str(crop.get("crop_id", crop.get("id", "")))
        require(crop_id != "", "crop missing id in data")
        for season in SEASONS:
            for stage in range(4):
                require_runtime(f"crops/{season}/crop_{crop_id}_stage_{stage:02d}_{season}_64.png", min_size=(64, 64))


def validate_characters() -> None:
    for action in PROTAGONIST_ACTIONS:
        for direction in DIRECTIONS:
            if action == "idle":
                require_runtime(f"characters/player/chr_player_base_idle_{direction}_128.png", min_size=(128, 128))
            else:
                require_runtime(f"characters/player/chr_player_base_{action}_{direction}_4x128.png", min_size=(512, 128))

    for npc in NPC_IDS:
        require_png(PACKAGE / "01_mother_images" / "characters" / f"npc_{npc}_8dir_motion_mother.png", min_size=(1024, 256), alpha_allowed=False)
        for direction in DIRECTIONS:
            require_runtime(f"characters/npc/npc_{npc}_idle_{direction}_128.png", min_size=(128, 128))
            require_runtime(f"characters/npc/npc_{npc}_walk_{direction}_4x128.png", min_size=(512, 128))
        for portrait in PORTRAITS:
            require_runtime(f"portraits/npc_{npc}_portrait_{portrait}_512.png", min_size=(512, 512))


def validate_items_props_fx() -> None:
    items_path = ROOT / "game" / "data" / "items.json"
    items = json.loads(items_path.read_text(encoding="utf-8")) if items_path.exists() else []
    for item in items:
        item_id = str(item.get("item_id", item.get("id", "")))
        require(item_id != "", "item missing id in data")
        require_runtime(f"items/{item_id}_64.png", min_size=(64, 64))

    require_png(PACKAGE / "01_mother_images" / "props" / "prop_mother_board.png", min_size=(1000, 700), alpha_allowed=False)
    for prop in ["house_player", "mailbox", "well", "bench", "road_sign", "fence", "tree", "rock", "storage_crate", "farm_shed", "dock", "shrine", "mountain_hut"]:
        require_runtime(f"props/prop_{prop}_256.png", min_size=(256, 256))
    for fx in ["rain_streaks", "snow_flakes", "leaf_drift", "sunbeam", "mist_patch"]:
        require_runtime(f"fx/fx_{fx}_256.png", min_size=(256, 256))


def validate_regions(manifest: dict) -> None:
    regions = manifest.get("regions", [])
    require(len(regions) == len(REGIONS), f"expected {len(REGIONS)} regions, got {len(regions)}")
    ids = {region.get("region_id") for region in regions}
    require(ids == set(REGIONS), f"region id set mismatch: {ids}")

    road_signatures = set()
    focal_buckets = set()
    centerline_focals = []
    for region_id in REGIONS:
        region_dir = PACKAGE / "01_mother_images" / "regions" / region_id
        require_png(region_dir / f"{region_id}_layout_mother.png", min_size=(1000, 800), alpha_allowed=False, opaque_required=True)
        require_png(region_dir / f"{region_id}_painted_source.png", min_size=(1000, 800), alpha_allowed=False, opaque_required=True)
        manifest_path = region_dir / f"{region_id}_manifest.json"
        require(manifest_path.exists(), f"missing region manifest: {region_id}")
        region_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        require(region_manifest.get("status") == "usable", f"{region_id} status must be usable")
        require(region_manifest.get("launch_quality_approved") is False, f"{region_id} launch approval must remain false")
        layout_profile = region_manifest.get("layout_profile", {})
        signature = layout_profile.get("road_signature")
        require(signature == EXPECTED_ROAD_SIGNATURES[region_id], f"{region_id} road signature mismatch: {signature}")
        road_signatures.add(signature)
        road_paths = layout_profile.get("road_paths", [])
        require(len(road_paths) >= 1, f"{region_id} missing road path records")
        path_shapes = {tuple(path.get("points", [])) for path in road_paths}
        require(len(path_shapes) == len(road_paths), f"{region_id} has duplicated road path shapes")
        focal = layout_profile.get("composition_focal_point")
        require(isinstance(focal, list) and len(focal) == 2, f"{region_id} missing composition focal point")
        fx, fy = float(focal[0]), float(focal[1])
        require(0.20 <= fx <= 0.80 and 0.20 <= fy <= 0.80, f"{region_id} focal point out of usable interior: {focal}")
        if abs(fx - 0.5) + abs(fy - 0.5) < 0.05:
            centerline_focals.append(region_id)
        focal_buckets.add((round(fx, 2), round(fy, 2)))
        connectors = layout_profile.get("seam_connectors", {})
        require(set(connectors.keys()) == {"north", "south", "east", "west"}, f"{region_id} seam connector set mismatch")
        width, height = region_manifest["canvas_size"]
        require(connectors["north"][1] <= int(height * 0.12), f"{region_id} north connector is not near north edge")
        require(connectors["south"][1] >= int(height * 0.88), f"{region_id} south connector is not near south edge")
        require(connectors["west"][0] <= int(width * 0.12), f"{region_id} west connector is not near west edge")
        require(connectors["east"][0] >= int(width * 0.88), f"{region_id} east connector is not near east edge")
        validate_functional_layout(region_id, layout_profile)
        for layer in REGION_LAYERS:
            require_runtime(f"regions/{region_id}/layers/{region_id}_{layer}.png", min_size=(1000, 800))
        for season in SEASONS:
            require_runtime(f"regions/{region_id}/layers/{region_id}_light_weather_overlay_{season}.png", min_size=(1000, 800))
        review_artifacts = region_manifest.get("review_artifacts", {})
        require_png(ROOT / review_artifacts.get("runtime_composite_preview", ""), min_size=(1000, 800), alpha_allowed=False, opaque_required=True)
        require_png(ROOT / review_artifacts.get("runtime_layer_contact_sheet", ""), min_size=(500, 400), alpha_allowed=False, opaque_required=True)
    require(len(road_signatures) == len(REGIONS), "region road signatures must be unique")
    require(len(focal_buckets) >= 8, f"region composition focal points are too repetitive: {sorted(focal_buckets)}")
    require(len(centerline_focals) <= 1, f"too many centered composition focal points: {centerline_focals}")


def validate_gallery_files() -> None:
    scene = ROOT / "scenes" / "dev" / "greenfield_p0_asset_gallery.tscn"
    require(scene.exists(), "missing Godot gallery scene")
    text = scene.read_text(encoding="utf-8")
    for banned in BANNED_SOURCE_STRINGS:
        require(banned not in text, f"gallery references banned old HomeArea source: {banned}")
    for section in ["CharacterSamples", "SeasonTileSamples", "UISamples", "PropSamples", "RegionSamples"]:
        require(section in text, f"gallery missing section: {section}")
    require_png(PACKAGE / "03_contact_sheets" / "greenfield_p0_region_painted_sources_contact_sheet.png", min_size=(600, 400), alpha_allowed=False, opaque_required=True)
    require_png(PACKAGE / "03_contact_sheets" / "greenfield_p0_season_tiles_contact_sheet.png", min_size=(400, 250), alpha_allowed=False, opaque_required=True)
    require_png(PACKAGE / "03_contact_sheets" / "greenfield_p0_props_contact_sheet.png", min_size=(400, 250), alpha_allowed=False, opaque_required=True)
    require_png(PACKAGE / "03_contact_sheets" / "greenfield_p0_world_layout_socket_preview.png", min_size=(1000, 700), alpha_allowed=False, opaque_required=True)


def validate_complete_delivery(manifest: dict) -> None:
    sheets = manifest.get("contact_sheets", {})
    require(set(sheets) == REQUIRED_CONTACT_SHEETS, f"contact sheet set mismatch: {set(sheets)}")
    min_sizes = {
        "region_painted_sources": (600, 400),
        "season_tiles": (400, 250),
        "props": (400, 250),
        "item_icons": (600, 250),
        "crop_stages": (700, 700),
        "player_motion": (900, 600),
        "npc_motion": (900, 900),
        "npc_portraits": (600, 300),
        "ui_pieces": (500, 300),
        "ui_screens": (600, 500),
        "region_runtime_composites": (600, 400),
    }
    for sheet_id, sheet_path in sheets.items():
        require_png(ROOT / sheet_path, min_size=min_sizes[sheet_id], alpha_allowed=False, opaque_required=True)

    completion = manifest.get("package_completion", {})
    catalog_path = ROOT / completion.get("asset_catalog", {}).get("path", "")
    import_map_path = ROOT / completion.get("runtime_import_map", {}).get("path", "")
    report_path = ROOT / completion.get("delivery_report", {}).get("path", "")
    require(catalog_path.exists(), "missing asset catalog")
    require(import_map_path.exists(), "missing runtime import map")
    require(report_path.exists(), "missing delivery report")
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    summary = catalog.get("summary", {})
    require(summary.get("package_png_count", 0) >= 350, "asset catalog package PNG count too low")
    require(summary.get("runtime_png_count", 0) >= 250, "asset catalog runtime PNG count too low")
    require(summary.get("region_count") == len(REGIONS), "asset catalog region count mismatch")
    require(summary.get("ui_screen_count") == len(UI_SCREEN_IDS), "asset catalog UI screen count mismatch")
    require(summary.get("contact_sheet_count") == len(REQUIRED_CONTACT_SHEETS), "asset catalog contact sheet count mismatch")
    import_map = json.loads(import_map_path.read_text(encoding="utf-8"))
    entries = import_map.get("entries", [])
    require(len(entries) >= 250, "runtime import map entry count too low")
    require(all(entry.get("exists_in_runtime") for entry in entries), "runtime import map has missing runtime copies")
    report_text = report_path.read_text(encoding="utf-8")
    require("Status: complete_review_candidate" in report_text, "delivery report missing completion status")
    require("not launch-quality-approved" in report_text, "delivery report missing approval boundary")


def main() -> None:
    manifest = load_manifest()
    validate_manifest_basics(manifest)
    validate_style_and_ui(manifest)
    validate_tiles_and_crops()
    validate_characters()
    validate_items_props_fx()
    validate_regions(manifest)
    validate_world_layout(manifest)
    validate_gallery_files()
    validate_complete_delivery(manifest)
    print("OK: greenfield P0 art package validates")


if __name__ == "__main__":
    main()
