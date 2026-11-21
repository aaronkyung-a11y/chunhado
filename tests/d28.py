# v0.16 — 화면 조작으로 확인: AI 가 걸어온 일기토(할 일 · 답하는 창 · 받지 않기 · 받아 겨루기 · 열흘 재생에서 걸어오기) · 출병 요청 · AI 끼리의 협정 보기
#   python3 tests/d28.py          찍은 그림은 tests/shots30/
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import taphex, tapsel
B.SHOTS = os.path.join(B.ROOT, 'shots30')
os.makedirs(B.SHOTS, exist_ok=True)
fails = []
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)
def toast(pg): return pg.evaluate('$("toast").textContent')
def head(pg): return pg.evaluate('MODAL ? document.querySelector("#modal .dlg-h h2").textContent : ""')
def talktx(pg): return pg.evaluate('(() => { var t = $("talk"); return t && t.classList.contains("on") ? t.innerText.replace(/\\n+/g, " | ") : ""; })()')
def facName(pg, f): return pg.evaluate('facName(%d)' % f)
def reload(pg):
    pg.reload(); pg.wait_for_function('window.R3 && R3.ready', timeout=60000); pg.wait_for_timeout(600)
def fresh(pg, fac, seed):
    pg.evaluate('([f, s]) => { localStorage.clear(); newGame(f, s); saveGame(); }', [fac, seed]); reload(pg)
    tapsel(pg, '#tCont'); pg.wait_for_timeout(1300)
    if pg.evaluate('!!MODAL'): pg.evaluate('closeDialog()')
    pg.evaluate('talkHide()'); pg.wait_for_timeout(200)
# 여포(복양)의 부대 a 를 내 하후돈 부대 d 옆에 세운다
SETUP = """() => {
  function field() { for (var r = 92; r < 112; r++) for (var c = 146; c < 168; c++) { var good = true; for (var dr = -2; dr <= 2 && good; dr++) for (var dc = -3; dc <= 3 && good; dc++) { var k = K(c + dc, r + dr); if (TCH[k] !== 112 || ZONE[k] >= 0 || BAT[k] !== undefined || PAT[k] || UAT[k]) good = false; } if (good) return [c, r]; } return null; }
  var f = field(), b = facBases(G.player)[0], eb = G.bases[baseByName('복양')];
  b.w.spear = 30000; b.troops = 60000; b.food = 200000; G.factions[G.player].ap = 250; eb.troops = 60000; eb.w.spear = 30000; eb.food = 200000; G.factions[eb.owner].ap = 250;
  if (G.peace) G.peace.until = 0;
  var me = G.officers.filter(function (o) { return o.n === '하후돈'; })[0], foe = G.officers.filter(function (o) { return o.n === '여포'; })[0];
  var a = cmdDeploy(eb, { type: 'spear', ids: [foe.id], troops: 5000, food: 5000 }).unit, d = cmdDeploy(b, { type: 'spear', ids: [me.id], troops: 5000, food: 5000 }).unit;
  placeUnit(a, f[0], f[1]); placeUnit(d, f[0] + 1, f[1]);
  [a, d].forEach(function (u) { u.born = -9; u.done = false; u.mp = uMaxMp(u); u.morale = 80; });
  window.T = { a: a.id, d: d.id, f: f }; window._rnd = rnd;
  EVQ.length = 0; clearSel(); syncScene(); jumpTo(f[0], f[1], 1.5); requestDraw();
  return { a: uName(a), d: uName(d), wa: foe.war, wd: me.war, f: f, ask: DUEL_K.aiAsk, pact: [DIP_K.aiPact, DIP_K.aiPactUp] };
}"""
RESET = """() => { var a = UMAP[T.a], d = UMAP[T.d]; [a, d].forEach(function (u) { u.troops = 5000; u.morale = 80; u.status = null; u.done = false; u.mp = uMaxMp(u); u.ox = -1; }); G.asks = []; closeDialog(); talkHide(); clearSel(); syncScene(); }"""
DU_STATE = '''() => { var e = $('duel'); if (!e || !DU) return null; var S = DU.S;
  return { on: e.classList.contains('on'), kind: S.kind, seal: e.querySelector('.du-seal').textContent, round: $('duR').textContent, names: [e.querySelector('#duFa .du-nm').textContent, e.querySelector('#duFd .du-nm').textContent],
    st: [e.querySelector('#duFa .du-st').textContent, e.querySelector('#duFd .du-st').textContent], hp: [+$('duHa').textContent, +$('duHd').textContent], bar: [$('duBa').style.width, $('duBd').style.width],
    moves: Array.prototype.map.call(e.querySelectorAll('.du-mv'), function (b) { return b.querySelector('b').textContent; }), movesOff: $('duMoves').classList.contains('off'), hint: $('duHint').innerText.replace(/\\n+/g, ' '),
    plan: S.plan, hintMove: S.hint ? S.hint.move : null, r: S.round, over: S.over, win: S.win, ko: S.ko, log: S.log.length, busy: DU.busy, ended: DU.ended, res: $('duRes').classList.contains('on') ? $('duRes').innerText.replace(/\\n+/g, ' | ') : '',
    fit: (function () { var r = e.querySelector('.du-in').getBoundingClientRect(), m = $('duMoves').getBoundingClientRect(), f = $('duFoot').getBoundingClientRect(); return [document.documentElement.scrollWidth <= window.innerWidth, Math.round(Math.max(m.bottom, f.bottom)) <= window.innerHeight, Math.round(r.width)]; })() }; }'''
def play_out(pg, pick):
    """끝날 때까지 수를 낸다. pick(state) → 누를 수의 이름. 돌려주는 값 = 합마다의 상태"""
    seen = []
    for _ in range(8):
        pg.wait_for_function('!DU || DU.ended || (!DU.busy && !$("duMoves").classList.contains("off"))', timeout=15000)
        st = pg.evaluate(DU_STATE)
        if st is None or st['ended']: break
        seen.append(st)
        name = pick(st); pg.locator('#duel .du-mv:has(b:text-is("%s"))' % name).first.tap()      # 이름이 꼭 같은 단추(풀이에 다른 수의 이름이 나온다)
    pg.wait_for_function('DU && DU.ended', timeout=15000); pg.wait_for_timeout(500)
FIT = """(() => { var d = document.querySelector('#modal .dlg'), r = d ? d.getBoundingClientRect() : null; return r ? [Math.round(r.left) >= 0, Math.round(r.right) <= innerWidth, Math.round(r.bottom) <= innerHeight] : null; })()"""
CMDS = """Array.prototype.map.call(document.querySelectorAll('#modal .cmds .cmd'), function (e) { return [e.getAttribute('data-a'), e.innerText.replace(/\\n+/g, ' | '), e.classList.contains('off'), e.scrollWidth <= e.clientWidth + 1]; })"""
ASKDLG = """(() => { var m = $('modal'); if (!MODAL) return null; var ks = m.querySelectorAll('.dk');
  return { head: m.querySelector('.dlg-h h2').textContent, say: (m.querySelector('.say') || {}).innerText || '', cards: Array.prototype.map.call(ks, function (e) { return [e.classList.contains('me'), e.innerText.replace(/\\n+/g, ' | '), e.scrollWidth <= e.clientWidth + 1]; }),
    btn: Array.prototype.map.call(m.querySelectorAll('.cmds .cmd'), function (e) { return [e.getAttribute('data-a'), e.innerText.replace(/\\n+/g, ' | ')]; }), text: m.querySelector('.dlg-b').innerText }; })()"""
def open_dip(pg):
    pg.evaluate('(() => { closeDialog(); talkHide(); gotoBase(G.bases[BID], "men"); })()'); pg.wait_for_timeout(400)
    tapsel(pg, '#sheet [data-a=dip]'); pg.wait_for_timeout(400)
def open_fac(pg, f):
    open_dip(pg); pg.locator('#modal .row[data-a=f][data-v="%d"]' % f).tap(); pg.wait_for_timeout(400)
def steps(pg):
    fresh(pg, 0, 1)
    ok(pg.evaluate('GAME_VERSION') == 'v0.16', '판 번호 v0.16')
    S = pg.evaluate(SETUP); print('     ', S)
    ok(S['ask'] == 0 and S['pact'] == [0, 0], '시험 기본값: AI 의 일기토 신청 · AI 끼리의 협정은 꺼 둔다(이 시험이 제 손으로 켠다)')
    # ================= 1. 걸어온 일기토 — 할 일과 답하는 창 =================
    print('1. 걸어온 일기토: 할 일 · 답하는 창')
    r = pg.evaluate('(() => { var r = aiChallenge(UMAP[T.a], UMAP[T.d]); HOME.open = true; clearSel(); showHome(); refreshHud(); return [r, duelAsks().length, UMAP[T.a].morale, UMAP[T.a].done]; })()'); pg.wait_for_timeout(400)
    ok(r == [True, 1, 80 - 10, True], '여포가 하후돈에게 건다 → 적어 둔다(건 쪽 기력 -10 · 행동 끝) %s' % r)
    td = pg.evaluate('todoList().filter(function (x) { return x.go[0] === "duelask"; }).map(function (x) { return [x.t, x.s, x.lb, x.go, x.cls]; })')
    ok(len(td) == 1 and '여포' in td[0][0] and '하후돈에게 일기토를 걸어왔습니다' in td[0][0] and td[0][2] == '답하기' and ('무력 %d 대 %d' % (S['wa'], S['wd'])) in td[0][1], '[지금 할 일]에 뜬다 — %s · %s' % (td[0][0], td[0][1]) if td else '[지금 할 일]에 뜬다')
    home = pg.evaluate('$("sheet").innerText'); ok('일기토를 걸어왔습니다' in home, '화면의 할 일 줄에도 보인다'); B.shot(pg, 'y1_todo', 200)
    pg.evaluate('askSoon(100)'); pg.wait_for_function('!!MODAL', timeout=5000); pg.wait_for_timeout(500)
    d = pg.evaluate(ASKDLG)
    ok(d and d['head'] == '일기토 신청 — 여포' and len(d['cards']) == 2 and d['cards'][0][0] is False and '여포' in d['cards'][0][1] and d['cards'][1][0] is True and '하후돈' in d['cards'][1][1] and all(c[2] for c in d['cards']), '내 차례 첫머리에 답하는 창이 뜬다: 두 주장의 무력 · 부대 — %s' % (d and [c[1] for c in d['cards']]))
    ok(d and [b[0] for b in d['btn']] == ['yes', 'no'] and '기력 -5' in d['btn'][1][1] and '이기면' in d['text'] and '받지 않으면' in d['text'] and ('상대가 %d 높습니다' % (S['wa'] - S['wd'])) in d['text'], '[받아들인다] · [받지 않는다]와 걸린 것(이기면 · 지면 · 받지 않으면)이 적혀 있다')
    fit = pg.evaluate(FIT); ok(fit and all(fit), '창이 화면 안에 들어온다 %s' % fit)
    B.shot(pg, 'y1_ask', 200)
    # 받지 않는다
    tapsel(pg, '#modal [data-a=no]'); pg.wait_for_timeout(500)
    st = pg.evaluate('[UMAP[T.d].morale, duelAsks().length, !!MODAL, !!DU]'); tk = talktx(pg)
    ok(st == [75, 0, False, False] and '받지 않았습니다' in tk and '기력 -5' in tk and '하후돈' in tk, '받지 않는다 → 내 부대 기력 -5, 하후돈의 한마디 — ' + tk[:70])
    B.shot(pg, 'y1_no', 200)
    pg.wait_for_timeout(1300); ok(pg.evaluate('!MODAL'), '더 걸려 온 것이 없으면 창이 다시 뜨지 않는다')
    ok(pg.evaluate('todoList().filter(function (x) { return x.go[0] === "duelask"; }).length') == 0, '할 일에서도 사라진다')
    # ================= 2. 받아들여 직접 겨룬다 =================
    print('2. 받아들여 겨룬다')
    pg.evaluate(RESET); pg.wait_for_timeout(300)
    pg.evaluate('(() => { aiChallenge(UMAP[T.a], UMAP[T.d]); UMAP[T.a].morale = 80; goTodo(todoList().filter(function (x) { return x.go[0] === "duelask"; })[0].go); })()'); pg.wait_for_timeout(500)
    ok(head(pg) == '일기토 신청 — 여포', '[답하기]로도 같은 창이 열린다')
    tapsel(pg, '#modal [data-a=yes]'); pg.wait_for_function('!!DU', timeout=8000); pg.wait_for_timeout(800)
    st = pg.evaluate(DU_STATE)
    ok(st['on'] and st['kind'] == 'duel' and pg.evaluate('DU.human') == 'd' and len(st['moves']) == 3 and st['hp'] == [100, 100] and '여포' in st['names'][0] and '하후돈' in st['names'][1] and pg.evaluate('UMAP[T.d].morale === 80 && duelAsks().length === 0 && !MODAL'), '일기토 화면: 건 쪽(여포)이 왼쪽, 내가 오른쪽에서 수를 고른다 — %s' % st['names'])
    ok(all(st['fit']) if isinstance(st.get('fit'), list) else True, '화면 안에 들어온다')
    B.shot(pg, 'y2_duel', 200)
    BEAT = {'atk': '방어', 'def': '필살', 'sp': '맹공'}
    play_out(pg, lambda s: BEAT[s['plan']['a']])                      # 상대(a)가 낼 수를 이기는 수
    won = pg.evaluate(DU_STATE)
    eff = pg.evaluate('[UMAP[T.a] ? UMAP[T.a].morale : -1, UMAP[T.a] ? UMAP[T.a].troops : -1, UMAP[T.d].morale, UMAP[T.d].troops]')
    ok(won['win'] == 'd' and eff == [80 - (35 if won['ko'] else 25), 5000 - (600 if won['ko'] else 400), 90, 5000], '늘 이기는 수로 이긴다 → 여포 부대 기력 · 병력이 깎이고 내 부대 기력 +10 %s' % eff)
    B.shot(pg, 'y2_won', 200)
    pg.locator('#duel [data-x=close]').tap(); pg.wait_for_timeout(900)
    t2 = pg.evaluate('({ toast: $("toast").textContent, busy: UI.busy, du: !!DU, modal: !!MODAL })')
    ok('일기토!' in t2['toast'] and '하후돈 승' in t2['toast'] and not t2['busy'] and not t2['du'], '닫으면 결과가 뜨고 판으로 돌아온다 — ' + t2['toast'][:70])
    lg = pg.evaluate('G.log.slice(-3).map(function (x) { return x.t; })'); ok(any('일기토! 여포 대 하후돈' in x for x in lg), '기록에 남는다 — %s' % lg[-1][:60])
    # 떨어지면 없던 일
    pg.evaluate(RESET); pg.wait_for_timeout(200)
    gone = pg.evaluate('(() => { aiChallenge(UMAP[T.a], UMAP[T.d]); var n0 = duelAsks().length; placeUnit(UMAP[T.a], T.f[0] - 2, T.f[1]); var n1 = duelAsks().length, td = todoList().filter(function (x) { return x.go[0] === "duelask"; }).length; flowDuelAsk(T.a, T.d); var r = [n0, n1, td, !!MODAL, $("toast").textContent]; placeUnit(UMAP[T.a], T.f[0], T.f[1]); return r; })()')
    ok(gone[:4] == [1, 0, 0, False] and '지나간 신청' in gone[4], '두 부대가 떨어지면 없던 일이 된다 — ' + gone[4])
    # ================= 3. 열흘 재생에서 걸어온다 =================
    print('3. 열흘 재생: AI 가 제 차례에 걸어온다')
    pg.evaluate(RESET); pg.wait_for_timeout(200)
    pg.evaluate("""() => { var a = UMAP[T.a], d = UMAP[T.d]; d.done = true; DUEL_K.aiAsk = 100; UI.pspeed = 1; window._t0 = G.turn; window._cap = [];
      var _sc = setCaption; setCaption = function (f, h, c) { window._cap.push(String(h).replace(/<[^>]+>/g, '')); return _sc(f, h, c); }; clearSel(); syncScene(); }""")
    tapsel(pg, '#btnEnd'); pg.wait_for_timeout(300)
    if pg.evaluate('!UI.play && !MODAL'): tapsel(pg, '#btnEnd')
    if pg.evaluate('!!MODAL && !UI.play'): print('      (창)', head(pg), pg.evaluate('Array.prototype.map.call(document.querySelectorAll("#modal button"), function (b) { return (b.getAttribute("data-a") || "") + ":" + b.textContent.slice(0, 10); })'))
    pg.wait_for_timeout(600)
    try: pg.wait_for_function('G.turn > window._t0 && !UI.play && !UI.busy', timeout=240000)
    except Exception: print('      (재생이 끝나지 않음)')
    pg.evaluate('DUEL_K.aiAsk = 0'); pg.wait_for_timeout(600)
    caps = pg.evaluate('window._cap'); asked = [c for c in caps if '일기토 신청' in c]
    n = pg.evaluate('duelAsks().map(function (x) { return [uLeader(UMAP[x.a]).n, uLeader(UMAP[x.d]).n]; })')
    print('     ', asked[:3], n)
    ok(len(n) >= 1 and n[0] == ['여포', '하후돈'], 'AI 가 제 차례에 내 부대에 일기토를 걸어 두었다 %s' % n)
    ok(any('여포' in c and '내 차례에 답합니다' in c for c in asked), '재생 중에 그 장면이 자막으로 나온다 — %s' % (asked[0] if asked else ''))
    rep = head(pg); body = pg.evaluate('MODAL ? document.querySelector("#modal .dlg-b").innerText : ""')
    ok(rep == '지난 열흘의 일' and '일기토를 걸어왔다' in body, '지난 열흘의 일 — 중요한 일에 적힌다'); B.shot(pg, 'y3_report', 200)
    tapsel(pg, '#modal [data-a=close]'); 
    try: pg.wait_for_function('MODAL && document.querySelector("#modal .dlg-h h2").textContent.indexOf("일기토 신청") === 0', timeout=6000)
    except Exception: pass
    pg.wait_for_timeout(400)
    ok(head(pg) == '일기토 신청 — 여포', '요약을 닫으면 답하는 창이 저절로 뜬다 — ' + head(pg)); B.shot(pg, 'y3_auto', 200)
    m0 = pg.evaluate('UMAP[T.d].morale'); tapsel(pg, '#modal [data-a=no]'); pg.wait_for_timeout(400)
    ok(pg.evaluate('UMAP[T.d].morale') == m0 - 5 and pg.evaluate('duelAsks().length') == 0, '받지 않는다 → 기력 -5')
    # 결과 한 줄(AI 끼리의 일기토)
    rm = pg.evaluate("""[resultMsg('여포대', { kind: 'challenge', tname: '관우대', accepted: false, mor: 5 }), resultMsg('여포대', { kind: 'challenge', tname: '관우대', accepted: true, duel: { a: '여포', d: '관우', win: true, ko: true } }), resultMsg('여포대', { kind: 'challenge', tname: '관우대', accepted: true, duel: { a: '여포', d: '관우', draw: true } })]""")
    ok(rm == ['여포대 일기토 신청 → 관우대 — 받지 않음 (기력 -5)', '여포대 일기토 신청 → 관우대 — 여포 승(쓰러뜨림)', '여포대 일기토 신청 → 관우대 — 비김'], 'AI 끼리의 일기토 자막 — %s' % rm[1])
    # ================= 4. 출병 요청 =================
    print('4. 출병 요청')
    fresh(pg, 0, 1)
    D = pg.evaluate("""(() => { var b = facCities(G.player)[0]; b.gold = 30000; G.factions[G.player].ap = 250; window.BID = b.id; window._rnd = rnd; if (G.peace) G.peace.until = 0;
      var me = G.player, N = dipNbrs(), t = -1, x = -1, i, k;
      for (i = 0; i < G.factions.length && t < 0; i++) { if (i === me || !dipFac(i)) continue; for (k in N[i] || {}) if (+k !== me && dipFac(+k)) { t = i; x = +k; break; } }
      var other = -1; for (i = 0; i < G.factions.length; i++) if (i !== me && i !== t && i !== x && dipFac(i)) { other = i; break; }
      return { t: t, x: x, other: other, tn: facName(t), xn: facName(x), on: facName(other), nb: aimList(t).length }; })()""")
    print('     ', D)
    T_, X_, O_ = D['t'], D['x'], D['other']
    open_fac(pg, T_); c = pg.evaluate(CMDS)
    ok([q[0] for q in c] == ['gift', 'truce', 'ally', 'aim'] and c[3][2] and '동맹을 맺은 세력에게만' in c[3][1] and all(q[3] for q in c), '세력 창에 [출병 요청] — 동맹이 아니면 꺼져 있다: ' + c[3][1])
    tapsel(pg, '#modal [data-a=aim]'); pg.wait_for_timeout(300); ok('동맹을 맺은 세력에게만' in toast(pg) and head(pg) == D['tn'] + '군과의 외교', '눌러도 까닭만 알린다 — ' + toast(pg))
    pg.evaluate('(() => { dipSign(G.player, %d, "ally"); dipOf().rel[dipKey(G.player, %d)] = 80; refreshDialog(); })()' % (T_, T_)); pg.wait_for_timeout(300)
    c = pg.evaluate(CMDS)
    ok([q[0] for q in c] == ['gift', 'truce', 'ally', 'aim', 'brk'] and not c[3][2] and '칠 상대를 고릅니다' in c[3][1] and '행 15' in c[3][1] and all(q[3] for q in c), '동맹이면 켜진다 — ' + c[3][1])
    B.shot(pg, 'y4_fac', 200)
    tapsel(pg, '#modal [data-a=aim]'); pg.wait_for_timeout(400)
    rows = pg.evaluate("""Array.prototype.map.call(document.querySelectorAll('#modal .rows.dipl .row'), function (e) { return [+e.getAttribute('data-v'), e.innerText.replace(/\\n+/g, ' | '), e.classList.contains('off'), e.scrollWidth <= e.clientWidth + 1]; })""")
    ok(head(pg) == D['tn'] + '군에 출병 요청' and len(rows) == D['nb'] and any(q[0] == X_ and not q[2] and '받아들일 확률 최고' in q[1] for q in rows) and all(q[3] for q in rows), '칠 상대의 표: %s군과 이웃한 %d세력 — %s' % (D['tn'], len(rows), [q[1] for q in rows][:2]))
    ok('원군이 들어오는 것은 아닙니다' in pg.evaluate('document.querySelector("#modal .dlg-b").innerText'), '무엇을 청하는 것인지 적혀 있다(우리 성에 원군이 들어오는 것은 아니다)')
    fit = pg.evaluate(FIT); ok(fit and all(fit), '창이 화면 안에 들어온다 %s' % fit); B.shot(pg, 'y4_targets', 200)
    pg.locator('#modal .row[data-a=x][data-v="%d"]' % X_).tap(); pg.wait_for_timeout(400)
    ok('출병 요청' in head(pg) and D['xn'] in head(pg) and pg.evaluate('!!document.querySelector("#modal [data-a=auto]")'), '사신을 고르는 표 — ' + head(pg))
    tapsel(pg, '#modal [data-a=auto]'); pg.wait_for_timeout(300)
    pv = pg.evaluate('document.querySelector("#modal .pv").innerText'); pick = pg.evaluate('(() => { var e = document.querySelector("#modal .tr.sel"); return e ? +e.getAttribute("data-v") : -1; })()')
    q = pg.evaluate('(id) => aimTerms(G.player, %d, %d, off(id))' % (T_, X_), pick)
    best = pg.evaluate('Math.max.apply(null, idleOfficers(G.bases[BID]).map(function (o) { return aimTerms(G.player, %d, %d, o).p; }))' % (T_, X_))
    ok(q['p'] == best and ('받아들일 확률 %d%%' % q['p']) in pv and '우호 80' in pv and '바탕 −35' in pv, '[자동]은 확률이 가장 높은 사신 · 셈이 적힌다 — ' + pv.replace('\n', ' '))
    B.shot(pg, 'y4_pick', 200)
    # 거절
    pg.evaluate('(() => { rnd = function () { return 0.999; }; })()'); ap0 = pg.evaluate('G.factions[G.player].ap')
    tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(600); pg.evaluate('(() => { rnd = window._rnd; })()')
    st = pg.evaluate('[G.factions[G.player].ap, relOf(G.player, %d), dipAimOf(%d), !!MODAL]' % (T_, T_)); tk = talktx(pg)
    ok(st == [ap0 - 15, 78, -1, False] and '출병 요청을 물리쳤습니다' in tk and '60일 뒤에 다시' in tk, '거절: 행동력 15 · 우호 −2 · 60일 뒤에 다시 — ' + tk[:90])
    open_fac(pg, T_); c = pg.evaluate(CMDS); ok(c[3][2] and '뒤에 다시' in c[3][1], '단추에 언제 다시 청할 수 있는지 — ' + c[3][1])
    # 받아들임
    pg.evaluate('(() => { dipOf().cd = {}; G.factions[G.player].ap = 250; refreshDialog(); })()'); pg.wait_for_timeout(200)
    tapsel(pg, '#modal [data-a=aim]'); pg.wait_for_timeout(300); pg.locator('#modal .row[data-a=x][data-v="%d"]' % X_).tap(); pg.wait_for_timeout(300)
    tapsel(pg, '#modal [data-a=auto]'); pg.wait_for_timeout(200)
    pg.evaluate('(() => { rnd = function () { return 0; }; })()'); tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(600); pg.evaluate('(() => { rnd = window._rnd; })()')
    st = pg.evaluate('[dipAimOf(%d), dipAimLeft(%d), !!MODAL]' % (T_, T_)); tk = talktx(pg)
    ok(st == [X_, 9, False] and (D['xn'] + '군을 먼저 치기로 했습니다') in tk and '90일' in tk, '받아들임: 90일 동안 그 세력을 먼저 노린다 — ' + tk[:90])
    B.shot(pg, 'y4_yes', 200)
    open_fac(pg, T_); c = pg.evaluate(CMDS); px = pg.evaluate('(() => { var e = document.querySelector("#modal .diph .ds.px"); return e ? e.innerText : ""; })()')
    ok(c[3][2] and (D['xn'] + '군을 치기로 함') in c[3][1] and '90일 남음' in c[3][1] and (D['xn'] + '군을 치기로 함') in px, '세력 창: 단추와 머리에 치기로 한 상대 — ' + px)
    B.shot(pg, 'y4_fac_aim', 200)
    # ================= 5. AI 끼리의 협정 보기 =================
    print('5. AI 끼리의 협정')
    pg.evaluate('(() => { dipSign(%d, %d, "truce"); })()' % (X_, O_))
    open_dip(pg)
    rw = pg.evaluate("""(f) => { var e = document.querySelector('#modal .row[data-a=f][data-v="' + f + '"]'), p = e ? e.querySelector('.ds.px') : null; return [p ? p.innerText : '', e ? e.scrollWidth <= e.clientWidth + 1 : false]; }""", X_)
    ok((D['on'] + '군과 정전') in rw[0] and rw[1], '세력 표: 다른 세력끼리 맺은 협정이 적힌다 — ' + rw[0])
    rt = pg.evaluate("""(f) => { var e = document.querySelector('#modal .row[data-a=f][data-v="' + f + '"] .ds.px'); return e ? e.innerText : ''; }""", T_)
    ok((D['xn'] + '군을 치기로 함') in rt, '동맹의 줄에는 치기로 한 상대 — ' + rt)
    B.shot(pg, 'y5_list', 200)
    pg.locator('#modal .row[data-a=f][data-v="%d"]' % X_).tap(); pg.wait_for_timeout(400)
    px = pg.evaluate('(() => { var e = document.querySelector("#modal .diph .ds.px"); return e ? e.innerText : ""; })()')
    ok((D['on'] + '군과 정전 180일') in px, '세력 창에는 남은 기간까지 — ' + px); B.shot(pg, 'y5_fac', 200)
    # 달이 바뀔 때 AI 끼리 맺는 것(확률을 100 으로)
    mk = pg.evaluate("""(() => { var N = dipNbrs(), me = G.player, A = -1, Bf = -1, C = -1, i, j, c;
      for (i = 0; i < G.factions.length && A < 0; i++) for (j = i + 1; j < G.factions.length && A < 0; j++) for (c = 0; c < G.factions.length && A < 0; c++) if (i !== me && j !== me && c !== i && c !== j && dipFac(i) && dipFac(j) && dipFac(c) && !pactOn(i, j) && !pactOn(i, c) && !pactOn(j, c) && dipNear(i, j, N) && dipNear(i, c, N) && dipNear(j, c, N)) { A = i; Bf = j; C = c; }
      if (A < 0) return null;
      for (i = 0; i < G.factions.length; i++) if (dipFac(i)) { facBases(i).forEach(function (q, k) { q.troops = k ? 0 : 10000; }); facUnits(i).slice().forEach(function (u) { removeUnit(u); }); }
      facBases(C)[0].troops = 40000; DIP_K.aiPact = 100; var L0 = G.log.length; dipMonthAI(); DIP_K.aiPact = 0; syncScene();
      return { A: facName(A), B: facName(Bf), C: facName(C), on: pactOf(A, Bf) ? pactOf(A, Bf).t : '', log: G.log.slice(L0).map(function (x) { return x.t + '#' + x.imp; }) }; })()""")
    print('     ', mk)
    ok(mk and mk['on'] == 'truce' and any('정전하기로 했다' in x and x.endswith('#1') for x in mk['log']), '같은 큰 적을 둔 이웃끼리 정전한다 → 지난 열흘의 요약(천하의 움직임)에 적힌다 — %s' % (mk and mk['log'][:1]))
    # ================= 6. 도움말 · 작은 화면 =================
    print('6. 도움말 · 작은 화면')
    pg.evaluate('closeDialog()'); t = pg.evaluate('HELP_HTML.replace(/<[^>]+>/g, " ")')
    need = ['AI 도 일기토를 걸어옵니다', '출병 요청', 'AI 끼리도 손을 잡습니다']
    ok(all(x in t for x in need), '도움말: %s' % [x for x in need if x not in t])
    tail = t[t.index('이번 판에 아직 없는 것'):]; ok('외교' not in tail, '「아직 없는 것」에서 외교를 뺐다 — ' + tail[:60].strip())
    pg.set_viewport_size({'width': 360, 'height': 640}); pg.wait_for_timeout(400)
    S2 = pg.evaluate(SETUP)
    pg.evaluate('(() => { aiChallenge(UMAP[T.a], UMAP[T.d]); flowDuelAsk(T.a, T.d); })()'); pg.wait_for_timeout(500)
    d = pg.evaluate(ASKDLG); fit = pg.evaluate(FIT)
    ok(d and d['head'] == '일기토 신청 — 여포' and all(c[2] for c in d['cards']) and fit and fit[0] and fit[1], '작은 화면(360×640): 답하는 창이 넘치지 않는다 %s' % fit); B.shot(pg, 'y6_small_ask', 200)
    pg.evaluate('closeDialog()')
    pg.evaluate('(() => { window.BID = facCities(G.player)[0].id; })()'); open_fac(pg, T_); c = pg.evaluate(CMDS); fit = pg.evaluate(FIT)
    ok(all(q[3] for q in c) and fit and fit[0] and fit[1], '작은 화면: 세력 창의 단추 글씨가 넘치지 않는다 %s' % fit); B.shot(pg, 'y6_small_fac', 200)
    pg.evaluate('closeDialog()')
B.run(steps, 390, 844, 2)
errs = [e for e in B.errors if 'GPU stall' not in e and 'GL Driver' not in e and 'ERR_FILE_NOT_FOUND' not in e and 'willReadFrequently' not in e]
print('console errors:', errs[:6])
print('FAILS %d' % len(fails), fails)
sys.exit(1 if fails or errs else 0)
