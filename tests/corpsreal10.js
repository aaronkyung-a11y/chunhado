// v0.10 — 평소대로 시작해(아무것도 보태 주지 않고) 군단에 공격을 맡겨 두면 어떻게 되는가.
//   node tests/corpsreal10.js          (몇 분 걸린다)
// 원소로 시작해 첫 턴에 군단을 만들고 공격 방침을 준 뒤 150턴까지 턴만 넘긴다. 처음 나선 턴 · 함락한 턴 · 30턴마다의 '낼 수 있는 병력/필요'와 목표의 수비.
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.env.SRC || path.join(__dirname, '..', 'src');
function run(seed, names, tname) {
  const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat };
  vm.createContext(ctx);
  for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
  ctx.ARG = { seed, names, tname };
  return vm.runInContext(`(function () {
    newGame(4, ARG.seed);
    var T = G.bases[baseByName(ARG.tname)], cp = corpsCreate(ARG.names.map(function (n) { return G.bases[baseByName(n)].id; })).corps;
    corpsSetDir(cp, 'atk', T.id);
    var first = 0, fell = 0, log = [], t;
    for (t = 1; t <= 150 && !fell && !G.over; t++) {
      endTurn();
      if (!first && corpsUnits(cp).some(function (u) { return u.type !== 'trans' && u.ai && u.ai.mode === 'attack'; })) first = t;
      if (T.owner === G.player) fell = t;
      if (t % 30 === 0) { var o = corpsById(cp.id) ? corpsOutlook(cp, T) : null; log.push(t + '턴 ' + (o ? o.have + '/' + o.need : '-') + ' 수비 ' + T.troops); }
    }
    return { first: first, fell: fell, over: G.over, log: log, bases: facBases(G.player).length };
  })()`, ctx);
}
for (const [names, t] of [[['남피', '평원'], '계'], [['남피', '평원', '업'], '계'], [['남피', '평원', '업'], '북해']]) for (const seed of [1, 2, 3]) {
  const r = run(seed, names, t);
  console.log(names.join('+') + ' → ' + t + ' 씨앗 ' + seed + ': 처음 나선 턴 ' + (r.first || '-') + ' · 함락 ' + (r.fell ? r.fell + '턴' : '못 함') + ' · 거점 ' + r.bases + ' | ' + r.log.join(' | '));
}
