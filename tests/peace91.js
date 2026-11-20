// v0.9.1: 초반 보호 기간(18/12/9턴 = 6개월/4개월/3개월)과 옛 저장 옮기기.   node tests/peace91.js
//  - 새 판: 시작 병력 1만 미만 18턴 · 2만 미만 12턴 · 그 밖 9턴. 모두 하순에 끝난다
//  - 0.8.1~0.9 에서 시작한 판(보호의 끝이 옛 기간으로 저장됨): 새 기간으로 당기되 불러온 때부터 30일은 남긴다. 한 번만 당기고, 기록에 한 줄 남긴다
//  - 0.8 이전 저장(보호 자체가 없음): 새 기간으로 붙는다
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.env.SRC || path.join(__dirname, '..', 'src');
const X = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat };
vm.createContext(X);
for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), X, { filename: f });
let fails = 0, n = 0;
function ok(c, m, i) { n++; console.log((c ? '  ok   ' : '  FAIL ') + m + (i !== undefined ? ' [' + i + ']' : '')); if (!c) fails++; }
const G = () => vm.runInContext('G', X);
console.log('1. 새 판');
ok(JSON.stringify(vm.runInContext('[PEACE_PLAYER, PEACE_ALL, PEACE_RAMP]', X)) === '[[[10000,18],[20000,12]],9,24]', '기간 표: 1만 미만 18턴 · 2만 미만 12턴 · 그 밖 9턴 · 완충 24턴');
const seen = {};
for (let f = 0; f < X.SCENARIO.factions.length; f++) {
  X.newGame(f, 7); const P = G().peace, tr = X.startTroops(f), want = tr < 10000 ? 18 : (tr < 20000 ? 12 : 9); seen[want] = (seen[want] || 0) + 1;
  if (P.until !== 1 + want || P.v !== 2 || !/하순$/.test(X.dateOfTurn(P.until - 1))) ok(false, X.SCENARIO.factions[f].n + ' 보호 기간', tr + '명 → ' + P.until + ' ' + X.dateOfTurn(P.until - 1));
}
ok(true, '19세력 모두: 시작 병력대로 기간이 붙고 하순에 끝난다', '18턴 ' + (seen[18] || 0) + '곳 · 12턴 ' + (seen[12] || 0) + '곳 · 9턴 ' + (seen[9] || 0) + '곳');
X.newGame(2, 7); ok(G().peace.until === 19 && X.dateOfTurn(18) === '194년 6월 하순', '유비(7,000명): 194년 6월 하순까지', X.dateOfTurn(G().peace.until - 1));
X.newGame(2, 7); G().aiOnly = false;
let hit = 0; for (let t = 0; t < 18 && !G().over; t++) { X.endTurn(); }
ok(G().turn === 19 && X.peaceLeft() === 0, '18턴이 지나면 보호가 끝난다', '턴 ' + G().turn + ' 남은 ' + X.peaceLeft());
ok(G().log.some(e => /초반 보호가 30일 남았습니다/.test(e.t)) && G().log.some(e => /초반 보호가 끝났습니다/.test(e.t)), '끝나기 30일 전과 끝난 날에 기록이 남는다(날수로 적는다)');
ok(!G().log.some(e => /\d턴 남았/.test(e.t)), '기록에 "N턴 남았습니다"가 없다');
console.log('2. 0.8.1~0.9 에서 시작한 판');
function old(f, turn, until) { X.newGame(f, 7); const g = JSON.parse(X.serialize()); delete g.peace.v; g.peace.until = until; g.turn = turn; g.log = []; return JSON.stringify(g); }
X.deserialize(old(2, 5, 37)); ok(G().peace.until === 19 && G().peace.v === 2 && G().log.length === 1 && /짧아졌습니다/.test(G().log[0].t), '5턴째에 열면: 끝을 37 → 19 로 당기고 기록 한 줄', G().log[0] && G().log[0].t);
X.deserialize(old(2, 17, 37)); ok(G().peace.until === 20 && X.peaceLeft() === 3, '17턴째에 열면: 19가 아니라 불러온 때부터 30일(20)', G().peace.until);
X.deserialize(old(2, 25, 37)); ok(G().peace.until === 28 && X.peaceLeft() === 3, '25턴째(새 기간으로는 이미 지남)에 열면: 30일을 남긴다', G().peace.until + ' · ' + (G().log[0] || {}).t);
X.deserialize(old(2, 36, 37)); ok(G().peace.until === 37 && G().log.length === 0, '36턴째(어차피 10일 남음): 그대로, 기록 없음');
X.deserialize(old(2, 40, 37)); ok(G().peace.until === 37 && G().log.length === 0, '40턴째(이미 끝난 판): 그대로');
X.deserialize(X.serialize()); ok(G().peace.until === 37 && G().log.length === 0, '다시 열어도 또 건드리지 않는다');
X.deserialize(old(2, 5, 37)); X.deserialize(X.serialize()); ok(G().peace.until === 19 && G().log.length === 1, '당긴 판을 저장했다 다시 열어도 한 번만 당긴다');
X.deserialize(old(1, 4, 25)); ok(G().peace.until === 13, '여포(14,000명) 4턴째: 25 → 13', G().peace.until);
X.deserialize(old(4, 4, 13)); ok(G().peace.until === 10, '원소(42,000명) 4턴째: 13 → 10', G().peace.until);
{ X.deserialize(old(2, 5, 37)); const g = G(); g.peace.broken[0] = true; X.deserialize(X.serialize()); ok(G().peace.broken[0] === true, '먼저 친 세력의 기록은 그대로 남는다'); }
console.log('3. 0.8 이전 저장');
{ X.newGame(2, 7); const g8 = JSON.parse(X.serialize()); delete g8.peace; g8.turn = 4; const L = g8.log.length; X.deserialize(JSON.stringify(g8)); ok(G().peace.until === 19 && G().peace.v === 2 && G().log.length === L, '보호가 없던 저장: 새 기간으로 붙는다(당겼다는 기록은 없다)', G().peace.until); }
console.log('\n확인 ' + n + '건 · 실패 ' + fails + '건');
process.exit(fails ? 1 : 0);
