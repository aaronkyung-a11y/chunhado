// v0.18 — 규칙 시험: 전법의 새 이름(한자 · 효과 딱지) · 견인(牽引)의 끌어당김 · 특기의 짧은 풀이 · 레벨이 없는 시설.   node tests/tac18.js
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.env.SRC || path.join(__dirname, '..', 'src');
const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array };
vm.createContext(ctx);
for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
let pass = 0, fail = 0;
function ok(c, msg) { if (c) pass++; else { fail++; console.log('  ✗ ' + msg); } }
const R = JSON.parse(vm.runInContext(`JSON.stringify((function () {
  var R = {}, _rnd = rnd;
  function O(n) { return G.officers.filter(function (o) { return o.n === n; })[0]; }
  function clear(c, r) { return inMap(c, r) && terr(c, r) === 'p' && !UAT[K(c, r)] && BAT[K(c, r)] === undefined && !PAT[K(c, r)]; }
  function field() {                                   // 둘레 두 겹이 모두 빈 평지인 자리
    for (var r = 6; r < H - 6; r++) for (var c = 6; c < W - 6; c++) {
      var good = true;
      for (var dr = -3; dr <= 3 && good; dr++) for (var dc = -4; dc <= 4 && good; dc++) if (!clear(c + dc, r + dr)) good = false;
      if (good) return [c, r];
    }
    return null;
  }
  // ① 이름: 열두 가지 모두 새 이름 · 한자 두 글자 · 효과 딱지. id 는 그대로
  var ids = [], names = [], hans = [], tags = [], k, OLD = Object.keys(TACTIC_OLD);
  for (k in TACTICS) TACTICS[k].forEach(function (t) { ids.push(t.id); names.push(t.name); hans.push(t.han || ''); tags.push(t.tag || ''); });
  R.names = { n: ids.length, ids: ids.join(','), names: names.join(','), hans: hans.join(','), noTag: tags.filter(function (t) { return !t; }).length,
    han2: hans.filter(function (h) { return h.length === 2 && /^[\\u4e00-\\u9fff]+$/.test(h); }).length,
    uniq: names.filter(function (n, i) { return names.indexOf(n) === i; }).length,
    oldLeft: names.filter(function (n) { return OLD.indexOf(n) >= 0; }).length,
    oldMap: OLD.length, oldOk: OLD.filter(function (o) { return !!TACTIC_BY_ID[TACTIC_OLD[o]]; }).length,
    byId: Object.keys(TACTIC_BY_ID).length,
    idOld: tacIdOf({ kind: 'tactic', tac: '갈퀴' }), idNew: tacIdOf({ kind: 'tactic', tac: '견인', tacId: 'galkwi' }), idNone: tacIdOf({ kind: 'attack' }), idOdd: tacIdOf({ kind: 'tactic', tac: '없는것' }),
    pullOnly: ids.filter(function (id) { return TACTIC_BY_ID[id].pull; }).join(',') };
  // ② 견인: 끌어당김
  newGame(0, 7); G.aiOnly = false; if (G.peace) G.peace.until = 0;
  var b = facCities(G.player)[0], eb = G.bases.filter(function (x) { return x.owner >= 0 && x.owner !== G.player && x.kind === 'city'; })[0];
  [b, eb].forEach(function (x) { x.troops = 60000; x.w.spear = x.w.halberd = x.w.bow = x.w.horse = 30000; x.food = 200000; G.factions[x.owner].ap = 250; });
  var me = idleOfficers(b).sort(function (p, q) { return q.war - p.war; })[0], foe = idleOfficers(eb).sort(function (p, q) { return q.ldr - p.ldr; })[0];
  var a = cmdDeploy(b, { type: 'halberd', ids: [me.id], troops: 5000, food: 5000 }).unit, d = cmdDeploy(eb, { type: 'spear', ids: [foe.id], troops: 5000, food: 5000 }).unit;
  var f = field(), GK = TACTIC_BY_ID.galkwi;
  function reset(dc) {
    placeUnit(a, f[0], f[1]); placeUnit(d, f[0] + (dc || 1), f[1]);
    [a, d].forEach(function (u) { u.born = -9; u.done = false; u.mp = uMaxMp(u); u.morale = 80; u.troops = 5000; u.status = null; u.stT = 0; }); G.fires = {};
  }
  function go(roll) { rnd = function () { return roll; }; var r = unitTactic0(a, GK, { kind: 'unit', u: d, c: d.c, r: d.r }); rnd = _rnd; return r; }
  function snap(r) { return { ok: r.ok, fail: !!r.fail, pulled: !!r.pulled, noPull: !!r.noPull, a: [a.c, a.r], d: [d.c, d.r], tc: [r.tc, r.tr], uc: [r.uc, r.ur], counter: r.counter || 0, dmg: r.dmg, tacId: r.tacId, tac: r.tac,
    uatA: UAT[K(a.c, a.r)] === a, uatD: UAT[K(d.c, d.r)] === d, uatOld: UAT[K(f[0] + 1, f[1])] === undefined, dist: hdist(a.c, a.r, d.c, d.r), mor: 80 - a.morale, done: a.done }; }
  R.f = f; R.apt = uApt(a); R.has = tacticList(a).some(function (t) { return t.id === 'galkwi'; });
  reset(); R.room = pullRoom(a, d); R.pull = snap(go(0.50));                 // 성공(대성공은 아니게 가운데쯤): od.crit < 50 < od.ok 이어야 한다
  reset(); var od = tacticOdds(a, d); R.od = [od.ok, od.crit];
  // 서쪽에서 끌기(방향이 거꾸로여도)
  reset(-1); R.pullW = snap(go(0.50));
  // 내 뒤에 부대가 있으면 끌지 못한다
  reset(); var blk = cmdDeploy(b, { type: 'spear', ids: [idleOfficers(b)[0].id], troops: 3000, food: 3000 }).unit; placeUnit(blk, f[0] - 1, f[1]);
  R.roomBlk = pullRoom(a, d); R.blocked = snap(go(0.50)); R.blkAt = [blk.c, blk.r];
  placeUnit(blk, f[0] - 3, f[1] + 2);
  // 내 뒤가 불타고 있으면 끌지 못한다
  reset(); G.fires[K(f[0] - 1, f[1])] = 2; R.roomFire = pullRoom(a, d); R.fire = snap(go(0.50)); G.fires = {};
  // 실패하면 끌지 못한다(반격을 받는다)
  reset(); R.failed = snap(go(0.999));
  // 대성공: 끌어당기고 기력도 깎는다
  reset(); var rc = go(0.0); R.crit = { crit: !!rc.crit, pulled: !!rc.pulled, mor: rc.mor || 0, dmor: 80 - d.morale };
  // 끌려와 죽어도 탈이 없다
  reset(); d.troops = 1; var rk = go(0.50); R.kill = { killed: !!rk.killed, pulled: !!rk.pulled, a: [a.c, a.r], gone: !UMAP[d.id], uat: UAT[K(f[0], f[1])] === undefined };
  // ③ 다른 전법도 tacId 를 싣는다
  var d2 = cmdDeploy(eb, { type: 'spear', ids: [idleOfficers(eb)[0].id], troops: 5000, food: 5000 }).unit, sp = cmdDeploy(b, { type: 'spear', ids: [idleOfficers(b)[0].id], troops: 5000, food: 5000 }).unit;
  placeUnit(sp, f[0], f[1] + 3); placeUnit(d2, f[0] + 1, f[1] + 3); sp.done = false; sp.morale = 80;
  rnd = function () { return 0.50; }; var r3 = unitTactic0(sp, TACTIC_BY_ID.dolchul, { kind: 'unit', u: d2, c: d2.c, r: d2.r }); rnd = _rnd;
  R.other = { tacId: r3.tacId, tac: r3.tac, pulled: r3.pulled === undefined && r3.noPull === undefined, pushed: r3.pushed || 0 };
  // ④ 특기의 짧은 풀이(화면이 줄마다 곁들인다) — 있는 특기는 모두
  if (typeof SKILL_TAG !== 'undefined') {
    var sk = Object.keys(SKILLS); R.sk = { n: sk.length, noTag: sk.filter(function (s) { return !SKILL_TAG[s]; }).join(','), extra: Object.keys(SKILL_TAG).filter(function (s) { return !SKILLS[s]; }).join(','), long: sk.filter(function (s) { return (SKILL_TAG[s] || '').length > 18; }).join(','),
      used: G.officers.filter(function (o) { return o.sk && !SKILLS[o.sk]; }).length };
  }
  // ⑤ 레벨이 없는 시설(공방 · 조폐 · 곡창): 합칠 수 없고, 옛 저장의 레벨은 1로
  R.nolv = { list: Object.keys(FAC).filter(function (t) { return !facHasLv(t); }).join(','), has: Object.keys(FAC).filter(function (t) { return facHasLv(t); }).join(',') };
  var pb = facCities(G.player)[0], pr = null, i2, j2;
  for (i2 = 0; i2 < pb.plots.length && !pr; i2++) for (j2 = 0; j2 < pb.plots.length && !pr; j2++) if (i2 !== j2 && hdist(pb.plots[i2].c, pb.plots[i2].r, pb.plots[j2].c, pb.plots[j2].r) === 1) pr = [i2, j2];
  function F(t, lv) { return { t: t, lv: lv, done: true, prog: 0, need: 0, rate: 0, hp: FAC_HP }; }
  var keep = pb.plots.map(function (q) { return q.fac; });
  pb.plots.forEach(function (q) { q.fac = null; });
  pb.gold = 9000; G.factions[G.player].ap = 250; var who = idleOfficers(pb)[0];
  R.merge = {};
  ['mint', 'granary', 'workshop', 'market', 'barracks'].forEach(function (t) {
    pb.plots[pr[0]].fac = F(t, 1); pb.plots[pr[1]].fac = F(t, 1); who.acted = false;
    var c = mergeCandidates(pb, pr[0]).length, r = cmdMerge(pb, pr[0], pr[1], [who.id]);
    R.merge[t] = [c, !!r.ok, pb.plots[pr[0]].fac.lv, !!pb.plots[pr[1]].fac];
    pb.plots[pr[0]].fac = null; pb.plots[pr[1]].fac = null;
  });
  // 레벨은 수입에 쓰이지 않는다(그래서 없앴다): 조폐 Lv1 과 Lv3 의 금 수입이 같다
  pb.plots[pr[0]].fac = F('market', 1); pb.plots[pr[1]].fac = F('mint', 1); var g1 = goldIncome(pb); pb.plots[pr[1]].fac.lv = 3; var g3 = goldIncome(pb); pb.plots[pr[1]].fac = null; var g0 = goldIncome(pb);
  R.inc = [g0, g1, g3];
  // 옛 저장: 조폐 Lv3 · 시장 Lv3 을 담아 저장했다가 불러온다
  pb.plots[pr[0]].fac = F('market', 3); pb.plots[pr[1]].fac = F('mint', 3);
  var sv = serialize(); var bid = pb.id; deserialize(sv);
  var nb = G.bases[bid]; R.load = [nb.plots[pr[0]].fac.t, nb.plots[pr[0]].fac.lv, nb.plots[pr[1]].fac.t, nb.plots[pr[1]].fac.lv];
  return R;
})())`, ctx));
// ① 이름
ok(R.names.n === 12 && R.names.byId === 12, '전법 12가지 ' + R.names.n);
ok(R.names.ids === 'dolchul,naseon,idan,galkwi,hoengchi,seonpung,hwasi,gwansi,nansa,dolgyeok,dolpa,doljin', 'id 는 그대로 ' + R.names.ids);
ok(R.names.names === '격퇴,난진,탈기,견인,횡소,일소,화전,관통,전우,축출,관진,유린', '새 이름 ' + R.names.names);
ok(R.names.hans === '擊退,亂陣,奪氣,牽引,橫掃,一掃,火箭,貫通,箭雨,逐出,貫陣,蹂躪', '한자 ' + R.names.hans);
ok(R.names.han2 === 12 && R.names.noTag === 0 && R.names.uniq === 12, '한자 두 글자 · 효과 딱지 · 겹치지 않음 ' + JSON.stringify(R.names));
ok(R.names.oldLeft === 0 && R.names.oldMap === 12 && R.names.oldOk === 12, '옛 이름은 남지 않고, 옛 이름 → id 표는 열두 줄');
ok(R.names.idOld === 'galkwi' && R.names.idNew === 'galkwi' && R.names.idNone === '' && R.names.idOdd === '', '옛 기록의 이름도 id 로 찾는다 ' + [R.names.idOld, R.names.idNew]);
ok(R.names.pullOnly === 'galkwi', '끌어당기는 전법은 견인뿐 ' + R.names.pullOnly);
// ② 견인
const f = R.f;
ok(R.has, '극병 적성 ' + R.apt + ' — 견인을 쓸 수 있다');
ok(R.od[1] < 50 && R.od[0] > 50, '시험 주사위 50 은 성공(대성공 아님) ' + R.od);
ok(R.room === true, '뒤가 비었으면 끌 수 있다고 미리 안다');
ok(R.pull.ok && !R.pull.fail && R.pull.pulled && !R.pull.noPull, '성공 → 끌어당김 ' + JSON.stringify(R.pull));
ok(R.pull.a[0] === f[0] - 1 && R.pull.a[1] === f[1], '나는 한 칸 뒤로 ' + R.pull.a + ' (처음 ' + f + ')');
ok(R.pull.d[0] === f[0] && R.pull.d[1] === f[1], '적은 내가 섰던 자리로 ' + R.pull.d);
ok(R.pull.tc[0] === f[0] && R.pull.tc[1] === f[1] && R.pull.uc[0] === f[0] - 1, '결과에 옮긴 자리가 실린다 ' + R.pull.tc + ' / ' + R.pull.uc);
ok(R.pull.uatA && R.pull.uatD && R.pull.uatOld && R.pull.dist === 1, '자리 표(UAT)가 맞고 둘은 여전히 붙어 있다');
ok(R.pull.counter === 0 && R.pull.mor === 10 && R.pull.done, '반격 없음 · 기력 10 · 행동 끝');
ok(R.pull.tacId === 'galkwi' && R.pull.tac === '견인', '결과의 이름 · id');
ok(R.pullW.pulled && R.pullW.a[0] === f[0] + 1 && R.pullW.d[0] === f[0], '반대쪽의 적도 내 쪽으로 끈다 ' + JSON.stringify([R.pullW.a, R.pullW.d]));
ok(R.roomBlk === false && !R.blocked.pulled && R.blocked.noPull && R.blocked.a[0] === f[0] && R.blocked.d[0] === f[0] + 1, '뒤에 부대가 있으면 끌지 못한다 ' + JSON.stringify(R.blocked));
ok(R.blocked.ok && !R.blocked.fail && R.blocked.counter === 0 && R.blocked.dmg === R.pull.dmg, '끌지 못해도 피해는 같고 반격은 없다 ' + R.blocked.dmg + ' / ' + R.pull.dmg);
ok(R.roomFire === false && !R.fire.pulled && R.fire.noPull && R.fire.a[0] === f[0], '뒤가 불타고 있으면 끌지 못한다');
ok(R.failed.fail && !R.failed.pulled && !R.failed.noPull && R.failed.a[0] === f[0] && R.failed.d[0] === f[0] + 1 && R.failed.counter > 0, '실패하면 끌지 못하고 반격을 받는다 ' + JSON.stringify(R.failed));
ok(R.crit.crit && R.crit.pulled && R.crit.mor === 15 && R.crit.dmor >= 15, '대성공 → 끌어당기고 기력 −15 ' + JSON.stringify(R.crit));
ok(R.kill.killed && R.kill.gone && R.kill.a[0] === f[0] - 1 && R.kill.uat, '끌려와 궤멸해도 자리 표가 깨끗하다 ' + JSON.stringify(R.kill));
// ③
ok(R.other.tacId === 'dolchul' && R.other.tac === '격퇴' && R.other.pulled && R.other.pushed === 1, '다른 전법은 끌지 않는다 · tacId ' + JSON.stringify(R.other));
// ④
if (R.sk) {
  ok(R.sk.n >= 46 && R.sk.noTag === '' && R.sk.extra === '', '특기 ' + R.sk.n + '가지 모두 짧은 풀이 — 없는 것: [' + R.sk.noTag + '] 남는 것: [' + R.sk.extra + ']');
  ok(R.sk.long === '', '짧은 풀이는 18자 안 — 긴 것: ' + R.sk.long);
  ok(R.sk.used === 0, '무장이 가진 특기는 모두 풀이가 있다');
} else ok(false, 'SKILL_TAG 가 없다');
// ⑤ 레벨이 없는 시설
ok(R.nolv.list === 'workshop,mint,granary' && R.nolv.has === 'market,farm,barracks,smithy,stable', '레벨이 없는 시설은 공방 · 조폐 · 곡창 셋 [' + R.nolv.list + ']');
ok(['mint', 'granary', 'workshop'].every(t => R.merge[t][0] === 0 && !R.merge[t][1] && R.merge[t][2] === 1 && R.merge[t][3]), '조폐 · 곡창 · 공방은 붙어 있어도 합칠 수 없다(그대로 두 곳) ' + JSON.stringify([R.merge.mint, R.merge.granary, R.merge.workshop]));
ok(['market', 'barracks'].every(t => R.merge[t][0] === 1 && R.merge[t][1] && R.merge[t][2] === 2 && !R.merge[t][3]), '시장 · 병영은 전처럼 합쳐 Lv2 ' + JSON.stringify([R.merge.market, R.merge.barracks]));
ok(R.inc[1] > R.inc[0] && R.inc[1] === R.inc[2], '조폐의 레벨은 수입에 쓰이지 않는다(없을 때 ' + R.inc[0] + ' · Lv1 ' + R.inc[1] + ' · Lv3 ' + R.inc[2] + ')');
ok(R.load.join(',') === 'market,3,mint,1', '옛 저장을 불러오면 조폐의 레벨은 1로, 시장은 그대로 [' + R.load + ']');
console.log('tac18: ' + pass + ' passed, ' + fail + ' failed');
process.exit(fail ? 1 : 0);
