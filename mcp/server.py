#!/usr/bin/env python3
"""
Claude MCP Server for Godot Game Development
Provides tools for game development assistance, code generation, and scene manipulation.
"""

import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

from mcp.server import Server, StdioServerTransport
from mcp.types import Tool, TextResource, Resource, CallToolResult

# Server configuration
SERVER_NAME = "godot-claude-mcp"
SERVER_VERSION = "1.0.0"

# Paths
PROJECT_PATH = os.environ.get("PROJECT_PATH", r"D:\那个村庄")
GODOT_PATH = os.environ.get("GODOT_PATH", r"C:\Users\23732\AppData\Local\Programs\Godot\4.6.1\Godot_v4.6.1-stable_win64.exe")

# Initialize server
server = Server(SERVER_NAME)

# Claude client
claude_client = None
if HAS_ANTHROPIC:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        claude_client = anthropic.Anthropic(api_key=api_key)

# Tools definition
@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="godot_execute_script",
            description="Execute a GDScript in Godot project and return output",
            inputSchema={
                "type": "object",
                "properties": {
                    "script_path": {
                        "type": "string",
                        "description": "Path to the script file (relative to project)"
                    },
                    "method": {
                        "type": "string",
                        "description": "Method to call (e.g., '_ready', 'test')"
                    }
                }
            }
        ),
        Tool(
            name="godot_load_scene",
            description="Load and inspect a Godot scene file",
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {
                        "type": "string",
                        "description": "Path to the scene file (relative to project)"
                    }
                }
            }
        ),
        Tool(
            name="godot_create_script",
            description="Create a new GDScript file in the project",
            inputSchema={
                "type": "object",
                "properties": {
                    "script_name": {
                        "type": "string",
                        "description": "Name of the script (e.g., 'player_controller')"
                    },
                    "template": {
                        "type": "string",
                        "description": "Script template type: 'node2d', 'characterbody2d', 'resource'",
                        "enum": ["node2d", "characterbody2d", "resource", "empty"]
                    },
                    "path": {
                        "type": "string",
                        "description": "Directory path (relative to project)"
                    }
                }
            }
        ),
        Tool(
            name="godot_create_scene",
            description="Create a new scene file (.tscn)",
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_name": {
                        "type": "string",
                        "description": "Name of the scene"
                    },
                    "root_type": {
                        "type": "string",
                        "description": "Root node type (e.g., 'Node2D', 'Control')"
                    },
                    "path": {
                        "type": "string",
                        "description": "Directory path (relative to project)"
                    }
                }
            }
        ),
        Tool(
            name="godot_read_project_file",
            description="Read project.godot file",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="claude_generate_code",
            description="Use Claude to generate GDScript code based on description",
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Description of what the code should do"
                    },
                    "context": {
                        "type": "string",
                        "description": "Additional context about the project"
                    }
                }
            }
        ),
        Tool(
            name="claude_analyze_scene",
            description="Use Claude to analyze a scene and suggest improvements",
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_path": {
                        "type": "string",
                        "description": "Path to the scene file"
                    }
                }
            }
        ),
        Tool(
            name="godot_list_scenes",
            description="List all scene files in the project",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory to search (relative to project)"
                    }
                }
            }
        ),
        Tool(
            name="godot_list_scripts",
            description="List all GDScript files in the project",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory to search (relative to project)"
                    }
                }
            }
        )
    ]

# Tool implementations
@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    try:
        if name == "godot_execute_script":
            return await godot_execute_script(arguments)
        elif name == "godot_load_scene":
            return await godot_load_scene(arguments)
        elif name == "godot_create_script":
            return await godot_create_script(arguments)
        elif name == "godot_create_scene":
            return await godot_create_scene(arguments)
        elif name == "godot_read_project_file":
            return await godot_read_project_file(arguments)
        elif name == "claude_generate_code":
            return await claude_generate_code(arguments)
        elif name == "claude_analyze_scene":
            return await claude_analyze_scene(arguments)
        elif name == "godot_list_scenes":
            return await godot_list_scenes(arguments)
        elif name == "godot_list_scripts":
            return await godot_list_scripts(arguments)
        else:
            return CallToolResult(isError=True, content=[{"type": "text", "text": f"Unknown tool: {name}"}])
    except Exception as e:
        return CallToolResult(isError=True, content=[{"type": "text", "text": f"Error: {str(e)}"}])

async def godot_execute_script(args: Dict[str, Any]) -> CallToolResult:
    script_path = args.get("script_path", "")
    method = args.get("method", "_ready")
    
    full_path = os.path.join(PROJECT_PATH, script_path)
    if not os.path.exists(full_path):
        return CallToolResult(isError=True, content=[{"type": "text", "text": f"Script not found: {script_path}"}])
    
    output = f"Script found at: {full_path}\n"
    output += f"Method to call: {method}\n"
    output += "Note: Full script execution requires Godot headless mode setup"
    
    return CallToolResult(isError=False, content=[{"type": "text", "text": output}])

async def godot_load_scene(args: Dict[str, Any]) -> CallToolResult:
    scene_path = args.get("scene_path", "")
    full_path = os.path.join(PROJECT_PATH, scene_path)
    
    if not os.path.exists(full_path):
        return CallToolResult(isError=True, content=[{"type": "text", "text": f"Scene not found: {scene_path}"}])
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')[:50]
        preview = '\n'.join(lines)
        
        return CallToolResult(isError=False, content=[{
            "type": "text", 
            "text": f"Scene preview ({scene_path}):\n\n{preview}\n\n... (truncated, {len(content)} total lines)"
        }])
    except Exception as e:
        return CallToolResult(isError=True, content=[{"type": "text", "text": f"Error reading scene: {str(e)}"}])

async def godot_create_script(args: Dict[str, Any]) -> CallToolResult:
    script_name = args.get("script_name", "new_script")
    template = args.get("template", "empty")
    path = args.get("path", "scripts")
    
    templates = {
        "node2d": '''extends Node2D

func _ready() -> void:
    print("Node2D script ready")
''',
        "characterbody2d": '''extends CharacterBody2D

func _ready() -> void:
    print("CharacterBody2D ready")

func _physics_process(delta: float) -> void:
    move_and_slide()
''',
        "resource": '''extends Resource
class_name NewResource

@export var value: int = 0

func _init() -> void:
    pass
''',
        "empty": '''extends Node

func _ready() -> void:
    pass
'''
    }
    
    script_content = templates.get(template, templates["empty"])
    script_file = f"{script_name}.gd"
    
    os.makedirs(os.path.join(PROJECT_PATH, path), exist_ok=True)
    full_path = os.path.join(PROJECT_PATH, path, script_file)
    
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    return CallToolResult(isError=False, content=[{
        "type": "text", 
        "text": f"Created script: {path}/{script_file}\n\nContent:\n{script_content}"
    }])

async def godot_create_scene(args: Dict[str, Any]) -> CallToolResult:
    scene_name = args.get("scene_name", "new_scene")
    root_type = args.get("root_type", "Node2D")
    path = args.get("path", "scenes")
    
    scene_content = f'''[gd_scene format=3]

[node name="{scene_name}" type="{root_type}"]
'''
    
    scene_file = f"{scene_name}.tscn"
    os.makedirs(os.path.join(PROJECT_PATH, path), exist_ok=True)
    full_path = os.path.join(PROJECT_PATH, path, scene_file)
    
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(scene_content)
    
    return CallToolResult(isError=False, content=[{
        "type": "text", 
        "text": f"Created scene: {path}/{scene_file}\n\nContent:\n{scene_content}"
    }])

async def godot_read_project_file(args: Dict[str, Any]) -> CallToolResult:
    project_file = os.path.join(PROJECT_PATH, "project.godot")
    
    if not os.path.exists(project_file):
        return CallToolResult(isError=True, content=[{"type": "text", "text": "project.godot not found"}])
    
    try:
        with open(project_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return CallToolResult(isError=False, content=[{
            "type": "text", 
            "text": f"project.godot content:\n\n{content}"
        }])
    except Exception as e:
        return CallToolResult(isError=True, content=[{"type": "text", "text": f"Error reading project.godot: {str(e)}"}])

async def claude_generate_code(args: Dict[str, Any]) -> CallToolResult:
    description = args.get("description", "")
    context = args.get("context", "")
    
    if not claude_client:
        return CallToolResult(isError=True, content=[{
            "type": "text", 
            "text": "Claude API not configured. Set ANTHROPIC_API_KEY environment variable."
        }])
    
    prompt = f"""Generate GDScript code for Godot 4.6 for the following requirement:

Description: {description}

Project Context: {context}

Requirements:
- Use Godot 4.6 GDScript syntax
- Follow best practices
- Include type hints
- Add documentation comments in Chinese

Respond with the complete GDScript code in a code block."""

    try:
        response = claude_client.messages.create(
            model="claude-opus-4-20251114",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        code = response.content[0].text
        return CallToolResult(isError=False, content=[{"type": "text", "text": f"Claude generated code:\n\n{code}"}])
    except Exception as e:
        return CallToolResult(isError=True, content=[{"type": "text", "text": f"Claude error: {str(e)}"}])

async def claude_analyze_scene(args: Dict[str, Any]) -> CallToolResult:
    scene_path = args.get("scene_path", "")
    full_path = os.path.join(PROJECT_PATH, scene_path)
    
    if not os.path.exists(full_path):
        return CallToolResult(isError=True, content=[{"type": "text", "text": f"Scene not found: {scene_path}"}])
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not claude_client:
            return CallToolResult(isError=True, content=[{
                "type": "text", 
                "text": "Claude API not configured. Scene content preview:\n\n" + content[:2000]
            }])
        
        prompt = f"""Analyze this Godot scene file and provide suggestions for improvements:

Scene file: {scene_path}

Content:
```
{content[:4000]}
```

Please analyze:
1. Scene structure and node hierarchy
2. Potential issues or improvements
3. Suggestions for optimization
4. Best practices recommendations

Respond in Chinese."""

        response = claude_client.messages.create(
            model="claude-opus-4-20251114",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        analysis = response.content[0].text
        return CallToolResult(isError=False, content=[{"type": "text", "text": f"Scene analysis for {scene_path}:\n\n{analysis}"}])
    except Exception as e:
        return CallToolResult(isError=True, content=[{"type": "text", "text": f"Error analyzing scene: {str(e)}"}])

async def godot_list_scenes(args: Dict[str, Any]) -> CallToolResult:
    directory = args.get("directory", "")
    search_path = os.path.join(PROJECT_PATH, directory) if directory else PROJECT_PATH
    
    scenes = []
    for root, dirs, files in os.walk(search_path):
        for file in files:
            if file.endswith('.tscn'):
                rel_path = os.path.relpath(os.path.join(root, file), PROJECT_PATH)
                scenes.append(rel_path)
    
    scenes.sort()
    output = f"Scene files in project ({len(scenes)} found):\n\n"
    output += "\n".join(scenes[:50])
    if len(scenes) > 50:
        output += f"\n\n... and {len(scenes) - 50} more"
    
    return CallToolResult(isError=False, content=[{"type": "text", "text": output}])

async def godot_list_scripts(args: Dict[str, Any]) -> CallToolResult:
    directory = args.get("directory", "")
    search_path = os.path.join(PROJECT_PATH, directory) if directory else PROJECT_PATH
    
    scripts = []
    for root, dirs, files in os.walk(search_path):
        for file in files:
            if file.endswith('.gd'):
                rel_path = os.path.relpath(os.path.join(root, file), PROJECT_PATH)
                scripts.append(rel_path)
    
    scripts.sort()
    output = f"GDScript files in project ({len(scripts)} found):\n\n"
    output += "\n".join(scripts[:50])
    if len(scripts) > 50:
        output += f"\n\n... and {len(scripts) - 50} more"
    
    return CallToolResult(isError=False, content=[{"type": "text", "text": output}])

# Resources
@server.list_resources()
async def list_resources() -> List[Resource]:
    return [
        TextResource(
            uri="godot://project.godot",
            name="Project Configuration",
            mimeType="text/plain",
            description="The Godot project configuration file"
        )
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    if uri == "godot://project.godot":
        project_file = os.path.join(PROJECT_PATH, "project.godot")
        if os.path.exists(project_file):
            with open(project_file, 'r', encoding='utf-8') as f:
                return f.read()
    return ""

async def main():
    print(f"[{SERVER_NAME}] Starting MCP server for Godot development...", file=sys.stderr)
    transport = StdioServerTransport()
    await server.run(transport)

if __name__ == "__main__":
    import sys
    asyncio.run(main())