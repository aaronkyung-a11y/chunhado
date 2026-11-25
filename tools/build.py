#!/usr/bin/env python3
"""src/*.js, style.css, index.html + 지형 텍스처 → 단일 HTML.
  build.py            → dist/index.html  : three.js를 CDN에서 불러오는 단일 파일(v0.16까지는 이것을 아티팩트에 올렸다. 지금은 버전별 스냅샷 versions/ 에 쓴다)
  build.py --split    → dist/artifact/   : 아티팩트에 올리는 판(v0.17~). index.html(three.js는 CDN) + data/scenes.json(무장의 큰 그림) — 아티팩트의 페이지 하나는 16MiB 까지라서 떼어 냈다
  build.py --embed    → dist/offline.html: three.js까지 넣은 완전 단일 파일(오프라인·시험용)
  build.py --pwa      → dist/pwa/        : 앱으로 설치할 수 있는 판(GitHub Pages용). index.html(three.js 포함) + manifest·sw.js·아이콘·음악
  음악(bgm/*.mp3)은 어느 판이든 HTML 옆의 bgm/ 폴더에서 읽는다. 없으면 코드로 만든 음악이 대신 나온다.
  영상(video/*.mp4 · *.webm — v0.19)도 HTML 옆의 video/ 폴더에서 읽는다. --pwa 와 --split 은 그 폴더를 같이 놓는다. 없으면 영상 없이 돈다."""
import os, sys, re, base64, shutil
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
src = os.path.join(root, 'src')
pwa = '--pwa' in sys.argv
split = '--split' in sys.argv          # v0.17: 아티팩트에 올리는 판 — 큰 그림(SCENES)을 data/scenes.json 으로 떼어 낸다(페이지 하나는 16MiB 까지)
embed = '--embed' in sys.argv or pwa
def rd(n): return open(os.path.join(src, n), encoding='utf-8').read()
THREE_CDN = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/0.149.0/three.min.js'
terrain = "var TERRAIN_B64='" + base64.b64encode(open(os.path.join(root, 'build', 'terrain.jpg'), 'rb').read()).decode('ascii') + "';\n"
CODE = ['mapdata.js', 'roster.js', 'data.js', 'bios.js', 'core.js', 'ai.js', 'ui3d.js', 'fx.js', 'voice.js', 'duel.js', 'cine.js', 'ui_panels.js']      # v0.19: bios.js(열전) · cine.js(영상)
assets = rd('assets.js')
# v0.24: 그림 묶음(src/assets_<pack>.js = var PACK_<pack>={"por":{흉상},"scn":{장면}}; — tools/make_pack24.py). 한 파일짜리 판(오프라인 · PWA)에는 그대로 넣고,
#   아티팩트 판(--split)에는 data/por-<pack>-<지문>.json · data/scn-<pack>-<지문>.json 으로 떼어 페이지가 뜬 뒤에 받아 온다(받기 전에는 그 초상 자리가 빈 종이다).
#   파일 이름에 내용의 지문이 들어 있어, 그림이 바뀌지 않으면 옛 스냅샷(versions/)도 같은 파일을 쓴다.
import json, hashlib
PACKS = [n for n in ('pool', 'p253') if os.path.exists(os.path.join(src, 'assets_%s.js' % n))]
pack_parts = []; pack_files = []; pack_urls = {'por': [], 'scn': []}
for _p in PACKS:
    _t = rd('assets_%s.js' % _p)
    if split:
        _m = re.match(r'^var PACK_%s=(\{.*\});\s*$' % _p, _t, re.S); _o = json.loads(_m.group(1))
        for _k in ('por', 'scn'):
            _j = '{\n' + ',\n'.join(json.dumps(k) + ':' + json.dumps(_o[_k][k]) for k in sorted(_o[_k])) + '\n}\n'
            _n = 'data/%s-%s-%s.json' % (_k, _p, hashlib.sha256(_j.encode('utf-8')).hexdigest()[:8])
            pack_files.append((_n, _j)); pack_urls[_k].append(_n)
    else:
        pack_parts.append(('assets_%s.js' % _p, _t + '(function(P){var k;for(k in P.por)PORTRAITS[k]=P.por[k];for(k in P.scn)SCENES[k]=P.scn[k];})(PACK_%s);PACK_%s=null;' % (_p, _p)))
# v0.18: 제목 그림(TITLE_IMG)은 CSS 로 옮긴다 — 큰 스크립트를 다 읽기 전, 첫 화면부터 그려지게(앱을 열자마자 보이는 그림이다)
_mt = re.search(r'^var TITLE_IMG="([^"]+)";$', assets, re.M)
TITLE_CSS = ('\n/* 제목 그림(tools/build.py 가 src/assets.js 의 TITLE_IMG 를 옮겨 넣는다) */\n#title { background-image: url(' + _mt.group(1) + '); }\n') if _mt else ''
if _mt: assets = assets[:_mt.start()] + 'var TITLE_IMG="";' + assets[_mt.end():]
scenes_json = None
if split:
    import re, json
    m = re.search(r'^var SCENES=(\{.*\});$', assets, re.M)
    obj = json.loads(m.group(1))
    scenes_json = '{\n' + ',\n'.join(json.dumps(k) + ':' + json.dumps(obj[k]) for k in sorted(obj)) + '\n}\n'
    # 큰 그림은 페이지가 뜬 뒤에 받아 온다. 받기 전(이나 받지 못했을 때)에는 작은 초상이 그 자리에 나온다(sceneTag · duPor 가 본래 그렇게 한다)
    LOADER = '''var SCENES={};
(function () {
  function go(n) {
    fetch('data/scenes.json').then(function (r) { if (!r.ok) throw new Error('scenes ' + r.status); return r.json(); }).then(function (o) {
      for (var k in o) SCENES[k] = o[k]; window.SCENES_READY = true;                  // v0.24: 바꿔치지 않고 더한다(그림 묶음의 장면이 먼저 와 있을 수 있다)
      if (typeof SCENE_URL !== 'undefined') SCENE_URL = {};                    // 받기 전에 '없음'으로 적어 둔 것을 지운다
      try { if (typeof MODAL !== 'undefined' && MODAL && typeof refreshDialog === 'function') refreshDialog(); } catch (e) { /* */ }
    }).catch(function () { if (n < 3) setTimeout(function () { go(n + 1); }, 2500 * (n + 1)); else window.SCENES_READY = false; });
  }
  go(0);
})();'''
    if PACKS:                                                                # v0.24: 그림 묶음을 받아 온다
        LOADER += '''
window.PACKS_WANT = %d; window.PACKS_READY = 0;
(function () {
  function get(url, done, n) { n = n || 0; fetch(url).then(function (r) { if (!r.ok) throw new Error(url + ' ' + r.status); return r.json(); }).then(done).catch(function () { if (n < 3) setTimeout(function () { get(url, done, n + 1); }, 2500 * (n + 1)); else window.PACKS_FAIL = (window.PACKS_FAIL || 0) + 1; }); }
  function redraw() { try { if (typeof G !== 'undefined' && G && typeof refreshHud === 'function') { refreshHud(); if (typeof refreshSheet === 'function') refreshSheet(); } if (typeof MODAL !== 'undefined' && MODAL && typeof refreshDialog === 'function') refreshDialog(); } catch (e) { /* */ } }
  %s.forEach(function (u) { get(u, function (o) { for (var k in o) { PORTRAITS[k] = o[k]; if (window.POR_BUILT) { POR_URL[k] = URL.createObjectURL(b64blob(o[k], 'image/webp')); delete POR_IMG[k]; } } window.PACKS_READY++; redraw(); }); });
  %s.forEach(function (u) { get(u, function (o) { for (var k in o) SCENES[k] = o[k]; if (typeof SCENE_URL !== 'undefined') SCENE_URL = {}; window.PACKS_READY++; redraw(); }); });
})();''' % (len(pack_files), json.dumps(pack_urls['por']), json.dumps(pack_urls['scn']))
    assets = assets[:m.start()] + LOADER + assets[m.end():]
parts = [('assets.js', assets)] + pack_parts + [('terrain', terrain), ('sprites.js', rd('sprites.js')), ('map3d.js', rd('map3d.js')), ('sfxdata.js', rd('sfxdata.js')), ('voicedata.js', rd('voicedata.js'))] + [(n, rd(n)) for n in CODE]
js = '\n'.join('/* ==== file: ' + n + ' ==== */\n' + t for n, t in parts)
# v0.26: 가까이 당겼을 때의 바탕 그림(4배 조각 — tools/map4.py 가 art/map4/tiles 에 만든다). 아티팩트 판은 data/t4-<지문>/, 앱(PWA)은 tiles/t4-<지문>/ 에 두고
#   가까이 당긴 자리의 조각만 받아 온다(src/ui3d.js 의 hiTick). 한 파일짜리 판(오프라인 · dist/index.html)에는 없다 — 본래 그림 그대로다.
HITILE = None
_tj = os.path.join(root, 'art', 'map4', 'tiles.json')
if (split or pwa) and os.path.exists(_tj):
    _tm = json.load(open(_tj)); HITILE = ('data' if split else 'tiles') + '/t4-' + _tm['hash'] + '/'
    js = 'window.HITILE = ' + json.dumps({'base': HITILE, 'nx': _tm['nx'], 'ny': _tm['ny'], 'w': _tm['w'], 'h': _tm['h'], 'm': _tm['m'], 'W': _tm['W'], 'H': _tm['H']}) + ';\n' + js
def copy_tiles(parent):
    if not HITILE: return
    for _d in (os.listdir(parent) if os.path.isdir(parent) else []):
        if _d.startswith('t4-') and _d != 't4-' + _tm['hash']: shutil.rmtree(os.path.join(parent, _d))
    dst = os.path.join(parent, 't4-' + _tm['hash']); os.makedirs(dst, exist_ok=True)
    for n in sorted(os.listdir(os.path.join(root, 'art', 'map4', 'tiles'))):
        if n.endswith('.webp'): shutil.copy(os.path.join(root, 'art', 'map4', 'tiles', n), os.path.join(dst, n))
assert '</script' not in js.lower()
if embed:
    three = open(os.path.join(root, 'vendor', 'package', 'build', 'three.min.js'), encoding='utf-8').read()
    assert '</script' not in three.lower()
    tag = '<script>\n' + three + '\n</script>'
else:
    tag = '<script src="' + THREE_CDN + '"></script>'
# 앱(PWA)판에만 들어가는 것: manifest·아이콘 연결, 서비스 워커 등록, '앱으로 설치' 단추
PWA_HEAD = """<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" sizes="48x48" href="icons/favicon-48.png">
<link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black">
<meta name="apple-mobile-web-app-title" content="천하도">
<meta name="description" content="삼국지 11 PK식 시스템의 모바일 삼국지 전략 게임">"""
PWA_JS = """<script>
/* 앱(PWA): 서비스 워커를 등록하고(https 또는 내 컴퓨터에서만), 설치할 수 있으면 제목 화면에 '앱으로 설치' 단추를 보인다 */
(function () {
  var btn = document.getElementById('tInstall'), ask = null;
  window.addEventListener('beforeinstallprompt', function (e) { e.preventDefault(); ask = e; if (btn) btn.hidden = false; });
  window.addEventListener('appinstalled', function () { ask = null; if (btn) btn.hidden = true; });
  if (btn) btn.addEventListener('click', function () {
    if (!ask) return;
    var a = ask; ask = null; btn.hidden = true;
    try { a.prompt(); } catch (e) { /* */ }
  });
  // 앱으로 열렸을 때(전체 화면·독립 창)만: 휴대폰의 '뒤로'가 앱을 바로 끄지 않고 ×처럼 한 단계씩 물러나게 한다
  var inApp = false;
  try { inApp = matchMedia('(display-mode: standalone)').matches || matchMedia('(display-mode: fullscreen)').matches || navigator.standalone === true; } catch (e) { /* */ }
  if (inApp && window.history && history.pushState) {
    var hold = function () { try { history.pushState({ app: 1 }, ''); } catch (e) { /* */ } };
    hold();
    window.addEventListener('popstate', function () {
      var went = false;
      try { went = typeof appBack === 'function' && appBack(); } catch (e) { /* */ }
      if (went) { hold(); return; }
      try { toast('뒤로를 한 번 더 누르면 나갑니다', 2200); } catch (e) { /* */ }
      setTimeout(hold, 2500);                               // 그 사이에 한 번 더 누르면 앱이 닫히고, 안 누르면 다시 받는다
    });
  }
  if (!('serviceWorker' in navigator)) return;
  if (location.protocol !== 'https:' && location.hostname !== 'localhost' && location.hostname !== '127.0.0.1') return;
  window.addEventListener('load', function () {
    try {
      navigator.serviceWorker.register('sw.js').then(function () { return navigator.serviceWorker.ready; }).then(function (reg) {
        setTimeout(function () { try { if (reg.active) reg.active.postMessage('warm'); } catch (e) { /* */ } }, 6000);   // 화면이 뜬 뒤에 음악을 받아 둔다
      }).catch(function () { /* 등록이 안 되어도 게임은 된다 */ });
    } catch (e) { /* */ }
  });
})();
</script>"""
html = rd('index.html').replace('/*__CSS__*/', rd('style.css') + TITLE_CSS).replace('<!--__THREE__-->', tag).replace('/*__JS__*/', js)
assert '<!--__PWA_HEAD__-->' in html and '<!--__PWA_JS__-->' in html
html = html.replace('<!--__PWA_HEAD__-->', PWA_HEAD if pwa else '').replace('<!--__PWA_JS__-->', PWA_JS if pwa else '')
os.makedirs(os.path.join(root, 'dist'), exist_ok=True)
def copy_video(d):                                               # v0.19: 영상 파일을 판 옆에 놓는다
    v = os.path.join(root, 'video')
    if not os.path.isdir(v): return
    os.makedirs(os.path.join(d, 'video'), exist_ok=True)
    for n in sorted(os.listdir(v)):
        if n.endswith('.mp4') or n.endswith('.webm'): shutil.copy(os.path.join(v, n), os.path.join(d, 'video', n))
if pwa:
    d = os.path.join(root, 'dist', 'pwa')
    if os.path.isdir(d): shutil.rmtree(d)
    os.makedirs(os.path.join(d, 'icons')); os.makedirs(os.path.join(d, 'bgm'))
    out = os.path.join(d, 'index.html')
    for n in ('manifest.webmanifest', 'sw.js'): shutil.copy(os.path.join(root, 'pwa', n), os.path.join(d, n))
    for n in sorted(os.listdir(os.path.join(root, 'pwa', 'icons'))): shutil.copy(os.path.join(root, 'pwa', 'icons', n), os.path.join(d, 'icons', n))
    for n in sorted(os.listdir(os.path.join(root, 'bgm'))):
        if n.endswith('.mp3'): shutil.copy(os.path.join(root, 'bgm', n), os.path.join(d, 'bgm', n))
    copy_video(d); copy_tiles(os.path.join(d, 'tiles'))
    open(os.path.join(d, '.nojekyll'), 'w').close()                      # GitHub Pages: 파일을 그대로 내보내게
else:
    out = os.path.join(root, 'dist', 'offline.html' if embed else 'index.html')
    if split:
        assert not embed
        os.makedirs(os.path.join(root, 'dist', 'artifact', 'data'), exist_ok=True)
        out = os.path.join(root, 'dist', 'artifact', 'index.html')
        open(os.path.join(root, 'dist', 'artifact', 'data', 'scenes.json'), 'w', encoding='utf-8').write(scenes_json)
        for _f in os.listdir(os.path.join(root, 'dist', 'artifact', 'data')):          # v0.24: 그림 묶음(옛 지문의 파일은 치운다)
            if _f.startswith('por-') or _f.startswith('scn-'): os.remove(os.path.join(root, 'dist', 'artifact', 'data', _f))
        for _n, _j in pack_files: open(os.path.join(root, 'dist', 'artifact', _n), 'w', encoding='utf-8').write(_j)
        copy_video(os.path.join(root, 'dist', 'artifact')); copy_tiles(os.path.join(root, 'dist', 'artifact', 'data'))
        assert len(html.encode('utf-8')) < 16 * 1024 * 1024, '아티팩트의 페이지는 16MiB 까지'
open(out, 'w', encoding='utf-8').write(html)
open(os.path.join(root, 'dist', 'code.js'), 'w', encoding='utf-8').write('\n'.join(rd(n) for n in CODE))   # 문법 검사용
print('built', out, os.path.getsize(out), 'bytes')
