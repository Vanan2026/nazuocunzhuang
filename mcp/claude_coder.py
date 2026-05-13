#!/usr/bin/env python3
"""
Claude Code Generator for Godot
直接通过命令行调用 Claude 生成 GDScript 代码
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Optional

def load_env():
    """加载环境变量"""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

def get_anthropic_client():
    """获取 Anthropic 客户端"""
    try:
        from anthropic import Anthropic
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            api_key = os.environ.get("CLAUDE_API_KEY")
        if not api_key:
            print("Error: ANTHROPIC_API_KEY not set")
            return None
        return Anthropic(api_key=api_key)
    except ImportError:
        print("Error: anthropic package not installed")
        print("Install with: pip install anthropic")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def generate_gdscript(description: str, output_path: Optional[str] = None, template: str = "node2d") -> str:
    """生成 GDScript 代码"""
    client = get_anthropic_client()
    if not client:
        return ""
    
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
    # 重力
    if not is_on_floor():
        velocity.y += gravity * delta
    
    # 移动
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
    
    prompt = f"""你是一个专业的 Godot 4.6 游戏开发助手。请根据以下描述生成 GDScript 代码。

要求：
1. 使用 Godot 4.6 GDScript 语法
2. 添加类型提示
3. 添加中文注释
4. 遵循 Godot 最佳实践

基础模板：
{base_template}

需要实现的功能：
{description}

请只输出代码，代码必须是可以直接使用的完整脚本。不要输出任何解释。"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        code = response.content[0].text
        # 提取代码块中的内容
        if "```" in code:
            parts = code.split("```")
            for i, part in enumerate(parts):
                if i % 2 == 1:  # 代码块
                    if part.startswith("gdscript"):
                        part = part[7:]
                    elif part.startswith("gd"):
                        part = part[2:]
                    code = part.strip()
                    break
        
        return code
    
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="Claude GDScript Code Generator")
    parser.add_argument("command", choices=["generate", "analyze", "help"], help="Command to execute")
    parser.add_argument("-d", "--description", help="Description of what to generate")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("-t", "--template", default="node2d", 
                        choices=["node2d", "characterbody2d", "area2d", "camera2d"],
                        help="Template type")
    parser.add_argument("-f", "--file", help="File to analyze")
    parser.add_argument("-p", "--prompt", help="Custom prompt")
    
    args = parser.parse_args()
    
    if args.command == "help":
        print("""
Claude GDScript Code Generator
==============================

Usage:
  python mcp/claude_coder.py generate -d "描述" [-o output.gd] [-t template]
  python mcp/claude_coder.py analyze -f script.gd

Templates:
  node2d       - 基础 Node2D 脚本
  characterbody2d - 角色控制器
  area2d       - 交互区域
  camera2d     - 相机跟随

Environment:
  Set ANTHROPIC_API_KEY to enable Claude API

Examples:
  python mcp/claude_coder.py generate -d "玩家射击系统" -t characterbody2d -o player_shoot.gd
  python mcp/claude_coder.py analyze -f player.gd
""")
        return
    
    if args.command == "generate":
        if not args.description and not args.prompt:
            print("Error: Specify -d or --prompt for description")
            return
        
        description = args.description or args.prompt
        print(f"Generating code with template: {args.template}...")
        
        code = generate_gdscript(description, args.output, args.template)
        
        if code and not code.startswith("Error"):
            if args.output:
                output_path = Path(args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                print(f"Code saved to: {args.output}")
            else:
                print(code)
        else:
            print(code if code else "Failed to generate code")
    
    elif args.command == "analyze":
        if not args.file:
            print("Error: Specify -f or --file for code file to analyze")
            return
        
        if not os.path.exists(args.file):
            print(f"Error: File not found: {args.file}")
            return
        
        with open(args.file, 'r', encoding='utf-8') as f:
            code = f.read()
        
        client = get_anthropic_client()
        if not client:
            return
        
        prompt = f"""请分析以下 GDScript 代码并提供改进建议：

```{code}```

请从以下方面分析：
1. 代码结构和设计
2. 潜在问题
3. 改进建议
4. Godot 最佳实践

请用中文回答。"""

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            print(response.content[0].text)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    load_env()
    main()