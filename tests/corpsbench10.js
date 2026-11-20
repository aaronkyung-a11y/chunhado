// v0.10 — 맡겨 두면 어떻게 되는가(가늠용): 3년(108턴) 동안 직할은 아무 명령도 내리지 않고 턴만 넘긴다.
//   node tests/corpsbench10.js
//   ① 군단 없이 아무것도 안 함  ② 군주가 있는 성만 빼고 군단 하나(군비)에 맡김  ③ 모든 거점을 군단 하나(군비)에 맡김
//   끝났을 때의 거점 수 · 병력(주둔 + 부대) · 시설 수 · 금 · 무장 수. 'lose@N' 은 N턴째에 멸망.
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.env.SRC || path.join(__dirname, '..', 'src');
function run(fac, seed, mode) {
  const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat };
  vm.createContext(ctx);
  for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
  ctx.ARG = { fac, seed, mode };
  return vm.runInContext(`(function () {
    newGame(ARG.fac, ARG.seed);
    var lb = G.bases[off(G.factions[G.player].lord).loc];
    if (ARG.mode !== 'none') { var ids = facBases(G.player).filter(function (b) { return ARG.mode === 'all' || b !== lb; }).map(function (b) { return b.id; }); var r = corpsCreate(ids); if (r.ok && ARG.mode === 'dev') corpsSetDir(r.corps, 'dev', -1); }
    for (var t = 0; t < 108 && !G.over; t++) endTurn();
    var f = G.player, tr = 0, fac = 0, gold = 0; facBases(f).forEach(function (b) { tr += b.troops; gold += b.gold; b.plots.forEach(function (p) { if (p.fac) fac++; }); }); facUnits(f).forEach(function (u) { tr += u.troops; });
    return { over: G.over, turn: G.turn, bases: G.factions[f].alive ? facBases(f).length : 0, troops: tr, fac: fac, gold: gold, off: facOfficers(f).length };
  })()`, ctx);
}
for (const [fac, name] of [[4, '원소'], [14, '유표'], [0, '조조'], [9, '원술']]) for (const seed of [1, 2]) {
  const a = run(fac, seed, 'none'), b = run(fac, seed, 'arm'), c = run(fac, seed, 'all');
  const f = x => (x.over ? x.over + '@' + x.turn : '거점 ' + x.bases) + ' 병력 ' + x.troops + ' 시설 ' + x.fac + ' 금 ' + x.gold + ' 무장 ' + x.off;
  console.log(name + ' 씨앗 ' + seed + ' | 아무것도 안 함: ' + f(a) + ' | 군주 성만 빼고 군단(군비): ' + f(b) + ' | 모두 군단(군비): ' + f(c));
}
