// v0.10.1 — 군사의 조언이 얼마나 맞는가(식의 값 그대로, 주사위 없음).
//   node tests/adv101.js            지금 소스의 adviceAcc 로, 세력마다(자동으로 앉은 군사) 대상별 적중률의 분포
//   SRC=<폴더> 로 다른 판의 소스를 줄 수 있다.
// 대상: ① 재야(free · hidden) 무장  ② 다른 세력의 무장(등용 · 그 무장 혼자 이끄는 부대에 거는 계략)  ③ 시설에 지르는 불(상대 지력이 없다)
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.env.SRC || path.join(__dirname, '..', 'src');
const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array };
vm.createContext(ctx);
for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
const out = vm.runInContext(`
(function () {
  var rows = [];
  newGame(0, 1);
  var NF = G.factions.length;
  for (var f = 0; f < NF; f++) {
    newGame(f, 1);
    var A = facAdv(f) || autoAdvisor(f);
    if (!A) { rows.push({ f: G.factions[f].name, adv: null }); continue; }
    var free = [], foe = [];
    G.officers.forEach(function (o) {
      if (o.st === 'free' || o.st === 'hidden') free.push(adviceAcc(A, o.int));
      else if (o.f >= 0 && o.f !== f && o.st === 'active') foe.push(adviceAcc(A, o.int));
    });
    function st(a) { var s = 0, c100 = 0, c90 = 0, mn = 999; a.forEach(function (v) { s += v; if (v >= 100) c100++; if (v >= 90) c90++; if (v < mn) mn = v; }); return { n: a.length, avg: a.length ? Math.round(s / a.length * 10) / 10 : 0, p100: a.length ? Math.round(c100 / a.length * 100) : 0, p90: a.length ? Math.round(c90 / a.length * 100) : 0, min: a.length ? mn : 0 }; }
    rows.push({ f: G.factions[f].name, adv: A.n, int: A.int, free: st(free), foe: st(foe), fac: adviceAcc(A, 0) });
  }
  return JSON.stringify(rows);
})()`, ctx);
const rows = JSON.parse(out);
const pad = (s, n) => { s = String(s); let w = 0; for (const ch of s) w += ch.charCodeAt(0) > 255 ? 2 : 1; return s + ' '.repeat(Math.max(0, n - w)); };
console.log(pad('세력', 8) + pad('군사(지력)', 16) + pad('재야: 평균 · 100%인 몫 · 90%↑ · 최저 (n)', 44) + pad('다른 세력: 평균 · 100% · 90%↑ · 최저 (n)', 44) + '시설에 불');
let all = { free: [], foe: [] };
rows.forEach(r => {
  if (!r.adv) { console.log(pad(r.f, 8) + '군사 없음'); return; }
  console.log(pad(r.f, 8) + pad(r.adv + '(' + r.int + ')', 16) + pad(r.free.avg + '% · ' + r.free.p100 + '% · ' + r.free.p90 + '% · ' + r.free.min + '% (' + r.free.n + ')', 44) + pad(r.foe.avg + '% · ' + r.foe.p100 + '% · ' + r.foe.p90 + '% · ' + r.foe.min + '% (' + r.foe.n + ')', 44) + r.fac + '%');
});
