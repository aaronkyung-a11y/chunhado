# v0.9.2 글 덜어내기(5/…): 마무리
#  - 판 번호 v0.9.2
#  - 거점 창의 무기 줄: 충차가 0대면 적지 않는다(그 한 칸 때문에 줄이 둘로 넘어갔다)
#  - STATUS 창 '지금 할 일' 위의 빈 틈을 줄인다
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)
p = 'src/data.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "var GAME_VERSION = 'v0.9.1';", "var GAME_VERSION = 'v0.9.2';")
io.open(p, 'w', encoding='utf-8').write(s)
p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, """'</b></span><span>' + ico('ram') + '충차 <b>' + b.w.ram + '</b></span></div>';""", """'</b></span>' + (b.w.ram ? '<span>' + ico('ram') + '충차 <b>' + b.w.ram + '</b></span>' : '') + '</div>';""")
io.open(p, 'w', encoding='utf-8').write(s)
p = 'src/style.css'; s = io.open(p, encoding='utf-8').read()
s += """
/* ---- v0.9.2 마무리 ---- */
#sheet.home .sh-body > .sec:first-child { margin-top: 4px; }
.wp { flex-wrap: nowrap; overflow: hidden; gap: 4px 10px; }
"""
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
