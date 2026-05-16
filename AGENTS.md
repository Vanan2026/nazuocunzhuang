# AGENTS.md — Codex 项目执行规则

本文件是《那座村庄》仓库内 Codex、代码代理或自动化开发代理的最高优先级项目说明。任何实现、重构、美术占位资产生成、数据表生成和文档更新都必须遵守本文件。

---

## 1. 项目身份

项目名：那座村庄  
类型：无战斗治愈系乡村生活模拟  
引擎：Godot 4.x  
视角：固定 3/4 俯视 2D  
美术方向：模块化 2D 治愈绘本风  
核心体验：慢生活、修复、关系、四季、轻探索、温柔秘密

---

## 2. 绝对禁止事项

Codex 不得加入以下内容：

- 战斗系统、怪物、伤害、武器、护甲、血量、击杀、战利品掉落。
- 硬核生存惩罚，例如死亡、永久损失、饥饿致死、装备掉落。
- 高压力倒计时、强制失败、付费抽卡、PVP、掠夺。
- 直接复制任何现有游戏、美术、角色、地图或文本。
- 在提示词中要求“某某知名游戏/动画的风格复刻”。只能使用通用风格描述。
- 未经说明就改变项目方向、视角、画风、核心循环或文件结构。

如果用户或任务要求“增加战斗”，Codex 必须改为提供非战斗替代方案，例如“净化、修复、安抚、解谜、避让、照料、供奉”。

---

## 3. 核心设计原则

每个系统必须服务以下至少一项：

1. **日常舒适感**：让玩家每天有温和目标。
2. **村庄恢复感**：玩家行为让环境、NPC、设施产生变化。
3. **人物关系感**：NPC 不是商店机器，而是有作息、记忆和个人问题。
4. **四季变化感**：同一地点在不同季节有资源、视觉和事件差异。
5. **隐藏发现感**：秘密要藏在生活中，而不是通过战斗关卡表达。

---

## 4. 技术原则

### 4.1 Godot 代码规范

- 使用 Godot 4.x。
- GDScript 尽量使用类型标注。
- 使用 `snake_case` 命名变量和函数。
- 使用 `PascalCase` 命名类、场景和资源类型。
- 系统应数据驱动，不把作物、NPC、物品硬编码在逻辑中。
- 优先使用 autoload 单例管理全局状态。
- 使用 signal 进行跨系统通讯，避免强耦合。
- 每次实现功能时优先考虑保存/读取兼容。

### 4.2 推荐 Autoload

```text
GameState.gd
EventBus.gd
TimeManager.gd
SeasonManager.gd
WeatherManager.gd
InventoryManager.gd
RelationshipManager.gd
QuestManager.gd
DialogueManager.gd
SaveManager.gd
DataRegistry.gd
SceneRouter.gd
```

### 4.3 推荐目录

```text
game/
  autoload/
  systems/
  entities/player/
  entities/npc/
  entities/interactable/
  scenes/world/
  scenes/home/
  scenes/ui/
  data/
assets/
  art/characters/
  art/environments/
  art/props/
  art/ui/
  audio/music/
  audio/sfx/
docs/
data/
```

### 4.4 Godot MCP / Godot AI 工具优先级

- 本项目已配置 Godot MCP / Godot AI 工具，Codex 在需要查看、操作、验证 Godot 工程状态时，应优先使用 Godot MCP。
- 当前 Codex CLI 配置中的服务器名为 `godot-ai`，地址为 `http://127.0.0.1:8000/mcp`。
- 适用场景包括：读取编辑器状态、查看当前场景、检查节点树、操作场景、运行 Godot 相关验证、辅助定位 Godot 资源或场景问题。
- 正确连接方式是 streamable-http MCP：
  1. 向 `http://127.0.0.1:8000/mcp` 发送 MCP `initialize` 请求，请求头包含 `Accept: application/json, text/event-stream` 与 `Content-Type: application/json`。
  2. 从响应头读取 `Mcp-Session-Id`。
  3. 用同一 session id 发送 `notifications/initialized`。
  4. 后续用 `tools/call` 调用 `session_manage(op="list")`、`session_activate`、`editor_state`、`scene_open`、`scene_get_hierarchy` 等工具。
- 不要只根据 `codex mcp list`、`codex mcp get godot-ai` 或通用 `list_mcp_resources` 失败就判断 Godot MCP 不可用；本项目中这些 Codex 包装层可能不同步。必须先按 streamable-http MCP 协议直接探测 `/mcp`。
- 如果按上述 streamable-http 方式仍无法 initialize、拿不到 session，或 `session_manage(op="list")` 没有 ready 的编辑器会话，才记录具体原因并回退到 Godot headless CLI / 项目验证脚本。
- 不得因为 MCP 不可用就跳过验证；只能改用可验证的回退方式。
- 原始 HTTP `/mcp` 端点使用 streamable-http MCP 协议，不应当作普通一次性 JSON-RPC POST 随意调用。

---

## 5. 美术资产生成原则

若 Codex 需要生成占位图、SVG、PNG、导入表或资源脚本，必须遵守：

- 风格：温暖低饱和、轻绘本感、清晰轮廓、固定 3/4 俯视。
- 角色：3.5 到 4 头身，朴素、圆润、少细节，大色块。
- 场景：模块化，远景柔和，交互物清晰。
- UI：手账/木牌/纸张风，不做科幻 HUD。
- 输出文件：透明背景 PNG 或可转换 SVG，命名符合 `docs/05_ART_ASSET_BIBLE.md`。
- 所有美术占位图都要可替换，不要让代码依赖具体图片尺寸以外的不可控细节。

---

## 6. 任务执行方式

每次接到任务时，Codex 必须：

1. 读取相关文档。
2. 总结将修改的文件。
3. 只实现当前任务范围内的内容。
4. 不引入无关功能。
5. 保持无战斗、治愈、模块化、数据驱动。
6. 完成后给出：修改清单、测试方式、已知限制。

---

## 7. 验收底线

一个功能只有满足以下条件才算完成：

- 能在 Godot 中运行或被明确标注为文档/数据任务。
- 不破坏已有功能。
- 不违背无战斗设定。
- 命名、目录、数据结构符合文档。
- 如果涉及 UI 或资产，必须符合美术圣经。
- 如果涉及系统，必须有最小可验证场景或测试步骤。

---

## 8. 默认实现优先级

先做垂直切片，不做大而空的全量系统：

```text
玩家移动
→ 时间/日期/季节
→ 交互物
→ 农田
→ 背包
→ NPC 对话
→ 送礼与关系
→ 村庄修复
→ 事件触发
→ 保存读取
→ UI 美化
→ 扩展内容
```

---

## 9. 项目口径

Codex 在生成任何文案、注释、README、UI 文本时，应保持以下口径：

> 《那座村庄》不是冒险战斗游戏，而是一款关于回家、整理生活、修复村庄、认识人、度过四季的治愈系乡村生活模拟游戏。
