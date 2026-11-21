# v0.9.3 — 화면 조작으로 확인: 대화창 · 군사의 말 · 군사 임명
#   1) 대화창: 내 차례가 시작되면 군사가 한마디 하는가(한 턴에 한 번), 누르면 닫히는가, 저절로 사라지는가, 메뉴에서 끄면 알림 줄로 바뀌는가
#   2) 업무: 징병·순찰·훈련·생산·거래·탐색·포상·이동·합병·출진·수송·포로 해방 — 맡은 무장(포상·해방은 상대, 거래는 군사)이 답하고 결과가 그 아래에 붙는가
#   3) 군사: STATUS 창의 한마디를 누르면 그 일로 가는가, 군사가 없으면 붉게 알리고 [임명]으로 세울 수 있는가, 조언이 빗나가면 한마디 덧붙이는가
#   python3 tests/d19.py          찍은 그림은 tests/shots19/
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import taphex, tapsel
B.SHOTS = os.path.join(B.ROOT, 'shots19')
os.makedirs(B.SHOTS, exist_ok=True)
fails = []
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)
TK = '''(() => { var t = document.getElementById("talk"), r = t.getBoundingClientRect(), q = function (c) { var e = t.querySelector(c); return e ? e.textContent : ""; }, to = document.getElementById("toast"), tr = to.getBoundingClientRect();
  return { on: t.classList.contains("on"), who: q(".tk-who b"), role: q(".tk-who em"), say: q(".tk-say"), sub: q(".tk-sub"), adv: q(".tk-adv"), por: !!t.querySelector(".por"), chip: !!t.querySelector(".tk-who .fchip, .tk-who .chip, .tk-who i, .tk-who span"),
    top: Math.round(r.top), bottom: Math.round(r.bottom), left: Math.round(r.left), right: Math.round(r.right), op: +getComputedStyle(t).opacity, pe: getComputedStyle(t).pointerEvents,
    toast: to.textContent, toastOn: to.classList.contains("on"), toastTop: Math.round(tr.top), W: window.innerWidth, hud: document.getElementById("hud").offsetHeight }; })()'''
def tk(pg): return pg.evaluate(TK)
# 그 무장이 그 일에 할 수 있는 말(sayLine 을 여러 번 불러 모은다 — 말은 고를 때마다 바뀔 수 있으므로)
def lines(pg, name, key, x=None):
    return pg.evaluate('''([n, key, x]) => { var o = G.officers.filter(function (v) { return v.n === n; })[0], s = {}; for (var i = 0; i < 60; i++) s[x === null ? sayLine(o, key) : sayLine(o, key, x)] = 1; return Object.keys(s); }''', [name, key, x])
def clean(s): return bool(s) and '{' not in s and 'undefined' not in s and 'NaN' not in s and '<' not in s
def reset(pg, bid):
    pg.evaluate('''(id) => { var b = G.bases[id]; baseOfficers(b).forEach(function (o) { o.acted = false; }); G.factions[G.player].ap = 300; b.gold = 6000; b.food = 80000; b.troops = 20000; b.morale = 60; b.order = 55;
      b.w.spear = 9000; b.w.halberd = 3000; b.w.bow = 3000; b.w.horse = 3000; refreshSheet(); refreshHud(); }''', bid)
def cmd(pg, name):
    # 그 단추가 있는 탭을 찾아 누른다
    n = pg.locator('#sheet .tabs button').count()
    for i in range(n):
        if pg.locator('#sheet [data-a=%s]' % name).count(): break
        pg.locator('#sheet .tabs button').nth(i).tap(); pg.wait_for_timeout(350)
    tapsel(pg, '#sheet [data-a=%s]' % name); pg.wait_for_timeout(350)
def pick_auto_ok(pg):
    tapsel(pg, '#modal [data-a=auto]'); pg.wait_for_timeout(150)
    first = pg.evaluate('''(() => { var rs = document.querySelectorAll("#modal .tr.sel"), e = null, i; for (i = 0; i < rs.length; i++) { var o = rs[i].querySelector(".ord"); if (!o || o.textContent === "1") { e = rs[i]; break; } } return e ? off(+e.getAttribute("data-v")).n : ""; })()''')      # 맨 먼저 고른 무장(= 답하는 사람)
    tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(450)
    return first

def steps(pg):
    # ================= 1. 대화창 =================
    # 1-1. 새 판: 시작 안내를 닫으면 군사가 한마디
    B.start(pg, 4)                                           # 원소(거점 셋)
    pg.wait_for_timeout(1300)
    s0 = pg.evaluate('''(() => { var A = facAdv(G.player), top = advTop(todoList()); return { f: G.factions[G.player].name, adv: A ? A.n : "", say: top ? top.say.replace(/<[^>]*>/g, "") : "", brief: UI.briefT, turn: G.turn, modal: !!MODAL }; })()''')
    t0 = tk(pg); B.shot(pg, 'k01_brief', 100)
    print('  시작:', s0, t0)
    ok(s0['f'] == '원소' and not s0['modal'], '(준비) 원소로 시작')
    ok(t0['on'] and t0['who'] == s0['adv'] and t0['role'] == '군사' and t0['say'] == s0['say'] and clean(t0['say']) and t0['sub'] == '' and t0['por'], '시작 안내를 닫으면 군사(%s)가 대화창에서 지금 가장 급한 일을 말한다 ["%s"]' % (s0['adv'], t0['say']))
    ok(s0['brief'] == s0['turn'], '이 턴의 한마디로 적어 둔다')
    ok(t0['hud'] <= t0['top'] <= t0['hud'] + 60 and t0['left'] >= 0 and t0['right'] <= t0['W'] and t0['bottom'] - t0['top'] <= 110 and t0['op'] > 0.9, '화면 위쪽 한 띠 — 위에서 %d~%dpx, 좌우 %d~%d(화면 %d)' % (t0['top'], t0['bottom'], t0['left'], t0['right'], t0['W']))
    hm = pg.evaluate('''(() => { var p = document.querySelector("#sheet .hm-advp"), s = p ? p.querySelector(".hm-say") : null; return p ? { say: s.querySelector(".tx > span").textContent, name: s.querySelector(".tx i b").textContent, por: !!s.querySelector(".por"), btn: p.querySelector(".hm-adv").textContent, dis: s.disabled, first: document.querySelector("#sheet .sh-body").firstElementChild === p } : null; })()''')
    ok(hm and hm['say'] == s0['say'] and hm['name'] == s0['adv'] and hm['por'] and hm['btn'] == '바꾸기' and hm['first'] and not hm['dis'], 'STATUS 창 맨 위에도 같은 말이 남아 있다(초상 · 군사 %s · [바꾸기])' % s0['adv'])
    # 1-2. 누르면 닫힌다 / 같은 턴에는 다시 뜨지 않는다
    pg.locator('#talk').tap(); pg.wait_for_timeout(350)
    t1 = tk(pg)
    ok(not t1['on'] and t1['op'] < 0.1 and t1['pe'] == 'none', '대화창을 누르면 바로 닫힌다(닫힌 뒤에는 누름을 가로채지 않는다)')
    pg.evaluate('advBrief(30)'); pg.wait_for_timeout(500)
    ok(not tk(pg)['on'], '같은 턴에는 다시 뜨지 않는다(한 턴에 한 번)')
    # v0.11(헌책): 같은 말은 턴마다 되풀이하지 않는다 — 다음 턴 · 그다음 턴에는 '다른' 헌책을 말하거나(있으면) 말하지 않는다. 같은 문장은 세 턴 안에 다시 뜨지 않는다. 말이 바뀌면 바로 뜬다
    rp = []; said = [t0['say']]
    for dt in (1, 2, 3):
        pg.evaluate('() => { talkHide(); G.turn += 1; UI.briefT = undefined; advBrief(30); }'); pg.wait_for_timeout(450)
        t = tk(pg); rp.append(t['on']); said.append(t['say'] if t['on'] else '')
    pg.evaluate('() => { talkHide(); UI.briefT = undefined; UI.briefSay = "다른 말"; advBrief(30); }'); pg.wait_for_timeout(450)
    rp.append(tk(pg)['on'])
    pg.evaluate('() => { talkHide(); G.turn -= 3; UI.briefT = G.turn; UI.briefAt = G.turn; }')
    print('  턴마다의 한마디:', said)
    rep_ok = all(not said[i] or (said[i] != said[i - 1] and (i < 2 or said[i] != said[i - 2])) for i in range(1, 4))
    ok(rep_ok and rp[3], '같은 말은 되풀이하지 않는다 — 이어지는 세 턴의 한마디가 앞의 두 턴과 겹치지 않고(다른 헌책을 말하거나 쉰다), 말이 바뀌면 바로 뜬다 %s' % rp)
    # 1-3. 저절로 사라진다
    lord = pg.evaluate('''(() => { var L = off(G.factions[G.player].lord); talk(L, "시험 삼아 한마디 하겠다.", "결과 한 줄", 700); return L.n; })()''')
    pg.wait_for_timeout(200); t2 = tk(pg); pg.wait_for_timeout(900); t3 = tk(pg)
    ok(t2['on'] and t2['who'] == lord and t2['role'] == '군주' and t2['sub'] == '결과 한 줄' and not t3['on'], '잠깐 뒤 저절로 사라진다 — 군주는 [군주] 딱지')
    ms = pg.evaluate('''(() => { var o = baseOfficers(facCities(G.player)[0]).filter(function (x) { return !isLord(x) && facAdv(G.player) !== x; })[0], out = [], st = window.setTimeout;
      window.setTimeout = function (fn, t) { out.push(t); return st(fn, t); };
      talk(o, "가", ""); talk(o, "가나다라마바사아자차카타파하가나다라마바사", "결과 한 줄 — 열두 자쯤"); talk(o, "하".repeat(90), "결".repeat(40));
      window.setTimeout = st; talkHide(); return { out: out, role: roleOf(o), n: o.n }; })()''')
    ok(ms['out'][0] == 2600 and 2600 < ms['out'][1] < 5200 and ms['out'][2] == 5200 and ms['role'] == '', '뜨는 시간은 말의 길이에 따라 2.6~5.2초 %s — 여느 무장은 딱지 없음' % ms['out'])
    # 1-4. 이어서 하기: 불러온 판에서도 군사가 한마디
    pg.evaluate('() => { newGame(4, 4242); saveGame(); }')
    pg.reload(); pg.wait_for_function('window.R3 && R3.ready', timeout=60000); pg.wait_for_timeout(600)
    tapsel(pg, '#tCont'); pg.wait_for_timeout(1500)
    t4 = tk(pg); a4 = pg.evaluate('facAdv(G.player).n')
    ok(t4['on'] and t4['who'] == a4 and t4['role'] == '군사' and clean(t4['say']), '이어서 하기로 들어와도 군사가 한마디 ["%s"]' % t4['say'])
    pg.locator('#talk').tap(); pg.wait_for_timeout(300)

    # ================= 2. 업무마다 =================
    info = pg.evaluate('''(() => { var b = facCities(G.player)[0]; selectBase(b); return { id: b.id, n: b.n, bases: facBases(G.player).length, market: !!hasFac(b, "market"), smithy: !!hasFac(b, "smithy"), barracks: !!hasFac(b, "barracks"), adv: facAdv(G.player).n, lord: off(G.factions[G.player].lord).n }; })()''')
    pg.wait_for_timeout(600)
    print('  거점:', info)
    bid = info['id']
    def after(key, x=None, expect_who=None):
        t = tk(pg)
        ls = lines(pg, t['who'], key, x) if t['who'] else []
        return t, ls
    # --- 징병
    reset(pg, bid); tr0 = pg.evaluate('(id) => G.bases[id].troops', bid)
    cmd(pg, 'draft'); who = pick_auto_ok(pg); t, ls = after('draft')
    d = pg.evaluate('(id) => G.bases[id].troops', bid) - tr0
    print('  징병:', who, t['who'], t['say'], '|', t['sub'])
    ok(t['on'] and t['who'] == who and t['say'] in ls and clean(t['say']) and t['sub'] == '징병 +{:,}명'.format(d) and d > 0 and t['por'], '징병: 맡은 무장(%s)이 답하고 결과가 아래에 ["%s" / %s]' % (who, t['say'], t['sub']))
    ok(not t['toastOn'] or '자동' in t['toast'], '결과는 대화창에만 — 알림 줄에는 겹쳐 나오지 않는다 [%s]' % t['toast'])
    ok(not pg.evaluate('!!MODAL'), '창은 전처럼 닫힌다(대화창은 명령의 흐름을 막지 않는다)')
    B.shot(pg, 'k02_draft', 100)
    # 대화창이 떠 있는 채로 바로 다음 명령을 내릴 수 있다
    cmd(pg, 'patrol'); ok(pg.evaluate('!!MODAL') and '순찰' in pg.evaluate('document.querySelector("#modal .dlg-h").textContent'), '대화창이 떠 있어도 다음 명령 창이 바로 열린다')
    od0 = pg.evaluate('(id) => G.bases[id].order', bid)
    who = pick_auto_ok(pg); t, ls = after('patrol'); d = pg.evaluate('(id) => G.bases[id].order', bid) - od0
    ok(t['on'] and t['who'] == who and t['say'] in ls and t['sub'] == '치안 +%d' % d and d > 0, '순찰: %s ["%s" / %s]' % (who, t['say'], t['sub']))
    # --- 훈련
    reset(pg, bid); m0 = pg.evaluate('(id) => G.bases[id].morale', bid)
    cmd(pg, 'train'); who = pick_auto_ok(pg); t, ls = after('train'); d = pg.evaluate('(id) => G.bases[id].morale', bid) - m0
    ok(t['on'] and t['who'] == who and t['say'] in ls and t['sub'] == '기력 +%d' % d and d > 0, '훈련: %s ["%s" / %s]' % (who, t['say'], t['sub']))
    # --- 생산(창)
    reset(pg, bid)
    if not info['smithy']: pg.evaluate('(id) => { var b = G.bases[id], p = b.plots.filter(function (q) { return !q.fac; })[0]; p.fac = { t: "smithy", lv: 1, done: true, prog: 0, need: 0, rate: 0, hp: FAC_HP }; refreshSheet(); }', bid)
    w0 = pg.evaluate('(id) => G.bases[id].w.spear', bid)
    cmd(pg, 'produce'); tapsel(pg, '#modal [data-a=k]', 0); pg.wait_for_timeout(300)
    who = pick_auto_ok(pg); t = tk(pg); ls = lines(pg, t['who'], 'produce', '창'); d = pg.evaluate('(id) => G.bases[id].w.spear', bid) - w0
    ok(t['on'] and t['who'] == who and t['say'] in ls and clean(t['say']) and t['sub'] == '창 +{:,}'.format(d) and d > 0, '생산: %s ["%s" / %s]' % (who, t['say'], t['sub']))
    ok(all(clean(x) for x in ls) and any('창을' in x or '창,' in x for x in ls), '말에 만드는 물건의 이름과 맞는 조사가 들어간다 %s' % ls)
    # --- 거래: 맡는 무장이 없으므로 군사가 답한다
    reset(pg, bid)
    if not info['market']: pg.evaluate('(id) => { var b = G.bases[id], p = b.plots.filter(function (q) { return !q.fac; })[0]; p.fac = { t: "market", lv: 1, done: true, prog: 0, need: 0, rate: 0, hp: FAC_HP }; refreshSheet(); }', bid)
    g0 = pg.evaluate('(id) => [G.bases[id].gold, G.bases[id].food]', bid)
    cmd(pg, 'trade')
    pg.evaluate('''(() => { var r = document.getElementById("trR"); r.value = 300; r.dispatchEvent(new Event("input", { bubbles: true })); })()'''); pg.wait_for_timeout(200)
    tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(450)
    t = tk(pg); g1 = pg.evaluate('(id) => [G.bases[id].gold, G.bases[id].food]', bid); ls = lines(pg, info['adv'], 'trade')
    print('  거래:', g0, g1, t['who'], t['say'], '|', t['sub'])
    ok(g1[0] == g0[0] - 300 and g1[1] == g0[1] + 1200, '(준비) 금 300으로 병량 1,200을 샀다')
    ok(t['on'] and t['who'] == info['adv'] and t['role'] == '군사' and t['say'] in ls and t['sub'] == '병량 +1,200 (금 −300)' and not pg.evaluate('!!MODAL'), '거래: 군사(%s)가 답한다 ["%s" / %s]' % (info['adv'], t['say'], t['sub']))
    # --- 탐색
    reset(pg, bid)
    cmd(pg, 'search'); who = pick_auto_ok(pg); t = tk(pg)
    key = 'found' if '찾았습니다' in t['sub'] and '금 ' not in t['sub'] else ('gold' if t['sub'].startswith('금 ') else 'nothing')
    x = t['sub'].split('을 찾았')[0].split('를 찾았')[0] if key == 'found' else None
    ls = lines(pg, t['who'], key, x)
    print('  탐색:', who, key, x, t['say'], '|', t['sub'])
    ok(t['on'] and t['who'] == who and t['say'] in ls and clean(t['say']) and ('찾았습니다' in t['sub'] or t['sub'] == '아무것도 찾지 못했습니다'), '탐색(%s): %s ["%s" / %s]' % (key, who, t['say'], t['sub']))
    # 세 가지 결과의 말이 모두 온전한가(찾은 사람의 이름 · 받침에 맞는 조사)
    sl = pg.evaluate('''(() => { var b = facCities(G.player)[0], os = baseOfficers(b), out = {}; ["found", "gold", "nothing"].forEach(function (k) { out[k] = []; os.forEach(function (o) { ["관우", "조조", "제갈량", "초선"].forEach(function (x) { for (var i = 0; i < 6; i++) out[k].push(k === "found" ? sayLine(o, k, x) : sayLine(o, k)); }); }); }); return out; })()''')
    bad = [s for k in sl for s in sl[k] if not clean(s)] + [s for s in sl['found'] if not any(n in s for n in ('관우', '조조', '제갈량', '초선'))] + [s for s in sl['found'] if re.search('관우이라|조조이라|제갈량라|초선라|관우을|조조을|제갈량를|초선를', s)]
    ok(not bad, '탐색의 말: 찾은 사람의 이름이 들어가고 조사가 받침에 맞는다 (%d가지 — 어긋난 것 %s)' % (len(set(sl['found'])), bad[:3]))
    # --- 포상: 받는 무장이 답한다
    reset(pg, bid)
    pg.evaluate('(id) => { baseOfficers(G.bases[id]).filter(function (o) { return !isLord(o); }).slice(0, 2).forEach(function (o, i) { o.loy = 70 + i; }); refreshSheet(); }', bid)
    cmd(pg, 'reward')
    rw = pg.evaluate('''(() => { var e = document.querySelector("#modal .row[data-a=r]:not(.dim)"); return { id: +e.getAttribute("data-v"), n: off(+e.getAttribute("data-v")).n, loy: off(+e.getAttribute("data-v")).loy }; })()''')
    tapsel(pg, '#modal .row[data-a=r]:not(.dim)', 0); pg.wait_for_timeout(400)
    t = tk(pg); l1 = pg.evaluate('(id) => off(id).loy', rw['id']); ls = lines(pg, rw['n'], 'reward')
    ok(t['on'] and t['who'] == rw['n'] and t['say'] in ls and t['sub'] == '충성 +%d (%d)' % (l1 - rw['loy'], l1) and l1 > rw['loy'] and pg.evaluate('!!MODAL'), '포상: 받는 무장(%s)이 답한다 — 창은 열린 채 ["%s" / %s]' % (rw['n'], t['say'], t['sub']))
    B.shot(pg, 'k03_reward', 100)
    z = pg.evaluate('''(() => { var t = document.getElementById("talk"), m = document.getElementById("modal"); return [+getComputedStyle(t).zIndex, +getComputedStyle(m).zIndex]; })()''')
    ok(z[0] > z[1], '대화창은 열려 있는 창보다 위에 뜬다(z %d > %d)' % (z[0], z[1]))
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(300)
    # --- 이동
    reset(pg, bid)
    cmd(pg, 'move')
    mv = pg.evaluate('''(() => { var e = document.querySelector("#modal .tr[data-a=pick]"); return off(+e.getAttribute("data-v")).n; })()''')
    tapsel(pg, '#modal .tr[data-a=pick]', 0); tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(400)
    ok('어디로 보낼까요' in pg.evaluate('document.querySelector("#modal .dlg-h").textContent'), '(준비) 이동: 보낼 곳을 고르는 창')
    tapsel(pg, '#modal .row[data-a=d]', 0); pg.wait_for_timeout(450)
    t = tk(pg); ls = lines(pg, mv, 'move')
    ok(t['on'] and t['who'] == mv and t['say'] in ls and re.match(r'^1명 출발 — \d+일 뒤 도착$', t['sub']) is not None and not pg.evaluate('!!MODAL'), '이동: 떠나는 무장(%s)이 답한다 ["%s" / %s]' % (mv, t['say'], t['sub']))
    # --- 흡수합병
    reset(pg, bid)
    mg = pg.evaluate('''((id) => { var b = G.bases[id], pair = null, i, j;
      for (i = 0; i < b.plots.length && !pair; i++) for (j = 0; j < b.plots.length && !pair; j++) if (i !== j && !b.plots[i].fac && !b.plots[j].fac && hdist(b.plots[i].c, b.plots[i].r, b.plots[j].c, b.plots[j].r) === 1) pair = [i, j];
      if (!pair) return null;
      pair.forEach(function (k) { b.plots[k].fac = { t: "farm", lv: 1, done: true, prog: 0, need: 0, rate: 0, hp: FAC_HP }; });
      flowFacility(b, pair[0]); return pair; })''', bid)
    pg.wait_for_timeout(400)
    if mg:
        tapsel(pg, '#modal [data-a=merge]'); pg.wait_for_timeout(350)
        who = pick_auto_ok(pg); t = tk(pg); ls = lines(pg, t['who'], 'merge', '농장')
        lv = pg.evaluate('([id, i]) => G.bases[id].plots[i].fac.lv', [bid, mg[0]])
        ok(t['on'] and t['who'] == who and t['say'] in ls and clean(t['say']) and t['sub'] == '농장 Lv2로 올랐습니다' and lv == 2, '흡수합병: %s ["%s" / %s]' % (who, t['say'], t['sub']))
        pg.evaluate('if (MODAL) closeDialog()')
    else:
        print('  (흡수합병: 맞붙은 빈 부지 두 칸이 없어 건너뜀)')
    # --- 포로 해방: 풀려나는 무장이 답한다
    cp = pg.evaluate('''((id) => { var b = G.bases[id], o = G.officers.filter(function (x) { return x.f >= 0 && x.f !== G.player && x.st === "active" && x.unit === null && !isLord(x) && facBases(x.f).length >= 1; })[0];
      captureOfficer(o, G.player, b); refreshSheet(); return { id: o.id, n: o.n, f: G.factions[o.f].name }; })''', bid)
    pg.wait_for_timeout(200)
    cmd(pg, 'captive'); pg.wait_for_timeout(200)
    tapsel(pg, '#modal [data-a=rel][data-v="%d"]' % cp['id']); pg.wait_for_timeout(400)
    t = tk(pg); ls = lines(pg, cp['n'], 'released'); st = pg.evaluate('(id) => [off(id).st, G.bases[off(id).loc].owner === off(id).f]', cp['id'])
    ok(t['on'] and t['who'] == cp['n'] and t['say'] in ls and t['sub'].endswith('풀어 주었습니다') and cp['n'] in t['sub'] and st == ['active', True], '포로 해방: 풀려나는 무장(%s군 %s)이 답한다 ["%s" / %s]' % (cp['f'], cp['n'], t['say'], t['sub']))
    pg.evaluate('if (MODAL) closeDialog()'); pg.wait_for_timeout(200)
    # --- 출진: 주장이 답한다
    reset(pg, bid)
    cmd(pg, 'deploy'); tapsel(pg, '#modal [data-a=auto]'); pg.wait_for_timeout(300)
    tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(1100)
    t = tk(pg); u = pg.evaluate('''(() => { var u = selUnit(); return u ? { leader: uLeader(u).n, name: uName(u), type: UNIT_TYPES[u.type].name, troops: u.troops } : null; })()''')
    ls = lines(pg, u['leader'], 'deploy') if u else []
    print('  출진:', u, t['who'], t['say'], '|', t['sub'])
    ok(u is not None and t['on'] and t['who'] == u['leader'] and t['say'] in ls and t['sub'] == '%s 출진 — %s %s명' % (u['name'], u['type'], '{:,}'.format(u['troops'])), '출진: 주장(%s)이 답한다 ["%s" / %s]' % (u and u['leader'], t['say'], t['sub']))
    B.shot(pg, 'k04_deploy', 100)
    pg.evaluate('clearSel(); showHome()'); pg.wait_for_timeout(300)
    # --- 수송
    pg.evaluate('(id) => { selectBase(G.bases[id]); }', bid); pg.wait_for_timeout(500); reset(pg, bid)
    cmd(pg, 'trans'); tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(900)
    t = tk(pg); u = pg.evaluate('''(() => { var u = selUnit(); return u ? { leader: uLeader(u).n, type: u.type } : null; })()''')
    ls = lines(pg, u['leader'], 'trans') if u else []
    ok(u is not None and u['type'] == 'trans' and t['on'] and t['who'] == u['leader'] and t['say'] in ls and t['sub'].startswith('수송대 출발'), '수송: 이끄는 무장(%s)이 답한다 ["%s" / %s]' % (u and u['leader'], t['say'], t['sub']))
    pg.evaluate('clearSel(); showHome()'); pg.wait_for_timeout(300)
    # --- 안 되는 명령은 전처럼 알림 줄로(대화창은 뜨지 않는다)
    pg.evaluate('talkHide()')
    pg.evaluate('(id) => { selectBase(G.bases[id]); }', bid); pg.wait_for_timeout(500); reset(pg, bid)
    pg.evaluate('(id) => { G.bases[id].gold = 0; G.factions[G.player].ap = 300; refreshSheet(); }', bid)
    cmd(pg, 'draft')
    if pg.evaluate('!!MODAL'): pick_auto_ok(pg)
    t = tk(pg)
    ok(not t['on'] and '금이 부족합니다' in t['toast'], '안 되는 명령은 전처럼 알림 줄로 까닭만 [%s]' % t['toast'])
    pg.evaluate('if (MODAL) closeDialog()'); pg.wait_for_timeout(200)

    # ================= 3. 메뉴에서 끄기 =================
    pg.evaluate('showMenu()'); pg.wait_for_timeout(300)
    lb0 = pg.evaluate('document.querySelector("#modal [data-a=talk]").textContent')
    tapsel(pg, '#modal [data-a=talk]'); pg.wait_for_timeout(300)
    lb1 = pg.evaluate('document.querySelector("#modal [data-a=talk]").textContent')
    opt = pg.evaluate('JSON.parse(localStorage.getItem("chunhado_opts")).talk')
    ok(lb0 == '대화창 켜짐' and lb1 == '대화창 꺼짐' and opt is False and pg.evaluate('UI.talk') is False, '메뉴의 [대화창 켜짐] → [꺼짐], 설정에 저장된다')
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(200)
    reset(pg, bid); tr0 = pg.evaluate('(id) => G.bases[id].troops', bid)
    cmd(pg, 'draft'); who = pick_auto_ok(pg); t = tk(pg); d = pg.evaluate('(id) => G.bases[id].troops', bid) - tr0
    ok(not t['on'] and t['toastOn'] and t['toast'] == '징병 +{:,}명'.format(d), '끄면 전처럼 결과만 알림 줄로 [%s]' % t['toast'])
    # 꺼 둔 채로 등용 결과(군사의 덧말에 태그가 섞인다)가 알림 줄에 글로만 나오는가
    raw = pg.evaluate('''(() => { var o = off(G.factions[G.player].lord); talk(o, "말", '관우가 거절했습니다 (충성 +3)<i class="tk-adv">군사 전풍: …뜻밖입니다.</i>'); return document.getElementById("toast").innerHTML; })()''')
    ok('<' not in raw and '관우가 거절했습니다 (충성 +3)' in raw and '군사 전풍' in raw, '끈 채로는 태그 없이 글만 [%s]' % raw)
    pg.evaluate('UI.briefT = undefined; advBrief(30)'); pg.wait_for_timeout(500)
    t = tk(pg)
    ok(not t['on'] and '거절했습니다' in t['toast'], '꺼 두면 차례 첫머리의 군사 한마디도 뜨지 않는다(알림 줄로도 나오지 않는다)')
    # 다시 불러와도 꺼진 채
    pg.evaluate('saveGame()'); pg.reload(); pg.wait_for_function('window.R3 && R3.ready', timeout=60000); pg.wait_for_timeout(600)
    tapsel(pg, '#tCont'); pg.wait_for_timeout(1500)
    ok(pg.evaluate('UI.talk') is False and not tk(pg)['on'], '다시 들어와도 꺼진 채로 — 군사의 한마디도 뜨지 않는다')
    pg.evaluate('showMenu()'); pg.wait_for_timeout(300); tapsel(pg, '#modal [data-a=talk]'); pg.wait_for_timeout(300)
    ok(pg.evaluate('UI.talk') is True and pg.evaluate('document.querySelector("#modal [data-a=talk]").textContent') == '대화창 켜짐' and pg.evaluate('JSON.parse(localStorage.getItem("chunhado_opts")).talk') is True, '다시 켠다')
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(200)

    # ================= 4. 군사 =================
    # 4-1. STATUS 창의 한마디를 누르면 그 일로
    pg.evaluate('clearSel(); showHome()'); pg.wait_for_timeout(300)
    h1 = pg.evaluate('''(() => { var top = advTop(todoList()), first = todoList()[0]; return { say: top ? top.say.replace(/<[^>]*>/g, "") : "", go: top ? top.go : null, same: top === advTop([first].concat([])) || true, shown: document.querySelector("#sheet .hm-say .tx > span").textContent, t0: first ? first.t : "" }; })()''')
    ok(h1['shown'] == h1['say'] and clean(h1['say']), 'STATUS 창의 군사 한마디 = 지금 할 일 가운데 맨 위의 것 ["%s"]' % h1['shown'])
    tapsel(pg, '#sheet .hm-say'); pg.wait_for_timeout(700)
    w = pg.evaluate('''(() => { var s = UI.sel; return { sel: s ? s.kind : null, modal: !!MODAL, title: MODAL ? document.querySelector("#modal .dlg-h").textContent : "", base: s && s.kind === "base" ? G.bases[s.id].n : "" }; })()''')
    print('  한마디를 누르면:', h1['go'], w)
    ok((h1['go'][0] in ('base', 'recruit') and w['sel'] == 'base') or (h1['go'][0] == 'unit' and w['sel'] == 'unit') or (h1['go'][0] in ('list', 'peace') and w['modal']) or h1['go'][0] == 'end', '누르면 그 일로 간다 %s → %s' % (h1['go'], w))
    pg.evaluate('if (MODAL) closeDialog(); clearSel(); showHome()'); pg.wait_for_timeout(300)
    # 4-2. 군사가 없을 때
    pg.evaluate('G.factions[G.player].adv = -1; showHome()'); pg.wait_for_timeout(300)
    n0 = pg.evaluate('''(() => { var p = document.querySelector("#sheet .hm-advp"), b = p.querySelector(".hm-adv"); return { cls: p.className, tx: p.querySelector(".hm-say").innerText.replace(/\\n/g, " "), btn: b.textContent, pri: b.classList.contains("pri"), bad: !!p.querySelector(".bad") }; })()''')
    ok('none' in n0['cls'] and '군사가 없습니다' in n0['tx'] and n0['btn'] == '임명' and n0['pri'] and n0['bad'], '군사가 없으면 STATUS 창에 붉게 알리고 [임명] 단추가 도드라진다 [%s]' % n0['tx'])
    B.shot(pg, 'k05_noadv', 100)
    pg.evaluate('UI.briefT = undefined; advBrief(30)'); pg.wait_for_timeout(500)
    ok(not tk(pg)['on'], '군사가 없으면 차례 첫머리의 한마디도 없다')
    tapsel(pg, '#sheet .hm-adv'); pg.wait_for_timeout(400)
    dl = pg.evaluate('''(() => { var m = document.getElementById("modal"); return { h: m.querySelector(".dlg-h").textContent, note: (m.querySelector(".note.bad") || {}).textContent || "", n: m.querySelectorAll("[data-a=set]").length, rows: m.querySelectorAll(".advl .row").length, first: m.querySelector(".advl .row .nm").textContent, top: advCandidates(G.player)[0].n, int: advCandidates(G.player)[0].int }; })()''')
    ok('군사 임명' in dl['h'] and '군사가 없습니다' in dl['note'] and dl['n'] == dl['rows'] and dl['n'] >= 3 and dl['first'].startswith(dl['top']), "'군사 임명' 창: 후보 %d명 모두에 [임명] 단추, 지력이 높은 순(맨 위 %s)" % (dl['n'], dl['top']))
    tapsel(pg, '#modal [data-a=set]', 0); pg.wait_for_timeout(400)
    t = tk(pg); ls = lines(pg, dl['top'], 'advisor')
    ok(pg.evaluate('facAdv(G.player).n') == dl['top'] and t['on'] and t['who'] == dl['top'] and t['role'] == '군사' and t['say'] in ls and t['sub'] == '%s 군사로 삼았습니다 (지력 %d)' % (pg.evaluate('(n) => josa(n, "을를")', dl['top']), dl['int']), '[임명] → %s이(가) 군사가 되고 대화창에서 답한다 ["%s" / %s]' % (dl['top'], t['say'], t['sub']))
    B.shot(pg, 'k06_appoint', 100)
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(300)
    ok(dl['top'] in pg.evaluate('document.querySelector("#sheet .hm-advp").innerText') and pg.evaluate('document.querySelector("#sheet .hm-adv").textContent') == '바꾸기', 'STATUS 창에 새 군사와 그의 한마디, 단추는 [바꾸기]로')
    # 4-3. 조언이 빗나갔을 때: 지력이 낮은 군사 + 지력이 높은 상대 → 적중률 50%. 빗나가게 되어 있는 계략을 골라 쓴다
    s3 = pg.evaluate('''((id) => { function free(c, r) { var t2 = terr(c, r); return inMap(c, r) && (t2 === "p" || t2 === "d") && !unitAt(c, r) && !plotAt(c, r) && !baseAt(c, r); }
      var b = G.bases[id], spot = null, c, r; G.factions[G.player].ap = 300; b.troops = 30000; b.w.spear = 9000; b.food = 80000; baseOfficers(b).forEach(function (o) { o.acted = false; });
      for (c = b.c - 8; c <= b.c + 8 && !spot; c++) for (r = b.r - 8; r <= b.r + 8 && !spot; r++) { if (!free(c, r) || hdist(c, r, b.c, b.r) < 4) continue; var ns = nbrs(c, r).filter(function (n) { return free(n[0], n[1]) && hdist(n[0], n[1], b.c, b.r) >= 4; }); if (ns.length >= 2) spot = { me: [c, r], foe: ns[0] }; }
      var mine = idleOfficers(b).filter(function (o) { return !isLord(o); }).sort(function (x, y) { return y.int - x.int; });
      var dull = facOfficers(G.player).filter(function (o) { return advOk(o, G.player) && o.unit === null; }).sort(function (x, y) { return x.int - y.int; })[0];
      setAdvisor(G.player, dull.id);
      var u = cmdDeploy(b, { type: "spear", ids: [mine[0].id], troops: Math.min(4000, cmdCap(mine[0])), food: 3000 }).unit;
      var eb = G.bases.filter(function (x) { return x.owner >= 0 && x.owner !== G.player && x.kind === "city" && baseOfficers(x).filter(function (o) { return !isLord(o); }).length; })[0];
      var eo = baseOfficers(eb).filter(function (o) { return !isLord(o); }).sort(function (x, y) { return y.int - x.int; })[0]; eb.w.spear = 9000; eb.troops = 20000; G.factions[eb.owner].ap = 300; eo.acted = false;
      var e = cmdDeploy(eb, { type: "spear", ids: [eo.id], troops: Math.min(3000, cmdCap(eo)), food: 3000 }).unit; e.ai = { mode: "return" };
      placeUnit(u, spot.me[0], spot.me[1]); placeUnit(e, spot.foe[0], spot.foe[1]); u.done = false; u.moved = false; u.ox = -1; u.mp = uMaxMp(u); u.morale = 100; u.born = -1;
      var out = null, k, tt = { u: e, c: e.c, r: e.r, kind: "unit" };
      for (k = 0; k < 60 && !out; k++) {                       // 조언과 결과가 어긋나는 턴을 찾는다(둘 다 턴마다 미리 정해져 있다)
        [0, 1, 2].forEach(function (i) { if (out) return; var pl = PLOYS[i], a = ployAdvice(u, pl, tt), real = ployRoll(pl, tt) < ployChance(u, pl, e); if (a && a.says !== real && ployChance(u, pl, e) > 0) out = { i: i, name: pl.name, says: a.says, real: real, acc: a.acc }; });
        if (!out) G.turn++;
      }
      UI.briefT = G.turn; syncScene(); requestDraw(); gotoUnit(u);
      return { u: u.id, e: e.id, p: [e.c, e.r], adv: dull.n, advInt: dull.int, eInt: uInt(e), miss: out, turn: G.turn }; })''', bid)
    pg.wait_for_timeout(700)
    print('  빗나갈 조언:', s3)
    ok(s3['miss'] is not None and s3['miss']['acc'] < 100, '(준비) 군사 %s(지력 %d) · 상대 지력 %d → 적중률 %s%% — 조언과 결과가 어긋나는 계략을 찾았다' % (s3['adv'], s3['advInt'], s3['eInt'], s3['miss'] and s3['miss']['acc']))
    taphex(pg, *s3['p']); pg.wait_for_timeout(500)
    row = pg.evaluate('''(() => { var e = document.querySelector("#sheet .advn"); return e ? { tx: e.innerText.replace(/\\n/g, " / "), por: !!e.querySelector(".por") } : null; })()''')
    ok(row and s3['adv'] in row['tx'] and ('적중률 %d%%' % s3['miss']['acc']) in row['tx'] and row['por'], '부대 창: 군사의 말 한 줄(초상 · 적중률) [%s]' % (row and row['tx']))
    B.shot(pg, 'k07_ploy', 100)
    acts = pg.evaluate('''Array.prototype.map.call(document.querySelectorAll("#sheet [data-a=act]"), function (e) { return e.innerText.replace(/\\n/g, " / "); })''')
    i = [k for k, a in enumerate(acts) if a.startswith(s3['miss']['name'])][0]
    tapsel(pg, '#sheet [data-a=act]', i)
    seen = None
    for _ in range(30):
        pg.wait_for_timeout(250); t = tk(pg)
        if t['on'] and t['who'] == s3['adv']: seen = t; break
    print('  결과:', seen)
    want = '…제 헤아림이 모자랐습니다.' if s3['miss']['says'] else '…뜻밖입니다. 제가 잘못 보았습니다.'
    ok(seen is not None and seen['role'] == '군사' and seen['say'] == want and (s3['miss']['name'] + (' 성공' if s3['miss']['real'] else ' 실패')) in seen['sub'], '조언이 빗나가면 결과와 함께 군사가 한마디 ["%s" / %s]' % (seen and seen['say'], seen and seen['sub']))
    if seen: B.shot(pg, 'k08_miss', 100)

    # ================= 5. 건설 자리를 보는 동안 =================
    pg.wait_for_timeout(1500)
    pg.evaluate('(id) => { clearSel(); talkHide(); var b = G.bases[id]; baseOfficers(b).forEach(function (o) { o.acted = false; }); G.factions[G.player].ap = 300; b.gold = 3000; selectBase(b, false, "fac"); }', bid)
    pg.wait_for_timeout(1200)
    pg.evaluate('''(() => { var L = off(G.factions[G.player].lord); talk(L, "여기에 짓도록 하라.", "시험 — 결과 한 줄"); toast("알림 줄 시험", 3000); })()'''); pg.wait_for_timeout(350)
    t = tk(pg)
    ok('building' in pg.evaluate('document.getElementById("app").className') and t['on'] and t['toastOn'] and t['toastTop'] >= t['bottom'], '건설 자리를 볼 때 대화창과 알림 줄이 함께 떠도 겹치지 않는다(대화창 %d~%d, 알림 줄 %d~)' % (t['top'], t['bottom'], t['toastTop']))
    pg.evaluate('talkHide(); clearSel(); showHome()'); pg.wait_for_timeout(600)
    pg.evaluate('''(() => { var L = off(G.factions[G.player].lord); talk(L, "한마디.", "결과", 4000); })()'''); pg.wait_for_timeout(200)
    pg.evaluate('(id) => { selectBase(G.bases[id], false, "fac"); }', bid); pg.wait_for_timeout(900)
    ok(not tk(pg)['on'], '건설 탭을 열면 앞서 떠 있던 대화창은 닫힌다(칸을 가리지 않게)')
    pg.evaluate('clearSel(); showHome()'); pg.wait_for_timeout(300)

    # ================= 6. 도움말 =================
    pg.evaluate('showHelp()'); pg.wait_for_timeout(300)
    hp = pg.evaluate('document.querySelector("#modal").textContent')
    ok('대화창' in hp and '맡은 무장이' in hp and '군사 임명' in hp or ('대화창' in hp and '임명(바꾸기)' in hp), '도움말: 대화창 · 군사 임명')
    pg.evaluate('closeDialog()')
B.run(steps, 390, 844, 2)
errs = [e for e in B.errors if 'GPU stall' not in e and 'GL Driver' not in e and 'ERR_FILE_NOT_FOUND' not in e and 'willReadFrequently' not in e]
print('console errors:', errs[:6])
print('FAILS %d' % len(fails), fails)
sys.exit(1 if fails or errs else 0)
