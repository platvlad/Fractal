uniform vec2 u_resolution;
uniform sampler1D tex;
uniform int max_iterations;
uniform float threshold;
uniform float scale;
uniform vec2 translation;

void main() {
    vec2 st = gl_FragCoord.xy/u_resolution;
    vec2 z = vec2(st.x*4.0 - 2.0, st.y*4.0 - 2.0);
    z += translation;
    z *= vec2(scale, scale);
    vec2 z0 = z;
    int counter = 0;
    while ((z.x * z.x + z.y * z.y < threshold * threshold) && (counter < max_iterations)) {
        vec2 new_z = vec2(z.x * z.x - z.y * z.y + z0.x, 2.0 * z.x * z.y + z0.y);
        z = new_z;
        ++counter;
    }
    float red = 0.0;
    gl_FragColor = texture1D(tex, float(counter) / float(max_iterations));
}
