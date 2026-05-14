extends CanvasLayer

signal crop_selected(crop_type: String)
signal action_completed

var farm_system: Node = null
var is_visible: bool = false
var current_plot_index: int = -1

var crop_buttons: Array = []
var action_buttons: Array = []

@onready var panel: Panel = $FarmPanel
@onready var crop_container: VBoxContainer = $FarmPanel/CropContainer
@onready var action_container: HBoxContainer = $FarmPanel/ActionContainer
@onready var info_label: Label = $FarmPanel/InfoLabel
@onready var close_button: Button = $FarmPanel/CloseButton

func _ready() -> void:
	farm_system = get_parent().get_node_or_null("FarmSystem")
	if not farm_system:
		var tree = get_tree()
		if tree:
			farm_system = tree.get_first_node_in_group("farm_system")
	
	setup_ui()
	hide_panel()

func setup_ui() -> void:
	if close_button:
		close_button.pressed.connect(hide_panel)
	
	for i in range(9):
		var btn = Button.new()
		btn.text = "鐢?"
		btn.custom_minimum_size = Vector2(100, 40)
		btn.pressed.connect(func(): on_plot_button_pressed(i))
		crop_container.add_child(btn)
		crop_buttons.append(btn)

func show_panel(plot_index: int) -> void:
	current_plot_index = plot_index
	is_visible = true
	panel.visible = true
	update_plot_info()
	update_buttons()

func hide_panel() -> void:
	is_visible = false
	panel.visible = false
	current_plot_index = -1

func update_plot_info() -> void:
	if current_plot_index < 0 or not farm_system:
		return
	
	var info = farm_system.get_plot_info(current_plot_index)
	var state_name = info.get("state_name", "empty")
	var crop = info.get("crop_type", "")
	var progress = info.get("growth_progress", 0.0) * 100
	
	var text = "鐢板湴 %d\n鐘舵€? %s" % [current_plot_index, state_name]
	if crop:
		text += "\n浣滅墿: %s" % crop
		text += "\n鐢熼暱: %.0f%%" % progress
	
	if info_label:
		info_label.text = text

func update_buttons() -> void:
	if current_plot_index < 0 or not farm_system:
		return
	
	var info = farm_system.get_plot_info(current_plot_index)
	var state = info.get("state", 0)
	var is_watered = info.get("is_watered", false)
	
	for btn in action_buttons:
		btn.queue_free()
	action_buttons.clear()
	
	match state:
		0:
			var available = farm_system.get_available_crops()
			for crop in available:
				var btn = Button.new()
				btn.text = "绉?" + crop
				btn.pressed.connect(func(): plant_crop(crop))
				action_container.add_child(btn)
				action_buttons.append(btn)
		
		1, 2:
			if not is_watered:
				var btn = Button.new()
				btn.text = "娴囨按"
				btn.pressed.connect(water_plot)
				action_container.add_child(btn)
				action_buttons.append(btn)
			else:
				var lbl = Label.new()
				lbl.text = "宸叉祰姘达紝绛夊緟鐢熼暱..."
				action_container.add_child(lbl)
				action_buttons.append(lbl)
		
		3:
			var btn = Button.new()
			btn.text = "鏀惰幏"
			btn.pressed.connect(harvest_plot)
			action_container.add_child(btn)
			action_buttons.append(btn)

func plant_crop(crop_type: String) -> void:
	if current_plot_index >= 0 and farm_system:
		farm_system.plant(current_plot_index, crop_type)
		update_plot_info()
		update_buttons()
		emit_signal("action_completed")

func water_plot() -> void:
	if current_plot_index >= 0 and farm_system:
		farm_system.water(current_plot_index)
		update_plot_info()
		update_buttons()
		emit_signal("action_completed")

func harvest_plot() -> void:
	if current_plot_index >= 0 and farm_system:
		farm_system.harvest(current_plot_index)
		update_plot_info()
		update_buttons()
		emit_signal("action_completed")

func on_plot_button_pressed(index: int) -> void:
	show_panel(index)
