# v0.8.1 초반 보호 — 보호가 끝난 뒤의 완충(PEACE_RAMP 턴 동안)
#  잰 것: 손을 놓고 있는 약한 세력은 보호가 끝나는 37턴째에 이웃 여럿이 한꺼번에 출진했다(35판 가운데 첫 출진이 37턴인 판이 대부분).
#  ① '국력이 압도적이면 파상 공세'(남는 병력 1.2만 이상 + 세력 병력이 수비의 4배 이상이면 절반 확률로 그냥 출진)도 완충 기간에는 배수를 따라 올린다(4배 → 6.4배에서 시작)
#  ② 완충 기간에는 한 번에 한 세력만 플레이어를 치러 온다 — 다른 AI 세력이 이미 플레이어의 거점으로 가고 있으면 기다린다(플레이어가 먼저 친 세력은 예외)
#  ③ 보호가 3턴 남았을 때와 끝났을 때 턴 재생 중에 자막으로도 알린다
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:100])
    return s.replace(a, b)
p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, """function aiNeedMul(f, owner) {
  var P = G.peace;
  if (!P || owner !== G.player || P.broken[f]) return 1.25;
  return 1.25 + 0.75 * clamp(1 - (G.turn - P.until) / PEACE_RAMP, 0, 1);
}""", """function aiNeedMul(f, owner) {
  var P = G.peace;
  if (!P || owner !== G.player || P.broken[f]) return 1.25;
  return 1.25 + 0.75 * clamp(1 - (G.turn - P.until) / PEACE_RAMP, 0, 1);
}
/* 완충 기간(보호가 끝난 뒤 PEACE_RAMP 턴)인가 — 이때는 한 번에 한 세력만 플레이어를 치러 온다. 플레이어가 먼저 친 세력에게는 해당 없음 */
function peaceRamp(f) { var P = G.peace; return !!P && !P.broken[f] && G.turn < P.until + PEACE_RAMP; }
/* 세력 f 말고 다른 AI 세력이 지금 플레이어의 거점을 치러 가고 있는가 */
function othersOnPlayer(f) {
  for (var i = 0; i < G.units.length; i++) { var u = G.units[i]; if (u.f !== f && u.f !== G.player && u.ai && u.ai.mode === 'attack' && u.ai.target >= 0 && G.bases[u.ai.target].owner === G.player) return true; }
  return false;
}""")
s = rep(s, """    if (pl === 3 && cap) logMsg('석 턴 뒤(' + dateOfTurn(G.peace.until) + ') 초반 보호가 끝납니다 — 그 뒤로는 다른 세력이 우리 거점을 칠 수 있습니다', cap.c, cap.r, f, 2);
    if (pl === 0 && cap) logMsg('초반 보호가 끝났습니다 — 이제 다른 세력이 우리 거점을 칠 수 있습니다', cap.c, cap.r, f, 2);""",
"""    if (pl === 3 && cap) { logMsg('초반 보호가 3턴 남았습니다 — ' + dateOfTurn(G.peace.until) + '부터는 다른 세력이 우리 거점을 칠 수 있습니다', cap.c, cap.r, f, 2); ev({ t: 'news', f: f, c: cap.c, r: cap.r, warn: 1, text: '<b>초반 보호가 3턴 남았습니다</b> — ' + dateOfTurn(G.peace.until) + '부터는 다른 세력이 우리 거점을 칠 수 있습니다' }); }
    if (pl === 0 && cap) { logMsg('초반 보호가 끝났습니다 — 이제 다른 세력이 우리 거점을 칠 수 있습니다', cap.c, cap.r, f, 2); ev({ t: 'news', f: f, c: cap.c, r: cap.r, warn: 1, text: '<b>초반 보호가 끝났습니다</b> — 이제 다른 세력이 우리 거점을 칠 수 있습니다' }); }""")
s = rep(s, "  if (f === G.player) return G.turn > PEACE_ALL || !!P.broken[owner];   // 플레이어 자리를 AI 가 대신 둘 때(시험·AI 대전)",
           "  if (f === G.player) return G.turn > PEACE_ALL;                   // 플레이어 자리를 AI 가 대신 둘 때(시험·AI 대전): 다른 AI 와 같다")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/ai.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, """        if (!aiMayStrike(f, T.owner)) continue;                      // 초반 보호: 남이 지키는 거점을 먼저 치지 않는다
        var def = T.troops;
        enemyUnitsNear(f, T.c, T.r, 3).forEach(function (e) { if (e.f === T.owner) def += e.troops; });
        need = def * aiNeedMul(f, T.owner) + 2500 + (T.kind === 'gate' ? 1500 : 0);
        if (avail >= 12000 && avail < need && aiFacTroops(f) >= def * 4 && chance(50)) need = avail;   // 국력이 압도적이면 파상 공세""",
"""        if (!aiMayStrike(f, T.owner)) continue;                      // 초반 보호: 남이 지키는 거점을 먼저 치지 않는다
        var ramp = T.owner === G.player && peaceRamp(f);              // 보호가 끝난 뒤의 완충 기간
        if (ramp && othersOnPlayer(f)) continue;                     //   한 번에 한 세력만 플레이어를 치러 온다
        var def = T.troops, mul = aiNeedMul(f, T.owner);
        enemyUnitsNear(f, T.c, T.r, 3).forEach(function (e) { if (e.f === T.owner) def += e.troops; });
        need = def * mul + 2500 + (T.kind === 'gate' ? 1500 : 0);
        if (avail >= 12000 && avail < need && aiFacTroops(f) >= def * 4 * mul / 1.25 && chance(50)) need = avail;   // 국력이 압도적이면 파상 공세(완충 기간에는 문턱도 함께 높다)""")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
