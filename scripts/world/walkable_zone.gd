extends Node2D

@export var polygon: PackedVector2Array = PackedVector2Array()
@export var debug_draw: bool = false
@export var debug_fill_color: Color = Color(0.15, 0.75, 0.25, 0.18)
@export var debug_outline_color: Color = Color(0.1, 0.9, 0.35, 0.75)


func _ready() -> void:
    queue_redraw()


func _draw() -> void:
    if not visible:
        return
    if not debug_draw:
        return
    if polygon.size() < 3:
        return
    draw_colored_polygon(polygon, debug_fill_color)

    var closed: PackedVector2Array = polygon.duplicate()
    closed.append(polygon[0])
    draw_polyline(closed, debug_outline_color, 2.0)


func contains_global_point(global_point: Vector2) -> bool:
    if polygon.size() < 3:
        return true
    var local_point := to_local(global_point)
    return Geometry2D.is_point_in_polygon(local_point, polygon)


func closest_global_point(global_point: Vector2) -> Vector2:
    if polygon.size() < 3:
        return global_point

    var local_point := to_local(global_point)
    if Geometry2D.is_point_in_polygon(local_point, polygon):
        return global_point

    var closest := polygon[0]
    var closest_distance := INF
    for i in polygon.size():
        var a := polygon[i]
        var b := polygon[(i + 1) % polygon.size()]
        var candidate := Geometry2D.get_closest_point_to_segment(local_point, a, b)
        var distance := candidate.distance_squared_to(local_point)
        if distance < closest_distance:
            closest_distance = distance
            closest = candidate

    return to_global(closest)
