#!/usr/bin/env python3
import os
import sys
import json
import subprocess

PROJECT_PATH = os.environ.get("PROJECT_PATH", "D:/那个村庄")

def claude_execute(prompt, timeout=300):
    try:
        proc = subprocess.Popen(
            ["claude", "--print"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=PROJECT_PATH,
            shell=True
        )
        stdout, stderr = proc.communicate(input=prompt, timeout=timeout)
        return {"success": proc.returncode == 0 or len(stdout) > 0, "output": stdout or stderr}
    except subprocess.TimeoutExpired:
        proc.kill()
        return {"success": False, "output": "", "error": "Command timed out"}
    except FileNotFoundError:
        return {"success": False, "output": "", "error": "Claude CLI not found"}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}

def handle_request(request):
    method = request.get("method", "")
    params = request.get("params", {})

    if method == "initialize":
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "godot-game-studio", "version": "1.0.0"}
        }

    if method == "tools/list":
        tools = [
            {
                "name": "godot_generate_code",
                "description": "生成 GDScript 代码",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "template": {"type": "string"}
                    }
                }
            },
            {
                "name": "godot_analyze_scene",
                "description": "分析场景文件",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "scene_path": {"type": "string"}
                    }
                }
            },
            {
                "name": "godot_analyze_code",
                "description": "分析代码",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "code_path": {"type": "string"}
                    }
                }
            },
            {
                "name": "godot_dev_help",
                "description": "开发帮助",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string"}
                    }
                }
            }
        ]
        return {"tools": tools}

    if method == "tools/call":
        name = params.get("name", "")
        args = params.get("arguments", {})

        if name == "godot_generate_code":
            desc = args.get("description", "")
            template = args.get("template", "node2d")
            prompt = "生成 %s GDScript 代码：%s\n\n只输出代码。" % (template, desc)
            result = claude_execute(prompt)
            text = result.get("output") or result.get("error", "Error")
            return {"content": [{"type": "text", "text": text}]}

        if name == "godot_analyze_scene":
            path = args.get("scene_path", "")
            full = os.path.join(PROJECT_PATH, path)
            if os.path.exists(full):
                with open(full, "r", encoding="utf-8") as f:
                    content = f.read()[:2000]
                prompt = "分析场景 %s：\n%s\n\n用中文回答。" % (path, content)
                result = claude_execute(prompt)
                text = result.get("output") or result.get("error", "Error")
                return {"content": [{"type": "text", "text": text}]}
            return {"content": [{"type": "text", "text": "文件不存在: %s" % path}]}

        if name == "godot_analyze_code":
            path = args.get("code_path", "")
            full = os.path.join(PROJECT_PATH, path)
            if os.path.exists(full):
                with open(full, "r", encoding="utf-8") as f:
                    content = f.read()[:2000]
                prompt = "分析代码 %s：\n%s\n\n用中文回答。" % (path, content)
                result = claude_execute(prompt)
                text = result.get("output") or result.get("error", "Error")
                return {"content": [{"type": "text", "text": text}]}
            return {"content": [{"type": "text", "text": "文件不存在: %s" % path}]}

        if name == "godot_dev_help":
            question = args.get("question", "")
            prompt = "Godot 4.6 游戏开发问题：%s\n\n用中文回答。" % question
            result = claude_execute(prompt)
            text = result.get("output") or result.get("error", "Error")
            return {"content": [{"type": "text", "text": text}]}

        return {"content": [{"type": "text", "text": "Unknown tool: %s" % name}]}

    return {}

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
            print(json.dumps(response), flush=True)
        except Exception as e:
            print(json.dumps({"error": str(e)}), flush=True)

if __name__ == "__main__":
    main()
