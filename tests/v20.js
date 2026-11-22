// v0.20 — 규칙 시험: 홍농(새 거점) · 옛 저장에 거점 덧붙이기 · 부대의 참모(싸움터의 조언).   OLD=build/logs/v020/src0191 node tests/v20.js
//   ① 새 판: 홍농은 49번(맨 뒤), 이각의 둘째 성, 함곡관 — 홍농 — 동관으로 이어진다. 앞선 거점의 번호 · 자리 · 부지는 0.19.1 과 같다.
//   ② 옛 저장(0.19.1 의 규칙으로 만든 판)을 열면: 거점이 50곳이 되고, 홍농의 주인은 장안을 쥔 세력(없으면 빈 성), 그 칸에 서 있던 부대는 옆으로 비킨다.
//      연 판은 저장 → 열기를 되풀이해도 같고, AI 끼리 20턴을 더 돌려도 탈이 없다.
//   ③ 참모: 부장 가운데 지력 · 통솔이 높은 사람(없으면 주장). 조언의 맞을 확률은 참모의 지력, 추천을 바르게 짚을 확률 · 예상 피해가 벌어지는 폭은 통솔(과 지력).
const fs = require('fs'), vm = require('vm'), path = require('path');
function load(root) {
  const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array };
  vm.createContext(ctx);
  for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
  return ctx;
}
function run(ctx, code) { return JSON.parse(vm.runInContext('JSON.stringify((function () {' + code + '})())', ctx)); }
const NEW = load(process.env.SRC || path.join(__dirname, '..', 'src'));
const OLD = load(process.env.OLD || path.join(__dirname, '..', 'build', 'logs', 'v020', 'src0191'));
let pass = 0, fail = 0;
function ok(c, msg) { if (c) pass++; else { fail++; console.log('  ✗ ' + msg); } }

/* ① 새 판 */
const SHAPE = `return { ver: typeof GAME_VERSION === 'string' ? GAME_VERSION : '', n: MAPDATA.bases.length, bases: MAPDATA.bases.map(function (b) { return [b.n, b.k, b.c, b.r, b.sz]; }), plots: MAPDATA.bases.map(function (b) { return JSON.stringify(MAPDATA.plots[b.n] || []); }), edges: MAPDATA.edges.length };`;
const sN = run(NEW, SHAPE), sO = run(OLD, SHAPE);
ok(/^v0\.(2\d|[3-9]\d)/.test(sN.ver), '판 번호가 v0.20 이후 [' + sN.ver + ']');
ok(sO.n === 49 && sN.n === 50 && sN.bases[49][0] === '홍농' && sN.bases[49][1] === 'city', '거점 49 → 50, 맨 뒤가 홍농: ' + JSON.stringify(sN.bases[49]));
ok(JSON.stringify(sN.bases.slice(0, 49)) === JSON.stringify(sO.bases) && JSON.stringify(sN.plots.slice(0, 49)) === JSON.stringify(sO.plots), '앞선 49곳의 이름 · 자리 · 부지는 0.19.1 과 같다');
const g1 = run(NEW, `newGame(15, 3); var b = G.bases[baseByName('홍농')], hg = G.bases[baseByName('함곡관')], dg = G.bases[baseByName('동관')];
  return { id: b.id, owner: b.owner, f: G.factions[b.owner] ? G.factions[b.owner].name : '', troops: b.troops, plots: b.plots.length, facs: b.plots.filter(function (p) { return p.fac && p.fac.done; }).map(function (p) { return p.fac.t; }),
    offs: baseOfficers(b).map(function (o) { return o.n; }).sort(), adj: ADJ[b.id].map(function (a) { return [G.bases[a.to].n, a.len]; }), hg: ADJ[hg.id].map(function (a) { return G.bases[a.to].n; }), dg: ADJ[dg.id].map(function (a) { return G.bases[a.to].n; }),
    terr: terr(b.c, b.r), road: isRoad(b.c, b.r), zone: zoneAt(b.c, b.r) === b.id, spots: deploySpots(b).length, cities: facCities(15).map(function (x) { return x.n; }), dur: [b.dur, b.maxDur], lordAt: G.bases[off(G.factions[15].lord).loc].n,
    plotOk: b.plots.every(function (p) { var t = terr(p.c, p.r); return t !== 'm' && t !== 's' && t !== 'x' && t !== 'w' && BAT[K(p.c, p.r)] === undefined && hdist(p.c, p.r, b.c, b.r) >= 2; }) };`);
console.log('① 홍농', JSON.stringify(g1));
ok(g1.id === 49 && g1.f === '이각' && g1.troops > 0 && g1.plots === 10 && g1.facs.join() === 'market,farm,barracks', '194년: 이각의 성 · 부지 10곳 · 시장 · 농장 · 병영');
ok(g1.offs.join() === '장수,장제,호거아' && g1.lordAt === '장안' && g1.cities.join() === '장안,홍농', '장제 · 장수 · 호거아가 지킨다(이각은 장안에)');
ok(JSON.stringify(g1.adj.sort()) === JSON.stringify([['동관', 10], ['함곡관', 10]]) && g1.hg.indexOf('홍농') >= 0 && g1.hg.indexOf('동관') < 0 && g1.dg.indexOf('홍농') >= 0 && g1.dg.indexOf('함곡관') < 0, '길: 함곡관 — 홍농(10) — 동관(10). 함곡관과 동관은 이제 바로 이어지지 않는다');
ok(g1.terr === 'p' && g1.zone && g1.spots >= 4 && g1.plotOk && g1.dur[0] === g1.dur[1], '성이 선 칸은 평지 · 성역이 있다 · 나갈 자리 ' + g1.spots + '곳 · 부지는 갈 수 있는 땅(성에서 2칸 밖)');
const ai1 = run(NEW, `newGame(0, 7); G.aiOnly = true; var err = '', own0 = G.bases[49].owner; try { for (var t = 0; t < 45 && !G.over; t++) endTurn(); } catch (e) { err = String(e && e.stack || e).slice(0, 300); }
  var b = G.bases[49]; return { err: err, turn: G.turn, own0: own0, owner: b.owner, troops: b.troops, units: G.units.length, bad: G.units.filter(function (u) { return BAT[K(u.c, u.r)] !== undefined; }).length };`);
ok(!ai1.err && ai1.turn > 40 && ai1.bad === 0, 'AI 끼리 45턴: 탈 없음(' + ai1.turn + '턴 · 부대 ' + ai1.units + ' · 홍농의 주인 ' + ai1.own0 + ' → ' + ai1.owner + ')' + ai1.err);

/* ② 옛 저장 */
const saves = run(OLD, `var out = [];
  newGame(0, 21); out.push(serialize());                                             // 막 시작한 판
  newGame(2, 5); G.aiOnly = true; for (var t = 0; t < 24 && !G.over; t++) endTurn(); G.aiOnly = false; out.push(serialize());      // 24턴 뒤
  newGame(15, 9); var L = G.bases[baseByName('장안')], us = idleOfficers(L); var r = cmdDeploy(L, { type: 'spear', ids: [us[1].id], troops: 2000, food: 2000 }); placeUnit(r.unit, 112, 100); out.push(serialize());      // 새 성이 설 칸에 부대가 서 있다
  newGame(0, 4); var c = G.bases[baseByName('장안')]; G.officers.forEach(function (o) { if (o.loc === c.id && o.f === c.owner && o.unit === null) { o.f = -1; o.st = 'free'; } }); c.owner = -1; c.troops = 0; out.push(serialize());      // 장안이 빈 성
  return out;`);
const M = `function shape() { return JSON.stringify(G.bases.map(function (b) { return [b.id, b.n, b.owner, b.troops, b.plots.length]; })); }
  var S = __SAVES, out = [];
  for (var i = 0; i < S.length; i++) {
    var raw = JSON.parse(S[i]), ok = deserialize(S[i]), b = G.bases[49], ca = G.bases[baseByName('장안')], x = { ok: !!ok, n: G.bases.length, rawN: raw.bases.length };
    x.same = G.bases.slice(0, 49).every(function (g, k) { var r = raw.bases[k]; return g.id === k && g.n === r.n && g.owner === r.owner && g.troops === r.troops && g.gold === r.gold; });
    x.b = b ? [b.n, b.id, b.owner, b.troops, b.plots.length, b.plots.filter(function (p) { return p.fac && p.fac.done; }).length, b.grown === undefined, b.dur === b.maxDur] : null; x.ca = ca.owner;
    x.onBase = G.units.filter(function (u) { return BAT[K(u.c, u.r)] !== undefined; }).length; x.units = G.units.length; x.rawUnits = raw.units.length;
    x.moved = raw.units.filter(function (u) { return u.c === 112 && u.r === 100; }).map(function (u) { var v = UMAP[u.id]; return v ? [v.c, v.r, hdist(v.c, v.r, 112, 100), UAT[K(v.c, v.r)] === v] : null; });
    x.log = G.log.filter(function (l) { return String(l.text || l.t || '').indexOf('홍농') >= 0; }).length;
    var s1 = serialize(); deserialize(s1); x.stable = serialize() === s1 && G.bases.length === 50;
    var err = ''; G.aiOnly = true; try { for (var t = 0; t < 20 && !G.over; t++) endTurn(); } catch (e) { err = String(e && e.stack || e).slice(0, 300); } x.err = err; x.turn = G.turn;
    out.push(x);
  }
  return out;`;
NEW.__SAVES = saves;
const mg = run(NEW, M);
mg.forEach((x, i) => console.log('② 옛 저장 ' + (i + 1), JSON.stringify(x)));
ok(mg.every(x => x.ok && x.rawN === 49 && x.n === 50 && x.same), '옛 저장 네 판: 열리고, 거점이 50곳이 되고, 앞선 49곳은 그대로');
ok(mg.every(x => x.b && x.b[0] === '홍농' && x.b[1] === 49 && x.b[4] === 10 && x.b[6] && x.b[7]), '덧붙은 거점은 홍농(49번 · 부지 10곳 · 내구 가득)');
ok(mg.slice(0, 3).every(x => x.b[2] === x.ca && x.ca >= 0 && x.b[3] === 4000 && x.b[5] === 3), '주인 = 장안을 쥔 세력 · 병력 4,000 · 시설 셋');
ok(mg[3].ca === -1 && mg[3].b[2] === -1 && mg[3].b[3] === 0 && mg[3].b[5] === 0, '장안이 빈 성이면 홍농도 빈 성(병력 0 · 시설 없음)');
ok(mg[2].moved.length === 1 && mg[2].moved[0] && mg[2].moved[0][2] === 1 && mg[2].moved[0][3] && mg.every(x => x.onBase === 0 && x.units === x.rawUnits), '새 성이 설 칸에 서 있던 부대는 옆 칸으로 비킨다(' + JSON.stringify(mg[2].moved) + ') · 부대 수는 그대로');
ok(mg.every(x => x.log >= 1), '기록에 새 성이 더해졌음을 알린다');
ok(mg.every(x => x.stable && !x.err), '연 판: 저장 → 열기가 같다 · AI 끼리 20턴을 더 돌려도 탈이 없다 ' + mg.map(x => x.err).join(''));
const bad = run(NEW, `var S = __SAVES, g = JSON.parse(S[0]); g.bases[3].n = '딴성'; var a = deserialize(JSON.stringify(g)), n1 = G.bases.length; var g2 = JSON.parse(S[0]); g2.bases.length = 40; var r2; try { r2 = baseGrow(g2); } catch (e) { r2 = 'err'; } return [n1, r2];`);
ok(bad[0] === 49 && bad[1] === 0, '다른 지도로 만든 저장(이름이 다르다 · 거점이 49곳보다 적다)에는 덧붙이지 않는다 ' + JSON.stringify(bad));

/* ③ 부대의 참모 */
const st = run(NEW, `newGame(0, 3); G.aiOnly = false; var b = facCities(0)[0], os = idleOfficers(b).filter(function (o) { return !isLord(o); });
  function by(k) { return os.slice().sort(function (x, y) { return y[k] - x[k]; }); }
  var hi = by('int')[0], lead = by('war').filter(function (o) { return o !== hi; })[0], third = os.filter(function (o) { return o !== hi && o !== lead; }).sort(function (x, y) { return x.int - y.int; })[0];
  var u1 = cmdDeploy(b, { type: 'spear', ids: [lead.id], troops: 2000, food: 2000 }).unit, s1 = uStaff(u1);
  var u2 = cmdDeploy(b, { type: 'spear', ids: [third.id, hi.id], troops: 2000, food: 2000 }).unit, s2 = uStaff(u2);
  var A = { ldr: 90, int: 90 }, B = { ldr: 60, int: 50 }, C = { ldr: 30, int: 30 }, E = { ldr: 88, int: 10 }, F = { ldr: 48, int: 99 };
  var acc = [adviceAcc(hi, 0), adviceAcc({ int: 40 }, 0), adviceAcc({ int: 60 }, 90)];
  var a1 = adviseBy(hi, 10, 0, 50, 0), a2 = adviseBy(hi, 90, 0, 50, 0), a3 = adviseBy({ int: 50, n: 'x' }, 10, 99, 50, 0), a4 = adviseBy(null, 1, 1, 50, 0), fa = facAdv(0), a5 = advise(0, 10, 0, 50, 0);
  return { lead: lead.n, s1: s1.n, hi: [hi.n, hi.int], s2: s2.n, third: third.n, read: [staffRead(A), staffRead(B), staffRead(C)], err: [staffErr(A), staffErr(E), staffErr(B), staffErr(C), staffErr(F)], acc: acc,
    says: [a1.says, a2.says, a3.says, a4, a1.adv.n === hi.n, a1.acc === acc[0]], fa: fa ? fa.n : '', a5: a5 ? a5.adv.n : '', K: STAFF };`);
console.log('③ 참모', JSON.stringify(st));
ok(st.s1 === st.lead, '부장이 없으면 주장이 스스로 헤아린다(' + st.s1 + ')');
ok(st.s2 === st.hi[0] && st.s2 !== st.third, '부장이 있으면 부장이 참모(주장 ' + st.third + ' · 부장 ' + st.s2 + ' 지력 ' + st.hi[1] + ')');
ok(st.read[0] === 100 && st.read[1] > st.read[2] && st.read[1] < 100 && st.read[2] === st.K.readMin, '추천을 바르게 짚을 확률: 통솔 · 지력 90 → 100%, 낮을수록 낮아지고 바닥은 ' + st.K.readMin + '% ' + JSON.stringify(st.read));
ok(st.err[0] === 0 && st.err[1] === 0 && st.err[2] > 0 && st.err[3] === st.K.errMax && st.err[4] === st.K.errMax, '예상 피해가 벌어지는 폭: 통솔 ' + st.K.errAt + ' 이상이면 0, 낮을수록 커지고 끝은 ±' + st.K.errMax * 100 + '% — 지력은 상관없다 ' + JSON.stringify(st.err));
ok(st.says[0] === true && st.says[1] === false && st.says[2] === false && st.says[3] === null && st.says[4] && st.says[5], '조언(adviseBy): 맞을 때는 실제대로 · 빗나갈 때는 거꾸로 · 참모가 없으면 없다 · 맞을 확률은 참모의 지력');
ok(st.acc[0] > st.acc[1] && st.acc[2] < 60, '지력이 높을수록 잘 맞히고, 상대가 더 똑똑하면 깎인다 ' + JSON.stringify(st.acc));
ok(st.fa && st.a5 === st.fa, '내정의 조언(advise)은 전처럼 군사가 한다(' + st.fa + ')');
console.log(fail ? 'FAIL ' + fail : 'PASS ' + pass);
process.exit(fail ? 1 : 0);
