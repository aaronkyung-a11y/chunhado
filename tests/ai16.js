// v0.16 — 규칙 시험: AI 가 걸어오는 일기토 · 출병 요청 · AI 끼리의 협정.   node tests/ai16.js
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.env.SRC || path.join(__dirname, '..', 'src');
const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array };
vm.createContext(ctx);
for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
let pass = 0, fail = 0;
function ok(c, msg) { if (c) pass++; else { fail++; console.log('  ✗ ' + msg); } }
const R = JSON.parse(vm.runInContext(`JSON.stringify((function () {
  var R = {}, DK = DUEL_K, PK = DIP_K, _r = rnd;
  function O(n) { return G.officers.filter(function (o) { return o.n === n; })[0]; }
  function field() { for (var r = 92; r < 112; r++) for (var c = 146; c < 168; c++) { var good = true; for (var dr = -2; dr <= 2 && good; dr++) for (var dc = -3; dc <= 3 && good; dc++) { var k = K(c + dc, r + dr); if (TCH[k] !== 112 || ZONE[k] >= 0 || BAT[k] !== undefined || PAT[k] || UAT[k] || ELV[k] !== ELV[K(c, r)]) good = false; } if (good) return [c, r]; } return null; }
  function setup(seed) {
    newGame(0, seed); G.aiOnly = false; if (G.peace) G.peace.until = 0;
    var b = facCities(G.player)[0], eb = G.bases[baseByName('복양')]; b.troops = 60000; b.w.spear = 30000; b.food = 200000; eb.troops = 60000; eb.w.spear = 30000; eb.food = 200000; G.factions[G.player].ap = 250; G.factions[eb.owner].ap = 250;
    var me = O('하후돈'), foe = O('여포'), f = field();
    var a = cmdDeploy(eb, { type: 'spear', ids: [foe.id], troops: 5000, food: 5000 }).unit, d = cmdDeploy(b, { type: 'spear', ids: [me.id], troops: 5000, food: 5000 }).unit;
    placeUnit(a, f[0], f[1]); placeUnit(d, f[0] + 1, f[1]); [a, d].forEach(function (u) { u.born = -9; u.done = false; u.mp = uMaxMp(u); u.morale = 80; });
    return { a: a, d: d, f: f, b: b, eb: eb };
  }
  // ① 걸 마음: 무력이 높고 상대와 겨룰 만할 때
  var S = setup(1), a = S.a, d = S.d;
  R.want = { base: aiWantsDuel(a, d), rev: aiWantsDuel(d, a), wars: [uLeader(a).war, uLeader(d).war] };
  a.morale = DK.ask + DK.aiMorale - 1; R.want.tired = aiWantsDuel(a, d); a.morale = 80;
  d.status = 'confuse'; R.want.conf = aiWantsDuel(a, d); d.status = null;
  var w0 = uLeader(d).war; uLeader(d).war = DK.minWar - 1; R.want.weak = aiWantsDuel(a, d); uLeader(d).war = w0;
  var wa = uLeader(a).war; uLeader(a).war = w0 + DK.aiLead - 1; R.want.lower = aiWantsDuel(a, d); uLeader(a).war = Math.max(DK.aiMinWar, w0 + DK.aiLead); R.want.edge = aiWantsDuel(a, d); uLeader(a).war = wa;
  dipSign(a.f, d.f, 'truce'); R.want.pact = aiWantsDuel(a, d); delete G.dip.pact[dipKey(a.f, d.f)];
  // ② 내 부대에 걸면: 적어 두고 내 차례에 답한다
  var L0 = G.log.length, r1 = aiChallenge(a, d);
  R.ask = { ok: r1, n: G.asks.length, a: G.asks[0].a === a.id, d: G.asks[0].d === d.id, done: a.done, mor: a.morale, dmor: d.morale, log: G.log.slice(L0).map(function (x) { return x.t + '#' + x.imp; }).join('|'), list: duelAsks().length, ev: EVQ.filter(function (e) { return e.t === 'ask'; }).length };
  a.done = false; R.askTwice = aiChallenge(a, d); a.done = true;
  // 떨어지면 없던 일
  placeUnit(a, S.f[0] - 2, S.f[1]); R.askFar = [duelAsks().length, duelAskAnswer(a.id, d.id, true).msg || '']; placeUnit(a, S.f[0], S.f[1]);
  // 응하지 않는다
  G.asks = [{ a: a.id, d: d.id, turn: G.turn }]; var no = duelAskAnswer(a.id, d.id, false);
  R.no = { ok: no.ok, acc: no.accepted, mor: d.morale, left: duelAsks().length, again: duelAskAnswer(a.id, d.id, false).msg || '' };
  // 응한다 → 판을 받아 겨루고 맺는다
  G.asks = [{ a: a.id, d: d.id, turn: G.turn }]; d.morale = 80; a.morale = 70; var tr0 = [a.troops, d.troops], mt0 = uLeader(a).merit + uLeader(d).merit;
  var yes = duelAskAnswer(a.id, d.id, true), DS = yes.duelS;
  R.yes = { ok: yes.ok, acc: yes.accepted, kind: DS && DS.kind, who: DS && [DS.a.id === uLeader(a).id, DS.d.id === uLeader(d).id, DS.ua === a.id, DS.ud === d.id], over: DS && DS.over, untouched: d.morale === 80 && a.morale === 70, defer: DUEL_DEFER, left: duelAsks().length };
  duelAuto(DS); var out = duelFinish(DS, yes);
  R.fin = { win: DS.win, out: !!out, duel: !!yes.duel, changed: a.morale !== 70 || d.morale !== 80 || a.troops !== tr0[0] || d.troops !== tr0[1] || uLeader(a).merit + uLeader(d).merit !== mt0, twice: duelFinish(DS, yes) };
  // ③ 차례를 넘기면 응하지 않은 것
  S = setup(2); a = S.a; d = S.d; aiChallenge(a, d); var m0 = d.morale; var st = turnStepper();
  R.lapse = { mor: m0 - d.morale, n: (G.asks || []).length };
  // ④ AI 가 제 차례에 건다(확률을 100 으로)
  S = setup(3); a = S.a; d = S.d; var keepAsk = DK.aiAsk; DK.aiAsk = 100; d.done = true; a.ai = a.ai || {}; 
  endTurn(); DK.aiAsk = keepAsk;
  var asked = (G.asks || []).filter(function (x) { return x.d === d.id; });
  R.turn = { n: asked.length, by: asked.length ? uLeader(UMAP[asked[0].a]).n : '', alive: !!UMAP[d.id], rep: REPORT.filter(function (x) { return /일기토를 걸어왔다/.test(x.t); }).length };
  // ⑤ AI 끼리는 그 자리에서: 응하면 저절로 겨룬다
  S = setup(4); a = S.a; d = S.d; d.f = 2; d.off.forEach(function (id) { off(id).f = 2; }); G.asks = [];
  rnd = function () { return 0.01; }; var _cr = challengeRoll; challengeRoll = function () { return 0; }; var r5 = aiChallenge(a, d); challengeRoll = _cr; rnd = _r;
  var e5 = EVQ.filter(function (e) { return e.t === 'act' && e.res && e.res.kind === 'challenge'; })[0];
  R.aiai = { ok: r5, asks: G.asks.length, done: a.done, ev: !!e5, acc: e5 && e5.res.accepted, rec: e5 && !!e5.res.duelRec, duel: e5 && !!e5.res.duel };
  // AI 대전에서는 플레이어 자리의 부대에도 그 자리에서
  S = setup(5); G.aiOnly = true; G.asks = []; challengeRoll = function () { return 99; }; var r6 = aiChallenge(S.a, S.d); challengeRoll = _cr; R.aionly = [r6, G.asks.length, S.a.done];
  // ⑥ 출병 요청
  newGame(0, 6); G.aiOnly = false; if (G.peace) G.peace.until = 0;
  var me = G.player, b = facCities(me)[0], N = dipNbrs(); b.gold = 20000; G.factions[me].ap = 250;
  function idle() { return idleOfficers(b).filter(function (o) { return !isLord(o); }); }
  var t = -1, x = -1; for (var i = 0; i < G.factions.length && t < 0; i++) { if (i === me || !dipFac(i)) continue; for (var k in N[i] || {}) if (+k !== me && dipFac(+k)) { t = i; x = +k; break; } }
  var far = -1; for (i = 0; i < G.factions.length; i++) if (i !== me && i !== t && dipFac(i) && !dipNear(t, i, N)) { far = i; break; }
  R.nb = { sym: dipNear(t, x, N) && dipNear(x, t, N), self: dipNear(t, t, N) };
  R.aimNo = aimCan(me, t, x);
  dipSign(me, t, 'truce'); R.aimTruce = aimCan(me, t, x); dipSign(me, t, 'ally');
  R.aimOk = aimCan(me, t, x); R.aimFar = far >= 0 ? aimCan(me, t, far) : 'none'; R.aimSelf = [aimCan(me, t, me), aimCan(me, t, t)];
  dipSign(t, x, 'truce'); R.aimPact = aimCan(me, t, x); delete G.dip.pact[dipKey(t, x)];
  dipOf().rel[dipKey(me, t)] = 80; var e = idle()[0], q = aimTerms(me, t, x, e);
  R.terms = { q: q, sum: clamp(q.rel + q.base + q.envoy + q.pow + q.war, 0, PK.askHi), envoy: Math.round((e.cha - 70) * PK.envoyK) };
  dipHit(t, x, false); R.termsWar = aimTerms(me, t, x, e).war;
  rnd = function () { return 0.999; }; var ap0 = G.factions[me].ap, rel0 = relOf(me, t), f1 = cmdAim(b, e.id, t, x); rnd = _r;
  R.aimFail = { ok: f1.ok, s: f1.success, ap: ap0 - G.factions[me].ap, rel: relOf(me, t) - rel0, can: aimCan(me, t, x), aim: dipAimOf(t), acted: e.acted };
  G.turn += PK.aimCool; rnd = function () { return 0; }; var relx = relOf(t, x), e2 = idle()[0], f2 = cmdAim(b, e2.id, t, x); rnd = _r;
  R.aimYes = { ok: f2.ok, s: f2.success, aim: dipAimOf(t) === x, left: dipAimLeft(t), relx: relOf(t, x) - relx, can: aimCan(me, t, x), log: G.log[G.log.length - 1].t };
  G.turn += PK.aimTurns; R.aimEnd = [dipAimOf(t), dipAimLeft(t)]; G.turn -= PK.aimTurns;
  dipSign(t, x, 'truce'); R.aimVoid = dipAimOf(t); delete G.dip.pact[dipKey(t, x)];
  // ⑦ AI 끼리의 협정: 같은 큰 적을 둔 이웃끼리
  newGame(0, 7); G.aiOnly = true; N = dipNbrs();
  var A = -1, B = -1, C = -1;
  for (i = 0; i < G.factions.length && A < 0; i++) for (var j = 0; j < G.factions.length && A < 0; j++) for (var c2 = 0; c2 < G.factions.length && A < 0; c2++) if (i < j && c2 !== i && c2 !== j && dipNear(i, j, N) && dipNear(i, c2, N) && dipNear(j, c2, N)) { A = i; B = j; C = c2; }
  function pw(f, v) { var bs = facBases(f); bs.forEach(function (q, k) { q.troops = k ? 0 : v; }); facUnits(f).slice().forEach(function (u) { removeUnit(u); }); }
  for (i = 0; i < G.factions.length; i++) if (dipFac(i)) pw(i, 10000);
  R.threat0 = [dipThreat(A, N), dipThreat(B, N)];
  pw(C, 30000); R.threat1 = [dipThreat(A, N), dipThreat(B, N), dipThreat(C, N), C];
  rnd = function () { return 0.999; }; dipMonthAI(); R.pactNo = pactOn(A, B);
  rnd = function () { return 0; }; dipMonthAI(); rnd = _r;
  R.pact = { on: pactOf(A, B) && pactOf(A, B).t, left: pactLeft(A, B), strike: [aiMayStrike(A, B), aiMayStrike(B, A), aiMayStrike(A, C)], withC: pactOn(A, C) || pactOn(B, C), log: G.log[G.log.length - 1].t + '#' + G.log[G.log.length - 1].imp };
  rnd = function () { return 0; }; dipMonthAI(); rnd = _r; R.pactUp = pactOf(A, B).t;
  // 끝난 협정은 치운다
  var key = dipKey(A, B); G.dip.pact[key].until = G.turn; rnd = function () { return 0.999; }; dipMonthAI(); rnd = _r; R.clean = G.dip.pact[key] === undefined;
  // 플레이어는 끼지 않는다(사람이 두는 판)
  newGame(A, 8); G.aiOnly = false; N = dipNbrs(); for (i = 0; i < G.factions.length; i++) if (dipFac(i)) pw(i, 10000); pw(C, 30000); rnd = function () { return 0; }; dipMonthAI(); rnd = _r;
  R.noPlayer = [G.player === A, pactOn(A, B)];
  // ⑧ AI 대전 120턴: 무너지지 않고, 협정이 생기며, 협정을 맺은 사이에는 치지 않는다
  newGame(0, 12345); G.aiOnly = true; var signed = 0, hitPact = 0, asksSeen = 0, duels = 0, _ds = dipSign; dipSign = function (f, t2, k) { signed++; return _ds(f, t2, k); };
  var _ua = unitAttack; unitAttack = function (u, tg) { var tf = actTargetF(tg); if (tf >= 0 && pactOn(u.f, tf)) hitPact++; return _ua(u, tg); };
  var _uc = unitChallenge; unitChallenge = function (u, tg) { duels++; return _uc(u, tg); };
  for (var tt = 0; tt < 120; tt++) { endTurn(); if (G.asks && G.asks.length) asksSeen++; }
  dipSign = _ds; unitAttack = _ua; unitChallenge = _uc;
  R.sim = { signed: signed, hitPact: hitPact, asks: asksSeen, duels: duels, alive: G.factions.filter(function (f) { return f.alive; }).length, turn: G.turn };
  return R;
})())`, ctx));
const DK = vm.runInContext('DUEL_K', ctx), PK = vm.runInContext('DIP_K', ctx);
// ①
ok(R.want.base === true && R.want.rev === (R.want.wars[1] >= DK.aiMinWar && R.want.wars[1] - R.want.wars[0] >= DK.aiLead), '걸 마음: 여포(' + R.want.wars[0] + ') → 하후돈(' + R.want.wars[1] + ') ' + R.want.base + ', 거꾸로 ' + R.want.rev);
ok(!R.want.tired && !R.want.conf && !R.want.weak && !R.want.lower && R.want.edge && !R.want.pact, '걸지 않는 때: 기력이 모자람 · 상대가 어지러움 · 상대가 약함(무력 ' + DK.minWar + ' 아래) · 내가 ' + (-DK.aiLead) + ' 넘게 처짐 · 협정');
// ②
ok(R.ask.ok && R.ask.n === 1 && R.ask.a && R.ask.d && R.ask.done && R.ask.mor === 80 - DK.ask && R.ask.dmor === 80 && R.ask.list === 1 && R.ask.ev === 1 && /일기토를 걸어왔다.*#2/.test(R.ask.log), '내 부대에 걸면 적어 둔다(건 쪽은 기력 −' + DK.ask + ' · 행동 끝) — ' + R.ask.log);
ok(R.askTwice === false, '한 부대에는 한 번에 하나만');
ok(R.askFar[0] === 0 && /이제는 겨룰 수 없/.test(R.askFar[1]), '두 부대가 떨어지면 없던 일이 된다');
ok(R.no.ok && R.no.acc === false && R.no.mor === 80 - DK.refuse && R.no.left === 0 && /그런 신청이 없/.test(R.no.again), '응하지 않으면 내 부대의 기력 −' + DK.refuse);
ok(R.yes.ok && R.yes.acc && R.yes.kind === 'duel' && R.yes.who.every(Boolean) && R.yes.over === false && R.yes.untouched && R.yes.defer === false && R.yes.left === 0, '응하면 겨룰 판을 받는다(건 쪽이 a, 내가 d) — 아직 아무것도 입혀지지 않았다');
ok(R.fin.out && R.fin.duel && R.fin.changed && R.fin.twice === null, '겨룬 뒤 한 번만 맺는다(결과 ' + R.fin.win + ')');
// ③
ok(R.lapse.mor === DK.refuse && R.lapse.n === 0, '차례를 넘기면 응하지 않은 것으로 친다(기력 −' + DK.refuse + ')');
// ④
ok(R.turn.n === 1 && R.turn.by === '여포' && R.turn.alive && R.turn.rep >= 1, 'AI 가 제 차례에 내 부대에 일기토를 건다 → 지난 열흘의 요약에 뜬다');
// ⑤
ok(R.aiai.ok && R.aiai.asks === 0 && R.aiai.done && R.aiai.ev && R.aiai.acc && R.aiai.rec && R.aiai.duel, 'AI 끼리는 그 자리에서 정하고 저절로 겨룬다(기록이 남는다)');
ok(R.aionly[0] === true && R.aionly[1] === 0 && R.aionly[2] === true, 'AI 대전에서는 적어 두지 않는다');
// ⑥
ok(R.nb.sym && !R.nb.self, '이웃은 서로 이웃');
ok(/동맹을 맺은 세력에게만/.test(R.aimNo) && /동맹을 맺은 세력에게만/.test(R.aimTruce) && R.aimOk === '', '출병 요청은 동맹에게만(정전으로는 안 된다)');
ok((R.aimFar === 'none' || /이웃해 있지 않/.test(R.aimFar)) && R.aimSelf.every(m => /칠 상대가 아닙/.test(m)) && /협정을 맺고 있/.test(R.aimPact), '청할 수 없는 상대: 이웃하지 않은 세력 · 우리 · 동맹 자신 · 동맹과 협정 중인 세력');
ok(R.terms.q.p === R.terms.sum && R.terms.q.rel === 80 && R.terms.q.base === PK.aimBase && R.terms.q.envoy === R.terms.envoy && R.terms.q.war === 0 && R.termsWar === PK.aimWar, '받아들일 확률 = 우호 + 바탕 + 사신(매력) + 힘의 비 + 이미 싸우는 중: ' + JSON.stringify(R.terms.q));
ok(R.aimFail.ok && R.aimFail.s === false && R.aimFail.ap === 15 && R.aimFail.rel === -PK.aimRefuse && /뒤에 다시/.test(R.aimFail.can) && R.aimFail.aim === -1 && R.aimFail.acted, '거절: 우호 −' + PK.aimRefuse + ' · ' + PK.aimCool + '턴 뒤에 다시');
ok(R.aimYes.ok && R.aimYes.s && R.aimYes.aim && R.aimYes.left === PK.aimTurns && R.aimYes.relx === -PK.aimRel && /이미 .*치기로/.test(R.aimYes.can) && /치기로 했다/.test(R.aimYes.log), '받아들임: ' + PK.aimTurns + '턴 동안 그 세력을 먼저 노린다 · 둘의 우호 −' + PK.aimRel + ' — ' + R.aimYes.log);
ok(R.aimEnd[0] === -1 && R.aimEnd[1] === 0 && R.aimVoid === -1, '기간이 끝나거나 둘이 협정을 맺으면 없던 일이 된다');
// ⑦
ok(R.threat0[0] === -1 && R.threat0[1] === -1, '병력이 비슷하면 두려워할 적이 없다');
ok(R.threat1[0] === R.threat1[3] && R.threat1[1] === R.threat1[3] && R.threat1[2] === -1, '병력이 ' + PK.threat + '배 이상인 이웃이 큰 적이다');
ok(R.pactNo === false && R.pact.on === 'truce' && R.pact.left === PK.truceTurns && R.pact.strike[0] === false && R.pact.strike[1] === false && !R.pact.withC && /정전하기로 했다.*#1/.test(R.pact.log), '같은 큰 적을 둔 이웃끼리 정전한다(주사위가 맞을 때) · 서로 치지 않는다 — ' + R.pact.log);
ok(R.pactUp === 'ally' && R.clean, '정전 중이면 동맹으로 올린다 · 끝난 협정은 치운다');
ok(R.noPlayer[0] && R.noPlayer[1] === false, '사람이 두는 세력은 AI 끼리의 협정에 끼지 않는다');
// ⑧
ok(R.sim.hitPact === 0 && R.sim.turn > 100, 'AI 대전 120턴: 협정을 맺은 사이에는 치지 않는다 (맺은 협정 ' + R.sim.signed + '번 · AI 끼리의 일기토 신청 ' + R.sim.duels + '번 · 남은 세력 ' + R.sim.alive + ')');
ok(R.sim.asks === 0, 'AI 대전에서는 답을 기다리는 신청이 쌓이지 않는다');
console.log('  AI 대전 120턴: 협정 ' + R.sim.signed + ' · 일기토 신청 ' + R.sim.duels + ' · 남은 세력 ' + R.sim.alive);
console.log((fail ? 'FAIL ' : 'ok ') + pass + ' / ' + (pass + fail));
process.exit(fail ? 1 : 0);
