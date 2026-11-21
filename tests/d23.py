# v0.12 — 화면 조작으로 확인: 세이브 파일 보내기 · 가져오기 · 시설 칸에 서기 · 발밑의 시설 치기 · 전법 실패의 풀이 · 쏘는 소리의 큐 · 나갈 자리 · 아래에 더 있다는 표시
#   python3 tests/d23.py          찍은 그림은 tests/shots25/
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import taphex, tapsel
B.SHOTS = os.path.join(B.ROOT, 'shots25')
os.makedirs(B.SHOTS, exist_ok=True)
fails = []
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)
def toast(pg): return pg.evaluate('$("toast").textContent')
def head(pg): return pg.evaluate('MODAL ? document.querySelector("#modal .dlg-h").textContent.replace("×", "") : ""')
def reload(pg):
    pg.reload(); pg.wait_for_function('window.R3 && R3.ready', timeout=60000); pg.wait_for_timeout(600)
def fresh(pg, fac, seed):
    pg.evaluate('([f, s]) => { localStorage.clear(); newGame(f, s); saveGame(); }', [fac, seed]); reload(pg)
    tapsel(pg, '#tCont'); pg.wait_for_timeout(1300)
    if pg.evaluate('!!MODAL'): pg.evaluate('closeDialog()')
    pg.evaluate('talkHide()'); pg.wait_for_timeout(200)
SLOTS = '(() => { var o = {}; slotIds().forEach(function (id) { var m = slotInfo(id); o[id] = m ? (m.bad ? "bad" : m.f + "|" + m.d) : null; }); return o; })()'
ROWS = '''Array.prototype.map.call(document.querySelectorAll('#modal .rows.svl .row'), function (e) { return e.getAttribute('data-slot'); })'''
FACSET = '''(() => {
  var b = facCities(G.player)[0]; b.troops = 60000; b.food = 200000; b.w.spear = 30000; G.factions[G.player].ap = 255;
  for (var i = 0; i < b.plots.length; i++) if (!b.plots[i].fac) b.plots[i].fac = { t: 'market', lv: 1, done: true, prog: 0, need: 0, rate: 0, hp: FAC_HP };
  var os = idleOfficers(b).filter(function (o) { return !isLord(o); }), units = [];
  var ring = nbrs(b.c, b.r).filter(function (q) { var t = terr(q[0], q[1]); return t !== 'm' && t !== 's' && t !== 'x'; });
  var free = ring.filter(function (q) { return !PAT[K(q[0], q[1])]; }).length;
  for (i = 0; i < free + 1 && i < os.length; i++) { var x = cmdDeploy(b, { type: 'spear', ids: [os[i].id], troops: 2000, food: 2000 }); if (x.ok) units.push(x.unit.id); }
  var last = UMAP[units[units.length - 1]], pf = PAT[K(last.c, last.r)];
  units.forEach(function (id) { var u = UMAP[id]; u.done = false; u.mp = uMaxMp(u); u.born = -9; });
  EVQ.length = 0; clearSel(); syncScene(); jumpTo(b.c, b.r, 1.6); requestDraw();
  return { b: b.id, free: free, ring: ring.length, n: units.length, last: last.id, onFac: !!(pf && pf.b === b.id && b.plots[pf.i].fac), pi: pf ? pf.i : -1, units: units };
})()'''
def steps(pg):
    # ================= 1. 저장이 없는 제목 화면 =================
    print('1. 제목 화면')
    pg.evaluate('localStorage.clear()'); reload(pg)
    t0 = pg.evaluate('[$("tCont").disabled, $("tLoad").disabled, $("tVer").textContent]')
    ok(t0[0] is True and t0[1] is False and t0[2].startswith('v0.13'), '저장이 없어도 [불러오기]가 열린다 · 판 번호 %s' % t0)
    tapsel(pg, '#tLoad'); pg.wait_for_timeout(400)
    v = pg.evaluate('({ t: document.querySelector("#modal").textContent, imp: !!document.querySelector("#modal [data-a=simport]"), paste: !!document.querySelector("#modal [data-a=spaste]") })')
    ok(head(pg) == '불러오기' and '저장된 판이 없습니다' in v['t'] and v['imp'] and v['paste'], '불러오기 창: 빈 알림 + [파일에서 가져오기] · [붙여넣기로 가져오기]')
    B.shot(pg, 'v1_title_load', 200)
    pg.evaluate('closeDialog()')
    tapsel(pg, '#tShare'); pg.wait_for_timeout(400)
    ok(head(pg) == '공유' and pg.evaluate('!!document.querySelector("#modal [data-a=savesend]")') and '하던 판 보내기' in pg.evaluate('document.querySelector("#modal").textContent'), '공유 창: [세이브 파일 보내기]')
    B.shot(pg, 'v1_share', 200)
    tapsel(pg, '#modal [data-a=savesend]'); pg.wait_for_timeout(400)
    ok(head(pg) == '세이브 파일 보내기' and '저장된 판이 없습니다' in pg.evaluate('document.querySelector("#modal").textContent'), '저장이 없으면 보낼 판이 없다고 알린다')
    pg.evaluate('backDialog()'); pg.wait_for_timeout(200)
    ok(head(pg) == '공유', '닫으면 공유 창으로 돌아온다')
    pg.evaluate('closeDialog()')

    # ================= 2. 세이브 파일 보내기 =================
    print('2. 세이브 파일 보내기')
    fresh(pg, 13, 4242)
    pg.evaluate('(() => { endTurn(); EVQ.length = 0; REPORT.length = 0; saveTo("s2"); })()'); pg.wait_for_timeout(300)
    if pg.evaluate('!!MODAL'): pg.evaluate('closeDialog()')
    s2 = pg.evaluate('localStorage.getItem("chunhado_save_v2_s2")')
    pg.evaluate('showMenu()'); pg.wait_for_timeout(300); tapsel(pg, '#modal [data-a=share]'); pg.wait_for_timeout(400)
    tapsel(pg, '#modal [data-a=savesend]'); pg.wait_for_timeout(400)
    rows = pg.evaluate(ROWS); txt = pg.evaluate('document.querySelector("#modal").textContent')
    ok(rows[0] == 'auto' and 's2' in rows and '자동 = 지금 하는 판' in txt.replace('\\n', ' '), '보낼 판 고르기: %s' % rows)
    ok(pg.evaluate('localStorage.getItem("chunhado_save_v2") === serialize()'), '창을 열 때 지금 모습이 자동 저장에 적힌다')
    B.shot(pg, 'v2_pick', 200)
    tapsel(pg, '#modal [data-slot=s2] [data-a=spick]'); pg.wait_for_timeout(300)
    b2 = pg.evaluate('({ share: !!document.querySelector("#modal [data-a=sshare]"), down: document.querySelector("#modal [data-a=sdown]").innerText.replace(/\\n+/g, " | "), downPri: document.querySelector("#modal [data-a=sdown]").classList.contains("pri"), copy: !!document.querySelector("#modal [data-a=scopy]"), note: document.querySelector("#modal .note").textContent })')
    ok(not b2['share'] and b2['downPri'] and b2['copy'] and '천하도_왕랑_194년1월중순.txt' in b2['down'] and '실을 수 없어' in b2['note'], '공유 창이 파일을 못 받는 곳: [파일로 저장] · [글자로 복사]만 %s' % b2)
    B.shot(pg, 'v2_send_nofile', 200)
    with pg.expect_download() as dl: tapsel(pg, '#modal [data-a=sdown]')
    d = dl.value; path = os.path.join(B.SHOTS, 'save_s2.txt'); d.save_as(path); text = open(path, encoding='utf-8').read(); lines = text.split('\n')
    ok(d.suggested_filename == '천하도_왕랑_194년1월중순.txt' and lines[0].startswith('삼국지 천하도 세이브 — 왕랑 · 194년 1월 중순') and 'v0.13' in lines[0] and 'aaronkyung-a11y.github.io/chunhado' in lines[1] and '파일에서 가져오기' in lines[1], '파일 이름 · 머리말 두 줄: %s / %s' % (d.suggested_filename, lines[:2]))
    ok(lines[2] == s2 and len(lines) == 4 and lines[3] == '', '셋째 줄이 저장본 그대로다(%d자)' % len(s2))
    # 글자로 복사
    pg.evaluate('(() => { window._clip = null; try { Object.defineProperty(navigator, "clipboard", { value: { writeText: function (t) { window._clip = t; return Promise.resolve(); } }, configurable: true }); } catch (e) { window._clipErr = String(e); } })()')
    tapsel(pg, '#modal [data-a=scopy]'); pg.wait_for_timeout(300)
    ok(pg.evaluate('window._clip') == text and '복사' in toast(pg), '[글자로 복사]: 같은 글이 복사된다 — ' + toast(pg))
    # 공유 창이 파일을 받는 기기
    pg.evaluate('''(() => { navigator.canShare = function (d) { return !!(d && d.files && d.files.length === 1); };
      navigator.share = function (d) { window._shd = { title: d.title, text: d.text, name: d.files[0].name, type: d.files[0].type, size: d.files[0].size }; return d.files[0].text().then(function (t) { window._sht = t; }); }; refreshDialog(); })()''')
    pg.wait_for_timeout(200)
    b3 = pg.evaluate('({ share: !!document.querySelector("#modal [data-a=sshare].pri"), downPri: document.querySelector("#modal [data-a=sdown]").classList.contains("pri"), note: document.querySelector("#modal .note").textContent })')
    ok(b3['share'] and not b3['downPri'] and '실을 수 없어' not in b3['note'], '공유 창이 파일을 받는 기기: [보내기]가 첫째 단추 %s' % b3)
    B.shot(pg, 'v2_send', 200)
    tapsel(pg, '#modal [data-a=sshare]'); pg.wait_for_timeout(500)
    sd = pg.evaluate('window._shd')
    ok(sd and sd['name'] == '천하도_왕랑_194년1월중순.txt' and sd['type'].startswith('text/plain') and pg.evaluate('window._sht') == text and '불러오기' in sd['text'] and 'chunhado' in sd['text'], '[보내기]: 공유 창에 파일(.txt · text/plain)과 여는 법이 간다 %s' % sd)
    tapsel(pg, '#modal [data-a=sback]'); pg.wait_for_timeout(200)
    ok(len(pg.evaluate(ROWS)) == len(rows), '[다른 판]: 고르는 줄로 돌아간다')
    pg.evaluate('closeDialog()')

    # ================= 3. 가져오기 =================
    print('3. 가져오기')
    snap = pg.evaluate('JSON.stringify([G.turn, G.player, G.year, G.month, G.xun, G.units.length, G.bases.map(function (b) { return [b.owner, b.troops, b.gold, b.food]; }), G.officers.map(function (o) { return [o.f, o.loy, o.b]; })])')
    reload(pg); pg.evaluate('localStorage.clear()'); reload(pg)          # 받는 쪽: 저장이 하나도 없는 기기(게임 중에 떠나면 자동 저장이 남으므로 제목 화면에서 비운다)
    tapsel(pg, '#tLoad'); pg.wait_for_timeout(400)
    with pg.expect_file_chooser() as fc: tapsel(pg, '#modal [data-a=simport]')
    fc.value.set_files(path); pg.wait_for_timeout(900)
    sl = pg.evaluate(SLOTS); rows = pg.evaluate(ROWS)
    ok(sl['s1'] == '왕랑|194년 1월 중순' and sl['auto'] is None and rows == ['s1'] and '1번 칸에 넣었습니다' in toast(pg), '[파일에서 가져오기]: 첫 빈 칸(1번)에 들어간다 — ' + toast(pg) + ' %s %s' % (sl, rows))
    ok(pg.evaluate('localStorage.getItem("chunhado_save_v2_s1")') == s2 and pg.evaluate('!G || $("title").classList.contains("off") === false'), '넣은 저장본이 보낸 것과 글자까지 같고, 제목 화면 그대로다')
    B.shot(pg, 'v3_imported', 200)
    tapsel(pg, '#modal [data-slot=s1] [data-a=sload]'); pg.wait_for_timeout(1600)
    if pg.evaluate('!!MODAL'): pg.evaluate('closeDialog()')
    snap2 = pg.evaluate('JSON.stringify([G.turn, G.player, G.year, G.month, G.xun, G.units.length, G.bases.map(function (b) { return [b.owner, b.troops, b.gold, b.food]; }), G.officers.map(function (o) { return [o.f, o.loy, o.b]; })])')
    ok(snap2 == snap and pg.evaluate('$("title").classList.contains("off")'), '가져온 판을 불러오면 보낸 쪽의 판과 같다(턴 · 거점 · 무장)')
    # 붙여넣기로
    pg.evaluate('showSaves("load")'); pg.wait_for_timeout(300); tapsel(pg, '#modal [data-a=spaste]'); pg.wait_for_timeout(300)
    ok(head(pg) == '붙여넣기로 가져오기', '붙여넣기 창')
    tapsel(pg, '#modal [data-a=take]'); pg.wait_for_timeout(200)
    ok('붙여 넣은 글이 없습니다' in toast(pg) and head(pg) == '붙여넣기로 가져오기', '빈 칸으로 [가져오기]: 알리고 그대로')
    pg.fill('#svTa', text); B.shot(pg, 'v3_paste', 200)
    tapsel(pg, '#modal [data-a=take]'); pg.wait_for_timeout(700)
    sl = pg.evaluate(SLOTS)
    ok(sl['s2'] == '왕랑|194년 1월 중순' and '2번 칸에 넣었습니다' in toast(pg) and head(pg).startswith('저장') and 's2' in pg.evaluate(ROWS), '[붙여넣기로 가져오기]: 다음 빈 칸(2번) — ' + toast(pg))
    pg.evaluate('closeDialog()')
    # 받지 않는 글: 하던 판과 저장 칸은 그대로
    g0 = pg.evaluate('serialize()'); sl0 = pg.evaluate(SLOTS)
    bads = pg.evaluate('''(text) => {
      var body = text.split('\\n')[2], out = [], g;
      function tryIt(name, t) { $('toast').textContent = ''; flowImport(t); out.push([name, $('toast').textContent, !!MODAL && document.querySelector('#modal .dlg-h').textContent]); if (MODAL) closeDialog(); }
      tryIt('글자 몇 자', '안녕하세요');
      tryIt('다른 JSON', '{"a":1,"b":[1,2,3]}');
      tryIt('끊긴 파일', text.slice(0, Math.floor(text.length / 2)));
      g = JSON.parse(body); g.officers[3].n = '<img src=x onerror=alert(1)>'; tryIt('꺾쇠가 든 이름', JSON.stringify(g));
      g = JSON.parse(body); g.factions[0].name = 'a" onmouseover="x'; tryIt('따옴표가 든 세력 이름', JSON.stringify(g));
      g = JSON.parse(body); g.factions[1].color = 'red;background:url(x)'; tryIt('색이 아닌 색', JSON.stringify(g));
      g = JSON.parse(body); g.ver = 1; tryIt('다른 판의 저장', JSON.stringify(g));
      g = JSON.parse(body); g.bases = [{ n: 'x' }]; tryIt('열리지 않는 저장', JSON.stringify(g));
      g = JSON.parse(body); g.units.push({ id: 999, f: 0, c: 5, r: 5, type: 'spear', off: [99999], troops: 100 }); tryIt('없는 무장이 이끄는 부대', JSON.stringify(g));
      g = JSON.parse(body); g.bases[3].owner = 77; tryIt('없는 세력의 거점', JSON.stringify(g));
      g = JSON.parse(body); g.log.push({ d: 'x', t: new Array(900).join('가'), c: 0, r: 0, f: 0, imp: 0 }); tryIt('지나치게 긴 글', JSON.stringify(g));
      return out;
    }''', text)
    for b_ in bads: print('     ', b_)
    ok(all(b_[1] and '넣었습니다' not in b_[1] and not b_[2] for b_ in bads) and len(bads) == 11, '받지 않는 글 열한 가지: 모두 까닭을 알리고 넣지 않는다')
    ok('아닙니다' in bads[0][1] and '아닙니다' in bads[1][1] and ('끊겼' in bads[2][1] or '아닙니다' in bads[2][1]) and all('알 수 없는 내용' in bads[i][1] for i in (3, 4, 5, 10)) and '아닙니다' in bads[6][1] and all('열 수 없는' in bads[i][1] for i in (7, 8, 9)), '까닭이 맞게 나온다')
    ok(pg.evaluate('serialize()') == g0 and pg.evaluate(SLOTS) == sl0 and pg.evaluate('G.units.every(function (u) { return UAT[K(u.c, u.r)] === u; }) && !document.querySelector("img[src=x]")'), '하던 판 · 저장 칸은 그대로, 받은 글은 화면에 찍히지 않는다')
    # 깨진 저장을 불러오다 실패해도 하던 판은 그대로(고침)
    pg.evaluate('(() => { var g = JSON.parse(localStorage.getItem("chunhado_save_v2_s1")); g.officers = null; localStorage.setItem("chunhado_save_v2_s5", JSON.stringify(g)); })()')
    lf = pg.evaluate('(g0) => [loadFrom("s5"), serialize() === g0, G.units.every(function (u) { return UAT[K(u.c, u.r)] === u; })]', g0)
    ok(lf == [False, True, True], '깨진 저장을 불러오면 실패하고 하던 판이 그대로 남는다 %s' % lf)
    pg.evaluate('slotDrop("s5")')
    # 빈 칸이 없을 때: 덮어쓸 칸을 고른다(두 번 눌러야)
    pg.evaluate('(() => { for (var i = 1; i <= SAVE_SLOTS; i++) saveTo("s" + i); })()')
    pg.evaluate('(t) => { flowImport(t); }', text); pg.wait_for_timeout(400)
    ok(head(pg) == '넣을 칸 고르기' and len(pg.evaluate(ROWS)) == 6, '빈 칸이 없으면 덮어쓸 칸을 고르게 한다')
    B.shot(pg, 'v3_overwrite', 200)
    before = pg.evaluate('localStorage.getItem("chunhado_save_v2_s3")')
    tapsel(pg, '#modal [data-slot=s3] [data-a=over]'); pg.wait_for_timeout(300)
    ok(pg.evaluate('localStorage.getItem("chunhado_save_v2_s3")') == before and '정말 덮어쓰기' in pg.evaluate('document.querySelector("#modal [data-slot=s3] [data-a=over]").textContent'), '한 번 누르면 되묻는다')
    tapsel(pg, '#modal [data-slot=s3] [data-a=over]'); pg.wait_for_timeout(400)
    ok(pg.evaluate('localStorage.getItem("chunhado_save_v2_s3")') == s2 and '3번 칸에 넣었습니다' in toast(pg) and not pg.evaluate('!!MODAL'), '두 번째에 덮어쓴다 — ' + toast(pg))

    # ================= 4. 시설 칸에 서기 =================
    print('4. 시설')
    fresh(pg, 0, 1)
    F = pg.evaluate(FACSET); print('     ', F)
    ok(F['n'] == F['free'] + 1 and F['onFac'], '성 둘레의 빈 땅 %d칸이 다 찬 뒤의 부대는 시설 칸으로 나간다(v0.11: "성 밖에 나갈 자리가 없습니다")' % F['free'])
    pg.wait_for_timeout(500)
    op = pg.evaluate('(F) => { var b = G.bases[F.b], o = [], on = R3.facs[F.b + ":" + F.pi].sp.material.opacity; for (var j = 0; j < b.plots.length; j++) if (j !== F.pi && b.plots[j].fac && !UAT[K(b.plots[j].c, b.plots[j].r)]) o.push(R3.facs[F.b + ":" + j].sp.material.opacity); return [on, Math.min.apply(null, o), Math.max.apply(null, o)]; }', F)
    ok(abs(op[0] - 0.38) < 0.01 and op[1] == 1 and op[2] == 1, '부대가 올라선 시설은 흐리게(%.2f), 나머지는 또렷하게' % op[0])
    B.shot(pg, 'v4_on_facility', 300)
    # 누르기: 고른 부대의 이동 범위에 든 내 시설 칸을 누르면 그리로 간다(창이 뜨지 않는다)
    m = pg.evaluate('''(F) => { var u = UMAP[F.units[0]], b = G.bases[F.b]; selectUnit(u, true); var rc = UI.rc, hit = null;
      for (var j = 0; j < b.plots.length && !hit; j++) { var p = b.plots[j], k = K(p.c, p.r); if (p.fac && !UAT[k] && rc && rc.stop[k]) hit = [p.c, p.r, j]; }
      return { u: u.id, hit: hit, nFac: b.plots.filter(function (p) { return p.fac && rc && rc.stop[K(p.c, p.r)]; }).length }; }''', F)
    ok(m['hit'] is not None and m['nFac'] >= 1, '이동 범위(파란 칸)에 내 시설 칸이 들어 있다: %d칸' % m['nFac'])
    pg.wait_for_timeout(400); B.shot(pg, 'v4_reach', 200)
    taphex(pg, m['hit'][0], m['hit'][1]); pg.wait_for_timeout(1800)
    at = pg.evaluate('(m) => { var u = UMAP[m.u]; return [u.c, u.r, !!MODAL, R3.facs[G.bases[%d].id + ":" + m.hit[2]].sp.material.opacity]; }' % F['b'], m)
    ok(at[0] == m['hit'][0] and at[1] == m['hit'][1] and not at[2] and abs(at[3] - 0.38) < 0.01, '시설 칸을 누르면 그리로 움직인다 %s' % at)
    # 고른 부대가 없을 때 내 시설을 누르면 전처럼 시설 창
    free_fac = pg.evaluate('(F) => { clearSel(); var b = G.bases[F.b]; for (var j = 0; j < b.plots.length; j++) { var p = b.plots[j]; if (p.fac && !UAT[K(p.c, p.r)]) return [p.c, p.r, FAC[p.fac.t].name]; } return null; }', F)
    pg.wait_for_timeout(300); taphex(pg, free_fac[0], free_fac[1]); pg.wait_for_timeout(500)
    ok(pg.evaluate('!!MODAL') and free_fac[2] in head(pg), '고른 부대가 없으면 내 시설을 눌러 시설 창이 뜬다(전과 같다) — ' + head(pg))
    pg.evaluate('closeDialog()')
    # 남의 시설: 옆 칸에서 누르면 대상 창([시설 파괴] · [이 칸으로 이동]) → 올라서서 [시설 파괴]
    E = pg.evaluate('''(F) => {
      var u = UMAP[F.units[0]], eb = null, i;
      for (i = 0; i < G.bases.length && !eb; i++) { var q = G.bases[i]; if (q.owner > 0 && q.plots && q.plots.length >= 3) eb = q; }
      for (i = 0; i < eb.plots.length; i++) if (!eb.plots[i].fac) eb.plots[i].fac = { t: 'farm', lv: 1, done: true, prog: 0, need: 0, rate: 0, hp: FAC_HP };
      var ep = null, side = null;
      for (i = 0; i < eb.plots.length && !side; i++) { var p = eb.plots[i], t = terr(p.c, p.r); if (t === 'm' || t === 's' || t === 'x' || t === 'w' || UAT[K(p.c, p.r)]) continue;
        var ns = nbrs(p.c, p.r).filter(function (n) { var t2 = terr(n[0], n[1]), kk = K(n[0], n[1]); return (t2 === 'p' || t2 === 'g' || t2 === 'h') && !UAT[kk] && BAT[kk] === undefined && !PAT[kk]; });
        if (ns.length) { ep = p; side = ns[0]; } }
      placeUnit(u, side[0], side[1]); u.done = false; u.mp = uMaxMp(u); u.born = -9; u.ox = -1; u.morale = 100;
      EVQ.length = 0; clearSel(); syncScene(); jumpTo(ep.c, ep.r, 1.6); selectUnit(u, true); requestDraw();
      return { u: u.id, eb: eb.id, ebn: eb.n, ep: [ep.c, ep.r], pi: eb.plots.indexOf(ep), hp: ep.fac.hp, fn: FAC[ep.fac.t].name };
    }''', F)
    pg.wait_for_timeout(700)
    taphex(pg, E['ep'][0], E['ep'][1]); pg.wait_for_timeout(500)
    tg = pg.evaluate('({ kind: UI.target ? UI.target.kind : null, acts: Array.prototype.map.call(document.querySelectorAll("#sheet .acts .act"), function (e) { return (e.getAttribute("data-a") || "") + ":" + e.innerText.replace(/\\n+/g, " ") + (e.classList.contains("off") ? "(off)" : ""); }) })')
    ok(tg['kind'] == 'fac' and any(a.startswith('act:시설 파괴') and '(off)' not in a for a in tg['acts']) and any(a.startswith('moveon:이 칸으로 이동') for a in tg['acts']), '옆 칸에서 남의 시설을 누르면: [시설 파괴] · [이 칸으로 이동] %s' % tg['acts'])
    B.shot(pg, 'v4_enemy_fac', 200)
    tapsel(pg, '#sheet [data-a=moveon]'); pg.wait_for_timeout(1800)
    on = pg.evaluate('(E) => { var u = UMAP[E.u]; return { at: [u.c, u.r], btn: (document.querySelector("#sheet [data-a=facunder]") || { innerText: "" }).innerText.replace(/\\n+/g, " "), pri: !!document.querySelector("#sheet [data-a=facunder].pri"), done: u.done }; }', E)
    ok(on['at'] == E['ep'] and '시설 파괴' in on['btn'] and ('발밑의 ' + E['fn']) in on['btn'] and on['pri'], '남의 시설 칸에 올라서면 부대 창에 [시설 파괴 · 발밑의 %s] %s' % (E['fn'], on))
    B.shot(pg, 'v4_under', 200)
    tapsel(pg, '#sheet [data-a=facunder]'); pg.wait_for_timeout(400)
    tg2 = pg.evaluate('({ kind: UI.target ? UI.target.kind : null, d: UI.target ? UI.target.d : null, tgt: (document.querySelector("#sheet .tgt") || { textContent: "" }).textContent, moveon: !!document.querySelector("#sheet [data-a=moveon]") })')
    ok(tg2['kind'] == 'fac' and tg2['d'] == 0 and E['ebn'] in tg2['tgt'] and E['fn'] in tg2['tgt'] and not tg2['moveon'], '대상 창: %s' % tg2['tgt'])
    tapsel(pg, '#sheet [data-a=act]'); pg.wait_for_timeout(2600)
    hp = pg.evaluate('(E) => { var f = G.bases[E.eb].plots[E.pi].fac; return f ? f.hp : 0; }', E)
    ok(hp < E['hp'], '발밑의 시설을 치면 내구가 깎인다: %s → %s' % (E['hp'], hp))

    # ================= 5. 전법 실패의 풀이 · 쏘는 소리의 큐 =================
    print('5. 풀이 · 큐')
    pg.evaluate('showHelp()'); pg.wait_for_timeout(300)
    hp_ = pg.evaluate('document.querySelector("#modal").textContent')
    need = ['통상 공격의 85%', '세이브 파일 보내기', '파일에서 가져오기', '붙여넣기로 가져오기', '시설이 선 칸도 지나가고 설 수 있습니다']
    ok(all(n in hp_ for n in need), '도움말: %s' % [n for n in need if n not in hp_])
    pg.evaluate('closeDialog()')
    cues = pg.evaluate('(() => { var miss = [], k, i; for (k in CUES) for (i = 0; i < CUES[k].s.length; i++) if (!SFX_DATA[CUES[k].s[i][0]]) miss.push(k + ":" + CUES[k].s[i][0]); return { miss: miss, n: Object.keys(SFX_DATA).length, hit: CUES.arrowhit.s.map(function (x) { return x[0]; }), big: CUES.arrowbig.s.map(function (x) { return x[0]; }), fail: CUES.arrowfail.s.map(function (x) { return x[0]; }), great: CUES.arrowgreat.s.map(function (x) { return x[0]; }) }; })()')
    ok(cues['miss'] == [] and cues['n'] == 29, '큐가 가리키는 소리가 모두 있다(소리 %d개)' % cues['n'])
    ok(cues['hit'] == ['thock'] and cues['big'] == ['arrowland'] and 'thud' not in cues['fail'] + cues['great'] and 'crush' not in cues['great'], '쏘는 공격이 맞는 소리는 화살 소리뿐이다 %s' % {k: cues[k] for k in ('hit', 'big', 'great', 'fail')})

    # ================= 6. 나갈 자리 =================
    print('6. 나갈 자리')
    fresh(pg, 0, 1)
    pg.evaluate('(() => { var b = facCities(G.player)[0]; jumpTo(b.c, b.r, 1.6); flowDeploy(b); })()'); pg.wait_for_timeout(400)
    ok(not pg.evaluate('!!document.querySelector("#modal .dring")'), '무장을 고르기 전에는 나갈 자리 그림이 없다')
    tapsel(pg, '#modal [data-a=auto]'); pg.wait_for_timeout(300)
    RING = """(() => { var b = facCities(G.player)[0], ps = document.querySelectorAll('#modal .dring polygon[data-a=at]'), ts = document.querySelectorAll('#modal .dring text'), auto = deploySpot(b);
      return { n: ps.length, cells: Array.prototype.map.call(ps, function (p, i) { return [p.getAttribute('data-v'), p.getAttribute('class'), ts[i + 1].textContent]; }), city: ts[0].textContent, auto: auto.join(','),
        txt: document.querySelector('#dpAt').innerText.replace(/\\n+/g, ' | '), btn: !!document.querySelector('#modal [data-a=atauto]') }; })()"""
    r0 = pg.evaluate(RING); print('     ', r0)
    au = [c for c in r0['cells'] if ' au' in c[1]]
    ok(r0['n'] == 6 and r0['city'] == '진류' and len(au) == 1 and au[0][0] == r0['auto'] and '자동' in r0['txt'] and not r0['btn'], '성 둘레 여섯 칸 · 고르지 않으면 게임이 고를 칸이 점선 — ' + r0['txt'])
    ok(all(c[2] for c in r0['cells']) and any(c[2] in ('시장', '농장', '병영', '대장간', '마구간') for c in r0['cells']) and any(c[2] in ('길', '평지') for c in r0['cells']), '칸마다 무엇이 있는지 적혀 있다 %s' % [c[2] for c in r0['cells']])
    geo = pg.evaluate("""(() => { var b = facCities(G.player)[0], p0 = hexCenter(b.c, b.r), svg = document.querySelector('#modal .dring').getBoundingClientRect(), out = [];
      Array.prototype.forEach.call(document.querySelectorAll('#modal .dring polygon[data-a=at]'), function (p) { var v = p.getAttribute('data-v').split(','), q = hexCenter(+v[0], +v[1]), r = p.getBoundingClientRect();
        out.push([Math.sign(Math.round((q[0] - p0[0]) * 10)), Math.sign(Math.round((q[1] - p0[1]) * 10)), Math.sign(Math.round(r.left + r.width / 2 - svg.left - svg.width / 2)), Math.sign(Math.round(r.top + r.height / 2 - svg.top - svg.height / 2))]); });
      return out; })()""")
    ok(all(g[0] == g[2] and g[1] == g[3] for g in geo), '그림의 방향이 지도와 같다(동서 · 남북) %s' % geo)
    pick = [c for c in r0['cells'] if 'ok' in c[1] and ' au' not in c[1] and c[2] in ('시장', '농장', '병영', '대장간', '마구간')][0]
    pg.locator('#modal .dring polygon[data-v="%s"]' % pick[0]).tap(); pg.wait_for_timeout(300)
    r1 = pg.evaluate(RING)
    on = [c for c in r1['cells'] if ' on' in c[1]]
    ok(len(on) == 1 and on[0][0] == pick[0] and '고른 자리' in r1['txt'] and pick[2] in r1['txt'] and r1['btn'] and not any(' au' in c[1] for c in r1['cells']), '칸을 누르면 그 칸이 고른 자리 — ' + r1['txt'])
    B.shot(pg, 'v6_ring', 200)
    tapsel(pg, '#modal [data-a=atauto]'); pg.wait_for_timeout(200)
    r2 = pg.evaluate(RING); ok(not any(' on' in c[1] for c in r2['cells']) and '자동' in r2['txt'], '[자동]으로 되돌린다')
    pg.locator('#modal .dring polygon[data-v="%s"]' % pick[0]).tap(); pg.wait_for_timeout(300)
    tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(2600)
    u = pg.evaluate('(() => { var u = G.units.filter(function (x) { return x.f === G.player; }).pop(); return u ? u.c + "," + u.r : ""; })()')
    ok(u == pick[0], '고른 칸으로 나간다: %s (게임이 골랐을 칸 %s)' % (u, r0['auto']))
    pg.evaluate('talkHide()'); B.shot(pg, 'v6_out', 300)
    pg.evaluate('(() => { clearSel(); flowDeploy(facCities(G.player)[0]); })()'); pg.wait_for_timeout(400); tapsel(pg, '#modal [data-a=auto]'); pg.wait_for_timeout(300)
    r3 = pg.evaluate(RING); cell = [c for c in r3['cells'] if c[0] == pick[0]][0]
    ok('no' in cell[1] and cell[2] == '부대', '부대가 선 칸은 흐리게 · "부대" %s' % cell)
    pg.evaluate('$("toast").textContent = ""'); pg.locator('#modal .dring polygon[data-v="%s"]' % pick[0]).tap(); pg.wait_for_timeout(300)
    ok('나갈 수 없습니다' in toast(pg) and not any(' on' in c[1] for c in pg.evaluate(RING)['cells']), '그 칸은 고를 수 없다 — ' + toast(pg))
    pg.evaluate('closeDialog()')
    pg.evaluate('(() => { flowTransport(facCities(G.player)[0]); })()'); pg.wait_for_timeout(400)
    ok(pg.evaluate('document.querySelectorAll("#modal .dring polygon[data-a=at]").length') == 6, '수송 창에도 나갈 자리')
    pg.evaluate('closeDialog()')

    # ================= 7. 아래에 더 있다는 표시 =================
    print('7. 아래에 더 있습니다')
    MORE = """(() => { var b = document.querySelector('#modal .dlg-b'), h = b && b.querySelector(':scope > .morehint'); if (!b) return null; var r = b.getBoundingClientRect(), c = h && h.firstChild.getBoundingClientRect();
      return { more: b.scrollHeight - b.scrollTop - b.clientHeight, has: !!h, on: !!h && h.classList.contains('on'), op: h ? +getComputedStyle(h).opacity : -1, top: b.scrollTop, chip: c ? [Math.round(c.bottom - r.bottom), Math.round(c.left + c.width / 2 - r.left - r.width / 2), h.firstChild.textContent] : null }; })()"""
    pg.evaluate('showHelp()'); pg.wait_for_timeout(600)
    m0 = pg.evaluate(MORE); print('     ', m0)
    ok(m0['more'] > 100 and m0['has'] and m0['on'] and m0['op'] > 0.9 and '아래에 더 있습니다' in m0['chip'][2], '긴 창(도움말): 아래 끝에 딱지가 뜬다')
    ok(-40 <= m0['chip'][0] <= 0 and abs(m0['chip'][1]) <= 2, '딱지는 몸통의 아래 끝 가운데 %s' % m0['chip'][:2])
    B.shot(pg, 'v7_help', 200)
    cb = pg.evaluate('(() => { var r = document.querySelector("#modal .morehint i").getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; })()')      # 딱지는 살짝 흔들리므로 자리를 재서 누른다
    pg.touchscreen.tap(cb[0], cb[1]); pg.wait_for_timeout(900)
    m1 = pg.evaluate(MORE)
    ok(m1['top'] > m0['top'] + 200, '딱지를 누르면 한 화면쯤 내려간다: %d → %d' % (m0['top'], m1['top']))
    pg.evaluate('(() => { var b = document.querySelector("#modal .dlg-b"); b.scrollTop = b.scrollHeight; })()'); pg.wait_for_timeout(500)
    m2 = pg.evaluate(MORE)
    ok(m2['more'] <= 1 and m2['has'] and not m2['on'] and m2['op'] < 0.1, '끝까지 내리면 사라진다 %s' % m2)
    pg.evaluate('(() => { var b = document.querySelector("#modal .dlg-b"); b.scrollTop = 0; refreshDialog(); })()'); pg.wait_for_timeout(100)
    m3 = pg.evaluate(MORE); ok(m3['has'] and m3['on'], '창을 다시 그려도 그대로 붙어 있다')
    pg.evaluate('closeDialog(); showMenu()'); pg.wait_for_timeout(500)
    m4 = pg.evaluate(MORE); ok(m4['more'] <= 10 and not m4['on'], '짧은 창(메뉴)에는 뜨지 않는다 %s' % m4)
    pg.evaluate('closeDialog()')
    # 아래 판(목록이 긴 거점 창): 무장이 많은 도시의 인재 갈래
    pg.evaluate('selectBase(facCities(G.player)[0])'); pg.wait_for_timeout(600)
    sh = pg.evaluate("""(() => { var body = document.querySelector('#sheet .sh-body'), h = body && body.querySelector(':scope > .morehint'); return { has: !!h, more: body ? body.scrollHeight - body.clientHeight : -1, on: !!h && h.classList.contains('on') }; })()""")
    ok(sh['has'] and (sh['on'] == (sh['more'] > 10)), '아래 판에도 붙는다(더 있을 때만 켜진다) %s' % sh)

    # ================= 8. Claude 앱 안(아티팩트)에서 파일 내보내기 (v0.12.1) =================
    print('8. 아티팩트 안')
    pg.evaluate('closeDialog(); saveTo("s1")')
    SEND = """({ share: !!document.querySelector('#modal [data-a=sshare]'), down: (document.querySelector('#modal [data-a=sdown]') || { innerText: '' }).innerText.replace(/\\n+/g, ' | '), wait: Array.prototype.some.call(document.querySelectorAll('#modal .cmd[disabled]'), function (e) { return e.textContent.indexOf('준비') >= 0; }), note: document.querySelector('#modal .note').textContent })"""
    # (가) downloads 기능이 있는 화면
    pg.evaluate("""(() => { DLCAP = undefined; window._dl = null; window._useN = 0;
      window.claude = { use: function (name) { window._useN++; return new Promise(function (res) { setTimeout(function () { res(name === 'downloads' ? { save: function (req) { window._dl = req; return window._dlFail ? Promise.reject({ code: window._dlFail, message: 'x' }) : Promise.resolve({ status: 'saved' }); } } : null); }, 250); }); } };
      navigator.canShare = function () { return true; }; navigator.share = function () { window._webshare = 1; return Promise.resolve(); }; })()""")
    pg.evaluate('showShare()'); pg.wait_for_timeout(300)
    ok(not pg.evaluate('!!document.querySelector("#modal [data-a=send]")'), '아티팩트 안: 주소의 [보내기](공유 창)는 내지 않는다')
    tapsel(pg, '#modal [data-a=savesend]'); pg.wait_for_timeout(100); tapsel(pg, '#modal [data-slot=s1] [data-a=spick]'); pg.wait_for_timeout(50)
    w = pg.evaluate(SEND)
    pg.wait_for_timeout(500); r = pg.evaluate(SEND)
    ok(not r['share'] and r['down'].startswith('파일로 내보내기') and not r['wait'] and '내보낼 수 없습니다' not in r['note'], '기능이 준비되면 [파일로 내보내기] — 공유 창 단추는 없다 %s (준비 중 표시: %s)' % (r['down'], w['wait']))
    B.shot(pg, 'v8_claude', 200)
    want = pg.evaluate('saveFileText("s1").text')
    tapsel(pg, '#modal [data-a=sdown]'); pg.wait_for_timeout(400)
    dl = pg.evaluate('window._dl')
    ok(dl and dl['filename'].endswith('.txt') and dl['filename'].startswith('천하도_') and dl['data'] == want and '내보냈습니다' in toast(pg) and not pg.evaluate('!!window._webshare'), '[파일로 내보내기]: downloads.save 에 파일 이름과 세이브 글이 간다 — ' + toast(pg))
    pg.evaluate('(() => { window._dlFail = "declined"; $("toast").textContent = ""; })()'); tapsel(pg, '#modal [data-a=sdown]'); pg.wait_for_timeout(400)
    ok(toast(pg) == '', '보는 사람이 거절하면 아무 알림도 없다(내보냈다고 하지 않는다)')
    pg.evaluate('(() => { window._dlFail = "unavailable"; })()'); tapsel(pg, '#modal [data-a=sdown]'); pg.wait_for_timeout(400)
    ok('내보내지 못했습니다' in toast(pg), '그 밖의 실패는 알린다 — ' + toast(pg))
    ok(pg.evaluate('window._useN') == 1, '기능은 한 번만 묻는다')
    pg.evaluate('closeDialog()')
    # (나) 기능이 없는 화면
    pg.evaluate("""(() => { DLCAP = undefined; window.claude = { use: function () { return Promise.resolve(null); } }; })()""")
    pg.evaluate('showSaveSend()'); pg.wait_for_timeout(200); tapsel(pg, '#modal [data-slot=s1] [data-a=spick]'); pg.wait_for_timeout(300)
    r2 = pg.evaluate(SEND)
    ok(not r2['share'] and r2['down'] == '' and '이 화면에서는 파일로 내보낼 수 없습니다' in r2['note'] and pg.evaluate('!!document.querySelector("#modal [data-a=scopy]")'), '기능이 없으면 파일 단추를 내지 않고 그렇다고 적는다 · [글자로 복사]는 남는다')
    pg.evaluate('(() => { closeDialog(); delete window.claude; DLCAP = undefined; delete navigator.share; delete navigator.canShare; })()')
    # (다) 밖(브라우저)에서는 전과 같다
    pg.evaluate('showSaveSend()'); pg.wait_for_timeout(200); tapsel(pg, '#modal [data-slot=s1] [data-a=spick]'); pg.wait_for_timeout(300)
    r3 = pg.evaluate(SEND); ok(r3['down'].startswith('파일로 저장') and '.txt' in r3['down'], '아티팩트 밖에서는 전과 같이 [파일로 저장] — ' + r3['down'])
    pg.evaluate('closeDialog()')
B.run(steps, 390, 844, 2)
errs = [e for e in B.errors if 'GPU stall' not in e and 'GL Driver' not in e and 'ERR_FILE_NOT_FOUND' not in e and 'willReadFrequently' not in e]
print('console errors:', errs[:6])
print('FAILS %d' % len(fails), fails)
sys.exit(1 if fails or errs else 0)
