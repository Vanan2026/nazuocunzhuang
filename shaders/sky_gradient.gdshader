shader_type canvas_item;

uniform vec4 sky_color_top : source_color = vec4(0.6, 0.75, 0.95, 1.0);
uniform vec4 sky_color_bottom : source_color = vec4(0.9, 0.88, 0.82, 1.0);
uniform float time_offset : hint_range(0.0, 1.0) = 0.0;
uniform float animation_speed : hint_range(0.0, 0.5) = 0.05;

void fragment() {
    // 动态渐变，带有轻微的呼吸感
    float wave = sin(TIME * animation_speed + time_offset * 6.28) * 0.015;
    float gradient = UV.y + wave;
    gradient = clamp(gradient, 0.0, 1.0);

    // 颜色插值
    vec4 sky = mix(sky_color_bottom, sky_color_top, gradient);

    // 添加轻微的光晕效果
    float glow = smoothstep(0.3, 0.7, UV.y) * 0.1;
    sky.rgb += glow;

    COLOR = sky;
}
