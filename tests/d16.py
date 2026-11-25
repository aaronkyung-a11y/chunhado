# v0.9: 군사(임명·조언) · 이웃 거점의 다른 세력 무장 등용 — 화면 조작으로 확인
#   v0.9.3: 군사의 말은 초상이 있는 줄(.say)로, 결과는 대화창(#talk)으로 나온다 — 그에 맞춰 보는 자리를 옮겼다
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
def talk(pg): return pg.evaluate('(() => { var t = document.getElementById("talk"); return { on: t.classList.contains("on"), who: (t.querySelector(".tk-who b") || {}).textContent || "", role: (t.querySelector(".tk-who em") || {}).textContent || "", say: (t.querySelector(".tk-say") || {}).textContent || "", sub: (t.querySelector(".tk-sub") || {}).textContent || "" }; })()')
def steps(pg):
    B.start(pg, 0)                                           # 조조
    # ---------- 1. 군사 ----------
    adv = txt(pg, '#sheet .hm-advp')
    info = pg.evaluate('(() => { var A = facAdv(G.player); return { n: A.n, int: A.int, top: advCandidates(G.player)[0].n, n2: advCandidates(G.player)[1].n, i2: advCandidates(G.player)[1].int }; })()')
    print('  군사', adv, info)
    ok(info['n'] == info['top'] and info['n'] in adv and '군사' in adv and '軍' not in adv, 'STATUS 창에 군사의 자리 — 처음에는 지력이 가장 높은 무장 [%s]' % adv[:60])
    ok(pg.evaluate('!!document.querySelector("#sheet .hm-advp .por")') and txt(pg, '#sheet .hm-adv') == '바꾸기' and len(txt(pg, '#sheet .hm-say')) > len(info['n']) + 6, '초상 · 군사의 말 한 줄 · [바꾸기] 단추')
    B.shot(pg, 'a1_home', 300)
    tapsel(pg, '#sheet .hm-adv'); pg.wait_for_timeout(400)
    d = txt(pg, '#modal')
    ok('군사' in txt(pg, '#modal .dlg-h') and info['n'] in txt(pg, '#modal .advc') and ('지력 %d' % info['int']) in txt(pg, '#modal .advc') and '적중률' in d, '군사 창: 지금의 군사 · 지력 · 적중률')
    ok(len(txt(pg, '#modal .cap')) <= 60, '군사 창의 풀이는 한두 줄(%d자)' % len(txt(pg, '#modal .cap')))
    rows = pg.evaluate('Array.prototype.map.call(document.querySelectorAll("#modal .row"), function (e) { return e.innerText.replace(/\\n/g, " "); })')
    ok(len(rows) >= 5 and info['n'] in rows[0] and '군사' in rows[0], '후보는 지력 순, 지금의 군사에 딱지 [%s]' % rows[0][:30])
    B.shot(pg, 'a2_advisor', 200)
    btn = pg.evaluate('Array.prototype.map.call(document.querySelectorAll("#modal .row"), function (e) { var b = e.querySelector("[data-a=set]"); return b ? b.innerText : ""; })')
    ok(btn[0] == '' and all(x == '임명' for x in btn[1:]) and '지금의 군사' in rows[0], '지금의 군사 말고는 줄마다 [임명] 단추 (%d개)' % (len(btn) - 1))
    tapsel(pg, '#modal .row [data-a=set]', 0); pg.wait_for_timeout(400)
    now = pg.evaluate('facAdv(G.player).n'); tk = talk(pg)
    ok(now == info['n2'] and tk['on'] and tk['who'] == info['n2'] and tk['role'] == '군사' and len(tk['say']) >= 6 and '군사로 삼았습니다' in tk['sub'] and ('지력 %d' % info['i2']) in tk['sub'], '[임명]을 누르면 바뀌고, 새 군사가 대화창에서 답한다 → %s "%s" [%s]' % (now, tk['say'], tk['sub']))
    ok('지금의 군사' in pg.evaluate('document.querySelectorAll("#modal .row")[1].innerText') and pg.evaluate('!document.querySelectorAll("#modal .row")[1].querySelector("[data-a=set]")'), '창의 목록도 바로 바뀐다')
    ap0 = pg.evaluate('G.factions[G.player].ap')
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(300)
    ok(info['n2'] in txt(pg, '#sheet .hm-advp'), 'STATUS 창의 군사도 바뀐다')
    # 무장 창에서 되돌리기
    pg.evaluate('(n) => showOfficer(G.officers.filter(function (o) { return o.n === n; })[0])', info['n']); pg.wait_for_timeout(400)
    ok('군사로 삼기' in txt(pg, '#modal .dlg-f'), '무장 창에 [군사로 삼기]')
    tapsel(pg, '#modal [data-a=adv]'); pg.wait_for_timeout(400)
    tk = talk(pg)
    ok(pg.evaluate('facAdv(G.player).n') == info['n'] and '지금의 군사' in txt(pg, '#modal .dlg-f') and pg.evaluate('G.factions[G.player].ap') == ap0, '눌러서 군사로 — 행동력은 쓰지 않는다')
    ok(tk['on'] and tk['who'] == info['n'] and '군사로 삼았습니다' in tk['sub'], '무장 창에서 삼아도 대화창으로 답한다 [%s / %s]' % (tk['say'], tk['sub']))
    ok('군사' in txt(pg, '#modal .dlg-h'), '무장 창 머리말에 [군사] 딱지')
    B.shot(pg, 'a3_officer', 200)
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(300)
    # ---------- 1b. 지금 할 일: 군사가 '응할 것'이라고 보는 이웃 무장 ----------
    hint = pg.evaluate('''(() => { var b = facCities(G.player)[0], ts = poachTargets(b).filter(function (t) { return !bondOf(t); });
      ts.forEach(function (t) { t.loy0 = t.loy; }); var pickT = ts.slice().sort(function (x, y) { return recruitRoll(x) - recruitRoll(y); })[0]; pickT.loy = 75;      // 주사위가 가장 낮은 사람의 충성을 낮춰 '응할 사람'을 하나 만든다
      clearSel(); showHome(); var hs = poachHints(b), rows = Array.prototype.map.call(document.querySelectorAll("#sheet .todo"), function (t) { return t.innerText.replace(/\\n/g, " / "); });
      var idx = -1; rows.forEach(function (r, i) { if (/등용할 만한 무장/.test(r)) idx = i; });
      return { n: hs.length, names: hs.map(function (x) { return x.t.n; }), row: idx >= 0 ? rows[idx] : "", idx: idx, pick: pickT.n, need: todoList().need }; })()''')
    print('  응할 것', hint)
    ok(hint['n'] >= 1 and hint['pick'] in hint['names'] and hint['idx'] >= 0 and ('%d명' % hint['n']) in hint['row'] and hint['names'][0] in hint['row'] and '%' in hint['row'], '지금 할 일에 "등용할 만한 무장 N명"과 이름·성공률 [%s]' % hint['row'][:70])
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
    ok('이웃 거점의 다른 세력 무장' in d and '한 달에 한 번' in d and '거절하면 충성 +3' in d, '등용 창에 이웃 거점의 다른 세력 무장(v0.9.2: 풀이는 한 줄 — 한 달에 한 번 · 거절하면 충성 +3)')
    rows = pg.evaluate('''Array.prototype.map.call(document.querySelectorAll("#modal .row"), function (e) { return { t: e.innerText.replace(/\\n/g, " "), dim: e.classList.contains("dim"), id: +e.getAttribute("data-v") }; })''')
    ok(len(rows) == st['n'] and all('충성' in r['t'] for r in rows), '%d명 모두 충성과 함께 나온다' % len(rows))
    bd = [r for r in rows if any(n in r['t'] for n in st['bonded'])]
    ok(len(bd) == len(st['bonded']) and all(r['dim'] and '주군과' in r['t'] for r in bd), '제 주군과 인연이 있는 무장은 흐리게 + 까닭 %s' % [r['t'][-14:] for r in bd][:2])
    live = [r for r in rows if not r['dim']]
    ok(len(live) > 0 and '최고' in live[0]['t'] and rows.index(live[0]) == 0, '권할 수 있는 사람이 위에, 성공률이 높은 순 [%s]' % live[0]['t'][-22:])
    B.shot(pg, 'r1_list', 200)
    pg.evaluate('(() => { facAdv(G.player).int = 100; })()')      # v0.10.1: 적중률 = 군사의 지력. 조언이 늘 맞는 것을 보려고 군사의 지력을 100으로 둔다(전에는 순욱(96)도 100% 였다)
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
    pv = txt(pg, '#modal .dlg-f .pv'); sy = txt(pg, '#modal .pksay .say')
    advn = pg.evaluate('facAdv(G.player).n')
    ok('성공률' in pv and '군사' not in pv, '아래 줄에는 성공률만 [%s]' % pv)
    ok(advn in sy and plan['yes']['n'] in sy and '적중률' in sy and ('응할 것입니다' in sy or '응하지 않을 것입니다' in sy) and pg.evaluate('!!document.querySelector("#modal .pksay .say .por")'), '고르면 표 아래에 군사의 말 한 줄(초상과 함께) [%s]' % sy)
    if plan['acc'] == 100: ok('응할 것입니다' in sy, '적중률 100%: 군사는 "응할 것입니다"라고 한다')
    B.shot(pg, 'r2_pick', 200)
    n0 = pg.evaluate('facOfficers(G.player).length')
    tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(600)
    res = pg.evaluate('''((tid) => { var t = off(tid); return { f: t.f, loc: G.bases[t.loc].n, loy: t.loy, acted: t.acted, n: facOfficers(G.player).length, log: G.log[G.log.length - 1].t }; })''', plan['yes']['id']); tk = talk(pg)
    print('  응함', res, tk)
    ok(res['f'] == 0 and res['n'] == n0 + 1 and '떠나 합류했습니다' in tk['sub'], '실행 → %s군의 %s이(가) 넘어왔다 [%s]' % (plan['yes']['from'], plan['yes']['n'], tk['sub']))
    ok(tk['on'] and tk['who'] == plan['yes']['n'] and len(tk['say']) >= 6, '넘어온 무장이 대화창에서 한마디 한다 [%s]' % tk['say'])
    ok('등용' in res['log'] and plan['yes']['n'] in res['log'], '기록 [%s]' % res['log'])
    # 거절
    if pg.evaluate('!MODAL'): tapsel(pg, '#sheet [data-a=recruit]'); pg.wait_for_timeout(400)
    pg.evaluate('refreshDialog()'); pg.wait_for_timeout(200)
    ok(pg.evaluate('(id) => !document.querySelector(\'#modal .row[data-v="\' + id + \'"]\')', plan['yes']['id']), '넘어온 무장은 목록에서 빠진다')
    tapsel(pg, '#modal .row[data-v="%d"]' % plan['no']['id']); pg.wait_for_timeout(500)
    tapsel(pg, '#modal [data-a=auto]'); pg.wait_for_timeout(300)
    pv2 = txt(pg, '#modal .pksay .say')
    tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(600)
    res2 = pg.evaluate('''((tid) => { var t = off(tid); return { f: t.f, loy: t.loy, wait: askWait(t) }; })''', plan['no']['id']); tk2 = talk(pg)
    print('  거절', res2, tk2, '|', pv2)
    ok(res2['f'] != 0 and '거절했습니다' in tk2['sub'] and '(충성 +3)' in tk2['sub'] and res2['loy'] == plan['no']['loy'] + 3 + 2 and res2['wait'] == 3, '거절 → 충성 +3(앞서 한 사람이 떠나 +2 된 데 더해), 한 달 뒤에 다시 청할 수 있다 [%s]' % tk2['sub'])
    ok(tk2['on'] and tk2['who'] == plan['no']['n'] and len(tk2['say']) >= 6, '거절한 무장이 대화창에서 한마디 한다 [%s]' % tk2['say'])
    if '응하지 않을 것입니다' in pv2: ok('군사 ' not in tk2['sub'], '조언이 맞았으면 군사는 덧붙이지 않는다')
    else: ok('군사 ' in tk2['sub'] and '헤아림이 모자랐습니다' in tk2['sub'], '조언이 빗나갔으면 군사가 한마디 덧붙인다 [%s]' % tk2['sub'])
    if plan['acc'] == 100: ok('응하지 않을 것입니다' in pv2, '군사는 미리 "응하지 않을 것입니다"라고 했다')
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
      return { u: u.id, e: e.id, p: [e.c, e.r], acc: adviceAcc(uStaff(u), uInt(e)), eint: uInt(e), staff: uStaff(u).n, lead: uStaff(u) === uLeader(u) }; })()''')      # v0.20: 싸움터의 조언은 부대의 참모(부장 — 없으면 주장)가
    pg.wait_for_timeout(700)
    taphex(pg, *s3['p']); pg.wait_for_timeout(500)
    acts = pg.evaluate('''Array.prototype.map.call(document.querySelectorAll("#sheet [data-a=act]"), function (e) { var a = e.querySelector(".adv"); return { t: e.innerText.replace(/\\n/g, " / "), m: a ? a.className : "" }; })''')
    pl = [a for a in acts if a['t'].startswith(('화계', '교란', '위보'))]
    print('  계략 단추', pl, '적중률', s3['acc'])
    ok(len(pl) == 3 and all(a['m'] in ('adv y', 'adv n') for a in pl), '계략 단추마다 군사의 ○·×')
    ok(not any(a['m'] for a in acts if not a['t'].startswith(('화계', '교란', '위보'))), '공격·전법 단추에는 없다(조언은 등용과 계략에만)')
    note = txt(pg, '#sheet .advn'); advn = s3['staff']
    ok(note.startswith(('주장' if s3['lead'] else '부장') + advn) and ('통하겠' in note or '어렵겠습니다' in note) and ('적중률 %d%%' % s3['acc']) in note and len(note) <= 60 and pg.evaluate('!!document.querySelector("#sheet .advn .por")'), '대상 줄 아래에 군사의 말 한 줄(초상 · 무엇이 통할지 · 적중률) [%s]' % note)
    ys = [a['t'][:2] for a in pl if a['m'] == 'adv y']; ns = [a['t'][:2] for a in pl if a['m'] == 'adv n']
    ok(all(y in note.split('어렵')[0].split('통하겠')[0] for y in ys) and all(n in note.split('통하겠')[-1] for n in ns), '말과 단추의 ○·×가 같다 (○ %s · × %s)' % (ys, ns))
    B.shot(pg, 'p1_ploy', 200)
    real = pg.evaluate('''(([uid, eid]) => { var u = UMAP[uid], e = UMAP[eid], t = UI.target; return [1, 2].map(function (i) { var pl = PLOYS[i]; return { name: pl.name, real: ployRoll(pl, t) < ployChance(u, pl, e), says: ployAdvice(u, pl, t).says, p: ployChance(u, pl, e) }; }); })''', [s3['u'], s3['e']])
    print('  실제', real)
    if s3['acc'] == 100: ok(all(r['real'] == r['says'] for r in real), '적중률 100%: 조언 = 실제 결과')
    i = [k for k, a in enumerate(acts) if a['t'].startswith(real[0]['name'])][0]
    tapsel(pg, '#sheet [data-a=act]', i); pg.wait_for_timeout(3600)
    aft = pg.evaluate('(eid) => [UMAP[eid] ? UMAP[eid].status : "gone", $("toast").textContent]', s3['e']); tk = talk(pg)
    if real[0]['real'] != real[0]['says']:                                       # 조언이 빗나갔다 → 결과는 군사의 대화창에 실린다
        ok(tk['on'] and tk['who'] == advn and ('잘못 보았습니다' in tk['say'] or '헤아림이 모자랐습니다' in tk['say']), '조언이 빗나가면 군사가 대화창에서 그렇게 말한다 [%s]' % tk['say'])
        aft[1] = tk['sub']
    ok((aft[0] == 'confuse') == real[0]['real'] and ((real[0]['name'] + ' 성공') in aft[1]) == real[0]['real'], '%s 실행 → 미리 정해 둔 대로 %s [%s]' % (real[0]['name'], '성공' if real[0]['real'] else '실패', aft[1]))
    # ---------- 4. 내 무장을 데려갈 위험 ----------
    w = pg.evaluate('''(() => { var b = facCities(G.player)[0], o = baseOfficers(b).filter(function (x) { return !isLord(x) && !bondOf(x); })[0]; o.loy = 72; clearSel(); showHome();
      var before = Array.prototype.some.call(document.querySelectorAll("#sheet .todo"), function (t) { return /떠날 수 있는 무장/.test(t.innerText); });
      G.peace.until = G.turn; showHome();
      var row = Array.prototype.filter.call(document.querySelectorAll("#sheet .todo"), function (t) { return /떠날 수 있는 무장/.test(t.innerText); })[0];
      var rk = poachRisk(o); return { n: o.n, before: before, row: row ? row.innerText.replace(/\\n/g, " / ") : "", p: rk ? rk.p : 0, by: rk ? rk.by.n : "", idx: row ? Array.prototype.indexOf.call(document.querySelectorAll("#sheet .todo"), row) : -1, need: todoList().need }; })()''')
    print('  위험', w)
    ok(w['before'] is False, '초반 보호 중에는 뜨지 않는다(그동안은 권하지 않으므로)')
    ok(w['row'] and w['n'] in w['row'] and '충성 72' in w['row'] and ('(%d%%)' % w['p']) in w['row'] and '포상' in w['row'], '보호가 끝나면: 지금 할 일에 "떠날 수 있는 무장" [%s]' % w['row'][:60])
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
    hp = pg.evaluate('document.querySelector("#modal").textContent')              # v0.9.2: 도움말은 접힌 토막 — 보이는 글에는 제목만 있다
    ok('군사(軍師)' in hp and '다른 세력의 무장' in hp and '미리 정해져 있습니다' in hp, '도움말: 군사 · 다른 세력의 무장 등용')
    pg.evaluate('closeDialog()')
B.run(steps, 412, 915, 2)
errs = [e for e in B.errors if 'GPU stall' not in e and 'ERR_FILE_NOT_FOUND' not in e]
print('console errors:', errs[:6])
print('FAILS %d' % len(fails), fails)
sys.exit(1 if fails or errs else 0)
