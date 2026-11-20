// v0.9.1: 창에 보여 주고 AI 가 쓰는 '기대값'(core.js 의 attackExpect · tacticExpect)이 실제 판정과 맞는가.
//   node tests/exp91.js [시행 수=12000]
// 방법: 실제 무장으로 부대를 만들어 빈 평지에 장면을 차리고(그냥 맞붙음 / 뒤가 막힘 / 뒤로 한 칸만 빔 / 옆에 다른 적 / 혼란 중 / 원거리 · 원거리+뒤에 적),
//       unitAttack0 · unitTactic0 을 시행 수만큼 되풀이해 '준 피해의 평균'(함께 맞은 적 포함)과 '받은 반격의 평균'을 기대값과 견준다.
// 기대값에 넣지 않은 것은 여기서도 뺀다: 일기토는 끈다. 맞은 뒤 줄어든 병력으로 반격이 약해지는 몫은, 맞는 쪽 병력을 2만 4천으로 두어 화력이 천장에 붙게 해서 없앤다.
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.env.SRC || path.join(__dirname, '..', 'src');
const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat };
vm.createContext(ctx);
for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
const N = +(process.argv[2] || 12000);
vm.runInContext(`
var FAILS = [], ROWS = [], CHECKS = 0;
function chk(name, cond, info) { CHECKS++; if (!cond) FAILS.push(name + ' ' + (info || '')); }
function byName(n) { for (var i = 0; i < G.officers.length; i++) if (G.officers[i].n === n) return G.officers[i]; return null; }
function freeHexes() {                     // 두 겹 둘레까지 모두 빈 평지인 자리들(서로 8칸 넘게 떨어뜨린다)
  var out = [];
  function clear(c, r) { return inMap(c, r) && terr(c, r) === 'p' && !UAT[K(c, r)] && BAT[K(c, r)] === undefined && !PAT[K(c, r)]; }
  function ring(c, r, n) { for (var a = Math.max(0, c - n - 1); a <= Math.min(W - 1, c + n + 1); a++) for (var b = Math.max(0, r - n); b <= Math.min(H - 1, r + n); b++) if (hdist(c, r, a, b) <= n && !clear(a, b)) return false; return c - n - 1 >= 0 && c + n + 1 < W && r - n >= 0 && r + n < H; }
  for (var r = 4; r < H - 4; r++) for (var c = 4; c < W - 4; c++) {
    if (!ring(c, r, 3)) continue;
    var far = true; for (var q = 0; q < out.length; q++) if (hdist(c, r, out[q][0], out[q][1]) < 9) far = false;
    if (far) out.push([c, r]);
  }
  return out;
}
function mkUnit(name, type) {
  var o = byName(name); if (!o) throw new Error('없는 무장 ' + name);
  var b = G.bases[o.loc]; if (!b || o.st !== 'active' || o.unit !== null) throw new Error('쓸 수 없는 무장 ' + name + ' ' + o.st);
  b.troops = Math.max(b.troops, 20000); b.w.spear = b.w.halberd = b.w.bow = b.w.horse = 30000; G.factions[b.owner].ap = 999; o.acted = false;
  var r = cmdDeploy(b, { type: type, ids: [o.id], troops: Math.min(3000, cmdCap(o)), food: 0 });
  if (!r.ok) throw new Error(name + ': ' + r.msg);
  return r.unit;
}
tryDuel = function () {};                    // 일기토는 기대값에 없다
var UN = {}, PARK = {}, LOT = [];          // 만든 부대는 곧바로 먼 빈터(LOT)에 세워 둔다 — 성문 앞에 두면 다음 부대가 나오지 못한다
function U(name, type) {
  if (!UN[name]) { UN[name] = mkUnit(name, type); var pk = LOT.shift(); if (!pk) throw new Error('세워 둘 자리 부족'); placeUnit(UN[name], pk[0], pk[1]); PARK[name] = pk; }
  if (UN[name].type !== type) throw new Error(name + ' 병과가 다름'); return UN[name];
}
function step(c, r, dir, n) { var d = [[1, 0], [1, -1], [0, -1], [-1, 0], [-1, 1], [0, 1]][dir]; for (var i = 0; i < n; i++) { var p = stepDir(c, r, d[0], d[1]); c = p[0]; r = p[1]; } return [c, r]; }
/* 장면: { a:[이름,병과,병력], d:[이름,병과,병력], dist: 1|2, others: [[이름,병과,[방향, 거리, 기준('a'|'d')]] …], status } — 방향 0 은 a → d 쪽 */
function stage(sp, S) {
  var a = U(S.a[0], S.a[1]), d = U(S.d[0], S.d[1]), units = [a, d], i;
  placeUnit(a, sp[0], sp[1]); a.troops = a.max = S.a[2]; a.morale = 100; a.status = null; a.stT = 0; a.done = false;
  var dp = step(sp[0], sp[1], 0, S.dist || 1); placeUnit(d, dp[0], dp[1]); d.troops = d.max = S.d[2]; d.morale = 100; d.status = S.status || null; d.stT = S.status ? 2 : 0;
  for (i = 0; i < (S.others || []).length; i++) {
    var O = S.others[i], q = U(O[0], O[1]), base = O[2][2] === 'a' ? sp : dp, qp = step(base[0], base[1], O[2][0], O[2][1]);
    if (UAT[K(qp[0], qp[1])]) throw new Error('자리가 겹침 ' + O[0]);
    placeUnit(q, qp[0], qp[1]); q.troops = q.max = 24000; q.morale = 100; q.status = null; units.push(q);
  }
  return { a: a, d: d, units: units, keep: units.map(function (u) { return [u.c, u.r, u.troops, u.morale, u.status, u.stT]; }) };
}
function reset(St) { for (var i = 0; i < St.units.length; i++) { var u = St.units[i], k = St.keep[i]; if (!UMAP[u.id]) throw new Error('부대가 사라짐'); placeUnit(u, k[0], k[1]); u.troops = k[2]; u.morale = k[3]; u.status = k[4]; u.stT = k[5]; u.done = false; } G.fires = {}; }
function park(St) { for (var i = 0; i < St.units.length; i++) { var u = St.units[i], nm = uLeader(u).n; placeUnit(u, PARK[nm][0], PARK[nm][1]); u.status = null; u.stT = 0; } }
function near(name, got, want, n, sd) {       // 기대값의 1.5% + 표본 오차 4σ + 3
  var tol = Math.abs(want) * 0.015 + 4 * sd / Math.sqrt(n) + 3;
  chk(name, Math.abs(got - want) <= tol, '기대 ' + want.toFixed(1) + ' 실제 ' + got.toFixed(1) + ' (허용 ±' + tol.toFixed(1) + ')');
}
function meanSd(xs) { var m = 0, v = 0, i; for (i = 0; i < xs.length; i++) m += xs[i]; m /= xs.length; for (i = 0; i < xs.length; i++) v += (xs[i] - m) * (xs[i] - m); return [m, Math.sqrt(v / Math.max(1, xs.length - 1))]; }
function runScene(label, sp, S, N) {
  var St = stage(sp, S), a = St.a, d = St.d, t = { kind: 'unit', u: d, c: d.c, r: d.r }, i, res, ds, cs;
  // 보통 공격
  reset(St); var NE = attackExpect(a, d);
  ds = []; cs = [];
  for (i = 0; i < N; i++) { reset(St); res = unitAttack0(a, { kind: 'unit', u: d, c: d.c, r: d.r }); if (!res.ok) throw new Error(res.msg); ds.push(res.dmg + (res.dmg2 || 0)); cs.push(res.counter || 0); }
  var md = meanSd(ds), mc = meanSd(cs);
  near(label + ' 보통 공격 피해', md[0], NE.dealt, N, md[1]); near(label + ' 보통 공격 반격', mc[0], NE.recv, N, mc[1]);
  ROWS.push(label + ' | 보통 공격: 피해 ' + md[0].toFixed(0) + ' (기대 ' + NE.dealt.toFixed(0) + ') · 반격 ' + mc[0].toFixed(0) + ' (기대 ' + NE.recv.toFixed(0) + ')');
  // 전법
  reset(St);
  var tl = tacticList(a);
  for (var ti = 0; ti < tl.length; ti++) {
    var tac = tl[ti];
    reset(St);
    if (!tacticTargets(a, tac).some(function (x) { return x.u === d; })) continue;
    var X = tacticExpect(a, d, tac), okN = 0, crN = 0;
    chk(label + ' ' + tac.name + ' 보통 공격 값이 같다', Math.abs(X.nDealt - NE.dealt) < 1e-6 && Math.abs(X.nRecv - NE.recv) < 1e-6);
    ds = []; cs = [];
    for (i = 0; i < N; i++) {
      reset(St); res = unitTactic0(a, tac, { kind: 'unit', u: d, c: d.c, r: d.r }); if (!res.ok) throw new Error(res.msg);
      var sum = res.dmg; for (var e = 0; e < res.extra.length; e++) sum += res.extra[e].dmg;
      ds.push(sum); cs.push(res.counter || 0); if (!res.fail) okN++; if (res.crit) crN++;
    }
    md = meanSd(ds); mc = meanSd(cs);
    near(label + ' ' + tac.name + ' 피해', md[0], X.dealt, N, md[1]); near(label + ' ' + tac.name + ' 반격', mc[0], X.recv, N, mc[1]);
    chk(label + ' ' + tac.name + ' 성공률', Math.abs(100 * okN / N - X.ok) < 2.5, (100 * okN / N).toFixed(1) + ' / ' + X.ok);
    ROWS.push(label + ' | ' + tac.name + ' (성공 ' + X.ok + '% 대성공 ' + X.crit + '%' + (X.others ? ', 함께 맞는 ' + X.others + '부대' : '') + '): 피해 ' + md[0].toFixed(0) + ' (기대 ' + X.dealt.toFixed(0) + ') · 반격 ' + mc[0].toFixed(0) + ' (기대 ' + X.recv.toFixed(0) + ')');
  }
  reset(St); park(St);
  return St;
}
function run(N) {
  newGame(0, 20261120); G.aiOnly = true;
  var spots = freeHexes(); if (spots.length < 2) throw new Error('빈 자리 부족 ' + spots.length);
  var sp = spots[0], D24 = 24000;
  for (var li = 1; li < spots.length && LOT.length < 40; li++) { LOT.push(spots[li]); var ln = nbrs(spots[li][0], spots[li][1]); for (var lj = 0; lj < ln.length; lj += 2) LOT.push(ln[lj]); }
  var scenes = [
    ['조운(창)→하후돈 · 맞붙음',            { a: ['조운', 'spear', 6000], d: ['하후돈', 'halberd', D24] }],
    ['조운(창)→하후돈 · 뒤가 막힘',          { a: ['조운', 'spear', 6000], d: ['하후돈', 'halberd', D24], others: [['원소', 'spear', [0, 1, 'd']]] }],
    ['조운(창)→하후돈 · 혼란 중',            { a: ['조운', 'spear', 12000], d: ['하후돈', 'halberd', D24], status: 'confuse' }],
    ['유표(극)→조인(철벽) · 약한 쪽이 침',     { a: ['유표', 'halberd', 6000], d: ['조인', 'spear', D24] }],
    ['장합(극·극장)→유비 · 옆에 적 둘',       { a: ['장합', 'halberd', 9000], d: ['유비', 'spear', D24], others: [['원술', 'spear', [1, 1, 'a']], ['한당', 'bow', [3, 1, 'a']]] }],
    ['관우(극·신장)→공손찬 · 옆에 적 하나',    { a: ['관우', 'halberd', 9000], d: ['공손찬', 'cav', D24], others: [['원술', 'spear', [5, 1, 'a']]] }],
    ['여포(기·비장)→원술 · 맞붙음',          { a: ['여포', 'cav', 8000], d: ['원술', 'spear', D24] }],
    ['여포(기)→원술 · 뒤로 한 칸만 빔',       { a: ['여포', 'cav', 8000], d: ['원술', 'spear', D24], others: [['원소', 'spear', [0, 2, 'd']]] }],
    ['여포(기)→원술 · 뒤가 막힘',            { a: ['여포', 'cav', 8000], d: ['원술', 'spear', D24], others: [['원소', 'spear', [0, 1, 'd']]] }],
    ['하후연(기·급습)→안량 · 맞붙음',         { a: ['하후연', 'cav', 6000], d: ['안량', 'spear', D24] }],
    ['조조(노)→원소 · 두 칸 밖',            { a: ['조조', 'bow', 6000], d: ['원소', 'spear', D24], dist: 2 }],
    ['조조(노)→원소 · 두 칸 밖, 뒤와 옆에 적',  { a: ['조조', 'bow', 6000], d: ['원소', 'spear', D24], dist: 2, others: [['원술', 'spear', [0, 1, 'd']], ['유비', 'spear', [2, 1, 'd']]] }],
    ['조조(노)→한당(노) · 두 칸 밖',         { a: ['조조', 'bow', 6000], d: ['한당', 'bow', D24], dist: 2 }],
    ['조조(노)→한당(노) · 맞붙음',           { a: ['조조', 'bow', 6000], d: ['한당', 'bow', D24] }],
    ['황충(노·궁신)→문추 · 두 칸 밖',         { a: ['황충', 'bow', 6000], d: ['문추', 'cav', D24], dist: 2 }]
  ];
  for (var i = 0; i < scenes.length; i++) runScene(scenes[i][0], sp, scenes[i][1], N);
  // 모양 확인(주사위 없이): 밀려난 적은 반격하지 못한다 / 뒤가 막히면 반격을 받는다 / 갈퀴·돌파는 성공하면 반격이 없다
  var St = stage(sp, { a: ['조운', 'spear', 6000], d: ['하후돈', 'halberd', D24] }), dol = TACTICS.spear[0], idan = TACTICS.spear[2];
  var x1 = tacticExpect(St.a, St.d, dol), x2 = tacticExpect(St.a, St.d, idan), p = x1.ok / 100, cf = dmgBase(St.d, St.a, 1, false) * TACTICS_FAILC();
  chk('돌출: 뒤가 비어 있으면 반격은 실패했을 때뿐', Math.abs(x1.recv - (1 - p) * cf) < 1e-6, x1.recv + ' / ' + (1 - p) * cf);
  chk('이단첨: 성공해도 보통 공격만큼 반격', Math.abs(x2.recv - (p * dmgBase(St.d, St.a, 1, false) * TACTIC_K.okCounter + (1 - p) * cf)) < 1e-6);
  chk('성공했을 때의 반격 = 보통 공격의 반격(0.55)', TACTIC_K.okCounter === 0.55);
  park(St);
  St = stage(sp, { a: ['조운', 'spear', 6000], d: ['하후돈', 'halberd', D24], others: [['원소', 'spear', [0, 1, 'd']]] });
  var x3 = tacticExpect(St.a, St.d, dol);
  chk('돌출: 뒤가 막히면 성공해도 반격을 받고 피해가 는다', x3.recv > x1.recv + 1 && x3.dealt > x1.dealt * 1.1, x3.recv.toFixed(1) + ' > ' + x1.recv.toFixed(1) + ' · ' + x3.dealt.toFixed(1) + ' > ' + x1.dealt.toFixed(1));
  park(St);
  St = stage(sp, { a: ['장합', 'halberd', 9000], d: ['유비', 'spear', D24] });
  var g = tacticExpect(St.a, St.d, TACTICS.halberd[0]), pg = g.ok / 100;
  chk('갈퀴: 반격은 실패했을 때뿐', Math.abs(g.recv - (1 - pg) * dmgBase(St.d, St.a, 1, false) * TACTIC_K.failCounter) < 1e-6);
  // 강 위에서: 내 부대가 물에 있으면 −30% 가 기대값에도 들어간다(v0.9 까지 공격 단추의 '예상'에는 빠져 있었다)
  var wh = null; for (var kk = 0; kk < NHEX && wh === null; kk++) { if (TCH[kk] !== 119) continue; var wc = kk % W, wr = (kk - wc) / W, ns = nbrs(wc, wr); for (var n = 0; n < ns.length; n++) if (inMap(ns[n][0], ns[n][1]) && terr(ns[n][0], ns[n][1]) === 'p' && !UAT[K(ns[n][0], ns[n][1])] && BAT[K(ns[n][0], ns[n][1])] === undefined && !UAT[kk]) { wh = [wc, wr, ns[n][0], ns[n][1]]; break; } }
  if (wh) {
    var A = St.a, Dd = St.d; placeUnit(A, wh[0], wh[1]); placeUnit(Dd, wh[2], wh[3]);
    var land = dmgBase(A, Dd, 1, false) / 0.7, ex = attackExpect(A, Dd), sum = 0;
    for (var q = 0; q < 4000; q++) { Dd.troops = D24; A.done = false; sum += unitAttack0(A, { kind: 'unit', u: Dd, c: Dd.c, r: Dd.r }).dmg; A.troops = 9000; }
    chk('강 위의 부대: 기대 피해에 −30% 가 들어 있다', Math.abs(ex.dealt / (land * (critNormal(A, Dd) ? 1.3 : 1)) - 0.7) < 1e-6, (ex.dealt / land).toFixed(3));
    chk('강 위의 부대: 기대 피해 = 실제 평균', Math.abs(sum / 4000 - ex.dealt) < ex.dealt * 0.015 + 3, (sum / 4000).toFixed(1) + ' / ' + ex.dealt.toFixed(1));
    chk('v0.9 의 예상(estUU)은 강 위에서 실제보다 컸다', estUU(A, Dd, 1, false) > sum / 4000 * 1.3, estUU(A, Dd, 1, false).toFixed(0) + ' vs ' + (sum / 4000).toFixed(0));
    ROWS.push('강 위의 장합 → 유비: 실제 평균 ' + (sum / 4000).toFixed(0) + ' · 기대(attackExpect) ' + ex.dealt.toFixed(0) + ' · v0.9 의 예상(estUU) ' + estUU(A, Dd, 1, false).toFixed(0));
  } else ROWS.push('강 옆 빈 평지를 찾지 못해 강 위 확인은 건너뜀');
  park(St);
  return { rows: ROWS, fails: FAILS, checks: CHECKS };
}
function TACTICS_FAILC() { return TACTIC_K.failCounter; }
`, ctx);
const out = vm.runInContext('run(' + N + ')', ctx);
out.rows.forEach(r => console.log(r));
console.log('\n시행 ' + N + '회씩 · 확인 ' + out.checks + '건 · 어긋난 것 ' + out.fails.length + '건');
out.fails.slice(0, 40).forEach(f => console.log('  ✗ ' + f));
process.exit(out.fails.length ? 1 : 0);
