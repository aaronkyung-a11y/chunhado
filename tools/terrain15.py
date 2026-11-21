#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.15 지형 손질: (1) 산을 넓힌다 — 산에 붙은 가파른 기슭을 못 가는 산으로  (2) 칸마다 높이 단계를 적는다.
   ("지형과 산에 따른 영향이 필요. 산은 갈 수 없는 곳은 hex 표시없게")

 (1) steep: 지금의 높이맵(map3d.js)에서 칸마다 험한 정도(가운데와 여섯 모서리 쪽 일곱 점의 높이 차)를 재서,
     험함이 RUG 이상인 구릉·평지·숲·황무지 칸 가운데 '산에 붙은 것'(두 겹까지)을 산(m)으로 바꾼다.
     바꾸지 않는 칸: 길과 길 옆 · 거점에서 3칸 안 · 부지와 그 옆.
     지키는 것: 이웃한 거점 사이의 걸음(보병 이동 비용)이 5% 넘게 늘지 않는다 · 갈 수 있던 땅이 섬처럼 끊기지 않는다.
     어긋나면 그 길 위 · 그 둘레의 바꾼 칸을 되돌리고 다시 본다.
 (2) elev: 높이맵에서 칸의 높이를 0.1 단위로 끊어 단계(0~35)로 적는다 → MAPDATA.e (36진수 한 글자씩).

usage:  terrain15.py steep <map3d.js> <mapdata.js> [mapdata.json …]     칸을 바꾼다(그 뒤에 tools/bake3d_ink.py 로 그림을 다시 굽는다)
        terrain15.py elev  <map3d.js> <mapdata.js> [mapdata.json …]     높이 단계를 적는다(다시 구운 높이맵으로)
        --dry 를 붙이면 파일을 고치지 않고 셈만 보인다.
 두 번 돌려도 같다: steep 는 MAPDATA.t0(바꾸기 전의 지형)이 있으면 그것에서 다시 시작한다."""
import sys, json, re, math, base64, heapq, collections
import numpy as np
RUG = 0.28; RINGS = 2; KEEP_BASE = 3; SLACK = 1.05; STEP = 0.10
args = [a for a in sys.argv[1:] if not a.startswith('--')]; DRY = '--dry' in sys.argv
mode, M3, SRC = args[0], args[1], args[2]; MORE = args[3:]
s = open(SRC, encoding='utf8').read()
m = re.match(r'^(var MAPDATA\s*=\s*)(.*?)(;\s*)$', s, re.S); D = json.loads(m.group(2))
W, H, RD, bases = D['W'], D['H'], D['road'], D['bases']
T0 = D.get('t0', D['t'])
SQ3 = math.sqrt(3)
def K(c, r): return r * W + c
def nbrs(c, r):
    d = [(1, 0), (-1, 0), (1, -1), (0, -1), (1, 1), (0, 1)] if r & 1 else [(1, 0), (-1, 0), (0, -1), (-1, -1), (0, 1), (-1, 1)]
    return [(c + a, r + b) for a, b in d if 0 <= c + a < W and 0 <= r + b < H]
def cube(c, r): x = c - ((r - (r & 1)) >> 1); return x, -x - r, r
def dist(a, b):
    ax, ay, az = cube(*a); bx, by, bz = cube(*b); return max(abs(ax - bx), abs(ay - by), abs(az - bz))
def center(c, r): return (SQ3 * (c + 0.5 * (r & 1)) + SQ3 * 0.5, 1.5 * r + 1.0)
# ---------- 높이맵 ----------
m3 = open(M3, encoding='utf8').read(); J = json.loads(m3[m3.index('{'):m3.rindex('}') + 1])
GX, GZ, WX, WZ = J['GX'], J['GZ'], J['WX'], J['WZ']
HM = (J['hmin'] + np.frombuffer(base64.b64decode(J['hm']), dtype='<u2').astype(np.float64) * (J['hmax'] - J['hmin']) / 65535).reshape(GZ, GX)
def gy(x, z):
    gx = min(max(x / WX * (GX - 1), 0), GX - 1.001); gz = min(max(z / WZ * (GZ - 1), 0), GZ - 1.001)
    ix, iz = int(gx), int(gz); fx, fz = gx - ix, gz - iz
    return (HM[iz, ix] * (1 - fx) + HM[iz, ix + 1] * fx) * (1 - fz) + (HM[iz + 1, ix] * (1 - fx) + HM[iz + 1, ix + 1] * fx) * fz
def hexstat(c, r):
    x, z = center(c, r); pts = [gy(x, z)] + [gy(x + 0.8 * math.cos(k * math.pi / 3 + math.pi / 6), z + 0.8 * math.sin(k * math.pi / 3 + math.pi / 6)) for k in range(6)]
    return sum(pts) / 7.0, max(pts) - min(pts)
CONV = None
def write(D):
    if DRY: print('(dry) 파일은 그대로'); return
    open(SRC, 'w', encoding='utf8').write(m.group(1) + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + m.group(3))
    for p in MORE:
        j = json.load(open(p, encoding='utf8'))
        for k in ('t', 't0', 'e'):
            if k in D: j[k] = D[k]
        if 'traw' in j and CONV is not None:                 # 그림을 굽는 쪽(bake3d_ink.py)은 traw 를 본다 — 바꾼 칸을 거기에도 산으로
            j.setdefault('traw0', j['traw']); tr = list(j['traw0'])
            for c, r in CONV: tr[K(c, r)] = 'm'
            j['traw'] = ''.join(tr)
        json.dump(j, open(p, 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
    print('고친 파일:', SRC, *MORE)

if mode == 'elev':
    B36 = '0123456789abcdefghijklmnopqrstuvwxyz'; e = []; cnt = collections.Counter()
    for r in range(H):
        for c in range(W):
            lv = int(min(35, max(0, round(hexstat(c, r)[0] / STEP)))); e.append(B36[lv])
            if D['t'][K(c, r)] in 'pfhdw': cnt[lv] += 1
    D['e'] = ''.join(e)
    tot = sum(cnt.values()); acc = 0; q = {}
    for lv in sorted(cnt):
        acc += cnt[lv]
        for p in (50, 90, 99):
            if p not in q and acc >= tot * p / 100: q[p] = lv
    print('갈 수 있는 칸 %d: 높이 단계 가운데 %d · 90%% %d · 99%% %d · 가장 높은 %d' % (tot, q[50], q[90], q[99], max(cnt)))
    diff = collections.Counter()
    for r in range(H):
        for c in range(W):
            if D['t'][K(c, r)] not in 'pfhdw': continue
            a = B36.index(D['e'][K(c, r)])
            for cc, rr in nbrs(c, r):
                if D['t'][K(cc, rr)] in 'pfhdw': diff[min(4, abs(a - B36.index(D['e'][K(cc, rr)])))] += 1
    tt = sum(diff.values()); print('이웃한 두 칸의 높이 차(%):', {k: round(100.0 * v / tt, 1) for k, v in sorted(diff.items())})
    write(D); sys.exit(0)

assert mode == 'steep', mode
PASS = set('pfhdw')
road = {(c, r) for r in range(H) for c in range(W) if RD[K(c, r)] == '1'}
keep = set(road)
for c, r in road: keep.update(nbrs(c, r))
for b in bases:
    for r in range(max(0, b['r'] - KEEP_BASE - 1), min(H, b['r'] + KEEP_BASE + 2)):
        for c in range(max(0, b['c'] - KEEP_BASE - 1), min(W, b['c'] + KEEP_BASE + 2)):
            if dist((c, r), (b['c'], b['r'])) <= KEEP_BASE: keep.add((c, r))
for name, ps in D['plots'].items():
    for c, r in ps: keep.add((c, r)); keep.update(nbrs(c, r))
RGm = {}
def rug(c, r):
    if (c, r) not in RGm: RGm[(c, r)] = hexstat(c, r)[1]
    return RGm[(c, r)]
# 산에 붙은 가파른 칸을 두 겹까지
T = list(T0); conv = set(); front = {(c, r) for r in range(H) for c in range(W) if T0[K(c, r)] == 'm'}
for ring in range(RINGS):
    new = set()
    for c, r in front:
        for cc, rr in nbrs(c, r):
            if (cc, rr) in conv or (cc, rr) in keep or T0[K(cc, rr)] not in 'hpfd': continue
            if rug(cc, rr) >= RUG: new.add((cc, rr))
    conv |= new; front = new
print('바꿀 만한 칸', len(conv), dict(collections.Counter(T0[K(c, r)] for c, r in conv)))
MOVE = {'p': 3, 'f': 5, 'h': 5, 'd': 4}
def cost(c, r, blocked):
    t = T0[K(c, r)]
    if t in 'msx' or (c, r) in blocked: return None
    if t == 'w': return 4 if (c, r) in road else 8
    return 2 if (c, r) in road else MOVE[t]
def path(a, b, blocked):
    """보병의 가장 싼 길: (비용, 지나는 칸들)"""
    best = {a: 0}; prev = {}; pq = [(0, a)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == b: break
        if d > best.get(u, 1e18): continue
        for v in nbrs(*u):
            cst = cost(v[0], v[1], blocked)
            if v == b: cst = 1
            if cst is None: continue
            nd = d + cst
            if nd < best.get(v, 1e18): best[v] = nd; prev[v] = u; heapq.heappush(pq, (nd, v))
    if b not in best: return None, []
    p = [b]
    while p[-1] != a: p.append(prev[p[-1]])
    return best[b], p
def components(blocked):
    comp = {}; n = 0
    for r in range(H):
        for c in range(W):
            if (c, r) in comp or T0[K(c, r)] not in PASS or (c, r) in blocked: continue
            n += 1; st = [(c, r)]; comp[(c, r)] = n
            while st:
                u = st.pop()
                for v in nbrs(*u):
                    if v not in comp and T0[K(v[0], v[1])] in PASS and v not in blocked: comp[v] = n; st.append(v)
    return comp
edges = [(tuple((bases[a]['c'], bases[a]['r'])), tuple((bases[b]['c'], bases[b]['r']))) for a, b, _ in D['edges']]
before = [path(a, b, set()) for a, b in edges]
comp0 = components(set()); main0 = collections.Counter(comp0.values()).most_common(1)[0][0]
for it in range(12):
    undo = set()
    for (a, b), (c0, p0) in zip(edges, before):
        c1, p1 = path(a, b, conv)
        if c1 is None or c1 > c0 * SLACK:
            for h in p0:                                   # 전의 길과 그 옆의 바꾼 칸을 되돌린다
                if h in conv: undo.add(h)
                for v in nbrs(*h):
                    if v in conv: undo.add(v)
    comp1 = components(conv); main1 = collections.Counter(comp1.values()).most_common(1)[0][0]
    cut = [h for h, k in comp0.items() if k == main0 and h not in conv and comp1.get(h) != main1]
    for h in cut:
        for v in nbrs(*h):
            if v in conv: undo.add(v)
    print('  %d번째: 되돌릴 칸 %d (끊긴 칸 %d)' % (it + 1, len(undo), len(cut)))
    if not undo: break
    conv -= undo
else: raise SystemExit('가라앉지 않았다')
# 한 칸짜리 구멍(사방이 산이 된 갈 수 있는 칸)은 남기지 않는다: 이웃이 모두 못 가는 칸이면 함께 산으로
after = [path(a, b, conv) for a, b in edges]
worst = max((c1 / c0 for (c0, _), (c1, _) in zip(before, after)))
print('바꾸는 칸 %d %s · 이웃 거점 사이 걸음이 가장 많이 늘어난 곳 ×%.3f · 늘어난 길 %d / %d' % (len(conv), dict(collections.Counter(T0[K(c, r)] for c, r in conv)), worst, sum(1 for (c0, _), (c1, _) in zip(before, after) if c1 > c0), len(edges)))
for c, r in conv: T[K(c, r)] = 'm'
CONV = conv
D['t0'] = T0; D['t'] = ''.join(T)
print('산 %d → %d칸 · 갈 수 있는 칸 %d → %d' % (T0.count('m'), D['t'].count('m'), sum(1 for ch in T0 if ch in PASS), sum(1 for ch in D['t'] if ch in PASS)))
write(D)
