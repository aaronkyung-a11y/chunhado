# v0.18 시설의 레벨 — 레벨이 쓰이지 않는 시설(공방 · 조폐 · 곡창)은 레벨이 없다
#   그동안: 이 셋도 'Lv1'로 적히고 흡수합병으로 레벨을 올릴 수 있었지만, 올려도 효과는 같았다(합치면 한 곳이 줄 뿐 — 창에 "레벨은 영향 없음"이라고 적어 두었다).
#   이제: 레벨을 적지 않고, 합칠 수도 없다(규칙: mergeCandidates 가 내놓지 않는다 → AI 도 합치지 않는다). 옛 저장에 Lv2 · Lv3 로 남은 것은 불러올 때 1로 되돌린다.
#   CH_ROOT=<폴더> 로 다른 나무에 입힐 수 있다(시험용).
import io, os
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)

# ───────────────────────── data.js ─────────────────────────
s = rd('src/data.js')
s = rep(s, "cost: 270, build: 500, desc: '충차 생산' },", "cost: 270, build: 500, desc: '충차 생산', noLv: true },      // noLv(v0.18): 레벨이 없는 시설 — 레벨이 효과에 쓰이지 않는다")
s = rep(s, "cost: 200, build: 400, desc: '인접한 시장의 수입 +50%' },", "cost: 200, build: 400, desc: '인접한 시장의 수입 +50%', noLv: true },")
s = rep(s, "cost: 200, build: 400, desc: '인접한 농장의 수입 +50%' }", "cost: 200, build: 400, desc: '인접한 농장의 수입 +50%', noLv: true }")
wr('src/data.js', s)

# ───────────────────────── core.js ─────────────────────────
s = rd('src/core.js')
s = rep(s, "function mergeCandidates(b, pi) {\n  var p = b.plots[pi], f = p.fac, out = [];\n  if (!f || !f.done || f.lv >= 3) return out;\n",
"""/* v0.18: 레벨이 있는 시설인가 — 공방 · 조폐 · 곡창은 레벨이 효과에 쓰이지 않으므로 레벨이 없다(적지 않고, 합치지도 못한다) */
function facHasLv(t) { return !(FAC[t] && FAC[t].noLv); }
function mergeCandidates(b, pi) {
  var p = b.plots[pi], f = p.fac, out = [];
  if (!f || !f.done || f.lv >= 3 || !facHasLv(f.t)) return out;
""")
# 옛 저장: 레벨이 없는 시설에 남은 Lv2 · Lv3 은 1로
s = rep(s, "  var grown = rosterGrow(g);                                             // v0.17: 무장이 늘었다 — 옛 저장에 새 무장을 덧붙인다\n",
"""  for (var fb = 0; fb < g.bases.length; fb++) (g.bases[fb].plots || []).forEach(function (pq) { if (pq.fac && !facHasLv(pq.fac.t) && pq.fac.lv !== 1) pq.fac.lv = 1; });      // v0.18: 레벨이 없는 시설(공방 · 조폐 · 곡창)
  var grown = rosterGrow(g);                                             // v0.17: 무장이 늘었다 — 옛 저장에 새 무장을 덧붙인다
""")
wr('src/core.js', s)

# ───────────────────────── ui3d.js: 지도의 시설 그림 크기 ─────────────────────────
s = rd('src/ui3d.js')
s = rep(s, "setSprite(fo.sp, sk || fc.t, FAC_W * (0.94 + 0.10 * (fc.lv - 1)));", "setSprite(fo.sp, sk || fc.t, FAC_W * (0.94 + 0.10 * ((facHasLv(fc.t) ? fc.lv : 1) - 1)));")
wr('src/ui3d.js', s)

# ───────────────────────── ui_panels.js ─────────────────────────
s = rd('src/ui_panels.js')
s = rep(s, "function lvTail(lv, f) {", "function facLv(fc) { return facHasLv(fc.t) ? ' Lv' + fc.lv : ''; }                               // v0.18: 레벨이 없는 시설(공방 · 조폐 · 곡창)에는 적지 않는다\nfunction lvTail(lv, f) {")
s = rep(s, "  if (t === 'workshop') return '충차 생산 · 레벨은 영향 없음';\n  if (t === 'mint') return '옆 시장의 수입 +50% · 레벨은 영향 없음';\n  if (t === 'granary') return '옆 농장의 수입 +50% · 레벨은 영향 없음';\n",
           "  if (t === 'workshop') return '충차 생산';\n  if (t === 'mint') return '옆 시장의 수입 +50%';\n  if (t === 'granary') return '옆 농장의 수입 +50%';\n")
# 시설 창의 둘째 줄: 공방이 둘이면 하나는 쓸모가 없다
s = rep(s, "  if (t === 'barracks' || t === 'smithy' || t === 'stable') {\n    var best = 0, what = t === 'barracks' ? '징병량' : '생산량';",
           "  if (t === 'workshop') { for (i = 0; i < b.plots.length; i++) { var g0 = b.plots[i].fac; if (i !== pi && g0 && g0.done && g0.t === t) return '이 도시에 공방이 또 있습니다 — <b>하나면 충분합니다</b>'; } return ''; }\n"
           "  if (t === 'barracks' || t === 'smithy' || t === 'stable') {\n    var best = 0, what = t === 'barracks' ? '징병량' : '생산량';")
# 새로 지을 때의 카드
s = rep(s, "  if (lv < 3 && adjFacCount(b, pi, t)) return ['옆 ' + FAC[t].name + '과 합병 가능', 'ok'];", "  if (facHasLv(t) && lv < 3 && adjFacCount(b, pi, t)) return ['옆 ' + FAC[t].name + '과 합병 가능', 'ok'];")
s = rep(s, "  return ['이미 있음 (Lv' + lv + ')', 'warn'];", "  return ['이미 있음' + (facHasLv(t) ? ' (Lv' + lv + ')' : ''), 'warn'];")
# 시설 줄 · 시설 창
s = rep(s, "lotChip(b, i) + FAC[fc.t].name + ' Lv' + fc.lv + '</span>", "lotChip(b, i) + FAC[fc.t].name + facLv(fc) + '</span>")
s = rep(s, "var h = dlgHead(b.n + ' ' + lotMark(lotNo(b, pi)) + ' ' + F.name + ' Lv' + fc.lv) + ", "var h = dlgHead(b.n + ' ' + lotMark(lotNo(b, pi)) + ' ' + F.name + facLv(fc)) + ")
s = rep(s, "        '<div class=\"cmds\"><button class=\"cmd' + (cands.length ? ' pri' : ' off') + '\" type=\"button\" data-a=\"merge\"><b>흡수합병</b><small>' + (fc.lv >= 3 ? '최고 레벨' : (cands.length ? '금 ' + COST.merge * fc.lv + ' · 행 ' + AP.merge : '인접한 같은 시설 필요')) + '</small></button>' +\n",
           "        '<div class=\"cmds\">' + (facHasLv(fc.t) ? '<button class=\"cmd' + (cands.length ? ' pri' : ' off') + '\" type=\"button\" data-a=\"merge\"><b>흡수합병</b><small>' + (fc.lv >= 3 ? '최고 레벨' : (cands.length ? '금 ' + COST.merge * fc.lv + ' · 행 ' + AP.merge : '인접한 같은 시설 필요')) + '</small></button>' : '') +      // v0.18: 레벨이 없는 시설에는 합병 단추가 없다\n")
s = rep(s, "        '<p class=\"note\">흡수합병 = 옆의 같은 시설을 합쳐 레벨 +1 (최대 3)' + (cands.length ? ' — ' + mergeNote(b, pi, cands[0]) : '') + ({ mint: 1, granary: 1, workshop: 1 }[fc.t] ? '<br><b class=\"bad\">' + josa(F.name, '은는') + ' 레벨을 올려도 효과가 같습니다</b> — 합치면 한 곳이 줄 뿐입니다' : '') + '</p></div>';",
           "        (facHasLv(fc.t) ? '<p class=\"note\">흡수합병 = 옆의 같은 시설을 합쳐 레벨 +1 (최대 3)' + (cands.length ? ' — ' + mergeNote(b, pi, cands[0]) : '') + '</p>'\n"
           "          : '<p class=\"note nolv\"><b>' + josa(F.name, '은는') + ' 레벨이 없는 시설입니다</b> — ' + (fc.t === 'workshop' ? '하나만 있으면 충차를 만들 수 있습니다.' : '옆의 ' + (fc.t === 'mint' ? '시장' : '농장') + ' 한 곳에 둘까지, 하나마다 수입을 +50% 보탭니다.') + '</p>') + '</div>';")
# 도움말
s = rep(s, "조폐·곡창·공방은 레벨을 올려도 효과가 같습니다.", "<b>조폐·곡창·공방은 레벨이 없습니다</b>(레벨이 효과에 쓰이지 않아 적지 않고, 합칠 수도 없습니다).")
wr('src/ui_panels.js', s)
print('p5_fac18: ok')
