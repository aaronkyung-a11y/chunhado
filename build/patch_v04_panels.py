#!/usr/bin/env python3
"""v0.4: ui_panels.js — 출진을 처음 방식으로, 공격·이동 연출, 성역 안내, 수묵 색. build/ui_panels.v03.js → src/ui_panels.js"""
import os, re
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
s = open(os.path.join(root, 'build', 'ui_panels.v03.js'), encoding='utf8').read()
def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:80], s.count(old))
    s = s.replace(old, new)
def cut(start, end, new):
    """start 로 시작해 end 직전까지를 new 로 바꾼다"""
    global s
    a = s.index(start); b = s.index(end, a)
    assert s.count(start) == 1, start[:60]
    s = s[:a] + new + s[b:]

# ---- 아이콘·칩 색을 먹빛으로 ----
for a, b in [('#e3b341', '#c9a23f'), ('#7a5a12', '#1b1a18'), ('#d8c08a', '#e6dcc0'), ('#6b5326', '#1b1a18'), ('#cfd6dc', '#e2ddd0'), ('#9aa7b1', '#b9b3a4'), ('#39424a', '#1b1a18'),
             ('#ef7d36', '#b5332a'), ('#8b3410', '#1b1a18'), ('#6fa58d', '#8fa698'), ('#234b3c', '#1b1a18'), ('#b9ae98', '#d3ccba'), ('#4b4334', '#1b1a18'), ('#b08a4e', '#4a4037'),
             ('#d7dde2', '#e2ddd0'), ('#c2925a', '#b9a37c'), ('#5a3d18', '#1b1a18'), ('#a07a44', '#a8946c'), ('#3f2c12', '#1b1a18'), ('#6b4a22', '#3a332a'), ('#7d766a', '#8d877b')]:
    s = s.replace(a, b)
rep("color:#f0e7d0;font:16px sans-serif", "color:#1b1a18;font:16px sans-serif")
rep("color:#f0e7d0;font:16px/1.6 sans-serif", "color:#1b1a18;font:16px/1.6 sans-serif")
rep("font-size:22px;color:var(--gold)", "font-size:22px;color:var(--seal)")

# ---- 지도 누르기: 처음 방식(파란 칸 이동 · 적 눌러 공격). 먼 곳 행군은 [행군] 단추를 눌렀을 때만 ----
rep("function clearSel() { UI.sel = null; UI.rc = null; UI.atk = null; UI.target = null; UI.march = null; closeSheet(); requestDraw(); }",
    "function clearSel() { UI.sel = null; UI.rc = null; UI.atk = null; UI.target = null; UI.march = null; UI.pickMarch = false; closeSheet(); requestDraw(); }")
rep("  UI.sel = { kind: 'unit', id: u.id }; UI.target = null; UI.march = null;\n", "  UI.sel = { kind: 'unit', id: u.id }; UI.target = null; UI.march = null; UI.pickMarch = false;\n")
rep("      if (!any) { if (t.kind !== 'base' || !proposeMarch(su, c, r)) toast('닿지 않습니다 — 먼저 가까이 이동하세요'); return; }",
    "      if (!any) { if (!(UI.pickMarch && t.kind === 'base' && proposeMarch(su, c, r))) toast('닿지 않습니다 — 먼저 가까이 이동하세요'); return; }")
rep("    if (UI.rc && UI.rc.stop[k]) { UI.march = null; doMove(su, c, r); return; }\n    if (!u && MC[clsIdx(su)][k] < 99 && !(pl && pl.plot.fac)) { proposeMarch(su, c, r); return; }   // 닿지 않는 곳 → 행군 목적지",
    "    if (UI.pickMarch && !u && MC[clsIdx(su)][k] < 99 && !(pl && pl.plot.fac)) { proposeMarch(su, c, r); return; }   // [행군]을 누른 뒤: 목적지 고르기\n"
    "    if (UI.rc && UI.rc.stop[k]) { UI.march = null; doMove(su, c, r); return; }\n"
    "    if (!u && !b && !(pl && pl.base.owner === G.player) && MC[clsIdx(su)][k] < 99) { toast('닿지 않습니다 — 이번 턴에는 파란 칸까지만 갈 수 있습니다', 2200); return; }")
rep("  UI.march = { k: k, path: path, turns: marchTurns(u, path), name: b ? b.n : TERRAIN_NAME[terr(c, r)], base: b ? b.id : -1 };\n  UI.target = null; refreshSheet(); requestDraw();",
    "  UI.march = { k: k, path: path, turns: marchTurns(u, path), name: b ? b.n : TERRAIN_NAME[terr(c, r)], base: b ? b.id : -1 };\n  UI.target = null; UI.pickMarch = false; refreshSheet(); requestDraw();")

# ---- 이동: 성역 경계 안내, 점령 연출 ----
rep("""    if (res.entered !== undefined) { toast(G.bases[res.entered].n + ' 입성'); selectBase(G.bases[res.entered]); }
    else if (res.captured !== undefined) { sfx('fall'); toast(G.bases[res.captured].n + ' 점령!'); selectBase(G.bases[res.captured]); }
    else if (res.dead) { toast('불길 속에서 부대가 흩어졌습니다'); clearSel(); }
    else {
      if (res.burn) { floatText(c, r, '-' + fmt(res.burn), '#ff9a5a'); sfx('fire'); }
      UI.rc = unitReach(u); UI.atk = allTargets(u); refreshSheet();
    }
    afterAction();
  });
}""",
"""    if (res.entered !== undefined) { toast(G.bases[res.entered].n + ' 입성'); selectBase(G.bases[res.entered]); }
    else if (res.captured !== undefined) { sfx('fall'); fxFall(G.bases[res.captured], '점령'); toast(G.bases[res.captured].n + ' 점령!'); selectBase(G.bases[res.captured]); }
    else if (res.dead) { toast('불길 속에서 부대가 흩어졌습니다'); clearSel(); }
    else {
      if (res.burn) { floatText(c, r, '-' + fmt(res.burn), '#b5332a'); sfx('fire'); }
      UI.rc = unitReach(u); UI.atk = allTargets(u); refreshSheet();
      if (zoneAt(res.from[0], res.from[1]) !== zoneAt(c, r)) zoneToast(res.from, c, r);
    }
    afterAction();
  });
}
/* 성역의 경계를 넘었을 때의 안내 */
function zoneToast(from, c, r) {
  var z1 = zoneAt(c, r), z0 = zoneAt(from[0], from[1]);
  toast(z1 >= 0 ? G.bases[z1].n + '의 성역에 들어섰습니다 — 이번 턴 이동은 여기까지입니다' : G.bases[z0].n + '의 성역을 벗어났습니다 — 이번 턴 이동은 여기까지입니다', 2800);
}""")

# ---- 결과 표시: 말(resultMsg)과 화면 효과(resultFx)를 나눈다 ----
cut("function presentResult(name, res, quiet) {", "function doAct(a) {",
"""/* 행동 결과를 한 줄로 */
function resultMsg(name, res) {
  var msg = name + ' ';
  if (res.kind === 'ploy') {
    if (res.success) msg += res.ploy + ' 성공' + (res.dmg ? ' (-' + fmt(res.dmg) + ')' : '') + (res.chain ? ' · 연환!' : '');
    else msg += res.ploy + ' 실패 (성공률 ' + res.p + '%)' + (res.reflected ? ' — 반계에 당했습니다!' : '');
  } else {
    if (res.kind === 'tactic') msg += res.tac + (res.fail ? ' 실패' : (res.crit ? ' 크리티컬' : ' 성공')); else msg += '공격';
    msg += ' → ' + res.tname + ' -' + fmt(res.dmg);
    if (res.dur) msg += ' · 내구 -' + fmt(res.dur);
    if (res.dmg2) msg += ' · 연전 -' + fmt(res.dmg2);
    if (res.slam) msg += ' · 뒤가 막혀 추가 피해';
    if (res.confused) msg += ' · 혼란';
  }
  if (res.counter) msg += ' (반격 -' + fmt(res.counter) + ')';
  if (res.duel) msg += ' · 일기토! ' + res.duel.a + ' 대 ' + res.duel.d + ' — ' + (res.duel.win ? res.duel.a : res.duel.d) + ' 승';
  if (res.killed) msg += ' · 궤멸!';
  if (res.destroyed) msg += ' · 파괴!';
  if (res.selfDead) msg += ' · 아군 부대 궤멸…';
  if (res.fell) msg = res.tname + ' 함락!';
  return msg;
}
/* 타격 순간에 띄우는 숫자·글씨와 소리. 피해는 인주색, 전법 이름은 먹, 계략은 쪽빛 */
function resultFx(res) {
  var C_DMG = '#b5332a', C_INK = '#1b1a18', C_PLOY = '#2f4f6f', C_DIM = '#6a645a', C_CNT = '#8a5a12';
  var tc = res.tc1 !== undefined ? res.tc1 : (res.tc !== undefined ? res.tc : res.c), tr = res.tr1 !== undefined ? res.tr1 : (res.tr !== undefined ? res.tr : res.r);
  var ac = res.ac1 !== undefined ? res.ac1 : res.ac, ar = res.ar1 !== undefined ? res.ar1 : res.ar;
  if (res.kind === 'ploy') {
    if (res.success) {
      floatText(res.c, res.r, res.ploy + '!', res.ploy === '화계' ? '#c8551f' : C_PLOY, 0, true, -34);
      if (res.dmg) floatText(res.c, res.r, '-' + fmt(res.dmg), C_DMG, 260);
      sfx(res.ploy === '화계' || res.ploy === '소화' ? 'fire' : 'hit');
    } else {
      floatText(res.c, res.r, '실패', C_DIM); sfx('fail');
      if (res.reflected) floatText(res.ac, res.ar, '반계!', C_PLOY, 300, true);
    }
  } else {
    // 글씨가 한자리에 겹치지 않게: 전법 이름은 위, 피해는 가운데, 덧붙는 것은 아래로 차례차례
    if (res.kind === 'tactic') floatText(res.c, res.r, res.fail ? '전법 실패' : res.tac + (res.crit ? ' 크리티컬!' : '!'), res.fail ? C_DIM : C_INK, 0, true, -34);
    else if (res.crit) floatText(res.c, res.r, '크리티컬!', C_INK, 0, true, -34);
    floatText(tc, tr, '-' + fmt(res.dmg), C_DMG, res.kind === 'tactic' || res.crit ? 200 : 0, res.crit || (res.kind === 'tactic' && !res.fail));
    if (res.dur) floatText(tc, tr, '내구 -' + fmt(res.dur), C_CNT, 380, false, 26);
    if (res.dmg2) floatText(tc, tr, '연전 -' + fmt(res.dmg2), C_DMG, 620, false, 26);
    if (res.extra) res.extra.forEach(function (x, i) { floatText(x.c, x.r, '-' + fmt(x.dmg), C_DMG, 300 + i * 80); });
    if (res.confused) floatText(tc, tr, '혼란', C_PLOY, 700, false, 48);
    if (res.fire) sfx('fire');
    sfx(res.fail ? 'fail' : (res.kind === 'tactic' || res.crit ? 'big' : 'hit'));
  }
  if (res.counter) floatText(ac, ar, '-' + fmt(res.counter), C_CNT, 520);
  if (res.duel) { floatText(res.duel.win ? tc : ac, res.duel.win ? tr : ar, '일기토 패 -' + fmt(res.duel.loss), C_INK, 1150, true, -8); sfx('big'); }
  if (res.selfDmg) floatText(res.ac, res.ar, '-' + fmt(res.selfDmg), C_CNT, 500);
  if (res.fell) sfx('fall');
}
function presentResult(name, res, quiet) { var msg = resultMsg(name, res); resultFx(res); if (!quiet) toast(msg, 3200); return msg; }
""")

# ---- 내 부대의 공격: 붓질 연출이 끝난 뒤에 다음으로 ----
cut("function doAct(a) {", "/* 행군 중인 부대의 남은 길(어림) */",
"""function doAct(a) {
  var u = selUnit(), t = UI.target;
  if (!u || !t || UI.busy) return;
  var name = uName(u), res;
  if (a.kind === 'attack') res = unitAttack(u, t);
  else if (a.kind === 'tactic') res = unitTactic(u, a.tac, t);
  else res = unitPloy(u, a.ploy, t);
  if (!res.ok) { toast(res.msg); return; }
  UI.battleTurn = G.turn; playBgm('battle');
  var msg = resultMsg(name, res), fellB = res.fell && t.kind === 'base' ? t.b : null;
  UI.busy = true; UI.rc = null; UI.atk = null; UI.target = null;
  requestDraw();
  actZoom(res.ac0, res.ar0, t.c, t.r, function (back) {      // 싸우는 곳을 가까이 당겨서 보여 준다
    animAct(res, function () {
      UI.busy = false;
      if (fellB) fxFall(fellB, fellB.kind === 'gate' ? '점령' : '함락');
      toast(msg, 3200);
      clearSel();
      if (fellB && fellB.owner === G.player) selectBase(fellB);
      back();
      afterAction();
    }, function () { resultFx(res); });
  });
}
/* 두 칸 사이를 화면 가운데로 당긴다. 이미 충분히 가까우면 그대로. cb(back) — back() 을 부르면 원래 시점으로 돌아간다 */
function actZoom(c1, r1, c2, r2, cb) {
  var c0 = { x: cam.x, y: cam.y, z: cam.z }, near = cam.z >= 1.45 && onScreen(c1, r1, 30) && onScreen(c2, r2, 30);
  function back() { if (near) return; var x0 = cam.x, y0 = cam.y, z0 = cam.z; anim(360, function (t) { var e = t * (2 - t); cam.x = x0 + (c0.x - x0) * e; cam.y = y0 + (c0.y - y0) * e; cam.z = z0 + (c0.z - z0) * e; clampCam(); }); }
  if (near) { cb(back); return; }
  var a = hexCenter(c1, r1), b = hexCenter(c2, r2), z1 = Math.max(cam.z, 1.75), x0 = cam.x, y0 = cam.y, z0 = cam.z;
  var D = 62 / z1, pt = (68 - 27 * clamp(Math.log(z1 / Z_MIN) / Math.log(Z_MAX / Z_MIN), 0, 1)) * Math.PI / 180;
  var tx = (a[0] + b[0]) / 2, ty = (a[1] + b[1]) / 2 + (0.5 - safeArea().fy) * D * K3 / Math.sin(pt);
  anim(300, function (t) { var e = t * (2 - t); cam.x = x0 + (tx - x0) * e; cam.y = y0 + (ty - y0) * e; cam.z = z0 + (z1 - z0) * e; clampCam(); }, function () { cb(back); });
}
""")

# ---- 부대 창: [행군] 단추, 안내문 ----
rep("""            (x.dest >= 0 ? '<button class="act" type="button" data-a="unmarch"><b>행군 취소</b><small>' + destName(x.dest) + ' 방면</small></button>' : '') + '</div>' +
            (x.dest >= 0 ? '<p class="note"><b class="hi">' + destName(x.dest) + ' 방면 행군 중</b>' + marchLeft(x) + ' — 턴을 마치면 다음 구간을 갑니다. 그 전에 직접 움직이거나 공격해도 됩니다.</p>' : '<p class="note">파란 칸을 누르면 이동합니다. 먼 곳이나 거점을 누르면 여러 턴에 걸쳐 가는 <b>행군</b>을 정할 수 있습니다. 적을 누르면 공격·전법·계략을 고릅니다.</p>');""",
"""            (x.dest >= 0 ? '<button class="act" type="button" data-a="unmarch"><b>행군 취소</b><small>' + destName(x.dest) + ' 방면</small></button>' : '<button class="act' + (UI.pickMarch ? ' pri' : '') + '" type="button" data-a="pickmarch"><b>행군</b><small>' + (UI.pickMarch ? '목적지를 누르세요' : '먼 곳까지 알아서') + '</small></button>') + '</div>' +
            (x.dest >= 0 ? '<p class="note"><b class="hi">' + destName(x.dest) + ' 방면 행군 중</b>' + marchLeft(x) + ' — 턴을 마치면 다음 구간을 갑니다. 그 전에 직접 움직이거나 공격해도 됩니다.</p>' : (UI.pickMarch ? '<p class="note"><b class="hi">행군 목적지를 지도에서 누르세요.</b> 거점이나 길 위의 칸을 고르면 걸리는 날수를 보여 줍니다. 그만두려면 행군을 한 번 더 누르세요.</p>' : '<p class="note"><b>파란 칸</b>을 누르면 이동하고, <b>적</b>을 누르면 공격·전법·계략을 고릅니다. 옅은 파란 칸은 성역의 경계 — 넘으면 이번 턴 이동이 끝납니다.</p>'));""")
rep("      unmarch: function () { UI.march = null; var x = UMAP[u.id]; if (x) x.dest = -1; refreshSheet(); requestDraw(); },",
    "      unmarch: function () { UI.march = null; UI.pickMarch = false; var x = UMAP[u.id]; if (x) x.dest = -1; refreshSheet(); requestDraw(); },\n      pickmarch: function () { UI.pickMarch = !UI.pickMarch; UI.march = null; UI.target = null; refreshSheet(); requestDraw(); },")
rep("      douse: function () { var x = selUnit(); if (!x) return; var res = unitPloy(x, PLOYS[3], { c: x.c, r: x.r }); if (!res.ok) { toast(res.msg); return; } sfx('fire'); toast('주위의 불을 껐습니다'); clearSel(); afterAction(); },",
    "      douse: function () { var x = selUnit(); if (!x || UI.busy) return; var res = unitPloy(x, PLOYS[3], { c: x.c, r: x.r }); if (!res.ok) { toast(res.msg); return; } UI.busy = true; animAct(res, function () { UI.busy = false; toast('주위의 불을 껐습니다'); clearSel(); afterAction(); }, function () { sfx('fire'); }); requestDraw(); },")

# ---- 출진: 처음 방식 — 병과·무장·병력·군량만 정하고, 나온 부대를 직접 움직인다 ----
cut("/* ---------- v0.3: 출진 목적지" if "/* ---------- v0.3: 출진 목적지" in s else "function destCands(b) {", "function flowDeploy(b) {", "")
cut("function flowDeploy(b) {", "function flowTransport(b) {",
"""function flowDeploy(b) {
  var list = idleOfficers(b).sort(function (x, y) { return aiMilScore(y) - aiMilScore(x); });
  if (!list.length) return toast('행동할 수 있는 무장이 없습니다');
  if (b.troops < 100) return toast('주둔 병력이 없습니다');
  var st = { type: 'sword', ids: [], troops: 0, turns: 12, auto: true };
  function stock(t) { var wp = UNIT_TYPES[t].weapon; return wp === 'ram' ? b.w.ram : (wp ? b.w[wp] : 1e9); }
  function usable(t) { return t === 'ram' ? stock(t) >= 1 : stock(t) >= 100; }
  ['spear', 'halberd', 'bow', 'cav'].forEach(function (t) { if (usable(t) && (st.type === 'sword' || stock(t) > stock(st.type))) st.type = t; });
  function mx() {
    if (!st.ids.length) return 0;
    var m = Math.min(b.troops, cmdCap(off(st.ids[0]))), wp = UNIT_TYPES[st.type].weapon;
    if (wp && wp !== 'ram') m = Math.min(m, b.w[wp]);
    return Math.floor(m / 100) * 100;
  }
  function food() { return Math.min(b.food, Math.ceil(st.troops / 20) * st.turns); }
  function fix() { var m = mx(); if (st.auto || st.troops > m) st.troops = m; }
  function pv() {
    if (!st.ids.length) return '주장을 고르세요';
    var tmp = { type: st.type, off: st.ids, troops: st.troops, max: st.troops };
    return '공격 <b>' + Math.round(uAtk(tmp)) + '</b> · 방어 <b>' + Math.round(uDef(tmp)) + '</b> · 이동 <b>' + uMaxMp(tmp) + '</b> · 군량 <b>' + fmt(food()) + '</b>';
  }
  showDialog({
    render: function () {
      var h = dlgHead('출진 — ' + b.n) + '<div class="dlg-b"><div class="sec">병과</div><div class="opts">', i;
      var UKEY = { sword: 'u_sword', spear: 'u_spear', halberd: 'u_halberd', bow: 'u_bow', cav: 'u_cav', ram: 'u_ram' };
      for (i = 0; i < COMBAT_TYPES.length; i++) {
        var t = COMBAT_TYPES[i], T = UNIT_TYPES[t], ok = usable(t);
        h += '<button class="opt' + (st.type === t ? ' on' : '') + (ok ? '' : ' off') + '" type="button" data-a="type" data-v="' + t + '">' + thumb(UKEY[t]) + '<b>' + T.name + '</b><small>' + (t === 'sword' ? '무기 불필요' : (t === 'ram' ? '충차 ' + b.w.ram + '대' : WEAPON_NAMES[T.weapon] + ' ' + fmt(stock(t)))) + '</small></button>';
      }
      h += '</div><div class="sec">무장 — 첫 번째가 주장, 최대 3명<button class="btn auto" type="button" data-a="auto">자동 편성</button></div><div class="rows">';
      var ai = APT_IDX[st.type];
      for (i = 0; i < list.length; i++) {
        var o = list[i], si = st.ids.indexOf(o.id);
        h += offRow(o, { a: 'pick', sel: si >= 0, badge: si === 0 ? '주장' : (si > 0 ? '부장' : ''), rt: (ai !== undefined ? '적성 <b class="' + (o.apt.charAt(ai) === 'S' ? 'bad' : (o.apt.charAt(ai) === 'A' ? 'hi' : '')) + '">' + o.apt.charAt(ai) + '</b><br>' : '') + '지휘 ' + fmt(cmdCap(o)) });
      }
      h += '</div>';
      if (st.ids.length) {
        h += '<div class="fld"><label><span>병력 (주둔 ' + fmt(b.troops) + ')</span><b id="dpV">' + fmt(st.troops) + '</b></label><input type="range" id="dpR" min="0" max="' + mx() + '" step="100" value="' + st.troops + '" data-i="troops"></div><div class="sec">군량</div><div class="opts c4">';
        [6, 12, 18, 24].forEach(function (n) { h += '<button class="opt' + (st.turns === n ? ' on' : '') + '" type="button" data-a="turns" data-v="' + n + '"><b>' + days(n) + '분</b><small>' + fmt(Math.ceil(st.troops / 20) * n) + '</small></button>'; });
        h += '</div><p class="note">도시 병량 ' + fmt(b.food) + '. 이웃 성까지는 적어도 30일, 보통 40~60일이 걸립니다. 군량이 떨어지면 병사가 흩어집니다.</p>';
      }
      return h + '</div><div class="dlg-f"><div class="pv" id="dpP">' + pv() + '</div><button class="btn pri" type="button" data-a="ok"' + (st.ids.length && st.troops >= 100 ? '' : ' disabled') + '>출진</button></div>';
    },
    on: {
      type: function (el) { var t = el.getAttribute('data-v'); if (!usable(t)) return toast(t === 'ram' ? '충차가 없습니다 — 공방에서 생산하세요' : WEAPON_NAMES[UNIT_TYPES[t].weapon] + ' 재고가 없습니다'); st.type = t; st.auto = true; fix(); refreshDialog(); },
      pick: function (el) { var id = +el.getAttribute('data-v'), i = st.ids.indexOf(id); if (i >= 0) st.ids.splice(i, 1); else if (st.ids.length < 3) st.ids.push(id); else return toast('최대 3명입니다'); st.auto = true; fix(); refreshDialog(); },
      turns: function (el) { st.turns = +el.getAttribute('data-v'); refreshDialog(); },
      auto: function () { st.ids = autoTeam(b, st.type, Math.min(b.troops, 8000)); st.auto = true; fix(); toast(st.ids.length ? UNIT_TYPES[st.type].name + '에 가장 알맞은 ' + st.ids.length + '명을 골랐습니다' : '편성할 무장이 없습니다', 2200); refreshDialog(); },
      troops: function (el) { st.troops = +el.value; st.auto = false; $('dpV').textContent = fmt(st.troops); $('dpP').innerHTML = pv(); },
      ok: function () {
        var r = cmdDeploy(b, { type: st.type, ids: st.ids, troops: st.troops, food: food() });
        if (!r.ok) return toast(r.msg);
        closeDialog(); sfx('drum');
        var u = r.unit, name = uName(u);
        clearSel(); refreshHud(); syncScene();                       // 막 나온 부대를 지도에 세우고
        if (!onScreen(u.c, u.r, 20)) jumpTo(u.c, u.r, Math.max(cam.z, 0.8));
        UI.busy = true;
        fxDeploy(u, b, function () {                                // 성에서 걸어 나오는 모습을 보인 뒤 고른 상태로
          UI.busy = false;
          if (alive(u)) { selectUnit(u); toast(name + ' 출진 — 파란 칸을 눌러 이동하세요', 2600); }
          afterAction();
        });
      }
    }
  });
}
""")
rep("closeDialog(); toast('수송대 출발 — 아군 거점으로 들여보내면 물자가 합쳐집니다'); selectUnit(r.unit); afterAction();",
    "closeDialog(); toast('수송대 출발 — 파란 칸을 눌러 이동하세요. 아군 거점으로 들여보내면 물자가 합쳐집니다', 3200); syncScene(); selectUnit(r.unit); afterAction();")

# ---- 지난 열흘 재생: 사건이 생긴 그 자리에서 관련 부대를 붙잡아 두고, 공격은 붓질 연출로 ----
rep("""    if (s) {
      for (i = 0; i < evs.length; i++) { evs[i].cls = evClass(evs[i]); if (evs[i].cls === 2) big = true; }""",
"""    if (s) {
      for (i = 0; i < evs.length; i++) { evs[i].cls = evClass(evs[i]); if (evs[i].cls === 2) big = true; }
      for (i = 0; i < evs.length; i++) holdEv(evs[i]);          // 보여 줄 때까지 그림을 지금 모습 그대로 둔다""")
rep("function pump() {",
"""/* 사건에 얽힌 부대 그림을 붙잡아 둔다(규칙 쪽 상태는 이미 앞서가 있으므로) */
function holdEv(e) {
  if (!R3 || !e.cls) return;
  var o;
  if (e.t === 'move') { o = R3.units[e.id]; if (o) o.anim = true; }
  else if (e.t === 'act' && e.res) { o = R3.units[e.res.aid]; if (o) o.anim = true; if (e.res.tid >= 0) { o = R3.units[e.res.tid]; if (o) o.anim = true; } }
}
function pump() {""")
rep("""  for (i = 0; i < evs.length; i++) if (evs[i].t === 'move') { var o = R3.units[evs[i].id]; if (o) o.anim = true; }
  syncScene();                                             // 새로 나온 부대를 만들고, 움직일 부대는 출발점에 둔 채로""",
"""  for (i = 0; i < evs.length; i++) holdEv(evs[i]);
  syncScene();                                             // 새로 나온 부대를 만들고, 움직일 부대는 출발점에 둔 채로
  for (i = 0; i < evs.length; i++) if (evs[i].t === 'deploy') {   // 막 출진한 부대는 성 앞 칸에 세워 둔다(뒤따르는 이동은 거기서 시작)
    var od = R3.units[evs[i].id];
    if (od && !od.held) { od.anim = true; od.held = true; fxPut(od, hexPos(evs[i].c, evs[i].r)); }
  }""")
rep("""    focus(e.tc, e.tr, pg(function () {
      var msg = presentResult(e.name, e.res, true);
      setCaption(e.f, msg, e.tf === G.player ? 'hit' : '');
      requestDraw(); pwait((e.res.fell ? 500 : 1500) * k, cb);        // 함락이면 바로 뒤에 함락 장면이 따로 나온다
    }));""",
"""    focus(e.tc, e.tr, pg(function () {
      setCaption(e.f, resultMsg(e.name, e.res), e.tf === G.player ? 'hit' : '');
      var n0 = UI.anims.length;
      animAct(e.res, pg(function () { P.ans = []; requestDraw(); pwait((e.res.fell ? 200 : 700) * k, cb); }), function () { resultFx(e.res); });   // 함락이면 바로 뒤에 함락 장면이 따로 나온다
      P.ans = UI.anims.slice(n0);
    }));""")
rep("""      sfx('fall'); flashHex(b.c, b.r, '#ffe9a6'); floatText(b.c, b.r, b.kind === 'gate' ? '점령' : '함락', '#ffd76a', 0, true);""",
    """      sfx('fall'); fxFall(b, e.old < 0 || b.kind === 'gate' ? '점령' : '함락');""")
rep("""      setCaption(e.f, G.bases[e.base].n + '에서 <b>' + e.n + '</b> 출진');
      flashHex(e.c, e.r, G.factions[e.f].color); sfx('step');
      pwait(520, cb);""",
"""      setCaption(e.f, G.bases[e.base].n + '에서 <b>' + e.n + '</b> 출진');
      sfx('drum');
      var odp = R3.units[e.id], bb = G.bases[e.base];
      if (odp && bb) {                                           // 성에서 걸어 나온다(뒤따르는 이동 장면을 위해 붙잡아 둔 채로)
        var q0 = hexPos(bb.c, bb.r), q1 = hexPos(e.c, e.r);
        anim(420, function (t) { var w = 1 - (1 - t) * (1 - t), px = q0[0] + (q1[0] - q0[0]) * w, pz = q0[2] + (q1[2] - q0[2]) * w; fxPut(odp, [px, groundY(px, pz) + Math.sin(Math.PI * t) * 0.16, pz]); });
        P.ans = [UI.anims[UI.anims.length - 1]];
      }
      pwait(640, cb);""")
rep("      flashHex(e.c, e.r, '#ffb0a0'); sfx('drum');", "      flashHex(e.c, e.r, '#b5332a'); sfx('drum');")
rep("function clearAnimFlags() { if (!R3) return; for (var id in R3.units) { var o = R3.units[id]; if (o.anim) { o.anim = false; o.c = -1; o.sig = ''; } } }",
    "function clearAnimFlags() { if (!R3) return; for (var id in R3.units) { var o = R3.units[id]; o.held = false; if (o.anim) { o.anim = false; o.c = -1; o.sig = ''; } } }")
rep("jumpTo(e.c, e.r, Math.max(cam.z, 0.8)); flashHex(e.c, e.r, '#ffe9a6'); } } }", "jumpTo(e.c, e.r, Math.max(cam.z, 0.8)); flashHex(e.c, e.r, '#b5332a'); } } }")
# 내 행군(턴 종료 때): 점령 연출
rep("      P.ans = []; if (res.captured !== undefined) sfx('fall');", "      P.ans = []; if (res.captured !== undefined) { sfx('fall'); fxFall(G.bases[res.captured], '점령'); }")

# 재생 중 공격 장면은 가까이 당겨서 보여 준다
rep("""    focus(e.tc, e.tr, pg(function () {
      setCaption(e.f, resultMsg(e.name, e.res), e.tf === G.player ? 'hit' : '');""",
"""    focusNear(e.tc, e.tr, pg(function () {
      setCaption(e.f, resultMsg(e.name, e.res), e.tf === G.player ? 'hit' : '');""")
rep("function startPlayback() {",
"""/* 싸움 장면용: 충분히 가까이(확대 1.3 이상) 보이게 한 뒤 cb */
function focusNear(c, r, cb) {
  var P = UI.play;
  if (P && P.skip) { cb(); return; }
  if (onScreen(c, r, 40) && cam.z >= 1.3) { cb(); return; }
  jumpTo(c, r, 1.6, 0, 340);
  pwait(400, cb, true);
}
function startPlayback() {""")
# ---- 도움말 ----
cut("  '<h3>출진과 행군</h3>", "  '<h3>전투</h3>",
"""  '<h3>출진과 이동</h3><p>군사 → 출진에서 병과, 무장(주장과 부장 둘), 병력, 군량을 정하면 부대가 성 앞에 나옵니다. 창병·극병·노병·기병은 무기 재고가 병력만큼 필요합니다. 부대를 누르면 이번 턴에 갈 수 있는 칸이 <b>파랗게</b> 보이고, 그 칸을 누르면 움직입니다. 적이나 적의 성을 누르면 공격합니다. 적 부대 옆 칸에 들어서면 그 턴에는 더 나아가지 못합니다. 자기 거점으로 들어가면 입성하고, 주인 없는 거점은 들어가면 차지합니다.</p>' +
  '<h3>성역과 행군 일수</h3><p>성 둘레 ' + ZONE_R + '칸(붓으로 두른 고리 안)은 그 성의 <b>성역</b>입니다. 성역의 경계를 넘으면 — 나가든 들어가든 — 그 턴의 이동은 거기서 끝납니다(옅은 파란 칸). 그래서 성에서 나와 다른 성에 닿기까지 가장 가까운 곳도 <b>30일</b>(3턴), 보통은 40~60일이 걸립니다. 적이 성역에 들어서면 한 턴의 여유가 생기니 그때 막을 준비를 하세요. 관문에는 성역이 없습니다.</p>' +
  '<h3>행군(선택)</h3><p>먼 곳까지 매 턴 직접 움직이기 번거로우면 부대 창의 <b>행군</b>을 누르고 목적지를 누르세요. 걸리는 날수를 보여 주고, 턴을 마칠 때마다 한 구간씩 알아서 갑니다. 도중에 직접 움직이거나 공격해도 됩니다.</p>' +
""")
rep("  '<h3>턴 종료와 지난 열흘</h3><p>턴 종료를 누르면 열흘이 흐릅니다. 먼저 행군 중인 내 부대가 움직이고, 이어서",
    "  '<h3>턴 종료와 지난 열흘</h3><p>턴 종료를 누르면 열흘이 흐릅니다. 먼저 행군을 맡겨 둔 내 부대가 움직이고, 이어서")
rep("거점 이름표의 붉은 숫자는 아직 일하지 않은 무장 수입니다.", "거점 이름표의 붉은 낙관 숫자는 아직 일하지 않은 무장 수입니다.")

# ---- v0.4 마무리: 성역에 막 들어선 부대는 그 턴에 그 성을 칠 수 없다(노병의 2칸 사격 포함) — 안내 문구 ----
rep("""  } else if (t.kind === 'base') {
    var e = estBase(u, t.b);
    out.push({ kind: 'attack', label: '공격', sub: d <= rg ? '병력 -' + fmt(e.t) + ' · 내구 -' + fmt(e.d) : '사거리 밖', ok: d <= rg, pri: true });""",
"""  } else if (t.kind === 'base') {
    var e = estBase(u, t.b), fresh = zoneFresh(u, t.b);
    out.push({ kind: 'attack', label: '공격', sub: fresh ? '성역에 막 들어섬 — 다음 턴부터' : (d <= rg ? '병력 -' + fmt(e.t) + ' · 내구 -' + fmt(e.d) : '사거리 밖'), ok: d <= rg && !fresh, pri: true });""")
rep("      if (!any) { if (!(UI.pickMarch && t.kind === 'base' && proposeMarch(su, c, r))) toast('닿지 않습니다 — 먼저 가까이 이동하세요'); return; }",
    "      if (!any) {\n"
    "        if (t.kind === 'base' && zoneFresh(su, t.b) && hdist(su.c, su.r, c, r) <= uRange(su)) toast('성역에 막 들어선 부대는 이번 턴에 성을 칠 수 없습니다 — 다음 턴에 공격하세요', 2800);\n"
    "        else if (!(UI.pickMarch && t.kind === 'base' && proposeMarch(su, c, r))) toast('닿지 않습니다 — 먼저 가까이 이동하세요');\n"
    "        return;\n"
    "      }")
rep("  toast(z1 >= 0 ? G.bases[z1].n + '의 성역에 들어섰습니다 — 이번 턴 이동은 여기까지입니다' : ",
    "  var foe = z1 >= 0 && G.bases[z1].owner >= 0 && G.bases[z1].owner !== G.player;\n"
    "  toast(z1 >= 0 ? G.bases[z1].n + '의 성역에 들어섰습니다 — 이번 턴 이동은 여기까지' + (foe ? ', 성 공격은 다음 턴부터입니다' : '입니다') : ")
rep("그 턴의 이동은 거기서 끝납니다(옅은 파란 칸). 그래서 성에서 나와",
    "그 턴의 이동은 거기서 끝납니다(옅은 파란 칸). 성역에 막 들어선 부대는 그 턴에 그 성을 칠 수 없습니다(노병의 두 칸 사격도 마찬가지). 그래서 성에서 나와")
# 소개 창의 낡은 안내(목적지를 고르는 v0.3 방식)를 지금 방식으로
rep("        '<li><b>군사 → 출진</b>에서 <b>목적지</b>를 고르면 부대가 바로 길을 떠나고, 남은 길은 <b>턴을 마칠 때마다</b> 이어서 갑니다. 이웃 도시까지 보통 20~60일 걸립니다.</li>' +",
    "        '<li><b>군사 → 출진</b>으로 부대를 성 앞에 내보낸 뒤, <b>파란 칸</b>을 눌러 움직이고 <b>적</b>을 눌러 공격합니다. 이웃 성까지는 적어도 30일이 걸립니다.</li>' +")
rep("/* 출진할 때 고를 수 있는 목적지: 길로 이어진 이웃 거점과 그 다음 거점 */\n", "")

# 부대 창: 성역에 막 들어선 턴이면 알려 준다 / [행군]으로 빈 성을 차지했을 때도 점령 연출
rep("""            (x.dest >= 0 ? '<p class="note"><b class="hi">' + destName(x.dest) + ' 방면 행군 중</b>'""",
    """            (x.zin >= 0 && G.bases[x.zin].owner >= 0 && G.bases[x.zin].owner !== x.f ? '<p class="note"><b class="hi">' + G.bases[x.zin].n + '의 성역에 막 들어섰습니다.</b> 성 공격은 다음 턴부터 할 수 있습니다.</p>' : '') +
            (x.dest >= 0 ? '<p class="note"><b class="hi">' + destName(x.dest) + ' 방면 행군 중</b>'""")
rep("          else if (res && res.ok && res.captured !== undefined) { sfx('fall'); toast(G.bases[res.captured].n + ' 점령!'); selectBase(G.bases[res.captured]); }",
    "          else if (res && res.ok && res.captured !== undefined) { sfx('fall'); fxFall(G.bases[res.captured], '점령'); toast(G.bases[res.captured].n + ' 점령!'); selectBase(G.bases[res.captured]); }")
open(os.path.join(root, 'src', 'ui_panels.js'), 'w', encoding='utf8').write(s)
print('ui_panels.js', len(s))
