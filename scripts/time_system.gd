extends Node

const SEASONS = ["spring", "summer", "autumn", "winter"]
const DAYS_PER_SEASON = 30

var current_day: int = 1
var current_season: String = "spring"
var time_progress: float = 0.0

signal day_advanced
signal season_advanced(new_season: String)

func _ready() -> void:
    pass

func _process(delta: float) -> void:
    pass

func advance_day() -> void:
    current_day += 1
    emit_signal("day_advanced")
    if current_day > DAYS_PER_SEASON:
        advance_season()

func advance_season() -> void:
    current_day = 1
    var season_index = SEASONS.find(current_season)
    season_index = (season_index + 1) % SEASONS.size()
    current_season = SEASONS[season_index]
    emit_signal("season_advanced", current_season)

func get_season_color() -> Color:
    match current_season:
        "spring": return Color(1.0, 0.85, 0.8)
        "summer": return Color(1.0, 1.0, 0.85)
        "autumn": return Color(1.0, 0.85, 0.7)
        "winter": return Color(0.85, 0.9, 1.0)
    return Color.WHITE
