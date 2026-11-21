# v0.10.1 — 화면 조작으로 확인: 군사의 적중률(지력 그대로) · 고른 시설의 표시와 부지 번호 · 짓는 중인 시설의 공사장 그림 · 세이브 칸
#   python3 tests/d21.py          찍은 그림은 tests/shots22/
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import taphex, tapsel
B.SHOTS = os.path.join(B.ROOT, 'shots22')
os.makedirs(B.SHOTS, exist_ok=True)
fails = []
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)
def txt(pg, sel): return pg.evaluate('(s) => { var e = document.querySelector(s); return e ? e.innerText.replace(/\\n+/g, " / ") : ""; }', sel)
def toast(pg): return pg.evaluate('$("toast").textContent')
def reload(pg):
    pg.reload(); pg.wait_for_function('window.R3 && R3.ready', timeout=60000); pg.wait_for_timeout(600)
def wait_play(pg, limit=240):
    for _ in range(limit * 4):
        pg.wait_for_timeout(250)
        if not pg.evaluate('!!UI.play'): return True
    return False
# 화면 상태 한 줌
VIEW = '''(() => { var m = $("modal"), v = buildView(), h = m.querySelector(".dlg-h h2");
  return { modal: !!MODAL, title: h ? h.textContent : "", see: m.classList.contains("see"), app: $("app").className, depth: MSTACK.length, fsel: MODAL && MODAL.fsel ? [MODAL.fsel.b, MODAL.fsel.pi] : null, dev: MODAL && MODAL.dev ? [MODAL.dev.b, MODAL.dev.pi] : null,
    sheet: getComputedStyle($("sheet")).visibility, spot: SPOT.on, fi: v ? v.fi : null, pi: v ? v.pi : null, lots: v ? v.lots.length : null, facs: v ? v.facs.length : null, tab: SHEET && SHEET.fac ? !!SHEET.fac() : false }; })()'''
def view(pg): return pg.evaluate(VIEW)
# 건설 자리 그림(#spot)의 한 점의 빛깔 [r, g, b, a]
PIX = '''function pix(px, py) { var cv = $("spot"), q = cv.getContext("2d").getImageData(Math.round(px * DPR), Math.round(py * DPR), 1, 1).data; return [q[0], q[1], q[2], q[3]]; }
function near(p, c, tol) { return Math.abs(p[0] - c[0]) <= tol && Math.abs(p[1] - c[1]) <= tol && Math.abs(p[2] - c[2]) <= tol; }'''
SPOTPIX = '(([c, r]) => { ' + PIX + ''' var R = hexRing(c, r, 1), p = hexPos(c, r), q = w2s(p[0], p[1], p[2]), u = pxPerUnit(q[2]), seal = 0, i, sa = safeArea();
  for (i = 0; i < R.length; i++) { var a = pix(R[i][0], R[i][1]); if (a[3] > 200 && near(a, [181, 51, 42], 46)) seal++; }
  var fpx = clamp(Math.round(u * 0.40), 10, 13), fly = q[1] + u * 0.16;                 // 이름표(번호 딱지 + 이름)의 자리: 고른 시설이면 붉은 딱지
  var tag = pix(q[0] + 4, fly - fpx / 2 - 2.5), mid = pix(q[0], q[1] - u * 0.45), far = pix(12, sa.top + 14);
  return { ring: seal, n: R.length, tag: tag, mid: mid, far: far, q: [Math.round(q[0]), Math.round(q[1])], area: [Math.round(sa.top), Math.round(sa.bottom)], a: Math.round(SPOT.a * 100) }; })'''
# 시험용 성: 번호가 정해진 자리에 시설을 놓는다(완성 · 짓는 중)
SETUP = '''(() => {
  var b = facCities(G.player)[0], F = function (t, lv) { return { t: t, lv: lv || 1, done: true, prog: 0, need: 0, rate: 0, hp: FAC_HP }; };
  var C = function (t, k) { return { t: t, lv: 1, done: false, prog: Math.round(FAC[t].build * k), need: FAC[t].build, rate: 120, hp: 300, by: [], t0: G.turn }; };
  var no = lotNos(b), byNo = {}; for (var i = 0; i < b.plots.length; i++) byNo[no[i]] = i;
  b.plots.forEach(function (p) { p.fac = null; });
  var plan = { 1: F("market", 2), 3: F("market", 2), 5: F("market"), 7: F("smithy"), 9: F("farm"), 11: C("farm", 0.5), 12: C("barracks", 0.1), 13: C("barracks", 0.8), 2: C("market", 0.2) };
  for (var k in plan) if (byNo[k] !== undefined) b.plots[byNo[k]].fac = plan[k];
  G.factions[G.player].ap = 235; b.gold = 2400; reindex(); clearSel(); selectBase(b); UI.dirty = true; requestDraw();
  return { id: b.id, n: b.n, plots: b.plots.length, byNo: byNo, pos: b.plots.map(function (p) { return [p.c, p.r]; }) };
})()'''
ROWS = '''Array.prototype.map.call(document.querySelectorAll("#sheet .row[data-a=plot]"), function (e) { var c = e.querySelector(".lno"), im = e.querySelector("img.th");
  return { pi: +e.getAttribute("data-v"), no: c ? +c.textContent : -1, nm: e.querySelector(".nm").textContent, ds: e.querySelector(".ds").textContent, src: im ? im.getAttribute("src").slice(0, 5) : "" }; })'''
SLOTS = '''(() => { var o = {}; slotIds().forEach(function (id) { var m = slotInfo(id); o[id] = m ? (m.bad ? "bad" : m.f + "|" + m.d + "|" + m.n + "|" + (m.t ? 1 : 0)) : null; }); return o; })()'''
SROWS = '''Array.prototype.map.call(document.querySelectorAll("#modal .svl .row"), function (e) { var b = e.querySelector("[data-a=ssave], [data-a=sload]"), d = e.querySelector("[data-a=sdel]");
  return { id: e.getAttribute("data-slot"), emp: e.classList.contains("emp"), t: e.querySelector(".mid").innerText.replace(/\\n+/g, " / "), act: b ? b.textContent : "", del: d ? d.textContent : "" }; })'''

def steps(pg):
    # ================= 0. 같은 판으로 시작(왕랑 · 씨앗 4242) =================
    pg.evaluate('localStorage.clear()'); reload(pg)
    t0 = pg.evaluate('[$("tCont").disabled, $("tLoad").disabled, $("tLoad").textContent, getComputedStyle($("tLoad")).display !== "none"]')
    ok(t0 == [True, False, '불러오기', True], '저장이 없는 제목 화면: [이어하기]는 꺼져 있고 [불러오기]는 열린다(v0.12 — 받은 세이브 파일을 가져올 수 있다) %s' % t0)
    r = pg.evaluate('(() => { var a = $("tCont").getBoundingClientRect(), b = $("tLoad").getBoundingClientRect(); return [Math.round(a.top) === Math.round(b.top), Math.round(a.width), Math.round(b.width), Math.round(b.right) <= window.innerWidth]; })()')
    ok(r[0] and abs(r[1] - r[2]) <= 2 and r[3], '두 단추가 한 줄에 나란히 %s' % r)
    pg.evaluate('() => { newGame(13, 4242); saveGame(); }'); reload(pg)
    tapsel(pg, '#tCont'); pg.wait_for_timeout(1500)
    if pg.evaluate('!!MODAL'): pg.evaluate('closeDialog()')
    pg.evaluate('talkHide()')
    info = pg.evaluate('(() => { var A = facAdv(G.player); return { ver: GAME_VERSION, f: G.factions[G.player].name, adv: A.n, int: A.int }; })()')
    ok(info['ver'] == 'v0.16', '판 번호 v0.16 [%s]' % info['ver'])
    ok(info['f'] == '왕랑', '(준비) 왕랑으로 시작 — 군사 %s(지력 %d)' % (info['adv'], info['int']))

    # ================= 1. 군사의 적중률 = 지력 =================
    print('1. 군사의 적중률')
    acc = pg.evaluate('(() => { var A = facAdv(G.player); return [adviceAcc(A, 0), adviceAcc(A, 30), adviceAcc(A, A.int), adviceAcc(A, A.int + 10), adviceAcc(A, 95), adviceAcc({ int: 100 }, 99), adviceAcc({ int: 40 }, 99)]; })()')
    I = info['int']
    ok(acc[0] == I and acc[1] == I and acc[2] == I, '상대가 더 똑똑하지 않으면 지력 그대로: 상대 없음 %d · 지력 30 %d · 같은 지력 %d' % (acc[0], acc[1], acc[2]))
    ok(acc[3] == I - 5 and acc[5] == 100 and acc[6] == 50, '상대가 10 더 똑똑하면 −5 (%d) · 지력 100은 100 · 바닥 50' % acc[3])
    pg.evaluate('showAdvisor()'); pg.wait_for_timeout(300)
    card = txt(pg, '#modal .advc'); cap = txt(pg, '#modal .cap')
    ok(('지력 %d' % I) in card and ('적중률 %d%%' % I) in card and ('지력 95인 상대에게는 %d%%' % acc[4]) in card, '군사 창: 적중률 = 지력 [%s]' % card)
    ok('지력이 곧 적중률' in cap, '군사 창의 풀이 [%s]' % cap)
    B.shot(pg, 'a1_advisor', 200); pg.evaluate('closeDialog()')
    # 등용: 표 아래의 말과 단추의 ○× 가 그 적중률로 나온다
    rc = pg.evaluate('''(() => { var b = facCities(G.player)[0], A = facAdv(G.player), h = G.officers.filter(function (o) { return o.st === "hidden" || o.st === "free"; }), lo = null, hi = null;
      h.forEach(function (o) { if (o.int <= A.int - 10 && !lo) lo = o; if (o.int >= A.int + 8 && !hi) hi = o; });
      [lo, hi].forEach(function (o) { if (o) { o.st = "free"; o.loc = b.id; } });
      G.factions[G.player].ap = 235; baseOfficers(b).forEach(function (o) { o.acted = false; }); selectBase(b);
      return { b: b.id, lo: lo ? { id: lo.id, n: lo.n, int: lo.int, acc: adviceAcc(A, lo.int) } : null, hi: hi ? { id: hi.id, n: hi.n, int: hi.int, acc: adviceAcc(A, hi.int) } : null }; })()''')
    print('  등용 대상', rc)
    ok(rc['lo'] is not None and rc['hi'] is not None, '(준비) 군사보다 덜 똑똑한 재야와 더 똑똑한 재야')
    for key in ('lo', 'hi'):
        t = rc[key]
        pg.locator('#sheet .tabs button').nth(2).tap(); pg.wait_for_timeout(400)
        tapsel(pg, '#sheet [data-a=recruit]'); pg.wait_for_timeout(500)
        tapsel(pg, '#modal .row[data-v="%d"]' % t['id']); pg.wait_for_timeout(500)
        tapsel(pg, '#modal [data-a=auto]'); pg.wait_for_timeout(300)
        sy = txt(pg, '#modal .pksay .say')
        want = I if key == 'lo' else I - round((t['int'] - I) * 0.5 + 1e-9)
        ok(t['acc'] == (I if key == 'lo' else t['acc']) and ('적중률 %d%%' % t['acc']) in sy and t['acc'] <= I and (key == 'lo' or t['acc'] < I), '등용(%s, 지력 %d): 군사의 말에 적중률 %d%% [%s]' % (t['n'], t['int'], t['acc'], sy))
        if key == 'lo': B.shot(pg, 'a2_recruit', 200)
        pg.evaluate('closeDialog()'); pg.wait_for_timeout(200)
    # 시설에 지르는 불(상대의 지력이 없다): 전에는 100% 였다
    fr = pg.evaluate('''(() => { var A = facAdv(G.player), u = { off: [A.id], f: G.player, type: "spear", troops: 3000, morale: 100 }; var a = advise(G.player, 10, 10, 92, 0); return [a.acc, A.int]; })()''')
    ok(fr[0] == fr[1], '상대의 지력이 없는 일(시설에 불)도 지력 그대로 %d%%' % fr[0])
    # 실제로 그만큼 맞는가: 이 군사가 재야 무장 한 사람에 대해 턴마다 내는 조언 3,000번
    hit = pg.evaluate('''((tid) => { var b = facCities(G.player)[0], t = off(tid), o = idleOfficers(b)[0], t0 = G.turn, n = 0, right = 0;
      for (var k = 1; k <= 3000; k++) { G.turn = 5000 + k; var a = recruitAdvice(b, o, t), real = recruitRoll(t) < recruitChance(b, o, t); n++; if (a.says === real) right++; }
      G.turn = t0; return [n, right]; })''', rc['lo']['id'])
    pct = 100.0 * hit[1] / hit[0]
    ok(abs(pct - I) < 3.0, '3,000번 가운데 맞힌 것 %.1f%% (적중률 %d%%)' % (pct, I))

    # ================= 2. 고른 시설의 표시 · 부지 번호 =================
    print('2. 고른 시설')
    st = pg.evaluate(SETUP); pg.wait_for_timeout(700)
    byNo = {int(k): v for k, v in st['byNo'].items()}
    pg.locator('#sheet .tabs button').nth(3).tap(); pg.wait_for_timeout(1300)
    rows = pg.evaluate(ROWS); v = view(pg)
    print('  줄', [(r['no'], r['nm'], r['src']) for r in rows])
    ok([r['no'] for r in rows] == sorted(r['no'] for r in rows) and len(rows) == 9, '지은 시설의 줄이 번호 차례 %s' % [r['no'] for r in rows])
    ok(all(byNo[r['no']] == r['pi'] for r in rows) and all(r['nm'].startswith(str(r['no'])) for r in rows), '줄 앞의 번호 = 그 부지의 번호(지도의 번호와 같다)')
    ok(all((r['src'] == 'blob:') == ('건설 중' in r['ds']) for r in rows) and sum(1 for r in rows if r['src'] == 'blob:') == 4, '짓는 중인 줄만 공사장 그림(작은 그림) %s' % [r['src'] for r in rows])
    ok(v['spot'] and v['fi'] == -1 and v['lots'] == st['plots'] - 9 and v['facs'] == 9 and v['sheet'] == 'visible', '시설 탭: 건설 자리가 비치고 고른 시설은 없다 %s' % {k: v[k] for k in ('spot', 'fi', 'lots', 'facs')})
    lab = pg.evaluate('(() => { var v = buildView(); return v.facs.map(function (f) { return [f.no, f.n, f.done, f.left]; }); })()')
    ok(all(x[0] >= 1 for x in lab) and all((x[3] == '') == x[2] for x in lab) and any(x[3] == '20일' for x in lab), '지도의 이름표에 넣을 것: 번호 · 이름 · 짓는 중이면 남은 날수 %s' % lab[:4])
    B.shot(pg, 'f1_tab', 200)
    # 2-1. 줄을 눌러 시설 창을 연다(③ 시장 Lv2 — 시장이 넷)
    p3 = byNo[3]; c3 = st['pos'][p3]
    tapsel(pg, '#sheet .row[data-a=plot][data-v="%d"]' % p3); pg.wait_for_timeout(1400)
    v = view(pg)
    ok(v['modal'] and v['fsel'] == [st['id'], p3] and v['title'] == '회계 ③ 시장 Lv2', '시설 창: 제목에 번호 [%s]' % v['title'])
    ok(v['see'] and 'seeing' in v['app'] and 'building' in v['app'] and v['sheet'] == 'hidden', '지도를 가리지 않는 창(아래 창은 숨는다) %s' % v['app'])
    ok(v['spot'] and v['fi'] == p3, '건설 자리 그림이 고른 시설을 안다 (fi %s)' % v['fi'])
    sp = pg.evaluate(SPOTPIX, c3)
    print('  빛깔', sp)
    ok(sp['a'] == 100 and sp['ring'] >= 8, '고른 칸에 붉은 테두리 (12점 가운데 %d점이 붉다)' % sp['ring'])
    ok(sp['tag'][3] > 200 and abs(sp['tag'][0] - 181) < 46 and sp['tag'][1] < 110, '이름표가 붉은 딱지 %s' % sp['tag'])
    ok(sp['mid'][3] < 40 and sp['far'][3] > 140, '고른 시설은 환하고(덮개 %d) 먼 곳은 어둡다(덮개 %d)' % (sp['mid'][3], sp['far'][3]))
    ok(sp['area'][0] + 30 < sp['q'][1] < sp['area'][1] - 10 and 20 < sp['q'][0] < 370, '고른 시설이 창 위쪽 지도 안에 보인다 %s / %s' % (sp['q'], sp['area']))
    other = pg.evaluate(SPOTPIX, st['pos'][byNo[5]])
    ok(other['ring'] <= 2 and other['mid'][3] > 140 and not (abs(other['tag'][0] - 181) < 46 and other['tag'][1] < 110 and other['tag'][3] > 200), '다른 시장(⑤)에는 테두리도 붉은 이름표도 없고 어둡다 (붉은 점 %d · 덮개 %d · 이름표 자리 %s)' % (other['ring'], other['mid'][3], other['tag']))
    B.shot(pg, 'f2_selected', 200)
    # 2-2. 지도에서 다른 시설을 누르면 그 시설로 바뀐다
    p12 = byNo[12]
    taphex(pg, *st['pos'][p12]); pg.wait_for_timeout(900)
    v = view(pg)
    ok(v['fsel'] == [st['id'], p12] and v['title'] == '회계 ⑫ 병영 Lv1' and v['depth'] == 0 and v['fi'] == p12, '지도에서 다른 시설(⑫ 병영, 짓는 중)을 누르면 그 시설로 [%s]' % v['title'])
    dl = pg.evaluate('(() => { var m = $("modal"), im = m.querySelector(".card img"); return { src: im.getAttribute("src"), site: siteUrl("barracks"), note: (m.querySelector(".note") || {}).textContent || "", demo: m.querySelector("[data-a=demo] b").textContent }; })()')
    ok(dl['src'] == dl['site'] and dl['src'].startswith('blob:') and '건설 중' in dl['note'] and dl['demo'] == '공사 중단', '짓는 중인 시설의 창: 공사장 그림 · 남은 날수 · [공사 중단]')
    sp = pg.evaluate(SPOTPIX, st['pos'][p12]); old = pg.evaluate(SPOTPIX, c3)
    ok(sp['ring'] >= 8 and old['ring'] <= 2, '테두리도 옮겨 갔다 (새 칸 %d점 · 앞의 칸 %d점)' % (sp['ring'], old['ring']))
    B.shot(pg, 'f3_site', 200)
    taphex(pg, *st['pos'][p12]); pg.wait_for_timeout(500)
    ok(view(pg)['fsel'] == [st['id'], p12], '같은 시설을 다시 눌러도 그대로')
    # 2-3. 빈 부지를 누르면 '무엇을 지을까요', 거기서 시설을 누르면 다시 시설 창
    p4 = byNo[4]
    taphex(pg, *st['pos'][p4]); pg.wait_for_timeout(900)
    v = view(pg)
    ok(v['dev'] == [st['id'], p4] and v['fsel'] is None and '무엇을 지을까요' in v['title'] and v['fi'] == -1 and v['pi'] == p4, "빈 부지(④)를 누르면 '무엇을 지을까요'로 [%s]" % v['title'])
    taphex(pg, *st['pos'][byNo[7]]); pg.wait_for_timeout(900)
    v = view(pg)
    ok(v['fsel'] == [st['id'], byNo[7]] and v['dev'] is None and v['title'] == '회계 ⑦ 대장간 Lv1', "'무엇을 지을까요'에서 시설(⑦ 대장간)을 누르면 그 시설의 창 [%s]" % v['title'])
    # 2-4. 닫기: 바깥을 누른다 · × · Esc
    out = pg.evaluate('''(() => { var b = G.bases[MODAL.fsel.b], sa = safeArea(), best = null;
      for (var dc = -9; dc <= 9; dc++) for (var dr = -9; dr <= 9; dr++) { var c = b.c + dc, r = b.r + dr; if (!inMap(c, r) || plotAt(c, r) || baseAt(c, r) || UAT[K(c, r)] || hdist(b.c, b.r, c, r) < 5) continue;
        var p = hexPos(c, r), q = w2s(p[0], p[1], p[2]); if (q && q[0] > 30 && q[0] < CW - 30 && q[1] > sa.top + 30 && q[1] < sa.bottom - 30) { best = [c, r]; break; } }
      return best; })()''')
    ok(out is not None, '(준비) 부지가 아닌 빈 칸')
    taphex(pg, *out); pg.wait_for_timeout(900)
    v = view(pg)
    ok(not v['modal'] and v['sheet'] == 'visible' and v['tab'] and v['spot'] and v['fi'] == -1 and 'seeing' not in v['app'], '바깥을 누르면 닫히고 시설 탭으로 돌아온다')
    tapsel(pg, '#sheet .row[data-a=plot][data-v="%d"]' % p3); pg.wait_for_timeout(900)
    tapsel(pg, '#modal [data-a=close]'); pg.wait_for_timeout(600)
    v1 = view(pg)
    tapsel(pg, '#sheet .row[data-a=plot][data-v="%d"]' % p3); pg.wait_for_timeout(900)
    pg.keyboard.press('Escape'); pg.wait_for_timeout(600)
    v2 = view(pg)
    ok(not v1['modal'] and v1['tab'] and not v2['modal'] and v2['tab'], '× 와 Esc 도 한 단계(시설 탭으로)')
    # 2-5. 흡수합병 · 철거가 전처럼 된다
    mg = pg.evaluate('''(() => { var b = facCities(G.player)[0], i, j, pair = null;
      for (i = 0; i < b.plots.length && !pair; i++) for (j = 0; j < b.plots.length; j++) if (i !== j && !b.plots[i].fac && !b.plots[j].fac && hdist(b.plots[i].c, b.plots[i].r, b.plots[j].c, b.plots[j].r) === 1) { pair = [i, j]; break; }      // 빈 부지 둘(끝나면 다시 빈다)
      var F = function () { return { t: "farm", lv: 1, done: true, prog: 0, need: 0, rate: 0, hp: FAC_HP }; };
      b.plots[pair[0]].fac = F(); b.plots[pair[1]].fac = F(); baseOfficers(b).forEach(function (o) { o.acted = false; }); b.gold = 2400; G.factions[G.player].ap = 235; reindex(); refreshSheet(); UI.dirty = true;
      return { pair: pair, cand: mergeCandidates(b, pair[0]).length, no: [lotNo(b, pair[0]), lotNo(b, pair[1])] }; })()''')
    pg.wait_for_timeout(500)
    ok(mg['cand'] >= 1, '(준비) 붙어 있는 농장 둘 %s' % mg['no'])
    tapsel(pg, '#sheet .row[data-a=plot][data-v="%d"]' % mg['pair'][0]); pg.wait_for_timeout(900)
    tapsel(pg, '#modal [data-a=merge]'); pg.wait_for_timeout(500)
    v = view(pg)
    ok(v['depth'] == 1 and 'seeing' in v['app'] and v['fi'] == mg['pair'][0] and '흡수합병' in v['title'], '흡수합병: 담당 무장 표가 겹쳐 뜨고 고른 시설의 표시는 그대로 [%s]' % v['title'])
    tapsel(pg, '#modal [data-a=auto]'); pg.wait_for_timeout(300); tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(900)
    aft = pg.evaluate('([a, b2]) => { var b = facCities(G.player)[0]; return [b.plots[a].fac ? b.plots[a].fac.lv : 0, !!b.plots[b2].fac, !!MODAL]; }', mg['pair'])
    ok(aft == [2, False, False], '합쳐져 Lv2, 옆 부지는 비고, 창은 닫혔다 %s' % aft)
    pg.wait_for_timeout(2600); pg.evaluate('talkHide()')
    tapsel(pg, '#sheet .row[data-a=plot][data-v="%d"]' % mg['pair'][0]); pg.wait_for_timeout(900)
    tapsel(pg, '#modal [data-a=demo]'); pg.wait_for_timeout(350)
    arm = pg.evaluate('document.querySelector("#modal [data-a=demo] b").textContent')
    tapsel(pg, '#modal [data-a=demo]'); pg.wait_for_timeout(700)
    aft = pg.evaluate('(a) => { var b = facCities(G.player)[0]; return [!!b.plots[a].fac, !!MODAL]; }', mg['pair'][0])
    ok(arm == '정말 철거?' and aft == [False, False], '철거: 한 번 더 묻고 비운다')
    # 2-6. 거점을 고르지 않은 채 지도에서 시설을 눌러도 표시된다 · 닫으면 덮개도 걷힌다
    pg.evaluate('clearSel()'); pg.wait_for_timeout(700)
    v0 = view(pg); p5 = byNo[5]; c5 = st['pos'][p5]
    taphex(pg, *c5); pg.wait_for_timeout(1300)
    v = view(pg); sp = pg.evaluate(SPOTPIX, c5)
    ok(not v0['spot'] and v['fsel'] == [st['id'], p5] and v['spot'] and v['fi'] == p5 and sp['ring'] >= 8, '지도에서 바로 눌러도 그 시설(⑤ 시장)이 표시된다 (붉은 점 %d)' % sp['ring'])
    # 성의 그림에 가린 부지(③ — 성 바로 뒤): 건설 자리를 보는 중에는 성이 아니라 그 부지가 집힌다
    hid = pg.evaluate('(([c, r]) => { var p = hexPos(c, r), s = w2s(p[0], p[1], p[2]), g = pickGround(s[0], s[1]), h = worldToHex(g[0], g[1]), b = G.bases[MODAL.fsel.b]; var on = SPOT.on; SPOT.on = false; var raw = pickAt(s[0], s[1]); SPOT.on = on; return { ground: h, raw: raw, base: [b.c, b.r], now: pickAt(s[0], s[1]) }; })', c3)
    taphex(pg, *c3); pg.wait_for_timeout(900)
    v = view(pg)
    ok(hid['raw'] == hid['base'] and hid['now'] == c3 and v['fsel'] == [st['id'], p3] and v['title'] == '회계 ③ 시장 Lv2', '성의 그림에 가린 칸(③)도 건설 자리를 보는 중에는 부지로 집힌다 (전에는 성 %s 이 집혔다) [%s]' % (hid['raw'], v['title']))
    pg.evaluate('backDialog()'); pg.wait_for_timeout(900)
    v = view(pg)
    ok(not v['modal'] and not v['spot'] and v['sheet'] == 'visible', '닫으면 덮개가 걷힌다')
    # 2-7. 빈 부지가 없는 성: 시설 탭에는 덮개가 없지만, 시설을 고르면 그 시설만 비춘다
    full = pg.evaluate('''(() => { var b = facCities(G.player)[0], keep = b.plots.map(function (p) { return p.fac; });
      b.plots.forEach(function (p) { if (!p.fac) p.fac = { t: "farm", lv: 1, done: true, prog: 0, need: 0, rate: 0, hp: FAC_HP }; }); reindex(); selectBase(b); window._keep = keep; return b.plots.length; })()''')
    pg.wait_for_timeout(500); pg.locator('#sheet .tabs button').nth(3).tap(); pg.wait_for_timeout(900)
    v0 = view(pg)
    tapsel(pg, '#sheet .row[data-a=plot][data-v="%d"]' % p3); pg.wait_for_timeout(1300)
    v = view(pg); sp = pg.evaluate(SPOTPIX, c3)
    ok(not v0['spot'] and v['spot'] and v['lots'] == 0 and v['fi'] == p3 and sp['ring'] >= 8 and sp['far'][3] > 140, '빈 부지가 없는 성에서도 고른 시설은 표시된다')
    pg.evaluate('(() => { closeDialog(); var b = facCities(G.player)[0]; b.plots.forEach(function (p, i) { p.fac = window._keep[i]; }); reindex(); refreshSheet(); UI.dirty = true; })()'); pg.wait_for_timeout(600)

    # ================= 3. 짓는 중인 시설의 그림 =================
    print('3. 공사장 그림')
    g = pg.evaluate('''(([bid, p2, p12, p13, p3]) => { var one = function (pi) { var b = G.bases[bid], fc = b.plots[pi].fac, fo = R3.facs[bid + ":" + pi], k = fo.sp.userData.key;
        return { key: k, stage: fc.done ? -1 : siteStage(fc), same: fo.sp.material.map === TEX[k], op: fo.sp.material.opacity, cv: !!(TEX[k].image && TEX[k].image.getContext), w: SPRITES[k].w === SPRITES[fc.t].w && SPRITES[k].h === SPRITES[fc.t].h && SPRITES[k].ay === SPRITES[fc.t].ay }; };
      syncScene(); return { m2: one(p2), b12: one(p12), b13: one(p13), m3: one(p3) }; })''', [st['id'], byNo[2], byNo[12], byNo[13], p3])
    print('  ', g)
    ok(g['m2']['key'] == 'market@0' and g['b12']['key'] == 'barracks@0' and g['b13']['key'] == 'barracks@2', '짓는 중: 공사장 그림(공사가 나아간 만큼 단계가 다르다) %s' % [g[k]['key'] for k in ('m2', 'b12', 'b13')])
    ok(all(g[k]['same'] and g[k]['op'] == 1 and g[k]['cv'] and g[k]['w'] for k in ('m2', 'b12', 'b13')), '화면에서 만든 그림 · 반투명이 아니다 · 크기는 완성된 그림과 같다')
    ok(g['m3']['key'] == 'market' and g['m3']['op'] == 1 and not g['m3']['cv'], '다 지은 시설은 전과 같은 그림')
    px = pg.evaluate('''(() => { var cnt = function (c) { var d = c.getContext("2d").getImageData(0, 0, c.width, c.height).data, o = { och: 0, red: 0, ink: 0, n: 0 };
        for (var i = 0; i < d.length; i += 4) { if (d[i + 3] < 40) continue; o.n++; var r = d[i], g = d[i + 1], b = d[i + 2];
          if (d[i + 3] > 200 && Math.abs(r - 156) < 30 && Math.abs(g - 108) < 30 && Math.abs(b - 52) < 30) o.och++;
          if (d[i + 3] > 200 && r > 150 && g < 90 && b < 80) o.red++; if (r + g + b < 240) o.ink++; }
        return o; };
      var orig = document.createElement("canvas"), S = SPRITES.market; orig.width = S.w; orig.height = S.h; orig.getContext("2d").drawImage(SITE_IMG.market, 0, 0, S.w, S.h);
      return { s0: cnt(TEX[siteTexKey("market", 0)].image), s2: cnt(TEX[siteTexKey("market", 2)].image), o: cnt(orig) }; })()''')
    print('  ', px)
    ok(px['s0']['och'] > 400 and 20 < px['s0']['red'] < px['o']['red'] / 3, '비계(대나무 빛 %d점)와 붉은 깃발(%d점 — 완성된 시장의 붉은 지붕 %d점은 사라졌다)' % (px['s0']['och'], px['s0']['red'], px['o']['red']))
    ok(px['s0']['ink'] < px['s2']['ink'] < px['o']['ink'], '밑그림은 공사가 나아갈수록 짙어진다 (짙은 점 %d → %d, 완성 %d)' % (px['s0']['ink'], px['s2']['ink'], px['o']['ink']))
    pg.evaluate('(() => { var b = facCities(G.player)[0], p = hexCenter(b.c, b.r); clearSel(); cam.x = p[0]; cam.y = p[1]; cam.z = 1.7; clampCam(); requestDraw(); })()'); pg.wait_for_timeout(900)
    B.shot(pg, 'g1_sites', 200)
    # 단계가 오르면 그림이 바뀌고, 다 지으면 완성된 그림으로
    up = pg.evaluate('''(([bid, pi]) => { var b = G.bases[bid], fc = b.plots[pi].fac, fo = R3.facs[bid + ":" + pi], out = [];
      [0.05, 0.4, 0.7].forEach(function (k) { fc.prog = Math.round(fc.need * k); syncScene(); out.push(fo.sp.userData.key); });
      fc.prog = fc.need - 10; fc.rate = 120; fc.by = []; return out; })''', [st['id'], byNo[12]])
    ok(up == ['barracks@0', 'barracks@1', 'barracks@2'], '공사가 3분의 1씩 나아갈 때마다 그림이 바뀐다 %s' % up)
    pg.evaluate('G.factions[G.player].ap = 0'); tapsel(pg, '#btnEnd'); pg.wait_for_timeout(500)
    if pg.evaluate('!!MODAL && !UI.play'): tapsel(pg, '#modal [data-a=go], #modal [data-a=ok], #modal .btn.pri'); pg.wait_for_timeout(400)
    ok(wait_play(pg), '(준비) 열흘이 흐른다')
    pg.wait_for_timeout(600)
    if pg.evaluate('!!MODAL'): pg.evaluate('closeDialog()')
    pg.wait_for_timeout(400)
    fin = pg.evaluate('''(([bid, pi]) => { var b = G.bases[bid], fc = b.plots[pi].fac, fo = R3.facs[bid + ":" + pi]; syncScene(); return [fc.done, fo.sp.userData.key, fo.sp.material.map === TEX.barracks, fo.sp.material.opacity]; })''', [st['id'], byNo[12]])
    ok(fin == [True, 'barracks', True, 1], '다 지으면 완성된 그림으로 %s' % fin)

    # ================= 4. 세이브 칸 =================
    print('4. 세이브 칸')
    s0 = pg.evaluate(SLOTS)
    ok(s0['auto'] is not None and s0['auto'].startswith('왕랑|') and all(s0[k] is None for k in ('s1', 's2', 's3', 's4', 's5', 's6')) and len(s0) == 8, '칸은 자동 · 직전 · 1~6 — 처음에는 자동 저장만 %s' % s0['auto'])
    tapsel(pg, '#btnMenu'); pg.wait_for_timeout(300)
    note = txt(pg, '#modal .note')
    tapsel(pg, '#modal [data-a=save]'); pg.wait_for_timeout(400)
    rs = pg.evaluate(SROWS); v = view(pg)
    ok(v['title'] == '저장 · 불러오기' and v['depth'] == 1 and '저장 칸 6개' in note, '메뉴 → 저장: 칸을 고르는 창(메뉴 위에 겹쳐 뜬다)')
    ok([r['id'] for r in rs] == ['s1', 's2', 's3', 's4', 's5', 's6'] and all(r['emp'] and r['act'] == '저장' and r['del'] == '' and '빈 칸' in r['t'] for r in rs) and pg.evaluate('document.querySelector("#modal .seg .on").textContent') == '저장', '저장 쪽: 번호 칸 여섯(모두 빈 칸)')
    B.shot(pg, 's1_save', 200)
    cur = pg.evaluate('serialize()')
    tapsel(pg, '#modal [data-slot=s1] [data-a=ssave]'); pg.wait_for_timeout(500)
    a = pg.evaluate('[localStorage.getItem("chunhado_save_v2_s1") === serialize(), localStorage.getItem("chunhado_save_v2") === serialize(), !!MODAL]'); rs = pg.evaluate(SROWS)
    ok(a == [True, True, True] and '1번 칸에 저장했습니다' in toast(pg), '빈 칸은 바로 저장 — 자동 저장도 같은 모습이 된다 [%s]' % toast(pg))
    ok(rs[0]['id'] == 's1' and not rs[0]['emp'] and '왕랑' in rs[0]['t'] and pg.evaluate('dateStr()') in rs[0]['t'] and '1성' in rs[0]['t'] and '오늘' in rs[0]['t'] and rs[0]['del'] == '×', '찬 칸의 줄: 세력 · 날짜 · 거점 · 병력 · 저장한 때 [%s]' % rs[0]['t'])
    # 덮어쓰기: 한 번 더 눌러야 한다
    pg.evaluate('(() => { facCities(G.player)[0].gold += 123; })()')
    tapsel(pg, '#modal [data-slot=s1] [data-a=ssave]'); pg.wait_for_timeout(400)
    b1 = pg.evaluate('[document.querySelector("#modal [data-slot=s1] [data-a=ssave]").textContent, localStorage.getItem("chunhado_save_v2_s1") === serialize()]')
    tapsel(pg, '#modal [data-a=smode][data-v=load]'); pg.wait_for_timeout(300); tapsel(pg, '#modal [data-a=smode][data-v=save]'); pg.wait_for_timeout(300)
    b2 = pg.evaluate('document.querySelector("#modal [data-slot=s1] [data-a=ssave]").textContent')
    tapsel(pg, '#modal [data-slot=s1] [data-a=ssave]'); pg.wait_for_timeout(350); tapsel(pg, '#modal [data-slot=s1] [data-a=ssave]'); pg.wait_for_timeout(500)
    b3 = pg.evaluate('localStorage.getItem("chunhado_save_v2_s1") === serialize()')
    ok(b1 == ['덮어쓰기', False] and b2 == '저장' and b3, '찬 칸: 한 번 누르면 [덮어쓰기]로 바뀌기만 하고, 한 번 더 눌러야 덮어쓴다(쪽을 바꾸면 물음이 풀린다)')
    tapsel(pg, '#modal [data-slot=s2] [data-a=ssave]'); pg.wait_for_timeout(500)
    # 불러오기 쪽
    tapsel(pg, '#modal [data-a=smode][data-v=load]'); pg.wait_for_timeout(400)
    rs = pg.evaluate(SROWS)
    ok([r['id'] for r in rs] == ['auto', 's1', 's2'] and all(r['act'] == '불러오기' for r in rs) and rs[0]['del'] == '' and rs[1]['del'] == '×', '불러오기 쪽: 찬 칸만(자동 · 1 · 2), 자동 저장은 지울 수 없다')
    B.shot(pg, 's2_load', 200)
    # 하던 판을 바꾼 뒤 1번 칸을 불러온다 → 바꾼 모습은 '직전' 칸에 남는다
    s1 = pg.evaluate('localStorage.getItem("chunhado_save_v2_s1")')
    pg.evaluate('(() => { facCities(G.player)[0].gold += 777; })()')
    before = pg.evaluate('serialize()'); g_before = pg.evaluate('facCities(G.player)[0].gold')
    tapsel(pg, '#modal [data-slot=s1] [data-a=sload]'); pg.wait_for_timeout(1500)
    a = pg.evaluate('[!!MODAL, facCities(G.player)[0].gold, localStorage.getItem("chunhado_save_v2_prev"), localStorage.getItem("chunhado_save_v2"), $("title").classList.contains("off")]')
    ok(a[0] is False and a[1] == g_before - 777 and a[4] and '1번 칸을 불러왔습니다' in toast(pg), '불러오면 그 칸의 모습으로 이어진다 [%s]' % toast(pg))
    ok(a[2] == before and a[3] == s1, "하던 판의 지금 모습은 '직전' 칸에, 불러온 판은 자동 저장에")
    pg.wait_for_timeout(1500); pg.evaluate('talkHide()')
    tapsel(pg, '#btnMenu'); pg.wait_for_timeout(300); tapsel(pg, '#modal [data-a=load]'); pg.wait_for_timeout(400)
    rs = pg.evaluate(SROWS)
    ok([r['id'] for r in rs] == ['auto', 'prev', 's1', 's2'] and pg.evaluate('document.querySelector("#modal .seg .on").textContent') == '불러오기' and '직전' in pg.evaluate('document.querySelector("#modal [data-slot=prev] .svn").textContent'), "메뉴 → 불러오기: 자동 · 직전 · 1 · 2")
    tapsel(pg, '#modal [data-slot=prev] [data-a=sload]'); pg.wait_for_timeout(1500)
    a = pg.evaluate('[facCities(G.player)[0].gold, localStorage.getItem("chunhado_save_v2_prev") === localStorage.getItem("chunhado_save_v2_s1"), localStorage.getItem("chunhado_save_v2")]')
    ok(a[0] == g_before and a[1] and a[2] == before and '직전 판을 불러왔습니다' in toast(pg), "'직전'을 불러오면 되돌아간다(그때 하던 판이 다시 직전 칸에)")
    pg.wait_for_timeout(1500); pg.evaluate('talkHide()')
    # 지우기: × → 지움
    tapsel(pg, '#btnMenu'); pg.wait_for_timeout(300); tapsel(pg, '#modal [data-a=load]'); pg.wait_for_timeout(400)
    tapsel(pg, '#modal [data-slot=s2] [data-a=sdel]'); pg.wait_for_timeout(350)
    d1 = pg.evaluate('[document.querySelector("#modal [data-slot=s2] [data-a=sdel]").textContent, !!localStorage.getItem("chunhado_save_v2_s2")]')
    tapsel(pg, '#modal [data-slot=s2] [data-a=sdel]'); pg.wait_for_timeout(400)
    d2 = pg.evaluate('[!!localStorage.getItem("chunhado_save_v2_s2"), !!JSON.parse(localStorage.getItem("chunhado_save_v2_meta")).s2, !!document.querySelector("#modal [data-slot=s2]")]')
    ok(d1 == ['지움', True] and d2 == [False, False, False], '지우기: × 를 누르면 [지움]으로 바뀌고, 한 번 더 눌러야 지운다')
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(300)
    # 처음으로 → 제목 화면
    tapsel(pg, '#btnMenu'); pg.wait_for_timeout(300); tapsel(pg, '#modal [data-a=title]'); pg.wait_for_timeout(700)
    t1 = pg.evaluate('[!$("title").classList.contains("off"), $("tCont").disabled, $("tLoad").disabled, $("talk").classList.contains("on")]')
    ok(t1 == [True, False, False, False], '제목 화면: [이어하기] · [불러오기] 켜짐, 대화창은 남지 않는다 %s' % t1)
    B.shot(pg, 's3_title', 300)
    tapsel(pg, '#tLoad'); pg.wait_for_timeout(500)
    rs = pg.evaluate(SROWS); v = view(pg)
    ok(v['title'] == '불러오기' and pg.evaluate('!document.querySelector("#modal .seg")') and [r['id'] for r in rs] == ['auto', 'prev', 's1'], '제목 화면의 불러오기: 저장 쪽 없이 찬 칸만 %s' % [r['id'] for r in rs])
    B.shot(pg, 's4_title_load', 200)
    pg.evaluate('backDialog()'); pg.wait_for_timeout(300)
    ok(pg.evaluate('!MODAL'), '닫으면 제목 화면 그대로')
    # 새 게임(원소): 하던 판(자동 저장)이 직전 칸으로 가고, 새 판이 바로 자동 저장이 된다
    auto0 = pg.evaluate('localStorage.getItem("chunhado_save_v2")')
    tapsel(pg, '#tNew'); pg.wait_for_timeout(300)
    tapsel(pg, '#modal .row', 4); tapsel(pg, '#modal [data-a=go]'); pg.wait_for_timeout(700)
    tapsel(pg, '#modal [data-a=close]'); pg.wait_for_timeout(900); pg.evaluate('talkHide()')
    a = pg.evaluate('[G.factions[G.player].name, localStorage.getItem("chunhado_save_v2_prev"), localStorage.getItem("chunhado_save_v2") === serialize()]'); sl = pg.evaluate(SLOTS)
    ok(a[0] == '원소' and a[1] == auto0 and a[2] and sl['auto'].startswith('원소|') and sl['prev'].startswith('왕랑|') and sl['s1'].startswith('왕랑|'), '새 게임: 하던 판은 직전 칸에, 새 판은 바로 자동 저장에 %s' % {k: sl[k] for k in ('auto', 'prev', 's1')})
    # 다시 열어도 그대로
    reload(pg)
    t2 = pg.evaluate('[$("tCont").disabled, $("tLoad").disabled]'); sl2 = pg.evaluate(SLOTS)
    ok(t2 == [False, False] and sl2 == sl, '다시 열어도 칸이 그대로다')
    tapsel(pg, '#tLoad'); pg.wait_for_timeout(500); tapsel(pg, '#modal [data-slot=s1] [data-a=sload]'); pg.wait_for_timeout(1600)
    a = pg.evaluate('[G.factions[G.player].name, $("title").classList.contains("off"), !!MODAL, localStorage.getItem("chunhado_save_v2") === localStorage.getItem("chunhado_save_v2_s1")]'); sl = pg.evaluate(SLOTS)
    ok(a == ['왕랑', True, False, True] and sl['prev'].startswith('원소|'), '제목 화면에서 1번 칸을 불러온다 → 왕랑의 판, 자동 저장이던 원소의 판은 직전 칸에')
    pg.evaluate('talkHide()')
    # 요약이 없는 옛 저장(0.10까지) · 열 수 없는 저장 · 저장 공간이 모자랄 때
    pg.evaluate('(() => { localStorage.removeItem("chunhado_save_v2_meta"); localStorage.setItem("chunhado_save_v2_s3", "garbage"); })()')
    tapsel(pg, '#btnMenu'); pg.wait_for_timeout(300); tapsel(pg, '#modal [data-a=load]'); pg.wait_for_timeout(400)
    rs = pg.evaluate(SROWS); m = pg.evaluate('JSON.parse(localStorage.getItem("chunhado_save_v2_meta") || "{}")')
    r_auto = [r for r in rs if r['id'] == 'auto'][0]; r3 = [r for r in rs if r['id'] == 's3'][0]
    ok('왕랑' in r_auto['t'] and '오늘' not in r_auto['t'] and m.get('auto', {}).get('f') == '왕랑' and m['auto']['t'] == 0, '요약이 없는 저장(전의 판에서 쓴 것)은 저장본을 읽어 요약을 다시 만든다 [%s]' % r_auto['t'])
    ok('열 수 없는 저장' in r3['t'] and r3['act'] == '' and r3['del'] == '×', '열 수 없는 저장은 그렇게 적고 지울 수만 있다 [%s]' % r3['t'])
    tapsel(pg, '#modal [data-slot=s3] [data-a=sdel]'); pg.wait_for_timeout(350); tapsel(pg, '#modal [data-slot=s3] [data-a=sdel]'); pg.wait_for_timeout(350)
    tapsel(pg, '#modal [data-a=smode][data-v=save]'); pg.wait_for_timeout(300)
    pg.evaluate('(() => { window._set = Storage.prototype.setItem; Storage.prototype.setItem = function (k, v) { if (String(v).length > 2000) throw new Error("QuotaExceededError"); return window._set.call(this, k, v); }; })()')
    tapsel(pg, '#modal [data-slot=s4] [data-a=ssave]'); pg.wait_for_timeout(500)
    q = pg.evaluate('(() => { Storage.prototype.setItem = window._set; return [!!localStorage.getItem("chunhado_save_v2_s4"), document.querySelector("#modal [data-slot=s4]").classList.contains("emp")]; })()')
    ok(q == [False, True] and '저장 공간이 모자랍니다' in toast(pg), '저장 공간이 모자라면 알리고 칸은 빈 채로 [%s]' % toast(pg))
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(300)
    # 판이 끝나면 자동 저장만 지워진다
    pg.evaluate('(() => { G.over = "lose"; showGameOver(); })()'); pg.wait_for_timeout(500)
    sl = pg.evaluate(SLOTS)
    ok(sl['auto'] is None and sl['s1'] is not None and sl['prev'] is not None, '판이 끝나면 자동 저장만 지워지고 번호 칸 · 직전 칸은 남는다')
    tapsel(pg, '#modal [data-a=t]'); pg.wait_for_timeout(700)
    t3 = pg.evaluate('[!$("title").classList.contains("off"), $("tCont").disabled, $("tLoad").disabled]')
    ok(t3 == [True, True, False], '끝난 뒤의 제목 화면: [이어하기]는 꺼지고 [불러오기]는 켜져 있다 %s' % t3)

    # ================= 5. 도움말 =================
    pg.evaluate('showHelp()'); pg.wait_for_timeout(300)
    hp = pg.evaluate('document.querySelector("#modal").textContent')
    ok('군사의 지력 그대로' in hp and '직전' in hp and '번호 칸 6개' in hp and '붉은 이름표' in hp and '공사장' in hp, '도움말: 군사의 적중률 · 저장 칸 · 고른 시설 · 공사장')
    pg.evaluate('closeDialog()')
B.run(steps, 390, 844, 2)
errs = [e for e in B.errors if 'GPU stall' not in e and 'GL Driver' not in e and 'ERR_FILE_NOT_FOUND' not in e and 'willReadFrequently' not in e]
print('console errors:', errs[:6])
print('FAILS %d' % len(fails), fails)
sys.exit(1 if fails or errs else 0)
