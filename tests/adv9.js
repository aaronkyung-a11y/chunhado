// v0.9 규칙: 미리 정해 둔 결과(omenRoll) · 군사의 조언 · 다른 세력 무장 등용      node tests/adv9.js
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.env.SRC || path.join(__dirname, '..', 'src');
function mk() {
  const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array };
  vm.createContext(ctx);
  for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
  return ctx;
}
let pass = 0, fail = 0;
function ok(c, msg, extra) { if (c) pass++; else fail++; console.log((c ? '  ok   ' : '  FAIL ') + msg + (extra !== undefined ? '  [' + extra + ']' : '')); }
const X = mk(); X.newGame(0, 12345); const G = X.G;
const by = n => G.officers.find(o => o.n === n), base = n => G.bases[X.baseByName(n)];

console.log('1. 미리 정해 둔 결과');
{
  const a = X.omenRoll('r7'), s0 = G.seed; for (let i = 0; i < 50; i++) X.rnd();
  ok(X.omenRoll('r7') === a && G.seed !== s0, '난수를 뽑아도(G.seed 가 바뀌어도) 같은 턴·같은 대상의 결과는 같다');
  const t0 = G.turn; G.turn++; const b = X.omenRoll('r7'); G.turn = t0;
  ok(b !== a && X.omenRoll('r7') === a, '턴이 바뀌면 달라지고, 돌아오면 같다');
  ok(X.omenRoll('r8') !== a && X.omenRoll('pconfuseu7') !== a, '대상·종류가 다르면 다르다');
  let n = 0, sum = 0, dec = new Array(10).fill(0), lo = 0;
  for (let t = 1; t <= 200; t++) { G.turn = t; for (let k = 0; k < 300; k++) { const v = X.omenRoll('r' + k); n++; sum += v; dec[Math.floor(v / 10)]++; if (v < 23) lo++; } }
  G.turn = t0;
  const worst = Math.max(...dec.map(d => Math.abs(d / n - 0.1)));
  ok(Math.abs(sum / n - 50) < 0.6 && worst < 0.006, '고르게 퍼진다: 6만 번의 평균 ' + (sum / n).toFixed(2) + ', 열 구간의 최대 치우침 ' + (worst * 100).toFixed(2) + '%p');
  ok(Math.abs(lo / n - 0.23) < 0.006, '성공률 23%면 23%쯤 성공', (100 * lo / n).toFixed(2) + '%');
  const s = X.serialize(), a2 = X.omenRoll('pfireu3'); X.deserialize(s); ok(X.omenRoll('pfireu3') === a2 && X.G.seed0 === 12345, '저장했다 불러도 같다(G.seed0 = 처음 씨앗)');
}
const G1 = X.G;
console.log('2. 군사');
{
  const fs_ = G1.factions.map((F, f) => X.facAdv(f)), all = fs_.every((A, f) => { const c = X.advCandidates(f); return c.length ? (A && A.id === c[0].id && A.int === Math.max(...c.map(o => o.int))) : A === null; });
  ok(all, '새 판: 세력마다 지력이 가장 높은 무장(군주 제외)이 군사', G1.factions.slice(0, 6).map((F, f) => F.name + ':' + (fs_[f] ? fs_[f].n + fs_[f].int : '-')).join(' '));
  ok(fs_.every((A, f) => !A || A.id !== G1.factions[f].lord), '군주는 군사가 아니다');
  ok(X.setAdvisor(0, G1.factions[0].lord).ok === undefined || X.setAdvisor(0, G1.factions[0].lord).ok === false, '군주를 군사로 삼을 수 없다');
  const other = X.advCandidates(1)[0]; ok(!X.setAdvisor(0, other.id).ok, '다른 세력의 무장도 안 된다');
  const c0 = X.advCandidates(0), low = c0[c0.length - 1]; ok(X.setAdvisor(0, low.id).ok && X.facAdv(0) === low, '바꿀 수 있다', low.n + ' 지력 ' + low.int);
  ok(X.adviceAcc({ int: 90 }, 70) === 100 && X.adviceAcc({ int: 70 }, 90) === 60 && X.adviceAcc({ int: 80 }, 80) === 80 && X.adviceAcc({ int: 40 }, 99) === 50 && X.adviceAcc({ int: 100 }, 100) === 100, '적중률 = 지력 + (지력 − 상대 지력) × 0.5, 50~100', '90↔70 100 · 70↔90 60 · 80↔80 80 · 40↔99 50');
  // 실제로 그만큼 맞는가: 군사 지력 70, 상대 지력 80 → 65%
  const A = { int: 70 }, save = G1.factions[0].adv; let n = 0, right = 0, p = 37;
  low.int0 = low.int; low.int = 70;
  for (let t = 1; t <= 300; t++) { G1.turn = t; for (let k = 0; k < 100; k++) { const key = 'r' + k, a = X.advise(0, X.omenRoll(key), X.omenRoll('a|' + key), p, 80), real = X.omenRoll(key) < p; n++; if (a.says === real) right++; if (a.acc !== 65) fail++; } }
  ok(Math.abs(right / n - 0.65) < 0.01, '적중률 65%인 군사는 3만 번 가운데 65%쯤 맞힌다', (100 * right / n).toFixed(2) + '%');
  // 지력이 높은 군사가 맞히는 때는 낮은 군사가 맞히는 때를 모두 포함한다(군사를 바꿔 물어도 새 정보가 없다)
  let viol = 0, hiRight = 0;
  for (let t = 1; t <= 100; t++) { G1.turn = t; for (let k = 0; k < 100; k++) { const key = 'pconfuseu' + k, real = X.omenRoll(key) < 44; low.int = 60; const a1 = X.advise(0, X.omenRoll(key), X.omenRoll('a|' + key), 44, 75); low.int = 95; const a2 = X.advise(0, X.omenRoll(key), X.omenRoll('a|' + key), 44, 75); if (a1.says === real && a2.says !== real) viol++; if (a2.says === real) hiRight++; } }
  ok(viol === 0 && hiRight === 10000, '낮은 군사가 맞힌 것을 높은 군사가 틀리는 일은 없다 · 적중률 100%면 늘 맞는다', 'viol ' + viol + ', 100% 군사 ' + hiRight + '/10000');
  low.int = low.int0; G1.turn = 1; G1.factions[0].adv = save;
  // 자리가 비면 채운다
  const A0 = X.facAdv(0); A0.st = 'captive'; ok(X.facAdv(0) === null, '사로잡히면 자리가 빈다');
  X.phaseStart(0); ok(X.facAdv(0) && X.facAdv(0).id !== A0.id && X.facAdv(0).int === Math.max(...X.advCandidates(0).map(o => o.int)), '그 세력의 차례가 오면 지력이 가장 높은 무장으로 채운다', X.facAdv(0).n);
  A0.st = 'active';
}
console.log('3. 다른 세력 무장 등용 — 대상과 성공률');
{
  X.newGame(0, 777); const G2 = X.G, b = base('진류'), nb = X.ADJ[b.id].map(e => G2.bases[e.to]);
  const ts = X.poachTargets(b);
  ok(ts.length > 0 && ts.every(t => t.f !== 0 && t.f >= 0 && !X.isLord(t) && t.unit === null && nb.some(x => x.id === t.loc)), '대상: 이웃 거점에 머무는 다른 세력의 무장(군주 제외)', ts.length + '명 — ' + [...new Set(ts.map(t => G2.bases[t.loc].n))].join('·'));
  const o = X.idleOfficers(b).sort((x, y) => y.cha - x.cha)[0];
  const bonded = ts.find(t => X.bondOf(t)), high = ts.find(t => !X.bondOf(t) && t.loy >= 95), norm = ts.filter(t => !X.bondOf(t) && t.loy < 95);
  if (bonded) ok(X.recruitChance(b, o, bonded) === 0, '제 주군과 인연이 있으면 0%', bonded.n + ' ' + X.bondOf(bonded));
  const T = norm[0], l0 = T.loy;
  T.loy = 95; ok(X.recruitChance(b, o, T) === 0, '충성 95 이상이면 0%');
  T.loy = 94; const p94 = X.recruitChance(b, o, T); T.loy = 80; const p80 = X.recruitChance(b, o, T); T.loy = 70; const p70 = X.recruitChance(b, o, T);
  ok(p94 <= p80 && p80 < p70 && p70 <= 85, '충성이 낮을수록 잘 응한다', o.n + '(매 ' + o.cha + ' 정 ' + o.pol + ') → ' + T.n + ': 충성 94 ' + p94 + '% · 80 ' + p80 + '% · 70 ' + p70 + '%');
  const L = X.off(G2.factions[0].lord), TL = X.off(G2.factions[T.f].lord);
  ok(p80 === X.clamp(Math.round(15 + (o.cha - 50) * 0.5 + (o.pol - 50) * 0.2 + (L.cha - TL.cha) * 0.25 - 10 * 2.5 + (o.sk === '논객' ? 20 : 0)), 0, 85), '식 그대로: 15 + (매력−50)×0.5 + (정치−50)×0.2 + (군주 매력 차)×0.25 − (충성−70)×2.5', p80 + '%');
  const sk0 = o.sk; o.sk = '논객'; T.loy = 86; const pt = X.recruitChance(b, o, T); o.sk = ''; const pn = X.recruitChance(b, o, T); o.sk = sk0; ok(pt - pn === 20 || pt === 85, '논객 +20', pn + ' → ' + pt);
  T.loy = l0;
  ok(!X.canPoach(b, X.off(G2.factions[T.f].lord)), '군주에게는 권할 수 없다');
  const farB = G2.bases.find(x => x.owner >= 0 && x.owner !== 0 && !nb.some(y => y.id === x.id) && X.baseOfficers(x).some(q => !X.isLord(q)));
  const farT = X.baseOfficers(farB).find(q => !X.isLord(q)); ok(!X.canPoach(b, farT) && !X.cmdRecruit(b, o.id, farT.id).ok, '이웃이 아닌 거점의 무장에게는 권할 수 없다', farB.n + ' ' + farT.n);
}
console.log('4. 권하기 — 넘어옴 / 거절 / 다시 권하기');
{
  X.newGame(0, 4242); const G3 = X.G, b = base('진류'); G3.factions[0].ap = 255;
  const idle = () => X.idleOfficers(b).sort((x, y) => y.cha - x.cha);
  let T = X.poachTargets(b).filter(t => !X.bondOf(t))[0]; const tf = T.f, tb = G3.bases[T.loc];
  // 반드시 응하게 / 반드시 거절하게: 충성을 조정해 성공률을 만들고, 이번 턴의 주사위와 견준다
  // 다른 세력 무장의 주사위는 달마다 한 번: 같은 달에는 턴이 바뀌어도 같고, 달이 바뀌면 달라진다
  { const r0 = X.recruitRoll(T), t0 = G3.turn; G3.turn = t0 + 1; const r1 = X.recruitRoll(T); G3.turn = t0 + 2; const r2 = X.recruitRoll(T); G3.turn = t0; G3.month = 2; const r3 = X.recruitRoll(T); G3.month = 1;
    ok(r0 === r1 && r1 === r2 && r3 !== r0, '다른 세력 무장의 마음은 달마다 한 번 정해진다(같은 달에는 같고, 달이 바뀌면 다르다)', r0.toFixed(1) + ' / ' + r3.toFixed(1));
    const fo = { id: T.id, st: 'free' }; G3.turn = t0 + 1; const f1 = X.recruitRoll(fo); G3.turn = t0; ok(X.recruitRoll(fo) !== f1, '재야·포로는 턴마다 새로 정해진다'); }
  const roll = X.recruitRoll(T);
  T.loy = 94; let o = idle()[0], p = X.recruitChance(b, o, T);
  if (roll >= p) {
    const n0 = X.facOfficers(tf).length, ap0 = G3.factions[0].ap, r = X.cmdRecruit(b, o.id, T.id);
    ok(r.ok && !r.joined && T.f === tf && T.loc === tb.id && T.loy === 97 && X.facOfficers(tf).length === n0, '거절: 그대로 남고 충성 +3', 'p ' + p + ' 주사위 ' + roll.toFixed(1) + ' 충성 94 → ' + T.loy);
    ok(G3.factions[0].ap === ap0 - X.AP.recruit && o.acted, '행동력과 무장의 차례는 쓴다');
    const r2 = X.cmdRecruit(b, idle()[0].id, T.id); ok(!r2.ok && /다음 달/.test(r2.msg) && X.askWait(T) === 3, '한 무장에게는 한 달에 한 번(1월 상순에 권했으면 2월 상순부터 다시)', r2.msg);
    G3.turn += 2; ok(X.askWait(T) === 1, '1월 하순에도 아직'); G3.turn += 1; ok(X.askWait(T) === 0, '다음 달 상순에는 다시 권할 수 있다'); G3.turn -= 3;
  } else ok(false, '(준비) 거절 사례를 만들지 못함 — 씨앗을 바꿀 것', 'p ' + p + ' roll ' + roll);
  // 응하는 사례: 다른 대상 가운데 주사위가 낮은 사람을 골라 충성을 낮춘다
  let cand = X.poachTargets(b).filter(t => !X.bondOf(t) && t !== T).map(t => ({ t, roll: X.recruitRoll(t) })).sort((x, y) => x.roll - y.roll)[0];
  T = cand.t; T.loy = 70; o = idle()[0]; p = X.recruitChance(b, o, T);
  ok(cand.roll < p, '(준비) 이번 턴에 응하게 되어 있는 대상', T.n + ' p ' + p + ' 주사위 ' + cand.roll.toFixed(1));
  const from = T.f, fb = G3.bases[T.loc], wasAdv = G3.factions[from].adv === T.id, n1 = X.facOfficers(from).length, m1 = X.facOfficers(0).length;
  const rest = X.facOfficers(from).filter(q => q !== T && !X.isLord(q)).map(q => [q, q.loy]);
  G3.factions[from].adv = T.id; T.job = { b: fb.id, i: 0 };
  // 낮은 사람이 통하면 높은 사람도 통한다(주사위는 대상에만 걸려 있다)
  const ps = idle().map(x => X.recruitChance(b, x, T)), outs = ps.map(q => cand.roll < q);
  ok(ps.every((q, i) => ps.every((q2, j) => !(q2 >= q && outs[i] && !outs[j]))), '성공률이 더 높은 무장이 안 되는데 낮은 무장이 되는 일은 없다', ps.join(',') + ' → ' + outs.map(x => x ? 'o' : 'x').join(''));
  const r = X.cmdRecruit(b, o.id, T.id);
  ok(r.ok && r.joined && r.far && r.from === from, '응함');
  ok(T.f === 0 && T.loc === b.id && T.st === 'active' && T.acted === true && T.unit === null, '그 자리에서 내 거점으로 넘어온다', fb.n + ' → ' + G3.bases[T.loc].n);
  ok(T.loy >= 70 && T.loy <= 85, '새 주군에 대한 충성 70~85', T.loy);
  ok(X.facOfficers(from).length === n1 - 1 && X.facOfficers(0).length === m1 + 1, '무장 수: 그쪽 −1, 이쪽 +1');
  ok(rest.length > 0 && rest.every(([q, l]) => q.loy === Math.min(100, l + 2)), '그 세력에 남은 무장들의 충성 +2(이미 100이면 그대로)', rest.slice(0, 4).map(([q, l]) => q.n + ' ' + l + '→' + q.loy).join(' '));
  ok(T.job === null && X.jobOf(T) === null, '맡던 공사에서 빠진다');
  ok(X.facAdv(from) === null, '그 세력의 군사였다면 자리가 빈다'); X.phaseStart(from); ok(X.facAdv(from) !== null && X.facAdv(from).id !== T.id, '그 세력의 차례에 새 군사');
  ok(G3.log.some(e => e.t.indexOf(T.n) >= 0 && e.t.indexOf('등용') >= 0), '기록에 남는다', G3.log[G3.log.length - 1].t);
  // 재야: 한 턴에 한 번
  const cb = G3.bases.find(x => x.owner === 0 && X.hiddenOfficers(x).length) || b, hid = X.hiddenOfficers(cb)[0];
  if (hid) { hid.st = 'free'; G3.factions[0].ap = 255; const os = X.idleOfficers(cb); if (os.length >= 2) { const rr = X.cmdRecruit(cb, os[0].id, hid.id); if (!rr.joined) { const r3 = X.cmdRecruit(cb, os[1].id, hid.id); ok(!r3.ok && /이미 권했습니다/.test(r3.msg), '재야도 한 턴에 한 번만 권할 수 있다', r3.msg); G3.turn++; ok(X.askWait(hid) === 0, '다음 턴에는 다시 권할 수 있다'); G3.turn--; } else ok(true, '재야 등용 성공(한 턴에 한 번 검사는 건너뜀)'); } }
}
console.log('5. 계략 — 결과가 미리 정해 둔 것과 같은가');
{
  X.newGame(0, 99); const G4 = X.G, b = base('진류'), eb = base('복양'); G4.factions[0].ap = 255; G4.factions[eb.owner].ap = 255; b.w.spear = 9000; eb.w.spear = 9000; b.troops = 20000; eb.troops = 20000;
  let same = 0, n = 0, advRight = 0;
  const A = X.facAdv(0); A.int = 100;                                    // 적중률 100%
  for (let k = 0; k < 40; k++) {
    b.w.spear = 9000; eb.w.spear = 9000; b.troops = 20000; eb.troops = 20000; b.food = 30000; eb.food = 30000;
    const o1 = X.idleOfficers(b)[0], o2 = X.baseOfficers(eb).filter(q => !X.isLord(q) && !q.acted)[0]; if (!o1 || !o2) break;
    const d1 = X.cmdDeploy(b, { type: 'spear', ids: [o1.id], troops: Math.min(3000, X.cmdCap(o1)), food: 2000 }), d2 = X.cmdDeploy(eb, { type: 'spear', ids: [o2.id], troops: Math.min(3000, X.cmdCap(o2)), food: 2000 });
    if (!d1.ok || !d2.ok) { console.log('     (준비 실패)', d1.msg, d2.msg); break; }
    const u = d1.unit, e = d2.unit;
    const c = 150 + k % 5, r = 60 + Math.floor(k / 5); X.placeUnit(u, c, r); X.placeUnit(e, c + 1, r); u.morale = 100; u.done = false; u.born = -1;
    const pl = X.PLOYS[1 + k % 2], t = { kind: 'unit', u: e, c: e.c, r: e.r }, p = X.ployChance(u, pl, e), want = X.ployRoll(pl, t) < p, adv = X.advise(0, X.ployRoll(pl, t), X.ployRollA(pl, t), p, X.uInt(e));
    const res = X.unitPloy(u, pl, t); n++; if (res.ok && res.success === want) same++; if (adv.says === want) advRight++;
    X.removeUnit(u); X.removeUnit(e); o1.unit = null; o2.unit = null; o1.acted = false; o2.acted = false; G4.factions[0].ap = 255; G4.factions[eb.owner].ap = 255; G4.turn++;
  }
  ok(n >= 20 && same === n, '교란·위보 ' + n + '번: 실제 결과 = 미리 정해 둔 결과', same + '/' + n);
  ok(advRight === n, '지력 100인 군사의 조언이 모두 맞았다', advRight + '/' + n);
}
console.log('6. AI — 초반 보호 중에는 플레이어의 무장에게 권하지 않는다 / 그 뒤에는 권한다');
{
  X.newGame(1, 5); const G5 = X.G;                                         // 여포(매력 40, 보호 24턴)
  vm.runInContext(`var PQ = { early: 0, late: 0, gone: 0, total: 0, firstLate: 0 }; var _cr9 = cmdRecruit; cmdRecruit = function (b, id, tid) { var t = off(tid), mine = t && t.f === G.player && t.st === 'active' && b.owner !== G.player, tn = G.turn, un = G.peace.until; var r = _cr9(b, id, tid); if (r && r.ok && r.far) PQ.total++; if (r && r.ok && mine) { if (tn < un) PQ.early++; else { PQ.late++; if (!PQ.firstLate) PQ.firstLate = tn; } if (r.joined) PQ.gone++; } return r; };`, X);
  const until = G5.peace.until, n0 = X.facOfficers(1).length;
  for (let t = 0; t < 60 && !G5.over; t++) X.endTurn();
  ok(X.PQ.early === 0, '보호가 끝나기 전(' + (until - 1) + '턴까지)에는 여포군 무장에게 권한 일이 없다', 'early ' + X.PQ.early);
  ok(X.PQ.total > 0, 'AI끼리는 권한다', '60턴 동안 ' + X.PQ.total + '번');
  console.log('     (참고) 보호가 끝난 뒤 여포군 무장에게 권한 횟수 ' + X.PQ.late + ', 넘어간 무장 ' + X.PQ.gone + ', 처음 권한 턴 ' + (X.PQ.firstLate || '-') + ' · 무장 수 ' + n0 + ' → ' + (G5.factions[1].alive ? X.facOfficers(1).length : '멸망'));
}
console.log('7. 옛 저장');
{
  X.newGame(2, 31); const g = JSON.parse(X.serialize()); delete g.seed0; g.factions.forEach(F => { delete F.adv; }); g.officers.forEach(o => { delete o.ask; });
  ok(X.deserialize(JSON.stringify(g)), '군사·고정 씨앗이 없는 저장을 연다');
  const G6 = X.G; ok(typeof G6.seed0 === 'number' && G6.factions.every((F, f) => !F.alive || X.advCandidates(f).length === 0 || X.facAdv(f)), '고정 씨앗과 군사가 붙는다', '유비군 군사 ' + (X.facAdv(2) ? X.facAdv(2).n : '-'));
  const a = X.omenRoll('r1'), s2 = X.serialize(); X.deserialize(s2); ok(X.omenRoll('r1') === a, '다시 저장했다 열어도 결과가 같다');
}
console.log('\n' + (pass + fail) + '항목, 실패 ' + fail);
process.exit(fail ? 1 : 0);
