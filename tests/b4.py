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
      var ns = nbrs(t.c, t.r).filter(free); placeUnit(u1, ns[0][0], ns[0][1]);
      var eo = idleOfficers(t).sort((x, y) => aiMilScore(y) - aiMilScore(x));
      var e1 = cmdDeploy(t, {type: "cav", ids: [eo[0].id], troops: 5000, food: 2000}).unit; e1.ai = {mode: "defend", home: t.id};
      var e2 = cmdDeploy(t, {type: "halberd", ids: [eo[1].id], troops: 3000, food: 2000}).unit; e2.ai = {mode: "defend", home: t.id};
      var near = [];
      for (var c = e1.c - 3; c <= e1.c + 3; c++) for (var r = e1.r - 3; r <= e1.r + 3; r++) if (inMap(c, r) && hdist(c, r, e1.c, e1.r) === 2 && free([c, r])) near.push([c, r]);
      placeUnit(u2, near[0][0], near[0][1]);
      var n2 = nbrs(e2.c, e2.r).filter(free); placeUnit(u3, n2[0][0], n2[0][1]);
      G.fires[K(near[1][0], near[1][1])] = 3; G.fires[K(near[2][0], near[2][1])] = 3;
      var p = hexCenter(t.c, t.r); cam.x = p[0]; cam.y = p[1] + 2; cam.z = 1.25; clampCam(); requestDraw(); refreshHud();
      selectUnit(u1);
      floatText(e1.c, e1.r, "-1,234", "#ff6a55", 0, false); floatText(t.c, t.r, "격퇴 크리티컬!", "#ffd76a", 0, true); flashHex(e2.c, e2.r, "#fff");
      UI.floats.forEach(function (f) { f.dur = 600000; f.t0 = performance.now() - (f.ring ? 200000 : 100000); });
      return 1;
    })()''')
    shot(pg, '50_battle', 2500)
    pg.evaluate('clearSel(); cam.z = 0.7; clampCam()'); shot(pg, '51_battle_mid', 1500)
run(steps, dpr=2)
print('ERRORS', [e for e in errors if 'ReadPixels' not in e][:12])
