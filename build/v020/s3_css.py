# v0.20 (3) 화면의 틀 — 네모칸을 붓으로 두른 듯이 · 아래 줄(턴 종료)이 잘리지 않게 · 아래에 더 있을 때는 큰 화살표
#   "네모칸들이 동양화와 어울리지 않는다. 너무 딱딱해" / "턴 종료 버튼이 너무 끝에 있다. 잘려나가는 거 같다" / "아래에 더 있습니다라기보다는 화살표가 큰게 좋을 듯"
#   · 단추 · 선택 칸의 곧은 테두리 대신: 붓으로 그은 듯 흔들리고 마른 선(가짜 요소 + SVG 거름 #inkEdge). 모서리는 손으로 그린 듯 조금씩 다르게 둥글다.
#   · 판(위 정보줄 · 아래 판 · 아래 줄 · 창)의 경계선: 가운데가 굵고 끝이 가늘어지는 붓 한 획.
#   · 아래 줄: 좁은 화면(360px)에서 '다음 부대 N'이 뜨면 '턴 종료'가 화면 밖으로 밀렸다 — 단추가 줄어들 수 있게 하고, 그래도 넘치면 글씨와 여백을 한 단계씩 줄인다(barFit).
import io, os
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)

STROKE = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 600 16' preserveAspectRatio='none'%3E"
          "%3Cfilter id='f' x='-2%25' y='-90%25' width='104%25' height='280%25'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.012 0.45' numOctaves='2' seed='SEED' result='n'/%3E"
          "%3CfeDisplacementMap in='SourceGraphic' in2='n' scale='5' xChannelSelector='R' yChannelSelector='G' result='d'/%3E"
          "%3CfeTurbulence type='fractalNoise' baseFrequency='0.35 0.9' numOctaves='1' seed='11' result='g'/%3E%3CfeColorMatrix in='g' type='matrix' values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -1.5 1.62' result='ga'/%3E"
          "%3CfeComposite in='d' in2='ga' operator='in'/%3E%3C/filter%3E"
          "%3Cpath d='M3 8 C 90 4.6 300 4.2 520 5.6 C 560 6 590 7 597 8 C 588 9.2 560 10.4 520 10.8 C 300 12 90 11.2 3 8Z' fill='%231b1a18' filter='url(%23f)'/%3E%3C/svg%3E\")")
CSS = """
/* ── v0.20 붓으로 두른 틀: 곧은 네모 대신 흔들리고 마른 먹선 ── */
:root { --rad-a: 10px 6px 11px 5px / 6px 11px 5px 10px; --rad-b: 6px 11px 5px 10px / 10px 5px 11px 6px; --rad-s: 5px 3px 6px 3px / 3px 6px 3px 5px;
  --stroke-a: STROKE_A; --stroke-b: STROKE_B; }
.cmd, .btn, .act, #bar button, .t-menu button, .opt, .pl-ctl button, .hm-links button, .du-mv, .x.fold, .seg { position: relative; border-color: transparent; border-radius: var(--rad-a); }
.cmd:nth-child(even), .act:nth-child(even), .opt:nth-child(even), #bar button:nth-child(even), .t-menu button:nth-child(even), .btn:nth-of-type(even) { border-radius: var(--rad-b); }
.cmd::after, .btn::after, .act::after, #bar button::after, .t-menu button::after, .opt::after, .pl-ctl button::after, .hm-links button::after, .du-mv::after, .x.fold::after, .seg::after {
  content: ''; position: absolute; inset: 0; border: solid #1b1a18e8; border-width: 1.5px 1.9px 2.5px 1.6px; border-radius: inherit; filter: url(#inkEdge); pointer-events: none; }
.opt::after { border-color: #1b1a1899; border-width: 1.2px 1.5px 1.9px 1.3px; }
.opt.on::after { border-color: var(--seal); border-width: 2px 2.4px 3px 2.1px; }
.cmd.pri::after, .btn.pri::after, .act.pri::after, #bar #btnEnd::after, .t-menu button.pri::after { border-color: var(--seal-2); }
.btn.auto::after { border-color: #000000d9; }
.cmd.off::after, .act.off::after, .btn:disabled::after, .btn.alt.off::after, .t-menu button:disabled::after { border-color: #1b1a1866; border-width: 1.2px 1.4px 1.7px 1.2px; }
.cmd, .btn, .act, #bar button, .t-menu button, .du-mv, .x.fold { box-shadow: 0 2px 1px -1px #1b1a1830, 0 4px 8px -2px #1b1a1826, inset 0 1px 0 #ffffffa6; }
.cmd.pri, .btn.pri, .act.pri, #bar #btnEnd, .t-menu button.pri { box-shadow: 0 2px 1px -1px #5c140f73, 0 4px 9px -2px #1b1a1840, inset 0 0 0 2px #fbf3e433, inset 0 1px 0 #ffffff59; }
.cmd.off, .act.off, .btn:disabled, .btn.alt.off, .t-menu button:disabled { box-shadow: 0 1px 2px -1px #1b1a1826; }
.por, .porb, #mini, .th { border-radius: var(--rad-s); }
.chip, .hud-date, .row .nm em, .sh-title em, .advt, #talk .tk-who em, .stamp, .say, #toast, .todo > .n.sq, .act .rec, .gauge { border-radius: var(--rad-s); }
#talk { border-radius: var(--rad-a) !important; }
/* 판의 경계: 붓 한 획 */
#hud { border-bottom-color: transparent; } #sheet, #bar, .dlg { border-top-color: transparent; }
#hud::after, #sheet::before, #bar::before, .dlg::before { content: ''; position: absolute; left: -2px; right: -2px; height: 9px; background: var(--stroke-a) center / 100% 100% no-repeat; pointer-events: none; z-index: 2; }
#hud::after { bottom: -6px; } #sheet::before, #bar::before { top: -6px; } .dlg::before { top: -5px; background-image: var(--stroke-b); }
#bar::before { background-image: var(--stroke-b); transform: scaleX(-1); }
.dlg { position: relative; overflow: visible; } .dlg > .dlg-b { border-radius: 0; }
.dlg-h { border-bottom-color: transparent; position: relative; }
.dlg-h::after, .tabs::after { content: ''; position: absolute; left: 0; right: 0; bottom: -4px; height: 6px; background: var(--stroke-b) center / 100% 100% no-repeat; opacity: .82; pointer-events: none; }
.tabs { border-bottom-color: transparent; }
@media (min-width: 700px) { #bar::before { display: none; } #bar { border-top-color: var(--ink); } }

/* ── v0.20 아래 줄: 좁은 화면에서도 '턴 종료'가 잘리지 않게 ── */
#bar { gap: 5px; padding-left: max(8px, env(safe-area-inset-left, 0px)); padding-right: max(10px, env(safe-area-inset-right, 0px)); }
#bar button { flex: 0 1 auto; min-width: 0; padding: 0 clamp(8px, 2.8vw, 12px); font-size: clamp(13px, 3.7vw, 14.5px); overflow: visible; }
#bar #btnEnd { flex: 0 0 auto; font-size: clamp(14.5px, 4.1vw, 16px); padding: 0 clamp(11px, 3.6vw, 16px); }
#bar .sp { flex: 1 1 0; min-width: 0; }
#bar.t1 { gap: 4px; } #bar.t1 button { padding: 0 7px; font-size: 13px; letter-spacing: -.02em; } #bar.t1 #btnEnd { padding: 0 10px; font-size: 14.5px; letter-spacing: 0; }
#bar.t2 #btnNext .w { display: none; }
#bar.t3 button { padding: 0 5px; font-size: 12px; } #bar.t3 #btnEnd { padding: 0 8px; font-size: 13.5px; }
.wp { gap: 4px clamp(5px, 2.2vw, 10px); font-size: clamp(11.5px, 3.4vw, 13px); } .wp span { white-space: nowrap; flex: none; }

/* ── v0.20 아래에 더 있다는 표시: 글 대신 큰 화살표 ── */
.morehint i { bottom: 6px; width: 46px; height: 46px; padding: 0; border-radius: 50%; background: #1b1a18e0; color: var(--paper); font-size: 0; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 9px #1b1a1866, inset 0 0 0 2px #f4efe326; }
.morehint i::before { content: ''; width: 15px; height: 15px; border: solid var(--paper); border-width: 0 4px 4px 0; transform: translateY(-4px) rotate(45deg); border-radius: 1px; }
.morehint i::after { content: ''; position: absolute; left: 50%; top: 50%; width: 15px; height: 15px; margin: -1px 0 0 -9.5px; border: solid #f4efe38c; border-width: 0 4px 4px 0; transform: rotate(45deg); border-radius: 1px; }
.morehint::before { height: 66px; }
@keyframes mhbob { 0%, 100% { transform: translate(-50%, 0); } 50% { transform: translate(-50%, 6px); } }
"""
CSS = CSS.replace('STROKE_A', STROKE.replace('SEED', '7')).replace('STROKE_B', STROKE.replace('SEED', '23'))
s = rd('src/style.css')
assert 'v0.20 붓으로 두른 틀' not in s
s = s.rstrip('\n') + '\n' + CSS
wr('src/style.css', s)

s = rd('src/index.html')
s = rep(s, '<body>\n<div id="app">', """<body>
<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>
  <filter id="inkEdge" x="-8%" y="-16%" width="116%" height="132%" color-interpolation-filters="sRGB">
    <feTurbulence type="fractalNoise" baseFrequency="0.022 0.03" numOctaves="2" seed="4" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="2.6" xChannelSelector="R" yChannelSelector="G" result="d"/>
    <feTurbulence type="fractalNoise" baseFrequency="0.55 0.5" numOctaves="1" seed="9" result="g"/>
    <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.15 1.52" result="ga"/>
    <feComposite in="d" in2="ga" operator="in"/>
  </filter>
</defs></svg>
<div id="app">""")
s = rep(s, '<button id="btnNext" type="button">다음 부대<span class="n"></span></button>', '<button id="btnNext" type="button">다음<span class="w"> 부대</span><span class="n"></span></button>')
wr('src/index.html', s)
print('s3 css ok')
