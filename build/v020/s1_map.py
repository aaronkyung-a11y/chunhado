# v0.20 (1) 홍농(弘農) — 낙양과 장안 사이, 함곡관과 동관 사이의 성.   ("낙양하고 장안 사이에 홍농이라는 도시가 있지 않나?")
#   지도 자료는 tools/add_base20.py + tools/add_plots.py 가 고친다(거점 목록의 맨 뒤 = 49번, 길 20걸음을 10 + 10 으로 나눔, 부지 10곳).
#   여기서는: 194년의 주인(이각 — 장제 · 장수 · 호거아가 지킨다), 옛 저장을 열 때 덧붙이기, 판 번호.
#   CH_ROOT=<폴더> 로 다른 나무에 입힐 수 있다(시험용).
import io, os
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)

s = rd('src/data.js')
s = rep(s, "var GAME_VERSION = 'v0.19.1';", "var GAME_VERSION = 'v0.20';")
s = rep(s, "'이각': '장안을 차지한 서량군. 병력은 많고 민심은 없다.'", "'이각': '장안과 홍농을 차지한 서량군. 병력은 많고 민심은 없다.'")
s = rep(s, "var MAX_DUR = {", """var BASES_OLD = 49;                                         // v0.20: 0.19.1 까지의 거점 수(옛 저장은 이만큼만 가지고 있다)
var BASE_GROW = { '홍농': '장안' };                          // 옛 저장에 덧붙일 때의 주인: 이 성을 쥔 세력(없으면 빈 성)
var MAX_DUR = {""")
wr('src/data.js', s)

s = rd('src/roster.js')
s = rep(s, '{"n":"이각","color":"#7b241c","cities":["장안"]}', '{"n":"이각","color":"#7b241c","cities":["장안","홍농"]}')
for n in ('장제', '장수', '호거아'):
    a = '"f":15,"c":"장안"'
    i = s.index('{"n":"%s","ldr"' % n); j = s.index('}', i); seg = s[i:j]
    assert seg.count(a) == 1, (n, seg[:80])
    s = s[:i] + seg.replace(a, '"f":15,"c":"홍농"') + s[j:]
wr('src/roster.js', s)

s = rd('src/core.js')
s = rep(s, """function deserialize(s) {
  var g = JSON.parse(s);
  if (!g || g.ver !== 2) return false;
""", """/* v0.20: 거점이 늘었다(홍농). 옛 저장에는 없다 — 뒤에 덧붙인다(앞선 거점의 번호와 자리는 그대로다).
   주인은 BASE_GROW 가 가리키는 성(장안)을 쥔 세력 — 그 세력이 없으면 빈 성이다. 새 성이 서는 칸에 부대가 있으면 옆 칸으로 비킨다. */
function baseGrow(g) {
  var n0 = g.bases.length, i, j, n = 0;
  if (n0 >= MAPDATA.bases.length || n0 < BASES_OLD) return 0;
  for (i = 0; i < n0; i++) if (!g.bases[i] || g.bases[i].n !== MAPDATA.bases[i].n) return 0;       // 다른 지도로 만든 저장이면 건드리지 않는다
  for (i = n0; i < MAPDATA.bases.length; i++) {
    var mb = MAPDATA.bases[i], ni = BASE_GROW[mb.n] ? baseByName(BASE_GROW[mb.n]) : -1, nb = ni >= 0 && ni < n0 ? g.bases[ni] : null;
    var own = (nb && nb.owner >= 0 && g.factions[nb.owner] && g.factions[nb.owner].alive !== false) ? nb.owner : -1, has = own >= 0 && mb.k === 'city';
    var b = { id: i, n: mb.n, kind: mb.k, c: mb.c, r: mb.r, sz: mb.sz, owner: own, gold: has ? 600 : 0, food: has ? 6000 : 0, troops: has ? 4000 : 0, morale: 60, order: 60,
      dur: MAX_DUR[mb.sz], maxDur: MAX_DUR[mb.sz], w: { spear: has ? 1600 : 0, halberd: has ? 1000 : 0, bow: has ? 1000 : 0, horse: 0, ram: 0 }, plots: [], captives: [], ai: {}, grown: 1 };
    var pl = MAPDATA.plots[mb.n] || [];
    for (j = 0; j < pl.length; j++) b.plots.push({ c: pl[j][0], r: pl[j][1], fac: null });
    if (has) ['market', 'farm', 'barracks'].forEach(function (t, k) { if (b.plots[k]) b.plots[k].fac = { t: t, lv: 1, done: true, prog: 0, need: 0, rate: 0, hp: FAC_HP }; });
    g.bases.push(b); n++;
    var us = g.units || [], occ = {}, q, moved;
    for (j = 0; j < us.length; j++) occ[K(us[j].c, us[j].r)] = 1;
    for (j = 0; j < us.length; j++) {
      if (us[j].c !== mb.c || us[j].r !== mb.r) continue;
      var ring = [[mb.c, mb.r]], seen = {}, step; moved = false; seen[K(mb.c, mb.r)] = 1;
      for (step = 0; step < 6 && !moved; step++) {
        var next = [];
        for (q = 0; q < ring.length && !moved; q++) {
          var ns = nbrs(ring[q][0], ring[q][1]);
          for (var z = 0; z < ns.length && !moved; z++) {
            var hk = K(ns[z][0], ns[z][1]), tc = TCH[hk];
            if (seen[hk]) continue; seen[hk] = 1;
            if (tc === 120 || tc === 115 || tc === 109) continue;
            if (!occ[hk] && BAT[hk] === undefined) { delete occ[K(us[j].c, us[j].r)]; us[j].c = ns[z][0]; us[j].r = ns[z][1]; occ[hk] = 1; moved = true; }
            else next.push(ns[z]);
          }
        }
        ring = next;
      }
    }
  }
  return n;
}
function deserialize(s) {
  var g = JSON.parse(s);
  if (!g || g.ver !== 2) return false;
  var grownB = baseGrow(g);                                              // v0.20: 거점이 늘었다(홍농)
""")
wr('src/core.js', s)

s = rd('src/ui_panels.js')
s = rep(s, "  if (g.bases.length !== MAPDATA.bases.length || nf !== SCENARIO.factions.length || no < 1) return false;",
        "  if (g.bases.length > MAPDATA.bases.length || g.bases.length < BASES_OLD || nf !== SCENARIO.factions.length || no < 1) return false;      // v0.20: 옛 저장은 거점이 적다(홍농이 없다) — 열 때 덧붙인다")
wr('src/ui_panels.js', s)
print('s1 ok')

s = rd('src/core.js')
s = rep(s, """  var tfix = terrainFix();                                               // v0.15: 산이 넓어졌다""", """  if (grownB) for (var gbi = G.bases.length - grownB; gbi < G.bases.length; gbi++) {
    var gnb = G.bases[gbi]; delete gnb.grown;
    logMsg('지도에 새 성이 더해졌습니다(v0.20) — ' + gnb.n + (gnb.owner >= 0 ? ' · ' + facName(gnb.owner) + '군의 성' : ' · 빈 성'), gnb.c, gnb.r, G.player, 1);
  }
  var tfix = terrainFix();                                               // v0.15: 산이 넓어졌다""")
wr('src/core.js', s)
print('s1b ok')
