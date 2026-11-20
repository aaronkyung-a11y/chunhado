# v0.9 손질: AI 는 무장이 4명 이하(군주 포함)인 세력의 무장에게는 등용을 권하지 않는다
#  재 본 것(장양 자리를 AI 가 둔 5판, 72턴): 장양군은 무장 4명으로 시작하는데, 보호가 끝난 뒤 새로 얻은 무장(충성 70~85)을 원소·조조가 데려가 한 판은 군주 혼자 남았다.
#  작은 세력이 등용만으로 말라 죽지 않게 바닥을 둔다. 플레이어가 작은 세력에게서 데려오는 것은 막지 않는다.
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:100])
    return s.replace(a, b)
p = 'src/data.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "/* AI 가 다른 세력의 무장에게 권하는 빈도: 턴마다 tryPct% 의 확률로 한 번, 성공률이 min% 이상인 대상에게만 */\nvar POACH_AI = { tryPct: 25, min: 12 };",
           "/* AI 가 다른 세력의 무장에게 권하는 빈도: 턴마다 tryPct% 의 확률로 한 번, 성공률이 min% 이상인 대상에게만.\n   spare = 무장이 이 수 이하(군주 포함)인 세력의 무장에게는 권하지 않는다(작은 세력이 등용만으로 말라 죽지 않게) */\nvar POACH_AI = { tryPct: 25, min: 12, spare: 4 };")
io.open(p, 'w', encoding='utf-8').write(s)
p = 'src/ai.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "      if (t.f === G.player && G.peace && G.turn < G.peace.until) continue;      // 초반 보호: 그동안은 플레이어의 무장에게 권하지 않는다",
           "      if (t.f === G.player && G.peace && G.turn < G.peace.until) continue;      // 초반 보호: 그동안은 플레이어의 무장에게 권하지 않는다\n      if (facOfficers(t.f).length <= POACH_AI.spare) continue;                  // 무장이 몇 안 되는 세력은 건드리지 않는다")
io.open(p, 'w', encoding='utf-8').write(s)
p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "  if (!o || o.st !== 'active' || o.unit !== null || o.f < 0 || isLord(o) || bondOf(o) || o.loy >= POACH.wall) return null;\n  var best = null;",
           "  if (!o || o.st !== 'active' || o.unit !== null || o.f < 0 || isLord(o) || bondOf(o) || o.loy >= POACH.wall) return null;\n  if (facOfficers(o.f).length <= POACH_AI.spare) return null;          // AI 는 무장이 몇 안 되는 세력의 무장에게는 권하지 않는다\n  var best = null;")
io.open(p, 'w', encoding='utf-8').write(s)
p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "  '<p>다른 세력도 같은 규칙으로 <b>내 무장을 데려갑니다</b>(초반 보호 기간에는 권하지 않습니다).",
           "  '<p>다른 세력도 같은 규칙으로 <b>내 무장을 데려갑니다</b>(초반 보호 기간에는 권하지 않고, 무장이 ' + POACH_AI.spare + '명 이하인 세력의 무장에게도 권하지 않습니다).")
io.open(p, 'w', encoding='utf-8').write(s)
p = 'tools/pack_sources.py'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "build/v09/p5_ui2.py build/v09/p6_touch.py\n", "build/v09/p5_ui2.py build/v09/p6_touch.py build/v09/p7_spare.py\n")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
