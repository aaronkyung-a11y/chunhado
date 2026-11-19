# v0.3: 부대가 몰린 전장에서 얼굴 딱지·이름표가 어떻게 보이는지, 내 부대의 전투·도착 처리
from browser import *
import browser
browser.SHOTS = os.path.join(ROOT, 'shots3')
def end_turn(pg, limit=150):
    pg.evaluate('if (MODAL) closeDialog(); clearSel()')
    tapsel(pg, '#btnEnd'); pg.wait_for_timeout(150)
    if not pg.evaluate('!!UI.play') and not pg.evaluate('!!MODAL'): tapsel(pg, '#btnEnd')
    t0 = time.time()
    while pg.evaluate('!!UI.play') and time.time() - t0 < limit: pg.wait_for_timeout(100)
    pg.wait_for_timeout(250); return time.time() - t0
def steps(pg):
    start(pg, 2)
    pg.evaluate('UI.pspeed = 0')
    # 관우·장비를 하비로 행군시켜 놓고 세 턴을 넘긴다(재생 끔)
    r = pg.evaluate('''() => { var b = facBases(G.player)[0], db = G.bases[baseByName('하비')], ids = autoTeam(b, 'spear', 2800);
      var eta = deployEta(b, 'spear', ids, K(db.c, db.r));
      var r = cmdDeploy(b, { type: 'spear', ids: ids, troops: 2800, food: 3000, toward: db, dest: K(db.c, db.r) });
      var m = unitMarch(r.unit); requestDraw();
      return { eta: eta, ok: r.ok, first: m && m.ok, left: marchTurns(r.unit, marchPath(r.unit, r.unit.dest)) }; }''')
    print('deploy', r)
    for t in range(4):
        dt = end_turn(pg)
        st = pg.evaluate('''() => { var u = facUnits(G.player)[0]; return { date: dateStr(), u: u ? { c: u.c, r: u.r, dest: u.dest, troops: u.troops, tg: attackTargets(u).length } : null, todo: todoList().map(function (t) { return t.t; }), rep: REPORT.filter(function (e) { return e.imp >= 1 && e.f === G.player; }).map(function (e) { return e.t; }) }; }''')
        print('T%d %.1fs' % (t, dt), st)
        if st['u'] and st['u']['dest'] < 0: break
    pg.evaluate('if (MODAL) closeDialog(); clearSel()')
    shot(pg, 'c4_home_war', 500)
    # 내 부대를 고른다 → 붉은 칸(적)을 눌러 공격
    u = pg.evaluate('''() => { var u = facUnits(G.player)[0]; if (!u) return null; gotoUnit(u); var ts = attackTargets(u); return { id: u.id, c: u.c, r: u.r, ts: ts.map(function (t) { return [t.kind, t.c, t.r]; }) }; }''')
    print('unit', u)
    pg.wait_for_timeout(900); shot(pg, 'c4_unit_sel', 300)
    if u and u['ts']:
        t = u['ts'][0]; taphex(pg, t[1], t[2]); shot(pg, 'c4_target', 400)
        tapsel(pg, '#sheet .act.pri'); pg.wait_for_timeout(1200); shot(pg, 'c4_attack', 100)
        print('toast', pg.evaluate('$("toast").textContent'))
    # 적이 몰려 있는 소패 둘레
    pg.evaluate('clearSel(); var b = facBases(G.player)[0]; jumpTo(b.c, b.r, 1.0)'); shot(pg, 'c4_crowd_z10', 1200)
    pg.evaluate('var b = facBases(G.player)[0]; jumpTo(b.c, b.r, 1.5)'); shot(pg, 'c4_crowd_z15', 1200)
    pg.evaluate('var b = facBases(G.player)[0]; jumpTo(b.c, b.r, 0.55)'); shot(pg, 'c4_crowd_z055', 1200)
    # 느리게 한 턴 재생하며 장면 몇 장
    pg.evaluate('UI.pspeed = 1'); pg.evaluate('clearSel()')
    tapsel(pg, '#btnEnd'); pg.wait_for_timeout(150)
    if not pg.evaluate('!!UI.play'): tapsel(pg, '#btnEnd')
    t0 = time.time(); n = 0; last = ''
    while pg.evaluate('!!UI.play') and time.time() - t0 < 120:
        m = pg.evaluate('$("plMsg").innerText')
        if m != last and n < 4: last = m; pg.wait_for_timeout(450); shot(pg, 'c4_scene%d' % n, 30); n += 1
        pg.wait_for_timeout(100)
    print('slow turn %.1fs' % (time.time() - t0))
    shot(pg, 'c4_report', 500)
run(steps, 390, 844, 2)
print('ERRORS', [e for e in errors if 'ReadPixels' not in e and 'ERR_FILE_NOT_FOUND' not in e and 'ERR_FAILED' not in e][:8])
