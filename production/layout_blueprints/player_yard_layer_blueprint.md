# PlayerYard Layer Blueprint

Source scene: `res://game/scenes/world/PlayerYard.tscn`

Coordinate space: Godot scene units.

Export rule: `full_canvas_shared_origin`. Every runtime layer keeps the same canvas, origin, scale, perspective, and rotation. Transparent layers are derived from one `scene_mother` composition, not regenerated independently.

## Layers

| Layer | Purpose |
| --- | --- |
| `scene_mother` | Full painted composition reference. |
| `base` | Ground, paths, farm soil, and resource staging surface. |
| `foreground_occlusion` | Props that may visually stand in front of NPCs or the player. |
| `interaction_hotspots` | Interaction gates and route/debug zones. |
| `npc_standing_points` | Schedule-driven NPC anchor overlay. |

## Object Zones

| Zone | Rect | Layer |
| --- | --- | --- |
| `home_mailbox` | `32,42,36,36` | `foreground_occlusion` |
| `notice_board` | `96,42,56,34` | `foreground_occlusion` |
| `farm_garden` | `20,150,138,92` | `base` |
| `repair_well` | `226,136,58,58` | `foreground_occlusion` |
| `repair_bench` | `198,204,58,28` | `foreground_occlusion` |
| `village_sign` | `270,90,34,38` | `foreground_occlusion` |
| `forest_gate` | `312,116,44,38` | `interaction_hotspots` |
| `resource_staging` | `-64,150,98,92` | `base` |

## NPC Standing Points

| NPC | Time | Point | Anchor |
| --- | --- | --- | --- |
| `aoi` | `late_morning` | `116,86` | `notice_board_front_left` |
| `aoi` | `afternoon` | `208,196` | `farm_garden_north_east` |
| `aoi` | `evening` | `48,96` | `mailbox_path_exit` |
| `gen` | `late_morning` | `174,224` | `repair_bench_work_left` |
| `gen` | `evening` | `212,116` | `repair_yard_tool_path` |
| `mika` | `late_morning` | `188,84` | `notice_board_front_right` |
| `hana` | `morning` | `170,224` | `sunny_path_bench_left` |
| `hana` | `late_morning` | `150,146` | `yard_center_clear_north_edge` |
| `hana` | `afternoon` | `150,146` | `yard_center_clear_north_edge` |
| `hana` | `evening` | `126,118` | `notice_path_clear` |

## Production Notes

- Treat these rectangles as layout and registration guidance, not pixel-perfect painting constraints.
- Keep NPC points outside object zones so exported prop layers do not cover idle character feet.
- Keep the `farm_garden`, `repair_bench`, `npc_standing_points`, `full_canvas_shared_origin`, and `foreground_occlusion` labels intact for validation.
