# v0.23 — 화면: 시대 고르기 · 나이 · 후계 정하기 · 군주의 죽음과 후계 알림 (요청 11-25 11:17 의 5 · 6번, 13:08 의 후계)
#   1) 새 판: 시대 단추 여덟 개(처음에는 194년). 시대를 바꾸면 세력 표가 바뀐다. 207년 유비로 시작하면 207년 1월 상순, 신야, 제갈량은 신야에서 찾는다.
#   2) 무장 창: 나이(세는나이)와 태어난 해. 사서에 없는 해에는 '추정'.
#   3) 후계 정하기: 군주의 무장 창 → [후계 정하기] → 차례대로 늘어선 표. 누르면 정해지고(후계 표시), 다시 누르면 풀린다. 무장 창의 [후계로 세우기]도 같다.
#   4) 군주가 세상을 떠나면: 병석 알림 → 뒤를 이음 → 내 차례에 '후계' 창(충성의 변화) → 세력의 이름이 바뀐다. 혈연이 아닌 후계면 선대의 일가가 흔들린다.
#   5) 저장하고 다시 열어도 시대 · 후계 · 나이가 그대로다.
#   6) 수명 켬 · 끔: 새 판 창의 단추, 메뉴의 단추. 무장 창에 아버지 · 자식.
#   python3 tests/d39.py          찍은 그림은 tests/shots39/h_*.png
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
B.SHOTS = os.path.join(B.ROOT, 'shots39')
os.makedirs(B.SHOTS, exist_ok=True)
fails = []
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)
def tapsel(pg, sel, nth=0, wait=350): pg.locator(sel).nth(nth).tap(); pg.wait_for_timeout(wait)
def steps(pg):
    # ================= 1. 시대 고르기 =================
    print('1. 시대 고르기')
    ok(pg.evaluate('GAME_VERSION') == B.VER, '판 번호 ' + B.VER)
    tapsel(pg, '#tNew')
    a = pg.evaluate('''() => ({ n: document.querySelectorAll('#modal .scb').length, on: [].map.call(document.querySelectorAll('#modal .scb.on'), function (e) { return e.getAttribute('data-v'); }),
      rows: document.querySelectorAll('#modal .row').length, h: document.querySelector('#modal h2').textContent, w: document.querySelector('#modal .scn').getBoundingClientRect().width,
      cut: [].some.call(document.querySelectorAll('#modal .scb span'), function (e) { return e.scrollWidth > e.parentNode.clientWidth + 1; }) })''')
    print('    ', a)
    ok(a['n'] == 8 and a['on'] == ['194'] and a['rows'] == 19 and '194년 군웅할거' in a['h'], '시대 단추 8개 · 처음은 194년 군웅할거(세력 19)')
    ok(not a['cut'], '시대 이름이 단추 밖으로 넘치지 않는다')
    B.shot(pg, 'h_scen194')
    lf = [pg.evaluate('() => document.querySelector("#modal .lifeb").textContent')]
    tapsel(pg, '#modal .lifeb', 0, 200); lf.append(pg.evaluate('() => document.querySelector("#modal .lifeb").textContent'))
    tapsel(pg, '#modal .lifeb', 0, 200); lf.append(pg.evaluate('() => document.querySelector("#modal .lifeb").textContent'))
    ok(lf[0].startswith('수명 켬') and lf[1].startswith('수명 끔') and '늙어 죽지 않습니다' in lf[1] and lf[2].startswith('수명 켬'), '수명 단추: 처음에는 켬 · 누르면 끔 · 다시 누르면 켬')
    seen = {}
    for sid, nf, nm in [('184', 10, '황건의 난'), ('190', 20, '반동탁 연합'), ('200', 9, '관도대전'), ('219', 4, '한중 쟁탈'), ('227', 4, '출사표'), ('234', 4, '오장원'), ('207', 9, '삼고초려')]:
        tapsel(pg, '#modal .scb[data-v="%s"]' % sid, 0, 250)
        seen[sid] = pg.evaluate('''() => ({ rows: document.querySelectorAll('#modal .row').length, h: document.querySelector('#modal h2').textContent, go: document.querySelector('#modal [data-a=go]').disabled,
          names: [].map.call(document.querySelectorAll('#modal .row .nm'), function (e) { return e.firstChild.textContent.trim(); }), por: [].every.call(document.querySelectorAll('#modal .row .por'), function (e) { return /url\\(/.test(e.getAttribute('style') || ''); }),
          wide: [].some.call(document.querySelectorAll('#modal .row'), function (e) { return e.scrollWidth > e.clientWidth + 1; }) })''')
        ok(seen[sid]['rows'] == nf and (sid + '년 ' + nm) in seen[sid]['h'] and seen[sid]['go'] and seen[sid]['por'] and not seen[sid]['wide'], '%s년 %s: 세력 %d · 군주마다 초상 · 줄이 넘치지 않는다 · 군주를 고르기 전에는 [시작]이 잠겨 있다' % (sid, nm, nf))
    print('     207:', seen['207']['names'])
    B.shot(pg, 'h_scen207')
    k = seen['207']['names'].index('유비')
    tapsel(pg, '#modal .row', k); tapsel(pg, '#modal [data-a=go]'); pg.wait_for_timeout(700)
    g = pg.evaluate('''() => { var F = G.factions[G.player], L = off(F.lord), z = offByName('제갈량'), b = G.bases[L.loc];
      return { scen: G.scen, date: dateStr(), d1: dateOfTurn(1), f: F.name, house: F.house, city: b.n, own: b.owner === G.player, intro: document.querySelector('#modal') ? document.querySelector('#modal').textContent.slice(0, 90) : '',
        zg: [z.st, z.y, G.bases[z.loc].n, hiddenOfficers(G.bases[z.loc]).indexOf(z) >= 0], nf: G.factions.length, cao: facBases(0).length, dead: G.officers.filter(function (o) { return o.st === 'dead'; }).length,
        peace: dateOfTurn(G.peace.until - 1) }; }''')
    print('    ', g)
    ok(g['scen'] == '207' and g['date'] == '207년 1월 상순' and g['d1'] == '207년 1월 상순' and g['f'] == '유비' and g['city'] == '신야' and g['own'], '207년 유비로 시작: 207년 1월 상순 · 신야')
    ok('와룡' in g['intro'] and g['peace'].startswith('20'), '첫 창에 그 시대의 소개가 나온다 · 초반 보호의 날짜가 207년부터 센다(%s)' % g['peace'])
    ok(g['zg'] == ['hidden', 207, '신야', True], '제갈량은 신야에 숨어 있다 — 탐색으로 찾는다(삼고초려)')
    ok(g['nf'] == 9 and g['cao'] >= 17 and g['dead'] > 100, '조조는 하북까지(거점 %d) · 이미 세상을 떠난 사람 %d명은 나오지 않는다' % (g['cao'], g['dead']))
    tapsel(pg, '#modal [data-a=close]'); pg.wait_for_timeout(600)
    pg.evaluate('() => { talkHide(); UI.talk = false; }')

    # ================= 2. 나이 =================
    print('2. 나이')
    r = pg.evaluate('''() => { var L = off(G.factions[G.player].lord), gy = offByName('관우'); showOfficer(L); var a = document.querySelector('#modal .stats').textContent; closeDialog();
      showOfficer(gy); var b = document.querySelector('#modal .stats').textContent; closeDialog();
      ocardOpen(offByName('동탁')); var c = document.querySelector('#ocard .stats').textContent; ocardClose();
      return { lord: a, gy: b, dead: c, age: ageOf(L), by: L.by, e: [L.e || 0, gy.e || 0] }; }''')
    print('    ', r)
    ok(r['age'] == 47 and '47세' in r['lord'] and '161년생' in r['lord'] and '추정' not in r['lord'], '유비: 47세 · 161년생(사서에 있는 해 — 추정 표시가 없다)')
    ok('162년생' in r['gy'] and '추정' in r['gy'], '관우: 162년생 · 추정')
    ok('139 ~ 192' in r['dead'] and '향년 54세' in r['dead'], '세상을 떠난 사람(동탁)은 생몰년: 139 ~ 192 · 향년 54세')
    fm = pg.evaluate('''() => { var L = off(G.factions[G.player].lord); showOfficer(L); var a = (document.querySelector('#modal .note.fam') || {}).textContent || ''; closeDialog();
      showOfficer(offByName('관평')); var b = (document.querySelector('#modal .note.fam') || {}).textContent || ''; closeDialog(); return { lord: a, gp: b, life: G.life }; }''')
    print('    ', fm)
    ok('자식' in fm['lord'] and '유선(1세)' in fm['lord'] and '아버지 관우' in fm['gp'] and fm['life'] == 1, '무장 창에 아버지 · 자식이 적힌다(유비: 자식 유선(1세) · 관평: 아버지 관우)')

    # ================= 3. 후계 정하기 =================
    print('3. 후계 정하기')
    pg.evaluate('() => { showOfficer(off(G.factions[G.player].lord)); }'); pg.wait_for_timeout(300)
    f0 = pg.evaluate('''() => ({ btn: !!document.querySelector('#modal [data-a=heirs]'), note: (document.querySelector('#modal .note.heir') || {}).textContent || '' })''')
    ok(f0['btn'] and '정하지 않음' in f0['note'], '군주의 무장 창: [후계 정하기] · "%s"' % f0['note'])
    tapsel(pg, '#modal [data-a=heirs]')
    h1 = pg.evaluate('''() => { var rk = heirRank(G.player); return { n: document.querySelectorAll('#modal .hrl .row').length, first: document.querySelector('#modal .hrl .row').textContent.slice(0, 60), rk: rk.slice(0, 4).map(function (o) { return o.n; }),
      wide: [].some.call(document.querySelectorAll('#modal .row'), function (e) { return e.scrollWidth > e.clientWidth + 1; }), heir: G.factions[G.player].heir }; }''')
    print('    ', h1)
    ok(h1['n'] >= 5 and '지금 차례' in h1['first'] and h1['heir'] == -1 and not h1['wide'], '후계 창: 뒤를 이을 차례대로 · 맨 위는 "지금 차례"(%s)' % h1['rk'][0])
    ok(h1['rk'][0] == '관우' and '의형제' in h1['first'] and '일가 반발' not in h1['first'], '관우는 유비의 의형제 — 한집안이라 뒤를 이어도 선대의 인연이 이어진다')
    B.shot(pg, 'h_heir')
    gy = pg.evaluate('() => offByName("관우").id')
    tapsel(pg, '#modal .hrl .row[data-v="%d"]' % gy)
    h2 = pg.evaluate('''() => ({ heir: G.factions[G.player].heir, sel: (document.querySelector('#modal .hrl .row.sel') || {}).textContent || '', pv: document.querySelector('#modal .dlg-f .pv').textContent })''')
    ok(h2['heir'] == gy and '후계' in h2['sel'] and '관우' in h2['pv'], '관우를 누르면 후계로 정해진다(줄에 "후계", 아래에 "정해 둔 후계 관우")')
    tapsel(pg, '#modal .hrl .row[data-v="%d"]' % gy)
    ok(pg.evaluate('() => G.factions[G.player].heir') == -1, '다시 누르면 풀린다')
    pg.evaluate('() => { closeDialog(); closeDialog(); showOfficer(offByName("조운")); }'); pg.wait_for_timeout(300)
    n1 = pg.evaluate('''() => ({ note: (document.querySelector('#modal .note.heir') || {}).textContent || '', btn: (document.querySelector('#modal [data-a=heir]') || {}).textContent || '' })''')
    print('    ', n1)
    ok('한집안이 아님' in n1['note'] and '일가 반발' in n1['note'] and n1['btn'] == '후계로 세우기', '조운의 무장 창: 뒤를 이으면 "한집안이 아님 · 일가 반발 N명" · [후계로 세우기]')
    tapsel(pg, '#modal [data-a=heir]')
    n2 = pg.evaluate('''() => ({ heir: G.factions[G.player].heir === offByName('조운').id, tag: document.querySelector('#modal h2').textContent, btn: document.querySelector('#modal [data-a=heir]').textContent, role: roleTag(offByName('조운')) })''')
    ok(n2['heir'] and '후계' in n2['tag'] and n2['btn'] == '후계 풀기' and n2['role'] == '후계', '[후계로 세우기] → 조운이 후계 · 창 머리에 "후계" · 단추는 [후계 풀기]')
    pg.evaluate('() => { closeDialog(); }')

    # ================= 4. 군주의 죽음 =================
    print('4. 군주의 죽음과 후계')
    pre = pg.evaluate('''() => { var L = off(G.factions[G.player].lord); L.dy = G.year; L.dm = 5; window.L0 = L.id;      // 유비가 207년 5월에 세상을 떠난다
      var o = {}; ['관우', '장비', '미축', '간옹', '서서', '조운'].forEach(function (n) { var x = offByName(n); o[n] = [x.loy, bondOf(x)]; }); return o; }''')
    print('     앞:', pre)
    def end_turn(): pg.evaluate('() => { endTurn(); }')
    sick = None
    for t in range(13):
        end_turn()
        s = pg.evaluate('''() => { var L = off(L0); return { d: dateStr(), st: L.st, sick: !!L.sick, name: G.factions[G.player].name, succ: G.succ ? [off(G.succ.heir).n, G.succ.kin, G.succ.named, G.succ.rows.length, G.succ.keep] : null,
          news: G.log.filter(function (e) { return e.f === G.player && /병석|뒤를 이었다/.test(e.t); }).map(function (e) { return e.d + ' ' + e.t; }) }; }''')
        if s['sick'] and sick is None: sick = s['d']; print('     병석:', s['d'], s['news'][-1:])
        if s['st'] == 'dead': break
    print('    ', s)
    ok(sick is not None and sick.startswith('207년 2월'), '숨을 거두기 석 달 앞서 병석에 눕는다(%s) — "후계를 정해 두십시오"' % sick)
    ok(s['st'] == 'dead' and s['d'].startswith('207년 5월') and s['name'] == '조운', '207년 5월에 유비가 세상을 떠나고 정해 둔 후계 조운이 잇는다 — 세력의 이름이 조운군으로')
    ok(s['succ'] and s['succ'][0] == '조운' and s['succ'][1] is False and s['succ'][2] is True, '후계 기록: 조운 · 혈연이 아님 · 미리 정해 둠')
    ok(len(s['news']) == 2 and '유비가 병석에 누웠다(47세)' in s['news'][0] and '유비 병사 (향년 47세) — 조운이 뒤를 이었다 (한집안이 아니다)' in s['news'][1], '기록에 남는다: ' + ' / '.join(s['news']))
    post = pg.evaluate('''() => { var o = {}; ['관우', '장비', '미축', '간옹', '서서', '조운'].forEach(function (n) { var x = offByName(n); o[n] = [x.loy, bondOf(x)]; }); return o; }''')
    print('     뒤:', post)
    ok(pre['관우'] == [100, '의형제'] and post['관우'][1] is None and 75 <= post['관우'][0] <= 85 and 75 <= post['장비'][0] <= 85, '선대의 의형제(관우 · 장비)는 인연이 끊겨 충성이 15 ~ 25 내린다(%d · %d)' % (post['관우'][0], post['장비'][0]))
    ok(post['미축'][1] is None and 75 <= post['미축'][0] <= 85, '인척(미축)도 내린다(%d)' % post['미축'][0])
    ok(post['간옹'][1] is None and (post['간옹'][0] == 100 or 85 <= post['간옹'][0] <= 92), '심복(간옹)은 흔들릴 수도 그대로일 수도(%d)' % post['간옹'][0])
    pg.evaluate('() => { EVQ.length = 0; succShow(function () { window.SUCC_CB = 1; }); }'); pg.wait_for_timeout(400)
    d = pg.evaluate('''() => ({ h: (document.querySelector('#modal h2') || {}).textContent || '', body: (document.querySelector('#modal .dlg-b') || {}).textContent.slice(0, 120), rows: document.querySelectorAll('#modal .rows .row').length,
      bad: document.querySelectorAll('#modal .rows .row .rt .bad').length, pv: (document.querySelector('#modal .dlg-f .pv') || {}).textContent || '' })''')
    print('    ', d)
    ok('후계' in d['h'] and '조운' in d['h'] and '한집안이 아닙니다' in d['body'] and d['rows'] >= 3 and d['bad'] >= 3 and '조운군' in d['pv'], '후계 창: 누가 뒤를 이었는지 · 혈연이 아니라는 말 · 충성이 내린 무장들(%d줄)' % d['rows'])
    B.shot(pg, 'h_succ')
    tapsel(pg, '#modal [data-a=close]'); pg.wait_for_timeout(300)
    ok(pg.evaluate('() => G.succ.seen === 1 && window.SUCC_CB === 1'), '확인을 누르면 다시 뜨지 않는다(다음 창으로 넘어간다)')
    hud = pg.evaluate('''() => { refreshHud(); refreshSheet(); return { title: (document.querySelector('.sh-title') || {}).textContent || '', lordAge: ageOf(off(G.factions[G.player].lord)), adv: facAdv(G.player) ? facAdv(G.player).n : '' }; }''')
    ok('조운군' in hud['title'] and hud['adv'] != '조운', 'STATUS 창의 이름도 조운군 · 군사는 새 군주가 아닌 사람(%s)' % hud['adv'])

    # ================= 5. 저장 =================
    print('5. 저장')
    sv = pg.evaluate('''() => { var s = serialize(), g = JSON.parse(s), shape = saveShapeOk(g); G = null; scenarioUse('194'); var ok2 = deserialize(s);
      return { shape: shape, ok: ok2 !== false, scen: G.scen, sy: SCENARIO.year, name: G.factions[G.player].name, past: G.factions[G.player].past, n: G.officers.length, by: offByName('조운').by, date: dateOfTurn(1) }; }''')
    print('    ', sv)
    ok(sv['shape'] and sv['ok'] and sv['scen'] == '207' and sv['sy'] == 207 and sv['name'] == '조운' and sv['past'] == ['유비'] and sv['by'] == 168 and sv['date'] == '207년 1월 상순', '저장을 다시 열면 시대(207) · 군주(조운 ← 유비) · 나이가 그대로')

    # ================= 6. 수명 켬 · 끔 =================
    print('6. 수명 켬 · 끔')
    pg.evaluate('() => { UI.scenPick = "194"; showFactionSelect(); }'); pg.wait_for_timeout(300)
    tapsel(pg, '#modal .lifeb', 0, 200); tapsel(pg, '#modal .row', 0); tapsel(pg, '#modal [data-a=go]'); pg.wait_for_timeout(700)
    z = pg.evaluate('() => ({ life: G.life, scen: G.scen, f: G.factions[G.player].name })')
    ok(z == {'life': 0, 'scen': '194', 'f': '조조'}, '수명을 끄고 시작한 판: G.life = 0')
    tapsel(pg, '#modal [data-a=close]'); pg.wait_for_timeout(500)
    pg.evaluate('() => { talkHide(); UI.talk = false; showMenu(); }'); pg.wait_for_timeout(300)
    m0 = pg.evaluate('() => document.querySelector("#modal [data-a=life]").textContent')
    tapsel(pg, '#modal [data-a=life]', 0, 300)
    m1 = pg.evaluate('() => ({ t: document.querySelector("#modal [data-a=life]").textContent, life: G.life })')
    ok(m0.startswith('수명 꺼짐') and m1['t'].startswith('수명 켜짐') and m1['life'] == 1, '메뉴의 수명 단추로 판을 하는 중에도 켠다')
    B.shot(pg, 'h_menu')
    pg.evaluate('() => { closeDialog(); }')
B.run(steps, 393, 852, 2)
errs = [e for e in B.errors if 'ReadPixels' not in e and 'ERR_FILE' not in e and 'GPU stall' not in e and 'AudioContext' not in e]
print('오류 기록:', errs[:6])
ok(not errs, '오류 · 경고 기록이 없다(%d건)' % len(errs))
print('\nd39: %d fail' % len(fails))
for f in fails: print('  ✗', f)
sys.exit(1 if fails else 0)
