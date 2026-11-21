// v0.11 — 군사의 헌책과 탐색(규칙 시험).   node tests/cns11.js
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.env.SRC || path.join(__dirname, '..', 'src');
const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array };
vm.createContext(ctx);
for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
let pass = 0, fail = 0;
function ok(c, msg) { if (c) pass++; else { fail++; console.log('  ✗ ' + msg); } }
function run(code) { return JSON.parse(vm.runInContext('JSON.stringify((function () {' + code + '})())', ctx)); }

/* ① 탐색: 미리 정해 둔 결과 — 미리 본 것과 실제가 같다 · 같은 턴의 두 번째는 주사위가 새로 · 찾는 비율 ≈ 성공률 */
const s1 = run(`
  newGame(0, 1); G.aiOnly = false;
  var res = { same: 0, n: 0, found: 0, psum: 0, re: 0, reN: 0, gold: 0, goldN: 0, noHid: 0, noHidFound: 0, adv: 0, advN: 0, cities: 0 };
  var cities = G.bases.filter(function (b) { return b.kind === 'city' && b.owner >= 0; });
  var A = facAdv(0); res.advInt = A.int; res.acc = adviceAcc(A, 0);
  for (var turn = 1; turn <= 400; turn++) {
    G.turn = turn;
    cities.forEach(function (b) {
      var f = b.owner, os = baseOfficers(b); if (!os.length) return;
      os.forEach(function (o) { o.acted = false; }); G.factions[f].ap = 200;
      var hid = hiddenOfficers(b), o = os[turn % os.length], p = searchChance(b, o), pre = searchRoll(b) < p, pre2;
      // 군사(세력 0)의 말: 맞는 비율
      var a = advise(0, searchRoll(b), searchRollA(b), p, 0); res.advN++; if (a.says === pre) res.adv++;
      var k1 = searchKey(b), st = hid.map(function (h) { return h.id; });
      var r = cmdSearch(b, o.id);
      if (!hid.length) { res.noHid++; if (r.found !== undefined) res.noHidFound++; if (r.gold) res.gold++; res.goldN++; return; }
      res.n++; res.psum += p; if ((r.found !== undefined) === pre) res.same++; if (r.found !== undefined) { res.found++; off(r.found).st = 'hidden'; } else { res.goldN++; if (r.gold) res.gold++; }
      if (searchKey(b) !== k1) res.re++; res.reN++;
    });
  }
  return res;`);
console.log('① 탐색 ' + s1.n + '번(숨은 인재가 있는 도시): 미리 본 것과 실제가 같은 것 ' + s1.same + ' · 찾은 비율 ' + (s1.found / s1.n * 100).toFixed(1) + '% (성공률 평균 ' + (s1.psum / s1.n).toFixed(1) + '%) · 재물 ' + (s1.gold / s1.goldN * 100).toFixed(1) + '%(35%)');
ok(s1.same === s1.n, '탐색: 미리 본 결과와 실제가 다르다');
ok(Math.abs(s1.found / s1.n * 100 - s1.psum / s1.n) < 3, '찾는 비율이 성공률과 3%p 넘게 다르다');
ok(Math.abs(s1.gold / s1.goldN * 100 - 35) < 3, '재물을 찾는 비율이 35%와 3%p 넘게 다르다');
ok(s1.re === s1.reN, '같은 턴에 다시 찾으면 주사위가 새로 정해져야 한다');
ok(s1.noHidFound === 0, '숨은 인재가 없는 도시에서 인재를 찾으면 안 된다');
console.log('   군사(지력 ' + s1.advInt + ')의 탐색 조언이 맞은 비율 ' + (s1.adv / s1.advN * 100).toFixed(1) + '% (적중률 ' + s1.acc + '%) — ' + s1.advN + '번');
ok(Math.abs(s1.adv / s1.advN * 100 - s1.acc) < 2.5, '탐색 조언의 적중률이 지력과 2.5%p 넘게 다르다');

/* ② 헌책: 같은 턴에는 같다 · 징병은 이웃이 더 셀 때만 · 지력에 따라 달라진다 */
const s2 = run(`
  newGame(13, 1); G.aiOnly = false;                              // 왕랑(회계 한 곳)
  var f = 13, F = G.factions[f], b = facCities(f)[0], res = {}, A = facAdv(f);
  res.adv = [A.n, A.int];
  function kinds(L) { return L.map(function (c) { return c.kind + ':' + Math.round(c.w); }); }
  var c1 = counsel(f), c2 = counsel(f);
  res.same = JSON.stringify(c1) === JSON.stringify(c2); res.start = kinds(c1.list); res.lvl = c1.lvl;
  res.thr = nbrThreat(b); res.troops = b.troops;
  // 징병: 이웃이 약하면 없다, 이웃이 세면 있다
  var nbs = ADJ[b.id].map(function (e) { return G.bases[e.to]; }).filter(function (x) { return x.owner >= 0 && x.owner !== f; });
  res.nbs = nbs.map(function (x) { return x.n + ' ' + x.troops; });
  if (!hasFac(b, 'barracks')) { b.plots[0].fac = { t: 'barracks', lv: 1, done: true, prog: 0, need: 0, rate: 0, hp: 800 }; }
  b.gold = 3000; b.order = 80; b.food = 90000; b.morale = 80; F.ap = 200; A.int = 100;
  nbs.forEach(function (x) { x.troops = 1000; }); b.troops = 9000;
  res.draftWeak = counselRaw(f).filter(function (c) { return c.kind === 'draft'; }).length;
  nbs[0].troops = 30000; G.peace.until = G.turn + 30;
  var d1 = counselRaw(f).filter(function (c) { return c.kind === 'draft'; })[0]; res.draftLater = d1 ? [Math.round(d1.w), d1.x.soon] : null;
  G.peace.until = G.turn + 3;
  var d2 = counselRaw(f).filter(function (c) { return c.kind === 'draft'; })[0]; res.draftSoon = d2 ? [Math.round(d2.w), d2.x.soon] : null;
  b.food = 100; res.draftNoFood = counselRaw(f).filter(function (c) { return c.kind === 'draft'; }).length; b.food = 90000;
  // 여러 가지가 한꺼번에 있는 도시
  b.order = 35; b.morale = 50; b.troops = 9000; nbs[0].troops = 30000; b.w.spear = 0; b.w.halberd = 0; b.w.bow = 0;
  if (!hasFac(b, 'smithy')) b.plots[1].fac = { t: 'smithy', lv: 1, done: true, prog: 0, need: 0, rate: 0, hp: 800 };
  baseOfficers(b).forEach(function (o, i) { if (!isLord(o) && i === 1) o.loy = 62; });
  var rawAll = counselRaw(f); res.rawKinds = kinds(rawAll.slice().sort(function (x, y) { return y.w - x.w; }));
  // 지력에 따라: 맨 앞이 '정말 가장 급한 것'인 비율, 알아채기 어려운 일(d > 지력)을 놓치는 비율, 말의 자세함
  res.byInt = [50, 65, 80, 95, 100].map(function (iq) {
    A.int = iq; var top = 0, n = 0, seen = 0, hard = 0, lv = -1;
    for (var t = 1; t <= 360; t++) {
      G.turn = t; G.xun = (t - 1) % 3; G.month = Math.floor((t - 1) / 3) % 12 + 1; G.year = 194 + Math.floor((t - 1) / 36);
      G.peace.until = t + 3;
      var cs = counsel(f), raw = counselRaw(f).filter(function (c) { return c.kind !== 'search' && c.kind !== 'recruit' && c.kind !== 'poach'; });
      var L = cs.list.filter(function (c) { return c.kind !== 'search' && c.kind !== 'recruit' && c.kind !== 'poach'; });
      var mx = raw.slice().sort(function (x, y) { return y.w - x.w; })[0];
      n++; if (L.length && mx && L[0].kind === mx.kind) top++;
      raw.forEach(function (c) { if (c.d > iq) { hard++; if (L.some(function (q) { return q.kind === c.kind; })) seen++; } });
      lv = cs.lvl;
    }
    return { iq: iq, lvl: lv, top: Math.round(top / n * 100), miss: hard ? Math.round((1 - seen / hard) * 100) : 0, hard: hard };
  });
  return res;`);
console.log('② 왕랑의 군사 ' + s2.adv.join(' ') + ' · 시작할 때의 헌책 ' + JSON.stringify(s2.start) + ' · 자세함 ' + s2.lvl);
console.log('   이웃: ' + s2.nbs.join(', ') + ' / 회계 병력 ' + s2.troops);
ok(s2.same, '같은 턴에 헌책이 달라진다');
ok(s2.draftWeak === 0, '이웃이 약한데 징병을 권한다');
ok(s2.draftLater && s2.draftLater[0] === 30 && s2.draftLater[1] === false, '보호가 길게 남았을 때의 징병: ' + JSON.stringify(s2.draftLater));
ok(s2.draftSoon && s2.draftSoon[0] >= 58 && s2.draftSoon[1] === true, '보호가 곧 끝날 때의 징병: ' + JSON.stringify(s2.draftSoon));
ok(s2.draftNoFood === 0, '병량이 없는데 징병을 권한다');
console.log('   징병: 이웃이 약할 때 ' + s2.draftWeak + '건 · 이웃 30,000 · 보호 300일 → 무게 ' + s2.draftLater[0] + ' · 보호 30일 → 무게 ' + s2.draftSoon[0]);
console.log('   일이 겹친 도시의 후보(무게순): ' + s2.rawKinds.join(' '));
['patrol', 'train', 'draft', 'reward', 'produce', 'build'].forEach(k => ok(s2.rawKinds.some(x => x.indexOf(k + ':') === 0), '후보에 ' + k + ' 가 없다'));
console.log('   지력 → [자세함, 맨 앞이 정말 가장 급한 것인 턴 %, 어려운 일을 놓친 %]: ' + s2.byInt.map(x => x.iq + ' → [' + x.lvl + ', ' + x.top + '%, ' + (x.hard ? x.miss + '%' : '-') + ']').join('  '));
ok(s2.byInt[4].top === 100 && s2.byInt[4].miss === 0, '지력 100 이면 늘 가장 급한 것부터, 놓치는 것이 없어야 한다');
ok(s2.byInt[0].top < s2.byInt[2].top && s2.byInt[2].top <= s2.byInt[3].top, '지력이 높을수록 가장 급한 것을 먼저 말해야 한다');
ok(s2.byInt[0].lvl === 0 && s2.byInt[1].lvl === 1 && s2.byInt[2].lvl === 2, '말의 자세함의 문턱(65 · 80)');
ok(s2.byInt[0].miss > s2.byInt[1].miss || s2.byInt[1].hard === 0, '지력이 낮을수록 어려운 일을 더 놓쳐야 한다');

/* ③ 숨은 인재의 귀띔: 맞는 비율 ≈ 적중률(달마다), 세력마다 시작할 때 맨 앞에 서는 헌책 */
const s3 = run(`
  var res = { hunch: [], tops: [] };
  [60, 84, 96].forEach(function (iq) {
    newGame(0, 1); G.aiOnly = false; var A = facAdv(0); A.int = iq;
    var cities = G.bases.filter(function (b) { return b.kind === 'city'; }), right = 0, n = 0, said = 0, hidN = 0;
    for (var m = 0; m < 240; m++) {
      G.month = m % 12 + 1; G.year = 194 + Math.floor(m / 12);
      cities.forEach(function (b) { var hid = hiddenOfficers(b).length > 0, knows = omenRoll('adv|hid' + b.id, true) < adviceAcc(A, 0), belief = knows ? hid : !hid; n++; if (belief === hid) right++; if (belief) said++; if (hid) hidN++; });
    }
    res.hunch.push([iq, Math.round(right / n * 1000) / 10, Math.round(said / n * 1000) / 10, Math.round(hidN / n * 1000) / 10]);
  });
  for (var f = 0; f < 19; f++) {
    newGame(f, 1); G.aiOnly = false; var cs = counsel(f), A2 = facAdv(f);
    res.tops.push(G.factions[f].name + '(' + (A2 ? A2.n + ' ' + A2.int : '-') + '): ' + cs.list.slice(0, 3).map(function (c) { return c.kind; }).join(' > ') + (cs.list.length > 3 ? ' … ' + cs.list.length + '건' : ''));
  }
  return res;`);
s3.hunch.forEach(h => { console.log('③ 군사 지력 ' + h[0] + ': 숨은 인재가 있는지 맞힌 비율 ' + h[1] + '% · "있다"고 말한 도시 ' + h[2] + '% (실제로 있는 도시 ' + h[3] + '%)'); ok(Math.abs(h[1] - h[0]) < 3, '귀띔의 적중률이 지력과 3%p 넘게 다르다: ' + h.join(',')); });
console.log('   시작할 때 맨 앞의 헌책(세력 · 군사): ');
s3.tops.forEach(t => console.log('     ' + t));
console.log((fail ? '실패 ' + fail + ' · ' : '') + '통과 ' + pass);
process.exit(fail ? 1 : 0);
