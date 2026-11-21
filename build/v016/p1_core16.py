#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.16 — 규칙(data.js · core.js · ai.js).   요청: "니가 제안한 b,c 하고" (b = 동맹군에 원군 요청 · AI끼리의 동맹 / c = AI가 일기토를 걸어오게)
   (1) AI 가 걸어오는 일기토: AI 부대가 옆의 부대에 일기토를 건다. 상대가 내 부대면 그 자리에서 정하지 않고 적어 두었다가(G.asks)
       내 차례에 응할지 고른다 — 응하면 화면에서 직접 겨루고(받는 쪽), 응하지 않으면 기력 −refuse. 차례를 넘기면 응하지 않은 것.
       상대가 다른 AI 면 그 자리에서 응할지(challengeChance) 정하고 저절로 겨룬다.
   (2) 출병 요청: 동맹 세력에게 "○○를 쳐 달라"고 청한다. 받아들이면 aimTurns 턴 동안 그 세력의 AI 가 그 상대의 거점을 먼저 노린다.
   (3) AI 끼리의 협정: 달이 바뀔 때, 이웃한 두 AI 세력이 같은 큰 적(둘 다와 이웃하고 병력이 threat 배 이상)을 두고 있으면 정전하고, 정전 중이면 동맹으로 올린다."""
import os, io
ROOT = os.environ.get('CH_ROOT') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
def rd(n): return io.open(os.path.join(ROOT, 'src', n), encoding='utf-8').read()
def wr(n, s): io.open(os.path.join(ROOT, 'src', n), 'w', encoding='utf-8').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:70])
    return s.replace(a, b)

# ---------- data.js ----------
s = rd('data.js')
s = rep(s, "var GAME_VERSION = 'v0.15';", "var GAME_VERSION = 'v0.16';")
s = rep(s, "  hitRel: 2, fallRel: 12, drift: 1, talkMin: 10, talkHp: 60,\n  aiAsk: 35, aiTruceRel: 45, aiAllyRel: 75, aiWeak: 0.8 };",
           "  hitRel: 2, fallRel: 12, drift: 1, talkMin: 10, talkHp: 60,\n  aiAsk: 35, aiTruceRel: 45, aiAllyRel: 75, aiWeak: 0.8,\n"
           "  /* v0.16 출병 요청: aimTurns 동안 · 받아들일 확률의 바탕 aimBase(우호에 더한다) · 사신은 매력 · 힘의 비는 동맹 ÷ 칠 상대 · 이미 그 상대와 싸우는 중이면 aimWar\n"
           "     받아들이면 동맹과 그 상대의 우호 −aimRel · AI 의 과녁 점수 +aimScore, 필요한 병력 ×aimNeed · 거절당하면 우호 −aimRefuse, aimCool 턴 뒤에 다시 */\n"
           "  aimTurns: 9, aimBase: -35, aimWar: 15, aimRel: 10, aimScore: 40, aimNeed: 0.85, aimRefuse: 2, aimCool: 6,\n"
           "  /* v0.16 AI 끼리: 같은 큰 적(병력이 threat 배 이상인 이웃)을 둔 이웃끼리 달마다 aiPact% 로 정전, 정전 중이면 aiPactUp% 로 동맹 */\n"
           "  threat: 1.4, aiPact: 25, aiPactUp: 20 };")
s = rep(s, "ask: 10, refuse: 5, accBase: 50, accK: 4, accBold: 20,", "ask: 10, refuse: 5, accBase: 50, accK: 4, accBold: 20,\n  /* v0.16 AI 가 거는 일기토: 주장의 무력이 aiMinWar 이상이고 상대보다 aiLead 넘게 낮지 않으며, 부대의 기력이 ask + aiMorale 이상일 때 aiAsk% 로 */\n  aiAsk: 30, aiLead: -3, aiMinWar: 80, aiMorale: 30,")
wr('data.js', s)

# ---------- core.js ----------
s = rd('core.js')
ASK = r'''/* ---------- AI 가 걸어오는 일기토(v0.16) ---------- */
function duelAskOk(x) { var a = UMAP[x.a], d = UMAP[x.d]; return !!a && !!d && duelBattleOk(a, d) && !a.status && !d.status && d.f === G.player; }
function duelAsks() { return G.asks ? G.asks.filter(duelAskOk) : []; }
function aiWantsDuel(u, d) {
  if (!duelBattleOk(u, d) || d.status || u.status || u.morale < DUEL_K.ask + DUEL_K.aiMorale || pactOn(u.f, d.f)) return false;
  var la = uLeader(u), ld = uLeader(d);
  return la.war >= DUEL_K.aiMinWar && la.war - ld.war >= DUEL_K.aiLead && ld.war >= DUEL_K.minWar;
}
/* AI 부대 u 가 d 에게 일기토를 건다 → 행동을 썼으면 true */
function aiChallenge(u, d) {
  if (d.f === G.player && !G.aiOnly) {
    if (!G.asks) G.asks = [];
    for (var i = 0; i < G.asks.length; i++) if (G.asks[i].d === d.id || G.asks[i].a === u.id) return false;      // 한 부대에는 한 번에 하나만
    u.morale -= DUEL_K.ask; u.done = true; u.ox = -1;
    G.asks.push({ a: u.id, d: d.id, turn: G.turn });
    logMsg(facName(u.f) + '군 ' + josa(uLeader(u).n, '이가') + ' ' + uLeader(d).n + '에게 일기토를 걸어왔다 — 내 차례에 답한다', d.c, d.r, G.player, 2);
    ev({ t: 'ask', f: u.f, id: u.id, c: u.c, r: u.r, tc: d.c, tr: d.r, name: uName(u), tname: uName(d), tf: d.f });
    return true;
  }
  var r = unitChallenge(u, { kind: 'unit', u: d, c: d.c, r: d.r });
  return !!(r && r.ok);
}
/* 걸어온 일기토에 답한다. yes → 겨룰 판(res.duelS)을 돌려준다 — 화면이 겨루고 duelFinish(S, res) 로 맺는다. no → 내 부대의 기력이 내린다 */
function duelAskAnswer(aid, did, yes) {
  var L = G.asks || [], i = -1;
  for (var j = 0; j < L.length; j++) if (L[j].a === aid && L[j].d === did) i = j;
  if (i < 0) return ERR('그런 신청이 없습니다');
  var x = L[i]; L.splice(i, 1);
  if (!duelAskOk(x)) return ERR('이제는 겨룰 수 없습니다 — 두 부대가 떨어졌거나 흩어졌습니다');
  var a = UMAP[aid], d = UMAP[did];
  if (!yes) {
    d.morale = Math.max(0, d.morale - DUEL_K.refuse);
    logMsg(josa(uLeader(d).n, '이가') + ' ' + uLeader(a).n + '의 일기토를 받지 않음 (기력 -' + DUEL_K.refuse + ')', d.c, d.r, G.player, 0);
    return { ok: true, accepted: false, mor: DUEL_K.refuse };
  }
  var res = { ok: true, kind: 'challenge', accepted: true, asked: true, c: d.c, r: d.r, ac: a.c, ar: a.r, tname: uName(d) };
  var keep = DUEL_DEFER; DUEL_DEFER = true; duelBattle(a, d, res); DUEL_DEFER = keep;
  return res;
}
/* 차례를 넘길 때: 답하지 않은 신청은 응하지 않은 것으로 친다 */
function duelAsksLapse() {
  if (!G.asks || !G.asks.length) return 0;
  var L = duelAsks(), n = 0;
  for (var i = 0; i < L.length; i++) { var r = duelAskAnswer(L[i].a, L[i].d, false); if (r.ok) n++; }
  G.asks = [];
  return n;
}
function unitChallenge0(u, t) {'''
s = rep(s, "function unitChallenge0(u, t) {", ASK)
# 차례를 넘길 때
s = rep(s, "function turnStepper() {\n  var f = -1, st = null, stage = 0;\n", "function turnStepper() {\n  if (!G.aiOnly) duelAsksLapse();                                    // v0.16: 답하지 않은 일기토 신청\n  var f = -1, st = null, stage = 0;\n")

AIM = r'''/* ---------- 출병 요청 · AI 끼리의 협정(v0.16) ---------- */
/* 세력마다 이웃한 세력(거점이 길로 이어진) */
function dipNbrs() {
  var N = {}, i, j;
  for (i = 0; i < G.bases.length; i++) {
    var b = G.bases[i]; if (b.owner < 0) continue;
    for (j = 0; j < ADJ[i].length; j++) { var o = G.bases[ADJ[i][j].to].owner; if (o >= 0 && o !== b.owner) { if (!N[b.owner]) N[b.owner] = {}; N[b.owner][o] = 1; } }
  }
  return N;
}
function dipNear(a, b, N) { N = N || dipNbrs(); return !!(N[a] && N[a][b]); }
/* 세력 f 가 두려워할 큰 적: 이웃한 세력 가운데 병력이 threat 배 이상인 가장 센 세력(없으면 -1) */
function dipThreat(f, N) {
  N = N || dipNbrs(); var pf = dipPower(f), best = -1, bp = 0;
  for (var k in N[f] || {}) { var x = +k; if (!dipFac(x)) continue; var px = dipPower(x); if (px >= pf * DIP_K.threat && px > bp) { bp = px; best = x; } }
  return best;
}
/* 세력 f 가 지금 먼저 노리기로 한 상대(출병 요청을 받아들인 것). 없으면 -1 */
function dipAimOf(f) { var D = G.dip, a = D && D.aim ? D.aim[f] : null; return a && a.until > G.turn && dipFac(a.f) && !pactOn(f, a.f) ? a.f : -1; }
function dipAimLeft(f) { var D = G.dip, a = D && D.aim ? D.aim[f] : null; return dipAimOf(f) >= 0 ? a.until - G.turn : 0; }
/* f 가 동맹 t 에게 x 를 쳐 달라고 청할 수 있는가 → '' 이면 된다 */
function aimCan(f, t, x) {
  var p = pactOf(f, t);
  if (!p || p.t !== 'ally') return '동맹을 맺은 세력에게만 청할 수 있습니다';
  if (x === f || x === t || !dipFac(x)) return '칠 상대가 아닙니다';
  if (pactOn(t, x)) return facName(t) + '군이 그 세력과 협정을 맺고 있습니다';
  if (pactOn(f, x)) return '우리가 그 세력과 협정을 맺고 있습니다';
  if (!dipNear(t, x)) return facName(t) + '군의 거점과 이웃해 있지 않습니다';
  if (dipAimOf(t) >= 0) return '이미 ' + facName(dipAimOf(t)) + '군을 치기로 했습니다 (' + dipDays(dipAimLeft(t)) + ' 남음)';
  var D = G.dip, c = D && D.cd[f + ':' + t + ':aim']; if (c && c > G.turn) return dipDays(c - G.turn) + ' 뒤에 다시 청할 수 있습니다';
  return '';
}
function aimTerms(f, t, x, o) {
  var K = DIP_K, rel = relOf(f, t), pt = dipPower(t), px = dipPower(x), rt = Math.max(1, pt) / Math.max(1, px);
  var pow = rt >= 1 ? Math.min((rt - 1) * K.powK, K.powHi) : -Math.min((1 / rt - 1) * K.powK, K.powLo), w = G.dip ? G.dip.war[dipKey(t, x)] : undefined;
  var q = { rel: rel, base: K.aimBase, envoy: Math.round(((o ? o.cha : 70) - 70) * K.envoyK), pow: Math.round(pow), war: w !== undefined && G.turn - w <= K.warTurns ? K.aimWar : 0 };
  q.p = clamp(q.rel + q.base + q.envoy + q.pow + q.war, 0, K.askHi);
  return q;
}
function cmdAim(b, id, t, x) {
  var f = b.owner, K = DIP_K, os = getIdle(b, [id]); if (!os) return ERR('보낼 무장을 고르세요');
  var why = aimCan(f, t, x); if (why) return ERR(why);
  if (!needAP(f, AP.treaty)) return ERR('행동력이 부족합니다');
  useAP(f, AP.treaty); markActed(os, 20);
  var D = dipOf(), p = aimTerms(f, t, x, os[0]).p, ok = rnd() * 100 < p;
  if (!ok) { D.cd[f + ':' + t + ':aim'] = G.turn + K.aimCool; relAdd(f, t, -K.aimRefuse); logMsg(facName(t) + '군이 출병 요청을 물리쳤다', b.c, b.r, f, 0); return { ok: true, success: false, p: p, o: os[0].id }; }
  if (!D.aim) D.aim = {};
  D.aim[t] = { f: x, until: G.turn + K.aimTurns, by: f };
  relAdd(t, x, -K.aimRel); os[0].merit += 60;
  var c = facCities(x)[0] || facBases(x)[0];
  logMsg(facName(t) + '군이 우리의 청을 받아들여 ' + facName(x) + '군을 치기로 했다 — ' + dipDays(K.aimTurns), c ? c.c : undefined, c ? c.r : undefined, f, 2);
  return { ok: true, success: true, p: p, o: os[0].id, until: D.aim[t].until };
}
/* 달이 바뀔 때: AI 끼리 — 같은 큰 적을 둔 이웃끼리 손을 잡는다 */
function dipMonthAI() {
  var D = dipOf(), K = DIP_K, N = dipNbrs(), th = {}, i, j, n = G.factions.length;
  for (var k in D.pact) { var p0 = D.pact[k]; if (p0.until <= G.turn) delete D.pact[k]; }               // 끝난 협정은 치운다
  for (i = 0; i < n; i++) if (dipFac(i)) th[i] = dipThreat(i, N);
  for (i = 0; i < n; i++) for (j = i + 1; j < n; j++) {
    if (!dipFac(i) || !dipFac(j)) continue;
    if (!G.aiOnly && (i === G.player || j === G.player)) continue;
    var x = th[i]; if (x < 0 || x !== th[j] || x === i || x === j || !dipNear(i, j, N)) continue;
    if (pactOn(i, x) || pactOn(j, x)) continue;
    var p = pactOf(i, j);
    if (!p) { if (K.aiPact > 0 && rnd() * 100 < K.aiPact) dipSign(i, j, 'truce'); }
    else if (p.t === 'truce' && K.aiPactUp > 0 && rnd() * 100 < K.aiPactUp) dipSign(i, j, 'ally');
  }
}
'''
s = rep(s, "/* 달이 바뀔 때: 우호가 처음 값 쪽으로 한 칸 돌아가고(협정 중인 사이는 그대로), 끝난 협정을 알리고, AI 가 플레이어에게 청해 온다 */", AIM + "/* 달이 바뀔 때: 우호가 처음 값 쪽으로 한 칸 돌아가고(협정 중인 사이는 그대로), 끝난 협정을 알리고, AI 가 플레이어에게 청해 온다 */")
# dipMonth: AI 끼리의 협정을 먼저(AI 대전에서도 돈다)
s = rep(s, "  D.offers = [];\n  if (G.aiOnly || !dipFac(G.player)) return;\n", "  D.offers = [];\n  dipMonthAI();                                                    // v0.16: AI 끼리의 협정(AI 대전에서도)\n  if (G.aiOnly || !dipFac(G.player)) return;\n")
# 협정을 알리는 글: 내가 끼지 않은 것은 '천하의 움직임'으로
s = rep(s, "logMsg(facName(f) + '군과 ' + facName(t) + '군이 ' + (kind === 'ally' ? '동맹을 맺었다' : '정전하기로 했다') + ' — ' + dipDays(D.pact[dipKey(f, t)].until - G.turn), c ? c.c : undefined, c ? c.r : undefined, f === G.player || t === G.player ? G.player : f, 2);",
           "var mine = !G.aiOnly && (f === G.player || t === G.player);\n  logMsg(facName(f) + '군과 ' + facName(t) + '군이 ' + (kind === 'ally' ? '동맹을 맺었다' : '정전하기로 했다') + ' — ' + dipDays(D.pact[dipKey(f, t)].until - G.turn), c ? c.c : undefined, c ? c.r : undefined, mine ? G.player : f, mine ? 2 : 1);")
wr('core.js', s)

# ---------- ai.js ----------
s = rd('ai.js')
s = rep(s, "    var tgt = { kind: 'unit', u: tg, c: tg.c, r: tg.r };\n    // 계략\n",
           "    var tgt = { kind: 'unit', u: tg, c: tg.c, r: tg.r };\n    // v0.16: 일기토를 건다(주장의 무력이 높고 상대와 겨룰 만할 때)\n    if (DUEL_K.aiAsk > 0 && aiWantsDuel(u, tg) && chance(DUEL_K.aiAsk) && aiChallenge(u, tg)) return;\n    // 계략\n")
s = rep(s, "        sc = 50 - def / 400 - len * 0.5 + (T.kind === 'city' ? 15 : 0) + (T.sz === 'L' ? 8 : 0);      // v0.8.1: 플레이어의 성에 주던 가산점(+3)을 없앰\n",
           "        sc = 50 - def / 400 - len * 0.5 + (T.kind === 'city' ? 15 : 0) + (T.sz === 'L' ? 8 : 0);      // v0.8.1: 플레이어의 성에 주던 가산점(+3)을 없앰\n        if (!AISCOPE && dipAimOf(f) === T.owner) { sc += DIP_K.aimScore; need *= DIP_K.aimNeed; }      // v0.16: 동맹의 청을 받아 먼저 노리는 상대\n")
wr('ai.js', s)
print('p1_core16 ok')
