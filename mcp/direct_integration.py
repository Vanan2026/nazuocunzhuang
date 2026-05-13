#!/usr/bin/env python3
"""
Claude Code Direct Integration for Trae
直接调用 Claude Code CLI 的游戏工作室能力

用法：
1. 通过 Trae MCP 配置调用此脚本
2. 或者直接在 Trae 对话中调用 Python 函数
3. Claude Code CLI 会在后台处理请求

功能：
- 代码生成 (godot_generate_code)
- 场景分析 (godot_analyze_scene)  
- 代码审查 (godot_analyze_code)
- 开发帮助 (godot_dev_help)
"""

import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

# 项目路径
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

# Claude Code CLI 路径（在 PATH 中或常见位置）
CLAUDE_CLI_PATHS = [
    "claude",  # PATH 中
    "C:\\Users\\23732\\AppData\\Roaming\\npm\\claude.cmd",
    "C:\\Program Files\\Claude\\claude.exe",
]

def find_claude_cli() -> Optional[str]:
    """查找 Claude Code CLI"""
    for path in CLAUDE_CLI_PATHS:
        try:
            result = subprocess.run(
                [path, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=True
            )
            if result.returncode == 0:
                return path
        except:
            continue
    return None

def run_claude_command(prompt: str, timeout: int = 120) -> Dict[str, Any]:
    """
    运行 Claude Code 命令
    
    Args:
        prompt: 要发送给 Claude Code 的提示
        timeout: 超时时间（秒）
    
    Returns:
        包含 success、output、error 的字典
    """
    cli_path = find_claude_cli()
    
    if not cli_path:
        return {
            "success": False,
            "error": "Claude Code CLI not found",
            "hint": "Install Claude Code: npm install -g @anthropic-ai/claude-code"
        }
    
    # 构建完整的 prompt
    full_prompt = f"""{prompt}

项目路径: {PROJECT_PATH}
游戏类型: Godot 4.6 2D 日式田园治愈游戏
引擎版本: Godot 4.6.1

请直接生成代码，不要询问确认。"""

    try:
        # 使用 --print 选项（如果支持）或 -p
        cmd = [cli_path, "--print"]
        
        result = subprocess.run(
            cmd,
            input=full_prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=PROJECT_PATH,
            shell=True,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"}
        )
        
        return {
            "success": result.returncode == 0 or len(result.stdout) > 0,
            "output": result.stdout if result.stdout else result.stderr,
            "error": None if result.returncode == 0 else result.stderr
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Command timed out after {timeout}s"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def godot_generate_code(description: str, template: str = "node2d") -> str:
    """
    生成 GDScript 代码
    
    Args:
        description: 代码功能描述
        template: 模板类型 (node2d, characterbody2d, area2d, camera2d)
    
    Returns:
        生成的代码字符串
    """
    templates = {
        "node2d": """extends Node2D

# 节点引用
@onready var sprite: Sprite2D = $Sprite2D

func _ready() -> void:
    # 初始化代码
    pass

func _process(delta: float) -> void:
    # 每帧更新
    pass""",
        "characterbody2d": """extends CharacterBody2D

@export var speed: float = 200.0
@export var jump_velocity: float = -400.0

var gravity: float = ProjectSettings.get_setting("physics/2d/default_gravity")

func _ready() -> void:
    pass

func _physics_process(delta: float) -> void:
    if not is_on_floor():
        velocity.y += gravity * delta
    
    var direction := Input.get_axis("ui_left", "ui_right")
    if direction:
        velocity.x = direction * speed
    else:
        velocity.x = move_toward(velocity.x, 0, speed)
    
    move_and_slide()""",
        "area2d": """extends Area2D

signal interacted

@export var interaction_hint: String = "按 E 交互"

func _ready() -> void:
    body_entered.connect(_on_body_entered)
    body_exited.connect(_on_body_exited)

func _on_body_entered(body: Node) -> void:
    if body.is_in_group("player"):
        show_hint(true)

func _on_body_exited(body: Node) -> void:
    if body.is_in_group("player"):
        show_hint(false)

func on_interact(interactor: Node) -> void:
    print("[交互] 执行交互")
    emit_signal("interacted")

func show_hint(show: bool) -> void:
    var hint = get_node_or_null("HintLabel")
    if hint:
        hint.visible = show

func get_interaction_hint() -> String:
    return interaction_hint""",
        "camera2d": """extends Camera2D

@export var target: Node2D
@export var follow_speed: float = 6.0

func _ready() -> void:
    pass

func _process(delta: float) -> void:
    if target:
        global_position = global_position.lerp(target.global_position, 1.0 - exp(-follow_speed * delta))"""
    }
    
    base_template = templates.get(template, templates["node2d"])
    
    prompt = f"""生成 GDScript 代码（Godot 4.6）：

模板类型: {template}

基础代码结构:
{base_template}

需要实现的功能:
{description}

要求：
1. 使用 Godot 4.6 GDScript 语法
2. 添加类型提示
3. 添加中文注释
4. 遵循最佳实践

只输出代码，不要其他内容。"""

    result = run_claude_command(prompt)
    
    if result["success"]:
        return result["output"]
    else:
        return f"Error: {result.get('error', 'Unknown error')}"

def godot_analyze_scene(scene_path: str) -> str:
    """
    分析 Godot 场景文件
    
    Args:
        scene_path: 场景文件路径（相对于项目根目录）
    
    Returns:
        分析结果字符串
    """
    full_path = os.path.join(PROJECT_PATH, scene_path)
    
    if not os.path.exists(full_path):
        return f"Error: Scene not found: {scene_path}"
    
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    prompt = f"""分析以下 Godot 场景文件 (.tscn)：

文件: {scene_path}

内容（前3000字符）:
{content[:3000]}

请分析：
1. 场景结构和节点层级
2. 潜在问题
3. 改进建议
4. 最佳实践建议

用中文回答。"""

    result = run_claude_command(prompt)
    
    if result["success"]:
        return result["output"]
    else:
        return f"Error: {result.get('error', 'Unknown error')}"

def godot_analyze_code(code_path: str) -> str:
    """
    分析 GDScript 代码
    
    Args:
        code_path: 代码文件路径（相对于项目根目录）
    
    Returns:
        分析结果字符串
    """
    full_path = os.path.join(PROJECT_PATH, code_path)
    
    if not os.path.exists(full_path):
        return f"Error: Code file not found: {code_path}"
    
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    prompt = f"""分析以下 GDScript 代码：

文件: {code_path}

代码内容（前3000字符）:
{content[:3000]}

请分析：
1. 代码结构和设计
2. 潜在问题
3. 改进建议
4. Godot 最佳实践

用中文回答。"""

    result = run_claude_command(prompt)
    
    if result["success"]:
        return result["output"]
    else:
        return f"Error: {result.get('error', 'Unknown error')}"

def godot_dev_help(question: str) -> str:
    """
    获取游戏开发帮助
    
    Args:
        question: 开发问题
    
    Returns:
        回答字符串
    """
    prompt = f"""{question}

项目背景：
- 引擎: Godot 4.6.1
- 游戏类型: 2D 日式田园治愈游戏
- 项目路径: {PROJECT_PATH}
- 语言: GDScript

请提供详细的技术建议和代码示例。用中文回答。"""

    result = run_claude_command(prompt)
    
    if result["success"]:
        return result["output"]
    else:
        return f"Error: {result.get('error', 'Unknown error')}"

def list_project_scenes(directory: str = "scenes") -> list:
    """列出项目中的所有场景文件"""
    scenes = []
    search_path = os.path.join(PROJECT_PATH, directory)
    
    if not os.path.exists(search_path):
        return scenes
    
    for root, dirs, files in os.walk(search_path):
        for file in files:
            if file.endswith('.tscn'):
                rel_path = os.path.relpath(os.path.join(root, file), PROJECT_PATH)
                scenes.append(rel_path)
    
    return sorted(scenes)

def list_project_scripts(directory: str = "scripts") -> list:
    """列出项目中的所有脚本文件"""
    scripts = []
    search_path = os.path.join(PROJECT_PATH, directory)
    
    if not os.path.exists(search_path):
        return scripts
    
    for root, dirs, files in os.walk(search_path):
        for file in files:
            if file.endswith('.gd'):
                rel_path = os.path.relpath(os.path.join(root, file), PROJECT_PATH)
                scripts.append(rel_path)
    
    return sorted(scripts)

# CLI 入口
def main():
    if len(sys.argv) < 2:
        print("Claude Code Game Studio Integration")
        print("")
        print("Usage:")
        print("  python mcp/direct_integration.py generate <description> [-t template]")
        print("  python mcp/direct_integration.py analyze-scene <scene_path>")
        print("  python mcp/direct_integration.py analyze-code <code_path>")
        print("  python mcp/direct_integration.py help <question>")
        print("  python mcp/direct_integration.py list-scenes")
        print("  python mcp/direct_integration.py list-scripts")
        print("")
        print("Templates: node2d, characterbody2d, area2d, camera2d")
        return
    
    command = sys.argv[1]
    
    if command == "generate":
        description = sys.argv[2] if len(sys.argv) > 2 else ""
        template = "node2d"
        
        for i, arg in enumerate(sys.argv):
            if arg == "-t" and i + 1 < len(sys.argv):
                template = sys.argv[i + 1]
        
        result = godot_generate_code(description, template)
        print(result)
    
    elif command == "analyze-scene":
        scene_path = sys.argv[2] if len(sys.argv) > 2 else ""
        result = godot_analyze_scene(scene_path)
        print(result)
    
    elif command == "analyze-code":
        code_path = sys.argv[2] if len(sys.argv) > 2 else ""
        result = godot_analyze_code(code_path)
        print(result)
    
    elif command == "help":
        question = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        result = godot_dev_help(question)
        print(result)
    
    elif command == "list-scenes":
        scenes = list_project_scenes()
        print(f"Found {len(scenes)} scene files:")
        for scene in scenes[:50]:
            print(f"  {scene}")
        if len(scenes) > 50:
            print(f"  ... and {len(scenes) - 50} more")
    
    elif command == "list-scripts":
        scripts = list_project_scripts()
        print(f"Found {len(scripts)} script files:")
        for script in scripts[:50]:
            print(f"  {script}")
        if len(scripts) > 50:
            print(f"  ... and {len(scripts) - 50} more")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()