# v0.13 — 화면에서 확인: 중국어 음성(소리 120개가 풀리는지 · 목소리 갈래 · 겹칠 때의 차례 · 대화창과 싸움에 붙는 것 · 뜻풀이 · 켜고 끄기)
#   python3 tests/d25.py          찍은 그림은 tests/shots27/
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import taphex, tapsel
B.SHOTS = os.path.join(B.ROOT, 'shots27')
os.makedirs(B.SHOTS, exist_ok=True)
fails = []
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)
def toast(pg): return pg.evaluate('$("toast").textContent')
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
  EVQ.length = 0; clearSel(); syncScene(); jumpTo(f[0], f[1], 1.5); requestDraw();
  return { a: uName(a), d: uName(d), me: me.n, foe: foe.n, kme: voiceKind(me), kfoe: voiceKind(foe) };
}'''
QUIET = '(() => { voiceStop(true); VOICE.last = {}; VOICE.cur = null; })()'
CUR = '(() => { var c = VOICE.cur; return c ? { name: c.name, pri: c.pri, started: !!c.s, left: Math.round(c.end - performance.now()) } : null; })()'
def steps(pg):
    fresh(pg, 0, 1)
    pg.touchscreen.tap(200, 500); pg.wait_for_timeout(300)
    pg.evaluate('(() => { UI.sound = true; audioInit(); })()'); pg.wait_for_timeout(600)
    # ================= 1. 소리 120개 =================
    print('1. 소리')
    r = pg.evaluate('''(() => { var ks = Object.keys(VOICE_DATA), kinds = {}, sits = {}, bad = [];
      ks.forEach(function (k) { var m = /^(brave|sage|lord|gen|lady)_([a-z]+)_([12])$/.exec(k); if (!m) { bad.push(k); return; } kinds[m[1]] = 1; sits[m[2]] = 1; var t = VOICE_TEXT[k]; if (!t || t.length !== 2 || !/[\\u4e00-\\u9fff]/.test(t[0]) || !/[가-힣]/.test(t[1])) bad.push('text:' + k); });
      return { n: ks.length, kinds: Object.keys(kinds).sort(), sits: Object.keys(sits).sort(), bad: bad, pri: Object.keys(VOICE_PRI).sort(), ac: !!AC, state: AC && AC.state }; })()''')
    ok(r['n'] == 120 and len(r['kinds']) == 5 and len(r['sits']) == 12 and not r['bad'] and r['sits'] == r['pri'], '소리 120개 = 갈래 5 × 상황 12 × 2, 대사(中文 · 뜻)가 모두 있다 — %s' % {k: r[k] for k in ('n', 'kinds', 'bad')})
    d = pg.evaluate('''() => Promise.all(Object.keys(VOICE_DATA).map(function (k) { return new Promise(function (res) {
        try { var bin = atob(VOICE_DATA[k]), u8 = new Uint8Array(bin.length); for (var i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
          var pr = AC.decodeAudioData(u8.buffer, function (b) { var ch = b.getChannelData(0), mx = 0; for (var j = 0; j < ch.length; j += 7) { var v = Math.abs(ch[j]); if (v > mx) mx = v; } res([k, b.duration, mx, bin.length]); }, function () { res([k, -1, 0, 0]); }); if (pr && pr.catch) pr.catch(function () { res([k, -1, 0, 0]); });
        } catch (e) { res([k, -1, 0, 0]); } }); }))''')
    bad = [x[0] for x in d if x[1] < 0]; dur = [x[1] for x in d if x[1] > 0]; mx = [x[2] for x in d if x[1] > 0]; size = sum(x[3] for x in d)
    ok(len(d) == 120 and not bad and min(dur) >= 0.3 and max(dur) <= 4.2 and min(mx) > 0.25 and max(mx) <= 1.0, '120개가 모두 풀린다 — 길이 %.2f~%.2f초(합 %.0f초) · 가장 큰 값 %.2f~%.2f · mp3 합 %d KB · 못 푼 것 %s' % (min(dur), max(dur), sum(dur), min(mx), max(mx), size // 1024, bad))
    # ================= 2. 목소리 갈래 =================
    print('2. 목소리 갈래')
    k = pg.evaluate('''(() => { var o = {}; ['여포', '장비', '조조', '유비', '손책', '순욱', '관우', '초선', '하후돈', '진궁', '여령기', '조운'].forEach(function (n) { var x = G.officers.filter(function (q) { return q.n === n; })[0]; o[n] = x ? voiceKind(x) + (isLord(x) ? '*' : '') : '-'; }); return o; })()''')
    print('     ', k)
    ok(k['여포'].startswith('brave') and k['장비'] == 'brave' and k['조조'] == 'lord*' and k['유비'] == 'lord*' and k['순욱'] == 'sage' and k['초선'] == 'lady' and k['관우'] == 'gen' and k['여령기'] == 'lady' and k['진궁'] == 'sage', '맹장 · 군주 · 지장 · 무장 · 여장이 뜻대로 갈린다(여포는 군주여도 맹장)')
    cnt = pg.evaluate('(() => { var c = {}; G.officers.forEach(function (o) { var k = voiceKind(o); c[k] = (c[k] || 0) + 1; }); return c; })()')
    ok(all(cnt.get(x, 0) > 0 for x in ('brave', 'sage', 'lord', 'gen', 'lady')), '다섯 갈래에 모두 사람이 있다 — %s' % cnt)
    # ================= 3. 말하기 · 겹칠 때 =================
    print('3. 말하기')
    S = pg.evaluate(SETUP); print('     ', S)
    pg.evaluate(QUIET)
    n1 = pg.evaluate('voiceSay(off(T.me), "deploy")'); pg.wait_for_timeout(350); c1 = pg.evaluate(CUR)
    ok(bool(n1) and re.match(r'^%s_deploy_[12]$' % S['kme'], n1) and c1 and c1['name'] == n1 and c1['started'] and c1['left'] > 0, '말이 나간다 — %s, 남은 %s ms' % (n1, c1 and c1['left']))
    ok(pg.evaluate('voiceSay(off(T.me), "deploy")') is False, '같은 이의 같은 말은 바로 다시 나오지 않는다')
    ok(pg.evaluate('voiceSay(off(T.foe), "hurt")') is False and pg.evaluate(CUR)['name'] == n1, '말이 나오는 동안 더 가벼운 말은 넘어간다')
    n2 = pg.evaluate('voiceSay(off(T.foe), "fall")'); pg.wait_for_timeout(400); c2 = pg.evaluate(CUR)
    ok(bool(n2) and '_fall_' in n2 and c2 and c2['name'] == n2, '더 무거운 말은 이어서(또는 앞의 말을 줄이고) 나온다 — %s' % n2)
    pg.wait_for_timeout(3600)
    ok(pg.evaluate(CUR) is None, '다 말하면 자리가 빈다')
    pg.evaluate(QUIET)
    a = [pg.evaluate('(() => { VOICE.last = {}; VOICE.cur = null; return voiceSay(off(T.me), "attack"); })()') for _ in range(4)]
    ok(len(set(a)) == 2 and a[0] != a[1] and a[1] != a[2], '두 대사를 번갈아 한다 — %s' % a)
    pg.evaluate(QUIET)
    ok(pg.evaluate('(() => { var r0 = Math.random; Math.random = function () { return 0.9; }; var x = voiceSay(off(T.me), "order", { p: 0.7 }); Math.random = function () { return 0.1; }; var y = voiceSay(off(T.me), "order", { p: 0.7 }); Math.random = r0; return [x, !!y]; })()') == [False, True], '확률을 주면 그만큼만 말한다')
    # ================= 4. 켜고 끄기 =================
    print('4. 켜고 끄기')
    pg.evaluate(QUIET)
    pg.evaluate('showMenu()'); pg.wait_for_timeout(300)
    lab = pg.evaluate('document.querySelector("#modal [data-a=voi]").innerText.replace(/\\n+/g, " | ")')
    ok(lab.startswith('음성 켜짐') and '중국어' in lab, '메뉴에 [음성] — ' + lab)
    B.shot(pg, 'w4_menu', 200)
    tapsel(pg, '#modal [data-a=voi]'); pg.wait_for_timeout(300)
    lab2 = pg.evaluate('document.querySelector("#modal [data-a=voi]").innerText.replace(/\\n+/g, " | ")'); opt = pg.evaluate('JSON.parse(localStorage.getItem("chunhado_opts"))')
    ok(lab2.startswith('음성 꺼짐') and opt.get('voice') is False and '음성 끔' in toast(pg), '누르면 꺼지고 기억한다 — %s / %s' % (lab2, opt))
    ok(pg.evaluate('voiceSay(off(T.me), "deploy")') is False and pg.evaluate('voiceAct({ kind: "tactic", af: G.player, tf: 1, alead: T.me, tlead: T.foe, ac0: T.f[0], ar0: T.f[1] }, 0)') is False, '꺼 두면 아무 말도 하지 않는다')
    Tj = pg.evaluate('(() => { saveGame(); return T; })()')
    pg.evaluate('closeDialog()'); reload(pg); tapsel(pg, '#tCont'); pg.wait_for_timeout(1200)
    if pg.evaluate('!!MODAL'): pg.evaluate('closeDialog()')
    ok(pg.evaluate('UI.voice') is False, '다시 열어도 꺼져 있다')
    pg.evaluate('(() => { UI.sound = true; audioInit(); showMenu(); })()'); pg.wait_for_timeout(300); tapsel(pg, '#modal [data-a=voi]'); pg.wait_for_timeout(200)
    ok(pg.evaluate('UI.voice') is True and pg.evaluate('JSON.parse(localStorage.getItem("chunhado_opts")).voice') is True, '다시 누르면 켜진다')
    tapsel(pg, '#modal [data-a=snd]'); pg.wait_for_timeout(200)
    lab3 = pg.evaluate('document.querySelector("#modal [data-a=voi]").innerText.replace(/\\n+/g, " | ")')
    ok(pg.evaluate('(t) => { window.T = t; EVQ.length = 0; return !!(UMAP[t.a] && UMAP[t.d] && uLeader(UMAP[t.a]).id === t.me); }', Tj), '(준비) 다시 열어도 두 부대가 그대로 있다')
    ok('효과음이 꺼져 있음' in lab3 and pg.evaluate('voiceSay(off(T.me), "deploy")') is False, '효과음을 끄면 음성도 나오지 않고, 단추에 그렇게 적힌다 — ' + lab3)
    pg.evaluate('showMenu()'); pg.wait_for_timeout(200); tapsel(pg, '#modal [data-a=snd]'); pg.wait_for_timeout(300); pg.evaluate('closeDialog()')
    ok(pg.evaluate('UI.sound && voiceOn()') is True, '효과음을 켜면 다시 나온다')
    # ================= 5. 대화창에 붙는 음성 =================
    print('5. 대화창')
    pg.evaluate(QUIET)
    pg.evaluate('(() => { var o = off(T.me); talk(o, sayLine(o, "deploy"), "출진"); })()'); pg.wait_for_timeout(350); c = pg.evaluate(CUR)
    ok(c and re.match(r'^%s_deploy_[12]$' % S['kme'], c['name']) and c['started'], '출진의 대화창에 출진의 음성 — %s' % (c and c['name']))
    B.shot(pg, 'w5_talk', 100)
    pg.evaluate(QUIET)
    pg.evaluate('(() => { var o = off(T.me); talk(o, "그냥 하는 말", ""); })()'); pg.wait_for_timeout(200)
    ok(pg.evaluate(CUR) is None, 'sayLine 을 거치지 않은 말에는 음성이 없다')
    pg.evaluate('(() => { var o = off(T.me); talk(o, sayLine(o, "found", "누구"), ""); })()'); pg.wait_for_timeout(200)
    ok(pg.evaluate(CUR) is None, '음성이 없는 갈래(탐색의 말)는 조용하다')
    pg.evaluate('(() => { var o = off(T.me), p = off(T.foe); sayLine(p, "joined", "조조"); talk(o, "다른 사람의 창", ""); })()'); pg.wait_for_timeout(200)
    ok(pg.evaluate(CUR) is None, '고른 말과 창의 주인이 다르면 붙이지 않는다')
    pg.evaluate('(() => { var r0 = Math.random; Math.random = function () { return 0.1; }; var o = off(T.foe); talk(o, sayLine(o, "joined", "조조"), ""); Math.random = r0; })()'); pg.wait_for_timeout(300); c = pg.evaluate(CUR)
    ok(c and '_join_' in c['name'], '등용에 응하는 말에는 등용의 음성 — %s' % (c and c['name']))
    pg.evaluate('(() => { UI.talk = false; voiceStop(true); VOICE.last = {}; VOICE.cur = null; var o = off(T.me); talk(o, sayLine(o, "deploy"), "출진"); UI.talk = true; })()'); pg.wait_for_timeout(300); c = pg.evaluate(CUR)
    ok(c and '_deploy_' in c['name'], '대화창을 꺼 두어도 음성은 나온다')
    pg.evaluate('talkHide()')
    # ================= 6. 싸움에 붙는 음성 =================
    print('6. 싸움')
    pg.evaluate(QUIET)
    ok(pg.evaluate('voiceAct({ kind: "tactic", af: 3, tf: 4, alead: T.me, tlead: T.foe, ac0: T.f[0], ar0: T.f[1] }, 0)') is False, '내가 끼지 않은 싸움에는 음성이 없다')
    r = pg.evaluate('''(() => { var a = UMAP[T.a], d = UMAP[T.d]; var tac = tacticList(a)[0]; a.morale = 100;
      var res = unitTactic(a, tac, { kind: 'unit', u: d, c: d.c, r: d.r });
      if (!res.ok) return { ok: false, msg: res.msg, tac: JSON.stringify(tac).slice(0, 120) };
      jumpTo(T.f[0], T.f[1], 1.5); requestDraw();
      window._res = res; delete SND.last.shout; var n0 = document.querySelectorAll('#fx .flt.vsay').length;
      var v0 = VOICE.said; animAct(res, function () { window._done = 1; }, function () { resultFx(res); });
      return { ok: true, alead: res.alead, tlead: res.tlead, me: T.me, foe: T.foe, kind: res.kind, fail: !!res.fail, crit: !!res.crit, cur: VOICE.cur && VOICE.cur.name, caps: document.querySelectorAll('#fx .flt.vsay').length - n0 }; })()''')
    print('     ', r)
    ok(r['ok'] and r['alead'] == r['me'] and r['tlead'] == r['foe'], '싸움 결과에 두 대장이 적힌다')
    ok(r['ok'] and r['cur'] and '_tactic_' in r['cur'], '전법을 쓰면 치는 쪽이 전법의 한마디를 한다 — %s' % r.get('cur'))
    pg.wait_for_timeout(450)
    cap = pg.evaluate('''(() => { var e = document.querySelectorAll('#fx .flt.vsay'); return e.length ? e[e.length - 1].textContent : ''; })()''')
    want = pg.evaluate('VOICE_TEXT[%s][1]' % json.dumps(r.get('cur') or 'x')) if r.get('cur') else None
    ok(bool(cap) and want and cap == '「' + want + '」', '칸 위에 뜻이 뜬다 — %s' % cap)
    B.shot(pg, 'w6_tactic', 0)
    pg.wait_for_function('window._done === 1', timeout=15000)
    ok(pg.evaluate('SND.last.shout === undefined'), '음성이 나가면 전법의 기합 효과음은 내지 않는다')
    pg.wait_for_timeout(2600); pg.evaluate(QUIET)
    r2 = pg.evaluate('''(() => { var res = window._res, o = {}; function t(x, ph) { voiceStop(true); VOICE.last = {}; VOICE.cur = null; var r0 = Math.random; Math.random = function () { return 0.1; }; var base = {}; for (var k in res) base[k] = res[k]; for (k in x) base[k] = x[k]; voiceAct(base, ph); Math.random = r0; return VOICE.cur ? VOICE.cur.name : null; }
      o.fall = t({ fell: true }, 1); o.rout = t({ fell: false, tAlive: false }, 1); o.adead = t({ fell: false, tAlive: true, aAlive: false }, 1);
      o.fail = t({ fell: false, tAlive: true, aAlive: true, kind: 'tactic', fail: true, crit: false }, 1); o.crit = t({ fell: false, tAlive: true, aAlive: true, kind: 'tactic', fail: false, crit: true }, 1);
      o.ploy = t({ fell: false, tAlive: true, aAlive: true, kind: 'ploy', success: true }, 1); o.hurt = t({ fell: false, tAlive: true, aAlive: true, kind: 'attack', fail: false, crit: false, dmg: 99999 }, 1);
      o.plain = t({ fell: false, tAlive: true, aAlive: true, kind: 'attack', fail: false, crit: false, dmg: 1 }, 1); o.atk = t({ kind: 'attack' }, 0);
      voiceStop(true); VOICE.last = {}; VOICE.cur = null; return o; })()''')
    print('     ', r2)
    ok('_fall_' in (r2['fall'] or '') and '_rout_' in (r2['rout'] or '') and '_retreat_' in (r2['adead'] or '') and '_hurt_' in (r2['fail'] or '') and '_great_' in (r2['crit'] or '') and '_ploy_' in (r2['ploy'] or '') and '_hurt_' in (r2['hurt'] or '') and r2['plain'] is None and '_attack_' in (r2['atk'] or ''), '결과에 맞는 한마디: 함락 · 궤멸 · 퇴각 · 실패 · 대성공 · 계략 · 크게 잃음 · (보통은 조용) · 공격')
    kinds = pg.evaluate('[voiceKind(off(T.me)), voiceKind(off(T.foe))]')
    ok(r2['fall'].startswith(kinds[0]) and r2['hurt'].startswith(kinds[1]), '친 쪽의 말은 친 쪽 목소리, 맞은 쪽의 말은 맞은 쪽 목소리 — %s' % kinds)
    # 음성을 끄면 기합 효과음이 돌아온다
    pg.evaluate('''(() => { UI.voice = false; var a = UMAP[T.a], d = UMAP[T.d]; a.done = false; a.morale = 100; a.troops = 5000; d.troops = 5000; a.mp = uMaxMp(a); var tac = tacticList(a)[0];
      var res = unitTactic(a, tac, { kind: 'unit', u: d, c: d.c, r: d.r }); window._done = 0; delete SND.last.shout; window._ok2 = res.ok; if (res.ok) animAct(res, function () { window._done = 1; }, function () { resultFx(res); }); else window._done = 1; })()''')
    pg.wait_for_function('window._done === 1', timeout=15000)
    ok(pg.evaluate('window._ok2 && SND.last.shout !== undefined && VOICE.cur === null'), '음성을 끄면 기합 효과음이 전처럼 난다')
    pg.evaluate('(() => { UI.voice = true; })()'); pg.wait_for_timeout(1500)
    # ================= 7. 대결 화면 =================
    print('7. 대결 화면')
    pg.evaluate(QUIET)
    pg.evaluate('''(() => { var S = duelNew('duel', off(T.me), off(T.foe), {}); duelOpen(S, 'a', { sub: '시험' }, function () {}); })()'''); pg.wait_for_timeout(700)
    c = pg.evaluate(CUR); cap = pg.evaluate('''(() => { var e = document.querySelector('#duel .du-float.vsay'); return e ? e.textContent : ''; })()''')
    box = pg.evaluate('''(() => { var e = document.querySelector('#duel .du-float.vsay'); if (!e) return null; var r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.right), innerWidth]; })()''')
    ok(box and box[0] >= 0 and box[1] <= box[2], '말풍선이 화면 밖으로 나가지 않는다 — %s' % box)
    ok(c and '_duel_' in c['name'] and c['name'].startswith(kinds[0]) and cap.startswith('「'), '일기토가 열리면 건 쪽이 한마디 하고 뜻이 뜬다 — %s %s' % (c and c['name'], cap))
    B.shot(pg, 'w7_duel', 0)
    pg.evaluate('''(() => { var e = document.querySelector('#duel [data-x=auto]'); if (e) e.click(); })()''')
    pg.wait_for_function('DU && DU.ended', timeout=40000); pg.wait_for_timeout(900)
    c = pg.evaluate(CUR); w = pg.evaluate('DU.S.win')
    ok(w == 'draw' or (c and ('_great_' in c['name'])), '끝나면 이긴 쪽이 한마디 한다 — 결과 %s · %s' % (w, c and c['name']))
    pg.evaluate('''(() => { var e = document.querySelector('#duel [data-x=close]'); if (e) e.click(); })()'''); pg.wait_for_timeout(400)
    # ================= 8. 도움말 =================
    print('8. 도움말')
    pg.evaluate('showHelp()'); pg.wait_for_timeout(300)
    t = pg.evaluate('document.querySelector("#modal").textContent')
    ok('음성' in t and '중국어' in t and '맹장' in t and '여장' in t, '도움말에 음성 풀이가 있다')
    pg.evaluate('closeDialog()')
B.run(steps, 390, 844, 2)
errs = [e for e in B.errors if 'GPU stall' not in e and 'GL Driver' not in e and 'ERR_FILE_NOT_FOUND' not in e and 'willReadFrequently' not in e]
print('console errors:', errs[:6])
print('FAILS %d' % len(fails), fails)
sys.exit(1 if fails or errs else 0)
