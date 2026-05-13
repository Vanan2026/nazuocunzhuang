# Hunyuan Scene 001 Regeneration Prompt Pack (v1)

Date: 2026-05-12  
Scope: Rebuild upstream 3D source as modular official pack for Godot

## Goal

Replace unreadable fragmented source with clean, semantically readable modules while keeping current project directory contracts.

## Required output files (official module names)

Place final GLB files into:

`res://assets/3d/modules/hunyuan_scene_001/official/`

Required names:

1. `hunyuan_scene_001_module_ground.glb`
2. `hunyuan_scene_001_module_architecture.glb`
3. `hunyuan_scene_001_module_vegetation.glb`
4. `hunyuan_scene_001_module_props.glb`

Recommended optional (if you can author):

5. `hunyuan_scene_001_walkable_nav.glb`
6. `hunyuan_scene_001_blockers.glb`

## Global generation constraints (for every module)

- Style:
  - Japanese countryside slow-life
  - warm, soft, low saturation
  - hand-painted feeling
  - not photorealistic, not horror, not high-contrast gritty
- Coordinate consistency:
  - all modules must align when imported at `(0,0,0)`
  - do not auto-center each object before export
  - keep one shared world origin across modules
- Geometry quality:
  - avoid floating shard clouds and salt-and-pepper disconnected fragments
  - preserve large readable masses first
- Output:
  - glTF 2.0 / GLB
  - include vertex color or textures (either is fine)
  - Y-up

## Prompt 01: Ground

```
日式田园慢生活村庄庭院地形模块，作为“地面/可行走层”。
俯视半固定镜头可读，形体清晰，保留庭院主路、草地、土路、院落边界起伏。
风格温暖柔和、低饱和、轻手绘质感。
不要碎片化噪点网格，不要悬浮破面，不要高频破碎三角面。
输出为单独 ground 模块，和同批其他模块共享统一世界原点，导出后放在(0,0,0)可直接拼合。
```

## Prompt 02: Architecture

```
日式乡村庭院的建筑体块模块（房屋、廊檐、墙体、台阶等），强调可读的大形。
保持半固定镜头下轮廓明确，体块连续，不要碎裂面云。
风格温暖柔和、低饱和、手绘质感，不做写实脏污。
输出 architecture 独立模块，和 ground/vegetation/props 保持同一世界坐标原点，不做单件居中重置。
```

## Prompt 03: Vegetation

```
日式田园庭院植被模块（树、灌木、草簇），用于构建“こもれび”树影氛围。
要求整体形体可读，树冠与树干分区清晰，避免噪点碎片和漂浮断面。
色彩低饱和偏暖，轻手绘观感。
输出 vegetation 独立模块，保持与其他模块统一原点和比例，导出后在(0,0,0)可对齐。
```

## Prompt 04: Props

```
日式乡村庭院道具模块（围栏、木箱、小凳、盆栽、工具、杂物点缀），用于生活感补充。
道具数量适中，避免过密导致可读性下降。
整体风格温暖、低饱和、手绘感，形体完整，避免碎片化破面。
输出 props 独立模块，保持与 ground/architecture/vegetation 统一世界原点，不做自动居中。
```

## Optional Prompt 05: Walkable Nav Mesh

```
基于同一庭院布局生成“仅可行走面”的简化网格：
只保留角色可走区域，不包含墙体、立面和悬空结构。
网格要干净、连续、低面数，适合 NavigationMesh 使用。
与主场景模块共用统一世界原点。
导出为单独 walkable_nav 模块。
```

## Optional Prompt 06: Blockers

```
基于同一庭院布局生成“阻挡体代理模块”：
只保留不可达障碍（墙体、围栏、主要障碍物）对应的低面数体块。
强调语义清晰（按障碍区域分块），不要一个超大整体盒。
与主场景模块共用统一世界原点。
导出为单独 blockers 模块。
```

## Export checklist (before sending files)

- 4 个官方模块文件名完全匹配
- 导出后四个模块同时加载在 `(0,0,0)` 能拼回同一庭院
- 无明显碎片云/爆面
- 视角下可辨认“地面-建筑-植被-道具”结构

## Intake flow in this repo

After files are dropped in official dir:

1. `python tools/switch_hunyuan_scene_001_to_official_modules.py`
2. `python tools/build_hunyuan_scene_001_runtime_proxies.py`
3. `python tools/validate_hunyuan_scene_001_characterbody3d.py`
4. Godot preview playtest in `res://scenes/dev/hunyuan_scene_001_preview.tscn`

