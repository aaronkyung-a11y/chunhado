# v0.9 AI: 다른 세력의 무장에게 등용을 권한다(플레이어와 같은 규칙, 같은 확률 — 결과를 미리 알지는 못한다)
#  턴마다 POACH_AI.tryPct% 의 확률로 한 번. 쉬는 무장이 있는 거점에서, 이웃 거점의 무장 가운데 성공률이 POACH_AI.min% 이상인 사람 중 (성공률 × 능력 합)이 가장 큰 사람에게.
#  플레이어가 초반 보호를 받는 동안에는 플레이어의 무장에게 권하지 않는다.
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:100])
    return s.replace(a, b)
p = 'src/data.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "/* 군사의 조언이 맞을 확률(%)", "/* AI 가 다른 세력의 무장에게 권하는 빈도: 턴마다 tryPct% 의 확률로 한 번, 성공률이 min% 이상인 대상에게만 */\nvar POACH_AI = { tryPct: 25, min: 12 };\n/* 군사의 조언이 맞을 확률(%)")
io.open(p, 'w', encoding='utf-8').write(s)
p = 'src/ai.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "function aiInternal(f) {", """/* ---------- 다른 세력 무장 등용(v0.9) ---------- */
function aiPoachScore(o) { return o.cha * POACH.cha + o.pol * POACH.pol + (o.sk === '논객' ? POACH.talker : 0); }
function aiPoach(f) {
  var F = G.factions[f];
  if (F.ap < AP.recruit + 20 || !chance(POACH_AI.tryPct)) return;
  var bs = facBases(f), best = null, bv = 0;
  for (var bi = 0; bi < bs.length; bi++) {
    var b = bs[bi], os = idleOfficers(b); if (!os.length) continue;
    var ts = poachTargets(b); if (!ts.length) continue;
    os.sort(function (a, c) { return aiPoachScore(c) - aiPoachScore(a) || a.id - c.id; });
    var o = os[0];
    for (var i = 0; i < ts.length; i++) {
      var t = ts[i];
      if (askWait(t)) continue;
      if (t.f === G.player && G.peace && G.turn < G.peace.until) continue;      // 초반 보호: 그동안은 플레이어의 무장에게 권하지 않는다
      var p = recruitChance(b, o, t); if (p < POACH_AI.min) continue;
      var v = p * (t.ldr + t.war + t.int + t.pol);
      if (v > bv) { bv = v; best = { b: b, o: o, t: t }; }
    }
  }
  if (best) cmdRecruit(best.b, best.o.id, best.t.id);
}
function aiInternal(f) {""")
s = rep(s, "      aiDefense(f); aiCaptives(f); aiInternal(f); aiOffense(f); aiLogistics(f);", "      aiDefense(f); aiCaptives(f); aiPoach(f); aiInternal(f); aiOffense(f); aiLogistics(f);")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
