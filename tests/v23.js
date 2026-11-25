// v0.23 — 시대(시나리오) · 수명 · 후계: 규칙.   node tests/v23.js     (SIMY=4 — 시대마다 AI 끼리 돌려 보는 햇수)
//   A 명부: 생몰년 · 수명의 셈(병사는 역사의 해, 처형 · 전사는 max(+LIFE.add, LIFE.min 세)) · 194년 판은 예전 명부 그대로
//   B 시대 여덟: 판이 만들어지고, 군주 · 땅 · 관문 · 무장의 자리가 맞다
//   C 수명: 병석 → 죽음, 출진 중에는 버틴다, 숨은 사람 · 재야는 조용히
//   D 후계: 차례(정해 둔 후계 → 아들 → 형제 → 혈연 → 남), 인연이 이어지는가, 충성의 변화, 뒤를 이을 사람이 없으면 무너진다
//   E 장성: 집안으로 · 아버지가 섬기는 세력으로      F 옛 저장      H 아이 · 수명 켬/끔      G 시대마다 AI 끼리 몇 해
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.env.SRC || path.join(__dirname, '..', 'src');
const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat, Int32Array, Uint8Array, Float32Array, Uint32Array, Int16Array };
vm.createContext(ctx);
for (const f of ['mapdata.js', 'roster.js', 'data.js', 'bios.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
let pass = 0, fail = 0;
function ok(c, msg) { if (c) pass++; else { fail++; console.log('  ✗ ' + msg); } }
const run = s => vm.runInContext(s, ctx);
const J = s => JSON.parse(run('JSON.stringify(' + s + ')'));
const SIMY = +process.env.SIMY || 4;
run(`function N(n) { return offByName(n); }
function killNow(o) { o.dy = G.year; o.dm = G.month; lifeTick(); }
function inv() {                                   // 판이 어긋난 데가 없는가
  var bad = [];
  G.factions.forEach(function (F) {
    if (!F.alive) return;
    var L = off(F.lord);
    if (!L || L.st === 'dead' || L.f !== F.id) bad.push('군주 ' + F.name);
    else if (L.n !== F.name) bad.push('이름 ' + F.name + '/' + L.n);
    if (F.adv >= 0 && off(F.adv).st === 'dead') bad.push('죽은 군사 ' + F.name);
    if (F.heir >= 0 && off(F.heir).st === 'dead') bad.push('죽은 후계 ' + F.name);
  });
  G.officers.forEach(function (o) {
    if (o.st === 'dead' && (o.f >= 0 || o.unit !== null)) bad.push('죽은 사람이 세력에 ' + o.n);
    if (o.st === 'active' && o.f >= 0 && o.unit === null && G.bases[o.loc].owner !== o.f) bad.push('남의 땅에 ' + o.n);
    if (o.st !== 'dead' && o.st !== 'hidden' && o.unit === null && o.st !== 'travel' && o.dy && G.year * 12 + G.month > o.dy * 12 + o.dm + 1) bad.push('수명이 지났다 ' + o.n);
  });
  G.bases.forEach(function (b) { b.captives.forEach(function (id) { if (off(id).st !== 'captive') bad.push('포로 ' + off(id).n); }); });
  G.units.forEach(function (u) { u.off.forEach(function (id) { if (off(id).st === 'dead') bad.push('죽은 장수의 부대 ' + off(id).n); }); });
  return bad;
}`);

// ───────── A 명부 ─────────
console.log('A 명부');
const R = J('ROSTER'), LIFE = J('LIFE');
ok(R.length === 508 && new Set(R.map(r => r.n)).size === R.length, '무장 ' + R.length + '명 · 이름이 겹치지 않는다');
ok(R.every(r => r.by > 100 && r.hd > r.by + 15 && r.dm >= 1 && r.dm <= 12), '태어난 해 · 죽은 해 · 달이 모두 있다');
const badLife = R.filter(r => r.dy !== (r.k ? Math.max(r.hd + LIFE.add, r.by + LIFE.min) : r.hd));
ok(badLife.length === 0, '수명: 병사 · 자연사는 역사의 해, 처형 · 전사는 max(+' + LIFE.add + '년, ' + LIFE.min + '세) — 어긋난 사람 ' + badLife.map(r => r.n).slice(0, 5).join(' '));
const by = {}; R.forEach(r => { by[r.n] = r; });
ok(by['조조'].by === 155 && by['조조'].dy === 220 && !by['조조'].k && !by['조조'].e, '조조 155 ~ 220(병사 — 역사 그대로, 추정 아님)');
ok(by['관우'].k === 1 && by['관우'].hd === 220 && by['관우'].dy === 235 && (by['관우'].e & 1) === 1, '관우 ? ~ 220(처형) → 판에서는 235년까지(+15) · 태어난 해는 추정');
ok(by['손책'].by === 175 && by['손책'].hd === 200 && by['손책'].dy === 235, '손책 175 ~ 200(암살) → +15 를 해도 60세가 안 되어 60세(235년)까지');
ok(by['제갈량'].dy === 234 && by['여포'].dy === 221 && by['유선'].by === 207, '제갈량 234 · 여포 199(처형) → 221(60세) · 유선 207년생');
const badFa = R.filter(r => r.fa && (!by[r.fa] || by[r.fa].by + 13 > r.by));
ok(badFa.length === 0, '아버지가 명부에 있고 나이가 맞는다 — ' + badFa.map(r => r.n).join(' '));
const estB = R.filter(r => r.e & 1).length, estD = R.filter(r => r.e & 2).length;
console.log('   추정: 태어난 해 ' + estB + '명 · 죽은 해 ' + estD + '명 (모두 ' + R.length + '명)');
ok(estB > 300 && estD > 150, '사서에 없는 해에는 추정 표시가 있다');
const oldP = path.join(__dirname, '..', 'build', 'roster.v0221.js');
if (fs.existsSync(oldP)) {
  const t = fs.readFileSync(oldP, 'utf8'), O = JSON.parse(t.slice(t.indexOf('{'), t.lastIndexOf('}') + 1)), S = J('scenarioMake("194")');
  let d = 0;
  O.officers.forEach((o, i) => { const n = S.officers[i]; for (const k of Object.keys(o)) { if (k === 'por' && /^g[mc]\d$/.test(o.por)) { if (/^g[mc]\d$/.test(n.por)) d++; continue; } if (JSON.stringify(o[k]) !== JSON.stringify(n[k])) d++; }      // v0.24: 공용 초상을 쓰던 사람의 초상 열쇠만 바뀌었다(0.24 능력에 맞는 공용 초상 → 0.25 제 초상)
  for (const k of ['st', 'y', 'j', 'sk']) if ((k in n) !== (k in o)) d++; });
  ok(d === 0 && O.officers.length === 425, '194년 판: 예전 명부의 425명이 글자까지 같다(능력 · 세력 · 도시 · 등장 연도)');
  ok(JSON.stringify(O.factions.map(f => [f.n, f.cities])) === JSON.stringify(S.factions.map(f => [f.n, f.cities])) && JSON.stringify(O.gates) === JSON.stringify(S.gates) && JSON.stringify(O.women) === JSON.stringify(S.women), '194년 판: 세력 · 땅 · 관문 · 여성 표가 같다');
  const nw = S.officers.slice(425);
  console.log('   194년 판의 새 무장: 있음 ' + nw.filter(o => o.f >= 0).map(o => o.n).join('·') + ' · 재야 ' + nw.filter(o => o.st === 'free').map(o => o.n).join('·') + ' · 숨음 ' + nw.filter(o => o.st === 'hidden').length + ' · 죽음 ' + nw.filter(o => o.st === 'dead').length);
} else console.log('   (build/roster.v0221.js 가 없어 예전 명부와의 대조는 건너뛴다)');

// ───────── B 시대 ─────────
console.log('B 시대');
const SC = J('scenarioList()');
ok(SC.map(s => s.id).join() === '184,190,194,200,207,219,227,234' && SC.map(s => s.nf).join() === '10,20,19,9,9,4,4,4', '시대 여덟: ' + SC.map(s => s.year + ' ' + s.name + '(' + s.nf + ')').join(' · '));
for (const s of SC) {
  const r = J(`(function () {
    newGame(0, 5, '${s.id}');
    var S = SCENARIO, out = { scen: G.scen, y: G.year, m: G.month, d1: dateOfTurn(1), bad: [], n: G.officers.length, cnt: {}, inv: inv() }, i;
    G.officers.forEach(function (o) { out.cnt[o.st] = (out.cnt[o.st] || 0) + 1; });
    G.factions.forEach(function (F, k) {
      var sf = S.factions[k], L = off(F.lord), t = 0;
      if (!L || L.n !== sf.n || F.name !== sf.n) out.bad.push('군주 ' + sf.n);
      else if (G.bases[L.loc].n !== sf.cities[0]) out.bad.push('본거지 ' + sf.n);
      if (F.house !== houseName(sf.n) || F.heir !== -1 || F.n0 !== sf.n) out.bad.push('집안 ' + sf.n);
      sf.cities.forEach(function (c) { var b = G.bases[baseByName(c)]; if (b.owner !== k) out.bad.push('땅 ' + c); if (S.id !== '194' && !baseOfficers(b).length) out.bad.push('빈 성 ' + c); });
      G.bases.forEach(function (b) { if (b.owner === k) t += b.troops; });
      if (t !== startTroops(k)) out.bad.push('병력 ' + sf.n + ' ' + t + '/' + startTroops(k));
    });
    G.officers.forEach(function (o) {
      if (!o.by || !o.dy) out.bad.push('생몰년 ' + o.n);
      if (o.st === 'active' && (o.f < 0 || G.bases[o.loc].owner !== o.f)) out.bad.push('자리 ' + o.n);
      if (o.st === 'free' && o.f !== -1) out.bad.push('재야 ' + o.n);
      if (o.st !== 'dead' && o.dy < G.year) out.bad.push('이미 죽었어야 ' + o.n);
      if (o.st === 'active' && o.by + 12 > G.year) out.bad.push('너무 어리다 ' + o.n + ' ' + o.by);
      if (o.st === 'hidden' && o.j && o.y <= G.year) out.bad.push('숨었는데 나올 해가 지났다 ' + o.n);
    });
    out.gates = Object.keys(S.gates).filter(function (g) { var b = G.bases[baseByName(g)]; return !b || b.owner !== S.gates[g]; });
    return out;
  })()`);
  ok(r.scen === s.id && r.y === s.year && r.m === 1 && r.d1 === s.year + '년 1월 상순' && r.n === 508, s.year + '년 ' + s.name + ': 판이 그 해 1월 상순에 시작한다');
  ok(r.bad.length === 0 && r.gates.length === 0 && r.inv.length === 0, s.year + '년: 군주 · 본거지 · 땅 · 관문 · 병력 · 무장의 자리 — ' + r.bad.concat(r.gates, r.inv).slice(0, 6).join(' | '));
  console.log('   ' + s.year + ' ' + s.name + ': 있음 ' + (r.cnt.active || 0) + ' · 숨음 ' + (r.cnt.hidden || 0) + ' · 재야 ' + (r.cnt.free || 0) + ' · 죽음 ' + (r.cnt.dead || 0));
}
const spot = J(`(function () {
  function at(id, n) { newGame(0, 5, id); var o = N(n); return [o.st, o.f >= 0 ? G.factions[o.f].name : '-', G.bases[o.loc].n, o.y || 0, o.j || '']; }
  return { zj: at('184', '장각'), gy184: at('184', '관우'), lb190: at('190', '여포'), sc190: at('190', '손책'), gy200: at('200', '관우'), yl200: at('200', '안량'), zy200: at('200', '조운'), zg207: at('207', '제갈량'), xs207: at('207', '서서'),
    gy219: at('219', '관우'), xh219: at('219', '하후연'), lz219: at('219', '유장'), zg227: at('227', '제갈량'), jw227: at('227', '강유'), sm234: at('234', '사마의'), jw234: at('234', '강유'), dz200: at('200', '동탁'), ly194: at('194', '유언'), zl194: at('194', '주령') };
})()`);
ok(spot.zj.join() === 'active,장각,업,0,' && spot.gy184.join() === 'active,유비,계,0,', '184: 장각은 업 · 관우는 유비와 계에');
ok(spot.lb190.join() === 'active,동탁,낙양,0,' && spot.sc190.join() === 'hidden,-,여강,191,손견', '190: 여포는 동탁 밑에 · 손책은 191년에 손견에게로');
ok(spot.gy200.join() === 'active,유비,하비,0,' && spot.yl200[1] === '원소' && spot.zy200[1] === '유비' && spot.dz200[0] === 'dead', '200: 관우는 하비 · 안량은 원소 · 조운은 유비 · 동탁은 없다');
ok(spot.zg207.join() === 'hidden,-,신야,207,' && spot.xs207[1] === '유비', '207: 제갈량은 신야에 숨어 있다(탐색) · 서서는 유비에게');
ok(spot.gy219.join() === 'active,유비,강릉,0,' && spot.xh219.join() === 'active,조조,한중,0,' && spot.lz219[1] === '유비', '219: 관우는 강릉 · 하후연은 한중 · 유장은 유비 밑에');
ok(spot.zg227.join() === 'active,유선,한중,0,' && spot.jw227.join() === 'active,조예,천수,0,' && spot.sm234.join() === 'active,조예,장안,0,' && spot.jw234[1] === '유선', '227: 제갈량은 한중 · 강유는 아직 위의 천수 / 234: 사마의는 장안 · 강유는 촉');
ok(spot.ly194[0] === 'dead' && spot.zl194.join() === 'active,조조,진류,0,', '194: 유언은 내지 않는다(유장이 군주) · 새 무장 주령은 조조에게');

// ───────── C 수명 ─────────
console.log('C 수명');
const c1 = J(`(function () {
  newGame(0, 7, '194'); G.aiOnly = true;
  var o = N('도겸'), f = o.f, out = { dy: o.dy, dm: o.dm, sickAt: '', deadAt: '', log: [] };
  for (var t = 0; t < 40 && o.st !== 'dead'; t++) { endTurn(); if (o.sick && !out.sickAt) out.sickAt = dateStr(); }
  out.deadAt = dateStr(); out.died = o.died; out.f = o.f; out.name = G.factions[f].name; out.past = G.factions[f].past; out.lordOk = off(G.factions[f].lord).f === f && off(G.factions[f].lord).n === G.factions[f].name;
  out.log = G.log.filter(function (e) { return /도겸/.test(e.t); }).map(function (e) { return e.d + ' ' + e.t; }); out.inv = inv(); out.age = ageOf(o);
  return out;
})()`);
console.log('   ' + c1.log.join(' / '));
ok(c1.dy === 194 && c1.dm >= 7 && c1.sickAt === '194년 ' + (c1.dm - 3) + '월 상순' && c1.deadAt === '194년 ' + c1.dm + '월 상순' && c1.died === 194 && c1.f === -1, '도겸(194년 병사): 석 달 앞서 병석에 눕고(' + c1.sickAt + ') 그 달에 떠난다(' + c1.deadAt + ') — 시작한 해에 죽는 사람은 7월 뒤로');
ok(c1.name !== '도겸' && c1.past.join() === '도겸' && c1.lordOk && c1.inv.length === 0 && c1.age === 63, '뒤를 이은 사람(' + c1.name + ')의 이름이 세력의 이름이 된다 · 향년 63세');
const c2 = J(`(function () {
  newGame(0, 7, '194'); G.aiOnly = true;
  var a = N('하후돈'), b = N('순욱'), h = G.officers.filter(function (o) { return o.st === 'hidden'; })[0], out = {};
  a.dy = G.year; a.dm = 1; a.unit = 99999; lifeTick(); out.inUnit = a.st;                // 출진 중
  a.unit = null; lifeTick(); out.back = a.st;
  b.dy = G.year; b.dm = 1; b.st = 'travel'; b.dest = b.loc; lifeTick(); out.travel = b.st; b.st = 'active'; lifeTick(); out.arrived = b.st;
  var n0 = G.log.length; h.dy = G.year; h.dm = 1; lifeTick(); out.hidden = h.st; out.quiet = G.log.length === n0;
  var fr = N('배원소'); fr.dy = G.year; fr.dm = 1; n0 = G.log.length; lifeTick(); out.free = [fr.st, G.log.length === n0];
  var x = N('조인'); x.dy = G.year; x.dm = 1; G.life = 0; lifeTick(); out.off = x.st; G.life = 1; lifeTick(); out.on = x.st;
  out.adv = facAdv(0) ? facAdv(0).n : ''; out.inv = inv();
  return out;
})()`);
ok(c2.inUnit === 'active' && c2.back === 'dead' && c2.travel === 'travel' && c2.arrived === 'dead', '출진 · 이동 중에는 버티고, 거점에 돌아오면 숨을 거둔다');
ok(c2.hidden === 'dead' && c2.quiet && c2.free.join() === 'dead,true', '세상에 나오지 않은 사람 · 재야는 조용히 떠난다');
ok(c2.off === 'active' && c2.on === 'dead' && c2.adv !== '순욱' && c2.inv.length === 0, 'G.life 가 1 일 때만 · 군사가 죽으면 다른 사람이 맡는다(' + c2.adv + ')');

// ───────── D 후계 ─────────
console.log('D 후계');
const d1 = J(`(function () {
  var out = {};
  function rank(id, lord, n) { newGame(0, 9, id); G.aiOnly = true; var f = N(lord).f; return heirRank(f).slice(0, n || 3).map(function (o) { return o.n; }); }
  out.cao = rank('219', '조조', 4); out.sun = rank('200', '손책'); out.zj = rank('184', '장각'); out.lb = rank('207', '유표'); out.ys = rank('200', '원소'); out.gs = rank('219', '공손강'); out.lbei = rank('219', '유비'); out.dq = rank('194', '도겸', 2);
  // 219: 조조 → 조비
  newGame(0, 9, '219'); G.aiOnly = true;
  var L = N('조조'), loy0 = {}, b0 = {};
  facOfficers(0).forEach(function (o) { loy0[o.id] = o.loy; b0[o.id] = bondOf(o); });
  var fc = heirForecast(0, N('조비'));
  killNow(L);
  var F = G.factions[0], ch = { same: 0, down: 0, up: 0, bad: [] };
  facOfficers(0).forEach(function (o) { if (o.id === F.lord) return; var d = o.loy - loy0[o.id], nb = bondOf(o);
    if (b0[o.id] && !nb) ch.bad.push('끊김 ' + o.n);
    if (nb && o.loy !== 100) ch.bad.push('100 아님 ' + o.n);
    if (!nb && !b0[o.id]) { if (d === 0) ch.same++; else if (d < 0) { ch.down++; if (d < -12 || d > -4) ch.bad.push('폭 ' + o.n + d); } else { ch.up++; if (d < 3 || d > 6) ch.bad.push('폭 ' + o.n + d); } } });
  out.c = { name: F.name, past: F.past, heir: F.heir, hd: bondOf(N('하후돈')), xc: bondOf(N('허저')), ci: bondOf(N('조인')), smy: bondOf(N('사마의')), ch: ch, fc: [fc.kin, fc.house, fc.fam.length, fc.vas.length, fc.keep, fc.n, fc.p], inv: inv(), merit: off(F.lord).merit, loy: off(F.lord).loy, isLord: isLord(N('조비')), cap: G.bases[N('조비').loc].owner === 0 };
  return out;
})()`);
console.log('   차례: 조조 → ' + d1.cao.join(' · ') + ' | 손책 → ' + d1.sun.join(' · ') + ' | 장각 → ' + d1.zj.join(' · ') + ' | 유표 → ' + d1.lb.join(' · ') + ' | 원소 → ' + d1.ys.join(' · ') + ' | 공손강 → ' + d1.gs.join(' · ') + ' | 유비(219) → ' + d1.lbei.join(' · ') + ' | 도겸 → ' + d1.dq.join(' · '));
ok(d1.cao.slice(0, 3).join() === '조비,조창,조식', '조조의 뒤: 아들이 나이순으로(조비 · 조창 · 조식)');
ok(d1.sun[0] === '손권' && d1.zj[0] === '장보' && d1.lb[0] === '유기' && d1.ys[0] === '원담' && d1.gs[0] === '공손공', '아들이 없으면 형제(손책 → 손권, 공손강 → 공손공) · 혈연(장각 → 장보) · 맏아들(유표 → 유기, 원소 → 원담)');
ok(d1.c.name === '조비' && d1.c.past.join() === '조조' && d1.c.heir === -1 && d1.c.isLord && d1.c.merit >= 2000 && d1.c.loy === 100 && d1.c.inv.length === 0, '조조가 죽으면 조비가 잇고 세력의 이름이 조비가 된다');
ok(d1.c.hd === '혈연' && d1.c.ci === '혈연' && d1.c.xc === '세신' && d1.c.smy === '심복', '인연이 이어진다: 하후돈 · 조인 혈연, 허저(조조의 심복)는 세신, 사마의는 조비의 심복');
ok(d1.c.ch.bad.length === 0 && d1.c.fc[0] && d1.c.fc[1] && d1.c.fc[2] === 0 && d1.c.fc[3] === 0, '한집안이 이으면 인연이 끊기는 사람이 없다 — ' + d1.c.ch.bad.slice(0, 4).join(' '));
ok(d1.c.ch.same > 0 && d1.c.ch.down > 0, '인연이 없는 무장은 흔들리기도(' + d1.c.ch.down + '명, −4 ~ −12) 그대로이기도(' + d1.c.ch.same + '명) 한다 · 오른 사람 ' + d1.c.ch.up + '명 · 미리 본 확률 ' + d1.c.fc[6] + '%');
const d2 = J(`(function () {
  newGame(0, 9, '219'); G.player = 0;
  var L = N('조조'), sm = N('사마의'), out = {}, loy0 = {}, b0 = {};
  out.e1 = cmdHeir(L.id).ok; out.e2 = cmdHeir(N('관우').id).ok; out.set = cmdHeir(sm.id).ok && G.factions[0].heir === sm.id; out.off = cmdHeir(sm.id).off === true && G.factions[0].heir === -1; cmdHeir(sm.id);
  out.rank0 = heirRank(0)[0].n; out.heirOf = heirOf(0).n;
  facOfficers(0).forEach(function (o) { loy0[o.id] = o.loy; b0[o.id] = bondOf(o); });
  var fc = heirForecast(0, sm); out.fc = [fc.kin, fc.house, fc.fam.map(function (o) { return o.n; }).sort().join(), fc.vas.map(function (o) { return o.n; }).sort().join(), fc.keep];
  killNow(L);
  var F = G.factions[0], fam = [], vas = [], bad = [];
  facOfficers(0).forEach(function (o) { if (o.id === F.lord) return; var d = o.loy - loy0[o.id], was = b0[o.id], nb = bondOf(o);
    if (was && !nb) { if (was === '심복' || was === '세신') { vas.push(o.n); if (!(d === 0 || (d <= -8 && d >= -15))) bad.push('심복 ' + o.n + d); } else { fam.push(o.n); if (!(d <= -15 && d >= -25)) bad.push('일가 ' + o.n + d); } } });
  out.name = F.name; out.fam = fam.sort().join(); out.vas = vas.sort().join(); out.bad = bad; out.succ = G.succ ? [off(G.succ.heir).n, G.succ.kin, G.succ.house, G.succ.named, G.succ.rows.length > 0, G.succ.rows.every(function (r) { return off(r[0]).loy === r[2]; })] : null;
  out.cz = [loy0[N('조비').id], N('조비').loy, bondOf(N('조비'))]; out.log = G.log.filter(function (e) { return /뒤를 이었다/.test(e.t); }).map(function (e) { return e.t; }); out.inv = inv();
  return out;
})()`);
console.log('   ' + d2.log.join(' / ') + '  조비의 충성 ' + d2.cz.join(' → '));
ok(d2.e1 === false && d2.e2 === false && d2.set && d2.off && d2.rank0 === '사마의' && d2.heirOf === '사마의', '후계 정하기: 군주 자신 · 남의 무장은 안 된다 · 다시 고르면 풀린다 · 정해 두면 맨 앞 차례');
ok(d2.name === '사마의' && d2.succ && d2.succ.join() === '사마의,false,false,true,true,true', '정해 둔 후계(사마의)가 잇는다 — 혈연도 한집안도 아니다 · 내 세력이면 G.succ 에 충성의 변화가 남는다');
ok(d2.bad.length === 0 && d2.fam === d2.fc[2] && d2.vas === d2.fc[3] && d2.fam.split(',').length >= 8 && /조비/.test(d2.fam) && /허저/.test(d2.vas), '조씨 · 하후씨 일가 ' + d2.fam.split(',').length + '명은 15 ~ 25 내리고, 심복(' + d2.vas + ')은 그대로거나 8 ~ 15 내린다 — 미리 본 것과 같다 ' + d2.bad.slice(0, 3).join(' '));
ok(d2.cz[0] === 100 && d2.cz[1] <= 85 && d2.cz[2] === null && d2.inv.length === 0, '아들 조비도 인연이 끊겨 충성이 내린다(' + d2.cz[1] + ')');
const d3 = J(`(function () {
  newGame(2, 9, '194'); G.aiOnly = false;
  var out = {}, f = N('공융').f, L = N('공융');
  facOfficers(f).forEach(function (o) { if (o !== L) { o.f = -1; o.st = 'free'; } });
  var nb = facBases(f).length; killNow(L);
  out.kong = [G.factions[f].alive, facBases(f).length, nb, G.bases[baseByName('북해')].owner, G.bases[baseByName('북해')].troops, G.log.filter(function (e) { return /뒤를 이을 사람이 없다|멸망/.test(e.t); }).length, G.over];
  // 내 세력이 그렇게 되면 진다
  var me = G.player, ML = off(G.factions[me].lord);
  facOfficers(me).forEach(function (o) { if (o !== ML) { o.f = -1; o.st = 'free'; } });
  killNow(ML); out.me = [G.factions[me].alive, G.over]; out.inv = inv();
  // 포로가 된 무장은 뒤를 잇지 못한다 · 여성은 혈연이 아니면 맨 뒤
  newGame(0, 9, '194'); var f3 = N('도겸').f, L3 = N('도겸');
  var rk = heirRank(f3), w = rk.filter(function (o) { return isWoman(o); }), lastMan = -1, firstW = 99; rk.forEach(function (o, i) { if (isWoman(o)) firstW = Math.min(firstW, i); else lastMan = i; });
  out.women = [w.length, firstW > lastMan]; var top = rk[0]; top.st = 'captive'; out.cap = heirRank(f3)[0] !== top;
  return out;
})()`);
ok(d3.kong.join() === 'false,0,1,-1,0,2,', '뒤를 이을 무장이 없으면 세력이 사라지고 땅은 주인 없는 땅이 된다(공융)');
ok(d3.me.join() === 'false,lose' && d3.inv.length === 0, '내 세력이 그렇게 되면 패배');
ok(d3.women[0] >= 1 && d3.women[1] && d3.cap, '혈연이 아닌 여성은 맨 뒤 차례 · 포로는 뒤를 잇지 못한다');
const d4 = J(`(function () {
  var out = {};
  newGame(0, 9, '200'); G.aiOnly = true; var f = N('손책').f; killNow(N('손책'));
  out.sun = [G.factions[f].name, bondOf(N('주유')), bondOf(N('정보')), bondOf(N('손정')), N('주유').loy, G.factions[f].past.join('>'), facHouse(f)];
  newGame(0, 9, '207'); G.aiOnly = true; f = N('유비').f; killNow(N('유비'));
  out.shu = [G.factions[f].name, bondOf(N('장비')), bondOf(N('조운')), bondOf(N('미축'))];
  newGame(0, 9, '227'); G.aiOnly = true; f = N('유선').f;
  out.liushan = [bondOf(N('제갈량')), bondOf(N('조운')), bondOf(N('장완')), bondOf(N('관흥'))];
  out.caorui = [bondOf(N('사마의')), bondOf(N('조진')), bondOf(N('허저')), bondOf(N('진군'))];
  out.sunquan = [bondOf(N('육손')), bondOf(N('한당')), bondOf(N('제갈근'))];
  newGame(0, 9, '194'); out.b194 = G.officers.filter(function (o) { return o.id < 425 && o.f >= 0 && bondOf(o); }).map(function (o) { return o.n + bondOf(o); }).sort().join(',');
  return out;
})()`);
ok(d4.sun.join() === '손권,세신,세신,혈연,100,손견>손책,손견', '손책 → 손권: 주유(의형제) · 정보(심복)는 세신, 손정은 혈연 — 충성 100 그대로 · 집안은 손견');
ok(d4.shu.join() === '관우,의형제,세신,인척', '207년 유비 → 관우(의형제 — 한집안): 장비는 여전히 의형제, 조운은 세신, 미축은 인척으로 이어진다 — ' + d4.shu.join());
ok(d4.liushan.join() === '세신,세신,심복,세신' && d4.caorui.join() === '세신,혈연,세신,세신' && d4.sunquan.join() === '인척,세신,심복', '처음부터 대를 이은 군주(유선 · 조예 · 손권)도 선대의 인연을 물려받는다');
const b194 = J(`(function () { var m = {}; SCENARIO.factions.forEach(function (sf, k) { var L = sf.n, B = BONDS[L] || {}; SCENARIO.officers.forEach(function (o, i) { if (i < 425 && o.f === k && B[o.n]) m[o.n] = B[o.n]; }); }); return Object.keys(m).map(function (n) { return n + m[n]; }).sort().join(','); })()`);
ok(d4.b194 === b194, '194년 판에서 예전 425명의 인연은 달라지지 않았다(' + d4.b194.split(',').length + '명)');

// ───────── E 장성 ─────────
console.log('E 장성');
const e1 = J(`(function () {
  var out = {};
  newGame(0, 9, '190'); G.aiOnly = true; var sc = N('손책'), f = N('손견').f;
  while (G.year < 191) endTurn();
  out.sc = [sc.st, sc.f === f, sc.loy, bondOf(sc)];
  // 군주가 바뀌어도 집안으로 찾아간다
  newGame(0, 9, '200'); G.aiOnly = true; f = N('손책').f; killNow(N('손책')); var lx = N('능통'); lx.dad = null; lx.j = '손책'; lx.y = 201;
  while (G.year < 201) endTurn();
  out.house = [G.factions[f].name, lx.st, lx.f === f];
  // 아버지가 섬기는 세력으로
  newGame(0, 9, '194'); G.aiOnly = true; var gy = N('관우'), gp = N('관평'); gy.f = 0; gy.loc = off(G.factions[0].lord).loc; gp.y = 195;
  while (G.year < 195) endTurn();
  out.dad = [gp.dad, gp.st, gp.f, gy.f];
  var free = G.officers.filter(function (o) { return o.st === 'hidden' && !o.j && !o.dad && o.y <= G.year; }).length; out.stay = free > 0;
  return out;
})()`);
ok(e1.sc.join() === 'active,true,100,혈연', '190: 손책은 191년에 손견의 세력으로(아버지 · 혈연 — 충성 100)');
ok(e1.house.join() === '손권,active,true', '군주가 손권으로 바뀐 뒤에도 "손책"을 따르던 사람은 그 집안으로 간다');
ok(e1.dad[0] === '관우' && e1.dad[1] === 'active' && e1.dad[2] === e1.dad[3] && e1.stay, '아버지가 다른 세력을 섬기면 아이도 그 세력으로(관평 → 관우가 있는 곳) · 따라갈 곳이 없는 사람은 그대로 숨어 있다(탐색)');

// ───────── F 옛 저장 ─────────
console.log('F 옛 저장');
const f1 = J(`(function () {
  newGame(4, 11, '194'); G.aiOnly = true; for (var t = 0; t < 6; t++) endTurn();
  var g = JSON.parse(serialize());
  delete g.scen; delete g.life; g.factions.forEach(function (F) { delete F.n0; delete F.house; delete F.past; delete F.heir; });
  g.officers = g.officers.slice(0, 425); g.officers.forEach(function (o) { delete o.by; delete o.dy; delete o.dm; delete o.e; delete o.dad; delete o.sick; });
  g.year = 203;                                                    // 예전 판으로 203년까지 온 저장이라 치자
  scenarioUse('219');                                              // 다른 시대를 하고 있었더라도
  var okd = deserialize(JSON.stringify(g)), out = { ok: okd !== false, scen: G.scen, sy: SCENARIO.year, n: G.officers.length, life: G.life };
  var nw = G.officers.slice(425); out.newDead = nw.filter(function (o) { return o.st === 'dead'; }).length; out.zl = [N('주령').st, N('주령').f]; out.dz = N('동탁').st;
  out.by = G.officers.every(function (o) { return o.by && o.dy; }); out.fac = G.factions.every(function (F) { return F.n0 === F.name && F.house && F.heir === -1 && F.past; }); out.sun = G.factions[10].house + '/' + G.factions[10].past.join();
  var late = G.officers.filter(function (o) { return o.late; }); out.late = late.length; out.lateOk = late.every(function (o) { return o.dy > 203 && o.dy <= 203 + LIFE.old && o.st !== 'dead'; });
  out.none = G.officers.filter(function (o) { return o.st !== 'dead' && o.st !== 'hidden' && o.dy <= 203; }).length;
  var per = {}; G.aiOnly = true; for (var y = 0; y < 6; y++) { for (var m = 0; m < 12; m++) { G.month++; if (G.month > 12) { G.month = 1; G.year++; } lifeTick(); } }
  late.forEach(function (o) { if (o.st === 'dead') per[o.died] = (per[o.died] || 0) + 1; }); out.per = per; out.inv = inv(); out.log = G.log.filter(function (e) { return /무장이 늘었습니다/.test(e.t); }).map(function (e) { return e.t; });
  return out;
})()`);
console.log('   ' + f1.log.join(' / ') + ' · 수명이 지나 있던 사람 ' + f1.late + '명이 떠난 해: ' + JSON.stringify(f1.per));
ok(f1.ok && f1.scen === '194' && f1.sy === 194 && f1.n === 508 && f1.life === 1 && f1.by && f1.fac && f1.sun === '손견/손견', '예전 저장: 194년 판으로 열리고, 무장이 508명으로 늘고, 생몰년 · 집안이 붙는다');
ok(f1.newDead >= 25 && f1.dz === 'dead' && f1.zl[0] === 'active' && f1.zl[1] === 0, '새 무장: 이미 죽은 사람은 죽은 채로(' + f1.newDead + '명) · 주령은 조조의 세력으로');
ok(f1.late >= 5 && f1.lateOk && f1.none === 0 && Object.keys(f1.per).length >= 3 && f1.inv.length === 0, '이미 수명이 지난 ' + f1.late + '명은 한꺼번에 떠나지 않고 1 ~ ' + LIFE.old + '년에 걸쳐 떠난다');

// ───────── H 아이 ─────────
console.log('H 아이');
function BIRTH_TXT() { const B = J('BIRTH'); return B.min + ' ~ ' + B.max + '세'; }
const h1 = J(`(function () {
  var out = {};
  // 명부의 아이: 태어난 해에 알린다 → 등장 연도에 아버지의 세력으로
  newGame(2, 31, '200'); G.aiOnly = false; var ls = N('유선'), lb = N('유비');
  out.pre = [ls.st, ls.by, ls.y, ls.j, ls.dad];
  G.year = 206; G.month = 12; G.xun = 2; G.life = 0; EVQ = []; endTurn();
  out.note = G.log.filter(function (e) { return /유선/.test(e.t); }).map(function (e) { return e.d + ' ' + e.t + '#' + e.imp; });
  out.kidsOff = G.officers.length;                                 // 수명을 끈 판: 가상의 아이는 태어나지 않는다
  G.year = 221; G.month = 12; G.xun = 2; endTurn();
  out.debut = [ls.st, ls.f === lb.f, bondOf(ls), ls.loy, heirRank(lb.f)[0].n];
  // 가상의 아이
  newGame(0, 31, '194'); G.aiOnly = true; var p0 = BIRTH.p, l0 = BIRTH.lord, seed = G.seed;
  BIRTH.p = 100; BIRTH.lord = 100; G.year = 195;
  var elig = G.officers.filter(function (o) { var a = ageOf(o); return o.f >= 0 && o.st === 'active' && !isWoman(o) && a >= BIRTH.min && a <= BIRTH.max && o.n.length <= 3 && kidsOf(o).length < BIRTH.kids; });
  var n0 = G.officers.length; var made = birthTick(), kids = G.officers.slice(n0);
  out.made = [made, elig.length, kids.length, G.seed === seed];
  var names = {}; G.officers.forEach(function (o) { names[o.n] = (names[o.n] || 0) + 1; });
  out.dup = Object.keys(names).filter(function (n) { return names[n] > 1; });
  out.bad = kids.filter(function (k) { var f = N(k.dad); return !(k.kid === 1 && k.st === 'hidden' && k.f === -1 && k.by === 195 && k.y === 195 + BIRTH.grow && k.j === facHouse(f.f) && k.id === G.officers.indexOf(k) && k.n.indexOf(surnameOf(f.n)) === 0 && k.n.length === surnameOf(f.n).length + 1
    && ['ldr', 'war', 'int', 'pol', 'cha'].every(function (s) { return k[s] >= 20 && k[s] <= 97 && Math.abs(k[s] - (f[s] * BIRTH.inh + 60 * (1 - BIRTH.inh))) <= BIRTH.vr + 1; })
    && /^[SABC]{5}$/.test(k.apt) && (!k.sk || SKILLS[k.sk]) && (k.sex === 'f' ? /^gf[1-5][0-9][0-9]$/ : /^gm[1-5][0-9][0-9]$/).test(k.por) && k.dy >= k.by + BIRTH.life[0] && k.dy <= k.by + BIRTH.life[1] && k.dm >= 1 && k.dm <= 12 && G.bases[k.loc].kind === 'city' && bioOf(k).length >= 20); }).map(function (k) { return k.n; });
  var cc = N('조조'), ck = kids.filter(function (k) { return k.dad === '조조'; })[0], zg = kids.filter(function (k) { return /^(하후|공손)/.test(k.n); }).map(function (k) { return k.dad + '→' + k.n; });
  out.cao = ck ? [ck.n, ck.ldr, ck.war, ck.int, ck.pol, ck.cha, ck.apt, ck.sk, ck.por] : null; out.two = zg.slice(0, 3);
  out.noW = kids.every(function (k) { return !isWoman(N(k.dad)); }); out.skIn = kids.filter(function (k) { return k.sk && k.sk === N(k.dad).sk; }).length; out.skNone = kids.filter(function (k) { return !k.sk; }).length;
  // 한 사람에게 BIRTH.kids 명까지(명부의 자식도 센다)
  for (var y = 196; y <= 199; y++) { G.year = y; birthTick(); }
  out.cap = Math.max.apply(null, elig.map(function (o) { return kidsOf(o).length; })); out.caoKids = kidsOf(cc).map(function (k) { return k.n; });
  BIRTH.p = p0; BIRTH.lord = l0;
  // 장성: 등장 연도에 아버지의 세력으로 · 군주의 아들은 혈연이고 뒤를 잇는 맨 앞 차례
  var mk = kidsOf(N('유비')).filter(function (k) { return k.kid; })[0], f = N('유비').f; mk.y = 200; G.year = 199; G.month = 12; G.xun = 2; G.life = 0; endTurn();
  out.join = [mk.st, mk.f === f, bondOf(mk), mk.loy, heirRank(f)[0] === mk, G.log.some(function (e) { return e.t.indexOf(mk.n + '이 장성하여') === 0 || e.t.indexOf(mk.n + '가 장성하여') === 0; })];
  // 저장
  var sv = serialize(), n1 = G.officers.length; deserialize(sv);
  out.save = [G.officers.length === n1, G.officers.every(function (o, i) { return o.id === i; }), N(mk.n).kid === 1, N(mk.n).dad, bioOf(N(mk.n))];
  // 수명 켬 · 끔
  newGame(0, 31, '194', false); out.off = G.life; G.year = 230; lifeTick(); out.offAlive = N('도겸').st; var on = lifeSet(true);
  var late = G.officers.filter(function (o) { return o.late; }); out.on = [on, G.life, late.length > 50, late.every(function (o) { return o.dy > 230 && o.dy <= 230 + LIFE.old; })];
  lifeTick(); out.onAlive = N('도겸').st; out.back = [lifeSet(false), G.life];
  return out;
})()`);
console.log('   ' + h1.note.join(' / ') + ' · 조조의 아이 ' + JSON.stringify(h1.cao) + ' · 두 글자 성 ' + h1.two.join(' ') + ' · 조조의 자식 ' + h1.caoKids.join(' '));
ok(h1.pre.join() === 'hidden,207,222,유비,유비' && h1.note.length === 1 && /^207년 1월 상순 유비에게 아들 유선이 태어났다#1$/.test(h1.note[0]) && h1.kidsOff === 508, '명부의 아이: 유선은 207년에 태어났다고 알린다(수명을 꺼도) · 수명을 끈 판에서는 가상의 아이가 태어나지 않는다');
ok(h1.debut.join() === 'active,true,혈연,100,유선', '222년에 유비의 세력으로 장성 — 혈연 · 충성 100 · 뒤를 이을 맨 앞 차례');
ok(h1.made[0] === h1.made[1] && h1.made[2] === h1.made[0] && h1.made[0] > 100 && h1.made[3], '가상의 아이: 확률을 100%로 두면 벼슬하는 남자 무장(' + BIRTH_TXT() + ') ' + h1.made[1] + '명 모두에게서 · 판의 난수는 쓰지 않는다');
ok(h1.dup.length === 0 && h1.bad.length === 0 && h1.noW, '이름이 겹치지 않고(아버지의 성 + 한 글자), 능력은 아버지를 닮고(±' + J('BIRTH.vr') + '), 숨은 채로 15년 뒤를 기다린다 — ' + h1.dup.concat(h1.bad).slice(0, 5).join(' '));
ok(h1.two.length >= 1 && h1.two.every(x => /→(하후|공손)./.test(x)) && h1.skIn > 10 && h1.skNone > 30, '두 글자 성(하후 · 공손)을 따른다 · 특기는 물려받기도(' + h1.skIn + '명) 없기도(' + h1.skNone + '명)');
ok(h1.cap === 3 && h1.cao === null && h1.caoKids.join() === '조비,조창,조식,조절', '한 사람에게 3명까지 — 명부의 자식도 센다(조조는 이미 넷이라 더 태어나지 않는다)');
ok(h1.join.join() === 'active,true,혈연,100,true,true', '가상의 아이도 장성하면 아버지의 세력으로 — 군주의 아들은 혈연이고 뒤를 이을 맨 앞 차례');
ok(h1.save[0] && h1.save[1] && h1.save[2] && h1.save[3] === '유비' && /유비의 아들\. 19\d년에 이 판에서 태어났다/.test(h1.save[4]), '저장하고 다시 열어도 아이가 그대로다 · 열전: ' + h1.save[4]);
ok(h1.off === 0 && h1.offAlive === 'active' && h1.on.join() === 'true,1,true,true' && h1.onAlive === 'active' && h1.back.join() === 'false,0', '수명을 끈 판: 230년이 되어도 도겸이 살아 있다 · 켜면 수명이 지난 사람은 1 ~ ' + LIFE.old + '년에 걸쳐 떠난다 · 다시 끌 수 있다');

// ───────── G AI 끼리 ─────────
console.log('G 시대마다 AI 끼리 ' + SIMY + '년');
for (const s of SC) {
  const t0 = Date.now();
  const r = J(`(function () {
    newGame(0, 23, '${s.id}'); G.aiOnly = true;
    var y0 = G.year, err = '', bad = [], t = 0, succ = 0;
    try { while (G.year < y0 + ${SIMY} && !G.over && t < 2000) { endTurn(); t++; if (G.xun === 0 && G.month % 3 === 1) { var b = inv(); if (b.length) { bad = bad.concat(b.slice(0, 3)); break; } } } } catch (e) { err = String(e && e.stack || e).slice(0, 300); }
    G.factions.forEach(function (F) { if (F.past && F.past.length > (SCENARIO.factions[F.id].anc || []).length) succ++; });
    return { y: G.year, err: err, bad: bad, succ: succ, kids: G.officers.filter(function (o) { return o.kid; }).length, grown: G.officers.filter(function (o) { return o.kid && o.st !== 'hidden'; }).length, dead: G.officers.filter(function (o) { return o.st === 'dead' && o.died >= y0; }).length, alive: G.factions.filter(function (F) { return F.alive; }).map(function (F) { return F.name; }).join(' ') };
  })()`);
  ok(!r.err && r.bad.length === 0 && r.y >= s.year + SIMY, s.year + '년 ' + s.name + ': ' + SIMY + '년 — 오류 없음 ' + (r.err || r.bad.join(' | ')));
  console.log('   ' + s.year + ' → ' + r.y + ': 세상을 떠난 사람 ' + r.dead + '명 · 태어난 아이 ' + r.kids + '명(장성 ' + r.grown + ') · 군주가 바뀐 세력 ' + r.succ + ' · 남은 세력 ' + r.alive + '  (' + ((Date.now() - t0) / 1000).toFixed(0) + '초)');
}
console.log('\nv23: ' + pass + ' pass, ' + fail + ' fail');
process.exit(fail ? 1 : 0);
