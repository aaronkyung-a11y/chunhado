// v0.7.1 규칙 확인: 건설을 맡은 무장은 완공될 때까지 묶인다(다른 명령·출진·이동 불가). 완공·공사 중단·함락·파괴로 풀린다.
//   node tests/job8.js            ← 지금 규칙
//   SRC=<v0.7 소스 폴더> node tests/job8.js   ← 앞 판에서는 어떻게 되는지(다음 턴에 다시 쓸 수 있었음)
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.env.SRC || path.join(__dirname, '..', 'src');
const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat };
vm.createContext(ctx);
for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
vm.runInContext(fs.readFileSync(path.join(__dirname, 'sim.js'), 'utf8').match(/function invariants\(\)[\s\S]*?\n}\nfunction summary/)[0].replace(/\nfunction summary$/, ''), ctx);
vm.runInContext(`
var RES = [];
function chk(name, cond, info) { RES.push([name, !!cond, info === undefined ? '' : JSON.stringify(info)]); }
var HAS = typeof jobOf === 'function';
function busy(o) { return HAS ? !!jobOf(o) : false; }
function setup(seed) {
  newGame(0, seed);
  var b = facCities(G.player)[0];
  b.gold = 9000; b.food = 90000; b.troops = 20000; b.w.spear = 9000; G.factions[G.player].ap = 255;
  return b;
}
function freePlots(b) { var out = []; b.plots.forEach(function (p, i) { if (!p.fac && !UAT[K(p.c, p.r)]) out.push(i); }); return out; }
function nextTurn(b) { endTurn(); G.factions[G.player].ap = 255; b.gold = Math.max(b.gold, 5000); }
function run() {
  // ---------- 1. 착공한 턴과 그 뒤 ----------
  var b = setup(8001), os = idleOfficers(b).sort(function (x, y) { return y.pol - x.pol; });
  var A = os[0], B = os[1], other = os[2], pi = freePlots(b)[0];
  var r = cmdDevelop(b, pi, 'market', [A.id, B.id]);
  chk('착공 성공', r.ok && r.turns >= 2, r);
  var T = r.turns, fc = b.plots[pi].fac;
  chk('착공한 턴: 두 무장 모두 행동 완료', A.acted && B.acted);
  chk('착공한 턴: 그 무장으로 징병 불가', !cmdDraft(b, [A.id]).ok);
  chk('착공한 턴: 그 무장으로 출진 불가', !cmdDeploy(b, { type: 'spear', ids: [A.id], troops: 3000, food: 3000 }).ok);
  chk('착공한 턴: 다른 무장은 쓸 수 있음', cmdPatrol(b, [other.id]).ok);
  var log = [];
  for (var t = 1; t < T; t++) {
    nextTurn(b);
    var idleNow = idleOfficers(b).map(function (o) { return o.id; });
    var st = { turn: t, done: fc.done, busyA: busy(A), actedA: A.acted, inIdle: idleNow.indexOf(A.id) >= 0 || idleNow.indexOf(B.id) >= 0,
      draft: cmdDraft(b, [A.id]).ok, deploy: false, move: false, build2: false };
    if (!st.draft) {                                     // 묶여 있다면 나머지 명령도 모두 막혀야 한다
      st.deploy = cmdDeploy(b, { type: 'spear', ids: [B.id], troops: 3000, food: 3000 }).ok;
      var dst = facBases(G.player).filter(function (x) { return x.id !== b.id; })[0];
      st.move = dst ? cmdMoveOfficers(b, [B.id], dst.id).ok : false;
      var fp = freePlots(b); st.build2 = fp.length ? cmdDevelop(b, fp[0], 'farm', [B.id]).ok : false;
      st.auto = autoPick('draft', b, null, 3).some(function (id) { return id === A.id || id === B.id; }) || autoTeam(b, 'spear', 5000).some(function (id) { return id === A.id || id === B.id; });
    }
    log.push(st);
  }
  chk('공사 중인 턴마다(' + (T - 1) + '턴): 시설은 아직 미완성', log.every(function (s) { return !s.done; }), log);
  chk('공사 중: 담당 무장이 쉬는 무장 목록에 없음', log.every(function (s) { return !s.inIdle; }), log);
  chk('공사 중: 징병·출진·이동·다른 공사 모두 불가, 자동 추천에도 안 나옴', log.every(function (s) { return !s.draft && !s.deploy && !s.move && !s.build2 && !s.auto; }), log);
  if (HAS) chk('공사 중: jobOf 가 남은 턴을 알려 줌', (function () { var j = jobOf(A); return j && j.fac === fc && j.left >= 1; })() || fc.done);
  nextTurn(b);
  chk('완공한 턴: 시설 완성', fc.done, { prog: fc.prog, need: fc.need });
  chk('완공한 턴: 담당 무장이 바로 풀려 그 턴에 쓸 수 있음', !A.acted && !B.acted && !busy(A) && !busy(B) && cmdDraft(b, [A.id]).ok);
  chk('완공 기록에 담당 무장 이름', REPORT.some(function (m) { return /완공/.test(m.msg || m.t || JSON.stringify(m)) && JSON.stringify(m).indexOf(A.n) >= 0; }) || !HAS, REPORT.slice(-3));
  // ---------- 2. 공사 중단(철거) ----------
  b = setup(8002); os = idleOfficers(b).sort(function (x, y) { return y.pol - x.pol; }); A = os[0]; B = os[1]; pi = freePlots(b)[0];
  r = cmdDevelop(b, pi, 'barracks', [A.id]);
  var d0 = cmdDemolish(b, pi);
  chk('같은 턴에 중단: 시설 없어지고 무장은 이번 턴 그대로 행동 완료', d0.ok && !b.plots[pi].fac && A.acted && !busy(A) && !cmdDraft(b, [A.id]).ok);
  nextTurn(b); chk('다음 턴에는 다시 쓸 수 있음', !A.acted && cmdDraft(b, [A.id]).ok);
  nextTurn(b);
  pi = freePlots(b)[0]; r = cmdDevelop(b, pi, 'barracks', [A.id, B.id]); nextTurn(b);
  var mid = { busyA: busy(A), actedA: A.acted, actedB: B.acted };
  d0 = cmdDemolish(b, pi);
  chk('다음 턴에 중단: 묶여 있던 무장이 그 자리에서 풀려 바로 쓸 수 있음', (!HAS || (mid.busyA && mid.actedA && mid.actedB)) && d0.ok && !A.acted && !B.acted && cmdDraft(b, [A.id, B.id]).ok, mid);
  // ---------- 3. 함락: 짓다 만 시설은 버려지고 담당은 잡히거나 달아남 ----------
  b = setup(8003); os = idleOfficers(b).sort(function (x, y) { return y.pol - x.pol; }); A = os[0]; pi = freePlots(b)[0];
  r = cmdDevelop(b, pi, 'market', [A.id]);
  var doneBefore = b.plots.filter(function (p) { return p.fac && p.fac.done; }).length;
  var eb = G.bases.filter(function (x) { return x.owner >= 0 && x.owner !== G.player && x.kind === 'city' && idleOfficers(x).length; })[0];
  eb.troops = 20000; eb.w.spear = 9000; G.factions[eb.owner].ap = 255;
  var eu = cmdDeploy(eb, { type: 'spear', ids: [idleOfficers(eb)[0].id], troops: 5000, food: 5000 }).unit;
  captureBase(b, eu);
  chk('함락: 짓다 만 시설은 사라지고 다 지은 시설은 남음', !b.plots[pi].fac && b.plots.filter(function (p) { return p.fac && p.fac.done; }).length === doneBefore && b.owner === eu.f);
  chk('함락: 담당이던 무장의 공사 표시가 지워짐', !busy(A) && !A.job && (A.st === 'captive' || A.loc !== b.id));
  chk('함락 뒤 불변식', invariants().length === 0, invariants().slice(0, 3));
  // ---------- 4. 공격·불로 파괴 ----------
  b = setup(8004); os = idleOfficers(b).sort(function (x, y) { return y.pol - x.pol; }); A = os[0]; pi = freePlots(b)[0];
  r = cmdDevelop(b, pi, 'market', [A.id]);
  b.plots[pi].fac = null;                                // 적의 공격이나 불로 무너진 것과 같다(그 코드도 fac = null)
  chk('파괴된 그 턴: 이번 턴은 이미 일한 것(행동 완료)', A.acted && !busy(A));
  nextTurn(b); chk('파괴된 다음 턴: 풀려서 쓸 수 있음', !A.acted && cmdDraft(b, [A.id]).ok);
  // ---------- 5. 저장했다 불러도 그대로 ----------
  b = setup(8005); os = idleOfficers(b).sort(function (x, y) { return y.pol - x.pol; }); A = os[0]; pi = freePlots(b)[0];
  r = cmdDevelop(b, pi, 'market', [A.id]); nextTurn(b);
  var keepId = A.id, bid = b.id; deserialize(serialize());
  A = off(keepId); b = G.bases[bid];
  chk('저장·불러오기 뒤에도 묶여 있음', A.acted && (!HAS || busy(A)) === HAS && !cmdDraft(b, [A.id]).ok === HAS);
  // ---------- 6. 예전 저장(담당 기록이 없는 공사)은 그대로 진행 ----------
  b = setup(8006); pi = freePlots(b)[0];
  b.plots[pi].fac = { t: 'market', lv: 1, done: false, prog: 0, need: 300, rate: 150, hp: 300 };
  nextTurn(b); nextTurn(b);
  chk('담당 기록이 없는 공사도 완공되고 오류 없음', b.plots[pi].fac && b.plots[pi].fac.done && invariants().length === 0);
  // ---------- 7. 여러 턴 돌려도 불변식 유지(AI 포함) ----------
  b = setup(8007); var bad = [];
  for (var k = 0; k < 40 && !G.over; k++) {
    facBases(G.player).forEach(function (x) { var fp = freePlots(x), io = idleOfficers(x); if (fp.length && io.length && x.gold >= 400 && k % 3 === 0) cmdDevelop(x, fp[0], 'farm', [io[0].id]); });
    endTurn(); var e = invariants(); if (e.length) bad.push([k, e.slice(0, 2)]);
  }
  chk('40턴 동안 불변식 위반 없음(AI도 같은 규칙)', bad.length === 0, bad.slice(0, 3));
  var aiBuilds = 0, aiBusy = 0;
  G.bases.forEach(function (x) { if (x.owner >= 0 && x.owner !== G.player) x.plots.forEach(function (p) { if (p.fac && !p.fac.done) { aiBuilds++; aiBusy += HAS ? builders(p.fac).length : 0; } }); });
  return { res: RES, aiBuilds: aiBuilds, aiBusy: aiBusy, has: HAS };
}
`, ctx);
const out = vm.runInContext('run()', ctx);
let bad = 0;
out.res.forEach(([n, ok, info]) => { if (!ok) bad++; console.log((ok ? '  ok   ' : '  FAIL ') + n + (ok ? '' : '  ← ' + info.slice(0, 400))); });
console.log('\n' + (out.has ? '이 판(담당 무장이 묶임)' : '앞 판(담당 무장 기록 없음)') + ' — 검사 ' + out.res.length + '개 가운데 통과 ' + (out.res.length - bad) + ', 실패 ' + bad + ' · 40턴 뒤 다른 세력의 공사 ' + out.aiBuilds + '곳, 묶인 무장 ' + out.aiBusy + '명');
process.exit(bad ? 1 : 0);
