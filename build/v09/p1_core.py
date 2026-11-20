# v0.9 규칙: 군사(軍師)와 조언 · 이웃 거점의 다른 세력 무장 등용
#  요청(2026-11-20 07:31): "그리고 군사를 둘 수 있으면 좋겠고, 군사가 조언 해주면 좋겠어. 뭔가 하려고 할 때 성공여부를 맞추는 건데 지력 차이에 따라서 확률이 다르게? …
#                          등용을 다른 곳에 속해있는 무장도 인접했다면 할 수 있어야해."
#  ① 등용과 계략의 성패를 '이번 턴 · 대상(· 계략 종류)'으로 미리 정해 둔다(omenRoll). 그래야 군사가 하기 전에 말할 수 있고, 창을 다시 열거나 저장을 다시 불러도 답이 같다.
#     주사위를 '누가 하는가'에 걸지 않는 까닭: 걸면 무장마다 주사위가 따로라서, 군사에게 무장을 바꿔 가며 물어 통하는 사람만 보내면 성공률이 1 − Π(1 − p)로 뛴다.
#     대상에만 걸면 가장 잘하는 사람이 안 되면 누구도 안 된다(= 한 턴에 그 대상에게 주사위는 한 번).
#  ② 군사: 세력마다 한 사람(G.factions[f].adv). 조언이 맞을 확률 = 군사 지력 + (군사 지력 − 상대 지력) × 0.5, 50~100%.
#     '맞는가'의 주사위도 대상에만 건다 — 군사를 바꿔 가며 물어 다수결을 내는 것을 막는다(지력이 높은 군사가 맞는 때는 낮은 군사가 맞는 때를 모두 포함한다).
#  ③ 다른 세력 무장 등용: 내 거점과 길로 바로 이어진 이웃 거점에 머무는 무장(군주·출진·이동 중 제외). 제 주군과 인연이 있거나 충성 95 이상이면 응하지 않는다.
#     한 무장에게는 한 번 권하면 3턴 동안 다시 권할 수 없고(재야·포로도 한 턴에 한 번), 거절한 다른 세력 무장은 충성이 3 오른다.
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:100])
    return s.replace(a, b)
p = 'src/data.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "var GAME_VERSION = 'v0.8.1';", "var GAME_VERSION = 'v0.9';")
s = rep(s, "/* 초반 보호(v0.8.1):", """/* 다른 세력의 무장 등용(v0.9). 성공률 = base + (담당 매력−50)×cha + (담당 정치−50)×pol + (내 군주 매력 − 그쪽 군주 매력)×lord − (대상 충성−loy0)×loyK
   + 논객 talker + 대상이 내 군주와 인연이면 bond.  0~max%.  충성이 wall 이상이거나 제 주군과 인연이 있으면 0.
   wait = 한 번 권한 뒤 다시 권할 수 있을 때까지의 턴 수, up = 거절한 무장의 충성이 오르는 폭 */
var POACH = { base: 15, cha: 0.5, pol: 0.2, lord: 0.25, loy0: 70, loyK: 2.5, talker: 20, bond: 30, max: 85, wall: 95, wait: 3, up: 3 };
/* 군사의 조언이 맞을 확률(%) = 군사 지력 + (군사 지력 − 상대 지력) × k, min~100 */
var ADVISE = { k: 0.5, min: 50 };

/* 초반 보호(v0.8.1):""")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()
# 고정 씨앗
s = rep(s, "    player: playerFaction, factions: [], officers: [], bases: [], units: [], fires: {}, nextUnit: 1, log: [], over: null, aiOnly: false\n  };",
           "    player: playerFaction, factions: [], officers: [], bases: [], units: [], fires: {}, nextUnit: 1, log: [], over: null, aiOnly: false\n  };\n  G.seed0 = G.seed;                                                // 판마다 고정된 씨앗(G.seed 는 난수를 뽑을 때마다 바뀐다) — 미리 정해 두는 결과(omenRoll)에 쓴다")
s = rep(s, "    G.factions.push({ id: i, name: sf.n, color: sf.color, lord: -1, ap: 80, alive: true });",
           "    G.factions.push({ id: i, name: sf.n, color: sf.color, lord: -1, ap: 80, alive: true, adv: -1 });")
s = rep(s, "  G.peace = { until: 1 + peaceTurns(G.player), broken: {} };      // 초반 보호: until 턴부터 AI 가 플레이어의 거점을 칠 수 있다\n",
           "  G.peace = { until: 1 + peaceTurns(G.player), broken: {} };      // 초반 보호: until 턴부터 AI 가 플레이어의 거점을 칠 수 있다\n  for (i = 0; i < G.factions.length; i++) autoAdvisor(i);          // 군사: 처음에는 지력이 가장 높은 무장(군주 제외)\n")
# omen · 군사
s = rep(s, "function ri(a, b) { return a + Math.floor(rnd() * (b - a + 1)); }", """function ri(a, b) { return a + Math.floor(rnd() * (b - a + 1)); }
/* ---------- 미리 정해 둔 결과(v0.9) ----------
   등용과 계략의 성패는 '이번 턴 · 대상(· 계략 종류)'으로 미리 정해져 있다: 성공률이 p 일 때 omenRoll(key) < p 이면 성공.
   같은 턴에 같은 대상이면 몇 번을 물어도, 창을 다시 열어도, 저장을 다시 불러도 같다 — 그래서 군사가 하기 전에 말할 수 있다.
   G.rnd 흐름(G.seed)과는 따로 논다. */
function strHash(s) { var h = 2166136261 | 0; for (var i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h | 0; }
function omenRoll(key) {                                           // 0 이상 100 미만
  var t = (G.seed0 | 0) ^ Math.imul((G.turn | 0) + 0x7F4A7C15, 0x9E3779B1) ^ strHash(key);
  t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); t = Math.imul(t ^ (t >>> 13), 0x5bd1e995 | 1);
  return ((t ^ (t >>> 15)) >>> 0) / 4294967296 * 100;
}
function recruitKey(t) { return 'r' + t.id; }                       // 등용: 대상에만 건다
function ployKey(ploy, t) { return 'p' + ploy.id + (t.u ? 'u' + t.u.id : 'k' + K(t.c, t.r)); }   // 계략: 종류 + 대상 부대(부대가 없으면 칸)""")
s = rep(s, "function isLord(o) { return o.f >= 0 && G.factions[o.f].lord === o.id; }", """function isLord(o) { return o.f >= 0 && G.factions[o.f].lord === o.id; }
/* ---------- 군사(軍師, v0.9) ----------
   세력마다 한 사람. 군주는 될 수 없다. 출진해 있거나 다른 거점으로 가는 중이어도 군사다. 사로잡히거나 죽거나 떠나면 자리가 비고, 그 세력의 차례가 올 때 지력이 가장 높은 무장으로 채운다. */
function advOk(o, f) { return !!o && o.f === f && (o.st === 'active' || o.st === 'travel') && G.factions[f].lord !== o.id; }
function facAdv(f) { var F = G.factions[f]; if (!F || F.adv === undefined || F.adv < 0) return null; var o = off(F.adv); return advOk(o, f) ? o : null; }
function advCandidates(f) { return G.officers.filter(function (o) { return advOk(o, f); }).sort(function (a, b) { return b.int - a.int || a.id - b.id; }); }
function autoAdvisor(f) { var c = advCandidates(f); G.factions[f].adv = c.length ? c[0].id : -1; return c.length ? c[0] : null; }
function setAdvisor(f, id) { var o = off(id); if (!advOk(o, f)) return ERR('군사로 삼을 수 없는 무장입니다'); G.factions[f].adv = o.id; return { ok: true }; }
/* 조언이 맞을 확률(%) */
function adviceAcc(A, tInt) { return clamp(Math.round(A.int + (A.int - tInt) * ADVISE.k), ADVISE.min, 100); }
/* 조언: { adv, acc, says } — says = "통한다"고 말하는가. 군사가 없으면 null.
   실제 결과(omenRoll(key) < p)를 acc% 의 확률로 바르게, 나머지는 거꾸로 말한다. '맞는가'도 대상에만 걸려 있어, 군사를 바꿔 물어도 새 정보가 생기지 않는다 */
function advise(f, key, p, tInt) {
  var A = facAdv(f); if (!A) return null;
  var real = omenRoll(key) < p, acc = adviceAcc(A, tInt);
  return { adv: A, acc: acc, says: (omenRoll('a|' + key) < acc) ? real : !real };
}""")
# 군사 자리 채우기
s = rep(s, """  var F = G.factions[f], i;
  if (!F.alive) return;
  F.ap = Math.min(255, F.ap + apRegen(f));""", """  var F = G.factions[f], i;
  if (!F.alive) return;
  if (!facAdv(f)) {                                                // 군사 자리가 비었으면 채운다
    var hadAdv = F.adv !== undefined && F.adv >= 0, na = autoAdvisor(f);
    if (f === G.player && !G.aiOnly && na && G.turn > 1) logMsg((hadAdv ? '군사 자리가 비어 ' : '') + josa(na.n, '을를') + ' 군사로 삼았다 (지력 ' + na.int + ')', undefined, undefined, f, 1);
  }
  F.ap = Math.min(255, F.ap + apRegen(f));""")
# 등용
s = rep(s, """function recruitChance(b, o, t) {
  var p = 35 + (o.cha - 50) * 0.7 + (o.pol - 50) * 0.2;
  var L = off(G.factions[b.owner].lord);""", """/* 다른 세력의 무장 가운데 거점 b 에서 등용을 권할 수 있는 사람: b 와 길로 바로 이어진 이웃 거점에 머무는 무장(군주 제외, 출진·이동 중 제외) */
function isNeighbor(b, id) { var a = ADJ[b.id]; for (var i = 0; i < a.length; i++) if (a[i].to === id) return true; return false; }
function canPoach(b, t) { return !!t && t.st === 'active' && t.unit === null && t.f >= 0 && t.f !== b.owner && !isLord(t) && G.bases[t.loc].owner === t.f && isNeighbor(b, t.loc); }
function poachTargets(b) {
  var out = [], seen = {};
  if (b.owner < 0) return out;
  ADJ[b.id].forEach(function (e) {
    var nb = G.bases[e.to]; if (seen[nb.id] || nb.owner < 0 || nb.owner === b.owner) return; seen[nb.id] = 1;
    baseOfficers(nb).forEach(function (o) { if (!isLord(o)) out.push(o); });
  });
  return out;
}
/* 등용을 권한 뒤 다시 권할 수 있는 턴(그 전에는 못 권한다). 재야·포로는 한 턴에 한 번, 다른 세력의 무장은 POACH.wait 턴에 한 번 */
function askWait(t) { return (t.ask !== undefined && t.ask > G.turn) ? t.ask - G.turn : 0; }
function recruitChance(b, o, t) {
  var L = off(G.factions[b.owner].lord);
  if (t.st === 'active') {                                              // 다른 세력의 무장(v0.9)
    var mine = bondWith(t, b.owner);
    if (bondOf(t)) return 0;                                            //   제 주군과 인연이 있으면 응하지 않는다
    if (t.loy >= POACH.wall && !mine) return 0;                         //   충성이 아주 높아도 응하지 않는다
    var q = POACH.base + (o.cha - 50) * POACH.cha + (o.pol - 50) * POACH.pol + (L.cha - off(G.factions[t.f].lord).cha) * POACH.lord - (t.loy - POACH.loy0) * POACH.loyK;
    if (o.sk === '논객') q += POACH.talker;
    if (mine) q += POACH.bond;
    return clamp(Math.round(q), 0, POACH.max);
  }
  var p = 35 + (o.cha - 50) * 0.7 + (o.pol - 50) * 0.2;""")
s = rep(s, """  var t = off(tid);
  if (!t || t.loc !== b.id || !((t.st === 'free') || (t.st === 'captive' && t.capF === b.owner))) return ERR('등용할 수 없는 대상입니다');
  if (!needAP(b.owner, AP.recruit)) return ERR('행동력이 부족합니다');
  useAP(b.owner, AP.recruit);
  var o = os[0]; markActed(os, 15);
  if (chance(recruitChance(b, o, t))) {
    if (t.st === 'captive') { var i = b.captives.indexOf(t.id); if (i >= 0) b.captives.splice(i, 1); }
    t.st = 'active'; t.f = b.owner; t.capF = -1; t.unit = null; t.acted = true; t.loy = 70 + ri(0, 15); t.merit = Math.round(t.merit * 0.5); if (bondOf(t)) t.loy = 100;
    o.merit += 60;
    return { ok: true, joined: true };
  }
  return { ok: true, joined: false };
}""", """  var t = off(tid), far = canPoach(b, t);
  if (!t || !(far || (t.loc === b.id && ((t.st === 'free') || (t.st === 'captive' && t.capF === b.owner))))) return ERR('등용할 수 없는 대상입니다');
  if (askWait(t)) return ERR(far ? '얼마 전에 권했습니다 — ' + askWait(t) + '턴 뒤에 다시 권할 수 있습니다' : '이번 턴에는 이미 권했습니다 — 다음 턴에 다시');
  if (!needAP(b.owner, AP.recruit)) return ERR('행동력이 부족합니다');
  useAP(b.owner, AP.recruit);
  var o = os[0]; markActed(os, 15);
  var p = recruitChance(b, o, t), okR = omenRoll(recruitKey(t)) < p;    // 미리 정해 둔 결과(군사가 미리 말해 줄 수 있다)
  t.ask = G.turn + (far ? POACH.wait : 1);
  if (okR) {
    var from = far ? t.f : -1, fb = far ? G.bases[t.loc] : null;
    if (t.st === 'captive') { var i = b.captives.indexOf(t.id); if (i >= 0) b.captives.splice(i, 1); }
    if (far) { t.job = null; t.loc = b.id; if (G.factions[from].adv === t.id) G.factions[from].adv = -1; }      // 맡던 공사·군사 자리를 두고 이쪽으로 넘어온다
    t.st = 'active'; t.f = b.owner; t.capF = -1; t.unit = null; t.acted = true; t.loy = 70 + ri(0, 15); t.merit = Math.round(t.merit * 0.5); if (bondOf(t)) t.loy = 100;
    o.merit += far ? 100 : 60;
    if (far) {
      logMsg(facName(b.owner) + '군 ' + josa(o.n, '이가') + ' ' + facName(from) + '군의 ' + josa(t.n, '을를') + ' 등용 (' + fb.n + ' → ' + b.n + ')', b.c, b.r, from === G.player ? G.player : b.owner, from === G.player ? 2 : 1);
      if (from === G.player && !G.aiOnly) ev({ t: 'news', f: b.owner, c: fb.c, r: fb.r, warn: 1, text: '<b>' + fb.n + '의 ' + josa(t.n, '이가') + ' ' + facName(b.owner) + '군의 등용에 응해 떠났습니다</b>' });
    }
    return { ok: true, joined: true, p: p, far: far, from: from };
  }
  if (far) {                                                            // 거절: 마음을 다잡는다
    var l0 = t.loy; t.loy = Math.min(100, t.loy + POACH.up);
    if (t.f === G.player && !G.aiOnly) logMsg(facName(b.owner) + '군 ' + josa(o.n, '이가') + ' 우리 ' + t.n + '에게 등용을 권했으나 거절 (충성 ' + l0 + ' → ' + t.loy + ')', G.bases[t.loc].c, G.bases[t.loc].r, G.player, 1);
  }
  return { ok: true, joined: false, p: p, far: far };
}""")
# 계략: 미리 정해 둔 결과
s = rep(s, """  var tu = t.u || null, p = ployChance(u, ploy, tu);
  res.p = p;
  if (chance(p)) {""", """  var tu = t.u || null, p = ployChance(u, ploy, tu);
  res.p = p;
  if (omenRoll(ployKey(ploy, t)) < p) {                                 // v0.9: 미리 정해 둔 결과(같은 턴·같은 계략·같은 대상이면 같다)""")
# 옛 저장
s = rep(s, "  if (!g.peace && SCENARIO.factions[g.player]) g.peace = { until: 1 + peaceFor(startTroops(g.player)), broken: {} };\n  G = g; reindex(); REPORT = []; EVQ = [];",
"""  if (!g.peace && SCENARIO.factions[g.player]) g.peace = { until: 1 + peaceFor(startTroops(g.player)), broken: {} };
  if (g.seed0 === undefined) g.seed0 = (g.seed ^ 0x2545F491) | 0;        // v0.9: 미리 정해 두는 결과의 고정 씨앗(옛 저장에는 없다 — 열 때 한 번 정해 저장본에 남는다)
  G = g; reindex(); REPORT = []; EVQ = [];
  for (var fi = 0; fi < G.factions.length; fi++) if (G.factions[fi].adv === undefined) { G.factions[fi].adv = -1; if (G.factions[fi].alive) autoAdvisor(fi); }   // v0.9: 군사""")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
