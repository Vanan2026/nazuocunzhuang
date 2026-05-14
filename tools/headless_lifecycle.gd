extends RefCounted
class_name HeadlessLifecycle

const SETTLE_SECONDS := 0.65
const SETTLE_FRAMES := 3


static func load_packed_scene(path: String) -> PackedScene:
	return ResourceLoader.load(path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE) as PackedScene


static func cleanup_and_quit(tree: SceneTree, exit_code: int = 0) -> void:
	await cleanup(tree)
	tree.quit(exit_code)


static func cleanup(tree: SceneTree) -> void:
	if tree == null:
		return

	_cleanup_autoloads(tree)
	_release_audio_players(tree.root)
	_queue_free_runtime_nodes(tree)

	await _settle_frames(tree, SETTLE_FRAMES)
	await _wait_with_timer(tree, SETTLE_SECONDS)
	await _settle_frames(tree, SETTLE_FRAMES)

	_release_audio_players(tree.root)


static func _cleanup_autoloads(tree: SceneTree) -> void:
	for child in tree.root.get_children():
		if child != null and child.has_method("cleanup_for_headless"):
			child.call("cleanup_for_headless")


static func _queue_free_runtime_nodes(tree: SceneTree) -> void:
	var autoload_names := _get_autoload_names()
	if tree.current_scene != null:
		tree.current_scene.queue_free()
		tree.current_scene = null

	for child in tree.root.get_children():
		if autoload_names.has(String(child.name)):
			continue
		if child.is_queued_for_deletion():
			continue
		child.queue_free()


static func _get_autoload_names() -> Dictionary:
	var names := {}
	for property in ProjectSettings.get_property_list():
		var property_name := String(property.get("name", ""))
		if property_name.begins_with("autoload/"):
			names[property_name.get_slice("/", 1)] = true
	return names


static func _release_audio_players(root_node: Node) -> void:
	if root_node == null:
		return
	_release_audio_players_recursive(root_node)


static func _release_audio_players_recursive(node: Node) -> void:
	if node is AudioStreamPlayer:
		var player := node as AudioStreamPlayer
		player.stop()
		player.stream = null

	for child in node.get_children():
		_release_audio_players_recursive(child)


static func _settle_frames(tree: SceneTree, count: int) -> void:
	for _i in range(count):
		await tree.process_frame


static func _wait_with_timer(tree: SceneTree, seconds: float) -> void:
	var timer := Timer.new()
	timer.one_shot = true
	timer.wait_time = seconds
	tree.root.add_child(timer)
	timer.start()
	await timer.timeout
	timer.queue_free()
