#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.15 — 지형의 규칙(data.js · core.js).  ("지형과 산에 따른 영향이 필요")
   지도 쪽(tools/terrain15.py — 산을 넓히고 칸마다 높이 단계 MAPDATA.e 를 적는다)이 먼저 되어 있어야 한다.
   · 높낮이: 치는 칸이 맞는 칸보다 한 단 높을 때마다 주는 피해 +6%, 낮을 때마다 −6% (세 단까지). 반격에도 같은 셈.
   · 기병: 평지에서 평지의 적을 치면 +10%, 숲 · 구릉에서 치거나 숲 · 구릉의 적을 치면 −15%.
   · 숲 속의 적을 쏘면(두 칸 밖) −15% 더 (숲의 −15% 에 겹친다).
   · 전부터 있던 것(숲 · 구릉의 적 −15%, 강 위의 적 +20%, 강 위에서 치면 −30%)은 그대로 — 한 곳(terrMods)에서 셈하고 화면이 그 내역을 적는다.
   · 옛 저장: 산이 넓어지면서 못 가는 칸이 된 곳에 서 있던 부대는 가장 가까운 빈 칸으로 옮긴다(terrainFix)."""
import os, io
ROOT = os.environ.get('CH_ROOT') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
def rd(n): return io.open(os.path.join(ROOT, 'src', n), encoding='utf-8').read()
def wr(n, s): io.open(os.path.join(ROOT, 'src', n), 'w', encoding='utf-8').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:70])
    return s.replace(a, b)

# ---------- data.js ----------
s = rd('data.js')
s = rep(s, "var GAME_VERSION = 'v0.14';", "var GAME_VERSION = 'v0.15';")
s = rep(s, "  p: '이동이 쉽다.', f: '이동이 느리다. 방어 유리(피해 -15%). 기병 전법 불가.', h: '이동이 느리다. 방어 유리(피해 -15%).',\n  d: '조금 느리다.', w: '건너는 데 이동력이 많이 든다. 물 위에서는 공격 -30%, 받는 피해 +20%.', m: '지나갈 수 없다.', s: '지나갈 수 없다.', x: '지나갈 수 없다.'\n};",
           "  p: '이동이 쉽다. 기병이 평지의 적을 치면 +10%.', f: '이동이 느리다. 받는 피해 -15%(화살은 -15% 더). 기병은 -15%, 기병 전법 불가.', h: '이동이 느리다. 받는 피해 -15%. 기병은 -15%.',\n  d: '조금 느리다.', w: '건너는 데 이동력이 많이 든다. 물 위에서는 공격 -30%, 받는 피해 +20%.', m: '지나갈 수 없다.', s: '지나갈 수 없다.', x: '지나갈 수 없다.'\n};\n"
           "/* 지형이 싸움에 미치는 값(v0.15)\n"
           "   ELEV_K: 높이 한 단(지도 높이 0.1) 차이에 피해 ±step, max 단까지\n"
           "   TERR_K: cover 숲 · 구릉의 적 / forestShot 숲 속의 적을 쏠 때 더 / riverDef 강 위의 적 / riverAtk 강 위에서 칠 때 / cavPlain 기병이 평지에서 평지의 적을 / cavRough 기병이 숲 · 구릉에서, 또는 숲 · 구릉의 적을 */\n"
           "var ELEV_K = { step: 0.06, max: 3 };\n"
           "var TERR_K = { cover: 0.85, forestShot: 0.85, riverDef: 1.2, riverAtk: 0.7, cavPlain: 1.10, cavRough: 0.85 };")
wr('data.js', s)

# ---------- core.js ----------
s = rd('core.js')
s = rep(s, "var NHEX = W * H, NBR = new Int32Array(NHEX * 6), TCH = new Uint8Array(NHEX), RDB = new Uint8Array(NHEX);",
           "var NHEX = W * H, NBR = new Int32Array(NHEX * 6), TCH = new Uint8Array(NHEX), RDB = new Uint8Array(NHEX), ELV = new Uint8Array(NHEX);      // ELV: 칸의 높이 단계(v0.15)")
s = rep(s, "    TCH[k] = t.charCodeAt(0); RDB[k] = rd ? 1 : 0;\n",
           "    TCH[k] = t.charCodeAt(0); RDB[k] = rd ? 1 : 0; ELV[k] = MAPDATA.e ? (parseInt(MAPDATA.e.charAt(k), 36) || 0) : 0;\n")
TERR = r'''/* ---------- 지형이 싸움에 미치는 것(v0.15) ----------
   치는 부대 a 가 맞는 부대 d 에게 주는 피해에 곱해지는 값들. ranged = 두 칸 밖에서 쏘는가. 화면도 이것으로 내역을 적는다 */
function elevOf(c, r) { return ELV[r * W + c]; }
function elevDiff(a, d) { return clamp(ELV[a.r * W + a.c] - ELV[d.r * W + d.c], -ELEV_K.max, ELEV_K.max); }
function terrMods(a, d, ranged) {
  var out = [], td = terr(d.c, d.r), ta = terr(a.c, a.r), T = TERR_K;
  if (td === 'f' || td === 'h') out.push({ k: TERRAIN_NAME[td] + '의 적', m: T.cover });
  else if (td === 'w') out.push({ k: '강 위의 적', m: T.riverDef });
  if (ranged && td === 'f') out.push({ k: '숲 속으로 쏨', m: T.forestShot });
  if (ta === 'w') out.push({ k: '강 위에서', m: T.riverAtk });
  if (UNIT_TYPES[a.type].cls === 'horse' && !ranged) {
    if (ta === 'f' || ta === 'h' || td === 'f' || td === 'h') out.push({ k: '기병 · 험한 땅', m: T.cavRough });
    else if (ta === 'p' && td === 'p') out.push({ k: '기병 · 평지', m: T.cavPlain });
  }
  var dh = elevDiff(a, d);
  if (dh) out.push({ k: dh > 0 ? '높은 곳에서' : '낮은 곳에서', m: 1 + ELEV_K.step * dh, dh: dh });
  return out;
}
function terrMul(a, d, ranged) { var ms = terrMods(a, d, ranged), x = 1; for (var i = 0; i < ms.length; i++) x *= ms[i].m; return x; }
/* 옛 저장: 못 가는 칸(넓어진 산)에 서 있는 부대를 가장 가까운 갈 수 있는 빈 칸으로 옮긴다 → 옮긴 부대들 */
function terrainFix() {
  var moved = [];
  for (var i = 0; i < G.units.length; i++) {
    var u = G.units[i], k0 = u.r * W + u.c;
    if (MC[0][k0] < 99) continue;
    var seen = {}, q = [[u.c, u.r]], hit = null, n = 0; seen[k0] = 1;
    while (q.length && !hit && n < 4000) {
      var p = q.shift(), ns = nbrs(p[0], p[1]); n++;
      for (var j = 0; j < ns.length && !hit; j++) { var nk = ns[j][1] * W + ns[j][0]; if (seen[nk]) continue; seen[nk] = 1; if (MC[0][nk] < 99 && !UAT[nk] && BAT[nk] === undefined) hit = ns[j]; else q.push(ns[j]); }
    }
    if (hit) { placeUnit(u, hit[0], hit[1]); moved.push(u); }
  }
  return moved;
}

function dmgBase(a, d, mult, ranged) {'''
s = rep(s, "function dmgBase(a, d, mult, ranged) {", TERR)
s = rep(s, "  var td = terr(d.c, d.r), ta = terr(a.c, a.r);\n  if (td === 'f' || td === 'h') x *= 0.85; else if (td === 'w') x *= 1.2;\n  if (ta === 'w') x *= 0.7;\n  if (d.status === 'confuse') x *= 1.25;\n  return x;",
           "  x *= terrMul(a, d, ranged);                                  // v0.15: 지형 · 높낮이 · 병과\n  if (d.status === 'confuse') x *= 1.25;\n  return x;")
s = rep(s, "  if (terr(a.c, a.r) === 'w') x *= 0.7;\n  return Math.max(20, Math.round(x));", "  if (terr(a.c, a.r) === 'w') x *= TERR_K.riverAtk;\n  return Math.max(20, Math.round(x));")
s = rep(s, "  G = g; reindex(); REPORT = []; EVQ = []; JOT = null;\n  corpsFix();\n",
           "  G = g; reindex(); REPORT = []; EVQ = []; JOT = null;\n  var tfix = terrainFix();                                               // v0.15: 산이 넓어졌다 — 못 가는 칸에 서 있던 부대를 옮긴다\n  for (var ti = 0; ti < tfix.length; ti++) if (tfix[ti].f === G.player) logMsg(uName(tfix[ti]) + ' — 지형이 바뀌어(v0.15) 옆의 갈 수 있는 칸으로 옮겼습니다', tfix[ti].c, tfix[ti].r, G.player, 1);\n  corpsFix();\n")
wr('core.js', s)
print('p1_terrain ok')
