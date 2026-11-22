# v0.8.1: 초반 보호(화면) + 상태 이상 표시(지도 딱지·소용돌이·창의 풀이) — 화면 조작으로 확인
# v0.9.2: 글을 덜어 냈다 — '지금 할 일'의 초반 보호 줄이 없어지고 이름 옆의 표(누르면 풀이)만 남는다. 경고·풀이·기록의 문장이 짧아졌다. 도움말은 접힌 토막
# v0.9.1: 기간을 턴 수가 아니라 날짜·날수·개월로 적는다('보호 36턴' → '6월 하순까지 보호', '혼란 2턴' → '혼란 20일'). 보호 기간은 18/12/9턴(6·4·3개월)
#   python3 tests/d15.py          찍은 그림은 tests/shots15/
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import taphex, tapsel
B.SHOTS = os.path.join(B.ROOT, 'shots15')
os.makedirs(B.SHOTS, exist_ok=True)
fails = []
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)
FREE = '''function free(c, r) { var t2 = terr(c, r); return inMap(c, r) && (t2 === "p" || t2 === "d") && !unitAt(c, r) && !plotAt(c, r) && !baseAt(c, r) && !G.fires[K(c, r)]; }'''
def steps(pg):
    # ---------- 1. 군주 고르기: 병력과 보호 기간 ----------
    tapsel(pg, '#tNew'); pg.wait_for_timeout(300)
    rows = pg.evaluate('''Array.prototype.map.call(document.querySelectorAll("#modal .row"), function (e) { return e.innerText.replace(/\\n/g, " / "); })''')
    print('  유비 줄:', rows[2][-60:])
    ok('병력 7,000' in rows[2] and '초반 보호 6개월' in rows[2], '군주 고르기: 유비 줄에 병력 7,000 · 초반 보호 6개월')
    ok('초반 보호 3개월' in rows[4] and '병력 42,000' in rows[4], '군주 고르기: 원소 줄에 병력 42,000 · 초반 보호 3개월 [%s]' % rows[4][-40:])
    import re
    ok(not any(re.search(r'[0-9]\s*턴', r) for r in rows), '군주 고르기 어느 줄에도 "N턴"이 없다')
    same = pg.evaluate('''(() => { var bad = []; for (var i = 0; i < SCENARIO.factions.length; i++) { newGame(i, 7); var t = 0; G.bases.forEach(function (b) { if (b.owner === i) t += b.troops; }); if (t !== startTroops(i) || G.peace.until !== 1 + peaceFor(startTroops(i))) bad.push(i); } G = null; return bad; })()''')
    ok(same == [], '군주 고르기에 적힌 병력·보호 기간 = 실제로 판을 만들었을 때의 값 (19세력 모두) %s' % same)
    tapsel(pg, '#modal .row', 2); pg.wait_for_timeout(200)
    foot = pg.evaluate('document.querySelector("#modal .dlg-f .pv").innerText')
    ok('초반 보호 6개월(194년 6월 하순까지)' in foot and '턴' not in foot, '고르면 아래에도 보호 기간이 나온다 [%s]' % foot.replace('\n', ' / '))
    B.shot(pg, 'p1_select', 200)
    tapsel(pg, '#modal [data-a=go]'); pg.wait_for_timeout(600)
    intro = pg.evaluate('document.querySelector("#modal").innerText')
    ok('초반 보호' in intro and '194년 6월 하순까지(6개월)' in intro and not re.search(r'[0-9]\s*턴', intro), '시작 안내에 초반 보호 한 줄(194년 6월 하순까지, 6개월)')
    B.shot(pg, 'p2_intro', 200)
    tapsel(pg, '#modal [data-a=close]'); pg.wait_for_timeout(600)
    # ---------- 2. STATUS 창 ----------
    home = pg.evaluate('''(() => { var pz = document.querySelector("#sheet .pz"), t0 = document.querySelector("#sheet .todo"); return { pz: pz ? pz.innerText : "", t0: t0 ? t0.innerText.replace(/\\n/g, " / ") : "", need: todoList().need, until: G.peace.until, left: peaceLeft() }; })()''')
    print('  home', home)
    ok(home['pz'] == '6월 하순까지 보호' and home['until'] == 19, 'STATUS 창 날짜 옆에 [6월 하순까지 보호] (%s)' % home['pz'])
    ok('초반 보호' not in home['t0'], "v0.9.2: '지금 할 일'에 초반 보호 줄은 없다(이름 옆의 표로 충분) [%s]" % home['t0'][:44])
    B.shot(pg, 'p3_home', 300)
    tapsel(pg, '#sheet .pz', 0); pg.wait_for_timeout(400)                    # v0.9.2: 표를 누르면 풀이 창
    dlg = pg.evaluate('document.querySelector("#modal") ? document.querySelector("#modal").innerText : ""')
    ok('초반 보호' in dlg and '194년 6월 하순까지' in dlg and '완충 기간' in dlg, '표를 누르면 풀이 창이 열린다')
    ok('(180일 남음)' in dlg and '끝난 뒤 8개월은' in dlg and not re.search(r'[0-9]\s*턴', dlg), '풀이 창: 기간을 날짜·날수·개월로 적는다("N턴" 없음)')
    ok(len(dlg) < 190, 'v0.9.2: 풀이 창이 짧다(%d자 — 0.9.1 은 430자쯤)' % len(dlg))
    B.shot(pg, 'p4_info', 200)
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(300)
    # ---------- 3. 먼저 치면 풀린다 ----------
    info = pg.evaluate('''(() => { %s
      var b = facCities(G.player)[0], t = G.bases[baseByName("하비")];
      G.factions[G.player].ap = 200; b.troops = 20000; b.w.spear = 9000; b.food = 30000;
      var os = idleOfficers(b).sort((x, y) => aiMilScore(y) - aiMilScore(x));
      var u = cmdDeploy(b, {type: "spear", ids: [os[0].id], troops: 5000, food: 4000}).unit;
      var ns = nbrs(t.c, t.r).filter(function (n) { return free(n[0], n[1]) || (terr(n[0], n[1]) !== "m" && terr(n[0], n[1]) !== "w" && !unitAt(n[0], n[1]) && !(plotAt(n[0], n[1]) && plotAt(n[0], n[1]).plot.fac)); });
      placeUnit(u, ns[0][0], ns[0][1]); u.mp = uMaxMp(u); u.done = false; u.moved = false; u.ox = -1; u.born = -1; u.morale = 90;
      syncScene(); requestDraw(); refreshHud();
      return { id: u.id, t: [t.c, t.r], tid: t.id, of: t.owner, on: facName(t.owner), may0: aiMayStrike(t.owner, G.player), mayOther0: aiMayStrike(1, G.player), wb: peaceWouldBreak(t.owner) };
    })()''' % FREE)
    print('  staged', info)
    ok(info['may0'] is False and info['mayOther0'] is False and info['wb'] is True, '치기 전: %s군도 여포군도 우리 거점을 칠 수 없다' % info['on'])
    pg.evaluate('(id) => gotoUnit(UMAP[id])', info['id']); pg.wait_for_timeout(700)
    taphex(pg, *info['t']); pg.wait_for_timeout(500)
    warn = pg.evaluate('document.querySelector("#sheet .pzw") ? document.querySelector("#sheet .pzw").innerText : ""')
    ok('먼저 치면' in warn and info['on'] + '군과의 보호가 풀립니다' in warn and len(warn) <= 24, '보호 중인 세력의 성을 고르면 한 줄 경고가 뜬다 [%s]' % warn[:40])
    B.shot(pg, 'p5_warn', 200)
    tapsel(pg, '#sheet [data-a=act]', 0); pg.wait_for_timeout(3600)
    aft = pg.evaluate('''(of) => ({ broken: !!G.peace.broken[of], may: aiMayStrike(of, G.player), mayOther: aiMayStrike(1, G.player), toast: $("toast").textContent, log: G.log[G.log.length - 1].t, t0: document.querySelector("#sheet .todo") ? document.querySelector("#sheet .todo").innerText.replace(/\\n/g, " / ") : "", mul: aiNeedMul(of, G.player), ramp: peaceRamp(of) })''', info['of'])
    print('  after', aft)
    ok(aft['broken'] and aft['may'] is True, '치고 나면 %s군에 대한 보호가 풀린다(그쪽은 이제 칠 수 있다)' % info['on'])
    ok(aft['mayOther'] is False, '다른 세력(여포)과의 보호는 그대로')
    ok(info['on'] + '군과의 보호가 풀림' in aft['toast'], '알림에 적힌다 [%s]' % aft['toast'][-34:])
    ok('먼저' in aft['log'] and info['on'] in aft['log'], '기록에도 남는다 [%s]' % aft['log'][:40])
    pg.evaluate('showPeaceInfo()'); pg.wait_for_timeout(300)
    pd = pg.evaluate('document.querySelector("#modal").innerText'); pg.evaluate('closeDialog()'); pg.wait_for_timeout(200)
    ok('먼저 친 세력: ' + info['on'] + '군' in pd, '보호 풀이 창에 먼저 친 세력이 적힌다 [%s]' % pd.replace('\n', ' / ')[:90])
    ok(aft['mul'] == 1.25 and aft['ramp'] is False, '먼저 친 세력에게는 완충도 없다(배수 1.25)')
    B.shot(pg, 'p6_broken', 300)
    # 보호가 끝나 갈 때 / 끝났을 때
    end = pg.evaluate('''(() => { G.turn = G.peace.until - 3; REPORT = []; EVQ = []; phaseStart(G.player); var a = REPORT.map(function (e) { return e.t; }).join(" | "), n1 = EVQ.filter(function (e) { return e.t === "news"; }).length;
      showHome(); var pz1 = document.querySelector("#sheet .pz"), c1 = pz1 ? pz1.className + ":" + pz1.innerText : "";
      G.turn = G.peace.until; REPORT = []; EVQ = []; phaseStart(G.player); var b = REPORT.map(function (e) { return e.t; }).join(" | "), n2 = EVQ.filter(function (e) { return e.t === "news"; }).length;
      showHome(); var pz2 = document.querySelector("#sheet .pz");
      return { a: a, b: b, n1: n1, n2: n2, c1: c1, pz2: !!pz2, row: Array.prototype.map.call(document.querySelectorAll("#sheet .todo"), function (t) { return t.innerText; }).join(" / "), may: aiMayStrike(1, G.player), mul: aiNeedMul(1, G.player), ramp: peaceRamp(1) }; })()''')
    print('  end', end)
    ok('초반 보호가 30일 남았습니다' in end['a'] and end['n1'] == 1 and end['c1'] == 'pz end:보호 30일 남음', '30일 남았을 때: 기록 + 턴 재생 자막 + 붉은 표 [%s]' % end['c1'])
    ok('초반 보호가 끝났습니다' in end['b'] and end['n2'] == 1 and not end['pz2'] and '초반 보호' not in end['row'], '끝났을 때: 기록 + 자막, 표와 줄은 사라진다')
    ok(end['may'] is True and end['mul'] == 2 and end['ramp'] is True, '끝난 턴: 다른 세력이 칠 수 있고, 필요한 우위는 2배에서 시작(완충)')
    r2 = pg.evaluate('''(() => { G.turn = G.peace.until + 12; var m1 = aiNeedMul(1, G.player); G.turn = G.peace.until + 24; return [m1, aiNeedMul(1, G.player), peaceRamp(1)]; })()''')
    ok(abs(r2[0] - 1.625) < 1e-9 and r2[1] == 1.25 and r2[2] is False, '완충: 120일 뒤 1.625배, 240일 뒤 1.25배로 끝난다 %s' % r2)
    # ---------- 4. 상태 이상: 지도 ----------
    pg.evaluate('G.turn = 5; G.xun = 1; G.month = 2;')
    st = pg.evaluate('''((id) => { %s
      var u = UMAP[id], b = facCities(G.player)[0], spot = null;
      for (var c = b.c - 7; c <= b.c + 7 && !spot; c++) for (var r = b.r - 7; r <= b.r + 7 && !spot; r++) {
        if (!free(c, r) || hdist(c, r, b.c, b.r) < 4) continue;
        var ns = nbrs(c, r).filter(function (n) { return free(n[0], n[1]) && hdist(n[0], n[1], b.c, b.r) >= 4; });
        if (ns.length >= 3) spot = { me: [c, r], foe: ns[0], foe2: ns[1] };
      }
      placeUnit(u, spot.me[0], spot.me[1]); u.done = false; u.moved = false; u.ox = -1; u.mp = uMaxMp(u); u.morale = 100; u.troops = 5000;
      // 적 부대 둘(여포군): 하나는 계략으로 걸 것, 하나는 바로 위보 상태로
      var eb = G.bases[baseByName("복양")], eo = baseOfficers(eb).filter(function (o) { return !isLord(o); }).sort((x, y) => aiMilScore(y) - aiMilScore(x));
      eb.w.spear = 9000; eb.troops = 20000; G.factions[eb.owner].ap = 200;
      var e1 = cmdDeploy(eb, {type: "spear", ids: [eo[0].id], troops: Math.min(3000, cmdCap(eo[0])), food: 3000}).unit, e2 = cmdDeploy(eb, {type: "spear", ids: [eo[1].id], troops: Math.min(3000, cmdCap(eo[1])), food: 3000}).unit;
      placeUnit(e1, spot.foe[0], spot.foe[1]); placeUnit(e2, spot.foe2[0], spot.foe2[1]); e1.ai = e2.ai = { mode: "return" };
      setStatus(e2, "rumor", 2);
      G.fires[K(e2.c, e2.r)] = 3;
      UI.sel = null; syncScene(); requestDraw();
      return { me: spot.me, e1: e1.id, e2: e2.id, p1: [e1.c, e1.r], p2: [e2.c, e2.r] };
    })''' % FREE, info['id'])
    print('  staged', st)
    pg.evaluate('([c, r]) => { clearSel(); jumpTo(c, r, 1.9); }', st['me']); pg.wait_for_timeout(900)
    m0 = pg.evaluate('''([a, b]) => { var o1 = R3.units[a], o2 = R3.units[b]; return { on1: o1.stOn, sw1: o1.sw.visible, on2: o2.stOn, sw2: o2.sw.visible, vis2: o2.st.sp.visible, col2: o2.sp.material.color.getHexString(), segs2: statusSegs(UMAP[b]).map(function (g) { return g.t; }), w2: o2.st.w, lab2: "", swcol2: o2.sw.material.color.getHexString() }; }''', [st['e1'], st['e2']])
    print('  map0', m0)
    ok(m0['on1'] is False and m0['sw1'] is False, '걸리지 않은 부대: 딱지도 소용돌이도 없다')
    ok(m0['on2'] and m0['sw2'] and m0['vis2'] and m0['segs2'] == ['위보 20일', '불길'], '위보에 걸리고 불 위에 선 부대: 딱지 [위보 20일][불길] + 소용돌이 %s' % m0['segs2'])
    ok(m0['col2'] != 'ffffff' and m0['swcol2'] == '8a5a12', '부대 그림의 빛이 바래고 소용돌이는 황토빛')
    B.shot(pg, 's1_map_rumor_fire', 300)
    # 계략으로 건다(성공하도록 고정)
    pg.evaluate('(id) => { window._pr = ployRoll; ployRoll = function () { return 0; }; gotoUnit(UMAP[id]); }', info['id']); pg.wait_for_timeout(600)      # v0.9: 계략의 성패는 ployRoll 로 미리 정해진다 — 시험에서는 통하게 고정
    taphex(pg, *st['p1']); pg.wait_for_timeout(500)
    acts = [pg.locator('#sheet [data-a=act]').nth(i).inner_text().replace('\n', ' / ') for i in range(pg.locator('#sheet [data-a=act]').count())]
    ci = [i for i, a in enumerate(acts) if a.startswith('교란')]
    ok(len(ci) == 1, '대상을 고르면 교란이 있다 %s' % acts)
    tapsel(pg, '#sheet [data-a=act]', ci[0]); pg.wait_for_timeout(700)
    flt = pg.evaluate('Array.prototype.map.call(document.querySelectorAll("#fx .flt"), function (e) { return e.textContent; })')
    pg.wait_for_timeout(3000)
    a1 = pg.evaluate('''(e) => { ployRoll = window._pr; var u = UMAP[e], o = R3.units[e]; return { st: u.status, stT: u.stT, left: statusLeft(u), toast: (function () { var t = $("talk"), q = t && t.classList.contains("on") ? t.querySelector(".tk-sub") : null; return q && /교란/.test(q.textContent) ? q.textContent : $("toast").textContent; })(), on: o.stOn, sw: o.sw.visible, segs: statusSegs(u).map(function (g) { return g.t; }), swcol: o.sw.material.color.getHexString(), tint: o.sp.material.color.getHexString() }; }''', st['e1'])
    print('  ploy', a1, flt)
    ok(a1['st'] == 'confuse' and a1['left'] == 2, '교란 성공 → 혼란, 남은 차례 2')
    ok('혼란 20일' in a1['toast'] and '턴' not in a1['toast'], '알림에 날수까지 [%s]' % a1['toast'])      # v0.9.3: 군사의 조언이 빗나갔으면(시험은 성패를 고정하므로 판에 따라 그럴 수 있다) 결과는 군사의 대화창에 실린다 — 그때는 거기서 읽는다
    ok(any('혼란 20일' in f for f in flt), '걸리는 순간 떠오르는 글씨에도 [혼란 20일] %s' % flt)
    ok(a1['on'] and a1['sw'] and a1['segs'] == ['혼란 20일'] and a1['swcol'] == '2f4f6f' and a1['tint'] == 'aebdd2', '지도: 딱지 [혼란 20일] + 쪽빛 소용돌이 + 바랜 빛')
    pg.evaluate('([c, r]) => { clearSel(); jumpTo(c, r, 1.9); }', st['me']); pg.wait_for_timeout(900)
    B.shot(pg, 's2_map_confuse', 300)
    r0 = pg.evaluate('(e) => R3.units[e].sp.material.rotation', st['e1']); pg.wait_for_timeout(430); r1 = pg.evaluate('(e) => R3.units[e].sp.material.rotation', st['e1'])
    s0 = pg.evaluate('(e) => R3.units[e].sw.material.rotation', st['e1']); pg.wait_for_timeout(300); s1 = pg.evaluate('(e) => R3.units[e].sw.material.rotation', st['e1'])
    ok(r0 != r1 and abs(r0) <= 0.076 and abs(r1) <= 0.076, '혼란에 걸린 부대는 비틀거린다(기울기 %.3f → %.3f)' % (r0, r1))
    ok(s0 != s1, '소용돌이가 돈다')
    pg.evaluate('jumpTo(%d, %d, 0.7)' % (st['me'][0], st['me'][1])); pg.wait_for_timeout(800)
    B.shot(pg, 's3_map_mid', 300)
    far = pg.evaluate('''(e) => { cam.z = 0.2; clampCam(); UI.render = true; return 0; }''', st['e1']); pg.wait_for_timeout(500)
    ok(pg.evaluate('(e) => R3.units[e].st.sp.visible === false && R3.units[e].lab.sp.visible === false', st['e1']), '아주 멀리 물러나면 이름표와 함께 딱지도 숨는다')
    pg.evaluate('([c, r]) => { jumpTo(c, r, 1.5); }', st['me']); pg.wait_for_timeout(800)
    # ---------- 5. 상태 이상: 창 ----------
    pg.evaluate('(e) => selectUnit(UMAP[e])', st['e1']); pg.wait_for_timeout(500)
    sh = pg.evaluate('''(() => { var b = document.querySelector("#sheet .stb"), c = document.querySelector("#sheet .sh-sub .stc"); return { b: b ? b.className + " | " + b.innerText.replace(/\\n/g, " / ") : "", c: c ? c.className + ":" + c.innerText : "" }; })()''')
    print('  sheet(foe)', sh)
    ok('st-confuse' in sh['b'] and '앞으로 20일' in sh['b'] and '받는 피해 +25%' in sh['b'], '적 부대 창: 풀이 띠(혼란 · 앞으로 20일 · 효과)')
    ok(sh['c'] == 'stc st-confuse:혼란 20일', '머리말에 딱지 [혼란 20일]')
    B.shot(pg, 's4_sheet_foe', 200)
    pg.evaluate('(e) => selectUnit(UMAP[e])', st['e2']); pg.wait_for_timeout(500)
    sh2 = pg.evaluate('''Array.prototype.map.call(document.querySelectorAll("#sheet .stb"), function (b) { return b.className + " | " + b.innerText.replace(/\\n/g, " / "); })''')
    print('  sheet(foe2)', sh2)
    ok(len(sh2) == 2 and 'st-rumor' in sh2[0] and 'st-fire' in sh2[1] and '불은 30일 더 탑니다' in sh2[1] and '앞으로 20일' in sh2[0], '위보 + 불길: 띠가 둘(날수로) %s' % [x[-40:] for x in sh2])
    B.shot(pg, 's5_sheet_foe2', 200)
    # 내 부대가 걸렸을 때: 적의 차례에 걸린 것처럼 만든 뒤 실제로 턴을 넘긴다
    lines = []
    def turn():
        return pg.evaluate('''([id, e1]) => { endTurn(); var u = UMAP[id], rep = REPORT.filter(function (x) { return x.f === G.player && /혼란|위보/.test(x.t); }).map(function (x) { return x.t; });
          clearSel(); showHome(); syncScene();
          var rows = Array.prototype.map.call(document.querySelectorAll("#sheet .todo"), function (t) { return t.innerText.replace(/\\n/g, " / "); }).filter(function (t) { return /혼란|위보|불길/.test(t); });
          var x = UMAP[e1];
          return { turn: G.turn, st: u ? u.status : "gone", stT: u ? u.stT : -1, left: u ? statusLeft(u) : -1, done: u ? u.done : null, segs: u ? statusSegs(u).map(function (g) { return g.t; }) : [], rep: rep, rows: rows, need: todoList().need, foe: x ? [x.status, statusLeft(x), statusSegs(x).map(function (g) { return g.t; }).join("+")] : null }; }''', [info['id'], st['e1']])
    pg.evaluate('''([id, e2]) => { var u = UMAP[id]; setStatus(u, "confuse", 2); delete G.fires[K(UMAP[e2].c, UMAP[e2].r)]; G.units.forEach(function (x) { if (x.f !== G.player) x.ai = { mode: "return" }; }); }''', [info['id'], st['e2']])
    t1 = turn(); print('  내 부대 1턴째', t1)
    ok(t1['st'] == 'confuse' and t1['left'] == 2 and t1['done'] is True and t1['segs'] == ['혼란 20일'], '내 부대: 걸린 다음 턴 — 딱지 [혼란 20일], 명령 불가')
    ok(len(t1['rows']) == 1 and '혼란 (이번 턴 포함 20일)' in t1['rows'][0], '지금 할 일에 한 줄 [%s]' % (t1['rows'][0][:40] if t1['rows'] else ''))
    ok(any('움직이지 못함 (이번 턴 포함 20일)' in r for r in t1['rep']), '지난 열흘의 일에도 적힌다 %s' % t1['rep'])
    pg.evaluate('(id) => gotoUnit(UMAP[id])', info['id']); pg.wait_for_timeout(700)
    mine = pg.evaluate('''(() => { var b = document.querySelector("#sheet .stb"), n = document.querySelector("#sheet .note"); return { b: b ? b.innerText.replace(/\\n/g, " / ") : "", n: n ? n.innerText : "", acts: document.querySelectorAll("#sheet [data-a=wait]").length }; })()''')
    ok('이번 턴 포함 20일' in mine['b'] and '명령을 내릴 수 없습니다' in mine['n'] and mine['acts'] == 0, '내 부대 창: 풀이 띠 + 명령 단추 없음 [%s]' % mine['n'])
    B.shot(pg, 's6_sheet_mine', 300)
    if t1['foe']: ok(t1['foe'][0] == 'confuse' and t1['foe'][1] == 1 and t1['foe'][2] == '혼란 10일', '적 부대: 한 차례 지나 [혼란 10일] %s' % t1['foe'])
    t2 = turn(); print('  내 부대 2턴째', t2)
    ok(t2['st'] == 'confuse' and t2['left'] == 1 and t2['segs'] == ['혼란 10일'] and len(t2['rows']) == 1 and '이번 턴만 — 다음 턴에 풀립니다' in t2['rows'][0], '2턴째: [혼란 10일], 이번 턴만')
    if t2['foe']: ok(t2['foe'][0] == 'confuse' and t2['foe'][1] == 0 and t2['foe'][2] == '혼란', '적 부대: 두 차례 지나 [혼란](숫자 없음 = 다음 차례에 풀림) %s' % t2['foe'])
    if t2['foe']:
        pg.evaluate('(e) => selectUnit(UMAP[e])', st['e1']); pg.wait_for_timeout(400)
        s3 = pg.evaluate('document.querySelector("#sheet .stb") ? document.querySelector("#sheet .stb").innerText.replace(/\\n/g, " / ") : ""')
        ok('다음 차례에 풀립니다' in s3 and pg.evaluate('document.querySelector("#sheet .sh-sub .stc").innerText') == '혼란 · 곧 풀림', '적 부대 창: 다음 차례에 풀립니다 / [혼란 · 곧 풀림]')
    t3 = turn(); print('  내 부대 3턴째', t3)
    ok(t3['st'] is None and t3['done'] is False and t3['segs'] == [] and t3['rows'] == [], '3턴째: 풀려났다 — 딱지·줄 없음, 다시 명령 가능')
    ok(any('혼란에서 벗어남' in r for r in t3['rep']), '풀려난 것도 적힌다 %s' % t3['rep'])
    m3 = pg.evaluate('''(id) => { var o = R3.units[id]; return { on: o.stOn, sw: o.sw.visible, vis: o.st.sp.visible, rot: o.sp.material.rotation, col: o.sp.material.color.getHexString() }; }''', info['id'])
    ok(m3['on'] is False and m3['sw'] is False and m3['vis'] is False and m3['rot'] == 0 and m3['col'] == 'ffffff', '지도: 딱지·소용돌이가 사라지고 그림이 제 빛·제 자세로 돌아온다 %s' % m3)
    if t3['foe']: ok(t3['foe'][0] is None, '적 부대도 풀렸다 %s' % t3['foe'])
    # 목록
    pg.evaluate('''([id]) => { setStatus(UMAP[id], "rumor", 1); showLists("unit"); }''', [info['id']]); pg.wait_for_timeout(400)
    lst = pg.evaluate('''Array.prototype.map.call(document.querySelectorAll("#modal .row .stc"), function (e) { return e.className + ":" + e.innerText; })''')
    ok('stc st-rumor:위보 10일' in lst, '부대 목록에도 같은 딱지 %s' % lst)
    B.shot(pg, 's7_list', 200)
    pg.evaluate('closeDialog()')
    # 도움말
    pg.evaluate('showHelp()'); pg.wait_for_timeout(300)
    hp = pg.evaluate('document.querySelector("#modal").textContent')                     # v0.9.2: 토막이 접혀 있어 보이는 글(innerText)에는 제목만 있다
    seen = pg.evaluate('document.querySelector("#modal .dlg-b").innerText')
    ok('초반 보호' in hp and '계략과 상태 이상' in hp and '성역의 경계 — 넘으면' not in hp, '도움말에 두 항목이 있다')
    ok(len(seen) < 260 and '초반 보호' in seen and pg.evaluate('document.querySelectorAll("#modal details").length') >= 15, 'v0.9.2: 도움말은 제목만 보인다(보이는 글 %d자, 토막 %d개)' % (len(seen), pg.evaluate('document.querySelectorAll("#modal details").length')))
    pg.evaluate('''Array.prototype.forEach.call(document.querySelectorAll("#modal details"), function (d) { if (/초반 보호/.test(d.querySelector("summary").textContent)) d.querySelector("summary").click(); })'''); pg.wait_for_timeout(200)
    ok('1만 미만이면 6개월' in pg.evaluate('document.querySelector("#modal .dlg-b").innerText'), '제목을 누르면 그 토막이 펼쳐진다')
    bad = re.findall(r'[^\n]{0,14}[0-9]\s*턴[^\n]{0,8}', hp)
    ok(bad == [], '도움말 어디에도 기간을 "N턴"으로 적은 곳이 없다 %s' % bad[:4])
    ok('1만 미만이면 6개월, 2만 미만이면 4개월, 그 밖은 3개월' in hp and '교란으로 걸면 20일, 전법(난진 등)으로 걸면 10일' in hp, '도움말: 보호 기간은 개월로, 상태 이상은 날수로')
    pg.evaluate('closeDialog()')
    # ---------- 6. 턴 재생 중의 알림(보호가 30일 남았을 때) ----------
    pg.evaluate('''() => { G.units.slice().forEach(function (u) { if (u.f === G.player) { u.status = null; u.done = true; } }); G.peace.until = G.turn + 4; G.peace.broken = {}; UI.pspeed = 2; clearSel(); showHome(); }''')
    pg.locator('#btnEnd').tap(); pg.wait_for_timeout(250)
    if not pg.evaluate('!!UI.play'): pg.locator('#btnEnd').tap()
    seen = False; t0 = time.time()
    while pg.evaluate('!!UI.play') and time.time() - t0 < 120:
        if '초반 보호가 30일 남았습니다' in pg.evaluate('$("plMsg").innerText'): seen = True
        pg.wait_for_timeout(60)
    pg.wait_for_timeout(500)
    rep = pg.evaluate('document.querySelector("#modal") ? document.querySelector("#modal").innerText : ""')
    ok(seen, '턴 재생 중 자막으로 알린다: 초반 보호가 30일 남았습니다')
    ok('중요한 일' in rep and '초반 보호가 30일 남았습니다' in rep, '지난 열흘의 일 — 중요한 일에 적힌다')
    B.shot(pg, 'p7_report', 200)
    pg.evaluate('if (MODAL) closeDialog()'); pg.wait_for_timeout(300)
    ok(pg.evaluate('document.querySelector("#sheet .pz").className + ":" + document.querySelector("#sheet .pz").innerText') == 'pz end:보호 30일 남음', 'STATUS 창의 표가 붉게 [보호 30일 남음]')
    B.shot(pg, 'p8_home_3left', 200)
B.run(steps, 412, 915, 2)
errs = [e for e in B.errors if 'GPU stall' not in e and 'ERR_FILE_NOT_FOUND' not in e]   # 음악 파일은 따로 싣는다(오프라인 판에는 없다)
print('console errors:', errs[:6])
print('FAILS %d' % len(fails), fails)
sys.exit(1 if fails or errs else 0)
