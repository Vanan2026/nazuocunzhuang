# region_home_area_structure_cloud_house_back_v001.png 生产指令

## 状态

- 目标：正式单资产生产
- 类型：YSortWorld structure / house body
- 输出：单张透明 PNG
- 背景：必须透明
- 禁止：资产展示板、表格、文字、编号、说明、白底、灰底、整场景背景

## 资产名

```text
region_home_area_structure_cloud_house_back_v001.png
```

## 用途

`Region_HomeArea` 主屋本体。用于 Godot `YSortWorld/Houses/CloudHouse` 节点下，作为角色可从屋前穿行时的主体建筑资产。

屋顶遮挡层稍后单独生产：

```text
region_home_area_structure_cloud_house_roof_occluder_v001.png
```

因此本资产可以包含房屋主体和必要的屋顶轮廓，但不要把屋檐遮挡层画得过度复杂，也不要把前景遮挡逻辑烘焙死。

## 尺寸与锚点建议

- 目标视觉宽度：`1500–1800 px`
- 建议画布：`2048 x 1536` 或更高
- 透明背景
- 锚点：房屋底部中心
- `anchor_x = width / 2`
- `anchor_y = height`

## 正向 Prompt

```text
Create one single game-ready 2D environment asset as a transparent PNG.

Asset name:
region_home_area_structure_cloud_house_back_v001.png

Asset:
The main body of a cozy rural Japanese wooden house from the Region_HomeArea scene of a slow-life village game.

View:
Oblique top-down 2D exploration map perspective, matching a Godot 2D walkable map. The perspective must match a hand-painted exploration map, not a side-view illustration and not a 3D render.

Composition:
Only the house body asset. No asset sheet. No layout board. No labels. No text. No table. No preview scene. No background panel. No white background. No gray background.

Visual content:
A small warm countryside wooden house with weathered timber walls, sliding front door, small windows, stone doorstep, low foundation, subtle potted plants near the door, and soft contact shadow at the base. The house should feel old but cared for. Use warm wood tones, muted plaster panels, and a dark gray Japanese tiled roof. The roof can be included as part of the silhouette, but keep the upper eaves clean enough to allow a separate roof occluder asset later.

Shape requirements:
Clean readable silhouette, suitable for later slicing and Godot YSort placement. The bottom base line should be stable and easy to anchor. Avoid large empty margins. Avoid excessive grass field around the house. A small amount of contact grass and base shadow is acceptable.

Style:
High-quality hand-painted Japanese animation background art, warm low-saturation summer rural lighting, soft Ghibli-inspired countryside mood, watercolor and gouache texture, detailed but clean, calm and healing atmosphere.

Technical requirements:
Transparent background, RGBA.
No text, no labels, no watermark.
No characters, no people, no NPCs, no animals.
No UI.
No full scene background.
No rectangular background.
Foot/base anchor should visually be at bottom center.
Target visual width around 1500–1800 px.
High resolution.
```

## 反向 Prompt

```text
asset sheet, reference sheet, multiple assets, table, labels, text, numbers, file names, UI, logo, watermark, background panel, white background, gray background, black background, full scene, landscape background, grass field background, characters, people, NPC, animals, isometric grid, pixel art, 3D render, photorealism, blurry, messy edges, cropped roof, cropped base, duplicated house, distorted perspective, unreadable door, black outline, overly saturated colors, harsh contrast, fantasy castle, modern house, city building
```

## 验收标准

1. 只出现一栋房子，不出现资产表、说明文字、编号或展示背景。
2. 背景必须透明。
3. 透视必须接近当前 `Region_HomeArea` 母图。
4. 房屋底部中心可作为 Godot 锚点。
5. 门、窗、屋檐、屋基可读。
6. 角色 `192 x 288` 放到门口时比例自然。
7. 屋顶边界清楚，后续可单独做 roof occluder。
8. 不包含角色、动物、NPC、UI、文字。
9. 不把大面积草地或道路烘焙进房屋资产。
10. 画风必须与母图一致：低饱和、温暖、治愈、手绘质感。

## 如果模型再次生成资产展示板

判定为不合格，直接重跑。必须强调：

```text
single isolated transparent PNG asset only, no asset sheet, no labels, no text, no background
```
