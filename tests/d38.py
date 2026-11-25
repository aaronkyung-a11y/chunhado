# v0.22.1 — 화면: 순찰의 소리 · 탭 아래의 붓 획 · 출진의 순서 · 이각의 초상 (요청 11-25 11:17 의 1 ~ 4번)
#   1) 순찰은 싸움용 발구름(step → stomp, 음높이 ±8%)이 아니라 딱따기(patrol → clack, 흔들림 없음)를 낸다. clack 이 풀리고(decode) 깨지지 않는다(0.98 을 넘는 점 없음).
#   2) 성 창의 탭: 고른 탭 아래의 줄이 곧은 줄(border 3px)이 아니라 붓 획(::after 의 그림)이다 — 붉은 점의 높이가 자리마다 다르다.
#   3) 출진: 부대가 나갈 칸에 먼저 서 있지 않는다.
#        · 내 출진: [출진]을 누른 바로 그때 그림은 성 안에 작고 옅게 있다. 끝나면 나갈 칸에 제 크기로.
#        · 지난 열흘의 출진(AI): 앞 장면이 도는 동안 그 부대는 보이지 않고, 출진 장면에서 성 안에서부터 나온다. 건너뛰어도 보이지 않는 채로 남지 않는다.
#   4) 이각의 흉상: 얼굴이 가운데 있다(왼쪽 3분의 1 이 흰 종이가 아니다).
#   python3 tests/d38.py          찍은 그림은 tests/shots38/h_*.png
import sys, os, io, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
import d2 as D2
from PIL import Image
B.SHOTS = os.path.join(B.ROOT, 'shots38')
os.makedirs(B.SHOTS, exist_ok=True)
fails = []
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)
def tapsel(pg, sel, nth=0, wait=350): pg.locator(sel).nth(nth).tap(); pg.wait_for_timeout(wait)
SLOW = 0.1
def steps(pg):
    B.start(pg, 0)
    ok(pg.evaluate('GAME_VERSION') == B.VER, '판 번호 ' + B.VER)
    pg.evaluate('() => { talkHide(); UI.talk = false; window.SFXLOG = []; var s0 = sfx; sfx = function (k) { SFXLOG.push(k); return s0(k); }; }')

    # ================= 1. 순찰의 소리 =================
    print('1. 순찰의 소리')
    c = pg.evaluate('() => ({ patrol: CUES.patrol, step: CUES.step, n: Object.keys(SFX_DATA).length, clack: typeof SFX_DATA.clack === "string" ? SFX_DATA.clack.length : 0, pat: typeof SFX_DATA.patrol === "string" ? SFX_DATA.patrol.length : 0 })')
    ok(c['patrol'] and c['patrol']['s'] == [['patrol', 0.85, 0]] and c['pat'] > 3000 and c['clack'] == 0 and c['n'] == 30, '순찰의 소리 patrol = 순라군의 발걸음(v0.25 — 0.22.1 의 딱따기 clack 은 뺐다), 음높이 흔들림 0 · 소리 30개(29 + patrol)')
    ok(c['step']['s'][0][0] == 'stomp' and c['step']['s'][0][2] == 0.08, '싸움의 발구름 step 은 그대로(stomp, ±8%)')
    d = pg.evaluate('''async () => { UI.sound = true; audioInit(); for (var i = 0; i < 60 && !(SND.buf.patrol && SND.buf.stomp); i++) await new Promise(function (r) { setTimeout(r, 100); });
      function S(k) { var b = SND.buf[k]; if (!b) return null; var d = b.getChannelData(0), pk = 0, n98 = 0, n10 = Math.floor(b.sampleRate * 0.01), run = 0, best = 0, j, i2;
        for (j = 0; j < d.length; j++) { var a = Math.abs(d[j]); if (a > pk) pk = a; if (a >= 0.98) n98++; }
        for (j = 0; j + n10 <= d.length; j += n10) { var m = 0; for (i2 = j; i2 < j + n10; i2++) if (Math.abs(d[i2]) > m) m = Math.abs(d[i2]); run = m > 0.35 * pk ? run + 1 : 0; if (run > best) best = run; }
        return { dur: +b.duration.toFixed(2), pk: +pk.toFixed(2), n98: n98, thick: best * 10, off: +(SND.off[k] || 0).toFixed(3) }; }
      return { clack: S('patrol'), stomp: S('stomp'), loaded: Object.keys(SND.buf).length }; }''')
    print('    ', d)
    ok(d['clack'] and 0.8 <= d['clack']['dur'] <= 1.2 and d['clack']['n98'] == 0 and d['clack']['pk'] <= 0.9, '순찰의 발걸음이 풀렸고 깨진 점이 없다(길이 %s초 · 봉우리 %s)' % (d['clack'] and d['clack']['dur'], d['clack'] and d['clack']['pk']))
    ok(d['clack']['thick'] <= 80 and d['stomp']['thick'] >= 150, '굵은 소리 덩어리: 순찰의 발걸음 %dms(걸음마다 짧게 끊긴다) · 처음에 쓰던 발구름 %dms' % (d['clack']['thick'], d['stomp']['thick']))
    pg.evaluate('() => { clearSel(); var b = facCities(G.player)[0]; b.order = 40; b.gold = 5000; baseOfficers(b).forEach(function (o) { o.acted = false; }); G.factions[G.player].ap = 300; selectBase(b, false, "home"); window.T = { b: b.id, order: b.order }; SFXLOG.length = 0; }')
    pg.wait_for_timeout(500)
    tapsel(pg, '#sheet [data-a=patrol]', 0, 500); tapsel(pg, '#modal [data-a=auto]', 0, 300); pg.evaluate('SFXLOG.length = 0'); tapsel(pg, '#modal [data-a=ok]', 0, 600)
    r = pg.evaluate('() => ({ log: SFXLOG.slice(), order: G.bases[T.b].order - T.order, modal: !!MODAL })')
    ok(r['order'] > 0 and 'patrol' in r['log'] and 'step' not in r['log'], '순찰을 실행하면 치안이 오르고(+%d) 딱따기가 난다 — 낸 소리 %s' % (r['order'], r['log']))

    # ================= 2. 탭 아래의 붓 획 =================
    print('2. 탭 아래의 붓 획')
    pg.evaluate('() => { talkHide(); if (MODAL) closeDialog(); selectBase(G.bases[T.b], false, "home"); }'); pg.wait_for_timeout(600)
    cs = pg.evaluate('''() => { var on = document.querySelector("#sheet .tabs button.on"), off = document.querySelector("#sheet .tabs button:not(.on)"), a = getComputedStyle(on, "::after"), c = getComputedStyle(on), a2 = getComputedStyle(off, "::after"), r = on.getBoundingClientRect();
      return { bg: a.backgroundImage.slice(0, 26), content: a.content, h: parseFloat(a.height), w: parseFloat(a.width), bw: r.width, bcol: c.borderBottomColor, offContent: a2.content, text: on.textContent, rect: [r.left, r.top, r.width, r.height], n: document.querySelectorAll("#sheet .tabs button").length }; }''')
    print('    ', cs)
    ok('data:image/svg' in cs['bg'] and cs['content'] != 'none' and cs['h'] >= 9 and 0.7 * cs['bw'] <= cs['w'] <= cs['bw'], '고른 탭(%s) 아래에 붓 획 그림이 있다(폭 %.0f / 탭 %.0f · 높이 %.0f)' % (cs['text'], cs['w'], cs['bw'], cs['h']))
    ok(cs['bcol'] in ('rgba(0, 0, 0, 0)', 'transparent') and cs['offContent'] == 'none', '곧은 줄(border)은 없고, 고르지 않은 탭에는 획이 없다')
    x, y, w, h = cs['rect']; dpr = pg.evaluate('devicePixelRatio')
    im = Image.open(io.BytesIO(pg.screenshot(clip={'x': x, 'y': y + h - 8, 'width': w, 'height': 22}))).convert('RGB'); W, H = im.size; px = im.load()
    cols = []
    for i in range(W):
        cols.append(sum(1 for j in range(H) if px[i, j][0] > 130 and px[i, j][0] - px[i, j][1] > 55 and px[i, j][0] - px[i, j][2] > 55))
    red = [c2 for c2 in cols if c2 > 0]; span = len(red) / float(W)
    print('     붉은 점: 열 %d / %d, 높이 %s ~ %s (화소 — 배율 %s)' % (len(red), W, min(red) if red else 0, max(red) if red else 0, dpr))
    ok(red and 0.5 <= span <= 0.98 and max(red) - min(red) >= 3 * dpr, '붉은 줄의 굵기가 자리마다 다르다(붓 획) — 가장 가는 곳 %d · 가장 굵은 곳 %d 화소, 탭 폭의 %d%%' % (min(red) if red else 0, max(red) if red else 0, span * 100))
    pg.screenshot(path=os.path.join(B.SHOTS, 'h_tabs.png'), clip={'x': 0, 'y': y - 10, 'width': pg.viewport_size['width'], 'height': h + 34})
    tapsel(pg, '#sheet .tabs button', 1, 500)
    cs2 = pg.evaluate('() => { var on = document.querySelector("#sheet .tabs button.on"); return [on.textContent, getComputedStyle(on, "::after").content !== "none", document.querySelectorAll("#sheet .tabs button.on").length]; }')
    ok(cs2[1] and cs2[2] == 1 and cs2[0] != cs['text'], '다른 탭(%s)을 누르면 획이 그 탭으로 옮겨 간다' % cs2[0])

    # ================= 3. 출진의 순서 =================
    print('3. 출진의 순서 — 내 출진')
    PROBE = '''(id) => { var o = R3.units[id], u = UMAP[id], b = G.bases[T.b]; if (!o || !u) return null; var pc = hexPos(b.c, b.r), pu = hexPos(u.c, u.r), p = o.g.position, D = Math.hypot(pu[0] - pc[0], pu[2] - pc[2]);
      return { fromCastle: +(Math.hypot(p.x - pc[0], p.z - pc[2]) / D).toFixed(2), op: +o.sp.material.opacity.toFixed(2), sc: +(o.sp.scale.x / o.sp.userData.w).toFixed(2), vis: o.g.visible ? 1 : 0, anim: !!o.anim, busy: !!UI.busy }; }'''
    pg.evaluate('''() => { talkHide(); clearSel(); var b = G.bases[T.b]; b.troops = 30000; b.food = 90000; b.w.spear = 9000; baseOfficers(b).forEach(function (o) { o.acted = false; }); G.factions[G.player].ap = 300; selectBase(b, false, "mil"); T.n0 = G.units.length; T.ids = G.units.map(function (u) { return u.id; }); flowDeploy(b); }''')
    pg.wait_for_timeout(600)
    tapsel(pg, '#modal [data-a=type][data-v=spear]'); tapsel(pg, '#modal .rows .row', 0); tapsel(pg, '#modal [data-a=next]', 0, 700)
    pg.evaluate(D2.SLOWJS, SLOW)
    pg.evaluate('''() => { window.FIRST = null; var f0 = fxDeploy; fxDeploy = function (u, b, done) { var r = f0(u, b, done); var o = R3.units[u.id]; T.u = u.id;
      if (o) { var pc = hexPos(b.c, b.r), pu = hexPos(u.c, u.r), p = o.g.position; FIRST = { fromCastle: +(Math.hypot(p.x - pc[0], p.z - pc[2]) / Math.hypot(pu[0] - pc[0], pu[2] - pc[2])).toFixed(2), op: +o.sp.material.opacity.toFixed(2), sc: +(o.sp.scale.x / o.sp.userData.w).toFixed(2) }; } return r; }; }''')
    tapsel(pg, '#modal [data-a=ok]', 0, 60)
    first = pg.evaluate('FIRST'); uid = pg.evaluate('T.u')
    seq = [pg.evaluate(PROBE, uid)]
    pg.wait_for_timeout(120 / SLOW); seq.append(pg.evaluate(PROBE, uid))
    pg.wait_for_function('() => !UI.busy && UI.anims.length === 0', timeout=120000); pg.wait_for_timeout(1200)
    fin = pg.evaluate(PROBE, uid)
    print('     거는 순간', first); [print('     ', json.dumps(x)) for x in seq]; print('     끝', fin)
    ok(first and first['fromCastle'] <= 0.02 and first['op'] <= 0.25 and first['sc'] <= 0.56, '[출진]을 누른 바로 그때(연출을 건 같은 자리에서): 그림은 성 안에 작고(%s배) 옅게(%s) 있다' % (first and first['sc'], first and first['op']))
    ok(seq[0] and seq[0]['fromCastle'] < 0.6 and seq[0]['anim'] and seq[1]['fromCastle'] < 1.0 and seq[1]['fromCastle'] >= seq[0]['fromCastle'], '그 뒤로 성에서 나갈 칸 쪽으로 걸어 나온다(%s → %s)' % (seq[0] and seq[0]['fromCastle'], seq[1] and seq[1]['fromCastle']))
    ok(fin and fin['fromCastle'] == 1.0 and fin['sc'] == 1.0 and fin['op'] == 1.0 and not fin['anim'] and not fin['busy'], '끝나면 나갈 칸에 제 크기 · 제 빛으로 선다')
    pg.screenshot(path=os.path.join(B.SHOTS, 'h_deploy.png'))

    print('3. 출진의 순서 — 지난 열흘의 출진(AI)')
    a = pg.evaluate('''() => { talkHide(); clearSel(); hideSheet(); if (MODAL) closeDialog();
      var E = G.bases.filter(function (b) { return b.owner >= 0 && b.owner !== G.player && b.kind === 'city' && idleOfficers(b).length >= 2; })[0]; E.troops = 30000; E.food = 90000; E.w.spear = 9000; G.factions[E.owner].ap = 300;
      var mv = G.units.filter(function (u) { return u.id === T.u; })[0];
      UI.play = { next: null, skip: false, cam0: { x: cam.x, y: cam.y, z: cam.z }, timer: 0, wake: null, ans: [], batch: [], err: null, minor: 0, shown: 0, save0: null }; UI.busy = true; $('app').classList.add('playing');
      EVQ.length = 0;
      var r = cmdDeploy(E, { type: 'spear', ids: [idleOfficers(E)[0].id], troops: 3000, food: 900 }); if (!r.ok) return { err: r.msg };
      var X = r.unit, bb = G.bases[T.b], evs = EVQ.splice(0, EVQ.length);
      // 앞에 다른 장면 하나(소식)를 둔다 — 그 장면이 도는 동안 막 출진한 부대가 보이면 안 된다
      evs.unshift({ t: 'news', f: E.owner, c: E.c, r: E.r, text: '시험: 앞 장면' });
      evs.forEach(function (e) { e.cls = 2; }); evs.forEach(function (e) { holdEv(e); });
      window.PB = { done: false, x: X.id, e: E.id }; presentEvents(evs, function () { PB.done = true; });
      return { evs: evs.map(function (e) { return e.t; }), x: X.id, at: [X.c, X.r], base: E.n }; }''')
    print('    ', a)
    ok(not a.get('err') and a['evs'] == ['news', 'deploy'], '장면의 차례: 앞 장면(소식) → %s 의 출진' % a.get('base'))
    PR = '''() => { var o = R3.units[PB.x], u = UMAP[PB.x], b = G.bases[PB.e]; if (!o) return { none: 1 }; var pc = hexPos(b.c, b.r), pu = hexPos(u.c, u.r), p = o.g.position;
      return { vis: o.g.visible ? 1 : 0, ring: o.ring.visible ? 1 : 0, wait: !!o.wait, fromCastle: +(Math.hypot(p.x - pc[0], p.z - pc[2]) / Math.hypot(pu[0] - pc[0], pu[2] - pc[2])).toFixed(2), sc: +(o.sp.scale.x / o.sp.userData.w).toFixed(2), op: +o.sp.material.opacity.toFixed(2), cap: $('plMsg').textContent.slice(0, 24), done: PB.done }; }'''
    s1 = pg.evaluate(PR); pg.wait_for_timeout(60 / SLOW); s2 = pg.evaluate(PR)
    pg.wait_for_function('''() => { var o = R3.units[PB.x]; return (o && o.g.visible) || PB.done; }''', timeout=120000); s3 = pg.evaluate(PR)
    pg.screenshot(path=os.path.join(B.SHOTS, 'h_ai_deploy.png'))
    pg.wait_for_function('() => PB.done && UI.anims.length === 0', timeout=180000); pg.wait_for_timeout(900)      # 늦춘 시계에서는 장면의 기다림(실제 시간)이 걸음(늦춘 시간)보다 먼저 끝난다 → 걸음이 끝날 때까지
    fin = pg.evaluate(PR)
    [print('     ', json.dumps(x, ensure_ascii=False)) for x in (s1, s2, s3)]; print('      끝', json.dumps(fin, ensure_ascii=False))
    ok(s1.get('vis') == 0 and s1.get('ring') == 0 and s2.get('vis') == 0 and '앞 장면' in s2.get('cap', ''), '앞 장면이 도는 동안 막 출진한 부대는 보이지 않는다(전에는 나갈 칸에 먼저 서 있었다)')
    ok(s3.get('vis') == 1 and s3['fromCastle'] <= 0.35 and s3['sc'] < 0.8 and '출진' in s3['cap'], '출진 장면에서 성 안에서부터 작게 나온다(성에서 %s · 크기 %s배)' % (s3.get('fromCastle'), s3.get('sc')))
    ok(fin.get('vis') == 1 and fin['fromCastle'] == 1.0 and fin['sc'] == 1.0 and fin['op'] == 1.0 and fin['done'], '장면이 끝나면 나갈 칸에 제 크기로 선다')
    # 건너뛰기: 출진 장면이 나오기 전에 끝내도 보이지 않는 채로 남지 않는다
    b2 = pg.evaluate('''() => { var E = G.bases[PB.e]; baseOfficers(E).forEach(function (o) { if (!o.unit && o.unit !== 0) o.acted = false; }); G.factions[E.owner].ap = 300; EVQ.length = 0;
      var r = cmdDeploy(E, { type: 'spear', ids: [idleOfficers(E)[0].id], troops: 3000, food: 900 }); if (!r.ok) return { err: r.msg };
      var evs = EVQ.splice(0, EVQ.length); evs.unshift({ t: 'news', f: E.owner, c: E.c, r: E.r, text: '시험: 앞 장면' }); evs.forEach(function (e) { e.cls = 2; }); evs.forEach(function (e) { holdEv(e); });
      PB.done = false; PB.x = r.unit.id; presentEvents(evs, function () { PB.done = true; }); var o = R3.units[PB.x]; var hid = o ? [o.g.visible ? 1 : 0, !!o.wait] : null;
      UI.play.skip = true; if (UI.play.wake) UI.play.wake(); return { hid: hid }; }''')
    pg.wait_for_function('() => PB.done', timeout=60000); pg.wait_for_timeout(400)
    b3 = pg.evaluate('''() => { var o = R3.units[PB.x]; var r = o ? [o.g.visible ? 1 : 0, o.ring.visible ? 1 : 0, !!o.wait, !!o.anim] : null; UI.play = null; UI.busy = false; $('app').classList.remove('playing'); clearAnimFlags(); requestDraw(); return r; }''')
    print('     건너뛰기', b2, b3)
    ok(b2.get('hid') == [0, True] and b3 == [1, 1, False, False], '건너뛰면: 숨겨 둔 부대가 바로 보이고 붙잡아 둔 표시가 남지 않는다')

    # ================= 4. 이각의 흉상 =================
    print('4. 이각의 흉상')
    f = pg.evaluate('''async () => { function load(u) { return new Promise(function (res) { var im = new Image(); im.onload = function () { res(im); }; im.onerror = function () { res(null); }; im.src = u; }); }
      var out = {}, ks = ['lijue', 'guosi'];
      for (var i = 0; i < ks.length; i++) { var im = await load(POR_URL[ks[i]]); if (!im) { out[ks[i]] = null; continue; } var c = document.createElement('canvas'); c.width = im.naturalWidth; c.height = im.naturalHeight; var x = c.getContext('2d'); x.drawImage(im, 0, 0);
        var d = x.getImageData(0, 0, c.width, c.height).data, W = c.width, H = c.height, wl = 0, wr = 0, nl = 0, nr = 0;
        for (var yy = 0; yy < H; yy++) for (var xx = 0; xx < W; xx++) { var k = (yy * W + xx) * 4, white = d[k] > 240 && d[k + 1] > 240 && d[k + 2] > 240; if (xx < W / 3) { nl++; if (white) wl++; } else if (xx >= W * 2 / 3) { nr++; if (white) wr++; } }
        out[ks[i]] = { w: W, h: H, whiteL: +(wl / nl).toFixed(2), whiteR: +(wr / nr).toFixed(2) }; }
      return out; }''')
    print('    ', f)
    ok(f['lijue'] and f['lijue']['w'] == 256 and f['lijue']['whiteL'] < 0.45, '이각의 흉상: 왼쪽 3분의 1 에서 흰 종이의 몫 %s (0.22 까지는 0.6 을 넘었다 — 얼굴이 오른쪽 끝에 있었다)' % (f['lijue'] and f['lijue']['whiteL']))
B.run(steps, 393, 852, 2)
errs = [e for e in B.errors if 'ReadPixels' not in e and 'ERR_FILE' not in e and 'GPU stall' not in e and 'AudioContext' not in e]
print('오류 기록:', errs[:6])
ok(not errs, '오류 · 경고 기록이 없다(%d건)' % len(errs))
print('\nd38: %d fail' % len(fails))
for f in fails: print('  ✗', f)
sys.exit(1 if fails else 0)
