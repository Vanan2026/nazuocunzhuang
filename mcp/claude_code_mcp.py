#!/usr/bin/env python3
"""
Claude Code Game Studio MCP Server
通过 Claude Code CLI 集成游戏开发能力到 Trae IDE

功能：
- 生成 GDScript 代码
- 分析 Godot 场景
- 协助项目开发
- 执行代码审查

使用方式：
1. 在 Trae 中配置 MCP 连接
2. 通过自然语言描述需求
3. Claude Code CLI 在后台处理请求
"""

import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

# 配置
SERVER_NAME = "godot-game-studio"
SERVER_VERSION = "1.0.0"
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLAUDE_CLI_PATH = "claude"  # 假设 claude 在 PATH 中

class ClaudeCodeRunner:
    """Claude Code CLI 运行器"""
    
    def __init__(self, project_path: str = PROJECT_PATH):
        self.project_path = project_path
        self.cli_path = self._find_claude_cli()
    
    def _find_claude_cli(self) -> Optional[str]:
        """查找 Claude Code CLI"""
        # 检查常见位置
        paths_to_check = [
            "claude",  # PATH 中
            "C:\\Users\\23732\\AppData\\Roaming\\npm\\claude.cmd",
            "C:\\Program Files\\Claude\\claude.exe",
            os.path.expanduser("~\\AppData\\Roaming\\npm\\claude.cmd"),
        ]
        
        for path in paths_to_check:
            try:
                result = subprocess.run(
                    [path, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return path
            except:
                continue
        
        return None
    
    def is_available(self) -> bool:
        """检查 Claude Code 是否可用"""
        return self._find_claude_cli() is not None
    
    def execute_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行游戏开发任务"""
        if not self.is_available():
            return {
                "success": False,
                "error": "Claude Code CLI not found. Please install Claude Code.",
                "hint": "npm install -g @anthropic-ai/claude-code"
            }
        
        # 构建 prompt
        project_context = f"""
项目路径: {self.project_path}
游戏类型: Godot 4.6 2D 日式田园治愈游戏
场景目录: scenes/
脚本目录: scripts/
资源目录: sprites/

当前任务: {task}

"""
        if context:
            project_context += f"\n上下文: {json.dumps(context, ensure_ascii=False)}\n"
        
        # 准备 Claude Code 命令
        # 注意：Claude Code 主要用于交互式会话
        # 这里我们使用 --print 选项（如果支持）或生成临时脚本
        
        try:
            # 尝试使用 claude --print 命令
            result = subprocess.run(
                [self.cli_path, "--print", "--no-input", project_context],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=self.project_path
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# 全局实例
runner = ClaudeCodeRunner(PROJECT_PATH)

# MCP 服务器实现
def handle_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """处理 MCP 请求"""
    method = request.get("method", "")
    params = request.get("params", {})
    
    if method == "initialize":
        return {
            "protocolVersion": "1.0",
            "capabilities": {
                "tools": True,
                "resources": True
            },
            "serverInfo": {
                "name": SERVER_NAME,
                "version": SERVER_VERSION
            }
        }
    
    elif method == "tools/list":
        return {
            "tools": [
                {
                    "name": "godot_generate_code",
                    "description": "生成 GDScript 代码（调用 Claude Code）",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "template": {"type": "string", "enum": ["node2d", "characterbody2d", "area2d", "camera2d"]}
                        }
                    }
                },
                {
                    "name": "godot_analyze_scene",
                    "description": "分析 Godot 场景文件",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "scene_path": {"type": "string"}
                        }
                    }
                },
                {
                    "name": "godot_analyze_code",
                    "description": "分析 GDScript 代码",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "code_path": {"type": "string"}
                        }
                    }
                },
                {
                    "name": "godot_dev_help",
                    "description": "获取游戏开发帮助",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string"}
                        }
                    }
                }
            ]
        }
    
    elif method == "tools/call":
        tool_name = params.get("name", "")
        tool_args = params.get("arguments", {})
        
        if tool_name == "godot_generate_code":
            description = tool_args.get("description", "")
            template = tool_args.get("template", "node2d")
            
            context = {
                "template": template,
                "language": "GDScript",
                "engine": "Godot 4.6"
            }
            
            result = runner.execute_task(
                f"生成 {template} 类型的 GDScript 代码。{description}",
                context
            )
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result.get("output", result.get("error", "Unknown error"))
                    }
                ]
            }
        
        elif tool_name == "godot_analyze_scene":
            scene_path = tool_args.get("scene_path", "")
            full_path = os.path.join(PROJECT_PATH, scene_path)
            
            if not os.path.exists(full_path):
                return {"content": [{"type": "text", "text": f"Scene not found: {scene_path}"}]}
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            result = runner.execute_task(
                f"分析以下 Godot 场景文件，指出问题并提供改进建议：\n\n{content[:3000]}",
                {"file": scene_path}
            )
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result.get("output", "Claude Code unavailable")
                    }
                ]
            }
        
        elif tool_name == "godot_analyze_code":
            code_path = tool_args.get("code_path", "")
            full_path = os.path.join(PROJECT_PATH, code_path)
            
            if not os.path.exists(full_path):
                return {"content": [{"type": "text", "text": f"Code file not found: {code_path}"}]}
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            result = runner.execute_task(
                f"分析以下 GDScript 代码，提供改进建议：\n\n{content[:3000]}",
                {"file": code_path, "language": "GDScript"}
            )
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result.get("output", "Claude Code unavailable")
                    }
                ]
            }
        
        elif tool_name == "godot_dev_help":
            question = tool_args.get("question", "")
            
            result = runner.execute_task(question)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result.get("output", "Claude Code unavailable")
                    }
                ]
            }
        
        else:
            return {"content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}]}
    
    elif method == "resources/list":
        return {
            "resources": [
                {
                    "uri": f"file://{PROJECT_PATH}/project.godot",
                    "name": "Project Configuration",
                    "mimeType": "text/plain"
                }
            ]
        }
    
    elif method == "resources/read":
        uri = params.get("uri", "")
        if "project.godot" in uri:
            project_file = os.path.join(PROJECT_PATH, "project.godot")
            if os.path.exists(project_file):
                with open(project_file, 'r', encoding='utf-8') as f:
                    return {"contents": [{"uri": uri, "text": f.read()}]}
        
        return {"contents": []}
    
    else:
        return {"error": f"Unknown method: {method}"}

def main():
    """主入口 - 通过 stdin/stdout 与 MCP 客户端通信"""
    print(f"[{SERVER_NAME}] Claude Code Game Studio MCP Server", file=sys.stderr)
    
    # 检查 Claude Code CLI
    if runner.is_available():
        print(f"[{SERVER_NAME}] Claude Code CLI found", file=sys.stderr)
    else:
        print(f"[{SERVER_NAME}] Warning: Claude Code CLI not found", file=sys.stderr)
        print(f"[{SERVER_NAME}] Install with: npm install -g @anthropic-ai/claude-code", file=sys.stderr)
    
    # 读取请求
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            
            try:
                request = json.loads(line)
                response = handle_request(request)
                
                # 输出响应
                print(json.dumps(response), flush=True)
            except json.JSONDecodeError:
                print(json.dumps({"error": "Invalid JSON"}), flush=True)
            except Exception as e:
                print(json.dumps({"error": str(e)}), flush=True)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"[{SERVER_NAME}] Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()