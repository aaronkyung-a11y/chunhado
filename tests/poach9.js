// v0.9 다른 세력 무장 등용 — 얼마나 자주 일어나는가를 잰다
//   node tests/poach9.js ai [턴=108] [씨앗=1] [플레이어 자리=0]       AI끼리 돌려 해마다 권한 횟수·넘어간 횟수, 세력별 무장 수
//   node tests/poach9.js player [세력=0] [씨앗=1] [달 수=12]         사람이 작정하고 빼 가는 경우: 적중률 100% 군사를 두고, 달마다 '응하게 되어 있는' 이웃 무장에게만 권한다(그 밖에는 아무것도 안 함)
//   SRC=<폴더> 로 다른 판을 잼
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.env.SRC || path.join(__dirname, '..', 'src'), mode = process.argv[2] || 'ai';
const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array };
vm.createContext(ctx);
for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
if (mode === 'ai') {
  const turns = +(process.argv[3] || 108), seed = +(process.argv[4] || 1), fac = +(process.argv[5] || 0);
  vm.runInContext(`var PC = { ask: 0, ok: 0, fromP: 0, askP: 0, byYear: {}, pair: {}, ps: [] };
    var _cr = cmdRecruit; cmdRecruit = function (b, id, tid) { var t = off(tid), far = canPoach(b, t), tf = t ? t.f : -1, y = G.year; var r = _cr(b, id, tid);
      if (r && r.ok && far) { PC.ask++; PC.ps.push(r.p); var Y = PC.byYear[y] = PC.byYear[y] || [0, 0]; Y[0]++; if (tf === G.player) PC.askP++; if (r.joined) { PC.ok++; Y[1]++; if (tf === G.player) PC.fromP++; var k = facName(b.owner) + '←' + facName(tf); PC.pair[k] = (PC.pair[k] || 0) + 1; } } return r; };`, ctx);
  ctx.newGame(fac, seed); ctx.G.aiOnly = true;
  const n0 = ctx.G.factions.map((F, f) => ctx.facOfficers(f).length);
  for (let t = 0; t < turns; t++) { ctx.endTurn(); if (ctx.G.over) break; }
  const PC = ctx.PC, ps = PC.ps.slice().sort((a, b) => a - b);
  console.log('seed', seed, 'turns', turns, '| 권한 횟수', PC.ask, '넘어간 횟수', PC.ok, '(' + (PC.ask ? Math.round(100 * PC.ok / PC.ask) : 0) + '%) | 권할 때의 성공률 가운데값', ps[Math.floor(ps.length / 2)], '평균', ps.length ? Math.round(ps.reduce((a, b) => a + b, 0) / ps.length) : '-');
  console.log(' 해마다 [권함, 넘어감]', JSON.stringify(PC.byYear), '| 플레이어 자리(' + ctx.G.factions[fac].name + ')의 무장에게 권함', PC.askP, '넘어감', PC.fromP);
  console.log(' 누가 누구에게서', Object.entries(PC.pair).sort((a, b) => b[1] - a[1]).slice(0, 12).map(e => e[0] + ' ' + e[1]).join(', '));
  console.log(' 무장 수(시작 → 지금)', ctx.G.factions.map((F, f) => F.name + ' ' + n0[f] + '→' + (F.alive ? ctx.facOfficers(f).length : '망')).join(', '));
} else {
  const fac = +(process.argv[3] || 0), seed = +(process.argv[4] || 1), months = +(process.argv[5] || 12);
  ctx.newGame(fac, seed); const G = ctx.G; ctx.facAdv(fac).int = 100;
  const got = [], perMonth = [];
  for (let t = 0; t < months * 3 && !G.over; t++) {
    let n = 0;
    for (const b of ctx.facBases(fac)) {
      const ts = ctx.poachTargets(b).filter(x => !ctx.askWait(x)).map(x => ({ x, roll: ctx.recruitRoll(x) })).sort((a, c) => a.roll - c.roll);
      for (const { x, roll } of ts) {
        const os = ctx.idleOfficers(b).map(o => ({ o, p: ctx.recruitChance(b, o, x) })).filter(q => q.p > roll).sort((a, c) => a.p - c.p);   // 통하는 사람 가운데 가장 못하는 사람부터 쓴다
        if (!os.length || G.factions[fac].ap < ctx.AP.recruit) continue;
        const from = ctx.facName(x.f), l = x.loy, r = ctx.cmdRecruit(b, os[0].o.id, x.id);
        if (r.ok && r.joined) { n++; got.push(ctx.dateStr() + ' ' + from + ' ' + x.n + '(충성 ' + l + ', ' + os[0].p + '%)'); } else { console.log('어긋남: 응하게 되어 있는데 거절', JSON.stringify(r)); process.exit(1); }
      }
    }
    perMonth[Math.floor(t / 3)] = (perMonth[Math.floor(t / 3)] || 0) + n;
    ctx.endTurn();
  }
  console.log(G.factions[fac].name, 'seed', seed, '| 달마다 넘어온 무장', perMonth.join(' '), '| 모두', got.length);
  console.log('  ', got.join(' · '));
}
