# v0.8 건설 부지 늘리기 — 규칙 쪽: 옛 저장을 열면 모자란 부지를 채운다(부지 자료는 tools/add_plots.py 가 src/mapdata.js 에 덧붙였다)
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:100])
    return s.replace(a, b)
p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, """  G = g; reindex(); REPORT = []; EVQ = [];
  return true;
}""", """  // v0.8: 부지가 늘었다(6·8·10 → 10·13·16). 옛 저장에는 앞쪽 부지만 있으므로 뒤에 덧붙인다(앞쪽은 자리·순서가 그대로다)
  for (var bi = 0; bi < g.bases.length; bi++) {
    var gb = g.bases[bi], mb = MAPDATA.bases[bi], pl = (mb && mb.n === gb.n && MAPDATA.plots[gb.n]) || [];
    if (!gb.plots) gb.plots = [];
    for (var pj = gb.plots.length; pj < pl.length; pj++) gb.plots.push({ c: pl[pj][0], r: pl[pj][1], fac: null });
  }
  G = g; reindex(); REPORT = []; EVQ = [];
  return true;
}""")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
