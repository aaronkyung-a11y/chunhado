# v0.11 (5/…): 확대했을 때의 지도  (ui3d.js · ui_panels.js)
#  요청: "확대했을 때 지도가 깨진다."
#  까닭: 바탕 그림은 지도 전체가 3072×2610 한 장이라, 가장 크게 당기면 그림의 한 점이 화면의 서너 점이 된다. 그사이를 곧은 선으로 메우다 보니(이중 선형)
#        물가의 먹점 같은 가는 붓자국이 계단처럼 각져 보였다.
#  고침: 그림이 크게 늘어나 보일 때(확대 1.25 언저리부터 서서히, 2.1 부터 온전히 — 그 아래에서는 전과 똑같다)만
#        ① 둥글게 메우고(3차 B-스플라인 — 계단이 사라진다), ② 읽는 자리를 종이 결 잡음으로 그림 1.2점 안팎 흔들어 먹이 종이에 번진 듯한 가장자리를 만들고,
#        ③ 고운 종이 결을 덧입힌다. 멀리서 볼 때의 모습과 속도는 그대로다.
#  한계: 그림 자체를 더 크게 굽는 것이 아니라서 새 붓자국이 생기지는 않는다 — 각진 계단이 번짐으로 바뀐다. 또렷한 물가 선은 물가를 따로 그려 넣어야 한다(다음에).
#  기기: 가지 안에서 그림을 읽으려면 '몇 번째 축소본을 읽을지'를 직접 정해야 한다(texture2DLodEXT). WebGL2 이거나 EXT_shader_texture_lod 가 있을 때만 켠다 — 없으면 전과 같다.
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)

p = 'src/ui3d.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "  'const float SQ3 = 1.7320508;',\n",
"""  'const float SQ3 = 1.7320508;',
  '#ifdef MAGFIX',                                                                                       // v0.11: 그림이 늘어나 보일 때의 손질(위 풀이)
  'uniform vec2 mapN; uniform float pxr;',
  'vec4 cubicW(float v){ vec4 n = vec4(1.0, 2.0, 3.0, 4.0) - v; vec4 s = n * n * n; float x = s.x; float y = s.y - 4.0 * s.x; float z = s.z - 4.0 * s.y + 6.0 * s.x; float w = 6.0 - x - y - z; return vec4(x, y, z, w) * (1.0 / 6.0); }',
  'vec3 texBic(sampler2D t, vec2 uv){ vec2 inv = 1.0 / mapN; uv = uv * mapN - 0.5; vec2 f = fract(uv); uv -= f; vec4 xc = cubicW(f.x), yc = cubicW(f.y); vec4 c = uv.xxyy + vec2(-0.5, 1.5).xyxy; vec4 s = vec4(xc.xz + xc.yw, yc.xz + yc.yw); vec4 o = c + vec4(xc.yw, yc.yw) / s; o *= inv.xxyy;',
  '  vec3 s0 = texture2DLodEXT(t, o.xz, 0.0).rgb, s1 = texture2DLodEXT(t, o.yz, 0.0).rgb, s2 = texture2DLodEXT(t, o.xw, 0.0).rgb, s3 = texture2DLodEXT(t, o.yw, 0.0).rgb; float sx = s.x / (s.x + s.y), sy = s.z / (s.z + s.w); return mix(mix(s3, s2, sx), mix(s1, s0, sx), sy); }',
  'float nz(vec2 uv, float k, float wpx, float ch){ vec4 s = texture2DLodEXT(detail, uv, max(0.0, log2(wpx * k * 256.0))); return mix(s.r, s.g, ch); }',   // 잡음: 화면 한 점에 잡음 한 점이 되는 축소본을 읽는다
  '#endif',
""")
s = rep(s, "  '  vec3 col = texture2D(map, 1.0 - abs(1.0 - abs(vUv)), clamp(eo * 13.0, 0.0, 7.0)).rgb;',              // 밖은 안쪽을 거울처럼 비추되 풀릴수록 번지게(흐리게)\n",
"""  '  vec3 col = texture2D(map, 1.0 - abs(1.0 - abs(vUv)), clamp(eo * 13.0, 0.0, 7.0)).rgb;',              // 밖은 안쪽을 거울처럼 비추되 풀릴수록 번지게(흐리게)
  '  float mg = 0.0;',
  '#ifdef MAGFIX',
  '  vec2 muv = 1.0 - abs(1.0 - abs(vUv));',
  '  float magK = (1.0 - smoothstep(0.28, 0.45, length(fwidth(muv * mapN)) * pxr)) * step(eo, 0.0);',     // 그림이 얼마나 늘어나 보이나: 화면 한 점(CSS)에 그림 몇 점인가 — 0.45 아래부터 서서히, 0.28 아래면 온전히(확대 1.25 ~ 2.1 사이). 지도 안에서만
  '  float wpx = max(length(dFdx(vW)), length(dFdy(vW)));',
  '  if (magK > 0.0) {',
  '    vec2 wn = vec2(nz(vW * 3.1 + 0.27, 3.1, wpx, 0.0) + nz(vW * 9.7 + 0.53, 9.7, wpx, 1.0) * 0.6, nz(vW * 3.7 + 0.71, 3.7, wpx, 1.0) + nz(vW * 8.9 + 0.19, 8.9, wpx, 0.0) * 0.6) - 0.8;',
  '    col = mix(col, texBic(map, muv + wn * (1.2 * magK) / mapN), magK);',                                // 둥글게 메우고, 읽는 자리를 종이 결만큼 흔든다(번짐)
  '    mg = magK * (0.06 * (nz(vW * 4.3 + 0.11, 4.3, wpx, 0.0) - 0.5) + 0.045 * (nz(vW * 11.7 + 0.71, 11.7, wpx, 1.0) - 0.5));',   // 고운 종이 결
  '  }',
  '#endif',
""")
s = rep(s, "  '  col *= 0.955 + 0.09 * dn + nearK * 0.10 * (dn2 - 0.5);',\n", "  '  col *= 0.955 + 0.09 * dn + nearK * 0.10 * (dn2 - 0.5) + mg;',\n")
s = rep(s, "fogColor: { value: new THREE.Color(FOGC) }, fogNear: { value: 60 }, fogFar: { value: 200 }, gridK: { value: 1 }, tint: { value: new THREE.Vector3(1, 1, 1) }, edge: { value: new THREE.Vector3(MAP3D.WX, MAP3D.WZ, APRON) } },\n    vertexShader: TERRAIN_VS, fragmentShader: TERRAIN_FS, extensions: { derivatives: true }\n  });\n",
           "fogColor: { value: new THREE.Color(FOGC) }, fogNear: { value: 60 }, fogFar: { value: 200 }, gridK: { value: 1 }, tint: { value: new THREE.Vector3(1, 1, 1) }, edge: { value: new THREE.Vector3(MAP3D.WX, MAP3D.WZ, APRON) },\n"
           "      mapN: { value: new THREE.Vector2(1, 1) }, pxr: { value: DPR || 1 } },\n"
           "    vertexShader: TERRAIN_VS, fragmentShader: TERRAIN_FS, extensions: { derivatives: true, shaderTextureLOD: true }\n  });\n"
           "  R3.magfix = !!(renderer.capabilities.isWebGL2 || renderer.extensions.has('EXT_shader_texture_lod'));      // v0.11: 확대했을 때의 손질을 켤 수 있는 기기인가\n"
           "  if (R3.magfix) R3.tmat.defines = { MAGFIX: 1 };\n")
s = rep(s, "  R3.renderer.setPixelRatio(DPR); R3.renderer.setSize(CW, CH, false);", "  R3.renderer.setPixelRatio(DPR); R3.renderer.setSize(CW, CH, false); if (R3.tmat && R3.tmat.uniforms.pxr) R3.tmat.uniforms.pxr.value = DPR;")
s = rep(s, "    R3.tmat.uniforms.map.value = t;\n", "    R3.tmat.uniforms.map.value = t; R3.tmat.uniforms.mapN.value.set(im.width, im.height);\n")
io.open(p, 'w', encoding='utf-8').write(s)

# 도움말
p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "황하 하류는 후한 때의 물길을 따릅니다.</p>' +\n",
           "황하 하류는 후한 때의 물길을 따릅니다. 바탕 그림은 지도 전체가 한 장이라, 가장 크게 당기면 붓자국이 먹이 번진 듯 부드럽게 보입니다.</p>' +\n")
io.open(p, 'w', encoding='utf-8').write(s)
print('p5 ok')
