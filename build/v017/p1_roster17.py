# v0.17 — 무장 추가(301 → 425명): 옛 저장에 새 무장을 덧붙이는 일 · 인연 · 여성의 목소리 · 도움말
#   명부 자체(src/roster.js)와 초상(src/assets.js)은 패치가 아니라 도구로 다시 만든다 — build/v017/apply.sh 머리의 풀이를 볼 것.
#   CH_ROOT=<폴더> 로 다른 나무에 입힐 수 있다(시험용).
import io, os
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)

# ── data.js: 판 번호 · 인연 ──
d = rd('src/data.js')
d = rep(d, "var GAME_VERSION = 'v0.16';", "var GAME_VERSION = 'v0.17';")
d = rep(d, "'조창': '혈연', '전위': '심복', '허저': '심복' },", "'조창': '혈연', '전위': '심복', '허저': '심복',\n            '변씨': '부부', '조절': '혈연', '조식': '혈연', '조휴': '혈연', '조진': '혈연', '하후상': '혈연', '하후패': '혈연', '하후무': '혈연', '하후덕': '혈연' },      // v0.17")
d = rep(d, "'여포': { '초선': '부부', '여령기': '혈연',", "'여포': { '초선': '부부', '엄씨': '부부', '여령기': '혈연',")
d = rep(d, "'관흥': '심복', '장포': '심복' },", "'관흥': '심복', '장포': '심복', '감부인': '부부', '미부인': '부부', '관색': '심복', '관은병': '심복' },")
d = rep(d, "'안량': '심복', '문추': '심복', '심배': '심복' },", "'안량': '심복', '문추': '심복', '심배': '심복', '유씨': '부부' },")
d = rep(d, "'원술': { '원윤': '혈연', '기령': '심복' },", "'원술': { '원윤': '혈연', '기령': '심복', '풍씨': '부부', '원씨': '혈연' },")
d = rep(d, "'한당': '심복', '주치': '심복' },", "'한당': '심복', '주치': '심복',\n            '오국태': '혈연', '손상향': '혈연', '손익': '혈연', '손교': '혈연', '손환': '혈연', '손노반': '혈연', '서곤': '인척', '소교': '인척' },      // v0.17")
d = rep(d, "'유표': { '채모': '인척', '유반': '혈연', '황조': '심복' },", "'유표': { '채모': '인척', '유반': '혈연', '황조': '심복', '채부인': '부부' },")
d = rep(d, "'방덕': '심복', '한수': '의형제' },", "'방덕': '심복', '한수': '의형제', '마운록': '혈연' },")
d = rep(d, "'장로': { '장위': '혈연' },", "'장로': { '장위': '혈연', '노씨': '혈연', '장기영': '혈연' },\n  '왕랑': { '왕숙': '혈연' },")
d = rep(d, "'유장': { '황권': '심복', '장임': '심복', '엄안': '심복', '왕루': '심복' }", "'유장': { '황권': '심복', '장임': '심복', '엄안': '심복', '왕루': '심복', '오씨': '인척' }")
wr('src/data.js', d)

# ── core.js: 옛 저장에 새 무장을 덧붙인다 ──
c = rd('src/core.js')
c = rep(c, "function serialize() { return JSON.stringify(G); }\n",
"""function serialize() { return JSON.stringify(G); }
/* v0.17: 무장이 늘었다. 옛 저장에는 앞쪽 사람들만 있으므로(번호는 그대로다) 명부의 뒤쪽을 덧붙인다 → 더한 수.
   · 194년에 세력에 있던 사람: 그 세력이 살아 있으면 그 세력에(본래의 도시를 아직 쥐고 있으면 거기, 아니면 군주가 있는 거점 · 그 세력의 첫 거점). 망했으면 그 도시의 재야로.
   · 재야 · 뒷날 나오는 사람: 새 판과 똑같이 숨은 채로(등장 연도가 되면 탐색으로 찾거나, 정해진 군주에게 간다). */
function rosterGrow(g) {
  var n0 = g.officers.length, i, n = 0;
  if (n0 >= SCENARIO.officers.length) return 0;
  for (i = 0; i < n0; i++) if (!SCENARIO.officers[i] || SCENARIO.officers[i].n !== g.officers[i].n) return 0;       // 다른 명부로 만든 저장이면 건드리지 않는다
  for (i = n0; i < SCENARIO.officers.length; i++) {
    var so = SCENARIO.officers[i], loc = baseByName(so.c), b = g.bases[loc];
    var o = { id: i, n: so.n, ldr: so.ldr, war: so.war, int: so.int, pol: so.pol, cha: so.cha, apt: so.apt, sk: so.sk || '', por: so.por,
      f: -1, st: 'hidden', loc: loc, unit: null, loy: 100, merit: 0, acted: false, y: so.y || 0, j: so.j || null, capF: -1, dest: -1, eta: 0, pf: so.f, grown: 1 };
    var F = so.f >= 0 ? g.factions[so.f] : null;
    if (F && F.alive && SCENARIO.factions[so.f] && F.name === SCENARIO.factions[so.f].n) {
      var home = (b && b.owner === so.f) ? b : null, L = g.officers[F.lord], k;
      if (!home && L && L.unit === null && g.bases[L.loc] && g.bases[L.loc].owner === so.f) home = g.bases[L.loc];
      if (!home) for (k = 0; k < g.bases.length && !home; k++) if (g.bases[k].owner === so.f && g.bases[k].kind === 'city') home = g.bases[k];
      if (!home) for (k = 0; k < g.bases.length && !home; k++) if (g.bases[k].owner === so.f) home = g.bases[k];
      if (home) { o.f = so.f; o.st = 'active'; o.loc = home.id; o.merit = Math.max(0, (o.ldr + o.war - 120) * 20); }
    }
    g.officers.push(o); n++;
  }
  return n;
}
""")
c = rep(c, "  G = g; reindex(); REPORT = []; EVQ = []; JOT = null;\n",
           "  var grown = rosterGrow(g);                                             // v0.17: 무장이 늘었다 — 옛 저장에 새 무장을 덧붙인다\n"
           "  G = g; reindex(); REPORT = []; EVQ = []; JOT = null;\n"
           "  if (grown) {\n"
           "    var gj = 0; for (var gi = G.officers.length - grown; gi < G.officers.length; gi++) { var gn = G.officers[gi]; delete gn.grown; if (gn.f >= 0) { gn.loy = loyNat(gn); if (gn.f === G.player) gj++; } }\n"
           "    var gcap = facCities(G.player)[0] || facBases(G.player)[0];\n"
           "    logMsg('무장이 늘었습니다(v0.17) — 천하에 ' + grown + '명이 더해졌습니다' + (gj ? ' · 우리 세력에 ' + gj + '명' : ''), gcap ? gcap.c : undefined, gcap ? gcap.r : undefined, G.player, 1);\n"
           "  }\n")
wr('src/core.js', c)

# ── voice.js: 여성의 목소리는 명부의 여성 표를 따른다 ──
v = rd('src/voice.js')
v = rep(v, "  if (VOICE_LADY[o.n] || /^gf\\d/.test(o.por || '')) return 'lady';",
           "  if (VOICE_LADY[o.n] || VOICE_WOMEN[o.n] || /^gf\\d/.test(o.por || '')) return 'lady';")
v = rep(v, "var VOICE_LADY = {", "var VOICE_WOMEN = (function () { var m = {}, L = (typeof SCENARIO !== 'undefined' && SCENARIO.women) || []; for (var i = 0; i < L.length; i++) m[L[i]] = 1; return m; })();      // v0.17: 명부(roster.js)의 여성 표\nvar VOICE_LADY = {")
wr('src/voice.js', v)

# ── 도움말 ──
s = rd('src/ui_panels.js')
s = rep(s, "'<h3>충성과 인연</h3>", "'<h3>무장 명부</h3><p>무장은 모두 ' + SCENARIO.officers.length + '명입니다(v0.17에서 124명이 늘었습니다 — 여성 ' + SCENARIO.women.length + '명). 194년에 이미 세력에 있는 사람 말고는 <b>등장 연도</b>가 되어야 나옵니다: 재야의 사람은 그 도시에서 <b>탐색</b>으로 찾고, 군주의 집안사람은 해가 바뀔 때 스스로 찾아옵니다. 예전 판의 저장을 불러오면 새 무장이 그 판에 덧붙습니다 — 세력에 있던 사람은 그 세력이 살아 있으면 그 세력으로, 망했으면 그 도시의 재야로 갑니다.</p>' +\n  '<h3>충성과 인연</h3>")
wr('src/ui_panels.js', s)
print('ok p1_roster17')
