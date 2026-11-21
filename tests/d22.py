# v0.11 — 화면 조작으로 확인: 공유 · 시설의 레벨 표시 · 무장 줄의 적성 · 치안 풀이 · 출진 군량 · 등용과 옛 관계 · 수송대의 보급 · 군사의 헌책 · 탐색 조언 · 확대한 지도
#   python3 tests/d22.py          찍은 그림은 tests/shots24/
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import taphex, tapsel
B.SHOTS = os.path.join(B.ROOT, 'shots24')
os.makedirs(B.SHOTS, exist_ok=True)
fails = []
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)
def txt(pg, sel): return pg.evaluate('(s) => { var e = document.querySelector(s); return e ? e.innerText.replace(/\\n+/g, " / ") : ""; }', sel)
def toast(pg): return pg.evaluate('$("toast").textContent')
def head(pg): return pg.evaluate('MODAL ? document.querySelector("#modal .dlg-h").textContent.replace("×", "") : ""')
def reload(pg):
    pg.reload(); pg.wait_for_function('window.R3 && R3.ready', timeout=60000); pg.wait_for_timeout(600)
def fresh(pg, fac, seed):                                   # 정해진 세력 · 씨앗으로 새 판을 열어 들어간다
    pg.evaluate('([f, s]) => { localStorage.clear(); newGame(f, s); saveGame(); }', [fac, seed]); reload(pg)
    tapsel(pg, '#tCont'); pg.wait_for_timeout(1300)
    if pg.evaluate('!!MODAL'): pg.evaluate('closeDialog()')
    pg.evaluate('talkHide()'); pg.wait_for_timeout(200)
def setrange(pg, sel, v):
    pg.evaluate('([s, v]) => { var r = document.querySelector(s); r.value = v; r.dispatchEvent(new Event("input", { bubbles: true })); }', [sel, v]); pg.wait_for_timeout(200)
def qr_read(path):
    import cv2
    im = cv2.imread(path); im = cv2.resize(im, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST)
    val, _, _ = cv2.QRCodeDetector().detectAndDecode(im)
    return val
FACSET = '''(() => {
  var b = facCities(G.player)[0], F = function (t, lv) { return { t: t, lv: lv || 1, done: true, prog: 0, need: 0, rate: 0, hp: FAC_HP }; };
  function adj(i) { var p = b.plots[i], out = []; nbrs(p.c, p.r).forEach(function (n) { var q = PAT[K(n[0], n[1])]; if (q && q.b === b.id) out.push(q.i); }); return out; }
  b.plots.forEach(function (p) { p.fac = null; });
  var A = -1, best = 0; for (var i = 0; i < b.plots.length; i++) { var n = adj(i).length; if (n > best) { best = n; A = i; } }
  var ns = adj(A), used = {}; used[A] = 1;
  b.plots[A].fac = F('market', 2); b.plots[ns[0]].fac = F('market', 1); used[ns[0]] = 1; b.plots[ns[1]].fac = F('mint', 1); used[ns[1]] = 1;
  var rest = []; for (i = 0; i < b.plots.length; i++) if (!used[i] && adj(i).indexOf(A) < 0 && adj(i).indexOf(ns[0]) < 0) rest.push(i);
  var plan = [F('farm', 3), F('barracks', 2), F('barracks', 1), F('smithy', 1), F('workshop', 1), F('stable', 3)];
  for (i = 0; i < plan.length && i < rest.length; i++) b.plots[rest[i]].fac = plan[i];
  // 곡창: 농장과 붙지 않은 자리에(보탬이 없다는 말이 나와야 한다)
  var farmI = rest[0], gi = -1; for (i = plan.length; i < rest.length; i++) if (adj(rest[i]).indexOf(farmI) < 0) { gi = rest[i]; break; }
  if (gi >= 0) b.plots[gi].fac = F('granary', 1);
  G.factions[G.player].ap = 235; b.gold = 2400; b.order = 64; b.food = 9000; b.troops = 14000; b.w.spear = 9000; b.w.horse = 4000; reindex(); selectBase(b); UI.dirty = true; requestDraw();
  return { id: b.id, n: b.n, A: A, m1: ns[0], mint: ns[1], gran: gi, laid: Math.min(plan.length, rest.length) };
})()'''
def steps(pg):
    # ================= 1. 공유 =================
    print('1. 공유')
    ok(pg.evaluate('!!$("tShare") && !!$("tHelp") && $("tVer").textContent.indexOf("v0.17") === 0'), '제목 화면: [공유] 단추와 판 번호 v0.17 — ' + pg.evaluate('$("tVer").textContent'))
    tapsel(pg, '#tShare'); pg.wait_for_timeout(600)
    sh = pg.evaluate('({ title: MODAL ? document.querySelector("#modal .dlg-h").textContent : "", url: $("shU") ? $("shU").value : "", want: SHARE_URL, qr: !!document.querySelector("#modal svg.qr path"), send: !!document.querySelector("#modal [data-a=send]"), nat: typeof navigator.share })')
    ok(sh['title'].startswith('공유') and sh['url'] == sh['want'] == 'https://aaronkyung-a11y.github.io/chunhado/', '공유 창: 공유 창이 없는 브라우저에서는 주소가 적힌 창이 뜬다 %s' % sh)
    ok(sh['qr'] and not sh['send'], 'QR이 그려지고, 공유 창이 없으면 [보내기]는 없다')
    pg.locator('#modal svg.qr').screenshot(path=os.path.join(B.SHOTS, 'q1_qr.png'))
    q = qr_read(os.path.join(B.SHOTS, 'q1_qr.png'))
    ok(q == sh['want'], '화면의 QR을 읽으면 그 주소다: %r' % q)
    tapsel(pg, '#modal [data-a=copy]'); pg.wait_for_timeout(300)
    ok('복사' in toast(pg), '[주소 복사] → ' + toast(pg))
    B.shot(pg, 'q1_share', 200)
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(200)
    # 공유 창이 있는 기기(v0.12: 늘 주소 창이 먼저 뜨고, [보내기]가 그 창을 부른다) / 막혀 있으면 알림 / 닫으면 아무 일도 없다
    pg.evaluate('(() => { navigator.share = function (d) { window._sh = d; return Promise.resolve(); }; })()')
    tapsel(pg, '#tShare'); pg.wait_for_timeout(400)
    ok(head(pg).startswith('공유') and pg.evaluate('!!document.querySelector("#modal [data-a=send]") && !window._sh'), '공유 창이 있는 기기: 주소 창이 먼저 뜨고 [보내기]가 있다')
    tapsel(pg, '#modal [data-a=send]'); pg.wait_for_timeout(400)
    s2 = pg.evaluate('({ d: window._sh || null, modal: !!MODAL })')
    ok(s2['d'] and s2['d']['url'] == sh['want'] and '천하도' in s2['d']['title'], '[보내기]: 공유 창에 제목 · 글 · 주소를 넘긴다 %s' % s2)
    pg.evaluate('(() => { navigator.share = function () { return Promise.reject(new DOMException("no", "NotAllowedError")); }; })()')
    tapsel(pg, '#modal [data-a=send]'); pg.wait_for_timeout(500)
    ok(head(pg).startswith('공유') and '복사' in toast(pg), '공유 창이 막혀 있으면(아티팩트 안 등) 알리고 주소 창에 그대로 있다 — ' + toast(pg))
    pg.evaluate('(() => { $("toast").textContent = ""; navigator.share = function () { return Promise.reject(new DOMException("x", "AbortError")); }; })()')
    tapsel(pg, '#modal [data-a=send]'); pg.wait_for_timeout(500)
    ok(head(pg).startswith('공유') and toast(pg) == '', '공유 창을 그냥 닫으면 아무 알림도 없다')
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(200)
    pg.evaluate('(() => { delete navigator.share; })()')

    # ================= 2. 시설의 레벨 표시 =================
    print('2. 시설의 레벨 표시')
    fresh(pg, 13, 4242)
    pg.evaluate('showMenu()'); pg.wait_for_timeout(300)
    ok('v0.17' in head(pg) and pg.evaluate('!!document.querySelector("#modal [data-a=share]")'), '메뉴: ' + head(pg) + ' · [공유]')
    pg.evaluate('closeDialog()')
    S = pg.evaluate(FACSET); print('   ', S); pg.wait_for_timeout(600)
    pg.locator('#sheet .tabs button').nth(3).tap(); pg.wait_for_timeout(1000)
    rows = pg.evaluate('Array.from(document.querySelectorAll("#sheet .row[data-a=plot]")).map(function (r) { return r.querySelector(".nm").textContent.replace(/^\\d+/, "") + " | " + r.querySelector(".ds").textContent; })')
    for r in rows: print('     ', r)
    want = ['시장 Lv2 | 금 +300/월 · Lv3 +440', '시장 Lv1 | 금 +180/월 · Lv2 +300', '농장 Lv3 | 병량 +4,400/분기 · 최고 레벨', '병영 Lv1 | 징병 가능 · Lv2 징병량 ×1.3', '병영 Lv2 | 징병량 ×1.3 · Lv3 ×1.6',
            '대장간 Lv1 | 창·극·노 생산 · Lv2 생산량 ×1.3', '마구간 Lv3 | 군마 생산량 ×1.6 · 최고 레벨', '조폐 Lv1 | 옆 시장의 수입 +50% · 레벨은 영향 없음', '공방 Lv1 | 충차 생산 · 레벨은 영향 없음']
    miss = [w for w in want if w not in rows]
    ok(not miss, '지은 시설의 줄: 지금 레벨의 값이 먼저 — 빠진 것 %s' % miss)
    ok(not any('180 (Lv2' in r or 'Lv2 300, Lv3 440' in r for r in rows), '줄에 Lv1 기준의 옛 글(180 (Lv2 300, Lv3 440))이 없다')
    def open_fac(pi):
        pg.evaluate('(pi) => { closeDialog(); flowFacility(G.bases[%d], pi); }' % S['id'], pi); pg.wait_for_timeout(700)
    open_fac(S['A'])
    f1 = pg.evaluate('''(([bid, pi]) => { var b = G.bases[bid], y = facYield(b, pi), g1 = goldIncome(b), fc = b.plots[pi].fac; b.plots[pi].fac = null; var g0 = goldIncome(b); b.plots[pi].fac = fc;
      return { head: document.querySelector("#modal .dlg-h").textContent, v: document.querySelector("#modal .fcv").textContent, n: document.querySelector("#modal .fcn").textContent, y: y.gold, real: g1 - g0, note: document.querySelector("#modal .dlg-b > p.note:last-of-type").innerText }; })''', [S['id'], S['A']])
    print('    ', f1)
    ok('시장 Lv2' in f1['head'] and f1['v'] == '금 +300/월 · Lv3 +440', '시설 창의 큰 글: ' + f1['v'])
    ok(f1['y'] == f1['real'] and ('+%s' % format(f1['y'], ',')) in f1['n'] and '옆 조폐 1곳 +50%' in f1['n'] and '치안 64 → 82%' in f1['n'], '그 아래: 지금 실제로 보태는 수입과 까닭 — ' + f1['n'])
    ok('금 수입' in f1['note'] and '부지가 빕니다' in f1['note'], '합병하면 달라지는 수입과 비는 부지: ' + f1['note'].replace('\n', ' / '))
    B.shot(pg, 'q2_market', 200)
    # 합병: 미리보기의 금액 = 실제로 드는 금, 수입 변화 = 미리 본 값
    pre = pg.evaluate('(([bid, pi, pj]) => { var b = G.bases[bid]; return { gold: b.gold, inc: goldIncome(b), mg: mergeGain(b, pi, pj).gold, cost: COST.merge * b.plots[pi].fac.lv }; })', [S['id'], S['A'], S['m1']])
    tapsel(pg, '#modal [data-a=merge]'); pg.wait_for_timeout(500); tapsel(pg, '#modal [data-a=auto]'); pg.wait_for_timeout(400)
    pv = txt(pg, '#modal .pv')
    ok(('금 %d' % pre['cost']) in pv and '금 수입' in pv, '합병 미리보기: 금 %d(= 100 × 레벨), 수입 변화 — %s' % (pre['cost'], pv))
    tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(900)
    post = pg.evaluate('(([bid, pi, pj]) => { var b = G.bases[bid]; return { gold: b.gold, inc: goldIncome(b), lv: b.plots[pi].fac.lv, gone: !b.plots[pj].fac }; })', [S['id'], S['A'], S['m1']])
    ok(pre['gold'] - post['gold'] == pre['cost'] == 200 and post['lv'] == 3 and post['gone'], '합병: 금이 미리보기대로 %d 줄고 Lv3, 합쳐진 부지는 빈다' % (pre['gold'] - post['gold']))
    ok(post['inc'] - pre['inc'] == pre['mg'], '합병 뒤의 수입 변화가 미리 본 값과 같다(%+d)' % pre['mg'])
    pg.evaluate('talkHide(); closeDialog()'); pg.wait_for_timeout(300)
    # 병영 Lv1(다른 곳에 Lv2), 곡창(옆에 농장 없음), 조폐(레벨 영향 없음)
    b1 = pg.evaluate('(bid) => { var b = G.bases[bid]; for (var i = 0; i < b.plots.length; i++) { var f = b.plots[i].fac; if (f && f.t === "barracks" && f.lv === 1) return i; } return -1; }', S['id'])
    open_fac(b1); t1 = txt(pg, '#modal .fcn')
    ok('Lv2 병영이 있어 이곳은 보탬이 없습니다' in t1 and '가장 높은 한 곳만' in t1, '병영 Lv1: ' + t1)
    if S['gran'] >= 0:
        open_fac(S['gran']); t2 = txt(pg, '#modal .fcn')
        ok('농장이 없어' in t2 and '보탬이 없습니다' in t2, '곡창(옆에 농장 없음): ' + t2)
    open_fac(S['mint']); t3 = txt(pg, '#modal .dlg-b > p.note:last-of-type')
    ok('조폐는 레벨을 올려도 효과가 같습니다' in t3, '조폐: ' + t3)
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(300)
    # 새로 지을 때의 카드는 Lv1 기준 그대로
    e0 = pg.evaluate('(bid) => { var b = G.bases[bid]; for (var i = 0; i < b.plots.length; i++) if (!b.plots[i].fac) return i; return -1; }', S['id'])
    pg.evaluate('(pi) => { flowDevelop(G.bases[%d], pi); }' % S['id'], e0); pg.wait_for_timeout(700)
    ok('무엇을' in head(pg) or '건설' in head(pg), '빈 부지: 짓는 창이 그대로 열린다 — ' + head(pg))
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(300)

    # ================= 3. 무장 줄의 적성 =================
    print('3. 무장 줄의 적성')
    pg.locator('#sheet .tabs button').nth(2).tap(); pg.wait_for_timeout(600)
    a3 = pg.evaluate('''(() => { var rs = Array.from(document.querySelectorAll("#sheet .row[data-a=off]")); return rs.map(function (r) { var o = off(+r.getAttribute("data-v")), ap = r.querySelector(".ap5");
      return { n: o.n, apt: o.apt, shown: ap ? Array.from(ap.querySelectorAll("b")).map(function (x) { return x.textContent; }).join("") : null, lab: ap ? Array.from(ap.querySelectorAll("i")).map(function (x) { return x.textContent; }).join(" ") : "", h: r.getBoundingClientRect().height }; }); })()''')
    ok(len(a3) >= 3 and all(x['shown'] == x['apt'] for x in a3), '거점의 무장 줄마다 적성 다섯 글자가 그 무장의 것과 같다 %s' % [(x['n'], x['shown']) for x in a3[:3]])
    ok(a3[0]['lab'] == '창 극 노 기 병기' and max(x['h'] for x in a3) <= 84, '적성의 이름표(창 극 노 기 병기), 줄 높이 %s' % max(x['h'] for x in a3))
    pg.locator('#sheet .row[data-a=off]').nth(0).tap(); pg.wait_for_timeout(600)
    d3 = pg.evaluate('document.querySelector("#modal .dlg-b").innerText')
    ok('병종 적성' in d3 and '×0.85' in d3 and '×1.15' in d3 and '전법' in d3, '무장 창: 적성 칸에 제목과 풀이')
    B.shot(pg, 'q3_officer', 200); pg.evaluate('closeDialog()'); pg.wait_for_timeout(300)
    pg.locator('#sheet .tabs button').nth(1).tap(); pg.wait_for_timeout(500)
    tapsel(pg, '#sheet [data-a=deploy]'); pg.wait_for_timeout(600)
    tapsel(pg, '#modal [data-a=type][data-v=cav]'); pg.wait_for_timeout(400)
    on = pg.evaluate('Array.from(document.querySelectorAll("#modal .row .ap5")).map(function (a) { return Array.from(a.children).findIndex(function (s) { return s.classList.contains("on"); }); })')
    ok(len(on) >= 3 and all(i == 3 for i in on), '출진 창: 고른 병과(기병)의 적성 칸에 밑줄 %s' % on[:4])

    # ================= 4. 출진 군량 =================
    print('4. 출진 군량')
    tapsel(pg, '#modal [data-a=type][data-v=spear]'); pg.wait_for_timeout(300)
    tapsel(pg, '#modal [data-a=auto]'); pg.wait_for_timeout(500)
    o4 = pg.evaluate('({ opts: Array.from(document.querySelectorAll("#modal [data-a=turns]")).map(function (x) { return [x.getAttribute("data-v"), x.querySelector("b").textContent, x.querySelector("small").textContent, x.classList.contains("on")]; }), troops: +$("dpR").value, note: $("dpN").innerText, pv: $("dpP").innerText })')
    print('    ', o4)
    ok([x[1] for x in o4['opts']] == ['90일분', '180일분', '270일분', '360일분'] and [x[3] for x in o4['opts']] == [False, True, False, False], '군량 칸: 90 · 180 · 270 · 360일분, 처음 값 180일분')
    per = -(-o4['troops'] // 20)
    ok([int(x[2].replace(',', '')) for x in o4['opts']] == [per * 9, per * 18, per * 27, per * 36], '칸마다 수량 = 병력 ÷ 20 × 턴 수')
    setrange(pg, '#dpR', 3000)
    o5 = pg.evaluate('Array.from(document.querySelectorAll("#modal [data-a=turns] small")).map(function (x) { return x.textContent; })')
    ok(o5 == ['1,350', '2,700', '4,050', '5,400'], '병력을 바꾸면 칸의 수량도 바로 바뀐다 %s' % o5)
    setrange(pg, '#dpR', o4['troops'])
    pg.locator('#modal [data-a=turns]').nth(3).tap(); pg.wait_for_timeout(400)
    n6 = pg.evaluate('({ note: $("dpN").innerText, pv: $("dpP").innerText, food: G.bases[%d].food })' % S['id'])
    ok('모자랍니다' in n6['note'] and '분만 실립니다' in n6['note'] and format(n6['food'], ',') in n6['pv'], '도시 병량(9,000)이 360일분에 못 미치면 실리는 날수를 적는다 — ' + n6['note'])
    pg.evaluate('G.bases[%d].food = 90000; refreshDialog()' % S['id']); pg.wait_for_timeout(300)
    ok('모자랍니다' not in pg.evaluate('$("dpN").innerText'), '병량이 넉넉하면 그 말이 없다')
    tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(2600)
    u4 = pg.evaluate('(() => { var u = facUnits(G.player)[0]; return u ? { troops: u.troops, food: u.food, days: unitFoodTurns(u) * 10 } : null; })()')
    ok(u4 and u4['food'] == -(-u4['troops'] // 20) * 36 and u4['days'] == 360, '360일분으로 출진한 부대의 군량 %s' % u4)
    pg.evaluate('talkHide(); clearSel()'); pg.wait_for_timeout(300)

    # ================= 5. 치안 =================
    print('5. 치안')
    pg.evaluate('selectBase(G.bases[%d])' % S['id']); pg.wait_for_timeout(500)
    c5 = pg.evaluate('({ cell: document.querySelector("#sheet [data-a=order]").innerText.replace(/\\n/g, " "), order: G.bases[%d].order, pct: incPct(G.bases[%d].order), gi: goldIncome(G.bases[%d]) })' % (S['id'], S['id'], S['id']))
    ok(('수입 %d%%' % c5['pct']) in c5['cell'] and c5['pct'] == round(50 + c5['order'] / 2), '거점 창의 치안 칸에 수입 몫: ' + c5['cell'])
    tapsel(pg, '#sheet [data-a=order]'); pg.wait_for_timeout(500)
    t5 = pg.evaluate('document.querySelector("#modal").innerText')
    ok(('치안 %d' % c5['order']) in head(pg) and '82%' in t5 and '78%' in t5 and '20 아래면 징병할 수 없습니다' in t5 and '순찰' in t5 and '민란' in t5, '치안 풀이 창: 수입 82% · 징병량 78% · 내려갈 때 · 올릴 때')
    B.shot(pg, 'q5_order', 200); pg.evaluate('closeDialog()'); pg.wait_for_timeout(300)
    tapsel(pg, '#sheet [data-a=patrol]'); pg.wait_for_timeout(500); tapsel(pg, '#modal [data-a=auto]'); pg.wait_for_timeout(400)
    p5 = txt(pg, '#modal .pv'); m = re.search(r'치안 \+(\d+).*수입 (\d+)% → (\d+)%', p5)
    ok(m and int(m.group(2)) == c5['pct'] and int(m.group(3)) == round(50 + (c5['order'] + int(m.group(1))) / 2), '순찰 미리보기에 수입 몫의 변화: ' + p5)
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(300)

    # ================= 6. 등용과 옛 관계 =================
    print('6. 등용과 옛 관계')
    fresh(pg, 0, 4242)
    G6 = pg.evaluate('''(() => {
      var me = G.player, foe = 1, cap = facCities(me)[0], fb = facBases(foe)[0];
      var r = cmdDeploy(cap, { type: 'sword', ids: idleOfficers(cap).filter(function (o) { return !isLord(o); }).slice(0, 3).map(function (o) { return o.id; }), troops: 3000, food: 1500 });
      captureBase(fb, r.unit);
      G.officers.forEach(function (o) { if (o.f === me) o.acted = false; });
      G.factions[me].ap = 250; fb.gold = 900; reindex(); syncScene(); selectBase(fb, false, 'men'); UI.dirty = true; requestDraw();
      window._rr = recruitRoll;
      return { fb: fb.id, n: fb.n, alive: G.factions[foe].alive, caps: fb.captives.length, lord: off(G.factions[foe].lord).n };
    })()'''); print('   ', G6); pg.wait_for_timeout(700)
    ok(not G6['alive'] and G6['caps'] >= 8, '여포군의 마지막 거점을 차지 → 세력 멸망, 포로 %d명' % G6['caps'])
    tapsel(pg, '#sheet [data-a=recruit]'); pg.wait_for_timeout(600)
    R6 = '''Array.from(document.querySelectorAll("#modal .row[data-a=t]")).filter(function (r) { return off(+r.getAttribute("data-v")).st === "captive"; }).map(function (r) { var o = off(+r.getAttribute("data-v")); return { id: o.id, n: o.n, nm: r.querySelector(".nm").innerText, rt: r.querySelector(".rt").innerText.replace(/\\n/g, " / "), best: bestRecruiter(G.bases[%d], o).p, bond: !!bondDirect(o, off(G.factions[1].lord)) }; })''' % G6['fb']
    r6 = pg.evaluate(R6)
    for x in r6[:4]: print('     ', x)
    ok(all('옛 여포군 · 멸망' in x['rt'] for x in r6), '포로 줄마다 출신(옛 여포군 · 멸망)')
    cmp6 = pg.evaluate('''(() => { var fb = G.bases[%d], L = off(G.factions[G.player].lord), out = [];
      fb.captives.forEach(function (id) { var t = off(id); idleOfficers(fb).forEach(function (o) { var x = recruitTerms(fb, o, t), old = 35 + (o.cha - 50) * 0.7 + (o.pol - 50) * 0.2 + (L.cha - 70) * 0.4 + (o.sk === '논객' ? 20 : 0) + (bondWith(t, G.player) ? 30 : 0) - 15;
        out.push({ t: t.n, lord: G.factions[1].lord === t.id, p: x.p, old: clamp(Math.round(old), 3, 95), exp: clamp(Math.round(old + (G.factions[1].lord === t.id ? 0 : 25)), 3, 95) }); }); });
      return out; })()''' % G6['fb'])
    ok(all(x['p'] == x['exp'] for x in cmp6) and any(x['p'] > x['old'] for x in cmp6), '멸망한 세력 출신의 포로: 전보다 +25(옛 군주는 그대로) — %d조합' % len(cmp6))
    zl = next((x for x in r6 if x['n'] == '장료'), r6[1])
    idx = pg.evaluate('(id) => Array.from(document.querySelectorAll("#modal .row[data-a=t]")).findIndex(function (r) { return +r.getAttribute("data-v") === id; })', zl['id'])
    pg.locator('#modal .row[data-a=t]').nth(idx).tap(); pg.wait_for_timeout(600)
    tapsel(pg, '#modal [data-a=auto]'); pg.wait_for_timeout(400)
    pv6 = txt(pg, '#modal .pv')
    ok('멸망한 세력 출신 +25' in pv6, '보낼 무장을 고르면 아래에 더해진 까닭: ' + pv6)
    pg.evaluate('(() => { recruitRoll = function () { return 0; }; })()')         # 주사위를 0 으로: 반드시 응한다
    tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(900)
    j6 = pg.evaluate('(id) => { var o = off(id); return [o.st, o.f, o.pf, o.past]; }', zl['id'])
    ok(j6[0] == 'active' and j6[1] == 0 and j6[2] == 0 and j6[3] == [1], zl['n'] + ' 등용 → 섬겼던 세력에 여포군이 적힌다 %s' % j6)
    pg.evaluate('recruitRoll = window._rr; talkHide(); G.officers.forEach(function (o) { if (o.f === G.player) o.acted = false; }); G.factions[G.player].ap = 250; closeDialog(); flowRecruit(G.bases[%d]);' % G6['fb']); pg.wait_for_timeout(600)
    r7 = pg.evaluate(R6)
    for x in r7[:3]: print('     ', x)
    lordrow = next(x for x in r7 if x['n'] == G6['lord'])
    ok((zl['n'] + ' · 옛 신하') in lordrow['rt'], '옛 군주의 줄: 가장 잘 권할 무장과 그 사이 — ' + lordrow['rt'])
    ok(all((zl['n'] + ' · 옛 동료') in x['rt'] or '·' in x['rt'] for x in r7 if x['n'] != G6['lord']) and sum(1 for x in r7 if (zl['n'] + ' · 옛 동료') in x['rt']) >= 5, '다른 포로의 줄: %s · 옛 동료' % zl['n'])
    mate = next(x for x in r7 if x['n'] != G6['lord'] and '옛 동료' in x['rt'] and not x['bond'])      # 옛 군주와 인연이 없던 포로
    idx = pg.evaluate('(id) => Array.from(document.querySelectorAll("#modal .row[data-a=t]")).findIndex(function (r) { return +r.getAttribute("data-v") === id; })', mate['id'])
    pg.locator('#modal .row[data-a=t]').nth(idx).tap(); pg.wait_for_timeout(600)
    pk = pg.evaluate('Array.from(document.querySelectorAll("#modal .tr")).map(function (r) { return r.querySelector(".c-n").innerText + ":" + r.querySelector(".c-x").innerText.replace(/\\n/g, "/"); })')
    ok(any(p.startswith(zl['n'] + ':') and '옛 동료' in p for p in pk), '무장을 고르는 표: %s 의 칸에 옛 동료 — %s' % (zl['n'], pk[:3]))
    tapsel(pg, '#modal [data-a=auto]'); pg.wait_for_timeout(400)
    pv7 = txt(pg, '#modal .pv')
    ok('멸망한 세력 출신 +25' in pv7 and '옛 동료의 설득 +12' in pv7, '미리보기: ' + pv7)
    B.shot(pg, 'q6_recruit', 200)
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(300)
    pg.evaluate('(id) => showOfficer(off(id))', zl['id']); pg.wait_for_timeout(500)
    ok('섬겼던 세력 — 여포군(멸망)' in pg.evaluate('document.querySelector("#modal .dlg-b").innerText'), '무장 창에 섬겼던 세력')
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(300)
    # 옛 군주를 참수하면
    pg.evaluate('selectBase(G.bases[%d], true, "men")' % G6['fb']); pg.wait_for_timeout(400)
    tapsel(pg, '#sheet [data-a=captive]'); pg.wait_for_timeout(500)
    c6 = pg.evaluate('document.querySelector("#modal .dlg-b").innerText')
    ok('옛 군주를 참수하면' in c6 and '옛 여포군 · 멸망' in c6 and pg.evaluate('document.querySelectorAll("#modal .row .ap5").length') >= 5, '포로 창: 참수의 뒷일 · 출신 · 적성')
    before = pg.evaluate('(([fb, id]) => recruitTerms(G.bases[fb], idleOfficers(G.bases[fb]).filter(function (o) { return o.n !== "%s"; })[0], off(id)).p)' % zl['n'], [G6['fb'], mate['id']])
    li = pg.evaluate('(n) => Array.from(document.querySelectorAll("#modal .row")).findIndex(function (r) { return r.querySelector(".nm").textContent.indexOf(n) === 0; })', G6['lord'])
    pg.locator('#modal .row').nth(li).locator('[data-a=exe]').tap(); pg.wait_for_timeout(300)
    pg.locator('#modal .row').nth(li).locator('[data-a=exe]').tap(); pg.wait_for_timeout(500)
    ex = pg.evaluate('(([fb, id]) => { var L = off(G.factions[1].lord), x = recruitTerms(G.bases[fb], idleOfficers(G.bases[fb]).filter(function (o) { return o.n !== "%s"; })[0], off(id)); return { st: L.st, exBy: L.exBy, p: x.p, why: x.why }; })' % zl['n'], [G6['fb'], mate['id']])
    ok(ex['st'] == 'dead' and ex['exBy'] == 0 and any('참수의 원한' in w[0] and w[1] == -20 for w in ex['why']) and ex['p'] == max(3, before - 20), '옛 군주를 참수 → 그 신하였던 포로(%s)의 성공률 %d%% → %d%% (참수의 원한 −20)' % (mate['n'], before, ex['p']))
    bd = next((x for x in r7 if x['bond'] and x['n'] != G6['lord']), None)
    if bd:
        pb = pg.evaluate('(([fb, id]) => recruitTerms(G.bases[fb], idleOfficers(G.bases[fb])[0], off(id)).p)', [G6['fb'], bd['id']])
        ok(pb <= 3, '옛 군주와 인연이 있던 포로(%s)는 3%% 이하: %d%%' % (bd['n'], pb))
    pg.evaluate('closeDialog(); clearSel()'); pg.wait_for_timeout(300)

    # ================= 7. 수송대의 보급 =================
    print('7. 수송대의 보급')
    fresh(pg, 0, 4242)
    U7 = pg.evaluate('''(() => {
      var b = facCities(G.player)[0]; b.troops = 20000; b.food = 60000; b.w.spear = 9000; G.factions[G.player].ap = 250;
      var os = idleOfficers(b).filter(function (o) { return !isLord(o); }), spots = [];
      for (var dc = -9; dc <= 9 && spots.length < 2; dc++) for (var dr = -9; dr <= 9 && spots.length < 2; dr++) {
        var c = b.c + dc, r0 = b.r + dr, k = K(c, r0); if (c < 0 || r0 < 0 || c >= W || r0 >= H) continue;
        if (terr(c, r0) !== 'p' || UAT[k] || BAT[k] !== undefined || PAT[k] || hdist(c, r0, b.c, b.r) < 4) continue;
        if (nbrs(c, r0).filter(function (n) { return terr(n[0], n[1]) === 'p' && !PAT[K(n[0], n[1])] && BAT[K(n[0], n[1])] === undefined; }).length < 5) continue;
        if (spots.some(function (q) { return hdist(q[0], q[1], c, r0) < 5; })) continue;
        spots.push([c, r0]);
      }
      var A = cmdDeploy(b, { type: 'spear', ids: [os[0].id], troops: 3000, food: 300 }).unit; placeUnit(A, spots[0][0], spots[0][1]);
      var T = cmdDeploy(b, { type: 'trans', ids: [os[1].id], troops: 2100, food: 9000, gold: 300, cargo: { spear: 1500, halberd: 0, bow: 0, horse: 0, ram: 0 } }).unit; placeUnit(T, spots[1][0], spots[1][1]);
      A.done = false; T.done = false; A.moved = false; T.moved = false;
      syncScene(); selectUnit(T); requestDraw();
      return { A: A.id, T: T.id, cap: cmdCap(uLeader(A)), an: uName(A), tn: uName(T), far: hdist(A.c, A.r, T.c, T.r) };
    })()'''); print('   ', U7); pg.wait_for_timeout(700)
    s7 = pg.evaluate('({ btn: !!document.querySelector("#sheet [data-a=supply]"), off: document.querySelector("#sheet [data-a=supply]").classList.contains("off"), cargo: (document.querySelector("#sheet .cgo") || { innerText: "" }).innerText.replace(/\\n/g, " ") })')
    ok(s7['btn'] and s7['off'] and '병량 9,000' in s7['cargo'] and '창 1,500' in s7['cargo'] and '금 300' in s7['cargo'], '수송대 창: 실은 것(%s)과 [보급](옆에 아군 부대가 없으면 흐리게)' % s7['cargo'])
    tapsel(pg, '#sheet [data-a=supply]'); pg.wait_for_timeout(300)
    ok('옆 칸' in toast(pg) and not pg.evaluate('!!MODAL'), '떨어져 있을 때 누르면 풀이만: ' + toast(pg))
    pg.evaluate('''(([a, t]) => { var A = UMAP[a], T = UMAP[t], ns = nbrs(A.c, A.r); for (var i = 0; i < ns.length; i++) { var k = K(ns[i][0], ns[i][1]); if (!UAT[k] && terr(ns[i][0], ns[i][1]) === 'p' && !PAT[k] && BAT[k] === undefined) { placeUnit(T, ns[i][0], ns[i][1]); break; } } syncScene(); selectUnit(T); requestDraw(); })''', [U7['A'], U7['T']]); pg.wait_for_timeout(600)
    ok(pg.evaluate('document.querySelector("#sheet [data-a=supply]").classList.contains("pri")'), '아군 부대 옆에 서면 [보급]이 켜진다')
    tapsel(pg, '#sheet [data-a=supply]'); pg.wait_for_timeout(500)
    h7 = head(pg); mx = pg.evaluate('(([a, t]) => supplyMax(UMAP[t], UMAP[a]))', [U7['A'], U7['T']])
    ok(h7.startswith('보급') and U7['tn'] in h7 and U7['an'] in h7 and mx['troops'] == 1500 and '창' in mx['why'], '보급 창: %s · 병력 한도 %s' % (h7, mx))
    setrange(pg, '#modal [data-i=food]', 6000); setrange(pg, '#modal [data-i=troops]', 1500)
    pv = txt(pg, '#spP')
    ok('20일분 → 280일분' in pv and '3,000 → 4,500' in pv and '남는 병량 3,000' in pv, '미리보기(받는 부대의 군량 날수 · 병력, 수송대에 남는 병량): ' + pv)
    B.shot(pg, 'q7_supply', 200)
    tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(900)
    a7 = pg.evaluate('(([a, t]) => { var A = UMAP[a], T = UMAP[t]; return { A: [A.troops, A.food, A.done], T: [T.troops, T.food, T.cargo.spear, T.done], modal: !!MODAL, talk: $("talk") ? $("talk").innerText.replace(/\\n/g, " / ") : "" }; })', [U7['A'], U7['T']])
    ok(a7['A'][:2] == [4500, 6300] and a7['T'] == [600, 3000, 0, True] and not a7['modal'], '보급: 받은 부대 병력 4,500 · 병량 6,300, 수송대 병력 600 · 병량 3,000 · 창 0 · 행동 끝 %s' % a7)
    ok('보급' in a7['talk'] and '병량 6,000' in a7['talk'], '대화창: ' + a7['talk'])
    pg.evaluate('talkHide()')
    # 받는 쪽에서: 행동하지 않은 수송대가 옆에 있으면 [보급 받기]
    pg.evaluate('(([a, t]) => { UMAP[t].done = false; selectUnit(UMAP[a]); })', [U7['A'], U7['T']]); pg.wait_for_timeout(500)
    b7 = pg.evaluate('(() => { var e = document.querySelector("#sheet [data-a=supply]"); return e ? e.innerText.replace(/\\n/g, " ") : ""; })()')
    ok('보급 받기' in b7, '받는 부대의 창: ' + b7)
    tapsel(pg, '#sheet [data-a=supply]'); pg.wait_for_timeout(500)
    ok(head(pg).startswith('보급') and '넘길 수 없습니다' in pg.evaluate('document.querySelector("#modal .dlg-b").innerText'), '창이 떨어진 뒤: 병력은 넘길 수 없다는 까닭이 적힌다')
    pg.evaluate('closeDialog(); clearSel()'); pg.wait_for_timeout(300)

    # ================= 8. 군사의 헌책 =================
    print('8. 군사의 헌책')
    fresh(pg, 0, 4242)
    pg.evaluate('HOME.open = true; showHome()'); pg.wait_for_timeout(400)
    def say(): return pg.evaluate('(() => { var e = document.querySelector("#sheet .hm-say .tx"); return e ? e.innerText.replace(/\\n+/g, " | ") : ""; })()')
    k8 = pg.evaluate('''(() => { var A = facAdv(G.player), cs = counsel(G.player); return { adv: A.n, int: A.int, n: cs.list.length, kinds: cs.list.map(function (c) { return c.kind; }), lvl: cs.lvl, texts: cs.list.map(function (c) { return counselText(c).say; }) }; })()''')
    print('    ', k8['adv'], k8['int'], k8['kinds']); [print('       ', t) for t in k8['texts']]
    s1 = say()
    ok(k8['n'] >= 2 and k8['texts'][0] in s1 and ('1/%d' % k8['n']) in s1, '군사의 한마디 = 헌책의 맨 앞, 몇 번째인지(1/%d): %s' % (k8['n'], s1))
    ok(all(t and not t.startswith(' ') and 'undefined' not in t and 'NaN' not in t for t in k8['texts']), '헌책의 글에 빈 말 · undefined 가 없다')
    seen = [s1]
    for i in range(k8['n'] - 1):
        tapsel(pg, '#sheet [data-a=advnext]'); pg.wait_for_timeout(200); seen.append(say())
    ok(len(set(seen)) == k8['n'] and all(k8['texts'][i] in seen[i] for i in range(k8['n'])), '[다른 조언]을 누를 때마다 다음 헌책(%d가지 모두 다르다)' % len(set(seen)))
    tapsel(pg, '#sheet [data-a=advnext]'); pg.wait_for_timeout(200)
    ok(k8['texts'][0] in say(), '한 바퀴 돌면 처음으로')
    B.shot(pg, 'q8_counsel', 200)
    todo = pg.evaluate('Array.from(document.querySelectorAll("#sheet .todo")).map(function (t) { return t.querySelector(".mid").innerText.replace(/\\n/g, " — "); })')
    print('    ', todo)
    ok(any('쉬는 무장' in t and '→' in t for t in todo) and not any('탐색으로 인재·재물 찾기' in t for t in todo), '지금 할 일의 거점 줄도 헌책에서: %s' % [t for t in todo if '쉬는 무장' in t])
    # 누르면 그 일로
    g8 = pg.evaluate('(() => { var cs = counsel(G.player), t = counselText(cs.list[0]); return t.go; })()')
    tapsel(pg, '#sheet .hm-say'); pg.wait_for_timeout(700)
    w8 = pg.evaluate('({ sel: UI.sel ? [UI.sel.kind, UI.sel.id] : null, modal: MODAL ? document.querySelector("#modal .dlg-h").textContent : "" })')
    ok(w8['sel'] and w8['sel'][1] == g8[1] and (g8[0] != 'recruit' or '등용' in w8['modal']), '헌책을 누르면 그 거점(' + str(g8) + ')으로: %s' % w8)
    pg.evaluate('closeDialog(); clearSel(); showHome()'); pg.wait_for_timeout(300)
    # 지력에 따라 말이 달라진다
    lv = pg.evaluate('''(() => { var A = facAdv(G.player), keep = A.int, b = facCities(G.player)[0], out = {};
      b.order = 40; b.gold = 3000;
      [100, 70, 50].forEach(function (iq) { A.int = iq; var cs = counsel(G.player), p = cs.list.filter(function (c) { return c.kind === 'patrol'; })[0], bd = cs.list.filter(function (c) { return c.kind === 'build'; })[0];
        out[iq] = { lvl: cs.lvl, patrol: p ? counselText(p).say : '', build: bd ? counselText(bd).say : '', top: cs.list.length ? cs.list[0].kind : '' }; });
      A.int = keep; return out; })()''')
    print('    ', json.dumps(lv, ensure_ascii=False))
    ok(lv['100']['lvl'] == 2 and lv['70']['lvl'] == 1 and lv['50']['lvl'] == 0, '말의 자세함: 지력 100 → 2 · 70 → 1 · 50 → 0')
    ok('40까지 떨어져 수입이 70%뿐' in lv['100']['patrol'] and '맡기십시오' in lv['100']['patrol'] or '주공께서 직접' in lv['100']['patrol'], '지력 100: 숫자와 사람까지 — ' + lv['100']['patrol'])
    ok('40' not in lv['70']['patrol'] and '순찰을 돌리십시오' in lv['70']['patrol'] and lv['50']['patrol'].endswith('치안이 어지럽습니다. 순찰을 돌리십시오.'), '지력 70 · 50: ' + lv['70']['patrol'] + ' / ' + lv['50']['patrol'])
    ok('부지에' in lv['100']['build'] and '/월' in lv['100']['build'] or '/분기' in lv['100']['build'] or '병영' in lv['100']['build'], '지력 100 의 건설: 무엇을 어디에 얼마 — ' + lv['100']['build'])
    ok('빈 부지가' in lv['50']['build'] or lv['50']['build'] == '', '지력 50 의 건설: 두루뭉술하게 — ' + lv['50']['build'])
    # 징병: 이웃이 약하면 말하지 않는다 / 세면 말한다
    dr = pg.evaluate('''(() => { var b = facCities(G.player)[0], f = G.player, A = facAdv(f), keep = A.int; A.int = 100;
      if (!hasFac(b, 'barracks')) { for (var i = 0; i < b.plots.length; i++) if (!b.plots[i].fac) { b.plots[i].fac = { t: 'barracks', lv: 1, done: true, prog: 0, need: 0, rate: 0, hp: FAC_HP }; break; } }
      b.order = 80; b.gold = 3000; b.food = 90000; b.troops = 12000; G.factions[f].ap = 250;
      var nbs = ADJ[b.id].map(function (e) { return G.bases[e.to]; }).filter(function (x) { return x.owner >= 0 && x.owner !== f; }), keepT = nbs.map(function (x) { return x.troops; });
      nbs.forEach(function (x) { x.troops = 2000; });
      var weak = counsel(f).list.filter(function (c) { return c.kind === 'draft'; }).length;
      nbs[0].troops = 40000; G.peace.until = G.turn + 2;
      var d = counsel(f).list.filter(function (c) { return c.kind === 'draft'; })[0], t = d ? counselText(d) : null;
      nbs.forEach(function (x, i) { x.troops = keepT[i]; }); A.int = keep;
      return { weak: weak, say: t ? t.say : '', tip: t ? t.tip : '', nb: nbs[0].n }; })()''')
    ok(dr['weak'] == 0, '이웃 세력이 약하면 징병을 권하지 않는다')
    ok('40,000' in dr['say'] and '12,000뿐' in dr['say'] and '징병하십시오' in dr['say'] and dr['nb'] in dr['say'], '이웃이 세면 까닭과 함께: ' + dr['say'])
    # 턴이 넘어가면: 같은 말을 되풀이하지 않는다
    first = pg.evaluate('(() => { showHome(); var e = document.querySelector("#sheet .hm-say .tx span"); return e ? e.textContent : ""; })()')
    k0 = pg.evaluate('Object.keys(UI.cSaid || {})')
    pg.evaluate('doEndTurn()'); pg.wait_for_timeout(600)
    for _ in range(240):
        pg.wait_for_timeout(250)
        if pg.evaluate('!!UI.play'):
            if pg.evaluate('!!$("plSkip")'): pg.evaluate('$("plSkip").click()')
        elif pg.evaluate('!!MODAL'): pg.evaluate('closeDialog()')
        elif pg.evaluate('!UI.busy'): break
    pg.wait_for_timeout(1500)
    brief = pg.evaluate('$("talk") ? $("talk").innerText.replace(/\\n/g, " / ") : ""')
    pg.evaluate('talkHide(); showHome()'); pg.wait_for_timeout(300)
    second = pg.evaluate('(() => { var e = document.querySelector("#sheet .hm-say .tx span"); return e ? e.textContent : ""; })()')
    urgent = pg.evaluate('(() => { var cs = counsel(G.player); return cs.list.length ? [cs.list[0].kind, Math.round(cs.list[0].w)] : null; })()')
    print('     턴 ', pg.evaluate('G.turn'), '| 지난 턴:', first, '| 이번 턴:', second, '| 맨 앞:', urgent, '| 대화창:', brief[:80])
    ok(second and (second != first or (urgent and urgent[1] >= 70) or pg.evaluate('!!document.querySelector("#sheet .todo.warn")')), '다음 턴의 한마디는 지난 턴과 다르다(급한 일은 예외)')

    # ================= 9. 탐색 조언 =================
    print('9. 탐색 조언')
    fresh(pg, 0, 4242)
    P9 = pg.evaluate('''(() => { var b = facCities(G.player)[0], A = facAdv(G.player); A.int = 100;
      var h = G.officers.filter(function (o) { return o.st === 'hidden'; })[0]; h.loc = b.id; h.y = G.year; h.j = null;
      G.factions[G.player].ap = 250; selectBase(b, true, 'men');
      var cs = counsel(G.player), c = cs.list.filter(function (x) { return x.kind === 'search'; })[0];
      return { b: b.id, hid: hiddenOfficers(b).map(function (o) { return o.n; }), c: c ? counselText(c).say : '', says: c ? c.x.says : null, os: idleOfficers(b).map(function (o) { return [o.id, o.n, Math.round(searchChance(b, o)), searchRoll(b) < searchChance(b, o)]; }), roll: Math.round(searchRoll(b)) }; })()''')
    print('    ', {k: v for k, v in P9.items() if k != 'os'}, P9['os'][:3])
    ok(len(P9['hid']) >= 1 and P9['c'] and '숨은 인재' in P9['c'], '숨은 인재가 있는 도시: 헌책에 귀띔 — ' + P9['c'])
    tapsel(pg, '#sheet [data-a=search]'); pg.wait_for_timeout(500)
    marks = pg.evaluate('Array.from(document.querySelectorAll("#modal .tr")).map(function (r) { return [+r.getAttribute("data-v"), !!r.querySelector(".c-x .adv.y"), !!r.querySelector(".c-x .adv.n")]; })')
    truth = {o[0]: o[3] for o in P9['os']}
    ok(len(marks) >= 3 and all((m[1] if truth[m[0]] else m[2]) for m in marks), '탐색할 무장을 고르는 표: 무장마다 ○ · × (지력 100 의 군사 = 실제와 같다)')
    tapsel(pg, '#modal [data-a=auto]'); pg.wait_for_timeout(400)
    sel9 = pg.evaluate('(() => { var r = document.querySelector("#modal .tr.sel"); return r ? +r.getAttribute("data-v") : -1; })()')
    ps = txt(pg, '#modal .pksay')
    ok(('만날 것입니다' in ps) == truth.get(sel9, False) and ('만나지 못할 것입니다' in ps) != truth.get(sel9, False) and '적중률 100%' in ps, '군사의 말: ' + ps)
    B.shot(pg, 'q9_search', 200)
    tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(900)
    r9 = pg.evaluate('({ talk: $("talk") ? $("talk").innerText.replace(/\\n/g, " / ") : "", free: freeOfficers(G.bases[%d]).map(function (o) { return o.n; }), sN: G.bases[%d].sN })' % (P9['b'], P9['b']))
    ok((len(r9['free']) >= 1) == truth.get(sel9, False) and r9['sN'] == 1, '실제 결과가 군사의 말과 같다: %s' % r9)
    pg.evaluate('talkHide(); clearSel()'); pg.wait_for_timeout(300)

    # ================= 10. 확대한 지도 =================
    print('10. 확대한 지도')
    z = pg.evaluate('({ fix: R3.magfix, def: JSON.stringify(R3.tmat.defines), n: [R3.tmat.uniforms.mapN.value.x, R3.tmat.uniforms.mapN.value.y], pxr: R3.tmat.uniforms.pxr.value, dpr: DPR })')
    ok(z['fix'] and 'MAGFIX' in z['def'] and z['n'] == [3072, 2610] and z['pxr'] == z['dpr'], '확대 손질이 켜져 있다 %s' % z)
    import numpy as np
    from PIL import Image
    def grab(zoom, on, name):
        pg.evaluate('([z, on]) => { HOME.open = false; showHome(); var b = G.bases.filter(function (x) { return x.n === "오"; })[0], p = hexCenter(b.c, b.r); cam.x = p[0] - 4; cam.y = p[1] - 3.5; cam.z = z; clampCam(); R3.tmat.defines = on ? { MAGFIX: 1 } : {}; R3.tmat.needsUpdate = true; requestDraw(); }', [zoom, on]); pg.wait_for_timeout(900)
        path = os.path.join(B.SHOTS, name + '.png'); pg.screenshot(path=path, clip={'x': 0, 'y': 120, 'width': 390, 'height': 420})
        return np.asarray(Image.open(path).convert('RGB')).astype(int)
    a0, a1 = grab(0.8, False, 'q10_z08_off'), grab(0.8, True, 'q10_z08_on')
    b0, b1 = grab(2.3, False, 'q10_z23_off'), grab(2.3, True, 'q10_z23_on')
    d08, d23 = float(np.abs(a0 - a1).mean()), float(np.abs(b0 - b1).mean())
    # 각진 계단: 이웃한 점의 차이 가운데 큰 것(가로 · 세로)의 몫 — 번지게 메우면 줄어든다
    def steps_of(im): g = im.mean(axis=2); return float(((np.abs(np.diff(g, axis=1)) > 9).mean() + (np.abs(np.diff(g, axis=0)) > 9).mean()) * 50)
    ok(d08 < 0.05, '평소의 크기(확대 0.8)에서는 전과 같다 — 차이 %.3f' % d08)
    ok(d23 > 0.3 and steps_of(b1) < steps_of(b0), '가장 크게 당기면(2.3) 달라지고, 각진 가장자리가 줄어든다 — 차이 %.2f · 급한 가장자리 %.2f%% → %.2f%%' % (d23, steps_of(b0), steps_of(b1)))
    pg.evaluate('cam.z = 0.9; clampCam(); HOME.open = true; showHome(); requestDraw()'); pg.wait_for_timeout(400)

    # ================= 11. 저장 · 옛 저장 · 도움말 =================
    print('11. 저장 · 옛 저장 · 도움말')
    pg.evaluate('(() => { var o = baseOfficers(facCities(G.player)[0]).filter(function (x) { return !isLord(x); })[0]; o.f = 1; pastSweep(); o.f = G.player; pastSweep(); window._oid = o.id; saveGame(); })()')
    reload(pg); tapsel(pg, '#tCont'); pg.wait_for_timeout(1200)
    if pg.evaluate('!!MODAL'): pg.evaluate('closeDialog()')
    pg.evaluate('talkHide()')
    sv = pg.evaluate('(() => { var all = G.officers.every(function (o) { return o.pf !== undefined; }); var moved = G.officers.filter(function (o) { return o.past && o.past.length; }).map(function (o) { return [o.n, o.pf, o.past]; }); return { all: all, moved: moved, sT: G.bases.filter(function (b) { return b.sT; }).length }; })()')
    ok(sv['all'] and len(sv['moved']) == 1 and sv['moved'][0][1] == 0 and sv['moved'][0][2] == [1] and sv['sT'] == 1, '저장했다 열어도 섬겼던 세력 · 탐색한 턴이 그대로 %s' % sv)
    # 0.10.1 까지의 저장(새 필드가 없다)
    pg.evaluate('(() => { var g = JSON.parse(localStorage.getItem(SAVE_KEY)); g.officers.forEach(function (o) { delete o.pf; delete o.past; delete o.exBy; }); g.bases.forEach(function (b) { delete b.sN; delete b.sT; }); localStorage.setItem(SAVE_KEY, JSON.stringify(g)); })()')
    reload(pg); tapsel(pg, '#tCont'); pg.wait_for_timeout(1200)
    if pg.evaluate('!!MODAL'): pg.evaluate('closeDialog()')
    pg.evaluate('talkHide()')
    old = pg.evaluate('(() => { return { ok: !!G && !$("title").classList.contains("off") === false, all: G.officers.every(function (o) { return o.pf !== undefined; }), same: G.officers.every(function (o) { return o.f < 0 || o.pf === o.f; }), say: (document.querySelector("#sheet .hm-say .tx span") || { textContent: "" }).textContent }; })()')
    ok(old['ok'] and old['all'] and old['same'] and old['say'], '옛 저장(0.10.1 까지)을 이어 하면 섬겼던 세력이 채워지고 헌책이 나온다 — ' + old['say'])
    pg.evaluate('showHelp()'); pg.wait_for_timeout(300)
    hp = pg.evaluate('document.querySelector("#modal").textContent')
    need = ['헌책', '다른 조언', '옛 관계', '멸망한 세력 출신', '수송과 보급', '보급 받기', '공유', 'QR', '치안', '시설의 레벨', '90일~360일', '창 · 극 · 노 · 기 · 병기', '오늘 숨은 인재를 만날지', '먹이 번진 듯']
    ok(all(n in hp for n in need), '도움말: %s' % [n for n in need if n not in hp])
    pg.evaluate('closeDialog()')
B.run(steps, 390, 844, 2)
errs = [e for e in B.errors if 'GPU stall' not in e and 'GL Driver' not in e and 'ERR_FILE_NOT_FOUND' not in e and 'willReadFrequently' not in e]
print('console errors:', errs[:6])
print('FAILS %d' % len(fails), fails)
sys.exit(1 if fails or errs else 0)
