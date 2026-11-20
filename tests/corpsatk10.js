// v0.10 — 군단이 공격에 나서는 문턱(CORPS_ATK)이 알맞은가를 잰다.
//   node tests/corpsatk10.js
// 방법: 원소로 시작해 도시를 군단에 맡기고 공격 방침을 준다. 도시들의 병력을 '낼 수 있는 병력 = 필요 × 1.05' 가 되게 맞추고
//       (무장의 지휘 한도 때문에 못 미치면 닿는 데까지), 24턴 동안 맡겨 둔다 — 징병 · 뒤따라 보태기 모두 평소대로, 목표의 주인(AI)도 평소대로 지킨다.
//       나섰는가 · 차지했는가 · 몇 턴 걸렸는가 · 몇 부대(몇 명)를 냈는가를 씨앗 여섯으로 본다.
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.env.SRC || path.join(__dirname, '..', 'src');
function run2(seed, tname, k, names) {
  const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat };
  vm.createContext(ctx);
  for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
  ctx.ARG = { seed, tname, k, names: names || ['남피', '평원'] };
  return vm.runInContext(`(function () {
    newGame(4, ARG.seed);
    var T = G.bases[baseByName(ARG.tname)], cs = ARG.names.map(function (n) { return G.bases[baseByName(n)]; });
    var cp = corpsCreate(cs.map(function (b) { return b.id; })).corps;
    corpsSetDir(cp, 'atk', T.id);
    var need = corpsOutlook(cp, T).need, per = Math.round(need * ARG.k / cs.length / 0.75 / 100) * 100;
    cs.forEach(function (b) { b.troops = per; b.morale = 80; b.gold = 20000; b.food = 400000; b.w.spear = per; b.w.halberd = per; b.w.bow = per; b.w.horse = Math.round(per / 2); });
    cp.ap = 120;
    var o0 = corpsOutlook(cp, T), def0 = T.troops, first = 0, fell = 0, sent = 0, seen = {}, t;
    for (t = 1; t <= 24 && !fell && !G.over; t++) {
      endTurn();
      corpsUnits(cp).forEach(function (u) { if (u.type !== 'trans' && !seen[u.id]) { seen[u.id] = 1; sent += u.max; if (!first) first = t; } });
      if (T.owner === G.player) fell = t;
    }
    var left = 0; corpsUnits(cp).forEach(function (u) { if (u.type !== 'trans') left += u.troops; });
    return { need: need, have: o0.have, def0: def0, first: first, fell: fell, sent: sent, defEnd: T.owner === G.player ? 0 : T.troops, units: Object.keys(seen).length };
  })()`, ctx);
}
{
  console.log('① 도시 둘(남피 · 평원 — 무장 11명)을 맡긴 군단. 문턱 ' + JSON.stringify(require('vm').runInNewContext(fs.readFileSync(path.join(root, 'data.js'), 'utf8') + ';CORPS_ATK')) + ' — 낼 수 있는 병력을 필요의 1.05배로 맞추고 24턴');
  for (const tname of ['북해', '계', '복양', '북평']) {
    let fell = 0, went = 0, out = [], need = 0, have = 0, def0 = 0;
    for (const seed of [1, 2, 3, 4, 5, 6]) { const x = run2(seed, tname, 1.05); need = x.need; have = x.have; def0 = x.def0; if (x.first) went++; if (x.fell) fell++; out.push(x.first ? (x.fell ? '함락 ' + x.fell + '턴' : '실패(' + x.defEnd + ')') + ' ' + x.units + '부대 ' + x.sent : '나서지 않음'); }
    console.log(tname.padEnd(4) + ' 수비 ' + String(def0).padStart(6) + '  필요 ' + String(need).padStart(6) + '  낼 수 있는 병력 ' + String(have).padStart(6) + '  나섬 ' + went + '/6  함락 ' + fell + '/6   ' + out.join(' | '));
  }
}
{
  console.log('② 도시 셋(남피 · 평원 · 업 — 무장 27명)을 맡긴 군단이 단단한 성을 칠 때(같은 방법)');
  for (const tname of ['복양', '북평']) {
    let fell = 0, went = 0, out = [], need = 0, have = 0, def0 = 0;
    for (const seed of [1, 2, 3, 4, 5, 6]) { const x = run2(seed, tname, 1.05, ['남피', '평원', '업']); need = x.need; have = x.have; def0 = x.def0; if (x.first) went++; if (x.fell) fell++; out.push(x.first ? (x.fell ? '함락 ' + x.fell + '턴' : '실패(' + x.defEnd + ')') + ' ' + x.units + '부대 ' + x.sent : '나서지 않음'); }
    console.log(tname.padEnd(4) + ' 수비 ' + String(def0).padStart(6) + '  필요 ' + String(need).padStart(6) + '  낼 수 있는 병력 ' + String(have).padStart(6) + '  나섬 ' + went + '/6  함락 ' + fell + '/6   ' + out.join(' | '));
  }
}
