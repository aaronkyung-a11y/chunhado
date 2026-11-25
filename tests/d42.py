# v0.25 — 화면으로 확인: 메뉴(저장 · 불러오기는 크게, 나머지는 작게 · '이 판' 없음) · 가늠의 말(높음 · 보통 · 낮음) · 개별 초상.
#   요청(11-25 20:42): "메뉴에 저장과 불러오기 버튼이 크고 나머지는 좀 작게해도 되겠어. 수명 켜짐 밑에 이 판 이라는 말은 필요없어" / "높은 듯 반반인 듯 이런 말은 높음 보통 낮음 이런 식으로 표기"
#   python3 tests/d42.py          찍은 그림은 tests/shots42/
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
B.SHOTS = os.path.join(B.ROOT, 'shots42')
os.makedirs(B.SHOTS, exist_ok=True)
fails = []
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)
MENU = '''() => { showMenu();
  var q = function (e) { var r = e.getBoundingClientRect(), b = e.querySelector("b"); return { a: e.dataset.a, w: Math.round(r.width), h: Math.round(r.height), f: parseFloat(getComputedStyle(b).fontSize), cut: e.scrollWidth > e.clientWidth + 1 || b.scrollWidth > e.clientWidth + 1, t: e.innerText.replace(/\\n/g, "|") }; };
  var top = Array.prototype.map.call(document.querySelectorAll("#modal .mnu-top .cmd"), q), rest = Array.prototype.map.call(document.querySelectorAll("#modal .mnu-rest .cmd"), q), d = document.querySelector("#modal .dlg").getBoundingClientRect();
  return { top: top, rest: rest, dlg: [Math.round(d.top), Math.round(d.bottom)], vh: window.innerHeight, sw: document.documentElement.scrollWidth <= window.innerWidth, txt: document.querySelector("#modal .dlg").innerText }; }'''
def menu(pg, tag):
    m = pg.evaluate(MENU); pg.wait_for_timeout(300)
    top, rest = m['top'], m['rest']
    ok([t['a'] for t in top] == ['save', 'load'] and len(rest) == 11, '%s: 위 줄에 저장 · 불러오기, 아래에 나머지 %d개' % (tag, len(rest)))
    ok(all(t['h'] >= 60 and t['f'] >= 19 for t in top) and all(r['h'] < min(t['h'] for t in top) and r['f'] < 15 for r in rest), '%s: 저장 · 불러오기가 크다(%d × %dpx · 글씨 %.1fpx) — 나머지는 작다(%d × %dpx · 글씨 %.1fpx)' % (tag, top[0]['w'], top[0]['h'], top[0]['f'], rest[0]['w'], rest[0]['h'], rest[0]['f']))
    ok(all(r['h'] >= 44 for r in rest) and not any(r['cut'] for r in rest + top), '%s: 작은 단추도 누를 만하고(높이 44px 이상) 글씨가 잘리지 않는다 %s' % (tag, [r['a'] for r in rest if r['cut'] or r['h'] < 44]))
    ok(m['dlg'][1] <= m['vh'] and m['dlg'][0] >= 0 and m['sw'], '%s: 메뉴가 화면 안에 다 들어온다(위 %d · 아래 %d / 화면 %d)' % (tag, m['dlg'][0], m['dlg'][1], m['vh']))
    life = [r for r in rest if r['a'] == 'life'][0]
    ok(life['t'] in ('수명 켜짐', '수명 꺼짐') and '이 판' not in m['txt'], "%s: 수명 단추에 '이 판' 이 없다 — %s" % (tag, life['t']))
    B.shot(pg, 'm_' + tag, 250)
    pg.evaluate('closeDialog()')
def steps(pg):
    B.start(pg, 0); pg.wait_for_timeout(600)
    if pg.evaluate('!!MODAL'): pg.evaluate('closeDialog()')
    pg.evaluate('talkHide()')
    print('1. 메뉴')
    menu(pg, 'phone')
    pg.evaluate('showMenu()'); pg.wait_for_timeout(200)
    pg.locator('#modal [data-a=life]').first.tap(); pg.wait_for_timeout(400)
    t = pg.evaluate('({ t: document.querySelector("#modal [data-a=life]").innerText.replace(/\\n/g, "|"), life: G.life })')
    ok(t['t'] == '수명 꺼짐' and t['life'] == 0, '수명 단추를 누르면 바뀐다 — %s' % t['t'])
    pg.locator('#modal [data-a=life]').first.tap(); pg.wait_for_timeout(400); pg.evaluate('closeDialog()')
    print('2. 가늠의 말')
    w = pg.evaluate('''() => { UI.pct = false; var L = off(G.factions[G.player].lord), A = facAdv(G.player), li = L.int, ai = A ? A.int : 0;
      L.int = 90; if (A) A.int = 90; var fine = [5, 30, 50, 70, 90].map(function (p) { return oddsWord(p); }), gf = pcG(50);
      L.int = 50; if (A) A.int = 50; var coarse = [5, 30, 50, 70, 90].map(function (p) { return oddsWord(p); }), gc = pcG(50), eye = eyeNote();
      L.int = li; if (A) A.int = ai;
      return { W: ODDS_W, WC: ODDS_WC, fine: fine, coarse: coarse, gf: gf, gc: gc, eye: eye }; }''')
    ok(w['fine'] == ['매우 낮음', '낮음', '보통', '높음', '매우 높음'], '또렷이 볼 때: %s' % ' · '.join(w['fine']))
    ok(w['coarse'] == ['낮음', '낮음', '보통', '높음', '높음'] and 'dim' in w['gc'] and 'dim' not in w['gf'] and '어림으로만' in w['eye'], "어림으로 볼 때: %s — '듯' 이 없고, 어림인 것은 흐린 눈금과 한 줄이 알린다" % ' · '.join(w['coarse']))
    ok(not any('듯' in x or '반반' in x for x in w['W'] + w['WC']), "가늠의 말에 '듯' · '반반' 이 없다")
    hl = pg.evaluate('''() => { var o = offByName("주령"), fc = heirForecast(G.player, o), keep = UI.pct, out = { n: fc.n, p: fc.p };
      UI.pct = false; out.word = heirLine(fc, off(G.factions[G.player].lord), ""); UI.pct = true; out.num = heirLine(fc, off(G.factions[G.player].lord), ""); UI.pct = keep; return out; }''')
    ok(hl['n'] > 0 and '%' not in hl['word'] and '동요할 가능성' in hl['word'] and ('%d%%로 동요' % hl['p']) in hl['num'], '후계의 가늠도 확률 표시를 따른다 — 말: …%s / 숫자: …%s' % (hl['word'][-22:], hl['num'][-14:]))
    pg.evaluate('showHelp()'); pg.wait_for_timeout(300)
    h = pg.evaluate('document.querySelector("#modal .dlg").textContent')        # 도움말은 접힌 칸(details)이라 보이는 글(innerText)에는 없다
    ok('높음 · 보통 · 낮음' in h and '높은 듯' not in h and '반반인 듯' not in h and '매우 높음 · 높음 · 보통 · 낮음 · 매우 낮음' in h, '도움말도 같은 말로 적는다')
    pg.evaluate('closeDialog()')
    print('3. 개별 초상')
    p = pg.evaluate('''() => { var O = G.officers, gen = O.filter(function (o) { return !o.kid && /^g[mcf][0-9]/.test(o.por || ""); }).length, use = {}, miss = 0;
      O.forEach(function (o) { if (!o.kid) { use[o.por] = (use[o.por] || 0) + 1; if (!POR_URL[o.por]) miss++; } });
      var mx = 0, k; for (k in use) if (use[k] > mx) mx = use[k];
      return { n: O.length, gen: gen, kinds: Object.keys(use).length, max: mx, miss: miss, ex: ['동탁', '손견', '사환', '관구검', '곽유지'].map(function (n) { var o = offByName(n); return n + ':' + o.por + ':' + (POR_URL[o.por] ? 1 : 0); }) }; }''')
    ok(p['gen'] == 0 and p['miss'] == 0 and p['max'] == 1 and p['kinds'] == p['n'], '명부 %d명이 저마다 제 초상을 쓴다(공용 초상 0명 · 그림이 없는 사람 0명) — %s' % (p['n'], ' '.join(p['ex'])))
    pg.evaluate('showOfficer(offByName("동탁"))'); pg.wait_for_timeout(700)
    c = pg.evaluate('''() => { var e = document.querySelector('#modal .card .por'); return { bg: (e && e.getAttribute('style')) || '', nm: document.querySelector('#modal .dlg-h').innerText }; }''')
    ok('blob:' in c['bg'] and '동탁' in c['nm'], '동탁의 카드에 그림이 나온다'); B.shot(pg, 'p_dongzhuo', 300)
    pg.evaluate('closeDialog()')
B.run(steps, 390, 844, 2)
def small(pg):
    B.start(pg, 0); pg.wait_for_timeout(600)
    if pg.evaluate('!!MODAL'): pg.evaluate('closeDialog()')
    pg.evaluate('talkHide()')
    print('4. 작은 화면(360 × 640)')
    menu(pg, 'small')
B.run(small, 360, 640, 2)
errs = [e for e in B.errors if 'GPU stall' not in e and 'GL Driver' not in e and 'ERR_FILE_NOT_FOUND' not in e and 'willReadFrequently' not in e]
print('console errors:', errs[:6])
print('FAILS %d' % len(fails), fails)
sys.exit(1 if fails or errs else 0)
