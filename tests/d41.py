# v0.24 — 지난 열흘에 벌어진 일기토(내 부대가 얽힌 것)를 다시 그려 보일 때: '일기토 패' 글씨와 승패의 말은 일기토 화면이 닫힌 뒤에.
#   요청(11-25 19:00): "일기토가 시작될 때 일기토 패 라는 글씨가 나오던데.. 버그 같네? 일기토는 시작도 안 했는데."
#   python3 tests/d41.py          찍은 그림은 tests/shots41/
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import tapsel
B.SHOTS = os.path.join(B.ROOT, 'shots41')
os.makedirs(B.SHOTS, exist_ok=True)
fails = []
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)
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
  window.T = { a: a.id, d: d.id, f: f, me: me.id, foe: foe.id };
  DUEL_K.rate = 100; challengeRoll = function () { return 0; };
  EVQ.length = 0; clearSel(); syncScene(); jumpTo(f[0], f[1], 1.5); requestDraw();
  return { a: uName(a), d: uName(d), mine: a.f === G.player, foe: d.f !== G.player };
}'''
# 적 부대(d)가 내 부대(a)를 친다(kind = attack) / 일기토를 건다(challenge) → 그 일을 '지난 열흘'처럼 그려 보인다(presentEvent)
RUN = '''([kind, meWar, foeWar]) => {
  var a = UMAP[T.a], d = UMAP[T.d], me = off(T.me), foe = off(T.foe);
  if (!a || !d) return { ok: false, msg: "부대가 없다" };
  [a, d].forEach(function (u) { u.troops = 5000; u.morale = 80; u.status = null; u.done = false; u.mp = uMaxMp(u); });
  me.war = meWar; foe.war = foeWar; syncScene(); EVQ.length = 0;
  var t = { kind: "unit", u: a, c: a.c, r: a.r }, res = kind === "challenge" ? unitChallenge(d, t) : unitAttack(d, t);
  var e = EVQ.filter(function (x) { return x.t === "act"; })[0]; EVQ.length = 0;
  if (!res.ok || !e) return { ok: false, msg: res.msg || "기록된 일이 없다" };
  e.cls = 2;
  UI.play = { next: null, skip: false, cam0: { x: cam.x, y: cam.y, z: cam.z }, timer: 0, wake: null, ans: [], batch: [], err: null, minor: 0, shown: 0, save0: null, rest: [] };
  UI.busy = true; $("app").classList.add("playing");
  window._tl = []; window._pdone = 0;
  window._iv = setInterval(function () { _tl.push({ t: Math.round(performance.now()), du: !!DU, flt: FLT().length, cap: $("plMsg").textContent }); }, 25);
  presentEvent(e, function () { window._pdone = 1; });
  return { ok: true, duel: res.duel, rec: !!res.duelRec, accepted: res.accepted, kind: res.kind || "" };
}'''
FLT = '''(() => { window.FLT = function () { return Array.prototype.filter.call(document.querySelectorAll("#fx .flt"), function (x) { return x.textContent.indexOf("일기토 패") >= 0; }).map(function (x) { return x.textContent; }); }; })()'''
STOP = '''() => { clearInterval(window._iv); var tl = window._tl; UI.play = null; UI.busy = false; $("app").classList.remove("playing");
  var firstDu = -1, lastDu = -1, firstFlt = -1, i;
  for (i = 0; i < tl.length; i++) { if (tl[i].du) { if (firstDu < 0) firstDu = i; lastDu = i; } if (tl[i].flt && firstFlt < 0) firstFlt = i; }
  return { n: tl.length, firstDu: firstDu, lastDu: lastDu, firstFlt: firstFlt, capBefore: firstDu > 0 ? tl[firstDu - 1].cap : "", capDuring: lastDu >= 0 ? tl[lastDu].cap : "", capEnd: tl.length ? tl[tl.length - 1].cap : "" }; }'''
def replay_case(pg, tag, kind, me_war, foe_war, loser_mine):
    r = pg.evaluate(RUN, [kind, me_war, foe_war]); print('     ', tag, r)
    ok(r.get('ok') and r.get('rec') and r.get('duel') and not r['duel']['draw'], '%s: 일기토가 벌어지고 기록이 남는다(비기지 않음)' % tag)
    if not r.get('ok'): return
    pg.wait_for_function('!!DU', timeout=30000); pg.wait_for_timeout(350)
    at_open = pg.evaluate('({ flt: FLT(), cap: $("plMsg").textContent, seen: _tl.filter(function (x) { return x.flt; }).length })')
    ok(at_open['flt'] == [] and at_open['seen'] == 0, "%s: 일기토 화면이 열릴 때까지 '일기토 패' 글씨가 없다 — %s" % (tag, at_open['flt']))
    ok('승' not in at_open['cap'] and '비김' not in at_open['cap'] and ('일기토!' in at_open['cap'] or '응함' in at_open['cap']), '%s: 그때의 말에는 승패가 없다 — %s' % (tag, at_open['cap'][:70]))
    B.shot(pg, 'u_%s_open' % tag, 300)
    pg.wait_for_function('DU && DU.ended', timeout=90000)
    mid = pg.evaluate('({ flt: FLT(), cap: $("plMsg").textContent })')
    ok(mid['flt'] == [] and '승' not in mid['cap'], "%s: 일기토가 끝난 화면이 떠 있는 동안에도 지도에는 아직 없다 — %s" % (tag, mid['cap'][:60]))
    pg.wait_for_function('!DU', timeout=20000)                                 # 다시 보기는 2.6초 뒤에 저절로 닫힌다
    try: pg.wait_for_function('FLT().length > 0', timeout=5000)
    except Exception: pass
    after = pg.evaluate('({ flt: FLT(), cap: $("plMsg").textContent })')
    ok(len(after['flt']) == 1 and '승' in after['cap'], "%s: 화면이 닫힌 뒤에 '일기토 패' 글씨와 승패의 말이 나온다 — %s · %s" % (tag, after['flt'], after['cap'][:70]))
    B.shot(pg, 'u_%s_after' % tag, 250)
    pg.wait_for_function('window._pdone === 1', timeout=15000)
    tl = pg.evaluate(STOP)
    ok(tl['firstDu'] >= 0 and tl['firstFlt'] > tl['lastDu'], "%s: 차례 — 일기토 화면(%d ~ %d번째 눈금)이 먼저, 글씨(%d)는 그 뒤" % (tag, tl['firstDu'], tl['lastDu'], tl['firstFlt']))
    mine_lost = bool(r['duel']['win'])                                            # duel.win = 건 쪽(여기서는 적)이 이겼다
    ok(mine_lost == loser_mine, '%s: 바란 쪽이 졌다(내 부대가 %s)' % (tag, '짐' if loser_mine else '이김'))
def steps(pg):
    fresh(pg, 0, 1)
    pg.evaluate(FLT)
    S = pg.evaluate(SETUP); print('     ', S)
    ok(S['mine'] and S['foe'], '시험 부대: 내 부대와 적 부대가 맞붙어 있다')
    pg.wait_for_timeout(500)
    print('1. 적이 내 부대를 쳐서 벌어진 일기토 — 내가 이긴다')
    replay_case(pg, 'atk_win', 'attack', 100, 76, False)
    print('2. 적이 내 부대를 쳐서 벌어진 일기토 — 내가 진다')
    replay_case(pg, 'atk_lose', 'attack', 76, 100, True)
    print('3. 적이 건 일기토(신청)')
    replay_case(pg, 'chal', 'challenge', 100, 76, False)
    print('4. 연출 사이에 건너뛰기를 누르면: 화면 없이 결과만')
    r = pg.evaluate(RUN, ['attack', 100, 76]); print('     ', r)
    pg.evaluate('(() => { UI.play.skip = true; })()')
    pg.wait_for_function('window._pdone === 1', timeout=30000)
    sk = pg.evaluate('({ flt: FLT(), cap: $("plMsg").textContent, du: !!DU })')
    tl = pg.evaluate(STOP)
    ok(r.get('ok') and tl['firstDu'] < 0 and not sk['du'] and len(sk['flt']) == 1 and '승' in sk['cap'], "건너뛰면 일기토 화면은 뜨지 않고 '일기토 패' 글씨와 승패의 말이 바로 나온다 — %s · %s" % (sk['flt'], sk['cap'][:70]))
    print('5. 내가 얽히지 않은 일(다시 그려 보이지 않는 일)은 예전 그대로')
    plain = pg.evaluate('''() => { var a = UMAP[T.a], d = UMAP[T.d]; [a, d].forEach(function (u) { u.troops = 5000; u.morale = 80; u.status = null; u.done = false; });
      off(T.me).war = 100; off(T.foe).war = 76; EVQ.length = 0;
      var res = unitAttack(d, { kind: "unit", u: a, c: a.c, r: a.r }); EVQ.length = 0;
      return { full: resultMsg("가", res), hid: resultMsg("가", res, true), duel: !!res.duel }; }''')
    ok(plain['duel'] and '승' in plain['full'] and '승' not in plain['hid'] and '일기토!' in plain['hid'], '결과의 말: 그대로 부르면 승패까지, 가리면 "일기토!" 까지 — %s / %s' % (plain['full'][-34:], plain['hid'][-20:]))
B.run(steps, 390, 844, 2)
errs = [e for e in B.errors if 'GPU stall' not in e and 'GL Driver' not in e and 'ERR_FILE_NOT_FOUND' not in e and 'willReadFrequently' not in e]
print('console errors:', errs[:6])
print('FAILS %d' % len(fails), fails)
sys.exit(1 if fails or errs else 0)
