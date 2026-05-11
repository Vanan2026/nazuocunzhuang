extends Node2D

@onready var sky_rect: ColorRect = $SkyRect
@onready var cloud_layer: ColorRect = $CloudLayer
@onready var tint_rect: ColorRect = $TintLayer

var current_season: String = "spring"
var time_of_day: float = 0.5  # 0=午夜, 0.5=正午, 1=午夜

const SEASON_COLORS = {
    "spring": {
        "top": Color(0.6, 0.75, 0.95),
        "bottom": Color(0.9, 0.88, 0.82)
    },
    "summer": {
        "top": Color(0.5, 0.7, 0.9),
        "bottom": Color(0.95, 0.92, 0.85)
    },
    "autumn": {
        "top": Color(0.7, 0.75, 0.85),
        "bottom": Color(0.95, 0.85, 0.75)
    },
    "winter": {
        "top": Color(0.75, 0.8, 0.95),
        "bottom": Color(0.9, 0.92, 0.98)
    }
}

func _ready() -> void:
    # 连接时间系统信号
    if has_node("/root/TimeSystem"):
        var ts = get_node("/root/TimeSystem")
        ts.season_advanced.connect(_on_season_changed)

func _on_season_changed(new_season: String) -> void:
    current_season = new_season
    update_sky_colors()

func update_sky_colors() -> void:
    if not sky_rect:
        return

    var colors = SEASON_COLORS.get(current_season, SEASON_COLORS["spring"])
    var sky_material = sky_rect.material as ShaderMaterial

    if sky_material:
        sky_material.set_shader_parameter("sky_color_top", colors["top"])
        sky_material.set_shader_parameter("sky_color_bottom", colors["bottom"])

func set_time_of_day(time: float) -> void:
    time_of_day = clamp(time, 0.0, 1.0)
    # 根据时间调整天空颜色
    var sky_material = sky_rect.material as ShaderMaterial if sky_rect else null
    if sky_material:
        # 简单的日出-正午-日落-夜晚颜色调整
        var brightness = sin(time_of_day * PI)
        sky_material.set_shader_parameter("time_offset", time_of_day)

func set_season_blend(blend: float) -> void:
    var tint_material = tint_rect.material as ShaderMaterial if tint_rect else null
    if tint_material:
        tint_material.set_shader_parameter("season_blend", blend)
