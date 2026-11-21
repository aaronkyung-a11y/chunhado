#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.14 — 외교의 규칙(core.js · data.js · ai.js). 화면은 p2_dip_ui.py.
   · 우호도(0~100, 처음 40): 세력 둘 사이의 값. 친선(선물)으로 오르고, 치면 내려가고, 달마다 40 쪽으로 한 칸씩 돌아간다.
   · 협정: 정전(180일) · 동맹(360일, 우호 60 이상). 협정을 맺은 세력의 부대 · 거점 · 시설은 칠 수 없고 계략도 걸 수 없다(AI 도 마찬가지).
   · 제안은 무장을 사신으로 보낸다. 받아들일 확률 = 우호도 + 사신의 능력 + 힘의 비 + 저쪽의 형편. 주사위 대신 설전으로 담판할 수 있다.
   · 파기: 그 세력과의 우호 −40, 다른 모든 세력과의 우호 −10, 180일 동안 그 세력에 다시 제안하지 못한다.
   · AI 는 달마다 플레이어에게 정전 · 동맹을 청해 올 수 있다(G.dip.offers). AI 끼리는 협정을 맺지 않는다(이 판).
   저장: G.dip 가 없으면 그 자리에서 만든다(옛 저장을 그대로 연다)."""
import os, io
ROOT = os.environ.get('CH_ROOT') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')      # CH_ROOT: 다른 작업 폴더에 입힐 때
def rd(n): return io.open(os.path.join(ROOT, 'src', n), encoding='utf-8').read()
def wr(n, s): io.open(os.path.join(ROOT, 'src', n), 'w', encoding='utf-8').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:70])
    return s.replace(a, b)

# ---------- data.js ----------
s = rd('data.js')
s = rep(s, "var GAME_VERSION = 'v0.13';", "var GAME_VERSION = 'v0.14';")
s = rep(s, "var AP = { develop: 20, merge: 20, draft: 20, patrol: 15, train: 15, produce: 20, trade: 10, search: 15, recruit: 15, reward: 5, move: 10, deploy: 10 };",
           "var AP = { develop: 20, merge: 20, draft: 20, patrol: 15, train: 15, produce: 20, trade: 10, search: 15, recruit: 15, reward: 5, move: 10, deploy: 10, gift: 10, treaty: 15 };\n"
           "/* 외교(v0.14)\n"
           "   rel0 처음 우호도 · gift* 친선(금 giftGold → 우호 + giftBase + 사신의 정치 ÷ giftPol, 한 세력에 턴마다 한 번)\n"
           "   truce/ally: 기간(턴) · 받아들일 확률의 바탕(우호도에 더하는 값) · 동맹은 우호 allyRel 이상이어야 청할 수 있다\n"
           "   envoyK 사신의 능력(정전 = 정치, 동맹 = 매력)이 70 을 넘는 만큼 × 이 값 · powK 힘의 비: 우리가 두 배면 +powK(+powHi 까지), 저쪽이 두 배면 −powK(−powLo 까지) · busy 저쪽이 다른 세력과 싸우는 중이면 더하는 값(warTurns 턴 안에 맞았으면)\n"
           "   okRel 맺으면 오르는 우호 · refuse 거절당하면 내리는 우호 · cool 다시 청할 수 있을 때까지(턴)\n"
           "   break* 파기: 그 세력과의 우호 · 다른 모든 세력과의 우호 · 그 세력에 다시 청하지 못하는 턴\n"
           "   hitRel 칠 때마다 · fallRel 거점을 빼앗으면 · drift 달마다 rel0 쪽으로\n"
           "   talkMin 설전을 걸 수 있는 가장 낮은 확률 · talkHp 상대의 버티는 힘이 100 이 되는 확률(등용의 설전과 같은 꼴)\n"
           "   ai*: AI 가 플레이어에게 청해 오는 것 — 달마다 aiAsk% 로, 정전은 우호 aiTruceRel 이상이면서 플레이어보다 약하거나(힘이 aiWeak 배 아래) 다른 싸움에 바쁠 때, 동맹은 우호 aiAllyRel 이상일 때 */\n"
           "var DIP_K = { rel0: 40, giftGold: 1000, giftBase: 8, giftPol: 10,\n"
           "  truceTurns: 18, allyTurns: 36, truceBase: -15, allyBase: -40, allyRel: 60, envoyK: 0.4, powK: 20, powLo: 25, powHi: 20, busy: 15, warTurns: 6, askHi: 95,\n"
           "  okRelTruce: 5, okRelAlly: 10, refuse: 3, cool: 6, breakRel: 40, breakOthers: 10, breakCool: 18,\n"
           "  hitRel: 2, fallRel: 12, drift: 1, talkMin: 10, talkHp: 60,\n"
           "  aiAsk: 35, aiTruceRel: 45, aiAllyRel: 75, aiWeak: 0.8 };\n"
           "var PACT_NAME = { truce: '정전', ally: '동맹' };")
wr('data.js', s)

# ---------- core.js ----------
s = rd('core.js')
DIP = r'''
/* ================= 외교(v0.14) =================
   G.dip = { rel: { 'a-b': 우호도 }, pact: { 'a-b': { t: 'truce' | 'ally', until: 턴, by: 청한 세력 } }, cd: { 'f:t': 다시 청할 수 있는 턴 }, gift: { 'f:t': 선물한 턴 },
             war: { 'a-b': 마지막으로 서로 친 턴 }, offers: [{ from, kind, turn }] (AI 가 플레이어에게 청해 온 것 — 그 턴에만 살아 있다) } */
function dipInit() { return { rel: {}, pact: {}, cd: {}, gift: {}, war: {}, offers: [], v: 1 }; }
function dipOf() { if (!G.dip) G.dip = dipInit(); return G.dip; }
function dipKey(a, b) { return a < b ? a + '-' + b : b + '-' + a; }
function dipFac(f) { return f >= 0 && !!G.factions[f] && G.factions[f].alive; }
function relOf(a, b) { if (!G.dip) return DIP_K.rel0; var v = G.dip.rel[dipKey(a, b)]; return v === undefined ? DIP_K.rel0 : v; }
function relAdd(a, b, d) { if (a === b || !dipFac(a) || !dipFac(b)) return relOf(a, b); var D = dipOf(), v = clamp(Math.round(relOf(a, b) + d), 0, 100); D.rel[dipKey(a, b)] = v; return v; }
function relWord(v) { return v >= 80 ? '친밀' : (v >= 60 ? '우호' : (v >= 40 ? '보통' : (v >= 20 ? '냉담' : '적대'))); }
/* 두 세력 사이에 살아 있는 협정(없으면 null) */
function pactOf(a, b) {
  if (!G.dip || a === b || a < 0 || b < 0) return null;
  var p = G.dip.pact[dipKey(a, b)];
  return p && G.turn < p.until && dipFac(a) && dipFac(b) ? p : null;
}
function pactOn(a, b) { return !!pactOf(a, b); }
function pactLeft(a, b) { var p = pactOf(a, b); return p ? p.until - G.turn : 0; }
/* 세력의 힘: 거점과 부대의 병력을 모두 더한 것 */
function dipPower(f) {
  var t = 0, i;
  for (i = 0; i < G.bases.length; i++) if (G.bases[i].owner === f) t += G.bases[i].troops;
  for (i = 0; i < G.units.length; i++) if (G.units[i].f === f) t += G.units[i].troops;
  return t;
}
/* 세력 t 가 except 말고 다른 세력과 싸우는 중인가(warTurns 턴 안에 서로 쳤다) */
function dipBusy(t, except) {
  if (!G.dip) return false;
  for (var i = 0; i < G.factions.length; i++) {
    if (i === t || i === except || !dipFac(i)) continue;
    var w = G.dip.war[dipKey(t, i)];
    if (w !== undefined && G.turn - w <= DIP_K.warTurns) return true;
  }
  return false;
}
/* 세력 f 가 (사신 o 를 보내) t 에게 kind 를 청할 때 받아들일 확률(%)과 그 내역 */
function dipTerms(f, t, kind, o) {
  var K = DIP_K, rel = relOf(f, t), pf = dipPower(f), pt = dipPower(t);
  var stat = o ? (kind === 'ally' ? o.cha : o.pol) : 70;
  var rt = Math.max(1, pf) / Math.max(1, pt), pow = rt >= 1 ? Math.min((rt - 1) * K.powK, K.powHi) : -Math.min((1 / rt - 1) * K.powK, K.powLo);      // 우리가 두 배면 +powK, 저쪽이 두 배면 −powK
  var x = { rel: rel, base: kind === 'ally' ? K.allyBase : K.truceBase, envoy: Math.round((stat - 70) * K.envoyK), pow: Math.round(pow), busy: dipBusy(t, f) ? K.busy : 0 };
  x.p = clamp(x.rel + x.base + x.envoy + x.pow + x.busy, 0, K.askHi);
  if (kind === 'ally' && rel < K.allyRel) { x.p = 0; x.low = true; }
  return x;
}
function dipChance(f, t, kind, o) { return dipTerms(f, t, kind, o).p; }
function dipCool(f, t) { var D = G.dip, v = D ? D.cd[f + ':' + t] : 0; return v && v > G.turn ? v - G.turn : 0; }
/* 지금 f 가 t 에게 kind 를 청할 수 있는가 → '' 이면 된다, 아니면 안 되는 까닭 */
function dipCan(f, t, kind) {
  if (f === t || !dipFac(f) || !dipFac(t)) return '상대할 세력이 아닙니다';
  var p = pactOf(f, t);
  if (kind === 'truce' && p) return p.t === 'ally' ? '이미 동맹입니다' : '이미 정전 중입니다';
  if (kind === 'ally' && p && p.t === 'ally') return '이미 동맹입니다';
  if (kind === 'ally' && relOf(f, t) < DIP_K.allyRel) return '우호가 ' + DIP_K.allyRel + ' 이상이어야 동맹을 청할 수 있습니다';
  var c = dipCool(f, t);
  if (c) return dipDays(c) + ' 뒤에 다시 청할 수 있습니다';
  return '';
}
function dipDays(n) { return n * 10 + '일'; }
/* 저쪽에서 말로 맞설 사람: 군사 → 지력이 가장 높은 무장 → 군주 */
function dipSpeaker(t) {
  var a = facAdv(t); if (a) return a;
  var os = facOfficers(t), best = null;
  for (var i = 0; i < os.length; i++) if (!best || os[i].int > best.int) best = os[i];
  return best || off(G.factions[t].lord);
}
/* 협정을 맺는다(규칙 안에서만 부른다) */
function dipSign(f, t, kind) {
  var D = dipOf(), K = DIP_K;
  D.pact[dipKey(f, t)] = { t: kind, until: G.turn + (kind === 'ally' ? K.allyTurns : K.truceTurns), by: f };
  relAdd(f, t, kind === 'ally' ? K.okRelAlly : K.okRelTruce);
  var c = facCities(t)[0] || facBases(t)[0];
  logMsg(facName(f) + '군과 ' + facName(t) + '군이 ' + (kind === 'ally' ? '동맹을 맺었다' : '정전하기로 했다') + ' — ' + dipDays(D.pact[dipKey(f, t)].until - G.turn), c ? c.c : undefined, c ? c.r : undefined, f === G.player || t === G.player ? G.player : f, 2);
}
/* 친선: 금을 보내 우호를 올린다 */
function cmdGift(b, id, t) {
  var f = b.owner, K = DIP_K, os = getIdle(b, [id]); if (!os) return ERR('보낼 무장을 고르세요');
  if (f === t || !dipFac(t)) return ERR('상대할 세력이 아닙니다');
  var D = dipOf();
  if (D.gift[f + ':' + t] === G.turn) return ERR('이번 턴에는 이미 선물을 보냈습니다');
  if (relOf(f, t) >= 100) return ERR('우호가 이미 가장 높습니다');
  if (b.gold < K.giftGold) return ERR('금이 부족합니다(금 ' + K.giftGold + ')');
  if (!needAP(f, AP.gift)) return ERR('행동력이 부족합니다');
  useAP(f, AP.gift); b.gold -= K.giftGold; markActed(os, 10);
  var add = K.giftBase + Math.round(os[0].pol / K.giftPol), r0 = relOf(f, t), r1 = relAdd(f, t, add);
  D.gift[f + ':' + t] = G.turn;
  logMsg(os[0].n + ', ' + facName(t) + '군에 선물 — 우호 ' + r0 + ' → ' + r1, b.c, b.r, f, 0);
  return { ok: true, add: r1 - r0, rel: r1, o: os[0].id };
}
/* 설전으로 담판을 지을 수 있는가 · 그 판을 만든다(등용의 설전과 같은 꼴) */
function dipTalkOk(b, o, t, kind) { var p = dipChance(b.owner, t, kind, o); return !dipCan(b.owner, t, kind) && p >= DIP_K.talkMin && p < 100; }
function dipTalkNew(b, o, t, kind) {
  var p = dipChance(b.owner, t, kind, o), S = duelNew('talk', o, dipSpeaker(t), { hpD: Math.round(DUEL_K.hp * (1 + (DIP_K.talkHp - p) / 100)) });
  S.db = b.id; S.do = o.id; S.dt = t; S.dk = kind; S.dp = p;
  return S;
}
/* 정전 · 동맹을 청한다. S = 끝난 설전(있으면 그 승패가 주사위를 대신한다) */
function cmdTreaty(b, id, t, kind, S) {
  var f = b.owner, K = DIP_K, os = getIdle(b, [id]); if (!os) return ERR('보낼 무장을 고르세요');
  if (kind !== 'truce' && kind !== 'ally') return ERR('알 수 없는 제안입니다');
  var why = dipCan(f, t, kind); if (why) return ERR(why);
  if (S && (S.kind !== 'talk' || !S.over || S.used || S.db !== b.id || S.do !== id || S.dt !== t || S.dk !== kind)) return ERR('설전의 결과가 맞지 않습니다');
  if (!needAP(f, AP.treaty)) return ERR('행동력이 부족합니다');
  useAP(f, AP.treaty); markActed(os, 20);
  var p = dipChance(f, t, kind, os[0]), ok = S ? S.win === 'a' : rnd() * 100 < p;
  if (S) S.used = true;
  if (ok) { dipSign(f, t, kind); os[0].merit += 80; return { ok: true, success: true, p: p, kind: kind, o: os[0].id, until: dipOf().pact[dipKey(f, t)].until }; }
  var D = dipOf(); D.cd[f + ':' + t] = G.turn + K.cool; relAdd(f, t, -K.refuse);
  logMsg(facName(t) + '군이 ' + PACT_NAME[kind] + ' 제안을 물리쳤다', b.c, b.r, f, 0);
  return { ok: true, success: false, p: p, kind: kind, o: os[0].id, cool: K.cool };
}
/* 협정을 깬다(행동력 · 사신 없이 바로). 그 세력과의 우호가 크게 내리고, 다른 세력들도 믿지 않게 된다 */
function cmdBreak(f, t) {
  var p = pactOf(f, t); if (!p) return ERR('맺은 협정이 없습니다');
  var D = dipOf(), K = DIP_K, kind = p.t;
  delete D.pact[dipKey(f, t)];
  relAdd(f, t, -K.breakRel);
  for (var i = 0; i < G.factions.length; i++) if (i !== f && i !== t && dipFac(i)) relAdd(f, i, -K.breakOthers);
  D.cd[f + ':' + t] = G.turn + K.breakCool; D.cd[t + ':' + f] = G.turn + K.breakCool;
  var c = facCities(t)[0] || facBases(t)[0];
  logMsg(facName(f) + '군이 ' + facName(t) + '군과의 ' + PACT_NAME[kind] + '을 깼다', c ? c.c : undefined, c ? c.r : undefined, f === G.player || t === G.player ? G.player : f, 2);
  return { ok: true, kind: kind };
}
/* AI 가 플레이어에게 청해 온 것에 답한다 */
function dipOffers() { var D = G.dip; return D ? D.offers.filter(function (x) { return x.turn === G.turn && dipFac(x.from) && !dipCan(x.from, G.player, x.kind); }) : []; }
function dipAnswer(from, kind, yes) {
  var D = dipOf(), i = -1;
  for (var j = 0; j < D.offers.length; j++) if (D.offers[j].from === from && D.offers[j].kind === kind && D.offers[j].turn === G.turn) i = j;
  if (i < 0) return ERR('그런 제안이 없습니다');
  D.offers.splice(i, 1);
  if (dipCan(from, G.player, kind)) return ERR('지금은 맺을 수 없습니다');
  if (yes) { dipSign(from, G.player, kind); return { ok: true, success: true, kind: kind }; }
  D.cd[from + ':' + G.player] = G.turn + DIP_K.cool; relAdd(from, G.player, -DIP_K.refuse);
  return { ok: true, success: false, kind: kind };
}
/* 서로 쳤을 때: 우호가 내려가고, 싸우는 중이라고 적어 둔다 */
function dipHit(f, tf, fell) {
  if (f === tf || !dipFac(f) || tf < 0 || !G.factions[tf]) return;
  dipOf().war[dipKey(f, tf)] = G.turn;
  if (dipFac(tf)) relAdd(f, tf, -(DIP_K.hitRel + (fell ? DIP_K.fallRel : 0)));
}
/* 달이 바뀔 때: 우호가 처음 값 쪽으로 한 칸 돌아가고(협정 중인 사이는 그대로), 끝난 협정을 알리고, AI 가 플레이어에게 청해 온다 */
function dipMonth() {
  var D = dipOf(), K = DIP_K, k, i;
  for (k in D.rel) { var ab = k.split('-'), a = +ab[0], b = +ab[1]; if (!dipFac(a) || !dipFac(b)) { delete D.rel[k]; continue; } if (pactOf(a, b)) continue; if (D.rel[k] > K.rel0) D.rel[k] = Math.max(K.rel0, D.rel[k] - K.drift); else if (D.rel[k] < K.rel0) D.rel[k] = Math.min(K.rel0, D.rel[k] + K.drift); }
  D.offers = [];
  if (G.aiOnly || !dipFac(G.player)) return;
  var me = G.player, pm = dipPower(me);
  function offer(from, kind) { D.offers.push({ from: from, kind: kind, turn: G.turn }); var c = facCities(from)[0] || facBases(from)[0]; logMsg(facName(from) + '군이 ' + PACT_NAME[kind] + '을 청해 왔습니다 — 이번 턴 안에 답하십시오', c ? c.c : undefined, c ? c.r : undefined, me, 2); }
  for (i = 0; i < G.factions.length; i++) {
    if (i === me || !dipFac(i)) continue;
    var rel = relOf(i, me), p = pactOf(i, me);
    if (dipCool(i, me) || (G.peace && G.turn < G.peace.until && !G.peace.broken[i])) continue;       // 초반 보호가 살아 있는 동안은 청해 올 까닭이 없다
    if (!(p && p.t === 'ally') && rel >= K.aiAllyRel) { if (rnd() * 100 < K.aiAsk) offer(i, 'ally'); continue; }
    if (!p && rel >= K.aiTruceRel && (dipPower(i) < pm * K.aiWeak || dipBusy(i, me))) { if (rnd() * 100 < K.aiAsk) offer(i, 'truce'); }
  }
}
/* 턴이 바뀔 때: 플레이어의 협정이 곧 끝나거나 끝났으면 알린다 */
function dipTurn() {
  var D = G.dip; if (!D || G.aiOnly || !dipFac(G.player)) return;
  for (var k in D.pact) {
    var ab = k.split('-'), a = +ab[0], b = +ab[1], p = D.pact[k], o = a === G.player ? b : (b === G.player ? a : -1);
    if (o < 0 || !dipFac(o)) continue;
    var c = facCities(o)[0] || facBases(o)[0];
    if (p.until - G.turn === 3) logMsg(facName(o) + '군과의 ' + PACT_NAME[p.t] + '이 30일 뒤에 끝납니다', c ? c.c : undefined, c ? c.r : undefined, G.player, 1);
    else if (p.until === G.turn) { logMsg(facName(o) + '군과의 ' + PACT_NAME[p.t] + '이 끝났습니다', c ? c.c : undefined, c ? c.r : undefined, G.player, 2); delete D.pact[k]; }
  }
}
'''
s = rep(s, "/* 지금 플레이어가 세력 o 의 거점·시설을 치면 초반 보호가 깨지는가 */", DIP.strip('\n') + "\n/* 지금 플레이어가 세력 o 의 거점·시설을 치면 초반 보호가 깨지는가 */")
# 협정을 맺은 세력은 칠 수 없다
s = rep(s, "    if (ou && ou.f !== u.f) { out.push({ kind: 'unit', u: ou, c: c, r: r, d: d }); continue; }\n    var bi = BAT[k];\n    if (bi !== undefined) { var b = G.bases[bi]; if (b.owner >= 0 && b.owner !== u.f && !justOut(u)) out.push({ kind: 'base', b: b, c: c, r: r, d: d }); continue; }\n    var pf = PAT[k];\n    if (pf) { var pb = G.bases[pf.b], fc = pb.plots[pf.i].fac; if (fc && pb.owner >= 0 && pb.owner !== u.f && d === 1 && !justOut(u)) out.push({ kind: 'fac', b: pb, i: pf.i, c: c, r: r, d: d }); }",
           "    if (ou && ou.f !== u.f) { if (!pactOn(u.f, ou.f)) out.push({ kind: 'unit', u: ou, c: c, r: r, d: d }); continue; }      // v0.14: 협정을 맺은 세력은 칠 수 없다\n    var bi = BAT[k];\n    if (bi !== undefined) { var b = G.bases[bi]; if (b.owner >= 0 && b.owner !== u.f && !justOut(u) && !pactOn(u.f, b.owner)) out.push({ kind: 'base', b: b, c: c, r: r, d: d }); continue; }\n    var pf = PAT[k];\n    if (pf) { var pb = G.bases[pf.b], fc = pb.plots[pf.i].fac; if (fc && pb.owner >= 0 && pb.owner !== u.f && d === 1 && !justOut(u) && !pactOn(u.f, pb.owner)) out.push({ kind: 'fac', b: pb, i: pf.i, c: c, r: r, d: d }); }")
s = rep(s, "  var pb = G.bases[pf.b]; if (!pb.plots[pf.i].fac || pb.owner < 0 || pb.owner === u.f) return null;",
           "  var pb = G.bases[pf.b]; if (!pb.plots[pf.i].fac || pb.owner < 0 || pb.owner === u.f || pactOn(u.f, pb.owner)) return null;")
s = rep(s, "      if (ou && ou.f === u.f) continue;\n      var pf = PAT[k], enemyFac = pf && G.bases[pf.b].plots[pf.i].fac && G.bases[pf.b].owner !== u.f;\n      if (!ou && !enemyFac) continue;\n      out.push({ c: c, r: r, u: ou || null });\n    } else if (ou && ou.f !== u.f && !ou.status) out.push({ c: c, r: r, u: ou });",
           "      if (ou && (ou.f === u.f || pactOn(u.f, ou.f))) continue;\n      var pf = PAT[k], enemyFac = pf && G.bases[pf.b].plots[pf.i].fac && G.bases[pf.b].owner !== u.f && !pactOn(u.f, G.bases[pf.b].owner);\n      if (!ou && !enemyFac) continue;\n      out.push({ c: c, r: r, u: ou || null });\n    } else if (ou && ou.f !== u.f && !ou.status && !pactOn(u.f, ou.f)) out.push({ c: c, r: r, u: ou });")
s = rep(s, "function aiMayStrike(f, owner) {\n  if (owner < 0 || owner === f) return true;\n",
           "function aiMayStrike(f, owner) {\n  if (owner < 0 || owner === f) return true;\n  if (pactOn(f, owner)) return false;                              // v0.14: 협정을 맺은 세력은 치지 않는다\n")
s = rep(s, "function canPoach(b, t) { return !!t && t.st === 'active' && t.unit === null && t.f >= 0 && t.f !== b.owner && !isLord(t) && G.bases[t.loc].owner === t.f && isNeighbor(b, t.loc); }",
           "function canPoach(b, t) { return !!t && t.st === 'active' && t.unit === null && t.f >= 0 && t.f !== b.owner && !isLord(t) && G.bases[t.loc].owner === t.f && isNeighbor(b, t.loc) && !pactOn(b.owner, t.f); }      // v0.14: 협정을 맺은 세력의 무장에게는 권하지 않는다")
# 싸움이 있을 때마다 우호가 내려간다
s = rep(s, "    res.alead = u.off[0]; res.tlead = t && t.u ? t.u.off[0] : -1;",
           "    res.alead = u.off[0]; res.tlead = t && t.u ? t.u.off[0] : -1;\n    var df = tf !== undefined && tf >= 0 ? tf : (hf !== undefined ? hf : -1); if (df >= 0 && df !== f) dipHit(f, df, !!res.fell);      // v0.14: 치면 우호가 내려간다(시설을 태운 것도)")
# 규칙 쪽에서도 막는다: 협정을 맺은 세력을 치려 하면 아무것도 쓰지 않고 돌려보낸다
s = rep(s, "function unitChallenge(u, t) { var f = u.f, n = uName(u), ac = u.c, ar = u.r, tf = actTargetF(t); return actEv(",
           "function pactErr(u, t, ploy) { var tf = actTargetF(t), hf = actHoldF(t, ploy); return (tf >= 0 && tf !== u.f && pactOn(u.f, tf)) || (hf >= 0 && hf !== u.f && pactOn(u.f, hf)) ? ERR('협정을 맺은 세력은 칠 수 없습니다 — 치려면 먼저 협정을 깨야 합니다') : null; }\nfunction unitChallenge(u, t) { var pe = pactErr(u, t); if (pe) return pe; var f = u.f, n = uName(u), ac = u.c, ar = u.r, tf = actTargetF(t); return actEv(")
s = rep(s, "function unitAttack(u, t) { var f = u.f,", "function unitAttack(u, t) { var pe = pactErr(u, t); if (pe) return pe; var f = u.f,")
s = rep(s, "function unitTactic(u, tac, t) { var f = u.f,", "function unitTactic(u, tac, t) { var pe = pactErr(u, t); if (pe) return pe; var f = u.f,")
s = rep(s, "function unitPloy(u, ploy, t) { var f = u.f,", "function unitPloy(u, ploy, t) { var pe = pactErr(u, t, ploy); if (pe) return pe; var f = u.f,")
s = rep(s, "var o = UAT[K(ns[i][0], ns[i][1])]; if (o && o.f !== u.f && !o.status) out.push({ kind: 'unit', u: o, c: o.c, r: o.r }); }",
           "var o = UAT[K(ns[i][0], ns[i][1])]; if (o && o.f !== u.f && !o.status && !pactOn(u.f, o.f)) out.push({ kind: 'unit', u: o, c: o.c, r: o.r }); }")
# 달 · 턴이 바뀔 때
s = rep(s, "  var newMonth = G.xun === 0, newQuarter = newMonth && (G.month === 1 || G.month === 4 || G.month === 7 || G.month === 10), newYear = newMonth && G.month === 1;\n",
           "  var newMonth = G.xun === 0, newQuarter = newMonth && (G.month === 1 || G.month === 4 || G.month === 7 || G.month === 10), newYear = newMonth && G.month === 1;\n  dipTurn(); if (newMonth) dipMonth(); else if (G.dip) G.dip.offers = [];      // v0.14: 외교\n")
wr('core.js', s)

# ---------- ai.js ----------
s = rd('ai.js')
s = rep(s, "  for (var i = 0; i < G.units.length; i++) { var u = G.units[i]; if (u.f !== f && hdist(c, r, u.c, u.r) <= rad) out.push(u); }",
           "  for (var i = 0; i < G.units.length; i++) { var u = G.units[i]; if (u.f !== f && hdist(c, r, u.c, u.r) <= rad && !pactOn(f, u.f)) out.push(u); }      // v0.14: 협정을 맺은 세력의 부대는 적으로 세지 않는다")
s = rep(s, "      if (t.f === G.player && G.peace && G.turn < G.peace.until) continue;      // 초반 보호: 그동안은 플레이어의 무장에게 권하지 않는다",
           "      if (t.f === G.player && G.peace && G.turn < G.peace.until) continue;      // 초반 보호: 그동안은 플레이어의 무장에게 권하지 않는다\n      if (pactOn(f, t.f)) continue;                                              // v0.14: 협정을 맺은 세력의 무장도")
wr('ai.js', s)
print('p1_dip_core ok')
