# v0.9.1 옛 저장: 0.8.1~0.9 에서 시작한 판에는 옛 기간으로 셈한 보호의 끝(G.peace.until)이 저장되어 있다.
#  새 기간으로 당기되, 그러면 이미 지났거나 30일 안에 끝나게 되는 판은 '불러온 날부터 30일'은 남긴다(갑자기 사라지지 않게). 당겼다는 것은 기록에 한 줄 남긴다.
#  G.peace.v = 2: 새 기간으로 셈한 판(새 판은 처음부터 붙는다) — 한 번만 당기기 위한 표시.
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)
p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "  G.peace = { until: 1 + peaceTurns(G.player), broken: {} };      // 초반 보호: until 턴부터 AI 가 플레이어의 거점을 칠 수 있다",
           "  G.peace = { until: 1 + peaceTurns(G.player), broken: {}, v: 2 };      // 초반 보호: until 턴부터 AI 가 플레이어의 거점을 칠 수 있다. v = 기간 표의 판(2 = v0.9.1 의 18/12/9턴)")
s = rep(s, """  if (!g.peace && SCENARIO.factions[g.player]) g.peace = { until: 1 + peaceFor(startTroops(g.player)), broken: {} };
""", """  if (!g.peace && SCENARIO.factions[g.player]) g.peace = { until: 1 + peaceFor(startTroops(g.player)), broken: {}, v: 2 };
  // v0.9.1: 보호 기간이 짧아졌다(36/24/12턴 → 18/12/9턴). 0.8.1~0.9 에서 시작한 판은 옛 끝이 저장되어 있다 — 새 기간으로 당기되, 불러온 때부터 적어도 30일은 남긴다
  var peaceCut = 0;
  if (g.peace && !g.peace.v) {
    var nu = SCENARIO.factions[g.player] ? 1 + peaceFor(startTroops(g.player)) : g.peace.until;
    if (nu < g.peace.until && g.turn < g.peace.until) { peaceCut = g.peace.until; g.peace.until = Math.max(nu, Math.min(g.peace.until, g.turn + 3)); if (g.peace.until === peaceCut) peaceCut = 0; }
    g.peace.v = 2;
  }
""")
s = rep(s, """  G = g; reindex(); REPORT = []; EVQ = [];
""", """  G = g; reindex(); REPORT = []; EVQ = [];
  if (peaceCut) { var pcap = facCities(G.player)[0] || facBases(G.player)[0]; if (pcap) logMsg('초반 보호 기간이 짧아졌습니다(v0.9.1) — 이 판의 보호는 ' + dateOfTurn(G.peace.until - 1) + '까지입니다(전에는 ' + dateOfTurn(peaceCut - 1) + '까지)', pcap.c, pcap.r, G.player, 2); REPORT = []; }
""")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
