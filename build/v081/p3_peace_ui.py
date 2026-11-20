# v0.8.1 초반 보호 — 화면
#  ① STATUS 창: 날짜 줄에 '보호 N턴' 표, '지금 할 일' 맨 위에 '초반 보호 — ○○까지(N턴)' 줄(누르면 풀이)
#  ② 보호 중인 세력의 거점·시설을 고르면 대상 줄 아래에 '먼저 치면 보호가 풀린다'는 경고, 치고 나면 알림 + 기록
#  ③ 군주 고르기: 세력마다 시작 병력과 보호 기간. 시작 안내에도 한 줄
#  ④ 도움말 '초반 보호'
#  ⑤ 낡은 안내문 고침: 부대 창의 "옅은 파란 칸은 성역의 경계 — 넘으면 이번 턴 이동이 끝납니다"(0.8에서 없앤 규칙인데 글이 남아 있었다)
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:100])
    return s.replace(a, b)
p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, """function peaceTurns(f) {                 // 세력 f 로 시작하면 몇 턴 보호받는가(시작 병력으로 정한다)
  var t = 0; G.bases.forEach(function (b) { if (b.owner === f) t += b.troops; });
  for (var i = 0; i < PEACE_PLAYER.length; i++) if (t < PEACE_PLAYER[i][0]) return PEACE_PLAYER[i][1];
  return PEACE_ALL;
}""", """function peaceFor(troops) {               // 시작 병력 → 보호 턴 수
  for (var i = 0; i < PEACE_PLAYER.length; i++) if (troops < PEACE_PLAYER[i][0]) return PEACE_PLAYER[i][1];
  return PEACE_ALL;
}
function peaceTurns(f) {                 // 세력 f 로 시작하면 몇 턴 보호받는가(지금 가진 병력으로 — 새 판을 만들 때 부른다)
  var t = 0; G.bases.forEach(function (b) { if (b.owner === f) t += b.troops; });
  return peaceFor(t);
}
/* 시나리오에서 세력 i 가 처음 가진 병력(성 + 관문) — newGame 과 같은 셈. 판을 만들기 전(군주 고르기)에 쓴다 */
function startTroops(i) {
  var sf = SCENARIO.factions[i], st = START[sf.n] || [10000, 1500, 15000, 1000], t = 0, j;
  for (j = 0; j < sf.cities.length; j++) t += Math.round(st[0] * (j === 0 ? 1 : 0.55) / 100) * 100;
  for (var gn in SCENARIO.gates) if (SCENARIO.gates[gn] === i && baseByName(gn) >= 0) t += 2000;
  return t;
}
/* 지금 플레이어가 세력 o 의 거점·시설을 치면 초반 보호가 깨지는가 */
function peaceWouldBreak(o) { return !!G.peace && o >= 0 && o !== G.player && G.turn < G.peace.until && !G.peace.broken[o]; }
/* 플레이어가 먼저 쳐서 보호가 풀린 세력(살아 있는 것만) */
function peaceBroken() { var out = []; if (G.peace) for (var k in G.peace.broken) if (G.peace.broken[k] && G.factions[+k] && G.factions[+k].alive) out.push(+k); return out; }""")
s = rep(s, """    G.peace.broken[hf] = true;
    if (G.turn < G.peace.until) res.brokePeace = hf;               // 보호 기간 안에 깼을 때만 화면에 알린다""",
"""    G.peace.broken[hf] = true;
    if (G.turn < G.peace.until) {                                  // 보호 기간 안에 깼을 때만 화면에 알리고 기록한다
      res.brokePeace = hf;
      logMsg('우리가 먼저 ' + facName(hf) + '군의 ' + (t.kind === 'base' ? josa(t.b.n, '을를') : '시설을') + ' 쳤다 — 이제 ' + facName(hf) + '군도 우리 거점을 칠 수 있다', t.c, t.r, f, 2);
    }""")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()
# ① STATUS 창
s = rep(s, """function todoList() {
  var f = G.player, F = G.factions[f], out = [], bs = facBases(f), us = facUnits(f), seen = {};
""", """function peaceNote() {                       // 초반 보호 풀이(창과 도움말에서 함께 쓴다)
  var P = G.peace, left = peaceLeft(), br = peaceBroken().map(function (k) { return facName(k) + '군'; });
  var h = '<div class="help">';
  if (left > 0) h += '<p><b>' + dateOfTurn(P.until - 1) + '까지(' + left + '턴 남음)</b> 다른 세력은 우리 <b>거점과 시설</b>을 먼저 치지 않습니다. ' + dateOfTurn(P.until) + '부터는 칠 수 있습니다.</p>';
  else h += '<p>초반 보호는 <b>' + dateOfTurn(P.until - 1) + '</b>에 끝났습니다.' + (G.turn < P.until + PEACE_RAMP ? ' <b>' + dateOfTurn(P.until + PEACE_RAMP - 1) + '</b>까지는 완충 기간입니다.' : '') + '</p>';
  if (br.length) h += '<p class="bad"><b>우리가 먼저 친 세력: ' + br.join(' · ') + '</b> — 이 세력은 지금도 우리 거점을 칠 수 있습니다.</p>';
  return h + '<ul><li>보호 기간은 <b>시작할 때의 병력</b>으로 정해집니다 — 1만 미만 ' + PEACE_PLAYER[0][1] + '턴(1년), 2만 미만 ' + PEACE_PLAYER[1][1] + '턴(8개월), 그 밖은 ' + PEACE_ALL + '턴(4개월).</li>' +
    '<li>지켜지는 것은 <b>거점과 시설</b>입니다. 들판의 부대끼리는 싸울 수 있고, 주인 없는 성은 누구나 차지합니다.</li>' +
    '<li><b>우리가 어떤 세력의 거점이나 시설을 먼저 치면</b>(시설에 놓는 화계 포함) 그 세력에 대해서는 보호가 풀립니다. 다른 세력과의 보호는 그대로입니다.</li>' +
    '<li>처음 ' + PEACE_ALL + '턴은 다른 세력끼리도 서로의 거점을 치지 않습니다.</li>' +
    '<li>보호가 끝난 뒤 ' + PEACE_RAMP + '턴(8개월)은 <b>완충 기간</b>입니다 — 한 번에 한 세력만 우리를 치러 오고, 우리 수비 병력의 2배(차츰 1.25배로 내려옴)를 넘게 모아야 출진합니다.</li></ul></div>';
}
function showPeaceInfo() { showDialog({ render: function () { return dlgHead('초반 보호') + '<div class="dlg-b">' + peaceNote() + '</div>'; }, on: {} }); }
function todoList() {
  var f = G.player, F = G.factions[f], out = [], bs = facBases(f), us = facUnits(f), seen = {};
  if (peaceLeft() > 0) {
    var pl = peaceLeft(), pb = peaceBroken();
    out.push({ cls: pl <= 3 ? 'warn' : 'cool peace', ic: '守', t: '초반 보호 — ' + dateOfTurn(G.peace.until - 1) + '까지 (' + pl + '턴 남음)', s: '다른 세력이 우리 거점·시설을 먼저 치지 않습니다' + (pb.length ? ' · 먼저 친 ' + pb.map(function (k) { return facName(k); }).join('·') + '군은 예외' : ' · 그동안 병력과 내정을 키우세요'), go: ['peace'], lb: '풀이', info: 1 });
  }
""")
s = rep(s, "  var need = 0; out.forEach(function (t) { if (t.cls !== 'cool' && t.go) need++; });",
           "  var need = 0; out.forEach(function (t) { if (t.cls !== 'cool' && !t.info && t.go) need++; });")
s = rep(s, "  else if (g[0] === 'end') doEndTurn();\n}", "  else if (g[0] === 'peace') showPeaceInfo();\n  else if (g[0] === 'end') doEndTurn();\n}")
s = rep(s, """        '<div class="sh-sub">' + dateStr() + ' · ' + (need ? '<b class="hi">할 일 ' + need + '건</b>' : '<b class="ok">할 일 없음</b>') + '</div>' +""",
           """        '<div class="sh-sub">' + dateStr() + ' · ' + (need ? '<b class="hi">할 일 ' + need + '건</b>' : '<b class="ok">할 일 없음</b>') + (peaceLeft() > 0 ? ' <span class="pz' + (peaceLeft() <= 3 ? ' end' : '') + '">보호 ' + peaceLeft() + '턴</span>' : '') + '</div>' +""")
# ② 대상 줄 아래 경고 + 치고 난 뒤 알림
s = rep(s, """          h += '<div class="tgt">대상 — <b>' + tn + '</b></div><div class="acts">';""",
           """          h += '<div class="tgt">대상 — <b>' + tn + '</b></div>';
          if (t.kind !== 'unit' && peaceWouldBreak(t.b.owner)) h += '<p class="note pzw"><b>초반 보호 중</b> — ' + facName(t.b.owner) + '군은 아직 우리 거점을 치지 못합니다. 우리가 먼저 치면 <b>' + facName(t.b.owner) + '군에 대한 보호가 풀려</b> 그쪽도 우리를 칠 수 있게 됩니다.</p>';
          h += '<div class="acts">';""")
s = rep(s, """  var msg = resultMsg(name, res), fellB = res.fell && t.kind === 'base' ? t.b : null;
  UI.busy = true; UI.rc = null; UI.atk = null; UI.target = null;""",
"""  var msg = resultMsg(name, res), fellB = res.fell && t.kind === 'base' ? t.b : null;
  if (res.brokePeace !== undefined) msg += ' — ' + facName(res.brokePeace) + '군에 대한 초반 보호가 풀렸습니다';
  UI.busy = true; UI.rc = null; UI.atk = null; UI.target = null;""")
# ⑤ 낡은 안내문
s = rep(s, "<b>파란 칸</b>을 누르면 이동하고, <b>적</b>을 누르면 공격·전법·계략을 고릅니다. 옅은 파란 칸은 성역의 경계 — 넘으면 이번 턴 이동이 끝납니다.</p>",
           "<b>파란 칸</b>을 누르면 이동하고, <b>적</b>을 누르면 공격·전법·계략을 고릅니다. 먼 곳은 <b>행군</b>을 누르고 목적지를 고르면 턴마다 알아서 갑니다.</p>")
# ③ 군주 고르기 · 시작 안내
s = rep(s, "    return { i: i, n: sf.n, color: sf.color, cities: sf.cities, cnt: os.length, lord: lord };",
           "    return { i: i, n: sf.n, color: sf.color, cities: sf.cities, cnt: os.length, lord: lord, troops: startTroops(i), peace: peaceFor(startTroops(i)) };")
s = rep(s, """<span class="ds" style="white-space:normal">' + FACTION_DESC[x.n] + '</span></span><span class="rt">무장<br><b>' + x.cnt + '</b></span></button>';""",
           """<span class="ds" style="white-space:normal">' + FACTION_DESC[x.n] + '</span><span class="ds fs-st">병력 <b>' + fmt(x.troops) + '</b> · 초반 보호 <b' + (x.peace > PEACE_ALL ? ' class="ok"' : '') + '>' + x.peace + '턴</b></span></span><span class="rt">무장<br><b>' + x.cnt + '</b></span></button>';""")
s = rep(s, """(st.f >= 0 ? '<b>' + info[st.f].n + '</b> · 도시 ' + info[st.f].cities.length + ' · 무장 ' + info[st.f].cnt + '명' : '세력을 누르면 선택됩니다')""",
           """(st.f >= 0 ? '<b>' + info[st.f].n + '</b> · 도시 ' + info[st.f].cities.length + ' · 무장 ' + info[st.f].cnt + '명<br>병력 ' + fmt(info[st.f].troops) + ' · 초반 보호 ' + info[st.f].peace + '턴(' + days(info[st.f].peace) + ')' : '세력을 누르면 선택됩니다<br><small>병력이 적은 세력일수록 초반 보호가 깁니다</small>')""")
s = rep(s, """        '<li>명령은 <b>행동력</b>을 씁니다. 할 일을 마치면 <b>턴 종료</b> — 열흘 동안 일어난 일을 차례로 보여 줍니다.</li>' +""",
           """        '<li>명령은 <b>행동력</b>을 씁니다. 할 일을 마치면 <b>턴 종료</b> — 열흘 동안 일어난 일을 차례로 보여 줍니다.</li>' +
        (peaceLeft() > 0 ? '<li><b>초반 보호</b>: <b>' + dateOfTurn(G.peace.until - 1) + '까지(' + peaceLeft() + '턴)</b> 다른 세력은 우리 거점과 시설을 먼저 치지 않습니다. 그동안 병력과 내정을 키우세요. 우리가 먼저 친 세력에게는 보호가 풀립니다.</li>' : '') +""")
# ④ 도움말
s = rep(s, """  '<h3>행군(선택)</h3>""", """  '<h3>초반 보호</h3><p>판을 시작하면 한동안 다른 세력이 우리 <b>거점과 시설</b>을 먼저 치지 않습니다. 기간은 <b>시작할 때의 병력</b>으로 정해집니다 — 1만 미만이면 ' + PEACE_PLAYER[0][1] + '턴(1년), 2만 미만이면 ' + PEACE_PLAYER[1][1] + '턴(8개월), 그 밖은 ' + PEACE_ALL + '턴(4개월). 남은 턴은 STATUS 창의 날짜 옆과 <b>지금 할 일</b> 맨 위에 보입니다.</p>' +
  '<ul><li>들판의 부대끼리는 싸울 수 있고, 주인 없는 성은 누구나 차지합니다.</li><li><b>우리가 어떤 세력의 거점이나 시설을 먼저 치면</b> 그 세력에 대해서는 보호가 풀립니다(치기 전에 알려 줍니다). 다른 세력과의 보호는 그대로입니다.</li><li>처음 ' + PEACE_ALL + '턴은 다른 세력끼리도 서로의 거점을 치지 않습니다.</li><li>보호가 끝난 뒤 ' + PEACE_RAMP + '턴은 완충 기간입니다 — 한 번에 한 세력만 우리를 치러 오고, 우리 수비 병력의 2배(차츰 1.25배로)를 넘게 모아야 출진합니다.</li><li>0.8까지의 저장을 이어 하는 판에는 보호가 없습니다.</li></ul>' +
  '<h3>행군(선택)</h3>""")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/style.css'; s = io.open(p, encoding='utf-8').read()
s += """
/* v0.8.1 초반 보호 */
.pz { display: inline-block; margin-left: 5px; padding: 0 6px; border: 1px solid var(--jade); border-radius: 2px; color: var(--jade); font: 700 12px var(--font-body); vertical-align: 1px; white-space: nowrap; }
.pz.end { border-color: var(--seal); color: var(--seal); }
.todo.peace .n { border-color: var(--jade); color: var(--jade); font-family: var(--font-display); }
.todo.peace b { color: var(--jade); }
.note.pzw { margin: -2px 0 8px; padding: 6px 9px; border-left: 4px solid var(--ochre); background: var(--paper-2); color: var(--ink-2); font-size: 12.5px; line-height: 1.4; }
.row .ds.fs-st { margin-top: 2px; color: var(--ink-2); }
.row .ds.fs-st b { font-weight: 800; }
.dlg-f .pv small { color: var(--dim); font-size: 12px; }
"""
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
