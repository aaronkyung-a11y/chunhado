# v0.20 — 화면 조작으로 확인(15가지 요청 가운데 화면에 드러나는 것들. 출진의 두 단계 · 지도에서 나갈 자리는 d23, 수송은 d32, 부장의 조언은 d31 · d16 이 본다)
#   ① 아래 줄: 좁은 화면에서도 '턴 종료'가 잘리지 않는다(320 ~ 412px · '다음 부대 N'이 떴을 때 · 글씨가 큰 기기)   ② 아래에 더 있을 때의 큰 화살표   ③ 붓으로 두른 틀
#   ④ 성 이름표의 내구 막대   ⑤ 짓는 중인 시설   ⑥ 세력이 망하는 장면의 그림   ⑦ 이동: 지도에서 보낼 성 고르기 · 이동 중인 무장의 가는 곳   ⑧ 등용: 정렬
#   ⑨ 일기토 화면의 합별 기록   ⑩ 화살 · 불의 그림   ⑪ 홍농 · 물빛
#   python3 tests/d34.py          찍은 그림은 tests/shots36/
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import taphex, tapsel
import d2
B.SHOTS = os.path.join(B.ROOT, 'shots36')
os.makedirs(B.SHOTS, exist_ok=True)
fails = []
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)
BAR = '''() => { var b = $('bar'), r = b.getBoundingClientRect(), bs = [].filter.call(b.querySelectorAll('button'), function (x) { return x.style.display !== 'none'; });
  return { w: innerWidth, cls: b.className, end: Math.round($('btnEnd').getBoundingClientRect().right), endL: Math.round($('btnEnd').getBoundingClientRect().left), bar: Math.round(r.right),
    over: bs.filter(function (x) { return x.scrollWidth > x.clientWidth + 1; }).map(function (x) { return x.textContent; }), lap: bs.some(function (x, i) { return i && x.getBoundingClientRect().left < bs[i - 1].getBoundingClientRect().right - 0.5; }),
    txt: bs.map(function (x) { return x.textContent; }), h: bs.map(function (x) { return Math.round(x.getBoundingClientRect().height); }), wp: [].map.call(document.querySelectorAll('#sheet .wp span'), function (s) { return Math.round(s.getBoundingClientRect().height); }) }; }'''
def steps(pg):
    B.start(pg, 0)
    ok(pg.evaluate('GAME_VERSION') == B.VER, '판 번호 ' + B.VER)
    pg.evaluate('''() => { G.aiOnly = false; talkHide(); var A = facCities(G.player)[0]; window.T = { a: A.id }; G.factions[G.player].ap = 250;
      for (var i = 0; i < 2; i++) { var ids = autoTeam(A, 'spear', 2000); cmdDeploy(A, { type: 'spear', ids: ids.slice(0, 1), troops: 2000, food: 2000 }); }
      syncScene(); selectBase(A); refreshHud(); }'''); pg.wait_for_timeout(500)
    # ---------- ① 아래 줄 ----------
    print('① 아래 줄')
    for w in (412, 390, 360, 344, 320):
        pg.set_viewport_size({'width': w, 'height': 780}); pg.wait_for_timeout(350)
        b = pg.evaluate(BAR)
        ok(b['end'] <= w - 4 and not b['over'] and not b['lap'] and '턴 종료' in b['txt'] and any(t.startswith('다음') and t.endswith('2') for t in b['txt']) and min(b['h']) >= 40, "%dpx: '턴 종료'의 오른쪽 끝 %d ≤ %d · 넘치는 단추 %s · 겹침 %s [%s] %s" % (w, b['end'], w - 4, b['over'], b['lap'], b['cls'], b['txt']))
        if w in (360, 320): ok(len(b['wp']) >= 4 and max(b['wp']) <= 24, '%dpx: 무기 줄(창 · 극 · 노 · 군마)의 글이 세로로 꺾이지 않는다 %s' % (w, b['wp']))
        if w == 360: B.shot(pg, 'a1_bar360', 100)
    b0 = pg.evaluate(BAR)
    pg.evaluate('''() => { var st = document.createElement('style'); st.id = 'bigfont'; st.textContent = '#bar button { font-size: 19px !important; } #bar.t1 button { font-size: 15px !important; } #bar.t3 button { font-size: 12px !important; }'; document.head.appendChild(st); refreshHud(); }'''); pg.wait_for_timeout(250)
    b1 = pg.evaluate(BAR); B.shot(pg, 'a2_bar_big', 100)
    ok(b0['cls'] == '' and 't1' in b1['cls'] and b1['end'] <= 320 - 4 and not b1['over'], "글씨가 큰 기기(320px · 19px): 넘치면 한 단계씩 줄인다 — [%s] · '턴 종료' 끝 %d · 넘침 %s" % (b1['cls'], b1['end'], b1['over']))
    pg.evaluate('() => { $("bigfont").remove(); refreshHud(); }'); pg.set_viewport_size({'width': 360, 'height': 780}); pg.wait_for_timeout(350)
    ok(pg.evaluate(BAR)['cls'] == '', '되돌리면 줄였던 것도 풀린다')
    # ---------- ② 아래에 더 있을 때 ----------
    print('② 큰 화살표')
    pg.evaluate('showHelp()'); pg.wait_for_timeout(1000)
    mh = pg.evaluate('''() => { var h = document.querySelector('#modal .dlg-b > .morehint'), i = h.querySelector('i'), r = i.getBoundingClientRect(), cs = getComputedStyle(i), b = document.querySelector('#modal .dlg-b').getBoundingClientRect();
      return { on: h.classList.contains('on'), w: Math.round(r.width), h: Math.round(r.height), fs: cs.fontSize, round: cs.borderRadius, mid: Math.round(r.left + r.width / 2 - b.left - b.width / 2), arrow: getComputedStyle(i, '::before').borderBottomWidth, top0: document.querySelector('#modal .dlg-b').scrollTop }; }''')
    ok(mh['on'] and mh['w'] >= 44 and mh['h'] >= 44 and mh['fs'] == '0px' and mh['round'] == '50%' and abs(mh['mid']) <= 2 and mh['arrow'] == '4px', '글 대신 둥근 큰 화살표(%d × %d · 가운데 · 글씨는 숨김) %s' % (mh['w'], mh['h'], mh))
    B.shot(pg, 'b1_more', 100)
    cb = pg.evaluate('(() => { var r = document.querySelector("#modal .morehint i").getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; })()')
    pg.touchscreen.tap(cb[0], cb[1]); pg.wait_for_timeout(900)
    ok(pg.evaluate('document.querySelector("#modal .dlg-b").scrollTop') > 200, '화살표를 누르면 한 화면쯤 내려간다')
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(200)
    # ---------- ③ 붓으로 두른 틀 ----------
    print('③ 붓 테두리')
    br = pg.evaluate('''() => { var c = document.querySelector('#sheet .cmd'), a = getComputedStyle(c, '::after'), cs = getComputedStyle(c), f = document.getElementById('inkEdge');
      return { filt: a.filter, bw: [a.borderTopWidth, a.borderRightWidth, a.borderBottomWidth, a.borderLeftWidth], rad: cs.borderTopLeftRadius + '/' + cs.borderTopRightRadius, own: cs.borderTopColor, fe: f ? [].map.call(f.children, function (x) { return x.tagName; }) : null,
        sheet: getComputedStyle($('sheet'), '::before').backgroundImage.slice(0, 26), hud: getComputedStyle($('hud'), '::after').backgroundImage.slice(0, 26), bar: getComputedStyle($('btnEnd'), '::after').borderTopColor, st: getComputedStyle($('sheet')).borderTopColor }; }''')
    print('     ', br)
    ok(br['fe'] and 'feTurbulence' in br['fe'] and 'feDisplacementMap' in br['fe'] and 'inkEdge' in br['filt'], '단추의 테두리는 붓 거름(#inkEdge)을 거친 가짜 요소가 그린다')
    ok(len(set(br['bw'])) >= 2 and br['rad'] != '2px/2px' and br['rad'].split('/')[0] != br['rad'].split('/')[1] and 'rgba(0, 0, 0, 0)' in br['own'], '선의 굵기가 변마다 다르고(%s) 모서리가 고르지 않다(%s) — 곧은 테두리는 지웠다' % (br['bw'], br['rad']))
    ok('svg' in br['sheet'] and 'svg' in br['hud'] and 'rgba(0, 0, 0, 0)' in br['st'], '판의 경계(위 정보줄 · 아래 판)는 붓 한 획 그림')
    # ---------- ④ 내구 막대 ----------
    print('④ 내구 막대')
    DUR = '''(v) => { var b = G.bases[T.a]; b.dur = Math.round(b.maxDur * v); clearSel(); UI.dirty = true; syncScene(); var L = R3.bases[b.id].lab, x = L.cv.getContext('2d'), h = L.cv.height, w = L.cv.width;
      var d = x.getImageData(0, h - 11, w, 1).data, n = { w: w, light: 0, yellow: 0, red: 0, dark: 0, sig: R3.bases[b.id].sig };      // 막대의 한가운데 줄을 훑는다
      for (var i = 0; i < d.length; i += 4) { var r = d[i], g = d[i + 1], bl = d[i + 2]; if (d[i + 3] < 100) continue; if (r > 215 && g > 210 && bl > 190) n.light++; else if (r > 200 && g > 150 && g < 215 && bl < 120) n.yellow++; else if (r > 190 && g < 130 && bl < 120) n.red++; else if (r < 70 && g < 70 && bl < 70) n.dark++; }
      return n; }'''
    d1 = pg.evaluate(DUR, 1); d2_ = pg.evaluate(DUR, 0.45); d3 = pg.evaluate(DUR, 0.2)
    print('     ', d1, d2_, d3)
    ok(d1['light'] >= d1['w'] * 0.5 and d1['yellow'] == 0 and d1['red'] == 0 and d1['dark'] <= 6, '내구가 가득하면 막대가 끝까지 종이 빛(이름표 너비 %d 가운데 %d)' % (d1['w'], d1['light']))
    ok(0.4 * d1['light'] * 0.8 <= d2_['yellow'] <= 0.5 * d1['light'] * 1.15 and d2_['dark'] >= d1['light'] * 0.4 and d2_['red'] == 0 and d2_['sig'] != d1['sig'], '45%%: 누런 막대가 절반 못 미치게(%d), 나머지는 먹빛 홈(%d)' % (d2_['yellow'], d2_['dark']))
    ok(0.12 * d1['light'] <= d3['red'] <= 0.28 * d1['light'] and d3['yellow'] == 0 and d3['dark'] >= d1['light'] * 0.6, '20%%: 붉은 막대(%d), 나머지는 홈(%d)' % (d3['red'], d3['dark']))
    pg.evaluate(DUR, 1)
    # ---------- ⑤ 짓는 중인 시설 ----------
    print('⑤ 짓는 중인 시설')
    site = pg.evaluate('''() => { var A = G.bases[T.a]; A.gold = 30000; G.factions[G.player].ap = 250; var os = idleOfficers(A).filter(function (o) { return !isLord(o); }), pi = -1;
      for (var i = 0; i < A.plots.length; i++) if (!A.plots[i].fac && !UAT[K(A.plots[i].c, A.plots[i].r)]) { pi = i; break; }
      var r = cmdDevelop(A, pi, 'farm', [os[0].id]); syncScene(); var fo = R3.facs[A.id + ':' + pi], fc = A.plots[pi].fac; window.T.pi = pi; selectBase(A); flowFacility(A, pi);
      var cvs = TEX[siteTexKey('farm', 0)].image, x = cvs.getContext('2d'), d = x.getImageData(0, 0, cvs.width, cvs.height).data, n = 0, dk = 0;
      for (var k = 0; k < d.length; k += 4) if (d[k + 3] > 60) { n++; if (d[k] < 150) dk++; }
      return { ok: r.ok, sig: fo.sig, key: siteTexKey(fc.t, siteStage(fc)), ink: SITE_INK, al: SITE_A, share: Math.round(dk / n * 100) }; }''')
    pg.wait_for_timeout(900); B.shot(pg, 'e1_site', 200)
    site.update(pg.evaluate('''() => { var A = G.bases[T.a], fo = R3.facs[A.id + ':' + T.pi]; return { op: fo.sp.material.opacity, vis: fo.sp.visible, spot: !!(SPOT.on && SPOT.v && SPOT.v.fi === T.pi), left: (SPOT.v.facs.filter(function (f) { return f.i === T.pi; })[0] || {}).left }; }'''))
    print('     ', site)
    ok(site['vis'] and '일' in (site['left'] or '') and site['ok'] and site['key'] == 'farm@0' and site['op'] >= 0.99 and site['spot'] and site['ink'][0] >= 0.6 and site['al'][0] >= 0.95 and site['share'] >= 12, '짓는 중인 농장: 비계 그림이 불투명하게 · 먹이 짙다(짙은 점 %d%% · 먹 %s)' % (site['share'], site['ink']))
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(200)
    # ---------- ⑥ 세력이 망하는 장면 ----------
    print('⑥ 멸망 장면의 그림')
    cp = pg.evaluate('''() => { setCaption(-1, '<b>' + facName(1) + '군 멸망</b>', 'big', 1); var p = $('plPor'), a = { img: p.style.backgroundImage.indexOf('url(') === 0, gone: p.classList.contains('gone'), lord: off(G.factions[1].lord).por, same: p.style.backgroundImage.indexOf(POR_URL[off(G.factions[1].lord).por]) >= 0, msg: $('plMsg').textContent };
      setCaption(-1, '<b>소식</b>'); a.plain = [$('plPor').style.backgroundImage, $('plPor').classList.contains('gone')]; setCaption(0, 'x'); a.mine = [$('plPor').style.backgroundImage.indexOf('url(') === 0, $('plPor').classList.contains('gone')]; return a; }''')
    ok(cp['img'] and cp['gone'] and cp['same'] and '멸망' in cp['msg'] and cp['plain'] == ['', False] and cp['mine'] == [True, False], '망한 세력의 군주 초상이 뜬다(잿빛 표시) — 다른 자막은 전과 같다 %s' % cp)
    src = pg.evaluate('(typeof playStep === "function" ? playStep : (typeof playEvent === "function" ? playEvent : setCaption)).toString().length > 0') and pg.evaluate('''() => /e\\.t === 'fallen'[\\s\\S]{0,80}setCaption\\(-1, [^;]*, 'big', e\\.f\\)/.test(document.documentElement.innerHTML)''')
    ok(src, '재생의 멸망 장면이 그 세력을 넘겨 준다(setCaption(…, e.f))')
    # ---------- ⑦ 이동 ----------
    print('⑦ 이동: 지도에서')
    mv = pg.evaluate('''() => { var A = G.bases[T.a], n1 = G.bases[baseByName('허창')], n2 = G.bases[baseByName('낙양')]; [n1, n2].forEach(function (b) { G.officers.forEach(function (o) { if (o.loc === b.id && o.f === b.owner && o.unit === null && o.st === 'active') { o.f = -1; o.st = 'free'; } }); b.owner = G.player; b.troops = 3000; });
      reindex(); clearSel(); syncScene(); selectBase(A); flowMove(A); return [n1.id, n2.id, [n1.c, n1.r], [n2.c, n2.r]]; }'''); pg.wait_for_timeout(500)
    tapsel(pg, '#modal [data-a=pick]', 1); tapsel(pg, '#modal .dlg-f .btn.pri'); pg.wait_for_timeout(900)
    m0 = pg.evaluate('''() => ({ head: document.querySelector('#modal .dlg-h').textContent, see: $('modal').classList.contains('see'), picking: $('app').classList.contains('picking'), mk: [].map.call(document.querySelectorAll('#fx .mk.ex'), function (e) { var r = e.getBoundingClientRect(); return [e.className.replace('mk ex', '').trim(), e.querySelector('b').textContent, e.querySelector('small').textContent, r.top > 50 && r.bottom < document.querySelector('#modal .dlg').getBoundingClientRect().top && r.left >= 0 && r.right <= innerWidth]; }),
      rows: [].map.call(document.querySelectorAll('#modal .row[data-a=d] .nm'), function (e) { return e.textContent; }), go: !!document.querySelector('#modal [data-a=go]'), list: MODAL.pick.list().length })''')
    print('     ', m0); B.shot(pg, 'g1_move', 200)
    ok('어디로' in m0['head'] and m0['see'] and m0['picking'] and len(m0['mk']) == 3 and m0['mk'][0][0] == 'src' and sorted(x[1] for x in m0['mk'][1:]) == ['낙양', '허창'] and all(re.match(r'^\d+일$', x[2]) for x in m0['mk'][1:]) and all(x[3] for x in m0['mk']) and not m0['go'], '보낼 곳 창: 지도에 우리 성마다 이름과 날수 — 모두 창 위에 보인다 %s' % m0['mk'])
    x, y = B.hexpos(pg, mv[2][0], mv[2][1]); pg.touchscreen.tap(x, y - 6); pg.wait_for_timeout(500)
    m1 = pg.evaluate('''() => ({ sel: [].map.call(document.querySelectorAll('#modal .row.sel .nm'), function (e) { return e.textContent; }), go: (document.querySelector('#modal [data-a=go]') || {}).textContent || '', on: [].map.call(document.querySelectorAll('#fx .mk.ex.on b'), function (e) { return e.textContent; }), modal: !!MODAL })''')
    ok(m1['sel'] == ['허창'] and m1['on'] == ['허창'] and '허창' in m1['go'] and '보낸다' in m1['go'] and m1['modal'], '지도에서 허창을 누르면 고를 뿐이다 — 목록의 줄과 딱지가 붉어지고 [%s]가 뜬다' % m1['go'])
    emp = pg.evaluate('''() => { var top = $('hud').getBoundingClientRect().bottom + 30, bot = document.querySelector('#modal .dlg').getBoundingClientRect().top - 20, rc = cv.getBoundingClientRect(), g = pickGround(rc.width * 0.5, (top + bot) / 2 - rc.top), h = worldToHex(g[0], g[1]);
      for (var d = 0; d < 12; d++) { var c = h[0] + d, r = h[1]; if (!baseAt(c, r) && !UAT[K(c, r)] && !plotAt(c, r)) { var p = hexPos(c, r), s = w2s(p[0], p[1], p[2]); if (s[1] + rc.top > top && s[1] + rc.top < bot && s[0] > 10 && s[0] < rc.width - 10) return [s[0] + rc.left, s[1] + rc.top, c, r]; } } return null; }''')
    pg.evaluate('$("toast").textContent = ""'); pg.touchscreen.tap(emp[0], emp[1]); pg.wait_for_timeout(400)
    ok('우리 성을 누르세요' in pg.evaluate('$("toast").textContent') and pg.evaluate('!!MODAL') and pg.evaluate('''[].map.call(document.querySelectorAll('#modal .row.sel .nm'), function (e) { return e.textContent; })''') == ['허창'], '빈 땅(%d,%d)을 누르면 알릴 뿐 창과 고른 성은 그대로 — %s' % (emp[2], emp[3], pg.evaluate('$("toast").textContent')))
    B.shot(pg, 'g2_move_sel', 100)
    tapsel(pg, '#modal [data-a=go]'); pg.wait_for_timeout(700)
    m2 = pg.evaluate('''([id]) => { var os = G.officers.filter(function (o) { return o.st === 'travel' && o.dest === id; }); return { n: os.length, st: os.map(function (o) { return offStatus(o); }), modal: !!MODAL, marks: document.querySelectorAll('#fx .mk').length, picking: $('app').classList.contains('picking'), talk: $('talk') ? $('talk').textContent : '' }; }''', [mv[0]])
    ok(m2['n'] == 1 and re.match(r'^허창으로 이동 중 \(\d+일\)$', m2['st'][0]) and not m2['modal'] and m2['marks'] == 0 and not m2['picking'] and '허창으로' in m2['talk'], '[보낸다] → 떠난다 · 상태 글에 가는 곳(%s) · 딱지는 걷힌다' % m2['st'])
    pg.evaluate('talkHide()')
    # ---------- ⑧ 등용 정렬 ----------
    print('⑧ 등용: 정렬')
    pg.evaluate('() => { clearSel(); var A = G.bases[T.a]; selectBase(A); flowRecruit(A); }'); pg.wait_for_timeout(500)
    ROWS = '''() => ({ srt: [].map.call(document.querySelectorAll('#modal .srt button'), function (b) { return [b.getAttribute('data-v'), b.textContent, b.classList.contains('on')]; }),
      secs: [].map.call(document.querySelectorAll('#modal .rows'), function (rs) { return [].map.call(rs.querySelectorAll('.row'), function (r) { var o = off(+r.getAttribute('data-v')); return { n: o.n, war: o.war, sum: o.ldr + o.war + o.int + o.pol + o.cha, a0: APT_RANK[o.apt.charAt(0)], hi: (r.querySelector('.st5 b.hi') || {}).textContent || '', ap: [].findIndex.call(r.querySelectorAll('.ap5 span'), function (s) { return s.classList.contains('on'); }) }; }); }) })'''
    r0 = pg.evaluate(ROWS)
    ok([s[0] for s in r0['srt']] == ['p', 'sum', 'ldr', 'war', 'int', 'pol', 'cha', 'a0', 'a1', 'a2', 'a3', 'a4'] and [s[2] for s in r0['srt']].count(True) == 1 and r0['srt'][0][2] and sum(len(s) for s in r0['secs']) >= 4, '정렬 줄: 가능성 · 능력 · 통솔 · 무력 · 지력 · 정치 · 매력 · 창 · 극 · 노 · 기 · 병기 (처음은 가능성) — 대상 %d명' % sum(len(s) for s in r0['secs']))
    desc = lambda xs: all(xs[i] >= xs[i + 1] for i in range(len(xs) - 1))
    tapsel(pg, '#modal [data-a=srt][data-v=war]'); r1 = pg.evaluate(ROWS)
    ok(all(desc([o['war'] for o in s]) for s in r1['secs']) and all(o['hi'] == str(o['war']) for s in r1['secs'] for o in s) and [s[0] for s in r1['srt'] if s[2]] == ['war'], '[무력]: 묶음마다 무력이 높은 순 · 그 능력치가 짙게 %s' % [o['n'] + str(o['war']) for o in r1['secs'][-1][:4]])
    tapsel(pg, '#modal [data-a=srt][data-v=sum]'); r2 = pg.evaluate(ROWS)
    ok(all(desc([o['sum'] for o in s]) for s in r2['secs']) and all(o['hi'] == '' for s in r2['secs'] for o in s), '[능력]: 다섯 능력치의 합이 높은 순')
    tapsel(pg, '#modal [data-a=srt][data-v=a0]'); r3 = pg.evaluate(ROWS); B.shot(pg, 'h1_recruit_apt', 100)
    ok(all(desc([o['a0'] for o in s]) for s in r3['secs']) and all(o['ap'] == 0 for s in r3['secs'] for o in s), '[창]: 창병 적성이 높은 순(S › A › B › C) · 그 적성 칸에 밑줄 %s' % [o['n'] for o in r3['secs'][-1][:4]])
    tapsel(pg, '#modal [data-a=srt][data-v=p]'); r4 = pg.evaluate(ROWS)
    ok([[o['n'] for o in s] for s in r4['secs']] == [[o['n'] for o in s] for s in r0['secs']], '[가능성]으로 돌아오면 처음 차례 그대로')
    pg.evaluate('closeDialog()')
    # ---------- ⑨ 일기토 화면 ----------
    print('⑨ 일기토: 합별 기록')
    pg.evaluate('''() => { var a = G.officers.filter(function (o) { return o.n === '장비'; })[0], d = G.officers.filter(function (o) { return o.n === '하후연'; })[0]; var S = duelNew('duel', a, d, {}); window._S = S; window._dd = 0; duelOpen(S, null, { sub: '지켜보기' }, function () { window._dd = 1; }); }''')
    pg.wait_for_function('DU && DU.ended', timeout=40000); pg.wait_for_timeout(700)
    du = pg.evaluate('''() => { var L = $('duLog').getBoundingClientRect(), rows = document.querySelectorAll('#duLogL li'), first = rows[0].getBoundingClientRect(), res = $('duRes').getBoundingClientRect(), st = document.querySelector('.du-stage').getBoundingClientRect();
      return { watch: $('duel').classList.contains('watch'), rounds: _S.round, rows: rows.length, top: rows[0].querySelector('.n').textContent, cells: [].map.call(rows, function (r) { return [r.className, r.querySelectorAll('.g').length, r.querySelector('.m').textContent]; }),
        logTop: Math.round(L.top), logH: Math.round(L.height), resTop: Math.round(res.top), resBottom: Math.round(res.bottom), stageBottom: Math.round(st.bottom), firstTop: Math.round(first.top), vh: innerHeight, wm: (document.querySelector('.du-wm') || {}).textContent, names: document.querySelector('.du-logh').textContent, moves: $('duMoves').children.length }; }''')
    print('     ', du); B.shot(pg, 'i1_duel_watch', 100)
    ok(du['watch'] and du['rows'] == du['rounds'] and du['top'] == '%d합' % du['rounds'] and all(c[1] == 2 and re.search(r'\d', c[2]) for c in du['cells']) and du['moves'] == 0, '지켜보는 일기토: 합마다 한 줄(%d줄 · 새 합이 위) — 두 사람의 수와 잃은 힘 %s' % (du['rows'], du['cells'][0]))
    ok(du['resTop'] >= du['stageBottom'] - 2 and du['firstTop'] >= du['resBottom'] - 2 and du['wm'] == '一騎討' and '장비' in du['names'] and '하후연' in du['names'], '끝나면 결과가 초상 아래 · 기록 위에 선다(기록을 덮지 않는다) — 결과 %d~%d · 기록 첫 줄 %d' % (du['resTop'], du['resBottom'], du['firstTop']))
    ok(du['firstTop'] > du['vh'] * 0.45, '화면 아래 절반이 비어 있지 않다(기록 첫 줄의 자리 %d / 화면 %d)' % (du['firstTop'], du['vh']))
    pg.evaluate('duClose()'); pg.wait_for_timeout(200)
    pg.evaluate('''() => { var a = off(G.factions[G.player].lord), d = G.officers.filter(function (o) { return o.n === '여포'; })[0]; duelOpen(duelNew('duel', a, d, {}), 'a', {}, function () {}); }'''); pg.wait_for_timeout(1300)
    pg.locator('#duMoves .du-mv').first.tap(); pg.wait_for_timeout(2400)
    du2 = pg.evaluate('''() => ({ watch: $('duel').classList.contains('watch'), rows: document.querySelectorAll('#duLogL li').length, moves: $('duMoves').children.length, wm: getComputedStyle(document.querySelector('.du-wm')).display, fit: $('duLog').getBoundingClientRect().bottom <= innerHeight + 1 })''')
    ok(not du2['watch'] and du2['rows'] == 1 and du2['moves'] == 3 and du2['wm'] == 'none' and du2['fit'], '내가 겨루는 일기토: 수 단추 아래에 기록이 쌓인다 %s' % du2); B.shot(pg, 'i2_duel_play', 100)
    pg.evaluate('() => { DU.done = null; duClose(); UI.busy = false; }'); pg.wait_for_timeout(200)
    # ---------- ⑩ 화살 · 불 ----------
    print('⑩ 화살 · 불')
    pg.set_viewport_size({'width': 390, 'height': 844}); pg.wait_for_timeout(300)
    s = pg.evaluate(d2.SETUP); pg.evaluate('(s) => { window.S = s; }', s); pg.wait_for_timeout(700)
    tx = pg.evaluate('''() => { var a = fxTex('arrow').image, t = fxTex('trail').image, e = fxTex('ember').image; return [a.width, a.height, t.width, e.width, VOLLEY]; }''')
    ok(tx[0] == 192 and tx[1] == 40 and tx[2] == 192 and tx[3] == 64 and tx[4]['fly0'] >= 400 and tx[4]['w'] >= 1.8, '화살 그림 192 × 40(살대 · 살촉 · 깃) · 잔상 · 불티 그림이 있다 · 날아가는 시간 %d ms + 거리' % tx[4]['fly0'])
    COUNT = '''() => { var a = fxTex('arrow'), t = fxTex('trail'), e = fxTex('ember'), p = fxTex('puff'), n = { arrow: 0, trail: 0, flame: 0, ember: 0, puff: 0, top: 0, ord: 0 };
      FX.live.forEach(function (s) { var m = s.material.map; if (s.material.opacity < 0.05) return; if (m === a) { n.arrow++; n.ord = Math.max(n.ord, s.renderOrder); } else if (m === t) n.trail++; else if (m === R3.flame) n.flame++; else if (m === e) n.ember++; else if (m === p) n.puff++; }); return n; }'''
    def sample(js, times):
        pg.evaluate(d2.SLOWJS, d2.SLOW); pg.evaluate(js); out = []; last = 0
        for t in times:
            pg.wait_for_timeout(max(1, (t - last) / d2.SLOW - 120)); last = t; out.append(pg.evaluate(COUNT))
        pg.wait_for_function('!UI.busy && FX.live.length === 0', timeout=90000); return out
    bow = sample(d2.act(2, 0, 'attack'), (260, 420, 600))
    print('      활:', bow); mxa = max(b['arrow'] for b in bow); mxt = max(b['trail'] for b in bow)
    ok(mxa >= 4 and mxt >= 3 and max(b['ord'] for b in bow) > 9, '활 공격: 날아가는 화살 %d발과 잔상 %d줄이 한꺼번에 보인다 · 부대의 딱지 위에 그려진다' % (mxa, mxt))
    fire = sample(d2.act(2, 0, 'fire'), (420, 620, 900))
    print('      화계:', fire)
    if '성공' in pg.evaluate('$("toast").textContent'):
        ok(max(f['flame'] for f in fire) >= 4 and max(f['ember'] for f in fire) >= 1 and max(f['puff'] for f in fire) >= 1, '화계: 불길 여럿 · 불티 · 연기 %s' % fire)
    else: print('      (화계가 실패한 판 — 불길은 보지 않는다: %s)' % pg.evaluate('$("toast").textContent'))
    fz = pg.evaluate('''() => { var k = K(S.f[0] + 3, S.f[1] + 2); G.fires[k] = 3; UI.dirty = true; syncScene(); var g = R3.fires[k]; var r = g ? { n: g.children.length, smoke: g.children.filter(function (c) { return c.userData.smoke; }).length } : null; delete G.fires[k]; UI.dirty = true; syncScene(); return r; }''')
    ok(fz and fz['n'] == 7 and fz['smoke'] == 2, '칸에 붙은 불: 불꽃 다섯 + 연기 둘 %s' % fz)
    # ---------- ⑪ 홍농 · 물빛 ----------
    print('⑪ 홍농 · 물빛')
    hn = pg.evaluate('''() => { var b = G.bases[baseByName('홍농')]; clearSel(); jumpTo(b.c, b.r, 1.0); syncScene(); return { id: b.id, n: G.bases.length, obj: !!R3.bases[b.id], own: facName(b.owner), mini: MAP3D.mini.length }; }'''); pg.wait_for_timeout(900); B.shot(pg, 'k1_hongnong', 300)
    ok(hn['id'] == 49 and hn['n'] == 50 and hn['obj'] and hn['own'] == '이각', '홍농이 지도에 선다(49번 · 이각군)')
    wt = pg.evaluate('''async () => { var im = new Image(); im.src = 'data:image/jpeg;base64,' + TERRAIN_B64; await im.decode(); var c = document.createElement('canvas'); c.width = im.width; c.height = im.height; var x = c.getContext('2d'); x.drawImage(im, 0, 0);
      function at(cc, r) { var p = hexCenter(cc, r), d = x.getImageData(Math.round(p[0] / MAP3D.WX * im.width), Math.round(p[1] / MAP3D.WZ * im.height), 3, 3).data, s = [0, 0, 0]; for (var i = 0; i < d.length; i += 4) { s[0] += d[i]; s[1] += d[i + 1]; s[2] += d[i + 2]; } return s.map(function (v) { return Math.round(v / 9); }); }
      var sea = [], land = [];
      for (var r = 4; r < H - 4; r += 5) for (var cc = 4; cc < W - 4; cc += 5) { var t = terr(cc, r); if (t === 's') sea.push(at(cc, r)); else if (t === 'p') land.push(at(cc, r)); }
      function avg(a) { var s = [0, 0, 0]; a.forEach(function (p) { s[0] += p[0]; s[1] += p[1]; s[2] += p[2]; }); return s.map(function (v) { return Math.round(v / a.length); }); }
      return { sea: avg(sea), land: avg(land), ns: sea.length, nl: land.length, w: im.width }; }''')
    print('     ', wt)
    ok(wt['ns'] > 50 and wt['sea'][2] - wt['sea'][0] >= 25 and wt['land'][0] - wt['land'][2] >= 8, '바탕 그림: 바다는 쪽빛(파랑 − 빨강 = %d), 평지는 종이 빛(빨강 − 파랑 = %d)' % (wt['sea'][2] - wt['sea'][0], wt['land'][0] - wt['land'][2]))
    print('console errors:', [e for e in B.errors if 'ReadPixels' not in e and 'ERR_FILE_NOT_FOUND' not in e][:6])
    ok(not [e for e in B.errors if e.startswith('pageerror')], '화면 오류 없음')
B.run(steps, 360, 780, 2)
print('FAILS', len(fails), fails)
sys.exit(1 if fails else 0)
