# v0.22.1 — 네 가지(요청 11-25 11:17 의 1 ~ 4번)
#   1) 순찰의 소리: 싸움용 발구름(stomp — 0.2초짜리 굵은 소리 뭉치, 음높이 ±8% 흔들림) 대신 딱따기 두 번(clack — tools/make_audio_v0221.py). 음높이를 흔들지 않는다.
#   2) 성 창의 탭(내정 · 출진 · 인재 · 건설 · 군단): 고른 탭 아래의 곧은 붉은 줄을 붓으로 그은 붉은 획으로.
#   3) 출진: 부대가 나갈 칸에 먼저 서 있다가 성에서 다시 걸어 나오던 것.
#        · 지난 열흘을 보여 줄 때(다른 세력 · 내 군단의 출진): 장면들을 묶어 보여 주기 전에 새 부대를 만들어 나갈 칸에 세워 두었다 —
#          앞의 장면들이 나오는 동안, 그리고 출진 장면의 화면이 옮겨 가는 동안 부대가 이미 서 있었다. 이제 출진 장면이 시작될 때까지 보이지 않는다.
#        · 내 출진: 연출의 첫 모습(성 안 · 작고 옅게)을 연출을 거는 그 자리에서 바로 입힌다(한 장이라도 나갈 칸에 선 모습이 그려지지 않게).
#        · 두 연출을 같게: 성에서 작고 옅게 나와 제 크기 · 제 빛으로.
#   4) 판 번호
import io, os, math, random, urllib.parse
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)

# ---------- 판 번호 ----------
s = rd('src/data.js')
s = rep(s, "var GAME_VERSION = 'v0.22';", "var GAME_VERSION = 'v0.22.1';")
wr('src/data.js', s)

# ---------- 1) 순찰의 소리 ----------
s = rd('src/ui3d.js')
s = rep(s, "  hammer:   { s: [['hammer', 0.8, 0.03]], gap: 300, syn: 'drum' },\n",
        "  hammer:   { s: [['hammer', 0.8, 0.03]], gap: 300, syn: 'drum' },\n"
        "  patrol:   { s: [['clack', 0.8, 0]], gap: 500, syn: 'ui' },                                     // v0.22.1: 순찰 — 딱따기 두 번. 음높이를 흔들지 않는다(전에는 싸움용 발구름 step 을 썼다 — 혼자 나면 깨진 소리처럼 들렸다)\n")
s = rep(s, "    o.g.visible = o.ring.visible = (u.id !== UI.hide) || o.anim;\n",
        "    o.g.visible = o.ring.visible = !o.wait && ((u.id !== UI.hide) || o.anim);      // v0.22.1: 출진 장면을 기다리는 부대(o.wait)는 보이지 않는다\n")
wr('src/ui3d.js', s)

s = rd('src/ui_panels.js')
s = rep(s, "function (os) { var r = cmdPatrol(b, ids(os)); return done(r, r.ok ? '치안 +' + r.n : '', 'step', os[0], 'patrol'); });",
        "function (os) { var r = cmdPatrol(b, ids(os)); return done(r, r.ok ? '치안 +' + r.n : '', 'patrol', os[0], 'patrol'); });")

# ---------- 3) 출진의 순서 ----------
s = rep(s, "    if (od && !od.held) { od.anim = true; od.held = true; fxPut(od, hexPos(evs[i].c, evs[i].r)); }\n",
        "    if (od && !od.held) { od.anim = true; od.held = true; fxPut(od, hexPos(evs[i].c, evs[i].r)); od.wait = true; od.g.visible = od.ring.visible = false; }      // v0.22.1: 출진 장면이 나올 때까지는 보이지 않는다(나갈 칸에 먼저 서 있지 않게)\n")
s = rep(s, "        anim(420, function (t) { var w = 1 - (1 - t) * (1 - t), px = q0[0] + (q1[0] - q0[0]) * w, pz = q0[2] + (q1[2] - q0[2]) * w; fxPut(odp, [px, groundY(px, pz) + Math.sin(Math.PI * t) * 0.16, pz]); });\n",
        "        var dstep = function (t) {                               // v0.22.1: 성 안에서 작고 옅게 나와 제 크기 · 제 빛으로(내 출진의 연출 fxDeploy 와 같게)\n"
        "          var w = 1 - (1 - t) * (1 - t), px = q0[0] + (q1[0] - q0[0]) * w, pz = q0[2] + (q1[2] - q0[2]) * w, sc = 0.55 + 0.45 * w;\n"
        "          fxPut(odp, [px, groundY(px, pz) + Math.sin(Math.PI * t) * 0.16, pz]);\n"
        "          if (odp.sp && odp.sp.userData.w) { odp.sp.scale.set(odp.sp.userData.w * sc, odp.sp.userData.h * sc, 1); odp.sp.material.opacity = Math.min(1, 0.2 + t * 1.6); }\n"
        "        };\n"
        "        dstep(0); odp.wait = false; odp.g.visible = odp.ring.visible = true;      // 이제 보인다 — 성 안에서부터\n"
        "        anim(420, dstep);\n")
s = rep(s, "function clearAnimFlags() { if (!R3) return; for (var id in R3.units) { var o = R3.units[id]; o.held = false; o.keep = false; if (o.anim) { o.anim = false; o.c = -1; o.sig = ''; } } holdsFree(); }",
        "function clearAnimFlags() { if (!R3) return; for (var id in R3.units) { var o = R3.units[id]; o.held = false; o.keep = false; if (o.wait) { o.wait = false; o.g.visible = o.ring.visible = true; } if (o.anim) { o.anim = false; o.c = -1; o.sig = ''; } } holdsFree(); }")
wr('src/ui_panels.js', s)

s = rd('src/fx.js')
s = rep(s, "  o.anim = true; fxFace(o, p0, p1);\n  anim(430, function (t) {\n    var e = easeOut(t), p = fxLerp(p0, p1, e), s = 0.55 + 0.45 * e;\n    fxPut(o, [p[0], p[1] + Math.sin(Math.PI * t) * 0.18, p[2]]);\n    o.sp.scale.set(o.sp.userData.w * s, o.sp.userData.h * s, 1); o.sp.material.opacity = Math.min(1, 0.2 + t * 1.6);\n  }, function () {",
        "  o.anim = true; fxFace(o, p0, p1);\n  var step = function (t) {\n    var e = easeOut(t), p = fxLerp(p0, p1, e), s = 0.55 + 0.45 * e;\n    fxPut(o, [p[0], p[1] + Math.sin(Math.PI * t) * 0.18, p[2]]);\n    o.sp.scale.set(o.sp.userData.w * s, o.sp.userData.h * s, 1); o.sp.material.opacity = Math.min(1, 0.2 + t * 1.6);\n  };\n"
        "  step(0);                                                    // v0.22.1: 첫 모습(성 안 · 작고 옅게)을 바로 입힌다 — 나갈 칸에 선 모습이 한 장이라도 먼저 그려지지 않게\n"
        "  anim(430, step, function () {")
wr('src/fx.js', s)

# ---------- 2) 탭 아래의 붉은 붓 획 ----------
def stroke(p0, p1, t0, t1, rnd, split=True, n=22, wav=0.5, tp=0.8):          # build/v021/s5_css.py 의 획과 같은 셈
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
    paths = ['M' + ' L'.join('%.1f %.1f' % p for p in up + dn[::-1]) + 'Z']
    if split:
        hb = thick(be) / 2
        for off in (-0.62, 0.05, 0.66)[:rnd.choice((2, 3, 3))]:
            s0 = be - 0.05; s1 = rnd.uniform(0.90, 1.05); wd = hb * rnd.uniform(0.30, 0.44)
            ax, ay = cen(s0); bx, by = cen(min(s1, 1.0)); bx += dx * max(0, s1 - 1); by += dy * max(0, s1 - 1)
            ax += nx * hb * off; ay += ny * hb * off; bx += nx * hb * off * 0.85; by += ny * hb * off * 0.85
            paths.append('M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f Z' % (ax + nx * wd, ay + ny * wd, bx + nx * wd * .25, by + ny * wd * .25, bx - nx * wd * .25, by - ny * wd * .25, ax - nx * wd, ay - ny * wd))
    return paths
def dab(color, seed):
    """짧은 붓 획(탭 하나의 폭): 왼쪽에 붓을 대고 오른쪽으로 가늘어지며 갈라진다. 폭 160 · 높이 16"""
    rnd = random.Random(seed)
    d = ' '.join(stroke((5, 8.6), (155, 7.2), 10.5, 5.6, rnd, True, 26, 0.7))
    svg = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 160 16' preserveAspectRatio='none'><filter id='r' x='-4%' y='-80%' width='108%' height='260%'><feTurbulence type='fractalNoise' baseFrequency='0.06 0.4' numOctaves='2' seed='" + str(seed) + "' result='n'/>"
           "<feDisplacementMap in='SourceGraphic' in2='n' scale='3.2' xChannelSelector='R' yChannelSelector='G' result='d'/><feTurbulence type='fractalNoise' baseFrequency='0.12 0.9' numOctaves='1' seed='" + str(seed + 5) + "' result='g'/>"
           "<feColorMatrix in='g' type='matrix' values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -1.7 1.78' result='ga'/><feComposite in='d' in2='ga' operator='in'/></filter>"
           "<path d='" + d + "' fill='" + color + "' filter='url(#r)'/></svg>")
    return 'url("data:image/svg+xml,' + urllib.parse.quote(svg, safe="/:=' ") + '")'
s = rd('src/style.css')
assert '--stroke-t' not in s
s += ("\n/* ── v0.22.1 성 창의 탭: 고른 탭 아래의 줄을 붓으로 그은 붉은 획으로(전에는 곧은 줄 3px 이었다) ── */\n"
      ":root { --stroke-t: " + dab('#b5332a', 11) + "; }\n"
      ".tabs button { position: relative; }\n"
      ".tabs button.on { border-bottom-color: transparent; }\n"
      ".tabs button.on::after { content: ''; position: absolute; left: 6%; right: 6%; bottom: -6px; height: 12px; background: var(--stroke-t) center / 100% 100% no-repeat; pointer-events: none; z-index: 1; }\n")
wr('src/style.css', s)
print('v0.22.1 s1 ok')
