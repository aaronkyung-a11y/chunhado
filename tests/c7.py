# v0.2에서 만든 저장을 v0.3이 그대로 여는지 (같은 브라우저 저장소)
import os, time
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.abspath(__file__))
V02 = 'file://' + os.path.join(ROOT, '..', 'chunhado-v0.2-offline.html')
V03 = 'file://' + os.path.join(ROOT, '..', 'dist', 'offline.html')
errors = []
with sync_playwright() as p:
    br = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
    cxt = br.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, is_mobile=True, has_touch=True, locale='ko-KR')
    pg = cxt.new_page()
    pg.on('console', lambda m: errors.append(m.type + ': ' + m.text) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: errors.append('pageerror: ' + str(e)))
    pg.goto(V02); pg.wait_for_function('window.R3 && R3.ready', timeout=60000); pg.wait_for_timeout(500)
    print('v0.2 page', pg.evaluate('GAME_VERSION'))
    # v0.2에서 유비로 시작 → 관우를 하비로 행군시키고 두 턴 진행 → 저장
    pg.evaluate('''() => { newGame(2, 777); var b = facBases(G.player)[0], db = G.bases[baseByName('하비')], ids = autoTeam(b, 'spear', 2800);
      var r = cmdDeploy(b, { type: 'spear', ids: ids, troops: 2800, food: 3000 }); r.unit.dest = K(db.c, db.r); unitMarch(r.unit);
      endTurn(); endTurn(); saveGame(); }''')
    s02 = pg.evaluate('''() => ({ date: dateStr(), units: G.units.length, off: G.officers.length, ver: G.ver, key: SAVE_KEY, len: localStorage.getItem(SAVE_KEY).length, mine: facUnits(G.player).map(function (u) { return [u.c, u.r, u.dest, u.troops]; }), por: [G.officers.filter(function (o) { return o.n === '여령기'; })[0].por, G.officers.filter(function (o) { return o.n === '황보숭'; })[0].por], gold: facBases(G.player)[0].gold })''')
    print('v0.2 state', s02)
    pg.goto(V03); pg.wait_for_function('window.R3 && R3.ready', timeout=60000); pg.wait_for_timeout(500)
    print('v0.3 page', pg.evaluate('GAME_VERSION'), 'has save', pg.evaluate('hasSave()'))
    pg.locator('#tCont').tap(); pg.wait_for_timeout(900)
    s03 = pg.evaluate('''() => ({ date: dateStr(), units: G.units.length, off: G.officers.length, ver: G.ver, mine: facUnits(G.player).map(function (u) { return [u.c, u.r, u.dest, u.troops]; }), por: [G.officers.filter(function (o) { return o.n === '여령기'; })[0].por, G.officers.filter(function (o) { return o.n === '황보숭'; })[0].por], gold: facBases(G.player)[0].gold, home: SHEET && SHEET.home, todo: todoList().map(function (t) { return t.t; }) })''')
    print('v0.3 state', s03)
    same = all(s02[k] == s03[k] for k in ('date', 'units', 'off', 'ver', 'mine', 'gold'))
    print('same state', same, '| portraits', s02['por'], '->', s03['por'])
    # 이어서 한 턴 진행(재생 포함)
    pg.evaluate('UI.pspeed = 3; clearSel()'); pg.locator('#btnEnd').tap(); pg.wait_for_timeout(200)
    if not pg.evaluate('!!UI.play'): pg.locator('#btnEnd').tap()
    t0 = time.time()
    while pg.evaluate('!!UI.play') and time.time() - t0 < 120: pg.wait_for_timeout(100)
    pg.wait_for_timeout(300)
    print('after one v0.3 turn', pg.evaluate('[dateStr(), G.over, UI.busy, facUnits(G.player).map(function (u) { return [u.c, u.r, u.dest]; })]'))
    br.close()
print('ERRORS', [e for e in errors if 'ERR_FILE_NOT_FOUND' not in e and 'ERR_FAILED' not in e][:6])
