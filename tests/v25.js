// v0.25 — 개별 초상 253장(새 무장 83 + 공용 초상을 쓰던 170): 묶음 · 명부 · 옛 저장.   node tests/v25.js
//   A 그림 묶음(src/assets_p253.js): 253장, 열쇠 = art/por25_scenes.tsv      B 명부: 253명이 저마다 제 초상을 쓴다 · 공용 초상을 쓰는 명부의 사람은 없다
//   C 옛 저장(0.24 — 공용 초상을 쓰던 저장)을 열면 제 초상으로 바뀐다 · 아이는 그대로 공용 초상      D 순찰의 소리 이름
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.env.SRC || path.join(__dirname, '..', 'src');
const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array };
vm.createContext(ctx);
for (const f of ['mapdata.js', 'roster.js', 'data.js', 'bios.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
let pass = 0, fail = 0;
function ok(c, msg) { if (c) pass++; else { fail++; console.log('  ✗ ' + msg); } }
const J = s => JSON.parse(vm.runInContext('JSON.stringify(' + s + ')', ctx));
const rows = fs.readFileSync(path.join(__dirname, '..', 'art', 'por25_scenes.tsv'), 'utf8').split('\n').filter(l => l && l[0] !== '#').map(l => l.split('\t')).map(a => a.length === 5 ? a.slice(1) : a);
const KEY = {}; rows.forEach(r => { KEY[r[1]] = r[0]; });
function pack(name) { const t = fs.readFileSync(path.join(root, 'assets_' + name + '.js'), 'utf8'); return JSON.parse(t.slice(t.indexOf('{'), t.lastIndexOf('}') + 1)); }

console.log('A 그림 묶음');
ok(rows.length === 253 && Object.keys(KEY).length === 253 && new Set(rows.map(r => r[0])).size === 253, '장면 표: 253줄 · 이름과 열쇠가 겹치지 않는다');
const P = pack('p253'), pk = Object.keys(P.por).sort(), sk = Object.keys(P.scn).sort(), want = rows.map(r => r[0]).sort();
ok(pk.join() === want.join() && sk.join() === pk.join(), '묶음에 흉상 ' + pk.length + '장 · 장면 ' + sk.length + '장 — 열쇠가 표와 같다');
ok(pk.every(k => P.por[k].startsWith('UklGR') && P.por[k].length > 8000 && P.scn[k].startsWith('UklGR') && P.scn[k].length > 9000)      /* v0.26: 다시 그린 그림에는 흰 종이가 넓은 전신 그림이 있어 장면이 더 작다(가장 작은 것 12,920자) */, '모두 WebP 그림이다(흉상 평균 ' + Math.round(pk.reduce((a, k) => a + P.por[k].length, 0) / pk.length / 1366) + 'KB · 장면 평균 ' + Math.round(pk.reduce((a, k) => a + P.scn[k].length, 0) / pk.length / 1366) + 'KB)');
const a0 = {}; vm.createContext(a0); vm.runInContext(fs.readFileSync(path.join(root, 'assets.js'), 'utf8'), a0);
const base = new Set(vm.runInContext('Object.keys(PORTRAITS)', a0)), pool = new Set(Object.keys(pack('pool').por));
ok(pk.every(k => !base.has(k) && !pool.has(k)), '새 열쇠는 있던 초상(assets.js ' + base.size + '장 · 공용 ' + pool.size + '장)의 열쇠와 겹치지 않는다');

console.log('B 명부');
const R = J('SCENARIO.officers.map(function (o) { return [o.n, o.por]; })');
const own = R.filter(x => KEY[x[0]] !== undefined), wrong = own.filter(x => x[1] !== KEY[x[0]]);
ok(own.length === 253 && wrong.length === 0, '표의 253명이 모두 명부에 있고 제 열쇠를 쓴다 ' + wrong.slice(0, 4).map(x => x.join(':')).join(' '));
const generic = R.filter(x => /^g[mc][0-9]$/.test(x[1]) || /^g[mf][1-5][0-9][0-9]$/.test(x[1]));
ok(generic.length === 0, '명부에서 공용 초상(옛 10장 · 새 120장)을 쓰는 사람은 없다 ' + generic.slice(0, 4).map(x => x.join(':')).join(' '));
const miss = R.filter(x => !base.has(x[1]) && !P.por[x[1]]);
ok(miss.length === 0, '명부의 초상 열쇠가 모두 그림에 있다 ' + miss.slice(0, 4).map(x => x.join(':')).join(' '));
const use = {}; R.forEach(x => { use[x[1]] = (use[x[1]] || 0) + 1; });
const dup = own.filter(x => use[x[1]] > 1);
ok(dup.length === 0, '253명의 초상은 한 사람에 한 장이다 ' + dup.slice(0, 4).map(x => x.join(':')).join(' '));
console.log('   명부 ' + R.length + '명 · 서로 다른 초상 ' + Object.keys(use).length + '장 · 가장 많이 같이 쓰는 초상 ' + Math.max.apply(null, Object.values(use)) + '명');

console.log('C 옛 저장 · 아이');
const c = J(`(function () {
  newGame(0, 7, '190');
  var S = JSON.parse(serialize()), names = ['동탁', '손견', '사환', '관구검'], before = {}, i;
  S.officers.forEach(function (o) { if (names.indexOf(o.n) >= 0) { before[o.n] = o.por; o.por = 'gm101'; } });       // 0.24 의 저장처럼: 공용 초상을 쓰던 때
  deserialize(JSON.stringify(S));
  var after = {}; G.officers.forEach(function (o) { if (names.indexOf(o.n) >= 0) after[o.n] = o.por; });
  var dad = G.officers.filter(function (o) { return o.f === G.player && o.st === 'active' && !isWoman(o); })[0];
  var kid = makeKid(dad, G.year), b0 = BIRTH.boy; BIRTH.boy = 0;                    // 딸만 태어나게 해 두고 한 명 더
  var girl = makeKid(dad, G.year); BIRTH.boy = b0;
  return { before: before, after: after, kid: kid ? kid.por : null, girl: girl ? girl.por : null };
})()`);
ok(['동탁', '손견', '사환', '관구검'].every(n => c.after[n] === KEY[n] && c.before[n] === KEY[n]), '공용 초상이 적힌 옛 저장을 열면 제 초상으로 바뀐다 — ' + JSON.stringify(c.after));
ok(/^g[mf][1-5][0-9][0-9]$/.test(c.kid || '') && /^gf[1-5][0-9][0-9]$/.test(c.girl || ''), '가상의 아이는 그대로 공용 초상을 쓴다(첫 아이 ' + c.kid + ' · 딸 ' + c.girl + ')');

console.log('D 순찰의 소리');
const sd = fs.readFileSync(path.join(root, 'sfxdata.js'), 'utf8'), names = (sd.match(/^\s*(\w+): "/gm) || []).map(s => s.trim().replace(/: "$/, ''));
ok(names.length === 30 && names.indexOf('patrol') >= 0 && names.indexOf('clack') < 0 && names.indexOf('march') >= 0, '소리 30개 — 순찰의 발걸음 patrol 이 있고 딱따기 clack 은 없다(부대가 걷는 소리 march 는 그대로)');
const u3 = fs.readFileSync(path.join(root, 'ui3d.js'), 'utf8');
ok(/patrol:\s+\{ s: \[\['patrol', 0\.85, 0\]\]/.test(u3) && u3.indexOf("'clack'") < 0, '순찰은 patrol 을 음높이 흔들림 없이 튼다');

console.log((fail ? 'FAIL ' : 'PASS ') + pass + ' / ' + (pass + fail));
process.exit(fail ? 1 : 0);
