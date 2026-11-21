// v0.11 — 수송대의 부대 보급(규칙 시험).   node tests/sup11.js
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.env.SRC || path.join(__dirname, '..', 'src');
const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array };
vm.createContext(ctx);
for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
let pass = 0, fail = 0;
function ok(c, msg) { if (c) pass++; else { fail++; console.log('  ✗ ' + msg); } }
const r = JSON.parse(vm.runInContext(`JSON.stringify((function () {
  newGame(0, 1); G.aiOnly = false;
  var b = facCities(0)[0], res = {};
  b.troops = 20000; b.food = 60000; b.w.spear = 9000; b.w.horse = 5000; G.factions[0].ap = 250;
  var os = idleOfficers(b).filter(function (o) { return !isLord(o); });
  // 성 앞은 자리가 좁다: 나온 부대를 들판의 빈 칸(서로 세 칸 넘게 떨어진 곳)으로 옮겨 놓고 다음 부대를 낸다
  var spots = [];
  for (var dc = -9; dc <= 9 && spots.length < 4; dc++) for (var dr = -9; dr <= 9 && spots.length < 4; dr++) {
    var c = b.c + dc, r0 = b.r + dr, k = K(c, r0); if (c < 0 || r0 < 0 || c >= W || r0 >= H) continue;
    var tt = terr(c, r0); if (tt !== 'p' && tt !== 'g' && tt !== 'h') continue;
    if (UAT[k] || BAT[k] !== undefined || PAT[k] || hdist(c, r0, b.c, b.r) < 4) continue;
    if (nbrs(c, r0).filter(function (n) { var t2 = terr(n[0], n[1]); return (t2 === 'p' || t2 === 'g' || t2 === 'h') && !PAT[K(n[0], n[1])] && BAT[K(n[0], n[1])] === undefined; }).length < 4) continue;
    if (spots.some(function (q) { return hdist(q[0], q[1], c, r0) < 4; })) continue;
    spots.push([c, r0]);
  }
  if (spots.length < 4) return { err: ['빈 칸이 모자람', spots.length, terr(b.c + 4, b.r)] };
  function out(spec, i) { var x = cmdDeploy(b, spec); if (x.ok) placeUnit(x.unit, spots[i][0], spots[i][1]); return x; }
  var A = out({ type: 'spear', ids: [os[0].id], troops: 3000, food: 300 }, 0).unit;                       // 창병 3,000 · 병량 300(20일분)
  var T = out({ type: 'trans', ids: [os[1].id], troops: 2100, food: 9000, gold: 0, cargo: { spear: 1500, halberd: 0, bow: 0, horse: 0, ram: 0 } }, 1).unit;
  var C = out({ type: 'cav', ids: [os[2].id], troops: 1000, food: 500 }, 2).unit;                         // 기병(수송대에 군마가 없다)
  var rS = out({ type: 'sword', ids: [os[3].id], troops: 1000, food: 500 }, 3), S = rS.unit;              // 검병(무기가 필요 없다)
  if (!A || !T || !C || !S) return { err: [os.length, rS.msg || '', !!A, !!T, !!C] };
  // 수송대를 A 의 옆 빈 칸으로 옮기고, C · S 도 수송대 옆으로
  function freeNbr(u, not) { var ns = nbrs(u.c, u.r); for (var i = 0; i < ns.length; i++) { var k = K(ns[i][0], ns[i][1]), t = terr(ns[i][0], ns[i][1]); if (!UAT[k] && BAT[k] === undefined && t !== 'm' && t !== 's' && t !== 'x' && t !== 'w') return ns[i]; } return null; }
  var far0 = hdist(T.c, T.r, A.c, A.r);
  // 처음에 멀리 떼어 놓는다: 수송대를 A 에서 두 칸 넘게
  res.cap = cmdCap(uLeader(A));
  var e0 = cmdSupply(T, A, { food: 1000 }); res.adj0 = [far0, e0.ok, e0.msg || ''];
  var p = freeNbr(A); placeUnit(T, p[0], p[1]);
  res.adj = hdist(T.c, T.r, A.c, A.r);
  res.targets = supplyTargets(T).map(function (u) { return uName(u); }); res.sources = supplySources(A).map(function (u) { return uName(u); });
  var mx = supplyMax(T, A); res.mx = mx;
  var tot0 = { food: A.food + T.food, troops: A.troops + T.troops, spear: A.troops + T.cargo.spear };
  res.e = { zero: cmdSupply(T, A, {}).msg, food: cmdSupply(T, A, { food: T.food + 1 }).msg, troops: cmdSupply(T, A, { troops: mx.troops + 100 }).msg, self: cmdSupply(T, T, { food: 100 }).msg, rev: cmdSupply(A, T, { food: 100 }).msg };
  var m0 = A.morale; T.morale = 40; A.morale = 80;
  var g = cmdSupply(T, A, { food: 6000, troops: mx.troops });
  res.g = g; res.after = { A: [A.troops, A.food, A.morale, A.max], T: [T.troops, T.food, T.cargo.spear, T.done] };
  res.keep = (A.food + T.food === tot0.food) && (A.troops + T.troops === tot0.troops) && (A.troops + T.cargo.spear === tot0.spear);
  res.expMorale = Math.round((3000 * 80 + mx.troops * 40) / (3000 + mx.troops));
  res.again = cmdSupply(T, A, { food: 100 }).msg;
  res.srcAfter = supplySources(A).length;
  // 기병에게: 군마가 없으면 병력은 0, 병량만
  T.done = false; var pc = freeNbr(T); placeUnit(C, pc[0], pc[1]);
  res.cav = supplyMax(T, C); var gc = cmdSupply(T, C, { food: 500 }); res.cavOk = [gc.ok, C.food];
  // 검병에게: 무기 없이 병력을 넘긴다(수송대에 100명은 남는다)
  T.done = false; var ps = freeNbr(T); placeUnit(S, ps[0], ps[1]);
  res.sw = supplyMax(T, S); res.tTroops = T.troops; var gs = cmdSupply(T, S, { troops: res.sw.troops }); res.swOk = [gs.ok, S.troops, T.troops];
  // 다른 세력의 부대에는 안 된다
  T.done = false; S.f = 1; res.foe = cmdSupply(T, S, { food: 100 }).msg; S.f = 0;
  return res;
})())`, ctx));
if (r.err) { console.log('출진 실패', JSON.stringify(r.err)); process.exit(1); }
console.log('지휘 한도 ' + r.cap + ' · 한도 ' + JSON.stringify(r.mx));
ok(!r.adj0[1] || r.adj0[0] === 1, '떨어져 있으면 안 된다: ' + JSON.stringify(r.adj0));
ok(r.adj === 1 && r.targets.length >= 1 && r.sources.length === 1, '옆 칸 판정: ' + JSON.stringify([r.adj, r.targets, r.sources]));
ok(r.mx.food === 9000 && r.mx.troops === Math.min(1500, Math.floor(Math.min(r.cap - 3000, 2000) / 100) * 100), '한도: ' + JSON.stringify(r.mx));
ok(/정하세요/.test(r.e.zero) && /모자랍니다/.test(r.e.food) && /까지/.test(r.e.troops) && /없는 대상/.test(r.e.self) && /없는 대상/.test(r.e.rev), '거절: ' + JSON.stringify(r.e));
ok(r.g.ok && r.g.food === 6000 && r.g.troops === r.mx.troops, '보급: ' + JSON.stringify(r.g));
ok(r.after.A[0] === 3000 + r.mx.troops && r.after.A[1] === 6300 && r.after.T[1] === 3000 && r.after.T[3] === true, '보급 뒤: ' + JSON.stringify(r.after));
ok(r.after.A[2] === r.expMorale, '기력이 섞여야 한다: ' + r.after.A[2] + ' ≠ ' + r.expMorale);
ok(r.after.A[3] >= r.after.A[0], '부대의 최대 병력이 따라 올라야 한다');
ok(r.keep, '병량 · 병력 · 창의 합이 그대로여야 한다');
ok(/이미 행동/.test(r.again) && r.srcAfter === 0, '보급한 수송대는 그 턴에 다시 못 한다: ' + r.again);
ok(r.cav.troops === 0 && /군마/.test(r.cav.why) && r.cavOk[0] && r.cavOk[1] === 1000, '기병: 군마가 없으면 병력 0, 병량은 된다 — ' + JSON.stringify([r.cav, r.cavOk]));
ok(r.sw.troops === Math.floor(Math.min(r.tTroops - 100, 99999) / 100) * 100 || r.sw.troops > 0, '검병: 무기 없이 — ' + JSON.stringify(r.sw));
ok(r.swOk[0] && r.swOk[2] >= 100, '수송대에 100명은 남는다: ' + JSON.stringify(r.swOk));
ok(/없는 대상/.test(r.foe), '다른 세력의 부대: ' + r.foe);
console.log('보급 뒤 — 받은 부대 [병력, 병량, 기력, 최대] ' + JSON.stringify(r.after.A) + ' · 수송대 [병력, 병량, 창, 행동 끝] ' + JSON.stringify(r.after.T));
console.log('기병에게 ' + JSON.stringify(r.cav) + ' · 검병에게 ' + JSON.stringify(r.sw) + ' → ' + JSON.stringify(r.swOk));
console.log((fail ? '실패 ' + fail + ' · ' : '') + '통과 ' + pass);
process.exit(fail ? 1 : 0);
