# v0.12 (2/…): 시설이 길을 막지 않는다  (core.js · ui_panels.js · ui3d.js)
#  요청 "시장 같은 건물들이 전투에 너무 크게 방해가 된다."
#   v0.11 까지: 시설이 선 칸은 누구도 들어갈 수 없었다(내 시설도). 도시 둘레 여섯 칸 가운데 보통 세 칸이 부지라(42곳 가운데 31곳),
#   시설을 지을수록 성 밖으로 나갈 자리 · 성을 칠 자리 · 지나갈 길이 줄었다.
#   - 시설 칸은 여느 땅처럼 지나가고 설 수 있다(내 시설 · 남의 시설 모두). 이동력은 그 칸의 지형대로.
#   - 출진할 때 나갈 자리: 시설 칸도 쓰되 빈 땅을 먼저 고른다. 밀려나는 부대(돌출 · 돌격)도 시설 칸으로 밀려날 수 있다.
#   - 시설은 여전히 옆 칸에서 칠 수 있고, 시설 위에 올라선 부대는 발밑의 시설도 칠 수 있다(부대 창의 [시설 파괴]).
#   - 그림: 부대가 올라선 시설은 흐리게(부대가 가려지지 않게).
#   - 그대로: 부대가 있는 칸에는 새로 짓지 못한다. 불은 시설을 태운다. AI 의 시설 공격(가끔)도 그대로.
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)

# ---------------------------------------------------------------- core.js
p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()
# 한 턴 이동 범위
s = rep(s, "      var pf = PAT[nk];\n      if (pf && G.bases[pf.b].plots[pf.i].fac) continue;               // 시설\n", "")
# 먼 길 찾기(AI · 행군)
s = rep(s, "      var pf = PAT[nk];\n      if (pf && G.bases[pf.b].plots[pf.i].fac) continue;\n      var ou = UAT[nk];\n      if (ou) mc += (ou.f === u.f ? 3 : 25);",
           "      var ou = UAT[nk];\n      if (ou) mc += (ou.f === u.f ? 3 : 25);")
# 출진할 자리: 시설 칸도 되지만 빈 땅이 먼저(v0.12)
s = rep(s, "    var pf = PAT[k]; if (pf && G.bases[pf.b].plots[pf.i].fac) continue;\n"
           "    var s = (t === 'w' ? 10 : 0) + (isRoad(c, r) ? 0 : 2) + (G.fires[k] ? 20 : 0);\n"
           "    if (toward) s = hdist(c, r, toward.c, toward.r) + (t === 'w' ? 3 : 0) + (G.fires[k] ? 20 : 0);",
           "    var pf = PAT[k], onFac = pf && G.bases[pf.b].plots[pf.i].fac ? 1 : 0;                      // v0.12: 시설 칸으로도 나갈 수 있다(빈 땅이 먼저)\n"
           "    var s = (t === 'w' ? 10 : 0) + (isRoad(c, r) ? 0 : 2) + (G.fires[k] ? 20 : 0) + onFac * 4;\n"
           "    if (toward) s = hdist(c, r, toward.c, toward.r) + (t === 'w' ? 3 : 0) + (G.fires[k] ? 20 : 0) + onFac * 0.5;")
# 밀려날 자리
s = rep(s, "  if (UAT[k] || BAT[k] !== undefined) return false;\n  var pf = PAT[k]; if (pf && G.bases[pf.b].plots[pf.i].fac) return false;\n  return true;",
           "  if (UAT[k] || BAT[k] !== undefined) return false;\n  return true;                                                     // v0.12: 시설 칸으로도 밀려난다")
# 칠 수 있는 것: 발밑의 남의 시설
s = rep(s, "    if (pf) { var pb = G.bases[pf.b], fc = pb.plots[pf.i].fac; if (fc && pb.owner >= 0 && pb.owner !== u.f && d === 1 && !justOut(u)) out.push({ kind: 'fac', b: pb, i: pf.i, c: c, r: r, d: d }); }\n  }\n  return out;",
           "    if (pf) { var pb = G.bases[pf.b], fc = pb.plots[pf.i].fac; if (fc && pb.owner >= 0 && pb.owner !== u.f && d === 1 && !justOut(u)) out.push({ kind: 'fac', b: pb, i: pf.i, c: c, r: r, d: d }); }\n  }\n"
           "  var uf = facUnder(u); if (uf && !justOut(u)) out.push(uf);            // v0.12: 올라선 시설\n  return out;")
s = rep(s, "function critNormal(a, d) {",
           "/* 부대가 올라서 있는 남의 시설(없으면 null) — v0.12 부터 시설 칸에 설 수 있다 */\n"
           "function facUnder(u) {\n"
           "  var pf = PAT[K(u.c, u.r)]; if (!pf) return null;\n"
           "  var pb = G.bases[pf.b]; if (!pb.plots[pf.i].fac || pb.owner < 0 || pb.owner === u.f) return null;\n"
           "  return { kind: 'fac', b: pb, i: pf.i, c: u.c, r: u.r, d: 0 };\n"
           "}\n"
           "function critNormal(a, d) {")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- ui_panels.js
p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()
# 행군 목적지로 시설 칸도 고를 수 있다
s = rep(s, "if (UI.pickMarch && !u && MC[clsIdx(su)][k] < 99 && !(pl && pl.plot.fac)) { proposeMarch(su, c, r); return; }",
           "if (UI.pickMarch && !u && MC[clsIdx(su)][k] < 99) { proposeMarch(su, c, r); return; }")
# 부대 창: 남의 시설 위에 서 있으면 [시설 파괴]
s = rep(s, "      untarget: function () { UI.target = null; refreshSheet(); requestDraw(); },",
           "      untarget: function () { UI.target = null; refreshSheet(); requestDraw(); },\n"
           "      facunder: function () { var x = selUnit(), t = x ? facUnder(x) : null; if (!t) return; UI.target = t; UI.march = null; UI.pickMarch = false; refreshSheet(); requestDraw(); },")
s = rep(s, "          h += '<div class=\"acts\"><button class=\"act\" type=\"button\" data-a=\"wait\"><b>대기</b></button>' +\n",
           "          var fu = facUnder(x);\n"
           "          h += '<div class=\"acts\">' + (fu ? '<button class=\"act' + (justOut(x) ? ' off' : ' pri') + '\" type=\"button\" data-a=\"facunder\"><b>시설 파괴</b><small>' + (justOut(x) ? '다음 턴부터' : '발밑의 ' + FAC[fu.b.plots[fu.i].fac.t].name) + '</small></button>' : '') +\n"
           "            '<button class=\"act\" type=\"button\" data-a=\"wait\"><b>대기</b></button>' +\n")
# 남의 시설 칸을 눌렀을 때: 칠 수 없으면 그리로 가고, 칠 수 있으면 대상 창에 [이 칸으로 이동]도 낸다
s = rep(s, "      if (!any) {\n        if ((t.kind === 'base' || t.kind === 'fac') && justOut(su)",
           "      if (!any) {\n        if (t.kind === 'fac' && UI.rc && UI.rc.stop[k]) { UI.march = null; doMove(su, c, r); return; }\n        if ((t.kind === 'base' || t.kind === 'fac') && justOut(su)")
s = rep(s, "          h += '<button class=\"act\" type=\"button\" data-a=\"untarget\"><b>대상 취소</b></button></div>';",
           "          if (t.kind === 'fac' && UI.rc && UI.rc.stop[K(t.c, t.r)]) h += '<button class=\"act\" type=\"button\" data-a=\"moveon\"><b>이 칸으로 이동</b></button>';\n"
           "          h += '<button class=\"act\" type=\"button\" data-a=\"untarget\"><b>대상 취소</b></button></div>';")
s = rep(s, "      facunder: function () {",
           "      moveon: function () { var x = selUnit(), t = UI.target; if (!x || !t || !UI.rc || !UI.rc.stop[K(t.c, t.r)]) return; UI.target = null; UI.march = null; doMove(x, t.c, t.r); },\n"
           "      facunder: function () {")
# 도움말
s = rep(s, "<li>거점은 병력이나 내구가 0이 되면 함락됩니다.</li>",
           "<li>거점은 병력이나 내구가 0이 되면 함락됩니다.</li><li>시설이 선 칸도 지나가고 설 수 있습니다. 남의 시설은 옆 칸이나 그 위에서 부술 수 있습니다.</li>")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- ui3d.js
p = 'src/ui3d.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "fs = fc.t + fc.lv + (fc.done ? 'd' : 'c' + sk);",
           "onU = UAT[K(pl.c, pl.r)] ? 1 : 0, fs = fc.t + fc.lv + (fc.done ? 'd' : 'c' + sk) + (onU ? 'u' : '');")
s = rep(s, "fo.sp.material.opacity = (fc.done || sk) ? 1 : 0.5; }",
           "fo.sp.material.opacity = ((fc.done || sk) ? 1 : 0.5) * (onU ? 0.38 : 1); }      // v0.12: 부대가 올라선 시설은 흐리게")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
