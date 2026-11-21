/* ===== 천하도 — 규칙 엔진 (DOM 없음) ===== */
var W = MAPDATA.W, H = MAPDATA.H;
var G = null;                 // 게임 상태 (저장 대상)
var UMAP = {}, UAT = {};      // 런타임 색인: 부대 id→부대, 헥스→부대
var BAT = {}, PAT = {};       // 정적 색인: 헥스→거점 id, 헥스→{b, i}
var ADJ = [];                 // 거점 그래프
var REPORT = [];              // 이번 턴 전황 보고 (저장 안 함)
var EVQ = [];                 // 화면 연출용 이벤트 (저장 안 함)

function K(c, r) { return r * W + c; }
function inMap(c, r) { return c >= 0 && r >= 0 && c < W && r < H; }
function terr(c, r) { return MAPDATA.t.charAt(r * W + c); }
function isRoad(c, r) { return MAPDATA.road.charAt(r * W + c) === '1'; }
var NB_EVEN = [[1, 0], [-1, 0], [0, -1], [-1, -1], [0, 1], [-1, 1]];
var NB_ODD = [[1, 0], [-1, 0], [1, -1], [0, -1], [1, 1], [0, 1]];
function nbrs(c, r) {
  var d = (r & 1) ? NB_ODD : NB_EVEN, out = [];
  for (var i = 0; i < 6; i++) { var cc = c + d[i][0], rr = r + d[i][1]; if (inMap(cc, rr)) out.push([cc, rr]); }
  return out;
}
function cubeX(c, r) { return c - ((r - (r & 1)) >> 1); }
function hdist(c1, r1, c2, r2) {
  var dx = cubeX(c1, r1) - cubeX(c2, r2), dz = r1 - r2;
  return Math.max(Math.abs(dx), Math.abs(dz), Math.abs(dx + dz));
}
function stepDir(c, r, dx, dz) { var x = cubeX(c, r) + dx, z = r + dz; return [x + ((z - (z & 1)) >> 1), z]; }
function clamp(v, a, b) { return v < a ? a : (v > b ? b : v); }
/* ---------- 지형 표(빠른 경로 탐색용) ---------- */
var NHEX = W * H, NBR = new Int32Array(NHEX * 6), TCH = new Uint8Array(NHEX), RDB = new Uint8Array(NHEX), ELV = new Uint8Array(NHEX);      // ELV: 칸의 높이 단계(v0.15)
var MC = [new Uint8Array(NHEX), new Uint8Array(NHEX), new Uint8Array(NHEX)];
(function () {
  for (var r = 0; r < H; r++) for (var c = 0; c < W; c++) {
    var k = r * W + c, t = MAPDATA.t.charAt(k), rd = MAPDATA.road.charAt(k) === '1', d = (r & 1) ? NB_ODD : NB_EVEN;
    TCH[k] = t.charCodeAt(0); RDB[k] = rd ? 1 : 0; ELV[k] = MAPDATA.e ? (parseInt(MAPDATA.e.charAt(k), 36) || 0) : 0;
    for (var i = 0; i < 6; i++) { var cc = c + d[i][0], rr = r + d[i][1]; NBR[k * 6 + i] = (cc >= 0 && rr >= 0 && cc < W && rr < H) ? rr * W + cc : -1; }
    for (var ci = 0; ci < 3; ci++) MC[ci][k] = (t === 'm' || t === 's' || t === 'x') ? 99 : (t === 'w' ? (rd ? 4 : 8) : (rd ? ROAD_COST[ci] : MOVE_COST[t][ci]));
  }
})();
function clsIdx(u) { var cls = UNIT_TYPES[u.type].cls; return cls === 'horse' ? 1 : (cls === 'siege' ? 2 : 0); }
/* 조사: josa('관우', '이가') → '관우가' */
function josa(w, pair) {
  var c = w.charCodeAt(w.length - 1), bat = (c >= 0xAC00 && c <= 0xD7A3) ? ((c - 0xAC00) % 28 !== 0) : (c >= 48 && c <= 57 ? '013678'.indexOf(w.charAt(w.length - 1)) >= 0 : false);
  return w + (bat ? pair.charAt(0) : pair.charAt(1));
}
function nf(n) { return Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ','); }

/* ---------- 난수 ---------- */
function rnd() {
  G.seed = (G.seed + 0x6D2B79F5) | 0;
  var t = G.seed;
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
}
function ri(a, b) { return a + Math.floor(rnd() * (b - a + 1)); }
/* ---------- 미리 정해 둔 결과(v0.9) ----------
   등용과 계략의 성패는 '때(턴 또는 달) · 대상(· 계략 종류)'으로 미리 정해져 있다: 성공률이 p 일 때 주사위(0~100) < p 이면 성공.
   같은 턴에 같은 대상이면 몇 번을 물어도, 창을 다시 열어도, 저장을 다시 불러도 같다 — 그래서 군사가 하기 전에 말할 수 있다.
   G.rnd 흐름(G.seed)과는 따로 논다. */
function strHash(s) { var h = 2166136261 | 0; for (var i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h | 0; }
function omenRoll(key, monthly) {                                  // 0 이상 100 미만. monthly = 턴이 아니라 달마다 한 번 정해지는 것(그 달에는 같다)
  var e = monthly ? 0x40000 + G.year * 12 + G.month : (G.turn | 0);
  var t = (G.seed0 | 0) ^ Math.imul(e + 0x7F4A7C15, 0x9E3779B1) ^ strHash(key);
  t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); t = Math.imul(t ^ (t >>> 13), 0x5bd1e995 | 1);
  return ((t ^ (t >>> 15)) >>> 0) / 4294967296 * 100;
}
/* 등용의 주사위: 대상에만 건다. 재야·포로는 턴마다, 다른 세력의 무장(st 'active')은 달마다 한 번 */
function recruitRoll(t) { return omenRoll('r' + t.id, t.st === 'active'); }
function recruitRollA(t) { return omenRoll('a|r' + t.id, t.st === 'active'); }            // 군사의 조언이 맞는가
function ployKey(ploy, t) { return 'p' + ploy.id + (t.u ? 'u' + t.u.id : 'k' + K(t.c, t.r)); }   // 계략: 종류 + 대상 부대(부대가 없으면 칸). 턴마다
function ployRoll(ploy, t) { return omenRoll(ployKey(ploy, t)); }
function ployRollA(ploy, t) { return omenRoll('a|' + ployKey(ploy, t)); }
function chance(p) { return rnd() * 100 < p; }
function pick(arr) { return arr[Math.floor(rnd() * arr.length)]; }

/* ---------- 정적 색인 ---------- */
(function () {
  var i, j, b;
  for (i = 0; i < MAPDATA.bases.length; i++) {
    b = MAPDATA.bases[i];
    BAT[K(b.c, b.r)] = i;
    ADJ.push([]);
    var pl = MAPDATA.plots[b.n] || [];
    for (j = 0; j < pl.length; j++) PAT[K(pl[j][0], pl[j][1])] = { b: i, i: j };
  }
  for (i = 0; i < MAPDATA.edges.length; i++) {
    var e = MAPDATA.edges[i];
    ADJ[e[0]].push({ to: e[1], len: e[2] });
    ADJ[e[1]].push({ to: e[0], len: e[2] });
  }
})();
/* 성역(城域): 성 둘레 ZONE_R 칸. 값 = 그 성의 번호, 성역 밖은 -1. 관문에는 성역이 없다.
   v0.8부터 이동을 막지 않는다(0.5~0.7에서는 경계를 넘으면 그 턴 이동이 끝났다) — 이름·고리 표시·긴장한 음악의 기준으로만 쓴다. */
var ZONE = new Int16Array(NHEX);
(function () {
  var i, c, r;
  for (i = 0; i < NHEX; i++) ZONE[i] = -1;
  for (i = 0; i < MAPDATA.bases.length; i++) {
    var b = MAPDATA.bases[i];
    if (b.k !== 'city') continue;
    for (r = Math.max(0, b.r - ZONE_R); r <= Math.min(H - 1, b.r + ZONE_R); r++) for (c = Math.max(0, b.c - ZONE_R - 1); c <= Math.min(W - 1, b.c + ZONE_R + 1); c++) {
      if (hdist(c, r, b.c, b.r) > ZONE_R) continue;
      var k = r * W + c;
      if (ZONE[k] < 0 || hdist(c, r, b.c, b.r) < hdist(c, r, MAPDATA.bases[ZONE[k]].c, MAPDATA.bases[ZONE[k]].r)) ZONE[k] = i;
    }
  }
})();
function zoneAt(c, r) { return ZONE[r * W + c]; }
function baseByName(n) { for (var i = 0; i < MAPDATA.bases.length; i++) if (MAPDATA.bases[i].n === n) return i; return -1; }

/* ---------- 접근자 ---------- */
function off(id) { return G.officers[id]; }
function fac(id) { return G.factions[id]; }
function unitAt(c, r) { return UAT[K(c, r)] || null; }
function baseAt(c, r) { var i = BAT[K(c, r)]; return i === undefined ? null : G.bases[i]; }
function plotAt(c, r) { var p = PAT[K(c, r)]; return p ? { base: G.bases[p.b], i: p.i, plot: G.bases[p.b].plots[p.i] } : null; }
function facAt(c, r) { var p = PAT[K(c, r)]; if (!p) return null; return G.bases[p.b].plots[p.i].fac; }
function reindex() {
  UMAP = {}; UAT = {};
  for (var i = 0; i < G.units.length; i++) { var u = G.units[i]; UMAP[u.id] = u; UAT[K(u.c, u.r)] = u; }
}
function facName(f) { return f < 0 ? '재야' : G.factions[f].name; }
function isLord(o) { return o.f >= 0 && G.factions[o.f].lord === o.id; }
/* ---------- 군사(軍師, v0.9) ----------
   세력마다 한 사람. 군주는 될 수 없다. 출진해 있거나 다른 거점으로 가는 중이어도 군사다. 사로잡히거나 죽거나 떠나면 자리가 비고, 그 세력의 차례가 올 때 지력이 가장 높은 무장으로 채운다. */
function advOk(o, f) { return !!o && o.f === f && (o.st === 'active' || o.st === 'travel') && G.factions[f].lord !== o.id; }
function facAdv(f) { var F = G.factions[f]; if (!F || F.adv === undefined || F.adv < 0) return null; var o = off(F.adv); return advOk(o, f) ? o : null; }
function advCandidates(f) { return G.officers.filter(function (o) { return advOk(o, f); }).sort(function (a, b) { return b.int - a.int || a.id - b.id; }); }
function autoAdvisor(f) { var c = advCandidates(f); G.factions[f].adv = c.length ? c[0].id : -1; return c.length ? c[0] : null; }
function setAdvisor(f, id) { var o = off(id); if (!advOk(o, f)) return ERR('군사로 삼을 수 없는 무장입니다'); G.factions[f].adv = o.id; return { ok: true }; }
/* 조언이 맞을 확률(%): 군사의 지력 그대로. 상대가 더 똑똑하면 그 차이 × k 만큼 깎인다(상대의 지력이 없는 일은 tInt = 0) */
function adviceAcc(A, tInt) { return clamp(Math.round(A.int - Math.max(0, (tInt || 0) - A.int) * ADVISE.k), ADVISE.min, 100); }
/* 조언: { adv, acc, says } — says = "통한다"고 말하는가. 군사가 없으면 null.
   roll = 그 일의 주사위(recruitRoll·ployRoll), rollA = '조언이 맞는가'의 주사위(recruitRollA·ployRollA), p = 성공률, tInt = 상대의 지력.
   실제 결과(roll < p)를 acc% 의 확률로 바르게, 나머지는 거꾸로 말한다. '맞는가'도 대상에만 걸려 있어, 군사를 바꿔 물어도 새 정보가 생기지 않는다 */
function advise(f, roll, rollA, p, tInt) {
  var A = facAdv(f); if (!A) return null;
  var real = roll < p, acc = adviceAcc(A, tInt);
  return { adv: A, acc: acc, says: rollA < acc ? real : !real };
}
function dateStr() { return G.year + '년 ' + G.month + '월 ' + ['상순', '중순', '하순'][G.xun]; }
function dateOfTurn(t) { var m = Math.floor((t - 1) / 3); return (194 + Math.floor(m / 12)) + '년 ' + (m % 12 + 1) + '월 ' + ['상순', '중순', '하순'][(t - 1) % 3]; }   // 턴 번호 → 날짜(1턴 = 194년 1월 상순)
/* ---------- 초반 보호 ---------- */
function peaceFor(troops) {               // 시작 병력 → 보호 턴 수
  for (var i = 0; i < PEACE_PLAYER.length; i++) if (troops < PEACE_PLAYER[i][0]) return PEACE_PLAYER[i][1];
  return PEACE_ALL;
}
function peaceTurns(f) {                 // 세력 f 로 시작하면 몇 턴 보호받는가(지금 가진 병력으로 — 새 판을 만들 때 부른다)
  var t = 0; G.bases.forEach(function (b) { if (b.owner === f) t += b.troops; });
  return peaceFor(t);
}
/* 시나리오에서 세력 i 가 처음 가진 병력(성 + 관문) — newGame 과 같은 셈. 판을 만들기 전(군주 고르기)에 쓴다 */
function startTroops(i) {
  var sf = SCENARIO.factions[i], st = START[sf.n] || [10000, 1500, 15000, 1000], t = 0, j;
  for (j = 0; j < sf.cities.length; j++) t += Math.round(st[0] * (j === 0 ? 1 : 0.55) / 100) * 100;
  for (var gn in SCENARIO.gates) if (SCENARIO.gates[gn] === i && baseByName(gn) >= 0) t += 2000;
  return t;
}
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
/* 지금 플레이어가 세력 o 의 거점·시설을 치면 초반 보호가 깨지는가 */
function peaceWouldBreak(o) { return !!G.peace && o >= 0 && o !== G.player && G.turn < G.peace.until && !G.peace.broken[o]; }
/* 플레이어가 먼저 쳐서 보호가 풀린 세력(살아 있는 것만) */
function peaceBroken() { var out = []; if (G.peace) for (var k in G.peace.broken) if (G.peace.broken[k] && G.factions[+k] && G.factions[+k].alive) out.push(+k); return out; }
function peaceLeft() { return G.peace ? Math.max(0, G.peace.until - G.turn) : 0; }      // 플레이어의 보호가 몇 턴 남았나
/* AI 세력 f 가 owner 의 거점·시설을 '먼저' 쳐도 되는가 */
function aiMayStrike(f, owner) {
  if (owner < 0 || owner === f) return true;
  if (pactOn(f, owner)) return false;                              // v0.14: 협정을 맺은 세력은 치지 않는다
  var P = G.peace;
  if (!P) return true;                                             // 옛 저장: 보호 없음
  if (owner === G.player) return G.turn >= P.until || !!P.broken[f];
  if (f === G.player) return !G.aiOnly || G.turn > PEACE_ALL;      // AI 대전에서 플레이어 자리를 AI 가 둘 때는 다른 AI 와 같다. 사람이 두는 판에서 이 물음이 오는 것은 내 군단의 부대뿐 — 명을 받아 치는 것이다
  return G.turn > PEACE_ALL;                                       // AI 끼리: 처음 PEACE_ALL 턴은 쉰다
}
/* AI 가 플레이어의 거점을 칠 때 필요한 병력 우위(배): 보호가 막 끝났을 때 2.0, PEACE_RAMP 턴 뒤 1.25. 플레이어가 먼저 친 세력은 1.25 */
function aiNeedMul(f, owner) {
  var P = G.peace;
  if (!P || owner !== G.player || P.broken[f]) return 1.25;
  return 1.25 + 0.75 * clamp(1 - (G.turn - P.until) / PEACE_RAMP, 0, 1);
}
/* 완충 기간(보호가 끝난 뒤 PEACE_RAMP 턴)인가 — 이때는 한 번에 한 세력만 플레이어를 치러 온다. 플레이어가 먼저 친 세력에게는 해당 없음 */
function peaceRamp(f) { var P = G.peace; return !!P && !P.broken[f] && G.turn < P.until + PEACE_RAMP; }
/* 세력 f 말고 다른 AI 세력이 지금 플레이어의 거점을 치러 가고 있는가 */
function othersOnPlayer(f) {
  for (var i = 0; i < G.units.length; i++) { var u = G.units[i]; if (u.f !== f && u.f !== G.player && u.ai && u.ai.mode === 'attack' && u.ai.target >= 0 && G.bases[u.ai.target].owner === G.player) return true; }
  return false;
}

function baseOfficers(b) {
  var out = [];
  if (b.owner < 0) return out;
  for (var i = 0; i < G.officers.length; i++) { var o = G.officers[i]; if (o.st === 'active' && o.f === b.owner && o.loc === b.id && o.unit === null) out.push(o); }
  return out;
}
function idleOfficers(b) { return baseOfficers(b).filter(function (o) { return !o.acted; }); }
/* ---------- 공사 담당 ----------
   시설을 짓는 무장은 완공될 때까지 그 일에 묶인다: 다른 명령도 출진도 이동도 못 한다(o.acted 가 턴이 바뀌어도 풀리지 않는다).
   o.job = { b: 거점, i: 부지 }, 시설 쪽에는 fac.by = [무장 id…], fac.t0 = 착공한 턴.
   완공·공사 중단(철거)·파괴·함락으로 풀린다. 시설이 어떻게 없어졌든 jobOf 가 그 자리에서 알아채고 풀어 준다. */
function jobOf(o) {
  var j = o.job; if (!j) return null;
  var b = G.bases[j.b], p = b && b.plots[j.i], f = p && p.fac;
  if (!f || f.done || !f.by || f.by.indexOf(o.id) < 0 || o.st !== 'active' || o.unit !== null || o.loc !== j.b || o.f !== b.owner) { o.job = null; return null; }
  return { b: b, i: j.i, fac: f, left: Math.max(1, Math.ceil((f.need - f.prog) / f.rate)) };
}
function builders(f) {                          // 지금 이 공사를 맡고 있는 무장들
  var out = [];
  if (f && !f.done && f.by) for (var i = 0; i < f.by.length; i++) { var o = off(f.by[i]), j = o && jobOf(o); if (j && j.fac === f) out.push(o); }
  return out;
}
function freeBuilders(f, rest) {                // 담당 무장을 풀어 준다. rest = 이번 턴은 이미 일한 것으로 둔다(행동 완료 유지)
  if (!f || !f.by) return;
  for (var i = 0; i < f.by.length; i++) { var o = off(f.by[i]); if (o && o.job && G.bases[o.job.b] && G.bases[o.job.b].plots[o.job.i] && G.bases[o.job.b].plots[o.job.i].fac === f) { o.job = null; if (!rest) o.acted = false; } }
  f.by = [];
}
function freeOfficers(b) { return G.officers.filter(function (o) { return o.st === 'free' && o.loc === b.id; }); }
function hiddenOfficers(b) { return G.officers.filter(function (o) { return o.st === 'hidden' && o.loc === b.id && o.y <= G.year && !o.j; }); }
function baseCaptives(b) { return b.captives.map(off); }
function facBases(f) { return G.bases.filter(function (b) { return b.owner === f; }); }
function facCities(f) { return G.bases.filter(function (b) { return b.owner === f && b.kind === 'city'; }); }
function facUnits(f) { return G.units.filter(function (u) { return u.f === f; }); }
function facOfficers(f) { return G.officers.filter(function (o) { return o.f === f && (o.st === 'active' || o.st === 'travel'); }); }
function hasFac(b, type) { for (var i = 0; i < b.plots.length; i++) { var f = b.plots[i].fac; if (f && f.done && f.t === type) return f; } return null; }
function bestFacLv(b, type) { var lv = 0; for (var i = 0; i < b.plots.length; i++) { var f = b.plots[i].fac; if (f && f.done && f.t === type && f.lv > lv) lv = f.lv; } return lv; }
function baseHasSkill(b, sk) { var os = baseOfficers(b); for (var i = 0; i < os.length; i++) if (os[i].sk === sk) return true; return false; }
function anyHas(os, sk) { for (var i = 0; i < os.length; i++) if (os[i].sk === sk) return true; return false; }
function bestOf(os, stat) { var m = 0; for (var i = 0; i < os.length; i++) if (os[i][stat] > m) m = os[i][stat]; return m; }
function sumOthers(os, stat) { var s = 0, m = 0; for (var i = 0; i < os.length; i++) { s += os[i][stat]; if (os[i][stat] > m) m = os[i][stat]; } return s - m; }

function cmdCap(o) {
  var v = 4000 + (o.ldr >= 90 ? 2000 : o.ldr >= 80 ? 1000 : o.ldr >= 70 ? 500 : 0);
  if (isLord(o)) v += 3000;
  v += Math.min(6000, Math.floor(o.merit / 400) * 500);
  return v;
}

/* ---------- 부대 능력 ---------- */
function uMembers(u) { return u.off.map(off); }
/* 충성과 인연 */
function bondWith(o, f) {                 // 무장 o 와 세력 f 의 군주 사이(없으면 null)
  if (!o || f === undefined || f < 0 || !G.factions[f] || G.factions[f].lord === o.id) return null;
  var L = off(G.factions[f].lord), m = L && BONDS[L.n];
  return (m && m[o.n]) || null;
}
function bondOf(o) { return o ? bondWith(o, o.f) : null; }       // 지금 모시는 군주와의 사이
function loyNat(o) {                      // 충성이 자리 잡는 값: 인연이 있으면 100, 아니면 사람됨(이름에서 뽑은 86~93)과 군주의 매력(-2~+6)에 따라 80~98
  if (bondOf(o)) return 100;
  var L = (o.f >= 0 && G.factions[o.f]) ? off(G.factions[o.f].lord) : null;
  var h = (o.n.charCodeAt(0) * 7 + o.n.charCodeAt(o.n.length - 1) * 13) % 8;
  return clamp(Math.round(86 + h + ((L ? L.cha : 70) - 70) / 5), 80, 98);
}
function uLeader(u) { return off(u.off[0]); }
function uHas(u, sk) { for (var i = 0; i < u.off.length; i++) if (off(u.off[i]).sk === sk) return true; return false; }
function uInt(u) { return bestOf(uMembers(u), 'int'); }
function uWar(u) { return bestOf(uMembers(u), 'war'); }
function uApt(u) {
  var idx = APT_IDX[u.type];
  if (idx === undefined) return 'B';
  var best = 'C', ms = uMembers(u);
  for (var i = 0; i < ms.length; i++) { var a = ms[i].apt.charAt(idx); if (APT_RANK[a] > APT_RANK[best]) best = a; }
  return best;
}
function uAtk(u) { var L = uLeader(u); return (L.war * 0.7 + uWar(u) * 0.3) * UNIT_TYPES[u.type].atk * APT_MUL[uApt(u)]; }
function uDef(u) { var L = uLeader(u); return (L.ldr * 0.7 + bestOf(uMembers(u), 'ldr') * 0.3) * UNIT_TYPES[u.type].def * APT_MUL[uApt(u)]; }
function uMaxMp(u) { var mp = UNIT_TYPES[u.type].mp; if (uHas(u, '강행')) mp += 3; return mp; }
function uRange(u) { return UNIT_TYPES[u.type].range; }
function uName(u) { return uLeader(u).n + '대'; }
function troopFactor(t) { return clamp(0.35 + 0.65 * Math.sqrt(Math.max(0, t) / 5000), 0.35, 1.25); }

function moveCost(u, c, r) {
  var k = r * W + c, ci = clsIdx(u), v = MC[ci][k];
  if (v < 99 && !RDB[k] && (TCH[k] === 102 || TCH[k] === 104) && uHas(u, '답파')) return MOVE_COST.p[ci];
  return v;
}
function enemyAdjacent(f, c, r) {
  var ns = nbrs(c, r);
  for (var i = 0; i < ns.length; i++) { var o = UAT[K(ns[i][0], ns[i][1])]; if (o && o.f !== f) return true; }
  return false;
}

/* ---------- 우선순위 큐 ---------- */
function Heap() { this.a = []; }
Heap.prototype.push = function (p, v) {
  var a = this.a, i = a.length; a.push([p, v]);
  while (i > 0) { var j = (i - 1) >> 1; if (a[j][0] <= a[i][0]) break; var t = a[j]; a[j] = a[i]; a[i] = t; i = j; }
};
Heap.prototype.pop = function () {
  var a = this.a, top = a[0], last = a.pop();
  if (a.length) {
    a[0] = last; var i = 0, n = a.length;
    for (;;) { var l = i * 2 + 1, r = l + 1, m = i; if (l < n && a[l][0] < a[m][0]) m = l; if (r < n && a[r][0] < a[m][0]) m = r; if (m === i) break; var t = a[m]; a[m] = a[i]; a[i] = t; i = m; }
  }
  return top;
};

/* v0.8: 성역의 경계에서 멈추는 규칙을 없앴다(0.5~0.7: 경계를 넘으면 그 턴 이동 끝, 막 들어선 성역의 성은 그 턴에 못 침).
   성역은 이름(○○ 성역)과 고리 표시로만 남는다. 급습을 막는 장치는 하나 — 출진한 그 턴에는 거점과 시설을 칠 수 없다(부대끼리는 싸울 수 있다). */
function justOut(u) { return u.born !== undefined && u.born === G.turn; }
/* 이번 턴 이동 가능 범위. 반환: { cost:{key:cost}, prev:{key:key}, stop:{key:true} } */
function unitReach(u) {
  var cost = {}, prev = {}, stop = {}, start = K(u.c, u.r), h = new Heap();
  var ignoreZoc = uHas(u, '비장');
  cost[start] = 0; h.push(0, start);
  while (h.a.length) {
    var top = h.pop(), d = top[0], k = top[1];
    if (d > cost[k]) continue;
    var c = k % W, r = (k - c) / W;
    if (k !== start) {
      if (BAT[k] !== undefined) continue;                              // 거점에 들어가면 이동 끝
      if (!ignoreZoc && enemyAdjacent(u.f, c, r)) continue;            // ZOC: 멈춤
    }
    var ns = nbrs(c, r);
    for (var i = 0; i < 6 && i < ns.length; i++) {
      var cc = ns[i][0], rr = ns[i][1], nk = K(cc, rr);
      var mc = moveCost(u, cc, rr);
      if (mc >= 99) continue;
      var nd = d + mc;
      if (nd > u.mp) continue;
      var ou = UAT[nk];
      if (ou && ou.f !== u.f) continue;                                // 적 부대
      var bi = BAT[nk];
      if (bi !== undefined) { var b = G.bases[bi]; if (b.owner !== u.f && b.owner !== -1) continue; }
      if (cost[nk] === undefined || nd < cost[nk]) {
        cost[nk] = nd; prev[nk] = k;
        if (!ou) stop[nk] = true;
        h.push(nd, nk);
      }
    }
  }
  delete stop[start];
  return { cost: cost, prev: prev, stop: stop };
}
function pathFromReach(rc, u, c, r) {
  var path = [], k = K(c, r), start = K(u.c, u.r);
  while (k !== start) { path.push(k); k = rc.prev[k]; if (k === undefined) return null; }
  path.reverse();
  return path;
}

/* 장거리 경로 (AI·행군·위보용). goal(key)→bool. hint=[c, r, 여유] 를 주면 A*로 좁혀 찾는다. 적 부대는 비싼 통과로 본다. */
var LP_COST = new Float32Array(NHEX), LP_PREV = new Int32Array(NHEX), LP_STAMP = new Uint32Array(NHEX), LP_GEN = 0;
function longPath(u, goalFn, maxCost, hint) {
  var start = K(u.c, u.r), h = new Heap(), found = -1, ci = clsIdx(u), dapa = uHas(u, '답파'), mcT = MC[ci], pc = MOVE_COST.p[ci], minStep = ROAD_COST[ci];
  var hc = hint ? hint[0] : -1, hr = hint ? hint[1] : 0, slack = hint ? (hint[2] || 0) : 0;
  function heur(k) { if (hc < 0) return 0; var c = k % W, d = hdist(c, (k - c) / W, hc, hr) - slack; return d > 0 ? d * minStep : 0; }
  maxCost = maxCost || 900;
  LP_GEN++;
  LP_COST[start] = 0; LP_STAMP[start] = LP_GEN; LP_PREV[start] = -1; h.push(heur(start), start);
  while (h.a.length) {
    var top = h.pop(), k = top[1], d = LP_COST[k];
    if (top[0] > d + heur(k) + 1e-4) continue;
    if (k !== start && goalFn(k)) { found = k; break; }
    if (d > maxCost) break;
    if (k !== start && BAT[k] !== undefined) continue;
    for (var i = 0; i < 6; i++) {
      var nk = NBR[k * 6 + i];
      if (nk < 0) continue;
      var mc = mcT[nk];
      if (mc >= 99) continue;
      if (dapa && !RDB[nk] && (TCH[nk] === 102 || TCH[nk] === 104)) mc = pc;
      var bi = BAT[nk];
      if (bi !== undefined) { var b = G.bases[bi]; if (b.owner !== u.f && b.owner !== -1 && !goalFn(nk)) continue; }
      var ou = UAT[nk];
      if (ou) mc += (ou.f === u.f ? 3 : 25);
      if (G.fires[nk]) mc += 6;
      var nd = d + mc;
      if (LP_STAMP[nk] !== LP_GEN || nd < LP_COST[nk]) { LP_STAMP[nk] = LP_GEN; LP_COST[nk] = nd; LP_PREV[nk] = k; h.push(nd + heur(nk), nk); }
    }
  }
  if (found < 0) return null;
  var path = [], kk = found;
  while (kk !== start) { path.push(kk); kk = LP_PREV[kk]; }
  path.reverse();
  return path;
}

/* ---------- 기록 ---------- */
function logMsg(text, c, r, f, imp) {
  var e = { d: dateStr(), t: text, c: c, r: r, f: f === undefined ? -1 : f, imp: imp || 0 };
  G.log.push(e);
  if (G.log.length > 150) G.log.shift();
  REPORT.push(e);
}
function ev(o) { EVQ.push(o); }

/* 세력 색을 석채(石彩) 빛으로: 원래 색에 먹빛을 조금 섞어 가라앉힌다(수묵 지도 위의 포인트색) */
(function () {
  for (var i = 0; i < SCENARIO.factions.length; i++) {
    var c = SCENARIO.factions[i].color, v = parseInt(c.slice(1), 16), r = (v >> 16) & 255, g = (v >> 8) & 255, b = v & 255;
    r = Math.round(r * 0.80 + 104 * 0.20); g = Math.round(g * 0.80 + 98 * 0.20); b = Math.round(b * 0.80 + 88 * 0.20);
    SCENARIO.factions[i].color = '#' + ((1 << 24) | (r << 16) | (g << 8) | b).toString(16).slice(1);
  }
})();
/* ---------- 게임 생성 ---------- */
function newGame(playerFaction, seed) {
  var i, j;
  G = {
    ver: 2, year: 194, month: 1, xun: 0, turn: 1, seed: (seed === undefined ? (Date.now() & 0x7fffffff) : seed) | 0,
    player: playerFaction, factions: [], officers: [], bases: [], units: [], fires: {}, nextUnit: 1, log: [], over: null, aiOnly: false, corps: [], nextCorps: 1
  };
  G.seed0 = G.seed;                                                // 판마다 고정된 씨앗(G.seed 는 난수를 뽑을 때마다 바뀐다) — 미리 정해 두는 결과(omenRoll)에 쓴다
  for (i = 0; i < SCENARIO.factions.length; i++) {
    var sf = SCENARIO.factions[i];
    G.factions.push({ id: i, name: sf.n, color: sf.color, lord: -1, ap: 80, alive: true, adv: -1 });
  }
  for (i = 0; i < MAPDATA.bases.length; i++) {
    var mb = MAPDATA.bases[i];
    var b = { id: i, n: mb.n, kind: mb.k, c: mb.c, r: mb.r, sz: mb.sz, owner: -1, gold: 0, food: 0, troops: 0, morale: 60, order: 60,
      dur: MAX_DUR[mb.sz], maxDur: MAX_DUR[mb.sz], w: { spear: 0, halberd: 0, bow: 0, horse: 0, ram: 0 }, plots: [], captives: [], ai: {} };
    var pl = MAPDATA.plots[mb.n] || [];
    for (j = 0; j < pl.length; j++) b.plots.push({ c: pl[j][0], r: pl[j][1], fac: null });
    G.bases.push(b);
  }
  function addFac(b, idx, t) { if (b.plots[idx]) b.plots[idx].fac = { t: t, lv: 1, done: true, prog: 0, need: 0, rate: 0, hp: FAC_HP }; }
  for (i = 0; i < SCENARIO.factions.length; i++) {
    var sf2 = SCENARIO.factions[i], st = START[sf2.n] || [10000, 1500, 15000, 1000];
    for (j = 0; j < sf2.cities.length; j++) {
      var cb = G.bases[baseByName(sf2.cities[j])], cap = j === 0, m = cap ? 1 : 0.55;
      cb.owner = i; cb.troops = Math.round(st[0] * m / 100) * 100; cb.gold = Math.round(st[1] * (cap ? 1 : 0.6));
      cb.food = Math.round(st[2] * (cap ? 1 : 0.6)); cb.morale = 70; cb.order = 75;
      cb.w.spear = Math.round(st[0] * 0.4 * m / 100) * 100; cb.w.halberd = Math.round(st[0] * 0.25 * m / 100) * 100;
      cb.w.bow = Math.round(st[0] * 0.25 * m / 100) * 100; cb.w.horse = Math.round(st[3] * m / 100) * 100;
      addFac(cb, 0, 'market'); addFac(cb, 1, 'farm'); addFac(cb, 2, 'barracks');
      if (cap) addFac(cb, 3, 'smithy');
    }
  }
  for (var gn in SCENARIO.gates) {
    var gb = G.bases[baseByName(gn)];
    if (!gb) continue;
    gb.owner = SCENARIO.gates[gn];
    if (gb.owner >= 0) { gb.troops = 2000; gb.morale = 70; gb.food = 0; }
  }
  for (i = 0; i < SCENARIO.officers.length; i++) {
    var so = SCENARIO.officers[i];
    var o = { id: i, n: so.n, ldr: so.ldr, war: so.war, int: so.int, pol: so.pol, cha: so.cha, apt: so.apt, sk: so.sk || '', por: so.por,
      f: so.f, st: so.st || 'active', loc: baseByName(so.c), unit: null, loy: 100, merit: 0, acted: false, y: so.y || 0, j: so.j || null, capF: -1, dest: -1, eta: 0, pf: so.f };
    if (o.f >= 0) {
      if (SCENARIO.factions[o.f].n === o.n) { G.factions[o.f].lord = i; o.merit = 2000; }
      else { o.merit = Math.max(0, (o.ldr + o.war - 120) * 20); }
    }
    G.officers.push(o);
  }
  for (i = 0; i < G.officers.length; i++) { var lo = G.officers[i]; if (lo.f >= 0 && G.factions[lo.f].lord !== lo.id) lo.loy = loyNat(lo); }   // 군주가 정해진 뒤에 매긴다
  G.peace = { until: 1 + peaceTurns(G.player), broken: {}, v: 2 };      // 초반 보호: until 턴부터 AI 가 플레이어의 거점을 칠 수 있다. v = 기간 표의 판(2 = v0.9.1 의 18/12/9턴)
  for (i = 0; i < G.factions.length; i++) autoAdvisor(i);          // 군사: 처음에는 지력이 가장 높은 무장(군주 제외)
  reindex();
  REPORT = []; EVQ = [];
  phaseStart(G.player);
  REPORT = [];
  return G;
}

/* ---------- 수입 ---------- */
function adjFacCount(b, pi, type) {
  var p = b.plots[pi], n = 0, ns = nbrs(p.c, p.r);
  for (var i = 0; i < ns.length; i++) { var q = PAT[K(ns[i][0], ns[i][1])]; if (q && q.b === b.id) { var f = b.plots[q.i].fac; if (f && f.done && f.t === type) n++; } }
  return n;
}
function goldIncome(b) {
  if (b.kind !== 'city' || b.owner < 0) return 0;
  var v = BASE_GOLD[b.sz];
  for (var i = 0; i < b.plots.length; i++) { var f = b.plots[i].fac; if (f && f.done && f.t === 'market') v += MARKET_INC[f.lv] * (1 + 0.5 * Math.min(2, adjFacCount(b, i, 'mint'))); }
  v *= 0.5 + 0.5 * b.order / 100;
  if (baseHasSkill(b, '부호')) v *= 1.2;
  return Math.round(v);
}
function foodIncome(b) {
  if (b.kind !== 'city' || b.owner < 0) return 0;
  var v = BASE_FOOD[b.sz];
  for (var i = 0; i < b.plots.length; i++) { var f = b.plots[i].fac; if (f && f.done && f.t === 'farm') v += FARM_INC[f.lv] * (1 + 0.5 * Math.min(2, adjFacCount(b, i, 'granary'))); }
  v *= 0.5 + 0.5 * b.order / 100;
  if (baseHasSkill(b, '미도')) v *= 1.2;
  return Math.round(v);
}
function apRegen(f) {
  var nc = facCities(f).length;
  if (f === G.player && !G.aiOnly && G.corps && G.corps.length) nc = directBases(f).filter(function (b) { return b.kind === 'city'; }).length;      // 군단에 맡긴 도시는 군단의 행동력으로 센다
  var L = off(G.factions[f].lord), v = 50 + 8 * nc + Math.floor(L.cha / 5);
  var os = facOfficers(f);
  if (anyHas(os, '지도')) v += 10;
  if (anyHas(os, '왕좌')) v += 15;
  return Math.min(160, v);
}

/* ---------- 턴 진행 ---------- */
function phaseStart(f) {
  if (f === G.player && G.peace && !G.aiOnly) {                    // 보호가 끝나 가는 것을 미리 알린다
    var pl = G.peace.until - G.turn, cap = facCities(f)[0] || facBases(f)[0];
    if (pl === 3 && cap) { logMsg('초반 보호가 30일 남았습니다', cap.c, cap.r, f, 2); ev({ t: 'news', f: f, c: cap.c, r: cap.r, warn: 1, text: '<b>초반 보호가 30일 남았습니다</b>' }); }
    if (pl === 0 && cap) { logMsg('초반 보호가 끝났습니다', cap.c, cap.r, f, 2); ev({ t: 'news', f: f, c: cap.c, r: cap.r, warn: 1, text: '<b>초반 보호가 끝났습니다</b>' }); }
  }
  var F = G.factions[f], i;
  if (!F.alive) return;
  if (f === G.player && !G.aiOnly) corpsFix();
  if (!facAdv(f)) {                                                // 군사 자리가 비었으면 채운다
    var hadAdv = F.adv !== undefined && F.adv >= 0, na = autoAdvisor(f);
    if (f === G.player && !G.aiOnly && na && G.turn > 1) logMsg((hadAdv ? '군사 자리가 비어 ' : '') + josa(na.n, '을를') + ' 군사로 삼았다 (지력 ' + na.int + ')', undefined, undefined, f, 1);
  }
  F.ap = Math.min(255, F.ap + apRegen(f));
  for (i = 0; i < G.officers.length; i++) {
    var o = G.officers[i];
    if (o.f !== f) continue;
    if (o.st === 'active') o.acted = !!jobOf(o);                  // 공사를 맡은 무장은 완공될 때까지 쉬지 못한다
    else if (o.st === 'travel') {
      o.eta--;
      if (o.eta <= 0) {
        var db = G.bases[o.dest];
        if (!db || db.owner !== f) { var nb = nearestOwnBase(f, G.bases[o.loc].c, G.bases[o.loc].r); db = nb; }
        if (db) { o.st = 'active'; o.loc = db.id; o.acted = false; }
        else { o.st = 'free'; o.f = -1; o.loc = cityOf(o.loc); }
      }
    }
  }
  var bs = facBases(f);
  for (i = 0; i < bs.length; i++) {
    var b = bs[i];
    for (var j = 0; j < b.plots.length; j++) {
      var fc = b.plots[j].fac;
      if (fc && fc.done && fc.hp < FAC_HP && !G.fires[K(b.plots[j].c, b.plots[j].r)]) fc.hp = Math.min(FAC_HP, fc.hp + 100);
      if (fc && !fc.done) {
        fc.prog += fc.rate;
        if (fc.prog >= fc.need) {
          var who = builders(fc).map(function (x) { return x.n; });
          freeBuilders(fc, false); fc.done = true; fc.hp = FAC_HP;
          if (f === G.player) logMsg(b.n + '에 ' + FAC[fc.t].name + ' 완공' + (who.length ? ' — ' + who.join('·') + ' 복귀' : ''), b.plots[j].c, b.plots[j].r, f, 1);
        }
      }
    }
  }
  var us = facUnits(f);
  for (i = 0; i < us.length; i++) {
    var u = us[i];
    if (!UMAP[u.id]) continue;
    u.mp = uMaxMp(u); u.done = false; u.moved = false; u.ox = -1;
    // 군량
    var need = Math.ceil(u.troops / (uHas(u, '둔전') ? 40 : 20));
    if (u.food >= need) u.food -= need;
    else {
      u.food = 0;
      var loss = Math.max(100, Math.round(u.troops * 0.12));
      u.troops -= loss; u.morale = Math.max(0, u.morale - 15);
      if (f === G.player) logMsg(uName(u) + ' 군량이 떨어져 병사 ' + nf(loss) + '명 이탈', u.c, u.r, f, 2);
      if (u.troops <= 0) { destroyUnit(u, -1); continue; }
    }
    // 불
    if (G.fires[K(u.c, u.r)] && !uHas(u, '화신')) {
      var fd = ri(250, 400);
      u.morale = Math.max(0, u.morale - 5);
      if (f === G.player) logMsg(uName(u) + ' 불길에 ' + nf(fd) + '명 피해', u.c, u.r, f, 1);
      if (hurtUnit(u, fd, -1)) continue;
    }
    // 상태
    if (u.status) {
      if (u.stT <= 0) { if (f === G.player && !G.aiOnly) logMsg(uName(u) + ' ' + statusName(u.status) + '에서 벗어남', u.c, u.r, f, 1); u.status = null; }
      else {
        u.stT--;
        if (u.status === 'rumor') autoRetreat(u);
        if (UMAP[u.id]) {
          u.done = true; u.stSkip = G.turn;                         // 이 턴을 건너뛴다(화면이 '이번 턴 포함 N턴'을 셀 수 있게 적어 둔다)
          if (f === G.player && !G.aiOnly) logMsg(uName(u) + ' ' + statusName(u.status) + (u.status === 'rumor' ? ' — 명령을 듣지 않고 물러남' : ' — 움직이지 못함') + (u.stT > 0 ? ' (이번 턴 포함 ' + (u.stT + 1) * 10 + '일)' : ' (다음 턴에 풀림)'), u.c, u.r, f, 1);
        }
      }
    }
  }
}

function roundEnd() {
  var k, i;
  // 불: 번짐·소멸
  var keys = Object.keys(G.fires);
  for (i = 0; i < keys.length; i++) {
    k = +keys[i];
    var c = k % W, r = (k - c) / W;
    var pf = PAT[k];
    if (pf) { var fc = G.bases[pf.b].plots[pf.i].fac; if (fc) { fc.hp -= 200; if (fc.hp <= 0) { G.bases[pf.b].plots[pf.i].fac = null; logMsg(G.bases[pf.b].n + '의 ' + FAC[fc.t].name + ' 소실', c, r, G.bases[pf.b].owner, 1); } } }
    if (G.fires[k] >= 2) {
      var ns = nbrs(c, r);
      for (var j = 0; j < ns.length; j++) { var nk = K(ns[j][0], ns[j][1]); if (!G.fires[nk] && terr(ns[j][0], ns[j][1]) === 'f' && chance(20)) G.fires[nk] = 2; }
    }
    G.fires[k]--;
    if (G.fires[k] <= 0) delete G.fires[k];
  }
  pastSweep();                                                        // 섬겼던 세력을 적어 둔다(v0.11)
  // 날짜
  G.turn++; G.xun++;
  if (G.xun > 2) { G.xun = 0; G.month++; if (G.month > 12) { G.month = 1; G.year++; } }
  var newMonth = G.xun === 0, newQuarter = newMonth && (G.month === 1 || G.month === 4 || G.month === 7 || G.month === 10), newYear = newMonth && G.month === 1;
  dipTurn(); if (newMonth) dipMonth(); else if (G.dip) G.dip.offers = [];      // v0.14: 외교
  var pg = 0, pfood = 0;
  for (i = 0; i < G.bases.length; i++) {
    var b = G.bases[i];
    if (b.owner < 0 || b.kind !== 'city') continue;
    if (newMonth) { var gi = goldIncome(b); b.gold += gi; if (b.owner === G.player) pg += gi; if (b.order > 50) b.order--; }
    if (newQuarter) { var fi = foodIncome(b); b.food += fi; if (b.owner === G.player) pfood += fi; }
    var need = Math.ceil(b.troops / 60);
    if (b.food >= need) b.food -= need;
    else if (b.troops > 0) {
      b.food = 0; var loss = Math.round(b.troops * 0.05); b.troops -= loss; b.order = Math.max(0, b.order - 3);
      if (b.owner === G.player) logMsg(b.n + ' 병량이 바닥나 병사 ' + nf(loss) + '명 이탈', b.c, b.r, b.owner, 2);
    }
    if (b.dur < b.maxDur) b.dur = Math.min(b.maxDur, b.dur + 20);
  }
  for (i = 0; i < G.bases.length; i++) { var gb = G.bases[i]; if (gb.kind === 'gate' && gb.owner >= 0 && gb.dur < gb.maxDur) gb.dur = Math.min(gb.maxDur, gb.dur + 20); }
  if (newMonth && pg) logMsg('금 수입 +' + nf(pg), undefined, undefined, G.player, 1);
  if (newQuarter && pfood) logMsg('병량 수확 +' + nf(pfood), undefined, undefined, G.player, 1);
  if (newQuarter) {
    for (i = 0; i < G.officers.length; i++) {
      var o = G.officers[i];
      if (o.st !== 'active' || o.f < 0 || isLord(o)) continue;
      var nat = loyNat(o);
      if (nat >= 100) o.loy = 100;                                       // 인연: 내려가지 않는다
      else if (o.loy > nat) { if (chance(30)) o.loy--; }                 // 포상으로 올린 몫은 천천히 빠진다
      else if (o.loy < nat) o.loy = Math.min(nat, o.loy + 2);            // 새로 온 무장은 분기마다 2씩 자리를 잡는다
      if (o.loy < 50 && o.unit === null && chance(8)) {
        logMsg(josa(o.n, '이가') + ' ' + facName(o.f) + ' 진영을 떠났다', G.bases[o.loc].c, G.bases[o.loc].r, o.f, 1);
        o.f = -1; o.st = 'free'; o.loc = cityOf(o.loc);
      }
    }
  }
  if (newYear) {
    for (i = 0; i < G.officers.length; i++) {
      var h = G.officers[i];
      if (h.st !== 'hidden' || !h.j || h.y > G.year) continue;
      var lf = -1;
      for (var q = 0; q < G.factions.length; q++) if (G.factions[q].alive && G.factions[q].name === h.j) lf = q;
      if (lf >= 0) {
        var L = off(G.factions[lf].lord), lb = (L.unit === null) ? G.bases[L.loc] : nearestOwnBase(lf, UMAP[L.unit].c, UMAP[L.unit].r);
        if (lb && lb.owner === lf) { h.st = 'active'; h.f = lf; h.loc = lb.id; h.loy = 95; h.j = null; if (bondOf(h)) h.loy = 100; logMsg(josa(h.n, '이가') + ' 장성하여 ' + facName(lf) + ' 진영에 가담', lb.c, lb.r, lf, 1); continue; }
      }
      h.j = null;
    }
  }
}

/* 턴 진행을 잘게 쪼갠 실행기. 부를 때마다 한 단계 나아가고 {kind} 를 돌려준다(끝나면 null).
   kind: 'phase' 세력 차례 시작 · 'step' 그 세력의 한 행동 · 'round' 날짜가 넘어감 · 'start' 내 차례 시작.
   화면은 단계 사이사이에 EVQ(사건)를 읽어 보여 준다. endTurn() 은 이것을 끝까지 돌린 것과 같다. */
function turnStepper() {
  var f = -1, st = null, stage = 0;
  var cps = (!G.aiOnly && G.corps && G.corps.length) ? G.corps.slice() : [], ci = 0, cur = null;      // 군단(v0.10): 내 차례의 끝에, 다른 세력보다 먼저
  if (cps.length) stage = -1;
  return function () {
    if (G.over) { JOT = null; return null; }
    if (stage === -1) {
      if (st) { if (st()) return { kind: 'step', f: G.player, corps: cur.id }; st = null; corpsEnd(cur); if (G.over) return null; }
      while (ci < cps.length) {
        cur = cps[ci++];
        if (!corpsStart(cur)) continue;
        st = corpsStepper(cur);
        return { kind: 'corps', f: G.player, corps: cur.id };
      }
      stage = 0;
    }
    if (stage === 0) {
      if (st) { if (st()) return { kind: 'step', f: f }; st = null; if (G.over) return null; }
      for (f = f + 1; f < G.factions.length; f++) {
        if ((f === G.player && !G.aiOnly) || !G.factions[f].alive) continue;
        phaseStart(f); st = aiPhaseStepper(f);
        return { kind: 'phase', f: f };
      }
      stage = 1; roundEnd();
      return { kind: 'round' };
    }
    if (stage === 1) { stage = 2; if (!G.aiOnly) phaseStart(G.player); checkVictory(); return { kind: 'start' }; }
    return null;
  };
}
function marchList(f) {
  return facUnits(f).filter(function (u) { return UMAP[u.id] && !u.done && u.dest >= 0; }).sort(function (a, b) { return a.id - b.id; });
}
function endTurn() {
  if (G.over) return;
  REPORT = []; EVQ = [];
  if (!G.aiOnly) marchList(G.player).forEach(function (u) { if (UMAP[u.id]) unitMarch(u); });
  var next = turnStepper();
  while (next()) { EVQ.length = 0; }
}

/* ---------- 거점·세력 ---------- */
function nearestOwnBase(f, c, r, exceptId) {
  var best = null, bd = 1e9;
  for (var i = 0; i < G.bases.length; i++) { var b = G.bases[i]; if (b.owner !== f || b.id === exceptId) continue; var d = hdist(c, r, b.c, b.r) + (b.kind === 'gate' ? 3 : 0); if (d < bd) { bd = d; best = b; } }
  return best;
}
function nearestCity(c, r) {
  var best = null, bd = 1e9;
  for (var i = 0; i < G.bases.length; i++) { var b = G.bases[i]; if (b.kind !== 'city') continue; var d = hdist(c, r, b.c, b.r); if (d < bd) { bd = d; best = b; } }
  return best;
}
function checkFaction(f) {
  if (f < 0) return;
  var F = G.factions[f];
  if (!F.alive) return;
  if (facBases(f).length > 0) return;
  F.alive = false;
  var us = facUnits(f), i;
  for (i = 0; i < us.length; i++) {
    var u = us[i], nc = nearestCity(u.c, u.r);
    for (var j = 0; j < u.off.length; j++) { var o = off(u.off[j]); o.unit = null; o.f = -1; o.st = 'free'; o.loc = nc.id; }
    removeUnit(u);
  }
  for (i = 0; i < G.officers.length; i++) {
    var p = G.officers[i];
    if (p.f === f && (p.st === 'active' || p.st === 'travel')) { p.f = -1; p.st = 'free'; p.unit = null; p.loc = cityOf(p.loc); }
    else if (p.f === f && p.st === 'captive') { p.f = -1; }
    if (p.st === 'captive' && p.capF === f) { releaseCaptive(p); }
  }
  logMsg(F.name + ' 세력이 멸망했다', undefined, undefined, f, 3);
  ev({ t: 'fallen', f: f });
  checkVictory();
}
function checkVictory() {
  if (G.over) return;
  if (!G.factions[G.player].alive && !G.aiOnly) { G.over = 'lose'; return; }
  var alive = G.factions.filter(function (x) { return x.alive; });
  if (alive.length === 1 && alive[0].id === G.player) { G.over = 'win'; return; }
  var cities = G.bases.filter(function (b) { return b.kind === 'city'; });
  if (!G.aiOnly && cities.every(function (b) { return b.owner === G.player; })) G.over = 'win';
}

function cityOf(baseId) { var b = G.bases[baseId]; return b.kind === 'city' ? baseId : nearestCity(b.c, b.r).id; }
function nearestOwnCity(f, c, r) {
  var best = null, bd = 1e9;
  for (var i = 0; i < G.bases.length; i++) { var b = G.bases[i]; if (b.owner !== f || b.kind !== 'city') continue; var d = hdist(c, r, b.c, b.r); if (d < bd) { bd = d; best = b; } }
  return best;
}
function releaseCaptive(o) {
  var hb = G.bases[o.loc];
  var idx = hb.captives.indexOf(o.id);
  if (idx >= 0) hb.captives.splice(idx, 1);
  o.capF = -1;
  if (o.f >= 0 && G.factions[o.f].alive) {
    var nb = nearestOwnBase(o.f, hb.c, hb.r);
    if (nb) { o.st = 'active'; o.loc = nb.id; o.acted = true; o.unit = null; return; }
  }
  o.f = -1; o.st = 'free';
  if (hb.kind !== 'city') o.loc = nearestCity(hb.c, hb.r).id;
}
function captureOfficer(o, byF, holdBase) {
  o.unit = null; o.st = 'captive'; o.capF = byF; o.loc = holdBase.id; o.acted = true;
  holdBase.captives.push(o.id);
}
function fleeOfficer(o, c, r, exceptBase) {
  var nb = nearestOwnBase(o.f, c, r, exceptBase);
  o.unit = null;
  if (nb) { o.st = 'active'; o.loc = nb.id; o.acted = true; }
  else { o.st = 'free'; o.f = -1; var nc = nearestCity(c, r); o.loc = nc.id; }
}

function addUnit(u) { G.units.push(u); UMAP[u.id] = u; UAT[K(u.c, u.r)] = u; }
function removeUnit(u) {
  var i = G.units.indexOf(u);
  if (i >= 0) G.units.splice(i, 1);
  delete UMAP[u.id];
  if (UAT[K(u.c, u.r)] === u) delete UAT[K(u.c, u.r)];
}
function placeUnit(u, c, r) {
  if (UAT[K(u.c, u.r)] === u) delete UAT[K(u.c, u.r)];
  u.c = c; u.r = r; UAT[K(c, r)] = u;
}
function destroyUnit(u, byF) {
  var hold = byF >= 0 ? (nearestOwnCity(byF, u.c, u.r) || nearestOwnBase(byF, u.c, u.r)) : null;
  var capP = 25;
  for (var i = 0; i < u.off.length; i++) {
    var o = off(u.off[i]);
    if (hold && !isLord(o) && chance(capP * (u._capMul || 1))) {
      captureOfficer(o, byF, hold);
      logMsg(o.n + ' 사로잡힘 (' + facName(byF) + ')', u.c, u.r, o.f, (u.f === G.player || byF === G.player) ? 2 : 0);
    } else fleeOfficer(o, u.c, u.r);
  }
  logMsg(facName(u.f) + '의 ' + uName(u) + ' 궤멸', u.c, u.r, u.f, (u.f === G.player || byF === G.player) ? 2 : 0);
  ev({ t: 'dead', c: u.c, r: u.r });
  var f = u.f;
  removeUnit(u);
  checkFaction(f);
}
/* 병력 피해. 궤멸하면 true */
function hurtUnit(u, dmg, byF, byUnit) {
  u.troops -= dmg;
  if (u.troops <= 0) {
    u.troops = 0;
    u._capMul = (byUnit && uHas(byUnit, '포박')) ? 2 : 1;
    if (byUnit) addMerit(byUnit, 150);
    destroyUnit(u, byF);
    return true;
  }
  return false;
}
function addMerit(u, v) { for (var i = 0; i < u.off.length; i++) off(u.off[i]).merit += v; }

function enterBase(u, b) {
  var nt = b.troops + u.troops;
  b.morale = nt > 0 ? Math.round((b.troops * b.morale + u.troops * u.morale) / nt) : u.morale;
  b.troops = nt; b.food += u.food; b.gold += u.gold;
  var wp = UNIT_TYPES[u.type].weapon;
  if (wp === 'ram') b.w.ram += 1; else if (wp) b.w[wp] += u.troops;
  if (u.cargo) for (var k in u.cargo) b.w[k] += u.cargo[k];
  for (var i = 0; i < u.off.length; i++) { var o = off(u.off[i]); o.unit = null; o.loc = b.id; o.acted = true; }
  removeUnit(u);
}
function captureBase(b, u) {
  var old = b.owner, i;
  for (i = 0; i < b.plots.length; i++) { var uf = b.plots[i].fac; if (uf && !uf.done) { freeBuilders(uf, true); b.plots[i].fac = null; } }   // 짓다 만 시설은 버려진다
  if (old >= 0) {
    var os = baseOfficers(b), otherBases = facBases(old).length > 1;
    for (i = 0; i < os.length; i++) {
      var o = os[i];
      if (isLord(o)) { if (otherBases) fleeOfficer(o, b.c, b.r, b.id); else captureOfficer(o, u.f, b); }
      else if (chance(uHas(u, '포박') ? 60 : 40) || !otherBases) { captureOfficer(o, u.f, b); }
      else fleeOfficer(o, b.c, b.r, b.id);
    }
    for (i = 0; i < G.officers.length; i++) { var t = G.officers[i]; if (t.st === 'travel' && t.f === old && t.loc === b.id) t.loc = (nearestOwnBase(old, b.c, b.r, b.id) || b).id; }
    var held = b.captives.slice();
    for (i = 0; i < held.length; i++) {
      var cp = off(held[i]);
      if (cp.capF !== old) continue;
      if (cp.f === u.f) { b.captives.splice(b.captives.indexOf(cp.id), 1); cp.st = 'active'; cp.capF = -1; cp.loc = b.id; cp.acted = true; logMsg(cp.n + ' 구출', b.c, b.r, u.f, 1); }
      else releaseCaptive(cp);
    }
  }
  logMsg(old >= 0 ? josa(facName(u.f) + '군', '이가') + ' ' + josa(b.n, '을를') + (b.kind === 'gate' ? ' 점령' : ' 함락') + ' (' + facName(old) + '군의 땅)' : josa(facName(u.f) + '군', '이가') + ' 주인 없는 ' + josa(b.n, '을를') + ' 차지', b.c, b.r, old >= 0 ? old : u.f, old === G.player || u.f === G.player ? 3 : 2);
  ev({ t: 'fall', b: b.id, by: u.f, old: old });
  b.owner = u.f; b.troops = 0;
  if (b.corps || u.corps) b.corps = (u.f === G.player && !G.aiOnly && u.corps && corpsById(u.corps)) ? u.corps : 0;      // 군단의 부대가 차지한 거점은 그 군단에 든다
  b.dur = Math.max(b.dur, Math.round(b.maxDur * 0.3));
  if (b.kind === 'city') b.order = Math.max(20, b.order - 25);
  addMerit(u, 300);
  enterBase(u, b);
  checkFaction(old);
  checkVictory();
}

/* ---------- 군단(v0.10) ----------
   플레이어가 제 거점을 묶어 군단장에게 맡긴다. 맡긴 거점과 거기서 나간 부대는 군단장이 방침대로 움직인다(ai.js 의 corpsStepper).
     G.corps = [{ id, n(번호: 제n군단), lead(군단장 무장 id, 비면 -1), dir, target(거점 id, 없으면 -1), ap, t0(만든 턴), note(지난 차례의 보고) }]
     거점 b.corps · 부대 u.corps = 군단 id (직할이면 0 이거나 없다)
   방침 dir: 'dev' 내정 · 'arm' 군비 · 'atk' 공격(target = 칠 거점) · 'sup' 지원(target = 병력·물자를 보낼 내 거점)
   군단은 제 행동력(ap)을 따로 가진다. 직할의 행동력은 직할 도시만 센다(apRegen). AI 세력에는 군단이 없다. */
function corpsAll() { return G.corps || (G.corps = []); }
function corpsById(id) { var cs = G.corps || [], i; if (!id) return null; for (i = 0; i < cs.length; i++) if (cs[i].id === id) return cs[i]; return null; }
function corpsName(cp) { return '제' + cp.n + '군단'; }
function corpsBases(cp) { return G.bases.filter(function (b) { return b.owner === G.player && b.corps === cp.id; }); }
function corpsCities(cp) { return G.bases.filter(function (b) { return b.owner === G.player && b.corps === cp.id && b.kind === 'city'; }); }
function corpsUnits(cp) { return G.units.filter(function (u) { return u.f === G.player && u.corps === cp.id; }); }
function baseCorps(b) { return (b && b.owner === G.player && b.corps) ? corpsById(b.corps) : null; }       // 그 거점을 맡은 군단(직할이면 null)
function unitCorps(u) { return (u && u.f === G.player && u.corps) ? corpsById(u.corps) : null; }
function directBases(f) { return G.bases.filter(function (b) { return b.owner === f && !(f === G.player && b.corps && corpsById(b.corps)); }); }
function directUnits(f) { return G.units.filter(function (u) { return u.f === f && !(f === G.player && u.corps && corpsById(u.corps)); }); }
function corpsTroops(cp) { var t = 0; corpsBases(cp).forEach(function (b) { t += b.troops; }); corpsUnits(cp).forEach(function (u) { t += u.troops; }); return t; }
function corpsOfficers(cp) {
  return G.officers.filter(function (o) {
    if (o.f !== G.player) return false;
    if (o.unit !== null && o.unit !== undefined) { var u = UMAP[o.unit]; return !!u && u.corps === cp.id; }
    return o.st === 'active' && !!G.bases[o.loc] && G.bases[o.loc].owner === G.player && G.bases[o.loc].corps === cp.id;
  });
}
/* 군단장이 될 수 있는가: 군주가 아니고, 그 군단의 거점에 있거나 그 군단의 부대에 있다 */
function corpsLeadOk(cp, o) {
  if (!o || o.f !== G.player || isLord(o)) return false;
  if (o.unit !== null && o.unit !== undefined) { var u = UMAP[o.unit]; return !!u && u.corps === cp.id; }
  return o.st === 'active' && !!G.bases[o.loc] && G.bases[o.loc].owner === G.player && G.bases[o.loc].corps === cp.id;
}
function corpsLead(cp) { var o = (cp.lead !== undefined && cp.lead >= 0) ? off(cp.lead) : null; return corpsLeadOk(cp, o) ? o : null; }
function corpsLeadScore(o) { return o.ldr + o.int * 0.6 + o.cha * 0.6 + o.war * 0.3; }
function corpsLeadCands(cp) { return G.officers.filter(function (o) { return corpsLeadOk(cp, o); }).sort(function (a, b) { return corpsLeadScore(b) - corpsLeadScore(a) || a.id - b.id; }); }
function corpsRegen(cp) { var L = corpsLead(cp); return Math.min(CORPS_AP.max, CORPS_AP.base + CORPS_AP.city * corpsCities(cp).length + (L ? Math.floor(L.cha / 5) : 0)); }
/* 방침을 말로: "공격 → 여남" */
function corpsDirText(cp) {
  var T = (cp.target !== undefined && cp.target >= 0) ? G.bases[cp.target] : null;
  return CORPS_DIR[cp.dir] + ((cp.dir === 'atk' || cp.dir === 'sup') && T ? ' → ' + T.n : '');
}
function corpsDirOk(cp, dir, target) {
  if (!CORPS_DIR[dir]) return '없는 방침';
  if (dir === 'atk') { var T = G.bases[target]; if (!T || T.owner === G.player) return '칠 거점을 고르세요'; }
  if (dir === 'sup') { var D = G.bases[target]; if (!D || D.owner !== G.player) return '보낼 거점을 고르세요'; if (D.corps === cp.id) return '같은 군단의 거점에는 보낼 수 없습니다'; }
  return '';
}
function corpsSetDir(cp, dir, target) {
  var why = corpsDirOk(cp, dir, target); if (why) return ERR(why);
  cp.dir = dir; cp.target = (dir === 'atk' || dir === 'sup') ? target : -1;
  corpsUnits(cp).forEach(function (u) {                              // 이미 나가 있는 부대도 새 방침을 따른다(수송대는 가던 길을 간다)
    if (u.type === 'trans') return;
    if (dir === 'atk') u.ai = { mode: 'attack', target: cp.target, home: u.home };
    else if (u.ai && u.ai.mode === 'attack') u.ai = { mode: 'return', home: u.home };
  });
  return { ok: true };
}
function corpsSetLead(cp, id) {
  var o = off(id); if (!corpsLeadOk(cp, o)) return ERR('그 군단의 거점이나 부대에 있는 무장만 군단장이 될 수 있습니다(군주 제외)');
  cp.lead = o.id; return { ok: true };
}
/* 새 군단: 직할 거점들을 묶는다. 군단장을 주지 않으면 가장 알맞은 사람이 맡는다. 방침을 주지 않으면 군비 */
function corpsCreate(baseIds, leadId, dir, target) {
  if (G.aiOnly) return ERR('AI 대전에는 군단이 없습니다');
  var cs = corpsAll(), i, bs = [];
  if (cs.length >= CORPS_MAX) return ERR('군단은 ' + CORPS_MAX + '개까지 둘 수 있습니다');
  if (!baseIds || !baseIds.length) return ERR('맡길 거점을 고르세요');
  for (i = 0; i < baseIds.length; i++) { var b = G.bases[baseIds[i]]; if (!b || b.owner !== G.player) return ERR('내 거점만 맡길 수 있습니다'); if (baseCorps(b)) return ERR(b.n + '은(는) 이미 군단에 맡겼습니다'); bs.push(b); }
  var n = 1, used = {}; cs.forEach(function (c) { used[c.n] = 1; }); while (used[n]) n++;
  G.nextCorps = (G.nextCorps || 1);
  var cp = { id: G.nextCorps++, n: n, lead: -1, dir: 'arm', target: -1, ap: 0, t0: G.turn, note: null };
  cs.push(cp); cs.sort(function (x, y) { return x.n - y.n; });
  bs.forEach(function (b2) { b2.corps = cp.id; });
  var c2 = corpsLeadCands(cp);
  if (!c2.length) { corpsDisband(cp); return ERR('군단장을 맡을 무장이 없습니다 — 군주 말고 무장이 있는 거점을 넣으세요'); }
  cp.lead = (leadId !== undefined && leadId >= 0 && corpsLeadOk(cp, off(leadId))) ? leadId : c2[0].id;
  if (dir && dir !== 'arm') { var r = corpsSetDir(cp, dir, target); if (!r.ok) { corpsDisband(cp); return r; } }
  return { ok: true, corps: cp };
}
/* 거점을 군단에 넣는다(직할이든 다른 군단의 것이든) */
function corpsAssign(cp, baseId) {
  var b = G.bases[baseId];
  if (!b || b.owner !== G.player) return ERR('내 거점만 맡길 수 있습니다');
  if (b.corps === cp.id) return ERR('이미 이 군단의 거점입니다');
  var old = baseCorps(b);
  b.corps = cp.id;
  if (cp.dir === 'sup' && cp.target === b.id) { cp.dir = 'arm'; cp.target = -1; }      // 보내던 곳이 제 거점이 되었다
  if (old) corpsFix();
  return { ok: true };
}
/* 거점을 직할로 되돌린다. 거점이 남지 않은 군단은 해산된다 */
function corpsRelease(baseId) {
  var b = G.bases[baseId], cp = baseCorps(b);
  if (!cp) return ERR('직할 거점입니다');
  b.corps = 0;
  corpsFix();
  return { ok: true, gone: !corpsById(cp.id) };
}
function corpsTakeUnit(u) { if (!unitCorps(u)) return ERR('직할 부대입니다'); u.corps = 0; u.ai = null; return { ok: true }; }      // 부대를 직할로
function corpsDisband(cp) {
  G.bases.forEach(function (b) { if (b.corps === cp.id) b.corps = 0; });
  G.units.forEach(function (u) { if (u.corps === cp.id) { u.corps = 0; if (u.f === G.player) u.ai = null; } });
  var cs = corpsAll(), i = cs.indexOf(cp); if (i >= 0) cs.splice(i, 1);
  return { ok: true };
}
/* 뒤처리: 잃은 거점의 표시 지우기 · 거점이 없는 군단 해산 · 빈 군단장 자리 채우기 · 이룬(또는 어긋난) 방침 돌리기. 바뀐 것은 기록에 남긴다 */
function corpsFix() {
  if (!G.corps || !G.corps.length) return;
  var i, cs = G.corps.slice();
  G.bases.forEach(function (b) { if (b.corps && (b.owner !== G.player || !corpsById(b.corps))) b.corps = 0; });
  for (i = 0; i < cs.length; i++) {
    var cp = cs[i], bs = corpsBases(cp), nm = corpsName(cp), cap = bs[0];
    if (!bs.length) {
      var us = corpsUnits(cp);
      corpsDisband(cp);
      logMsg(nm + ' 해산 — 맡은 거점이 없습니다' + (us.length ? ' (부대 ' + us.length + '개는 직할로)' : ''), us.length ? us[0].c : undefined, us.length ? us[0].r : undefined, G.player, 2);
      continue;
    }
    if (!corpsLead(cp)) {
      var had = cp.lead !== undefined && cp.lead >= 0 ? off(cp.lead) : null, c2 = corpsLeadCands(cp);
      cp.lead = c2.length ? c2[0].id : -1;
      if (c2.length) logMsg(nm + ' — ' + (had ? josa(had.n, '이가') + ' 자리를 비워 ' : '') + josa(c2[0].n, '이가') + ' 군단장을 맡았다', cap.c, cap.r, G.player, 1);
      else if (had) logMsg(nm + ' — 군단장 자리가 비었습니다(맡을 무장이 없습니다)', cap.c, cap.r, G.player, 2);
    }
    var T = (cp.target !== undefined && cp.target >= 0) ? G.bases[cp.target] : null;
    if (cp.dir === 'atk' && (!T || T.owner === G.player)) {
      if (T) { logMsg(nm + ' — ' + josa(T.n, '을를') + ' 손에 넣어 방침을 군비로 돌렸다', T.c, T.r, G.player, 2); ev({ t: 'news', f: G.player, c: T.c, r: T.r, text: '<b>' + nm + '</b> — ' + josa(T.n, '을를') + ' 손에 넣었습니다. 방침을 <b>군비</b>로 돌립니다' }); }
      corpsSetDir(cp, 'arm', -1);
    } else if (cp.dir === 'sup' && (!T || T.owner !== G.player || T.corps === cp.id)) {
      logMsg(nm + ' — 보낼 거점이 없어져 방침을 군비로 돌렸다', cap.c, cap.r, G.player, 2);
      corpsSetDir(cp, 'arm', -1);
    }
  }
  G.units.forEach(function (u) { if (u.corps && (u.f !== G.player || !corpsById(u.corps))) { u.corps = 0; if (u.f === G.player) u.ai = null; } });
}
/* 군단의 차례: 시작(행동력을 채우고 한 일을 적을 준비) → ai.js 의 corpsStepper → 끝(한 일을 한 줄로 기록) */
var JOT = null;                                                   // 군단의 차례를 돌리는 동안만 배열: 그 군단이 한 일
function jot(k, b, n, x) { if (JOT) JOT.push({ k: k, b: b ? b.id : -1, n: n || 0, x: x }); }
function corpsStart(cp) {
  corpsFix();
  if (!corpsById(cp.id)) return false;
  cp.ap = Math.min(CORPS_AP.cap, (cp.ap || 0) + corpsRegen(cp));
  JOT = [];
  return true;
}
function corpsNoteText(J) {
  var d = { draft: 0, patrol: 0, train: 0, search: 0, reward: 0, trade: 0, fights: 0, sieges: 0 }, prod = {}, built = [], merged = [], joined = [], out = [], sent = 0, sentN = 0, sup = 0, supN = 0, moved = 0, i;
  for (i = 0; i < J.length; i++) {
    var e = J[i];
    if (e.k === 'draft') d.draft += e.n;
    else if (e.k === 'patrol') d.patrol++;
    else if (e.k === 'train') d.train++;
    else if (e.k === 'produce') prod[e.x] = (prod[e.x] || 0) + e.n;
    else if (e.k === 'develop') built.push(FAC[e.x].name);
    else if (e.k === 'merge') merged.push(FAC[e.x].name + ' Lv' + e.n);
    else if (e.k === 'search') d.search++;
    else if (e.k === 'recruit') { if (e.n) joined.push(off(e.x).n); }
    else if (e.k === 'reward') d.reward++;
    else if (e.k === 'trade') d.trade++;
    else if (e.k === 'move') moved += e.n;
    else if (e.k === 'deploy') { if (e.x === 'trans') { sup++; supN += e.n; } else { sent++; sentN += e.n; } }
    else if (e.k === 'act') d.fights++;
    else if (e.k === 'siege') d.sieges++;
  }
  if (sent) out.push(sent + '부대 출진(' + nf(sentN) + '명)');
  if (d.sieges) out.push('성 공격 ' + d.sieges + '회');
  if (d.fights) out.push('싸움 ' + d.fights + '회');
  if (sup) out.push('수송 ' + sup + '대(' + nf(supN) + '명)');
  if (d.draft) out.push('징병 +' + nf(d.draft));
  for (var k in prod) out.push(WEAPON_NAMES[k] + ' +' + nf(prod[k]));
  if (built.length) out.push(built.join('·') + ' 착공');
  if (merged.length) out.push(merged.join('·') + ' 합병');
  if (joined.length) out.push(joined.join('·') + ' 등용');
  if (d.train) out.push('훈련' + (d.train > 1 ? ' ' + d.train : ''));
  if (d.patrol) out.push('순찰' + (d.patrol > 1 ? ' ' + d.patrol : ''));
  if (d.search) out.push('탐색' + (d.search > 1 ? ' ' + d.search : ''));
  if (d.reward) out.push('포상 ' + d.reward);
  if (d.trade) out.push('거래' + (d.trade > 1 ? ' ' + d.trade : ''));
  if (moved) out.push('무장 ' + moved + '명 이동');
  return out.join(' · ');
}
function corpsEnd(cp) {
  var J = JOT || []; JOT = null;
  if (!corpsById(cp.id)) return;
  corpsFix();
  if (!corpsById(cp.id)) return;
  var txt = corpsNoteText(J), L = corpsLead(cp), cap = corpsBases(cp)[0];
  cp.note = { t: G.turn, s: txt, n: J.length };
  var e = { d: dateStr(), t: corpsName(cp) + ' (' + (L ? L.n + ' · ' : '') + corpsDirText(cp) + ') — ' + (txt || '한 일 없음 (행동력 ' + cp.ap + ')'), c: cap ? cap.c : undefined, r: cap ? cap.r : undefined, f: G.player, imp: 1, corps: cp.id };
  G.log.push(e); if (G.log.length > 150) G.log.shift(); REPORT.push(e);
}

/* ---------- 내정 명령 ---------- */
function ERR(m) { return { ok: false, msg: m }; }
function needAP(f, n) { return G.factions[f].ap >= n; }
function useAP(f, n) { G.factions[f].ap -= n; }
function getIdle(b, ids) {
  var os = [];
  for (var i = 0; i < ids.length; i++) { var o = off(ids[i]); if (!o || o.st !== 'active' || o.f !== b.owner || o.loc !== b.id || o.unit !== null || o.acted) return null; os.push(o); }
  return os;
}
function markActed(os, merit) { for (var i = 0; i < os.length; i++) { os[i].acted = true; os[i].merit += merit || 0; } }

function cmdDevelop(b, pi, type, ids) {
  var p = b.plots[pi], F = FAC[type];
  if (!p || p.fac) return ERR('빈 부지가 아닙니다');
  if (!F) return ERR('없는 시설');
  var os = getIdle(b, ids); if (!os || !os.length || os.length > 3) return ERR('담당 무장을 고르세요');
  if (b.gold < F.cost) return ERR('금이 부족합니다 (' + F.cost + ' 필요)');
  if (!needAP(b.owner, AP.develop)) return ERR('행동력이 부족합니다');
  if (UAT[K(p.c, p.r)]) return ERR('부대가 있는 칸에는 지을 수 없습니다');
  b.gold -= F.cost; useAP(b.owner, AP.develop);
  var rate = 60 + Math.round((bestOf(os, 'pol') + sumOthers(os, 'pol') * 0.5) * 0.6);
  if (anyHas(os, '축성')) rate *= 2;
  p.fac = { t: type, lv: 1, done: false, prog: 0, need: F.build, rate: rate, hp: 300, by: os.map(function (o) { return o.id; }), t0: G.turn };
  jot('develop', b, 0, type);
  for (var i = 0; i < os.length; i++) os[i].job = { b: b.id, i: pi };
  markActed(os, 30);
  return { ok: true, turns: Math.ceil(F.build / rate) };
}
function mergeCandidates(b, pi) {
  var p = b.plots[pi], f = p.fac, out = [];
  if (!f || !f.done || f.lv >= 3) return out;
  var ns = nbrs(p.c, p.r);
  for (var i = 0; i < ns.length; i++) { var q = PAT[K(ns[i][0], ns[i][1])]; if (q && q.b === b.id) { var g = b.plots[q.i].fac; if (g && g.done && g.t === f.t && g.lv <= f.lv) out.push(q.i); } }
  return out;
}
function cmdMerge(b, pi, pj, ids) {
  var cands = mergeCandidates(b, pi);
  if (cands.indexOf(pj) < 0) return ERR('흡수할 수 있는 같은 종류의 인접 시설이 없습니다');
  var f = b.plots[pi].fac, cost = COST.merge * f.lv;
  var os = getIdle(b, ids); if (!os || os.length !== 1) return ERR('담당 무장을 고르세요');
  if (b.gold < cost) return ERR('금이 부족합니다 (' + cost + ' 필요)');
  if (!needAP(b.owner, AP.merge)) return ERR('행동력이 부족합니다');
  b.gold -= cost; useAP(b.owner, AP.merge);
  f.lv++; b.plots[pj].fac = null;
  markActed(os, 30); jot('merge', b, f.lv, f.t);
  return { ok: true, lv: f.lv };
}
function cmdDemolish(b, pi) {
  if (!b.plots[pi] || !b.plots[pi].fac) return ERR('시설이 없습니다');
  var f = b.plots[pi].fac, freed = builders(f).map(function (o) { return o.id; });
  if (!f.done) freeBuilders(f, f.t0 === G.turn);
  b.plots[pi].fac = null;
  return { ok: true, freed: freed };
}

function draftAmount(b, os) {
  var lv = bestFacLv(b, 'barracks');
  var v = (1200 + bestOf(os, 'cha') * 18 + sumOthers(os, 'cha') * 4) * LV_MUL[lv] * (0.4 + 0.6 * b.order / 100);
  if (anyHas(os, '명성')) v *= 1.5;
  return Math.round(v / 10) * 10;
}
function cmdDraft(b, ids) {
  if (b.kind !== 'city') return ERR('도시에서만 가능합니다');
  if (!hasFac(b, 'barracks')) return ERR('병영이 필요합니다');
  var os = getIdle(b, ids); if (!os || !os.length || os.length > 3) return ERR('담당 무장을 고르세요');
  if (b.gold < COST.draft) return ERR('금이 부족합니다 (' + COST.draft + ' 필요)');
  if (b.order < 20) return ERR('치안이 너무 낮습니다');
  if (!needAP(b.owner, AP.draft)) return ERR('행동력이 부족합니다');
  var n = draftAmount(b, os);
  b.gold -= COST.draft; useAP(b.owner, AP.draft); jot('draft', b, n);
  b.morale = Math.round((b.troops * b.morale + n * 35) / Math.max(1, b.troops + n));
  b.troops += n;
  b.order = Math.max(0, b.order - (anyHas(os, '인덕') ? 5 : 10));
  markActed(os, 30);
  return { ok: true, n: n };
}
function cmdPatrol(b, ids) {
  if (b.kind !== 'city') return ERR('도시에서만 가능합니다');
  var os = getIdle(b, ids); if (!os || !os.length || os.length > 3) return ERR('담당 무장을 고르세요');
  if (b.gold < COST.patrol) return ERR('금이 부족합니다 (' + COST.patrol + ' 필요)');
  if (!needAP(b.owner, AP.patrol)) return ERR('행동력이 부족합니다');
  var best = Math.max(bestOf(os, 'war'), bestOf(os, 'ldr'));
  var v = Math.round(5 + best / 9 + (os.length - 1) * 2);
  if (anyHas(os, '위압')) v *= 2;
  b.gold -= COST.patrol; useAP(b.owner, AP.patrol); jot('patrol', b, v);
  var before = b.order; b.order = Math.min(100, b.order + v);
  markActed(os, 20);
  return { ok: true, n: b.order - before };
}
function cmdTrain(b, ids) {
  var os = getIdle(b, ids); if (!os || !os.length || os.length > 3) return ERR('담당 무장을 고르세요');
  if (!needAP(b.owner, AP.train)) return ERR('행동력이 부족합니다');
  if (b.troops <= 0) return ERR('병력이 없습니다');
  var v = Math.round(8 + bestOf(os, 'ldr') / 8 + (os.length - 1) * 2);
  useAP(b.owner, AP.train); jot('train', b, v);
  var before = b.morale; b.morale = Math.min(100, b.morale + v);
  markActed(os, 20);
  return { ok: true, n: b.morale - before };
}
function produceAmount(b, kind, os) {
  var lv = bestFacLv(b, kind === 'horse' ? 'stable' : 'smithy');
  var v = (900 + bestOf(os, 'int') * 14 + sumOthers(os, 'int') * 3) * LV_MUL[lv];
  if (kind === 'horse') { v *= 0.8; if (anyHas(os, '번식')) v *= 1.5; }
  else if (anyHas(os, '능리')) v *= 1.5;
  return Math.round(v / 10) * 10;
}
function cmdProduce(b, kind, ids) {
  var os = getIdle(b, ids); if (!os || !os.length || os.length > 3) return ERR('담당 무장을 고르세요');
  var need = kind === 'ram' ? 'workshop' : (kind === 'horse' ? 'stable' : 'smithy');
  if (!hasFac(b, need)) return ERR(josa(FAC[need].name, '이가') + ' 필요합니다');
  var cost = kind === 'ram' ? (anyHas(os, '발명') ? COST.ramInv : COST.ram) : COST.produce;
  if (b.gold < cost) return ERR('금이 부족합니다 (' + cost + ' 필요)');
  if (!needAP(b.owner, AP.produce)) return ERR('행동력이 부족합니다');
  b.gold -= cost; useAP(b.owner, AP.produce);
  var n = kind === 'ram' ? 1 : produceAmount(b, kind, os);
  b.w[kind] += n; jot('produce', b, n, kind);
  markActed(os, 30);
  return { ok: true, n: n };
}
function cmdTrade(b, dir, gold) {
  if (!hasFac(b, 'market')) return ERR('시장이 필요합니다');
  if (!needAP(b.owner, AP.trade)) return ERR('행동력이 부족합니다');
  gold = Math.floor(gold);
  if (gold <= 0) return ERR('수량을 정하세요');
  if (dir === 'buy') { if (b.gold < gold) return ERR('금이 부족합니다'); b.gold -= gold; b.food += gold * 4; useAP(b.owner, AP.trade); jot('trade', b, gold, dir); return { ok: true, n: gold * 4 }; }
  if (b.food < gold * 6) return ERR('병량이 부족합니다');
  b.food -= gold * 6; b.gold += gold; useAP(b.owner, AP.trade); jot('trade', b, gold, dir);
  return { ok: true, n: gold };
}
/* 탐색(v0.11): 숨은 인재를 찾아낼 확률(%)과 그 주사위. 주사위는 거점 · 턴 · 그 턴의 몇 번째 탐색인가로 정해진다(누가 가도 같은 주사위 — 성공률만 다르다) */
function searchSkill(o) { return (25 + o.pol * 0.35 + o.cha * 0.15) * (o.sk === '안력' ? 2 : 1); }
function searchChance(b, o) { return hiddenOfficers(b).length ? Math.min(100, searchSkill(o)) : 0; }
function searchKey(b) { return 's' + b.id + ':' + (b.sT === G.turn ? (b.sN || 0) : 0); }
function searchRoll(b) { return omenRoll(searchKey(b)); }
function searchRollA(b) { return omenRoll('a|' + searchKey(b)); }                // 군사의 조언이 맞는가
function cmdSearch(b, id) {
  if (b.kind !== 'city') return ERR('도시에서만 가능합니다');
  var os = getIdle(b, [id]); if (!os) return ERR('담당 무장을 고르세요');
  if (!needAP(b.owner, AP.search)) return ERR('행동력이 부족합니다');
  useAP(b.owner, AP.search); jot('search', b);
  var o = os[0]; markActed(os, 15);
  var key = searchKey(b), hid = hiddenOfficers(b), p = searchChance(b, o);       // v0.11: 미리 정해 둔 결과(군사가 미리 말해 줄 수 있다)
  b.sN = (b.sT === G.turn ? (b.sN || 0) : 0) + 1; b.sT = G.turn;                 // 같은 턴에 다시 찾으면 주사위가 새로 정해진다
  if (hid.length && omenRoll(key) < p) { var h = hid[Math.min(hid.length - 1, Math.floor(omenRoll('w|' + key) / 100 * hid.length))]; h.st = 'free'; return { ok: true, found: h.id }; }
  if (omenRoll('g|' + key) < 35) { var g = (5 + Math.floor(omenRoll('q|' + key) / 100 * 16)) * 10; b.gold += g; return { ok: true, gold: g }; }
  return { ok: true };
}
/* 다른 세력의 무장 가운데 거점 b 에서 등용을 권할 수 있는 사람: b 와 길로 바로 이어진 이웃 거점에 머무는 무장(군주 제외, 출진·이동 중 제외) */
function isNeighbor(b, id) { var a = ADJ[b.id]; for (var i = 0; i < a.length; i++) if (a[i].to === id) return true; return false; }
function canPoach(b, t) { return !!t && t.st === 'active' && t.unit === null && t.f >= 0 && t.f !== b.owner && !isLord(t) && G.bases[t.loc].owner === t.f && isNeighbor(b, t.loc) && !pactOn(b.owner, t.f); }      // v0.14: 협정을 맺은 세력의 무장에게는 권하지 않는다
function poachTargets(b) {
  var out = [], seen = {};
  if (b.owner < 0) return out;
  ADJ[b.id].forEach(function (e) {
    var nb = G.bases[e.to]; if (seen[nb.id] || nb.owner < 0 || nb.owner === b.owner) return; seen[nb.id] = 1;
    baseOfficers(nb).forEach(function (o) { if (!isLord(o)) out.push(o); });
  });
  return out;
}
/* 무장 o 를 이웃 세력이 데려갈 위험: 이웃 거점에 있는 다른 세력 무장 가운데 가장 잘 권하는 사람과 그 성공률 { p, by, base }. 위험이 없으면 null */
function poachRisk(o) {
  if (!o || o.st !== 'active' || o.unit !== null || o.f < 0 || isLord(o) || bondOf(o)) return null;
  if (facOfficers(o.f).length <= POACH_AI.spare) return null;          // AI 는 무장이 몇 안 되는 세력의 무장에게는 권하지 않는다
  var best = null;
  ADJ[o.loc].forEach(function (e) {
    var nb = G.bases[e.to]; if (nb.owner < 0 || nb.owner === o.f) return;
    baseOfficers(nb).forEach(function (r) { var q = recruitChance(nb, r, o); if (q > 0 && (!best || q > best.p)) best = { p: q, by: r, base: nb }; });
  });
  return best;
}
/* 등용을 권한 뒤 다시 권할 수 있을 때까지 남은 턴(0 이면 권할 수 있다). 재야·포로는 한 턴에 한 번, 다른 세력의 무장은 한 달에 한 번(다음 달 상순부터 다시) */
function askWait(t) { return (t.ask !== undefined && t.ask > G.turn) ? t.ask - G.turn : 0; }
/* ---------- 옛 관계(v0.11) ----------
   o.pf = 마지막으로 섬긴 세력(지금 섬기고 있으면 그 세력, 섬긴 적이 없으면 -1), o.past = 그 앞에 섬겼던 세력들(없으면 필드가 없다).
   세력이 바뀌는 곳이 여럿이라(등용 · 장성 · 멸망 · 이탈 …) 그때마다 적지 않고 pastSweep() 이 훑어서 적는다 — 턴이 넘어갈 때와 등용 직후.
   세력의 군주(G.factions[f].lord)는 바뀌지 않으므로 '누가 누구의 옛 주군인가'는 이것만으로 알 수 있다. */
function homeF(o) { var so = SCENARIO.officers[o.id]; return (so && so.f >= 0) ? so.f : -1; }             // 시나리오가 시작될 때 섬기던 세력
function pastInit(o) {                                                  // 옛 저장(v0.10.1 까지)에는 없다: 시나리오의 세력에서 지금 세력으로 한 번 옮긴 것으로 본다
  var h = homeF(o);
  o.pf = o.f >= 0 ? o.f : h;
  if (h >= 0 && h !== o.pf) o.past = [h];
}
function pastNote(o) {
  if (o.pf === undefined) { pastInit(o); return; }
  if (o.f < 0 || o.f === o.pf) return;                                  // 재야 · 주인 잃은 포로: 마지막 세력을 그대로 둔다
  if (o.pf >= 0) { if (!o.past) o.past = []; var k = o.past.indexOf(o.pf); if (k >= 0) o.past.splice(k, 1); o.past.push(o.pf); }
  o.pf = o.f;
  if (o.past) { var k2 = o.past.indexOf(o.f); if (k2 >= 0) o.past.splice(k2, 1); }      // 예전에 섬기던 세력으로 돌아왔다: 옛 세력 목록에서는 뺀다
}
function pastSweep() { for (var i = 0; i < G.officers.length; i++) pastNote(G.officers[i]); }
function lastF(o) { return o.pf === undefined ? (o.f >= 0 ? o.f : homeF(o)) : o.pf; }
function servedF(o) {                                                   // 섬겼던 세력들 — 지금 섬기는 세력은 뺀다(재야 · 주인 잃은 포로라면 마지막 세력도 든다)
  var pf = lastF(o), out = o.past ? o.past.slice() : [], k;
  if (o.pf === undefined) { var h = homeF(o); if (h >= 0 && out.indexOf(h) < 0) out.push(h); }
  if (pf >= 0 && out.indexOf(pf) < 0) out.push(pf);
  if (o.f >= 0) { k = out.indexOf(o.f); if (k >= 0) out.splice(k, 1); }
  return out;
}
function fallenOf(t) { var lf = lastF(t); return t.f < 0 && lf >= 0 && !!G.factions[lf] && !G.factions[lf].alive && G.factions[lf].lord !== t.id; }   // 멸망한 세력 출신(그 군주 자신은 아니다)
function lordOfAny(o, fs) { for (var i = 0; i < fs.length; i++) if (G.factions[fs[i]] && G.factions[fs[i]].lord === o.id) return true; return false; }
function bondDirect(a, b) { var m = BONDS[a.n], n = BONDS[b.n]; return (m && m[b.n]) || (n && n[a.n]) || null; }
function bondShared(a, b) { for (var L in BONDS) if (BONDS[L][a.n] && BONDS[L][b.n]) return L; return null; }
/* 보내는 무장 o 와 대상 t 의 옛 사이(가장 큰 것 하나) → { k, v, label, short } 또는 null. f = 권하는 세력(o 가 지금 섬기는 세력)
   같은 주군과의 인연(kin)은 그 주군이 권하는 세력의 군주가 아닐 때만 센다 — 그때는 '우리 군주와 인연'으로 이미 세었다 */
function tieOf(o, t, f) {
  if (f === undefined) f = o.f;
  var FL = (f >= 0 && G.factions[f]) ? off(G.factions[f].lord) : null;
  var d = bondDirect(o, t); if (d) return { k: 'bond', v: TIES.bond, label: (FL && FL.id === o.id ? '군주가 직접 설득' : '보내는 무장과 ' + d), short: d };
  var st = servedF(t), so = servedF(o), i;
  if (lordOfAny(o, st)) return { k: 'lord', v: TIES.lord, label: '옛 주군의 설득', short: '옛 주군' };
  var sh = bondShared(o, t); if (sh && !(FL && FL.n === sh)) return { k: 'kin', v: TIES.kin, label: josa(sh, '과와') + ' 맺은 인연', short: '인연' };
  if (lordOfAny(t, so)) return { k: 'vassal', v: TIES.vassal, label: '옛 신하의 설득', short: '옛 신하' };
  for (i = 0; i < so.length; i++) if (st.indexOf(so[i]) >= 0) return { k: 'mate', v: TIES.mate, label: '옛 동료의 설득', short: '옛 동료' };
  return null;
}
/* 세력 f 가 t 의 주군(지금 · 예전)을 참수했는가 → { lord, bond } 또는 null */
function grudgeOf(f, t) {
  var fs = servedF(t); if (t.f >= 0) fs.push(t.f);
  for (var i = 0; i < fs.length; i++) { var F = G.factions[fs[i]], L = F ? off(F.lord) : null; if (L && L.id !== t.id && L.st === 'dead' && L.exBy === f) return { lord: L, bond: (BONDS[L.n] && BONDS[L.n][t.n]) || null }; }
  return null;
}
/* 등용 성공률과 그 까닭 { p, why: [[글, 값]…], tie, no: 응하지 않는 까닭 } — recruitChance 는 p 만 돌려준다 */
function recruitTerms(b, o, t) {
  var L = off(G.factions[b.owner].lord), why = [], tie = tieOf(o, t, b.owner), home = servedF(t).indexOf(b.owner) >= 0, gr = grudgeOf(b.owner, t), mine = bondWith(t, b.owner), k;
  if (t.st === 'active') {                                              // 다른 세력의 무장(v0.9)
    if (bondOf(t)) return { p: 0, why: why, tie: tie, no: '주군과 ' + bondOf(t) };                       //   제 주군과 인연이 있으면 응하지 않는다
    if (t.loy >= POACH.wall && !mine && !(tie && tie.k === 'bond')) return { p: 0, why: why, tie: tie, no: '충성 ' + POACH.wall + ' 이상' };   //   충성이 아주 높아도 응하지 않는다(인연이 있는 사람이 가면 다르다)
    var q = POACH.base + (o.cha - 50) * POACH.cha + (o.pol - 50) * POACH.pol + (L.cha - off(G.factions[t.f].lord).cha) * POACH.lord - (t.loy - POACH.loy0) * POACH.loyK;
    if (o.sk === '논객') { q += POACH.talker; why.push(['논객', POACH.talker]); }
    if (mine) { q += POACH.bond; why.push(['우리 군주와 ' + mine, POACH.bond]); }
    if (tie) { k = Math.round(tie.v * TIES.poach); q += k; why.push([tie.label, k]); }
    if (home) { k = Math.round(TIES.home * TIES.poach); q += k; why.push(['예전에 섬긴 세력', k]); }
    if (gr) { q += TIES.grudge; why.push([gr.lord.n + ' 참수의 원한', TIES.grudge]); }
    q = clamp(Math.round(q), 0, POACH.max);
    if (gr && gr.bond) q = Math.min(q, TIES.grudgeCap);
    return { p: q, why: why, tie: tie };
  }
  var p = 35 + (o.cha - 50) * 0.7 + (o.pol - 50) * 0.2;
  p += (L.cha - 70) * 0.4;
  if (o.sk === '논객') { p += 20; why.push(['논객', 20]); }
  if (mine) { p += 30; why.push(['우리 군주와 ' + mine, 30]); }           // 내 군주와 인연이 있는 사람
  var dead = fallenOf(t);
  if (t.st === 'captive') {
    if (dead) why.push(['멸망한 세력 출신', 15 + TIES.fallen]);            //   돌아갈 곳이 없다: 포로라서 깎이던 15 가 없고, 거기에 더한다
    else { p -= 15; if (t.f >= 0 && G.factions[t.f].alive) p -= (t.loy - 60) * 0.8; }
  } else if (dead) why.push(['멸망한 세력 출신', TIES.fallen]);
  if (dead) p += TIES.fallen;
  if (tie) { p += tie.v; why.push([tie.label, tie.v]); }
  if (home) { p += TIES.home; why.push(['예전에 섬긴 세력', TIES.home]); }
  if (gr) { p += TIES.grudge; why.push([gr.lord.n + ' 참수의 원한', TIES.grudge]); }
  p = clamp(Math.round(p), 3, 95);
  if (t.st === 'captive' && t.f >= 0 && G.factions[t.f].alive && bondOf(t)) p = Math.min(p, 5);   // 주군과 인연이 있는 포로는 주군의 세력이 살아 있는 한 거의 응하지 않는다
  if (gr && gr.bond) p = Math.min(p, TIES.grudgeCap);                    // 인연이 있던 주군을 벤 세력에는 거의 응하지 않는다
  return { p: p, why: why, tie: tie };
}
function recruitChance(b, o, t) { return recruitTerms(b, o, t).p; }
function cmdRecruit(b, id, tid, S) {
  var os = getIdle(b, [id]); if (!os) return ERR('담당 무장을 고르세요');
  var t = off(tid), far = canPoach(b, t);
  if (!t || !(far || (t.loc === b.id && ((t.st === 'free') || (t.st === 'captive' && t.capF === b.owner))))) return ERR('등용할 수 없는 대상입니다');
  if (askWait(t)) return ERR(far ? '이번 달에는 이미 권했습니다 — 다음 달에 다시 권할 수 있습니다' : '이번 턴에는 이미 권했습니다 — 다음 턴에 다시');
  if (S && (S.kind !== 'talk' || !S.over || S.used || S.rb !== b.id || S.ro !== id || S.rt !== tid)) return ERR('설전의 결과가 맞지 않습니다');
  if (!needAP(b.owner, AP.recruit)) return ERR('행동력이 부족합니다');
  useAP(b.owner, AP.recruit);
  var o = os[0]; markActed(os, 15);
  var p = recruitChance(b, o, t), okR = S ? S.win === 'a' : recruitRoll(t) < p;      // 미리 정해 둔 결과(군사가 미리 말해 줄 수 있다). 설전을 벌였으면 그 승패(v0.13)
  if (S) S.used = true;
  t.ask = G.turn + (far ? 3 - G.xun : 1);                               // 다른 세력의 무장: 다음 달 상순부터 다시
  if (okR) {
    var from = far ? t.f : -1, fb = far ? G.bases[t.loc] : null;
    if (t.st === 'captive') { var i = b.captives.indexOf(t.id); if (i >= 0) b.captives.splice(i, 1); }
    if (far) {                                                          // 맡던 공사·군사 자리를 두고 이쪽으로 넘어온다
      t.job = null; t.loc = b.id; if (G.factions[from].adv === t.id) G.factions[from].adv = -1;
      for (var qi = 0; qi < G.officers.length; qi++) { var q = G.officers[qi]; if (q.f === from && q !== t && (q.st === 'active' || q.st === 'travel') && G.factions[from].lord !== q.id && q.loy < 100) q.loy = Math.min(100, q.loy + POACH.tighten); }   // 남은 무장들이 마음을 다잡는다(주군의 단속)
    }
    t.st = 'active'; t.f = b.owner; t.capF = -1; t.unit = null; t.acted = true; t.loy = 70 + ri(0, 15); t.merit = Math.round(t.merit * 0.5); if (bondOf(t)) t.loy = 100;
    pastNote(t);                                                        // 섬겼던 세력을 적어 둔다(v0.11)
    o.merit += far ? 100 : 60;
    if (far) {
      logMsg(facName(b.owner) + '군 ' + josa(o.n, '이가') + ' ' + facName(from) + '군의 ' + josa(t.n, '을를') + ' 등용 (' + fb.n + ' → ' + b.n + ')', b.c, b.r, from === G.player ? G.player : b.owner, from === G.player ? 2 : 1);
      if (from === G.player && !G.aiOnly) ev({ t: 'news', f: b.owner, c: fb.c, r: fb.r, warn: 1, text: '<b>' + fb.n + '의 ' + josa(t.n, '이가') + ' ' + facName(b.owner) + '군의 등용에 응해 떠났습니다</b> — 남은 무장들의 충성 +' + POACH.tighten });
    }
    jot('recruit', b, 1, t.id);
    return { ok: true, joined: true, p: p, far: far, from: from };
  }
  if (far) {                                                            // 거절: 마음을 다잡는다
    var l0 = t.loy; t.loy = Math.min(100, t.loy + POACH.up);
    if (t.f === G.player && !G.aiOnly) logMsg(facName(b.owner) + '군 ' + josa(o.n, '이가') + ' 우리 ' + t.n + '에게 등용을 권했으나 거절 (충성 ' + l0 + ' → ' + t.loy + ')', G.bases[t.loc].c, G.bases[t.loc].r, G.player, 1);
  }
  jot('recruit', b, 0, t.id);
  return { ok: true, joined: false, p: p, far: far };
}
function cmdReward(b, tid) {
  var t = off(tid);
  if (!t || t.f !== b.owner || t.st !== 'active' || t.loc !== b.id) return ERR('대상이 없습니다');
  if (b.gold < COST.reward) return ERR('금이 부족합니다 (' + COST.reward + ' 필요)');
  if (!needAP(b.owner, AP.reward)) return ERR('행동력이 부족합니다');
  if (t.loy >= 100) return ERR('이미 충성도가 최고입니다');
  b.gold -= COST.reward; useAP(b.owner, AP.reward); jot('reward', b, 1, t.id);
  var before = t.loy; t.loy = Math.min(100, t.loy + ri(8, 12));
  return { ok: true, n: t.loy - before };
}
function travelTurns(a, b) { return Math.max(1, Math.round(hdist(a.c, a.r, b.c, b.r) / 10)); }
function cmdMoveOfficers(b, ids, destId) {
  var d = G.bases[destId];
  if (!d || d.owner !== b.owner || d.id === b.id) return ERR('갈 수 없는 곳입니다');
  var os = getIdle(b, ids); if (!os || !os.length) return ERR('무장을 고르세요');
  if (!needAP(b.owner, AP.move)) return ERR('행동력이 부족합니다');
  useAP(b.owner, AP.move); jot('move', b, os.length, destId);
  var t = travelTurns(b, d);
  for (var i = 0; i < os.length; i++) { os[i].st = 'travel'; os[i].dest = d.id; os[i].eta = t; os[i].acted = true; }
  return { ok: true, turns: t };
}
function cmdCaptive(b, tid, action) {
  var t = off(tid);
  if (!t || t.st !== 'captive' || t.loc !== b.id || t.capF !== b.owner) return ERR('대상이 없습니다');
  if (action === 'release') { releaseCaptive(t); return { ok: true }; }
  if (action === 'execute') { var i = b.captives.indexOf(t.id); if (i >= 0) b.captives.splice(i, 1); t.st = 'dead'; t.f = -1; t.capF = -1; t.exBy = b.owner; return { ok: true }; }      // exBy: 누가 베었는가(v0.11 — 그 신하였던 무장들이 원한을 품는다)
  return ERR('?');
}

/* ---------- 출진 ---------- */
function deploySpot(b, toward) {
  var ns = nbrs(b.c, b.r), best = null, bs = 1e9;
  for (var i = 0; i < ns.length; i++) {
    var c = ns[i][0], r = ns[i][1], k = K(c, r), t = terr(c, r);
    if (t === 'm' || t === 's' || t === 'x') continue;
    if (UAT[k] || BAT[k] !== undefined) continue;
    var pf = PAT[k], onFac = pf && G.bases[pf.b].plots[pf.i].fac ? 1 : 0;                      // v0.12: 시설 칸으로도 나갈 수 있다(빈 땅이 먼저)
    var s = (t === 'w' ? 10 : 0) + (isRoad(c, r) ? 0 : 2) + (G.fires[k] ? 20 : 0) + onFac * 4;
    if (toward) s = hdist(c, r, toward.c, toward.r) + (t === 'w' ? 3 : 0) + (G.fires[k] ? 20 : 0) + onFac * 0.5;
    if (s < bs) { bs = s; best = [c, r]; }
  }
  return best;
}
/* 성 밖으로 나갈 수 있는 칸들(둘레 여섯 칸 가운데 산 · 바다 · 부대가 선 칸을 뺀 것). v0.12: 출진할 때 이 가운데서 고를 수 있다 */
function deploySpots(b) {
  var ns = nbrs(b.c, b.r), out = [];
  for (var i = 0; i < ns.length; i++) {
    var c = ns[i][0], r = ns[i][1], k = K(c, r), t = terr(c, r);
    if (t === 'm' || t === 's' || t === 'x' || UAT[k] || BAT[k] !== undefined) continue;
    out.push([c, r]);
  }
  return out;
}
/* spec: { type, ids, troops, food, gold, cargo, toward, at }   at = [c, r] 나갈 칸을 직접 고른 것(v0.12) */
function cmdDeploy(b, spec) {
  var T = UNIT_TYPES[spec.type];
  if (!T) return ERR('병과를 고르세요');
  var os = getIdle(b, spec.ids); if (!os || !os.length || os.length > 3) return ERR('무장을 고르세요 (1~3명)');
  var troops = Math.floor(spec.troops);
  if (troops < 100) return ERR('병력은 100명 이상이어야 합니다');
  if (troops > b.troops) return ERR('도시 병력이 부족합니다');
  if (spec.type !== 'trans' && troops > cmdCap(os[0])) return ERR('주장의 지휘 한도(' + cmdCap(os[0]) + ')를 넘습니다');
  if (T.weapon === 'ram') { if (b.w.ram < 1) return ERR('충차가 없습니다'); }
  else if (T.weapon && b.w[T.weapon] < troops) return ERR(josa(WEAPON_NAMES[T.weapon], '이가') + ' 부족합니다 (' + b.w[T.weapon] + ')');
  var food = Math.floor(spec.food || 0), gold = Math.floor(spec.gold || 0);
  if (food > b.food) return ERR('병량이 부족합니다');
  if (gold > b.gold) return ERR('금이 부족합니다');
  var cargo = null, k;
  if (spec.cargo) { cargo = { spear: 0, halberd: 0, bow: 0, horse: 0, ram: 0 }; for (k in cargo) { cargo[k] = Math.floor(spec.cargo[k] || 0); if (cargo[k] > b.w[k]) return ERR(WEAPON_NAMES[k] + ' 재고가 부족합니다'); } }
  if (!needAP(b.owner, AP.deploy)) return ERR('행동력이 부족합니다');
  var spot = null;
  if (spec.at) {
    var sps = deploySpots(b);
    for (var si = 0; si < sps.length; si++) if (sps[si][0] === spec.at[0] && sps[si][1] === spec.at[1]) spot = sps[si];
    if (!spot) return ERR('그 칸으로는 나갈 수 없습니다');
  } else spot = deploySpot(b, spec.toward);
  if (!spot) return ERR('성 밖에 나갈 자리가 없습니다');
  useAP(b.owner, AP.deploy);
  b.troops -= troops; b.food -= food; b.gold -= gold;
  if (T.weapon === 'ram') b.w.ram -= 1; else if (T.weapon) b.w[T.weapon] -= troops;
  if (cargo) for (k in cargo) b.w[k] -= cargo[k];
  var u = { id: G.nextUnit++, f: b.owner, c: spot[0], r: spot[1], type: spec.type, off: os.map(function (o) { return o.id; }), troops: troops, max: troops,
    morale: b.morale, food: food, gold: gold, cargo: cargo, status: null, stT: 0, done: false, moved: false, mp: 0, home: b.id, ox: -1, oy: -1, omp: 0, born: G.turn, ai: null, dest: -1 };
  for (var i = 0; i < os.length; i++) { os[i].unit = u.id; os[i].acted = true; }
  u.mp = uMaxMp(u);
  if (spec.dest !== undefined && spec.dest >= 0) u.dest = spec.dest;
  addUnit(u); jot('deploy', b, troops, spec.type);
  ev({ t: 'deploy', id: u.id, f: u.f, n: uName(u), base: b.id, c: u.c, r: u.r });
  return { ok: true, unit: u };
}

/* ---------- 부대 이동 ---------- */
function unitMove(u, c, r, rc) {
  if (u.done) return ERR('이미 행동을 마쳤습니다');
  rc = rc || unitReach(u);
  var k = K(c, r);
  if (!rc.stop[k]) return ERR('갈 수 없는 곳입니다');
  var path = pathFromReach(rc, u, c, r);
  if (!path) return ERR('경로가 없습니다');
  var from = [u.c, u.r];
  u.ox = u.c; u.oy = u.r; u.omp = u.mp;
  var b = baseAt(c, r);
  if (b) {
    u.mp = 0; u.moved = true;
    ev({ t: 'move', id: u.id, f: u.f, n: uName(u), from: from, path: path, c: c, r: r, into: b.id });
    if (b.owner === u.f) { enterBase(u, b); return { ok: true, path: path, from: from, entered: b.id }; }
    if (b.owner === -1) { placeUnit(u, c, r); captureBase(b, u); return { ok: true, path: path, from: from, captured: b.id }; }
    return ERR('적의 거점입니다');
  }
  placeUnit(u, c, r);
  u.mp = Math.max(0, u.mp - rc.cost[k]);
  u.moved = true;
  var res = { ok: true, path: path, from: from };
  ev({ t: 'move', id: u.id, f: u.f, n: uName(u), from: from, path: path, c: c, r: r });
  if (G.fires[k] && !uHas(u, '화신')) { var fd = ri(150, 250); res.burn = fd; u.ox = -1; if (hurtUnit(u, fd, -1)) res.dead = true; }
  return res;
}
function unitUndoMove(u) {
  if (u.done || u.ox < 0 || !UMAP[u.id]) return false;
  if (UAT[K(u.ox, u.oy)]) return false;
  placeUnit(u, u.ox, u.oy); u.mp = u.omp; u.moved = false; u.ox = -1;
  return true;
}
function unitWait(u) { u.done = true; u.ox = -1; return { ok: true }; }
/* ---------- 보급(v0.11): 수송대가 옆 칸의 아군 부대에 병량과 병력을 넘긴다 ----------
   병력은 받는 주장의 지휘 한도까지, 수송대에는 100명을 남긴다. 창·극·노·기병에게는 수송대에 실은 그 무기만큼만(무기도 함께 넘어간다).
   보급한 수송대는 그 턴의 행동을 마친다. 받는 부대의 행동은 쓰지 않는다. */
function supplyTargets(t) {                                  // 수송대 t 가 보급할 수 있는 부대
  var out = []; if (!t || t.type !== 'trans') return out;
  nbrs(t.c, t.r).forEach(function (n) { var u = UAT[K(n[0], n[1])]; if (u && u.f === t.f && u.type !== 'trans') out.push(u); });
  return out;
}
function supplySources(u) {                                  // 부대 u 옆에서 보급해 줄 수 있는 수송대(아직 행동하지 않은)
  var out = []; if (!u || u.type === 'trans') return out;
  nbrs(u.c, u.r).forEach(function (n) { var t = UAT[K(n[0], n[1])]; if (t && t.f === u.f && t.type === 'trans' && !t.done && !t.status) out.push(t); });
  return out;
}
function supplyMax(t, u) {                                   // 넘길 수 있는 한도 { food, troops, why: 병력이 그만큼인 까닭 }
  var wp = UNIT_TYPES[u.type].weapon, room = Math.max(0, cmdCap(uLeader(u)) - u.troops), spare = Math.max(0, t.troops - 100), m = Math.min(room, spare);
  var why = room <= spare ? '지휘 한도 ' + nf(cmdCap(uLeader(u))) : '수송대에 100명은 남깁니다';
  if (wp && wp !== 'ram') { var have = (t.cargo && t.cargo[wp]) || 0; if (have < m) { m = have; why = '실은 ' + WEAPON_NAMES[wp] + ' ' + nf(have); } }
  return { food: Math.max(0, Math.floor(t.food)), troops: Math.floor(m / 100) * 100, why: why };
}
function cmdSupply(t, u, give) {
  if (!t || !u || t.type !== 'trans' || u.type === 'trans' || t.f !== u.f) return ERR('보급할 수 없는 대상입니다');
  if (t.done) return ERR('수송대가 이미 행동을 마쳤습니다');
  if (t.status) return ERR('수송대가 명령을 들을 수 없습니다');
  if (hdist(t.c, t.r, u.c, u.r) !== 1) return ERR('옆 칸의 부대에만 보급할 수 있습니다');
  var food = Math.max(0, Math.floor(give.food || 0)), troops = Math.max(0, Math.floor((give.troops || 0) / 100) * 100), mx = supplyMax(t, u);
  if (food > mx.food) return ERR('수송대의 병량이 모자랍니다');
  if (troops > mx.troops) return ERR('병력은 ' + nf(mx.troops) + '명까지 넘길 수 있습니다 (' + mx.why + ')');
  if (!food && !troops) return ERR('넘길 것을 정하세요');
  t.food -= food; u.food += food;
  if (troops) {
    var wp = UNIT_TYPES[u.type].weapon;
    if (wp && wp !== 'ram') t.cargo[wp] -= troops;                       // 무기도 함께 넘어간다
    u.morale = Math.round((u.troops * u.morale + troops * t.morale) / (u.troops + troops));
    u.troops += troops; t.troops -= troops; if (!(u.max >= u.troops)) u.max = u.troops;
  }
  t.done = true; t.ox = -1;
  return { ok: true, food: food, troops: troops };
}

function autoRetreat(u) {
  var nb = nearestOwnBase(u.f, u.c, u.r);
  if (!nb) return;
  var gk = K(nb.c, nb.r);
  var path = longPath(u, function (k) { return k === gk; }, 0, [nb.c, nb.r, 0]);
  if (!path) return;
  var rc = unitReach(u), best = -1;
  for (var i = 0; i < path.length; i++) if (rc.stop[path[i]]) best = path[i];
  if (best >= 0) { var c = best % W, r = (best - c) / W; unitMove(u, c, r, rc); }
}

/* ---------- 행군(목적지 지정 이동) ---------- */
function marchPath(u, gk) { var gc = gk % W; return longPath(u, function (k) { return k === gk; }, 3000, [gc, (gk - gc) / W, 0]); }
function marchTurns(u, path) {
  var full = uMaxMp(u), left = u.done ? 0 : u.mp, turns = 1;
  for (var i = 0; i < path.length; i++) {
    var c = path[i] % W, mc = moveCost(u, c, (path[i] - c) / W);
    if (mc > left) { turns++; left = full; }
    left -= mc;
  }
  return turns;
}
function unitMarch(u) {
  if (u.done || u.dest === undefined || u.dest === null || u.dest < 0) return null;
  if (K(u.c, u.r) === u.dest) { u.dest = -1; return null; }
  var path = marchPath(u, u.dest);
  if (!path) { u.dest = -1; return { ok: false, lost: true }; }
  var rc = unitReach(u), best = -1;
  for (var i = 0; i < path.length; i++) if (rc.stop[path[i]] && (!G.fires[path[i]] || BAT[path[i]] !== undefined)) best = path[i];
  if (best < 0) {
    // 목적지가 바로 옆의 적 거점이면 도착한 것으로 본다(들어갈 수는 없으니 공격은 직접 명령)
    var dc0 = u.dest % W, dr0 = (u.dest - dc0) / W, db0 = baseAt(dc0, dr0);
    if (db0 && db0.owner >= 0 && db0.owner !== u.f && hdist(u.c, u.r, dc0, dr0) <= 1) { u.dest = -1; return { ok: false, front: db0.id }; }
    return null;
  }
  var c = best % W, r = (best - c) / W, dk = u.dest, res = unitMove(u, c, r, rc);
  if (res.ok && (best === dk || res.entered !== undefined || res.captured !== undefined || res.dead)) u.dest = -1;
  else if (res.ok && UMAP[u.id]) {                         // 적 거점 바로 앞에 닿았으면 행군은 여기까지
    var dc1 = dk % W, dr1 = (dk - dc1) / W, db1 = baseAt(dc1, dr1);
    if (db1 && db1.owner >= 0 && db1.owner !== u.f && hdist(u.c, u.r, dc1, dr1) <= 1) { u.dest = -1; res.front = db1.id; }
  }
  return res;
}

/* 출진 전에 목적지까지 걸릴 턴 수를 재 본다: 실제로 나가게 될 성 밖 칸에서 출발하는 임시 부대로 잰다.
   돌려주는 값은 '출진한 턴을 포함해 몇 턴째에 닿는가'. 길이 없으면 0 */
function deployEta(b, type, ids, destKey) {
  if (!ids.length) return 0;
  var dc = destKey % W, dr = (destKey - dc) / W, spot = deploySpot(b, { c: dc, r: dr });
  if (!spot) return 0;
  if (K(spot[0], spot[1]) === destKey) return 1;
  var tmp = { id: -1, f: b.owner, c: spot[0], r: spot[1], type: type, off: ids, troops: 1000, done: false, mp: 0 };
  tmp.mp = uMaxMp(tmp);
  var path = marchPath(tmp, destKey);
  return path ? marchTurns(tmp, path) : 0;
}

/* ---------- 자동 추천: 그 일을 가장 잘하는 무장 ---------- */
function statSum(o) { return o.ldr + o.war + o.int + o.pol + o.cha; }
function autoValue(kind, b, os, ctx) {
  var v = 0, i, t = 0;
  for (i = 0; i < os.length; i++) t += statSum(os[i]);
  if (kind === 'develop') { v = 60 + Math.round((bestOf(os, 'pol') + sumOthers(os, 'pol') * 0.5) * 0.6); if (anyHas(os, '축성')) v *= 2; }
  else if (kind === 'draft') v = draftAmount(b, os) + (anyHas(os, '인덕') ? 150 : 0);
  else if (kind === 'patrol') { v = Math.round(5 + Math.max(bestOf(os, 'war'), bestOf(os, 'ldr')) / 9 + (os.length - 1) * 2); if (anyHas(os, '위압')) v *= 2; v *= 10; }
  else if (kind === 'train') v = Math.round(8 + bestOf(os, 'ldr') / 8 + (os.length - 1) * 2) * 10;
  else if (kind === 'produce') { if (ctx && ctx.kind === 'ram') v = anyHas(os, '발명') ? 1000 : (os.length > 1 ? -1 : 0); else v = produceAmount(b, ctx.kind, os); }
  else if (kind === 'search') v = (25 + os[0].pol * 0.35 + os[0].cha * 0.15) * (os[0].sk === '안력' ? 2 : 1) * 10;
  else if (kind === 'recruit') v = recruitChance(b, os[0], ctx.target) * 10;
  else if (kind === 'merge') v = 0;
  return v - t * 0.001;                       // 같은 효과면 능력이 낮은 무장을 쓴다
}
function autoPick(kind, b, ctx, max, cands) {
  cands = cands || idleOfficers(b); max = max || 1;
  var chosen = [], cur = -1e9;
  while (chosen.length < max) {
    var bi = -1, bv = cur + (chosen.length ? 0.5 : 0);   // 덧붙여도 이득이 없으면 더 넣지 않는다
    for (var i = 0; i < cands.length; i++) {
      if (chosen.indexOf(cands[i]) >= 0) continue;
      var v = autoValue(kind, b, chosen.concat([cands[i]]), ctx);
      if (v > bv) { bv = v; bi = i; }
    }
    if (bi < 0) break;
    chosen.push(cands[bi]); cur = bv;
  }
  return chosen.map(function (o) { return o.id; });
}
/* 출진 편성 추천: 병과에 맞는 주장 + 도움이 되는 부장 */
function teamScore(type, os, want) {
  var L = os[0], idx = APT_IDX[type], apt = 'B', i;
  if (type === 'trans') return 300 - (L.war * 0.55 + L.ldr * 0.45) - (isLord(L) ? 100 : 0);
  if (idx !== undefined) { apt = 'C'; for (i = 0; i < os.length; i++) { var a = os[i].apt.charAt(idx); if (APT_RANK[a] > APT_RANK[apt]) apt = a; } }
  var atk = L.war * 0.7 + bestOf(os, 'war') * 0.3, def = L.ldr * 0.7 + bestOf(os, 'ldr') * 0.3;
  var v = (atk + def) * APT_MUL[apt] * (0.55 + 0.45 * Math.min(1, cmdCap(L) / Math.max(1000, want)));
  v += bestOf(os, 'int') * 0.12;
  for (i = 0; i < os.length; i++) if (os[i].sk && AUTO_WAR_SKILLS.indexOf(os[i].sk) >= 0) v += 6;
  if (isLord(L)) v *= 0.93;
  return v;
}
var AUTO_WAR_SKILLS = ['비장', '신장', '투신', '용장', '창장', '극장', '궁장', '기장', '기신', '궁신', '위풍', '연전', '금강', '철벽', '불굴', '급습', '공심', '강행', '답파', '포박', '공성', '신산', '허실', '귀모', '통찰', '명경', '간파', '반계', '연환', '심모', '화신', '화공', '둔전'];
function autoTeam(b, type, want) {
  var cands = idleOfficers(b), best = null, bv = -1e9, i;
  for (i = 0; i < cands.length; i++) { var v = teamScore(type, [cands[i]], want); if (v > bv) { bv = v; best = cands[i]; } }
  if (!best) return [];
  var team = [best];
  if (type === 'trans') return [best.id];
  while (team.length < 3) {
    var bi = null, gain = bv * 1.012;                 // 1.2% 넘게 좋아질 때만 부장을 붙인다
    for (i = 0; i < cands.length; i++) {
      if (team.indexOf(cands[i]) >= 0 || isLord(cands[i])) continue;
      var v2 = teamScore(type, team.concat([cands[i]]), want) - statSum(cands[i]) * 0.002;
      if (v2 > gain) { gain = v2; bi = cands[i]; }
    }
    if (!bi) break;
    team.push(bi); bv = teamScore(type, team, want);
  }
  return team.map(function (o) { return o.id; });
}

/* ---------- 전투 ---------- */
/* 주사위를 뺀 피해(v0.9.1) — dmgUU 가 여기에 0.92~1.08 을 곱한다. 창의 '예상'과 전법의 기대값(tacticExpect)이 이 값을 쓴다 */
/* ---------- 지형이 싸움에 미치는 것(v0.15) ----------
   치는 부대 a 가 맞는 부대 d 에게 주는 피해에 곱해지는 값들. ranged = 두 칸 밖에서 쏘는가. 화면도 이것으로 내역을 적는다 */
function elevOf(c, r) { return ELV[r * W + c]; }
function elevDiff(a, d) { return clamp(ELV[a.r * W + a.c] - ELV[d.r * W + d.c], -ELEV_K.max, ELEV_K.max); }
function terrMods(a, d, ranged) {
  var out = [], td = terr(d.c, d.r), ta = terr(a.c, a.r), T = TERR_K;
  if (td === 'f' || td === 'h') out.push({ k: TERRAIN_NAME[td] + '의 적', m: T.cover });
  else if (td === 'w') out.push({ k: '강 위의 적', m: T.riverDef });
  if (ranged && td === 'f') out.push({ k: '숲 속으로 쏨', m: T.forestShot });
  if (ta === 'w') out.push({ k: '강 위에서', m: T.riverAtk });
  if (UNIT_TYPES[a.type].cls === 'horse' && !ranged) {
    if (ta === 'f' || ta === 'h' || td === 'f' || td === 'h') out.push({ k: '기병 · 험한 땅', m: T.cavRough });
    else if (ta === 'p' && td === 'p') out.push({ k: '기병 · 평지', m: T.cavPlain });
  }
  var dh = elevDiff(a, d);
  if (dh) out.push({ k: dh > 0 ? '높은 곳에서' : '낮은 곳에서', m: 1 + ELEV_K.step * dh, dh: dh });
  return out;
}
function terrMul(a, d, ranged) { var ms = terrMods(a, d, ranged), x = 1; for (var i = 0; i < ms.length; i++) x *= ms[i].m; return x; }
/* 옛 저장: 못 가는 칸(넓어진 산)에 서 있는 부대를 가장 가까운 갈 수 있는 빈 칸으로 옮긴다 → 옮긴 부대들 */
function terrainFix() {
  var moved = [];
  for (var i = 0; i < G.units.length; i++) {
    var u = G.units[i], k0 = u.r * W + u.c;
    if (MC[0][k0] < 99) continue;
    var seen = {}, q = [[u.c, u.r]], hit = null, n = 0; seen[k0] = 1;
    while (q.length && !hit && n < 4000) {
      var p = q.shift(), ns = nbrs(p[0], p[1]); n++;
      for (var j = 0; j < ns.length && !hit; j++) { var nk = ns[j][1] * W + ns[j][0]; if (seen[nk]) continue; seen[nk] = 1; if (MC[0][nk] < 99 && !UAT[nk] && BAT[nk] === undefined) hit = ns[j]; else q.push(ns[j]); }
    }
    if (hit) { placeUnit(u, hit[0], hit[1]); moved.push(u); }
  }
  return moved;
}

function dmgBase(a, d, mult, ranged) {
  var x = 620 * Math.pow(uAtk(a) / Math.max(10, uDef(d)), 0.9) * troopFactor(a.troops) * mult;
  var c = (COMPAT[a.type] && COMPAT[a.type][d.type]) || 1;
  if (VS_TYPE[d.type] && (!ranged || d.type === 'trans' || d.type === 'ram')) c *= VS_TYPE[d.type];
  x *= c;
  x *= terrMul(a, d, ranged);                                  // v0.15: 지형 · 높낮이 · 병과
  if (d.status === 'confuse') x *= 1.25;
  return x;
}
function dmgUU(a, d, mult, ranged) {
  var x = dmgBase(a, d, mult, ranged);
  x *= 0.92 + rnd() * 0.16;
  return Math.max(30, Math.round(x));
}
function baseDefVal(b) {
  var os = baseOfficers(b), l = Math.max(50, bestOf(os, 'ldr'));
  return l * (b.kind === 'gate' ? 1.6 : 1.3) * (0.7 + 0.3 * b.dur / b.maxDur);
}
function dmgUB(a, b) {
  var T = UNIT_TYPES[a.type];
  var x = 620 * Math.pow(uAtk(a) / baseDefVal(b), 0.9) * troopFactor(a.troops) * T.vsBase * (0.92 + rnd() * 0.16);
  if (terr(a.c, a.r) === 'w') x *= TERR_K.riverAtk;
  return Math.max(20, Math.round(x));
}
function durDmgUB(a) {
  var T = UNIT_TYPES[a.type];
  var x = (uAtk(a) * 1.2 + 40) * troopFactor(a.troops) * T.siege;
  if (uHas(a, '공성')) x *= 1.5;
  return Math.round(x);
}
function dmgBU(b, u) {
  var os = baseOfficers(b), w = Math.max(50, bestOf(os, 'war'));
  var x = 620 * Math.pow(w / Math.max(10, uDef(u)), 0.9) * troopFactor(b.troops) * 0.5 * (0.92 + rnd() * 0.16);
  if (uHas(u, '금강')) x *= 0.65;
  return Math.max(20, Math.round(x));
}
function defMods(d, dmg, kind) {
  if (kind === 'normal' && uHas(d, '금강')) dmg *= 0.65;
  if (kind === 'tactic' && uHas(d, '철벽')) dmg *= 0.7;
  if (uHas(d, '불굴') && d.troops <= d.max * 0.3) dmg *= 0.5;
  return Math.round(dmg);
}
function afterHit(a, d, dealt) {
  addMerit(a, Math.round(dealt / 25));
  if (uHas(a, '공심') && UMAP[a.id]) a.troops = Math.min(a.max, a.troops + Math.round(dealt * 0.1));
  if (uHas(a, '위풍') && UMAP[d.id]) d.morale = Math.max(0, d.morale - 10);
}
function alive(u) { return !!UMAP[u.id]; }
function setStatus(u, st, turns) { if (!alive(u)) return; u.status = st; u.stT = turns; u.stSkip = -1; }
/* 상태 이상(혼란·위보)으로 잃는 차례 수 — 지금부터 셈. 지금 건너뛰고 있는 차례가 있으면 그것까지 넣는다. 0 이면 '다음 차례에 풀린다'(그때까지는 아직 걸려 있다) */
function statusLeft(u) { return u.status ? (u.stT || 0) + (u.stSkip === G.turn ? 1 : 0) : 0; }
function statusName(st) { return st === 'confuse' ? '혼란' : (st === 'rumor' ? '위보' : ''); }
function unitOnFire(u) { return !!G.fires[K(u.c, u.r)]; }
function setFire(c, r, turns) {
  var t = terr(c, r);
  if (t === 'w' || t === 's' || t === 'm' || t === 'x') return false;
  if (BAT[K(c, r)] !== undefined) return false;
  G.fires[K(c, r)] = Math.max(G.fires[K(c, r)] || 0, turns);
  return true;
}

/* 일기토: 근접전에서 낮은 확률로 벌어지는 자동 판정 */
/* ====================== 대결(v0.13): 일기토 · 설전 ======================
   판 S = { kind, a, d(두 사람: id · n · st 능력 · rd 읽는 능력 · hp · max · mom 기세 · last 지난 수), round, max, over, win('a' | 'd' | 'draw'), ko, log[합의 기록], plan, hint }
   규칙은 여기서 끝난다 — 화면(src/duel.js)은 수를 고르게 하고 결과를 그려 보일 뿐이다. 숫자는 data.js 의 DUEL_K · DUEL_KIND */
var DUEL_DEFER = false;                                            // 켜져 있으면 싸움터의 일기토를 여기서 끝내지 않고 판만 만들어 돌려준다(res.duelS) — 사람이 수를 고른다
function duelSide(o, K, hp) { return { id: o.id, n: o.n, st: Math.max(1, o[K.stat]), rd: o[K.read], hp: hp, max: hp, mom: 0, last: null }; }
function duelNew(kind, A, D, opt) {
  var K = DUEL_KIND[kind], o = opt || {};
  return { kind: kind, a: duelSide(A, K, o.hpA || DUEL_K.hp), d: duelSide(D, K, o.hpD || DUEL_K.hp), round: 0, max: o.rounds || DUEL_K.rounds, over: false, win: null, ko: false, log: [], plan: null, hint: null };
}
function duelOther(side) { return side === 'a' ? 'd' : 'a'; }
/* AI 가 수를 고를 때의 무게. 일기토는 성미(무력이 지력보다 높을수록 거칠다)와 형세, 설전은 고르게 — 둘 다 상대가 지난 합에 낸 수를 이기는 수에 조금 더 건다 */
function duelWeights(S, side) {
  var K = DUEL_KIND[S.kind], me = S[side], op = S[duelOther(side)], o = off(me.id), w = {}, i, ids = K.order;
  if (S.kind === 'duel') {
    var bold = clamp((o.war - o.int) / 40, -1, 1);
    w.atk = 40 + 10 * bold; w.sp = 30 + 10 * bold; w.def = 30 - 20 * bold;
    if (me.hp < me.max * 0.35) w.sp += 20;                           // 몰리면 크게 건다
    if (me.mom >= 2) w.atk += 10;                                   // 기세를 탔으면 몰아친다
  } else for (i = 0; i < ids.length; i++) w[ids[i]] = 34;
  for (i = 0; i < ids.length; i++) {
    if (op.last && K.moves[ids[i]].beats === op.last) w[ids[i]] += 15;
    if (me.last === ids[i]) w[ids[i]] -= 8;                          // 같은 수를 거듭 내지는 않으려 한다
    if (w[ids[i]] < 5) w[ids[i]] = 5;
  }
  return w;
}
function duelPick(S, side) {
  var w = duelWeights(S, side), ids = DUEL_KIND[S.kind].order, tot = 0, i;
  for (i = 0; i < ids.length; i++) tot += w[ids[i]];
  var x = rnd() * tot;
  for (i = 0; i < ids.length; i++) { x -= w[ids[i]]; if (x < 0) return ids[i]; }
  return ids[ids.length - 1];
}
/* side 가 상대의 기색을 맞게 읽을 확률(%) */
function duelRead(S, side) { var me = S[side], op = S[duelOther(side)]; return Math.round(clamp(DUEL_K.readBase + (me.rd - op.rd) * DUEL_K.readK, DUEL_K.readLo, DUEL_K.readHi)); }
/* 다음 합을 준비한다: 사람이 두지 않는 쪽의 수를 미리 정하고(S.plan), 사람(human = 'a' | 'd' | null)에게 보일 기색(S.hint = { move, p })을 만든다 */
function duelPlan(S, human) {
  if (S.over) return null;
  S.plan = { a: human === 'a' ? null : duelPick(S, 'a'), d: human === 'd' ? null : duelPick(S, 'd') };
  S.hint = null;
  if (human) {
    var real = S.plan[duelOther(human)], p = duelRead(S, human), show = real;
    if (!(rnd() * 100 < p)) { var others = DUEL_KIND[S.kind].order.filter(function (m) { return m !== real; }); show = others[Math.floor(rnd() * others.length)]; }
    S.hint = { move: show, p: p };
  }
  return S.plan;
}
function duelDmg(from, to, mult) { return Math.max(1, Math.round(DUEL_K.base * Math.pow(from.st / to.st, DUEL_K.pow) * mult * (1 + DUEL_K.mom * from.mom) * (0.88 + rnd() * 0.24))); }
/* 한 합을 치른다. ma · md = 두 사람의 수. 돌려주는 값 = 그 합의 기록 { n, ma, md, win('a' | 'd' | null), how, toA, toD(받은 피해), heal, hpA, hpD } */
function duelStep(S, ma, md) {
  if (S.over) return null;
  var K = DUEL_KIND[S.kind], A = S.a, D = S.d, MA = K.moves[ma], MD = K.moves[md];
  if (!MA || !MD) return null;
  var R = { n: S.round + 1, ma: ma, md: md, win: null, how: '', toA: 0, toD: 0, heal: 0 };
  if (ma === md) {
    var T = MA.tie; R.how = T[0];
    if (T[0] === 'both') { R.toD = duelDmg(A, D, T[1]); R.toA = duelDmg(D, A, T[1]); }
    else if (T[0] === 'rest') { R.heal = T[1]; A.hp = Math.min(A.max, A.hp + T[1]); D.hp = Math.min(D.max, D.hp + T[1]); }
    else { var pa = Math.pow(A.st, 3) / (Math.pow(A.st, 3) + Math.pow(D.st, 3)); if (rnd() < pa) { R.win = 'a'; R.toD = duelDmg(A, D, T[1]); } else { R.win = 'd'; R.toA = duelDmg(D, A, T[1]); } }
  } else if (MA.beats === md) { R.win = 'a'; R.how = 'beat'; R.toD = duelDmg(A, D, MA.mult * (MD.lose || 1)); }
  else { R.win = 'd'; R.how = 'beat'; R.toA = duelDmg(D, A, MD.mult * (MA.lose || 1)); }
  A.hp -= R.toA; D.hp -= R.toD;
  if (R.win === 'a') { A.mom = Math.min(DUEL_K.momMax, A.mom + 1); D.mom = 0; } else if (R.win === 'd') { D.mom = Math.min(DUEL_K.momMax, D.mom + 1); A.mom = 0; }
  A.last = ma; D.last = md; S.round++; S.plan = null; S.hint = null;
  if (A.hp <= 0 || D.hp <= 0) {                                      // 쓰러졌다. 둘 다 쓰러지면 덜 깎인 쪽이 이긴다
    S.over = true; S.ko = true;
    S.win = A.hp <= 0 && D.hp <= 0 ? (A.hp === D.hp ? 'draw' : (A.hp > D.hp ? 'a' : 'd')) : (A.hp <= 0 ? 'd' : 'a');
    if (S.win === 'draw') S.ko = false;
    if (A.hp < 0) A.hp = 0; if (D.hp < 0) D.hp = 0;
  } else if (S.round >= S.max) {                                     // 판정: 남은 힘의 비율
    var ra = A.hp / A.max * 100, rd = D.hp / D.max * 100;
    S.over = true; S.win = Math.abs(ra - rd) < DUEL_K.drawGap ? 'draw' : (ra > rd ? 'a' : 'd');
  }
  R.hpA = A.hp; R.hpD = D.hp; S.log.push(R);
  return R;
}
function duelAuto(S) { var n = 0; while (!S.over && n++ < 99) { var p = duelPlan(S, null); duelStep(S, p.a, p.d); } return S; }

/* ---------- 싸움터의 일기토 ---------- */
function duelBattleOk(a, d) { return alive(a) && alive(d) && hdist(a.c, a.r, d.c, d.r) === 1 && a.f !== d.f; }
function tryDuel(a, d, res) {
  if (!duelBattleOk(a, d)) return;
  var la = uLeader(a), ld = uLeader(d);
  if (la.war < DUEL_K.minWar || ld.war < DUEL_K.minWar || !chance(DUEL_K.rate)) return;
  duelBattle(a, d, res);
}
/* 두 부대의 주장이 일기토를 벌인다. DUEL_DEFER 가 켜져 있으면 판만 만들어 res.duelS 로 돌려준다(끝나면 화면이 duelFinish 를 부른다) */
function duelBattle(a, d, res) {
  var S = duelNew('duel', uLeader(a), uLeader(d));
  S.ua = a.id; S.ud = d.id;
  if (DUEL_DEFER) { res.duelS = S; return S; }
  duelAuto(S); duelFinish(S, res);
  res.duelRec = duelRecOf(S);                                        // 화면이 처음부터 다시 그려 보일 수 있게(저장되지 않는다)
  return S;
}
function duelRecOf(S) { return { kind: S.kind, a: { id: S.a.id, st: S.a.st, max: S.a.max }, d: { id: S.d.id, st: S.d.st, max: S.d.max }, log: S.log, win: S.win, ko: S.ko, max: S.max }; }
/* 끝난 일기토의 결과를 부대에 입힌다(한 번만). res 가 있으면 res.duel 에 요약을 붙이고, 부대가 무너졌으면 res.killed · res.selfDead 도 */
function duelFinish(S, res) {
  if (!S || !S.over || S.done || S.kind !== 'duel') return null;
  S.done = true;
  var a = UMAP[S.ua], d = UMAP[S.ud], la = off(S.a.id), ld = off(S.d.id), out = { a: la.n, d: ld.n, win: S.win === 'a', draw: S.win === 'draw', ko: S.ko, rounds: S.round, loss: 0 };
  if (res) res.duel = out;
  if (!a || !d) return out;                                          // 그사이 부대가 사라졌다(일어나지 않아야 하지만 멈추지는 않는다)
  if (S.win === 'draw') {
    la.merit += DUEL_K.drawMerit; ld.merit += DUEL_K.drawMerit;
    logMsg('일기토! ' + la.n + ' 대 ' + ld.n + ' — ' + S.round + '합을 겨루고 비김', d.c, d.r, -1, (a.f === G.player || d.f === G.player) ? 2 : 0);
    return out;
  }
  var Wn = S.win === 'a' ? a : d, Ls = S.win === 'a' ? d : a, wl = S.win === 'a' ? la : ld;
  out.loss = Math.round(Ls.troops * (S.ko ? DUEL_K.koLoss : DUEL_K.loss));
  Ls.morale = Math.max(0, Ls.morale - (S.ko ? DUEL_K.koMor : DUEL_K.morLose)); Wn.morale = Math.min(100, Wn.morale + DUEL_K.morWin);
  wl.merit += DUEL_K.merit;
  logMsg('일기토! ' + la.n + ' 대 ' + ld.n + ' — ' + wl.n + (S.ko ? ' 승(' + S.round + '합 만에 쓰러뜨림)' : ' 승'), d.c, d.r, -1, (a.f === G.player || d.f === G.player) ? 2 : 0);
  var dead = hurtUnit(Ls, out.loss, Wn.f, Wn);
  if (dead) { if (res) { if (Ls === a) res.selfDead = true; else res.killed = true; } }
  else if (S.ko && !uHas(Ls, '통찰') && !uHas(Ls, '명경')) { setStatus(Ls, 'confuse', DUEL_K.koTurns); out.confused = true; }
  return out;
}
/* ---------- 일기토 신청(v0.13) ---------- */
function challengeTargets(u) {
  var out = [], ns = nbrs(u.c, u.r);
  for (var i = 0; i < ns.length; i++) { var o = UAT[K(ns[i][0], ns[i][1])]; if (o && o.f !== u.f && !o.status && !pactOn(u.f, o.f)) out.push({ kind: 'unit', u: o, c: o.c, r: o.r }); }
  return out;
}
function challengeChance(u, d) {                                    // 상대가 응할 확률(%)
  var la = uLeader(u), ld = uLeader(d), bold = ld.war >= 85 && ld.int < 70;
  return Math.round(clamp(DUEL_K.accBase + (ld.war - la.war) * DUEL_K.accK + (bold ? DUEL_K.accBold : 0), 5, 95));
}
function challengeRoll(u, d) { return omenRoll('duel|' + u.id + '|' + d.id); }      // 미리 정해 둔 결과(턴마다): 같은 턴에 다시 물어도 같다
function unitChallenge0(u, t) {
  if (u.done) return ERR('이미 행동을 마쳤습니다');
  if (u.status) return ERR('명령을 내릴 수 없는 부대입니다');
  var d = t && t.u;
  if (!d || !duelBattleOk(u, d)) return ERR('옆에 붙은 적 부대에만 걸 수 있습니다');
  if (d.status) return ERR('어지러운 부대는 응할 수 없습니다');
  if (u.morale < DUEL_K.ask) return ERR('기력이 부족합니다 (' + DUEL_K.ask + ' 필요)');
  var p = challengeChance(u, d), yes = challengeRoll(u, d) < p;
  u.morale -= DUEL_K.ask; u.done = true; u.ox = -1;
  var res = { ok: true, kind: 'challenge', c: d.c, r: d.r, ac: u.c, ar: u.r, tname: uName(d), p: p, accepted: yes };
  if (!yes) { d.morale = Math.max(0, d.morale - DUEL_K.refuse); res.mor = DUEL_K.refuse; logMsg(uLeader(u).n + '의 일기토 신청을 ' + josa(uLeader(d).n, '이가') + ' 받지 않음', d.c, d.r, -1, 0); return res; }
  duelBattle(u, d, res);
  return res;
}
function pactErr(u, t, ploy) { var tf = actTargetF(t), hf = actHoldF(t, ploy); return (tf >= 0 && tf !== u.f && pactOn(u.f, tf)) || (hf >= 0 && hf !== u.f && pactOn(u.f, hf)) ? ERR('협정을 맺은 세력은 칠 수 없습니다 — 치려면 먼저 협정을 깨야 합니다') : null; }
function unitChallenge(u, t) { var pe = pactErr(u, t); if (pe) return pe; var f = u.f, n = uName(u), ac = u.c, ar = u.r, tf = actTargetF(t); return actEv(u, t, unitChallenge0(u, t), f, n, ac, ar, tf, -1); }
/* ---------- 설전으로 등용(v0.13) ---------- */
function talkRecruitOk(b, o, t) { var p = recruitChance(b, o, t); return p >= DUEL_K.talkMin && p < 100; }
function talkRecruitNew(b, o, t) {
  var p = recruitChance(b, o, t), S = duelNew('talk', o, t, { hpD: Math.round(DUEL_K.hp * (1 + (DUEL_K.talkHp - p) / 100)) });
  S.rb = b.id; S.ro = o.id; S.rt = t.id; S.rp = p;
  return S;
}

/* 공격 가능한 대상 (현재 위치 기준) */
function attackTargets(u) {
  var out = [], rg = uRange(u), c, r;
  for (c = Math.max(0, u.c - rg - 1); c <= Math.min(W - 1, u.c + rg + 1); c++) for (r = Math.max(0, u.r - rg); r <= Math.min(H - 1, u.r + rg); r++) {
    var d = hdist(u.c, u.r, c, r);
    if (d < 1 || d > rg) continue;
    var k = K(c, r), ou = UAT[k];
    if (ou && ou.f !== u.f) { if (!pactOn(u.f, ou.f)) out.push({ kind: 'unit', u: ou, c: c, r: r, d: d }); continue; }      // v0.14: 협정을 맺은 세력은 칠 수 없다
    var bi = BAT[k];
    if (bi !== undefined) { var b = G.bases[bi]; if (b.owner >= 0 && b.owner !== u.f && !justOut(u) && !pactOn(u.f, b.owner)) out.push({ kind: 'base', b: b, c: c, r: r, d: d }); continue; }
    var pf = PAT[k];
    if (pf) { var pb = G.bases[pf.b], fc = pb.plots[pf.i].fac; if (fc && pb.owner >= 0 && pb.owner !== u.f && d === 1 && !justOut(u) && !pactOn(u.f, pb.owner)) out.push({ kind: 'fac', b: pb, i: pf.i, c: c, r: r, d: d }); }
  }
  var uf = facUnder(u); if (uf && !justOut(u)) out.push(uf);            // v0.12: 올라선 시설
  return out;
}
/* 부대가 올라서 있는 남의 시설(없으면 null) — v0.12 부터 시설 칸에 설 수 있다 */
function facUnder(u) {
  var pf = PAT[K(u.c, u.r)]; if (!pf) return null;
  var pb = G.bases[pf.b]; if (!pb.plots[pf.i].fac || pb.owner < 0 || pb.owner === u.f || pactOn(u.f, pb.owner)) return null;
  return { kind: 'fac', b: pb, i: pf.i, c: u.c, r: u.r, d: 0 };
}
function critNormal(a, d) { return (uHas(a, '비장') || uHas(a, '용장') || uHas(a, '신장')) && uWar(a) > uWar(d); }

function unitAttack0(u, t) {
  if (u.done) return ERR('이미 행동을 마쳤습니다');
  if ((t.kind === 'base' || t.kind === 'fac') && justOut(u)) return ERR('출진한 턴에는 거점과 시설을 칠 수 없습니다');
  var res = { ok: true, kind: t.kind, c: t.c, r: t.r, ac: u.c, ar: u.r };
  u.done = true; u.ox = -1;
  if (t.kind === 'unit') {
    var d = t.u, ranged = hdist(u.c, u.r, d.c, d.r) > 1;
    var crit = critNormal(u, d);
    var dmg = defMods(d, dmgUU(u, d, crit ? 1.3 : 1, ranged), 'normal');
    res.crit = crit; res.dmg = dmg; res.tname = uName(d);
    var dead = hurtUnit(d, dmg, u.f, u);
    afterHit(u, d, dmg);
    res.killed = dead;
    if (!dead && d.status !== 'confuse' && d.status !== 'rumor' && (!ranged || d.type === 'bow')) {
      if (!(uHas(u, '급습') && chance(50))) {
        var cm = ranged ? 0.4 : 0.55; if (d.type === 'bow' && !ranged) cm *= 0.6;
        var cd = defMods(u, dmgUU(d, u, cm, ranged), 'normal');
        res.counter = cd;
        if (hurtUnit(u, cd, d.f, d)) { res.selfDead = true; return res; }
      }
    }
    if (!dead && alive(u) && uHas(u, '연전') && chance(50)) {
      var d2 = defMods(d, dmgUU(u, d, 0.8, ranged), 'normal');
      res.dmg2 = d2; res.killed = hurtUnit(d, d2, u.f, u); afterHit(u, d, d2);
    }
    if (!ranged) tryDuel(u, d, res);
    return res;
  }
  if (t.kind === 'base') {
    var b = t.b, td = dmgUB(u, b), dd = durDmgUB(u), ranged2 = hdist(u.c, u.r, b.c, b.r) > 1;
    td = Math.min(td, b.troops);
    b.troops -= td; b.dur = Math.max(0, b.dur - dd);
    res.dmg = td; res.dur = dd; res.tname = b.n;
    addMerit(u, Math.round((td + dd) / 25));
    if (b.owner === G.player) logMsg(b.n + ' 피습! ' + facName(u.f) + ' ' + uName(u) + ' (병력 -' + nf(td) + ', 내구 -' + nf(dd) + ')', b.c, b.r, b.owner, 2);
    if (b.troops <= 0 || b.dur <= 0) {
      res.fell = true;
      if (!ranged2) captureBase(b, u);
      else {   // 원거리로 무너뜨리면 빈 거점이 된다
        var old = b.owner, os = baseOfficers(b), i;
        for (i = 0; i < os.length; i++) fleeOfficer(os[i], b.c, b.r, b.id);
        var held = b.captives.slice(); for (i = 0; i < held.length; i++) releaseCaptive(off(held[i]));
        logMsg(b.n + ' 수비대 궤멸 — 빈 거점이 되었다', b.c, b.r, old, 2);
        b.owner = -1; b.troops = 0; if (b.corps) b.corps = 0; b.dur = Math.max(b.dur, Math.round(b.maxDur * 0.3));
        checkFaction(old);
      }
      return res;
    }
    if (!ranged2 && b.troops > 0) { var cb = dmgBU(b, u); res.counter = cb; if (hurtUnit(u, cb, b.owner, null)) res.selfDead = true; }
    return res;
  }
  if (t.kind === 'fac') {
    var fc = t.b.plots[t.i].fac;
    if (!fc) return res;
    var fd = Math.round(uAtk(u) * 2.2 * troopFactor(u.troops));
    fc.hp -= fd; res.dmg = fd; res.tname = FAC[fc.t].name;
    if (fc.hp <= 0) { t.b.plots[t.i].fac = null; res.destroyed = true; u.gold += 100; logMsg(t.b.n + '의 ' + FAC[fc.t].name + ' 파괴됨', t.c, t.r, t.b.owner, 1); }
    return res;
  }
  return res;
}

/* 전법 */
function tacticList(u) {
  var list = TACTICS[u.type] || [], apt = uApt(u), out = [];
  for (var i = 0; i < list.length; i++) if (APT_RANK[apt] >= APT_RANK[list[i].need]) out.push(list[i]);
  return out;
}
function tacticCrit(u, d) {                    // 성공한 전법이 반드시 대성공이 되는가 → 그때의 배수(아니면 0). 여럿이 겹치면 큰 쪽
  var c = TACTIC_K.crit, g = TACTIC_K.critGod, m = 0;
  if (critNormal(u, d)) m = uHas(u, '신장') ? g : c;            // v0.9.3: 보통 공격이 치명타가 되는 조건(비장·용장·신장 + 상대보다 무력이 높다)이면 전법도. 신장은 피해 +10%
  if (u.type === 'spear' && (uHas(u, '창장') || uHas(u, '투신'))) m = Math.max(m, c);
  if (u.type === 'halberd' && (uHas(u, '극장') || uHas(u, '투신'))) m = Math.max(m, c);
  if (u.type === 'bow') { if (uHas(u, '궁신')) m = Math.max(m, g); else if (uHas(u, '궁장')) m = Math.max(m, c); }
  if (u.type === 'cav') { if (uHas(u, '기신')) m = Math.max(m, g); else if (uHas(u, '기장')) m = Math.max(m, c); }
  return m;
}
/* 전법의 성공·대성공 확률(%) — v0.8: 상대와 병력까지 본다. 대성공은 성공 안에 들어 있다.
   성공 = 적성(TACTIC_RATE)
        + 무장: (내 부대 최고 무력×0.6 + 내 주장 통솔×0.4 − 적 부대 최고 통솔) × 0.8      [−30 ~ +15]   (v0.8~0.9: × 0.6 [−24 ~ +12])
        + 병력: log2(내 병력 ÷ 적 병력) × 8                                              [−16 ~ +8]   (절반이면 −8, 두 배면 +8)
        + 적의 병과 적성: C +3 · B 0 · A −3 · S −6
        + 적이 선 곳: 숲·구릉 −5, 강 +5   + 적이 혼란 중 +10   + 맞는 특기(창장·기장…, 무력이 낮은 적을 치는 비장·용장·신장) +5
        → 10 ~ 95
   대성공 = 적성 + 무력 + (내 무력 − 상대 통솔). 맞는 특기가 있으면 성공한 전법은 모두 대성공 */
var TACTIC_CRIT = { C: 4, B: 8, A: 12, S: 18 };
function uLdr(u) { return bestOf(uMembers(u), 'ldr'); }
function tacticParts(u, d) {
  var pow = uWar(u) * 0.6 + uLeader(u).ldr * 0.4, td = terr(d.c, d.r);
  return { apt: TACTIC_RATE[uApt(u)],
    stat: Math.round(clamp((pow - uLdr(d)) * TACTIC_K.stat, TACTIC_K.statLo, TACTIC_K.statHi)),
    troops: Math.round(clamp(Math.log(Math.max(1, u.troops) / Math.max(1, d.troops)) / Math.LN2 * 8, -16, 8)),
    dapt: -3 * (APT_RANK[uApt(d)] - 1),
    terr: (td === 'f' || td === 'h') ? -5 : (td === 'w' ? 5 : 0),
    conf: d.status === 'confuse' ? 10 : 0,
    skill: tacticCrit(u, d) ? 5 : 0 };
}
function tacticOdds(u, d) {
  var forced = tacticCrit(u, d), P = tacticParts(u, d);
  var ok = Math.round(clamp(P.apt + P.stat + P.troops + P.dapt + P.terr + P.conf + P.skill, 10, 95));
  if (forced) return { ok: ok, crit: ok, mult: forced, sure: true, parts: P };
  var w = uWar(u);
  var cr = Math.round(clamp(TACTIC_CRIT[uApt(u)] + clamp((w - 70) * 0.5, -4, 15) + clamp((w - uLdr(d)) * 0.15, -6, 6), 2, 45));
  return { ok: ok, crit: Math.min(cr, ok), mult: TACTIC_K.crit, sure: false, parts: P };
}
/* 전법 피해에 얹는 병력 비: 큰 부대를 작은 부대가 전법 한 번으로 무너뜨리지 못한다(¼ 병력이면 ×0.75, 두 배 넘어도 ×1.1 까지) */
function tacticSizeK(u, d) { return clamp(Math.pow(Math.max(1, u.troops) / Math.max(1, d.troops), 0.25), 0.75, 1.1); }
/* 대성공이면 전법의 효과 자체가 세진다(TACTICS 의 great 가 덮어쓴다) */
function tacticEff(tac, crit) {
  if (!crit || !tac.great) return tac;
  var o = {}, k;
  for (k in tac) o[k] = tac[k];
  for (k in tac.great) o[k] = tac.great[k];
  return o;
}
/* 전법으로 혼란시킬 확률(%): 맞는 쪽의 지력·통솔이 높을수록 낮다. confuse 가 1 이상이면 반드시 */
function confuseOdds(e, d) {
  if (!e.confuse) return 0;
  if (e.confuse >= 1) return 100;
  return Math.round(clamp(e.confuse * 100 + (70 - (uInt(d) + uLdr(d)) / 2) * 0.6, 5, 95));
}
function tacticTargets(u, tac) {
  if (u.morale < tac.cost) return [];
  if (tac.noForest && terr(u.c, u.r) === 'f') return [];
  return attackTargets(u).filter(function (t) { return t.kind === 'unit' && !(tac.noForest && terr(t.c, t.r) === 'f'); });
}
function canPushInto(c, r, u) {
  if (!inMap(c, r)) return false;
  var t = terr(c, r), k = K(c, r);
  if (t === 'm' || t === 's' || t === 'x') return false;
  if (UAT[k] || BAT[k] !== undefined) return false;
  return true;                                                     // v0.12: 시설 칸으로도 밀려난다
}
function behindHex(u, d) {
  var dist = hdist(u.c, u.r, d.c, d.r), dx = cubeX(d.c, d.r) - cubeX(u.c, u.r), dz = d.r - u.r;
  if (dist === 1) return stepDir(d.c, d.r, dx, dz);
  if (dx % 2 === 0 && dz % 2 === 0) return stepDir(d.c, d.r, dx / 2, dz / 2);
  var ns = nbrs(d.c, d.r), best = null, bd = 0;
  for (var i = 0; i < ns.length; i++) { var q = hdist(u.c, u.r, ns[i][0], ns[i][1]); if (q > bd) { bd = q; best = ns[i]; } }
  return best;
}
/* 전법에 함께 맞는 적들: [부대, 피해 비율] — 밀어내기 전의 자리로 잡는다. e = 이번에 적용되는 효과(대성공이면 강화된 것) */
function tacticOthers(u, d, tac, e) {
  var others = [], i, ns, q;
  if (tac.arc) { ns = nbrs(u.c, u.r); for (i = 0; i < ns.length; i++) { q = UAT[K(ns[i][0], ns[i][1])]; if (q && q.f !== u.f && q !== d && hdist(q.c, q.r, d.c, d.r) === 1) others.push([q, e.side || 0.8]); } }
  if (tac.all) { ns = nbrs(u.c, u.r); for (i = 0; i < ns.length; i++) { q = UAT[K(ns[i][0], ns[i][1])]; if (q && q.f !== u.f && q !== d) others.push([q, 1.0]); } }
  if (tac.pierce) { var bh = behindHex(u, d); if (bh && inMap(bh[0], bh[1])) { q = UAT[K(bh[0], bh[1])]; if (q && q.f !== u.f) others.push([q, e.side || 0.8]); } }
  if (tac.splash) { ns = nbrs(d.c, d.r); for (i = 0; i < ns.length; i++) { q = UAT[K(ns[i][0], ns[i][1])]; if (q && q.f !== u.f && q !== d) others.push([q, e.side || 0.6]); } }
  return others;
}
/* 적 뒤로 n 칸까지 가운데 밀어낼 수 있는 칸 수 */
function pushRoom(u, d, n) {
  var dx = cubeX(d.c, d.r) - cubeX(u.c, u.r), dz = d.r - u.r, c = d.c, r = d.r, room = 0;
  for (var i = 0; i < n; i++) { var nx = stepDir(c, r, dx, dz); if (!canPushInto(nx[0], nx[1], d)) break; c = nx[0]; r = nx[1]; room++; }
  return room;
}
/* 보통 공격 한 번의 기대값(주사위 없이): 주는 피해 · 받는 반격. 맞은 뒤 줄어든 병력으로 반격이 약해지는 몫과 일기토는 넣지 않는다 */
function attackExpect(u, d) {
  var ranged = hdist(u.c, u.r, d.c, d.r) > 1, quiet = d.status === 'confuse' || d.status === 'rumor', bow = d.type === 'bow';
  var cN = quiet ? 0 : (ranged ? (bow ? 0.4 : 0) : 0.55 * (bow ? 0.6 : 1));
  return { dealt: dmgBase(u, d, 1, ranged) * (uHas(d, '금강') ? 0.65 : 1) * ((critNormal(u, d) ? 1.3 : 1) + (uHas(u, '연전') ? 0.4 : 0)),
    recv: dmgBase(d, u, 1, ranged) * (uHas(u, '금강') ? 0.65 : 1) * cN * (uHas(u, '급습') ? 0.5 : 1) };
}
/* 전법 한 번의 기대값(v0.9.1): 성공·대성공·실패를 확률대로 섞은 '주는 피해 · 받는 반격', 그리고 같은 자리에서 보통 공격을 했을 때의 값.
   넣은 것: 전법 배수 · 병력 비 · 대성공 배수 · 막힌 적을 밀 때의 +20% · 함께 맞는 적(extra) · 실패 때의 피해와 반격 · 반격을 받지 않는 경우(갈퀴·돌파, 멀리서 쏜 전법, 밀려나 떨어진 적, 혼란·위보 중인 적, 이 전법으로 혼란에 빠진 적) · 금강·철벽
   넣지 않은 것: 맞은 뒤 줄어든 병력으로 반격이 약해지는 몫, 일기토, 혼란·기력 깎기 같은 효과의 값어치 */
function tacticExpect(u, d, tac) {
  var ranged = hdist(u.c, u.r, d.c, d.r) > 1, quiet = d.status === 'confuse' || d.status === 'rumor', bow = d.type === 'bow';
  var od = tacticOdds(u, d), p = od.ok / 100, g = od.ok > 0 ? od.crit / od.ok : 0;            // g = 성공 가운데 대성공의 몫
  var kN = uHas(d, '금강') ? 0.65 : 1, kT = uHas(d, '철벽') ? 0.7 : 1;
  var e1 = tacticEff(tac, true), n0 = !ranged && tac.push ? tac.push : 0, n1 = !ranged && e1.push ? e1.push : 0;
  var room = (n0 || n1) ? pushRoom(u, d, Math.max(n0, n1)) : 0;
  var s0 = n0 && room < n0 ? 1.2 : 1, s1 = n1 && room < n1 ? 1.2 : 1;                          // 뒤가 막혀 있으면 +20%
  var AD = dmgBase(u, d, 1, ranged);
  var dealt = AD * (p * tac.mult * tacticSizeK(u, d) * kT * ((1 - g) * s0 + g * od.mult * s1) + (1 - p) * TACTIC_K.failDmg * kN);
  var os0 = tacticOthers(u, d, tac, tac), os1 = tacticOthers(u, d, tac, e1), extra = 0, i;
  for (i = 0; i < os0.length; i++) {
    var o = os0[i][0];
    extra += dmgBase(u, o, 1, hdist(u.c, u.r, o.c, o.r) > 1) * tac.mult * tacticSizeK(u, o) * (uHas(o, '철벽') ? 0.7 : 1) * ((1 - g) * os0[i][1] + g * od.mult * os1[i][1]);
  }
  extra *= p;
  var away = n0 > 0 && !tac.follow && room >= 1;                                               // 밀려나 한 칸 떨어진 적은 반격하지 못한다
  var cOk = (quiet || tac.noCounter || ranged || away) ? 0 : TACTIC_K.okCounter * (bow ? 0.6 : 1);
  cOk *= (1 - g) * (1 - confuseOdds(tac, d) / 100) + g * (1 - confuseOdds(e1, d) / 100);         // 이 전법으로 혼란에 빠진 적은 반격하지 못한다(나선첨·돌진)
  var cFl = quiet ? 0 : (ranged ? (bow ? 0.4 : 0) : TACTIC_K.failCounter * (bow ? 0.6 : 1));
  var N = attackExpect(u, d);
  return { ok: od.ok, crit: od.crit, dealt: dealt + extra, extra: extra, others: os0.length, recv: dmgBase(d, u, 1, ranged) * (uHas(u, '금강') ? 0.65 : 1) * (p * cOk + (1 - p) * cFl), nDealt: N.dealt, nRecv: N.recv };
}
function unitTactic0(u, tac, t) {
  if (u.done) return ERR('이미 행동을 마쳤습니다');
  if (u.morale < tac.cost) return ERR('기력이 부족합니다');
  var d = t.u, ranged = hdist(u.c, u.r, d.c, d.r) > 1;
  var res = { ok: true, kind: 'tactic', tac: tac.name, c: d.c, r: d.r, ac: u.c, ar: u.r, tname: uName(d), extra: [] };
  u.done = true; u.ox = -1; u.morale -= tac.cost;
  var od = tacticOdds(u, d), roll = rnd() * 100;
  res.pOk = od.ok; res.pCrit = od.crit;
  if (roll >= od.ok) {                                         // 실패: 피해는 보통 공격의 TACTIC_K.failDmg, 반격은 보통 공격보다 크게 받는다(원거리는 노병에게만)
    res.fail = true;
    var fdm = defMods(d, dmgUU(u, d, TACTIC_K.failDmg, ranged), 'normal');
    res.dmg = fdm; res.killed = hurtUnit(d, fdm, u.f, u);
    if (!res.killed && d.status !== 'confuse' && d.status !== 'rumor' && (!ranged || d.type === 'bow')) {
      var fc = defMods(u, dmgUU(d, u, ranged ? 0.4 : (d.type === 'bow' ? TACTIC_K.failCounter * 0.6 : TACTIC_K.failCounter), ranged), 'normal');
      res.counter = fc; if (hurtUnit(u, fc, d.f, d)) res.selfDead = true;
    }
    return res;
  }
  var crit = roll < od.crit ? od.mult : 0, e = tacticEff(tac, !!crit);      // e = 이번에 적용되는 효과(대성공이면 강화된 것)
  res.crit = !!crit;
  var cm = crit || 1;
  var dmg = defMods(d, dmgUU(u, d, tac.mult * cm * tacticSizeK(u, d), ranged), 'tactic');
  var oc = d.c, or_ = d.r, dx = cubeX(d.c, d.r) - cubeX(u.c, u.r), dz = d.r - u.r;
  // 부가 대상(먼저 목록을 잡아 둔다)
  var others = tacticOthers(u, d, tac, e), i;
  // 밀어내기
  if (e.push && !ranged) {
    for (i = 0; i < e.push; i++) {
      var nx = stepDir(d.c, d.r, dx, dz);
      if (canPushInto(nx[0], nx[1], d)) {
        var pc = d.c, pr = d.r;
        placeUnit(d, nx[0], nx[1]);
        res.pushed = (res.pushed || 0) + 1;
        if (tac.follow) placeUnit(u, pc, pr);
      } else { dmg = Math.round(dmg * 1.2); res.slam = true; break; }
    }
  }
  res.dmg = dmg; res.tc = d.c; res.tr = d.r;
  var dead = hurtUnit(d, dmg, u.f, u);
  afterHit(u, d, dmg);
  res.killed = dead;
  if (!dead) {
    if (e.moraleDmg) { var md = Math.min(d.morale, e.moraleDmg); d.morale -= md; if (md) res.mor = md; }
    var cp = confuseOdds(e, d);
    if (cp) { res.pConf = cp; if (cp >= 100 || chance(cp)) { setStatus(d, 'confuse', 1); res.confused = true; res.st = 'confuse'; res.stN = 1; } }
  }
  if (tac.fire) { if (setFire(oc, or_, e.fireT || 2)) res.fire = true; }
  if (tac.pass && !ranged) {
    var bx = stepDir(oc, or_, dx, dz);
    if (canPushInto(bx[0], bx[1], u) && moveCost(u, bx[0], bx[1]) < 99) { placeUnit(u, bx[0], bx[1]); res.passed = true; }
  }
  for (i = 0; i < others.length; i++) {
    var o2 = others[i][0];
    if (!alive(o2) || !alive(u)) continue;
    var od = defMods(o2, dmgUU(u, o2, tac.mult * cm * others[i][1] * tacticSizeK(u, o2), hdist(u.c, u.r, o2.c, o2.r) > 1), 'tactic');
    var ex = { c: o2.c, r: o2.r, dmg: od };
    res.extra.push(ex);
    var dead2 = hurtUnit(o2, od, u.f, u); afterHit(u, o2, od);
    if (!dead2 && e.moraleAll) { var m2 = Math.min(o2.morale, e.moraleAll); o2.morale -= m2; if (m2) ex.mor = m2; }
  }
  res.uc = u.c; res.ur = u.r;
  if (!dead && !tac.noCounter && !ranged && alive(u) && d.status !== 'confuse' && d.status !== 'rumor' && hdist(u.c, u.r, d.c, d.r) === 1) {
    var cd = defMods(u, dmgUU(d, u, d.type === 'bow' ? TACTIC_K.okCounter * 0.6 : TACTIC_K.okCounter, false), 'normal');
    res.counter = cd;
    if (hurtUnit(u, cd, d.f, d)) res.selfDead = true;
  }
  if (!ranged) tryDuel(u, d, res);
  return res;
}

/* 계략 */
function ployRange(u) { return uHas(u, '귀모') ? 2 : 1; }
function ployTargets(u, ploy) {
  var out = [], rg = ployRange(u), c, r;
  if (u.morale < ploy.cost) return out;
  if (ploy.id === 'douse') { var any = G.fires[K(u.c, u.r)]; nbrs(u.c, u.r).forEach(function (n) { if (G.fires[K(n[0], n[1])]) any = true; }); return any ? [{ c: u.c, r: u.r }] : []; }
  for (c = Math.max(0, u.c - rg - 1); c <= Math.min(W - 1, u.c + rg + 1); c++) for (r = Math.max(0, u.r - rg); r <= Math.min(H - 1, u.r + rg); r++) {
    var d = hdist(u.c, u.r, c, r);
    if (d < 1 || d > rg) continue;
    var k = K(c, r), ou = UAT[k];
    if (ploy.id === 'fire') {
      var t = terr(c, r);
      if (t === 'w' || t === 's' || t === 'm' || t === 'x' || BAT[k] !== undefined) continue;
      if (ou && (ou.f === u.f || pactOn(u.f, ou.f))) continue;
      var pf = PAT[k], enemyFac = pf && G.bases[pf.b].plots[pf.i].fac && G.bases[pf.b].owner !== u.f && !pactOn(u.f, G.bases[pf.b].owner);
      if (!ou && !enemyFac) continue;
      out.push({ c: c, r: r, u: ou || null });
    } else if (ou && ou.f !== u.f && !ou.status && !pactOn(u.f, ou.f)) out.push({ c: c, r: r, u: ou });
  }
  return out;
}
function ployChance(u, ploy, tu) {
  var it = uInt(u), base = ploy.id === 'fire' ? 55 : (ploy.id === 'confuse' ? 45 : 40), mul = ploy.id === 'fire' ? 1.2 : 1.5;
  if (ploy.id === 'douse') return 100;
  if (!tu) return 92;
  var ti = uInt(tu);
  if (uHas(tu, '통찰')) return 0;
  if (ploy.id !== 'fire' && uHas(tu, '명경')) return 0;
  if (uHas(tu, '간파') && ti > it) return 0;
  if (ploy.id === 'fire' && uHas(u, '화신')) return 100;
  if (uHas(u, '신산') && it > ti) return 100;
  var p = base + (it - ti) * mul;
  if (uHas(u, '허실')) p += 20;
  if (ploy.id === 'fire' && uHas(u, '화공')) p += 20;
  return clamp(Math.round(p), 5, 95);
}
function fireDamage(u) {
  var v = 250 + uInt(u) * 3;
  if (uHas(u, '화공')) v *= 1.5;
  if (uHas(u, '화신')) v *= 2;
  if (uHas(u, '심모')) v *= 1.5;
  return Math.round(v * (0.9 + rnd() * 0.2));
}
function applyPloy(u, ploy, c, r, tu, res) {
  var ext = uHas(u, '심모') ? 1 : 0;
  if (ploy.id === 'fire') {
    setFire(c, r, 3 + ext);
    if (tu && alive(tu) && !uHas(tu, '화신')) { var fd = fireDamage(u); res.dmg = (res.dmg || 0) + fd; tu.morale = Math.max(0, tu.morale - 5); res.killed = hurtUnit(tu, fd, u.f, u) || res.killed; }
    var pf = PAT[K(c, r)]; if (pf) { var fc = G.bases[pf.b].plots[pf.i].fac; if (fc) { fc.hp -= 300; if (fc.hp <= 0) G.bases[pf.b].plots[pf.i].fac = null; } }
  } else if (tu && alive(tu)) { setStatus(tu, ploy.id, 2 + ext); res.st = ploy.id; res.stN = 2 + ext; }
}
function unitPloy0(u, ploy, t) {
  if (u.done) return ERR('이미 행동을 마쳤습니다');
  if (u.morale < ploy.cost) return ERR('기력이 부족합니다');
  u.done = true; u.ox = -1; u.morale -= ploy.cost;
  var res = { ok: true, kind: 'ploy', ploy: ploy.name, c: t.c, r: t.r, ac: u.c, ar: u.r };
  if (ploy.id === 'douse') { delete G.fires[K(u.c, u.r)]; nbrs(u.c, u.r).forEach(function (n) { delete G.fires[K(n[0], n[1])]; }); res.success = true; return res; }
  var tu = t.u || null, p = ployChance(u, ploy, tu);
  res.p = p;
  if (ployRoll(ploy, t) < p) {                                          // v0.9: 미리 정해 둔 결과(같은 턴·같은 계략·같은 대상이면 같다)
    res.success = true;
    applyPloy(u, ploy, t.c, t.r, tu, res);
    addMerit(u, 30);
    if (uHas(u, '연환') && alive(u)) {
      var ns = nbrs(t.c, t.r);
      for (var i = 0; i < ns.length; i++) { var q = UAT[K(ns[i][0], ns[i][1])]; if (q && q.f !== u.f && !q.status) { applyPloy(u, ploy, q.c, q.r, q, res); res.chain = true; break; } }
    }
  } else {
    res.success = false;
    if (tu && uHas(tu, '반계') && alive(u)) {
      res.reflected = true;
      if (ploy.id === 'fire') { setFire(u.c, u.r, 2); if (!uHas(u, '화신')) { var rd = fireDamage(tu); res.selfDmg = rd; if (hurtUnit(u, rd, tu.f, tu)) res.selfDead = true; } }
      else if (!uHas(u, '통찰') && !uHas(u, '명경')) { setStatus(u, ploy.id, 2); res.selfSt = ploy.id; res.selfStN = 2; }
    }
  }
  return res;
}

/* ---------- 저장 ---------- */
/* 행동 + 연출용 사건 기록. tf = 맞은 쪽 세력(행동 전 기준) */
function actTargetF(t) { return t && t.u ? t.u.f : (t && t.b ? t.b.owner : -1); }
/* 이 행동이 건드리는 거점·시설의 주인(없으면 -1) — 행동 '전'에 잰다. 화계는 그 칸에 남의 시설이 있으면 시설을 친 것으로 본다 */
function actHoldF(t, ploy) {
  if (!t) return -1;
  if (t.kind === 'base' || t.kind === 'fac') return t.b ? t.b.owner : -1;
  if (ploy && ploy.id === 'fire') { var p = PAT[K(t.c, t.r)]; if (p && G.bases[p.b].plots[p.i].fac) return G.bases[p.b].owner; }
  return -1;
}
function actEv(u, t, res, f, name, ac, ar, tf, hf) {
  if (res && res.ok && G.peace && f === G.player && hf !== undefined && hf >= 0 && hf !== f && !G.peace.broken[hf]) {   // 플레이어가 남의 거점·시설을 먼저 치면 그 세력에 대한 보호가 풀린다
    G.peace.broken[hf] = true;
    if (G.turn < G.peace.until) {                                  // 보호 기간 안에 깼을 때만 화면에 알리고 기록한다
      res.brokePeace = hf;
      logMsg(facName(hf) + '군과의 보호가 풀렸다 — 우리가 먼저 ' + (t.kind === 'base' ? josa(t.b.n, '을를') : '시설을') + ' 침', t.c, t.r, f, 2);
    }
  }
  if (res && res.ok) {
    // 화면 연출에 쓰는 정보: 공격한 부대·맞은 부대의 번호와 병과, 행동 뒤의 자리
    res.aid = u.id; res.atype = u.type; res.af = f; res.ac0 = ac; res.ar0 = ar;
    res.alead = u.off[0]; res.tlead = t && t.u ? t.u.off[0] : -1;
    var df = tf !== undefined && tf >= 0 ? tf : (hf !== undefined ? hf : -1); if (df >= 0 && df !== f) dipHit(f, df, !!res.fell);      // v0.14: 치면 우호가 내려간다(시설을 태운 것도)      // v0.13: 두 부대의 대장(화면의 음성이 쓴다)
    res.ac1 = u.c; res.ar1 = u.r; res.aAlive = !!UMAP[u.id];
    res.tk = t ? t.kind : ''; res.tid = t && t.u ? t.u.id : -1; res.tbase = t && t.b ? t.b.id : -1; res.tf = tf;
    if (t && t.u) { res.tc1 = t.u.c; res.tr1 = t.u.r; res.tAlive = !!UMAP[t.u.id]; res.ttype = t.u.type; }
    ev({ t: 'act', f: f, name: name, ac: ac, ar: ar, tc: t && t.c, tr: t && t.r, tf: tf, res: res });
  }
  return res;
}
function unitAttack(u, t) { var pe = pactErr(u, t); if (pe) return pe; var f = u.f, n = uName(u), ac = u.c, ar = u.r, tf = actTargetF(t), hf = actHoldF(t, null); return actEv(u, t, unitAttack0(u, t), f, n, ac, ar, tf, hf); }
function unitTactic(u, tac, t) { var pe = pactErr(u, t); if (pe) return pe; var f = u.f, n = uName(u), ac = u.c, ar = u.r, tf = actTargetF(t); return actEv(u, t, unitTactic0(u, tac, t), f, n, ac, ar, tf, -1); }
function unitPloy(u, ploy, t) { var pe = pactErr(u, t, ploy); if (pe) return pe; var f = u.f, n = uName(u), ac = u.c, ar = u.r, tf = actTargetF(t), hf = actHoldF(t, ploy); return actEv(u, t, unitPloy0(u, ploy, t), f, n, ac, ar, tf, hf); }

/* ---------- 군사의 헌책(v0.11) ----------
   평소의 조언: 직접 다스리는 거점마다 '할 만한 일'을 후보로 뽑고(counselRaw), 군사의 지력으로 거른다(counsel).
   후보 { kind, b, w(급한 정도), d(알아채기 어려운 정도), x(그 일의 사실들) }. 말은 화면 쪽(counselText)에서 만든다. */
function bestBy(os, f) { var b = null, bv = -1e18; for (var i = 0; i < os.length; i++) { var v = f(os[i]); if (v > bv) { bv = v; b = os[i]; } } return b; }
function nbrThreat(b) {                                    // 길로 이어진 이웃 거점 가운데 다른 세력의 가장 큰 병력 { nb, troops } (없으면 null)
  var best = null;
  ADJ[b.id].forEach(function (e) { var nb = G.bases[e.to]; if (nb.owner >= 0 && nb.owner !== b.owner && (!best || nb.troops > best.troops)) best = { nb: nb.id, troops: nb.troops }; });
  return best;
}
function facGainAt(b, pi, t) { var p = b.plots[pi], g0 = goldIncome(b), f0 = foodIncome(b); p.fac = { t: t, lv: 1, done: true }; var g1 = goldIncome(b), f1 = foodIncome(b); p.fac = null; return { gold: g1 - g0, food: f1 - f0 }; }
function cityFoodTurns(b) { var need = Math.ceil(b.troops / 60); return need > 0 ? Math.floor(b.food / need) : 999; }
/* 무엇을 어디에 지을까: 급한 것(병영이 없다 · 병량 수입이 소비에 못 미친다)이 먼저, 아니면 수입이 가장 크게 느는 자리 → { t, pi, gain, why } 또는 null */
function buildPick(b, thr) {
  var em = [], i;
  for (i = 0; i < b.plots.length; i++) if (!b.plots[i].fac && !UAT[K(b.plots[i].c, b.plots[i].r)]) em.push(i);
  if (!em.length) return null;
  function bestPlot(t) { var bi = em[0], bv = -1e9; em.forEach(function (pi) { var g = facGainAt(b, pi, t), v = g.gold * 3 + g.food / 5; if (v > bv) { bv = v; bi = pi; } }); return { t: t, pi: bi, gain: facGainAt(b, bi, t), v: bv }; }
  function has(t) { for (var j = 0; j < b.plots.length; j++) if (b.plots[j].fac && b.plots[j].fac.t === t) return true; return false; }      // 짓는 중인 것도 센다
  var upkeep = Math.ceil(b.troops / 60) * 9, fi = foodIncome(b), r;
  if (!has('barracks') && thr && b.gold >= FAC.barracks.cost) { r = bestPlot('barracks'); r.why = 'nobarracks'; return r; }
  if (fi < upkeep && b.gold >= FAC.farm.cost) { r = bestPlot('farm'); r.why = 'food'; r.fi = fi; r.upkeep = upkeep; return r; }
  var cands = [];
  ['market', 'farm', 'mint', 'granary'].forEach(function (t) { if (b.gold >= FAC[t].cost) cands.push(bestPlot(t)); });
  cands.sort(function (x, y) { return y.v - x.v; });
  if (cands.length && cands[0].v > 0) { cands[0].why = 'income'; return cands[0]; }
  return null;
}
function counselRaw(f) {
  var F = G.factions[f], out = [], pl = (f === G.player && !G.aiOnly) ? peaceLeft() : 0;
  directBases(f).forEach(function (b) {
    var idle = idleOfficers(b); if (!idle.length) return;
    var city = b.kind === 'city', thr = nbrThreat(b);
    function add(kind, w, d, x) { out.push({ kind: kind, b: b.id, w: w, d: d, x: x || {} }); }
    function best(t) { var o = bestBy(idle, function (q) { return recruitChance(b, q, t) * 1000 - q.id; }); return { t: t.id, o: o.id, p: recruitChance(b, o, t) }; }
    // 훈련
    if (b.morale < 70 && b.troops >= 2000 && F.ap >= AP.train) add('train', 28 + (70 - b.morale) * 0.8 + (thr && !pl && thr.troops > b.troops * 0.7 ? 15 : 0), 30, { morale: b.morale });
    // 이웃의 주인 없는 거점 · 허술한 거점
    if (b.troops >= 3000 && F.ap >= AP.deploy) {
      var vac = null, weak = null;
      ADJ[b.id].forEach(function (e) { var nb = G.bases[e.to]; if (nb.owner < 0) { if (!vac) vac = nb; } else if (nb.owner !== f && nb.troops * 1.5 + 2000 < b.troops && (!weak || nb.troops < weak.troops)) weak = nb; });
      if (vac) add('vacant', 60, 55, { nb: vac.id });
      if (weak) { var brk = f === G.player && !G.aiOnly && peaceWouldBreak(weak.owner); add('strike', 42 + Math.min(15, (b.troops - weak.troops * 1.5 - 2000) / 1000) - (brk ? 14 : 0), 75, { nb: weak.id, def: weak.troops, troops: b.troops, brk: brk }); }
    }
    if (!city) return;
    // 순찰
    if (b.gold >= COST.patrol && F.ap >= AP.patrol) {
      if (b.order < 60) add('patrol', 62 + (60 - b.order) * 0.6, 10, { order: b.order, by: bestBy(idle, function (o) { return Math.max(o.war, o.ldr) + (o.sk === '위압' ? 40 : 0); }).id });
      else if (b.order < 80 && b.gold >= 300) add('patrol2', 22, 45, { order: b.order });
    }
    // 등용: 이 거점의 재야 · 포로, 이웃 세력의 무장(누가 응할지는 군사가 가린다)
    if (F.ap >= AP.recruit) {
      var ts = freeOfficers(b).concat(baseCaptives(b).filter(function (o) { return o.capF === f; })).filter(function (t) { return !askWait(t); });
      if (ts.length) add('recruit', 60, 30, { ts: ts.map(best) });
      var far = poachTargets(b).filter(function (t) { return !askWait(t); }).map(best).filter(function (x) { return x.p >= COUNSEL.poachMin; });
      if (far.length) add('poach', 64, 50, { ts: far });
    }
    // 탐색: 숨은 인재가 있는지(x.hid)는 군사가 헤아린다
    if (F.ap >= AP.search) { var so = bestBy(idle, searchSkill); add('search', 50, 60, { hid: hiddenOfficers(b).length > 0, o: so.id, p: searchChance(b, so) }); }
    // 포상
    if (b.gold >= COST.reward && F.ap >= AP.reward) { var lo = null; baseOfficers(b).forEach(function (o) { if (!isLord(o) && !bondOf(o) && o.loy < 80 && (!lo || o.loy < lo.loy)) lo = o; }); if (lo) add('reward', 40 + (80 - lo.loy) * 1.5, 35, { t: lo.id, loy: lo.loy }); }
    // 징병: 이웃 세력의 병력이 우리보다 많을 때만(병량이 한 분기를 못 버티면 권하지 않는다)
    if (hasFac(b, 'barracks') && b.gold >= COST.draft && b.order >= 30 && F.ap >= AP.draft && thr && b.troops < thr.troops * 0.8 && cityFoodTurns(b) >= 9) {
      var soon = pl <= 9;
      add('draft', soon ? 58 + Math.min(20, (thr.troops - b.troops) / 1000 * 2) : 30, 40, { nb: thr.nb, thr: thr.troops, troops: b.troops, soon: soon, pl: pl, order: b.order });
    }
    // 건설: 무엇을 어디에
    var bp = F.ap >= AP.develop ? buildPick(b, thr) : null;
    if (bp) add('build', (bp.why === 'income' ? 34 : 48) + (b.gold >= FAC[bp.t].cost * 3 ? 10 : 0), 50, { t: bp.t, pi: bp.pi, gain: bp.gain, why: bp.why, fi: bp.fi, upkeep: bp.upkeep, empty: b.plots.filter(function (q) { return !q.fac; }).length });
    // 무기
    if (hasFac(b, 'smithy') && b.gold >= COST.produce && F.ap >= AP.produce) { var arms = b.w.spear + b.w.halberd + b.w.bow; if (b.troops >= 3000 && arms < b.troops * 0.6) add('produce', 30, 45, { arms: arms, troops: b.troops }); }
    // 거래
    if (hasFac(b, 'market') && F.ap >= AP.trade) {
      var ft = cityFoodTurns(b);
      if (ft < 9 && b.gold >= 300) add('buyfood', 66, 30, { ft: ft });
      else if (b.gold < 150 && ft > 40) add('sellfood', 32, 55, { gold: b.gold });
    }
  });
  var seenNb = {};                                                       // 같은 이웃 거점(빈 곳 · 허술한 곳)은 병력이 가장 많은 우리 거점에서 한 번만
  out.forEach(function (c) { if (c.kind !== 'vacant' && c.kind !== 'strike') return; var k = c.kind + c.x.nb, o = seenNb[k]; if (!o || G.bases[c.b].troops > G.bases[o.b].troops) seenNb[k] = c; });
  return out.filter(function (c) { return (c.kind !== 'vacant' && c.kind !== 'strike') || seenNb[c.kind + c.x.nb] === c; });
}
/* 군사의 눈으로 거른 헌책 { adv, lvl(말의 자세함 0~2), list(급한 것부터) } — 군사가 없으면 뻔한 일(d ≤ 40)만 */
function counsel(f) {
  var A = facAdv(f), raw = counselRaw(f), out = [];
  var acc0 = A ? adviceAcc(A, 0) : 0, amp = A ? COUNSEL.noise * (100 - A.int) / 50 : 0, lvl = !A ? 1 : (A.int >= COUNSEL.detail ? 2 : (A.int >= COUNSEL.some ? 1 : 0));
  raw.forEach(function (c) {
    var key = c.kind + ':' + c.b, b = G.bases[c.b];
    if (!A) { if (c.d > 40) return; if (c.kind === 'recruit') { c.x.pick = c.x.ts[0]; c.x.says = null; } }
    else {
      if (c.kind === 'recruit' || c.kind === 'poach') {                  // 응할 사람을 군사가 가려낸다(맞힐 확률 = 적중률)
        var yes = [], no = [];
        c.x.ts.forEach(function (x) { var t = off(x.t), a = advise(f, recruitRoll(t), recruitRollA(t), x.p, t.int); x.says = !!(a && a.says); (x.says ? yes : no).push(x); });
        yes.sort(function (p1, p2) { return statSum(off(p2.t)) - statSum(off(p1.t)) || p1.t - p2.t; });
        if (c.kind === 'poach') { if (!yes.length) return; c.x.pick = yes[0]; c.x.says = true; }
        else if (yes.length) { c.x.pick = yes[0]; c.x.says = true; c.w = 72 + Math.min(15, statSum(off(yes[0].t)) / 30); }
        else { c.x.pick = no[0]; c.x.says = false; c.w = 18; }
        if (lvl === 0 && c.kind === 'recruit') c.w = 55;                 // 지력이 낮으면 누가 응할지 가리지 못한다
      }
      if (c.kind === 'search') {                                         // 숨은 인재가 있는지: 적중률만큼 바르게 안다(달마다 정해진다)
        var knows = omenRoll('adv|hid' + c.b, true) < acc0, belief = knows ? c.x.hid : !c.x.hid;
        if (!belief) return;
        var sa = advise(f, searchRoll(b), searchRollA(b), c.x.p, 0);
        c.x.says = !!(sa && sa.says); c.w = lvl === 0 ? 40 : (c.x.says ? 68 : 26);
      }
      if (c.d > A.int && omenRoll('adv|see|' + key, true) < (c.d - A.int) * COUNSEL.seeK) return;      // 놓쳤다
    }
    c.key = key; c.lvl = lvl;
    c.ws = c.w + (A ? (omenRoll('adv|w|' + key) / 100 - 0.5) * amp : 0);
    out.push(c);
  });
  out.sort(function (a, b2) { return b2.ws - a.ws || a.b - b2.b || (a.kind < b2.kind ? -1 : 1); });
  return { adv: A, lvl: lvl, list: out };
}

function serialize() { return JSON.stringify(G); }
function deserialize(s) {
  var g = JSON.parse(s);
  if (!g || g.ver !== 2) return false;
  // 초상은 저장본이 아니라 지금 판의 명부를 따른다(예전 저장을 열어도 새로 그린 초상이 나오게)
  for (var i = 0; i < g.officers.length; i++) { var so = SCENARIO.officers[i]; if (so && so.n === g.officers[i].n) g.officers[i].por = so.por; }
  // 세력 색도 지금 판의 색(석채 빛)을 따른다
  for (var j = 0; j < g.factions.length; j++) { var sf = SCENARIO.factions[j]; if (sf && sf.n === g.factions[j].name) g.factions[j].color = sf.color; }
  // v0.8: 부지가 늘었다(6·8·10 → 10·13·16). 옛 저장에는 앞쪽 부지만 있으므로 뒤에 덧붙인다(앞쪽은 자리·순서가 그대로다)
  for (var bi = 0; bi < g.bases.length; bi++) {
    var gb = g.bases[bi], mb = MAPDATA.bases[bi], pl = (mb && mb.n === gb.n && MAPDATA.plots[gb.n]) || [];
    if (!gb.plots) gb.plots = [];
    for (var pj = gb.plots.length; pj < pl.length; pj++) gb.plots.push({ c: pl[pj][0], r: pl[pj][1], fac: null });
  }
  // v0.8.1: 초반 보호. 0.8까지의 저장에는 없다 — 그 세력의 시작 병력으로 기간을 정해 붙인다(아직 그 기간 안이면 보호받는다. 누구를 먼저 쳤는지는 알 수 없어 비워 둔다)
  if (!g.peace && SCENARIO.factions[g.player]) g.peace = { until: 1 + peaceFor(startTroops(g.player)), broken: {}, v: 2 };
  // v0.9.1: 보호 기간이 짧아졌다(36/24/12턴 → 18/12/9턴). 0.8.1~0.9 에서 시작한 판은 옛 끝이 저장되어 있다 — 새 기간으로 당기되, 불러온 때부터 적어도 30일은 남긴다
  var peaceCut = 0;
  if (g.peace && !g.peace.v) {
    var nu = SCENARIO.factions[g.player] ? 1 + peaceFor(startTroops(g.player)) : g.peace.until;
    if (nu < g.peace.until && g.turn < g.peace.until) { peaceCut = g.peace.until; g.peace.until = Math.max(nu, Math.min(g.peace.until, g.turn + 3)); if (g.peace.until === peaceCut) peaceCut = 0; }
    g.peace.v = 2;
  }
  if (g.seed0 === undefined) g.seed0 = (g.seed ^ 0x2545F491) | 0;        // v0.9: 미리 정해 두는 결과의 고정 씨앗(옛 저장에는 없다 — 열 때 한 번 정해 저장본에 남는다)
  if (!g.corps) { g.corps = []; g.nextCorps = 1; }                         // v0.10: 군단(옛 저장에는 없다)
  G = g; reindex(); REPORT = []; EVQ = []; JOT = null;
  var tfix = terrainFix();                                               // v0.15: 산이 넓어졌다 — 못 가는 칸에 서 있던 부대를 옮긴다
  for (var ti = 0; ti < tfix.length; ti++) if (tfix[ti].f === G.player) logMsg(uName(tfix[ti]) + ' — 지형이 바뀌어(v0.15) 옆의 갈 수 있는 칸으로 옮겼습니다', tfix[ti].c, tfix[ti].r, G.player, 1);
  corpsFix();
  pastSweep();                                                           // v0.11: 섬겼던 세력(옛 저장에는 없다 — 시나리오의 세력으로 미루어 채운다)
  if (peaceCut) { var pcap = facCities(G.player)[0] || facBases(G.player)[0]; if (pcap) logMsg('초반 보호 기간이 짧아졌습니다(v0.9.1) — 이 판의 보호는 ' + dateOfTurn(G.peace.until - 1) + '까지입니다(전에는 ' + dateOfTurn(peaceCut - 1) + '까지)', pcap.c, pcap.r, G.player, 2); REPORT = []; }
  for (var fi = 0; fi < G.factions.length; fi++) if (G.factions[fi].adv === undefined) { G.factions[fi].adv = -1; if (G.factions[fi].alive) autoAdvisor(fi); }   // v0.9: 군사
  for (var oi = 0; oi < G.officers.length; oi++) { var go = G.officers[oi]; if (go.f >= 0 && go.st !== 'hidden' && bondOf(go)) go.loy = 100; }   // v0.8: 인연이 있는 무장
  return true;
}
