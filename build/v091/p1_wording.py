# v0.9.1 표기: "보호턴이라고 쓰지 말고.." (2026-11-20 15:20)
#  처음부터 있던 약속(v0.1 피드백): "1턴을 10일로 해서 계산하고, '몇 일분' 이런 식으로 … 10턴분 이런 식으로 하지 말고". 0.8.1~0.9 에서 내가 '보호 24턴', '혼란 2턴', '완충 24턴'처럼 다시 턴으로 적었다.
#  기간은 날짜·일수·개월로 적는다. '이번 턴', '다음 턴', '한 턴에 한 번'처럼 차례를 가리키는 말은 그대로 둔다.
#   - 초반 보호: STATUS 창의 표 "[8월 하순까지 보호]"(30일 이하로 남으면 "[보호 30일 남음]"), 줄 "…까지 (240일 남음)", 군주 고르기 "초반 보호 8개월", 풀이·도움말·알림
#   - 상태 이상: 지도 딱지 [혼란 20일], 창의 [혼란 20일] · "앞으로 20일", 알림 "혼란 20일", 불 "30일 더 탑니다"
#   - 전부터 있던 것도 함께: 전법·계략·특기 풀이의 (1턴)·(2턴)·2턴간·1턴 더
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)
p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "function days(turns) { return fmt(turns * 10) + '일'; }",
"""function days(turns) { return fmt(turns * 10) + '일'; }
function months(turns) { var m = turns / 3; return turns % 3 ? days(turns) : (m % 12 ? m + '개월' : (m / 12) + '년'); }   // 3턴 = 한 달. 달로 나누어떨어지지 않으면 일수로
function shortDate(t) { var d = dateOfTurn(t), y = G.year + '년 '; return d.indexOf(y) === 0 ? d.slice(y.length) : d; }      // 올해면 해를 뺀다""")
# 상태 이상
s = rep(s, "  if (u.status) h += '<b class=\"stc st-' + u.status + '\">' + statusName(u.status) + (n > 0 ? ' ' + n + '턴' : ' · 곧 풀림') + '</b>';",
           "  if (u.status) h += '<b class=\"stc st-' + u.status + '\">' + statusName(u.status) + (n > 0 ? ' ' + days(n) : ' · 곧 풀림') + '</b>';")
s = rep(s, "return n === 1 ? '이번 턴만 — 다음 턴에 풀립니다' : '이번 턴 포함 ' + n + '턴';", "return n === 1 ? '이번 턴만 — 다음 턴에 풀립니다' : '이번 턴 포함 ' + days(n);")
s = rep(s, "  return '앞으로 ' + n + '턴';", "  return '앞으로 ' + days(n);")
s = rep(s, "(ft <= 1 ? '이번 턴이 지나면 꺼집니다' : '불은 ' + ft + '턴 더 탑니다')", "(ft <= 1 ? '이번 턴이 지나면 꺼집니다' : '불은 ' + days(ft) + ' 더 탑니다')")
s = rep(s, "(res.st ? ' — ' + statusName(res.st) + ' ' + res.stN + '턴' : '') + (res.chain ? ' · 연환!' : '');", "(res.st ? ' — ' + statusName(res.st) + ' ' + days(res.stN) : '') + (res.chain ? ' · 연환!' : '');")
s = rep(s, "(res.selfSt ? ' 우리 부대가 ' + statusName(res.selfSt) + ' ' + res.selfStN + '턴' : '')", "(res.selfSt ? ' 우리 부대가 ' + statusName(res.selfSt) + ' ' + days(res.selfStN) : '')")
s = rep(s, "    if (res.confused) msg += ' · 혼란 ' + (res.stN || 1) + '턴';", "    if (res.confused) msg += ' · 혼란 ' + days(res.stN || 1);")
s = rep(s, "floatText(res.c, res.r, statusName(res.st) + ' ' + res.stN + '턴', C_PLOY, 420, false, 26);", "floatText(res.c, res.r, statusName(res.st) + ' ' + days(res.stN), C_PLOY, 420, false, 26);")
s = rep(s, "floatText(res.ac, res.ar, statusName(res.selfSt) + ' ' + res.selfStN + '턴', C_PLOY, 640, false, 26);", "floatText(res.ac, res.ar, statusName(res.selfSt) + ' ' + days(res.selfStN), C_PLOY, 640, false, 26);")
s = rep(s, "    if (res.confused) fxs.push('혼란 ' + (res.stN || 1) + '턴');", "    if (res.confused) fxs.push('혼란 ' + days(res.stN || 1));")
# 초반 보호
s = rep(s, "'까지(' + left + '턴 남음)</b> 다른 세력은", "'까지(' + days(left) + ' 남음)</b> 다른 세력은")
s = rep(s, "— 1만 미만 ' + PEACE_PLAYER[0][1] + '턴(1년), 2만 미만 ' + PEACE_PLAYER[1][1] + '턴(8개월), 그 밖은 ' + PEACE_ALL + '턴(4개월).</li>' +",
           "— 1만 미만 ' + months(PEACE_PLAYER[0][1]) + ', 2만 미만 ' + months(PEACE_PLAYER[1][1]) + ', 그 밖은 ' + months(PEACE_ALL) + '.</li>' +")
s = rep(s, "    '<li>처음 ' + PEACE_ALL + '턴은 다른 세력끼리도 서로의 거점을 치지 않습니다.</li>' +", "    '<li>처음 ' + months(PEACE_ALL) + '은 다른 세력끼리도 서로의 거점을 치지 않습니다.</li>' +")
s = rep(s, "    '<li>보호가 끝난 뒤 ' + PEACE_RAMP + '턴(8개월)은 <b>완충 기간</b>입니다", "    '<li>보호가 끝난 뒤 ' + months(PEACE_RAMP) + '은 <b>완충 기간</b>입니다")
s = rep(s, "t: '초반 보호 — ' + dateOfTurn(G.peace.until - 1) + '까지 (' + pl + '턴 남음)',", "t: '초반 보호 — ' + dateOfTurn(G.peace.until - 1) + '까지 (' + days(pl) + ' 남음)',")
s = rep(s, "(peaceLeft() > 0 ? ' <span class=\"pz' + (peaceLeft() <= 3 ? ' end' : '') + '\">보호 ' + peaceLeft() + '턴</span>' : '')",
           "(peaceLeft() > 0 ? ' <span class=\"pz' + (peaceLeft() <= 3 ? ' end' : '') + '\">' + (peaceLeft() <= 3 ? '보호 ' + days(peaceLeft()) + ' 남음' : shortDate(G.peace.until - 1) + '까지 보호') + '</span>' : '')")
s = rep(s, "'>' + x.peace + '턴</b></span></span><span class=\"rt\">무장<b", "'>' + months(x.peace) + '</b></span></span><span class=\"rt\">무장<b")
s = rep(s, "' · 초반 보호 ' + info[st.f].peace + '턴(' + days(info[st.f].peace) + ')' :", "' · 초반 보호 ' + months(info[st.f].peace) + '(' + dateOfTurn(info[st.f].peace) + '까지)' :")
s = rep(s, "<b>' + dateOfTurn(G.peace.until - 1) + '까지(' + peaceLeft() + '턴)</b> 다른 세력은 우리 거점과 시설을 먼저 치지 않습니다. 그동안 병력과 내정을 키우세요.",
           "<b>' + dateOfTurn(G.peace.until - 1) + '까지(' + months(peaceLeft()) + ')</b> 다른 세력은 우리 거점과 시설을 먼저 치지 않습니다. 그동안 병력과 내정을 키우세요.")
# 도움말
s = rep(s, "— 1만 미만이면 ' + PEACE_PLAYER[0][1] + '턴(1년), 2만 미만이면 ' + PEACE_PLAYER[1][1] + '턴(8개월), 그 밖은 ' + PEACE_ALL + '턴(4개월). 남은 턴은 STATUS 창의 날짜 옆과",
           "— 1만 미만이면 ' + months(PEACE_PLAYER[0][1]) + ', 2만 미만이면 ' + months(PEACE_PLAYER[1][1]) + ', 그 밖은 ' + months(PEACE_ALL) + '. 언제까지인지는 STATUS 창의 날짜 옆과")
s = rep(s, "<li>처음 ' + PEACE_ALL + '턴은 다른 세력끼리도 서로의 거점을 치지 않습니다.</li><li>보호가 끝난 뒤 ' + PEACE_RAMP + '턴은 완충 기간입니다",
           "<li>처음 ' + months(PEACE_ALL) + '은 다른 세력끼리도 서로의 거점을 치지 않습니다.</li><li>보호가 끝난 뒤 ' + months(PEACE_RAMP) + '은 완충 기간입니다")
s = rep(s, "딱지의 숫자는 <b>남은 턴</b>입니다.", "딱지에 <b>남은 날수</b>가 적힙니다.")
s = rep(s, "교란으로 걸면 2턴, 전법(나선첨 등)으로 걸면 1턴입니다.</li><li><b>위보</b>: 2턴 동안 명령을 듣지 않고", "교란으로 걸면 20일, 전법(나선첨 등)으로 걸면 10일입니다.</li><li><b>위보</b>: 20일 동안 명령을 듣지 않고")
s = rep(s, "부대를 누르면 창 맨 위에 걸린 상태·남은 턴·효과가 적혀 있습니다.", "부대를 누르면 창 맨 위에 걸린 상태·남은 날수·효과가 적혀 있습니다.")
s = rep(s, "가까운 성끼리는 20일(2턴), 대개는 30일 넘게 걸립니다.", "가까운 성끼리는 20일, 대개는 30일 넘게 걸립니다.")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "logMsg('초반 보호가 3턴 남았습니다 — '", "logMsg('초반 보호가 30일 남았습니다 — '")
s = rep(s, "text: '<b>초반 보호가 3턴 남았습니다</b> — '", "text: '<b>초반 보호가 30일 남았습니다</b> — '")
s = rep(s, "(u.stT > 0 ? ' (이번 턴 포함 ' + (u.stT + 1) + '턴)' : ' (다음 턴에 풀림)')", "(u.stT > 0 ? ' (이번 턴 포함 ' + (u.stT + 1) * 10 + '일)' : ' (다음 턴에 풀림)')")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/ai.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "(res.success && res.st ? ' — ' + statusName(res.st) + ' ' + res.stN + '턴' : '');", "(res.success && res.st ? ' — ' + statusName(res.st) + ' ' + res.stN * 10 + '일' : '');")
s = rep(s, "(res.confused ? ' — 혼란 ' + res.stN + '턴' : '');", "(res.confused ? ' — 혼란 ' + res.stN * 10 + '일' : '');")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/ui3d.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "  if (u.status) segs.push({ t: statusName(u.status) + (n > 0 ? ' ' + n : ''), bg: ST_COL[u.status] || ST_COL.confuse });",
           "  if (u.status) segs.push({ t: statusName(u.status) + (n > 0 ? ' ' + n * 10 + '일' : ''), bg: ST_COL[u.status] || ST_COL.confuse });      // 남은 날수(1턴 = 10일)")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/data.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "fx: '적을 혼란에 빠뜨린다(1턴)'", "fx: '적을 혼란에 빠뜨린다(10일)'")
s = rep(s, "fx: '적이 선 칸에 불(2턴)', gfx: '불이 3턴 타고 적 기력 -10', desc: '불화살. 적이 선 칸에 불을 붙인다(2턴). 대성공이면 3턴 타고 적 기력 -10.'",
           "fx: '적이 선 칸에 불(20일)', gfx: '불이 30일 타고 적 기력 -10', desc: '불화살. 적이 선 칸에 불을 붙인다(20일). 대성공이면 30일 타고 적 기력 -10.'")
s = rep(s, "desc: '적 부대를 혼란시켜 2턴간 행동하지 못하게 한다.'", "desc: '적 부대를 혼란시켜 20일 동안 행동하지 못하게 한다.'")
s = rep(s, "desc: '거짓 소식으로 적 부대를 2턴간 본거지 쪽으로 물러나게 한다.'", "desc: '거짓 소식으로 적 부대를 20일 동안 본거지 쪽으로 물러나게 한다.'")
s = rep(s, "'심모': '계략 효과가 1턴 더 지속되고 화계 피해 +50%.',", "'심모': '계략 효과가 10일 더 이어지고 화계 피해 +50%.',")
s = rep(s, "var GAME_VERSION = 'v0.9';", "var GAME_VERSION = 'v0.9.1';")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
