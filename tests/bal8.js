// 균형 재기: AI 끼리 돌리며 돈·병량·병력·시설·전투가 어떻게 흘러가는지 센다.   node tests/bal8.js <turns> <seed>     (SRC=<폴더> 로 다른 판과 견줌)
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.env.SRC || path.join(__dirname, '..', 'src');
const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array };
vm.createContext(ctx);
for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
const turns = +(process.argv[2] || 216), seed = +(process.argv[3] || 1);
vm.runInContext(`
var C = { draft: 0, drafted: 0, produce: 0, build: 0, merge: 0, patrol: 0, reward: 0, deploy: 0, tacOk: 0, tacCrit: 0, tacFail: 0, tacDmg: 0, tacCounter: 0, atk: 0, atkDmg: 0, atkCounter: 0, unitsLost: 0, captures: 0, starve: 0 };
function wrap(name, fn) { var o = this[name]; if (typeof o !== 'function') return; this[name] = function () { var r = o.apply(this, arguments); try { fn(r, arguments); } catch (e) { } return r; }; }
wrap('cmdDraft', function (r) { if (r && r.ok) { C.draft++; C.drafted += r.n; } });
wrap('cmdProduce', function (r) { if (r && r.ok) C.produce++; });
wrap('cmdDevelop', function (r) { if (r && r.ok) C.build++; });
wrap('cmdMerge', function (r) { if (r && r.ok) C.merge++; });
wrap('cmdPatrol', function (r) { if (r && r.ok) C.patrol++; });
wrap('cmdReward', function (r) { if (r && r.ok) C.reward++; });
wrap('cmdDeploy', function (r) { if (r && r.ok) C.deploy++; });
wrap('unitTactic0', function (r) { if (r && r.ok) { if (r.fail) C.tacFail++; else { C.tacOk++; if (r.crit) C.tacCrit++; } C.tacDmg += r.dmg || 0; C.tacCounter += r.counter || 0; } });
wrap('unitAttack0', function (r) { if (r && r.ok && r.kind === 'unit') { C.atk++; C.atkDmg += r.dmg || 0; C.atkCounter += r.counter || 0; } });
wrap('destroyUnit', function () { C.unitsLost++; });
wrap('captureBase', function () { C.captures++; });
function snap() {
  var gold = 0, gi = 0, food = 0, fi = 0, tr = 0, fac = {}, empty = 0, plots = 0, cities = 0, held = 0, ut = 0, order = 0;
  G.bases.forEach(function (b) { if (b.kind !== 'city') return; cities++; if (b.owner < 0) return; held++; gold += b.gold; gi += goldIncome(b); food += b.food; fi += foodIncome(b); tr += b.troops; order += b.order;
    b.plots.forEach(function (p) { plots++; if (!p.fac) empty++; else if (p.fac.done) fac[p.fac.t] = (fac[p.fac.t] || 0) + 1; }); });
  G.units.forEach(function (u) { ut += u.troops; });
  var alive = G.factions.filter(function (f) { return f.alive; }), top = alive.map(function (f, i) { return facCities(G.factions.indexOf(f)).length; }).sort(function (a, b) { return b - a; });
  return { date: dateStr(), alive: alive.length, held: held, top3: top.slice(0, 3).join('/'), gold: gold, goldPerCityMonth: Math.round(gi / Math.max(1, held)), food: food, foodPerCityQuarter: Math.round(fi / Math.max(1, held)), garrison: tr, field: ut, units: G.units.length, order: Math.round(order / Math.max(1, held)),
    market: fac.market || 0, farm: fac.farm || 0, other: (fac.barracks || 0) + (fac.smithy || 0) + (fac.stable || 0) + (fac.workshop || 0) + (fac.mint || 0) + (fac.granary || 0), empty: empty, plots: plots };
}
`, ctx);
ctx.newGame(0, seed); ctx.G.aiOnly = true;
const marks = [0, 36, 72, 108, 144, 216, 288, 360];
const rows = [];
for (let t = 0; t <= turns; t++) {
  if (marks.includes(t)) rows.push(Object.assign({ t }, ctx.snap(), { c: JSON.parse(JSON.stringify(ctx.C)) }));
  if (t === turns) break;
  try { ctx.endTurn(); } catch (e) { console.log('EXCEPTION turn', t, e.stack); process.exit(1); }
  if (ctx.G.over) { rows.push(Object.assign({ t: t + 1, over: 1 }, ctx.snap(), { c: JSON.parse(JSON.stringify(ctx.C)) })); break; }
}
console.log('seed', seed, '| src', path.basename(root));
console.log(' 턴  날짜           세력 성(상위3)    금합계  성당월수입  병량합계  성당분기수확  주둔     야전(부대)   치안  시장 농장 기타 빈터/부지');
for (const r of rows) console.log(String(r.t).padStart(3), r.date.padEnd(13), String(r.alive).padStart(3), (r.held + '(' + r.top3 + ')').padEnd(12), String(r.gold).padStart(7), String(r.goldPerCityMonth).padStart(8), String(r.food).padStart(10), String(r.foodPerCityQuarter).padStart(9), String(r.garrison).padStart(9), (r.field + '(' + r.units + ')').padStart(12), String(r.order).padStart(5), String(r.market).padStart(5), String(r.farm).padStart(4), String(r.other).padStart(4), (r.empty + '/' + r.plots).padStart(8));
const c = rows[rows.length - 1].c;
console.log(' 누적: 징병 ' + c.draft + '회(' + c.drafted + '명) 생산 ' + c.produce + ' 건설 ' + c.build + ' 합병 ' + c.merge + ' 순찰 ' + c.patrol + ' 포상 ' + c.reward + ' 출진 ' + c.deploy + ' | 부대 궤멸 ' + c.unitsLost + ' 거점 함락 ' + c.captures);
console.log(' 전투: 보통 공격 ' + c.atk + '회 평균 피해 ' + Math.round(c.atkDmg / Math.max(1, c.atk)) + ' 평균 반격 ' + Math.round(c.atkCounter / Math.max(1, c.atk)) + ' | 전법 성공 ' + c.tacOk + '(대성공 ' + c.tacCrit + ') 실패 ' + c.tacFail + ' 평균 피해 ' + Math.round(c.tacDmg / Math.max(1, c.tacOk + c.tacFail)) + ' 평균 반격 ' + Math.round(c.tacCounter / Math.max(1, c.tacOk + c.tacFail)));
