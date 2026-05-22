from __future__ import annotations

import json
import math
import random
import shutil
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "production" / "assets" / "base_asset_pack" / "v001"
RUNTIME = ROOT / "assets" / "art" / "greenfield_p0"
SCENE_PATH = ROOT / "scenes" / "dev" / "greenfield_p0_asset_gallery.tscn"

SEASONS = ["spring", "summer", "autumn", "winter"]
DIRECTIONS = ["down", "down_right", "right", "up_right", "up", "up_left", "left", "down_left"]
PROTAGONIST_ACTIONS = ["idle", "walk", "interact", "water", "pickup"]
NPC_IDS = ["aoi", "gen", "mika", "hana"]
PORTRAITS = ["neutral", "happy", "thinking"]
UI_SCREEN_IDS = ["hud", "inventory", "journal_map", "dialogue_gift", "pause_settings"]
REGION_LAYERS = ["base_ground", "terrain_details", "behind_player_structures", "ysort_props_structures", "foreground_occlusion", "shadow_overlay"]

REGIONS = [
    {"id": "home_area", "display": "HomeArea", "canvas": [1470, 1070], "theme": "home", "features": ["house", "mailbox", "well", "bench", "road_sign", "trees"]},
    {"id": "village", "display": "Village", "canvas": [1800, 1200], "theme": "village", "features": ["notice_board", "shop", "shrine", "square", "trees"]},
    {"id": "back_farm", "display": "BackFarm", "canvas": [1600, 1200], "theme": "farm", "features": ["farm_plots", "shed", "fence", "water_barrel"]},
    {"id": "forest_edge", "display": "ForestEdge", "canvas": [1700, 1150], "theme": "forest", "features": ["deep_trees", "forage", "moss_path", "small_shrine"]},
    {"id": "orchard", "display": "Orchard", "canvas": [1700, 1150], "theme": "orchard", "features": ["fruit_trees", "basket", "path", "fence"]},
    {"id": "pond", "display": "Pond", "canvas": [1600, 1100], "theme": "pond", "features": ["pond", "dock", "reeds", "rest_spot"]},
    {"id": "mountain_path", "display": "MountainPath", "canvas": [1700, 1200], "theme": "mountain_path", "features": ["stone_steps", "pines", "rail", "sign"]},
    {"id": "mountain_hut", "display": "MountainHut", "canvas": [1500, 1050], "theme": "hut", "features": ["hut", "woodpile", "herbs", "pines"]},
    {"id": "mountain", "display": "Mountain", "canvas": [1800, 1200], "theme": "mountain", "features": ["rocks", "pines", "stream", "clearing"]},
    {"id": "cliff_view", "display": "CliffView", "canvas": [1500, 1000], "theme": "cliff", "features": ["cliff", "view", "grass_edge", "rest_spot"]},
]

REGION_LAYOUT_PROFILES = {
    "home_area": {
        "road_signature": "home_public_lane_private_yard_spurs",
        "road_motif": "soft_home_lane",
        "composition_focal_point": (0.43, 0.45),
        "anchors": {
            "center": (0.43, 0.72), "north": (0.58, 0.08), "south": (0.43, 0.92),
            "west": (0.08, 0.72), "east": (0.92, 0.74), "nw": (0.18, 0.25),
            "ne": (0.82, 0.22), "sw": (0.22, 0.78), "se": (0.76, 0.75),
            "porch": (0.40, 0.50), "north_side_a": (0.53, 0.47), "north_side_b": (0.60, 0.25),
            "yard_bend": (0.40, 0.64), "front_lane_e": (0.64, 0.72), "east_bend": (0.78, 0.74),
            "mailbox": (0.23, 0.64), "mailbox_stand": (0.28, 0.72),
            "well": (0.72, 0.59), "well_stand": (0.64, 0.66), "bench": (0.22, 0.80),
            "bench_stand": (0.31, 0.72), "house": (0.40, 0.35),
            "road_sign": (0.84, 0.72),
        },
        "roads": [
            {"id": "public_front_lane", "role": "public_lane", "points": ["west", "mailbox_stand", "center", "front_lane_e", "east_bend", "east"], "width": 0.029, "alpha": 175, "style": "soft"},
            {"id": "home_walk", "role": "home_access", "points": ["south", "center", "yard_bend", "porch"], "width": 0.031, "alpha": 195, "style": "soft"},
            {"id": "north_side_lane", "role": "side_footpath", "points": ["porch", "north_side_a", "north_side_b", "north"], "width": 0.019, "alpha": 120, "style": "soft"},
            {"id": "well_footpath", "role": "utility_footpath", "points": ["yard_bend", "well_stand", "front_lane_e"], "width": 0.017, "alpha": 110, "style": "soft"},
            {"id": "bench_step", "role": "rest_access", "points": ["mailbox_stand", "bench_stand"], "width": 0.014, "alpha": 95, "style": "soft"},
        ],
        "object_zones": [
            {"id": "house", "role": "home_structure", "rect": (0.285, 0.135, 0.515, 0.445), "relation": "main lane stops at the porch apron, not under the house footprint"},
            {"id": "mailbox", "role": "roadside_prop", "rect": (0.180, 0.565, 0.275, 0.660), "relation": "beside the public front lane, not on it"},
            {"id": "well", "role": "yard_utility", "rect": (0.670, 0.485, 0.785, 0.645), "relation": "inside the private yard, reached from a narrow side footpath"},
            {"id": "bench", "role": "rest_prop", "rect": (0.125, 0.755, 0.310, 0.890), "relation": "rest spot near the fence, separated from the lane"},
        ],
    },
    "village": {
        "road_signature": "village_plaza_lane_doorstep_spurs",
        "road_motif": "settled_village_lane",
        "composition_focal_point": (0.55, 0.48),
        "anchors": {
            "center": (0.54, 0.58), "north": (0.44, 0.08), "south": (0.63, 0.92),
            "west": (0.08, 0.60), "east": (0.92, 0.50), "nw": (0.22, 0.26),
            "ne": (0.77, 0.23), "sw": (0.26, 0.78), "se": (0.73, 0.72),
            "square_a": (0.43, 0.50), "square_b": (0.60, 0.49), "square_c": (0.64, 0.62),
            "square_d": (0.48, 0.68), "house_a": (0.27, 0.35), "house_a_door": (0.33, 0.44),
            "house_b": (0.74, 0.37), "house_b_door": (0.68, 0.46),
            "shrine": (0.52, 0.32), "shrine_stand": (0.52, 0.43), "bench": (0.38, 0.77),
            "road_sign": (0.56, 0.60),
        },
        "roads": [
            {"id": "village_main_lane", "role": "village_through_lane", "points": ["west", "square_d", "square_c", "east"], "width": 0.028, "alpha": 170, "style": "settled"},
            {"id": "north_lane", "role": "village_through_lane", "points": ["north", "square_a", "square_b"], "width": 0.023, "alpha": 145, "style": "settled"},
            {"id": "south_lane", "role": "village_through_lane", "points": ["south", "square_c"], "width": 0.023, "alpha": 145, "style": "settled"},
            {"id": "plaza_edge", "role": "plaza_edge", "points": ["square_a", "square_b", "square_c", "square_d", "square_a"], "width": 0.017, "alpha": 92, "style": "settled"},
            {"id": "left_doorstep", "role": "doorstep", "points": ["square_a", "house_a_door"], "width": 0.014, "alpha": 95, "style": "settled"},
            {"id": "right_doorstep", "role": "doorstep", "points": ["square_b", "house_b_door"], "width": 0.014, "alpha": 95, "style": "settled"},
            {"id": "shrine_step", "role": "landmark_access", "points": ["square_a", "shrine_stand"], "width": 0.012, "alpha": 80, "style": "settled"},
        ],
        "object_zones": [
            {"id": "house_a", "role": "village_structure", "rect": (0.185, 0.155, 0.350, 0.365), "relation": "left house sits off the square road"},
            {"id": "house_b", "role": "village_structure", "rect": (0.670, 0.190, 0.815, 0.395), "relation": "right house sits above the east spur with a small doorstep"},
            {"id": "shrine", "role": "small_landmark", "rect": (0.485, 0.265, 0.555, 0.355), "relation": "landmark above the plaza with a narrow approach"},
            {"id": "bench", "role": "rest_prop", "rect": (0.315, 0.725, 0.450, 0.830), "relation": "rest prop below the plaza lane, not in road center"},
        ],
    },
    "back_farm": {
        "road_signature": "farm_service_lane_fields_shed_gate",
        "road_motif": "field_lane",
        "composition_focal_point": (0.48, 0.58),
        "anchors": {
            "center": (0.50, 0.62), "north": (0.50, 0.08), "south": (0.50, 0.94),
            "west": (0.08, 0.72), "east": (0.92, 0.73), "nw": (0.22, 0.23),
            "ne": (0.74, 0.24), "sw": (0.18, 0.80), "se": (0.84, 0.79),
            "shed": (0.80, 0.34), "shed_stand": (0.80, 0.39), "shed_bend": (0.74, 0.58), "field_gate": (0.50, 0.78),
            "farm_junction": (0.50, 0.64), "lane_a": (0.28, 0.70), "lane_b": (0.61, 0.60),
            "lane_c": (0.80, 0.72), "west_field_gap": (0.39, 0.67), "east_field_gap": (0.64, 0.57),
        },
        "roads": [
            {"id": "lower_access_lane", "role": "farm_access_lane", "points": ["west", "lane_a", "field_gate", "lane_c", "east"], "width": 0.026, "alpha": 150, "style": "field"},
            {"id": "farm_service_lane", "role": "farm_service_lane", "points": ["south", "field_gate", "farm_junction", "shed_bend", "shed_stand"], "width": 0.023, "alpha": 155, "style": "field"},
            {"id": "north_field_entry", "role": "farm_access_lane", "points": ["north", "farm_junction"], "width": 0.018, "alpha": 110, "style": "field"},
            {"id": "west_field_service", "role": "field_service_path", "points": ["farm_junction", "west_field_gap"], "width": 0.014, "alpha": 90, "style": "field"},
            {"id": "east_field_service", "role": "field_service_path", "points": ["farm_junction", "east_field_gap"], "width": 0.014, "alpha": 90, "style": "field"},
        ],
        "object_zones": [
            {"id": "shed", "role": "farm_structure", "rect": (0.735, 0.185, 0.865, 0.360), "relation": "shed stands above the service lane, with a clear approach point"},
            {"id": "field_block_west", "role": "farm_plots", "rect": (0.160, 0.305, 0.445, 0.630), "relation": "field block left of the central lane"},
            {"id": "field_block_east", "role": "farm_plots", "rect": (0.545, 0.305, 0.700, 0.525), "relation": "smaller field block right of the central lane"},
        ],
    },
    "forest_edge": {
        "road_signature": "forest_broken_moss_trail_west_north",
        "road_motif": "broken_moss_path",
        "composition_focal_point": (0.58, 0.45),
        "anchors": {
            "center": (0.56, 0.54), "north": (0.63, 0.08), "south": (0.38, 0.92),
            "west": (0.08, 0.62), "east": (0.92, 0.50), "nw": (0.24, 0.24),
            "ne": (0.78, 0.20), "sw": (0.20, 0.78), "se": (0.82, 0.74),
            "moss_a": (0.24, 0.64), "moss_b": (0.42, 0.55), "moss_c": (0.58, 0.43),
            "moss_d": (0.70, 0.31), "shrine": (0.57, 0.42),
        },
        "roads": [
            {"id": "broken_moss_west_north", "role": "forest_trail", "points": ["west", "moss_a", "moss_b", "moss_c", "moss_d", "north"], "width": 0.030, "alpha": 145, "style": "broken"},
            {"id": "faint_east_deer_path", "role": "forage_spur", "points": ["moss_c", "east"], "width": 0.020, "alpha": 105, "style": "broken"},
            {"id": "orchard_footpath", "role": "forest_orchard_link", "points": ["moss_b", "south"], "width": 0.018, "alpha": 95, "style": "broken"},
        ],
    },
    "orchard": {
        "road_signature": "orchard_diagonal_service_rows",
        "road_motif": "orchard_service_path",
        "composition_focal_point": (0.44, 0.52),
        "anchors": {
            "center": (0.45, 0.56), "north": (0.44, 0.08), "south": (0.54, 0.92),
            "west": (0.08, 0.48), "east": (0.92, 0.64), "nw": (0.20, 0.24),
            "ne": (0.73, 0.22), "sw": (0.30, 0.78), "se": (0.82, 0.75),
            "basket": (0.70, 0.77), "row_break_a": (0.34, 0.38), "row_break_b": (0.50, 0.55),
            "row_break_c": (0.68, 0.70),
        },
        "roads": [
            {"id": "diagonal_service_path", "role": "orchard_service_path", "points": ["north", "row_break_a", "row_break_b", "row_break_c", "south"], "width": 0.032, "alpha": 185, "style": "soft"},
            {"id": "east_cart_gap", "role": "orchard_cart_gap", "points": ["west", "row_break_b", "east"], "width": 0.022, "alpha": 130, "style": "soft"},
        ],
    },
    "pond": {
        "road_signature": "pond_crescent_bank_path",
        "road_motif": "water_edge_crescent",
        "composition_focal_point": (0.45, 0.49),
        "anchors": {
            "center": (0.50, 0.57), "north": (0.51, 0.08), "south": (0.36, 0.92),
            "west": (0.08, 0.65), "east": (0.92, 0.45), "nw": (0.20, 0.28),
            "ne": (0.78, 0.24), "sw": (0.22, 0.78), "se": (0.76, 0.72),
            "dock": (0.58, 0.68), "bank_a": (0.20, 0.70), "bank_b": (0.32, 0.76),
            "bank_c": (0.54, 0.75), "bank_d": (0.73, 0.61), "rest": (0.25, 0.78),
        },
        "roads": [
            {"id": "lower_bank_crescent", "role": "pond_bank_path", "points": ["west", "bank_a", "bank_b", "bank_c", "dock", "bank_d", "east"], "width": 0.028, "alpha": 170, "style": "soft"},
            {"id": "south_rest_spur", "role": "rest_access", "points": ["south", "rest", "bank_b"], "width": 0.022, "alpha": 125, "style": "soft"},
            {"id": "north_bank_arrival", "role": "pond_arrival_path", "points": ["north", "bank_d"], "width": 0.018, "alpha": 95, "style": "soft"},
        ],
    },
    "mountain_path": {
        "road_signature": "mountain_switchback_southwest_northeast",
        "road_motif": "stone_switchback",
        "composition_focal_point": (0.53, 0.50),
        "anchors": {
            "center": (0.52, 0.55), "north": (0.68, 0.08), "south": (0.31, 0.92),
            "west": (0.08, 0.72), "east": (0.92, 0.36), "nw": (0.24, 0.23),
            "ne": (0.78, 0.21), "sw": (0.24, 0.79), "se": (0.76, 0.72),
            "switch_a": (0.33, 0.76), "switch_b": (0.55, 0.66), "switch_c": (0.42, 0.53),
            "switch_d": (0.66, 0.43), "sign": (0.40, 0.57),
        },
        "roads": [
            {"id": "switchback_steps", "role": "mountain_switchback", "points": ["south", "switch_a", "switch_b", "switch_c", "switch_d", "east", "north"], "width": 0.026, "alpha": 160, "style": "stone"},
        ],
    },
    "mountain_hut": {
        "road_signature": "hut_curved_arrival_west_south",
        "road_motif": "hut_arrival_path",
        "composition_focal_point": (0.46, 0.44),
        "anchors": {
            "center": (0.47, 0.57), "north": (0.46, 0.08), "south": (0.35, 0.92),
            "west": (0.08, 0.57), "east": (0.92, 0.66), "nw": (0.22, 0.27),
            "ne": (0.75, 0.25), "sw": (0.25, 0.78), "se": (0.82, 0.76),
            "hut": (0.46, 0.43), "porch": (0.46, 0.58), "woodpile": (0.66, 0.64),
            "herb_patch": (0.34, 0.58),
        },
        "roads": [
            {"id": "hut_arrival_curve", "role": "mountain_hut_access", "points": ["south", "herb_patch", "porch", "hut"], "width": 0.030, "alpha": 175, "style": "soft"},
            {"id": "woodpile_side_path", "role": "workyard_path", "points": ["west", "porch", "woodpile", "east"], "width": 0.021, "alpha": 125, "style": "soft"},
            {"id": "ridge_arrival_path", "role": "ridge_link", "points": ["north", "porch"], "width": 0.018, "alpha": 105, "style": "soft"},
        ],
    },
    "mountain": {
        "road_signature": "mountain_uneven_trail_stream_crossing",
        "road_motif": "rocky_trail",
        "composition_focal_point": (0.56, 0.50),
        "anchors": {
            "center": (0.55, 0.56), "north": (0.60, 0.08), "south": (0.48, 0.92),
            "west": (0.08, 0.66), "east": (0.92, 0.41), "nw": (0.23, 0.24),
            "ne": (0.77, 0.22), "sw": (0.22, 0.79), "se": (0.80, 0.73),
            "trail_a": (0.25, 0.68), "trail_b": (0.43, 0.62), "trail_c": (0.58, 0.51),
            "trail_d": (0.75, 0.39), "clearing": (0.62, 0.36),
        },
        "roads": [
            {"id": "rocky_stream_crossing", "role": "rocky_trail", "points": ["west", "trail_a", "trail_b", "trail_c", "trail_d", "east"], "width": 0.025, "alpha": 145, "style": "stone"},
            {"id": "clearing_spur", "role": "clearing_spur", "points": ["trail_c", "clearing", "north"], "width": 0.019, "alpha": 105, "style": "broken"},
            {"id": "hut_descent", "role": "ridge_link", "points": ["trail_b", "south"], "width": 0.018, "alpha": 100, "style": "broken"},
        ],
    },
    "cliff_view": {
        "road_signature": "cliff_contour_ledge_path",
        "road_motif": "ledge_contour",
        "composition_focal_point": (0.50, 0.62),
        "anchors": {
            "center": (0.50, 0.62), "north": (0.44, 0.08), "south": (0.54, 0.92),
            "west": (0.08, 0.54), "east": (0.92, 0.47), "nw": (0.20, 0.27),
            "ne": (0.78, 0.23), "sw": (0.22, 0.76), "se": (0.82, 0.73),
            "ledge_a": (0.18, 0.53), "ledge_b": (0.38, 0.57), "ledge_c": (0.59, 0.55),
            "ledge_d": (0.80, 0.48), "rest": (0.49, 0.61),
        },
        "roads": [
            {"id": "contour_ledge", "role": "cliff_ledge_path", "points": ["west", "ledge_a", "ledge_b", "rest", "ledge_c", "ledge_d", "east"], "width": 0.029, "alpha": 170, "style": "soft"},
            {"id": "south_view_spur", "role": "view_rest_access", "points": ["south", "rest"], "width": 0.021, "alpha": 120, "style": "soft"},
        ],
    },
}

WORLD_LAYOUT_GRID = {
    "mountain_path": {"grid": (1, 0), "world_role": "north_trail_gate"},
    "mountain": {"grid": (2, 0), "world_role": "highland_resource_area"},
    "cliff_view": {"grid": (3, 0), "world_role": "scenic_secret_edge"},
    "forest_edge": {"grid": (0, 1), "world_role": "forage_and_secret_edge"},
    "village": {"grid": (1, 1), "world_role": "social_service_hub"},
    "mountain_hut": {"grid": (2, 1), "world_role": "remote_work_hut"},
    "orchard": {"grid": (0, 2), "world_role": "seasonal_harvest_area"},
    "home_area": {"grid": (1, 2), "world_role": "player_home_hub"},
    "pond": {"grid": (2, 2), "world_role": "water_rest_and_fishing"},
    "back_farm": {"grid": (1, 3), "world_role": "daily_farm_work_area"},
}

WORLD_ADJACENCIES = [
    {"id": "village_to_mountain_path", "from": "village", "from_edge": "north", "to": "mountain_path", "to_edge": "south", "route_role": "village_to_trail", "traversal": "walk", "note": "Village north road becomes the mountain footpath."},
    {"id": "mountain_path_to_mountain", "from": "mountain_path", "from_edge": "east", "to": "mountain", "to_edge": "west", "route_role": "trail_to_highland", "traversal": "walk", "note": "Switchback path hands off to rocky mountain trail."},
    {"id": "mountain_to_cliff_view", "from": "mountain", "from_edge": "east", "to": "cliff_view", "to_edge": "west", "route_role": "highland_to_view", "traversal": "walk", "note": "Rocky trail reaches the scenic cliff ledge."},
    {"id": "forest_edge_to_village", "from": "forest_edge", "from_edge": "east", "to": "village", "to_edge": "west", "route_role": "forest_to_village_lane", "traversal": "walk", "note": "Forage trail returns to the village lane."},
    {"id": "forest_edge_to_orchard", "from": "forest_edge", "from_edge": "south", "to": "orchard", "to_edge": "north", "route_role": "forest_orchard_link", "traversal": "walk", "note": "Soft nature seam between forest edge and orchard rows."},
    {"id": "orchard_to_home_area", "from": "orchard", "from_edge": "east", "to": "home_area", "to_edge": "west", "route_role": "orchard_home_lane", "traversal": "walk_cart", "note": "Orchard cart gap meets the home public lane."},
    {"id": "village_to_home_area", "from": "village", "from_edge": "south", "to": "home_area", "to_edge": "north", "route_role": "home_village_daily_lane", "traversal": "walk", "note": "Primary daily route from home to village."},
    {"id": "home_area_to_back_farm", "from": "home_area", "from_edge": "south", "to": "back_farm", "to_edge": "north", "route_role": "home_farm_work_lane", "traversal": "walk_cart", "note": "Back-yard work route into the farm plots."},
    {"id": "home_area_to_pond", "from": "home_area", "from_edge": "east", "to": "pond", "to_edge": "west", "route_role": "home_pond_rest_lane", "traversal": "walk", "note": "Public home lane continues toward pond rest space."},
    {"id": "village_to_mountain_hut", "from": "village", "from_edge": "east", "to": "mountain_hut", "to_edge": "west", "route_role": "village_hut_work_lane", "traversal": "walk", "note": "Village east spur reaches the remote hut workyard."},
    {"id": "mountain_to_mountain_hut", "from": "mountain", "from_edge": "south", "to": "mountain_hut", "to_edge": "north", "route_role": "ridge_hut_link", "traversal": "walk", "note": "Highland descent enters the hut from the ridge."},
    {"id": "mountain_hut_to_pond", "from": "mountain_hut", "from_edge": "south", "to": "pond", "to_edge": "north", "route_role": "hut_pond_supply_path", "traversal": "walk", "note": "Hut arrival path descends to the pond bank."},
]

ROAD_ROLE_RULES = {
    "public_lane": {"npc_usage": "daily_public", "collision_band": "wide", "path_cost": 1.0, "supports_cart": True},
    "home_access": {"npc_usage": "player_private", "collision_band": "medium", "path_cost": 0.9, "supports_cart": False},
    "side_footpath": {"npc_usage": "private_side", "collision_band": "narrow", "path_cost": 1.2, "supports_cart": False},
    "utility_footpath": {"npc_usage": "utility", "collision_band": "narrow", "path_cost": 1.3, "supports_cart": False},
    "rest_access": {"npc_usage": "rest_spot", "collision_band": "narrow", "path_cost": 1.4, "supports_cart": False},
    "village_through_lane": {"npc_usage": "daily_public", "collision_band": "wide", "path_cost": 0.8, "supports_cart": True},
    "plaza_edge": {"npc_usage": "social_idle", "collision_band": "medium", "path_cost": 1.0, "supports_cart": False},
    "doorstep": {"npc_usage": "resident_private", "collision_band": "narrow", "path_cost": 1.3, "supports_cart": False},
    "landmark_access": {"npc_usage": "ritual_visit", "collision_band": "narrow", "path_cost": 1.4, "supports_cart": False},
    "farm_access_lane": {"npc_usage": "farm_work", "collision_band": "wide", "path_cost": 0.9, "supports_cart": True},
    "farm_service_lane": {"npc_usage": "farm_work", "collision_band": "medium", "path_cost": 1.0, "supports_cart": True},
    "field_service_path": {"npc_usage": "farm_work", "collision_band": "narrow", "path_cost": 1.5, "supports_cart": False},
    "forest_trail": {"npc_usage": "forage_walk", "collision_band": "medium", "path_cost": 1.6, "supports_cart": False},
    "forage_spur": {"npc_usage": "forage_walk", "collision_band": "narrow", "path_cost": 1.9, "supports_cart": False},
    "forest_orchard_link": {"npc_usage": "forage_walk", "collision_band": "narrow", "path_cost": 1.7, "supports_cart": False},
    "orchard_service_path": {"npc_usage": "harvest_work", "collision_band": "medium", "path_cost": 1.0, "supports_cart": True},
    "orchard_cart_gap": {"npc_usage": "harvest_work", "collision_band": "medium", "path_cost": 0.9, "supports_cart": True},
    "pond_bank_path": {"npc_usage": "rest_walk", "collision_band": "medium", "path_cost": 1.2, "supports_cart": False},
    "pond_arrival_path": {"npc_usage": "rest_walk", "collision_band": "narrow", "path_cost": 1.4, "supports_cart": False},
    "mountain_switchback": {"npc_usage": "exploration_walk", "collision_band": "medium", "path_cost": 2.0, "supports_cart": False},
    "mountain_hut_access": {"npc_usage": "work_visit", "collision_band": "medium", "path_cost": 1.3, "supports_cart": False},
    "workyard_path": {"npc_usage": "work_visit", "collision_band": "narrow", "path_cost": 1.4, "supports_cart": False},
    "ridge_link": {"npc_usage": "exploration_walk", "collision_band": "narrow", "path_cost": 2.1, "supports_cart": False},
    "rocky_trail": {"npc_usage": "exploration_walk", "collision_band": "medium", "path_cost": 2.0, "supports_cart": False},
    "clearing_spur": {"npc_usage": "secret_walk", "collision_band": "narrow", "path_cost": 2.3, "supports_cart": False},
    "cliff_ledge_path": {"npc_usage": "scenic_walk", "collision_band": "medium", "path_cost": 1.8, "supports_cart": False},
    "view_rest_access": {"npc_usage": "rest_spot", "collision_band": "narrow", "path_cost": 1.6, "supports_cart": False},
}

SEASON_PALETTES = {
    "spring": {"grass": (121, 161, 86), "grass2": (154, 184, 104), "path": (197, 165, 109), "water": (94, 151, 160), "accent": (226, 172, 183), "light": (255, 238, 184, 70)},
    "summer": {"grass": (82, 139, 73), "grass2": (112, 166, 86), "path": (195, 156, 93), "water": (65, 138, 163), "accent": (238, 197, 89), "light": (255, 228, 142, 80)},
    "autumn": {"grass": (145, 132, 72), "grass2": (184, 131, 63), "path": (181, 139, 91), "water": (81, 131, 145), "accent": (203, 88, 51), "light": (255, 198, 126, 85)},
    "winter": {"grass": (172, 184, 174), "grass2": (213, 219, 209), "path": (178, 166, 147), "water": (105, 143, 155), "accent": (173, 190, 202), "light": (220, 235, 255, 65)},
}


def reset_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def save_image(image: Image.Image, path: Path) -> None:
    ensure_parent(path)
    image.save(path)


def save_runtime(image: Image.Image, relative_path: str) -> dict:
    prod_path = PACKAGE / "02_runtime_exports" / relative_path
    runtime_path = RUNTIME / relative_path
    save_image(image, prod_path)
    save_image(image, runtime_path)
    with Image.open(prod_path) as loaded:
        size = list(loaded.size)
        mode = loaded.mode
    return {
        "runtime_path": "res://" + str(runtime_path.relative_to(ROOT)).replace("\\", "/"),
        "production_path": str(prod_path.relative_to(ROOT)).replace("\\", "/"),
        "size": size,
        "mode": mode,
    }


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def texture(size: tuple[int, int], base: tuple[int, int, int], seed: int, alpha: int = 255) -> Image.Image:
    rng = random.Random(seed)
    img = Image.new("RGBA", size, (*base, alpha))
    px = img.load()
    for y in range(size[1]):
        for x in range(size[0]):
            n = rng.randint(-10, 10)
            stripe = int(6 * math.sin((x + y) * 0.035))
            r = max(0, min(255, base[0] + n + stripe))
            g = max(0, min(255, base[1] + n + stripe))
            b = max(0, min(255, base[2] + n + stripe))
            px[x, y] = (r, g, b, alpha)
    return img


def draw_soft_ellipse(layer: Image.Image, box: tuple[int, int, int, int], color: tuple[int, int, int, int]) -> None:
    shadow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse(box, fill=color)
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    layer.alpha_composite(shadow)


def draw_path(layer: Image.Image, points: list[tuple[int, int]], width: int, color: tuple[int, int, int, int]) -> None:
    path_layer = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(path_layer)
    edge = (126, 104, 70, max(60, color[3] // 2))
    draw.line(points, fill=edge, width=width + max(6, width // 10), joint="curve")
    draw.line(points, fill=color, width=width, joint="curve")
    draw.line(points, fill=(232, 207, 153, max(16, color[3] // 6)), width=max(3, width // 8), joint="curve")
    for point in points:
        x, y = point
        r = max(8, width // 5)
        draw.ellipse([x - r, y - r // 3, x + r, y + r // 3], fill=(244, 221, 170, max(14, color[3] // 10)))
    layer.alpha_composite(path_layer)


def draw_tree(layer: Image.Image, x: int, y: int, scale: float = 1.0, season: str = "spring") -> None:
    draw = ImageDraw.Draw(layer)
    trunk = (96, 67, 42, 255)
    palette = SEASON_PALETTES[season]
    leaf = palette["grass2"]
    draw_soft_ellipse(layer, (int(x - 65 * scale), int(y - 20 * scale), int(x + 70 * scale), int(y + 25 * scale)), (34, 28, 20, 42))
    draw.rounded_rectangle([x - 9 * scale, y - 58 * scale, x + 11 * scale, y + 2 * scale], radius=int(5 * scale), fill=trunk)
    draw.line([x - 4 * scale, y - 52 * scale, x - 4 * scale, y - 2 * scale], fill=(143, 103, 62, 150), width=max(1, int(3 * scale)))
    for dx, dy, radius in [(-36, -86, 42), (0, -108, 50), (38, -85, 42), (-5, -70, 46)]:
        draw.ellipse(
            [x + (dx - radius) * scale, y + (dy - radius) * scale, x + (dx + radius) * scale, y + (dy + radius) * scale],
            fill=(*leaf, 228),
            outline=(67, 103, 60, 200),
            width=max(1, int(2 * scale)),
        )
    for dx, dy, radius in [(-44, -103, 12), (-10, -125, 15), (32, -102, 13), (10, -80, 10)]:
        draw.ellipse(
            [x + (dx - radius) * scale, y + (dy - radius) * scale, x + (dx + radius) * scale, y + (dy + radius) * scale],
            fill=(min(255, leaf[0] + 42), min(255, leaf[1] + 38), min(255, leaf[2] + 28), 90),
        )


def draw_house(layer: Image.Image, x: int, y: int, scale: float = 1.0, hut: bool = False) -> None:
    draw = ImageDraw.Draw(layer)
    wall = (214, 196, 156, 255) if not hut else (158, 118, 79, 255)
    roof = (143, 75, 45, 255) if not hut else (102, 72, 48, 255)
    trim = (93, 62, 43, 255)
    w = int(250 * scale)
    h = int(120 * scale)
    roof_h = int(70 * scale)
    draw_soft_ellipse(layer, (x - w // 2 - 36, y - 18, x + w // 2 + 48, y + 30), (35, 28, 20, 46))
    draw.rectangle([x + int(w * 0.22), y - h - roof_h + int(8 * scale), x + int(w * 0.34), y - h - int(38 * scale)], fill=(92, 61, 43, 255))
    draw.polygon([(x - w // 2, y - h), (x, y - h - roof_h), (x + w // 2, y - h), (x + w // 2 + 24, y - h + 28), (x - w // 2 - 24, y - h + 28)], fill=roof, outline=trim)
    for i in range(-4, 5):
        xx = x + int(i * w / 9)
        draw.line([(xx, y - h - roof_h + 10), (xx + int(30 * scale), y - h + 28)], fill=(184, 105, 57, 150), width=max(1, int(2 * scale)))
    draw.rounded_rectangle([x - w // 2, y - h + 18, x + w // 2, y], radius=int(8 * scale), fill=wall, outline=trim, width=max(1, int(3 * scale)))
    draw.rectangle([x - w // 2 + int(12 * scale), y - int(20 * scale), x + w // 2 - int(12 * scale), y], fill=(177, 145, 102, 170))
    draw.rounded_rectangle([x - 28 * scale, y - 62 * scale, x + 28 * scale, y], radius=int(5 * scale), fill=(107, 70, 45, 255), outline=trim)
    draw.rounded_rectangle([x - 52 * scale, y - 12 * scale, x + 52 * scale, y + 16 * scale], radius=int(5 * scale), fill=(169, 128, 77, 255), outline=trim)
    for wx in [x - int(82 * scale), x + int(82 * scale)]:
        draw.rounded_rectangle([wx - 28 * scale, y - 75 * scale, wx + 28 * scale, y - 34 * scale], radius=int(4 * scale), fill=(100, 147, 151, 255), outline=trim)
        draw.line([wx - 24 * scale, y - 55 * scale, wx + 24 * scale, y - 55 * scale], fill=(223, 236, 220, 130), width=max(1, int(2 * scale)))


def draw_prop(layer: Image.Image, prop: str, x: int, y: int, scale: float = 1.0) -> None:
    draw = ImageDraw.Draw(layer)
    brown = (111, 72, 46, 255)
    outline = (68, 48, 35, 230)
    if prop == "mailbox":
        draw.rounded_rectangle([x - 23 * scale, y - 54 * scale, x + 23 * scale, y - 20 * scale], radius=int(8 * scale), fill=(151, 72, 55, 255), outline=outline)
        draw.rectangle([x - 5 * scale, y - 20 * scale, x + 5 * scale, y], fill=brown)
    elif prop == "well":
        draw.ellipse([x - 42 * scale, y - 40 * scale, x + 42 * scale, y + 12 * scale], fill=(121, 118, 103, 255), outline=outline, width=max(1, int(3 * scale)))
        draw.ellipse([x - 27 * scale, y - 29 * scale, x + 27 * scale, y + 3 * scale], fill=(63, 103, 117, 255))
        draw.line([x - 38 * scale, y - 40 * scale, x, y - 93 * scale, x + 38 * scale, y - 40 * scale], fill=brown, width=max(2, int(5 * scale)))
    elif prop == "bench":
        draw.rounded_rectangle([x - 70 * scale, y - 36 * scale, x + 70 * scale, y - 18 * scale], radius=int(5 * scale), fill=(145, 92, 52, 255), outline=outline)
        draw.rounded_rectangle([x - 78 * scale, y - 15 * scale, x + 78 * scale, y + 2 * scale], radius=int(5 * scale), fill=(158, 103, 57, 255), outline=outline)
        for leg in [-54, 54]:
            draw.rectangle([x + leg * scale - 5, y + 2 * scale, x + leg * scale + 5, y + 34 * scale], fill=brown)
    elif prop == "road_sign":
        draw.rectangle([x - 5 * scale, y - 78 * scale, x + 5 * scale, y + 6 * scale], fill=brown)
        draw.rounded_rectangle([x - 45 * scale, y - 76 * scale, x + 50 * scale, y - 42 * scale], radius=int(6 * scale), fill=(174, 122, 62, 255), outline=outline)
        draw.polygon([(x + 50 * scale, y - 76 * scale), (x + 75 * scale, y - 59 * scale), (x + 50 * scale, y - 42 * scale)], fill=(174, 122, 62, 255), outline=outline)
    elif prop == "fence":
        for i in range(5):
            xx = x + (i - 2) * 38 * scale
            draw.rectangle([xx - 4, y - 48 * scale, xx + 4, y], fill=brown)
        draw.line([x - 90 * scale, y - 38 * scale, x + 90 * scale, y - 20 * scale], fill=brown, width=max(2, int(7 * scale)))
    elif prop == "dock":
        draw.rounded_rectangle([x - 95 * scale, y - 28 * scale, x + 95 * scale, y + 22 * scale], radius=int(5 * scale), fill=(143, 98, 59, 255), outline=outline)
        for i in range(-4, 5):
            xx = x + i * 22 * scale
            draw.line([(xx, y - 28 * scale), (xx, y + 22 * scale)], fill=(96, 65, 43, 180), width=2)
    else:
        draw.rounded_rectangle([x - 30 * scale, y - 55 * scale, x + 30 * scale, y], radius=int(8 * scale), fill=(144, 101, 60, 255), outline=outline)


def draw_ground_brush(layer: Image.Image, width: int, height: int, theme: str, seed: int, season: str = "spring") -> None:
    rng = random.Random(seed)
    detail = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(detail)
    palette = SEASON_PALETTES[season]
    grass_dark = tuple(max(0, c - 32) for c in palette["grass"])
    grass_light = tuple(min(255, c + 28) for c in palette["grass2"])
    flower = palette["accent"]
    for _ in range(150):
        x = rng.randint(20, width - 20)
        y = rng.randint(20, height - 20)
        rx = rng.randint(30, 110)
        ry = rng.randint(12, 44)
        tint = grass_light if rng.random() < 0.55 else grass_dark
        draw.ellipse([x - rx, y - ry, x + rx, y + ry], fill=(*tint, rng.randint(12, 28)))
    for _ in range(420):
        x = rng.randint(18, width - 18)
        y = rng.randint(18, height - 18)
        if rng.random() < 0.75:
            length = rng.randint(8, 22)
            draw.line([x, y, x + rng.randint(-8, 9), y - length], fill=(*grass_light, rng.randint(58, 105)), width=1)
            draw.line([x + 2, y, x + rng.randint(-6, 8), y - length // 2], fill=(*grass_dark, rng.randint(45, 90)), width=1)
        else:
            draw.ellipse([x - 2, y - 2, x + 3, y + 3], fill=(*flower, rng.randint(80, 150)))

    if theme in {"mountain", "mountain_path", "cliff"}:
        for _ in range(45):
            x = rng.randint(40, width - 40)
            y = rng.randint(60, height - 40)
            r = rng.randint(10, 26)
            draw.polygon(
                [(x - r, y + r // 2), (x - r // 3, y - r), (x + r, y - r // 3), (x + r // 2, y + r)],
                fill=(120, 122, 108, rng.randint(105, 165)),
                outline=(80, 78, 66, 120),
            )
    if theme in {"forest", "orchard"}:
        for _ in range(70):
            x = rng.randint(20, width - 20)
            y = rng.randint(20, height - 20)
            draw.ellipse([x - 8, y - 4, x + 9, y + 5], fill=(*grass_dark, rng.randint(45, 90)))
    if theme == "pond":
        for _ in range(55):
            x = rng.randint(30, width - 30)
            y = rng.randint(int(height * 0.28), int(height * 0.76))
            draw.line([x, y, x + rng.randint(-6, 6), y - rng.randint(18, 42)], fill=(78, 120, 76, rng.randint(120, 190)), width=2)
    layer.alpha_composite(detail)


def draw_small_bush(layer: Image.Image, x: int, y: int, scale: float, season: str = "spring") -> None:
    draw = ImageDraw.Draw(layer)
    palette = SEASON_PALETTES[season]
    for dx, dy, r in [(-22, 0, 24), (0, -10, 28), (24, 2, 22)]:
        draw.ellipse(
            [x + (dx - r) * scale, y + (dy - r) * scale, x + (dx + r) * scale, y + (dy + r) * scale],
            fill=(*palette["grass2"], 205),
            outline=(73, 111, 61, 130),
        )
    if season in {"spring", "summer", "autumn"}:
        for i in range(6):
            px = x + int((i - 2.5) * 13 * scale)
            py = y - int((8 + (i % 2) * 9) * scale)
            draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(*palette["accent"], 190))


def draw_flower_patch(layer: Image.Image, x: int, y: int, scale: float, season: str = "spring", seed: int = 0) -> None:
    rng = random.Random(seed)
    draw = ImageDraw.Draw(layer)
    palette = SEASON_PALETTES[season]
    grass = tuple(max(0, c - 24) for c in palette["grass"])
    for _ in range(24):
        px = x + int(rng.randint(-52, 52) * scale)
        py = y + int(rng.randint(-22, 22) * scale)
        draw.line([px, py + 8, px + rng.randint(-4, 4), py - rng.randint(8, 18)], fill=(*grass, 150), width=max(1, int(2 * scale)))
        if rng.random() < 0.75:
            draw.ellipse([px - 3, py - 12, px + 4, py - 5], fill=(*palette["accent"], 170))


def draw_stone_cluster(layer: Image.Image, x: int, y: int, scale: float, seed: int = 0) -> None:
    rng = random.Random(seed)
    draw = ImageDraw.Draw(layer)
    for idx in range(7):
        px = x + int(rng.randint(-70, 70) * scale)
        py = y + int(rng.randint(-32, 32) * scale)
        r = int(rng.randint(8, 24) * scale)
        color = (rng.randint(110, 137), rng.randint(112, 132), rng.randint(98, 118), rng.randint(135, 205))
        draw.polygon(
            [(px - r, py + r // 2), (px - r // 2, py - r), (px + r, py - r // 3), (px + r // 2, py + r)],
            fill=color,
            outline=(76, 73, 63, 125),
        )


def draw_reed_cluster(layer: Image.Image, x: int, y: int, scale: float, seed: int = 0) -> None:
    rng = random.Random(seed)
    draw = ImageDraw.Draw(layer)
    for _ in range(28):
        px = x + int(rng.randint(-60, 60) * scale)
        py = y + int(rng.randint(-20, 20) * scale)
        h = int(rng.randint(28, 70) * scale)
        draw.line([px, py, px + rng.randint(-8, 8), py - h], fill=(65, 104, 65, rng.randint(145, 210)), width=max(1, int(3 * scale)))
        if rng.random() < 0.35:
            draw.ellipse([px - 3, py - h - 8, px + 5, py - h + 12], fill=(118, 91, 54, 165))


def decorate_region_layers(base: Image.Image, terrain: Image.Image, ysort: Image.Image, foreground: Image.Image, region: dict) -> None:
    rid = region["id"]
    theme = region["theme"]
    width, height = base.size
    draw_ground_brush(base, width, height, theme, seed=9000 + len(rid))
    pts = region_points(width, height, rid)

    if theme == "home":
        draw_soft_ellipse(terrain, (int(width * 0.28), int(height * 0.48), int(width * 0.58), int(height * 0.76)), (202, 179, 122, 58))
        draw_soft_ellipse(terrain, (int(width * 0.58), int(height * 0.49), int(width * 0.82), int(height * 0.70)), (196, 176, 120, 38))
        draw_soft_ellipse(terrain, (int(width * 0.12), int(height * 0.70), int(width * 0.34), int(height * 0.90)), (188, 158, 100, 34))
        for pos in [(int(width * 0.38), int(height * 0.49)), (int(width * 0.62), int(height * 0.49)), (int(width * 0.74), int(height * 0.78))]:
            draw_small_bush(ysort, pos[0], pos[1], 0.75)
        draw_flower_patch(terrain, int(width * 0.27), int(height * 0.62), 1.0, seed=1201)
        draw_flower_patch(terrain, int(width * 0.72), int(height * 0.62), 0.8, seed=1202)
        draw_tree(foreground, int(width * 0.15), int(height * 0.3), 1.15, "spring")
        draw_tree(foreground, int(width * 0.88), int(height * 0.32), 1.15, "spring")
        draw_prop(ysort, "fence", int(width * 0.18), int(height * 0.82), 1.2)
    elif theme == "village":
        draw_soft_ellipse(terrain, (int(width * 0.36), int(height * 0.43), int(width * 0.69), int(height * 0.74)), (207, 184, 128, 58))
        draw_soft_ellipse(terrain, (int(width * 0.19), int(height * 0.32), int(width * 0.38), int(height * 0.48)), (202, 178, 120, 38))
        draw_soft_ellipse(terrain, (int(width * 0.64), int(height * 0.34), int(width * 0.82), int(height * 0.51)), (202, 178, 120, 34))
        for pos in [(int(width * 0.18), int(height * 0.70)), (int(width * 0.84), int(height * 0.67)), (int(width * 0.50), int(height * 0.76))]:
            draw_small_bush(ysort, pos[0], pos[1], 0.65)
        draw_flower_patch(terrain, int(width * 0.48), int(height * 0.55), 0.75, seed=1301)
        draw_flower_patch(terrain, int(width * 0.60), int(height * 0.48), 0.55, seed=1302)
        draw_prop(ysort, "bench", pts["bench"][0], pts["bench"][1], 0.9)
        draw_prop(ysort, "shrine", pts["shrine"][0], pts["shrine"][1], 0.9)
    elif theme == "farm":
        draw_soft_ellipse(terrain, (int(width * 0.13), int(height * 0.28), int(width * 0.47), int(height * 0.65)), (159, 119, 73, 42))
        draw_soft_ellipse(terrain, (int(width * 0.52), int(height * 0.28), int(width * 0.72), int(height * 0.56)), (159, 119, 73, 34))
        draw_soft_ellipse(terrain, (int(width * 0.68), int(height * 0.34), int(width * 0.87), int(height * 0.55)), (198, 177, 123, 40))
        draw_prop(ysort, "fence", int(width * 0.32), int(height * 0.24), 1.6)
        draw_prop(ysort, "fence", int(width * 0.68), int(height * 0.24), 1.6)
        draw_stone_cluster(terrain, int(width * 0.16), int(height * 0.28), 0.75, seed=1401)
        draw_flower_patch(terrain, int(width * 0.76), int(height * 0.80), 0.8, seed=1402)
        for pos in [(int(width * 0.15), int(height * 0.75)), (int(width * 0.87), int(height * 0.78))]:
            draw_small_bush(ysort, pos[0], pos[1], 0.7)
    elif theme == "forest":
        for pos in [pts["nw"], pts["ne"], pts["west"], pts["east"], pts["sw"], pts["se"], pts["north"]]:
            draw_tree(foreground if pos[1] > height * 0.55 else ysort, pos[0], pos[1], 1.0, "spring")
        draw_flower_patch(terrain, int(width * 0.36), int(height * 0.55), 0.85, seed=1501)
        draw_stone_cluster(terrain, int(width * 0.58), int(height * 0.66), 0.6, seed=1502)
        draw_prop(ysort, "shrine", int(width * 0.56), int(height * 0.42), 0.55)
    elif theme == "orchard":
        for row in [0.3, 0.48, 0.66]:
            for col in [0.22, 0.40, 0.58, 0.76]:
                draw_tree(ysort if row < 0.55 else foreground, int(width * col), int(height * row), 0.62, "spring")
        draw_flower_patch(terrain, int(width * 0.50), int(height * 0.76), 0.75, seed=1601)
        draw_prop(ysort, "storage_crate", int(width * 0.73), int(height * 0.77), 0.8)
    elif theme == "pond":
        draw_prop(ysort, "bench", int(width * 0.24), int(height * 0.78), 0.85)
        draw_reed_cluster(foreground, int(width * 0.18), int(height * 0.56), 1.0, seed=1701)
        draw_reed_cluster(foreground, int(width * 0.79), int(height * 0.47), 0.9, seed=1702)
        draw_small_bush(foreground, int(width * 0.18), int(height * 0.58), 0.75)
        draw_small_bush(foreground, int(width * 0.82), int(height * 0.52), 0.75)
    elif theme == "mountain_path":
        draw_stone_cluster(terrain, int(width * 0.33), int(height * 0.38), 1.1, seed=1801)
        draw_stone_cluster(terrain, int(width * 0.72), int(height * 0.42), 0.9, seed=1802)
        draw_prop(ysort, "road_sign", int(width * 0.40), int(height * 0.56), 0.85)
        draw_prop(ysort, "fence", int(width * 0.62), int(height * 0.62), 1.15)
    elif theme == "hut":
        draw_prop(ysort, "storage_crate", int(width * 0.66), int(height * 0.63), 1.0)
        draw_prop(ysort, "fence", int(width * 0.26), int(height * 0.68), 1.1)
        draw_flower_patch(terrain, int(width * 0.34), int(height * 0.58), 0.8, seed=1901)
        draw_stone_cluster(terrain, int(width * 0.78), int(height * 0.70), 0.75, seed=1902)
        for pos in [(int(width * 0.24), int(height * 0.42)), (int(width * 0.78), int(height * 0.42))]:
            draw_tree(foreground, pos[0], pos[1], 0.95, "spring")
    elif theme == "mountain":
        for pos in [pts["nw"], pts["ne"], pts["west"], pts["east"], pts["sw"], pts["se"]]:
            draw_tree(foreground if pos[1] > height * 0.5 else ysort, pos[0], pos[1], 0.95, "spring")
        draw_stone_cluster(terrain, int(width * 0.34), int(height * 0.64), 1.1, seed=2001)
        draw_stone_cluster(terrain, int(width * 0.66), int(height * 0.34), 0.9, seed=2002)
        ImageDraw.Draw(terrain).line([int(width * 0.2), int(height * 0.78), int(width * 0.82), int(height * 0.38)], fill=(87, 134, 151, 140), width=max(18, width // 70))
    elif theme == "cliff":
        draw_flower_patch(terrain, int(width * 0.22), int(height * 0.42), 0.75, seed=2101)
        draw_stone_cluster(terrain, int(width * 0.78), int(height * 0.38), 0.95, seed=2102)
        draw_prop(ysort, "bench", int(width * 0.48), int(height * 0.61), 0.95)
        for pos in [(int(width * 0.18), int(height * 0.48)), (int(width * 0.82), int(height * 0.44))]:
            draw_small_bush(foreground, pos[0], pos[1], 0.8)


def draw_character(direction: str, palette: dict[str, tuple[int, int, int]], action: str = "idle", frame: int = 0, size: int = 128) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, foot_y = size // 2, 106
    bob = 0
    if action in {"walk", "water", "pickup"}:
        bob = -2 if frame % 2 else 1
    side = 1 if "right" in direction else -1 if "left" in direction else 0
    back = direction.startswith("up")
    draw.ellipse([cx - 22, foot_y - 8, cx + 22, foot_y + 5], fill=(55, 45, 34, 55))
    draw.rounded_rectangle([cx - 16, foot_y - 58 + bob, cx + 16, foot_y - 18 + bob], radius=10, fill=palette["shirt"], outline=palette["outline"], width=2)
    draw.rectangle([cx - 16, foot_y - 20 + bob, cx - 3, foot_y - 3], fill=palette["pants"])
    draw.rectangle([cx + 3, foot_y - 20 + bob, cx + 16, foot_y - 3], fill=palette["pants"])
    draw.ellipse([cx - 19, foot_y - 88 + bob, cx + 19, foot_y - 50 + bob], fill=palette["skin"], outline=palette["outline"], width=2)
    hair_box = [cx - 22, foot_y - 91 + bob, cx + 22, foot_y - 60 + bob]
    if back:
        draw.ellipse(hair_box, fill=palette["hair"], outline=palette["outline"], width=2)
    else:
        draw.pieslice(hair_box, start=180, end=360, fill=palette["hair"], outline=palette["outline"], width=2)
        eye_y = foot_y - 70 + bob
        eye_shift = side * 4
        draw.ellipse([cx - 8 + eye_shift, eye_y, cx - 4 + eye_shift, eye_y + 4], fill=(40, 35, 32, 255))
        draw.ellipse([cx + 6 + eye_shift, eye_y, cx + 10 + eye_shift, eye_y + 4], fill=(40, 35, 32, 255))
    arm_y = foot_y - 48 + bob
    if action == "water":
        draw.line([cx + 17, arm_y, cx + 34, arm_y - 14], fill=palette["skin"], width=5)
        draw.ellipse([cx + 26, arm_y - 25, cx + 50, arm_y - 6], fill=(89, 128, 135, 255), outline=palette["outline"])
    elif action == "pickup":
        draw.line([cx - 17, arm_y, cx - 28, arm_y + 16], fill=palette["skin"], width=5)
        draw.line([cx + 17, arm_y, cx + 28, arm_y + 16], fill=palette["skin"], width=5)
    elif action == "interact":
        draw.line([cx + 17, arm_y, cx + 34 + side * 4, arm_y - 6], fill=palette["skin"], width=5)
    else:
        swing = (-1 if frame % 2 else 1) if action == "walk" else 0
        draw.line([cx - 17, arm_y, cx - 28, arm_y + 18 * swing], fill=palette["skin"], width=5)
        draw.line([cx + 17, arm_y, cx + 28, arm_y - 18 * swing], fill=palette["skin"], width=5)
    return img


def make_sheet(frames: list[Image.Image]) -> Image.Image:
    sheet = Image.new("RGBA", (frames[0].width * len(frames), frames[0].height), (0, 0, 0, 0))
    for idx, frame in enumerate(frames):
        sheet.alpha_composite(frame, (idx * frame.width, 0))
    return sheet


def generate_style_mother() -> dict:
    img = Image.new("RGBA", (1200, 760), (239, 231, 207, 255))
    draw = ImageDraw.Draw(img)
    draw.text((40, 30), "Greenfield P0 Style Mother", fill=(69, 53, 39, 255))
    for idx, season in enumerate(SEASONS):
        p = SEASON_PALETTES[season]
        x = 60 + idx * 270
        draw.rounded_rectangle([x, 90, x + 220, 260], radius=16, fill=(*p["grass"], 255), outline=(75, 70, 52, 255), width=3)
        draw.line([x + 20, 220, x + 200, 145], fill=(*p["path"], 255), width=28)
        draw.ellipse([x + 135, 120, x + 200, 176], fill=(*p["accent"], 230))
        draw.text((x, 280), season, fill=(69, 53, 39, 255))
    for i, color in enumerate([(69, 53, 39), (143, 75, 45), (214, 196, 156), (94, 151, 160), (121, 161, 86), (197, 165, 109)]):
        draw.rounded_rectangle([80 + i * 165, 380, 190 + i * 165, 490], radius=10, fill=(*color, 255), outline=(63, 50, 37, 255), width=2)
    draw.text((70, 560), "Warm low-saturation storybook shapes, clear silhouettes, fixed 3/4 top-down readability.", fill=(69, 53, 39, 255))
    path = PACKAGE / "01_mother_images" / "style" / "greenfield_p0_style_mother.png"
    save_image(img, path)
    return {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "size": list(img.size)}


def generate_tiles(manifest: dict) -> None:
    tile_types = ["grass_a", "grass_b", "dirt", "stone_path", "field_tilled_dry", "field_tilled_wet", "water_edge", "wood_floor", "shadow_soft"]
    records = []
    for season in SEASONS:
        p = SEASON_PALETTES[season]
        for idx, tile_type in enumerate(tile_types):
            base = p["grass"]
            if "grass_b" == tile_type:
                base = p["grass2"]
            elif "dirt" in tile_type or "path" in tile_type or "field" in tile_type:
                base = p["path"]
            elif "water" in tile_type:
                base = p["water"]
            elif tile_type == "wood_floor":
                base = (139, 92, 55)
            elif tile_type == "shadow_soft":
                base = (70, 72, 58)
            img = texture((64, 64), base, seed=1000 + idx + SEASONS.index(season) * 100, alpha=160 if tile_type == "shadow_soft" else 255)
            draw = ImageDraw.Draw(img)
            if "field" in tile_type:
                for y in range(10, 64, 14):
                    draw.line([(2, y), (62, y - 5)], fill=(104, 78, 48, 150), width=3)
            if tile_type == "stone_path":
                for _ in range(12):
                    x = random.Random(idx * 90 + _).randint(0, 58)
                    y = random.Random(idx * 120 + _).randint(0, 58)
                    draw.ellipse([x, y, x + 8, y + 5], fill=(173, 157, 126, 170))
            if tile_type == "water_edge":
                draw.arc([4, 18, 74, 78], 190, 340, fill=(222, 235, 222, 150), width=3)
            records.append(save_runtime(img, f"tiles/{season}/tile_{tile_type}_{season}_64.png"))
    manifest["tiles"] = {"types": tile_types, "seasons": SEASONS, "records": records}


def generate_characters(manifest: dict) -> None:
    character_records = []
    palettes = {
        "player": {"skin": (226, 178, 136, 255), "hair": (87, 54, 37, 255), "shirt": (96, 126, 116, 255), "pants": (75, 79, 82, 255), "outline": (55, 43, 35, 255)},
        "aoi": {"skin": (226, 180, 137, 255), "hair": (44, 54, 67, 255), "shirt": (78, 126, 152, 255), "pants": (68, 82, 89, 255), "outline": (48, 42, 38, 255)},
        "gen": {"skin": (206, 157, 113, 255), "hair": (104, 93, 76, 255), "shirt": (131, 108, 72, 255), "pants": (70, 68, 61, 255), "outline": (49, 42, 34, 255)},
        "mika": {"skin": (232, 185, 146, 255), "hair": (93, 62, 80, 255), "shirt": (156, 96, 115, 255), "pants": (78, 70, 84, 255), "outline": (51, 40, 42, 255)},
        "hana": {"skin": (224, 176, 132, 255), "hair": (73, 64, 49, 255), "shirt": (112, 145, 86, 255), "pants": (75, 79, 64, 255), "outline": (49, 43, 34, 255)},
    }
    mother = Image.new("RGBA", (8 * 128, 6 * 128), (244, 238, 220, 255))
    for action_idx, action in enumerate(PROTAGONIST_ACTIONS):
        for dir_idx, direction in enumerate(DIRECTIONS):
            if action == "idle":
                frame = draw_character(direction, palettes["player"], action)
                record = save_runtime(frame, f"characters/player/chr_player_base_idle_{direction}_128.png")
            else:
                frames = [draw_character(direction, palettes["player"], action, frame=i) for i in range(4)]
                record = save_runtime(make_sheet(frames), f"characters/player/chr_player_base_{action}_{direction}_4x128.png")
                frame = frames[0]
            mother.alpha_composite(frame, (dir_idx * 128, action_idx * 128))
            character_records.append({"id": "player", "action": action, "direction": direction, **record})
    save_image(mother, PACKAGE / "01_mother_images" / "characters" / "player_8dir_motion_mother.png")

    npc_records = []
    for npc in NPC_IDS:
        npc_mother = Image.new("RGBA", (8 * 128, 2 * 128), (244, 238, 220, 255))
        for dir_idx, direction in enumerate(DIRECTIONS):
            idle = draw_character(direction, palettes[npc], "idle")
            walk = make_sheet([draw_character(direction, palettes[npc], "walk", frame=i) for i in range(4)])
            npc_mother.alpha_composite(idle, (dir_idx * 128, 0))
            npc_mother.alpha_composite(walk.crop((0, 0, 128, 128)), (dir_idx * 128, 128))
            npc_records.append({"id": npc, "action": "idle", "direction": direction, **save_runtime(idle, f"characters/npc/npc_{npc}_idle_{direction}_128.png")})
            npc_records.append({"id": npc, "action": "walk", "direction": direction, **save_runtime(walk, f"characters/npc/npc_{npc}_walk_{direction}_4x128.png")})
        save_image(npc_mother, PACKAGE / "01_mother_images" / "characters" / f"npc_{npc}_8dir_motion_mother.png")
        for mood in PORTRAITS:
            portrait = Image.new("RGBA", (512, 512), (236, 224, 198, 255))
            draw = ImageDraw.Draw(portrait)
            draw_soft_ellipse(portrait, (132, 310, 380, 430), (60, 45, 35, 45))
            draw.rounded_rectangle([170, 190, 342, 420], radius=58, fill=palettes[npc]["shirt"], outline=palettes[npc]["outline"], width=8)
            draw.ellipse([150, 80, 362, 292], fill=palettes[npc]["skin"], outline=palettes[npc]["outline"], width=8)
            draw.pieslice([126, 42, 386, 246], 180, 360, fill=palettes[npc]["hair"], outline=palettes[npc]["outline"], width=8)
            eye_y = 180
            draw.ellipse([208, eye_y, 225, eye_y + 16], fill=(42, 35, 31, 255))
            draw.ellipse([287, eye_y, 304, eye_y + 16], fill=(42, 35, 31, 255))
            if mood == "happy":
                draw.arc([218, 210, 294, 260], 10, 170, fill=(116, 61, 62, 255), width=6)
            elif mood == "thinking":
                draw.line([222, 238, 292, 230], fill=(116, 61, 62, 255), width=5)
                draw.ellipse([355, 104, 390, 139], fill=(255, 255, 255, 210), outline=palettes[npc]["outline"], width=3)
            else:
                draw.line([230, 235, 282, 235], fill=(116, 61, 62, 255), width=5)
            npc_records.append({"id": npc, "portrait": mood, **save_runtime(portrait, f"portraits/npc_{npc}_portrait_{mood}_512.png")})
    manifest["characters"] = {"directions": DIRECTIONS, "protagonist_actions": PROTAGONIST_ACTIONS, "p0_npcs": NPC_IDS, "player_records": character_records, "npc_records": npc_records}


def generate_items_and_crops(manifest: dict) -> None:
    item_records = []
    items_path = ROOT / "game" / "data" / "items.json"
    items = json.loads(items_path.read_text(encoding="utf-8")) if items_path.exists() else []
    for idx, item in enumerate(items):
        item_id = str(item.get("item_id", item.get("id", f"item_{idx}")))
        category = str(item.get("category", "item"))
        base = {
            "seed": (190, 150, 70),
            "crop": (118, 160, 75),
            "material": (139, 112, 82),
            "forage": (110, 154, 86),
            "fish": (89, 143, 157),
            "food": (205, 157, 91),
            "key": (174, 132, 60),
        }.get(category, (143, 124, 93))
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw_soft_ellipse(img, (10, 46, 54, 60), (49, 38, 28, 45))
        draw.rounded_rectangle([14, 12, 50, 48], radius=10, fill=(*base, 255), outline=(68, 50, 35, 230), width=2)
        draw.line([22, 22, 42, 38], fill=(255, 240, 184, 130), width=3)
        item_records.append({"id": item_id, "category": category, **save_runtime(img, f"items/{item_id}_64.png")})

    crop_records = []
    crops_path = ROOT / "game" / "data" / "crops.json"
    crops = json.loads(crops_path.read_text(encoding="utf-8")) if crops_path.exists() else []
    for crop_idx, crop in enumerate(crops):
        crop_id = str(crop.get("crop_id", crop.get("id", f"crop_{crop_idx}")))
        for season in SEASONS:
            p = SEASON_PALETTES[season]
            for stage in range(4):
                img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                draw.ellipse([12, 42, 52, 58], fill=(83, 61, 42, 120))
                if stage == 0:
                    draw.ellipse([27, 34, 37, 44], fill=(112, 81, 48, 255))
                else:
                    h = 10 + stage * 10
                    draw.line([32, 46, 32, 46 - h], fill=(62, 112, 56, 255), width=4)
                    draw.ellipse([19, 38 - h, 34, 50 - h], fill=(*p["grass2"], 255))
                    draw.ellipse([30, 34 - h, 47, 46 - h], fill=(*p["grass"], 255))
                    if stage == 3:
                        draw.ellipse([25, 18, 42, 35], fill=(*p["accent"], 255), outline=(82, 72, 45, 180))
                crop_records.append({"crop_id": crop_id, "season": season, "stage": stage, **save_runtime(img, f"crops/{season}/crop_{crop_id}_stage_{stage:02d}_{season}_64.png")})
    manifest["items"] = item_records
    manifest["crops"] = crop_records


def generate_props_ui_fx(manifest: dict) -> None:
    prop_names = ["house_player", "mailbox", "well", "bench", "road_sign", "fence", "tree", "rock", "storage_crate", "farm_shed", "dock", "shrine", "mountain_hut"]
    prop_records = []
    board = Image.new("RGBA", (1024, 768), (241, 234, 214, 255))
    for idx, prop in enumerate(prop_names):
        w, h = (256, 256)
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        if prop == "house_player":
            draw_house(img, 128, 210, 0.72)
        elif prop == "tree":
            draw_tree(img, 128, 210, 1.05, "spring")
        elif prop == "mountain_hut":
            draw_house(img, 128, 210, 0.65, hut=True)
        elif prop == "rock":
            draw = ImageDraw.Draw(img)
            draw.polygon([(84, 190), (122, 136), (178, 155), (200, 204), (110, 220)], fill=(120, 122, 108, 255), outline=(67, 66, 58, 230))
        elif prop == "storage_crate":
            draw = ImageDraw.Draw(img)
            draw.rounded_rectangle([78, 126, 178, 210], radius=8, fill=(151, 101, 56, 255), outline=(70, 51, 36, 230), width=4)
            draw.line([86, 135, 170, 202], fill=(101, 67, 41, 160), width=4)
        elif prop == "farm_shed":
            draw_house(img, 128, 210, 0.45, hut=True)
        elif prop == "shrine":
            draw_house(img, 128, 210, 0.38, hut=True)
            ImageDraw.Draw(img).rectangle([94, 160, 162, 213], fill=(133, 60, 49, 255), outline=(70, 45, 36, 255), width=3)
        else:
            draw_prop(img, prop.replace("road_sign", "road_sign"), 128, 190, 1.0)
        prop_records.append({"id": prop, **save_runtime(img, f"props/prop_{prop}_256.png")})
        board.alpha_composite(img.resize((128, 128)), ((idx % 6) * 160 + 24, (idx // 6) * 180 + 50))
        ImageDraw.Draw(board).text(((idx % 6) * 160 + 24, (idx // 6) * 180 + 182), prop, fill=(70, 55, 40, 255))
    save_image(board, PACKAGE / "01_mother_images" / "props" / "prop_mother_board.png")
    manifest["props"] = prop_records

    ui_records = []
    ui_board = Image.new("RGBA", (1200, 800), (235, 225, 199, 255))
    draw = ImageDraw.Draw(ui_board)
    draw.text((40, 32), "UI Layout Mother Board", fill=(70, 53, 38, 255))
    draw.rounded_rectangle([40, 90, 520, 180], radius=16, fill=(246, 236, 207, 255), outline=(126, 87, 49, 255), width=5)
    draw.text((70, 122), "HUD: date / time / weather / money", fill=(70, 53, 38, 255))
    draw.rounded_rectangle([40, 520, 760, 740], radius=18, fill=(246, 236, 207, 255), outline=(126, 87, 49, 255), width=6)
    draw.text((78, 560), "Dialogue box + portrait frame", fill=(70, 53, 38, 255))
    draw.rounded_rectangle([810, 90, 1160, 520], radius=18, fill=(236, 221, 188, 255), outline=(126, 87, 49, 255), width=6)
    draw.text((838, 125), "Inventory / Journal", fill=(70, 53, 38, 255))
    save_image(ui_board, PACKAGE / "01_mother_images" / "ui" / "ui_layout_mother_board.png")
    for name, size in [("panel_frame", (512, 320)), ("hud_panel", (512, 128)), ("dialogue_frame", (1024, 256)), ("button", (256, 96)), ("prompt_marker", (128, 128)), ("journal_tab", (256, 128))]:
        img = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([4, 4, size[0] - 5, size[1] - 5], radius=max(10, min(size) // 10), fill=(246, 236, 207, 245), outline=(126, 87, 49, 255), width=6)
        draw.rounded_rectangle([16, 16, size[0] - 17, size[1] - 17], radius=max(8, min(size) // 12), outline=(181, 139, 91, 160), width=2)
        ui_records.append({"id": name, **save_runtime(img, f"ui/ui_{name}_{size[0]}x{size[1]}.png")})
    manifest["ui"] = ui_records

    fx_records = []
    for fx in ["rain_streaks", "snow_flakes", "leaf_drift", "sunbeam", "mist_patch"]:
        img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        rng = random.Random(500 + len(fx))
        if fx == "rain_streaks":
            for _ in range(36):
                x, y = rng.randint(0, 255), rng.randint(0, 255)
                draw.line([x, y, x - 10, y + 28], fill=(188, 214, 225, 135), width=2)
        elif fx == "snow_flakes":
            for _ in range(44):
                x, y = rng.randint(0, 255), rng.randint(0, 255)
                draw.ellipse([x, y, x + 4, y + 4], fill=(245, 250, 255, 180))
        elif fx == "leaf_drift":
            for _ in range(32):
                x, y = rng.randint(0, 255), rng.randint(0, 255)
                draw.ellipse([x, y, x + 12, y + 7], fill=(190, 105, 55, 150))
        elif fx == "sunbeam":
            draw.polygon([(80, 0), (180, 0), (255, 256), (20, 256)], fill=(255, 230, 150, 70))
        else:
            draw.ellipse([20, 90, 240, 190], fill=(220, 226, 210, 70))
            img = img.filter(ImageFilter.GaussianBlur(18))
        fx_records.append({"id": fx, **save_runtime(img, f"fx/fx_{fx}_256.png")})
    manifest["fx"] = fx_records


def draw_ui_window(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str, fill: tuple[int, int, int, int] = (246, 236, 207, 255)) -> None:
    draw.rounded_rectangle(box, radius=18, fill=fill, outline=(126, 87, 49, 255), width=5)
    draw.rounded_rectangle([box[0] + 14, box[1] + 14, box[2] - 14, box[3] - 14], radius=12, outline=(181, 139, 91, 140), width=2)
    draw.text((box[0] + 24, box[1] + 22), title, fill=(70, 53, 38, 255))


def generate_ui_screen_mothers(manifest: dict) -> None:
    screen_records = []
    output_dir = PACKAGE / "01_mother_images" / "ui" / "screens"
    for screen_id in UI_SCREEN_IDS:
        img = Image.new("RGBA", (1280, 720), (228, 220, 196, 255))
        draw = ImageDraw.Draw(img)
        draw.text((38, 26), f"Greenfield P0 UI screen mother / {screen_id}", fill=(70, 53, 38, 255))
        if screen_id == "hud":
            draw_ui_window(draw, (34, 68, 430, 164), "day / season / weather")
            draw_ui_window(draw, (894, 68, 1246, 164), "money / village state")
            draw_ui_window(draw, (330, 588, 950, 688), "tool belt / selected item")
            for idx in range(8):
                x = 374 + idx * 68
                draw.rounded_rectangle([x, 612, x + 52, 664], radius=8, fill=(230, 214, 176, 255), outline=(112, 83, 54, 255), width=3)
            draw.ellipse([110, 232, 1170, 830], fill=(115, 154, 98, 120), outline=(88, 116, 76, 180), width=5)
        elif screen_id == "inventory":
            draw_ui_window(draw, (78, 78, 1196, 646), "inventory")
            for idx, name in enumerate(["all", "seed", "crop", "food", "key"]):
                y = 142 + idx * 72
                draw.rounded_rectangle([116, y, 238, y + 48], radius=10, fill=(232, 216, 179, 255), outline=(122, 91, 58, 255), width=3)
                draw.text((144, y + 14), name, fill=(70, 53, 38, 255))
            for row in range(4):
                for col in range(6):
                    x = 292 + col * 78
                    y = 142 + row * 78
                    draw.rounded_rectangle([x, y, x + 58, y + 58], radius=8, fill=(238, 225, 190, 255), outline=(132, 99, 66, 255), width=3)
            draw_ui_window(draw, (822, 142, 1140, 510), "selected item")
        elif screen_id == "journal_map":
            draw_ui_window(draw, (64, 76, 412, 652), "journal")
            for idx in range(6):
                y = 150 + idx * 70
                draw.rounded_rectangle([104, y, 372, y + 42], radius=8, fill=(232, 216, 179, 255), outline=(122, 91, 58, 255), width=2)
            draw_ui_window(draw, (462, 76, 1214, 652), "world map / relations")
            for adjacency in WORLD_ADJACENCIES:
                a = WORLD_LAYOUT_GRID[adjacency["from"]]["grid"]
                b = WORLD_LAYOUT_GRID[adjacency["to"]]["grid"]
                ax, ay = 600 + a[0] * 120, 160 + a[1] * 92
                bx, by = 600 + b[0] * 120, 160 + b[1] * 92
                draw.line([ax, ay, bx, by], fill=(126, 93, 58, 180), width=7)
            for rid, tile in WORLD_LAYOUT_GRID.items():
                x, y = 600 + tile["grid"][0] * 120, 160 + tile["grid"][1] * 92
                draw.rounded_rectangle([x - 42, y - 26, x + 42, y + 26], radius=8, fill=(210, 191, 142, 255), outline=(90, 70, 48, 255), width=3)
                draw.text((x - 35, y - 7), rid[:9], fill=(50, 42, 32, 255))
        elif screen_id == "dialogue_gift":
            draw_ui_window(draw, (72, 442, 1208, 664), "dialogue")
            draw_ui_window(draw, (88, 112, 348, 408), "portrait")
            for idx in range(3):
                x = 438 + idx * 228
                draw.rounded_rectangle([x, 188, x + 170, 260], radius=12, fill=(232, 216, 179, 255), outline=(122, 91, 58, 255), width=3)
                draw.text((x + 42, 214), f"gift {idx + 1}", fill=(70, 53, 38, 255))
            draw.text((132, 512), "NPC line, relationship feedback, and gentle choices live here.", fill=(70, 53, 38, 255))
        else:
            draw_ui_window(draw, (420, 82, 860, 638), "pause / settings")
            for idx, name in enumerate(["resume", "journal", "settings", "save", "title"]):
                y = 168 + idx * 78
                draw.rounded_rectangle([488, y, 792, y + 52], radius=12, fill=(232, 216, 179, 255), outline=(122, 91, 58, 255), width=3)
                draw.text((582, y + 17), name, fill=(70, 53, 38, 255))
        opaque = Image.new("RGBA", img.size, (228, 220, 196, 255))
        opaque.alpha_composite(img)
        img = opaque
        path = output_dir / f"greenfield_p0_ui_screen_{screen_id}.png"
        save_image(img, path)
        screen_records.append({"id": screen_id, "production_path": rel(path), "size": [1280, 720], "status": "review_mother"})
    manifest["ui_screens"] = screen_records


def scaled_point(width: int, height: int, point: tuple[float, float]) -> tuple[int, int]:
    return (int(width * point[0]), int(height * point[1]))


def region_points(width: int, height: int, region_id: str) -> dict[str, tuple[int, int]]:
    profile = REGION_LAYOUT_PROFILES[region_id]
    return {key: scaled_point(width, height, value) for key, value in profile["anchors"].items()}


def road_points(points: dict[str, tuple[int, int]], road: dict) -> list[tuple[int, int]]:
    return [points[name] for name in road["points"]]


def add_path_texture_marks(layer: Image.Image, path: list[tuple[int, int]], width: int, style: str, seed: int) -> None:
    rng = random.Random(seed)
    marks = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(marks)
    if style == "stone":
        for start, end in zip(path, path[1:]):
            for step in range(5):
                t = (step + 1) / 6.0
                x = int(start[0] + (end[0] - start[0]) * t + rng.randint(-10, 10))
                y = int(start[1] + (end[1] - start[1]) * t + rng.randint(-7, 7))
                r = max(5, width // 6)
                draw.ellipse([x - r, y - r // 2, x + r, y + r // 2], fill=(143, 133, 111, 150), outline=(91, 82, 67, 100))
    elif style == "field":
        for start, end in zip(path, path[1:]):
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            length = max(1.0, math.hypot(dx, dy))
            nx = -dy / length
            ny = dx / length
            offset = max(7, width // 5)
            for side in [-1, 1]:
                shifted = [
                    (int(start[0] + nx * offset * side), int(start[1] + ny * offset * side)),
                    (int(end[0] + nx * offset * side), int(end[1] + ny * offset * side)),
                ]
                draw.line(shifted, fill=(122, 92, 58, 95), width=max(2, width // 12))
    elif style == "settled":
        for point in path:
            r = max(5, width // 7)
            draw.ellipse([point[0] - r, point[1] - r // 2, point[0] + r, point[1] + r // 2], fill=(222, 202, 153, 125))
    layer.alpha_composite(marks)


def draw_region_roads(layer: Image.Image, region: dict, points: dict[str, tuple[int, int]], palette: dict, layout_mode: bool = False) -> list[dict]:
    width, _height = layer.size
    road_records = []
    profile = REGION_LAYOUT_PROFILES[region["id"]]
    for index, road in enumerate(profile["roads"]):
        path = road_points(points, road)
        road_width = max(18, int(width * road["width"]))
        alpha = 220 if layout_mode else int(road["alpha"])
        color = (168, 139, 92, alpha) if layout_mode else (*palette["path"], alpha)
        style = road["style"]
        if style == "broken":
            for segment_index, segment in enumerate(zip(path, path[1:])):
                if segment_index % 3 == 1:
                    continue
                draw_path(layer, [segment[0], segment[1]], max(12, int(road_width * 0.76)), color)
        else:
            draw_path(layer, path, road_width, color)
        add_path_texture_marks(layer, path, road_width, style, seed=2300 + index * 31 + len(region["id"]))
        road_records.append({
            "id": road["id"],
            "role": road.get("role", "path"),
            "style": style,
            "points": list(road["points"]),
            "pixel_points": [list(point) for point in path],
            "width_px": road_width,
            "width_factor": road["width"],
        })
    return road_records


def zone_records(region: dict, width: int, height: int) -> list[dict]:
    records = []
    for zone in REGION_LAYOUT_PROFILES[region["id"]].get("object_zones", []):
        x1, y1, x2, y2 = zone["rect"]
        records.append({
            "id": zone["id"],
            "role": zone["role"],
            "relation": zone["relation"],
            "rect": [int(width * x1), int(height * y1), int(width * x2), int(height * y2)],
        })
    return records


def farm_plot_rects(width: int, height: int) -> list[tuple[int, int, int, int]]:
    west_x = [0.175, 0.270, 0.365]
    west_y = [0.325, 0.455]
    east_x = [0.565, 0.635]
    east_y = [0.330, 0.455]
    rects = []
    for row_y in west_y:
        for col_x in west_x:
            rects.append((int(width * col_x), int(height * row_y), int(width * (col_x + 0.065)), int(height * (row_y + 0.085))))
    for row_y in east_y:
        for col_x in east_x:
            rects.append((int(width * col_x), int(height * row_y), int(width * (col_x + 0.055)), int(height * (row_y + 0.075))))
    return rects


def generate_region(region: dict, manifest: dict) -> None:
    rid = region["id"]
    width, height = region["canvas"]
    p = SEASON_PALETTES["spring"]
    profile = REGION_LAYOUT_PROFILES[rid]
    pts = region_points(width, height, rid)

    base = texture((width, height), p["grass"], seed=7000 + len(rid))
    terrain = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    behind = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ysort = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    foreground = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    road_records = draw_region_roads(terrain, region, pts, p)
    decorate_region_layers(base, terrain, ysort, foreground, region)

    if "pond" in region["theme"]:
        draw = ImageDraw.Draw(base)
        draw.ellipse([int(width * 0.18), int(height * 0.22), int(width * 0.77), int(height * 0.72)], fill=(*p["water"], 255), outline=(68, 111, 123, 255), width=8)
        water_detail = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(water_detail)
        for offset in [0.30, 0.40, 0.50, 0.60]:
            y = int(height * offset)
            draw.arc([int(width * 0.24), y - 42, int(width * 0.70), y + 46], 8, 172, fill=(170, 210, 210, 85), width=4)
        draw.ellipse([int(width * 0.28), int(height * 0.34), int(width * 0.34), int(height * 0.39)], fill=(90, 133, 82, 180))
        draw.ellipse([int(width * 0.62), int(height * 0.51), int(width * 0.68), int(height * 0.56)], fill=(90, 133, 82, 180))
        base.alpha_composite(water_detail)
        draw_prop(ysort, "dock", int(width * 0.57), int(height * 0.68), 1.2)
    if "farm" in region["theme"]:
        draw = ImageDraw.Draw(terrain)
        for index, (x1, y1, x2, y2) in enumerate(farm_plot_rects(width, height)):
            draw.rounded_rectangle([x1, y1, x2, y2], radius=8, fill=(111, 78, 47, 220), outline=(79, 57, 39, 180), width=3)
            for groove in range(3):
                gy = y1 + int((groove + 1) * (y2 - y1) / 4)
                draw.line([x1 + 10, gy, x2 - 10, gy - 6], fill=(77, 53, 34, 110), width=3)
            if index % 2 == 0:
                draw.ellipse([x1 + 18, y1 + 18, x1 + 36, y1 + 36], fill=(*p["grass2"], 190))
                draw.ellipse([x2 - 34, y1 + 22, x2 - 16, y1 + 42], fill=(*p["grass"], 180))
        draw_house(behind, pts["shed"][0], pts["shed"][1], 0.48, hut=True)
    if "village" in region["theme"]:
        draw_house(behind, pts["house_a"][0], pts["house_a"][1], 0.55)
        draw_house(behind, pts["house_b"][0], pts["house_b"][1], 0.50)
        draw_prop(ysort, "road_sign", pts["road_sign"][0], pts["road_sign"][1], 1.0)
    if "home" in region["theme"]:
        draw_house(behind, pts["house"][0], pts["house"][1], 0.82)
        draw_prop(ysort, "mailbox", pts["mailbox"][0], pts["mailbox"][1], 1.0)
        draw_prop(ysort, "well", pts["well"][0], pts["well"][1], 1.0)
        draw_prop(ysort, "bench", pts["bench"][0], pts["bench"][1], 1.0)
        draw_prop(ysort, "road_sign", pts["road_sign"][0], pts["road_sign"][1], 1.0)
    if "hut" in region["theme"]:
        draw_house(behind, pts["hut"][0], pts["hut"][1], 0.75, hut=True)
        draw_prop(ysort, "storage_crate", pts["woodpile"][0], pts["woodpile"][1], 1.0)
    if "cliff" in region["theme"]:
        draw = ImageDraw.Draw(base)
        draw.polygon([(int(width * 0.12), int(height * 0.58)), (int(width * 0.88), int(height * 0.42)), (width, height), (0, height)], fill=(155, 145, 116, 255), outline=(93, 83, 68, 255))
        cliff_detail = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(cliff_detail)
        for band in range(5):
            y = int(height * (0.62 + band * 0.07))
            draw.line([int(width * 0.10), y, int(width * 0.92), y - int(width * 0.07)], fill=(118, 108, 88, 105), width=5)
        base.alpha_composite(cliff_detail)
    if "mountain" in region["theme"] or "forest" in region["theme"] or "orchard" in region["theme"]:
        for x, y in [pts["nw"], pts["ne"], pts["west"], pts["east"], pts["sw"], pts["se"]]:
            draw_tree(behind if y < height * 0.55 else foreground, x, y, 0.95 if "orchard" not in region["theme"] else 0.72, "spring")

    for x, y in [pts["nw"], pts["ne"], pts["sw"], pts["se"]]:
        draw_soft_ellipse(shadow, (x - 90, y - 28, x + 90, y + 42), (41, 35, 28, 42))

    light_records = []
    for season in SEASONS:
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        draw.rectangle([0, 0, width, height], fill=SEASON_PALETTES[season]["light"])
        if season == "winter":
            for i in range(80):
                rng = random.Random(i + width)
                x, y = rng.randint(0, width - 1), rng.randint(0, height - 1)
                draw.ellipse([x, y, x + 3, y + 3], fill=(245, 250, 255, 120))
        if season == "autumn":
            for i in range(70):
                rng = random.Random(i + height)
                x, y = rng.randint(0, width - 1), rng.randint(0, height - 1)
                draw.ellipse([x, y, x + 9, y + 5], fill=(188, 96, 46, 95))
        light_records.append({"season": season, **save_runtime(overlay, f"regions/{rid}/layers/{rid}_light_weather_overlay_{season}.png")})

    painted = Image.alpha_composite(base, terrain)
    painted = Image.alpha_composite(painted, behind)
    painted = Image.alpha_composite(painted, ysort)
    painted = Image.alpha_composite(painted, shadow)
    painted = Image.alpha_composite(painted, foreground)

    layout = Image.new("RGBA", (width, height), (240, 234, 218, 255))
    layout_draw = ImageDraw.Draw(layout)
    layout_draw.rectangle([8, 8, width - 9, height - 9], outline=(82, 63, 45, 255), width=6)
    layout_zones = zone_records(region, width, height)
    zone_overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    zone_draw = ImageDraw.Draw(zone_overlay)
    for zone in layout_zones:
        rect = zone["rect"]
        zone_draw.rounded_rectangle(rect, radius=12, fill=(112, 143, 118, 88), outline=(65, 87, 70, 210), width=4)
    layout.alpha_composite(zone_overlay)
    draw_region_roads(layout, region, pts, p, layout_mode=True)
    for zone in layout_zones:
        rect = zone["rect"]
        layout_draw.rounded_rectangle(rect, radius=12, outline=(54, 70, 58, 255), width=2)
        layout_draw.text((rect[0] + 10, rect[1] + 10), zone["id"], fill=(42, 55, 44, 255))
    for label, pos in pts.items():
        if label in {"north", "south", "east", "west", "center"}:
            layout_draw.ellipse([pos[0] - 12, pos[1] - 12, pos[0] + 12, pos[1] + 12], fill=(132, 82, 64, 255))
            layout_draw.text((pos[0] + 15, pos[1] - 8), label, fill=(72, 56, 42, 255))
    layout_draw.text((35, 34), f"{region['display']} layout mother: {profile['road_motif']}", fill=(72, 56, 42, 255))

    mother_dir = PACKAGE / "01_mother_images" / "regions" / rid
    save_image(layout, mother_dir / f"{rid}_layout_mother.png")
    save_image(painted, mother_dir / f"{rid}_painted_source.png")

    layer_records = {
        "base_ground": save_runtime(base, f"regions/{rid}/layers/{rid}_base_ground.png"),
        "terrain_details": save_runtime(terrain, f"regions/{rid}/layers/{rid}_terrain_details.png"),
        "behind_player_structures": save_runtime(behind, f"regions/{rid}/layers/{rid}_behind_player_structures.png"),
        "ysort_props_structures": save_runtime(ysort, f"regions/{rid}/layers/{rid}_ysort_props_structures.png"),
        "foreground_occlusion": save_runtime(foreground, f"regions/{rid}/layers/{rid}_foreground_occlusion.png"),
        "shadow_overlay": save_runtime(shadow, f"regions/{rid}/layers/{rid}_shadow_overlay.png"),
        "light_weather_overlays": light_records,
    }
    region_manifest = {
        "region_id": rid,
        "display_name": region["display"],
        "canvas_size": [width, height],
        "status": "usable",
        "launch_quality_approved": False,
        "human_visual_approval_required": True,
        "layout_mother": str((mother_dir / f"{rid}_layout_mother.png").relative_to(ROOT)).replace("\\", "/"),
        "painted_source": str((mother_dir / f"{rid}_painted_source.png").relative_to(ROOT)).replace("\\", "/"),
        "features": region["features"],
        "layers": layer_records,
        "anchors": [{"id": key, "position": list(value)} for key, value in pts.items()],
        "layout_profile": {
            "road_signature": profile["road_signature"],
            "road_motif": profile["road_motif"],
            "composition_focal_point": list(profile["composition_focal_point"]),
            "road_paths": road_records,
            "object_zones": zone_records(region, width, height),
            "seam_connectors": {key: list(pts[key]) for key in ["north", "south", "east", "west"]},
        },
        "season_variant_mapping": {season: f"{rid}_light_weather_overlay_{season}.png" for season in SEASONS},
    }
    manifest_dir = PACKAGE / "01_mother_images" / "regions" / rid
    (manifest_dir / f"{rid}_manifest.json").write_text(json.dumps(region_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest.setdefault("regions", []).append(region_manifest)


def make_contact_sheet(images: list[tuple[str, Path]], path: Path, thumb: tuple[int, int] = (180, 140), cols: int = 5) -> None:
    rows = math.ceil(len(images) / cols)
    sheet = Image.new("RGBA", (cols * (thumb[0] + 24), rows * (thumb[1] + 48) + 28), (242, 236, 218, 255))
    draw = ImageDraw.Draw(sheet)
    for idx, (label, source) in enumerate(images):
        img = Image.open(source).convert("RGBA")
        img.thumbnail(thumb)
        x = (idx % cols) * (thumb[0] + 24) + 12
        y = (idx // cols) * (thumb[1] + 48) + 16
        sheet.alpha_composite(img, (x, y))
        draw.text((x, y + thumb[1] + 8), label[:24], fill=(72, 56, 42, 255))
    save_image(sheet, path)


def region_manifest_by_id(manifest: dict) -> dict[str, dict]:
    return {region["region_id"]: region for region in manifest["regions"]}


def world_tile_center(grid: tuple[int, int], cell: tuple[int, int], margin: tuple[int, int]) -> tuple[int, int]:
    return (margin[0] + grid[0] * cell[0] + cell[0] // 2, margin[1] + grid[1] * cell[1] + cell[1] // 2)


def build_world_layout_records(manifest: dict) -> dict:
    regions_by_id = region_manifest_by_id(manifest)
    tiles = []
    sockets = []
    for region_id, tile in WORLD_LAYOUT_GRID.items():
        region = regions_by_id[region_id]
        tiles.append({
            "region_id": region_id,
            "grid": list(tile["grid"]),
            "world_role": tile["world_role"],
            "canvas_size": region["canvas_size"],
            "painted_source": region["painted_source"],
        })
    for adjacency in WORLD_ADJACENCIES:
        for side_key, edge_key, peer_key, peer_edge_key in [
            ("from", "from_edge", "to", "to_edge"),
            ("to", "to_edge", "from", "from_edge"),
        ]:
            region_id = adjacency[side_key]
            edge = adjacency[edge_key]
            region = regions_by_id[region_id]
            connector = region["layout_profile"]["seam_connectors"][edge]
            sockets.append({
                "id": f"{adjacency['id']}__{region_id}_{edge}",
                "connection_id": adjacency["id"],
                "region_id": region_id,
                "edge": edge,
                "grid": list(WORLD_LAYOUT_GRID[region_id]["grid"]),
                "connector_px": connector,
                "connects_to_region": adjacency[peer_key],
                "connects_to_edge": adjacency[peer_edge_key],
                "route_role": adjacency["route_role"],
                "traversal": adjacency["traversal"],
            })
    return {
        "status": "review_candidate",
        "grid_size": [4, 4],
        "tile_size_px": [360, 250],
        "tiles": tiles,
        "adjacencies": WORLD_ADJACENCIES,
        "sockets": sockets,
        "route_rule_notes": [
            "Adjacency sockets are structural map-assembly metadata, not final scene transitions.",
            "Road role rules are the first contract for NPC path preferences, collision width, and cart support.",
            "Generated review scenes remain inspection artifacts until human visual approval.",
        ],
    }


def generate_world_layout_preview(manifest: dict) -> dict:
    world_layout = build_world_layout_records(manifest)
    regions_by_id = region_manifest_by_id(manifest)
    cell = (360, 250)
    margin = (100, 100)
    width = margin[0] * 2 + world_layout["grid_size"][0] * cell[0]
    height = margin[1] * 2 + world_layout["grid_size"][1] * cell[1]
    preview = Image.new("RGBA", (width, height), (238, 231, 211, 255))
    draw = ImageDraw.Draw(preview)
    draw.text((40, 30), "Greenfield P0 world layout sockets", fill=(58, 48, 36, 255))

    centers = {
        region_id: world_tile_center(tuple(tile["grid"]), cell, margin)
        for region_id, tile in WORLD_LAYOUT_GRID.items()
    }
    connection_overlay = Image.new("RGBA", preview.size, (0, 0, 0, 0))
    connection_draw = ImageDraw.Draw(connection_overlay)
    for adjacency in WORLD_ADJACENCIES:
        start = centers[adjacency["from"]]
        end = centers[adjacency["to"]]
        connection_draw.line([start, end], fill=(126, 93, 58, 180), width=9)
        mid = ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2)
        connection_draw.ellipse([mid[0] - 9, mid[1] - 9, mid[0] + 9, mid[1] + 9], fill=(82, 122, 91, 220))
    preview.alpha_composite(connection_overlay)

    for tile in world_layout["tiles"]:
        region_id = tile["region_id"]
        center = centers[region_id]
        box = [center[0] - 142, center[1] - 88, center[0] + 142, center[1] + 88]
        draw.rounded_rectangle([box[0] - 10, box[1] - 10, box[2] + 10, box[3] + 34], radius=8, fill=(247, 242, 224, 255), outline=(94, 77, 55, 255), width=3)
        image = Image.open(ROOT / regions_by_id[region_id]["painted_source"]).convert("RGBA")
        image.thumbnail((284, 176))
        preview.alpha_composite(image, (center[0] - image.width // 2, center[1] - image.height // 2))
        draw.text((box[0], box[3] + 10), f"{region_id} / {tile['world_role']}", fill=(58, 48, 36, 255))

    preview_path = PACKAGE / "03_contact_sheets" / "greenfield_p0_world_layout_socket_preview.png"
    save_image(preview, preview_path)
    world_layout["preview"] = str(preview_path.relative_to(ROOT)).replace("\\", "/")
    manifest["world_layout"] = world_layout
    manifest["road_role_rules"] = ROAD_ROLE_RULES
    return world_layout


def generate_contact_sheets(manifest: dict) -> None:
    contact_sheets = {}
    region_images = []
    for region in manifest["regions"]:
        region_images.append((region["region_id"], ROOT / region["painted_source"]))
    path = PACKAGE / "03_contact_sheets" / "greenfield_p0_region_painted_sources_contact_sheet.png"
    make_contact_sheet(region_images, path, thumb=(330, 230), cols=2)
    contact_sheets["region_painted_sources"] = rel(path)

    tile_images = []
    for record in manifest["tiles"]["records"][:32]:
        tile_images.append((Path(record["production_path"]).stem, ROOT / record["production_path"]))
    path = PACKAGE / "03_contact_sheets" / "greenfield_p0_season_tiles_contact_sheet.png"
    make_contact_sheet(tile_images, path, thumb=(64, 64), cols=8)
    contact_sheets["season_tiles"] = rel(path)

    prop_images = [(record["id"], ROOT / record["production_path"]) for record in manifest["props"]]
    path = PACKAGE / "03_contact_sheets" / "greenfield_p0_props_contact_sheet.png"
    make_contact_sheet(prop_images, path, thumb=(128, 128), cols=6)
    contact_sheets["props"] = rel(path)

    item_images = [(record["id"], ROOT / record["production_path"]) for record in manifest["items"]]
    path = PACKAGE / "03_contact_sheets" / "greenfield_p0_item_icons_contact_sheet.png"
    make_contact_sheet(item_images, path, thumb=(64, 64), cols=10)
    contact_sheets["item_icons"] = rel(path)

    crop_images = [
        (f"{record['crop_id']}_{record['season']}_{record['stage']}", ROOT / record["production_path"])
        for record in manifest["crops"]
    ]
    path = PACKAGE / "03_contact_sheets" / "greenfield_p0_crop_stages_contact_sheet.png"
    make_contact_sheet(crop_images, path, thumb=(64, 64), cols=12)
    contact_sheets["crop_stages"] = rel(path)

    player_images = [
        (f"{record['action']}_{record['direction']}", ROOT / record["production_path"])
        for record in manifest["characters"]["player_records"]
    ]
    path = PACKAGE / "03_contact_sheets" / "greenfield_p0_player_motion_contact_sheet.png"
    make_contact_sheet(player_images, path, thumb=(160, 80), cols=8)
    contact_sheets["player_motion"] = rel(path)

    npc_motion_images = [
        (f"{record['id']}_{record.get('action', record.get('portrait'))}_{record.get('direction', '')}", ROOT / record["production_path"])
        for record in manifest["characters"]["npc_records"]
        if "action" in record
    ]
    path = PACKAGE / "03_contact_sheets" / "greenfield_p0_npc_motion_contact_sheet.png"
    make_contact_sheet(npc_motion_images, path, thumb=(160, 80), cols=8)
    contact_sheets["npc_motion"] = rel(path)

    npc_portrait_images = [
        (f"{record['id']}_{record['portrait']}", ROOT / record["production_path"])
        for record in manifest["characters"]["npc_records"]
        if "portrait" in record
    ]
    path = PACKAGE / "03_contact_sheets" / "greenfield_p0_npc_portraits_contact_sheet.png"
    make_contact_sheet(npc_portrait_images, path, thumb=(128, 128), cols=6)
    contact_sheets["npc_portraits"] = rel(path)

    ui_piece_images = [(record["id"], ROOT / record["production_path"]) for record in manifest["ui"]]
    path = PACKAGE / "03_contact_sheets" / "greenfield_p0_ui_pieces_contact_sheet.png"
    make_contact_sheet(ui_piece_images, path, thumb=(180, 100), cols=3)
    contact_sheets["ui_pieces"] = rel(path)

    ui_screen_images = [(record["id"], ROOT / record["production_path"]) for record in manifest["ui_screens"]]
    path = PACKAGE / "03_contact_sheets" / "greenfield_p0_ui_screens_contact_sheet.png"
    make_contact_sheet(ui_screen_images, path, thumb=(300, 170), cols=2)
    contact_sheets["ui_screens"] = rel(path)

    region_composites = []
    for region in manifest["regions"]:
        rid = region["region_id"]
        composite = Image.new("RGBA", tuple(region["canvas_size"]), (0, 0, 0, 0))
        for layer in REGION_LAYERS:
            composite.alpha_composite(Image.open(ROOT / region["layers"][layer]["production_path"]).convert("RGBA"))
        region_preview_path = PACKAGE / "03_contact_sheets" / "regions" / f"{rid}_runtime_composite_preview.png"
        save_image(composite, region_preview_path)

        layer_images = [(layer, ROOT / region["layers"][layer]["production_path"]) for layer in REGION_LAYERS]
        layer_images.extend(
            (f"light_{record['season']}", ROOT / record["production_path"])
            for record in region["layers"]["light_weather_overlays"]
        )
        layer_sheet_path = PACKAGE / "03_contact_sheets" / "regions" / f"{rid}_runtime_layer_contact_sheet.png"
        make_contact_sheet(layer_images, layer_sheet_path, thumb=(260, 180), cols=2)
        region["review_artifacts"] = {
            "runtime_composite_preview": rel(region_preview_path),
            "runtime_layer_contact_sheet": rel(layer_sheet_path),
        }
        region_composites.append((rid, region_preview_path))
        manifest_path = PACKAGE / "01_mother_images" / "regions" / rid / f"{rid}_manifest.json"
        manifest_path.write_text(json.dumps(region, ensure_ascii=False, indent=2), encoding="utf-8")

    path = PACKAGE / "03_contact_sheets" / "greenfield_p0_region_runtime_composites_contact_sheet.png"
    make_contact_sheet(region_composites, path, thumb=(330, 230), cols=2)
    contact_sheets["region_runtime_composites"] = rel(path)
    manifest["contact_sheets"] = contact_sheets


def generate_runtime_import_map(manifest: dict) -> dict:
    entries = []
    prod_root = PACKAGE / "02_runtime_exports"
    for prod_path in sorted(prod_root.rglob("*.png")):
        relative = prod_path.relative_to(prod_root)
        runtime_path = RUNTIME / relative
        entries.append({
            "id": prod_path.stem,
            "production_path": rel(prod_path),
            "runtime_path": "res://" + rel(runtime_path),
            "exists_in_runtime": runtime_path.exists(),
        })
    import_map = {
        "package_id": manifest["package_id"],
        "runtime_root": "res://" + rel(RUNTIME),
        "entries": entries,
    }
    path = PACKAGE / "runtime_import_map.json"
    path.write_text(json.dumps(import_map, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"path": rel(path), "entry_count": len(entries)}


def collect_file_catalog(root: Path, root_id: str) -> list[dict]:
    entries = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        entry = {
            "root": root_id,
            "path": rel(path),
            "suffix": path.suffix.lower(),
            "bytes": path.stat().st_size,
        }
        if path.suffix.lower() == ".png":
            with Image.open(path) as image:
                entry["image_size"] = list(image.size)
                entry["mode"] = image.mode
        entries.append(entry)
    return entries


def generate_asset_catalog(manifest: dict) -> dict:
    package_entries = collect_file_catalog(PACKAGE, "production_package")
    runtime_entries = collect_file_catalog(RUNTIME, "godot_runtime_copy")
    catalog = {
        "package_id": manifest["package_id"],
        "summary": {
            "package_file_count": len(package_entries),
            "package_png_count": sum(1 for entry in package_entries if entry["suffix"] == ".png"),
            "runtime_file_count": len(runtime_entries),
            "runtime_png_count": sum(1 for entry in runtime_entries if entry["suffix"] == ".png"),
            "region_count": len(manifest["regions"]),
            "ui_screen_count": len(manifest.get("ui_screens", [])),
            "contact_sheet_count": len(manifest.get("contact_sheets", {})),
        },
        "entries": package_entries + runtime_entries,
    }
    path = PACKAGE / "asset_catalog.json"
    path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"path": rel(path), "summary": catalog["summary"]}


def generate_delivery_report(manifest: dict, catalog_record: dict, import_map_record: dict) -> dict:
    lines = [
        "# Greenfield P0 Art Asset Package Delivery",
        "",
        "Status: complete_review_candidate",
        "",
        "## Coverage",
        f"- Regions: {len(manifest['regions'])}",
        f"- Region runtime layer sets: {len(manifest['regions'])}",
        f"- World adjacencies: {len(manifest['world_layout']['adjacencies'])}",
        f"- World sockets: {len(manifest['world_layout']['sockets'])}",
        f"- Protagonist actions: {len(PROTAGONIST_ACTIONS)} x {len(DIRECTIONS)} directions",
        f"- P0 NPCs: {len(NPC_IDS)} with 8-direction idle/walk and {len(PORTRAITS)} portraits each",
        f"- UI screen mothers: {len(manifest.get('ui_screens', []))}",
        f"- Contact sheets: {len(manifest.get('contact_sheets', {}))}",
        f"- Runtime import entries: {import_map_record['entry_count']}",
        "",
        "## Boundaries",
        "- This package is complete as a P0 review asset package.",
        "- It is not launch-quality-approved and still requires human visual review.",
        "- Generated review scenes are inspection artifacts, not active runtime replacements.",
        "",
        "## Primary Review Entry Points",
        f"- {manifest['world_layout']['preview']}",
        "- scenes/dev/greenfield_p0_asset_gallery.tscn",
        "- scenes/dev/greenfield_p0_reviews/greenfield_p0_region_review_all.tscn",
        "- scenes/dev/greenfield_p0_reviews/greenfield_p0_world_layout_review.tscn",
    ]
    path = PACKAGE / "GREENFIELD_P0_ASSET_PACKAGE_DELIVERY.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"path": rel(path), "status": "complete_review_candidate", "catalog": catalog_record["path"], "runtime_import_map": import_map_record["path"]}


def generate_delivery_artifacts(manifest: dict) -> None:
    import_map_record = generate_runtime_import_map(manifest)
    catalog_record = generate_asset_catalog(manifest)
    report_record = generate_delivery_report(manifest, catalog_record, import_map_record)
    manifest["package_completion"] = {
        "status": "complete_review_candidate",
        "scope": "greenfield_p0_art_asset_package",
        "asset_catalog": catalog_record,
        "runtime_import_map": import_map_record,
        "delivery_report": report_record,
        "human_visual_approval_required": True,
        "launch_quality_approved": False,
    }


def generate_gallery_scene(manifest: dict) -> None:
    resources: list[tuple[str, str]] = []

    def add_resource(res_path: str) -> str:
        res_id = f"tex_{len(resources) + 1}"
        resources.append((res_id, res_path))
        return res_id

    player_tex = add_resource("res://assets/art/greenfield_p0/characters/player/chr_player_base_idle_down_128.png")
    tile_tex = add_resource("res://assets/art/greenfield_p0/tiles/spring/tile_grass_a_spring_64.png")
    ui_tex = add_resource("res://assets/art/greenfield_p0/ui/ui_panel_frame_512x320.png")
    prop_tex = add_resource("res://assets/art/greenfield_p0/props/prop_house_player_256.png")
    region_tex_ids = []
    for region in REGIONS:
        region_tex_ids.append((region["id"], add_resource(f"res://assets/art/greenfield_p0/regions/{region['id']}/layers/{region['id']}_base_ground.png")))

    lines = ["[gd_scene load_steps=%d format=3]" % (len(resources) + 1), ""]
    for res_id, path in resources:
        lines.append(f'[ext_resource type="Texture2D" path="{path}" id="{res_id}"]')
    lines.extend([
        "",
        '[node name="GreenfieldP0AssetGallery" type="Node2D"]',
        'metadata/package_id = "greenfield_p0_base_asset_pack_v001"',
        'metadata/status = "usable"',
        'metadata/launch_quality_approved = false',
        "",
        '[node name="CharacterSamples" type="Node2D" parent="."]',
        "",
        '[node name="PlayerIdleDown" type="Sprite2D" parent="CharacterSamples"]',
        "position = Vector2(120, 120)",
        f"texture = ExtResource(\"{player_tex}\")",
        "",
        '[node name="SeasonTileSamples" type="Node2D" parent="."]',
        "",
        '[node name="SpringGrassTile" type="Sprite2D" parent="SeasonTileSamples"]',
        "position = Vector2(280, 120)",
        f"texture = ExtResource(\"{tile_tex}\")",
        "",
        '[node name="UISamples" type="Node2D" parent="."]',
        "",
        '[node name="PanelFrame" type="Sprite2D" parent="UISamples"]',
        "position = Vector2(520, 140)",
        "scale = Vector2(0.35, 0.35)",
        f"texture = ExtResource(\"{ui_tex}\")",
        "",
        '[node name="PropSamples" type="Node2D" parent="."]',
        "",
        '[node name="HouseProp" type="Sprite2D" parent="PropSamples"]',
        "position = Vector2(760, 150)",
        "scale = Vector2(0.5, 0.5)",
        f"texture = ExtResource(\"{prop_tex}\")",
        "",
        '[node name="RegionSamples" type="Node2D" parent="."]',
        "",
    ])
    for idx, (rid, tex_id) in enumerate(region_tex_ids):
        x = 170 + (idx % 5) * 250
        y = 360 + (idx // 5) * 210
        lines.extend([
            f'[node name="{rid}" type="Node2D" parent="RegionSamples"]',
            f"position = Vector2({x}, {y})",
            "",
            f'[node name="BaseGround" type="Sprite2D" parent="RegionSamples/{rid}"]',
            "scale = Vector2(0.12, 0.12)",
            f"texture = ExtResource(\"{tex_id}\")",
            "",
        ])
    ensure_parent(SCENE_PATH)
    SCENE_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    reset_dir(PACKAGE)
    reset_dir(RUNTIME)
    SCENE_PATH.parent.mkdir(parents=True, exist_ok=True)

    manifest: dict = {
        "package_id": "greenfield_p0_base_asset_pack_v001",
        "asset_type": "base_asset_pack",
        "status": "usable",
        "source_first": True,
        "runtime_replacement": False,
        "launch_quality_approved": False,
        "human_visual_approval_required": True,
        "seasons": SEASONS,
        "directions": DIRECTIONS,
        "old_home_area_sources_allowed": False,
        "source_mothers": {},
        "validation": [
            "python tools/validate_greenfield_p0_art_pack.py",
            "D:/Godot/Godot_v4.6.1-stable_win64_console.exe --headless --path . --script tools/validate_greenfield_p0_gallery.gd",
        ],
    }
    manifest["source_mothers"]["style"] = generate_style_mother()
    generate_tiles(manifest)
    generate_characters(manifest)
    generate_items_and_crops(manifest)
    generate_props_ui_fx(manifest)
    generate_ui_screen_mothers(manifest)
    for region in REGIONS:
        generate_region(region, manifest)
    generate_world_layout_preview(manifest)
    generate_contact_sheets(manifest)
    generate_gallery_scene(manifest)
    (PACKAGE / "workflow_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    generate_delivery_artifacts(manifest)
    (PACKAGE / "workflow_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print("OK: generated greenfield P0 art package")


if __name__ == "__main__":
    main()
