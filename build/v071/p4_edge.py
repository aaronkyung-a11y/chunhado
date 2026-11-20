# v0.8 지도 가장자리 (2차안 — 1차안은 지도 '안쪽'을 흐리게 해서 끝 칸의 지형이 안 보였다. 버림)
#  · 지도 안은 그대로. 지도 '밖' APRON 만큼은 안쪽 땅을 거울처럼 비춰 이어 그리고(높이도), 먹이 종이로 스며들 듯 풀어 낸다
#  · 칸 줄·이동 범위는 지도 끝에서 멈춘다. 숲은 밖으로 조금 이어지다 성기고 옅어진다
#  · 지도 끝이 화면 안으로 들어오는 한도를 확대·아래 창 높이에 맞춘다(가려지지 않은 영역의 1/5까지) → 빈 종이만 보이는 일이 없다
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:90])
    return s.replace(a, b)
p = 'src/ui3d.js'; s = io.open(p, encoding='utf-8').read()

# 1) 지도 밖의 거리·높이
s = rep(s, """function hexPos(c, r) { var p = hexCenter(c, r); return [p[0], groundY(p[0], p[1]), p[1]]; }
""", """function hexPos(c, r) { var p = hexCenter(c, r); return [p[0], groundY(p[0], p[1]), p[1]]; }
/* 지도 밖: 그림이 뚝 끊기지 않게, 끝에서 APRON 만큼은 안쪽 땅을 거울처럼 비춰 이어 그리고 종이로 풀어 낸다(칸·부대는 없다. 지도 단위 — 한 칸의 폭이 약 1.7) */
var APRON = 13;
function outDist(x, z) { var dx = Math.max(-x, x - MAP3D.WX, 0), dz = Math.max(-z, z - MAP3D.WZ, 0); return Math.sqrt(dx * dx + dz * dz); }
function apronY(x, z) {
  var od = outDist(x, z); if (od <= 0) return groundY(x, z);
  var mx = x < 0 ? -x : x > MAP3D.WX ? 2 * MAP3D.WX - x : x, mz = z < 0 ? -z : z > MAP3D.WZ ? 2 * MAP3D.WZ - z : z;
  var t = clamp(od / APRON, 0, 1), base = MAP3D.hmin - 0.05;
  return base + (groundY(mx, mz) - base) * (1 - t * t * (3 - 2 * t));     // 바깥으로 갈수록 바닥(여백의 높이)으로 잦아든다
}
""")

# 2) 카메라 한도
s = rep(s, """function clampCam() {
  cam.z = clamp(cam.z, Z_MIN, Z_MAX);
  cam.x = clamp(cam.x, 6, MAP3D.WX - 6); cam.y = clamp(cam.y, 8, MAP3D.WZ - 3);
  UI.render = true;
}""", """/* 지도 끝이 화면 안으로 들어오는 한도 — 가려지지 않은 지도 영역의 1/5(적어도 손가락 한 마디)까지. 확대와 아래 창 높이에 따라 달라진다 */
function camLimits() {
  if (CW < 60 || CH < 60) return { x0: 6, x1: MAP3D.WX - 6, y0: 8, y1: MAP3D.WZ - 3 };
  var D = camDist(), p = camPitch(), sa = safeArea(), h = Math.max(1, sa.bottom - sa.top);
  var hw = D * K3 * (CW / CH) / 2, mx = hw * (1 - 2 * clamp(70 / CW, 0.2, 0.45));     // 바라보는 깊이에서 화면 반폭(지도 단위)
  var iy = Math.max(0.2 * h, Math.min(60, 0.45 * h));
  function north(y) { var a = Math.atan((0.5 - y / CH) * K3); return D * (Math.sin(p) / Math.tan(Math.max(0.08, p - a)) - Math.cos(p)); }   // 화면의 y 줄에 놓인 땅이 바라보는 점보다 얼마나 북쪽인가
  return { x0: mx, x1: MAP3D.WX - mx, y0: north(sa.top + iy), y1: MAP3D.WZ + north(sa.bottom - iy) };
}
function clampCam() {
  cam.z = clamp(cam.z, Z_MIN, Z_MAX);
  var L = camLimits();
  cam.x = L.x0 > L.x1 ? MAP3D.WX / 2 : clamp(cam.x, L.x0, L.x1);
  cam.y = L.y0 > L.y1 ? (L.y0 + L.y1) / 2 : clamp(cam.y, L.y0, L.y1);
  UI.render = true;
}
/* 아래 창 높이가 바뀌어 한도가 달라졌으면 부드럽게 제자리로(끌거나 다른 움직임이 있을 때는 건드리지 않는다) */
var _settleT = 0;
function settleCam() {
  if (!R3 || !R3.ready || UI.anims.length || ptList().length) return;
  var x0 = cam.x, y0 = cam.y; clampCam(); var x1 = cam.x, y1 = cam.y;
  if (Math.abs(x1 - x0) + Math.abs(y1 - y0) < 0.02) return;
  cam.x = x0; cam.y = y0;
  anim(240, function (t) { var e = t * (2 - t); cam.x = x0 + (x1 - x0) * e; cam.y = y0 + (y1 - y0) * e; UI.render = true; });
}
function settleSoon() { clearTimeout(_settleT); _settleT = setTimeout(settleCam, 90); }""")

# 3) 그림
s = rep(s, """  'uniform vec2 hexN; uniform vec3 fogColor; uniform float fogNear; uniform float fogFar; uniform float gridK; uniform vec3 tint;',""",
"""  'uniform vec2 hexN; uniform vec3 fogColor; uniform float fogNear; uniform float fogFar; uniform float gridK; uniform vec3 tint; uniform vec3 edge;',""")
s = rep(s, """  '  vec3 col = texture2D(map, vUv).rgb;',""",
"""  '  float od = length(max(max(-vW, vW - edge.xy), 0.0)), inMap = 1.0 - smoothstep(0.0, 0.05, od), et = od / edge.z;',   // 지도 밖으로 나간 거리(안이면 0)
  '  float ew = (texture2D(detail, vW * 0.011 + 0.13).r - 0.5) * 2.0 + (texture2D(detail, vW * 0.047 + 0.61).g - 0.5) * 0.9;',
  '  float eo = et + ew * min(1.0, et * 3.0);',                                                           // 그림이 얼마나 풀렸나 — 잡음 때문에 곳에 따라 더 멀리까지 이어진다(끝이 들쭉날쭉)
  '  vec3 col = texture2D(map, 1.0 - abs(1.0 - abs(vUv)), clamp(eo * 13.0, 0.0, 7.0)).rgb;',              // 밖은 안쪽을 거울처럼 비추되 풀릴수록 번지게(흐리게)""")
s = rep(s, """  '  float gk = gridK * pass * (1.0 - smoothstep(0.03, 0.10, aa));',""",
"""  '  float gk = gridK * pass * inMap * (1.0 - smoothstep(0.03, 0.10, aa));',                           // 칸 줄은 지도 끝에서 멈춘다""")
s = rep(s, """    } else {',                                                // 이동·공격 범위: 칸 가장자리를 짙게""",
"""    } else if (inMap > 0.5) {',                               // 이동·공격 범위: 칸 가장자리를 짙게""")
s = rep(s, """  '  col = mix(col, fogColor, smoothstep(fogNear, fogFar, vD));',""",
"""  '  col = mix(fogColor, col, (1.0 - smoothstep(0.0, 0.70, eo)) * (1.0 - smoothstep(0.72, 1.0, et)));',  // 지도 밖: 먹이 종이로 스며들 듯 풀린다
  '  col = mix(col, fogColor, smoothstep(fogNear, fogFar, vD));',""")
s = rep(s, """fogColor: { value: new THREE.Color(FOGC) }, fogNear: { value: 60 }, fogFar: { value: 200 }, gridK: { value: 1 }, tint: { value: new THREE.Vector3(1, 1, 1) } },""",
"""fogColor: { value: new THREE.Color(FOGC) }, fogNear: { value: 60 }, fogFar: { value: 200 }, gridK: { value: 1 }, tint: { value: new THREE.Vector3(1, 1, 1) }, edge: { value: new THREE.Vector3(MAP3D.WX, MAP3D.WZ, APRON) } },""")

# 4) 땅: 격자를 지도 밖 APRON 까지 넓힌다
s = rep(s, """  var GX = MAP3D.GX, GZ = MAP3D.GZ, NX = 8, NZ = 8, sx = MAP3D.WX / (GX - 1), sz = MAP3D.WZ / (GZ - 1);
  for (var cz = 0; cz < NZ; cz++) for (var cx = 0; cx < NX; cx++) {
    var x0 = Math.floor(cx * (GX - 1) / NX), x1 = Math.floor((cx + 1) * (GX - 1) / NX), z0 = Math.floor(cz * (GZ - 1) / NZ), z1 = Math.floor((cz + 1) * (GZ - 1) / NZ);""",
"""  var GX = MAP3D.GX, GZ = MAP3D.GZ, NX = 8, NZ = 8, sx = MAP3D.WX / (GX - 1), sz = MAP3D.WZ / (GZ - 1);
  var ax = Math.ceil(APRON / sx), az = Math.ceil(APRON / sz), X0 = -ax, XN = GX - 1 + 2 * ax, Z0 = -az, ZN = GZ - 1 + 2 * az;   // 지도 밖 띠까지
  for (var cz = 0; cz < NZ; cz++) for (var cx = 0; cx < NX; cx++) {
    var x0 = X0 + Math.floor(cx * XN / NX), x1 = X0 + Math.floor((cx + 1) * XN / NX), z0 = Z0 + Math.floor(cz * ZN / NZ), z1 = Z0 + Math.floor((cz + 1) * ZN / NZ);""")
s = rep(s, """      pos[p++] = gx * sx; pos[p++] = HMAP[gz * GX + gx]; pos[p++] = gz * sz;""",
"""      pos[p++] = gx * sx; pos[p++] = (gx >= 0 && gx < GX && gz >= 0 && gz < GZ) ? HMAP[gz * GX + gx] : apronY(gx * sx, gz * sz); pos[p++] = gz * sz;""")

# 5) 숲: 지도 밖으로 조금 이어지다 성기고 옅어진다
s = rep(s, """  var NB = 8, buckets = [], i, j, k;
  for (i = 0; i < NB * NB; i++) buckets.push([]);""", """  var NB = 8, buckets = [], outer = [[], [], []], TW = 3.6, i, j, k;
  for (i = 0; i < NB * NB; i++) buckets.push([]);""")
s = rep(s, """      buckets[Math.min(NB - 1, Math.floor(z / MAP3D.WZ * NB)) * NB + Math.min(NB - 1, Math.floor(x / MAP3D.WX * NB))].push([x, groundY(x, z), z, 0.75 + 0.6 * hash2(k, j * 7 + 3), hash2(k, j * 7 + 4)]);
    }""", """      var sc = 0.75 + 0.6 * hash2(k, j * 7 + 3), rt = hash2(k, j * 7 + 4);
      buckets[Math.min(NB - 1, Math.floor(z / MAP3D.WZ * NB)) * NB + Math.min(NB - 1, Math.floor(x / MAP3D.WX * NB))].push([x, groundY(x, z), z, sc, rt]);
      var xs = x < TW ? -x : MAP3D.WX - x < TW ? 2 * MAP3D.WX - x : null, zs = z < TW ? -z : MAP3D.WZ - z < TW ? 2 * MAP3D.WZ - z : null, mir = [];
      if (xs !== null) mir.push([xs, z]); if (zs !== null) mir.push([x, zs]); if (xs !== null && zs !== null) mir.push([xs, zs]);
      for (var mi = 0; mi < mir.length; mi++) {
        var X = mir[mi][0], Z = mir[mi][1], tt = outDist(X, Z) / TW;
        if (tt >= 1 || hash2(k, j * 7 + 5 + mi) < 0.25 + tt * 0.8) continue;
        outer[Math.min(2, Math.floor(tt * 3))].push([X, apronY(X, Z), Z, sc * (1 - 0.45 * tt), rt]);
      }
    }""")
s = rep(s, """    mesh.instanceMatrix.needsUpdate = true; mesh.matrixAutoUpdate = false; R3.scene.add(mesh); R3.trees.push(mesh);
  }
}""", """    mesh.instanceMatrix.needsUpdate = true; mesh.matrixAutoUpdate = false; R3.scene.add(mesh); R3.trees.push(mesh);
  }
  var paper = new THREE.Color(FOGC);
  for (i = 0; i < 3; i++) {                               // 지도 밖의 나무: 멀수록 종이색에 가깝게(세 단계)
    var O = outer[i]; if (!O.length) continue;
    var f = 0.3 + 0.25 * i, og = cone.clone(), oc = new Float32Array(cols.length);
    for (j = 0; j < cols.length; j += 3) { oc[j] = cols[j] * (1 - f) + paper.r * f; oc[j + 1] = cols[j + 1] * (1 - f) + paper.g * f; oc[j + 2] = cols[j + 2] * (1 - f) + paper.b * f; }
    og.setAttribute('color', new THREE.BufferAttribute(oc, 3));
    var om = new THREE.InstancedMesh(og, mat, O.length);
    for (j = 0; j < O.length; j++) {
      var oe = O[j]; q.setFromAxisAngle(up, oe[4] * 6.283); s.set(oe[3], oe[3] * (0.85 + 0.4 * oe[4]), oe[3]); v.set(oe[0], oe[1] - 0.03, oe[2]);
      m4.compose(v, q, s); om.setMatrixAt(j, m4);
      var og2 = 1 + (0.72 + 0.5 * oe[4] - 1) * (1 - f); col.setRGB(og2, og2, og2); om.setColorAt(j, col);
    }
    om.instanceMatrix.needsUpdate = true; om.matrixAutoUpdate = false; om.frustumCulled = false; R3.scene.add(om); R3.trees.push(om);
  }
}""")

# 6) 아래 창 높이가 바뀌면 한도도 바뀐다 → 살며시 제자리로
s = rep(s, """function initInput() {
""", """function initInput() {
  if (typeof ResizeObserver === 'function') { var ro = new ResizeObserver(settleSoon); ['sheet', 'bar', 'play', 'hud'].forEach(function (id) { if ($(id)) ro.observe($(id)); }); }
""")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
