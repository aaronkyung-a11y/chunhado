# v0.24 — 그림 묶음(공용 초상 120장)과 딸: 화면.
#   아티팩트에 올리는 판(dist/artifact/)은 공용 초상을 data/por-pool-<지문>.json · data/scn-pool-<지문>.json 으로 떼어 페이지가 뜬 뒤에 받아 온다(페이지 하나는 16MiB 까지).
#     0) 파일  1) 받아 온다  2) 늦게 와도(처음에 못 받아도) 다시 받아 그 자리에서 그림이 채워진다 — 그동안에도 판은 돈다  3) 딸: 초상 · 열전 · 아버지의 창 · 목소리
#   한 파일짜리 판(dist/offline.html)에는 묶음이 들어 있다 — 뜨자마자 쓸 수 있다.
#   python3 tests/d40.py          (먼저 python3 tools/build.py --split · --embed)   찍은 그림은 tests/shots40/h_*.png
import sys, os, json, glob, threading, functools, http.server, socketserver
os.environ['CDN'] = 'ok'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import tapsel
ART = os.path.join(B.ROOT, '..', 'dist', 'artifact')
B.SHOTS = os.path.join(B.ROOT, 'shots40'); os.makedirs(B.SHOTS, exist_ok=True)
fails = []
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), functools.partial(Q, directory=ART)); srv.daemon_threads = True
threading.Thread(target=srv.serve_forever, daemon=True).start()
OFFLINE = B.URL
B.URL = 'http://127.0.0.1:%d/index.html' % srv.server_address[1]
html = open(os.path.join(ART, 'index.html'), encoding='utf-8').read()
pf = sorted(glob.glob(os.path.join(ART, 'data', 'por-pool-*.json'))); sf = sorted(glob.glob(os.path.join(ART, 'data', 'scn-pool-*.json')))
print('0. 파일')
ok(len(html.encode('utf-8')) < 16 * 1024 * 1024, 'index.html %.2fMiB — 16MiB 아래' % (len(html.encode('utf-8')) / 1048576))
ok(len(pf) == 1 and len(sf) == 1, '그림 묶음 파일이 하나씩: %s · %s' % (os.path.basename(pf[0]) if pf else '-', os.path.basename(sf[0]) if sf else '-'))
pj = json.load(open(pf[0], encoding='utf-8')); sj = json.load(open(sf[0], encoding='utf-8'))
ok(len(pj) == 120 and sorted(pj) == sorted(sj) and all(v.startswith('UklGR') for v in pj.values()), '흉상 120장(%.2fMiB) · 장면 120장(%.2fMiB)' % (os.path.getsize(pf[0]) / 1048576, os.path.getsize(sf[0]) / 1048576))
NP = len(glob.glob(os.path.join(ART, 'data', 'por-*-*.json'))) + len(glob.glob(os.path.join(ART, 'data', 'scn-*-*.json')))      # v0.25: 묶음이 둘(공용 pool · 개별 p253) — 파일은 묶음마다 둘
ok('"gm101":"UklGR' not in html and ('"data/' + os.path.basename(pf[0]) + '"') in html and ('"data/' + os.path.basename(sf[0]) + '"') in html and ('window.PACKS_WANT = %d' % NP) in html, '묶음은 페이지에 없고 data/ 의 파일 %d개를 받아 오게 되어 있다' % NP)
p2 = sorted(glob.glob(os.path.join(ART, 'data', 'por-p253-*.json'))); s2 = sorted(glob.glob(os.path.join(ART, 'data', 'scn-p253-*.json')))
if p2 or s2:
    j2 = json.load(open(p2[0], encoding='utf-8')); k2 = json.load(open(s2[0], encoding='utf-8'))
    ok(len(p2) == 1 and len(s2) == 1 and len(j2) == 253 and sorted(j2) == sorted(k2) and '"zhuling":"UklGR' not in html and ('"data/' + os.path.basename(p2[0]) + '"') in html, '개별 초상 묶음: 흉상 253장(%.2fMiB) · 장면 253장(%.2fMiB) — 페이지에는 없다' % (os.path.getsize(p2[0]) / 1048576, os.path.getsize(s2[0]) / 1048576))
IMG = '''([kind, key]) => new Promise(function (res) { var u = kind === 'p' ? POR_URL[key] : sceneUrl(key); if (!u) return res(0); var a = new Image(); a.onload = function () { res(a.naturalWidth); }; a.onerror = function () { res(-1); }; a.src = u; })'''
CARD = '''(n) => { var o = offByName(n); ocardOpen(o); var e = document.querySelector('#ocard'), p = e.querySelector('.por'); var r = { por: o.por, bg: (p && p.getAttribute('style')) || '', sc: !!e.querySelector('.por.sc'), tx: e.textContent.slice(0, 1200) }; return r; }'''
def boot(pg, f=0):
    pg.evaluate('([f]) => { localStorage.clear(); newGame(f, 3); saveGame(); }', [f]); pg.reload(); pg.wait_for_function('window.R3 && R3.ready', timeout=60000); pg.wait_for_timeout(500)
    tapsel(pg, '#tCont'); pg.wait_for_timeout(1300)
    if pg.evaluate('!!MODAL'): pg.evaluate('closeDialog()')
    pg.evaluate('talkHide(); UI.talk = false;')
def steps(pg):
    print('1. 받아 온다')
    pg.wait_for_function('window.PACKS_READY === %d' % NP, timeout=30000)
    st = pg.evaluate('({ ver: GAME_VERSION, n: Object.keys(PORTRAITS).filter(function (k) { return /^g[mf][1-5][0-9][0-9]$/.test(k); }).length, url: !!POR_URL.gm101 && !!POR_URL.gf510, sc: !!SCENES.gm101 && !!SCENES.gf510, fail: window.PACKS_FAIL || 0 })')
    ok(st == {'ver': B.VER, 'n': 120, 'url': True, 'sc': True, 'fail': 0}, '페이지가 뜬 뒤 공용 초상 120장을 받아 왔다 %s' % st)
    w = [pg.evaluate(IMG, ['p', 'gm101']), pg.evaluate(IMG, ['p', 'gf510']), pg.evaluate(IMG, ['s', 'gm305']), pg.evaluate(IMG, ['s', 'gf204'])]
    ok(w[0] == 256 and w[1] == 256 and w[2] >= 300 and w[3] >= 300, '그림이 풀린다 — 흉상 %d · %dpx, 장면 %d · %dpx' % tuple(w))
    boot(pg)
    pg.wait_for_function('window.PACKS_READY === %d' % NP, timeout=30000)
    d = pg.evaluate(CARD, '주령')
    ok((d['por'].startswith('gm1') or d['por'] == 'zhuling') and d['sc'] and 'blob:' in d['bg'], '묶음의 초상을 쓰는 무장(주령 — 0.24 에서는 공용 초상, 0.25 부터는 제 초상: %s)의 카드에 큰 그림이 나온다' % d['por']); B.shot(pg, 'h_roster', 300)
    pg.evaluate('ocardClose()')

    print('2. 늦게 와도')
    n_err = len(B.errors)
    pg.route('**/data/por-*-*.json', lambda r: r.abort()); pg.route('**/data/scn-*-*.json', lambda r: r.abort())
    pg.reload(); pg.wait_for_function('window.R3 && R3.ready', timeout=60000); pg.wait_for_timeout(600)
    tapsel(pg, '#tCont'); pg.wait_for_timeout(1300)
    if pg.evaluate('!!MODAL'): pg.evaluate('closeDialog()')
    pg.evaluate('talkHide(); UI.talk = false;')
    s0 = pg.evaluate('({ ready: window.PACKS_READY, url: !!POR_URL.gm101, own: !!POR_URL.caocao, turn: G.turn })')
    d0 = pg.evaluate('''() => { showOfficer(offByName('주령')); var p = document.querySelector('#modal .card .por'); return { bg: (p && p.getAttribute('style')) || '', lg: !!document.querySelector('#modal .card .por.lg') }; }''')
    ok(s0['ready'] == 0 and not s0['url'] and s0['own'] and 'blob:' not in d0['bg'], '묶음을 아직 못 받았으면 그 초상 자리는 빈 종이다(제 초상이 있는 무장은 그대로 나온다) %s' % s0)
    t0 = pg.evaluate('''() => { var t = G.turn; closeDialog(); endTurn(); showOfficer(offByName('주령')); return [t, G.turn]; }''')
    ok(t0[1] == t0[0] + 1, '그동안에도 판은 돈다(턴 %d → %d)' % (t0[0], t0[1]))
    pg.unroute('**/data/por-*-*.json'); pg.unroute('**/data/scn-*-*.json')
    pg.wait_for_function('window.PACKS_READY === %d' % NP, timeout=40000); pg.wait_for_timeout(400)
    d1 = pg.evaluate('''() => { var p = document.querySelector('#modal .card .por'); return { bg: (p && p.getAttribute('style')) || '', sc: !!document.querySelector('#modal .card .por.sc'), url: !!POR_URL.gm101 }; }''')
    ok(d1['url'] and 'blob:' in d1['bg'] and d1['sc'], '다시 받아 오면 열려 있던 창의 그림이 그 자리에서 채워진다')
    pg.evaluate('closeDialog()')
    bad = [e for e in B.errors[n_err:] if 'pool-' not in e and 'p253-' not in e and 'Failed to load resource' not in e and 'net::ERR_FAILED' not in e]
    ok(not bad, '그때 나는 오류는 그 파일을 받지 못했다는 것뿐 %s' % bad[:3])
    del B.errors[n_err:]

    print('3. 딸')
    k = pg.evaluate('''() => { var p0 = BIRTH.p, l0 = BIRTH.lord; BIRTH.p = 100; BIRTH.lord = 100; G.year++; var n0 = G.officers.length; birthTick(); BIRTH.p = p0; BIRTH.lord = l0;
      var kids = G.officers.slice(n0), g = kids.filter(function (x) { return x.sex === 'f' && offByName(x.dad).f === G.player; })[0], b = kids.filter(function (x) { return x.sex !== 'f' && offByName(x.dad).f === G.player; })[0];
      return { n: kids.length, girls: kids.filter(function (x) { return x.sex === 'f'; }).length, g: g.n, gd: g.dad, gp: g.por, gc: POOL.name[porCat(g)], b: b.n, bp: b.por, voice: [voiceKind(g), voiceKind(b)], miss: kids.filter(function (x) { return !POR_URL[x.por]; }).length }; }''')
    print('    ', k)
    ok(k['n'] > 100 and 0.4 < k['girls'] / k['n'] < 0.6 and k['miss'] == 0, '아이 %d명 가운데 딸 %d명 — 모두 초상이 있다' % (k['n'], k['girls']))
    d = pg.evaluate(CARD, k['g'])
    ok(d['por'] == k['gp'] and d['por'].startswith('gf') and d['sc'] and 'blob:' in d['bg'] and ('의 딸.' in d['tx']) and ('아버지 ' + k['gd']) in d['tx'] and '1세' in d['tx'], '딸의 카드: 여성 공용 초상(%s — %s이 으뜸) · 열전에 "…의 딸" · 아버지 · 나이' % (d['por'], k['gc']))
    B.shot(pg, 'h_girl', 400)
    d2 = pg.evaluate(CARD, k['gd'])
    ok(('자식 ' in d2['tx']) and k['g'] in d2['tx'], '아버지(%s)의 카드에 자식으로 적힌다' % k['gd'])
    d3 = pg.evaluate(CARD, k['b'])
    ok(d3['por'].startswith('gm') and 'blob:' in d3['bg'] and '의 아들.' in d3['tx'] and k['voice'] == ['lady', k['voice'][1]] and k['voice'][1] != 'lady', '아들은 남성 공용 초상 · 딸은 여성의 목소리')
    B.shot(pg, 'h_boy', 300)
    pg.evaluate('ocardClose()')
B.run(steps, 393, 852, 2)
errs = [e for e in B.errors if 'ReadPixels' not in e and 'ERR_FILE' not in e and 'GPU stall' not in e and 'AudioContext' not in e and 'bgm/' not in e and '404' not in e]      # 404: 이 폴더에는 음악(bgm/)이 없다(d30 과 같다)
print('오류 기록:', errs[:6])
ok(not errs, '오류 · 경고 기록이 없다(%d건)' % len(errs))
print('4. 한 파일짜리 판')
B.URL = OFFLINE; n_e = len(B.errors)
def steps2(pg):
    st = pg.evaluate('({ packs: typeof window.PACKS_WANT, n: Object.keys(PORTRAITS).filter(function (k) { return /^g[mf][1-5][0-9][0-9]$/.test(k); }).length, url: !!POR_URL.gm101 && !!POR_URL.gf510, sc: !!SCENES.gf101, pack: typeof PACK_pool === "undefined" || PACK_pool === null, own: (function () { var k = SCENARIO.officers.filter(function (o) { return o.n === "주령"; })[0].por; return !!POR_URL[k] && !/^g[mf][0-9]/.test(k); })() })')
    ok(st == {'packs': 'undefined', 'n': 120, 'url': True, 'sc': True, 'pack': True, 'own': True}, '오프라인 판에는 묶음이 들어 있어 뜨자마자 쓴다(공용 120장 · 주령의 제 초상) %s' % st)
B.run(steps2, 393, 852, 2)
print('\nd40: %d fail' % len(fails))
for f in fails: print('  ✗', f)
sys.exit(1 if fails else 0)
