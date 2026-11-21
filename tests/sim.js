// 헤드리스 시뮬레이션: AI 대 AI로 돌리며 불변식 검사
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.env.SRC || path.join(__dirname, '..', 'src');   // SRC=<폴더> 로 다른 판의 규칙을 돌려 견줄 수 있다
const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat };
vm.createContext(ctx);
for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
const turns = +(process.argv[2] || 360), seed = +(process.argv[3] || 12345), verbose = process.argv[4] === 'v';
vm.runInContext(`
function invariants() {
  var errs = [], i, j;
  function num(v, what) { if (typeof v !== 'number' || v !== v || !isFinite(v)) errs.push('NaN ' + what + '=' + v); }
  for (i = 0; i < G.bases.length; i++) {
    var b = G.bases[i];
    ['gold','food','troops','morale','order','dur'].forEach(function (k) { num(b[k], b.n + '.' + k); if (b[k] < 0) errs.push('neg ' + b.n + '.' + k + '=' + b[k]); });
    for (var k in b.w) { num(b.w[k], b.n + '.w.' + k); if (b.w[k] < 0) errs.push('neg weapon ' + b.n + ' ' + k); }
    if (b.owner >= 0 && !G.factions[b.owner].alive) errs.push('base of dead faction ' + b.n);
    for (j = 0; j < b.captives.length; j++) { var cp = G.officers[b.captives[j]]; if (cp.st !== 'captive' || cp.loc !== b.id) errs.push('captive mismatch ' + cp.n + ' st=' + cp.st); if (cp.capF !== b.owner) errs.push('captive holder mismatch ' + cp.n + ' capF=' + cp.capF + ' owner=' + b.owner + ' @' + b.n); }
    if (UAT[K(b.c, b.r)]) errs.push('unit on base hex ' + b.n);
  }
  var seen = {};
  for (i = 0; i < G.units.length; i++) {
    var u = G.units[i];
    ['troops','morale','food','gold','mp','c','r'].forEach(function (k) { num(u[k], 'unit' + u.id + '.' + k); });
    if (u.troops <= 0) errs.push('unit with no troops ' + u.id);
    if (UAT[K(u.c, u.r)] !== u) errs.push('UAT mismatch unit ' + u.id);
    if (seen[K(u.c, u.r)]) errs.push('two units on one hex'); seen[K(u.c, u.r)] = 1;
    var t = terr(u.c, u.r); if (t === 'm' || t === 's' || t === 'x') errs.push('unit on impassable ' + t);
    // (v0.12: 시설 칸에 설 수 있다 — 'unit on facility' 검사는 없앴다)
    if (!G.factions[u.f].alive) errs.push('unit of dead faction');
    if (!u.off.length) errs.push('unit without officers');
    for (j = 0; j < u.off.length; j++) { var o = G.officers[u.off[j]]; if (o.unit !== u.id || o.st !== 'active' || o.f !== u.f) errs.push('unit officer mismatch ' + o.n + ' st=' + o.st + ' unit=' + o.unit + ' f=' + o.f + '/' + u.f); }
  }
  // 공사 담당(v0.7.1): 짓는 중인 시설의 담당 무장은 그 거점에 있고 묶여 있어야(행동 완료) 한다. 한 무장이 두 공사를 맡지 않는다
  if (typeof jobOf === 'function') {
    var jobs = {};
    for (i = 0; i < G.bases.length; i++) {
      var jb = G.bases[i];
      for (j = 0; j < jb.plots.length; j++) {
        var jf = jb.plots[j].fac;
        if (!jf || jf.done || !jf.by) continue;
        for (var q = 0; q < jf.by.length; q++) {
          var bo = G.officers[jf.by[q]], jj = jobOf(bo);
          if (!jj || jj.fac !== jf) continue;                      // 떠난 담당(잡혔거나 달아남)은 세지 않는다
          if (jobs[bo.id]) errs.push('builder on two jobs ' + bo.n); jobs[bo.id] = 1;
          if (!bo.acted) errs.push('builder not busy ' + bo.n + ' @' + jb.n);
          if (bo.st !== 'active' || bo.loc !== jb.id || bo.unit !== null || bo.f !== jb.owner) errs.push('builder misplaced ' + bo.n + ' @' + jb.n);
        }
      }
    }
    for (i = 0; i < G.officers.length; i++) { var po = G.officers[i]; if (po.job && jobOf(po) && !jobs[po.id]) errs.push('job without facility ' + po.n); }
  }
  for (i = 0; i < G.officers.length; i++) {
    var p = G.officers[i];
    if (p.st === 'active') {
      if (p.f < 0 || !G.factions[p.f].alive) errs.push('active officer w/o faction ' + p.n);
      else if (p.unit !== null) { if (!UMAP[p.unit] || UMAP[p.unit].off.indexOf(p.id) < 0) errs.push('officer unit dangling ' + p.n); }
      else if (G.bases[p.loc].owner !== p.f) errs.push('officer in foreign base ' + p.n + ' @' + G.bases[p.loc].n + ' owner=' + G.bases[p.loc].owner + ' f=' + p.f);
    } else if (p.st === 'free') { if (p.f !== -1) errs.push('free officer with faction ' + p.n); if (p.unit !== null) errs.push('free officer in unit ' + p.n); if (G.bases[p.loc].kind !== 'city') errs.push('free officer at gate ' + p.n); }
    else if (p.st === 'captive') { if (G.bases[p.loc].captives.indexOf(p.id) < 0) errs.push('captive not listed ' + p.n); }
    else if (p.st === 'travel') { if (p.f < 0 || !G.factions[p.f].alive) errs.push('traveler w/o faction ' + p.n); }
    num(p.loy, p.n + '.loy'); num(p.merit, p.n + '.merit'); if (p.loy < 0 || p.loy > 100) errs.push('loyalty out of range ' + p.n + ' ' + p.loy);
  }
  for (i = 0; i < G.factions.length; i++) {
    var F = G.factions[i], nb = facBases(i).length;
    num(F.ap, F.name + '.ap');
    if (F.alive !== (nb > 0)) errs.push('alive mismatch ' + F.name + ' bases=' + nb);
    if (F.alive) { var L = G.officers[F.lord]; if (L.f !== i || (L.st !== 'active' && L.st !== 'travel')) errs.push('lord invalid ' + F.name + ' st=' + L.st + ' f=' + L.f); }
    // 군사(v0.9): 번호가 있으면 있는 무장이어야 하고 군주가 아니어야 한다. facAdv 가 돌려주는 사람은 그 세력의 무장이어야 한다
    if (typeof facAdv === 'function' && F.alive) {
      if (F.adv !== undefined && F.adv >= 0 && !G.officers[F.adv]) errs.push('advisor id invalid ' + F.name + ' ' + F.adv);
      if (F.adv === F.lord) errs.push('lord is advisor ' + F.name);
      var A = facAdv(i); if (A && (A.f !== i || (A.st !== 'active' && A.st !== 'travel'))) errs.push('advisor not ours ' + F.name + ' ' + A.n);
    }
  }
  return errs;
}
function summary() {
  var s = [];
  G.factions.forEach(function (F) { if (!F.alive) return; var cs = facCities(F.id), t = 0; facBases(F.id).forEach(function (b) { t += b.troops; }); facUnits(F.id).forEach(function (u) { t += u.troops; }); s.push(F.name + ':' + cs.length + '성/' + Math.round(t / 1000) + '천/' + facOfficers(F.id).length + '명'); });
  return s.join(' ');
}
`, ctx);
ctx.newGame(0, seed); ctx.G.aiOnly = true;
let bad = 0;
const t0 = Date.now();
for (let t = 0; t < turns; t++) {
  try { ctx.endTurn(); } catch (e) { console.log('EXCEPTION turn', t, e.stack); process.exit(1); }
  const errs = ctx.invariants();
  if (errs.length) { console.log('turn', t, ctx.dateStr(), 'INVARIANT', errs.slice(0, 8)); if (++bad > 3) process.exit(1); }
  if (verbose && t % 36 === 35) console.log(ctx.dateStr(), '|', ctx.summary(), '| units', ctx.G.units.length);
  if (ctx.G.over) { console.log('over', ctx.G.over, 'turn', t); break; }
}
console.log('done', turns, 'turns in', Date.now() - t0, 'ms |', ctx.dateStr());
console.log(ctx.summary());
console.log('alive', ctx.G.factions.filter(f => f.alive).length, 'units', ctx.G.units.length, 'neutral cities', ctx.G.bases.filter(b => b.owner < 0 && b.kind === 'city').length);
