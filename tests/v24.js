// v0.24 — 아이의 성비 · 딸 · 능력에 맞는 공용 초상: 규칙.   node tests/v24.js
//   A 그림 묶음(src/assets_pool.js): 120장(남 60 · 여 60), 갈래마다 14 · 14 · 12 · 10 · 10      B 명부: 옛 공용 초상(gm1 ~ 5 · gc1 ~ 5)을 쓰는 사람이 없다 — 가장 뛰어난 능력의 갈래로
//   C 성비 105 : 100 · 딸      D 초상 고르기: 갈래 · 덜 쓰인 것부터 · 죽은 사람의 그림은 다시 돈다      E 0.23 의 아이      F 딸과 후계
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.env.SRC || path.join(__dirname, '..', 'src');
const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array };
vm.createContext(ctx);
for (const f of ['mapdata.js', 'roster.js', 'data.js', 'bios.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
let pass = 0, fail = 0;
function ok(c, msg) { if (c) pass++; else { fail++; console.log('  ✗ ' + msg); } }
const J = s => JSON.parse(vm.runInContext('JSON.stringify(' + s + ')', ctx));
const POOL = J('POOL'), BIRTH = J('BIRTH');

console.log('A 그림 묶음');
const want = []; for (const s of ['gm', 'gf']) POOL.n.forEach((n, c) => { for (let j = 1; j <= n; j++) want.push(s + (c + 1) + String(j).padStart(2, '0')); });
ok(POOL.n.join() === '14,14,12,10,10' && POOL.key.join() === 'war,ldr,int,pol,cha' && want.length === 120, '공용 초상 120장: 갈래(무력 · 통솔 · 지력 · 정치 · 매력)마다 14 · 14 · 12 · 10 · 10 × 남녀');
const pf = path.join(root, 'assets_pool.js');
if (fs.existsSync(pf)) {
  const t = fs.readFileSync(pf, 'utf8'), P = JSON.parse(t.slice(t.indexOf('{'), t.lastIndexOf('}') + 1));
  const pk = Object.keys(P.por).sort(), sk = Object.keys(P.scn).sort();
  ok(pk.join() === want.slice().sort().join() && sk.join() === pk.join(), '묶음에 흉상 ' + pk.length + '장 · 장면 ' + sk.length + '장 — 열쇠가 표와 같다');
  ok(pk.every(k => P.por[k].startsWith('UklGR') && P.por[k].length > 8000 && P.scn[k].startsWith('UklGR') && P.scn[k].length > 15000), '모두 WebP 그림이다(흉상 평균 ' + Math.round(pk.reduce((a, k) => a + P.por[k].length, 0) / pk.length / 1024) + 'KB · 장면 평균 ' + Math.round(pk.reduce((a, k) => a + P.scn[k].length, 0) / pk.length / 1024) + 'KB)');
} else ok(false, 'src/assets_pool.js 가 없다');

console.log('B 명부');
const b = J(`(function () {
  var O = SCENARIO.officers, old = O.filter(function (o) { return /^g[mc][0-9]$/.test(o.por); }).length, pool = O.filter(function (o) { return /^g[mf][1-5][0-9][0-9]$/.test(o.por); }), bad = [], use = {}, cat = [0, 0, 0, 0, 0];
  pool.forEach(function (o) { var c = porCat(o); cat[c]++; if (o.por.slice(0, 3) !== 'gm' + (c + 1) || SCENARIO.women.indexOf(o.n) >= 0 || +o.por.slice(3) > POOL.n[c]) bad.push(o.n + ':' + o.por); use[o.por] = (use[o.por] || 0) + 1; });
  var spread = POOL.n.map(function (n, c) { var v = []; for (var j = 1; j <= n; j++) v.push(use['gm' + (c + 1) + (j < 10 ? '0' : '') + j] || 0); return Math.max.apply(null, v) - Math.min.apply(null, v); });
  return { old: old, pool: pool.length, bad: bad, cat: cat, spread: spread, n: O.length, ex: ['동탁', '사마사', '주령'].map(function (n) { var o = O.filter(function (x) { return x.n === n; })[0]; return n + ':' + o.por + ':' + POOL.name[porCat(o)]; }) };
})()`);
console.log('   공용 초상을 쓰는 사람 ' + b.pool + '명 — 갈래마다 ' + POOL.name.map((n, i) => n + ' ' + b.cat[i]).join(' · ') + ' · 예: ' + b.ex.join(' '));
ok(b.old === 0 && b.pool === 253 && b.bad.length === 0, '옛 공용 초상 열 장을 쓰는 사람이 없고, 253명이 가장 뛰어난 능력의 갈래에서 고른 공용 초상을 쓴다 ' + b.bad.slice(0, 4).join(' '));
ok(b.spread.every(x => x <= 1), '갈래 안에서는 고루 돌려 쓴다(가장 많이 쓰인 그림과 적게 쓰인 그림의 차이 ' + b.spread.join(' · ') + ')');

console.log('C 성비 · 딸');
const c = J(`(function () {
  function run(boy, girl, years) { newGame(0, 41, '194'); G.aiOnly = true; BIRTH.p = 100; BIRTH.lord = 100; BIRTH.kids = 9; var b0 = BIRTH.boy, g0 = BIRTH.girl; BIRTH.boy = boy; BIRTH.girl = girl;
    var n0 = G.officers.length; for (var y = 0; y < years; y++) { G.year = 195 + y; birthTick(); } BIRTH.boy = b0; BIRTH.girl = g0; return G.officers.slice(n0); }
  var out = {}, k = run(105, 100, 4), g = k.filter(function (x) { return x.sex === 'f'; }), m = k.filter(function (x) { return x.sex !== 'f'; });
  out.n = k.length; out.boys = m.length; out.girls = g.length;
  out.badG = g.filter(function (x) { var f = offByName(x.dad), nm = x.n.slice(surnameOf(f.n).length); return !(isWoman(x) && /^gf[1-5][0-9][0-9]$/.test(x.por) && x.n.indexOf(surnameOf(f.n)) === 0 && (GIRL_NAMES.indexOf(nm) >= 0 || nm.length === 2) && /의 딸\\. /.test(bioOf(x)) && !isWoman(f)); }).map(function (x) { return x.n; });
  out.badM = m.filter(function (x) { var f = offByName(x.dad), nm = x.n.slice(surnameOf(f.n).length); return !(!isWoman(x) && /^gm[1-5][0-9][0-9]$/.test(x.por) && (KID_NAMES.indexOf(nm) >= 0 || nm.length === 2) && /의 아들\\. /.test(bioOf(x))); }).map(function (x) { return x.n; });
  var names = {}; G.officers.forEach(function (o) { names[o.n] = (names[o.n] || 0) + 1; }); out.dup = Object.keys(names).filter(function (n) { return names[n] > 1; });
  out.ex = g.slice(0, 5).map(function (x) { return x.dad + '→' + x.n; });
  out.allBoys = run(100, 0, 1).every(function (x) { return x.sex !== 'f'; }); out.allGirls = run(0, 100, 1).every(function (x) { return x.sex === 'f'; });
  BIRTH.p = ${BIRTH.p}; BIRTH.lord = ${BIRTH.lord}; BIRTH.kids = ${BIRTH.kids};
  return out;
})()`);
const share = c.boys / c.n;
console.log('   아이 ' + c.n + '명: 아들 ' + c.boys + ' · 딸 ' + c.girls + ' (아들 ' + (share * 100).toFixed(1) + '% — 105 : 100 이면 51.2%) · 딸의 이름: ' + c.ex.join(' '));
ok(BIRTH.boy === 105 && BIRTH.girl === 100 && c.n > 500 && Math.abs(share - 105 / 205) < 0.045, '성비: 아들 105 : 딸 100 (잰 것 ' + c.boys + ' : ' + c.girls + ')');
ok(c.badG.length === 0 && c.badM.length === 0 && c.dup.length === 0, '딸은 여성(아버지의 성 + 딸의 이름 · 여성 공용 초상 · 열전에 "딸"), 아들은 남성 공용 초상 — 이름이 겹치지 않는다 ' + c.badG.concat(c.badM, c.dup).slice(0, 5).join(' '));
ok(c.allBoys && c.allGirls, 'BIRTH.boy : BIRTH.girl 을 100 : 0 · 0 : 100 으로 두면 아들만 · 딸만 태어난다');

console.log('D 초상 고르기');
const d = J(`(function () {
  newGame(0, 43, '194'); G.aiOnly = true; var out = {}, id = G.officers.length;
  function kid(n, sex, st) { var k = { id: G.officers.length, n: n, ldr: st[1], war: st[0], int: st[2], pol: st[3], cha: st[4], apt: 'BBBBB', sk: '', por: '', f: -1, st: 'hidden', loc: 0, unit: null, by: 195, dy: 260, dm: 6, kid: 1, y: 210 }; if (sex === 'f') k.sex = 'f'; k.por = poolPick(k); G.officers.push(k); return k; }
  // 갈래: 가장 뛰어난 능력
  out.cat = [['a무', 'f', [90, 50, 50, 50, 50]], ['a통', 'f', [50, 90, 50, 50, 50]], ['a지', 'f', [50, 50, 90, 50, 50]], ['a정', 'f', [50, 50, 50, 90, 50]], ['a매', 'f', [50, 50, 50, 50, 90]], ['a같', 'f', [80, 80, 80, 80, 80]], ['b무', 'm', [90, 50, 50, 50, 50]], ['b매', 'm', [50, 50, 50, 50, 90]]].map(function (x) { return kid(x[0], x[1], x[2]).por.slice(0, 3); });
  // 덜 쓰인 것부터: 무력이 으뜸이고 지력이 버금인 딸 30명 — 처음 14명은 무력 갈래의 서로 다른 그림, 그다음은 지력 갈래의 남은 그림, 그 뒤에야 겹친다
  newGame(0, 43, '194'); G.aiOnly = true; id = G.officers.length;
  var ks = []; for (var i = 0; i < 30; i++) ks.push(kid('c' + i, 'f', [90, 40, 70, 40, 40]).por);
  var first = ks.slice(0, 14), uniq = {}; ks.forEach(function (p) { uniq[p] = (uniq[p] || 0) + 1; });
  out.first = first.every(function (p) { return p.slice(0, 3) === 'gf1'; }) && Object.keys(uniq).length; out.mid = ks.slice(14, 26).every(function (p) { return p.slice(0, 3) === 'gf3'; }) && ks.slice(26).every(function (p) { return p.slice(0, 3) === 'gf1'; });
  out.max = Math.max.apply(null, Object.keys(uniq).map(function (p) { return uniq[p]; })); out.n1 = Object.keys(uniq).filter(function (p) { return p.slice(0, 3) === 'gf1'; }).length; out.n3 = Object.keys(uniq).filter(function (p) { return p.slice(0, 3) === 'gf3'; }).length;
  // 죽은 사람의 그림은 다시 돈다
  var dead = G.officers.filter(function (o) { return o.n === 'c3'; })[0]; dead.st = 'dead'; var used = dead.por, cnt = G.officers.filter(function (o) { return o.por === used && o.st !== 'dead'; }).length;
  out.recycle = [cnt, kid('d0', 'f', [90, 40, 70, 40, 40]).por === used || cnt > 0];
  out.same = poolPick(G.officers[id]) === poolPick(G.officers[id]);
  return out;
})()`);
ok(d.cat.join() === 'gf1,gf2,gf3,gf4,gf5,gf1,gm1,gm5', '갈래: 무력 → 1 · 통솔 → 2 · 지력 → 3 · 정치 → 4 · 매력 → 5(같으면 앞의 것), 딸은 gf · 아들은 gm');
ok(d.first && d.mid && d.n1 === 14 && d.n3 === 12, '덜 쓰인 것부터: 같은 갈래의 딸 30명 — 제 갈래의 14장을 다 쓰고, 버금 능력의 갈래 12장을 쓴 뒤에야 겹친다(가장 많이 쓰인 그림 ' + d.max + '번)');
ok(d.recycle[1] && d.same, '세상을 떠난 사람이 쓰던 그림은 다시 돈다 · 같은 사람에게는 늘 같은 답(판의 난수를 쓰지 않는다)');

console.log('E 0.23 의 아이 · F 딸과 후계');
const e = J(`(function () {
  var out = {};
  newGame(0, 45, '194'); G.aiOnly = true; BIRTH.p = 100; BIRTH.lord = 100; G.year = 195; var n0 = G.officers.length; birthTick(); BIRTH.p = ${BIRTH.p}; BIRTH.lord = ${BIRTH.lord};
  var kids = G.officers.slice(n0); kids.forEach(function (k, i) { k.por = (i % 2 ? 'gm' : 'gc') + (1 + i % 5); delete k.sex; });      // 0.23 의 아이: 옛 공용 초상 · 아들뿐
  var g = JSON.parse(serialize()); deserialize(JSON.stringify(g));
  var k2 = G.officers.slice(n0); out.fixed = k2.every(function (k) { return /^gm[1-5][0-9][0-9]$/.test(k.por); }); out.n = k2.length;
  // 군주의 딸: 남자 혈연이 없으면 뒤를 잇는다(혈연이 아닌 남자보다 앞)
  newGame(0, 45, '194'); G.aiOnly = true; var f = offByName('도겸').f, L = offByName('도겸');
  var dg = { id: G.officers.length, n: '도연', ldr: 60, war: 50, int: 70, pol: 70, cha: 75, apt: 'BBBBB', sk: '', por: 'gf301', f: f, st: 'active', loc: L.loc, unit: null, loy: 100, merit: 0, acted: false, y: 0, j: null, capF: -1, dest: -1, eta: 0, pf: f, by: 176, dy: 240, dm: 5, dad: '도겸', kid: 1, sex: 'f' };
  G.officers.push(dg); out.bond = bondOf(dg); out.cls = heirClass(dg, L, G.factions[f]); out.rank0 = heirRank(f)[0].n; L.dy = G.year; L.dm = G.month; lifeTick(); out.name = G.factions[f].name; out.isLord = isLord(dg);
  return out;
})()`);
ok(e.fixed && e.n > 100, '0.23 에서 태어난 아이(옛 공용 초상)는 저장을 열 때 새 공용 초상으로 바뀐다(' + e.n + '명)');
ok(e.bond === '혈연' && e.cls === 4 && e.rank0 === '도연' && e.name === '도연' && e.isLord, '군주의 딸은 혈연 — 남자 혈연이 없으면 뒤를 잇는다(도겸 → 딸 도연)');
console.log('\nv24: ' + pass + ' pass, ' + fail + ' fail');
process.exit(fail ? 1 : 0);
