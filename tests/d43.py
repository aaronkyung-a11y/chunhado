# v0.26 — 가까이 당겼을 때의 바탕 그림(4배 조각): 아티팩트에 올리는 판(dist/artifact/)을 http 로 띄워 확인한다.
#   요청: (11-25 21:30) "맵을 확대하면 맵이 깨져보이거나 뭉개지는데 …" · (23:41) "b 로해"(4배로 키운 그림을 조각으로 — 가까이 당긴 곳만 받아 온다)
#   python3 tests/d43.py          찍은 그림은 tests/shots43/
import sys, os, json, glob, threading, functools, http.server, socketserver, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
import numpy as np
from PIL import Image, ImageFilter
B.SHOTS = os.path.join(B.ROOT, 'shots43')
os.makedirs(B.SHOTS, exist_ok=True)
ART = os.path.join(B.ROOT, '..', 'dist', 'artifact'); OFFLINE = B.URL
fails = []
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), functools.partial(Q, directory=ART)); srv.daemon_threads = True
threading.Thread(target=srv.serve_forever, daemon=True).start()
B.URL = 'http://127.0.0.1:%d/index.html' % srv.server_address[1]
html = open(os.path.join(ART, 'index.html'), encoding='utf-8').read()
tdir = sorted(glob.glob(os.path.join(ART, 'data', 't4-*')))
print('0. 파일')
ok(len(tdir) == 1 and len(glob.glob(os.path.join(tdir[0], '*.webp'))) == 64, '조각 64장이 data/%s/ 에 있다(%.2fMiB)' % (os.path.basename(tdir[0]) if tdir else '-', sum(os.path.getsize(f) for f in glob.glob(os.path.join(tdir[0], '*.webp'))) / 1048576 if tdir else 0))
ok(('window.HITILE = {"base": "data/%s/"' % os.path.basename(tdir[0])) in html, '페이지가 조각이 있는 곳을 안다')
reqs = []
STATE = '''() => ({ on: HT.on, z: +cam.z.toFixed(2), slots: HT.slot.map(function (s) { return s.key + ":" + s.k.toFixed(2); }), k: R3.tmat.uniforms.hiK.value.toArray(), n: Object.keys(HT.tex).length, loaded: HT.loaded, bad: Object.keys(HT.bad).length, def: !!(R3.tmat.defines && R3.tmat.defines.HITILE) })'''
def shot_arr(pg):
    pg.wait_for_timeout(350)
    im = Image.open(io.BytesIO(pg.screenshot(clip={'x': 0, 'y': 170, 'width': 390, 'height': 430}))).convert('L')
    return np.asarray(im, dtype=np.float32)
def grad(a):
    gx = np.zeros_like(a); gy = np.zeros_like(a); gx[:, :-1] = np.abs(np.diff(a, axis=1)); gy[:-1, :] = np.abs(np.diff(a, axis=0)); return np.hypot(gx, gy)
def edge(a_on, a_off):
    """선이 얼마나 또렷한가: 두 화면이 서로 다른 자리(= 바탕 그림이 바뀐 자리 — 성 · 칸 줄 · 글씨는 두 화면에서 같다)에서 밝기 기울기의 평균을 견준다"""
    m = np.asarray(Image.fromarray(((np.abs(a_on - a_off) > 12) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9))) > 0
    return float(grad(a_on)[m].mean()), float(grad(a_off)[m].mean()), float(m.mean())
def low(a): return np.asarray(Image.fromarray(a.astype(np.uint8)).resize((48, 54), Image.BOX), dtype=np.float32)
def boot(pg):
    B.start(pg, 0); pg.wait_for_timeout(600)
    if pg.evaluate('!!MODAL'): pg.evaluate('closeDialog()')
    pg.evaluate('talkHide(); UI.talk = false; clearSel();')
def steps(pg):
    pg.on('request', lambda r: reqs.append(r.url) if '/t4-' in r.url else None)
    boot(pg)
    print('1. 멀리서는 받지 않는다')
    pg.wait_for_function('HT.busy === 0', timeout=30000)
    pg.evaluate('jumpTo(126, 96, 0.5)'); pg.wait_for_timeout(900)
    l0 = pg.evaluate('HT.loaded'); pg.wait_for_timeout(900)
    s = pg.evaluate(STATE); print('     ', s)
    ok(s['on'] and s['def'] and s['z'] < 0.8 and s['loaded'] == l0 and s['k'] == [0, 0, 0, 0], '멀리서 볼 때(확대 %.2f)는 조각을 받지도 겹치지도 않는다' % s['z'])
    print('2. 가까이 당기면 그 자리의 조각을 받아 겹친다')
    pg.evaluate('jumpTo(126, 96, 2.3)')
    pg.wait_for_function('HT.slot.filter(function (s) { return s.key && s.k >= 1; }).length >= 1 && HT.busy === 0', timeout=30000); pg.wait_for_timeout(600)
    s = pg.evaluate(STATE); print('     ', s, len(reqs))
    nf = len([x for x in s['slots'] if not x.startswith(':')])
    ok(1 <= nf <= 4 and max(s['k']) == 1 and s['bad'] == 0, '가장 가까이(확대 %.2f) 당기니 그 자리의 조각 %d장을 겹쳤다(한 번에 넷까지)' % (s['z'], nf))
    a_on = shot_arr(pg); B.shot(pg, 'z_on', 100)
    pg.evaluate('(() => { HT.on = false; R3.tmat.uniforms.hiK.value.set(0, 0, 0, 0); UI.render = true; })()')
    a_off = shot_arr(pg); B.shot(pg, 'z_off', 100)
    pg.evaluate('(() => { HT.on = true; HT.last = 0; })()'); pg.wait_for_timeout(500)
    e_on, e_off, share = edge(a_on, a_off); dl = float(np.abs(low(a_on) - low(a_off)).mean())
    print('      선의 또렷함(바탕 그림이 바뀐 자리 %.1f%% 에서 밝기 기울기의 평균): 조각 %.2f · 본래 그림 %.2f  /  큰 얼룩의 밝기 차이 %.2f' % (share * 100, e_on, e_off, dl))
    ok(share > 0.02 and e_on > e_off * 1.3, '조각을 겹친 화면의 선이 더 또렷하다(%.2f > %.2f × 1.3)' % (e_on, e_off))
    ok(dl < 6.0, '겹쳐도 밝기와 빛깔의 큰 흐름은 그대로다(8점 평균의 차이 %.2f / 255)' % dl)
    print('3. 옮겨 다녀도 받아 둔 조각은 여섯까지')
    for c, r in ((60, 60), (180, 150), (40, 170), (200, 40), (110, 110), (150, 60)):
        pg.evaluate('jumpTo(%d, %d, 2.0)' % (c, r)); pg.wait_for_timeout(250)
        pg.wait_for_function('HT.busy === 0', timeout=30000); pg.wait_for_timeout(450)
    pg.wait_for_function('HT.busy === 0 && HT.slot.filter(function (s) { return s.key && s.k >= 1; }).length >= 1', timeout=30000)
    s = pg.evaluate(STATE); print('     ', s, len(reqs))
    ok(s['n'] <= 6 and s['loaded'] >= l0 + 6 and max(s['k']) == 1, '여섯 곳을 옮겨 다닌 뒤: 새로 받은 조각 %d장 · 쥐고 있는 것은 %d장' % (s['loaded'] - l0, s['n']))
    print('4. 멀어지면 내려놓는다')
    pg.evaluate('jumpTo(126, 96, 0.4)'); pg.wait_for_timeout(1000)
    s = pg.evaluate(STATE)
    ok(s['k'] == [0, 0, 0, 0] and all(x.startswith(':') for x in s['slots']), '멀어지면 겹친 조각을 내려놓는다 %s' % s['slots'])
    print('5. 조각을 못 받아도 판은 돈다')
    n_err = len(B.errors)
    pg.route('**/t4-*/*.webp', lambda r: r.abort())
    pg.reload(); pg.wait_for_function('window.R3 && R3.ready', timeout=60000); pg.wait_for_timeout(600)
    B.tapsel(pg, '#tCont'); pg.wait_for_timeout(1300)
    if pg.evaluate('!!MODAL'): pg.evaluate('closeDialog()')
    pg.evaluate('talkHide(); UI.talk = false; jumpTo(126, 96, 2.2)'); pg.wait_for_timeout(2500)
    s = pg.evaluate(STATE); t = pg.evaluate('(() => { var t = G.turn; endTurn(); return [t, G.turn]; })()')
    ok(s['on'] and s['bad'] >= 1 and s['k'] == [0, 0, 0, 0] and s['n'] == 0 and t[1] == t[0] + 1, '조각을 못 받으면 본래 그림 그대로 두고 판은 돈다(못 받은 조각 %d · 턴 %d → %d)' % (s['bad'], t[0], t[1]))
    pg.unroute('**/t4-*/*.webp')
    bad = [e for e in B.errors[n_err:] if 't4-' not in e and 'Failed to load resource' not in e and 'net::ERR_FAILED' not in e]
    ok(not bad, '그동안 다른 오류는 없다 %s' % bad[:2])
B.run(steps, 390, 844, 2)
print('6. 한 파일짜리 판에는 조각이 없다')
B.URL = OFFLINE
def steps2(pg):
    st = pg.evaluate('({ cfg: typeof window.HITILE, on: HT.on, def: !!(R3.tmat.defines && R3.tmat.defines.HITILE) })')
    ok(st == {'cfg': 'undefined', 'on': False, 'def': False}, '오프라인 한 장에서는 꺼져 있다(본래 그림 그대로) %s' % st)
B.run(steps2, 390, 844, 2)
print('7. 앱 판을 파일로 열면(file://) 조각을 청하지 않는다')
B.URL = 'file://' + os.path.join(B.ROOT, '..', 'dist', 'pwa', 'index.html')
def steps3(pg):
    n_err = len(B.errors); rq = []
    pg.on('request', lambda r: rq.append(r.url) if '/t4-' in r.url else None)
    boot(pg)
    pg.evaluate('jumpTo(126, 96, 2.2)'); pg.wait_for_timeout(2200)
    st = pg.evaluate('({ cfg: typeof window.HITILE, on: HT.on, n: Object.keys(HT.tex).length, fail: HT.fail, z: +cam.z.toFixed(1) })')
    bad = [e for e in B.errors[n_err:] if 'GPU stall' not in e and 'GL Driver' not in e and 'willReadFrequently' not in e and 'ERR_FILE_NOT_FOUND' not in e]
    ok(st == {'cfg': 'object', 'on': False, 'n': 0, 'fail': 0, 'z': 2.2} and not rq and not bad, '파일로 연 앱 판: 조각을 청하지 않고(요청 %d) 오류도 없다 %s %s' % (len(rq), st, bad[:1]))
B.run(steps3, 390, 844, 2)
errs = [e for e in B.errors if 'GPU stall' not in e and 'GL Driver' not in e and 'ERR_FILE_NOT_FOUND' not in e and 'willReadFrequently' not in e and 't4-' not in e and 'Failed to load resource' not in e and 'net::ERR_FAILED' not in e]
print('console errors:', errs[:6])
print('\nd43: %d fail' % len(fails), fails)
sys.exit(1 if fails or errs else 0)
