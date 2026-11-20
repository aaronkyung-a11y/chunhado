# v0.8: 성역의 경계에서 멈추는 규칙을 없앤다 ("성 주변에 오면 억지로 한 턴 멈추는 데 그건 별로인 듯").
#  · 없앰: 경계를 넘으면 그 턴 이동 끝 / 막 들어선 성역의 성은 그 턴에 못 친다(zin) / 길 찾기의 경계 벌점(ZONE_PEN)
#  · 남김(급습 막이): 출진한 그 턴에는 거점을 칠 수 없다(u.born === G.turn)
#  · 성역은 이름(○○ 성역)·고리 표시·긴장한 음악의 기준으로만 남는다
import io, re
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:100])
    return s.replace(a, b)
p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()
i0 = s.index("/* 성역의 경계를 넘는 걸음이 그 턴의 이동을 끝내는가."); i1 = s.index("/* 이번 턴 이동 가능 범위.")
s = s[:i0] + """/* v0.8: 성역의 경계에서 멈추는 규칙을 없앴다(0.5~0.7: 경계를 넘으면 그 턴 이동 끝, 막 들어선 성역의 성은 그 턴에 못 침).
   성역은 이름(○○ 성역)과 고리 표시로만 남는다. 급습을 막는 장치는 하나 — 출진한 그 턴에는 거점을 칠 수 없다. */
function justOut(u) { return u.born !== undefined && u.born === G.turn; }
""" + s[i1:]
s = rep(s, "/* 이번 턴 이동 가능 범위. 반환: { cost:{key:cost}, prev:{key:key}, stop:{key:true}, halt:{key:true — 거기 서면 이번 턴 이동 끝} } */",
           "/* 이번 턴 이동 가능 범위. 반환: { cost:{key:cost}, prev:{key:key}, stop:{key:true} } */")
s = rep(s, "  var cost = {}, prev = {}, stop = {}, halt = {}, start = K(u.c, u.r), h = new Heap();", "  var cost = {}, prev = {}, stop = {}, start = K(u.c, u.r), h = new Heap();")
s = rep(s, "      if (halt[k]) continue;                                           // 성역의 경계를 넘었으면 이동 끝\n", "")
s = rep(s, "        if (zoneHalts(u, ZONE[k], ZONE[nk])) halt[nk] = true; else delete halt[nk];\n", "")
s = rep(s, "  return { cost: cost, prev: prev, stop: stop, halt: halt };", "  return { cost: cost, prev: prev, stop: stop };")
s = rep(s, "      if (ZONE[nk] !== ZONE[k] && zoneHalts(u, ZONE[k], ZONE[nk])) mc += ZONE_PEN;\n", "")
s = rep(s, "home: b.id, ox: -1, oy: -1, omp: 0, ozin: -1, zin: -1, ai: null, dest: -1 };", "home: b.id, ox: -1, oy: -1, omp: 0, born: G.turn, ai: null, dest: -1 };")
s = rep(s, "  u.ox = u.c; u.oy = u.r; u.omp = u.mp; u.ozin = (u.zin === undefined ? -1 : u.zin);", "  u.ox = u.c; u.oy = u.r; u.omp = u.mp;")
s = rep(s, """  var halted = rc.halt ? !!rc.halt[k] : ZONE[k] !== ZONE[K(from[0], from[1])];
  if (halted) { u.mp = 0; u.zin = ZONE[k]; }                // 성역의 경계를 넘었으면 이번 턴 이동은 여기까지. 막 들어선 성역의 성은 이번 턴에 칠 수 없다(zin)
  u.moved = true;
  var res = { ok: true, path: path, from: from, halted: halted };""", """  u.moved = true;
  var res = { ok: true, path: path, from: from };""")
s = rep(s, "  placeUnit(u, u.ox, u.oy); u.mp = u.omp; u.zin = (u.ozin === undefined ? -1 : u.ozin); u.moved = false; u.ox = -1;", "  placeUnit(u, u.ox, u.oy); u.mp = u.omp; u.moved = false; u.ox = -1;")
s = rep(s, """  var full = uMaxMp(u), left = u.done ? 0 : u.mp, turns = 1, z = ZONE[K(u.c, u.r)], halt = false;
  for (var i = 0; i < path.length; i++) {
    var c = path[i] % W, mc = moveCost(u, c, (path[i] - c) / W);
    if (halt || mc > left) { turns++; left = full; halt = false; }
    left -= mc;
    if (ZONE[path[i]] !== z) { if (zoneHalts(u, z, ZONE[path[i]])) halt = true; z = ZONE[path[i]]; }   // 성역의 경계를 넘으면 그 턴은 거기까지(수송대는 우리 땅 안에서 예외)
  }
  return turns;""", """  var full = uMaxMp(u), left = u.done ? 0 : u.mp, turns = 1;
  for (var i = 0; i < path.length; i++) {
    var c = path[i] % W, mc = moveCost(u, c, (path[i] - c) / W);
    if (mc > left) { turns++; left = full; }
    left -= mc;
  }
  return turns;""")
s = rep(s, "    u.mp = uMaxMp(u); u.done = false; u.moved = false; u.ox = -1; u.zin = -1;", "    u.mp = uMaxMp(u); u.done = false; u.moved = false; u.ox = -1;")
s = rep(s, "if (b.owner >= 0 && b.owner !== u.f && u.zin !== b.id) out.push({ kind: 'base', b: b, c: c, r: r, d: d }); continue; }", "if (b.owner >= 0 && b.owner !== u.f && !justOut(u)) out.push({ kind: 'base', b: b, c: c, r: r, d: d }); continue; }")
s = rep(s, "function zoneFresh(u, b) { return !!b && u.zin !== undefined && u.zin >= 0 && u.zin === b.id; }   // 이번 턴에 이 성의 성역에 막 들어섰는가\n", "")
s = rep(s, "  if (t.kind === 'base' && zoneFresh(u, t.b)) return ERR('성역에 막 들어선 부대는 이번 턴에 성을 칠 수 없습니다');", "  if (t.kind === 'base' && justOut(u)) return ERR('출진한 턴에는 거점을 칠 수 없습니다');")
assert 'zoneHalts' not in s and 'zoneFresh' not in s and 'ZONE_PEN' not in s, [m.start() for m in re.finditer('zoneHalts|zoneFresh|ZONE_PEN', s)]
print('zin left in core:', [s[m.start()-40:m.start()+40] for m in re.finditer(r'\bzin\b', s)])
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/ai.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "        if (ZONE[k] === T.id && (ZONE[K(u.c, u.r)] !== T.id || u.zin === T.id)) continue;   // 성역에 막 들어선 턴에는 그 성을 칠 수 없다\n",
           "        if (justOut(u)) continue;                                                          // 출진한 턴에는 거점을 칠 수 없다\n")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/data.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, """/* 성역: 성 둘레 이만큼의 칸. 경계를 넘으면 그 턴 이동 끝(행군 최소 30일의 근거). ZONE_PEN 은 길 찾기에서 경계를 넘는 걸음에 얹는 값 */
var ZONE_R = 2, ZONE_PEN = 8;""", """/* 성역: 성 둘레 이만큼의 칸. v0.8부터 이동을 막지 않는다 — 이름(○○ 성역)과 고리 표시, 긴장한 음악의 기준으로만 쓴다 */
var ZONE_R = 2;""")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
