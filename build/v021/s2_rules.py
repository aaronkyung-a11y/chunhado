# v0.21 (2) 규칙 손질 — 충성 100 · 등용 · 성의 내구
#   ③ "오경의 마음이 흔들립니다라고 하는데 오경은 충성도 100이거든?"
#      0.20 까지: 충성이 95 이상이면 응하지 않지만, 권하는 쪽 군주와 인연이 있거나 인연이 있는 사람이 가면 그 벽이 없었다 — 충성 100 이어도 등용에 응할 수 있었다
#      (오경: 손책과 인척 → 손책 쪽이 권하면 가능성이 있었고, 그래서 '떠날 수 있는 무장'으로 꼽혔다).
#      → 충성 100 은 누가 권해도 응하지 않는다.
#   ⑤ "등용이 지나치게 쉬운 느낌이 있다."
#      재야 · 포로: 거절하면 다음 턴이 아니라 '다음 달'에 다시 권할 수 있다 — 주사위도 달마다 한 번(턴마다 다시 굴려 보는 일이 없다).
#                   바탕 35 → 24, 매력의 몫 0.7 → 0.6, 위 끝 95 → 88. 포로라서 깎이는 값은 15 → 6(한 번 권할 때의 성공률은 전과 비슷하게 두고, 다시 권하는 틈만 길어진다).
#      다른 세력의 무장: 바탕 15 → 11, 충성 1마다 −2.5 → −2.8, 위 끝 85 → 75.
#      잰 값은 build/v021/measure_recruit.js.
#      값은 RECRUIT · POACH 에 모았다.
#   ⑧ "성 내구도는 전투가 없으면 서서히 회복해야 할듯?"
#      성이 맞은 턴을 적어 두고(b.hitT), 맞지 않은 지 DUR_HEAL.wait 턴이 지나면 턴마다 최대 내구의 DUR_HEAL.pct % 씩 저절로 돌아온다
#      0.20 까지는 싸우는 중에도 턴마다 20(대도시 3000 의 0.7%)씩이라 눈에 띄지 않았다. 맞은 적이 없는 성(옛 저장 포함)은 곧바로 회복을 시작한다.
import io, os
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)

s = rd('src/core.js')
# ③ 충성 100
s = rep(s, "    if (bondOf(t)) return { p: 0, why: why, tie: tie, no: '주군과 ' + bondOf(t) };                       //   제 주군과 인연이 있으면 응하지 않는다",
           "    if (bondOf(t)) return { p: 0, why: why, tie: tie, no: '주군과 ' + bondOf(t) };                       //   제 주군과 인연이 있으면 응하지 않는다\n    if (t.loy >= 100) return { p: 0, why: why, tie: tie, no: '충성 100' };                               //   v0.21: 충성 100 은 누가 권해도 응하지 않는다")
# ⑤ 등용
s = rep(s, "  var p = 35 + (o.cha - 50) * 0.7 + (o.pol - 50) * 0.2;\n  p += (L.cha - 70) * 0.4;",
           "  var p = RECRUIT.base + (o.cha - 50) * RECRUIT.cha + (o.pol - 50) * RECRUIT.pol;\n  p += (L.cha - 70) * RECRUIT.lord;")
s = rep(s, "    else { p -= 15; if (t.f >= 0 && G.factions[t.f].alive) p -= (t.loy - 60) * 0.8; }",
           "    else { p -= RECRUIT.cap; if (t.f >= 0 && G.factions[t.f].alive) p -= (t.loy - 60) * RECRUIT.capLoy; }")
s = rep(s, "    if (dead) why.push(['멸망한 세력 출신', 15 + TIES.fallen]);", "    if (dead) why.push(['멸망한 세력 출신', RECRUIT.cap + TIES.fallen]);")
s = rep(s, "  p = clamp(Math.round(p), 3, 95);\n  if (t.st === 'captive' && t.f >= 0 && G.factions[t.f].alive && bondOf(t)) p = Math.min(p, 5);",
           "  p = clamp(Math.round(p), RECRUIT.min, RECRUIT.max);\n  if (t.st === 'captive' && t.f >= 0 && G.factions[t.f].alive && bondOf(t)) p = Math.min(p, 5);")
s = rep(s, "function recruitRoll(t) { return omenRoll('r' + t.id, t.st === 'active'); }", "function recruitRoll(t) { return omenRoll('r' + t.id, true); }")
s = rep(s, "function recruitRollA(t) { return omenRoll('a|r' + t.id, t.st === 'active'); }", "function recruitRollA(t) { return omenRoll('a|r' + t.id, true); }")
s = rep(s, "/* 등용의 주사위: 대상에만 건다. 재야·포로는 턴마다, 다른 세력의 무장(st 'active')은 달마다 한 번 */", "/* 등용의 주사위: 대상에만 건다. 달마다 한 번(v0.21: 재야 · 포로도 — 0.20 까지는 턴마다였다) */")
s = rep(s, "  t.ask = G.turn + (far ? 3 - G.xun : 1);                               // 다른 세력의 무장: 다음 달 상순부터 다시",
           "  t.ask = G.turn + 3 - G.xun;                                           // 다음 달 상순부터 다시(v0.21: 재야 · 포로도 한 달에 한 번)")
s = rep(s, "  if (askWait(t)) return ERR(far ? '이번 달에는 이미 권했습니다 — 다음 달에 다시 권할 수 있습니다' : '이번 턴에는 이미 권했습니다 — 다음 턴에 다시');",
           "  if (askWait(t)) return ERR('이번 달에는 이미 권했습니다 — 다음 달에 다시 권할 수 있습니다');")
# ⑧ 성의 내구: 맞지 않으면 저절로 돌아온다
s = rep(s, "    if (b.dur < b.maxDur) b.dur = Math.min(b.maxDur, b.dur + 20);\n  }", "    durHeal(b);\n  }")
s = rep(s, "if (gb.kind === 'gate' && gb.owner >= 0 && gb.dur < gb.maxDur) gb.dur = Math.min(gb.maxDur, gb.dur + 20); }", "if (gb.kind === 'gate' && gb.owner >= 0) durHeal(gb); }")
s = rep(s, "    b.troops -= td; b.dur = Math.max(0, b.dur - dd);\n", "    b.troops -= td; b.dur = Math.max(0, b.dur - dd); b.hitT = G.turn;                 // v0.21: 맞은 턴(내구의 회복이 멈춘다)\n")
s = rep(s, "function roundEnd() {", """/* v0.21 성의 내구: 맞지 않은 지 DUR_HEAL.wait 턴이 지나면 턴마다 최대 내구의 DUR_HEAL.pct % 씩 돌아온다(0.20 까지: 싸우는 중에도 턴마다 20).
   durHealAt(b, turn) = 그 턴으로 넘어갈 때 돌아올 양(화면에서는 turn = G.turn + 1 로 다음 턴의 것을 본다) */
function durHealAt(b, turn) {
  if (b.owner < 0 || b.dur >= b.maxDur) return 0;
  if (b.hitT !== undefined && turn - b.hitT < DUR_HEAL.wait) return 0;
  return Math.min(b.maxDur - b.dur, Math.max(1, Math.round(b.maxDur * DUR_HEAL.pct / 100)));
}
function durHeal(b) { var n = durHealAt(b, G.turn); if (n) b.dur += n; return n; }
function roundEnd() {""")
wr('src/core.js', s)

s = rd('src/data.js')
import re
m = re.search(r"var POACH = \{[^\n]*\};", s); assert m, 'POACH'
old = m.group(0)
assert 'base: 15' in old and 'cha: 0.5' in old and 'loyK: 2.5' in old and 'max: 85' in old, old
new = old.replace('base: 15', 'base: 11').replace('loyK: 2.5', 'loyK: 2.8').replace('max: 85', 'max: 75')
s = s.replace(old, new + "\n/* v0.21 재야 · 포로의 등용(0.20 까지: base 35 · cha 0.7 · max 95 · cap 15 · 턴마다 다시 권할 수 있었다). cap = 포로라서 깎이는 값, capLoy = 옛 주군에 대한 충성(60 넘는 만큼)의 몫 */\nvar RECRUIT = { base: 24, cha: 0.6, pol: 0.2, lord: 0.4, cap: 6, capLoy: 0.8, min: 3, max: 88 };")
s = rep(s, "var MAX_DUR = { L: 3000, M: 2400, S: 1800, G: 2200 };", "var MAX_DUR = { L: 3000, M: 2400, S: 1800, G: 2200 };\nvar DUR_HEAL = { wait: 2, pct: 4 };      // v0.21 성의 내구: 맞지 않은 지 wait 턴이 지나면 턴마다 최대 내구의 pct % 씩 돌아온다")
wr('src/data.js', s)
print('s2 ok')
