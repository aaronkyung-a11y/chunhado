// v0.21 — 규칙 시험: 관문의 능선 · 충성 100 · 등용 · 성의 내구 · 수송을 마친 뒤.   OLD=build/logs/v021/src020 node tests/v21.js
//   ① 능선(MAPDATA.walls): 변마다 양쪽에서 이웃이 아니다 · 거점 칸에는 닿지 않는다 · 길의 그래프(허창 — 호로관, 동관 — 무관, 양평관 — 검각).
//   ② 관문마다: 관문에서 16칸 안에서는 관문을 지나지 않고 건너편으로 갈 수 없다. 보병의 이동력으로 관문 길과 돌아가는 길을 잰다.
//   ③ 내 관문은 지나가고(관문 칸에 서지 않는다) 남의 관문은 못 지난다 · 능선 너머 옆 칸은 칠 수 없다.
//   ④ 0.20 의 규칙으로 만든 저장: 그대로 열리고(부대의 자리 · 거점), AI 끼리 더 돌려도 탈이 없다.
//   ⑤ 충성 100 은 누가 권해도 응하지 않는다 · 재야 · 포로도 한 달에 한 번 · 등용의 값(RECRUIT · POACH).
//   ⑥ 성의 내구: 맞은 뒤 DUR_HEAL.wait 턴은 멈추고, 그 뒤 턴마다 최대의 DUR_HEAL.pct %.
//   ⑦ 수송을 마친 뒤: 내 수송대가 걸어서 우리 거점에 들어가면 물을 것이 쌓이고(G.tdone), 답에 따라 머물거나 돌아간다. 일기토의 G.asks 와 섞이지 않는다.
const fs = require('fs'), vm = require('vm'), path = require('path');
function load(root) {
  const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array };
  vm.createContext(ctx);
  for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
  return ctx;
}
function run(ctx, code) { return JSON.parse(vm.runInContext('JSON.stringify((function () {' + code + '})())', ctx)); }
const NEW = load(process.env.SRC || path.join(__dirname, '..', 'src'));
const OLD = load(process.env.OLD || path.join(__dirname, '..', 'build', 'logs', 'v021', 'src020'));
let pass = 0, fail = 0;
function ok(c, msg) { if (c) pass++; else { fail++; console.log('  ✗ ' + msg); } }

/* ① 능선 */
const w1 = run(NEW, `newGame(0, 7); var ws = MAPDATA.walls || [], bad = 0, onBase = 0, far = 0, nb = 0;
  ws.forEach(function (w) { var a = K(w[0], w[1]), b = K(w[2], w[3]);
    if (!walled(a, b) || !walled(b, a)) bad++;
    if (hdist(w[0], w[1], w[2], w[3]) !== 1) far++;
    if (BAT[a] !== undefined || BAT[b] !== undefined) onBase++;
    if (nbrs(w[0], w[1]).some(function (n) { return n[0] === w[2] && n[1] === w[3]; }) || nbrs(w[2], w[3]).some(function (n) { return n[0] === w[0] && n[1] === w[1]; })) nb++;
  });
  function adj(n) { return ADJ[baseByName(n)].map(function (e) { return G.bases[e.to].n + ' ' + e.len; }).sort(); }
  return { ver: GAME_VERSION, n: ws.length, bad: bad, far: far, onBase: onBase, nb: nb, edges: MAPDATA.edges.length, hl: adj('호로관'), dg: adj('동관'), yp: adj('양평관'), ly: adj('낙양'), hc: adj('허창'), mg: adj('무관'), gg: adj('검각'), hz: adj('한중'), ca: adj('장안') };`);
const w0 = run(OLD, `newGame(0, 7); return { walls: (MAPDATA.walls || []).length, edges: MAPDATA.edges.length, bases: MAPDATA.bases.length, t: MAPDATA.t.length };`);
console.log('① 능선', JSON.stringify(w1));
ok(/^v0\.(2[1-9]|[3-9]\d)/.test(w1.ver), '판 번호가 v0.21 이후 [' + w1.ver + ']');
ok(w0.walls === 0 && w1.n === 143 && w1.bad === 0 && w1.far === 0 && w1.nb === 0, '능선의 변 143곳: 서로 이웃한 두 칸 사이이고 양쪽에서 이웃이 아니다');
ok(w1.onBase === 0, '거점 칸에 닿은 능선은 없다(성 둘레의 여섯 칸은 늘 드나든다)');
ok(w1.edges === 76 && w0.edges === 76, '길의 수는 76 그대로');
ok(w1.hl.join() === '낙양 7,진류 12,허창 12' && w1.ly.indexOf('허창 18') < 0 && w1.hc.indexOf('호로관 12') >= 0, '허창 — 낙양 길은 호로관을 지난다: ' + w1.hl.join(' · '));
ok(w1.dg.join() === '무관 13,장안 17,홍농 10' && w1.ca.indexOf('무관 29') < 0 && w1.mg.join() === '동관 13,완 21', '장안 — 무관 길은 동관을 지난다: ' + w1.dg.join(' · '));
ok(w1.yp.join() === '검각 14,천수 17,한중 7' && w1.hz.indexOf('검각 22') < 0 && w1.gg.join() === '양평관 14,자동 8', '한중 — 검각 길은 양평관을 지난다: ' + w1.yp.join(' · '));
const same = run(NEW, `return { t: MAPDATA.t, road: MAPDATA.road, bases: MAPDATA.bases.map(function (b) { return [b.n, b.k, b.c, b.r, b.sz]; }), plots: MAPDATA.plots };`);
const sameO = run(OLD, `return { t: MAPDATA.t, road: MAPDATA.road, bases: MAPDATA.bases.map(function (b) { return [b.n, b.k, b.c, b.r, b.sz]; }), plots: MAPDATA.plots };`);
ok(JSON.stringify(same) === JSON.stringify(sameO), '땅 · 길의 칸 · 거점 · 부지는 0.20 과 같다(칸은 바꾸지 않았다)');

/* ② 관문마다 */
const g2 = run(NEW, `newGame(0, 7);
  var FOOT = { p: 3, f: 5, h: 5, d: 4 };
  function step(k) { var t = MAPDATA.t.charAt(k), rd = MAPDATA.road.charAt(k) === '1'; return t === 'w' ? (rd ? 4 : 8) : (rd ? 2 : FOOT[t]); }
  function walk(a, b, open) {                                  // 보병의 이동력으로 가장 싼 길(거점 칸은 끝점과 열린 관문만)
    var dist = {}, h = new Heap(); dist[a] = 0; h.push(0, a);
    while (h.a.length) { var top = h.pop(), d = top[0], k = top[1]; if (k === b) return d; if (d > dist[k]) continue;
      var c = k % W, r = (k - c) / W, ns = nbrs(c, r);
      for (var i = 0; i < ns.length; i++) { var nk = K(ns[i][0], ns[i][1]), t = MAPDATA.t.charAt(nk), cost;
        if (BAT[nk] !== undefined) { if (nk !== b && !(open && G.bases[BAT[nk]].kind === 'gate')) continue; cost = 2; }
        else if (t === 'm' || t === 's' || t === 'x') continue; else cost = step(nk);
        if (dist[nk] === undefined || d + cost < dist[nk]) { dist[nk] = d + cost; h.push(d + cost, nk); } } }
    return null;
  }
  var out = [];
  G.bases.forEach(function (g) { if (g.kind !== 'gate') return;
    var ns = nbrs(g.c, g.r).filter(function (n) { var t = terr(n[0], n[1]); return t !== 'm' && t !== 's' && t !== 'x' && BAT[K(n[0], n[1])] === undefined; });
    // 둘레의 칸을 편으로 가른다: 관문을 지나지 않고 16칸 안에서 서로 닿는 것끼리
    var side = {}, nside = 0;
    ns.forEach(function (s0) { var k0 = K(s0[0], s0[1]); if (side[k0] !== undefined) return; var id = nside++, q = [s0], seen = {}; seen[k0] = 1;
      while (q.length) { var p = q.shift(), kk = K(p[0], p[1]); if (side[kk] === undefined && ns.some(function (n) { return K(n[0], n[1]) === kk; })) side[kk] = id;
        nbrs(p[0], p[1]).forEach(function (n) { var nk = K(n[0], n[1]), t = terr(n[0], n[1]); if (seen[nk] || BAT[nk] !== undefined || t === 'm' || t === 's' || t === 'x' || hdist(n[0], n[1], g.c, g.r) > 16) return; seen[nk] = 1; q.push(n); }); } });
    var ends = ADJ[g.id].map(function (e) { return G.bases[e.to]; }), a = ends[0], b = ends[1];
    // 양 끝의 두 거점: 서로 다른 편에 있는 둘을 고른다(길이 셋인 관문은 처음 둘이 같은 편일 수 있다)
    var pairs = [];
    for (var i = 0; i < ends.length; i++) for (var j = i + 1; j < ends.length; j++) { var thru = walk(K(ends[i].c, ends[i].r), K(ends[j].c, ends[j].r), true), around = walk(K(ends[i].c, ends[i].r), K(ends[j].c, ends[j].r), false); pairs.push([ends[i].n, ends[j].n, thru, around]); }
    out.push({ n: g.n, ns: ns.length, sides: nside, pairs: pairs });
  });
  return out;`);
g2.forEach(x => console.log('② ' + x.n + ' 둘레 ' + x.ns + '칸 · ' + x.sides + '편 | ' + x.pairs.map(p => p[0] + '–' + p[1] + ' 관문 길 ' + p[2] + ' / 돌아가는 길 ' + p[3]).join(' · ')));
ok(g2.length === 7 && g2.every(x => x.sides >= 2), '일곱 관문 모두: 둘레의 칸이 관문을 지나야만 닿는 두 편 이상으로 갈린다(16칸 안) ' + g2.map(x => x.n + ':' + x.sides).join(' '));
const pr = {}; g2.forEach(x => x.pairs.forEach(p => { pr[p[0] + '–' + p[1]] = [p[2], p[3]]; }));
function ratio(k) { const p = pr[k] || pr[k.split('–').reverse().join('–')]; return p ? (p[1] === null ? 99 : p[1] / p[0]) : -1; }
ok(ratio('진류–낙양') >= 1.8 && ratio('낙양–홍농') >= 3 && ratio('장안–홍농') >= 2 && ratio('천수–한중') >= 2 && ratio('진양–업') >= 1.7, '돌아가는 길이 관문 길보다 훨씬 멀다(보병의 이동력): 호로관 ×' + ratio('진류–낙양').toFixed(2) + ' · 함곡관 ×' + ratio('낙양–홍농').toFixed(2) + ' · 동관 ×' + ratio('장안–홍농').toFixed(2) + ' · 양평관 ×' + ratio('천수–한중').toFixed(2) + ' · 호관 ×' + ratio('진양–업').toFixed(2));

/* ③ 지나가기 · 막히기 */
const t3 = run(NEW, `newGame(15, 3); var g = G.bases[baseByName('함곡관')], ly = G.bases[baseByName('낙양')], hn = G.bases[baseByName('홍농')];
  function mk(b, type) { var o = baseOfficers(b).filter(function (x) { return x.unit === null; })[0]; b.troops = Math.max(b.troops, 20000); b.w.spear = b.w.horse = b.w.bow = 30000; G.factions[b.owner].ap = 999; o.acted = false;
    var r = cmdDeploy(b, { type: type, ids: [o.id], troops: 3000, food: 0 }); if (!r.ok) throw new Error(r.msg); r.unit.born = -5; return r.unit; }
  var ns = nbrs(g.c, g.r).filter(function (n) { var t = terr(n[0], n[1]); return t !== 'm' && t !== 's' && t !== 'x'; });
  var A = ns[0], B = ns[1], res = { ns: ns.length, adj: hdist(A[0], A[1], B[0], B[1]), wall: walled(K(A[0], A[1]), K(B[0], B[1])) };
  var u1 = mk(hn, 'spear'); placeUnit(u1, B[0], B[1]); u1.mp = uMaxMp(u1); u1.done = false;
  var rc1 = unitReach(u1); res.ownReach = !!rc1.stop[K(A[0], A[1])]; res.ownGateStop = !!rc1.stop[K(g.c, g.r)];
  var p1 = longPath(u1, function (k) { return k === K(ly.c, ly.r); }, 3000, [ly.c, ly.r, 0]); res.ownVia = p1 ? p1.indexOf(K(g.c, g.r)) : -9; res.ownLen = p1 ? p1.length : null;
  var gt = g.troops; u1.dest = K(A[0] + 2, A[1]); var m = unitMarch(u1); res.march = { ok: !!(m && m.ok), alive: !!UMAP[u1.id], gate: g.troops === gt, side: UMAP[u1.id] ? hdist(u1.c, u1.r, A[0], A[1]) <= 3 : false };
  var fb = G.bases.filter(function (b) { return b.owner >= 0 && b.owner !== 15 && baseOfficers(b).length > 1; })[0];
  var u2 = mk(fb, 'spear'); placeUnit(u2, A[0], A[1]); u2.mp = uMaxMp(u2); u2.done = false; if (UMAP[u1.id]) placeUnit(u1, B[0], B[1]);
  var rc2 = unitReach(u2); res.foeReach = !!rc2.stop[K(B[0], B[1])]; res.foeGate = rc2.cost[K(g.c, g.r)] !== undefined;
  var p2 = longPath(u2, function (k) { return k === K(B[0] - 1, B[1]); }, 3000, [B[0] - 1, B[1], 0]); res.foeLen = p2 ? p2.length : null;
  res.foeAtk = attackTargets(u2).map(function (t) { return t.kind + (t.b ? t.b.n : ''); }).sort();
  var u3 = mk(fb, 'bow'); placeUnit(u3, A[0] + 1, A[1]); res.bowAtk = attackTargets(u3).map(function (t) { return t.kind; }).sort(); res.bowD = hdist(u3.c, u3.r, B[0], B[1]);
  g.owner = -1; g.troops = 0; var rc3 = unitReach(u2); res.emptyStop = !!rc3.stop[K(g.c, g.r)]; res.emptyPass = !!rc3.stop[K(B[0] - 1, B[1])];
  return res;`);
console.log('③ 함곡관', JSON.stringify(t3));
ok(t3.ns === 2 && t3.adj === 1 && t3.wall, '함곡관 둘레의 갈 수 있는 두 칸(낙양 쪽 · 홍농 쪽)은 붙어 있지만 그 사이에 능선이 있다');
ok(t3.ownReach && t3.ownGateStop && t3.ownVia >= 0, '주인의 부대: 관문을 지나 건너편에 닿는다 · 관문에 들어갈 수도 있다 · 낙양까지의 길(' + t3.ownLen + '걸음)이 관문 칸을 지난다');
ok(t3.march.ok && t3.march.alive && t3.march.gate && t3.march.side, '행군: 관문 칸에 서지 않고(입성하지 않고) 건너편으로 나아간다');
ok(!t3.foeReach && !t3.foeGate && (t3.foeLen === null || t3.foeLen > 40), '남의 부대: 건너편에 닿지 못한다 · 관문 칸으로 들어가지 못한다 · 돌아가는 길 ' + t3.foeLen + '걸음');
ok(t3.foeAtk.join() === 'base함곡관', '능선 너머 옆 칸의 부대는 칠 수 없다 — 칠 수 있는 것은 관문뿐: ' + t3.foeAtk.join());
ok(t3.bowD === 2 && t3.bowAtk.indexOf('unit') >= 0, '노병은 두 칸 거리에서 능선 너머를 쏜다');
ok(t3.emptyStop && !t3.emptyPass, '주인 없는 관문: 들어가면 차지한다 — 지나가지는 못한다');

/* ④ 0.20 의 저장 */
const saves = run(OLD, `var out = [];
  newGame(0, 21); out.push(serialize());
  newGame(2, 5); G.aiOnly = true; for (var t = 0; t < 30 && !G.over; t++) endTurn(); G.aiOnly = false; out.push(serialize());
  newGame(15, 9); G.aiOnly = true; for (var t2 = 0; t2 < 60 && !G.over; t2++) endTurn(); G.aiOnly = false; out.push(serialize());
  return out;`);
NEW.__SAVES = saves;
const mg = run(NEW, `var S = __SAVES, out = [];
  for (var i = 0; i < S.length; i++) {
    var raw = JSON.parse(S[i]), okk = deserialize(S[i]), x = { ok: !!okk, n: G.bases.length };
    x.same = G.bases.every(function (g, k) { var r = raw.bases[k]; return g.n === r.n && g.owner === r.owner && g.troops === r.troops && g.dur === r.dur; });
    x.units = G.units.length === raw.units.length && G.units.every(function (u, k) { return u.c === raw.units[k].c && u.r === raw.units[k].r; });
    x.nu = G.units.length; var s1 = serialize(); deserialize(s1); x.stable = serialize() === s1;
    var err = ''; G.aiOnly = true; try { for (var t = 0; t < 30 && !G.over; t++) endTurn(); } catch (e) { err = String(e && e.stack || e).slice(0, 300); } x.err = err; x.turn = G.turn;
    x.onBase = G.units.filter(function (u) { return BAT[K(u.c, u.r)] !== undefined; }).length;
    out.push(x);
  }
  return out;`);
mg.forEach((x, i) => console.log('④ 0.20 의 저장 ' + (i + 1), JSON.stringify(x)));
ok(mg.length === 3 && mg.every(x => x.ok && x.n === 50 && x.same && x.units && x.stable), '세 판 모두 그대로 열린다(거점 · 부대의 자리) · 저장 → 열기가 같다');
ok(mg.every(x => !x.err && x.onBase === 0), '연 판을 AI 끼리 30턴 더: 탈 없음' + mg.map(x => x.err).join(''));

/* ⑤ 충성 100 · 등용 */
const r5 = run(NEW, `newGame(0, 7); var b = G.bases[baseByName('진류')], out = { K: [RECRUIT.base, RECRUIT.cha, RECRUIT.max, RECRUIT.cap, POACH.base, POACH.loyK, POACH.max] };
  var me = baseOfficers(b).filter(function (o) { return !isLord(o); })[0];
  // 이웃한 다른 세력의 무장 하나: 인연을 억지로 붙여도 충성 100 이면 0
  var nb = null; ADJ[b.id].forEach(function (e) { var x = G.bases[e.to]; if (!nb && x.owner >= 0 && x.owner !== b.owner && baseOfficers(x).filter(function (o) { return !isLord(o) && !bondOf(o); }).length) nb = x; });
  if (!nb) { nb = G.bases[ADJ[b.id][0].to]; }
  var t = baseOfficers(nb).filter(function (o) { return !isLord(o) && !bondOf(o); })[0];
  out.t = t ? t.n : null;
  if (t) { t.loy = 60; var q60 = recruitTerms(b, me, t); t.loy = 99; var q99 = recruitTerms(b, me, t); t.loy = 100; var q100 = recruitTerms(b, me, t); out.q = [q60.p, q99.p, q99.no || '', q100.p, q100.no || '']; out.risk = poachRisk(t) ? poachRisk(t).p : 0; }
  // 재야: 한 달에 한 번 · 주사위는 달마다
  var fr = G.officers.filter(function (o) { if (o.st !== 'hidden' || bondWith(o, b.owner)) return false; o.st = 'free'; var l0 = o.loc; o.loc = b.id; var no = recruitRoll(o) >= recruitChance(b, me, o); o.st = 'hidden'; o.loc = l0; return no; })[0]; fr.st = 'free'; fr.loc = b.id; G.factions[b.owner].ap = 999;      // 이번 달에 거절할 사람
  var roll0 = recruitRoll(fr), p0 = recruitChance(b, me, fr); var r1 = cmdRecruit(b, me.id, fr.id); out.free = { p: p0, ok: r1.ok, joined: r1.joined, wait: askWait(fr), xun: G.xun };
  if (!r1.joined) { var me2 = baseOfficers(b).filter(function (o) { return !isLord(o) && !o.acted; })[0]; var r2 = cmdRecruit(b, me2.id, fr.id); out.again = r2.ok ? 'ok' : r2.msg; G.turn++; G.xun = 1; out.rollSame = recruitRoll(fr) === roll0; out.wait1 = askWait(fr); G.turn += 2; G.xun = 0; G.month++; out.rollNext = recruitRoll(fr) !== roll0; out.wait2 = askWait(fr); }
  return out;`);
console.log('⑤ 등용', JSON.stringify(r5));
ok(r5.K.join() === '24,0.6,88,6,11,2.8,75', '등용의 값: 재야 바탕 24 · 매력 0.6 · 위 끝 88 · 포로 −6 / 다른 세력 바탕 11 · 충성 −2.8 · 위 끝 75 [' + r5.K.join() + ']');
ok(r5.q && r5.q[3] === 0 && r5.q[4] === '충성 100' && r5.risk === 0, '충성 100 인 무장은 응하지 않는다(까닭: 충성 100) — 떠날 수 있는 무장으로 꼽히지 않는다');
ok(r5.q && r5.q[0] >= r5.q[1], '충성이 낮을수록 가능성이 높다(60: ' + (r5.q || [])[0] + ' · 99: ' + (r5.q || [])[1] + ')');
ok(r5.free.ok && !r5.free.joined && r5.free.wait === 3 && /이번 달/.test(r5.again) && r5.rollSame && r5.wait1 === 2 && r5.rollNext && r5.wait2 === 0, '재야: 거절하면 그 달에는 다시 권할 수 없고(주사위도 같다) 다음 달 상순에 풀린다 ' + JSON.stringify(r5.free));

/* ⑥ 성의 내구 */
const d6 = run(NEW, `newGame(0, 7); G.aiOnly = true; var b = G.bases[baseByName('진류')], out = { K: [DUR_HEAL.wait, DUR_HEAL.pct], max: b.maxDur };
  b.dur = 1000; b.hitT = G.turn; var seq = [];
  for (var t = 0; t < 5; t++) { var before = b.dur, nx = durHealAt(b, G.turn + 1); endTurn(); seq.push([G.turn - b.hitT, b.dur - before, nx]); }
  out.seq = seq; b.dur = b.maxDur - 10; delete b.hitT; endTurn(); out.cap = b.dur === b.maxDur;
  var g = G.bases.filter(function (x) { return x.kind === 'gate' && x.owner >= 0; })[0]; g.dur = 500; delete g.hitT; var gd = g.dur; endTurn(); out.gate = [g.maxDur, g.dur - gd];
  var e = G.bases.filter(function (x) { return x.owner < 0; })[0]; if (e) { e.dur = 100; endTurn(); out.empty = e.owner < 0 ? e.dur : 'taken'; }
  return out;`);
console.log('⑥ 내구', JSON.stringify(d6));
const per = Math.round(d6.max * d6.K[1] / 100);
ok(d6.K.join() === '2,4' && d6.seq[0][1] === 0 && d6.seq[0][2] === 0 && d6.seq[1][1] === per && d6.seq[1][2] === per && d6.seq[2][1] === per, '맞은 다음 턴은 멈추고, 그다음 턴부터 턴마다 최대의 4%(' + per + ')씩 돌아온다 — 화면에 적는 값(durHealAt)과 같다');
ok(d6.cap && d6.gate[1] === Math.round(d6.gate[0] * 0.04), '최대를 넘지 않는다 · 관문도 같다(+' + d6.gate[1] + ')');
ok(d6.empty === undefined || d6.empty === 100 || d6.empty === 'taken', '주인 없는 성은 돌아오지 않는다');

/* ⑦ 수송을 마친 뒤 */
const t7 = run(NEW, `newGame(15, 3); var b = G.bases[baseByName('장안')], d = G.bases[baseByName('동관')], out = {};
  var o = baseOfficers(b).filter(function (x) { return !isLord(x); })[0];
  var p = transPlan(b, o.id, K(d.c, d.r), true), p1 = transPlan(b, o.id, K(d.c, d.r), false); out.plan = [p.turns, p1.turns, p.turns <= p1.turns, deploySpots(b).some(function (s) { return s[0] === p.spot[0] && s[1] === p.spot[1]; })];
  var r = cmdDeploy(b, { type: 'trans', ids: [o.id], troops: 1000, food: 3000, at: p.spot }), u = r.unit, food0 = d.food, steps = 0;
  out.back = u.back === undefined; u.dest = K(d.c, d.r);
  G.asks = [{ a: 1, d: 2, turn: G.turn }];                                    // 일기토의 물음과 섞이지 않는다
  while (UMAP[u.id] && steps < 8) { var m = unitMarch(u); steps++; if (m && m.entered !== undefined) out.res = [m.entered === d.id, m.ask === true, m.back === undefined]; else { u.done = false; u.mp = uMaxMp(u); G.turn++; } }
  out.steps = steps; out.in = [d.food - food0, o.loc === d.id, o.st, o.unit === null]; out.q = (G.tdone || []).length; out.asks = G.asks.length;
  var v = transAskInfo(G.tdone[0]); out.info = v ? [v.b.n, v.home.n, v.os.length, v.turns] : null;
  var s = serialize(); deserialize(s); out.saved = (G.tdone || []).length;
  var a1 = cmdTransAsk(true), o2 = off(o.id); out.go = [a1.ok, a1.back ? a1.back.to : -1, o2.st, o2.dest, o2.eta, (G.tdone || []).length];
  // 머문다
  newGame(15, 3); b = G.bases[baseByName('장안')]; d = G.bases[baseByName('동관')]; o = baseOfficers(b).filter(function (x) { return !isLord(x); })[0];
  r = cmdDeploy(b, { type: 'trans', ids: [o.id], troops: 1000, food: 3000 }); u = r.unit; u.dest = K(d.c, d.r); steps = 0;
  while (UMAP[u.id] && steps < 8) { var m2 = unitMarch(u); steps++; if (!(m2 && m2.entered !== undefined)) { u.done = false; u.mp = uMaxMp(u); G.turn++; } }
  var a2 = cmdTransAsk(false); out.stay = [a2.ok, a2.stay === d.id, off(o.id).st, off(o.id).loc === d.id, (G.tdone || []).length, cmdTransAsk(true).ok];
  // 떠나온 곳으로 돌아오면 묻지 않는다 · AI 의 수송대는 묻지 않는다 · 답하지 않고 두 턴이 지나면 버린다
  r = cmdDeploy(b, { type: 'trans', ids: [baseOfficers(b).filter(function (x) { return !isLord(x) && !x.acted; })[0].id], troops: 500, food: 1000 }); u = r.unit;
  var rc = unitReach(u), mv = unitMove(u, b.c, b.r, rc); out.home = [mv.ok, mv.entered === b.id, mv.ask === undefined, (G.tdone || []).length];
  G.tdone = [{ k: 'trans', b: d.id, home: b.id, offs: [o.id], turn: G.turn - 3 }]; var fake = { f: 15, type: 'trans', home: b.id, off: [o.id] }; transAskPush(fake, d); out.old = G.tdone.length;
  G.aiOnly = true; out.ai = transAskPush(fake, d); G.aiOnly = false; fake.corps = 1; out.corps = transAskPush(fake, d);
  return out;`);
console.log('⑦ 수송', JSON.stringify(t7));
ok(t7.plan[2] && t7.plan[3] && t7.back, '갈 곳을 고르면 가장 빨리 닿는 쪽으로 나간다(' + t7.plan[0] + '턴) · 새 수송대에는 "돌아온다"가 붙지 않는다');
ok(t7.res && t7.res.every(Boolean) && t7.in[0] > 0 && t7.in[1] && t7.in[2] === 'active' && t7.q === 1 && t7.asks === 1, '동관에 들어가면: 짐이 들어가고 무장은 일단 그곳에 있다 · 물을 것 1건(일기토의 물음은 그대로)');
ok(t7.info && t7.info.join() === '동관,장안,1,' + t7.info[3] && t7.saved === 1, '물을 것: 동관 → 장안 · 무장 1명 · ' + (t7.info || [])[3] + '턴 — 저장에도 남는다');
ok(t7.go[0] && t7.go[2] === 'travel' && t7.go[4] === t7.info[3] && t7.go[5] === 0, '돌아간다: 무장이 떠나온 거점으로 길을 떠난다');
ok(t7.stay.slice(0, 5).join() === 'true,true,active,true,0' && t7.stay[5] === false, '머문다: 그 거점에 남는다 · 더 물을 것이 없다');
ok(t7.home[0] && t7.home[1] && t7.home[2] && t7.home[3] === 0, '떠나온 거점으로 되돌아 들어가면 묻지 않는다');
ok(t7.old === 1 && t7.ai === false && t7.corps === false, '답하지 않은 채 두 턴이 지난 것은 버린다 · AI 끼리의 판과 군단의 수송대는 묻지 않는다');

console.log(fail ? 'FAIL ' + fail + ' / ' + (pass + fail) : 'ALL PASS ' + pass + ' / ' + pass);
process.exit(fail ? 1 : 0);
