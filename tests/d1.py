# v0.4: 수묵 화면 둘러보기 — 타이틀, 세력 고르기, 본 화면, 거점 창, 출진(처음 방식), 이동, 턴 종료
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
B.SHOTS = os.path.join(B.ROOT, 'shots4')
def steps(pg):
    B.shot(pg, 'd1_00_title', 400)
    B.tapsel(pg, '#tNew'); B.shot(pg, 'd1_01_factions', 300)
    B.tapsel(pg, '#modal .row', 0); B.shot(pg, 'd1_02_intro', 300)
    B.tapsel(pg, '#modal [data-a=go]'); pg.wait_for_timeout(500); B.shot(pg, 'd1_03_help', 200)
    B.tapsel(pg, '#modal [data-a=close]'); pg.wait_for_timeout(900)
    B.shot(pg, 'd1_04_main', 600)
    info = pg.evaluate('''() => { var b = facBases(G.player)[0]; return [b.id, b.c, b.r, b.n]; }''')
    print('base', info)
    pg.evaluate('(id) => { selectBase(G.bases[id]); jumpTo(G.bases[id].c, G.bases[id].r, 1.0); }', info[0]); B.shot(pg, 'd1_05_base', 700)
    # 군사 탭 → 출진
    tabs = pg.locator('#sheet .tabs button'); n = tabs.count(); print('tabs', n, [tabs.nth(i).inner_text() for i in range(n)])
    for i in range(n):
        if '출진' in tabs.nth(i).inner_text(): tabs.nth(i).tap()      # v0.9.2: 탭 이름 '군사' → '출진'
    pg.wait_for_timeout(300); B.shot(pg, 'd1_06_mil', 200)
    pg.locator('#sheet [data-a=deploy]').tap(); pg.wait_for_timeout(400); B.shot(pg, 'd1_07_deploy0', 200)
    pg.locator('#modal [data-a=auto]').tap(); pg.wait_for_timeout(400); B.shot(pg, 'd1_08_deploy1', 200)
    print('has dests', pg.locator('#modal .dests').count())
    pg.locator('#modal [data-a=ok]').tap(); pg.wait_for_timeout(250); B.shot(pg, 'd1_09_deploying', 0)
    pg.wait_for_timeout(900); B.shot(pg, 'd1_10_deployed', 200)
    st = pg.evaluate('''() => { var u = selUnit(); if (!u) return null; var ks = Object.keys(UI.rc.stop).map(Number), far = ks[0], fd = -1;
      ks.forEach(function (k) { var c = k % W, r = (k - c) / W, d = hdist(c, r, u.c, u.r); if (d > fd) { fd = d; far = k; } });
      return { id: u.id, c: u.c, r: u.r, n: ks.length, far: [far % W, (far - far % W) / W], fd: fd, zone: zoneAt(u.c, u.r), mp: u.mp }; }''')
    print('unit', st)
    pg.evaluate('([c, r]) => { jumpTo(c, r, 1.25); }', [st['c'], st['r']]); B.shot(pg, 'd1_11_range', 700)
    B.taphex(pg, st['far'][0], st['far'][1]); B.shot(pg, 'd1_12_moving', 250); pg.wait_for_timeout(1500); B.shot(pg, 'd1_13_moved', 200)
    print('after move', pg.evaluate('() => { var u = UMAP[UI.sel.id]; return [u.c, u.r, u.mp, zoneAt(u.c, u.r), $("toast").textContent]; }'))
    pg.evaluate('() => { clearSel(); cam.z = 0.45; clampCam(); }'); B.shot(pg, 'd1_14_wide', 700)
    pg.evaluate('() => { cam.z = 0.2; clampCam(); }'); B.shot(pg, 'd1_15_far', 700)
    print('errors', B.errors)
B.run(steps, 390, 844, 2)
