extends Node2D

signal crop_planted(plot_index: int, crop_type: String)
signal crop_harvested(plot_index: int, crop_type: String, amount: int)
signal inventory_changed

const PLOT_COLS: int = 3
const PLOT_ROWS: int = 3
const TOTAL_PLOTS: int = PLOT_COLS * PLOT_ROWS

const SEASON_CROPS = {
    "spring": ["萝卜", "白菜", "番茄", "黄瓜"],
    "summer": ["西瓜", "葡萄", "甜瓜", "茄子"],
    "autumn": ["南瓜", "玉米", "苹果", "葡萄"],
    "winter": ["白菜", "萝卜", "菠菜", "土豆"]
}

const CROP_DATA = {
    "萝卜": {"days": 5, "sell_price": 10},
    "白菜": {"days": 7, "sell_price": 20},
    "番茄": {"days": 6, "sell_price": 25},
    "黄瓜": {"days": 4, "sell_price": 15},
    "西瓜": {"days": 8, "sell_price": 30},
    "葡萄": {"days": 6, "sell_price": 20},
    "甜瓜": {"days": 10, "sell_price": 50},
    "茄子": {"days": 7, "sell_price": 25},
    "南瓜": {"days": 9, "sell_price": 35},
    "玉米": {"days": 8, "sell_price": 28},
    "苹果": {"days": 12, "sell_price": 40},
    "菠菜": {"days": 5, "sell_price": 18},
    "土豆": {"days": 6, "sell_price": 22}
}

class FarmPlot:
    var state: int = 0
    var crop_type: String = ""
    var growth_progress: float = 0.0
    var days_growing: int = 0
    var max_days: int = 7
    var is_watered: bool = false

var plots: Array = []
var inventory: Dictionary = {}

func _ready() -> void:
    add_to_group("farm_system")
    init_plots()
    _connect_time_system()
    print("[Farm] 后院种地系统初始化完成，共 ", TOTAL_PLOTS, " 块田地")

func init_plots() -> void:
    plots.clear()
    for i in range(TOTAL_PLOTS):
        plots.append(FarmPlot.new())

func get_current_season() -> String:
    if has_node("/root/TimeSystem"):
        return get_node("/root/TimeSystem").current_season
    return "spring"

func get_available_crops() -> Array:
    return SEASON_CROPS.get(get_current_season(), SEASON_CROPS["spring"])

func plant(plot_index: int, crop_type: String) -> bool:
    if plot_index < 0 or plot_index >= TOTAL_PLOTS:
        return false

    var plot = plots[plot_index]
    if plot.state != 0:
        print("[Farm] 田地 ", plot_index, " 已有农作物，无法种植")
        return false

    var available = get_available_crops()
    if crop_type not in available:
        print("[Farm] ", crop_type, " 不适合当前季节种植")
        return false

    plot.crop_type = crop_type
    plot.state = 1
    plot.days_growing = 0
    plot.max_days = CROP_DATA.get(crop_type, {}).get("days", 7)
    plot.growth_progress = 0.0
    plot.is_watered = false

    emit_signal("crop_planted", plot_index, crop_type)
    print("[Farm] 在田地", plot_index, " 种植了", crop_type)
    return true

func water(plot_index: int) -> bool:
    if plot_index < 0 or plot_index >= TOTAL_PLOTS:
        return false

    var plot = plots[plot_index]
    if plot.state == 0:
        print("[Farm] 田地 ", plot_index, " 是空的")
        return false

    plot.is_watered = true
    print("[Farm] 给田地", plot_index, " 浇水")
    return true

func harvest(plot_index: int) -> bool:
    if plot_index < 0 or plot_index >= TOTAL_PLOTS:
        return false

    var plot = plots[plot_index]
    if plot.state != 3:
        print("[Farm] 田地 ", plot_index, " 农作物尚未成熟")
        return false

    var crop_type = plot.crop_type
    var amount = 1

    inventory[crop_type] = inventory.get(crop_type, 0) + amount
    emit_signal("inventory_changed")

    plot.state = 0
    plot.crop_type = ""
    plot.growth_progress = 0.0
    plot.days_growing = 0
    plot.is_watered = false

    emit_signal("crop_harvested", plot_index, crop_type, amount)
    print("[Farm] 收获了", amount, " 个", crop_type)
    return true

func advance_day() -> void:
    for i in range(TOTAL_PLOTS):
        var plot = plots[i]
        if plot.state == 0 or plot.state == 3:
            continue

        if plot.is_watered:
            plot.days_growing += 1
            plot.growth_progress = float(plot.days_growing) / float(plot.max_days)
            if plot.state == 1:
                plot.state = 2

            if plot.growth_progress >= 1.0:
                plot.state = 3
                print("[Farm] 田地 ", i, " 的", plot.crop_type, " 成熟了！")

        plot.is_watered = false

func get_plot_info(plot_index: int) -> Dictionary:
    if plot_index < 0 or plot_index >= TOTAL_PLOTS:
        return {}

    var plot = plots[plot_index]
    return {
        "state": plot.state,
        "state_name": ["empty", "planted", "growing", "ready"][plot.state],
        "crop_type": plot.crop_type,
        "growth_progress": plot.growth_progress,
        "days_growing": plot.days_growing,
        "max_days": plot.max_days,
        "is_watered": plot.is_watered
    }

func get_inventory() -> Dictionary:
    return inventory.duplicate()

func on_interact(interactor: Node) -> void:
    pass

func _connect_time_system() -> void:
    if not has_node("/root/TimeSystem"):
        return

    var time_system := get_node("/root/TimeSystem")
    if time_system.has_signal("day_advanced") and not time_system.day_advanced.is_connected(advance_day):
        time_system.day_advanced.connect(advance_day)
