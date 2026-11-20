# v0.9.2 — 화면에 보이는 글의 양을 잰다(같은 판·같은 장면에서, 빈칸을 뺀 글자 수)
#   python3 tests/text92.py                      지금 빌드(dist/offline.html)
#   PAGE=../chunhado-v0.9.1-offline.html python3 tests/text92.py      0.9.1 과 견줄 때
#   보이는 글 = innerText(접힌 토막·숨긴 것은 빠진다). 도움말은 전체 글(textContent)도 함께 적는다.
#   끝에 JSON 한 줄(TEXT92 {...})을 찍는다 — 두 판의 값을 나란히 놓을 때 쓴다.
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import taphex, tapsel
FREE = '''function free(c, r) { var t2 = terr(c, r); return inMap(c, r) && t2 === "p" && !unitAt(c, r) && !plotAt(c, r) && !baseAt(c, r) && !G.fires[K(c, r)]; }'''
OUT = {}
def n(pg, sel, name, vis=True):
    v = pg.evaluate('([s, vis]) => { var e = document.querySelector(s); if (!e) return -1; return (vis ? e.innerText : e.textContent).replace(/\\s+/g, "").length; }', [sel, vis])
    OUT[name] = v
    print('  %-28s %5d' % (name, v))
def steps(pg):
    tapsel(pg, '#tNew'); pg.wait_for_timeout(300)
    tapsel(pg, '#modal .row', 2); pg.wait_for_timeout(200)
    tapsel(pg, '#modal [data-a=go]'); pg.wait_for_timeout(600)
    n(pg, '#modal .dlg', '시작 안내')
    tapsel(pg, '#modal [data-a=close]'); pg.wait_for_timeout(500)
    # 같은 판으로: 씨앗을 정해 새로 만들고 저장한 뒤 이어 하기
    pg.evaluate('() => { newGame(2, 4242); saveGame(); }')
    pg.reload(); pg.wait_for_function('window.R3 && R3.ready', timeout=60000); pg.wait_for_timeout(600)
    tapsel(pg, '#tCont'); pg.wait_for_timeout(1200)
    if pg.evaluate('!!MODAL'): pg.evaluate('closeDialog()')
    pg.evaluate('() => { clearSel(); }'); pg.wait_for_timeout(300)
    n(pg, '#sheet', 'STATUS 창(첫 턴)')
    pg.evaluate('showPeaceInfo()'); pg.wait_for_timeout(250); n(pg, '#modal .dlg', '초반 보호 풀이'); pg.evaluate('closeDialog()')
    pg.evaluate('showAdvisor()'); pg.wait_for_timeout(250); n(pg, '#modal .dlg', '군사 창'); pg.evaluate('closeDialog()')
    st = pg.evaluate('''(() => { %s
      var b = facCities(G.player)[0], spot = null;
      G.factions[G.player].ap = 200; b.troops = 30000; b.w.spear = 20000; b.w.halberd = 20000; b.food = 60000;
      for (var c = b.c - 8; c <= b.c + 8 && !spot; c++) for (var r = b.r - 8; r <= b.r + 8 && !spot; r++) {
        if (!free(c, r) || hdist(c, r, b.c, b.r) < 4) continue;
        var ns = nbrs(c, r).filter(function (q) { return free(q[0], q[1]) && hdist(q[0], q[1], b.c, b.r) >= 4; });
        if (ns.length === 6) spot = { me: [c, r], foe: ns[0] };
      }
      var os = idleOfficers(b), strong = os.filter(function (o) { return o.n === "관우"; })[0], z = os.filter(function (o) { return o.n === "장비"; })[0];
      var u = cmdDeploy(b, {type: "spear", ids: [strong.id], troops: Math.min(6000, cmdCap(strong)), food: 4000}).unit, u2 = cmdDeploy(b, {type: "spear", ids: [z.id], troops: 4000, food: 600}).unit;
      var eb = G.bases[baseByName("복양")], eo = baseOfficers(eb).filter(function (o) { return o.n === "장료"; })[0];
      eb.w.spear = 9000; eb.troops = 30000; G.factions[eb.owner].ap = 200;
      var e = cmdDeploy(eb, {type: "spear", ids: [eo.id], troops: Math.min(6000, cmdCap(eo)), food: 3000}).unit; e.ai = { mode: "return" };
      placeUnit(u, spot.me[0], spot.me[1]); placeUnit(e, spot.foe[0], spot.foe[1]);
      [u, u2].forEach(function (x) { x.mp = uMaxMp(x); x.done = false; x.moved = false; x.ox = -1; x.born = -1; x.morale = 100; });
      syncScene(); requestDraw(); refreshHud(); clearSel(); showHome();
      return { u: u.id, u2: u2.id, e: e.id, ep: [e.c, e.r], b: b.id };
    })()''' % FREE)
    pg.wait_for_timeout(400)
    n(pg, '#sheet', 'STATUS 창(부대를 낸 뒤)')
    pg.evaluate('(id) => gotoUnit(UMAP[id])', st['u']); pg.wait_for_timeout(700); n(pg, '#sheet', '부대 창')
    taphex(pg, *st['ep']); pg.wait_for_timeout(500); n(pg, '#sheet', '부대 창(대상을 고름)')
    tapsel(pg, '#sheet [data-a=tacinfo]'); pg.wait_for_timeout(400); n(pg, '#modal .dlg', '전법 풀이'); n(pg, '#modal .dlg', '전법 풀이(접힌 것까지)', False)
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(200)
    pg.evaluate('(id) => { clearSel(); selectUnit(UMAP[id]); }', st['e']); pg.wait_for_timeout(500); n(pg, '#sheet', '적 부대 창')
    pg.evaluate('(b) => { clearSel(); selectBase(G.bases[b]); }', st['b']); pg.wait_for_timeout(500)
    for i, nm in enumerate(['내정', '출진(군사)', '인재', '건설(시설)']):
        pg.locator('#sheet .tabs button').nth(i).tap(); pg.wait_for_timeout(300); n(pg, '#sheet', '거점 창 — ' + nm)
    pg.locator('#sheet .lot[data-a=plot], #sheet .row[data-a=plot]').first.tap(); pg.wait_for_timeout(500); n(pg, '#modal .dlg', '무엇을 지을까요'); pg.evaluate('closeDialog()'); pg.wait_for_timeout(200)
    for a, tab, nm in [('deploy', 1, '출진 창'), ('recruit', 2, '등용 창'), ('search', 2, '탐색 창'), ('draft', 0, '징병 창')]:
        pg.evaluate('(b) => { if (MODAL) closeDialog(); selectBase(G.bases[b]); }', st['b']); pg.wait_for_timeout(150)
        pg.locator('#sheet .tabs button').nth(tab).tap(); pg.wait_for_timeout(200)
        if pg.locator('#sheet [data-a=%s]' % a).count():
            pg.locator('#sheet [data-a=%s]' % a).first.tap(); pg.wait_for_timeout(350)
            if pg.evaluate('!!MODAL'): n(pg, '#modal .dlg', nm)
    pg.evaluate('if (MODAL) closeDialog()')
    pg.evaluate('showMenu()'); pg.wait_for_timeout(250); n(pg, '#modal .dlg', '메뉴'); pg.evaluate('closeDialog()')
    pg.evaluate('showHelp()'); pg.wait_for_timeout(250); n(pg, '#modal .dlg', '도움말(보이는 글)'); n(pg, '#modal .dlg', '도움말(전체)', False); pg.evaluate('closeDialog()')
B.run(steps, 390, 844, 2)
errs = [e for e in B.errors if 'GPU stall' not in e and 'ERR_FILE_NOT_FOUND' not in e]
print('console errors:', errs[:5])
print('TEXT92 ' + json.dumps(OUT, ensure_ascii=False))
sys.exit(1 if errs else 0)
