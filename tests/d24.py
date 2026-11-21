# v0.13 — 화면 조작으로 확인: 일기토 신청 · 일기토 화면(수 고르기 · 맡기기) · 공격에서 벌어진 일기토 · 지난 열흘의 일기토 다시 보기 · 설전으로 등용
#   python3 tests/d24.py          찍은 그림은 tests/shots26/
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import taphex, tapsel
B.SHOTS = os.path.join(B.ROOT, 'shots26')
os.makedirs(B.SHOTS, exist_ok=True)
fails = []
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)
def toast(pg): return pg.evaluate('$("toast").textContent')
def head(pg): return pg.evaluate('MODAL ? document.querySelector("#modal .dlg-h").textContent.replace("×", "") : ""')
def reload(pg):
    pg.reload(); pg.wait_for_function('window.R3 && R3.ready', timeout=60000); pg.wait_for_timeout(600)
def fresh(pg, fac, seed):
    pg.evaluate('([f, s]) => { localStorage.clear(); newGame(f, s); saveGame(); }', [fac, seed]); reload(pg)
    tapsel(pg, '#tCont'); pg.wait_for_timeout(1300)
    if pg.evaluate('!!MODAL'): pg.evaluate('closeDialog()')
    pg.evaluate('talkHide()'); pg.wait_for_timeout(200)
SETUP = '''() => {
  function field() { for (var r = 92; r < 112; r++) for (var c = 146; c < 168; c++) { var good = true; for (var dr = -2; dr <= 2 && good; dr++) for (var dc = -3; dc <= 3 && good; dc++) { var k = K(c + dc, r + dr); if (TCH[k] !== 112 || ZONE[k] >= 0 || BAT[k] !== undefined || PAT[k] || UAT[k]) good = false; } if (good) return [c, r]; } return null; }
  var f = field(), b = facBases(G.player)[0], eb = G.bases[baseByName('복양')];
  b.w.spear = 30000; b.troops = 60000; b.food = 200000; G.factions[G.player].ap = 250; eb.troops = 60000; eb.w.spear = 30000; eb.food = 200000; G.factions[eb.owner].ap = 250;
  if (G.peace) G.peace.until = 0;
  var me = G.officers.filter(function (o) { return o.n === '하후돈'; })[0], foe = idleOfficers(eb).sort(function (x, y) { return y.war - x.war; })[0];
  var a = cmdDeploy(b, { type: 'spear', ids: [me.id], troops: 5000, food: 5000 }).unit, d = cmdDeploy(eb, { type: 'spear', ids: [foe.id], troops: 5000, food: 5000 }).unit;
  placeUnit(a, f[0], f[1]); placeUnit(d, f[0] + 1, f[1]);
  [a, d].forEach(function (u) { u.born = -9; u.done = false; u.mp = uMaxMp(u); u.morale = 80; });
  window.T = { a: a.id, d: d.id, f: f };
  EVQ.length = 0; clearSel(); syncScene(); jumpTo(f[0], f[1], 1.5); requestDraw();
  return { a: uName(a), d: uName(d), wa: me.war, wd: foe.war, ia: me.int, id: foe.int, f: f };
}'''
RESET = '''() => { var a = UMAP[T.a], d = UMAP[T.d]; [a, d].forEach(function (u) { u.troops = 5000; u.morale = 80; u.status = null; u.done = false; u.mp = uMaxMp(u); u.ox = -1; }); clearSel(); syncScene(); selectUnit(a, true); UI.target = { kind: 'unit', u: d, c: d.c, r: d.r }; refreshSheet(); }'''
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
    return seen
def steps(pg):
    fresh(pg, 0, 1)
    S = pg.evaluate(SETUP); print('     ', S)
    # ================= 1. 일기토 신청 =================
    print('1. 일기토 신청')
    pg.evaluate(RESET); pg.wait_for_timeout(400)
    acts = pg.evaluate('Array.prototype.map.call(document.querySelectorAll("#sheet .acts .act"), function (e) { return e.innerText.replace(/\\n+/g, " | ") + (e.classList.contains("off") ? " (off)" : ""); })')
    ch = [a for a in acts if a.startswith('일기토')]
    p = pg.evaluate('challengeChance(UMAP[T.a], UMAP[T.d])')
    ok(len(ch) == 1 and ('응할 확률 %d%%' % p) in ch[0] and ('무력 %d : %d' % (S['wa'], S['wd'])) in ch[0] and '(off)' not in ch[0], '대상 창에 [일기토]: %s' % ch)
    ok(pg.evaluate('(() => { var all = document.querySelectorAll("#sheet .acts .act"), bad = 0; for (var i = 0; i < all.length; i++) if (all[i].scrollWidth > all[i].clientWidth + 1) bad++; return bad; })()') == 0, '단추 글씨가 넘치지 않는다')
    B.shot(pg, 'u1_target', 200)
    # 응하지 않을 때
    pg.evaluate('(() => { window._cr = challengeRoll; challengeRoll = function () { return 99.9; }; })()')
    pg.locator('#sheet .acts .act', has_text='일기토').first.tap(); pg.wait_for_timeout(900)
    r = pg.evaluate('({ du: !!DU, a: [UMAP[T.a].morale, UMAP[T.a].done], d: UMAP[T.d].morale, talk: $("talk").innerText.replace(/\\n+/g, " | "), busy: UI.busy })')
    ok(not r['du'] and r['a'] == [70, True] and r['d'] == 75 and '받지 않았습니다' in r['talk'] and not r['busy'], '응하지 않으면: 화면 없이 알린다 · 내 기력 -10 · 상대 기력 -5 — ' + r['talk'])
    B.shot(pg, 'u1_refused', 300)
    # 응할 때: 화면이 열린다
    pg.evaluate('talkHide(); challengeRoll = function () { return 0; };'); pg.evaluate(RESET); pg.wait_for_timeout(300)
    pg.locator('#sheet .acts .act', has_text='일기토').first.tap(); pg.wait_for_timeout(900)
    st = pg.evaluate(DU_STATE)
    ok(st and st['on'] and st['kind'] == 'duel' and st['seal'] == '일기토' and st['round'] == '제1합 / 5' and st['hp'] == [100, 100] and st['moves'] == ['맹공', '방어', '필살'], '일기토 화면: %s' % {k: st[k] for k in ('seal', 'round', 'names', 'st', 'hp', 'moves')} if st else 'None')
    ok(st['names'][0].startswith('하후돈') and '나' in st['names'][0] and ('%d' % S['wa']) in st['st'][0] and ('%d' % S['wd']) in st['st'][1] and st['plan']['a'] is None and st['plan']['d'] in ('atk', 'def', 'sp'), '왼쪽이 나(하후돈) · 무력이 적혀 있다 · 상대의 수는 미리 정해져 있다')
    rd = pg.evaluate('duelRead(DU.S, "a")')
    ok('기색' in st['hint'] and ('읽기 %d%%' % rd) in st['hint'] and st['fit'][0] and st['fit'][1], '기색과 읽을 확률(%d%%) · 화면 안에 다 들어온다 %s — %s' % (rd, st['fit'], st['hint']))
    B.shot(pg, 'u2_duel_start', 200)
    # 한 합: 상대의 수를 이기는 수를 낸다 → 상대만 깎인다
    BEAT = {'atk': '방어', 'def': '필살', 'sp': '맹공'}
    plan_d = st['plan']['d']
    pg.locator('#duel .du-mv:has(b:text-is("%s"))' % BEAT[plan_d]).first.tap(); pg.wait_for_timeout(700)
    mid = pg.evaluate('({ g: [$("duGa").textContent, $("duGd").textContent], off: $("duMoves").classList.contains("off"), log: DU.S.log[0] })')
    ok(mid['g'][0] in ('攻', '守', '必') and mid['g'][1] in ('攻', '守', '必') and mid['off'] and mid['log']['win'] == 'a' and mid['log']['toA'] == 0 and mid['log']['toD'] > 0, '수가 드러나고, 이기는 수를 냈으니 상대만 깎인다 %s' % mid['log'])
    B.shot(pg, 'u2_duel_clash', 0)
    pg.wait_for_function('DU && (DU.ended || !DU.busy)', timeout=8000); pg.wait_for_timeout(300)
    st2 = pg.evaluate(DU_STATE)
    ok(st2['hp'][0] == 100 and st2['hp'][1] == 100 - mid['log']['toD'] and (st2['ended'] or st2['round'] == '제2합 / 5'), '힘 막대가 줄고 다음 합으로: %s %s' % (st2['hp'], st2['round']))
    # 끝까지: 늘 이기는 수 → 내가 이긴다
    seen = play_out(pg, lambda s: BEAT[s['plan']['d']])
    end = pg.evaluate(DU_STATE)
    ok(end['over'] and end['win'] == 'a' and '하후돈 승' in end['res'] and '기력' in end['res'] and '확인' in end['res'], '끝: %s' % end['res'])
    eff = pg.evaluate('({ a: [UMAP[T.a].morale, UMAP[T.a].troops], d: UMAP[T.d] ? [UMAP[T.d].morale, UMAP[T.d].troops, UMAP[T.d].status] : null, done: DU.S.done, stamp: (document.querySelector("#duel .du-stamp") || {}).textContent })')
    wantD = [80 - (35 if end['ko'] else 25), 5000 - (600 if end['ko'] else 400), 'confuse' if end['ko'] else None]
    ok(eff['done'] and eff['a'] == [80, 5000] and eff['d'] == wantD and eff['stamp'] == '勝', '결과가 부대에 입혀졌다: 내 부대 기력 70 → +10, 상대 %s (쓰러뜨림 %s)' % (eff['d'], end['ko']))
    B.shot(pg, 'u2_duel_end', 300)
    pg.locator('#duel [data-x=close]').tap(); pg.wait_for_timeout(600)
    after = pg.evaluate('({ du: !!DU, on: $("duel").classList.contains("on"), busy: UI.busy, done: UMAP[T.a].done, toast: $("toast").textContent })')
    ok(not after['du'] and not after['on'] and not after['busy'] and after['done'] and '일기토' in after['toast'] and '승' in after['toast'], '[확인] → 닫히고 행동이 끝난다 — ' + after['toast'])
    # 맡기기
    pg.evaluate(RESET); pg.wait_for_timeout(300)
    pg.locator('#sheet .acts .act', has_text='일기토').first.tap(); pg.wait_for_timeout(900)
    pg.locator('#duel [data-x=auto]').tap()
    pg.wait_for_function('DU && DU.ended', timeout=20000); pg.wait_for_timeout(400)
    au = pg.evaluate(DU_STATE)
    ok(au['over'] and au['res'] and au['log'] >= 1, '[맡기기]: 끝까지 저절로 겨룬다(%d합) — %s' % (au['log'], au['res'][:40]))
    pg.locator('#duel [data-x=close]').tap(); pg.wait_for_timeout(500)
    # 지는 판: 늘 지는 수
    LOSE = {'atk': '필살', 'def': '맹공', 'sp': '방어'}
    pg.evaluate(RESET); pg.wait_for_timeout(300)
    pg.locator('#sheet .acts .act', has_text='일기토').first.tap(); pg.wait_for_timeout(900)
    play_out(pg, lambda s: LOSE[s['plan']['d']])
    lost = pg.evaluate(DU_STATE)
    effL = pg.evaluate('UMAP[T.a] ? [UMAP[T.a].morale, UMAP[T.a].troops, UMAP[T.a].status] : null')
    ok(lost['win'] == 'd' and (document_has := pg.evaluate('!!document.querySelector("#duel .du-resin.lost") && document.querySelector("#duel .du-stamp").textContent === "敗"')) and effL == [70 - (35 if lost['ko'] else 25), 5000 - (600 if lost['ko'] else 400), 'confuse' if lost['ko'] else None], '지면: 敗 · 내 부대가 깎인다 %s' % effL)
    B.shot(pg, 'u2_duel_lost', 200)
    pg.locator('#duel [data-x=close]').tap(); pg.wait_for_timeout(500)

    # ================= 2. 공격에서 벌어진 일기토 =================
    print('2. 공격에서 벌어진 일기토')
    pg.evaluate('(() => { challengeRoll = window._cr; window._rate = DUEL_K.rate; DUEL_K.rate = 100; UI.pspeed = 1; })()')
    pg.evaluate(RESET); pg.wait_for_timeout(300)
    pg.evaluate('doAct({ kind: "attack" })')
    pg.wait_for_function('!!DU', timeout=15000); pg.wait_for_timeout(700)
    st = pg.evaluate(DU_STATE)
    ok(st['on'] and st['r'] == 0 and st['hp'] == [100, 100] and pg.evaluate('UMAP[T.a].morale === 80 && UMAP[T.d].morale === 80'), '공격 연출이 끝난 뒤 일기토 화면이 열린다(아직 아무것도 입혀지지 않았다)')
    play_out(pg, lambda s: BEAT[s['plan']['d']])
    pg.locator('#duel [data-x=close]').tap(); pg.wait_for_timeout(900)
    t2 = pg.evaluate('({ toast: $("toast").textContent, busy: UI.busy, du: !!DU })')
    ok('일기토!' in t2['toast'] and '하후돈 승' in t2['toast'] and not t2['busy'] and not t2['du'], '닫으면 결과의 말에 일기토가 붙는다 — ' + t2['toast'][:90])

    # ================= 3. 지난 열흘의 일기토 다시 보기 =================
    print('3. 다시 보기')
    rec = pg.evaluate('''() => { var a = UMAP[T.a], d = UMAP[T.d]; [a, d].forEach(function (u) { u.troops = 5000; u.morale = 80; u.status = null; u.done = false; });
      var res = unitAttack(d, { kind: 'unit', u: a, c: a.c, r: a.r }); window._res = res; EVQ.length = 0;
      return { has: !!res.duelRec, duel: res.duel, n: res.duelRec ? res.duelRec.log.length : 0, noS: res.duelS === undefined }; }''')
    ok(rec['has'] and rec['duel'] and rec['n'] >= 1 and rec['noS'], 'AI 가 건 싸움의 일기토는 저절로 끝나고 기록이 남는다(%d합)' % rec['n'])
    pg.evaluate('(() => { window._done = 0; duelReplay(_res.duelRec, { sub: "다시 보기", out: duelOutHtml(null, _res.duel, "가", "나") }, function () { window._done = 1; }); })()')
    pg.wait_for_timeout(900)
    rp = pg.evaluate(DU_STATE)
    ok(rp['on'] and rp['moves'] == [] and pg.evaluate('!document.querySelector("#duel [data-x=auto]")') and any('나' in n for n in rp['names']), '다시 보기: 수를 고르는 단추가 없고, 내 주장 쪽에 표시가 있다 %s' % rp['names'])
    pg.wait_for_function('DU && DU.ended', timeout=30000); pg.wait_for_timeout(300)
    rp2 = pg.evaluate(DU_STATE)
    ok(rp2['log'] == 0 and rp2['hp'] == pg.evaluate('(() => { var L = _res.duelRec.log, x = L[L.length - 1]; return [x.hpA, x.hpD]; })()') and ('승' in rp2['res'] or '비김' in rp2['res']), '적힌 합을 그대로 그린다(주사위를 굴리지 않는다) — ' + rp2['res'][:50])
    B.shot(pg, 'u3_replay_end', 200)
    pg.wait_for_function('!DU', timeout=8000)
    ok(pg.evaluate('window._done') == 1, '잠시 뒤 저절로 닫히고 다음으로 넘어간다')
    # 실제 열흘 재생에서: 적 부대가 내 부대를 치게 두고 턴을 넘긴다
    pg.evaluate('''() => { var a = UMAP[T.a], d = UMAP[T.d]; a.troops = 3000; d.troops = 9000; [a, d].forEach(function (u) { u.morale = 80; u.status = null; u.done = false; }); a.done = true; UI.pspeed = 1; window._rp = 0; window._t0 = G.turn;
      var _r = duelReplay; duelReplay = function (rec, o, done) { window._rp++; window._rpSub = o.sub; return _r(rec, o, done); }; clearSel(); syncScene(); }''')
    tapsel(pg, '#btnEnd'); pg.wait_for_timeout(300)
    if pg.evaluate('!UI.play && !MODAL'): tapsel(pg, '#btnEnd')
    if pg.evaluate('!!MODAL'): print('      (창)', pg.evaluate('document.querySelector("#modal .dlg-h").textContent'), pg.evaluate('Array.prototype.map.call(document.querySelectorAll("#modal button"), function (b) { return (b.getAttribute("data-a") || "") + ":" + b.textContent.slice(0, 10); })'))
    pg.wait_for_timeout(600)
    try: pg.wait_for_function('window._rp > 0 || (G.turn > window._t0 && !UI.play && !UI.busy)', timeout=120000)
    except Exception: pass
    hit = pg.evaluate('({ rp: window._rp, sub: window._rpSub || "", du: !!DU, play: !!UI.play })')
    print('     ', hit)
    ok(hit['rp'] >= 1 and hit['du'], '열흘 재생 도중: 내 부대가 얽힌 일기토가 화면으로 나온다 — ' + hit['sub'])
    if hit['du']:
        B.shot(pg, 'u3_replay_in_play', 900)
        pg.wait_for_function('!DU', timeout=40000)
    pg.wait_for_function('!UI.play', timeout=120000); pg.wait_for_timeout(800)
    if pg.evaluate('!!MODAL'): pg.evaluate('closeDialog()')
    ok(pg.evaluate('!UI.play && !DU && !UI.busy'), '재생이 끝까지 이어진다')
    pg.evaluate('DUEL_K.rate = window._rate; talkHide()')

    # ================= 4. 설전으로 등용 =================
    print('4. 설전')
    fresh(pg, 0, 1)
    R = pg.evaluate('''() => { var b = facCities(G.player)[0], free = G.officers.filter(function (o) { return o.st === 'free' || o.st === 'hidden'; }), out = [];
      G.factions[G.player].ap = 250;
      for (var i = 0; i < free.length && out.length < 3; i++) { var t = free[i]; t.st = 'free'; t.loc = b.id; var x = bestRecruiter(b, t); if (x.p >= 10 && x.p < 100) out.push({ id: t.id, n: t.n, p: x.p, int: t.int }); else { t.st = 'hidden'; } }
      window.RB = b.id; return out; }''')
    print('     ', R)
    ok(len(R) >= 2, '설전을 걸 만한 재야 무장이 있다')
    def open_pick(tid):
        pg.evaluate('(() => { closeDialog(); flowRecruit(G.bases[RB]); })()'); pg.wait_for_timeout(400)
        pg.locator('#modal .row[data-v="%d"]' % tid).tap(); pg.wait_for_timeout(400)
    open_pick(R[0]['id'])
    ok(pg.evaluate('!!document.querySelector("#modal [data-a=alt]") && document.querySelector("#modal [data-a=alt]").textContent') == '설전', '보낼 무장을 고르는 표에 [설전]')
    pg.locator('#modal [data-a=alt]').tap(); pg.wait_for_timeout(300)
    ok('무장을 먼저' in toast(pg) and not pg.evaluate('!!DU'), '무장을 고르기 전에는 걸 수 없다')
    tapsel(pg, '#modal [data-a=auto]'); pg.wait_for_timeout(300)
    B.shot(pg, 'u4_pick', 200)
    sender = pg.evaluate('(() => { var e = document.querySelector("#modal .tr.sel"); return e ? +e.getAttribute("data-v") : -1; })()')
    ap0 = pg.evaluate('G.factions[G.player].ap')
    pg.evaluate('(() => { window._dp = duelPick; duelPick = function (S, side) { return S.kind === "talk" && side === "d" ? "gain" : window._dp(S, side); }; })()')      # 상대는 늘 '이해' → '도리'로 이긴다
    pg.locator('#modal [data-a=alt]').tap(); pg.wait_for_timeout(900)
    st = pg.evaluate(DU_STATE)
    want_hp = pg.evaluate('([s, t]) => Math.round(100 * (1 + (60 - recruitChance(G.bases[RB], off(s), off(t))) / 100))', [sender, R[0]['id']])
    ok(st and st['kind'] == 'talk' and st['seal'] == '설전' and st['moves'] == ['도리', '이해', '시세'] and st['hp'] == [100, want_hp] and '지력' in st['st'][0] and not pg.evaluate('!!MODAL'), '설전 화면: 지력으로 겨루고, 상대의 버티는 힘은 %d — %s' % (want_hp, st['hint']) if st else 'None')
    ok(st['fit'][0] and st['fit'][1], '화면 안에 다 들어온다')
    B.shot(pg, 'u4_talk_start', 200)
    play_out(pg, lambda s: '도리')
    end = pg.evaluate(DU_STATE)
    j = pg.evaluate('([t]) => ({ f: off(t).f, st: off(t).st, ap: G.factions[G.player].ap })', [R[0]['id']])
    ok(end['win'] == 'a' and '합류했습니다' in end['res'] and j['f'] == 0 and j['st'] == 'active' and j['ap'] < ap0, '이기면 합류한다 — ' + end['res'][:70])
    B.shot(pg, 'u4_talk_won', 300)
    pg.locator('#duel [data-x=close]').tap(); pg.wait_for_timeout(700)
    ok(not pg.evaluate('!!DU') and not pg.evaluate('UI.busy'), '닫힌다')
    pg.evaluate('talkHide()')
    # 지는 설전
    open_pick(R[1]['id']); tapsel(pg, '#modal [data-a=auto]'); pg.wait_for_timeout(300)
    pg.locator('#modal [data-a=alt]').tap(); pg.wait_for_timeout(900)
    play_out(pg, lambda s: '시세')                                   # 상대의 '이해'가 '시세'를 이긴다
    end2 = pg.evaluate(DU_STATE)
    j2 = pg.evaluate('([t]) => ({ f: off(t).f, st: off(t).st, wait: askWait(off(t)) })', [R[1]['id']])
    ok(end2['win'] == 'd' and '뜻을 굽히지 않았습니다' in end2['res'] and j2['f'] != 0 and j2['wait'], '지면 거절 · 다시 권하려면 기다려야 한다 — ' + end2['res'][:70])
    pg.locator('#duel [data-x=close]').tap(); pg.wait_for_timeout(600)
    pg.evaluate('(() => { duelPick = window._dp; })()')
    # 걸 수 없는 상대: 확률이 100% 이거나 10% 아래
    blocked = pg.evaluate('''() => { var b = G.bases[RB], t = G.officers.filter(function (o) { return o.st === 'hidden'; })[0]; t.st = 'free'; t.loc = b.id; var o = idleOfficers(b)[0];
      var _rc = recruitChance; recruitChance = function () { return 100; }; var a = talkRecruitOk(b, o, t); recruitChance = function () { return 9; }; var c = talkRecruitOk(b, o, t); recruitChance = _rc; return [a, c]; }''')
    ok(blocked == [False, False], '확률이 100% 이거나 10% 아래면 설전을 걸 수 없다')

    # ================= 5. 도움말 · 작은 화면 =================
    print('5. 도움말')
    pg.evaluate('closeDialog(); showHelp()'); pg.wait_for_timeout(300)
    hp_ = pg.evaluate('document.querySelector("#modal").textContent')
    need = ['맹공은 필살을 이기고', '기색', '도리는 이해를', '설전', '응하지 않으면']
    ok(all(n in hp_ for n in need) and '직접 조작하는 일기토·설전' not in hp_, '도움말: %s' % [n for n in need if n not in hp_])
    pg.evaluate('closeDialog()')
B.run(steps, 390, 844, 2)
errs = [e for e in B.errors if 'GPU stall' not in e and 'GL Driver' not in e and 'ERR_FILE_NOT_FOUND' not in e and 'willReadFrequently' not in e]
print('console errors:', errs[:6])
print('FAILS %d' % len(fails), fails)
sys.exit(1 if fails or errs else 0)
