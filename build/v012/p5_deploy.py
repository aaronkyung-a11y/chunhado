# v0.12 (5/…): 나갈 자리를 고른다  (core.js · ui_panels.js · style.css)
#  요청(15:30) "그리고 성에서 부대가 나올 때 내가 원하는 방향으로 나오게 해줘야지"
#   v0.11 까지: 나갈 칸은 게임이 골랐다(길 → 평지 → 강 순, AI 는 가는 쪽으로). 고를 수 없었다.
#   - 출진 · 수송 창에 '나갈 자리': 성 둘레 여섯 칸을 지도와 같은 방향으로 그린 작은 그림. 칸을 누르면 그 칸으로 나간다.
#       칸마다 무엇이 있는지 적는다(길 · 평지 · 숲 · 강 · 시설 이름). 나갈 수 없는 칸(산 · 바다 · 부대가 선 칸)은 흐리게.
#       고르지 않으면 전과 같이 게임이 고른다 — 그 칸은 점선으로 보인다. [자동]으로 되돌린다.
#   - 규칙: cmdDeploy 의 spec.at = [c, r]. 둘레의 나갈 수 있는 칸이 아니면 출진하지 않고 까닭을 돌려준다. AI 는 전과 같다(spec.toward).
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)

p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "/* spec: { type, ids, troops, food, gold, cargo, toward } */\nfunction cmdDeploy(b, spec) {",
           "/* 성 밖으로 나갈 수 있는 칸들(둘레 여섯 칸 가운데 산 · 바다 · 부대가 선 칸을 뺀 것). v0.12: 출진할 때 이 가운데서 고를 수 있다 */\n"
           "function deploySpots(b) {\n"
           "  var ns = nbrs(b.c, b.r), out = [];\n"
           "  for (var i = 0; i < ns.length; i++) {\n"
           "    var c = ns[i][0], r = ns[i][1], k = K(c, r), t = terr(c, r);\n"
           "    if (t === 'm' || t === 's' || t === 'x' || UAT[k] || BAT[k] !== undefined) continue;\n"
           "    out.push([c, r]);\n"
           "  }\n"
           "  return out;\n"
           "}\n"
           "/* spec: { type, ids, troops, food, gold, cargo, toward, at }   at = [c, r] 나갈 칸을 직접 고른 것(v0.12) */\nfunction cmdDeploy(b, spec) {")
s = rep(s, "  var spot = deploySpot(b, spec.toward);\n  if (!spot) return ERR('성 밖에 나갈 자리가 없습니다');",
           "  var spot = null;\n"
           "  if (spec.at) {\n"
           "    var sps = deploySpots(b);\n"
           "    for (var si = 0; si < sps.length; si++) if (sps[si][0] === spec.at[0] && sps[si][1] === spec.at[1]) spot = sps[si];\n"
           "    if (!spot) return ERR('그 칸으로는 나갈 수 없습니다');\n"
           "  } else spot = deploySpot(b, spec.toward);\n"
           "  if (!spot) return ERR('성 밖에 나갈 자리가 없습니다');")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "function flowDeploy(b) {\n",
           "/* 나갈 자리(v0.12): 성 둘레 여섯 칸을 지도와 같은 방향으로 그린다. st.at = 고른 칸 [c, r] 또는 null(게임이 고른다 — 그 칸은 점선) */\n"
           "function dirName(dx, dz) { var a = Math.atan2(dz, dx) * 180 / Math.PI; return Math.abs(a) < 15 ? '동' : (Math.abs(a) > 165 ? '서' : (a < 0 ? (a > -90 ? '북동' : '북서') : (a < 90 ? '남동' : '남서'))); }\n"
           "function spotWhat(c, r) {\n"
           "  var k = K(c, r), t = terr(c, r), pf = PAT[k], fc = pf ? G.bases[pf.b].plots[pf.i].fac : null;\n"
           "  if (UAT[k]) return '부대';\n"
           "  if (fc) return FAC[fc.t].name;\n"
           "  if (G.fires[k]) return '불';\n"
           "  return isRoad(c, r) ? (t === 'w' ? '나루' : '길') : TERRAIN_NAME[t];\n"
           "}\n"
           "function deployRing(b, st) {\n"
           "  var ns = nbrs(b.c, b.r), p0 = hexCenter(b.c, b.r), okK = {}, auto = deploySpot(b), R = 29, D = R * Math.sqrt(3), cx = 92, cy = 84, h = '', i, sel = null;\n"
           "  deploySpots(b).forEach(function (q) { okK[K(q[0], q[1])] = 1; });\n"
           "  if (st.at && !okK[K(st.at[0], st.at[1])]) st.at = null;                // 고른 칸이 막혔으면(다른 부대가 섰으면) 자동으로 되돌린다\n"
           "  function hex(x, y, cls, attr) { var pts = ''; for (var a = 0; a < 6; a++) { var th = Math.PI / 180 * (60 * a - 30); pts += (x + R * 0.96 * Math.cos(th)).toFixed(1) + ',' + (y + R * 0.96 * Math.sin(th)).toFixed(1) + ' '; } return '<polygon class=\"' + cls + '\" points=\"' + pts + '\"' + (attr || '') + '/>'; }\n"
           "  h += hex(cx, cy, 'c') + '<text class=\"cn\" x=\"' + cx + '\" y=\"' + (cy + 4.5) + '\">' + b.n + '</text>';\n"
           "  for (i = 0; i < ns.length; i++) {\n"
           "    var c = ns[i][0], r = ns[i][1], p = hexCenter(c, r), dx = p[0] - p0[0], dz = p[1] - p0[1], x = cx + dx / SQ3 * D, y = cy + dz / SQ3 * D, k = K(c, r);\n"
           "    var on = st.at && st.at[0] === c && st.at[1] === r, au = !st.at && auto && auto[0] === c && auto[1] === r, ok = !!okK[k];\n"
           "    if (on || au) sel = [dirName(dx, dz), spotWhat(c, r)];\n"
           "    h += hex(x, y, (ok ? 'ok' : 'no') + (on ? ' on' : '') + (au ? ' au' : ''), ' data-a=\"at\" data-v=\"' + c + ',' + r + '\"') + '<text x=\"' + x.toFixed(1) + '\" y=\"' + (y + 4).toFixed(1) + '\"' + (ok ? '' : ' class=\"no\"') + '>' + spotWhat(c, r) + '</text>';\n"
           "  }\n"
           "  return '<div class=\"sec\">나갈 자리 <small>칸을 눌러 고릅니다</small>' + (st.at ? '<button class=\"btn auto\" type=\"button\" data-a=\"atauto\">자동</button>' : '') + '</div>' +\n"
           "    '<div class=\"dpat\"><svg class=\"dring\" viewBox=\"0 0 184 168\" role=\"img\" aria-label=\"성 둘레 여섯 칸\">' + h + '</svg>' +\n"
           "    '<p class=\"dpat-t\" id=\"dpAt\">' + (sel ? (st.at ? '<b>' + sel[0] + '쪽</b> ' + sel[1] + '<small>고른 자리</small>' : '<b>' + sel[0] + '쪽</b> ' + sel[1] + '<small>자동 — 길이 난 쪽부터</small>') : '<b class=\"bad\">나갈 자리가 없습니다</b>') + '</p></div>';\n"
           "}\n"
           "function ringOn(st) {                                           // 그림의 두 단추\n"
           "  return {\n"
           "    at: function (el) { if (el.getAttribute('class').indexOf('no') >= 0) return toast('그 칸으로는 나갈 수 없습니다'); var v = el.getAttribute('data-v').split(','); st.at = [+v[0], +v[1]]; refreshDialog(); },\n"
           "    atauto: function () { st.at = null; refreshDialog(); }\n"
           "  };\n"
           "}\n"
           "function flowDeploy(b) {\n")
s = rep(s, "  var st = { type: 'sword', ids: [], troops: 0, turns: DEPLOY_FOOD[1], auto: true };\n", "  var st = { type: 'sword', ids: [], troops: 0, turns: DEPLOY_FOOD[1], auto: true, at: null }, RO = ringOn(st);\n")
s = rep(s, "        h += '</div><p class=\"note\" id=\"dpN\">' + foodNote() + '</p>';\n      }\n",
           "        h += '</div><p class=\"note\" id=\"dpN\">' + foodNote() + '</p>' + deployRing(b, st);\n      }\n")
s = rep(s, "      turns: function (el) { st.turns = +el.getAttribute('data-v'); refreshDialog(); },\n",
           "      turns: function (el) { st.turns = +el.getAttribute('data-v'); refreshDialog(); },\n      at: RO.at, atauto: RO.atauto,\n")
s = rep(s, "        var r = cmdDeploy(b, { type: st.type, ids: st.ids, troops: st.troops, food: food() });\n",
           "        var r = cmdDeploy(b, { type: st.type, ids: st.ids, troops: st.troops, food: food(), at: st.at || undefined });\n")
# 수송
s = rep(s, "  var st = { id: list[0].id, troops: Math.min(1000, Math.floor(b.troops / 100) * 100), gold: 0, food: 0, spear: 0, halberd: 0, bow: 0, horse: 0, ram: 0 };\n",
           "  var st = { id: list[0].id, troops: Math.min(1000, Math.floor(b.troops / 100) * 100), gold: 0, food: 0, spear: 0, halberd: 0, bow: 0, horse: 0, ram: 0, at: null }, RO = ringOn(st);\n")
s = rep(s, "cargo: { spear: st.spear, halberd: st.halberd, bow: st.bow, horse: st.horse, ram: st.ram } });\n      if (!r.ok) return toast(r.msg);",
           "cargo: { spear: st.spear, halberd: st.halberd, bow: st.bow, horse: st.horse, ram: st.ram }, at: st.at || undefined });\n      if (!r.ok) return toast(r.msg);")
s = rep(s, "  fs.forEach(function (f) { on[f[0]] = function (el) { st[f[0]] = +el.value; $('tv_' + f[0]).textContent = fmt(st[f[0]]); }; });\n",
           "  fs.forEach(function (f) { on[f[0]] = function (el) { st[f[0]] = +el.value; $('tv_' + f[0]).textContent = fmt(st[f[0]]); }; });\n  on.at = RO.at; on.atauto = RO.atauto;\n")
s = rep(s, "      return h + '<p class=\"note\">군량 80일분은 자동으로 실립니다",
           "      h += deployRing(b, st);\n      return h + '<p class=\"note\">군량 80일분은 자동으로 실립니다")
# 도움말
s = rep(s, "<li>시설이 선 칸도 지나가고 설 수 있습니다.", "<li>출진 · 수송 창의 <b>나갈 자리</b>에서 성 둘레의 어느 칸으로 나갈지 고를 수 있습니다(고르지 않으면 길이 난 쪽부터).</li><li>시설이 선 칸도 지나가고 설 수 있습니다.")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/style.css'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "/* 세이브 파일 보내기 · 가져오기(v0.12) */",
           "/* 나갈 자리(v0.12): 성 둘레 여섯 칸 */\n"
           ".dpat { display: flex; align-items: center; gap: 12px; margin: 2px 0 6px; }\n"
           ".dring { width: 184px; height: 168px; flex: none; touch-action: manipulation; }\n"
           ".dring polygon { fill: #fffdf6; stroke: var(--ink); stroke-width: 1.2; }\n"
           ".dring polygon.c { fill: var(--ink); }\n"
           ".dring polygon.ok { cursor: pointer; }\n"
           ".dring polygon.no { fill: #1b1a1814; stroke: var(--line-2); stroke-dasharray: 2 3; }\n"
           ".dring polygon.au { stroke: var(--seal); stroke-width: 2; stroke-dasharray: 5 4; }\n"
           ".dring polygon.on { fill: var(--seal); stroke: var(--seal-2); stroke-width: 2; }\n"
           ".dring text { font: 800 11px var(--font-body); fill: var(--ink); text-anchor: middle; pointer-events: none; }\n"
           ".dring text.no { fill: var(--dim); font-weight: 500; }\n"
           ".dring text.cn { font: 900 12px var(--font-display); fill: var(--paper); }\n"
           ".dring polygon.on + text { fill: var(--seal-ink); }\n"
           ".dpat-t { margin: 0; font-size: 14px; line-height: 1.5; }\n"
           ".dpat-t b { font: 900 16px var(--font-display); margin-right: 3px; }\n"
           ".dpat-t small { display: block; color: var(--dim); font-size: 12px; }\n"
           "/* 세이브 파일 보내기 · 가져오기(v0.12) */")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
