shader_type canvas_item;

uniform vec4 light_color : source_color = vec4(1.0, 0.98, 0.85, 0.6);
uniform float flicker_speed : hint_range(0.0, 2.0) = 0.8;
uniform float flicker_density : hint_range(0.0, 1.0) = 0.3;
uniform vec2 light_direction : hint_vector2 = vec2(0.5, -0.5);

float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
}

float light_flcker(vec2 uv, float time) {
    vec2 grid_uv = floor(uv * 20.0);
    float h = hash(grid_uv);

    // 随机闪烁
    float flicker = step(1.0 - flicker_density, h);
    float anim = sin(time * flicker_speed + h * 6.28) * 0.5 + 0.5;

    return flicker * anim;
}

void fragment() {
    vec2 uv = UV;

    // 从光源方向投射斑驳
    vec2 offset = light_direction * 0.1;
    vec2 flick_uv = uv + offset;

    float flicker = light_flcker(flick_uv, TIME);

    vec4 final_color = light_color;
    final_color.a *= flicker;

    COLOR = final_color;
}
