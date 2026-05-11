extends Node

signal visitor_arrived(visitor_data: Dictionary)
signal visitor_departed(visitor_id: String)

const VISITOR_TYPES = {
    "seasonal": ["返乡青年", "旅游者", "商人"],
    "relationship": ["居民的朋友", "探亲家人"],
    "random": ["流浪猫", "旅行画家", "迷路的旅人"]
}

var active_visitors: Array = []
var visitor_queue: Array = []

func _ready() -> void:
    print("[Visitor] 访客系统初始化")

func generate_daily_visitors() -> Array:
    var visitors = []
    
    var season = "spring"
    if has_node("/root/TimeSystem"):
        season = get_node("/root/TimeSystem").current_season
    
    var seasonal = VISITOR_TYPES["seasonal"].pick_random()
    visitors.append({
        "type": "seasonal",
        "name": seasonal,
        "arrival_day": 1,
        "stay_days": randi() % 5 + 2,
        "season": season
    })
    
    if randf() < 0.3:
        var random_type = VISITOR_TYPES["random"].pick_random()
        visitors.append({
            "type": "random",
            "name": random_type,
            "arrival_day": randi() % 3 + 1,
            "stay_days": 1
        })
    
    return visitors

func trigger_visitor(visitor_data: Dictionary) -> void:
    active_visitors.append(visitor_data)
    emit_signal("visitor_arrived", visitor_data)
    print("[Visitor] 访客到来: ", visitor_data.get("name", "???"))

func remove_visitor(visitor_id: String) -> void:
    for i in range(active_visitors.size()):
        if active_visitors[i].get("id") == visitor_id:
            active_visitors.remove_at(i)
            emit_signal("visitor_departed", visitor_id)
            print("[Visitor] 访客离开: ", visitor_id)
            break

func is_visitor_active(visitor_name: String) -> bool:
    return active_visitors.any(func(v): return v.get("name") == visitor_name)

func get_active_visitors() -> Array:
    return active_visitors.duplicate()
