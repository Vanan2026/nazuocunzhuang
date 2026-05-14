# Trae MCP 配置 - Claude Code 游戏工作室

本目录包含 Claude Code 游戏工作室的 MCP 服务器配置。

## 文件说明

- `direct_integration.py` - 直接调用 Claude Code CLI 的 MCP 服务器
- `claude_code_mcp.py` - 完整 MCP 服务器实现
- `config.json` - Trae MCP 配置

## 在 Trae 中配置

### 方式 1：通过 Claude Code 配置文件（推荐）

将以下配置添加到项目的 `.claude/settings.json` 中：

```json
{
  "mcpServers": {
    "godot-game-studio": {
      "command": "python",
      "args": ["D:/那个村庄/mcp/direct_integration.py"],
      "env": {
        "PROJECT_PATH": "D:/那个村庄"
      }
    }
  }
}
```

### 方式 2：通过 Trae IDE 设置

1. 打开 Trae IDE 设置
2. 找到 MCP Servers 配置
3. 添加新服务器：
   - Name: `godot-game-studio`
   - Command: `python`
   - Arguments: `["D:/那个村庄/mcp/direct_integration.py"]`
   - Environment: `PROJECT_PATH=D:/那个村庄`

## Claude Code CLI 配置（使用 MiniMax）

你的项目已经配置了 MiniMax 作为 API 提供商：

```json
"env": {
  "ANTHROPIC_BASE_URL": "https://api.minimaxi.com/anthropic",
  "ANTHROPIC_AUTH_TOKEN": "sk-cp-...",  // MiniMax API Key
  "ANTHROPIC_MODEL": "MiniMax-M2.7"
}
```

这意味着 Claude Code CLI 会自动使用 MiniMax 的 API。

## 可用工具

### godot_generate_code
生成 GDScript 代码

```python
# 在 Trae 中调用
result = godot_generate_code("玩家射击系统", "characterbody2d")
```

### godot_analyze_scene
分析 Godot 场景文件

```python
result = godot_analyze_scene("scenes/world/world.tscn")
```

### godot_analyze_code
分析 GDScript 代码

```python
result = godot_analyze_code("scripts/player_controller.gd")
```

### godot_dev_help
获取游戏开发帮助

```python
result = godot_dev_help("如何实现玩家和NPC的对话系统？")
```

## 命令行使用

```bash
# 生成代码
python mcp/direct_integration.py generate "玩家移动系统" -t characterbody2d

# 分析场景
python mcp/direct_integration.py analyze-scene scenes/regions/region_home_area.tscn

# 分析代码
python mcp/direct_integration.py analyze-code scripts/player_controller.gd

# 获取帮助
python mcp/direct_integration.py help "如何实现存档系统"

# 列出场景
python mcp/direct_integration.py list-scenes

# 列出脚本
python mcp/direct_integration.py list-scripts
```

## 验证 Claude Code CLI

```bash
claude --version
```

如果已安装，应该显示版本号。

如果未安装：
```bash
npm install -g @anthropic-ai/claude-code
```

## 注意事项

1. Claude Code CLI 会在后台调用 MiniMax API
2. 所有工具都会自动使用项目上下文
3. 代码生成后会返回完整的 GDScript 代码
4. 分析功能会提供改进建议