# Greenfield P0 Art Bible

参考母版：`production/assets/references/style_mother/greenfield_p0_style_mother_2026-05-27.jpg`

## 视觉定位

《那座村庄》P0 采用温暖低饱和、手绘纸感、木质 UI、固定 3/4 俯视的田园慢生活风格。参考图是美术圣经和体验目标，不是逐像素复刻对象。

关键词：

- warm low saturation
- storybook
- paper texture
- wood frame
- 3/4 top-down
- cozy village life
- modular Godot-ready assets

禁止：

- 战斗、怪物、武器、伤害、击杀、战利品掉落。
- 科幻 HUD、霓虹高饱和、写实照片风、黑暗恐怖风。
- 直接复制任何具体商业游戏、动画、地图或角色。

## 场景规范

P0 场景以 `HomeArea` 为垂直切片，不先做全村。

必要元素：

- 小屋
- 泥土路
- 农田
- 水井
- 信箱
- 栅栏
- 树木
- 花丛
- 可遮挡角色的屋檐、树冠或前景植物

场景层级：

```text
HomeArea.tscn
├── BaseSprite
├── YSortObjects
├── ForegroundOcclusion
├── CollisionLayer
├── InteractionPoints
├── NavigationRegion2D
└── PlayerSpawnPoint
```

分层规则：

- `mother/base/foreground_occlusion/collision_mask` 共享画布、原点、比例和透视。
- `foreground_occlusion` 保持 full-canvas alpha，不裁剪到物体边界。
- 碰撞和交互点来自数据或清晰命名节点，不从图像猜。

## UI 规范

UI 必须像手账、木牌、羊皮纸和村庄公告板，不像现代软件后台。

核心材料：

- 羊皮纸面板
- 木质边框
- 藤蔓或小叶装饰
- 手绘小图标
- 暖棕描边
- 柔和圆角按钮

UI 层级：

- 左上：时间、季节、天气。
- 右上：金币、体力、关系或基础状态。
- 底部：快捷栏。
- 中心与下中区域保持可游玩，不常驻大面板。

所有界面复用：

```text
ui/theme/greenfield_theme.tres
ui/components/GFPanel.tscn
ui/components/GFButton.tscn
ui/components/GFItemSlot.tscn
ui/components/GFTabBar.tscn
```

## 角色规范

地图角色：

- Q 版 3.5 到 4 头身。
- 3/4 top-down。
- 大色块、圆润比例、少细节。
- 脚底中心为 origin。

对话立绘：

- 半身或胸像。
- 表情至少 neutral/happy/surprised 或 neutral/happy/shy。
- 用于 DialogueScreen、GiftSelection、RelationshipFeedback。

## 图标规范

图标用于背包、采集、送礼、任务。第一批图标必须清晰、低饱和、手绘描边，64x64 起步。

图标不得硬编码到界面脚本中，只能从 `data/items.json` 等数据表解析路径。

## 验收原则

每个资产或界面必须满足：

- 缩小到游戏尺寸仍能识别。
- 风格接近 style mother 的纸木田园语言。
- Godot 可导入。
- 路径和命名可替换。
- 不声明 launch quality，除非有明确人工审批和验证证据。
