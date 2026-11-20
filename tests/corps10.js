// v0.10 — 군단의 규칙과 군단장의 판단(core.js · ai.js)
//   node tests/corps10.js
// 화면 없이 규칙만: 만들기 · 넣고 빼기 · 해산 · 군단장 · 행동력 · 방침 넷 · 차례(턴 진행) · 직할을 건드리지 않는가 · 차지한 거점 · 잃은 거점 · 저장 · AI 세력이 그대로인가
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = process.env.SRC || path.join(__dirname, '..', 'src');
function fresh() {
  const ctx = { console, Math, JSON, Date, Object, Array, String, Number, isNaN, parseInt, parseFloat };
  vm.createContext(ctx);
  for (const f of ['mapdata.js', 'roster.js', 'data.js', 'core.js', 'ai.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
  vm.runInContext(`
    var FAILS = [], CHECKS = 0;
    function chk(name, cond, info) { CHECKS++; if (!cond) { FAILS.push(name + (info !== undefined ? ' [' + (typeof info === 'string' ? info : JSON.stringify(info)) + ']' : '')); console.log('  FAIL ' + name + (info !== undefined ? ' [' + (typeof info === 'string' ? info : JSON.stringify(info)) + ']' : '')); } else console.log('  ok   ' + name + (info !== undefined ? ' [' + (typeof info === 'string' ? info : JSON.stringify(info)) + ']' : '')); }
    function B(n) { return G.bases[baseByName(n)]; }
    function lordBase() { return G.bases[off(G.factions[G.player].lord).loc]; }
    /* 군단의 차례만 돌린다(다른 세력은 움직이지 않는다) */
    function corpsOnly() {
      REPORT = []; EVQ = [];
      var cps = G.corps.slice(), n = 0;
      for (var i = 0; i < cps.length; i++) { if (!corpsStart(cps[i])) continue; var st = corpsStepper(cps[i]); while (st()) n++; corpsEnd(cps[i]); }
      return n;
    }
    function snapDirect() {
      return JSON.stringify(directBases(G.player).map(function (b) { return [b.id, b.troops, b.gold, b.food, b.order, b.morale, JSON.stringify(b.w), b.plots.map(function (p) { return p.fac ? p.fac.t + p.fac.lv + (p.fac.done ? 'd' : 'c') : '-'; }).join(''), baseOfficers(b).map(function (o) { return o.id + (o.acted ? 'a' : 'i'); }).join(',')]; })) + '|' + G.factions[G.player].ap + '|' + directUnits(G.player).map(function (u) { return u.id + ':' + u.c + ',' + u.r + ':' + u.troops + ':' + u.done; }).join(';');
    }
  `, ctx);
  return ctx;
}
let total = 0, fails = [];
function part(title, code) {
  console.log('\n' + title);
  const ctx = fresh();
  vm.runInContext(code, ctx);
  total += ctx.CHECKS; fails = fails.concat(ctx.FAILS);
}

part('1. 만들기 · 넣고 빼기 · 해산', `
  newGame(4, 4242);                                  // 원소: 남피 · 평원 · 업(군주)
  var lb = lordBase(), others = facCities(G.player).filter(function (b) { return b !== lb; });
  chk('처음에는 군단이 없다', corpsAll().length === 0 && directBases(G.player).length === 3);
  chk('남의 거점은 맡길 수 없다', !corpsCreate([B('북해').id]).ok && corpsAll().length === 0);
  chk('거점을 고르지 않으면 안 된다', !corpsCreate([]).ok);
  var r = corpsCreate([others[0].id]), cp = r.corps;
  chk('거점 하나로 군단을 만든다', r.ok && corpsName(cp) === '제1군단' && corpsBases(cp).length === 1 && others[0].corps === cp.id && cp.dir === 'arm' && cp.target === -1, corpsName(cp));
  chk('군단장은 그 거점의 무장 가운데 가장 알맞은 사람(군주는 아니다)', corpsLead(cp) && !isLord(corpsLead(cp)) && corpsLead(cp).loc === others[0].id && corpsLead(cp) === corpsLeadCands(cp)[0], corpsLead(cp).n);
  chk('이미 맡긴 거점은 다시 새 군단에 넣을 수 없다', !corpsCreate([others[0].id]).ok);
  chk('직할 거점 · 군단 거점이 갈린다', directBases(G.player).length === 2 && baseCorps(others[0]) === cp && baseCorps(lb) === null && baseCorps(B('북해')) === null);
  var r2 = corpsCreate([others[1].id]);
  chk('둘째 군단은 제2군단', r2.ok && corpsName(r2.corps) === '제2군단' && corpsAll().length === 2);
  chk('거점을 다른 군단으로 옮기면 빈 군단은 해산된다', corpsAssign(cp, others[1].id).ok && corpsBases(cp).length === 2 && !corpsById(r2.corps.id) && corpsAll().length === 1);
  var r3 = corpsCreate([lb.id]);
  chk('군주만 있는 것은 아니므로 군주가 있는 거점도 맡길 수 있다(군단장은 다른 무장)', r3.ok && !isLord(corpsLead(r3.corps)), r3.ok ? corpsLead(r3.corps).n : r3.msg);
  chk('번호는 비어 있는 가장 작은 수', corpsName(r3.corps) === '제2군단');
  corpsDisband(r3.corps);
  chk('해산하면 거점이 직할로', !corpsById(r3.corps.id) && !lb.corps && baseCorps(lb) === null);
  var rr = corpsRelease(others[1].id);
  chk('거점을 직할로 되돌린다(군단은 남는다)', rr.ok && !rr.gone && !others[1].corps && corpsBases(cp).length === 1);
  var rr2 = corpsRelease(others[0].id);
  chk('마지막 거점을 되돌리면 군단이 해산된다', rr2.ok && rr2.gone && corpsAll().length === 0 && directBases(G.player).length === 3);
  chk('직할 거점을 또 되돌리려 하면 거절', !corpsRelease(others[0].id).ok);
  // 군단장을 맡을 무장이 없는 거점
  var ob = others[0], moved = baseOfficers(ob); moved.forEach(function (o) { o.loc = lb.id; });
  var r4 = corpsCreate([ob.id]);
  chk('무장이 없는 거점만으로는 군단을 만들 수 없다(표시도 남지 않는다)', !r4.ok && !ob.corps && corpsAll().length === 0, r4.msg);
  moved.forEach(function (o) { o.loc = ob.id; });
  var made = 0; for (var k = 0; k < 10; k++) { var q = corpsCreate([others[0].id]); if (q.ok) { made++; corpsRelease(others[0].id); } }
  chk('만들고 없애기를 되풀이해도 번호는 1 (id 는 새로)', made === 10 && corpsAll().length === 0 && G.nextCorps > 10);
  var ids = []; G.aiOnly = true; chk('AI 대전에는 군단이 없다', !corpsCreate([others[0].id]).ok); G.aiOnly = false;
`);

part('2. 군단장', `
  newGame(4, 4242);
  var lb = lordBase(), others = facCities(G.player).filter(function (b) { return b !== lb; });
  var cp = corpsCreate([others[0].id, others[1].id]).corps, L0 = corpsLead(cp);
  var cands = corpsLeadCands(cp);
  chk('후보 = 군단의 거점에 있는 무장(군주 제외)', cands.length === baseOfficers(others[0]).length + baseOfficers(others[1]).length && cands.every(function (o) { return !isLord(o); }), cands.length);
  chk('다른 거점의 무장 · 군주는 군단장이 될 수 없다', !corpsSetLead(cp, off(G.factions[G.player].lord).id).ok && !corpsSetLead(cp, baseOfficers(lb).filter(function (o) { return !isLord(o); })[0].id).ok);
  var L1 = cands[cands.length - 1];
  chk('군단장을 바꾼다', corpsSetLead(cp, L1.id).ok && corpsLead(cp) === L1);
  var reg1 = corpsRegen(cp);
  chk('행동력 회복 = 20 + 도시 × 8 + 군단장 매력 ÷ 5', reg1 === Math.min(CORPS_AP.max, CORPS_AP.base + CORPS_AP.city * 2 + Math.floor(L1.cha / 5)), reg1);
  // 군단장이 자리를 비운다: 직할 거점으로 옮김
  L1.loc = lb.id; REPORT = [];
  corpsFix();
  chk('군단장이 군단 밖으로 가면 다음 사람이 맡는다 + 기록', corpsLead(cp) && corpsLead(cp) !== L1 && corpsLead(cp) === corpsLeadCands(cp)[0] && REPORT.some(function (e) { return /군단장을 맡았다/.test(e.t) && e.f === G.player; }), REPORT.map(function (e) { return e.t; }));
  // 군단장이 부대를 이끌고 나가도 군단장이다
  var L2 = corpsLead(cp), hb = G.bases[L2.loc]; hb.w.spear = 9000; G.factions[G.player].ap = 200;
  var u = cmdDeploy(hb, { type: 'spear', ids: [L2.id], troops: 2000, food: 2000 }).unit;
  chk('직할로 낸 부대에 있으면 군단장이 아니다', !corpsLeadOk(cp, L2));
  u.corps = cp.id;
  chk('군단의 부대에 있으면 군단장이다', corpsLeadOk(cp, L2) && corpsLead(cp) === L2);
  // 군단에 무장이 하나도 없게 되면
  corpsOfficers(cp).forEach(function (o) { if (o.unit === null) o.loc = lb.id; }); removeUnit(u); L2.unit = null; L2.loc = lb.id; REPORT = [];
  corpsFix();
  chk('맡을 무장이 없으면 자리가 빈 채로 남고 기록에 알린다(군단은 남는다)', corpsById(cp.id) && cp.lead === -1 && corpsLead(cp) === null && REPORT.some(function (e) { return /군단장 자리가 비었습니다/.test(e.t) && e.imp === 2; }));
  chk('군단장이 없으면 매력 몫 없이 회복', corpsRegen(cp) === CORPS_AP.base + CORPS_AP.city * 2);
`);

part('3. 행동력: 직할과 군단이 따로', `
  newGame(4, 4242);
  var lb = lordBase(), others = facCities(G.player).filter(function (b) { return b !== lb; });
  var r0 = apRegen(G.player);
  var cp = corpsCreate([others[0].id, others[1].id]).corps;
  var r1 = apRegen(G.player);
  chk('직할의 회복은 직할 도시만 센다(도시 둘을 맡기면 −16)', r0 - r1 === 16, [r0, r1]);
  var d0 = G.factions[G.player].ap, snap = snapDirect();
  cp.ap = 0;
  var steps = corpsOnly();
  chk('군단의 차례가 돌았다', steps >= 1 && cp.note && cp.note.t === G.turn, [steps, cp.note && cp.note.s]);
  chk('군단은 제 행동력만 쓴다 — 직할의 행동력은 그대로', G.factions[G.player].ap === d0, [d0, G.factions[G.player].ap]);
  chk('군단의 행동력: 회복한 만큼에서 쓴 만큼 줄었다(0 이상, 회복량 이하)', cp.ap >= 0 && cp.ap <= corpsRegen(cp), cp.ap);
  chk('직할 거점 · 직할 무장 · 직할 부대는 손대지 않았다', snapDirect() === snap);
  chk('군단의 거점에서는 일이 있었다', cp.note.n > 0 && corpsBases(cp).some(function (b) { return baseOfficers(b).some(function (o) { return o.acted; }); }), cp.note.s);
  // 내가 직할 거점에서 명령해도 군단의 행동력은 그대로
  var a0 = cp.ap, f0 = G.factions[G.player].ap, io = idleOfficers(lb).filter(function (o) { return !isLord(o); })[0];
  var rp = cmdPatrol(lb, [io.id]);
  chk('직할의 명령은 직할의 행동력만 쓴다', rp.ok && cp.ap === a0 && G.factions[G.player].ap === f0 - AP.patrol);
  chk('한 일을 적는 장부는 차례가 끝나면 닫힌다', JOT === null);
  cp.ap = 250; corpsOnly();
  chk('행동력은 255 까지만 쌓인다', cp.ap <= 255);
  corpsDisband(cp);
  chk('해산하면 직할의 회복이 되돌아온다', apRegen(G.player) === r0);
`);

part('4. 방침 — 내정 · 군비', `
  newGame(4, 4242);
  var lb = lordBase(), others = facCities(G.player).filter(function (b) { return b !== lb; });
  var cp = corpsCreate([others[0].id, others[1].id]).corps;
  chk('없는 방침 · 목표 없는 공격 · 제 거점으로의 지원은 거절', !corpsSetDir(cp, 'xx', -1).ok && !corpsSetDir(cp, 'atk', -1).ok && !corpsSetDir(cp, 'atk', lb.id).ok && !corpsSetDir(cp, 'sup', others[0].id).ok && !corpsSetDir(cp, 'sup', B('북해').id).ok);
  // 내정: 병력이 8,000 을 넘으면 더 모으지 않는다 / 시설은 짓는다
  corpsSetDir(cp, 'dev', -1);
  others.forEach(function (b) { b.troops = 9000; b.gold = 5000; b.order = 80; b.morale = 80; });
  var t0 = others.map(function (b) { return b.troops; }), fac0 = others.map(function (b) { return b.plots.filter(function (p) { return p.fac; }).length; }), built = 0, drafted = 0;
  for (var k = 0; k < 6; k++) { cp.ap = 200; baseOfficers(others[0]).concat(baseOfficers(others[1])).forEach(function (o) { if (!jobOf(o)) o.acted = false; }); others.forEach(function (b) { b.gold = 5000; }); corpsOnly(); if (/징병/.test(cp.note.s)) drafted++; if (/착공/.test(cp.note.s)) built++; }
  chk('내정: 병력 9,000 인 도시에서는 징병하지 않는다', drafted === 0 && others.every(function (b, i) { return b.troops === t0[i]; }), others.map(function (b) { return b.troops; }));
  var nDev = others.map(function (b, i) { return b.plots.filter(function (p) { return p.fac; }).length - fac0[i]; });
  chk('내정: 시설을 짓는다(도시마다 한꺼번에 둘 넘게도 벌인다)', built >= 1 && nDev[0] + nDev[1] >= 3, nDev);
  // 군비: 전선이 아니어도 한도까지 모은다
  corpsSetDir(cp, 'arm', -1); drafted = 0;
  for (k = 0; k < 6; k++) { cp.ap = 200; baseOfficers(others[0]).concat(baseOfficers(others[1])).forEach(function (o) { if (!jobOf(o)) o.acted = false; }); others.forEach(function (b) { b.gold = 5000; b.order = 80; }); corpsOnly(); if (/징병/.test(cp.note.s)) drafted++; }
  chk('군비: 같은 도시에서 징병한다', drafted >= 3 && others.some(function (b, i) { return b.troops > t0[i]; }), [drafted, others.map(function (b) { return b.troops; })]);
  chk('내정 · 군비는 부대를 내지 않는다(적이 없을 때)', corpsUnits(cp).length === 0);
  chk('방침을 말로', corpsDirText(cp) === '군비' && CORPS_DIR.dev === '내정');
`);

part('5. 방침 — 공격', `
  newGame(4, 4242);
  var lb = lordBase(), others = facCities(G.player).filter(function (b) { return b !== lb; });
  var cp = corpsCreate([others[0].id, others[1].id]).corps, T = B('북해');
  others.forEach(function (b) { b.troops = 12000; b.morale = 80; b.gold = 8000; b.food = 200000; b.w.spear = 12000; b.w.halberd = 12000; b.w.bow = 12000; b.w.horse = 6000; });
  T.troops = 30000;
  chk('공격 방침을 준다', corpsSetDir(cp, 'atk', T.id).ok && cp.dir === 'atk' && cp.target === T.id && corpsDirText(cp) === '공격 → 북해');
  var o = corpsOutlook(cp, T), len = Math.min(routeLen(others[0], T), routeLen(others[1], T));
  var bestD = 0; baseOfficers(T).forEach(function (x) { bestD = Math.max(bestD, x.war, x.ldr); });
  var fk = 1 + Math.max(0, bestD - 75) / 50;
  chk('필요한 병력 = (수비 + 가는 동안 늘어날 몫) × mul × (지키는 장수의 몫) + add', o.need === Math.round((30000 + CORPS_ATK.grow * Math.ceil(len / 5)) * CORPS_ATK.mul * fk + CORPS_ATK.add) && o.k === fk && o.have === 18000 && o.going === 0, [o, bestD]);
  // 지키는 장수의 몫 · 밖에 나와 있는 부대
  var ldr0 = baseOfficers(T)[0], w0 = ldr0.war; ldr0.war = 100;
  chk('지키는 장수의 무력이 100 이면 문턱이 1.5배 몫', corpsFoeK(T) === 1.5 && corpsOutlook(cp, T).need > o.need);
  ldr0.war = w0;
  var eo = baseOfficers(T).filter(function (x) { return !isLord(x); })[0]; T.w.spear = 9000; G.factions[T.owner].ap = 200;
  var eu = cmdDeploy(T, { type: 'spear', ids: [eo.id], troops: 3000, food: 3000 }).unit;
  chk('성 밖에 나와 있는 부대(12칸 안)도 수비로 센다', corpsDef(T) === T.troops + 3000 && T.troops === 27000);
  T.troops += 3000; removeUnit(eu); eo.unit = null;
  cp.ap = 200; corpsOnly();
  chk('모자라면 나서지 않고 까닭을 적어 둔다(병력)', corpsUnits(cp).length === 0 && cp.wait && cp.wait.need > cp.wait.have && !cp.wait.ap, cp.wait);
  chk('기다리는 동안 내정은 한다', cp.note.n > 0, cp.note.s);
  // 수비를 줄인다 → 병력은 차지만 행동력이 모자라면 아낀다
  T.troops = 500; others.forEach(function (b) { b.troops = 16000; }); baseOfficers(others[0]).concat(baseOfficers(others[1])).forEach(function (x) { if (!jobOf(x)) x.acted = false; });
  cp.ap = 0; var ap0 = corpsRegen(cp);
  corpsOnly();
  chk('병력은 찼어도 행동력이 60 아래면 나서지 않고 그 턴의 내정도 쉰다(모은다)', corpsUnits(cp).length === 0 && cp.wait && cp.wait.ap === 1 && cp.ap === ap0 && cp.note.n === 0, [cp.wait, cp.ap, ap0, cp.note.s]);
  baseOfficers(others[0]).concat(baseOfficers(others[1])).forEach(function (x) { if (!jobOf(x)) x.acted = false; });
  cp.ap = 120; var br0 = !!G.peace.broken[T.owner];
  corpsOnly();
  var us = corpsUnits(cp);
  chk('행동력이 모이면 나선다 — 군단의 부대, 목표는 그 거점', us.length >= 2 && us.every(function (u) { return u.corps === cp.id && u.ai && u.ai.mode === 'attack' && u.ai.target === T.id; }) && /부대 출진/.test(cp.note.s), [us.length, cp.note.s]);
  chk('나간 부대는 직할 부대가 아니다(명령 대기에도 들지 않는다)', directUnits(G.player).length === 0 && us.every(function (u) { return unitCorps(u) === cp; }));
  chk('셋째 부대부터는 노병을 섞는다(재고가 있을 때)', us.length < 3 || us.some(function (u) { return u.type === 'bow'; }), us.map(function (u) { return u.type; }));
  // 방침을 바꾸면 나가 있는 부대도 따른다
  corpsSetDir(cp, 'arm', -1);
  chk('방침을 군비로 돌리면 가던 부대는 돌아온다', us.every(function (u) { return u.ai.mode === 'return'; }));
  corpsSetDir(cp, 'atk', T.id);
  chk('다시 공격을 주면 다시 그 거점으로', us.every(function (u) { return u.ai.mode === 'attack' && u.ai.target === T.id; }));
  // 부대를 직할로
  var u0 = us[0];
  chk('부대를 직할로 되돌린다', corpsTakeUnit(u0).ok && !u0.corps && u0.ai === null && directUnits(G.player).length === 1 && !corpsTakeUnit(u0).ok);
  u0.corps = cp.id; u0.ai = { mode: 'attack', target: T.id, home: u0.home };
  // 끝까지: 다른 세력은 멈춰 두고 군단만 돌린다 → 차지하면 그 군단의 거점이 되고 방침은 군비로
  var fell = 0;
  for (var k = 0; k < 14 && !fell; k++) {
    G.turn++; facUnits(G.player).forEach(function (u) { u.mp = uMaxMp(u); u.done = false; u.moved = false; });
    T.troops = Math.min(T.troops, 2500);
    cp.ap = 100; corpsOnly();
    if (T.owner === G.player) fell = k + 1;
  }
  chk('수비가 얇은 거점을 차지한다', fell > 0, fell);
  chk('군단의 부대가 차지한 거점은 그 군단에 든다', T.corps === cp.id && baseCorps(T) === cp && corpsBases(cp).length === 3);
  chk('목표를 손에 넣으면 방침은 군비로 돌아간다 + 중요한 일로 기록', cp.dir === 'arm' && cp.target === -1 && G.log.some(function (e) { return /손에 넣어 방침을 군비로/.test(e.t) && e.imp === 2; }));
  chk('먼저 쳤으므로 그 세력과의 보호가 풀렸다(내가 칠 때와 같다)', !br0 && Object.keys(G.peace.broken).length >= 1, Object.keys(G.peace.broken));
`);

part('6. 방침 — 공격: 빈 거점 · 직할 부대가 차지한 거점', `
  newGame(4, 4242);
  var lb = lordBase(), others = facCities(G.player).filter(function (b) { return b !== lb; });
  var cp = corpsCreate([others[0].id]).corps;
  var E = G.bases.filter(function (b) { return b.owner === -1; }).sort(function (x, y) { return hdist(others[0].c, others[0].r, x.c, x.r) - hdist(others[0].c, others[0].r, y.c, y.r); })[0];
  chk('(준비) 가까운 빈 거점', !!E, E && E.n);
  corpsSetDir(cp, 'atk', E.id);
  var o = corpsOutlook(cp, E);
  chk('빈 거점은 병력 600 이면 나선다', o.need === 600, o);
  cp.ap = 30; corpsOnly();
  var us = corpsUnits(cp);
  chk('한 부대가 차지하러 나선다(행동력 60 을 기다리지 않는다)', us.length === 1 && us[0].ai.mode === 'attack' && us[0].ai.target === E.id && us[0].troops <= 3000, us.map(function (u) { return [u.type, u.troops]; }));
  var got = 0;
  for (var k = 0; k < 20 && !got; k++) { G.turn++; facUnits(G.player).forEach(function (u) { u.mp = uMaxMp(u); u.done = false; u.moved = false; }); cp.ap = 50; corpsOnly(); if (E.owner === G.player) got = k + 1; }
  chk('빈 거점을 차지해 군단에 넣는다', got > 0 && E.corps === cp.id && cp.dir === 'arm', [got, E.owner]);
  // 직할 부대가 차지한 거점은 직할
  var E2 = G.bases.filter(function (b) { return b.owner === -1; })[0], u = cmdDeploy(lb, { type: 'spear', ids: [idleOfficers(lb).filter(function (x) { return !isLord(x); })[0].id], troops: 1000, food: 1000 });
  lb.w.spear = 5000; G.factions[G.player].ap = 200;
  u = cmdDeploy(lb, { type: 'spear', ids: [idleOfficers(lb).filter(function (x) { return !isLord(x); })[0].id], troops: 1000, food: 1000 }).unit;
  captureBase(E2, u);
  chk('직할 부대가 차지한 거점은 직할', E2.owner === G.player && !E2.corps && baseCorps(E2) === null);
`);

part('7. 방침 — 지원', `
  newGame(4, 4242);
  var lb = lordBase(), others = facCities(G.player).filter(function (b) { return b !== lb; });
  var cp = corpsCreate([others[0].id, others[1].id]).corps;
  chk('지원 방침을 준다(직할 거점으로)', corpsSetDir(cp, 'sup', lb.id).ok && corpsDirText(cp) === '지원 → ' + lb.n);
  others.forEach(function (b) { b.troops = 12000; b.gold = 6000; b.food = 60000; b.w.spear = 4000; });
  while ((G.turn + cp.id) % 3 !== 1) G.turn++;
  var g0 = lb.gold, t0 = lb.troops, f0 = lb.food;
  cp.ap = 200; corpsOnly();
  chk('보내는 달이 아니면 수송대를 내지 않는다', corpsUnits(cp).length === 0);
  while ((G.turn + cp.id) % 3 !== 0) G.turn++;
  baseOfficers(others[0]).concat(baseOfficers(others[1])).forEach(function (x) { if (!jobOf(x)) x.acted = false; });
  cp.ap = 200; corpsOnly();
  var us = corpsUnits(cp);
  chk('보내는 달: 도시마다 수송대 — 병력은 3,000 을 남기고, 금 · 병량 · 병기도 싣는다', us.length === 2 && us.every(function (u) { return u.type === 'trans' && u.corps === cp.id && u.ai.mode === 'supply' && u.ai.target === lb.id && u.gold > 0 && u.cargo.spear > 0; }) && others.every(function (b) { return b.troops >= 3000 && b.troops < 12000; }) && /수송 2대/.test(cp.note.s), [us.map(function (u) { return [u.type, u.troops, u.gold]; }), others.map(function (b) { return b.troops; }), cp.note.s]);
  chk('군단장과 군주는 수송대를 이끌지 않는다', us.every(function (u) { return uLeader(u).id !== cp.lead && !isLord(uLeader(u)); }));
  var sentT = us.reduce(function (a, u) { return a + u.troops; }, 0), sentG = us.reduce(function (a, u) { return a + u.gold; }, 0), arr = 0;
  for (var k = 0; k < 20 && corpsUnits(cp).length; k++) { G.turn++; facUnits(G.player).forEach(function (u) { u.mp = uMaxMp(u); u.done = false; u.moved = false; }); while ((G.turn + cp.id) % 3 === 0) G.turn++; cp.ap = 20; corpsOnly(); }
  chk('수송대가 도착하면 병력과 금이 그 거점에 합쳐진다', corpsUnits(cp).length === 0 && lb.troops === t0 + sentT && lb.gold === g0 + sentG, [lb.troops - t0, sentT, lb.gold - g0, sentG]);
  // 보내던 곳을 잃으면 방침이 군비로
  corpsSetDir(cp, 'sup', lb.id); lb.owner = 5; REPORT = [];
  corpsFix();
  chk('보낼 거점이 없어지면 방침을 군비로 돌리고 기록에 알린다', cp.dir === 'arm' && cp.target === -1 && REPORT.some(function (e) { return /보낼 거점이 없어져/.test(e.t); }));
  lb.owner = G.player;
`);

part('8. 잃은 거점 · 뒤처리', `
  newGame(4, 4242);
  var lb = lordBase(), others = facCities(G.player).filter(function (b) { return b !== lb; });
  var cp = corpsCreate([others[0].id, others[1].id]).corps, L = corpsLead(cp), hb = G.bases[L.loc], ob = others[0] === hb ? others[1] : others[0];
  // 다른 세력이 한 거점을 빼앗는다
  var eb = B('북평'), eo = baseOfficers(eb).filter(function (o) { return !isLord(o); })[0]; eb.w.spear = 9000; G.factions[eb.owner].ap = 200;
  var eu = cmdDeploy(eb, { type: 'spear', ids: [eo.id], troops: 3000, food: 3000 }).unit;
  placeUnit(eu, ob.c + 1, ob.r); captureBase(ob, eu);
  chk('빼앗긴 거점의 군단 표시는 지워진다', ob.owner === eb.owner && !ob.corps && corpsBases(cp).length === 1 && baseCorps(ob) === null);
  // 되찾아도 직할
  var mo = idleOfficers(lb).filter(function (x) { return !isLord(x); })[0]; lb.w.spear = 9000; G.factions[G.player].ap = 200;
  var mu = cmdDeploy(lb, { type: 'spear', ids: [mo.id], troops: 2000, food: 2000 }).unit;
  ob.troops = 0; captureBase(ob, mu);
  chk('직할 부대로 되찾으면 직할(옛 표시가 되살아나지 않는다)', ob.owner === G.player && !ob.corps);
  // 남은 거점마저 잃으면 해산, 군단의 부대는 직할로
  var lo = idleOfficers(hb)[0]; hb.w.spear = 9000; hb.troops = 9000; G.factions[G.player].ap = 200;
  var cu = cmdDeploy(hb, { type: 'spear', ids: [lo.id], troops: 2000, food: 2000 }).unit; cu.corps = cp.id; cu.ai = { mode: 'return' };
  hb.owner = eb.owner; REPORT = [];
  corpsFix();
  chk('거점을 모두 잃으면 군단은 해산되고 부대는 직할로 + 중요한 일로 기록', corpsAll().length === 0 && !cu.corps && cu.ai === null && !hb.corps && REPORT.some(function (e) { return /제1군단 해산/.test(e.t) && e.imp === 2; }), REPORT.map(function (e) { return e.t; }));
  hb.owner = G.player;
  // 턴 진행 속에서도
  var cp2 = corpsCreate([hb.id]).corps;
  hb.corps = 99; corpsFix();
  chk('없는 군단을 가리키는 표시는 지워진다', !hb.corps && corpsAll().length === 0);
`);

part('9. 턴 진행 — 군단은 내 차례의 끝에, 다른 세력보다 먼저', `
  newGame(4, 4242);
  var lb = lordBase(), others = facCities(G.player).filter(function (b) { return b !== lb; });
  var cp = corpsCreate([others[0].id, others[1].id]).corps;
  REPORT = []; EVQ = [];
  var next = turnStepper(), kinds = [], s, seenAI = false, corpsAfterAI = false, t0 = G.turn;
  while ((s = next())) { kinds.push(s.kind + (s.corps ? '#' + s.corps : '')); if (s.kind === 'phase') seenAI = true; if (s.corps && seenAI) corpsAfterAI = true; EVQ.length = 0; }
  chk('첫 단계는 군단의 차례', kinds[0] === 'corps#' + cp.id, kinds.slice(0, 4));
  chk('군단이 끝난 뒤에 다른 세력이 움직인다', !corpsAfterAI && kinds.indexOf('phase') > 0 && kinds.indexOf('round') > kinds.indexOf('phase'));
  chk('한 턴이 흘렀다', G.turn === t0 + 1);
  var rep = REPORT.filter(function (e) { return e.corps === cp.id; });
  chk('지난 열흘의 일에 군단의 보고가 한 줄(군단 이름 · 군단장 · 방침 · 한 일)', rep.length === 1 && rep[0].f === G.player && rep[0].imp === 1 && rep[0].t.indexOf('제1군단 (' + corpsLead(cp).n + ' · 군비) — ') === 0 && rep[0].c !== undefined, rep.map(function (e) { return e.t; }));
  chk('보고는 군단 창에도 남는다', cp.note && cp.note.s && rep[0].t.indexOf(cp.note.s) > 0, cp.note);
  // 한 일이 없을 때
  cp.ap = 0; baseOfficers(others[0]).concat(baseOfficers(others[1])).forEach(function (o) { o.acted = true; }); CORPS_AP.base = 0; CORPS_AP.city = 0; var keepLead = cp.lead; cp.lead = -1; corpsBases(cp).forEach(function (b) { baseOfficers(b).forEach(function (o) { o.loc = lb.id; }); });
  corpsOnly();
  chk('한 일이 없으면 그렇게 적는다(행동력과 함께)', /한 일 없음 \\(행동력 0\\)/.test(REPORT[REPORT.length - 1].t), REPORT[REPORT.length - 1].t);
`);

part('10. 저장 · 불러오기', `
  newGame(4, 4242);
  var lb = lordBase(), others = facCities(G.player).filter(function (b) { return b !== lb; });
  var cp = corpsCreate([others[0].id, others[1].id]).corps; corpsSetDir(cp, 'atk', B('북해').id); cp.ap = 77;
  var s1 = serialize();
  chk('불러오기', deserialize(s1) === true);
  var c2 = corpsAll()[0];
  chk('군단이 그대로 돌아온다(번호 · 군단장 · 방침 · 목표 · 행동력 · 거점)', corpsAll().length === 1 && c2.n === 1 && c2.lead === cp.lead && c2.dir === 'atk' && c2.target === B('북해').id && c2.ap === 77 && corpsBases(c2).length === 2);
  endTurn();
  chk('불러온 판에서 턴을 넘기면 군단이 움직인다', corpsAll()[0].note && corpsAll()[0].note.t === G.turn - 1);
  // 군단이 없던 옛 저장
  var g = JSON.parse(s1); delete g.corps; delete g.nextCorps; g.bases.forEach(function (b) { delete b.corps; });
  chk('군단이 없던 저장(0.9.3 까지)도 열린다', deserialize(JSON.stringify(g)) === true && corpsAll().length === 0 && G.nextCorps === 1 && directBases(G.player).length === 3);
  var r = corpsCreate([facCities(G.player).filter(function (b) { return b !== lordBase(); })[0].id]);
  chk('옛 저장에서도 군단을 만들 수 있다', r.ok && corpsName(r.corps) === '제1군단');
`);

part('11. 같은 판은 같은 길로', `
  function play(seed) {
    newGame(4, seed);
    var lb = lordBase(), others = facCities(G.player).filter(function (b) { return b !== lb; });
    var cp = corpsCreate([others[0].id, others[1].id]).corps; corpsSetDir(cp, 'atk', B('계').id);
    for (var k = 0; k < 12; k++) endTurn();
    return serialize();
  }
  var a = play(77), b = play(77), c = play(78);
  chk('같은 씨앗 · 같은 명령이면 12턴 뒤의 판이 글자까지 같다', a === b, a.length);
  chk('씨앗이 다르면 다르다', a !== c);
`);

part('12. 군단이 없는 판 · AI 대전은 0.9.3 과 같은 길', `
  // 군단을 만들지 않으면 군단의 단계가 없다
  newGame(4, 4242);
  var next = turnStepper(), s, kinds = {};
  while ((s = next())) { kinds[s.kind] = 1; EVQ.length = 0; }
  chk('군단이 없으면 군단의 차례도 없다', !kinds.corps && kinds.phase && kinds.round && kinds.start);
  // AI 세력의 판단은 좁혀지지 않는다
  chk('차례가 끝나면 좁히기는 풀려 있다', AISCOPE === null && JOT === null);
  var f = 5; chk('AI 세력이 보는 거점 = 그 세력의 모든 거점', aiBases(f).length === facBases(f).length && aiCities(f).length === facCities(f).length);
`);

console.log('\n검사 ' + total + '개, 어긋남 ' + fails.length + '개');
if (fails.length) { console.log(fails.join('\n')); process.exit(1); }
