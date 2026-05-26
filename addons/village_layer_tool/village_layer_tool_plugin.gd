@tool
extends EditorPlugin

const INTERACTABLE_SCRIPT_PATH := "res://scripts/world/yard_interactable.gd"

const MODE_BACK := "back"
const MODE_MID := "mid"
const MODE_FRONT := "front"
const MODE_INTERACTION := "interaction"
const MODE_BLOCKER := "blocker"

const PROJECT_REVIEW_SCENES := [
	{
		"label": "Main",
		"path": "res://game/scenes/Main.tscn",
	},
	{
		"label": "PlayerYard",
		"path": "res://game/scenes/world/PlayerYard.tscn",
	},
	{
		"label": "Yard Blueprint",
		"path": "res://scenes/dev/player_yard_layer_blueprint_review.tscn",
	},
	{
		"label": "ForestEdge",
		"path": "res://game/scenes/world/ForestEdge.tscn",
	},
	{
		"label": "Greenfield Review",
		"path": "res://scenes/dev/greenfield_p0_reviews/greenfield_p0_region_review_all.tscn",
	},
]

const VALIDATION_COMMANDS := [
	"python tools\\validate_project_structure.py",
	"python tools\\validate_play_start_experience.py",
	"python tools\\validate_player_yard_layer_blueprint_review_scene.py",
	"python tools\\validate_yard_blockout_readability.py",
	"python tools\\validate_forest_edge_gameplay_layout.py",
	"git diff --check",
]

var dock: VBoxContainer
var review_dock: VBoxContainer
var mode_selector: OptionButton
var active_button: Button
var name_edit: LineEdit
var hint_edit: LineEdit
var status_label: Label
var review_status_label: Label

var is_active := false
var current_mode := MODE_BLOCKER
var points_root: PackedVector2Array = PackedVector2Array()
var mouse_root := Vector2.ZERO
var mouse_screen := Vector2.ZERO

func _enter_tree() -> void:
	_create_dock()
	add_control_to_dock(DOCK_SLOT_LEFT_UL, dock)
	_create_review_dock()
	add_control_to_dock(DOCK_SLOT_RIGHT_UL, review_dock)
	add_tool_menu_item("Village Layer Tool", Callable(self, "_show_dock"))
	set_input_event_forwarding_always_enabled()
	set_force_draw_over_forwarding_enabled()

func _exit_tree() -> void:
	remove_tool_menu_item("Village Layer Tool")
	if review_dock != null:
		remove_control_from_docks(review_dock)
		review_dock.queue_free()
		review_dock = null
	if dock != null:
		remove_control_from_docks(dock)
		dock.queue_free()
		dock = null

func _handles(object: Object) -> bool:
	return object is CanvasItem or object is Node

func _create_dock() -> void:
	dock = VBoxContainer.new()
	dock.name = "村庄精确标注"

	var title := Label.new()
	title.text = "村庄精确标注"
	dock.add_child(title)

	var help := Label.new()
	help.text = "左键加点；Backspace 撤销；Enter 或右键完成；Esc 取消。生成 Godot 原生多边形节点。"
	help.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	dock.add_child(help)

	mode_selector = OptionButton.new()
	_add_mode_item("后景 Polygon2D", MODE_BACK)
	_add_mode_item("中景 Polygon2D", MODE_MID)
	_add_mode_item("前景 Polygon2D", MODE_FRONT)
	_add_mode_item("交互 Area2D", MODE_INTERACTION)
	_add_mode_item("阻挡 StaticBody2D", MODE_BLOCKER)
	mode_selector.select(4)
	mode_selector.item_selected.connect(_on_mode_selected)
	dock.add_child(mode_selector)

	name_edit = LineEdit.new()
	name_edit.placeholder_text = "名称，可空"
	dock.add_child(name_edit)

	hint_edit = LineEdit.new()
	hint_edit.placeholder_text = "交互提示，可空"
	dock.add_child(hint_edit)

	active_button = Button.new()
	active_button.text = "开始点选"
	active_button.toggle_mode = true
	active_button.toggled.connect(_on_active_toggled)
	dock.add_child(active_button)

	var undo_button := Button.new()
	undo_button.text = "撤销上一点"
	undo_button.pressed.connect(_remove_last_point)
	dock.add_child(undo_button)

	var finish_button := Button.new()
	finish_button.text = "完成多边形"
	finish_button.pressed.connect(_finish_polygon)
	dock.add_child(finish_button)

	var cancel_button := Button.new()
	cancel_button.text = "取消当前多边形"
	cancel_button.pressed.connect(_cancel_polygon)
	dock.add_child(cancel_button)

	var clear_button := Button.new()
	clear_button.text = "清空本工具生成节点"
	clear_button.pressed.connect(_clear_manual_nodes)
	dock.add_child(clear_button)

	var save_button := Button.new()
	save_button.text = "保存当前场景"
	save_button.pressed.connect(_save_scene)
	dock.add_child(save_button)

	status_label = Label.new()
	status_label.text = "插件已加载。"
	status_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	dock.add_child(status_label)

func _create_review_dock() -> void:
	review_dock = VBoxContainer.new()
	review_dock.name = "Village Review"

	var title := Label.new()
	title.text = "Village Review"
	review_dock.add_child(title)

	var help := Label.new()
	help.text = "Open high-value review scenes and copy the current validation command set."
	help.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	review_dock.add_child(help)

	for scene_info in PROJECT_REVIEW_SCENES:
		var button := Button.new()
		button.text = "Open %s" % String(scene_info["label"])
		button.pressed.connect(_open_review_scene.bind(String(scene_info["path"])))
		review_dock.add_child(button)

	var copy_button := Button.new()
	copy_button.text = "Copy validation commands"
	copy_button.pressed.connect(_copy_validation_commands)
	review_dock.add_child(copy_button)

	var refresh_button := Button.new()
	refresh_button.text = "Refresh status summary"
	refresh_button.pressed.connect(_refresh_review_status)
	review_dock.add_child(refresh_button)

	review_status_label = Label.new()
	review_status_label.text = "Status not loaded."
	review_status_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	review_dock.add_child(review_status_label)
	_refresh_review_status()

func _open_review_scene(scene_path: String) -> void:
	if not ResourceLoader.exists(scene_path):
		_update_review_status("Missing scene: %s" % scene_path)
		return
	get_editor_interface().open_scene_from_path(scene_path)
	_update_review_status("Open scene requested: %s" % scene_path)

func _copy_validation_commands() -> void:
	var lines := PackedStringArray()
	for command in VALIDATION_COMMANDS:
		lines.append(String(command))
	DisplayServer.clipboard_set("\n".join(lines))
	_update_review_status("Copied %s validation commands." % lines.size())

func _refresh_review_status() -> void:
	var status_file := FileAccess.open("res://.codex/status.md", FileAccess.READ)
	if status_file == null:
		_update_review_status("Could not read res://.codex/status.md")
		return
	var lines := PackedStringArray()
	while not status_file.eof_reached() and lines.size() < 14:
		var line := status_file.get_line().strip_edges()
		if not line.is_empty():
			lines.append(line)
	_update_review_status("\n".join(lines))

func _update_review_status(text: String) -> void:
	if review_status_label != null:
		review_status_label.text = text

func _add_mode_item(label: String, mode: String) -> void:
	var index := mode_selector.item_count
	mode_selector.add_item(label)
	mode_selector.set_item_metadata(index, mode)

func _show_dock() -> void:
	if dock != null:
		dock.visible = true
		_update_status("Dock 已显示。")

func _on_mode_selected(index: int) -> void:
	current_mode = String(mode_selector.get_item_metadata(index))
	_update_status("模式：%s。当前点数：%s" % [_mode_label(current_mode), points_root.size()])

func _on_active_toggled(enabled: bool) -> void:
	is_active = enabled
	active_button.text = "停止点选" if enabled else "开始点选"
	if not enabled:
		_cancel_polygon()
	_update_status("已激活：左键逐点描边。" if enabled else "未激活。")
	update_overlays()

func _forward_canvas_gui_input(event: InputEvent) -> bool:
	if not is_active:
		return false
	if get_editor_interface().get_edited_scene_root() == null:
		_update_status("没有打开可编辑场景。")
		return false

	if event is InputEventMouseMotion:
		mouse_screen = event.position
		mouse_root = _screen_to_root_local(event.position)
		update_overlays()
		return false

	if event is InputEventMouseButton:
		mouse_screen = event.position
		mouse_root = _screen_to_root_local(event.position)
		if event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
			points_root.append(mouse_root)
			_update_status("已添加点 %s：%s" % [points_root.size(), mouse_root.round()])
			update_overlays()
			return true
		if event.button_index == MOUSE_BUTTON_RIGHT and event.pressed:
			_finish_polygon()
			return true

	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_ENTER, KEY_KP_ENTER:
				_finish_polygon()
				return true
			KEY_ESCAPE:
				_cancel_polygon()
				return true
			KEY_BACKSPACE:
				_remove_last_point()
				return true

	return false

func _forward_canvas_draw_over_viewport(overlay: Control) -> void:
	if not is_active:
		return
	var color := _mode_color(current_mode)
	var screen_points := PackedVector2Array()
	for point in points_root:
		screen_points.append(_root_local_to_screen(point))
	if points_root.size() > 0:
		screen_points.append(mouse_screen)
	for i in screen_points.size():
		overlay.draw_circle(screen_points[i], 4.0, color)
		if i > 0:
			overlay.draw_line(screen_points[i - 1], screen_points[i], color, 2.0)
	if screen_points.size() >= 3:
		overlay.draw_colored_polygon(screen_points, Color(color.r, color.g, color.b, 0.12))

func _screen_to_root_local(screen_position: Vector2) -> Vector2:
	var root := get_editor_interface().get_edited_scene_root()
	if root == null:
		return screen_position
	var viewport := get_editor_interface().get_editor_viewport_2d()
	if viewport == null:
		return screen_position
	var canvas_position := viewport.global_canvas_transform.affine_inverse() * screen_position
	if root is Node2D:
		return root.to_local(canvas_position)
	return canvas_position

func _root_local_to_screen(root_position: Vector2) -> Vector2:
	var root := get_editor_interface().get_edited_scene_root()
	var viewport := get_editor_interface().get_editor_viewport_2d()
	if root == null or viewport == null:
		return root_position
	var canvas_position := root_position
	if root is Node2D:
		canvas_position = root.to_global(root_position)
	return viewport.global_canvas_transform * canvas_position

func _finish_polygon() -> void:
	if points_root.size() < 3:
		_update_status("至少需要 3 个点。当前：%s" % points_root.size())
		return
	var root := get_editor_interface().get_edited_scene_root()
	if root == null:
		_update_status("没有打开可编辑场景。")
		return
	match current_mode:
		MODE_BACK, MODE_MID, MODE_FRONT:
			_create_layer_polygon(root)
		MODE_INTERACTION:
			_create_interaction_polygon(root)
		MODE_BLOCKER:
			_create_blocker_polygon(root)
	points_root.clear()
	update_overlays()

func _cancel_polygon() -> void:
	points_root.clear()
	_update_status("已取消当前多边形。")
	update_overlays()

func _remove_last_point() -> void:
	if points_root.size() > 0:
		points_root.remove_at(points_root.size() - 1)
	_update_status("当前点数：%s" % points_root.size())
	update_overlays()

func _create_layer_polygon(root: Node) -> void:
	var parent := _get_or_create_parent(root, _parent_path_for_mode(current_mode))
	var poly := Polygon2D.new()
	poly.name = _unique_name(parent, _manual_name_or(_default_name_for_mode(current_mode)))
	poly.polygon = _points_to_parent_local(root, parent)
	poly.color = Color(_mode_color(current_mode).r, _mode_color(current_mode).g, _mode_color(current_mode).b, 0.22)
	poly.z_index = _z_index_for_mode(current_mode)
	poly.set_meta("manual_authoring_tool", "village_layer_tool")
	poly.set_meta("manual_role", current_mode)
	parent.add_child(poly)
	_set_owner_tree(poly, root)
	_update_status("已创建%s多边形：%s" % [_mode_label(current_mode), poly.name])

func _create_interaction_polygon(root: Node) -> void:
	var parent := _get_or_create_parent(root, _parent_path_for_mode(MODE_INTERACTION))
	var parent_points := _points_to_parent_local(root, parent)
	var center := _polygon_center(parent_points)
	var local_points := _offset_polygon(parent_points, -center)
	var area := Area2D.new()
	area.name = _unique_name(parent, _manual_name_or("ManualInteraction"))
	area.position = center
	area.add_to_group("interactable", true)
	var loaded_script := load(INTERACTABLE_SCRIPT_PATH)
	if loaded_script != null:
		area.set_script(loaded_script)
	area.set("object_id", area.name.to_snake_case())
	area.set("display_name", _manual_name_or("手动交互"))
	area.set("interaction_hint", _hint_text())
	area.set("feedback_text", _manual_name_or("这里还需要填写交互反馈。"))
	area.set_meta("manual_authoring_tool", "village_layer_tool")
	area.set_meta("manual_role", MODE_INTERACTION)
	parent.add_child(area)
	_set_owner_tree(area, root)

	var shape := CollisionPolygon2D.new()
	shape.name = "CollisionPolygon2D"
	shape.polygon = local_points
	area.add_child(shape)
	_set_owner_tree(shape, root)
	_add_visual_polygon(area, root, local_points, MODE_INTERACTION)
	_update_status("已创建交互多边形：%s" % area.name)

func _create_blocker_polygon(root: Node) -> void:
	var parent := _get_or_create_parent(root, _parent_path_for_mode(MODE_BLOCKER))
	var parent_points := _points_to_parent_local(root, parent)
	var center := _polygon_center(parent_points)
	var local_points := _offset_polygon(parent_points, -center)
	var body := StaticBody2D.new()
	body.name = _unique_name(parent, _manual_name_or("ManualBlocker"))
	body.position = center
	body.set_meta("manual_authoring_tool", "village_layer_tool")
	body.set_meta("manual_role", MODE_BLOCKER)
	parent.add_child(body)
	_set_owner_tree(body, root)

	var shape := CollisionPolygon2D.new()
	shape.name = "CollisionPolygon2D"
	shape.polygon = local_points
	body.add_child(shape)
	_set_owner_tree(shape, root)
	_add_visual_polygon(body, root, local_points, MODE_BLOCKER)
	_update_status("已创建阻挡多边形：%s" % body.name)

func _add_visual_polygon(parent: Node, root: Node, polygon: PackedVector2Array, mode: String) -> void:
	var poly := Polygon2D.new()
	poly.name = "VisualGuide"
	poly.polygon = polygon
	poly.color = Color(_mode_color(mode).r, _mode_color(mode).g, _mode_color(mode).b, 0.18)
	poly.z_index = 1000
	poly.set_meta("manual_authoring_tool", "village_layer_tool")
	poly.set_meta("manual_role", "%s_visual_guide" % mode)
	parent.add_child(poly)
	_set_owner_tree(poly, root)

func _points_to_parent_local(root: Node, parent: Node) -> PackedVector2Array:
	var out := PackedVector2Array()
	for point in points_root:
		out.append(_root_to_parent_position(root, parent, point))
	return out

func _polygon_center(polygon: PackedVector2Array) -> Vector2:
	if polygon.is_empty():
		return Vector2.ZERO
	var sum := Vector2.ZERO
	for point in polygon:
		sum += point
	return sum / float(polygon.size())

func _offset_polygon(polygon: PackedVector2Array, offset: Vector2) -> PackedVector2Array:
	var result := PackedVector2Array()
	for point in polygon:
		result.append(point + offset)
	return result

func _get_or_create_parent(root: Node, path: String) -> Node:
	var current := root
	for part in path.split("/", false):
		var child := current.get_node_or_null(part)
		if child == null:
			child = Node2D.new()
			child.name = part
			child.set_meta("manual_authoring_tool", "village_layer_tool")
			child.set_meta("manual_folder", true)
			current.add_child(child)
			_set_owner_tree(child, root)
		current = child
	return current

func _root_to_parent_position(root: Node, parent: Node, root_position: Vector2) -> Vector2:
	if root is Node2D and parent is Node2D:
		return parent.to_local(root.to_global(root_position))
	return root_position

func _set_owner_tree(node: Node, owner: Node) -> void:
	node.owner = owner
	for child in node.get_children():
		_set_owner_tree(child, owner)

func _clear_manual_nodes() -> void:
	var root := get_editor_interface().get_edited_scene_root()
	if root == null:
		_update_status("没有打开可编辑场景。")
		return
	var removed := _remove_child_if_exists(root, "ManualAuthoring")
	_update_status("已清空 ManualAuthoring：%s" % ("是" if removed else "无"))

func _remove_child_if_exists(parent: Node, child_name: String) -> bool:
	var child := parent.get_node_or_null(child_name)
	if child == null:
		return false
	parent.remove_child(child)
	child.queue_free()
	return true

func _save_scene() -> void:
	var error := get_editor_interface().save_scene()
	_update_status("已请求保存当前场景。错误码：%s" % error)

func _unique_name(parent: Node, base: String) -> String:
	var safe_base := base.strip_edges().replace(" ", "_")
	if safe_base.is_empty():
		safe_base = "ManualPolygon"
	var candidate := safe_base
	var index := 2
	while parent.has_node(candidate):
		candidate = "%s_%02d" % [safe_base, index]
		index += 1
	return candidate

func _manual_name_or(default_value: String) -> String:
	var text := name_edit.text.strip_edges()
	return default_value if text.is_empty() else text

func _hint_text() -> String:
	var text := hint_edit.text.strip_edges()
	return "按 E 互动" if text.is_empty() else text

func _parent_path_for_mode(mode: String) -> String:
	match mode:
		MODE_BACK:
			return "ManualAuthoring/Layers/Back"
		MODE_MID:
			return "ManualAuthoring/Layers/Mid"
		MODE_FRONT:
			return "ManualAuthoring/Layers/Front"
		MODE_INTERACTION:
			return "ManualAuthoring/Interactions"
		MODE_BLOCKER:
			return "ManualAuthoring/Blockers"
	return "ManualAuthoring"

func _mode_color(mode: String) -> Color:
	match mode:
		MODE_BACK:
			return Color(0.25, 0.55, 1.0, 0.95)
		MODE_MID:
			return Color(0.35, 0.9, 0.45, 0.95)
		MODE_FRONT:
			return Color(1.0, 0.65, 0.18, 0.95)
		MODE_INTERACTION:
			return Color(0.95, 0.85, 0.15, 0.95)
		MODE_BLOCKER:
			return Color(1.0, 0.22, 0.18, 0.95)
	return Color.WHITE

func _mode_label(mode: String) -> String:
	match mode:
		MODE_BACK:
			return "后景"
		MODE_MID:
			return "中景"
		MODE_FRONT:
			return "前景"
		MODE_INTERACTION:
			return "交互"
		MODE_BLOCKER:
			return "阻挡"
	return "未知"

func _default_name_for_mode(mode: String) -> String:
	match mode:
		MODE_BACK:
			return "BackPolygon"
		MODE_MID:
			return "MidPolygon"
		MODE_FRONT:
			return "FrontPolygon"
	return "ManualPolygon"

func _z_index_for_mode(mode: String) -> int:
	match mode:
		MODE_BACK:
			return -160
		MODE_MID:
			return 40
		MODE_FRONT:
			return 220
	return 0

func _update_status(text: String) -> void:
	if status_label != null:
		status_label.text = text
