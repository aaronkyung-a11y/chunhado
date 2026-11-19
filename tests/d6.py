# v0.4: 나머지 화면을 수묵 테마로 훑어본다 — 세력 고르기, 소개, 도움말, 목록(탭 전부), 기록, 보고, 장수 상세, 메뉴, 거점 탭 전부, 흐름 창들, 게임 끝
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
B.SHOTS = os.path.join(B.ROOT, 'shots4')
def steps(pg):
    B.tapsel(pg, '#tNew'); B.shot(pg, 'd6_01_factions', 300)
    pg.evaluate('() => { var d = document.querySelector("#modal .dlg-b"); if (d) d.scrollTop = 900; }'); B.shot(pg, 'd6_01b_factions2', 300)
    B.tapsel(pg, '#modal .row', 2); B.shot(pg, 'd6_02_intro', 300)
    B.tapsel(pg, '#modal [data-a=go]'); pg.wait_for_timeout(500); B.shot(pg, 'd6_03_help', 200)
    pg.evaluate('() => { var d = document.querySelector("#modal .dlg-b"); if (d) d.scrollTop = 700; }'); B.shot(pg, 'd6_03b_help2', 300)
    pg.evaluate('() => { var d = document.querySelector("#modal .dlg-b"); if (d) d.scrollTop = 1500; }'); B.shot(pg, 'd6_03c_help3', 300)
    B.tapsel(pg, '#modal [data-a=close]'); pg.wait_for_timeout(900)
    B.shot(pg, 'd6_04_home', 600)
    # 목록 탭들
    pg.evaluate('() => showLists()'); B.shot(pg, 'd6_05_lists0', 300)
    tabs = pg.locator('#modal .tabs button'); n = tabs.count(); print('list tabs', [tabs.nth(i).inner_text() for i in range(n)])
    for i in range(1, n):
        tabs.nth(i).tap(); B.shot(pg, 'd6_05_lists%d' % i, 300)
    pg.evaluate('() => closeDialog()')
    # 장수 상세
    pg.evaluate('() => { var b = facBases(G.player)[0]; showOfficer(G.officers[b.gov >= 0 ? b.gov : baseOfficers(b)[0].id]); }'); B.shot(pg, 'd6_06_officer', 300)
    pg.evaluate('() => closeDialog()')
    pg.evaluate('''() => { var o = G.officers.filter(function (x) { return x.n === '초선' || x.n === '여령기'; })[0]; showOfficer(o); }'''); B.shot(pg, 'd6_06b_officer2', 300)
    pg.evaluate('() => closeDialog()')
    # 메뉴, 기록
    pg.evaluate('() => showMenu()'); B.shot(pg, 'd6_07_menu', 300); pg.evaluate('() => closeDialog()')
    # 거점 탭 전부
    pg.evaluate('() => { var b = facBases(G.player)[0]; selectBase(b); jumpTo(b.c, b.r, 1.0); }'); B.shot(pg, 'd6_08_base0', 500)
    tabs = pg.locator('#sheet .tabs button'); n = tabs.count(); names = [tabs.nth(i).inner_text() for i in range(n)]; print('base tabs', names)
    for i in range(1, n):
        tabs.nth(i).tap(); B.shot(pg, 'd6_08_base%d' % i, 300)
    # 흐름 창: 버튼을 차례로 눌러 창이 뜨면 찍고 닫는다
    seen = []
    for i in range(n):
        pg.locator('#sheet .tabs button').nth(i).tap(); pg.wait_for_timeout(200)
        acts = pg.evaluate('() => Array.prototype.map.call(document.querySelectorAll("#sheet [data-a]"), function (e) { return [e.getAttribute("data-a"), e.disabled ? 1 : 0, e.getAttribute("data-i") || ""]; })')
        for a in acts:
            if a[0] in seen or a[1] or a[0] in ('close', 'tab'): continue
            seen.append(a[0])
            pg.locator('#sheet [data-a=%s]' % a[0]).first.tap(); pg.wait_for_timeout(350)
            if pg.evaluate('() => !!MODAL'):
                B.shot(pg, 'd6_09_flow_%s' % a[0], 150)
                pg.evaluate('() => closeDialog()'); pg.wait_for_timeout(150)
            else:
                print('  action', a[0], '→ no dialog; toast:', pg.evaluate('() => $("toast").textContent'))
            pg.evaluate('() => { var b = facBases(G.player)[0]; if (!SHEET || SHEET.home) selectBase(b); }'); pg.wait_for_timeout(150)
            pg.locator('#sheet .tabs button').nth(i).tap(); pg.wait_for_timeout(150)
    print('flows seen', seen)
    # 한 턴 넘겨 보고와 기록
    pg.evaluate('() => { clearSel(); UI.pspeed = 3; }'); pg.locator('#btnEnd').tap(); pg.wait_for_timeout(300)
    if not pg.evaluate('!!UI.play'): pg.locator('#btnEnd').tap()
    import time; t0 = time.time()
    while pg.evaluate('!!UI.play') and time.time() - t0 < 120: pg.wait_for_timeout(100)
    pg.wait_for_timeout(400); B.shot(pg, 'd6_10_report', 200)
    pg.evaluate('() => closeDialog()')
    pg.evaluate('() => showLog(G.log, "기록")'); B.shot(pg, 'd6_11_log', 300); pg.evaluate('() => closeDialog()')
    # 게임 끝 화면(양쪽)
    pg.evaluate('() => { G.over = "win"; showGameOver(); }'); B.shot(pg, 'd6_12_win', 400)
    pg.evaluate('() => { closeDialog(); G.over = "lose"; showGameOver(); }'); B.shot(pg, 'd6_13_lose', 400)
    print('errors', B.errors)
B.run(steps, 390, 844, 2)
