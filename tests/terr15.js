// v0.15 — 지형의 규칙 시험: 넓어진 산 · 높이 단계 · 싸움에 곱해지는 값 · 옛 저장 옮기기.   node tests/terr15.js
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.env.SRC || path.join(__dirname, '..', 'src');
const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array };
vm.createContext(ctx);
for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
let pass = 0, fail = 0;
function ok(c, msg) { if (c) pass++; else { fail++; console.log('  ✗ ' + msg); } }
const R = JSON.parse(vm.runInContext(`JSON.stringify((function () {
  var R = {}, T = MAPDATA.t, T0 = MAPDATA.t0, RD = MAPDATA.road, i, c, r;
  newGame(0, 1); G.aiOnly = false;
  // ① 지도: 바뀐 칸
  var conv = 0, from = {}, badRoad = 0, other = 0;
  for (i = 0; i < T.length; i++) if (T.charAt(i) !== T0.charAt(i)) { if (T.charAt(i) === 'm' && 'hpfd'.indexOf(T0.charAt(i)) >= 0) { conv++; from[T0.charAt(i)] = (from[T0.charAt(i)] || 0) + 1; if (RD.charAt(i) === '1') badRoad++; } else other++; }
  var nearM = 0; for (i = 0; i < T.length; i++) if (T.charAt(i) === 'm' && T0.charAt(i) !== 'm') { var cc = i % W, rr = (i - cc) / W, ns = nbrs(cc, rr), near = false; for (var j = 0; j < ns.length; j++) { var q = nbrs(ns[j][0], ns[j][1]); if (T0.charAt(K(ns[j][0], ns[j][1])) === 'm') near = true; for (var k2 = 0; k2 < q.length; k2++) if (T0.charAt(K(q[k2][0], q[k2][1])) === 'm') near = true; } if (near) nearM++; }
  R.map = { len: [T.length, T0.length, MAPDATA.e.length, NHEX], conv: conv, from: from, badRoad: badRoad, other: other, nearM: nearM, m0: T0.split('m').length - 1, m1: T.split('m').length - 1 };
  // 거점 · 부지 · 길은 갈 수 있는 칸
  var badBase = 0, badPlot = 0, badRd = 0;
  G.bases.forEach(function (b) { if ('msx'.indexOf(terr(b.c, b.r)) >= 0) badBase++; b.plots.forEach(function (p) { if (MC[0][K(p.c, p.r)] >= 99) badPlot++; }); nbrs(b.c, b.r).forEach(function () {}); });
  for (i = 0; i < NHEX; i++) if (RDB[i] && MC[0][i] >= 99) badRd++;
  R.keep = [badBase, badPlot, badRd];
  // 이웃한 거점 사이의 길이 모두 있다
  var noPath = 0, fakeU = { type: 'spear', f: G.player, off: [G.factions[G.player].lord], troops: 1000, morale: 100, c: 0, r: 0 };
  MAPDATA.edges.forEach(function (e) { var a = G.bases[e[0]], b = G.bases[e[1]]; fakeU.c = a.c; fakeU.r = a.r; var p = marchPath(fakeU, K(b.c, b.r)); if (!p || !p.length) noPath++; });
  R.paths = [MAPDATA.edges.length, noPath];
  // ② 높이 단계
  var lv = {}, mx = 0; for (i = 0; i < NHEX; i++) { if (MC[0][i] >= 99) continue; lv[ELV[i]] = (lv[ELV[i]] || 0) + 1; if (ELV[i] > mx) mx = ELV[i]; }
  R.elev = { max: mx, zero: lv[0] || 0, kinds: Object.keys(lv).length, sample: [elevOf(156, 92), ELV[K(156, 92)]] };
  // ③ 싸움에 곱해지는 값: 조건에 맞는 이웃한 두 칸을 찾아 쓴다
  function pair(fn) { for (var r = 4; r < H - 4; r++) for (var c = 4; c < W - 4; c++) { if (MC[0][K(c, r)] >= 99) continue; var ns = nbrs(c, r); for (var j = 0; j < ns.length; j++) { if (MC[0][K(ns[j][0], ns[j][1])] >= 99) continue; if (fn(c, r, ns[j][0], ns[j][1])) return [[c, r], ns[j]]; } } return null; }
  function U(p, type) { return { c: p[0], r: p[1], type: type || 'spear' }; }
  function ks(ms) { return ms.map(function (m) { return m.k + ':' + m.m.toFixed(2); }).join('|'); }
  function tt(c, r) { return terr(c, r); }
  var flat = pair(function (a, b, c, d) { return tt(a, b) === 'p' && tt(c, d) === 'p' && ELV[K(a, b)] === ELV[K(c, d)]; });
  var toF = pair(function (a, b, c, d) { return tt(a, b) === 'p' && tt(c, d) === 'f' && ELV[K(a, b)] === ELV[K(c, d)]; });
  var toH = pair(function (a, b, c, d) { return tt(a, b) === 'p' && tt(c, d) === 'h' && ELV[K(a, b)] === ELV[K(c, d)]; });
  var fromF = pair(function (a, b, c, d) { return tt(a, b) === 'f' && tt(c, d) === 'p' && ELV[K(a, b)] === ELV[K(c, d)]; });
  var toW = pair(function (a, b, c, d) { return tt(a, b) === 'p' && tt(c, d) === 'w' && ELV[K(a, b)] === ELV[K(c, d)]; });
  var up1 = pair(function (a, b, c, d) { return tt(a, b) === 'p' && tt(c, d) === 'p' && ELV[K(a, b)] - ELV[K(c, d)] === 1; });
  var up2 = pair(function (a, b, c, d) { return tt(a, b) === 'd' && tt(c, d) === 'd' && ELV[K(a, b)] - ELV[K(c, d)] === 2; }) || pair(function (a, b, c, d) { return tt(a, b) === 'p' && tt(c, d) === 'p' && ELV[K(a, b)] - ELV[K(c, d)] === 2; });
  var up4 = flat, e4 = ELV[K(flat[0][0], flat[0][1])]; ELV[K(flat[0][0], flat[0][1])] = e4 + 9;      // 높이 차가 아주 큰 경우는 지도에 드물다 — 잠깐 만들어서 본다
  R.m4 = [ks(terrMods(U(up4[0]), U(up4[1]), false)), ks(terrMods(U(up4[1]), U(up4[0]), false))]; R.diff4 = elevDiff(U(up4[0]), U(up4[1])); ELV[K(flat[0][0], flat[0][1])] = e4;
  R.found = [!!flat, !!toF, !!toH, !!fromF, !!toW, !!up1, !!up2, !!up4];
  R.mods = {
    flat: ks(terrMods(U(flat[0]), U(flat[1]), false)), flatCav: ks(terrMods(U(flat[0], 'cav'), U(flat[1]), false)), flatBow: ks(terrMods(U(flat[0], 'bow'), U(flat[1]), true)),
    toF: ks(terrMods(U(toF[0]), U(toF[1]), false)), toFshot: ks(terrMods(U(toF[0], 'bow'), U(toF[1]), true)), toFcav: ks(terrMods(U(toF[0], 'cav'), U(toF[1]), false)),
    toH: ks(terrMods(U(toH[0]), U(toH[1]), false)), toHshot: ks(terrMods(U(toH[0], 'bow'), U(toH[1]), true)),
    fromFcav: ks(terrMods(U(fromF[0], 'cav'), U(fromF[1]), false)), fromF: ks(terrMods(U(fromF[0]), U(fromF[1]), false)),
    toW: ks(terrMods(U(toW[0]), U(toW[1]), false)), fromW: ks(terrMods(U(toW[1]), U(toW[0]), false)),
    up1: ks(terrMods(U(up1[0]), U(up1[1]), false)), down1: ks(terrMods(U(up1[1]), U(up1[0]), false)),
    up2: up2 ? ks(terrMods(U(up2[0]), U(up2[1]), false)) : '', up4: R.m4[0], down4: R.m4[1]
  };
  R.mul = [terrMul(U(toF[0], 'cav'), U(toF[1]), false), TERR_K.cover * TERR_K.cavRough, terrMul(U(flat[0]), U(flat[1]), false)];
  R.diff = [elevDiff(U(up1[0]), U(up1[1])), elevDiff(U(up1[1]), U(up1[0])), R.diff4];
  // ④ 실제 피해에 들어간다: 같은 두 부대를 평평한 칸과 높낮이가 있는 칸에 세워 본다(주사위를 빼려고 dmgBase)
  var b = facCities(G.player)[0], eb = G.bases[baseByName('복양')]; b.troops = 60000; b.w.spear = 30000; b.w.horse = 30000; b.food = 200000; eb.troops = 60000; eb.w.spear = 30000; eb.food = 200000; G.factions[G.player].ap = 250; G.factions[eb.owner].ap = 250;
  var os = idleOfficers(b).filter(function (o) { return !isLord(o); });
  var a1 = cmdDeploy(b, { type: 'spear', ids: [os[0].id], troops: 5000, food: 5000 }).unit, cv = cmdDeploy(b, { type: 'cav', ids: [os[1].id], troops: 5000, food: 5000 }).unit, d1 = cmdDeploy(eb, { type: 'spear', ids: [idleOfficers(eb)[0].id], troops: 5000, food: 5000 }).unit;
  function at(u, p) { placeUnit(u, p[0], p[1]); }
  function free(p) { return !UAT[K(p[0][0], p[0][1])] && !UAT[K(p[1][0], p[1][1])] && BAT[K(p[0][0], p[0][1])] === undefined && BAT[K(p[1][0], p[1][1])] === undefined; }
  at(a1, flat[0]); at(d1, flat[1]); var base = dmgBase(a1, d1, 1, false);
  at(a1, up1[0]); at(d1, up1[1]); var hi = dmgBase(a1, d1, 1, false), lo = dmgBase(d1, a1, 1, false); at(a1, up1[1]); at(d1, up1[0]); var loA = dmgBase(a1, d1, 1, false);
  at(a1, toF[0]); at(d1, toF[1]); var inF = dmgBase(a1, d1, 1, false), shotF = dmgBase(a1, d1, 1, true);
  R.dmg = { hi: hi / base, loA: loA / base, inF: inF / base, shotF: shotF / base };
  at(a1, flat[0]); at(d1, flat[1]); removeUnit(a1); at(cv, flat[0]); var cb = dmgBase(cv, d1, 1, false); at(cv, fromF[0]); at(d1, fromF[1]); var cr = dmgBase(cv, d1, 1, false);
  R.cav = cr / cb;
  // 예상 피해(화면이 보이는 값)에도 들어 있다
  at(cv, up1[0]); at(d1, up1[1]); var e1 = attackExpect(cv, d1).dealt; at(cv, up1[1]); at(d1, up1[0]); var e2 = attackExpect(cv, d1).dealt; R.expect = e1 / e2;
  // ⑤ 옛 저장: 못 가는 칸에 선 부대를 옮긴다
  var mh = null; for (i = 0; i < NHEX && !mh; i++) if (T.charAt(i) === 'm' && T0.charAt(i) !== 'm') mh = [i % W, (i - i % W) / W];
  delete UAT[K(cv.c, cv.r)]; cv.c = mh[0]; cv.r = mh[1]; UAT[K(cv.c, cv.r)] = cv;
  var L0 = G.log.length, sv = serialize(); deserialize(sv); var cv2 = UMAP[cv.id];
  R.fix = { was: [mh[0], mh[1], terr(mh[0], mh[1])], now: [cv2.c, cv2.r, terr(cv2.c, cv2.r)], pass: MC[0][K(cv2.c, cv2.r)] < 99, dist: hdist(mh[0], mh[1], cv2.c, cv2.r), uat: UAT[K(cv2.c, cv2.r)] === cv2 && !UAT[K(mh[0], mh[1])], log: G.log.slice(-3).map(function (x) { return x.t; }).join('|'), again: terrainFix().length };
  // 한 판을 돌려도 못 가는 칸에 서는 부대가 없다
  newGame(0, 5); G.aiOnly = true; var bad = 0; for (var t = 0; t < 60; t++) { endTurn(); G.units.forEach(function (u) { if (MC[0][K(u.c, u.r)] >= 99) bad++; }); }
  R.sim = [bad, G.turn];
  return R;
})())`, ctx));
const E = vm.runInContext('ELEV_K', ctx), TK = vm.runInContext('TERR_K', ctx);
// ①
ok(R.map.len.every(n => n === R.map.len[3]), '지형 · 전의 지형 · 높이 단계가 모두 칸 수만큼');
ok(R.map.conv === 642 && R.map.other === 0 && R.map.badRoad === 0 && R.map.nearM === R.map.conv && R.map.m1 === R.map.m0 + R.map.conv, '산으로 바뀐 칸 ' + R.map.conv + ' ' + JSON.stringify(R.map.from) + ' — 모두 산에서 두 칸 안, 길은 없다 (산 ' + R.map.m0 + ' → ' + R.map.m1 + ')');
ok(R.keep.join() === '0,0,0', '거점 · 부지 · 길은 모두 갈 수 있는 칸: ' + R.keep);
ok(R.paths[1] === 0, '이웃한 거점 ' + R.paths[0] + '쌍 사이에 길이 있다');
// ②
ok(R.elev.max >= 10 && R.elev.max <= 35 && R.elev.kinds >= 8 && R.elev.sample[0] === R.elev.sample[1], '높이 단계: 갈 수 있는 칸의 가장 높은 곳 ' + R.elev.max + ' · ' + R.elev.kinds + '가지');
// ③
ok(R.found.every(Boolean), '시험에 쓸 칸을 찾았다 ' + R.found);
ok(R.mods.flat === '' && R.mods.flatBow === '', '평지 · 같은 높이: 아무것도 곱해지지 않는다');
ok(R.mods.flatCav === '기병 · 평지:' + TK.cavPlain.toFixed(2), '기병이 평지에서 평지의 적을: ' + R.mods.flatCav);
ok(R.mods.toF === '숲의 적:0.85' && R.mods.toH === '구릉의 적:0.85', '숲 · 구릉의 적: ' + R.mods.toF + ' / ' + R.mods.toH);
ok(R.mods.toFshot === '숲의 적:0.85|숲 속으로 쏨:0.85' && R.mods.toHshot === '구릉의 적:0.85', '숲 속의 적을 쏘면 더 깎인다(구릉은 아니다): ' + R.mods.toFshot);
ok(R.mods.toFcav === '숲의 적:0.85|기병 · 험한 땅:0.85' && R.mods.fromFcav === '기병 · 험한 땅:0.85' && R.mods.fromF === '', '기병은 숲으로 치든 숲에서 치든 −15%: ' + R.mods.toFcav + ' / ' + R.mods.fromFcav);
ok(R.mods.toW === '강 위의 적:1.20' && R.mods.fromW === '강 위에서:0.70', '강: ' + R.mods.toW + ' / ' + R.mods.fromW);
ok(R.mods.up1 === '높은 곳에서:' + (1 + E.step).toFixed(2) && R.mods.down1 === '낮은 곳에서:' + (1 - E.step).toFixed(2), '한 단 높으면 +' + E.step * 100 + '%, 낮으면 −: ' + R.mods.up1 + ' / ' + R.mods.down1);
ok(R.mods.up2.indexOf('높은 곳에서:' + (1 + 2 * E.step).toFixed(2)) >= 0, '두 단: ' + R.mods.up2);
ok(R.mods.up4.indexOf('높은 곳에서:' + (1 + E.max * E.step).toFixed(2)) >= 0 && R.mods.down4.indexOf('낮은 곳에서:' + (1 - E.max * E.step).toFixed(2)) >= 0 && R.diff[2] === E.max, '세 단까지만: ' + R.mods.up4 + ' / ' + R.mods.down4);
ok(Math.abs(R.mul[0] - R.mul[1]) < 1e-9 && R.mul[2] === 1 && R.diff[0] === 1 && R.diff[1] === -1, '곱은 내역의 곱과 같고, 높이 차는 뒤집으면 부호가 바뀐다');
// ④
ok(Math.abs(R.dmg.hi - (1 + E.step)) < 1e-6 && Math.abs(R.dmg.loA - (1 - E.step)) < 1e-6, '피해에 들어간다: 높은 곳 ×' + R.dmg.hi.toFixed(3) + ' · 낮은 곳 ×' + R.dmg.loA.toFixed(3));
ok(Math.abs(R.dmg.inF - 0.85) < 1e-6 && Math.abs(R.dmg.shotF - 0.85 * 0.85) < 1e-6, '숲의 적 ×' + R.dmg.inF.toFixed(3) + ' · 쏘면 ×' + R.dmg.shotF.toFixed(3));
ok(Math.abs(R.cav - TK.cavRough / TK.cavPlain) < 1e-6, '기병: 숲에서 치면 평지의 ×' + R.cav.toFixed(3));
ok(Math.abs(R.expect - (1 + E.step) / (1 - E.step)) < 0.02, '예상 피해에도 들어 있다(위에서 ÷ 아래에서 = ' + R.expect.toFixed(3) + ')');
// ⑤
ok(R.fix.was[2] === 'm' && R.fix.pass && R.fix.dist >= 1 && R.fix.dist <= 4 && R.fix.uat && /지형이 바뀌어/.test(R.fix.log) && R.fix.again === 0, '옛 저장: 산이 된 칸의 부대를 ' + R.fix.dist + '칸 옆의 갈 수 있는 칸으로 옮기고 알린다 — ' + R.fix.now);
ok(R.sim[0] === 0, 'AI 대전 60턴: 못 가는 칸에 서는 부대가 없다');
console.log((fail ? 'FAIL ' : 'ok ') + pass + ' / ' + (pass + fail));
process.exit(fail ? 1 : 0);
