# v0.10.1 화면 찍기 — 세이브 칸:  python3 tests/shot101b.py [w=396] [h=859] [dpr=2]   → tests/shots22/
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import taphex, tapsel
B.SHOTS = os.path.join(B.ROOT, 'shots22')
os.makedirs(B.SHOTS, exist_ok=True)
W = int(sys.argv[1]) if len(sys.argv) > 1 else 396
H = int(sys.argv[2]) if len(sys.argv) > 2 else 859
D = int(sys.argv[3]) if len(sys.argv) > 3 else 2
ST = '''(() => { var o = {}; slotIds().forEach(function (id) { var m = slotInfo(id); o[id] = m ? (m.bad ? "bad" : m.f + " " + m.d + " " + m.n + "성 t" + (m.t ? 1 : 0)) : null; }); return o; })()'''
def steps(pg):
    pg.evaluate('localStorage.clear()'); pg.reload(); pg.wait_for_function('window.R3 && R3.ready', timeout=60000); pg.wait_for_timeout(600)
    B.shot(pg, 's00_title_empty', 300)
    print('title', pg.evaluate('[$("tCont").disabled, $("tLoad").disabled]'))
    tapsel(pg, '#tNew'); pg.wait_for_timeout(300)
    tapsel(pg, '#modal .row', 13); tapsel(pg, '#modal [data-a=go]'); pg.wait_for_timeout(600)
    tapsel(pg, '#modal [data-a=close]'); pg.wait_for_timeout(1200); pg.evaluate('talkHide()')
    print('after new', pg.evaluate(ST))
    tapsel(pg, '#btnMenu'); pg.wait_for_timeout(300); B.shot(pg, 's01_menu', 200)
    tapsel(pg, '#modal [data-a=save]'); pg.wait_for_timeout(400); B.shot(pg, 's02_save_empty', 200)
    tapsel(pg, '#modal [data-a=ssave]', 0); pg.wait_for_timeout(500); B.shot(pg, 's03_saved1', 200)
    print('toast', pg.evaluate('$("toast").textContent'), pg.evaluate(ST))
    tapsel(pg, '#modal [data-a=ssave]', 0); pg.wait_for_timeout(400); B.shot(pg, 's04_overwrite_arm', 200)
    print('arm', pg.evaluate('document.querySelector("#modal [data-a=ssave]").textContent'))
    tapsel(pg, '#modal [data-a=smode][data-v=load]'); pg.wait_for_timeout(400); B.shot(pg, 's05_load_list', 200)
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(300)
    # 한 턴 넘기고 처음으로 → 새 게임(원소)
    pg.evaluate('(() => { endTurn(); saveGame(); refreshHud(); })()'); pg.wait_for_timeout(300)
    tapsel(pg, '#btnMenu'); pg.wait_for_timeout(300); tapsel(pg, '#modal [data-a=title]'); pg.wait_for_timeout(600); B.shot(pg, 's06_title', 300)
    print('title', pg.evaluate('[$("tCont").disabled, $("tLoad").disabled]'))
    tapsel(pg, '#tNew'); pg.wait_for_timeout(300)
    tapsel(pg, '#modal .row', 4); tapsel(pg, '#modal [data-a=go]'); pg.wait_for_timeout(600)
    tapsel(pg, '#modal [data-a=close]'); pg.wait_for_timeout(1200); pg.evaluate('talkHide()')
    print('after new2', pg.evaluate(ST))
    tapsel(pg, '#btnMenu'); pg.wait_for_timeout(300); tapsel(pg, '#modal [data-a=load]'); pg.wait_for_timeout(400); B.shot(pg, 's07_load_three', 200)
    tapsel(pg, '#modal [data-slot=s1] [data-a=sload]'); pg.wait_for_timeout(1500); B.shot(pg, 's08_loaded1', 200)
    print('loaded', pg.evaluate('[G.factions[G.player].name, dateStr(), $("toast").textContent]'), pg.evaluate(ST))
    tapsel(pg, '#btnMenu'); pg.wait_for_timeout(300); tapsel(pg, '#modal [data-a=load]'); pg.wait_for_timeout(400)
    tapsel(pg, '#modal [data-slot=s1] [data-a=sdel]'); pg.wait_for_timeout(400); B.shot(pg, 's09_del_arm', 200)
    tapsel(pg, '#modal [data-slot=s1] [data-a=sdel]'); pg.wait_for_timeout(400)
    print('deleted', pg.evaluate(ST))
    tapsel(pg, '#modal [data-slot=prev] [data-a=sload]'); pg.wait_for_timeout(1500)
    print('loaded prev', pg.evaluate('[G.factions[G.player].name, dateStr(), $("toast").textContent]'), pg.evaluate(ST))
    # 제목 화면에서 불러오기
    tapsel(pg, '#btnMenu'); pg.wait_for_timeout(300); tapsel(pg, '#modal [data-a=title]'); pg.wait_for_timeout(600)
    tapsel(pg, '#tLoad'); pg.wait_for_timeout(500); B.shot(pg, 's10_title_load', 200)
    print('keys', pg.evaluate('Object.keys(localStorage).sort().map(function (k) { return k + ":" + localStorage.getItem(k).length; })'))
B.run(steps, W, H, D)
print('errors:', [e for e in B.errors if 'GPU stall' not in e][:5])
