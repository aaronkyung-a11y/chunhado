# v0.22 (6) 화면 손질 — 요청 1 · 8
#   ① "버튼 색과 배경색이 달라서 네모 선 바깥으로 삐져나온 흰색 네모칸이 보이는 게 좀 별로다. 완성도가 낮아보여. 그 바깥쪽은 누끼처리를 하든가해야할 듯?"
#      0.21 의 단추: 밝은 종이빛 바탕(네모) + 그 위에 붓으로 그은 틀(::after 의 border-image). 붓 획은 굵기가 변하고 모서리에서 엇갈리므로,
#      획이 가는 곳과 모서리에서는 네모난 바탕이 획 바깥으로 0.5 ~ 1.5px 드러났고, 바탕 밖으로 그림자도 졌다 — 틀 바깥에 흰 네모가 보였다.
#      → 단추를 틀의 생김새대로 오려 낸다(누끼): 붓 획과 그 안쪽만 남기고 바깥은 비운다.
#        틀과 같은 획(같은 씨앗 · 같은 흔들림)에 안쪽을 채운 그림을 '가림 그림'으로 쓴다(-webkit-mask-box-image / mask-border — 틀과 똑같이 아홉 조각).
#        바탕 · 눌린 빛깔 · 붉은 단추 같은 상태의 꾸밈은 그대로 두고 바깥만 잘린다. 틀 밖으로 지던 그림자는 없앤다(오려 낸 바깥에는 그릴 수 없다).
#        틀(::after)과 가림 그림이 같은 자리에 놓이도록 이 단추들의 테두리 두께(투명 1px)를 0 으로 한다.
#      가림 그림을 모르는 브라우저(파이어폭스)에서는 0.21 과 같게 보인다.
#   ⑧ "수송대를 보니까 정보가 잘린다. 노 까지만 보이고 군마는 안 보임. 그리고 도시 정보도 충차 숫자는 안 보임"
#      무기 줄(.wp)은 한 줄에 넘치는 것을 잘라 냈다(nowrap + overflow: hidden). 숫자가 다섯 자리를 넘으면 뒤쪽이 사라졌다.
#      → 넘치면 다음 줄로 내린다. 이름과 숫자 사이도 조금 띄운다('창10,807' → '창 10,807').
import io, os, math, random, urllib.parse
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)

# ---- 0.21 의 틀 그림과 똑같은 획을 다시 만든다(build/v021/s5_css.py 의 stroke · frame 과 같은 셈 — 같은 씨앗이면 같은 획) ----
def stroke(p0, p1, t0, t1, rnd, split=True, n=22, wav=0.5, tp=0.8):
    (x0, y0), (x1, y1) = p0, p1; dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy); ux, uy = dx / L, dy / L; nx, ny = -uy, ux
    ph = rnd.uniform(0, 6)
    def thick(s): return (t1 + (t0 - t1) * (1 - s) ** tp + 0.22 * t0 * math.exp(-((s - 0.05) / 0.07) ** 2)) * (1 - 0.55 * max(0, s - 0.93) / 0.07 if not split else 1)
    def cen(s): w = math.sin(s * 7 + ph) * wav; return x0 + dx * s + nx * w, y0 + dy * s + ny * w
    be = 0.80 if split else 1.0; up, dn = [], []
    for i in range(n + 1):
        s = be * i / n; cx, cy = cen(s); h = thick(s) / 2
        if i == 0: h *= 0.55
        a, b = h * (1 + rnd.uniform(-.09, .09)), h * (1 + rnd.uniform(-.09, .09))
        up.append((cx + nx * a - (ux * 2.2 if i == 0 else 0), cy + ny * a - (uy * 2.2 if i == 0 else 0))); dn.append((cx - nx * b, cy - ny * b))
    return ['M' + ' L'.join('%.1f %.1f' % p for p in up + dn[::-1]) + 'Z']
def strokes(seed, k=1.0):
    rnd = random.Random(seed)
    S = [((1.5, 6.2), (117.5, 5.2), 11 * k, 3.6 * k, 'h'), ((114.4, 1.5), (113.8, 117.5), 12 * k, 4.2 * k, 'v'), ((2, 113.6), (118, 112.8), 13.5 * k, 4.8 * k, 'h'), ((5.8, 2), (6.6, 117.5), 10.5 * k, 3.8 * k, 'v')]
    if seed % 2: S = [((2, 5.4), (118, 6.6), 10.5 * k, 3.8 * k, 'h'), ((113.6, 2), (114.6, 118), 12.5 * k, 4.0 * k, 'v'), ((1.5, 112.8), (117.5, 114.0), 13 * k, 5.0 * k, 'h'), ((6.8, 1.5), (5.6, 117.5), 11 * k, 3.6 * k, 'v')]
    d = ' '.join(p for s in S for p in stroke(s[0], s[1], s[2] * 1.22, s[3] * 0.92, rnd, False, 26, 0.5, 1.6))
    return S, d
def cross(a, b):                                             # 두 곧은 줄(획의 가운데 줄)이 만나는 점
    (x1, y1), (x2, y2) = a; (x3, y3), (x4, y4) = b
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / den
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / den
    return px, py
def mask(seed, k=1.0):
    """틀과 같은 획 + 획의 가운데 줄로 둘러싼 안쪽. 같은 흔들림 필터를 둘 다에 건다 — 틀 그림과 한 점도 어긋나지 않는다."""
    S, d = strokes(seed, k)
    T, R, B, L = [(s[0], s[1]) for s in S]
    face = 'M' + ' L'.join('%.1f %.1f' % p for p in (cross(T, L), cross(T, R), cross(B, R), cross(B, L))) + 'Z'
    svg = ("<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 120 120'>"
           "<filter id='r' x='-6%' y='-6%' width='112%' height='112%'><feTurbulence type='fractalNoise' baseFrequency='0.085' numOctaves='2' seed='" + str(seed) + "' result='n'/>"
           "<feDisplacementMap in='SourceGraphic' in2='n' scale='3.2' xChannelSelector='R' yChannelSelector='G'/></filter>"
           "<g filter='url(#r)'><path d='" + face + "' fill='#000'/><path d='" + d + "' fill='#000' stroke='#000' stroke-width='0.5' stroke-linejoin='round'/></g></svg>")
    return 'url("data:image/svg+xml,' + urllib.parse.quote(svg, safe="/:=' ") + '")', d

s = rd('src/style.css')
ma, da = mask(4); mb, db = mask(7); mf, df = mask(4, 0.72)
# 틀 그림 안의 획과 같은지 확인한다(어긋나면 누끼가 틀과 맞지 않는다)
for nm, d in (('--bf-a', da), ('--bf-b', db), ('--bf-f', df)):
    i = s.index('  ' + nm + ': url('); j = s.index('\n', i); line = urllib.parse.unquote(s[i:j])
    assert d in line, ('stroke mismatch', nm)

FR = ".cmd, .btn, .act, #bar button, .t-menu button, .opt, .pl-ctl button, .hm-links button, .du-mv, .x.fold, .seg"
def m(sel, src=None, w=None):
    out = []
    if src: out.append('-webkit-mask-box-image-source: var(' + src + '); mask-border-source: var(' + src + ');')
    if w: out.append('-webkit-mask-box-image-width: ' + w + '; mask-border-width: ' + w + ';')
    return sel + ' { ' + ' '.join(out) + ' }\n'
css = """
/* ── v0.22 단추를 틀의 생김새대로 오려 낸다(누끼) — 붓 획과 그 안쪽만 남기고 바깥은 비운다 ──
   가림 그림(--bm-*)은 틀 그림(--bf-*)과 같은 획에 안쪽을 채운 것이다. 틀과 똑같이 아홉 조각으로 놓인다(모서리는 그대로, 변은 늘어난다).
   틀(::after — 안쪽 여백 상자에 놓인다)과 가림 그림(테두리 상자에 놓인다)이 같은 자리에 오도록 테두리 두께를 0 으로 한다. 틀 밖의 그림자는 없앤다. */
:root {
  --bm-a: """ + ma + """;
  --bm-b: """ + mb + """;
  --bm-f: """ + mf + """; }
@supports ((-webkit-mask-box-image-source: none) or (mask-border-source: none)) {
""" + FR + """, .hm-advp .hm-say { border-width: 0;
  -webkit-mask-box-image: var(--bm-a) 30 fill / 9px stretch; mask-border: var(--bm-a) 30 fill / 9px stretch; }
"""
css += m(".cmd:nth-child(even), .act:nth-child(even), .opt:nth-child(even), #bar button:nth-child(even), .t-menu button:nth-child(even), .btn:nth-of-type(even)", '--bm-b')
css += m(".btn, #bar button, .pl-ctl button, .hm-links button, .x.fold, .seg, .opt", None, '7px')
css += m(".opt, .opt:nth-child(even)", '--bm-f')
css += m(".opt.on, .opt.on:nth-child(even)", '--bm-b', '9px')
css += m(".cmd.pri, .btn.pri, .act.pri, #bar #btnEnd, .t-menu button.pri", '--bm-a')
css += m("#bar #btnEnd", None, '9px')
css += m(".btn.auto", '--bm-a')
css += m(".cmd.off, .act.off, .btn:disabled, .btn.alt.off, .btn.pri.off, .t-menu button:disabled", '--bm-f')
css += m(".hm-advp .hm-say", '--bm-b', '7px')
css += m(".hm-advp .hm-say:disabled", '--bm-f')
css += """.cmd, .btn, .act, #bar button, .t-menu button, .du-mv, .x.fold { box-shadow: inset 0 1px 0 #ffffffa6; }
.cmd.pri, .btn.pri, .act.pri, #bar #btnEnd, .t-menu button.pri { box-shadow: inset 0 0 0 2px #fbf3e433, inset 0 1px 0 #ffffff59; }
.btn.auto { box-shadow: inset 0 1px 0 #ffffff47; }
.cmd.off, .act.off, .btn:disabled, .btn.alt.off, .t-menu button:disabled { box-shadow: none; }
.cmd:active, .btn:active, .act:active, #bar button:active, .t-menu button:active, .du-mv:active, .x.fold:active { box-shadow: inset 0 2px 3px #00000040; }
.cmd.pri:active, .btn.pri:active, .act.pri:active, #bar #btnEnd:active, .t-menu button.pri:active { box-shadow: inset 0 2px 4px #00000059; }
}
/* ── v0.22 무기 줄 · 실은 물자 줄: 넘치면 다음 줄로(전에는 잘렸다 — 군마 · 충차가 보이지 않았다) ── */
.wp { flex-wrap: wrap; overflow: visible; row-gap: 3px; }
.wp span { gap: 3px; }
/* ── v0.22 출진: 적성 순 표시 · 수송: 병량이 없다는 말 ── */
.sec small .aptby { color: var(--seal); font-weight: 700; }
.note.lack { margin: 2px 0 8px; }
.note .btn.auto { height: 30px; padding: 0 10px; margin: 4px 0 0 2px; font: 800 12.5px var(--font-body); vertical-align: middle; }
/* ── v0.22 고르지 않은 칸의 틀은 모두 옅게(0.21 에서는 짝수째 칸만 짙었다 — 짝수 규칙이 더 셌다) ── */
.opt:nth-child(even)::after { border-image-source: var(--bf-f); }
.opt.on:nth-child(even)::after { border-image-source: var(--bf-s); }
"""
s = s.rstrip('\n') + '\n' + css
wr('src/style.css', s)
print('s6 ok', len(ma), len(mb), len(mf))
