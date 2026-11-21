# v0.15 — 화면에서 확인: 지형(못 가는 칸에는 칸 줄이 없다 · 부대 창의 지형 줄 · 대상 창의 지형 풀이 · 빈 땅의 알림 · 도움말)
#   python3 tests/d27.py          찍은 그림은 tests/shots29/
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import taphex, tapsel
B.SHOTS = os.path.join(B.ROOT, 'shots29')
os.makedirs(B.SHOTS, exist_ok=True)
fails = []
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)
def toast(pg): return pg.evaluate('$("toast").textContent')
def reload(pg):
    pg.reload(); pg.wait_for_function('window.R3 && R3.ready', timeout=60000); pg.wait_for_timeout(600)
def fresh(pg, fac, seed):
    pg.evaluate('([f, s]) => { localStorage.clear(); newGame(f, s); saveGame(); }', [fac, seed]); reload(pg)
    tapsel(pg, '#tCont'); pg.wait_for_timeout(1300)
    if pg.evaluate('!!MODAL'): pg.evaluate('closeDialog()')
    pg.evaluate('talkHide()'); pg.wait_for_timeout(200)
PAIR = '''(fn) => { fn = eval(fn); for (var r = 60; r < 150; r++) for (var c = 100; c < 200; c++) { if (MC[0][K(c, r)] >= 99 || UAT[K(c, r)] || BAT[K(c, r)] !== undefined || PAT[K(c, r)]) continue; var ns = nbrs(c, r); for (var j = 0; j < ns.length; j++) { var k = K(ns[j][0], ns[j][1]); if (MC[0][k] >= 99 || UAT[k] || BAT[k] !== undefined || PAT[k]) continue; if (fn(c, r, ns[j][0], ns[j][1])) return [[c, r], ns[j]]; } } return null; }'''
def steps(pg):
    fresh(pg, 0, 1)
    # ================= 1. 못 가는 칸에는 칸 줄이 없다 =================
    print('1. 칸 줄')
    g = pg.evaluate('''(() => { var d = R3.stTex.image.data, off = 0, bad = 0, on = 0; for (var i = 0; i < NHEX; i++) { var imp = MC[0][i] >= 99; if (d[i * 4] === 0) off++; else on++; if ((d[i * 4] === 0) !== imp) bad++; }
      var conv = 0, convOff = 0; for (i = 0; i < NHEX; i++) if (MAPDATA.t.charAt(i) === 'm' && MAPDATA.t0.charAt(i) !== 'm') { conv++; if (d[i * 4] === 0) convOff++; }
      return { off: off, on: on, bad: bad, conv: conv, convOff: convOff }; })()''')
    ok(g['bad'] == 0 and g['conv'] == 642 and g['convOff'] == 642, '칸 줄을 그리는 칸 = 갈 수 있는 칸 (%d칸), 못 가는 칸 %d에는 없다 · 새로 산이 된 %d칸도' % (g['on'], g['off'], g['conv']))
    M = pg.evaluate('''(() => { talkHide(); HOME.open = false; clearSel(); var best = null;
      for (var r = 60; r < 150; r += 2) for (var c = 100; c < 200; c += 2) { var m = 0, h = 0, p = 0, n = 0; for (var dr = -4; dr <= 4; dr++) for (var dc = -4; dc <= 4; dc++) { var t = terr(c + dc, r + dr); if (t === 'm') { m++; if (MAPDATA.t0.charAt(K(c + dc, r + dr)) !== 'm') n++; } else if (t === 'h') h++; else if (t === 'p') p++; } if (m >= 12 && n >= 4 && h >= 10 && p >= 10) { var sc = n * 3 - Math.abs(m - 24); if (!best || sc > best.sc) best = { c: c, r: r, sc: sc, m: m, n: n }; } }
      jumpTo(best.c, best.r, 1.5); requestDraw(); return best; })()''')
    print('     ', M); B.shot(pg, 'y1_mountain', 1500)
    # 산을 누르면
    mh = pg.evaluate('(() => { for (var r = %d - 4; r <= %d + 4; r++) for (var c = %d - 4; c <= %d + 4; c++) if (terr(c, r) === "m") { var ok = true; nbrs(c, r).forEach(function (q) { if (terr(q[0], q[1]) !== "m") ok = false; }); if (ok) return [c, r]; } return null; })()' % (M['r'], M['r'], M['c'], M['c']))
    taphex(pg, mh[0], mh[1]); pg.wait_for_timeout(300); t = toast(pg)
    ok(t.startswith('산') and '지나갈 수 없다' in t and '높이' not in t, '산을 누르면: ' + t)
    # ================= 2. 빈 땅 =================
    print('2. 빈 땅의 알림')
    ph = pg.evaluate(PAIR, '(function (a, b, c, d) { return terr(a, b) === "h" && terr(c, d) === "h"; })')
    pg.evaluate('([c, r]) => { jumpTo(c, r, 1.5); requestDraw(); }', ph[0]); pg.wait_for_timeout(700)
    taphex(pg, ph[0][0], ph[0][1]); pg.wait_for_timeout(300); t = toast(pg); lv = pg.evaluate('elevOf(%d, %d)' % (ph[0][0], ph[0][1]))
    ok(t.startswith('구릉') and ('높이 %d' % lv) in t and '받는 피해 -15%' in t, '구릉을 누르면 지형 · 높이 · 효과: ' + t)
    # ================= 3. 부대 창 · 대상 창 =================
    print('3. 부대 창 · 대상 창')
    S = pg.evaluate('''(() => { var b = facCities(G.player)[0], eb = G.bases[baseByName('복양')]; b.troops = 60000; b.w.spear = 30000; b.w.horse = 30000; b.w.bow = 30000; b.food = 200000; eb.troops = 60000; eb.w.spear = 30000; eb.food = 200000; G.factions[G.player].ap = 250; G.factions[eb.owner].ap = 250; if (G.peace) G.peace.until = 0;
      var os = idleOfficers(b).filter(function (o) { return !isLord(o); }), es = idleOfficers(eb);
      var sp = cmdDeploy(b, { type: 'spear', ids: [os[0].id], troops: 5000, food: 5000 }).unit, cv = cmdDeploy(b, { type: 'cav', ids: [os[1].id], troops: 5000, food: 5000 }).unit, bw = cmdDeploy(b, { type: 'bow', ids: [os[2].id], troops: 5000, food: 5000 }).unit;
      var d = cmdDeploy(eb, { type: 'spear', ids: [es[0].id], troops: 5000, food: 5000 }).unit;
      [sp, cv, bw, d].forEach(function (u) { u.born = -9; u.done = false; u.mp = uMaxMp(u); u.morale = 100; });
      window.T = { sp: sp.id, cv: cv.id, bw: bw.id, d: d.id }; EVQ.length = 0; HOME.open = false; clearSel(); return true; })()''')
    def put(uid, hexa, did, hexd):
        pg.evaluate('([a, pa, d, pd]) => { var u = UMAP[a], t = UMAP[d]; placeUnit(u, 0, 0); placeUnit(t, 1, 0); placeUnit(u, pa[0], pa[1]); placeUnit(t, pd[0], pd[1]); u.done = false; syncScene(); jumpTo(pa[0], pa[1], 1.5); clearSel(); selectUnit(u, true); UI.target = { kind: "unit", u: t, c: t.c, r: t.r }; refreshSheet(); requestDraw(); }', [uid, hexa, did, hexd]); pg.wait_for_timeout(400)
    def tnote(): return pg.evaluate('(() => { var e = document.querySelector("#sheet .tnote"); return e ? e.innerText.replace(/\\n+/g, " / ") : ""; })()')
    def atk(): return pg.evaluate('(() => { var e = document.querySelector("#sheet .acts .act"); return e ? e.innerText.replace(/\\n+/g, " | ") : ""; })()')
    T = pg.evaluate('T')
    # (가) 평지 · 같은 높이: 풀이가 없다
    flat = pg.evaluate(PAIR, '(function (a, b, c, d) { return terr(a, b) === "p" && terr(c, d) === "p" && ELV[K(a, b)] === ELV[K(c, d)] && !isRoad(a, b); })')
    put(T['sp'], flat[0], T['d'], flat[1]); e0 = pg.evaluate('attackExpect(UMAP[T.sp], UMAP[T.d]).dealt')
    ok(tnote() == '', '평지 · 같은 높이: 지형 풀이가 없다')
    pg.evaluate('(() => { UI.target = null; refreshSheet(); })()'); pg.wait_for_timeout(200)
    tl = pg.evaluate('(() => { var e = document.querySelector("#sheet .terrl"); return e ? [e.innerText.replace(/\\n+/g, " "), e.scrollWidth <= e.clientWidth + 1] : null; })()')
    ok(tl and '평지' in tl[0] and ('높이 %d' % pg.evaluate('elevOf(UMAP[T.sp].c, UMAP[T.sp].r)')) in tl[0] and tl[1], '부대 창에 선 칸의 지형과 높이 — %s' % tl)
    B.shot(pg, 'y3_unit', 200)
    # (나) 낮은 곳에서 구릉의 적을
    up = pg.evaluate(PAIR, '(function (a, b, c, d) { return terr(a, b) === "p" && terr(c, d) === "h" && ELV[K(c, d)] - ELV[K(a, b)] === 2; })')
    put(T['sp'], up[0], T['d'], up[1]); n = tnote(); e1 = pg.evaluate('attackExpect(UMAP[T.sp], UMAP[T.d]).dealt')
    ok('구릉의 적 −15%' in n and '낮은 곳에서 −12%' in n and '내 피해 −25%' in n and '반격' in n and '높은 곳에서 +12%' in n, '낮은 곳에서 구릉의 적을 칠 때 — ' + n)
    ok(abs(e1 / e0 - 0.85 * 0.88) < 0.03 and ('%s' % format(round(e1), ',')) in atk(), '[공격]의 예상 피해에 들어 있다: 평지의 %.0f → %.0f (×%.2f) — %s' % (e0, e1, e1 / e0, atk()))
    fit = pg.evaluate('(() => { var e = document.querySelector("#sheet .tnote"), r = e.getBoundingClientRect(); return [r.left >= 0, r.right <= innerWidth, e.scrollWidth <= e.clientWidth + 1]; })()'); ok(all(fit), '풀이가 화면 안에 들어온다 %s' % fit)
    B.shot(pg, 'y3_target_up', 200)
    pg.evaluate('(() => { UI.target = null; refreshSheet(); })()'); pg.wait_for_timeout(200)
    # (다) 기병: 평지에서 평지의 적 · 숲의 적
    put(T['cv'], flat[0], T['d'], flat[1]); n = tnote()
    ok('기병 · 평지 +10%' in n, '기병이 평지에서: ' + n)
    tl = pg.evaluate('document.querySelector("#sheet .terrl") ? "" : ""'); pg.evaluate('(() => { UI.target = null; refreshSheet(); })()'); pg.wait_for_timeout(200)
    tl = pg.evaluate('document.querySelector("#sheet .terrl").innerText.replace(/\\n+/g, " ")'); ok('기병' in tl and '+10%' in tl, '기병의 부대 창: ' + tl)
    tf = pg.evaluate(PAIR, '(function (a, b, c, d) { return terr(a, b) === "p" && terr(c, d) === "f" && ELV[K(c, d)] === ELV[K(a, b)]; })')
    put(T['cv'], tf[0], T['d'], tf[1]); n = tnote()
    ok('숲의 적 −15%' in n and '기병 · 험한 땅 −15%' in n and '내 피해 −28%' in n, '기병이 숲의 적을: ' + n)
    acts = pg.evaluate('Array.prototype.map.call(document.querySelectorAll("#sheet .acts .act"), function (e) { return e.innerText.replace(/\\n+/g, " | "); })')
    ok(any('숲에서는 불가' in a for a in acts), '숲의 적에게는 기병 전법을 쓸 수 없다(전과 같다) — %s' % [a for a in acts if '불가' in a][:1])
    B.shot(pg, 'y3_cav_forest', 200)
    # (라) 노병: 두 칸 밖의 숲 속 적
    far = pg.evaluate('''(() => { for (var r = 60; r < 150; r++) for (var c = 100; c < 200; c++) { if (terr(c, r) !== 'f' || MC[0][K(c, r)] >= 99 || UAT[K(c, r)] || BAT[K(c, r)] !== undefined || PAT[K(c, r)]) continue; for (var dc = -2; dc <= 2; dc++) for (var dr = -2; dr <= 2; dr++) { var c2 = c + dc, r2 = r + dr; if (hdist(c, r, c2, r2) !== 2 || terr(c2, r2) !== 'p' || ELV[K(c2, r2)] !== ELV[K(c, r)] || UAT[K(c2, r2)] || BAT[K(c2, r2)] !== undefined || PAT[K(c2, r2)]) continue; return [[c2, r2], [c, r]]; } } return null; })()''')
    put(T['bw'], far[0], T['d'], far[1]); n = tnote()
    ok('숲의 적 −15%' in n and '숲 속으로 쏨 −15%' in n and '반격' not in n, '노병이 두 칸 밖의 숲 속을 쏠 때(반격은 없다): ' + n)
    # ================= 4. 실제로 쳐 본다 =================
    print('4. 실제 피해')
    put(T['sp'], up[1], T['d'], up[0])
    r = pg.evaluate('''(() => { var a = UMAP[T.sp], d = UMAP[T.d]; a.troops = 5000; d.troops = 5000; a.done = false; var _r = rnd; rnd = function () { return 0.5; }; DUEL_K.rate = 0; var e = attackExpect(a, d).dealt, res = unitAttack(a, { kind: 'unit', u: d, c: d.c, r: d.r }); rnd = _r; return { ok: res.ok, dmg: res.dmg, e: e, mods: terrMods(a, d, false).map(function (m) { return m.k; }) }; })()''')
    ok(r['ok'] and abs(r['dmg'] - r['e']) <= max(3, r['e'] * 0.02) and r['mods'] == ['높은 곳에서'], '높은 곳(구릉)에서 평지의 적을 쳤다: 피해 %s · 예상 %.0f · 걸린 것 %s' % (r['dmg'], r['e'], r['mods']))
    # ================= 5. 도움말 =================
    print('5. 도움말')
    pg.evaluate('(() => { clearSel(); showHelp(); })()'); pg.wait_for_timeout(300); t = pg.evaluate('document.querySelector("#modal").textContent')
    need = ['지형', '칸 줄이 없습니다', '높낮이', '한 단 높을 때마다', '기병', '숲 속의 부대를 화살로']
    ok(all(n in t for n in need), '도움말: %s' % [n for n in need if n not in t])
    pg.evaluate('closeDialog()')
B.run(steps, 390, 844, 2)
errs = [e for e in B.errors if 'GPU stall' not in e and 'GL Driver' not in e and 'ERR_FILE_NOT_FOUND' not in e and 'willReadFrequently' not in e]
print('console errors:', errs[:6])
print('FAILS %d' % len(fails), fails)
sys.exit(1 if fails or errs else 0)
