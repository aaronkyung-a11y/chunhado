# v0.9.3 (1/…): 건설 번호를 부지마다 고정 · 보통 공격이 늘 치명타인 무장의 전법
#  요청(0.9.2 보고의 보기 b·c): "b,c,d 하고, …"
#  b. 부지의 번호는 성을 가운데 두고 북쪽에서 시계 방향으로 1, 2, 3 …(같은 방향이면 가까운 것 먼저). 부지마다 정해져 있어 무엇을 지어도 바뀌지 않는다.
#     (0.9.2 는 빈 부지에만 차례로 번호를 매겨서, 하나를 지으면 뒤의 번호가 모두 당겨졌다)
#  c. 보통 공격이 치명타가 되는 조건(비장·용장·신장이고 상대보다 무력이 높다)이면 전법도 성공하면 대성공.
#     - 전에는 신장(관우)만 그랬고, 비장(여포)·용장(안량·손책·방덕·염행)은 보통 공격만 1.3배였다. 그래서 이들의 전법은 피해가 보통 공격과 비슷하거나 낮았다
#       (같은 장면 비교 tests/tac93.js, 씨앗 1·2: 가장 나은 전법의 피해 ×1.22·×1.16 → ×1.41·×1.33, 전법이 이득인 장면 76%·73% → 89%·89%)
#     - 신장은 이름값대로 대성공의 피해 +10%(기신·궁신과 같은 ×1.375).
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)

# ---------------------------------------------------------------- core.js
p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, """function tacticCrit(u, d) {
  var c = TACTIC_K.crit, g = TACTIC_K.critGod;
  if (uHas(u, '신장') && uWar(u) > uWar(d)) return c;
  if (u.type === 'spear' && (uHas(u, '창장') || uHas(u, '투신'))) return c;
  if (u.type === 'halberd' && (uHas(u, '극장') || uHas(u, '투신'))) return c;
  if (u.type === 'bow') { if (uHas(u, '궁신')) return g; if (uHas(u, '궁장')) return c; }
  if (u.type === 'cav') { if (uHas(u, '기신')) return g; if (uHas(u, '기장')) return c; }
  return 0;
}""",
"""function tacticCrit(u, d) {                    // 성공한 전법이 반드시 대성공이 되는가 → 그때의 배수(아니면 0). 여럿이 겹치면 큰 쪽
  var c = TACTIC_K.crit, g = TACTIC_K.critGod, m = 0;
  if (critNormal(u, d)) m = uHas(u, '신장') ? g : c;            // v0.9.3: 보통 공격이 치명타가 되는 조건(비장·용장·신장 + 상대보다 무력이 높다)이면 전법도. 신장은 피해 +10%
  if (u.type === 'spear' && (uHas(u, '창장') || uHas(u, '투신'))) m = Math.max(m, c);
  if (u.type === 'halberd' && (uHas(u, '극장') || uHas(u, '투신'))) m = Math.max(m, c);
  if (u.type === 'bow') { if (uHas(u, '궁신')) m = Math.max(m, g); else if (uHas(u, '궁장')) m = Math.max(m, c); }
  if (u.type === 'cav') { if (uHas(u, '기신')) m = Math.max(m, g); else if (uHas(u, '기장')) m = Math.max(m, c); }
  return m;
}""")
s = rep(s, "        + 적이 선 곳: 숲·구릉 −5, 강 +5   + 적이 혼란 중 +10   + 맞는 특기(창장·기장·신장…) +5",
           "        + 적이 선 곳: 숲·구릉 −5, 강 +5   + 적이 혼란 중 +10   + 맞는 특기(창장·기장…, 무력이 낮은 적을 치는 비장·용장·신장) +5")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- data.js
p = 'src/data.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "'비장': 'ZOC를 무시한다. 무력이 낮은 적에게 통상 공격이 크리티컬.',", "'비장': 'ZOC를 무시한다. 무력이 낮은 적에게 통상 공격은 크리티컬, 전법은 성공하면 반드시 대성공(성공률 +5).',")
s = rep(s, "'신장': '무력이 낮은 적에게 통상 공격은 크리티컬, 전법은 성공하면 반드시 대성공(성공률 +5).',", "'신장': '무력이 낮은 적에게 통상 공격은 크리티컬, 전법은 성공하면 반드시 대성공이고 피해 +10%(성공률 +5).',")
s = rep(s, "'용장': '무력이 낮은 적에게 통상 공격이 크리티컬.',", "'용장': '무력이 낮은 적에게 통상 공격은 크리티컬, 전법은 성공하면 반드시 대성공(성공률 +5).',")
s = rep(s, "var GAME_VERSION = 'v0.9.2';", "var GAME_VERSION = 'v0.9.3';")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- ui_panels.js
p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "function lotNo(b, pi) { return emptyLots(b).indexOf(pi) + 1; }",
"""/* 부지의 번호(v0.9.3): 성을 가운데 두고 북쪽에서 시계 방향으로 1, 2, 3 …(같은 방향이면 가까운 것 먼저). 부지마다 정해져 있어 무엇을 지어도 바뀌지 않는다 */
var LOTNO = {};
function lotNos(b) {
  var m = LOTNO[b.id], i;
  if (m && m.length === b.plots.length) return m;
  var c0 = hexCenter(b.c, b.r), idx = [];
  for (i = 0; i < b.plots.length; i++) { var q = hexCenter(b.plots[i].c, b.plots[i].r), dx = q[0] - c0[0], dz = q[1] - c0[1]; idx.push({ i: i, a: Math.round(((Math.atan2(dx, -dz) + 2 * Math.PI) % (2 * Math.PI)) * 1e6), d: dx * dx + dz * dz }); }
  idx.sort(function (x, y) { return x.a - y.a || x.d - y.d; });
  m = []; for (i = 0; i < idx.length; i++) m[idx[i].i] = i + 1;
  return (LOTNO[b.id] = m);
}
function lotNo(b, pi) { return lotNos(b)[pi]; }
function emptyLotsByNo(b) { return emptyLots(b).sort(function (x, y) { return lotNo(b, x) - lotNo(b, y); }); }      // 빈 부지를 번호 차례로""")
s = rep(s, "  var why = buildWhy(b), pi = d ? d.pi : -1, sig = b.id + '/' + pi + '/' + why + '/', lots = [], facs = [], n = 0;",
           "  var why = buildWhy(b), pi = d ? d.pi : -1, sig = b.id + '/' + pi + '/' + why + '/', lots = [], facs = [];")
s = rep(s, "    else { var ok = !why && !UAT[K(p.c, p.r)]; lots.push({ i: i, c: p.c, r: p.r, n: ++n, ok: ok }); sig += i + (ok ? '' : 'x') + ','; }",
           "    else { var ok = !why && !UAT[K(p.c, p.r)]; lots.push({ i: i, c: p.c, r: p.r, n: lotNo(b, i), ok: ok }); sig += i + (ok ? '' : 'x') + ','; }")
s = rep(s, "  if (!lots.length) return null;                               // 빈 부지가 없으면 비출 것이 없다",
           "  if (!lots.length) return null;                               // 빈 부지가 없으면 비출 것이 없다\n  lots.sort(function (x, y) { return x.n - y.n; });")
# 건설 탭: 번호 단추는 번호 차례로, 그 아래 지은 시설
s = rep(s, """        for (var pass = 0; pass < 2; pass++) for (i = 0; i < b.plots.length; i++) {
          var fc = b.plots[i].fac;
          if (pass === 1 && i === 0) h += (nE ? '</div>' : '') + (nF ? '<div class="sec">지은 시설 <em class="cnt">' + nF + '</em></div>' : '') + '<div class="rows">';
          if ((pass === 0) !== !fc) continue;
          if (!fc) h += '<button class="lot' + (why || UAT[K(b.plots[i].c, b.plots[i].r)] ? ' no' : '') + '" type="button" data-a="plot" data-v="' + i + '" aria-label="빈 부지 ' + lotNo(b, i) + '">' + lotNo(b, i) + '</button>';
          else h +=""",
"""        var em = emptyLotsByNo(b);
        for (i = 0; i < em.length; i++) h += '<button class="lot' + (why || UAT[K(b.plots[em[i]].c, b.plots[em[i]].r)] ? ' no' : '') + '" type="button" data-a="plot" data-v="' + em[i] + '" aria-label="빈 부지 ' + lotNo(b, em[i]) + '">' + lotNo(b, em[i]) + '</button>';
        h += (nE ? '</div>' : '') + (nF ? '<div class="sec">지은 시설 <em class="cnt">' + nF + '</em></div>' : '') + '<div class="rows">';
        for (i = 0; i < b.plots.length; i++) {
          var fc = b.plots[i].fac;
          if (!fc) continue;
          h +=""")
s = rep(s, "        '<li>창장·극장·궁장·기장 같은 특기가 맞으면 성공한 전법은 모두 대성공입니다.</li></ul></details>';",
           "        '<li>창장·극장·궁장·기장 같은 특기가 맞으면 성공한 전법은 모두 대성공입니다. 비장·용장·신장은 무력이 낮은 적을 칠 때 그렇습니다.</li></ul></details>';")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
