extends Node

class_name ClaudeIntegrator

signal code_generated(code: String, script_name: String)
signal analysis_complete(analysis: String)
signal error_occurred(error_message: String)

const MCP_PATH: String = "res://mcp/claude_coder.py"
const API_KEY_ENV_VAR: String = "ANTHROPIC_API_KEY"

var is_initialized: bool = false
var last_generated_code: String = ""

func _ready() -> void:
    print("[ClaudeIntegrator] 初始化中")
    is_initialized = _check_environment()

func _check_environment() -> bool:
    var api_key = OS.get_environment(API_KEY_ENV_VAR)
    if api_key.is_empty():
        push_warning("[ClaudeIntegrator] ANTHROPIC_API_KEY 未设置")
        push_warning("[ClaudeIntegrator] Claude 代码生成功能不可用")
        return false
    print("[ClaudeIntegrator] API Key 已配置")
    return true

func generate_code(description: String, template: String = "node2d") -> String:
    if not is_initialized:
        emit_signal("error_occurred", "Claude 未初始化")
        return ""

    print("[ClaudeIntegrator] 生成代码: ", description)

    var temp_script_path = "temp_generated.gd"
    var args = [
        OS.get_environment("PYTHON_EXECUTABLE") if OS.has_environment("PYTHON_EXECUTABLE") else "python",
        ProjectSettings.globalize_path(MCP_PATH),
        "generate",
        "-d", description,
        "-t", template,
        "-o", ProjectSettings.globalize_path(temp_script_path)
    ]

    var output: Array = []
    var error: int = OS.execute(args[0], args.slice(1), output, false)

    if error != 0:
        var error_msg = "执行失败: " + output[0] if output.size() > 0 else "未知错误"
        emit_signal("error_occurred", error_msg)
        print("[ClaudeIntegrator] 错误: ", error_msg)
        return ""

    var result = output[0] if output.size() > 0 else ""
    last_generated_code = result

    var generated_file = ProjectSettings.globalize_path(temp_script_path)
    if FileAccess.file_exists(generated_file):
        var file = FileAccess.open(generated_file, FileAccess.READ)
        if file:
            result = file.get_as_text()
            file.close()
            DirAccess.remove_absolute(generated_file)

    emit_signal("code_generated", result, temp_script_path)
    print("[ClaudeIntegrator] 代码生成完成")
    return result

func analyze_code(code: String) -> String:
    if not is_initialized:
        emit_signal("error_occurred", "Claude 未初始化")
        return ""

    print("[ClaudeIntegrator] 分析代码...")

    var temp_file = "temp_analysis.gd"
    var temp_path = ProjectSettings.globalize_path(temp_file)

    var file = FileAccess.open(temp_path, FileAccess.WRITE)
    if file:
        file.store_string(code)
        file.close()

    var args = [
        OS.get_environment("PYTHON_EXECUTABLE") if OS.has_environment("PYTHON_EXECUTABLE") else "python",
        ProjectSettings.globalize_path(MCP_PATH),
        "analyze",
        "-f", temp_path
    ]

    var output: Array = []
    var error: int = OS.execute(args[0], args.slice(1), output, false)

    if FileAccess.file_exists(temp_path):
        DirAccess.remove_absolute(temp_path)

    if error != 0:
        var error_msg = "分析失败: " + output[0] if output.size() > 0 else "未知错误"
        emit_signal("error_occurred", error_msg)
        return error_msg

    var result = output[0] if output.size() > 0 else ""
    emit_signal("analysis_complete", result)
    print("[ClaudeIntegrator] 分析完成")
    return result

func analyze_scene(scene_path: String) -> String:
    if not FileAccess.file_exists(scene_path):
        emit_signal("error_occurred", "场景文件不存在 " + scene_path)
        return ""

    var file = FileAccess.open(scene_path, FileAccess.READ)
    if not file:
        emit_signal("error_occurred", "无法读取场景文件")
        return ""

    var content = file.get_as_text()
    file.close()

    return analyze_code(content)

func save_generated_code(code: String, script_path: String) -> bool:
    var path = ProjectSettings.globalize_path(script_path)

    var parent_dir = path.get_base_dir()
    var dir = DirAccess.open(parent_dir)
    if dir == null:
        dir = DirAccess.make_dir_recursive_absolute(parent_dir)

    var file = FileAccess.open(path, FileAccess.WRITE)
    if file:
        file.store_string(code)
        file.close()
        print("[ClaudeIntegrator] 代码已保存 ", script_path)
        return true
    else:
        emit_signal("error_occurred", "无法保存文件: " + script_path)
        return false

func create_script_interactive(template: String = "node2d") -> void:
    print("[ClaudeIntegrator] 交互式脚本创建")
    print("请使用 ClaudeIntegrator.generate_code() 方法生成代码")

func get_project_scripts() -> Array:
    var scripts: Array = []
    var scripts_dir = ProjectSettings.globalize_path("res://scripts")

    if DirAccess.dir_exists_absolute(scripts_dir):
        var dir = DirAccess.open(scripts_dir)
        if dir:
            dir.list_dir_begin()
            var file_name = dir.get_next()
            while file_name != "":
                if file_name.ends_with(".gd"):
                    scripts.append("res://scripts/" + file_name)
                file_name = dir.get_next()
            dir.list_dir_end()

    return scripts

func get_project_scenes() -> Array:
    var scenes: Array = []
    _scan_directory_for_scenes("res://scenes", scenes)
    return scenes

func _scan_directory_for_scenes(path: String, output: Array) -> void:
    if not DirAccess.dir_exists_absolute(ProjectSettings.globalize_path(path)):
        return

    var dir = DirAccess.open(ProjectSettings.globalize_path(path))
    if dir:
        dir.list_dir_begin()
        var file_name = dir.get_next()
        while file_name != "":
            if dir.current_is_dir():
                _scan_directory_for_scenes(path + "/" + file_name, output)
            elif file_name.ends_with(".tscn"):
                output.append(path + "/" + file_name)
            file_name = dir.get_next()
        dir.list_dir_end()