// 급습 막이 규칙이 실제 AI 대전에서 지켜지는지: node tests/zonecheck.js <turns> <seed>     (v0.8: 성역에서 멈추는 규칙은 없어졌다)
//  - 출진한 턴에 거점을 친 일이 없는가
//  - 성에서 나온 부대가 다른 성을 처음 치거나 들어간 것이 '출진한 턴 포함 몇 턴째'인가(최소 2여야 한다)
//  - 성역의 경계를 넘은 뒤에도 같은 턴에 더 움직인 일이 있는가(있어야 정상 — 횟수만 센다)
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = path.join(__dirname, '..', 'src');
const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat };
vm.createContext(ctx);
for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
const turns = +(process.argv[2] || 360), seed = +(process.argv[3] || 1);
vm.runInContext(`
var ROUND = 0, VIOL = [], HIST = { city: {}, gate: {} }, STAT = { moves: 0, crossings: 0, crossedWithMpLeft: 0, baseAttacks: 0, cityAttacks: 0, enters: 0, deploys: 0, bowBaseAttacks: 0 };
var _phaseStart = phaseStart, _unitMove = unitMove, _unitAttack0 = unitAttack0, _cmdDeploy = cmdDeploy;
phaseStart = function (f) { var r = _phaseStart(f); facUnits(f).forEach(function (u) { u._crossed = false; u._into = -1; }); return r; };
cmdDeploy = function (b, spec) { var r = _cmdDeploy(b, spec); if (r && r.ok) { var u = r.unit; u._born = ROUND; u._home = b.id; u._homeKind = b.kind; u._crossed = false; u._into = -1; u._first = false; STAT.deploys++; } return r; };
function contact(u, b, how) {
  if (u._first || u._born === undefined) return;
  if (b.kind !== 'city' || b.id === u._home) return;
  u._first = true; var n = ROUND - u._born + 1, h = HIST[u._homeKind === 'city' ? 'city' : 'gate'];
  h[n] = (h[n] || 0) + 1;
  if (u._homeKind === 'city' && n < 2 && how === 'attack') VIOL.push('city contact on turn ' + n + ': ' + uName(u) + ' ' + u.type + ' ' + G.bases[u._home].n + '→' + b.n + ' (' + how + ')');
}
unitMove = function (u, c, r, rc) {
  var k0 = K(u.c, u.r), was = u._crossed, tb = baseAt(c, r);
  var res = _unitMove(u, c, r, rc);
  if (res && res.ok) {
    STAT.moves++;
    var k1 = K(c, r);
    if (ZONE[k1] !== ZONE[k0]) { STAT.crossings++; u._crossed = true; u._into = ZONE[k1]; if (UMAP[u.id] && u.mp > 0) STAT.crossedWithMpLeft++; }
    if ((res.entered !== undefined || res.captured !== undefined) && tb) { STAT.enters++; contact(u, tb, res.captured !== undefined ? 'capture' : 'enter'); }
  }
  return res;
};
unitAttack0 = function (u, t) {
  var into = u._into, res = _unitAttack0(u, t);
  if (res && res.ok && t.kind === 'fac' && u._born === ROUND) VIOL.push('attacked a facility on the deploy turn: ' + uName(u) + ' round ' + ROUND);
  if (res && res.ok && t.kind === 'base') {
    STAT.baseAttacks++; if (t.b.kind === 'city') STAT.cityAttacks++; if (u.type === 'bow') STAT.bowBaseAttacks++;
    if (u._born === ROUND) VIOL.push('attacked a base on the deploy turn: ' + uName(u) + ' ' + u.type + ' → ' + t.b.n + ' round ' + ROUND);
    contact(u, t.b, 'attack');
  }
  return res;
};
`, ctx);
ctx.newGame(0, seed); ctx.G.aiOnly = true;
for (let t = 0; t < turns; t++) {
  ctx.ROUND = t;
  try { ctx.endTurn(); } catch (e) { console.log('EXCEPTION turn', t, e.stack); process.exit(1); }
  if (ctx.G.over) break;
}
console.log('seed', seed, 'turns', turns, '|', ctx.dateStr(), '| stats', JSON.stringify(ctx.STAT));
console.log('  first contact with another city, counted from the deploy turn (units from a city):', JSON.stringify(ctx.HIST.city));
console.log('  (units from a gate — exempt):', JSON.stringify(ctx.HIST.gate));
console.log('  violations', ctx.VIOL.length, ctx.VIOL.slice(0, 8));
process.exit(ctx.VIOL.length ? 1 : 0);
