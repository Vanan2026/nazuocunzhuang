class_name WeeklyRhythmContext
extends RefCounted

const WEEKLY_RHYTHMS: Array[Dictionary] = [
	{
		"id": "settle",
		"label": "修整日",
		"planner": "把屋边、菜地和背包顺一顺，今天只要让动线更清楚。",
		"journal": "适合整理屋边、菜地和背包，让接下来的几天更顺。",
		"chip": "先从屋边和菜地的小整理开始。",
	},
	{
		"id": "village_gate",
		"label": "村口日",
		"planner": "适合去公告旁站一会儿，看看村里有没有新的闲话。",
		"journal": "适合绕到村口，读一眼公告，也听听路边的小消息。",
		"chip": "村口公告和旧枫树旁都可以慢慢看。",
	},
	{
		"id": "neighbor",
		"label": "邻里日",
		"planner": "适合和一位路过的人问候，不需要把话聊得很长。",
		"journal": "适合找一位邻居说几句，给关系留一点自然的温度。",
		"chip": "遇到邻居时停一下，问候一句就够。",
	},
	{
		"id": "garden",
		"label": "菜地日",
		"planner": "适合多看一眼作物、土壤和水井，慢慢确认今天的地块。",
		"journal": "适合把注意力放回菜地，浇水、收成或整理都可以。",
		"chip": "菜地、旧水井和收成状态值得先看。",
	},
	{
		"id": "materials",
		"label": "材料日",
		"planner": "适合顺路收一点木柴和石块，别把它变成赶路。",
		"journal": "适合整理修复材料，为之后的村庄修补留一点余裕。",
		"chip": "顺路捡近处材料，不用跑完整张地图。",
	},
	{
		"id": "walk",
		"label": "散步日",
		"planner": "适合沿熟悉的小路慢慢走，留意平时容易错过的角落。",
		"journal": "适合在院子、村口和林边之间走一圈，发现藏在生活里的小事。",
		"chip": "沿熟路散步，路边细节比远路更重要。",
	},
	{
		"id": "quiet",
		"label": "安静日",
		"planner": "适合少安排一点，只做眼前最舒服的一件小事。",
		"journal": "适合把节奏放慢，回屋、看地、听雨声都算过好今天。",
		"chip": "少做一点也可以，先照顾眼前的小事。",
	},
]


static func get_total_day(time_manager: Node) -> int:
	if time_manager != null:
		if time_manager.has_method("get_date_info"):
			var date_info: Dictionary = time_manager.get_date_info()
			return maxi(1, int(date_info.get("total_day", 1)))
		if time_manager.has_method("get_total_day"):
			return maxi(1, int(time_manager.get_total_day()))
	return 1


static func get_rhythm_for_day(time_manager: Node) -> Dictionary:
	var index := (get_total_day(time_manager) - 1) % WEEKLY_RHYTHMS.size()
	return WEEKLY_RHYTHMS[index]


static func build_planner_status(base_text: String, time_manager: Node) -> String:
	return _append_line(base_text, _format_rhythm_line("今日节奏", "planner", time_manager))


static func build_journal_note(base_text: String, time_manager: Node) -> String:
	return _append_line(base_text, _format_rhythm_line("本周节奏", "journal", time_manager))


static func build_chip_hint(base_text: String, time_manager: Node) -> String:
	return _append_line(base_text, _format_rhythm_line("节奏提示", "chip", time_manager))


static func _format_rhythm_line(prefix: String, copy_key: String, time_manager: Node) -> String:
	var rhythm := get_rhythm_for_day(time_manager)
	var label := String(rhythm.get("label", "日常"))
	var copy := String(rhythm.get(copy_key, "今天按自己的步子慢慢来。"))
	return "%s：%s - %s" % [prefix, label, copy]


static func _append_line(base_text: String, extra_line: String) -> String:
	if extra_line.is_empty():
		return base_text
	if base_text.is_empty():
		return extra_line
	return "%s\n%s" % [base_text, extra_line]
