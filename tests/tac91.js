// 전법이 보통 공격보다 얼마나 이득인가 — 같은 싸움 장면들 위에서 숫자 묶음(규칙)을 바꿔 가며 잰다.
//   node tests/tac91.js [turns=144] [seed=1]        BASE=<묶음 이름> 판이 흘러갈 규칙(기본 v0.9.1) · SETS='{…}' 다른 묶음을 넣어 볼 때 · SRC=<폴더>
// 방법: AI 끼리 한 판을 돌리면서 부대가 부대를 칠 때마다 그 순간의 두 부대를 붙잡아, 쓸 수 있는 전법 하나하나의 기대 피해·기대 반격을
//       core.js 의 tacticExpect 로 계산한다(주사위를 굴리지 않으므로 판의 흐름은 바뀌지 않는다). 같은 자리에서 보통 공격을 했을 때의 기대값(attackExpect)을 1 로 놓고 견준다.
//       tacticExpect 가 실제 판정과 맞는지는 tests/exp91.js 가 따로 본다.
// 계산에 넣은 것·넣지 않은 것은 core.js 의 tacticExpect 머리말에 있다(일기토, 맞은 뒤 줄어든 병력으로 약해지는 반격, 혼란·기력 깎기 같은 효과의 값어치는 넣지 않는다).
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.env.SRC || path.join(__dirname, '..', 'src');
const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array };
vm.createContext(ctx);
for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
const turns = +(process.argv[2] || 144), seed = +(process.argv[3] || 1);
const M09 = { dolchul: 1.25, naseon: 1.35, idan: 1.55, galkwi: 1.25, hoengchi: 1.15, seonpung: 1.05, hwasi: 1.1, gwansi: 1.3, nansa: 1.05, dolgyeok: 1.3, dolpa: 1.35, doljin: 1.6 };
function mul(k) { const o = {}; for (const id in M09) o[id] = Math.round(M09[id] * k * 20) / 20; return o; }      // 0.05 단위로
const SETS = JSON.parse(process.env.SETS || 'null') || {
  'v0.9':   { rate: { C: 55, B: 63, A: 71, S: 80 }, K: { okCounter: 0.4, failDmg: 0.5, failCounter: 0.7, crit: 1.3, critGod: 1.43, stat: 0.6, statLo: -24, statHi: 12 }, mult: M09 },
  'v0.9.1': { rate: { C: 55, B: 63, A: 71, S: 80 }, K: { okCounter: 0.55, failDmg: 0.4, failCounter: 0.85, crit: 1.25, critGod: 1.375, stat: 0.8, statLo: -30, statHi: 15 },
              mult: { dolchul: 1.15, naseon: 1.3, idan: 1.45, galkwi: 1.0, hoengchi: 1.15, seonpung: 1.05, hwasi: 1.05, gwansi: 1.25, nansa: 1.0, dolgyeok: 1.25, dolpa: 1.1, doljin: 1.5 } }
};
ctx.SETS = SETS; ctx.BASESET = process.env.BASE || (SETS['v0.9.1'] ? 'v0.9.1' : Object.keys(SETS)[0]);
vm.runInContext(`
var OPP = [];                                    // 장면마다: { diff, ranged, n: {dealt, recv}, sets: { 이름: [ {id, p, pc, dealt, recv} ... ] } }
function useSet(S) { var k, t, i; for (k in S.rate) TACTIC_RATE[k] = S.rate[k]; for (k in S.K) TACTIC_K[k] = S.K[k]; for (t in TACTICS) for (i = 0; i < TACTICS[t].length; i++) TACTICS[t][i].mult = S.mult[TACTICS[t][i].id]; }
function look(u, d) {
  var N = attackExpect(u, d);
  var rec = { diff: uWar(u) * 0.6 + uLeader(u).ldr * 0.4 - uLdr(d), ranged: hdist(u.c, u.r, d.c, d.r) > 1, type: u.type, n: { dealt: N.dealt, recv: N.recv }, sets: {} }, any = false;
  for (var name in SETS) {
    useSet(SETS[name]);
    var tl = tacticList(u), list = [];
    for (var i = 0; i < tl.length; i++) {
      var tac = tl[i]; if (u.morale < tac.cost) continue;
      var tt = tacticTargets(u, tac), okT = false; for (var q = 0; q < tt.length; q++) if (tt[q].u === d) okT = true;
      if (!okT) continue;
      var X = tacticExpect(u, d, tac);
      list.push({ id: tac.id, cost: tac.cost, p: X.ok, pc: X.crit, dealt: X.dealt, recv: X.recv });
      any = true;
    }
    rec.sets[name] = list;
  }
  useSet(SETS[BASESET]);
  if (any) OPP.push(rec);
}
var _a = unitAttack0, _t = unitTactic0;
unitAttack0 = function (u, t) { if (t.kind === 'unit' && !u.done) look(u, t.u); return _a.apply(this, arguments); };
unitTactic0 = function (u, tac, t) { if (!u.done) look(u, t.u); return _t.apply(this, arguments); };
`, ctx);
vm.runInContext('useSet(SETS[BASESET])', ctx);
ctx.newGame(0, seed); ctx.G.aiOnly = true;
for (let t = 0; t < turns; t++) { ctx.endTurn(); if (ctx.G.over) break; }
const OPP = ctx.OPP, NAMES = {}; for (const t in ctx.TACTICS) for (const x of ctx.TACTICS[t]) NAMES[x.id] = x.name;
const f2 = x => (Math.round(x * 100) / 100).toFixed(2);
console.log('src ' + path.basename(root) + ' | seed ' + seed + ' | ' + turns + '턴 | 판은 "' + ctx.BASESET + '" 규칙으로 흘러감 | 전법을 쓸 수 있었던 싸움 장면 ' + OPP.length + '개 (원거리 ' + OPP.filter(o => o.ranged).length + ')');
const classes = [['강한 쪽이 침 (무장 차 +10 이상)', o => o.diff >= 10], ['비슷함 (−10 ~ +10)', o => o.diff > -10 && o.diff < 10], ['약한 쪽이 침 (−10 이하)', o => o.diff <= -10], ['모두', o => true]];
for (const name of Object.keys(SETS)) {
  const S = SETS[name];
  console.log('\n■ ' + name + '  — 적성 ' + ['C', 'B', 'A', 'S'].map(k => S.rate[k]).join('/') + ' · 성공 반격 ' + S.K.okCounter + ' · 실패 피해 ' + S.K.failDmg + ' · 실패 반격 ' + S.K.failCounter + ' · 대성공 ×' + S.K.crit + '(' + S.K.critGod + ') · 무장 항 ×' + S.K.stat + ' [' + S.K.statLo + '~' + S.K.statHi + '] · 배수 ' + Object.keys(S.mult).map(k => S.mult[k]).join(' '));
  console.log('   ' + '싸움 장면'.padEnd(26) + '장면   성공률  | 피해가 가장 큰 전법: 피해 · 반격 · 남는 몫 | 남는 몫이 가장 큰 전법: 피해 · 반격 · 남는 몫 | 전법이 이득인 장면');
  for (const [label, fn] of classes) {
    const os = OPP.filter(fn).filter(o => o.sets[name].length);
    if (!os.length) { console.log('   ' + label.padEnd(26) + '0'); continue; }
    let nD = 0, nR = 0, bD = 0, bR = 0, gD = 0, gR = 0, better = 0, pSum = 0;
    for (const o of os) {
      const L = o.sets[name], N = o.n;
      const byD = L.reduce((a, b) => (b.dealt > a.dealt ? b : a)), byN = L.reduce((a, b) => (b.dealt - b.recv > a.dealt - a.recv ? b : a));
      nD += N.dealt; nR += N.recv; bD += byD.dealt; bR += byD.recv; gD += byN.dealt; gR += byN.recv; pSum += byD.p;
      if (byN.dealt - byN.recv > N.dealt - N.recv + 0.1 * N.dealt) better++;
    }
    const net = (d, r) => f2((d - r) / (nD - nR));
    console.log('   ' + label.padEnd(26) + String(os.length).padStart(5) + '  ' + String(Math.round(pSum / os.length)).padStart(4) + '%   |        ×' + f2(bD / nD) + ' · ×' + f2(bR / Math.max(1, nR)) + ' · ×' + net(bD, bR) + '              |          ×' + f2(gD / nD) + ' · ×' + f2(gR / Math.max(1, nR)) + ' · ×' + net(gD, gR) + '               | ' + Math.round(100 * better / os.length) + '%');
  }
  const pick = {}, avail = {};
  for (const o of OPP) { const L = o.sets[name]; if (!L.length) continue; const byN = L.reduce((a, b) => (b.dealt - b.recv > a.dealt - a.recv ? b : a)); pick[byN.id] = (pick[byN.id] || 0) + 1; for (const x of L) avail[x.id] = (avail[x.id] || 0) + 1; }
  console.log('   전법별(쓸 수 있었던 장면 가운데 남는 몫이 가장 커서 뽑힌 비율): ' + Object.keys(S.mult).map(id => NAMES[id] + ' ' + (avail[id] ? Math.round(100 * (pick[id] || 0) / avail[id]) + '%' : '-') + '(' + (avail[id] || 0) + ')').join(' · '));
}
console.log('\n읽는 법: ×1.00 = 그 장면에서 보통 공격을 했을 때의 기대값(피해 합 · 받는 반격 합 · 남는 몫 = 피해 − 반격). "이득인 장면" = 가장 나은 전법의 남는 몫이 보통 공격보다 그 피해의 10% 넘게 큰 장면의 비율.');
