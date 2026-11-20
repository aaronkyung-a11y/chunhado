# v0.10.1 화면 찍기(고른 시설 표시 · 공사장 그림 · 세이브 칸):  python3 tests/shot101.py [w=396] [h=859] [dpr=2]   → tests/shots22/
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import taphex, tapsel
B.SHOTS = os.path.join(B.ROOT, 'shots22')
os.makedirs(B.SHOTS, exist_ok=True)
W = int(sys.argv[1]) if len(sys.argv) > 1 else 396
H = int(sys.argv[2]) if len(sys.argv) > 2 else 859
D = int(sys.argv[3]) if len(sys.argv) > 3 else 2
SETUP = '''(() => {
  var b = facCities(G.player)[0], F = function (t, lv) { return { t: t, lv: lv || 1, done: true, prog: 0, need: 0, rate: 0, hp: FAC_HP }; };
  var C = function (t, k) { return { t: t, lv: 1, done: false, prog: Math.round(FAC[t].build * k), need: FAC[t].build, rate: 120, hp: 300, by: [], t0: G.turn }; };
  var no = lotNos(b), byNo = {}; for (var i = 0; i < b.plots.length; i++) byNo[no[i]] = i;
  b.plots.forEach(function (p) { p.fac = null; });
  var plan = { 1: F('market', 2), 3: F('market', 2), 5: F('market'), 7: F('smithy'), 9: F('farm'), 11: C('farm', 0.5), 12: C('barracks', 0.1), 13: C('barracks', 0.8), 2: C('market', 0.2) };
  for (var k in plan) if (byNo[k] !== undefined) b.plots[byNo[k]].fac = plan[k];
  G.factions[G.player].ap = 235; b.gold = 741; reindex(); selectBase(b); UI.dirty = true; requestDraw();
  return { id: b.id, n: b.n, plots: b.plots.length };
})()'''
def steps(pg):
    tapsel(pg, '#tNew'); pg.wait_for_timeout(300)
    tapsel(pg, '#modal .row', 13); tapsel(pg, '#modal [data-a=go]'); pg.wait_for_timeout(600)
    tapsel(pg, '#modal [data-a=close]'); pg.wait_for_timeout(1200)
    pg.evaluate('talkHide()')
    print(pg.evaluate(SETUP)); pg.wait_for_timeout(700)
    pg.locator('#sheet .tabs button').nth(3).tap(); pg.wait_for_timeout(1200); B.shot(pg, 'f01_tab', 300)
    rows = pg.evaluate('Array.from(document.querySelectorAll("#sheet .row[data-a=plot]")).map(function (r) { return r.textContent.slice(0, 30); })')
    print(rows)
    pg.locator('#sheet .row[data-a=plot]').nth(2).tap(); pg.wait_for_timeout(1300); B.shot(pg, 'f02_market_sel', 300)       # ③ 시장 Lv2(다 지은 것, 성 바로 뒤)
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(700)
    pg.locator('#sheet .row[data-a=plot]').nth(1).tap(); pg.wait_for_timeout(1300); B.shot(pg, 'f02b_site_market', 300)    # ② 시장(짓는 중)
    print('dlg', pg.evaluate('document.querySelector("#modal .dlg-h").textContent'), '| see', pg.evaluate('document.getElementById("modal").className'), '| app', pg.evaluate('document.getElementById("app").className'))
    # 지도에서 다른 시설을 누른다(짓는 중인 병영)
    q = pg.evaluate('(() => { var b = G.bases[MODAL.fsel.b]; for (var i = 0; i < b.plots.length; i++) if (b.plots[i].fac && !b.plots[i].fac.done && b.plots[i].fac.t === "barracks") return [b.plots[i].c, b.plots[i].r]; })()')
    taphex(pg, q[0], q[1]); pg.wait_for_timeout(900); B.shot(pg, 'f03_site_sel', 300)
    print('dlg', pg.evaluate('document.querySelector("#modal .dlg-h").textContent'))
    # 빈 부지를 누른다 → '무엇을 지을까요'
    q = pg.evaluate('(() => { var b = G.bases[MODAL.fsel.b]; for (var i = 0; i < b.plots.length; i++) if (!b.plots[i].fac) return [b.plots[i].c, b.plots[i].r]; })()')
    taphex(pg, q[0], q[1]); pg.wait_for_timeout(900); B.shot(pg, 'f04_to_lot', 300)
    print('dlg', pg.evaluate('MODAL ? document.querySelector("#modal .dlg-h").textContent : "-"'))
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(600)
    pg.evaluate('clearSel()'); pg.wait_for_timeout(900); B.shot(pg, 'f05_map', 300)       # 평소의 지도: 공사장 그림
    pg.evaluate('(() => { var b = facCities(G.player)[0], p = hexCenter(b.c, b.r); cam.x = p[0]; cam.y = p[1]; cam.z = 1.9; clampCam(); requestDraw(); })()'); pg.wait_for_timeout(900); B.shot(pg, 'f06_map_zoom', 300)
B.run(steps, W, H, D)
print('errors:', B.errors[:5])
