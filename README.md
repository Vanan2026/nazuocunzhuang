# 那座村庄

《那座村庄》是一款无战斗、低压力、治愈系乡村生活模拟游戏。玩家回到一座旧村庄，在修复老屋、经营庭院、种植作物、拜访村民、度过四季的日常中，让村庄慢慢恢复生机，并发现被时间和自然藏起来的温柔秘密。

## 当前项目口径

- 引擎：Godot 4.x
- 类型：固定 3/4 俯视 2D / 2.5D 乡村生活模拟
- 核心：慢生活、修复、关系、四季、轻探索、温柔秘密
- 禁止：战斗、怪物、伤害、武器、血量、击杀、战利品掉落、高压失败惩罚

## 新会话启动顺序

1. 读取 `AGENTS.md`
2. 读取 `.codex/status.md`
3. 读取 `00_README_FOR_CODEX.md`
4. 读取 `docs/10_CODEX_TASKS.md`
5. 检查 Godot MCP / Godot AI 是否可用
6. 按 `.codex/status.md` 的“下一步”继续

如果需要恢复更完整上下文，再读取：

- `.codex/context/project_state.md`
- `.codex/context/roadmap.md`
- `.codex/context/decisions.md`

## 当前结构

```text
game/                 新规范 Godot 运行结构骨架
assets/art/           新规范美术资产入口
assets/audio/         新规范音频资产入口
docs/                 当前设计、技术、任务、验收文档
data/                 当前内容数据表和风格配置
prompts/              Codex 主提示词
scenes/ scripts/      现有可运行 Godot 2D/2.5D 世界链路
sprites/ audio/       现有运行时素材
production/           素材生产和候选包
tools/                验证、导入、构建和生产脚本
.codex/               项目状态、路线图、决策、错误和改进记录
```

## Godot MCP 规则

- 优先使用 Codex MCP 中的 `godot-ai` 服务器处理 Godot 工程查看、编辑器状态、场景检查和验证相关工作。
- 当前配置：`godot-ai` -> `http://127.0.0.1:8000/mcp`。
- 正确使用方式：该地址是 streamable-http MCP 端点。先发送 MCP `initialize`，请求头带 `Accept: application/json, text/event-stream` 和 `Content-Type: application/json`；从响应头保存 `Mcp-Session-Id`；再发送 `notifications/initialized`；之后用 `tools/call` 调用 `session_manage(op="list")`、`session_activate`、`editor_state`、`scene_open`、`scene_get_hierarchy` 等工具。
- 不要只因为 `codex mcp list`、`codex mcp get godot-ai` 或通用 `list_mcp_resources` 失败就判定 MCP 不可用；这些包装层在当前会话可能不同步。必须先按 streamable-http 协议直接探测 `/mcp`。
- 如果 streamable-http 初始化失败、拿不到 session id，或 `session_manage(op="list")` 没有 ready 的 Godot editor session，必须在状态记录中写明原因，并回退到 Godot headless CLI 验证。
- Godot headless CLI 是回退手段，不是首选手段。

## 当前任务状态

Task 001 已落地：

- 已确认仓库存在 `project.godot`
- 已创建 `game/` 推荐目录骨架
- 已创建 `assets/art/` 与 `assets/audio/` 骨架
- 已添加 README 占位说明以便空目录可追踪
- 已添加可加载的 `game/scenes/Main.tscn`
- 已添加可加载的 `game/scenes/world/WorldRoot.tscn`

Task 002 已落地：

- 已添加 `game/autoload/` 下 12 个推荐管理器脚本骨架
- 已添加 Task 002 文本结构验证器
- 已添加 Task 002 Godot 脚本加载验证器
- 新 Autoload 暂不注册到 `project.godot`，避免和旧运行链路双轨冲突

当前 `project.godot` 的启动场景仍是现有可运行入口 `res://scenes/world/world.tscn`。不要把启动场景切到新 `game/` 骨架，直到后续任务把它接成可玩流程。

## 下一步

执行 `docs/10_CODEX_TASKS.md` 的 Task 003：建立 `game/data/*.json` 和 DataRegistry 加载/校验。
