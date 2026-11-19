// 성↔성 '최소 30일' 바닥 검증: 빈 지도에서 턴마다 갈 수 있는 모든 칸을 넓혀 가며(전수 탐색) 가장 이른 공격 턴을 잰다.
//   node tests/floor.js            현재 규칙
//   NOZIN=1 node tests/floor.js    '막 들어선 성역의 성은 못 친다' 규칙을 끈 경우(비교용)
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = path.join(__dirname, '..', process.env.SRC || 'src');
const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array, process };
vm.createContext(ctx);
for (const f of 'mapdata.js,roster.js,data.js,core.js,ai.js'.split(',')) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
ctx.NOZIN = !!process.env.NOZIN; ctx.TMAX = +(process.env.TMAX || 3);
vm.runInContext(`
newGame(0, 7);
console.log('units on map at start:', G.units.length, '| zone radius', ZONE_R, '| rule zin', !NOZIN);
var TYPES = [['spear', 0], ['bow', 0], ['cav', 0], ['ram', 0], ['trans', 0], ['spear', 3], ['bow', 3], ['cav', 3]];
var _uMaxMp = uMaxMp;
var cities = G.bases.filter(function (b) { return b.kind === 'city'; }), gates = G.bases.filter(function (b) { return b.kind !== 'city'; });
function starts(a) {
  var out = [];
  nbrs(a.c, a.r).forEach(function (q) { var c = q[0], r = q[1], k = K(c, r), t = terr(c, r);
    if (t === 'm' || t === 's' || t === 'x') return; if (UAT[k] || BAT[k] !== undefined) return;
    var pf = PAT[k]; if (pf && G.bases[pf.b].plots[pf.i].fac) return; out.push(k); });
  return out;
}
/* A에서 나온 부대가 t턴째에 설 수 있는 칸: fresh[k] = 그 턴에 성역 경계를 넘어 들어온 경우만 있는가 */
function spread(a, type, bonus) {
  var full = UNIT_TYPES[type].mp + bonus, u = { id: -1, f: a.owner >= 0 ? a.owner : -2, c: 0, r: 0, type: type, off: [G.factions[0].lord], troops: 1000, done: false, mp: full, zin: -1 };
  var seenStart = {}, cur = starts(a), turns = [];
  cur.forEach(function (k) { seenStart[k] = 1; });
  for (var t = 1; t <= TMAX; t++) {
    var pos = {}, next = [];           // pos[k] = 1: 성역을 넘지 않고(또는 제자리에서) 설 수 있다, 2: 이번 턴에 넘어 들어와야만 설 수 있다
    cur.forEach(function (h) {
      u.c = h % W; u.r = (h - u.c) / W; u.mp = full;
      pos[h] = 1;
      var rc = unitReach(u);
      for (var k in rc.stop) { k = +k; var fresh = ZONE[k] !== ZONE[h]; if (!fresh) pos[k] = 1; else if (!pos[k]) pos[k] = 2;
        if (!seenStart[k]) { seenStart[k] = 1; next.push(k); } }
      // 빈 성·자기 성으로 들어가는 것은 stop 에 없으므로(거점은 따로) cost 로 본다
      for (var k2 in rc.cost) { k2 = +k2; if (BAT[k2] !== undefined && k2 !== h) { if (!pos['b' + k2]) pos['b' + k2] = 1; } }
    });
    turns.push(pos);
    cur = cur.concat(next);            // 다음 턴의 출발 칸: 지금까지 설 수 있었던 모든 칸
  }
  return turns;
}
function firstTurn(turns, b, rg, mode) {
  for (var t = 0; t < turns.length; t++) { var pos = turns[t];
    for (var k in pos) { if (k.charAt(0) === 'b') continue; k = +k; var c = k % W, r = (k - c) / W;
      if (mode === 'attack') { var d = hdist(c, r, b.c, b.r); if (d < 1 || d > rg) continue;
        if (!NOZIN && pos[k] === 2 && ZONE[k] === b.id) continue; return t + 1; }
      if (mode === 'plot') { for (var i = 0; i < b.plots.length; i++) if (hdist(c, r, b.plots[i].c, b.plots[i].r) === 1) return t + 1; }
      if (mode === 'zone') { if (ZONE[k] === b.id) return t + 1; }
    } }
  return 0;
}
var H1 = {}, rowsMin = {};
function add(h, key, v) { h[key] = h[key] || {}; h[key][v || ('>' + TMAX)] = (h[key][v || ('>' + TMAX)] || 0) + 1; }
var near = [];
TYPES.forEach(function (T) {
  var key = T[0] + (T[1] ? '+' + T[1] : ''), rg = UNIT_TYPES[T[0]].range;
  uMaxMp = function (u) { return UNIT_TYPES[u.type].mp + T[1]; };
  cities.forEach(function (a) {
    var turns = spread(a, T[0], T[1]);
    cities.forEach(function (b) { if (a === b) return; var hd = hdist(a.c, a.r, b.c, b.r); if (hd > 40) return;
      var at = firstTurn(turns, b, rg, 'attack'), pl = firstTurn(turns, b, rg, 'plot'), zn = firstTurn(turns, b, rg, 'zone');
      add(H1, 'city→city attack ' + key, at); add(H1, 'city→city plot-adjacent ' + key, pl); add(H1, 'city→city zone-entry ' + key, zn);
      if (at && at < 3) near.push([key, a.n, b.n, hd, 'attack@' + at]);
      if (pl && pl < 3 && T[1] === 0 && (T[0] === 'spear' || T[0] === 'cav')) near.push([key, a.n, b.n, hd, 'plot@' + pl]);
    });
    gates.forEach(function (b) { var hd = hdist(a.c, a.r, b.c, b.r); if (hd > 40) return; add(H1, 'city→gate attack ' + key, firstTurn(turns, b, rg, 'attack')); });
  });
  gates.forEach(function (a) {
    var turns = spread(a, T[0], T[1]);
    cities.forEach(function (b) { var hd = hdist(a.c, a.r, b.c, b.r); if (hd > 40) return; add(H1, 'gate→city attack ' + key, firstTurn(turns, b, rg, 'attack')); });
  });
  uMaxMp = _uMaxMp;
});
Object.keys(H1).sort().forEach(function (k) { console.log(k, JSON.stringify(H1[k])); });
console.log('cases below 3 turns:', near.length); near.slice(0, 60).forEach(function (x) { console.log('  ' + x.join(' ')); });
`, ctx);
