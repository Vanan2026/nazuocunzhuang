# Region_HomeArea Art Direction v0.1

## 目标
为 `Region_HomeArea` 制定可执行的上线级场景美术方案。该方案先解决构图、分区、镜头和玩法空间，再进入 3D 底模或高质量 2D 底图/模块资产生产。

## 核心定位
`Region_HomeArea` 是玩家的家门口庭院，承担三个职责：

- 情绪锚点：安静、熟悉、温暖的日式乡村家屋。
- 玩法起点：玩家出生、休息、查看邮箱/路牌/水井、进入后院农场。
- 世界连接：向北/西北通往村庄，向南/东南通往 BackFarm。

## 推荐流程
采用流程 A 作为主线：

1. 设计方案确认。
2. 搭建 3D 底模：只做空间、体块、镜头、遮挡、光源和资产分区。
3. 根据底模分区生产高质量 2D 美术资产。
4. 分层导出 PNG：底图、结构、道具、遮挡、光影。
5. Godot 接入：origin、anchor、z-index、YSort、碰撞和可走区。

流程 B 可作为补充：

- 直接根据本设计生产完整场景底图，再额外生产模块化 props/occluders，在 Godot 中拼接。

## 镜头与画布
- 生产画布：`6144 x 4096`。
- 镜头语言：斜俯视 2D/2.5D，约等同 3/4 俯视地图，不采用纯横版近景。
- 玩法镜头重点：玩家应始终能看清脚下路径、交互点和区域出口。
- 禁止把房屋或树冠画成遮住大面积可走区域的插画式构图。

## 总体构图
构图采用“上方家屋、中央庭院、左右景深、下方出口/前景”的结构。

```text
┌──────────────────────────────────────────────┐
│  A 北侧村路 / 远景树篱 / 轻坡               │
│        ┌──────── B 家屋与屋檐 ────────┐      │
│        │  门口 / veranda / 休息点      │      │
│  C 左树│                              │D 右树 │
│        └──────────────────────────────┘      │
│                                              │
│              E 中央前院可走区                │
│       邮箱/路牌        水井        长椅       │
│                                              │
│  F 西侧小菜圃/花丛            G 东南后院路径 │
│                                              │
│  H 前景草/叶/光影，少量遮挡，不压住主路      │
└──────────────────────────────────────────────┘
```

## 分区设计

### A. 北侧村路和远景边界
- 坐标范围：`x=420..5620`, `y=520..1500`。
- 功能：通往 `Region_Village` 的视觉出口。
- 美术：泥路/石子路，从左北侧或中北侧进入画面，边缘有低矮树篱、远处田地或村屋提示。
- 玩法：道路必须和 `WalkableZone` 的北侧入口一致。

### B. 家屋主体和 veranda
- 坐标范围：房屋基准点约 `x=3160`, `y=1660`；视觉宽 `1500-1900`，高 `750-1050`。
- 功能：家的身份核心、门口检查、长椅休息。
- 美术：一层木造日式乡村家屋，瓦/铁皮屋顶，木格门，低矮檐口，阳光斑驳。
- 分层：`house_body`、`house_roof_occluder`、`veranda_floor`、`door/detail`。
- 遮挡：屋檐可遮住玩家头部/上身，但不能遮住脚下路径判断。

### C. 左侧大树
- 坐标范围：树根约 `x=1420`, `y=1220`。
- 功能：画面深度、光影来源、左侧边界。
- 美术：大树体量偏左上，树冠向中上方伸展。
- 分层：`tree_left_trunk` 在 YSort，`tree_left_canopy_occluder` 为遮挡层。
- 玩法：树干碰撞小，树冠只遮局部，不盖住主出口。

### D. 右侧果树/柿子树
- 坐标范围：树根约 `x=4630`, `y=1660`。
- 功能：平衡右侧画面、提供遮挡和季节感。
- 美术：较左树略小，树冠更圆，允许少量果实色点。
- 分层：`tree_right_trunk`、`tree_right_canopy_occluder`。

### E. 中央前院可走区
- 坐标范围：`x=1600..4550`, `y=1550..2850`。
- 功能：主移动空间、玩家出生空间。
- 美术：草地、压实泥土、踏石、稀疏花草。
- 玩法：这是视觉最清晰区域，不能被高对比纹理或大遮挡切碎。

### F. 西侧小菜圃/花丛
- 坐标范围：`x=520..2100`, `y=1520..2860`。
- 功能：生活感和后续小交互扩展。
- 美术：低矮菜畦、花丛、工具痕迹。
- 玩法：低矮 detail 层，不遮玩家脚。

### G. 东南 BackFarm 路径
- 坐标范围：`x=3650..4550`, `y=2500..3600`。
- 功能：通往 `Region_BackFarm`。
- 美术：从前院绕向屋后的小路，草边逐渐收窄。
- 玩法：必须清晰指向 `BackyardFarmEntrance`，避免被长椅或树冠误导。

### H. 前景草和光影
- 坐标范围：前景主要在 `y=3080..4096`，左右两侧为主。
- 功能：增加层次。
- 美术：前景草、少量花、树叶投影、斑驳光。
- 玩法：前景遮挡只压边缘，不遮主要交互点。

## 玩法空间
必须保留以下空间：

- 默认出生点：中央前院，约 `x=3072`, `y=2280`。
- 休息点：家屋/veranda 附近，约 `x=4110`, `y=2410`。
- 邮箱：前院左中，约 `x=2370`, `y=2140`。
- 水井：前院右中，约 `x=3600`, `y=2200`。
- 路牌：北/东出口附近，约 `x=5180`, `y=1420`。
- BackFarm 入口：东南/南侧，约 `x=4200`, `y=3370`。

## 3D 底模要求
3D 底模只解决这些问题：

- 地面高低和路径走向。
- 房屋体块、屋檐深度、门口/veranda 关系。
- 树干位置、树冠体积、遮挡范围。
- 主光源方向和投影参考。
- 相机固定视角和资产分区。

3D 底模不追求最终材质，不进入运行时。

## 高质量资产生产清单

第一批必须生产：

- `region_home_area_base_full_v001.png`
- `region_home_area_ground_yard_v001.png`
- `region_home_area_path_village_road_v001.png`
- `region_home_area_path_back_farm_v001.png`
- `region_home_area_house_body_v001.png`
- `region_home_area_house_roof_occluder_v001.png`
- `region_home_area_veranda_floor_v001.png`
- `region_home_area_tree_left_trunk_v001.png`
- `region_home_area_tree_left_canopy_occluder_v001.png`
- `region_home_area_tree_right_trunk_v001.png`
- `region_home_area_tree_right_canopy_occluder_v001.png`
- `region_home_area_foreground_grass_v001.png`
- `region_home_area_shadow_dappled_v001.png`
- `region_home_area_light_overlay_v001.png`

第二批再做：

- mailbox、well、bench、road sign、cat bed、garden tools、small flowers、fallen leaves。

## 接入验收
接入 Godot 前：

- 设计图或 3D 底模方案通过视觉审查。
- 所有资产都来自同一构图，不是拼贴碎片。
- 透明边缘无明显 matte/fringe。
- 每个导出层有 origin、anchor、z-index/YSort 说明。

接入 Godot 后：

- `Region_HomeArea` 能加载。
- 玩家比例正确。
- 可走区和地面图一致。
- 屋檐/树冠/前景草遮挡符合预期。
- HomeArea -> BackFarm 和 HomeArea -> Village 出口仍清晰。
