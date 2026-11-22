// v0.18 — 규칙 시험: 공격 명령(u.aim — 적을 찍어 두면 다가가서 알아서 친다) · 충차(빨라지고 내구를 두 배로 깎는다) · 군단의 출격 금지.   node tests/aim18.js
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.env.SRC || path.join(__dirname, '..', 'src');
const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array };
vm.createContext(ctx);
for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
let pass = 0, fail = 0;
function ok(c, msg) { if (c) pass++; else { fail++; console.log('  ✗ ' + msg); } }
const R = JSON.parse(vm.runInContext(`JSON.stringify((function () {
  var R = {}, _rnd = rnd;
  function clear(c, r) { return inMap(c, r) && terr(c, r) === 'p' && !UAT[K(c, r)] && BAT[K(c, r)] === undefined && !PAT[K(c, r)]; }
  function field() { for (var r = 6; r < H - 6; r++) for (var c = 8; c < W - 8; c++) { var good = true; for (var dr = -3; dr <= 3 && good; dr++) for (var dc = -7; dc <= 7 && good; dc++) if (!clear(c + dc, r + dr)) good = false; if (good) return [c, r]; } return null; }
  function fresh(u) { u.born = -9; u.done = false; u.mp = uMaxMp(u); u.morale = 80; u.status = null; u.stT = 0; u.ox = -1; }
  newGame(0, 11); G.aiOnly = false; if (G.peace) G.peace.until = 0;
  var b = facCities(G.player)[0], eb = G.bases.filter(function (x) { return x.owner >= 0 && x.owner !== G.player && x.kind === 'city'; }).sort(function (p, q) { return idleOfficers(q).length - idleOfficers(p).length; })[0];
  [b, eb].forEach(function (x) { x.troops = 90000; x.w.spear = x.w.halberd = x.w.bow = x.w.horse = 60000; x.w.ram = 3; x.food = 400000; G.factions[x.owner].ap = 9999; });
  R.eoff = idleOfficers(eb).length;
  function E(tr) { var o = idleOfficers(eb).sort(function (p, q) { return cmdCap(q) - cmdCap(p); })[0], r = cmdDeploy(eb, { type: 'spear', ids: [o.id], troops: Math.min(tr, Math.floor(cmdCap(o) / 100) * 100), food: 9000 }); if (!r.ok) throw new Error('적 부대: ' + r.msg); return r.unit; }
  var f = field(), ids = idleOfficers(b).filter(function (o) { return !isLord(o); }).sort(function (p, q) { return q.war - p.war; });
  var a = cmdDeploy(b, { type: 'spear', ids: [ids[0].id], troops: 6000, food: 9000 }).unit, bw = cmdDeploy(b, { type: 'bow', ids: [ids[1].id], troops: 5000, food: 9000 }).unit;
  var d = E(6000);
  [a, bw, d].forEach(fresh);
  // ① 고르는 수: 군사의 추천과 같은 셈
  placeUnit(a, f[0], f[1]); placeUnit(d, f[0] + 1, f[1]); placeUnit(bw, f[0] - 5, f[1] + 3);
  var bs = bestStrike(a, d), N = attackExpect(a, d), tv = tacticList(a).map(function (t) { var X = tacticExpect(a, d, t); return [t.id, Math.round(X.dealt - X.recv)]; });
  R.pick = { tac: bs.tac ? bs.tac.id : '', v: Math.round(bs.v), n: Math.round(N.dealt - N.recv), tv: tv };
  // ② 명령을 내린다 · 물리친다
  R.set = { own: aimSet(a, { kind: 'base', b: b }).msg || '', empty: (function () { var e0 = G.bases.filter(function (x) { return x.owner < 0; })[0]; return e0 ? (aimSet(a, { kind: 'base', b: e0 }).msg || '') : 'n/a'; })(), none: a.aim === undefined };
  dipSign(a.f, d.f, 'truce'); R.set.pact = aimSet(a, { kind: 'unit', u: d }).msg || ''; delete G.dip.pact[dipKey(a.f, d.f)];
  // ③ 먼 적 부대: 다가가고, 닿으면 친다
  placeUnit(d, f[0] + 7, f[1]); fresh(a); fresh(d);
  var s1 = aimSet(a, { kind: 'unit', u: d }); R.unit = { ok: !!s1.ok, aim: a.aim, dest: [a.dest % W, (a.dest - a.dest % W) / W], inList: marchList(G.player).some(function (x) { return x.id === a.id; }), name: aimName(a) };
  var d0 = hdist(a.c, a.r, d.c, d.r), t0 = d.troops, steps = [], guard = 0;
  rnd = function () { return 0.5; };
  while (a.aim && UMAP[d.id] && guard++ < 8) { fresh(a); var o = aimStep(a); steps.push([hdist(a.c, a.r, d.c, d.r), !!(o && o.moved), o && o.res ? (o.res.kind + (o.res.tacId ? ':' + o.res.tacId : '')) : '', d.troops]); if (o && o.res) break; }
  rnd = _rnd;
  R.unit.d0 = d0; R.unit.steps = steps; R.unit.hit = t0 - d.troops; R.unit.done = a.done; R.unit.still = !!a.aim;
  // 대상이 궤멸하면 명령은 끝난다
  fresh(a); d.troops = 1; rnd = function () { return 0.5; }; var L0 = G.log.length, o2 = aimStep(a); rnd = _rnd;
  R.kill = { end: o2 && o2.end, aim: !!a.aim, dest: a.dest, gone: !UMAP[d.id], log: G.log.slice(L0).map(function (x) { return x.t; }).join('|') };
  // 대상이 사라지면(다른 까닭) 명령을 거둔다
  var d2 = E(4000); fresh(d2); placeUnit(d2, f[0] + 6, f[1] + 2); fresh(a);
  aimSet(a, { kind: 'unit', u: d2 }); removeUnit(d2); L0 = G.log.length; var o3 = aimStep(a);
  R.gone = { end: o3 && o3.end, aim: !!a.aim, dest: a.dest, log: G.log.slice(L0).map(function (x) { return x.t; }).join('|') };
  // ④ 멀리서 쏘는 부대는 사거리 끝에 선다
  var d3 = E(6000); fresh(d3); placeUnit(d3, f[0] + 1, f[1] + 3); fresh(bw);
  aimSet(bw, { kind: 'unit', u: d3 }); rnd = function () { return 0.5; }; var o4 = aimStep(bw); rnd = _rnd;
  R.bow = { dist: hdist(bw.c, bw.r, d3.c, d3.r), moved: !!(o4 && o4.moved), res: o4 && o4.res ? o4.res.kind : '', counter: o4 && o4.res ? (o4.res.counter || 0) : -1 };
  aimClear(bw); removeUnit(d3);
  // ⑤ 적 거점: 다가가서 성 앞에 서고, 턴마다 친다. 출진한 턴에는 치지 못한다
  var ns = nbrs(eb.c, eb.r).filter(function (q) { return inMap(q[0], q[1]) && MC[0][K(q[0], q[1])] < 99 && !UAT[K(q[0], q[1])] && BAT[K(q[0], q[1])] === undefined; });
  var far = null; for (var rr = 3; rr <= 9 && !far; rr++) for (var qc = eb.c - rr; qc <= eb.c + rr && !far; qc++) for (var qr = eb.r - rr; qr <= eb.r + rr && !far; qr++) if (inMap(qc, qr) && hdist(qc, qr, eb.c, eb.r) === rr && rr >= 5 && MC[0][K(qc, qr)] < 99 && !UAT[K(qc, qr)] && BAT[K(qc, qr)] === undefined && !PAT[K(qc, qr)]) { placeUnit(a, qc, qr); if (marchPath(a, K(eb.c, eb.r))) far = [qc, qr]; }
  fresh(a); var s5 = aimSet(a, { kind: 'base', b: eb });
  R.base = { ok: !!s5.ok, dest: a.dest === K(eb.c, eb.r), far: far ? hdist(far[0], far[1], eb.c, eb.r) : -1, name: aimName(a) };
  var bs5 = [], tr0 = eb.troops, du0 = eb.dur; guard = 0;
  while (a.aim && guard++ < 12) { fresh(a); var o5 = aimStep(a); bs5.push([hdist(a.c, a.r, eb.c, eb.r), !!(o5 && o5.moved), !!(o5 && o5.res)]); if (o5 && o5.res) break; }
  R.base.steps = bs5; R.base.hit = [tr0 - eb.troops, du0 - eb.dur]; R.base.still = !!a.aim; R.base.adj = hdist(a.c, a.r, eb.c, eb.r);
  fresh(a); a.born = G.turn; tr0 = eb.troops; var o6 = aimStep(a); R.base.justOut = [!!(o6 && o6.res), tr0 - eb.troops, !!a.aim]; a.born = -9;
  // 성이 내 것이 되면 명령은 끝난다
  var own0 = eb.owner; eb.owner = G.player; L0 = G.log.length; fresh(a); var o7 = aimStep(a); R.base.mine = [o7 && o7.end, !!a.aim, a.dest]; eb.owner = own0;
  // ⑥ 턴을 마칠 때: 행군 다음, 군단보다 먼저 한 부대씩
  var d4 = E(6000); fresh(d4); placeUnit(a, f[0], f[1]); placeUnit(d4, f[0] + 1, f[1]); fresh(a);
  aimSet(a, { kind: 'unit', u: d4 }); var t4 = d4.troops; EVQ.length = 0;
  rnd = function () { return 0.5; }; var next = turnStepper(), st0 = next(); rnd = _rnd;
  R.turn = { kind: st0 && st0.kind, id: st0 && st0.id === a.id, hit: t4 - (UMAP[d4.id] ? d4.troops : 0), evs: EVQ.map(function (e) { return e.t + (e.res ? ':' + e.res.kind : ''); }).join(','), f: st0 && st0.f === G.player };
  // ⑦ 충차
  var rm = cmdDeploy(b, { type: 'ram', ids: [ids[2].id], troops: 5000, food: 9000 }).unit, sp = { type: 'spear', off: rm.off, troops: 5000, max: 5000, c: rm.c, r: rm.r };
  var road = -1; for (var k = 0; k < NHEX && road < 0; k++) if (RDB[k] && MC[0][k] === ROAD_COST[0] && TCH[k] !== 119) road = k;
  R.ram = { mp: UNIT_TYPES.ram.mp, siege: UNIT_TYPES.ram.siege, road: ROAD_COST.join(','), plain: MOVE_COST.p.join(','), mc: road >= 0 ? [MC[0][road], MC[1][road], MC[2][road]] : null, dur: durDmgUB(rm), durSpear: durDmgUB(sp), umax: uMaxMp(rm) };
  return R;
})())`, ctx));
// ①
ok(typeof R.pick.v === 'number' && (R.pick.tac ? R.pick.tv.some(t => t[0] === R.pick.tac && t[1] === R.pick.v && t[1] > R.pick.n * 1.05 - 1) : R.pick.v === R.pick.n && R.pick.tv.every(t => t[1] <= R.pick.n * 1.05 + 1)), '고르는 수 = 기대값(주는 피해 − 받는 반격)이 가장 큰 것, 전법은 보통 공격보다 5% 넘게 나을 때만 ' + JSON.stringify(R.pick));
// ②
ok(R.set.own === '적이 아닙니다' && (R.set.empty === '적이 아닙니다' || R.set.empty === 'n/a') && R.set.none, '내 성 · 빈 성에는 공격 명령을 내릴 수 없다 [' + R.set.own + ']');
ok(/정전 중 — 칠 수 없습니다$/.test(R.set.pact), '협정을 맺은 세력에는 내릴 수 없다 [' + R.set.pact + ']');
// ③
ok(R.unit.ok && R.unit.aim.k === 'unit' && R.unit.name && !R.unit.inList, '먼 적 부대에 공격 명령: 대상을 기억하고, 여느 행군 목록에는 들지 않는다 ' + JSON.stringify(R.unit.aim));
const us = R.unit.steps;
ok(us.length >= 2 && us[0][0] < R.unit.d0 && us[0][1] && !us[0][2] && us[us.length - 1][2] !== '' && us[us.length - 1][0] <= 3 && us[us.length - 2][0] <= 4, '턴마다 다가가서(거리 ' + R.unit.d0 + ' → ' + us.map(s => s[0]).join(' → ') + ') 닿으면 친다 [' + us[us.length - 1][2] + ']');
ok(R.unit.hit > 0 && R.unit.done && R.unit.still, '친 뒤에도 대상이 살아 있으면 명령은 남는다(피해 ' + R.unit.hit + ')');
ok(R.kill.end === 'done' && !R.kill.aim && R.kill.dest === -1 && R.kill.gone && /공격 명령을 마침/.test(R.kill.log), '대상이 궤멸하면 명령이 끝난다 [' + R.kill.log + ']');
ok(R.gone.end === 'gone' && !R.gone.aim && R.gone.dest === -1 && /칠 수 없게 되어 공격 명령을 거둠/.test(R.gone.log), '대상이 사라지면 명령을 거둔다 [' + R.gone.log + ']');
// ④
ok(R.bow.moved && R.bow.dist === 2 && R.bow.res && R.bow.counter === 0, '노병은 사거리 끝(두 칸)에 서서 쏜다 — 반격 없음 ' + JSON.stringify(R.bow));
// ⑤
const bq = R.base.steps;
ok(R.base.ok && R.base.dest && R.base.far >= 5, '적 거점에 공격 명령(거리 ' + R.base.far + '): 그 성을 향한다');
ok(bq.length >= 2 && bq[0][1] && !bq[0][2] && bq[bq.length - 1][2] && R.base.adj === 1, '성 앞까지 다가가서(' + bq.map(s => s[0]).join(' → ') + ') 닿은 턴에 친다');
ok(R.base.hit[0] > 0 && R.base.hit[1] > 0 && R.base.still, '성을 쳤다(병력 −' + R.base.hit[0] + ' · 내구 −' + R.base.hit[1] + ') — 성이 버티면 명령은 남는다');
ok(!R.base.justOut[0] && R.base.justOut[1] === 0 && R.base.justOut[2], '출진한 턴에는 거점을 치지 않는다(명령은 남는다)');
ok(R.base.mine[0] === 'gone' && !R.base.mine[1] && R.base.mine[2] === -1, '성이 내 것이 되면 명령은 끝난다');
// ⑥
ok(R.turn.kind === 'aim' && R.turn.id && R.turn.f && R.turn.hit > 0 && /act:(attack|tactic)/.test(R.turn.evs), '턴을 마치면 맨 먼저 공격 명령을 받은 부대가 친다 ' + JSON.stringify(R.turn));
// ⑦ 충차
ok(R.ram.mp === 10 && R.ram.umax === 10 && R.ram.siege === 8 && R.ram.road === '2,2,2' && R.ram.plain === '3,3,4', '충차: 이동력 10 · 공성 8 · 길의 칸값은 모두 2(길 밖은 그대로) ' + JSON.stringify(R.ram));
ok(R.ram.mc && R.ram.mc.join(',') === '2,2,2', '길 칸의 값이 보병 · 기병 · 수레 모두 2 ' + JSON.stringify(R.ram.mc));
ok(R.ram.dur >= R.ram.durSpear * 3.5 && R.ram.dur >= 500, '충차 한 번의 내구 피해 ' + R.ram.dur + ' — 같은 무장의 창병 ' + R.ram.durSpear + '의 ' + (R.ram.dur / R.ram.durSpear).toFixed(1) + '배');
// ⑧ 군단의 출격: 공격 방침은 늘 나간다 · 내정 방침은 나가지 않는다 · 군비 · 지원은 출격 금지(cp.hold)를 따른다
const C = JSON.parse(vm.runInContext(`JSON.stringify((function () {
  function run(dir, hold) {
    newGame(0, 21); G.aiOnly = false; if (G.peace) G.peace.until = 0;
    var b = facCities(G.player)[0], eb = G.bases.filter(function (x) { return x.owner >= 0 && x.owner !== G.player && x.kind === 'city'; }).sort(function (p, q) { return idleOfficers(q).length - idleOfficers(p).length; })[0];
    b.troops = 40000; b.w.spear = b.w.halberd = b.w.bow = b.w.horse = 30000; b.food = 300000; eb.troops = 60000; eb.w.spear = 30000; eb.food = 300000; G.factions[eb.owner].ap = 999;
    var cp = corpsCreate([b.id]).corps; if (dir !== 'arm') corpsSetDir(cp, dir, -1); if (hold) corpsSetHold(cp, true);
    var o = idleOfficers(eb).sort(function (p, q) { return cmdCap(q) - cmdCap(p); })[0], e = cmdDeploy(eb, { type: 'spear', ids: [o.id], troops: 5000, food: 9000 }).unit;
    var spot = null; for (var r = b.r - 3; r <= b.r + 3 && !spot; r++) for (var c = b.c - 3; c <= b.c + 3 && !spot; c++) if (inMap(c, r) && hdist(c, r, b.c, b.r) === 3 && MC[0][K(c, r)] < 99 && !UAT[K(c, r)] && BAT[K(c, r)] === undefined && terr(c, r) !== 'w') spot = [c, r];
    placeUnit(e, spot[0], spot[1]); e.born = -9; var t0 = e.troops;
    cp.ap = 200; REPORT = []; EVQ = [];
    if (corpsStart(cp)) { var st = corpsStepper(cp); var g = 0; while (st() && g++ < 400) { } corpsEnd(cp); }
    var us = corpsUnits(cp).filter(function (u) { return u.type !== 'trans'; });
    var out = { sortie: corpsSortie(cp), out: us.length, modes: us.map(function (u) { return u.ai ? u.ai.mode : ''; }).join(','), hit: t0 - (UMAP[e.id] ? e.troops : 0), near: enemyUnitsNear(G.player, b.c, b.r, 4).length };
    if (!hold && dir === 'arm') { var rr = corpsSetHold(cp, true); out.back = rr.back; out.after = corpsUnits(cp).filter(function (u) { return u.type !== 'trans'; }).map(function (u) { return u.ai.mode; }).join(','); out.holds = us.length ? corpsHolds(us[0]) : null; out.dev = (corpsSetHold(cp, false), corpsSetDir(cp, 'dev', -1), corpsSortie(cp)); out.atk = (cp.hold = true, cp.dir = 'atk', corpsSortie(cp)); }
    return out;
  }
  return { arm: run('arm', false), hold: run('arm', true), dev: run('dev', false), sup: null };
})())`, ctx));
ok(C.arm.sortie && C.arm.near >= 0 && C.arm.out >= 1 && /defend/.test(C.arm.modes), '군비 방침(출격 허용): 적이 성 가까이 오면 부대를 내어 막는다 ' + JSON.stringify(C.arm));
ok(C.arm.back === C.arm.out && C.arm.after.split(',').every(m => m === 'return') && C.arm.holds === true, '출격 금지로 바꾸면 나가 있던 부대를 불러들인다(' + C.arm.back + '개 → ' + C.arm.after + ')');
ok(C.arm.dev === false && C.arm.atk === true, '내정 방침은 늘 나가지 않고, 공격 방침은 출격 금지를 따르지 않는다');
ok(!C.hold.sortie && C.hold.out === 0 && C.hold.hit === 0, '군비 방침 + 출격 금지: 적이 와도 나가지 않는다 ' + JSON.stringify(C.hold));
ok(!C.dev.sortie && C.dev.out === 0 && C.dev.hit === 0, '내정 방침: 적이 와도 나가지 않는다 ' + JSON.stringify(C.dev));
console.log('aim18: ' + pass + ' passed, ' + fail + ' failed');
process.exit(fail ? 1 : 0);
