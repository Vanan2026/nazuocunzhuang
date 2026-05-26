# Greenfield P0 Scene Asset Request - Mother + Base + Foreground

更新时间：2026-05-21 21:46

## 结论

当前批次生产 10 个可探索场景的大图资产。

每个场景需要 3 张图：

- `*_scene_mother.png`: 完整不透明场景母图，用于审图、总构图确认、碰撞/交互参考。
- `*_base.png`: 去除前景遮挡后的完整不透明底图，用作 Godot 主背景。
- `*_foreground_occlusion.png`: 透明前景遮挡层，只包含会盖住玩家的前景像素。

这三张图必须 registration-perfect：同尺寸、同原点、同透视、同构图、同坐标系。

不再生产：

- `terrain_details`
- `behind_player_structures`
- `ysort_props_structures`
- `shadow_overlay`
- `light_weather_overlay_spring/summer/autumn/winter`

天气、季节、光照、整体阴影、交互点、碰撞、多边形阻挡、Y-sort 节点由 Godot 系统层处理。

## 三张图的职责

### 1. `*_scene_mother.png`

完整成品场景图。

要求：

- PNG，完全不透明。
- 包含完整视觉效果：地面、建筑、树、石头、道具、前景遮挡物等。
- 用于审查构图、风格、动线、物件位置、镜头安全边。
- 不直接作为最终主背景，避免玩家被前景物体永远压住。

### 2. `*_base.png`

运行时主背景图。

要求：

- PNG，完全不透明。
- 从母图中去掉所有 `foreground_occlusion` 像素后补绘底下环境。
- 必须保留地面、道路、水体、建筑主体、树干/树体中不遮挡玩家的部分、可见道具等。
- 不能留下透明洞、空白洞、涂抹脏边或明显 AI 修补痕迹。
- 用于 Godot 背景层和碰撞/交互定位参考。

### 3. `*_foreground_occlusion.png`

运行时前景遮挡图。

要求：

- PNG，RGBA，透明背景。
- 只包含玩家走到后面时应该盖住玩家的像素。
- 必须和母图/base 完全对齐。
- 应当叠在 base 上时基本复原母图中对应前景遮挡关系。

## 前景遮挡层放什么

只放“玩家走到后面时应该被盖住”的前景像素：

- 树冠前缘、灌木前缘、篱笆前缘。
- 房屋前檐、门廊前缘、棚子顶前缘。
- 高草前缘、桥栏、台阶/坡面前沿。
- 岩壁前沿、悬崖前沿、洞口前沿、棚架前沿。

不要放：

- 天气、季节光效、雪、雨、雾、落叶。
- 接触阴影和整体调色。
- 整棵树、整栋房子、整块岩石，除非该部分确实在玩家前方遮挡。
- 可交互物整件物体，除非它的前缘需要遮挡玩家。

## 通用美术要求

- 类型：无战斗治愈系乡村生活模拟场景。
- 视角：固定 3/4 俯视 2D。
- 风格：温暖低饱和、轻绘本感、清晰轮廓、软手绘纹理、模块化可读。
- 禁止：战斗、怪物、武器、血量、击杀、恐怖、科幻 HUD、强压力表现。
- 不要 UI、文字、水印、角色、对话框、图标。
- 每张母图必须是完整可探索区域，不是小插画，不是物件拼贴。
- 构图必须有足够“可走空间”，道路、空地、门口、桥、台阶、地形边界要读得清楚。
- 镜头移动时边缘不能露出场景外，所以画布边缘也必须是完整环境，可自然延伸或作为边界。
- 玩家主要活动区距离画布硬边建议至少 `220px`。

## 每场景交付路径

```text
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/01_scene_mothers/regions/{region}/{region}_scene_mother.png
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/02_scene_base/regions/{region}/{region}_base.png
production/assets/external_gpt_handoff/greenfield_p0/v001/incoming/03_foreground_occlusion/regions/{region}/{region}_foreground_occlusion.png
```

文件规则：

- 三张图必须同尺寸。
- `scene_mother` 和 `base` 必须完全不透明。
- `foreground_occlusion` 必须 RGBA 透明背景。
- 禁止裁切到物体 bounding box。
- `base + foreground_occlusion` 叠加后，应接近复原 `scene_mother` 的前景遮挡关系。

## 画布尺寸建议

旧尺寸可作为最低尺寸，但为了镜头移动留边，建议使用更稳妥的大场景尺寸。

推荐：

- 小场景：`1920x1280`
- 中场景：`2200x1400`
- 大场景：`2400x1600`

如果已经按旧尺寸生产过，也可以保留旧尺寸，但必须满足：玩家活动区距离画布边缘至少 `220px` 安全边，镜头不会看到空白或截断边界。

## 10 个场景清单

| 序号 | region | 旧尺寸 | 建议尺寸 | 场景目标 |
|---:|---|---:|---:|---|
| 01 | `home_area` | `1470x1070` | `1920x1280` | 玩家住宅、院子、门前公共小路，是新手核心活动点。 |
| 02 | `village` | `1800x1200` | `2400x1600` | 小村中心、道路交汇、广场边、住户门前路径、地标。 |
| 03 | `back_farm` | `1600x1200` | `2200x1400` | 后院农田、作物地块、工具棚/水源、可扩建空间。 |
| 04 | `forest_edge` | `1700x1150` | `2200x1400` | 村外林缘、自然入口、采集点、通往森林的缓坡小路。 |
| 05 | `orchard` | `1700x1150` | `2200x1400` | 果树园、树列、草地、可穿行小径、温和采摘氛围。 |
| 06 | `pond` | `1600x1100` | `2200x1400` | 池塘、水边步道、钓鱼/观察点、芦苇和石岸。 |
| 07 | `mountain_path` | `1700x1200` | `2200x1400` | 山路、坡道、石阶、树影、通往更高处的路径。 |
| 08 | `mountain_hut` | `1500x1050` | `1920x1280` | 山中小屋、门前空地、柴堆/井/围栏等生活痕迹。 |
| 09 | `mountain` | `1800x1200` | `2400x1600` | 岩石山地、溪流穿越、开阔点、通往山屋/眺望点的连接。 |
| 10 | `cliff_view` | `1500x1000` | `1920x1280` | 悬崖眺望点、安全步道、休息小平台、远景。 |

## 单场景生产模板

将 `{region}`、`{recommended_size}`、`{scene brief}` 替换后使用。

```text
Create three registration-perfect PNG assets for the same explorable 2D game scene: {region}.

Style: warm low-saturation storybook 2D art, fixed 3/4 top-down rural village view, clear readable silhouettes, soft hand-painted texture, clean outlines, cozy countryside life simulation. No combat, no monsters, no weapons, no horror, no sci-fi HUD, no UI text, no characters.

Canvas: {recommended_size} px. All three outputs must have the exact same canvas size, origin, scale, perspective, and composition. The scene must be large enough for camera movement; keep the main walkable/play area at least 220 px away from hard canvas edges. Edges must still be fully painted environment, not blank cutoff.

Scene brief: {scene brief}

Output 1: {region}_scene_mother.png
A fully opaque complete mother image showing the final scene with all ground, buildings, trees, props, and foreground occluders visible. Use it for composition review.

Output 2: {region}_base.png
A fully opaque runtime base image derived from the same mother composition, with only the foreground occlusion pixels removed and the hidden area underneath cleanly repaired. This is the main Godot background. Do not leave holes, transparent areas, or messy inpaint artifacts.

Output 3: {region}_foreground_occlusion.png
A transparent RGBA foreground occlusion image, exact same canvas, containing only the pixels that should visually cover the player when the player walks behind them: front canopy edges, front eaves, fence fronts, tall grass fronts, railings, cliff fronts, ledge fronts, etc. Do not include weather, seasonal overlays, full objects, UI, text, characters, or shadows unrelated to occlusion.

Gameplay readability: include clear walkable paths, open space for player movement, readable entrances/exits, object placement beside paths instead of blocking paths, and natural boundaries. Collision, interaction, weather, season, and lighting will be handled in Godot, not in this asset batch.
```

## 场景 brief

### 01 home_area

Private home yard plus public front lane. The house sits above its yard paths, not on the road. Mailbox and bench sit beside the public lane. A well or small utility point stays inside the private yard with a narrow side footpath. Keep the home entrance, yard loop, and public lane readable.

### 02 village

Small lived-in village center with through lanes, a modest plaza edge, doorstep paths, and a small landmark. Houses are set back from roads with readable door approaches, not pasted into the lane. Keep room for NPC walking and player navigation.

### 03 back_farm

Quiet back farm area behind or near the home. Include readable farm plots, soil beds, tool/storage corner, water access, and expansion space. Paths should connect cleanly to the home/village direction without cluttering crop areas.

### 04 forest_edge

Transition from village edge into soft woodland. Include a readable path entering trees, small gathering clearings, low bushes, logs, stones, and a natural boundary. Avoid making the path feel like a combat dungeon.

### 05 orchard

Cozy orchard with rows or clusters of fruit trees, grass paths, small crates/baskets, and room to walk between trees. Tree crowns may create foreground occlusion, but paths must remain clear.

### 06 pond

Gentle pond scene with water edge, fishing/observing spot, reeds, stones, small footpath, and safe walkable bank. Water boundary must be visually clear for collision setup.

### 07 mountain_path

Mountain trail with slopes, stone steps, switchback path, shrubs, and rock edges. Make the traversable route readable and not too narrow. Use front ledges or tree branches for foreground occlusion.

### 08 mountain_hut

Small mountain hut with a lived-in yard, front approach path, woodpile or simple rural props, and quiet isolation. Keep the door approach and surrounding walkable clearing readable.

### 09 mountain

Rocky mountain area with trail continuity, stream crossing or small clearing spur, larger rock masses, and natural elevation. Rocks frame the route while preserving clear traversal.

### 10 cliff_view

Cliff overlook with safe contour ledge path, rest/view spur, and distant vista beyond the walkable edge. The walkable ground must read clearly as safe; cliff/vista should read as boundary, not traversable floor.

## 接收验收标准

- 每个 region 恰好 3 张 PNG。
- `scene_mother` 完全不透明。
- `base` 完全不透明，且已去除/修补前景遮挡像素。
- `foreground_occlusion` 为透明 RGBA。
- 三张图尺寸完全一致。
- `base + foreground_occlusion` 叠加后接近复原 `scene_mother`。
- 画布足够大，镜头移动不会露出空白或截断。
- 3/4 俯视一致，不混入正侧视、纯俯视或透视插画。
- 路径、边界、入口、交互点可读。
- 无战斗、无怪物、无 UI、无文字、无角色。
- 前景层只包含遮挡玩家的像素，不包含天气/季节/整体光效。
