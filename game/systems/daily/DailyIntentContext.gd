class_name DailyIntentContext
extends RefCounted

const DEFAULT_SEASON: String = "spring"
const DEFAULT_WEATHER: String = "sunny"

const WEATHER_INTENT_LINES: Dictionary = {
	"rainy": {
		"tend_crops": "今天有雨，菜地会自己喝上一些水，可以多看看土壤和可收的作物。",
		"check_village_notice": "雨天去村口不用赶路，顺手留意屋檐下有没有新的纸条。",
		"visit_neighbor": "雨声会让谈话慢下来，适合找一位愿意停脚的人问候。",
		"gather_repair_material": "雨后地面发软，只整理近处材料就好，别把今天变成赶路。",
	},
	"cloudy": {
		"tend_crops": "多云天光线温和，适合慢慢检查每一块地。",
		"check_village_notice": "云层压低时，村口的公告和路边小事会更容易被注意到。",
		"visit_neighbor": "天气不晒，适合在院边或村口多停一会儿。",
		"gather_repair_material": "多云天适合整理木柴和石块，先从顺路的地方开始。",
	},
	"sunny": {
		"tend_crops": "阳光足，适合早些浇水，再看看嫩芽有没有长高。",
		"check_village_notice": "晴天视线清楚，村口到旧枫树旁的小线索都可以慢慢看。",
		"visit_neighbor": "晴天路好走，问候一位路过的人就够了。",
		"gather_repair_material": "晴天适合搬运材料，但今天只需要整理一小段路边的东西。",
	},
}

const SEASON_INTENT_LINES: Dictionary = {
	"spring": {
		"tend_crops": "春天适合从新芽开始，照看一点点也会有回应。",
		"check_village_notice": "春天村口常有新的留言，先看一眼就好。",
		"visit_neighbor": "春天大家会多在路边停留，问候可以很短。",
		"gather_repair_material": "春天的修复先从松动的小地方开始。",
	},
	"summer": {
		"tend_crops": "夏天日头重，浇水和收成最好放在一天前半。",
		"check_village_notice": "夏天村口人多，公告旁的小闲话也会多一点。",
		"visit_neighbor": "夏天适合找阴凉处说话，不必站太久。",
		"gather_repair_material": "夏天搬东西容易累，先整理轻一点的材料。",
	},
	"autumn": {
		"tend_crops": "秋天适合收拾成熟的作物，也适合把地块理顺。",
		"check_village_notice": "秋天的公告常和修整、储备有关，慢慢看。",
		"visit_neighbor": "秋天适合听别人说近来的收成和小烦恼。",
		"gather_repair_material": "秋天修补旧物很合适，先把能用的材料分出来。",
	},
	"winter": {
		"tend_crops": "冬天作物长得慢，确认地块和存下的种子就好。",
		"check_village_notice": "冬天路上安静，村口的纸条可以慢慢读。",
		"visit_neighbor": "冬天问候可以短一些，暖意留在一句话里就够。",
		"gather_repair_material": "冬天先整理屋边材料，别把手冻得太久。",
	},
}


static func get_season_id(time_manager: Node) -> String:
	if time_manager != null:
		if time_manager.has_method("get_date_info"):
			var date_info: Dictionary = time_manager.get_date_info()
			return String(date_info.get("season", DEFAULT_SEASON))
		if time_manager.has_method("get_current_season"):
			return String(time_manager.get_current_season())
	return DEFAULT_SEASON


static func get_weather_id(weather_manager: Node) -> String:
	if weather_manager != null:
		if weather_manager.has_method("get_today_weather"):
			return String(weather_manager.get_today_weather())
		if weather_manager.has_method("get_weather_info"):
			var weather_info: Dictionary = weather_manager.get_weather_info()
			return String(weather_info.get("today", DEFAULT_WEATHER))
	return DEFAULT_WEATHER


static func build_context_line(intent_id: String, time_manager: Node, weather_manager: Node) -> String:
	var weather_id := get_weather_id(weather_manager)
	var weather_line := _line_for(WEATHER_INTENT_LINES, weather_id, intent_id)
	var season_id := get_season_id(time_manager)
	var season_line := _line_for(SEASON_INTENT_LINES, season_id, intent_id)
	if not weather_line.is_empty() and not season_line.is_empty():
		return "%s %s" % [weather_line, season_line]
	if not weather_line.is_empty():
		return weather_line
	return season_line


static func build_planner_feedback(intent_id: String, base_text: String, time_manager: Node, weather_manager: Node) -> String:
	return _append_context(base_text, build_context_line(intent_id, time_manager, weather_manager))


static func build_journal_summary(intent_id: String, base_text: String, time_manager: Node, weather_manager: Node) -> String:
	return _append_context(base_text, build_context_line(intent_id, time_manager, weather_manager))


static func build_chip_hint(intent_id: String, base_text: String, time_manager: Node, weather_manager: Node) -> String:
	return _append_context(base_text, build_context_line(intent_id, time_manager, weather_manager))


static func build_sleep_reflection(intent_id: String, base_text: String, time_manager: Node, weather_manager: Node) -> String:
	return _append_context(base_text, build_context_line(intent_id, time_manager, weather_manager))


static func _line_for(table: Dictionary, context_id: String, intent_id: String) -> String:
	var context_lines: Variant = table.get(context_id, {})
	if context_lines is Dictionary:
		return String((context_lines as Dictionary).get(intent_id, ""))
	return ""


static func _append_context(base_text: String, context_line: String) -> String:
	if context_line.is_empty():
		return base_text
	if base_text.is_empty():
		return context_line
	return "%s %s" % [base_text, context_line]
