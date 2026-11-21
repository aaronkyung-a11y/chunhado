# v0.11 (4/…): 군사의 평소 조언 — 헌책  (data.js · core.js · ui_panels.js · style.css)
#  요청 ① "평소 군사 조언이 빈땅있으면 지어라하고 병력 보강하라는 말만 너무 많이 하는 듯? 이것도 지력 차이가 있나?"
#  요청 ② "군사가 탐색 등에 대한 조언은 왜 안 하지?"
#  전에는: 거점마다 정해진 차례(순찰 → 등용 → 빈 부지 → 징병 → 훈련 → 탐색)의 첫 줄을 그대로 읽었다. 군사의 지력은 관계가 없었다.
#  이제는:
#  - 할 만한 일을 후보로 뽑는다(counselRaw): 순찰 · 등용(응할 사람) · 이웃 세력의 무장 · 탐색 · 포상 · 훈련 · 징병 · 건설(무엇을 어디에) · 무기 생산 · 병량 사기/팔기 ·
#    주인 없는 이웃 거점 · 허술한 이웃 거점. 후보마다 무게 w(급한 정도)와 어려움 d(알아채기 어려운 정도).
#    징병은 '길로 이어진 이웃 세력의 병력이 우리보다 많을 때'만 권한다(보호가 30일 넘게 남았으면 낮은 무게). 건설은 무엇을 어디에 지으면 얼마가 느는지까지.
#  - 군사의 지력으로 거른다(counsel): d 가 지력보다 높은 일은 (d − 지력) × 2.5% 의 확률로 놓치고(달마다), 순위에 잡음이 섞이고(폭 28 × (100 − 지력) ÷ 50, 턴마다),
#    말의 자세함이 달라진다(80 이상: 숫자와 사람까지 · 65 이상: 무엇을 할지 · 그 아래: 두루뭉술하게).
#  - 같은 말을 되풀이하지 않는다: 한 번 한 말은 두 턴 동안 맨 앞에 세우지 않고, 같은 종류의 말(징병 · 건설 …)도 그동안 뒤로 돌린다(무게 70 이상의 급한 일은 예외). STATUS 창의 [다른 조언]으로 다음 것을 듣는다.
#  - 군사의 한마디는 급한 알림(적 접근 · 맞닿음 · 혼란 · 불 · 군량 · 떠날 무장) → 헌책 → 그 밖(명령 대기 등)의 차례. '지금 할 일'의 거점 줄도 헌책에서 나온다(할 만한 일이 없는 거점은 줄이 없다).
#  - 탐색: 결과를 미리 정해 둔다(등용과 같은 방식 — 거점 · 턴 · 그 턴의 몇 번째인가). 군사가 탐색할 무장을 고르는 표에서 "오늘 만날 것 / 만나지 못할 것"을 말하고,
#    숨은 인재가 있는 도시를 헌책으로 귀띔한다(있는지 없는지를 아는 것도 지력만큼만 맞는다 — 달마다 정해진다).
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)

# ---------------------------------------------------------------- data.js
p = 'src/data.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "var ADVISE = {",
"""/* 군사의 헌책(v0.11): seeK = 어려운 일(d > 지력)을 놓칠 확률 = (d − 지력) × seeK % · noise = 순위에 섞이는 잡음의 폭(× (100 − 지력) ÷ 50)
   detail · some = 말이 자세해지는 지력의 문턱 · keep = 한 번 한 말을 맨 앞에 다시 세우지 않는 턴 수 · urgent = 그래도 되풀이하는 무게 */
var COUNSEL = { seeK: 2.5, noise: 28, detail: 80, some: 65, keep: 2, urgent: 70, poachMin: 20 };      // poachMin: 이웃 세력의 무장은 성공률이 이만큼은 되어야 먼저 권한다(낮은 확률의 '응할 것'은 거의 헛짚은 것이다)
var ADVISE = {""")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- core.js
p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()

# 1) 탐색: 미리 정해 둔 결과
s = rep(s, """  var o = os[0]; markActed(os, 15);
  var hid = hiddenOfficers(b);
  if (hid.length) {
    var p = 25 + o.pol * 0.35 + o.cha * 0.15;
    if (o.sk === '안력') p *= 2;
    if (chance(p)) { var h = pick(hid); h.st = 'free'; return { ok: true, found: h.id }; }
  }
  if (chance(35)) { var g = ri(5, 20) * 10; b.gold += g; return { ok: true, gold: g }; }
""",
"""  var o = os[0]; markActed(os, 15);
  var key = searchKey(b), hid = hiddenOfficers(b), p = searchChance(b, o);       // v0.11: 미리 정해 둔 결과(군사가 미리 말해 줄 수 있다)
  b.sN = (b.sT === G.turn ? (b.sN || 0) : 0) + 1; b.sT = G.turn;                 // 같은 턴에 다시 찾으면 주사위가 새로 정해진다
  if (hid.length && omenRoll(key) < p) { var h = hid[Math.min(hid.length - 1, Math.floor(omenRoll('w|' + key) / 100 * hid.length))]; h.st = 'free'; return { ok: true, found: h.id }; }
  if (omenRoll('g|' + key) < 35) { var g = (5 + Math.floor(omenRoll('q|' + key) / 100 * 16)) * 10; b.gold += g; return { ok: true, gold: g }; }
""")
s = rep(s, "function cmdSearch(b, id) {\n",
"""/* 탐색(v0.11): 숨은 인재를 찾아낼 확률(%)과 그 주사위. 주사위는 거점 · 턴 · 그 턴의 몇 번째 탐색인가로 정해진다(누가 가도 같은 주사위 — 성공률만 다르다) */
function searchSkill(o) { return (25 + o.pol * 0.35 + o.cha * 0.15) * (o.sk === '안력' ? 2 : 1); }
function searchChance(b, o) { return hiddenOfficers(b).length ? Math.min(100, searchSkill(o)) : 0; }
function searchKey(b) { return 's' + b.id + ':' + (b.sT === G.turn ? (b.sN || 0) : 0); }
function searchRoll(b) { return omenRoll(searchKey(b)); }
function searchRollA(b) { return omenRoll('a|' + searchKey(b)); }                // 군사의 조언이 맞는가
function cmdSearch(b, id) {
""")

# 2) 헌책
s = rep(s, "function serialize() { return JSON.stringify(G); }\n",
"""/* ---------- 군사의 헌책(v0.11) ----------
   평소의 조언: 직접 다스리는 거점마다 '할 만한 일'을 후보로 뽑고(counselRaw), 군사의 지력으로 거른다(counsel).
   후보 { kind, b, w(급한 정도), d(알아채기 어려운 정도), x(그 일의 사실들) }. 말은 화면 쪽(counselText)에서 만든다. */
function bestBy(os, f) { var b = null, bv = -1e18; for (var i = 0; i < os.length; i++) { var v = f(os[i]); if (v > bv) { bv = v; b = os[i]; } } return b; }
function nbrThreat(b) {                                    // 길로 이어진 이웃 거점 가운데 다른 세력의 가장 큰 병력 { nb, troops } (없으면 null)
  var best = null;
  ADJ[b.id].forEach(function (e) { var nb = G.bases[e.to]; if (nb.owner >= 0 && nb.owner !== b.owner && (!best || nb.troops > best.troops)) best = { nb: nb.id, troops: nb.troops }; });
  return best;
}
function facGainAt(b, pi, t) { var p = b.plots[pi], g0 = goldIncome(b), f0 = foodIncome(b); p.fac = { t: t, lv: 1, done: true }; var g1 = goldIncome(b), f1 = foodIncome(b); p.fac = null; return { gold: g1 - g0, food: f1 - f0 }; }
function cityFoodTurns(b) { var need = Math.ceil(b.troops / 60); return need > 0 ? Math.floor(b.food / need) : 999; }
/* 무엇을 어디에 지을까: 급한 것(병영이 없다 · 병량 수입이 소비에 못 미친다)이 먼저, 아니면 수입이 가장 크게 느는 자리 → { t, pi, gain, why } 또는 null */
function buildPick(b, thr) {
  var em = [], i;
  for (i = 0; i < b.plots.length; i++) if (!b.plots[i].fac && !UAT[K(b.plots[i].c, b.plots[i].r)]) em.push(i);
  if (!em.length) return null;
  function bestPlot(t) { var bi = em[0], bv = -1e9; em.forEach(function (pi) { var g = facGainAt(b, pi, t), v = g.gold * 3 + g.food / 5; if (v > bv) { bv = v; bi = pi; } }); return { t: t, pi: bi, gain: facGainAt(b, bi, t), v: bv }; }
  function has(t) { for (var j = 0; j < b.plots.length; j++) if (b.plots[j].fac && b.plots[j].fac.t === t) return true; return false; }      // 짓는 중인 것도 센다
  var upkeep = Math.ceil(b.troops / 60) * 9, fi = foodIncome(b), r;
  if (!has('barracks') && thr && b.gold >= FAC.barracks.cost) { r = bestPlot('barracks'); r.why = 'nobarracks'; return r; }
  if (fi < upkeep && b.gold >= FAC.farm.cost) { r = bestPlot('farm'); r.why = 'food'; r.fi = fi; r.upkeep = upkeep; return r; }
  var cands = [];
  ['market', 'farm', 'mint', 'granary'].forEach(function (t) { if (b.gold >= FAC[t].cost) cands.push(bestPlot(t)); });
  cands.sort(function (x, y) { return y.v - x.v; });
  if (cands.length && cands[0].v > 0) { cands[0].why = 'income'; return cands[0]; }
  return null;
}
function counselRaw(f) {
  var F = G.factions[f], out = [], pl = (f === G.player && !G.aiOnly) ? peaceLeft() : 0;
  directBases(f).forEach(function (b) {
    var idle = idleOfficers(b); if (!idle.length) return;
    var city = b.kind === 'city', thr = nbrThreat(b);
    function add(kind, w, d, x) { out.push({ kind: kind, b: b.id, w: w, d: d, x: x || {} }); }
    function best(t) { var o = bestBy(idle, function (q) { return recruitChance(b, q, t) * 1000 - q.id; }); return { t: t.id, o: o.id, p: recruitChance(b, o, t) }; }
    // 훈련
    if (b.morale < 70 && b.troops >= 2000 && F.ap >= AP.train) add('train', 28 + (70 - b.morale) * 0.8 + (thr && !pl && thr.troops > b.troops * 0.7 ? 15 : 0), 30, { morale: b.morale });
    // 이웃의 주인 없는 거점 · 허술한 거점
    if (b.troops >= 3000 && F.ap >= AP.deploy) {
      var vac = null, weak = null;
      ADJ[b.id].forEach(function (e) { var nb = G.bases[e.to]; if (nb.owner < 0) { if (!vac) vac = nb; } else if (nb.owner !== f && nb.troops * 1.5 + 2000 < b.troops && (!weak || nb.troops < weak.troops)) weak = nb; });
      if (vac) add('vacant', 60, 55, { nb: vac.id });
      if (weak) { var brk = f === G.player && !G.aiOnly && peaceWouldBreak(weak.owner); add('strike', 42 + Math.min(15, (b.troops - weak.troops * 1.5 - 2000) / 1000) - (brk ? 14 : 0), 75, { nb: weak.id, def: weak.troops, troops: b.troops, brk: brk }); }
    }
    if (!city) return;
    // 순찰
    if (b.gold >= COST.patrol && F.ap >= AP.patrol) {
      if (b.order < 60) add('patrol', 62 + (60 - b.order) * 0.6, 10, { order: b.order, by: bestBy(idle, function (o) { return Math.max(o.war, o.ldr) + (o.sk === '위압' ? 40 : 0); }).id });
      else if (b.order < 80 && b.gold >= 300) add('patrol2', 22, 45, { order: b.order });
    }
    // 등용: 이 거점의 재야 · 포로, 이웃 세력의 무장(누가 응할지는 군사가 가린다)
    if (F.ap >= AP.recruit) {
      var ts = freeOfficers(b).concat(baseCaptives(b).filter(function (o) { return o.capF === f; })).filter(function (t) { return !askWait(t); });
      if (ts.length) add('recruit', 60, 30, { ts: ts.map(best) });
      var far = poachTargets(b).filter(function (t) { return !askWait(t); }).map(best).filter(function (x) { return x.p >= COUNSEL.poachMin; });
      if (far.length) add('poach', 64, 50, { ts: far });
    }
    // 탐색: 숨은 인재가 있는지(x.hid)는 군사가 헤아린다
    if (F.ap >= AP.search) { var so = bestBy(idle, searchSkill); add('search', 50, 60, { hid: hiddenOfficers(b).length > 0, o: so.id, p: searchChance(b, so) }); }
    // 포상
    if (b.gold >= COST.reward && F.ap >= AP.reward) { var lo = null; baseOfficers(b).forEach(function (o) { if (!isLord(o) && !bondOf(o) && o.loy < 80 && (!lo || o.loy < lo.loy)) lo = o; }); if (lo) add('reward', 40 + (80 - lo.loy) * 1.5, 35, { t: lo.id, loy: lo.loy }); }
    // 징병: 이웃 세력의 병력이 우리보다 많을 때만(병량이 한 분기를 못 버티면 권하지 않는다)
    if (hasFac(b, 'barracks') && b.gold >= COST.draft && b.order >= 30 && F.ap >= AP.draft && thr && b.troops < thr.troops * 0.8 && cityFoodTurns(b) >= 9) {
      var soon = pl <= 9;
      add('draft', soon ? 58 + Math.min(20, (thr.troops - b.troops) / 1000 * 2) : 30, 40, { nb: thr.nb, thr: thr.troops, troops: b.troops, soon: soon, pl: pl, order: b.order });
    }
    // 건설: 무엇을 어디에
    var bp = F.ap >= AP.develop ? buildPick(b, thr) : null;
    if (bp) add('build', (bp.why === 'income' ? 34 : 48) + (b.gold >= FAC[bp.t].cost * 3 ? 10 : 0), 50, { t: bp.t, pi: bp.pi, gain: bp.gain, why: bp.why, fi: bp.fi, upkeep: bp.upkeep, empty: b.plots.filter(function (q) { return !q.fac; }).length });
    // 무기
    if (hasFac(b, 'smithy') && b.gold >= COST.produce && F.ap >= AP.produce) { var arms = b.w.spear + b.w.halberd + b.w.bow; if (b.troops >= 3000 && arms < b.troops * 0.6) add('produce', 30, 45, { arms: arms, troops: b.troops }); }
    // 거래
    if (hasFac(b, 'market') && F.ap >= AP.trade) {
      var ft = cityFoodTurns(b);
      if (ft < 9 && b.gold >= 300) add('buyfood', 66, 30, { ft: ft });
      else if (b.gold < 150 && ft > 40) add('sellfood', 32, 55, { gold: b.gold });
    }
  });
  var seenNb = {};                                                       // 같은 이웃 거점(빈 곳 · 허술한 곳)은 병력이 가장 많은 우리 거점에서 한 번만
  out.forEach(function (c) { if (c.kind !== 'vacant' && c.kind !== 'strike') return; var k = c.kind + c.x.nb, o = seenNb[k]; if (!o || G.bases[c.b].troops > G.bases[o.b].troops) seenNb[k] = c; });
  return out.filter(function (c) { return (c.kind !== 'vacant' && c.kind !== 'strike') || seenNb[c.kind + c.x.nb] === c; });
}
/* 군사의 눈으로 거른 헌책 { adv, lvl(말의 자세함 0~2), list(급한 것부터) } — 군사가 없으면 뻔한 일(d ≤ 40)만 */
function counsel(f) {
  var A = facAdv(f), raw = counselRaw(f), out = [];
  var acc0 = A ? adviceAcc(A, 0) : 0, amp = A ? COUNSEL.noise * (100 - A.int) / 50 : 0, lvl = !A ? 1 : (A.int >= COUNSEL.detail ? 2 : (A.int >= COUNSEL.some ? 1 : 0));
  raw.forEach(function (c) {
    var key = c.kind + ':' + c.b, b = G.bases[c.b];
    if (!A) { if (c.d > 40) return; if (c.kind === 'recruit') { c.x.pick = c.x.ts[0]; c.x.says = null; } }
    else {
      if (c.kind === 'recruit' || c.kind === 'poach') {                  // 응할 사람을 군사가 가려낸다(맞힐 확률 = 적중률)
        var yes = [], no = [];
        c.x.ts.forEach(function (x) { var t = off(x.t), a = advise(f, recruitRoll(t), recruitRollA(t), x.p, t.int); x.says = !!(a && a.says); (x.says ? yes : no).push(x); });
        yes.sort(function (p1, p2) { return statSum(off(p2.t)) - statSum(off(p1.t)) || p1.t - p2.t; });
        if (c.kind === 'poach') { if (!yes.length) return; c.x.pick = yes[0]; c.x.says = true; }
        else if (yes.length) { c.x.pick = yes[0]; c.x.says = true; c.w = 72 + Math.min(15, statSum(off(yes[0].t)) / 30); }
        else { c.x.pick = no[0]; c.x.says = false; c.w = 18; }
        if (lvl === 0 && c.kind === 'recruit') c.w = 55;                 // 지력이 낮으면 누가 응할지 가리지 못한다
      }
      if (c.kind === 'search') {                                         // 숨은 인재가 있는지: 적중률만큼 바르게 안다(달마다 정해진다)
        var knows = omenRoll('adv|hid' + c.b, true) < acc0, belief = knows ? c.x.hid : !c.x.hid;
        if (!belief) return;
        var sa = advise(f, searchRoll(b), searchRollA(b), c.x.p, 0);
        c.x.says = !!(sa && sa.says); c.w = lvl === 0 ? 40 : (c.x.says ? 68 : 26);
      }
      if (c.d > A.int && omenRoll('adv|see|' + key, true) < (c.d - A.int) * COUNSEL.seeK) return;      // 놓쳤다
    }
    c.key = key; c.lvl = lvl;
    c.ws = c.w + (A ? (omenRoll('adv|w|' + key) / 100 - 0.5) * amp : 0);
    out.push(c);
  });
  out.sort(function (a, b2) { return b2.ws - a.ws || a.b - b2.b || (a.kind < b2.kind ? -1 : 1); });
  return { adv: A, lvl: lvl, list: out };
}

function serialize() { return JSON.stringify(G); }
""")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- ui_panels.js
p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()

# 1) 거점의 조언: 헌책에서
s = rep(s, """function baseAdvice(b) {
  var n = idleOfficers(b).length, tips = [];
  if (!n) return null;
  if (b.kind === 'city') {
    var empty = b.plots.filter(function (p) { return !p.fac; }).length, men = freeOfficers(b).length + b.captives.length;
    if (b.order < 60) tips.push(['치안 ' + b.order + ' → 순찰', 'home', '치안이 어지럽습니다. 순찰을 돌리십시오.']);
    if (men) tips.push(['등용할 인재 ' + men + '명', 'men', '부를 만한 인재가 ' + men + '명 있습니다. 등용하시지요.']);
    if (empty && b.gold >= minFacCost()) tips.push(['빈 부지 ' + empty + '곳 → 시설 건설', 'fac', '빈 부지가 ' + empty + '곳 있습니다. 시설을 지으시지요.']);
    if (hasFac(b, 'barracks') && b.gold >= COST.draft && b.order >= 60) tips.push(['징병', 'home', '병사를 더 모으시지요.']);
    if (b.morale < 60 && b.troops >= 1000) tips.push(['기력 ' + b.morale + ' → 훈련', 'home', '군의 기력이 낮습니다. 훈련하십시오.']);
    if (!tips.length) tips.push(['탐색으로 인재·재물 찾기', 'men', '탐색으로 인재를 찾아보시지요.']);
  } else {
    if (b.morale < 60 && b.troops >= 1000) tips.push(['기력 ' + b.morale + ' → 훈련', 'mil', '군의 기력이 낮습니다. 훈련하십시오.']);
    if (b.troops >= 1000) tips.push(['출진 가능', 'mil', '군을 낼 수 있습니다.']);
    if (!tips.length) return null;
  }
  return { n: n, tips: tips.slice(0, 2).map(function (t) { return t[0]; }), tab: tips[0][1], say: tips[0][2] };
}
""",
"""/* ---------- 군사의 헌책(v0.11): 후보(core.js 의 counsel)를 말로 옮긴다 ----------
   lvl 2 = 숫자와 사람까지 · 1 = 무엇을 할지 · 0 = 두루뭉술하게.  → { say(군사의 말), tip(할 일 줄의 짧은 글), go, key, w } */
function counselText(c) {
  var b = G.bases[c.b], x = c.x, L = c.lvl, say = '', tip = '', go = ['base', b.id, 'home'], nb = x.nb !== undefined ? G.bases[x.nb] : null, t, o, P;
  function nbName() { return nb.n + (nb.owner >= 0 ? '(' + facName(nb.owner) + '군)' : ''); }
  function send(q, from) { return isLord(q) ? '주공께서 직접 권하십시오' : (from ? from + '의 ' : '') + josa(q.n, '을를') + ' 보내십시오'; }      // 군주가 가장 잘 권할 때
  if (c.kind === 'patrol') {
    o = off(x.by); tip = '치안 ' + x.order + ' → 순찰';
    say = L === 2 ? b.n + '의 치안이 ' + x.order + '까지 떨어져 수입이 ' + incPct(x.order) + '%뿐입니다. ' + (isLord(o) ? '주공께서 직접 순찰을 도십시오.' : o.n + '에게 순찰을 맡기십시오.') : (L === 1 ? b.n + '의 치안이 낮아 수입이 줄고 있습니다. 순찰을 돌리십시오.' : b.n + ' — 치안이 어지럽습니다. 순찰을 돌리십시오.');
  } else if (c.kind === 'patrol2') {
    tip = '치안 ' + x.order + ' → 순찰';
    say = L === 2 ? b.n + '의 치안은 ' + x.order + '(수입 ' + incPct(x.order) + '%)입니다. 여유가 있을 때 순찰로 더 올려 두시지요.' : b.n + ' — 여유가 있으면 순찰로 치안을 다져 두시지요.';
  } else if (c.kind === 'recruit') {
    P = x.pick; t = off(P.t); o = off(P.o); go = ['recruit', b.id];
    var kindN = t.st === 'captive' ? '포로' : '재야', tie = tieOf(o, t, b.owner);
    if (x.says === null || L === 0) { tip = '등용할 인재 ' + x.ts.length + '명'; say = b.n + ' — 부를 만한 인재가 ' + x.ts.length + '명 있습니다. 등용하시지요.'; }
    else if (x.says) { tip = t.n + ' 등용 <i class="adv y">○</i>'; say = L === 2 ? b.n + '의 ' + kindN + ' ' + t.n + '에게 ' + send(o) + (tie ? '(' + tie.short + ')' : '') + '. 응할 것입니다.' : b.n + '의 ' + josa(t.n, '은는') + ' 지금 부르면 응할 것입니다.'; }
    else { tip = kindN + ' ' + x.ts.length + '명 <i class="adv n">×</i>'; say = b.n + '의 ' + josa(t.n, '은는') + ' 오늘은 응하지 않겠습니다. 다음 턴에 다시 권하시지요.'; }
  } else if (c.kind === 'poach') {
    P = x.pick; t = off(P.t); o = off(P.o); go = ['recruit', b.id]; tip = L === 0 ? '이웃 무장 등용' : t.n + ' 등용 <i class="adv y">○</i>';
    say = L === 0 ? b.n + ' — 이웃 세력의 무장을 불러 보시지요.' : (L === 2 ? G.bases[t.loc].n + '의 ' + t.n + '(' + facName(t.f) + '군)에게 ' + send(o, b.n) + '. 응할 것입니다.' : b.n + '에서 ' + josa(t.n, '을를') + ' 부르면 응할 것입니다.');
  } else if (c.kind === 'search') {
    o = off(x.o); go = ['base', b.id, 'men'];
    if (L === 0) { tip = '탐색'; say = b.n + ' — 탐색으로 인재를 찾아보시지요.'; }
    else if (x.says) { tip = '탐색 <i class="adv y">○</i>'; say = L === 2 ? b.n + '에 숨은 인재가 있습니다. ' + (isLord(o) ? '주공께서 직접' : josa(o.n, '이가')) + ' 찾아 나서면 오늘 만날 것입니다.' : b.n + '에 숨은 인재가 있는 듯합니다. 탐색해 보시지요.'; }
    else { tip = '숨은 인재 <i class="adv n">×</i>'; say = b.n + '에 숨은 인재가 있는 듯하나, 오늘은 만나기 어렵겠습니다. 다음 턴에 찾아보시지요.'; }
  } else if (c.kind === 'reward') {
    t = off(x.t); go = ['base', b.id, 'men']; tip = t.n + ' 충성 ' + x.loy + ' → 포상';
    say = L === 2 ? b.n + '의 ' + josa(t.n, '은는') + ' 충성이 ' + x.loy + '입니다. 포상으로 마음을 잡아 두십시오.' : b.n + ' — 마음이 뜬 무장이 있습니다. 포상하시지요.';
  } else if (c.kind === 'train') {
    go = ['base', b.id, b.kind === 'city' ? 'home' : 'mil']; tip = '기력 ' + x.morale + ' → 훈련';
    say = L === 2 ? b.n + ' 병사들의 기력이 ' + x.morale + '입니다. 싸움에 앞서 훈련해 두십시오.' : b.n + ' — 군의 기력이 낮습니다. 훈련하십시오.';
  } else if (c.kind === 'draft') {
    tip = '병력 ' + fmt(x.troops) + ' < 이웃 ' + fmt(x.thr) + ' → 징병';
    if (L === 0) say = b.n + ' — 병사를 더 모으시지요.';
    else if (x.soon) say = L === 2 ? '이웃 ' + nbName() + '의 병력이 ' + fmt(x.thr) + '인데 ' + josa(b.n, '은는') + ' ' + fmt(x.troops) + '뿐입니다. 징병하십시오.' + (x.pl > 0 ? ' 보호는 ' + days(x.pl) + ' 남았습니다.' : '') : b.n + '의 병력이 이웃 ' + nb.n + '보다 적습니다. 징병하십시오.';
    else say = L === 2 ? '보호가 끝나기 전에 ' + b.n + '의 병력을 길러 두십시오. 이웃 ' + nbName() + '의 병력은 ' + fmt(x.thr) + '입니다.' : '보호가 끝나기 전에 ' + b.n + '의 병력을 길러 두시지요.';
  } else if (c.kind === 'build') {
    var FN = FAC[x.t].name, lm = lotMark(lotNo(b, x.pi)), gt = x.gain.gold ? '금 +' + fmt(x.gain.gold) + '/월' : (x.gain.food ? '병량 +' + fmt(x.gain.food) + '/분기' : '');
    go = ['base', b.id, 'fac'];
    if (L === 0) { tip = '빈 부지 ' + x.empty + '곳 → 건설'; say = b.n + ' — 빈 부지가 ' + x.empty + '곳 있습니다. 시설을 지으시지요.'; }
    else {
      tip = lm + ' ' + FN + (gt ? ' ' + gt : '');
      if (x.why === 'nobarracks') say = b.n + '에 병영이 없어 징병을 못 합니다. ' + (L === 2 ? lm + ' 부지에 ' : '') + '병영을 지으십시오.';
      else if (x.why === 'food') say = L === 2 ? b.n + '의 병량 수입(분기 +' + fmt(x.fi) + ')이 군량(분기 −' + fmt(x.upkeep) + ')에 못 미칩니다. ' + lm + ' 부지에 농장을 지으십시오.' : b.n + '의 병량 수입이 군량에 못 미칩니다. 농장을 지으십시오.';
      else say = L === 2 ? b.n + ' ' + lm + ' 부지에 ' + josa(FN, '을를') + ' 지으면 ' + gt + '입니다.' : b.n + '에 ' + josa(FN, '을를') + ' 더 지으시지요.';
    }
  } else if (c.kind === 'produce') {
    tip = '무기 ' + fmt(x.arms) + ' → 생산';
    say = L === 2 ? b.n + '의 병력 ' + fmt(x.troops) + '에 창·극·노가 ' + fmt(x.arms) + '뿐입니다. 대장간을 돌리십시오.' : b.n + ' — 무기가 모자랍니다. 생산하시지요.';
  } else if (c.kind === 'buyfood') {
    tip = '병량 ' + days(x.ft) + '분 → 거래';
    say = L === 2 ? b.n + '의 병량이 ' + days(x.ft) + '분뿐입니다. 금으로 병량을 사 두십시오(금 1에 병량 4).' : b.n + ' — 병량이 모자랍니다. 거래로 사 두십시오.';
  } else if (c.kind === 'sellfood') {
    tip = '금 ' + fmt(x.gold) + ' → 병량 팔기';
    say = L === 2 ? b.n + '의 금이 ' + fmt(x.gold) + '뿐입니다. 남는 병량을 팔아 금을 마련하시지요(병량 6에 금 1).' : b.n + ' — 금이 모자랍니다. 남는 병량을 파시지요.';
  } else if (c.kind === 'vacant') {
    go = ['base', b.id, 'mil']; tip = '빈 ' + nb.n + ' → 출진';
    say = L === 0 ? b.n + ' — 군을 낼 수 있습니다.' : '이웃 ' + josa(nb.n, '이가') + ' 주인 없이 비어 있습니다. ' + b.n + '에서 군을 보내 차지하십시오.';
  } else if (c.kind === 'strike') {
    go = ['base', b.id, 'mil']; tip = nb.n + ' 수비 ' + fmt(x.def) + ' → 출진';
    say = L === 0 ? b.n + ' — 군을 낼 수 있습니다.' : (L === 2 ? nbName() + '의 수비는 ' + fmt(x.def) + '뿐입니다. ' + b.n + '의 ' + fmt(x.troops) + '이면 칠 만합니다.' : nb.n + '의 수비가 허술합니다. ' + b.n + '에서 군을 내시지요.') + (x.brk ? ' 다만 먼저 치면 그 세력과의 보호가 풀립니다.' : '');
  }
  return { say: say, tip: tip, go: go, key: c.key, w: c.w, kind: c.kind };
}
/* 거점 줄의 조언: 그 거점에 대한 헌책 가운데 앞의 둘 */
function baseAdvice(b, cs) {
  var n = idleOfficers(b).length; if (!n) return null;
  var L = (cs || counsel(G.player)).list.filter(function (c) { return c.b === b.id; }); if (!L.length) return null;
  var tx = L.slice(0, 2).map(counselText);
  return { n: n, tips: tx.map(function (t) { return t.tip; }), tab: tx[0].go[0] === 'recruit' ? 'men' : tx[0].go[2], say: tx[0].say };
}
/* 지금 군사가 말할 헌책 하나: 한 번 한 말은 COUNSEL.keep 턴 동안 맨 앞에 세우지 않는다(급한 것은 예외). [다른 조언]을 누르면 다음 것 */
function counselPick(cs) {
  if (!cs || !cs.list.length) return null;
  if (UI.cGame !== G.seed0 || UI.cTurn > G.turn) { UI.cGame = G.seed0; UI.cSaid = {}; UI.cKind = {}; UI.cTurn = -1; }      // 다른 판을 열었다
  if (UI.cTurn !== G.turn) { UI.cTurn = G.turn; UI.cSkip = 0; }
  function ok(c, t) { return c.w >= COUNSEL.urgent || t === undefined || t === G.turn || G.turn - t > COUNSEL.keep; }
  var fresh = cs.list.filter(function (c) { return ok(c, UI.cSaid[c.key]); });
  var L = fresh.length ? fresh : cs.list, front = [], back = [];
  L.forEach(function (c) { (ok(c, UI.cKind[c.kind]) ? front : back).push(c); });      // 같은 종류의 말(징병 · 건설 …)도 잇달아 하지 않는다: 지난 두 턴에 한 종류는 뒤로 돌린다
  L = front.concat(back);
  var i = UI.cSkip % L.length, x = counselText(L[i]);
  UI.cSaid[L[i].key] = G.turn; UI.cKind[L[i].kind] = G.turn;
  x.n = L.length; x.i = i; x.cns = 1;
  return x;
}
""")

# 2) 지금 할 일: 헌책을 한 번 구해 거점 줄을 만든다
s = rep(s, "var x = bestRecruiter(b, t); if (x.p > 0 && x.adv && x.adv.says) out.push({ t: t, p: x.p, adv: x.adv }); });",
           "var x = bestRecruiter(b, t); if (x.p >= COUNSEL.poachMin && x.adv && x.adv.says) out.push({ t: t, p: x.p, adv: x.adv }); });      // v0.11: 성공률이 낮은 '응할 것'은 거의 헛짚은 것이라 먼저 권하지 않는다")
s = rep(s, "      var a = baseAdvice(b); if (!a) return;\n", "      var a = baseAdvice(b, CS); if (!a) return;\n")
s = rep(s, "  if (F.ap >= 10) {\n    var nb = 0, more = 0, lordLoc = off(F.lord).unit === null ? off(F.lord).loc : -1;\n",
           "  var CS = counsel(f);                                              // 군사의 헌책(v0.11) — 거점 줄과 군사의 한마디가 여기서 나온다\n  if (F.ap >= 10) {\n    var nb = 0, more = 0, lordLoc = off(F.lord).unit === null ? off(F.lord).loc : -1;\n")
s = rep(s, "  var need = 0; out.forEach(function (t) { if (t.cls !== 'cool' && !t.info && t.go) need++; });\n  out.need = need;\n",
           "  var need = 0; out.forEach(function (t) { if (t.cls !== 'cool' && !t.info && t.go) need++; });\n  out.need = need; out.cs = CS;\n")

# 3) 군사의 한마디: 급한 알림 → 헌책 → 그 밖
s = rep(s, """function advTop(list) {
  for (var i = 0; i < list.length; i++) if (list[i].say) return list[i];
  return null;
}
""",
"""function advTop(list) {
  var i;
  for (i = 0; i < list.length; i++) if (list[i].say && list[i].cls && /warn/.test(list[i].cls)) return list[i];      // 급한 알림이 먼저
  var c = counselPick(list.cs); if (c) return c;                                                                  // 평소의 헌책(v0.11)
  for (i = 0; i < list.length; i++) if (list[i].say) return list[i];
  return null;
}
""")
s = rep(s, "      advgo: function () { var t = advTop(st.todo); if (t && t.go) goTodo(t.go); },\n",
           "      advgo: function () { var t = advTop(st.todo); if (t && t.go) goTodo(t.go); },\n"
           "      advnext: function () { UI.cSkip = (UI.cSkip || 0) + 1; sfx('ui'); refreshSheet(); },\n")
s = rep(s, "'<span class=\"tx\"><i>군사 <b>' + A.n + '</b></i><span>' + (top ? top.say : '…') + '</span></span></button>'",
           "'<span class=\"tx\"><i>군사 <b>' + A.n + '</b>' + (top && top.cns && top.n > 1 ? ' <em class=\"cnt2\">' + (top.i + 1) + '/' + top.n + '</em>' : '') + '</i><span>' + (top ? top.say : '…') + '</span></span></button>'")
s = rep(s, "        '<button class=\"btn' + (A ? '' : ' pri') + ' hm-adv\" type=\"button\" data-a=\"adv\">' + (A ? '바꾸기' : '임명') + '</button></div>' +\n",
           "        '<div class=\"hm-advb\">' + (A && top && top.cns && top.n > 1 ? '<button class=\"btn hm-nx\" type=\"button\" data-a=\"advnext\">다른 조언</button>' : '') + '<button class=\"btn' + (A ? '' : ' pri') + ' hm-adv\" type=\"button\" data-a=\"adv\">' + (A ? '바꾸기' : '임명') + '</button></div></div>' +\n")

# 4) 탐색: 군사의 조언
s = rep(s, """  pickOfficers({ title: '탐색 — 담당 무장', list: idleOfficers(b), max: 1, hi: 'pol', key: function (o) { return o.pol + (o.sk === '안력' ? 50 : 0); }, auto: function (n) { return autoPick('search', b, null, 1); }, preview: function () { return '인재나 재물을 찾습니다'; } },
    function (os) {
      var r = cmdSearch(b, os[0].id);
      if (!r.ok) return done(r);
      if (r.found !== undefined) { sfx('drum'); done(r, josa(off(r.found).n, '을를') + ' 찾았습니다', '', os[0], 'found', off(r.found).n); }
      else if (r.gold) done(r, '금 ' + josa(String(r.gold), '을를') + ' 찾았습니다', '', os[0], 'gold');
      else done(r, '아무것도 찾지 못했습니다', '', os[0], 'nothing');
    });
""",
"""  pickOfficers({ title: '탐색 — 담당 무장', list: idleOfficers(b), max: 1, hi: 'pol', key: function (o) { return o.pol + (o.sk === '안력' ? 50 : 0); }, auto: function (n) { return autoPick('search', b, null, 1); }, preview: function () { return '인재나 재물을 찾습니다'; },
      rt: function (o) { return advMark(searchAdvice(b, o)) + (o.sk || '—'); },
      say: function (os) { return advSay(searchAdvice(b, os[0]), '', '오늘 숨은 인재를 만날 것입니다.', '오늘은 인재를 만나지 못할 것입니다.'); } },
    function (os) {
      var a0 = searchAdvice(b, os[0]), r = cmdSearch(b, os[0].id);
      if (!r.ok) return done(r);
      var miss = advAfter(a0, r.found !== undefined), tail = miss ? '<i class="tk-adv">군사 ' + a0.adv.n + ': ' + miss + '</i>' : '';
      if (r.found !== undefined) { sfx('drum'); done(r, josa(off(r.found).n, '을를') + ' 찾았습니다' + tail, '', os[0], 'found', off(r.found).n); }
      else if (r.gold) done(r, '금 ' + josa(String(r.gold), '을를') + ' 찾았습니다' + tail, '', os[0], 'gold');
      else done(r, '아무것도 찾지 못했습니다' + tail, '', os[0], 'nothing');
    });
""")
s = rep(s, "function recruitAdvice(b, o, t) {", "function searchAdvice(b, o) { return advise(G.player, searchRoll(b), searchRollA(b), searchChance(b, o), 0); }      // 탐색(v0.11): 숨은 인재를 오늘 만나는가\nfunction recruitAdvice(b, o, t) {")

# 5) 도움말
s = rep(s, "군사는 지금 가장 급한 일을 말해 주고 — 누르면 그 일로 갑니다 — 내 차례가 시작될 때도 대화창으로 알립니다.",
           "군사는 지금 가장 급한 일을 말해 주고 — 누르면 그 일로 갑니다 — 내 차례가 시작될 때도 대화창으로 알립니다. 급한 알림이 없을 때는 <b>헌책</b>(평소의 조언)을 하나씩 말하고, <b>다른 조언</b>을 누르면 다음 것을 듣습니다.")
s = rep(s, "  '<p>등용과 계략의 성패는 <b>대상마다 미리 정해져 있습니다</b>(계략과 재야·포로 등용은 턴마다, 다른 세력 무장의 등용은 달마다).",
           "  '<p><b>헌책과 지력</b> — 헌책은 순찰·등용·탐색·포상·훈련·징병·건설·무기·거래·출진 가운데 지금 할 만한 일입니다. 군사의 지력이 높을수록 <b>정말 급한 것부터</b> 말하고(지력이 낮으면 순위가 뒤섞입니다), <b>알아채기 어려운 일</b>(숨은 인재 · 허술한 이웃 거점 · 무엇을 지을지)을 놓치지 않으며, 말이 자세합니다 — 지력 ' + COUNSEL.detail + ' 이상이면 숫자와 보낼 사람까지, ' + COUNSEL.some + ' 이상이면 무엇을 할지, 그 아래는 두루뭉술하게. 징병은 길로 이어진 이웃 세력의 병력이 우리보다 많을 때만 권합니다. 한 번 한 말은 ' + days(COUNSEL.keep) + ' 동안 맨 앞에 다시 세우지 않고, 같은 종류의 말(징병 · 건설 …)도 잇달아 하지 않습니다(급한 일은 예외).</p>' +\n"
           "  '<p><b>탐색</b>의 결과도 미리 정해져 있습니다(도시 · 턴 · 그 턴의 몇 번째인가). 탐색할 무장을 고르면 군사가 <b>오늘 숨은 인재를 만날지</b> 말해 줍니다. 숨은 인재가 있는 도시는 헌책으로 귀띔해 주는데, 있는지 없는지를 아는 것도 지력만큼만 맞습니다(달마다 정해집니다).</p>' +\n"
           "  '<p>등용과 계략의 성패는 <b>대상마다 미리 정해져 있습니다</b>(계략과 재야·포로 등용은 턴마다, 다른 세력 무장의 등용은 달마다).")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- style.css
p = 'src/style.css'; s = io.open(p, encoding='utf-8').read()
s += """/* 군사의 헌책 */
.hm-advb { display: flex; flex-direction: column; gap: 4px; flex: none; justify-content: center; }
.hm-advb .btn { flex: 1; height: auto; min-width: 58px; min-height: 27px; padding: 2px 9px; font-size: 12px; display: flex; align-items: center; justify-content: center; }      /* [다른 조언](.hm-nx) · [바꾸기](.hm-adv — 전부터 쓰던 이름 그대로) */
.hm-advp .tx > span { -webkit-line-clamp: 3; font-size: 13px; }
.hm-advb .btn.hm-nx { background: var(--paper-2); }
.hm-say .cnt2 { font: 600 10.5px var(--font-body); font-style: normal; color: var(--dim); margin-left: 3px; }
.todo small .adv { font-style: normal; font-size: 12px; }
/* 무장을 고르는 표: 줄이 많을 때 줄어드는 것은 표뿐이다 — 고른 무장의 이름과 군사의 말이 잘리지 않게 */
.selstrip, .pksay, .dlg-h, .dlg-f { flex: none; }
"""
io.open(p, 'w', encoding='utf-8').write(s)
print('p4 ok')
