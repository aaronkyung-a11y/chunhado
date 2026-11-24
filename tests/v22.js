// v0.22 — 규칙 시험: 부지를 피하는 능선 · 합병 · 함락 때 부서지는 시설 · 함께 맞은 부대의 번호.   OLD=build/logs/v022/src021 node tests/v22.js
//   ① 능선(MAPDATA.walls 149곳): 부지 칸에도, 성에서 2칸 안의 칸에도 닿지 않는다. 한 성의 이웃한 부지를 가르는 능선은 없다(0.21 에는 9쌍이 있었다).
//      길의 그래프와 관문마다의 '관문 길 / 돌아가는 길'은 0.21 처럼 선다.
//   ② 합병: 홍농의 (113,97) · (114,98) 농장이 합쳐진다(0.21 에서는 "인접한 같은 시설 필요"). 부지끼리의 옆은 능선과 상관없다(nbrsAll) — 조폐 · 곡창의 옆도.
//   ③ 함락: 다 지은 시설 n 곳 가운데 sackCount(n) 곳이 부서진다 — 맞붙어 빼앗든 멀리서 쏘아 무너뜨리든. 둘은 반드시 남는다. 빈 거점을 차지할 때는 부서지지 않는다.
//      어느 것이 부서지는지는 판의 난수를 쓰지 않는다(G.seed 가 그대로다).
//   ④ 전법에 함께 맞은 부대: res.extra[] 에 그 부대의 번호(id), 궤멸했으면 dead.
//   ⑤ 0.21 의 저장: 그대로 열리고, AI 끼리 더 돌려도 탈이 없다(능선이 옮겨졌어도 부대는 제자리에 있다).
const fs = require('fs'), vm = require('vm'), path = require('path');
function load(root) {
  const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array };
  vm.createContext(ctx);
  for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
  return ctx;
}
function run(ctx, code) { return JSON.parse(vm.runInContext('JSON.stringify((function () {' + code + '})())', ctx)); }
const NEW = load(process.env.SRC || path.join(__dirname, '..', 'src'));
const OLD = load(process.env.OLD || path.join(__dirname, '..', 'build', 'logs', 'v022', 'src021'));
let pass = 0, fail = 0;
function ok(c, msg) { if (c) pass++; else { fail++; console.log('  ✗ ' + msg); } }

/* ① 능선 */
const WALLS = `newGame(0, 7); var ws = MAPDATA.walls || [], bad = 0, onBase = 0, onPlot = 0, inZone = 0, cut = 0, pairs = 0;
  ws.forEach(function (w) { var a = K(w[0], w[1]), b = K(w[2], w[3]);
    if (!walled(a, b) || !walled(b, a) || hdist(w[0], w[1], w[2], w[3]) !== 1) bad++;
    if (BAT[a] !== undefined || BAT[b] !== undefined) onBase++;
    if (PAT[a] || PAT[b]) onPlot++;
    [[w[0], w[1]], [w[2], w[3]]].forEach(function (h) { if (G.bases.some(function (x) { return x.kind === 'city' && hdist(h[0], h[1], x.c, x.r) <= 2; })) inZone++; });
  });
  var D6 = [[[1, 0], [-1, 0], [0, -1], [-1, -1], [0, 1], [-1, 1]], [[1, 0], [-1, 0], [1, -1], [0, -1], [1, 1], [0, 1]]], cutAt = {};
  G.bases.forEach(function (x) { x.plots.forEach(function (p) { D6[p.r & 1].forEach(function (d) { var q = PAT[K(p.c + d[0], p.r + d[1])];
    if (q && q.b === x.id) { pairs++; if (walled(K(p.c, p.r), K(p.c + d[0], p.r + d[1]))) { cut++; cutAt[x.n] = (cutAt[x.n] || 0) + 1; } } }); }); });
  function adj(n) { return ADJ[baseByName(n)].map(function (e) { return G.bases[e.to].n + ' ' + e.len; }).sort(); }
  return { ver: GAME_VERSION, n: ws.length, bad: bad, onBase: onBase, onPlot: onPlot, inZone: inZone, pairs: pairs / 2, cut: cut / 2, cutAt: cutAt, edges: MAPDATA.edges.length, hl: adj('호로관'), dg: adj('동관'), yp: adj('양평관') };`;
const w1 = run(NEW, WALLS), w0 = run(OLD, WALLS);
console.log('① 능선 0.22', JSON.stringify(w1)); console.log('① 능선 0.21', JSON.stringify({ n: w0.n, onPlot: w0.onPlot, inZone: w0.inZone, cut: w0.cut, cutAt: w0.cutAt }));
ok(/^v0\.(2[2-9]|[3-9]\d)/.test(w1.ver), '판 번호가 v0.22 이후 [' + w1.ver + ']');
ok(w1.n === 149 && w1.bad === 0 && w1.onBase === 0, '능선의 변 149곳: 이웃한 두 칸 사이이고 양쪽에서 막혔다 · 거점 칸에 닿지 않는다');
ok(w1.onPlot === 0 && w1.inZone === 0, '부지 칸에도, 성에서 2칸 안의 칸에도 닿지 않는다 (0.21: 부지에 닿은 변 ' + w0.onPlot + ' · 성역에 닿은 칸 ' + w0.inZone + ')');
ok(w1.cut === 0 && w0.cut === 9 && w1.pairs === w0.pairs, '한 성의 이웃한 부지 ' + w1.pairs + '쌍 가운데 능선에 갈린 것이 없다 (0.21: ' + w0.cut + '쌍 — ' + Object.keys(w0.cutAt).join(' · ') + ')');
ok(w1.edges === 76 && w1.hl.join() === '낙양 7,진류 12,허창 12' && w1.dg.join() === '무관 13,장안 17,홍농 10' && w1.yp.join() === '검각 14,천수 17,한중 7', '길의 그래프는 0.21 과 같다(허창 — 호로관 · 동관 — 무관 · 양평관 — 검각)');
const same = `return { t: MAPDATA.t, road: MAPDATA.road, bases: MAPDATA.bases.map(function (b) { return [b.n, b.k, b.c, b.r, b.sz]; }), plots: MAPDATA.plots, edges: MAPDATA.edges };`;
ok(JSON.stringify(run(NEW, same)) === JSON.stringify(run(OLD, same)), '땅 · 길 · 거점 · 부지 · 길의 그래프는 0.21 과 같다(능선만 옮겼다)');
const GATES = `newGame(0, 7);
  var FOOT = { p: 3, f: 5, h: 5, d: 4 };
  function step(k) { var t = MAPDATA.t.charAt(k), rd = MAPDATA.road.charAt(k) === '1'; return t === 'w' ? (rd ? 4 : 8) : (rd ? 2 : FOOT[t]); }
  function walk(a, b, open) {
    var dist = {}, h = new Heap(); dist[a] = 0; h.push(0, a);
    while (h.a.length) { var top = h.pop(), d = top[0], k = top[1]; if (k === b) return d; if (d > dist[k]) continue;
      var c = k % W, r = (k - c) / W, ns = nbrs(c, r);
      for (var i = 0; i < ns.length; i++) { var nk = K(ns[i][0], ns[i][1]), t = MAPDATA.t.charAt(nk), cost;
        if (BAT[nk] !== undefined) { if (nk !== b && !(open && G.bases[BAT[nk]].kind === 'gate')) continue; cost = 2; }
        else if (t === 'm' || t === 's' || t === 'x') continue; else cost = step(nk);
        if (dist[nk] === undefined || d + cost < dist[nk]) { dist[nk] = d + cost; h.push(d + cost, nk); } } }
    return null;
  }
  var P = [['호관', '진양', '업'], ['호로관', '진류', '낙양'], ['호로관', '허창', '낙양'], ['함곡관', '낙양', '홍농'], ['동관', '장안', '홍농'], ['무관', '장안', '완'], ['양평관', '천수', '한중'], ['검각', '한중', '자동']];
  return P.map(function (p) { var a = G.bases[baseByName(p[1])], b = G.bases[baseByName(p[2])]; return [p[0], p[1], p[2], walk(K(a.c, a.r), K(b.c, b.r), true), walk(K(a.c, a.r), K(b.c, b.r), false)]; });`;
const g1 = run(NEW, GATES), g0 = run(OLD, GATES);
g1.forEach((x, i) => console.log('① ' + x[0] + ' · ' + x[1] + ' — ' + x[2] + ': 관문 길 ' + x[3] + ' (' + Math.round(x[3] / 12 * 10) + '일) / 돌아가는 길 ' + x[4] + ' (' + Math.round(x[4] / 12 * 10) + '일) ×' + (x[4] / x[3]).toFixed(2) + '   [0.21: ' + g0[i][3] + ' / ' + g0[i][4] + ']'));
ok(g1.every((x, i) => x[3] === g0[i][3]), '관문을 지나는 길의 길이는 0.21 과 같다');
ok(g1.every(x => x[4] === null || x[4] / x[3] >= 1.3), '돌아가는 길은 모두 관문 길의 1.3배 이상: ' + g1.map(x => x[0] + ' ×' + (x[4] / x[3]).toFixed(2)).join(' · '));

/* ② 합병 */
const MERGE = `newGame(15, 3); var hn = G.bases[baseByName('홍농')], ia = PAT[K(113, 97)].i, ib = PAT[K(114, 98)].i;
  function put(b, i, t) { b.plots[i].fac = { t: t, lv: 1, done: true, prog: 0, need: 0, rate: 0, hp: FAC_HP }; }
  hn.plots.forEach(function (p) { p.fac = null; }); put(hn, ia, 'farm'); put(hn, ib, 'farm');
  var out = { owner: hn.owner, adj: hdist(113, 97, 114, 98), ca: mergeCandidates(hn, ia), cb: mergeCandidates(hn, ib), walled: walled(K(113, 97), K(114, 98)) };
  hn.gold = 9999; G.factions[hn.owner].ap = 999; var o = baseOfficers(hn).filter(function (x) { return x.unit === null; })[0]; if (o) { o.acted = false; o.job = null; }
  var r = o ? cmdMerge(hn, ia, ib, [o.id]) : { ok: false, msg: 'no officer' }; out.merge = r.ok ? r.lv : r.msg; out.left = hn.plots[ib].fac === null && hn.plots[ia].fac && hn.plots[ia].fac.lv;
  put(hn, ia, 'market'); put(hn, ib, 'mint'); out.mint = adjFacCount(hn, ia, 'mint');
  return out;`;
const m1 = run(NEW, MERGE), m0 = run(OLD, MERGE);
console.log('② 합병 0.22', JSON.stringify(m1)); console.log('② 합병 0.21', JSON.stringify(m0));
ok(m1.adj === 1 && m1.ca.length === 1 && m1.cb.length === 1 && m1.merge === 2 && m1.left === 2, '홍농의 붙어 있는 두 농장이 합쳐진다(Lv2 · 흡수된 부지는 비었다)');
ok(m0.walled && m0.ca.length === 0 && m0.merge !== 2, '0.21 에서는 그 사이에 능선이 있어 합칠 수 없었다: ' + m0.merge);
ok(m1.mint === 1 && m0.mint === 0, '조폐가 옆 시장에 주는 몫도 이어졌다(0.21 에서는 끊겼다)');
const na = run(NEW, `newGame(0, 3); var bad = 0, tot = 0, more = 0; for (var k = 0; k < NHEX; k += 7) { var c = k % W, r = (k - c) / W, a = nbrs(c, r), b = nbrsAll(c, r); tot++; if (b.length < a.length) bad++; if (b.length > a.length) more++;
  a.forEach(function (n) { if (!b.some(function (m) { return m[0] === n[0] && m[1] === n[1]; })) bad++; }); }
  var w = MAPDATA.walls[0]; return { tot: tot, bad: bad, more: more, wn: nbrs(w[0], w[1]).length, wa: nbrsAll(w[0], w[1]).length };`);
ok(na.bad === 0 && na.wa > na.wn, 'nbrsAll 은 nbrs 에 능선 너머의 이웃을 더한 것이다 [' + JSON.stringify(na) + ']');

/* ③ 함락 */
const s3 = run(NEW, `var out = { cnt: [0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16].map(function (n) { return n + ':' + sackCount(n); }).join(' '), K: SACK };
  function fill(b, n, unf) { b.plots.forEach(function (p, i) { p.fac = i < n ? { t: FAC_ORDER[i % FAC_ORDER.length], lv: 1 + (i % 2), done: true, prog: 0, need: 0, rate: 0, hp: FAC_HP } : null; });
    if (unf) b.plots[n].fac = { t: 'farm', lv: 1, done: false, prog: 10, need: 300, rate: 100, hp: 300, by: [], t0: G.turn }; }
  function cnt(b) { return b.plots.filter(function (p) { return p.fac && p.fac.done; }).length; }
  function mk(b, type) { var o = baseOfficers(b).filter(function (x) { return x.unit === null; })[0]; b.troops = Math.max(b.troops, 20000); b.w.spear = b.w.horse = b.w.bow = 30000; G.factions[b.owner].ap = 999; o.acted = false;
    var r = cmdDeploy(b, { type: type, ids: [o.id], troops: 5000, food: 9000 }); if (!r.ok) throw new Error(r.msg); r.unit.born = -5; r.unit.done = false; return r.unit; }
  function side(b) { return nbrs(b.c, b.r).filter(function (n) { var k = K(n[0], n[1]), t = terr(n[0], n[1]); return t !== 'm' && t !== 's' && t !== 'x' && !UAT[k] && BAT[k] === undefined; }); }
  // (가) 맞붙어 빼앗는다 — 시설 10곳 + 짓다 만 것 하나
  newGame(0, 11); var me = facCities(0)[0], E = G.bases[baseByName('복양')], n0 = Math.min(10, E.plots.length - 1); fill(E, n0, true);
  var u = mk(me, 'spear'), s = side(E)[0]; placeUnit(u, s[0], s[1]); E.troops = 40; E.dur = 3; var seed0 = G.seed, old = E.owner;
  var r = unitAttack(u, { kind: 'base', b: E, c: E.c, r: E.r });
  out.melee = { ok: r.ok, fell: !!r.fell, n0: n0, want: sackCount(n0), sacked: (r.sacked || []).length, left: cnt(E), owner: E.owner === 0, unf: E.plots[n0].fac === null, txt: r.sacked ? sackText(r.sacked) : '', log: G.log.filter(function (e) { return e.t.indexOf('부서졌다') >= 0; }).length, ev: EVQ.filter(function (e) { return e.t === 'fall'; }).map(function (e) { return e.lost; }) };
  // (나) 같은 판 · 같은 턴이면 같은 것이 부서진다(주사위는 턴 · 거점 · 부지로 정해진다) · 판의 난수를 쓰지 않는다
  newGame(0, 11); E = G.bases[baseByName('복양')]; fill(E, n0, false); var sd = G.seed, a1 = sackBase(E).join(); out.seedSame = G.seed === sd; fill(E, n0, false); var a2 = sackBase(E).join(); out.same = a1 === a2; out.a1 = a1;
  // (다) 멀리서 쏘아 무너뜨린다 — 빈 거점이 되고, 시설의 일부가 부서진다
  newGame(0, 11); me = facCities(0)[0]; E = G.bases[baseByName('복양')]; fill(E, 6, false); var bw = mk(me, 'bow');
  var far = null; for (var rr = E.r - 2; rr <= E.r + 2 && !far; rr++) for (var cc = E.c - 2; cc <= E.c + 2 && !far; cc++) { var kk = K(cc, rr), tt = terr(cc, rr); if (hdist(cc, rr, E.c, E.r) === 2 && tt !== 'm' && tt !== 's' && tt !== 'x' && !UAT[kk] && BAT[kk] === undefined && !PAT[kk]) far = [cc, rr]; }
  placeUnit(bw, far[0], far[1]); E.troops = 30; E.dur = 3; var r2 = unitAttack(bw, { kind: 'base', b: E, c: E.c, r: E.r });
  out.ranged = { ok: r2.ok, fell: !!r2.fell, owner: E.owner, sacked: (r2.sacked || []).length, left: cnt(E), want: sackCount(6) };
  // (라) 주인 없는 거점에 걸어 들어가 차지한다 — 부서지지 않는다
  var left0 = cnt(E), u3 = mk(me, 'spear'), s3 = side(E)[0]; placeUnit(u3, s3[0], s3[1]); u3.mp = uMaxMp(u3); var rc = unitReach(u3), mv = unitMove(u3, E.c, E.r, rc);
  out.walk = { ok: mv.ok, cap: mv.captured === E.id, owner: E.owner === 0, left: cnt(E), left0: left0 };
  // (마) 시설이 둘뿐이면 하나도 부서지지 않는다
  newGame(0, 11); me = facCities(0)[0]; E = G.bases[baseByName('복양')]; fill(E, 2, false); u = mk(me, 'spear'); s = side(E)[0]; placeUnit(u, s[0], s[1]); E.troops = 40; E.dur = 3;
  var r4 = unitAttack(u, { kind: 'base', b: E, c: E.c, r: E.r }); out.two = { fell: !!r4.fell, sacked: (r4.sacked || []).length, left: cnt(E) };
  return out;`);
console.log('③ 함락', JSON.stringify(s3));
ok(s3.cnt === '0:0 1:0 2:0 3:1 4:1 5:2 6:2 8:2 10:3 12:4 16:5' && s3.K.rate === 0.3 && s3.K.min === 1 && s3.K.keep === 2, '부서지는 수: 시설 n 곳 × 0.3(반올림), 적어도 1 · 둘은 남긴다 → ' + s3.cnt);
ok(s3.melee.ok && s3.melee.fell && s3.melee.owner && s3.melee.sacked === s3.melee.want && s3.melee.left === s3.melee.n0 - s3.melee.want && s3.melee.want === 3, '맞붙어 빼앗은 성: 시설 ' + s3.melee.n0 + '곳 가운데 ' + s3.melee.sacked + '곳이 부서지고 ' + s3.melee.left + '곳이 남았다 (' + s3.melee.txt + ')');
ok(s3.melee.unf && s3.melee.log === 1 && s3.melee.ev.join() === String(s3.melee.want), '짓다 만 시설은 전처럼 버려진다 · 기록 한 줄 · 함락 사건에 부서진 수가 실린다');
ok(s3.seedSame && s3.same && s3.a1.split(',').length === 3, '어느 것이 부서지는지: 판의 난수를 쓰지 않고(G.seed 그대로), 같은 턴 · 같은 거점이면 같다 [' + s3.a1 + ']');
ok(s3.ranged.ok && s3.ranged.fell && s3.ranged.owner === -1 && s3.ranged.sacked === s3.ranged.want && s3.ranged.left === 6 - s3.ranged.want, '멀리서 쏘아 무너뜨린 성: 빈 거점이 되고 시설 6곳 가운데 ' + s3.ranged.sacked + '곳이 부서졌다');
ok(s3.walk.ok && s3.walk.cap && s3.walk.owner && s3.walk.left === s3.walk.left0, '주인 없는 거점에 걸어 들어가 차지하면 시설은 그대로다(' + s3.walk.left + '곳)');
ok(s3.two.fell && s3.two.sacked === 0 && s3.two.left === 2, '시설이 둘뿐인 성은 함락되어도 부서지지 않는다');

/* ④ 함께 맞은 부대의 번호 */
const x4 = run(NEW, `var out = { tries: 0 };
  for (var seed = 1; seed <= 60 && !out.done; seed++) {
    newGame(0, seed); var me = facCities(0)[0], E = G.bases[baseByName('복양')];
    var os = baseOfficers(me).filter(function (o) { return o.unit === null && o.apt.charAt(APT_IDX.halberd) >= 'A' || o.apt.charAt(APT_IDX.halberd) === 'S'; });
    os = baseOfficers(me).filter(function (o) { return o.unit === null && (o.apt.charAt(APT_IDX.halberd) === 'S' || o.apt.charAt(APT_IDX.halberd) === 'A'); }); if (!os.length) continue;
    me.troops = 30000; me.w.halberd = 30000; G.factions[0].ap = 999; os[0].acted = false;
    var r = cmdDeploy(me, { type: 'halberd', ids: [os[0].id], troops: 6000, food: 9000 }); if (!r.ok) continue; var u = r.unit; u.born = -5; u.done = false; u.morale = 100;
    // 빈 들판에 세우고 둘레에 작은 적 부대 셋
    var f = null; for (var rr = 92; rr < 112 && !f; rr++) for (var cc = 146; cc < 168 && !f; cc++) { var okk = true; for (var dr = -2; dr <= 2 && okk; dr++) for (var dc = -3; dc <= 3 && okk; dc++) { var k = K(cc + dc, rr + dr); if (TCH[k] !== 112 || ZONE[k] >= 0 || BAT[k] !== undefined || PAT[k] || UAT[k]) okk = false; } if (okk) f = [cc, rr]; }
    placeUnit(u, f[0], f[1]); E.troops = 30000; G.factions[E.owner].ap = 999;
    var ns = nbrs(f[0], f[1]), foes = [];
    for (var i = 0; i < 3; i++) { var eo = baseOfficers(E).filter(function (o) { return o.unit === null; })[0]; if (!eo) break; eo.acted = false; var er = cmdDeploy(E, { type: 'sword', ids: [eo.id], troops: 100, food: 100 }); if (!er.ok) break; placeUnit(er.unit, ns[i][0], ns[i][1]); foes.push(er.unit.id); }
    if (foes.length < 3) continue;
    var tac = tacticList(u).filter(function (t) { return t.id === 'seonpung'; })[0]; if (!tac) continue;
    var tg = UMAP[foes[0]]; out.tries++;
    var res = unitTactic(u, tac, { kind: 'unit', u: tg, c: tg.c, r: tg.r }); if (!res.ok || res.fail) continue;
    out.done = true; out.extra = res.extra.map(function (x) { return [x.id, !!x.dead, !!UMAP[x.id], x.dmg > 0]; }); out.foes = foes; out.killed = !!res.killed;
  }
  return out;`);
console.log('④ 함께 맞은 부대', JSON.stringify(x4));
ok(x4.done && x4.extra.length === 2 && x4.extra.every(e => x4.foes.indexOf(e[0]) >= 0 && e[3]), '일소: 함께 맞은 두 부대의 번호가 결과에 실린다');
ok(x4.done && x4.extra.every(e => e[1] === !e[2]), '궤멸한 부대에는 dead 가 붙는다(남은 부대에는 없다): ' + JSON.stringify(x4.extra));

/* ⑤ 0.21 의 저장 */
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
    x.facs = G.bases.every(function (g, k) { return g.plots.every(function (p, j) { var q = raw.bases[k].plots[j]; return (!!p.fac) === (!!q.fac) && (!p.fac || p.fac.t === q.fac.t); }); });
    x.nu = G.units.length; var s1 = serialize(); deserialize(s1); x.stable = serialize() === s1;
    var err = ''; G.aiOnly = true; try { for (var t = 0; t < 30 && !G.over; t++) endTurn(); } catch (e) { err = String(e && e.stack || e).slice(0, 300); } x.err = err; x.turn = G.turn;
    x.onBase = G.units.filter(function (u) { return BAT[K(u.c, u.r)] !== undefined; }).length;
    out.push(x);
  }
  return out;`);
mg.forEach((x, i) => console.log('⑤ 0.21 의 저장 ' + (i + 1), JSON.stringify(x)));
ok(mg.length === 3 && mg.every(x => x.ok && x.n === 50 && x.same && x.units && x.facs && x.stable), '세 판 모두 그대로 열린다(거점 · 시설 · 부대의 자리) · 저장 → 열기가 같다');
ok(mg.every(x => !x.err && x.onBase === 0), '연 판을 AI 끼리 30턴 더: 탈 없음' + mg.map(x => x.err).join(''));

console.log('\nv22: ' + pass + ' passed, ' + fail + ' failed');
process.exit(fail ? 1 : 0);
