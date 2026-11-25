# -*- coding: utf-8 -*-
"""v0.23 (1) 규칙: 시대(시나리오) · 수명 · 후계.   python3 build/v023/s1_core.py   (src/ 를 고친다 — apply.sh 가 v0.22.1 백업에서 되돌린 뒤 부른다)"""
import io, os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8').write(s)


def rep(s, a, b, n=1):
    assert s.count(a) == n, (a[:70], s.count(a))
    return s.replace(a, b)


# ───────── data.js ─────────
d = rd('src/data.js')
d = rep(d, "var GAME_VERSION = 'v0.22.1';", "var GAME_VERSION = 'v0.23';")
d = rep(d, "'조진': '혈연', '하후상': '혈연', '하후패': '혈연', '하후무': '혈연', '하후덕': '혈연' },      // v0.17",
        "'조진': '혈연', '하후상': '혈연', '하후패': '혈연', '하후무': '혈연', '하후덕': '혈연', '조예': '혈연' },      // v0.17 · v0.23(조예)")
d = rep(d, "  '공손도': { '공손강': '혈연', '공손공': '혈연' },", "  '공손도': { '공손강': '혈연', '공손공': '혈연', '공손연': '혈연' },")
d = rep(d, "  '유장': { '황권': '심복', '장임': '심복', '엄안': '심복', '왕루': '심복', '오씨': '인척' }\n};",
        """  '유장': { '황권': '심복', '장임': '심복', '엄안': '심복', '왕루': '심복', '오씨': '인척' },
  /* v0.23: 다른 시대의 군주들. 뒤에 붙인다(앞의 차례가 바뀌면 '같은 주군과의 인연'을 찾는 차례가 달라진다) */
  '손견': { '손책': '혈연', '손권': '혈연', '손익': '혈연', '손상향': '혈연', '손정': '혈연', '손분': '혈연', '오경': '인척', '오국태': '부부', '정보': '심복', '황개': '심복', '한당': '심복', '조무': '심복', '주치': '심복' },
  '손권': { '노숙': '심복', '여몽': '심복', '육손': '인척', '제갈근': '심복', '주태': '심복', '보연사': '부부', '손등': '혈연', '손휴': '혈연' },
  '동탁': { '동민': '혈연', '우보': '인척', '이각': '심복', '곽사': '심복' },
  '장각': { '장보': '혈연', '장량': '혈연' },
  '유언': { '유장': '혈연' },
  '조비': { '조예': '혈연', '견씨': '부부', '곽여왕': '부부', '사마의': '심복', '진군': '심복' },
  '유선': { '장완': '심복', '비의': '심복' },
  '유우': { '선우보': '심복', '전주': '심복' }
};
/* v0.23 수명: warn = 숨을 거두기 몇 달 앞서 병석에 눕는가(그때 알린다) · old = 옛 저장을 열었을 때, 이미 수명이 지난 사람에게 더 주는 해(1 ~ old 년에 걸쳐 차례로 떠난다)
   add · min = 처형 · 전사한 사람의 수명: max(역사의 해 + add, 태어난 해 + min). 명부를 만들 때(tools/roster23.py 의 LIFE_ADD · LIFE_MIN) 이미 셈해 넣었다 — 여기 값은 도움말과 시험(tests/v23.js)이 본다 */
var LIFE = { warn: 3, old: 5, add: 15, min: 60 };
/* v0.23 후계: 군주가 죽으면 뒤를 잇는 차례 = 정해 둔 후계 → 아들(나이순) → 형제(나이순) → 그 밖의 혈연(매력순. 남자 먼저) → 남(매력 × 2 + 통솔 + 정치가 높은 순. 남자 먼저).
   충성: 새 군주와 인연이 있거나(직접 · 선대의 인연이 한집안으로 이어짐) 이어지면 100 그대로.
   선대와 인연이 있었는데 끊긴 사람 — 한집안(혈연 · 의형제 · 부부 · 인척)은 반드시 kin 만큼, 심복은 bondP% 로 bond 만큼 내린다.
   인연이 없던 사람 — base + (선대 매력 − 새 군주 매력) × cha + (공적이 새 군주보다 높으면 merit) − (미리 정해 둔 후계면 named) % (min ~ max) 로 drop 만큼 내린다.
   그렇지 않고 새 군주의 매력이 upAt 넘게 높으면 upP% 로 up 만큼 오른다. 어느 쪽도 아니면 그대로다. */
var HEIR = { kin: [15, 25], bond: [8, 15], bondP: 70, base: 25, cha: 1.5, merit: 20, named: 10, min: 5, max: 85, drop: [4, 12], upAt: 10, upP: 30, up: [3, 6] };""")
d = rep(d, "/* 인연: 군주와 깊은 사이인 무장(군주 이름 → { 무장 이름: 사이 }). 그 군주를 모시는 동안 충성이 100 에서 내려가지 않는다.",
        "/* 인연: 군주와 깊은 사이인 무장(군주 이름 → { 무장 이름: 사이 }). 그 군주를 모시는 동안 충성이 100 에서 내려가지 않는다.\n   v0.23: 군주가 바뀌어도 새 군주가 선대와 한집안이면 선대의 인연이 이어진다(혈연 · 인척은 그대로, 의형제 · 심복은 '세신') — core.js 의 bondUnder")
wr('src/data.js', d)

# ───────── bios.js: 새 무장의 열전 ─────────
b = rd('src/bios.js')
nb = json.load(io.open(os.path.join(ROOT, 'build', 'v023', 'bios_new.json'), encoding='utf-8'))
tail = "'\n};\nfunction bioOf(o)"
assert b.count(tail) == 1
add = ''.join(",\n'%s': '%s'" % (k, v) for k, v in nb.items())
assert "'" not in ''.join(nb.values()) and '\\' not in ''.join(nb.values())
b = b.replace(tail, "'" + add + "\n};\nfunction bioOf(o)")
b = rep(b, "/* 무장 열전 (v0.19) — 이름 → 두세 문장.", "/* 무장 열전 (v0.19, v0.23 에서 새 무장 %d명) — 이름 → 두세 문장." % len(nb))
wr('src/bios.js', b)

# ───────── core.js ─────────
c = rd('src/core.js')
c = rep(c, "function dateOfTurn(t) { var m = Math.floor((t - 1) / 3); return (194 + Math.floor(m / 12))",
        "function dateOfTurn(t, y0) { var m = Math.floor((t - 1) / 3); return ((y0 || SCENARIO.year || 194) + Math.floor(m / 12))")
c = rep(c, """function startTroops(i) {
  var sf = SCENARIO.factions[i], st = START[sf.n] || [10000, 1500, 15000, 1000], t = 0, j;
  for (j = 0; j < sf.cities.length; j++) t += Math.round(st[0] * (j === 0 ? 1 : 0.55) / 100) * 100;
  for (var gn in SCENARIO.gates) if (SCENARIO.gates[gn] === i && baseByName(gn) >= 0) t += 2000;
  return t;
}""", """function startTroops(i, S) {                 // v0.23: S = 들여다볼 시대(없으면 지금 판의 시대)
  S = S || SCENARIO;
  var sf = S.factions[i], st = sf.start || START[sf.n] || [10000, 1500, 15000, 1000], t = 0, j;
  for (j = 0; j < sf.cities.length; j++) t += Math.round(st[0] * (j === 0 ? 1 : (sf.mul || 0.55)) / 100) * 100;
  for (var gn in S.gates) if (S.gates[gn] === i && baseByName(gn) >= 0) t += 2000;
  return t;
}""")
c = rep(c, """(function () {
  for (var i = 0; i < SCENARIO.factions.length; i++) {
    var c = SCENARIO.factions[i].color, v = parseInt(c.slice(1), 16), r = (v >> 16) & 255, g = (v >> 8) & 255, b = v & 255;
    r = Math.round(r * 0.80 + 104 * 0.20); g = Math.round(g * 0.80 + 98 * 0.20); b = Math.round(b * 0.80 + 88 * 0.20);
    SCENARIO.factions[i].color = '#' + ((1 << 24) | (r << 16) | (g << 8) | b).toString(16).slice(1);
  }
})();""", """function scenTint(S) {
  if (S._tint) return S;
  S._tint = 1;
  for (var i = 0; i < S.factions.length; i++) {
    var c = S.factions[i].color, v = parseInt(c.slice(1), 16), r = (v >> 16) & 255, g = (v >> 8) & 255, b = v & 255;
    r = Math.round(r * 0.80 + 104 * 0.20); g = Math.round(g * 0.80 + 98 * 0.20); b = Math.round(b * 0.80 + 88 * 0.20);
    S.factions[i].color = '#' + ((1 << 24) | (r << 16) | (g << 8) | b).toString(16).slice(1);
  }
  return S;
}
scenTint(SCENARIO);
/* ---------- 시대(v0.23) ---------- 명부(roster.js)의 scenarioMake(id) 가 시대 하나를 예전의 SCENARIO 꼴로 펼친다.
   SCENARIO 는 '지금 판의 시대'다: 새 판을 만들 때(newGame)와 저장을 열 때(deserialize) scenarioUse 로 바꾼다. 들여다보기만 할 때는 scenarioPeek. */
function scenarioPeek(id) { return scenTint(scenarioMake(id || '194')); }
function scenarioUse(id) { SCENARIO = scenarioPeek(id); return SCENARIO; }
function scenarioList() { return SCENS.map(function (s) { return { id: s.id, year: s.year, name: s.name, han: s.han, sub: s.sub, nf: s.factions.length }; }); }
function facHouse(f) { var F = G.factions[f]; return F ? (F.house || houseName(F.n0 || F.name)) : ''; }      // 세력의 집안(처음 일으킨 사람의 이름) — 군주가 바뀌어도 그대로다
function offByName(n) { for (var i = 0; i < G.officers.length; i++) if (G.officers[i].n === n) return G.officers[i]; return null; }
function lifeInit(o, so) { o.by = so.by; o.dy = so.dy; o.dm = so.dm || 6; if (so.e) o.e = so.e; if (so.fa) o.dad = so.fa; }      // 생몰년(태어난 해 · 수명이 다하는 해와 달 · 추정 표시) · 아버지""")
c = rep(c, """function newGame(playerFaction, seed) {
  var i, j;
  G = {
    ver: 2, year: 194, month: 1, xun: 0, turn: 1,""", """function newGame(playerFaction, seed, scen) {      // v0.23: scen = 시대(없으면 194년 군웅할거)
  var i, j;
  scenarioUse(scen);
  G = {
    ver: 2, scen: SCENARIO.id, life: 1, year: SCENARIO.year, month: SCENARIO.month || 1, xun: 0, turn: 1,""")
c = rep(c, "    G.factions.push({ id: i, name: sf.n, color: sf.color, lord: -1, ap: 80, alive: true, adv: -1 });",
        "    G.factions.push({ id: i, name: sf.n, color: sf.color, lord: -1, ap: 80, alive: true, adv: -1, n0: sf.n, house: sf.house || sf.n, past: (sf.anc || []).slice(), heir: -1 });      // v0.23: n0 처음 이름 · house 집안 · past 앞선 군주들 · heir 정해 둔 후계")
c = rep(c, """    var sf2 = SCENARIO.factions[i], st = START[sf2.n] || [10000, 1500, 15000, 1000];
    for (j = 0; j < sf2.cities.length; j++) {
      var cb = G.bases[baseByName(sf2.cities[j])], cap = j === 0, m = cap ? 1 : 0.55;
      cb.owner = i; cb.troops = Math.round(st[0] * m / 100) * 100; cb.gold = Math.round(st[1] * (cap ? 1 : 0.6));
      cb.food = Math.round(st[2] * (cap ? 1 : 0.6)); cb.morale = 70; cb.order = 75;""", """    var sf2 = SCENARIO.factions[i], st = sf2.start || START[sf2.n] || [10000, 1500, 15000, 1000], m2 = sf2.mul ? sf2.mul + 0.05 : 0.6;      // v0.23: 시대마다 제 형편(큰 세력은 성마다의 몫이 작다)
    for (j = 0; j < sf2.cities.length; j++) {
      var cb = G.bases[baseByName(sf2.cities[j])], cap = j === 0, m = cap ? 1 : (sf2.mul || 0.55);
      cb.owner = i; cb.troops = Math.round(st[0] * m / 100) * 100; cb.gold = Math.round(st[1] * (cap ? 1 : m2));
      cb.food = Math.round(st[2] * (cap ? 1 : m2)); cb.morale = 70; cb.order = 75;""")
c = rep(c, """      f: so.f, st: so.st || 'active', loc: baseByName(so.c), unit: null, loy: 100, merit: 0, acted: false, y: so.y || 0, j: so.j || null, capF: -1, dest: -1, eta: 0, pf: so.f };
    if (o.f >= 0) {
      if (SCENARIO.factions[o.f].n === o.n) { G.factions[o.f].lord = i; o.merit = 2000; }""", """      f: so.f, st: so.st || 'active', loc: baseByName(so.c), unit: null, loy: 100, merit: 0, acted: false, y: so.y || 0, j: so.j || null, capF: -1, dest: -1, eta: 0, pf: so.f };
    lifeInit(o, so);
    if (o.f >= 0) {
      if (SCENARIO.factions[o.f].n === o.n) { G.factions[o.f].lord = i; o.merit = 2000; }""")
# 장성: 아버지가 섬기는 세력 → 집안
c = rep(c, """      if (h.st !== 'hidden' || !h.j || h.y > G.year) continue;
      var lf = -1;
      for (var q = 0; q < G.factions.length; q++) if (G.factions[q].alive && G.factions[q].name === h.j) lf = q;
      if (lf >= 0) {""", """      if (h.st !== 'hidden' || h.y > G.year) continue;
      var lf = -1, dd = h.dad ? offByName(h.dad) : null;
      if (dd && dd.f >= 0 && (dd.st === 'active' || dd.st === 'travel') && G.factions[dd.f].alive) lf = dd.f;      // v0.23: 아버지가 섬기는 세력으로 간다
      if (lf < 0 && !h.j) continue;                                      // 따라갈 곳이 없다: 그 도시에서 탐색으로 찾는다
      if (lf < 0) for (var q = 0; q < G.factions.length; q++) if (G.factions[q].alive && facHouse(q) === houseName(h.j)) lf = q;      // v0.23: 이름이 아니라 집안으로 찾는다(군주가 바뀌어도 간다)
      if (lf >= 0) {""")
c = rep(c, """      h.j = null;
    }
  }
}
""", """      h.j = null;
    }
  }
  if (newMonth) lifeTick();                                              // v0.23: 수명
}
""")
c = rep(c, """function bondWith(o, f) {                 // 무장 o 와 세력 f 의 군주 사이(없으면 null)
  if (!o || f === undefined || f < 0 || !G.factions[f] || G.factions[f].lord === o.id) return null;
  var L = off(G.factions[f].lord), m = L && BONDS[L.n];
  return (m && m[o.n]) || null;
}""", """function bondWith(o, f) {                 // 무장 o 와 세력 f 의 군주 사이(없으면 null)
  if (!o || f === undefined || f < 0 || !G.factions[f] || G.factions[f].lord === o.id) return null;
  var F = G.factions[f];
  return bondUnder(o, off(F.lord), F.past, F.pastD);
}
/* v0.23: 군주 L 아래에서 무장 o 의 인연. past = 앞선 군주들의 이름(오래된 것부터), pastD = 그들의 아버지 이름.
   ① 군주와 직접(BONDS) ② 거꾸로(내가 모시던 일가가 군주가 되었다 — 심복은 빼고) ③ 군주의 자식 · 형제 · 아버지 ④ 선대의 인연 — 새 군주가 그 선대와 한집안일 때만 이어진다(혈연 · 부부 → 혈연, 인척 → 인척, 의형제 · 심복 → 세신) */
function bondUnder(o, L, past, pastD) {
  if (!o || !L || o.id === L.id) return null;
  var m = BONDS[L.n]; if (m && m[o.n]) return m[o.n];
  var n = BONDS[o.n]; if (n && n[L.n] && n[L.n] !== '심복') return n[L.n];      // 거꾸로: 혈연 · 의형제 · 부부 · 인척은 서로의 사이다(심복은 아니다 — 주인이 옛 신하의 심복이 되지는 않는다)
  if ((o.dad && (o.dad === L.n || o.dad === L.dad)) || (L.dad && L.dad === o.n)) return '혈연';
  for (var i = (past ? past.length : 0) - 1; i >= 0; i--) {
    var P = past[i], pm = BONDS[P], t = (pm && pm[o.n]) || (o.dad === P ? '혈연' : null);
    if (!t || !famName(P, pastD ? pastD[i] : '', L)) continue;
    if (t === '의형제' && pm && pm[L.n] === '의형제') return '의형제';      // 같은 맹세의 형제(관우가 뒤를 이으면 장비는 여전히 의형제)
    return (t === '혈연' || t === '부부') ? '혈연' : (t === '인척' ? '인척' : '세신');
  }
  return null;
}
function famName(P, Pdad, L) {             // 앞선 군주 P(이름)와 지금 군주 L 이 한집안인가(혈연 · 의형제 · 부부)
  var m = BONDS[P], n = BONDS[L.n], t = (m && m[L.n]) || (n && n[P]) || null;
  if (t === '혈연' || t === '의형제' || t === '부부') return true;
  if (L.dad && (L.dad === P || L.dad === Pdad)) return true;
  for (var Q in BONDS) if (BONDS[Q][P] === '혈연' && BONDS[Q][L.n] === '혈연') return true;
  return false;
}
function kinOf(a, b) {                     // 두 사람이 혈연인가
  if (!a || !b || a === b) return false;
  if ((a.dad && (a.dad === b.n || a.dad === b.dad)) || (b.dad && b.dad === a.n)) return true;
  var m = BONDS[a.n], n = BONDS[b.n];
  if ((m && m[b.n] === '혈연') || (n && n[a.n] === '혈연')) return true;
  for (var Q in BONDS) { var q = BONDS[Q]; if ((q[a.n] === '혈연' || (a.dad && q[a.dad] === '혈연')) && (q[b.n] === '혈연' || (b.dad && q[b.dad] === '혈연'))) return true; }      // 같은 어른의 혈연(아버지가 그 혈연이어도)
  return false;
}""")
c = rep(c, "   세력의 군주(G.factions[f].lord)는 바뀌지 않으므로 '누가 누구의 옛 주군인가'는 이것만으로 알 수 있다. */",
        "   '누가 누구의 옛 주군인가'는 세력으로 본다 — v0.23 부터 군주가 수명으로 바뀔 수 있다: 그때는 뒤를 이은 사람이 그 세력의 '주군'이다. */")
c = rep(c, "t.st = 'dead'; t.f = -1; t.capF = -1; t.exBy = b.owner; return { ok: true }; }", "t.st = 'dead'; t.f = -1; t.capF = -1; t.exBy = b.owner; t.died = G.year; return { ok: true }; }")

LIFE_JS = r"""/* ================= 수명 · 후계(v0.23) =================
   무장마다 by(태어난 해) · dy(수명이 다하는 해) · dm(그 달)이 있다 — 명부(roster.js)에서 온다. 병사 · 자연사한 사람은 역사의 그 해, 처형 · 전사한 사람은 더 오래 산다.
   달이 바뀔 때(roundEnd) lifeTick 이 본다: LIFE.warn 달 앞서 병석에 눕고(알림), 때가 되면 숨을 거둔다. 출진 · 이동 중이면 거점에 돌아올 때까지 버틴다.
   군주가 죽으면 succeed — 뒤를 이을 사람이 없으면 세력이 무너진다(거점은 주인 없는 땅이 된다). 판의 난수(rnd)는 쓰지 않는다(omenRoll). */
function ageOf(o) { return o && o.by ? ((o.st === 'dead' && o.died ? o.died : G.year) - o.by + 1) : 0; }      // 세는나이(태어난 해가 한 살)
function lifeDue(o, ahead) { return !!o.dy && G.year * 12 + G.month + (ahead || 0) >= o.dy * 12 + (o.dm || 6); }
function offAt(o) {                        // 무장이 있는 곳 { c, r }
  if (o.unit !== null && o.unit !== undefined && UMAP[o.unit]) return { c: UMAP[o.unit].c, r: UMAP[o.unit].r };
  var b = G.bases[o.st === 'travel' && o.dest >= 0 ? o.dest : o.loc] || G.bases[0];
  return { c: b.c, r: b.r };
}
function lifeTick() {
  if (G.life !== 1) return;
  for (var i = 0; i < G.officers.length; i++) {
    var o = G.officers[i];
    if (o.st === 'dead' || !o.dy) continue;
    if (o.st === 'hidden') { if (lifeDue(o)) { o.st = 'dead'; o.died = G.year; } continue; }      // 세상에 나오기 전에 떠났다
    if (!lifeDue(o, LIFE.warn)) continue;
    if (!lifeDue(o)) {
      if (!o.sick) {
        o.sick = 1;
        if (o.f >= 0 && o.st !== 'captive') {
          var p = offAt(o), lord = isLord(o);
          logMsg(josa(o.n, '이가') + ' 병석에 누웠다(' + ageOf(o) + '세)', p.c, p.r, o.f, (o.f === G.player ? 1 : 0) + (lord ? 1 : 0));      // 남의 무장은 알리지 않는다(군주만 '천하의 움직임'에)
          if (o.f === G.player && !G.aiOnly) ev({ t: 'news', f: o.f, c: p.c, r: p.r, warn: 1, text: '<b>' + josa(o.n, '이가') + ' 병석에 누웠습니다</b> (' + ageOf(o) + '세)' + (lord ? ' — 후계를 정해 두십시오' : '') });
        }
      }
      continue;
    }
    if (o.unit !== null || o.st === 'travel') continue;
    officerDies(o);
  }
}
function deathWord(o) { return ageOf(o) >= 70 ? '노환으로 별세' : '병사'; }
function officerDies(o) {
  var f = o.f, F = f >= 0 ? G.factions[f] : null, cap = o.st === 'captive', p = offAt(o), age = ageOf(o), word = deathWord(o);
  if (cap) { var hb = G.bases[o.loc], ci = hb ? hb.captives.indexOf(o.id) : -1; if (ci >= 0) hb.captives.splice(ci, 1); }
  if (F && F.alive && F.lord === o.id) { succeed(f, o, age, word); return; }
  o.st = 'dead'; o.died = G.year; o.unit = null; o.capF = -1; o.f = -1; o.job = null; delete o.sick;
  if (!F || !F.alive) return;
  logMsg(o.n + ' ' + word + ' (향년 ' + age + '세)', p.c, p.r, f, f === G.player ? 2 : 0);
  if (f === G.player && !G.aiOnly) ev({ t: 'news', f: f, c: p.c, r: p.r, warn: 1, text: '<b>' + josa(o.n, '이가') + ' 세상을 떠났습니다</b> — ' + word + ' (향년 ' + age + '세)' });
  if (F.heir === o.id) F.heir = -1;
  if (F.adv === o.id) autoAdvisor(f);
  if (f === G.player) corpsFix();
}
function isWoman(o) { return SCENARIO.women.indexOf(o.n) >= 0 || o.sex === 'f'; }
function heirOk(o, f) { return !!o && o.f === f && (o.st === 'active' || o.st === 'travel') && G.factions[f].lord !== o.id; }
function heirOf(f) { var F = G.factions[f], o = (F && F.heir !== undefined && F.heir >= 0) ? off(F.heir) : null; return heirOk(o, f) ? o : null; }      // 정해 둔 후계(없으면 null)
function heirClass(o, L, F) {              // 0 정해 둔 후계 · 1 아들 · 2 형제 · 3 그 밖의 혈연(남) · 4 혈연(여) · 5 남 · 6 남(여)
  if (F.heir === o.id) return 0;
  var w = isWoman(o);
  if (o.dad && o.dad === L.n && !w) return 1;
  if (o.dad && L.dad && o.dad === L.dad && !w) return 2;
  return kinOf(o, L) ? (w ? 4 : 3) : (w ? 6 : 5);
}
function heirScore(o) { return o.cha * 2 + o.ldr + o.pol; }      // 혈연이 없을 때: 매력을 가장 크게, 통솔 · 정치를 함께 본다
function heirRank(f) {                     // 뒤를 이을 차례대로
  var F = G.factions[f], L = off(F.lord), cl = {};
  var os = G.officers.filter(function (o) { return heirOk(o, f); });
  os.forEach(function (o) { cl[o.id] = heirClass(o, L, F); });
  os.sort(function (a, b) { var x = cl[a.id], y = cl[b.id]; return x - y || ((x === 1 || x === 2) ? (a.by || 999) - (b.by || 999) : ((x === 3 || x === 4) ? b.cha - a.cha : heirScore(b) - heirScore(a))) || a.id - b.id; });
  return os;
}
function heirNext(f) { var r = heirRank(f); return r.length ? r[0] : null; }
function cmdHeir(id) {                     // 후계를 정한다(같은 사람을 다시 고르면 푼다). 행동력을 쓰지 않는다
  var f = G.player, F = G.factions[f], o = id >= 0 ? off(id) : null;
  if (id < 0 || F.heir === id) { F.heir = -1; return { ok: true, off: true }; }
  if (!heirOk(o, f)) return ERR('후계로 세울 수 없습니다');
  F.heir = id;
  return { ok: true };
}
/* h 가 뒤를 이으면 무장들이 어떻게 되는가 → { kin: 군주의 혈연인가, house: 한집안인가(혈연 · 의형제 · 부부 — 선대의 인연이 이어진다), rel: 군주와의 사이,
   keep: 인연이 이어지는 사람 수, fam: [일가인데 인연이 끊기는 사람], vas: [심복인데 끊기는 사람], n: 인연이 없는 사람 수, p: 그들이 흔들릴 확률(%, 공적이 새 군주보다 낮은 사람 기준) } */
function heirForecast(f, h) {
  var F = G.factions[f], L = off(F.lord), past = (F.past || []).concat([L.n]), pastD = (F.pastD || []).slice(), out = { keep: 0, fam: [], vas: [], n: 0, kin: kinOf(h, L), house: famName(L.n, L.dad || '', h), rel: bondOf(h) || '' };
  while (pastD.length < past.length - 1) pastD.unshift('');
  pastD.push(L.dad || '');
  G.officers.forEach(function (o) {
    if (!heirOk(o, f) || o.id === h.id) return;
    var ob = bondOf(o), nb = bondUnder(o, h, past, pastD);
    if (nb) out.keep++;
    else if (ob) (ob === '심복' || ob === '세신' ? out.vas : out.fam).push(o);
    else out.n++;
  });
  out.p = clamp(Math.round(HEIR.base + (L.cha - h.cha) * HEIR.cha - (F.heir === h.id ? HEIR.named : 0)), HEIR.min, HEIR.max);
  return out;
}
function succeed(f, old, age, word) {
  var F = G.factions[f], h = heirNext(f), p = offAt(old), named = !!h && F.heir === h.id, i;
  var os = G.officers.filter(function (o) { return o.f === f && o.id !== old.id && (o.st === 'active' || o.st === 'travel' || o.st === 'captive'); }), ob = {};
  os.forEach(function (o) { ob[o.id] = bondOf(o); });                    // 선대와의 인연(바꾸기 전에 적어 둔다)
  old.st = 'dead'; old.died = G.year; old.unit = null; old.capF = -1; old.f = -1; old.job = null; delete old.sick;
  if (!h) {
    logMsg(old.n + ' ' + word + ' (향년 ' + age + '세) — 뒤를 이을 사람이 없다', p.c, p.r, f, f === G.player ? 3 : 1);
    if (!G.aiOnly) ev({ t: 'news', f: f, c: p.c, r: p.r, warn: 1, text: '<b>' + old.n + ' ' + word + '</b> (향년 ' + age + '세) — 뒤를 이을 사람이 없습니다' });
    factionCollapse(f);
    return null;
  }
  var kin = kinOf(h, old), house = famName(old.n, old.dad || '', h), hm = h.merit, rows = [], keep = 0;
  function span(key, a) { return a[0] + omenRoll(key + '|v') / 100 * (a[1] - a[0]); }
  F.past = (F.past || []).concat([old.n]); F.pastD = (F.pastD || []).concat([old.dad || '']);
  while (F.pastD.length < F.past.length) F.pastD.unshift('');
  F.lord = h.id; F.name = h.n; F.heir = -1;
  h.loy = 100; h.merit = Math.max(h.merit, 2000);
  if (!facAdv(f)) autoAdvisor(f);
  for (i = 0; i < os.length; i++) {
    var o = os[i]; if (o.id === h.id) continue;
    var was = ob[o.id], now = bondOf(o), key = 'succ|' + f + '|' + o.id + '|' + old.id, d = 0, why = '';
    if (now) { if (o.loy < 100) { rows.push([o.id, o.loy, 100, now]); } o.loy = 100; keep++; continue; }
    if (was) {
      var fam = !(was === '심복' || was === '세신');
      if (fam || omenRoll(key + '|p') < HEIR.bondP) { d = -span(key, fam ? HEIR.kin : HEIR.bond); why = josa(old.n, '과와') + ' ' + was; }
    } else {
      var pr = clamp(HEIR.base + (old.cha - h.cha) * HEIR.cha + (o.merit > hm ? HEIR.merit : 0) - (named ? HEIR.named : 0), HEIR.min, HEIR.max);
      if (omenRoll(key + '|p') < pr) { d = -span(key, HEIR.drop); why = o.merit > hm ? '공적이 더 높다' : ''; }
      else if (h.cha - old.cha >= HEIR.upAt && omenRoll(key + '|u') < HEIR.upP) { d = span(key, HEIR.up); why = '새 주군의 덕'; }
    }
    d = Math.round(d);
    if (d) { var l0 = o.loy; o.loy = clamp(o.loy + d, 10, 100); if (o.loy !== l0) rows.push([o.id, l0, o.loy, why]); }
  }
  var down = rows.filter(function (r) { return r[2] < r[1]; }).length;
  logMsg(old.n + ' ' + word + ' (향년 ' + age + '세) — ' + josa(h.n, '이가') + ' 뒤를 이었다' + (house ? '' : ' (한집안이 아니다)') + (down ? ' · 충성이 흔들린 무장 ' + down + '명' : ''), p.c, p.r, f, f === G.player ? 3 : 1);
  if (!G.aiOnly) ev({ t: 'news', f: f, c: p.c, r: p.r, warn: f === G.player ? 1 : 0, text: '<b>' + old.n + ' ' + word + '</b> (향년 ' + age + '세) — <b>' + josa(h.n, '이가') + '</b> 뒤를 이었습니다' + (down ? ' · 충성이 흔들린 무장 ' + down + '명' : '') });
  if (f === G.player) { G.succ = { turn: G.turn, old: old.id, heir: h.id, kin: kin, house: house, named: named, keep: keep, rows: rows }; corpsFix(); }      // 내 차례가 오면 화면이 알린다(ui_panels.js 의 succShow)
  return h;
}
function factionCollapse(f) {              // 뒤를 이을 사람이 없다: 거점은 주인 없는 땅이 되고 세력은 사라진다
  for (var i = 0; i < G.bases.length; i++) {
    var b = G.bases[i], j; if (b.owner !== f) continue;
    for (j = 0; j < b.plots.length; j++) { var uf = b.plots[j].fac; if (uf && !uf.done) { freeBuilders(uf, true); b.plots[j].fac = null; } }
    var held = b.captives.slice();
    for (j = 0; j < held.length; j++) { var cp = off(held[j]); if (cp && cp.capF === f) releaseCaptive(cp); }
    b.owner = -1; b.troops = 0; if (b.corps) b.corps = 0;
  }
  checkFaction(f);
}
"""
c = rep(c, "function serialize() { return JSON.stringify(G); }", LIFE_JS + "function serialize() { return JSON.stringify(G); }")

# 명부가 늘 때(옛 저장): 죽은 사람 · 재야 · 생몰년
c = rep(c, "f: -1, st: 'hidden', loc: loc, unit: null, loy: 100, merit: 0, acted: false, y: so.y || 0, j: so.j || null, capF: -1, dest: -1, eta: 0, pf: so.f, grown: 1 };\n    var F = so.f >= 0 ? g.factions[so.f] : null;\n    if (F && F.alive && SCENARIO.factions[so.f] && F.name === SCENARIO.factions[so.f].n) {",
        "f: -1, st: (so.st === 'dead' || so.st === 'free') ? so.st : 'hidden', loc: loc, unit: null, loy: 100, merit: 0, acted: false, y: so.y || 0, j: so.j || null, capF: -1, dest: -1, eta: 0, pf: so.f, grown: 1 };      // v0.23: 그 시대에 이미 죽은 사람 · 재야\n    lifeInit(o, so);\n    var F = so.f >= 0 ? g.factions[so.f] : null;\n    if (F && F.alive && SCENARIO.factions[so.f] && (F.n0 || F.name) === SCENARIO.factions[so.f].n) {")
c = rep(c, """function deserialize(s) {
  var g = JSON.parse(s);
  if (!g || g.ver !== 2) return false;
""", """function deserialize(s) {
  var g = JSON.parse(s);
  if (!g || g.ver !== 2) return false;
  if (!g.scen) g.scen = '194';                                           // v0.23: 시대(옛 저장은 모두 194년 군웅할거)
  scenarioUse(g.scen);
""")
c = rep(c, "if (sf && sf.n === g.factions[j].name) g.factions[j].color = sf.color; }", "if (sf && sf.n === (g.factions[j].n0 || g.factions[j].name)) g.factions[j].color = sf.color; }")
c = rep(c, """  var grown = rosterGrow(g);                                             // v0.17: 무장이 늘었다 — 옛 저장에 새 무장을 덧붙인다
""", """  var grown = rosterGrow(g);                                             // v0.17: 무장이 늘었다 — 옛 저장에 새 무장을 덧붙인다
  // v0.23: 집안 · 후계 · 수명(옛 저장에는 없다). 이미 수명이 지난 사람은 한꺼번에 떠나지 않도록 1 ~ LIFE.old 년에 걸쳐 흩는다
  for (var hf = 0; hf < g.factions.length; hf++) {
    var HF = g.factions[hf], hs = SCENARIO.factions[hf];
    if (HF.n0 === undefined) HF.n0 = HF.name;
    if (!HF.house) HF.house = (hs && hs.n === HF.n0 && hs.house) || houseName(HF.n0);
    if (!HF.past) HF.past = ((hs && hs.n === HF.n0 && hs.anc) || []).slice();
    if (HF.heir === undefined) HF.heir = -1;
  }
  var lifeNew = g.life === undefined;
  for (var li = 0; li < g.officers.length; li++) {
    var lo = g.officers[li], ls = SCENARIO.officers[li];
    if (!ls || ls.n !== lo.n) continue;
    if (lo.by === undefined) {
      lifeInit(lo, ls);
      if (lifeNew && lo.st !== 'dead' && lo.st !== 'hidden' && lo.dy <= g.year) { lo.dy = g.year + 1 + (strHash(lo.n) >>> 0) % LIFE.old; lo.late = 1; }
    }
  }
  if (lifeNew) g.life = 1;
""")
c = rep(c, "var gn = G.officers[gi]; delete gn.grown; if (gn.f >= 0) { gn.loy = loyNat(gn); if (gn.f === G.player) gj++; } }",
        "var gn = G.officers[gi]; delete gn.grown; if (gn.st !== 'dead') galive++; if (gn.f >= 0) { gn.loy = loyNat(gn); if (gn.f === G.player) gj++; } }")
c = rep(c, "    var gj = 0; for (var gi = G.officers.length - grown;", "    var gj = 0, galive = 0; for (var gi = G.officers.length - grown;")
c = rep(c, "logMsg('무장이 늘었습니다(v0.17) — 천하에 ' + grown + '명이 더해졌습니다'", "logMsg('무장이 늘었습니다 — 천하에 ' + galive + '명이 더해졌습니다'")
wr('src/core.js', c)
print('s1_core ok')
