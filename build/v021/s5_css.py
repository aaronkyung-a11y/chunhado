# v0.21 (5) 붓으로 그은 틀 · 초상
#   ⑦ "UI 박스가 펜슬로 그린거 같이 되었는데 좀 더 동양화같은 붓 느낌을 줄 수는 없을까?"
#      0.20 의 틀: 1.5 ~ 2.5px 의 가는 선을 필터(feDisplacementMap)로 흔든 것 — 굵기가 한결같고 가늘어 연필 선처럼 보였다.
#      → 네 변을 저마다 한 획으로 긋는다: 붓을 댄 자리는 굵고(起筆) 끝으로 갈수록 가늘어진다(收筆). 획마다 굵기가 다르고(아래 · 오른쪽이 더 굵다) 모서리에서 조금씩 엇갈린다.
#        그림(SVG)을 틀의 아홉 조각(border-image)으로 쓴다 — 모서리는 그대로, 변은 늘어난다. 먹빛 · 붉은빛(으뜸 단추) · 옅은 먹(쓸 수 없는 단추) 세 가지.
#      판의 경계(위 정보줄 아래 · 아래 창 위 · 창의 머리)의 긴 획도 더 굵고, 끝이 갈라지며 마른 붓 자국(飛白)이 난다.
#   ② "군주, 태수 사진이 출진메뉴를 누르면 비어있다. 출진 메뉴에서만 유독 비어있다."
#      시험 브라우저(393×852 · 배율 2 · 3)에서는 출진 탭에서도 초상이 그려진다 — 다시 나타나게 하지 못했다(원인을 확인하지 못함).
#      0.20 에서 새로 넣은 것 가운데 의심 가는 것을 걷어 낸다: (가) 틀마다 걸던 CSS 필터 filter: url(#inkEdge) — 이제 쓰지 않는다(index.html 의 필터도 지운다)
#      (나) 초상의 비뚤어진 둥근 모서리(--rad-s) — 0.19.1 처럼 2px 로.
import io, os, math, random, urllib.parse
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)

def stroke(p0, p1, t0, t1, rnd, split=True, n=22, wav=0.5, tp=0.8):
    (x0, y0), (x1, y1) = p0, p1; dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy); ux, uy = dx / L, dy / L; nx, ny = -uy, ux
    ph = rnd.uniform(0, 6)
    def thick(s): return (t1 + (t0 - t1) * (1 - s) ** tp + 0.22 * t0 * math.exp(-((s - 0.05) / 0.07) ** 2)) * (1 - 0.55 * max(0, s - 0.93) / 0.07 if not split else 1)
    def cen(s): w = math.sin(s * 7 + ph) * wav; return x0 + dx * s + nx * w, y0 + dy * s + ny * w
    be = 0.80 if split else 1.0; up, dn = [], []
    for i in range(n + 1):
        s = be * i / n; cx, cy = cen(s); h = thick(s) / 2
        if i == 0: h *= 0.55                                         # 붓을 댄 자리: 비스듬히
        a, b = h * (1 + rnd.uniform(-.09, .09)), h * (1 + rnd.uniform(-.09, .09))
        up.append((cx + nx * a - (ux * 2.2 if i == 0 else 0), cy + ny * a - (uy * 2.2 if i == 0 else 0))); dn.append((cx - nx * b, cy - ny * b))
    paths = ['M' + ' L'.join('%.1f %.1f' % p for p in up + dn[::-1]) + 'Z']
    if split:
        hb = thick(be) / 2
        for off in (-0.62, 0.05, 0.66)[:rnd.choice((2, 3, 3))]:
            s0 = be - 0.05; s1 = rnd.uniform(0.90, 1.05); wd = hb * rnd.uniform(0.30, 0.44)
            ax, ay = cen(s0); bx, by = cen(min(s1, 1.0)); bx += dx * max(0, s1 - 1); by += dy * max(0, s1 - 1)
            ax += nx * hb * off; ay += ny * hb * off; bx += nx * hb * off * 0.85; by += ny * hb * off * 0.85
            paths.append('M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f Z' % (ax + nx * wd, ay + ny * wd, bx + nx * wd * .25, by + ny * wd * .25, bx - nx * wd * .25, by - ny * wd * .25, ax - nx * wd, ay - ny * wd))
    return paths
def frame(color, seed, k=1.0, wash=0.07):
    rnd = random.Random(seed)
    # 위 · 오른쪽 · 아래 · 왼쪽: 붓을 댄 곳은 굵고 뗀 곳은 가늘다. 가운데 줄은 가장자리에서 6 안쪽(틀을 요소 밖으로 내밀지 않는다 — 밖으로 내밀면 단추의 scrollWidth 가 늘어 '넘침'으로 읽힌다)
    S = [((1.5, 6.2), (117.5, 5.2), 11 * k, 3.6 * k, 'h'), ((114.4, 1.5), (113.8, 117.5), 12 * k, 4.2 * k, 'v'), ((2, 113.6), (118, 112.8), 13.5 * k, 4.8 * k, 'h'), ((5.8, 2), (6.6, 117.5), 10.5 * k, 3.8 * k, 'v')]
    if seed % 2: S = [((2, 5.4), (118, 6.6), 10.5 * k, 3.8 * k, 'h'), ((113.6, 2), (114.6, 118), 12.5 * k, 4.0 * k, 'v'), ((1.5, 112.8), (117.5, 114.0), 13 * k, 5.0 * k, 'h'), ((6.8, 1.5), (5.6, 117.5), 11 * k, 3.6 * k, 'v')]
    d = ' '.join(p for s in S for p in stroke(s[0], s[1], s[2] * 1.22, s[3] * 0.92, rnd, False, 26, 0.5, 1.6))
    svg = ("<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 120 120'>"
           "<filter id='r' x='-6%' y='-6%' width='112%' height='112%'><feTurbulence type='fractalNoise' baseFrequency='0.085' numOctaves='2' seed='" + str(seed) + "' result='n'/>"
           "<feDisplacementMap in='SourceGraphic' in2='n' scale='3.2' xChannelSelector='R' yChannelSelector='G'/></filter>"
           "<filter id='w' x='-8%' y='-8%' width='116%' height='116%'><feGaussianBlur stdDeviation='2.0'/></filter>"
           "<path d='" + d + "' fill='" + color + "' fill-opacity='" + str(wash) + "' filter='url(#w)'/><path d='" + d + "' fill='" + color + "' filter='url(#r)'/></svg>")
    return 'url("data:image/svg+xml,' + urllib.parse.quote(svg, safe="/:=' ") + '")'
def line(color, seed, t0=9.5, t1=3.2):
    rnd = random.Random(seed)
    d = ' '.join(stroke((4, 8.2), (594, 7.6), t0, t1, rnd, True, 60, 0.9))
    svg = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 600 16' preserveAspectRatio='none'><filter id='r' x='-2%' y='-80%' width='104%' height='260%'><feTurbulence type='fractalNoise' baseFrequency='0.02 0.4' numOctaves='2' seed='" + str(seed) + "' result='n'/>"
           "<feDisplacementMap in='SourceGraphic' in2='n' scale='4' xChannelSelector='R' yChannelSelector='G' result='d'/><feTurbulence type='fractalNoise' baseFrequency='0.05 0.9' numOctaves='1' seed='" + str(seed + 5) + "' result='g'/>"
           "<feColorMatrix in='g' type='matrix' values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -1.7 1.78' result='ga'/><feComposite in='d' in2='ga' operator='in'/></filter>"
           "<path d='" + d + "' fill='" + color + "' filter='url(#r)'/></svg>")
    return 'url("data:image/svg+xml,' + urllib.parse.quote(svg, safe="/:=' ") + '")'

s = rd('src/style.css')
# 0.20 의 변수 줄(--rad-* · --stroke-*)을 통째로 바꾼다
i = s.index(":root { --rad-a: 10px 6px 11px 5px"); j = s.index(".cmd, .btn, .act, #bar button, .t-menu button, .opt, .pl-ctl button, .hm-links button, .du-mv, .x.fold, .seg { position: relative;")
s = s[:i] + (":root { --rad-a: 3px 2px 4px 2px; --rad-b: 2px 4px 2px 3px; --rad-s: 5px 3px 6px 3px / 3px 6px 3px 5px;\n"
  "  --bf-a: " + frame('#1b1a18', 4) + ";\n  --bf-b: " + frame('#1b1a18', 7) + ";\n  --bf-r: " + frame('#7c1a14', 4) + ";\n  --bf-s: " + frame('#b5332a', 7) + ";\n  --bf-f: " + frame('#1b1a18', 4, 0.72, 0.03).replace("fill='%231b1a18' filter", "fill='%231b1a18' fill-opacity='0.5' filter") + ";\n"
  "  --stroke-a: " + line('#1b1a18', 3) + ";\n  --stroke-b: " + line('#1b1a18', 8) + "; }\n") + s[j:]
s = rep(s, "  content: ''; position: absolute; inset: 0; border: solid #1b1a18e8; border-width: 1.5px 1.9px 2.5px 1.6px; border-radius: inherit; filter: url(#inkEdge); pointer-events: none; }",
           "  content: ''; position: absolute; inset: 0; border: 9px solid transparent; border-image: var(--bf-a) 30 / 9px stretch; pointer-events: none; }\n"
           ".cmd:nth-child(even)::after, .act:nth-child(even)::after, .opt:nth-child(even)::after, #bar button:nth-child(even)::after, .t-menu button:nth-child(even)::after, .btn:nth-of-type(even)::after { border-image-source: var(--bf-b); }\n"
           ".btn::after, #bar button::after, .pl-ctl button::after, .hm-links button::after, .x.fold::after, .seg::after, .opt::after { border-width: 7px; border-image-width: 7px; }")
s = rep(s, ".opt::after { border-color: #1b1a1899; border-width: 1.2px 1.5px 1.9px 1.3px; }", ".opt::after { border-image-source: var(--bf-f); }")
s = rep(s, ".opt.on::after { border-color: var(--seal); border-width: 2px 2.4px 3px 2.1px; }", ".opt.on::after { border-image-source: var(--bf-s); border-width: 9px; border-image-width: 9px; }")
s = rep(s, ".cmd.pri::after, .btn.pri::after, .act.pri::after, #bar #btnEnd::after, .t-menu button.pri::after { border-color: var(--seal-2); }",
           ".cmd.pri::after, .btn.pri::after, .act.pri::after, #bar #btnEnd::after, .t-menu button.pri::after { border-image-source: var(--bf-r); }\n#bar #btnEnd::after { border-width: 9px; border-image-width: 9px; }")
s = rep(s, ".btn.auto::after { border-color: #000000d9; }", ".btn.auto::after { border-image-source: var(--bf-a); }")
s = rep(s, ".cmd.off::after, .act.off::after, .btn:disabled::after, .btn.alt.off::after, .t-menu button:disabled::after { border-color: #1b1a1866; border-width: 1.2px 1.4px 1.7px 1.2px; }",
           ".cmd.off::after, .act.off::after, .btn:disabled::after, .btn.alt.off::after, .btn.pri.off::after, .t-menu button:disabled::after { border-image-source: var(--bf-f); }")
s = rep(s, ".por, .porb, #mini, .th { border-radius: var(--rad-s); }", ".porb, #mini, .th { border-radius: var(--rad-s); }")
# 판의 경계: 더 굵은 획
s = rep(s, "#hud::after, #sheet::before, #bar::before, .dlg::before { content: ''; position: absolute; left: -2px; right: -2px; height: 9px;", "#hud::after, #sheet::before, #bar::before, .dlg::before { content: ''; position: absolute; left: -2px; right: -2px; height: 13px;")
s = rep(s, "#hud::after { bottom: -6px; } #sheet::before, #bar::before { top: -6px; } .dlg::before { top: -5px; background-image: var(--stroke-b); }", "#hud::after { bottom: -8px; } #sheet::before, #bar::before { top: -8px; } .dlg::before { top: -7px; background-image: var(--stroke-b); }")
s = rep(s, ".dlg-h::after, .tabs::after { content: ''; position: absolute; left: 0; right: 0; bottom: -4px; height: 6px;", ".dlg-h::after, .tabs::after { content: ''; position: absolute; left: 0; right: 0; bottom: -5px; height: 8px;")
s = s.rstrip('\n') + """
/* v0.21 군사의 말 칸도 붓으로 */
.hm-advp .hm-say { position: relative; border-color: transparent; border-radius: var(--rad-a); }
.hm-advp .hm-say::after { content: ''; position: absolute; inset: 0; border: 7px solid transparent; border-image: var(--bf-b) 30 / 7px stretch; pointer-events: none; }
.hm-advp .hm-say:disabled::after { border-image-source: var(--bf-f); }
"""
wr('src/style.css', s)

s = rd('src/index.html')
i = s.index('<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>'); j = s.index('</defs></svg>') + len('</defs></svg>')
assert 'inkEdge' in s[i:j] and s.count('inkEdge') == 1
s = s[:i].rstrip('\n') + '\n' + s[j:].lstrip('\n')
wr('src/index.html', s)
assert 'inkEdge' not in rd('src/style.css')
print('s5 ok')
