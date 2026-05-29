class_name GreenfieldAssetPaths
extends RefCounted

const UI_PAPER_PANEL := "res://assets/ui/panels/ui_panel_paper_01.png"
const UI_WOOD_PANEL := "res://assets/ui/panels/ui_panel_wood_01.png"
const UI_BUTTON_NORMAL := "res://assets/ui/buttons/ui_button_normal.png"
const UI_BUTTON_HOVER := "res://assets/ui/buttons/ui_button_hover.png"
const UI_BUTTON_PRESSED := "res://assets/ui/buttons/ui_button_pressed.png"
const UI_SLOT_ITEM := "res://assets/ui/slots/ui_slot_item.png"
const UI_SLOT_SELECTED := "res://assets/ui/slots/ui_slot_selected.png"
const UI_TAB_NORMAL := "res://assets/ui/tabs/ui_tab_normal.png"
const UI_TAB_ACTIVE := "res://assets/ui/tabs/ui_tab_active.png"
const UI_CHECKBOX_ON := "res://assets/ui/widgets/ui_checkbox_on.png"
const UI_CHECKBOX_OFF := "res://assets/ui/widgets/ui_checkbox_off.png"
const UI_SCROLLBAR := "res://assets/ui/widgets/ui_scrollbar.png"

const UI_ICON_COIN := "res://assets/ui/icons/ui_icon_coin.png"
const UI_ICON_HEART := "res://assets/ui/icons/ui_icon_heart.png"
const UI_ICON_WEATHER_SUN := "res://assets/ui/icons/ui_icon_weather_sun.png"
const UI_ICON_WEATHER_RAIN := "res://assets/ui/icons/ui_icon_weather_rain.png"
const UI_ICON_BAG := "res://assets/ui/icons/ui_icon_bag.png"
const UI_ICON_MAP := "res://assets/ui/icons/ui_icon_map.png"
const UI_ICON_SETTINGS := "res://assets/ui/icons/ui_icon_settings.png"

const UI_MAP_VILLAGE_PAPER := "res://assets/ui/maps/ui_map_village_paper_01.png"
const UI_SETTINGS_PAPER_PREVIEW := "res://assets/ui/screens/ui_settings_paper_preview.png"

const HOME_AREA_COMPONENT_ROOT := "res://assets/art/greenfield_p0/regions/home_area/components"
const HOME_HOUSE_BODY := "res://assets/art/greenfield_p0/regions/home_area/components/home_house_body_01.png"
const HOME_HOUSE_ROOF := "res://assets/art/greenfield_p0/regions/home_area/components/home_house_roof_01.png"
const HOME_WELL := "res://assets/art/greenfield_p0/regions/home_area/components/home_well_01.png"
const HOME_MAILBOX := "res://assets/art/greenfield_p0/regions/home_area/components/home_mailbox_01.png"
const HOME_FENCE_HORIZONTAL := "res://assets/art/greenfield_p0/regions/home_area/components/home_fence_horizontal_01.png"
const HOME_FENCE_VERTICAL := "res://assets/art/greenfield_p0/regions/home_area/components/home_fence_vertical_01.png"
const HOME_FENCE_CORNER := "res://assets/art/greenfield_p0/regions/home_area/components/home_fence_corner_01.png"
const HOME_GARDEN_PLOT_GROWN := "res://assets/art/greenfield_p0/regions/home_area/components/home_garden_plot_grown_01.png"
const HOME_TREE_LARGE := "res://assets/art/greenfield_p0/regions/home_area/components/home_tree_large_01.png"
const HOME_BUSH_FLOWER := "res://assets/art/greenfield_p0/regions/home_area/components/home_bush_flower_01.png"
const HOME_TABLE_WOOD := "res://assets/art/greenfield_p0/regions/home_area/components/home_table_wood_01.png"
const HOME_BRIDGE_WOOD := "res://assets/art/greenfield_p0/regions/home_area/components/home_bridge_wood_01.png"
const HOME_AREA_INTERACTION_POINTS := "res://assets/scenes/home_area/scene_home_area_interaction_points.json"


static func item_icon_path(item_id: String) -> String:
	return "res://assets/items/icons/icon_%s.png" % item_id


static func load_texture(path: String, fallback_path: String = "") -> Texture2D:
	var texture := _load_direct(path)
	if texture != null:
		return texture
	if fallback_path.is_empty() or fallback_path == path:
		return null
	return _load_direct(fallback_path)


static func _load_direct(path: String) -> Texture2D:
	if path.is_empty():
		return null
	if ResourceLoader.exists(path):
		return load(path) as Texture2D
	if FileAccess.file_exists(path):
		var image := Image.load_from_file(path)
		if image != null and not image.is_empty():
			return ImageTexture.create_from_image(image)
	return null
