# v0.20 (2) 지도 위의 물체 — 성의 내구 막대 · 짓는 중인 시설이 보이게
#   · 성 이름표 아래에 내구 막대("성에는 내구도가 bar 형태로 바로 보여지게"): 가득하면 종이 빛, 60% 아래 누런빛, 30% 아래 붉은빛
#   · 짓는 중인 시설("공사 중인 농장이 갑자기 안 보인다"): 시설 창을 띄우면 이름표가 건물 한가운데를 덮었다 — 이름표를 건물 아래(칸의 아랫변)로 내리고,
#     짓는 중인 그림의 먹을 짙게 · 비계 기둥을 굵게 했다(멀리서도 보이게)
import io, os
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)

s = rd('src/ui3d.js')
# --- 내구 막대 ---
s = rep(s, "function drawLabel(L, lines, bg, border, badge, badgeBg, face) {\n  var x = L.cv.getContext('2d'), i, w = 0, h = 10, S = 2;",
        "function drawLabel(L, lines, bg, border, badge, badgeBg, face, bar) {\n  var x = L.cv.getContext('2d'), i, w = 0, h = 10, S = 2, BH = bar ? 13 : 0;      // v0.20: bar = { v: 0~1 } 이면 판 아래에 막대(성의 내구)")
s = rep(s, "  w = Math.ceil(w + 22 * S / 2 + (badge ? 30 : 8)); h = Math.ceil(h);\n",
        "  w = Math.ceil(w + 22 * S / 2 + (badge ? 30 : 8)); h = Math.ceil(h) + BH;\n")
s = rep(s, "  if (badge) { rr(x, w - 31, 3, 28, 28, 4); x.fillStyle = badgeBg || SEAL; x.fill();",
        """  if (bar) {                                                    // 내구 막대: 먹빛 홈에 남은 만큼
    var bx0 = 9, bwid = bw - 18, by0 = h - BH - 2, bv = clamp(bar.v, 0, 1);
    rr(x, bx0, by0, bwid, 8, 2.5); x.fillStyle = 'rgba(20,18,16,0.62)'; x.fill();
    if (bv > 0) { rr(x, bx0 + 1, by0 + 1, Math.max(3, (bwid - 2) * bv), 6, 2); x.fillStyle = bv < 0.3 ? '#e2574a' : (bv < 0.6 ? '#e6b63c' : '#f4efe3'); x.fill(); }
    x.lineWidth = 1; x.strokeStyle = 'rgba(251,246,234,0.55)'; rr(x, bx0, by0, bwid, 8, 2.5); x.stroke();
  }
  if (badge) { rr(x, w - 31, 3, 28, 28, 4); x.fillStyle = badgeBg || SEAL; x.fill();""")
s = rep(s, "(UI.sel && UI.sel.kind === 'base' && UI.sel.id === b.id) + '|' + (cpL ? cpL.n : '');\n    if (sig !== o.sig) {",
        "(UI.sel && UI.sel.kind === 'base' && UI.sel.id === b.id) + '|' + (cpL ? cpL.n : '') + '|' + Math.round(40 * b.dur / Math.max(1, b.maxDur));\n    if (sig !== o.sig) {")
s = rep(s, "cpL ? corpsMark(cpL) : (mineB && idleN[b.id] ? idleN[b.id] : 0), cpL ? INK : null);\n      R3.labelK = 0;",
        "cpL ? corpsMark(cpL) : (mineB && idleN[b.id] ? idleN[b.id] : 0), cpL ? INK : null, null, { v: b.dur / Math.max(1, b.maxDur) });\n      R3.labelK = 0;")
# --- 짓는 중인 그림 ---
s = rep(s, "SITE_INK = [0.42, 0.54, 0.68], SITE_A = [0.84, 0.90, 0.95];", "SITE_INK = [0.66, 0.76, 0.86], SITE_A = [0.96, 0.98, 1];      // v0.20: 먹을 짙게(멀리서도 보이게 — 전에는 0.42~0.68 · 0.84~0.95)")
s = rep(s, "line([P[0], P[1] + 2], up(P, H + 5), 2.2, POLE, true); });", "line([P[0], P[1] + 2], up(P, H + 5), 3.2, POLE, true); });")
s = rep(s, "line(up(L, H * q), up(F, H * q), 1.8, POLE, true); line(up(F, H * q), up(R, H * q), 1.8, POLE, true); });", "line(up(L, H * q), up(F, H * q), 2.6, POLE, true); line(up(F, H * q), up(R, H * q), 2.6, POLE, true); });")
s = rep(s, "x.lineTo(ft[0] - 14, ft[1] + 4.5); x.lineTo(ft[0], ft[1] + 9); x.closePath(); x.fillStyle = '#ba342a'; x.fill();",
        "x.lineTo(ft[0] - 22, ft[1] + 7); x.lineTo(ft[0], ft[1] + 14); x.closePath(); x.fillStyle = '#ba342a'; x.fill(); x.lineWidth = 1; x.strokeStyle = 'rgba(58,40,24,0.9)'; x.stroke();")
# --- 시설 이름표: 건물 아래로 ---
s = rep(s, "fon = fa === selF, fly = fq[1] + fpu * 0.16;", "fon = fa === selF, fly = fq[1] + fpu * (fa.done ? 0.16 : 0.42), fnm = fa.done ? fa.n : fa.n + ' · ' + fa.left;      // v0.20: 짓는 중인 시설의 이름표는 건물의 발치로 내리고(비계를 가리지 않게) 남은 날수를 같은 줄에 적는다(전에는 한 줄 더 — 아래 칸을 덮었다)")
s = rep(s, "var ftw = x.measureText(fa.n).width, fbr = clamp(fpx * 0.6, 6, 7.8)", "var ftw = x.measureText(fnm).width, fbr = clamp(fpx * 0.6, 6, 7.8)")
s = rep(s, """    if (!fon) x.strokeText(fa.n, ftx, fly);
    x.fillText(fa.n, ftx, fly);
    if (!fa.done) { var fly2 = fly + fpx + (fon ? 6 : 1); x.font = '600 ' + (fpx - 1) + 'px ' + FONT_B; x.fillStyle = '#f0d58a'; x.strokeText(fa.left + ' 남음', fq[0], fly2); x.fillText(fa.left + ' 남음', fq[0], fly2); }      // 짓는 중: 남은 날수
""", """    if (!fon) x.strokeText(fnm, ftx, fly);
    x.fillText(fnm, ftx, fly);
""")
wr('src/ui3d.js', s)
print('s2 ok')
