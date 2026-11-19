# v0.4: 전법 12가지 · 계략 4가지 · 성 공격 연출이 모두 끝까지 돌고 뒤끝(멈춘 그림·남은 효과·오류)이 없는지
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
import d2
B.SHOTS = os.path.join(B.ROOT, 'shots4')
SETUP = d2.SETUP.replace("var mineSpec = [['spear', 0, 0], ['cav', 0, 1], ['bow', -2, 0]], foeSpec = [['spear', 1, 0], ['spear', 1, 1], ['sword', 2, -1]];",
                         "b.w.halberd = 9000; var mineSpec = [['spear', 0, 0], ['cav', 0, 1], ['bow', -1, 0], ['halberd', 0, -1]], foeSpec = [['spear', 1, 0], ['spear', 1, 1], ['sword', 1, -1]];")
assert SETUP != d2.SETUP
def wait_idle(pg, limit=9000):
    t0 = time.time()
    while (pg.evaluate('UI.busy || UI.anims.length > 0 || FX.live.length > 0')) and (time.time() - t0) * 1000 < limit: pg.wait_for_timeout(60)
    return (time.time() - t0) * 1000
def steps(pg):
    B.start(pg, 0)
    pg.evaluate('() => { UI.pspeed = 1; uApt = function () { return "S"; }; }')
    s = pg.evaluate(SETUP); print('setup', s)
    pg.evaluate('(s) => { window.S = s; }', s); pg.wait_for_timeout(700)
    # 적을 계속 살려 두고(병력·기력 보충), 제자리로 돌려놓으며 전법을 하나씩
    RESET = '''() => { var f = S.f, home = { 0: [0, 0], 1: [0, 1], 2: [-1, 0], 3: [0, -1] }, fh = { 0: [1, 0], 1: [1, 1], 2: [1, -1] }, i, u;
      for (i = 0; i < S.foe.length; i++) { u = UMAP[S.foe[i]]; if (!u) continue; u.troops = 3000; u.morale = 100; u.status = null; u.stT = 0; }
      for (i = 0; i < S.mine.length; i++) { u = UMAP[S.mine[i]]; if (!u) continue; u.troops = 4000; u.morale = 100; u.done = false; u.status = null; }
      for (i = 0; i < S.foe.length; i++) { u = UMAP[S.foe[i]]; if (u && (u.c !== f[0] + fh[i][0] || u.r !== f[1] + fh[i][1]) && !unitAt(f[0] + fh[i][0], f[1] + fh[i][1])) placeUnit(u, f[0] + fh[i][0], f[1] + fh[i][1]); }
      for (i = 0; i < S.mine.length; i++) { u = UMAP[S.mine[i]]; if (u && (u.c !== f[0] + home[i][0] || u.r !== f[1] + home[i][1]) && !unitAt(f[0] + home[i][0], f[1] + home[i][1])) placeUnit(u, f[0] + home[i][0], f[1] + home[i][1]); }
      for (var pass = 0; pass < 2; pass++) {
        for (i = 0; i < S.mine.length; i++) { u = UMAP[S.mine[i]]; if (u && (u.c !== f[0] + home[i][0] || u.r !== f[1] + home[i][1]) && !unitAt(f[0] + home[i][0], f[1] + home[i][1])) placeUnit(u, f[0] + home[i][0], f[1] + home[i][1]); }
        for (i = 0; i < S.foe.length; i++) { u = UMAP[S.foe[i]]; if (u && (u.c !== f[0] + fh[i][0] || u.r !== f[1] + fh[i][1]) && !unitAt(f[0] + fh[i][0], f[1] + fh[i][1])) placeUnit(u, f[0] + fh[i][0], f[1] + fh[i][1]); }
      }
      for (var k in G.fires) delete G.fires[k];
      clearSel(); syncScene(); requestDraw(); return G.units.length; }'''
    pairs = { 'spear': (0, 0), 'cav': (1, 1), 'bow': (2, 0), 'halberd': (3, 2) }
    seen = {}
    for typ in ['spear', 'halberd', 'bow', 'cav']:
        n = pg.evaluate('(t) => TACTICS[t].length', typ)
        for ti in range(n):
            for rep in range(3):
                pg.evaluate(RESET); pg.wait_for_timeout(120)
                mi, fi = pairs[typ]
                r = pg.evaluate('''([mi, fi, typ, ti]) => { var u = UMAP[S.mine[mi]], t = UMAP[S.foe[fi]], tac = TACTICS[typ][ti]; if (!u || !t) return ['gone'];
                  var ok = tacticTargets(u, tac).some(function (x) { return x.u === t; }); if (!ok) return ['no target', tac.name, hdist(u.c, u.r, t.c, t.r)];
                  selectUnit(u, true); UI.target = { kind: 'unit', u: t, c: t.c, r: t.r }; window.__lastN = EVQ.length; doAct({ kind: 'tactic', tac: tac }); return ['ok', tac.name]; }''', [mi, fi, typ, ti])
                if r[0] != 'ok': print('  ', typ, ti, r); break
                if typ == 'halberd' and ti == 0 and rep == 0:
                    pg.wait_for_timeout(430); pg.screenshot(path=os.path.join(B.SHOTS, 'd2b_galkwi.png'))
                ms = wait_idle(pg)
                toast = pg.evaluate('$("toast").textContent')
                key = r[1] + (' 성공' if '성공' in toast else (' 실패' if '실패' in toast else ' ?'))
                seen[key] = seen.get(key, 0) + 1
                st = pg.evaluate('[UI.busy, UI.anims.length, FX.live.length, Object.keys(R3.units).filter(function (id) { return R3.units[id].anim; }).length]')
                if st != [False, 0, 0, 0]: print('  LEFTOVER', typ, r[1], st, '%.0fms' % ms)
    print('tactics run', seen)
    # 계략 넷
    for pi in range(4):
        for rep in range(2):
            pg.evaluate(RESET); pg.wait_for_timeout(120)
            r = pg.evaluate('''(pi) => { var u = UMAP[S.mine[0]], t = UMAP[S.foe[0]], pl = PLOYS[pi]; if (!u || !t) return ['gone'];
              if (pl.id === 'douse') { G.fires[K(u.c, u.r)] = 2; syncScene(); selectUnit(u, true); var res = unitPloy(u, pl, { c: u.c, r: u.r }); if (!res.ok) return ['refused', res.msg]; UI.busy = true; animAct(res, function () { UI.busy = false; clearSel(); afterAction(); }, function () {}); return ['ok', pl.name]; }
              var ts = ployTargets(u, pl), tg = null; for (var i = 0; i < ts.length; i++) if (ts[i].u === t) tg = ts[i]; if (!tg) return ['no target', pl.name];
              selectUnit(u, true); UI.target = { kind: 'unit', u: t, c: t.c, r: t.r }; doAct({ kind: 'ploy', ploy: pl }); return ['ok', pl.name]; }''', pi)
            ms = wait_idle(pg)
            st = pg.evaluate('[UI.busy, UI.anims.length, FX.live.length]')
            print('  ploy', r, pg.evaluate('$("toast").textContent')[:40], st, '%.0fms' % ms)
    print('ERRORS', [e for e in B.errors if 'ReadPixels' not in e and 'ERR_FILE_NOT_FOUND' not in e][:8])
B.run(steps, 390, 844, 2)
