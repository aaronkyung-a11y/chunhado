# v0.21 — 화면 조작으로 확인(09:24 의 아홉 가지 가운데 화면에 드러나는 것들)
#   ① 수송: ②단계는 '어디로' — 지도에 우리 성마다 이름과 날수 · 고르면 나오자마자 행군 · 머물지/돌아갈지는 수송이 끝났을 때 묻는다(턴을 넘기는 사이에 닿으면 내 차례가 오자마자)
#   ② 출진 탭의 초상(그려지는가 — 화면의 점을 본다) · 초상의 모서리   ③ 충성 100 인 무장: 등용 창의 까닭 · '떠날 수 있는 무장'에 꼽히지 않는다
#   ④ 관문: 능선의 먹선이 지도에 선다 · 능선 너머는 갈 수 있는 칸으로 빛나지 않는다 · 내 관문은 지나간다   ⑤ 등용의 말(한 달에 한 번)   ⑥ 무장 이동: 몇 명이든 · [모두]
#   ⑦ 붓으로 그은 틀: 틀은 그림(border-image) · 필터 없음 · 아래 줄이 줄지 않는다   ⑧ 내구: 다음 턴에 돌아올 양 / 회복 멈춤   ⑨ 성공 · 실패의 소리
#   python3 tests/d35.py          찍은 그림은 tests/shots37/
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import taphex, tapsel
B.SHOTS = os.path.join(B.ROOT, 'shots37')
os.makedirs(B.SHOTS, exist_ok=True)
fails = []
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)
def endturn(pg):
    pg.evaluate('''() => { if (MODAL && !MODAL.lock) closeDialog(); talkHide(); doEndTurn(); doEndTurn(); }''')
    pg.wait_for_function('() => !UI.play', timeout=180000); pg.wait_for_timeout(900)
def boxstat(pg, sel, nth=0):
    """그 요소 안쪽(가운데 60%)의 점들: 밝기의 표준편차와 어두운 점의 몫 — 초상이 그려졌는지."""
    bb = pg.locator(sel).nth(nth).bounding_box()
    import io
    from PIL import Image
    im = Image.open(io.BytesIO(pg.screenshot(clip={'x': bb['x'] + bb['width'] * 0.2, 'y': bb['y'] + bb['height'] * 0.2, 'width': bb['width'] * 0.6, 'height': bb['height'] * 0.6}))).convert('L')
    px = list(im.getdata()); m = sum(px) / len(px); sd = (sum((p - m) ** 2 for p in px) / len(px)) ** 0.5
    return round(sd, 1), round(sum(1 for p in px if p < 110) / len(px), 3)
def steps(pg):
    B.start(pg, 0)
    ok(pg.evaluate('GAME_VERSION') == B.VER, '판 번호 ' + B.VER)
    # 이각(장안 · 홍농 · 함곡관 · 동관 · 무관)으로 본다
    pg.evaluate('''() => { newGame(15, 3); G.aiOnly = false; syncScene(); refreshHud(); clearSel(); talkHide(); UI.talk = false; G.factions[15].ap = 250;
      window.SFXLOG = []; var s0 = sfx; sfx = function (k) { SFXLOG.push(k); return s0(k); }; var A = G.bases[baseByName('장안')]; window.T = { a: A.id }; selectBase(A, false, 'mil'); }'''); pg.wait_for_timeout(700)
    # ---------- ② 초상 ----------
    print('② 출진 탭의 초상')
    por = pg.evaluate('''() => { var h = $('hudFac').children[1], s = document.querySelector('#sheet .sh-head .por'); function f(e) { var c = getComputedStyle(e); return [c.backgroundImage.indexOf('blob:') >= 0, c.borderTopLeftRadius, c.borderBottomRightRadius, c.filter]; }
      return { tab: document.querySelector('#sheet .tabs .on') ? document.querySelector('#sheet .tabs .on').textContent : '', hud: f(h), sh: f(s) }; }''')
    st_h, st_s = boxstat(pg, '#hudFac > :nth-child(2)'), boxstat(pg, '#sheet .sh-head .por')
    print('     ', por, st_h, st_s); B.shot(pg, 'a1_mil', 100)
    ok(por['tab'] == '출진' and por['hud'][0] and por['sh'][0], '출진 탭: 위 정보줄과 거점 창의 초상에 그림이 걸려 있다')
    ok(st_h[0] > 25 and st_h[1] > 0.04 and st_s[0] > 25 and st_s[1] > 0.04, '화면의 점으로 보아도 그려져 있다(밝기의 흩어짐 %s · %s, 먹빛 점의 몫 %s · %s)' % (st_h[0], st_s[0], st_h[1], st_s[1]))
    ok(por['sh'][1] == por['sh'][2] == '2px' and por['sh'][3] == 'none', '초상의 모서리는 2px 로 고르다 · 필터가 걸려 있지 않다 %s' % por['sh'])
    # ---------- ⑦ 붓으로 그은 틀 ----------
    print('⑦ 붓으로 그은 틀')
    fr = pg.evaluate('''() => { function af(sel) { var e = document.querySelector(sel); if (!e) return null; var c = getComputedStyle(e, '::after'); return [c.borderImageSource.slice(0, 26), c.borderImageSource.length, c.borderTopWidth, c.filter, c.borderImageSlice]; }
      var all = [].slice.call(document.querySelectorAll('*')), flt = 0; all.forEach(function (e) { if (getComputedStyle(e).filter.indexOf('url') >= 0 || getComputedStyle(e, '::after').filter.indexOf('url') >= 0 || getComputedStyle(e, '::before').filter.indexOf('url') >= 0) flt++; });
      return { cmd: af('#sheet .cmd'), pri: af('#sheet .cmd.pri'), bar: af('#bar button'), end: af('#btnEnd'), ink: !!document.getElementById('inkEdge'), flt: flt, barCls: $('bar').className,
        same: getComputedStyle(document.querySelector('#sheet .cmd.pri'), '::after').borderImageSource === getComputedStyle(document.querySelectorAll('#sheet .cmd')[1], '::after').borderImageSource,
        hud: getComputedStyle($('hud'), '::after').height, end0: Math.round($('btnEnd').getBoundingClientRect().right), w: innerWidth }; }''')
    print('     ', fr)
    ok(fr['cmd'] and fr['cmd'][0].startswith('url("data:image/svg+xml') and fr['cmd'][1] > 2000 and fr['cmd'][2] == '9px' and fr['cmd'][4].startswith('30'), '단추의 틀은 붓 획을 그린 그림(아홉 조각)이다 — 굵기 9px')
    ok(fr['bar'][2] == '7px' and fr['end'][2] == '9px' and not fr['same'], "작은 단추는 7px · '턴 종료'는 9px · 으뜸 단추는 붉은 획(다른 그림)")
    ok(not fr['ink'] and fr['flt'] == 0, 'CSS 필터(url)를 쓰는 요소가 없다 · #inkEdge 도 없다')
    ok(fr['barCls'] == '' and fr['end0'] <= fr['w'] - 4 and fr['hud'] == '13px', "아래 줄이 줄지 않았다(틀이 2px 나와 있어도) · '턴 종료' 끝 %d ≤ %d · 판의 경계 획 13px" % (fr['end0'], fr['w'] - 4))
    # ---------- ⑧ 내구 ----------
    print('⑧ 내구')
    def durtxt(): return pg.evaluate('''() => { var ds = [].filter.call(document.querySelectorAll('#sheet .stats > div'), function (d) { return d.textContent.indexOf('내구') >= 0; })[0]; return ds ? ds.textContent : ''; }''')
    d0 = durtxt()
    pg.evaluate('''() => { var A = G.bases[T.a]; A.dur = 1000; delete A.hitT; refreshSheet(); }'''); pg.wait_for_timeout(200); d1 = durtxt()
    pg.evaluate('''() => { var A = G.bases[T.a]; A.hitT = G.turn; refreshSheet(); }'''); pg.wait_for_timeout(200); d2 = durtxt(); B.shot(pg, 'a2_dur', 100)
    need = pg.evaluate('''() => Math.round(G.bases[T.a].maxDur * DUR_HEAL.pct / 100)''')
    print('     ', d0, '|', d1, '|', d2)
    ok('+' not in d0 and '멈춤' not in d0 and ('+%d' % need) in d1.replace(',', '') and '회복 멈춤' in d2, '내구 칸: 가득이면 숫자만 · 깎였으면 다음 턴에 돌아올 양(+%d) · 방금 맞았으면 "회복 멈춤"' % need)
    pg.evaluate('''() => { var A = G.bases[T.a]; A.dur = A.maxDur; delete A.hitT; refreshSheet(); }''')
    # ---------- ① 수송 ----------
    print('① 수송')
    tapsel(pg, '#sheet [data-a="trans"]'); pg.wait_for_timeout(400)
    s1 = pg.evaluate('''() => document.querySelector('#modal .dlg').textContent''')
    tapsel(pg, '#modal [data-a="next"]'); pg.wait_for_timeout(1300)
    s2 = pg.evaluate('''() => ({ head: document.querySelector('#modal h2').textContent, txt: document.querySelector('#modal .dlg-b').textContent, rows: [].map.call(document.querySelectorAll('#modal .row'), function (e) { return e.textContent; }),
      marks: [].map.call(document.querySelectorAll('#fx .mk'), function (e) { return e.textContent; }), see: $('modal').classList.contains('see'), okOff: document.querySelector('#modal [data-a="ok"]').classList.contains('off'), seg: !!document.querySelector('#modal .seg.tbk') })''')
    print('     ', s2['head'], s2['rows'], s2['marks']); B.shot(pg, 'b1_trans_to', 200)
    ok('짐을 내린' not in s1 and '짐 내린' not in s1 and '어디로' in s2['head'] and not s2['seg'] and '수송을 마쳤을 때' in s2['txt'], "②단계는 '어디로' — 머물지 · 돌아올지를 고르는 칸이 없다('짐을 내린 뒤'라는 말도 없다)")
    ok(s2['see'] and len(s2['rows']) == 5 and all(any(m.startswith(n) and m.endswith('일') for m in s2['marks']) for n in ('동관', '무관', '홍농', '함곡관')) and any(m.startswith('장안') for m in s2['marks']), '지도에 우리 성마다 이름과 날수가 뜬다(동관 · 무관 · 홍농 · 함곡관) · 아래 목록 4곳 + "성 앞에 나가 기다린다"')
    ok(s2['okOff'], '갈 곳을 고르기 전에는 [출발]이 흐리다')
    tapsel(pg, '#modal [data-a="ok"]'); pg.wait_for_timeout(300)
    ok(pg.evaluate('() => !!MODAL && G.units.length === 0'), '고르지 않고 [출발]을 눌러도 나가지 않는다')
    hx = pg.evaluate('''() => { var d = G.bases[baseByName('동관')]; return [d.c, d.r]; }''')
    taphex(pg, hx[0], hx[1]); pg.wait_for_timeout(500)
    s3 = pg.evaluate('''() => ({ pv: document.querySelector('#modal .dlg-f .pv').textContent, sel: document.querySelector('#modal .row.sel') ? document.querySelector('#modal .row.sel').textContent : '', on: [].filter.call(document.querySelectorAll('#fx .mk.on'), function () { return true; }).map(function (e) { return e.textContent; }) })''')
    print('     ', s3); B.shot(pg, 'b2_trans_pick', 150)
    ok(s3['pv'].startswith('동관') and '일' in s3['pv'] and s3['sel'].startswith('동관') and len(s3['on']) == 1 and s3['on'][0].startswith('동관'), '지도에서 동관을 누르면: 목록 · 딱지 · 아래 줄이 모두 동관을 가리킨다')
    tapsel(pg, '#modal [data-a="ok"]'); pg.wait_for_timeout(2600)
    u1 = pg.evaluate('''() => { var u = G.units.filter(function (x) { return x.f === 15 && x.type === 'trans'; })[0], A = G.bases[T.a], d = G.bases[baseByName('동관')]; if (!u) return null; window.T.u = u.id;
      return { dest: destName(u.dest), back: u.back === undefined, moved: hdist(u.c, u.r, A.c, A.r) > 1, closer: hdist(u.c, u.r, d.c, d.r) < hdist(A.c, A.r, d.c, d.r), modal: !!MODAL, sheet: $('sheet').textContent.indexOf('짐 내린 뒤') < 0, home: $('sheet').textContent.indexOf('귀환') >= 0 }; }''')
    print('     ', u1); B.shot(pg, 'b3_trans_go', 150)
    ok(u1 and u1['dest'] == '동관' and u1['moved'] and u1['closer'] and not u1['modal'], '[출발]: 수송대가 나와 곧바로 동관으로 행군한다(이번 턴에 갈 수 있는 만큼 갔다)')
    ok(u1 and u1['back'] and u1['sheet'], "수송대에 '돌아온다'가 미리 붙지 않는다 · 부대 창에 '짐 내린 뒤' 단추가 없다")
    asked = None
    for i in range(6):
        endturn(pg)
        asked = pg.evaluate('''() => (MODAL && MODAL.ask) ? { ask: MODAL.ask, lock: !!MODAL.lock, txt: document.querySelector('#modal .dlg').textContent, x: !!document.querySelector('#modal .x'), btn: [].map.call(document.querySelectorAll('#modal .dlg-f .btn'), function (b) { return b.textContent; }), q: (G.tdone || []).length, rep: !!document.querySelector('#modal .rep') } : null''')
        if asked or not pg.evaluate('() => !!UMAP[T.u]'): break
    print('     ', asked); B.shot(pg, 'b4_trans_ask', 200)
    ok(asked and asked['ask'] == 'trans' and asked['lock'] and not asked['x'] and '수송 완료 — 동관' in asked['txt'], '동관에 닿은 뒤 내 차례가 돌아오자마자 묻는다: "수송 완료 — 동관"(닫는 단추가 없는 창)')
    ok(asked and len(asked['btn']) == 2 and asked['btn'][0].startswith('동관에 머문다') and asked['btn'][1].startswith('장안으로 돌아간다') and '일' in asked['btn'][1], '고를 것 둘: 동관에 머문다 / 장안으로 돌아간다(날수)')
    pg.evaluate('''() => { document.querySelector('#modal').dispatchEvent(new MouseEvent('click', { bubbles: true })); }'''); pg.wait_for_timeout(300)
    ok(pg.evaluate('() => !!(MODAL && MODAL.ask)'), '창 밖을 눌러도 닫히지 않는다')
    tapsel(pg, '#modal [data-a="tgo"]'); pg.wait_for_timeout(1000)
    a2 = pg.evaluate('''() => ({ q: (G.tdone || []).length, trav: G.officers.filter(function (o) { return o.f === 15 && o.st === 'travel'; }).map(function (o) { return G.bases[o.dest].n; }), modal: !!MODAL, ask: MODAL ? MODAL.ask || '' : '', txt: MODAL ? document.querySelector('#modal .dlg').textContent.slice(0, 30) : '' })''')
    print('     ', a2)
    ok(a2['q'] == 0 and a2['trav'] == ['장안'], '[돌아간다]: 호송 무장이 장안으로 길을 떠난다 · 더 물을 것이 없다')
    ok(a2['modal'] and not a2['ask'], '답한 뒤에 지난 턴의 보고가 뜬다 [%s]' % a2['txt'])
    pg.evaluate('''() => { closeDialog(); }''')
    # 손으로 옮겨 넣었을 때: 그 자리에서 묻는다 → 머문다
    pg.evaluate('''() => { var A = G.bases[T.a], d = G.bases[baseByName('동관')]; G.factions[15].ap = 250; var o = idleOfficers(A).filter(function (x) { return !isLord(x); })[0];
      var r = cmdDeploy(A, { type: 'trans', ids: [o.id], troops: 500, food: 1500 }), u = r.unit; var ns = nbrs(d.c, d.r).filter(function (n) { var t = terr(n[0], n[1]); return t !== 'm' && t !== 's' && t !== 'x' && !UAT[K(n[0], n[1])]; }).sort(function (x, y) { return hdist(x[0], x[1], A.c, A.r) - hdist(y[0], y[1], A.c, A.r); })[0];
      placeUnit(u, ns[0], ns[1]); u.mp = uMaxMp(u); u.done = false; syncScene(); selectUnit(u); window.T.o2 = o.id; }'''); pg.wait_for_timeout(600)
    taphex(pg, hx[0], hx[1]); pg.wait_for_timeout(2600)
    a3 = pg.evaluate('''() => (MODAL && MODAL.ask) ? [MODAL.ask, document.querySelector('#modal h2').textContent] : [null, MODAL ? document.querySelector('#modal .dlg').textContent.slice(0, 40) : '', $('toast') ? $('toast').textContent : '']''')
    print('     ', a3)
    ok(a3[0] == 'trans' and '동관' in a3[1], '손으로 움직여 동관에 넣으면 그 자리에서 묻는다')
    if a3[0] == 'trans':
        tapsel(pg, '#modal [data-a="tstay"]'); pg.wait_for_timeout(700)
        a4 = pg.evaluate('''() => { var o = off(T.o2); return [o.st, G.bases[o.loc].n, (G.tdone || []).length, !!MODAL]; }''')
        ok(a4 == ['active', '동관', 0, False], '[머문다]: 그 무장은 동관에 남는다 %s' % a4)
    # 부대에 보급한 뒤에도 묻는다
    pg.evaluate('''() => { if (MODAL) closeDialog(); var A = G.bases[T.a]; G.factions[15].ap = 250; A.troops = Math.max(A.troops, 9000); var os = idleOfficers(A).filter(function (x) { return !isLord(x); });
      var r1 = cmdDeploy(A, { type: 'sword', ids: [os[0].id], troops: 2000, food: 500 }), u = r1.unit, r2 = cmdDeploy(A, { type: 'trans', ids: [os[1].id], troops: 600, food: 4000 }), t = r2.unit;
      var s = [A.c + 3, A.r]; while (terr(s[0], s[1]) === 'm' || UAT[K(s[0], s[1])] || BAT[K(s[0], s[1])] !== undefined) s[0]++; placeUnit(u, s[0], s[1]);
      var n = nbrs(s[0], s[1]).filter(function (q) { return terr(q[0], q[1]) !== 'm' && !UAT[K(q[0], q[1])] && BAT[K(q[0], q[1])] === undefined; })[0]; placeUnit(t, n[0], n[1]); t.done = false; t.born = -5; u.born = -5;
      syncScene(); selectUnit(t); window.T.t = t.id; }'''); pg.wait_for_timeout(600)
    has = pg.evaluate('''() => !!document.querySelector('#sheet [data-a="supply"]')''')
    if has:
        tapsel(pg, '#sheet [data-a="supply"]'); pg.wait_for_timeout(500)
        if pg.evaluate('() => !!document.querySelector("#modal .row")'): tapsel(pg, '#modal .row'); pg.wait_for_timeout(400)
        pg.evaluate('''() => { var f = document.querySelector('#modal input[data-i="food"]'); if (f) { f.value = 1000; f.dispatchEvent(new Event('input', { bubbles: true })); } }''')
        tapsel(pg, '#modal [data-a="ok"]'); pg.wait_for_timeout(1700)
        a5 = pg.evaluate('''() => (MODAL && MODAL.ask) ? [MODAL.ask, document.querySelector('#modal h2').textContent, [].map.call(document.querySelectorAll('#modal .dlg-f .btn'), function (b) { return b.textContent; })] : [null]''')
        print('     ', a5); B.shot(pg, 'b5_supply_ask', 150)
        ok(a5[0] == 'supply' and a5[1] == '보급 완료' and a5[2][0].startswith('이곳에 남는다') and a5[2][1].startswith('장안으로 돌아간다'), '보급을 마치면 묻는다: 이곳에 남는다 / 장안으로 돌아간다')
        if a5[0] == 'supply':
            tapsel(pg, '#modal [data-a="tgo"]'); pg.wait_for_timeout(600)
            ok(pg.evaluate('''() => { var t = UMAP[T.t]; return !!t && destName(t.dest) === '장안' && !MODAL; }'''), '[돌아간다]: 수송대가 장안으로 행군 명령을 받는다')
    else: ok(False, '보급 단추가 없다')
    # ---------- ⑨ 소리 ----------
    print('⑨ 성공 · 실패의 소리')
    snd = pg.evaluate('''() => { var err = ''; try { SFXLOG.length = 0; sfxSyn('good'); sfxSyn('bad'); } catch (e) { err = String(e); } return { err: err, pl: typeof pluck }; }''')
    ok(not snd['err'] and snd['pl'] == 'function', '만든 소리 good · bad 가 탈 없이 난다 ' + snd['err'])
    # 등용: 응할 사람 / 거절할 사람을 하나씩 만들어 권한다
    pg.evaluate('''() => { if (MODAL) closeDialog(); clearSel(); var A = G.bases[T.a]; G.factions[15].ap = 250; baseOfficers(A).forEach(function (o) { o.acted = false; });
      var me = idleOfficers(A).sort(function (x, y) { return y.cha - x.cha; })[0], hs = G.officers.filter(function (o) { return o.st === 'hidden' && !bondWith(o, 15); }), yes = null, no = null;
      hs.forEach(function (o) { var l0 = o.loc; o.st = 'free'; o.loc = A.id; var p = recruitChance(A, me, o), r = recruitRoll(o); if (!yes && r < p) yes = o; else if (!no && r >= p) no = o; o.st = 'hidden'; o.loc = l0; });
      yes.st = 'free'; yes.loc = A.id; no.st = 'free'; no.loc = A.id; window.T.yes = yes.id; window.T.no = no.id; window.T.me = me.id; selectBase(A, false, 'men'); }'''); pg.wait_for_timeout(500)
    def recruit(tid):
        pg.evaluate('''() => { SFXLOG.length = 0; }''')
        tapsel(pg, '#sheet [data-a="recruit"]'); pg.wait_for_timeout(400)
        pg.locator('#modal [data-a="t"][data-v="%d"]' % tid).tap(); pg.wait_for_timeout(500)
        pg.locator('#modal [data-a="pick"][data-v="%d"]' % pg.evaluate('T.me')).tap(); pg.wait_for_timeout(300)
        tapsel(pg, '#modal [data-a="ok"]'); pg.wait_for_timeout(700)
        return pg.evaluate('''() => SFXLOG.slice()''')
    note = None
    tapsel(pg, '#sheet [data-a="recruit"]'); pg.wait_for_timeout(400)
    note = pg.evaluate('''() => document.querySelector('#modal .dlg-b').textContent'''); B.shot(pg, 'c1_recruit', 100); pg.evaluate('() => closeDialog()')
    ok('한 사람에게 한 달에 한 번' in note, '⑤ 등용 창: "한 사람에게 한 달에 한 번"이 재야 · 포로 쪽에도 적혀 있다')
    sy = recruit(pg.evaluate('T.yes')); st_y = pg.evaluate('() => off(T.yes).st')
    pg.evaluate('''() => { if (MODAL) closeDialog(); talkHide(); baseOfficers(G.bases[T.a]).forEach(function (o) { o.acted = false; }); G.factions[15].ap = 250; refreshSheet(); }'''); pg.wait_for_timeout(300)
    sn = recruit(pg.evaluate('T.no')); st_n = pg.evaluate('() => off(T.no).st')
    print('     ', sy, st_y, sn, st_n)
    ok(st_y == 'active' and 'good' in sy and 'bad' not in sy, '등용 성공: 맑게 올라가는 소리(good) %s' % sy)
    ok(st_n == 'free' and 'bad' in sn and 'good' not in sn, '등용 실패: 낮게 내려가는 소리(bad) %s' % sn)
    pg.evaluate('''() => { if (MODAL) closeDialog(); talkHide(); baseOfficers(G.bases[T.a]).forEach(function (o) { o.acted = false; }); G.factions[15].ap = 250; refreshSheet(); }'''); pg.wait_for_timeout(300)
    tapsel(pg, '#sheet [data-a="recruit"]'); pg.wait_for_timeout(400)
    again = pg.evaluate('''() => { var r = document.querySelector('#modal [data-a="t"][data-v="' + T.no + '"]'); return r ? r.textContent : ''; }'''); pg.evaluate('() => closeDialog()')
    ok('다음 달에 다시' in again, '거절한 재야 무장의 줄: "다음 달에 다시" [%s]' % again[-24:])
    # ---------- ③ 충성 100 ----------
    print('③ 충성 100')
    l100 = pg.evaluate('''() => { var A = G.bases[T.a], ts = poachTargets(A).filter(function (t) { return !bondOf(t); }); if (!ts.length) return null; var t = ts[0]; t.loy = 100; window.T.p = t.id;
      var mine = G.officers.filter(function (o) { return o.f === 15 && o.st === 'active' && !isLord(o) && !bondOf(o) && o.unit === null; })[0]; mine.loy = 100; var rk = poachRisk(mine);
      return { n: t.n, p: bestRecruiter(A, t).p, risk: rk ? rk.p : 0, hint: todoList().filter(function (x) { return x.ic === '離' && x.say && x.say.indexOf(mine.n) >= 0; }).length }; }''')
    print('     ', l100)
    if l100:
        tapsel(pg, '#sheet [data-a="recruit"]'); pg.wait_for_timeout(400)
        row = pg.evaluate('''() => { var r = document.querySelector('#modal [data-a="t"][data-v="' + T.p + '"]'); return r ? r.textContent : ''; }'''); B.shot(pg, 'c2_loy100', 100); pg.evaluate('() => closeDialog()')
        ok(l100['p'] == 0 and '충성 100' in row, '충성 100 인 이웃 무장: 가능성 0 · 줄에 "충성 100" [%s]' % row[-30:])
        ok(l100['risk'] == 0 and l100['hint'] == 0, '충성 100 인 내 무장은 "떠날 수 있는 무장"에 꼽히지 않는다')
    else: ok(False, '이웃한 다른 세력의 무장이 없다')
    # ---------- ⑥ 무장 이동 ----------
    print('⑥ 무장 이동')
    pg.evaluate('''() => { if (MODAL) closeDialog(); talkHide(); var A = G.bases[T.a]; baseOfficers(A).forEach(function (o) { o.acted = false; }); G.factions[15].ap = 250; selectBase(A, false, 'men'); }'''); pg.wait_for_timeout(400)
    n_idle = pg.evaluate('() => idleOfficers(G.bases[T.a]).length')
    tapsel(pg, '#sheet [data-a="move"]'); pg.wait_for_timeout(400)
    m0 = pg.evaluate('''() => ({ pv: document.querySelector('#modal .dlg-f .pv').textContent, all: !!document.querySelector('#modal [data-a="all"]') })''')
    tapsel(pg, '#modal [data-a="all"]'); pg.wait_for_timeout(300)
    m1 = pg.evaluate('''() => ({ n: document.querySelectorAll('#modal .tr.sel').length, btn: document.querySelector('#modal [data-a="all"]').textContent, pv: document.querySelector('#modal .dlg-f .pv').textContent })'''); B.shot(pg, 'd1_move_all', 100)
    print('     ', n_idle, m0, m1)
    ok(n_idle > 6 and m0['all'] and '몇 명이든' in m0['pv'] and m1['n'] == n_idle and m1['btn'] == '모두 풀기', '[모두]: 쉬는 무장 %d명을 한 번에 고른다(전에는 6명까지)' % n_idle)
    tapsel(pg, '#modal [data-a="ok"]'); pg.wait_for_timeout(900)
    pg.locator('#modal .row').nth(0).tap(); pg.wait_for_timeout(900)
    mv = pg.evaluate('''() => G.officers.filter(function (o) { return o.f === 15 && o.st === 'travel'; }).length''')
    ok(mv >= n_idle, '한 번에 %d명이 길을 떠났다(쉬던 무장 %d명)' % (mv, n_idle))
    # ---------- ④ 관문 ----------
    print('④ 관문과 능선')
    pg.evaluate('''() => { if (MODAL) closeDialog(); clearSel(); talkHide(); }''')
    gw = pg.evaluate('''() => { var n = 0, tri = 0; R3.scene.traverse(function (o) { if (o.isMesh && o.material && o.material.color && o.material.color.getHex() === 0x1b1a18 && o.material.opacity > 0.7 && o.geometry.index) { n++; tri += o.geometry.index.count / 3; } });
      return { walls: (MAPDATA.walls || []).length, mesh: n, tri: tri }; }''')
    print('     ', gw)
    ok(gw['walls'] == 143 and gw['mesh'] >= 1 and gw['tri'] >= 143 * 6, '능선 143변이 지도에 먹선으로 선다(세모 %d개)' % gw['tri'])
    g1 = pg.evaluate('''() => { var g = G.bases[baseByName('함곡관')], hn = G.bases[baseByName('홍농')]; G.factions[15].ap = 250; hn.troops = Math.max(hn.troops, 9000);
      var ns = nbrs(g.c, g.r).filter(function (n) { var t = terr(n[0], n[1]); return t !== 'm' && t !== 's' && t !== 'x'; }), A = ns[0], Bq = ns[1];
      var o = baseOfficers(hn).filter(function (x) { return x.unit === null; })[0]; o.acted = false; var r = cmdDeploy(hn, { type: 'spear', ids: [o.id], troops: 2000, food: 3000 }), u = r.unit; placeUnit(u, Bq[0], Bq[1]); u.mp = uMaxMp(u); u.done = false; u.born = -5;
      syncScene(); jumpTo(g.c + 1, g.r, 1.25, 0.42, 0); selectUnit(u); window.T.g = u.id; window.T.A = A; window.T.B = Bq;
      return { A: A, B: Bq, reachA: !!UI.rc.stop[K(A[0], A[1])], gate: [g.c, g.r], troops: g.troops }; }'''); pg.wait_for_timeout(1500); B.shot(pg, 'e1_gate_own', 300)
    print('     ', g1)
    ok(g1['reachA'], '내 관문(함곡관): 건너편 칸이 갈 수 있는 칸으로 빛난다')
    taphex(pg, g1['A'][0] + 1, g1['A'][1]); pg.wait_for_timeout(2600)
    g2 = pg.evaluate('''() => { var u = UMAP[T.g], g = G.bases[baseByName('함곡관')]; return u ? { at: [u.c, u.r], side: hdist(u.c, u.r, T.A[0], T.A[1]) <= 2, gate: g.troops } : null; }''')
    print('     ', g2)
    ok(g2 and g2['side'] and g2['gate'] == g1['troops'], '건너편의 칸을 누르면 관문을 지나 그리로 간다(관문에 입성하지 않는다)')
    g3 = pg.evaluate('''() => { var g = G.bases[baseByName('함곡관')], u = UMAP[T.g]; g.owner = G.bases.filter(function (b) { return b.owner >= 0 && b.owner !== 15; })[0].owner; placeUnit(u, T.B[0], T.B[1]); u.mp = uMaxMp(u); u.done = false; u.moved = false;
      syncScene(); clearSel(); selectUnit(u); return { reachA: !!UI.rc.stop[K(T.A[0], T.A[1])], atk: (UI.atk || []).map(function (t) { return t.kind + (t.b ? t.b.n : ''); }) }; }'''); pg.wait_for_timeout(900); B.shot(pg, 'e2_gate_foe', 300)
    print('     ', g3)
    ok(not g3['reachA'] and 'base함곡관' in g3['atk'], '남의 관문이 되면: 건너편 칸이 빛나지 않는다 · 관문은 칠 수 있다')
    # ---------- 도움말 ----------
    pg.evaluate('''() => { clearSel(); if (typeof showHelp === 'function') showHelp(); }'''); pg.wait_for_timeout(400)
    hp = pg.evaluate('''() => MODAL ? document.querySelector('#modal .dlg').textContent : ""''')
    ok(all(k in hp for k in ('관문과 능선', '성의 내구', '수송을 마친 뒤', '한 사람에게 한 달에 한 번')) and '짐을 내린 뒤' not in hp, '도움말: 관문과 능선 · 성의 내구 · 등용 · 수송을 마친 뒤')
    print('console errors:', [e for e in B.errors if 'ReadPixels' not in e and 'ERR_FILE_NOT_FOUND' not in e][:6])
    ok(not [e for e in B.errors if e.startswith('pageerror')], '화면 오류 없음')
B.run(steps, 393, 852, 2)
print('FAILS', len(fails), fails)
sys.exit(1 if fails else 0)
