# Region_HomeArea / Region_HomeBackFarm Art Asset Spec v0.1

## Global Rules

- Style target: cozy hand-painted oblique 2D exploration map, low-saturation summer rural lighting.
- No characters baked into environment assets. Player, NPCs, animals, and movable props are separate runtime actors.
- Export format: PNG, RGBA, straight alpha, sRGB, 1x pixel scale, no premultiplied dark fringe.
- Source files: keep layered PSD/KRA/Clip source beside exports; every export layer must be reproducible from source.
- Coordinate system: Godot pixel coordinates, top-left region origin `(0, 0)`.
- Region canvases:
  - `Region_HomeArea`: `6144 x 4096`
  - `Region_HomeBackFarm`: `4096 x 3072`
- Ground/path/large shadows may be delivered either as cropped PNGs with explicit `origin_x, origin_y`, or as full-region transparent source-space PNGs. Cropped PNG is preferred after layout stabilizes.
- Props and structures use foot/base anchor: local anchor at the visual ground contact center, usually `(width / 2, height)`.
- Foreground occluders must be tight transparent cutouts around visible pixels. Do not export broad rectangular masks that cover empty alpha over the player.
- Contact shadows for static props can be baked only if the prop never moves. Player/NPC shadows stay separate runtime sprites.
- Naming: lowercase snake case, region prefix, semantic layer, asset id, version. Example: `region_home_area_path_south_stone_v001.png`.

## Runtime Layer Contract

- `TileMapLayer_Ground`: grass, soil, base terrain. z target `-120`.
- `TileMapLayer_Path`: road, stone path, steps. z target `-110`.
- `TileMapLayer_Detail`: pebbles, tiny flowers, low ground decals that never occlude feet. z target `-95`.
- `YSortWorld`: houses, trees, props, interactables, player, NPCs. Split tall objects into base/collider part and canopy/occluder part when needed.
- `ForegroundStatic`: front-only cutouts that must always draw over the player. z target `80`.
- `LightAndWeather`: semi-transparent light/shadow/weather overlays. z target `95`; no opaque pixels.

## Region_HomeArea Required Assets

Canvas: `6144 x 4096`.

| Current node / paint id | Export name | Type | Cropped origin | Approx size | Anchor |
| --- | --- | --- | --- | --- | --- |
| `grass_north` | `region_home_area_ground_grass_north_v001.png` | ground patch | `(0, 0)` | `6144 x 1560` | top-left |
| `grass_home_yard` | `region_home_area_ground_grass_yard_v001.png` | ground patch | `(1440, 1320)` | `3580 x 1800` | top-left |
| `grass_south` | `region_home_area_ground_grass_south_v001.png` | ground patch | `(0, 2480)` | `6144 x 1616` | top-left |
| `west_garden_soil` | `region_home_area_ground_west_garden_soil_v001.png` | ground patch | `(520, 1520)` | `1610 x 1300` | top-left |
| `north_village_road` | `region_home_area_path_north_village_road_v001.png` | path patch | `(520, 560)` | `5100 x 1000` | top-left |
| `home_front_yard_path` | `region_home_area_path_front_yard_v001.png` | path patch | `(2060, 1600)` | `2200 x 980` | top-left |
| `south_stone_path` | `region_home_area_path_south_stone_v001.png` | path patch | `(2450, 2460)` | `1870 x 1360` | top-left |
| `west_garden_path` | `region_home_area_path_west_garden_v001.png` | path patch | `(520, 1560)` | `1780 x 1300` | top-left |
| `CloudHouse` | `region_home_area_structure_cloud_house_back_v001.png` | y-sort structure | cropped tight | target width `1500-1800` | foot/base center |
| `CloudHouse` roof/eaves | `region_home_area_structure_cloud_house_roof_occluder_v001.png` | foreground/Y-sort occluder | cropped tight | match house width | top-left or documented pivot |
| `LeftTree` | `region_home_area_tree_left_trunk_v001.png` | prop body | cropped tight | target height `480-620` | trunk foot center |
| `LeftTree` canopy | `region_home_area_tree_left_canopy_occluder_v001.png` | occluder | cropped tight | target width `700-950` | top-left documented |
| `RightTree` | `region_home_area_tree_right_trunk_v001.png` | prop body | cropped tight | target height `560-760` | trunk foot center |
| `RightTree` canopy | `region_home_area_tree_right_canopy_occluder_v001.png` | occluder | cropped tight | target width `850-1150` | top-left documented |
| `Mailbox` | `region_home_area_prop_mailbox_v001.png` | prop | cropped tight | target height `120-170` | foot center |
| `Well` | `region_home_area_prop_well_v001.png` | prop/interactable | cropped tight | target width `220-320` | base center |
| `Bench` | `region_home_area_prop_bench_v001.png` | prop/interactable | cropped tight | target width `300-420` | front-leg center |
| `RoadSign` | `region_home_area_prop_road_sign_v001.png` | prop/interactable | cropped tight | target height `180-260` | post foot center |
| `CatBed` | `region_home_area_prop_cat_bed_v001.png` | prop | cropped tight | target width `160-240` | base center |
| `FrontGrassLeft` | `region_home_area_foreground_front_grass_left_v001.png` | foreground occluder | `(0, 3200)` | max `960 x 896` | top-left |
| `FrontFlowersRight` | `region_home_area_foreground_front_flowers_right_v001.png` | foreground occluder | `(5210, 3080)` | max `934 x 1016` | top-left |
| `DappledLight` | `region_home_area_fx_dappled_light_v001.png` | light overlay | `(700, 840)` | max `1780 x 870` | top-left |
| `WindLeavesGuide` | `region_home_area_fx_wind_leaves_top_v001.png` | animated foliage overlay | `(0, 0)` | max `1720 x 680` | top-left |

## Region_HomeBackFarm Required Assets

Canvas: `4096 x 3072`.

| Current node / paint id | Export name | Type | Cropped origin | Approx size | Anchor |
| --- | --- | --- | --- | --- | --- |
| `back_slope_grass` | `region_home_back_farm_ground_back_slope_grass_v001.png` | ground patch | `(0, 0)` | `4096 x 1120` | top-left |
| `farm_soil_block` | `region_home_back_farm_ground_farm_soil_block_v001.png` | ground patch | `(760, 760)` | `2600 x 1600` | top-left |
| `lower_grass_edge` | `region_home_back_farm_ground_lower_grass_edge_v001.png` | ground patch | `(0, 2120)` | `4096 x 952` | top-left |
| `home_return_path` | `region_home_back_farm_path_home_return_v001.png` | path patch | `(1680, 2560)` | `660 x 512` | top-left |
| `farm_main_lane` | `region_home_back_farm_path_main_lane_v001.png` | path patch | `(1120, 920)` | `1460 x 1460` | top-left |
| `cross_lane` | `region_home_back_farm_path_cross_lane_v001.png` | path patch | `(720, 1400)` | `2600 x 440` | top-left |
| `CropRows` | `region_home_back_farm_crop_rows_base_v001.png` | ground/detail | `(900, 800)` | max `2300 x 1400` | top-left |
| `CropRows` foreground | `region_home_back_farm_crop_rows_front_occluder_v001.png` | foreground occluder | `(720, 2400)` | max `2650 x 672` | top-left |
| `ToolShed` | `region_home_back_farm_structure_tool_shed_v001.png` | y-sort structure | cropped tight | target width `520-720` | base center |
| `Fence` | `region_home_back_farm_prop_fence_long_v001.png` | blocker/prop | cropped tight | target width `1600-1900` | base center |
| `WateringCan` | `region_home_back_farm_prop_watering_can_v001.png` | prop/interactable | cropped tight | target width `120-180` | base center |
| `CompostBin` | `region_home_back_farm_prop_compost_bin_v001.png` | prop/interactable | cropped tight | target width `220-320` | base center |
| `StorageCrate` | `region_home_back_farm_prop_storage_crate_v001.png` | prop/interactable | cropped tight | target width `220-320` | base center |
| `FrontGrassRight` | `region_home_back_farm_foreground_front_grass_right_v001.png` | foreground occluder | `(3320, 2300)` | max `776 x 772` | top-left |
| `MorningLightBand` | `region_home_back_farm_fx_morning_light_band_v001.png` | light overlay | `(560, 520)` | max `2460 x 630` | top-left |
| `WindGrassGuide` | `region_home_back_farm_fx_wind_grass_top_v001.png` | animated grass overlay | `(0, 0)` | max `1440 x 690` | top-left |

## Occlusion Requirements

- Trees must be split into at least `trunk/body` and `canopy_occluder`.
- House must be split into at least `back/body` and `roof_or_eaves_occluder`.
- Tall crops need a front leaves occluder only for the lower foreground edge; do not export one giant crop rectangle over the full field.
- Alpha bounding boxes should not exceed visible pixels by more than `16 px` on any side, except for soft shadows/light overlays.
- Any occluder that covers the player torso should have a companion placement note with its intended Godot parent and z-index.

## Delivery Checklist

- PNG exports match names above.
- Each cropped PNG has an `origin_x, origin_y` recorded in a sidecar CSV or JSON.
- Each prop records `anchor_x, anchor_y` for the foot/base point.
- Ground/path patches align cleanly when placed at their documented origin.
- No visible rectangular alpha edge when composited over checkerboard.
- No player/NPC/animal baked into any environment layer.
