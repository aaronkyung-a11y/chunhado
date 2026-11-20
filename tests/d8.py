# 옛 판(v0.2, v0.3)에서 만든 저장을 v0.4가 그대로 여는지 (같은 브라우저 저장소)
import os, sys, time
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.abspath(__file__))
OLD = 'file://' + os.path.join(ROOT, '..', sys.argv[1] if len(sys.argv) > 1 else 'chunhado-v0.3-offline.html')
NEW = 'file://' + os.path.join(ROOT, '..', 'dist', 'offline.html')
errors = []
STATE = '''() => ({ date: dateStr(), units: G.units.length, off: G.officers.length, ver: G.ver, key: SAVE_KEY, len: (localStorage.getItem(SAVE_KEY) || '').length,
  mine: facUnits(G.player).map(function (u) { return [u.c, u.r, u.dest, u.troops]; }), gold: facBases(G.player)[0].gold,
  por: [G.officers.filter(function (o) { return o.n === '여령기'; })[0].por, G.officers.filter(function (o) { return o.n === '황보숭'; })[0].por],
  col: G.factions.slice(0, 4).map(function (f) { return f.color; }), page: GAME_VERSION })'''
with sync_playwright() as p:
    br = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
    cxt = br.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, is_mobile=True, has_touch=True, locale='ko-KR')
    pg = cxt.new_page()
    pg.on('console', lambda m: errors.append(m.type + ': ' + m.text) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: errors.append('pageerror: ' + str(e)))
    pg.goto(OLD); pg.wait_for_function('window.R3 && R3.ready', timeout=60000); pg.wait_for_timeout(500)
    pg.evaluate('() => { try { localStorage.clear(); } catch (e) {} }')
    # 옛 판에서 유비로 시작 → 관우를 하비로 행군시키고 두 턴 진행 → 저장
    pg.evaluate('''() => { newGame(2, 777); var b = facBases(G.player)[0], db = G.bases[baseByName('하비')], ids = autoTeam(b, 'spear', 2800);
      var r = cmdDeploy(b, { type: 'spear', ids: ids, troops: 2800, food: 3000 }); r.unit.dest = K(db.c, db.r); unitMarch(r.unit);
      endTurn(); endTurn(); saveGame(); }''')
    s0 = pg.evaluate(STATE); print('old ', s0)
    pg.goto(NEW); pg.wait_for_function('window.R3 && R3.ready', timeout=60000); pg.wait_for_timeout(500)
    print('new page', pg.evaluate('GAME_VERSION'), 'has save', pg.evaluate('hasSave()'))
    pg.locator('#tCont').tap(); pg.wait_for_timeout(1200)
    s1 = pg.evaluate(STATE); print('new ', s1)
    print('same state', all(s0[k] == s1[k] for k in ('date', 'units', 'off', 'ver', 'mine', 'gold')), '| portraits', s0['por'], '->', s1['por'], '| colors changed', s0['col'] != s1['col'])
    # v0.9.1: 0.8.1~0.9 에서 만든 저장은 보호의 끝이 옛 기간으로 들어 있다 — 열면 새 기간으로 당겨지고 기록에 한 줄 남는가(그 전 판의 저장에는 보호가 없어 새 기간이 그대로 붙는다)
    pz = pg.evaluate('''() => (typeof peaceFor === "function" && G.peace) ? { until: G.peace.until, v: G.peace.v, want: 1 + peaceFor(startTroops(G.player)), turn: G.turn, note: G.log.filter(function (e) { return /초반 보호 기간이 짧아졌습니다/.test(e.t); }).map(function (e) { return e.t; }), chip: (document.querySelector("#sheet .pz") || {}).innerText || "" } : null''')
    print('peace', pz)
    if pz:
        had = s0['page'] in ('v0.8.1', 'v0.9')
        if pz['v'] != 2 or pz['until'] != max(pz['want'], min(pz['until'], pz['turn'] + 3)) or (had and (pz['until'] != pz['want'] or len(pz['note']) != 1)) or (not had and pz['note']) or '턴' in pz['chip']:
            errors.append('peace migration: %s' % pz)
    print('portrait keys all present', pg.evaluate('G.officers.every(function (o) { return !!POR_URL[o.por]; })'), '| zin on old units', pg.evaluate('G.units.map(function (u) { return u.zin; }).slice(0, 4)'))
    pg.screenshot(path=os.path.join(ROOT, 'shots4', 'd8_loaded_%s.png' % s0['page']))
    # 이어서 세 턴 진행(재생 포함) — 행군이 새 규칙(성역)으로 이어지는가
    for i in range(3):
        pg.evaluate('UI.pspeed = 3; clearSel()'); pg.locator('#btnEnd').tap(); pg.wait_for_timeout(250)
        if not pg.evaluate('!!UI.play'): pg.locator('#btnEnd').tap()
        t0 = time.time()
        while pg.evaluate('!!UI.play') and time.time() - t0 < 150: pg.wait_for_timeout(100)
        pg.wait_for_timeout(300); pg.evaluate('if (MODAL) closeDialog()')
        print('  turn +%d' % (i + 1), pg.evaluate('[dateStr(), G.over, UI.busy, JSON.stringify(facUnits(G.player).map(function (u) { return [u.c, u.r, u.dest, u.zin, zoneAt(u.c, u.r)]; })), facBases(G.player).map(function (b) { return b.n; }).join(",")]'))
    print('  log tail', pg.evaluate('G.log.slice(-7).map(function (e) { return e.d + " " + e.t; })'))
    print('save again + reload', pg.evaluate('''() => { var ok = saveGame(), a = serialize(); loadGame(); return [ok, a === serialize()]; }'''))
    br.close()
errs = [e for e in errors if 'ERR_FILE_NOT_FOUND' not in e and 'ERR_FAILED' not in e]
print('ERRORS', errs[:6])
sys.exit(1 if errs else 0)      # v0.9.1: 오류가 있으면 종료 코드로도 알린다(그 전에는 늘 0 이었다)
