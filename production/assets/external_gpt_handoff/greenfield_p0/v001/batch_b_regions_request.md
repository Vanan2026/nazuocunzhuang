# Batch B - Region Mother Images And Runtime Layers Request

用途：生产 Greenfield P0 的 10 个区域母图、精绘源图和 Godot runtime layers。

交付方式：请在外部生成 PNG 后，按每个条目的相对路径放入 `incoming/` 目录。

Incoming 根目录：

```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming
```

验收命令：

```powershell
py -3.12 tools\validate_greenfield_p0_external_asset_intake.py --allow-partial
```

## 全局风格锁定

Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD.

## 全局负面要求

Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.

## 第二批总体要求

- 本批共 `110` 张 PNG：10 个区域，每个区域 11 张。
- 每个区域先做并确认 `painted_source` 完整精绘母图；runtime layers 必须从同一张母图拆层/遮罩/补绘生成，不要分别重新生成新构图。
- 目标是 `registration-perfect`：同一区域 11 张图必须完全同尺寸、同原点、同透视、同构图、同坐标系；叠加后应复原 painted_source 的主要空间关系。
- Manifest 坐标是工程蓝图和空间逻辑约束，不要求每个手绘边缘、草花石头笔触逐像素复刻坐标表。
- `painted_source` 与 `base_ground` 必须完全不透明；其他 layers 必须透明背景并保留干净 alpha。
- 透明 layers 必须导出完整区域画布，不能裁切到物体 bounding box，不能自动贴边。
- 道路、房屋、水井、田地、树、池塘、山路等必须遵守生活逻辑：物件在路边或可到达位置，不得压在路中心；田块不得覆盖路；建筑不得堵死入口。
- 构图不能过分工整或十区域套同一模板；每个区域必须有自己的道路节奏、功能重心和自然边界。
- 边缘 seam/socket 必须留出可连接空间，后续会用于无缝地图拼装。
- 不要把 UI、文字、水印、角色、战斗元素、怪物、武器画进区域图。

## Runtime Layer 规则

- `painted_source`: complete region source/review mother; fully painted composite for judging layout, mood, object placement, and seam readiness.
- `base_ground`: opaque base layer only: terrain, roads, water/soil/stone base, and walkable ground shapes; no tall props or foreground occluders.
- `terrain_details`: transparent detail layer: grass tufts, soil accents, small stones, leaves, and local texture variation; no blocking objects.
- `behind_player_structures`: transparent back/depth layer: walls, upper structures, distant tree masses, slopes, and forms that should render behind the player.
- `ysort_props_structures`: transparent interactive/depth layer: readable props, structures, crops, benches, wells, doors, rocks, or trees with bottom anchors for Y-sort.
- `foreground_occlusion`: transparent foreground layer: sparse canopy, front eaves, tall grass, rails, or ledge fronts that may pass in front of the player.
- `shadow_overlay`: transparent soft shadow layer: contact shadows and grounding shadows only; avoid heavy black shadows.
- `light_weather_overlay_spring`: transparent spring overlay: subtle warm light, fresh foliage hints, soft pollen or blossom accents.
- `light_weather_overlay_summer`: transparent summer overlay: gentle warmer light, fuller foliage accents, soft humid atmosphere.
- `light_weather_overlay_autumn`: transparent autumn overlay: low-saturation fallen leaves and mellow golden light.
- `light_weather_overlay_winter`: transparent winter overlay: light snow dusting or cool seasonal tint while preserving path readability.

## Region: home_area / HomeArea

- Canvas: `1470x1070`
- Road motif: `soft_home_lane`
- Road signature: `home_public_lane_private_yard_spurs`
- Composition focal point: `[0.43, 0.45]`
- Seam connectors: `{'north': [852, 85], 'south': [632, 984], 'east': [1352, 791], 'west': [117, 770]}`
- Space brief: Private home yard plus public front lane. The house must sit above its yard paths, never on the road. Mailbox and bench sit beside the public lane, and the well stays inside the private yard with a narrow side footpath.

### Road contract

- `public_front_lane` / role `public_lane` / width `42px` / points: (117, 770), (411, 770), (632, 770), (940, 770), (1146, 791), (1352, 791)
- `home_walk` / role `home_access` / width `45px` / points: (632, 984), (632, 770), (588, 684), (588, 535)
- `north_side_lane` / role `side_footpath` / width `27px` / points: (588, 535), (779, 502), (882, 267), (852, 85)
- `well_footpath` / role `utility_footpath` / width `24px` / points: (588, 684), (940, 706), (940, 770)
- `bench_step` / role `rest_access` / width `20px` / points: (411, 770), (455, 770)

### Object-zone contract

- `house` / role `home_structure` / rect `[418, 144, 757, 476]` / relation: main lane stops at the porch apron, not under the house footprint
- `mailbox` / role `roadside_prop` / rect `[264, 604, 404, 706]` / relation: beside the public front lane, not on it
- `well` / role `yard_utility` / rect `[984, 518, 1153, 690]` / relation: inside the private yard, reached from a narrow side footpath
- `bench` / role `rest_prop` / rect `[183, 807, 455, 952]` / relation: rest spot near the fence, separated from the lane

### Registration contract

- `painted_source` is the only composition source for this region.
- All runtime layers must keep the full canvas, origin `(0, 0)`, scale `1`, rotation `0`, and the same 3/4 perspective as `painted_source`.
- Roads and object zones should follow the manifest structure and remain spatially readable; natural hand-painted edge variation is allowed.
- Details such as grass, flowers, pebbles, leaves, and brush texture do not need pixel-perfect correspondence to manifest points.

### Asset requests

#### 1. home_area_painted_source

- 文件路径：
```text
01_mother_images/regions/home_area/home_area_painted_source.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/01_mother_images/regions/home_area/home_area_painted_source.png
```

- 尺寸：`1470x1070`
- Alpha：`fully opaque PNG`
- Layer brief: complete region source/review mother; fully painted composite for judging layout, mood, object placement, and seam readiness.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint a complete region source/review mother for home_area_painted_source; exact canvas 1470x1070 px; fully opaque complete review image; believable village-space layout, readable roads, props beside paths, no impossible overlaps. Region-specific requirement: Private home yard plus public front lane. The house must sit above its yard paths, never on the road. Mailbox and bench sit beside the public lane, and the well stays inside the private yard with a narrow side footpath. Layer requirement: complete region source/review mother; fully painted composite for judging layout, mood, object placement, and seam readiness. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 2. home_area_base_ground

- 文件路径：
```text
02_runtime_exports/regions/home_area/layers/home_area_base_ground.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/home_area/layers/home_area_base_ground.png
```

- 尺寸：`1470x1070`
- Alpha：`fully opaque PNG`
- Layer brief: opaque base layer only: terrain, roads, water/soil/stone base, and walkable ground shapes; no tall props or foreground occluders.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for home_area_base_ground; exact canvas 1470x1070 px; fully opaque complete review image; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Private home yard plus public front lane. The house must sit above its yard paths, never on the road. Mailbox and bench sit beside the public lane, and the well stays inside the private yard with a narrow side footpath. Layer requirement: opaque base layer only: terrain, roads, water/soil/stone base, and walkable ground shapes; no tall props or foreground occluders. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 3. home_area_terrain_details

- 文件路径：
```text
02_runtime_exports/regions/home_area/layers/home_area_terrain_details.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/home_area/layers/home_area_terrain_details.png
```

- 尺寸：`1470x1070`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent detail layer: grass tufts, soil accents, small stones, leaves, and local texture variation; no blocking objects.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for home_area_terrain_details; exact canvas 1470x1070 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Private home yard plus public front lane. The house must sit above its yard paths, never on the road. Mailbox and bench sit beside the public lane, and the well stays inside the private yard with a narrow side footpath. Layer requirement: transparent detail layer: grass tufts, soil accents, small stones, leaves, and local texture variation; no blocking objects. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 4. home_area_behind_player_structures

- 文件路径：
```text
02_runtime_exports/regions/home_area/layers/home_area_behind_player_structures.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/home_area/layers/home_area_behind_player_structures.png
```

- 尺寸：`1470x1070`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent back/depth layer: walls, upper structures, distant tree masses, slopes, and forms that should render behind the player.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for home_area_behind_player_structures; exact canvas 1470x1070 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Private home yard plus public front lane. The house must sit above its yard paths, never on the road. Mailbox and bench sit beside the public lane, and the well stays inside the private yard with a narrow side footpath. Layer requirement: transparent back/depth layer: walls, upper structures, distant tree masses, slopes, and forms that should render behind the player. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 5. home_area_ysort_props_structures

- 文件路径：
```text
02_runtime_exports/regions/home_area/layers/home_area_ysort_props_structures.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/home_area/layers/home_area_ysort_props_structures.png
```

- 尺寸：`1470x1070`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent interactive/depth layer: readable props, structures, crops, benches, wells, doors, rocks, or trees with bottom anchors for Y-sort.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for home_area_ysort_props_structures; exact canvas 1470x1070 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Private home yard plus public front lane. The house must sit above its yard paths, never on the road. Mailbox and bench sit beside the public lane, and the well stays inside the private yard with a narrow side footpath. Layer requirement: transparent interactive/depth layer: readable props, structures, crops, benches, wells, doors, rocks, or trees with bottom anchors for Y-sort. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 6. home_area_foreground_occlusion

- 文件路径：
```text
02_runtime_exports/regions/home_area/layers/home_area_foreground_occlusion.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/home_area/layers/home_area_foreground_occlusion.png
```

- 尺寸：`1470x1070`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent foreground layer: sparse canopy, front eaves, tall grass, rails, or ledge fronts that may pass in front of the player.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for home_area_foreground_occlusion; exact canvas 1470x1070 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Private home yard plus public front lane. The house must sit above its yard paths, never on the road. Mailbox and bench sit beside the public lane, and the well stays inside the private yard with a narrow side footpath. Layer requirement: transparent foreground layer: sparse canopy, front eaves, tall grass, rails, or ledge fronts that may pass in front of the player. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 7. home_area_shadow_overlay

- 文件路径：
```text
02_runtime_exports/regions/home_area/layers/home_area_shadow_overlay.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/home_area/layers/home_area_shadow_overlay.png
```

- 尺寸：`1470x1070`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent soft shadow layer: contact shadows and grounding shadows only; avoid heavy black shadows.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for home_area_shadow_overlay; exact canvas 1470x1070 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Private home yard plus public front lane. The house must sit above its yard paths, never on the road. Mailbox and bench sit beside the public lane, and the well stays inside the private yard with a narrow side footpath. Layer requirement: transparent soft shadow layer: contact shadows and grounding shadows only; avoid heavy black shadows. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 8. home_area_light_weather_overlay_spring

- 文件路径：
```text
02_runtime_exports/regions/home_area/layers/home_area_light_weather_overlay_spring.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/home_area/layers/home_area_light_weather_overlay_spring.png
```

- 尺寸：`1470x1070`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent spring overlay: subtle warm light, fresh foliage hints, soft pollen or blossom accents.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for home_area_light_weather_overlay_spring; exact canvas 1470x1070 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Private home yard plus public front lane. The house must sit above its yard paths, never on the road. Mailbox and bench sit beside the public lane, and the well stays inside the private yard with a narrow side footpath. Layer requirement: transparent spring overlay: subtle warm light, fresh foliage hints, soft pollen or blossom accents. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 9. home_area_light_weather_overlay_summer

- 文件路径：
```text
02_runtime_exports/regions/home_area/layers/home_area_light_weather_overlay_summer.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/home_area/layers/home_area_light_weather_overlay_summer.png
```

- 尺寸：`1470x1070`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent summer overlay: gentle warmer light, fuller foliage accents, soft humid atmosphere.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for home_area_light_weather_overlay_summer; exact canvas 1470x1070 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Private home yard plus public front lane. The house must sit above its yard paths, never on the road. Mailbox and bench sit beside the public lane, and the well stays inside the private yard with a narrow side footpath. Layer requirement: transparent summer overlay: gentle warmer light, fuller foliage accents, soft humid atmosphere. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 10. home_area_light_weather_overlay_autumn

- 文件路径：
```text
02_runtime_exports/regions/home_area/layers/home_area_light_weather_overlay_autumn.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/home_area/layers/home_area_light_weather_overlay_autumn.png
```

- 尺寸：`1470x1070`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent autumn overlay: low-saturation fallen leaves and mellow golden light.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for home_area_light_weather_overlay_autumn; exact canvas 1470x1070 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Private home yard plus public front lane. The house must sit above its yard paths, never on the road. Mailbox and bench sit beside the public lane, and the well stays inside the private yard with a narrow side footpath. Layer requirement: transparent autumn overlay: low-saturation fallen leaves and mellow golden light. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 11. home_area_light_weather_overlay_winter

- 文件路径：
```text
02_runtime_exports/regions/home_area/layers/home_area_light_weather_overlay_winter.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/home_area/layers/home_area_light_weather_overlay_winter.png
```

- 尺寸：`1470x1070`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent winter overlay: light snow dusting or cool seasonal tint while preserving path readability.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for home_area_light_weather_overlay_winter; exact canvas 1470x1070 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Private home yard plus public front lane. The house must sit above its yard paths, never on the road. Mailbox and bench sit beside the public lane, and the well stays inside the private yard with a narrow side footpath. Layer requirement: transparent winter overlay: light snow dusting or cool seasonal tint while preserving path readability. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

## Region: village / Village

- Canvas: `1800x1200`
- Road motif: `settled_village_lane`
- Road signature: `village_plaza_lane_doorstep_spurs`
- Composition focal point: `[0.55, 0.48]`
- Seam connectors: `{'north': [792, 96], 'south': [1134, 1104], 'east': [1656, 600], 'west': [144, 720]}`
- Space brief: Small lived-in village center with through lanes, a modest plaza edge, doorstep paths, and a small landmark. Houses must be set back from roads with readable door approaches, not pasted into the lane.

### Road contract

- `village_main_lane` / role `village_through_lane` / width `50px` / points: (144, 720), (864, 816), (1152, 744), (1656, 600)
- `north_lane` / role `village_through_lane` / width `41px` / points: (792, 96), (774, 600), (1080, 588)
- `south_lane` / role `village_through_lane` / width `41px` / points: (1134, 1104), (1152, 744)
- `plaza_edge` / role `plaza_edge` / width `30px` / points: (774, 600), (1080, 588), (1152, 744), (864, 816), (774, 600)
- `left_doorstep` / role `doorstep` / width `25px` / points: (774, 600), (594, 528)
- `right_doorstep` / role `doorstep` / width `25px` / points: (1080, 588), (1224, 552)
- `shrine_step` / role `landmark_access` / width `21px` / points: (774, 600), (936, 516)

### Object-zone contract

- `house_a` / role `village_structure` / rect `[333, 186, 630, 438]` / relation: left house sits off the square road
- `house_b` / role `village_structure` / rect `[1206, 228, 1467, 474]` / relation: right house sits above the east spur with a small doorstep
- `shrine` / role `small_landmark` / rect `[873, 318, 999, 426]` / relation: landmark above the plaza with a narrow approach
- `bench` / role `rest_prop` / rect `[567, 870, 810, 996]` / relation: rest prop below the plaza lane, not in road center

### Registration contract

- `painted_source` is the only composition source for this region.
- All runtime layers must keep the full canvas, origin `(0, 0)`, scale `1`, rotation `0`, and the same 3/4 perspective as `painted_source`.
- Roads and object zones should follow the manifest structure and remain spatially readable; natural hand-painted edge variation is allowed.
- Details such as grass, flowers, pebbles, leaves, and brush texture do not need pixel-perfect correspondence to manifest points.

### Asset requests

#### 1. village_painted_source

- 文件路径：
```text
01_mother_images/regions/village/village_painted_source.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/01_mother_images/regions/village/village_painted_source.png
```

- 尺寸：`1800x1200`
- Alpha：`fully opaque PNG`
- Layer brief: complete region source/review mother; fully painted composite for judging layout, mood, object placement, and seam readiness.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint a complete region source/review mother for village_painted_source; exact canvas 1800x1200 px; fully opaque complete review image; believable village-space layout, readable roads, props beside paths, no impossible overlaps. Region-specific requirement: Small lived-in village center with through lanes, a modest plaza edge, doorstep paths, and a small landmark. Houses must be set back from roads with readable door approaches, not pasted into the lane. Layer requirement: complete region source/review mother; fully painted composite for judging layout, mood, object placement, and seam readiness. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 2. village_base_ground

- 文件路径：
```text
02_runtime_exports/regions/village/layers/village_base_ground.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/village/layers/village_base_ground.png
```

- 尺寸：`1800x1200`
- Alpha：`fully opaque PNG`
- Layer brief: opaque base layer only: terrain, roads, water/soil/stone base, and walkable ground shapes; no tall props or foreground occluders.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for village_base_ground; exact canvas 1800x1200 px; fully opaque complete review image; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Small lived-in village center with through lanes, a modest plaza edge, doorstep paths, and a small landmark. Houses must be set back from roads with readable door approaches, not pasted into the lane. Layer requirement: opaque base layer only: terrain, roads, water/soil/stone base, and walkable ground shapes; no tall props or foreground occluders. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 3. village_terrain_details

- 文件路径：
```text
02_runtime_exports/regions/village/layers/village_terrain_details.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/village/layers/village_terrain_details.png
```

- 尺寸：`1800x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent detail layer: grass tufts, soil accents, small stones, leaves, and local texture variation; no blocking objects.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for village_terrain_details; exact canvas 1800x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Small lived-in village center with through lanes, a modest plaza edge, doorstep paths, and a small landmark. Houses must be set back from roads with readable door approaches, not pasted into the lane. Layer requirement: transparent detail layer: grass tufts, soil accents, small stones, leaves, and local texture variation; no blocking objects. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 4. village_behind_player_structures

- 文件路径：
```text
02_runtime_exports/regions/village/layers/village_behind_player_structures.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/village/layers/village_behind_player_structures.png
```

- 尺寸：`1800x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent back/depth layer: walls, upper structures, distant tree masses, slopes, and forms that should render behind the player.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for village_behind_player_structures; exact canvas 1800x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Small lived-in village center with through lanes, a modest plaza edge, doorstep paths, and a small landmark. Houses must be set back from roads with readable door approaches, not pasted into the lane. Layer requirement: transparent back/depth layer: walls, upper structures, distant tree masses, slopes, and forms that should render behind the player. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 5. village_ysort_props_structures

- 文件路径：
```text
02_runtime_exports/regions/village/layers/village_ysort_props_structures.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/village/layers/village_ysort_props_structures.png
```

- 尺寸：`1800x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent interactive/depth layer: readable props, structures, crops, benches, wells, doors, rocks, or trees with bottom anchors for Y-sort.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for village_ysort_props_structures; exact canvas 1800x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Small lived-in village center with through lanes, a modest plaza edge, doorstep paths, and a small landmark. Houses must be set back from roads with readable door approaches, not pasted into the lane. Layer requirement: transparent interactive/depth layer: readable props, structures, crops, benches, wells, doors, rocks, or trees with bottom anchors for Y-sort. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 6. village_foreground_occlusion

- 文件路径：
```text
02_runtime_exports/regions/village/layers/village_foreground_occlusion.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/village/layers/village_foreground_occlusion.png
```

- 尺寸：`1800x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent foreground layer: sparse canopy, front eaves, tall grass, rails, or ledge fronts that may pass in front of the player.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for village_foreground_occlusion; exact canvas 1800x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Small lived-in village center with through lanes, a modest plaza edge, doorstep paths, and a small landmark. Houses must be set back from roads with readable door approaches, not pasted into the lane. Layer requirement: transparent foreground layer: sparse canopy, front eaves, tall grass, rails, or ledge fronts that may pass in front of the player. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 7. village_shadow_overlay

- 文件路径：
```text
02_runtime_exports/regions/village/layers/village_shadow_overlay.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/village/layers/village_shadow_overlay.png
```

- 尺寸：`1800x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent soft shadow layer: contact shadows and grounding shadows only; avoid heavy black shadows.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for village_shadow_overlay; exact canvas 1800x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Small lived-in village center with through lanes, a modest plaza edge, doorstep paths, and a small landmark. Houses must be set back from roads with readable door approaches, not pasted into the lane. Layer requirement: transparent soft shadow layer: contact shadows and grounding shadows only; avoid heavy black shadows. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 8. village_light_weather_overlay_spring

- 文件路径：
```text
02_runtime_exports/regions/village/layers/village_light_weather_overlay_spring.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/village/layers/village_light_weather_overlay_spring.png
```

- 尺寸：`1800x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent spring overlay: subtle warm light, fresh foliage hints, soft pollen or blossom accents.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for village_light_weather_overlay_spring; exact canvas 1800x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Small lived-in village center with through lanes, a modest plaza edge, doorstep paths, and a small landmark. Houses must be set back from roads with readable door approaches, not pasted into the lane. Layer requirement: transparent spring overlay: subtle warm light, fresh foliage hints, soft pollen or blossom accents. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 9. village_light_weather_overlay_summer

- 文件路径：
```text
02_runtime_exports/regions/village/layers/village_light_weather_overlay_summer.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/village/layers/village_light_weather_overlay_summer.png
```

- 尺寸：`1800x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent summer overlay: gentle warmer light, fuller foliage accents, soft humid atmosphere.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for village_light_weather_overlay_summer; exact canvas 1800x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Small lived-in village center with through lanes, a modest plaza edge, doorstep paths, and a small landmark. Houses must be set back from roads with readable door approaches, not pasted into the lane. Layer requirement: transparent summer overlay: gentle warmer light, fuller foliage accents, soft humid atmosphere. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 10. village_light_weather_overlay_autumn

- 文件路径：
```text
02_runtime_exports/regions/village/layers/village_light_weather_overlay_autumn.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/village/layers/village_light_weather_overlay_autumn.png
```

- 尺寸：`1800x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent autumn overlay: low-saturation fallen leaves and mellow golden light.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for village_light_weather_overlay_autumn; exact canvas 1800x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Small lived-in village center with through lanes, a modest plaza edge, doorstep paths, and a small landmark. Houses must be set back from roads with readable door approaches, not pasted into the lane. Layer requirement: transparent autumn overlay: low-saturation fallen leaves and mellow golden light. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 11. village_light_weather_overlay_winter

- 文件路径：
```text
02_runtime_exports/regions/village/layers/village_light_weather_overlay_winter.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/village/layers/village_light_weather_overlay_winter.png
```

- 尺寸：`1800x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent winter overlay: light snow dusting or cool seasonal tint while preserving path readability.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for village_light_weather_overlay_winter; exact canvas 1800x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Small lived-in village center with through lanes, a modest plaza edge, doorstep paths, and a small landmark. Houses must be set back from roads with readable door approaches, not pasted into the lane. Layer requirement: transparent winter overlay: light snow dusting or cool seasonal tint while preserving path readability. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

## Region: back_farm / BackFarm

- Canvas: `1600x1200`
- Road motif: `field_lane`
- Road signature: `farm_service_lane_fields_shed_gate`
- Composition focal point: `[0.48, 0.58]`
- Seam connectors: `{'north': [800, 96], 'south': [800, 1128], 'east': [1472, 876], 'west': [128, 864]}`
- Space brief: Working farm area with a lower access lane, central service lane, clear shed approach, and field blocks on either side. Field plots must leave visible service gaps and must not cover or interrupt the roads.

### Road contract

- `lower_access_lane` / role `farm_access_lane` / width `41px` / points: (128, 864), (448, 840), (800, 936), (1280, 864), (1472, 876)
- `farm_service_lane` / role `farm_service_lane` / width `36px` / points: (800, 1128), (800, 936), (800, 768), (1184, 696), (1280, 468)
- `north_field_entry` / role `farm_access_lane` / width `28px` / points: (800, 96), (800, 768)
- `west_field_service` / role `field_service_path` / width `22px` / points: (800, 768), (624, 804)
- `east_field_service` / role `field_service_path` / width `22px` / points: (800, 768), (1024, 683)

### Object-zone contract

- `shed` / role `farm_structure` / rect `[1176, 222, 1384, 432]` / relation: shed stands above the service lane, with a clear approach point
- `field_block_west` / role `farm_plots` / rect `[256, 366, 712, 756]` / relation: field block left of the central lane
- `field_block_east` / role `farm_plots` / rect `[872, 366, 1120, 630]` / relation: smaller field block right of the central lane

### Registration contract

- `painted_source` is the only composition source for this region.
- All runtime layers must keep the full canvas, origin `(0, 0)`, scale `1`, rotation `0`, and the same 3/4 perspective as `painted_source`.
- Roads and object zones should follow the manifest structure and remain spatially readable; natural hand-painted edge variation is allowed.
- Details such as grass, flowers, pebbles, leaves, and brush texture do not need pixel-perfect correspondence to manifest points.

### Asset requests

#### 1. back_farm_painted_source

- 文件路径：
```text
01_mother_images/regions/back_farm/back_farm_painted_source.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/01_mother_images/regions/back_farm/back_farm_painted_source.png
```

- 尺寸：`1600x1200`
- Alpha：`fully opaque PNG`
- Layer brief: complete region source/review mother; fully painted composite for judging layout, mood, object placement, and seam readiness.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint a complete region source/review mother for back_farm_painted_source; exact canvas 1600x1200 px; fully opaque complete review image; believable village-space layout, readable roads, props beside paths, no impossible overlaps. Region-specific requirement: Working farm area with a lower access lane, central service lane, clear shed approach, and field blocks on either side. Field plots must leave visible service gaps and must not cover or interrupt the roads. Layer requirement: complete region source/review mother; fully painted composite for judging layout, mood, object placement, and seam readiness. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 2. back_farm_base_ground

- 文件路径：
```text
02_runtime_exports/regions/back_farm/layers/back_farm_base_ground.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/back_farm/layers/back_farm_base_ground.png
```

- 尺寸：`1600x1200`
- Alpha：`fully opaque PNG`
- Layer brief: opaque base layer only: terrain, roads, water/soil/stone base, and walkable ground shapes; no tall props or foreground occluders.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for back_farm_base_ground; exact canvas 1600x1200 px; fully opaque complete review image; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Working farm area with a lower access lane, central service lane, clear shed approach, and field blocks on either side. Field plots must leave visible service gaps and must not cover or interrupt the roads. Layer requirement: opaque base layer only: terrain, roads, water/soil/stone base, and walkable ground shapes; no tall props or foreground occluders. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 3. back_farm_terrain_details

- 文件路径：
```text
02_runtime_exports/regions/back_farm/layers/back_farm_terrain_details.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/back_farm/layers/back_farm_terrain_details.png
```

- 尺寸：`1600x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent detail layer: grass tufts, soil accents, small stones, leaves, and local texture variation; no blocking objects.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for back_farm_terrain_details; exact canvas 1600x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Working farm area with a lower access lane, central service lane, clear shed approach, and field blocks on either side. Field plots must leave visible service gaps and must not cover or interrupt the roads. Layer requirement: transparent detail layer: grass tufts, soil accents, small stones, leaves, and local texture variation; no blocking objects. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 4. back_farm_behind_player_structures

- 文件路径：
```text
02_runtime_exports/regions/back_farm/layers/back_farm_behind_player_structures.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/back_farm/layers/back_farm_behind_player_structures.png
```

- 尺寸：`1600x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent back/depth layer: walls, upper structures, distant tree masses, slopes, and forms that should render behind the player.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for back_farm_behind_player_structures; exact canvas 1600x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Working farm area with a lower access lane, central service lane, clear shed approach, and field blocks on either side. Field plots must leave visible service gaps and must not cover or interrupt the roads. Layer requirement: transparent back/depth layer: walls, upper structures, distant tree masses, slopes, and forms that should render behind the player. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 5. back_farm_ysort_props_structures

- 文件路径：
```text
02_runtime_exports/regions/back_farm/layers/back_farm_ysort_props_structures.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/back_farm/layers/back_farm_ysort_props_structures.png
```

- 尺寸：`1600x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent interactive/depth layer: readable props, structures, crops, benches, wells, doors, rocks, or trees with bottom anchors for Y-sort.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for back_farm_ysort_props_structures; exact canvas 1600x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Working farm area with a lower access lane, central service lane, clear shed approach, and field blocks on either side. Field plots must leave visible service gaps and must not cover or interrupt the roads. Layer requirement: transparent interactive/depth layer: readable props, structures, crops, benches, wells, doors, rocks, or trees with bottom anchors for Y-sort. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 6. back_farm_foreground_occlusion

- 文件路径：
```text
02_runtime_exports/regions/back_farm/layers/back_farm_foreground_occlusion.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/back_farm/layers/back_farm_foreground_occlusion.png
```

- 尺寸：`1600x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent foreground layer: sparse canopy, front eaves, tall grass, rails, or ledge fronts that may pass in front of the player.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for back_farm_foreground_occlusion; exact canvas 1600x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Working farm area with a lower access lane, central service lane, clear shed approach, and field blocks on either side. Field plots must leave visible service gaps and must not cover or interrupt the roads. Layer requirement: transparent foreground layer: sparse canopy, front eaves, tall grass, rails, or ledge fronts that may pass in front of the player. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 7. back_farm_shadow_overlay

- 文件路径：
```text
02_runtime_exports/regions/back_farm/layers/back_farm_shadow_overlay.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/back_farm/layers/back_farm_shadow_overlay.png
```

- 尺寸：`1600x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent soft shadow layer: contact shadows and grounding shadows only; avoid heavy black shadows.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for back_farm_shadow_overlay; exact canvas 1600x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Working farm area with a lower access lane, central service lane, clear shed approach, and field blocks on either side. Field plots must leave visible service gaps and must not cover or interrupt the roads. Layer requirement: transparent soft shadow layer: contact shadows and grounding shadows only; avoid heavy black shadows. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 8. back_farm_light_weather_overlay_spring

- 文件路径：
```text
02_runtime_exports/regions/back_farm/layers/back_farm_light_weather_overlay_spring.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/back_farm/layers/back_farm_light_weather_overlay_spring.png
```

- 尺寸：`1600x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent spring overlay: subtle warm light, fresh foliage hints, soft pollen or blossom accents.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for back_farm_light_weather_overlay_spring; exact canvas 1600x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Working farm area with a lower access lane, central service lane, clear shed approach, and field blocks on either side. Field plots must leave visible service gaps and must not cover or interrupt the roads. Layer requirement: transparent spring overlay: subtle warm light, fresh foliage hints, soft pollen or blossom accents. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 9. back_farm_light_weather_overlay_summer

- 文件路径：
```text
02_runtime_exports/regions/back_farm/layers/back_farm_light_weather_overlay_summer.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/back_farm/layers/back_farm_light_weather_overlay_summer.png
```

- 尺寸：`1600x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent summer overlay: gentle warmer light, fuller foliage accents, soft humid atmosphere.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for back_farm_light_weather_overlay_summer; exact canvas 1600x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Working farm area with a lower access lane, central service lane, clear shed approach, and field blocks on either side. Field plots must leave visible service gaps and must not cover or interrupt the roads. Layer requirement: transparent summer overlay: gentle warmer light, fuller foliage accents, soft humid atmosphere. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 10. back_farm_light_weather_overlay_autumn

- 文件路径：
```text
02_runtime_exports/regions/back_farm/layers/back_farm_light_weather_overlay_autumn.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/back_farm/layers/back_farm_light_weather_overlay_autumn.png
```

- 尺寸：`1600x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent autumn overlay: low-saturation fallen leaves and mellow golden light.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for back_farm_light_weather_overlay_autumn; exact canvas 1600x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Working farm area with a lower access lane, central service lane, clear shed approach, and field blocks on either side. Field plots must leave visible service gaps and must not cover or interrupt the roads. Layer requirement: transparent autumn overlay: low-saturation fallen leaves and mellow golden light. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 11. back_farm_light_weather_overlay_winter

- 文件路径：
```text
02_runtime_exports/regions/back_farm/layers/back_farm_light_weather_overlay_winter.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/back_farm/layers/back_farm_light_weather_overlay_winter.png
```

- 尺寸：`1600x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent winter overlay: light snow dusting or cool seasonal tint while preserving path readability.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for back_farm_light_weather_overlay_winter; exact canvas 1600x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Working farm area with a lower access lane, central service lane, clear shed approach, and field blocks on either side. Field plots must leave visible service gaps and must not cover or interrupt the roads. Layer requirement: transparent winter overlay: light snow dusting or cool seasonal tint while preserving path readability. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

## Region: forest_edge / ForestEdge

- Canvas: `1700x1150`
- Road motif: `broken_moss_path`
- Road signature: `forest_broken_moss_trail_west_north`
- Composition focal point: `[0.58, 0.45]`
- Seam connectors: `{'north': [1071, 92], 'south': [646, 1058], 'east': [1564, 575], 'west': [136, 713]}`
- Space brief: Loose forest border with a broken moss trail, forage spur, and orchard link. Keep tree masses organic but leave the path readable.

### Road contract

- `broken_moss_west_north` / role `forest_trail` / width `51px` / points: (136, 713), (408, 736), (714, 632), (985, 494), (1190, 356), (1071, 92)
- `faint_east_deer_path` / role `forage_spur` / width `34px` / points: (985, 494), (1564, 575)
- `orchard_footpath` / role `forest_orchard_link` / width `30px` / points: (714, 632), (646, 1058)

### Object-zone contract

- No required object-zone rectangles in manifest; preserve the road motif and leave walkable gaps around major props.

### Registration contract

- `painted_source` is the only composition source for this region.
- All runtime layers must keep the full canvas, origin `(0, 0)`, scale `1`, rotation `0`, and the same 3/4 perspective as `painted_source`.
- Roads and object zones should follow the manifest structure and remain spatially readable; natural hand-painted edge variation is allowed.
- Details such as grass, flowers, pebbles, leaves, and brush texture do not need pixel-perfect correspondence to manifest points.

### Asset requests

#### 1. forest_edge_painted_source

- 文件路径：
```text
01_mother_images/regions/forest_edge/forest_edge_painted_source.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/01_mother_images/regions/forest_edge/forest_edge_painted_source.png
```

- 尺寸：`1700x1150`
- Alpha：`fully opaque PNG`
- Layer brief: complete region source/review mother; fully painted composite for judging layout, mood, object placement, and seam readiness.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint a complete region source/review mother for forest_edge_painted_source; exact canvas 1700x1150 px; fully opaque complete review image; believable village-space layout, readable roads, props beside paths, no impossible overlaps. Region-specific requirement: Loose forest border with a broken moss trail, forage spur, and orchard link. Keep tree masses organic but leave the path readable. Layer requirement: complete region source/review mother; fully painted composite for judging layout, mood, object placement, and seam readiness. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 2. forest_edge_base_ground

- 文件路径：
```text
02_runtime_exports/regions/forest_edge/layers/forest_edge_base_ground.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/forest_edge/layers/forest_edge_base_ground.png
```

- 尺寸：`1700x1150`
- Alpha：`fully opaque PNG`
- Layer brief: opaque base layer only: terrain, roads, water/soil/stone base, and walkable ground shapes; no tall props or foreground occluders.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for forest_edge_base_ground; exact canvas 1700x1150 px; fully opaque complete review image; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Loose forest border with a broken moss trail, forage spur, and orchard link. Keep tree masses organic but leave the path readable. Layer requirement: opaque base layer only: terrain, roads, water/soil/stone base, and walkable ground shapes; no tall props or foreground occluders. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 3. forest_edge_terrain_details

- 文件路径：
```text
02_runtime_exports/regions/forest_edge/layers/forest_edge_terrain_details.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/forest_edge/layers/forest_edge_terrain_details.png
```

- 尺寸：`1700x1150`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent detail layer: grass tufts, soil accents, small stones, leaves, and local texture variation; no blocking objects.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for forest_edge_terrain_details; exact canvas 1700x1150 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Loose forest border with a broken moss trail, forage spur, and orchard link. Keep tree masses organic but leave the path readable. Layer requirement: transparent detail layer: grass tufts, soil accents, small stones, leaves, and local texture variation; no blocking objects. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 4. forest_edge_behind_player_structures

- 文件路径：
```text
02_runtime_exports/regions/forest_edge/layers/forest_edge_behind_player_structures.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/forest_edge/layers/forest_edge_behind_player_structures.png
```

- 尺寸：`1700x1150`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent back/depth layer: walls, upper structures, distant tree masses, slopes, and forms that should render behind the player.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for forest_edge_behind_player_structures; exact canvas 1700x1150 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Loose forest border with a broken moss trail, forage spur, and orchard link. Keep tree masses organic but leave the path readable. Layer requirement: transparent back/depth layer: walls, upper structures, distant tree masses, slopes, and forms that should render behind the player. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 5. forest_edge_ysort_props_structures

- 文件路径：
```text
02_runtime_exports/regions/forest_edge/layers/forest_edge_ysort_props_structures.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/forest_edge/layers/forest_edge_ysort_props_structures.png
```

- 尺寸：`1700x1150`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent interactive/depth layer: readable props, structures, crops, benches, wells, doors, rocks, or trees with bottom anchors for Y-sort.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for forest_edge_ysort_props_structures; exact canvas 1700x1150 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Loose forest border with a broken moss trail, forage spur, and orchard link. Keep tree masses organic but leave the path readable. Layer requirement: transparent interactive/depth layer: readable props, structures, crops, benches, wells, doors, rocks, or trees with bottom anchors for Y-sort. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 6. forest_edge_foreground_occlusion

- 文件路径：
```text
02_runtime_exports/regions/forest_edge/layers/forest_edge_foreground_occlusion.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/forest_edge/layers/forest_edge_foreground_occlusion.png
```

- 尺寸：`1700x1150`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent foreground layer: sparse canopy, front eaves, tall grass, rails, or ledge fronts that may pass in front of the player.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for forest_edge_foreground_occlusion; exact canvas 1700x1150 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Loose forest border with a broken moss trail, forage spur, and orchard link. Keep tree masses organic but leave the path readable. Layer requirement: transparent foreground layer: sparse canopy, front eaves, tall grass, rails, or ledge fronts that may pass in front of the player. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 7. forest_edge_shadow_overlay

- 文件路径：
```text
02_runtime_exports/regions/forest_edge/layers/forest_edge_shadow_overlay.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/forest_edge/layers/forest_edge_shadow_overlay.png
```

- 尺寸：`1700x1150`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent soft shadow layer: contact shadows and grounding shadows only; avoid heavy black shadows.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for forest_edge_shadow_overlay; exact canvas 1700x1150 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Loose forest border with a broken moss trail, forage spur, and orchard link. Keep tree masses organic but leave the path readable. Layer requirement: transparent soft shadow layer: contact shadows and grounding shadows only; avoid heavy black shadows. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 8. forest_edge_light_weather_overlay_spring

- 文件路径：
```text
02_runtime_exports/regions/forest_edge/layers/forest_edge_light_weather_overlay_spring.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/forest_edge/layers/forest_edge_light_weather_overlay_spring.png
```

- 尺寸：`1700x1150`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent spring overlay: subtle warm light, fresh foliage hints, soft pollen or blossom accents.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for forest_edge_light_weather_overlay_spring; exact canvas 1700x1150 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Loose forest border with a broken moss trail, forage spur, and orchard link. Keep tree masses organic but leave the path readable. Layer requirement: transparent spring overlay: subtle warm light, fresh foliage hints, soft pollen or blossom accents. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 9. forest_edge_light_weather_overlay_summer

- 文件路径：
```text
02_runtime_exports/regions/forest_edge/layers/forest_edge_light_weather_overlay_summer.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/forest_edge/layers/forest_edge_light_weather_overlay_summer.png
```

- 尺寸：`1700x1150`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent summer overlay: gentle warmer light, fuller foliage accents, soft humid atmosphere.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for forest_edge_light_weather_overlay_summer; exact canvas 1700x1150 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Loose forest border with a broken moss trail, forage spur, and orchard link. Keep tree masses organic but leave the path readable. Layer requirement: transparent summer overlay: gentle warmer light, fuller foliage accents, soft humid atmosphere. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 10. forest_edge_light_weather_overlay_autumn

- 文件路径：
```text
02_runtime_exports/regions/forest_edge/layers/forest_edge_light_weather_overlay_autumn.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/forest_edge/layers/forest_edge_light_weather_overlay_autumn.png
```

- 尺寸：`1700x1150`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent autumn overlay: low-saturation fallen leaves and mellow golden light.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for forest_edge_light_weather_overlay_autumn; exact canvas 1700x1150 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Loose forest border with a broken moss trail, forage spur, and orchard link. Keep tree masses organic but leave the path readable. Layer requirement: transparent autumn overlay: low-saturation fallen leaves and mellow golden light. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 11. forest_edge_light_weather_overlay_winter

- 文件路径：
```text
02_runtime_exports/regions/forest_edge/layers/forest_edge_light_weather_overlay_winter.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/forest_edge/layers/forest_edge_light_weather_overlay_winter.png
```

- 尺寸：`1700x1150`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent winter overlay: light snow dusting or cool seasonal tint while preserving path readability.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for forest_edge_light_weather_overlay_winter; exact canvas 1700x1150 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Loose forest border with a broken moss trail, forage spur, and orchard link. Keep tree masses organic but leave the path readable. Layer requirement: transparent winter overlay: light snow dusting or cool seasonal tint while preserving path readability. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

## Region: orchard / Orchard

- Canvas: `1700x1150`
- Road motif: `orchard_service_path`
- Road signature: `orchard_diagonal_service_rows`
- Composition focal point: `[0.44, 0.52]`
- Seam connectors: `{'north': [748, 92], 'south': [918, 1058], 'east': [1564, 736], 'west': [136, 552]}`
- Space brief: Orchard with diagonal service path and cart gap through tree rows. Rows may be rhythmic but should not become a perfect grid.

### Road contract

- `diagonal_service_path` / role `orchard_service_path` / width `54px` / points: (748, 92), (578, 437), (850, 632), (1156, 805), (918, 1058)
- `east_cart_gap` / role `orchard_cart_gap` / width `37px` / points: (136, 552), (850, 632), (1564, 736)

### Object-zone contract

- No required object-zone rectangles in manifest; preserve the road motif and leave walkable gaps around major props.

### Registration contract

- `painted_source` is the only composition source for this region.
- All runtime layers must keep the full canvas, origin `(0, 0)`, scale `1`, rotation `0`, and the same 3/4 perspective as `painted_source`.
- Roads and object zones should follow the manifest structure and remain spatially readable; natural hand-painted edge variation is allowed.
- Details such as grass, flowers, pebbles, leaves, and brush texture do not need pixel-perfect correspondence to manifest points.

### Asset requests

#### 1. orchard_painted_source

- 文件路径：
```text
01_mother_images/regions/orchard/orchard_painted_source.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/01_mother_images/regions/orchard/orchard_painted_source.png
```

- 尺寸：`1700x1150`
- Alpha：`fully opaque PNG`
- Layer brief: complete region source/review mother; fully painted composite for judging layout, mood, object placement, and seam readiness.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint a complete region source/review mother for orchard_painted_source; exact canvas 1700x1150 px; fully opaque complete review image; believable village-space layout, readable roads, props beside paths, no impossible overlaps. Region-specific requirement: Orchard with diagonal service path and cart gap through tree rows. Rows may be rhythmic but should not become a perfect grid. Layer requirement: complete region source/review mother; fully painted composite for judging layout, mood, object placement, and seam readiness. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 2. orchard_base_ground

- 文件路径：
```text
02_runtime_exports/regions/orchard/layers/orchard_base_ground.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/orchard/layers/orchard_base_ground.png
```

- 尺寸：`1700x1150`
- Alpha：`fully opaque PNG`
- Layer brief: opaque base layer only: terrain, roads, water/soil/stone base, and walkable ground shapes; no tall props or foreground occluders.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for orchard_base_ground; exact canvas 1700x1150 px; fully opaque complete review image; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Orchard with diagonal service path and cart gap through tree rows. Rows may be rhythmic but should not become a perfect grid. Layer requirement: opaque base layer only: terrain, roads, water/soil/stone base, and walkable ground shapes; no tall props or foreground occluders. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 3. orchard_terrain_details

- 文件路径：
```text
02_runtime_exports/regions/orchard/layers/orchard_terrain_details.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/orchard/layers/orchard_terrain_details.png
```

- 尺寸：`1700x1150`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent detail layer: grass tufts, soil accents, small stones, leaves, and local texture variation; no blocking objects.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for orchard_terrain_details; exact canvas 1700x1150 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Orchard with diagonal service path and cart gap through tree rows. Rows may be rhythmic but should not become a perfect grid. Layer requirement: transparent detail layer: grass tufts, soil accents, small stones, leaves, and local texture variation; no blocking objects. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 4. orchard_behind_player_structures

- 文件路径：
```text
02_runtime_exports/regions/orchard/layers/orchard_behind_player_structures.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/orchard/layers/orchard_behind_player_structures.png
```

- 尺寸：`1700x1150`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent back/depth layer: walls, upper structures, distant tree masses, slopes, and forms that should render behind the player.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for orchard_behind_player_structures; exact canvas 1700x1150 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Orchard with diagonal service path and cart gap through tree rows. Rows may be rhythmic but should not become a perfect grid. Layer requirement: transparent back/depth layer: walls, upper structures, distant tree masses, slopes, and forms that should render behind the player. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 5. orchard_ysort_props_structures

- 文件路径：
```text
02_runtime_exports/regions/orchard/layers/orchard_ysort_props_structures.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/orchard/layers/orchard_ysort_props_structures.png
```

- 尺寸：`1700x1150`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent interactive/depth layer: readable props, structures, crops, benches, wells, doors, rocks, or trees with bottom anchors for Y-sort.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for orchard_ysort_props_structures; exact canvas 1700x1150 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Orchard with diagonal service path and cart gap through tree rows. Rows may be rhythmic but should not become a perfect grid. Layer requirement: transparent interactive/depth layer: readable props, structures, crops, benches, wells, doors, rocks, or trees with bottom anchors for Y-sort. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 6. orchard_foreground_occlusion

- 文件路径：
```text
02_runtime_exports/regions/orchard/layers/orchard_foreground_occlusion.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/orchard/layers/orchard_foreground_occlusion.png
```

- 尺寸：`1700x1150`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent foreground layer: sparse canopy, front eaves, tall grass, rails, or ledge fronts that may pass in front of the player.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for orchard_foreground_occlusion; exact canvas 1700x1150 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Orchard with diagonal service path and cart gap through tree rows. Rows may be rhythmic but should not become a perfect grid. Layer requirement: transparent foreground layer: sparse canopy, front eaves, tall grass, rails, or ledge fronts that may pass in front of the player. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 7. orchard_shadow_overlay

- 文件路径：
```text
02_runtime_exports/regions/orchard/layers/orchard_shadow_overlay.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/orchard/layers/orchard_shadow_overlay.png
```

- 尺寸：`1700x1150`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent soft shadow layer: contact shadows and grounding shadows only; avoid heavy black shadows.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for orchard_shadow_overlay; exact canvas 1700x1150 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Orchard with diagonal service path and cart gap through tree rows. Rows may be rhythmic but should not become a perfect grid. Layer requirement: transparent soft shadow layer: contact shadows and grounding shadows only; avoid heavy black shadows. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 8. orchard_light_weather_overlay_spring

- 文件路径：
```text
02_runtime_exports/regions/orchard/layers/orchard_light_weather_overlay_spring.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/orchard/layers/orchard_light_weather_overlay_spring.png
```

- 尺寸：`1700x1150`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent spring overlay: subtle warm light, fresh foliage hints, soft pollen or blossom accents.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for orchard_light_weather_overlay_spring; exact canvas 1700x1150 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Orchard with diagonal service path and cart gap through tree rows. Rows may be rhythmic but should not become a perfect grid. Layer requirement: transparent spring overlay: subtle warm light, fresh foliage hints, soft pollen or blossom accents. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 9. orchard_light_weather_overlay_summer

- 文件路径：
```text
02_runtime_exports/regions/orchard/layers/orchard_light_weather_overlay_summer.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/orchard/layers/orchard_light_weather_overlay_summer.png
```

- 尺寸：`1700x1150`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent summer overlay: gentle warmer light, fuller foliage accents, soft humid atmosphere.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for orchard_light_weather_overlay_summer; exact canvas 1700x1150 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Orchard with diagonal service path and cart gap through tree rows. Rows may be rhythmic but should not become a perfect grid. Layer requirement: transparent summer overlay: gentle warmer light, fuller foliage accents, soft humid atmosphere. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 10. orchard_light_weather_overlay_autumn

- 文件路径：
```text
02_runtime_exports/regions/orchard/layers/orchard_light_weather_overlay_autumn.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/orchard/layers/orchard_light_weather_overlay_autumn.png
```

- 尺寸：`1700x1150`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent autumn overlay: low-saturation fallen leaves and mellow golden light.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for orchard_light_weather_overlay_autumn; exact canvas 1700x1150 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Orchard with diagonal service path and cart gap through tree rows. Rows may be rhythmic but should not become a perfect grid. Layer requirement: transparent autumn overlay: low-saturation fallen leaves and mellow golden light. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 11. orchard_light_weather_overlay_winter

- 文件路径：
```text
02_runtime_exports/regions/orchard/layers/orchard_light_weather_overlay_winter.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/orchard/layers/orchard_light_weather_overlay_winter.png
```

- 尺寸：`1700x1150`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent winter overlay: light snow dusting or cool seasonal tint while preserving path readability.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for orchard_light_weather_overlay_winter; exact canvas 1700x1150 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Orchard with diagonal service path and cart gap through tree rows. Rows may be rhythmic but should not become a perfect grid. Layer requirement: transparent winter overlay: light snow dusting or cool seasonal tint while preserving path readability. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

## Region: pond / Pond

- Canvas: `1600x1100`
- Road motif: `water_edge_crescent`
- Road signature: `pond_crescent_bank_path`
- Composition focal point: `[0.45, 0.49]`
- Seam connectors: `{'north': [816, 88], 'south': [576, 1012], 'east': [1472, 495], 'west': [128, 715]}`
- Space brief: Pond bank with a crescent walking path, small dock/rest point, south rest spur, and north arrival path. Water edge and bank path must be distinct.

### Road contract

- `lower_bank_crescent` / role `pond_bank_path` / width `44px` / points: (128, 715), (320, 770), (512, 836), (864, 825), (927, 748), (1168, 671), (1472, 495)
- `south_rest_spur` / role `rest_access` / width `35px` / points: (576, 1012), (400, 858), (512, 836)
- `north_bank_arrival` / role `pond_arrival_path` / width `28px` / points: (816, 88), (1168, 671)

### Object-zone contract

- No required object-zone rectangles in manifest; preserve the road motif and leave walkable gaps around major props.

### Registration contract

- `painted_source` is the only composition source for this region.
- All runtime layers must keep the full canvas, origin `(0, 0)`, scale `1`, rotation `0`, and the same 3/4 perspective as `painted_source`.
- Roads and object zones should follow the manifest structure and remain spatially readable; natural hand-painted edge variation is allowed.
- Details such as grass, flowers, pebbles, leaves, and brush texture do not need pixel-perfect correspondence to manifest points.

### Asset requests

#### 1. pond_painted_source

- 文件路径：
```text
01_mother_images/regions/pond/pond_painted_source.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/01_mother_images/regions/pond/pond_painted_source.png
```

- 尺寸：`1600x1100`
- Alpha：`fully opaque PNG`
- Layer brief: complete region source/review mother; fully painted composite for judging layout, mood, object placement, and seam readiness.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint a complete region source/review mother for pond_painted_source; exact canvas 1600x1100 px; fully opaque complete review image; believable village-space layout, readable roads, props beside paths, no impossible overlaps. Region-specific requirement: Pond bank with a crescent walking path, small dock/rest point, south rest spur, and north arrival path. Water edge and bank path must be distinct. Layer requirement: complete region source/review mother; fully painted composite for judging layout, mood, object placement, and seam readiness. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 2. pond_base_ground

- 文件路径：
```text
02_runtime_exports/regions/pond/layers/pond_base_ground.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/pond/layers/pond_base_ground.png
```

- 尺寸：`1600x1100`
- Alpha：`fully opaque PNG`
- Layer brief: opaque base layer only: terrain, roads, water/soil/stone base, and walkable ground shapes; no tall props or foreground occluders.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for pond_base_ground; exact canvas 1600x1100 px; fully opaque complete review image; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Pond bank with a crescent walking path, small dock/rest point, south rest spur, and north arrival path. Water edge and bank path must be distinct. Layer requirement: opaque base layer only: terrain, roads, water/soil/stone base, and walkable ground shapes; no tall props or foreground occluders. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 3. pond_terrain_details

- 文件路径：
```text
02_runtime_exports/regions/pond/layers/pond_terrain_details.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/pond/layers/pond_terrain_details.png
```

- 尺寸：`1600x1100`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent detail layer: grass tufts, soil accents, small stones, leaves, and local texture variation; no blocking objects.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for pond_terrain_details; exact canvas 1600x1100 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Pond bank with a crescent walking path, small dock/rest point, south rest spur, and north arrival path. Water edge and bank path must be distinct. Layer requirement: transparent detail layer: grass tufts, soil accents, small stones, leaves, and local texture variation; no blocking objects. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 4. pond_behind_player_structures

- 文件路径：
```text
02_runtime_exports/regions/pond/layers/pond_behind_player_structures.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/pond/layers/pond_behind_player_structures.png
```

- 尺寸：`1600x1100`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent back/depth layer: walls, upper structures, distant tree masses, slopes, and forms that should render behind the player.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for pond_behind_player_structures; exact canvas 1600x1100 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Pond bank with a crescent walking path, small dock/rest point, south rest spur, and north arrival path. Water edge and bank path must be distinct. Layer requirement: transparent back/depth layer: walls, upper structures, distant tree masses, slopes, and forms that should render behind the player. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 5. pond_ysort_props_structures

- 文件路径：
```text
02_runtime_exports/regions/pond/layers/pond_ysort_props_structures.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/pond/layers/pond_ysort_props_structures.png
```

- 尺寸：`1600x1100`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent interactive/depth layer: readable props, structures, crops, benches, wells, doors, rocks, or trees with bottom anchors for Y-sort.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for pond_ysort_props_structures; exact canvas 1600x1100 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Pond bank with a crescent walking path, small dock/rest point, south rest spur, and north arrival path. Water edge and bank path must be distinct. Layer requirement: transparent interactive/depth layer: readable props, structures, crops, benches, wells, doors, rocks, or trees with bottom anchors for Y-sort. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 6. pond_foreground_occlusion

- 文件路径：
```text
02_runtime_exports/regions/pond/layers/pond_foreground_occlusion.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/pond/layers/pond_foreground_occlusion.png
```

- 尺寸：`1600x1100`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent foreground layer: sparse canopy, front eaves, tall grass, rails, or ledge fronts that may pass in front of the player.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for pond_foreground_occlusion; exact canvas 1600x1100 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Pond bank with a crescent walking path, small dock/rest point, south rest spur, and north arrival path. Water edge and bank path must be distinct. Layer requirement: transparent foreground layer: sparse canopy, front eaves, tall grass, rails, or ledge fronts that may pass in front of the player. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 7. pond_shadow_overlay

- 文件路径：
```text
02_runtime_exports/regions/pond/layers/pond_shadow_overlay.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/pond/layers/pond_shadow_overlay.png
```

- 尺寸：`1600x1100`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent soft shadow layer: contact shadows and grounding shadows only; avoid heavy black shadows.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for pond_shadow_overlay; exact canvas 1600x1100 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Pond bank with a crescent walking path, small dock/rest point, south rest spur, and north arrival path. Water edge and bank path must be distinct. Layer requirement: transparent soft shadow layer: contact shadows and grounding shadows only; avoid heavy black shadows. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 8. pond_light_weather_overlay_spring

- 文件路径：
```text
02_runtime_exports/regions/pond/layers/pond_light_weather_overlay_spring.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/pond/layers/pond_light_weather_overlay_spring.png
```

- 尺寸：`1600x1100`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent spring overlay: subtle warm light, fresh foliage hints, soft pollen or blossom accents.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for pond_light_weather_overlay_spring; exact canvas 1600x1100 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Pond bank with a crescent walking path, small dock/rest point, south rest spur, and north arrival path. Water edge and bank path must be distinct. Layer requirement: transparent spring overlay: subtle warm light, fresh foliage hints, soft pollen or blossom accents. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 9. pond_light_weather_overlay_summer

- 文件路径：
```text
02_runtime_exports/regions/pond/layers/pond_light_weather_overlay_summer.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/pond/layers/pond_light_weather_overlay_summer.png
```

- 尺寸：`1600x1100`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent summer overlay: gentle warmer light, fuller foliage accents, soft humid atmosphere.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for pond_light_weather_overlay_summer; exact canvas 1600x1100 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Pond bank with a crescent walking path, small dock/rest point, south rest spur, and north arrival path. Water edge and bank path must be distinct. Layer requirement: transparent summer overlay: gentle warmer light, fuller foliage accents, soft humid atmosphere. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 10. pond_light_weather_overlay_autumn

- 文件路径：
```text
02_runtime_exports/regions/pond/layers/pond_light_weather_overlay_autumn.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/pond/layers/pond_light_weather_overlay_autumn.png
```

- 尺寸：`1600x1100`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent autumn overlay: low-saturation fallen leaves and mellow golden light.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for pond_light_weather_overlay_autumn; exact canvas 1600x1100 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Pond bank with a crescent walking path, small dock/rest point, south rest spur, and north arrival path. Water edge and bank path must be distinct. Layer requirement: transparent autumn overlay: low-saturation fallen leaves and mellow golden light. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 11. pond_light_weather_overlay_winter

- 文件路径：
```text
02_runtime_exports/regions/pond/layers/pond_light_weather_overlay_winter.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/pond/layers/pond_light_weather_overlay_winter.png
```

- 尺寸：`1600x1100`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent winter overlay: light snow dusting or cool seasonal tint while preserving path readability.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for pond_light_weather_overlay_winter; exact canvas 1600x1100 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Pond bank with a crescent walking path, small dock/rest point, south rest spur, and north arrival path. Water edge and bank path must be distinct. Layer requirement: transparent winter overlay: light snow dusting or cool seasonal tint while preserving path readability. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

## Region: mountain_path / MountainPath

- Canvas: `1700x1200`
- Road motif: `stone_switchback`
- Road signature: `mountain_switchback_southwest_northeast`
- Composition focal point: `[0.53, 0.5]`
- Seam connectors: `{'north': [1156, 96], 'south': [527, 1104], 'east': [1564, 432], 'west': [136, 864]}`
- Space brief: Stone switchback trail with clear elevation rhythm. The path should feel climbable and continuous, not a decorative zigzag over cliffs.

### Road contract

- `switchback_steps` / role `mountain_switchback` / width `44px` / points: (527, 1104), (561, 912), (935, 792), (714, 636), (1122, 516), (1564, 432), (1156, 96)

### Object-zone contract

- No required object-zone rectangles in manifest; preserve the road motif and leave walkable gaps around major props.

### Registration contract

- `painted_source` is the only composition source for this region.
- All runtime layers must keep the full canvas, origin `(0, 0)`, scale `1`, rotation `0`, and the same 3/4 perspective as `painted_source`.
- Roads and object zones should follow the manifest structure and remain spatially readable; natural hand-painted edge variation is allowed.
- Details such as grass, flowers, pebbles, leaves, and brush texture do not need pixel-perfect correspondence to manifest points.

### Asset requests

#### 1. mountain_path_painted_source

- 文件路径：
```text
01_mother_images/regions/mountain_path/mountain_path_painted_source.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/01_mother_images/regions/mountain_path/mountain_path_painted_source.png
```

- 尺寸：`1700x1200`
- Alpha：`fully opaque PNG`
- Layer brief: complete region source/review mother; fully painted composite for judging layout, mood, object placement, and seam readiness.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint a complete region source/review mother for mountain_path_painted_source; exact canvas 1700x1200 px; fully opaque complete review image; believable village-space layout, readable roads, props beside paths, no impossible overlaps. Region-specific requirement: Stone switchback trail with clear elevation rhythm. The path should feel climbable and continuous, not a decorative zigzag over cliffs. Layer requirement: complete region source/review mother; fully painted composite for judging layout, mood, object placement, and seam readiness. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 2. mountain_path_base_ground

- 文件路径：
```text
02_runtime_exports/regions/mountain_path/layers/mountain_path_base_ground.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/mountain_path/layers/mountain_path_base_ground.png
```

- 尺寸：`1700x1200`
- Alpha：`fully opaque PNG`
- Layer brief: opaque base layer only: terrain, roads, water/soil/stone base, and walkable ground shapes; no tall props or foreground occluders.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for mountain_path_base_ground; exact canvas 1700x1200 px; fully opaque complete review image; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Stone switchback trail with clear elevation rhythm. The path should feel climbable and continuous, not a decorative zigzag over cliffs. Layer requirement: opaque base layer only: terrain, roads, water/soil/stone base, and walkable ground shapes; no tall props or foreground occluders. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 3. mountain_path_terrain_details

- 文件路径：
```text
02_runtime_exports/regions/mountain_path/layers/mountain_path_terrain_details.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/mountain_path/layers/mountain_path_terrain_details.png
```

- 尺寸：`1700x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent detail layer: grass tufts, soil accents, small stones, leaves, and local texture variation; no blocking objects.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for mountain_path_terrain_details; exact canvas 1700x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Stone switchback trail with clear elevation rhythm. The path should feel climbable and continuous, not a decorative zigzag over cliffs. Layer requirement: transparent detail layer: grass tufts, soil accents, small stones, leaves, and local texture variation; no blocking objects. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 4. mountain_path_behind_player_structures

- 文件路径：
```text
02_runtime_exports/regions/mountain_path/layers/mountain_path_behind_player_structures.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/mountain_path/layers/mountain_path_behind_player_structures.png
```

- 尺寸：`1700x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent back/depth layer: walls, upper structures, distant tree masses, slopes, and forms that should render behind the player.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for mountain_path_behind_player_structures; exact canvas 1700x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Stone switchback trail with clear elevation rhythm. The path should feel climbable and continuous, not a decorative zigzag over cliffs. Layer requirement: transparent back/depth layer: walls, upper structures, distant tree masses, slopes, and forms that should render behind the player. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 5. mountain_path_ysort_props_structures

- 文件路径：
```text
02_runtime_exports/regions/mountain_path/layers/mountain_path_ysort_props_structures.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/mountain_path/layers/mountain_path_ysort_props_structures.png
```

- 尺寸：`1700x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent interactive/depth layer: readable props, structures, crops, benches, wells, doors, rocks, or trees with bottom anchors for Y-sort.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for mountain_path_ysort_props_structures; exact canvas 1700x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Stone switchback trail with clear elevation rhythm. The path should feel climbable and continuous, not a decorative zigzag over cliffs. Layer requirement: transparent interactive/depth layer: readable props, structures, crops, benches, wells, doors, rocks, or trees with bottom anchors for Y-sort. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 6. mountain_path_foreground_occlusion

- 文件路径：
```text
02_runtime_exports/regions/mountain_path/layers/mountain_path_foreground_occlusion.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/mountain_path/layers/mountain_path_foreground_occlusion.png
```

- 尺寸：`1700x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent foreground layer: sparse canopy, front eaves, tall grass, rails, or ledge fronts that may pass in front of the player.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for mountain_path_foreground_occlusion; exact canvas 1700x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Stone switchback trail with clear elevation rhythm. The path should feel climbable and continuous, not a decorative zigzag over cliffs. Layer requirement: transparent foreground layer: sparse canopy, front eaves, tall grass, rails, or ledge fronts that may pass in front of the player. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 7. mountain_path_shadow_overlay

- 文件路径：
```text
02_runtime_exports/regions/mountain_path/layers/mountain_path_shadow_overlay.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/mountain_path/layers/mountain_path_shadow_overlay.png
```

- 尺寸：`1700x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent soft shadow layer: contact shadows and grounding shadows only; avoid heavy black shadows.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for mountain_path_shadow_overlay; exact canvas 1700x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Stone switchback trail with clear elevation rhythm. The path should feel climbable and continuous, not a decorative zigzag over cliffs. Layer requirement: transparent soft shadow layer: contact shadows and grounding shadows only; avoid heavy black shadows. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 8. mountain_path_light_weather_overlay_spring

- 文件路径：
```text
02_runtime_exports/regions/mountain_path/layers/mountain_path_light_weather_overlay_spring.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/mountain_path/layers/mountain_path_light_weather_overlay_spring.png
```

- 尺寸：`1700x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent spring overlay: subtle warm light, fresh foliage hints, soft pollen or blossom accents.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for mountain_path_light_weather_overlay_spring; exact canvas 1700x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Stone switchback trail with clear elevation rhythm. The path should feel climbable and continuous, not a decorative zigzag over cliffs. Layer requirement: transparent spring overlay: subtle warm light, fresh foliage hints, soft pollen or blossom accents. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 9. mountain_path_light_weather_overlay_summer

- 文件路径：
```text
02_runtime_exports/regions/mountain_path/layers/mountain_path_light_weather_overlay_summer.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/mountain_path/layers/mountain_path_light_weather_overlay_summer.png
```

- 尺寸：`1700x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent summer overlay: gentle warmer light, fuller foliage accents, soft humid atmosphere.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for mountain_path_light_weather_overlay_summer; exact canvas 1700x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Stone switchback trail with clear elevation rhythm. The path should feel climbable and continuous, not a decorative zigzag over cliffs. Layer requirement: transparent summer overlay: gentle warmer light, fuller foliage accents, soft humid atmosphere. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 10. mountain_path_light_weather_overlay_autumn

- 文件路径：
```text
02_runtime_exports/regions/mountain_path/layers/mountain_path_light_weather_overlay_autumn.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/mountain_path/layers/mountain_path_light_weather_overlay_autumn.png
```

- 尺寸：`1700x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent autumn overlay: low-saturation fallen leaves and mellow golden light.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for mountain_path_light_weather_overlay_autumn; exact canvas 1700x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Stone switchback trail with clear elevation rhythm. The path should feel climbable and continuous, not a decorative zigzag over cliffs. Layer requirement: transparent autumn overlay: low-saturation fallen leaves and mellow golden light. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 11. mountain_path_light_weather_overlay_winter

- 文件路径：
```text
02_runtime_exports/regions/mountain_path/layers/mountain_path_light_weather_overlay_winter.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/mountain_path/layers/mountain_path_light_weather_overlay_winter.png
```

- 尺寸：`1700x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent winter overlay: light snow dusting or cool seasonal tint while preserving path readability.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for mountain_path_light_weather_overlay_winter; exact canvas 1700x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Stone switchback trail with clear elevation rhythm. The path should feel climbable and continuous, not a decorative zigzag over cliffs. Layer requirement: transparent winter overlay: light snow dusting or cool seasonal tint while preserving path readability. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

## Region: mountain_hut / MountainHut

- Canvas: `1500x1050`
- Road motif: `hut_arrival_path`
- Road signature: `hut_curved_arrival_west_south`
- Composition focal point: `[0.46, 0.44]`
- Seam connectors: `{'north': [690, 84], 'south': [525, 966], 'east': [1380, 693], 'west': [120, 598]}`
- Space brief: Quiet hut workyard with curved arrival path, porch, herb patch, woodpile side path, and ridge link. The hut should not block the access path.

### Road contract

- `hut_arrival_curve` / role `mountain_hut_access` / width `45px` / points: (525, 966), (510, 609), (690, 609), (690, 451)
- `woodpile_side_path` / role `workyard_path` / width `31px` / points: (120, 598), (690, 609), (990, 672), (1380, 693)
- `ridge_arrival_path` / role `ridge_link` / width `26px` / points: (690, 84), (690, 609)

### Object-zone contract

- No required object-zone rectangles in manifest; preserve the road motif and leave walkable gaps around major props.

### Registration contract

- `painted_source` is the only composition source for this region.
- All runtime layers must keep the full canvas, origin `(0, 0)`, scale `1`, rotation `0`, and the same 3/4 perspective as `painted_source`.
- Roads and object zones should follow the manifest structure and remain spatially readable; natural hand-painted edge variation is allowed.
- Details such as grass, flowers, pebbles, leaves, and brush texture do not need pixel-perfect correspondence to manifest points.

### Asset requests

#### 1. mountain_hut_painted_source

- 文件路径：
```text
01_mother_images/regions/mountain_hut/mountain_hut_painted_source.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/01_mother_images/regions/mountain_hut/mountain_hut_painted_source.png
```

- 尺寸：`1500x1050`
- Alpha：`fully opaque PNG`
- Layer brief: complete region source/review mother; fully painted composite for judging layout, mood, object placement, and seam readiness.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint a complete region source/review mother for mountain_hut_painted_source; exact canvas 1500x1050 px; fully opaque complete review image; believable village-space layout, readable roads, props beside paths, no impossible overlaps. Region-specific requirement: Quiet hut workyard with curved arrival path, porch, herb patch, woodpile side path, and ridge link. The hut should not block the access path. Layer requirement: complete region source/review mother; fully painted composite for judging layout, mood, object placement, and seam readiness. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 2. mountain_hut_base_ground

- 文件路径：
```text
02_runtime_exports/regions/mountain_hut/layers/mountain_hut_base_ground.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/mountain_hut/layers/mountain_hut_base_ground.png
```

- 尺寸：`1500x1050`
- Alpha：`fully opaque PNG`
- Layer brief: opaque base layer only: terrain, roads, water/soil/stone base, and walkable ground shapes; no tall props or foreground occluders.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for mountain_hut_base_ground; exact canvas 1500x1050 px; fully opaque complete review image; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Quiet hut workyard with curved arrival path, porch, herb patch, woodpile side path, and ridge link. The hut should not block the access path. Layer requirement: opaque base layer only: terrain, roads, water/soil/stone base, and walkable ground shapes; no tall props or foreground occluders. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 3. mountain_hut_terrain_details

- 文件路径：
```text
02_runtime_exports/regions/mountain_hut/layers/mountain_hut_terrain_details.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/mountain_hut/layers/mountain_hut_terrain_details.png
```

- 尺寸：`1500x1050`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent detail layer: grass tufts, soil accents, small stones, leaves, and local texture variation; no blocking objects.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for mountain_hut_terrain_details; exact canvas 1500x1050 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Quiet hut workyard with curved arrival path, porch, herb patch, woodpile side path, and ridge link. The hut should not block the access path. Layer requirement: transparent detail layer: grass tufts, soil accents, small stones, leaves, and local texture variation; no blocking objects. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 4. mountain_hut_behind_player_structures

- 文件路径：
```text
02_runtime_exports/regions/mountain_hut/layers/mountain_hut_behind_player_structures.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/mountain_hut/layers/mountain_hut_behind_player_structures.png
```

- 尺寸：`1500x1050`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent back/depth layer: walls, upper structures, distant tree masses, slopes, and forms that should render behind the player.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for mountain_hut_behind_player_structures; exact canvas 1500x1050 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Quiet hut workyard with curved arrival path, porch, herb patch, woodpile side path, and ridge link. The hut should not block the access path. Layer requirement: transparent back/depth layer: walls, upper structures, distant tree masses, slopes, and forms that should render behind the player. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 5. mountain_hut_ysort_props_structures

- 文件路径：
```text
02_runtime_exports/regions/mountain_hut/layers/mountain_hut_ysort_props_structures.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/mountain_hut/layers/mountain_hut_ysort_props_structures.png
```

- 尺寸：`1500x1050`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent interactive/depth layer: readable props, structures, crops, benches, wells, doors, rocks, or trees with bottom anchors for Y-sort.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for mountain_hut_ysort_props_structures; exact canvas 1500x1050 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Quiet hut workyard with curved arrival path, porch, herb patch, woodpile side path, and ridge link. The hut should not block the access path. Layer requirement: transparent interactive/depth layer: readable props, structures, crops, benches, wells, doors, rocks, or trees with bottom anchors for Y-sort. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 6. mountain_hut_foreground_occlusion

- 文件路径：
```text
02_runtime_exports/regions/mountain_hut/layers/mountain_hut_foreground_occlusion.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/mountain_hut/layers/mountain_hut_foreground_occlusion.png
```

- 尺寸：`1500x1050`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent foreground layer: sparse canopy, front eaves, tall grass, rails, or ledge fronts that may pass in front of the player.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for mountain_hut_foreground_occlusion; exact canvas 1500x1050 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Quiet hut workyard with curved arrival path, porch, herb patch, woodpile side path, and ridge link. The hut should not block the access path. Layer requirement: transparent foreground layer: sparse canopy, front eaves, tall grass, rails, or ledge fronts that may pass in front of the player. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 7. mountain_hut_shadow_overlay

- 文件路径：
```text
02_runtime_exports/regions/mountain_hut/layers/mountain_hut_shadow_overlay.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/mountain_hut/layers/mountain_hut_shadow_overlay.png
```

- 尺寸：`1500x1050`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent soft shadow layer: contact shadows and grounding shadows only; avoid heavy black shadows.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for mountain_hut_shadow_overlay; exact canvas 1500x1050 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Quiet hut workyard with curved arrival path, porch, herb patch, woodpile side path, and ridge link. The hut should not block the access path. Layer requirement: transparent soft shadow layer: contact shadows and grounding shadows only; avoid heavy black shadows. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 8. mountain_hut_light_weather_overlay_spring

- 文件路径：
```text
02_runtime_exports/regions/mountain_hut/layers/mountain_hut_light_weather_overlay_spring.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/mountain_hut/layers/mountain_hut_light_weather_overlay_spring.png
```

- 尺寸：`1500x1050`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent spring overlay: subtle warm light, fresh foliage hints, soft pollen or blossom accents.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for mountain_hut_light_weather_overlay_spring; exact canvas 1500x1050 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Quiet hut workyard with curved arrival path, porch, herb patch, woodpile side path, and ridge link. The hut should not block the access path. Layer requirement: transparent spring overlay: subtle warm light, fresh foliage hints, soft pollen or blossom accents. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 9. mountain_hut_light_weather_overlay_summer

- 文件路径：
```text
02_runtime_exports/regions/mountain_hut/layers/mountain_hut_light_weather_overlay_summer.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/mountain_hut/layers/mountain_hut_light_weather_overlay_summer.png
```

- 尺寸：`1500x1050`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent summer overlay: gentle warmer light, fuller foliage accents, soft humid atmosphere.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for mountain_hut_light_weather_overlay_summer; exact canvas 1500x1050 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Quiet hut workyard with curved arrival path, porch, herb patch, woodpile side path, and ridge link. The hut should not block the access path. Layer requirement: transparent summer overlay: gentle warmer light, fuller foliage accents, soft humid atmosphere. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 10. mountain_hut_light_weather_overlay_autumn

- 文件路径：
```text
02_runtime_exports/regions/mountain_hut/layers/mountain_hut_light_weather_overlay_autumn.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/mountain_hut/layers/mountain_hut_light_weather_overlay_autumn.png
```

- 尺寸：`1500x1050`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent autumn overlay: low-saturation fallen leaves and mellow golden light.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for mountain_hut_light_weather_overlay_autumn; exact canvas 1500x1050 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Quiet hut workyard with curved arrival path, porch, herb patch, woodpile side path, and ridge link. The hut should not block the access path. Layer requirement: transparent autumn overlay: low-saturation fallen leaves and mellow golden light. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 11. mountain_hut_light_weather_overlay_winter

- 文件路径：
```text
02_runtime_exports/regions/mountain_hut/layers/mountain_hut_light_weather_overlay_winter.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/mountain_hut/layers/mountain_hut_light_weather_overlay_winter.png
```

- 尺寸：`1500x1050`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent winter overlay: light snow dusting or cool seasonal tint while preserving path readability.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for mountain_hut_light_weather_overlay_winter; exact canvas 1500x1050 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Quiet hut workyard with curved arrival path, porch, herb patch, woodpile side path, and ridge link. The hut should not block the access path. Layer requirement: transparent winter overlay: light snow dusting or cool seasonal tint while preserving path readability. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

## Region: mountain / Mountain

- Canvas: `1800x1200`
- Road motif: `rocky_trail`
- Road signature: `mountain_uneven_trail_stream_crossing`
- Composition focal point: `[0.56, 0.5]`
- Seam connectors: `{'north': [1080, 96], 'south': [864, 1104], 'east': [1656, 491], 'west': [144, 792]}`
- Space brief: Rocky trail and stream crossing with a clearing spur and hut descent. Rocks frame the path while preserving traversable continuity.

### Road contract

- `rocky_stream_crossing` / role `rocky_trail` / width `45px` / points: (144, 792), (450, 816), (774, 744), (1044, 612), (1350, 468), (1656, 491)
- `clearing_spur` / role `clearing_spur` / width `34px` / points: (1044, 612), (1116, 432), (1080, 96)
- `hut_descent` / role `ridge_link` / width `32px` / points: (774, 744), (864, 1104)

### Object-zone contract

- No required object-zone rectangles in manifest; preserve the road motif and leave walkable gaps around major props.

### Registration contract

- `painted_source` is the only composition source for this region.
- All runtime layers must keep the full canvas, origin `(0, 0)`, scale `1`, rotation `0`, and the same 3/4 perspective as `painted_source`.
- Roads and object zones should follow the manifest structure and remain spatially readable; natural hand-painted edge variation is allowed.
- Details such as grass, flowers, pebbles, leaves, and brush texture do not need pixel-perfect correspondence to manifest points.

### Asset requests

#### 1. mountain_painted_source

- 文件路径：
```text
01_mother_images/regions/mountain/mountain_painted_source.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/01_mother_images/regions/mountain/mountain_painted_source.png
```

- 尺寸：`1800x1200`
- Alpha：`fully opaque PNG`
- Layer brief: complete region source/review mother; fully painted composite for judging layout, mood, object placement, and seam readiness.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint a complete region source/review mother for mountain_painted_source; exact canvas 1800x1200 px; fully opaque complete review image; believable village-space layout, readable roads, props beside paths, no impossible overlaps. Region-specific requirement: Rocky trail and stream crossing with a clearing spur and hut descent. Rocks frame the path while preserving traversable continuity. Layer requirement: complete region source/review mother; fully painted composite for judging layout, mood, object placement, and seam readiness. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 2. mountain_base_ground

- 文件路径：
```text
02_runtime_exports/regions/mountain/layers/mountain_base_ground.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/mountain/layers/mountain_base_ground.png
```

- 尺寸：`1800x1200`
- Alpha：`fully opaque PNG`
- Layer brief: opaque base layer only: terrain, roads, water/soil/stone base, and walkable ground shapes; no tall props or foreground occluders.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for mountain_base_ground; exact canvas 1800x1200 px; fully opaque complete review image; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Rocky trail and stream crossing with a clearing spur and hut descent. Rocks frame the path while preserving traversable continuity. Layer requirement: opaque base layer only: terrain, roads, water/soil/stone base, and walkable ground shapes; no tall props or foreground occluders. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 3. mountain_terrain_details

- 文件路径：
```text
02_runtime_exports/regions/mountain/layers/mountain_terrain_details.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/mountain/layers/mountain_terrain_details.png
```

- 尺寸：`1800x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent detail layer: grass tufts, soil accents, small stones, leaves, and local texture variation; no blocking objects.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for mountain_terrain_details; exact canvas 1800x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Rocky trail and stream crossing with a clearing spur and hut descent. Rocks frame the path while preserving traversable continuity. Layer requirement: transparent detail layer: grass tufts, soil accents, small stones, leaves, and local texture variation; no blocking objects. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 4. mountain_behind_player_structures

- 文件路径：
```text
02_runtime_exports/regions/mountain/layers/mountain_behind_player_structures.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/mountain/layers/mountain_behind_player_structures.png
```

- 尺寸：`1800x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent back/depth layer: walls, upper structures, distant tree masses, slopes, and forms that should render behind the player.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for mountain_behind_player_structures; exact canvas 1800x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Rocky trail and stream crossing with a clearing spur and hut descent. Rocks frame the path while preserving traversable continuity. Layer requirement: transparent back/depth layer: walls, upper structures, distant tree masses, slopes, and forms that should render behind the player. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 5. mountain_ysort_props_structures

- 文件路径：
```text
02_runtime_exports/regions/mountain/layers/mountain_ysort_props_structures.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/mountain/layers/mountain_ysort_props_structures.png
```

- 尺寸：`1800x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent interactive/depth layer: readable props, structures, crops, benches, wells, doors, rocks, or trees with bottom anchors for Y-sort.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for mountain_ysort_props_structures; exact canvas 1800x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Rocky trail and stream crossing with a clearing spur and hut descent. Rocks frame the path while preserving traversable continuity. Layer requirement: transparent interactive/depth layer: readable props, structures, crops, benches, wells, doors, rocks, or trees with bottom anchors for Y-sort. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 6. mountain_foreground_occlusion

- 文件路径：
```text
02_runtime_exports/regions/mountain/layers/mountain_foreground_occlusion.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/mountain/layers/mountain_foreground_occlusion.png
```

- 尺寸：`1800x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent foreground layer: sparse canopy, front eaves, tall grass, rails, or ledge fronts that may pass in front of the player.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for mountain_foreground_occlusion; exact canvas 1800x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Rocky trail and stream crossing with a clearing spur and hut descent. Rocks frame the path while preserving traversable continuity. Layer requirement: transparent foreground layer: sparse canopy, front eaves, tall grass, rails, or ledge fronts that may pass in front of the player. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 7. mountain_shadow_overlay

- 文件路径：
```text
02_runtime_exports/regions/mountain/layers/mountain_shadow_overlay.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/mountain/layers/mountain_shadow_overlay.png
```

- 尺寸：`1800x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent soft shadow layer: contact shadows and grounding shadows only; avoid heavy black shadows.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for mountain_shadow_overlay; exact canvas 1800x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Rocky trail and stream crossing with a clearing spur and hut descent. Rocks frame the path while preserving traversable continuity. Layer requirement: transparent soft shadow layer: contact shadows and grounding shadows only; avoid heavy black shadows. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 8. mountain_light_weather_overlay_spring

- 文件路径：
```text
02_runtime_exports/regions/mountain/layers/mountain_light_weather_overlay_spring.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/mountain/layers/mountain_light_weather_overlay_spring.png
```

- 尺寸：`1800x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent spring overlay: subtle warm light, fresh foliage hints, soft pollen or blossom accents.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for mountain_light_weather_overlay_spring; exact canvas 1800x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Rocky trail and stream crossing with a clearing spur and hut descent. Rocks frame the path while preserving traversable continuity. Layer requirement: transparent spring overlay: subtle warm light, fresh foliage hints, soft pollen or blossom accents. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 9. mountain_light_weather_overlay_summer

- 文件路径：
```text
02_runtime_exports/regions/mountain/layers/mountain_light_weather_overlay_summer.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/mountain/layers/mountain_light_weather_overlay_summer.png
```

- 尺寸：`1800x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent summer overlay: gentle warmer light, fuller foliage accents, soft humid atmosphere.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for mountain_light_weather_overlay_summer; exact canvas 1800x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Rocky trail and stream crossing with a clearing spur and hut descent. Rocks frame the path while preserving traversable continuity. Layer requirement: transparent summer overlay: gentle warmer light, fuller foliage accents, soft humid atmosphere. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 10. mountain_light_weather_overlay_autumn

- 文件路径：
```text
02_runtime_exports/regions/mountain/layers/mountain_light_weather_overlay_autumn.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/mountain/layers/mountain_light_weather_overlay_autumn.png
```

- 尺寸：`1800x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent autumn overlay: low-saturation fallen leaves and mellow golden light.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for mountain_light_weather_overlay_autumn; exact canvas 1800x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Rocky trail and stream crossing with a clearing spur and hut descent. Rocks frame the path while preserving traversable continuity. Layer requirement: transparent autumn overlay: low-saturation fallen leaves and mellow golden light. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 11. mountain_light_weather_overlay_winter

- 文件路径：
```text
02_runtime_exports/regions/mountain/layers/mountain_light_weather_overlay_winter.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/mountain/layers/mountain_light_weather_overlay_winter.png
```

- 尺寸：`1800x1200`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent winter overlay: light snow dusting or cool seasonal tint while preserving path readability.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for mountain_light_weather_overlay_winter; exact canvas 1800x1200 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Rocky trail and stream crossing with a clearing spur and hut descent. Rocks frame the path while preserving traversable continuity. Layer requirement: transparent winter overlay: light snow dusting or cool seasonal tint while preserving path readability. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

## Region: cliff_view / CliffView

- Canvas: `1500x1000`
- Road motif: `ledge_contour`
- Road signature: `cliff_contour_ledge_path`
- Composition focal point: `[0.5, 0.62]`
- Seam connectors: `{'north': [660, 80], 'south': [810, 920], 'east': [1380, 470], 'west': [120, 540]}`
- Space brief: Cliff overlook with contour ledge path and rest/view spur. The walking area must read as safe ground, with the vista beyond it.

### Road contract

- `contour_ledge` / role `cliff_ledge_path` / width `43px` / points: (120, 540), (270, 530), (570, 570), (735, 610), (885, 550), (1200, 480), (1380, 470)
- `south_view_spur` / role `view_rest_access` / width `31px` / points: (810, 920), (735, 610)

### Object-zone contract

- No required object-zone rectangles in manifest; preserve the road motif and leave walkable gaps around major props.

### Registration contract

- `painted_source` is the only composition source for this region.
- All runtime layers must keep the full canvas, origin `(0, 0)`, scale `1`, rotation `0`, and the same 3/4 perspective as `painted_source`.
- Roads and object zones should follow the manifest structure and remain spatially readable; natural hand-painted edge variation is allowed.
- Details such as grass, flowers, pebbles, leaves, and brush texture do not need pixel-perfect correspondence to manifest points.

### Asset requests

#### 1. cliff_view_painted_source

- 文件路径：
```text
01_mother_images/regions/cliff_view/cliff_view_painted_source.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/01_mother_images/regions/cliff_view/cliff_view_painted_source.png
```

- 尺寸：`1500x1000`
- Alpha：`fully opaque PNG`
- Layer brief: complete region source/review mother; fully painted composite for judging layout, mood, object placement, and seam readiness.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint a complete region source/review mother for cliff_view_painted_source; exact canvas 1500x1000 px; fully opaque complete review image; believable village-space layout, readable roads, props beside paths, no impossible overlaps. Region-specific requirement: Cliff overlook with contour ledge path and rest/view spur. The walking area must read as safe ground, with the vista beyond it. Layer requirement: complete region source/review mother; fully painted composite for judging layout, mood, object placement, and seam readiness. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 2. cliff_view_base_ground

- 文件路径：
```text
02_runtime_exports/regions/cliff_view/layers/cliff_view_base_ground.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/cliff_view/layers/cliff_view_base_ground.png
```

- 尺寸：`1500x1000`
- Alpha：`fully opaque PNG`
- Layer brief: opaque base layer only: terrain, roads, water/soil/stone base, and walkable ground shapes; no tall props or foreground occluders.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for cliff_view_base_ground; exact canvas 1500x1000 px; fully opaque complete review image; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Cliff overlook with contour ledge path and rest/view spur. The walking area must read as safe ground, with the vista beyond it. Layer requirement: opaque base layer only: terrain, roads, water/soil/stone base, and walkable ground shapes; no tall props or foreground occluders. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 3. cliff_view_terrain_details

- 文件路径：
```text
02_runtime_exports/regions/cliff_view/layers/cliff_view_terrain_details.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/cliff_view/layers/cliff_view_terrain_details.png
```

- 尺寸：`1500x1000`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent detail layer: grass tufts, soil accents, small stones, leaves, and local texture variation; no blocking objects.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for cliff_view_terrain_details; exact canvas 1500x1000 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Cliff overlook with contour ledge path and rest/view spur. The walking area must read as safe ground, with the vista beyond it. Layer requirement: transparent detail layer: grass tufts, soil accents, small stones, leaves, and local texture variation; no blocking objects. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 4. cliff_view_behind_player_structures

- 文件路径：
```text
02_runtime_exports/regions/cliff_view/layers/cliff_view_behind_player_structures.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/cliff_view/layers/cliff_view_behind_player_structures.png
```

- 尺寸：`1500x1000`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent back/depth layer: walls, upper structures, distant tree masses, slopes, and forms that should render behind the player.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for cliff_view_behind_player_structures; exact canvas 1500x1000 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Cliff overlook with contour ledge path and rest/view spur. The walking area must read as safe ground, with the vista beyond it. Layer requirement: transparent back/depth layer: walls, upper structures, distant tree masses, slopes, and forms that should render behind the player. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 5. cliff_view_ysort_props_structures

- 文件路径：
```text
02_runtime_exports/regions/cliff_view/layers/cliff_view_ysort_props_structures.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/cliff_view/layers/cliff_view_ysort_props_structures.png
```

- 尺寸：`1500x1000`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent interactive/depth layer: readable props, structures, crops, benches, wells, doors, rocks, or trees with bottom anchors for Y-sort.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for cliff_view_ysort_props_structures; exact canvas 1500x1000 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Cliff overlook with contour ledge path and rest/view spur. The walking area must read as safe ground, with the vista beyond it. Layer requirement: transparent interactive/depth layer: readable props, structures, crops, benches, wells, doors, rocks, or trees with bottom anchors for Y-sort. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 6. cliff_view_foreground_occlusion

- 文件路径：
```text
02_runtime_exports/regions/cliff_view/layers/cliff_view_foreground_occlusion.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/cliff_view/layers/cliff_view_foreground_occlusion.png
```

- 尺寸：`1500x1000`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent foreground layer: sparse canopy, front eaves, tall grass, rails, or ledge fronts that may pass in front of the player.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for cliff_view_foreground_occlusion; exact canvas 1500x1000 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Cliff overlook with contour ledge path and rest/view spur. The walking area must read as safe ground, with the vista beyond it. Layer requirement: transparent foreground layer: sparse canopy, front eaves, tall grass, rails, or ledge fronts that may pass in front of the player. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 7. cliff_view_shadow_overlay

- 文件路径：
```text
02_runtime_exports/regions/cliff_view/layers/cliff_view_shadow_overlay.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/cliff_view/layers/cliff_view_shadow_overlay.png
```

- 尺寸：`1500x1000`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent soft shadow layer: contact shadows and grounding shadows only; avoid heavy black shadows.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for cliff_view_shadow_overlay; exact canvas 1500x1000 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Cliff overlook with contour ledge path and rest/view spur. The walking area must read as safe ground, with the vista beyond it. Layer requirement: transparent soft shadow layer: contact shadows and grounding shadows only; avoid heavy black shadows. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 8. cliff_view_light_weather_overlay_spring

- 文件路径：
```text
02_runtime_exports/regions/cliff_view/layers/cliff_view_light_weather_overlay_spring.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/cliff_view/layers/cliff_view_light_weather_overlay_spring.png
```

- 尺寸：`1500x1000`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent spring overlay: subtle warm light, fresh foliage hints, soft pollen or blossom accents.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for cliff_view_light_weather_overlay_spring; exact canvas 1500x1000 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Cliff overlook with contour ledge path and rest/view spur. The walking area must read as safe ground, with the vista beyond it. Layer requirement: transparent spring overlay: subtle warm light, fresh foliage hints, soft pollen or blossom accents. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 9. cliff_view_light_weather_overlay_summer

- 文件路径：
```text
02_runtime_exports/regions/cliff_view/layers/cliff_view_light_weather_overlay_summer.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/cliff_view/layers/cliff_view_light_weather_overlay_summer.png
```

- 尺寸：`1500x1000`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent summer overlay: gentle warmer light, fuller foliage accents, soft humid atmosphere.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for cliff_view_light_weather_overlay_summer; exact canvas 1500x1000 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Cliff overlook with contour ledge path and rest/view spur. The walking area must read as safe ground, with the vista beyond it. Layer requirement: transparent summer overlay: gentle warmer light, fuller foliage accents, soft humid atmosphere. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 10. cliff_view_light_weather_overlay_autumn

- 文件路径：
```text
02_runtime_exports/regions/cliff_view/layers/cliff_view_light_weather_overlay_autumn.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/cliff_view/layers/cliff_view_light_weather_overlay_autumn.png
```

- 尺寸：`1500x1000`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent autumn overlay: low-saturation fallen leaves and mellow golden light.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for cliff_view_light_weather_overlay_autumn; exact canvas 1500x1000 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Cliff overlook with contour ledge path and rest/view spur. The walking area must read as safe ground, with the vista beyond it. Layer requirement: transparent autumn overlay: low-saturation fallen leaves and mellow golden light. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

#### 11. cliff_view_light_weather_overlay_winter

- 文件路径：
```text
02_runtime_exports/regions/cliff_view/layers/cliff_view_light_weather_overlay_winter.png
```

- 完整放置路径：
```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_runtime_exports/regions/cliff_view/layers/cliff_view_light_weather_overlay_winter.png
```

- 尺寸：`1500x1000`
- Alpha：`transparent PNG with clean alpha`
- Layer brief: transparent winter overlay: light snow dusting or cool seasonal tint while preserving path readability.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Paint one modular region runtime layer for cliff_view_light_weather_overlay_winter; exact canvas 1500x1000 px; transparent background with clean alpha; keep the fixed 3/4 top-down world perspective, reusable layer edges, and no UI text. Region-specific requirement: Cliff overlook with contour ledge path and rest/view spur. The walking area must read as safe ground, with the vista beyond it. Layer requirement: transparent winter overlay: light snow dusting or cool seasonal tint while preserving path readability. Preserve road contract, object-zone logic, seam connector readability, and registration-perfect layer alignment: same full canvas, origin, scale, rotation, perspective, and composition as the region painted_source. Use manifest points as a layout guide, not as a demand that every hand-painted edge follows exact pixels.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

## 本批验收标准

- 110 张 PNG 全部按路径放入 `incoming/`。
- 文件尺寸必须与条目完全一致。
- `painted_source` 和 `base_ground` 不透明；其他 runtime layers 保持透明背景。
- 所有透明 layers 必须保留完整区域画布，不裁切、不缩放、不自动贴边。
- 同一区域所有 layers 必须 registration-perfect：像素级同画布、同原点、同透视、同坐标系，不能出现单层偏移、缩放、旋转或透视变化。
- 道路中心线建议严格跟随 manifest 的结构和功能关系，但手绘边缘允许自然浮动；草、花、石头等细节不做像素级锁死。
- 每个区域的道路和对象关系必须符合本文件的 road/object-zone contract，且 runtime layers 必须从确认后的母图构图拆出。
- 不得出现房子压路、水井隔十字路口、田地压路、路径被装饰物截断、过度工整中心构图、十区域同模板等问题。
- 不得包含水印、模型签名、乱码文字、UI 文本、战斗元素、科幻 HUD 或命名 IP 风格复刻。
