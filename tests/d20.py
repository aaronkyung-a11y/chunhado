# v0.10 — 화면 조작으로 확인: 군단(만들기 · 방침 · 군단장 · 거점 창 · 부대 창 · 지도 딱지 · 턴 재생과 보고 · 직할로 되돌리기 · 해산 · 저장)
#   python3 tests/d20.py          찍은 그림은 tests/shots21/
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import taphex, tapsel
B.SHOTS = os.path.join(B.ROOT, 'shots21')
os.makedirs(B.SHOTS, exist_ok=True)
fails = []
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)
TK = '''(() => { var t = document.getElementById("talk"), q = function (c) { var e = t.querySelector(c); return e ? e.textContent : ""; }, to = document.getElementById("toast");
  return { on: t.classList.contains("on"), who: q(".tk-who b"), say: q(".tk-say"), sub: q(".tk-sub"), toast: to.textContent, toastOn: to.classList.contains("on") }; })()'''
def tk(pg): return pg.evaluate(TK)
def txt(pg, sel): return pg.evaluate('(s) => { var e = document.querySelector(s); return e ? e.innerText.replace(/\\n+/g, " / ") : ""; }', sel)
CP = '''(() => { var cp = corpsAll()[0]; if (!cp) return null; var L = corpsLead(cp); return { id: cp.id, name: corpsName(cp), lead: L ? L.n : "", leadId: cp.lead, dir: cp.dir, target: cp.target, tname: cp.target >= 0 ? G.bases[cp.target].n : "", ap: cp.ap, regen: corpsRegen(cp),
  bases: corpsBases(cp).map(function (b) { return b.n; }), units: corpsUnits(cp).map(function (u) { return u.id; }), text: corpsDirText(cp), note: cp.note ? cp.note.s : null }; })()'''
def cp(pg): return pg.evaluate(CP)
def wait_play(pg, limit=180):
    for _ in range(limit * 4):
        pg.wait_for_timeout(250)
        if not pg.evaluate('!!UI.play'): return True
    return False

def steps(pg):
    # ================= 0. 거점이 하나뿐이면 군단은 보이지 않는다 =================
    B.start(pg, 2)                                           # 유비(소패 하나)
    pg.wait_for_timeout(400)
    one = pg.evaluate('''(() => { var b = facCities(G.player)[0]; selectBase(b); return { n: facBases(G.player).length, strip: !!document.querySelector("#sheet .hm-corps"), tabs: Array.prototype.map.call(document.querySelectorAll("#sheet .tabs button"), function (t) { return t.textContent; }) }; })()''')
    pg.evaluate('clearSel(); showHome()'); pg.wait_for_timeout(200)
    one['strip'] = pg.evaluate('!!document.querySelector("#sheet .hm-corps")')
    ok(one['n'] == 1 and not one['strip'] and one['tabs'] == ['내정', '출진', '인재', '건설'], '거점이 하나뿐이면 STATUS 창에 군단 줄이 없고 거점 창에 군단 탭도 없다 %s' % one['tabs'])

    # ================= 1. 군단 만들기 =================
    pg.evaluate('() => { newGame(4, 4242); saveGame(); }')   # 원소: 남피 · 평원 · 업(군주)
    pg.reload(); pg.wait_for_function('window.R3 && R3.ready', timeout=60000); pg.wait_for_timeout(600)
    tapsel(pg, '#tCont'); pg.wait_for_timeout(1500)
    pg.evaluate('talkHide(); clearSel(); showHome()'); pg.wait_for_timeout(300)
    info = pg.evaluate('''(() => { var lb = G.bases[off(G.factions[G.player].lord).loc], cs = facCities(G.player); return { lord: lb.n, lordId: lb.id, others: cs.filter(function (b) { return b !== lb; }).map(function (b) { return [b.id, b.n]; }), ap: G.factions[G.player].ap, regen: apRegen(G.player), ver: GAME_VERSION }; })()''')
    print('  판:', info)
    ok(info['ver'] == 'v0.12', '판 번호 v0.12 [%s]' % info['ver'])
    st = pg.evaluate('''(() => { var s = document.querySelector("#sheet .hm-corps"); return s ? { n: s.querySelectorAll(".cpb").length, nw: s.querySelector(".cpb.new") ? s.querySelector(".cpb.new").innerText.replace(/\\n+/g, " / ") : "", before: s.previousElementSibling.className, after: s.nextElementSibling.textContent.slice(0, 5) } : null; })()''')
    ok(st and st['n'] == 1 and '+ 군단' in st['nw'] and 'hm-advp' in st['before'] and st['after'].startswith('지금 할'), 'STATUS 창: 군사의 자리 아래에 [+ 군단] 한 칸 [%s]' % (st and st['nw']))
    B.shot(pg, 'c01_home', 200)
    tapsel(pg, '#sheet .cpb.new'); pg.wait_for_timeout(400)
    nw = pg.evaluate('''(() => { var m = document.getElementById("modal"); return { h: m.querySelector(".dlg-h").textContent, rows: Array.prototype.map.call(m.querySelectorAll(".row[data-a=b]"), function (e) { return e.innerText.replace(/\\n+/g, " / "); }), okDis: m.querySelector("[data-a=ok]").disabled, pv: m.querySelector(".pv").textContent }; })()''')
    ok('새 군단' in nw['h'] and len(nw['rows']) == 3 and nw['okDis'] and any(info['lord'] in r and '군주' in r for r in nw['rows']), "'새 군단 — 맡길 거점': 직할 거점 3곳, 군주가 있는 곳에는 딱지, 고르기 전에는 [군단 만들기]가 꺼져 있다 %s" % nw['rows'])
    for bid, _ in info['others']: tapsel(pg, '#modal .row[data-a=b][data-v="%d"]' % bid)
    pg.wait_for_timeout(200)
    sel = pg.evaluate('''(() => { var m = document.getElementById("modal"); return { n: m.querySelectorAll(".row.sel").length, pv: m.querySelector(".pv").textContent, okDis: m.querySelector("[data-a=ok]").disabled }; })()''')
    ok(sel['n'] == 2 and '2' in sel['pv'] and not sel['okDis'], '두 곳을 고르면 "거점 2곳" [%s]' % sel['pv'])
    B.shot(pg, 'c02_new', 200)
    tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(600)
    c = cp(pg); t = tk(pg)
    print('  군단:', c, t)
    ok(c and c['name'] == '제1군단' and sorted(c['bases']) == sorted(n for _, n in info['others']) and c['dir'] == 'arm' and c['lead'], '제1군단이 생긴다 — 거점 %s, 군단장 %s, 방침은 군비로 시작' % (c and c['bases'], c and c['lead']))
    ok(t['on'] and t['who'] == c['lead'] and len(t['say']) >= 6 and '거점 2곳을 맡았습니다' in t['sub'], '군단장이 대화창에서 답한다 ["%s" / %s]' % (t['say'], t['sub']))
    d = pg.evaluate('''(() => { var m = document.getElementById("modal"); return m.classList.contains("on") ? { h: m.querySelector(".dlg-h").textContent, card: m.querySelector(".cpc").innerText.replace(/\\n+/g, " / "), dirs: Array.prototype.map.call(m.querySelectorAll(".cpd .opt"), function (e) { return [e.getAttribute("data-v"), e.classList.contains("on"), e.innerText.replace(/\\n+/g, " / ")]; }), bases: m.querySelectorAll("[data-a=rel]").length, por: !!m.querySelector(".cpc .por") } : null; })()''')
    ok(d and '제1군단' in d['h'] and c['lead'] in d['card'] and ('행동력 %d' % c['ap']) in d['card'] and ('+%d/턴' % c['regen']) in d['card'] and d['por'], '군단 창이 바로 열린다: 군단장 · 행동력 · 병력 [%s]' % (d and d['card']))
    ok(d and [x[0] for x in d['dirs']] == ['dev', 'arm', 'atk', 'sup'] and [x[1] for x in d['dirs']] == [False, True, False, False] and d['bases'] == 2, '방침 넷(내정 · 군비 · 공격 · 지원) 가운데 군비가 켜져 있고, 거점마다 [직할로] %s' % (d and [x[2] for x in d['dirs']]))
    B.shot(pg, 'c03_corps', 200)
    ap1 = pg.evaluate('[apRegen(G.player), G.factions[G.player].ap]')
    ok(ap1[0] == info['regen'] - 16 and ap1[1] == info['ap'], '맡긴 도시 둘은 내 행동력 회복에서 빠진다(%d → %d), 지금의 행동력은 그대로' % (info['regen'], ap1[0]))

    # ================= 2. 방침 =================
    tapsel(pg, '#modal .cpd .opt[data-v=dev]'); pg.wait_for_timeout(350)
    c = cp(pg); t = tk(pg)
    ok(c['dir'] == 'dev' and t['on'] and t['who'] == c['lead'] and '내정' in t['sub'] and pg.evaluate('document.querySelector("#modal .cpd .opt.on").getAttribute("data-v")') == 'dev', '내정을 누르면 바로 바뀌고 군단장이 답한다 ["%s" / %s]' % (t['say'], t['sub']))
    # 공격: 목표 고르기
    tapsel(pg, '#modal .cpd .opt[data-v=atk]'); pg.wait_for_timeout(400)
    tg = pg.evaluate('''(() => { var m = document.getElementById("modal"), cp = corpsAll()[0]; return { h: m.querySelector(".dlg-h").textContent, cap: m.querySelector(".cap").textContent,
      rows: Array.prototype.map.call(m.querySelectorAll(".row[data-a=t]"), function (e) { var b = G.bases[+e.getAttribute("data-v")], o = corpsOutlook(cp, b); return { id: b.id, n: b.n, own: b.owner, t: e.innerText.replace(/\\n+/g, " / "), need: o.need, len: o.len, have: o.have, ok: e.querySelector(".rt").classList.contains("ok"), brk: peaceWouldBreak(b.owner) }; }), depth: MSTACK.length }; })()''')
    print('  목표:', [(r['n'], r['need'], r['len']) for r in tg['rows'][:6]])
    ok('어디를 칠까요' in tg['h'] and tg['depth'] == 1 and 6 <= len(tg['rows']) <= 14 and all(r['own'] != 4 for r in tg['rows']), '공격을 누르면 목표를 고르는 창(군단 창 위에) — 내 거점이 아닌 곳 %d곳' % len(tg['rows']))
    ok([r['len'] for r in tg['rows']] == sorted(r['len'] for r in tg['rows']), '가까운 곳부터')
    ok(all(('필요 {:,}'.format(r['need'])) in r['t'].replace(' / ', ' ') for r in tg['rows']) and ('{:,}'.format(tg['rows'][0]['have'])) in tg['cap'], "줄마다 '필요' 병력(= 군단장이 나서는 문턱), 위에는 지금 낼 수 있는 병력 [%s]" % tg['rows'][0]['t'])
    ok(all(r['ok'] == (r['have'] >= r['need']) for r in tg['rows']), '지금 나설 수 있는 곳은 초록')
    ok(all(('보호가 풀림' in r['t']) == r['brk'] for r in tg['rows']) and any(r['brk'] for r in tg['rows']), '먼저 치면 보호가 풀리는 세력의 거점에는 그렇게 적힌다')
    B.shot(pg, 'c04_target', 200)
    emp = [r for r in tg['rows'] if r['own'] < 0]
    pickT = emp[0] if emp else tg['rows'][0]
    tapsel(pg, '#modal .row[data-a=t][data-v="%d"]' % pickT['id']); pg.wait_for_timeout(450)
    c = cp(pg); t = tk(pg)
    g = pg.evaluate('''(() => { var m = document.getElementById("modal"), g = m.querySelector(".cpg"); return { h: m.querySelector(".dlg-h").textContent, g: g ? g.innerText.replace(/\\n+/g, " / ") : "", depth: MSTACK.length, on: m.querySelector(".cpd .opt.on").getAttribute("data-v") }; })()''')
    ok(c['dir'] == 'atk' and c['target'] == pickT['id'] and c['text'] == '공격 → ' + pickT['n'] and g['depth'] == 0 and '제1군단' in g['h'] and g['on'] == 'atk', '고르면 군단 창으로 돌아오고 방침은 "%s"' % c['text'])
    ok(pickT['n'] in g['g'] and ('나섭니다' in g['g'] or '낼 수 있는 병력' in g['g'] or '보낼 병력' in g['g']), '군단 창에 목표와 지금 나설 수 있는지가 적힌다 [%s]' % g['g'])
    ok(t['on'] and t['who'] == c['lead'] and pickT['n'] in t['say'] and ('공격 → ' + pickT['n']) in t['sub'], '군단장: "%s" / %s' % (t['say'], t['sub']))
    B.shot(pg, 'c05_attack', 200)
    # 지원: 보낼 곳 고르기
    tapsel(pg, '#modal .cpd .opt[data-v=sup]'); pg.wait_for_timeout(400)
    ds = pg.evaluate('''Array.prototype.map.call(document.querySelectorAll("#modal .row[data-a=d]"), function (e) { return [+e.getAttribute("data-v"), e.innerText.replace(/\\n+/g, " / ")]; })''')
    ok(len(ds) == 1 and ds[0][0] == info['lordId'] and '직할' in ds[0][1], '지원을 누르면 보낼 곳을 고르는 창 — 이 군단 밖의 내 거점 %s' % ds)
    tapsel(pg, '#modal .row[data-a=d]', 0); pg.wait_for_timeout(450)
    c = cp(pg); t = tk(pg)
    ok(c['dir'] == 'sup' and c['target'] == info['lordId'] and t['on'] and info['lord'] in t['say'] and ('지원 → ' + info['lord']) in t['sub'], '지원 → %s ["%s"]' % (info['lord'], t['say']))
    ok(pg.evaluate('document.querySelector("#modal .cpg").innerText').find('한 달에 한 번') >= 0, '군단 창에 보낼 곳과 "한 달에 한 번"')
    # 군비로
    tapsel(pg, '#modal .cpd .opt[data-v=arm]'); pg.wait_for_timeout(300)
    ok(cp(pg)['dir'] == 'arm' and pg.evaluate('!document.querySelector("#modal .cpg")'), '군비로 돌리면 목표 줄이 사라진다')

    # ================= 3. 군단장 바꾸기 =================
    tapsel(pg, '#modal [data-a=lead]'); pg.wait_for_timeout(400)
    ld = pg.evaluate('''(() => { var m = document.getElementById("modal"), cp = corpsAll()[0]; return { h: m.querySelector(".dlg-h").textContent, rows: Array.prototype.map.call(m.querySelectorAll(".tr[data-a=pick]"), function (e) { return +e.getAttribute("data-v"); }), cands: corpsLeadCands(cp).map(function (o) { return o.id; }), names: corpsLeadCands(cp).map(function (o) { return o.n; }) }; })()''')
    ok('군단장' in ld['h'] and ld['rows'] == ld['cands'] and len(ld['rows']) >= 4, '군단장을 고르는 표: 군단의 거점에 있는 무장 %d명(알맞은 순)' % len(ld['rows']))
    newL = [i for i in ld['cands'] if i != c['leadId']][0]
    tapsel(pg, '#modal .tr[data-a=pick][data-v="%d"]' % newL); pg.wait_for_timeout(200)
    pv = txt(pg, '#modal .dlg-f .pv')
    tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(500)
    c2 = cp(pg); t = tk(pg)
    ok(c2['leadId'] == newL and t['on'] and t['who'] == c2['lead'] and '군단장이 되었습니다' in t['sub'] and '행동력 +' in pv, '군단장을 바꾼다 → %s ["%s" / %s] (고를 때 아래 줄: %s)' % (c2['lead'], t['say'], t['sub'], pv))
    ok(pg.evaluate('!!MODAL') and c2['lead'] in txt(pg, '#modal .cpc'), '군단 창으로 돌아와 새 군단장이 보인다')
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(300)

    # ================= 4. STATUS 창 · 지도 · 거점 창 =================
    pg.evaluate('talkHide(); clearSel(); showHome()'); pg.wait_for_timeout(400)
    hs = pg.evaluate('''(() => { var s = document.querySelector("#sheet .hm-corps"); return { chips: Array.prototype.map.call(s.querySelectorAll(".cpb"), function (e) { return e.innerText.replace(/\\n+/g, " / "); }), por: !!s.querySelector(".cpb .por"),
      todo: Array.prototype.map.call(document.querySelectorAll("#sheet .todo"), function (e) { return e.innerText.replace(/\\n+/g, " / "); }) }; })()''')
    ok(len(hs['chips']) == 2 and '제1군단' in hs['chips'][0] and '군비' in hs['chips'][0] and hs['por'] and '+ 군단' in hs['chips'][1], 'STATUS 창의 군단 줄: [제1군단 · 군비] [+ 군단] %s' % hs['chips'])
    ok(not any(n in ' '.join(hs['todo']) for _, n in info['others']) and info['lord'] in ' '.join(hs['todo']), "'지금 할 일'에는 직할 거점(%s)만 — 맡긴 거점의 쉬는 무장은 나오지 않는다" % info['lord'])
    lab = pg.evaluate('''((ids) => ids.map(function (id) { return R3.bases[id].sig; }).concat([R3.bases[facCities(G.player).filter(function (b) { return !b.corps; })[0].id].sig]))''', [b for b, _ in info['others']])
    ok(all(s.endswith('|1') for s in lab[:2]) and lab[2].endswith('|'), '지도의 이름표: 맡긴 거점에는 군단 번호 딱지(①), 직할 거점에는 없다 %s' % lab)
    pg.evaluate('(id) => { var b = G.bases[id]; jumpTo(b.c, b.r, 0.6); }', info['others'][0][0]); pg.wait_for_timeout(600)
    B.shot(pg, 'c06_map', 300)
    tapsel(pg, '#sheet .cpb[data-a=corps]'); pg.wait_for_timeout(350)
    ok('제1군단' in txt(pg, '#modal .dlg-h'), 'STATUS 창의 군단 칸을 누르면 군단 창')
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(200)
    # 맡긴 거점의 창
    bid, bn = info['others'][0]
    pg.evaluate('(id) => { selectBase(G.bases[id]); }', bid); pg.wait_for_timeout(700)
    bs = pg.evaluate('''(() => { var s = document.getElementById("sheet"); return { bn: s.querySelector(".cpbn") ? s.querySelector(".cpbn").innerText.replace(/\\n+/g, " / ") : "", tabs: s.querySelectorAll(".tabs button").length, cmds: Array.prototype.map.call(s.querySelectorAll(".cmd"), function (e) { return e.getAttribute("data-a"); }), rows: s.querySelectorAll(".rows .row").length, spot: !!buildView() }; })()''')
    ok('제1군단' in bs['bn'] and '군비' in bs['bn'] and c2['lead'] in bs['bn'] and bs['tabs'] == 0 and bs['cmds'] == ['corps', 'direct'] and bs['rows'] >= 1 and not bs['spot'], '맡긴 거점의 창: 명령 탭 대신 군단 띠 + [군단] · [직할로], 무장 목록은 그대로 [%s]' % bs['bn'])
    B.shot(pg, 'c07_base', 200)
    plot = pg.evaluate('(id) => { var b = G.bases[id], p = b.plots.filter(function (q) { return !q.fac; })[0]; return [p.c, p.r]; }', bid)
    taphex(pg, *plot); pg.wait_for_timeout(400)
    ok(pg.evaluate('!MODAL') and pg.evaluate('UI.sel && UI.sel.kind === "base"'), '맡긴 거점의 빈 부지를 눌러도 건설 창은 열리지 않는다')
    tapsel(pg, '#sheet [data-a=corps]'); pg.wait_for_timeout(300)
    ok('제1군단' in txt(pg, '#modal .dlg-h'), '[군단] → 군단 창')
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(200)
    tapsel(pg, '#sheet [data-a=direct]'); pg.wait_for_timeout(400)
    c3 = cp(pg); t = tk(pg)
    ok(c3 and c3['bases'] == [info['others'][1][1]] and pg.evaluate('(id) => !G.bases[id].corps', bid) and '직할로 되돌렸습니다' in t['toast'] and pg.evaluate('document.querySelectorAll("#sheet .tabs button").length') == 5, '[직할로] → 바로 직할(명령 탭이 돌아온다: 다섯째는 군단) [%s]' % t['toast'])
    # 직할 거점의 '군단' 탭 → 다시 맡기기
    tapsel(pg, '#sheet .tabs button[data-v=corps]'); pg.wait_for_timeout(300)
    ct = pg.evaluate('''(() => { var s = document.getElementById("sheet"); return { rows: Array.prototype.map.call(s.querySelectorAll(".rows .row"), function (e) { return e.innerText.replace(/\\n+/g, " / "); }), nw: !!s.querySelector("[data-a=cnew]"), note: s.querySelector(".note").textContent }; })()''')
    ok(len(ct['rows']) == 1 and '제1군단' in ct['rows'][0] and '맡기기' in ct['rows'][0] and ct['nw'] and '직할 거점' in ct['note'], "직할 거점의 '군단' 탭: 있는 군단마다 [맡기기] + [새 군단] %s" % ct['rows'])
    B.shot(pg, 'c08_tab', 200)
    tapsel(pg, '#sheet [data-a=cjoin]'); pg.wait_for_timeout(450)
    c4 = cp(pg); t = tk(pg)
    ok(sorted(c4['bases']) == sorted(n for _, n in info['others']) and t['on'] and '제1군단에 맡겼습니다' in t['sub'] and pg.evaluate('!!document.querySelector("#sheet .cpbn")'), '[맡기기] → 다시 군단의 거점 [%s]' % t['sub'])
    pg.evaluate('talkHide(); clearSel(); showHome()'); pg.wait_for_timeout(300)

    # ================= 5. 턴을 넘기면 군단이 움직인다 =================
    # 가장 가까운 남의 도시를 치게 한다. 시험이라 그 도시의 수비를 얇게 묶어 두고(턴마다 1,500 으로), 군단에는 넉넉한 병력과 행동력을 준다
    # (지키는 장수가 뛰어나면 문턱이 높다 — 북평의 조운이면 1.42배. 그래서 병력을 24,000 씩 준다)
    PREP = '''((tid) => { var cp = corpsAll()[0], T = G.bases[tid]; if (T.owner !== G.player) T.troops = Math.min(T.troops, 1500);
      if (cp) { cp.ap = Math.max(cp.ap, 120); corpsBases(cp).forEach(function (b) { if (b.id === tid) return; b.troops = Math.max(b.troops, 24000); b.morale = 80; b.food = Math.max(b.food, 200000); b.gold = Math.max(b.gold, 5000); b.w.spear = Math.max(b.w.spear, 9000); b.w.halberd = Math.max(b.w.halberd, 9000); b.w.bow = Math.max(b.w.bow, 9000); }); } })'''
    e = pg.evaluate('''(() => { var cp = corpsAll()[0], L = G.bases.filter(function (b) { return b.owner >= 0 && b.owner !== G.player && b.kind === "city"; }).map(function (b) { return [b, corpsOutlook(cp, b).len]; }).sort(function (x, y) { return x[1] - y[1]; }), E = L[0][0];
      corpsSetDir(cp, "atk", E.id); UI.pspeed = 1; return { id: E.id, n: E.n, len: L[0][1], own: facName(E.owner) }; })()''')
    pg.evaluate(PREP, e['id'])
    print('  목표:', e)
    d0 = pg.evaluate('[G.factions[G.player].ap, G.turn, pendingUnits().length]')
    tapsel(pg, '#btnEnd'); pg.wait_for_timeout(300)
    chips = set()
    for _ in range(400):
        pg.wait_for_timeout(150)
        if not pg.evaluate('!!UI.play'): break
        chips.add(pg.evaluate('document.getElementById("plFac").textContent'))
    print('  재생 중 자막의 칩:', sorted(chips)[:8])
    ok(any('제1군단' in x for x in chips), '턴 재생: 군단의 차례에는 세력 칩에 군단 이름이 붙는다')
    pg.wait_for_timeout(600)
    rp = pg.evaluate('''(() => { var m = document.getElementById("modal"); if (!m.classList.contains("on")) return null; var secs = Array.prototype.map.call(m.querySelectorAll(".sec"), function (e) { return e.textContent; }), row = null;
      Array.prototype.forEach.call(m.querySelectorAll(".row.rep"), function (e) { if (/제1군단 \\(/.test(e.textContent)) row = { t: e.innerText.replace(/\\n+/g, " / "), por: !!e.querySelector(".por"), sec: (function () { var p = e.parentElement.previousElementSibling; return p ? p.textContent : ""; })() }; });
      return { h: m.querySelector(".dlg-h").textContent, secs: secs, row: row }; })()''')
    print('  보고:', rp)
    ok(rp and '지난 열흘' in rp['h'] and rp['row'] and rp['row']['sec'] == '군단' and rp['row']['por'] and ('공격 → ' + e['n']) in rp['row']['t'], "지난 열흘의 일: '군단' 토막에 한 줄(군단장의 초상 · 방침 · 한 일) [%s]" % (rp and rp['row'] and rp['row']['t']))
    ok(rp and rp['row'] and ('출진' in rp['row']['t'] or '징병' in rp['row']['t'] or '착공' in rp['row']['t']), '한 일이 적혀 있다')
    B.shot(pg, 'c09_report', 200)
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(400)
    c5 = cp(pg)
    ok(len(c5['units']) >= 2 and pg.evaluate('G.turn') == d0[1] + 1, '군단이 부대 %d개를 냈다(%s을(를) 치러)' % (len(c5['units']), e['n']))
    ok(pg.evaluate('pendingUnits().length') == 0 and not any('명령 대기' in x for x in pg.evaluate('Array.prototype.map.call(document.querySelectorAll("#sheet .todo"), function (e) { return e.innerText; })')), "군단의 부대는 '명령 대기'에 들지 않는다")
    # 부대 창
    uid = c5['units'][0]
    pg.evaluate('(id) => { talkHide(); gotoUnit(UMAP[id]); }', uid); pg.wait_for_timeout(700)
    us = pg.evaluate('''((id) => { var s = document.getElementById("sheet"), u = UMAP[id]; return { bn: s.querySelector(".cpbn") ? s.querySelector(".cpbn").innerText.replace(/\\n+/g, " / ") : "", cmds: Array.prototype.map.call(s.querySelectorAll(".cmd"), function (e) { return e.getAttribute("data-a"); }), acts: s.querySelectorAll(".act").length, rc: !!UI.rc, sig: R3.units[id].sig.split("|")[0], pos: [u.c, u.r] }; })''', uid)
    ok('제1군단' in us['bn'] and (e['n'] + ' 공격') in us['bn'] and us['cmds'] == ['corps', 'direct'] and us['acts'] == 0 and not us['rc'] and us['sig'] == '1', '군단의 부대 창: 하는 일("%s 공격")과 [군단] · [직할로] — 이동 칸도 명령 단추도 없다 [%s]' % (e['n'], us['bn']))
    B.shot(pg, 'c10_unit', 200)
    nb = pg.evaluate('''((id) => { var u = UMAP[id], ns = nbrs(u.c, u.r).filter(function (n) { return inMap(n[0], n[1]) && !unitAt(n[0], n[1]) && !baseAt(n[0], n[1]) && !plotAt(n[0], n[1]) && MC[clsIdx(u)][K(n[0], n[1])] < 99; }); return ns[0]; })''', uid)
    if nb:
        taphex(pg, *nb); pg.wait_for_timeout(400)
        ok(pg.evaluate('(id) => [UMAP[id].c, UMAP[id].r]', uid) == us['pos'], '옆 칸을 눌러도 군단의 부대는 움직이지 않는다')
        pg.evaluate('(id) => { gotoUnit(UMAP[id]); }', uid); pg.wait_for_timeout(500)
    tapsel(pg, '#sheet [data-a=direct]'); pg.wait_for_timeout(450)
    ud = pg.evaluate('''((id) => { var u = UMAP[id]; return { corps: u.corps || 0, ai: u.ai, rc: !!UI.rc, acts: document.querySelectorAll("#sheet .act").length, pend: pendingUnits().length, sig: R3.units[id].sig.split("|")[0], toast: document.getElementById("toast").textContent }; })''', uid)
    ok(ud['corps'] == 0 and ud['ai'] is None and ud['rc'] and ud['acts'] >= 2 and ud['pend'] == 1 and ud['sig'] == '' and '직할로 되돌렸습니다' in ud['toast'], '[직할로] → 내 부대가 된다(이동 칸 · 명령 단추 · 명령 대기 1) [%s]' % ud['toast'])
    pg.evaluate('(id) => { var u = UMAP[id], cp = corpsAll()[0]; u.corps = cp.id; u.ai = { mode: "attack", target: cp.target, home: u.home }; clearSel(); showHome(); syncScene(); }', uid); pg.wait_for_timeout(300)

    # ================= 6. 차지한 거점은 군단에 든다 =================
    got = False
    pg.evaluate('UI.pspeed = 0')                              # 재생은 요약만(빠르게)
    for k in range(14):
        if pg.evaluate('(id) => G.bases[id].owner === G.player', e['id']): got = True; break
        pg.evaluate(PREP, e['id'])
        tapsel(pg, '#btnEnd'); pg.wait_for_timeout(200)
        if pg.evaluate('!UI.play && !MODAL'): tapsel(pg, '#btnEnd')
        ok_done = wait_play(pg)
        pg.wait_for_timeout(300)
        if pg.evaluate('!!MODAL'): pg.evaluate('closeDialog()'); pg.wait_for_timeout(200)
        if pg.evaluate('!!G.over'): break
    got = pg.evaluate('(id) => G.bases[id].owner === G.player', e['id'])
    c6 = cp(pg)
    print('  차지:', got, c6)
    ok(got and e['n'] in c6['bases'] and c6['dir'] == 'arm', '%s군의 %s을(를) 차지해 제1군단의 거점이 되고, 방침은 군비로 돌아갔다 %s' % (e['own'], e['n'], c6['bases']))
    lg = pg.evaluate('G.log.filter(function (x) { return /손에 넣어 방침을 군비로/.test(x.t); }).map(function (x) { return x.t; })')
    ok(len(lg) == 1 and e['n'] in lg[0], '기록에 남는다 [%s]' % (lg[0] if lg else ''))
    ok(pg.evaluate('(id) => R3.bases[id].sig', e['id']).endswith('|1'), '새 거점의 이름표에도 군단 딱지')

    # ================= 7. 저장 · 이어서 하기 =================
    pg.evaluate('saveGame()'); pg.reload(); pg.wait_for_function('window.R3 && R3.ready', timeout=60000); pg.wait_for_timeout(600)
    tapsel(pg, '#tCont'); pg.wait_for_timeout(1500)
    pg.evaluate('talkHide(); clearSel(); showHome()'); pg.wait_for_timeout(300)
    c7 = cp(pg)
    ok(c7 and c7['bases'] == c6['bases'] and c7['lead'] == c6['lead'] and '제1군단' in txt(pg, '#sheet .hm-corps') and pg.evaluate('(id) => R3.bases[id].sig', e['id']).endswith('|1'), '다시 들어와도 군단이 그대로(거점 · 군단장 · STATUS 창 · 지도 딱지)')

    # ================= 8. 해산 =================
    tapsel(pg, '#sheet .cpb[data-a=corps]'); pg.wait_for_timeout(350)
    tapsel(pg, '#modal [data-a=disband]'); pg.wait_for_timeout(250)
    mid = pg.evaluate('[corpsAll().length, document.querySelector("#modal [data-a=disband] b").textContent]')
    ok(mid == [1, '정말 해산?'], '[해산]은 한 번 더 묻는다 %s' % mid)
    tapsel(pg, '#modal [data-a=disband]'); pg.wait_for_timeout(450)
    fin = pg.evaluate('''(() => ({ n: corpsAll().length, direct: directBases(G.player).length, all: facBases(G.player).length, modal: !!MODAL, toast: document.getElementById("toast").textContent, regen: apRegen(G.player), cities: facCities(G.player).length, strip: Array.prototype.map.call(document.querySelectorAll("#sheet .cpb"), function (e) { return e.innerText.replace(/\\n+/g, " / "); }), marks: G.bases.filter(function (b) { return b.corps; }).length, umarks: G.units.filter(function (u) { return u.corps; }).length }))()''')
    ok(fin['n'] == 0 and fin['direct'] == fin['all'] and not fin['modal'] and '해산' in fin['toast'] and fin['marks'] == 0 and fin['umarks'] == 0 and len(fin['strip']) == 1 and '+ 군단' in fin['strip'][0], '해산 → 거점 %d곳과 부대가 모두 직할로, STATUS 창에는 [+ 군단]만 [%s]' % (fin['all'], fin['toast']))
    ok(fin['regen'] == min(160, info['regen'] - 24 + 8 * fin['cities']), '내 행동력 회복도 도시 %d곳을 모두 센다(+%d/턴)' % (fin['cities'], fin['regen']))

    # ================= 9. 도움말 =================
    pg.evaluate('showHelp()'); pg.wait_for_timeout(300)
    hp = pg.evaluate('document.querySelector("#modal").textContent')
    ok('군단' in hp and '방침' in hp and '직할로' in hp and '제 행동력' in hp, '도움말: 군단')
    pg.evaluate('closeDialog()')
B.run(steps, 390, 844, 2)
errs = [e for e in B.errors if 'GPU stall' not in e and 'GL Driver' not in e and 'ERR_FILE_NOT_FOUND' not in e and 'willReadFrequently' not in e]
print('console errors:', errs[:6])
print('FAILS %d' % len(fails), fails)
sys.exit(1 if fails or errs else 0)
