# v0.4: 성역에 막 들어선 부대는 그 턴에 그 성을 칠 수 없다(노병의 2칸 사격 포함) — 화면 조작으로 확인
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import taphex, tapsel
B.SHOTS = os.path.join(B.ROOT, 'shots4')
def end_turn(pg):
    pg.evaluate('() => { clearSel(); UI.pspeed = 3; }'); pg.locator('#btnEnd').tap(); pg.wait_for_timeout(250)
    if not pg.evaluate('!!UI.play'): pg.locator('#btnEnd').tap()
    t0 = time.time()
    while pg.evaluate('!!UI.play') and time.time() - t0 < 150: pg.wait_for_timeout(100)
    dt = time.time() - t0
    for i in range(20):                      # 요약 창이 조금 늦게 뜰 수 있다 — 뜨면 닫는다
        pg.wait_for_timeout(100)
        if pg.evaluate('!!MODAL'): pg.evaluate('closeDialog()'); break
    pg.wait_for_timeout(200); pg.evaluate('if (MODAL) closeDialog()'); return dt
def steps(pg):
    B.start(pg, 0)
    info = pg.evaluate('''(() => {
      var b = G.bases[baseByName("진류")], t = G.bases[baseByName("복양")];
      G.factions[G.player].ap = 200; b.troops = 20000; b.w.bow = 9000; b.food = 30000;
      var os = idleOfficers(b).sort((x, y) => aiMilScore(y) - aiMilScore(x));
      var u = cmdDeploy(b, {type: "bow", ids: [os[0].id], troops: 4000, food: 3000}).unit;
      function free(c, r) { var t2 = terr(c, r); return t2 !== "m" && t2 !== "w" && t2 !== "s" && t2 !== "x" && !unitAt(c, r) && !facAt(c, r) && !baseAt(c, r); }
      // 복양에서 3칸 떨어진(성역 바로 밖) 빈 칸 가운데, 2칸째 칸(성역 안)이 옆에 있는 곳
      var best = null;
      for (var c = t.c - 4; c <= t.c + 4 && !best; c++) for (var r = t.r - 4; r <= t.r + 4 && !best; r++) {
        if (!inMap(c, r) || hdist(c, r, t.c, t.r) !== 3 || !free(c, r) || zoneAt(c, r) >= 0) continue;
        var inn = nbrs(c, r).filter(function (q) { return hdist(q[0], q[1], t.c, t.r) === 2 && free(q[0], q[1]) && zoneAt(q[0], q[1]) === t.id && !plotAt(q[0], q[1]); });
        if (inn.length) best = { out: [c, r], inn: inn[0] };
      }
      placeUnit(u, best.out[0], best.out[1]); u.mp = uMaxMp(u); u.done = false; u.moved = false; u.zin = -1; u.ox = -1; u.morale = 90;
      syncScene(); requestDraw(); refreshHud();
      return { id: u.id, out: best.out, inn: best.inn, t: [t.c, t.r], tid: t.id, tn: t.n, owner: t.owner, range: uRange(u) };
    })()''')
    print('staged', info)
    pg.evaluate('(id) => gotoUnit(UMAP[id])', info['id']); pg.wait_for_timeout(700)
    print('before: stop has inner hex', pg.evaluate('([c, r]) => !!(UI.rc && UI.rc.stop[K(c, r)])', info['inn']), '| base in targets', pg.evaluate('(tid) => attackTargets(selUnit()).some(function (x) { return x.kind === "base" && x.b.id === tid; })', info['tid']))
    taphex(pg, *info['inn']); pg.wait_for_timeout(1700)
    st = pg.evaluate('(tid) => { var u = selUnit(); return { pos: [u.c, u.r], mp: u.mp, zin: u.zin, d: hdist(u.c, u.r, G.bases[tid].c, G.bases[tid].r), baseTarget: attackTargets(u).some(function (x) { return x.kind === "base"; }), atkOverlay: (UI.atk || []).some(function (x) { return x.kind === "base"; }), toast: $("toast").textContent }; }', info['tid'])
    print('entered zone', st)
    B.shot(pg, 'd7_1_entered', 200)
    taphex(pg, *info['t']); pg.wait_for_timeout(400)
    print('tap city → target', pg.evaluate('UI.target && UI.target.kind'), '| toast:', pg.evaluate('$("toast").textContent'))
    r = pg.evaluate('(tid) => { var u = selUnit(), b = G.bases[tid], res = unitAttack(u, { kind: "base", b: b, c: b.c, r: b.r }); return [res.ok, res.msg, u.done]; }', info['tid'])
    print('engine refuses', r)
    # 이동 취소 → 표시가 풀리는가, 다시 들어가면 다시 걸리는가
    tapsel(pg, '#sheet [data-a=undo]'); pg.wait_for_timeout(500)
    print('after undo', pg.evaluate('() => { var u = selUnit(); return [u.c, u.r, u.mp, u.zin]; }'))
    taphex(pg, *info['inn']); pg.wait_for_timeout(1700)
    print('re-entered', pg.evaluate('() => { var u = selUnit(); return [u.c, u.r, u.mp, u.zin]; }'))
    dt = end_turn(pg)
    alive = pg.evaluate('(id) => !!UMAP[id]', info['id'])
    print('next turn %.1fs' % dt, pg.evaluate('dateStr()'), 'unit alive', alive)
    if alive:
        moved = pg.evaluate("""([id, tid]) => { var u = UMAP[id], t = G.bases[tid]; if (hdist(u.c, u.r, t.c, t.r) <= uRange(u) && zoneAt(u.c, u.r) === tid) return false;
          for (var c = t.c - 3; c <= t.c + 3; c++) for (var r = t.r - 3; r <= t.r + 3; r++) { if (!inMap(c, r)) continue; var d = hdist(c, r, t.c, t.r), tt = terr(c, r);
            if (d < 1 || d > uRange(u) || zoneAt(c, r) !== tid || unitAt(c, r) || baseAt(c, r) || facAt(c, r) || tt === 'm' || tt === 'w' || tt === 's' || tt === 'x') continue;
            placeUnit(u, c, r); syncScene(); requestDraw(); return [c, r]; }
          return 'no free hex'; }""", [info['id'], info['tid']])
        print('pushed out of range by the enemy turn → put on a free hex in range:', moved)
        pg.evaluate('(id) => gotoUnit(UMAP[id])', info['id']); pg.wait_for_timeout(700)
        print('next turn state', pg.evaluate('(tid) => { var u = selUnit(); return { pos: [u.c, u.r], zin: u.zin, mp: u.mp, baseTarget: attackTargets(u).some(function (x) { return x.kind === "base" && x.b.id === tid; }) }; }', info['tid']))
        taphex(pg, *info['t']); pg.wait_for_timeout(400)
        n = pg.locator('#sheet [data-a=act]').count()
        print('acts', [pg.locator('#sheet [data-a=act]').nth(i).inner_text().replace('\n', ' / ') for i in range(n)])
        B.shot(pg, 'd7_2_nextturn', 200)
        if n:
            tapsel(pg, '#sheet [data-a=act]', 0); pg.wait_for_timeout(3200)
            print('attack toast:', pg.evaluate('$("toast").textContent'), '| busy', pg.evaluate('UI.busy'), 'fx', pg.evaluate('FX.live.length'))
    print('ERRORS', [e for e in B.errors if 'ERR_FILE_NOT_FOUND' not in e and 'GPU stall' not in e][:6])
B.run(steps, 390, 844, 2)
