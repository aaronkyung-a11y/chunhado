# v0.10 (3/…): 군단 — 화면(ui_panels.js · ui3d.js · style.css)
#  - STATUS 창: 군사의 자리 아래에 군단 줄(군단마다 한 칸 — 누르면 군단 창, 끝에 [+ 군단]). 거점이 둘 이상일 때부터 보인다.
#    '지금 할 일'과 '명령 대기 부대'는 직할 거점·직할 부대만 센다(적이 다가온 것은 군단의 거점도 알린다).
#  - 군단 창(showCorps): 군단장 · 행동력 · 병력, 방침 넷(내정 · 군비 · 공격 · 지원), 공격이면 목표와 '낼 수 있는 병력 / 필요', 지원이면 보낼 곳,
#    거점마다 [직할로], 나가 있는 부대마다 [직할로], 지난 보고, [해산]. 방침을 바꾸면 군단장이 대화창에서 답한다.
#  - 새 군단(showCorpsNew): 직할 거점을 골라 [군단 만들기] → 군단장은 가장 알맞은 사람이 맡고(바꿀 수 있다) 방침은 군비로 시작한다.
#  - 거점 창: 군단에 맡긴 거점은 명령 단추 대신 군단 띠(군단 · 방침 · 군단장)와 [군단] · [직할로]. 직할 거점에는 '군단' 탭(거점이 둘 이상일 때).
#  - 부대 창: 군단의 부대는 하는 일("여남 공격")과 [군단] · [직할로]. 직접 움직일 수 없다(직할로 되돌리면 된다).
#  - 지도: 군단의 거점과 부대에는 군단 번호 딱지(①②…).
#  - 턴 재생: 군단의 차례에는 자막의 세력 칩에 군단 이름. 내 군단의 싸움은 천천히 보여 준다.
#  - 지난 열흘의 일: '군단' 토막에 군단마다 한 줄(군단장의 초상과 함께).
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)

# ---------------------------------------------------------------- ui_panels.js
p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()

# 1) 말: 군단장의 대답
s = rep(s, "  released: { W: ['이 은혜는 잊지 않겠소.'], C: ['베푸신 은혜, 잊지 않겠습니다.'], L: ['…이 일은 기억해 두겠소.'] }\n};",
           "  released: { W: ['이 은혜는 잊지 않겠소.'], C: ['베푸신 은혜, 잊지 않겠습니다.'], L: ['…이 일은 기억해 두겠소.'] },\n"
           "  corps:    { W: ['맡겨 주시오. 실망시키지 않겠소.', '이 땅은 내가 지키겠소.'], C: ['맡겨 주십시오. 빈틈없이 다스리겠습니다.', '삼가 맡겠습니다.'], L: ['…'] },\n"
           "  cdev:     { W: ['고을을 일구는 일도 싸움이라 여기겠소.'], C: ['고을을 살찌우겠습니다.', '백성부터 돌보겠습니다.'], L: ['…'] },\n"
           "  carm:     { W: ['병사를 모으고 칼을 갈겠소.'], C: ['군비를 갖추겠습니다.', '병사와 병기를 모으겠습니다.'], L: ['…'] },\n"
           "  catk:     { W: ['{x}{을} 치겠소. 채비가 되는 대로 나서겠소!'], C: ['{x}{을} 치겠습니다. 채비가 되는 대로 나서겠습니다.'], L: ['…'] },\n"
           "  csup:     { W: ['{x}{으로} 병력과 물자를 보내겠소.'], C: ['{x}{으로} 병력과 물자를 보내겠습니다.'], L: ['…'] }\n};")
s = rep(s, "  if (x !== undefined) t = t.replace(/\\{x\\}\\{을\\}/g, josa(String(x), '을를'))", "  if (x !== undefined) t = t.replace(/\\{x\\}\\{으로\\}/g, euro(String(x))).replace(/\\{x\\}\\{을\\}/g, josa(String(x), '을를'))")
s = rep(s, "function hasBatchim(w) {", "function euro(w) { var c = w.charCodeAt(w.length - 1), j = (c >= 0xAC00 && c <= 0xD7A3) ? (c - 0xAC00) % 28 : 0; return w + (j && j !== 8 ? '으로' : '로'); }      // 여남으로 · 소패로 · 강릉으로 · 서울로\nfunction hasBatchim(w) {")

# 2) 명령 대기 · 지금 할 일: 직할만
s = rep(s, "function pendingUnits() { return facUnits(G.player).filter(function (u) { return !u.done && !(u.dest >= 0) && !u.moved; }); }",
           "function pendingUnits() { return directUnits(G.player).filter(function (u) { return !u.done && !(u.dest >= 0) && !u.moved; }); }      // v0.10: 군단의 부대는 군단장이 움직인다")
s = rep(s, "  var f = G.player, F = G.factions[f], out = [], bs = facBases(f), us = facUnits(f), seen = {};\n  bs.forEach(function (b) {\n    var es = enemyUnitsNear(f, b.c, b.r, 4); if (!es.length) return;",
           "  var f = G.player, F = G.factions[f], out = [], all = facBases(f), bs = directBases(f), us = directUnits(f), seen = {};      // v0.10: 할 일은 직할 거점·직할 부대만. 적이 다가온 것은 군단의 거점도 알린다\n  all.forEach(function (b) {\n    var es = enemyUnitsNear(f, b.c, b.r, 4); if (!es.length) return;")
s = rep(s, "go: ['unit', es[0].id], lb: '보기', say: b.n + ' 가까이 '", "go: ['unit', es[0].id], lb: '보기', info: baseCorps(b) ? 1 : 0, say: b.n + ' 가까이 '")
s = rep(s, "  var mar = us.filter(function (u) { return u.dest >= 0; });",
           "  if (!corpsAll().length && all.length >= 4) out.push({ cls: 'cool', ic: '軍', t: '거점 ' + all.length + '곳 — 군단에 맡길 수 있습니다', s: '방침만 주면 군단장이 다스립니다', go: ['corpsnew'], lb: '군단', info: 1, say: '거점이 늘었습니다. 먼 곳은 군단에 맡기시지요.' });\n  var mar = us.filter(function (u) { return u.dest >= 0; });")
s = rep(s, "  else if (g[0] === 'end') doEndTurn();", "  else if (g[0] === 'end') doEndTurn();\n  else if (g[0] === 'corpsnew') showCorpsNew();")

# 3) STATUS 창: 군단 줄
s = rep(s, "      advgo: function () { var t = advTop(st.todo); if (t && t.go) goTodo(t.go); },",
           "      advgo: function () { var t = advTop(st.todo); if (t && t.go) goTodo(t.go); },\n      corps: function (el) { showCorps(+el.getAttribute('data-v')); },\n      corpsnew: function () { showCorpsNew(); },")
s = rep(s, "        '<div class=\"sec\">지금 할 일' + (need ? ' <em class=\"cnt\">' + need + '</em>' : '') + '</div><div class=\"todos\">';",
           "        corpsStrip() +\n        '<div class=\"sec\">지금 할 일' + (need ? ' <em class=\"cnt\">' + need + '</em>' : '') + '</div><div class=\"todos\">';")

# 4) 부대를 골랐을 때: 군단의 부대는 직접 움직일 수 없다
s = rep(s, "  if (u.f === G.player && !u.done) { UI.rc = unitReach(u); UI.atk = allTargets(u); } else { UI.rc = null; UI.atk = null; }",
           "  if (u.f === G.player && !u.done && !unitCorps(u)) { UI.rc = unitReach(u); UI.atk = allTargets(u); } else { UI.rc = null; UI.atk = null; }")
s = rep(s, "  var k = K(c, r), u = UAT[k] || null, b = baseAt(c, r), pl = plotAt(c, r), su = selUnit();",
           "  var k = K(c, r), u = UAT[k] || null, b = baseAt(c, r), pl = plotAt(c, r), su = selUnit();\n  if (su && unitCorps(su)) su = null;                                  // 군단의 부대를 보고 있을 때: 다른 곳을 누르면 그것을 고를 뿐이다")
s = rep(s, "  if (pl && pl.base.owner === G.player) {                              // 내 부지:",
           "  if (pl && pl.base.owner === G.player && baseCorps(pl.base)) { selectBase(pl.base); return; }      // 군단에 맡긴 거점의 부지: 거점 창만 연다\n  if (pl && pl.base.owner === G.player) {                              // 내 부지:")
s = rep(s, "      var su = selUnit();\n      if (su === x) {",
           "      var su = selUnit(), cpU = mine ? unitCorps(x) : null;\n"
           "      if (cpU) {                                                 // 군단의 부대: 하는 일과 [군단] · [직할로]\n"
           "        var Lu = corpsLead(cpU);\n"
           "        h += '<div class=\"cpbn\">' + (Lu ? porTag(Lu, 'sm') : '<i class=\"por sm none\"></i>') + '<div><b>' + corpsName(cpU) + '</b> · ' + unitMission(x) + '<small>군단장' + (Lu ? ' ' + Lu.n : '') + '의 명을 따릅니다</small></div></div>' +\n"
           "          '<div class=\"cmds\"><button class=\"cmd\" type=\"button\" data-a=\"corps\"><b>군단</b><small>' + corpsDirText(cpU) + '</small></button><button class=\"cmd\" type=\"button\" data-a=\"direct\"><b>직할로</b><small>내가 직접 움직인다</small></button></div><div class=\"rows\">';\n"
           "        for (i = 0; i < ms.length; i++) h += offRow(ms[i], { badge: i === 0 ? '주장' : '부장' });\n"
           "        return h + '</div></div>';\n"
           "      }\n"
           "      if (su === x) {")
s = rep(s, "      off: function (el) { showOfficer(off(+el.getAttribute('data-v'))); }\n    },\n    render: function () {\n      var x = UMAP[u.id];",
           "      off: function (el) { showOfficer(off(+el.getAttribute('data-v'))); },\n"
           "      corps: function () { var x = UMAP[u.id], cp = x && unitCorps(x); if (cp) showCorps(cp.id); },\n"
           "      direct: function () { var x = UMAP[u.id]; if (!x) return; var r = corpsTakeUnit(x); if (!r.ok) return toast(r.msg); sfx('ui'); toast(uName(x) + ' — 직할로 되돌렸습니다'); selectUnit(x, true); syncScene(); afterAction(); }\n"
           "    },\n    render: function () {\n      var x = UMAP[u.id];")

# 5) 거점 창: 군단의 거점은 군단 띠, 직할 거점에는 '군단' 탭
s = rep(s, "    fac: function () { var b = B(); return (st.tab === 'fac' && b.owner === G.player && b.kind === 'city') ? b : null; },",
           "    fac: function () { var b = B(); return (st.tab === 'fac' && b.owner === G.player && b.kind === 'city' && !baseCorps(b)) ? b : null; },")
s = rep(s, "    plot: function (el) { var i = +el.getAttribute('data-v'), b = B(); if (b.plots[i].fac) flowFacility(b, i); else flowDevelop(b, i); }\n  };",
           "    plot: function (el) { var i = +el.getAttribute('data-v'), b = B(); if (b.plots[i].fac) flowFacility(b, i); else flowDevelop(b, i); },\n"
           "    corps: function () { var cp = baseCorps(B()); if (cp) showCorps(cp.id); },\n"
           "    direct: function () { var b = B(), cp = baseCorps(b); if (!cp) return; var nm = corpsName(cp), r = corpsRelease(b.id); if (!r.ok) return toast(r.msg); sfx('ui'); toast(b.n + ' — 직할로 되돌렸습니다' + (r.gone ? ' (' + nm + ' 해산)' : '')); syncScene(); refreshSheet(); afterAction(); },\n"
           "    cjoin: function (el) { var b = B(), cp = corpsById(+el.getAttribute('data-v')); if (!cp) return; var r = corpsAssign(cp, b.id); if (!r.ok) return toast(r.msg); corpsSaid(cp, 'corps', undefined, josa(b.n, '을를') + ' ' + corpsName(cp) + '에 맡겼습니다'); syncScene(); refreshSheet(); afterAction(); },\n"
           "    cnew: function () { showCorpsNew(B().id); }\n  };")
s = rep(s, "      if (!mine) {\n        var os = baseOfficers(b);",
           "      var cpB = mine ? baseCorps(b) : null;\n"
           "      if (cpB) {                                                 // 군단에 맡긴 거점: 명령은 군단장이 내린다\n"
           "        var Lb = corpsLead(cpB), ob = baseOfficers(b);\n"
           "        h += '<div class=\"cpbn\">' + (Lb ? porTag(Lb, 'sm') : '<i class=\"por sm none\"></i>') + '<div><b>' + corpsName(cpB) + '</b> · ' + corpsDirText(cpB) + '<small>군단장' + (Lb ? ' ' + Lb.n : ' 없음') + ' — 이 거점의 명령은 군단장이 내립니다</small></div></div>' +\n"
           "          '<div class=\"cmds\"><button class=\"cmd pri\" type=\"button\" data-a=\"corps\"><b>군단</b><small>방침 · 군단장</small></button><button class=\"cmd\" type=\"button\" data-a=\"direct\"><b>직할로</b><small>내가 직접 다스린다</small></button></div>' +\n"
           "          '<div class=\"sec\">무장 <em class=\"cnt\">' + ob.length + '</em></div><div class=\"rows\">';\n"
           "        ob.sort(function (x, y) { return (isLord(y) ? 1000 : 0) + (y.ldr + y.war + y.int + y.pol) / 4 - (isLord(x) ? 1000 : 0) - (x.ldr + x.war + x.int + x.pol) / 4; });\n"
           "        for (i = 0; i < ob.length; i++) h += offRow(ob[i], { badge: isLord(ob[i]) ? '군주' : (cpB.lead === ob[i].id ? '군단장' : advTag(ob[i])), rt: '<span class=\"' + (ob[i].loy < 70 ? 'bad' : '') + '\">충 ' + ob[i].loy + '</span><br>' + offStatus(ob[i]) });\n"
           "        return h + '</div></div>';\n"
           "      }\n"
           "      if (!mine) {\n        var os = baseOfficers(b);")
s = rep(s, "      var tabs = city ? [['home', '내정'], ['mil', '출진'], ['men', '인재'], ['fac', '건설']] : [['mil', '출진'], ['men', '인재']];",
           "      var tabs = city ? [['home', '내정'], ['mil', '출진'], ['men', '인재'], ['fac', '건설']] : [['mil', '출진'], ['men', '인재']];\n"
           "      if (facBases(G.player).length >= 2) tabs.push(['corps', '군단']); else if (st.tab === 'corps') st.tab = tabs[0][0];      // v0.10: 거점이 둘 이상이면 군단에 맡길 수 있다")
s = rep(s, "      if (st.tab === 'home') {\n        h += '<div class=\"cmds\">' + cmd('draft',",
           "      if (st.tab === 'corps') {\n"
           "        var cps = corpsAll(), canLead = baseOfficers(b).some(function (o) { return !isLord(o); });\n"
           "        h += '<p class=\"note\">직할 거점입니다. 군단에 맡기면 군단장이 <b>방침</b>대로 다스리고, 언제든 직할로 되돌릴 수 있습니다.</p><div class=\"rows\">';\n"
           "        for (i = 0; i < cps.length; i++) { var Lj = corpsLead(cps[i]); h += '<div class=\"row\">' + (Lj ? porTag(Lj) : '<i class=\"por none\"></i>') + '<span class=\"mid\"><span class=\"nm\">' + corpsName(cps[i]) + '</span><span class=\"ds\">' + (Lj ? Lj.n + ' · ' : '') + corpsDirText(cps[i]) + ' · 거점 ' + corpsBases(cps[i]).length + '</span></span><button class=\"btn pri\" type=\"button\" data-a=\"cjoin\" data-v=\"' + cps[i].id + '\">맡기기</button></div>'; }\n"
           "        h += '</div><div class=\"cmds\"><button class=\"cmd' + (cps.length ? '' : ' pri') + (cps.length >= CORPS_MAX ? ' off' : '') + '\" type=\"button\" data-a=\"cnew\"><b>새 군단</b><small>' + (cps.length >= CORPS_MAX ? CORPS_MAX + '개까지' : (canLead ? '이 거점부터' : '거점을 골라서')) + '</small></button></div>';\n"
           "      } else if (st.tab === 'home') {\n        h += '<div class=\"cmds\">' + cmd('draft',")
s = rep(s, "function flowDevelop(b, pi) {\n  if (b.owner !== G.player) return;", "function flowDevelop(b, pi) {\n  if (b.owner !== G.player || baseCorps(b)) return;")
s = rep(s, "function flowFacility(b, pi) {\n  var fc = b.plots[pi].fac; if (!fc) return;", "function flowFacility(b, pi) {\n  var fc = b.plots[pi].fac; if (!fc || baseCorps(b)) return;")

# 6) 턴 재생: 군단의 차례
s = rep(s, "  $('plFac').innerHTML = F ? '<span class=\"chip\" style=\"background:' + F.color + '\">' + F.name + '군' + (f === G.player ? ' · 아군' : '') + '</span>'",
           "  var pcp = (f === G.player && UI.play && UI.play.cp) ? corpsById(UI.play.cp) : null;\n"
           "  $('plFac').innerHTML = F ? '<span class=\"chip\" style=\"background:' + F.color + '\">' + F.name + '군' + (f === G.player ? (pcp ? ' · ' + corpsName(pcp) : ' · 아군') : '') + '</span>'")
s = rep(s, "    var s = P.next(), evs = EVQ.splice(0, EVQ.length), show = [], i, e, big = false, onlyMoves = false;",
           "    var s = P.next(), evs = EVQ.splice(0, EVQ.length), show = [], i, e, big = false, onlyMoves = false;\n"
           "    if (s) { if (s.corps) P.cp = s.corps; else if (s.kind !== 'step') P.cp = 0; }             // 군단의 차례인가(자막의 칩에 군단 이름을 붙인다)")
s = rep(s, "  if (e.t === 'act') return e.tf === G.player ? 2 : (nearMine(e.tc, e.tr, 7) ? 1 : 0);",
           "  if (e.t === 'act') return (e.tf === G.player || e.f === G.player) ? 2 : (nearMine(e.tc, e.tr, 7) ? 1 : 0);      // v0.10: 내 군단이 치는 싸움도 천천히")

# 7) 지난 열흘의 일: 군단 토막
s = rep(s, "  var secs = [['중요한 일', []], ['우리 세력', []], ['천하의 움직임', []]], i, n = 0;\n  for (i = 0; i < list.length; i++) {\n    var e = list[i]; if (e.imp < 1) continue;\n    secs[e.imp >= 2 ? 0 : (e.f === G.player ? 1 : 2)][1].push(i); n++;\n  }",
           "  var secs = [['중요한 일', []], ['군단', []], ['우리 세력', []], ['천하의 움직임', []]], i, n = 0;\n  for (i = 0; i < list.length; i++) {\n    var e = list[i]; if (e.imp < 1) continue;\n    secs[e.imp >= 2 ? 0 : (e.corps ? 1 : (e.f === G.player ? 2 : 3))][1].push(i); n++;\n  }")
s = rep(s, "      for (var s = 0; s < 3; s++) {\n        var ids = secs[s][1]; if (!ids.length) continue;",
           "      for (var s = 0; s < secs.length; s++) {\n        var ids = secs[s][1]; if (!ids.length) continue;")
s = rep(s, "'\"><span class=\"mk\">' + (x.imp >= 3 ? '★' : (s === 0 ? '●' : '·')) + '</span><span class=\"mid\">' + x.t + '</span>'",
           "'\">' + repMark(x, s) + '<span class=\"mid\">' + x.t + '</span>'")
s = rep(s, "function showReport(list) {", "function repMark(x, s) {                            // 줄 머리: 군단의 보고는 군단장의 초상\n"
           "  var cp = x.corps ? corpsById(x.corps) : null, L = cp ? corpsLead(cp) : null;\n"
           "  if (L && x.imp < 2) return porTag(L, 'sm');\n"
           "  return '<span class=\"mk\">' + (x.imp >= 3 ? '★' : (s === 0 ? '●' : '·')) + '</span>';\n}\nfunction showReport(list) {")

# 8) 도움말
s = rep(s, "  '<h3>군사(軍師)</h3>", "  '<h3>군단</h3><p>거점이 늘면 먼 곳은 <b>군단</b>에 맡길 수 있습니다. STATUS 창의 <b>+ 군단</b>(또는 거점 창의 <b>군단</b> 탭)에서 맡길 거점을 고르면 그 거점의 무장 가운데 한 사람이 <b>군단장</b>이 되어 다스립니다. 군단 창에서 <b>방침</b>을 줍니다 — <b>내정</b>(시설 · 치안, 병력은 지킬 만큼만) · <b>군비</b>(징병 · 병기 · 훈련) · <b>공격</b>(고른 거점을 친다) · <b>지원</b>(병력과 물자를 고른 내 거점으로 보낸다).</p>' +\n"
           "  '<p>군단은 내가 <b>턴 종료</b>를 누른 직후, 다른 세력보다 먼저 움직입니다. 한 일은 <b>지난 열흘의 일</b>에 군단마다 한 줄로 나옵니다. 군단은 <b>제 행동력</b>을 따로 씁니다(턴마다 ' + CORPS_AP.base + ' + 도시 × ' + CORPS_AP.city + ' + 군단장 매력 ÷ 5) — 맡긴 도시는 내 행동력에서 빠집니다.</p>' +\n"
           "  '<p><b>공격</b>은 군단장이 이길 만하다고 볼 때만 나섭니다: 낼 수 있는 병력이 <b>(수비 + 가는 동안 늘어날 몫) × ' + CORPS_ATK.mul + ' + ' + fmt(CORPS_ATK.add) + '</b>을 넘고 행동력이 60 모였을 때(지키는 장수의 무력·통솔이 75를 넘으면 그만큼 더 — 100이면 1.5배). 수비에는 그 세력이 12칸 안에 내놓은 부대도 셉니다. 한번 나서면 남은 도시들도 뒤따라 보탭니다. 군단 창에 지금의 병력과 필요한 병력이 적혀 있습니다. 군단이 차지한 거점은 그 군단에 들고, 목표를 손에 넣으면 방침은 군비로 돌아갑니다. 먼저 치면 그 세력과의 초반 보호가 풀리는 것은 내가 칠 때와 같습니다.</p>' +\n"
           "  '<p>맡긴 거점과 군단의 부대에는 직접 명령할 수 없습니다. 거점 창 · 부대 창 · 군단 창의 <b>직할로</b>를 누르면 언제든 되돌아옵니다. 포로는 군단장이 풀어 주지 않습니다(등용만 권합니다).</p>' +\n"
           "  '<h3>군사(軍師)</h3>")

# 8b) 목록: 맡긴 거점에는 군단 이름, '명령을 기다리는 부대'는 직할만
s = rep(s, "+ b.n + ' <em>' + SIZE_NAME[b.sz] + '</em></span><span class=\"ds\">금 '", "+ b.n + ' <em>' + SIZE_NAME[b.sz] + '</em>' + (baseCorps(b) ? ' <em class=\"advt\">' + corpsName(baseCorps(b)) + '</em>' : '') + '</span><span class=\"ds\">금 '")
s = rep(s, "ready = us.filter(function (u) { return !u.done && !u.status; }).length;", "ready = us.filter(function (u) { return !u.done && !u.status && !unitCorps(u); }).length;")

# 9) 새 함수들
s += r"""
/* ---------- 군단(v0.10) ---------- */
var DIR_KEYS = ['dev', 'arm', 'atk', 'sup'];
var DIR_SUB = { dev: '시설 · 치안', arm: '징병 · 병기 · 훈련', atk: '고른 거점을 친다', sup: '병력 · 물자를 보낸다' };
/* 군단의 부대가 지금 하는 일 */
function unitMission(u) {
  var ai = u.ai || {}, T = (ai.target !== undefined && ai.target >= 0) ? G.bases[ai.target] : null, H = (ai.home !== undefined && ai.home >= 0) ? G.bases[ai.home] : null;
  if (u.type === 'trans') return T ? euro(T.n) + ' 수송' : '수송';
  if (ai.mode === 'attack' && T) return T.owner === G.player ? T.n + ' 입성' : T.n + ' 공격';
  if (ai.mode === 'defend' && H) return H.n + ' 방어';
  if (ai.mode === 'garrison' && T) return T.n + ' 입성';
  return '귀환';
}
/* 군단장이 대화창에서 답한다(군단장이 없으면 알림 줄) */
function corpsSaid(cp, key, x, sub) { var L = corpsLead(cp); if (L) talk(L, sayLine(L, key, x), sub); else if (sub) toast(String(sub).replace(/<[^>]*>/g, '')); }
/* STATUS 창의 군단 줄 */
function corpsStrip() {
  var f = G.player, cps = corpsAll(), n = facBases(f).length, i, h = '';
  if (!cps.length && n < 2) return '';
  h = '<div class="hm-corps">';
  for (i = 0; i < cps.length; i++) {
    var cp = cps[i], L = corpsLead(cp);
    h += '<button class="cpb" type="button" data-a="corps" data-v="' + cp.id + '">' + (L ? porTag(L, 'sm') : '<i class="por sm none"></i>') + '<span><b>' + corpsName(cp) + '</b><small>' + corpsDirText(cp) + '</small></span></button>';
  }
  if (cps.length < CORPS_MAX && directBases(f).length) h += '<button class="cpb new" type="button" data-a="corpsnew"><span><b>+ 군단</b><small>거점 맡기기</small></span></button>';
  return h + '</div>';
}
/* 공격 방침: 지금 나설 수 있는가를 한 줄로 */
function corpsWaitText(cp) {
  var T = G.bases[cp.target], o = cp.dir === 'atk' ? corpsOutlook(cp, T) : null;
  if (!o) return '';
  var tot = o.have + o.going;
  if (o.going >= o.need && o.going > 0) return '<b class="ok">' + fmt(o.going) + '명이 가고 있습니다</b>';
  if (T.owner < 0) return tot >= o.need ? '<b class="ok">빈 거점 — 곧 차지하러 나섭니다</b>' : '<b class="bad">보낼 병력이 없습니다</b>';
  if (tot >= o.need) return '<b class="ok">나설 수 있습니다</b> — 낼 수 있는 병력 ' + fmt(tot) + ' / 필요 ' + fmt(o.need) + (cp.ap < 60 && !o.going ? ' · 행동력 60이 모이면' : '');
  return '<b class="bad">아직 모자랍니다</b> — 낼 수 있는 병력 ' + fmt(tot) + ' / 필요 ' + fmt(o.need);
}
function corpsRefresh() { syncScene(); refreshDialog(); refreshSheet(); refreshHud(); requestDraw(); }
/* 군단 창 */
function showCorps(id) {
  showDialog({
    render: function () {
      var cp = corpsById(id), i;
      if (!cp) return dlgHead('군단') + '<div class="dlg-b"><p class="note">이 군단은 해산되었습니다.</p></div>';
      var L = corpsLead(cp), bs = corpsBases(cp), us = corpsUnits(cp), T = (cp.target !== undefined && cp.target >= 0) ? G.bases[cp.target] : null;
      var h = dlgHead(corpsName(cp)) + '<div class="dlg-b">' +
        '<div class="card cpc">' + (L ? porTag(L, 'md') : '<i class="por md none"></i>') + '<div><p>군단장 <b class="hi">' + (L ? L.n : '없음') + '</b></p><p class="note">행동력 <b>' + cp.ap + '</b> <small>(+' + corpsRegen(cp) + '/턴)</small> · 병력 <b>' + fmt(corpsTroops(cp)) + '</b> · 무장 ' + corpsOfficers(cp).length + '명</p></div><button class="btn" type="button" data-a="lead">바꾸기</button></div>' +
        '<div class="sec">방침</div><div class="opts cpd">';
      for (i = 0; i < DIR_KEYS.length; i++) h += '<button class="opt' + (cp.dir === DIR_KEYS[i] ? ' on' : '') + '" type="button" data-a="dir" data-v="' + DIR_KEYS[i] + '"><b>' + CORPS_DIR[DIR_KEYS[i]] + '</b><small>' + DIR_SUB[DIR_KEYS[i]] + '</small></button>';
      h += '</div>';
      if (cp.dir === 'atk' && T) h += '<div class="cpg"><p>목표 <b>' + T.n + '</b> ' + (T.owner >= 0 ? facChip(T.owner) + ' 병력 ' + fmt(T.troops) + (corpsFoeK(T) >= 1.2 ? ' · 맹장 ' + foeBest(T) : '') : '<em class="advt">빈 거점</em>') + '<button class="btn sm" type="button" data-a="tgt">바꾸기</button></p><p class="note">' + corpsWaitText(cp) + '</p>' + (peaceWouldBreak(T.owner) ? '<p class="note pzw">먼저 치면 <b>' + facName(T.owner) + '군과의 보호가 풀립니다</b></p>' : '') + '</div>';
      else if (cp.dir === 'sup' && T) h += '<div class="cpg"><p>보낼 곳 <b>' + T.n + '</b> ' + (baseCorps(T) ? '<em class="advt">' + corpsName(baseCorps(T)) + '</em>' : '<em class="advt">직할</em>') + '<button class="btn sm" type="button" data-a="tgt">바꾸기</button></p><p class="note">한 달에 한 번, 지킬 만큼만 남기고 보냅니다</p></div>';
      h += '<div class="sec">거점 <em class="cnt">' + bs.length + '</em><button class="btn sm" type="button" data-a="add">+ 넣기</button></div><div class="rows cpl">';
      for (i = 0; i < bs.length; i++) h += '<div class="row">' + thumb(bs[i].kind === 'city' ? 'city_' + bs[i].sz : 'gate') + '<span class="mid"><span class="nm">' + bs[i].n + '</span><span class="ds">' + SIZE_NAME[bs[i].sz] + ' · 병력 ' + fmt(bs[i].troops) + ' · 무장 ' + baseOfficers(bs[i]).length + '명</span></span><button class="btn" type="button" data-a="rel" data-v="' + bs[i].id + '">직할로</button></div>';
      h += '</div>';
      if (us.length) {
        h += '<div class="sec">부대 <em class="cnt">' + us.length + '</em></div><div class="rows cpl">';
        for (i = 0; i < us.length; i++) h += '<div class="row">' + porTag(uLeader(us[i])) + '<span class="mid"><span class="nm">' + uName(us[i]) + '</span><span class="ds">' + UNIT_TYPES[us[i].type].name + ' ' + fmt(us[i].troops) + '명 · ' + unitMission(us[i]) + '</span></span><button class="btn" type="button" data-a="take" data-v="' + us[i].id + '">직할로</button></div>';
        h += '</div>';
      }
      if (cp.note) h += '<div class="sec">지난 보고</div><p class="note cpn">' + (cp.note.s || '한 일 없음') + '</p>';
      return h + '<div class="cmds"><button class="cmd" type="button" data-a="disband"><b>해산</b><small>모두 직할로</small></button></div></div>';
    },
    on: {
      dir: function (el) {
        var cp = corpsById(id), k = el.getAttribute('data-v'); if (!cp) return;
        if (k === 'atk') return pickCorpsTarget(cp);
        if (k === 'sup') return pickCorpsDest(cp);
        if (cp.dir === k) return;
        var r = corpsSetDir(cp, k, -1); if (!r.ok) return toast(r.msg);
        sfx('ui'); corpsSaid(cp, k === 'dev' ? 'cdev' : 'carm', undefined, corpsName(cp) + ' 방침 — <b>' + CORPS_DIR[k] + '</b>'); corpsRefresh();
      },
      tgt: function () { var cp = corpsById(id); if (!cp) return; if (cp.dir === 'atk') pickCorpsTarget(cp); else pickCorpsDest(cp); },
      lead: function () {
        var cp = corpsById(id); if (!cp) return;
        pickOfficers({ push: true, title: corpsName(cp) + ' — 군단장', list: corpsLeadCands(cp), max: 1, hi: 'ldr', key: corpsLeadScore, rtHead: '자리', rt: function (o) { return o.unit !== null ? '출진 중' : G.bases[o.loc].n; }, auto: function () { return corpsLeadCands(cp).slice(0, 1).map(function (o) { return o.id; }); }, preview: function (os) { return '행동력 +' + (CORPS_AP.base + CORPS_AP.city * corpsCities(cp).length + Math.floor(os[0].cha / 5)) + '/턴 <small>(매력 ' + os[0].cha + ')</small>'; }, ok: '맡기기' },
          function (os) { var r = corpsSetLead(cp, os[0].id); if (!r.ok) { toast(r.msg); return false; } sfx('ui'); showCorps(cp.id); talk(os[0], sayLine(os[0], 'corps'), josa(os[0].n, '이가') + ' ' + corpsName(cp) + '의 군단장이 되었습니다'); corpsRefresh(); return true; });      // 표는 창을 모두 닫으므로 군단 창을 다시 연다
      },
      add: function () { var cp = corpsById(id); if (cp) pickCorpsBase(cp); },
      rel: function (el) {
        var cp = corpsById(id), b = G.bases[+el.getAttribute('data-v')]; if (!cp || !b) return;
        var nm = corpsName(cp), r = corpsRelease(b.id); if (!r.ok) return toast(r.msg);
        sfx('ui'); toast(b.n + ' — 직할로 되돌렸습니다' + (r.gone ? ' (' + nm + ' 해산)' : ''));
        if (r.gone) closeDialog();
        corpsRefresh();
      },
      take: function (el) { var u = UMAP[+el.getAttribute('data-v')]; if (!u) return; var r = corpsTakeUnit(u); if (!r.ok) return toast(r.msg); sfx('ui'); toast(uName(u) + ' — 직할로 되돌렸습니다'); corpsRefresh(); },
      disband: function (el) {
        var cp = corpsById(id); if (!cp) return;
        if (!el.getAttribute('data-c')) { el.setAttribute('data-c', '1'); el.querySelector('b').textContent = '정말 해산?'; el.classList.add('pri'); return; }
        var nm = corpsName(cp); corpsDisband(cp); closeDialog(); sfx('ui'); toast(nm + ' 해산 — 거점과 부대를 모두 직할로 되돌렸습니다'); corpsRefresh();
      }
    }
  });
}
/* 그 거점을 지키는 가장 뛰어난 장수(무력·통솔 가운데 큰 쪽) — '필요'가 높은 까닭을 알린다 */
function foeBest(b) { var best = null, bv = 0; baseOfficers(b).forEach(function (o) { var v = Math.max(o.war, o.ldr); if (v > bv) { bv = v; best = o; } }); return best ? best.n : ''; }
/* 공격 목표 고르기: 가까운 곳부터, 거점마다 '필요' 병력 */
function pickCorpsTarget(cp) {
  var L = G.bases.filter(function (b) { return b.owner !== G.player; }).map(function (b) { return { b: b, o: corpsOutlook(cp, b) }; }).sort(function (x, y) { return x.o.len - y.o.len || x.b.id - y.b.id; }).slice(0, 14);
  showDialog({
    render: function () {
      var have = L.length ? L[0].o.have : 0, h = dlgHead(corpsName(cp) + ' — 어디를 칠까요') + '<div class="dlg-b"><p class="cap">지금 낼 수 있는 병력 <b>' + fmt(have) + '</b>. <b>필요</b>를 넘으면 군단장이 나섭니다.</p><div class="rows cptl">';
      for (var i = 0; i < L.length; i++) {
        var b = L[i].b, o = L[i].o, ok = o.have + o.going >= o.need;
        h += '<button class="row' + (cp.dir === 'atk' && cp.target === b.id ? ' sel' : '') + '" type="button" data-a="t" data-v="' + b.id + '">' + thumb(b.kind === 'city' ? 'city_' + b.sz : 'gate') + '<span class="mid"><span class="nm">' + b.n + ' ' + (b.owner >= 0 ? facChip(b.owner) : '<em class="advt">빈 거점</em>') + '</span><span class="ds">' + (b.owner >= 0 ? '병력 ' + fmt(b.troops) + ' · ' : '') + days(Math.max(1, Math.ceil(o.len / 5))) + ' 거리' + (peaceWouldBreak(b.owner) ? ' · <b class="bad">보호가 풀림</b>' : '') + (o.k >= 1.2 ? ' · 맹장 <b>' + foeBest(b) + '</b>' : '') + '</span></span><span class="rt' + (ok ? ' ok' : '') + '">필요 <b>' + fmt(o.need) + '</b></span></button>';
      }
      return h + '</div></div>';
    },
    on: { t: function (el) {
      var T = G.bases[+el.getAttribute('data-v')], r = corpsSetDir(cp, 'atk', T.id); if (!r.ok) return toast(r.msg);
      sfx('drum'); backDialog(); corpsSaid(cp, 'catk', T.n, corpsName(cp) + ' 방침 — <b>공격 → ' + T.n + '</b>'); corpsRefresh();
    } }
  }, true);
}
/* 지원할 곳 고르기: 이 군단 밖의 내 거점 */
function pickCorpsDest(cp) {
  var from = corpsBases(cp)[0], L = facBases(G.player).filter(function (b) { return b.corps !== cp.id; });
  if (!L.length) return toast('보낼 다른 거점이 없습니다');
  L.sort(function (x, y) { return (from ? hdist(from.c, from.r, x.c, x.r) - hdist(from.c, from.r, y.c, y.r) : 0) || x.id - y.id; });
  showDialog({
    render: function () {
      var h = dlgHead(corpsName(cp) + ' — 어디로 보낼까요') + '<div class="dlg-b"><p class="cap">병력 · 금 · 병량 · 병기를 한 달에 한 번 실어 보냅니다.</p><div class="rows">';
      for (var i = 0; i < L.length; i++) { var b = L[i], oc = baseCorps(b); h += '<button class="row' + (cp.dir === 'sup' && cp.target === b.id ? ' sel' : '') + '" type="button" data-a="d" data-v="' + b.id + '">' + thumb(b.kind === 'city' ? 'city_' + b.sz : 'gate') + '<span class="mid"><span class="nm">' + b.n + ' <em class="advt">' + (oc ? corpsName(oc) : '직할') + '</em></span><span class="ds">병력 ' + fmt(b.troops) + ' · 금 ' + fmt(b.gold) + ' · 병량 ' + fmt(b.food) + '</span></span><span class="rt">' + (from ? days(Math.max(1, Math.ceil(hdist(from.c, from.r, b.c, b.r) / 5))) : '') + '</span></button>'; }
      return h + '</div></div>';
    },
    on: { d: function (el) {
      var D = G.bases[+el.getAttribute('data-v')], r = corpsSetDir(cp, 'sup', D.id); if (!r.ok) return toast(r.msg);
      sfx('ui'); backDialog(); corpsSaid(cp, 'csup', D.n, corpsName(cp) + ' 방침 — <b>지원 → ' + D.n + '</b>'); corpsRefresh();
    } }
  }, true);
}
/* 군단에 거점 넣기: 이 군단 밖의 내 거점(직할이든 다른 군단의 것이든) */
function pickCorpsBase(cp) {
  showDialog({
    render: function () {
      var L = facBases(G.player).filter(function (b) { return b.corps !== cp.id; }), h = dlgHead(corpsName(cp) + ' — 넣을 거점') + '<div class="dlg-b"><div class="rows cpl">';
      for (var i = 0; i < L.length; i++) { var b = L[i], oc = baseCorps(b); h += '<div class="row">' + thumb(b.kind === 'city' ? 'city_' + b.sz : 'gate') + '<span class="mid"><span class="nm">' + b.n + ' <em class="advt">' + (oc ? corpsName(oc) : '직할') + '</em>' + (baseOfficers(b).some(isLord) ? ' <em class="advt">군주</em>' : '') + '</span><span class="ds">' + SIZE_NAME[b.sz] + ' · 병력 ' + fmt(b.troops) + ' · 무장 ' + baseOfficers(b).length + '명</span></span><button class="btn pri" type="button" data-a="b" data-v="' + b.id + '">넣기</button></div>'; }
      if (!L.length) h += '<p class="note">넣을 거점이 없습니다.</p>';
      return h + '</div></div>';
    },
    on: { b: function (el) { var b = G.bases[+el.getAttribute('data-v')], r = corpsAssign(cp, b.id); if (!r.ok) return toast(r.msg); sfx('ui'); corpsSaid(cp, 'corps', undefined, josa(b.n, '을를') + ' ' + corpsName(cp) + '에 맡겼습니다'); corpsRefresh(); } }
  }, true);
}
/* 새 군단: 맡길 직할 거점 고르기 */
function showCorpsNew(pre) {
  var sel = {};
  if (pre !== undefined && G.bases[pre] && !baseCorps(G.bases[pre])) sel[pre] = 1;
  showDialog({
    render: function () {
      var bs = directBases(G.player), i, n = 0, h = dlgHead('새 군단 — 맡길 거점') + '<div class="dlg-b"><p class="cap">고른 거점을 군단장이 방침대로 다스립니다. 언제든 직할로 되돌릴 수 있습니다.</p><div class="rows">';
      for (i = 0; i < bs.length; i++) {
        var b = bs[i], on = !!sel[b.id], os = baseOfficers(b);
        if (on) n++;
        h += '<button class="row' + (on ? ' sel' : '') + '" type="button" data-a="b" data-v="' + b.id + '">' + thumb(b.kind === 'city' ? 'city_' + b.sz : 'gate') + '<span class="mid"><span class="nm">' + b.n + (os.some(isLord) ? ' <em class="advt">군주</em>' : '') + '</span><span class="ds">' + SIZE_NAME[b.sz] + ' · 병력 ' + fmt(b.troops) + ' · 무장 ' + os.length + '명</span></span><span class="rt ck">' + (on ? '✓' : '') + '</span></button>';
      }
      return h + '</div></div><div class="dlg-f"><div class="pv">' + (n ? '거점 <b>' + n + '</b>곳' : '거점을 고르세요') + '</div><button class="btn pri" type="button" data-a="ok"' + (n ? '' : ' disabled') + '>군단 만들기</button></div>';
    },
    on: {
      b: function (el) { var id = +el.getAttribute('data-v'); if (sel[id]) delete sel[id]; else sel[id] = 1; refreshDialog(); },
      ok: function () {
        var ids = Object.keys(sel).map(Number); if (!ids.length) return;
        var r = corpsCreate(ids); if (!r.ok) return toast(r.msg, 3200);
        var cp = r.corps; sfx('drum'); closeDialog(); clearSel(); showHome(); showCorps(cp.id);
        corpsSaid(cp, 'corps', undefined, corpsName(cp) + ' — 거점 ' + ids.length + '곳을 맡았습니다'); corpsRefresh();
      }
    }
  });
}
"""
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- ui3d.js: 지도의 군단 딱지
p = 'src/ui3d.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "    sig = b.owner + '|' + (b.owner >= 0 ? Math.round(b.troops / 100) : '') + '|' + (mineB ? (idleN[b.id] || 0) : '') + '|' + (UI.sel && UI.sel.kind === 'base' && UI.sel.id === b.id);",
           "    var cpL = mineB ? baseCorps(b) : null;                                 // 군단에 맡긴 거점: 쉬는 무장 수 대신 군단 번호 딱지\n"
           "    sig = b.owner + '|' + (b.owner >= 0 ? Math.round(b.troops / 100) : '') + '|' + (mineB && !cpL ? (idleN[b.id] || 0) : '') + '|' + (UI.sel && UI.sel.kind === 'base' && UI.sel.id === b.id) + '|' + (cpL ? cpL.n : '');")
s = rep(s, "      drawLabel(o.lab, ls, shade(col, 0.86), (UI.sel && UI.sel.kind === 'base' && UI.sel.id === b.id) ? SEAL : INK, mineB && idleN[b.id] ? idleN[b.id] : 0);",
           "      drawLabel(o.lab, ls, shade(col, 0.86), (UI.sel && UI.sel.kind === 'base' && UI.sel.id === b.id) ? SEAL : INK, cpL ? corpsMark(cpL) : (mineB && idleN[b.id] ? idleN[b.id] : 0), cpL ? INK : null);")
s = rep(s, "function drawLabel(L, lines, bg, border, badge) {", "function corpsMark(cp) { return cp.n >= 1 && cp.n <= 20 ? String.fromCharCode(0x245F + cp.n) : String(cp.n); }      // ① ② ③ …\nfunction drawLabel(L, lines, bg, border, badge, badgeBg) {")
s = rep(s, "  if (badge) { rr(x, w - 31, 3, 28, 28, 4); x.fillStyle = SEAL; x.fill();", "  if (badge) { rr(x, w - 31, 3, 28, 28, 4); x.fillStyle = badgeBg || SEAL; x.fill();")
s = rep(s, "    sig = u.f + '|' + u.type + '|' + Math.round(u.troops / 10) + '|' + (u.f === G.player && u.done) + '|'",
           "    var cpU = unitCorps(u);\n    sig = (cpU ? cpU.n : '') + '|' + u.f + '|' + u.type + '|' + Math.round(u.troops / 10) + '|' + (u.f === G.player && u.done) + '|'")
s = rep(s, "      var mark = (!u.status && u.dest >= 0) ? '▸ ' : '', lns", "      var mark = cpU ? corpsMark(cpU) + ' ' : ((!u.status && u.dest >= 0) ? '▸ ' : ''), lns")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- style.css
p = 'src/style.css'; s = io.open(p, encoding='utf-8').read()
s += """
/* ---------- 군단(v0.10) ---------- */
.hm-corps { display: flex; gap: 6px; overflow-x: auto; margin: 0 0 10px; padding-bottom: 2px; -webkit-overflow-scrolling: touch; }
.hm-corps .cpb { flex: none; display: flex; align-items: center; gap: 7px; min-height: 44px; padding: 4px 10px 4px 5px; border: 1px solid var(--line); background: var(--paper-2); color: var(--ink); border-radius: 3px; font: inherit; text-align: left; cursor: pointer; }
.hm-corps .cpb .por { flex: none; }
.hm-corps .cpb span { display: flex; flex-direction: column; line-height: 1.2; }
.hm-corps .cpb b { font-size: 13px; }
.hm-corps .cpb small { font-size: 11px; color: var(--dim); white-space: nowrap; }
.hm-corps .cpb.new { padding-left: 10px; border-style: dashed; background: transparent; }
.hm-corps .cpb.new b { color: var(--seal); }
.cpbn { display: flex; align-items: center; gap: 9px; margin: 10px 0 8px; padding: 8px 10px; border: 1px solid var(--line); border-left: 4px solid var(--ink); background: var(--paper-2); font-size: 14px; }
.cpbn > div { min-width: 0; }
.cpbn small { display: block; margin-top: 2px; font-size: 11.5px; color: var(--dim); }
.card.cpc { align-items: center; }
.card.cpc > div { flex: 1; min-width: 0; }
.card.cpc .btn { flex: none; }
.opts.cpd { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.opts.cpd .opt small { white-space: nowrap; }
.cpg { margin: 8px 0 2px; padding: 8px 10px; border: 1px solid var(--line); background: var(--paper-2); }
.cpg p { margin: 0; font-size: 14px; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.cpg p.note { display: block; margin-top: 5px; font-size: 12.5px; }
.cpg .btn.sm { margin-left: auto; }
.btn.sm { min-height: 30px; padding: 3px 9px; font-size: 12px; }
.sec .btn.sm { float: right; margin-top: -5px; }
.rows.cpl .row { cursor: default; }
.rows.cpl .row .btn { flex: none; min-width: 58px; }
.row .rt.ok b, .row .rt.ok { color: #2e6b3a; }
.row .rt.ck { font-size: 18px; font-weight: 800; color: var(--seal); min-width: 20px; text-align: center; }
.note.cpn { line-height: 1.5; }
.row.rep .por { flex: none; margin-right: 2px; }
.rows.cptl .row .ds { white-space: normal; }
"""
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
