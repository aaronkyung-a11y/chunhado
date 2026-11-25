# -*- coding: utf-8 -*-
"""v0.25: (요청 11-25 20:42)
  1. "메뉴에 저장과 불러오기 버튼이 크고 나머지는 좀 작게해도 되겠어. 수명 켜짐 밑에 이 판 이라는 말은 필요없어"
  2. "높은 듯 반반인 듯 이런 말은 높음 보통 낮음 이런 식으로 표기"
  3. "치안 할 때 소리가 이상한 땡똥 하는 소리가 되었어. 바꿔줘"   (소리 자체는 tools/make_audio_v025.py — 여기서는 순찰이 그 소리를 틀게만 한다)
   python3 build/v025/s1_ui.py   (apply.sh 가 v0.24 백업에서 되돌린 뒤 부른다)"""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8').write(s)


def rep(s, a, b, n=1):
    assert s.count(a) == n, (a[:70], s.count(a))
    return s.replace(a, b)


# ───────── data.js: 판 번호 ─────────
d = rd('src/data.js')
d = rep(d, "var GAME_VERSION = 'v0.24';", "var GAME_VERSION = 'v0.25';")
wr('src/data.js', d)

u = rd('src/ui_panels.js')
# ───────── 1. 메뉴: 저장 · 불러오기는 크게, 나머지는 작게. '이 판' 은 뺀다 ─────────
u = rep(u, '<div class="dlg-b"><div class="cmds"><button class="cmd" type="button" data-a="save"><b>저장</b></button><button class="cmd" type="button" data-a="load"><b>불러오기</b></button>\' +',
        '<div class="dlg-b"><div class="cmds mnu-top"><button class="cmd" type="button" data-a="save"><b>저장</b></button><button class="cmd" type="button" data-a="load"><b>불러오기</b></button></div><div class="cmds mnu-rest">\' +')
u = rep(u, "(G.life === 1 ? '켜짐' : '꺼짐') + '</b><small>이 판</small></button>' +", "(G.life === 1 ? '켜짐' : '꺼짐') + '</b></button>' +")
# ───────── 2. 가늠의 말: '높은 듯 · 반반인 듯 · 낮은 듯' → '높음 · 보통 · 낮음' (가운데 말은 또렷이 볼 때도 '보통'으로 맞춘다) ─────────
u = rep(u, "var ODDS_W = ['불가', '매우 낮음', '낮음', '반반', '높음', '매우 높음', '확실'], ODDS_WC = ['불가', '낮은 듯', '낮은 듯', '반반인 듯', '높은 듯', '높은 듯', '확실'];",
        "var ODDS_W = ['불가', '매우 낮음', '낮음', '보통', '높음', '매우 높음', '확실'], ODDS_WC = ['불가', '낮음', '낮음', '보통', '높음', '높음', '확실'];      // v0.25: 어림(셋)도 '높음 · 보통 · 낮음' 으로 적는다 — 어림인 것은 흐린 눈금과 '어림으로만 봅니다' 줄이 알린다")
u = rep(u, "'확률을 말로 가늠해 보여 줍니다 — 높음 · 반반 · 낮음'", "'확률을 말로 가늠해 보여 줍니다 — 높음 · 보통 · 낮음'")
u = rep(u, "숫자 대신 <b>매우 높음 · 높음 · 반반 · 낮음 · 매우 낮음</b>과 눈금 다섯 칸으로", "숫자 대신 <b>매우 높음 · 높음 · 보통 · 낮음 · 매우 낮음</b>과 눈금 다섯 칸으로")
u = rep(u, "미만이면 <b>높은 듯 · 반반인 듯 · 낮은 듯</b> 셋으로만 어림합니다.", "미만이면 <b>높음 · 보통 · 낮음</b> 셋으로만 어림합니다(눈금이 흐리게 보입니다).")
# 헌책의 한마디도 같은 투로: '응할 듯 · 만날 듯' → '응할 것 · 만날 것' (군사의 말 "응할 것입니다 · 만날 것입니다"와 맞춘다. 안 될 때는 전부터 '오늘은 불응 · 오늘은 못 만남')
u = rep(u, '등용 <i class="adv y">응할 듯</i>', '등용 <i class="adv y">응할 것</i>', 2)
u = rep(u, '탐색 <i class="adv y">만날 듯</i>', '탐색 <i class="adv y">만날 것</i>')
# 후계의 가늠(0.23 에 넣은 줄): '그 밖 N명은 76%로 동요' 가 확률 표시(말 · 숫자)를 따르지 않고 늘 숫자였다 — 말로 볼 때는 '동요할 가능성 높음'
u = rep(u, "' · 그 밖 ' + fc.n + '명은 ' + fc.p + '%로 동요' : '');", "' · 그 밖 ' + fc.n + '명은 ' + (UI.pct ? fc.p + '%로 동요' : '동요할 가능성 ' + pcT(fc.p)) : '');")
wr('src/ui_panels.js', u)

# ───────── 메뉴의 생김새 ─────────
c = rd('src/style.css')
c = rep(c, ".cmds.c2 { grid-template-columns: 1fr 1fr; }",
        "/* v0.25 메뉴: 저장 · 불러오기는 크게(두 칸), 나머지 설정은 작게(세 칸) */\n"
        ".cmds.mnu-top { grid-template-columns: 1fr 1fr; gap: 9px; margin-bottom: 10px; }\n"
        ".cmds.mnu-top .cmd { min-height: 68px; }\n"
        ".cmds.mnu-top .cmd b { font-size: 21px; letter-spacing: .1em; }\n"
        ".cmds.mnu-rest { gap: 6px; }\n"
        ".cmds.mnu-rest .cmd { min-height: 44px; padding: 4px 3px; }\n"
        ".cmds.mnu-rest .cmd b { font-size: 13.5px; letter-spacing: .02em; }\n"
        ".cmds.mnu-rest .cmd small { font-size: 10.5px; }\n"
        ".cmds.c2 { grid-template-columns: 1fr 1fr; }")
wr('src/style.css', c)

# ───────── 3. 순찰의 소리: 딱따기(clack) → 순라군의 발걸음(patrol) ─────────
g = rd('src/ui3d.js')
i = g.index("  patrol:   { s: [['clack', 0.8, 0]], gap: 500, syn: 'ui' },"); j = g.index('\n', i)
g = g[:i] + "  patrol:   { s: [['patrol', 0.85, 0]], gap: 700, syn: 'ui' },                                   // v0.25: 순찰 — 순라군의 발걸음 셋(음높이를 흔들지 않는다). 0.22.1 의 딱따기(셈으로 만든 맑은 두 음)는 \"땡 — 똥\"처럼 들려서 뺐다" + g[j:]
assert g.count("'clack'") == 0, g.count("'clack'")
wr('src/ui3d.js', g)
print('s1_ui ok')
