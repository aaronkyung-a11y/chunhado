# v0.11 화면 찍기(시설 레벨 표시 · 적성 · 치안 · 출진 군량 · 공유):  python3 tests/shot11.py [w=396] [h=859] [dpr=2]   → tests/shots24/
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import taphex, tapsel
B.SHOTS = os.path.join(B.ROOT, 'shots24')
os.makedirs(B.SHOTS, exist_ok=True)
W = int(sys.argv[1]) if len(sys.argv) > 1 else 396
H = int(sys.argv[2]) if len(sys.argv) > 2 else 859
D = int(sys.argv[3]) if len(sys.argv) > 3 else 2
SETUP = '''(() => {
  var b = facCities(G.player)[0], F = function (t, lv) { return { t: t, lv: lv || 1, done: true, prog: 0, need: 0, rate: 0, hp: FAC_HP }; };
  function adj(i) { var p = b.plots[i], out = []; nbrs(p.c, p.r).forEach(function (n) { var q = PAT[K(n[0], n[1])]; if (q && q.b === b.id) out.push(q.i); }); return out; }
  b.plots.forEach(function (p) { p.fac = null; });
  var A = -1, best = 0; for (var i = 0; i < b.plots.length; i++) { var n = adj(i).length; if (n > best) { best = n; A = i; } }
  var ns = adj(A), used = {}; used[A] = 1;
  b.plots[A].fac = F('market', 2);
  b.plots[ns[0]].fac = F('market', 1); used[ns[0]] = 1;
  b.plots[ns[1]].fac = F('mint', 1); used[ns[1]] = 1;
  var rest = []; for (i = 0; i < b.plots.length; i++) if (!used[i]) rest.push(i);
  var plan = [F('farm', 3), F('barracks', 2), F('barracks', 1), F('smithy', 1), F('granary', 1), F('workshop', 1), F('stable', 3)];
  for (i = 0; i < plan.length && i < rest.length; i++) b.plots[rest[i]].fac = plan[i];
  G.factions[G.player].ap = 235; b.gold = 2400; b.order = 64; b.food = 9000; b.troops = 14000; b.w.spear = 9000; b.w.horse = 4000; reindex(); selectBase(b); UI.dirty = true; requestDraw();
  return { id: b.id, n: b.n, plots: b.plots.length, A: lotNo(b, A), adj: best };
})()'''
def steps(pg):
    B.shot(pg, 'a00_title', 600)
    tapsel(pg, '#tShare'); pg.wait_for_timeout(700); B.shot(pg, 'a01_share', 300)
    print('share dlg:', pg.evaluate('MODAL ? document.querySelector("#modal .dlg-h").textContent : "-"'), '| url', pg.evaluate('document.getElementById("shU") ? document.getElementById("shU").value : "-"'))
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(300)
    tapsel(pg, '#tNew'); pg.wait_for_timeout(300)
    tapsel(pg, '#modal .row', 13); tapsel(pg, '#modal [data-a=go]'); pg.wait_for_timeout(600)
    tapsel(pg, '#modal [data-a=close]'); pg.wait_for_timeout(1200)
    pg.evaluate('talkHide()')
    print(pg.evaluate(SETUP)); pg.wait_for_timeout(700)
    B.shot(pg, 'b01_home', 300)
    tapsel(pg, '#sheet [data-a=order]'); pg.wait_for_timeout(600); B.shot(pg, 'b02_order', 300); pg.evaluate('closeDialog()'); pg.wait_for_timeout(300)
    tapsel(pg, '#sheet [data-a=patrol]'); pg.wait_for_timeout(500); tapsel(pg, '#modal [data-a=auto]'); pg.wait_for_timeout(400); B.shot(pg, 'b03_patrol', 300); pg.evaluate('closeDialog()'); pg.wait_for_timeout(300)
    tabs = pg.evaluate('Array.from(document.querySelectorAll("#sheet .tabs button")).map(function (x) { return x.textContent; })'); print(tabs)
    pg.locator('#sheet .tabs button').nth(3).tap(); pg.wait_for_timeout(1200); B.shot(pg, 'c01_fac_tab', 300)
    rows = pg.evaluate('Array.from(document.querySelectorAll("#sheet .row[data-a=plot]")).map(function (r) { return r.querySelector(".nm").textContent + " | " + r.querySelector(".ds").textContent + (r.querySelector(".rt") ? " | " + r.querySelector(".rt").textContent : ""); })')
    for r in rows: print('  ', r)
    n = len(rows)
    for i in range(n):
        pg.locator('#sheet .row[data-a=plot]').nth(i).tap(); pg.wait_for_timeout(900)
        print('  dlg', pg.evaluate('document.querySelector("#modal .dlg-h").textContent'), '→', pg.evaluate('document.querySelector("#modal .card p").innerText.replace(/\\n/g, " / ")'), '||', pg.evaluate('(document.querySelector("#modal .note:last-of-type") || {innerText: ""}).innerText.replace(/\\n/g, " / ")'))
        B.shot(pg, 'c02_fac_%d' % i, 200)
        if i == 0:
            if pg.evaluate('!!document.querySelector("#modal [data-a=merge].pri")'):
                tapsel(pg, '#modal [data-a=merge]'); pg.wait_for_timeout(500); tapsel(pg, '#modal [data-a=auto]'); pg.wait_for_timeout(400); B.shot(pg, 'c03_merge', 200)
                print('  merge pv:', pg.evaluate('document.querySelector("#modal .pv").innerText.replace(/\\n/g, " / ")'))
                pg.evaluate('backDialog()'); pg.wait_for_timeout(300)
        pg.evaluate('closeDialog()'); pg.wait_for_timeout(500)
    # 무장 줄 · 무장 창
    pg.locator('#sheet .tabs button').nth(2).tap(); pg.wait_for_timeout(700); B.shot(pg, 'd01_men', 300)
    pg.locator('#sheet .row[data-a=off]').nth(0).tap(); pg.wait_for_timeout(700); B.shot(pg, 'd02_officer', 300); pg.evaluate('closeDialog()'); pg.wait_for_timeout(300)
    # 출진
    pg.locator('#sheet .tabs button').nth(1).tap(); pg.wait_for_timeout(700)
    tapsel(pg, '#sheet [data-a=deploy]'); pg.wait_for_timeout(700); B.shot(pg, 'e01_deploy', 300)
    tapsel(pg, '#modal [data-a=auto]'); pg.wait_for_timeout(600)
    pg.evaluate('document.querySelector("#modal .dlg-b").scrollTop = 99999'); pg.wait_for_timeout(300); B.shot(pg, 'e02_deploy_food', 300)
    print('  food opts:', pg.evaluate('Array.from(document.querySelectorAll("#modal [data-a=turns]")).map(function (x) { return x.innerText.replace(/\\n/g, " "); })'), '| note:', pg.evaluate('document.getElementById("dpN").innerText'), '| pv:', pg.evaluate('document.getElementById("dpP").innerText'))
    pg.evaluate('(() => { var r = document.getElementById("dpR"); r.value = 3000; r.dispatchEvent(new Event("input", { bubbles: true })); })()'); pg.wait_for_timeout(300)
    print('  after slider:', pg.evaluate('Array.from(document.querySelectorAll("#modal [data-a=turns]")).map(function (x) { return x.innerText.replace(/\\n/g, " "); })'), '| note:', pg.evaluate('document.getElementById("dpN").innerText'))
    pg.locator('#modal [data-a=turns]').nth(3).tap(); pg.wait_for_timeout(400); B.shot(pg, 'e03_deploy_360', 300)
    print('  360:', pg.evaluate('document.getElementById("dpN").innerText'), '| pv:', pg.evaluate('document.getElementById("dpP").innerText'))
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(300)
    # 메뉴 → 공유
    pg.evaluate('showMenu()'); pg.wait_for_timeout(600); B.shot(pg, 'f01_menu', 300)
    tapsel(pg, '#modal [data-a=share]'); pg.wait_for_timeout(700); B.shot(pg, 'f02_menu_share', 300)
    tapsel(pg, '#modal [data-a=copy]'); pg.wait_for_timeout(500); print('  toast:', pg.evaluate('document.getElementById("toast").textContent'))
    # 목록 → 무장
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(300)
    print('errors:', B.errors)
B.run(steps, W, H, D)
