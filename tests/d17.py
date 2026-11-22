# v0.9.1 — 화면 조작으로 확인
#   1) 기간을 턴 수가 아니라 날짜·날수·개월로 적는가(군주 고르기 · 시작 안내 · STATUS 창)   2) 짧아진 초반 보호(유비 6개월 · 여포 4개월 · 조조 3개월)
#   3) 전법 풀이의 '기대 피해 · 받는 반격'이 규칙의 값(tacticExpect)과 같은가, 공격 단추의 '예상'이 attackExpect 와 같은가, 강한 쪽·약한 쪽이 다르게 나오는가
#   4) 0.9 에서 하던 판(보호의 끝이 옛 기간으로 저장됨)을 이어 하면 보호가 당겨지고 그 사실이 보이는가
#   python3 tests/d17.py          찍은 그림은 tests/shots17/
import sys, os, re, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import taphex, tapsel
B.SHOTS = os.path.join(B.ROOT, 'shots17')
os.makedirs(B.SHOTS, exist_ok=True)
fails = []
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)
TURNS = re.compile(r'[0-9]\s*턴')
FREE = '''function free(c, r) { var t2 = terr(c, r); return inMap(c, r) && t2 === "p" && !unitAt(c, r) && !plotAt(c, r) && !baseAt(c, r) && !G.fires[K(c, r)]; }'''
def steps(pg):
    # ---------- 1. 군주 고르기 · 시작 안내 · STATUS 창 ----------
    tapsel(pg, '#tNew'); pg.wait_for_timeout(300)
    rows = pg.evaluate('''Array.prototype.map.call(document.querySelectorAll("#modal .row"), function (e) { return e.innerText.replace(/\\n/g, " / "); })''')
    ok('초반 보호 3개월' in rows[4] and '초반 보호 4개월' in rows[1] and '초반 보호 6개월' in rows[2], '군주 고르기: 원소(42,000명) 3개월 · 여포(14,000명) 4개월 · 유비(7,000명) 6개월 [%s | %s | %s]' % (rows[4][-22:], rows[1][-22:], rows[2][-22:]))
    ok(not any(TURNS.search(r) for r in rows), '군주 고르기에 "N턴"이 없다')
    tapsel(pg, '#modal .row', 2); pg.wait_for_timeout(200)
    foot = pg.evaluate('document.querySelector("#modal .dlg-f .pv").innerText')
    ok('초반 보호 6개월(194년 6월 하순까지)' in foot, '고른 세력 아래: 초반 보호 6개월(194년 6월 하순까지) [%s]' % foot.replace('\n', ' / '))
    B.shot(pg, 'a1_select', 200)
    tapsel(pg, '#modal [data-a=go]'); pg.wait_for_timeout(600)
    intro = pg.evaluate('document.querySelector("#modal").innerText')
    ok('194년 6월 하순까지(6개월)' in intro and not TURNS.search(intro), '시작 안내: 194년 6월 하순까지(6개월), "N턴" 없음')
    tapsel(pg, '#modal [data-a=close]'); pg.wait_for_timeout(600)
    home = pg.evaluate('''(() => { var pz = document.querySelector("#sheet .pz"); return { pz: pz ? pz.className + ":" + pz.innerText : "", all: document.querySelector("#sheet").innerText, v: GAME_VERSION, until: G.peace.until, pv: G.peace.v }; })()''')
    ok(home['v'] == B.VER, '판 번호 %s [%s]' % (B.VER, home['v']))
    ok(home['pz'] == 'pz:6월 하순까지 보호' and home['until'] == 19 and home['pv'] == 2, 'STATUS 창 날짜 옆: [6월 하순까지 보호] (%s)' % home['pz'])
    ok('초반 보호 —' not in home['all'] and not TURNS.search(home['all']), 'STATUS 창: v0.9.2 부터 초반 보호 줄은 없고(이름 옆 표만), 창 어디에도 "N턴" 없음')
    tapsel(pg, '#sheet .pz'); pg.wait_for_timeout(400)
    pzd = pg.evaluate('document.querySelector("#modal") ? document.querySelector("#modal").innerText : ""')
    ok('194년 6월 하순까지' in pzd and '(180일 남음)' in pzd and not TURNS.search(pzd), '표를 누르면 풀이 창: 194년 6월 하순까지 (180일 남음), "N턴" 없음')
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(200)
    B.shot(pg, 'a2_home', 300)
    # ---------- 2. 전법 풀이의 기대값 ----------
    st = pg.evaluate('''(() => { %s
      var b = facCities(G.player)[0], spot = null;
      G.factions[G.player].ap = 200; b.troops = 30000; b.w.spear = 20000; b.w.halberd = 20000; b.food = 60000;
      for (var c = b.c - 8; c <= b.c + 8 && !spot; c++) for (var r = b.r - 8; r <= b.r + 8 && !spot; r++) {
        if (!free(c, r) || hdist(c, r, b.c, b.r) < 4) continue;
        var ns = nbrs(c, r).filter(function (n) { return free(n[0], n[1]) && hdist(n[0], n[1], b.c, b.r) >= 4; });
        if (ns.length === 6) { var beh = stepDir(ns[0][0], ns[0][1], cubeX(ns[0][0], ns[0][1]) - cubeX(c, r), ns[0][1] - r); if (free(beh[0], beh[1])) spot = { me: [c, r], foe: ns[0], me2: ns[3] }; }
      }
      var os = idleOfficers(b), strong = os.filter(function (o) { return o.n === "관우"; })[0], weak = os.filter(function (o) { return !isLord(o) && o.n !== "관우" && o.n !== "장비"; }).sort(function (x, y) { return (x.war + x.ldr) - (y.war + y.ldr); })[0];
      var u = cmdDeploy(b, {type: "halberd", ids: [strong.id], troops: Math.min(6000, cmdCap(strong)), food: 4000}).unit, u2 = cmdDeploy(b, {type: "spear", ids: [weak.id], troops: Math.min(4000, cmdCap(weak)), food: 4000}).unit;
      var eb = G.bases[baseByName("복양")], eo = baseOfficers(eb).filter(function (o) { return o.n === "장료"; })[0];
      eb.w.spear = 9000; eb.troops = 30000; G.factions[eb.owner].ap = 200;
      var e = cmdDeploy(eb, {type: "spear", ids: [eo.id], troops: Math.min(6000, cmdCap(eo)), food: 3000}).unit; e.ai = { mode: "return" };
      placeUnit(u, spot.me[0], spot.me[1]); placeUnit(e, spot.foe[0], spot.foe[1]); placeUnit(u2, spot.me2[0], spot.me2[1]);
      [u, u2].forEach(function (x) { x.mp = uMaxMp(x); x.done = false; x.moved = false; x.ox = -1; x.born = -1; x.morale = 100; });
      // 약한 부대는 적과 붙여 둔다(관우의 반대쪽 옆 칸)
      var adj = nbrs(e.c, e.r).filter(function (n) { return free(n[0], n[1]) && hdist(n[0], n[1], u.c, u.r) > 1; }); placeUnit(u2, adj[0][0], adj[0][1]);
      syncScene(); requestDraw(); refreshHud();
      return { u: u.id, u2: u2.id, e: e.id, ep: [e.c, e.r], names: [uName(u), uName(u2), uName(e)], weak: weak.n + " 무" + weak.war + " 통" + weak.ldr };
    })()''' % FREE)
    print('  staged', st)
    def look(uid, tag):
        pg.evaluate('(id) => gotoUnit(UMAP[id])', uid); pg.wait_for_timeout(700)
        taphex(pg, *st['ep']); pg.wait_for_timeout(500)
        acts = [pg.locator('#sheet [data-a=act]').nth(i).inner_text().replace('\n', ' / ') for i in range(pg.locator('#sheet [data-a=act]').count())]
        want = pg.evaluate('''([id, e]) => { var u = UMAP[id], d = UMAP[e], N = attackExpect(u, d), tl = tacticList(u);
          return { n: [Math.round(N.dealt), Math.round(N.recv)], est09: Math.round(estUU(u, d, 1, false)), crit: critNormal(u, d),
            t: tl.filter(function (t) { return u.morale >= t.cost && tacticTargets(u, t).some(function (x) { return x.u === d; }); }).map(function (t) { var X = tacticExpect(u, d, t); return [t.name, Math.round(X.dealt), Math.round(X.recv), X.ok, Math.round((X.dealt / X.nDealt - 1) * 100), X.nRecv >= 1 ? Math.round((X.recv / X.nRecv - 1) * 100) : null]; }),
            fmt: function () {} }; }''', [uid, st['e']])
        atk = [a for a in acts if a.startswith('공격')]
        print('  %s 단추:' % tag, acts[:4], '| 규칙:', want['n'], want['t'])
        ok(len(atk) == 1 and ('예상 -{:,}'.format(want['n'][0])) in atk[0], '%s: 공격 단추의 예상 = attackExpect 의 피해 (%s)' % (tag, atk[0] if atk else '-'))
        tapsel(pg, '#sheet [data-a=tacinfo]'); pg.wait_for_timeout(400)
        dlg = pg.evaluate('document.querySelector("#modal").textContent')          # v0.9.2: 셈법은 접혀 있어 보이는 글(innerText)에는 없다
        # v0.9.2: 문장이 아니라 표 — 첫 줄이 보통 공격, 그 아래 쓸 수 있는 전법마다 [피해, 받는 반격]
        lines = pg.evaluate('''Array.prototype.map.call(document.querySelectorAll("#modal .tcmp tr[data-t]"), function (t) { var td = t.querySelectorAll("td"); return [t.getAttribute("data-t"), [td[0].querySelector("b").textContent, td[1].querySelector("b").textContent], Array.prototype.map.call(t.querySelectorAll("em"), function (m) { return m.className + ":" + m.textContent; })]; })''')
        nrm = pg.evaluate('''(() => { var r = document.querySelector("#modal .tcmp tr.nrm"); return r ? Array.prototype.map.call(r.querySelectorAll("td b"), function (b) { return b.textContent; }) : []; })()''')
        print('  %s 풀이:' % tag, nrm, lines)
        ok(nrm == ['{:,}'.format(want['n'][0]), '{:,}'.format(want['n'][1])], '%s: 표의 첫 줄에 보통 공격의 값 (피해 %d · 반격 %d)' % (tag, want['n'][0], want['n'][1]))
        good = True
        for t in want['t']:
            ln = [l for l in lines if l[0] == t[0]]
            if not ln or ln[0][1] != ['{:,}'.format(t[1]), '{:,}'.format(t[2])]: good = False; print('    어긋남', t, ln)
        ok(good and len(want['t']) >= 1 and len(lines) == len(want['t']), '%s: 표의 전법 줄마다 피해 · 받는 반격이 tacticExpect 와 같다 (%d개)' % (tag, len(want['t'])))
        ok('NaN' not in dlg and 'undefined' not in dlg and 'Infinity' not in dlg, '%s: 풀이 창에 깨진 숫자가 없다' % tag)
        return want, lines, dlg
    w1, l1, d1 = look(st['u'], '강한 쪽(관우)')
    ok('성공해도 반격은 통상 공격만큼 받습니다' in d1 and '85%' in d1 and '1.55배' in d1, '풀이 창의 설명: 성공해도 반격은 통상 공격만큼 · 실패 피해 85%(v0.12 — 전에는 40%) · 실패 반격 1.55배')
    ok('× 0.8 (-30 ~ +15)' in d1, '풀이 창의 설명: 무장 항 × 0.8 (-30 ~ +15)')
    ok(any(t[0] == '견인' and t[2] < w1['n'][1] for t in w1['t']), '관우의 견인: 받는 반격이 보통 공격보다 적다(성공하면 반격 없음)')
    ok(any(any(m.startswith('good:−') for m in l[2]) for l in l1 if l[0] == '견인'), '줄어든 반격은 좋은 쪽 빛(good)으로 적는다')
    B.shot(pg, 'b1_tacinfo_strong', 300)
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(300)
    w2, l2, d2 = look(st['u2'], '약한 쪽(%s)' % st['names'][1])
    ok(all(t[4] < 0 for t in w2['t']) and all(t[5] is None or t[5] > 0 for t in w2['t'] if t[0] != '격퇴'), '약한 쪽이 강한 쪽을 치면: 어느 전법이든 기대 피해는 보통 공격보다 적고(반격은 더 받는다) %s' % [(t[0], t[4], t[5]) for t in w2['t']])
    ok(len(l2) >= 1 and all(any(m.startswith('bad:−') for m in l[2]) for l in l2), '줄어든 피해는 나쁜 쪽 빛(bad)으로 적는다')
    ok(w1['t'][0][3] - w2['t'][0][3] >= 25, '성공률: 관우 %d%% · %s %d%% — 무장의 차이가 크게 든다' % (w1['t'][0][3], st['names'][1], w2['t'][0][3]))
    B.shot(pg, 'b2_tacinfo_weak', 300)
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(300)
    # 실제로 써 본다: 관우의 견인(성공하도록 주사위를 고정) — 반격이 없고, 알림에 기간이 날수로 적힌다
    pg.evaluate('(id) => { window._rnd = rnd; var n = 0; rnd = function () { n++; return n === 1 ? 0.001 : window._rnd(); }; gotoUnit(UMAP[id]); }', st['u']); pg.wait_for_timeout(600)
    taphex(pg, *st['ep']); pg.wait_for_timeout(500)
    acts = [pg.locator('#sheet [data-a=act]').nth(i).inner_text().replace('\n', ' / ') for i in range(pg.locator('#sheet [data-a=act]').count())]
    gi = [i for i, a in enumerate(acts) if a.startswith('견인')]
    before = pg.evaluate('([a, b]) => [UMAP[a].troops, UMAP[b].troops]', [st['u'], st['e']])
    tapsel(pg, '#sheet [data-a=act]', gi[0]); pg.wait_for_timeout(3800)
    after = pg.evaluate('([a, b]) => { rnd = window._rnd; return [UMAP[a] ? UMAP[a].troops : 0, UMAP[b] ? UMAP[b].troops : 0, $("toast").textContent]; }', [st['u'], st['e']])
    print('  견인:', before, '→', after)
    ok(after[0] == before[0] and after[1] < before[1], '견인 성공: 적 병력만 줄고 내 병력은 그대로(반격 없음)')
    ok(not TURNS.search(after[2]), '알림에 "N턴"이 없다 [%s]' % after[2][-40:])
    # ---------- 3. 0.9 에서 하던 판을 이어 하기 ----------
    made = pg.evaluate('''() => { newGame(2, 4242); for (var i = 0; i < 24; i++) endTurn(); delete G.peace.v; G.peace.until = 37;      // 0.9 의 저장 모양으로(화면을 떠날 때 다시 저장되므로 G 자체를 바꿔 둔다)
      localStorage.setItem(SAVE_KEY, serialize()); return { turn: G.turn, date: dateStr(), over: G.over, saved: JSON.parse(localStorage.getItem(SAVE_KEY)).peace }; }''')
    print('  옛 저장을 만든다(0.9 의 모양: 보호의 끝 37턴, 표시 없음):', made)
    pg.reload(); pg.wait_for_function('window.R3 && R3.ready', timeout=60000); pg.wait_for_timeout(600)
    tapsel(pg, '#tCont'); pg.wait_for_timeout(1200)
    old = pg.evaluate('''(() => { var pz = document.querySelector("#sheet .pz"), t0 = document.querySelector("#sheet .todo"); return { turn: G.turn, until: G.peace.until, v: G.peace.v, left: peaceLeft(), pz: pz ? pz.className + ":" + pz.innerText : "", t0: t0 ? t0.innerText.replace(/\\n/g, " / ") : "", log: G.log[G.log.length - 1].t }; })()''')
    print('  이어 하기:', old)
    ok(made['turn'] == 25 and old['turn'] == 25 and old['until'] == 28 and old['v'] == 2 and old['left'] == 3, '25턴째에 이어 하면: 보호의 끝이 37 → 28 (불러온 때부터 30일)')
    ok(old['pz'] == 'pz end:보호 30일 남음', 'STATUS 창의 표가 붉게 [보호 30일 남음] (%s)' % old['pz'])
    pg.evaluate('showPeaceInfo()'); pg.wait_for_timeout(300)
    pd30 = pg.evaluate('document.querySelector("#modal").innerText'); pg.evaluate('closeDialog()'); pg.wait_for_timeout(200)
    ok('(30일 남음)' in pd30 and '초반 보호' not in old['t0'], '풀이 창에도 30일 남음(지금 할 일에는 보호 줄이 없다) [%s]' % pd30.replace('\n', ' / ')[:60])
    ok('초반 보호 기간이 짧아졌습니다(v0.9.1)' in old['log'] and '전에는 194년 12월 하순까지' in old['log'], '기록에 한 줄 남는다 [%s]' % old['log'])
    B.shot(pg, 'c1_old_save', 300)
    pg.evaluate('saveGame()'); pg.reload(); pg.wait_for_function('window.R3 && R3.ready', timeout=60000); pg.wait_for_timeout(600)
    tapsel(pg, '#tCont'); pg.wait_for_timeout(1200)
    again = pg.evaluate('[G.peace.until, G.log.filter(function (e) { return /짧아졌습니다/.test(e.t); }).length]')
    ok(again == [28, 1], '저장하고 다시 열어도 또 당기지 않는다 %s' % again)
B.run(steps, 412, 915, 2)
errs = [e for e in B.errors if 'GPU stall' not in e and 'ERR_FILE_NOT_FOUND' not in e]   # 음악 파일은 따로 싣는다(오프라인 판에는 없다)
print('console errors:', errs[:6])
print('FAILS %d' % len(fails), fails)
sys.exit(1 if fails or errs else 0)
