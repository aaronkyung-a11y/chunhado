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
var NHEX = W * H, NBR = new Int32Array(NHEX * 6), TCH = new Uint8Array(NHEX), RDB = new Uint8Array(NHEX);
var MC = [new Uint8Array(NHEX), new Uint8Array(NHEX), new Uint8Array(NHEX)];
(function () {
  for (var r = 0; r < H; r++) for (var c = 0; c < W; c++) {
    var k = r * W + c, t = MAPDATA.t.charAt(k), rd = MAPDATA.road.charAt(k) === '1', d = (r & 1) ? NB_ODD : NB_EVEN;
    TCH[k] = t.charCodeAt(0); RDB[k] = rd ? 1 : 0;
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
   성역의 경계를 넘는 걸음(들어가든 나오든)을 디디면 그 턴의 이동은 거기서 끝난다 →
   성에서 나와(1턴째에 경계 밖에서 멈춤) 다른 성의 성역에 들어서고(멈춤) 성에 닿기까지 적어도 3턴(30일)이 걸린다. */
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
function dateStr() { return G.year + '년 ' + G.month + '월 ' + ['상순', '중순', '하순'][G.xun]; }

function baseOfficers(b) {
  var out = [];
  if (b.owner < 0) return out;
  for (var i = 0; i < G.officers.length; i++) { var o = G.officers[i]; if (o.st === 'active' && o.f === b.owner && o.loc === b.id && o.unit === null) out.push(o); }
  return out;
}
function idleOfficers(b) { return baseOfficers(b).filter(function (o) { return !o.acted; }); }
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

/* 이번 턴 이동 가능 범위. 반환: { cost:{key:cost}, prev:{key:key}, stop:{key:true} } */
function unitReach(u) {
  var cost = {}, prev = {}, stop = {}, start = K(u.c, u.r), h = new Heap();
  var ignoreZoc = uHas(u, '비장'), z0 = ZONE[start];
  cost[start] = 0; h.push(0, start);
  while (h.a.length) {
    var top = h.pop(), d = top[0], k = top[1];
    if (d > cost[k]) continue;
    var c = k % W, r = (k - c) / W;
    if (k !== start) {
      if (BAT[k] !== undefined) continue;                              // 거점에 들어가면 이동 끝
      if (ZONE[k] !== z0) continue;                                    // 성역의 경계를 넘었으면 이동 끝
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
      var pf = PAT[nk];
      if (pf && G.bases[pf.b].plots[pf.i].fac) continue;               // 시설
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
      var pf = PAT[nk];
      if (pf && G.bases[pf.b].plots[pf.i].fac) continue;
      var ou = UAT[nk];
      if (ou) mc += (ou.f === u.f ? 3 : 25);
      if (G.fires[nk]) mc += 6;
      if (ZONE[nk] !== ZONE[k]) mc += ZONE_PEN;
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
    player: playerFaction, factions: [], officers: [], bases: [], units: [], fires: {}, nextUnit: 1, log: [], over: null, aiOnly: false
  };
  for (i = 0; i < SCENARIO.factions.length; i++) {
    var sf = SCENARIO.factions[i];
    G.factions.push({ id: i, name: sf.n, color: sf.color, lord: -1, ap: 80, alive: true });
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
      f: so.f, st: so.st || 'active', loc: baseByName(so.c), unit: null, loy: 100, merit: 0, acted: false, y: so.y || 0, j: so.j || null, capF: -1, dest: -1, eta: 0 };
    if (o.f >= 0) {
      if (SCENARIO.factions[o.f].n === o.n) { G.factions[o.f].lord = i; o.merit = 2000; }
      else { o.loy = 78 + ((o.n.charCodeAt(0) + o.n.charCodeAt(o.n.length - 1)) % 20); o.merit = Math.max(0, (o.ldr + o.war - 120) * 20); }
    }
    G.officers.push(o);
  }
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
  var L = off(G.factions[f].lord), v = 50 + 8 * facCities(f).length + Math.floor(L.cha / 5);
  var os = facOfficers(f);
  if (anyHas(os, '지도')) v += 10;
  if (anyHas(os, '왕좌')) v += 15;
  return Math.min(160, v);
}

/* ---------- 턴 진행 ---------- */
function phaseStart(f) {
  var F = G.factions[f], i;
  if (!F.alive) return;
  F.ap = Math.min(255, F.ap + apRegen(f));
  for (i = 0; i < G.officers.length; i++) {
    var o = G.officers[i];
    if (o.f !== f) continue;
    if (o.st === 'active') o.acted = false;
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
      if (fc && !fc.done) { fc.prog += fc.rate; if (fc.prog >= fc.need) { fc.done = true; fc.hp = FAC_HP; if (f === G.player) logMsg(b.n + '에 ' + FAC[fc.t].name + ' 완공', b.plots[j].c, b.plots[j].r, f, 1); } }
    }
  }
  var us = facUnits(f);
  for (i = 0; i < us.length; i++) {
    var u = us[i];
    if (!UMAP[u.id]) continue;
    u.mp = uMaxMp(u); u.done = false; u.moved = false; u.ox = -1; u.zin = -1;
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
      if (u.stT <= 0) { u.status = null; }
      else {
        u.stT--;
        if (u.status === 'rumor') autoRetreat(u);
        if (UMAP[u.id]) u.done = true;
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
  // 날짜
  G.turn++; G.xun++;
  if (G.xun > 2) { G.xun = 0; G.month++; if (G.month > 12) { G.month = 1; G.year++; } }
  var newMonth = G.xun === 0, newQuarter = newMonth && (G.month === 1 || G.month === 4 || G.month === 7 || G.month === 10), newYear = newMonth && G.month === 1;
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
      if (o.loy > 60 && chance(30)) o.loy--;
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
        if (lb && lb.owner === lf) { h.st = 'active'; h.f = lf; h.loc = lb.id; h.loy = 95; h.j = null; logMsg(josa(h.n, '이가') + ' 장성하여 ' + facName(lf) + ' 진영에 가담', lb.c, lb.r, lf, 1); continue; }
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
  return function () {
    if (G.over) return null;
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
  b.dur = Math.max(b.dur, Math.round(b.maxDur * 0.3));
  if (b.kind === 'city') b.order = Math.max(20, b.order - 25);
  addMerit(u, 300);
  enterBase(u, b);
  checkFaction(old);
  checkVictory();
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
  p.fac = { t: type, lv: 1, done: false, prog: 0, need: F.build, rate: rate, hp: 300 };
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
  var f = b.plots[pi].fac, cost = 150 * f.lv;
  var os = getIdle(b, ids); if (!os || os.length !== 1) return ERR('담당 무장을 고르세요');
  if (b.gold < cost) return ERR('금이 부족합니다 (' + cost + ' 필요)');
  if (!needAP(b.owner, AP.merge)) return ERR('행동력이 부족합니다');
  b.gold -= cost; useAP(b.owner, AP.merge);
  f.lv++; b.plots[pj].fac = null;
  markActed(os, 30);
  return { ok: true, lv: f.lv };
}
function cmdDemolish(b, pi) { if (!b.plots[pi] || !b.plots[pi].fac) return ERR('시설이 없습니다'); b.plots[pi].fac = null; return { ok: true }; }

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
  if (b.gold < 300) return ERR('금이 부족합니다 (300 필요)');
  if (b.order < 20) return ERR('치안이 너무 낮습니다');
  if (!needAP(b.owner, AP.draft)) return ERR('행동력이 부족합니다');
  var n = draftAmount(b, os);
  b.gold -= 300; useAP(b.owner, AP.draft);
  b.morale = Math.round((b.troops * b.morale + n * 35) / Math.max(1, b.troops + n));
  b.troops += n;
  b.order = Math.max(0, b.order - (anyHas(os, '인덕') ? 5 : 10));
  markActed(os, 30);
  return { ok: true, n: n };
}
function cmdPatrol(b, ids) {
  if (b.kind !== 'city') return ERR('도시에서만 가능합니다');
  var os = getIdle(b, ids); if (!os || !os.length || os.length > 3) return ERR('담당 무장을 고르세요');
  if (b.gold < 100) return ERR('금이 부족합니다 (100 필요)');
  if (!needAP(b.owner, AP.patrol)) return ERR('행동력이 부족합니다');
  var best = Math.max(bestOf(os, 'war'), bestOf(os, 'ldr'));
  var v = Math.round(5 + best / 9 + (os.length - 1) * 2);
  if (anyHas(os, '위압')) v *= 2;
  b.gold -= 100; useAP(b.owner, AP.patrol);
  var before = b.order; b.order = Math.min(100, b.order + v);
  markActed(os, 20);
  return { ok: true, n: b.order - before };
}
function cmdTrain(b, ids) {
  var os = getIdle(b, ids); if (!os || !os.length || os.length > 3) return ERR('담당 무장을 고르세요');
  if (!needAP(b.owner, AP.train)) return ERR('행동력이 부족합니다');
  if (b.troops <= 0) return ERR('병력이 없습니다');
  var v = Math.round(8 + bestOf(os, 'ldr') / 8 + (os.length - 1) * 2);
  useAP(b.owner, AP.train);
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
  var cost = kind === 'ram' ? (anyHas(os, '발명') ? 300 : 600) : 300;
  if (b.gold < cost) return ERR('금이 부족합니다 (' + cost + ' 필요)');
  if (!needAP(b.owner, AP.produce)) return ERR('행동력이 부족합니다');
  b.gold -= cost; useAP(b.owner, AP.produce);
  var n = kind === 'ram' ? 1 : produceAmount(b, kind, os);
  b.w[kind] += n;
  markActed(os, 30);
  return { ok: true, n: n };
}
function cmdTrade(b, dir, gold) {
  if (!hasFac(b, 'market')) return ERR('시장이 필요합니다');
  if (!needAP(b.owner, AP.trade)) return ERR('행동력이 부족합니다');
  gold = Math.floor(gold);
  if (gold <= 0) return ERR('수량을 정하세요');
  if (dir === 'buy') { if (b.gold < gold) return ERR('금이 부족합니다'); b.gold -= gold; b.food += gold * 4; useAP(b.owner, AP.trade); return { ok: true, n: gold * 4 }; }
  if (b.food < gold * 6) return ERR('병량이 부족합니다');
  b.food -= gold * 6; b.gold += gold; useAP(b.owner, AP.trade);
  return { ok: true, n: gold };
}
function cmdSearch(b, id) {
  if (b.kind !== 'city') return ERR('도시에서만 가능합니다');
  var os = getIdle(b, [id]); if (!os) return ERR('담당 무장을 고르세요');
  if (!needAP(b.owner, AP.search)) return ERR('행동력이 부족합니다');
  useAP(b.owner, AP.search);
  var o = os[0]; markActed(os, 15);
  var hid = hiddenOfficers(b);
  if (hid.length) {
    var p = 25 + o.pol * 0.35 + o.cha * 0.15;
    if (o.sk === '안력') p *= 2;
    if (chance(p)) { var h = pick(hid); h.st = 'free'; return { ok: true, found: h.id }; }
  }
  if (chance(35)) { var g = ri(5, 20) * 10; b.gold += g; return { ok: true, gold: g }; }
  return { ok: true };
}
function recruitChance(b, o, t) {
  var p = 35 + (o.cha - 50) * 0.7 + (o.pol - 50) * 0.2;
  var L = off(G.factions[b.owner].lord);
  p += (L.cha - 70) * 0.4;
  if (o.sk === '논객') p += 20;
  if (t.st === 'captive') { p -= 15; if (t.f >= 0 && G.factions[t.f].alive) p -= (t.loy - 60) * 0.8; }
  return clamp(Math.round(p), 3, 95);
}
function cmdRecruit(b, id, tid) {
  var os = getIdle(b, [id]); if (!os) return ERR('담당 무장을 고르세요');
  var t = off(tid);
  if (!t || t.loc !== b.id || !((t.st === 'free') || (t.st === 'captive' && t.capF === b.owner))) return ERR('등용할 수 없는 대상입니다');
  if (!needAP(b.owner, AP.recruit)) return ERR('행동력이 부족합니다');
  useAP(b.owner, AP.recruit);
  var o = os[0]; markActed(os, 15);
  if (chance(recruitChance(b, o, t))) {
    if (t.st === 'captive') { var i = b.captives.indexOf(t.id); if (i >= 0) b.captives.splice(i, 1); }
    t.st = 'active'; t.f = b.owner; t.capF = -1; t.unit = null; t.acted = true; t.loy = 70 + ri(0, 15); t.merit = Math.round(t.merit * 0.5);
    o.merit += 60;
    return { ok: true, joined: true };
  }
  return { ok: true, joined: false };
}
function cmdReward(b, tid) {
  var t = off(tid);
  if (!t || t.f !== b.owner || t.st !== 'active' || t.loc !== b.id) return ERR('대상이 없습니다');
  if (b.gold < 100) return ERR('금이 부족합니다 (100 필요)');
  if (!needAP(b.owner, AP.reward)) return ERR('행동력이 부족합니다');
  if (t.loy >= 100) return ERR('이미 충성도가 최고입니다');
  b.gold -= 100; useAP(b.owner, AP.reward);
  var before = t.loy; t.loy = Math.min(100, t.loy + ri(8, 12));
  return { ok: true, n: t.loy - before };
}
function travelTurns(a, b) { return Math.max(1, Math.round(hdist(a.c, a.r, b.c, b.r) / 10)); }
function cmdMoveOfficers(b, ids, destId) {
  var d = G.bases[destId];
  if (!d || d.owner !== b.owner || d.id === b.id) return ERR('갈 수 없는 곳입니다');
  var os = getIdle(b, ids); if (!os || !os.length) return ERR('무장을 고르세요');
  if (!needAP(b.owner, AP.move)) return ERR('행동력이 부족합니다');
  useAP(b.owner, AP.move);
  var t = travelTurns(b, d);
  for (var i = 0; i < os.length; i++) { os[i].st = 'travel'; os[i].dest = d.id; os[i].eta = t; os[i].acted = true; }
  return { ok: true, turns: t };
}
function cmdCaptive(b, tid, action) {
  var t = off(tid);
  if (!t || t.st !== 'captive' || t.loc !== b.id || t.capF !== b.owner) return ERR('대상이 없습니다');
  if (action === 'release') { releaseCaptive(t); return { ok: true }; }
  if (action === 'execute') { var i = b.captives.indexOf(t.id); if (i >= 0) b.captives.splice(i, 1); t.st = 'dead'; t.f = -1; t.capF = -1; return { ok: true }; }
  return ERR('?');
}

/* ---------- 출진 ---------- */
function deploySpot(b, toward) {
  var ns = nbrs(b.c, b.r), best = null, bs = 1e9;
  for (var i = 0; i < ns.length; i++) {
    var c = ns[i][0], r = ns[i][1], k = K(c, r), t = terr(c, r);
    if (t === 'm' || t === 's' || t === 'x') continue;
    if (UAT[k] || BAT[k] !== undefined) continue;
    var pf = PAT[k]; if (pf && G.bases[pf.b].plots[pf.i].fac) continue;
    var s = (t === 'w' ? 10 : 0) + (isRoad(c, r) ? 0 : 2) + (G.fires[k] ? 20 : 0);
    if (toward) s = hdist(c, r, toward.c, toward.r) + (t === 'w' ? 3 : 0) + (G.fires[k] ? 20 : 0);
    if (s < bs) { bs = s; best = [c, r]; }
  }
  return best;
}
/* spec: { type, ids, troops, food, gold, cargo, toward } */
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
  var spot = deploySpot(b, spec.toward);
  if (!spot) return ERR('성 밖에 나갈 자리가 없습니다');
  useAP(b.owner, AP.deploy);
  b.troops -= troops; b.food -= food; b.gold -= gold;
  if (T.weapon === 'ram') b.w.ram -= 1; else if (T.weapon) b.w[T.weapon] -= troops;
  if (cargo) for (k in cargo) b.w[k] -= cargo[k];
  var u = { id: G.nextUnit++, f: b.owner, c: spot[0], r: spot[1], type: spec.type, off: os.map(function (o) { return o.id; }), troops: troops, max: troops,
    morale: b.morale, food: food, gold: gold, cargo: cargo, status: null, stT: 0, done: false, moved: false, mp: 0, home: b.id, ox: -1, oy: -1, omp: 0, ozin: -1, zin: -1, ai: null, dest: -1 };
  for (var i = 0; i < os.length; i++) { os[i].unit = u.id; os[i].acted = true; }
  u.mp = uMaxMp(u);
  if (spec.dest !== undefined && spec.dest >= 0) u.dest = spec.dest;
  addUnit(u);
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
  u.ox = u.c; u.oy = u.r; u.omp = u.mp; u.ozin = (u.zin === undefined ? -1 : u.zin);
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
  if (ZONE[k] !== ZONE[K(from[0], from[1])]) { u.mp = 0; u.zin = ZONE[k]; }   // 성역의 경계를 넘었으면 이번 턴 이동은 여기까지. 막 들어선 성역의 성은 이번 턴에 칠 수 없다(zin)
  u.moved = true;
  var res = { ok: true, path: path, from: from };
  ev({ t: 'move', id: u.id, f: u.f, n: uName(u), from: from, path: path, c: c, r: r });
  if (G.fires[k] && !uHas(u, '화신')) { var fd = ri(150, 250); res.burn = fd; u.ox = -1; if (hurtUnit(u, fd, -1)) res.dead = true; }
  return res;
}
function unitUndoMove(u) {
  if (u.done || u.ox < 0 || !UMAP[u.id]) return false;
  if (UAT[K(u.ox, u.oy)]) return false;
  placeUnit(u, u.ox, u.oy); u.mp = u.omp; u.zin = (u.ozin === undefined ? -1 : u.ozin); u.moved = false; u.ox = -1;
  return true;
}
function unitWait(u) { u.done = true; u.ox = -1; return { ok: true }; }

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
  var full = uMaxMp(u), left = u.done ? 0 : u.mp, turns = 1, z = ZONE[K(u.c, u.r)], halt = false;
  for (var i = 0; i < path.length; i++) {
    var c = path[i] % W, mc = moveCost(u, c, (path[i] - c) / W);
    if (halt || mc > left) { turns++; left = full; halt = false; }
    left -= mc;
    if (ZONE[path[i]] !== z) { z = ZONE[path[i]]; halt = true; }       // 성역의 경계를 넘으면 그 턴은 거기까지
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
function dmgUU(a, d, mult, ranged) {
  var x = 620 * Math.pow(uAtk(a) / Math.max(10, uDef(d)), 0.9) * troopFactor(a.troops) * mult;
  var c = (COMPAT[a.type] && COMPAT[a.type][d.type]) || 1;
  if (VS_TYPE[d.type] && (!ranged || d.type === 'trans' || d.type === 'ram')) c *= VS_TYPE[d.type];
  x *= c;
  var td = terr(d.c, d.r), ta = terr(a.c, a.r);
  if (td === 'f' || td === 'h') x *= 0.85; else if (td === 'w') x *= 1.2;
  if (ta === 'w') x *= 0.7;
  if (d.status === 'confuse') x *= 1.25;
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
  if (terr(a.c, a.r) === 'w') x *= 0.7;
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
function setStatus(u, st, turns) { if (!alive(u)) return; u.status = st; u.stT = turns; }
function setFire(c, r, turns) {
  var t = terr(c, r);
  if (t === 'w' || t === 's' || t === 'm' || t === 'x') return false;
  if (BAT[K(c, r)] !== undefined) return false;
  G.fires[K(c, r)] = Math.max(G.fires[K(c, r)] || 0, turns);
  return true;
}

/* 일기토: 근접전에서 낮은 확률로 벌어지는 자동 판정 */
function tryDuel(a, d, res) {
  if (!alive(a) || !alive(d) || hdist(a.c, a.r, d.c, d.r) !== 1) return;
  var la = uLeader(a), ld = uLeader(d);
  if (la.war < 75 || ld.war < 75 || !chance(7)) return;
  var win = chance(100 / (1 + Math.exp(-(la.war - ld.war) / 6)));
  var Wn = win ? a : d, Ls = win ? d : a, loss = Math.round(Ls.troops * 0.08);
  Ls.morale = Math.max(0, Ls.morale - 25); Wn.morale = Math.min(100, Wn.morale + 10);
  off(Wn.off[0]).merit += 100;
  res.duel = { a: la.n, d: ld.n, win: win, loss: loss };
  logMsg('일기토! ' + la.n + ' 대 ' + ld.n + ' — ' + (win ? la.n : ld.n) + ' 승', d.c, d.r, -1, (a.f === G.player || d.f === G.player) ? 2 : 0);
  if (hurtUnit(Ls, loss, Wn.f, Wn)) { if (Ls === a) res.selfDead = true; else res.killed = true; }
}

/* 공격 가능한 대상 (현재 위치 기준) */
function attackTargets(u) {
  var out = [], rg = uRange(u), c, r;
  for (c = Math.max(0, u.c - rg - 1); c <= Math.min(W - 1, u.c + rg + 1); c++) for (r = Math.max(0, u.r - rg); r <= Math.min(H - 1, u.r + rg); r++) {
    var d = hdist(u.c, u.r, c, r);
    if (d < 1 || d > rg) continue;
    var k = K(c, r), ou = UAT[k];
    if (ou && ou.f !== u.f) { out.push({ kind: 'unit', u: ou, c: c, r: r, d: d }); continue; }
    var bi = BAT[k];
    if (bi !== undefined) { var b = G.bases[bi]; if (b.owner >= 0 && b.owner !== u.f && u.zin !== b.id) out.push({ kind: 'base', b: b, c: c, r: r, d: d }); continue; }
    var pf = PAT[k];
    if (pf) { var pb = G.bases[pf.b], fc = pb.plots[pf.i].fac; if (fc && pb.owner >= 0 && pb.owner !== u.f && d === 1) out.push({ kind: 'fac', b: pb, i: pf.i, c: c, r: r, d: d }); }
  }
  return out;
}
function critNormal(a, d) { return (uHas(a, '비장') || uHas(a, '용장') || uHas(a, '신장')) && uWar(a) > uWar(d); }

function zoneFresh(u, b) { return !!b && u.zin !== undefined && u.zin >= 0 && u.zin === b.id; }   // 이번 턴에 이 성의 성역에 막 들어섰는가
function unitAttack0(u, t) {
  if (u.done) return ERR('이미 행동을 마쳤습니다');
  if (t.kind === 'base' && zoneFresh(u, t.b)) return ERR('성역에 막 들어선 부대는 이번 턴에 성을 칠 수 없습니다');
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
        b.owner = -1; b.troops = 0; b.dur = Math.max(b.dur, Math.round(b.maxDur * 0.3));
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
function tacticCrit(u, d) {
  if (uHas(u, '신장') && uWar(u) > uWar(d)) return 1.3;
  if (u.type === 'spear' && (uHas(u, '창장') || uHas(u, '투신'))) return 1.3;
  if (u.type === 'halberd' && (uHas(u, '극장') || uHas(u, '투신'))) return 1.3;
  if (u.type === 'bow') { if (uHas(u, '궁신')) return 1.43; if (uHas(u, '궁장')) return 1.3; }
  if (u.type === 'cav') { if (uHas(u, '기신')) return 1.43; if (uHas(u, '기장')) return 1.3; }
  return 0;
}
/* 전법의 성공·대성공 확률(%). 대성공은 성공 안에 들어 있다(성공 80·대성공 15 → 실패 20, 보통 성공 65, 대성공 15).
   - 성공: 병과 적성 + 무력
   - 대성공: 병과 적성 + 무력 + (내 무력 − 상대 통솔). 특기(창장·기장·신장…)가 맞으면 반드시 대성공 */
var TACTIC_CRIT = { C: 4, B: 8, A: 12, S: 18 };
function uLdr(u) { return bestOf(uMembers(u), 'ldr'); }
function tacticOdds(u, d) {
  var forced = tacticCrit(u, d);
  if (forced) return { ok: 100, crit: 100, mult: forced, sure: true };
  var w = uWar(u), ok = Math.round(TACTIC_RATE[uApt(u)] + clamp((w - 70) / 3, -5, 8));
  var cr = Math.round(clamp(TACTIC_CRIT[uApt(u)] + clamp((w - 70) * 0.5, -4, 15) + clamp((w - uLdr(d)) * 0.15, -6, 6), 2, 45));
  return { ok: ok, crit: Math.min(cr, ok), mult: 1.3, sure: false };
}
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
  var pf = PAT[k]; if (pf && G.bases[pf.b].plots[pf.i].fac) return false;
  return true;
}
function behindHex(u, d) {
  var dist = hdist(u.c, u.r, d.c, d.r), dx = cubeX(d.c, d.r) - cubeX(u.c, u.r), dz = d.r - u.r;
  if (dist === 1) return stepDir(d.c, d.r, dx, dz);
  if (dx % 2 === 0 && dz % 2 === 0) return stepDir(d.c, d.r, dx / 2, dz / 2);
  var ns = nbrs(d.c, d.r), best = null, bd = 0;
  for (var i = 0; i < ns.length; i++) { var q = hdist(u.c, u.r, ns[i][0], ns[i][1]); if (q > bd) { bd = q; best = ns[i]; } }
  return best;
}
function unitTactic0(u, tac, t) {
  if (u.done) return ERR('이미 행동을 마쳤습니다');
  if (u.morale < tac.cost) return ERR('기력이 부족합니다');
  var d = t.u, ranged = hdist(u.c, u.r, d.c, d.r) > 1;
  var res = { ok: true, kind: 'tactic', tac: tac.name, c: d.c, r: d.r, ac: u.c, ar: u.r, tname: uName(d), extra: [] };
  u.done = true; u.ox = -1; u.morale -= tac.cost;
  var od = tacticOdds(u, d), roll = od.sure ? 0 : rnd() * 100;
  res.pOk = od.ok; res.pCrit = od.crit;
  if (roll >= od.ok) {
    res.fail = true;
    var fdm = defMods(d, dmgUU(u, d, 0.6, ranged), 'normal');
    res.dmg = fdm; res.killed = hurtUnit(d, fdm, u.f, u);
    if (!res.killed && !ranged && d.status !== 'confuse') { var fc = defMods(u, dmgUU(d, u, 0.4, false), 'normal'); res.counter = fc; if (hurtUnit(u, fc, d.f, d)) res.selfDead = true; }
    return res;
  }
  var crit = roll < od.crit ? od.mult : 0, e = tacticEff(tac, !!crit);      // e = 이번에 적용되는 효과(대성공이면 강화된 것)
  res.crit = !!crit;
  var cm = crit || 1;
  var dmg = defMods(d, dmgUU(u, d, tac.mult * cm, ranged), 'tactic');
  var oc = d.c, or_ = d.r, dx = cubeX(d.c, d.r) - cubeX(u.c, u.r), dz = d.r - u.r;
  // 부가 대상(먼저 목록을 잡아 둔다)
  var others = [], i, ns, q;
  if (tac.arc) { ns = nbrs(u.c, u.r); for (i = 0; i < ns.length; i++) { q = UAT[K(ns[i][0], ns[i][1])]; if (q && q.f !== u.f && q !== d && hdist(q.c, q.r, d.c, d.r) === 1) others.push([q, e.side || 0.8]); } }
  if (tac.all) { ns = nbrs(u.c, u.r); for (i = 0; i < ns.length; i++) { q = UAT[K(ns[i][0], ns[i][1])]; if (q && q.f !== u.f && q !== d) others.push([q, 1.0]); } }
  if (tac.pierce) { var bh = behindHex(u, d); if (bh && inMap(bh[0], bh[1])) { q = UAT[K(bh[0], bh[1])]; if (q && q.f !== u.f) others.push([q, e.side || 0.8]); } }
  if (tac.splash) { ns = nbrs(d.c, d.r); for (i = 0; i < ns.length; i++) { q = UAT[K(ns[i][0], ns[i][1])]; if (q && q.f !== u.f && q !== d) others.push([q, e.side || 0.6]); } }
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
    if (cp) { res.pConf = cp; if (cp >= 100 || chance(cp)) { setStatus(d, 'confuse', 1); res.confused = true; } }
  }
  if (tac.fire) { if (setFire(oc, or_, e.fireT || 2)) res.fire = true; }
  if (tac.pass && !ranged) {
    var bx = stepDir(oc, or_, dx, dz);
    if (canPushInto(bx[0], bx[1], u) && moveCost(u, bx[0], bx[1]) < 99) { placeUnit(u, bx[0], bx[1]); res.passed = true; }
  }
  for (i = 0; i < others.length; i++) {
    var o2 = others[i][0];
    if (!alive(o2) || !alive(u)) continue;
    var od = defMods(o2, dmgUU(u, o2, tac.mult * cm * others[i][1], hdist(u.c, u.r, o2.c, o2.r) > 1), 'tactic');
    var ex = { c: o2.c, r: o2.r, dmg: od };
    res.extra.push(ex);
    var dead2 = hurtUnit(o2, od, u.f, u); afterHit(u, o2, od);
    if (!dead2 && e.moraleAll) { var m2 = Math.min(o2.morale, e.moraleAll); o2.morale -= m2; if (m2) ex.mor = m2; }
  }
  res.uc = u.c; res.ur = u.r;
  if (!dead && !tac.noCounter && !ranged && alive(u) && d.status !== 'confuse' && d.status !== 'rumor' && hdist(u.c, u.r, d.c, d.r) === 1) {
    var cd = defMods(u, dmgUU(d, u, 0.25, false), 'normal');
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
      if (ou && ou.f === u.f) continue;
      var pf = PAT[k], enemyFac = pf && G.bases[pf.b].plots[pf.i].fac && G.bases[pf.b].owner !== u.f;
      if (!ou && !enemyFac) continue;
      out.push({ c: c, r: r, u: ou || null });
    } else if (ou && ou.f !== u.f && !ou.status) out.push({ c: c, r: r, u: ou });
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
  } else if (tu && alive(tu)) setStatus(tu, ploy.id, 2 + ext);
}
function unitPloy0(u, ploy, t) {
  if (u.done) return ERR('이미 행동을 마쳤습니다');
  if (u.morale < ploy.cost) return ERR('기력이 부족합니다');
  u.done = true; u.ox = -1; u.morale -= ploy.cost;
  var res = { ok: true, kind: 'ploy', ploy: ploy.name, c: t.c, r: t.r, ac: u.c, ar: u.r };
  if (ploy.id === 'douse') { delete G.fires[K(u.c, u.r)]; nbrs(u.c, u.r).forEach(function (n) { delete G.fires[K(n[0], n[1])]; }); res.success = true; return res; }
  var tu = t.u || null, p = ployChance(u, ploy, tu);
  res.p = p;
  if (chance(p)) {
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
      else if (!uHas(u, '통찰') && !uHas(u, '명경')) setStatus(u, ploy.id, 2);
    }
  }
  return res;
}

/* ---------- 저장 ---------- */
/* 행동 + 연출용 사건 기록. tf = 맞은 쪽 세력(행동 전 기준) */
function actTargetF(t) { return t && t.u ? t.u.f : (t && t.b ? t.b.owner : -1); }
function actEv(u, t, res, f, name, ac, ar, tf) {
  if (res && res.ok) {
    // 화면 연출에 쓰는 정보: 공격한 부대·맞은 부대의 번호와 병과, 행동 뒤의 자리
    res.aid = u.id; res.atype = u.type; res.af = f; res.ac0 = ac; res.ar0 = ar;
    res.ac1 = u.c; res.ar1 = u.r; res.aAlive = !!UMAP[u.id];
    res.tk = t ? t.kind : ''; res.tid = t && t.u ? t.u.id : -1; res.tbase = t && t.b ? t.b.id : -1; res.tf = tf;
    if (t && t.u) { res.tc1 = t.u.c; res.tr1 = t.u.r; res.tAlive = !!UMAP[t.u.id]; res.ttype = t.u.type; }
    ev({ t: 'act', f: f, name: name, ac: ac, ar: ar, tc: t && t.c, tr: t && t.r, tf: tf, res: res });
  }
  return res;
}
function unitAttack(u, t) { var f = u.f, n = uName(u), ac = u.c, ar = u.r, tf = actTargetF(t); return actEv(u, t, unitAttack0(u, t), f, n, ac, ar, tf); }
function unitTactic(u, tac, t) { var f = u.f, n = uName(u), ac = u.c, ar = u.r, tf = actTargetF(t); return actEv(u, t, unitTactic0(u, tac, t), f, n, ac, ar, tf); }
function unitPloy(u, ploy, t) { var f = u.f, n = uName(u), ac = u.c, ar = u.r, tf = actTargetF(t); return actEv(u, t, unitPloy0(u, ploy, t), f, n, ac, ar, tf); }

function serialize() { return JSON.stringify(G); }
function deserialize(s) {
  var g = JSON.parse(s);
  if (!g || g.ver !== 2) return false;
  // 초상은 저장본이 아니라 지금 판의 명부를 따른다(예전 저장을 열어도 새로 그린 초상이 나오게)
  for (var i = 0; i < g.officers.length; i++) { var so = SCENARIO.officers[i]; if (so && so.n === g.officers[i].n) g.officers[i].por = so.por; }
  // 세력 색도 지금 판의 색(석채 빛)을 따른다
  for (var j = 0; j < g.factions.length; j++) { var sf = SCENARIO.factions[j]; if (sf && sf.n === g.factions[j].name) g.factions[j].color = sf.color; }
  G = g; reindex(); REPORT = []; EVQ = [];
  return true;
}
