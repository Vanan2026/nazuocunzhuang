# 12 — Runtime Migration Plan

版本：v0.1  
用途：避免新 `game/` 规范骨架和旧 `scenes/` / `scripts/` 可运行链路长期双轨失控。

## 当前事实

- 当前可运行入口仍是 `res://scenes/world/world.tscn`。
- Task 001 创建的 `game/` 结构是新规范骨架，尚未接管运行时。
- Task 002 创建的 `game/autoload/*.gd` 是新规范管理器骨架，暂不注册到 `project.godot`。

## 迁移原则

1. 不一次性切换主场景。
2. 不删除当前可验证运行链路。
3. 新系统先在 `game/` 下建立清晰接口。
4. 每次只迁移一个可验证功能面。
5. 迁移时优先用 Godot MCP / Godot AI 查看编辑器、场景和节点状态。
6. Godot MCP 必须先按 `http://127.0.0.1:8000/mcp` 的 streamable-http 协议直接 initialize，并通过 `session_manage(op="list")` / `editor_state` 确认 ready session；不要只看 `codex mcp list` 或通用 resource/list。
7. 如果 streamable-http 初始化失败、拿不到 `Mcp-Session-Id`，或没有 ready editor session，必须记录原因，并回退到 Godot headless 加载当前主场景和新目标场景。

## 收敛顺序

1. Task 002: 建立 `game/autoload/` 管理器骨架。
2. Task 003: 建立 `game/data/*.json` 和 DataRegistry 校验。
3. Task 004: 在 `game/` 下建立玩家和交互基类测试场景。
4. 当 `game/scenes/world/WorldRoot.tscn` 具备玩家移动和基础交互后，再评估是否切换 `project.godot` 主场景。
5. 切换前保留旧 `scenes/world/world.tscn` 作为回滚入口。

## 当前禁止

- 不把空 `game/scenes/Main.tscn` 设置为项目主场景。
- 不把旧 Autoload 直接删除。
- 不在旧 `scripts/` 和新 `game/autoload/` 同时实现同一完整系统逻辑。
- 不引入战斗、怪物、伤害、武器、血量、击杀或掉落系统。
- 不在未按 streamable-http 协议探测 Godot MCP 的情况下直接把 headless CLI 当作唯一验证路径。Codex 包装层未暴露 MCP 工具不等于 Godot MCP 服务不可用。

## Task 002 验收

- 12 个推荐 Autoload 脚本存在。
- 脚本有基本信号、属性和职责接口。
- 不实现完整业务逻辑。
- 不注册到 `project.godot`。
- 通过 `tools/validate_task002_autoload_skeletons.py`。
