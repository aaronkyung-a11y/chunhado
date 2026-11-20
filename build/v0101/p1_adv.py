# v0.10.1 (1/…): 군사의 적중률 — "군사의 말이 너무 100% 맞는 것 같은데 지력에 따라 차이가 좀 나야하나"
#  전: 적중률 = 군사 지력 + (군사 지력 − 상대 지력) × 0.5, 50~100.
#      상대보다 똑똑한 만큼이 더해져서 웬만한 군사는 90~100% 였다(tests/adv101.js: 왕랑의 우번(지력 84)은 재야 무장에게 평균 89.1%,
#      다른 세력의 무장에게 평균 94.7%, 시설에 지르는 불에는 100%. 순욱 · 가후는 거의 모든 상대에게 100%).
#  후: 적중률 = 군사 지력. 상대가 군사보다 똑똑하면 그 차이 × 0.5 만큼 깎인다. 50~100.
#      지력 84 → 84%(여섯 번에 한 번 틀린다), 96 → 96%, 76 → 76%. 지력 100 이라야 늘 맞는다.
#      상대의 지력이 없는 일(시설에 지르는 불)도 군사의 지력 그대로다(전에는 지력 67 이상이면 100%).
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)

# ---------------------------------------------------------------- data.js
p = 'src/data.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "var GAME_VERSION = 'v0.10';", "var GAME_VERSION = 'v0.10.1';")
s = rep(s, "/* 군사의 조언이 맞을 확률(%) = 군사 지력 + (군사 지력 − 상대 지력) × k, min~100 */\nvar ADVISE = { k: 0.5, min: 50 };",
           "/* 군사의 조언이 맞을 확률(%) = 군사 지력 − (상대가 더 똑똑한 만큼) × k, min~100.\n"
           "   v0.10.1: 전에는 '군사 지력 + (군사 지력 − 상대 지력) × k' 라 상대보다 똑똑한 만큼이 더해져 웬만한 군사는 90~100% 였다. 이제 지력이 곧 적중률이다 */\n"
           "var ADVISE = { k: 0.5, min: 50 };")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- core.js
p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "/* 조언이 맞을 확률(%) */\nfunction adviceAcc(A, tInt) { return clamp(Math.round(A.int + (A.int - tInt) * ADVISE.k), ADVISE.min, 100); }",
           "/* 조언이 맞을 확률(%): 군사의 지력 그대로. 상대가 더 똑똑하면 그 차이 × k 만큼 깎인다(상대의 지력이 없는 일은 tInt = 0) */\n"
           "function adviceAcc(A, tInt) { return clamp(Math.round(A.int - Math.max(0, (tInt || 0) - A.int) * ADVISE.k), ADVISE.min, 100); }")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- ui_panels.js
p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()
# 도움말
s = rep(s, "맞힐 확률은 <b>군사의 지력 + (군사의 지력 − 상대의 지력) × ' + ADVISE.k + '</b>, ' + ADVISE.min + '~100%입니다(지력 90인 군사가 지력 70인 상대를 보면 100%, 지력 70인 군사가 지력 90인 상대를 보면 60%).</p>' +",
           "맞힐 확률은 <b>군사의 지력 그대로</b>입니다(지력 84면 84%). 상대가 군사보다 똑똑하면 그 차이의 절반만큼 더 틀립니다(지력 70인 군사가 지력 90인 상대를 보면 60%). ' + ADVISE.min + '% 아래로는 내려가지 않고, 지력 100이라야 늘 맞습니다.</p>' +")
# 군사 임명 창: 지금 군사의 적중률 — 한 줄로
s = rep(s, "<p class=\"note\">적중률 <b>' + adviceAcc(A, 60) + '%</b> · <b>' + adviceAcc(A, 75) + '%</b> · <b>' + adviceAcc(A, 90) + '%</b> <small>(상대 지력 60 · 75 · 90)</small></p>",
           "<p class=\"note\">적중률 <b>' + adviceAcc(A, 0) + '%</b>' + (A.int < 95 ? ' <small>· 지력 95인 상대에게는 ' + adviceAcc(A, 95) + '%</small>' : '') + '</p>")
s = rep(s, "<p class=\"cap\">군사는 등용·계략이 통할지 미리 말해 줍니다. 지력이 높을수록 잘 맞습니다.</p>",
           "<p class=\"cap\">군사는 등용·계략이 통할지 미리 말해 줍니다. 지력이 곧 적중률입니다.</p>")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
