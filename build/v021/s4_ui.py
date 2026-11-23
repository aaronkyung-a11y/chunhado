# v0.21 (4) 화면 손질 — 무장 이동의 인원 · 등용의 말 · 내구의 회복 · 성공/실패의 소리 · 도움말 · 판 번호
#   ⑥ "무장 이동이 최대 6명일 이유는 없다." → 몇 명이든 한 번에 보낸다([모두] 단추).
#   ⑨ "어떤 일이 성공하거나 실패했을 때 가벼운 효과음이 있으면 좋겠어. 예를들어 등용에 성공한 음과 실패한 음을 구분한다던가"
#      → 맑게 올라가는 두 음(good) · 낮게 내려가는 두 음(bad). 만든 소리(받아 온 파일 없음). 등용 · 설전 등용 · 탐색 · 외교(동맹 · 정전 · 출병 요청).
import io, os
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)

s = rd('src/data.js')
s = rep(s, "var GAME_VERSION = 'v0.20';", "var GAME_VERSION = 'v0.21';")
wr('src/data.js', s)

s = rd('src/ui3d.js')
s = rep(s, "function sfxSyn(kind) {                                       // 만든 소리(대신 쓰는 것)", """/* v0.21 뜯는 현 한 음(성공 · 실패의 가벼운 소리): 빠르게 서고 길게 스러지는 음 + 옅은 배음 */
function pluck(t, freq, dur, vol) {
  var out = (typeof sndBus === 'function') ? sndBus() : AC.destination;
  [[1, 1, 'triangle'], [2, 0.28, 'sine'], [3, 0.10, 'sine']].forEach(function (h) {
    var o = AC.createOscillator(); o.type = h[2]; o.frequency.setValueAtTime(freq * h[0], t);
    var g = AC.createGain(); g.gain.setValueAtTime(0.0001, t); g.gain.linearRampToValueAtTime(vol * h[1], t + 0.008); g.gain.exponentialRampToValueAtTime(0.0008, t + dur / h[0]);
    o.connect(g); g.connect(out); o.start(t); o.stop(t + dur / h[0] + 0.03);
  });
}
function sfxSyn(kind) {                                       // 만든 소리(대신 쓰는 것)""")
s = rep(s, "  else if (kind === 'fail') nz(t, 0.2, 'lowpass', 240, 0.8, 0.2);\n}",
           "  else if (kind === 'fail') nz(t, 0.2, 'lowpass', 240, 0.8, 0.2);\n  else if (kind === 'good') { pluck(t, 783.99, 0.55, 0.16); pluck(t + 0.12, 1174.66, 0.85, 0.18); }                     // 솔 → 레: 맑게 올라간다\n  else if (kind === 'bad') { pluck(t, 293.66, 0.42, 0.17); pluck(t + 0.15, 220.0, 0.70, 0.17); nz(t, 0.09, 'lowpass', 280, 0.7, 0.07); }   // 레 → 라: 낮게 내려간다\n}")
wr('src/ui3d.js', s)

s = rd('src/ui_panels.js')
# ⑥ 무장 이동: 인원 제한 없음
s = rep(s, "pickOfficers({ keep: true, title: '이동 — 보낼 무장', list: idleOfficers(b), max: 6, key:", "pickOfficers({ keep: true, title: '이동 — 보낼 무장', list: idleOfficers(b), max: 99, all: true, key:")
s = rep(s, "(max > 1 ? '무장을 고르세요 (최대 ' + max + '명)' : '무장을 고르세요')", "(max > 1 ? (max >= 99 ? '무장을 고르세요 (몇 명이든)' : '무장을 고르세요 (최대 ' + max + '명)') : '무장을 고르세요')")
s = rep(s, "        (opts.auto ? '<button class=\"btn auto\" type=\"button\" data-a=\"auto\">자동</button>' : '') +\n        (opts.alt ?",
           "        (opts.auto ? '<button class=\"btn auto\" type=\"button\" data-a=\"auto\">자동</button>' : '') +\n        (opts.all && opts.list.length > 1 ? '<button class=\"btn auto\" type=\"button\" data-a=\"all\">' + (sel.length === opts.list.length ? '모두 풀기' : '모두') + '</button>' : '') +      // v0.21\n        (opts.alt ?")
s = rep(s, "      sort: function (el) { var k = el.getAttribute('data-v'); if (sortK === k) sortDir = -sortDir; else { sortK = k; sortDir = -1; } refreshDialog(); },\n      pick: function (el) {",
           "      sort: function (el) { var k = el.getAttribute('data-v'); if (sortK === k) sortDir = -sortDir; else { sortK = k; sortDir = -1; } refreshDialog(); },\n      all: function () { sel = sel.length === opts.list.length ? [] : sorted().map(function (o) { return o.id; }); refreshDialog(); },\n      pick: function (el) {")
# ⑤ ③ 등용의 말
s = rep(s, "    if (askWait(t)) return t.st === 'active' ? '다음 달에 다시' : '다음 턴에 다시';\n    if (t.st === 'active' && bondOf(t)) return '주군과 ' + bondOf(t);",
           "    if (askWait(t)) return '다음 달에 다시';\n    if (t.st === 'active' && bondOf(t)) return '주군과 ' + bondOf(t);\n    if (t.st === 'active' && t.loy >= 100) return '충성 100';")
s = rep(s, "tieSub(t, true)) }, sopt())); }\n        h += '</div>';\n      }", "tieSub(t, true)) }, sopt())); }\n        h += '</div><p class=\"note\">한 사람에게 <b>한 달에 한 번</b> 권할 수 있습니다</p>';\n      }")
s = rep(s, "' — 충성 +' + POACH.up + ' · 다음 달에 다시 권할 수 있습니다' : ' — 다음 턴에 다시 권할 수 있습니다')", "' — 충성 +' + POACH.up + ' · 다음 달에 다시 권할 수 있습니다' : ' — 다음 달에 다시 권할 수 있습니다')")
# ⑨ 성공 · 실패의 소리
s = rep(s, "var a0 = recruitAdvice(b, os[0], t), r = cmdRecruit(b, os[0].id, t.id); if (r.ok && r.joined) sfx('cheer');",
           "var a0 = recruitAdvice(b, os[0], t), r = cmdRecruit(b, os[0].id, t.id); if (r.ok && r.joined) { sfx('good'); sfx('cheer'); } else if (r.ok) sfx('bad');")
s = rep(s, "      if (r && r.ok && r.joined) { sfx('cheer'); talk(t, sayLine(t, 'joined', G.factions[G.player].name), josa(t.n, '이가') + ' 합류했습니다!', 3000); }\n      refreshSheet(); afterAction();",
           "      if (r && r.ok && r.joined) { sfx('good'); sfx('cheer'); talk(t, sayLine(t, 'joined', G.factions[G.player].name), josa(t.n, '이가') + ' 합류했습니다!', 3000); }\n      else if (r && r.ok) sfx('bad');\n      refreshSheet(); afterAction();")
s = rep(s, "      if (r.found !== undefined) { sfx('drum'); done(r,", "      if (r.found !== undefined) { sfx('good'); done(r,")
s = rep(s, "      else if (r.gold) done(r, '금 ' + josa(String(r.gold), '을를') + ' 찾았습니다' + tail, '', os[0], 'gold');\n      else done(r, '아무것도 찾지 못했습니다' + tail, '', os[0], 'nothing');",
           "      else if (r.gold) done(r, '금 ' + josa(String(r.gold), '을를') + ' 찾았습니다' + tail, 'good', os[0], 'gold');\n      else done(r, '아무것도 찾지 못했습니다' + tail, 'bad', os[0], 'nothing');")
s = rep(s, "            if (r.success) { sfx('gong'); talk(L, sayLine(L, 'aimYes'),", "            if (r.success) { sfx('gong'); sfx('good'); talk(L, sayLine(L, 'aimYes'),")
s = rep(s, "            else { sfx('fail'); talk(L, sayLine(L, 'aimNo'),", "            else { sfx('bad'); talk(L, sayLine(L, 'aimNo'),")
s = rep(s, "  if (r.success) { sfx('gong'); sfx('cheerlate'); talk(L, sayLine(L, 'dipYes'),", "  if (r.success) { sfx('gong'); sfx('good'); sfx('cheerlate'); talk(L, sayLine(L, 'dipYes'),")
s = rep(s, "  else { sfx('fail'); talk(L, sayLine(L, 'dipNo'),", "  else { sfx('bad'); talk(L, sayLine(L, 'dipNo'),")
s = rep(s, "    function () { if (r && r.ok && r.success) sfx('cheer'); if (MODAL) refreshDialog();", "    function () { if (r && r.ok && r.success) { sfx('good'); sfx('cheer'); } else if (r && r.ok) sfx('bad'); if (MODAL) refreshDialog();")
# ⑧ 내구: 다음 턴에 돌아올 양 / 맞아서 멈춘 것
s = rep(s, "        '<div><span>' + ico('dur') + '내구</span><b>' + fmt(b.dur) + '</b></div></div>';",
           "        '<div><span>' + ico('dur') + '내구</span><b' + (b.dur < b.maxDur * 0.5 ? ' class=\"bad\"' : '') + '>' + fmt(b.dur) + (b.owner >= 0 && b.dur < b.maxDur ? (durHealAt(b, G.turn + 1) ? ' <small>+' + fmt(durHealAt(b, G.turn + 1)) + '</small>' : ' <small class=\"bad\">회복 멈춤</small>') : '') + '</b></div></div>';")
# 도움말
s = rep(s, "  '<h3>초반 보호</h3><p>판을 시작하면 한동안 다른 세력이 ", """  '<h3>관문과 능선</h3><p>관문(호관 · 호로관 · 함곡관 · 동관 · 무관 · 양평관 · 검각) 양옆으로는 <b>능선</b>이 이어집니다(지도에 좁은 산줄기로 그려져 있습니다). 능선은 넘을 수 없습니다 — 능선 너머의 칸은 바로 옆이어도 갈 수 없고 맞붙어 칠 수 없습니다(노병은 두 칸 거리에서 넘겨 쏘고, 계략은 넘어갑니다). <b>내 관문은 그냥 지나갑니다</b>(관문 칸에 서면 입성). <b>남의 관문은 빼앗아야</b> 지나고, 주인 없는 관문은 들어가면 내 것이 됩니다. 능선은 관문에서 열 몇 칸까지 이어지므로 멀리 돌아가는 길이 남아 있는 곳도 있습니다(호로관은 보병으로 관문 길 32일 · 돌아가면 59일쯤). 호로관은 낙양의 동쪽을 모두 막습니다 — 허창에서 낙양으로 가는 길도 호로관을 지납니다. 장안에서 무관으로 가는 길은 동관을, 한중에서 검각으로 가는 길은 양평관을 지납니다.</p>' +
  '<h3>성의 내구</h3><p>성과 관문의 내구는 <b>맞지 않은 지 ' + days(DUR_HEAL.wait) + '이 지나면</b> 턴마다 최대 내구의 ' + DUR_HEAL.pct + '%씩 저절로 돌아옵니다(대도시 ' + Math.round(MAX_DUR.L * DUR_HEAL.pct / 100) + ' · 관문 ' + Math.round(MAX_DUR.G * DUR_HEAL.pct / 100) + '). 공격을 받는 동안에는 돌아오지 않습니다 — 거점 창의 내구 옆에 다음 턴에 돌아올 양(+숫자)이나 <b>회복 멈춤</b>이 적혀 있습니다.</p>' +
  '<h3>등용</h3><p>재야 · 포로 · 이웃한 다른 세력의 무장 모두 <b>한 사람에게 한 달에 한 번</b> 권할 수 있습니다. 응할지는 달마다 한 번 정해집니다(같은 달에는 누가 권해도 군사의 ○×가 같습니다 — 권하는 무장에 따라 가능성은 달라집니다). <b>충성 100</b>인 무장은 누가 권해도 응하지 않습니다.</p>' +
  '<h3>초반 보호</h3><p>판을 시작하면 한동안 다른 세력이 """)
wr('src/ui_panels.js', s)
print('s4 ok')
