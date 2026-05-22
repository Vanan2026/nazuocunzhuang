extends SceneTree

const HeadlessLifecycle := preload("res://tools/headless_lifecycle.gd")
const GALLERY_SCENE := "res://scenes/dev/greenfield_p0_asset_gallery.tscn"

var _finishing := false


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var error := change_scene_to_file(GALLERY_SCENE)
	if error != OK:
		_fail("could not load greenfield gallery scene: %s" % error)
		return

	await process_frame
	await process_frame

	var gallery := current_scene
	if gallery == null:
		_fail("gallery scene did not become current_scene")
		return
	if gallery.name != "GreenfieldP0AssetGallery":
		_fail("gallery root must be GreenfieldP0AssetGallery")
		return
	if bool(gallery.get_meta("launch_quality_approved", true)):
		_fail("gallery metadata launch_quality_approved must remain false")
		return

	for path in [
		"CharacterSamples",
		"SeasonTileSamples",
		"UISamples",
		"PropSamples",
		"RegionSamples",
		"CharacterSamples/PlayerIdleDown",
		"SeasonTileSamples/SpringGrassTile",
		"UISamples/PanelFrame",
		"PropSamples/HouseProp",
		"RegionSamples/home_area/BaseGround",
		"RegionSamples/village/BaseGround",
		"RegionSamples/back_farm/BaseGround",
		"RegionSamples/forest_edge/BaseGround",
		"RegionSamples/orchard/BaseGround",
		"RegionSamples/pond/BaseGround",
		"RegionSamples/mountain_path/BaseGround",
		"RegionSamples/mountain_hut/BaseGround",
		"RegionSamples/mountain/BaseGround",
		"RegionSamples/cliff_view/BaseGround",
	]:
		if gallery.get_node_or_null(path) == null:
			_fail("gallery missing node: %s" % path)
			return

	for path in [
		"CharacterSamples/PlayerIdleDown",
		"SeasonTileSamples/SpringGrassTile",
		"UISamples/PanelFrame",
		"PropSamples/HouseProp",
		"RegionSamples/home_area/BaseGround",
		"RegionSamples/village/BaseGround",
		"RegionSamples/back_farm/BaseGround",
	]:
		var sprite := gallery.get_node_or_null(path) as Sprite2D
		if sprite == null or sprite.texture == null:
			_fail("gallery sprite missing texture: %s" % path)
			return

	print("OK: greenfield P0 asset gallery validates")
	_finish_deferred(0)


func _fail(message: String) -> void:
	printerr("FAIL: %s" % message)
	_finish_deferred(1)


func _finish_deferred(exit_code: int) -> void:
	if _finishing:
		return
	_finishing = true
	call_deferred("_finish", exit_code)


func _finish(exit_code: int) -> void:
	await HeadlessLifecycle.cleanup_and_quit(self, exit_code)
