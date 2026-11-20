from browser import *
def steps(pg):
    start(pg, 0)
    info = pg.evaluate('''(() => {
      var b = G.bases[baseByName("진류")], t = G.bases[baseByName("복양")];
      var os = idleOfficers(b).sort((x, y) => aiMilScore(y) - aiMilScore(x));
      var u1 = cmdDeploy(b, {type: "spear", ids: [os[0].id, os[1].id], troops: 6000, food: 3000}).unit;
      var u2 = cmdDeploy(b, {type: "bow", ids: [os[2].id], troops: 4000, food: 2000}).unit;
      var u3 = cmdDeploy(b, {type: "cav", ids: [os[3].id], troops: 3000, food: 2000}).unit;
      function free(n) { var t2 = terr(n[0], n[1]); return t2 !== "m" && t2 !== "w" && t2 !== "s" && t2 !== "x" && !unitAt(n[0], n[1]) && !facAt(n[0], n[1]) && !baseAt(n[0], n[1]); }
      var ns = nbrs(t.c, t.r).filter(free);
      placeUnit(u1, ns[0][0], ns[0][1]);
      var eo = idleOfficers(t).sort((x, y) => aiMilScore(y) - aiMilScore(x));
      var e1 = cmdDeploy(t, {type: "cav", ids: [eo[0].id], troops: 5000, food: 2000}).unit; e1.ai = {mode: "defend", home: t.id};
      var e2 = cmdDeploy(t, {type: "spear", ids: [eo[1].id], troops: 5000, food: 2000}).unit; e2.ai = {mode: "defend", home: t.id};
      var near = [];
      for (var c = e1.c - 3; c <= e1.c + 3; c++) for (var r = e1.r - 3; r <= e1.r + 3; r++) if (inMap(c, r) && hdist(c, r, e1.c, e1.r) === 2 && free([c, r])) near.push([c, r]);
      placeUnit(u2, near[0][0], near[0][1]);
      var n2 = nbrs(e2.c, e2.r).filter(free);
      placeUnit(u3, n2[0][0], n2[0][1]);
      u1.morale = u2.morale = u3.morale = 90;
      G.fires[K(near[1][0], near[1][1])] = 3;
      var p = hexCenter(t.c, t.r); cam.x = p[0]; cam.y = p[1] + 3; cam.z = 1.05; clampCam(); requestDraw(); refreshHud();
      return {u1: [u1.c, u1.r], u2: [u2.c, u2.r], u3: [u3.c, u3.r], e1: [e1.c, e1.r], e2: [e2.c, e2.r], t: [t.c, t.r]};
    })()''')
    print(info)
    shot(pg, '30_setup', 900)
    taphex(pg, *info['u1']); pg.wait_for_timeout(500); shot(pg, '31_sel_u1')
    print('sel', pg.evaluate('JSON.stringify(UI.sel)'))
    taphex(pg, *info['t']); pg.wait_for_timeout(300); shot(pg, '32_target_base')
    tapsel(pg, '#sheet [data-a=act]', 0); shot(pg, '33_attack_base', 250)
    pg.wait_for_timeout(900)
    taphex(pg, *info['u2']); pg.wait_for_timeout(600)
    print('sel', pg.evaluate('JSON.stringify(UI.sel)'))
    taphex(pg, *info['e1']); pg.wait_for_timeout(300); shot(pg, '34_target_unit')
    n = pg.locator('#sheet [data-a=act]').count(); print('acts', n, [pg.locator('#sheet [data-a=act]').nth(i).inner_text().replace('\n', ' / ') for i in range(n)])
    tapsel(pg, '#sheet [data-a=act]', 1); shot(pg, '35_tactic', 200)
    pg.wait_for_timeout(900)
    pg.evaluate('cam.z = 0.5; clampCam()'); shot(pg, '36_mid')
    pg.evaluate('clearSel()'); print('pre', pg.evaluate('[dateStr(), UI.busy, !!MODAL, pendingUnits().length, UI.anims.length]'))
    tapsel(pg, '#btnEnd'); pg.wait_for_timeout(400); print('tap1', pg.evaluate('[dateStr(), UI.busy, !!MODAL, document.getElementById("toast").textContent, document.getElementById("veil").className]'))
    if pg.locator('#modal.on').count() == 0 and pg.locator('#veil.on').count() == 0: tapsel(pg, '#btnEnd')
    pg.wait_for_timeout(1800); print('tap2', pg.evaluate('[dateStr(), UI.busy, !!MODAL, document.getElementById("toast").textContent]')); shot(pg, '38_report')
    if pg.locator('#modal.on').count(): tapsel(pg, '#modal [data-a=close]')
    shot(pg, '39_after')
    tapsel(pg, '#btnMenu'); shot(pg, '40_menu'); tapsel(pg, '#modal [data-a=save]'); tapsel(pg, '#modal [data-a=ssave]', 0); pg.evaluate('closeDialog()')      # v0.10.1: 저장은 칸을 고른다
    d1 = pg.evaluate('dateStr() + " " + G.units.length')
    pg.reload(); pg.wait_for_function('window.R3 && R3.ready', timeout=60000); pg.wait_for_timeout(500)
    tapsel(pg, '#tCont'); pg.wait_for_timeout(800)
    d2 = pg.evaluate('dateStr() + " " + G.units.length')
    print('save/load', d1, '|', d2)
    shot(pg, '41_loaded')
    tapsel(pg, '#btnList'); shot(pg, '42_list'); tapsel(pg, '#modal [data-a=tab][data-v=unit]'); shot(pg, '43_list_unit')
run(steps)
print('ERRORS', [e for e in errors if 'ReadPixels' not in e][:12])
