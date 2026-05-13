extends Node2D

const HOME_AREA_BGM := "res://audio/bgm/Sunlight_on_the_Veranda.mp3"


func _ready() -> void:
	var audio_manager := get_node_or_null("/root/AudioManager")
	if audio_manager == null:
		push_warning("[Region_HomeArea] AudioManager autoload missing; skip BGM")
		return

	audio_manager.play_bgm(HOME_AREA_BGM, true)
