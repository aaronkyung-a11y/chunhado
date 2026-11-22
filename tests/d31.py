# v0.18 — 화면 조작으로 확인: 제목 화면(관우 전신 · 三國志 天下圖) · 얼굴을 누르면 뜨는 무장 카드 · 특기 풀이와 고르는 표의 병종 적성
#   · 확률을 말로(가늠) · 군사의 추천 · 전법의 새 이름과 견인(끌어당김) · 얼굴이 붙은 부대 이름표 · 단추의 두께
#   python3 tests/d31.py          찍은 그림은 tests/shots33/
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import taphex, tapsel
B.SHOTS = os.path.join(B.ROOT, 'shots33')
os.makedirs(B.SHOTS, exist_ok=True)
fails = []
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)
def toast(pg): return pg.evaluate('$("toast").textContent')
def head(pg): return pg.evaluate('MODAL ? document.querySelector("#modal .dlg-h h2").textContent : ""')
WORDS = ['불가', '매우 낮음', '낮음', '반반', '높음', '매우 높음', '확실']
COARSE = ['불가', '낮은 듯', '반반인 듯', '높은 듯', '확실']
# 내 하후돈(극병 S) 부대 a 옆에 적 부대 d 를 세운다. T = { a, d, f, b }
SETUP = """() => {
  G.aiOnly = false; if (G.peace) G.peace.until = 0;
  function clear(c, r) { return inMap(c, r) && terr(c, r) === 'p' && !UAT[K(c, r)] && BAT[K(c, r)] === undefined && !PAT[K(c, r)]; }
  var f = null;
  for (var r = 6; r < H - 6 && !f; r++) for (var c = 6; c < W - 6 && !f; c++) { var good = true; for (var dr = -3; dr <= 3 && good; dr++) for (var dc = -4; dc <= 4 && good; dc++) if (!clear(c + dc, r + dr)) good = false; if (good) f = [c, r]; }
  var b = facCities(G.player)[0], eb = G.bases.filter(function (x) { return x.owner >= 0 && x.owner !== G.player && x.kind === 'city'; })[1];
  [b, eb].forEach(function (x) { x.troops = 90000; x.w.spear = x.w.halberd = x.w.bow = x.w.horse = 60000; x.food = 400000; x.gold = 9000; G.factions[x.owner].ap = 250; });
  function O(n) { return G.officers.filter(function (o) { return o.n === n; })[0]; }
  var a = cmdDeploy(b, { type: 'halberd', ids: [O('하후돈').id], troops: 6000, food: 6000 }).unit;
  var d = cmdDeploy(eb, { type: 'spear', ids: [idleOfficers(eb)[0].id], troops: 6000, food: 6000 }).unit;
  var k = cmdDeploy(b, { type: 'spear', ids: [O('조인').id], troops: 3000, food: 3000 }).unit;
  placeUnit(a, f[0], f[1]); placeUnit(d, f[0] + 1, f[1]); placeUnit(k, f[0] - 3, f[1] + 2);
  [a, d, k].forEach(function (u) { u.born = -9; u.done = false; u.mp = uMaxMp(u); u.morale = 80; });
  var p = hexCenter(f[0], f[1]); cam.x = p[0]; cam.y = p[1]; cam.z = 1.5; clampCam(); HOME.open = false; clearSel(); UI.dirty = true; syncScene(); requestDraw();
  window.T = { a: a.id, d: d.id, k: k.id, f: f, b: b.id, eb: eb.id };
  return window.T;
}"""
RESET = """() => { var a = UMAP[T.a], d = UMAP[T.d], k = UMAP[T.k]; placeUnit(a, T.f[0], T.f[1]); placeUnit(d, T.f[0] + 1, T.f[1]); placeUnit(k, T.f[0] - 3, T.f[1] + 2);
  [a, d, k].forEach(function (u) { u.done = false; u.morale = 80; u.troops = 6000; u.status = null; u.stT = 0; u.ox = -1; }); G.fires = {}; talkHide(); if (MODAL) closeDialog(); clearSel(); syncScene(); requestDraw(); }"""
ACTS = """() => Array.prototype.map.call(document.querySelectorAll('#sheet .act[data-a=act]'), function (e) {
  var b = e.querySelector('b'), fx = e.querySelector('small.fx'), sm = e.querySelectorAll('small'), sub = sm.length ? sm[sm.length - 1] : null, g = e.querySelector('.odg');
  return { label: b ? b.childNodes[0].textContent.trim() : '', han: e.querySelector('.hj') ? e.querySelector('.hj').textContent : '', fx: fx ? fx.textContent : '', sub: sub && sub !== fx ? sub.textContent : '',
    gauge: g ? [g.querySelectorAll('u').length, g.querySelectorAll('u.on').length, g.classList.contains('dim')] : null, rec: !!e.querySelector('.rec'), off: e.classList.contains('off'), fit: e.scrollWidth <= e.clientWidth + 1 }; })"""
TARGET = """() => { var a = UMAP[T.a], d = UMAP[T.d]; selectUnit(a, true); UI.target = { kind: 'unit', u: d, c: d.c, r: d.r }; refreshSheet(); requestDraw(); }"""
CARD = """() => { var e = $('ocard'); if (!e || !e.classList.contains('on')) return null; var r = e.querySelector('.oc').getBoundingClientRect();
  return { name: e.querySelector('h2').textContent.trim(), bars: e.querySelectorAll('.bar').length, apt: e.querySelectorAll('.apt > div').length, sk: (e.querySelector('.skp') || e.querySelector('.oc-b')).textContent,
    scene: !!e.querySelector('.card .por'), stats: e.querySelector('.stats').textContent, unit: e.querySelector('.ocu') ? e.querySelector('.ocu').textContent : '', inView: r.top >= 0 && r.bottom <= innerHeight + 1 && r.left >= 0 && r.right <= innerWidth + 1, id: OCARD }; }"""
def steps(pg):
    # ---------- 1. 제목 화면 ----------
    t = pg.evaluate('''() => { var ti = $('title'), cs = getComputedStyle(ti), m = document.querySelector('.t-menu').getBoundingClientRect(), nm = document.querySelector('.t-name').getBoundingClientRect();
      var bs = Array.prototype.map.call(document.querySelectorAll('.t-menu button:not([hidden])'), function (b) { var r = b.getBoundingClientRect(); return [b.textContent, Math.round(r.top), Math.round(r.bottom), r.right <= innerWidth && r.left >= 0, b.scrollWidth <= b.clientWidth + 1]; });
      return { han: document.querySelector('.t-han').textContent, seal: document.querySelector('.t-seal').textContent, ko: !!document.querySelector('.t-ko'), bg: cs.backgroundImage.slice(0, 26), bgLen: cs.backgroundImage.length, size: cs.backgroundSize, pos: cs.backgroundPosition,
        menuTop: m.top / innerHeight, nameBottom: nm.bottom / innerHeight, nameLeft: nm.left / innerWidth, bs: bs, ver: $('tVer').textContent, shadow: getComputedStyle($('tNew')).boxShadow, inline: (ti.style.backgroundImage || '').length, js: TITLE_IMG.length, vh: innerHeight }; }''')
    print('  제목:', {k: v for k, v in t.items() if k != 'bs'}); B.shot(pg, 'a1_title', 300)
    ok(t['han'] == '三國志' and t['seal'] == '天下圖' and not t['ko'], '제목은 모두 한자 — 三國志 + 낙관 天下圖 [%s %s]' % (t['han'], t['seal']))
    ok(t['bg'].startswith('url("data:image/jpeg;base') and t['bgLen'] > 300000 and t['size'] == 'cover', '제목 그림(관우 전신)이 화면을 덮는다 — CSS 에 들어 있어 첫 화면부터 보인다(%d자, %s)' % (t['bgLen'], t['size']))
    ok(t['js'] == 0 and t['inline'] == 0, '제목 그림은 한 번만 들어 있다(스크립트 쪽은 비었다)')
    ok(t['menuTop'] >= 0.76 and all(b[3] and b[4] for b in t['bs']) and len(t['bs']) == 5, '단추 다섯은 아래 %.0f%% 안에 두 줄로 — 발끝까지 보인다 %s' % ((1 - t['menuTop']) * 100, [b[0] for b in t['bs']]))
    ok(t['nameBottom'] < 0.36 and t['nameLeft'] > 0.70, '제목 글씨는 오른쪽 위 빈 종이에(아래 끝 %.0f%%, 왼쪽 끝 %.0f%%)' % (t['nameBottom'] * 100, t['nameLeft'] * 100))
    ok(t['ver'].startswith('v0.18') and '삼국지 천하도' in t['ver'], '판 번호 줄: ' + t['ver'])
    ok(t['shadow'] != 'none' and 'inset' in t['shadow'], '단추에 두께(그림자)가 있다')
    # 세력을 고르는 창의 얼굴에는 번호가 없다(판 밖)
    tapsel(pg, '#tNew'); pg.wait_for_timeout(400)
    ok(pg.evaluate('document.querySelectorAll("#modal [data-oid]").length') == 0 and pg.evaluate('document.querySelectorAll("#modal .por").length') > 0, '세력을 고르는 창: 얼굴은 있지만 누를 수 있는 무장 카드는 없다(판이 시작되기 전)')
    pg.evaluate('closeDialog()')
    # ---------- 2. 판을 시작한다 ----------
    B.start(pg, 0)
    ok(pg.evaluate('GAME_VERSION') == 'v0.18' and pg.evaluate('UI.pct') is True, '판 번호 v0.18 · 시험 틀은 확률을 숫자로 켜 둔다')
    T = pg.evaluate(SETUP); pg.wait_for_timeout(600)
    # ---------- 3. 부대 이름표: 얼굴이 판에 붙어 한 덩어리 ----------
    try: pg.wait_for_function('R3.units[T.a] && R3.units[T.a].hasFace', timeout=8000)      # 초상 그림은 처음 쓸 때 불러온다
    except Exception: pass
    u = pg.evaluate('''() => { var o = R3.units[T.a]; return { face: !!o.hasFace, fc: o.fc.sp.visible, fcOn: o.fcOn, ax: o.lab.ax, ay: o.lab.ay, w: o.lab.w, h: o.lab.h, cx: o.lab.sp.center.x, cy: o.lab.sp.center.y, lab: o.lab.sp.visible, zoom: [R3.faceZoom, R3.nameZoom] }; }''')
    print('  이름표:', u); B.shot(pg, 'b1_units', 500)
    ok(u['face'] and not u['fc'] and not u['fcOn'] and u['lab'], '주장의 얼굴이 이름·병력 판에 붙어 있다(따로 뜨던 얼굴 딱지는 쓰지 않는다)')
    ok(abs(u['cx'] - u['ax']) < 1e-6 and abs(u['cy'] - u['ay']) < 1e-6 and u['ax'] > 0.5 and u['ay'] < 1, '판의 윗변 가운데가 부대 발밑에 온다(얼굴은 왼쪽 위로 걸친다) ax %.3f ay %.3f' % (u['ax'], u['ay']))
    w1 = u['w']
    pg.evaluate('() => { cam.z = 0.3; clampCam(); UI.dirty = true; requestDraw(); }'); pg.wait_for_timeout(500)
    u2 = pg.evaluate('''() => { var o = R3.units[T.a]; return { face: !!o.hasFace, w: o.lab.w, ax: o.lab.ax, ay: o.lab.ay }; }''')
    ok(not u2['face'] and u2['ax'] == 0.5 and u2['ay'] == 1 and u2['w'] < w1, '멀리서 보면 얼굴 없이 병력 판만(폭 %d → %d)' % (w1, u2['w']))
    pg.evaluate('() => { cam.z = 1.5; clampCam(); UI.dirty = true; requestDraw(); }'); pg.wait_for_timeout(400)
    # ---------- 4. 무장 카드: 얼굴을 누르면 겹쳐 뜬다 ----------
    pg.evaluate('() => { selectUnit(UMAP[T.a], true); }'); pg.wait_for_timeout(400)
    ok(pg.evaluate('document.querySelector("#sheet .sh-head .por").getAttribute("data-oid")') == str(pg.evaluate('UMAP[T.a].off[0]')), 'STATUS 창의 얼굴에 무장 번호가 실려 있다')
    tapsel(pg, '#sheet .sh-head .por'); pg.wait_for_timeout(300)
    c = pg.evaluate(CARD); print('  카드:', c); B.shot(pg, 'c1_card_unit', 200)
    ok(c and c['name'].startswith('하후돈') and c['bars'] == 5 and c['apt'] == 5 and c['scene'], '부대 창의 얼굴 → 하후돈의 카드(능력 다섯 · 병종 적성 다섯 · 큰 그림)')
    ok(c and '특기 · ' in c['sk'] and len(c['sk']) > 12 and '출진 중' in c['stats'] and '주장' in c['unit'] and '극병' in c['unit'] and '6,000' in c['unit'], '특기의 풀이와 있는 곳 · 이끄는 부대가 적혀 있다 [%s | %s]' % (c['sk'][:40], c['unit']))
    ok(c and c['inView'] and pg.evaluate('!!SHEET && !MODAL && UI.sel && UI.sel.id === T.a'), '카드는 화면 안에 뜨고, 아래의 부대 창은 그대로다')
    tapsel(pg, '#ocard [data-oc=x]')
    ok(pg.evaluate('!ocardOn() && !!SHEET && UI.sel && UI.sel.id === T.a'), '×로 닫으면 부대 창이 그대로 남는다')
    tapsel(pg, '#sheet .rows .row .por'); pg.wait_for_timeout(200)
    ok(pg.evaluate('ocardOn() && !MODAL'), '무장 줄의 얼굴 → 카드(무장 창이 따로 열리지 않는다)')
    pg.mouse.click(6, 6); pg.wait_for_timeout(250)
    ok(pg.evaluate('!ocardOn() && !MODAL && !!SHEET'), '바깥을 누르면 닫히고, 그 누름이 아래로 새지 않는다')
    tapsel(pg, '#sheet .rows .row .mid'); pg.wait_for_timeout(300)
    ok(head(pg).startswith('하후돈') and not pg.evaluate('ocardOn()'), '줄의 얼굴 밖을 누르면 예전처럼 무장 창이 열린다')
    tapsel(pg, '#modal .card .por'); pg.wait_for_timeout(200)
    ok(pg.evaluate('ocardOn() && !!MODAL'), '무장 창의 큰 그림을 눌러도 카드가 뜬다'); pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    ok(pg.evaluate('!ocardOn() && !!MODAL'), 'Esc 는 카드부터 닫는다(창은 남는다)'); pg.evaluate('closeDialog()')
    ok(pg.evaluate('(() => { ocardOpen(off(UMAP[T.d].off[0])); var r = appBack(); var a = [r, ocardOn()]; return a; })()') == [True, False], '휴대폰의 뒤로: 카드부터 닫는다')
    # 무장을 고르는 표에서: 얼굴 = 카드, 줄 = 고르기. 고른 것은 그대로 남는다
    pg.evaluate('() => { clearSel(); selectBase(G.bases[T.b]); }'); pg.wait_for_timeout(400)
    tapsel(pg, '#sheet .cmd[data-a=draft]'); pg.wait_for_timeout(400)
    rows = pg.evaluate('''() => Array.prototype.map.call(document.querySelectorAll('#modal .tr'), function (r) { var c2 = r.querySelector('.c-2'), sk = c2 ? c2.querySelector('.sk2') : null, id = +r.getAttribute('data-v'), o = off(id);
      return { n: o.n, sk: o.sk, ap: c2 ? c2.querySelectorAll('.ap5 > span').length : 0, apt: c2 ? Array.prototype.map.call(c2.querySelectorAll('.ap5 b'), function (b) { return b.textContent; }).join('') : '', real: o.apt, skTx: sk ? sk.textContent : '', gist: SKILL_TAG[o.sk] || '', h: r.offsetHeight, fit: r.scrollWidth <= r.clientWidth + 1, oid: r.querySelector('.por').getAttribute('data-oid') == id }; })''')
    print('  고르는 표:', len(rows), rows[0]); B.shot(pg, 'c2_pick', 200)
    ok(len(rows) >= 5 and all(r['ap'] == 5 and r['apt'] == r['real'] and r['oid'] and r['fit'] for r in rows), '무장을 고르는 표: 줄마다 병종 적성 다섯 칸(창 · 극 · 노 · 기 · 병기)이 그 무장의 것대로')
    ok(all((r['sk'] in r['skTx'] and r['gist'] in r['skTx'] and r['gist']) if r['sk'] else r['skTx'] == '' for r in rows) and any(r['sk'] for r in rows), '특기가 있으면 이름과 짧은 풀이가 같은 줄에 [%s]' % next(r['skTx'] for r in rows if r['sk']))
    tapsel(pg, '#modal .tr .c-n', 1); pg.wait_for_timeout(200)
    sel0 = pg.evaluate('Array.prototype.map.call(document.querySelectorAll("#modal .tr.sel"), function (r) { return r.getAttribute("data-v"); })')
    tapsel(pg, '#modal .tr .por', 3); pg.wait_for_timeout(250)
    c = pg.evaluate(CARD); B.shot(pg, 'c3_pick_card', 150)
    ok(len(sel0) == 1 and c and c['name'].startswith(rows[3]['n']) and pg.evaluate('!!MODAL'), '표에서 넷째 줄의 얼굴 → %s의 카드(표는 그대로 아래에)' % rows[3]['n'])
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    sel1 = pg.evaluate('Array.prototype.map.call(document.querySelectorAll("#modal .tr.sel"), function (r) { return r.getAttribute("data-v"); })')
    ok(sel1 == sel0 and pg.evaluate('!ocardOn() && !!MODAL'), '카드를 닫아도 고른 무장은 그대로 %s' % sel1)
    pg.evaluate('closeDialog()')
    # 목록의 특기 풀이(출진 창)
    tapsel(pg, '#sheet [data-a=tab][data-v=mil]'); tapsel(pg, '#sheet .cmd[data-a=deploy]'); pg.wait_for_timeout(500)
    g = pg.evaluate('''() => Array.prototype.map.call(document.querySelectorAll('#modal .row[data-a=pick]'), function (r) { var o = off(+r.getAttribute('data-v')), s = r.querySelector('.skg'); return [o.sk || '', s ? s.textContent : '', SKILL_TAG[o.sk] || '', r.querySelectorAll('.ap5 > span').length]; })''')
    ok(len(g) >= 3 and all(x[1] == x[2] and x[3] == 5 for x in g) and any(x[1] for x in g), '출진 창: 특기 이름 옆에 무엇을 하는 특기인지 한 줄 [%s — %s]' % next((x[0], x[1]) for x in g if x[1])); B.shot(pg, 'c4_deploy', 200)
    pg.evaluate('closeDialog()'); pg.evaluate(RESET); pg.wait_for_timeout(300)
    # ---------- 5. 전법의 새 이름 · 확률(숫자) · 군사의 추천 ----------
    pg.evaluate(TARGET); pg.wait_for_timeout(400)
    acts = pg.evaluate(ACTS); tacs = [a for a in acts if a['han']]
    print('  단추(숫자):', [(a['label'], a['han'], a['fx'], a['sub'], a['rec']) for a in acts])
    ok([a['label'] for a in tacs] == ['견인', '횡소', '일소'] and [a['han'] for a in tacs] == ['牽引', '橫掃', '一掃'], '극병 전법 셋: 새 이름과 한자 %s' % [(a['label'], a['han']) for a in tacs])
    ok(tacs[0]['fx'] == '끌어당김 · 반격 없음' and tacs[1]['fx'] == '양옆의 적도 벰' and tacs[2]['fx'] == '둘레의 적 모두', '단추마다 무엇을 하는 전법인지 적혀 있다')
    ok(all(re.search(r'^\d+% · 기력 \d+$', a['sub']) and a['gauge'] is None for a in tacs), '확률 표시 = 숫자: 예전처럼 %%로 [%s]' % tacs[0]['sub'])
    ok(sum(1 for a in acts if a['rec']) == 1 and all(a['fit'] for a in acts), '군사의 추천(薦)은 한 곳에만 — %s · 넘치는 단추 %s' % ([a['label'] for a in acts if a['rec']], [a['label'] for a in acts if not a['fit']]))
    say = pg.evaluate('(document.querySelector("#sheet .say.advn") || {}).textContent || ""')
    rec = [a['label'] for a in acts if a['rec']][0]
    ok((rec + ('이' if (ord(rec[-1]) - 0xAC00) % 28 else '가') + ' 가장 낫겠습니다.') in say, '군사의 말: ' + say[:60])
    # 군사가 없으면 추천도 없다
    adv0 = pg.evaluate('(() => { var a = G.factions[G.player].adv; G.factions[G.player].adv = -1; refreshSheet(); return a; })()')
    ok(pg.evaluate('document.querySelectorAll("#sheet .act .rec").length') == 0, '군사가 없으면 추천하지 않는다')
    pg.evaluate('(a) => { G.factions[G.player].adv = a; refreshSheet(); }', adv0)
    # ---------- 6. 확률을 말로(가늠) ----------
    pg.evaluate('() => { UI.pct = false; refreshSheet(); }'); pg.wait_for_timeout(200)
    acts = pg.evaluate(ACTS); tacs = [a for a in acts if a['han']]
    print('  단추(말):', [(a['label'], a['sub'], a['gauge']) for a in acts]); B.shot(pg, 'd1_words', 200)
    ok(all('%' not in a['sub'] for a in acts) and all(any(a['sub'].startswith(w) for w in WORDS) and a['gauge'] and a['gauge'][0] == 5 and not a['gauge'][2] for a in tacs), '말로: 전법 단추에 %% 가 없고 "높음" 같은 말과 눈금 다섯 칸 [%s %s]' % (tacs[0]['sub'], tacs[0]['gauge']))
    od = pg.evaluate('tacticOdds(UMAP[T.a], UMAP[T.d]).ok'); lv = 5 if od >= 85 else 4 if od >= 65 else 3 if od >= 45 else 2 if od >= 25 else 1
    ok(tacs[0]['sub'].startswith(WORDS[lv]) and tacs[0]['gauge'][1] == lv, '성공률 %d%% → "%s" · 눈금 %d칸' % (od, WORDS[lv], lv))
    eye = pg.evaluate('(() => { var e = oddsEye(); return [e.o.n, e.adv, e.fine, e.o.int]; })()')
    ok(eye[1] and eye[2], '가늠하는 이: 군사 %s(지력 %d) — 또렷이' % (eye[0], eye[3]))
    ch = [a for a in acts if a['label'] == '일기토'][0]; pl = [a for a in acts if a['label'] in ('화계', '교란', '위보')]
    ok('응할 확률' in ch['sub'] and '%' not in ch['sub'] and all(p['gauge'] for p in pl if not p['off']), '일기토 · 계략도 말로 [%s | %s]' % (ch['sub'], pl[0]['sub']))
    ok('적중률' not in pg.evaluate('(document.querySelector("#sheet .say.advn") || {}).textContent || ""'), '군사의 조언도 "적중률 N%" 대신 말로: ' + pg.evaluate('(document.querySelector("#sheet .say.advn small") || {}).textContent || ""'))
    # 전법 풀이
    tapsel(pg, '#sheet [data-a=tacinfo]'); pg.wait_for_timeout(300)
    ti = pg.evaluate('''() => { var m = $('modal'); return { odds: m.querySelector('.odds').textContent, w: m.querySelector('.odds').classList.contains('w'), eye: (m.querySelector('.note.eye') || {}).textContent || '', names: Array.prototype.map.call(m.querySelectorAll('.tac .tn b'), function (b) { return b.textContent; }),
      ids: Array.prototype.map.call(m.querySelectorAll('.tac'), function (b) { return b.getAttribute('data-t'); }), sum: m.querySelector('.sum:nth-of-type(2)') ? m.querySelector('.sum:nth-of-type(2)').textContent : m.querySelectorAll('.sum')[1].textContent, pull: m.querySelector('.tac[data-t=galkwi] .tl span').textContent, rows: Array.prototype.map.call(m.querySelectorAll('.tcmp tr[data-t]'), function (r) { return r.getAttribute('data-t'); }) }; }''')
    print('  전법 풀이(말):', ti); B.shot(pg, 'd2_tacinfo_words', 200)
    ok(ti['w'] and '%' not in ti['odds'] and '통할 가능성' in ti['odds'] and '대성공' in ti['odds'] and '가늠 — 군사' in ti['eye'] and '또렷이' in ti['eye'], '전법 풀이: 성공 · 대성공을 말로, 누가 가늠하는지 한 줄')
    ok(ti['names'] == ['견인 牽引', '횡소 橫掃', '일소 一掃'] and ti['ids'] == ['galkwi', 'hoengchi', 'seonpung'] and ti['rows'] == ['견인', '횡소', '일소'], '전법 풀이의 이름: %s' % ti['names'])
    ok('끌어당긴다' in ti['pull'] and '반격을 받지 않는다' in ti['pull'], '견인의 효과: ' + ti['pull'])
    ok('%' not in ti['sum'] and '통할 가능성' in ti['sum'] and ('▲' in ti['sum'] or '▼' in ti['sum'] or '–' in ti['sum']), '셈법도 숫자 대신 보탬 · 깎임의 화살표로: ' + ti['sum'][:70])
    pg.evaluate('() => { UI.pct = true; refreshDialog(); }'); pg.wait_for_timeout(150)
    o2 = pg.evaluate('(() => { var m = $("modal"); return [m.querySelector(".odds").textContent, m.querySelector(".odds").classList.contains("w"), !!m.querySelector(".note.eye"), m.querySelectorAll(".sum")[1].textContent]; })()')
    ok(o2[0].count('%') == 3 and not o2[1] and not o2[2] and ('성공률 %d%% = 적성' % od) in o2[3], '숫자로 바꾸면 예전 그대로(대성공 · 성공 · 실패 %% 셋): ' + o2[0])
    pg.evaluate('() => { UI.pct = false; closeDialog(); }')
    # 어림: 군사와 군주의 지력이 모두 낮으면 셋으로만 보인다
    pg.evaluate('''() => { var F = G.factions[G.player], L = off(F.lord), A = facAdv(G.player); window.__int = [L.int, A.int]; L.int = 55; A.int = 60; refreshSheet(); }'''); pg.wait_for_timeout(150)
    ac2 = pg.evaluate(ACTS); t2 = [a for a in ac2 if a['han']]
    eye2 = pg.evaluate('(() => { var e = oddsEye(); return [e.o.n, e.adv, e.fine, e.o.int]; })()')
    ok(not eye2[2] and all(any(a['sub'].startswith(w) for w in COARSE) and a['gauge'][2] for a in t2), '지력 60의 눈으로는 어림으로만: %s (눈금은 흐리게)' % t2[0]['sub'])
    tapsel(pg, '#sheet [data-a=tacinfo]'); pg.wait_for_timeout(250)
    e2 = pg.evaluate('(document.querySelector("#modal .note.eye") || {}).textContent || ""')
    ok('어림으로만' in e2 and '지력 70 이상의 군사' in e2, '전법 풀이에 까닭이 적혀 있다: ' + e2[:60]); B.shot(pg, 'd3_coarse', 150)
    pg.evaluate('() => { closeDialog(); var F = G.factions[G.player]; off(F.lord).int = window.__int[0]; facAdv(G.player).int = window.__int[1]; refreshSheet(); }')
    # 메뉴: 확률 표시
    pg.evaluate('() => { clearSel(); }'); tapsel(pg, '#btnMenu'); pg.wait_for_timeout(300)
    b0 = pg.evaluate('document.querySelector("#modal [data-a=pct]").textContent')
    tapsel(pg, '#modal [data-a=pct]'); b1 = pg.evaluate('document.querySelector("#modal [data-a=pct]").textContent'); s1 = pg.evaluate('[UI.pct, JSON.parse(localStorage.getItem("chunhado_opts")).pct]'); t1 = toast(pg)
    tapsel(pg, '#modal [data-a=pct]'); s2 = pg.evaluate('[UI.pct, JSON.parse(localStorage.getItem("chunhado_opts")).pct]')
    ok('말로 가늠' in b0 and '숫자' in b1 and s1 == [True, True] and s2 == [False, False] and '숫자' in t1, '메뉴 → 확률 표시: 말 ↔ 숫자, 기기에 남는다 [%s → %s]' % (b0, b1)); B.shot(pg, 'd4_menu', 150)
    pg.evaluate('closeDialog()')
    # 등용 표도 말로
    pg.evaluate('() => { selectBase(G.bases[T.b]); }'); pg.wait_for_timeout(300); tapsel(pg, '#sheet [data-a=tab][data-v=men]'); tapsel(pg, '#sheet .cmd[data-a=recruit]'); pg.wait_for_timeout(500)
    rt = pg.evaluate('Array.prototype.map.call(document.querySelectorAll("#modal .row .rt"), function (e) { return e.textContent; })')
    ok(len(rt) > 0 and all('%' not in x for x in rt) and any(any(w in x for w in WORDS) for x in rt), '등용 창: 응할 가능성도 말로 %s' % rt[:3]); B.shot(pg, 'd5_recruit', 150)
    pg.evaluate('closeDialog()'); pg.evaluate(RESET); pg.wait_for_timeout(300)
    # ---------- 7. 견인: 끌어당긴다 ----------
    def pull(roll, name):
        pg.evaluate(TARGET); pg.wait_for_timeout(250)
        fx = [a for a in pg.evaluate(ACTS) if a['label'] == '견인'][0]['fx']
        pg.evaluate('''([roll]) => { window.__rnd = rnd; var first = true; rnd = function () { if (first) { first = false; return roll; } return 0.5; }; window.__fl = [];
          var _ft = floatText; window.__ft = _ft; floatText = function (c, r, tx) { window.__fl.push(tx); return _ft.apply(null, arguments); }; }''', [roll])
        i = pg.evaluate('Array.prototype.findIndex.call(document.querySelectorAll("#sheet .act[data-a=act]"), function (e) { return e.querySelector("b").textContent.indexOf("견인") === 0; })')
        tapsel(pg, '#sheet .act[data-a=act]', i); pg.wait_for_timeout(620); pg.screenshot(path=os.path.join(B.SHOTS, name + '.png')); pg.wait_for_timeout(2600)
        return pg.evaluate('''() => { rnd = window.__rnd; floatText = window.__ft; var a = UMAP[T.a], d = UMAP[T.d], oa = R3.units[T.a], od = R3.units[T.d];
          return { fl: window.__fl, toast: $('toast').textContent, a: [a.c, a.r], d: d ? [d.c, d.r] : null, sa: [oa.c, oa.r], sd: od ? [od.c, od.r] : null, busy: UI.busy, anim: oa.anim, at: a.troops, dt: d ? d.troops : 0, done: a.done }; }'''), fx
    r, fx = pull(0.5, 'e1_pull'); f = T['f']; print('  견인:', r, fx)
    ok(fx == '끌어당김 · 반격 없음', '끌 수 있는 자리: 단추에 "끌어당김 · 반격 없음"')
    ok(r['a'] == [f[0] - 1, f[1]] and r['d'] == [f[0], f[1]], '성공: 나는 한 칸 뒤로, 적은 내가 섰던 자리로 %s %s' % (r['a'], r['d']))
    ok(r['sa'] == r['a'] and r['sd'] == r['d'] and not r['busy'] and not r['anim'], '지도의 부대 그림도 옮긴 자리에 선다(움직임이 끝났다)')
    ok(any(x == '牽引 견인!' for x in r['fl']) and '끌어당김' in r['fl'] and '견인 성공' in r['toast'] and '끌어당김' in r['toast'], '글씨: 牽引 견인! · 끌어당김 / 알림: ' + r['toast'])
    ok(r['at'] == 6000 and r['dt'] < 6000 and r['done'], '반격을 받지 않았다(내 병력 그대로) · 적 병력 %d' % r['dt'])
    # 뒤가 막힌 자리
    pg.evaluate(RESET); pg.evaluate('() => { placeUnit(UMAP[T.k], T.f[0] - 1, T.f[1]); syncScene(); requestDraw(); }'); pg.wait_for_timeout(300)
    r, fx = pull(0.5, 'e2_blocked'); print('  막힌 견인:', r, fx)
    ok(fx == '뒤가 막혀 끌지 못함 · 반격 없음', '뒤가 막힌 자리: 단추가 미리 알려 준다 [%s]' % fx)
    ok(r['a'] == [f[0], f[1]] and r['d'] == [f[0] + 1, f[1]] and '끌지 못함' in r['fl'] and '뒤가 막혀 끌지 못함' in r['toast'] and r['at'] == 6000, '끌지 못해도 피해는 주고 반격은 없다: ' + r['toast'])
    # 실패: 말로 볼 때는 "(가늠은 …)"
    pg.evaluate(RESET); pg.wait_for_timeout(300)
    r, fx = pull(0.999, 'e3_fail'); print('  실패:', r)
    ok(r['a'] == [f[0], f[1]] and r['d'] == [f[0] + 1, f[1]] and '견인 실패' in r['toast'] and '가늠은 ' in r['toast'] and '%' not in r['toast'] and r['at'] < 6000, '실패: 끌지 못하고 반격을 받는다 — 알림에 확률은 말로: ' + r['toast'])
    pg.evaluate('() => { UI.pct = true; }'); pg.evaluate(RESET); pg.wait_for_timeout(300)
    r, fx = pull(0.999, 'e4_fail_pct')
    ok(re.search(r'\(성공률 \d+%\)', r['toast']) is not None, '숫자로 볼 때는 예전처럼: ' + r['toast'])
    pg.evaluate('() => { UI.pct = false; }'); pg.evaluate(RESET)
    # ---------- 8. 도움말 ----------
    tapsel(pg, '#btnMenu'); tapsel(pg, '#modal [data-a=help]'); pg.wait_for_timeout(300)
    hp = pg.evaluate('document.querySelector("#modal .dlg-b").textContent')
    ok('무장 카드와 특기' in hp and '가늠 — 확률을 말로' in hp and '전법 열두 가지' in hp and '견인 牽引 끌어당김 · 반격 없음' in hp and '격퇴 擊退 한 칸 밀어냄' in hp and '유린 蹂躪' in hp, '도움말: 무장 카드 · 가늠 · 전법 열두 가지의 이름과 효과')
    ok(all(x not in hp for x in ['갈퀴', '돌출', '나선첨', '이단첨', '횡치', '선풍', '화시', '관시', '난사', '돌격', '돌파', '돌진']), '도움말에 옛 전법 이름이 남아 있지 않다')
    pg.evaluate('closeDialog()')
    # ---------- 9. 일기토 화면의 얼굴 ----------
    pg.evaluate(RESET); pg.wait_for_timeout(200)
    du = pg.evaluate('''() => { var a = UMAP[T.a], d = UMAP[T.d], la = uLeader(a), ld = uLeader(d); var h = duPor(la); var m = /data-oid="(\\d+)"/.exec(h); return [m ? +m[1] : -1, la.id, duPor({ n: 'x', por: la.por }).indexOf('data-oid') < 0]; }''')
    ok(du[0] == du[1] and du[2], '일기토 화면의 초상에도 무장 번호가 실린다(판 밖의 얼굴에는 없다)')
def small(pg):
    # ---------- 10. 작은 화면(360×640) ----------
    t = pg.evaluate('''() => { var m = document.querySelector('.t-menu').getBoundingClientRect(); return [m.top / innerHeight, Array.prototype.every.call(document.querySelectorAll('.t-menu button:not([hidden])'), function (b) { var r = b.getBoundingClientRect(); return r.bottom <= innerHeight && r.right <= innerWidth && b.scrollWidth <= b.clientWidth + 1; }), $('tVer').getBoundingClientRect().bottom <= innerHeight]; }''')
    ok(t[0] >= 0.70 and t[1] and t[2], '작은 화면: 제목의 단추가 아래 %.0f%% 안에 들어온다' % ((1 - t[0]) * 100)); B.shot(pg, 'f1_small_title', 200)
    B.start(pg, 0); pg.evaluate('() => { UI.pct = false; }'); pg.evaluate(SETUP); pg.wait_for_timeout(500)
    pg.evaluate(TARGET); pg.wait_for_timeout(300)
    acts = pg.evaluate(ACTS)
    ok(all(a['fit'] for a in acts) and len(acts) >= 8, '작은 화면: 대상 단추의 글씨(이름 · 한자 · 효과 · 가늠)가 넘치지 않는다 (%d개) 넘치는 것 %s' % (len(acts), [(a['label'], a['sub']) for a in acts if not a['fit']])); B.shot(pg, 'f2_small_acts', 200)
    tapsel(pg, '#sheet .sh-head .por'); pg.wait_for_timeout(300)
    c = pg.evaluate(CARD)
    sc = pg.evaluate('(() => { var b = document.querySelector("#ocard .oc-b"), o = document.querySelector("#ocard .oc").getBoundingClientRect(); return [o.top >= 0, o.bottom <= innerHeight + 1, b.scrollHeight >= b.clientHeight]; })()')
    ok(c and c['inView'] and all(sc), '작은 화면: 무장 카드가 화면 안에 들어오고, 길면 안에서 굴린다 %s' % sc); B.shot(pg, 'f3_small_card', 200)
    pg.evaluate('ocardClose()')
def more(pg):
    # ================= 11. 나중에 더한 것: 시설의 레벨 · 행군과 공격 명령 · 군단의 출격 · 충차 · 북소리 =================
    B.start(pg, 0); pg.evaluate('() => { UI.pct = false; }'); T = pg.evaluate(SETUP); pg.wait_for_timeout(500); f = T['f']
    # ---------- 11-1. 레벨이 없는 시설(공방 · 조폐 · 곡창) ----------
    fc = pg.evaluate("""() => { var b = G.bases[T.b], pr = null, i, j;
      for (i = 0; i < b.plots.length && !pr; i++) for (j = 0; j < b.plots.length && !pr; j++) if (i !== j && hdist(b.plots[i].c, b.plots[i].r, b.plots[j].c, b.plots[j].r) === 1) pr = [i, j];
      function F(t, lv) { return { t: t, lv: lv, done: true, prog: 0, need: 0, rate: 0, hp: FAC_HP }; }
      b.plots.forEach(function (q) { q.fac = null; }); b.plots[pr[0]].fac = F('mint', 1); b.plots[pr[1]].fac = F('mint', 1);
      var rest = b.plots.map(function (q, k) { return k; }).filter(function (k) { return k !== pr[0] && k !== pr[1]; });
      b.plots[rest[0]].fac = F('market', 2); b.plots[rest[1]].fac = F('granary', 1); b.plots[rest[2]].fac = F('workshop', 1); b.plots[rest[3]].fac = F('workshop', 1);
      clearSel(); selectBase(b, false, 'fac'); return { mint: pr[0], market: rest[0], ws: rest[2] }; }""")
    pg.wait_for_timeout(500)
    rows = pg.evaluate('Array.from(document.querySelectorAll("#sheet .row[data-a=plot]")).map(function (r) { return r.querySelector(".nm").textContent.replace(/^\\d+/, "") + " | " + r.querySelector(".ds").textContent + " | " + (r.querySelector(".rt") ? r.querySelector(".rt").textContent : ""); })')
    print('  시설 줄:', rows); B.shot(pg, 'g1_fac_rows', 200)
    ok(sum(1 for r in rows if r.startswith('조폐 | 옆 시장의 수입 +50% | ')) == 2 and any(r.startswith('곡창 | 옆 농장의 수입 +50%') for r in rows) and sum(1 for r in rows if r.startswith('공방 | 충차 생산 | ')) == 2, '조폐 · 곡창 · 공방의 줄에는 레벨이 없다')
    ok(any(r.startswith('시장 Lv2 | 금 +') for r in rows) and not any('합병 가능' in r for r in rows if not r.startswith('시장')), '시장은 전처럼 Lv2 — 붙어 있는 조폐 둘에도 "합병 가능"이 뜨지 않는다')
    pg.evaluate('([i]) => flowFacility(G.bases[T.b], i)', [fc['mint']]); pg.wait_for_timeout(400)
    d = pg.evaluate('(() => { var m = $("modal"); return [m.querySelector(".dlg-h h2").textContent, !!m.querySelector("[data-a=merge]"), !!m.querySelector("[data-a=demo]"), m.querySelector(".note.nolv") ? m.querySelector(".note.nolv").textContent : ""]; })()')
    ok('Lv' not in d[0] and '조폐' in d[0] and not d[1] and d[2] and '조폐는 레벨이 없는 시설입니다' in d[3], '조폐의 창: 레벨도 흡수합병 단추도 없다 [%s | %s]' % (d[0], d[3])); B.shot(pg, 'g2_mint', 150)
    pg.evaluate('closeDialog()'); pg.evaluate('([i]) => flowFacility(G.bases[T.b], i)', [fc['ws']]); pg.wait_for_timeout(300)
    d = pg.evaluate('(() => { var m = $("modal"); return [m.querySelector(".dlg-h h2").textContent, !!m.querySelector("[data-a=merge]"), (m.querySelector(".fcn") || {}).textContent || ""]; })()')
    ok('Lv' not in d[0] and not d[1] and '하나면 충분합니다' in d[2], '공방의 창: 레벨이 없고, 둘이면 하나는 쓸모없다고 알린다 [%s]' % d[2])
    pg.evaluate('closeDialog()'); pg.evaluate('([i]) => flowFacility(G.bases[T.b], i)', [fc['market']]); pg.wait_for_timeout(300)
    d = pg.evaluate('(() => { var m = $("modal"); return [m.querySelector(".dlg-h h2").textContent, !!m.querySelector("[data-a=merge]")]; })()')
    ok('시장 Lv2' in d[0] and d[1], '시장의 창은 전처럼 레벨과 흡수합병 단추가 있다'); pg.evaluate('closeDialog()')
    # ---------- 11-2. 행군: 먼 땅을 누르면 곧바로 ----------
    pg.evaluate(RESET); pg.wait_for_timeout(300)
    pg.evaluate('() => { selectUnit(UMAP[T.a], true); }'); pg.wait_for_timeout(300)
    u0 = pg.evaluate("""() => { var u = UMAP[T.a], rc = UI.rc, best = null;
      for (var r = u.r - 9; r <= u.r + 9 && !best; r++) for (var c = u.c - 10; c <= u.c - 5 && !best; c++) { if (!inMap(c, r)) continue; var k = K(c, r); if (MC[0][k] < 99 && !UAT[k] && BAT[k] === undefined && !PAT[k] && !rc.stop[k] && hdist(u.c, u.r, c, r) >= 6 && marchPath(u, k)) best = [c, r]; }
      return { far: best, at: [u.c, u.r], btn: !!document.querySelector('#sheet [data-a=pickmarch]'), note: (document.querySelector('#sheet .note') || {}).textContent || '', undoOff: document.querySelector('#sheet [data-a=undo]').classList.contains('off') }; }""")
    ok(not u0['btn'] and '먼 곳을 누르면 그곳으로 행군' in u0['note'] and u0['undoOff'], '부대 창에 [행군] 단추가 없다 — 안내: ' + u0['note'])
    pg.evaluate('([c, r]) => onTap(c, r)', u0['far']); pg.wait_for_timeout(1700)
    m = pg.evaluate("""() => { var u = UMAP[T.a]; return { at: [u.c, u.r], dest: u.dest, toast: $('toast').textContent, sel: !!selUnit(), undoOff: document.querySelector('#sheet [data-a=undo]').classList.contains('off'), cancel: (document.querySelector('#sheet [data-a=unmarch]') || {}).textContent || '', note: Array.from(document.querySelectorAll('#sheet .note')).map(function (n) { return n.textContent; }).join(' / '), path: UI.mpath ? UI.mpath.path.length : 0, busy: UI.busy }; }""")
    print('  행군:', m); B.shot(pg, 'h1_march', 200)
    ok(m['at'] != u0['at'] and m['dest'] == pg.evaluate('([c, r]) => K(c, r)', u0['far']) and m['sel'] and not m['busy'], '먼 땅을 누름 → 곧바로 그쪽으로 움직였다 %s → %s' % (u0['at'], m['at']))
    ok('방면 행군 — 약' in m['toast'] and '이동 취소' in m['toast'] and '행군 취소' in m['cancel'] and '방면 행군 중' in m['note'] and m['path'] > 0 and not m['undoOff'], '알림에 걸리는 날수와 물리는 법, 부대 창에 [행군 취소] · 갈 길 표시: ' + m['toast'])
    tapsel(pg, '#sheet [data-a=undo]'); pg.wait_for_timeout(300)
    m2 = pg.evaluate("() => { var u = UMAP[T.a]; return { at: [u.c, u.r], dest: u.dest, toast: $('toast').textContent, cancel: !!document.querySelector('#sheet [data-a=unmarch]'), path: !!UI.mpath }; }")
    ok(m2['at'] == u0['at'] and m2['dest'] == -1 and '명령도 거두었습니다' in m2['toast'] and not m2['cancel'] and not m2['path'], '[이동 취소] → 제자리로 돌아오고 행군 명령도 거둔다: ' + m2['toast'])
    # ---------- 11-3. 공격 명령: 닿지 않는 적을 누르면 다가가고, 턴을 마칠 때 알아서 친다 ----------
    e0 = pg.evaluate("""() => { var a = UMAP[T.a], d = UMAP[T.d]; placeUnit(d, T.f[0] + 3, T.f[1]); syncScene(); selectUnit(a, true); requestDraw(); return { dist: hdist(a.c, a.r, d.c, d.r), tr: d.troops, name: uName(d) }; }""")
    pg.wait_for_timeout(300); pg.evaluate('() => { var d = UMAP[T.d]; onTap(d.c, d.r); }'); pg.wait_for_timeout(1700)
    am = pg.evaluate("""() => { var a = UMAP[T.a], d = UMAP[T.d]; return { aim: a.aim, dist: hdist(a.c, a.r, d.c, d.r), tr: d.troops, done: a.done, toast: $('toast').textContent, cancel: (document.querySelector('#sheet [data-a=unmarch]') || {}).textContent || '', note: (document.querySelector('#sheet .note.aimn') || {}).textContent || '', target: !!UI.target }; }""")
    print('  공격 명령:', am); B.shot(pg, 'h2_aim', 200)
    ok(e0['dist'] == 3 and am['aim'] and am['aim']['k'] == 'unit' and am['dist'] == 1 and am['tr'] == e0['tr'] and not am['done'] and not am['target'], '닿지 않는 적을 누름 → 공격 명령: 옆까지 다가간다(아직 치지는 않는다) 거리 %d → %d' % (e0['dist'], am['dist']))
    ok((e0['name'] + ' 공격 명령') in am['toast'] and '명령 취소' in am['cancel'] and (e0['name'] + ' 공격 명령') in am['note'] and '닿으면 알아서 칩니다' in am['note'], '알림과 부대 창: ' + am['note'])
    # 닿는 적을 누르면 전처럼 내가 고른다
    pg.evaluate('() => { var d = UMAP[T.d]; onTap(d.c, d.r); }'); pg.wait_for_timeout(400)
    ok(pg.evaluate('!!UI.target && document.querySelectorAll("#sheet .act[data-a=act]").length >= 5 && !!UMAP[T.a].aim'), '닿는 적을 누르면 전처럼 수를 직접 고르는 단추들이 뜬다(명령은 남아 있다)')
    pg.evaluate('() => { UI.target = null; clearSel(); }')
    # 턴을 마친다: 맨 먼저 공격 명령을 받은 부대가 친다(다른 세력은 건너뛰어 본다)
    pg.evaluate('() => { window.__sk = true; doEndTurn(); }'); pg.wait_for_timeout(600)
    if pg.evaluate('!UI.play'): pg.evaluate('doEndTurn()'); pg.wait_for_timeout(600)      # "명령 대기 N부대 — 한 번 더"
    seen = False
    for i in range(120):
        st = pg.evaluate("() => ({ play: !!UI.play, cap: $('plMsg').textContent, tr: UMAP[T.d] ? UMAP[T.d].troops : 0, modal: !!MODAL })")
        if st['play'] and st['tr'] < e0['tr'] and not seen: seen = True; B.shot(pg, 'h3_aim_play', 0); pg.evaluate('playSkip()')
        if not st['play']: break
        pg.wait_for_timeout(500)
    pg.wait_for_timeout(800); pg.evaluate('() => { if (MODAL) closeDialog(); talkHide(); }')
    at = pg.evaluate("""() => { var acts = REPORT.filter(function (e) { return e.t === 'act' && e.res && e.res.aid === T.a; }); return { n: acts.length, kind: acts.length ? acts[0].res.kind + (acts[0].res.tacId ? ':' + acts[0].res.tacId : '') : '', tid: acts.length ? acts[0].res.tid === T.d : false, tr: UMAP[T.d] ? UMAP[T.d].troops : 0, aim: UMAP[T.a] ? !!UMAP[T.a].aim : null, turn: G.turn }; }""")
    print('  턴 종료 뒤:', at, '재생에서 봄', seen)
    ok(at['tr'] < e0['tr'] and seen and at['turn'] == 2, '턴을 마치자 그 부대가 알아서 쳤다(적 병력 %d → %d) — 지난 열흘의 재생에도 나온다' % (e0['tr'], at['tr']))
    # 명령 취소
    if pg.evaluate('!!UMAP[T.a] && !!UMAP[T.a].aim'):
        pg.evaluate('() => { selectUnit(UMAP[T.a], true); }'); pg.wait_for_timeout(300); tapsel(pg, '#sheet [data-a=unmarch]')
        ok(pg.evaluate('!UMAP[T.a].aim && UMAP[T.a].dest === -1'), '[명령 취소] → 공격 명령을 거둔다')
    # 먼 적의 성: 공격 명령 / 협정을 맺은 세력: 내릴 수 없다
    bz = pg.evaluate("""() => { var a = UMAP[T.a]; if (!a) return null; a.done = false; a.mp = uMaxMp(a); selectUnit(a, true); var bs = G.bases.filter(function (b) { return b.owner >= 0 && b.owner !== G.player && !pactOn(G.player, b.owner) && marchPath(a, K(b.c, b.r)); }).sort(function (x, y) { return hdist(a.c, a.r, x.c, x.r) - hdist(a.c, a.r, y.c, y.r); });
      var b = bs[0]; onTap(b.c, b.r); return { id: b.id, n: b.n, f: b.owner }; }""")
    pg.wait_for_timeout(1700)
    if bz:
        ab = pg.evaluate("() => { var a = UMAP[T.a]; return { aim: a.aim, toast: $('toast').textContent, note: (document.querySelector('#sheet .note.aimn') || {}).textContent || '' }; }")
        ok(ab['aim'] and ab['aim']['k'] == 'base' and ab['aim']['id'] == bz['id'] and (bz['n'] + ' 공격 명령') in ab['toast'], '먼 적의 성(%s)을 누름 → 공격 명령: %s' % (bz['n'], ab['toast'][:50]))
        pg.evaluate("() => { var a = UMAP[T.a]; aimClear(a); a.done = false; a.mp = uMaxMp(a); a.ox = -1; }")
        pt = pg.evaluate("([id, f]) => { dipSign(G.player, f, 'truce'); var a = UMAP[T.a], b = G.bases[id]; selectUnit(a, true); onTap(b.c, b.r); var r = [!!a.aim, $('toast').textContent]; delete G.dip.pact[dipKey(G.player, f)]; return r; }", [bz['id'], bz['f']])
        ok(not pt[0] and '정전 중 — 칠 수 없습니다' in pt[1], '정전 중인 세력의 성에는 공격 명령을 내릴 수 없다: ' + pt[1])
    # 먼 내 성: 그 성의 창 + [이 성으로 행군]
    ow = pg.evaluate("""() => { var a = UMAP[T.a], b = G.bases[T.b]; a.done = false; a.mp = uMaxMp(a); a.ox = -1; a.dest = -1; selectUnit(a, true); var far = !UI.rc.stop[K(b.c, b.r)]; onTap(b.c, b.r); var bt = document.querySelector('#sheet [data-a=marchhere]'); return { far: far, sheet: UI.sel && UI.sel.kind === 'base' && UI.sel.id === b.id, btn: bt ? bt.textContent : '', n: b.n }; }""")
    if ow['far']:
        ok(ow['sheet'] and (pg.evaluate('uName(UMAP[T.a])') + ' — 이 성으로 행군') in ow['btn'] and '약 ' in ow['btn'], '부대를 고른 채 먼 내 성을 누름 → 그 성의 창 + [%s]' % ow['btn']); B.shot(pg, 'h4_marchhere', 200)
        tapsel(pg, '#sheet [data-a=marchhere]'); pg.wait_for_timeout(1700)
        mh = pg.evaluate("() => { var a = UMAP[T.a], b = G.bases[T.b]; return [a ? a.dest === K(b.c, b.r) : 'entered', !!selUnit(), $('toast').textContent]; }")
        ok(mh[0] in (True, 'entered') and '방면 행군' in mh[2], '[이 성으로 행군] → 그 성으로 행군을 시작한다: ' + mh[2][:40])
    # ---------- 11-4. 군단: 출격 금지 · 군단의 거점에서도 수송 ----------
    pg.evaluate('() => { if (MODAL) closeDialog(); clearSel(); G.units.slice().forEach(function (u) { if (u.f === G.player) removeUnit(u); }); syncScene(); }')
    cid = pg.evaluate("() => { var b = G.bases[T.b]; G.factions[G.player].ap = 250; var r = corpsCreate([b.id]); if (!r.ok) return r.msg; showCorps(r.corps.id); return r.corps.id; }"); pg.wait_for_timeout(400)
    c1 = pg.evaluate("() => { var e = document.querySelector('#modal .cph'); return e ? [e.querySelector('p').textContent, !!e.querySelector('[data-a=hold]'), e.querySelector('.note').textContent] : null; }")
    ok(isinstance(cid, int) and c1 and '출격 허용' in c1[0] and c1[1] and '나가서' in c1[2] or (c1 and '부대를 내어 막습니다' in c1[2]), '군단 창(군비 방침): 출격 허용 + [금지로] 단추 %s' % c1); B.shot(pg, 'i1_corps', 150)
    tapsel(pg, '#modal [data-a=hold]'); pg.wait_for_timeout(250)
    c2 = pg.evaluate("([id]) => { var e = document.querySelector('#modal .cph'), cp = corpsById(id); return [e.querySelector('p').textContent, cp.hold, corpsSortie(cp), e.querySelector('.note').textContent]; }", [cid])
    ok('출격 금지' in c2[0] and c2[1] is True and c2[2] is False and '나가 싸우지 않습니다' in c2[3], '[금지로] → 출격 금지: ' + c2[3])
    tapsel(pg, '#modal .opt[data-a=dir][data-v=dev]'); pg.wait_for_timeout(300)
    c3 = pg.evaluate("([id]) => { var e = document.querySelector('#modal .cph'), cp = corpsById(id), o = document.querySelector('#modal .opt[data-v=dev]'); return [e.querySelector('p').textContent, !!e.querySelector('[data-a=hold]'), corpsSortie(cp), e.querySelector('.note').textContent, o.textContent]; }", [cid])
    ok('출격 금지' in c3[0] and not c3[1] and c3[2] is False and '내정 방침에서는 성 밖으로 나가 싸우지 않습니다' in c3[3] and '출격 안 함' in c3[4], '내정 방침: 늘 출격 금지(고르는 단추가 없다) — ' + c3[3][:40]); B.shot(pg, 'i2_corps_dev', 150)
    pg.evaluate('closeDialog()'); pg.evaluate('() => { clearSel(); selectBase(G.bases[T.b]); }'); pg.wait_for_timeout(400)
    cb = pg.evaluate("() => Array.from(document.querySelectorAll('#sheet .cmd')).map(function (e) { return e.getAttribute('data-a'); })")
    ok(cb == ['corps', 'direct', 'trans'], '군단에 맡긴 거점의 창: [군단] · [직할로] · [수송] %s' % cb); B.shot(pg, 'i3_corps_base', 150)
    tapsel(pg, '#sheet .cmd[data-a=trans]'); pg.wait_for_timeout(500)
    tr = pg.evaluate("([id]) => { var cp = corpsById(id), h = MODAL ? document.querySelector('#modal .dlg-h h2').textContent : ''; return [h, cp.lead, Array.from(document.querySelectorAll('#modal [data-oid]')).map(function (e) { return +e.getAttribute('data-oid'); })]; }", [cid])
    ok('수송' in tr[0] and tr[1] not in tr[2], '군단의 거점에서 수송 창이 열린다(군단장은 보내지 않는다) [%s]' % tr[0]); B.shot(pg, 'i4_corps_trans', 150)
    pg.evaluate('closeDialog()')
    # ---------- 11-5. 충차 · 북소리 ----------
    rm = pg.evaluate("() => [UNIT_TYPES.ram.mp, UNIT_TYPES.ram.siege, ROAD_COST.join(','), JSON.stringify(CUES.deploy.s), Object.keys(SFX_DATA).length, SFX_DATA.drum.length, SFX_DATA.drums.length]")
    ok(rm[0] == 10 and rm[1] == 8 and rm[2] == '2,2,2', '충차: 이동력 10 · 공성 8 · 길의 칸값 2')
    ok(rm[3] == '[["drums",0.85,0.02],["horn",0.42,0.01,0.9]]' and rm[4] == 29, '출진의 소리: 북(둥 — 둥 — 둥둥둥) + 마지막 센 박에 뿔나팔 · 효과음은 29개 그대로')
B.run(steps, 390, 844, 2)
B.run(small, 360, 640, 2)
B.run(more, 390, 844, 2)
# 앱(PWA)판: 아이콘을 바꿨으니 서비스 워커의 껍데기 번호가 올라가 있어야 한다
sw = open(os.path.join(B.ROOT, '..', 'dist', 'pwa', 'sw.js'), encoding='utf-8').read()
ok("var SHELL = 'chunhado-shell-2'" in sw, '앱판의 서비스 워커: 껍데기 저장소 번호 2(아이콘의 낙관이 天下圖 로 바뀌었다)')
errs = [e for e in B.errors if 'GPU stall' not in e and 'GL Driver' not in e and 'ERR_FILE_NOT_FOUND' not in e and 'willReadFrequently' not in e]
print('console errors:', errs[:6])
print('FAILS %d' % len(fails), fails)
sys.exit(1 if fails or errs else 0)
