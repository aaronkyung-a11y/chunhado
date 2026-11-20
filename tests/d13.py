# v0.7 앱(PWA)판 점검 — dist/pwa 를 내 컴퓨터의 http 서버로 띄워 놓고: 서비스 워커 등록, 설치 조건, 저장(캐시), 음악 미리 받기와 구간 요청,
#   인터넷을 끊은 채 다시 열기, 새 판을 올렸을 때 바로 바뀌는지, '앱으로 설치' 단추
#   python3 tools/build.py --pwa && python3 tests/d13.py
import sys, os, json, time, subprocess, socket, hashlib
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.abspath(__file__)); PWA = os.path.join(ROOT, '..', 'dist', 'pwa')
RES = []
def check(name, cond, got=None):
    RES.append((name, bool(cond)))
    print(('  ok   ' if cond else '  FAIL ') + name + ('' if cond else '  ← ' + json.dumps(got, ensure_ascii=False)[:500]))
s = socket.socket(); s.bind(('127.0.0.1', 0)); PORT = s.getsockname()[1]; s.close()
srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT), '--bind', '127.0.0.1'], cwd=PWA, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
URL = 'http://127.0.0.1:%d/' % PORT
errors = []
idx = os.path.join(PWA, 'index.html'); orig = open(idx, 'rb').read()
try:
    time.sleep(0.8)
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        cxt = br.new_context(viewport={'width': 412, 'height': 915}, is_mobile=True, has_touch=True, locale='ko-KR')
        pg = cxt.new_page()
        pg.on('console', lambda m: errors.append(m.type + ': ' + m.text + ' @ ' + str((m.location or {}).get('url', ''))[:120]) if m.type == 'error' else None)      # v0.10.1: 어느 자원인지도 적는다
        pg.on('pageerror', lambda e: errors.append('pageerror: ' + str(e)))
        t0 = time.time(); pg.goto(URL); pg.wait_for_function('window.R3 && R3.ready', timeout=90000); t1 = time.time()
        print('  처음 열기(서버에서) %.1f초' % (t1 - t0))
        # ---------- 1. 서비스 워커·설치 조건 ----------
        sw = pg.evaluate('''async () => { var reg = await navigator.serviceWorker.ready; for (var i = 0; i < 50 && !navigator.serviceWorker.controller; i++) await new Promise(function (r) { setTimeout(r, 100); });
          return { scope: reg.scope, state: reg.active && reg.active.state, controlled: !!navigator.serviceWorker.controller, manifest: (document.querySelector('link[rel=manifest]') || {}).href,
            apple: !!document.querySelector('link[rel=apple-touch-icon]'), install: !!document.getElementById('tInstall'), hidden: document.getElementById('tInstall').hidden }; }''')
        print('  서비스 워커', sw)
        check('서비스 워커가 등록되어 이 화면을 맡음', sw['state'] == 'activated' and sw['controlled'] and sw['scope'] == URL, sw)
        check('manifest·애플 아이콘 연결이 들어 있음', sw['manifest'] == URL + 'manifest.webmanifest' and sw['apple'], sw)
        cdp = cxt.new_cdp_session(pg)
        man = cdp.send('Page.getAppManifest'); ie = cdp.send('Page.getInstallabilityErrors')
        mj = json.loads(man.get('data') or '{}')
        print('  manifest 오류', man.get('errors'), '| 설치 조건 오류', ie.get('installabilityErrors'))
        check('크롬이 manifest 를 오류 없이 읽음', not man.get('errors') and mj.get('name') == '삼국지 천하도' and mj.get('display') == 'fullscreen' and len(mj.get('icons', [])) == 3, man.get('errors'))
        other = [e for e in ie.get('installabilityErrors', []) if e.get('errorId') != 'in-incognito']     # 시험용 브라우저는 늘 시크릿 창이라 그 한 가지는 뜬다
        check('크롬의 설치 조건 검사에 걸리는 것이 없음(시험 창이 시크릿이라는 것 말고)', other == [], ie)
        from PIL import Image
        ok_icons = True; sizes = []
        for ic in mj.get('icons', []):
            im = Image.open(os.path.join(PWA, ic['src'])); sizes.append((ic['src'], im.size, ic['sizes'], ic.get('purpose')))
            if '%dx%d' % im.size != ic['sizes']: ok_icons = False
        check('아이콘 파일 크기가 manifest 에 적은 것과 같음', ok_icons, sizes)
        # ---------- 2. 저장(캐시) ----------
        ca = pg.evaluate('''async () => { var out = {}; var ks = await caches.keys(); for (var i = 0; i < ks.length; i++) { var c = await caches.open(ks[i]); out[ks[i]] = (await c.keys()).map(function (r) { return r.url.replace(location.origin, ''); }); } return out; }''')
        print('  저장:', {k: len(v) for k, v in ca.items()})
        sh = ca.get('chunhado-shell-1', [])
        check('화면·manifest·아이콘 5개가 저장됨', '/' in sh and '/manifest.webmanifest' in sh and len([x for x in sh if x.startswith('/icons/')]) == 5, sh)
        # 음악 미리 받기: 화면이 뜨고 6초 뒤에 시작한다
        n = 0
        for i in range(120):
            n = pg.evaluate('''async () => { var c = await caches.open('chunhado-bgm-1'); return (await c.keys()).length; }''')
            if n >= 8: break
            pg.wait_for_timeout(1000)
        check('음악 8곡을 미리 받아 둠', n == 8, n)
        # 구간 요청(Range): 저장해 둔 곡을 잘라서 답하는가
        raw = open(os.path.join(PWA, 'bgm', 'title.mp3'), 'rb').read()
        rg = pg.evaluate('''async () => { var r = await fetch('bgm/title.mp3', { headers: { Range: 'bytes=1000-1999' } }), b = new Uint8Array(await r.arrayBuffer());
          var r2 = await fetch('bgm/title.mp3', { headers: { Range: 'bytes=-500' } }), b2 = new Uint8Array(await r2.arrayBuffer());
          var r3 = await fetch('bgm/title.mp3', { headers: { Range: 'bytes=99999999-' } });
          var r4 = await fetch('bgm/title.mp3'), b4 = await r4.arrayBuffer();
          return { st: r.status, cr: r.headers.get('content-range'), len: b.length, head: Array.prototype.slice.call(b, 0, 16), st2: r2.status, cr2: r2.headers.get('content-range'), len2: b2.length, tail: Array.prototype.slice.call(b2, 484, 500), st3: r3.status, st4: r4.status, len4: b4.byteLength }; }''')
        N = len(raw)
        check('구간 요청에 206 과 맞는 바이트', rg['st'] == 206 and rg['len'] == 1000 and rg['cr'] == 'bytes 1000-1999/%d' % N and rg['head'] == list(raw[1000:1016]), rg)
        check('끝에서부터의 구간·범위 밖·전체 요청', rg['st2'] == 206 and rg['len2'] == 500 and rg['cr2'] == 'bytes %d-%d/%d' % (N - 500, N - 1, N) and rg['tail'] == list(raw[-16:]) and rg['st3'] == 416 and rg['st4'] == 200 and rg['len4'] == N, rg)
        # ---------- 3. '앱으로 설치' 단추 ----------
        b0 = pg.evaluate('''() => { var b = document.getElementById('tInstall'), h0 = b.hidden, called = 0; var e = new Event('beforeinstallprompt'); e.prompt = function () { called++; }; window.dispatchEvent(e); var h1 = b.hidden; b.click(); var h2 = b.hidden; return [h0, h1, h2, called]; }''')
        check("설치할 수 있다는 신호가 오면 '앱으로 설치' 단추가 보이고, 누르면 설치 창을 부름", b0 == [True, False, True, 1], b0)
        pg.screenshot(path=os.path.join(ROOT, 'shots4', 'd13_01_title.png'))
        # ---------- 3b. 앱으로 열렸을 때(전체 화면) 휴대폰의 '뒤로' ----------
        base_hist = pg.evaluate('history.length')
        pg.add_init_script('''(function () { var mm = window.matchMedia.bind(window); window.matchMedia = function (q) {
          if (/display-mode:\\s*(standalone|fullscreen)/.test(q)) return { matches: true, media: q, addListener: function () {}, removeListener: function () {}, addEventListener: function () {}, removeEventListener: function () {} };
          return mm(q); }; })();''')                          # 설치된 앱으로 열린 것처럼(display-mode) 꾸민다
        pg.reload(); pg.wait_for_function('window.R3 && R3.ready', timeout=90000); pg.wait_for_timeout(500)
        def back(): pg.evaluate('history.back()'); pg.wait_for_timeout(450)
        def state(): return pg.evaluate('''() => ({ modal: MODAL ? (document.querySelector('#modal .dlg-h h2') || {}).textContent : null, depth: MSTACK.length, sheet: !SHEET ? null : (SHEET.home ? 'home' : 'sel'), title: !$('title').classList.contains('off'), toast: $('toast').classList.contains('on') ? $('toast').textContent : '' })''')
        pg.locator('#tHelp').tap(); pg.wait_for_timeout(400); s0 = state(); back(); s1 = state()
        check("제목 화면에서 도움말을 연 채 '뒤로' → 도움말만 닫힘", s0['modal'] == '도움말' and s1['modal'] is None and s1['title'], [s0, s1])
        pg.locator('#tNew').tap(); pg.wait_for_timeout(350); pg.locator('#modal .row').nth(0).tap(); pg.wait_for_timeout(300); pg.locator('#modal [data-a=go]').tap(); pg.wait_for_timeout(900)
        pg.locator('#modal [data-a=close]').nth(0).tap(); pg.wait_for_timeout(800)
        pg.locator('#btnList').tap(); pg.wait_for_timeout(350); pg.locator('#modal .tabs button[data-v=off]').tap(); pg.wait_for_timeout(300); pg.locator('#modal .row[data-a=off]').nth(1).tap(); pg.wait_for_timeout(400)
        a = state(); back(); b = state(); back(); c = state()
        check("목록 → 무장 정보에서 '뒤로' → 목록 → 한 번 더 → 닫힘", a['depth'] == 1 and b['modal'] == '목록' and b['depth'] == 0 and c['modal'] is None and c['sheet'] == 'home', [a, b, c])
        pg.evaluate('() => { gotoBase(facBases(G.player)[0]); }'); pg.wait_for_timeout(500); a = state(); back(); b = state()
        check("거점 창에서 '뒤로' → STATUS 창", a['sheet'] == 'sel' and b['sheet'] == 'home', [a, b])
        back(); c = state()
        check("더 물러날 곳이 없으면 '한 번 더 누르면 나갑니다'만 띄우고 그대로", '한 번 더' in c['toast'] and c['sheet'] == 'home' and pg.evaluate('!!(window.R3 && R3.ready)'), c)
        pg.wait_for_timeout(2900)
        pg.locator('#btnMenu').tap(); pg.wait_for_timeout(350); a = state(); back(); b = state()
        check("잠시 뒤에는 다시 '뒤로'를 받음(메뉴 닫힘)", a['modal'] and a['modal'].startswith('메뉴') and b['modal'] is None, [a, b])
        # ---------- 4. 인터넷을 끊고 다시 열기 ----------
        cxt.set_offline(True)
        t0 = time.time(); pg.reload(); pg.wait_for_function('window.R3 && R3.ready', timeout=90000); t1 = time.time()
        print('  인터넷 없이 다시 열기 %.1f초' % (t1 - t0))
        check('인터넷이 없어도 열림', pg.evaluate('!!(window.R3 && R3.ready) && typeof GAME_VERSION === "string"'), None)
        pg.locator('#tHelp').tap(); pg.wait_for_timeout(2500)
        m = pg.evaluate('() => ({ mode: BGM.mode, file: BGM.file, paused: BGM.el ? BGM.el.paused : null, t: BGM.el ? BGM.el.currentTime : -1, dead: Object.keys(BGM.dead), n: Object.keys(SND.buf).length })')
        check('인터넷이 없어도 음악(저장해 둔 title.mp3)과 효과음이 나옴', m['mode'] == 'file' and m['file'] == 'title' and m['paused'] is False and m['t'] > 0.5 and m['n'] == 27, m)
        pg.locator('#modal .dlg-h .x').tap(); pg.wait_for_timeout(300)
        pg.locator('#tNew').tap(); pg.wait_for_timeout(300); pg.locator('#modal .row').nth(0).tap(); pg.wait_for_timeout(300); pg.locator('#modal [data-a=go]').tap(); pg.wait_for_timeout(900)
        pg.locator('#modal [data-a=close]').nth(0).tap(); pg.wait_for_timeout(2500)
        m = pg.evaluate('() => ({ mode: BGM.mode, file: BGM.file, name: BGM.name, paused: BGM.el ? BGM.el.paused : null, t: BGM.el ? BGM.el.currentTime : -1, date: dateStr() })')
        check('인터넷 없이 새 게임 시작 + 평시 음악', m['mode'] == 'file' and m['name'] == 'field' and m['paused'] is False and m['t'] > 0.3, m)
        pg.screenshot(path=os.path.join(ROOT, 'shots4', 'd13_02_offline_game.png'))
        cxt.set_offline(False)
        # ---------- 5. 새 판을 올리면 다음에 열 때 바로 바뀌는가 ----------
        time.sleep(1.2)                                      # 서버의 Last-Modified 는 초 단위
        open(idx, 'wb').write(orig.replace(b'<title>', b'<!-- d13-new-build --><title>', 1))
        t0 = time.time(); pg.reload(); pg.wait_for_function('window.R3 && R3.ready', timeout=90000); t1 = time.time()
        got = pg.evaluate('() => document.documentElement.outerHTML.indexOf("d13-new-build") >= 0')
        print('  새 판을 올린 뒤 다시 열기 %.1f초' % (t1 - t0))
        check('서버의 화면이 바뀌면 다음에 열 때 새 화면', got, got)
        cxt.set_offline(True); pg.reload(); pg.wait_for_function('window.R3 && R3.ready', timeout=90000)
        got2 = pg.evaluate('() => document.documentElement.outerHTML.indexOf("d13-new-build") >= 0')
        check('새 화면이 저장되어 인터넷 없이도 새 화면', got2, got2)
        cxt.set_offline(False)
        br.close()
finally:
    open(idx, 'wb').write(orig)
    srv.terminate()
# v0.10.1: 인터넷 없이 새 판을 시작했을 때, 그때 처음 필요해진 글꼴 조각(예: '등용할 만한 무장'의 招 — 판에 따라 나오기도 안 나오기도 한다)은 받을 수 없다.
#   그 글자는 기기의 글꼴로 대신 그려질 뿐이라 오류로 치지 않고 적어만 둔다(전부터 있던 일 — 0.10.1 에서 군사의 권유가 잦아져 더 자주 걸렸다).
font_miss = [e for e in errors if 'fonts.gstatic.com' in e and 'ERR_FAILED' in e]
if font_miss: print('  (참고) 인터넷 없이 처음 필요해진 글꼴 조각 %d건 — 그 글자는 기기의 글꼴로 그려진다: %s' % (len(font_miss), [e.split('.')[-2] for e in font_miss]))
errs = [e for e in errors if 'GPU stall' not in e and 'GL Driver Message' not in e and 'status of 416' not in e and e not in font_miss]   # 416 은 범위 밖 구간을 일부러 물은 것
print('console errors:', len(errs)); [print('   ', e[:300]) for e in errs[:10]]
bad = [n for n, ok in RES if not ok]
print('검사 %d개 가운데 통과 %d, 실패 %d' % (len(RES), len(RES) - len(bad), len(bad)))
sys.exit(1 if bad or errs else 0)
