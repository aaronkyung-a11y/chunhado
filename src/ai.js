/* ===== 천하도 — AI ===== */
/* 군단(v0.10): 군단의 차례를 돌리는 동안만 그 군단(그 밖에는 null = 세력 전체). 아래 판단들이 이 값으로 볼 거점·부대를 좁힌다 */
var AISCOPE = null;
function aiBases(f) { var bs = facBases(f); return AISCOPE ? bs.filter(function (b) { return b.corps === AISCOPE.id; }) : bs; }
function aiCities(f) { var cs = facCities(f); return AISCOPE ? cs.filter(function (b) { return b.corps === AISCOPE.id; }) : cs; }
/* 부대가 돌아갈 곳: 군단의 부대는 제 군단의 거점으로(없으면 아무 내 거점) */
function aiNearBase(u) {
  if (u.corps) {
    var best = null, bd = 1e9;
    for (var i = 0; i < G.bases.length; i++) { var b = G.bases[i]; if (b.owner !== u.f || b.corps !== u.corps) continue; var d = hdist(u.c, u.r, b.c, b.r) + (b.kind === 'gate' ? 3 : 0); if (d < bd) { bd = d; best = b; } }
    if (best) return best;
  }
  return nearestOwnBase(u.f, u.c, u.r);
}
function estUU(a, d, mult, ranged) {
  var x = 620 * Math.pow(uAtk(a) / Math.max(10, uDef(d)), 0.9) * troopFactor(a.troops) * mult;
  var c = (COMPAT[a.type] && COMPAT[a.type][d.type]) || 1;
  if (VS_TYPE[d.type] && (!ranged || d.type === 'trans' || d.type === 'ram')) c *= VS_TYPE[d.type];
  x *= c;
  var td = terr(d.c, d.r);
  if (td === 'f' || td === 'h') x *= 0.85; else if (td === 'w') x *= 1.2;
  if (d.status === 'confuse') x *= 1.25;
  return x;
}
function enemyUnitsNear(f, c, r, rad) {
  var out = [];
  for (var i = 0; i < G.units.length; i++) { var u = G.units[i]; if (u.f !== f && hdist(c, r, u.c, u.r) <= rad) out.push(u); }
  return out;
}
function aiMilScore(o) { return o.war * 0.55 + o.ldr * 0.45; }

function aiChooseType(b, leader, want) {
  var best = 'sword', bs = -1, types = ['spear', 'halberd', 'bow', 'cav'];
  for (var i = 0; i < types.length; i++) {
    var t = types[i], wp = UNIT_TYPES[t].weapon, stock = b.w[wp];
    if (stock < Math.min(want, 1500)) continue;
    var s = APT_RANK[leader.apt.charAt(APT_IDX[t])] * 10 + (t === 'cav' ? 3 : t === 'spear' ? 2 : 1) + Math.min(1, stock / want) * 6;
    if (s > bs) { bs = s; best = t; }
  }
  return best;
}
function aiDeploy(b, leader, subs, troops, turns, ai, toward, forceType) {
  var type = forceType || aiChooseType(b, leader, troops);
  var wp = UNIT_TYPES[type].weapon;
  troops = Math.min(troops, cmdCap(leader), b.troops);
  if (wp && wp !== 'ram') troops = Math.min(troops, b.w[wp]);
  troops = Math.floor(troops / 100) * 100;
  if (troops < 500) return null;
  var food = Math.min(Math.ceil(troops / 20) * turns, Math.floor(b.food * 0.6));
  var res = cmdDeploy(b, { type: type, ids: [leader.id].concat(subs.map(function (o) { return o.id; })), troops: troops, food: food, toward: toward });
  if (!res.ok) return null;
  res.unit.ai = ai;
  if (AISCOPE) res.unit.corps = AISCOPE.id;
  return res.unit;
}

/* ---------- 부대 행동 ---------- */
function aiUnitAct(u) {
  if (!alive(u) || u.done) return;
  var f = u.f, ai = u.ai || (u.ai = { mode: 'return' });
  var T = (ai.target !== undefined && ai.target >= 0) ? G.bases[ai.target] : null;
  var mode = ai.mode;
  if (u.type === 'trans') mode = 'supply';
  if (mode === 'attack') { if (!T) mode = 'return'; else if (T.owner === f) mode = 'garrison'; else if (T.owner >= 0 && !aiMayStrike(f, T.owner)) ai.mode = mode = 'return'; }   // 아직 칠 수 없는 세력이 먼저 들어간 성: 그 앞에 눌러앉지 않고 돌아간다
  if (mode === 'defend') {
    var home = G.bases[ai.home];
    if (!home || home.owner !== f || enemyUnitsNear(f, home.c, home.r, 5).length === 0) mode = 'return';
  }
  var nbH = aiNearBase(u), tHome = nbH ? Math.ceil(hdist(u.c, u.r, nbH.c, nbH.r) / 4.5) + 1 : 2;
  var lowFood = u.food < Math.ceil(u.troops / 20) * tHome, weak = u.troops < Math.max(600, u.max * (u.corps ? 0.35 : 0.2));
  if ((lowFood || weak) && mode !== 'supply' && mode !== 'garrison') mode = 'return';

  var rc = unitReach(u), k, c, r, i;
  var stops = [K(u.c, u.r)];
  for (k in rc.stop) { k = +k; if (BAT[k] === undefined && !G.fires[k]) stops.push(k); }

  // 1) 공격 기회
  var best = null, bv = 0, rg = uRange(u);
  if (mode !== 'supply') {
    var en = enemyUnitsNear(f, u.c, u.r, 9);
    var onlyHere = (mode === 'return');
    for (i = 0; i < en.length; i++) {
      var e = en[i];
      for (var s = 0; s < stops.length; s++) {
        if (onlyHere && s > 0) break;
        k = stops[s]; c = k % W; r = (k - c) / W;
        var d = hdist(c, r, e.c, e.r);
        if (d < 1 || d > rg) continue;
        var ranged = d > 1;
        var dmg = estUU(u, e, 1.2, ranged);
        var v = dmg + (dmg >= e.troops ? 600 : 0) + (e.type === 'trans' ? 300 : 0);
        if (!ranged && e.status !== 'confuse') v -= estUU(e, u, 0.55, false) * 0.6;
        if (rg > 1 && ranged) v += 80;
        if (terr(c, r) === 'w') v -= 200;
        if (T && mode === 'attack') v -= hdist(c, r, T.c, T.r) * 4;
        if (v > bv) { bv = v; best = { kind: 'unit', u: e, k: k }; }
      }
    }
    if (mode === 'attack' && T && T.owner >= 0 && T.owner !== f && aiMayStrike(f, T.owner)) {
      for (s = 0; s < stops.length; s++) {
        k = stops[s]; c = k % W; r = (k - c) / W;
        var db = hdist(c, r, T.c, T.r);
        if (db < 1 || db > rg) continue;
        if (justOut(u)) continue;                                                          // 출진한 턴에는 거점을 칠 수 없다
        var vb = 260 + durDmgUB(u) * 0.5 + (terr(c, r) === 'w' ? -150 : 0) + (db > 1 ? 60 : 0);
        if (T.troops < 800) vb += 500;
        if (u.corps) vb += clamp((4500 - T.troops) / 2, 0, 1500);                           // 군단: 수비가 얇아진 성은 들판의 적보다 먼저 친다
        if (vb > bv) { bv = vb; best = { kind: 'base', b: T, k: k }; }
      }
    }
    // 길을 막는 적 시설
    if (!best && mode === 'attack') {
      var ats = attackTargets(u);
      for (i = 0; i < ats.length; i++) if (ats[i].kind === 'fac' && aiMayStrike(f, ats[i].b.owner) && chance(15)) { best = { kind: 'fac', t: ats[i], k: K(u.c, u.r) }; bv = 1; break; }
    }
  }
  if (best && bv > 0) {
    if (best.k !== K(u.c, u.r)) { c = best.k % W; r = (best.k - c) / W; var mv = unitMove(u, c, r, rc); if (!mv.ok || !alive(u)) return; }
    if (best.kind === 'base') { var rb = unitAttack(u, { kind: 'base', b: best.b, c: best.b.c, r: best.b.r }); if (rb && rb.ok) jot('siege', best.b, rb.dmg || 0); return; }
    if (best.kind === 'fac') { unitAttack(u, best.t); return; }
    var tg = best.u;
    if (!alive(tg)) { unitWait(u); return; }
    var tgt = { kind: 'unit', u: tg, c: tg.c, r: tg.r };
    // 계략
    if (uInt(u) >= 78 && u.morale >= 30 && hdist(u.c, u.r, tg.c, tg.r) <= ployRange(u) && chance(30)) {
      var pl = (!tg.status && chance(50)) ? PLOYS[1] : PLOYS[0];
      var pts = ployTargets(u, pl), pt = null;
      for (i = 0; i < pts.length; i++) if (pts[i].u === tg) pt = pts[i];
      if (pt && pl.id === 'fire') { var hf = actHoldF(pt, pl); if (hf >= 0 && hf !== f && !aiMayStrike(f, hf)) pt = null; }   // 초반 보호: 남의 시설 위에는 불을 놓지 않는다
      if (pt && ployChance(u, pl, tg) >= 55) { aiReport(u, unitPloy(u, pl, pt), tg); return; }
    }
    // 전법
    var tl = tacticList(u), bt = null, bm = -9;
    for (i = 0; i < tl.length; i++) {
      if (u.morale < tl[i].cost) continue;
      var tt = tacticTargets(u, tl[i]), okT = false;
      for (var q = 0; q < tt.length; q++) if (tt[q].u === tg) okT = true;
      if (!okT) continue;
      // v0.9.1: 보통 공격과 견준 이득 = (기대 피해의 차이 − 받는 반격의 차이 × 0.6) ÷ 보통 공격의 피해. 반격의 무게 0.6 은 칠 상대를 고를 때와 같다.
      //         함께 맞는 적의 피해는 실제로 센다(v0.8~0.9: 주는 피해만 보고, 여럿을 치는 전법에는 어림으로 +0.2)
      var ex = tacticExpect(u, tg, tl[i]);
      var m = ((ex.dealt - ex.nDealt) - 0.6 * (ex.recv - ex.nRecv)) / Math.max(1, ex.nDealt);
      if (m > bm) { bm = m; bt = tl[i]; }
    }
    if (bt && bm >= 0.1 && chance(85)) { aiReport(u, unitTactic(u, bt, tgt), tg); return; }      // 보통 공격보다 나을 때만 쓴다(v0.7: 가장 센 전법을 75% 확률로 무조건)
    aiReport(u, unitAttack(u, tgt), tg);
    return;
  }

  // 2) 목표로 이동
  var goalFn = null, gb = null, hint = null;
  if (mode === 'attack') {
    if (T.owner === -1) { gb = T; }
    else { var tc = T.c, tr = T.r; goalFn = function (kk) { var cc = kk % W, rr = (kk - cc) / W; return BAT[kk] === undefined && hdist(cc, rr, tc, tr) <= rg; }; hint = [tc, tr, rg]; }
  } else if (mode === 'defend') {
    var hm = G.bases[ai.home], es = enemyUnitsNear(f, hm.c, hm.r, 5);
    if (es.length) { var ex = es[0]; goalFn = function (kk) { var cc = kk % W, rr = (kk - cc) / W; return BAT[kk] === undefined && hdist(cc, rr, ex.c, ex.r) <= 1; }; hint = [ex.c, ex.r, 1]; }
  }
  if (!goalFn && !gb) {
    if ((mode === 'garrison' || mode === 'supply') && T && T.owner === f) gb = T;
    else gb = aiNearBase(u);
    if (!gb) { unitWait(u); return; }
  }
  if (gb) { var gk = K(gb.c, gb.r); goalFn = function (kk) { return kk === gk; }; hint = [gb.c, gb.r, 0]; }
  var path = longPath(u, goalFn, 0, hint);
  if (!path) { ai.stuck = (ai.stuck || 0) + 1; if (ai.stuck > 3 && mode === 'attack') ai.mode = 'return'; unitWait(u); return; }
  var dest = -1;
  for (i = 0; i < path.length; i++) { k = path[i]; if (rc.stop[k] && (!G.fires[k] || BAT[k] !== undefined)) dest = k; }
  if (dest >= 0) {
    c = dest % W; r = (dest - c) / W;
    var res = unitMove(u, c, r, rc);
    if (!res.ok) { unitWait(u); return; }
    if (res.captured !== undefined || res.entered !== undefined) return;
    ai.stuck = 0;
  } else ai.stuck = (ai.stuck || 0) + 1;
  if (ai.stuck > 5 && mode === 'attack') ai.mode = 'return';
  if (alive(u)) unitWait(u);
}
function aiReport(u, res, tg) {
  if (!res || !res.ok || G.aiOnly) return;
  jot('act', null, res.dmg || 0, res.kind);
  if (tg && tg.f === G.player) {
    var txt = facName(u.f) + ' ' + uLeader(u).n + '대';
    if (res.kind === 'ploy') txt += '의 ' + res.ploy + (res.success ? ' 성공' : ' 실패') + ' → ' + (uLeaderSafe(tg)) + (res.dmg ? ' (-' + nf(res.dmg) + ')' : '') + (res.success && res.st ? ' — ' + statusName(res.st) + ' ' + res.stN * 10 + '일' : '');
    else if (res.kind === 'tactic') txt += '의 ' + res.tac + (res.fail ? ' 실패' : (res.crit ? ' 대성공' : '')) + ' → ' + uLeaderSafe(tg) + ' (-' + nf(res.dmg) + ')' + (res.confused ? ' — 혼란 ' + res.stN * 10 + '일' : '');
    else txt += '의 공격 → ' + uLeaderSafe(tg) + ' (-' + nf(res.dmg) + ')';
    if (res.duel) txt += ' · 일기토 ' + (res.duel.draw ? '비김' : (res.duel.win ? res.duel.a : res.duel.d) + ' 승');
    if (res.killed) txt += ' 궤멸';
    logMsg(txt, res.c, res.r, G.player, 1);
  }
}
function uLeaderSafe(u) { return (u && u.off && u.off.length) ? off(u.off[0]).n + '대' : '아군'; }
function aiUnits(f) {
  var us = facUnits(f);
  us.sort(function (a, b) { return a.id - b.id; });
  for (var i = 0; i < us.length; i++) { if (G.over) return; aiUnitAct(us[i]); }
}

/* ---------- 내정 ---------- */
function aiCountFac(b) {
  var n = { market: 0, farm: 0, barracks: 0, smithy: 0, stable: 0, workshop: 0, mint: 0, granary: 0 };
  for (var i = 0; i < b.plots.length; i++) if (b.plots[i].fac) n[b.plots[i].fac.t]++;
  return n;
}
function aiPickFacility(b) {
  var n = aiCountFac(b);
  if (!n.barracks) return 'barracks';
  if (!n.market) return 'market';
  if (!n.farm) return 'farm';
  if (!n.smithy) return 'smithy';
  if (n.market < 2) return 'market';
  if (n.farm < 2) return 'farm';
  if (!n.stable && b.plots.length >= 8) return 'stable';
  if (n.market < 3) return 'market';
  if (n.farm < 3) return 'farm';
  if (!n.mint && b.plots.length >= 8) return 'mint';
  if (!n.granary && b.plots.length >= 8) return 'granary';
  if (!n.workshop && b.plots.length >= 10) return 'workshop';
  return n.market <= n.farm ? 'market' : 'farm';
}
function aiPickPlot(b, type) {
  var free = [], i;
  for (i = 0; i < b.plots.length; i++) if (!b.plots[i].fac && !UAT[K(b.plots[i].c, b.plots[i].r)]) free.push(i);
  if (!free.length) return -1;
  if (type === 'mint' || type === 'granary') {
    var want = type === 'mint' ? 'market' : 'farm', bi = free[0], bn = -1;
    for (i = 0; i < free.length; i++) {
      var p = b.plots[free[i]], ns = nbrs(p.c, p.r), cnt = 0;
      for (var j = 0; j < ns.length; j++) { var q = PAT[K(ns[j][0], ns[j][1])]; if (q && q.b === b.id) { var fc = b.plots[q.i].fac; if (fc && fc.t === want) cnt++; } }
      if (cnt > bn) { bn = cnt; bi = free[i]; }
    }
    return bi;
  }
  return free[0];
}
function aiCaptives(f) {
  var F = G.factions[f], bs = aiBases(f);
  for (var bi = 0; bi < bs.length; bi++) {
    var b = bs[bi], caps = b.captives.slice();
    for (var i = 0; i < caps.length; i++) {
      var cp = off(caps[i]), os = idleOfficers(b);
      b.ai.capTry = b.ai.capTry || {};
      var n = b.ai.capTry[cp.id] = (b.ai.capTry[cp.id] || 0) + 1;
      if (os.length && F.ap >= AP.recruit && !(AISCOPE && n > 3 && n % 3)) {      // 군단: 세 번 권한 뒤에는 석 턴에 한 번만
        os.sort(function (a, c2) { return recruitChance(b, c2, cp) - recruitChance(b, a, cp) || c2.cha - a.cha || a.id - c2.id; });      // v0.11: 옛 주군 · 옛 동료가 있으면 그 사람이 간다
        var rr = cmdRecruit(b, os[0].id, cp.id);
        if (rr.ok && rr.joined) { delete b.ai.capTry[cp.id]; continue; }
      }
      if (n >= 3 && !AISCOPE) { cmdCaptive(b, cp.id, 'release'); delete b.ai.capTry[cp.id]; }      // 군단은 포로를 풀어 주지 않는다(내가 정할 일)
    }
  }
}
/* ---------- 다른 세력 무장 등용(v0.9) ---------- */
function aiPoachScore(o) { return o.cha * POACH.cha + o.pol * POACH.pol + (o.sk === '논객' ? POACH.talker : 0); }
function aiPoach(f) {
  var F = G.factions[f];
  if (F.ap < AP.recruit + 20 || !chance(POACH_AI.tryPct)) return;
  var bs = aiBases(f), best = null, bv = 0;
  for (var bi = 0; bi < bs.length; bi++) {
    var b = bs[bi], os = idleOfficers(b); if (!os.length) continue;
    var ts = poachTargets(b); if (!ts.length) continue;
    os.sort(function (a, c) { return aiPoachScore(c) - aiPoachScore(a) || a.id - c.id; });
    var o = os[0];
    for (var i = 0; i < ts.length; i++) {
      var t = ts[i];
      if (askWait(t)) continue;
      if (t.f === G.player && G.peace && G.turn < G.peace.until) continue;      // 초반 보호: 그동안은 플레이어의 무장에게 권하지 않는다
      if (facOfficers(t.f).length <= POACH_AI.spare) continue;                  // 무장이 몇 안 되는 세력은 건드리지 않는다
      var p = recruitChance(b, o, t); if (p < POACH_AI.min) continue;
      var v = p * (t.ldr + t.war + t.int + t.pol);
      if (v > bv) { bv = v; best = { b: b, o: o, t: t }; }
    }
  }
  if (best) cmdRecruit(best.b, best.o.id, best.t.id);
}
function aiInternal(f) {
  var F = G.factions[f], cities = aiCities(f), ci, i, DIR = AISCOPE ? AISCOPE.dir : '';      // DIR: 군단의 방침('' = AI 세력)
  if (AISCOPE && cities.length > 1) cities = cities.slice(G.turn % cities.length).concat(cities.slice(0, G.turn % cities.length));      // 군단: 도는 차례를 턴마다 돌린다(앞의 도시가 행동력을 다 쓰지 않게)
  for (ci = 0; ci < cities.length; ci++) {
    var b = cities[ci];
    var threatened = enemyUnitsNear(f, b.c, b.r, 4).length > 0;
    var idle = function () { return idleOfficers(b); };
    var os, o;
    // 포상
    os = baseOfficers(b);
    for (i = 0; i < os.length; i++) if (os[i].loy < 72 && !isLord(os[i]) && b.gold >= COST.reward + 110 && F.ap >= AP.reward) cmdReward(b, os[i].id);
    // 재야 등용
    var fr = freeOfficers(b);
    for (i = 0; i < fr.length; i++) { os = idle(); if (!os.length || F.ap < AP.recruit) break; var frT = fr[i]; os.sort(function (a, c2) { return recruitChance(b, c2, frT) - recruitChance(b, a, frT) || c2.cha - a.cha || a.id - c2.id; }); cmdRecruit(b, os[0].id, frT.id); }
    // 순찰
    if (b.order < 60 && b.gold >= COST.patrol + 40 && F.ap >= AP.patrol) { os = idle(); if (os.length) { os.sort(function (a, c2) { return Math.max(c2.war, c2.ldr) - Math.max(a.war, a.ldr); }); cmdPatrol(b, [os[0].id]); } }
    // 개발 — 공사를 맡은 무장은 완공까지 묶이므로: 적이 가까우면 새로 짓지 않고, 싸움에 가장 쓸모 있는 둘은 남겨 두고, 한꺼번에 벌이는 공사 수를 줄인다
    var nOff = baseOfficers(b).length, building = b.plots.filter(function (p) { return p.fac && !p.fac.done; }).length;
    var keep = (nOff > 3 && DIR !== 'dev') ? baseOfficers(b).sort(function (a, c2) { return aiMilScore(c2) - aiMilScore(a); }).slice(0, 2) : [];
    for (var rep = 0; rep < (DIR === 'dev' ? 3 : 2) && !threatened; rep++) {
      if (building >= (nOff <= 4 ? 1 : 2) + (DIR === 'dev' ? 1 : 0)) break;
      os = idle().filter(function (x) { return keep.indexOf(x) < 0; }); if (!os.length || F.ap < AP.develop + 10) break;
      var type = aiPickFacility(b), pi = aiPickPlot(b, type);
      if (pi < 0 || b.gold < FAC[type].cost + 70) break;
      os.sort(function (a, c2) { return c2.pol - a.pol; });
      var rdev = cmdDevelop(b, pi, type, os.slice(0, Math.min(nOff <= 5 ? 1 : 2, os.length)).map(function (x) { return x.id; }));
      if (rdev.ok) building++; else break;
    }
    // 흡수합병: 부지가 다 찼으면 붙어 있는 같은 시설을 합친다
    if (F.ap >= AP.merge + 10 && b.gold >= COST.merge * 2 + 200 && !b.plots.some(function (p) { return !p.fac; })) {
      for (var mp = 0; mp < b.plots.length; mp++) {
        var mc = mergeCandidates(b, mp);
        if (!mc.length) continue;
        os = idle(); if (os.length) { os.sort(function (a, c2) { return c2.pol - a.pol; }); cmdMerge(b, mp, mc[0], [os[0].id]); }
        break;
      }
    }
    // 징병
    var cap = Math.min(45000, 10000 + baseOfficers(b).length * 3500);
    if (DIR === 'dev') { if (!threatened) cap = Math.min(cap, 8000); }            // 내정: 지킬 만큼만
    else if (!DIR && !threatened && !aiIsFront(f, b)) cap = Math.min(cap, 8000);      // 군비·공격·지원: 전선이 아니어도 한도까지 모은다
    if (hasFac(b, 'barracks') && b.gold >= COST.draft + 80 && b.order >= 55 && b.troops < cap && b.food >= Math.ceil((b.troops + 2500) / 60) * 10 && F.ap >= AP.draft) {
      os = idle(); if (os.length) { os.sort(function (a, c2) { return c2.cha - a.cha; }); cmdDraft(b, os.slice(0, Math.min(2, os.length)).map(function (x) { return x.id; })); }
    }
    // 생산
    if (b.gold >= COST.produce + 50 && F.ap >= AP.produce) {
      os = idle();
      if (os.length) {
        os.sort(function (a, c2) { return c2.int - a.int; });
        var tot = b.w.spear + b.w.halberd + b.w.bow;
        if (hasFac(b, 'smithy') && tot < b.troops * (DIR === 'dev' ? 0.5 : 0.9)) {      // 내정: 병기는 모자랄 때만
          var lead = baseOfficers(b).sort(function (a, c2) { return aiMilScore(c2) - aiMilScore(a); })[0];
          var kinds = ['spear', 'halberd', 'bow'], bk = 'spear', bsc = -1;
          for (i = 0; i < 3; i++) { var sc = APT_RANK[lead.apt.charAt(i)] * 3 - b.w[kinds[i]] / 4000 + (i === 0 ? 0.5 : 0) + (DIR === 'atk' && i === 2 ? 6 : 0);      /* 공격 방침: 성을 칠 노부터 갖춘다 */ if (sc > bsc) { bsc = sc; bk = kinds[i]; } }
          cmdProduce(b, bk, [os[0].id]);
        } else if (hasFac(b, 'stable') && b.w.horse < b.troops * (DIR === 'dev' ? 0.15 : 0.35)) cmdProduce(b, 'horse', [os[0].id]);
        else if (DIR !== 'dev' && hasFac(b, 'workshop') && b.w.ram < 1 && b.gold >= COST.ram + 200) cmdProduce(b, 'ram', [os[0].id]);
      }
    }
    // 훈련
    if (b.morale < 75 && b.troops >= 2000 && F.ap >= AP.train) { os = idle(); if (os.length) { os.sort(function (a, c2) { return c2.ldr - a.ldr; }); cmdTrain(b, [os[0].id]); } }
    // 탐색
    if (F.ap >= 60 && chance(DIR === 'dev' ? 70 : 35)) { os = idle(); if (os.length >= 2) { os.sort(function (a, c2) { return c2.pol - a.pol; }); cmdSearch(b, os[0].id); } }
    // 거래
    if (hasFac(b, 'market') && F.ap >= AP.trade) {
      if (b.food < b.troops * 0.35 && b.gold >= 600) cmdTrade(b, 'buy', Math.min(400, b.gold - 300));
      else if (b.gold < 200 && b.food > b.troops * 1.2 + 6000) cmdTrade(b, 'sell', 200);
    }
  }
}

/* ---------- 방어·공격·보급 ---------- */
function aiDefense(f) {
  var F = G.factions[f], bs = aiBases(f);
  for (var bi = 0; bi < bs.length; bi++) {
    var b = bs[bi];
    var en = enemyUnitsNear(f, b.c, b.r, 4);
    if (!en.length || b.troops < 4000) continue;
    var et = 0; en.forEach(function (e) { et += e.troops; });
    var mine = 0; G.units.forEach(function (u) { if (u.f === f && hdist(u.c, u.r, b.c, b.r) <= 4) mine += u.troops; });
    var n = 0;
    while (n < 3 && F.ap >= AP.deploy && b.troops - 2000 >= 1500 && mine < et * 1.3) {
      var os = idleOfficers(b).filter(function (o) { return !isLord(o) || b.troops > 12000; });
      if (!os.length) break;
      os.sort(function (a, c) { return aiMilScore(c) - aiMilScore(a); });
      var u = aiDeploy(b, os[0], [], b.troops - 2000, 6, { mode: 'defend', home: b.id }, en[0]);
      if (!u) break;
      mine += u.troops; n++;
    }
  }
}
function aiTargets(f, b) {
  var out = [], seen = {};
  seen[b.id] = 1;
  function add(id, len) {
    if (seen[id]) return; seen[id] = 1;
    var T = G.bases[id];
    if (T.owner === f) { if (T.kind === 'gate') ADJ[id].forEach(function (e) { add(e.to, len + e.len); }); return; }
    out.push({ T: T, len: len });
  }
  ADJ[b.id].forEach(function (e) { add(e.to, e.len); });
  return out;
}
function aiOffense(f) {
  var F = G.factions[f], cities = aiCities(f);
  for (var ci = 0; ci < cities.length; ci++) {
    var b = cities[ci];
    if (F.ap < AP.deploy * 2) { if (AISCOPE && !AISCOPE.wait) AISCOPE.wait = { ap: 1 }; return; }
    if (enemyUnitsNear(f, b.c, b.r, 5).length) continue;
    var idle = idleOfficers(b);
    if (!idle.length) continue;
    var tg = AISCOPE ? corpsTargets(AISCOPE, b) : aiTargets(f, b), best = null, bs = -1e9, i;
    var pool = AISCOPE ? corpsPool(AISCOPE, b) : 0;                                 // 군단: 같은 군단의 다른 도시가 낼 수 있는 병력
    var sendable = AISCOPE ? corpsAvail(b) : 0;                                     // 군단: 이 도시가 실제로 낼 수 있는 병력(무장의 지휘 한도까지)
    var hasLord = baseOfficers(b).some(isLord);
    var reserve = Math.max(hasLord ? 4000 : 2500, Math.round(b.troops * 0.25));
    var avail = b.troops - reserve;
    for (i = 0; i < tg.length; i++) {
      var T = tg[i].T, len = tg[i].len, sc, need;
      if (T.owner === -1) { need = 600; sc = 90 - len * 0.5 + (T.kind === 'city' ? 10 : 0); }
      else {
        if (!aiMayStrike(f, T.owner)) continue;                      // 초반 보호: 남이 지키는 거점을 먼저 치지 않는다
        var ramp = T.owner === G.player && peaceRamp(f);              // 보호가 끝난 뒤의 완충 기간
        if (ramp && othersOnPlayer(f)) continue;                     //   한 번에 한 세력만 플레이어를 치러 온다
        var def = T.troops, mul = aiNeedMul(f, T.owner);
        enemyUnitsNear(f, T.c, T.r, 3).forEach(function (e) { if (e.f === T.owner) def += e.troops; });
        need = AISCOPE ? corpsNeed(corpsDef(T), len, T) : def * mul + 2500 + (T.kind === 'gate' ? 1500 : 0);
        if (!AISCOPE && avail >= 12000 && avail < need && aiFacTroops(f) >= def * 4 * mul / 1.25 && chance(50)) need = avail;   // 국력이 압도적이면 파상 공세(완충 기간에는 문턱도 함께 높다)
        sc = 50 - def / 400 - len * 0.5 + (T.kind === 'city' ? 15 : 0) + (T.sz === 'L' ? 8 : 0);      // v0.8.1: 플레이어의 성에 주던 가산점(+3)을 없앰
        if (b.morale < 55 || (b.ai.cool || 0) > G.turn) continue;
      }
      // 이미 그 거점으로 향하는 아군이 충분하면 건너뛴다
      var going = 0; G.units.forEach(function (u) { if (u.f === f && u.ai && u.ai.mode === 'attack' && u.ai.target === T.id) going += u.troops; });
      if (T.owner === -1 && going > 0) continue;
      var joined = AISCOPE && T.owner >= 0 && (going > 0 || AISCOPE.go === G.turn);      // 군단: 이미 싸움이 벌어졌으면(가고 있는 부대가 있거나 이번 턴에 다른 도시가 나섰으면) 문턱을 다시 묻지 않고 보탠다
      if (!joined && (AISCOPE ? sendable : avail) + going + pool < need) { if (AISCOPE) AISCOPE.wait = { need: Math.round(need), have: Math.round(sendable + going + pool) }; continue; }
      if (!joined && AISCOPE && T.owner >= 0 && going < need && F.ap < AP.deploy * 6) { AISCOPE.wait = { ap: 1, need: Math.round(need), have: Math.round(sendable + going + pool) }; continue; }      // 군단: 병력은 찼어도 여러 부대를 한꺼번에 낼 행동력(60)이 모일 때까지 기다린다
      if (going >= need) continue;
      if (sc > bs) { bs = sc; best = tg[i]; best.need = need; }
    }
    if (!best) continue;
    var Tb = best.T, turns = Math.ceil(best.len / 4) + (AISCOPE ? 16 : 8);      // 군단: 성을 오래 에워쌀 군량을 싣는다
    if (Tb.owner === -1) {
      if (avail < 800) continue;
      idle.sort(function (a, c) { return (c.pol + c.ldr) - (a.pol + a.ldr); });
      var gov = idle[0];
      if (isLord(gov) && idle.length > 1) gov = idle[1];
      aiDeploy(b, gov, [], Math.min(3000, Math.max(800, avail)), turns, { mode: 'attack', target: Tb.id, home: b.id }, Tb);
      continue;
    }
    idle = idle.filter(function (o) { return !isLord(o) || facCities(f).length === 1 && b.troops > 15000; });
    idle.sort(function (a, c) { return aiMilScore(c) - aiMilScore(a); });
    var nUnits = AISCOPE ? Math.min(idle.length, 5) : Math.min(idle.length, 5, Math.ceil(best.need / 5000) + 1), sent = 0, cnt = 0;      // 군단: 나서기로 했으면 낼 수 있는 대로 낸다
    if (b.w.ram >= 1 && idle.length > nUnits && avail > 6000) {
      var ro = idle.pop();
      if (aiDeploy(b, ro, [], 1500, turns, { mode: 'attack', target: Tb.id, home: b.id }, Tb, 'ram')) avail -= 1500;
    }
    for (i = 0; i < nUnits && F.ap >= AP.deploy; i++) {
      var left = b.troops - reserve;
      if (left < 1500) break;
      if (!idle[i]) break;
      var subs = (i === 0 && idle.length > nUnits + 1) ? [idle.pop()] : [];
      var share = Math.floor(left / (nUnits - i)), ft = (AISCOPE && i >= 1 && b.w.bow >= Math.min(share, cmdCap(idle[i]), 1500)) ? 'bow' : undefined;
      var u = aiDeploy(b, idle[i], subs, share, turns, { mode: 'attack', target: Tb.id, home: b.id }, Tb, ft);
      if (u) { sent += u.troops; cnt++; }
    }
    if (cnt) {
      b.ai.cool = G.turn + 8;
      if (AISCOPE) AISCOPE.go = G.turn;
      if (Tb.owner === G.player) {
        logMsg(facName(f) + '군이 ' + b.n + '에서 ' + Tb.n + ' 방면으로 출진 (' + cnt + '부대)', b.c, b.r, G.player, 2);
        ev({ t: 'news', f: f, c: b.c, r: b.r, warn: 1, text: '<b>' + facName(f) + '군이 ' + b.n + '에서 우리 ' + Tb.n + ' 방면으로 출진</b> (' + cnt + '부대)' });
      } else if (!AISCOPE) logMsg(facName(f) + '군이 ' + b.n + '에서 ' + Tb.n + (Tb.owner >= 0 ? '(' + facName(Tb.owner) + '군)' : '') + ' 방면으로 출진', b.c, b.r, f, 1);
    }
  }
}
function aiFacTroops(f) { var t = 0; G.bases.forEach(function (b) { if (b.owner === f) t += b.troops; }); return t; }
function aiIsFront(f, b) {
  if (enemyUnitsNear(f, b.c, b.r, 6).length) return true;
  return aiTargets(f, b).length > 0;
}
function aiLogistics(f) {
  var F = G.factions[f];
  var cities = aiCities(f);
  if (cities.length < 2) return;
  var ci, b;
  // 1) 태수 없는 도시에 한 명 보낸다
  var moved = 0;
  for (ci = 0; ci < cities.length && moved < 2; ci++) {
    b = cities[ci];
    if (baseOfficers(b).length > 0 || F.ap < AP.move) continue;
    var coming = G.officers.some(function (o) { return o.st === 'travel' && o.f === f && o.dest === b.id; });
    if (coming) continue;
    var src = null, sd = 1e9;
    cities.forEach(function (c2) { if (c2 === b) return; var n = idleOfficers(c2).filter(function (o) { return !isLord(o); }).length; if (n >= 1 && baseOfficers(c2).length >= 3) { var d = hdist(b.c, b.r, c2.c, c2.r); if (d < sd) { sd = d; src = c2; } } });
    if (!src) continue;
    var cand = idleOfficers(src).filter(function (o) { return !isLord(o); });
    cand.sort(function (a, c) { return (c.pol - aiMilScore(c) * 0.5) - (a.pol - aiMilScore(a) * 0.5); });
    if (cmdMoveOfficers(src, [cand[0].id], b.id).ok) moved++;
  }
  if ((G.turn + f) % 3 !== 0) return;
  var front = cities.filter(function (c3) { return aiIsFront(f, c3); });
  if (!front.length) return;
  for (ci = 0; ci < cities.length; ci++) {
    b = cities[ci];
    if (front.indexOf(b) >= 0 || F.ap < AP.deploy + 10) continue;
    var dest = null, bd = 1e9;
    front.forEach(function (fb) { var d = hdist(b.c, b.r, fb.c, fb.r) + fb.troops / 3000; if (d < bd) { bd = d; dest = fb; } });
    if (!dest) continue;
    var here = baseOfficers(b).length;
    var idle = idleOfficers(b).filter(function (o) { return !isLord(o); });
    // 2) 병력·물자 수송 (태수 한 명은 남긴다)
    if (b.troops >= 6000 && idle.length && here >= 2) {
      idle.sort(function (a, c) { return aiMilScore(a) - aiMilScore(c); });
      var keep = 3000, troops = b.troops - keep;
      var gold = Math.max(0, Math.floor((b.gold - 800) * 0.6)), food = Math.max(0, Math.floor((b.food - Math.ceil(keep / 60) * 30) * 0.5));
      var cargo = { spear: Math.floor(b.w.spear * 0.6), halberd: Math.floor(b.w.halberd * 0.6), bow: Math.floor(b.w.bow * 0.6), horse: Math.floor(b.w.horse * 0.6), ram: b.w.ram };
      var res = cmdDeploy(b, { type: 'trans', ids: [idle[0].id], troops: troops, food: food, gold: gold, cargo: cargo, toward: dest });
      if (res.ok) { res.unit.ai = { mode: 'supply', target: dest.id, home: b.id }; if (AISCOPE) res.unit.corps = AISCOPE.id; idle.shift(); here--; }
    } else if (!AISCOPE && F.ap >= 10 && (b.gold > 2500 || b.food > 30000)) {
      // 3) 후방의 남는 금·병량은 전선으로 보낸다 (AI 전용 간이 수송)
      var g2 = Math.max(0, Math.floor((b.gold - 1200) * 0.7)), f2 = Math.max(0, Math.floor((b.food - 15000) * 0.6));
      b.gold -= g2; b.food -= f2; dest.gold += g2; dest.food += f2; F.ap -= 10;
    }
    if (idle.length > 1 && here > 3 && F.ap >= AP.move) {
      idle.sort(function (a, c) { return aiMilScore(c) - aiMilScore(a); });
      cmdMoveOfficers(b, idle.slice(0, Math.min(2, here - 3, idle.length)).map(function (o) { return o.id; }), dest.id);
    }
  }
}

/* 한 세력의 차례를 '한 행동' 단위로 쪼갠 실행기. 부를 때마다 한 단계 하고, 더 할 일이 없으면 false */
function aiPhaseStepper(f) {
  var stage = 0, list = null, i = 0;
  function oneUnit() { while (i < list.length) { var u = list[i++]; if (alive(u) && !u.done) { aiUnitAct(u); return true; } } return false; }
  return function () {
    if (!G.factions[f].alive || G.over) return false;
    if (stage === 0) { list = facUnits(f); list.sort(function (a, b) { return a.id - b.id; }); i = 0; stage = 1; }
    if (stage === 1) { if (oneUnit()) return true; stage = 2; }
    if (stage === 2) {
      aiDefense(f); aiCaptives(f); aiPoach(f); aiInternal(f); aiOffense(f); aiLogistics(f);
      list = facUnits(f).filter(function (u) { return !u.done; }); i = 0; stage = 3;
      return true;
    }
    if (stage === 3) { if (oneUnit()) return true; stage = 4; }
    return false;
  };
}
function aiPhase(f) { var next = aiPhaseStepper(f); while (next()) { /* */ } }

/* ---------- 군단(v0.10) ---------- */
/* 거점 그래프에서 a → b 까지의 길이(칸). 길이 없으면 곧은 거리의 1.3배 */
function routeLen(a, b) {
  if (a.id === b.id) return 0;
  var dist = {}, open = [a.id], i; dist[a.id] = 0;
  while (open.length) {
    var bi = 0; for (i = 1; i < open.length; i++) if (dist[open[i]] < dist[open[bi]]) bi = i;
    var cur = open.splice(bi, 1)[0];
    if (cur === b.id) return dist[cur];
    for (i = 0; i < ADJ[cur].length; i++) { var e = ADJ[cur][i], nd = dist[cur] + e.len; if (dist[e.to] === undefined || nd < dist[e.to]) { if (dist[e.to] === undefined) open.push(e.to); dist[e.to] = nd; } }
  }
  return Math.round(hdist(a.c, a.r, b.c, b.r) * 1.3);
}
/* 군단이 칠 곳: 방침이 공격일 때 그 거점 하나 */
function corpsTargets(cp, b) {
  if (cp.dir !== 'atk') return [];
  var T = G.bases[cp.target];
  if (!T || T.owner === G.player) return [];
  return [{ T: T, len: routeLen(b, T) }];
}
/* 군단이 나서는 문턱: (지금의 수비 + 가는 동안 늘어날 몫) × mul + add. AI 세력의 문턱(수비 × 1.25 + 2,500)보다 높다 —
   맡긴 군단이 모자란 병력으로 나섰다가 무너지는 것을 막는다(tests/corpsatk10.js 로 잰 값) */
function corpsNeed(def, len, T) {
  return (def + CORPS_ATK.grow * Math.ceil(len / 5)) * CORPS_ATK.mul * corpsFoeK(T) + CORPS_ATK.add + (T.kind === 'gate' ? 1500 : 0);
}
/* 지키는 쪽의 병력: 그 거점의 주둔군 + 그 세력이 12칸 안에 내놓은 부대(잠깐 성을 비운 틈에 속지 않게) */
function corpsDef(T) {
  var def = T.troops;
  if (T.owner >= 0) G.units.forEach(function (e) { if (e.f === T.owner && hdist(e.c, e.r, T.c, T.r) <= 12) def += e.troops; });
  return def;
}
/* 지키는 장수의 몫: 그 거점에서 가장 뛰어난 무장의 무력·통솔(큰 쪽)이 75 를 넘는 만큼 문턱을 높인다(100 이면 1.5배) */
function corpsFoeK(T) {
  if (T.owner < 0) return 1;
  var best = 0; baseOfficers(T).forEach(function (o) { best = Math.max(best, o.war, o.ldr); });
  G.units.forEach(function (e) { if (e.f === T.owner && hdist(e.c, e.r, T.c, T.r) <= 12) uMembers(e).forEach(function (o) { best = Math.max(best, o.war, o.ldr); }); });
  return 1 + Math.max(0, best - 75) / 50;
}
/* 지금 그 거점을 치러 나서면 어떤가(화면용 — 주사위를 굴리지 않는다): { need(나서는 문턱), have(낼 수 있는 병력), going(이미 가고 있는 병력), len(가장 가까운 도시에서의 길) } */
function corpsOutlook(cp, T) {
  T = T || G.bases[cp.target];
  if (!T) return null;
  var f = G.player, cities = corpsCities(cp), len = null, have = 0, going = 0;
  cities.forEach(function (b) { var l = routeLen(b, T); if (len === null || l < len) len = l; have += corpsAvail(b); });
  G.units.forEach(function (u) { if (u.f === f && u.corps === cp.id && u.ai && u.ai.mode === 'attack' && u.ai.target === T.id) going += u.troops; });
  if (len === null) { len = 1e9; corpsBases(cp).forEach(function (b) { len = Math.min(len, routeLen(b, T)); }); if (len === 1e9) len = 0; }
  if (T.owner < 0) return { need: 600, have: have, going: going, len: len };
  return { need: Math.round(corpsNeed(corpsDef(T), len, T)), have: have, going: going, len: len, k: corpsFoeK(T) };
}
/* 한 도시가 한 번에 낼 수 있는 병력: 지킬 몫(25%, 적어도 2,500 — 군주가 있으면 4,000)을 뺀 것과, 나설 수 있는 무장 다섯의 지휘 한도를 더한 것 가운데 작은 쪽 */
function corpsAvail(b) {
  var res = Math.max(baseOfficers(b).some(isLord) ? 4000 : 2500, Math.round(b.troops * 0.25)), a = b.troops - res;
  if (a < 1500) return 0;
  var os = idleOfficers(b).filter(function (o) { return !isLord(o); }).sort(function (x, y) { return aiMilScore(y) - aiMilScore(x); }).slice(0, 5), cap = 0;
  os.forEach(function (o) { cap += cmdCap(o); });
  return Math.min(a, cap);
}
/* 같은 군단의 다른 도시들이 함께 낼 수 있는 병력. 그 도시들도 제 차례에 같은 셈을 한다 */
function corpsPool(cp, b) {
  var t = 0;
  aiCities(G.player).forEach(function (c) {
    if (c === b || enemyUnitsNear(G.player, c.c, c.r, 5).length || c.morale < 55 || (c.ai.cool || 0) > G.turn) return;
    t += corpsAvail(c);
  });
  return t;
}
/* 지원: 한 달에 한 번, 지킬 만큼만 남기고 병력·금·병량·병기를 고른 거점으로 실어 보낸다(수송대 — 이끈 무장은 도착한 거점에 남는다) */
function corpsSupply(cp) {
  var f = G.player, F = G.factions[f], dest = G.bases[cp.target];
  if (!dest || dest.owner !== f || (G.turn + cp.id) % 3 !== 0) return;
  var cities = aiCities(f);
  for (var ci = 0; ci < cities.length; ci++) {
    var b = cities[ci];
    if (F.ap < AP.deploy) break;
    if (enemyUnitsNear(f, b.c, b.r, 5).length) continue;                                  // 적이 가까우면 보내지 않는다
    var idle = idleOfficers(b).filter(function (o) { return !isLord(o) && o.id !== cp.lead; });
    if (!idle.length || baseOfficers(b).length < 2) continue;                              // 태수 한 명은 남긴다
    idle.sort(function (a, c) { return aiMilScore(a) - aiMilScore(c); });
    var keep = 3000, troops = Math.floor(Math.max(0, b.troops - keep) / 100) * 100;
    var gold = Math.max(0, Math.floor((b.gold - 800) * 0.6)), food = Math.max(0, Math.floor((b.food - Math.ceil(keep / 60) * 30) * 0.5));
    var cargo = { spear: Math.floor(b.w.spear * 0.6), halberd: Math.floor(b.w.halberd * 0.6), bow: Math.floor(b.w.bow * 0.6), horse: Math.floor(b.w.horse * 0.6), ram: 0 };
    var goods = gold >= 300 || food >= 3000 || cargo.spear + cargo.halberd + cargo.bow + cargo.horse >= 1000;
    if (troops < 2000 && !goods) continue;                                                // 보낼 것이 없다
    if (troops < 500) troops = Math.min(500, Math.floor(b.troops / 100) * 100);           // 물자만 보낼 때의 호위
    if (troops < 100) continue;
    var res = cmdDeploy(b, { type: 'trans', ids: [idle[0].id], troops: troops, food: Math.max(food, Math.min(b.food, Math.ceil(troops / 20) * 8)), gold: gold, cargo: cargo, toward: dest });
    if (res.ok) { res.unit.ai = { mode: 'supply', target: dest.id, home: b.id }; res.unit.corps = cp.id; }
  }
}
/* 군단장이 내리는 명령 한 묶음(내 차례의 끝에 한 번) */
function corpsOrders(cp) {
  var f = G.player;
  cp.wait = null;                                                     // 공격인데 아직 나서지 못한 까닭: { need, have }(병력) · { ap: 1 }(행동력)
  aiDefense(f);
  if (cp.dir === 'atk') aiOffense(f);                                 // 공격: 나설 수 있으면 내정보다 먼저 나선다
  if (cp.dir === 'sup') corpsSupply(cp);                              // 지원: 보낼 것부터 싣는다(내정에 무장을 다 쓰기 전에)
  var saving = cp.dir === 'atk' && cp.wait && cp.wait.ap;             // 병력은 찼는데 행동력이 모자라다 → 이번 턴은 내정을 쉬고 모은다
  if (!saving) { aiCaptives(f); aiPoach(f); aiInternal(f); if (cp.dir !== 'sup') aiLogistics(f); }
}
/* 한 군단의 차례를 '한 행동' 단위로 쪼갠 실행기(aiPhaseStepper 와 같은 꼴). 도는 동안 세력의 행동력 자리에 군단의 행동력을 잠깐 넣는다 */
function corpsStepper(cp) {
  var f = G.player, stage = 0, list = null, i = 0;
  function oneUnit() { while (i < list.length) { var u = list[i++]; if (alive(u) && !u.done && u.corps === cp.id) { aiUnitAct(u); return true; } } return false; }
  function step() {
    if (stage === 0) { list = corpsUnits(cp); list.sort(function (a, b) { return a.id - b.id; }); i = 0; stage = 1; }
    if (stage === 1) { if (oneUnit()) return true; stage = 2; }
    if (stage === 2) { corpsOrders(cp); list = corpsUnits(cp).filter(function (u) { return !u.done; }); i = 0; stage = 3; return true; }
    if (stage === 3) { if (oneUnit()) return true; stage = 4; }
    return false;
  }
  return function () {
    if (G.over || !G.factions[f].alive || !corpsById(cp.id)) return false;
    var F = G.factions[f], keep = F.ap, r = false;
    F.ap = cp.ap; AISCOPE = cp;
    try { r = step(); } finally { cp.ap = F.ap; F.ap = keep; AISCOPE = null; }
    return r;
  };
}
