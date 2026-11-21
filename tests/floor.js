// 성↔성 행군의 바닥 검증 (v0.8 규칙: 성역에서 멈추지 않는다. 출진한 턴에는 거점을 칠 수 없다)
//   빈 지도에서 턴마다 갈 수 있는 모든 칸을 넓혀 가며(전수 탐색) 한 성에서 나온 부대가 다른 성을 칠 수 있는 가장 이른 턴을 잰다.
//   node tests/floor.js            현재 규칙 → 1턴째(출진한 턴) 공격이 한 건도 없어야 합격
//   NOBORN=1 node tests/floor.js   '출진한 턴에는 못 친다'가 없다면(견줘 보기 — 합격 판정 없음)
//   TMAX=3 node tests/floor.js     더 뒤 턴까지(느리다). SRC=<폴더> 로 다른 판의 규칙을 잴 수 있다(v0.7 이전은 성역 멈춤 규칙으로 계산됨)
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = path.join(__dirname, '..', process.env.SRC || 'src');
const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array, process };
vm.createContext(ctx);
for (const f of 'mapdata.js,roster.js,data.js,core.js,ai.js'.split(',')) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
ctx.NOBORN = !!process.env.NOBORN; ctx.TMAX = +(process.env.TMAX || 2);
vm.runInContext(`
newGame(0, 7);
var OLD = typeof justOut !== 'function';            // v0.7 이전 규칙(성역 멈춤)인가
console.log('units on map at start:', G.units.length, '| rule:', OLD ? 'zone halt (old)' : (NOBORN ? 'none' : 'no base attack on the deploy turn'), '| turns searched', TMAX);
var TYPES = [['spear', 0], ['bow', 0], ['cav', 0], ['ram', 0], ['trans', 0], ['spear', 3], ['bow', 3], ['cav', 3]];
var _uMaxMp = uMaxMp;
var cities = G.bases.filter(function (b) { return b.kind === 'city'; }), gates = G.bases.filter(function (b) { return b.kind !== 'city'; });
function starts(a) {
  var out = [];
  nbrs(a.c, a.r).forEach(function (q) { var c = q[0], r = q[1], k = K(c, r), t = terr(c, r);
    if (t === 'm' || t === 's' || t === 'x') return; if (UAT[k] || BAT[k] !== undefined) return;
    if (typeof facUnder !== 'function') { var pf = PAT[k]; if (pf && G.bases[pf.b].plots[pf.i].fac) return; }      // v0.11 까지: 시설 칸으로는 나가지 못했다
    out.push(k); });
  return out;
}
/* A에서 나온 부대가 t턴째에 설 수 있는 칸 */
function spread(a, type, bonus) {
  var full = UNIT_TYPES[type].mp + bonus, u = { id: -1, f: a.owner >= 0 ? a.owner : -2, c: 0, r: 0, type: type, off: [G.factions[0].lord], troops: 1000, done: false, mp: full, zin: -1 };
  var seen = {}, cur = starts(a), turns = [];
  cur.forEach(function (k) { seen[k] = 1; });
  for (var t = 1; t <= TMAX; t++) {
    var pos = {}, next = [];
    cur.forEach(function (h) {
      u.c = h % W; u.r = (h - u.c) / W; u.mp = full;
      pos[h] = 1;
      var rc = unitReach(u);
      for (var k in rc.stop) { k = +k; var fresh = OLD && ZONE[k] !== ZONE[h]; if (!fresh) pos[k] = 1; else if (!pos[k]) pos[k] = 2;
        if (!seen[k]) { seen[k] = 1; next.push(k); } }
    });
    turns.push(pos);
    cur = cur.concat(next);
  }
  return turns;
}
function firstTurn(turns, b, rg, mode) {
  for (var t = 0; t < turns.length; t++) { var pos = turns[t];
    if ((mode === 'attack' || mode === 'plot') && !OLD && !NOBORN && t === 0) continue;             // 출진한 턴에는 거점도 시설도 칠 수 없다
    for (var k in pos) { k = +k; var c = k % W, r = (k - c) / W;
      if (mode === 'attack') { var d = hdist(c, r, b.c, b.r); if (d < 1 || d > rg) continue;
        if (OLD && pos[k] === 2 && ZONE[k] === b.id) continue; return t + 1; }
      if (mode === 'plot') { for (var i = 0; i < b.plots.length; i++) if (hdist(c, r, b.plots[i].c, b.plots[i].r) === 1) return t + 1; }
      if (mode === 'zone') { if (ZONE[k] === b.id) return t + 1; }
    } }
  return 0;
}
var H1 = {}, T1 = [], pairs = 0;
function add(h, key, v) { h[key] = h[key] || {}; h[key][v || ('>' + TMAX)] = (h[key][v || ('>' + TMAX)] || 0) + 1; }
TYPES.forEach(function (T, ti) {
  var key = T[0] + (T[1] ? '+' + T[1] : ''), rg = UNIT_TYPES[T[0]].range;
  uMaxMp = function (u) { return UNIT_TYPES[u.type].mp + T[1]; };
  cities.forEach(function (a) {
    var turns = spread(a, T[0], T[1]);
    cities.forEach(function (b) { if (a === b) return; var hd = hdist(a.c, a.r, b.c, b.r); if (hd > 40) return;
      if (!ti) pairs++;
      var at = firstTurn(turns, b, rg, 'attack'), pl = firstTurn(turns, b, rg, 'plot');
      add(H1, 'city→city attack ' + key, at); add(H1, 'city→city next to a plot ' + key, pl);
      if (at === 1 || pl === 1) T1.push([key, a.n, b.n, hd, at === 1 ? 'base' : 'facility']);
    });
    gates.forEach(function (b) { var hd = hdist(a.c, a.r, b.c, b.r); if (hd > 40) return; add(H1, 'city→gate attack ' + key, firstTurn(turns, b, rg, 'attack')); });
  });
  uMaxMp = _uMaxMp;
});
console.log('city pairs within 40 hexes (ordered):', pairs);
Object.keys(H1).sort().forEach(function (k) { console.log(k, JSON.stringify(H1[k])); });
console.log('city or facility attacked on the deploy turn:', T1.length); T1.slice(0, 40).forEach(function (x) { console.log('  ' + x.join(' ')); });
var FAIL = !OLD && !NOBORN && T1.length > 0;
console.log(OLD || NOBORN ? '(comparison only)' : (FAIL ? 'FAIL' : 'PASS — no base or facility can be attacked on the turn a unit is deployed'));
`, ctx);
process.exit(ctx.FAIL ? 1 : 0);
