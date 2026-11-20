# v0.9.1 전법(2/2): "추천하는 행동하고" = 0.9 보고의 b(전법 더 누르기)
#  재 본 것(tests/tac91.js, 같은 싸움 장면 1,952개 · 보통 공격 = 1): 0.9 의 전법은 피해 ×1.33 · 받는 반격 ×0.74. 약한 쪽이 강한 쪽을 쳐도 반격이 ×0.87 이라 절반 가까운 장면(46%)에서 전법이 이득이었다.
#  바꾼 것
#   1) 성공해도 반격은 보통 공격만큼 받는다(0.4 → 0.55). 갈퀴·돌파, 멀리서 쏜 전법, 밀려나 떨어진 적은 전과 같이 반격하지 못한다
#   2) 실패하면 더 아프다: 피해 50% → 40%, 받는 반격 0.7 → 0.85(보통 공격의 1.27배 → 1.55배)
#   3) 무장의 차이를 더 크게 본다: (내 무력×0.6 + 통솔×0.4 − 상대 통솔) × 0.6 [−24~+12] → × 0.8 [−30~+15]
#   4) 피해 배수: 한 부대만 치는 전법 −4~8%, 성공하면 반격을 받지 않는 갈퀴·돌파 −19~20%(1.25 → 1.0, 1.35 → 1.1), 여럿을 치는 횡치·선풍은 그대로.
#      대성공 1.3배 → 1.25배(궁신·기신은 거기에 +10%: 1.43 → 1.375)
#      (갈퀴·돌파를 −8% 만 내린 안도 재 보았다: 극병이 전법을 쓸 수 있는 장면의 84%에서 값싼 갈퀴가 가장 나은 전법으로 뽑혔다. −20% 로는 66%, 횡치 29%)
#   5) AI: '기대 피해가 보통 공격의 1.1배 이상'만 보던 것을, 받는 반격까지 넣어 셈한다(tacticExpect). 함께 맞는 적의 피해도 실제로 센다
#   6) 창: 전법 풀이에 전법마다 '기대 피해 · 받는 반격'을 보통 공격과 나란히 적는다. 공격 단추의 '예상'도 같은 셈(dmgBase)을 쓴다 — 전에는 내 부대가 강 위에 있을 때의 −30% 와 치명타·금강이 빠져 있었다
#  성공률의 바탕(적성 55/63/71/80)은 그대로 둔다 — 비슷한 상대에게는 전과 같이 통하고, 실패의 값만 비싸진다
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)

p = 'src/data.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "  /* v0.8: 피해 배수를 7~14%(평균 9.7%) 내렸다(v0.7: 돌출 1.35 나선첨 1.5 이단첨 1.8 / 갈퀴 1.35 횡치 1.25 선풍 1.15 / 화시 1.2 관시 1.45 난사 1.15 / 돌격 1.45 돌파 1.5 돌진 1.85).",
           "  /* v0.9.1: 피해 배수를 다시 내렸다(v0.8~0.9: 돌출 1.25 나선첨 1.35 이단첨 1.55 / 갈퀴 1.25 횡치 1.15 선풍 1.05 / 화시 1.1 관시 1.3 난사 1.05 / 돌격 1.3 돌파 1.35 돌진 1.6).\n     한 부대만 치는 전법 −4~8%. 성공하면 반격을 받지 않는 갈퀴·돌파는 −19~20%(반격을 피하는 값). 여럿을 치는 횡치·선풍은 그대로(한 부대만 보면 가장 약하다).\n     v0.8: 피해 배수를 7~14%(평균 9.7%) 내렸다(v0.7: 돌출 1.35 나선첨 1.5 이단첨 1.8 / 갈퀴 1.35 횡치 1.25 선풍 1.15 / 화시 1.2 관시 1.45 난사 1.15 / 돌격 1.45 돌파 1.5 돌진 1.85).")
for a, b in [("id: 'dolchul', name: '돌출', cost: 10, mult: 1.25,", "id: 'dolchul', name: '돌출', cost: 10, mult: 1.15,"),
             ("id: 'naseon',  name: '나선첨', cost: 15, mult: 1.35,", "id: 'naseon',  name: '나선첨', cost: 15, mult: 1.3,"),
             ("id: 'idan',    name: '이단첨', cost: 20, mult: 1.55,", "id: 'idan',    name: '이단첨', cost: 20, mult: 1.45,"),
             ("id: 'galkwi',   name: '갈퀴', cost: 10, mult: 1.25,", "id: 'galkwi',   name: '갈퀴', cost: 10, mult: 1.0,"),
             ("id: 'hwasi',  name: '화시', cost: 10, mult: 1.1,", "id: 'hwasi',  name: '화시', cost: 10, mult: 1.05,"),
             ("id: 'gwansi', name: '관시', cost: 15, mult: 1.3,", "id: 'gwansi', name: '관시', cost: 15, mult: 1.25,"),
             ("id: 'nansa',  name: '난사', cost: 20, mult: 1.05,", "id: 'nansa',  name: '난사', cost: 20, mult: 1.0,"),
             ("id: 'dolgyeok', name: '돌격', cost: 10, mult: 1.3,", "id: 'dolgyeok', name: '돌격', cost: 10, mult: 1.25,"),
             ("id: 'dolpa',    name: '돌파', cost: 15, mult: 1.35,", "id: 'dolpa',    name: '돌파', cost: 15, mult: 1.1,"),
             ("id: 'doljin',   name: '돌진', cost: 20, mult: 1.6,", "id: 'doljin',   name: '돌진', cost: 20, mult: 1.5,")]:
    s = rep(s, a, b)
s = rep(s, "var TACTIC_K = { okCounter: 0.4, failDmg: 0.5, failCounter: 0.7, crit: 1.3, critGod: 1.43, stat: 0.6, statLo: -24, statHi: 12 };   // 성공했을 때 받는 반격 / 실패했을 때 주는 피해·받는 반격 (보통 공격의 반격은 0.55). v0.7: 0.25 / 0.6 / 0.4",
"""/* 전법의 숫자(보통 공격의 피해 = 1, 보통 공격이 받는 반격 = 0.55)
   okCounter: 성공했을 때 받는 반격 · failDmg: 실패했을 때 주는 피해 · failCounter: 실패했을 때 받는 반격 · crit: 대성공 배수(critGod: 궁신·기신)
   stat: 무장 항의 기울기 — (내 부대 최고 무력×0.6 + 주장 통솔×0.4 − 상대 부대 최고 통솔) × stat, statLo ~ statHi
   v0.9.1: 성공해도 반격은 보통 공격만큼, 실패는 더 아프게, 무장의 차이는 더 크게.   v0.8~0.9: 0.4 / 0.5 / 0.7 / 1.3(1.43) / 0.6 [−24~+12]   v0.7: 0.25 / 0.6 / 0.4 */
var TACTIC_K = { okCounter: 0.55, failDmg: 0.4, failCounter: 0.85, crit: 1.25, critGod: 1.375, stat: 0.8, statLo: -30, statHi: 15 };""")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()
# 주사위를 뺀 피해
s = rep(s, """function dmgUU(a, d, mult, ranged) {
  var x = 620 * Math.pow(uAtk(a) / Math.max(10, uDef(d)), 0.9) * troopFactor(a.troops) * mult;""",
"""/* 주사위를 뺀 피해(v0.9.1) — dmgUU 가 여기에 0.92~1.08 을 곱한다. 창의 '예상'과 전법의 기대값(tacticExpect)이 이 값을 쓴다 */
function dmgBase(a, d, mult, ranged) {
  var x = 620 * Math.pow(uAtk(a) / Math.max(10, uDef(d)), 0.9) * troopFactor(a.troops) * mult;""")
s = rep(s, """  if (ta === 'w') x *= 0.7;
  if (d.status === 'confuse') x *= 1.25;
  x *= 0.92 + rnd() * 0.16;
  return Math.max(30, Math.round(x));
}""", """  if (ta === 'w') x *= 0.7;
  if (d.status === 'confuse') x *= 1.25;
  return x;
}
function dmgUU(a, d, mult, ranged) {
  var x = dmgBase(a, d, mult, ranged);
  x *= 0.92 + rnd() * 0.16;
  return Math.max(30, Math.round(x));
}""")
s = rep(s, "        + 무장: (내 부대 최고 무력×0.6 + 내 주장 통솔×0.4 − 적 부대 최고 통솔) × 0.6      [−24 ~ +12]",
           "        + 무장: (내 부대 최고 무력×0.6 + 내 주장 통솔×0.4 − 적 부대 최고 통솔) × 0.8      [−30 ~ +15]   (v0.8~0.9: × 0.6 [−24 ~ +12])")
# 함께 맞는 적을 한곳에서 고른다(unitTactic0 과 기대값이 같은 목록을 쓴다)
s = rep(s, """  // 부가 대상(먼저 목록을 잡아 둔다)
  var others = [], i, ns, q;
  if (tac.arc) { ns = nbrs(u.c, u.r); for (i = 0; i < ns.length; i++) { q = UAT[K(ns[i][0], ns[i][1])]; if (q && q.f !== u.f && q !== d && hdist(q.c, q.r, d.c, d.r) === 1) others.push([q, e.side || 0.8]); } }
  if (tac.all) { ns = nbrs(u.c, u.r); for (i = 0; i < ns.length; i++) { q = UAT[K(ns[i][0], ns[i][1])]; if (q && q.f !== u.f && q !== d) others.push([q, 1.0]); } }
  if (tac.pierce) { var bh = behindHex(u, d); if (bh && inMap(bh[0], bh[1])) { q = UAT[K(bh[0], bh[1])]; if (q && q.f !== u.f) others.push([q, e.side || 0.8]); } }
  if (tac.splash) { ns = nbrs(d.c, d.r); for (i = 0; i < ns.length; i++) { q = UAT[K(ns[i][0], ns[i][1])]; if (q && q.f !== u.f && q !== d) others.push([q, e.side || 0.6]); } }
""", """  // 부가 대상(먼저 목록을 잡아 둔다)
  var others = tacticOthers(u, d, tac, e), i;
""")
s = rep(s, """function unitTactic0(u, tac, t) {
  if (u.done) return ERR('이미 행동을 마쳤습니다');""", """/* 전법에 함께 맞는 적들: [부대, 피해 비율] — 밀어내기 전의 자리로 잡는다. e = 이번에 적용되는 효과(대성공이면 강화된 것) */
function tacticOthers(u, d, tac, e) {
  var others = [], i, ns, q;
  if (tac.arc) { ns = nbrs(u.c, u.r); for (i = 0; i < ns.length; i++) { q = UAT[K(ns[i][0], ns[i][1])]; if (q && q.f !== u.f && q !== d && hdist(q.c, q.r, d.c, d.r) === 1) others.push([q, e.side || 0.8]); } }
  if (tac.all) { ns = nbrs(u.c, u.r); for (i = 0; i < ns.length; i++) { q = UAT[K(ns[i][0], ns[i][1])]; if (q && q.f !== u.f && q !== d) others.push([q, 1.0]); } }
  if (tac.pierce) { var bh = behindHex(u, d); if (bh && inMap(bh[0], bh[1])) { q = UAT[K(bh[0], bh[1])]; if (q && q.f !== u.f) others.push([q, e.side || 0.8]); } }
  if (tac.splash) { ns = nbrs(d.c, d.r); for (i = 0; i < ns.length; i++) { q = UAT[K(ns[i][0], ns[i][1])]; if (q && q.f !== u.f && q !== d) others.push([q, e.side || 0.6]); } }
  return others;
}
/* 적 뒤로 n 칸까지 가운데 밀어낼 수 있는 칸 수 */
function pushRoom(u, d, n) {
  var dx = cubeX(d.c, d.r) - cubeX(u.c, u.r), dz = d.r - u.r, c = d.c, r = d.r, room = 0;
  for (var i = 0; i < n; i++) { var nx = stepDir(c, r, dx, dz); if (!canPushInto(nx[0], nx[1], d)) break; c = nx[0]; r = nx[1]; room++; }
  return room;
}
/* 보통 공격 한 번의 기대값(주사위 없이): 주는 피해 · 받는 반격. 맞은 뒤 줄어든 병력으로 반격이 약해지는 몫과 일기토는 넣지 않는다 */
function attackExpect(u, d) {
  var ranged = hdist(u.c, u.r, d.c, d.r) > 1, quiet = d.status === 'confuse' || d.status === 'rumor', bow = d.type === 'bow';
  var cN = quiet ? 0 : (ranged ? (bow ? 0.4 : 0) : 0.55 * (bow ? 0.6 : 1));
  return { dealt: dmgBase(u, d, 1, ranged) * (uHas(d, '금강') ? 0.65 : 1) * ((critNormal(u, d) ? 1.3 : 1) + (uHas(u, '연전') ? 0.4 : 0)),
    recv: dmgBase(d, u, 1, ranged) * (uHas(u, '금강') ? 0.65 : 1) * cN * (uHas(u, '급습') ? 0.5 : 1) };
}
/* 전법 한 번의 기대값(v0.9.1): 성공·대성공·실패를 확률대로 섞은 '주는 피해 · 받는 반격', 그리고 같은 자리에서 보통 공격을 했을 때의 값.
   넣은 것: 전법 배수 · 병력 비 · 대성공 배수 · 막힌 적을 밀 때의 +20% · 함께 맞는 적(extra) · 실패 때의 피해와 반격 · 반격을 받지 않는 경우(갈퀴·돌파, 멀리서 쏜 전법, 밀려나 떨어진 적, 혼란·위보 중인 적, 이 전법으로 혼란에 빠진 적) · 금강·철벽
   넣지 않은 것: 맞은 뒤 줄어든 병력으로 반격이 약해지는 몫, 일기토, 혼란·기력 깎기 같은 효과의 값어치 */
function tacticExpect(u, d, tac) {
  var ranged = hdist(u.c, u.r, d.c, d.r) > 1, quiet = d.status === 'confuse' || d.status === 'rumor', bow = d.type === 'bow';
  var od = tacticOdds(u, d), p = od.ok / 100, g = od.ok > 0 ? od.crit / od.ok : 0;            // g = 성공 가운데 대성공의 몫
  var kN = uHas(d, '금강') ? 0.65 : 1, kT = uHas(d, '철벽') ? 0.7 : 1;
  var e1 = tacticEff(tac, true), n0 = !ranged && tac.push ? tac.push : 0, n1 = !ranged && e1.push ? e1.push : 0;
  var room = (n0 || n1) ? pushRoom(u, d, Math.max(n0, n1)) : 0;
  var s0 = n0 && room < n0 ? 1.2 : 1, s1 = n1 && room < n1 ? 1.2 : 1;                          // 뒤가 막혀 있으면 +20%
  var AD = dmgBase(u, d, 1, ranged);
  var dealt = AD * (p * tac.mult * tacticSizeK(u, d) * kT * ((1 - g) * s0 + g * od.mult * s1) + (1 - p) * TACTIC_K.failDmg * kN);
  var os0 = tacticOthers(u, d, tac, tac), os1 = tacticOthers(u, d, tac, e1), extra = 0, i;
  for (i = 0; i < os0.length; i++) {
    var o = os0[i][0];
    extra += dmgBase(u, o, 1, hdist(u.c, u.r, o.c, o.r) > 1) * tac.mult * tacticSizeK(u, o) * (uHas(o, '철벽') ? 0.7 : 1) * ((1 - g) * os0[i][1] + g * od.mult * os1[i][1]);
  }
  extra *= p;
  var away = n0 > 0 && !tac.follow && room >= 1;                                               // 밀려나 한 칸 떨어진 적은 반격하지 못한다
  var cOk = (quiet || tac.noCounter || ranged || away) ? 0 : TACTIC_K.okCounter * (bow ? 0.6 : 1);
  cOk *= (1 - g) * (1 - confuseOdds(tac, d) / 100) + g * (1 - confuseOdds(e1, d) / 100);         // 이 전법으로 혼란에 빠진 적은 반격하지 못한다(나선첨·돌진)
  var cFl = quiet ? 0 : (ranged ? (bow ? 0.4 : 0) : TACTIC_K.failCounter * (bow ? 0.6 : 1));
  var N = attackExpect(u, d);
  return { ok: od.ok, crit: od.crit, dealt: dealt + extra, extra: extra, others: os0.length, recv: dmgBase(d, u, 1, ranged) * (uHas(u, '금강') ? 0.65 : 1) * (p * cOk + (1 - p) * cFl), nDealt: N.dealt, nRecv: N.recv };
}
function unitTactic0(u, tac, t) {
  if (u.done) return ERR('이미 행동을 마쳤습니다');""")
s = rep(s, "  if (roll >= od.ok) {                                         // 실패: 피해는 보통 공격의 절반, 반격은 보통 공격보다 크게 받는다(원거리는 노병에게만)",
           "  if (roll >= od.ok) {                                         // 실패: 피해는 보통 공격의 TACTIC_K.failDmg, 반격은 보통 공격보다 크게 받는다(원거리는 노병에게만)")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/ai.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, """    var tl = tacticList(u), bt = null, bm = 0;""", """    var tl = tacticList(u), bt = null, bm = -9;""")
s = rep(s, """      // 기대 피해(보통 공격 = 1): 성공률 × 배수 × 병력 비 × 대성공 몫 + 실패했을 때의 피해. 여럿을 치는 전법은 조금 더 쳐 준다
      var od0 = tacticOdds(u, tg), p0 = od0.ok / 100;
      var m = p0 * tl[i].mult * tacticSizeK(u, tg) * (1 + (od0.mult - 1) * od0.crit / Math.max(1, od0.ok)) + (1 - p0) * TACTIC_K.failDmg + (tl[i].all || tl[i].splash || tl[i].arc ? 0.2 * p0 : 0);
      if (m > bm) { bm = m; bt = tl[i]; }
    }
    if (bt && bm >= 1.1 && chance(85)) { aiReport(u, unitTactic(u, bt, tgt), tg); return; }      // 보통 공격보다 나을 때만 쓴다(v0.7: 가장 센 전법을 75% 확률로 무조건)""",
"""      // v0.9.1: 보통 공격과 견준 이득 = (기대 피해의 차이 − 받는 반격의 차이 × 0.6) ÷ 보통 공격의 피해. 반격의 무게 0.6 은 칠 상대를 고를 때와 같다.
      //         함께 맞는 적의 피해는 실제로 센다(v0.8~0.9: 주는 피해만 보고, 여럿을 치는 전법에는 어림으로 +0.2)
      var ex = tacticExpect(u, tg, tl[i]);
      var m = ((ex.dealt - ex.nDealt) - 0.6 * (ex.recv - ex.nRecv)) / Math.max(1, ex.nDealt);
      if (m > bm) { bm = m; bt = tl[i]; }
    }
    if (bt && bm >= 0.1 && chance(85)) { aiReport(u, unitTactic(u, bt, tgt), tg); return; }      // 보통 공격보다 나을 때만 쓴다(v0.7: 가장 센 전법을 75% 확률로 무조건)""")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "sub: d <= rg ? '예상 -' + fmt(estUU(u, t.u, 1, d > 1)) : '사거리 밖', ok: d <= rg, pri: true });",
           "sub: d <= rg ? '예상 -' + fmt(Math.round(attackExpect(u, t.u).dealt)) : '사거리 밖', ok: d <= rg, pri: true });")
s = rep(s, """      var all = TACTICS[u.type] || [], can = tacticList(u), od = tacticOdds(u, d), P = od.parts, i;""",
           """      var all = TACTICS[u.type] || [], can = tacticList(u), od = tacticOdds(u, d), P = od.parts, i, N = attackExpect(u, d);
      function vs(a, b, moreIsGood) { if (b < 1) return ''; var q = Math.round((a / b - 1) * 100); return q ? ' <em class="' + ((q > 0) === moreIsGood ? 'good' : 'bad') + '">' + (q > 0 ? '+' : '−') + Math.abs(q) + '%</em>' : ''; }      // 보통 공격과 견준 %: 피해는 많을수록, 반격은 적을수록 좋다""")
s = rep(s, """(P.skill ? ' · 특기 ' + sg(P.skill) : '') + '</p>';
      for (i = 0; i < all.length; i++) {""", """(P.skill ? ' · 특기 ' + sg(P.skill) : '') + '</p>' +
        '<p class="sum nrm">보통 공격이면 <b>피해 ' + fmt(Math.round(N.dealt)) + '</b> · <b>받는 반격 ' + fmt(Math.round(N.recv)) + '</b>쯤. 아래 <b>기대</b>는 성공·대성공·실패를 확률대로 섞은 값이고, 옆의 %는 보통 공격과 견준 것입니다.</p>';
      for (i = 0; i < all.length; i++) {""")
s = rep(s, """          '<div class="tl g"><i>대성공</i><span>피해 ' + od.mult + '배, ' + tac.gfx + (c1 && c1 < 100 ? ' — 이 상대에게는 <b>' + c1 + '%</b>' : '') + '</span></div></div>';""",
"""          '<div class="tl g"><i>대성공</i><span>피해 ' + od.mult + '배, ' + tac.gfx + (c1 && c1 < 100 ? ' — 이 상대에게는 <b>' + c1 + '%</b>' : '') + '</span></div>';
        if (have && u.morale >= tac.cost && tacticTargets(u, tac).some(function (x) { return x.u === d; })) {
          var X = tacticExpect(u, d, tac);
          h += '<div class="tl exv"><i>기대</i><span>피해 <b>' + fmt(Math.round(X.dealt)) + '</b>' + vs(X.dealt, N.dealt, true) + (X.others ? ' <small>(함께 맞는 ' + X.others + '부대 포함)</small>' : '') + ' · 받는 반격 <b>' + fmt(Math.round(X.recv)) + '</b>' + vs(X.recv, N.recv, false) + '</span></div>';
        }
        h += '</div>';""")
s = rep(s, """      h += '<p class="note"><b>성공</b>해도 반격은 받습니다(통상 공격 때의 ' + Math.round(TACTIC_K.okCounter / 0.55 * 100) + '%). <b>실패</b>하면 피해가 통상 공격의 ' + Math.round(TACTIC_K.failDmg * 100) + '%로 줄고 효과가 없으며, 반격을 통상 공격보다 크게(' + Math.round(TACTIC_K.failCounter / 0.55 * 100) + '%) 받습니다. 기력은 그대로 씁니다.</p>' +""",
"""      h += '<p class="note"><b>성공</b>해도 반격은 통상 공격만큼 받습니다(갈퀴·돌파, 멀리서 쏜 전법, 밀려나 떨어진 적은 반격하지 못합니다). <b>실패</b>하면 피해가 통상 공격의 ' + Math.round(TACTIC_K.failDmg * 100) + '%로 줄고 효과가 없으며, 반격을 통상 공격의 ' + (TACTIC_K.failCounter / 0.55).toFixed(2).replace(/0$/, '') + '배로 받습니다. 기력은 그대로 씁니다.</p>' +""")
s = rep(s, """'<p class="note"><b>무장</b> = (내 부대 최고 무력×0.6 + 주장 통솔×0.4) − 상대 부대 최고 통솔. <b>병력</b>""",
           """'<p class="note"><b>무장</b> = (내 부대 최고 무력×0.6 + 주장 통솔×0.4 − 상대 부대 최고 통솔) × ' + TACTIC_K.stat + ' (' + TACTIC_K.statLo + ' ~ +' + TACTIC_K.statHi + '). <b>병력</b>""")
s = rep(s, """<b>실패</b>하면 피해가 통상 공격의 절반으로 줄고 효과가 없으며 반격을 통상 공격보다 크게 받습니다. <b>성공</b>하면 전법의 피해와 효과가 들어가고 반격은 통상 공격보다 작게 받습니다. <b>대성공</b>이면 피해가 1.3배가 되고""",
           """<b>실패</b>하면 피해가 통상 공격의 ' + Math.round(TACTIC_K.failDmg * 100) + '%로 줄고 효과가 없으며 반격을 통상 공격의 ' + (TACTIC_K.failCounter / 0.55).toFixed(2).replace(/0$/, '') + '배로 받습니다. <b>성공</b>하면 전법의 피해와 효과가 들어가고 반격은 통상 공격만큼 받습니다(갈퀴·돌파, 멀리서 쏜 전법, 밀려나 떨어진 적은 반격하지 못합니다). <b>대성공</b>이면 피해가 ' + TACTIC_K.crit + '배가 되고""")
s = rep(s, """병력이 훨씬 많은 부대나 통솔이 높은 장수에게는 잘 통하지 않고, 병력 차만큼 피해도 줄어듭니다.""",
           """병력이 훨씬 많은 부대나 통솔이 높은 장수에게는 잘 통하지 않고, 병력 차만큼 피해도 줄어듭니다. <b>전법이 늘 이득은 아닙니다</b> — 무장이 상대보다 강할수록 이득이 크고, 약한 쪽이 쓰면 보통 공격보다 손해입니다.""")
s = rep(s, """<button class="act" type="button" data-a="tacinfo"><b>전법 풀이</b><small>효과·확률</small></button>""",
           """<button class="act" type="button" data-a="tacinfo"><b>전법 풀이</b><small>확률·효과·기대값</small></button>""")
s = rep(s, """적을 고른 뒤 <b>전법 풀이</b>를 누르면 그 상대에 대한 확률과 효과를 볼 수 있습니다.</p>'""",
           """적을 고른 뒤 <b>전법 풀이</b>를 누르면 그 상대에 대한 확률과 효과, 그리고 전법마다 <b>기대 피해 · 받는 반격</b>을 보통 공격과 나란히 볼 수 있습니다.</p>'""")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/style.css'; s = io.open(p, encoding='utf-8').read()
s = rep(s, ".tac .tl.g i { color: var(--seal); font-weight: 800; }",
""".tac .tl.g i { color: var(--seal); font-weight: 800; }
/* v0.9.1 전법의 기대값(보통 공격과 견줌) */
.tac .tl.exv { margin-top: 5px; padding-top: 5px; border-top: 1px dashed var(--line-2); font-variant-numeric: tabular-nums; }
.tac .tl.exv b { color: var(--ink); }
.tac .tl.exv small { font-size: 11.5px; color: var(--dim); }
.tac .tl.exv em { font-style: normal; font-size: 11.5px; font-weight: 800; margin-left: 2px; }
.tac .tl.exv em.good { color: #2f6b4f; } .tac .tl.exv em.bad { color: var(--seal); }
.tacs .sum.nrm { margin-top: 2px; }""")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
