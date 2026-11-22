# v0.18 지도 위의 부대 표시 — 주장의 얼굴을 이름·병력 판에 붙여 한 덩어리로
#   그동안: 얼굴 딱지는 부대 그림의 왼쪽 위에, 이름·병력 판은 발밑에 따로 떠 있었다 → 부대가 붙어 서면 어느 얼굴이 어느 숫자의 것인지 헷갈렸다.
#   이제: 얼굴 딱지가 판의 왼쪽 위 모서리에 걸쳐 붙는다(한 장의 그림). 판의 폭은 글씨가 가리지 않을 만큼만 넓어진다.
#   CH_ROOT=<폴더> 로 다른 나무에 입힐 수 있다(시험용).
import io, os
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)

s = rd('src/ui3d.js')
# 이름표: 얼굴(face = {img, ring, dim})을 주면 판의 왼쪽 위 모서리에 걸쳐 그린다. L.ax · L.ay = 판의 윗변 가운데(스프라이트의 기준점)
s = rep(s, "function drawLabel(L, lines, bg, border, badge, badgeBg) {\n  var x = L.cv.getContext('2d'), i, w = 0, h = 10, S = 2;\n",
           "function drawLabel(L, lines, bg, border, badge, badgeBg, face) {\n  var x = L.cv.getContext('2d'), i, w = 0, h = 10, S = 2;\n")
s = rep(s, "  w = Math.ceil(w + 22 * S / 2 + (badge ? 30 : 8)); h = Math.ceil(h);\n  L.cv.width = w; L.cv.height = h; L.w = w; L.h = h;\n  x = L.cv.getContext('2d');\n  var bw = w - (badge ? 22 : 0), sel = border === SEAL;\n",
"""  w = Math.ceil(w + 22 * S / 2 + (badge ? 30 : 8)); h = Math.ceil(h);
  // v0.18: 얼굴 딱지 — 판 밖으로 왼쪽 ox · 위 oy 만큼 나와 모서리에 걸친다. 글씨는 얼굴에 가리지 않게 오른쪽으로 조금 민다
  var FD = face ? FACE_D : 0, ox = face ? Math.round(FD * 0.40) : 0, oy = face ? Math.round(FD * 0.46) : 0, tsh = face ? Math.round(FD * 0.13) : 0;
  if (face) w += tsh * 2;
  L.cv.width = w + ox; L.cv.height = h + oy; L.w = w + ox; L.h = h + oy; L.ax = (ox + w / 2) / (w + ox); L.ay = h / (h + oy);
  x = L.cv.getContext('2d'); x.save(); x.translate(ox, oy);
  var bw = w - (badge ? 22 : 0), sel = border === SEAL, tcx = bw / 2 + tsh;
""")
s = rep(s, "    x.fillStyle = 'rgba(20,18,16,0.38)'; x.fillText(ln.t, bw / 2 + 1, y + 1.5);\n    x.fillStyle = ln.color || '#fbf6ea'; x.fillText(ln.t, bw / 2, y); y += ln.px * S * 1.18;\n",
           "    x.fillStyle = 'rgba(20,18,16,0.38)'; x.fillText(ln.t, tcx + 1, y + 1.5);\n    x.fillStyle = ln.color || '#fbf6ea'; x.fillText(ln.t, tcx, y); y += ln.px * S * 1.18;\n")
s = rep(s, "x.textBaseline = 'middle'; x.fillText(badge, w - 17, 18); }\n  L.tex.dispose(); L.tex.needsUpdate = true;\n}\n/* 상태 딱지(부대 머리 위)",
           "x.textBaseline = 'middle'; x.fillText(badge, w - 17, 18); }\n  x.restore();\n  if (face) { x.globalAlpha = face.dim ? 0.78 : 1; faceAt(x, face.img, face.ring, 0, 0, FD); x.globalAlpha = 1; }\n  L.tex.dispose(); L.tex.needsUpdate = true;\n}\n/* 상태 딱지(부대 머리 위)")
# 둥근 초상 그리기를 따로 떼어, 판에 붙일 때도 쓴다
s = rep(s, """/* 부대 왼쪽 위에 붙는 주장 얼굴 딱지(둥근 초상). 테두리는 세력 색 */
function drawFace(L, img, ring) {
  var S = 60, x; L.cv.width = L.cv.height = S; L.w = L.h = S; x = L.cv.getContext('2d');
  x.save(); x.beginPath(); x.arc(S / 2, S / 2, S / 2 - 4, 0, 6.3); x.clip(); x.fillStyle = '#f6f1e6'; x.fillRect(0, 0, S, S);
  x.globalCompositeOperation = 'multiply';
  try { var iw = img.naturalWidth, ih = img.naturalHeight; x.drawImage(img, iw * 0.25, ih * 0.13, iw * 0.50, ih * 0.50, 3, 3, S - 6, S - 6);    /* v0.5 흉상: 얼굴 중심이 가로 50%·세로 41% */ } catch (e) { /* 바탕만 */ }
  x.restore();
  x.beginPath(); x.arc(S / 2, S / 2, S / 2 - 4, 0, 6.3); x.lineWidth = 5; x.strokeStyle = ring; x.stroke();
  x.beginPath(); x.arc(S / 2, S / 2, S / 2 - 1.3, 0, 6.3); x.lineWidth = 1.4; x.strokeStyle = 'rgba(27,26,24,0.9)'; x.stroke();
  L.tex.dispose(); L.tex.needsUpdate = true;
}
""", """/* 주장 얼굴 딱지(둥근 초상). 테두리는 세력 색. v0.18: 이름·병력 판의 왼쪽 위 모서리에 붙여 한 덩어리로 그린다(drawLabel 의 face) */
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
""")
# 부대: 얼굴을 판에 붙인다(따로 뜨던 얼굴 스프라이트는 쓰지 않는다)
s = rep(s, "      o.lab.sp.center.set(0.5, 1); o.lab.sp.position.set(0, -0.16, 0);\n", "      o.lab.sp.position.set(0, -0.16, 0);\n")
s = rep(s, "      drawLabel(o.lab, lns, dim ? mixHex(fcol, '#8d877b', 0.6) : shade(fcol, 0.84), isSel ? SEAL : INK);\n      o.fcOn = !!fim;\n      if (fim) { drawFace(o.fc, fim, isSel ? SEAL : fcol); o.fc.sp.position.set(-0.74, o.sp.userData.top * 0.80, 0); o.fc.sp.material.opacity = dim ? 0.7 : 1; }\n",
           "      drawLabel(o.lab, lns, dim ? mixHex(fcol, '#8d877b', 0.6) : shade(fcol, 0.84), isSel ? SEAL : INK, undefined, undefined, fim ? { img: fim, ring: isSel ? SEAL : fcol, dim: dim } : null);      // v0.18: 얼굴 · 이름 · 병력이 한 덩어리\n"
           "      o.lab.sp.center.set(o.lab.ax, o.lab.ay); o.fcOn = false; o.hasFace = !!fim;\n")
wr('src/ui3d.js', s)
print('p2_unit18: ok')
