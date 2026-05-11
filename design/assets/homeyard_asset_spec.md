# 主角家檐廊 / 屋前庭院资产说明书

> 版本：2026-05-10
> 适用场景：`res://scenes/world/cloud_house.tscn`
> 母图：`resources/设计图/主角家檐廊.png`

## 场景目标

将主角家檐廊与屋前庭院拆成可复用、可交互、可做轻量动效的 Godot 2D 资产。核心体验是夏日午后三点的松弛感：檐廊、柿子树、风铃、电扇、西瓜、远山、村屋与斑驳光共同服务“宁静 -> 美与感动 -> 探索”。

## 分层规则

| 层级 | 内容 | Godot 分组 |
| --- | --- | --- |
| Background | 母图原版底板、云、远山、远村、远树 | `HomeyardLayers/Background` |
| SourceSplits | 从母图切出的透明局部层：建筑、庭院、树、前景遮挡等 | `HomeyardLayers/SourceSplits` |
| Props | 水井、木桶、风铃、电扇、西瓜、托盘 | `HomeyardLayers/Props` |
| PlayerLayer | 玩家出生点和后续角色层 | `HomeyardLayers/PlayerLayer` |
| OptionalFX | 叶片轻晃、风铃分件、风扇动效、斑驳光、浮尘 | `HomeyardLayers/OptionalFX` |

## 命名和导出

- 命名格式：`homeyard_<layer>_<subject>_01.png`。
- Godot 路径：`res://sprites/environments/homeyard/<category>/<asset_id>.png`。
- `homeyard_bg_sky_01.png` 在正式运行批次中作为母图原版底板使用，像素等于 `resources/设计图/主角家檐廊.png` resize 到 1920x1080 的结果。
- 背景和场景拆分图层使用 1920x1080 16:9，透明切片默认不渲染，避免与母图底板重复叠加。
- 独立道具使用原生透明 PNG，保留干净 alpha 边缘。
- 每个最终资产必须有预览：`sprites/environments/homeyard/previews/<asset_id>_preview.png`。

## 交互和动效

- `well/bucket/windchime/oldfan/watermelon/tray` 挂 `interactable` group，并写入 `asset_id` metadata。
- 风铃、电扇、斑驳光、浮尘只提供轻量动效节点和素材，不扩大玩法系统。
- 玩家与可交互物的具体逻辑仍由现有 interaction/farm/cooking 等系统后续接入。

## 生产说明

本批资产以母图作为原版底板，并从母图切出透明局部层。`cloud_house.tscn` 默认只渲染母图底板；拆分层、源图道具和可选 FX 保留在场景中但默认隐藏，供后续遮挡、视差或动效单独启用。母图中不存在的 `well` / `bucket` 仅保留为可选生成切图，默认隐藏。

## 来源摘要

```text
《那座村庄》主角家屋前庭院
场景资产拆分表 + 可复制 Prompt 文档
参考母图：主角家屋前庭院 · 夏日午后三点
项目《那座村庄》
场景主角家屋前庭院
画幅16:9 横版
核心意象こもれび / 斑驳阳光
1. 场景目标
本文件用于把「主角家屋前庭院 · 夏日午后总览」从概念图推进到 Godot 可实装资产。制作重点不是把插画机械切开，而是将场景拆成可复用、可交互、可做轻量动效的游戏资产。
核心体验：轻松、慵懒、治愈、没有强目标压力。
核心光影：夏日下午三点，树叶透光形成斑驳光斑。
核心空间：古民家、缘侧、屋前庭院、石板路、柿子树、远处村庄和山。
实装方向：背景层、主体层、前景遮挡层、交互道具层、动态氛围层。
2. 资产拆分总览
A. 远景背景层（Background）
资产名
内容
建议格式
Godot 用途 / 备注
homeyard_bg_sky_01
夏日晴空
PNG
可作为最底层背景。
homeyard_bg_clouds_01
缓慢云层
透明 PNG
可做轻微横向移动。
homeyard_bg_mountains_01
远山
PNG
放在云层前，低速视差。
homeyard_bg_far_village_01
远处村庄屋顶
透明 PNG
弱化细节，避免抢主体。
homeyard_bg_far_trees_01
远处树林带
透明 PNG
衔接远山和庭院。
B. 建筑主体层（Main Structure）
资产名
内容
建议格式
Godot 用途 / 备注
homeyard_mid_house_main_01
古民家主体
透明 PNG
主结构，可与屋顶合并或分层。
homeyard_mid_house_roof_01
瓦屋顶
透明 PNG
可单独调明暗和层级。
homeyard_mid_veranda_floor_01
缘侧木地板
透明 PNG
角色常活动区，建议保留阴影。
homeyard_mid_sliding_doors_01
拉门 / 障子门
透明 PNG
后续可做开门交互。
homeyard_mid_wooden_pillars_01
木柱
透明 PNG
可作为角色遮挡层。
homeyard_mid_interior_darkbase_01
屋内暗部基础
透明 PNG
让屋内空间有深度。
C. 庭院环境层（Garden / Ground）
资产名
内容
建议格式
Godot 用途 / 备注
homeyard_mid_garden_ground_01
庭院草地基础
PNG
地面主层。
homeyard_mid_stone_path_01
石板小路
透明 PNG
通往村庄 / 田园入口。
homeyard_mid_stone_wall_01
石墙
透明 PNG
庭院边界。
homeyard_mid_persimmon_tree_01
柿子树
透明 PNG
重要视觉锚点，可拆树冠和树干。
homeyard_mid_shrub_cluster_01
灌木丛 01
透明 PNG
可复用装饰。
homeyard_mid_flower_bush_blue_01
蓝色花丛
透明 PNG
边角点缀。
D. 可交互道具层（Props / Interactables）
资产名
内容
建议格式
是否建议交互
homeyard_prop_well_01
水井
透明 PNG
是
homeyard_prop_bucket_01
木桶
透明 PNG
是
homeyard_prop_windchime_01
风铃
透明 PNG
是
homeyard_prop_oldfan_01
老旧电扇
透明 PNG
是
homeyard_prop_fan_blades_01
电扇扇叶
透明 PNG
是，循环旋转
homeyard_prop_watermelon_half_01
半个西瓜
透明 PNG
可选
homeyard_prop_tray_01
木托盘
透明 PNG
可选
E. 前景遮挡层（Foreground Overlay）
资产名
内容
建议格式
Godot 用途 / 备注
homeyard_fg_leaves_top_01
顶部前景树叶
透明 PNG
放在角色层上方，增强景深。
homeyard_fg_grass_left_01
左前景草丛
透明 PNG
可遮角色脚部。
homeyard_fg_flower_right_01
右前景花丛
透明 PNG
柔化画面边缘。
homeyard_fg_shadow_overlay_01
斑驳阴影覆盖
半透明 PNG
统一光影。
homeyard_fg_branch_optional_01
近景树枝
透明 PNG
可选。
F. 动态氛围层（Animated Atmosphere）
资产名
内容
建议格式
动画建议
homeyard_fx_leaf_sway_01
树叶轻晃层
分层 PNG / Shader
小幅、慢速摆动。
homeyard_fx_windchime_anim_01
风铃摆动
分件 PNG
往复轻摆。
homeyard_fx_fan_blades_anim_01
电扇扇叶旋转
分件 PNG
循环旋转。
homeyard_fx_dapplelight_01
斑驳阳光变化层
半透明 PNG / Shader
缓慢流动。
homeyard_fx_dust_particles_01
浮尘 / 热空气感
粒子 / 透明 PNG 序列
极轻微，避免抢画面。
3. Godot 图层顺序建议
01 bg_sky
02 bg_clouds
03 bg_mountains
04 bg_far_village
05 bg_far_trees
06 garden_ground
07 stone_path
08 stone_wall
09 shrubs / flowers / grass
10 persimmon_tree
11 house_main
12 veranda_floor
13 sliding_doors / interior
14 props（井、桶、风铃、电扇、西瓜）
15 player
16 foreground leaves / flowers
17 shadow overlay
18 particles / light effects
4. 第一批生产优先级
第一批：先做可实装核心资产
优先级
资产名
原因
1
homeyard_bg_sky_01 / bg_mountains_01 / bg_far_village_01
先搭出空间纵深。
2
homeyard_mid_house_main_01
场景主体，决定风格统一。
3
homeyard_mid_ver
```
