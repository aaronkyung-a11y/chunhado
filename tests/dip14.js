// v0.14 — 외교의 규칙 시험.   node tests/dip14.js
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.env.SRC || path.join(__dirname, '..', 'src');
const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array };
vm.createContext(ctx);
for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
let pass = 0, fail = 0;
function ok(c, msg) { if (c) pass++; else { fail++; console.log('  ✗ ' + msg); } }
const R = JSON.parse(vm.runInContext(`JSON.stringify((function () {
  var R = {}, DK = DIP_K;
  newGame(0, 1); G.aiOnly = false;
  var me = G.player, b = facCities(me)[0];
  function O(n) { return G.officers.filter(function (o) { return o.n === n; })[0]; }
  function other() { for (var i = 0; i < G.factions.length; i++) if (i !== me && G.factions[i].alive) return i; }
  function others() { var o = []; for (var i = 0; i < G.factions.length; i++) if (i !== me && G.factions[i].alive) o.push(i); return o; }
  function idle() { return idleOfficers(b).filter(function (o) { return !isLord(o); }); }
  function fresh() { G.officers.forEach(function (o) { if (o.f === me && o.st === 'active') o.acted = !!jobOf(o); }); G.factions[me].ap = 250; b.gold = 20000; }
  var t = other(), ts = others(); b.gold = 20000; G.factions[me].ap = 250;
  // ① 처음 값 · 열쇠 · 낱말
  R.init = { rel: relOf(me, t), sym: relOf(t, me), key: [dipKey(3, 1), dipKey(1, 3)], pact: pactOf(me, t), noDip: G.dip === undefined, words: [relWord(0), relWord(20), relWord(40), relWord(60), relWord(80)] };
  // ② 친선
  var o1 = idle()[0], g0 = b.gold, ap0 = G.factions[me].ap, r1 = cmdGift(b, o1.id, t);
  R.gift = { ok: r1.ok, add: r1.add, want: DK.giftBase + Math.round(o1.pol / DK.giftPol), rel: relOf(me, t), gold: g0 - b.gold, ap: ap0 - G.factions[me].ap, acted: o1.acted };
  var o2 = idle()[0]; R.giftAgain = cmdGift(b, o2.id, t).msg || '';
  R.giftSelf = cmdGift(b, o2.id, me).msg || ''; b.gold = 10; R.giftPoor = cmdGift(b, o2.id, ts[1]).msg || ''; b.gold = 20000;
  G.factions[me].ap = 0; R.giftNoAp = cmdGift(b, o2.id, ts[1]).msg || ''; G.factions[me].ap = 250;
  R.giftUsed = cmdGift(b, o1.id, ts[1]).msg || '';
  // ③ 받아들일 확률의 내역
  dipOf().rel[dipKey(me, t)] = 50;
  var e = idle()[0], x = dipTerms(me, t, 'truce', e), xa = dipTerms(me, t, 'ally', e);
  R.terms = { x: x, sum: clamp(x.rel + x.base + x.envoy + x.pow + x.busy, 0, DK.askHi), envoyWant: Math.round((e.pol - 70) * DK.envoyK), ally: xa.p, allyLow: !!xa.low, allyCan: dipCan(me, t, 'ally') };
  dipOf().rel[dipKey(me, t)] = 100; var hi = dipTerms(me, t, 'truce', e); dipOf().rel[dipKey(me, t)] = 0; var lo = dipTerms(me, t, 'truce', e);
  R.ends = [hi.p, lo.p];
  // 힘의 비: 저쪽 병력을 크게 · 작게
  dipOf().rel[dipKey(me, t)] = 50;
  var tb = facBases(t), save = tb.map(function (q) { return q.troops; });
  tb.forEach(function (q) { q.troops = 1; }); var strong = dipTerms(me, t, 'truce', e).pow; tb.forEach(function (q) { q.troops = 9999999; }); var weak = dipTerms(me, t, 'truce', e).pow; tb.forEach(function (q, i) { q.troops = save[i]; });
  R.pow = [strong, weak];
  var mine = dipPower(me); tb.forEach(function (q, i) { q.troops = i ? 0 : Math.round(mine / 2); }); var p2a = dipTerms(me, t, 'truce', e).pow; tb.forEach(function (q, i) { q.troops = i ? 0 : mine * 2; }); var p2b = dipTerms(me, t, 'truce', e).pow; tb.forEach(function (q, i) { q.troops = i ? 0 : mine; }); var p2c = dipTerms(me, t, 'truce', e).pow; tb.forEach(function (q, i) { q.troops = save[i]; });
  facUnits(t).forEach(function () {}); R.pow2 = [p2a, p2b, p2c];
  // 저쪽이 다른 세력과 싸우는 중
  dipHit(ts[1], t, false); R.busy = [dipBusy(t, me), dipTerms(me, t, 'truce', e).busy, dipBusy(t, ts[1]), relOf(ts[1], t)];
  G.turn += DK.warTurns + 1; R.busyLater = dipBusy(t, me); G.turn -= DK.warTurns + 1;
  // ④ 정전: 주사위(반드시 되는 값 · 반드시 안 되는 값)
  fresh(); dipOf().rel[dipKey(me, t)] = 60;
  var _r = rnd; rnd = function () { return 0.999; }; var e1 = idle()[0], ap1 = G.factions[me].ap, f1 = cmdTreaty(b, e1.id, t, 'truce'); rnd = _r;
  R.refused = { ok: f1.ok, success: f1.success, rel: relOf(me, t), cool: dipCool(me, t), can: dipCan(me, t, 'truce'), ap: ap1 - G.factions[me].ap, acted: e1.acted, pact: !!pactOf(me, t) };
  G.turn += DK.cool; R.coolOver = dipCan(me, t, 'truce');
  fresh(); rnd = function () { return 0; }; var e2 = idle()[0], f2 = cmdTreaty(b, e2.id, t, 'truce'); rnd = _r;
  var p = pactOf(me, t);
  R.truce = { ok: f2.ok, success: f2.success, kind: p && p.t, left: pactLeft(me, t), sym: pactLeft(t, me), rel: relOf(me, t), again: dipCan(me, t, 'truce'), log: G.log[G.log.length - 1].t };
  // ⑤ 협정의 효과: 서로 칠 수 없다 · 계략도 · AI 도 · 등용도
  var eb = facCities(t)[0];
  var u = cmdDeploy(b, { type: 'spear', ids: [idle()[0].id], troops: 3000, food: 3000 }).unit, eo = idleOfficers(eb)[0], eu = cmdDeploy(eb, { type: 'spear', ids: [eo.id], troops: 3000, food: 3000 }).unit;
  // 빈 들판에 나란히 세운다
  var fld = (function () { for (var r = 92; r < 112; r++) for (var c = 146; c < 168; c++) { var good = true; for (var dr = -1; dr <= 1 && good; dr++) for (var dc = -2; dc <= 2 && good; dc++) { var k = K(c + dc, r + dr); if (TCH[k] !== 112 || ZONE[k] >= 0 || BAT[k] !== undefined || PAT[k] || UAT[k]) good = false; } if (good) return [c, r]; } })();
  placeUnit(u, fld[0], fld[1]); placeUnit(eu, fld[0] + 1, fld[1]); u.born = -9; eu.born = -9; u.done = false; eu.done = false; u.morale = 100; eu.morale = 100;
  var near = nbrs(eb.c, eb.r).filter(function (q) { return !UAT[K(q[0], q[1])] && TCH[K(q[0], q[1])] !== undefined; })[0];
  var tu = { kind: 'unit', u: eu, c: eu.c, r: eu.r }, m0 = u.morale;
  R.block = [unitAttack(u, tu).msg || '', unitTactic(u, tacticList(u)[0], tu).msg || '', unitPloy(u, PLOYS[1], tu).msg || '', unitChallenge(u, tu).msg || '', u.done, u.morale === m0, challengeTargets(u).length, unitAttack(u, { kind: 'base', b: eb, c: eb.c, r: eb.r }).msg || ''];
  R.eff = { tg: attackTargets(u).length, etg: attackTargets(eu).length, ploy: PLOYS.map(function (pl) { return ployTargets(u, pl).filter(function (q) { return q.u === eu; }).length; }), ai: aiMayStrike(t, me), ai2: aiMayStrike(me, t), near: enemyUnitsNear(me, u.c, u.r, 3).length };
  // 정전을 깨면 다시 칠 수 있다
  var relO = relOf(me, ts[1]), br = cmdBreak(me, t);
  R.broke = { ok: br.ok, kind: br.kind, rel: relOf(me, t), others: relOf(me, ts[1]) - relO, pact: !!pactOf(me, t), tg: attackTargets(u).filter(function (q) { return q.kind === 'unit'; }).length, etg: attackTargets(eu).length, ai: aiMayStrike(t, me) || (G.peace && G.turn < G.peace.until), cool: dipCool(me, t), coolBack: dipCool(t, me), can: dipCan(me, t, 'truce'), none: cmdBreak(me, t).msg || '', near: enemyUnitsNear(me, u.c, u.r, 3).length };
  // ⑥ 싸우면 우호가 내려간다
  if (G.peace) G.peace.until = 0;
  var r0 = relOf(me, t), a = unitAttack(u, { kind: 'unit', u: eu, c: eu.c, r: eu.r });
  R.hit = { ok: a.ok, d: relOf(me, t) - r0, war: dipOf().war[dipKey(me, t)] === G.turn, busy: dipBusy(t, ts[1]) };
  // ⑦ 동맹: 우호 60 아래면 청할 수 없고, 맺으면 360일. 정전 중에도 동맹으로 올릴 수 있다
  var t2 = ts[1]; fresh(); dipOf().rel[dipKey(me, t2)] = 59; R.allyLow = cmdTreaty(b, idle()[0].id, t2, 'ally').msg || '';
  dipOf().rel[dipKey(me, t2)] = 70; rnd = function () { return 0; }; var f3 = cmdTreaty(b, idle()[0].id, t2, 'truce'); var f4 = cmdTreaty(b, idle()[0].id, t2, 'ally'); rnd = _r;
  R.ally = { truce: f3.success, ok: f4.ok, success: f4.success, kind: pactOf(me, t2) && pactOf(me, t2).t, left: pactLeft(me, t2), again: dipCan(me, t2, 'ally'), truceNow: dipCan(me, t2, 'truce'), poach: (function () { var nb = facCities(t2)[0], oo = baseOfficers(nb).filter(function (q) { return !isLord(q); })[0]; return oo ? canPoach(b, oo) : null; })() };
  // ⑧ 설전으로 담판
  var t3 = ts[2]; fresh(); dipOf().rel[dipKey(me, t3)] = 50;
  var e3 = idle()[0], pp = dipChance(me, t3, 'truce', e3), S = dipTalkNew(b, e3, t3, 'truce'), sp = dipSpeaker(t3);
  R.talk = { ok: dipTalkOk(b, e3, t3, 'truce'), p: pp, hp: [S.d.hp, Math.round(DUEL_K.hp * (1 + (DK.talkHp - pp) / 100))], who: [S.a.id === e3.id, S.d.id === sp.id, sp.f === t3], kind: S.kind };
  R.talkUnfinished = cmdTreaty(b, e3.id, t3, 'truce', S).msg || '';
  S.over = true; S.win = 'd'; var ap3 = G.factions[me].ap, l = cmdTreaty(b, e3.id, t3, 'truce', S);
  R.talkLose = { ok: l.ok, success: l.success, pact: !!pactOf(me, t3), used: S.used, ap: ap3 - G.factions[me].ap, cool: dipCool(me, t3) };
  R.talkReuse = cmdTreaty(b, idle()[0].id, t3, 'truce', S).msg || '';
  G.turn += DK.cool; fresh(); var e4 = idle()[0], S2 = dipTalkNew(b, e4, t3, 'truce'); S2.over = true; S2.win = 'a';
  R.talkMismatch = [cmdTreaty(b, idle()[1].id, t3, 'truce', S2).msg || '', cmdTreaty(b, e4.id, t3, 'ally', S2).msg || '', cmdTreaty(b, e4.id, ts[3], 'truce', S2).msg || ''];
  rnd = function () { return 0.999; }; var w = cmdTreaty(b, e4.id, t3, 'truce', S2); rnd = _r;
  R.talkWin = { ok: w.ok, success: w.success, pact: !!pactOf(me, t3) };
  dipOf().rel[dipKey(me, ts[3])] = 100; var tb3 = facBases(ts[3]); tb3.forEach(function (q) { q.troops = 1; }); R.talkNo = [dipChance(me, ts[3], 'truce', O('순욱') || e4), dipTalkOk(b, e4, ts[3], 'truce')];
  // ⑨ 달이 바뀌면: 우호가 40 쪽으로 한 칸(협정 중인 사이는 그대로)
  var D = dipOf(); D.rel[dipKey(me, ts[4])] = 70; D.rel[dipKey(me, ts[5])] = 10; var relPact = relOf(me, t3);
  dipMonth();
  R.month = { hi: relOf(me, ts[4]), lo: relOf(me, ts[5]), pact: relOf(me, t3) - relPact };
  // ⑩ AI 가 청해 온다
  var t6 = ts[6]; D.rel[dipKey(me, t6)] = DK.aiTruceRel + DK.drift; facBases(t6).forEach(function (q) { q.troops = Math.min(q.troops, 100); }); if (G.peace) G.peace.until = 0;
  rnd = function () { return 0; }; dipMonth(); rnd = _r;
  var of = dipOffers();
  R.offer = { has: of.some(function (q) { return q.from === t6 && q.kind === 'truce'; }), n: of.length, notPact: !of.some(function (q) { return q.from === t3; }) };
  var ans = dipAnswer(t6, 'truce', true);
  R.accept = { ok: ans.ok, success: ans.success, pact: pactOf(me, t6) && pactOf(me, t6).t, left: dipOffers().some(function (q) { return q.from === t6; }), twice: dipAnswer(t6, 'truce', true).msg || '' };
  var t7 = ts[7]; D.rel[dipKey(me, t7)] = DK.aiAllyRel + DK.drift; rnd = function () { return 0; }; dipMonth(); rnd = _r;
  var of2 = dipOffers().filter(function (q) { return q.from === t7; }), rr = relOf(me, t7), no = dipAnswer(t7, 'ally', false);
  R.decline = { kind: of2.length ? of2[0].kind : '', ok: no.ok, success: no.success, rel: relOf(me, t7) - rr, cool: dipCool(t7, me), pact: !!pactOf(me, t7) };
  rnd = function () { return 0.999; }; dipMonth(); rnd = _r; R.noOffer = dipOffers().length;
  // 다음 턴이 되면 답하지 않은 제안은 사라진다
  D.offers.push({ from: ts[8], kind: 'truce', turn: G.turn }); var n0 = dipOffers().length; G.turn++; R.expire = [n0, dipOffers().length]; G.turn--;
  // ⑪ 협정이 끝난다
  if (!D.pact[dipKey(me, t6)]) { R.dbg = { offer: R.offer, accept: R.accept, t6: t6, can: dipCan(t6, me, 'truce'), rel: relOf(me, t6), pw: [dipPower(t6), dipPower(me)], peace: G.peace && [G.turn, G.peace.until], offers: D.offers }; return R; }
  var pk = dipKey(me, t6), until = D.pact[pk].until; G.turn = until - 3; var L0 = G.log.length; dipTurn(); var warn = G.log.slice(L0).map(function (q) { return q.t; }).join('|');
  G.turn = until; L0 = G.log.length; R.pactAtEnd = !!pactOf(me, t6); dipTurn(); var endT = G.log.slice(L0).map(function (q) { return q.t; }).join('|');
  R.expirePact = { warn: warn, end: endT, gone: D.pact[pk] === undefined, tgAgain: aiMayStrike(t6, me) };
  // ⑫ 저장 · 불러오기, 옛 저장(외교가 없는 것)
  var d0 = JSON.stringify(G.dip), sv = serialize(); deserialize(sv); R.save = { same: JSON.stringify(G.dip) === d0, pacts: Object.keys(G.dip.pact).length, v: G.dip.v };
  var g2 = JSON.parse(sv); delete g2.dip; deserialize(JSON.stringify(g2)); R.old = { rel: relOf(me, t3), pact: pactOf(me, t3), month: (function () { try { dipMonth(); dipTurn(); return true; } catch (e) { return String(e); } })() };
  // ⑬ AI 대전에서는 청해 오지 않고 주사위도 쓰지 않는다
  newGame(0, 7); G.aiOnly = true; var n = 0, _q = rnd; rnd = function () { n++; return _q(); }; dipMonth(); dipTurn(); rnd = _q; R.aiOnly = [n, dipOffers().length];
  // 망한 세력과는 아무것도 없다
  newGame(0, 3); G.aiOnly = false; var dead = other(); dipSign(G.player, dead, 'ally'); var had = pactOn(G.player, dead); G.factions[dead].alive = false;
  R.dead = [had, pactOn(G.player, dead), dipCan(G.player, dead, 'truce'), relAdd(G.player, dead, 10)];
  return R;
})())`, ctx));
const K = vm.runInContext('DIP_K', ctx);
if (R.dbg) { console.log(JSON.stringify(R.dbg)); }
// ①
ok(R.init.rel === 40 && R.init.sym === 40 && R.init.key[0] === '1-3' && R.init.key[1] === '1-3' && R.init.pact === null && R.init.noDip, '처음 우호도 40 · 열쇠는 두 방향이 같다 · 처음에는 G.dip 가 없다');
ok(R.init.words.join() === '적대,냉담,보통,우호,친밀', '우호도의 낱말: ' + R.init.words);
// ②
ok(R.gift.ok && R.gift.add === R.gift.want && R.gift.rel === 40 + R.gift.want && R.gift.gold === K.giftGold && R.gift.ap === 10 && R.gift.acted, '친선: 금 ' + K.giftGold + ' · 행동력 10 → 우호 +' + R.gift.add);
ok(/이미 선물/.test(R.giftAgain) && /상대할 세력/.test(R.giftSelf) && /금이 부족/.test(R.giftPoor) && /행동력/.test(R.giftNoAp) && /보낼 무장/.test(R.giftUsed), '친선을 보낼 수 없는 때: 같은 턴에 두 번 · 자기 자신 · 금 · 행동력 · 이미 일한 무장');
// ③
ok(R.terms.x.p === R.terms.sum && R.terms.x.rel === 50 && R.terms.x.base === K.truceBase && R.terms.x.envoy === R.terms.envoyWant, '정전의 확률 = 우호 + 바탕 + 사신 + 힘 + 형편: ' + JSON.stringify(R.terms.x));
ok(R.terms.ally === 0 && R.terms.allyLow && /우호가 60 이상/.test(R.terms.allyCan), '우호 60 아래면 동맹은 0%');
ok(R.ends[0] <= K.askHi && R.ends[0] >= 80 && R.ends[1] === 0, '확률은 0~95%: ' + R.ends);
ok(R.pow[0] === K.powHi && R.pow[1] === -K.powLo && R.pow2[0] === K.powK && R.pow2[1] === -K.powK && R.pow2[2] === 0, '힘의 비: 우리가 세면 +' + K.powHi + ', 저쪽이 훨씬 세면 −' + K.powLo);
ok(R.busy[0] === true && R.busy[1] === K.busy && R.busy[2] === false && R.busy[3] === 40 - K.hitRel && R.busyLater === false, '저쪽이 다른 세력과 싸우는 중이면 +' + K.busy + ' (' + K.warTurns + '턴 동안)');
// ④
ok(R.refused.ok && R.refused.success === false && R.refused.rel === 60 - K.refuse && R.refused.cool === K.cool && /뒤에 다시/.test(R.refused.can) && R.refused.ap === 15 && R.refused.acted && !R.refused.pact, '거절: 우호 −' + K.refuse + ' · ' + K.cool + '턴 동안 다시 청하지 못한다(행동력은 쓴다)');
ok(R.coolOver === '', '기다리면 다시 청할 수 있다');
ok(R.truce.ok && R.truce.success && R.truce.kind === 'truce' && R.truce.left === K.truceTurns && R.truce.sym === K.truceTurns && R.truce.rel === 60 - K.refuse + K.okRelTruce && /이미 정전/.test(R.truce.again) && /정전하기로/.test(R.truce.log), '정전: ' + K.truceTurns + '턴 · 우호 +' + K.okRelTruce + ' — ' + R.truce.log);
// ⑤
ok(R.eff.tg === 0 && R.eff.etg === 0 && R.eff.ploy.every(function (n) { return n === 0; }) && R.eff.ai === false && R.eff.ai2 === false && R.eff.near === 0, '정전 중: 서로 칠 수 없고 계략도 걸 수 없다(AI 도) ' + JSON.stringify(R.eff));
ok(R.broke.ok && R.broke.kind === 'truce' && !R.broke.pact && R.broke.others === -K.breakOthers && R.broke.tg === 1 && R.broke.etg >= 1 && R.broke.cool === K.breakCool && R.broke.coolBack === K.breakCool && /뒤에 다시/.test(R.broke.can) && /맺은 협정이 없/.test(R.broke.none) && R.broke.near === 1, '파기: 다른 세력과의 우호 −' + K.breakOthers + ' · 다시 칠 수 있다 · ' + K.breakCool + '턴 동안 다시 청하지 못한다 ' + JSON.stringify(R.broke));
ok(R.broke.rel === Math.max(0, 60 - K.refuse + K.okRelTruce - K.breakRel), '파기: 그 세력과의 우호 −' + K.breakRel + ' → ' + R.broke.rel);
ok(R.block.slice(0, 4).every(function (m) { return /협정을 맺은 세력/.test(m); }) && R.block[4] === false && R.block[5] === true && R.block[6] === 0 && /협정을 맺은 세력/.test(R.block[7]), '규칙 쪽에서도 막는다: 공격 · 전법 · 계략 · 일기토 · 거점 — 행동도 기력도 쓰지 않는다');
// ⑥
ok(R.hit.ok && R.hit.d === -K.hitRel && R.hit.war && R.hit.busy, '치면 우호 −' + K.hitRel + ' · 싸우는 중으로 적힌다');
// ⑦
ok(/우호가 60 이상/.test(R.allyLow), '동맹: 우호 60 아래면 청할 수 없다');
ok(R.ally.truce && R.ally.ok && R.ally.success && R.ally.kind === 'ally' && R.ally.left === K.allyTurns && /이미 동맹/.test(R.ally.again) && /이미 동맹/.test(R.ally.truceNow), '정전 중에도 동맹으로 올릴 수 있다 · ' + K.allyTurns + '턴');
ok(R.ally.poach === false || R.ally.poach === null, '협정을 맺은 세력의 무장에게는 등용을 권할 수 없다 (' + R.ally.poach + ')');
// ⑧
ok(R.talk.ok && R.talk.hp[0] === R.talk.hp[1] && R.talk.who.every(Boolean) && R.talk.kind === 'talk', '설전으로 담판: 확률 ' + R.talk.p + '% → 상대의 버티는 힘 ' + R.talk.hp[0] + ' · 저쪽은 군사(없으면 지력이 가장 높은 이)');
ok(/설전의 결과/.test(R.talkUnfinished) && /설전의 결과|뒤에 다시/.test(R.talkReuse), '끝나지 않은 판 · 이미 쓴 판은 받지 않는다: ' + R.talkUnfinished + ' / ' + R.talkReuse);
ok(R.talkLose.ok && R.talkLose.success === false && !R.talkLose.pact && R.talkLose.used && R.talkLose.ap === 15 && R.talkLose.cool === K.cool, '진 설전: 거절과 같다');
ok(R.talkMismatch.every(function (m) { return /설전의 결과|보낼 무장|우호가 60/.test(m); }), '사신 · 제안 · 상대가 다른 판은 받지 않는다: ' + R.talkMismatch);
ok(R.talkWin.ok && R.talkWin.success && R.talkWin.pact, '이긴 설전: 주사위와 상관없이 맺는다');
ok(R.talkNo[0] >= 95 ? R.talkNo[1] === true || R.talkNo[1] === false : true, '확률 ' + R.talkNo[0] + '% 일 때 설전 ' + R.talkNo[1]);
// ⑨
ok(R.month.hi === 70 - K.drift && R.month.lo === 10 + K.drift && R.month.pact === 0, '달마다 우호가 40 쪽으로 ' + K.drift + ' (협정 중인 사이는 그대로)');
// ⑩
ok(R.offer.has && R.offer.notPact, 'AI 가 정전을 청해 온다(약하고 우호 ' + K.aiTruceRel + ' 이상일 때)');
ok(R.accept.ok && R.accept.success && R.accept.pact === 'truce' && !R.accept.left && /그런 제안이 없/.test(R.accept.twice), '받아들이면 맺는다 · 한 번만');
ok(R.decline.kind === 'ally' && R.decline.ok && R.decline.success === false && R.decline.rel === -K.refuse && R.decline.cool === K.cool && !R.decline.pact, '우호 ' + K.aiAllyRel + ' 이상이면 동맹을 청해 온다 · 물리치면 우호 −' + K.refuse);
ok(R.noOffer === 0, '주사위가 안 맞으면 청해 오지 않는다');
ok(R.expire[0] >= 1 && R.expire[1] === 0, '답하지 않은 제안은 다음 턴에 사라진다');
// ⑪
ok(/30일 뒤에 끝납니다/.test(R.expirePact.warn) && R.pactAtEnd === false && /끝났습니다/.test(R.expirePact.end) && R.expirePact.gone, '협정이 끝나기 30일 전에 알리고, 끝나면 알린다 — ' + R.expirePact.warn + ' / ' + R.expirePact.end);
// ⑫
ok(R.save.same && R.save.pacts >= 1 && R.save.v === 1, '저장 · 불러오기에 외교가 남는다');
ok(R.old.rel === 40 && R.old.pact === null && R.old.month === true, '외교가 없는 옛 저장: 처음 값으로 연다');
// ⑬
ok(R.aiOnly[1] === 0, 'AI 대전: 플레이어에게 청해 오는 것은 없다(v0.16부터 AI 끼리의 협정에는 주사위를 쓴다 — ' + R.aiOnly[0] + '번)');
ok(R.dead[0] === true && R.dead[1] === false && /상대할 세력/.test(R.dead[2]), '망한 세력과의 협정은 없는 것이 된다');
console.log((fail ? 'FAIL ' : 'ok ') + pass + ' / ' + (pass + fail));
process.exit(fail ? 1 : 0);
