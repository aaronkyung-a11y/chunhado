# v0.9: 군사(임명·조언) · 이웃 거점의 다른 세력 무장 등용 — 화면 조작으로 확인
#   python3 tests/d16.py          찍은 그림은 tests/shots16/
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import taphex, tapsel
B.SHOTS = os.path.join(B.ROOT, 'shots16')
os.makedirs(B.SHOTS, exist_ok=True)
fails = []
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)
def txt(pg, sel): return pg.evaluate('(s) => { var e = document.querySelector(s); return e ? e.innerText.replace(/\\n/g, " / ") : ""; }', sel)
def steps(pg):
    B.start(pg, 0)                                           # 조조
    # ---------- 1. 군사 ----------
    adv = txt(pg, '#sheet .hm-adv')
    info = pg.evaluate('(() => { var A = facAdv(G.player); return { n: A.n, int: A.int, top: advCandidates(G.player)[0].n, n2: advCandidates(G.player)[1].n, i2: advCandidates(G.player)[1].int }; })()')
    print('  군사', adv, info)
    ok(info['n'] == info['top'] and info['n'] in adv and ('지력 %d' % info['int']) in adv, 'STATUS 창에 군사 단추 — 처음에는 지력이 가장 높은 무장 [%s]' % adv)
    B.shot(pg, 'a1_home', 300)
    tapsel(pg, '#sheet .hm-adv'); pg.wait_for_timeout(400)
    d = txt(pg, '#modal')
    ok('군사(軍師)' in d and '지금의 군사 · ' + info['n'] in d and '조언 적중률' in d, '군사 창: 풀이 · 지금의 군사 · 적중률')
    rows = pg.evaluate('Array.prototype.map.call(document.querySelectorAll("#modal .row"), function (e) { return e.innerText.replace(/\\n/g, " "); })')
    ok(len(rows) >= 5 and info['n'] in rows[0] and '군사' in rows[0], '후보는 지력 순, 지금의 군사에 딱지 [%s]' % rows[0][:30])
    B.shot(pg, 'a2_advisor', 200)
    tapsel(pg, '#modal .row', 1); pg.wait_for_timeout(400)
    now = pg.evaluate('facAdv(G.player).n')
    ok(now == info['n2'] and info['n2'] in pg.evaluate('$("toast").textContent'), '줄을 누르면 바뀐다 → %s [%s]' % (now, pg.evaluate('$("toast").textContent')))
    ap0 = pg.evaluate('G.factions[G.player].ap')
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(300)
    ok(info['n2'] in txt(pg, '#sheet .hm-adv'), 'STATUS 창의 단추도 바뀐다')
    # 무장 창에서 되돌리기
    pg.evaluate('(n) => showOfficer(G.officers.filter(function (o) { return o.n === n; })[0])', info['n']); pg.wait_for_timeout(400)
    ok('군사로 삼기' in txt(pg, '#modal .dlg-f'), '무장 창에 [군사로 삼기]')
    tapsel(pg, '#modal [data-a=adv]'); pg.wait_for_timeout(400)
    ok(pg.evaluate('facAdv(G.player).n') == info['n'] and '지금의 군사' in txt(pg, '#modal .dlg-f') and pg.evaluate('G.factions[G.player].ap') == ap0, '눌러서 군사로 — 행동력은 쓰지 않는다')
    ok('군사' in txt(pg, '#modal .dlg-h'), '무장 창 머리말에 [군사] 딱지')
    B.shot(pg, 'a3_officer', 200)
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(300)
    # ---------- 1b. 지금 할 일: 군사가 '응할 것'이라고 보는 이웃 무장 ----------
    hint = pg.evaluate('''(() => { var b = facCities(G.player)[0], ts = poachTargets(b).filter(function (t) { return !bondOf(t); });
      ts.forEach(function (t) { t.loy0 = t.loy; }); var pickT = ts.slice().sort(function (x, y) { return recruitRoll(x) - recruitRoll(y); })[0]; pickT.loy = 75;      // 주사위가 가장 낮은 사람의 충성을 낮춰 '응할 사람'을 하나 만든다
      clearSel(); showHome(); var hs = poachHints(b), rows = Array.prototype.map.call(document.querySelectorAll("#sheet .todo"), function (t) { return t.innerText.replace(/\\n/g, " / "); });
      var idx = -1; rows.forEach(function (r, i) { if (/등용에 응할 듯한/.test(r)) idx = i; });
      return { n: hs.length, names: hs.map(function (x) { return x.t.n; }), row: idx >= 0 ? rows[idx] : "", idx: idx, pick: pickT.n, need: todoList().need }; })()''')
    print('  응할 듯', hint)
    ok(hint['n'] >= 1 and hint['pick'] in hint['names'] and hint['idx'] >= 0 and ('%d명' % hint['n']) in hint['row'] and hint['names'][0] in hint['row'] and '군사 ' in hint['row'], '지금 할 일에 "등용에 응할 듯한 이웃 무장" [%s]' % hint['row'][:70])
    B.shot(pg, 'h1_hint', 300)
    tapsel(pg, '#sheet .todo', hint['idx']); pg.wait_for_timeout(600)
    ok('누구를 부를까요' in txt(pg, '#modal .dlg-h') and pg.evaluate('!!document.querySelector("#sheet [data-a=recruit]")'), '누르면 그 거점의 등용 창이 바로 열린다')
    marks = pg.evaluate('''Array.prototype.map.call(document.querySelectorAll("#modal .row"), function (e) { var a = e.querySelector(".adv"); return [e.innerText.replace(/\\n/g, " "), a ? a.className : "", e.classList.contains("dim")]; })''')
    ok(all((m[1] in ('adv y', 'adv n')) for m in marks if not m[2]) and any(m[1] == 'adv y' and hint['names'][0] in m[0] for m in marks), '등용 목록의 줄마다 군사의 ○·×(가장 잘하는 무장을 보냈을 때)')
    pg.evaluate('closeDialog(); clearSel()'); pg.wait_for_timeout(300)
    # ---------- 2. 다른 세력 무장 등용 ----------
    st = pg.evaluate('''(() => { var b = facCities(G.player)[0]; G.factions[G.player].ap = 255; gotoBase(b, "men"); var ts = poachTargets(b);
      return { b: b.id, n: ts.length, bonded: ts.filter(function (t) { return bondOf(t); }).map(function (t) { return t.n; }), bases: ts.map(function (t) { return G.bases[t.loc].n; }).filter(function (x, i, a) { return a.indexOf(x) === i; }) }; })()''')
    pg.wait_for_timeout(600)
    print('  이웃', st)
    cmdtxt = pg.evaluate('document.querySelector("#sheet [data-a=recruit]").innerText.replace(/\\n/g, " ")')
    ok(('이웃 %d' % st['n']) in cmdtxt, '인재 탭의 등용 단추에 이웃 %d [%s]' % (st['n'], cmdtxt))
    tapsel(pg, '#sheet [data-a=recruit]'); pg.wait_for_timeout(500)
    d = txt(pg, '#modal')
    ok('이웃 거점의 다른 세력 무장' in d and '응하면 이 거점으로 넘어옵니다' in d, '등용 창에 이웃 거점의 다른 세력 무장')
    rows = pg.evaluate('''Array.prototype.map.call(document.querySelectorAll("#modal .row"), function (e) { return { t: e.innerText.replace(/\\n/g, " "), dim: e.classList.contains("dim"), id: +e.getAttribute("data-v") }; })''')
    ok(len(rows) == st['n'] and all('충성' in r['t'] for r in rows), '%d명 모두 충성과 함께 나온다' % len(rows))
    bd = [r for r in rows if any(n in r['t'] for n in st['bonded'])]
    ok(len(bd) == len(st['bonded']) and all(r['dim'] and '주군과' in r['t'] for r in bd), '제 주군과 인연이 있는 무장은 흐리게 + 까닭 %s' % [r['t'][-14:] for r in bd][:2])
    live = [r for r in rows if not r['dim']]
    ok(len(live) > 0 and '최고' in live[0]['t'] and rows.index(live[0]) == 0, '권할 수 있는 사람이 위에, 성공률이 높은 순 [%s]' % live[0]['t'][-22:])
    B.shot(pg, 'r1_list', 200)
    # 이번 턴에 응하는 사람·거절하는 사람을 규칙에서 미리 뽑아(시험이라 아는 것) 화면의 조언과 견준다
    plan = pg.evaluate('''((bid) => { var b = G.bases[bid], os = idleOfficers(b), best = function (t) { var m = 0; os.forEach(function (o) { m = Math.max(m, recruitChance(b, o, t)); }); return m; };
      var ts = poachTargets(b).filter(function (t) { return !bondOf(t); }), yes = null, no = null;
      ts.forEach(function (t) { var r = recruitRoll(t); if (!yes && r < 40) { t.loy = 78; if (r < best(t)) yes = t; } });
      ts.forEach(function (t) { if (t === yes || no) return; var r = recruitRoll(t); if (best(t) > 0 && r >= best(t)) no = t; });
      return { yes: yes ? { id: yes.id, n: yes.n, p: best(yes), from: facName(yes.f), fb: G.bases[yes.loc].n } : null, no: no ? { id: no.id, n: no.n, p: best(no), loy: no.loy } : null, acc: yes ? adviceAcc(facAdv(G.player), yes.int) : 0, advInt: facAdv(G.player).int }; })''', st['b'])
    print('  plan', plan)
    ok(plan['yes'] is not None and plan['no'] is not None, '(준비) 응할 사람과 거절할 사람')
    pg.evaluate('refreshDialog()'); pg.wait_for_timeout(200)
    tapsel(pg, '#modal .row[data-v="%d"]' % plan['yes']['id']); pg.wait_for_timeout(500)
    pick = pg.evaluate('''Array.prototype.map.call(document.querySelectorAll("#modal .tr"), function (e) { var a = e.querySelector(".adv"); return { n: e.querySelector(".c-n").innerText, x: e.querySelector(".c-x").innerText.replace(/\\n/g, " "), m: a ? a.className : "" }; })''')
    print('  표', pick[:4])
    ok(len(pick) > 0 and all(p['m'] in ('adv y', 'adv n') for p in pick) and all('%' in p['x'] for p in pick), '무장 고르는 표: 성공률 앞에 군사의 ○·×')
    chk = pg.evaluate('''(([bid, tid]) => { var b = G.bases[bid], t = off(tid), bad = 0, n = 0; idleOfficers(b).forEach(function (o) { var a = recruitAdvice(b, o, t), real = recruitRoll(t) < recruitChance(b, o, t); n++; if (a.acc === 100 && a.says !== real) bad++; }); return [n, bad, adviceAcc(facAdv(G.player), t.int)]; })''', [st['b'], plan['yes']['id']])
    ok(chk[1] == 0, '적중률 100%%인 조언은 실제 결과와 같다 (%d명, 이 대상에 대한 적중률 %d%%)' % (chk[0], chk[2]))
    tapsel(pg, '#modal [data-a=auto]'); pg.wait_for_timeout(300)
    pv = txt(pg, '#modal .dlg-f .pv')
    ok('성공률' in pv and '군사 ' in pv and '적중률' in pv and ('통할 것입니다' in pv or '어렵겠습니다' in pv), '고르면 아래에 군사의 말 [%s]' % pv)
    B.shot(pg, 'r2_pick', 200)
    n0 = pg.evaluate('facOfficers(G.player).length')
    tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(600)
    res = pg.evaluate('''((tid) => { var t = off(tid); return { f: t.f, loc: G.bases[t.loc].n, loy: t.loy, acted: t.acted, toast: $("toast").textContent, n: facOfficers(G.player).length, log: G.log[G.log.length - 1].t }; })''', plan['yes']['id'])
    print('  응함', res)
    ok(res['f'] == 0 and res['n'] == n0 + 1 and '떠나 합류했습니다' in res['toast'], '실행 → %s군의 %s이(가) 넘어왔다 [%s]' % (plan['yes']['from'], plan['yes']['n'], res['toast']))
    ok('등용' in res['log'] and plan['yes']['n'] in res['log'], '기록 [%s]' % res['log'])
    # 거절
    if pg.evaluate('!MODAL'): tapsel(pg, '#sheet [data-a=recruit]'); pg.wait_for_timeout(400)
    pg.evaluate('refreshDialog()'); pg.wait_for_timeout(200)
    ok(pg.evaluate('(id) => !document.querySelector(\'#modal .row[data-v="\' + id + \'"]\')', plan['yes']['id']), '넘어온 무장은 목록에서 빠진다')
    tapsel(pg, '#modal .row[data-v="%d"]' % plan['no']['id']); pg.wait_for_timeout(500)
    tapsel(pg, '#modal [data-a=auto]'); pg.wait_for_timeout(300)
    pv2 = txt(pg, '#modal .dlg-f .pv')
    tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(600)
    res2 = pg.evaluate('''((tid) => { var t = off(tid); return { f: t.f, loy: t.loy, wait: askWait(t), toast: $("toast").textContent }; })''', plan['no']['id'])
    print('  거절', res2, '|', pv2)
    ok(res2['f'] != 0 and '거절했습니다' in res2['toast'] and '다음 달에 다시' in res2['toast'] and res2['loy'] == plan['no']['loy'] + 3 + 2 and res2['wait'] == 3, '거절 → 충성 +3(앞서 한 사람이 떠나 +2 된 데 더해), 다음 달에 다시 [%s]' % res2['toast'])
    if plan['acc'] == 100: ok('어렵겠습니다' in pv2, '군사는 미리 "어렵겠습니다"라고 했다')
    if pg.evaluate('!MODAL'): tapsel(pg, '#sheet [data-a=recruit]'); pg.wait_for_timeout(400)
    pg.evaluate('refreshDialog()'); pg.wait_for_timeout(200)
    again = pg.evaluate('(id) => { var e = document.querySelector(\'#modal .row[data-v="\' + id + \'"]\'); return e ? [e.classList.contains("dim"), e.innerText.replace(/\\n/g, " ")] : null; }', plan['no']['id'])
    ok(again and again[0] and '다음 달에 다시' in again[1], '목록에서 흐려지고 "다음 달에 다시" [%s]' % (again[1][-20:] if again else ''))
    tapsel(pg, '#modal .row[data-v="%d"]' % plan['no']['id']); pg.wait_for_timeout(300)
    ok('다음 달에 다시' in pg.evaluate('$("toast").textContent'), '눌러도 안내만 뜬다')
    B.shot(pg, 'r3_after', 200)
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(300)
    # ---------- 3. 계략: 군사의 조언 ----------
    s3 = pg.evaluate('''(() => { function free(c, r) { var t2 = terr(c, r); return inMap(c, r) && (t2 === "p" || t2 === "d") && !unitAt(c, r) && !plotAt(c, r) && !baseAt(c, r); }
      var b = facCities(G.player)[0], spot = null; G.factions[G.player].ap = 255; b.troops = 20000; b.w.spear = 9000; b.food = 30000;
      for (var c = b.c - 7; c <= b.c + 7 && !spot; c++) for (var r = b.r - 7; r <= b.r + 7 && !spot; r++) { if (!free(c, r) || hdist(c, r, b.c, b.r) < 4) continue; var ns = nbrs(c, r).filter(function (n) { return free(n[0], n[1]) && hdist(n[0], n[1], b.c, b.r) >= 4; }); if (ns.length >= 2) spot = { me: [c, r], foe: ns[0] }; }
      var os = idleOfficers(b).sort(function (x, y) { return y.int - x.int; }), u = cmdDeploy(b, { type: "spear", ids: [os[0].id], troops: Math.min(4000, cmdCap(os[0])), food: 3000 }).unit;
      var eb = G.bases[baseByName("복양")], eo = baseOfficers(eb).filter(function (o) { return !isLord(o); }); eb.w.spear = 9000; eb.troops = 20000; G.factions[eb.owner].ap = 255;
      var e = cmdDeploy(eb, { type: "spear", ids: [eo[0].id], troops: Math.min(3000, cmdCap(eo[0])), food: 3000 }).unit; e.ai = { mode: "return" };
      placeUnit(u, spot.me[0], spot.me[1]); placeUnit(e, spot.foe[0], spot.foe[1]); u.done = false; u.moved = false; u.ox = -1; u.mp = uMaxMp(u); u.morale = 100; u.born = -1;
      syncScene(); requestDraw(); gotoUnit(u);
      return { u: u.id, e: e.id, p: [e.c, e.r], acc: adviceAcc(facAdv(G.player), uInt(e)), eint: uInt(e) }; })()''')
    pg.wait_for_timeout(700)
    taphex(pg, *s3['p']); pg.wait_for_timeout(500)
    acts = pg.evaluate('''Array.prototype.map.call(document.querySelectorAll("#sheet [data-a=act]"), function (e) { var a = e.querySelector(".adv"); return { t: e.innerText.replace(/\\n/g, " / "), m: a ? a.className : "" }; })''')
    pl = [a for a in acts if a['t'].startswith(('화계', '교란', '위보'))]
    print('  계략 단추', pl, '적중률', s3['acc'])
    ok(len(pl) == 3 and all(a['m'] in ('adv y', 'adv n') for a in pl), '계략 단추마다 군사의 ○·×')
    ok(not any(a['m'] for a in acts if not a['t'].startswith(('화계', '교란', '위보'))), '공격·전법 단추에는 없다(조언은 등용과 계략에만)')
    note = txt(pg, '#sheet .advn')
    ok('의 조언' in note and ('적중률 %d%%' % s3['acc']) in note, '대상 줄 아래에 조언 풀이와 적중률 [%s]' % note)
    B.shot(pg, 'p1_ploy', 200)
    real = pg.evaluate('''(([uid, eid]) => { var u = UMAP[uid], e = UMAP[eid], t = UI.target; return [1, 2].map(function (i) { var pl = PLOYS[i]; return { name: pl.name, real: ployRoll(pl, t) < ployChance(u, pl, e), says: ployAdvice(u, pl, t).says, p: ployChance(u, pl, e) }; }); })''', [s3['u'], s3['e']])
    print('  실제', real)
    if s3['acc'] == 100: ok(all(r['real'] == r['says'] for r in real), '적중률 100%: 조언 = 실제 결과')
    i = [k for k, a in enumerate(acts) if a['t'].startswith(real[0]['name'])][0]
    tapsel(pg, '#sheet [data-a=act]', i); pg.wait_for_timeout(3600)
    aft = pg.evaluate('(eid) => [UMAP[eid] ? UMAP[eid].status : "gone", $("toast").textContent]', s3['e'])
    ok((aft[0] == 'confuse') == real[0]['real'] and ((real[0]['name'] + ' 성공') in aft[1]) == real[0]['real'], '%s 실행 → 미리 정해 둔 대로 %s [%s]' % (real[0]['name'], '성공' if real[0]['real'] else '실패', aft[1]))
    # ---------- 4. 내 무장을 데려갈 위험 ----------
    w = pg.evaluate('''(() => { var b = facCities(G.player)[0], o = baseOfficers(b).filter(function (x) { return !isLord(x) && !bondOf(x); })[0]; o.loy = 72; clearSel(); showHome();
      var before = Array.prototype.some.call(document.querySelectorAll("#sheet .todo"), function (t) { return /데려갈 수 있는/.test(t.innerText); });
      G.peace.until = G.turn; showHome();
      var row = Array.prototype.filter.call(document.querySelectorAll("#sheet .todo"), function (t) { return /데려갈 수 있는/.test(t.innerText); })[0];
      var rk = poachRisk(o); return { n: o.n, before: before, row: row ? row.innerText.replace(/\\n/g, " / ") : "", p: rk ? rk.p : 0, by: rk ? rk.by.n : "", idx: row ? Array.prototype.indexOf.call(document.querySelectorAll("#sheet .todo"), row) : -1, need: todoList().need }; })()''')
    print('  위험', w)
    ok(w['before'] is False, '초반 보호 중에는 뜨지 않는다(그동안은 권하지 않으므로)')
    ok(w['row'] and w['n'] in w['row'] and '충성 72' in w['row'] and ('(%d%%)' % w['p']) in w['row'] and '포상' in w['row'], '보호가 끝나면: 지금 할 일에 "다른 세력이 데려갈 수 있는 무장" [%s]' % w['row'][:60])
    B.shot(pg, 'k1_risk', 300)
    tapsel(pg, '#sheet .todo', w['idx']); pg.wait_for_timeout(600)
    ok(pg.evaluate('!!document.querySelector("#sheet [data-a=reward]")'), '누르면 그 거점의 인재 탭(포상)으로')
    # 실제로 데려가는 경우: 응하게 되어 있는 턴을 찾아 이웃 세력이 권한다
    g = pg.evaluate('''((n) => { var o = G.officers.filter(function (x) { return x.n === n; })[0], rk = poachRisk(o), t0 = G.turn, found = 0;
      for (var k = 0; k < 60 && !found; k++) { G.month = 1 + k % 12; G.year = 194 + Math.floor(k / 12); if (recruitRoll(o) < rk.p) found = 1; }      // 응하게 되어 있는 달을 찾는다
      REPORT = []; EVQ = []; rk.by.acted = false; G.factions[rk.base.owner].ap = 255; var from = G.bases[o.loc].n;
      var r = cmdRecruit(rk.base, rk.by.id, o.id);
      return { ok: r.ok, joined: r.joined, f: o.f, loc: G.bases[o.loc].n, from: from, rep: REPORT.map(function (e) { return [e.imp, e.f === G.player, e.t]; }), news: EVQ.filter(function (e) { return e.t === "news"; }).map(function (e) { return e.text; }) }; })''', w['n'])
    print('  떠남', g)
    ok(g['ok'] and g['joined'] and g['f'] != 0, '이웃 세력이 권해 응하면 떠난다 (%s → %s)' % (g['from'], g['loc']))
    ok(len(g['rep']) == 1 and g['rep'][0][0] == 2 and g['rep'][0][1] and len(g['news']) == 1 and '떠났습니다' in g['news'][0], '중요한 일로 기록되고 턴 재생 자막으로 알린다 [%s]' % (g['news'][0] if g['news'] else ''))
    # ---------- 5. 도움말 ----------
    pg.evaluate('showHelp()'); pg.wait_for_timeout(300)
    hp = pg.evaluate('document.querySelector("#modal").innerText')
    ok('군사(軍師)' in hp and '다른 세력의 무장' in hp and '미리 정해져 있습니다' in hp, '도움말: 군사 · 다른 세력의 무장 등용')
    pg.evaluate('closeDialog()')
B.run(steps, 412, 915, 2)
errs = [e for e in B.errors if 'GPU stall' not in e and 'ERR_FILE_NOT_FOUND' not in e]
print('console errors:', errs[:6])
print('FAILS %d' % len(fails), fails)
sys.exit(1 if fails or errs else 0)
