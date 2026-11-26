shader_type spatial;
render_mode cull_back;

// Finish type: 0 = Solid Lacquer, 1 = Sunburst, 2 = Metallic Flake, 3 = Flame Maple
uniform int finish_type : hint_range(0, 3) = 0;

// Colors
uniform vec4 color_inner : source_color = vec4(1.0, 0.82, 0.28, 1.0);  // Inner amber
uniform vec4 color_mid : source_color = vec4(0.85, 0.18, 0.08, 1.0);    // Mid cherry
uniform vec4 color_rim : source_color = vec4(0.05, 0.02, 0.02, 1.0);    // Outer rim/back
uniform vec4 base_color : source_color = vec4(0.85, 0.14, 0.16, 1.0);   // Solid / flake base

// Sunburst Controls
uniform float burst_falloff : hint_range(0.2, 5.0) = 1.7;
uniform float burst_mid_pos : hint_range(0.1, 0.9) = 0.52;
uniform float waist_pinch : hint_range(0.0, 1.0) = 0.45;
uniform vec2 body_center = vec2(0.0, 0.0);
uniform vec2 body_half_extents = vec2(0.17, 0.23);

// Metallic Flake Controls
uniform float flake_density : hint_range(20.0, 600.0) = 220.0;
uniform float flake_sparkle : hint_range(0.0, 2.5) = 1.0;

// Flame Maple Controls
uniform float flame_frequency : hint_range(10.0, 250.0) = 75.0;
uniform float flame_curl : hint_range(0.0, 10.0) = 3.5;
uniform float flame_intensity : hint_range(0.0, 1.0) = 0.65;

// Physical Material Properties
uniform float metallic : hint_range(0.0, 1.0) = 0.1;
uniform float roughness : hint_range(0.0, 1.0) = 0.2;
uniform float clearcoat : hint_range(0.0, 1.0) = 0.95;
uniform float clearcoat_roughness : hint_range(0.0, 1.0) = 0.05;

// Varyings to pass model/object-space attributes from vertex to fragment
varying vec3 v_model_pos;
varying vec3 v_model_normal;

void vertex() {
    // In vertex shader, VERTEX and NORMAL are in local object/model space
    v_model_pos = VERTEX;
    v_model_normal = NORMAL;
}

void fragment() {
    vec3 final_albedo = base_color.rgb;
    float final_metallic = metallic;
    float final_roughness = roughness;

    // Fixed model-space 2D coordinates centered on the guitar body
    vec2 v_pos = v_model_pos.xy - body_center;
    float nx = abs(v_pos.x) / max(0.01, body_half_extents.x);
    float ny = v_pos.y / max(0.01, body_half_extents.y);

    if (finish_type == 1) { // Contour Sunburst
        // Contour warping for waist pinch in model space
        float pinch = 1.0 + waist_pinch * smoothstep(0.4, -0.05, abs(ny + 0.05));
        float contour_dist = length(vec2(nx * pinch, ny * 0.92));
        
        // Edge/fillet darkening in model space: perimeter sides and fillets have v_model_normal.z near 0
        float edge_factor = 1.0 - clamp(abs(v_model_normal.z), 0.0, 1.0);
        float t = clamp(pow(contour_dist, burst_falloff) + edge_factor * 0.75, 0.0, 1.0);

        if (t < burst_mid_pos) {
            final_albedo = mix(color_inner.rgb, color_mid.rgb, t / burst_mid_pos);
        } else {
            final_albedo = mix(color_mid.rgb, color_rim.rgb, (t - burst_mid_pos) / (1.0 - burst_mid_pos));
        }
    } else if (finish_type == 2) { // Metallic Flake / Sparkle
        // Fixed 3D cell hash on the model surface
        vec3 cell = floor(v_model_pos * flake_density);
        vec3 f_hash = fract(sin(vec3(
            dot(cell, vec3(127.1, 311.7, 74.7)),
            dot(cell, vec3(269.5, 183.3, 246.1)),
            dot(cell, vec3(113.5, 271.9, 124.6))
        )) * 43758.5453);

        vec3 micro_norm = normalize(NORMAL + (f_hash - 0.5) * 0.75);
        vec3 light_dir = normalize(vec3(0.3, 0.8, 0.6));
        vec3 half_v = normalize(light_dir + VIEW);
        float sparkle = pow(max(0.0, dot(micro_norm, half_v)), 32.0);

        final_albedo = mix(base_color.rgb, vec3(1.0, 0.96, 0.92), sparkle * flake_sparkle);
        final_metallic = max(metallic, 0.45);
        final_roughness = mix(roughness, 0.12, sparkle * 0.5);
    } else if (finish_type == 3) { // Flame / Curly Maple
        // Fixed wood grain lines along model coordinates
        float wave = sin(v_model_pos.x * flame_curl * 35.0) * 0.012;
        float flame = sin((v_model_pos.y + wave) * flame_frequency);
        // Dynamic chatoyancy angle as surface tilts relative to view
        float chatoyancy = dot(normalize(NORMAL), normalize(VIEW));
        float flame_mix = smoothstep(-0.5, 0.5, flame + chatoyancy * 0.25);

        // Edge burst in model space
        float contour_dist = length(vec2(nx, ny * 0.9));
        float edge_factor = 1.0 - clamp(abs(v_model_normal.z), 0.0, 1.0);
        float t = clamp(pow(contour_dist, burst_falloff) + edge_factor * 0.65, 0.0, 1.0);

        vec3 wood_core = mix(color_inner.rgb, color_mid.rgb, flame_mix * flame_intensity);
        final_albedo = mix(wood_core, color_rim.rgb, smoothstep(0.7, 1.0, t));
    }

    ALBEDO = final_albedo;
    METALLIC = final_metallic;
    ROUGHNESS = final_roughness;
    CLEARCOAT = clearcoat;
    CLEARCOAT_ROUGHNESS = clearcoat_roughness;
}
