# v0.11 화면 찍기(등용과 옛 관계):  python3 tests/shot11b.py   → tests/shots24/
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
  var me = G.player, foe = 1, cap = facCities(me)[0], fb = facBases(foe)[0], FL = off(G.factions[foe].lord);
  var r = cmdDeploy(cap, { type: 'sword', ids: idleOfficers(cap).filter(function (o) { return !isLord(o); }).slice(0, 3).map(function (o) { return o.id; }), troops: 3000, food: 1500 });
  captureBase(fb, r.unit);
  // 장료를 미리 등용해 둔다(주사위 0) — 옛 동료가 권하는 모습을 보려고
  var rr = recruitRoll; recruitRoll = function () { return 0; };
  var zl = null; fb.captives.forEach(function (id) { if (off(id).n === '장료') zl = off(id); });
  G.officers.forEach(function (o) { if (o.f === me) o.acted = false; });
  var s0 = idleOfficers(fb)[0]; var j = zl && s0 ? cmdRecruit(fb, s0.id, zl.id) : null;
  recruitRoll = rr;
  G.officers.forEach(function (o) { if (o.f === me) o.acted = false; });
  G.factions[me].ap = 200; fb.gold = 900; reindex(); syncScene(); selectBase(fb); UI.dirty = true; requestDraw();
  return { fb: fb.n, alive: G.factions[foe].alive, caps: fb.captives.length, joined: j && j.joined, idle: idleOfficers(fb).map(function (o) { return o.n; }) };
})()'''
def steps(pg):
    tapsel(pg, '#tNew'); pg.wait_for_timeout(300)
    tapsel(pg, '#modal .row', 0); tapsel(pg, '#modal [data-a=go]'); pg.wait_for_timeout(600)
    tapsel(pg, '#modal [data-a=close]'); pg.wait_for_timeout(1200)
    pg.evaluate('talkHide()')
    print(pg.evaluate(SETUP)); pg.wait_for_timeout(900)
    tabs = pg.evaluate('Array.from(document.querySelectorAll("#sheet .tabs button")).map(function (x) { return x.textContent; })'); print(tabs)
    pg.locator('#sheet .tabs button').nth(2).tap(); pg.wait_for_timeout(700); B.shot(pg, 'g01_men', 300)
    tapsel(pg, '#sheet [data-a=recruit]'); pg.wait_for_timeout(700); B.shot(pg, 'g02_recruit', 300)
    rows = pg.evaluate('Array.from(document.querySelectorAll("#modal .row")).map(function (r) { return r.querySelector(".nm").innerText + " | " + (r.querySelector(".rt") ? r.querySelector(".rt").innerText.replace(/\\n/g, " / ") : ""); })')
    for r in rows: print('  ', r)
    # 여포를 고른다(옛 신하 장료가 있다)
    idx = pg.evaluate('Array.from(document.querySelectorAll("#modal .row")).findIndex(function (r) { return /여포/.test(r.querySelector(".nm").textContent); })')
    pg.locator('#modal .row').nth(idx).tap(); pg.wait_for_timeout(700)
    print('  pick:', pg.evaluate('Array.from(document.querySelectorAll("#modal .tr")).map(function (r) { return r.querySelector(".c-n").innerText + " " + r.querySelector(".c-x").innerText.replace(/\\n/g, "/"); })'))
    tapsel(pg, '#modal [data-a=auto]'); pg.wait_for_timeout(500); B.shot(pg, 'g03_pick_lord', 300)
    print('  pv:', pg.evaluate('document.querySelector("#modal .pv").innerText.replace(/\\n/g, " / ")'))
    pg.evaluate('backDialog()'); pg.wait_for_timeout(400)
    # 고순(멸망한 세력 출신, 옛 동료 장료)
    idx = pg.evaluate('Array.from(document.querySelectorAll("#modal .row")).findIndex(function (r) { return /고순/.test(r.querySelector(".nm").textContent); })')
    pg.locator('#modal .row').nth(idx).tap(); pg.wait_for_timeout(700)
    tapsel(pg, '#modal [data-a=auto]'); pg.wait_for_timeout(500); B.shot(pg, 'g04_pick_mate', 300)
    print('  pv:', pg.evaluate('document.querySelector("#modal .pv").innerText.replace(/\\n/g, " / ")'))
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(400)
    # 포로 창
    tapsel(pg, '#sheet [data-a=captive]'); pg.wait_for_timeout(700); B.shot(pg, 'g05_captive', 300)
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(300)
    # 장료의 무장 창(섬겼던 세력)
    pg.evaluate('(() => { var z = G.officers.filter(function (o) { return o.n === "장료"; })[0]; showOfficer(z); })()'); pg.wait_for_timeout(600)
    pg.evaluate('document.querySelector("#modal .dlg-b").scrollTop = 99999'); B.shot(pg, 'g06_officer_past', 300)
    print('errors:', [e for e in B.errors if 'GPU stall' not in e and 'GL Driver' not in e and 'ERR_FILE_NOT_FOUND' not in e])
B.run(steps, W, H, D)
