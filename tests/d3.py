# v0.4 회귀: 내정·출진(처음 방식)·파란 칸 이동·이동 취소·[행군] 지정·전투 연출·턴 종료 재생·저장/불러오기·메뉴·도움말·미니맵
from browser import *
import browser
browser.SHOTS = os.path.join(ROOT, 'shots4')
def wait_play(pg, limit=150):
    t0 = time.time()
    while pg.evaluate('!!UI.play') and time.time() - t0 < limit: pg.wait_for_timeout(100)
    pg.wait_for_timeout(250); return time.time() - t0
def end_turn(pg):
    pg.evaluate('if (MODAL) closeDialog(); clearSel()')
    tapsel(pg, '#btnEnd'); pg.wait_for_timeout(150)
    if not pg.evaluate('!!UI.play') and not pg.evaluate('!!MODAL'): tapsel(pg, '#btnEnd')
    return wait_play(pg)
def steps(pg):
    start(pg, 0)
    pg.evaluate('UI.pspeed = 3')
    b = pg.evaluate('(function(){ var L = off(G.factions[G.player].lord), b = G.bases[L.loc]; return [b.c, b.r, b.id]; })()')
    taphex(pg, b[0], b[1]); print('base sheet', pg.evaluate('SHEET && !SHEET.home && UI.sel'))
    tapsel(pg, '#sheet [data-a=draft]'); tapsel(pg, '#modal [data-a=auto]'); tapsel(pg, '#modal [data-a=ok]')
    print('draft toast', pg.evaluate('$("toast").textContent'))
    tapsel(pg, '#sheet [data-a=tab][data-v=fac]')
    pg.locator('#sheet .lot[data-a=plot]').first.tap(); pg.wait_for_timeout(300)        # v0.9.2: 빈 부지는 번호 단추
    tapsel(pg, '#modal [data-a=f][data-v=farm]'); tapsel(pg, '#modal [data-a=auto]'); tapsel(pg, '#modal [data-a=ok]')
    print('develop toast', pg.evaluate('$("toast").textContent'))
    tapsel(pg, '#sheet [data-a=tab][data-v=men]'); tapsel(pg, '#sheet [data-a=search]'); tapsel(pg, '#modal [data-a=auto]'); tapsel(pg, '#modal [data-a=ok]')
    print('search toast', pg.evaluate('$("toast").textContent'))
    # 출진(처음 방식): 병과·무장만 정하면 성 앞에 나오고, 고른 채로 파란 칸이 보인다
    tapsel(pg, '#sheet [data-a=tab][data-v=mil]'); tapsel(pg, '#sheet [data-a=deploy]'); tapsel(pg, '#modal [data-a=auto]')
    print('deploy dialog has destination list:', pg.locator('#modal .dests').count(), '| note:', pg.locator('#modal .note').last.inner_text()[:40])
    tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(1300)
    print('deployed', pg.evaluate('JSON.stringify(facUnits(G.player).map(function(u){return [u.c,u.r,u.dest,u.mp,u.done]}))'), 'sel', pg.evaluate('UI.sel'), 'busy', pg.evaluate('UI.busy'), 'reach', pg.evaluate('UI.rc ? Object.keys(UI.rc.stop).length : -1'))
    # v0.18: 닿지 않는 땅을 누르면 곧바로 그곳으로 행군 → [이동 취소]로 제자리 · 명령도 거둔다
    hc = pg.evaluate('(function(){ var b = G.bases[baseByName("허창")]; return [b.c, b.r]; })()')
    far = pg.evaluate('(function(){ var u = selUnit(); return [u.c + 7, u.r + 3]; })()')
    at0 = pg.evaluate('(function(){ var u = selUnit(); return [u.c, u.r, u.dest]; })()')
    pg.evaluate('([c,r]) => onTap(c, r)', far); pg.wait_for_timeout(1600)
    print('far tap → march', pg.evaluate('(function(){ var u = selUnit(); return [u.c, u.r, u.dest >= 0, u.ox >= 0]; })()'), '| toast:', pg.evaluate('$("toast").textContent'), '| still selected', pg.evaluate('!!selUnit()'))
    tapsel(pg, '#sheet [data-a=undo]'); at1 = pg.evaluate('(function(){ var u = selUnit(); return [u.c, u.r, u.dest]; })()')
    print('undo → back', at1, '(was', at0, ')'); assert at1 == at0, ('이동 취소가 행군 명령을 거두지 못했다', at0, at1)
    # 파란 칸(성역 안)으로 이동 → 이동 취소 → 성역 밖으로 이동(그 턴 이동 끝)
    inz = pg.evaluate('(function(){ var u = selUnit(), z = zoneAt(u.c, u.r), ks = Object.keys(UI.rc.stop).map(Number), a = null, o = null; ks.forEach(function (k) { var c = k % W, r = (k - c) / W; if (BAT[k] !== undefined) return; if (ZONE[k] === z) { if (!a) a = [c, r]; } else o = [c, r]; }); return { a: a, o: o, mp: u.mp }; })()')
    taphex(pg, *inz['a']); pg.wait_for_timeout(1200)
    print('move inside zone', inz['a'], pg.evaluate('(function(){ var u = selUnit(); return [u.c, u.r, u.mp, zoneAt(u.c, u.r)]; })()'))
    tapsel(pg, '#sheet [data-a=undo]'); print('undo', pg.evaluate('(function(){ var u = selUnit(); return [u.c, u.r, u.mp]; })()'))
    taphex(pg, *inz['o']); pg.wait_for_timeout(1500)
    print('move across zone edge', inz['o'], pg.evaluate('(function(){ var u = selUnit(); return [u.c, u.r, u.mp, zoneAt(u.c, u.r), Object.keys(UI.rc.stop).length]; })()'), '| toast:', pg.evaluate('$("toast").textContent'))
    # v0.18: 목적지(허창)를 누른다 — 적의 성이면 공격 명령, 내 성 · 빈 성이면 그 성의 창에서 [이 성으로 행군]
    pg.evaluate('([c,r]) => onTap(c, r)', hc); pg.wait_for_timeout(400)
    if pg.locator('#sheet [data-a=marchhere]').count():
        print('base sheet → march here:', pg.locator('#sheet [data-a=marchhere]').inner_text().replace('\n', ' / ')); tapsel(pg, '#sheet [data-a=marchhere]')
    else: print('aim order:', pg.evaluate('(function(){ var u = facUnits(G.player)[0]; return [u.aim, aimName(u)]; })()'))
    pg.wait_for_timeout(1600)
    print('after march', pg.evaluate('JSON.stringify(facUnits(G.player).map(function(u){return [u.c,u.r,u.dest,u.mp,u.done]}))'), '|', pg.evaluate('(document.querySelector("#sheet .note") || {}).innerText'))
    dt = end_turn(pg); print('turn1 %.1fs' % dt, pg.evaluate('[dateStr(), UI.busy, MODAL && document.querySelector("#modal h2").innerText]'))
    dt = end_turn(pg); print('turn2 %.1fs' % dt, pg.evaluate('JSON.stringify(facUnits(G.player).map(function(u){return [u.c,u.r,u.dest,u.mp,u.done]}))'), pg.evaluate('REPORT.filter(function (e) { return e.f === G.player && e.imp >= 1; }).map(function (e) { return e.t; })'))
    dt = end_turn(pg); print('turn3 %.1fs' % dt, pg.evaluate('JSON.stringify(facUnits(G.player).map(function(u){return [u.c,u.r,u.dest,u.mp,u.done]}))'), pg.evaluate('REPORT.filter(function (e) { return e.f === G.player && e.imp >= 1; }).map(function (e) { return e.t; })'), 'bases', pg.evaluate('facBases(G.player).map(function (b) { return b.n; })'))
    pg.evaluate('if (MODAL) closeDialog()')
    # 전투(화면 조작): 복양 옆에 부대를 놓고 성과 적 부대를 공격
    info = pg.evaluate('''(() => {
      var b = G.bases[baseByName("진류")], t = G.bases[baseByName("복양")];
      G.factions[G.player].ap = 200; b.troops = 20000; b.w.spear = 9000; b.w.bow = 9000; b.food = 30000;
      var os = idleOfficers(b).sort((x, y) => aiMilScore(y) - aiMilScore(x));
      var u1 = cmdDeploy(b, {type: "spear", ids: [os[0].id], troops: 4000, food: 3000}).unit;
      var u2 = cmdDeploy(b, {type: "bow", ids: [os[1].id], troops: 4000, food: 2000}).unit;
      u1.born = u2.born = -1;                                  // v0.8: 출진한 턴에는 거점을 칠 수 없다 → 앞서 나온 부대로 친다
      function free(n) { var t2 = terr(n[0], n[1]); return t2 !== "m" && t2 !== "w" && t2 !== "s" && t2 !== "x" && !unitAt(n[0], n[1]) && !facAt(n[0], n[1]) && !baseAt(n[0], n[1]); }
      var ns = nbrs(t.c, t.r).filter(free);
      placeUnit(u1, ns[0][0], ns[0][1]);
      var es = G.units.filter(function (u) { return u.f !== G.player; }), e1 = null, i;
      for (i = 0; i < es.length && !e1; i++) { var cand = []; for (var c = es[i].c - 2; c <= es[i].c + 2; c++) for (var r = es[i].r - 2; r <= es[i].r + 2; r++) if (inMap(c, r) && hdist(c, r, es[i].c, es[i].r) === 2 && free([c, r])) cand.push([c, r]); if (cand.length) { e1 = es[i]; placeUnit(u2, cand[0][0], cand[0][1]); } }
      u1.morale = u2.morale = 90; requestDraw(); refreshHud();
      return {u1: [u1.c, u1.r], u2: [u2.c, u2.r], e1: e1 ? [e1.c, e1.r] : null, t: [t.c, t.r], id1: u1.id, id2: u2.id};
    })()''')
    print(info)
    pg.evaluate('(id) => gotoUnit(UMAP[id])', info['id1']); pg.wait_for_timeout(700)
    taphex(pg, *info['t']); pg.wait_for_timeout(300)
    print('acts(base)', [pg.locator('#sheet [data-a=act]').nth(i).inner_text().replace('\n', ' / ') for i in range(pg.locator('#sheet [data-a=act]').count())])
    tapsel(pg, '#sheet [data-a=act]', 0); pg.wait_for_timeout(350); print('busy during anim', pg.evaluate('UI.busy'), 'anims', pg.evaluate('UI.anims.length')); pg.wait_for_timeout(2600); print('attack base toast', pg.evaluate('$("toast").textContent'), '| busy', pg.evaluate('UI.busy'), 'fx', pg.evaluate('FX.live.length'))
    if info['e1']:
        pg.evaluate('(id) => gotoUnit(UMAP[id])', info['id2']); pg.wait_for_timeout(700)
        taphex(pg, *info['e1']); pg.wait_for_timeout(300)
        n = pg.locator('#sheet [data-a=act]').count(); print('acts(unit)', n, pg.evaluate('UI.target && UI.target.kind'))
        if n: tapsel(pg, '#sheet [data-a=act]', 0); pg.wait_for_timeout(3000); print('attack unit toast', pg.evaluate('$("toast").textContent'), '| busy', pg.evaluate('UI.busy'), 'fx', pg.evaluate('FX.live.length'))
    dt = end_turn(pg); print('turn4 %.1fs' % dt, pg.evaluate('[dateStr(), UI.busy, G.over]'))
    pg.evaluate('if (MODAL) closeDialog()')
    # 저장 → 새로 열기 → 이어하기
    tapsel(pg, '#btnMenu'); shot(pg, 'd3_menu', 300)
    tapsel(pg, '#modal [data-a=spd]'); print('menu speed', pg.evaluate('UI.pspeed'), pg.evaluate('document.querySelector("#modal [data-a=spd] small").innerText'))
    tapsel(pg, '#modal [data-a=save]'); tapsel(pg, '#modal [data-a=ssave]', 0); tapsel(pg, '#modal [data-a=close]')      # v0.10.1: 저장은 칸을 고른다(1번 칸) — 자동 저장도 같이 맞춰진다
    tapsel(pg, '#modal [data-a=help]'); shot(pg, 'd3_help', 300); pg.evaluate('closeDialog()')
    d1 = pg.evaluate('dateStr() + " u" + G.units.length + " o" + facOfficers(G.player).length + " opts " + localStorage.getItem("chunhado_opts")')
    pg.reload(); pg.wait_for_function('window.R3 && R3.ready', timeout=60000); pg.wait_for_timeout(500)
    tapsel(pg, '#tCont'); pg.wait_for_timeout(900)
    d2 = pg.evaluate('dateStr() + " u" + G.units.length + " o" + facOfficers(G.player).length + " opts " + localStorage.getItem("chunhado_opts")')
    print('save/load', d1 == d2, '|', d2, '| sheet', pg.evaluate('SHEET && SHEET.home'), 'pspeed', pg.evaluate('UI.pspeed'))
    shot(pg, 'd3_loaded', 500)
    # HUD 누르기 → STATUS 창, 미니맵, 확대
    pg.evaluate('gotoBase(facBases(G.player)[0])'); pg.wait_for_timeout(400); tapsel(pg, '#hud'); print('hud tap → home', pg.evaluate('SHEET && SHEET.home && UI.sel === null'))
    box = pg.locator('#mini').bounding_box(); c0 = pg.evaluate('[Math.round(cam.x), Math.round(cam.y)]')
    pg.touchscreen.tap(box['x'] + box['width'] * 0.2, box['y'] + box['height'] * 0.7); pg.wait_for_timeout(400)
    print('minimap jump', c0, '->', pg.evaluate('[Math.round(cam.x), Math.round(cam.y)]'))
    pg.mouse.move(200, 400); pg.mouse.wheel(0, -600); pg.wait_for_timeout(300); print('zoom', pg.evaluate('cam.z'))
    dt = end_turn(pg); print('turn5 %.1fs' % dt, pg.evaluate('[dateStr(), UI.busy, G.over]'))
run(steps, 390, 844, 1)
print('ERRORS', [e for e in errors if 'ReadPixels' not in e and 'ERR_FILE_NOT_FOUND' not in e and 'ERR_FAILED' not in e][:12])
