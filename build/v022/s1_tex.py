# v0.22 (1) 코드로 그린 그림이 사라지지 않게 — 요청 2 · 3
#   ② "여전히 건설 중인 건물이 안 보이는 버그 있음(스크린샷 참고)"   ③ "불길이나 화살도 중간에 모양이 안 나오는 버그있음"
#   시험 브라우저에서는 다시 나타나지 않았다. 스크린샷에서 읽은 것:
#     · 같은 휴대폰의 예전 스크린샷(195년 복양 · 196년 낙양)에는 성 둘레의 붓 고리와 공사장(비계)이 보인다.
#     · 이번 스크린샷(197년 9월 낙양 · 12월 신야)에는 붓 고리도, 수송대 발밑의 먹점도 없다. 성 · 시설 · 부대 그림과 이름표는 멀쩡하다.
#   사라진 것의 공통점: 화면에서 '코드로 그린' 그림(그림판 canvas 를 텍스처의 원본으로 쓰는 THREE.CanvasTexture)이고, 만든 지 오래된 것이다
#   (이름표는 숫자가 바뀔 때마다 다시 그려 올리므로 살아 있다. 사진으로 넣은 그림은 <img> 가 원본이라 살아 있다).
#   텍스처는 WebGL 문맥이 새로 만들어지면(앱을 벗어났다 돌아왔을 때 흔하다) 원본에서 다시 올라간다. 그때 브라우저가 그림판의 내용을 비워 두었으면 빈 그림이 올라간다.
#   시험 브라우저에서 그 상황(그림판 비우기 + 문맥 끊김 · 복구)을 흉내 내면 스크린샷과 같은 모습이 된다: 공사장 · 불길 · 이름표가 사라지고 성 · 시설은 남는다(tests/d36.py).
#   고친 것:
#     · 그리자마자 화소를 읽어 텍스처가 스스로 지닌다(THREE.DataTexture — cvTex). 그림판에는 더 기대지 않는다: 이름표 · 불꽃 · 붓 자국(화살 · 불티 · 연기 …) · 성역의 붓 고리 · 먹점 · 공사장 · 땅의 결.
#     · 화면으로 돌아왔을 때 · 문맥이 복구됐을 때 그 텍스처들을 모두 다시 올리고 이름표를 다시 그린다(sceneRefresh).
#   실제 휴대폰에서 같은 까닭이었는지는 기기에서 확인해야 한다.
import io, os
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)

# ---------------- ui3d.js ----------------
s = rd('src/ui3d.js')

# 도우미
s = rep(s, "function noiseTexture() {\n", """/* ---------- 코드로 그린 그림을 텍스처로(v0.22) ----------
   0.21 까지는 그림판(canvas)을 그대로 텍스처의 원본으로 두었다(THREE.CanvasTexture). 텍스처는 WebGL 문맥이 새로 만들어질 때마다(앱을 벗어났다 돌아오면 흔하다)
   원본에서 다시 올라가는데, 그 사이에 브라우저가 그림판의 내용을 비웠으면 빈 그림이 올라간다 — 코드로 그린 것(공사장 · 불길 · 화살 · 붓 고리 · 먹점)만 사라지고
   사진으로 넣은 그림(성 · 시설 · 부대)은 남는다. 이제는 그리자마자 화소를 읽어 텍스처가 스스로 지닌다(THREE.DataTexture). 그림판에는 더 기대지 않는다. */
function cv2d(c) { return c.getContext('2d', { willReadFrequently: true }); }      // 곧바로 화소를 읽을 그림판(처음 한 번 이렇게 열어 두면 뒤의 getContext('2d') 도 같은 것을 돌려준다)
function cvPixels(c) {                                       // 그림판의 화소. 위아래를 뒤집는다(텍스처의 첫 줄 = 그림의 맨 아랫줄). 읽지 못하면 null
  var w = c.width, h = c.height, d;
  try { d = c.getContext('2d').getImageData(0, 0, w, h).data; } catch (e) { return null; }
  var row = w * 4, out = new Uint8Array(row * h);
  for (var y = 0; y < h; y++) out.set(d.subarray((h - 1 - y) * row, (h - y) * row), y * row);
  return { data: out, width: w, height: h };
}
function texMipOk(w, h) { return !!(R3 && R3.renderer && R3.renderer.capabilities.isWebGL2) || ((w & (w - 1)) === 0 && (h & (h - 1)) === 0); }
function cvTex(c, mip) {                                     // 그림판 → 텍스처. mip === false 면 축소본을 만들지 않는다
  var im = cvPixels(c);
  if (!im) return new THREE.CanvasTexture(c);                // 화소를 읽지 못하면(드물다) 전처럼
  var t = new THREE.DataTexture(im.data, im.width, im.height, THREE.RGBAFormat), mm = mip !== false && texMipOk(im.width, im.height);
  t.magFilter = THREE.LinearFilter; t.minFilter = mm ? THREE.LinearMipmapLinearFilter : THREE.LinearFilter; t.generateMipmaps = mm; t.needsUpdate = true;
  return t;
}
function cvTexPut(t, c) {                                    // 다시 그린 그림판을 이미 있는 텍스처에 담는다(이름표). 크기가 바뀌므로 먼저 버리고 새로 올린다
  var im = t.isDataTexture ? cvPixels(c) : null;
  t.dispose(); if (im) t.image = im; t.needsUpdate = true;
}
/* WebGL 문맥이 새로 만들어진 바로 그때: 끊긴 문맥에서 만든 것들에 걸려 있던 '버릴 때' 연락처를 뗀다 — three 는 새 문맥에서 쓸 때 새로 건다.
   그대로 두면 버릴 때마다(이름표를 다시 그릴 때 · 붓 자국을 지울 때) 옛 문맥의 것을 지우려다 경고가 쌓인다. three 의 복구 처리가 먼저 돈 뒤, 아무것도 다시 올리기 전에 부른다. */
function glStale() {
  if (!R3) return;
  var k;
  function drop(o) { if (o && o._listeners && o._listeners.dispose) o._listeners.dispose.length = 0; }
  R3.scene.traverse(function (o) { var m = o.material; if (m) { drop(m); drop(m.map); if (m.uniforms) for (var u in m.uniforms) { var v = m.uniforms[u].value; if (v && v.isTexture) drop(v); } } drop(o.geometry); });
  for (k in TEX) drop(TEX[k]); for (k in TEXF) drop(TEXF[k]);
  if (typeof FX !== 'undefined') for (k in FX.tex) drop(FX.tex[k]);
  drop(R3.flame); drop(R3.zoneTex); drop(R3.dotTex); drop(R3.stTex); drop(R3.ovTex);
}
/* 화면으로 돌아왔을 때 · WebGL 문맥이 복구됐을 때: 코드로 그린 텍스처를 모두 다시 올리고, 이름표를 다시 그리고, 화면을 새로 그린다 */
function sceneRefresh() {
  if (!R3 || !R3.ready) return;
  var k, i;
  function up(t) { if (t && t.isTexture) t.needsUpdate = true; }
  if (typeof FX !== 'undefined') for (k in FX.tex) up(FX.tex[k]);
  for (k in TEX) if (k.indexOf('@') > 0) up(TEX[k]);
  up(R3.flame); up(R3.zoneTex); up(R3.dotTex); up(R3.stTex); up(R3.ovTex); up(R3.tmat.uniforms.detail.value);
  for (i = 0; i < R3.bases.length; i++) if (R3.bases[i]) R3.bases[i].sig = '';
  for (k in R3.units) R3.units[k].sig = '';
  R3.labelK = 0; R3.refreshN = (R3.refreshN || 0) + 1; UI.dirty = true; UI.render = true;
  if (typeof MINI !== 'undefined') MINI.t = 0;
}

function noiseTexture() {
""")
s = rep(s, "  var x = c.getContext('2d'), im = x.createImageData(n, n), d = im.data, s = 12345;", "  var x = cv2d(c), im = x.createImageData(n, n), d = im.data, s = 12345;")
s = rep(s, "  var t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;", "  var t = cvTex(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;")
# 불꽃
s = rep(s, """  var x = c.getContext('2d'), g = x.createRadialGradient(32, 66, 2, 32, 60, 34);""", """  var x = cv2d(c), g = x.createRadialGradient(32, 66, 2, 32, 60, 34);""")
s = rep(s, """  x.fillStyle = g; x.beginPath(); x.moveTo(32, 2); x.bezierCurveTo(60, 44, 58, 92, 32, 94); x.bezierCurveTo(6, 92, 4, 44, 32, 2); x.fill();
  return new THREE.CanvasTexture(c);""", """  x.fillStyle = g; x.beginPath(); x.moveTo(32, 2); x.bezierCurveTo(60, 44, 58, 92, 32, 94); x.bezierCurveTo(6, 92, 4, 44, 32, 2); x.fill();
  return cvTex(c);""")
# 이름표
s = rep(s, """  var c = document.createElement('canvas'); c.width = 8; c.height = 8;
  var t = new THREE.CanvasTexture(c); t.minFilter = THREE.LinearFilter; t.generateMipmaps = false;""", """  var c = document.createElement('canvas'); c.width = 8; c.height = 8; cv2d(c);
  var t = cvTex(c, false);""")
s = rep(s, "  L.tex.dispose(); L.tex.needsUpdate = true;", "  cvTexPut(L.tex, L.cv);", 3)
# 붓 고리 · 먹점
s = rep(s, """  var n = 256, c = document.createElement('canvas'); c.width = c.height = n;
  var x = c.getContext('2d'), i, s = 91;""", """  var n = 256, c = document.createElement('canvas'); c.width = c.height = n;
  var x = cv2d(c), i, s = 91;""")
s = rep(s, "  var t2 = new THREE.CanvasTexture(c); t2.minFilter = THREE.LinearMipmapLinearFilter; return t2;", "  return cvTex(c);")
s = rep(s, """  var x = c.getContext('2d'), g = x.createRadialGradient(n / 2, n / 2, 4, n / 2, n / 2, n / 2);""", """  var x = cv2d(c), g = x.createRadialGradient(n / 2, n / 2, 4, n / 2, n / 2, n / 2);""")
s = rep(s, """  x.fillStyle = g; x.fillRect(0, 0, n, n);
  return new THREE.CanvasTexture(c);""", """  x.fillStyle = g; x.fillRect(0, 0, n, n);
  return cvTex(c);""")
# 공사장
s = rep(s, "  var x = c.getContext('2d'); x.drawImage(im, 0, 0, w, h);", "  var x = cv2d(c); x.drawImage(im, 0, 0, w, h);")
s = rep(s, "  var tx = new THREE.CanvasTexture(c); TEX[k] = tx; SPRITES[k] = { w: SPRITES[t].w, h: SPRITES[t].h, ay: SPRITES[t].ay };", "  var tx = cvTex(c); TEX[k] = tx; SPRITES[k] = { w: SPRITES[t].w, h: SPRITES[t].h, ay: SPRITES[t].ay };      // v0.22: 화소를 지닌 텍스처(그림판에 기대지 않는다)")
# 문맥이 복구됐을 때
s = rep(s, "  renderer.setClearColor(FOGC, 1);\n", "  renderer.setClearColor(FOGC, 1);\n  cv.addEventListener('webglcontextrestored', function () { try { glStale(); sceneRefresh(); } catch (e) { /* */ } }, false);      // v0.22: 문맥이 새로 만들어졌다 — 다시 올리고 다시 그린다(three 의 복구 처리는 이보다 먼저 걸려 있어 먼저 돈다)\n")
# 화면으로 돌아왔을 때
s = rep(s, """document.addEventListener('visibilitychange', function () {
  try { if (document.hidden) {""", """document.addEventListener('visibilitychange', function () {
  if (!document.hidden) { try { sceneRefresh(); } catch (e0) { /* */ } }      // v0.22: 돌아왔다 — 코드로 그린 그림을 다시 올린다
  try { if (document.hidden) {""")
wr('src/ui3d.js', s)

# ---------------- fx.js ----------------
s = rd('src/fx.js')
s = rep(s, "function fxCanvas(w, h) { var c = document.createElement('canvas'); c.width = w; c.height = h; return c; }", "function fxCanvas(w, h) { var c = document.createElement('canvas'); c.width = w; c.height = h; cv2d(c); return c; }")
s = rep(s, "function fxTexOf(c) { var t = new THREE.CanvasTexture(c); t.minFilter = THREE.LinearFilter; t.generateMipmaps = false; return t; }", "function fxTexOf(c) { return cvTex(c, false); }      // v0.22: 화소를 지닌 텍스처(ui3d.js 의 cvTex)")
wr('src/fx.js', s)
print('s1 ok')
