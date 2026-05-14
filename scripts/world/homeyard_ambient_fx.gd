extends Node2D

@export var cloud_drift_pixels: float = 18.0
@export var cloud_drift_seconds: float = 18.0
@export var leaf_sway_pixels: float = 3.0
@export var leaf_sway_seconds: float = 3.8
@export var shadow_drift_pixels: float = 6.0
@export var shadow_drift_seconds: float = 7.5
@export var windchime_sway_degrees: float = 2.4
@export var windchime_sway_seconds: float = 2.8

@onready var clouds: Sprite2D = $Clouds
@onready var leaves: Sprite2D = $LeafMotionTop
@onready var dapple_shadow: Sprite2D = $DappleShadow
@onready var wind_chime: Sprite2D = $WindChime

var _cloud_origin: Vector2
var _leaf_origin: Vector2
var _shadow_origin: Vector2
var _time: float = 0.0


func _ready() -> void:
    _cloud_origin = clouds.position
    _leaf_origin = leaves.position
    _shadow_origin = dapple_shadow.position
    dapple_shadow.modulate.a = 0.55
    wind_chime.rotation_degrees = 0.0


func _process(delta: float) -> void:
    _time += delta
    var cloud_phase := TAU * _time / cloud_drift_seconds
    clouds.position = _cloud_origin + Vector2(sin(cloud_phase) * cloud_drift_pixels, cos(cloud_phase * 0.7) * 2.0)

    var leaf_phase := TAU * _time / leaf_sway_seconds
    leaves.position = _leaf_origin + Vector2(sin(leaf_phase) * leaf_sway_pixels, cos(leaf_phase * 1.3) * 1.2)
    leaves.modulate.a = 0.78 + sin(leaf_phase * 0.8) * 0.08

    var shadow_phase := TAU * _time / shadow_drift_seconds
    dapple_shadow.position = _shadow_origin + Vector2(sin(shadow_phase) * shadow_drift_pixels, cos(shadow_phase * 0.9) * 2.5)
    dapple_shadow.modulate.a = 0.48 + sin(shadow_phase * 1.4) * 0.08

    var chime_phase := TAU * _time / windchime_sway_seconds
    wind_chime.rotation_degrees = sin(chime_phase) * windchime_sway_degrees
