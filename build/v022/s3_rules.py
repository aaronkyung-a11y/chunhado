# v0.22 (3) 규칙 — 요청 4 · 7
#   ④ "홍농 농장 흡수 합병이 안 되는 현상(스크린샷)"
#      까닭(0.21 에서 내가 만든 버그): 관문의 능선은 '칸과 칸 사이의 변'을 막는데, 0.21 의 능선은 가장 싼 변만 골라 부지에 닿는 변이 12곳 있었고(허창 8 · 홍농 3 · 한중 1), 그 가운데 9곳(허창 6 · 홍농 3)이 부지와 부지 사이를 지나갔다.
#        합병은 '이웃한 부지'를 찾을 때 능선 너머를 이웃으로 치지 않는 nbrs() 를 썼다 → 눈으로는 붙어 있는 농장 ⑥ · ⑦ 이 "인접한 같은 시설 필요".
#        (조폐 · 곡창이 옆의 시장 · 농장에 주는 +50% 도 같은 까닭으로 끊겼다.)
#      고친 것 둘:
#        (가) 능선을 다시 세운다 — 부지 칸과 성에서 2칸 안의 칸에 닿는 변은 막지 않는다(tools/gates22.py, 변 143 → 149곳). build/v022/apply.sh 가 돌린다.
#        (나) 한 성의 부지끼리의 '옆'은 능선과 상관없이 센다(nbrsAll) — 합병 · 조폐 · 곡창 · AI 의 자리 고르기 · 건설 창의 안내. 지도 자료가 어떻든 다시는 끊기지 않는다.
#   ⑦ "성을 점령하면 일부 시설물은 사라지게 해줘. 전부 다는 아니고 일부만"
#      남의 거점이 함락되면(맞붙어 빼앗든, 멀리서 쏘아 빈 거점으로 만들든) 다 지은 시설 가운데 일부가 부서져 빈 부지가 된다.
#        부서지는 수 = 다 지은 시설 수 × SACK.rate(반올림), 적어도 SACK.min 곳, 그러나 SACK.keep 곳은 반드시 남는다(시설이 둘 이하면 하나도 부서지지 않는다).
#        어느 것이 부서지는지는 그 턴 · 그 거점으로 정해지는 주사위(omenRoll — 판의 난수를 쓰지 않아 다른 일의 흐름을 건드리지 않는다).
#      주인 없는 거점에 걸어 들어가 차지할 때는 부서지지 않는다(함락이 아니다). 짓다 만 시설이 버려지는 것은 전과 같다.
import io, os
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)

# ---------------- core.js ----------------
s = rd('src/core.js')
s = rep(s, """  for (var i = 0; i < 6; i++) { var cc = c + d[i][0], rr = r + d[i][1]; if (inMap(cc, rr) && !WALLB[k6 + i]) out.push([cc, rr]); }      // v0.21: 능선 너머는 이웃이 아니다
  return out;
}
""", """  for (var i = 0; i < 6; i++) { var cc = c + d[i][0], rr = r + d[i][1]; if (inMap(cc, rr) && !WALLB[k6 + i]) out.push([cc, rr]); }      // v0.21: 능선 너머는 이웃이 아니다
  return out;
}
/* v0.22: 능선을 따지지 않는 이웃 — 한 성의 부지끼리의 '옆'(합병 · 조폐 · 곡창). 걷거나 치는 데에는 쓰지 않는다 */
function nbrsAll(c, r) {
  var d = (r & 1) ? NB_ODD : NB_EVEN, out = [];
  for (var i = 0; i < 6; i++) { var cc = c + d[i][0], rr = r + d[i][1]; if (inMap(cc, rr)) out.push([cc, rr]); }
  return out;
}
""")
s = rep(s, "  var p = b.plots[pi], n = 0, ns = nbrs(p.c, p.r);", "  var p = b.plots[pi], n = 0, ns = nbrsAll(p.c, p.r);      // v0.22: 부지끼리의 옆은 능선과 상관없다")
s = rep(s, """  if (!f || !f.done || f.lv >= 3 || !facHasLv(f.t)) return out;
  var ns = nbrs(p.c, p.r);""", """  if (!f || !f.done || f.lv >= 3 || !facHasLv(f.t)) return out;
  var ns = nbrsAll(p.c, p.r);                                // v0.22: 부지끼리의 옆은 능선과 상관없다(0.21 에서는 능선이 부지 사이를 지나 합병이 막혔다)""")

# 함락하면 시설의 일부가 부서진다
s = rep(s, "function captureBase(b, u) {\n  var old = b.owner, i;\n", """/* v0.22: 함락하면 시설의 일부가 부서진다 — 전부는 아니다.
   다 지은 시설 n 곳 가운데 round(n × SACK.rate) 곳(적어도 SACK.min 곳)이 사라져 빈 부지가 된다. 다만 SACK.keep 곳은 반드시 남는다(n 이 keep 이하면 하나도 부서지지 않는다).
   어느 것인지는 그 턴 · 그 거점 · 그 부지로 정해지는 주사위(omenRoll)의 작은 차례 — 판의 난수(rnd)는 쓰지 않는다. 돌려주는 값: 부서진 시설의 종류들 */
var SACK = { rate: 0.3, min: 1, keep: 2 };
function sackCount(n) { return Math.max(0, Math.min(Math.max(SACK.min, Math.round(n * SACK.rate)), n - SACK.keep)); }
function sackBase(b) {
  var done = [], lost = [], i;
  for (i = 0; i < b.plots.length; i++) { var f = b.plots[i].fac; if (f && f.done) done.push([omenRoll('sack|' + b.id + '|' + i), i]); }
  var k = sackCount(done.length);
  done.sort(function (x, y) { return x[0] - y[0] || x[1] - y[1]; });
  for (i = 0; i < k; i++) { var pi = done[i][1]; lost.push(b.plots[pi].fac.t); b.plots[pi].fac = null; }
  return lost;
}
function sackText(lost) {                                    // '시장 2 · 농장'
  var n = {}, out = [];
  lost.forEach(function (t) { n[t] = (n[t] || 0) + 1; });
  FAC_ORDER.forEach(function (t) { if (n[t]) out.push(FAC[t].name + (n[t] > 1 ? ' ' + n[t] : '')); });
  return out.join(' · ');
}
function captureBase(b, u) {
  var old = b.owner, i, lost = [];
""")
s = rep(s, """  ev({ t: 'fall', b: b.id, by: u.f, old: old });
  b.owner = u.f; b.troops = 0;""", """  if (old >= 0) {                                              // v0.22: 싸움에 시설의 일부가 부서진다
    lost = sackBase(b);
    if (lost.length) logMsg(b.n + '의 시설 ' + lost.length + '곳이 싸움에 부서졌다 (' + sackText(lost) + ')', b.c, b.r, old, old === G.player || u.f === G.player ? 2 : 0);
  }
  ev({ t: 'fall', b: b.id, by: u.f, old: old, lost: lost.length });
  b.owner = u.f; b.troops = 0;""")
s = rep(s, """  enterBase(u, b);
  checkFaction(old);
  checkVictory();
}""", """  enterBase(u, b);
  checkFaction(old);
  checkVictory();
  return lost;
}""")
s = rep(s, """      res.fell = true;
      if (!ranged2) captureBase(b, u);
      else {   // 원거리로 무너뜨리면 빈 거점이 된다
        var old = b.owner, os = baseOfficers(b), i;""", """      res.fell = true;
      if (!ranged2) { var lostC = captureBase(b, u); if (lostC && lostC.length) res.sacked = lostC; }
      else {   // 원거리로 무너뜨리면 빈 거점이 된다
        var old = b.owner, os = baseOfficers(b), i;
        var lostR = sackBase(b);                               // v0.22: 멀리서 무너뜨려도 시설의 일부가 부서진다
        if (lostR.length) { res.sacked = lostR; logMsg(b.n + '의 시설 ' + lostR.length + '곳이 싸움에 부서졌다 (' + sackText(lostR) + ')', b.c, b.r, old, old === G.player || u.f === G.player ? 2 : 0); }""")
wr('src/core.js', s)

# ---------------- ai.js: 지을 자리를 고를 때의 '옆' ----------------
s = rd('src/ai.js')
s = rep(s, "      var p = b.plots[free[i]], ns = nbrs(p.c, p.r), cnt = 0;", "      var p = b.plots[free[i]], ns = nbrsAll(p.c, p.r), cnt = 0;")
wr('src/ai.js', s)

# ---------------- ui_panels.js: 건설 창의 안내 · 결과의 말 ----------------
s = rd('src/ui_panels.js')
s = rep(s, "  var p = b.plots[i], ns = nbrs(p.c, p.r), cnt = {}, out = [];", "  var p = b.plots[i], ns = nbrsAll(p.c, p.r), cnt = {}, out = [];")
s = rep(s, "    var p = b.plots[pi], soon = nbrs(p.c, p.r).some(function (q) {", "    var p = b.plots[pi], soon = nbrsAll(p.c, p.r).some(function (q) {")
s = rep(s, "  if (res.fell) msg = res.tname + ' 함락!';", "  if (res.fell) msg = res.tname + ' 함락!' + (res.sacked && res.sacked.length ? ' · 시설 ' + res.sacked.length + '곳 소실 (' + sackText(res.sacked) + ')' : '');      // v0.22: 함락하면 시설의 일부가 부서진다")
s = rep(s, "+ '군 → ' + facName(e.by) + '군)' + (mine ? '<br>우리 거점을 잃었습니다' : '')", "+ '군 → ' + facName(e.by) + '군)' + (e.lost ? ' · 시설 ' + e.lost + '곳 소실' : '') + (mine ? '<br>우리 거점을 잃었습니다' : '')")
wr('src/ui_panels.js', s)
print('s3 ok')
