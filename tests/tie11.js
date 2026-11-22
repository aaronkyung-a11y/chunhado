// v0.11 — 등용과 옛 관계(규칙 시험, 화면 없음).   node tests/tie11.js
//   OLD=<폴더> 에 v0.10.1 소스(data.js · core.js · ai.js · mapdata.js · roster.js)를 주면 '옛 관계가 없을 때는 전과 같다'도 본다.
const fs = require('fs'), vm = require('vm'), path = require('path');
function load(root) {
  const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array };
  vm.createContext(ctx);
  for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
  return ctx;
}
const NEW = load(process.env.SRC || path.join(__dirname, '..', 'src'));
let pass = 0, fail = 0;
function ok(c, msg) { if (c) pass++; else { fail++; console.log('  ✗ ' + msg); } }
function run(ctx, code) { return JSON.parse(vm.runInContext('JSON.stringify((function () {' + code + '})())', ctx)); }

/* ① 옛 관계가 없으면 전과 같다: 새 게임의 모든 (거점 · 보내는 무장 · 이웃 세력의 무장) 조합 */
const ALL = `
  newGame(0, 1); var out = [];
  G.bases.forEach(function (b) { if (b.owner < 0) return; var os = baseOfficers(b), ts = poachTargets(b);
    os.forEach(function (o) { ts.forEach(function (t) { if (typeof LIM === 'number' && (o.id >= LIM || t.id >= LIM)) return; out.push([b.id, o.id, t.id, recruitChance(b, o, t), typeof tieOf === 'function' && tieOf(o, t, b.owner) ? o.n + '→' + t.n + '(' + tieOf(o, t, b.owner).short + ')' : '']); }); }); });
  return out;`;
if (process.env.OLD) {
  const OLD = load(process.env.OLD);
  NEW.LIM = OLD.LIM = vm.runInContext('SCENARIO.officers.length', OLD);      // v0.17: 무장이 늘었다 — 옛 판에도 있던 사람들끼리만 견준다(번호는 그대로다)
  const a = run(NEW, ALL), b = run(OLD, ALL);
  let diff = 0, tied = [], tiedUp = 0;
  // v0.20: 거점이 늘었다(홍농 — 장제 · 장수 · 호거아가 옮겨 갔고 함곡관 · 동관의 이웃이 바뀌었다). 조합의 차례가 달라졌으므로 (거점 · 보내는 무장 · 대상)이 같은 것끼리 견준다
  const old = {}; b.forEach(function (x) { old[x.slice(0, 3).join('|')] = x; });
  let both = 0;
  for (let i = 0; i < a.length; i++) {
    const o = old[a[i].slice(0, 3).join('|')]; if (!o) continue;
    both++;
    if (a[i][4]) { tied.push(a[i][4] + ' ' + o[3] + '→' + a[i][3] + '%'); if (a[i][3] >= o[3]) tiedUp++; } else if (a[i][3] !== o[3]) diff++;
  }
  ok(both >= b.length * 0.8 && diff === 0, '옛 관계가 없을 때의 성공률이 v0.10.1 과 다르다: ' + diff + ' / 두 판에 다 있는 ' + both + ' (새 판 ' + a.length + ' · 옛 판 ' + b.length + ')');
  ok(tiedUp === tied.length, '사이가 있는 조합은 전보다 낮아지면 안 된다');
  console.log('① 새 게임의 이웃 등용 ' + a.length + '조합 — 사이가 없는 ' + (a.length - tied.length) + '조합은 v0.10.1 과 다른 것 ' + diff + ', 사이가 있는 ' + tied.length + '조합: ' + tied.join(' · '));
}

/* ② 멸망한 세력 출신의 포로 · 옛 주군 · 옛 신하 · 옛 동료 · 직접 인연 */
const r2 = run(NEW, `
  newGame(0, 1); G.aiOnly = false;
  var me = 0, foe = 1, cap = facCities(me)[0], fb = facBases(foe)[0], L = off(G.factions[me].lord), FL = off(G.factions[foe].lord);
  var res = { cap: cap.n, fb: fb.n, lord: FL.n };
  var men = baseOfficers(fb).map(function (o) { return o.id; });
  var r = cmdDeploy(cap, { type: 'sword', ids: [idleOfficers(cap).filter(function (o) { return !isLord(o); })[0].id], troops: 1000, food: 500 });
  captureBase(fb, r.unit);
  res.alive = G.factions[foe].alive; res.capN = fb.captives.length; res.menN = men.length;
  res.state = men.map(function (id) { var o = off(id); return [o.n, o.st, o.f, o.pf, o.capF]; });
  var sender = idleOfficers(cap).filter(function (o) { return !isLord(o) && o.sk !== '논객'; })[0];
  function oldP(o, t, capPen) { var p = 35 + (o.cha - 50) * 0.7 + (o.pol - 50) * 0.2 + (L.cha - 70) * 0.4; if (o.sk === '논객') p += 20; if (bondWith(t, me)) p += 30; if (capPen) p -= 15; return p; }
  res.sender = sender.n; res.rows = [];
  fb.captives.forEach(function (id) { var t = off(id), x = recruitTerms(fb, sender, t), raw = oldP(sender, t, true);
    res.rows.push({ n: t.n, lord: t.id === FL.id, p: x.p, old: clamp(Math.round(raw), 3, 95), exp: clamp(Math.round(t.id === FL.id ? raw : raw + 15 + TIES.fallen), 3, 95), why: x.why, fallen: fallenOf(t), org: lastF(t) }); });
  // 옛 신하가 옛 주군(포로)에게: 먼저 신하 하나를 등용한다(주사위를 0 으로)
  var realRoll = recruitRoll; recruitRoll = function () { return 0; };
  var vas = off(fb.captives.filter(function (id) { return id !== FL.id && !bondDirect(off(id), FL); })[0]);
  // 포로는 복양에 있다 — 보내는 무장도 복양에 있어야 한다(부대가 들어가 있다)
  var inFb = idleOfficers(fb); res.inFb = inFb.map(function (o) { return o.n; });
  var s2 = inFb[0] || null;
  if (!s2) { var mv = idleOfficers(cap).filter(function (o) { return !isLord(o); })[0]; mv.loc = fb.id; s2 = mv; }
  var j1 = cmdRecruit(fb, s2.id, vas.id); res.j1 = [vas.n, j1.ok, j1.joined, vas.f, vas.pf, vas.past, j1.msg || ''];
  var xv = recruitTerms(fb, vas, FL); res.vassal = { by: vas.n, p: xv.p, tie: xv.tie, why: xv.why };
  var others = fb.captives.filter(function (id) { return id !== FL.id; }).map(off);
  res.mate = others.map(function (t) { var x = recruitTerms(fb, vas, t); return { n: t.n, tie: x.tie && x.tie.k, v: x.tie && x.tie.v, p: x.p }; });
  // 옛 주군을 등용한 뒤, 옛 주군이 옛 신하들에게
  var s3 = idleOfficers(fb)[0]; if (!s3) { G.officers.forEach(function (o) { if (o.f === me && o.loc === fb.id) o.acted = false; }); s3 = idleOfficers(fb)[0]; }
  var j2 = cmdRecruit(fb, s3.id, FL.id); res.j2 = [FL.n, j2.ok, j2.joined, FL.f, FL.pf, FL.past, j2.msg || ''];
  res.byLord = fb.captives.map(off).map(function (t) { var x = recruitTerms(fb, FL, t), y = recruitTerms(fb, sender, t); return { n: t.n, tie: x.tie && x.tie.k, v: x.tie && x.tie.v, p: x.p, plain: y.p, why: x.why, exp: clamp(Math.round(oldP(FL, t, false) + TIES.fallen + (x.tie ? x.tie.v : 0)), 3, 95) }; });
  recruitRoll = realRoll;
  res.served = [vas, FL].map(function (o) { return [o.n, servedF(o), lastF(o)]; });
  return res;`);
console.log('② ' + r2.fb + ' 함락 → ' + r2.lord + '군 멸망(' + (r2.alive ? '살아 있음?!' : '멸망') + '), 포로 ' + r2.capN + ' / ' + r2.menN + '명. 보내는 무장 ' + r2.sender);
ok(!r2.alive, '세력이 멸망하지 않았다'); ok(r2.capN === r2.menN, '마지막 거점의 무장이 모두 포로가 되어야 한다');
r2.state.forEach(s => ok(s[1] === 'captive' && s[2] === -1 && s[3] === 1, '포로의 상태 · 마지막 세력: ' + s.join(',')));
r2.rows.forEach(x => {
  console.log('   ' + x.n + (x.lord ? '(옛 군주)' : '') + ': 전 ' + x.old + '% → 지금 ' + x.p + '%  ' + x.why.map(w => w[0] + ' ' + (w[1] >= 0 ? '+' : '') + w[1]).join(' · '));
  ok(x.p === x.exp, x.n + ' 성공률 ' + x.p + ' ≠ 기대 ' + x.exp);
  ok(x.lord ? !x.fallen : x.fallen, x.n + ' 멸망 출신 판정');
  if (!x.lord) ok(x.why.some(w => w[0] === '멸망한 세력 출신' && w[1] === 25), x.n + ' 까닭에 멸망한 세력 출신 +25 가 없다');
});
console.log('   등용: ' + JSON.stringify(r2.j1) + ' / ' + JSON.stringify(r2.j2));
ok(r2.j1[2] === true && r2.j1[3] === 0 && r2.j1[4] === 0 && JSON.stringify(r2.j1[5]) === '[1]', '등용한 무장의 섬겼던 세력 기록: ' + JSON.stringify(r2.j1));
ok(r2.vassal.tie && r2.vassal.tie.k === 'vassal' && r2.vassal.why.some(w => w[1] === 20), '옛 신하 → 옛 주군: ' + JSON.stringify(r2.vassal));
console.log('   옛 신하 ' + r2.vassal.by + ' → 옛 주군 ' + r2.lord + ': ' + r2.vassal.p + '% (' + r2.vassal.tie.label + ' +' + r2.vassal.tie.v + ')');
r2.mate.forEach(m => ok(m.tie === 'mate' && m.v === 12, '옛 동료: ' + JSON.stringify(m)));
console.log('   옛 동료 ' + r2.vassal.by + ' → ' + r2.mate.map(m => m.n + ' ' + m.p + '%').join(', '));
ok(r2.j2[2] === true && JSON.stringify(r2.j2[5]) === '[1]', '옛 군주 등용 기록: ' + JSON.stringify(r2.j2));
r2.byLord.forEach(m => { ok((m.tie === 'bond' && m.v === 50) || (m.tie === 'lord' && m.v === 30), '옛 주군의 설득: ' + JSON.stringify(m)); ok(m.p === m.exp, m.n + ': 옛 주군이 권할 때 ' + m.p + ' ≠ 기대 ' + m.exp); });
console.log('   옛 주군 ' + r2.lord + ' → ' + r2.byLord.map(m => m.n + ' ' + m.p + '%(' + (m.tie === 'bond' ? '인연 +50' : '옛 주군 +30') + ', 보통 무장 ' + m.plain + '%)').join(', '));

/* ③ 참수의 원한 */
const r3 = run(NEW, `
  newGame(0, 1); G.aiOnly = false;
  var me = 0, foe = 1, cap = facCities(me)[0], fb = facBases(foe)[0], FL = off(G.factions[foe].lord);
  var r = cmdDeploy(cap, { type: 'sword', ids: [idleOfficers(cap).filter(function (o) { return !isLord(o); })[0].id], troops: 1000, food: 500 });
  captureBase(fb, r.unit);
  var sender = idleOfficers(cap).filter(function (o) { return !isLord(o) && o.sk !== '논객'; })[0];
  var before = fb.captives.filter(function (id) { return id !== FL.id; }).map(function (id) { return [off(id).n, recruitChance(fb, sender, off(id)), !!(BONDS[FL.n] && BONDS[FL.n][off(id).n])]; });
  var e = cmdCaptive(fb, FL.id, 'execute');
  var after = fb.captives.map(function (id) { var x = recruitTerms(fb, sender, off(id)); return [off(id).n, x.p, x.why]; });
  // 다른 세력이 권하면 원한이 없다
  var ob = facCities(4)[0], os = baseOfficers(ob)[0], other = fb.captives.map(function (id) { return recruitTerms(ob, os, off(id)).why.some(function (w) { return /원한/.test(w[0]); }); });
  return { ok: e.ok, st: FL.st, exBy: FL.exBy, before: before, after: after, other: other };`);
ok(r3.ok && r3.st === 'dead' && r3.exBy === 0, '참수 기록(exBy): ' + JSON.stringify([r3.ok, r3.st, r3.exBy]));
r3.before.forEach((b, i) => {
  const a = r3.after[i];
  console.log('③ ' + b[0] + (b[2] ? '(인연)' : '') + ': 참수 전 ' + b[1] + '% → 뒤 ' + a[1] + '%');
  ok(a[2].some(w => /참수의 원한/.test(w[0]) && w[1] === -20), b[0] + ' 까닭에 원한이 없다');
  if (b[2]) ok(a[1] <= 3, b[0] + ' 인연이 있던 무장은 3% 이하여야 한다: ' + a[1]); else ok(a[1] === Math.max(3, b[1] - 20), b[0] + ' −20 이어야 한다: ' + b[1] + ' → ' + a[1]);
});
ok(r3.other.every(x => !x), '참수하지 않은 세력에는 원한이 없어야 한다');

/* ④ 예전에 섬긴 세력 · 다른 세력의 무장(0.6배) · 충성의 벽 · 옛 저장 */
const r4 = run(NEW, `
  newGame(0, 1); G.aiOnly = false;
  var me = 0, cap = facCities(me)[0], L = off(G.factions[me].lord), res = {};
  var A = baseOfficers(cap).filter(function (o) { return !isLord(o) && !bondOf(o); })[0], S = baseOfficers(cap).filter(function (o) { return !isLord(o) && o !== A; })[0];
  // A 가 여포군으로 넘어갔다가(1) 재야가 된다
  A.f = 1; A.loc = facBases(1)[0].id; A.loy = 80; pastSweep(); res.a1 = [A.pf, A.past];
  var poach = recruitTerms(cap, S, A), poachL = recruitTerms(cap, L, A);                 // 아직 여포군의 무장
  res.poach = { p: poach.p, why: poach.why, no: poach.no }; res.poachL = { p: poachL.p, why: poachL.why, tie: poachL.tie && poachL.tie.k };
  A.f = -1; A.st = 'free'; A.loc = cap.id; pastSweep(); res.a2 = [A.pf, A.past, servedF(A)];
  var fr = recruitTerms(cap, S, A), frL = recruitTerms(cap, L, A);
  res.free = { p: fr.p, why: fr.why, tie: fr.tie && fr.tie.k }; res.freeL = { p: frL.p, why: frL.why, tie: frL.tie && frL.tie.k };
  // 충성의 벽: 인연이 있는 사람이 가면 넘는다. 여포의 심복 고순을 유표군(14)으로 옮기고, 여포를 조조군으로 옮긴다
  var gs = null, yp = off(G.factions[1].lord); G.officers.forEach(function (o) { if (BONDS[yp.n] && BONDS[yp.n][o.n] === '심복' && !gs) gs = o; });
  gs.f = 14; gs.loc = facBases(14)[0].id; gs.loy = 97; pastSweep();
  var w1 = recruitTerms(cap, S, gs);
  G.factions[1].alive = false; yp.f = 0; yp.loc = cap.id; pastSweep();
  var w2 = recruitTerms(cap, yp, gs); gs.loy = 80; var w3 = recruitTerms(cap, yp, gs), w4 = recruitTerms(cap, S, gs);
  res.wall = { gs: gs.n, plain: [w1.p, w1.no || ''], bond97: [w2.p, w2.no || '', w2.tie && w2.tie.k], bond80: [w3.p, w3.why], plain80: [w4.p, w4.why] };
  // 옛 저장: pf · past 가 없는 저장을 불러온다
  var s = JSON.parse(serialize()); s.officers.forEach(function (o) { delete o.pf; delete o.past; delete o.exBy; });
  var ok2 = deserialize(JSON.stringify(s));
  var bad = 0; G.officers.forEach(function (o) { if (o.pf === undefined) bad++; if (o.f >= 0 && o.pf !== o.f) bad++; });
  res.old = { ok: ok2, bad: bad, A: [off(A.id).pf, off(A.id).past], gs: [off(gs.id).pf, off(gs.id).past], yp: [off(yp.id).pf, off(yp.id).past] };
  // 저장했다 다시 열어도 그대로
  var t1 = serialize(); deserialize(t1); res.stable = serialize() === t1;
  return res;`);
console.log('④ 넘어간 뒤: ' + JSON.stringify(r4.a1) + ' → 재야가 된 뒤: ' + JSON.stringify(r4.a2));
ok(r4.a1[0] === 1 && JSON.stringify(r4.a1[1]) === '[0]', '세력을 옮긴 기록: ' + JSON.stringify(r4.a1));
ok(r4.a2[0] === 1 && JSON.stringify(r4.a2[2]) === '[0,1]', '재야가 된 뒤의 섬겼던 세력: ' + JSON.stringify(r4.a2));
ok(r4.poach.why.some(w => w[0] === '예전에 섬긴 세력' && w[1] === 9), '다른 세력에 있는 옛 우리 무장: +9(15 × 0.6) — ' + JSON.stringify(r4.poach));
ok(r4.poachL.tie === 'lord' && r4.poachL.why.some(w => /옛 주군/.test(w[0]) && w[1] === 18), '군주가 직접 권하면 옛 주군 +18(30 × 0.6) — ' + JSON.stringify(r4.poachL));
ok(r4.free.why.some(w => w[0] === '예전에 섬긴 세력' && w[1] === 15) && !r4.free.why.some(w => /멸망/.test(w[0])), '재야가 된 옛 우리 무장: +15, 멸망 출신은 아님 — ' + JSON.stringify(r4.free));
ok(r4.freeL.tie === 'lord' && r4.freeL.why.some(w => w[1] === 30), '군주가 직접: 옛 주군 +30 — ' + JSON.stringify(r4.freeL));
console.log('   옛 우리 무장(다른 세력에 있음): 보통 무장 ' + r4.poach.p + '% · 군주 ' + r4.poachL.p + '%   /  재야가 된 뒤: 보통 무장 ' + r4.free.p + '% · 군주 ' + r4.freeL.p + '%');
ok(r4.wall.plain[0] === 0 && /충성/.test(r4.wall.plain[1]), '충성 97: 보통 무장은 권할 수 없다 — ' + JSON.stringify(r4.wall.plain));
ok(!r4.wall.bond97[1] && r4.wall.bond97[2] === 'bond', '충성 97: 인연이 있는 사람은 벽에 막히지 않는다 — ' + JSON.stringify(r4.wall.bond97));
ok(r4.wall.bond80[1].some(w => /심복/.test(w[0]) && w[1] === 30), '직접 인연 +30(50 × 0.6) — ' + JSON.stringify(r4.wall.bond80));
console.log('   ' + r4.wall.gs + '(유표군, 충성 97): 보통 무장 ' + r4.wall.plain[0] + '%(' + r4.wall.plain[1] + ') · 옛 주군(심복) ' + r4.wall.bond97[0] + '%   충성 80: 옛 주군 ' + r4.wall.bond80[0] + '% · 보통 무장 ' + r4.wall.plain80[0] + '%');
ok(r4.old.ok && r4.old.bad === 0, '옛 저장을 불러오면 모든 무장에 pf 가 채워져야 한다: ' + JSON.stringify(r4.old));
ok(JSON.stringify(r4.old.gs) === '[14,[1]]' && JSON.stringify(r4.old.yp) === '[0,[1]]', '옛 저장: 시나리오의 세력을 옛 세력으로 — ' + JSON.stringify(r4.old));
ok(r4.stable, '저장 → 불러오기 → 저장이 같아야 한다');
console.log('   옛 저장을 열면: ' + JSON.stringify(r4.old));
console.log((fail ? '실패 ' + fail + ' · ' : '') + '통과 ' + pass);
process.exit(fail ? 1 : 0);
