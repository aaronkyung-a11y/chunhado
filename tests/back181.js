// v0.18.1 — 규칙 시험: 수송을 마친 무장이 머물지 · 돌아올지(u.back).   node tests/back181.js
//   돌아온다 + 아군 거점에 들어감 → 짐은 그 거점에, 무장은 떠나온 거점으로 걸어서(이동 명령과 같은 날수)
//   돌아온다 + 부대에 보급       → 수송대가 떠나온 거점으로 행군(u.dest)
//   떠나온 거점을 잃었거나 · 들어간 곳이 떠나온 거점이거나 · 빈 거점을 차지한 때는 머문다. 고르지 않으면 전과 같다.
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.env.SRC || path.join(__dirname, '..', 'src');
const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array };
vm.createContext(ctx);
for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
let pass = 0, fail = 0;
function ok(c, msg) { if (c) pass++; else { fail++; console.log('  ✗ ' + msg); } }
const R = JSON.parse(vm.runInContext(`JSON.stringify((function () {
  var R = {};
  function fresh(u) { u.born = -9; u.done = false; u.mp = uMaxMp(u); u.morale = 80; u.status = null; u.stT = 0; u.ox = -1; }
  function door(u, b) {                                   // 거점 b 의 옆 칸 가운데 부대 u 가 설 수 있는 곳
    var ns = nbrs(b.c, b.r);
    for (var i = 0; i < ns.length; i++) { var c = ns[i][0], r = ns[i][1]; if (inMap(c, r) && !UAT[K(c, r)] && BAT[K(c, r)] === undefined && moveCost(u, c, r) < 99 && !G.fires[K(c, r)]) return [c, r]; }
    return null;
  }
  function into(u, b) { var d = door(u, b); if (!d) throw new Error('옆 칸이 없다: ' + b.n); placeUnit(u, d[0], d[1]); fresh(u); return unitMove(u, b.c, b.r); }
  function snap(o) { return { st: o.st, loc: o.loc, dest: o.dest, eta: o.eta, unit: o.unit, acted: o.acted }; }
  newGame(0, 11); G.aiOnly = false;
  R.ver = GAME_VERSION;
  var A = facCities(G.player)[0];
  // 두 번째 거점: 주인 없는 거점 가운데 가장 가까운 곳을 내 것으로 둔다(그다음으로 가까운 빈 거점은 '차지'하는 시험에 쓴다)
  var empties = G.bases.filter(function (x) { return x.owner < 0; }).sort(function (p, q) { return hdist(A.c, A.r, p.c, p.r) - hdist(A.c, A.r, q.c, q.r); });
  var B = empties.filter(function (x) { return travelTurns(x, A) >= 3; })[0] || empties[empties.length - 1], C = empties.filter(function (x) { return x !== B; })[0];      // B 는 걸어서 세 턴 넘게 걸리는 곳
  B.owner = G.player; B.troops = 2000; B.food = 10000; B.gold = 500;
  A.troops = 60000; A.food = 400000; A.gold = 20000; A.w.spear = 30000; A.w.bow = 9000; G.factions[G.player].ap = 9999;
  R.setup = { aid: A.id, bid: B.id, A: A.n, B: B.n, C: C ? C.n : '', dist: hdist(A.c, A.r, B.c, B.r), tt: travelTurns(B, A), idle: idleOfficers(A).length };
  var ids = idleOfficers(A).filter(function (o) { return !isLord(o); }).map(function (o) { return o.id; });
  function T(i, back, extra) { var sp = { type: 'trans', ids: [ids[i]], troops: 1000, food: 6000, gold: 300, cargo: { spear: 400, halberd: 0, bow: 0, horse: 0, ram: 0 } }; if (back !== undefined) sp.back = back; for (var k in (extra || {})) sp[k] = extra[k]; var r = cmdDeploy(A, sp); if (!r.ok) throw new Error('수송: ' + r.msg); return r.unit; }

  // ① 돌아온다: 거점에 짐을 내리고 무장은 떠나온 곳으로
  var t1 = T(0, true), o1 = off(ids[0]);
  R.flag = { back: t1.back === true, home: t1.home === A.id };
  var b0 = { troops: B.troops, food: B.food, gold: B.gold, spear: B.w.spear }, ap0 = G.factions[G.player].ap;
  var r1 = into(t1, B);
  R.in1 = { ok: !!r1.ok, entered: r1.entered === B.id, back: r1.back || null, gone: !UMAP[t1.id], o: snap(o1), ap: G.factions[G.player].ap - ap0,
    dTroops: B.troops - b0.troops, dFood: B.food - b0.food, dGold: B.gold - b0.gold, dSpear: B.w.spear - b0.spear, inB: baseOfficers(B).some(function (o) { return o.id === o1.id; }), facHas: facOfficers(G.player).some(function (o) { return o.id === o1.id; }) };
  // 날이 차면 떠나온 거점에 닿는다(턴이 시작될 때마다 하루치씩 — 이동 명령과 같은 길)
  var etas = [], guard = 0;
  while (o1.st === 'travel' && guard++ < 12) { phaseStart(G.player); etas.push(o1.eta); }
  R.arr1 = { n: guard, o: snap(o1), etas: etas };

  // ② 머문다(고르지 않음 · false): 전과 같다
  var t2 = T(1), o2 = off(ids[1]); R.flag2 = { back: t2.back === undefined };
  var r2 = into(t2, B); R.in2 = { entered: r2.entered === B.id, back: r2.back === undefined, o: snap(o2) };
  var t2b = T(2, false), o2b = off(ids[2]); var r2b = into(t2b, B); R.in2b = { flag: t2b.back === undefined, back: r2b.back === undefined, o: snap(o2b) };

  // ③ 가는 길에 바꾼다(transSetBack) · 수송대가 아니면 붙지 않는다
  var t3 = T(3), o3 = off(ids[3]); R.tog = { a: transSetBack(t3, true) && t3.back === true, home: (transHome(t3, B) || {}).id === A.id, sameBase: transHome(t3, A) === null };
  transSetBack(t3, false); R.tog.b = t3.back === undefined && transHome(t3, B) === null; transSetBack(t3, true);
  var sp = cmdDeploy(A, { type: 'spear', ids: [ids[4]], troops: 3000, food: 9000, back: true }).unit; R.tog.combat = sp.back === undefined && transSetBack(sp, true) === false && sp.back === undefined;

  // ④ 떠나온 거점을 잃었으면 머문다
  var keep = A.owner; A.owner = (G.player + 1) % G.factions.length; R.lostHome = transHome(t3, B) === null;
  var r3 = into(t3, B); A.owner = keep; R.in3 = { entered: r3.entered === B.id, back: r3.back === undefined, o: snap(o3) };

  // ⑤ 떠나온 거점으로 도로 들어가면 머문다(이미 집이다)
  var t5 = T(5, true), o5 = off(ids[5]); var r5 = into(t5, A); R.in5 = { entered: r5.entered === A.id, back: r5.back === undefined, o: snap(o5) };

  // ⑥ 빈 거점을 차지한 때는 머문다
  if (C) { var t6 = T(6, true), o6 = off(ids[6]); var r6 = into(t6, C); R.in6 = { captured: r6.captured === C.id, owner: C.owner === G.player, back: r6.back === undefined, o: snap(o6), cid: C.id }; }

  // ⑦ 부대에 보급: 돌아가기로 한 수송대는 떠나온 거점으로 행군한다
  var t7 = T(7, true), d7 = door(t7, B); placeUnit(t7, d7[0], d7[1]); fresh(t7);
  var s7 = null, ns7 = nbrs(t7.c, t7.r);
  for (var i = 0; i < ns7.length && !s7; i++) if (inMap(ns7[i][0], ns7[i][1]) && !UAT[K(ns7[i][0], ns7[i][1])] && BAT[K(ns7[i][0], ns7[i][1])] === undefined && moveCost(sp, ns7[i][0], ns7[i][1]) < 99) s7 = ns7[i];
  placeUnit(sp, s7[0], s7[1]); fresh(sp);
  t7.aim = { k: 'u', id: -1, n: '' };
  var rs = cmdSupply(t7, sp, { food: 1000, troops: 0 });
  R.sup = { ok: !!rs.ok, home: rs.home === A.id, dest: t7.dest === K(A.c, A.r), done: t7.done, aim: t7.aim === undefined, list0: marchList(G.player).some(function (x) { return x.id === t7.id; }) };
  var dA0 = hdist(t7.c, t7.r, A.c, A.r); fresh(t7);
  R.sup.list1 = marchList(G.player).some(function (x) { return x.id === t7.id; });
  var m7 = unitMarch(t7); R.sup.march = { ok: !!(m7 && m7.ok), closer: !UMAP[t7.id] || hdist(t7.c, t7.r, A.c, A.r) < dA0, entered: m7 ? m7.entered : undefined };
  // 머물기로 한 수송대는 보급해도 그 자리
  var t8 = T(8), d8 = null, ns8 = nbrs(sp.c, sp.r);
  for (i = 0; i < ns8.length && !d8; i++) if (inMap(ns8[i][0], ns8[i][1]) && !UAT[K(ns8[i][0], ns8[i][1])] && BAT[K(ns8[i][0], ns8[i][1])] === undefined && moveCost(t8, ns8[i][0], ns8[i][1]) < 99) d8 = ns8[i];
  placeUnit(t8, d8[0], d8[1]); fresh(t8);
  var rs8 = cmdSupply(t8, sp, { food: 1000, troops: 0 }); R.sup8 = { ok: !!rs8.ok, home: rs8.home === undefined, dest: t8.dest };

  // ⑧ 저장했다 불러도 남는다
  transSetBack(t8, true); var saved = serialize(), g2 = JSON.parse(saved);
  R.save = { back: g2.units.filter(function (u) { return u.id === t8.id; })[0].back === true, none: g2.units.filter(function (u) { return u.id === sp.id; })[0].back === undefined };
  var okLoad = deserialize(saved); R.save.load = okLoad !== false && UMAP[t8.id] && UMAP[t8.id].back === true;
  return R;
})())`, ctx));

// AI와 군단은 쓰지 않는다: AI만으로 30턴을 돌려 back 이 붙은 부대가 한 번도 없어야 한다
const AI = JSON.parse(vm.runInContext(`JSON.stringify((function () {
  newGame(0, 5); G.aiOnly = true; var seen = 0, trans = 0, entered = 0;
  for (var t = 0; t < 30 && !G.over; t++) { endTurn(); G.units.forEach(function (u) { if (u.back !== undefined) seen++; if (u.type === 'trans') trans++; }); }
  return { seen: seen, trans: trans, turn: G.turn, travel: G.officers.filter(function (o) { return o.st === 'travel'; }).length };
})())`, ctx));

console.log('준비', JSON.stringify(R.setup));
ok(/^v0\.(18\.[1-9]|19|[2-9]\d)/.test(R.ver), '판 번호가 v0.18.1 이후 [' + R.ver + ']');
ok(R.setup.idle >= 10 && R.setup.tt >= 3, '준비: 쉬는 무장 ' + R.setup.idle + '명 · 돌아오는 데 ' + R.setup.tt + '턴');
ok(R.flag.back && R.flag.home, '① 돌아온다로 낸 수송대에는 back 이 붙는다(떠나온 거점 = home)');
ok(R.in1.ok && R.in1.entered && R.in1.gone, '① 아군 거점에 들어간다(부대는 사라진다)');
ok(R.in1.dTroops === 1000 && R.in1.dGold === 300 && R.in1.dFood === 6000 && R.in1.dSpear === 400, '① 실은 것은 모두 그 거점에 합쳐진다 ' + JSON.stringify([R.in1.dTroops, R.in1.dGold, R.in1.dFood, R.in1.dSpear]));
ok(R.in1.back && R.in1.back.turns === R.setup.tt && R.in1.back.turns >= 1, '① 결과에 돌아갈 곳과 날수(이동 명령과 같은 셈) ' + JSON.stringify(R.in1.back));
ok(R.in1.o.st === 'travel' && R.in1.o.dest === R.setup.aid && R.in1.o.loc === R.setup.bid && R.in1.o.eta === R.setup.tt && R.in1.o.unit === null && R.in1.o.acted === true && R.in1.back.to === R.setup.aid, '① 무장은 길 위에 있다 ' + JSON.stringify(R.in1.o));
ok(!R.in1.inB && R.in1.facHas, '① 길 위의 무장은 내린 거점의 무장 목록에 없고, 세력의 무장으로는 남는다');
ok(R.in1.ap === 0, '① 돌아가는 데 행동력은 들지 않는다 [' + R.in1.ap + ']');
ok(R.arr1.n === R.setup.tt && R.arr1.o.st === 'active' && R.arr1.o.loc === R.setup.aid && R.arr1.o.acted === false && R.arr1.etas.join() === Array.from({ length: R.setup.tt }, (_, i) => R.setup.tt - 1 - i).join(), '① ' + R.setup.tt + '턴 뒤 떠나온 거점에 닿아 쉰다 ' + JSON.stringify(R.arr1));
ok(R.flag2.back && R.in2.entered && R.in2.back && R.in2.o.st === 'active' && R.in2.o.acted === true, '② 고르지 않으면 전과 같다 — 들어간 거점에 머문다 ' + JSON.stringify(R.in2.o));
ok(R.in2b.flag && R.in2b.back && R.in2b.o.st === 'active', '② back: false 도 같다');
ok(R.tog.a && R.tog.home && R.tog.sameBase && R.tog.b, '③ 가는 길에 바꾼다(transSetBack) — 돌아갈 곳은 떠나온 거점, 그 거점에 들어가는 것이면 없다');
ok(R.tog.combat, '③ 수송대가 아니면 back 이 붙지 않는다');
ok(R.lostHome && R.in3.entered && R.in3.back && R.in3.o.st === 'active', '④ 떠나온 거점을 잃었으면 머문다 ' + JSON.stringify(R.in3.o));
ok(R.in5.entered && R.in5.back && R.in5.o.st === 'active', '⑤ 떠나온 거점으로 도로 들어가면 머문다');
if (R.in6) ok(R.in6.captured && R.in6.owner && R.in6.back && R.in6.o.st === 'active' && R.in6.o.loc === R.in6.cid, '⑥ 빈 거점을 차지한 때는 머문다 ' + JSON.stringify(R.in6.o));
else ok(false, '⑥ 빈 거점이 하나뿐이라 시험하지 못했다');
ok(R.sup.ok && R.sup.home && R.sup.dest && R.sup.done && R.sup.aim, '⑦ 보급을 마치면 떠나온 거점으로 행군 명령이 선다(공격 명령은 지운다) ' + JSON.stringify(R.sup));
ok(!R.sup.list0 && R.sup.list1, '⑦ 보급한 턴에는 움직이지 않고(행동 끝), 다음 턴부터 행군 차례에 든다');
ok(R.sup.march.ok && R.sup.march.closer, '⑦ 행군하면 떠나온 거점에 가까워진다 ' + JSON.stringify(R.sup.march));
ok(R.sup8.ok && R.sup8.home && R.sup8.dest === -1, '⑦ 머물기로 한 수송대는 보급해도 그 자리(전과 같다)');
ok(R.save.back && R.save.none && R.save.load, '⑧ 저장했다 불러도 남는다(다른 부대에는 없다)');
ok(AI.seen === 0 && AI.turn > 20, 'AI만으로 30턴: back 이 붙은 부대 0 (수송대는 ' + AI.trans + '번 보였다 · ' + AI.turn + '턴)');
console.log(fail ? 'FAIL ' + fail : 'PASS ' + pass);
process.exit(fail ? 1 : 0);
