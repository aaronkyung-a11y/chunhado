# v0.17 — 화면에서 확인: 늘어난 무장(425명) · 여성 무장의 초상과 목소리 · 옛 저장(301명)을 불러오면 덧붙는다 · 도움말
#   python3 tests/d29.py          찍은 그림은 tests/shots31/
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import taphex, tapsel
B.SHOTS = os.path.join(B.ROOT, 'shots31')
os.makedirs(B.SHOTS, exist_ok=True)
fails = []
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)
def head(pg): return pg.evaluate('MODAL ? document.querySelector("#modal .dlg-h h2").textContent : ""')
def reload(pg):
    pg.reload(); pg.wait_for_function('window.R3 && R3.ready', timeout=60000); pg.wait_for_timeout(600)
def fresh(pg, fac, seed):
    pg.evaluate('([f, s]) => { localStorage.clear(); newGame(f, s); saveGame(); }', [fac, seed]); reload(pg)
    tapsel(pg, '#tCont'); pg.wait_for_timeout(1300)
    if pg.evaluate('!!MODAL'): pg.evaluate('closeDialog()')
    pg.evaluate('talkHide()'); pg.wait_for_timeout(200)
IMGOK = '''(key) => new Promise(function (res) { var u = POR_URL[key], s = sceneUrl(key); if (!u || !s) return res([!!u, !!s, 0, 0]); var a = new Image(), b = new Image(), n = 0, out = [true, true, 0, 0];
  function done() { if (++n === 2) res(out); } a.onload = function () { out[2] = a.naturalWidth; done(); }; a.onerror = function () { out[0] = false; done(); }; b.onload = function () { out[3] = b.naturalWidth; done(); }; b.onerror = function () { out[1] = false; done(); }; a.src = u; b.src = s; })'''
def steps(pg):
    fresh(pg, 10, 1)                                                # 손책
    info = pg.evaluate('''(() => { var W = SCENARIO.women, b = facCities(G.player)[0]; window.BID = b.id;
      return { ver: GAME_VERSION, n: G.officers.length, w: W.length, fac: facName(G.player), city: b.n, mine: facOfficers(G.player).filter(function (o) { return o.id >= 301; }).map(function (o) { return o.n; }),
        noPor: G.officers.filter(function (o) { return !POR_URL[o.por]; }).map(function (o) { return o.n; }), wGen: G.officers.filter(function (o) { return W.indexOf(o.n) >= 0 && /^g[mcf]\\d/.test(o.por); }).map(function (o) { return o.n; }) }; })()''')
    print('     ', info)
    # ================= 1. 명부 =================
    print('1. 명부')
    ok(info['ver'] == 'v0.18.1', '판 번호 v0.18.1 [%s]' % info['ver'])
    ok(info['n'] == 425 and info['w'] == 42, '무장 %d명 · 여성 %d명' % (info['n'], info['w']))
    ok(info['noPor'] == [] and info['wGen'] == [], '초상이 없는 무장이 없고, 여성은 모두 제 초상을 쓴다 %s %s' % (info['noPor'][:4], info['wGen'][:4]))
    ok(sorted(info['mine']) == sorted(['서곤', '오국태']), '손책군(%s)에 새 무장 — %s' % (info['city'], info['mine']))
    keys = pg.evaluate('G.officers.filter(function (o) { return SCENARIO.women.indexOf(o.n) >= 0; }).map(function (o) { return [o.n, o.por]; })')
    bad = []
    for n, k in keys:
        r = pg.evaluate(IMGOK, k)
        if not (r[0] and r[1] and r[2] >= 200 and r[3] >= 300): bad.append((n, k, r))
    ok(len(keys) == 42 and not bad, '여성 42명의 작은 초상 · 큰 그림이 모두 그림으로 열린다 %s' % bad[:3])
    # ================= 2. 무장 창 =================
    print('2. 무장 창')
    for nm, shot in (('오국태', 'z2_wuguotai'), ('마운록', 'z2_mayunlu'), ('손상향', 'z2_sunshangxiang'), ('황월영', 'z2_huangyueying')):
        pg.evaluate('(n) => { closeDialog(); showOfficer(G.officers.filter(function (o) { return o.n === n; })[0]); }', nm); pg.wait_for_timeout(700)
        d = pg.evaluate('''(() => { var m = $('modal'), im = m.querySelector('.card img, .card .scene, .card [style*="background-image"]'), b = m.querySelector('.dlg-b');
          var r = m.querySelector('.dlg').getBoundingClientRect(); return { head: m.querySelector('.dlg-h h2').textContent, text: b.innerText, img: !!im, fit: [Math.round(r.left) >= 0, Math.round(r.right) <= innerWidth] }; })()''')
        ok(d['head'].startswith(nm) and d['img'] and all(d['fit']), '%s: 무장 창에 큰 그림 — %s' % (nm, d['head'].strip()))
        if nm == '오국태': ok('혈연' in d['text'] and '명성' in d['text'], '오국태: 손책과의 인연(혈연) · 특기 명성')
        if nm == '마운록': ok('기장' in d['text'], '마운록: 특기 기장')
        if nm == '황월영': ok('발명' in d['text'], '황월영: 특기 발명')
        B.shot(pg, shot, 300)
    pg.evaluate('closeDialog()')
    # 거점 창의 무장 표
    pg.evaluate('(() => { closeDialog(); talkHide(); gotoBase(G.bases[BID], "men"); })()'); pg.wait_for_timeout(500)
    sheet = pg.evaluate('$("sheet").innerText'); B.shot(pg, 'z2_sheet', 300)
    ok('오국태' in sheet and '서곤' in sheet, '거점 창의 [인재] 탭에 새 무장이 보인다')
    # ================= 3. 목소리 =================
    print('3. 목소리')
    vk = pg.evaluate('''['손상향', '오국태', '서모', '마운록', '변씨', '초선', '조진', '서곤', '올돌골'].map(function (n) { return n + ':' + voiceKind(G.officers.filter(function (o) { return o.n === n; })[0]); })''')
    ok(all(x.endswith(':lady') for x in vk[:6]) and not any(x.endswith(':lady') for x in vk[6:]), '여성 무장은 여장의 목소리 — %s' % vk)
    # ================= 4. 재야 · 등장 연도 =================
    print('4. 재야')
    fr = pg.evaluate('''(() => { var b = G.bases[BID], a = hiddenOfficers(b).map(function (o) { return o.n; }); G.year = 199; var c = hiddenOfficers(b).map(function (o) { return o.n; }); G.year = 194; return [a, c]; })()''')
    ok('교현' in fr[0] and '소교' not in fr[0] and '소교' in fr[1] and '대교' in fr[1], '여강: 194년에는 교현, 199년에는 대교 · 소교도 탐색으로 찾을 수 있다 — %s' % fr[1])
    # ================= 5. 옛 저장 =================
    print('5. 옛 저장(301명)')
    pg.evaluate('''(() => { var g = JSON.parse(serialize()); g.officers.length = 301; g.factions.forEach(function (f) { if (f.adv >= 301) f.adv = -1; }); localStorage.setItem(SAVE_KEY, JSON.stringify(g)); localStorage.removeItem(SAVE_KEY + '_meta'); saveGame = function () { return false; }; })()''')      # 화면을 떠날 때의 자동 저장이 이 저장을 덮어쓰지 않게
    n0 = pg.evaluate('JSON.parse(localStorage.getItem(SAVE_KEY)).officers.length')
    reload(pg); tapsel(pg, '#tCont'); pg.wait_for_timeout(1500)
    st = pg.evaluate('''(() => ({ n: G.officers.length, mine: facOfficers(G.player).filter(function (o) { return o.id >= 301; }).map(function (o) { return o.n + ':' + G.bases[o.loc].n + ':' + o.loy; }),
      log: G.log.filter(function (x) { return /무장이 늘었습니다/.test(x.t); }).map(function (x) { return x.t; }), modal: !!MODAL, errs: 0 }))()''')
    print('     ', st)
    ok(n0 == 301 and st['n'] == 425, '301명짜리 저장을 이어 하면 %d명이 된다' % st['n'])
    ok(len(st['mine']) == 2 and all(':여강:' in x for x in st['mine']) and len(st['log']) == 1 and '124명' in st['log'][0] and '우리 세력에 2명' in st['log'][0], '우리 세력의 새 무장은 제 도시에 · 기록에 한 줄 — %s' % (st['log'][0] if st['log'] else ''))
    if st['modal']: pg.evaluate('closeDialog()')
    pg.evaluate('talkHide()')
    pg.evaluate('(() => { saveGame(); })()'); reload(pg); tapsel(pg, '#tCont'); pg.wait_for_timeout(1300)
    ok(pg.evaluate('G.officers.length') == 425 and pg.evaluate('G.log.filter(function (x) { return /무장이 늘었습니다/.test(x.t); }).length') == 1, '다시 저장했다 불러도 더 늘지 않는다')
    if pg.evaluate('!!MODAL'): pg.evaluate('closeDialog()')
    # 한 턴을 넘겨 본다(새 무장이 있는 채로 굴러간다)
    pg.evaluate('(() => { talkHide(); UI.pspeed = 3; window._t0 = G.turn; })()')
    tapsel(pg, '#btnEnd'); pg.wait_for_timeout(300)
    if pg.evaluate('!UI.play && !MODAL'): tapsel(pg, '#btnEnd')
    if pg.evaluate('!!MODAL && !UI.play'):
        b = pg.locator('#modal [data-a=go], #modal [data-a=ok], #modal [data-a=yes]')
        if b.count(): b.first.tap()
    try: pg.wait_for_function('G.turn > window._t0 && !UI.play && !UI.busy', timeout=240000)
    except Exception: print('      (재생이 끝나지 않음)')
    ok(pg.evaluate('G.turn > window._t0 && G.officers.length === 425'), '턴을 넘겨도 그대로 굴러간다')
    if pg.evaluate('!!MODAL'): pg.evaluate('closeDialog()')
    # ================= 6. 도움말 · 작은 화면 =================
    print('6. 도움말 · 작은 화면')
    t = pg.evaluate('HELP_HTML.replace(/<[^>]+>/g, " ")')
    ok('무장 명부' in t and '425명' in t and '여성 42명' in t and '등장 연도' in t, '도움말: 무장 명부')
    pg.set_viewport_size({'width': 360, 'height': 640}); pg.wait_for_timeout(400)
    pg.evaluate('(() => { closeDialog(); showOfficer(G.officers.filter(function (o) { return o.n === "변씨"; })[0]); })()'); pg.wait_for_timeout(600)
    fit = pg.evaluate('''(() => { var r = document.querySelector('#modal .dlg').getBoundingClientRect(); return [Math.round(r.left) >= 0, Math.round(r.right) <= innerWidth, Math.round(r.bottom) <= innerHeight]; })()''')
    ok(fit[0] and fit[1], '작은 화면(360×640): 무장 창이 넘치지 않는다 %s' % fit); B.shot(pg, 'z6_small', 300)
    pg.evaluate('closeDialog()')
B.run(steps, 390, 844, 2)
errs = [e for e in B.errors if 'GPU stall' not in e and 'GL Driver' not in e and 'ERR_FILE_NOT_FOUND' not in e and 'willReadFrequently' not in e]
print('console errors:', errs[:6])
print('FAILS %d' % len(fails), fails)
sys.exit(1 if fails or errs else 0)
