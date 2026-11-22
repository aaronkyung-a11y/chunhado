// 전법 규칙 확인
//  v0.7: 성공·대성공 확률이 표시값과 같은가, 대성공 때 효과가 세지는가, 혼란이 상대 능력치에 따르는가
//  v0.8: 성공률이 상대 통솔·양쪽 병력·상대 적성·지형·혼란을 보는가, 피해에 병력 비가 들어가는가, 성공/실패 때의 반격 크기, 특기는 '성공하면 대성공'인가
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = path.join(__dirname, '..', 'src');
const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat };
vm.createContext(ctx);
for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
const N = +(process.argv[2] || 4000);
vm.runInContext(`
var FAILS = [];
function chk(name, cond, info) { if (!cond) FAILS.push(name + ' ' + (info || '')); }
function byName(n) { for (var i = 0; i < G.officers.length; i++) if (G.officers[i].n === n) return G.officers[i]; return null; }
function freeHexes() {                     // 주위 여섯 칸까지 모두 빈 평지인 자리들
  var out = [];
  function clear(c, r) { return inMap(c, r) && terr(c, r) === 'p' && !UAT[K(c, r)] && BAT[K(c, r)] === undefined && !PAT[K(c, r)]; }
  for (var r = 2; r < H - 2; r++) for (var c = 2; c < W - 2; c++) {
    if (!clear(c, r)) continue;
    var ns = nbrs(c, r), ok = 0, far = true;
    for (var i = 0; i < ns.length; i++) { if (clear(ns[i][0], ns[i][1])) { var n2 = nbrs(ns[i][0], ns[i][1]), o2 = 0; for (var j = 0; j < n2.length; j++) if (clear(n2[j][0], n2[j][1])) o2++; if (o2 === 6) ok++; } }
    for (var q = 0; q < out.length; q++) if (hdist(c, r, out[q][0], out[q][1]) < 6) far = false;
    if (ok === 6 && far) out.push([c, r]);
  }
  return out;
}
function mkUnit(name, type, troops) {
  var o = byName(name); if (!o) throw new Error('없는 무장 ' + name);
  var b = G.bases[o.loc]; if (!b || o.st !== 'active' || o.unit !== null) throw new Error('쓸 수 없는 무장 ' + name + ' ' + o.st);
  b.troops = Math.max(b.troops, 20000); b.w.spear = b.w.halberd = b.w.bow = b.w.horse = 30000; G.factions[b.owner].ap = 999; o.acted = false;
  var r = cmdDeploy(b, { type: type, ids: [o.id], troops: Math.min(troops, cmdCap(o)), food: 0 });
  if (!r.ok) throw new Error(name + ': ' + r.msg);
  return r.unit;
}
/* 한 번의 전법을 n 번 되풀이(상태는 매번 되돌린다) */
function trial(a, d, tac, n) {
  var out = { n: n, cOk: 0, nCOk: 0, cFail: 0, nCFail: 0, fail: 0, ok: 0, crit: 0, conf: 0, confOk: 0, confCrit: 0, mor: {}, push: {}, dmgOk: 0, dmgCrit: 0, dmgFail: 0, fireT: {}, pOk: 0, pCrit: 0, pConf: {} };
  var a0 = [a.c, a.r], d0 = [d.c, d.r], aT = a.troops, dT = d.troops, aM = a.morale, dM = d.morale;
  for (var i = 0; i < n; i++) {
    if (!UMAP[a.id] || !UMAP[d.id]) throw new Error('부대가 사라짐');
    placeUnit(a, a0[0], a0[1]); placeUnit(d, d0[0], d0[1]);
    a.troops = aT; d.troops = dT; a.morale = aM; d.morale = dM; a.done = false; d.done = false; a.status = d.status = null; a.stT = d.stT = 0; G.fires = {};
    var res = unitTactic0(a, tac, { kind: 'unit', u: d, c: d.c, r: d.r });
    if (!res.ok) throw new Error(res.msg);
    out.pOk = res.pOk; out.pCrit = res.pCrit;
    if (res.counter !== undefined) { if (res.fail) { out.cFail += res.counter; out.nCFail++; } else { out.cOk += res.counter; out.nCOk++; } }
    if (res.fail) { out.fail++; out.dmgFail += res.dmg; chk(tac.name + ' 실패 때 효과 없음', !res.confused && !res.mor && !res.pushed && !res.fire && d.morale === dM); continue; }
    if (res.crit) { out.crit++; out.dmgCrit += res.dmg; } else { out.ok++; out.dmgOk += res.dmg; }
    if (res.confused) { out.conf++; if (res.crit) out.confCrit++; else out.confOk++; }
    var key = res.crit ? 'crit' : 'ok';
    if (res.pConf !== undefined) out.pConf[key] = res.pConf;
    out.mor[key + ':' + (res.mor || 0)] = (out.mor[key + ':' + (res.mor || 0)] || 0) + 1;
    out.push[key + ':' + (res.pushed || 0) + (res.slam ? 's' : '')] = (out.push[key + ':' + (res.pushed || 0) + (res.slam ? 's' : '')] || 0) + 1;
    if (res.fire) { var ft = G.fires[K(d0[0], d0[1])]; out.fireT[key + ':' + ft] = (out.fireT[key + ':' + ft] || 0) + 1; }
    if (!res.duel) chk(tac.name + ' 기력 깎임 실제와 같음', dM - d.morale === (res.mor || 0) + (uHas(a, '위풍') ? Math.min(10, dM - (res.mor || 0)) : 0), dM + '→' + d.morale + ' mor ' + res.mor);
    else out.duel = (out.duel || 0) + 1;
  }
  placeUnit(a, a0[0], a0[1]); placeUnit(d, d0[0], d0[1]); a.troops = aT; d.troops = dT; a.morale = aM; d.morale = dM; a.done = d.done = false; a.status = d.status = null; G.fires = {};
  return out;
}
function pct(x, n) { return (100 * x / n).toFixed(1); }
function near(name, got, want, n) {          // 이항분포 4σ 안인가
  var p = want / 100, sd = Math.sqrt(Math.max(1e-9, p * (1 - p) / n)) * 100, tol = Math.max(0.01, 4 * sd);
  chk(name, Math.abs(got - want) <= tol, '기대 ' + want + '% 실제 ' + got.toFixed(2) + '% (허용 ±' + tol.toFixed(2) + ')');
}
function run(N) {
  newGame(0, 20261120); G.aiOnly = true;
  var rows = [];
  // [공격 무장, 병과, 방어 무장, 병과]
  var cases = [['조운', 'spear', '하후돈', 'halberd'], ['여포', 'cav', '유비', 'spear'], ['장비', 'spear', '조조', 'cav'], ['유비', 'spear', '여포', 'cav'], ['황충', 'bow', '원술', 'spear'], ['관우', 'halberd', '원소', 'spear'], ['도겸', 'spear', '조조', 'cav'], ['순욱', 'spear', '여포', 'cav']];
  var made = {};
  function unitOf(name, type) { var k = name; if (made[k] && made[k].type === type && UMAP[made[k].id]) return made[k]; if (made[k]) { throw new Error(name + ' 는 이미 다른 병과로 나가 있음'); } made[k] = mkUnit(name, type, 6000); return made[k]; }
  var spots = freeHexes(); if (spots.length < cases.length) throw new Error('빈 자리 부족 ' + spots.length);
  for (var ci = 0; ci < cases.length; ci++) {
    var cs = cases[ci], a, d;
    try { a = unitOf(cs[0], cs[1]); d = unitOf(cs[2], cs[3]); } catch (e) { rows.push('건너뜀: ' + cs.join(' ') + ' — ' + e.message); continue; }
    var sp = spots[ci];
    var keepA = [a.c, a.r], keepD = [d.c, d.r];
    placeUnit(a, sp[0], sp[1]);
    var ns = nbrs(sp[0], sp[1]), dn = ns[0]; placeUnit(d, dn[0], dn[1]);
    a.troops = a.max = 6000; d.troops = d.max = 20000; a.morale = 100; d.morale = 100;
    var tl = TACTICS[a.type], od = tacticOdds(a, d);
    for (var ti = 0; ti < tl.length; ti++) {
      var tac = tl[ti];
      if (APT_RANK[uApt(a)] < APT_RANK[tac.need]) continue;
      var o = trial(a, d, tac, N), nOk = o.ok + o.crit;
      near(cs[0] + '→' + cs[2] + ' ' + tac.name + ' 성공률', 100 * nOk / N, od.ok, N);
      near(cs[0] + '→' + cs[2] + ' ' + tac.name + ' 대성공률', 100 * o.crit / N, od.crit, N);
      chk(tac.name + ' 표시 확률 = 판정 확률', o.pOk === od.ok && o.pCrit === od.crit);
      var e0 = tac, e1 = tacticEff(tac, true);
      if (tac.confuse) {
        var c0 = confuseOdds(e0, d), c1 = confuseOdds(e1, d);
        if (o.ok > 200) near(tac.name + ' 혼란(성공)', 100 * o.confOk / o.ok, c0, o.ok);
        if (o.crit > 200) near(tac.name + ' 혼란(대성공)', 100 * o.confCrit / o.crit, c1, o.crit);
      }
      var dOk = o.ok ? o.dmgOk / o.ok : 0, dCr = o.crit ? o.dmgCrit / o.crit : 0, dFl = o.fail ? o.dmgFail / o.fail : 0;
      if (o.ok > 100 && o.crit > 100 && !tac.push) chk(tac.name + ' 대성공 피해 = 성공의 ' + od.mult + '배쯤', Math.abs(dCr / dOk - od.mult) < 0.06, (dCr / dOk).toFixed(3));
      rows.push([cs[0] + '(' + UNIT_TYPES[a.type].name + ' ' + uApt(a) + ', 무' + uWar(a) + ')', '→ ' + cs[2] + '(통' + uLdr(d) + ' 지' + uInt(d) + ')', tac.name,
        '표시 ' + od.ok + '/' + od.crit + (od.sure ? ' 확정' : ''), '실제 성공 ' + pct(nOk, N) + ' 대성공 ' + pct(o.crit, N) + ' 실패 ' + pct(o.fail, N),
        '피해 실패 ' + Math.round(dFl) + ' 성공 ' + Math.round(dOk) + ' 대성공 ' + Math.round(dCr),
        (tac.confuse ? '혼란 표시 ' + confuseOdds(e0, d) + '/' + confuseOdds(e1, d) + ' 실제 ' + (o.ok ? pct(o.confOk, o.ok) : '-') + '/' + (o.crit ? pct(o.confCrit, o.crit) : '-') : ''),
        'mor ' + JSON.stringify(o.mor), 'push ' + JSON.stringify(o.push), (tac.fire ? 'fire ' + JSON.stringify(o.fireT) : '')].join(' | '));
      // 효과 단계 확인
      var k;
      if (tac.moraleDmg || (tac.great && tac.great.moraleDmg)) {
        for (k in o.mor) { var pr = k.split(':'), want = pr[0] === 'crit' ? (e1.moraleDmg || 0) : (e0.moraleDmg || 0); chk(tac.name + ' 기력 ' + k, +pr[1] === want, '기대 ' + want); }
      }
      if (tac.push) for (k in o.push) { var p2 = k.split(':'), wantP = p2[0] === 'crit' ? e1.push : e0.push, gotP = parseInt(p2[1], 10); chk(tac.name + ' 밀어냄 ' + k, gotP === wantP || /s$/.test(p2[1]), '기대 ' + wantP); }
      if (tac.fire) for (k in o.fireT) { var p3 = k.split(':'); chk(tac.name + ' 불 ' + k, +p3[1] === (p3[0] === 'crit' ? 3 : 2)); }
    }
    placeUnit(a, keepA[0], keepA[1]); placeUnit(d, keepD[0], keepD[1]);
  }
  // ---------- v0.8 ----------
  var A = made['조운'], D = made['하후돈'], sp8 = spots[spots.length - 1], nb8 = nbrs(sp8[0], sp8[1])[0];
  var kA = [A.c, A.r], kD = [D.c, D.r];
  placeUnit(A, sp8[0], sp8[1]); placeUnit(D, nb8[0], nb8[1]); A.morale = D.morale = 100;
  function oddsWith(at, dt, st) { A.troops = at; D.troops = dt; D.status = st || null; var o = tacticOdds(A, D); D.status = null; return o; }
  function sumP(o) { var P = o.parts; return P.apt + P.stat + P.troops + P.dapt + P.terr + P.conf + P.skill; }
  var o11 = oddsWith(6000, 6000), o12 = oddsWith(3000, 6000), o14 = oddsWith(1500, 6000), o18 = oddsWith(700, 6000), o21 = oddsWith(12000, 6000), o41 = oddsWith(24000, 6000), oc = oddsWith(6000, 6000, 'confuse');
  chk('병력이 같으면 0', o11.parts.troops === 0, o11.parts.troops); chk('절반이면 -8', o12.parts.troops === -8, o12.parts.troops); chk('4분의 1이면 -16', o14.parts.troops === -16, o14.parts.troops);
  chk('더 적어도 -16', o18.parts.troops === -16, o18.parts.troops); chk('두 배면 +8', o21.parts.troops === 8, o21.parts.troops); chk('네 배여도 +8', o41.parts.troops === 8, o41.parts.troops);
  [o11, o12, o14, o18, o21, o41, oc].forEach(function (o, i) { chk('성공률 = 조각의 합(10~95) #' + i, o.ok === Math.round(clamp(sumP(o), 10, 95)), o.ok + ' / ' + sumP(o)); });
  chk('혼란 중인 상대 +10', oc.parts.conf === 10 && o11.parts.conf === 0);
  chk('병력이 적을수록 성공률이 낮다', o14.ok < o12.ok && o12.ok < o11.ok && o11.ok < o21.ok, [o14.ok, o12.ok, o11.ok, o21.ok].join(' < '));
  rows.push('v0.8 조운 6천 → 하후돈: 병력 ' + [700, 1500, 3000, 6000, 12000, 24000].map(function (t, i) { return t + '명 ' + [o18, o14, o12, o11, o21, o41][i].ok + '%'; }).join(' · ') + ' (조운 쪽 병력을 바꿔 가며)');
  // 상대 통솔: 방어 주장만 바꿔 본다(검병 = 적성 B 고정). 통솔이 높을수록 무장 항이 낮아야 한다
  var sample = G.officers.filter(function (o) { return o.st === 'active' && o.f >= 0; }).sort(function (a, b) { return a.ldr - b.ldr; }), prev = 99, lo = 99, hi = -99, mono = true;
  sample.forEach(function (o) { var pd = { id: -5, f: o.f, c: D.c, r: D.r, type: 'sword', off: [o.id], troops: 6000, max: 6000, morale: 100, status: null }; A.troops = 6000; var st = tacticOdds(A, pd).parts.stat; if (st > prev) mono = false; prev = st; lo = Math.min(lo, st); hi = Math.max(hi, st); });
  chk('상대 통솔이 높을수록 무장 항이 낮다(무장 ' + sample.length + '명)', mono && hi > lo + 10, lo + '~' + hi);
  rows.push('v0.8 조운 → 방어 주장 ' + sample.length + '명(통솔 ' + sample[0].ldr + '~' + sample[sample.length - 1].ldr + '): 무장 항 ' + hi + ' ~ ' + lo);
  // 상대 적성
  var want = { C: 3, B: 0, A: -3, S: -6 }, seenA = {};
  G.officers.forEach(function (o) { var ap = o.apt.charAt(APT_IDX.spear); if (seenA[ap] || o.st !== 'active' || o.f < 0) return; seenA[ap] = 1;
    var pd = { id: -6, f: o.f, c: D.c, r: D.r, type: 'spear', off: [o.id], troops: 6000, max: 6000, morale: 100, status: null }; chk('상대 창병 적성 ' + ap, tacticOdds(A, pd).parts.dapt === want[ap], tacticOdds(A, pd).parts.dapt); });
  chk('적성 네 등급을 모두 봄', Object.keys(seenA).length === 4, Object.keys(seenA).join(''));
  // 지형
  var fh = null, wh = null; for (var kk = 0; kk < NHEX && (!fh || !wh); kk++) { var tc = TCH[kk]; if (!fh && tc === 102) fh = kk; if (!wh && tc === 119) wh = kk; }
  [[fh, -5, '숲'], [wh, 5, '강']].forEach(function (q) { var pd = { id: -7, f: D.f, c: q[0] % W, r: (q[0] - q[0] % W) / W, type: 'spear', off: D.off, troops: 6000, max: 6000, morale: 100, status: null }; chk('상대가 ' + q[2] + '에 서 있으면 ' + q[1], tacticOdds(A, pd).parts.terr === q[1], tacticOdds(A, pd).parts.terr); });
  // 특기: 성공하면 대성공, 성공 자체는 확률대로
  var Z = made['장비'], oz = tacticOdds(Z, made['조조']);
  chk('특기가 맞아도 성공은 확률대로(장비→조조)', oz.sure && oz.crit === oz.ok && oz.ok < 100 && oz.parts.skill === 5, JSON.stringify(oz));
  // 피해의 병력 비
  function sk(at, dt) { A.troops = at; D.troops = dt; return tacticSizeK(A, D); }
  chk('병력 비 보정: 같으면 1', Math.abs(sk(6000, 6000) - 1) < 1e-9); chk('절반이면 0.84', Math.abs(sk(3000, 6000) - 0.8409) < 1e-3, sk(3000, 6000)); chk('바닥 0.75', sk(1000, 24000) === 0.75); chk('천장 1.1', sk(24000, 6000) === 1.1);
  var idan = TACTICS.spear[2];
  A.troops = A.max = 6000; D.troops = D.max = 6000; var t1 = trial(A, D, idan, N);
  A.troops = A.max = 6000; D.troops = D.max = 24000; var t2 = trial(A, D, idan, N);
  var r12 = (t2.dmgOk / t2.ok) / (t1.dmgOk / t1.ok);
  chk('상대가 네 배면 전법 피해 ×0.75쯤', Math.abs(r12 - 0.75) < 0.04, r12.toFixed(3));
  // 반격과 실패 피해(상대 병력을 크게 두어 화력이 천장에 붙게 한다 — 맞은 뒤에도 반격의 병력 계수가 같다)
  A.troops = A.max = 6000; D.troops = D.max = 24000;
  var bc = 0, bd = 0; for (var bi = 0; bi < 3000; bi++) { bc += dmgUU(D, A, 0.55, false); bd += dmgUU(A, D, 1, false); } bc /= 3000; bd /= 3000;
  var cOk = t2.cOk / Math.max(1, t2.nCOk), cFl = t2.cFail / Math.max(1, t2.nCFail), dFl2 = t2.dmgFail / Math.max(1, t2.fail);
  chk('성공 때 반격 = 보통 공격 반격의 ' + Math.round(TACTIC_K.okCounter / 0.55 * 100) + '%', t2.nCOk > 200 && Math.abs(cOk / bc - TACTIC_K.okCounter / 0.55) < 0.05, (cOk / bc).toFixed(3) + ' n=' + t2.nCOk);
  chk('실패 때 반격 = 보통 공격 반격의 ' + Math.round(TACTIC_K.failCounter / 0.55 * 100) + '%', t2.nCFail > 200 && Math.abs(cFl / bc - TACTIC_K.failCounter / 0.55) < 0.06, (cFl / bc).toFixed(3) + ' n=' + t2.nCFail);
  chk('실패 때 피해 = 보통 공격의 ' + Math.round(TACTIC_K.failDmg * 100) + '%', Math.abs(dFl2 / bd - TACTIC_K.failDmg) < 0.04, (dFl2 / bd).toFixed(3));
  chk('성공하면 반격을 빠짐없이 받는다(탈기)', t2.nCOk === t2.ok + t2.crit, t2.nCOk + ' / ' + (t2.ok + t2.crit));
  rows.push('v0.8 조운 6천 → 하후돈 2만4천 탈기: 보통 공격 ' + Math.round(bd) + ' / 반격 ' + Math.round(bc) + ' | 전법 성공 ' + Math.round(t2.dmgOk / Math.max(1, t2.ok)) + ' / 반격 ' + Math.round(cOk) + ' | 실패 ' + Math.round(dFl2) + ' / 반격 ' + Math.round(cFl) + ' | 상대 6천일 때 성공 피해 ' + Math.round(t1.dmgOk / Math.max(1, t1.ok)));
  placeUnit(A, kA[0], kA[1]); placeUnit(D, kD[0], kD[1]);
  return { rows: rows, fails: FAILS };
}
`, ctx);
const out = vm.runInContext('run(' + N + ')', ctx);
out.rows.forEach(r => console.log(r));
console.log('\n시행 ' + N + '회씩. 어긋난 것 ' + out.fails.length + '건');
out.fails.slice(0, 30).forEach(f => console.log('  ✗ ' + f));
process.exit(out.fails.length ? 1 : 0);
