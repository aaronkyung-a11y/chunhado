// v0.9.3 — 보통 공격이 늘 치명타인 무장(비장·용장·신장, 상대보다 무력이 높을 때)의 전법이 쓸 만한가.
//   node tests/tac93.js [turns=144] [seed=1]
// 방법은 tests/tac91.js 와 같다: AI 끼리 한 판을 돌리며 부대가 부대를 칠 때마다 그 순간의 두 부대를 붙잡아 보통 공격의 기대값(attackExpect)과
//   쓸 수 있는 전법 하나하나의 기대값(tacticExpect)을 견준다(주사위를 굴리지 않으므로 판은 바뀌지 않는다).
//   같은 장면에서 규칙 두 가지를 나란히 잰다:  "전" = 전법의 대성공이 병과 특기(창장·기장…)와 신장에만 붙는다(v0.9.2 까지)
//                                              "후" = 보통 공격이 치명타가 되는 조건(비장·용장·신장 + 상대보다 무력이 높다)이면 전법도 성공하면 대성공
//                                              "후′" = 후 + 그때의 대성공 배수를 보통 공격의 치명타와 같은 1.3 으로(다른 대성공은 1.25 그대로)
//                                              "지금" = 지금 소스의 tacticCrit 그대로(v0.9.3 에 넣은 것: 후 + 신장은 critGod)
//   판은 지금 소스의 규칙으로 흘러간다. SRC=<폴더> 로 다른 판의 소스를 줄 수 있다.
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.env.SRC || path.join(__dirname, '..', 'src');
const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array };
vm.createContext(ctx);
for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
const turns = +(process.argv[2] || 144), seed = +(process.argv[3] || 1);
vm.runInContext(`
var OPP = [], VAR = -1;                           // VAR: -1 = 소스 그대로, 0 = 전(병과 특기·신장만), 1 = 후(보통 공격이 치명타면 전법도)
var _tc0 = tacticCrit;
function tcOld(u, d) {                           // v0.9.2 까지의 규칙을 그대로 옮겨 적은 것
  var c = TACTIC_K.crit, g = TACTIC_K.critGod;
  if (uHas(u, '신장') && uWar(u) > uWar(d)) return c;
  if (u.type === 'spear' && (uHas(u, '창장') || uHas(u, '투신'))) return c;
  if (u.type === 'halberd' && (uHas(u, '극장') || uHas(u, '투신'))) return c;
  if (u.type === 'bow') { if (uHas(u, '궁신')) return g; if (uHas(u, '궁장')) return c; }
  if (u.type === 'cav') { if (uHas(u, '기신')) return g; if (uHas(u, '기장')) return c; }
  return 0;
}
tacticCrit = function (u, d) { if (VAR < 0) return _tc0(u, d); var c = tcOld(u, d); if (VAR >= 1 && critNormal(u, d)) return Math.max(c, VAR === 2 ? 1.3 : TACTIC_K.crit); return c; };
function look(u, d) {
  var N = attackExpect(u, d), rec = { cn: critNormal(u, d), tc: !!tcOld(u, d), sk: uMembers(u).map(function (o) { return o.sk; }).join(','), lead: uLeader(u).n, n: { dealt: N.dealt, recv: N.recv }, v: [[], [], [], []] }, any = false;
  for (var V = 0; V < 4; V++) {
    VAR = V === 3 ? -1 : V;
    var tl = tacticList(u);
    for (var i = 0; i < tl.length; i++) {
      var tac = tl[i]; if (u.morale < tac.cost) continue;
      var tt = tacticTargets(u, tac), okT = false; for (var q = 0; q < tt.length; q++) if (tt[q].u === d) okT = true;
      if (!okT) continue;
      var X = tacticExpect(u, d, tac);
      rec.v[V].push({ id: tac.id, p: X.ok, dealt: X.dealt, recv: X.recv }); any = true;
    }
  }
  VAR = -1;
  if (any) OPP.push(rec);
}
var _a = unitAttack0, _t = unitTactic0, USED = { n: 0, t: 0, cnN: 0, cnT: 0 };
unitAttack0 = function (u, t) { if (t.kind === 'unit' && !u.done) { look(u, t.u); USED.n++; if (critNormal(u, t.u)) USED.cnN++; } return _a.apply(this, arguments); };
unitTactic0 = function (u, tac, t) { if (!u.done) { look(u, t.u); USED.t++; if (critNormal(u, t.u)) USED.cnT++; } return _t.apply(this, arguments); };
`, ctx);
ctx.newGame(0, seed); ctx.G.aiOnly = true;
for (let t = 0; t < turns; t++) { ctx.endTurn(); if (ctx.G.over) break; }
const OPP = ctx.OPP, f2 = x => (Math.round(x * 100) / 100).toFixed(2);
console.log('src ' + path.basename(root) + ' ' + ctx.GAME_VERSION + ' | seed ' + seed + ' | ' + turns + '턴 | 전법을 쓸 수 있었던 싸움 장면 ' + OPP.length + '개');
console.log('이 판에서 AI 가 실제로 한 것: 보통 공격 ' + ctx.USED.n + '번(그 가운데 보통 공격이 치명타인 쪽 ' + ctx.USED.cnN + '번) · 전법 ' + ctx.USED.t + '번(치명타인 쪽 ' + ctx.USED.cnT + '번)');
const classes = [
  ['보통 공격이 치명타 · 전법엔 대성공 특기 없음 (비장·용장)', o => o.cn && !o.tc],
  ['보통 공격이 치명타 · 전법도 대성공 (신장, 또는 병과 특기 겹침)', o => o.cn && o.tc],
  ['보통 공격이 치명타가 아님 · 전법은 대성공 특기 (창장·기장…)', o => !o.cn && o.tc],
  ['그 밖(특기 없음)', o => !o.cn && !o.tc]];
console.log('\n' + '장면의 갈래'.padEnd(46) + '장면 | 규칙 | 성공률 | 남는 몫이 가장 큰 전법: 피해 · 받는 반격 · 남는 몫 | 전법이 이득인 장면');
for (const [label, fn] of classes) {
  const os = OPP.filter(fn);
  for (const V of [0, 1, 2, 3]) {
    const L = os.filter(o => o.v[V].length);
    if (!L.length) { if (V === 0) console.log(label.padEnd(46) + '   0'); continue; }
    let nD = 0, nR = 0, gD = 0, gR = 0, better = 0, pS = 0;
    for (const o of L) {
      const b = o.v[V].reduce((a, c) => (c.dealt - c.recv > a.dealt - a.recv ? c : a));
      nD += o.n.dealt; nR += o.n.recv; gD += b.dealt; gR += b.recv; pS += b.p;
      if (b.dealt - b.recv > o.n.dealt - o.n.recv + 0.1 * o.n.dealt) better++;
    }
    console.log((V === 0 ? label : '').padEnd(46) + String(L.length).padStart(4) + ' | ' + ['전  ', '후  ', '후′ ', '지금'][V] + ' |  ' + String(Math.round(pS / L.length)).padStart(3) + '%  |        ×' + f2(gD / nD) + ' · ×' + f2(gR / Math.max(1, nR)) + ' · ×' + f2((gD - gR) / (nD - nR)) + '                    | ' + String(Math.round(100 * better / L.length)).padStart(3) + '%');
  }
}
const who = {}; for (const o of OPP) if (o.cn && !o.tc) who[o.lead + '(' + o.sk + ')'] = (who[o.lead + '(' + o.sk + ')'] || 0) + 1;
console.log('\n첫 갈래의 부대(주장(부대원의 특기)): ' + Object.keys(who).sort((a, b) => who[b] - who[a]).slice(0, 12).map(k => k + ' ' + who[k]).join(' · '));
console.log('읽는 법: ×1.00 = 그 장면에서 보통 공격을 했을 때의 기대값. "이득인 장면" = 가장 나은 전법의 남는 몫(피해 − 반격)이 보통 공격보다 그 피해의 10% 넘게 큰 장면의 비율.');
