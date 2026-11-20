# v0.8.1 초반 보호 — 0.8까지의 저장
#  저장본에 G.peace 가 없으면 그 세력의 시작 병력으로 기간을 정해 붙인다. 아직 그 기간 안이면 이어 하는 판도 보호받는다.
#  누구를 먼저 쳤는지는 옛 저장에서 알 수 없으므로 비워 둔다(= 모두와 보호 상태로 본다).
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:100])
    return s.replace(a, b)
p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "  G = g; reindex(); REPORT = []; EVQ = [];\n  for (var oi = 0;",
"""  // v0.8.1: 초반 보호. 0.8까지의 저장에는 없다 — 그 세력의 시작 병력으로 기간을 정해 붙인다(아직 그 기간 안이면 보호받는다. 누구를 먼저 쳤는지는 알 수 없어 비워 둔다)
  if (!g.peace && SCENARIO.factions[g.player]) g.peace = { until: 1 + peaceFor(startTroops(g.player)), broken: {} };
  G = g; reindex(); REPORT = []; EVQ = [];
  for (var oi = 0;""")
io.open(p, 'w', encoding='utf-8').write(s)
p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "<li>0.8까지의 저장을 이어 하는 판에는 보호가 없습니다.</li>", "<li>0.8에서 하던 판을 이어 해도, 아직 그 기간 안이면 보호받습니다.</li>")
io.open(p, 'w', encoding='utf-8').write(s)
p = 'tools/pack_sources.py'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "build/v081/p7_touchup.py\n", "build/v081/p7_touchup.py build/v081/p8_migrate.py\n")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
