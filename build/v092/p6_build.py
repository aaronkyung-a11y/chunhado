# v0.9.2 (6/…): 건설 자리 비추기
#  요청: "건설이 가능한 공간을 하이라이트해서 보여주거나 그 공간 이외에는 암전을 줘서 어디에 내가 건설하는 지, 건설이 가능한지를 정확히 알면 좋겠어. 건설을 선택했을 때"
#  - 건설을 고른 동안(거점의 건설 탭, '무엇을 지을까요' 창)에는 지도를 어둡게 덮고 지을 수 있는 빈 부지만 뚫어 밝게 보인다. 빈 부지에는 번호가 붙고, 창에는 같은 번호의 단추가 한 줄로 놓인다
#    (전에는 '빈 부지 / 옆: 병영' 줄이 부지 수만큼 늘어섰다 — 옆에 무엇이 있는지는 이제 지도의 이름과 고르는 창이 알려 준다)
#  - 자리를 고르면 그 칸에 붉은 테두리와 '여기' 표가 붙는다. '무엇을 지을까요' 창은 화면 절반만 차지하고 그 위로 지도가 보인다 — 다른 밝은 칸을 누르면 자리가 바뀌고, 어두운 곳을 누르면 창이 닫힌다
#  - 지금 지을 수 없으면(쉬는 무장 없음·금 부족·행동력 부족) 칸은 밝아지지 않고 점선으로만 보이며, 까닭을 한 줄로 적는다
#  - '무엇을 지을까요' 창은 여덟 시설을 두 줄 카드로 한 번에 보인다(밀어 올릴 필요 없음). 카드에는 그 자리에 지었을 때 실제로 늘어나는 수입(금/월·병량/분기)을 적고,
#    조폐·곡창은 옆에 시장·농장이 없으면 붉게 알린다. 병영·대장간·마구간·공방은 이미 있으면 '이미 있음' 또는 '옆 …과 합병 가능'
#  - 착공하면 그 칸에서 글자가 떠오른다. 건설 자리를 보는 동안에는 알림 줄이 칸을 가리지 않게 위로 올라간다
#  규칙(core.js)은 바꾸지 않는다.
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)

# ---------------------------------------------------------------- index.html
p = 'src/index.html'; s = io.open(p, encoding='utf-8').read()
s = rep(s, '<canvas id="map"></canvas>\n', '<canvas id="map"></canvas>\n  <canvas id="spot" aria-hidden="true"></canvas>\n')
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- ui3d.js
p = 'src/ui3d.js'; s = io.open(p, encoding='utf-8').read()

s = rep(s, "function camPitch() {", "function pitchAt(z) { var t = clamp(Math.log(z / Z_MIN) / Math.log(Z_MAX / Z_MIN), 0, 1); return (68 - 27 * t) * Math.PI / 180; }\nfunction camPitch() {")

# 지도를 가리는 높이: '무엇을 지을까요' 창처럼 지도를 보여 주는 창(#modal.see)이 떠 있으면 그 창의 높이
s = rep(s, """  if (pl && pl.offsetHeight) cover = pl.offsetHeight;
  else cover = (bar ? bar.offsetHeight : 0) + (sh ? sh.offsetHeight : 0);""",
"""  var md = $('modal'), dl = md && md.classList.contains('see') ? md.querySelector('.dlg') : null;
  if (dl && dl.offsetHeight) cover = dl.offsetHeight;                         // 지도를 보여 주는 창(건설 자리 고르기)
  else if (pl && pl.offsetHeight) cover = pl.offsetHeight;
  else cover = (bar ? bar.offsetHeight : 0) + (sh ? sh.offsetHeight : 0);""")

# 카메라 옮기기: flyTo(지도 좌표) 가 새로 시작되면 먼저 가던 jumpTo 는 물러난다(둘이 한 화면을 두고 다투지 않게)
s = rep(s, """function jumpTo(c, r, z, fy, dur) {
  var p = hexCenter(c, r), z1 = clamp(z || cam.z, Z_MIN, Z_MAX), x0 = cam.x, y0 = cam.y, z0 = cam.z;""",
"""var camTok = 0;
function jumpTo(c, r, z, fy, dur) {
  var p = hexCenter(c, r), z1 = clamp(z || cam.z, Z_MIN, Z_MAX), x0 = cam.x, y0 = cam.y, z0 = cam.z, tok = camTok;""")
s = rep(s, "  anim(dur || 260, function (t) { var e = t * (2 - t); cam.x = x0 + (p[0] - x0) * e;", "  anim(dur || 260, function (t) { if (tok !== camTok) return; var e = t * (2 - t); cam.x = x0 + (p[0] - x0) * e;")
s = rep(s, "function ensureVisible(c, r) { if (!onScreen(c, r, 0)) jumpTo(c, r, Math.max(cam.z, 0.8)); }",
"""function ensureVisible(c, r) { if (!onScreen(c, r, 0)) jumpTo(c, r, Math.max(cam.z, 0.8)); }
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
}""")

# 건설 자리를 보는 동안 그 거점의 이름표는 숨긴다(성 북쪽의 부지를 가린다 — 거점 이름은 아래 창에 있다)
s = rep(s, "    var mineB = b.owner === G.player, col = b.owner >= 0 ? G.factions[b.owner].color : NEUTRAL;\n",
           "    var mineB = b.owner === G.player, col = b.owner >= 0 ? G.factions[b.owner].color : NEUTRAL;\n    o.lab.sp.visible = !(SPOT.on && SPOT.v && SPOT.v.b === b);\n")

# 덧칠: 지을 수 있는 칸은 조금 더 짙은 금빛, 고른 칸은 붉게
s = rep(s, "  if (UI.target) ovPut(K(UI.target.c, UI.target.r), [181, 51, 42], 225);\n",
"""  if (UI.target) ovPut(K(UI.target.c, UI.target.r), [181, 51, 42], 225);
  if (SPOT.on && SPOT.v) for (i = 0; i < SPOT.v.lots.length; i++) {            // 건설 자리
    var sl = SPOT.v.lots[i];
    if (sl.i === SPOT.v.pi) ovPut(K(sl.c, sl.r), [181, 51, 42], 138); else if (sl.ok) ovPut(K(sl.c, sl.r), [212, 160, 44], 120);
  }
""")

s = rep(s, "/* ---------- 연출 ---------- */",
"""/* ---------- 건설 자리 비추기 ----------
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
  x.globalCompositeOperation = 'destination-out'; x.fillStyle = '#000';
  for (i = 0; i < v.lots.length; i++) if (rings[i] && v.lots[i].ok) { ringPath(x, rings[i]); x.fill(); }      // 지을 수 있는 칸만 뚫는다
  x.globalCompositeOperation = 'source-over'; x.globalAlpha = SPOT.a; x.lineJoin = 'round'; x.textAlign = 'center'; x.textBaseline = 'middle';
  for (i = 0; i < v.facs.length; i++) {                        // 이미 지은 시설: 어둠 속에서도 옆에 무엇이 있는지 이름으로
    var fp = hexPos(v.facs[i].c, v.facs[i].r), fq = w2s(fp[0], fp[1], fp[2]); if (!fq) continue;
    var fpu = pxPerUnit(fq[2]); if (fpu < 15) continue;
    var fpx = clamp(Math.round(fpu * 0.40), 10, 13);
    x.font = '700 ' + fpx + 'px ' + FONT_B; x.lineWidth = 3; x.strokeStyle = 'rgba(20,18,16,0.72)';
    x.fillStyle = v.facs[i].done ? 'rgba(244,239,227,0.94)' : 'rgba(244,239,227,0.7)';
    x.strokeText(v.facs[i].n, fq[0], fq[1] + fpu * 0.16); x.fillText(v.facs[i].n, fq[0], fq[1] + fpu * 0.16);
    if (!v.facs[i].done) { x.font = '600 ' + (fpx - 1) + 'px ' + FONT_B; x.strokeText('짓는 중', fq[0], fq[1] + fpu * 0.16 + fpx + 1); x.fillText('짓는 중', fq[0], fq[1] + fpu * 0.16 + fpx + 1); }
  }
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
  x.globalAlpha = 1;
}

/* ---------- 연출 ---------- */""")

s = rep(s, "  if (R3 && R3.ready) {\n    var nzm = cam.z >= 1.15;", "  if (R3 && R3.ready) {\n    spotCheck();\n    var nzm = cam.z >= 1.15;")
s = rep(s, "      R3.renderer.render(R3.scene, R3.cam);\n", "      R3.renderer.render(R3.scene, R3.cam);\n      spotDraw();\n")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- ui_panels.js
p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()

# 지도를 보여 주는 창(see): 바탕을 덮지 않고, 창 밖(지도)을 누르면 지도가 받는다. 건설 창이 떠 있는 동안(담당 무장 표가 그 위에 겹쳐도) 아래 창과 단추 줄은 숨긴다
s = rep(s, "  var m = $('modal'); m.innerHTML = '<div class=\"dlg\">' + MODAL.render() + '</div>'; m.classList.add('on');\n  if (st) {",
           "  var m = $('modal'); m.innerHTML = '<div class=\"dlg\">' + MODAL.render() + '</div>'; m.classList.add('on');\n  m.classList.toggle('see', !!MODAL.see); $('app').classList.toggle('seeing', !!devOf());\n  if (st) {")
s = rep(s, "function closeDialog() { MSTACK.length = 0; MODAL = null; var m = $('modal'); m.classList.remove('on'); m.innerHTML = ''; paintRet(); }",
           "function closeDialog() { MSTACK.length = 0; MODAL = null; var m = $('modal'); m.classList.remove('on'); m.classList.remove('see'); $('app').classList.remove('seeing'); m.innerHTML = ''; paintRet(); }")

s = rep(s, "  return out.length ? '옆: ' + out.join(' · ') : '옆에 시설 없음 — 누르면 짓습니다';\n}",
"""  return out.length ? '옆: ' + out.join(' · ') : '옆에 시설 없음';
}
/* ---------- 건설 자리 ----------
   건설을 고른 동안(거점의 시설 탭, '무엇을 지을까요' 창과 그 위에 겹친 담당 무장 표) 지도는 어두워지고 지을 수 있는 빈 부지만 밝다 — 그리는 일은 ui3d.js 의 spotDraw.
   빈 부지에는 목록과 지도에서 같은 번호가 붙는다(b.plots 의 순서대로 1, 2, 3 …). */
function emptyLots(b) { var out = []; for (var i = 0; i < b.plots.length; i++) if (!b.plots[i].fac) out.push(i); return out; }
function lotNo(b, pi) { return emptyLots(b).indexOf(pi) + 1; }
function lotMark(n) { return n >= 1 && n <= 20 ? String.fromCharCode(0x245F + n) : '(' + n + ')'; }      // ① ② ③ …
function buildWhy(b) {                                         // 지금 이 거점에서 아무것도 지을 수 없는 까닭('' = 지을 수 있다)
  if (!idleOfficers(b).length) return '쉬는 무장이 없습니다';
  if (b.gold < minFacCost()) return '금이 모자랍니다 (' + minFacCost() + ' 필요)';
  if (!needAP(b.owner, AP.develop)) return '행동력이 모자랍니다';
  return '';
}
function devOf() { if (MODAL && MODAL.dev) return MODAL.dev; for (var i = MSTACK.length - 1; i >= 0; i--) if (MSTACK[i].d.dev) return MSTACK[i].d.dev; return null; }
function buildView() {
  if (!G || G.over || UI.play || UI.busy) return null;
  var d = devOf(), b = d ? G.bases[d.b] : (SHEET && SHEET.fac ? SHEET.fac() : null);
  if (!b || b.owner !== G.player || b.kind !== 'city') return null;
  var why = buildWhy(b), pi = d ? d.pi : -1, sig = b.id + '/' + pi + '/' + why + '/', lots = [], facs = [], n = 0;
  for (var i = 0; i < b.plots.length; i++) {
    var p = b.plots[i];
    if (p.fac) { facs.push({ c: p.c, r: p.r, n: FAC[p.fac.t].name, done: p.fac.done }); sig += 'f' + i + p.fac.t + (p.fac.done ? '' : 'c') + ','; }
    else { var ok = !why && !UAT[K(p.c, p.r)]; lots.push({ i: i, c: p.c, r: p.r, n: ++n, ok: ok }); sig += i + (ok ? '' : 'x') + ','; }
  }
  if (!lots.length) return null;                               // 빈 부지가 없으면 비출 것이 없다
  return { b: b, pi: pi, why: why, lots: lots, facs: facs, sig: sig };
}
/* '무엇을 지을까요' 창이 떠 있는 동안 지도를 눌렀다: 다른 빈 부지면 자리를 바꾸고, 그 밖이면 창을 닫는다 */
function devTap(c, r) {
  var d = MODAL.dev, b = G.bases[d.b], pl = plotAt(c, r);
  if (pl && pl.base === b && !pl.plot.fac) {
    if (UAT[K(c, r)]) { toast('부대가 서 있는 칸에는 지을 수 없습니다'); return; }
    if (pl.i !== d.pi) { d.pi = pl.i; sfx('ui'); refreshDialog(); }
    return;
  }
  backDialog();
}
/* 이 자리에 지으면 늘어나는 수입(금/월, 병량/분기) — 수입 셈(goldIncome·foodIncome)을 그대로 돌려 본 값이라 인접·치안·특기가 다 들어 있다 */
function gainAt(b, pi, t) {
  var p = b.plots[pi], g0 = goldIncome(b), f0 = foodIncome(b);
  p.fac = { t: t, lv: 1, done: true };
  var g1 = goldIncome(b), f1 = foodIncome(b);
  p.fac = null;
  return { gold: g1 - g0, food: f1 - f0 };
}
/* 카드 한 줄: 이 자리에 이 시설을 지으면 [글, 빛깔('' · ok · no · warn)] */
function lotEffect(b, pi, t) {
  var g, pair = { mint: 'market', granary: 'farm' }[t];
  if (t === 'market') return ['금 +' + fmt(gainAt(b, pi, t).gold) + '/월', ''];
  if (t === 'farm') return ['병량 +' + fmt(gainAt(b, pi, t).food) + '/분기', ''];
  if (pair) {                                                  // 조폐·곡창: 옆의 시장·농장 수입을 늘린다(한 곳에 둘까지)
    g = gainAt(b, pi, t); g = t === 'mint' ? g.gold : g.food;
    if (g > 0) return [(t === 'mint' ? '금 +' + fmt(g) + '/월' : '병량 +' + fmt(g) + '/분기'), ''];
    if (adjFacCount(b, pi, pair)) return ['효과 없음 (2곳까지)', 'no'];                              // 옆의 시장·농장에 이미 둘이 붙어 있다
    var p = b.plots[pi], soon = nbrs(p.c, p.r).some(function (q) { var x = PAT[K(q[0], q[1])], f = x && x.b === b.id ? b.plots[x.i].fac : null; return !!f && f.t === pair && !f.done; });
    return soon ? ['옆 ' + FAC[pair].name + ' 완공 뒤 효과', 'warn'] : ['옆에 ' + FAC[pair].name + ' 없음', 'no'];
  }
  var lv = bestFacLv(b, t), use = { barracks: '징병', smithy: '창·극·노 생산', stable: '군마 생산', workshop: '충차 생산' }[t];
  if (!lv) return b.plots.some(function (q) { return q.fac && q.fac.t === t; }) ? ['이미 짓는 중', 'warn'] : [use, ''];
  if (lv < 3 && adjFacCount(b, pi, t)) return ['옆 ' + FAC[t].name + '과 합병 가능', 'ok'];      // 같은 시설이 옆에 있으면 합쳐서 레벨을 올릴 수 있다
  return ['이미 있음 (Lv' + lv + ')', 'warn'];                                                  // 떨어진 자리에 하나 더 지어도 쓰이는 것은 레벨 높은 쪽 하나다
}""")

s = rep(s, "  if (UI.busy || !G || G.over || MODAL) return;\n  var k = K(c, r), u = UAT[k] || null, b = baseAt(c, r), pl = plotAt(c, r), su = selUnit();",
           "  if (UI.busy || !G || G.over) return;\n  if (MODAL) { if (MODAL.dev) devTap(c, r); return; }\n  var k = K(c, r), u = UAT[k] || null, b = baseAt(c, r), pl = plotAt(c, r), su = selUnit();")

s = rep(s, "  return {\n    on: on,\n    render: function () {\n      var b = B(), mine = b.owner === G.player, city = b.kind === 'city', i;",
           "  return {\n    on: on,\n    fac: function () { var b = B(); return (st.tab === 'fac' && b.owner === G.player && b.kind === 'city') ? b : null; },      // 시설 탭을 보는 중 = 건설 자리를 비춘다\n    render: function () {\n      var b = B(), mine = b.owner === G.player, city = b.kind === 'city', i;")

s = rep(s, """        h += '<div class="rows">';
        for (var pass = 0; pass < 2; pass++) for (i = 0; i < b.plots.length; i++) {
          var fc = b.plots[i].fac;
          if ((pass === 0) !== !fc) continue;
          if (!fc) h += '<button class="row" type="button" data-a="plot" data-v="' + i + '"><span class="th" style="display:flex;align-items:center;justify-content:center;font-size:22px;color:var(--seal)">＋</span><span class="mid"><span class="nm">빈 부지</span><span class="ds">' + plotNear(b, i) + '</span></span></button>';
          else h +=""",
"""        var why = buildWhy(b), nE = emptyLots(b).length, nF = b.plots.length - nE;
        if (nE) h += '<div class="sec">빈 부지 <em class="cnt">' + nE + '</em></div>' + (why ? '<p class="note lotw">지금은 지을 수 없습니다 — ' + why + '</p>' : '') + '<div class="lots">';       // 빈 부지는 번호 단추 한 줄(지도의 번호와 같다) — 옆에 무엇이 있는지는 지도와 고르는 창이 알려 준다
        for (var pass = 0; pass < 2; pass++) for (i = 0; i < b.plots.length; i++) {
          var fc = b.plots[i].fac;
          if (pass === 1 && i === 0) h += (nE ? '</div>' : '') + (nF ? '<div class="sec">지은 시설 <em class="cnt">' + nF + '</em></div>' : '') + '<div class="rows">';
          if ((pass === 0) !== !fc) continue;
          if (!fc) h += '<button class="lot' + (why || UAT[K(b.plots[i].c, b.plots[i].r)] ? ' no' : '') + '" type="button" data-a="plot" data-v="' + i + '" aria-label="빈 부지 ' + lotNo(b, i) + '">' + lotNo(b, i) + '</button>';
          else h +=""")

s = rep(s, """function flowDevelop(b, pi) {
  if (b.owner !== G.player) return;
  if (!idleOfficers(b).length) return toast('행동할 수 있는 무장이 없습니다');
  showDialog({
    render: function () {
      var h = dlgHead(b.n + ' — 무엇을 지을까요') + '<div class="dlg-b"><p class="note">보유 금 ' + fmt(b.gold) + ' · 행동력 ' + AP.develop + ' 소모</p><div class="lst-opt">';
      for (var i = 0; i < FAC_ORDER.length; i++) { var F = FAC[FAC_ORDER[i]], ok = b.gold >= F.cost; h += '<button class="row' + (ok ? '' : ' dim') + '" type="button" data-a="f" data-v="' + FAC_ORDER[i] + '">' + thumb(FAC_ORDER[i], 'lg') + '<span class="mid"><span class="nm">' + F.name + '</span><span class="ds">' + F.desc + '</span></span><span class="rt">금 <b>' + F.cost + '</b></span></button>'; }
      return h + '</div></div>';
    },
    on: { f: function (el) {
      var t = el.getAttribute('data-v'), F = FAC[t];
      if (b.gold < F.cost) return toast('금이 부족합니다 (' + F.cost + ' 필요)');
      pickOfficers({ push: true, title: F.name + ' 건설 — 담당 무장',""",
"""function flowDevelop(b, pi) {
  if (b.owner !== G.player) return;
  var why = buildWhy(b);
  if (why) return toast('지금은 지을 수 없습니다 — ' + why);
  if (UAT[K(b.plots[pi].c, b.plots[pi].r)]) return toast('부대가 서 있는 칸에는 지을 수 없습니다');
  var dev = { b: b.id, pi: pi };                                  // 고른 자리 — 창이 떠 있는 동안 지도에서 다른 빈 부지를 누르면 바뀐다(devTap)
  showDialog({
    dev: dev, see: true,
    render: function () {
      var h = dlgHead(b.n + ' ' + lotMark(lotNo(b, dev.pi)) + ' — 무엇을 지을까요') + '<div class="dlg-b"><p class="note fnote"><span>' + plotNear(b, dev.pi) + '</span><span>보유 금 ' + fmt(b.gold) + ' · 행동력 −' + AP.develop + '</span></p><div class="lst-opt fgrid">';
      for (var i = 0; i < FAC_ORDER.length; i++) {
        var F = FAC[FAC_ORDER[i]], ok = b.gold >= F.cost, ef = lotEffect(b, dev.pi, FAC_ORDER[i]);
        h += '<button class="row fcard' + (ok ? '' : ' dim') + '" type="button" data-a="f" data-v="' + FAC_ORDER[i] + '">' + thumb(FAC_ORDER[i]) + '<span class="mid"><span class="nm">' + F.name + '<i class="cost">금 ' + F.cost + '</i></span><span class="ds' + (ef[1] ? ' ' + ef[1] : '') + '">' + ef[0] + '</span></span></button>';
      }
      return h + '</div></div>';
    },
    on: { f: function (el) {
      var t = el.getAttribute('data-v'), F = FAC[t], pi = dev.pi;
      if (b.gold < F.cost) return toast('금이 부족합니다 (' + F.cost + ' 필요)');
      pickOfficers({ push: true, title: F.name + ' 건설 ' + lotMark(lotNo(b, pi)) + ' — 담당 무장',""")
s = rep(s, """        function (os) { var r = cmdDevelop(b, pi, t, ids(os)); return done(r, r.ok ? F.name + ' 착공 — ' + days(r.turns) + ' 뒤 완공' : '', 'hammer'); });""",
           """        function (os) { var r = cmdDevelop(b, pi, t, ids(os)); if (r.ok) { flashHex(b.plots[pi].c, b.plots[pi].r, SEAL); floatText(b.plots[pi].c, b.plots[pi].r, F.name + ' 착공', SEAL); } return done(r, r.ok ? F.name + ' 착공 — ' + days(r.turns) + ' 뒤 완공' : '', 'hammer'); });""")
# 탭 이름: '시설' → '건설'(지을 자리를 고르는 곳이다 — 이미 지은 시설도 이 탭 아래쪽에 그대로 있다)
s = rep(s, "[['home', '내정'], ['mil', '출진'], ['men', '인재'], ['fac', '시설']]", "[['home', '내정'], ['mil', '출진'], ['men', '인재'], ['fac', '건설']]")
s = rep(s, "<p>도시를 누르면 명령 패널이 열립니다. 도시 둘레의 밝은 칸이 부지이고, 누르면 시설을 짓습니다. 같은 시설이 붙어 있으면",
           "<p>도시를 누르면 명령 창이 열립니다. <b>건설</b> 탭을 열면 지도가 어두워지고 <b>지을 수 있는 빈 부지만 밝게</b> 번호와 함께 보입니다 — 밝은 칸이나 같은 번호의 줄을 누르고 시설을 고르면 됩니다(고른 자리는 붉은 테두리). 칸이 점선으로만 보이면 지금은 지을 수 없다는 뜻이고, 까닭(쉬는 무장·금·행동력)이 창에 적힙니다. 같은 시설이 붙어 있으면")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- style.css
p = 'src/style.css'; s = io.open(p, encoding='utf-8').read()
s += """
/* ---- v0.9.2 건설 자리 비추기 ---- */
#spot { position: absolute; inset: 0; width: 100%; height: 100%; z-index: 2; pointer-events: none; display: none; }
#spot.on { display: block; }
#app.building #mini { display: none; }                         /* 건설 자리를 보는 동안에는 작은 지도가 칸을 가리지 않게 */
#modal.see { background: none; pointer-events: none; }         /* 지도를 보여 주는 창: 바탕을 덮지 않고, 창 밖은 지도가 받는다 */
#modal.see .dlg { pointer-events: auto; max-height: 50%; }
#app.seeing #sheet, #app.seeing #bar { visibility: hidden; }
#app.building #toast { top: 96px; }                            /* 알림이 칸을 가리지 않게 위로 */
.note.fnote { display: flex; justify-content: space-between; gap: 12px; margin: 0 1px 7px; font-variant-numeric: tabular-nums; }
.note.fnote span:first-child { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.note.fnote span:last-child { flex: none; color: var(--ink-2); }
.lst-opt.fgrid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.row.fcard { min-height: 56px; padding: 4px 8px 4px 6px; gap: 7px; }
.row.fcard .th { width: 42px; height: 36px; }
.row.fcard .nm { display: flex; align-items: baseline; gap: 6px; }
.row.fcard .nm .cost { margin-left: auto; font: 700 12px var(--font-body); font-style: normal; color: var(--ink-2); font-variant-numeric: tabular-nums; }
.row.fcard .ds.no { color: var(--seal); font-weight: 700; }
.row.fcard .ds.ok { color: #2f6b4f; font-weight: 700; }
.row.fcard .ds.warn { color: var(--ochre); font-weight: 700; }
.lots { display: flex; flex-wrap: wrap; gap: 8px 9px; margin: 2px 0 2px; }
.lot { width: 42px; height: 42px; border-radius: 50%; border: 1.6px solid var(--ink); background: var(--paper); box-shadow: 0 0 0 2.5px #e6b63c; font: 900 18px var(--font-display); color: var(--ink); display: flex; align-items: center; justify-content: center; padding: 0 0 1px; margin: 3px; }
.lot.no { border: 1.4px dashed var(--dim); box-shadow: none; color: var(--dim); background: none; }
.note.lotw { margin: -2px 0 6px; padding: 6px 9px; border-left: 4px solid var(--seal); background: var(--paper-2); color: var(--ink-2); font-size: 12.5px; }
@media (min-width: 700px) { #modal.see { align-items: flex-end; } #modal.see .dlg { margin-bottom: 0; } }
@media (max-height: 720px) { #modal.see .dlg { max-height: 58%; } }          /* 낮은 화면: 여덟 카드가 다 보이도록 조금 더 */
"""
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
