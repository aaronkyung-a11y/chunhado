# v0.7 점검 — 소리(녹음된 효과음·여러 곡 음악), 전법의 실패·성공·대성공 표시, 전법 풀이, 부대 목록, STATUS 창의 부대 단추
#   PAGE=pwa/index.html python3 tests/d12.py     ← 음악 파일(bgm/)이 옆에 있는 판으로 돌려야 음악까지 본다
#   python3 tests/d12.py                         ← 음악 파일이 없는 판: 만든 음악으로 넘어가는지를 본다
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
B.SHOTS = os.path.join(B.ROOT, 'shots4')
RES = []
HAS_BGM = os.path.isdir(os.path.join(B.ROOT, '..', 'dist', os.path.dirname(os.environ.get('PAGE', 'offline.html')), 'bgm')) and bool(os.listdir(os.path.join(B.ROOT, '..', 'dist', os.path.dirname(os.environ.get('PAGE', 'offline.html')), 'bgm')))
def check(name, cond, got=None):
    RES.append((name, bool(cond)))
    print(('  ok   ' if cond else '  FAIL ') + name + ('' if cond else '  ← ' + json.dumps(got, ensure_ascii=False)))
def tap(pg, sel, nth=0, wait=300):
    loc = pg.locator(sel)
    if loc.count() <= nth or not loc.nth(nth).is_visible(): print('   (없는 단추: %s)' % sel); return False
    loc.nth(nth).tap(); pg.wait_for_timeout(wait); return True
SPY = '''() => { if (window.__spy) return; window.__spy = [];
  var _p = sndPlay; sndPlay = function (n, v, j, d) { var r = _p(n, v, j, d); window.__spy.push((r ? '' : '!') + n); return r; };
  var _m = sfxMove; sfxMove = function (t, ms) { window.__spy.push('move:' + t); return _m(t, ms); };
  var _s = sfxSyn; sfxSyn = function (k) { window.__spy.push('syn:' + k); return _s(k); }; }'''
def spied(pg):
    r = pg.evaluate('() => { var a = window.__spy.slice(); window.__spy.length = 0; return a; }'); return r
SETUP = '''() => {
  function field() {
    for (var r = 92; r < 112; r++) for (var c = 146; c < 168; c++) {
      var ok = true;
      for (var dr = -3; dr <= 3 && ok; dr++) for (var dc = -4; dc <= 4 && ok; dc++) { var k = K(c + dc, r + dr); if (TCH[k] !== 112 || ZONE[k] >= 0 || BAT[k] !== undefined || PAT[k] || UAT[k]) ok = false; }
      if (ok) return [c, r];
    }
    return null;
  }
  var f = field(), b = facBases(G.player)[0], eb = G.bases[baseByName('복양')], out = { f: f, mine: [], foe: [] };
  b.w.spear = 9000; b.w.horse = 9000; b.w.bow = 9000; b.w.halberd = 9000; b.troops = 30000; b.food = 90000; G.factions[G.player].ap = 250;
  eb.troops = 30000; eb.w.spear = 9000; eb.food = 90000; G.factions[eb.owner].ap = 250;
  var mineSpec = [['spear', 0, 0], ['cav', 0, 1], ['bow', -2, 0]], foeSpec = [['spear', 1, 0], ['spear', 1, 1]];
  mineSpec.forEach(function (s) {
    var ids = autoTeam(b, s[0], 4000); if (!ids.length) ids = [idleOfficers(b)[0].id];
    var r = cmdDeploy(b, { type: s[0], ids: ids.slice(0, 1), troops: 4000, food: 4000 });
    if (!r.ok) { out.err = r.msg; return; }
    placeUnit(r.unit, f[0] + s[1], f[1] + s[2]); r.unit.mp = uMaxMp(r.unit); r.unit.done = false; r.unit.morale = 100; out.mine.push(r.unit.id);
  });
  foeSpec.forEach(function (s, i) {
    var os = idleOfficers(eb); if (!os.length) return;
    var r = cmdDeploy(eb, { type: s[0], ids: [os[0].id], troops: 3000, food: 3000 });
    if (!r.ok) { out.err2 = r.msg; return; }
    placeUnit(r.unit, f[0] + s[1], f[1] + s[2]); r.unit.troops = r.unit.max = 12000; out.foe.push(r.unit.id);
  });
  EVQ.length = 0; clearSel(); syncScene(); jumpTo(f[0], f[1], 1.5); requestDraw();
  return out;
}'''
FLOATS = '''() => Array.prototype.map.call(document.querySelectorAll('#fx .flt'), function (e) { return e.textContent; })'''
def tactic(pg, mi, fi, tacjs, roll, name, shot_at=700):
    """rnd 를 roll 로 고정해 전법을 한 번 건다. 뜬 글씨·소리·결과 한 줄을 돌려준다"""
    pg.evaluate('''([mi, fi, roll]) => { var u = UMAP[S.mine[mi]], t = UMAP[S.foe[fi]]; u.done = false; u.morale = 100; t.morale = 100; t.status = null; t.troops = t.max = 12000; u.troops = 4000;
      window.__rnd = rnd; var first = true; rnd = function () { if (first) { first = false; return roll; } return 0.5; };
      window.__odds = tacticOdds(u, t); window.__fl = [];
      var _ft = floatText; window.__ft = _ft; floatText = function (c, r, tx) { window.__fl.push(tx); return _ft.apply(null, arguments); };
      selectUnit(u, true); UI.target = { kind: 'unit', u: t, c: t.c, r: t.r }; }''', [mi, fi, roll])
    spied(pg)
    pg.evaluate('(tac) => { doAct({ kind: "tactic", tac: eval(tac) }); }', tacjs)
    pg.wait_for_timeout(shot_at); pg.screenshot(path=os.path.join(B.SHOTS, name + '.png'))
    pg.wait_for_timeout(2600)
    out = pg.evaluate('''() => { rnd = window.__rnd; floatText = window.__ft; return { fl: window.__fl, toast: $('toast').textContent, odds: window.__odds, busy: UI.busy }; }''')
    out['snd'] = spied(pg); return out
def steps(pg):
    pg.evaluate(SPY)
    # ---------- 1. 소리 준비 ----------
    tap(pg, '#tHelp', 0, 900)                                  # 첫 누름: 소리 준비 + 제목 음악
    pg.wait_for_timeout(1500)
    a = pg.evaluate('''() => ({ n: Object.keys(SND.buf).length, total: Object.keys(SFX_DATA).length, ac: AC ? AC.state : null, off: SND.off, dur: Object.keys(SND.buf).map(function (k) { return [k, +SND.buf[k].duration.toFixed(2)]; }),
      mode: BGM.mode, file: BGM.file, name: BGM.name, paused: BGM.el ? BGM.el.paused : null, t: BGM.el ? BGM.el.currentTime : -1, dead: Object.keys(BGM.dead), syn: SYN.name })''')
    print('  효과음 풀린 것', a['n'], '/', a['total'], 'AC', a['ac'], '| 음악', a['mode'], a['file'], 'paused', a['paused'], 't', round(a['t'], 2), 'dead', a['dead'])
    check('효과음 27개가 모두 풀림', a['n'] == 27 and a['total'] == 27, a['n'])
    check('효과음 시작 보정이 0~60ms', all(0 <= v <= 0.061 for v in a['off'].values()), a['off'])
    check('소리 장치가 켜짐(running)', a['ac'] == 'running', a['ac'])
    print('  시작 보정(ms):', {k: round(v * 1000) for k, v in a['off'].items()})
    if HAS_BGM:
        check('제목 음악: 파일(title.mp3)이 나온다', a['mode'] == 'file' and a['file'] == 'title' and a['paused'] is False and a['t'] > 0.3, a)
    else:
        check('음악 파일이 없으면 만든 음악으로', a['mode'] == 'syn' and 'title' in a['dead'], a)
    spied(pg); tap(pg, '#modal .dlg-h .x')
    s = spied(pg); check('단추를 누르면 나무 두드리는 소리(tick)', 'tick' in s and not any(x.startswith('syn:') for x in s), s)
    # ---------- 2. 새 게임 → 평시 음악, 여러 곡 돌아가기 ----------
    tap(pg, '#tNew'); tap(pg, '#modal .row', 0); tap(pg, '#modal [data-a=go]', 0, 700); s = spied(pg)
    check('새 게임: 징 소리', 'gong' in s, s)
    tap(pg, '#modal [data-a=close]', 0, 1500)
    pg.wait_for_timeout(800)
    m = pg.evaluate('() => ({ mode: BGM.mode, file: BGM.file, name: BGM.name, loop: BGM.el && BGM.el.loop, t: BGM.el ? BGM.el.currentTime : -1 })')
    if HAS_BGM:
        check('게임 시작: 평시 음악(field1 또는 field2)', m['mode'] == 'file' and m['name'] == 'field' and m['file'] in ('field1', 'field2') and m['loop'] is False, m)
        first = m['file']
        pg.evaluate('() => { BGM.el.currentTime = BGM.el.duration - 0.6; }'); pg.wait_for_timeout(2200)
        m2 = pg.evaluate('() => ({ mode: BGM.mode, file: BGM.file, name: BGM.name, t: BGM.el.currentTime, paused: BGM.el.paused })')
        check('곡이 끝나면 같은 장면의 다음 곡으로', m2['file'] != first and m2['file'] in ('field1', 'field2') and m2['paused'] is False and m2['t'] < 2.5, m2)
    else:
        check('음악 파일이 없으면 만든 음악(평시)', m['mode'] == 'syn', m)
    # ---------- 3. STATUS 창의 부대 단추, 부대 목록 ----------
    links = pg.evaluate('''() => Array.prototype.map.call(document.querySelectorAll('#sheet .hm-links button'), function (b) { var r = b.getBoundingClientRect(); return [b.getAttribute('data-v'), b.textContent, Math.round(r.width), b.scrollWidth <= b.clientWidth + 1]; })''')
    print('  STATUS 단추:', links)
    check('v0.9.2: STATUS 창의 거점·부대·무장·천하 네 단추는 없다(아래 [목록] 단추와 같은 일을 했다)', links == [], links)
    S = pg.evaluate(SETUP); print('  setup', S); pg.evaluate('(s) => { window.S = s; }', S)
    # 다른 세력 부대 하나를 멀리(목록의 "가까이"에 안 들게) 옮겨 둔다
    B.shot(pg, 'd12_01_home', 500)
    tap(pg, '#btnList', 0, 500); tap(pg, '#modal .tabs button[data-v=unit]', 0, 500)       # v0.9.2: 아래 [목록] → 부대 탭
    L = pg.evaluate('''() => ({ title: (document.querySelector('#modal .dlg-h h2') || {}).textContent, tab: (document.querySelector('#modal .tabs button.on') || { getAttribute: function () {} }).getAttribute('data-v'),
      secs: Array.prototype.map.call(document.querySelectorAll('#modal .sec'), function (e) { return e.textContent; }),
      rows: Array.prototype.map.call(document.querySelectorAll('#modal .row[data-a=u]'), function (e) { return e.innerText.replace(/\\n+/g, ' | '); }) })''')
    print('  목록:', L['secs']); [print('    ', r) for r in L['rows']]
    check('[목록] → 부대 탭', L['title'] == '목록' and L['tab'] == 'unit', L)
    check('내 부대 3개와 가까운 다른 세력 부대 2개가 줄로 나옴', len(L['rows']) == 5 and '내 부대 3개' in L['secs'][0] and '2개' in L['secs'][1], L)
    check('내 부대 줄에 위치와 상태(명령 대기)', all(('칸' in r or '성역' in r) and '명령 대기' in r for r in L['rows'][:3]), L['rows'][:3])
    check('다른 세력 부대 줄에 세력·위치·내 부대와의 거리', all('내 ' in r and '칸' in r for r in L['rows'][3:]), L['rows'][3:])
    B.shot(pg, 'd12_02_unitlist', 300)
    fid = S['foe'][0]
    tap(pg, '#modal .row[data-a=u][data-v="%d"]' % fid, 0, 900)
    j = pg.evaluate('() => ({ modal: !!MODAL, sel: UI.sel ? UI.sel.kind + ":" + UI.sel.id : null, chip: $("ret").classList.contains("on") ? $("ret").textContent : null })')
    check('다른 세력 부대 줄을 누르면 그 부대로 건너뜀 + ‹ 목록 단추', (not j['modal']) and j['sel'] == 'unit:%d' % fid and j['chip'] and '목록' in j['chip'], j)
    tap(pg, '#ret', 0, 500)
    j2 = pg.evaluate('''() => ({ title: (document.querySelector('#modal .dlg-h h2') || {}).textContent, tab: (document.querySelector('#modal .tabs button.on') || { getAttribute: function () {} }).getAttribute('data-v') })''')
    check('‹ 목록 → 보던 부대 탭으로 돌아옴', j2['title'] == '목록' and j2['tab'] == 'unit', j2)
    tap(pg, '#modal .dlg-h .x')
    # ---------- 4. 전법: 확률 표시, 전법 풀이 ----------
    pg.evaluate('() => { var u = UMAP[S.mine[0]]; selectUnit(u, true); }'); pg.wait_for_timeout(400)
    ft = pg.evaluate('() => { var t = UMAP[S.foe[0]]; return [t.c, t.r]; }'); B.taphex(pg, ft[0], ft[1]); pg.wait_for_timeout(500)
    acts = pg.evaluate('''() => Array.prototype.map.call(document.querySelectorAll('#sheet .act'), function (b) { return [b.getAttribute('data-a'), b.innerText.replace(/\\n+/g, ' | '), b.classList.contains('off'), b.scrollWidth <= b.clientWidth + 1]; })''')
    [print('    ', x) for x in acts]
    od = pg.evaluate('() => tacticOdds(UMAP[S.mine[0]], UMAP[S.foe[0]])'); print('  확률', od)
    tnames = pg.evaluate('() => tacticList(UMAP[S.mine[0]]).map(function (t) { return t.name; })')
    tacs = [x for x in acts if x[0] == 'act' and x[1].split(' | ')[0] in tnames]
    check('전법 단추에 성공률(v0.9.2: 대성공률은 [전법 풀이]에만)', len(tacs) >= 1 and all(((('%d%%' % od['ok']) in x[1]) or '필중' in x[1]) and '대성공' not in x[1] for x in tacs), acts)
    check('단추 글씨가 넘치지 않음', all(x[3] for x in acts), acts)
    check('전법 풀이 단추가 있음', any(x[0] == 'tacinfo' for x in acts), acts)
    B.shot(pg, 'd12_03_target', 300)
    tap(pg, '#sheet [data-a=tacinfo]', 0, 500)
    info = pg.evaluate('''() => ({ title: (document.querySelector('#modal .dlg-h h2') || {}).textContent, odds: (document.querySelector('#modal .odds') || {}).innerText, tacs: Array.prototype.map.call(document.querySelectorAll('#modal .tac'), function (e) { return e.innerText.replace(/\\n+/g, ' | '); }) })''')
    print('  풀이:', info['odds'].replace('\n', ' ')); [print('    ', x) for x in info['tacs']]
    check('전법 풀이 창: 확률 세 칸의 합이 100', info['title'] == '전법 풀이' and (od['sure'] or ('%d%%' % od['crit']) in info['odds'] and ('%d%%' % (od['ok'] - od['crit'])) in info['odds'] and ('%d%%' % (100 - od['ok'])) in info['odds']), info)
    check('전법 풀이 창: 전법 셋의 성공·대성공 효과', len(info['tacs']) == 3 and all('성공' in x and '대성공' in x for x in info['tacs']), info['tacs'])
    B.shot(pg, 'd12_04_tacinfo', 300)
    tap(pg, '#modal .dlg-h .x')
    k = pg.evaluate('() => ({ modal: !!MODAL, target: !!UI.target, sel: UI.sel ? UI.sel.kind : null })')
    check('전법 풀이를 닫으면 대상을 고른 그 자리로', (not k['modal']) and k['target'] and k['sel'] == 'unit', k)
    # ---------- 5. 전법의 세 결과: 글씨·소리 ----------
    pg.evaluate('UI.pspeed = 1')
    r = tactic(pg, 0, 0, 'TACTICS.spear[0]', 0.999, 'd12_05_fail')
    print('  실패:', r['fl'], '|', r['toast'], '|', r['snd'])
    check('실패: "돌출 실패" 글씨와 성공률', any('돌출 실패' in x for x in r['fl']) and ('성공률 %d%%' % r['odds']['ok']) in r['toast'] and not any('밀어냄' in x for x in r['fl']), r)
    check('실패: 기합 → 막히는 소리(clang+thud)', 'shout' in r['snd'] and 'clang' in r['snd'] and 'thud' in r['snd'] and 'crush' not in r['snd'], r['snd'])
    r = tactic(pg, 0, 0, 'TACTICS.spear[0]', (r['odds']['crit'] + r['odds']['ok']) / 200.0, 'd12_06_ok')
    print('  성공:', r['fl'], '|', r['toast'], '|', r['snd'])
    check('성공: "돌출!" (대성공 아님), 한 칸', any(x == '돌출!' for x in r['fl']) and '돌출 성공' in r['toast'] and not any('두 칸' in x for x in r['fl']), r)
    check('성공: 기합 → 큰 타격(crush+clang)', 'shout' in r['snd'] and 'crush' in r['snd'] and 'gong' not in r['snd'], r['snd'])
    pg.evaluate('() => { var u = UMAP[S.mine[0]], t = UMAP[S.foe[0]]; placeUnit(t, u.c + 1, u.r); syncScene(); }'); pg.wait_for_timeout(300)
    r = tactic(pg, 0, 0, 'TACTICS.spear[0]', 0.001, 'd12_07_great', 900)
    print('  대성공:', r['fl'], '|', r['toast'], '|', r['snd'])
    check('대성공: "돌출 대성공!" + 두 칸 밀어냄', any('돌출 대성공!' in x for x in r['fl']) and any('두 칸 밀어냄' in x for x in r['fl']) and '대성공' in r['toast'] and '두 칸' in r['toast'], r)
    check('대성공: 더 큰 소리(crush+clang+gong)', 'crush' in r['snd'] and 'clang' in r['snd'] and 'gong' in r['snd'], r['snd'])
    # 이단첨 대성공(기력 -30): 적성이 모자라도 규칙을 바로 불러 확인
    pg.evaluate('() => { var u = UMAP[S.mine[0]], t = UMAP[S.foe[0]]; placeUnit(t, u.c + 1, u.r); syncScene(); }'); pg.wait_for_timeout(300)
    r = tactic(pg, 0, 0, 'TACTICS.spear[2]', 0.001, 'd12_08_idan', 900)
    print('  이단첨 대성공:', r['fl'], '|', r['toast'])
    check('이단첨 대성공: 기력 -30 글씨', any('기력 -30' in x for x in r['fl']) and '기력 -30' in r['toast'], r)
    r = tactic(pg, 0, 0, 'TACTICS.spear[1]', 0.001, 'd12_09_naseon', 1300)
    print('  나선첨 대성공:', r['fl'], '|', r['toast'])
    check('나선첨 대성공: 반드시 혼란(v0.9.1: 날수까지 — 혼란 10일)', any(x == '혼란 10일' for x in r['fl']) and '혼란 10일' in r['toast'], r)
    # ---------- 6. 이동·통상 공격·활·기병 전법의 소리 ----------
    pg.evaluate('() => { var u = UMAP[S.mine[1]]; u.done = false; u.mp = uMaxMp(u); selectUnit(u, true); }'); pg.wait_for_timeout(400); spied(pg)
    dest = pg.evaluate('() => { var u = UMAP[S.mine[1]], rc = UI.rc, best = null; for (var k in rc.cost) { k = +k; var c = k % W, r = (k - c) / W, d = hdist(u.c, u.r, c, r); if (d >= 2 && d <= 3 && !UAT[k] && c < u.c) { best = [c, r]; break; } } return best; }')
    if dest:
        B.taphex(pg, dest[0], dest[1]); pg.wait_for_timeout(1500); s = spied(pg)
        check('기병이 움직이면 말발굽 소리(move:cav)', 'move:cav' in s and not any(x.startswith('syn:') for x in s), s)
    pg.evaluate('''() => { var u = UMAP[S.mine[2]], t = UMAP[S.foe[1]]; u.done = false; t.troops = t.max = 12000; t.status = null; selectUnit(u, true); UI.target = { kind: 'unit', u: t, c: t.c, r: t.r }; doAct({ kind: 'attack' }); }''')
    pg.wait_for_timeout(3200); s = spied(pg); print('  활 공격 소리:', s)
    check('활 공격: 시위·화살 무리 → 박히는 소리', 'bow' in s and 'arrows' in s and 'thud' in s, s)
    pg.evaluate('''() => { var u = UMAP[S.mine[0]], t = UMAP[S.foe[0]]; u.done = false; t.status = null; placeUnit(t, u.c + 1, u.r); syncScene(); selectUnit(u, true); UI.target = { kind: 'unit', u: t, c: t.c, r: t.r }; doAct({ kind: 'attack' }); }''')
    pg.wait_for_timeout(3200); s = spied(pg); print('  근접 공격 소리:', s)
    check('근접 공격: 발 구르기 → 베는 소리', 'stomp' in s and 'slash' in s, s)
    # ---------- 7. 음악 장면: 전투 → (턴이 지나면) 긴장 → 평시 ----------
    st = pg.evaluate('() => ({ want: BGM.want, name: BGM.name, file: BGM.file, mode: BGM.mode, state: bgmForState() })')
    check('싸운 뒤에는 전투 음악', st['want'] == 'battle' and st['state'] == 'battle' and (not HAS_BGM or st['file'] in ('battle1', 'battle2')), st)
    t1 = pg.evaluate('''() => { UI.battleTurn = undefined; var a = bgmForState();        // 남의 부대가 내 부대 바로 옆 → 긴장
      S.foe.forEach(function (id) { var u = UMAP[id]; if (u) removeUnit(u); }); syncScene(); var b = bgmForState();
      return [a, b]; }''')
    check('싸움이 없고 적 부대가 가까우면 긴장, 없으면 평시', t1 == ['tense', 'field'], t1)
    pg.evaluate("() => { playBgm('tense'); }"); pg.wait_for_timeout(1800)
    m = pg.evaluate('() => ({ mode: BGM.mode, file: BGM.file, name: BGM.name, loop: BGM.el && BGM.el.loop, paused: BGM.el && BGM.el.paused })')
    if HAS_BGM: check('긴장 음악: tense.mp3 한 곡을 되풀이', m['mode'] == 'file' and m['file'] == 'tense' and m['loop'] is True and m['paused'] is False, m)
    else: check('긴장 음악: 파일이 없으면 만든 음악', m['mode'] == 'syn', m)
    # 음악 끄기·켜기
    pg.evaluate('() => { UI.music = false; stopBgm(); }'); pg.wait_for_timeout(300)
    off = pg.evaluate('() => ({ paused: BGM.el ? BGM.el.paused : true, name: BGM.name, syn: SYN.timer })')
    check('음악을 끄면 멈춤', off['paused'] and off['name'] == '' and not off['syn'], off)
    pg.evaluate('() => { UI.music = true; playBgm(bgmForState()); }'); pg.wait_for_timeout(1500)
    on = pg.evaluate('() => ({ mode: BGM.mode, name: BGM.name, paused: BGM.el ? BGM.el.paused : null })')
    check('다시 켜면 지금 장면의 음악', on['name'] == 'field' and on['mode'] in ('file', 'syn'), on)
    tap(pg, '#btnMenu', 0, 400)
    mt = pg.evaluate('''() => (document.querySelector('#modal [data-a=mus]') || {}).innerText || ""''')
    check('메뉴의 음악 단추가 지금 나오는 것이 연주곡인지 만든 음악인지 알려 줌', ('연주곡' in mt) if HAS_BGM else ('만든 음악' in mt), mt)
    B.shot(pg, 'd12_10_menu', 300)
    tap(pg, '#modal .dlg-h .x')
    B.shot(pg, 'd12_11_end', 300)
B.run(steps, 412, 915)
errs = [e for e in B.errors if 'ERR_FILE_NOT_FOUND' not in e and 'GPU stall' not in e and 'GL Driver Message' not in e]
print('console errors:', len(errs)); [print('   ', e[:300]) for e in errs[:12]]
bad = [n for n, ok in RES if not ok]
print('검사 %d개 가운데 통과 %d, 실패 %d' % (len(RES), len(RES) - len(bad), len(bad)))
sys.exit(1 if bad or errs else 0)
