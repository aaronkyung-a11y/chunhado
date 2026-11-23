/* ===== 천하도 — 3D 지도(three.js)·입력·연출·소리 ===== */
var SQ3 = Math.sqrt(3);
var FONT_D = '"Noto Serif KR","Nanum Myeongjo","AppleMyungjo","Batang",serif';
var FONT_B = '"Apple SD Gothic Neo","Noto Sans KR","Malgun Gothic",system-ui,sans-serif';
var FOV = 32, K3 = 2 * Math.tan(FOV / 2 * Math.PI / 180), Z_MIN = 0.14, Z_MAX = 2.3, FOGC = 0xefe9db;
var INK = '#1b1a18', PAPER = '#f4efe3', SEAL = '#b5332a', NEUTRAL = '#8d877b';
var cv, DPR = 1, CW = 0, CH = 0;
var cam = { x: 200, y: 160, z: 1 };                 // x·y = 바라보는 지면(월드 x·z), z = 확대
var UI = { sel: null, rc: null, atk: null, target: null, march: null, busy: false, anims: [], floats: [], dirty: true, render: true, sound: true, music: true, hide: -1, play: null, pspeed: 1, pct: false };      // pct(v0.18): 확률을 숫자로 보는가 — 기본은 말
var POR_URL = {}, POR_IMG = {}, SCENE_URL = {}, HMAP = null, R3 = null, TEX = {}, TEXF = {};

function $(id) { return document.getElementById(id); }
function fmt(n) { return Math.round(n).toLocaleString('en-US'); }
function requestDraw() { UI.dirty = true; }
function b64blob(b64, type) {
  var bin = atob(b64), n = bin.length, a = new Uint8Array(n);
  for (var i = 0; i < n; i++) a[i] = bin.charCodeAt(i);
  return new Blob([a], { type: type });
}
function rgbOf(hex) { var v = parseInt(hex.slice(1), 16); return [(v >> 16) & 255, (v >> 8) & 255, v & 255]; }

/* ---------- 좌표·높이 ---------- */
function hexCenter(c, r) { return [SQ3 * (c + 0.5 * (r & 1)) + SQ3 / 2, 1.5 * r + 1]; }
function worldToHex(wx, wz) {
  var r0 = Math.round((wz - 1) / 1.5), best = null, bd = 1e9;
  for (var r = r0 - 1; r <= r0 + 1; r++) {
    if (r < 0 || r >= H) continue;
    var c0 = Math.round((wx - SQ3 / 2) / SQ3 - 0.5 * (r & 1));
    for (var c = c0 - 1; c <= c0 + 1; c++) {
      if (c < 0 || c >= W) continue;
      var p = hexCenter(c, r), d = (p[0] - wx) * (p[0] - wx) + (p[1] - wz) * (p[1] - wz);
      if (d < bd) { bd = d; best = [c, r]; }
    }
  }
  return best;
}
function decodeHeights() {
  var bin = atob(MAP3D.hm), n = MAP3D.GX * MAP3D.GZ, k = (MAP3D.hmax - MAP3D.hmin) / 65535;
  HMAP = new Float32Array(n);
  for (var i = 0; i < n; i++) HMAP[i] = MAP3D.hmin + (bin.charCodeAt(2 * i) | (bin.charCodeAt(2 * i + 1) << 8)) * k;
}
function groundY(x, z) {
  var GX = MAP3D.GX, gx = clamp(x / MAP3D.WX * (GX - 1), 0, GX - 1.001), gz = clamp(z / MAP3D.WZ * (MAP3D.GZ - 1), 0, MAP3D.GZ - 1.001);
  var ix = Math.floor(gx), iz = Math.floor(gz), fx = gx - ix, fz = gz - iz, i = iz * GX + ix;
  return (HMAP[i] * (1 - fx) + HMAP[i + 1] * fx) * (1 - fz) + (HMAP[i + GX] * (1 - fx) + HMAP[i + GX + 1] * fx) * fz;
}
function hexPos(c, r) { var p = hexCenter(c, r); return [p[0], groundY(p[0], p[1]), p[1]]; }
/* 지도 밖: 그림이 뚝 끊기지 않게, 끝에서 APRON 만큼은 안쪽 땅을 거울처럼 비춰 이어 그리고 종이로 풀어 낸다(칸·부대는 없다. 지도 단위 — 한 칸의 폭이 약 1.7) */
var APRON = 13;
function outDist(x, z) { var dx = Math.max(-x, x - MAP3D.WX, 0), dz = Math.max(-z, z - MAP3D.WZ, 0); return Math.sqrt(dx * dx + dz * dz); }
function apronY(x, z) {
  var od = outDist(x, z); if (od <= 0) return groundY(x, z);
  var mx = x < 0 ? -x : x > MAP3D.WX ? 2 * MAP3D.WX - x : x, mz = z < 0 ? -z : z > MAP3D.WZ ? 2 * MAP3D.WZ - z : z;
  var t = clamp(od / APRON, 0, 1), base = MAP3D.hmin - 0.05;
  return base + (groundY(mx, mz) - base) * (1 - t * t * (3 - 2 * t));     // 바깥으로 갈수록 바닥(여백의 높이)으로 잦아든다
}

/* ---------- 카메라 ---------- */
function camDist() { return 62 / cam.z; }
function pitchAt(z) { var t = clamp(Math.log(z / Z_MIN) / Math.log(Z_MAX / Z_MIN), 0, 1); return (68 - 27 * t) * Math.PI / 180; }
function camPitch() { var t = clamp(Math.log(cam.z / Z_MIN) / Math.log(Z_MAX / Z_MIN), 0, 1); return (68 - 27 * t) * Math.PI / 180; }
/* 지도 끝이 화면 안으로 들어오는 한도 — 가려지지 않은 지도 영역의 1/5(적어도 손가락 한 마디)까지. 확대와 아래 창 높이에 따라 달라진다 */
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
function settleSoon() { clearTimeout(_settleT); _settleT = setTimeout(settleCam, 90); }
function applyCam() {
  var D = camDist(), p = camPitch(), ty = groundY(cam.x, cam.y), c = R3.cam;
  c.position.set(cam.x, ty + D * Math.sin(p), cam.y + D * Math.cos(p));
  c.lookAt(cam.x, ty, cam.y);
  c.near = Math.max(0.5, D * 0.08); c.far = D * 5 + 120; c.updateProjectionMatrix(); c.updateMatrixWorld();
  var fn = D * 1.15, ff = D * 3.3;
  R3.scene.fog.near = fn; R3.scene.fog.far = ff;
  R3.tmat.uniforms.fogNear.value = fn; R3.tmat.uniforms.fogFar.value = ff;
  if (R3.pitch !== p) { R3.pitch = p; R3.billboard = true; }
}
var _v = null;
function w2s(x, y, z) {
  _v.set(x, y, z).applyMatrix4(R3.cam.matrixWorldInverse);
  var depth = -_v.z; if (depth <= 0.1) return null;
  _v.applyMatrix4(R3.cam.projectionMatrix);
  return [(_v.x * 0.5 + 0.5) * CW, (0.5 - _v.y * 0.5) * CH, depth];
}
function screenRay(sx, sy) {
  var o = R3.cam.position, d = new THREE.Vector3(sx / CW * 2 - 1, 1 - sy / CH * 2, 0.5).unproject(R3.cam).sub(o).normalize();
  return { o: o, d: d };
}
function planeHit(sx, sy, y0) {
  var ry = screenRay(sx, sy); if (ry.d.y > -0.02) return null;
  var t = (y0 - ry.o.y) / ry.d.y; return [ry.o.x + ry.d.x * t, ry.o.z + ry.d.z * t];
}
function pickGround(sx, sy) {
  var ry = screenRay(sx, sy), o = ry.o, d = ry.d; if (d.y > -0.02) return null;
  var t = Math.max(0, (o.y - MAP3D.hmax - 0.5) / -d.y), step = 0.35, prev = t;
  for (var i = 0; i < 900; i++) {
    var x = o.x + d.x * t, y = o.y + d.y * t, z = o.z + d.z * t;
    if (y <= groundY(x, z)) {
      var a = prev, b = t;
      for (var j = 0; j < 12; j++) { var m = (a + b) / 2; if (o.y + d.y * m <= groundY(o.x + d.x * m, o.z + d.z * m)) b = m; else a = m; }
      return [o.x + d.x * b, o.z + d.z * b];
    }
    if (y < MAP3D.hmin - 1) break;
    prev = t; t += step;
  }
  return null;
}
function pxPerUnit(depth) { return CH / (K3 * depth); }
function resize() {
  if (!R3) return;
  DPR = Math.min(window.devicePixelRatio || 1, 2);
  CW = cv.clientWidth; CH = cv.clientHeight;
  R3.renderer.setPixelRatio(DPR); R3.renderer.setSize(CW, CH, false); if (R3.tmat && R3.tmat.uniforms.pxr) R3.tmat.uniforms.pxr.value = DPR;
  R3.cam.aspect = CW / Math.max(1, CH);
  R3.labelK = 0; clampCam(); requestDraw();
}
/* 상단 HUD와 아래 창(STATUS 창·버튼 줄·재생 줄)에 가려지지 않는 지도 영역 */
function safeArea() {
  var hud = $('hud'), top = (hud ? hud.offsetHeight : 64) + 6, cover = 0, sh = $('sheet'), bar = $('bar'), pl = $('play');
  var md = $('modal'), dl = md && md.classList.contains('see') ? md.querySelector('.dlg') : null;
  if (dl && dl.offsetHeight) cover = dl.offsetHeight;                         // 지도를 보여 주는 창(건설 자리 고르기)
  else if (pl && pl.offsetHeight) cover = pl.offsetHeight;
  else cover = (bar ? bar.offsetHeight : 0) + (sh ? sh.offsetHeight : 0);
  var bottom = Math.max(top + 90, CH - cover - 6);
  return { top: top, bottom: bottom, fy: (top + bottom) / 2 / Math.max(1, CH) };
}
var camTok = 0;
function jumpTo(c, r, z, fy, dur) {
  var p = hexCenter(c, r), z1 = clamp(z || cam.z, Z_MIN, Z_MAX), x0 = cam.x, y0 = cam.y, z0 = cam.z, tok = camTok;
  var D = 62 / z1, pt = (68 - 27 * clamp(Math.log(z1 / Z_MIN) / Math.log(Z_MAX / Z_MIN), 0, 1)) * Math.PI / 180;
  if (!fy) fy = safeArea().fy;
  var ty = p[1] + (0.5 - fy) * D * K3 / Math.sin(pt);
  anim(dur || 260, function (t) { if (tok !== camTok) return; var e = t * (2 - t); cam.x = x0 + (p[0] - x0) * e; cam.y = y0 + (ty - y0) * e; cam.z = z0 + (z1 - z0) * e; clampCam(); });
}
function onScreen(c, r, pad) {
  var sa = safeArea(), p = hexPos(c, r), s = w2s(p[0], p[1], p[2]); pad = pad || 0;
  return !!s && s[0] >= 44 + pad && s[0] <= CW - 44 - pad && s[1] >= sa.top + 44 + pad && s[1] <= sa.bottom - 14 - pad;
}
function ensureVisible(c, r) { if (!onScreen(c, r, 0)) jumpTo(c, r, Math.max(cam.z, 0.8)); }
function flyTo(wx, wz, z, fy, dur) {
  var z1 = clamp(z || cam.z, Z_MIN, Z_MAX), x0 = cam.x, y0 = cam.y, z0 = cam.z, D = 62 / z1, pt = pitchAt(z1), tok = ++camTok;
  if (!fy) fy = safeArea().fy;
  var ty = wz + (0.5 - fy) * D * K3 / Math.sin(pt);
  anim(dur || 260, function (t) { if (tok !== camTok) return; var e = t * (2 - t); cam.x = x0 + (wx - x0) * e; cam.y = y0 + (ty - y0) * e; cam.z = z0 + (z1 - z0) * e; clampCam(); });
}
/* 여러 칸이 한눈에 들어오게: 화면의 [top, bottom] 사이에 모두 들어오는 가장 가까운 거리로 옮긴다(zCap 보다 더 다가가지는 않는다) */
function frameHexes(list, top, bottom, zCap) {
  var x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9, i;
  for (i = 0; i < list.length; i++) { var p = hexCenter(list[i][0], list[i][1]); x0 = Math.min(x0, p[0] - 1.05); x1 = Math.max(x1, p[0] + 1.05); y0 = Math.min(y0, p[1] - 1.5); y1 = Math.max(y1, p[1] + 1.25); }
  var h = Math.max(80, bottom - top), z = Z_MAX;
  for (i = 0; i < 70; i++) {                                                  // 다 들어오는 가장 가까운 거리
    var ppu = CH / (K3 * 62 / z);
    if ((x1 - x0) * ppu <= CW - 16 && (y1 - y0) * ppu * Math.sin(pitchAt(z)) <= h - 8) break;
    z *= 0.96;
  }
  flyTo((x0 + x1) / 2, (y0 + y1) / 2, clamp(Math.min(z, zCap || Z_MAX), Z_MIN, Z_MAX), (top + bottom) / 2 / Math.max(1, CH), 300);
}

/* ---------- 장면 만들기 ---------- */
var TERRAIN_VS = 'varying vec2 vUv; varying vec2 vW; varying float vD;\nvoid main(){ vUv = uv; vW = position.xz; vec4 mv = modelViewMatrix * vec4(position, 1.0); vD = -mv.z; gl_Position = projectionMatrix * mv; }';
var TERRAIN_FS = [
  'uniform sampler2D map; uniform sampler2D detail; uniform sampler2D hexOv; uniform sampler2D hexSt;',
  'uniform vec2 hexN; uniform vec3 fogColor; uniform float fogNear; uniform float fogFar; uniform float gridK; uniform vec3 tint; uniform vec3 edge;',
  'varying vec2 vUv; varying vec2 vW; varying float vD;',
  'const float SQ3 = 1.7320508;',
  '#ifdef MAGFIX',                                                                                       // v0.11: 그림이 늘어나 보일 때의 손질(위 풀이)
  'uniform vec2 mapN; uniform float pxr;',
  'vec4 cubicW(float v){ vec4 n = vec4(1.0, 2.0, 3.0, 4.0) - v; vec4 s = n * n * n; float x = s.x; float y = s.y - 4.0 * s.x; float z = s.z - 4.0 * s.y + 6.0 * s.x; float w = 6.0 - x - y - z; return vec4(x, y, z, w) * (1.0 / 6.0); }',
  'vec3 texBic(sampler2D t, vec2 uv){ vec2 inv = 1.0 / mapN; uv = uv * mapN - 0.5; vec2 f = fract(uv); uv -= f; vec4 xc = cubicW(f.x), yc = cubicW(f.y); vec4 c = uv.xxyy + vec2(-0.5, 1.5).xyxy; vec4 s = vec4(xc.xz + xc.yw, yc.xz + yc.yw); vec4 o = c + vec4(xc.yw, yc.yw) / s; o *= inv.xxyy;',
  '  vec3 s0 = texture2DLodEXT(t, o.xz, 0.0).rgb, s1 = texture2DLodEXT(t, o.yz, 0.0).rgb, s2 = texture2DLodEXT(t, o.xw, 0.0).rgb, s3 = texture2DLodEXT(t, o.yw, 0.0).rgb; float sx = s.x / (s.x + s.y), sy = s.z / (s.z + s.w); return mix(mix(s3, s2, sx), mix(s1, s0, sx), sy); }',
  'float nz(vec2 uv, float k, float wpx, float ch){ vec4 s = texture2DLodEXT(detail, uv, max(0.0, log2(wpx * k * 256.0))); return mix(s.r, s.g, ch); }',   // 잡음: 화면 한 점에 잡음 한 점이 되는 축소본을 읽는다
  '#endif',
  'void main(){',
  '  float od = length(max(max(-vW, vW - edge.xy), 0.0)), inMap = 1.0 - smoothstep(0.0, 0.05, od), et = od / edge.z;',   // 지도 밖으로 나간 거리(안이면 0)
  '  float ew = (texture2D(detail, vW * 0.011 + 0.13).r - 0.5) * 2.0 + (texture2D(detail, vW * 0.047 + 0.61).g - 0.5) * 0.9;',
  '  float eo = et + ew * min(1.0, et * 3.0);',                                                           // 그림이 얼마나 풀렸나 — 잡음 때문에 곳에 따라 더 멀리까지 이어진다(끝이 들쭉날쭉)
  '  vec3 col = texture2D(map, 1.0 - abs(1.0 - abs(vUv)), clamp(eo * 13.0, 0.0, 7.0)).rgb;',              // 밖은 안쪽을 거울처럼 비추되 풀릴수록 번지게(흐리게)
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
  '  float dn = texture2D(detail, vW * 0.21).r, dn2 = texture2D(detail, vW * 1.17 + 0.37).g;',
  '  float nearK = 1.0 - smoothstep(25.0, 120.0, vD);',
  '  col *= 0.955 + 0.09 * dn + nearK * 0.10 * (dn2 - 0.5) + mg;',
  '  col *= tint;',
  '  vec2 p = vec2(vW.x - SQ3 * 0.5, vW.y - 1.0);',
  '  float rf = p.y / 1.5, qf = p.x / SQ3 - rf * 0.5;',
  '  float xr = floor(qf + 0.5), zr = floor(rf + 0.5), yr = floor(-qf - rf + 0.5);',
  '  float dx = abs(xr - qf), dz = abs(zr - rf), dy = abs(yr + qf + rf);',
  '  if (dx > dy && dx > dz) xr = -yr - zr; else if (dy <= dz) zr = -xr - yr;',
  '  vec2 dd = abs(p - vec2(SQ3 * (xr + zr * 0.5), 1.5 * zr));',
  '  float e = SQ3 * 0.5 - max(dd.x, dd.x * 0.5 + dd.y * 0.8660254);',
  '  vec2 huv = (vec2(xr + (zr - mod(zr, 2.0)) * 0.5, zr) + 0.5) / hexN;',
  '  vec4 ov = texture2D(hexOv, huv); float pass = texture2D(hexSt, huv).r;',
  '  float aa = fwidth(e) + 0.0006;',
  '  float line = 1.0 - smoothstep(0.0, aa * 1.5, e - 0.008);',
  '  float gk = gridK * pass * inMap * (1.0 - smoothstep(0.03, 0.10, aa));',                           // 칸 줄은 지도 끝에서 멈춘다
  '  col = mix(col, vec3(0.105, 0.10, 0.094), line * gk * 0.21);',
  '  if (ov.a > 0.004) {',
  '    if (ov.a < 0.30) {',                                      // 담채: 세력권·성역. 칸 테두리 없이 번지듯
  '      col = mix(col, col * mix(vec3(1.0), ov.rgb, 0.85), ov.a * 2.6);',
  '    } else if (inMap > 0.5) {',                               // 이동·공격 범위: 칸 가장자리를 짙게
  '      float edge = 1.0 - smoothstep(0.03, 0.06 + aa * 2.0, e);',
  '      col = mix(col, ov.rgb, ov.a * (0.34 + 0.66 * edge));',
  '    }',
  '  }',
  '  col = mix(fogColor, col, (1.0 - smoothstep(0.0, 0.70, eo)) * (1.0 - smoothstep(0.72, 1.0, et)));',  // 지도 밖: 먹이 종이로 스며들 듯 풀린다
  '  col = mix(col, fogColor, smoothstep(fogNear, fogFar, vD));',
  '  gl_FragColor = vec4(col, 1.0);',
  '}'].join('\n');

function noiseTexture() {
  var n = 256, c = document.createElement('canvas'); c.width = c.height = n;
  var x = c.getContext('2d'), im = x.createImageData(n, n), d = im.data, s = 12345;
  function rnd() { s = (s * 1664525 + 1013904223) | 0; return ((s >>> 8) & 0xffff) / 65535; }
  function layer(cell) {                             // 이음매 없는 값 잡음
    var g = n / cell, a = new Float32Array(g * g), out = new Float32Array(n * n), i, j;
    for (i = 0; i < g * g; i++) a[i] = rnd();
    for (j = 0; j < n; j++) for (i = 0; i < n; i++) {
      var fx = i / cell, fy = j / cell, x0 = Math.floor(fx), y0 = Math.floor(fy), tx = fx - x0, ty = fy - y0;
      tx = tx * tx * (3 - 2 * tx); ty = ty * ty * (3 - 2 * ty);
      var x1 = (x0 + 1) % g, y1 = (y0 + 1) % g;
      out[j * n + i] = (a[y0 * g + x0] * (1 - tx) + a[y0 * g + x1] * tx) * (1 - ty) + (a[y1 * g + x0] * (1 - tx) + a[y1 * g + x1] * tx) * ty;
    }
    return out;
  }
  var A = [layer(32), layer(16), layer(8), layer(4)], B = [layer(16), layer(8), layer(4), layer(2)];
  for (var k = 0; k < n * n; k++) {
    d[k * 4] = 255 * (A[0][k] * 0.45 + A[1][k] * 0.28 + A[2][k] * 0.17 + A[3][k] * 0.10);
    d[k * 4 + 1] = 255 * (B[0][k] * 0.35 + B[1][k] * 0.30 + B[2][k] * 0.20 + B[3][k] * 0.15);
    d[k * 4 + 2] = 128; d[k * 4 + 3] = 255;
  }
  x.putImageData(im, 0, 0);
  var t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;
}
function init3d() {
  cv = $('map'); decodeHeights(); _v = new THREE.Vector3();
  var renderer = new THREE.WebGLRenderer({ canvas: cv, antialias: true, alpha: false, powerPreference: 'high-performance' });
  renderer.setClearColor(FOGC, 1);
  var scene = new THREE.Scene(); scene.fog = new THREE.Fog(FOGC, 60, 200);
  var camera = new THREE.PerspectiveCamera(FOV, 1, 1, 800);
  R3 = { renderer: renderer, scene: scene, cam: camera, bases: [], units: {}, facs: {}, fires: {}, labelK: 0, pitch: -1, billboard: true, ready: false, loading: 0, labelCache: {} };
  // 헥스 자료 텍스처
  var st = new Uint8Array(NHEX * 4), i;
  for (i = 0; i < NHEX; i++) { var t = TCH[i]; st[i * 4] = (t === 120 || t === 115 || t === 109) ? 0 : 255; st[i * 4 + 3] = 255; }
  R3.stTex = new THREE.DataTexture(st, W, H); R3.stTex.magFilter = R3.stTex.minFilter = THREE.NearestFilter; R3.stTex.needsUpdate = true;
  R3.ovData = new Uint8Array(NHEX * 4);
  R3.ovTex = new THREE.DataTexture(R3.ovData, W, H); R3.ovTex.magFilter = R3.ovTex.minFilter = THREE.NearestFilter; R3.ovTex.needsUpdate = true;
  var blank = new THREE.DataTexture(new Uint8Array([120, 130, 100, 255]), 1, 1); blank.needsUpdate = true;
  R3.tmat = new THREE.ShaderMaterial({
    uniforms: { map: { value: blank }, detail: { value: noiseTexture() }, hexOv: { value: R3.ovTex }, hexSt: { value: R3.stTex }, hexN: { value: new THREE.Vector2(W, H) },
      fogColor: { value: new THREE.Color(FOGC) }, fogNear: { value: 60 }, fogFar: { value: 200 }, gridK: { value: 1 }, tint: { value: new THREE.Vector3(1, 1, 1) }, edge: { value: new THREE.Vector3(MAP3D.WX, MAP3D.WZ, APRON) },
      mapN: { value: new THREE.Vector2(1, 1) }, pxr: { value: DPR || 1 } },
    vertexShader: TERRAIN_VS, fragmentShader: TERRAIN_FS, extensions: { derivatives: true, shaderTextureLOD: true }
  });
  R3.magfix = !!(renderer.capabilities.isWebGL2 || renderer.extensions.has('EXT_shader_texture_lod'));      // v0.11: 확대했을 때의 손질을 켤 수 있는 기기인가
  if (R3.magfix) R3.tmat.defines = { MAGFIX: 1 };
  buildTerrain(); buildRoads(); buildTrees(); buildWalls();
  R3.objs = new THREE.Group(); scene.add(R3.objs);
  R3.flame = flameTexture();
}
function buildTerrain() {
  var GX = MAP3D.GX, GZ = MAP3D.GZ, NX = 8, NZ = 8, sx = MAP3D.WX / (GX - 1), sz = MAP3D.WZ / (GZ - 1);
  var ax = Math.ceil(APRON / sx), az = Math.ceil(APRON / sz), X0 = -ax, XN = GX - 1 + 2 * ax, Z0 = -az, ZN = GZ - 1 + 2 * az;   // 지도 밖 띠까지
  for (var cz = 0; cz < NZ; cz++) for (var cx = 0; cx < NX; cx++) {
    var x0 = X0 + Math.floor(cx * XN / NX), x1 = X0 + Math.floor((cx + 1) * XN / NX), z0 = Z0 + Math.floor(cz * ZN / NZ), z1 = Z0 + Math.floor((cz + 1) * ZN / NZ);
    var nx = x1 - x0 + 1, nz = z1 - z0 + 1, pos = new Float32Array(nx * nz * 3), uv = new Float32Array(nx * nz * 2), idx = new Uint16Array((nx - 1) * (nz - 1) * 6), p = 0, q = 0, k = 0, i, j;
    for (j = 0; j < nz; j++) for (i = 0; i < nx; i++) {
      var gx = x0 + i, gz = z0 + j;
      pos[p++] = gx * sx; pos[p++] = (gx >= 0 && gx < GX && gz >= 0 && gz < GZ) ? HMAP[gz * GX + gx] : apronY(gx * sx, gz * sz); pos[p++] = gz * sz;
      uv[q++] = gx / (GX - 1); uv[q++] = gz / (GZ - 1);
    }
    for (j = 0; j < nz - 1; j++) for (i = 0; i < nx - 1; i++) { var a = j * nx + i, b = a + 1, c = a + nx, d = c + 1; idx[k++] = a; idx[k++] = c; idx[k++] = b; idx[k++] = b; idx[k++] = c; idx[k++] = d; }
    var g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('uv', new THREE.BufferAttribute(uv, 2)); g.setIndex(new THREE.BufferAttribute(idx, 1));
    g.computeBoundingSphere();
    var m = new THREE.Mesh(g, R3.tmat); m.matrixAutoUpdate = false; R3.scene.add(m);
  }
  var skirt = new THREE.Mesh(new THREE.PlaneGeometry(MAP3D.WX + 900, MAP3D.WZ + 900), new THREE.MeshBasicMaterial({ color: 0xefe9db }));
  skirt.rotation.x = -Math.PI / 2; skirt.position.set(MAP3D.WX / 2, MAP3D.hmin - 0.08, MAP3D.WZ / 2); R3.scene.add(skirt);
}
function buildRoads() {
  var pos = [], idx = [], n = 0, w = 0.062;
  MAP3D.roads.forEach(function (f) {
    var m = f.length / 2, base = n;
    for (var i = 0; i < m; i++) {
      var x = f[2 * i], z = f[2 * i + 1], a = Math.max(0, i - 1), b = Math.min(m - 1, i + 1);
      var tx = f[2 * b] - f[2 * a], tz = f[2 * b + 1] - f[2 * a + 1], L = Math.sqrt(tx * tx + tz * tz) || 1, px = -tz / L * w, pz = tx / L * w;
      var y = Math.max(groundY(x + px, z + pz), groundY(x - px, z - pz), groundY(x, z)) + 0.03;
      pos.push(x + px, y, z + pz, x - px, y, z - pz); n += 2;
      if (i) idx.push(base + 2 * i - 2, base + 2 * i - 1, base + 2 * i, base + 2 * i - 1, base + 2 * i + 1, base + 2 * i);
    }
  });
  var g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(pos), 3)); g.setIndex(n > 65535 ? new THREE.BufferAttribute(new Uint32Array(idx), 1) : new THREE.BufferAttribute(new Uint16Array(idx), 1));
  var mat = new THREE.MeshBasicMaterial({ color: 0x2b2722, transparent: true, opacity: 0.46, depthWrite: false, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -3, polygonOffsetUnits: -3 });
  var mesh = new THREE.Mesh(g, mat); mesh.frustumCulled = false; mesh.renderOrder = 0; R3.scene.add(mesh);
}
function buildWalls() {                                          // v0.21 관문의 능선(MAPDATA.walls): 막힌 변을 따라 먹선 한 줄, 가운데에 짧은 빗금
  var ws = MAPDATA.walls || []; if (!ws.length) return;
  var pos = [], idx = [], n = 0, w = 0.075;
  function quad(ax, az, bx, bz, hw) {
    var tx = bx - ax, tz = bz - az, L = Math.sqrt(tx * tx + tz * tz) || 1, px = -tz / L * hw, pz = tx / L * hw;
    var ya = Math.max(groundY(ax, az), groundY(ax + px, az + pz), groundY(ax - px, az - pz)) + 0.05, yb = Math.max(groundY(bx, bz), groundY(bx + px, bz + pz), groundY(bx - px, bz - pz)) + 0.05;
    pos.push(ax + px, ya, az + pz, ax - px, ya, az - pz, bx + px, yb, bz + pz, bx - px, yb, bz - pz);
    idx.push(n, n + 1, n + 2, n + 1, n + 3, n + 2); n += 4;
  }
  ws.forEach(function (e, i) {
    var a = hexCenter(e[0], e[1]), b = hexCenter(e[2], e[3]), mx = (a[0] + b[0]) / 2, mz = (a[1] + b[1]) / 2, dx = b[0] - a[0], dz = b[1] - a[1], L = Math.sqrt(dx * dx + dz * dz) || 1;
    var ux = dx / L, uz = dz / L, px = -uz, pz = ux, j = (hash2(e[0] * 7 + e[2], e[1] * 5 + e[3]) - 0.5) * 0.10;
    var cx = mx + ux * j, cz = mz + uz * j;                         // 가운데를 조금 흔들어 꺾인 선으로
    quad(mx + px * 0.5, mz + pz * 0.5, cx, cz, w); quad(cx, cz, mx - px * 0.5, mz - pz * 0.5, w);
    var sgn = (i % 2) ? 1 : -1; quad(cx, cz, cx + ux * 0.24 * sgn + px * 0.10, cz + uz * 0.24 * sgn + pz * 0.10, w * 0.62);      // 빗금
  });
  var g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(pos), 3)); g.setIndex(new THREE.BufferAttribute(new Uint16Array(idx), 1));
  var mat = new THREE.MeshBasicMaterial({ color: 0x1b1a18, transparent: true, opacity: 0.74, depthWrite: false, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -4, polygonOffsetUnits: -4 });
  var mesh = new THREE.Mesh(g, mat); mesh.frustumCulled = false; mesh.renderOrder = 0; R3.scene.add(mesh);
}
function hash2(a, b) { var n = (a * 374761393 + b * 668265263) | 0; n = Math.imul(n ^ (n >>> 13), 1274126177); return ((n ^ (n >>> 16)) >>> 0) / 4294967296; }
function buildTrees() {
  var NB = 8, buckets = [], outer = [[], [], []], TW = 3.6, i, j, k;
  for (i = 0; i < NB * NB; i++) buckets.push([]);
  for (k = 0; k < NHEX; k++) {
    if (TCH[k] !== 102 || RDB[k] || PAT[k]) continue;
    var c = k % W, r = (k - c) / W, p = hexCenter(c, r);
    for (j = 0; j < 4; j++) {
      var a = hash2(k, j * 7 + 1) * 6.283, d = 0.18 + 0.56 * Math.sqrt(hash2(k, j * 7 + 2)), x = p[0] + Math.cos(a) * d, z = p[1] + Math.sin(a) * d;
      var sc = 0.75 + 0.6 * hash2(k, j * 7 + 3), rt = hash2(k, j * 7 + 4);
      buckets[Math.min(NB - 1, Math.floor(z / MAP3D.WZ * NB)) * NB + Math.min(NB - 1, Math.floor(x / MAP3D.WX * NB))].push([x, groundY(x, z), z, sc, rt]);
      var xs = x < TW ? -x : MAP3D.WX - x < TW ? 2 * MAP3D.WX - x : null, zs = z < TW ? -z : MAP3D.WZ - z < TW ? 2 * MAP3D.WZ - z : null, mir = [];
      if (xs !== null) mir.push([xs, z]); if (zs !== null) mir.push([x, zs]); if (xs !== null && zs !== null) mir.push([xs, zs]);
      for (var mi = 0; mi < mir.length; mi++) {
        var X = mir[mi][0], Z = mir[mi][1], tt = outDist(X, Z) / TW;
        if (tt >= 1 || hash2(k, j * 7 + 5 + mi) < 0.25 + tt * 0.8) continue;
        outer[Math.min(2, Math.floor(tt * 3))].push([X, apronY(X, Z), Z, sc * (1 - 0.45 * tt), rt]);
      }
    }
  }
  var cone = new THREE.ConeGeometry(0.21, 0.66, 5, 1, true); cone.translate(0, 0.30, 0);
  var cp = cone.attributes.position, cols = new Float32Array(cp.count * 3);
  for (i = 0; i < cp.count; i++) { var t = clamp(cp.getY(i) / 0.63, 0, 1); cols[i * 3] = 0.12 + 0.20 * t; cols[i * 3 + 1] = 0.15 + 0.23 * t; cols[i * 3 + 2] = 0.13 + 0.19 * t; }
  cone.setAttribute('color', new THREE.BufferAttribute(cols, 3));
  var mat = new THREE.MeshBasicMaterial({ vertexColors: true }), m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), s = new THREE.Vector3(), v = new THREE.Vector3(), col = new THREE.Color(), up = new THREE.Vector3(0, 1, 0);
  R3.trees = [];
  for (i = 0; i < buckets.length; i++) {
    var B = buckets[i]; if (!B.length) continue;
    var g = cone.clone(), mesh = new THREE.InstancedMesh(g, mat, B.length), minx = 1e9, maxx = -1e9, minz = 1e9, maxz = -1e9;
    for (j = 0; j < B.length; j++) {
      var e = B[j]; q.setFromAxisAngle(up, e[4] * 6.283); s.set(e[3], e[3] * (0.85 + 0.4 * e[4]), e[3]); v.set(e[0], e[1] - 0.03, e[2]);
      m4.compose(v, q, s); mesh.setMatrixAt(j, m4);
      var tg = 0.72 + 0.5 * e[4]; col.setRGB(tg, tg * (0.98 + 0.08 * hash2(j, i)), tg); mesh.setColorAt(j, col);
      minx = Math.min(minx, e[0]); maxx = Math.max(maxx, e[0]); minz = Math.min(minz, e[2]); maxz = Math.max(maxz, e[2]);
    }
    g.boundingSphere = new THREE.Sphere(new THREE.Vector3((minx + maxx) / 2, 1, (minz + maxz) / 2), Math.sqrt((maxx - minx) * (maxx - minx) + (maxz - minz) * (maxz - minz)) / 2 + 3);
    mesh.instanceMatrix.needsUpdate = true; mesh.matrixAutoUpdate = false; R3.scene.add(mesh); R3.trees.push(mesh);
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
}
function flameTexture() {
  var c = document.createElement('canvas'); c.width = 64; c.height = 96;
  var x = c.getContext('2d'), g = x.createRadialGradient(32, 66, 2, 32, 60, 34);
  g.addColorStop(0, 'rgba(255,226,150,0.98)'); g.addColorStop(0.32, 'rgba(236,120,44,0.95)'); g.addColorStop(0.72, 'rgba(190,52,36,0.78)'); g.addColorStop(1, 'rgba(120,24,18,0)');
  x.fillStyle = g; x.beginPath(); x.moveTo(32, 2); x.bezierCurveTo(60, 44, 58, 92, 32, 94); x.bezierCurveTo(6, 92, 4, 44, 32, 2); x.fill();
  return new THREE.CanvasTexture(c);
}
function loadAssets() {
  var k;
  for (k in PORTRAITS) POR_URL[k] = URL.createObjectURL(b64blob(PORTRAITS[k], 'image/webp'));
  if (typeof TITLE_IMG === 'string' && TITLE_IMG) $('title').style.backgroundImage = 'url(' + TITLE_IMG + ')';      // v0.18: 만든 판에서는 CSS 에 들어 있다(첫 화면부터 그려지게 — tools/build.py)
  if (typeof HANJI_IMG === 'string') document.documentElement.style.setProperty('--hanji', 'url(' + HANJI_IMG + ')');
  function img(src, done) { var im = new Image(); R3.loading++; im.onload = function () { done(im); R3.loading--; if (!R3.loading) { R3.ready = true; requestDraw(); } }; im.onerror = function () { R3.loading--; }; im.src = src; }
  img(URL.createObjectURL(b64blob(TERRAIN_B64, 'image/jpeg')), function (im) {
    var t = new THREE.Texture(im); t.flipY = false; t.anisotropy = Math.min(8, R3.renderer.capabilities.getMaxAnisotropy()); t.needsUpdate = true;
    R3.tmat.uniforms.map.value = t; R3.tmat.uniforms.mapN.value.set(im.width, im.height);
  });
  Object.keys(SPRITES).forEach(function (key) {
    img(SPRITES[key].u, function (im) {
      SITE_IMG[key] = im;
      var t = new THREE.Texture(im); t.needsUpdate = true; TEX[key] = t;
      var f = t.clone(); f.repeat.x = -1; f.offset.x = 1; f.needsUpdate = true; TEXF[key] = f;
    });
  });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { R3.labelCache = {}; R3.bases.forEach(function (o) { o.sig = ''; }); for (var id in R3.units) R3.units[id].sig = ''; requestDraw(); });
}

/* 장면 초상(3:4): 처음 볼 때만 주소를 만든다. 장면이 없는 키는 '' */
function sceneUrl(key) {
  if (SCENE_URL[key] === undefined) SCENE_URL[key] = (typeof SCENES !== 'undefined' && SCENES[key]) ? URL.createObjectURL(b64blob(SCENES[key], 'image/webp')) : '';
  return SCENE_URL[key];
}
/* 초상 그림 객체: 처음 쓸 때 불러오고, 다 불러오면 부대 이름표를 다시 그린다 */
function porImg(key) {
  var im = POR_IMG[key];
  if (im === undefined) {
    if (!POR_URL[key]) { POR_IMG[key] = null; return null; }
    im = POR_IMG[key] = new Image();
    im.onload = function () { im.ok = true; if (R3) { for (var id in R3.units) R3.units[id].sig = ''; } requestDraw(); };
    im.src = POR_URL[key];
  }
  return im && im.ok ? im : null;
}

/* ---------- 이름표 ---------- */
function rr(x, X, Y, w, h, r) { x.beginPath(); x.moveTo(X + r, Y); x.arcTo(X + w, Y, X + w, Y + h, r); x.arcTo(X + w, Y + h, X, Y + h, r); x.arcTo(X, Y + h, X, Y, r); x.arcTo(X, Y, X + w, Y, r); x.closePath(); }
function mkLabel() {
  var c = document.createElement('canvas'); c.width = 8; c.height = 8;
  var t = new THREE.CanvasTexture(c); t.minFilter = THREE.LinearFilter; t.generateMipmaps = false;
  var sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: t, transparent: true, depthTest: false, depthWrite: false, sizeAttenuation: false }));
  sp.center.set(0.5, 0); sp.renderOrder = 6;
  return { sp: sp, cv: c, tex: t, w: 8, h: 8 };
}
function labelSize(L, k) { L.sp.scale.set(L.w / 2 / CH * K3 * k, L.h / 2 / CH * K3 * k, 1); }
/* lines: [{t, px, font, color, bold}], 판 색 bg, 테두리 색 */
function corpsMark(cp) { return cp.n >= 1 && cp.n <= 20 ? String.fromCharCode(0x245F + cp.n) : String(cp.n); }      // ① ② ③ …
function drawLabel(L, lines, bg, border, badge, badgeBg, face, bar) {
  var x = L.cv.getContext('2d'), i, w = 0, h = 10, S = 2, BH = bar ? 13 : 0;      // v0.20: bar = { v: 0~1 } 이면 판 아래에 막대(성의 내구)
  for (i = 0; i < lines.length; i++) { x.font = (lines[i].bold || 700) + ' ' + lines[i].px * S + 'px ' + (lines[i].font || FONT_B); lines[i].w = x.measureText(lines[i].t).width; w = Math.max(w, lines[i].w); h += lines[i].px * S * 1.18; }
  w = Math.ceil(w + 22 * S / 2 + (badge ? 30 : 8)); h = Math.ceil(h) + BH;
  // v0.18: 얼굴 딱지 — 판 밖으로 왼쪽 ox · 위 oy 만큼 나와 모서리에 걸친다. 글씨는 얼굴에 가리지 않게 오른쪽으로 조금 민다
  var FD = face ? FACE_D : 0, ox = face ? Math.round(FD * 0.40) : 0, oy = face ? Math.round(FD * 0.46) : 0, tsh = face ? Math.round(FD * 0.13) : 0;
  if (face) w += tsh * 2;
  L.cv.width = w + ox; L.cv.height = h + oy; L.w = w + ox; L.h = h + oy; L.ax = (ox + w / 2) / (w + ox); L.ay = h / (h + oy);
  x = L.cv.getContext('2d'); x.save(); x.translate(ox, oy);
  var bw = w - (badge ? 22 : 0), sel = border === SEAL, tcx = bw / 2 + tsh;
  // 석채(石彩) 빛 판에 종이 빛 글씨, 가는 먹선. 고른 것은 인주색 겹테
  rr(x, 3, 3, bw - 6, h - 6, 3); x.fillStyle = bg; x.fill();
  x.lineWidth = sel ? 4 : 1.6; x.strokeStyle = sel ? SEAL : border; x.stroke();
  if (sel) { rr(x, 6.5, 6.5, bw - 13, h - 13, 1.5); x.lineWidth = 1.2; x.strokeStyle = 'rgba(251,246,234,0.75)'; x.stroke(); }
  var y = 5;
  x.textAlign = 'center'; x.textBaseline = 'top';
  for (i = 0; i < lines.length; i++) {
    var ln = lines[i]; x.font = (ln.bold || 700) + ' ' + ln.px * S + 'px ' + (ln.font || FONT_B);
    x.fillStyle = 'rgba(20,18,16,0.38)'; x.fillText(ln.t, tcx + 1, y + 1.5);
    x.fillStyle = ln.color || '#fbf6ea'; x.fillText(ln.t, tcx, y); y += ln.px * S * 1.18;
  }
  if (bar) {                                                    // 내구 막대: 먹빛 홈에 남은 만큼
    var bx0 = 9, bwid = bw - 18, by0 = h - BH - 2, bv = clamp(bar.v, 0, 1);
    rr(x, bx0, by0, bwid, 8, 2.5); x.fillStyle = 'rgba(20,18,16,0.62)'; x.fill();
    if (bv > 0) { rr(x, bx0 + 1, by0 + 1, Math.max(3, (bwid - 2) * bv), 6, 2); x.fillStyle = bv < 0.3 ? '#e2574a' : (bv < 0.6 ? '#e6b63c' : '#f4efe3'); x.fill(); }
    x.lineWidth = 1; x.strokeStyle = 'rgba(251,246,234,0.55)'; rr(x, bx0, by0, bwid, 8, 2.5); x.stroke();
  }
  if (badge) { rr(x, w - 31, 3, 28, 28, 4); x.fillStyle = badgeBg || SEAL; x.fill(); x.lineWidth = 1.5; x.strokeStyle = '#fbf6ea'; x.stroke(); x.fillStyle = '#fbf6ea'; x.font = '800 19px ' + FONT_B; x.textBaseline = 'middle'; x.fillText(badge, w - 17, 18); }
  x.restore();
  if (face) { x.globalAlpha = face.dim ? 0.78 : 1; faceAt(x, face.img, face.ring, 0, 0, FD); x.globalAlpha = 1; }
  L.tex.dispose(); L.tex.needsUpdate = true;
}
/* 상태 딱지(부대 머리 위): segs = [{t, bg}] 를 옆으로 나란히. 종이 빛 테두리를 둘러 어떤 땅 위에서도 읽힌다 */
var ST_COL = { confuse: '#2f4f6f', rumor: '#8a5a12', fire: '#b5332a' }, ST_TINT = { confuse: 0xaebdd2, rumor: 0xdccda4 };
function drawChips(L, segs) {
  var x = L.cv.getContext('2d'), S = 2, px = 12.5 * S, pad = 6.5 * S, gap = 2.5 * S, bh = Math.ceil(px * 1.5), w = 6, i, tail = 9;
  x.font = '800 ' + px + 'px ' + FONT_B;
  for (i = 0; i < segs.length; i++) { segs[i].w = Math.ceil(x.measureText(segs[i].t).width + pad * 2); w += segs[i].w + (i ? gap : 0); }
  L.cv.width = w; L.cv.height = bh + 6 + tail; L.w = w; L.h = bh + 6 + tail;
  x = L.cv.getContext('2d'); x.font = '800 ' + px + 'px ' + FONT_B; x.textAlign = 'center'; x.textBaseline = 'middle'; x.lineJoin = 'round';
  // 꼬리(가운데 아래 세모) — 어느 부대의 딱지인지 가리킨다
  x.beginPath(); x.moveTo(w / 2 - 9, bh + 1); x.lineTo(w / 2, bh + 3 + tail); x.lineTo(w / 2 + 9, bh + 1); x.closePath(); x.fillStyle = segs[0].bg; x.fill(); x.lineWidth = 2.4; x.strokeStyle = '#fbf6ea'; x.stroke();
  var X = 3;
  for (i = 0; i < segs.length; i++) {
    rr(x, X, 3, segs[i].w, bh, 6); x.fillStyle = segs[i].bg; x.fill(); x.lineWidth = 2.4; x.strokeStyle = '#fbf6ea'; x.stroke();
    x.fillStyle = 'rgba(20,18,16,0.4)'; x.fillText(segs[i].t, X + segs[i].w / 2 + 1, 3 + bh / 2 + 2.5);
    x.fillStyle = '#fbf6ea'; x.fillText(segs[i].t, X + segs[i].w / 2, 3 + bh / 2 + 1);
    X += segs[i].w + gap;
  }
  x.beginPath(); x.moveTo(w / 2 - 7.5, bh + 1.5); x.lineTo(w / 2, bh + tail); x.lineTo(w / 2 + 7.5, bh + 1.5); x.closePath(); x.fillStyle = segs[0].bg; x.fill();   // 테두리 선을 덮어 판과 꼬리를 잇는다
  L.tex.dispose(); L.tex.needsUpdate = true;
}
/* 부대의 상태 딱지에 적을 것 */
function statusSegs(u) {
  var segs = [], n = statusLeft(u);
  if (u.status) segs.push({ t: statusName(u.status) + (n > 0 ? ' ' + n * 10 + '일' : ''), bg: ST_COL[u.status] || ST_COL.confuse });      // 남은 날수(1턴 = 10일)
  if (unitOnFire(u)) segs.push({ t: '불길', bg: ST_COL.fire });
  return segs;
}
/* 주장 얼굴 딱지(둥근 초상). 테두리는 세력 색. v0.18: 이름·병력 판의 왼쪽 위 모서리에 붙여 한 덩어리로 그린다(drawLabel 의 face) */
var FACE_D = 60;
function faceAt(x, img, ring, X, Y, S) {                     // (X, Y) 에서 한 변 S 인 네모 안에
  x.save(); x.beginPath(); x.arc(X + S / 2, Y + S / 2, S / 2 - 4, 0, 6.3); x.clip(); x.fillStyle = '#f6f1e6'; x.fillRect(X, Y, S, S);
  x.globalCompositeOperation = 'multiply';
  try { var iw = img.naturalWidth, ih = img.naturalHeight; x.drawImage(img, iw * 0.25, ih * 0.13, iw * 0.50, ih * 0.50, X + 3, Y + 3, S - 6, S - 6);    /* v0.5 흉상: 얼굴 중심이 가로 50%·세로 41% */ } catch (e) { /* 바탕만 */ }
  x.restore();
  x.beginPath(); x.arc(X + S / 2, Y + S / 2, S / 2 - 4, 0, 6.3); x.lineWidth = 5; x.strokeStyle = ring; x.stroke();
  x.beginPath(); x.arc(X + S / 2, Y + S / 2, S / 2 - 1.3, 0, 6.3); x.lineWidth = 1.4; x.strokeStyle = 'rgba(27,26,24,0.9)'; x.stroke();
}
function drawFace(L, img, ring) {
  var S = FACE_D; L.cv.width = L.cv.height = S; L.w = L.h = S;
  faceAt(L.cv.getContext('2d'), img, ring, 0, 0, S);
  L.tex.dispose(); L.tex.needsUpdate = true;
}
function mixHex(a, b, t) { var x = rgbOf(a), y = rgbOf(b); return 'rgb(' + Math.round(x[0] + (y[0] - x[0]) * t) + ',' + Math.round(x[1] + (y[1] - x[1]) * t) + ',' + Math.round(x[2] + (y[2] - x[2]) * t) + ')'; }
/* 붓으로 한 번에 두른 고리(성역 표시): 굵기가 변하고 한쪽이 트여 있다 */
function ensoTexture() {
  var n = 256, c = document.createElement('canvas'); c.width = c.height = n;
  var x = c.getContext('2d'), i, s = 91;
  function rnd() { s = (s * 1664525 + 1013904223) | 0; return ((s >>> 8) & 0xffff) / 65535; }
  x.translate(n / 2, n / 2);
  for (var pass = 0; pass < 3; pass++) {
    var a0 = 0.5 + rnd() * 0.3, a1 = a0 + 5.45 + rnd() * 0.4, steps = 220;
    for (i = 0; i < steps; i++) {
      var t = i / (steps - 1), a = a0 + (a1 - a0) * t, r = 112 + Math.sin(a * 3.1 + pass) * 1.6 + (rnd() - 0.5) * 1.4;
      var wd = (2.2 + 4.6 * Math.sin(Math.PI * Math.pow(t, 0.8))) * (pass ? 0.55 : 1), al = (0.34 + 0.4 * Math.sin(Math.PI * t)) * (pass ? 0.5 : 1) * (0.6 + 0.4 * rnd());
      x.fillStyle = 'rgba(255,255,255,' + al.toFixed(3) + ')';
      x.beginPath(); x.arc(Math.cos(a) * (r - pass * 3.5), Math.sin(a) * (r - pass * 3.5), wd, 0, 6.3); x.fill();
    }
  }
  var t2 = new THREE.CanvasTexture(c); t2.minFilter = THREE.LinearMipmapLinearFilter; return t2;
}
/* 부대 발밑의 먹점: 가운데가 짙고 가장자리가 번진 점 */
function inkDotTexture() {
  var n = 96, c = document.createElement('canvas'); c.width = c.height = n;
  var x = c.getContext('2d'), g = x.createRadialGradient(n / 2, n / 2, 4, n / 2, n / 2, n / 2);
  g.addColorStop(0, 'rgba(255,255,255,0.95)'); g.addColorStop(0.62, 'rgba(255,255,255,0.86)'); g.addColorStop(0.84, 'rgba(255,255,255,0.42)'); g.addColorStop(1, 'rgba(255,255,255,0)');
  x.fillStyle = g; x.fillRect(0, 0, n, n);
  return new THREE.CanvasTexture(c);
}
function shade(hex, k) { var c = rgbOf(hex); return 'rgb(' + Math.round(c[0] * k) + ',' + Math.round(c[1] * k) + ',' + Math.round(c[2] * k) + ')'; }

/* ---------- 공사장(v0.10.1) ----------
   짓는 중인 시설은 완성된 그림 대신 '밑그림 + 비계'로 보인다: 그 시설의 그림을 먹빛만 옅게 남기고(밑그림), 그 위에 대나무 비계 · 통나무 더미 · 붉은 깃발을 덧그린다.
   공사가 나아갈수록(셋으로 나눈 단계 0·1·2) 밑그림이 짙어진다. 처음 쓸 때 만들어 TEX['시설@단계'] 에 넣어 둔다(SPRITES 에도 같은 크기로 올린다 — setSprite 가 그대로 쓴다). */
var SITE_IMG = {}, SITE_URL = {}, SITE_INK = [0.66, 0.76, 0.86], SITE_A = [0.96, 0.98, 1];      // v0.20: 먹을 짙게(멀리서도 보이게 — 전에는 0.42~0.68 · 0.84~0.95)
function siteStage(fc) { return clamp(Math.floor(3 * (fc.prog || 0) / Math.max(1, fc.need || 1)), 0, 2); }
function siteCanvas(key, st) {
  var im = SITE_IMG[key], S = SPRITES[key]; if (!im || !S) return null;
  var w = S.w, h = S.h, c = document.createElement('canvas'), i; c.width = w; c.height = h;
  var x = c.getContext('2d'); x.drawImage(im, 0, 0, w, h);
  var d, x0 = w, x1 = 0, y0 = h, y1 = 0, k = SITE_INK[st], al = SITE_A[st];
  try { d = x.getImageData(0, 0, w, h); } catch (e) { return null; }
  var p = d.data;
  for (i = 0; i < p.length; i += 4) {
    var a = p[i + 3];
    if (a > 60) { var px = (i >> 2) % w, py = ((i >> 2) / w) | 0; if (px < x0) x0 = px; if (px > x1) x1 = px; if (py < y0) y0 = py; if (py > y1) y1 = py; }
    var g = 255 - (255 - (p[i] * 0.3 + p[i + 1] * 0.59 + p[i + 2] * 0.11)) * k;
    p[i] = g; p[i + 1] = g * 0.985; p[i + 2] = g * 0.95; p[i + 3] = a * al;
  }
  x.putImageData(d, 0, 0);
  if (x1 - x0 < 40 || y1 - y0 < 40) return c;
  var seed = 7; for (i = 0; i < key.length; i++) seed = (Math.imul(seed, 31) + key.charCodeAt(i)) | 0;
  function rnd() { seed = (seed + 0x6D2B79F5) | 0; var t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }
  // 비계: 바닥의 마름모(왼쪽 L · 앞 F · 오른쪽 R · 뒤 B) 위에 세운 틀. 앞의 두 면은 또렷하게, 뒤는 옅게
  var cx = (x0 + x1) / 2, A = (x1 - x0) * 0.385, B = A * 0.5, base = y1 - B - (y1 - y0) * 0.11, H = Math.min(Math.max((base - B) - (y0 + 16), 34), A * 1.05);
  var L = [cx - A, base], F = [cx, base + B], R = [cx + A, base], K = [cx, base - B], POLE = '#9c6c34', EDGE = 'rgba(58,40,24,0.94)', BACK = 'rgba(150,112,64,0.5)';
  function up(P, hh) { return [P[0], P[1] - hh]; }
  function mid(P, Q) { return [(P[0] + Q[0]) / 2, (P[1] + Q[1]) / 2]; }
  function line(P, Q, wd, col, edge) {                               // 손으로 그은 듯 조금 흔들리는 선(먹 테두리 + 대나무 빛)
    var n = 6, pts = [], j;
    for (j = 0; j <= n; j++) { var t = j / n, in_ = (j > 0 && j < n) ? 1.2 : 0; pts.push([P[0] + (Q[0] - P[0]) * t + (rnd() - 0.5) * in_, P[1] + (Q[1] - P[1]) * t + (rnd() - 0.5) * in_]); }
    function path() { x.beginPath(); x.moveTo(pts[0][0], pts[0][1]); for (j = 1; j <= n; j++) x.lineTo(pts[j][0], pts[j][1]); }
    x.lineCap = 'round'; x.lineJoin = 'round';
    if (edge) { path(); x.strokeStyle = EDGE; x.lineWidth = wd + 1.3; x.stroke(); }
    path(); x.strokeStyle = col; x.lineWidth = wd; x.stroke();
  }
  line(K, up(K, H), 1.4, BACK); line(up(L, H), up(K, H), 1.4, BACK); line(up(K, H), up(R, H), 1.4, BACK);
  [0.36, 0.70].forEach(function (q) { line(up(L, H * q), up(K, H * q), 1.1, BACK); line(up(K, H * q), up(R, H * q), 1.1, BACK); });
  [L, mid(L, F), F, mid(F, R), R].forEach(function (P) { line([P[0], P[1] + 2], up(P, H + 5), 3.2, POLE, true); });
  [0.36, 0.70, 1].forEach(function (q) { line(up(L, H * q), up(F, H * q), 2.6, POLE, true); line(up(F, H * q), up(R, H * q), 2.6, POLE, true); });
  line(L, up(mid(L, F), H * 0.36), 1.3, POLE, true); line(up(mid(L, F), H * 0.36), up(F, H * 0.70), 1.3, POLE, true);
  line(R, up(mid(F, R), H * 0.36), 1.3, POLE, true); line(up(mid(F, R), H * 0.36), up(F, H * 0.70), 1.3, POLE, true);
  var ft = up(R, H + 22);                                             // 붉은 깃발: 오른쪽 기둥 꼭대기
  line(up(R, H + 5), ft, 1.0, EDGE);
  x.beginPath(); x.moveTo(ft[0], ft[1]); x.lineTo(ft[0] - 22, ft[1] + 7); x.lineTo(ft[0], ft[1] + 14); x.closePath(); x.fillStyle = '#ba342a'; x.fill(); x.lineWidth = 1; x.strokeStyle = 'rgba(58,40,24,0.9)'; x.stroke();
  var lx = cx - A * 0.72, ly = base + B * 0.78;                       // 통나무 더미: 왼쪽 앞 바닥
  for (i = 0; i < 3; i++) line([lx + i * 3.2 - 10, ly + i * 2.4 - 3], [lx + i * 3.2 + 10, ly + i * 2.4 - 13], 2.6, '#b0844e', true);
  return c;
}
/* 짓는 중인 시설에 쓸 그림의 키('market@1'). 만들 수 없으면(그림이 아직 없다) '' — 그때는 전처럼 완성된 그림을 옅게 쓴다 */
function siteTexKey(t, st) {
  var k = t + '@' + st;
  if (TEX[k]) return k;
  if (TEX[k] === null) return '';
  var c = siteCanvas(t, st);
  if (!c) { if (SITE_IMG[t]) TEX[k] = null; return ''; }
  var tx = new THREE.CanvasTexture(c); TEX[k] = tx; SPRITES[k] = { w: SPRITES[t].w, h: SPRITES[t].h, ay: SPRITES[t].ay };
  return k;
}
/* 목록과 창의 작은 그림에 쓸 주소(가운데 단계). 없으면 '' */
function siteUrl(t) {
  if (SITE_URL[t] === undefined) {
    var c = siteCanvas(t, 1); if (!c) return SITE_IMG[t] ? (SITE_URL[t] = '') : '';
    try { SITE_URL[t] = URL.createObjectURL(b64blob(c.toDataURL('image/png').split(',')[1], 'image/png')); } catch (e) { SITE_URL[t] = ''; }
  }
  return SITE_URL[t];
}

/* ---------- 물체 ---------- */
var BASE_W = { L: 3.5, M: 3.1, S: 2.7, G: 3.0 }, FAC_W = 1.62, UNIT_W = 2.0;
function spriteObj(key, wu, order) {
  var S = SPRITES[key], sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: TEX[key], transparent: true, depthTest: false, depthWrite: false }));
  sp.center.set(0.5, S.ay); sp.scale.set(wu, wu * S.h / S.w, 1); sp.renderOrder = order;
  sp.userData = { key: key, top: wu * S.h / S.w * (1 - S.ay), w: wu, h: wu * S.h / S.w, ay: S.ay };
  return sp;
}
function setSprite(sp, key, wu, flip) {
  var S = SPRITES[key]; sp.material.map = flip ? TEXF[key] : TEX[key]; sp.material.needsUpdate = true;
  sp.center.set(0.5, S.ay); sp.scale.set(wu, wu * S.h / S.w, 1);
  sp.userData.key = key; sp.userData.top = wu * S.h / S.w * (1 - S.ay); sp.userData.w = wu; sp.userData.h = wu * S.h / S.w; sp.userData.ay = S.ay;
}
function syncScene() {
  if (!G || !R3.ready) return;
  var i, j, b, o, p, sig, idleN = {};
  for (i = 0; i < G.officers.length; i++) { var of = G.officers[i]; if (of.st === 'active' && of.f === G.player && of.unit === null && !of.acted) idleN[of.loc] = (idleN[of.loc] || 0) + 1; }
  // 거점
  for (i = 0; i < G.bases.length; i++) {
    b = G.bases[i]; o = R3.bases[i];
    if (!o) {
      p = hexPos(b.c, b.r); o = R3.bases[i] = { g: new THREE.Group(), sig: '' };
      o.sp = spriteObj(b.kind === 'gate' ? 'gate' : 'city_' + b.sz, BASE_W[b.sz], 2); o.lab = mkLabel();
      o.g.position.set(p[0], p[1], p[2]); o.g.add(o.sp); o.g.add(o.lab.sp); o.lab.sp.position.set(0, o.sp.userData.top * 0.74, 0); R3.objs.add(o.g);
    }
    var mineB = b.owner === G.player, col = b.owner >= 0 ? G.factions[b.owner].color : NEUTRAL;
    o.lab.sp.visible = !(SPOT.on && SPOT.v && SPOT.v.b === b);
    if (b.kind === 'city' && !o.zone) {                                 // 성역(성 둘레 ZONE_R 칸)을 붓으로 두른 고리
      var zr = (ZONE_R + 0.5) * SQ3 * 0.94;
      o.zone = new THREE.Mesh(R3.zoneGeo || (R3.zoneGeo = new THREE.PlaneGeometry(2, 2).rotateX(-Math.PI / 2)), new THREE.MeshBasicMaterial({ map: R3.zoneTex || (R3.zoneTex = ensoTexture()), transparent: true, opacity: 0.6, depthTest: false, depthWrite: false }));
      o.zone.scale.set(zr, 1, zr * 0.93); o.zone.rotation.y = hash2(i, 77) * 6.283; o.zone.position.set(o.g.position.x, o.g.position.y + 0.06, o.g.position.z); o.zone.renderOrder = 0.5; R3.objs.add(o.zone);
    }
    if (o.zone && o.zcol !== col) { o.zcol = col; o.zone.material.color.set(shade(col, 0.82)); }
    var cpL = mineB ? baseCorps(b) : null;                                 // 군단에 맡긴 거점: 쉬는 무장 수 대신 군단 번호 딱지
    sig = b.owner + '|' + (b.owner >= 0 ? Math.round(b.troops / 100) : '') + '|' + (mineB && !cpL ? (idleN[b.id] || 0) : '') + '|' + (UI.sel && UI.sel.kind === 'base' && UI.sel.id === b.id) + '|' + (cpL ? cpL.n : '') + '|' + Math.round(40 * b.dur / Math.max(1, b.maxDur));
    if (sig !== o.sig) {
      o.sig = sig;
      var ls = [{ t: b.n, px: 15, font: FONT_D, bold: 900 }];
      if (b.owner >= 0) ls.push({ t: fmt(b.troops), px: 10.5, color: '#f6efdf' });
      drawLabel(o.lab, ls, shade(col, 0.86), (UI.sel && UI.sel.kind === 'base' && UI.sel.id === b.id) ? SEAL : INK, cpL ? corpsMark(cpL) : (mineB && idleN[b.id] ? idleN[b.id] : 0), cpL ? INK : null, null, { v: b.dur / Math.max(1, b.maxDur) });
      R3.labelK = 0;
    }
    // 시설
    for (j = 0; j < b.plots.length; j++) {
      var pl = b.plots[j], fk = i + ':' + j, fo = R3.facs[fk], fc = pl.fac;
      if (!fc) { if (fo) { R3.objs.remove(fo.sp); fo.sp.material.dispose(); delete R3.facs[fk]; } continue;      }
      var sk = fc.done ? '' : siteTexKey(fc.t, siteStage(fc)), onU = UAT[K(pl.c, pl.r)] ? 1 : 0, fs = fc.t + fc.lv + (fc.done ? 'd' : 'c' + sk) + (onU ? 'u' : '');      // 짓는 중: 공사장 그림(단계가 오르면 바뀐다)
      if (!fo) { p = hexPos(pl.c, pl.r); fo = R3.facs[fk] = { sp: spriteObj(fc.t, FAC_W, 2), sig: '' }; fo.sp.position.set(p[0], p[1], p[2]); R3.objs.add(fo.sp); }
      if (fo.sig !== fs) { fo.sig = fs; setSprite(fo.sp, sk || fc.t, FAC_W * (0.94 + 0.10 * ((facHasLv(fc.t) ? fc.lv : 1) - 1))); fo.sp.material.opacity = ((fc.done || sk) ? 1 : 0.5) * (onU ? 0.38 : 1); }      // v0.12: 부대가 올라선 시설은 흐리게
    }
  }
  // 부대
  var seen = {};
  for (i = 0; i < G.units.length; i++) {
    var u = G.units[i]; seen[u.id] = 1; o = R3.units[u.id];
    var fcol = G.factions[u.f].color, key = 'u_' + u.type, L = uLeader(u), isSel = UI.sel && UI.sel.kind === 'unit' && UI.sel.id === u.id;
    if (!o) {
      o = R3.units[u.id] = { g: new THREE.Group(), sig: '', anim: false, face: 1, c: -1, r: -1 };
      o.sp = spriteObj(key, UNIT_W, 3); o.lab = mkLabel(); o.g.add(o.sp); o.g.add(o.lab.sp);
      o.fc = mkLabel(); o.fc.sp.center.set(0.5, 0.5); o.fc.sp.renderOrder = 7; o.fc.sp.visible = false; o.fcOn = false; o.g.add(o.fc.sp);
      o.st = mkLabel(); o.st.sp.renderOrder = 8; o.st.sp.visible = false; o.stOn = false; o.stK = ''; o.ph = (u.id * 1.7) % 6.283; o.g.add(o.st.sp);      // 상태 딱지
      o.sw = new THREE.Sprite(new THREE.SpriteMaterial({ map: fxTex('swirl'), color: 0x2f4f6f, transparent: true, opacity: 0.9, depthTest: false, depthWrite: false }));   // 머리 위 소용돌이
      o.sw.renderOrder = 5; o.sw.visible = false; o.g.add(o.sw);
      o.ring = new THREE.Mesh(R3.ringGeo || (R3.ringGeo = new THREE.CircleGeometry(1.0, 24).rotateX(-Math.PI / 2)), new THREE.MeshBasicMaterial({ color: fcol, map: R3.dotTex || (R3.dotTex = inkDotTexture()), transparent: true, opacity: 0.78, depthTest: false, depthWrite: false }));
      o.ring.renderOrder = 1; R3.objs.add(o.ring); R3.objs.add(o.g);
    }
    if (!o.anim && (o.c !== u.c || o.r !== u.r)) {
      p = hexPos(u.c, u.r);
      if (o.c >= 0) { var px0 = hexCenter(o.c, o.r)[0]; if (Math.abs(p[0] - px0) > 0.2) o.face = p[0] < px0 ? -1 : 1; }
      o.c = u.c; o.r = u.r; o.g.position.set(p[0], p[1], p[2]); o.ring.position.set(p[0], p[1] + 0.04, p[2]);
    }
    var showName = isSel || R3.nameZoom, fim = (isSel || R3.faceZoom) ? porImg(L.por) : null;
    var segs = statusSegs(u);
    var cpU = unitCorps(u);
    sig = (cpU ? cpU.n : '') + '|' + u.f + '|' + u.type + '|' + Math.round(u.troops / 10) + '|' + (u.f === G.player && u.done) + '|' + segs.map(function (g) { return g.t; }).join('+') + '|' + isSel + '|' + o.face + '|' + L.n + '|' + (u.dest >= 0) + '|' + showName + '|' + (fim ? 1 : 0);
    if (sig !== o.sig) {
      o.sig = sig; setSprite(o.sp, key, UNIT_W, o.face < 0);
      var dim = u.f === G.player && u.done;
      o.sp.material.color.setHex(u.status ? (ST_TINT[u.status] || 0xffffff) : 0xffffff); o.sp.material.opacity = dim ? 0.52 : 1; o.ring.material.color.set(fcol); o.ring.material.opacity = dim ? 0.4 : 0.78;
      // 상태: 머리 위 딱지 + 소용돌이. 혼란이면 tick 에서 좌우로 비틀거리게 한다
      o.stOn = segs.length > 0; o.stK = u.status || '';
      if (!o.stK) o.sp.material.rotation = 0;
      if (o.stOn) { drawChips(o.st, segs); o.stY = o.sp.userData.top * 0.97; o.st.sp.position.set(0.06, o.stY, 0); }
      o.sw.visible = !!o.stK;
      if (o.stK) { o.sw.material.color.set(ST_COL[o.stK] || ST_COL.confuse); o.sw.scale.set(1.18, 1.18, 1); o.sw.position.set(0.02, o.sp.userData.top * 0.72, 0); }
      o.lab.sp.position.set(0, -0.16, 0);
      var mark = cpU ? corpsMark(cpU) + ' ' : ((!u.status && u.dest >= 0) ? '▸ ' : ''), lns = [{ t: mark + fmt(u.troops), px: 12, bold: 800, color: '#fbf6ea' }];      // 상태는 머리 위 딱지가 알린다(0.8까지는 여기에 '혼란 ' 글자를 붙였다)
      if (showName) lns.unshift({ t: L.n, px: 10.5, font: FONT_D, bold: 900, color: '#fbf6ea' });
      drawLabel(o.lab, lns, dim ? mixHex(fcol, '#8d877b', 0.6) : shade(fcol, 0.84), isSel ? SEAL : INK, undefined, undefined, fim ? { img: fim, ring: isSel ? SEAL : fcol, dim: dim } : null);      // v0.18: 얼굴 · 이름 · 병력이 한 덩어리
      o.lab.sp.center.set(o.lab.ax, o.lab.ay); o.fcOn = false; o.hasFace = !!fim;
      R3.labelK = 0;
    }
    o.g.visible = o.ring.visible = (u.id !== UI.hide) || o.anim;
  }
  for (var id in R3.units) {
    if (seen[id] || R3.units[id].anim) continue;
    o = R3.units[id]; R3.objs.remove(o.g); R3.objs.remove(o.ring); o.sp.material.dispose(); o.lab.tex.dispose(); o.lab.sp.material.dispose(); o.fc.tex.dispose(); o.fc.sp.material.dispose(); o.st.tex.dispose(); o.st.sp.material.dispose(); o.sw.material.dispose(); o.ring.material.dispose(); delete R3.units[id];
  }
  // 불
  for (var fk2 in G.fires) {
    if (R3.fires[fk2]) continue;
    var kk = +fk2, fc2 = kk % W; p = hexPos(fc2, (kk - fc2) / W);
    var fg = new THREE.Group(); fg.position.set(p[0], p[1], p[2]);
    for (j = 0; j < 5; j++) { var fsprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: R3.flame, transparent: true, depthTest: false, depthWrite: false })); fsprite.center.set(0.5, 0.08); fsprite.position.set((j - 2) * 0.33, 0, (j % 2) * 0.24 - 0.1); fsprite.renderOrder = 4; fsprite.userData.k = j === 2 ? 1.25 : (j % 2 ? 1 : 0.8); fg.add(fsprite); }      // v0.20: 불꽃 다섯(가운데가 크다)
    for (j = 0; j < 2; j++) { var smoke = new THREE.Sprite(new THREE.SpriteMaterial({ map: fxTex('puff'), color: 0x4a4640, transparent: true, opacity: 0, depthTest: false, depthWrite: false })); smoke.renderOrder = 3.9; smoke.userData.smoke = j + 1; fg.add(smoke); }      // 연기 둘이 번갈아 오른다
    R3.objs.add(fg); R3.fires[fk2] = fg;
  }
  for (fk2 in R3.fires) if (!G.fires[fk2]) { R3.objs.remove(R3.fires[fk2]); delete R3.fires[fk2]; }
  // 철
  var m = G.month, tn = R3.tmat.uniforms.tint.value;
  if (m >= 3 && m <= 5) tn.set(0.995, 1.0, 0.985); else if (m >= 6 && m <= 8) tn.set(0.985, 1.0, 0.975); else if (m >= 9 && m <= 11) tn.set(1.0, 0.985, 0.95); else tn.set(0.99, 0.995, 1.01);
  rebuildOverlay(); R3.billboard = true; drawMini();
}
function ovPut(k, c, a) { var d = R3.ovData, i = k * 4; d[i] = c[0]; d[i + 1] = c[1]; d[i + 2] = c[2]; d[i + 3] = a; }
function rebuildOverlay() {
  var d = R3.ovData, i, j, k; d.fill(0);
  for (i = 0; i < G.bases.length; i++) {                       // 세력권
    var b = G.bases[i]; if (b.owner < 0) continue;
    var col = rgbOf(G.factions[b.owner].color), rad = b.kind === 'gate' ? 1 : ZONE_R;
    for (var r = Math.max(0, b.r - rad); r <= Math.min(H - 1, b.r + rad); r++) for (var c = Math.max(0, b.c - rad - 1); c <= Math.min(W - 1, b.c + rad + 1); c++) {
      if (hdist(c, r, b.c, b.r) > rad) continue; k = r * W + c; var t = TCH[k];
      if (t !== 120 && t !== 115 && t !== 109) ovPut(k, col, 44);
    }
    if (b.owner === G.player && b.kind === 'city') for (j = 0; j < b.plots.length; j++) if (!b.plots[j].fac) ovPut(K(b.plots[j].c, b.plots[j].r), [176, 124, 34], 88);
  }
  var mpv = UI.mpath && UI.mpath.path ? UI.mpath.path : null;      // v0.18: 고른 부대가 행군(또는 공격 명령) 중이면 갈 길을 보여 준다
  if (mpv) for (i = 0; i < mpv.length; i++) ovPut(mpv[i], [47, 79, 111], 96);
  var su = selUnit();
  if (su && UI.rc && !UI.busy) {
    for (var ks in UI.rc.stop) { k = +ks; if (BAT[k] !== undefined) ovPut(k, [176, 124, 34], 170); else ovPut(k, [47, 79, 111], 122); }
    var ats = UI.atk || [];
    for (i = 0; i < ats.length; i++) ovPut(K(ats[i].c, ats[i].r), [181, 51, 42], 172);
  }
  if (UI.sel && UI.sel.kind === 'unit' && UMAP[UI.sel.id]) ovPut(K(UMAP[UI.sel.id].c, UMAP[UI.sel.id].r), [27, 26, 24], 96);
  if (UI.sel && UI.sel.kind === 'base') ovPut(K(G.bases[UI.sel.id].c, G.bases[UI.sel.id].r), [176, 124, 34], 150);
  if (UI.target) ovPut(K(UI.target.c, UI.target.r), [181, 51, 42], 225);
  var pkL = (typeof MODAL !== 'undefined' && MODAL && MODAL.pick) ? MODAL.pick.list() : null;      // v0.20: 지도에서 고르는 칸(나갈 자리 · 보낼 성)
  if (pkL) for (i = 0; i < pkL.length; i++) ovPut(K(pkL[i].c, pkL[i].r), pkL[i].on ? [181, 51, 42] : [212, 160, 44], pkL[i].on ? 205 : 160);
  if (SPOT.on && SPOT.v) for (i = 0; i < SPOT.v.lots.length; i++) {            // 건설 자리
    var sl = SPOT.v.lots[i];
    if (sl.i === SPOT.v.pi) ovPut(K(sl.c, sl.r), [181, 51, 42], 138); else if (sl.ok) ovPut(K(sl.c, sl.r), [212, 160, 44], 120);
  }
  R3.ovTex.needsUpdate = true;
}

document.addEventListener('click', function (e) { var t = document.getElementById('talk'); if (t && t.classList.contains('on') && t.contains(e.target)) talkHide(); });      // 대화창: 누르면 닫힌다

/* ---------- 건설 자리 비추기 ----------
   건설을 고른 동안에는 지도를 어둡게 덮고 지을 수 있는 빈 부지만 뚫어 밝게 보인다(고른 자리는 붉은 테두리와 '여기').
   무엇을 비출지는 buildView()(ui_panels.js)가 그때그때 정한다 — 창을 여닫는 곳마다 상태를 맞추지 않아도 된다.
   덮개는 지도 위에 얹은 2D 캔버스(#spot)다: 땅·부대·성·이름표가 한꺼번에 어두워지고 3D 재질은 건드리지 않는다. */
var SPOT = { cv: null, x: null, a: 0, on: false, sig: '', v: null, tok: 0, shown: false, area: '' }, SPOT_DARK = 0.66;
function hexRing(c, r, k) {                                    // 칸의 테두리(화면 좌표 12점: 모서리와 변의 가운데 — 땅의 굴곡을 따라간다)
  var p = hexCenter(c, r), out = [];
  for (var i = 0; i < 12; i++) {
    var a = (30 + 30 * i) * Math.PI / 180, rad = (i % 2 ? SQ3 / 2 : 1) * k, x = p[0] + Math.cos(a) * rad, z = p[1] + Math.sin(a) * rad, q = w2s(x, groundY(x, z), z);
    if (!q) return null;
    out.push(q);
  }
  return out;
}
function ringPath(x, pts) { x.beginPath(); x.moveTo(pts[0][0], pts[0][1]); for (var i = 1; i < pts.length; i++) x.lineTo(pts[i][0], pts[i][1]); x.closePath(); }
function spotCheck() {
  var v = (typeof buildView === 'function') ? buildView() : null, sig = v ? v.sig : '';
  if (sig === SPOT.sig) return;
  var was = SPOT.on, prev = SPOT.v;
  SPOT.sig = sig; SPOT.on = !!v;
  if (v) SPOT.v = v;
  if (was !== SPOT.on) {
    var tok = ++SPOT.tok, a0 = SPOT.a, a1 = v ? 1 : 0;
    anim(v ? 220 : 170, function (t) { if (tok !== SPOT.tok) return; SPOT.a = a0 + (a1 - a0) * t; UI.render = true; }, function () { if (tok === SPOT.tok && !SPOT.on) SPOT.v = null; });
    $('app').classList.toggle('building', SPOT.on);
    if (SPOT.on && typeof talkHide === 'function') talkHide();       // 건설 자리를 볼 때는 앞서 뜬 대화창이 칸을 가리지 않게
  }
  UI.dirty = true;
  if (v) spotCam(v, !was || !prev || prev.b !== v.b, was && prev ? prev.pi : -2);
}
function spotCam(v, fresh, prevPi) {
  var sa = safeArea(), top = sa.top + 2, bottom = sa.bottom - 2, i, area = Math.round(top / 10) + '/' + Math.round(bottom / 10);
  if (fresh || area !== SPOT.area) {                           // 처음 보거나 보이는 영역이 달라졌다(시설 탭 ↔ 고르는 창): 성과 부지 전체가 들어오게
    SPOT.area = area;
    var pts = [[v.b.c, v.b.r]];
    for (i = 0; i < v.b.plots.length; i++) pts.push([v.b.plots[i].c, v.b.plots[i].r]);
    frameHexes(pts, top, bottom, 1.7);
    return;
  }
  if (v.pi < 0 || v.pi === prevPi) return;                     // 같은 영역에서 자리만 바꿨다: 그 칸이 화면 밖일 때만 옮긴다
  var L = null; for (i = 0; i < v.lots.length; i++) if (v.lots[i].i === v.pi) L = v.lots[i];
  if (!L) return;
  var p = hexPos(L.c, L.r), q = w2s(p[0], p[1], p[2]);
  if (!q || q[0] < 30 || q[0] > CW - 30 || q[1] < top + 46 || q[1] > bottom - 24) flyTo(p[0], p[2], Math.max(cam.z, 0.9), (top + bottom + 16) / 2 / Math.max(1, CH), 280);
}
function spotDraw() {
  if (!SPOT.cv) { SPOT.cv = $('spot'); if (!SPOT.cv) return; SPOT.x = SPOT.cv.getContext('2d'); }
  var cvs = SPOT.cv, x = SPOT.x, v = SPOT.v, i;
  if (!v || SPOT.a < 0.004) { if (SPOT.shown) { SPOT.shown = false; cvs.classList.remove('on'); } return; }
  if (!SPOT.shown) { SPOT.shown = true; cvs.classList.add('on'); }
  var pw = Math.round(CW * DPR), ph = Math.round(CH * DPR);
  if (cvs.width !== pw || cvs.height !== ph) { cvs.width = pw; cvs.height = ph; }
  x.setTransform(DPR, 0, 0, DPR, 0, 0); x.globalCompositeOperation = 'source-over'; x.globalAlpha = 1; x.setLineDash([]);
  x.clearRect(0, 0, CW, CH);
  x.fillStyle = 'rgba(20,18,16,' + (SPOT_DARK * SPOT.a).toFixed(3) + ')'; x.fillRect(0, 0, CW, CH);
  var rings = [];
  for (i = 0; i < v.lots.length; i++) rings.push(hexRing(v.lots[i].c, v.lots[i].r, 1));
  var selF = null, selR = null, selQ = null, selU = 0;                                // 고른 시설(시설 창이 떠 있을 때)
  if (v.fi >= 0) for (i = 0; i < v.facs.length; i++) if (v.facs[i].i === v.fi) {
    var sp0 = hexPos(v.facs[i].c, v.facs[i].r), sq0 = w2s(sp0[0], sp0[1], sp0[2]);
    if (sq0) { selF = v.facs[i]; selR = hexRing(selF.c, selF.r, 1); selQ = sq0; selU = pxPerUnit(sq0[2]); }
  }
  x.globalCompositeOperation = 'destination-out'; x.fillStyle = '#000';
  for (i = 0; i < v.lots.length; i++) if (rings[i] && v.lots[i].ok) { ringPath(x, rings[i]); x.fill(); }      // 지을 수 있는 칸만 뚫는다
  if (selF) {                                                                          // 고른 시설은 건물 전체가 환하게(칸보다 조금 넓게, 가장자리는 번지게)
    var gy = selQ[1] - selU * 0.22, gr = selU * 1.34, gg = x.createRadialGradient(selQ[0], gy, gr * 0.5, selQ[0], gy, gr);
    gg.addColorStop(0, 'rgba(0,0,0,1)'); gg.addColorStop(0.7, 'rgba(0,0,0,0.92)'); gg.addColorStop(1, 'rgba(0,0,0,0)');
    x.fillStyle = gg; x.beginPath(); x.arc(selQ[0], gy, gr, 0, 6.2832); x.fill(); x.fillStyle = '#000';
  }
  x.globalCompositeOperation = 'source-over'; x.globalAlpha = SPOT.a; x.lineJoin = 'round'; x.textAlign = 'center'; x.textBaseline = 'middle';
  var facLabels = function () { for (i = 0; i < v.facs.length; i++) {      // 이미 지은 시설: 어둠 속에서도 옆에 무엇이 있는지 번호와 이름으로(빈 부지의 테두리보다 나중에 그린다 — 아래에서 부른다)
    var fp = hexPos(v.facs[i].c, v.facs[i].r), fq = w2s(fp[0], fp[1], fp[2]); if (!fq) continue;
    var fpu = pxPerUnit(fq[2]); if (fpu < 15) continue;
    var fpx = clamp(Math.round(fpu * 0.40), 10, 13), fa = v.facs[i], fon = fa === selF, fly = fq[1] + fpu * (fa.done ? 0.16 : 0.42), fnm = fa.done ? fa.n : fa.n + ' · ' + fa.left;      // v0.20: 짓는 중인 시설의 이름표는 건물의 발치로 내리고(비계를 가리지 않게) 남은 날수를 같은 줄에 적는다(전에는 한 줄 더 — 아래 칸을 덮었다)
    x.font = '700 ' + fpx + 'px ' + FONT_B;
    var ftw = x.measureText(fnm).width, fbr = clamp(fpx * 0.6, 6, 7.8), ftx = fq[0] + fbr + 1.5, fbx = ftx - ftw / 2 - fbr - 2.5;      // 번호 딱지 + 이름: 둘을 합친 것이 칸의 가운데에 오게
    if (fon) { rr(x, fbx - fbr - 4, fly - fpx / 2 - 4.5, ftx + ftw / 2 + 6 - (fbx - fbr - 4), fpx + 9, 3); x.fillStyle = SEAL; x.fill(); x.lineWidth = 1.4; x.strokeStyle = PAPER; x.stroke(); }      // 고른 시설: 이름표가 붉은 딱지가 된다
    x.lineWidth = 3; x.strokeStyle = 'rgba(20,18,16,0.78)';
    x.fillStyle = fon ? '#fff' : (fa.done ? 'rgba(244,239,227,0.96)' : 'rgba(244,239,227,0.8)');
    if (!fon) x.strokeText(fnm, ftx, fly);
    x.fillText(fnm, ftx, fly);
    x.beginPath(); x.arc(fbx, fly, fbr, 0, 6.2832); x.fillStyle = fon ? PAPER : 'rgba(244,239,227,0.95)'; x.fill(); x.lineWidth = 1; x.strokeStyle = fon ? PAPER : INK; x.stroke();      // 번호 딱지(빈 부지의 번호와 같은 차례 — 시설 탭의 줄 앞에도 같은 번호가 있다)
    x.fillStyle = fon ? SEAL : INK; x.font = '900 ' + Math.round(fbr * (fa.no > 9 ? 1.12 : 1.36)) + 'px ' + FONT_D; x.fillText(String(fa.no), fbx, fly + fbr * 0.08);
  } };
  var ord = []; for (i = 0; i < v.lots.length; i++) if (v.lots[i].i !== v.pi) ord.push(i);
  for (i = 0; i < v.lots.length; i++) if (v.lots[i].i === v.pi) ord.push(i);       // 고른 칸은 맨 나중에(옆 칸의 테두리가 '여기' 표를 덮지 않게)
  for (var oi = 0; oi < ord.length; oi++) {
    var L = v.lots[ord[oi]], R = rings[ord[oi]]; if (!R) continue;
    var sel = L.i === v.pi, p = hexPos(L.c, L.r), q = w2s(p[0], p[1], p[2]); if (!q) continue;
    var ppu = pxPerUnit(q[2]);
    ringPath(x, R);
    if (!L.ok) { x.setLineDash([5, 4]); x.lineWidth = 1.4; x.strokeStyle = 'rgba(244,239,227,0.62)'; x.stroke(); x.setLineDash([]); continue; }   // 빈 부지이지만 지금은 못 짓는다
    if (sel) { x.lineWidth = 6.4; x.strokeStyle = PAPER; x.stroke(); x.lineWidth = 3.8; x.strokeStyle = SEAL; x.stroke(); }
    else { x.lineWidth = 2.6; x.strokeStyle = '#e6b63c'; x.stroke(); }
    var rad = clamp(ppu * 0.40, 6.5, 13.5);
    x.beginPath(); x.arc(q[0], q[1], rad, 0, 6.2832); x.fillStyle = sel ? SEAL : PAPER; x.fill(); x.lineWidth = 1.2; x.strokeStyle = sel ? PAPER : INK; x.stroke();
    x.fillStyle = sel ? '#fff' : INK; x.font = '900 ' + Math.round(rad * 1.3) + 'px ' + FONT_D; x.fillText(String(L.n), q[0], q[1] + rad * 0.08);
    if (sel) {                                                 // '여기' 표
      var ty = 1e9; for (var j = 0; j < R.length; j++) ty = Math.min(ty, R[j][1]);
      x.font = '800 12px ' + FONT_B;
      var tw = x.measureText('여기').width + 16, bx = q[0] - tw / 2, by = ty - 31;
      rr(x, bx, by, tw, 22, 3); x.fillStyle = SEAL; x.fill(); x.lineWidth = 1.2; x.strokeStyle = PAPER; x.stroke();
      x.beginPath(); x.moveTo(q[0] - 5.5, by + 21.4); x.lineTo(q[0], by + 28); x.lineTo(q[0] + 5.5, by + 21.4); x.closePath(); x.fillStyle = SEAL; x.fill();
      x.fillStyle = '#fff'; x.fillText('여기', q[0], by + 11.5);
    }
  }
  if (selF && selR) { ringPath(x, selR); x.lineWidth = 6.4; x.strokeStyle = PAPER; x.stroke(); x.lineWidth = 3.8; x.strokeStyle = SEAL; x.stroke(); }      // 고른 시설: 붉은 테두리(이름표는 facLabels 가 붉은 딱지로 그린다 — 위의 칸을 가리는 '여기' 표는 달지 않는다)
  x.textAlign = 'center'; x.textBaseline = 'middle'; facLabels();
  x.globalAlpha = 1;
}

/* ---------- 연출 ---------- */
/* v0.20 지도 위의 붙박이 딱지: 고를 칸마다 글을 띄운다(나갈 자리 · 보낼 성). 화면이 움직이면 따라간다(tick) */
function marksClear() { var ms = UI.marks || []; for (var i = 0; i < ms.length; i++) ms[i].el.remove(); UI.marks = []; }
function marksSet(list) {
  marksClear();
  for (var i = 0; i < list.length; i++) {
    var m = list[i], el = document.createElement('div'); el.className = 'mk ' + (m.cls || ''); el.innerHTML = m.html; el.style.opacity = 0;
    $('fx').appendChild(el); UI.marks.push({ p: hexPos(m.c, m.r), el: el, dy: m.dy || 0 });
  }
  UI.render = true;
}
function anim(dur, step, done) { UI.anims.push({ t0: performance.now(), dur: dur, step: step, done: done }); UI.render = true; }
function floatText(c, r, text, color, delay, big, dy) {
  var el = document.createElement('div'); el.className = 'flt' + (big ? ' big' : ''); el.textContent = text; el.style.color = color || INK; el.style.opacity = 0;
  $('fx').appendChild(el);
  UI.floats.push({ p: hexPos(c, r), el: el, t0: performance.now() + (delay || 0), dur: 1350, dy: dy || 0 }); UI.render = true;
}
function flashHex(c, r, color) {
  var el = document.createElement('div'); el.className = 'ring'; el.style.borderColor = color || INK; el.style.opacity = 0;
  $('fx').appendChild(el);
  UI.floats.push({ p: hexPos(c, r), el: el, t0: performance.now(), dur: 360, ring: true }); UI.render = true;
}
function unitVis(u) { var L = uLeader(u); return { id: u.id, color: G.factions[u.f].color, por: L.por, type: u.type, ratio: u.troops / Math.max(1, u.max), name: L.n }; }
/* 부대 이동 연출 */
function animMove(vis, from, path, done, slow) {
  var pts = [hexPos(from[0], from[1])], i, o = R3.units[vis.id];
  for (i = 0; i < path.length; i++) { var k = path[i], c = k % W; pts.push(hexPos(c, (k - c) / W)); }
  if (!o || !path.length) { if (o) { o.anim = false; o.sig = ''; } UI.hide = -1; if (done) done(); return; }
  UI.busy = true; o.anim = true; o.g.visible = o.ring.visible = true;
  var dur = Math.min(1500, 150 * path.length + 120) * (slow || 1), last = -1, hop = vis.type === 'cav' ? 0.16 : (vis.type === 'ram' || vis.type === 'trans' ? 0.04 : 0.10);
  var mtype = vis.type;
  if (!vis.type) { var uu = UMAP[vis.id]; if (uu) { mtype = uu.type; hop = uu.type === 'cav' ? 0.16 : (uu.type === 'ram' || uu.type === 'trans' ? 0.04 : 0.10); } }
  sfxMove(mtype, dur);
  anim(dur, function (t) {
    var f = t * (pts.length - 1), i2 = Math.min(pts.length - 2, Math.floor(f)), w = f - i2, a = pts[i2], b = pts[i2 + 1];
    var x = a[0] + (b[0] - a[0]) * w, z = a[2] + (b[2] - a[2]) * w, y = groundY(x, z);
    o.g.position.set(x, y + Math.abs(Math.sin(w * Math.PI * 2)) * hop, z); o.ring.position.set(x, y + 0.04, z);
    if (i2 !== last) { last = i2; if (typeof fxDust === 'function') fxDust(a[0], a[1], a[2], 0.8); var nf_ = Math.abs(b[0] - a[0]) > 0.2 ? (b[0] < a[0] ? -1 : 1) : o.face; if (nf_ !== o.face) { o.face = nf_; setSprite(o.sp, o.sp.userData.key, UNIT_W, nf_ < 0); } }
  }, function () {
    var lastK = path[path.length - 1], lc = lastK % W; o.c = lc; o.r = (lastK - lc) / W;
    o.anim = false; o.sig = ''; UI.hide = -1; UI.busy = !!UI.play; requestDraw(); if (done) done();
  });
}

/* ---------- 미니맵 ---------- */
var MINI = { img: null, t: 0 };
function drawMini() {
  var m = $('mini'); if (!m || !G) return;
  var w = m.width, h = m.height, x = m.getContext('2d'), i;
  if (!MINI.img) { MINI.img = new Image(); MINI.img.onload = drawMini; MINI.img.src = MAP3D.mini; }
  if (MINI.img.complete && MINI.img.naturalWidth) x.drawImage(MINI.img, 0, 0, w, h); else { x.fillStyle = '#efe9db'; x.fillRect(0, 0, w, h); }
  var sx = w / MAP3D.WX, sz = h / MAP3D.WZ;
  for (i = 0; i < G.bases.length; i++) {
    var b = G.bases[i], p = hexCenter(b.c, b.r), s = b.kind === 'gate' ? 3 : 5;
    x.fillStyle = b.owner >= 0 ? G.factions[b.owner].color : '#a8a295'; x.fillRect(p[0] * sx - s / 2, p[1] * sz - s / 2, s, s);
    x.strokeStyle = b.owner === G.player ? SEAL : 'rgba(27,26,24,0.8)'; x.lineWidth = b.owner === G.player ? 1.6 : 1; x.strokeRect(p[0] * sx - s / 2, p[1] * sz - s / 2, s, s);
  }
  if (!R3 || !CW) return;
  var ty = groundY(cam.x, cam.y), cs = [planeHit(0, CH * 0.12, ty), planeHit(CW, CH * 0.12, ty), planeHit(CW, CH, ty), planeHit(0, CH, ty)];
  if (cs[0] && cs[1] && cs[2] && cs[3]) {
    x.beginPath(); for (i = 0; i < 4; i++) { if (i) x.lineTo(cs[i][0] * sx, cs[i][1] * sz); else x.moveTo(cs[i][0] * sx, cs[i][1] * sz); }
    x.closePath(); x.lineWidth = 1.6; x.strokeStyle = SEAL; x.stroke();
  }
}
function miniGo(e) {
  var m = $('mini'), rc = m.getBoundingClientRect();
  cam.x = (e.clientX - rc.left) / rc.width * MAP3D.WX; cam.y = (e.clientY - rc.top) / rc.height * MAP3D.WZ + camDist() * 0.12; clampCam();
}

/* ---------- 매 프레임 ---------- */
function tick(now) {
  var i, hot = false;
  for (i = UI.anims.length - 1; i >= 0; i--) {
    var a = UI.anims[i], t = clamp((now - a.t0) / a.dur, 0, 1);
    a.step(t); hot = true;
    if (t >= 1) { UI.anims.splice(i, 1); if (a.done) a.done(); }
  }
  if (R3 && R3.ready) {
    spotCheck();
    var nzm = cam.z >= 1.15; if (nzm !== R3.nameZoom) { R3.nameZoom = nzm; UI.dirty = true; }
    var fzm = cam.z >= 0.5; if (fzm !== R3.faceZoom) { R3.faceZoom = fzm; UI.dirty = true; }
    if (UI.dirty) { UI.dirty = false; syncScene(); UI.render = true; }
    var nf = 0; for (var fk in R3.fires) { nf++; var fg = R3.fires[fk]; for (i = 0; i < fg.children.length; i++) {
        var fch = fg.children[i];
        if (fch.userData.smoke) { var su = ((now / 1700) + fch.userData.smoke * 0.5 + (+fk) * 0.37) % 1; fch.position.set(0.25 * Math.sin(su * 5 + fch.userData.smoke), 1.5 + 1.9 * su, -0.05); fch.scale.set(1.1 + 1.5 * su, 0.9 + 1.2 * su, 1); fch.material.opacity = 0.42 * Math.sin(Math.PI * su); continue; }
        var s = (0.9 + 0.22 * Math.sin(now / 90 + i * 2.1 + (+fk))) * (fch.userData.k || 1); fch.scale.set(1.0 * s, 1.6 * s + 0.2 * Math.sin(now / 57 + i), 1);
      } }
    var nst = 0;
    for (var sid in R3.units) {
      var so = R3.units[sid]; if (!so.stK) continue;
      nst++;
      so.sw.material.rotation = -now / 380 + so.ph;                                                    // 소용돌이가 돈다
      if (so.stK === 'confuse') so.sp.material.rotation = 0.075 * Math.sin(now / 250 + so.ph);          // 혼란: 비틀거린다
      so.st.sp.position.y = so.stY + 0.05 * Math.sin(now / 320 + so.ph);                               // 딱지가 살짝 오르내린다
    }
    if (hot || UI.floats.length || ((nf || nst) && now - (R3.fireT || 0) > 50)) { UI.render = true; R3.fireT = now; }   // 불·상태 표시는 초당 20번만 다시 그린다
    if (UI.render) {
      UI.render = false; applyCam();
      var lk = clamp(0.72 + 0.26 * cam.z, 0.66, 1.12);
      if (R3.labelK !== lk || R3.billboard) {
        R3.labelK = lk; R3.billboard = false;
        var q = R3.cam.quaternion, showU = cam.z >= 0.26, showF = cam.z >= 0.3;
        for (i = 0; i < R3.bases.length; i++) { var bo = R3.bases[i]; if (!bo) continue; bo.g.quaternion.copy(q); labelSize(bo.lab, lk * (cam.z < 0.3 ? 0.82 : 1)); }
        for (var id in R3.units) { var uo = R3.units[id]; uo.g.quaternion.copy(q); labelSize(uo.lab, lk * 0.82); uo.lab.sp.visible = showU; labelSize(uo.fc, lk * 0.92); uo.fc.sp.visible = showU && uo.fcOn; labelSize(uo.st, lk * 0.84); uo.st.sp.visible = showU && uo.stOn; }
        for (var k2 in R3.facs) R3.facs[k2].sp.visible = showF;
        for (var f2 in R3.fires) R3.fires[f2].quaternion.copy(q);
      }
      R3.renderer.render(R3.scene, R3.cam);
      spotDraw();
      if (now - MINI.t > 120) { MINI.t = now; drawMini(); }
    }
    for (i = UI.floats.length - 1; i >= 0; i--) {
      var f = UI.floats[i], ft = (now - f.t0) / f.dur;
      if (ft < 0) continue;
      if (ft >= 1) { f.el.remove(); UI.floats.splice(i, 1); continue; }
      var sp = w2s(f.p[0], f.p[1] + (f.ring ? 0 : 0.9), f.p[2]);
      if (!sp) { f.el.style.opacity = 0; continue; }
      if (f.ring) { var rs = pxPerUnit(sp[2]) * (0.6 + ft * 1.3); f.el.style.cssText += ';width:' + rs + 'px;height:' + rs * 0.62 + 'px;opacity:' + (1 - ft) + ';transform:translate(' + (sp[0] - rs / 2) + 'px,' + (sp[1] - rs * 0.31) + 'px)'; }
      else if (f.stamp) { var ss = ft < 0.12 ? 2.5 - 1.5 * (ft / 0.12) : 1; f.el.style.opacity = ft < 0.05 ? ft / 0.05 : (ft < 0.78 ? 1 : (1 - ft) / 0.22); f.el.style.transform = 'translate(-50%,-50%) translate(' + sp[0] + 'px,' + (sp[1] - 22) + 'px) rotate(-5deg) scale(' + ss.toFixed(3) + ')'; }
      else { var pop = ft < 0.1 ? 0.6 + 4 * ft : 1; f.el.style.opacity = ft < 0.72 ? 1 : (1 - ft) / 0.28; f.el.style.transform = 'translate(-50%,-100%) translate(' + sp[0] + 'px,' + (sp[1] - ft * 34 + (f.dy || 0)) + 'px) scale(' + pop.toFixed(3) + ')'; }
    }
  }
  if (UI.marks && UI.marks.length) for (i = 0; i < UI.marks.length; i++) {
    var mk = UI.marks[i], ms = w2s(mk.p[0], mk.p[1] + 0.05, mk.p[2]);
    if (!ms) { mk.el.style.opacity = 0; continue; }
    mk.el.style.opacity = 1; mk.el.style.transform = 'translate(-50%,-50%) translate(' + ms[0].toFixed(1) + 'px,' + (ms[1] + mk.dy).toFixed(1) + 'px)';
  }
  requestAnimationFrame(tick);
}

/* ---------- 입력 ---------- */
var PT = {}, pinch = null, tapOK = false;
function ptList() { var a = []; for (var k in PT) a.push(PT[k]); return a; }
function pickAt(sx, sy) {
  var g = pickGround(sx, sy), gh = g ? worldToHex(g[0], g[1]) : null, su = selUnit();
  if (gh && su) { var gk = K(gh[0], gh[1]); if ((UI.rc && UI.rc.stop[gk]) || (UI.atk || []).some(function (t) { return K(t.c, t.r) === gk; })) return gh; }
  if (gh && typeof MODAL !== 'undefined' && MODAL && MODAL.pick && MODAL.pick.has(gh[0], gh[1])) return gh;      // v0.20: 고르는 칸은 성의 그림에 가려 있어도 그 칸으로 집는다
  if (gh && SPOT.on && SPOT.v) { var gp = plotAt(gh[0], gh[1]); if (gp && gp.base === SPOT.v.b) return gh; }      // 건설 자리를 보는 중(v0.10.1): 그 거점의 부지는 성의 그림에 가려 있어도 부지로 집는다
  var best = null, bd = 1e9;
  function test(c, r, sp, pri) {
    var p = hexPos(c, r), s = w2s(p[0], p[1], p[2]); if (!s) return;
    var ppu = pxPerUnit(s[2]), ud = sp.userData, hw = ud.w * ppu * 0.40, top = s[1] - ud.top * ppu * 0.86, bot = s[1] + ud.h * ud.ay * ppu * 0.8;
    if (sx < s[0] - hw || sx > s[0] + hw || sy < top || sy > bot) return;
    var d = Math.abs(sx - s[0]) + Math.abs(sy - (top + bot) / 2) - pri * 40;
    if (d < bd) { bd = d; best = [c, r]; }
  }
  for (var id in R3.units) { var o = R3.units[id], u = UMAP[id]; if (u && o.g.visible) test(u.c, u.r, o.sp, 1); }
  for (var i = 0; i < G.bases.length; i++) if (R3.bases[i]) test(G.bases[i].c, G.bases[i].r, R3.bases[i].sp, 0.5);
  return best || gh;
}
function initInput() {
  if (typeof ResizeObserver === 'function') { var ro = new ResizeObserver(settleSoon); ['sheet', 'bar', 'play', 'hud'].forEach(function (id) { if ($(id)) ro.observe($(id)); }); }
  cv.addEventListener('pointerdown', function (e) {
    audioInit(); bgmKick();
    try { cv.setPointerCapture(e.pointerId); } catch (er) { /* */ }
    PT[e.pointerId] = { x: e.clientX, y: e.clientY, sx: e.clientX, sy: e.clientY, t: performance.now(), moved: false };
    var a = ptList();
    if (a.length === 2) { pinch = { d: Math.hypot(a[0].x - a[1].x, a[0].y - a[1].y) || 1, z: cam.z }; a[0].moved = a[1].moved = true; }
  });
  cv.addEventListener('pointermove', function (e) {
    var p = PT[e.pointerId]; if (!p || !R3) return;
    var rect = cv.getBoundingClientRect(), ox = p.x - rect.left, oy = p.y - rect.top, nx = e.clientX - rect.left, ny = e.clientY - rect.top;
    p.x = e.clientX; p.y = e.clientY;
    var a = ptList();
    if (a.length >= 2 && pinch) {
      var d = Math.hypot(a[0].x - a[1].x, a[0].y - a[1].y) || 1, mx = (a[0].x + a[1].x) / 2 - rect.left, my = (a[0].y + a[1].y) / 2 - rect.top, ty = groundY(cam.x, cam.y);
      var before = planeHit(mx, my, ty);
      cam.z = clamp(pinch.z * d / pinch.d, Z_MIN, Z_MAX); applyCam();
      var after = planeHit(mx, my, ty);
      if (before && after) { cam.x += before[0] - after[0]; cam.y += before[1] - after[1]; }
      clampCam(); return;
    }
    if (!p.moved && Math.hypot(e.clientX - p.sx, e.clientY - p.sy) > 8) p.moved = true;
    if (p.moved) {
      var ty2 = groundY(cam.x, cam.y), h0 = planeHit(ox, oy, ty2), h1 = planeHit(nx, ny, ty2);
      if (h0 && h1) { cam.x += h0[0] - h1[0]; cam.y += h0[1] - h1[1]; clampCam(); }
    }
  });
  function up(e) {
    var p = PT[e.pointerId]; if (!p) return;
    delete PT[e.pointerId];
    if (ptList().length < 2) pinch = null;
    tapOK = (e.type === 'pointerup' && !p.moved && performance.now() - p.t < 700 && ptList().length === 0);
  }
  cv.addEventListener('pointerup', up); cv.addEventListener('pointercancel', up);
  cv.addEventListener('click', function (e) {             // 탭은 click 에서(유령 클릭이 새 창을 누르지 않게)
    bgmKick();
    if (!tapOK || !R3 || !R3.ready || !G) return;
    tapOK = false;
    if (UI.play) { playNudge(); return; }                 // 재생 중에는 화면을 누르면 다음 장면으로
    var rect = cv.getBoundingClientRect(), h = pickAt(e.clientX - rect.left, e.clientY - rect.top);
    if (h) onTap(h[0], h[1]);
  });
  cv.addEventListener('wheel', function (e) {
    e.preventDefault(); if (!R3) return;
    var rect = cv.getBoundingClientRect(), mx = e.clientX - rect.left, my = e.clientY - rect.top, ty = groundY(cam.x, cam.y), before = planeHit(mx, my, ty);
    cam.z = clamp(cam.z * (e.deltaY < 0 ? 1.15 : 1 / 1.15), Z_MIN, Z_MAX); applyCam();
    var after = planeHit(mx, my, ty);
    if (before && after) { cam.x += before[0] - after[0]; cam.y += before[1] - after[1]; }
    clampCam();
  }, { passive: false });
  var mini = $('mini'), md = false;
  mini.addEventListener('pointerdown', function (e) { md = true; try { mini.setPointerCapture(e.pointerId); } catch (er) { /* */ } miniGo(e); });
  mini.addEventListener('pointermove', function (e) { if (md) miniGo(e); });
  mini.addEventListener('pointerup', function () { md = false; }); mini.addEventListener('pointercancel', function () { md = false; });
  window.addEventListener('resize', resize);
}

/* ---------- 소리 ----------
   효과음은 녹음된 소리다(src/sfxdata.js 의 SFX_DATA — 짧은 mp3 를 base64 로 담은 것). 처음 누를 때 풀어 둔다.
   아직 풀리지 않았거나 풀지 못한 소리만 예전의 만든 소리(잡음 + 사인파)로 대신한다. */
var AC = null, NOISE = null;
var SND = { buf: {}, off: {}, last: {}, bus: null, loaded: false, mv: null };
/* 장면 → 낼 소리들 [표본, 크기, 음높이 흔들림, 늦춤(초)]. gap = 같은 장면 소리를 다시 낼 수 있는 가장 짧은 간격(ms). syn = 표본이 없을 때 대신할 만든 소리 */
var CUES = {
  ui:       { s: [['tick', 0.5, 0.06]], gap: 50, syn: 'ui' },
  page:     { s: [['page', 0.55, 0.05]], gap: 150, syn: 'ui' },
  step:     { s: [['stomp', 0.5, 0.08]], gap: 60, syn: 'step' },
  hit:      { s: [['slash', 0.8, 0.06]], gap: 70, syn: 'hit' },
  counter:  { s: [['slash', 0.5, 0.05]], gap: 70, syn: 'hit' },
  arrowhit: { s: [['thock', 0.75, 0.1]], gap: 70, syn: 'hit' },                                   // 화살 한 차례가 박힌다(v0.12 — 전에는 thud)
  arrowbig: { s: [['arrowland', 0.95, 0.05]], gap: 120, syn: 'big' },                            // 쏘는 전법 · 크게 맞음: 후두둑
  arrowgreat: { s: [['arrowland', 1.0, 0.04], ['thock', 0.6, 0.04, 0.12], ['gong', 0.3, 0, 0.1]], gap: 200, syn: 'big' },
  arrowfail: { s: [['thock', 0.4, 0.14], ['thock', 0.3, 0.14, 0.11]], gap: 120, syn: 'fail' },      // 빗나간 살 몇 대
  siege:    { s: [['crush', 0.6, 0.05], ['thud', 0.7, 0.05, 0.03]], gap: 120, syn: 'hit' },
  big:      { s: [['crush', 0.95, 0.04], ['clang', 0.55, 0.05, 0.03]], gap: 120, syn: 'big' },
  great:    { s: [['crush', 1.0, 0.03], ['clang', 0.75, 0.04, 0.02], ['gong', 0.3, 0, 0.06]], gap: 200, syn: 'big' },
  fail:     { s: [['clang', 0.5, 0.05], ['thud', 0.55, 0.05, 0.03]], gap: 120, syn: 'fail' },
  miss:     { s: [['thud', 0.6, 0.05]], gap: 120, syn: 'fail' },
  fire:     { s: [['fire', 0.8, 0.04]], gap: 300, syn: 'fire' },
  douse:    { s: [['douse', 0.8, 0.03]], gap: 300, syn: 'fire' },
  wind:     { s: [['wind', 0.7, 0.04]], gap: 300, syn: 'fail' },
  drum:     { s: [['drum', 0.85, 0.03]], gap: 150, syn: 'drum' },
  drums:    { s: [['drums', 0.9, 0.02]], gap: 400, syn: 'drum' },
  horn:     { s: [['horn', 0.7, 0.01]], gap: 800, syn: 'drum' },
  deploy:   { s: [['drums', 0.85, 0.02], ['horn', 0.42, 0.01, 0.9]], gap: 600, syn: 'drum' },      // v0.18: 북 "둥 — 둥 — 둥둥둥"의 마지막 센 박에 뿔나팔
  gong:     { s: [['gong', 0.8, 0.01]], gap: 500, syn: 'drum' },
  fall:     { s: [['fall', 0.95, 0]], gap: 3500, syn: 'fall' },          // 함락 장면이 곧바로 한 번 더 불러도 겹치지 않게
  cheerlate: { s: [['cheer', 0.6, 0.02, 1.0]], gap: 3500, syn: '' },
  cheer:    { s: [['cheer', 0.7, 0.02]], gap: 800, syn: 'drum' },
  rout:     { s: [['rout', 0.7, 0.03]], gap: 500, syn: 'big' },
  coin:     { s: [['coin', 0.7, 0.03]], gap: 200, syn: 'ui' },
  hammer:   { s: [['hammer', 0.8, 0.03]], gap: 300, syn: 'drum' },
  duel:     { s: [['duel', 0.95, 0.02]], gap: 800, syn: 'big' },
  shout:    { s: [['shout', 0.6, 0.05]], gap: 250, syn: '' },
  bow:      { s: [['bow', 0.8, 0.08]], gap: 60, syn: 'ui' },                                       // v0.12: 새로 만든 소리(시위 울림 + 바람 가르는 소리)
  arrows:   { s: [['arrows', 0.8, 0.04]], gap: 200, syn: 'step' },
  charge:   { s: [['cavalry', 0.85, 0.03]], gap: 500, syn: 'step' }
};
function acMake() {
  if (AC) return AC;
  try {
    AC = new (window.AudioContext || window.webkitAudioContext)();
    var n = AC.sampleRate, b = AC.createBuffer(1, n, AC.sampleRate), d = b.getChannelData(0);
    for (var i = 0; i < n; i++) d[i] = Math.random() * 2 - 1;
    NOISE = b;
  } catch (e) { AC = null; }
  return AC;
}
function audioInit() { if (!UI.sound || !acMake()) return; sndLoad(); }
function sndBus() {                                           // 여러 소리가 겹쳐도 찢어지지 않게 한데 모아 누른다
  if (!SND.bus) {
    var g = AC.createGain(); g.gain.value = 0.9;
    try {
      var c = AC.createDynamicsCompressor();
      c.threshold.value = -10; c.knee.value = 8; c.ratio.value = 6; c.attack.value = 0.003; c.release.value = 0.2;
      g.connect(c); c.connect(AC.destination);
    } catch (e) { g.connect(AC.destination); }
    SND.bus = g;
  }
  return SND.bus;
}
function sndLoad() {
  if (SND.loaded || typeof SFX_DATA === 'undefined' || !AC) return;
  SND.loaded = true;
  Object.keys(SFX_DATA).forEach(function (k) {
    try {
      var bin = atob(SFX_DATA[k]), u8 = new Uint8Array(bin.length), i;
      for (i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
      var ok = function (b) {
        // mp3 를 풀면 앞에 짧은 무음이 붙는다 → 소리가 시작되는 곳부터 틀어 누른 순간과 맞춘다(최대 60ms)
        var d = b.getChannelData(0), lim = Math.min(d.length, Math.floor(b.sampleRate * 0.06)), j = 0;
        while (j < lim && Math.abs(d[j]) < 0.02) j++;
        SND.off[k] = j >= lim ? 0 : Math.max(0, j / b.sampleRate - 0.002);
        SND.buf[k] = b;
      }, bad = function () { /* 이 소리는 만든 소리로 대신한다 */ };
      var pr = AC.decodeAudioData(u8.buffer, ok, bad);
      if (pr && pr.catch) pr.catch(bad);
    } catch (e) { /* */ }
  });
}
function sndPlay(name, vol, jit, delay) {
  var b = SND.buf[name]; if (!b) return null;
  var s = AC.createBufferSource(); s.buffer = b;
  if (jit) s.playbackRate.value = 1 + (Math.random() * 2 - 1) * jit;
  var g = AC.createGain(); g.gain.value = vol;
  s.connect(g); g.connect(sndBus());
  s.start(AC.currentTime + (delay || 0), SND.off[name] || 0);
  return { s: s, g: g };
}
function nz(t, dur, type, freq, q, vol) {
  var s = AC.createBufferSource(); s.buffer = NOISE; s.loop = true;
  var f = AC.createBiquadFilter(); f.type = type; f.frequency.value = freq; f.Q.value = q;
  var g = AC.createGain(); g.gain.setValueAtTime(vol, t); g.gain.exponentialRampToValueAtTime(0.001, t + dur);
  s.connect(f); f.connect(g); g.connect(AC.destination); s.start(t, Math.random() * 0.5); s.stop(t + dur + 0.02);
}
function thump(t, f0, f1, dur, vol) {
  var o = AC.createOscillator(); o.type = 'sine'; o.frequency.setValueAtTime(f0, t); o.frequency.exponentialRampToValueAtTime(f1, t + dur);
  var g = AC.createGain(); g.gain.setValueAtTime(vol, t); g.gain.exponentialRampToValueAtTime(0.001, t + dur);
  o.connect(g); g.connect(AC.destination); o.start(t); o.stop(t + dur + 0.02);
}
/* v0.21 뜯는 현 한 음(성공 · 실패의 가벼운 소리): 빠르게 서고 길게 스러지는 음 + 옅은 배음 */
function pluck(t, freq, dur, vol) {
  var out = (typeof sndBus === 'function') ? sndBus() : AC.destination;
  [[1, 1, 'triangle'], [2, 0.28, 'sine'], [3, 0.10, 'sine']].forEach(function (h) {
    var o = AC.createOscillator(); o.type = h[2]; o.frequency.setValueAtTime(freq * h[0], t);
    var g = AC.createGain(); g.gain.setValueAtTime(0.0001, t); g.gain.linearRampToValueAtTime(vol * h[1], t + 0.008); g.gain.exponentialRampToValueAtTime(0.0008, t + dur / h[0]);
    o.connect(g); g.connect(out); o.start(t); o.stop(t + dur / h[0] + 0.03);
  });
}
function sfxSyn(kind) {                                       // 만든 소리(대신 쓰는 것)
  var t = AC.currentTime;
  if (kind === 'step') nz(t, 0.06, 'lowpass', 420, 0.7, 0.10);
  else if (kind === 'ui') nz(t, 0.035, 'bandpass', 1900, 1.2, 0.06);
  else if (kind === 'hit') { nz(t, 0.16, 'bandpass', 1100, 0.9, 0.34); nz(t + 0.03, 0.22, 'lowpass', 300, 0.7, 0.3); thump(t, 120, 48, 0.18, 0.5); }
  else if (kind === 'big') { nz(t, 0.3, 'bandpass', 800, 0.7, 0.45); thump(t, 110, 38, 0.4, 0.8); nz(t + 0.08, 0.5, 'lowpass', 220, 0.6, 0.4); }
  else if (kind === 'fire') { nz(t, 0.7, 'bandpass', 2600, 0.6, 0.16); nz(t, 0.9, 'lowpass', 500, 0.5, 0.18); }
  else if (kind === 'drum') { thump(t, 95, 42, 0.5, 0.8); nz(t, 0.12, 'lowpass', 260, 0.7, 0.25); }
  else if (kind === 'fall') { thump(t, 95, 40, 0.5, 0.8); thump(t + 0.28, 95, 40, 0.6, 0.8); nz(t, 0.9, 'lowpass', 350, 0.6, 0.3); }
  else if (kind === 'fail') nz(t, 0.2, 'lowpass', 240, 0.8, 0.2);
  else if (kind === 'good') { pluck(t, 783.99, 0.55, 0.16); pluck(t + 0.12, 1174.66, 0.85, 0.18); }                     // 솔 → 레: 맑게 올라간다
  else if (kind === 'bad') { pluck(t, 293.66, 0.42, 0.17); pluck(t + 0.15, 220.0, 0.70, 0.17); nz(t, 0.09, 'lowpass', 280, 0.7, 0.07); }   // 레 → 라: 낮게 내려간다
}
function sfx(kind) {
  if (!AC || !UI.sound) return;
  try {
    if (AC.state === 'suspended') AC.resume();
    var q = CUES[kind];
    if (!q) { sfxSyn(kind); return; }
    var now = performance.now();
    if (now - (SND.last[kind] || 0) < q.gap) return;
    SND.last[kind] = now;
    var n = 0;
    for (var i = 0; i < q.s.length; i++) if (sndPlay(q.s[i][0], q.s[i][1], q.s[i][2], q.s[i][3])) n++;
    if (!n && q.syn) sfxSyn(q.syn);
  } catch (e) { /* 소리는 없어도 된다 */ }
}
/* 부대가 움직이는 동안의 소리: 보병은 발소리, 기병은 말발굽, 충차·수송대는 수레. ms 뒤에 잦아든다 */
function sfxMoveStop(quick) {
  var m = SND.mv; SND.mv = null;
  if (!m || !AC) return;
  try { var t = AC.currentTime; m.g.gain.cancelScheduledValues(t); m.g.gain.setValueAtTime(Math.max(0.0001, m.g.gain.value), t); m.g.gain.exponentialRampToValueAtTime(0.0001, t + (quick ? 0.05 : 0.14)); m.s.stop(t + 0.2); } catch (e) { /* */ }
}
function sfxMove(type, ms) {
  if (!AC || !UI.sound) return;
  try {
    if (AC.state === 'suspended') AC.resume();
    sfxMoveStop(true);
    var name = type === 'cav' ? 'gallop' : (type === 'ram' || type === 'trans' ? 'cart' : 'march'), b = SND.buf[name];
    if (!b) { sfxSyn('step'); return; }
    var s = AC.createBufferSource(), g = AC.createGain(), t = AC.currentTime, dur = Math.max(0.25, ms / 1000), off = SND.off[name] || 0, vol = name === 'cart' ? 0.55 : 0.5;
    s.buffer = b; s.playbackRate.value = 1 + (Math.random() * 2 - 1) * 0.04;
    if (dur > b.duration - off - 0.3) { s.loop = true; s.loopStart = off + 0.05; s.loopEnd = Math.max(off + 0.4, b.duration - 0.45); }   // 길게 가면 가운데 토막을 되풀이
    g.gain.setValueAtTime(vol, t); g.gain.setValueAtTime(vol, t + Math.max(0.05, dur - 0.16)); g.gain.exponentialRampToValueAtTime(0.0001, t + dur + 0.06);
    s.connect(g); g.connect(sndBus()); s.start(t, off); s.stop(t + dur + 0.1);
    var m = { s: s, g: g }; SND.mv = m;
    s.onended = function () { if (SND.mv === m) SND.mv = null; };
  } catch (e) { /* */ }
}

/* ---------- 배경 음악 ----------
   1) 같이 놓인 bgm/<곡>.mp3 를 튼다. 장면(제목·평시·긴장·전투·승리·패배)마다 곡이 정해져 있고, 여러 곡이면 차례로 돌아간다.
   2) 파일이 없거나 틀 수 없으면 코드로 만든 음악을 튼다: 뜯는 현(Karplus–Strong), 피리, 북, 낮게 깔리는 현. 오음 음계. */
var BGM_TRACKS = { title: ['title'], field: ['field1', 'field2'], tense: ['tense'], battle: ['battle1', 'battle2'], victory: ['victory'], defeat: ['defeat'] };
var BGM = { el: null, name: '', want: '', vol: 0.5, dead: {}, tok: 0, mode: '', idx: {}, file: '' };
var SYN = { g: null, timer: 0, t: 0, step: 0, style: null, name: '', bufs: {}, pad: null, last: 5, hold: 0 };
var SCALE_MAJ = [0, 2, 4, 7, 9], SCALE_MIN = [0, 3, 5, 7, 10];
var SYN_STYLE = {
  title:   { bpm: 56,  base: 293.66, pad: 73.42, sc: SCALE_MAJ, gain: 2.8 },
  field:   { bpm: 66,  base: 329.63, pad: 82.41, sc: SCALE_MAJ, gain: 3.0 },
  battle:  { bpm: 112, base: 293.66, pad: 73.42, sc: SCALE_MIN, gain: 1.5 },
  victory: { bpm: 80,  base: 392.00, pad: 98.00, sc: SCALE_MAJ, gain: 2.6 },
  defeat:  { bpm: 46,  base: 261.63, pad: 65.41, sc: SCALE_MIN, gain: 3.0 }
};
function synBus(ctx) {                      // 음악 버스: 음량 → 컴프레서 → 출력
  var g = ctx.createGain(), c = ctx.createDynamicsCompressor();
  c.threshold.value = -15; c.knee.value = 8; c.ratio.value = 4; c.attack.value = 0.008; c.release.value = 0.25;
  g.connect(c); c.connect(ctx.destination);
  return g;
}
function noteHz(st, deg) { var o = Math.floor(deg / 5), d = ((deg % 5) + 5) % 5; return st.base * Math.pow(2, o + st.sc[d] / 12); }
function ksBuf(hz) {
  var key = Math.round(hz * 4); if (SYN.bufs[key]) return SYN.bufs[key];
  var sr = AC.sampleRate, n = Math.floor(sr * 2.4), b = AC.createBuffer(1, n, sr), d = b.getChannelData(0), N = Math.max(2, Math.round(sr / hz)), ring = new Float32Array(N), i, k = 0, lp = 0;
  var damp = hz > 600 ? 0.9925 : (hz > 250 ? 0.995 : 0.9968);
  for (i = 0; i < N; i++) { lp += ((Math.random() * 2 - 1) - lp) * 0.5; ring[i] = lp; }           // 둥글린 초기 잡음 → 부드러운 음색
  for (i = 0; i < n; i++) { var j = k + 1 === N ? 0 : k + 1, y = ring[k]; d[i] = y; ring[k] = (y + ring[j]) * 0.5 * damp; k = j; }
  for (i = 0; i < 3000 && i < n; i++) d[n - 1 - i] *= i / 3000;
  return (SYN.bufs[key] = b);
}
function synOut(node, pan) {
  if (pan && AC.createStereoPanner) { var p = AC.createStereoPanner(); p.pan.value = pan; node.connect(p); p.connect(SYN.g); } else node.connect(SYN.g);
}
function pluck(t, hz, vol, pan) {
  var s = AC.createBufferSource(); s.buffer = ksBuf(hz);
  var g = AC.createGain(); g.gain.value = vol; s.connect(g); synOut(g, pan); s.start(t);
}
function flute(t, hz, dur, vol) {
  var o = AC.createOscillator(); o.type = 'triangle'; o.frequency.setValueAtTime(hz, t);
  var l = AC.createOscillator(); l.frequency.value = 5.1;
  var lg = AC.createGain(); lg.gain.setValueAtTime(0, t); lg.gain.linearRampToValueAtTime(hz * 0.007, t + dur * 0.6); l.connect(lg); lg.connect(o.frequency);
  var f = AC.createBiquadFilter(); f.type = 'lowpass'; f.frequency.value = hz * 2.4;
  var g = AC.createGain(); g.gain.setValueAtTime(0.0001, t); g.gain.linearRampToValueAtTime(vol, t + 0.14); g.gain.setValueAtTime(vol, t + dur * 0.72); g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
  o.connect(f); f.connect(g); synOut(g, 0.15); o.start(t); l.start(t); o.stop(t + dur + 0.05); l.stop(t + dur + 0.05);
  var s = AC.createBufferSource(); s.buffer = NOISE; s.loop = true;                               // 숨소리
  var bf = AC.createBiquadFilter(); bf.type = 'bandpass'; bf.frequency.value = hz * 2; bf.Q.value = 2;
  var bg = AC.createGain(); bg.gain.setValueAtTime(0.0001, t); bg.gain.linearRampToValueAtTime(vol * 0.10, t + 0.1); bg.gain.exponentialRampToValueAtTime(0.0001, t + dur);
  s.connect(bf); bf.connect(bg); synOut(bg, 0.15); s.start(t); s.stop(t + dur + 0.05);
}
function drum(t, vol, low) {
  var o = AC.createOscillator(); o.type = 'sine'; o.frequency.setValueAtTime(low ? 88 : 135, t); o.frequency.exponentialRampToValueAtTime(low ? 38 : 62, t + 0.26);
  var g = AC.createGain(); g.gain.setValueAtTime(vol, t); g.gain.exponentialRampToValueAtTime(0.001, t + (low ? 0.55 : 0.28));
  o.connect(g); g.connect(SYN.g); o.start(t); o.stop(t + 0.62);
  var s = AC.createBufferSource(); s.buffer = NOISE; var f = AC.createBiquadFilter(); f.type = 'lowpass'; f.frequency.value = low ? 320 : 1100;
  var g2 = AC.createGain(); g2.gain.setValueAtTime(vol * 0.45, t); g2.gain.exponentialRampToValueAtTime(0.001, t + 0.11);
  s.connect(f); f.connect(g2); g2.connect(SYN.g); s.start(t, Math.random() * 0.5); s.stop(t + 0.14);
}
function padOn(hz, level) {
  var out = AC.createGain(); out.gain.value = 0.0001;
  var f = AC.createBiquadFilter(); f.type = 'lowpass'; f.frequency.value = 380; f.Q.value = 0.4;
  var os = [hz, hz * 1.004, hz * 1.5, hz * 2.006].map(function (h, i) { var o = AC.createOscillator(); o.type = 'sawtooth'; o.frequency.value = h; var g = AC.createGain(); g.gain.value = i < 2 ? 0.5 : 0.2; o.connect(g); g.connect(f); o.start(); return o; });
  f.connect(out); out.connect(SYN.g); out.gain.exponentialRampToValueAtTime(level, AC.currentTime + 3.5);
  return { out: out, os: os };
}
function padOff(p) {
  var t = AC.currentTime;
  try { p.out.gain.cancelScheduledValues(t); p.out.gain.setValueAtTime(Math.max(0.0001, p.out.gain.value), t); p.out.gain.exponentialRampToValueAtTime(0.0001, t + 1.2); p.os.forEach(function (o) { o.stop(t + 1.3); }); } catch (e) { /* */ }
}
function rint(n) { return Math.floor(Math.random() * n); }
function walk(lo, hi) { SYN.last = clamp(SYN.last + [-2, -1, -1, 0, 1, 1, 2][rint(7)], lo, hi); return SYN.last; }
function synStep(name, s, t, st) {
  var b16 = s % 16, b32 = s % 32;
  if (name === 'battle') {
    var pat = [1, 0, 2, 2, 1, 0, 2, 1][s % 8];
    if (pat === 1) drum(t, 0.62, true); else if (pat === 2) drum(t, 0.26, false);
    pluck(t, noteHz(st, (s % 4 === 2 ? -3 : -5)) / 2, 0.20, -0.2);                                   // 낮은 현의 되풀이
    if (b32 === 30 || b32 === 31) { pluck(t, noteHz(st, 5 + (b32 - 30) * 2), 0.20, 0.3); pluck(t + 60 / st.bpm / 4, noteHz(st, 6 + (b32 - 30) * 2), 0.18, 0.3); }
    else if (Math.random() < (s % 2 ? 0.22 : 0.42)) pluck(t, noteHz(st, walk(2, 11)), 0.24, 0.25);
    if (b32 === 0) flute(t, noteHz(st, [5, 7, 4, 8][Math.floor(s / 32) % 4]), 60 / st.bpm * 6, 0.07);
    return;
  }
  if (name === 'title' || name === 'defeat') {
    if (b16 === 0) pluck(t, noteHz(st, -5) / 2, 0.30, -0.15);
    if (b16 === 8 && name === 'title') pluck(t, noteHz(st, -2) / 2, 0.22, -0.15);
    if (s >= SYN.hold && s % 2 === 0 && Math.random() < 0.72) { var beats = [2, 3, 3, 4, 6][rint(5)], dg = name === 'defeat' ? walk(-2, 5) : walk(0, 8); flute(t, noteHz(st, dg), 60 / st.bpm * beats * 0.95, 0.085); SYN.hold = s + beats * 2; }
    if (s % 2 === 1 && Math.random() < 0.22) pluck(t, noteHz(st, [0, 2, 4, 5, 7][rint(5)]), 0.14, 0.3);
    if (b32 === 0 && name === 'title') drum(t, 0.22, true);
    return;
  }
  // 평시·승리: 뜯는 현의 가락
  if (name === 'victory' && s < 10) { pluck(t, noteHz(st, s), 0.26, 0.2); if (s === 0) drum(t, 0.5, true); return; }
  if (b16 === 0) pluck(t, noteHz(st, -5) / 2, 0.30, -0.2);
  else if (b16 === 8) pluck(t, noteHz(st, -2) / 2, 0.24, -0.2);
  else if (b16 === 12 && Math.random() < 0.5) pluck(t, noteHz(st, -3) / 2, 0.18, -0.2);
  if (b32 === 28) { SYN.last = [0, 5, 2][rint(3)]; pluck(t, noteHz(st, SYN.last), 0.26, 0.25); }      // 구절 끝은 으뜸음 쪽으로
  else if (b32 < 28 && Math.random() < (s % 2 ? 0.34 : 0.64)) {
    var d2 = walk(0, 10); pluck(t, noteHz(st, d2), 0.24 - d2 * 0.006, 0.25);
    if (Math.random() < 0.16) pluck(t + 0.02, noteHz(st, d2 - 2), 0.12, 0.35);
  }
  if (b32 === 16 && Math.random() < 0.6) flute(t, noteHz(st, [5, 4, 7, 2][rint(4)]), 60 / st.bpm * 5, 0.05);
  if (b32 === 0) drum(t, 0.16, true);
}
function synTick() {
  if (!AC || !SYN.style || AC.state !== 'running') return;
  var sp = 60 / SYN.style.bpm / 2;
  if (SYN.t < AC.currentTime) SYN.t = AC.currentTime + 0.05;
  while (SYN.t < AC.currentTime + 0.4) { try { synStep(SYN.name, SYN.step, SYN.t, SYN.style); } catch (e) { /* */ } SYN.step++; SYN.t += sp; }
}
function synStart(name) {
  if (!acMake()) return;
  try { if (AC.state === 'suspended') AC.resume(); } catch (e) { /* */ }
  synStop();
  if (!SYN.g) SYN.g = synBus(AC);
  SYN.style = SYN_STYLE[name] || SYN_STYLE.field;
  var t = AC.currentTime; SYN.g.gain.cancelScheduledValues(t); SYN.g.gain.setValueAtTime(0.0001, t + 0.05); SYN.g.gain.exponentialRampToValueAtTime(BGM.vol * SYN.style.gain, t + 1.6); SYN.name = name; SYN.step = 0; SYN.hold = 0; SYN.t = t + 0.2; SYN.last = 5;
  SYN.pad = padOn(SYN.style.pad, name === 'battle' ? 0.07 : 0.05);
  SYN.timer = setInterval(synTick, 110);
  BGM.mode = 'syn';
}
function synStop() {
  if (SYN.timer) { clearInterval(SYN.timer); SYN.timer = 0; }
  if (SYN.pad) { padOff(SYN.pad); SYN.pad = null; }
  SYN.style = null;
}
function bgmEl() {
  if (!BGM.el) { BGM.el = new Audio(); BGM.el.preload = 'auto'; }
  return BGM.el;
}
function bgmFade(a, to, ms, end, tok) {
  var from = a.volume, t0 = performance.now();
  (function step() {
    if (tok !== BGM.tok) return;
    var t = clamp((performance.now() - t0) / ms, 0, 1);
    try { a.volume = from + (to - from) * t; } catch (e) { /* */ }
    if (t < 1) setTimeout(step, 40); else if (end) end();
  })();
}
function playBgm(name, once) {
  BGM.want = name;
  if (!UI.music) { stopBgm(); return; }
  if (BGM.name === name) return;
  var a0 = BGM.el, was = BGM.mode === 'file' && a0 && !a0.paused;
  stopBgm(was);                                            // 틀던 곡이 있으면 끊지 않고 잦아들게 한 뒤 바꾼다
  var tok = BGM.tok; BGM.name = name;
  if (was) bgmFade(a0, 0, 320, function () { bgmTrack(name, once, true, tok); }, tok);
  else bgmTrack(name, once, true, tok);
}
/* 장면의 다음 곡을 튼다. 못 트는 곡은 건너뛰고, 다 못 틀면 만든 음악 */
function bgmTrack(name, once, fadeIn, tok) {
  if (tok !== BGM.tok) return;
  var list = (BGM_TRACKS[name] || [name]).filter(function (f) { return !BGM.dead[f]; });
  if (!list.length) { synStart(SYN_STYLE[name] ? name : 'field'); return; }
  var i = (BGM.idx[name] || 0) % list.length, file = list[i], a = bgmEl();
  BGM.idx[name] = i + 1; BGM.file = file;
  var next = function () { if (tok === BGM.tok && !BGM.dead[file]) { BGM.dead[file] = 1; bgmTrack(name, once, fadeIn, tok); } };
  a.loop = !once && list.length === 1;
  a.onerror = next;                                         // 파일이 없다 → 다음 곡, 없으면 만든 음악
  a.onended = function () { if (tok === BGM.tok && !once) bgmTrack(name, once, false, tok); };
  a.src = 'bgm/' + file + '.mp3';
  try { a.volume = fadeIn ? 0 : BGM.vol; } catch (e) { /* */ }
  var p = a.play();
  if (p && p.then) p.then(function () { if (tok === BGM.tok) { BGM.mode = 'file'; if (fadeIn) bgmFade(a, BGM.vol, 900, null, tok); } })
    .catch(function (e) { if (tok !== BGM.tok) return; if (e && e.name === 'NotAllowedError') { BGM.name = ''; BGM.idx[name] = i; } else if (!e || e.name !== 'AbortError') next(); });
}
function stopBgm(keep) {
  BGM.tok++; BGM.name = ''; BGM.mode = '';
  var a = BGM.el; if (a) { a.onerror = null; a.onended = null; if (!keep) { try { a.pause(); } catch (e) { /* */ } } }
  if (SYN.g && AC) { var t = AC.currentTime; try { SYN.g.gain.cancelScheduledValues(t); SYN.g.gain.setValueAtTime(Math.max(0.0001, SYN.g.gain.value), t); SYN.g.gain.exponentialRampToValueAtTime(0.0001, t + 0.5); } catch (e) { /* */ } }
  synStop();
}
function bgmKick() { if (UI.music && BGM.want && !BGM.name) playBgm(BGM.want); }   // 첫 조작 뒤에야 소리를 낼 수 있다
document.addEventListener('visibilitychange', function () {
  try { if (document.hidden) { if (AC && AC.state === 'running') AC.suspend(); if (BGM.el && BGM.mode === 'file') BGM.el.pause(); } else { if (AC && (UI.sound || UI.music)) AC.resume(); if (BGM.el && BGM.mode === 'file' && UI.music) BGM.el.play(); } } catch (e) { /* */ }
});
