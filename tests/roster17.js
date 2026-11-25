// v0.17 — 규칙 시험: 무장 명부(425명) · 번호가 바뀌지 않음 · 새 판의 자리 · 인연 · 옛 저장에 덧붙이기.   node tests/roster17.js
//   OLD=<v0.16 의 src 폴더> 가 있으면 그 판으로 만든 저장을 불러 본다(없으면 지금 판의 저장에서 새 무장을 덜어 낸 것으로).
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.env.SRC || path.join(__dirname, '..', 'src');
function mk(dir, extra) {
  const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array };
  vm.createContext(ctx);
  for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js'].concat(extra || [])) vm.runInContext(fs.readFileSync(path.join(dir, f), 'utf8'), ctx, { filename: f });
  return ctx;
}
const ctx = mk(root);
let pass = 0, fail = 0;
function ok(c, msg) { if (c) pass++; else { fail++; console.log('  ✗ ' + msg); } }
const N_OLD = 301, H_OLD = 2229617849, N17 = 425, N_NOW = 508;      // v0.23: 명부가 508명으로 늘었다(다른 시대의 무장 83명 — tests/v23.js 가 본다). 여기서는 v0.17 에 늘어난 124명(301 ~ 424번)을 본다
// ① 명부
const R = JSON.parse(vm.runInContext(`JSON.stringify((function () {
  var S = SCENARIO, R = {}, O = S.officers, h = 0, s = O.slice(0, ${N_OLD}).map(function (o) { return o.n; }).join(',');
  for (var i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
  var names = {}, dup = [], bad = [];
  O.forEach(function (o, i) {
    if (names[o.n]) dup.push(o.n); names[o.n] = 1;
    if (baseByName(o.c) < 0) bad.push(o.n + ':도시 ' + o.c);
    ['ldr', 'war', 'int', 'pol', 'cha'].forEach(function (k) { if (!(o[k] >= 1 && o[k] <= 100)) bad.push(o.n + ':' + k); });
    if (!/^[SABC]{5}$/.test(o.apt)) bad.push(o.n + ':적성');
    if (o.sk && !SKILLS[o.sk]) bad.push(o.n + ':특기 ' + o.sk);
    if (o.f >= 0 && S.factions[o.f].cities.indexOf(o.c) < 0) bad.push(o.n + ':세력의 도시가 아님');
    if (o.f < 0 && !(o.st === 'dead' || o.st === 'free' || (o.st === 'hidden' && o.y >= 194))) bad.push(o.n + ':재야인데 연도가 없음');      // v0.23: 그 시대에 이미 죽은 사람 · 재야도 있다
    if (o.j && !S.factions.some(function (f) { return f.n === o.j || houseName(f.n) === houseName(o.j); })) bad.push(o.n + ':합류할 군주 ' + o.j);      // v0.23: 새 무장은 집안의 이름으로 적는다(손견 = 손책의 세력)
  });
  var W = S.women || [], nw = O.slice(${N_OLD}, ${N17}), wn = nw.filter(function (o) { return W.indexOf(o.n) >= 0; });
  R.n = O.length; R.hash = h; R.dup = dup; R.bad = bad; R.women = W.length; R.newN = nw.length; R.newW = wn.length; R.newActive = nw.filter(function (o) { return o.f >= 0; }).length;
  R.wPor = wn.filter(function (o) { return /^g[mcf]\\d/.test(o.por); }).map(function (o) { return o.n; });
  R.wAll = W.every(function (n) { return !!names[n]; });
  R.daqiao = O.filter(function (o) { return o.n === '대교'; })[0].por;
  R.years = nw.filter(function (o) { return o.f < 0; }).map(function (o) { return o.y; }).sort(function (a, b) { return a - b; });
  R.byYear = nw.filter(function (o) { return o.f < 0 && o.y <= 200; }).length;
  R.warW = wn.filter(function (o) { return o.war >= 70; }).map(function (o) { return o.n + o.war; });
  return R;
})())`, ctx));
ok(R.n === N_NOW && R.newN === 124 && R.newW === 38 && R.women === 42 && R.wAll, '무장 ' + R.n + '명(새로 ' + R.newN + '명 · 그 가운데 여성 ' + R.newW + '명), 여성은 모두 ' + R.women + '명');
ok(R.hash === H_OLD, '앞쪽 ' + N_OLD + '명은 이름 · 차례가 그대로다(번호가 바뀌지 않는다) ' + R.hash);
ok(R.dup.length === 0 && R.bad.length === 0, '겹치는 이름 · 틀린 값이 없다 ' + JSON.stringify(R.dup.concat(R.bad).slice(0, 5)));
ok(R.wPor.length === 0 && !/^g[mcf]\d/.test(R.daqiao), '새 여성 무장과 대교는 모두 제 초상을 쓴다 ' + JSON.stringify(R.wPor.slice(0, 5)) + ' · 대교 ' + R.daqiao);
ok(R.newActive === 22 && R.years[0] === 194 && R.years[R.years.length - 1] === 218, '194년에 이미 세력에 있는 사람 ' + R.newActive + '명, 나머지는 ' + R.years[0] + '~' + R.years[R.years.length - 1] + '년에 나온다(200년까지 ' + R.byYear + '명)');
ok(R.warW.length >= 6, '싸울 수 있는 여성 무장(무력 70 이상): ' + R.warW.join(' '));
// ② 새 판
const G1 = JSON.parse(vm.runInContext(`JSON.stringify((function () {
  var R = {}; newGame(0, 1);
  function O(n) { return G.officers.filter(function (o) { return o.n === n; })[0]; }
  R.n = G.officers.length;
  R.place = G.officers.slice(${N_OLD}).filter(function (o) { return o.f >= 0; }).every(function (o) { return G.bases[o.loc].owner === o.f && o.st === 'active' && o.loy >= 80; });
  R.lords = G.factions.map(function (f) { return off(f.lord).n; }).join(',') === SCENARIO.factions.map(function (f) { return f.n; }).join(',');
  R.bond = ['변씨', '엄씨', '감부인', '유씨', '채부인', '마운록', '오국태', '노씨'].map(function (n) { var o = O(n); return n + ':' + bondOf(o) + ':' + o.loy; });
  R.adv = G.factions.map(function (f) { return f.adv >= 0 ? off(f.adv).n : '-'; });
  var cy = G.bases[baseByName('장안')], lj = G.bases[baseByName('여강')];
  R.h194 = hiddenOfficers(cy).map(function (o) { return o.n; }); R.lj194 = hiddenOfficers(lj).map(function (o) { return o.n; });
  G.year = 199; R.lj199 = hiddenOfficers(lj).map(function (o) { return o.n; }); G.year = 194;
  R.j = ['손상향', '조진', '관은병', '장기영', '왕숙'].map(function (n) { var o = O(n); return n + '→' + o.j + '(' + o.y + ')'; });
  return R;
})())`, ctx));
ok(G1.n === N_NOW && G1.place && G1.lords, '새 판: 새 무장도 제 세력의 도시에 있고 군주는 그대로다');
ok(G1.bond.every(s => /:(부부|혈연):100$/.test(s)), '인연: ' + G1.bond.join(' '));
ok(G1.h194.indexOf('채염') >= 0 && G1.lj194.indexOf('교현') >= 0 && G1.lj194.indexOf('소교') < 0 && G1.lj199.indexOf('소교') >= 0 && G1.lj199.indexOf('손익') < 0, '재야: 194년 장안에 채염 · 여강에 교현, 소교는 199년부터(정해진 군주에게 갈 손익은 탐색에 나오지 않는다) — 199년 여강 ' + G1.lj199.join(' '));
ok(G1.j.join(' ') === '손상향→손책(203) 조진→조조(200) 관은병→유비(208) 장기영→장로(205) 왕숙→왕랑(210)', '집안사람은 해가 되면 군주에게: ' + G1.j.join(' '));
// ③ 옛 저장(301명)에 덧붙이기
let save;
if (process.env.OLD) { const old = mk(process.env.OLD); save = vm.runInContext(`(function () { newGame(0, 7); G.aiOnly = false; for (var t = 0; t < 4; t++) endTurn(); return serialize(); })()`, old); console.log('  (v0.16 판으로 만든 저장 ' + save.length + '자)'); }
else save = vm.runInContext(`(function () { newGame(0, 7); G.aiOnly = false; for (var t = 0; t < 4; t++) endTurn(); var g = JSON.parse(serialize()); g.officers.length = ${N_OLD}; g.factions.forEach(function (f) { if (f.adv >= ${N_OLD}) f.adv = -1; }); return JSON.stringify(g); })()`, ctx);
ctx.SAVE = save;
const M = JSON.parse(vm.runInContext(`JSON.stringify((function () {
  var R = {}, g0 = JSON.parse(SAVE);
  function O(n) { return G.officers.filter(function (o) { return o.n === n; })[0]; }
  R.n0 = g0.officers.length; R.ok = deserialize(SAVE) !== false; R.n = G.officers.length;
  R.ids = G.officers.every(function (o, i) { return o.id === i && o.n === SCENARIO.officers[i].n; });
  R.same = JSON.stringify(G.officers.slice(0, ${N_OLD}).map(function (o) { return [o.n, o.f, o.loc, o.st, o.loy, o.merit]; })) === JSON.stringify(g0.officers.map(function (o) { return [o.n, o.f, o.loc, o.st, o.loy, o.merit]; }));
  var nw = G.officers.slice(${N_OLD}, ${N17});
  R.act = nw.filter(function (o) { return o.f >= 0; }).length;
  R.place = nw.filter(function (o) { return o.f >= 0; }).every(function (o) { return G.bases[o.loc].owner === o.f && o.st === 'active' && o.unit === null && o.loy >= 80 && o.loy <= 100 && o.grown === undefined && o.f === SCENARIO.officers[o.id].f; });
  R.hid = nw.filter(function (o) { return o.f < 0; }).every(function (o) { return o.st === 'hidden' && o.y === (SCENARIO.officers[o.id].y || 0) && (o.j || null) === (SCENARIO.officers[o.id].j || null); });
  R.log = G.log.filter(function (x) { return /무장이 늘었습니다/.test(x.t); }).map(function (x) { return x.t + '#' + x.imp; });
  R.mine = facOfficers(G.player).filter(function (o) { return o.id >= ${N_OLD}; }).map(function (o) { return o.n + ':' + bondOf(o) + ':' + o.loy; });
  // 다시 저장했다 불러도 더 늘지 않는다
  var s2 = serialize(); deserialize(s2); R.n2 = G.officers.length; R.log2 = G.log.filter(function (x) { return /무장이 늘었습니다/.test(x.t); }).length;
  // 그대로 20턴을 더 둔다(무너지지 않는다)
  for (var t = 0; t < 20; t++) endTurn(); R.turn = G.turn; R.alive = G.factions.filter(function (f) { return f.alive; }).length;
  // 망한 세력의 사람은 그 도시의 재야로 · 본래의 도시를 잃은 세력의 사람은 군주가 있는 곳으로
  var g = JSON.parse(SAVE), fb = -1, i;
  for (i = 0; i < g.factions.length; i++) if (g.factions[i].name === '유비') fb = i;
  g.factions[fb].alive = false; g.bases.forEach(function (b) { if (b.owner === fb) b.owner = 0; }); g.officers.forEach(function (o) { if (o.f === fb) { o.f = -1; o.st = 'free'; } });
  var fy = -1; for (i = 0; i < g.factions.length; i++) if (g.factions[i].name === '원소') fy = i;
  var ye = baseByName('업'), np = baseByName('남피'); g.bases[ye].owner = 0; g.officers.forEach(function (o) { if (o.f === fy && o.loc === ye && o.unit === null) o.loc = np; });
  deserialize(JSON.stringify(g));
  var gan = O('감부인'), cy = O('최염'), ls = O('유씨');
  R.dead = [gan.f, gan.st, G.bases[gan.loc].n, hiddenOfficers(G.bases[gan.loc]).some(function (o) { return o.n === '감부인'; })];
  R.moved = [cy.f === fy, G.bases[cy.loc].n, ls.f === fy, G.bases[ls.loc].n, G.bases[off(G.factions[fy].lord).loc].n];
  // 다른 명부의 저장(이름이 어긋남)은 건드리지 않는다
  var gx = JSON.parse(SAVE); gx.officers[5].n = '다른사람'; deserialize(JSON.stringify(gx)); R.other = G.officers.length;
  return R;
})())`, ctx));
ok(M.n0 === N_OLD && M.ok && M.n === N_NOW && M.ids && M.same, '옛 저장(' + M.n0 + '명)을 불러오면 ' + M.n + '명이 된다 — 있던 사람들은 번호 · 자리 · 충성이 그대로');
ok(M.act === 22 && M.place && M.hid, '세력에 있던 ' + M.act + '명은 살아 있는 제 세력의 거점으로, 나머지는 새 판처럼 숨은 채로');
ok(M.log.length === 1 && /천하에 175명이 더해졌습니다 · 우리 세력에 4명#1$/.test(M.log[0]) && M.mine.length === 4,      // v0.23: 124 + 다른 시대의 무장 가운데 살아 있는 51명 · 조조에게는 주령이 더
   '알림 한 줄: ' + M.log[0] + ' — ' + M.mine.join(' '));
ok(M.n2 === N_NOW && M.log2 === 1, '다시 저장했다 불러도 더 늘지 않는다');
ok(M.turn >= 24 && M.alive >= 10, '불러온 판을 20턴 더 두어도 무너지지 않는다(' + M.turn + '턴 · 남은 세력 ' + M.alive + ')');
ok(M.dead[0] === -1 && M.dead[1] === 'hidden' && M.dead[2] === '소패' && M.dead[3], '망한 세력(유비)의 사람은 그 도시의 재야로 — 감부인: ' + M.dead.join(' '));
ok(M.moved[0] && M.moved[2] && M.moved[1] === M.moved[4] && M.moved[3] === M.moved[4] && M.moved[4] !== '업', '본래의 도시(업)를 잃은 세력의 사람은 군주가 있는 거점으로 — ' + M.moved[4]);
ok(M.other === N_OLD, '다른 명부로 만든 저장은 건드리지 않는다');
// ④ 초상: 명부의 초상 키가 모두 자산에 있다
if (fs.existsSync(path.join(root, 'assets.js'))) {
  const a = {}; vm.createContext(a); vm.runInContext(fs.readFileSync(path.join(root, 'assets.js'), 'utf8'), a);
  const P = vm.runInContext('Object.keys(PORTRAITS)', a), Sc = vm.runInContext('Object.keys(SCENES)', a), need = vm.runInContext('SCENARIO.officers.map(function (o) { return o.por; })', ctx);
  const miss = [...new Set(need.filter(k => P.indexOf(k) < 0))], wk = vm.runInContext(`SCENARIO.officers.filter(function (o) { return SCENARIO.women.indexOf(o.n) >= 0; }).map(function (o) { return o.por; })`, ctx);
  ok(miss.length === 0, '초상이 없는 키: ' + JSON.stringify(miss.slice(0, 8)));
  ok(wk.every(k => Sc.indexOf(k) >= 0), '여성 무장은 모두 큰 그림(장면)도 있다 ' + JSON.stringify(wk.filter(k => Sc.indexOf(k) < 0).slice(0, 5)));
}
console.log((fail ? 'FAIL ' : 'ok ') + pass + ' / ' + (pass + fail));
process.exit(fail ? 1 : 0);
