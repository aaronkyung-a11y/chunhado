# v0.22 — 화면 조작으로 확인(11-23 21:35 의 열한 가지 가운데 화면에 드러나는 것들)
#   ① 단추: 틀의 생김새대로 오려 낸다(누끼) — 가림 그림 · 테두리 0 · 틀 밖의 그림자 없음 · 단추 상자의 가장자리에 바탕이 드러나지 않는다
#   ② · ③ 코드로 그린 그림(공사장 · 불길 · 화살 · 붓 고리 · 먹점 · 이름표): 그림판의 내용이 지워지고 WebGL 문맥이 끊겼다 이어져도 남는다
#   ④ 합병: 홍농의 붙어 있는 두 농장   ⑤ 부대 그림: 창병의 크기 · 병과의 빛깔   ⑥ 수송 세 걸음 · '물자'   ⑦ 함락하면 시설의 일부가 부서진다(화면의 말)
#   ⑧ 무기 줄 · 실은 물자 줄이 잘리지 않는다   ⑨ 병량이 모자라면 모자란다고 말한다(출진 · 수송)   ⑩ 친 다음에 바뀐다(궤멸 · 함락 · 걸어 들어가 차지)   ⑪ 출진 무장의 적성 순
#   python3 tests/d36.py          찍은 그림은 tests/shots38/
import sys, os, io, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import tapsel
import d2 as D2
from PIL import Image
B.SHOTS = os.path.join(B.ROOT, 'shots38')
os.makedirs(B.SHOTS, exist_ok=True)
fails = []
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)
def T(pg, sel): return pg.evaluate('(s) => { var e = document.querySelector(s); return e ? e.textContent : null; }', sel)
def edge_face(pg, sel, nth=0):
    """단추의 바탕을 자홍으로 바꿔 놓고, 단추 상자의 가장자리 한 줄에 자홍 점이 얼마나 드러나는지(모서리는 뺀다). 0 이면 틀 바깥으로 바탕이 나오지 않는다."""
    pg.evaluate('([s, n]) => { var e = document.querySelectorAll(s)[n]; e.__st = e.getAttribute("style"); e.style.background = "#ff00ff"; e.style.backgroundImage = "none"; }', [sel, nth]); pg.wait_for_timeout(120)
    bb = pg.locator(sel).nth(nth).bounding_box()
    im = Image.open(io.BytesIO(pg.screenshot(clip={'x': bb['x'], 'y': bb['y'], 'width': bb['width'], 'height': bb['height']}))).convert('RGB')
    pg.evaluate('([s, n]) => { var e = document.querySelectorAll(s)[n]; if (e.__st === null) e.removeAttribute("style"); else e.setAttribute("style", e.__st); }', [sel, nth])
    w, h = im.size; px = im.load(); m = n = 0
    def mag(p): return p[0] > 200 and p[2] > 200 and p[1] < 90
    for x in range(int(w * 0.12), int(w * 0.88)):
        for y in (0, h - 1): n += 1; m += mag(px[x, y])
    for y in range(int(h * 0.2), int(h * 0.8)):
        for x in (0, w - 1): n += 1; m += mag(px[x, y])
    inner = sum(1 for x in range(w // 3, 2 * w // 3) for y in (h // 6, 5 * h // 6) if mag(px[x, y]))      # 안쪽은 자홍이어야 한다(시험이 제대로 보고 있는지)
    return round(m / max(1, n), 3), inner
def count(pg, clip, pred):
    im = Image.open(io.BytesIO(pg.screenshot(clip=clip))).convert('RGB'); return sum(1 for p in im.getdata() if pred(p))
def hexclip(pg, c, r, wd=70, up=70, dn=20):
    x, y = B.hexpos(pg, c, r); return {'x': x - wd / 2, 'y': y - up, 'width': wd, 'height': up + dn}
WIPE = '''() => { var n = 0;
  (window.CVS || []).forEach(function (c) { if (c.id === 'map') return; try { var x = c.getContext('2d'); if (x) { x.setTransform(1, 0, 0, 1, 0, 0); x.clearRect(0, 0, c.width, c.height); n++; } } catch (e) {} });
  var gl = R3.renderer.getContext(); window.EXT = gl.getExtension('WEBGL_lose_context'); EXT.loseContext(); return n; }'''

def steps(pg):
    B.start(pg, 0)
    ok(pg.evaluate('GAME_VERSION') == B.VER, '판 번호 ' + B.VER)
    pg.evaluate('''() => { talkHide(); UI.talk = false; var A = facCities(G.player)[0]; window.T = { a: A.id };
      A.w.spear = 10807; A.w.halberd = 26225; A.w.bow = 6887; A.w.horse = 14778; A.w.ram = 3; A.troops = 24199; A.food = 229582; A.gold = 95905; G.factions[G.player].ap = 250; selectBase(A); }'''); pg.wait_for_timeout(700)

    # ---------- ① 단추를 틀대로 오려 낸다 ----------
    print('① 단추 — 틀의 생김새대로 오려 낸다')
    ms = pg.evaluate('''() => { function f(sel) { var e = document.querySelector(sel); if (!e) return null; var c = getComputedStyle(e), a = getComputedStyle(e, '::after');
        return { src: (c.webkitMaskBoxImageSource || c.maskBorderSource || '').slice(0, 26), len: (c.webkitMaskBoxImageSource || c.maskBorderSource || '').length, w: c.webkitMaskBoxImageWidth || c.maskBorderWidth, sl: c.webkitMaskBoxImageSlice || c.maskBorderSlice,
          bw: c.borderTopWidth, fw: a.borderTopWidth, out: c.boxShadow.split(/,(?![^(]*\\))/).filter(function (s) { return s.trim() && s.trim() !== 'none' && s.indexOf('inset') < 0; }).length }; }
      return { cmd: f('#sheet .cmd'), bar: f('#bar button'), end: f('#btnEnd'), fold: f('.x.fold') }; }''')
    print('     ', ms)
    for k in ('cmd', 'bar', 'end'):
        m = ms[k]
        ok(m and m['src'].startswith('url("data:image/svg+xml') and m['len'] > 2000 and m['sl'].startswith('30') and m['w'] == m['fw'] and m['bw'] == '0px' and m['out'] == 0, "%s: 가림 그림이 걸려 있다(아홉 조각 · 굵기 %s = 틀의 굵기) · 테두리 0 · 틀 밖의 그림자 없음" % (k, m and m['w']))
    e1, i1 = edge_face(pg, '#sheet .cmd', 0); e2, i2 = edge_face(pg, '#bar button', 0); e3, i3 = edge_face(pg, '#btnEnd', 0)
    print('      가장자리에 드러난 바탕의 몫:', e1, e2, e3, '| 안쪽 점', i1, i2, i3)
    ok(e1 <= 0.02 and e2 <= 0.02 and e3 <= 0.02 and min(i1, i2, i3) > 10, '단추 상자의 가장자리 줄에 바탕이 드러나지 않는다(명령 %.3f · 아래 줄 %.3f · 턴 종료 %.3f) — 안쪽은 칠해져 있다' % (e1, e2, e3))
    B.shot(pg, 'a1_buttons', 100)

    # ---------- ⑧ 무기 줄 ----------
    print('⑧ 무기 줄 · 실은 물자 줄')
    wp = pg.evaluate('''() => { var w = document.querySelector('#sheet .wp'), r = w.getBoundingClientRect(), sp = [].slice.call(w.querySelectorAll('span'));
      return { h: Math.round(r.height), sw: w.scrollWidth, cw: w.clientWidth, n: sp.length, inside: sp.every(function (s) { var q = s.getBoundingClientRect(); return q.right <= r.right + 0.5 && q.bottom <= r.bottom + 0.5 && q.width > 10; }), txt: w.textContent,
        gap: sp.map(function (s) { var b = s.querySelector('b'), t = s.childNodes; return b ? Math.round((b.getBoundingClientRect().left - s.getBoundingClientRect().left)) : 0; }) }; }''')
    print('     ', wp)
    ok(wp['n'] == 5 and wp['inside'] and wp['sw'] <= wp['cw'] and '충차 3' in wp['txt'].replace('\xa0', ' ') or (wp['n'] == 5 and wp['inside'] and wp['sw'] <= wp['cw'] and '충차' in wp['txt']), '거점의 무기 줄: 다섯 가지가 모두 보인다(창 10,807 · 극 26,225 · 노 6,887 · 군마 14,778 · 충차 3) — 넘치면 다음 줄로(높이 %dpx)' % wp['h'])
    cg = pg.evaluate('''() => { var A = G.bases[T.a], o = idleOfficers(A)[idleOfficers(A).length - 1];
      var r = cmdDeploy(A, { type: 'trans', ids: [o.id], troops: 16600, food: 20267, gold: 70810, cargo: { spear: 1008, halberd: 714, bow: 4770, horse: 2300, ram: 2 } }); if (!r.ok) return r.msg;
      syncScene(); selectUnit(r.unit); window.T.tr = r.unit.id; var w = document.querySelector('#sheet .wp.cgo'), q = w.getBoundingClientRect(), sp = [].slice.call(w.querySelectorAll('span'));
      return { n: sp.length, sw: w.scrollWidth, cw: w.clientWidth, h: Math.round(q.height), inside: sp.every(function (s) { var z = s.getBoundingClientRect(); return z.right <= q.right + 0.5 && z.width > 10; }), txt: w.textContent }; }''')
    print('     ', cg); B.shot(pg, 'a2_cargo', 200)
    ok(isinstance(cg, dict) and cg['n'] == 7 and cg['inside'] and cg['sw'] <= cg['cw'] and '군마' in cg['txt'] and '충차' in cg['txt'], '수송대의 물자 줄: 병량 · 금 · 창 · 극 · 노 · 군마 · 충차 일곱 가지가 모두 보인다(높이 %s px)' % (cg['h'] if isinstance(cg, dict) else cg))
    pg.evaluate('''() => { var u = UMAP[T.tr]; if (u) { removeUnit(u); } clearSel(); syncScene(); selectBase(G.bases[T.a]); }'''); pg.wait_for_timeout(300)

    # ---------- ⑤ 부대 그림 ----------
    print('⑤ 부대 그림 — 창병의 크기 · 병과의 빛깔')
    sp = pg.evaluate('''() => { var out = { w: {}, col: {} };
      ['u_sword', 'u_spear', 'u_halberd', 'u_bow', 'u_cav', 'u_ram', 'u_trans'].forEach(function (k) { var S = SPRITES[k], im = SITE_IMG[k]; out.w[k] = [S.w, S.h];
        var c = document.createElement('canvas'); c.width = S.w; c.height = S.h; var x = c.getContext('2d', { willReadFrequently: true }); x.drawImage(im, 0, 0, S.w, S.h); var d = x.getImageData(0, 0, S.w, S.h).data, r = 0, g = 0, b = 0, n = 0, x0 = S.w, x1 = 0;
        for (var i = 0; i < d.length; i += 4) { if (d[i + 3] > 40) { var px = (i >> 2) % S.w; if (px < x0) x0 = px; if (px > x1) x1 = px; } if (d[i + 3] < 200) continue; var l = d[i] * 0.3 + d[i + 1] * 0.59 + d[i + 2] * 0.11; if (l < 110) continue; r += d[i]; g += d[i + 1]; b += d[i + 2]; n++; }
        out.col[k] = [Math.round(r / n), Math.round(g / n), Math.round(b / n)]; out.w[k].push(x1 - x0 + 1, Math.round((x0 + x1 + 1) / 2)); });
      return out; }''')
    print('     ', sp)
    ok(sp['w']['u_spear'][0] == 200 and abs(sp['w']['u_spear'][2] - sp['w']['u_sword'][2]) <= 8 and abs(sp['w']['u_spear'][3] - 100) <= 3, '창병 그림: 가로 200(전에는 162) · 무리의 폭 %dpx — 검병 %dpx 과 같은 크기 · 가운데에 선다' % (sp['w']['u_spear'][2], sp['w']['u_sword'][2]))
    c = sp['col']
    ok(c['u_spear'][2] - c['u_spear'][0] > 30 and c['u_halberd'][0] - c['u_halberd'][2] > 30 and c['u_halberd'][0] - c['u_halberd'][1] > 20 and c['u_bow'][1] - c['u_bow'][0] > 20 and c['u_bow'][1] - c['u_bow'][2] > 20 and c['u_cav'][0] - c['u_cav'][2] > 50 and c['u_cav'][1] - c['u_cav'][2] > 30,
       '병과의 빛깔(밝은 점의 평균 RGB): 창병 푸른빛 %s · 극병 붉은빛 %s · 노병 초록빛 %s · 기병 누른빛 %s' % (c['u_spear'], c['u_halberd'], c['u_bow'], c['u_cav']))
    ok(all(max(c[k]) - min(c[k]) < 28 for k in ('u_sword', 'u_ram', 'u_trans')), '검병 · 충차 · 수송대는 먹빛 그대로 %s %s %s' % (c['u_sword'], c['u_ram'], c['u_trans']))

    # ---------- ⑪ 출진: 적성 순 · ⑨ 병량 ----------
    print('⑪ 출진 무장의 적성 순')
    pg.evaluate('''() => { flowDeploy(G.bases[T.a]); }'''); pg.wait_for_timeout(500)
    def grades(): return pg.evaluate('''() => [].map.call(document.querySelectorAll('#modal .rows .row'), function (r) { var b = r.querySelector('.rt b'); return [r.getAttribute('data-v'), b ? b.textContent : '']; })''')
    R = 'CBAS'; res = {}
    for t in ('spear', 'halberd', 'bow', 'cav'):
        tapsel(pg, '#modal [data-a=type][data-v=%s]' % t); g = grades(); res[t] = [x[1] for x in g]
        ok(len(g) >= 5 and all(R.index(g[i][1]) >= R.index(g[i + 1][1]) for i in range(len(g) - 1)) and len(set(x[1] for x in g)) >= 2, '%s: 적성이 높은 차례로 선다 — %s' % (t, ''.join(x[1] for x in g)))
    lab = T(pg, '#modal .sec .aptby')
    same = pg.evaluate('''() => { var ids = [].map.call(document.querySelectorAll('#modal .rows .row'), function (r) { return +r.getAttribute('data-v'); }), ai = APT_IDX.cav, okk = true;
      for (var i = 0; i + 1 < ids.length; i++) { var a = off(ids[i]), b = off(ids[i + 1]); if (a.apt.charAt(ai) === b.apt.charAt(ai) && aiMilScore(a) < aiMilScore(b)) okk = false; } return okk; }''')
    ok(lab == '기병 적성 순' and same, "무장 줄머리에 '기병 적성 순' · 적성이 같으면 전처럼 싸움 솜씨 순")
    tapsel(pg, '#modal [data-a=type][data-v=sword]')
    sw = pg.evaluate('''() => { var ids = [].map.call(document.querySelectorAll('#modal .rows .row'), function (r) { return +r.getAttribute('data-v'); }), okk = true; for (var i = 0; i + 1 < ids.length; i++) if (aiMilScore(off(ids[i])) < aiMilScore(off(ids[i + 1]))) okk = false; return [okk, !!document.querySelector('#modal .sec .aptby')]; }''')
    ok(sw[0] and not sw[1], '검병(적성이 없다): 전과 같은 차례 · 표시 없음')
    of = pg.evaluate('''() => { function src(e) { return getComputedStyle(e, '::after').borderImageSource; } var os = [].slice.call(document.querySelectorAll('#modal .opt')), off = os.filter(function (e) { return !e.classList.contains('on'); }), on = os.filter(function (e) { return e.classList.contains('on'); })[0];
      return { n: os.length, one: off.every(function (e) { return src(e) === src(off[0]); }), diff: src(on) !== src(off[0]), mask: off.every(function (e) { return getComputedStyle(e).webkitMaskBoxImageSource === getComputedStyle(off[0]).webkitMaskBoxImageSource; }) }; }''')
    ok(of['n'] == 6 and of['one'] and of['diff'] and of['mask'], '고르지 않은 병과 칸의 틀은 모두 같은 옅은 획이다(0.21 에서는 짝수째만 짙었다) · 고른 칸은 붉은 획')
    B.shot(pg, 'b1_deploy_apt', 100)

    print('⑨ 병량이 모자라면 — 출진')
    tapsel(pg, '#modal [data-a=type][data-v=cav]'); tapsel(pg, '#modal .rows .row', 0)
    def opts(): return pg.evaluate('''() => [].map.call(document.querySelectorAll('#modal [data-a=turns]'), function (b) { return (b.classList.contains('on') ? 'on' : '') + (b.classList.contains('off') ? 'off' : '') + ':' + b.querySelector('b').textContent; })''')
    def okcls(): return pg.evaluate('''() => document.querySelector('#modal [data-a=ok]').className''')
    tapsel(pg, '#modal [data-a=next]'); pg.wait_for_timeout(600)
    n0, o0 = T(pg, '#dpN'), opts()
    ok('모자' not in n0 and o0[1].startswith('on') and not any('off' in x for x in o0) and 'off' not in okcls(), '병량이 넉넉하면 전과 같다: 180일분이 골라져 있다 [%s]' % n0)
    tapsel(pg, '#modal [data-a=prev]'); pg.evaluate('''() => { G.bases[T.a].food = 3000; }'''); tapsel(pg, '#modal [data-a=next]'); pg.wait_for_timeout(600)
    n1, o1 = T(pg, '#dpN'), opts(); B.shot(pg, 'b2_food_low', 100)
    ok('병량이 모자라 180일분 대신 90일분을 골랐습니다' in n1 and o1[0].startswith('on:') and all(x.startswith('off') for x in o1[1:]) and 'off' not in okcls(), '도시 병량 3,000(180일분에 5,400 필요): 댈 수 있는 90일분으로 고르고 그렇게 했다고 적는다 · 댈 수 없는 칸은 흐리다')
    tapsel(pg, '#modal [data-a=turns][data-v="36"]'); t1 = T(pg, '#toast')
    ok('도시 병량이 모자랍니다 — 360일분에 10,800 필요 · 보유 3,000' in (t1 or ''), '흐린 칸을 누르면 모자란다고 말한다: ' + str(t1))
    tapsel(pg, '#modal [data-a=prev]'); pg.evaluate('''() => { G.bases[T.a].food = 1200; }'''); tapsel(pg, '#modal [data-a=next]'); pg.wait_for_timeout(600)
    n2, o2, c2 = T(pg, '#dpN'), opts(), okcls(); nu0 = pg.evaluate('G.units.length')
    tapsel(pg, '#modal [data-a=ok]'); t2 = T(pg, '#toast'); B.shot(pg, 'b3_food_none', 100)
    ok('병량이 모자랍니다' in n2 and '90일분(2,700)도 댈 수 없습니다' in n2 and '있는 만큼 싣기 · 40일분' in n2 and all(x.startswith('off') for x in o2) and 'off' in c2, '도시 병량 1,200(90일분에도 못 미친다): 어느 칸도 고를 수 없고 [있는 만큼 싣기 · 40일분]이 뜬다 · [출진]이 흐리다')
    ok('병량이 모자랍니다' in (t2 or '') and pg.evaluate('G.units.length') == nu0 and pg.evaluate('!!MODAL'), '그대로 [출진]을 누르면 나가지 않고 까닭을 말한다: ' + str(t2))
    tapsel(pg, '#modal [data-a=fmax]'); n3 = T(pg, '#dpN'); p3 = T(pg, '#dpP')
    ok('있는 만큼 싣습니다 — 40일분(1,200)' in n3 and '군량 1,200' in p3 and 'off' not in okcls(), '[있는 만큼 싣기]: 40일분(1,200)을 싣고 나갈 수 있다')
    tapsel(pg, '#modal [data-a=prev]'); pg.evaluate('''() => { G.bases[T.a].food = 100; }'''); tapsel(pg, '#modal [data-a=next]'); pg.wait_for_timeout(600)
    n4 = T(pg, '#dpN'); tapsel(pg, '#modal [data-a=ok]'); t4 = T(pg, '#toast')
    ok('병량이 모자라 출진할 수 없습니다' in n4 and '열흘분(300)도 없습니다' in n4 and '있는 만큼' not in n4 and '병량이 모자라 출진할 수 없습니다' in (t4 or '') and pg.evaluate('G.units.length') == nu0, '도시 병량 100(열흘분 300 에도 못 미친다): 출진할 수 없고, 누르면 "병량이 모자라 출진할 수 없습니다"')
    pg.evaluate('() => { closeDialog(); }'); pg.wait_for_timeout(300)

    # ---------- ⑥ 수송 세 걸음 · 물자 ----------
    print("⑥ 수송 — 세 걸음 · '물자'")
    pg.evaluate('''() => { G.bases[T.a].food = 229582; flowTransport(G.bases[T.a]); }'''); pg.wait_for_timeout(500)
    h1 = T(pg, '#modal .dlg-h h2'); f1 = pg.evaluate('document.querySelectorAll("#modal .fld").length'); r1 = pg.evaluate('document.querySelectorAll("#modal .rows .row").length'); x1 = T(pg, '#modal .dlg')
    ok('1/3 호송 무장' in h1 and f1 == 0 and r1 >= 3, '① 호송 무장: 무장만 고른다(실을 것은 다음 걸음) [%s]' % h1)
    tapsel(pg, '#modal [data-a=next]'); pg.wait_for_timeout(300)
    h2 = T(pg, '#modal .dlg-h h2'); f2 = pg.evaluate('document.querySelectorAll("#modal .fld").length'); s2 = T(pg, '#modal .sec'); p2 = T(pg, '#modal [data-a=prev]'); nt2 = T(pg, '#trN'); x2 = T(pg, '#modal .dlg'); B.shot(pg, 'c1_trans_goods', 100)
    ok('2/3 물자' in h2 and f2 == 8 and s2 == '실을 물자' and '무장' in p2 and '80일분(400)' in nt2, "② 물자: [다음]을 누르면 실을 물자를 고른다(병력 · 금 · 병량 · 창 · 극 · 노 · 군마 · 충차) · 되돌아가는 단추 '%s'" % p2)
    tapsel(pg, '#modal [data-a=next]'); pg.wait_for_timeout(900)
    h3 = T(pg, '#modal .dlg-h h2'); p3 = T(pg, '#modal [data-a=prev]'); x3 = T(pg, '#modal .dlg'); mk = pg.evaluate('document.querySelectorAll(".mk.ex").length')
    ok('3/3 어디로' in h3 and '물자' in p3 and mk >= 1 and pg.evaluate('!!document.querySelector("#modal [data-a=to][data-v=x0]")'), "③ 어디로: 되돌아가는 단추 '%s' · 지도에 갈 곳이 뜬다" % p3)
    ok('짐' not in (x1 + x2 + x3), "수송 창 세 걸음 어디에도 '짐'이라는 말이 없다")
    tapsel(pg, '#modal [data-a=prev]'); pg.wait_for_timeout(300); hb = T(pg, '#modal .dlg-h h2'); tapsel(pg, '#modal [data-a=prev]'); pg.wait_for_timeout(200); ha = T(pg, '#modal .dlg-h h2')
    ok('2/3' in hb and '1/3' in ha, '되돌아가기: ③ → ② → ①')
    print('⑨ 병량이 모자라면 — 수송')
    pg.evaluate('() => { closeDialog(); G.bases[T.a].food = 300; flowTransport(G.bases[T.a]); }'); pg.wait_for_timeout(400); tapsel(pg, '#modal [data-a=next]'); pg.wait_for_timeout(300)
    nl = T(pg, '#trN'); lk = T(pg, '#modal .note.lack'); B.shot(pg, 'c2_trans_low', 100)
    ok('도시 병량이 모자랍니다' in nl and '80일분에 400 필요 · 보유 300' in nl and '60일분만 싣고 떠납니다' in nl, '도시 병량 300: 모자란다고 붉게 적는다 — ' + nl[:60])
    ok(lk is not None and '병량 — 실을 만큼 없습니다' in lk, '병량이 실을 만큼(500) 없으면 병량 칸을 말없이 빼지 않고 그렇다고 적는다: ' + str(lk))
    pg.evaluate('() => { closeDialog(); G.bases[T.a].food = 20; flowTransport(G.bases[T.a]); }'); pg.wait_for_timeout(400); tapsel(pg, '#modal [data-a=next]'); pg.wait_for_timeout(300)
    nz = T(pg, '#trN'); cz = pg.evaluate('''() => document.querySelector('#modal [data-a=next]').className'''); tapsel(pg, '#modal [data-a=next]'); tz = T(pg, '#toast'); hz = T(pg, '#modal .dlg-h h2')
    ok('열흘분도 없어 떠날 수 없습니다' in nz and 'off' in cz and '병량이 모자라 수송대를 낼 수 없습니다' in (tz or '') and '2/3' in hz, '도시 병량 20(열흘분 50 에도 못 미친다): 떠날 수 없고, 누르면 까닭을 말한다 — ' + str(tz))
    pg.evaluate('() => { closeDialog(); G.bases[T.a].food = 229582; }'); pg.wait_for_timeout(200)
    hp = pg.evaluate('''() => { var d = document.createElement('div'); d.innerHTML = HELP_HTML; var t = d.textContent; return [t.indexOf('짐') >= 0, t.indexOf('물자') >= 0, t.indexOf('시설의 일부가 싸움에 부서집니다') >= 0, t.indexOf('적성이 높은 차례') >= 0, t.indexOf('있는 만큼 싣기') >= 0, t.indexOf('창병 푸른빛') >= 0, t.indexOf('치는 모습이 끝난 뒤에') >= 0]; }''')
    ok(hp == [False, True, True, True, True, True, True], "도움말: '짐'이 없고 '물자' · 함락 때의 시설 · 적성 순 · 있는 만큼 싣기 · 병과의 빛깔 · 결과가 나타나는 때가 적혀 있다 %s" % hp)

    # ---------- ② · ③ 코드로 그린 그림 ----------
    print('② · ③ 코드로 그린 그림 — 그림판이 지워지고 WebGL 문맥이 끊겼다 이어져도 남는다')
    S0 = pg.evaluate('''() => { clearSel(); var A = G.bases[T.a], free = []; A.plots.forEach(function (p, i) { if (!p.fac) free.push(i); }); A.gold = 9000; G.factions[G.player].ap = 250;
      var os = idleOfficers(A).filter(function (o) { return !isLord(o); });
      var r1 = cmdDevelop(A, free[0], 'market', [os[0].id]), r2 = cmdDevelop(A, free[1], 'farm', [os[1].id]);
      var fk = null; for (var d = 3; d < 6 && fk === null; d++) { var k = K(A.c + d, A.r + 1), t = terr(A.c + d, A.r + 1); if (!PAT[k] && BAT[k] === undefined && !UAT[k] && t !== 'm' && t !== 's' && t !== 'x') fk = k; }
      G.fires[fk] = { t: 3, f: G.player }; fxTex('arrow'); fxTex('stroke'); fxTex('ember');
      syncScene(); jumpTo(A.c, A.r, 1.5); requestDraw();
      return { ok: [r1.ok, r2.ok], p: [[A.plots[free[0]].c, A.plots[free[0]].r], [A.plots[free[1]].c, A.plots[free[1]].r]], fire: [fk % W, (fk - fk % W) / W], city: [A.c, A.r], cvs: (window.CVS || []).length,
        kinds: { site: !!TEX['market@0'] && TEX['market@0'].isDataTexture === true, flame: R3.flame.isDataTexture === true, arrow: FX.tex.arrow.isDataTexture === true, enso: !!R3.zoneTex && R3.zoneTex.isDataTexture === true, dot: !R3.dotTex || R3.dotTex.isDataTexture === true, label: R3.bases[A.id].lab.tex.isDataTexture === true, noise: R3.tmat.uniforms.detail.value.isDataTexture === true },
        canv: (function () { var n = 0; R3.scene.traverse(function (o) { var m = o.material; if (m && m.map && m.map.isCanvasTexture) n++; }); for (var k2 in FX.tex) if (FX.tex[k2].isCanvasTexture) n++; return n; })() }; }''')
    pg.wait_for_function('() => UI.anims.length === 0', timeout=20000); pg.wait_for_timeout(1200)      # 시점이 다 옮겨 간 뒤에 잰다
    print('     ', S0)
    ok(S0['ok'] == [True, True] and all(S0['kinds'].values()) and S0['canv'] == 0, '공사장 · 불꽃 · 화살 · 붓 고리 · 이름표 · 땅의 결: 모두 화소를 지닌 텍스처다(그림판을 원본으로 삼는 텍스처 %d개)' % S0['canv'])
    def scaf(p): return p[0] > 110 and p[0] - p[2] > 45 and 60 < p[1] < 170 and p[0] - p[1] > 15           # 비계의 대나무빛
    def fire(p): return p[0] > 200 and p[1] > 80 and p[2] < 130 and p[0] - p[2] > 90                       # 불꽃
    def lab(p): return p[2] > 110 and p[2] - p[0] > 40 and p[1] > 70                                        # 이름표의 세력 빛(조조 — 쪽빛)
    def meas():
        a = count(pg, hexclip(pg, S0['p'][0][0], S0['p'][0][1]), scaf) + count(pg, hexclip(pg, S0['p'][1][0], S0['p'][1][1]), scaf)
        f = count(pg, hexclip(pg, S0['fire'][0], S0['fire'][1], 90, 90, 20), fire)
        l = count(pg, hexclip(pg, S0['city'][0], S0['city'][1], 150, 150, 0), lab)
        return a, f, l
    m0 = meas(); B.shot(pg, 'd1_before', 100)
    nw = pg.evaluate(WIPE); pg.wait_for_timeout(500); lost = pg.evaluate('R3.renderer.getContext().isContextLost()')
    pg.evaluate('() => { EXT.restoreContext(); }'); pg.wait_for_timeout(900)
    st = pg.evaluate('() => [R3.renderer.getContext().isContextLost(), R3.refreshN || 0]'); pg.evaluate('() => { requestDraw(); }'); pg.wait_for_timeout(700)
    m1 = meas(); B.shot(pg, 'd2_after', 100)
    print('      그림판 %d개를 비우고 문맥을 끊었다 이었다 · 비계 · 불꽃 · 이름표의 점: 전 %s → 뒤 %s' % (nw, m0, m1))
    ok(nw >= 20 and lost and st == [False, 1], '흉내: 그림판 %d개의 내용을 지우고 WebGL 문맥을 끊었다가 다시 이었다 — 복구 뒤 다시 올리기가 한 번 돌았다' % nw)
    ok(m0[0] > 150 and m0[1] > 150 and m0[2] > 400, '그 전: 공사장의 비계 %d점 · 불꽃 %d점 · 이름표 %d점이 보인다' % m0)
    ok(m0[0] * 0.9 <= m1[0] <= m0[0] * 1.1 and m1[1] > m0[1] * 0.4 and m0[2] * 0.95 <= m1[2] <= m0[2] * 1.05, '그 뒤에도 그대로 보인다: 비계 %d · 불꽃 %d(일렁인다) · 이름표 %d (0.21 에서는 셋 다 사라졌다)' % m1)
    pg.evaluate('''() => { document.dispatchEvent(new Event('visibilitychange')); }'''); pg.wait_for_timeout(500)
    ok(pg.evaluate('R3.refreshN') == 2, '화면으로 돌아올 때(visibilitychange)에도 코드로 그린 그림을 다시 올린다')
    pg.evaluate('''() => { for (var k in G.fires) delete G.fires[k]; syncScene(); requestDraw(); }''')

def steps2(pg):
    """느리게 돌려서 연출 도중을 본다(시계를 늦춘다 — 따로 연 창에서)."""
    B.start(pg, 0)
    S = pg.evaluate(D2.SETUP)
    pg.evaluate('(s) => { window.S = s; talkHide(); UI.talk = false; }', S)
    f = S['f']; SLOW = 0.1
    PROBE = '''() => { var o = {};
      o.foe = S.foe.map(function (id) { var x = R3.units[id]; return x ? [x.g.visible ? 1 : 0, x.sig.split('|')[3]] : null; });
      o.mine = S.mine.map(function (id) { var x = R3.units[id]; return x ? [x.g.visible ? 1 : 0, x.sig.split('|')[3]] : null; });
      if (S.base !== undefined) { var b = R3.bases[S.base], gb = G.bases[S.base]; o.base = [b.sig.split('|')[0], b.zcol || '', gb.owner, R3.ovData[K(gb.c + 1, gb.r) * 4 + 2], gb.plots.filter(function (p, i) { return !!R3.facs[S.base + ':' + i]; }).length, gb.plots.filter(function (p) { return !!p.fac; }).length]; }
      o.busy = UI.busy; o.held = [Object.keys(R3.bhold).length, Object.keys(R3.units).filter(function (k) { return R3.units[k].keep; }).length]; return o; }'''
    def case(name, js, times=(60, 200, 380)):
        pg.evaluate(D2.SLOWJS, SLOW); pg.evaluate(js)
        last = 0; out = []
        for i, t in enumerate(times):
            pg.wait_for_timeout(max(1, (t - last) / SLOW - 120)); last = t; out.append(pg.evaluate(PROBE))
            if i == 1: pg.screenshot(path=os.path.join(B.SHOTS, 'e_%s.png' % name))
        pg.wait_for_function('() => !UI.busy', timeout=120000); pg.wait_for_timeout(3000)
        out.append(pg.evaluate(PROBE)); return out
    print('⑩ 친 다음에 바뀐다 — 궤멸')
    pg.evaluate('([c, r]) => { jumpTo(c, r, 0.8); requestDraw(); }', f); pg.wait_for_timeout(700)
    k = case('kill', '''() => { var u = UMAP[S.mine[0]], t = UMAP[S.foe[2]]; placeUnit(t, u.c - 1, u.r); t.troops = 120; syncScene(); u.done = false; u.morale = 100; selectUnit(u, true); UI.target = { kind: 'unit', u: t, c: t.c, r: t.r }; doAct({ kind: 'attack' }); }''')
    for x in k: print('     ', json.dumps(x, ensure_ascii=False))
    ok(all(x['foe'][2] == [1, '12'] for x in k[:3]) and pg.evaluate('!UMAP[S.foe[2]]'), '궤멸할 부대(120명)의 그림과 이름표가 치는 동안 그대로 서 있다(싸움터를 당겨 보이는 0.3초 · 치는 순간) — 0.21 에서는 치기 전에 사라졌다')
    ok(k[3]['foe'][2] is None and k[3]['held'] == [0, 0] and not k[3]['busy'], '연출이 끝나면 사라진다 · 붙잡아 둔 것이 남지 않는다')
    print('⑩ 친 다음에 바뀐다 — 함락 · ⑦ 시설의 일부가 부서진다')
    r = pg.evaluate('''() => { var u = UMAP[S.mine[1]], eb = G.bases[baseByName('복양')]; eb.troops = 60; eb.dur = 5;
      eb.plots.forEach(function (p, i) { p.fac = i < 8 ? { t: FAC_ORDER[i % FAC_ORDER.length], lv: 1, done: true, prog: 0, need: 0, rate: 0, hp: FAC_HP } : null; });
      var ns = nbrs(eb.c, eb.r).filter(function (n) { var k = K(n[0], n[1]); return !UAT[k] && BAT[k] === undefined && TCH[k] !== 109 && TCH[k] !== 115 && TCH[k] !== 120; });
      placeUnit(u, ns[0][0], ns[0][1]); u.born = G.turn - 3; u.done = false; u.morale = 100; S.base = eb.id; S.old = eb.owner; syncScene(); jumpTo(eb.c, eb.r, 0.8); requestDraw(); return [eb.n, eb.owner, sackCount(8)]; }''')
    pg.wait_for_timeout(900 / SLOW)
    fl = case('fall', '''() => { var u = UMAP[S.mine[1]], eb = G.bases[S.base]; selectUnit(u, true); UI.target = { kind: 'base', b: eb, c: eb.c, r: eb.r }; doAct({ kind: 'attack' }); }''')
    for x in fl: print('     ', json.dumps(x, ensure_ascii=False))
    old = str(r[1]); tt = T(pg, '#toast') or ''
    ok(all(x['base'][0] == old and x['base'][2] == 0 and x['mine'][1] is not None and x['mine'][1][0] == 1 for x in fl[:3]), '함락한 성: 규칙으로는 이미 내 것이지만(주인 0) 치는 동안 이름표 · 붓 고리는 옛 주인(%s)의 빛이고, 성에 들어간 내 부대도 치는 자리에 서 있다' % old)
    ok(len(set(x['base'][1] for x in fl[:3])) == 1 and fl[3]['base'][1] != fl[0]['base'][1] and len(set(x['base'][3] for x in fl[:3])) == 1 and fl[3]['base'][3] != fl[0]['base'][3], '성역의 붓 고리와 세력권의 빛깔도 연출이 끝난 뒤에 바뀐다(%s → %s)' % (fl[0]['base'][1], fl[3]['base'][1]))
    ok(fl[3]['base'][0] == '0' and fl[3]['mine'][1] is None and fl[3]['held'] == [0, 0], '연출이 끝나면 내 빛깔이 되고, 부대는 성에 들어가 사라진다')
    ok(all(x['base'][4] == 8 for x in fl[:3]) and fl[3]['base'][4] == 8 - r[2] and fl[3]['base'][5] == 8 - r[2] and r[2] == 2, '시설 8곳: 치는 동안에는 지도에 여덟 채가 그대로 있고, 함락 뒤 %d곳이 사라진다(남은 %d곳)' % (r[2], fl[3]['base'][4]))
    ok('함락!' in tt and '시설 2곳 소실' in tt, '알림: ' + tt)
    print('⑩ 걸어 들어가 차지한 빈 거점')
    w = pg.evaluate('''() => { var e = G.bases.filter(function (b) { return b.owner < 0 && b.kind === 'city'; })[0]; if (!e) return null; var u = UMAP[S.mine[2]];
      var ns = nbrs(e.c, e.r).filter(function (n) { var k = K(n[0], n[1]); return !UAT[k] && BAT[k] === undefined && TCH[k] !== 109 && TCH[k] !== 115 && TCH[k] !== 120; });
      placeUnit(u, ns[0][0], ns[0][1]); u.mp = uMaxMp(u); u.done = false; u.moved = false; S.base = e.id; clearSel(); syncScene(); jumpTo(e.c, e.r, 0.9); requestDraw(); return [e.n, e.c, e.r]; }''')
    if w:
        pg.wait_for_timeout(900 / SLOW)
        mv = case('walk', '''() => { var u = UMAP[S.mine[2]], e = G.bases[S.base]; selectUnit(u, true); UI.rc = unitReach(u); doMove(u, e.c, e.r); }''', times=(40, 110))
        for x in mv: print('     ', json.dumps(x, ensure_ascii=False))
        ok(mv[0]['base'][0] == '-1' and mv[0]['base'][2] == 0 and mv[0]['held'][0] == 1 and mv[-1]['base'][0] == '0' and mv[-1]['held'] == [0, 0], '주인 없는 %s: 부대가 걸어 들어가는 동안에는 빈 성의 빛 그대로이고, 닿은 뒤에 내 빛깔이 된다' % w[0])
    else:
        ok(False, '주인 없는 성을 찾지 못했다')
    # AI 의 차례를 보여 줄 때: 남의 부대가 내 성을 함락한다 — 재생 중인 것처럼 꾸며 놓고 그 장면들(공격 → 함락)을 보여 준다
    print('⑩ AI 의 차례를 보여 줄 때 — 내 성이 함락된다')
    a = pg.evaluate('''() => { var B = G.bases[S.base], E = G.bases.filter(function (b) { return b.owner >= 0 && b.owner !== G.player && b.kind === 'city' && idleOfficers(b).length > 0; })[0];
      E.troops = 30000; G.factions[E.owner].ap = 250; var o = idleOfficers(E)[0]; var r = cmdDeploy(E, { type: 'sword', ids: [o.id], troops: 5000, food: 5000 }); if (!r.ok) return r.msg;
      var ns = nbrs(B.c, B.r).filter(function (n) { var k = K(n[0], n[1]); return !UAT[k] && BAT[k] === undefined && TCH[k] !== 109 && TCH[k] !== 115 && TCH[k] !== 120; });
      var X = r.unit; placeUnit(X, ns[0][0], ns[0][1]); X.born = G.turn - 5; X.done = false; X.morale = 100; B.troops = 30; B.dur = 3; S.x = X.id; S.xf = X.f;
      clearSel(); hideSheet(); syncScene(); jumpTo(B.c, B.r, 0.9); requestDraw(); return [B.n, B.owner, E.n, X.f]; }''')
    print('     ', a); pg.wait_for_timeout(900 / SLOW)
    pg.evaluate(D2.SLOWJS, SLOW)
    st = pg.evaluate('''() => { var X = UMAP[S.x], B = G.bases[S.base];
      UI.play = { next: null, skip: false, cam0: { x: cam.x, y: cam.y, z: cam.z }, timer: 0, wake: null, ans: [], batch: [], err: null, minor: 0, shown: 0, save0: null }; UI.busy = true; $('app').classList.add('playing');
      EVQ.length = 0; var res = unitAttack(X, { kind: 'base', b: B, c: B.c, r: B.r }); var raw = EVQ.map(function (e) { return e.t; }), evs = orderEvs(EVQ.splice(0, EVQ.length));
      evs.forEach(function (e) { e.cls = 2; }); evs.forEach(function (e) { holdEv(e); });
      window.PB = { done: false }; presentEvents(evs, function () { PB.done = true; });
      return { ok: res.ok, fell: !!res.fell, raw: raw, evs: evs.map(function (e) { return e.t; }), owner: B.owner }; }''')
    PR = '''() => { var b = R3.bases[S.base], x = R3.units[S.x]; return { shown: b.sig.split('|')[0], zcol: b.zcol, owner: G.bases[S.base].owner, x: x ? (x.g.visible ? 1 : 0) : null, held: [Object.keys(R3.bhold).length, Object.keys(R3.units).filter(function (k) { return R3.units[k].keep; }).length], cap: $('plMsg').textContent, done: PB.done }; }'''
    seq = []
    for t in (80, 420, 700):
        pg.wait_for_timeout(max(1, (t - (seq[-1][0] if seq else 0)) / SLOW - 120)); seq.append((t, pg.evaluate(PR)))
    pg.screenshot(path=os.path.join(B.SHOTS, 'e_ai_fall.png'))
    pg.wait_for_function('() => PB.done', timeout=180000); pg.wait_for_timeout(1500)
    fin = pg.evaluate(PR); pg.evaluate('''() => { UI.play = null; UI.busy = false; $('app').classList.remove('playing'); clearAnimFlags(); requestDraw(); }''')
    print('     ', st); [print('     ', t, json.dumps(x, ensure_ascii=False)) for t, x in seq]; print('      끝', json.dumps(fin, ensure_ascii=False))
    ok(st['ok'] and st['fell'] and st['raw'] == ['fall', 'act'] and st['evs'] == ['act', 'fall'], '규칙은 함락을 먼저 적지만(%s) 보여 줄 때는 치는 장면 다음에 함락 장면이 온다(%s)' % (st['raw'], st['evs']))
    ok(all(x['shown'] == '0' and x['owner'] == a[3] and x['x'] == 1 and x['held'][0] == 1 and '우리 거점을 잃었습니다' not in x['cap'] for t, x in seq[:2]), '치는 장면이 도는 동안: 규칙으로는 이미 남의 성이지만 지도에서는 아직 내 빛깔이고, 성에 들어간 그 부대도 치는 자리에 서 있다')
    ok(fin['shown'] == str(a[3]) and fin['x'] is None and fin['held'] == [0, 0] and fin['done'] and '우리 거점을 잃었습니다' in fin['cap'], '함락 장면("우리 거점을 잃었습니다")이 나온 뒤에 새 주인의 빛깔이 되고, 붙잡아 둔 것이 남지 않는다')

def steps3(pg):
    """④ 합병 — 이각(홍농)으로."""
    B.start(pg, 0)
    print('④ 합병 — 홍농의 붙어 있는 두 농장')
    r = pg.evaluate('''() => { newGame(15, 3); G.aiOnly = false; syncScene(); refreshHud(); clearSel(); talkHide(); UI.talk = false; G.factions[15].ap = 250;
      var hn = G.bases[baseByName('홍농')], ia = PAT[K(113, 97)].i, ib = PAT[K(114, 98)].i; hn.gold = 9000;
      hn.plots.forEach(function (p) { p.fac = null; }); [ia, ib].forEach(function (i) { hn.plots[i].fac = { t: 'farm', lv: 1, done: true, prog: 0, need: 0, rate: 0, hp: FAC_HP }; });
      var o = baseOfficers(hn).filter(function (x) { return x.unit === null; })[0]; if (o) { o.acted = false; o.job = null; }
      syncScene(); selectBase(hn, false, 'fac'); flowFacility(hn, ia); window.T = { b: hn.id, ia: ia, ib: ib };
      return { owner: hn.owner, idle: idleOfficers(hn).length, cand: mergeCandidates(hn, ia) }; }''')
    pg.wait_for_timeout(900)
    btn = pg.evaluate('''() => { var bs = [].slice.call(document.querySelectorAll('#sheet .cmd, #modal .cmd, #sheet .act, #modal .act')), m = bs.filter(function (b) { return b.textContent.indexOf('흡수합병') >= 0; })[0]; return m ? [m.className, m.textContent, m.getAttribute('data-a')] : null; }''')
    print('     ', r, btn); B.shot(pg, 'f1_merge', 100)
    ok(r['cand'] == [pg.evaluate('T.ib')] and btn and 'off' not in btn[0] and '인접한 같은 시설 필요' not in btn[1], '(113,97) · (114,98)의 두 농장: [흡수합병]이 켜져 있다 — %s' % (btn[1] if btn else btn))
    if btn and btn[2]:
        pg.evaluate('''() => { var bs = [].slice.call(document.querySelectorAll('#sheet .cmd, #modal .cmd, #sheet .act, #modal .act')), m = bs.filter(function (b) { return b.textContent.indexOf('흡수합병') >= 0; })[0]; m.click(); }'''); pg.wait_for_timeout(600)
        st = pg.evaluate('''() => { return { modal: !!MODAL, rows: document.querySelectorAll('#modal .row').length, h: document.querySelector('#modal .dlg-h h2') ? document.querySelector('#modal .dlg-h h2').textContent : '' }; }''')
        print('     ', st)
        ok(st['modal'], '누르면 합병할 무장을 고르는 창이 열린다 [%s]' % st['h'])

class Rec:
    pass
INIT = "(function(){ var oc = document.createElement; window.CVS = []; document.createElement = function (t) { var e = oc.apply(document, arguments); if (String(t).toLowerCase() === 'canvas') window.CVS.push(e); return e; }; })();"
def run(steps, w, h, dpr, init=None):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        cxt = br.new_context(viewport={'width': w, 'height': h}, device_scale_factor=dpr, is_mobile=True, has_touch=True, locale='ko-KR')
        if init: cxt.add_init_script(init)
        cxt.add_init_script("document.addEventListener('DOMContentLoaded', function () { try { if (window.DUEL_K) { DUEL_K.rate = 0; if (DUEL_K.aiAsk !== undefined) DUEL_K.aiAsk = 0; } if (window.DIP_K && DIP_K.aiPact !== undefined) { DIP_K.aiPact = 0; DIP_K.aiPactUp = 0; } if (window.UI && UI.pct !== undefined) UI.pct = true; if (window.UI) UI.video = false; } catch (e) {} });")
        pg = cxt.new_page()
        pg.on('console', lambda m: B.errors.append(m.type + ': ' + m.text) if m.type in ('error', 'warning') else None)
        pg.on('pageerror', lambda e: B.errors.append('pageerror: ' + str(e)))
        pg.goto(os.environ.get('URL0') or B.URL)
        pg.wait_for_function('window.R3 && R3.ready', timeout=60000); pg.wait_for_timeout(600)
        steps(pg); br.close()
which = sys.argv[1] if len(sys.argv) > 1 else 'all'
if which in ('all', '1'): run(steps, 393, 852, 2, INIT)
if which in ('all', '2'): run(steps2, 393, 852, 2)
if which in ('all', '3'): run(steps3, 393, 852, 2)
errs = [e for e in B.errors if 'ReadPixels' not in e and 'ERR_FILE' not in e and 'GPU stall' not in e]
print('오류 기록:', errs[:6])
ok(not errs, '오류 · 경고 기록이 없다(%d건)' % len(errs))
print('\nd36: %d fail' % len(fails))
for f in fails: print('  ✗', f)
sys.exit(1 if fails else 0)
