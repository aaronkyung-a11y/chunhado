// v0.13 — 대결(일기토 · 설전)의 규칙 시험.   node tests/duel13.js
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.env.SRC || path.join(__dirname, '..', 'src');
const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array };
vm.createContext(ctx);
for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
let pass = 0, fail = 0;
function ok(c, msg) { if (c) pass++; else { fail++; console.log('  ✗ ' + msg); } }
const R = JSON.parse(vm.runInContext(`JSON.stringify((function () {
  var R = {};
  newGame(0, 1); G.aiOnly = false;
  function O(n) { return G.officers.filter(function (o) { return o.n === n; })[0]; }
  function eq(st, rd) { return { id: 0, n: 'x', war: st, int: rd === undefined ? 70 : rd, cha: 70 }; }
  // ① 수의 물림: 능력이 같은 두 사람으로 아홉 가지(일기토) · 아홉 가지(설전)
  R.pairs = {};
  ['duel', 'talk'].forEach(function (kind) {
    var ids = DUEL_KIND[kind].order, A = O('하후돈'), D = O('하후돈');
    ids.forEach(function (ma) { ids.forEach(function (md) {
      var S = duelNew(kind, A, D), r = duelStep(S, ma, md);
      R.pairs[kind + ':' + ma + '>' + md] = [r.win, r.how, r.toA, r.toD, r.heal, S.a.mom, S.d.mom, S.a.hp, S.d.hp];
    }); });
  });
  // ② 피해의 크기: 같은 능력에서 맹공이 필살을 이겼을 때(×1.0 × 맞는 쪽 1.3) · 필살이 방어를 부쉈을 때(×1.6) · 방어가 받아쳤을 때(×0.7) — 평균
  function avg(kind, ma, md, N, A, D) { var s = 0; for (var i = 0; i < N; i++) { var S = duelNew(kind, A, D), r = duelStep(S, ma, md); s += r.toD; } return s / N; }
  var H = O('하후돈');
  R.dmg = { atkSp: avg('duel', 'atk', 'sp', 3000, H, H), spDef: avg('duel', 'sp', 'def', 3000, H, H), defAtk: avg('duel', 'def', 'atk', 3000, H, H), talk: avg('talk', 'ri', 'gain', 3000, H, H) };
  var LB = O('여포'), CH = O('조홍');
  R.ratio = { strong: avg('duel', 'sp', 'def', 3000, LB, CH), weak: avg('duel', 'sp', 'def', 3000, CH, LB), wA: LB.war, wD: CH.war };
  // ③ 기세: 세 번 이기면 3 에서 멈추고 지면 0
  var S = duelNew('duel', H, H, { hpA: 9999, hpD: 9999, rounds: 99 }); var moms = [];
  for (var i = 0; i < 4; i++) { duelStep(S, 'atk', 'sp'); moms.push(S.a.mom); } duelStep(S, 'sp', 'atk'); moms.push(S.a.mom, S.d.mom);
  var m3 = 0, m0 = 0; for (i = 0; i < 3000; i++) { var S3 = duelNew('duel', H, H, { hpA: 9999, hpD: 9999, rounds: 99 }); S3.a.mom = 3; m3 += duelStep(S3, 'atk', 'sp').toD; var S0 = duelNew('duel', H, H, { hpA: 9999, hpD: 9999, rounds: 99 }); m0 += duelStep(S0, 'atk', 'sp').toD; }
  R.mom = { seq: moms, k: m3 / m0 };
  // ④ 끝: 쓰러뜨림 · 판정 · 비김
  S = duelNew('duel', H, H, { hpD: 10 }); duelStep(S, 'sp', 'def'); R.ko = [S.over, S.win, S.ko, S.d.hp, S.round];
  S = duelNew('duel', H, H, { hpA: 9999, hpD: 9999 }); for (i = 0; i < 5; i++) duelStep(S, 'def', 'def'); R.judgeDraw = [S.over, S.win, S.ko, S.round];
  S = duelNew('duel', H, H); duelStep(S, 'atk', 'sp'); for (i = 0; i < 4; i++) duelStep(S, 'def', 'def'); R.judge = [S.over, S.win, S.ko, S.round, duelStep(S, 'atk', 'atk'), S.a.hp, S.d.hp];
  // ⑤ 기색: 읽을 확률과 실제로 맞는 비율
  var SX = duelNew('duel', O('조조'), O('하후돈')); R.read = [duelRead(SX, 'a'), duelRead(SX, 'd'), O('조조').int, O('하후돈').int];
  var hit = 0, N = 6000; for (i = 0; i < N; i++) { var Sh = duelNew('duel', O('조조'), O('하후돈')); duelPlan(Sh, 'a'); if (Sh.hint.move === Sh.plan.d) hit++; if (Sh.plan.a !== null) R.planBad = 1; }
  R.readHit = hit / N * 100;
  // ⑥ 능력의 무게: 저절로 겨뤘을 때
  function rate(kind, a, d, N2, opt) { var w = 0, dr = 0; for (var i = 0; i < N2; i++) { var Sx = duelAuto(duelNew(kind, O(a), O(d), opt)); if (Sx.win === 'a') w++; else if (Sx.win === 'draw') dr++; } return [Math.round(w / N2 * 1000) / 10, Math.round(dr / N2 * 1000) / 10]; }
  R.rates = { lb_hd: rate('duel', '여포', '하후돈', 3000), lb_ch: rate('duel', '여포', '조홍', 3000), hd_hd: rate('duel', '하후돈', '하후돈', 3000), sy_hd: rate('talk', '순욱', '하후돈', 2000), cc_sy150: rate('talk', '조조', '순욱', 3000, { hpD: 150 }) };
  // ⑦ 같은 씨앗이면 같은 판
  function trace(seed) { newGame(0, seed); var Sx = duelAuto(duelNew('duel', O('여포'), O('장비'))); return JSON.stringify(Sx.log); }
  R.same = trace(5) === trace(5); R.diff = trace(5) !== trace(6);
  // ---------- 싸움터 ----------
  newGame(0, 1); G.aiOnly = false;
  var b = facCities(0)[0], eb = null; for (i = 0; i < G.bases.length && !eb; i++) if (G.bases[i].owner > 0 && G.bases[i].kind === 'city') eb = G.bases[i];
  b.troops = 60000; b.food = 200000; b.w.spear = 30000; eb.troops = 60000; eb.food = 200000; eb.w.spear = 30000; G.factions[0].ap = 255; G.factions[eb.owner].ap = 255;
  function field() { for (var r = 92; r < 112; r++) for (var c = 146; c < 168; c++) { var good = true; for (var dr = -2; dr <= 2 && good; dr++) for (var dc = -3; dc <= 3 && good; dc++) { var k = K(c + dc, r + dr); if (TCH[k] !== 112 || BAT[k] !== undefined || PAT[k] || UAT[k]) good = false; } if (good) return [c, r]; } return null; }
  var f = field();
  function mk(base, name, c, r) { var o = name ? O(name) : idleOfficers(base).sort(function (x, y) { return y.war - x.war; })[0]; var x = cmdDeploy(base, { type: 'spear', ids: [o.id], troops: 5000, food: 5000 }); placeUnit(x.unit, c, r); x.unit.born = -9; x.unit.done = false; x.unit.morale = 80; return x.unit; }
  var ua = mk(b, '하후돈', f[0], f[1]), ud = mk(eb, null, f[0] + 1, f[1]);
  R.adj = hdist(ua.c, ua.r, ud.c, ud.r); R.leaders = [uLeader(ua).n, uLeader(ua).war, uLeader(ud).n, uLeader(ud).war];
  function reset() { ua.troops = 5000; ud.troops = 5000; ua.morale = 80; ud.morale = 80; ua.status = null; ud.status = null; ua.done = false; ud.done = false; }
  // 저절로 끝나는 일기토(DUEL_DEFER 꺼짐): 결과가 곧바로 입혀진다 — 세 갈래를 모두 볼 때까지
  var seen = {}, tries = 0;
  while (tries++ < 400 && !(seen.win && seen.ko && seen.draw)) {
    reset(); var la = uLeader(ua), ld = uLeader(ud), ma0 = la.merit, md0 = ld.merit, res = {}, S1 = duelBattle(ua, ud, res), d1 = res.duel;
    var key = d1.draw ? 'draw' : (d1.ko ? 'ko' : 'win'); if (seen[key]) continue;
    var Wn = d1.draw ? null : (d1.win ? ua : ud), Ls = d1.draw ? null : (d1.win ? ud : ua);
    seen[key] = { d: d1, wm: Wn ? Wn.morale : 0, lm: Ls ? Ls.morale : 0, lt: Ls ? Ls.troops : 0, st: Ls ? Ls.status : null, merit: [la.merit - ma0, ld.merit - md0], done: S1.done, again: duelFinish(S1, {}) };
  }
  R.seen = seen; R.tries = tries;
  // 미뤄 둔 일기토(DUEL_DEFER): 판만 돌려주고, duelFinish 를 부를 때까지 아무것도 바뀌지 않는다
  reset(); DUEL_DEFER = true; var res2 = {}, S2 = duelBattle(ua, ud, res2); DUEL_DEFER = false;
  R.defer = { has: !!res2.duelS, noDuel: res2.duel === undefined, over: S2.over, same: ua.morale === 80 && ud.morale === 80 && ua.troops === 5000 && ud.troops === 5000 };
  duelPlan(S2, 'a'); R.defer.hint = !!S2.hint && S2.plan.a === null && !!S2.plan.d;
  while (!S2.over) { duelPlan(S2, 'a'); duelStep(S2, 'atk', S2.plan.d); }
  var o2 = duelFinish(S2, res2); R.defer.fin = [!!o2, !!res2.duel, duelFinish(S2, res2) === null, ua.morale !== 80 || ud.morale !== 80 || o2.draw];
  // ---------- 일기토 신청 ----------
  reset(); var p = challengeChance(ua, ud), la2 = uLeader(ua), ld2 = uLeader(ud);
  R.ch = { p: p, want: Math.round(clamp(50 + (ld2.war - la2.war) * 4 + (ld2.war >= 85 && ld2.int < 70 ? 20 : 0), 5, 95)), targets: challengeTargets(ua).length, roll: [challengeRoll(ua, ud), challengeRoll(ua, ud)] };
  var yes = challengeRoll(ua, ud) < p;
  DUEL_DEFER = true; var rc = unitChallenge(ua, { kind: 'unit', u: ud, c: ud.c, r: ud.r }); DUEL_DEFER = false;
  R.ch.res = [rc.ok, rc.accepted === yes, ua.morale, ua.done, yes ? !!rc.duelS : ud.morale, rc.p];
  R.ch.again = unitChallenge(ua, { kind: 'unit', u: ud, c: ud.c, r: ud.r }).msg || '';
  reset(); ua.morale = 5; R.ch.low = unitChallenge(ua, { kind: 'unit', u: ud, c: ud.c, r: ud.r }).msg || '';
  reset(); ud.status = 'confuse'; R.ch.conf = [unitChallenge(ua, { kind: 'unit', u: ud, c: ud.c, r: ud.r }).msg || '', challengeTargets(ua).length];
  reset(); placeUnit(ud, f[0] + 2, f[1]); R.ch.far = unitChallenge(ua, { kind: 'unit', u: ud, c: ud.c, r: ud.r }).msg || ''; placeUnit(ud, f[0] + 1, f[1]);
  // 응할 확률의 끝: 약한 상대는 5%, 강한 맹장은 95%
  var weak = { off: [G.officers.filter(function (o) { return o.war < 40; })[0].id] }, lb = O('여포');
  R.ch.ends = [Math.round(clamp(50 + (off(weak.off[0]).war - la2.war) * 4, 5, 95)), Math.round(clamp(50 + (lb.war - la2.war) * 4 + 20, 5, 95))];
  // ---------- 설전으로 등용 ----------
  newGame(0, 1); G.aiOnly = false; b = facCities(0)[0]; G.factions[0].ap = 255;
  var free = G.officers.filter(function (o) { return o.st === 'free' || o.st === 'hidden'; });
  var t = free[0]; t.st = 'free'; t.loc = b.id; var o1 = idleOfficers(b).filter(function (o) { return !isLord(o); })[0];
  var pp = recruitChance(b, o1, t);
  R.talk = { p: pp, ok: talkRecruitOk(b, o1, t) === (pp >= 10 && pp < 100) };
  var St = talkRecruitNew(b, o1, t); R.talk.hp = [St.d.max, Math.round(100 * (1 + (60 - pp) / 100)), St.a.max, St.kind];
  R.talk.unfinished = cmdRecruit(b, o1.id, t.id, St).msg || '';
  St.over = true; St.win = 'd'; var ap0 = G.factions[0].ap, rl = cmdRecruit(b, o1.id, t.id, St);
  R.talk.lose = [rl.ok, !!rl.joined, t.f, G.factions[0].ap < ap0, St.used === true];
  R.talk.reuse = cmdRecruit(b, o1.id, t.id, St).msg || '';
  // 이긴 설전: 주사위가 어떻든 합류한다 — 다른 재야 무장으로
  var t2 = free[1]; t2.st = 'free'; t2.loc = b.id; var o2b = idleOfficers(b).filter(function (o) { return !isLord(o); })[0];
  var Sw = talkRecruitNew(b, o2b, t2); Sw.over = true; Sw.win = 'a'; var rw = cmdRecruit(b, o2b.id, t2.id, Sw);
  R.talk.win = [rw.ok, !!rw.joined, t2.f === 0, t2.st];
  var t3 = free[2]; t3.st = 'free'; t3.loc = b.id; var o3 = idleOfficers(b).filter(function (o) { return !isLord(o); })[0];
  var Sm = talkRecruitNew(b, o3, t3); Sm.over = true; Sm.win = 'a'; Sm.rt = t2.id; R.talk.mismatch = cmdRecruit(b, o3.id, t3.id, Sm).msg || '';
  var Sd = duelNew('duel', o3, t3); Sd.over = true; Sd.win = 'a'; Sd.rb = b.id; Sd.ro = o3.id; Sd.rt = t3.id; R.talk.wrongKind = cmdRecruit(b, o3.id, t3.id, Sd).msg || '';
  R.talk.plain = cmdRecruit(b, o3.id, t3.id).ok;                     // 넷째 인수가 없으면 전과 같이 주사위
  return R;
})())`, ctx));
const P = R.pairs, K = k => P[k];
// ① 물림
ok(K('duel:atk>sp')[0] === 'a' && K('duel:sp>def')[0] === 'a' && K('duel:def>atk')[0] === 'a' && K('duel:sp>atk')[0] === 'd' && K('duel:def>sp')[0] === 'd' && K('duel:atk>def')[0] === 'd', '일기토: 맹공 > 필살 > 방어 > 맹공');
ok(K('talk:ri>gain')[0] === 'a' && K('talk:gain>tide')[0] === 'a' && K('talk:tide>ri')[0] === 'a' && K('talk:gain>ri')[0] === 'd' && K('talk:tide>gain')[0] === 'd' && K('talk:ri>tide')[0] === 'd', '설전: 도리 > 이해 > 시세 > 도리');
ok(K('duel:atk>atk')[1] === 'both' && K('duel:atk>atk')[2] > 0 && K('duel:atk>atk')[3] > 0 && K('duel:atk>atk')[0] === null, '맹공끼리: 서로 친다');
ok(K('duel:def>def')[1] === 'rest' && K('duel:def>def')[4] === 6 && K('duel:def>def')[2] === 0 && K('duel:def>def')[7] === 100, '방어끼리: 숨을 고른다(+6, 가득 찬 힘은 넘지 않는다)');
ok(K('duel:sp>sp')[1] === 'clash' && (K('duel:sp>sp')[0] === 'a' || K('duel:sp>sp')[0] === 'd') && (K('duel:sp>sp')[2] > 0) !== (K('duel:sp>sp')[3] > 0), '필살끼리: 겨뤄서 한쪽만 맞는다');
ok(['ri', 'gain', 'tide'].every(m => K('talk:' + m + '>' + m)[1] === 'both' && K('talk:' + m + '>' + m)[2] > 0 && K('talk:' + m + '>' + m)[3] > 0), '설전의 같은 수: 서로 깎인다');
ok(K('duel:atk>sp')[5] === 1 && K('duel:atk>sp')[6] === 0 && K('duel:atk>atk')[5] === 0, '이긴 쪽의 기세 +1, 비기면 그대로');
// ② 피해
const D = R.dmg;
console.log('피해(능력이 같을 때의 평균): 맹공→필살 ' + D.atkSp.toFixed(1) + ' · 필살→방어 ' + D.spDef.toFixed(1) + ' · 방어→맹공 ' + D.defAtk.toFixed(1) + ' · 설전 ' + D.talk.toFixed(1) + '  |  여포(' + R.ratio.wA + ')→조홍(' + R.ratio.wD + ') ' + R.ratio.strong.toFixed(1) + ' · 조홍→여포 ' + R.ratio.weak.toFixed(1));
ok(Math.abs(D.atkSp - 24 * 1.3) < 0.8 && Math.abs(D.spDef - 24 * 1.6) < 0.9 && Math.abs(D.defAtk - 24 * 0.7) < 0.5 && Math.abs(D.talk - 24) < 0.6, '피해 = 24 × 배수(맹공이 필살을 치면 ×1.3 · 필살 ×1.6 · 받아치기 ×0.7 · 설전 ×1)');
const want = Math.pow(R.ratio.wA / R.ratio.wD, 2.5);
ok(Math.abs(R.ratio.strong / (24 * 1.6) - want) < 0.06 && Math.abs(R.ratio.weak / (24 * 1.6) - 1 / want) < 0.04, '능력의 비^2.5 가 피해에 곱해진다: ×' + (R.ratio.strong / 38.4).toFixed(2) + ' / ×' + (R.ratio.weak / 38.4).toFixed(2) + ' (바란 값 ×' + want.toFixed(2) + ')');
// ③ 기세
ok(JSON.stringify(R.mom.seq) === '[1,2,3,3,0,1]', '기세는 셋까지, 지면 0 ' + JSON.stringify(R.mom.seq));
ok(Math.abs(R.mom.k - 1.36) < 0.03, '기세 셋이면 피해 ×1.36 (' + R.mom.k.toFixed(3) + ')');
// ④ 끝
ok(R.ko[0] && R.ko[1] === 'a' && R.ko[2] === true && R.ko[3] === 0 && R.ko[4] === 1, '쓰러뜨리면 그 자리에서 끝난다 ' + JSON.stringify(R.ko));
ok(R.judgeDraw[0] && R.judgeDraw[1] === 'draw' && !R.judgeDraw[2] && R.judgeDraw[3] === 5, '다섯 합을 채우고 차이가 없으면 비김');
ok(R.judge[0] && R.judge[1] === 'a' && !R.judge[2] && R.judge[4] === null, '다섯 합 뒤 남은 힘이 많은 쪽이 판정승 · 끝난 판은 더 나아가지 않는다');
// ⑤ 기색
ok(R.read[0] === Math.round(Math.min(85, Math.max(35, 55 + (R.read[2] - R.read[3]) * 0.5))) && R.read[1] === Math.round(Math.min(85, Math.max(35, 55 + (R.read[3] - R.read[2]) * 0.5))), '읽을 확률 = 55 + 읽는 능력의 차 × 0.5 (35~85): ' + R.read[0] + '% / ' + R.read[1] + '%');
ok(Math.abs(R.readHit - R.read[0]) < 2.5 && !R.planBad, '기색이 실제로 맞는 비율 ' + R.readHit.toFixed(1) + '% ≈ ' + R.read[0] + '%');
// ⑥ 능력의 무게
console.log('저절로 겨룬 승률(승 · 비김 %): 여포-하후돈 ' + R.rates.lb_hd + ' · 여포-조홍 ' + R.rates.lb_ch + ' · 하후돈-하후돈 ' + R.rates.hd_hd + ' · 설전 순욱-하후돈 ' + R.rates.sy_hd + ' · 설전 조조-순욱(힘 150) ' + R.rates.cc_sy150);
ok(R.rates.lb_hd[0] > 62 && R.rates.lb_hd[0] < 80 && R.rates.lb_ch[0] > 80 && Math.abs(R.rates.hd_hd[0] - (100 - R.rates.hd_hd[1]) / 2) < 4 && R.rates.sy_hd[0] > 95 && R.rates.cc_sy150[0] < 30, '강한 쪽이 더 자주 이기되 뒤집힐 수 있다');
ok(R.same && R.diff, '같은 씨앗이면 같은 판, 다른 씨앗이면 다른 판');
// ⑦ 싸움터
ok(R.adj === 1 && R.leaders[1] >= 75, '시험 부대 둘이 붙어 있다 ' + JSON.stringify(R.leaders));
const sw = R.seen.win, sk = R.seen.ko, sd = R.seen.draw;
ok(sw && sk && sd, '세 갈래(판정승 · 쓰러뜨림 · 비김)를 모두 봤다(' + R.tries + '번)');
if (sw && sk && sd) {
  ok(sw.lm === 80 - 25 && sw.wm === 90 && sw.lt === 5000 - Math.round(5000 * 0.08) && sw.d.loss === 400 && !sw.st, '판정으로 지면: 기력 -25 · 병력 -8% / 이긴 쪽 기력 +10 ' + JSON.stringify([sw.lm, sw.wm, sw.lt]));
  ok(sk.lm === 80 - 35 && sk.lt === 5000 - 600 && sk.st === 'confuse' && sk.d.confused === true, '쓰러지면: 기력 -35 · 병력 -12% · 혼란 ' + JSON.stringify([sk.lm, sk.lt, sk.st]));
  ok(sw.merit.indexOf(100) >= 0 && sw.merit.indexOf(0) >= 0 && sd.merit[0] === 30 && sd.merit[1] === 30 && sd.d.loss === 0, '공적: 이긴 주장 +100, 비기면 둘 다 +30');
  ok(sw.done === true && sw.again === null, '결과는 한 번만 입혀진다');
}
ok(R.defer.has && R.defer.noDuel && !R.defer.over && R.defer.same && R.defer.hint, '미뤄 둔 일기토: 판만 돌려주고 아무것도 바뀌지 않는다 · 사람 쪽 수는 비워 두고 기색을 준다');
ok(R.defer.fin[0] && R.defer.fin[1] && R.defer.fin[2] && R.defer.fin[3], '끝난 뒤 duelFinish 가 결과를 입힌다(두 번째는 아무 일도 없다)');
// ⑧ 신청
ok(R.ch.p === R.ch.want && R.ch.targets === 1 && R.ch.roll[0] === R.ch.roll[1], '응할 확률 = 50 + 무력 차 × 4 (+20 맹장): ' + R.ch.p + '% · 주사위는 같은 턴에 같다');
ok(R.ch.res[0] && R.ch.res[1] && R.ch.res[2] === 70 && R.ch.res[3] === true && (R.ch.res[4] === true || R.ch.res[4] === 75), '신청: 기력 -10 · 행동 끝 · 응하면 판, 응하지 않으면 상대 기력 -5 ' + JSON.stringify(R.ch.res));
ok(/이미 행동/.test(R.ch.again) && /기력이 부족/.test(R.ch.low) && /어지러운|응할 수/.test(R.ch.conf[0]) && R.ch.conf[1] === 0 && /옆에 붙은/.test(R.ch.far), '걸 수 없는 때: 행동 끝 · 기력 부족 · 혼란한 상대 · 떨어진 상대');
ok(R.ch.ends[0] === 5 && R.ch.ends[1] === 95, '응할 확률은 5%~95%');
// ⑨ 설전 등용
ok(R.talk.ok && R.talk.hp[0] === R.talk.hp[1] && R.talk.hp[2] === 100 && R.talk.hp[3] === 'talk', '설전 등용: 확률 ' + R.talk.p + '% → 상대의 버티는 힘 ' + R.talk.hp[0]);
ok(/설전의 결과/.test(R.talk.unfinished) && R.talk.reuse !== "" && /설전의 결과/.test(R.talk.mismatch) && /설전의 결과/.test(R.talk.wrongKind), '끝나지 않은 판 · 이미 쓴 판 · 다른 사람의 판 · 일기토의 판은 받지 않는다 ' + JSON.stringify([R.talk.unfinished, R.talk.reuse, R.talk.mismatch, R.talk.wrongKind]));
ok(R.talk.lose[0] && !R.talk.lose[1] && R.talk.lose[2] !== 0 && R.talk.lose[3] && R.talk.lose[4], '진 설전: 거절(행동력은 쓴다)');
ok(R.talk.win[0] && R.talk.win[1] && R.talk.win[2] && R.talk.win[3] === 'active', '이긴 설전: 합류한다');
ok(R.talk.plain === true, '넷째 인수가 없으면 전과 같이 주사위로');
console.log((fail ? 'FAIL ' : 'ok ') + pass + ' / ' + (pass + fail));
process.exit(fail ? 1 : 0);
