# v0.18 제목 화면 · 단추 — ① 제목 화면을 관우의 전신 그림이 가득 채운다(그림은 src/assets.js 의 TITLE_IMG — tools/make_title18.py 로 만든다)
#   제목 글씨는 세로 한 줄 '三國志' + 낙관 '天下圖'(모두 한자) — 그림의 오른쪽 위 빈 종이에. 단추는 두 줄로 낮게 깔아 발끝까지 보이게 한다.
#   ② 단추에 살짝 두께를(밝은 윗면 · 아래 그림자 · 누르면 내려앉음)  ③ 휴대폰의 '뒤로'가 무장 카드부터 닫는다
#   CH_ROOT=<폴더> 로 다른 나무에 입힐 수 있다(시험용).
import io, os
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)

# ───────────────────────── index.html ─────────────────────────
s = rd('src/index.html')
s = rep(s, """    <div class="t-name">
      <div class="t-han">三國志</div>
      <div><div class="t-seal">天下圖</div><div class="t-ko">삼국지 천하도</div></div>
    </div>
    <div class="t-menu">
      <button id="tNew" class="pri" type="button">새 게임</button>
      <div class="t-row"><button id="tCont" type="button">이어하기</button><button id="tLoad" type="button">불러오기</button></div>
      <div class="t-row"><button id="tHelp" type="button">도움말</button><button id="tShare" type="button">공유</button></div>
      <button id="tInstall" type="button" hidden>앱으로 설치</button>
""", """    <div class="t-name" aria-label="삼국지 천하도">
      <div class="t-han">三國志</div>
      <div class="t-seal">天下圖</div>
    </div>
    <div class="t-menu">
      <div class="t-row"><button id="tNew" class="pri" type="button">새 게임</button><button id="tCont" type="button">이어하기</button></div>
      <div class="t-row t3"><button id="tLoad" type="button">불러오기</button><button id="tHelp" type="button">도움말</button><button id="tShare" type="button">공유</button></div>
      <button id="tInstall" type="button" hidden>앱으로 설치</button>
""")
wr('src/index.html', s)

# ───────────────────────── ui_panels.js · ui3d.js ─────────────────────────
s = rd('src/ui_panels.js')
s = rep(s, "  $('tVer').textContent = GAME_VERSION + ' · 194년 군웅할거';", "  $('tVer').textContent = GAME_VERSION + ' · 삼국지 천하도 · 194년 군웅할거';")
s = rep(s, "function appBack() {\n", "function appBack() {\n  if (ocardOn()) { ocardClose(); return true; }               // v0.18: 겹쳐 뜬 무장 카드부터 닫는다\n")
wr('src/ui_panels.js', s)
s = rd('src/ui3d.js')
s = rep(s, "  $('title').style.backgroundImage = 'url(' + TITLE_IMG + ')';", "  if (typeof TITLE_IMG === 'string' && TITLE_IMG) $('title').style.backgroundImage = 'url(' + TITLE_IMG + ')';      // v0.18: 만든 판에서는 CSS 에 들어 있다(첫 화면부터 그려지게 — tools/build.py)")
wr('src/ui3d.js', s)

# ───────────────────────── style.css ─────────────────────────
s = rd('src/style.css')
s += """
/* ── v0.18 제목 화면: 관우의 전신이 화면을 채운다. 제목은 세로 한 줄(三國志 + 낙관 天下圖), 단추는 낮게 두 줄 ── */
#title { background-position: center top; background-size: cover; }
.t-name { top: max(2.6%, env(safe-area-inset-top)); right: 5.5%; flex-direction: column; align-items: center; gap: 7px; }
.t-han { font-size: clamp(38px, 11.2vw, 62px); letter-spacing: .05em; text-shadow: 0 0 14px #f4efe3, 0 0 5px #f4efe3, 0 0 2px #f4efe3; }
.t-seal { margin-top: 0; font-size: clamp(19px, 5.6vw, 28px); padding: 9px 5px 10px; letter-spacing: .1em; box-shadow: inset 0 0 0 2px #fbf3e44d, 2px 3px 0 #1b1a1826; }
.t-menu { gap: 8px; padding: 30px 18px calc(12px + env(safe-area-inset-bottom, 0px)); background: linear-gradient(#f4efe300, #f4efe3c7 34%, #f4efe3eb); }
.t-menu button { height: 46px; font-size: 16px; letter-spacing: .14em; background-color: #f4efe3f0; }
.t-row { gap: 8px; }
.t-row.t3 button { font-size: 15px; letter-spacing: .06em; }
.t-ver { font-size: 11.5px; color: var(--ink-2); text-shadow: 0 0 4px #f4efe3; }
@media (max-height: 620px) { .t-menu button { height: 42px; } .t-menu { padding-top: 22px; gap: 6px; } }

/* ── v0.18 단추에 살짝 두께를: 윗면은 밝게, 아래에 먹빛 그림자 한 줄. 누르면 내려앉는다 ── */
.cmd, .btn, .act, #bar button, .t-menu button, .du-mv, .x.fold {
  background-image: linear-gradient(#ffffff6b, #ffffff00 48%, #1b1a180f);
  box-shadow: 0 2px 0 #1b1a183d, 0 3px 5px #1b1a181a, inset 0 1px 0 #ffffffb3;
  transition: transform .05s ease-out, box-shadow .05s ease-out;
}
.cmd:active, .btn:active, .act:active, #bar button:active, .t-menu button:active, .du-mv:active, .x.fold:active { transform: translateY(2px); box-shadow: 0 0 0 #1b1a1800, inset 0 2px 3px #00000040; background-image: none; }
.cmd.pri, .btn.pri, .act.pri, #bar #btnEnd, .t-menu button.pri {
  background-image: linear-gradient(#ffffff38, #ffffff00 52%, #00000024);
  box-shadow: 0 2px 0 var(--seal-2), 0 3px 6px #1b1a1833, inset 0 0 0 2px #fbf3e440, inset 0 1px 0 #ffffff66;
}
.cmd.pri:active, .btn.pri:active, .act.pri:active, #bar #btnEnd:active, .t-menu button.pri:active { box-shadow: inset 0 2px 4px #00000059; background-image: none; }
.btn.auto { background-image: linear-gradient(#ffffff2e, #ffffff00 52%); box-shadow: 0 2px 0 #000000a6, 0 3px 5px #1b1a1826, inset 0 1px 0 #ffffff47; }
.cmd.off, .act.off, .btn:disabled, .btn.alt.off, .t-menu button:disabled { box-shadow: 0 1px 0 #1b1a1826; background-image: none; }
"""
wr('src/style.css', s)
print('p4_title18: ok')
