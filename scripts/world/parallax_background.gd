extends ParallaxBackground

@export_group("Layer Settings")
@export var sky_scroll_factor: Vector2 = Vector2(0, 0)
@export var far_mountain_scroll_factor: Vector2 = Vector2(0.1, 0.05)
@export var cloud_scroll_factor: Vector2 = Vector2(0.2, 0.1)
@export var far_tree_scroll_factor: Vector2 = Vector2(0.3, 0.15)

@export_group("Visual Settings")
@export var sky_color_top: Color = Color(0.53, 0.81, 0.92)
@export var sky_color_bottom: Color = Color(0.85, 0.90, 0.95)

var layers: Dictionary = {}
var custom_scroll_offset: Vector2 = Vector2.ZERO
var auto_scroll_enabled: bool = true
var auto_scroll_speed: Vector2 = Vector2(5, 2)

func _ready() -> void:
    _setup_sky_layer()
    _setup_default_layers()
    print("[ParallaxBackground] 视差背景已初始化")

func _setup_sky_layer() -> void:
    var sky_layer = get_node_or_null("SkyLayer")
    if sky_layer == null:
        sky_layer = ParallaxLayer.new()
        sky_layer.name = "SkyLayer"
        sky_layer.motion_scale = sky_scroll_factor
        add_child(sky_layer)
        sky_layer.move_to_child_position(0)
    
    var sky_rect = ColorRect.new()
    sky_rect.name = "SkyRect"
    sky_rect.size = Vector2(1920, 1080) * 3
    sky_rect.position = Vector2(-960, -540)
    sky_rect.color = sky_color_bottom
    sky_layer.add_child(sky_rect)

func _setup_default_layers() -> void:
    setup_layer("FarMountainLayer", far_mountain_scroll_factor, Color(0.6, 0.65, 0.7, 0.5))
    setup_layer("CloudLayer", cloud_scroll_factor, Color(1, 1, 1, 0.3))
    setup_layer("FarTreeLayer", far_tree_scroll_factor, Color(0.3, 0.4, 0.3, 0.4))

func setup_layer(layer_name: String, scroll_factor: Vector2, tint: Color) -> void:
    var layer = get_node_or_null(layer_name)
    if layer == null:
        layer = ParallaxLayer.new()
        layer.name = layer_name
        layer.motion_scale = scroll_factor
        add_child(layer)
    
    layers[layer_name] = {
        "layer": layer,
        "scroll_factor": scroll_factor,
        "tint": tint
    }

func add_sprite_to_layer(layer_name: String, sprite: Sprite2D) -> void:
    var layer = get_node_or_null(layer_name)
    if layer != null:
        layer.add_child(sprite)

func _process(delta: float) -> void:
    if auto_scroll_enabled:
        custom_scroll_offset += auto_scroll_speed * delta
        custom_scroll_offset.x = fmod(custom_scroll_offset.x, 2000)
        custom_scroll_offset.y = fmod(custom_scroll_offset.y, 1000)
        
        for layer_name in layers.keys():
            var layer_data = layers[layer_name]
            var layer_node = layer_data["layer"]
            if layer_node != null:
                layer_node.motion_offset.x = custom_scroll_offset.x * layer_data["scroll_factor"].x
                layer_node.motion_offset.y = custom_scroll_offset.y * layer_data["scroll_factor"].y

func set_auto_scroll(enabled: bool) -> void:
    auto_scroll_enabled = enabled

func set_scroll_speed(speed: Vector2) -> void:
    auto_scroll_speed = speed

func update_camera_position(camera_pos: Vector2) -> void:
    custom_scroll_offset = camera_pos
