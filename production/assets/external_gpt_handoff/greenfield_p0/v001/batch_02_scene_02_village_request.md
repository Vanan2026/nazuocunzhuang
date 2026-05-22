# Batch 02 / Scene 02 - Village Registration-Perfect Region Request

用途：这是第 2 批区域资产中的单场景执行文件。它替代 110 张大批文件作为本次外部生产输入。

核心标准：`registration-perfect` 图层注册一致；不是按 manifest 坐标逐像素描摹美术笔触。

验收命令：

```powershell
py -3.12 tools\validate_greenfield_p0_external_asset_intake.py --allow-partial
```

## Global Style Lock

Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD.

## Global Negative Prompt

Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.

## Scene 02: village / Village

- Canvas: `1800x1200`
- Registration blueprint: 外部 GPT 先按本文件 `GPT Blueprint Requirement` 绘制/确认，不由 Codex 预先生图。
- Incoming root: `production/assets/external_gpt_handoff/greenfield_p0/v001/incoming`
- Road motif: `settled_village_lane`
- Road signature: `village_plaza_lane_doorstep_spurs`
- Composition focal point: `[0.55, 0.48]`
- Seam connectors: `{'north': [792, 96], 'south': [1134, 1104], 'east': [1656, 600], 'west': [144, 720]}`
- Space brief: Small lived-in village center with through lanes, a modest plaza edge, doorstep paths, and a small landmark. Houses must be set back from roads with readable door approaches, not pasted into the lane.

### Production Flow

1. Generate and confirm `painted_source` first.
2. Treat `painted_source` as the only composition source.
3. Split/mask/paint `base_ground` and transparent runtime layers from that same composition.
4. Export every PNG at the full canvas size. Do not crop, resize, rotate, or auto-trim transparent layers.
5. In Godot, every layer will be placed at position `(0, 0)`, scale `1`, rotation `0`, under the same parent.

### Registration Contract

- Required: same canvas size, origin, perspective, composition, coordinate system, pivot, scale, and rotation across all 11 PNGs.
- Required: transparent layers keep full canvas alpha outside painted pixels.
- Required: houses, shrine, bench, doors, roads, shadows, and foreground occlusion must align when stacked.
- Guide: manifest road points, road widths, object rectangles, and seam connectors define spatial logic.
- Allowed: natural hand-painted variation on road edges, grass, flowers, pebbles, leaves, and texture marks.

### GPT Blueprint Requirement

- 在生成 `painted_source` 之前，请先由外部 GPT 绘制一张 registration blueprint / engineering diagram。
- Blueprint 画布也是 `1800x1200`，用来确认构图注册，不作为 Godot runtime asset。
- Blueprint 应清楚标注：canvas 边界、主路/支路、road role、road width、object-zone rect、seam connector、composition focal point、完整画布导出规则。
- Blueprint 可以比 Codex 程序图更美观，但必须表达同一个空间逻辑：房子退到路外、门口可达、bench 不在路中心、shrine 有窄入口、道路不断裂。
- Blueprint 确认后，再生成 `village_painted_source`；所有 runtime layers 从该母图拆层/遮罩/补绘。

### Road Contract

- `village_main_lane` / role `village_through_lane` / width `50px` / points: (144, 720), (864, 816), (1152, 744), (1656, 600)
- `north_lane` / role `village_through_lane` / width `41px` / points: (792, 96), (774, 600), (1080, 588)
- `south_lane` / role `village_through_lane` / width `41px` / points: (1134, 1104), (1152, 744)
- `plaza_edge` / role `plaza_edge` / width `30px` / points: (774, 600), (1080, 588), (1152, 744), (864, 816), (774, 600)
- `left_doorstep` / role `doorstep` / width `25px` / points: (774, 600), (594, 528)
- `right_doorstep` / role `doorstep` / width `25px` / points: (1080, 588), (1224, 552)
- `shrine_step` / role `landmark_access` / width `21px` / points: (774, 600), (936, 516)

### Object-Zone Contract

- `house_a` / role `village_structure` / rect `[333, 186, 630, 438]` / relation: left house sits off the square road
- `house_b` / role `village_structure` / rect `[1206, 228, 1467, 474]` / relation: right house sits above the east spur with a small doorstep
- `shrine` / role `small_landmark` / rect `[873, 318, 999, 426]` / relation: landmark above the plaza with a narrow approach
- `bench` / role `rest_prop` / rect `[567, 870, 810, 996]` / relation: rest prop below the plaza lane, not in road center

### Runtime Layer Order For Godot

- `base_ground`: z_index 0; opaque bottom terrain/roads.
- `terrain_details`: z_index 1; transparent terrain accents.
- `behind_player_structures`: z_index 2; structures/trees behind player.
- `ysort_props_structures`: z_index 3 or later split into independent props for exact Y-sort.
- `shadow_overlay`: z_index 4; soft transparent shadow layer.
- `foreground_occlusion`: above player; foreground canopy/eaves/occluders.
- `light_weather_overlay_*`: seasonal overlay enabled one at a time.

### Asset Requests

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
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Create the confirmed painted_source mother image for village; exact canvas 1800x1200 px; fully opaque PNG. First create/confirm a registration blueprint from this request, then use it as the spatial guide. Small lived-in village center with through lanes, a modest plaza edge, doorstep paths, and a small landmark. Houses must be set back from roads with readable door approaches, not pasted into the lane. Keep roads, object zones, seam connectors, and composition readable. This image becomes the only composition source for all runtime layers.
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
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Create base_ground for village; exact canvas 1800x1200 px; fully opaque PNG. Derive/split/mask/paint this layer from the confirmed village_painted_source composition, not as a newly composed scene. Keep registration-perfect alignment: same full canvas, origin, scale, rotation, perspective, and composition. Layer requirement: opaque base layer only: terrain, roads, water/soil/stone base, and walkable ground shapes; no tall props or foreground occluders.
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
- Alpha：`transparent PNG with clean alpha; full canvas, no crop`
- Layer brief: transparent detail layer: grass tufts, soil accents, small stones, leaves, and local texture variation; no blocking objects.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Create terrain_details for village; exact canvas 1800x1200 px; transparent PNG with clean alpha; full canvas, no crop. Derive/split/mask/paint this layer from the confirmed village_painted_source composition, not as a newly composed scene. Keep registration-perfect alignment: same full canvas, origin, scale, rotation, perspective, and composition. Layer requirement: transparent detail layer: grass tufts, soil accents, small stones, leaves, and local texture variation; no blocking objects.
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
- Alpha：`transparent PNG with clean alpha; full canvas, no crop`
- Layer brief: transparent back/depth layer: walls, upper structures, distant tree masses, slopes, and forms that should render behind the player.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Create behind_player_structures for village; exact canvas 1800x1200 px; transparent PNG with clean alpha; full canvas, no crop. Derive/split/mask/paint this layer from the confirmed village_painted_source composition, not as a newly composed scene. Keep registration-perfect alignment: same full canvas, origin, scale, rotation, perspective, and composition. Layer requirement: transparent back/depth layer: walls, upper structures, distant tree masses, slopes, and forms that should render behind the player.
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
- Alpha：`transparent PNG with clean alpha; full canvas, no crop`
- Layer brief: transparent interactive/depth layer: readable props, structures, crops, benches, wells, doors, rocks, or trees with bottom anchors for Y-sort.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Create ysort_props_structures for village; exact canvas 1800x1200 px; transparent PNG with clean alpha; full canvas, no crop. Derive/split/mask/paint this layer from the confirmed village_painted_source composition, not as a newly composed scene. Keep registration-perfect alignment: same full canvas, origin, scale, rotation, perspective, and composition. Layer requirement: transparent interactive/depth layer: readable props, structures, crops, benches, wells, doors, rocks, or trees with bottom anchors for Y-sort.
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
- Alpha：`transparent PNG with clean alpha; full canvas, no crop`
- Layer brief: transparent foreground layer: sparse canopy, front eaves, tall grass, rails, or ledge fronts that may pass in front of the player.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Create foreground_occlusion for village; exact canvas 1800x1200 px; transparent PNG with clean alpha; full canvas, no crop. Derive/split/mask/paint this layer from the confirmed village_painted_source composition, not as a newly composed scene. Keep registration-perfect alignment: same full canvas, origin, scale, rotation, perspective, and composition. Layer requirement: transparent foreground layer: sparse canopy, front eaves, tall grass, rails, or ledge fronts that may pass in front of the player.
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
- Alpha：`transparent PNG with clean alpha; full canvas, no crop`
- Layer brief: transparent soft shadow layer: contact shadows and grounding shadows only; avoid heavy black shadows.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Create shadow_overlay for village; exact canvas 1800x1200 px; transparent PNG with clean alpha; full canvas, no crop. Derive/split/mask/paint this layer from the confirmed village_painted_source composition, not as a newly composed scene. Keep registration-perfect alignment: same full canvas, origin, scale, rotation, perspective, and composition. Layer requirement: transparent soft shadow layer: contact shadows and grounding shadows only; avoid heavy black shadows.
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
- Alpha：`transparent PNG with clean alpha; full canvas, no crop`
- Layer brief: transparent spring overlay: subtle warm light, fresh foliage hints, soft pollen or blossom accents.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Create light_weather_overlay_spring for village; exact canvas 1800x1200 px; transparent PNG with clean alpha; full canvas, no crop. Derive/split/mask/paint this layer from the confirmed village_painted_source composition, not as a newly composed scene. Keep registration-perfect alignment: same full canvas, origin, scale, rotation, perspective, and composition. Layer requirement: transparent spring overlay: subtle warm light, fresh foliage hints, soft pollen or blossom accents.
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
- Alpha：`transparent PNG with clean alpha; full canvas, no crop`
- Layer brief: transparent summer overlay: gentle warmer light, fuller foliage accents, soft humid atmosphere.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Create light_weather_overlay_summer for village; exact canvas 1800x1200 px; transparent PNG with clean alpha; full canvas, no crop. Derive/split/mask/paint this layer from the confirmed village_painted_source composition, not as a newly composed scene. Keep registration-perfect alignment: same full canvas, origin, scale, rotation, perspective, and composition. Layer requirement: transparent summer overlay: gentle warmer light, fuller foliage accents, soft humid atmosphere.
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
- Alpha：`transparent PNG with clean alpha; full canvas, no crop`
- Layer brief: transparent autumn overlay: low-saturation fallen leaves and mellow golden light.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Create light_weather_overlay_autumn for village; exact canvas 1800x1200 px; transparent PNG with clean alpha; full canvas, no crop. Derive/split/mask/paint this layer from the confirmed village_painted_source composition, not as a newly composed scene. Keep registration-perfect alignment: same full canvas, origin, scale, rotation, perspective, and composition. Layer requirement: transparent autumn overlay: low-saturation fallen leaves and mellow golden light.
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
- Alpha：`transparent PNG with clean alpha; full canvas, no crop`
- Layer brief: transparent winter overlay: light snow dusting or cool seasonal tint while preserving path readability.
- Prompt:

```text
Warm low-saturation storybook 2D game art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, modular assets, cozy countryside life simulation, no combat, no horror, no modern sci-fi HUD. Create light_weather_overlay_winter for village; exact canvas 1800x1200 px; transparent PNG with clean alpha; full canvas, no crop. Derive/split/mask/paint this layer from the confirmed village_painted_source composition, not as a newly composed scene. Keep registration-perfect alignment: same full canvas, origin, scale, rotation, perspective, and composition. Layer requirement: transparent winter overlay: light snow dusting or cool seasonal tint while preserving path readability.
```

- Negative:

```text
Do not copy any existing game, anime, movie, or named artist style. No photorealism, no combat, no weapons, no monsters, no aggressive expressions, no text baked into gameplay art, no harsh neon, no heavy black shadows, no random crop, no wrong perspective, no visible watermark.
```

## 本子批验收标准

- 共 11 张 PNG，全都按上方路径放入 `incoming/`。
- 11 张 PNG 全部为 `1800x1200`。
- `village_painted_source` 与 `village_base_ground` 必须完全不透明。
- 其他 9 张 runtime layers 必须透明背景、完整画布、不裁切、不缩放、不旋转。
- 所有 layers 叠加时必须对齐：房屋、shrine、bench、门口、道路、阴影、前景遮挡不能漂移。
- 道路/对象/seam 参考 blueprint 和 manifest，保持空间逻辑；手绘边缘和细节允许自然浮动。
- 不得出现房屋压路、道路穿房、bench 在路中心、shrine 堵路、路径被装饰截断、UI 文本、水印、战斗元素或科幻 HUD。
