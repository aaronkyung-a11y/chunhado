// v0.9.1: AI 끼리 둔 판에서 전법별로 실제로 얼마나 쓰였고 얼마나 주고받았는가(보통 공격과 나란히).   node tests/tacuse91.js [소스 폴더=src] [턴=216] [씨앗=1]
//  주의: 여기의 평균은 '전법을 쓴 장면'과 '보통 공격을 한 장면'이 서로 다른 장면이라, 전법의 세기를 재는 자로는 맞지 않는다(강한 부대가 유리한 자리에서 전법을 쓴다). 세기는 tests/tac91.js 로 잰다.
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.argv[2] || path.join(__dirname, '..', 'src'), turns = +(process.argv[3] || 216), seed = +(process.argv[4] || 1);
const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat };
vm.createContext(ctx);
for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
vm.runInContext(`
var T = {}, NA = { n: 0, d: 0, c: 0, cn: 0, melee: 0, md: 0, mc: 0 };
var _t = unitTactic0, _a = unitAttack0;
unitTactic0 = function (u, tac, t) { var rg = hdist(u.c, u.r, t.u.c, t.u.r) > 1; var r = _t.apply(this, arguments); if (r && r.ok) { var x = T[tac.name] || (T[tac.name] = { n: 0, ok: 0, d: 0, c: 0, cn: 0, ex: 0, rg: 0 }); x.n++; if (!r.fail) x.ok++; x.d += r.dmg || 0; x.c += r.counter || 0; if (r.counter) x.cn++; if (rg) x.rg++; for (var i = 0; i < (r.extra || []).length; i++) x.ex += r.extra[i].dmg; } return r; };
unitAttack0 = function (u, t) { var rg = t.kind === 'unit' && hdist(u.c, u.r, t.u.c, t.u.r) > 1; var r = _a.apply(this, arguments); if (r && r.ok && r.kind === 'unit') { NA.n++; NA.d += r.dmg || 0; NA.c += r.counter || 0; if (r.counter) NA.cn++; if (!rg) { NA.melee++; NA.md += r.dmg || 0; NA.mc += r.counter || 0; } } return r; };
`, ctx);
ctx.newGame(0, seed); ctx.G.aiOnly = true;
for (let t = 0; t < turns; t++) { ctx.endTurn(); if (ctx.G.over) break; }
const T = ctx.T, NA = ctx.NA;
console.log(path.basename(root) + ' seed ' + seed + ' ' + turns + '턴');
console.log('보통 공격 ' + NA.n + '회: 피해 ' + Math.round(NA.d / NA.n) + ' · 반격 ' + Math.round(NA.c / NA.n) + ' (반격 받은 비율 ' + Math.round(100 * NA.cn / NA.n) + '%) | 근접만 ' + NA.melee + '회: 피해 ' + Math.round(NA.md / NA.melee) + ' · 반격 ' + Math.round(NA.mc / NA.melee));
let tn = 0, td = 0, tc = 0;
for (const k of ['돌출', '나선첨', '이단첨', '갈퀴', '횡치', '선풍', '화시', '관시', '난사', '돌격', '돌파', '돌진']) { const x = T[k]; if (!x) { console.log(k.padEnd(4) + ' 0회'); continue; } tn += x.n; td += x.d; tc += x.c;
  console.log(k.padEnd(4) + String(x.n).padStart(5) + '회  성공 ' + String(Math.round(100 * x.ok / x.n)).padStart(3) + '%  피해 ' + String(Math.round(x.d / x.n)).padStart(5) + (x.ex ? ' (+딸린 ' + Math.round(x.ex / x.n) + ')' : '') + '  반격 ' + String(Math.round(x.c / x.n)).padStart(4) + '  반격 받은 비율 ' + String(Math.round(100 * x.cn / x.n)).padStart(3) + '%  원거리 ' + Math.round(100 * x.rg / x.n) + '%'); }
console.log('전법 합계 ' + tn + '회: 피해 ' + Math.round(td / tn) + ' · 반격 ' + Math.round(tc / tn) + ' | 부대끼리의 공격 가운데 전법 ' + Math.round(100 * tn / (tn + NA.n)) + '%');
