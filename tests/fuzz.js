// 플레이어 명령 무작위 퍼징: 규칙 엔진의 모든 명령을 마구 눌러 본다
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = path.join(__dirname, '..', 'src');
const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat };
vm.createContext(ctx);
for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
vm.runInContext(fs.readFileSync(path.join(__dirname, 'sim.js'), 'utf8').match(/function invariants\(\)[\s\S]*?\n}\nfunction summary/)[0].replace(/\nfunction summary$/, ''), ctx);
const turns = +(process.argv[2] || 200), seed = +(process.argv[3] || 1), fac = +(process.argv[4] || 0);
vm.runInContext(`
var R = ${seed} * 7919 + 13;
function fr() { R = (R * 1103515245 + 12345) & 0x7fffffff; return R / 0x7fffffff; }
function fpick(a) { return a[Math.floor(fr() * a.length)]; }
function fsome(a, n) { var b = a.slice(), out = []; while (b.length && out.length < n) out.push(b.splice(Math.floor(fr() * b.length), 1)[0]); return out; }
var STAT = {};
/* v0.8.1 초반 보호 감시: 보호 기간에, 플레이어가 먼저 치지 않은 세력이 플레이어의 거점·시설을 치면(또는 빼앗으면) 어김 */
var PV = { viol: 0, hits: 0, first: 0 };
var _ua0 = unitAttack0; unitAttack0 = function (u, t) {
  var mine = (t.kind === 'base' || t.kind === 'fac') && t.b && t.b.owner === G.player && u.f !== G.player;
  var prot = mine && G.peace && G.turn < G.peace.until && !G.peace.broken[u.f];
  var r = _ua0(u, t);
  if (r && r.ok && mine) { PV.hits++; if (!PV.first) PV.first = G.turn; if (prot) PV.viol++; }
  return r;
};
var _cb0 = captureBase; captureBase = function (b, u) { if (b.owner === G.player && u && u.f !== G.player && G.peace && G.turn < G.peace.until && !G.peace.broken[u.f]) PV.viol++; return _cb0(b, u); };
function note(k, r) { STAT[k] = STAT[k] || [0, 0]; STAT[k][r && r.ok ? 0 : 1]++; }
function fuzzTurn() {
  var f = G.player, i;
  facBases(f).forEach(function (b) {
    for (var n = 0; n < 6; n++) {
      var idle = idleOfficers(b); if (!idle.length) break;
      var os = fsome(idle, 1 + Math.floor(fr() * 3)).map(function (o) { return o.id; });
      var k = Math.floor(fr() * 16);
      // 자동 추천: 고른 무장이 모두 대기 중인 무장이어야 한다
      var ak = fpick(['develop', 'draft', 'patrol', 'train', 'search', 'merge', 'produce', 'recruit']), actx = null;
      if (ak === 'produce') actx = { kind: fpick(['spear', 'halberd', 'bow', 'horse', 'ram']) };
      if (ak === 'recruit') { var rts = freeOfficers(b).concat(baseCaptives(b)); actx = rts.length ? { target: fpick(rts) } : null; }
      if (ak !== 'recruit' || actx) {
        var ao = autoPick(ak, b, actx, 1 + Math.floor(fr() * 3));
        note('auto_' + ak, { ok: ao.length > 0 && ao.length <= 3 && ao.every(function (id) { return idle.some(function (o) { return o.id === id; }); }) });
        if (ao.length && fr() < 0.4 && ak !== 'recruit' && ak !== 'search' && ak !== 'merge') os = ao;
      }
      if (k === 0) { var free = []; b.plots.forEach(function (p, pi) { if (!p.fac) free.push(pi); }); if (free.length) note('develop', cmdDevelop(b, fpick(free), fpick(FAC_ORDER), os)); }
      else if (k === 1) note('draft', cmdDraft(b, os));
      else if (k === 2) note('patrol', cmdPatrol(b, os));
      else if (k === 3) note('train', cmdTrain(b, os));
      else if (k === 4) note('produce', cmdProduce(b, fpick(['spear', 'halberd', 'bow', 'horse', 'ram']), os));
      else if (k === 5) note('trade', cmdTrade(b, fpick(['buy', 'sell']), Math.floor(fr() * 500)));
      else if (k === 6) note('search', cmdSearch(b, os[0]));
      else if (k === 7) { var ts = freeOfficers(b).concat(baseCaptives(b)); if (ts.length) note('recruit', cmdRecruit(b, os[0], fpick(ts).id)); }
      else if (k === 8) { var bo = baseOfficers(b); note('reward', cmdReward(b, fpick(bo).id)); }
      else if (k === 9) { var ds = facBases(f).filter(function (x) { return x.id !== b.id; }); if (ds.length) note('move', cmdMoveOfficers(b, os, fpick(ds).id)); }
      else if (k === 10 && b.captives.length) note('captive', cmdCaptive(b, fpick(b.captives), fpick(['release', 'execute', 'release'])));
      else if (k === 11) { for (var pi = 0; pi < b.plots.length; pi++) { var c = mergeCandidates(b, pi); if (c.length) { note('merge', cmdMerge(b, pi, c[0], [os[0]])); break; } } }
      else if (k === 12 && fr() < 0.1) { var has = []; b.plots.forEach(function (p, pi2) { if (p.fac) has.push(pi2); }); if (has.length) note('demolish', cmdDemolish(b, fpick(has))); }
      else if (k === 13 || k === 14) { var t = fpick(COMBAT_TYPES), tr = Math.floor(fr() * 70) * 100; if (fr() < 0.5) { os = autoTeam(b, t, tr); note('autoTeam', { ok: os.length >= 1 && os.length <= 3 }); } var dsp = { type: t, ids: os, troops: tr, food: Math.floor(fr() * 4000) }; if (fr() < 0.5) { var db = fpick(G.bases), eta = deployEta(b, t, os, K(db.c, db.r)); if (!(eta >= 0)) throw new Error('deployEta ' + eta); note('deployEta', { ok: eta > 0 }); dsp.toward = db; dsp.dest = K(db.c, db.r); } var dr = cmdDeploy(b, dsp); note('deploy', dr); if (dr.ok && dsp.dest !== undefined) { if (dr.unit.dest !== dsp.dest) throw new Error('dest not set'); var m1 = unitMarch(dr.unit); note('deployMarch', m1 || { ok: true }); if (m1 && !m1.ok && m1.front === undefined && !m1.lost) throw new Error('bad march result'); } }
      else if (k === 15) note('trans', cmdDeploy(b, { type: 'trans', ids: [os[0]], troops: 100 + Math.floor(fr() * 20) * 100, food: Math.floor(fr() * 3000), gold: Math.floor(fr() * 300), cargo: { spear: Math.floor(fr() * 5) * 100, halberd: 0, bow: Math.floor(fr() * 3) * 100, horse: 0, ram: 0 } }));
    }
  });
  facUnits(f).forEach(function (u) { if (alive(u) && !u.done && u.dest >= 0) { var mr = unitMarch(u); note('march', mr || { ok: true }); } });
  facUnits(f).forEach(function (u) {
    if (!alive(u) || u.done) return;
    if (fr() < 0.25) {                                   // 행군 목적지: 아무 거점이나 근처 아무 칸
      var tb = fpick(G.bases), dk = fr() < 0.7 ? K(tb.c, tb.r) : K(clamp(u.c + Math.floor(fr() * 40) - 20, 0, W - 1), clamp(u.r + Math.floor(fr() * 40) - 20, 0, H - 1));
      var mp = marchPath(u, dk);
      if (mp) { var mt = marchTurns(u, mp); if (!(mt >= 1)) throw new Error('marchTurns ' + mt); u.dest = dk; note('marchSet', unitMarch(u) || { ok: true }); }
      else note('marchNoPath', { ok: true });
      if (!alive(u) || u.done) return;
    }
    for (var step = 0; step < 3 && alive(u) && !u.done; step++) {
      var rc = unitReach(u), stops = Object.keys(rc.stop);
      if (stops.length && fr() < 0.8) { var k = +fpick(stops), c = k % W, r = (k - c) / W; note('moveU', unitMove(u, c, r, rc)); if (alive(u) && fr() < 0.1) note('undo', { ok: unitUndoMove(u) }); }
      if (!alive(u) || u.done) break;
      var ats = attackTargets(u), q = fr();
      if (q < 0.45 && ats.length) { note('attack', unitAttack(u, fpick(ats))); break; }
      if (q < 0.7) { var tl = tacticList(u); if (tl.length) { var tac = fpick(tl), tt = tacticTargets(u, tac); if (tt.length) { note('tactic', unitTactic(u, tac, fpick(tt))); break; } } }
      if (q < 0.9) { var pl = fpick(PLOYS), pt = ployTargets(u, pl); if (pt.length) { note('ploy', unitPloy(u, pl, fpick(pt))); break; } }
    }
    if (alive(u) && !u.done && fr() < 0.7) unitWait(u);
  });
}
`, ctx);
ctx.newGame(fac, seed);
let bad = 0;
for (let t = 0; t < turns; t++) {
  try { ctx.fuzzTurn(); let e1 = ctx.invariants(); if (e1.length) { console.log('turn', t, 'after fuzz', e1.slice(0, 6)); if (++bad > 3) process.exit(1); }
        const s = ctx.serialize(); if (t % 25 === 0) { ctx.deserialize(s); }
        ctx.endTurn(); } catch (e) { console.log('EXCEPTION turn', t, e.stack); process.exit(1); }
  const errs = ctx.invariants();
  if (errs.length) { console.log('turn', t, ctx.dateStr(), 'INVARIANT', errs.slice(0, 6)); if (++bad > 3) process.exit(1); }
  if (ctx.G.over) { console.log('over', ctx.G.over, 'turn', t); break; }
}
if (ctx.G.peace) console.log('peace: until turn', ctx.G.peace.until, '| 먼저 친 세력', Object.keys(ctx.G.peace.broken).map(k => ctx.G.factions[+k].name).join('·') || '없음', '| 내 거점·시설이 처음 맞은 턴', ctx.PV.first || '-', '| 맞은 횟수', ctx.PV.hits, '| 보호 어김', ctx.PV.viol);
if (ctx.PV.viol) { console.log('FAIL: 보호 중인 거점·시설이 공격받음'); process.exit(1); }
console.log('fuzz ok', ctx.dateStr(), JSON.stringify(ctx.STAT), 'save bytes', ctx.serialize().length);
