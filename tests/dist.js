// 성↔성 행군 일수 측정: node tests/dist.js [v]
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = path.join(__dirname, '..', process.env.SRC || 'src');
const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array };
vm.createContext(ctx);
for (const f of (process.env.FILES || 'mapdata.js,roster.js,data.js,core.js,ai.js').split(',')) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
ctx.VERB = process.argv[2] === 'v';
vm.runInContext(`
newGame(0, 7);
var HASZ = typeof ZONE !== 'undefined';
// 실제 규칙으로 잰다: 임시 부대를 성 밖 칸에 세우고, 턴마다 unitReach 로 길 위에서 가장 멀리 간다
function etaSim(a, b, type, bonus) {
  var spot = deploySpot(a, { c: b.c, r: b.r }); if (!spot) return null;
  var full = UNIT_TYPES[type].mp + (bonus || 0);
  var u = { id: -1, f: a.owner >= 0 ? a.owner : -2, c: spot[0], r: spot[1], type: type, off: [G.factions[0].lord], troops: 1000, done: false, mp: full };
  var gk = K(b.c, b.r), turns = 0, hexes = 0;
  var saveOwner = b.owner; b.owner = -1;                 // 빈 성으로 보고 들어가는 턴까지 잰다
  while (turns < 60) {
    turns++; u.mp = full;
    if (K(u.c, u.r) === gk) break;
    var p = longPath(u, function (k) { return k === gk; }, 3000, [b.c, b.r, 0]);
    if (!p) { b.owner = saveOwner; return null; }
    var rc = unitReach(u), best = -1, bi = -1;
    for (var i = 0; i < p.length; i++) if (rc.stop[p[i]] || p[i] === gk && rc.cost[p[i]] !== undefined) { best = p[i]; bi = i; }
    if (best < 0) { b.owner = saveOwner; return null; }
    hexes += bi + 1; u.c = best % W; u.r = (best - u.c) / W;
    if (best === gk) break;
  }
  b.owner = saveOwner;
  return { turns: turns, hexes: hexes };
}
function uMaxMpOrig(u) { return UNIT_TYPES[u.type].mp; }
var cities = G.bases.filter(function (b) { return b.kind === 'city'; });
var res = { }, mins = {}, rows = [];
var TYPES = [['spear', 0], ['cav', 0], ['ram', 0], ['trans', 0], ['spear', 3], ['cav', 3]];
// 강행(+3)은 uMaxMp 가 특기로 주므로 여기서는 이동력을 직접 올려서 잰다
var _uMaxMp = uMaxMp;
MAPDATA.edges.forEach(function (e) {
  var a = G.bases[e[0]], b = G.bases[e[1]];
  var row = { a: a.n, b: b.n, cc: a.kind === 'city' && b.kind === 'city', hd: hdist(a.c, a.r, b.c, b.r), t: {} };
  TYPES.forEach(function (T) {
    var key = T[0] + (T[1] ? '+' + T[1] : '');
    uMaxMp = function (u) { return UNIT_TYPES[u.type].mp + T[1]; };
    var x = etaSim(a, b, T[0], T[1]), y = etaSim(b, a, T[0], T[1]);
    row.t[key] = [x ? x.turns : 0, y ? y.turns : 0];
  });
  uMaxMp = _uMaxMp;
  rows.push(row);
});
function hist(list, key) { var h = {}; list.forEach(function (x) { x.t[key].forEach(function (v) { h[v] = (h[v] || 0) + 1; }); }); return JSON.stringify(h); }
var cc = rows.filter(function (x) { return x.cc; }), cg = rows.filter(function (x) { return !x.cc; });
console.log('zone rule:', HASZ, '| city-city edges', cc.length, '(both directions counted)');
['spear', 'cav', 'ram', 'trans', 'spear+3', 'cav+3'].forEach(function (k) { console.log('  ' + k + ' turns', hist(cc, k)); });
console.log('edges with a gate', cg.length); ['spear', 'cav'].forEach(function (k) { console.log('  ' + k + ' turns', hist(cg, k)); });
cc.sort(function (x, y) { return x.hd - y.hd; });
cc.forEach(function (x, i) { if (VERB || i < 12) console.log(x.a + '-' + x.b, 'hd', x.hd, JSON.stringify(x.t)); });
// 간선이 없는 가까운 성 쌍도 확인(기병+강행)
var extraMin = 99, ex = '';
uMaxMp = function (u) { return UNIT_TYPES[u.type].mp + 3; };
for (var i = 0; i < cities.length; i++) for (var j = 0; j < cities.length; j++) {
  if (i === j) continue; var a = cities[i], b = cities[j];
  if (hdist(a.c, a.r, b.c, b.r) > 34) continue;
  if (ADJ[a.id].some(function (e) { return e.to === b.id; })) continue;
  var x = etaSim(a, b, 'cav', 3);
  if (x && x.turns < extraMin) { extraMin = x.turns; ex = a.n + '-' + b.n; }
}
uMaxMp = _uMaxMp;
console.log('non-edge city pairs within 34 hexes: min turns (cav+3) =', extraMin, ex);
`, ctx);
