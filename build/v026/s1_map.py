# -*- coding: utf-8 -*-
"""v0.26: 가까이 당겼을 때의 바탕 그림 — 4배로 키운 그림을 조각으로 받아 그 자리에 겹친다.
  요청: (11-25 21:30) "맵을 확대하면 맵이 깨져보이거나 뭉개지는데, 완성도가 떨어져보이는데 방법이 없을까"
        (23:24) "지도 확대 개선도 필요한데 확대가 안되게 하는 a 안은 절대 안된다고 하면 뭘로하겠어?"   (23:41) "b 로해"
  b = 바탕 그림을 4배로 키워(업스케일) 조각으로 나누고, 가까이 당긴 곳의 조각만 받아 온다. 그림은 tools/map4.py 가 만든다(art/map4/tiles).
  여기서는: 지형 셰이더에 조각 넷의 자리(HITILE) · 조각을 고르고 받아 오는 일(hiTick) · 앱(PWA)의 서비스 워커가 조각을 저장해 두는 일.
   python3 build/v026/s1_map.py   (apply.sh 가 v0.25 백업에서 되돌린 뒤 부른다)"""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)


def rep(s, a, b, n=1):
    assert s.count(a) == n, (a[:70], s.count(a))
    return s.replace(a, b)


d = rd('src/data.js')
d = rep(d, "var GAME_VERSION = 'v0.25';", "var GAME_VERSION = 'v0.26';")
wr('src/data.js', d)

g = rd('src/ui3d.js')
# ───────── 셰이더: 조각 넷 ─────────
g = rep(g, "  '#endif',\n  'void main(){',\n  '  float od = length(max(max(-vW, vW - edge.xy), 0.0)), inMap",
        "  '#endif',\n"
        "  '#ifdef HITILE',                                                                                       // v0.26: 가까이 당겼을 때 그 자리만 받아 오는 4배 바탕 그림(조각 넷까지 — 아래 hiTick)\n"
        "  'uniform sampler2D hiT0; uniform sampler2D hiT1; uniform sampler2D hiT2; uniform sampler2D hiT3; uniform vec4 hiR0; uniform vec4 hiR1; uniform vec4 hiR2; uniform vec4 hiR3; uniform vec4 hiK; uniform vec2 hiF;',\n"
        "  'vec4 hiS(sampler2D t, vec4 r, vec2 uv, float k){ vec2 q = (uv - r.xy) * r.zw; vec2 e = min(q, 1.0 - q) / hiF; return vec4(texture2D(t, clamp(q, 0.0, 1.0)).rgb, k * clamp(min(e.x, e.y), 0.0, 1.0)); }',   // 조각의 빛깔 + 얼마나 겹칠지(조각 밖 0 · 가장자리에서 스민다)\n"
        "  '#endif',\n"
        "  'void main(){',\n  '  float od = length(max(max(-vW, vW - edge.xy), 0.0)), inMap")
g = rep(g, "  '#endif',\n  '  float dn = texture2D(detail, vW * 0.21).r, dn2 = texture2D(detail, vW * 1.17 + 0.37).g;',",
        "  '#endif',\n"
        "  '#ifdef HITILE',\n"
        "  '  vec2 tuv = clamp(vUv, 0.0, 1.0); float hin = step(eo, 0.0);',                                        // 지도 안에서만\n"
        "  '  vec4 h0 = hiS(hiT0, hiR0, tuv, hiK.x), h1 = hiS(hiT1, hiR1, tuv, hiK.y), h2 = hiS(hiT2, hiR2, tuv, hiK.z), h3 = hiS(hiT3, hiR3, tuv, hiK.w);',\n"
        "  '  col = mix(col, h0.rgb, h0.a * hin); col = mix(col, h1.rgb, h1.a * hin); col = mix(col, h2.rgb, h2.a * hin); col = mix(col, h3.rgb, h3.a * hin);',\n"
        "  '  mg *= 1.0 - 0.7 * hin * max(max(h0.a, h1.a), max(h2.a, h3.a));',                                     // 조각에는 종이 결이 이미 있다 — 덧입히는 결을 줄인다\n"
        "  '#endif',\n"
        "  '  float dn = texture2D(detail, vW * 0.21).r, dn2 = texture2D(detail, vW * 1.17 + 0.37).g;',")
g = rep(g, "mapN: { value: new THREE.Vector2(1, 1) }, pxr: { value: DPR || 1 } },",
        "mapN: { value: new THREE.Vector2(1, 1) }, pxr: { value: DPR || 1 },\n"
        "      hiT0: { value: blank }, hiT1: { value: blank }, hiT2: { value: blank }, hiT3: { value: blank }, hiK: { value: new THREE.Vector4(0, 0, 0, 0) }, hiF: { value: new THREE.Vector2(0.01, 0.01) },\n"
        "      hiR0: { value: new THREE.Vector4(0, 0, 1, 1) }, hiR1: { value: new THREE.Vector4(0, 0, 1, 1) }, hiR2: { value: new THREE.Vector4(0, 0, 1, 1) }, hiR3: { value: new THREE.Vector4(0, 0, 1, 1) } },")
g = rep(g, "  if (R3.magfix) R3.tmat.defines = { MAGFIX: 1 };",
        "  if (R3.magfix) R3.tmat.defines = { MAGFIX: 1 };\n"
        "  R3.blankTex = blank;\n"
        "  if (window.HITILE && window.HITILE.base) { R3.tmat.defines = R3.tmat.defines || {}; R3.tmat.defines.HITILE = 1; hiInit(); }      // v0.26: 4배 조각이 있는 판에서만")
g = rep(g, "  if (R3 && R3.ready) {\n    spotCheck();", "  if (R3 && R3.ready) {\n    spotCheck();\n    if (HT.on && G && $('title').classList.contains('off')) hiTick(now);      // v0.26: 판이 열려 있을 때만(제목 화면에서는 받지 않는다)")
# ───────── 조각을 고르고 받아 오는 일 ─────────
g = rep(g, "/* ---------- 장면 만들기 ---------- */", r"""/* ---------- v0.26 가까이 당겼을 때의 바탕 그림 ----------
   바탕 그림(3072 × 2610)은 한 칸에 14점쯤이라 가까이 당기면 뭉개진다. 4배로 키운 그림(12288 × 10440)을 8 × 8 조각으로 잘라 두고(tools/map4.py),
   가까이 당긴 곳의 조각만 받아 와 그 자리에 겹친다(한 번에 넷까지 · 받아 둔 것은 여섯까지). 조각이 없는 판(한 파일짜리)이거나 못 받으면 예전 그대로다.
   window.HITILE = { base, nx, ny, w, h, m, W, H } 는 판을 만들 때 넣는다(tools/build.py): base = 조각이 있는 곳, w · h = 조각 한 장의 크기, m = 사방의 겹침, W · H = 큰 그림의 크기. */
var HI_Z = 0.8, HI_SLOTS = 4, HI_KEEP = 6;
var HT = { on: false, C: null, slot: [], tex: {}, bad: {}, busy: 0, last: 0, cx: -1, cy: -1, cz: -1, loaded: 0, fail: 0 };
function hiInit() {
  var C = window.HITILE, U = R3.tmat.uniforms, i;
  if (!C || !C.base || !U.hiK || location.protocol === 'file:') return;      /* 파일로 연 판(file://)에서는 조각을 청하지 않는다 — 다른 출처로 막혀 받을 수 없다(오류만 남는다) */
  HT.C = C; HT.on = true; HT.slot = [];
  for (i = 0; i < HI_SLOTS; i++) HT.slot.push({ key: '', k: 0, to: 0 });
  U.hiF.value.set(C.m / 2 / C.w, C.m / 2 / C.h);                    // 가장자리 16점에 걸쳐 스민다(겹침 32점의 절반 — 이웃 조각과 맞닿는 곳에서는 두 조각이 다 온전하다)
}
function hiRect(key, v) { var C = HT.C, a = key.split('_'), du = 1 / C.nx, dv = 1 / C.ny, mu = C.m / C.W, mv = C.m / C.H; return v.set(+a[0] * du - mu, +a[1] * dv - mv, 1 / (du + 2 * mu), 1 / (dv + 2 * mv)); }
function hiWant() {                                                  // 지금 보이는 땅에 걸친 조각 가운데 화면 가운데에 가까운 넷
  if (cam.z < HI_Z || CW < 60 || CH < 60) return [];
  var C = HT.C, D = camDist(), hw = D * K3 * (CW / CH) / 2 * 1.15, hd = D * K3 / 2 / Math.max(0.4, Math.sin(camPitch()));
  var x0 = cam.x - hw, x1 = cam.x + hw, y0 = cam.y - hd * 1.5, y1 = cam.y + hd * 0.9, tw = MAP3D.WX / C.nx, th = MAP3D.WZ / C.ny, out = [], i, j;
  for (j = Math.max(0, Math.floor(y0 / th)); j <= Math.min(C.ny - 1, Math.floor(y1 / th)); j++)
    for (i = Math.max(0, Math.floor(x0 / tw)); i <= Math.min(C.nx - 1, Math.floor(x1 / tw)); i++) {
      var dx = (i + 0.5) * tw - cam.x, dy = (j + 0.5) * th - (cam.y - hd * 0.2);
      out.push({ key: i + '_' + j, d: dx * dx + dy * dy });
    }
  out.sort(function (a, b) { return a.d - b.d; });
  return out.slice(0, HI_SLOTS).map(function (o) { return o.key; });
}
function hiLoad(key, now) {
  if (HT.tex[key] || HT.busy >= 2 || (HT.bad[key] && now - HT.bad[key] < 20000)) return;
  var im = new Image(); HT.busy++; HT.tex[key] = { t: null, at: now };
  im.onload = function () {
    HT.busy--;
    var t = new THREE.Texture(im), mm = !!R3.renderer.capabilities.isWebGL2;
    t.flipY = false; t.generateMipmaps = mm; t.minFilter = mm ? THREE.LinearMipmapLinearFilter : THREE.LinearFilter; t.magFilter = THREE.LinearFilter;
    t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping; t.anisotropy = Math.min(4, R3.renderer.capabilities.getMaxAnisotropy()); t.needsUpdate = true;
    if (HT.tex[key]) { HT.tex[key].t = t; HT.loaded++; } else t.dispose();
    HT.last = 0; UI.render = true;
  };
  im.onerror = function () { HT.busy--; delete HT.tex[key]; HT.bad[key] = performance.now(); if (++HT.fail >= 6 && !HT.loaded) HT.on = false; };      /* 한 장도 못 받은 채 여섯 번 실패하면 이 판에서는 그만둔다(조각을 못 받는 곳) */
  im.crossOrigin = 'anonymous';      /* 다른 출처로 취급되는 곳에서는 깨끗이 실패하게 — 더럽혀진 그림을 WebGL 에 올리다 멈추지 않도록 */
  im.src = HT.C.base + key + '.webp';
}
function hiTick(now) {
  var U = R3.tmat.uniforms, moved = cam.x !== HT.cx || cam.y !== HT.cy || cam.z !== HT.cz, i, s, fading = false;
  if (moved || now - HT.last > 400) {
    HT.cx = cam.x; HT.cy = cam.y; HT.cz = cam.z; HT.last = now;
    var want = hiWant(), free = [], k;
    for (i = 0; i < HI_SLOTS; i++) { s = HT.slot[i]; if (s.key && want.indexOf(s.key) < 0) { s.key = ''; s.k = 0; s.to = 0; U['hiT' + i].value = R3.blankTex; UI.render = true; } if (!s.key) free.push(i); }
    for (k = 0; k < want.length; k++) {
      var key = want[k], e = HT.tex[key], has = false;
      for (i = 0; i < HI_SLOTS; i++) if (HT.slot[i].key === key) has = true;
      if (e) e.at = now;
      if (has) continue;
      if (e && e.t && free.length) { i = free.shift(); s = HT.slot[i]; s.key = key; s.k = 0; s.to = 1; U['hiT' + i].value = e.t; hiRect(key, U['hiR' + i].value); }
      else if (!e) hiLoad(key, now);
    }
    var old = Object.keys(HT.tex).filter(function (q) { return HT.tex[q].t && want.indexOf(q) < 0; }).sort(function (a, b) { return HT.tex[a].at - HT.tex[b].at; });      // 오래 안 쓴 것부터 버린다
    while (old.length && Object.keys(HT.tex).length > HI_KEEP) { var q = old.shift(); HT.tex[q].t.dispose(); delete HT.tex[q]; }
  }
  for (i = 0; i < HI_SLOTS; i++) { s = HT.slot[i]; if (s.k < s.to) { s.k = Math.min(s.to, s.k + 0.08); fading = true; } U.hiK.value.setComponent(i, s.k); }
  if (fading) UI.render = true;
}

/* ---------- 장면 만들기 ---------- */""")
wr('src/ui3d.js', g)

# ───────── 도움말 한 줄 ─────────
u = rd('src/ui_panels.js')
u = rep(u, "'<h3>지도</h3><p>실제 지형(고도·강·해안)과 거점의 실제 위치를 바탕으로 만들었습니다.",
        "'<h3>지도</h3><p>실제 지형(고도·강·해안)과 거점의 실제 위치를 바탕으로 만들었습니다. 가까이 당기면 그 자리의 더 고운 그림을 받아 와 겹칩니다(인터넷이 없으면 본래 그림 그대로).")
wr('src/ui_panels.js', u)

# ───────── 앱(PWA): 조각을 저장해 둔다(한 번 받은 조각은 다시 받지 않는다 — 이름에 내용의 지문이 있다) ─────────
w = rd('pwa/sw.js')
w = rep(w, "var SHELL = 'chunhado-shell-2', BGM = 'chunhado-bgm-1', FONT = 'chunhado-font-1', VID = 'chunhado-video-1';",
        "var SHELL = 'chunhado-shell-2', BGM = 'chunhado-bgm-1', FONT = 'chunhado-font-1', VID = 'chunhado-video-1', TILE = 'chunhado-tile-1';      // TILE(v0.26): 가까이 당겼을 때의 바탕 그림 조각")
w = rep(w, "k !== SHELL && k !== BGM && k !== FONT && k !== VID;", "k !== SHELL && k !== BGM && k !== FONT && k !== VID && k !== TILE;")
w = rep(w, "self.addEventListener('fetch', function (e) {",
        "function tile(req) {                                         // 조각: 저장해 둔 것이 있으면 그것, 없으면 받아서 저장\n"
        "  return caches.open(TILE).then(function (c) {\n"
        "    return c.match(req).then(function (hit) {\n"
        "      if (hit) return hit;\n"
        "      return fetch(req).then(function (r) { if (r && r.ok) c.put(req, r.clone()); return r; });\n"
        "    });\n"
        "  });\n"
        "}\n"
        "self.addEventListener('fetch', function (e) {")
w = rep(w, "    if (/\\/bgm\\/[^/]+\\.mp3$/.test(url.pathname)) {", "    if (/\\/tiles\\/t4-[0-9a-f]+\\/[0-9]+_[0-9]+\\.webp$/.test(url.pathname)) { e.respondWith(tile(req)); return; }\n    if (/\\/bgm\\/[^/]+\\.mp3$/.test(url.pathname)) {")
wr('pwa/sw.js', w)
print('s1_map ok')
