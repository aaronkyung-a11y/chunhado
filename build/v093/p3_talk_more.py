# v0.9.3 (3/…): 대화창 — 빠져 있던 업무 둘
#  - 거래(병량 구입·판매): 맡는 무장이 없는 명령이라 군사(없으면 군주)가 답한다.
#  - 포로 해방: 풀려나는 무장이 한마디 한다. (참수 · 철거 · 공사 중단은 전처럼 알림 줄)
#  규칙(core.js)은 건드리지 않는다.
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)

p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "  advisor:  { W: ['머리 쓰는 일이라… 힘껏 해 보겠소.'], C: ['미력하나마 지혜를 다하겠습니다.', '삼가 명을 받들겠습니다.'], L: ['…'] }\n};",
           "  advisor:  { W: ['머리 쓰는 일이라… 힘껏 해 보겠소.'], C: ['미력하나마 지혜를 다하겠습니다.', '삼가 명을 받들겠습니다.'], L: ['…'] },\n"
           "  trade:    { W: ['셈을 마쳤소.'], C: ['거래를 마쳤습니다.', '상인들과 셈을 마쳤습니다.'], L: ['거래를 마쳤다.'] },\n"
           "  released: { W: ['이 은혜는 잊지 않겠소.'], C: ['베푸신 은혜, 잊지 않겠습니다.'], L: ['…이 일은 기억해 두겠소.'] }\n};")
# 거래: 군사(없으면 군주)가 답한다
s = rep(s, "done(r, r.ok ? (st.dir === 'buy' ? '병량 +' : '금 +') + fmt(r.n) : '', 'coin'); }",
           "done(r, r.ok ? (st.dir === 'buy' ? '병량 +' + fmt(r.n) + ' (금 −' + fmt(Math.floor(st.v)) + ')' : '금 +' + fmt(r.n) + ' (병량 −' + fmt(Math.floor(st.v) * 6) + ')') : '', 'coin', facAdv(G.player) || off(G.factions[G.player].lord), 'trade'); }")
# 포로 해방: 풀려나는 무장이 한마디
s = rep(s, "cmdCaptive(b, o.id, 'release'); toast(josa(o.n, '을를') + ' 풀어 주었습니다');",
           "var say0 = sayLine(o, 'released'); cmdCaptive(b, o.id, 'release'); talk(o, say0, josa(o.n, '을를') + ' 풀어 주었습니다');")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
