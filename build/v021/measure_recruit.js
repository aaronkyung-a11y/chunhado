// v0.21 등용 손질 — 같은 판(같은 무장 · 같은 자리)에서 0.20 의 값과 0.21 의 값으로 성공률을 견준다.   node build/v021/measure_recruit.js
const fs = require('fs'), vm = require('vm'), path = require('path');
function load(root) {
  const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array };
  vm.createContext(ctx);
  for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
  return ctx;
}
function run(ctx, code) { return JSON.parse(vm.runInContext('JSON.stringify((function () {' + code + '})())', ctx)); }
const NEW = load(path.join(__dirname, '..', '..', 'src'));
const all = { hereOld: [], hereNew: [], capOld: [], capNew: [], farOld: [], farNew: [], loy100: 0, farN: 0 };
for (const [scn, seed, turns] of [[0, 3, 0], [0, 3, 30], [0, 11, 60], [0, 5, 90], [0, 21, 30], [0, 22, 60], [0, 23, 90], [0, 31, 45], [0, 32, 75], [0, 33, 120]]) {
  const r = run(NEW, `
    try { newGame(0, ${seed}); } catch (e) { return { err: String(e) }; }
    G.aiOnly = true; for (var t = 0; t < ${turns} && !G.over; t++) endTurn();
    var NEWK = { R: JSON.parse(JSON.stringify(RECRUIT)), P: JSON.parse(JSON.stringify(POACH)) };
    var OLDK = { R: { base: 35, cha: 0.7, pol: 0.2, lord: 0.4, cap: 15, capLoy: 0.8, min: 3, max: 95 }, P: { base: 15, loyK: 2.5, max: 85 } };
    function setK(K) { var k; for (k in K.R) RECRUIT[k] = K.R[k]; for (k in K.P) POACH[k] = K.P[k]; }
    function best(b, t) { var m = -1; baseOfficers(b).forEach(function (o) { if (o.unit === null) m = Math.max(m, recruitChance(b, o, t)); }); return m; }
    var out = { hereOld: [], hereNew: [], capOld: [], capNew: [], farOld: [], farNew: [], loy100: 0, farN: 0, turn: G.turn };
    G.bases.forEach(function (b) {
      if (b.owner < 0 || !baseOfficers(b).length) return;
      G.officers.forEach(function (t) {
        if (t.loc !== b.id) return;
        if (t.st === 'free') { setK(OLDK); var a = best(b, t); setK(NEWK); var n = best(b, t); if (a >= 0) { out.hereOld.push(a); out.hereNew.push(n); } }
        if (t.st === 'captive' && t.capF === b.owner) { setK(OLDK); var a2 = best(b, t); setK(NEWK); var n2 = best(b, t); if (a2 >= 0) { out.capOld.push(a2); out.capNew.push(n2); } }
      });
      poachTargets(b).forEach(function (t) {
        if (!canPoach(b, t)) return;
        var l = t.loy; setK(OLDK); if (l >= 100) t.loy = 99.999; var a = best(b, t); t.loy = l; setK(NEWK); var n = best(b, t);
        if (a < 0) return; out.farN++; out.farOld.push(a); out.farNew.push(n); if (l >= 100 && a > 0) out.loy100++;
      });
    });
    setK(NEWK); return out;`);
  if (!r || r.err) { console.log('scn', scn, r); continue; }
  for (const k of ['hereOld', 'hereNew', 'capOld', 'capNew', 'farOld', 'farNew']) all[k].push(...r[k]);
  all.loy100 += r.loy100; all.farN += r.farN;
}
function st(a) { if (!a.length) return 'n=0'; const s = a.slice().sort((x, y) => x - y), m = a.reduce((x, y) => x + y, 0) / a.length; return 'n=' + a.length + ' 평균 ' + m.toFixed(1) + '% · 가운데값 ' + s[s.length >> 1] + '% · 70% 이상 ' + (100 * a.filter(x => x >= 70).length / a.length).toFixed(0) + '% · 0% ' + (100 * a.filter(x => x === 0).length / a.length).toFixed(0) + '%'; }
function month(a, per) { return (100 * a.reduce((x, p) => x + (per ? 1 - Math.pow(1 - p / 100, 3) : p / 100), 0) / a.length).toFixed(1) + '%'; }
console.log('재야(그 성에서 가장 잘 권하는 무장으로)\n  0.20:', st(all.hereOld), '| 한 달 안에 응할 확률(턴마다 다시 권함) ' + month(all.hereOld, true));
console.log('  0.21:', st(all.hereNew), '| 한 달 안에 응할 확률(한 달에 한 번) ' + month(all.hereNew, false));
console.log('포로\n  0.20:', st(all.capOld), '| 한 달 ' + (all.capOld.length ? month(all.capOld, true) : '-'));
console.log('  0.21:', st(all.capNew), '| 한 달 ' + (all.capNew.length ? month(all.capNew, false) : '-'));
console.log('이웃한 다른 세력의 무장(한 달에 한 번)\n  0.20:', st(all.farOld), '\n  0.21:', st(all.farNew), '\n  충성 100 인데 0.20 에서 응할 수 있던 경우', all.loy100, '/', all.farN);
