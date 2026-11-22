# v0.18.1 — 화면 조작으로 확인: ① 수송 창의 '짐을 내린 뒤 — 그곳에 머문다 | 돌아온다', 부대 창의 [짐 내린 뒤] · [귀환], 거점에 들어갔을 때 · 보급했을 때의 말
#   ② '지금 할 일'의 풀이 글 속 군사 표시가 둥근 배지로 그려지지 않는다(글과 같은 줄 · 말로)
#   python3 tests/d32.py          찍은 그림은 tests/shots34/
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import taphex, tapsel
B.SHOTS = os.path.join(B.ROOT, 'shots34')
os.makedirs(B.SHOTS, exist_ok=True)
fails = []
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)
def toast(pg): return pg.evaluate('$("toast").textContent')
# 내 도시 A 와, 걸어서 두 턴 넘게 걸리는 빈 거점 B(내 것으로 둔다). T = { a, b, tt }
SETUP = """() => {
  G.aiOnly = false;
  var A = facCities(G.player)[0];
  var es = G.bases.filter(function (x) { return x.owner < 0; }).sort(function (p, q) { return hdist(A.c, A.r, p.c, p.r) - hdist(A.c, A.r, q.c, q.r); });
  var Bb = es.filter(function (x) { return travelTurns(x, A) >= 2; })[0] || es[es.length - 1];
  Bb.owner = G.player; Bb.troops = 2000; Bb.food = 10000; Bb.gold = 500;
  A.troops = 60000; A.food = 400000; A.gold = 20000; A.w.spear = 30000; G.factions[G.player].ap = 250;
  HOME.open = true; clearSel(); UI.dirty = true; syncScene(); requestDraw();
  window.T = { a: A.id, b: Bb.id, an: A.n, bn: Bb.n, tt: travelTurns(Bb, A) };
  return window.T;
}"""
DOOR = """(a) => { var u = UMAP[a[0]], b = G.bases[a[1]], ns = nbrs(b.c, b.r);
  for (var i = 0; i < ns.length; i++) { var c = ns[i][0], r = ns[i][1]; if (inMap(c, r) && !UAT[K(c, r)] && BAT[K(c, r)] === undefined && moveCost(u, c, r) < 99) { placeUnit(u, c, r); u.born = -9; u.done = false; u.mp = uMaxMp(u); u.ox = -1; return [c, r]; } }
  return null; }"""
SHEET = """() => Array.prototype.map.call(document.querySelectorAll('#sheet .acts .act'), function (e) { var b = e.querySelector('b'), s = e.querySelector('small'); return { a: e.getAttribute('data-a'), b: b ? b.textContent : '', s: s ? s.textContent : '', on: e.classList.contains('on'), off: e.classList.contains('off'), fit: e.scrollWidth <= e.clientWidth + 1 }; })"""
def steps(pg):
    B.start(pg, 0)
    T = pg.evaluate(SETUP); pg.wait_for_timeout(400)
    print('  준비:', T)
    ok(pg.evaluate('GAME_VERSION') == 'v0.18.1' and T['tt'] >= 2, '판 번호 v0.18.1 · %s → %s 는 걸어서 %d턴' % (T['bn'], T['an'], T['tt']))

    # ---------- ② '지금 할 일'의 군사 표시 ----------
    tips = pg.evaluate('''() => { var A = G.bases[T.a], os = idleOfficers(A), free = G.officers.filter(function (o) { return o.st !== 'active' && o.st !== 'captive' && o.f < 0; });
      function tip(c) { c.b = A.id; c.lvl = 2; return counselText(c).tip; }
      return [tip({ kind: 'recruit', x: { pick: { t: free[0].id, o: os[0].id }, ts: [free[0].id, free[1].id], says: false } }), tip({ kind: 'recruit', x: { pick: { t: free[0].id, o: os[0].id }, ts: [free[0].id], says: true } }),
        tip({ kind: 'search', x: { o: os[0].id, says: true } }), tip({ kind: 'search', x: { o: os[0].id, says: false } })]; }''')
    print('  풀이 글:', tips)
    ok('오늘은 불응' in tips[0] and '응할 듯' in tips[1] and '만날 듯' in tips[2] and '오늘은 못 만남' in tips[3] and not any(('○' in t or '×' in t) for t in tips), '군사의 예측은 기호(○ · ×) 대신 말로 — 응할 듯 · 오늘은 불응 · 만날 듯 · 오늘은 못 만남')
    ok(all(('class="adv y"' in t or 'class="adv n"' in t) for t in tips), '표시의 빛깔 구분(adv y · adv n)은 그대로')
    m = pg.evaluate('''(tip) => { showHome(); var row = document.querySelector('#sheet .todo'), sm = row.querySelector('small') || row.querySelector('.mid').appendChild(document.createElement('small'));
      sm.innerHTML = '소패 수비 16,687 → 출진 · ' + tip; var a = sm.querySelector('.adv'), cs = getComputedStyle(a), ra = a.getBoundingClientRect(), rs = sm.getBoundingClientRect(), n = row.querySelector(':scope > .n'), cn = getComputedStyle(n), rn = n.getBoundingClientRect();
      return { disp: cs.display, radius: cs.borderTopLeftRadius, bw: cs.borderTopWidth, h: ra.height, w: ra.width, sameLine: ra.top >= rs.top - 1 && ra.bottom <= rs.bottom + 1, smH: rs.height, rowH: row.offsetHeight, fs: cs.fontSize, color: cs.color,
        badge: [Math.round(rn.width), Math.round(rn.height), cn.borderTopLeftRadius, cn.display], text: sm.textContent }; }''', tips[0])
    print('  줄 속의 표시:', m); B.shot(pg, 'a1_todo', 200)
    ok(m['disp'] == 'inline' and m['radius'] == '0px' and m['bw'] == '0px' and m['h'] <= 20 and m['sameLine'], "풀이 글 속의 표시는 글과 같은 줄의 글자다(둥근 배지가 아니다) — 높이 %.0f · %s" % (m['h'], m['disp']))
    ok(m['smH'] <= 20 and m['rowH'] <= 60, "'지금 할 일'은 여전히 줄마다 한 줄(풀이 %.0f · 줄 %d)" % (m['smH'], m['rowH']))
    ok(m['badge'][0] == 30 and m['badge'][1] == 30 and m['badge'][2] == '50%' and m['badge'][3] == 'flex', '왼쪽의 둥근 숫자 배지는 그대로(30 × 30) %s' % m['badge'])
    pg.evaluate('() => { refreshSheet(); }')

    # ---------- ① 수송 창: 짐을 내린 뒤 ----------
    pg.evaluate('() => { selectBase(G.bases[T.a]); flowTransport(G.bases[T.a]); }'); pg.wait_for_timeout(400)
    seg = pg.evaluate('''() => Array.prototype.map.call(document.querySelectorAll('#modal .seg.tbk button'), function (e) { return [e.textContent, e.classList.contains('on'), e.scrollWidth <= e.clientWidth + 1, Math.round(e.getBoundingClientRect().height)]; })''')
    print('  수송 창:', seg); B.shot(pg, 'b1_trans', 200)
    ok(len(seg) == 2 and seg[0][0] == '그곳에 머문다' and seg[0][1] and seg[1][0] == T['an'] + ('으로' if pg.evaluate('euro(T.an)').endswith('으로') else '로') + ' 돌아온다' and not seg[1][1] and seg[0][2] and seg[1][2], "수송 창에 '짐을 내린 뒤' 두 갈래 — 처음은 머문다 %s" % [s[0] for s in seg])
    ok(all(s[3] >= 36 for s in seg), '두 단추의 높이 %s (누를 만하다)' % [s[3] for s in seg])
    pg.evaluate('() => { var e = $("tr_gold"); e.value = 300; e.dispatchEvent(new Event("input", { bubbles: true })); }'); pg.wait_for_timeout(150)
    tapsel(pg, '#modal .seg.tbk button', 1)
    s2 = pg.evaluate('''() => ({ on: Array.prototype.map.call(document.querySelectorAll('#modal .seg.tbk button'), function (e) { return e.classList.contains('on'); }), ui: UI.tback, opt: JSON.parse(localStorage.getItem('chunhado_opts') || '{}').tback,
      note: document.querySelector('#modal .dlg-b .note').textContent, gold: +$('tr_gold').value, goldTx: $('tv_gold').textContent })''')
    ok(s2['on'] == [False, True] and s2['ui'] is True and s2['opt'] is True and '돌아온다' in s2['note'], '돌아온다를 누르면 켜지고, 고른 것을 기억한다(다음 수송 창에도 그대로) · 풀이가 붙는다')
    ok(s2['gold'] == 300 and s2['goldTx'] == '300', '갈래를 바꿔도 실을 것으로 고른 값은 그대로(금 %s)' % s2['goldTx'])
    b0 = pg.evaluate('() => { var b = G.bases[T.b]; return [b.troops, b.gold]; }')
    tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(700)
    u1 = pg.evaluate('''() => { var u = selUnit(); window.U1 = u ? u.id : -1; return u ? { type: u.type, back: u.back === true, home: u.home, lead: uLeader(u).n, oid: u.off[0], talk: ($('talk') ? $('talk').textContent : '') } : null; }''')
    print('  낸 수송대:', u1)
    ok(u1 and u1['type'] == 'trans' and u1['back'] and u1['home'] == T['a'] and '돌아옵니다' in u1['talk'], '돌아온다로 낸 수송대 — back 이 붙고, 출발의 한마디에 돌아온다는 말')

    # ---------- 부대 창: [짐 내린 뒤] · [귀환] ----------
    acts = pg.evaluate(SHEET); print('  부대 창:', [(a['a'], a['b'], a['s']) for a in acts]); B.shot(pg, 'b2_unit', 200)
    tb = [a for a in acts if a['a'] == 'tback']; gh = [a for a in acts if a['a'] == 'gohome']
    ok(len(tb) == 1 and tb[0]['b'] == '짐 내린 뒤' and tb[0]['s'].endswith('돌아옴') and T['an'] in tb[0]['s'] and tb[0]['on'], '부대 창의 [짐 내린 뒤] — %s' % (tb[0]['s'] if tb else ''))
    ok(len(gh) == 0, '막 나온 수송대(떠나온 거점의 바로 옆)에는 [귀환]을 내지 않는다')
    ok(all(a['fit'] for a in acts), '단추의 글이 넘치지 않는다')
    tapsel(pg, '#sheet [data-a=tback]'); t1 = toast(pg); a1 = [a for a in pg.evaluate(SHEET) if a['a'] == 'tback'][0]; bk1 = pg.evaluate('UMAP[U1].back')
    tapsel(pg, '#sheet [data-a=tback]'); t2 = toast(pg); a2 = [a for a in pg.evaluate(SHEET) if a['a'] == 'tback'][0]; bk2 = pg.evaluate('UMAP[U1].back')
    ok(bk1 is None and a1['s'] == '그곳에 머묾' and not a1['on'] and '머뭅니다' in t1, '누르면 머문다로 — %s / %s' % (a1['s'], t1))
    ok(bk2 is True and a2['on'] and '돌아옵니다' in t2 and u1['lead'] in t2, '다시 누르면 돌아온다로 — %s' % t2)
    ok(pg.evaluate('UI.tback') is True, '부대 창에서 바꾼 것은 수송 창의 기억을 바꾸지 않는다')

    # ---------- 거점에 짐을 내린다 ----------
    d = pg.evaluate(DOOR, [pg.evaluate('U1'), T['b']])
    pg.evaluate('''() => { var u = UMAP[U1], b = G.bases[T.b], p = hexCenter(b.c, b.r); cam.x = p[0]; cam.y = p[1]; cam.z = 1.5; clampCam(); syncScene(); selectUnit(u); requestDraw(); }'''); pg.wait_for_timeout(500)
    gh = [a for a in pg.evaluate(SHEET) if a['a'] == 'gohome']
    ok(len(gh) == 1 and gh[0]['b'] == '귀환' and T['an'] in gh[0]['s'] and gh[0]['fit'], '멀리 나간 수송대의 창에는 [귀환] — %s' % (gh[0]['s'] if gh else ''))
    bb = pg.evaluate('() => { var b = G.bases[T.b]; return [b.c, b.r]; }')
    taphex(pg, bb[0], bb[1]); pg.wait_for_timeout(300)
    if pg.evaluate('!!document.querySelector("#sheet [data-a=marchhere]")'): tapsel(pg, '#sheet [data-a=marchhere]')
    pg.wait_for_function('!UMAP[U1]', timeout=15000); pg.wait_for_timeout(1200)
    e1 = pg.evaluate('''(oid) => { var o = off(oid), b = G.bases[T.b]; return { st: o.st, dest: o.dest, eta: o.eta, loc: o.loc, toast: $('toast').textContent, troops: b.troops, gold: b.gold, sheet: (document.querySelector('#sheet .bn') || document.querySelector('#sheet h2') || $('sheet')).textContent.slice(0, 40),
      state: (typeof offWhere === 'function' ? offWhere(o) : ''), inList: baseOfficers(b).some(function (x) { return x.id === oid; }), log: G.log.slice(-3).map(function (x) { return x.t; }).join(' | ') }; }''', u1['oid'])
    print('  짐을 내린 뒤:', e1); B.shot(pg, 'b3_enter', 200)
    ok(e1['st'] == 'travel' and e1['dest'] == T['a'] and e1['eta'] == T['tt'] and e1['loc'] == T['b'] and not e1['inList'], '거점에 들어가면 무장은 떠나온 곳으로 길을 떠난다(%d턴)' % e1['eta'])
    ok(e1['troops'] == b0[0] + 1000 and e1['gold'] == b0[1] + 300, '실은 것은 그 거점에 합쳐진다(병력 +1,000 · 금 +300)')
    ok(T['bn'] + '에 짐을 내림' in e1['toast'] and '돌아갑니다' in e1['toast'] and ('%d일' % (T['tt'] * 10)) in e1['toast'] and T['an'] in e1['toast'], '알림: %s' % e1['toast'])
    row = pg.evaluate('(oid) => offStatus(off(oid))', u1['oid'])
    ok(row == '이동 중 (%d일)' % (T['tt'] * 10), '무장의 상태 글: %s' % row)
    # 날이 차면 떠나온 거점에서 쉰다
    arr = pg.evaluate('''(oid) => { var o = off(oid), n = 0; while (o.st === 'travel' && n < 9) { phaseStart(G.player); n++; } return [n, o.st, o.loc, o.acted]; }''', u1['oid'])
    ok(arr[0] == T['tt'] and arr[1] == 'active' and arr[2] == T['a'] and arr[3] is False, '%d턴 뒤 %s에 닿아 쉰다 %s' % (T['tt'], T['an'], arr))

    # ---------- 부대에 보급한 수송대는 떠나온 거점으로 행군 ----------
    pg.evaluate('() => { G.factions[G.player].ap = 250; selectBase(G.bases[T.a]); flowTransport(G.bases[T.a]); }'); pg.wait_for_timeout(400)
    ok(pg.evaluate('''Array.prototype.map.call(document.querySelectorAll('#modal .seg.tbk button'), function (e) { return e.classList.contains('on'); })''') == [False, True], '다음 수송 창은 지난번에 고른 대로(돌아온다) 열린다')
    tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(700)
    pg.evaluate('''() => { var t = selUnit(); window.U2 = t.id; talkHide(); var A = G.bases[T.a], o = idleOfficers(A).filter(function (x) { return !isLord(x); })[0];
      var s = cmdDeploy(A, { type: 'spear', ids: [o.id], troops: 3000, food: 2000 }).unit; window.U3 = s.id; }''')
    pg.evaluate(DOOR, [pg.evaluate('U2'), T['b']])
    pg.evaluate('''() => { var t = UMAP[U2], s = UMAP[U3], ns = nbrs(t.c, t.r);
      for (var i = 0; i < ns.length; i++) { var c = ns[i][0], r = ns[i][1]; if (inMap(c, r) && !UAT[K(c, r)] && BAT[K(c, r)] === undefined && moveCost(s, c, r) < 99) { placeUnit(s, c, r); break; } }
      s.born = -9; s.done = false; var p = hexCenter(t.c, t.r); cam.x = p[0]; cam.y = p[1]; clampCam(); syncScene(); selectUnit(t); requestDraw(); }'''); pg.wait_for_timeout(500)
    sa = pg.evaluate(SHEET); sup = [a for a in sa if a['a'] == 'supply']
    ok(len(sup) == 1 and not sup[0]['off'], '수송대가 아군 부대 옆에 서면 [보급]이 켜진다')
    tapsel(pg, '#sheet [data-a=supply]'); pg.wait_for_timeout(400); tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(700)
    s3 = pg.evaluate('''() => { var t = UMAP[U2], A = G.bases[T.a]; return { dest: t.dest === K(A.c, A.r), done: t.done, talk: $('talk') ? $('talk').textContent : '', note: (document.querySelector('#sheet .note') || {}).textContent || '', sel: selUnit() ? selUnit().id : -1 }; }''')
    pg.evaluate('() => { talkHide(); selectUnit(UMAP[U2]); }'); pg.wait_for_timeout(300)
    sb = pg.evaluate(SHEET); note = pg.evaluate('''Array.prototype.map.call(document.querySelectorAll('#sheet .note'), function (e) { return e.textContent; }).join(' / ')''')
    print('  보급한 뒤:', s3, [(a['a'], a['s']) for a in sb], note); B.shot(pg, 'b4_supply', 200)
    ok(s3['dest'] and s3['done'] and '돌아갑니다' in s3['talk'] and T['an'] in s3['talk'], '보급을 마치면 떠나온 거점으로 행군 명령이 선다 — %s' % s3['talk'][-40:])
    ok(('방면 행군 중' in note) and [a['a'] for a in sb] == ['tback'], "행동을 마친 수송대의 창: '행군 중' + [짐 내린 뒤]만 %s" % [a['a'] for a in sb])
    # 다음 턴: [행군 취소]로 물릴 수 있고, [귀환]은 이미 가는 길이라 없다
    pg.evaluate('() => { var t = UMAP[U2]; t.done = false; t.mp = uMaxMp(t); selectUnit(t); }'); pg.wait_for_timeout(300)
    sc = pg.evaluate(SHEET)
    ok(any(a['a'] == 'unmarch' for a in sc) and not any(a['a'] == 'gohome' for a in sc), '다음 턴의 창: [행군 취소]가 있고, 이미 돌아가는 길이라 [귀환]은 없다 %s' % [a['a'] for a in sc])
    tapsel(pg, '#sheet [data-a=unmarch]'); pg.wait_for_timeout(300)
    sd = pg.evaluate(SHEET)
    ok(pg.evaluate('UMAP[U2].dest') == -1 and any(a['a'] == 'gohome' for a in sd), '[행군 취소]를 누르면 멈추고 [귀환]이 다시 나온다')
    # [귀환]: 지금 떠나온 거점으로 행군
    d0 = pg.evaluate('() => { var t = UMAP[U2], A = G.bases[T.a]; return hdist(t.c, t.r, A.c, A.r); }')
    tapsel(pg, '#sheet [data-a=gohome]'); pg.wait_for_timeout(2500)
    g = pg.evaluate('''() => { var t = UMAP[U2], A = G.bases[T.a]; return t ? { dest: t.dest === K(A.c, A.r), d: hdist(t.c, t.r, A.c, A.r), toast: $('toast').textContent } : { gone: true, toast: $('toast').textContent }; }''')
    print('  귀환:', d0, g)
    ok(g.get('gone') or (g['dest'] and g['d'] < d0 and T['an'] in g['toast'] and '행군' in g['toast']), '[귀환] — %s 방면으로 행군을 시작한다(%s칸 → %s칸)' % (T['an'], d0, g.get('d')))

    # ---------- 머문다로 낸 수송대는 전과 같다 ----------
    pg.evaluate('() => { G.factions[G.player].ap = 250; clearSel(); selectBase(G.bases[T.a]); flowTransport(G.bases[T.a]); }'); pg.wait_for_timeout(400)
    tapsel(pg, '#modal .seg.tbk button', 0); tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(700)
    u4 = pg.evaluate('''() => { var u = selUnit(); window.U4 = u.id; talkHide(); return { back: u.back === undefined, oid: u.off[0], ui: UI.tback, tb: Array.prototype.map.call(document.querySelectorAll('#sheet [data-a=tback] small'), function (e) { return e.textContent; }) }; }''')
    ok(u4['back'] and u4['ui'] is False and u4['tb'] == ['그곳에 머묾'], '머문다로 내면 back 이 없다 · 기억도 머문다로')
    pg.evaluate(DOOR, [pg.evaluate('U4'), T['b']])
    r4 = pg.evaluate('''(oid) => { var u = UMAP[U4], b = G.bases[T.b], res = unitMove(u, b.c, b.r), o = off(oid); syncScene(); clearSel(); return { entered: res.entered === b.id, back: res.back === undefined, st: o.st, loc: o.loc }; }''', u4['oid'])
    ok(r4['entered'] and r4['back'] and r4['st'] == 'active' and r4['loc'] == T['b'], '머문다: 들어간 거점에 머문다(전과 같다) %s' % r4)

    # 도움말
    pg.evaluate('showHelp()'); pg.wait_for_timeout(250)
    hp = pg.evaluate('document.querySelector("#modal .dlg").textContent'); pg.evaluate('closeDialog()')
    ok('짐을 내린 뒤' in hp and '귀환' in hp, '도움말에 짐을 내린 뒤 · 귀환')
B.run(steps, 390, 844, 2)
errs = [e for e in B.errors if 'GPU stall' not in e and 'GL Driver' not in e and 'ERR_FILE_NOT_FOUND' not in e and 'willReadFrequently' not in e]
print('console errors:', errs[:6])
print('FAILS %d' % len(fails), fails)
sys.exit(1 if fails or errs else 0)
