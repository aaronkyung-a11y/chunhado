# 불러오는 시간 비교(헤드리스): 페이지를 열어 지도가 준비될 때까지. usage: d9.py file.html [file2.html …]
import sys, os, time
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.abspath(__file__))
with sync_playwright() as p:
    br = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
    for f in sys.argv[1:]:
        ts = []
        for i in range(3):
            cxt = br.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True, locale='ko-KR')
            pg = cxt.new_page(); t0 = time.time()
            pg.goto('file://' + os.path.join(ROOT, '..', f)); pg.wait_for_function('window.R3 && R3.ready', timeout=90000)
            ts.append(round(time.time() - t0, 2)); cxt.close()
        print(f, os.path.getsize(os.path.join(ROOT, '..', f)), 'bytes | ready in', ts, 's')
    br.close()
