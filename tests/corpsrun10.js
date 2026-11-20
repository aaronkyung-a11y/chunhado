// v0.10 — 군단을 두고 오래 돌려 본다(규칙이 어긋나거나 멈추지 않는가).
//   node tests/corpsrun10.js [턴=100]
// 방법: 여러 세력 · 씨앗으로 시작해, 군주가 있는 도시만 직할로 두고 나머지를 군단 한둘에 맡긴다. 직할은 아무 명령도 내리지 않는다(턴만 넘긴다).
//       턴마다 제멋대로(판의 주사위와 따로 굴리는 주사위로) 방침 바꾸기 · 거점 넣고 빼기 · 군단장 바꾸기 · 부대를 직할로 · 해산하고 다시 만들기를 섞고,
//       턴이 끝날 때마다 아래를 검사한다:
//         군단 표시(b.corps · u.corps)는 모두 살아 있는 군단을 가리키고 내 것에만 붙어 있다 / 군단마다 거점이 있다 / 군단장은 비었거나 자격이 있다
//         방침과 목표가 맞는다(공격 = 남의 거점, 지원 = 군단 밖의 내 거점) / 행동력은 0~255 / 차례가 끝나면 좁히기(AISCOPE)와 장부(JOT)는 닫혀 있다
//         부대의 무장은 그 부대에만 있다 / 병력 · 금 · 병량에 음수 · NaN 이 없다 / 직할 거점 + 군단 거점 = 내 거점
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.env.SRC || path.join(__dirname, '..', 'src');
const TURNS = +(process.argv[2] || 100);
function run(fac, seed) {
  const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat };
  vm.createContext(ctx);
  for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
  ctx.ARG = { fac, seed, TURNS };
  return vm.runInContext(`(function () {
    var R = ARG.seed * 7919 + 13;
    function rr() { R = (Math.imul(R, 1103515245) + 12345) & 0x7fffffff; return R / 0x7fffffff; }
    function pickOf(a) { return a[Math.floor(rr() * a.length)]; }
    var bad = [], stats = { turns: 0, made: 0, dir: 0, moved: 0, lead: 0, took: 0, disband: 0, captured: 0, lost: 0, notes: 0, deployed: 0, maxCorps: 0, atkWon: 0 };
    function fail(m) { if (bad.length < 12) bad.push('턴 ' + G.turn + ': ' + m); }
    function check() {
      var f = G.player, cs = corpsAll(), ids = {}, i;
      cs.forEach(function (c) { ids[c.id] = 1; });
      G.bases.forEach(function (b) {
        if (b.corps && (b.owner !== f || !ids[b.corps])) fail(b.n + ' 의 군단 표시가 어긋남 ' + b.corps + ' 주인 ' + b.owner);
        if (!(b.troops >= 0) || !(b.gold >= 0) || !(b.food >= 0)) fail(b.n + ' 수치 ' + [b.troops, b.gold, b.food]);
      });
      G.units.forEach(function (u) {
        if (u.corps && (u.f !== f || !ids[u.corps])) fail(uName(u) + ' 의 군단 표시가 어긋남');
        if (!(u.troops > 0)) fail(uName(u) + ' 병력 ' + u.troops);
        u.off.forEach(function (id) { var o = off(id); if (o.unit !== u.id) fail(o.n + ' 가 부대 밖에 있음'); });
      });
      cs.forEach(function (c) {
        var bs = corpsBases(c);
        if (!bs.length) fail(corpsName(c) + ' 에 거점이 없음');
        if (c.lead >= 0 && !corpsLeadOk(c, off(c.lead))) fail(corpsName(c) + ' 군단장 자격 없음 ' + off(c.lead).n);
        if (c.lead < 0 && corpsLeadCands(c).length) fail(corpsName(c) + ' 군단장 자리가 비었는데 후보가 있음');
        if (!(c.ap >= 0 && c.ap <= 255)) fail(corpsName(c) + ' 행동력 ' + c.ap);
        if (!CORPS_DIR[c.dir]) fail(corpsName(c) + ' 방침 ' + c.dir);
        var T = c.target >= 0 ? G.bases[c.target] : null;
        if (c.dir === 'atk' && (!T || T.owner === f)) fail(corpsName(c) + ' 공격 목표가 내 거점이거나 없음');
        if (c.dir === 'sup' && (!T || T.owner !== f || T.corps === c.id)) fail(corpsName(c) + ' 지원할 곳이 어긋남');
        if ((c.dir === 'dev' || c.dir === 'arm') && c.target !== -1) fail(corpsName(c) + ' 목표가 남아 있음');
      });
      if (directBases(f).length + cs.reduce(function (a, c) { return a + corpsBases(c).length; }, 0) !== facBases(f).length) fail('직할 + 군단 ≠ 내 거점');
      if (AISCOPE !== null || JOT !== null) fail('차례가 끝났는데 좁히기나 장부가 열려 있음');
      var F = G.factions[f]; if (!(F.ap >= 0 && F.ap <= 255)) fail('직할 행동력 ' + F.ap);
      stats.maxCorps = Math.max(stats.maxCorps, cs.length);
    }
    function nearTargets(c) { var b0 = corpsBases(c)[0]; return G.bases.filter(function (b) { return b.owner !== G.player; }).sort(function (x, y) { return hdist(b0.c, b0.r, x.c, x.r) - hdist(b0.c, b0.r, y.c, y.r); }).slice(0, 5); }
    function meddle() {
      var f = G.player, cs = corpsAll(), d = directBases(f), lordLoc = off(G.factions[f].lord).unit === null ? off(G.factions[f].lord).loc : -1, x = rr();
      var free = d.filter(function (b) { return b.id !== lordLoc; });
      if (free.length && (cs.length === 0 || (cs.length < 2 && rr() < 0.5))) {             // 새 군단
        var take = free.filter(function () { return rr() < 0.7; }); if (!take.length) take = [free[0]];
        var r = corpsCreate(take.map(function (b) { return b.id; })); if (r.ok) stats.made++;
        return;
      }
      if (!cs.length) return;
      var c = pickOf(cs);
      if (x < 0.30) {                                                                      // 방침
        var k = pickOf(['dev', 'arm', 'atk', 'atk', 'sup']), t = -1;
        if (k === 'atk') t = pickOf(nearTargets(c)).id;
        if (k === 'sup') { var outs = facBases(f).filter(function (b) { return b.corps !== c.id; }); if (!outs.length) return; t = pickOf(outs).id; }
        if (corpsSetDir(c, k, t).ok) stats.dir++;
      } else if (x < 0.40 && free.length) { if (corpsAssign(c, pickOf(free).id).ok) stats.moved++; }
      else if (x < 0.46 && corpsBases(c).length > 1) { if (corpsRelease(pickOf(corpsBases(c)).id).ok) stats.moved++; }
      else if (x < 0.54) { var lc = corpsLeadCands(c); if (lc.length && corpsSetLead(c, pickOf(lc).id).ok) stats.lead++; }
      else if (x < 0.60) { var us = corpsUnits(c); if (us.length && corpsTakeUnit(pickOf(us)).ok) stats.took++; }
      else if (x < 0.63) { corpsDisband(c); stats.disband++; }
    }
    newGame(ARG.fac, ARG.seed);
    var name = G.factions[G.player].name, nb0 = facBases(G.player).length;
    try {
      for (var t = 0; t < ARG.TURNS && !G.over; t++) {
        if (t % 2 === 0) meddle();
        corpsFix();
        var before = {}; G.bases.forEach(function (b) { before[b.id] = b.owner === G.player ? (b.corps || 0) + 1 : 0; });
        var atk = corpsAll().filter(function (c) { return c.dir === 'atk'; }).map(function (c) { return c.target; });
        // 직할 부대(되돌려 받은 것)는 그대로 두면 굶으므로 가까운 내 거점으로 돌려보낸다(AI 의 귀환을 빌린다)
        directUnits(G.player).forEach(function (u) { if (!u.done) { u.ai = { mode: 'return' }; aiUnitAct(u); u.ai = null; } });
        endTurn();
        stats.turns++;
        G.bases.forEach(function (b) { var now = b.owner === G.player ? (b.corps || 0) + 1 : 0; if (!before[b.id] && now > 1) stats.captured++; if (before[b.id] > 1 && !now) stats.lost++; if (!before[b.id] && now && atk.indexOf(b.id) >= 0) stats.atkWon++; });
        corpsAll().forEach(function (c) { if (c.note && c.note.t === G.turn - 1 && c.note.n) stats.notes++; if (c.note && c.note.t === G.turn - 1 && /출진/.test(c.note.s)) stats.deployed++; });
        check();
      }
    } catch (e) { bad.push('턴 ' + G.turn + ' 예외: ' + (e && e.stack ? e.stack.split('\\n').slice(0, 3).join(' | ') : e)); }
    return { name: name, seed: ARG.seed, over: G.over, bases: [nb0, G.factions[G.player].alive ? facBases(G.player).length : 0], stats: stats, bad: bad };
  })()`, ctx);
}
let fails = 0;
for (const [fac, seed] of [[4, 1], [4, 2], [14, 3], [15, 4], [18, 5], [9, 6]]) {
  const r = run(fac, seed), s = r.stats;
  console.log((r.name + '(씨앗 ' + r.seed + ')').padEnd(12) + ' ' + s.turns + '턴' + (r.over ? '(' + r.over + ')' : '') + ' | 거점 ' + r.bases[0] + ' → ' + r.bases[1] + ' | 군단 만들기 ' + s.made + ' · 방침 ' + s.dir + ' · 거점 넣고 빼기 ' + s.moved + ' · 군단장 ' + s.lead + ' · 부대 직할 ' + s.took + ' · 해산 ' + s.disband +
    ' | 군단이 일한 턴 ' + s.notes + ' · 출진한 턴 ' + s.deployed + ' · 차지한 거점 ' + s.captured + '(공격 목표 ' + s.atkWon + ') · 잃은 거점 ' + s.lost + ' | 어긋남 ' + r.bad.length);
  if (r.bad.length) { fails += r.bad.length; console.log('   ' + r.bad.join('\n   ')); }
}
console.log(fails ? '어긋남 ' + fails + '건' : '어긋남 없음');
process.exit(fails ? 1 : 0);
