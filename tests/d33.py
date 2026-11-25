# v0.19 — 화면 조작으로 확인: ① 무장 창 · 무장 카드의 열전(적성의 계산법 글은 도움말로) ② 영상 — 제목의 움직이는 그림 · 오프닝 · 끝(천하통일 / 패망) · 끄기 · 파일이 없을 때
#   ③ 한쪽으로 몰린 장면을 다시 자른 것(그림 265장을 재서 본다)
#   영상은 판 옆의 video/ 에서 읽으므로 앱판(dist/pwa/)으로 본다. 파일이 없는 판(dist/offline.html)으로도 한 번 더 — 조용히 건너뛰는지.
#   python3 tests/d33.py          찍은 그림은 tests/shots35/
import sys, os, json, io, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import taphex, tapsel
B.SHOTS = os.path.join(B.ROOT, 'shots35')
os.makedirs(B.SHOTS, exist_ok=True)
DIST = os.path.join(B.ROOT, '..', 'dist')
fails = []
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)
def head(pg): return pg.evaluate('MODAL && document.querySelector("#modal .dlg-h h2") ? document.querySelector("#modal .dlg-h h2").textContent : ""')
VID = '''() => { var v = $('tVid'); return v ? { on: v.classList.contains('on'), paused: v.paused, t: v.currentTime, w: v.videoWidth, h: v.videoHeight, loop: v.loop, muted: v.muted, src: (v.currentSrc || '').split('/').pop(), bad: v.getAttribute('data-bad'), set: v.getAttribute('data-set'),
  op: +getComputedStyle(v).opacity, fit: getComputedStyle(v).objectFit, z: getComputedStyle(v).zIndex } : null; }'''
CINE = '''() => { var b = $('cine'), v = b.querySelector('video'); return { cls: b.className, on: CINE.on, held: CINE.held, name: CINE.name, z: getComputedStyle(b).zIndex, disp: getComputedStyle(b).display, cap: (b.querySelector('.cn-tx b') || {}).textContent || '', sub: (b.querySelector('.cn-tx span') || {}).textContent || '',
  t: v ? v.currentTime : -1, dur: v ? v.duration : -1, paused: v ? v.paused : null, src: v ? (v.currentSrc || '').split('/').pop() : '', skip: !!b.querySelector('.cn-skip') && getComputedStyle(b.querySelector('.cn-skip')).display !== 'none' }; }'''
def steps(pg):
    # ---------- 1. 제목 화면의 움직이는 그림 ----------
    v0 = pg.evaluate(VID); print('  제목(영상 끔):', v0)
    ok(v0 is not None and not v0['on'] and v0['paused'] and v0['set'] is None, '시험 틀은 영상을 꺼 둔다 — 제목의 영상은 돌지 않고, 파일도 받지 않는다')
    pg.evaluate('() => { UI.video = true; titleVideo(true); }')
    pg.wait_for_function('$("tVid").classList.contains("on")', timeout=12000); pg.wait_for_timeout(900)
    v1 = pg.evaluate(VID); pg.wait_for_timeout(700); v2 = pg.evaluate(VID); print('  제목(영상 켬):', v1, '→ t', v2['t'])
    ok(v1['on'] and not v1['paused'] and v2['t'] != v1['t'] and v1['w'] == 720 and v1['h'] == 1280, '영상이 돈다(720 × 1280 · %s) — 시각 %.2f → %.2f' % (v1['src'], v1['t'], v2['t']))
    ok(v1['loop'] and v1['muted'] and v1['fit'] == 'cover' and v1['op'] > 0.9, '되풀이 · 무음 · 화면을 덮는다 · 서서히 드러난 뒤 다 보인다')
    B.shot(pg, 'a1_title', 200)
    hit = pg.evaluate('''() => { var r = $('tNew').getBoundingClientRect(), e = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2), n = document.querySelector('.t-han').getBoundingClientRect(), e2 = document.elementFromPoint(n.left + n.width / 2, n.top + n.height / 2); return [e && e.id, e2 && e2.className]; }''')
    ok(hit[0] == 'tNew' and hit[1] == 't-han', '영상은 글자와 단추 뒤에 깔린다(누르면 단추가 받는다) %s' % hit)
    tapsel(pg, '#tHelp'); pg.wait_for_timeout(300)
    hp = pg.evaluate('document.querySelector("#modal .dlg").textContent'); pg.evaluate('closeDialog()')
    ok('열전' in hp and '영상' in hp and '×0.85' in hp and '동작 줄이기' in hp, '도움말: 열전 · 영상 · 적성의 곱(×0.85 …)이 여기로 옮겨 왔다')

    # ---------- 2. 오프닝 ----------
    tapsel(pg, '#tNew'); tapsel(pg, '#modal .row', 0); tapsel(pg, '#modal [data-a=go]')
    pg.wait_for_function('$("cine").classList.contains("play")', timeout=8000); pg.wait_for_timeout(1300)
    c1 = pg.evaluate(CINE); tv = pg.evaluate(VID); print('  오프닝:', c1); B.shot(pg, 'b1_opening', 100)
    ok(c1['on'] and c1['name'] == 'opening' and c1['disp'] == 'block' and int(c1['z']) >= 60 and c1['t'] > 0.3 and not c1['paused'], '새 판을 시작하면 오프닝 영상이 화면을 덮고 돈다(%s · %.1f초 가운데 %.1f초)' % (c1['src'], c1['dur'], c1['t']))
    ok(c1['cap'] == '群雄割據' and '194년' in c1['sub'] and c1['skip'], '글자는 영상 위에 얹는다: %s / %s · [건너뛰기]' % (c1['cap'], c1['sub']))
    ok(tv['paused'] and pg.evaluate('!MODAL && !!G && $("title").classList.contains("off")'), '그동안 제목의 영상은 멈추고, 판은 이미 시작되어 있다(창은 아직 없다)')
    pg.touchscreen.tap(190, 400); pg.wait_for_timeout(120)
    cm = pg.evaluate('''() => { var b = $('cine'), d = document.querySelector('#modal [data-a=close]'), r = d ? d.getBoundingClientRect() : null, e = r ? document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2) : null;
      return { cls: b.className, op: +getComputedStyle(b).opacity, pe: getComputedStyle(b).pointerEvents, dur: b.style.transitionDuration, on: CINE.on, modal: !!MODAL, hit: !!d && (e === d || d.contains(e)) }; }''')
    print('  건너뛴 직후:', cm)
    ok('out' in cm['cls'] and 0 < cm['op'] < 1 and cm['dur'] == '320ms' and not cm['on'] and cm['modal'] and '194년' in head(pg), 'v0.19.1 화면을 누르면 뚝 끊기지 않고 0.32초 동안 걷힌다 — 그 아래에 첫 창이 이미 떠 있다(불투명도 %.2f)' % cm['op'])
    ok(cm['pe'] == 'none' and cm['hit'], '걷히는 동안 누름은 아래의 창이 받는다')
    pg.wait_for_timeout(600)
    c2 = pg.evaluate(CINE)
    ok(not c2['on'] and c2['cls'] == '' and c2['disp'] == 'none' and '194년' in head(pg), '다 걷히면 영상은 치워진다 — %s' % head(pg))
    tapsel(pg, '#modal [data-a=close]'); pg.wait_for_timeout(500)

    # ---------- 3. 열전 ----------
    bio = pg.evaluate('''() => { var L = off(G.factions[G.player].lord); showOfficer(L); var b = document.querySelector('#modal .dlg-b'), p = b.querySelector('.bio'), kids = Array.prototype.map.call(b.children, function (e) { return e.className; });
      var r = { name: L.n, bio: p ? p.textContent : '', head: (b.querySelector('.sec.bioh') || {}).textContent || '', aptn: !!b.querySelector('.aptn'), apt: b.querySelectorAll('.apt > div').length, text: b.innerText, order: kids, fits: p ? p.scrollWidth <= p.clientWidth + 1 : false, fs: p ? getComputedStyle(p).fontSize : '' };
      return r; }''')
    print('  무장 창:', bio['name'], '|', bio['bio'], '|', bio['order']); B.shot(pg, 'c1_officer', 300)
    ok(bio['head'] == '열전' and '맹덕' in bio['bio'] and len(bio['bio']) >= 40 and bio['fits'], '무장 창에 열전 — %s' % bio['bio'][:40])
    ok(not bio['aptn'] and '×0.85' not in bio['text'] and '곱해집니다' not in bio['text'] and bio['apt'] == 5 and '병종 적성' in bio['text'], '적성의 계산법 글은 없다(적성 다섯 칸과 제목은 그대로)')
    o = bio['order']; ok(o.index('sec bioh') > o.index('apt') and o.index('bio') == o.index('sec bioh') + 1 and o.index('bio') < o.index('stats'), '차례: 적성 → 특기 → 열전 → 소재 · 충성 …')
    pg.evaluate('closeDialog()')
    alln = pg.evaluate('''() => { var no = G.officers.filter(function (o) { return !bioOf(o); }).map(function (o) { return o.n; }); return [G.officers.length, no]; }''')
    ok(alln[0] == 508 and alln[1] == [],      # v0.23: 다른 시대의 무장 83명
       '판 안의 무장 %d명 모두에게 열전이 있다' % alln[0])
    card = pg.evaluate('''() => { var o = G.officers.filter(function (x) { return x.n === '초선'; })[0]; ocardOpen(o); var e = $('ocard'), p = e.querySelector('.bio'), r = e.querySelector('.oc').getBoundingClientRect(); var t = { bio: p ? p.textContent : '', aptn: !!e.querySelector('.aptn'), inView: r.top >= 0 && r.bottom <= innerHeight + 1 }; return t; }''')
    B.shot(pg, 'c2_card', 300); pg.evaluate('ocardClose()')
    ok('연의의 인물' in card['bio'] and not card['aptn'] and card['inView'], '얼굴을 누르면 뜨는 무장 카드에도 열전(지어낸 인물은 그렇다고 적는다) — %s' % card['bio'][:30])

    # ---------- 4. 메뉴에서 끈다 ----------
    pg.evaluate('showMenu()'); pg.wait_for_timeout(250)
    mb = pg.evaluate('(document.querySelector("#modal [data-a=vid]") || {}).innerText || ""')
    tapsel(pg, '#modal [data-a=vid]'); off1 = pg.evaluate('[UI.video, JSON.parse(localStorage.getItem("chunhado_opts")).video, document.querySelector("#modal [data-a=vid]").innerText, $("toast").textContent]')
    tapsel(pg, '#modal [data-a=vid]'); on1 = pg.evaluate('[UI.video, JSON.parse(localStorage.getItem("chunhado_opts")).video, document.querySelector("#modal [data-a=vid]").innerText]')
    pg.evaluate('closeDialog()')
    ok('영상 켜짐' in mb and off1[0] is False and off1[1] is False and '꺼짐' in off1[2] and '영상 끔' in off1[3] and on1[0] is True and on1[1] is True and '켜짐' in on1[2], '메뉴의 [영상]으로 끄고 켠다(기억한다) — %s → %s' % (mb.replace('\n', ' '), off1[2].replace('\n', ' ')))

    # ---------- 5. 끝: 천하통일 — 영상이 끝나면 마지막 장면 위에 창 ----------
    pg.evaluate('() => { G.over = "win"; showGameOver(); }')
    pg.wait_for_function('$("cine").classList.contains("play")', timeout=8000); pg.wait_for_timeout(900)
    w1 = pg.evaluate(CINE); B.shot(pg, 'd1_win', 100)
    ok(w1['on'] and w1['name'] == 'win' and w1['cap'] == '天下統一' and not pg.evaluate('!!MODAL'), '천하통일: 영상이 먼저 돈다(%s) — 큰 글 %s, 창은 아직' % (w1['src'], w1['cap']))
    pg.evaluate('() => { showGameOver(); afterAction(); }'); pg.wait_for_timeout(200)
    ok(pg.evaluate('CINE.on && !MODAL') and pg.evaluate(CINE)['t'] > w1['t'], '도는 동안 다시 불려도 처음부터 다시 틀지 않는다')
    pg.wait_for_function('CINE.held === true', timeout=12000); pg.wait_for_timeout(500)
    w2 = pg.evaluate(CINE); B.shot(pg, 'd2_win_dialog', 200)
    top = pg.evaluate('''() => { var b = document.querySelector('#modal [data-a=t]'), r = b.getBoundingClientRect(), e = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); return [e === b || b.contains(e), document.querySelector('#modal h2').textContent, $('cine').classList.contains('held')]; }''')
    ok(w2['held'] and not w2['on'] and w2['paused'] and int(w2['z']) < 20 and w2['t'] > 4.0 and not w2['skip'], '영상이 끝나면 마지막 장면이 바탕으로 남는다(%.1f초에서 멈춤 · 창 아래)' % w2['t'])
    ok(top[0] and top[1] == '천하통일' and top[2], '그 위에 끝 창이 뜨고 [처음으로]가 눌린다 — %s' % top[1])
    tapsel(pg, '#modal [data-a=t]'); pg.wait_for_timeout(1200)
    e1 = pg.evaluate('[!!G, $("title").classList.contains("off"), $("cine").className, !!MODAL, UI.ending]'); tv2 = pg.evaluate(VID)
    ok(e1 == [False, False, '', False, None] and not tv2['paused'], '[처음으로]: 바탕의 영상을 걷고 제목으로 — 제목의 영상이 다시 돈다 %s' % e1)

    # ---------- 6. 끝: 패망 — 도중에 누르면 그 장면에서 멈추고 창 ----------
    pg.evaluate('() => { UI.video = false; }'); B.start(pg, 0); pg.evaluate('() => { UI.video = true; G.over = "lose"; showGameOver(); }')
    pg.wait_for_function('$("cine").classList.contains("play")', timeout=8000); pg.wait_for_timeout(1200)
    l1 = pg.evaluate(CINE); B.shot(pg, 'e1_lose', 100)
    pg.touchscreen.tap(190, 300); pg.wait_for_timeout(500)
    l2 = pg.evaluate(CINE)
    ok(l1['name'] == 'lose' and l1['cap'] == '敗亡' and l2['held'] and l2['paused'] and 0.5 < l2['t'] < 4.5 and head(pg) == '패망', '패망: 누르면 그 장면(%.1f초)에서 멈추고 창이 뜬다 — %s' % (l2['t'], head(pg)))
    pg.touchscreen.tap(190, 200); pg.wait_for_timeout(300)
    ok(pg.evaluate('CINE.held && !!MODAL') and head(pg) == '패망', '멈춘 바탕을 눌러도 창은 닫히지 않는다')
    tapsel(pg, '#modal [data-a=t]'); pg.wait_for_timeout(600)

    # ---------- 7. 영상을 끄면 전과 똑같이 ----------
    pg.evaluate('() => { UI.video = false; titleVideo(true); }'); pg.wait_for_timeout(300)
    ok(pg.evaluate(VID)['paused'] and not pg.evaluate(VID)['on'], '끄면 제목의 영상이 멈추고 그림만 남는다')
    tapsel(pg, '#tNew'); tapsel(pg, '#modal .row', 0); tapsel(pg, '#modal [data-a=go]'); pg.wait_for_timeout(400)
    ok('194년' in head(pg) and pg.evaluate('$("cine").className') == '', '끄면 오프닝 없이 곧바로 첫 창')
    tapsel(pg, '#modal [data-a=close]'); pg.wait_for_timeout(400)
    pg.evaluate('() => { G.over = "win"; showGameOver(); }'); pg.wait_for_timeout(300)
    ok(head(pg) == '천하통일' and pg.evaluate('$("cine").className') == '', '끄면 끝 창도 곧바로')
    # Esc(휴대폰의 뒤로)는 도는 영상부터 건너뛴다
    tapsel(pg, '#modal [data-a=t]'); pg.wait_for_timeout(400)
    pg.evaluate('() => { UI.video = true; window.CN = null; cinePlay("opening", { cap: "群雄割據" }, function (s) { window.CN = s; }); }')
    pg.wait_for_function('$("cine").classList.contains("play")', timeout=8000); pg.wait_for_timeout(300)
    r = pg.evaluate('appBack()'); pg.wait_for_timeout(700)
    ok(r is True and pg.evaluate('window.CN') is True and pg.evaluate('$("cine").className') == '', '뒤로(appBack)는 도는 영상부터 건너뛴다')
    # v0.19.1: 저절로 끝날 때 — 끝나기 0.9초 전부터 걷히기 시작하고, 그때 다음 일(done)이 불린다
    pg.evaluate('() => { window.CN = null; window.CT = null; cinePlay("opening", { cap: "群雄割據" }, function (s) { var v = $("cine").querySelector("video"); window.CN = s; window.CT = v ? [v.currentTime, v.duration, v.paused] : null; }); }')
    pg.wait_for_function('window.CN !== null', timeout=15000); pg.wait_for_timeout(300)
    f1 = pg.evaluate('''() => { var b = $('cine'); return { cn: window.CN, ct: window.CT, cls: b.className, op: +getComputedStyle(b).opacity, dur: b.style.transitionDuration, on: CINE.on, disp: getComputedStyle(b).display }; }''')
    pg.wait_for_timeout(500); f2 = pg.evaluate('+getComputedStyle($("cine")).opacity'); pg.wait_for_timeout(700); f3 = pg.evaluate('[$("cine").className, getComputedStyle($("cine")).display, $("cine").style.transitionDuration]')
    print('  저절로 끝날 때:', f1, '→', f2, '→', f3)
    ok(f1['cn'] is False and f1['ct'] and 0.3 < f1['ct'][1] - f1['ct'][0] <= 0.95 and f1['ct'][2] is False, '끝나기 %.2f초 전에 걷히기 시작한다(영상은 아직 도는 중 · 그때 다음 창을 띄운다)' % (f1['ct'][1] - f1['ct'][0]))
    ok('out' in f1['cls'] and f1['dur'] == '900ms' and f1['disp'] == 'block' and not f1['on'] and 0 < f2 < f1['op'] < 1, '0.9초 동안 서서히 투명해진다(불투명도 %.2f → %.2f)' % (f1['op'], f2))
    ok(f3 == ['', 'none', ''], '다 걷히면 치워진다')
def nofile(pg):
    # 한 파일로 만든 판: 옆에 video/ 가 없다 — 조용히 건너뛴다
    pg.evaluate('() => { UI.video = true; titleVideo(true); }'); pg.wait_for_timeout(2500)
    v = pg.evaluate(VID)
    ok(not v['on'] and v['bad'] == '1' and v['op'] == 0, '영상 파일이 없으면 제목은 그림 그대로(표시 %s)' % v['bad'])
    t0 = pg.evaluate('''() => { window.CN = null; window.T0 = performance.now(); cinePlay('opening', { cap: '群雄割據' }, function (s) { window.CN = [s, Math.round(performance.now() - T0)]; }); return true; }''')
    pg.wait_for_function('window.CN !== null', timeout=8000)
    cn = pg.evaluate('window.CN'); st = pg.evaluate('[$("cine").className, CINE.on, CINE.held]')
    ok(cn[0] is True and cn[1] < 4200 and st == ['', False, False], '오프닝: 틀 수 없으면 %d ms 만에 건너뛰고 다음으로(화면에 남는 것 없음)' % cn[1])
    B.start(pg, 0)
    pg.evaluate('() => { UI.video = true; G.over = "lose"; showGameOver(); }'); pg.wait_for_function('!!MODAL', timeout=8000)
    ok(head(pg) == '패망' and pg.evaluate('$("cine").className') == '', '끝: 영상이 없으면 창만 뜬다')
B.URL = 'file://' + os.path.join(DIST, 'pwa', 'index.html')
B.run(steps, 390, 844, 2)
B.URL = 'file://' + os.path.join(DIST, 'offline.html')
B.run(nofile, 390, 844, 2)

# ---------- 8. 파일: 영상 여덟 개 · 서비스 워커 · 한쪽으로 몰린 장면 ----------
import subprocess, hashlib
import numpy as np
from PIL import Image
want = ['lose.mp4', 'lose.webm', 'opening.mp4', 'opening.webm', 'title.mp4', 'title.webm', 'win.mp4', 'win.webm']
for d in ('pwa', 'artifact'):
    fs = sorted(os.listdir(os.path.join(DIST, d, 'video'))); sz = sum(os.path.getsize(os.path.join(DIST, d, 'video', f)) for f in fs)
    ok(fs == want and sz < 9 * 1024 * 1024, 'dist/%s/video: 영상 여덟 개 · 모두 %.2f MB' % (d, sz / 1e6))
def probe(f): return subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=codec_name,width,height', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True, text=True).stdout.replace('\n', ',').strip(',')
pr = {f: probe(os.path.join(DIST, 'pwa', 'video', f)) for f in want}
print('  영상:', pr)
ok(all(pr[f].startswith('h264,720,1280') for f in want if f.endswith('.mp4')) and all(pr[f].startswith('vp9,720,1280') for f in want if f.endswith('.webm')), '.mp4 는 H.264 · .webm 은 VP9 · 720 × 1280')
ok(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type', '-of', 'csv=p=0', os.path.join(DIST, 'pwa', 'video', 'opening.mp4')], capture_output=True, text=True).stdout.split() == ['video'], '소리 줄은 없다(무음)')
sw = open(os.path.join(DIST, 'pwa', 'sw.js'), encoding='utf-8').read()
ok("VID = 'chunhado-video-1'" in sw and "video/' + n + '.mp4'" in sw and 'warm(VID, VIDEO_FILES)' in sw and "media(req, VID," in sw, '앱판의 서비스 워커: 영상을 받아 두고(구간 요청에도 답한다) 인터넷 없이도 튼다')
def ink(a):
    lum = a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114; sat = (a.max(axis=2) - a.min(axis=2)) / 255.0
    return np.maximum(np.clip((244.0 - lum) / 244.0, 0, 1), np.clip(sat * 1.2 - 0.05, 0, 1))
def centre(b64):
    a = np.asarray(Image.open(io.BytesIO(base64.b64decode(b64))).convert('RGB')).astype(np.float32); w = ink(a); d = np.where(w > 0.32, w, 0.0).sum(axis=0)
    c = np.cumsum(d); W = a.shape[1]; return float((d * np.arange(W)).sum() / d.sum()) / W, float(np.searchsorted(c, d.sum() * 0.03)) / W, 1 - float(np.searchsorted(c, d.sum() * 0.97)) / W
new = json.load(open(os.path.join(DIST, 'artifact', 'data', 'scenes.json'), encoding='utf-8')); old = json.load(open(os.path.join(B.ROOT, '..', 'versions', 'chunhado-v0.18.scenes.json'), encoding='utf-8'))
ch = sorted(k for k in new if new[k] != old.get(k)); cn = {k: centre(new[k]) for k in new}; co = {k: centre(old[k]) for k in ch}
far = lambda m, lo: sorted(k for k in m if m[k][0] >= lo)
print('  다시 자른 장면 %d장:' % len(ch), ' '.join(ch)); print('  장합: %.2f(왼쪽 여백 %.2f · 오른쪽 %.2f) → %.2f(%.2f · %.2f)' % (co['zhanghe'] + cn['zhanghe']))
ok(len(new) == 265 and sorted(new) == sorted(old) and len(ch) == 24 and 'zhanghe' in ch, '큰 그림 265장 가운데 24장을 다시 잘랐다(장합 포함) — 나머지 241장은 0.18과 글자까지 같다')
ok(all(abs(cn[k][1] - cn[k][2]) < abs(co[k][1] - co[k][2]) - 0.03 for k in ch), '다시 자른 24장은 모두 좌우 여백의 차이가 줄었다')
allold = {k: centre(old[k]) for k in old}
ok(len(far(allold, 0.62)) == 6 and len(far(cn, 0.62)) == 0 and len(far(allold, 0.58)) == 22 and len(far(cn, 0.58)) == 5, '인물의 가로 중심이 0.62 넘는 그림 6 → 0장 · 0.58 넘는 그림 22 → 5장')
errs = [e for e in B.errors if 'GPU stall' not in e and 'GL Driver' not in e and 'ERR_FILE_NOT_FOUND' not in e and 'willReadFrequently' not in e]
print('console errors:', errs[:6])
print('FAILS %d' % len(fails), fails)
sys.exit(1 if fails or errs else 0)
