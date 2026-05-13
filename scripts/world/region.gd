extends Node2D
class_name Region

signal region_loaded(region_id: String)
signal region_unloading(region_id: String)
signal region_activated(region_id: String)
signal region_deactivated(region_id: String)

@export var region_id: String = ""
@export var region_display_name: String = ""
@export var region_size: Vector2 = Vector2(4096, 4096)
@export var world_offset: Vector2 = Vector2.ZERO

@export var adjacent_regions: Array[String] = []
@export var is_always_loaded: bool = false

@export_group("Loading Settings")
@export var preload_distance: float = 800.0
@export var unload_distance: float = 1500.0
@export var fade_transition_time: float = 0.5

var is_loaded: bool = false
var is_active: bool = false
var load_priority: int = 0

var region_state: Dictionary = {}

func _ready() -> void:
    region_id = region_id if region_id else name
    _on_ready()

func _on_ready() -> void:
    pass

func get_world_bounds() -> Rect2:
    return Rect2(world_offset, region_size)

func get_center() -> Vector2:
    return world_offset + region_size / 2

func is_point_inside(p: Vector2) -> bool:
    var bounds := get_world_bounds()
    return bounds.has_point(p)

func distance_to_region(point: Vector2) -> float:
    var bounds := get_world_bounds()
    var closest := Vector2(
        clamp(point.x, bounds.position.x, bounds.end.x),
        clamp(point.y, bounds.position.y, bounds.end.y)
    )
    return point.distance_to(closest)

func should_preload(player_pos: Vector2) -> bool:
    if is_loaded:
        return false
    return distance_to_region(player_pos) < preload_distance

func should_unload(player_pos: Vector2) -> bool:
    if is_always_loaded:
        return false
    if is_loaded and not is_active:
        return distance_to_region(player_pos) > unload_distance
    return false

func should_activate(player_pos: Vector2) -> bool:
    if not is_loaded:
        return false
    var bounds := get_world_bounds()
    var expanded_bounds := bounds.grow(preload_distance)
    return expanded_bounds.has_point(player_pos)

func should_deactivate(player_pos: Vector2) -> bool:
    if not is_active:
        return false
    var bounds := get_world_bounds()
    var expanded_bounds := bounds.grow(unload_distance * 0.5)
    return not expanded_bounds.has_point(player_pos)

func load_region() -> void:
    if is_loaded:
        return
    is_loaded = true
    _on_load()
    emit_signal("region_loaded", region_id)
    print("[Region] 已加载: ", region_id)

func unload_region() -> void:
    if not is_loaded:
        return
    emit_signal("region_unloading", region_id)
    _on_unload()
    is_loaded = false
    is_active = false
    print("[Region] 已卸载: ", region_id)

func activate() -> void:
    if not is_loaded:
        return
    if is_active:
        return
    is_active = true
    _on_activate()
    emit_signal("region_activated", region_id)

func deactivate() -> void:
    if not is_active:
        return
    is_active = false
    _on_deactivate()
    emit_signal("region_deactivated", region_id)

func _on_load() -> void:
    _set_visibility(false)

func _on_unload() -> void:
    pass

func _on_activate() -> void:
    _set_visibility(true)

func _on_deactivate() -> void:
    _set_visibility(false)

func _set_visibility(visible: bool) -> void:
    for child in get_children():
        if child is Region:
            continue
        if child is Camera2D:
            continue
        if child.has_method("set_process"):
            child.set_process(visible)
        if child is CanvasItem:
            child.visible = visible

func save_state() -> Dictionary:
    return {
        "region_id": region_id,
        "timestamp": Time.get_unix_time_from_system()
    }

func load_state(state: Dictionary) -> void:
    region_state = state
    _on_state_loaded(state)

func _on_state_loaded(state: Dictionary) -> void:
    pass

func get_metadata() -> Dictionary:
    return {
        "region_id": region_id,
        "display_name": region_display_name,
        "size": region_size,
        "world_offset": world_offset,
        "adjacent_regions": adjacent_regions
    }
