# OutdoorWorld Seamless Art Master Blueprint

This is the global spatial contract for the current seamless 2D `OutdoorWorld`.
It is a structure guide, not final art and not runtime replacement.

## Runtime Coordinate Basis

- Active scene: `res://game/scenes/world/OutdoorWorld.tscn`
- Runtime source: `game/scenes/world/OutdoorWorld.gd`
- Generated region runtime size: `320x240`
- Generated region source canvas reference: `1800x1200`
- Runtime texture scale: `0.18`
- World bounds: `{'min_x': -40, 'min_y': -316, 'max_x': 1720, 'max_y': 564, 'width': 1760, 'height': 880}`

## Region Layout

| Region | Runtime bounds | Priority | Source status |
| --- | --- | --- | --- |
| `player_yard` | `[-40, -96, 372, 408]` | P0 | separate_home_area_chain |
| `forest_edge` | `[332, -108, 340, 320]` | P1 | needs_future_world2d_source |
| `village` | `[720, -12, 320, 240]` | P0 | layout_draft_only_not_final_painted_source |
| `back_farm` | `[0, 324, 320, 240]` | P2 | defer_until_player_verb_lock |
| `orchard` | `[380, 324, 320, 240]` | P2 | defer_until_daily_loop |
| `pond` | `[720, 324, 320, 240]` | P2 | defer_until_daily_activity_loop |
| `mountain_path` | `[720, -316, 320, 240]` | P2 | defer_until_exploration_escalation_loop |
| `mountain_hut` | `[1060, -12, 320, 240]` | P3 | defer_until_mountain_route_lock |
| `mountain` | `[1060, -316, 320, 240]` | P3 | defer_until_route_lock |
| `cliff_view` | `[1400, -316, 320, 240]` | P3 | defer_until_discovery_location_lock |

## Seam Connections

| Connection | Regions | Role |
| --- | --- | --- |
| `yard_to_forest_edge` | `player_yard` -> `forest_edge` | current_first_week_forest_route |
| `yard_to_village` | `player_yard` -> `village` | current_village_entry_route |
| `yard_to_back_farm` | `player_yard` -> `back_farm` | future_farm_work_route |
| `back_farm_to_orchard` | `back_farm` -> `orchard` | future_workland_lane |
| `orchard_to_pond` | `orchard` -> `pond` | future_daily_activity_lane |
| `village_to_pond` | `village` -> `pond` | future_south_village_exit |
| `village_to_mountain_path` | `village` -> `mountain_path` | future_north_village_exit |
| `village_to_mountain_hut` | `village` -> `mountain_hut` | future_east_village_extension |
| `mountain_path_to_mountain` | `mountain_path` -> `mountain` | future_exploration_lane |
| `mountain_to_cliff_view` | `mountain` -> `cliff_view` | future_discovery_overlook_lane |
| `mountain_to_hut` | `mountain` -> `mountain_hut` | future_hut_return_lane |

## Art Direction Rules

- Treat the world as one continuous countryside map before approving any single region.
- Match ground hue, road width, road material, lighting direction, and perspective at every seam.
- Region chunks may be produced one at a time, but their edges must respect this master blueprint.
- Use blueprint geometry as layout guidance, not pixel-perfect brush tracing.
- Do not split layers from the current Village structure draft.
