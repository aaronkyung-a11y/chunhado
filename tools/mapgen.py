#!/usr/bin/env python3
"""천하도 맵 생성기 — 수묵 고지도(china.jpg)에서 헥스 지형을 뽑고 도로·부지를 배치한다.
usage: mapgen.py <china.jpg> <out_mapdata.js> <debug.jpg>
"""
import sys, math, json, heapq, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SRC, OUT_JS, OUT_DBG = sys.argv[1], sys.argv[2], sys.argv[3]

# ---------- 격자 ----------
CROP = (50, 55, 915, 955)          # 원본 이미지 좌표
HEXW = 13.0
R = HEXW / math.sqrt(3)
ROWH = 1.5 * R
W, H = 66, 79

def center(c, r):
    return (HEXW * (c + 0.5 * (r & 1)) + HEXW / 2, R + r * ROWH)   # crop 좌표

def nbrs(c, r):
    if r & 1:
        d = [(1, 0), (-1, 0), (1, -1), (0, -1), (1, 1), (0, 1)]
    else:
        d = [(1, 0), (-1, 0), (0, -1), (-1, -1), (0, 1), (-1, 1)]
    out = []
    for dc, dr in d:
        cc, rr = c + dc, r + dr
        if 0 <= cc < W and 0 <= rr < H:
            out.append((cc, rr))
    return out

def to_cube(c, r):
    x = c - (r - (r & 1)) // 2
    z = r
    return (x, -x - z, z)

def dist(a, b):
    ax, ay, az = to_cube(*a); bx, by, bz = to_cube(*b)
    return max(abs(ax - bx), abs(ay - by), abs(az - bz))

def px2hex(x, y):
    """원본 이미지 좌표 → 가장 가까운 헥스"""
    x -= CROP[0]; y -= CROP[1]
    r0 = int(round((y - R) / ROWH))
    best = None
    for r in (r0 - 1, r0, r0 + 1):
        if r < 0 or r >= H: continue
        c0 = int(round((x - HEXW / 2) / HEXW - 0.5 * (r & 1)))
        for c in (c0 - 1, c0, c0 + 1):
            if c < 0 or c >= W: continue
            cx, cy = center(c, r)
            d = (cx - x) ** 2 + (cy - y) ** 2
            if best is None or d < best[0]: best = (d, c, r)
    return (best[1], best[2])

def ring(c, r, n):
    return [(cc, rr) for cc in range(max(0, c - n - 1), min(W, c + n + 2)) for rr in range(max(0, r - n), min(H, r + n + 1)) if dist((c, r), (cc, rr)) == n]

# ---------- 입력 데이터 ----------
# (이름, x, y, 규모)  규모: L 대도시 / M 중도시 / S 소도시
CITIES = [
 ('양평',785,112,'S'),('북평',661,136,'M'),('계',595,151,'M'),('남피',654,239,'M'),('평원',698,284,'M'),
 ('진양',490,250,'M'),('업',580,306,'L'),('북해',816,291,'M'),('하비',775,452,'M'),('소패',708,432,'M'),
 ('수춘',675,535,'M'),('복양',662,368,'M'),('진류',605,405,'M'),('허창',572,462,'L'),('여남',610,525,'M'),
 ('낙양',522,418,'L'),('완',470,478,'M'),('장안',351,387,'L'),('상용',390,535,'S'),('안정',277,284,'S'),
 ('천수',196,320,'S'),('무위',108,224,'S'),('한중',300,476,'M'),('자동',226,535,'M'),('강주',300,655,'M'),
 ('영안',392,590,'S'),('성도',232,622,'L'),('건녕',255,808,'S'),('운남',165,790,'S'),('신야',520,520,'S'),
 ('양양',470,560,'L'),('강릉',490,618,'M'),('강하',578,632,'M'),('장사',506,793,'M'),('무릉',440,720,'S'),
 ('계양',536,896,'S'),('영릉',440,850,'S'),('여강',725,585,'M'),('건업',815,535,'L'),('오',872,560,'M'),
 ('회계',880,640,'M'),('시상',665,655,'M'),
]
GATES = [
 ('호관',535,282),('호로관',562,408),('함곡관',480,412),('동관',440,395),('무관',410,440),
 ('양평관',262,462),('검각',262,508),
]
EDGES = [
 '양평-북평','북평-계','북평-남피','계-남피','계-진양','남피-평원','남피-업','평원-업','평원-북해','평원-복양',
 '업-복양','진양-호관','호관-업','진양-낙양','북해-하비','복양-진류','복양-소패','소패-하비','소패-진류',
 '하비-수춘','하비-건업','수춘-여남','수춘-여강','진류-허창','진류-호로관','호로관-낙양','허창-여남','허창-완',
 '허창-낙양','여남-신야','낙양-완','낙양-함곡관','함곡관-동관','동관-장안','장안-무관','무관-완','장안-안정',
 '장안-천수','장안-한중','안정-천수','안정-무위','천수-무위','천수-양평관','양평관-한중','한중-상용','상용-양양',
 '한중-검각','검각-자동','자동-성도','자동-강주','성도-강주','성도-건녕','강주-영안','강주-건녕',
 '건녕-운남','영안-강릉','완-신야','신야-양양','양양-강릉','양양-강하','강릉-강하','강릉-무릉','강하-시상',
 '강하-여강','강하-장사','무릉-장사','무릉-영릉','장사-계양','영릉-계양','장사-시상','시상-여강','여강-건업',
 '건업-오','오-회계','회계-시상',
]
HUANGHE = [(92,338),(150,332),(200,318),(225,298),(228,268),(255,248),(290,232),(305,180),(318,130),(345,105),(400,100),(455,108),(485,130),(490,160),(478,200),(468,240),(462,280),(470,320),(458,360),(452,395),(475,405),(510,397),(555,396),(600,388),(640,372),(672,340),(700,310),(735,280),(765,250),(790,236)]
CHANGJIANG = [(200,693),(236,689),(286,668),(314,650),(371,614),(429,593),(464,587),(500,596),(514,621),(543,636),(571,654),(604,625),(629,604),(657,621),(693,632),(721,614),(757,586),(786,543),(800,511),(829,504),(879,514),(915,521)]
SEAS = [
 [(860,68),(830,85),(810,105),(797,125),(785,145),(778,153),(762,170),(750,177),(735,175),(727,185),(725,200),(735,215),(750,222),(770,225),(780,235),(782,245),(790,262),(800,268),(812,262),(822,250),(832,240),(850,232),(862,240),(868,252),(880,255),(900,250),(915,253),(915,150),(880,170),(852,185),(850,170),(868,160),(870,152),(855,148),(852,140),(868,125),(878,100),(868,75)],
 [(920,272),(895,278),(885,285),(870,290),(858,297),(855,305),(850,312),(842,315),(845,325),(832,330),(822,345),(812,365),(808,385),(812,395),(830,400),(845,410),(852,430),(860,450),(872,470),(885,490),(888,505),(900,512),(920,518)],
 [(920,700),(912,700),(905,712),(895,720),(893,745),(880,760),(868,768),(858,775),(852,790),(855,800),(850,815),(848,830),(835,838),(825,848),(815,858),(800,868),(790,875),(775,885),(765,900),(755,915),(745,925),(735,935),(725,950),(700,975),(920,975)],
]
LAKES = [(702,668,13),(850,556,11),(772,458,11),(78,283,14)]

# ---------- 이미지 분석 ----------
img = Image.open(SRC).convert('RGB')
arr = np.asarray(img).astype(np.float32)
lum = arr @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
dark = (lum < 118).astype(np.float32)
# 적분 이미지로 원형(사각 근사) 평균
ii = np.pad(dark.cumsum(0).cumsum(1), ((1, 0), (1, 0)))
def box_mean(x, y, rad):
    x0 = int(max(0, x - rad)); x1 = int(min(arr.shape[1], x + rad + 1))
    y0 = int(max(0, y - rad)); y1 = int(min(arr.shape[0], y + rad + 1))
    s = ii[y1, x1] - ii[y0, x1] - ii[y1, x0] + ii[y0, x0]
    return s / max(1, (x1 - x0) * (y1 - y0))

T = {}            # (c,r) -> 지형 문자
DK = {}           # 어두움 지수
for r in range(H):
    for c in range(W):
        cx, cy = center(c, r)
        ix, iy = cx + CROP[0], cy + CROP[1]
        m = box_mean(ix, iy, 8)
        DK[(c, r)] = m
        T[(c, r)] = 'm' if m >= 0.30 else ('h' if m >= 0.14 else 'p')

def in_poly(x, y, poly):
    ins = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xi = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if xi > x: ins = not ins
    return ins

for (c, r) in list(T):
    cx, cy = center(c, r); ix, iy = cx + CROP[0], cy + CROP[1]
    for poly in SEAS:
        if in_poly(ix, iy, poly): T[(c, r)] = 's'
    for (lx, ly, lr) in LAKES:
        if (ix - lx) ** 2 + (iy - ly) ** 2 <= lr * lr: T[(c, r)] = 'w'

RIVER = set()
def raster(poly):
    for i in range(len(poly) - 1):
        x1, y1 = poly[i]; x2, y2 = poly[i + 1]
        n = int(math.hypot(x2 - x1, y2 - y1) / 2) + 1
        for k in range(n + 1):
            x = x1 + (x2 - x1) * k / n; y = y1 + (y2 - y1) * k / n
            if CROP[0] <= x < CROP[2] and CROP[1] <= y < CROP[3]:
                h = px2hex(x, y)
                RIVER.add(h)
raster(HUANGHE); raster(CHANGJIANG)
for h in RIVER:
    if T[h] != 's': T[h] = 'w'

# ---------- 거점 ----------
BASES = []   # dict(name, kind, c, r, size)
used = {}
def place(name, x, y, kind, size):
    h = px2hex(x, y)
    if T[h] in 'sw' or h in used:
        # 가장 가까운 육지 헥스로
        cand = sorted(((dist(h, (c, r)), abs(center(c, r)[0] + CROP[0] - x) + abs(center(c, r)[1] + CROP[1] - y), (c, r)) for c in range(W) for r in range(H) if T[(c, r)] not in 'sw' and (c, r) not in used and dist(h, (c, r)) <= 3))
        h = cand[0][2]
    used[h] = name
    BASES.append(dict(name=name, kind=kind, c=h[0], r=h[1], size=size))
for (n, x, y, s) in CITIES: place(n, x, y, 'city', s)
for (n, x, y) in GATES: place(n, x, y, 'gate', 'G')
BIDX = {b['name']: i for i, b in enumerate(BASES)}
BASEHEX = {(b['c'], b['r']): i for i, b in enumerate(BASES)}

# 도시 주변 1칸은 평지로(물 제외)
for b in BASES:
    T[(b['c'], b['r'])] = 'p'
    if b['kind'] == 'city':
        for h in ring(b['c'], b['r'], 1):
            if T[h] in 'mh': T[h] = 'p'
        for h in ring(b['c'], b['r'], 2):
            if T[h] == 'm': T[h] = 'h'

# ---------- 도로(A*) ----------
ROAD = set()
COST = {'p': 1.0, 'h': 1.8, 'm': 4.5, 'w': 5.0, 's': 1e9, 'f': 1.3, 'd': 1.2}
def line_dev(h, a, b):
    (x0, y0), (x1, y1), (x2, y2) = center(*h), center(*a), center(*b)
    L = math.hypot(x2 - x1, y2 - y1) or 1.0
    t = max(0.0, min(1.0, ((x0 - x1) * (x2 - x1) + (y0 - y1) * (y2 - y1)) / (L * L)))
    return math.hypot(x0 - (x1 + t * (x2 - x1)), y0 - (y1 + t * (y2 - y1))) / HEXW
def astar(a, b, banned=frozenset()):
    pq = [(0, a)]; g = {a: 0}; prev = {}
    while pq:
        f, u = heapq.heappop(pq)
        if u == b: break
        if f - dist(u, b) * 0.6 > g[u] + 1e-9: continue
        for v in nbrs(*u):
            if v in banned: continue
            if v in BASEHEX and v != b: continue          # 다른 거점은 통과하지 않음
            t = T[v]
            if t == 's': continue
            cst = COST[t]
            if v in ROAD: cst = min(cst, 0.6) if t != 'w' else 2.5
            cst += 0.45 * max(0.0, line_dev(v, a, b) - 1.0)
            ng = g[u] + cst
            if v not in g or ng < g[v] - 1e-9:
                g[v] = ng; prev[v] = u
                heapq.heappush(pq, (ng + dist(v, b) * 0.6, v))
    if b not in g: return None
    path = [b]
    while path[-1] != a: path.append(prev[path[-1]])
    return path[::-1]

EDGE_PATHS = []
for e in EDGES:
    an, bn = e.split('-')
    A = BASES[BIDX[an]]; B = BASES[BIDX[bn]]
    p = astar((A['c'], A['r']), (B['c'], B['r']))
    assert p, e
    EDGE_PATHS.append((BIDX[an], BIDX[bn], p))
    for h in p[1:-1]:
        ROAD.add(h)
        if T[h] == 'm': T[h] = 'h'

# ---------- 산길 넓히기 ----------
GATEHEX = [(b['c'], b['r']) for b in BASES if b['kind'] == 'gate']
for h in list(ROAD):
    if any(dist(h, g) <= 2 for g in GATEHEX): continue
    for v in nbrs(*h):
        if T[v] == 'm': T[v] = 'h'

# ---------- 관문 요충 강제 ----------
def passable(h): return T[h] not in 'ms'
def bfs_len(a, b, banned):
    from collections import deque
    dq = deque([a]); seen = {a: None}
    while dq:
        u = dq.popleft()
        if u == b: break
        for v in nbrs(*u):
            if v in seen or v in banned or not passable(v): continue
            if v in BASEHEX and v != b: continue
            seen[v] = u; dq.append(v)
    if b not in seen: return None
    path = [b]
    while seen[path[-1]] is not None: path.append(seen[path[-1]])
    return path[::-1]
PROTECT = set()
for b in BASES:
    PROTECT.add((b['c'], b['r']))
    if b['kind'] == 'city':
        for n in (1, 2):
            for h in ring(b['c'], b['r'], n): PROTECT.add(h)
blocked_added = []
for gname in [g[0] for g in GATES]:
    G = BASES[BIDX[gname]]; gh = (G['c'], G['r'])
    for n in (1, 2):
        for h in ring(gh[0], gh[1], n):
            if h not in ROAD and h not in BASEHEX and T[h] not in 'sw' and h not in PROTECT:
                if T[h] != 'm': blocked_added.append(h)
                T[h] = 'm'
    ends = [bi for (a, b2, p) in EDGE_PATHS for bi in ((a, b2) if BIDX[gname] in (a, b2) else ()) if bi != BIDX[gname]]
    if len(ends) < 2: continue
    A = BASES[ends[0]]; B = BASES[ends[1]]
    ah = (A['c'], A['r']); bh = (B['c'], B['r'])
    for _ in range(14):
        p = bfs_len(ah, bh, {gh})
        if p is None or len(p) > 26: break
        cand = [h for h in p[1:-1] if h not in ROAD and h not in PROTECT and h not in BASEHEX and T[h] != 'w' and dist(h, gh) <= 5]
        if not cand: break
        cand.sort(key=lambda h: dist(h, gh))
        T[cand[0]] = 'm'; blocked_added.append(cand[0])

# ---------- 부지 ----------
NPLOT = {'L': 10, 'M': 8, 'S': 6}
PLOTS = {}
claimed = set()
for b in BASES:
    if b['kind'] != 'city': continue
    ch = (b['c'], b['r'])
    def ok(h):
        if h in ROAD or h in BASEHEX or h in claimed: return False
        if T[h] in 'sw': return False
        for o in BASES:
            oh = (o['c'], o['r'])
            if oh != ch and dist(h, oh) <= 1: return False
        return True
    r1 = [h for h in ring(*ch, 1) if ok(h)]
    r2 = [h for h in ring(*ch, 2) if ok(h)]
    r3 = [h for h in ring(*ch, 3) if ok(h)]
    # 인접 1칸은 최대 3개만(출진 칸 확보)
    free1 = [h for h in ring(*ch, 1) if T[h] not in 'sw']
    keep_free = max(2, len(free1) - 3)
    road1 = [h for h in free1 if h in ROAD]
    max_r1 = max(0, len(free1) - max(keep_free, len(road1)))
    chosen = r1[:max_r1]
    def adjcount(h): return sum(1 for v in nbrs(*h) if v in chosen)
    pool = r2 + r3
    while len(chosen) < NPLOT[b['size']] and pool:
        pool.sort(key=lambda h: (-(adjcount(h) > 0), dist(h, ch), -adjcount(h), DK[h]))
        chosen.append(pool.pop(0))
    for h in chosen:
        claimed.add(h); T[h] = 'p'
    PLOTS[b['name']] = chosen

# ---------- 외곽(비활성) / 숲 / 황무지 ----------
from collections import deque
near = {}
dq = deque()
for h in list(ROAD) + list(BASEHEX) + list(claimed):
    near[h] = 0; dq.append(h)
while dq:
    u = dq.popleft()
    if near[u] >= 5: continue
    for v in nbrs(*u):
        if v not in near:
            near[v] = near[u] + 1; dq.append(v)
VOID = set(h for h in T if h not in near)

random.seed(194)
def vnoise(x, y, s, seed):
    def rnd(i, j):
        n = (i * 374761393 + j * 668265263 + seed * 2147483647) & 0xffffffff
        n = (n ^ (n >> 13)) * 1274126177 & 0xffffffff
        return ((n ^ (n >> 16)) & 0xffff) / 65535.0
    x /= s; y /= s
    i, j = int(math.floor(x)), int(math.floor(y)); fx, fy = x - i, y - j
    fx = fx * fx * (3 - 2 * fx); fy = fy * fy * (3 - 2 * fy)
    a = rnd(i, j) * (1 - fx) + rnd(i + 1, j) * fx
    b = rnd(i, j + 1) * (1 - fx) + rnd(i + 1, j + 1) * fx
    return a * (1 - fy) + b * fy
for (c, r) in list(T):
    h = (c, r)
    if T[h] != 'p' or h in ROAD or h in claimed or h in BASEHEX: continue
    cx, cy = center(c, r); ix, iy = cx + CROP[0], cy + CROP[1]
    n = 0.6 * vnoise(ix, iy, 34, 7) + 0.4 * vnoise(ix, iy, 13, 11)
    south = 1 if iy > 560 else 0
    west_dry = ix < 345 and iy < 345
    if west_dry:
        if n > 0.42: T[h] = 'd'
    else:
        thr = 0.60 if south else 0.68
        if n > thr and all(dist(h, (b['c'], b['r'])) > 1 for b in BASES): T[h] = 'f'

# ---------- 연결성 검증 ----------
def reach_all():
    start = (BASES[0]['c'], BASES[0]['r'])
    seen = {start}; dq = deque([start])
    while dq:
        u = dq.popleft()
        for v in nbrs(*u):
            if v in seen or T[v] in 'ms' or v in VOID: continue
            seen.add(v); dq.append(v)
    return [b['name'] for b in BASES if (b['c'], b['r']) not in seen]
unreach = reach_all()
assert not unreach, unreach

# ---------- 출력 ----------
rows = []
roadrows = []
for r in range(H):
    rows.append(''.join(('x' if (c, r) in VOID and T[(c, r)] not in 's' else T[(c, r)]) for c in range(W)))
    roadrows.append(''.join('1' if (c, r) in ROAD else '0' for c in range(W)))
out = dict(W=W, H=H, hexw=HEXW, crop=CROP, t=''.join(rows), road=''.join(roadrows),
           bases=[dict(n=b['name'], k=b['kind'], c=b['c'], r=b['r'], sz=b['size']) for b in BASES],
           edges=[[a, b, len(p) - 1] for (a, b, p) in EDGE_PATHS],
           paths=[[list(h) for h in p] for (a, b, p) in EDGE_PATHS],
           plots={n: [list(h) for h in v] for n, v in PLOTS.items()})
full = dict(out, dk=[round(float(DK[(c, r)]), 3) for r in range(H) for c in range(W)], blocked=[list(h) for h in blocked_added])
with open(OUT_JS.replace('.js', '.json'), 'w', encoding='utf-8') as f:
    json.dump(full, f, ensure_ascii=False)
slim = {k: v for k, v in out.items() if k not in ('paths', 'hexw', 'crop')}
with open(OUT_JS, 'w', encoding='utf-8') as f:
    f.write('var MAPDATA=' + json.dumps(slim, ensure_ascii=False, separators=(',', ':')) + ';\n')

# ---------- 디버그 렌더 ----------
SC = 2.0
crop = img.crop(CROP).resize((int((CROP[2] - CROP[0]) * SC), int((CROP[3] - CROP[1]) * SC)), Image.LANCZOS).convert('RGBA')
ov = Image.new('RGBA', crop.size, (0, 0, 0, 0))
d = ImageDraw.Draw(ov)
COL = {'p': None, 'h': (200, 150, 60, 70), 'm': (90, 40, 20, 150), 'w': (40, 110, 230, 150), 's': (30, 60, 160, 120), 'f': (20, 130, 40, 110), 'd': (230, 200, 90, 90), 'x': (0, 0, 0, 120)}
def poly(c, r, sc=SC, shrink=0.94):
    cx, cy = center(c, r)
    return [((cx + R * shrink * math.cos(math.radians(60 * k - 30))) * sc, (cy + R * shrink * math.sin(math.radians(60 * k - 30))) * sc) for k in range(6)]
for r in range(H):
    for c in range(W):
        t = 'x' if (c, r) in VOID and T[(c, r)] != 's' else T[(c, r)]
        if COL[t]: d.polygon(poly(c, r), fill=COL[t])
        if (c, r) in ROAD: d.polygon(poly(c, r, shrink=0.45), fill=(150, 60, 0, 230))
for n, v in PLOTS.items():
    for h in v: d.polygon(poly(*h, shrink=0.7), outline=(255, 255, 255, 255), fill=(255, 255, 255, 90))
for h in blocked_added:
    d.polygon(poly(*h, shrink=0.5), outline=(255, 0, 255, 255))
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
for i, b in enumerate(BASES):
    cx, cy = center(b['c'], b['r'])
    col = (255, 230, 0, 255) if b['kind'] == 'city' else (255, 0, 0, 255)
    d.ellipse([cx * SC - 6, cy * SC - 6, cx * SC + 6, cy * SC + 6], fill=col, outline=(0, 0, 0, 255))
    d.text((cx * SC + 7, cy * SC - 7), str(i), fill=(0, 0, 0, 255), font=font)
Image.alpha_composite(crop, ov).convert('RGB').save(OUT_DBG, quality=85)
from collections import Counter
print('terrain', Counter(out['t']))
print('roads', len(ROAD), 'edges', len(EDGE_PATHS), 'avg len', sum(len(p) - 1 for _, _, p in EDGE_PATHS) / len(EDGE_PATHS))
print('plots', {n: len(v) for n, v in PLOTS.items()})
print('edge lens', [(BASES[a]['name'] + '-' + BASES[b]['name'], len(p) - 1) for a, b, p in EDGE_PATHS])
print('blocked', len(blocked_added))
