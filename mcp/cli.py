#!/usr/bin/env python3
"""
Claude MCP Server for Godot - Simplified Version
直接通过 Claude API 生成代码和进行游戏开发辅助
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List

def check_dependencies():
    """检查依赖"""
    try:
        import anthropic
        print("[MCP] Anthropic SDK available")
        return True
    except ImportError:
        print("[MCP] Warning: anthropic package not installed")
        print("[MCP] Install with: pip install anthropic")
        return False

def get_api_key() -> str:
    """获取 API Key"""
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        print("[MCP] Warning: ANTHROPIC_API_KEY not set")
    return key

def claude_generate_code(description: str, context: str = "") -> str:
    """使用 Claude 生成代码"""
    if not check_dependencies():
        return "ERROR: anthropic package not installed"
    
    api_key = get_api_key()
    if not api_key:
        return "ERROR: ANTHROPIC_API_KEY not set"
    
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        
        prompt = f"""你是一个专业的 Godot 4.6 游戏开发助手。请根据以下描述生成 GDScript 代码。

要求：
1. 使用 Godot 4.6 GDScript 语法
2. 添加类型提示
3. 添加中文注释
4. 遵循 Godot 最佳实践

描述：{description}

额外上下文：{context}

请只输出代码，不要解释。代码必须是可以直接使用的完整脚本。"""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    except Exception as e:
        return f"ERROR: {str(e)}"

def claude_analyze_code(code: str, question: str = "") -> str:
    """使用 Claude 分析代码"""
    if not check_dependencies():
        return "ERROR: anthropic package not installed"
    
    api_key = get_api_key()
    if not api_key:
        return "ERROR: ANTHROPIC_API_KEY not set"
    
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        
        prompt = f"""请分析以下 GDScript 代码：

```{code}```

{question if question else "请指出代码的问题和改进建议"}"""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    except Exception as e:
        return f"ERROR: {str(e)}"

def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("Claude MCP for Godot")
        print("Usage:")
        print("  python mcp/cli.py generate <description>")
        print("  python mcp/cli.py analyze <code_file>")
        print("")
        print("Environment variables:")
        print("  ANTHROPIC_API_KEY - Your Claude API key")
        return
    
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    
    if command == "generate":
        description = sys.argv[2] if len(sys.argv) > 2 else ""
        result = claude_generate_code(description)
        print(result)
    
    elif command == "analyze":
        code_file = sys.argv[2] if len(sys.argv) > 2 else ""
        if code_file and os.path.exists(code_file):
            with open(code_file, 'r', encoding='utf-8') as f:
                code = f.read()
            result = claude_analyze_code(code)
            print(result)
        else:
            print("ERROR: Code file not found")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()