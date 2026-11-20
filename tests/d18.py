# v0.9.2 — 화면 조작으로 확인
#   1) 글 덜어내기: STATUS 창의 네 단추가 없어졌는가, '지금 할 일'이 한 줄씩인가, 시작 안내·보호 풀이·전법 풀이·도움말이 짧아졌는가(보이는 글자 수의 한도)
#   2) 건설 자리 비추기: 건설 탭을 열면 지도가 어두워지고 지을 수 있는 빈 부지만 뚫려 밝은가, 목록과 지도의 번호가 같은가,
#      칸을 고르면 그 칸이 창 위로 보이고 붉은 테두리가 붙는가, 다른 밝은 칸을 누르면 자리가 바뀌는가, 어두운 곳을 누르면 닫히는가,
#      카드의 수입(금/월·병량/분기)이 규칙의 값과 같은가, 고른 바로 그 칸에 지어지는가, 못 짓는 까닭(무장·금·행동력·부대)이 보이는가, 탭을 떠나면 걷히는가
#   python3 tests/d18.py          찍은 그림은 tests/shots18/
import sys, os, math, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import taphex, tapsel
B.SHOTS = os.path.join(B.ROOT, 'shots18')
os.makedirs(B.SHOTS, exist_ok=True)
fails = []
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)
def chars(pg, sel, vis=True):
    return pg.evaluate('([s, vis]) => { var e = document.querySelector(s); if (!e) return -1; return (vis ? e.innerText : e.textContent).replace(/\\s+/g, "").length; }', [sel, vis])
# 덮개(#spot)의 한 점: [r, g, b, a]
PIX = '''function pix(x, y) { var d = SPOT.x.getImageData(Math.round(x * DPR), Math.round(y * DPR), 1, 1).data; return [d[0], d[1], d[2], d[3]]; }
function lotPts(l) { var p = hexPos(l.c, l.r), q = w2s(p[0], p[1], p[2]), ppu = pxPerUnit(q[2]), R = hexRing(l.c, l.r, 1), gold = 0, red = 0;
  R.forEach(function (v) { var d = pix(v[0], v[1]); if (d[3] >= 200 && d[0] >= 190 && d[1] >= 140 && d[2] <= 110) gold++; if (d[3] >= 200 && d[0] >= 150 && d[1] <= 110 && d[2] <= 100) red++; });      // 테두리 12점 가운데 금빛·붉은빛인 점의 수(옆 칸과 맞닿은 변은 나중에 그린 쪽 빛이다)
  return { c: [q[0], q[1]], ppu: ppu, inside: pix(q[0] + ppu * 0.64, q[1]), corner: pix(R[0][0], R[0][1]), gold: gold, red: red, top: Math.min.apply(null, R.map(function (v) { return v[1]; })) }; }'''
def view(pg):
    return pg.evaluate('''(() => { %s
      var v = buildView(), sa = safeArea(), sp = $("spot");
      if (!v) return { on: false, cls: sp.className, a: SPOT.a, app: $("app").className, mini: getComputedStyle($("mini")).display };
      return { on: true, cls: sp.className, a: SPOT.a, app: $("app").className, mini: getComputedStyle($("mini")).display, b: v.b.id, pi: v.pi, why: v.why, sa: [sa.top, sa.bottom], CW: CW, CH: CH, z: cam.z,
        lots: v.lots.map(function (l) { var t = lotPts(l); return { i: l.i, n: l.n, ok: l.ok, c: l.c, r: l.r, x: t.c[0], y: t.c[1], ppu: t.ppu, inside: t.inside, corner: t.corner, gold: t.gold, red: t.red, top: t.top }; }),
        facs: v.facs.map(function (f) { var p = hexPos(f.c, f.r), q = w2s(p[0], p[1], p[2]), ppu = pxPerUnit(q[2]); return { n: f.n, done: f.done, dark: pix(q[0], q[1] - ppu * 0.5) }; }),
        far: pix(12, sa.top + 12), lab: R3.bases[v.b.id].lab.sp.visible };
    })()''' % PIX)
def rows(pg):
    # [부지 번호(b.plots 의 자리), 단추의 번호('' = 지은 시설의 줄), 클래스, 글]
    return pg.evaluate('''Array.prototype.map.call(document.querySelectorAll("#sheet [data-a=plot]"), function (e) { var lot = e.classList.contains("lot"); return [+e.getAttribute("data-v"), lot ? e.textContent : "", e.className, e.innerText.replace(/\\n+/g, " / ")]; })''')
def steps(pg):
    # ================= 1. 글 덜어내기 =================
    tapsel(pg, '#tNew'); pg.wait_for_timeout(300)
    tapsel(pg, '#modal .row', 2); pg.wait_for_timeout(200)
    tapsel(pg, '#modal [data-a=go]'); pg.wait_for_timeout(600)
    li = pg.evaluate('document.querySelectorAll("#modal .dlg-b li").length'); n0 = chars(pg, '#modal .dlg')
    ok(li <= 4 and 0 < n0 <= 200, '시작 안내: 항목 %d개(4개까지), 보이는 글 %d자(200자까지 — 0.9.1 은 412자)' % (li, n0))
    tapsel(pg, '#modal [data-a=close]'); pg.wait_for_timeout(500)
    pg.evaluate('() => { newGame(2, 4242); saveGame(); }')                      # 같은 판으로(씨앗을 정해 둔다)
    pg.reload(); pg.wait_for_function('window.R3 && R3.ready', timeout=60000); pg.wait_for_timeout(600)
    tapsel(pg, '#tCont'); pg.wait_for_timeout(1200)
    if pg.evaluate('!!MODAL'): pg.evaluate('closeDialog()')
    pg.evaluate('() => { clearSel(); }'); pg.wait_for_timeout(300)
    home = pg.evaluate('''(() => { var s = $("sheet"); return { v: GAME_VERSION, links: s.querySelectorAll(".hm-links, .hm-links button, .hm-stats").length, pz: !!s.querySelector("button.pz"), adv: !!s.querySelector(".hm-adv"),
      todos: Array.prototype.map.call(s.querySelectorAll(".todo"), function (t) { var b = t.querySelector("b"), sm = t.querySelector("small"); return [t.offsetHeight, b ? b.getBoundingClientRect().height : 0, sm ? sm.getBoundingClientRect().height : 0, t.innerText.replace(/\\n+/g, " / ")]; }) }; })()''')
    n1 = chars(pg, '#sheet')
    print('  STATUS 창:', home['todos'])
    ok(home['v'] == 'v0.9.3', '판 번호 v0.9.3 [%s]' % home['v'])
    ok(home['links'] == 0 and home['pz'] and home['adv'], 'STATUS 창: 거점·부대·무장·천하 네 단추와 숫자 띠가 없다 / 보호 표와 군사 단추는 있다')
    ok(len(home['todos']) >= 1 and all(t[0] <= 60 and t[1] <= 24 and t[2] <= 20 for t in home['todos']), "'지금 할 일'은 줄마다 한 줄씩(제목 한 줄 + 풀이 한 줄, 높이 60 이하) — %d줄" % len(home['todos']))
    ok(0 < n1 <= 150, 'STATUS 창의 보이는 글 %d자(150자까지 — 0.9.1 은 같은 판에서 302자)' % n1)
    pg.evaluate('showPeaceInfo()'); pg.wait_for_timeout(250); n2 = chars(pg, '#modal .dlg'); pg.evaluate('closeDialog()')
    ok(0 < n2 <= 160, '초반 보호 풀이 %d자(160자까지 — 0.9.1 은 307자)' % n2)
    pg.evaluate('showHelp()'); pg.wait_for_timeout(250)
    hv, ha = chars(pg, '#modal .dlg'), chars(pg, '#modal .dlg', False)
    hs = pg.evaluate('[document.querySelectorAll("#modal details").length, document.querySelectorAll("#modal details[open]").length]')
    ok(hs[0] >= 20 and hs[1] == 0 and hv <= 200 and ha > 3000, '도움말: 토막 %d개가 모두 접혀 있다 — 보이는 글 %d자(제목만), 전체 %d자' % (hs[0], hv, ha))
    pg.evaluate('''Array.prototype.forEach.call(document.querySelectorAll("#modal details summary"), function (s) { if (/도시와 시설/.test(s.textContent)) s.click(); })'''); pg.wait_for_timeout(200)
    hb = pg.evaluate('document.querySelector("#modal .dlg-b").innerText')
    ok('건설 탭을 열면' in hb and '지을 수 있는 빈 부지만 밝게' in hb and '점선' in hb, "도움말 '도시와 시설'을 펼치면 건설 자리 풀이가 있다")
    pg.evaluate('closeDialog()'); pg.wait_for_timeout(200)

    # ================= 2. 건설 자리 비추기 =================
    info = pg.evaluate('''(() => { var b = facCities(G.player)[0]; G.factions[G.player].ap = 200; b.gold = 800; b.order = 75; selectBase(b);
      return { id: b.id, n: b.n, plots: b.plots.length, empty: b.plots.filter(function (p) { return !p.fac; }).length, tabs: Array.prototype.map.call(document.querySelectorAll("#sheet .tabs button"), function (t) { return t.textContent; }) }; })()''')
    pg.wait_for_timeout(600)
    v0 = view(pg)
    ok(info['tabs'] == ['내정', '출진', '인재', '건설'], '거점 창의 탭: 내정 · 출진 · 인재 · 건설 %s' % info['tabs'])
    ok(not v0['on'] and 'on' not in v0['cls'] and v0['mini'] != 'none', '내정 탭에서는 덮개가 없다(작은 지도도 그대로)')
    B.shot(pg, 'd18_01_base', 200)
    tapsel(pg, '#sheet .tabs button[data-v=fac]'); pg.wait_for_timeout(900)
    v = view(pg); rw = rows(pg)
    B.shot(pg, 'd18_02_build', 200)
    print('  덮개:', {k: v[k] for k in ('cls', 'a', 'app', 'mini', 'pi', 'why', 'sa', 'z', 'far', 'lab')}); print('  칸:', [(l['n'], l['i'], l['ok'], round(l['x']), round(l['y']), l['inside'][3], l['corner'][:3]) for l in v['lots']])
    ok(v['on'] and 'on' in v['cls'] and abs(v['a'] - 1) < 0.01 and 'building' in v['app'], '건설 탭을 열면 덮개가 켜진다(#spot.on, 불투명도 %.2f)' % v['a'])
    ok(len(v['lots']) == info['empty'] and v['pi'] == -1 and v['why'] == '', '빈 부지 %d곳이 모두 대상(아직 고른 칸 없음)' % info['empty'])
    ok(v['far'][3] >= 150, '부지가 아닌 곳은 어둡다(덮개의 불투명도 %d/255)' % v['far'][3])
    ok(all(l['ok'] and l['inside'][3] <= 12 for l in v['lots']), '지을 수 있는 칸은 모두 뚫려 있다(칸 안의 덮개 불투명도 %s)' % sorted(set(l['inside'][3] for l in v['lots'])))
    ok(all(l['gold'] == 12 and l['red'] == 0 for l in v['lots']), '밝은 칸의 테두리는 금빛 %s (칸마다 테두리 12점 모두)' % v['lots'][0]['corner'])
    ok(len(v['facs']) == info['plots'] - info['empty'] and all(f['dark'][3] >= 150 for f in v['facs']), '이미 지은 시설 %d곳은 어두운 채(이름만 적힌다: %s)' % (len(v['facs']), '·'.join(f['n'] for f in v['facs'])))
    ok(all(v['sa'][0] <= l['top'] and l['y'] + l['ppu'] <= v['sa'][1] + 2 and 0 <= l['x'] - l['ppu'] * 0.87 and l['x'] + l['ppu'] * 0.87 <= v['CW'] for l in v['lots']), '빈 부지가 모두 창에 가려지지 않은 지도 영역(%d~%d) 안에 들어온다 — 확대 %.2f' % (v['sa'][0], v['sa'][1], v['z']))
    ok(min(l['ppu'] for l in v['lots']) * 1.73 >= 40, '칸의 너비가 손가락으로 누를 만하다(가장 작은 칸 %d px)' % round(min(l['ppu'] for l in v['lots']) * 1.73))
    ok(v['mini'] == 'none' and v['lab'] is False, '그동안 작은 지도와 이 거점의 이름표는 숨는다(칸을 가리지 않게)')
    em = [r for r in rw if r[1]]
    ok([r[0] for r in em] == [l['i'] for l in v['lots']] and [r[1] for r in em] == [str(l['n']) for l in v['lots']], '창의 번호 단추와 지도의 칸: 같은 차례 · 같은 번호 %s' % [r[1] for r in em])
    # v0.9.3: 번호는 부지마다 정해져 있다 — 성을 가운데 두고 북쪽에서 시계 방향으로 1, 2, 3 … (지은 칸의 번호는 건너뛴다)
    geo = pg.evaluate('(id) => { var b = G.bases[id], c0 = hexCenter(b.c, b.r); return b.plots.map(function (p, i) { var q = hexCenter(p.c, p.r); return [i, q[0] - c0[0], q[1] - c0[1], !p.fac]; }); }', info['id'])
    rank = sorted(geo, key=lambda g: (round((math.atan2(g[1], -g[2]) + 2 * math.pi) % (2 * math.pi), 6), g[1] * g[1] + g[2] * g[2]))
    lotno = dict((g[0], k + 1) for k, g in enumerate(rank))                     # 부지 자리 → 번호
    nums = [l['n'] for l in v['lots']]
    ok(nums == sorted(nums) and len(set(nums)) == len(nums) and all(1 <= n <= info['plots'] for n in nums) and all(lotno[l['i']] == l['n'] for l in v['lots']), '번호는 부지마다 고정: 성의 북쪽에서 시계 방향으로 1~%d, 빈 칸만 차례대로 %s' % (info['plots'], nums))
    ok(nums != list(range(1, len(nums) + 1)) or info['empty'] == info['plots'], '지은 시설이 있는 번호는 건너뛴다(다시 1부터 매기지 않는다) — 지은 칸의 번호 %s' % sorted(lotno[g[0]] for g in geo if not g[3]))
    scr = pg.evaluate('(id) => { var b = G.bases[id], p = hexPos(b.c, b.r), q = w2s(p[0], p[1], p[2]); return [q[0], q[1]]; }', info['id'])
    ang = [(math.degrees(math.atan2(l['x'] - scr[0], -(l['y'] - scr[1]))) + 360) % 360 for l in v['lots']]
    turn = sum(1 for k in range(1, len(ang)) if ang[k] + 12 < ang[k - 1])
    ok(turn == 0, '화면에서도 번호가 시계 방향으로 돈다(성에서 본 방향 %s도)' % [round(a) for a in ang])
    lotrow = pg.evaluate('''(() => { var e = document.querySelectorAll("#sheet .lot"), r0 = e[0].getBoundingClientRect(); return [r0.width, r0.height, document.querySelector("#sheet .lots").offsetHeight, document.querySelectorAll("#sheet .row[data-a=plot]").length]; })()''')
    ok(lotrow[0] >= 40 and lotrow[1] >= 40 and lotrow[2] <= 130 and lotrow[3] == info['plots'] - info['empty'], '빈 부지는 번호 단추 한두 줄(단추 %dpx, 묶음 높이 %dpx) — 줄로 늘어선 것은 지은 시설 %d곳뿐' % (lotrow[0], lotrow[2], lotrow[3]))
    secs = pg.evaluate('Array.prototype.map.call(document.querySelectorAll("#sheet .sh-body .sec"), function (e) { return e.textContent.replace(/\\s+/g, " ").trim(); })')
    ok(any(s.startswith('빈 부지') and s.endswith(str(info['empty'])) for s in secs) and any(s.startswith('지은 시설') for s in secs) and not pg.locator('#sheet .lotw').count(), '창: [빈 부지 %d] · [지은 시설 %d], 못 짓는 까닭 줄은 없다 %s' % (info['empty'], info['plots'] - info['empty'], secs))

    # --- 지도에서 칸을 고른다
    mk = pg.evaluate('''(id) => { var b = G.bases[id], out = { mk: [], far: [], pair: null, lone: null };      // 시장 옆 칸 / 시장 옆이 아닌 칸, 병영 옆 칸 / 아닌 칸
      b.plots.forEach(function (p, i) { if (p.fac) return; var m = adjFacCount(b, i, "market"), k = adjFacCount(b, i, "barracks"); (m ? out.mk : out.far).push(i); if (k && out.pair === null) out.pair = i; if (!k && out.lone === null) out.lone = i; });
      return out; }''', info['id'])
    print('  칸의 이웃:', mk)
    A = [l for l in v['lots'] if l['i'] == mk['mk'][0]][0]
    cam0 = pg.evaluate('[cam.x, cam.y, cam.z]')
    taphex(pg, A['c'], A['r']); pg.wait_for_timeout(900)
    d = pg.evaluate('''(() => { var m = $("modal"), dl = m.querySelector(".dlg"), r = dl ? dl.getBoundingClientRect() : null, body = m.querySelector(".dlg-b");
      return { dev: MODAL && MODAL.dev ? [MODAL.dev.b, MODAL.dev.pi] : null, see: m.classList.contains("see"), app: $("app").className, title: (m.querySelector("h2") || {}).textContent, top: r ? r.top : 0, h: r ? r.height : 0, CH: CH,
        bg: getComputedStyle(m).backgroundColor, sheet: getComputedStyle($("sheet")).visibility, bar: getComputedStyle($("bar")).visibility, scroll: body ? [body.scrollHeight, body.clientHeight] : null,
        cards: Array.prototype.map.call(m.querySelectorAll(".row[data-a=f]"), function (e) { var ds = e.querySelector(".ds"); return [e.getAttribute("data-v"), e.querySelector(".nm").childNodes[0].textContent, ds.textContent, ds.className.replace("ds", "").trim(), e.classList.contains("dim"), e.querySelector(".cost").textContent, Math.round(e.getBoundingClientRect().bottom)]; }) }; })()''')
    v2 = view(pg); S = [l for l in v2['lots'] if l['i'] == A['i']][0]
    B.shot(pg, 'd18_03_choose', 200)
    print('  고르는 창:', {k: d[k] for k in ('dev', 'see', 'app', 'title', 'top', 'h', 'bg', 'sheet', 'bar', 'scroll')}); [print('    ', c) for c in d['cards']]
    mark = chr(0x245F + A['n'])
    ok(d['dev'] == [info['id'], A['i']] and v2['pi'] == A['i'], '밝은 칸 %s을 누르면 그 칸을 고른 채 창이 열린다' % mark)
    ok(d['title'] == '%s %s — 무엇을 지을까요' % (info['n'], mark), '창의 제목에 고른 칸의 번호 [%s]' % d['title'])
    ok(d['see'] and 'seeing' in d['app'] and d['bg'] in ('rgba(0, 0, 0, 0)', 'transparent') and d['sheet'] == 'hidden' and d['bar'] == 'hidden', '창은 지도를 덮지 않는다(바탕 투명, 아래 창·단추 줄은 숨김)')
    ok(d['h'] <= d['CH'] * 0.5 + 1 and d['top'] >= d['CH'] * 0.5 - 1, '창은 화면의 절반 아래만 차지한다(높이 %d / 화면 %d)' % (d['h'], d['CH']))
    ok(len(d['cards']) == 8 and d['scroll'][0] <= d['scroll'][1] + 1 and all(c[6] <= d['CH'] for c in d['cards']), '여덟 시설이 밀어 올리지 않고 한 번에 보인다(내용 %d ≤ 창 %d)' % (d['scroll'][0], d['scroll'][1]))
    ok(v2['sa'][0] <= S['top'] - 20 and S['y'] + S['ppu'] <= d['top'] and 0 < S['x'] < v2['CW'], '고른 칸이 창 위로 보인다(칸의 세로 %d~%d, 창의 위 끝 %d)' % (S['top'], S['y'] + S['ppu'], d['top']))
    ok(S['red'] >= 10 and S['gold'] == 0, '고른 칸의 테두리는 붉다 %s (12점 가운데 %d점)' % (S['corner'], S['red']))
    ok(all(l['gold'] >= 7 for l in v2['lots'] if l['i'] != A['i']) and all(l['inside'][3] <= 12 for l in v2['lots']), '다른 빈 부지는 금빛 그대로 밝다(바꿔 고를 수 있다) %s' % [l['gold'] for l in v2['lots'] if l['i'] != A['i']])
    here = pg.evaluate('''(() => { %s var v = buildView(), l = v.lots.filter(function (x) { return x.i === v.pi; })[0], t = lotPts(l); return pix(t.c[0], t.top - 20); })()''' % PIX)
    ok(here[0] >= 150 and here[1] <= 110 and here[3] >= 200, "고른 칸 위에 붉은 '여기' 표 %s" % here)
    # 카드의 값 = 규칙의 값
    want = pg.evaluate('''([id, pi]) => { var b = G.bases[id], p = b.plots[pi], g0 = goldIncome(b), f0 = foodIncome(b), out = {};
      ["market", "farm", "mint", "granary"].forEach(function (t) { p.fac = { t: t, lv: 1, done: true, prog: 0, need: 0, rate: 0, hp: FAC_HP }; out[t] = [goldIncome(b) - g0, foodIncome(b) - f0]; p.fac = null; });
      out.adj = { market: adjFacCount(b, pi, "market"), farm: adjFacCount(b, pi, "farm"), barracks: adjFacCount(b, pi, "barracks"), smithy: adjFacCount(b, pi, "smithy") };
      out.lv = { barracks: bestFacLv(b, "barracks"), smithy: bestFacLv(b, "smithy"), stable: bestFacLv(b, "stable"), workshop: bestFacLv(b, "workshop") }; out.gold = b.gold; return out; }''', [info['id'], A['i']])
    print('  규칙의 값:', want)
    C = {c[0]: c for c in d['cards']}
    ok(C['market'][2] == '금 +{:,}/월'.format(want['market'][0]) and want['market'][0] > 0, '시장 카드: 이 자리에 지으면 %s — 수입 셈(goldIncome)의 차와 같다' % C['market'][2])
    ok(C['farm'][2] == '병량 +{:,}/분기'.format(want['farm'][1]) and want['farm'][1] > 0, '농장 카드: %s — foodIncome 의 차와 같다' % C['farm'][2])
    ok(want['adj']['market'] >= 1 and want['mint'][0] > 0 and C['mint'][2] == '금 +{:,}/월'.format(want['mint'][0]) and C['mint'][3] == '', '조폐 카드(시장 옆 칸): %s' % C['mint'][2])
    ok((C['granary'][2] == '옆에 농장 없음' and C['granary'][3] == 'no') if want['granary'][1] == 0 else C['granary'][2] == '병량 +{:,}/분기'.format(want['granary'][1]), '곡창 카드: %s [%s]' % (C['granary'][2], C['granary'][3]))
    for t, nm in [('barracks', '병영'), ('smithy', '대장간')]:
        exp = ('옆 %s과 합병 가능' % nm, 'ok') if (want['lv'][t] and want['adj'][t]) else (('이미 있음 (Lv%d)' % want['lv'][t], 'warn') if want['lv'][t] else None)
        ok(exp is None or (C[t][2], C[t][3]) == exp, '%s 카드: %s [%s]' % (nm, C[t][2], C[t][3]))
    ok(C['stable'][2] == '군마 생산' and C['workshop'][2] == '충차 생산' and want['lv']['stable'] == 0, '없는 시설의 카드는 쓰임만: 마구간 [%s] · 공방 [%s]' % (C['stable'][2], C['workshop'][2]))
    ok(all(c[5].startswith('금 ') for c in d['cards']) and all(len(c[2]) <= 13 for c in d['cards']), '카드의 풀이는 한 줄(가장 긴 것 %d자)' % max(len(c[2]) for c in d['cards']))

    # 드문 경우의 카드 글(규칙을 바로 불러 확인 — 부지를 잠깐 바꿨다가 되돌린다)
    edge = pg.evaluate('''(id) => { var b = G.bases[id], E = [], keep = b.plots.map(function (p) { return p.fac; }), out = {}, x = -1, y = -1, i, j;
      b.plots.forEach(function (p, k) { if (!p.fac) E.push(k); });
      function F(t, done) { return { t: t, lv: 1, done: done, prog: 0, need: 100, rate: 50, hp: FAC_HP, by: [] }; }
      function adj(m, n) { return hdist(b.plots[m].c, b.plots[m].r, b.plots[n].c, b.plots[n].r) === 1; }
      var best = -1;                                                                                           // 맞닿은 빈 부지 둘: x 에 시장을 두고 y 에서 조폐를 본다(x 옆에 빈 부지가 둘 더 있는 짝을 먼저)
      for (i = 0; i < E.length; i++) for (j = 0; j < E.length; j++) if (i !== j && adj(E[i], E[j]) && !adjFacCount(b, E[j], "market")) {
        var more = E.filter(function (k) { return k !== E[i] && k !== E[j] && adj(k, E[i]); }).length;
        if (more > best) { best = more; x = E[i]; y = E[j]; }
      }
      out.xy = [x, y];
      b.plots[x].fac = F("market", false); out.soon = lotEffect(b, y, "mint");
      b.plots[x].fac = F("market", true); out.now = lotEffect(b, y, "mint"); out.gain = gainAt(b, y, "mint").gold;
      b.plots[x].fac = null;
      // 조폐가 이미 둘 붙은 시장: 이웃 부지가 셋 이상인 부지 X 에 시장을 두고, 이웃 둘에 조폐를, 남은 빈 이웃 Y 에서 조폐를 본다(다른 시장은 잠깐 치운다)
      for (i = 0; i < b.plots.length && !out.full; i++) {
        var nb = []; for (j = 0; j < b.plots.length; j++) if (j !== i && adj(i, j)) nb.push(j);
        var ye = nb.filter(function (k) { return !keep[k]; });
        if (nb.length < 3 || !ye.length) continue;
        var Y = ye[0], ms = nb.filter(function (k) { return k !== Y; }).slice(0, 2);
        b.plots.forEach(function (p, k) { if (p.fac && p.fac.t === "market") p.fac = F("farm", true); });
        b.plots[i].fac = F("market", true); b.plots[ms[0]].fac = F("mint", true); b.plots[ms[1]].fac = F("mint", true);
        out.full = lotEffect(b, Y, "mint"); out.fullGain = gainAt(b, Y, "mint").gold; out.fullAt = [i, Y, ms];
        b.plots.forEach(function (p, k) { p.fac = keep[k]; });
      }
      var bi = -1; b.plots.forEach(function (p, k) { if (p.fac && p.fac.t === "barracks") bi = k; });
      if (bi >= 0) { b.plots[bi].fac = F("barracks", false); out.building = lotEffect(b, y, "barracks"); b.plots[bi].fac = null; out.none = lotEffect(b, y, "barracks"); }
      b.plots.forEach(function (p, k) { p.fac = keep[k]; });
      out.same = JSON.stringify(b.plots.map(function (p) { return p.fac ? p.fac.t : 0; })) === JSON.stringify(keep.map(function (f) { return f ? f.t : 0; }));
      return out; }''', info['id'])
    print('  드문 경우:', edge)
    ok(edge['soon'] == ['옆 시장 완공 뒤 효과', 'warn'], '조폐 카드: 옆의 시장이 아직 짓는 중이면 %s' % edge['soon'])
    ok(edge['now'] == ['금 +{:,}/월'.format(edge['gain']), ''] and edge['gain'] > 0, '조폐 카드: 그 시장이 완공되어 있으면 %s' % edge['now'])
    ok(edge.get('full') == ['효과 없음 (2곳까지)', 'no'] and edge.get('fullGain') == 0, '조폐 카드: 그 시장에 조폐가 이미 둘 붙어 있으면 %s' % edge.get('full'))
    ok(edge.get('building') == ['이미 짓는 중', 'warn'] and edge.get('none') == ['징병', ''], '병영 카드: 짓는 중인 것만 있으면 %s, 하나도 없으면 %s' % (edge.get('building'), edge.get('none')))
    ok(edge['same'], '확인하느라 바꾼 부지는 그대로 되돌렸다')

    # --- 다른 밝은 칸을 누르면 자리가 바뀐다 / 조폐: 시장 옆이 아니면 붉게
    if mk['far']:
        Bf = [l for l in v2['lots'] if l['i'] == mk['far'][0]][0]
        taphex(pg, Bf['c'], Bf['r']); pg.wait_for_timeout(600)
        d2 = pg.evaluate('''(() => { var m = $("modal"); return { dev: MODAL && MODAL.dev ? MODAL.dev.pi : null, title: (m.querySelector("h2") || {}).textContent, mint: (function (e) { var ds = e.querySelector(".ds"); return [ds.textContent, ds.className]; })(m.querySelector(".row[data-v=mint]")), depth: MSTACK.length }; })()''')
        v3 = view(pg); S3 = [l for l in v3['lots'] if l['i'] == Bf['i']][0]; O3 = [l for l in v3['lots'] if l['i'] == A['i']][0]
        ok(d2['dev'] == Bf['i'] and d2['title'].startswith('%s %s' % (info['n'], chr(0x245F + Bf['n']))) and d2['depth'] == 0, '창을 띄운 채 다른 밝은 칸을 누르면 자리가 바뀐다 [%s]' % d2['title'])
        ok(S3['red'] >= 10 and O3['red'] <= 3 and O3['gold'] >= 7, '붉은 테두리도 새 칸으로 옮겨 간다(새 칸 붉은 점 %d, 먼저 칸 금빛 점 %d)' % (S3['red'], O3['gold']))
        ok(d2['mint'][0] == '옆에 시장 없음' and 'no' in d2['mint'][1], '조폐 카드(시장 옆이 아닌 칸): 붉게 [%s]' % d2['mint'][0])
        B.shot(pg, 'd18_04_other', 200)
    # --- 어두운 곳을 누르면 닫힌다
    dark = pg.evaluate('''(id) => { var b = G.bases[id], sa = safeArea(), out = null;
      for (var c = b.c - 6; c <= b.c + 6 && !out; c++) for (var r = b.r - 5; r <= b.r + 5 && !out; r++) { if (plotAt(c, r) || baseAt(c, r) || unitAt(c, r) || !inMap(c, r)) continue; var p = hexPos(c, r), q = w2s(p[0], p[1], p[2]); if (q && q[0] > 30 && q[0] < CW - 30 && q[1] > sa.top + 20 && q[1] < sa.bottom - 20) out = [c, r]; }
      return out; }''', info['id'])
    taphex(pg, dark[0], dark[1]); pg.wait_for_timeout(600)
    c1 = pg.evaluate('''({ modal: !!MODAL, see: $("modal").classList.contains("see"), app: $("app").className, sheet: getComputedStyle($("sheet")).visibility, sel: UI.sel ? UI.sel.kind + ":" + UI.sel.id : null, tab: (document.querySelector("#sheet .tabs button.on") || { getAttribute: function () {} }).getAttribute("data-v") })''')
    v4 = view(pg)
    ok(not c1['modal'] and not c1['see'] and 'seeing' not in c1['app'] and c1['sheet'] == 'visible' and c1['sel'] == 'base:%d' % info['id'] and c1['tab'] == 'fac', '어두운 곳을 누르면 창만 닫힌다(거점 창의 건설 탭으로) %s' % c1)
    ok(v4['on'] and v4['pi'] == -1 and all(l['gold'] == 12 and l['red'] == 0 for l in v4['lots']), '덮개는 그대로, 고른 칸은 풀린다(모두 금빛)')

    # --- 줄을 눌러 고르고 → 짓는다: 고른 바로 그 칸에
    T = v4['lots'][len(v4['lots']) - 2]
    tapsel(pg, '#sheet .lot[data-a=plot][data-v="%d"]' % T['i']); pg.wait_for_timeout(700)
    t1 = pg.evaluate('[MODAL && MODAL.dev ? MODAL.dev.pi : null, (document.querySelector("#modal h2") || {}).textContent]')
    ok(t1[0] == T['i'] and chr(0x245F + T['n']) in t1[1], '창의 %d번 단추를 누르면 지도의 %d번 칸이 골라진다 [%s]' % (T['n'], T['n'], t1[1]))
    gw = pg.evaluate('([id, pi]) => { var b = G.bases[id]; return [gainAt(b, pi, "farm").food, foodIncome(b), b.gold, G.factions[G.player].ap, b.plots[pi].fac]; }', [info['id'], T['i']])
    tapsel(pg, '#modal .row[data-a=f][data-v=farm]'); pg.wait_for_timeout(500)
    pk = pg.evaluate('''({ title: (document.querySelector("#modal h2") || {}).textContent, depth: MSTACK.length, see: $("modal").classList.contains("see"), app: $("app").className, sheet: getComputedStyle($("sheet")).visibility, view: (function () { var v = buildView(); return v ? v.pi : null; })() })''')
    ok('농장 건설 %s' % chr(0x245F + T['n']) in pk['title'] and pk['depth'] == 1 and not pk['see'] and 'seeing' in pk['app'] and pk['sheet'] == 'hidden' and pk['view'] == T['i'], '담당 무장 표: 제목에 칸 번호, 그 밑에 고른 칸이 그대로 [%s]' % pk['title'])
    B.shot(pg, 'd18_05_pick', 200)
    tapsel(pg, '#modal [data-a=close]'); pg.wait_for_timeout(400)
    bk = pg.evaluate('[MODAL && MODAL.dev ? MODAL.dev.pi : null, $("modal").classList.contains("see"), MSTACK.length]')
    ok(bk == [T['i'], True, 0], '표의 × → 무엇을 지을까요 창으로(고른 칸 그대로) %s' % bk)
    tapsel(pg, '#modal .row[data-a=f][data-v=farm]'); pg.wait_for_timeout(400)
    tapsel(pg, '#modal [data-a=auto]'); tapsel(pg, '#modal [data-a=ok]'); pg.wait_for_timeout(250)
    fl = pg.evaluate('Array.prototype.map.call(document.querySelectorAll("#fx .flt"), function (e) { return e.textContent; })')
    pg.wait_for_timeout(900)
    aft = pg.evaluate('''([id, pi]) => { var b = G.bases[id], f = b.plots[pi].fac; return { fac: f ? [f.t, f.done, f.lv] : null, others: b.plots.filter(function (p, i) { return i !== pi && p.fac && !p.fac.done; }).length, gold: b.gold, ap: G.factions[G.player].ap, modal: !!MODAL, toast: $("toast").textContent, by: f ? off(f.by[0]).n : "",
      talk: (function () { var t = $("talk"), r = t.getBoundingClientRect(), q = function (c) { var e = t.querySelector(c); return e ? e.textContent : ""; }; return { on: t.classList.contains("on"), who: q(".tk-who b"), say: q(".tk-say"), sub: q(".tk-sub"), top: Math.round(r.top), bottom: Math.round(r.bottom), por: !!t.querySelector(".por") }; })(),
      tab: (document.querySelector("#sheet .tabs button.on") || { getAttribute: function () {} }).getAttribute("data-v"), app: $("app").className, toastTop: Math.round($("toast").getBoundingClientRect().top), hud: $("hud").offsetHeight }; }''', [info['id'], T['i']])
    v5 = view(pg); rw5 = rows(pg)
    B.shot(pg, 'd18_06_built', 200)
    print('  착공:', aft, '| 떠오른 글:', fl)
    ok(aft['fac'] == ['farm', False, 1] and aft['others'] == 0, '고른 바로 그 칸(%d번)에 농장이 착공된다 — 다른 칸에는 아무것도 생기지 않는다' % T['n'])
    tk = aft['talk']
    ok(aft['gold'] == gw[2] - 140 and aft['ap'] == gw[3] - 20 and not aft['modal'] and aft['tab'] == 'fac', '금 −140 · 행동력 −20, 창이 닫히고 건설 탭으로')
    ok(tk['on'] and tk['por'] and tk['who'] == aft['by'] and len(tk['say']) >= 6 and tk['sub'].startswith('농장 착공') and '뒤 완공' in tk['sub'], 'v0.9.3: 맡은 무장(%s)이 대화창에서 답하고, 결과가 그 아래에 ["%s" / %s]' % (aft['by'], tk['say'], tk['sub']))
    ok(any('농장 착공' in t for t in fl), '착공한 칸에서 글자가 떠오른다 %s' % fl)
    ok(aft['hud'] <= tk['top'] <= aft['hud'] + 60 and tk['bottom'] - tk['top'] <= 110, '대화창은 위쪽 한 띠(위에서 %d~%dpx)' % (tk['top'], tk['bottom']))
    ok(v5['on'] and len(v5['lots']) == info['empty'] - 1 and all(l['i'] != T['i'] for l in v5['lots']) and [l['n'] for l in v5['lots']] == [n for n in nums if n != T['n']] and all(lotno[l['i']] == l['n'] for l in v5['lots']), 'v0.9.3: 착공한 칸(%d번)만 밝은 칸에서 빠지고, 남은 칸의 번호는 그대로 %s' % (T['n'], [l['n'] for l in v5['lots']]))
    ok([r[1] for r in rw5 if r[1]] == [str(n) for n in nums if n != T['n']], '창의 번호 단추도 그대로 %s' % [r[1] for r in rw5 if r[1]])
    ok(any(f['n'] == '농장' and not f['done'] and f['dark'][3] >= 150 for f in v5['facs']), "그 칸은 어두워지고 '농장 짓는 중'으로 적힌다")
    ok(any(r[0] == T['i'] and '건설 중' in r[3] for r in rw5), "목록에서도 '지은 시설' 아래 '건설 중'으로")
    done_gain = pg.evaluate('([id, pi]) => { var b = G.bases[id]; b.plots[pi].fac.done = true; var v = foodIncome(b); b.plots[pi].fac.done = false; return v; }', [info['id'], T['i']])
    ok(done_gain - gw[1] == gw[0] and gw[0] > 0, '카드에 적혔던 병량 +%d/분기 = 완공했을 때 실제로 늘어나는 수입(%d → %d)' % (gw[0], gw[1], done_gain))

    # --- 지금은 지을 수 없을 때: 무장 · 금 · 행동력 · 부대가 선 칸
    def blocked(js, why, tag):
        pg.evaluate(js, info['id']); pg.wait_for_timeout(500)
        w = view(pg); rr = rows(pg); note = pg.evaluate('(document.querySelector("#sheet .lotw") || {}).textContent || ""')
        L0 = w['lots'][0]
        taphex(pg, L0['c'], L0['r']); pg.wait_for_timeout(400)
        tt = pg.evaluate('[!!MODAL, $("toast").textContent]')
        ok(w['on'] and w['why'] == why and all(not l['ok'] and l['inside'][3] >= 150 for l in w['lots']), '%s: 칸이 밝아지지 않는다(점선만) — "%s"' % (tag, w['why']))
        ok(note == '지금은 지을 수 없습니다 — ' + why and all(' no' in r[2] for r in rr if r[1]), '%s: 창에 까닭 한 줄, 번호 단추는 점선으로 [%s]' % (tag, note))
        ok(not tt[0] and tt[1] == '지금은 지을 수 없습니다 — ' + why, '%s: 칸을 눌러도 창은 열리지 않고 까닭을 알린다 [%s]' % (tag, tt[1]))
        return w
    w1 = blocked('(id) => { var b = G.bases[id]; window._act = baseOfficers(b).map(function (o) { return [o.id, o.acted]; }); baseOfficers(b).forEach(function (o) { o.acted = true; }); refreshSheet(); requestDraw(); }', '쉬는 무장이 없습니다', '쉬는 무장 없음')
    B.shot(pg, 'd18_07_blocked', 200)
    pg.evaluate('(id) => { window._act.forEach(function (a) { off(a[0]).acted = a[1]; }); }', info['id'])
    blocked('(id) => { var b = G.bases[id]; window._gold = b.gold; b.gold = 100; refreshSheet(); }', '금이 모자랍니다 (140 필요)', '금 부족')
    blocked('(id) => { var b = G.bases[id]; b.gold = window._gold; window._ap = G.factions[G.player].ap; G.factions[G.player].ap = 5; refreshSheet(); }', '행동력이 모자랍니다', '행동력 부족')
    pg.evaluate('() => { G.factions[G.player].ap = window._ap; refreshSheet(); }'); pg.wait_for_timeout(400)
    ub = pg.evaluate('''(id) => { var b = G.bases[id], o = idleOfficers(b)[0]; b.troops = Math.max(b.troops, 8000); b.w.spear = Math.max(b.w.spear, 6000);
      var u = cmdDeploy(b, { type: "spear", ids: [o.id], troops: 3000, food: 2000 }).unit, pi = -1; b.plots.forEach(function (p, i) { if (pi < 0 && !p.fac && !unitAt(p.c, p.r)) pi = i; });
      placeUnit(u, b.plots[pi].c, b.plots[pi].r); syncScene(); requestDraw(); refreshSheet(); return { u: u.id, pi: pi }; }''', info['id'])
    pg.wait_for_timeout(500)
    w4 = view(pg); r4 = rows(pg)
    U = [l for l in w4['lots'] if l['i'] == ub['pi']][0]
    ok(w4['why'] == '' and not U['ok'] and U['inside'][3] >= 150 and all(l['ok'] and l['inside'][3] <= 12 for l in w4['lots'] if l['i'] != ub['pi']), '부대가 선 빈 부지 한 칸만 밝아지지 않는다(나머지는 밝다)')
    ok(any(r[0] == ub['pi'] and ' no' in r[2] for r in r4) and sum(1 for r in r4 if r[1] and ' no' in r[2]) == 1, '그 칸의 번호 단추만 점선')
    tapsel(pg, '#sheet .lot[data-a=plot][data-v="%d"]' % ub['pi']); pg.wait_for_timeout(400)
    tu = pg.evaluate('[!!MODAL, $("toast").textContent]')
    ok(not tu[0] and tu[1] == '부대가 서 있는 칸에는 지을 수 없습니다', '그 단추를 누르면 까닭을 알린다 [%s]' % tu[1])
    taphex(pg, U['c'], U['r']); pg.wait_for_timeout(400)
    ok(not pg.evaluate('!!(MODAL && MODAL.dev)'), '지도에서 부대가 선 칸을 누르면 건설 창이 아니라 그 부대가 골라진다(%s)' % pg.evaluate('UI.sel ? UI.sel.kind : null'))
    pg.evaluate('([id, uid]) => { var u = UMAP[uid]; if (u) removeUnit(u); if (MODAL) closeDialog(); selectBase(G.bases[id], true, "fac"); syncScene(); requestDraw(); }', [info['id'], ub['u']]); pg.wait_for_timeout(500)

    # --- 탭을 떠나면 걷힌다
    tapsel(pg, '#sheet .tabs button[data-v=home]'); pg.wait_for_timeout(600)
    off = view(pg); lab = pg.evaluate('(id) => R3.bases[id].lab.sp.visible', info['id'])
    ok(not off['on'] and 'on' not in off['cls'] and off['a'] < 0.01 and 'building' not in off['app'] and off['mini'] != 'none' and lab is True, '내정 탭으로 가면 덮개가 걷힌다(작은 지도·이름표 돌아옴)')
    B.shot(pg, 'd18_08_off', 200)
    # --- 거점 창 없이 지도에서 빈 부지를 눌러도 같은 창, 닫으면 걷힌다
    pg.evaluate('clearSel()'); pg.wait_for_timeout(400)
    lot = pg.evaluate('(id) => { var b = G.bases[id], p = b.plots.filter(function (x) { return !x.fac && !unitAt(x.c, x.r); })[0]; return [p.c, p.r, b.plots.indexOf(p)]; }', info['id'])
    pg.evaluate('([c, r]) => jumpTo(c, r, 1.0)', lot[:2]); pg.wait_for_timeout(600)
    taphex(pg, lot[0], lot[1]); pg.wait_for_timeout(900)
    m1 = pg.evaluate('[MODAL && MODAL.dev ? MODAL.dev.pi : null, $("modal").classList.contains("see"), !!(SHEET && SHEET.home)]'); vm = view(pg)
    ok(m1 == [lot[2], True, True] and vm['on'] and vm['pi'] == lot[2], 'STATUS 창을 둔 채 지도에서 내 빈 부지를 눌러도 같은 창과 덮개 %s' % m1)
    Sm = [l for l in vm['lots'] if l['i'] == lot[2]][0]
    ok(Sm['y'] + Sm['ppu'] <= pg.evaluate('document.querySelector("#modal .dlg").getBoundingClientRect().top') and Sm['top'] >= vm['sa'][0], '그때도 고른 칸이 창 위로 보인다')
    tapsel(pg, '#modal [data-a=close]'); pg.wait_for_timeout(600)
    vo = view(pg)
    ok(not vo['on'] and 'on' not in vo['cls'] and pg.evaluate('!!(SHEET && SHEET.home) && !MODAL'), '창을 닫으면 덮개도 걷히고 STATUS 창 그대로')
    # --- 빈 부지가 없는 성 · 남의 성
    none = pg.evaluate('''(id) => { var b = G.bases[id]; window._plots = b.plots.map(function (p) { return p.fac; }); b.plots.forEach(function (p) { if (!p.fac) p.fac = { t: "farm", lv: 1, done: true, prog: 0, need: 0, rate: 0, hp: FAC_HP }; });
      syncScene(); selectBase(b, true, "fac"); return true; }''', info['id'])
    pg.wait_for_timeout(600)
    vn = view(pg); sn = pg.evaluate('Array.prototype.map.call(document.querySelectorAll("#sheet .sh-body .sec"), function (e) { return e.textContent.replace(/\\s+/g, " ").trim(); })')
    ok(not vn['on'] and 'on' not in vn['cls'] and not any(s.startswith('빈 부지') for s in sn), '빈 부지가 없는 성: 덮개 없음, 창에는 [지은 시설]만 %s' % sn)
    pg.evaluate('(id) => { var b = G.bases[id]; b.plots.forEach(function (p, i) { p.fac = window._plots[i]; }); syncScene(); clearSel(); }', info['id'])
    foe = pg.evaluate('''() => { var b = G.bases.filter(function (x) { return x.kind === "city" && x.owner >= 0 && x.owner !== G.player; })[0]; selectBase(b); return { n: b.n, tabs: document.querySelectorAll("#sheet .tabs button").length, view: !!buildView() }; }''')
    pg.wait_for_timeout(400)
    ok(foe['tabs'] == 0 and not foe['view'] and 'on' not in pg.evaluate('$("spot").className'), '남의 성(%s)에서는 건설 자리가 없다' % foe['n'])
B.run(steps, 390, 844, 2)
errs = [e for e in B.errors if 'GPU stall' not in e and 'ERR_FILE_NOT_FOUND' not in e and 'willReadFrequently' not in e]   # 음악 파일은 따로 싣는다(오프라인 판에는 없다) · 덮개의 점을 읽는 것은 이 시험뿐이다
print('console errors:', errs[:6])
print('FAILS %d' % len(fails), fails)
sys.exit(1 if fails or errs else 0)
