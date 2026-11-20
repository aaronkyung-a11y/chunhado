# v0.9.3 화면 찍기(대화창·군사·건설 번호):  python3 tests/shot93.py [w=390] [h=844] [dpr=2]   → tests/shots20/
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import taphex, tapsel
B.SHOTS = os.path.join(B.ROOT, 'shots20')
os.makedirs(B.SHOTS, exist_ok=True)
W = int(sys.argv[1]) if len(sys.argv) > 1 else 390
H = int(sys.argv[2]) if len(sys.argv) > 2 else 844
D = int(sys.argv[3]) if len(sys.argv) > 3 else 2
def steps(pg):
    tapsel(pg, '#tNew'); pg.wait_for_timeout(300)
    tapsel(pg, '#modal .row', 2); tapsel(pg, '#modal [data-a=go]'); pg.wait_for_timeout(600)
    tapsel(pg, '#modal [data-a=close]'); pg.wait_for_timeout(1500); B.shot(pg, 't01_brief', 200)       # 시작: 군사의 한마디
    pg.wait_for_timeout(4500); B.shot(pg, 't02_home', 200)
    tapsel(pg, '#sheet [data-a=adv]'); pg.wait_for_timeout(500); B.shot(pg, 't03_appoint', 200)
    pg.locator('#modal [data-a=set]').first.tap(); pg.wait_for_timeout(700); B.shot(pg, 't04_appointed', 200)
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(300)
    b = pg.evaluate('(() => { var b = facCities(G.player)[0]; G.factions[G.player].ap = 300; b.gold = 3000; b.troops = 20000; b.w.spear = 9000; b.food = 60000; selectBase(b); return b.id; })()')
    pg.wait_for_timeout(600)
    tapsel(pg, '#sheet [data-a=draft]'); pg.wait_for_timeout(400)
    tapsel(pg, '#modal [data-a=auto]'); tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(700); B.shot(pg, 't05_draft', 200)
    pg.locator('#sheet .tabs button').nth(3).tap(); pg.wait_for_timeout(900); B.shot(pg, 't06_lots', 200)
    pg.locator('#sheet .lot[data-a=plot]').nth(2).tap(); pg.wait_for_timeout(800)
    pg.locator('#modal .row[data-v=market]').tap(); pg.wait_for_timeout(400)
    tapsel(pg, '#modal [data-a=auto]'); tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(800); B.shot(pg, 't07_build', 200)
    pg.wait_for_timeout(2600)
    pg.evaluate('(id) => { baseOfficers(G.bases[id]).forEach(function (o) { o.acted = false; }); G.factions[G.player].ap = 300; refreshSheet(); }', b)
    pg.locator('#sheet .tabs button').nth(2).tap(); pg.wait_for_timeout(400)
    tapsel(pg, '#sheet [data-a=search]'); pg.wait_for_timeout(400)
    tapsel(pg, '#modal [data-a=auto]'); tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(800); B.shot(pg, 't08_search', 200)
    pg.wait_for_timeout(2600)
    pg.evaluate('(id) => { baseOfficers(G.bases[id]).forEach(function (o) { o.acted = false; }); G.factions[G.player].ap = 300; refreshSheet(); }', b)
    if pg.locator('#sheet [data-a=recruit]:not(.off)').count():
        tapsel(pg, '#sheet [data-a=recruit]'); pg.wait_for_timeout(500)
        if pg.evaluate('!!MODAL'):
            pg.locator('#modal .row[data-a=t]').first.tap(); pg.wait_for_timeout(500)
            if pg.locator('#modal [data-a=pick]').count():
                pg.locator('#modal [data-a=pick]').first.tap(); pg.wait_for_timeout(400); B.shot(pg, 't09_recruit_pick', 200)
                tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(900); B.shot(pg, 't10_recruit_result', 200)
    pg.evaluate('if (MODAL) closeDialog()'); pg.wait_for_timeout(2400)
    pg.evaluate('(id) => { baseOfficers(G.bases[id]).forEach(function (o) { o.acted = false; }); G.factions[G.player].ap = 300; refreshSheet(); }', b)
    pg.locator('#sheet .tabs button').nth(1).tap(); pg.wait_for_timeout(400)
    tapsel(pg, '#sheet [data-a=deploy]'); pg.wait_for_timeout(500)
    tapsel(pg, '#modal [data-a=auto]'); pg.wait_for_timeout(300); tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(1100); B.shot(pg, 't11_deploy', 200)
B.run(steps, W, H, D)
print('errors', [e for e in B.errors if 'GL Driver' not in e and 'ERR_FILE_NOT_FOUND' not in e][:6])
