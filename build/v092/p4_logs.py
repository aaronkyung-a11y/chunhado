# v0.9.2 글 덜어내기(4/…): 기록·알림의 긴 문장
#  '지난 열흘의 일'과 잠깐 뜨는 알림에서 뒤에 붙은 설명을 뗀다(규칙은 그대로 — 문구만).
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)
p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "logMsg('초반 보호가 30일 남았습니다 — ' + dateOfTurn(G.peace.until) + '부터는 다른 세력이 우리 거점을 칠 수 있습니다', cap.c, cap.r, f, 2);", "logMsg('초반 보호가 30일 남았습니다', cap.c, cap.r, f, 2);")
s = rep(s, "text: '<b>초반 보호가 30일 남았습니다</b> — ' + dateOfTurn(G.peace.until) + '부터는 다른 세력이 우리 거점을 칠 수 있습니다' });", "text: '<b>초반 보호가 30일 남았습니다</b>' });")
s = rep(s, "logMsg('초반 보호가 끝났습니다 — 이제 다른 세력이 우리 거점을 칠 수 있습니다', cap.c, cap.r, f, 2);", "logMsg('초반 보호가 끝났습니다', cap.c, cap.r, f, 2);")
s = rep(s, "text: '<b>초반 보호가 끝났습니다</b> — 이제 다른 세력이 우리 거점을 칠 수 있습니다' });", "text: '<b>초반 보호가 끝났습니다</b>' });")
s = rep(s, "logMsg(uName(u) + ' ' + statusName(u.status) + '에서 벗어남 — 다시 명령을 받습니다', u.c, u.r, f, 1);", "logMsg(uName(u) + ' ' + statusName(u.status) + '에서 벗어남', u.c, u.r, f, 1);")
s = rep(s, "logMsg('우리가 먼저 ' + facName(hf) + '군의 ' + (t.kind === 'base' ? josa(t.b.n, '을를') : '시설을') + ' 쳤다 — 이제 ' + facName(hf) + '군도 우리 거점을 칠 수 있다', t.c, t.r, f, 2);",
           "logMsg(facName(hf) + '군과의 보호가 풀렸다 — 우리가 먼저 ' + (t.kind === 'base' ? josa(t.b.n, '을를') : '시설을') + ' 침', t.c, t.r, f, 2);")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "msg += ' — ' + facName(res.brokePeace) + '군에 대한 초반 보호가 풀렸습니다';", "msg += ' — ' + facName(res.brokePeace) + '군과의 보호가 풀림';")
s = rep(s, "toast('출진한 턴에는 거점과 시설을 칠 수 없습니다 — 다음 턴에 공격하세요', 2800)", "toast('출진한 턴에는 거점을 칠 수 없습니다', 2400)")
s = rep(s, "toast('닿지 않습니다 — 먼저 가까이 이동하세요')", "toast('닿지 않습니다')")
s = rep(s, "toast('닿지 않습니다 — 이번 턴에는 파란 칸까지만 갈 수 있습니다', 2200)", "toast('닿지 않습니다 — 파란 칸까지만', 2000)")
s = rep(s, "'바로 옆에 같은 종류의 완성된 시설이 있어야 합니다'", "'옆에 같은 시설이 있어야 합니다'")
s = rep(s, "'충차가 없습니다 — 공방에서 생산하세요'", "'충차가 없습니다'")
s = rep(s, "toast('명령을 기다리는 부대가 ' + left + '개 있습니다 — 한 번 더 누르면 턴을 넘깁니다', 3500)", "toast('명령 대기 ' + left + '부대 — 한 번 더 누르면 턴 종료', 3000)")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
