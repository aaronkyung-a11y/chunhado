# v0.7.1 — 건설을 맡은 무장은 완공될 때까지 묶인다(다른 명령·출진·이동 불가)
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:90])
    return s.replace(a, b)
p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()

# 1) 담당 무장 추적
s = rep(s, """function idleOfficers(b) { return baseOfficers(b).filter(function (o) { return !o.acted; }); }""",
"""function idleOfficers(b) { return baseOfficers(b).filter(function (o) { return !o.acted; }); }
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
}""")

# 2) 턴이 바뀌어도 공사 중인 무장은 풀리지 않는다
s = rep(s, """    if (o.st === 'active') o.acted = false;
    else if (o.st === 'travel') {""", """    if (o.st === 'active') o.acted = !!jobOf(o);                  // 공사를 맡은 무장은 완공될 때까지 쉬지 못한다
    else if (o.st === 'travel') {""")

# 3) 완공하면 담당 무장이 풀려 그 턴부터 다시 쓸 수 있다
s = rep(s, """      if (fc && !fc.done) { fc.prog += fc.rate; if (fc.prog >= fc.need) { fc.done = true; fc.hp = FAC_HP; if (f === G.player) logMsg(b.n + '에 ' + FAC[fc.t].name + ' 완공', b.plots[j].c, b.plots[j].r, f, 1); } }""",
"""      if (fc && !fc.done) {
        fc.prog += fc.rate;
        if (fc.prog >= fc.need) {
          var who = builders(fc).map(function (x) { return x.n; });
          freeBuilders(fc, false); fc.done = true; fc.hp = FAC_HP;
          if (f === G.player) logMsg(b.n + '에 ' + FAC[fc.t].name + ' 완공' + (who.length ? ' — ' + who.join('·') + ' 복귀' : ''), b.plots[j].c, b.plots[j].r, f, 1);
        }
      }""")

# 4) 착공: 담당 무장을 시설에 적어 둔다
s = rep(s, """  p.fac = { t: type, lv: 1, done: false, prog: 0, need: F.build, rate: rate, hp: 300 };
  markActed(os, 30);
  return { ok: true, turns: Math.ceil(F.build / rate) };""", """  p.fac = { t: type, lv: 1, done: false, prog: 0, need: F.build, rate: rate, hp: 300, by: os.map(function (o) { return o.id; }), t0: G.turn };
  for (var i = 0; i < os.length; i++) os[i].job = { b: b.id, i: pi };
  markActed(os, 30);
  return { ok: true, turns: Math.ceil(F.build / rate) };""")

# 5) 철거(공사 중단): 담당 무장이 풀린다. 이번 턴에 착공한 것이면 이번 턴은 이미 일한 것
s = rep(s, """function cmdDemolish(b, pi) { if (!b.plots[pi] || !b.plots[pi].fac) return ERR('시설이 없습니다'); b.plots[pi].fac = null; return { ok: true }; }""",
"""function cmdDemolish(b, pi) {
  if (!b.plots[pi] || !b.plots[pi].fac) return ERR('시설이 없습니다');
  var f = b.plots[pi].fac, freed = builders(f).map(function (o) { return o.id; });
  if (!f.done) freeBuilders(f, f.t0 === G.turn);
  b.plots[pi].fac = null;
  return { ok: true, freed: freed };
}""")

# 6) 함락: 짓다 만 시설은 버려지고, 담당 무장은 다른 무장들과 같이 잡히거나 달아난다
s = rep(s, """function captureBase(b, u) {
  var old = b.owner, i;
  if (old >= 0) {""", """function captureBase(b, u) {
  var old = b.owner, i;
  for (i = 0; i < b.plots.length; i++) { var uf = b.plots[i].fac; if (uf && !uf.done) { freeBuilders(uf, true); b.plots[i].fac = null; } }   // 짓다 만 시설은 버려진다
  if (old >= 0) {""")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------- AI: 묶이는 것을 감안해 공사를 맡긴다 ----------
p = 'src/ai.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, """    // 개발
    for (var rep = 0; rep < 2; rep++) {
      os = idle(); if (!os.length || F.ap < AP.develop + 10) break;
      var type = aiPickFacility(b), pi = aiPickPlot(b, type);
      if (pi < 0 || b.gold < FAC[type].cost + (threatened ? 400 : 100)) break;
      os.sort(function (a, c2) { return c2.pol - a.pol; });
      cmdDevelop(b, pi, type, os.slice(0, Math.min(2, os.length)).map(function (x) { return x.id; }));
    }""", """    // 개발 — 공사를 맡은 무장은 완공까지 묶이므로: 적이 가까우면 새로 짓지 않고, 싸움에 가장 쓸모 있는 둘은 남겨 두고, 한꺼번에 벌이는 공사 수를 줄인다
    var nOff = baseOfficers(b).length, building = b.plots.filter(function (p) { return p.fac && !p.fac.done; }).length;
    var keep = nOff > 3 ? baseOfficers(b).sort(function (a, c2) { return aiMilScore(c2) - aiMilScore(a); }).slice(0, 2) : [];
    for (var rep = 0; rep < 2 && !threatened; rep++) {
      if (building >= (nOff <= 4 ? 1 : 2)) break;
      os = idle().filter(function (x) { return keep.indexOf(x) < 0; }); if (!os.length || F.ap < AP.develop + 10) break;
      var type = aiPickFacility(b), pi = aiPickPlot(b, type);
      if (pi < 0 || b.gold < FAC[type].cost + 100) break;
      os.sort(function (a, c2) { return c2.pol - a.pol; });
      var rdev = cmdDevelop(b, pi, type, os.slice(0, Math.min(nOff <= 5 ? 1 : 2, os.length)).map(function (x) { return x.id; }));
      if (rdev.ok) building++; else break;
    }""")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/data.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "var GAME_VERSION = 'v0.7';", "var GAME_VERSION = 'v0.7.1';")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
