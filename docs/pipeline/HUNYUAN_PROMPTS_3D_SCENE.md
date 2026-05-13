# 腾讯混元3D 场景生成提示词参考

> 基于 `hunyuan_scene_001_regen_prompt_pack.md` 生成
> 场景：云村庭院 (Cloud Village Homeyard)
> 风格：日式田园慢生活、新海诚光影

---

## 场景概述

| 项目 | 描述 |
|------|------|
| 场景名称 | 云村庭院 |
| 场景类型 | 日式乡村住宅庭院 |
| 风格关键词 | 温暖、柔和、低饱和、手绘质感、物哀之美 |
| 参考 | 新海诚动画、宫崎骏风格 |

---

## 全局约束（每个模块必须遵守）

```
- 坐标系: Y-up（Y轴向上）
- 导出格式: glTF 2.0 / GLB
- 世界原点: 所有模块共享同一原点 (0,0,0)
- 不要自动居中/重置原点
- 风格: 不做写实脏污，不要高频破碎三角面，不要悬浮碎片
- 色彩: 低饱和偏暖，柔和自然
```

---

## 模块 1: Ground（地面）

### 输出文件名
```
hunyuan_scene_001_module_ground.glb
```

### 中文提示词
```
日式田园慢生活村庄庭院地形模块，作为"地面/可行走层"。
俯视半固定镜头可读，形体清晰，保留庭院主路、草地、土路、院落边界起伏。
风格温暖柔和、低饱和、轻手绘质感。
不要碎片化噪点网格，不要悬浮破面，不要高频破碎三角面。
输出为单独 ground 模块，和同批其他模块共享统一世界原点，导出后放在(0,0,0)可直接拼合。
```

### English Prompt
```
Japanese countryside village courtyard terrain module for walkable ground layer.
Readable in top-down fixed camera view, clear forms with main paths, grass areas, dirt roads, and courtyard boundary variations.
Style: warm, soft, low saturation, hand-painted texture.
No fragmented noise meshes, no floating shards, no high-frequency broken triangles.
Export as standalone ground module sharing the same world origin (0,0,0) with other modules.
```

### 三角面数目标
- 目标: ~300 triangles
- 当前: 292 triangles

---

## 模块 2: Architecture（建筑）

### 输出文件名
```
hunyuan_scene_001_module_architecture.glb
```

### 中文提示词
```
日式乡村庭院的建筑体块模块（房屋、廊檐、墙体、台阶等），强调可读的大形。
保持半固定镜头下轮廓明确，体块连续，不要碎裂面云。
风格温暖柔和、低饱和、手绘质感，不做写实脏污。
输出 architecture 独立模块，和 ground/vegetation/props 保持同一世界坐标原点，不做单件居中重置。
```

### English Prompt
```
Japanese rural courtyard architectural block module (house, eaves, walls, steps), emphasizing readable large shapes.
Clear contours in semi-fixed camera view, continuous volumes, no fragmented mesh clouds.
Style: warm, soft, low saturation, hand-painted texture, no realistic dirt or grime.
Export as standalone architecture module sharing the same world origin (0,0,0) with other modules.
```

### 三角面数目标
- 目标: ~75,000 triangles
- 当前: 74,871 triangles

---

## 模块 3: Vegetation（植被）

### 输出文件名
```
hunyuan_scene_001_module_vegetation.glb
```

### 中文提示词
```
日式田园庭院植被模块（树、灌木、草簇），用于构建"こもれび"树影氛围。
要求整体形体可读，树冠与树干分区清晰，避免噪点碎片和漂浮断面。
色彩低饱和偏暖，轻手绘观感。
输出 vegetation 独立模块，保持与其他模块统一原点和比例，导出后在(0,0,0)可对齐。
```

### English Prompt
```
Japanese countryside courtyard vegetation module (trees, bushes, grass clusters) for "komorebi" (dappled light through trees) atmosphere.
Readable overall shapes, clear separation between canopy and trunk, no noise fragments or floating cross-sections.
Colors: low saturation, warm tones, hand-painted appearance.
Export as standalone vegetation module sharing the same world origin (0,0,0) with other modules.
```

### 三角面数目标
- 目标: ~64,000 triangles
- 当前: 63,550 triangles

---

## 模块 4: Props（道具）

### 输出文件名
```
hunyuan_scene_001_module_props.glb
```

### 中文提示词
```
日式乡村庭院道具模块（围栏、木箱、小凳、盆栽、工具、杂物点缀），用于生活感补充。
道具数量适中，避免过密导致可读性下降。
整体风格温暖、低饱和、手绘感，形体完整，避免碎片化破面。
输出 props 独立模块，保持与 ground/architecture/vegetation 统一世界原点，不做自动居中。
```

### English Prompt
```
Japanese rural courtyard props module (fences, wooden boxes, stools, potted plants, tools, decorative items) for life-like atmosphere.
Moderate number of props, avoid overcrowding to maintain readability.
Overall style: warm, low saturation, hand-painted feel, complete shapes, no fragmented broken surfaces.
Export as standalone props module sharing the same world origin (0,0,0) with other modules.
```

### 三角面数目标
- 目标: ~17,000 triangles
- 当前: 17,234 triangles

---

## 可选模块 5: Walkable Nav Mesh（可行走导航网格）

### 输出文件名
```
hunyuan_scene_001_walkable_nav.glb
```

### 中文提示词
```
基于同一庭院布局生成"仅可行走面"的简化网格：
只保留角色可走区域，不包含墙体、立面和悬空结构。
网格要干净、连续、低面数，适合 NavigationMesh 使用。
与主场景模块共用统一世界原点。
导出为单独 walkable_nav 模块。
```

### English Prompt
```
Generate a simplified walkable surface mesh based on the same courtyard layout:
Only include areas where characters can walk, excluding walls, facades, and elevated structures.
Mesh should be clean, continuous, and low-poly for NavigationMesh use.
Share the same world origin with main scene modules.
Export as standalone walkable_nav module.
```

---

## 可选模块 6: Blockers（阻挡体）

### 输出文件名
```
hunyuan_scene_001_blockers.glb
```

### 中文提示词
```
基于同一庭院布局生成"阻挡体代理模块"：
只保留不可达障碍（墙体、围栏、主要障碍物）对应的低面数体块。
强调语义清晰（按障碍区域分块），不要一个超大整体盒。
与主场景模块共用统一世界原点。
导出为单独 blockers 模块。
```

### English Prompt
```
Generate collision proxy blocks based on the same courtyard layout:
Only include low-poly volumes for impassable obstacles (walls, fences, main obstacles).
Emphasize semantic clarity (separate blocks by obstacle region), avoid one giant box.
Share the same world origin with main scene modules.
Export as standalone blockers module.
```

---

## 腾讯混元3D 使用指南

### 访问地址
```
https://3d.hunyuan.tencent.com/studio/
```

### 推荐的场景生成模式

1. **Scene（场景）模式** - 推荐用于完整庭院场景
2. **Concept（概念）模式** - 适合快速草图
3. **上传参考图** - 如果有草图或设计稿可上传

### 生成后处理

1. 下载 GLB 格式
2. 用 Blender 验证坐标原点
3. 确保模型在 (0,0,0) 可与其他模块对齐
4. 复制到 `assets/3d/modules/hunyuan_scene_001/official/`

### Blender 验证脚本

```python
import bpy
import os

# 验证模型坐标
obj = bpy.context.active_object
print(f"Location: {obj.location}")
print(f"Bound Box: {obj.bound_box}")

# 确保导出设置
bpy.ops.export_scene.gltf(
    filepath=os.path.join(output_dir, "export.glb"),
    export_format='GLB',
    use_selection=True,
    export_yup=True,
    export_apply=True  # 应用变换
)
```

---

## 文件清单

| 模块 | 文件名 | 状态 |
|------|--------|------|
| Ground | `hunyuan_scene_001_module_ground.glb` | ✅ 已有 |
| Architecture | `hunyuan_scene_001_module_architecture.glb` | ✅ 已有 |
| Vegetation | `hunyuan_scene_001_module_vegetation.glb` | ✅ 已有 |
| Props | `hunyuan_scene_001_module_props.glb` | ✅ 已有 |
| Walkable Nav | `hunyuan_scene_001_walkable_nav.glb` | ✅ 已有 |
| Blockers | `hunyuan_scene_001_blockers.glb` | ✅ 已有 |

---

## 下一步

如果需要重新生成某个模块：
1. 选择对应的提示词
2. 在腾讯混元3D中粘贴提示词
3. 生成并下载 GLB
4. 替换 official 目录中的对应文件
5. 在 Godot 中验证拼合效果
