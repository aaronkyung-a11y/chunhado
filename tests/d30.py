# v0.17 — 아티팩트에 올리는 판(dist/artifact/: index.html + data/scenes.json)을 실제처럼 http 로 내어 확인한다.
#   무장의 큰 그림(SCENES)을 페이지 밖으로 떼어 냈다(아티팩트의 페이지 하나는 16MiB 까지) — 받아 오는지, 받기 전 · 받지 못했을 때 작은 초상으로 버티는지.
#   python3 tests/d30.py          (먼저 python3 tools/build.py --split)
import sys, os, json, threading, functools, http.server, socketserver
os.environ['CDN'] = 'ok'                                            # three.js 는 CDN 주소를 가로채 로컬 파일로 답한다(browser.py)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import tapsel
ART = os.path.join(B.ROOT, '..', 'dist', 'artifact')
B.SHOTS = os.path.join(B.ROOT, 'shots32'); os.makedirs(B.SHOTS, exist_ok=True)
fails = []
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), functools.partial(Q, directory=ART)); srv.daemon_threads = True
threading.Thread(target=srv.serve_forever, daemon=True).start()
B.URL = 'http://127.0.0.1:%d/index.html' % srv.server_address[1]
html = open(os.path.join(ART, 'index.html'), encoding='utf-8').read(); sj = json.load(open(os.path.join(ART, 'data', 'scenes.json'), encoding='utf-8'))
print('0. 파일')
ok(len(html.encode('utf-8')) < 16 * 1024 * 1024, 'index.html %.2fMiB — 16MiB 아래' % (len(html.encode('utf-8')) / 1048576))
ok('var SCENES={};' in html and 'var SCENES={"' not in html and "fetch('data/scenes.json')" in html, '큰 그림은 페이지에 없고 data/scenes.json 을 받아 오게 되어 있다')
ok(len(sj) == 265 and all(isinstance(v, str) and len(v) > 1000 for v in sj.values()), 'data/scenes.json: 큰 그림 %d장(%.2fMiB)' % (len(sj), os.path.getsize(os.path.join(ART, 'data', 'scenes.json')) / 1048576))
SHOW = '''(n) => { closeDialog(); showOfficer(G.officers.filter(function (o) { return o.n === n; })[0]); var c = document.querySelector('#modal .card'); return { sc: !!c.querySelector('.por.sc'), lg: !!c.querySelector('.por.lg'), bg: (c.querySelector('.por') || {}).style ? c.querySelector('.por').style.backgroundImage.slice(0, 12) : '' }; }'''
IMG = '''(key) => new Promise(function (res) { var u = sceneUrl(key); if (!u) return res(0); var a = new Image(); a.onload = function () { res(a.naturalWidth); }; a.onerror = function () { res(-1); }; a.src = u; })'''
def steps(pg):
    print('1. 받아 온다')
    pg.wait_for_function('window.SCENES_READY === true', timeout=30000)
    st = pg.evaluate('({ n: Object.keys(SCENES).length, need: SCENARIO.officers.filter(function (o) { return !/^g[mcf]\\\\d/.test(o.por) && !SCENES[o.por]; }).map(function (o) { return o.n; }), ver: GAME_VERSION })')
    ok(st['n'] >= 265 and st['need'] == [] and st['ver'] == B.VER,      # v0.24: 그림 묶음(공용 초상 120장)의 장면이 먼저 와 있으면 더 많다
       '페이지가 뜬 뒤 큰 그림 %d장을 받아 왔다(제 초상이 있는 무장은 모두 큰 그림이 있다) %s' % (st['n'], st['need'][:3]))
    pg.evaluate('([f, s]) => { localStorage.clear(); newGame(f, s); saveGame(); }', [10, 1]); pg.reload(); pg.wait_for_function('window.R3 && R3.ready', timeout=60000)
    pg.wait_for_function('window.SCENES_READY === true', timeout=30000); pg.wait_for_timeout(400)
    tapsel(pg, '#tCont'); pg.wait_for_timeout(1300)
    if pg.evaluate('!!MODAL'): pg.evaluate('closeDialog()')
    pg.evaluate('talkHide()')
    d = pg.evaluate(SHOW, '오국태'); w = pg.evaluate(IMG, 'wuguotai')
    ok(d['sc'] and not d['lg'] and 'blob:' in d['bg'] and w >= 300, '무장 창에 큰 그림이 나온다(오국태, 가로 %dpx)' % w); B.shot(pg, 'w1_scene', 400)
    w2 = pg.evaluate(IMG, 'guanyu'); ok(w2 >= 300, '있던 무장의 큰 그림도 그대로(관우, %dpx)' % w2)
    print('2. 받기 전에는 작은 초상')
    d = pg.evaluate('(n) => { var keep = SCENES; SCENES = {}; SCENE_URL = {}; var r = (%s)(n); SCENES = keep; SCENE_URL = {}; return r; }' % SHOW, '오국태')
    ok(d['lg'] and not d['sc'] and 'blob:' in d['bg'], '큰 그림이 아직 없으면 작은 초상을 크게 보여 준다'); B.shot(pg, 'w2_fallback', 300)
    d = pg.evaluate(SHOW, '오국태'); ok(d['sc'], '받은 뒤에는 다시 큰 그림')
    pg.evaluate('closeDialog()')
    print('3. 받지 못해도 판은 돈다')
    pg.route('**/data/scenes.json', lambda r: r.abort())
    n_err = len(B.errors)
    pg.reload(); pg.wait_for_function('window.R3 && R3.ready', timeout=60000); pg.wait_for_timeout(1200)
    tapsel(pg, '#tCont'); pg.wait_for_timeout(1300)
    if pg.evaluate('!!MODAL'): pg.evaluate('closeDialog()')
    pg.evaluate('talkHide()')
    st = pg.evaluate('({ ready: window.SCENES_READY, n: Object.keys(SCENES).length, turn: G.turn, por: !!POR_URL["wuguotai"] })')
    d = pg.evaluate(SHOW, '오국태')
    ok(st['ready'] is not True and st['n'] <= 373 and st['por'] and d['lg'] and not d['sc'],      # v0.24: 그림 묶음의 장면 120장은 따로 온다 · v0.25: 개별 초상 묶음의 253장도(120 + 253 = 373) — 막힌 것은 scenes.json 의 265장
       '큰 그림을 받지 못해도 작은 초상으로 판이 돈다 %s' % st); B.shot(pg, 'w3_blocked', 300)
    pg.evaluate('closeDialog()')
    bad = [e for e in B.errors[n_err:] if 'scenes.json' not in e and 'Failed to load resource' not in e and 'net::ERR_FAILED' not in e]
    ok(not bad, '그때 나는 오류는 그 파일을 받지 못했다는 것뿐 %s' % bad[:3])
    del B.errors[n_err:]
    pg.unroute('**/data/scenes.json')
B.run(steps, 390, 844, 2)
errs = [e for e in B.errors if 'GPU stall' not in e and 'GL Driver' not in e and 'ERR_FILE_NOT_FOUND' not in e and 'willReadFrequently' not in e and 'bgm/' not in e and '404' not in e]
print('console errors:', errs[:6])
print('FAILS %d' % len(fails), fails)
sys.exit(1 if fails or errs else 0)
