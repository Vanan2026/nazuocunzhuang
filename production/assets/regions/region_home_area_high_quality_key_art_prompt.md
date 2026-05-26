# Region_HomeArea 高质量母图原画生产指令 v0.1

## 目标

为《那座村庄》的 `Region_HomeArea` 生产一张高质量完整场景母图，用作后续正式切片资产的唯一视觉基准。

本阶段不再生产程序化过渡贴图。正式流程为：

```text
母图原画 → 人工确认 → 切片资产 → Godot 导入 → 场景验收
```

## 输出规格

- 场景：`Region_HomeArea`
- 用途：Godot 2D 探索地图母图 / 后续切片源图
- 画布比例：横向大地图
- 目标尺寸：`6144 x 4096`
- 背景：完整场景原画，不要透明背景
- 禁止：角色、NPC、动物、UI、文字、Logo、水印

## 正向 Prompt

```text
Create a high-quality full scene key art for a 2D hand-painted exploration map.

Project:
那座村庄 / Region_HomeArea

Canvas:
6144 x 4096 horizontal game map canvas

Scene:
A cozy Japanese countryside home front yard in summer. The scene is an explorable 2D oblique top-down map for a slow-life village game. A small rural wooden house sits slightly above the center, with a warm tiled roof, soft eaves, a front door, and gentle shadow under the roof. Around the house is a quiet grassy yard, a north village road, a front yard path, a south stepping stone path, and a west garden soil patch. Add a mailbox near the path, a stone well, a simple wooden bench, a small road sign, and a soft cat bed near the yard. Add two large trees with split-friendly silhouettes, one on the left providing shade and one on the right near the yard. Add foreground grass and flowers at the bottom edges for depth.

Composition:
- Oblique 2D exploration map perspective, not first-person, not side view.
- The full area must feel walkable and readable in Godot.
- Keep clear path routes:
  1. northern road across the upper area
  2. front yard path from house entrance
  3. south stone path leading downward
  4. west garden path near the soil patch
- Leave walkable space in the center yard.
- Keep house base and door readable.
- Keep major shapes separable for later slicing into modular assets.
- Avoid excessive overlap between unrelated objects.
- No player character, no NPC, no animals baked into the environment.
- No UI, no labels, no text.

Art style:
High-quality Japanese animation background art, soft Ghibli-inspired countryside mood, warm low-saturation summer light, gentle diffuse shadows, watercolor and gouache texture, detailed but not noisy, calm healing atmosphere, subtle komorebi dappled sunlight through tree leaves.

Lighting:
Warm afternoon daylight, soft tree shadows on the grass, light patches on paths, no harsh contrast, no dramatic fantasy lighting.

Technical intent:
This image will later be sliced into modular Godot 2D assets:
ground patches, path patches, house body, roof occluder, tree trunks, tree canopies, props, foreground occluders, and light overlays.
Use clean separable shapes and avoid excessive overlapping between unrelated objects.
Keep transparent slicing in mind but render this as one complete concept map.
```

## 反向 Prompt

```text
characters, people, player, NPC, animals, UI, text, labels, logo, watermark, modern city, cars, power lines, fantasy castle, extreme perspective, side-scroller view, isometric grid, pixel art, 3D render, photorealism, blurry, messy composition, over-saturated colors, harsh shadows, dark horror mood, low quality, distorted buildings, unreadable paths, random props blocking walkable routes, excessive object overlap, black outlines, noisy texture, duplicate houses, duplicate wells, unreadable door, cropped house, cropped roads
```

## 混元/通用图像模型参数建议

```text
尺寸：优先 16:9 或 3:2 大图生成，再超分/扩图到 6144 x 4096
风格强度：中高
构图遵循：强
细节强度：中高
文字生成：关闭
人物生成：关闭
后处理：不要锐化过度，不要赛璐璐硬边
```

## 验收标准

1. 是否是一张完整可走的屋前庭院地图，而不是单纯插画背景。
2. 是否没有角色、NPC、动物、文字和 UI。
3. 是否能明确看出四条路径：北侧村道、屋前路、南侧石板路、西侧菜园路。
4. 房子、树、井、邮箱、长椅、路牌、猫窝是否比例合理。
5. 主角 `192x288` 的角色放入画面后，尺度是否自然。
6. 树冠、屋檐、前景草丛是否具备后续切成遮挡层的条件。
7. 地面与道路是否适合拆分成独立 PNG。
8. 光影是否统一，不能像多个素材拼贴。
9. 色彩是否符合低饱和、温暖、治愈、夏日下午。
10. 画面不能过度复杂，中心庭院必须保留足够可行走空间。

## 下一步

母图确认后，执行切片清单：

- `region_home_area_ground_grass_north_v001.png`
- `region_home_area_ground_grass_yard_v001.png`
- `region_home_area_ground_grass_south_v001.png`
- `region_home_area_ground_west_garden_soil_v001.png`
- `region_home_area_path_north_village_road_v001.png`
- `region_home_area_path_front_yard_v001.png`
- `region_home_area_path_south_stone_v001.png`
- `region_home_area_path_west_garden_v001.png`
- `region_home_area_structure_cloud_house_back_v001.png`
- `region_home_area_structure_cloud_house_roof_occluder_v001.png`
- `region_home_area_tree_left_trunk_v001.png`
- `region_home_area_tree_left_canopy_occluder_v001.png`
- `region_home_area_tree_right_trunk_v001.png`
- `region_home_area_tree_right_canopy_occluder_v001.png`
- `region_home_area_prop_mailbox_v001.png`
- `region_home_area_prop_well_v001.png`
- `region_home_area_prop_bench_v001.png`
- `region_home_area_prop_road_sign_v001.png`
- `region_home_area_prop_cat_bed_v001.png`
- `region_home_area_foreground_front_grass_left_v001.png`
- `region_home_area_foreground_front_flowers_right_v001.png`
- `region_home_area_fx_dappled_light_v001.png`
- `region_home_area_fx_wind_leaves_top_v001.png`
