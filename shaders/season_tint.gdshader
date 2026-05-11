shader_type canvas_item;

uniform vec4 spring_tint : source_color = vec4(1.0, 0.97, 0.93, 1.0);
uniform vec4 summer_tint : source_color = vec4(1.0, 1.0, 0.93, 1.0);
uniform vec4 autumn_tint : source_color = vec4(1.0, 0.88, 0.75, 1.0);
uniform vec4 winter_tint : source_color = vec4(0.88, 0.92, 1.0, 1.0);

uniform float season_blend : hint_range(0.0, 1.0) = 0.0;
uniform int current_season : hint_range(0, 3) = 0; // 0=spring, 1=summer, 2=autumn, 3=winter

uniform float vignette_intensity : hint_range(0.0, 1.0) = 0.3;

void fragment() {
    vec4 base_color = texture(TEXTURE, UV);

    // 根据季节选择色调
    vec4 tint = spring_tint;
    if (current_season == 1) {
        tint = summer_tint;
    } else if (current_season == 2) {
        tint = autumn_tint;
    } else if (current_season == 3) {
        tint = winter_tint;
    }

    // 季节转换时的混合
    vec4 final_tint = mix(tint, spring_tint, season_blend);

    // 应用色调
    vec4 final_color = base_color * final_tint;

    // 添加暗角效果
    vec2 vignette_uv = UV * (1.0 - UV);
    float vignette = vignette_uv.x * vignette_uv.y * 15.0;
    vignette = pow(vignette, vignette_intensity);
    final_color.rgb *= vignette;

    COLOR = final_color;
}
