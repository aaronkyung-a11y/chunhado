# v0.10 (2/…): 군단 — 군단장의 판단(ai.js)
#  AI 세력이 쓰는 판단(내정·방어·공격·보급·부대 행동)을 군단의 거점·부대로 좁혀서 그대로 쓴다. 좁히는 동안(AISCOPE)에만 달라지는 것:
#   - 거점·도시·돌아갈 곳은 그 군단의 것만 본다. 행동력은 군단의 것을 쓴다(차례 동안 세력의 행동력 자리에 잠깐 바꿔 넣는다).
#   - 방침: 내정 = 시설을 더 부지런히(한꺼번에 하나 더, 잘 싸우는 둘을 남겨 두지 않는다) · 병력은 8,000 까지만 · 탐색을 자주
#           군비 · 공격 · 지원 = 전선이 아니어도 병력을 한도까지 모은다
#           공격 = 고른 거점만 친다(군단의 여러 도시가 힘을 합쳐 셈한다). 모자라면 모으며 기다린다(cp.wait 에 적어 둔다)
#           지원 = 한 달에 한 번, 지킬 만큼만 남기고 병력·금·병량·병기를 고른 거점으로 실어 보낸다
#   - 포로는 풀어 주지 않는다(세 번 권한 뒤에는 석 턴에 한 번만 다시 권한다). AI 전용 간이 수송(금·병량을 그냥 옮기기)은 쓰지 않는다.
#  AISCOPE 가 없으면(= AI 세력의 차례) 0.9.3 과 한 글자도 다르지 않게 움직인다.
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)

p = 'src/ai.js'; s = io.open(p, encoding='utf-8').read()

s = rep(s, "/* ===== 천하도 — AI ===== */\n", """/* ===== 천하도 — AI ===== */
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
""")

# 출진: 군단이 낸 부대는 군단의 부대
s = rep(s, "  res.unit.ai = ai;\n  return res.unit;", "  res.unit.ai = ai;\n  if (AISCOPE) res.unit.corps = AISCOPE.id;\n  return res.unit;")

# 부대 행동: 돌아갈 곳, 한 일 적기
s = rep(s, "  var nbH = nearestOwnBase(f, u.c, u.r), tHome", "  var nbH = aiNearBase(u), tHome")
s = rep(s, "    else gb = nearestOwnBase(f, u.c, u.r);", "    else gb = aiNearBase(u);")
s = rep(s, "    if (best.kind === 'base') { unitAttack(u, { kind: 'base', b: best.b, c: best.b.c, r: best.b.r }); return; }",
           "    if (best.kind === 'base') { var rb = unitAttack(u, { kind: 'base', b: best.b, c: best.b.c, r: best.b.r }); if (rb && rb.ok) jot('siege', best.b, rb.dmg || 0); return; }")
s = rep(s, "function aiReport(u, res, tg) {\n  if (!res || !res.ok || G.aiOnly) return;", "function aiReport(u, res, tg) {\n  if (!res || !res.ok || G.aiOnly) return;\n  jot('act', null, res.dmg || 0, res.kind);")

# 포로 · 등용
s = rep(s, "  var F = G.factions[f], bs = facBases(f);", "  var F = G.factions[f], bs = aiBases(f);", 2)
s = rep(s, "      if (os.length && F.ap >= AP.recruit) {\n        os.sort(function (a, c2) { return c2.cha - a.cha; });\n        var rr = cmdRecruit(b, os[0].id, cp.id);",
           "      if (os.length && F.ap >= AP.recruit && !(AISCOPE && n > 3 && n % 3)) {      // 군단: 세 번 권한 뒤에는 석 턴에 한 번만\n        os.sort(function (a, c2) { return c2.cha - a.cha; });\n        var rr = cmdRecruit(b, os[0].id, cp.id);")
s = rep(s, "      if (n >= 3) { cmdCaptive(b, cp.id, 'release'); delete b.ai.capTry[cp.id]; }", "      if (n >= 3 && !AISCOPE) { cmdCaptive(b, cp.id, 'release'); delete b.ai.capTry[cp.id]; }      // 군단은 포로를 풀어 주지 않는다(내가 정할 일)")
s = rep(s, "  var bs = facBases(f), best = null, bv = 0;", "  var bs = aiBases(f), best = null, bv = 0;")

# 내정: 방침
s = rep(s, "  var F = G.factions[f], cities = facCities(f), ci, i;", "  var F = G.factions[f], cities = aiCities(f), ci, i, DIR = AISCOPE ? AISCOPE.dir : '';      // DIR: 군단의 방침('' = AI 세력)")
s = rep(s, "    var keep = nOff > 3 ? baseOfficers(b)", "    var keep = (nOff > 3 && DIR !== 'dev') ? baseOfficers(b)")
s = rep(s, "    for (var rep = 0; rep < 2 && !threatened; rep++) {\n      if (building >= (nOff <= 4 ? 1 : 2)) break;",
           "    for (var rep = 0; rep < (DIR === 'dev' ? 3 : 2) && !threatened; rep++) {\n      if (building >= (nOff <= 4 ? 1 : 2) + (DIR === 'dev' ? 1 : 0)) break;")
s = rep(s, "    if (!threatened && !aiIsFront(f, b)) cap = Math.min(cap, 8000);",
           "    if (DIR === 'dev') { if (!threatened) cap = Math.min(cap, 8000); }            // 내정: 지킬 만큼만\n    else if (!DIR && !threatened && !aiIsFront(f, b)) cap = Math.min(cap, 8000);      // 군비·공격·지원: 전선이 아니어도 한도까지 모은다")
s = rep(s, "    if (F.ap >= 60 && chance(35)) { os = idle();", "    if (F.ap >= 60 && chance(DIR === 'dev' ? 70 : 35)) { os = idle();")
s = rep(s, "        if (hasFac(b, 'smithy') && tot < b.troops * 0.9) {", "        if (hasFac(b, 'smithy') && tot < b.troops * (DIR === 'dev' ? 0.5 : 0.9)) {      // 내정: 병기는 모자랄 때만")
s = rep(s, "        } else if (hasFac(b, 'stable') && b.w.horse < b.troops * 0.35) cmdProduce(b, 'horse', [os[0].id]);\n        else if (hasFac(b, 'workshop') && b.w.ram < 1 && b.gold >= COST.ram + 200) cmdProduce(b, 'ram', [os[0].id]);",
           "        } else if (hasFac(b, 'stable') && b.w.horse < b.troops * (DIR === 'dev' ? 0.15 : 0.35)) cmdProduce(b, 'horse', [os[0].id]);\n        else if (DIR !== 'dev' && hasFac(b, 'workshop') && b.w.ram < 1 && b.gold >= COST.ram + 200) cmdProduce(b, 'ram', [os[0].id]);")
s = rep(s, "var sc = APT_RANK[lead.apt.charAt(i)] * 3 - b.w[kinds[i]] / 4000 + (i === 0 ? 0.5 : 0);", "var sc = APT_RANK[lead.apt.charAt(i)] * 3 - b.w[kinds[i]] / 4000 + (i === 0 ? 0.5 : 0) + (DIR === 'atk' && i === 2 ? 6 : 0);      /* 공격 방침: 성을 칠 노부터 갖춘다 */")
# 군단: 도시를 도는 차례를 턴마다 돌린다(앞의 도시가 행동력을 다 쓰지 않게)
s = rep(s, "  for (ci = 0; ci < cities.length; ci++) {\n    var b = cities[ci];\n    var threatened = enemyUnitsNear(f, b.c, b.r, 4).length > 0;",
           "  if (AISCOPE && cities.length > 1) cities = cities.slice(G.turn % cities.length).concat(cities.slice(0, G.turn % cities.length));      // 군단: 도는 차례를 턴마다 돌린다(앞의 도시가 행동력을 다 쓰지 않게)\n  for (ci = 0; ci < cities.length; ci++) {\n    var b = cities[ci];\n    var threatened = enemyUnitsNear(f, b.c, b.r, 4).length > 0;")

# 공격: 군단은 고른 거점만, 여러 도시의 힘을 합쳐 셈한다
s = rep(s, "  var F = G.factions[f], cities = facCities(f);\n  for (var ci = 0; ci < cities.length; ci++) {\n    var b = cities[ci];\n    if (F.ap < AP.deploy * 2) return;",
           "  var F = G.factions[f], cities = aiCities(f);\n  for (var ci = 0; ci < cities.length; ci++) {\n    var b = cities[ci];\n    if (F.ap < AP.deploy * 2) { if (AISCOPE && !AISCOPE.wait) AISCOPE.wait = { ap: 1 }; return; }")
s = rep(s, "    var tg = aiTargets(f, b), best = null, bs = -1e9, i;", "    var tg = AISCOPE ? corpsTargets(AISCOPE, b) : aiTargets(f, b), best = null, bs = -1e9, i;\n    var pool = AISCOPE ? corpsPool(AISCOPE, b) : 0;                                 // 군단: 같은 군단의 다른 도시가 낼 수 있는 병력\n    var sendable = AISCOPE ? corpsAvail(b) : 0;                                     // 군단: 이 도시가 실제로 낼 수 있는 병력(무장의 지휘 한도까지)")
s = rep(s, "      if (avail + going < need) continue;", "      var joined = AISCOPE && T.owner >= 0 && (going > 0 || AISCOPE.go === G.turn);      // 군단: 이미 싸움이 벌어졌으면(가고 있는 부대가 있거나 이번 턴에 다른 도시가 나섰으면) 문턱을 다시 묻지 않고 보탠다\n      if (!joined && (AISCOPE ? sendable : avail) + going + pool < need) { if (AISCOPE) AISCOPE.wait = { need: Math.round(need), have: Math.round(sendable + going + pool) }; continue; }\n      if (!joined && AISCOPE && T.owner >= 0 && going < need && F.ap < AP.deploy * 6) { AISCOPE.wait = { ap: 1, need: Math.round(need), have: Math.round(sendable + going + pool) }; continue; }      // 군단: 병력은 찼어도 여러 부대를 한꺼번에 낼 행동력(60)이 모일 때까지 기다린다")
s = rep(s, "      } else logMsg(facName(f) + '군이 ' + b.n + '에서 ' + Tb.n +", "      } else if (!AISCOPE) logMsg(facName(f) + '군이 ' + b.n + '에서 ' + Tb.n +")
s = rep(s, "    if (cnt) {\n      b.ai.cool = G.turn + 8;", "    if (cnt) {\n      b.ai.cool = G.turn + 8;\n      if (AISCOPE) AISCOPE.go = G.turn;")

s = rep(s, "        need = def * mul + 2500 + (T.kind === 'gate' ? 1500 : 0);", "        need = AISCOPE ? corpsNeed(corpsDef(T), len, T) : def * mul + 2500 + (T.kind === 'gate' ? 1500 : 0);")
s = rep(s, "    var nUnits = Math.min(idle.length, 5, Math.ceil(best.need / 5000) + 1), sent = 0, cnt = 0;", "    var nUnits = AISCOPE ? Math.min(idle.length, 5) : Math.min(idle.length, 5, Math.ceil(best.need / 5000) + 1), sent = 0, cnt = 0;      // 군단: 나서기로 했으면 낼 수 있는 대로 낸다")

# 군단의 공성: 셋째 부대부터는 노병(성에 붙을 자리는 여섯 칸뿐 — 노병은 두 칸 밖에서 치고 반격도 받지 않는다). 병력이 35% 아래로 줄면 물러난다(AI 세력은 20%)
s = rep(s, "      var u = aiDeploy(b, idle[i], subs, Math.floor(left / (nUnits - i)), turns, { mode: 'attack', target: Tb.id, home: b.id }, Tb);",
           "      var share = Math.floor(left / (nUnits - i)), ft = (AISCOPE && i >= 1 && b.w.bow >= Math.min(share, cmdCap(idle[i]), 1500)) ? 'bow' : undefined;\n      var u = aiDeploy(b, idle[i], subs, share, turns, { mode: 'attack', target: Tb.id, home: b.id }, Tb, ft);")
s = rep(s, "weak = u.troops < Math.max(600, u.max * 0.2);", "weak = u.troops < Math.max(600, u.max * (u.corps ? 0.35 : 0.2));")
s = rep(s, "        if (T.troops < 800) vb += 500;", "        if (T.troops < 800) vb += 500;\n        if (u.corps) vb += clamp((4500 - T.troops) / 2, 0, 1500);                           // 군단: 수비가 얇아진 성은 들판의 적보다 먼저 친다")

s = rep(s, "    var Tb = best.T, turns = Math.ceil(best.len / 4) + 8;", "    var Tb = best.T, turns = Math.ceil(best.len / 4) + (AISCOPE ? 16 : 8);      // 군단: 성을 오래 에워쌀 군량을 싣는다")

s = rep(s, "        if (avail >= 12000 && avail < need && aiFacTroops(f) >= def * 4 * mul / 1.25 && chance(50)) need = avail;", "        if (!AISCOPE && avail >= 12000 && avail < need && aiFacTroops(f) >= def * 4 * mul / 1.25 && chance(50)) need = avail;")      # 파상 공세는 AI 세력만(군단은 문턱을 지킨다)

# 보급: 군단은 제 도시들끼리만, 간이 수송은 쓰지 않는다
s = rep(s, "  var cities = facCities(f);\n  if (cities.length < 2) return;", "  var cities = aiCities(f);\n  if (cities.length < 2) return;")
s = rep(s, "      if (res.ok) { res.unit.ai = { mode: 'supply', target: dest.id, home: b.id }; idle.shift(); here--; }", "      if (res.ok) { res.unit.ai = { mode: 'supply', target: dest.id, home: b.id }; if (AISCOPE) res.unit.corps = AISCOPE.id; idle.shift(); here--; }")
s = rep(s, "    } else if (F.ap >= 10 && (b.gold > 2500 || b.food > 30000)) {", "    } else if (!AISCOPE && F.ap >= 10 && (b.gold > 2500 || b.food > 30000)) {")

s += r"""
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
"""
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
