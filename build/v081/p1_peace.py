# v0.8.1 초반 보호: "초반에 병력이 적은 곳으로 시작할 때는 병력이 많은 곳에서 너무 순식간에 압도적으로 쳐들어와서 게임을 하기가 어려워진다."
#  재 본 것(tests/rush8.js, 시작 병력 1만 미만인 일곱 세력 × 5판, 그 세력이 손을 놓고 있을 때):
#    첫 피격 턴의 가운데값 v0.7 14 → v0.8 8, 6턴 안에 맞은 판 5 → 15(35판 중), 72턴 안에 망한 판 30 → 35.   유비는 v0.8 에서 3턴째에 여포에게 맞았다.
#  까닭: AI 는 첫 턴부터 '남는 병력 ≥ 상대 병력×1.25 + 2,500'이면 바로 출진한다(유예 없음, 플레이어의 성에는 가산점 +3 까지). v0.8 에서 성역 멈춤이 없어져 더 일찍 닿고, 수입이 늘어 더 빨리 불어난다.
#  고침: ① 처음 PEACE_ALL(12)턴은 어느 AI 도 남이 지키는 거점·시설을 먼저 치지 않는다(빈 성 차지·방어·부대끼리의 싸움은 그대로)
#        ② 플레이어는 시작 병력이 적을수록 더 오래: 1만 미만 36턴(1년), 2만 미만 24턴(8개월), 그 밖 12턴. 그동안 AI 는 플레이어의 거점·시설을 치지 않는다
#        ③ 플레이어가 어떤 세력의 거점·시설을 먼저 치면 그 세력에 대해서는 보호가 풀린다
#        ④ 보호가 끝난 뒤 24턴에 걸쳐, AI 가 플레이어를 칠 때 필요한 병력 우위가 2.0배 → 1.25배로 내려온다(끝나자마자 사방에서 몰려오지 않게). 플레이어 가산점 +3 은 없앰
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:100])
    return s.replace(a, b)
p = 'src/data.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "/* 수입과 비용 — v0.8:", """/* 초반 보호(v0.8.1): 처음 PEACE_ALL 턴 동안은 어느 AI 세력도 남이 지키는 거점·시설을 먼저 치지 않는다(빈 성 차지·방어·부대끼리의 싸움은 한다).
   플레이어는 시작 병력이 적을수록 더 오래 보호받는다. 플레이어가 먼저 친 세력에게는 보호가 풀린다.
   PEACE_RAMP: 보호가 끝난 뒤 이만큼의 턴에 걸쳐 'AI 가 플레이어를 칠 때 필요한 병력 우위'가 2.0배에서 1.25배로 내려온다 */
var PEACE_ALL = 12;
var PEACE_PLAYER = [[10000, 36], [20000, 24]];      // [시작 병력이 이보다 적으면, 보호 턴 수] — 그 밖은 PEACE_ALL
var PEACE_RAMP = 24;

/* 수입과 비용 — v0.8:""")
s = rep(s, "var GAME_VERSION = 'v0.8';", "var GAME_VERSION = 'v0.8.1';")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "function dateStr() { return G.year + '년 ' + G.month + '월 ' + ['상순', '중순', '하순'][G.xun]; }",
"""function dateStr() { return G.year + '년 ' + G.month + '월 ' + ['상순', '중순', '하순'][G.xun]; }
function dateOfTurn(t) { var m = Math.floor((t - 1) / 3); return (194 + Math.floor(m / 12)) + '년 ' + (m % 12 + 1) + '월 ' + ['상순', '중순', '하순'][(t - 1) % 3]; }   // 턴 번호 → 날짜(1턴 = 194년 1월 상순)
/* ---------- 초반 보호 ---------- */
function peaceTurns(f) {                 // 세력 f 로 시작하면 몇 턴 보호받는가(시작 병력으로 정한다)
  var t = 0; G.bases.forEach(function (b) { if (b.owner === f) t += b.troops; });
  for (var i = 0; i < PEACE_PLAYER.length; i++) if (t < PEACE_PLAYER[i][0]) return PEACE_PLAYER[i][1];
  return PEACE_ALL;
}
function peaceLeft() { return G.peace ? Math.max(0, G.peace.until - G.turn) : 0; }      // 플레이어의 보호가 몇 턴 남았나
/* AI 세력 f 가 owner 의 거점·시설을 '먼저' 쳐도 되는가 */
function aiMayStrike(f, owner) {
  if (owner < 0 || owner === f) return true;
  var P = G.peace;
  if (!P) return true;                                             // 옛 저장: 보호 없음
  if (owner === G.player) return G.turn >= P.until || !!P.broken[f];
  if (f === G.player) return G.turn > PEACE_ALL || !!P.broken[owner];   // 플레이어 자리를 AI 가 대신 둘 때(시험·AI 대전)
  return G.turn > PEACE_ALL;                                       // AI 끼리: 처음 PEACE_ALL 턴은 쉰다
}
/* AI 가 플레이어의 거점을 칠 때 필요한 병력 우위(배): 보호가 막 끝났을 때 2.0, PEACE_RAMP 턴 뒤 1.25. 플레이어가 먼저 친 세력은 1.25 */
function aiNeedMul(f, owner) {
  var P = G.peace;
  if (!P || owner !== G.player || P.broken[f]) return 1.25;
  return 1.25 + 0.75 * clamp(1 - (G.turn - P.until) / PEACE_RAMP, 0, 1);
}""")
# 새 판: 보호 기간
s = rep(s, """  for (i = 0; i < G.officers.length; i++) { var lo = G.officers[i]; if (lo.f >= 0 && G.factions[lo.f].lord !== lo.id) lo.loy = loyNat(lo); }   // 군주가 정해진 뒤에 매긴다
""", """  for (i = 0; i < G.officers.length; i++) { var lo = G.officers[i]; if (lo.f >= 0 && G.factions[lo.f].lord !== lo.id) lo.loy = loyNat(lo); }   // 군주가 정해진 뒤에 매긴다
  G.peace = { until: 1 + peaceTurns(G.player), broken: {} };      // 초반 보호: until 턴부터 AI 가 플레이어의 거점을 칠 수 있다
""")
# 플레이어가 먼저 치면 풀린다 + 끝날 때 알림
s = rep(s, """function actEv(u, t, res, f, name, ac, ar, tf) {
  if (res && res.ok) {""", """function actEv(u, t, res, f, name, ac, ar, tf) {
  if (res && res.ok && G.peace && f === G.player && t) {           // 플레이어가 남의 거점·시설을 먼저 치면 그 세력에 대한 보호가 풀린다
    var pf = (t.kind === 'base' || t.kind === 'fac') ? (t.b ? t.b.owner : -1) : (!t.u && plotAt(t.c, t.r) && plotAt(t.c, t.r).plot.fac ? plotAt(t.c, t.r).base.owner : -1);
    if (pf >= 0 && pf !== f && !G.peace.broken[pf]) { G.peace.broken[pf] = true; if (G.turn < G.peace.until) res.brokePeace = pf; }
  }
  if (res && res.ok) {""")
s = rep(s, """function phaseStart(f) {
""", """function phaseStart(f) {
  if (f === G.player && G.peace && !G.aiOnly) {                    // 보호가 끝나 가는 것을 미리 알린다
    var pl = G.peace.until - G.turn, cap = facCities(f)[0] || facBases(f)[0];
    if (pl === 3 && cap) logMsg('석 턴 뒤(' + dateOfTurn(G.peace.until) + ') 초반 보호가 끝납니다 — 그 뒤로는 다른 세력이 우리 거점을 칠 수 있습니다', cap.c, cap.r, f, 2);
    if (pl === 0 && cap) logMsg('초반 보호가 끝났습니다 — 이제 다른 세력이 우리 거점을 칠 수 있습니다', cap.c, cap.r, f, 2);
  }
""")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/ai.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, """        var def = T.troops;
        enemyUnitsNear(f, T.c, T.r, 3).forEach(function (e) { if (e.f === T.owner) def += e.troops; });
        need = def * 1.25 + 2500 + (T.kind === 'gate' ? 1500 : 0);""", """        if (!aiMayStrike(f, T.owner)) continue;                      // 초반 보호: 남이 지키는 거점을 먼저 치지 않는다
        var def = T.troops;
        enemyUnitsNear(f, T.c, T.r, 3).forEach(function (e) { if (e.f === T.owner) def += e.troops; });
        need = def * aiNeedMul(f, T.owner) + 2500 + (T.kind === 'gate' ? 1500 : 0);""")
s = rep(s, "sc = 50 - def / 400 - len * 0.5 + (T.kind === 'city' ? 15 : 0) + (T.sz === 'L' ? 8 : 0) + (T.owner === G.player ? 3 : 0);", "sc = 50 - def / 400 - len * 0.5 + (T.kind === 'city' ? 15 : 0) + (T.sz === 'L' ? 8 : 0);      // v0.8.1: 플레이어의 성에 주던 가산점(+3)을 없앰")
s = rep(s, "    if (mode === 'attack' && T && T.owner >= 0 && T.owner !== f) {", "    if (mode === 'attack' && T && T.owner >= 0 && T.owner !== f && aiMayStrike(f, T.owner)) {")
s = rep(s, "for (i = 0; i < ats.length; i++) if (ats[i].kind === 'fac' && chance(15)) {", "for (i = 0; i < ats.length; i++) if (ats[i].kind === 'fac' && aiMayStrike(f, ats[i].b.owner) && chance(15)) {")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
