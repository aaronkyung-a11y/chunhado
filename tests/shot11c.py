# v0.11 화면 찍기(군사의 헌책 · 탐색 조언 · 보급):  python3 tests/shot11c.py [세력=0]  → tests/shots24/
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import taphex, tapsel
B.SHOTS = os.path.join(B.ROOT, 'shots24')
os.makedirs(B.SHOTS, exist_ok=True)
FAC = int(sys.argv[1]) if len(sys.argv) > 1 else 0
W, H, D = 396, 859, 2
def steps(pg):
    tapsel(pg, '#tNew'); pg.wait_for_timeout(300)
    tapsel(pg, '#modal .row', FAC); tapsel(pg, '#modal [data-a=go]'); pg.wait_for_timeout(600)
    tapsel(pg, '#modal [data-a=close]'); pg.wait_for_timeout(1500)
    print('talk:', pg.evaluate('document.getElementById("talk") ? document.getElementById("talk").innerText.replace(/\\n/g, " / ") : "-"'))
    B.shot(pg, 'h%02d_home' % FAC, 300)
    pg.evaluate('talkHide()')
    def say(): return pg.evaluate('(() => { var e = document.querySelector("#sheet .hm-say .tx"); return e ? e.innerText.replace(/\\n/g, " | ") : "-"; })()')
    print('1:', say())
    n = 0
    while pg.evaluate('!!document.querySelector("#sheet [data-a=advnext]")') and n < 7:
        tapsel(pg, '#sheet [data-a=advnext]'); pg.wait_for_timeout(250); n += 1
        print('%d:' % (n + 1), say())
        if n == 1: B.shot(pg, 'h%02d_next' % FAC, 200)
    print('todo:', pg.evaluate('Array.from(document.querySelectorAll("#sheet .todo")).map(function (t) { return t.querySelector(".mid").innerText.replace(/\\n/g, " — "); })'))
    # 헌책의 전부(지력을 바꿔 가며 글을 본다)
    print(pg.evaluate('''(() => { var out = [], A = facAdv(G.player), keep = A.int; [100, 70, 50].forEach(function (iq) { A.int = iq; var cs = counsel(G.player); out.push("— 지력 " + iq + " (" + cs.list.length + "건)"); cs.list.forEach(function (c) { var t = counselText(c); out.push("  [" + c.kind + " " + Math.round(c.w) + "] " + t.say + "  «" + t.tip.replace(/<[^>]+>/g, "") + "»"); }); }); A.int = keep; return out.join("\\n"); })()'''))
    # 탐색
    b = pg.evaluate('(() => { var b = facCities(G.player)[0]; selectBase(b, true, "men"); return b.n; })()'); pg.wait_for_timeout(500)
    tapsel(pg, '#sheet [data-a=search]'); pg.wait_for_timeout(500); tapsel(pg, '#modal [data-a=auto]'); pg.wait_for_timeout(400); B.shot(pg, 'h%02d_search' % FAC, 300)
    print('search say:', pg.evaluate('(document.querySelector("#modal .pksay") || {innerText: "-"}).innerText.replace(/\\n/g, " | ")'), '| rt:', pg.evaluate('Array.from(document.querySelectorAll("#modal .tr .c-x")).map(function (x) { return x.innerText; }).join(",")'))
    tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(900); B.shot(pg, 'h%02d_search_done' % FAC, 300)
    print('result:', pg.evaluate('document.getElementById("talk") ? document.getElementById("talk").innerText.replace(/\\n/g, " / ") : "-"'), '| toast:', pg.evaluate('document.getElementById("toast").textContent'))
    print('errors:', [e for e in B.errors if 'GPU stall' not in e and 'GL Driver' not in e and 'ERR_FILE_NOT_FOUND' not in e])
B.run(steps, W, H, D)
