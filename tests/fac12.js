// v0.12 — 시설 칸을 지나가고 설 수 있다 · 전법 실패의 피해(규칙 시험).   node tests/fac12.js     OLD=<v0.11 규칙 폴더> 를 주면 옛 규칙과도 견준다
const fs = require('fs'), vm = require('vm'), path = require('path');
function load(root) {
  const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array };
  vm.createContext(ctx);
  for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
  return ctx;
}
let pass = 0, fail = 0;
function ok(c, msg) { if (c) pass++; else { fail++; console.log('  ✗ ' + msg); } }
const SCRIPT = `JSON.stringify((function () {
  newGame(0, 1); G.aiOnly = false;
  var R = {}, b = facCities(0)[0];
  b.troops = 60000; b.food = 200000; b.gold = 50000; b.w.spear = 30000; G.factions[0].ap = 255;
  function ring() { return nbrs(b.c, b.r).filter(function (q) { var t = terr(q[0], q[1]); return t !== 'm' && t !== 's' && t !== 'x'; }); }
  function isFac(c, r) { var p = PAT[K(c, r)]; return !!(p && G.bases[p.b].plots[p.i].fac); }
  // 성 둘레의 부지마다 시설을 세운다(이미 선 것은 그대로)
  for (var i = 0; i < b.plots.length; i++) if (!b.plots[i].fac) b.plots[i].fac = { t: 'market', lv: 1, done: true, prog: 0, need: 0, rate: 0, hp: FAC_HP };
  var rg = ring(); R.ring = rg.length; R.ringFac = rg.filter(function (q) { return isFac(q[0], q[1]); }).length; R.ringFree = R.ring - R.ringFac;
  // ① 출진: 빈 땅이 먼저, 빈 땅이 다 차면 시설 칸으로
  var os = idleOfficers(b).filter(function (o) { return !isLord(o); }), outs = [];
  for (i = 0; i < R.ring && i < os.length; i++) { var x = cmdDeploy(b, { type: 'spear', ids: [os[i].id], troops: 2000, food: 2000 }); outs.push(x.ok ? [x.unit.c, x.unit.r, isFac(x.unit.c, x.unit.r) ? 1 : 0] : [x.msg]); }
  R.outs = outs; R.nOfficers = os.length;
  // ② 이동 범위에 시설 칸이 들어온다 · 실제로 들어간다
  var u = G.units.filter(function (v) { return v.f === 0; })[0];
  u.done = false; u.mp = uMaxMp(u); u.born = -9;
  var rc = unitReach(u), facStops = 0, anyFac = null;
  for (var k in rc.stop) { var c = k % W, r = (k - c) / W; if (isFac(c, r)) { facStops++; if (!anyFac && !UAT[k]) anyFac = [c, r]; } }
  R.facStops = facStops;
  if (anyFac) { var mv = unitMove(u, anyFac[0], anyFac[1], rc); R.moved = [mv.ok, u.c === anyFac[0] && u.r === anyFac[1], mv.msg || '']; }
  // ③ 부대가 선 부지에는 새로 짓지 못한다(전과 같다)
  var pl = PAT[K(u.c, u.r)]; if (pl) { var keep = b.plots[pl.i].fac; b.plots[pl.i].fac = null; var idle = idleOfficers(b); var dv = idle.length ? cmdDevelop(b, pl.i, 'farm', [idle[0].id]) : { ok: false, msg: '무장 없음' }; R.develop = [dv.ok, dv.msg || '']; b.plots[pl.i].fac = keep; }
  // ④ 남의 시설: 지나가고, 올라서고, 발밑의 시설을 친다
  var eb = null; for (i = 0; i < G.bases.length && !eb; i++) { var q = G.bases[i]; if (q.owner > 0 && q.plots && q.plots.length >= 3) eb = q; }
  for (i = 0; i < eb.plots.length; i++) if (!eb.plots[i].fac) eb.plots[i].fac = { t: 'farm', lv: 1, done: true, prog: 0, need: 0, rate: 0, hp: FAC_HP };
  var ep = null; for (i = 0; i < eb.plots.length && !ep; i++) { var t = terr(eb.plots[i].c, eb.plots[i].r); if (t !== 'm' && t !== 's' && t !== 'x' && t !== 'w' && !UAT[K(eb.plots[i].c, eb.plots[i].r)]) ep = eb.plots[i]; }
  // 옆 칸에 놓고 → 시설 칸으로 한 걸음
  var side = nbrs(ep.c, ep.r).filter(function (n) { var t2 = terr(n[0], n[1]), kk = K(n[0], n[1]); return t2 !== 'm' && t2 !== 's' && t2 !== 'x' && t2 !== 'w' && !UAT[kk] && BAT[kk] === undefined && !PAT[kk]; })[0];
  R.side = !!side;
  if (side) {
    placeUnit(u, side[0], side[1]); u.done = false; u.mp = uMaxMp(u); u.born = -9; u.ox = -1;
    var at0 = attackTargets(u).filter(function (a) { return a.kind === 'fac' && a.c === ep.c && a.r === ep.r; }).length;
    var rc2 = unitReach(u); R.enemyFacStop = !!rc2.stop[K(ep.c, ep.r)];
    var mv2 = unitMove(u, ep.c, ep.r, rc2); R.onEnemy = [mv2.ok, u.c === ep.c && u.r === ep.r, mv2.msg || ''];
    R.adjTarget = at0;
    var fu = facUnder(u); R.under = fu ? [fu.kind, fu.d, fu.b.id === eb.id] : null;
    var at1 = attackTargets(u).filter(function (a) { return a.kind === 'fac' && a.d === 0; });
    R.underInTargets = at1.length; R.justOut = justOut(u);
    var hp0 = ep.fac.hp; u.done = false; var ar = fu ? unitAttack(u, fu) : { ok: false };
    R.hit = [ar.ok, hp0, ep.fac ? ep.fac.hp : 0];
    // 내 시설 위에서는 칠 것이 없다
    var mine = b.plots.filter(function (p) { return p.fac && !UAT[K(p.c, p.r)]; })[0]; placeUnit(u, mine.c, mine.r); R.underMine = facUnder(u) === null;
  }
  // ⑤ 밀려날 자리: 시설 칸으로도 밀려난다
  var fp = b.plots.filter(function (p) { return p.fac && !UAT[K(p.c, p.r)]; })[0];
  R.push = fp ? canPushInto(fp.c, fp.r, u) : null;
  // ⑥ 먼 길 찾기: 시설이 길을 막지 않는다 — 시설 칸이 목적지여도 길이 나온다
  var u2 = G.units.filter(function (v) { return v.f === 0 && v !== u; })[0];
  if (u2 && fp) { var pth = marchPath(u2, K(fp.c, fp.r)); R.march = pth ? pth.length : -1; }
  // ⑧ 나갈 자리를 고른다(v0.12): 새 판에서
  if (typeof deploySpots === 'function') {
    newGame(0, 1); G.aiOnly = false; var b2 = facCities(0)[0]; b2.troops = 60000; b2.food = 200000; b2.w.spear = 30000; G.factions[0].ap = 255;
    for (i = 0; i < b2.plots.length; i++) if (!b2.plots[i].fac) b2.plots[i].fac = { t: 'market', lv: 1, done: true, prog: 0, need: 0, rate: 0, hp: FAC_HP };
    var sp = deploySpots(b2), o2 = idleOfficers(b2).filter(function (o) { return !isLord(o); }), auto = deploySpot(b2);
    var want = sp.filter(function (q) { return isFac(q[0], q[1]) && !(q[0] === auto[0] && q[1] === auto[1]); })[0];      // 게임이라면 고르지 않았을 시설 칸
    var d1 = cmdDeploy(b2, { type: 'spear', ids: [o2[0].id], troops: 2000, food: 2000, at: want });
    var tr0 = b2.troops, ap0 = G.factions[0].ap, n0 = G.units.length;
    var d2 = cmdDeploy(b2, { type: 'spear', ids: [o2[1].id], troops: 2000, food: 2000, at: want });                        // 이미 부대가 선 칸
    var d3 = cmdDeploy(b2, { type: 'spear', ids: [o2[1].id], troops: 2000, food: 2000, at: [b2.c + 3, b2.r] });           // 둘레가 아닌 칸
    var d4 = cmdDeploy(b2, { type: 'spear', ids: [o2[1].id], troops: 2000, food: 2000 });                                  // 고르지 않으면 전과 같이
    R.at = { spots: sp.length, want: want, auto: auto, d1: d1.ok ? [d1.unit.c, d1.unit.r] : d1.msg, d2: [d2.ok, d2.msg || ''], d3: [d3.ok, d3.msg || ''], same: [b2.troops + 2000 === tr0, G.units.length === n0 + 1], d4: d4.ok ? [d4.unit.c, d4.unit.r] : d4.msg,
      free: [o2[1].unit === d4.unit.id] };
  }
  // ⑦ 전법 실패의 피해
  R.failDmg = TACTIC_K.failDmg; R.failCounter = TACTIC_K.failCounter;
  return R;
})())`;
const N = load(process.env.SRC || path.join(__dirname, '..', 'src'));
const r = JSON.parse(vm.runInContext(SCRIPT.replace(/facUnder\(u\)/g, '(typeof facUnder === "function" ? facUnder(u) : null)'), N));
console.log('성 둘레 ' + r.ring + '칸 가운데 시설 ' + r.ringFac + '칸 · 빈 땅 ' + r.ringFree + '칸 · 출진 ' + JSON.stringify(r.outs));
const okOuts = r.outs.filter(o => o.length === 3);
ok(r.ringFac >= 1, '시험할 도시의 둘레에 시설 칸이 있다');
ok(okOuts.length === Math.min(r.ring, r.nOfficers), '둘레가 시설로 차 있어도 둘레 칸 수만큼 출진한다: ' + okOuts.length + ' / ' + Math.min(r.ring, r.nOfficers));
ok(okOuts.slice(0, r.ringFree).every(o => o[2] === 0), '빈 땅이 먼저 쓰인다');
ok(okOuts.slice(r.ringFree).every(o => o[2] === 1) && okOuts.length > r.ringFree, '빈 땅이 다 차면 시설 칸으로 나간다');
ok(r.facStops > 0, '이동 범위에 시설 칸이 들어온다: ' + r.facStops);
ok(r.moved && r.moved[0] && r.moved[1], '내 시설 칸으로 움직인다 ' + JSON.stringify(r.moved));
ok(r.develop && r.develop[0] === false && /부대가 있는/.test(r.develop[1]), '부대가 선 부지에는 짓지 못한다 ' + JSON.stringify(r.develop));
ok(r.side && r.adjTarget === 1, '남의 시설은 옆 칸에서 칠 수 있다(전과 같다)');
ok(r.enemyFacStop && r.onEnemy[0] && r.onEnemy[1], '남의 시설 칸으로도 들어간다 ' + JSON.stringify(r.onEnemy));
ok(r.under && r.under[0] === 'fac' && r.under[1] === 0 && r.under[2], '올라선 시설이 대상으로 잡힌다 ' + JSON.stringify(r.under));
ok(r.underInTargets === 1, '칠 수 있는 것에 발밑의 시설이 들어 있다');
ok(r.hit[0] && r.hit[2] < r.hit[1], '발밑의 시설을 치면 내구가 깎인다 ' + JSON.stringify(r.hit));
ok(r.underMine === true, '내 시설 위에서는 칠 것이 없다');
ok(r.push === true, '시설 칸으로도 밀려난다');
ok(r.march > 0, '시설 칸이 목적지여도 길이 나온다: ' + r.march);
ok(r.at && r.at.spots === r.ring && r.at.want && r.at.d1[0] === r.at.want[0] && r.at.d1[1] === r.at.want[1], '고른 칸(시설 칸)으로 나간다 — 게임이 골랐을 칸은 ' + JSON.stringify(r.at.auto) + ', 고른 칸 ' + JSON.stringify(r.at.want) + ' → ' + JSON.stringify(r.at.d1));
ok(r.at.d2[0] === false && /나갈 수 없습니다/.test(r.at.d2[1]) && r.at.d3[0] === false && /나갈 수 없습니다/.test(r.at.d3[1]), '부대가 선 칸 · 둘레가 아닌 칸은 고를 수 없다 ' + JSON.stringify([r.at.d2, r.at.d3]));
ok(r.at.same[0] && r.at.same[1] && r.at.d4[0] === r.at.auto[0] && r.at.d4[1] === r.at.auto[1], '거절된 출진은 아무것도 쓰지 않고, 고르지 않으면 전과 같은 칸으로 나간다 ' + JSON.stringify(r.at.d4));
ok(r.failDmg === 0.85 && r.failCounter === 0.85, '전법 실패: 피해 0.85 · 반격 0.85 (' + r.failDmg + ' / ' + r.failCounter + ')');
if (process.env.OLD) {
  const O = load(process.env.OLD), o = JSON.parse(vm.runInContext(SCRIPT.replace(/facUnder\(u\)/g, 'null'), O));
  const oOk = o.outs.filter(x => x.length === 3).length;
  console.log('v0.11: 출진 ' + oOk + '부대(빈 땅 ' + o.ringFree + '칸) · 이동 범위의 시설 칸 ' + o.facStops + ' · 남의 시설 칸 진입 ' + o.enemyFacStop + ' · 실패 피해 ' + o.failDmg);
  ok(oOk === o.ringFree && o.facStops === 0 && o.enemyFacStop === false && o.push === false, 'v0.11 에서는 시설이 막았다(견줌)');
  ok(o.failDmg === 0.4, 'v0.11 의 실패 피해는 0.4');
}
console.log((fail ? 'FAIL ' : 'ok ') + pass + ' / ' + (pass + fail));
process.exit(fail ? 1 : 0);
