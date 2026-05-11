extends Node

var current_scene_path: String = ""
var transition_duration: float = 0.5

signal scene_changed(new_scene: String)

func change_scene(scene_path: String, with_transition: bool = true) -> void:
    if with_transition:
        await play_transition_out()
    
    var root = get_tree().root
    var current = root.get_node_or_null(current_scene_path)
    if current:
        current.queue_free()
    
    var new_scene = load(scene_path)
    if new_scene:
        var instance = new_scene.instantiate()
        root.add_child(instance)
        current_scene_path = scene_path
        emit_signal("scene_changed", scene_path)
        
        if with_transition:
            await play_transition_in()
    else:
        push_error("Failed to load scene: " + scene_path)

func play_transition_out() -> void:
    await get_tree().create_timer(transition_duration).timeout

func play_transition_in() -> void:
    await get_tree().create_timer(transition_duration).timeout
