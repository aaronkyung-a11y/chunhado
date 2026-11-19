# 모바일 뷰포트에서 실제 조작을 흉내 내며 화면을 찍는다 (v0.2: WebGL — SwiftShader)
import sys, os, json, time
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.join(ROOT, '..', 'dist', os.environ.get('PAGE', 'offline.html'))   # 시험은 three.js를 넣은 판으로
SHOTS = os.path.join(ROOT, 'shots2')
errors = []
def run(steps, w=412, h=915, dpr=1):
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        cxt = br.new_context(viewport={'width': w, 'height': h}, device_scale_factor=dpr, is_mobile=True, has_touch=True, locale='ko-KR')
        pg = cxt.new_page()
        pg.on('console', lambda m: errors.append(m.type + ': ' + m.text) if m.type in ('error', 'warning') else None)
        pg.on('pageerror', lambda e: errors.append('pageerror: ' + str(e)))
        if os.environ.get('CDN'):                       # CDN 판: 주소를 가로채 로컬 파일로 답한다. CDN=fail1 이면 첫 주소는 막는다
            lib = open(os.path.join(ROOT, '..', 'vendor', 'package', 'build', 'three.min.js'), 'rb').read()
            def handler(route):
                u = route.request.url
                if os.environ['CDN'] == 'fail1' and 'cdnjs' in u: route.abort(); return
                if os.environ['CDN'] == 'failall': route.abort(); return
                route.fulfill(status=200, content_type='application/javascript', body=lib)
            pg.route('**/three.min.js', handler)
        pg.goto(URL)
        if os.environ.get('CDN') == 'failall': pg.wait_for_timeout(1500); steps(pg); br.close(); return
        pg.wait_for_function('window.R3 && R3.ready', timeout=60000); pg.wait_for_timeout(600)
        steps(pg)
        br.close()
def shot(pg, name, wait=500):
    pg.wait_for_timeout(wait)
    pg.screenshot(path=os.path.join(SHOTS, name + '.png'))
def hexpos(pg, c, r):
    return pg.evaluate('([c,r]) => { var p = hexPos(c,r), s = w2s(p[0],p[1],p[2]), rc = cv.getBoundingClientRect(); return [s[0]+rc.left, s[1]+rc.top]; }', [c, r])
def taphex(pg, c, r):
    x, y = hexpos(pg, c, r); pg.touchscreen.tap(x, y); pg.wait_for_timeout(300)
def tapsel(pg, sel, nth=0):
    pg.locator(sel).nth(nth).tap(); pg.wait_for_timeout(300)
def start(pg, faction=0):
    tapsel(pg, '#tNew'); tapsel(pg, '#modal .row', faction); tapsel(pg, '#modal [data-a=go]'); pg.wait_for_timeout(500); tapsel(pg, '#modal [data-a=close]'); pg.wait_for_timeout(600)
