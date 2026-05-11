shader_type canvas_item;

uniform float cloud_speed : hint_range(0.0, 2.0) = 0.3;
uniform float cloud_density : hint_range(0.0, 1.0) = 0.4;
uniform vec4 cloud_color : source_color = vec4(1.0, 1.0, 1.0, 0.5);
uniform vec2 cloud_direction : hint_vector2 = vec2(1.0, 0.3);
uniform float time_offset : hint_range(0.0, 10.0) = 0.0;

float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);

    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));

    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

float fbm(vec2 p) {
    float value = 0.0;
    float amplitude = 0.5;
    for (int i = 0; i < 4; i++) {
        value += amplitude * noise(p);
        p *= 2.0;
        amplitude *= 0.5;
    }
    return value;
}

void fragment() {
    vec2 uv = UV;

    // 云的流动动画
    float time = (TIME + time_offset) * cloud_speed * 0.1;
    vec2 cloud_uv = uv * 3.0 + cloud_direction * time;

    // 使用 FBM 噪声创建云层
    float cloud = fbm(cloud_uv);
    cloud = smoothstep(1.0 - cloud_density, 1.0, cloud);

    // 应用到颜色
    vec4 final_color = cloud_color;
    final_color.a *= cloud;

    COLOR = final_color;
}
