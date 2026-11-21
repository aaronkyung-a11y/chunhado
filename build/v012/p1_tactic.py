# v0.12 (1/…): 전법이 실패했을 때의 피해  (data.js)
#  요청 "특기 공격에 실패했을 때에도 일반 공격 수준의 공격력 또는 그보다 약간 약하게라도 나와야할 것 같은데, 격차가 너무 커."
#   - TACTIC_K.failDmg 0.4 → 0.85: 실패하면 보통 공격의 85%(전에는 40%). 성공(전법 배수 1.0~1.5)과의 벌어짐이 2.5~3.75배 → 1.18~1.76배.
#   - 그대로 둔 것: 실패하면 효과가 없고, 기력은 쓰며, 반격은 보통 공격의 1.55배(failCounter 0.85) — 실패는 여전히 보통 공격보다 손해다.
#   - 도움말·셈법 창·AI 의 기대값(tacticExpect)은 이 상수로 셈하므로 함께 바뀐다.
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)

p = 'src/data.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "var GAME_VERSION = 'v0.11';", "var GAME_VERSION = 'v0.12';")
s = rep(s, "   v0.9.1: 성공해도 반격은 보통 공격만큼, 실패는 더 아프게, 무장의 차이는 더 크게.   v0.8~0.9: 0.4 / 0.5 / 0.7 / 1.3(1.43) / 0.6 [−24~+12]   v0.7: 0.25 / 0.6 / 0.4 */\n"
           "var TACTIC_K = { okCounter: 0.55, failDmg: 0.4, failCounter: 0.85,",
           "   v0.12: 실패해도 피해는 보통 공격에 가깝게(failDmg 0.4 → 0.85) — 실패의 값은 기력과 큰 반격으로 치른다.\n"
           "   v0.9.1~0.11: 0.55 / 0.4 / 0.85 — 성공해도 반격은 보통 공격만큼, 실패는 더 아프게, 무장의 차이는 더 크게.   v0.8~0.9: 0.4 / 0.5 / 0.7 / 1.3(1.43) / 0.6 [−24~+12]   v0.7: 0.25 / 0.6 / 0.4 */\n"
           "var TACTIC_K = { okCounter: 0.55, failDmg: 0.85, failCounter: 0.85,")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
