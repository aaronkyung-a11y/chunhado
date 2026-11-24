#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.22 관문의 능선 — 성의 부지와 성역을 피해서 다시 세운다(0.21 의 gates21.py 를 고친 것).
 0.21 의 능선은 가장 싼 변만 골랐기 때문에 세 성(홍농 · 허창 · 한중)에서 부지와 부지 사이를 지나갔다 — 붙어 있는 농장이 "인접한 같은 시설 필요"로 합쳐지지 않았다.
 이제 부지 칸과 성에서 SAFE_R 칸 안의 칸에 닿는 변은 막지 않는다(값을 무한으로 둔다). 능선은 그 바깥으로 돌아간다.
 ── 아래는 0.21 의 설명 ──
 v0.21 관문이 길목이 되게 한다.   ("함곡관, 호로관 같은 관문을 아래로 통과할 수 있으면 관문이 왜 필요하지?")
 0.20 까지: 일곱 관문 모두 옆으로 돌아가는 길이 있었고, 그 길이 관문을 지나는 길보다 0 ~ 1걸음밖에 길지 않았다.
 관문마다 길을 가로지르는 '성벽'을 세운다. 성벽은 칸이 아니라 칸과 칸 사이(변)에 선다 — 땅은 바꾸지 않는다.
   · 관문을 지나는 길의 방향에 수직인 선(관문을 지난다)을 긋고, 그 선을 넘나드는 변을 막는다.
   · 다 막지는 않는다: 관문에서 R 칸 안에서, 관문을 지나지 않고 양쪽을 잇는 가장 짧은 길을 찾아 그 길이 선을 넘는 변을 막는다 — 그런 길이 없어질 때까지.
     (이미 산과 물로 막힌 곳에는 성벽이 서지 않는다. R 칸 밖으로 크게 돌아가는 길은 남는다.)
 성벽 때문에 끊긴 길(거점과 거점을 잇는 edge 가운데 관문 곁을 스쳐 가던 것)은 그 관문에 다시 잇는다(예: 낙양 — 허창 → 호로관 — 허창).
 usage: gates22.py <src/mapdata.js> <build/mapdata.json> [--dry] [--r=16] [--safe=2] [--show[=관문]]      두 번 돌려도 같다(이미 walls 가 있으면 그만둔다)."""
import sys, json, re, math, collections, heapq
SRC, JS = sys.argv[1], sys.argv[2]; DRY = '--dry' in sys.argv
R = int([a for a in sys.argv if a.startswith('--r=')][0][4:]) if any(a.startswith('--r=') for a in sys.argv) else 9
s = open(SRC, encoding='utf8').read()
m = re.match(r'^(var MAPDATA\s*=\s*)(.*?)(;\s*)$', s, re.S); D = json.loads(m.group(2))
M = json.load(open(JS, encoding='utf8'))
if D.get('walls') and not DRY: print('already there'); sys.exit(0)
W, H = D['W'], D['H']; T = D['t']; RD = D['road']; SQ3 = math.sqrt(3)
def nb(c, r):
    odd = r & 1
    return [(c + dc, r + dr) for dc, dr in ((1, 0), (-1, 0), (odd, -1), (odd - 1, -1), (odd, 1), (odd - 1, 1)) if 0 <= c + dc < W and 0 <= r + dr < H]
def pos(c, r): return (SQ3 * (c + 0.5 * (r & 1)), 1.5 * r)
def cube(c, r): x = c - (r - (r & 1)) // 2; return (x, -x - r, r)
def hd(a, b): A, B = cube(*a), cube(*b); return max(abs(A[i] - B[i]) for i in range(3))
def passable(c, r): return T[r * W + c] not in 'xsm'
bases = D['bases']; BAT = {(b['c'], b['r']): i for i, b in enumerate(bases)}
GATES = set(h for h, i in BAT.items() if bases[i]['k'] == 'gate')
SAFE_R = int([a for a in sys.argv if a.startswith('--safe=')][0][7:]) if any(a.startswith('--safe=') for a in sys.argv) else 2
SAFE = set()                                                    # 능선이 닿지 않을 칸: 성의 부지 + 성에서 SAFE_R 칸 안
for nm, pl in D['plots'].items():
    for c, r in pl: SAFE.add((c, r))
for b in bases:
    if b['k'] != 'city': continue
    for r in range(max(0, b['r'] - SAFE_R), min(H, b['r'] + SAFE_R + 1)):
        for c in range(max(0, b['c'] - SAFE_R - 1), min(W, b['c'] + SAFE_R + 2)):
            if hd((c, r), (b['c'], b['r'])) <= SAFE_R: SAFE.add((c, r))
WALL = set()                                                    # 막힌 변: frozenset({칸, 칸})
def walled(a, b): return frozenset((a, b)) in WALL
def route(a, b, through=None, limit=None, center=None):
    """a → b 의 가장 짧은 길(걸음 수). 거점 칸은 끝점과 through(지나갈 수 있는 관문)만 밟는다. 성벽은 못 넘는다. limit: center 에서 이 칸 안에서만."""
    prev = {a: None}; q = collections.deque([a])
    while q:
        u = q.popleft()
        if u == b:
            p = []
            while u is not None: p.append(u); u = prev[u]
            return p[::-1]
        for v in nb(*u):
            if v in prev or walled(u, v): continue
            if limit is not None and hd(v, center) > limit: continue
            if v in BAT:
                if v != b and v != through: continue
            elif not passable(*v): continue
            prev[v] = u; q.append(v)
    return None
ELEV = D.get('e')
def wgt(u, v):
    """변 하나를 막는 값 — 구릉과 높은 땅은 싸고(능선이 서기 좋다), 길 위와 평지는 비싸다."""
    tu, tv = T[u[1] * W + u[0]], T[v[1] * W + v[0]]
    w = 6 - 2 * ((tu == 'h') + (tv == 'h'))
    if RD[u[1] * W + u[0]] == '1' or RD[v[1] * W + v[0]] == '1': w += 4
    return w
def cutwall(G0, sa, sb, sco, gi, R, KEEP):
    """관문에서 R 칸 안에서, 관문을 지나지 않고는 이쪽(a0 쪽)에서 저쪽(b0 쪽)으로 못 가게 하는 가장 싼 변들(최소 절단)."""
    band = R * 0.55 * SQ3
    nodes = [(c, r) for r in range(max(0, G0[1] - R), min(H, G0[1] + R + 1)) for c in range(max(0, G0[0] - R - 1), min(W, G0[0] + R + 2))
             if hd((c, r), G0) <= R and (c, r) != G0 and ((c, r) in BAT or passable(c, r))]
    idx = {h: i for i, h in enumerate(nodes)}; N = len(nodes); S, Tt = N, N + 1
    cap = collections.defaultdict(int); adj = collections.defaultdict(set)
    def add(u, v, c):
        cap[(u, v)] += c; adj[u].add(v); adj[v].add(u)
    INF = 10 ** 6
    for h, i in idx.items():
        for v in nb(*h):
            if v in idx and not walled(h, v): add(i, idx[v], INF if (h in BAT or v in BAT or h in SAFE or v in SAFE or frozenset((h, v)) in KEEP) else wgt(h, v))
        if h in sa or (hd(h, G0) == R and sco(h) < -band): add(S, i, INF)
        if h in sb or (hd(h, G0) == R and sco(h) > band): add(i, Tt, INF)
    flow = 0
    while True:                                                 # Edmonds–Karp
        prev = {S: None}; q = collections.deque([S])
        while q and Tt not in prev:
            u = q.popleft()
            for v in adj[u]:
                if v not in prev and cap[(u, v)] > 0: prev[v] = u; q.append(v)
        if Tt not in prev: break
        f = INF; v = Tt
        while prev[v] is not None: f = min(f, cap[(prev[v], v)]); v = prev[v]
        v = Tt
        while prev[v] is not None: cap[(prev[v], v)] -= f; cap[(v, prev[v])] += f; v = prev[v]
        flow += f
        if flow >= INF: return None
    side = set(prev)                                            # 이쪽에서 닿는 칸
    out = []
    for h, i in idx.items():
        if i not in side: continue
        for v in nb(*h):
            if v in idx and idx[v] not in side and not walled(h, v):
                WALL.add(frozenset((h, v))); out.append([h[0], h[1], v[0], v[1], gi])
    return out
FOOT = {'p': 3, 'f': 5, 'h': 5, 'd': 4}
def step(v):
    k = v[1] * W + v[0]; t = T[k]; rd = RD[k] == '1'
    return (4 if rd else 8) if t == 'w' else (2 if rd else FOOT[t])
def walk(a, b, through=(), want_path=False):
    """a → b 의 가장 싼 길의 값(보병의 이동력). 거점 칸은 끝점과 through(지나갈 수 있는 관문들)만. 성벽은 못 넘는다. 없으면 None."""
    dist = {a: 0}; pq = [(0, a)]; prev = {a: None}
    while pq:
        d, u = heapq.heappop(pq)
        if u == b:
            if not want_path: return d
            pp = []
            while u is not None: pp.append(u); u = prev[u]
            return pp[::-1]
        if d > dist[u]: continue
        for v in nb(*u):
            if walled(u, v): continue
            if v in BAT:
                if v != b and v not in through: continue
                c = 2
            elif not passable(*v): continue
            else: c = step(v)
            if d + c < dist.get(v, 1e9): dist[v] = d + c; prev[v] = u; heapq.heappush(pq, (d + c, v))
    return None
report = []; per = {}; used = {}; ends_ = {}
OPEN = {'호로관': [frozenset(('허창', '낙양'))],                # 호로관은 낙양의 동쪽을 모두 막는다 — 허창 길도 이 관문을 지난다
        '동관': [frozenset(('장안', '무관'))],
        '양평관': [frozenset(('한중', '검각'))]}               # 한중 — 검각 길은 양평관을 한 바퀴 돌아 나갔다 — 양평관을 지나 남서로 갈라지는 길로                  # 장안 — 무관 길은 동관 바로 옆을 스쳐 갔다 — 동관을 지나 남쪽으로 갈라지는 길로
RMAX = {}
for gi, g in enumerate(bases):
    if g['k'] != 'gate': continue
    G0 = (g['c'], g['r']); ends = [(i, e) for i, e in enumerate(D['edges']) if gi in e[:2]]
    assert len(ends) == 2, (g['n'], ends)
    sides = []
    for i, e in ends:
        p = [tuple(x) for x in M['paths'][i]]
        if p[0] != G0: p.reverse()
        assert p[0] == G0, (g['n'], p[0])
        sides.append((e[0] if e[1] == gi else e[1], p))
    (ia, pa), (ib, pb) = sides
    A, B = (bases[ia]['c'], bases[ia]['r']), (bases[ib]['c'], bases[ib]['r'])
    before = (walk(A, B, GATES), walk(A, B))
    qa, qb = pos(*pa[min(3, len(pa) - 1)]), pos(*pb[min(3, len(pb) - 1)]); g0 = pos(*G0)
    dx, dz = qb[0] - qa[0], qb[1] - qa[1]; L = math.hypot(dx, dz); dx /= L; dz /= L
    def sco(h): p = pos(*h); return (p[0] - g0[0]) * dx + (p[1] - g0[1]) * dz
    a0, b0 = pa[1], pb[1]
    assert sco(a0) < 0 < sco(b0), (g['n'], sco(a0), sco(b0))
    # 다른 길(이 관문을 지나지 않는 길)은 끊지 않는다 — 다만 OPEN 에 적은 길은 이 관문에 다시 잇는다
    KEEP = set()
    for i2, e2 in enumerate(D['edges']):
        if gi in e2[:2]: continue
        nm = frozenset((bases[e2[0]]['n'], bases[e2[1]]['n']))
        if nm in OPEN.get(g['n'], ()): continue
        p2 = [tuple(x) for x in M['paths'][i2]]
        for j in range(len(p2) - 1): KEEP.add(frozenset((p2[j], p2[j + 1])))
    mine = None; RR = RMAX.get(g['n'], R)
    while mine is None and RR >= 5:
        sa = set(h for h in pa[1:] if hd(h, G0) <= RR and h not in BAT); sb = set(h for h in pb[1:] if hd(h, G0) <= RR and h not in BAT)
        mine = cutwall(G0, sa, sb, sco, gi, RR, KEEP)
        if mine is None: RR -= 1
    assert mine is not None, g['n']
    assert route(a0, b0, None, RR, G0) is None, g['n']
    used[gi] = RR
    per[gi] = mine
    ends_[gi] = (A, B, before, ia, ib)
for gi in per:
    A, B, before, ia, ib = ends_[gi]; g = bases[gi]; G0 = (g['c'], g['r'])
    print(g['n'], bases[ia]['n'] + '–' + bases[ib]['n'], 'R', used[gi], '성벽 변', len(per[gi]), '가장 먼 변', max([hd((w[0], w[1]), G0) for w in per[gi]] or [0]), '| 보병 이동력: 관문 길 / 돌아가는 길  전', before, '→ 후', (walk(A, B, GATES), walk(A, B)))
PLOTSET = set((c, r) for pl in D['plots'].values() for c, r in pl)
badp = [w for gi in per for w in per[gi] if (w[0], w[1]) in SAFE or (w[2], w[3]) in SAFE]
print('부지 · 성역에 닿는 변', len(badp))
assert not badp
if any(a.startswith('--show') for a in sys.argv):
    mark = {}
    for w in [w for gi in per for w in per[gi]]: mark[(w[0], w[1])] = 'a'; mark[(w[2], w[3])] = 'b'
    for gi in per:
        G0 = (bases[gi]['c'], bases[gi]['r']); print(bases[gi]['n'])
        if '--show=' + bases[gi]['n'] not in sys.argv and '--show' not in sys.argv: continue
        for r in range(G0[1] - R - 1, G0[1] + R + 2):
            row = ''
            for c in range(G0[0] - R - 2, G0[0] + R + 3):
                if not (0 <= c < W and 0 <= r < H): row += ' '; continue
                if (c, r) in BAT: row += 'G' if bases[BAT[(c, r)]]['k'] == 'gate' else 'C'
                elif (c, r) in mark: row += mark[(c, r)]
                elif (c, r) in PLOTSET: row += 'o'
                else:
                    t = T[r * W + c]; row += '=' if RD[r * W + c] == '1' else {'p': '.', 'm': '^', 'x': '#', 's': '~', 'h': ':', 'f': ';', 'w': '-', 'd': ','}.get(t, t)
            print(('%3d ' % r) + (' ' if r & 1 else '') + row)
walls = [w for gi in per for w in per[gi]]
# ---- 성벽에 끊긴 길을 관문에 다시 잇는다 ----
edges = [list(e) for e in D['edges']]; paths = [[tuple(x) for x in p] for p in M['paths']]; changed = []
wallgate = {frozenset(((w[0], w[1]), (w[2], w[3]))): w[4] for w in walls}
def has(x, y): return any(q is not None and set(q[:2]) == {x, y} for q in edges)
for i, e in enumerate(list(edges)):
    a, b = e[0], e[1]; p = paths[i]
    cr = [j for j in range(len(p) - 1) if frozenset((p[j], p[j + 1])) in wallgate]
    if not cr: continue
    assert wallgate[frozenset((p[cr[0]], p[cr[0] + 1]))] not in (a, b), (bases[a]['n'], bases[b]['n'], cr)
    assert len(cr) == 1, (bases[a]['n'], bases[b]['n'], cr)
    j = cr[0]; gi = wallgate[frozenset((p[j], p[j + 1]))]; gh = (bases[gi]['c'], bases[gi]['r'])
    assert gh in nb(*p[j]) or gh in nb(*p[j + 1]), (bases[a]['n'], bases[b]['n'], p[j], p[j + 1], gh)      # 끊긴 자리는 관문 바로 옆이어야 한다
    A0, B0 = (bases[a]['c'], bases[a]['r']), (bases[b]['c'], bases[b]['r'])
    first = p[0] == A0; ea, eb = (a, b) if first else (b, a)
    new = []
    for x, y, hx, hy in ((ea, gi, p[0], gh), (gi, eb, gh, p[-1])):
        if has(x, y): continue
        pp = walk(hx, hy, (), True); assert pp is not None, (bases[x]['n'], bases[y]['n'])
        new.append([x, y, len(pp) - 1, pp])
    changed.append((bases[a]['n'] + '–' + bases[b]['n'], '길이', e[2], '→', bases[gi]['n'], '에서 끊김 · 새 길', [(bases[x[0]]['n'], bases[x[1]]['n'], x[2]) for x in new]))
    edges[i] = None
    for x in new: edges.append(x[:3]); paths.append(x[3])
keep = [i for i, e in enumerate(edges) if e is not None]
edges2 = [edges[i] for i in keep]; paths2 = [[list(h) for h in paths[i]] for i in keep]
for c in changed: print('  edge', c)
print('walls', len(walls), 'edges', len(D['edges']), '→', len(edges2))
if not DRY:
    D['walls'] = walls; D['edges'] = edges2
    M['walls'] = walls; M['edges'] = edges2; M['paths'] = paths2
    open(SRC, 'w', encoding='utf8').write(m.group(1) + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + m.group(3))
    json.dump(M, open(JS, 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
    print('written')
