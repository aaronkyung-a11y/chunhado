# v0.9 화면 손질: 군사의 조언을 찾아다니지 않아도 보이게
#  ① 등용 목록의 줄마다 '가장 잘하는 무장을 보냈을 때'의 조언(○·×)을 성공률 앞에
#  ② 지금 할 일: 군사가 "응할 것"이라고 보는 이웃 무장이 있으면 거점마다 한 줄(누르면 그 거점의 등용 창)
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:100])
    return s.replace(a, b)
p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "function advTag(o) {", """/* 거점 b 에서 대상 t 에게 가장 잘 권하는 쉬는 무장과 그때의 성공률·조언 { o, p, adv } (쉬는 무장이 없으면 o = null) */
function bestRecruiter(b, t) {
  var bo = null, bp = -1; idleOfficers(b).forEach(function (o) { var q = recruitChance(b, o, t); if (q > bp) { bp = q; bo = o; } });
  return { o: bo, p: Math.max(0, bp), adv: bo ? recruitAdvice(b, bo, t) : null };
}
/* 군사가 "응할 것"이라고 보는 이웃 무장(가장 잘하는 무장을 보냈을 때) */
function poachHints(b) {
  var out = [];
  if (!idleOfficers(b).length) return out;
  poachTargets(b).forEach(function (t) { if (askWait(t)) return; var x = bestRecruiter(b, t); if (x.p > 0 && x.adv && x.adv.says) out.push({ t: t, p: x.p, adv: x.adv }); });
  return out.sort(function (x, y) { return y.p - x.p; });
}
function advTag(o) {""")
s = rep(s, "  function bestP(t) { var m = 0; idleOfficers(b).forEach(function (o) { m = Math.max(m, recruitChance(b, o, t)); }); return m; }\n  function why(t) {",
           "  function bestP(t) { return bestRecruiter(b, t).p; }\n  function bestM(t) { return advMark(bestRecruiter(b, t).adv); }\n  function why(t) {")
s = rep(s, "rt: w ? '<span class=\"bad\">' + w + '</span>' : (idle ? '최고 <b>' + bestP(t) + '%</b>' : '') }); }\n        h += '</div>';\n      }",
           "rt: w ? '<span class=\"bad\">' + w + '</span>' : (idle ? bestM(t) + '최고 <b>' + bestP(t) + '%</b>' : '') }); }\n        h += '</div>';\n      }")
s = rep(s, "(w ? '<span class=\"bad\">' + w + '</span>' : (idle ? '최고 <b>' + L[i].p + '%</b>' : '')) }); }",
           "(w ? '<span class=\"bad\">' + w + '</span>' : (idle ? (L[i].p ? bestM(t) : '') + '최고 <b>' + L[i].p + '%</b>' : '')) }); }")
s = rep(s, """  if (!peaceLeft()) bs.forEach(function (b) {                  // 이웃 세력이 데려갈 수 있는 무장""", """  if (F.ap >= AP.recruit) bs.forEach(function (b) {            // 군사가 '응할 것'이라고 보는 이웃 무장
    var hs = poachHints(b); if (!hs.length) return;
    out.push({ cls: 'cool advh', ic: '招', t: b.n + ' — 등용에 응할 듯한 이웃 무장 ' + hs.length + '명', s: hs.slice(0, 3).map(function (x) { return facName(x.t.f) + ' ' + x.t.n + '(' + x.p + '%)'; }).join(' · ') + ' — 군사 ' + hs[0].adv.adv.n + '의 조언', go: ['recruit', b.id], lb: '등용', info: 1 });
  });
  if (!peaceLeft()) bs.forEach(function (b) {                  // 이웃 세력이 데려갈 수 있는 무장""")
s = rep(s, "  else if (g[0] === 'peace') showPeaceInfo();", "  else if (g[0] === 'peace') showPeaceInfo();\n  else if (g[0] === 'recruit') { gotoBase(G.bases[g[1]], 'men'); flowRecruit(G.bases[g[1]]); }")
io.open(p, 'w', encoding='utf-8').write(s)
p = 'src/style.css'; s = io.open(p, encoding='utf-8').read()
s += """.todo.advh .n { border-color: var(--indigo); color: var(--indigo); font-family: var(--font-display); }
.todo.advh b { color: var(--indigo); }
"""
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')

# (바로잡음) 줄의 클래스 이름을 adv → advh 로: .adv 는 조언의 ○·× 표시에 쓰는 이름이라 줄 전체가 굵어졌다
