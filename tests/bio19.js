// v0.19 — 열전(src/bios.js): 명부의 425명 모두에게 있고, 남는 이름이 없고, 길이가 알맞고, 지어낸 인물에는 그렇다고 적혀 있는지.   node tests/bio19.js
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.env.SRC || path.join(__dirname, '..', 'src');
const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array };
vm.createContext(ctx);
for (const f of ['mapdata.js', 'roster.js', 'data.js', 'bios.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
let pass = 0, fail = 0;
function ok(c, msg) { if (c) pass++; else { fail++; console.log('  ✗ ' + msg); } }
const names = vm.runInContext('SCENARIO.officers.map(function (o) { return o.n; })', ctx), B = JSON.parse(vm.runInContext('JSON.stringify(BIOS)', ctx));
const keys = Object.keys(B), miss = names.filter(n => !B[n]), extra = keys.filter(k => !names.includes(k)), L = keys.map(k => B[k].length);
ok(names.length === 425 && keys.length === 425, '명부 ' + names.length + '명 · 열전 ' + keys.length + '편');
ok(miss.length === 0, '열전이 없는 사람: ' + miss.join(' '));
ok(extra.length === 0, '명부에 없는 이름: ' + extra.join(' '));
const short = keys.filter(k => B[k].length < 20), long = keys.filter(k => B[k].length > 110);
ok(short.length === 0, '너무 짧다(20자 미만): ' + short.join(' '));
ok(long.length === 0, '너무 길다(110자 넘음): ' + long.join(' '));
const badEnd = keys.filter(k => !/[다임장인들자요것함]\.$|\.$/.test(B[k]) || /\s$/.test(B[k]));
ok(badEnd.length === 0, '마침표로 끝나지 않는다: ' + badEnd.join(' '));
const badCh = keys.filter(k => /['"<>\\]|undefined|null|\s{2,}/.test(B[k]));
ok(badCh.length === 0, '쓰면 안 되는 글자(따옴표 · 꺾쇠 · 겹친 빈칸): ' + badCh.join(' '));
// 연의 · 민간 전승 · 소설에만 나오는 사람에게는 그렇다고 적혀 있어야 한다
const FICT = ['초선', '무안국', '종보', '양대장', '채중', '채화', '양송', '형도영', '축융', '오국태', '마운록', '주창', '관색', '타사대왕', '망아장', '관은병', '포삼랑', '왕도', '하후덕', '목록대왕', '올돌골', '철리길', '월길', '화만', '대래동주', '동도나', '아회남', '금환결', '이별'];
const unmarked = FICT.filter(n => !/연의|전승|소설|희곡/.test(B[n] || ''));
ok(FICT.every(n => names.includes(n)) && unmarked.length === 0, '지어낸 인물인데 그렇다는 말이 없다: ' + unmarked.join(' '));
// 이름 · 성씨가 뒷날 붙은 사람
const LATER = ['여령기', '황월영', '손상향', '보연사', '장기영', '엄씨', '추씨'];
const unmarked2 = LATER.filter(n => !/이름|성은/.test(B[n] || ''));
ok(unmarked2.length === 0, '이름이 뒷날 붙은 사람인데 그 말이 없다: ' + unmarked2.join(' '));
// bioOf: 판 안의 무장으로도 꺼낸다
const R = JSON.parse(vm.runInContext(`JSON.stringify((function () { newGame(0, 3); var all = G.officers.every(function (o) { return bioOf(o).length >= 20; }); return { all: all, cao: bioOf(off(G.factions[0].lord)), none: bioOf(null), n: G.officers.length }; })())`, ctx));
ok(R.all && R.n === 425 && R.cao.indexOf('맹덕') >= 0 && R.none === '', 'bioOf: 판 안의 무장 ' + R.n + '명 모두에게서 꺼낸다');
const tot = L.reduce((a, b) => a + b, 0);
console.log('열전 ' + keys.length + '편 · 가장 짧은 것 ' + Math.min(...L) + '자 · 가장 긴 것 ' + Math.max(...L) + '자 · 평균 ' + Math.round(tot / L.length) + '자 · 모두 ' + tot + '자');
console.log(fail ? 'FAIL ' + fail : 'PASS ' + pass);
process.exit(fail ? 1 : 0);
