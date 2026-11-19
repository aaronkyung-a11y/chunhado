// v0.7 전법 규칙 확인: 성공·대성공 확률이 표시값과 같은가, 대성공 때 효과가 세지는가, 혼란이 상대 능력치에 따르는가
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
  var out = { n: n, fail: 0, ok: 0, crit: 0, conf: 0, confOk: 0, confCrit: 0, mor: {}, push: {}, dmgOk: 0, dmgCrit: 0, dmgFail: 0, fireT: {}, pOk: 0, pCrit: 0, pConf: {} };
  var a0 = [a.c, a.r], d0 = [d.c, d.r], aT = a.troops, dT = d.troops, aM = a.morale, dM = d.morale;
  for (var i = 0; i < n; i++) {
    if (!UMAP[a.id] || !UMAP[d.id]) throw new Error('부대가 사라짐');
    placeUnit(a, a0[0], a0[1]); placeUnit(d, d0[0], d0[1]);
    a.troops = aT; d.troops = dT; a.morale = aM; d.morale = dM; a.done = false; d.done = false; a.status = d.status = null; a.stT = d.stT = 0; G.fires = {};
    var res = unitTactic0(a, tac, { kind: 'unit', u: d, c: d.c, r: d.r });
    if (!res.ok) throw new Error(res.msg);
    out.pOk = res.pOk; out.pCrit = res.pCrit;
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
  return { rows: rows, fails: FAILS };
}
`, ctx);
const out = vm.runInContext('run(' + N + ')', ctx);
out.rows.forEach(r => console.log(r));
console.log('\n시행 ' + N + '회씩. 어긋난 것 ' + out.fails.length + '건');
out.fails.slice(0, 30).forEach(f => console.log('  ✗ ' + f));
process.exit(out.fails.length ? 1 : 0);
