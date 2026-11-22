# v0.18 행군 · 공격 명령 — [행군] 단추를 없앤다
#   그동안: 먼 곳으로 보내려면 부대 창의 [행군] → 지도에서 목적지 → [행군 시작], 세 번을 눌러야 했다. 먼 적을 누르면 "닿지 않습니다"뿐이었다.
#   이제:
#     · 부대를 고른 채 파란 칸 밖의 땅을 누르면 곧바로 그곳으로 행군을 시작한다(이번 턴 몫만큼 바로 간다). 잘못 눌렀으면 [이동 취소] — 제자리로 돌아오고 행군 명령도 거둔다.
#     · 닿지 않는 적(부대 · 거점)을 누르면 '공격 명령': 그쪽으로 다가가고, 턴을 마칠 때마다 알아서 다가가 닿으면 친다(u.aim — 규칙).
#       치는 수는 '주는 피해 − 받는 반격'의 기대값이 가장 큰 것(bestStrike) — 화면의 군사 추천(薦)과 같은 셈이다. 계략 · 일기토는 걸지 않는다.
#       닿는 적을 누르면 전처럼 내가 수를 고른다.
#     · 내 성 · 빈 성을 누르면 전처럼 그 성의 창이 열리고, 맨 위에 [○○대 — 이 성으로 행군] 단추가 생긴다.
#   CH_ROOT=<폴더> 로 다른 나무에 입힐 수 있다(시험용).
import io, os
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)
def cut(s, a, b):                       # a 로 시작해 b 바로 앞까지를 돌려준다(a 는 한 번만 나와야 하고, b 는 a 뒤의 첫 번째 것)
    assert s.count(a) == 1, ('cut', s.count(a), a[:50])
    i = s.index(a); j = s.index(b, i + len(a))
    return s[i:j]

# ───────────────────────── core.js: 공격 명령(규칙) ─────────────────────────
s = rd('src/core.js')
s = rep(s, "  return facUnits(f).filter(function (u) { return UMAP[u.id] && !u.done && u.dest >= 0; })", "  return facUnits(f).filter(function (u) { return UMAP[u.id] && !u.done && u.dest >= 0 && !u.aim; })      /* v0.18: 공격 명령을 받은 부대는 제 차례(aimStep)에 움직인다 */")
s = rep(s, "  if (cps.length) stage = -1;\n  return function () {\n    if (G.over) { JOT = null; return null; }\n",
"""  if (cps.length) stage = -1;
  var aims = G.aiOnly ? [] : G.units.filter(function (u) { return u.f === G.player && u.aim && !u.corps; }).map(function (u) { return u.id; }), ai0 = 0;      // v0.18: 공격 명령을 받은 내 부대 — 행군 다음, 군단보다 먼저
  return function () {
    if (G.over) { JOT = null; return null; }
    while (ai0 < aims.length) { var au = UMAP[aims[ai0++]]; if (au && au.aim && !au.corps) { aimStep(au); if (G.over) { JOT = null; return null; } return { kind: 'aim', f: G.player, id: au.id }; } }
""")
s = rep(s, "/* 출진 전에 목적지까지 걸릴 턴 수를 재 본다:",
"""/* ---------- v0.18 공격 명령: 적(부대 · 거점)을 찍어 두면 닿을 때까지 턴마다 다가가고, 닿으면 알아서 친다 ----------
   u.aim = { k: 'base' | 'unit', id, n(부대일 때 그 이름) }. 내 차례가 끝날 때(행군하는 부대가 움직인 뒤, 군단보다 먼저) 한 부대씩 aimStep.
   치는 수는 '주는 피해 − 받는 반격'의 기대값이 가장 큰 것(bestStrike). 계략 · 일기토는 걸지 않는다. 출진한 턴에는 거점을 치지 못한다(규칙 그대로).
   대상이 사라지거나(궤멸 · 입성) 내 것이 되거나 협정을 맺으면 명령은 끝난다. 내가 직접 움직이거나 쳐도 명령은 남는다(거두는 것은 aimClear) */
function bestStrike(u, d) {                                // { tac(전법 또는 null = 보통 공격), v(그 수의 기대값) } — 전법은 보통 공격보다 5% 넘게 나을 때만
  var N = attackExpect(u, d), best = null, bv = (N.dealt - N.recv) * 1.05, tl = tacticList(u);
  for (var i = 0; i < tl.length; i++) {
    var tac = tl[i];
    if (u.morale < tac.cost || !tacticTargets(u, tac).some(function (x) { return x.u === d; })) continue;
    var X = tacticExpect(u, d, tac), v = X.dealt - X.recv;
    if (v > bv) { bv = v; best = tac; }
  }
  return { tac: best, v: best ? bv : N.dealt - N.recv };
}
function aimTarget(u) {
  var a = u.aim; if (!a) return null;
  if (a.k === 'base') { var b = G.bases[a.id]; return (b && b.owner >= 0 && b.owner !== u.f && !pactOn(u.f, b.owner)) ? { kind: 'base', b: b, c: b.c, r: b.r } : null; }
  var d = UMAP[a.id]; return (d && d.f !== u.f && !pactOn(u.f, d.f)) ? { kind: 'unit', u: d, c: d.c, r: d.r } : null;
}
function aimName(u) { var a = u.aim; if (!a) return ''; if (a.k === 'base') return G.bases[a.id] ? G.bases[a.id].n : ''; var d = UMAP[a.id]; return d ? uName(d) : (a.n || ''); }
function aimSet(u, t) {                                    // t = { kind: 'base', b } | { kind: 'unit', u }
  var of = t.kind === 'base' ? t.b.owner : (t.kind === 'unit' ? t.u.f : -1);
  if (of < 0 || of === u.f) return ERR('적이 아닙니다');
  var pk = pactOf(u.f, of); if (pk) return ERR(facName(of) + '군과 ' + PACT_NAME[pk.t] + ' 중 — 칠 수 없습니다');
  u.aim = t.kind === 'base' ? { k: 'base', id: t.b.id } : { k: 'unit', id: t.u.id, n: uName(t.u) };
  aimDest(u);
  return { ok: true };
}
function aimClear(u) { if (u.aim) { delete u.aim; u.dest = -1; } }
function aimInRange(u, t) { var d = hdist(u.c, u.r, t.c, t.r); return d >= 1 && d <= uRange(u); }
/* 다가갈 곳(u.dest): 거점이면 그 칸(행군이 성 앞에서 멈춘다), 부대면 그 둘레의 빈 칸 가운데 나와 가까운 곳. 없으면 -1 */
function aimDest(u) {
  var t = aimTarget(u); if (!t) return -1;
  if (t.kind === 'base') { u.dest = K(t.c, t.r); return u.dest; }
  var ns = nbrs(t.c, t.r), best = -1, bd = 1e9, ci = clsIdx(u);
  for (var i = 0; i < ns.length; i++) {
    var c = ns[i][0], r = ns[i][1]; if (!inMap(c, r)) continue;
    var k = K(c, r); if (MC[ci][k] >= 99 || BAT[k] !== undefined || (UAT[k] && UAT[k] !== u)) continue;
    var dd = hdist(u.c, u.r, c, r); if (dd < bd) { bd = dd; best = k; }
  }
  u.dest = best; return best;
}
/* 이번 턴에 닿을 수 있으면 칠 자리로 간다(멀리서 쏘는 부대는 사거리 끝에, 숲 · 구릉을 좋아하고 물은 피한다). 못 닿으면 대상 쪽으로 한 구간 행군한다.
   돌려주는 값은 unitMove 의 결과(움직이지 않았으면 null) */
function aimApproach(u) {
  var t = aimTarget(u); if (!t || u.done || u.status || aimInRange(u, t)) return null;
  var rc = unitReach(u), rg = uRange(u), best = -1, bv = -1e9, k;
  for (k in rc.stop) {
    k = +k; if (BAT[k] !== undefined || G.fires[k]) continue;
    var c = k % W, r = (k - c) / W, d = hdist(c, r, t.c, t.r);
    if (d < 1 || d > rg) continue;
    var tt = terr(c, r), v = (d === rg ? 30 : 0) + (tt === 'f' || tt === 'h' ? 12 : 0) - (tt === 'w' ? 60 : 0) - hdist(u.c, u.r, c, r) * 2;
    if (v > bv) { bv = v; best = k; }
  }
  if (best >= 0) { var bc = best % W, res = unitMove(u, bc, (best - bc) / W, rc); if (res.ok && UMAP[u.id]) u.dest = -1; return res.ok ? res : null; }
  if (aimDest(u) < 0) return null;
  var m = unitMarch(u);                                    // 한 구간. 적 거점 앞에 닿으면 dest 가 풀린다(명령은 남는다)
  return m && m.ok ? m : null;
}
/* 한 부대의 공격 명령을 한 번 수행한다: 다가가고, 닿으면 친다. { moved(unitMove 의 결과), res(친 결과), end('gone' = 대상이 없어짐 · 'done' = 해냄) } */
function aimStep(u) {
  if (!alive(u) || !u.aim) return null;
  var out = {}, me = uName(u), nm = aimName(u), t = aimTarget(u);
  if (!t) { aimClear(u); out.end = 'gone'; logMsg(me + ' — ' + (nm ? josa(nm, '을를') : '대상을') + ' 칠 수 없게 되어 공격 명령을 거둠', u.c, u.r, u.f, 1); return out; }
  if (u.done || u.status) return out;
  if (!aimInRange(u, t)) { var mv = aimApproach(u); if (mv) out.moved = mv; if (!alive(u)) return out; t = aimTarget(u); if (!t) { aimClear(u); out.end = 'gone'; return out; } }
  if (!aimInRange(u, t) || u.done) return out;
  if (t.kind === 'base') { if (justOut(u)) return out; out.res = unitAttack(u, { kind: 'base', b: t.b, c: t.c, r: t.r }); }
  else { var bs = bestStrike(u, t.u), tg = { kind: 'unit', u: t.u, c: t.c, r: t.r }; out.res = bs.tac ? unitTactic(u, bs.tac, tg) : unitAttack(u, tg); }
  if (alive(u) && u.aim && !aimTarget(u)) { aimClear(u); out.end = 'done'; logMsg(me + ' — ' + (nm ? josa(nm, '을를') : '대상을') + ' 쳐서 공격 명령을 마침', u.c, u.r, u.f, 1); }
  return out;
}

/* 출진 전에 목적지까지 걸릴 턴 수를 재 본다:""")
wr('src/core.js', s)

# ───────────────────────── ui3d.js: 행군 길 표시 ─────────────────────────
s = rd('src/ui3d.js')
s = rep(s, "  if (UI.march && UI.march.path) for (i = 0; i < UI.march.path.length; i++) ovPut(UI.march.path[i], [47, 79, 111], 96);",
           "  var mpv = UI.mpath && UI.mpath.path ? UI.mpath.path : null;      // v0.18: 고른 부대가 행군(또는 공격 명령) 중이면 갈 길을 보여 준다\n"
           "  if (mpv) for (i = 0; i < mpv.length; i++) ovPut(mpv[i], [47, 79, 111], 96);")
wr('src/ui3d.js', s)

# ───────────────────────── ui_panels.js ─────────────────────────
s = rd('src/ui_panels.js')
# 군사의 추천(薦)은 공격 명령이 고르는 수와 같은 셈으로
old = cut(s, "    var advR = facAdv(u.f);\n    if (advR && d <= rg) {\n", "    var chOk = challengeTargets(u)")
s = s.replace(old, """    var advR = facAdv(u.f);
    if (advR && d <= rg) {                                       // v0.18 군사의 추천 = 공격 명령이 고르는 수(bestStrike)
      var bs0 = bestStrike(u, t.u), recA = bs0.tac ? out.filter(function (a0) { return a0.tac === bs0.tac; })[0] : out[0];
      if (recA && bs0.v > 0) recA.rec = true;
    }
""")
# 고르기 상태를 지운다: 따라 열린 성(mfrom) · 갈 길(mpath)
s = rep(s, "function clearSel() { UI.sel = null; UI.rc = null; UI.atk = null; UI.target = null; UI.march = null; UI.pickMarch = false; UI.via = false; UI.sret = null;",
           "function clearSel() { UI.sel = null; UI.rc = null; UI.atk = null; UI.target = null; UI.march = null; UI.pickMarch = false; UI.via = false; UI.sret = null; UI.mfrom = -1; UI.mpath = null;")
s = rep(s, "  UI.sel = { kind: 'base', id: b.id }; UI.rc = null; UI.atk = null; UI.target = null; UI.march = null; UI.via = false; UI.sret = null;\n",
           "  UI.sel = { kind: 'base', id: b.id }; UI.rc = null; UI.atk = null; UI.target = null; UI.march = null; UI.via = false; UI.sret = null; UI.mfrom = -1; UI.mpath = null;\n")
s = rep(s, "  UI.sel = { kind: 'unit', id: u.id }; UI.target = null; UI.march = null; UI.pickMarch = false; UI.via = false; UI.sret = null;\n",
           "  UI.sel = { kind: 'unit', id: u.id }; UI.target = null; UI.march = null; UI.pickMarch = false; UI.via = false; UI.sret = null; UI.mfrom = -1; mpathOf(u);\n")
# 지도 누름
s = rep(s, "        if ((t.kind === 'base' || t.kind === 'fac') && justOut(su) && hdist(su.c, su.r, c, r) <= (t.kind === 'fac' ? 1 : uRange(su))) toast('출진한 턴에는 거점을 칠 수 없습니다', 2400);\n        else if (!(UI.pickMarch && t.kind === 'base' && proposeMarch(su, c, r))) toast('닿지 않습니다');\n        return;\n",
"""        if ((t.kind === 'base' || t.kind === 'fac') && justOut(su) && hdist(su.c, su.r, c, r) <= (t.kind === 'fac' ? 1 : uRange(su))) toast('출진한 턴에는 거점을 칠 수 없습니다', 2400);
        else if (t.kind === 'fac') { if (MC[clsIdx(su)][k] < 99 && !u) orderMarch(su, c, r); else toast('닿지 않습니다'); }      // 먼 시설: 그 칸으로 행군
        else orderAim(su, t);                                          // v0.18: 닿지 않는 적(부대 · 거점) → 공격 명령(다가가서 알아서 친다)
        return;
""")
s = rep(s, "    if (UI.pickMarch && !u && MC[clsIdx(su)][k] < 99) { proposeMarch(su, c, r); return; }   // [행군]을 누른 뒤: 목적지 고르기\n", "")
s = rep(s, "    if (!u && !b && !(pl && pl.base.owner === G.player) && MC[clsIdx(su)][k] < 99) { toast('닿지 않습니다 — 파란 칸까지만', 2000); return; }\n",
           "    if (!u && !b && !(pl && pl.base.owner === G.player) && MC[clsIdx(su)][k] < 99) { orderMarch(su, c, r); return; }      // v0.18: 파란 칸 밖의 땅 → 곧바로 그곳으로 행군([이동 취소]로 물린다)\n")
s = rep(s, "  if (b) { selectBase(b); return; }\n",
"""  if (b) {
    var mf = (su && (b.owner === G.player || b.owner < 0)) ? su.id : -1;      // v0.18: 부대를 고른 채 누른 내 성 · 빈 성 — 창을 열되, 그 부대를 이 성으로 보내는 단추를 낸다
    selectBase(b);
    if (mf >= 0) { UI.mfrom = mf; UI.sret = function () { var u2 = UMAP[mf]; if (u2 && u2.f === G.player && !u2.done) selectUnit(u2); else clearSel(); }; refreshSheet(); }
    return;
  }
""")
# 행군 제안(proposeMarch) → 곧바로 행군 · 공격 명령
old = cut(s, "/* ---------- 행군(여러 턴 걸리는 이동) ---------- */\nfunction proposeMarch(u, c, r) {", "function destName(k) {")
s = s.replace(old, """/* ---------- 행군(여러 턴 걸리는 이동) · 공격 명령(v0.18) ----------
   UI.mNew = 이번 턴에 내린 명령 { id, turn, from(그때 서 있던 칸), prev(그 전의 목적지), aim0(그 전의 공격 명령) } — [이동 취소]가 그 첫걸음을 물리면 명령도 되돌린다
   UI.mpath = 고른 부대의 갈 길 { id, path } (지도에 그린다)   UI.mfrom = 성의 창에 [이 성으로 행군] 단추를 낼 부대 */
function mpathOf(u) { UI.mpath = (u && u.f === G.player && UMAP[u.id] && u.dest >= 0) ? { id: u.id, path: marchPath(u, u.dest) } : null; if (UI.mpath && !UI.mpath.path) UI.mpath = null; }
function noteOrder(u) { UI.mNew = { id: u.id, turn: G.turn, from: K(u.c, u.r), prev: u.dest >= 0 ? u.dest : -1, aim0: u.aim ? { k: u.aim.k, id: u.aim.id, n: u.aim.n } : null }; }
function marchDone(x, res, say) {                            // 행군의 한 구간이 끝난 뒤(명령을 내린 직후)
  if (res && res.ok && res.entered !== undefined) { toast(G.bases[res.entered].n + ' 입성'); selectBase(G.bases[res.entered]); }
  else if (res && res.ok && res.captured !== undefined) { sfx('fall'); sfx('cheerlate'); fxFall(G.bases[res.captured], '점령'); toast(G.bases[res.captured].n + ' 점령!'); selectBase(G.bases[res.captured]); }
  else if (alive(x)) {
    if (res && res.front !== undefined && !x.aim) toast(G.bases[res.front].n + ' 앞 — 성을 눌러 공격', 3200);
    else if (res && res.lost) toast('그곳으로 가는 길이 없습니다');
    else toast(say || (x.dest >= 0 ? '행군 시작' : '도착'), 3000);
    UI.rc = unitReach(x); UI.atk = allTargets(x); mpathOf(x); refreshSheet();
  } else clearSel();
  afterAction();
}
/* 파란 칸 밖의 땅(또는 성)으로: 곧바로 행군을 시작한다 */
function orderMarch(u, c, r) {
  var k = K(c, r), path = marchPath(u, k);
  if (!path) { toast('그곳으로 가는 길이 없습니다'); return false; }
  var b = baseAt(c, r), nm = b ? b.n : TERRAIN_NAME[terr(c, r)], turns = marchTurns(u, path), food = unitFoodTurns(u);
  noteOrder(u);
  if (u.aim) delete u.aim;                                    // 새 행군은 공격 명령을 지운다
  u.dest = k; UI.target = null; UI.march = null; UI.pickMarch = false; sfx('drum');
  var say = nm + ' 방면 행군 — 약 ' + days(turns) + (turns > food ? ' · 군량이 모자랍니다(' + days(food) + '분)' : '') + ' · 잘못 눌렀으면 이동 취소';
  marchStep(u, true, function (res) { marchDone(u, res, say); });
  return true;
}
/* 닿지 않는 적(부대 · 거점)으로: 공격 명령 — 지금 다가가고, 턴을 마칠 때마다 알아서 다가가 닿으면 친다 */
function orderAim(u, t) {
  noteOrder(u);
  var r = aimSet(u, t);
  if (!r.ok) { UI.mNew = null; toast(r.msg, 2600); return false; }
  var nm = aimName(u), of = t.kind === 'base' ? t.b.owner : t.u.f;
  UI.target = null; UI.march = null; UI.pickMarch = false; sfx('drum');
  var say = nm + ' 공격 명령 — 다가가서 알아서 칩니다' + (t.kind === 'base' && peaceWouldBreak(of) ? ' · 치면 ' + facName(of) + '군과의 보호가 풀립니다' : '') + ' · 잘못 눌렀으면 이동 취소';
  if (R3 && R3.ready && !R3.units[u.id]) syncScene();
  var vis = unitVis(u), name = uName(u), res = aimApproach(u);
  if (!res) { marchDone(u, null, say); return true; }
  UI.hide = alive(u) ? u.id : -1; UI.rc = null; UI.atk = null;
  animMove(vis, res.from, res.path, function () { marchLog(u, name, res); marchDone(u, res, say); });
  return true;
}
""")
# 부대 창: [행군 시작] · [거점 보기] · [행군] 을 없애고, [이동 취소]가 방금 내린 명령도 거두게
old = cut(s, "      undo: function () { var x = UMAP[u.id]; if (x && unitUndoMove(x)) {", "      march: function () {")
s = s.replace(old, """      undo: function () {
        var x = UMAP[u.id]; if (!x) return;
        var mn = UI.mNew, mine0 = mn && mn.id === x.id && mn.turn === G.turn && x.ox >= 0 && K(x.ox, x.oy) === mn.from;      // 물리는 걸음이 방금 내린 행군 · 공격 명령의 첫걸음인가
        if (!unitUndoMove(x)) return;
        if (mine0) { if (x.aim) delete x.aim; x.dest = mn.prev; if (mn.aim0) x.aim = mn.aim0; UI.mNew = null; toast('제자리로 — 방금 내린 명령도 거두었습니다', 2400); }
        UI.rc = unitReach(x); UI.atk = allTargets(x); UI.target = null; mpathOf(x); refreshSheet(); requestDraw();
      },
""")
old = cut(s, "      march: function () {\n        var x = selUnit(), m = UI.march; if (!x || !m) return;", "      unmarch: function () {")
s = s.replace(old, "")
s = rep(s, "      unmarch: function () { UI.march = null; UI.pickMarch = false; var x = UMAP[u.id]; if (x) x.dest = -1; refreshSheet(); requestDraw(); },\n      pickmarch: function () { UI.pickMarch = !UI.pickMarch; UI.march = null; UI.target = null; refreshSheet(); requestDraw(); },\n",
           "      unmarch: function () { UI.march = null; UI.pickMarch = false; UI.mNew = null; UI.mpath = null; var x = UMAP[u.id]; if (x) { if (x.aim) aimClear(x); x.dest = -1; } refreshSheet(); requestDraw(); },      // 행군 취소 · 공격 명령 취소\n")
old = cut(s, "      viewbase: function () {\n", "      douse: function () {")
s = s.replace(old, "")
old = cut(s, "        if (UI.march) {\n          h += '<div class=\"tgt\">행군 — <b>'", "        } else if (UI.target) {")
s = s.replace(old + "        } else if (UI.target) {", "        if (UI.target) {")
s = rep(s, "            (x.dest >= 0 ? '<button class=\"act\" type=\"button\" data-a=\"unmarch\"><b>행군 취소</b></button>' : '<button class=\"act' + (UI.pickMarch ? ' pri' : '') + '\" type=\"button\" data-a=\"pickmarch\"><b>행군</b></button>') + '</div>' +\n",
           "            ((x.dest >= 0 || x.aim) ? '<button class=\"act\" type=\"button\" data-a=\"unmarch\"><b>' + (x.aim ? '명령 취소' : '행군 취소') + '</b></button>' : '') + '</div>' +\n")
s = rep(s, "            (x.dest >= 0 ? '<p class=\"note\"><b class=\"hi\">' + destName(x.dest) + ' 방면 행군 중</b>' + marchLeft(x) + '</p>' : (UI.pickMarch ? '<p class=\"note\"><b class=\"hi\">행군 목적지를 지도에서 누르세요</b></p>' : '<p class=\"note\">파란 칸 = 이동 · 적 = 공격 · 먼 곳은 <b>행군</b></p>'));",
           "            (x.aim ? '<p class=\"note aimn\"><b class=\"hi\">' + aimName(x) + ' 공격 명령</b> — 턴을 마칠 때마다 다가가고, 닿으면 알아서 칩니다</p>' : (x.dest >= 0 ? '<p class=\"note\"><b class=\"hi\">' + destName(x.dest) + ' 방면 행군 중</b>' + marchLeft(x) + '</p>' : '<p class=\"note\">파란 칸 = 이동 · 적 = 공격 · <b>먼 곳을 누르면 그곳으로 행군</b> · 먼 적을 누르면 가서 칩니다</p>'));")
# 성의 창: [이 성으로 행군]
s = rep(s, "    order: function () { showOrderInfo(B()); }\n  };",
"""    order: function () { showOrderInfo(B()); },
    marchhere: function () {                                   // v0.18: 방금 고르고 있던 부대를 이 성으로
      var b = B(), mu = UMAP[UI.mfrom]; if (!mu || mu.f !== G.player || mu.done) { UI.mfrom = -1; refreshSheet(); return; }
      selectUnit(mu, true); orderMarch(mu, b.c, b.r);
    }
  };""")
s = rep(s, "      h += '<div class=\"stats\">' +\n        '<div class=\"w\"><span>' + ico('gold') + '금</span><b>' + fmt(b.gold)",
"""      var mfu = UI.mfrom >= 0 ? UMAP[UI.mfrom] : null;
      if (mfu && mfu.f === G.player && !mfu.done && (b.owner === G.player || b.owner < 0)) {
        var mfp = marchPath(mfu, K(b.c, b.r));
        h += '<div class="acts mfrom"><button class="act' + (mfp ? ' pri' : ' off') + '" type="button" data-a="marchhere"><b>' + uName(mfu) + ' — 이 ' + (city ? '성' : '관문') + '으로 행군</b><small>' + (mfp ? '약 ' + days(marchTurns(mfu, mfp)) + (b.owner < 0 ? ' · 닿으면 차지합니다' : ' · 닿으면 입성') : '갈 길이 없습니다') + '</small></button></div>';
      }
      h += '<div class="stats">' +
        '<div class="w"><span>' + ico('gold') + '금</span><b>' + fmt(b.gold)""")
# 기록: 공격 명령 중에 성 앞에 닿은 것은 '명령을 내리세요'가 아니다
s = rep(s, "  else if (res.front !== undefined) { b = G.bases[res.front]; logMsg(name + ' ' + b.n + ' 앞에 도착 — 공격 명령을 내리세요', b.c, b.r, G.player, 2); }",
           "  else if (res.front !== undefined) { b = G.bases[res.front]; if (!(alive(u) && u.aim)) logMsg(name + ' ' + b.n + ' 앞에 도착 — 공격 명령을 내리세요', b.c, b.r, G.player, 2); }")
# 도움말
old = cut(s, "  '<h3>행군(선택)</h3><p>", "</p>' +")
s = s.replace(old, "  '<h3>행군과 공격 명령</h3><p>부대를 고른 채 <b>파란 칸 밖의 땅을 누르면 곧바로 그곳으로 행군</b>합니다 — 이번 턴에 갈 수 있는 만큼 바로 가고, 턴을 마칠 때마다 한 구간씩 알아서 갑니다. 잘못 눌렀으면 <b>이동 취소</b>(제자리로 돌아오고 명령도 거둡니다). <b>닿지 않는 적 부대나 적의 성을 누르면 공격 명령</b>입니다: 다가가서, 턴을 마칠 때 닿으면 알아서 칩니다(주는 피해에서 받는 반격을 뺀 기대값이 가장 큰 수 — 군사의 추천 薦과 같습니다. 계략 · 일기토는 걸지 않습니다). 닿는 적을 누르면 전처럼 수를 직접 고릅니다. 도중에 직접 움직이거나 쳐도 되고, 부대 창의 <b>명령 취소</b>로 거둡니다. 내 성이나 빈 성으로 보내려면 그 성을 누르고 맨 위의 <b>이 성으로 행군</b>을 누르세요.")
wr('src/ui_panels.js', s)

# ───────────────────────── style.css ─────────────────────────
s = rd('src/style.css')
s += """
/* ── v0.18 행군 · 공격 명령 ── */
.acts.mfrom { margin: 0 0 8px; }
.acts.mfrom .act { flex: 1 1 100%; }
.note.aimn b { color: var(--seal); }
"""
wr('src/style.css', s)
print('p8_march18: ok')
