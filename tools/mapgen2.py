# -*- coding: utf-8 -*-
"""천하도 v0.2 지도 생성.
실제 고도(4096×2048 전지구 고도 이미지)·Natural Earth 해안/호수/강 + 거점의 실제 위경도
→ 헥스 지형, 거점, 도로, 관문 요충, 부지, 변경(비활성)
사용: mapgen2.py <geo_dir> <out mapdata.js> <out mapdata.json> <debug.png>
"""
import sys, os, json, math, heapq, random
from collections import deque, Counter
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo import CITY_LL, GATE_LL, lcc_fwd, lcc_inv

GEO, OUT_JS, OUT_JSON, OUT_DBG = sys.argv[1:5]
Image.MAX_IMAGE_PIXELS = None
SQ3 = math.sqrt(3)
W = 220
MARG = 9.5                      # 가장자리 여백(헥스)
MIN_CC, MIN_CG = 7.0, 6.0       # 거점 최소 간격(헥스): 도시-도시, 관문 포함
VOID_DIST = 13                  # 도로·거점에서 이보다 멀면 변경(비활성)

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
# 게임에서 '강'(건너기 어려운 물) 지형이 되는 큰 강. 나머지는 그림으로만.
MAJOR_RIVERS = {'Huang', 'Chang Jiang', 'Yangtze', 'Han', 'Huai', 'Wei'}
MINOR_RIVERS = {'Jinsha', 'Yuan', 'Gan', 'Min', 'Jialing', 'Wu', 'Xiang', 'Fen', 'Luan', 'Liao', 'Zhang', 'Qin', 'Jing', 'Tuo',
                'Hai', 'Yongding', 'Sanggan', 'Hudi', 'Ying', 'Dan', 'Fuchun', 'Dadu', 'Yalong', 'Daling', 'Yi', 'Xi', 'Hongshui', 'Nanpan', 'Bei', 'Dong', 'You', 'Yu', 'Xun'}
LAKES = {'Dongting Hu', 'Poyang Hu', 'Tai Hu', 'Chao Hu', 'Qinghai Hu'}
# 후한 때 황하 하류(왕경 치수 이후): 지금보다 북쪽으로 흘러 천승(리진) 부근에서 발해로. (경도, 위도) 근사
HAN_HUANGHE = [(113.55, 34.95), (114.15, 35.12), (114.55, 35.58), (115.02, 35.90), (115.55, 36.20), (116.10, 36.62),
               (116.70, 37.03), (117.35, 37.42), (117.95, 37.72), (118.55, 37.95), (119.0, 38.1)]

# ---------- 격자 ----------
names = list(CITY_LL) + list(GATE_LL)
ll = np.array([(CITY_LL.get(n) or GATE_LL[n])[:2] for n in names])
bx, by = lcc_fwd(ll[:, 0], ll[:, 1])
HW = (bx.max() - bx.min()) / (W - 2 * MARG)        # 헥스 폭(km)
RS = HW * SQ3 / 2                                   # 행 간격(km)
H = int(math.ceil((by.max() - by.min()) / RS + 2 * MARG))
U = HW / SQ3                                        # 월드 단위 1 = U km (헥스 반지름 R = 1)
X0 = bx.min() - MARG * HW
Y0 = by.max() + MARG * RS
WX, WZ = SQ3 * (W + 0.5), 1.5 * H + 0.5
print('grid %dx%d  hex %.2f km  world %.1fx%.1f' % (W, H, HW, WX, WZ))

def center(c, r): return (SQ3 * (c + 0.5 * (r & 1)) + SQ3 / 2, 1.5 * r + 1.0)
def km2w(x, y): return (np.asarray(x) - X0) / U, (Y0 - np.asarray(y)) / U
def w2km(wx, wz): return X0 + np.asarray(wx) * U, Y0 - np.asarray(wz) * U
def ll2w(lat, lon): return km2w(*lcc_fwd(lat, lon))
def w2ll(wx, wz): return lcc_inv(*w2km(wx, wz))
def inmap(c, r): return 0 <= c < W and 0 <= r < H
def w2hex(wx, wz):
    r0 = int(round((wz - 1.0) / 1.5)); best = None; bd = 1e18
    for r in (r0 - 1, r0, r0 + 1):
        c0 = int(round((wx - SQ3 / 2) / SQ3 - 0.5 * (r & 1)))
        for c in (c0 - 1, c0, c0 + 1):
            x, z = center(c, r); d = (x - wx) ** 2 + (z - wz) ** 2
            if d < bd: bd = d; best = (c, r)
    return best
NB_EVEN = [(1, 0), (-1, 0), (0, -1), (-1, -1), (0, 1), (-1, 1)]
NB_ODD = [(1, 0), (-1, 0), (1, -1), (0, -1), (1, 1), (0, 1)]
def nbrs(c, r):
    for dc, dr in (NB_ODD if r & 1 else NB_EVEN):
        if inmap(c + dc, r + dr): yield (c + dc, r + dr)
def cube(c, r): x = c - ((r - (r & 1)) >> 1); return x, r
def dist(a, b):
    ax, az = cube(*a); bx_, bz = cube(*b); dx = ax - bx_; dz = az - bz
    return max(abs(dx), abs(dz), abs(dx + dz))
def ring(c, r, n):
    return [(cc, rr) for rr in range(r - n, r + n + 1) for cc in range(c - n - 1, c + n + 2) if inmap(cc, rr) and dist((c, r), (cc, rr)) == n]

# ---------- 고도·육지 래스터 ----------
dem = np.asarray(Image.open(os.path.join(GEO, 'elev_bump_4k.jpg')).convert('L'), dtype=np.float32)
def dem_at(lat, lon):
    px = (np.asarray(lon) + 180.0) / 360.0 * dem.shape[1] - 0.5; py = (90.0 - np.asarray(lat)) / 180.0 * dem.shape[0] - 0.5
    return ndi.map_coordinates(dem, [py, px], order=1, mode='nearest')
LL_BOX = (92.0, 18.0, 130.0, 47.0); PPD = 80
def ll_raster(features, pick=None):
    im = Image.new('L', (int((LL_BOX[2] - LL_BOX[0]) * PPD), int((LL_BOX[3] - LL_BOX[1]) * PPD)), 0); d = ImageDraw.Draw(im)
    for f in features:
        g = f['geometry']
        if not g or (pick and not pick(f['properties'])): continue
        polys = [g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']
        for poly in polys:
            for k, ringc in enumerate(poly):
                a = np.asarray(ringc, dtype=np.float64)
                if a[:, 0].max() < LL_BOX[0] or a[:, 0].min() > LL_BOX[2] or a[:, 1].max() < LL_BOX[1] or a[:, 1].min() > LL_BOX[3]: continue
                pts = [((x - LL_BOX[0]) * PPD, (LL_BOX[3] - y) * PPD) for x, y in a]
                d.polygon(pts, fill=(255 if k == 0 else 0))
    return np.asarray(im, dtype=np.float32) / 255.0
def ll_sample(rast, lat, lon):
    return ndi.map_coordinates(rast, [(LL_BOX[3] - np.asarray(lat)) * PPD - 0.5, (np.asarray(lon) - LL_BOX[0]) * PPD - 0.5], order=1, mode='nearest')
land_ll = ll_raster(json.load(open(os.path.join(GEO, 'land10.geojson')))['features'])
lake_ll = ll_raster(json.load(open(os.path.join(GEO, 'lakes10.geojson')))['features'], lambda p: p.get('name') in LAKES)

GS = 0.5                                                   # 미세 격자 간격(월드 단위)
gx = np.arange(0, WX + GS, GS); gz = np.arange(0, WZ + GS, GS)
GXX, GZZ = np.meshgrid(gx, gz)
LAT, LON = w2ll(GXX, GZZ)
E = ndi.gaussian_filter(dem_at(LAT, LON), 0.7)             # 0..255
LANDF = ll_sample(land_ll, LAT, LON) * (1 - ll_sample(lake_ll, LAT, LON))
REL = ndi.maximum_filter(E, size=7) - ndi.minimum_filter(E, size=7)
# 해안선(텍스처용): 더 촘촘한 육지 마스크를 저장
_fx = np.arange(0, WX + 0.2, 0.2); _fz = np.arange(0, WZ + 0.2, 0.2); _FX, _FZ = np.meshgrid(_fx, _fz); _la, _lo = w2ll(_FX, _FZ)
np.save(os.path.join(os.path.dirname(OUT_JSON), 'landmask.npy'), (ll_sample(land_ll, _la, _lo) * (1 - ll_sample(lake_ll, _la, _lo))).astype(np.float32))
del _FX, _FZ, _la, _lo
def gsample(A, wx, wz, order=1): return ndi.map_coordinates(A, [np.asarray(wz) / GS, np.asarray(wx) / GS], order=order, mode='nearest')
for nm, (la, lo) in {'성도': (30.66, 104.07), '시안': (34.3, 108.9), '타이위안': (37.87, 112.55), '태백산': (33.95, 107.77), '화북평원': (36.0, 116.0), '라싸': (29.65, 91.1), '무위': (37.93, 102.64), '쿤밍': (25.04, 102.7)}.items():
    print('  dem %s = %.1f' % (nm, float(dem_at(np.array([la]), np.array([lo]))[0])))

cc, rr = np.meshgrid(np.arange(W), np.arange(H))
CX = SQ3 * (cc + 0.5 * (rr & 1)) + SQ3 / 2; CZ = 1.5 * rr + 1.0
hlat, hlon = w2ll(CX, CZ)
hE = gsample(E, CX, CZ); hREL = gsample(REL, CX, CZ)
hLAND = gsample(LANDF, CX, CZ) * 0.4
for k in range(6):
    a = math.radians(60 * k); hLAND += gsample(LANDF, CX + 0.6 * math.cos(a), CZ + 0.6 * math.sin(a)) * 0.1
print('  rel percentiles(land)', np.percentile(hREL[hLAND > 0.5], [25, 50, 65, 75, 85, 92]).round(1))

TM, TH = float(os.environ.get('TM', 26)), float(os.environ.get('TH', 9))
T = {}
for r in range(H):
    for c in range(W):
        if hLAND[r, c] < 0.5: t = 's'
        elif hREL[r, c] >= TM or (hE[r, c] >= 95 and hREL[r, c] >= TM * 0.6): t = 'm'
        elif hREL[r, c] >= TH: t = 'h'
        else: t = 'p'
        T[(c, r)] = t

# ---------- 강 ----------
def densify(pts, step=0.3):
    out = [pts[0]]
    for i in range(1, len(pts)):
        (x0, z0), (x1, z1) = pts[i - 1], pts[i]; L = math.hypot(x1 - x0, z1 - z0); n = max(1, int(L / step))
        for k in range(1, n + 1): out.append((x0 + (x1 - x0) * k / n, z0 + (z1 - z0) * k / n))
    return out
def simplify(pts, eps):
    if len(pts) < 3: return pts
    (x0, z0), (x1, z1) = pts[0], pts[-1]; L = math.hypot(x1 - x0, z1 - z0) or 1e-9
    dm, im = 0, 0
    for i in range(1, len(pts) - 1):
        d = abs((pts[i][0] - x0) * (z1 - z0) - (pts[i][1] - z0) * (x1 - x0)) / L
        if d > dm: dm, im = d, i
    if dm <= eps: return [pts[0], pts[-1]]
    return simplify(pts[:im + 1], eps)[:-1] + simplify(pts[im:], eps)
RIVERS = []     # dict(name, major, pts[world])
def add_river(name, major, lonlat):
    a = np.asarray(lonlat, dtype=np.float64)
    wx, wz = ll2w(a[:, 1], a[:, 0])
    pts = list(zip(wx.tolist(), wz.tolist()))
    # 지도 안쪽 구간만
    seg = []
    for p in pts:
        if -4 <= p[0] <= WX + 4 and -4 <= p[1] <= WZ + 4: seg.append(p)
        else:
            if len(seg) > 1: RIVERS.append(dict(name=name, major=major, pts=seg))
            seg = []
    if len(seg) > 1: RIVERS.append(dict(name=name, major=major, pts=seg))
for f in json.load(open(os.path.join(GEO, 'rivers10.geojson')))['features']:
    g = f['geometry']; p = f['properties']; nm = p.get('name')
    if not g or (nm not in MAJOR_RIVERS and nm not in MINOR_RIVERS): continue
    lines = [g['coordinates']] if g['type'] == 'LineString' else g['coordinates']
    for line in lines:
        a = [(x, y) for x, y in line if LL_BOX[0] <= x <= LL_BOX[2] and LL_BOX[1] <= y <= LL_BOX[3]]
        if len(a) < 2: continue
        if nm == 'Huang':
            a = [(x, y) for x, y in a if x <= 113.55]            # 현대 하류는 버린다
            if len(a) < 2: continue
            if abs(a[-1][0] - 113.55) < 0.6: a = a + HAN_HUANGHE[1:]
            elif abs(a[0][0] - 113.55) < 0.6: a = HAN_HUANGHE[::-1][:-1] + a
        add_river(nm, nm in MAJOR_RIVERS, a)
RIVERHEX = set()
for rv in RIVERS:
    if not rv['major']: continue
    for (x, z) in densify(rv['pts'], 0.25):
        h = w2hex(x, z)
        if inmap(*h) and T[h] != 's': T[h] = 'w'; RIVERHEX.add(h)
print('rivers', Counter(r['name'] for r in RIVERS))

# ---------- 거점: 실제 위치 → 최소 간격 보정 → 헥스 ----------
kinds = ['city'] * len(CITY_LL) + ['gate'] * len(GATE_LL)
sizes = [CITY_LL[n][2] for n in CITY_LL] + ['G'] * len(GATE_LL)
P = np.stack(ll2w(ll[:, 0], ll[:, 1]), axis=1)            # 참 위치(월드)
Q = P.copy()
def mind(i, j): return (MIN_CC if kinds[i] == 'city' and kinds[j] == 'city' else MIN_CG) * SQ3
for it in range(600):
    Q += 0.02 * (P - Q) if it < 540 else 0
    for i in range(len(Q)):
        for j in range(i + 1, len(Q)):
            d = Q[i] - Q[j]; L = np.hypot(*d); m = mind(i, j) + 0.3
            if L < m:
                push = (m - L) / 2 * (d / (L or 1)); Q[i] += push; Q[j] -= push
disp = np.hypot(*(Q - P).T) / SQ3
print('base displacement (hex): mean %.2f  max %.2f (%s)  moved>0.5: %d' % (disp.mean(), disp.max(), names[int(disp.argmax())], int((disp > 0.5).sum())))
BASES = []; used = {}
for i, n in enumerate(names):
    h = w2hex(Q[i, 0], Q[i, 1])
    if T[h] in 'sw' or h in used:
        cand = sorted((((center(*v)[0] - Q[i, 0]) ** 2 + (center(*v)[1] - Q[i, 1]) ** 2, v) for d_ in (1, 2, 3) for v in ring(h[0], h[1], d_) if T[v] not in 'sw' and v not in used))
        h = cand[0][1]
    used[h] = n
    BASES.append(dict(name=n, kind=kinds[i], c=h[0], r=h[1], size=sizes[i], true=[round(float(P[i, 0]), 2), round(float(P[i, 1]), 2)], lat=float(ll[i, 0]), lon=float(ll[i, 1])))
BIDX = {b['name']: i for i, b in enumerate(BASES)}
BASEHEX = {(b['c'], b['r']): i for i, b in enumerate(BASES)}
snap = [math.hypot(center(b['c'], b['r'])[0] - P[i, 0], center(b['c'], b['r'])[1] - P[i, 1]) / SQ3 for i, b in enumerate(BASES)]
print('final offset from true position (hex): mean %.2f  median %.2f  max %.2f (%s)  >1.5: %s' % (np.mean(snap), np.median(snap), max(snap), names[int(np.argmax(snap))], [names[i] + ' %.1f' % s for i, s in enumerate(snap) if s > 1.5]))

for b in BASES:
    T[(b['c'], b['r'])] = 'p'
    if b['kind'] == 'city':
        for h in ring(b['c'], b['r'], 1):
            if T[h] in 'mh': T[h] = 'p'
        for h in ring(b['c'], b['r'], 2):
            if T[h] == 'm': T[h] = 'h'
        for h in ring(b['c'], b['r'], 3):
            if T[h] == 'm': T[h] = 'h'

# ---------- 도로(A*) ----------
def vnoise(x, y, s, seed):
    def rnd(i, j):
        n = (i * 374761393 + j * 668265263 + seed * 2147483647) & 0xffffffff
        n = (n ^ (n >> 13)) * 1274126177 & 0xffffffff
        return ((n ^ (n >> 16)) & 0xffff) / 65535.0
    x /= s; y /= s
    i, j = int(math.floor(x)), int(math.floor(y)); fx, fy = x - i, y - j
    fx = fx * fx * (3 - 2 * fx); fy = fy * fy * (3 - 2 * fy)
    a = rnd(i, j) * (1 - fx) + rnd(i + 1, j) * fx; b = rnd(i, j + 1) * (1 - fx) + rnd(i + 1, j + 1) * fx
    return a * (1 - fy) + b * fy
ROAD = set()
COST = {'p': 1.0, 'h': 1.7, 'm': 5.0, 'w': 5.0, 's': 1e9}
def line_dev(h, a, b):
    (x0, y0), (x1, y1), (x2, y2) = center(*h), center(*a), center(*b)
    L = math.hypot(x2 - x1, y2 - y1) or 1.0
    t = max(0.0, min(1.0, ((x0 - x1) * (x2 - x1) + (y0 - y1) * (y2 - y1)) / (L * L)))
    return math.hypot(x0 - (x1 + t * (x2 - x1)), y0 - (y1 + t * (y2 - y1))) / SQ3
def astar(a, b):
    pq = [(0, a)]; g = {a: 0}; prev = {}
    while pq:
        f, u = heapq.heappop(pq)
        if u == b: break
        if f - dist(u, b) * 0.6 > g[u] + 1e-9: continue
        for v in nbrs(*u):
            if v in BASEHEX and v != b: continue
            t = T[v]
            if t == 's': continue
            cst = COST[t]
            if t != 'w':
                vx, vz = center(*v); cst *= 0.7 + 0.9 * vnoise(vx, vz, 11.0, 23) + 0.35 * vnoise(vx, vz, 4.0, 5)
            if v in ROAD: cst = min(cst, 0.55) if t != 'w' else 2.5
            cst += 0.06 * max(0.0, line_dev(v, a, b) - 3.0)
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
    an, bn = e.split('-'); A = BASES[BIDX[an]]; B = BASES[BIDX[bn]]
    p = astar((A['c'], A['r']), (B['c'], B['r']))
    assert p, e
    EDGE_PATHS.append((BIDX[an], BIDX[bn], p))
    for h in p[1:-1]:
        ROAD.add(h)
        if T[h] == 'm': T[h] = 'h'

GATEHEX = [(b['c'], b['r']) for b in BASES if b['kind'] == 'gate']
for h in list(ROAD):                                           # 산길 넓히기
    if any(dist(h, g) <= 2 for g in GATEHEX): continue
    for v in nbrs(*h):
        if T[v] == 'm': T[v] = 'h'

# ---------- 관문 요충 ----------
def passable(h): return T[h] not in 'ms'
def bfs_path(a, b, banned, limit):
    dq = deque([a]); seen = {a: None}; depth = {a: 0}
    while dq:
        u = dq.popleft()
        if u == b: break
        if depth[u] >= limit: continue
        for v in nbrs(*u):
            if v in seen or v in banned or not passable(v): continue
            if v in BASEHEX and v != b: continue
            seen[v] = u; depth[v] = depth[u] + 1; dq.append(v)
    if b not in seen: return None
    path = [b]
    while seen[path[-1]] is not None: path.append(seen[path[-1]])
    return path[::-1]
PROTECT = set()
for b in BASES:
    PROTECT.add((b['c'], b['r']))
    if b['kind'] == 'city':
        for n in (1, 2, 3):
            for h in ring(b['c'], b['r'], n): PROTECT.add(h)
blocked_added = []
for g in BASES:
    if g['kind'] != 'gate': continue
    gh = (g['c'], g['r']); gi = BIDX[g['name']]
    for n in (1, 2):
        for h in ring(gh[0], gh[1], n):
            if h not in ROAD and h not in BASEHEX and T[h] not in 'sw' and h not in PROTECT:
                if T[h] != 'm': blocked_added.append(h)
                T[h] = 'm'
    ends = [x for (a, b2, p) in EDGE_PATHS if gi in (a, b2) for x in (a, b2) if x != gi]
    if len(ends) < 2: continue
    A = BASES[ends[0]]; B = BASES[ends[1]]; ah = (A['c'], A['r']); bh = (B['c'], B['r'])
    direct = dist(ah, gh) + dist(gh, bh)
    for _ in range(60):
        p = bfs_path(ah, bh, {gh}, int(direct * 1.8) + 6)
        if p is None: break
        cand = [h for h in p[1:-1] if h not in ROAD and h not in PROTECT and h not in BASEHEX and T[h] != 'w' and dist(h, gh) <= 7]
        if not cand: break
        cand.sort(key=lambda h: dist(h, gh))
        T[cand[0]] = 'm'; blocked_added.append(cand[0])

# ---------- 부지 ----------
NPLOT = {'L': 10, 'M': 8, 'S': 6}
PLOTS = {}; claimed = set()
for b in BASES:
    if b['kind'] != 'city': continue
    ch = (b['c'], b['r'])
    def ok(h):
        if h in ROAD or h in BASEHEX or h in claimed or T[h] in 'sw': return False
        return all(dist(h, (o['c'], o['r'])) > 1 for o in BASES if (o['c'], o['r']) != ch)
    r1 = [h for h in ring(*ch, 1) if ok(h)]; r2 = [h for h in ring(*ch, 2) if ok(h)]; r3 = [h for h in ring(*ch, 3) if ok(h)]
    free1 = [h for h in ring(*ch, 1) if T[h] not in 'sw']
    road1 = [h for h in free1 if h in ROAD]
    max_r1 = max(0, len(free1) - max(max(2, len(free1) - 3), len(road1)))
    chosen = r1[:max_r1]
    def adjcount(h): return sum(1 for v in nbrs(*h) if v in chosen)
    pool = r2 + r3
    while len(chosen) < NPLOT[b['size']] and pool:
        pool.sort(key=lambda h: (-(adjcount(h) > 0), dist(h, ch), -adjcount(h), hREL[h[1], h[0]]))
        chosen.append(pool.pop(0))
    assert len(chosen) == NPLOT[b['size']], (b['name'], len(chosen))
    for h in chosen: claimed.add(h); T[h] = 'p'
    PLOTS[b['name']] = chosen

# ---------- 변경(비활성) ----------
near = {}; dq = deque()
for h in list(ROAD) + list(BASEHEX) + list(claimed): near[h] = 0; dq.append(h)
while dq:
    u = dq.popleft()
    if near[u] >= VOID_DIST: continue
    for v in nbrs(*u):
        if v not in near: near[v] = near[u] + 1; dq.append(v)
far = set(h for h in T if h not in near)
# 바깥 변경만 남긴다: 지도 가장자리와 땅으로 이어진 먼 땅. 안쪽에 갇힌 먼 땅은 그냥 땅으로 둔다.
VOID = set(h for h in far if (h[0] in (0, W - 1) or h[1] in (0, H - 1)) and T[h] != 's'); dq = deque(VOID)
while dq:
    u = dq.popleft()
    for v in nbrs(*u):
        if v in far and v not in VOID and T[v] != 's': VOID.add(v); dq.append(v)

# ---------- 숲·황무지 ----------
basehexes = [(b['c'], b['r']) for b in BASES]
for (c, r) in list(T):
    h = (c, r)
    if T[h] not in 'ph' or h in ROAD or h in claimed or h in BASEHEX: continue
    x, z = center(c, r); la, lo = hlat[r, c], hlon[r, c]
    n = 0.6 * vnoise(x, z, 9.0, 7) + 0.4 * vnoise(x, z, 3.4, 11)
    arid = max(min((la - 34.5) / 4.0, 1.0), 0.0) * max(min((109.5 - lo) / 5.0, 1.0), 0.0)
    arid = max(arid, max(min((la - 39.8) / 1.5, 1.0), 0.0) * max(min((117.5 - lo) / 3.0, 1.0), 0.0))
    if T[h] == 'p' and arid > 0.05:
        if n > 0.66 - 0.45 * arid: T[h] = 'd'
        continue
    if T[h] == 'p':
        south = max(min((34.0 - la) / 6.0, 1.0), 0.0); ne = 1.0 if (la > 40.3 and lo > 119.5) else 0.0
        thr = 0.70 - 0.10 * south - 0.10 * ne
        if n > thr and all(dist(h, bh) > 1 for bh in basehexes if abs(bh[0] - c) < 4 and abs(bh[1] - r) < 4): T[h] = 'f'
    elif T[h] == 'h':
        south = max(min((34.5 - la) / 5.0, 1.0), 0.0)
        if n > 0.80 - 0.26 * south and arid < 0.05: T[h] = 'f'      # 남쪽 구릉은 숲이 많다

# ---------- 연결성 ----------
start = (BASES[0]['c'], BASES[0]['r']); seen = {start}; dq = deque([start])
while dq:
    u = dq.popleft()
    for v in nbrs(*u):
        if v in seen or T[v] in 'ms' or v in VOID: continue
        seen.add(v); dq.append(v)
unreach = [b['name'] for b in BASES if (b['c'], b['r']) not in seen]
assert not unreach, unreach

# ---------- 출력 ----------
def tt(c, r): return 'x' if (c, r) in VOID and T[(c, r)] != 's' else T[(c, r)]
tstr = ''.join(tt(c, r) for r in range(H) for c in range(W))
rstr = ''.join('1' if (c, r) in ROAD else '0' for r in range(H) for c in range(W))
slim = dict(W=W, H=H, km=round(HW, 2), t=tstr, road=rstr,
            bases=[dict(n=b['name'], k=b['kind'], c=b['c'], r=b['r'], sz=b['size']) for b in BASES],
            edges=[[a, b, len(p) - 1] for (a, b, p) in EDGE_PATHS],
            plots={n: [list(h) for h in v] for n, v in PLOTS.items()})
with open(OUT_JS, 'w', encoding='utf-8') as f:
    f.write('var MAPDATA=' + json.dumps(slim, ensure_ascii=False, separators=(',', ':')) + ';\n')
full = dict(slim, traw=''.join(T[(c, r)] for r in range(H) for c in range(W)), paths=[[list(h) for h in p] for (a, b, p) in EDGE_PATHS],
            rivers=[dict(name=rv['name'], major=rv['major'], pts=[[round(x, 2), round(z, 2)] for x, z in simplify(rv['pts'], 0.12)]) for rv in RIVERS],
            grid=dict(X0=X0, Y0=Y0, U=U, HW=HW, WX=WX, WZ=WZ), basesFull=BASES, blocked=[list(h) for h in blocked_added])
with open(OUT_JSON, 'w', encoding='utf-8') as f: json.dump(full, f, ensure_ascii=False)

cnt = Counter(tstr); n_all = W * H
print('terrain', {k: '%d (%.1f%%)' % (v, 100.0 * v / n_all) for k, v in cnt.most_common()})
play = [ch for ch in tstr if ch not in 'xs']; pc = Counter(play)
print('playable %d: %s' % (len(play), {k: '%.1f%%' % (100.0 * v / len(play)) for k, v in pc.most_common()}))
lens = [len(p) - 1 for _, _, p in EDGE_PATHS]
print('roads %d hexes, edges %d: len median %d  min %d  max %d' % (len(ROAD), len(lens), int(np.median(lens)), min(lens), max(lens)))
print('edge lens', ' '.join('%s-%s:%d' % (BASES[a]['name'], BASES[b]['name'], len(p) - 1) for a, b, p in EDGE_PATHS))
print('blocked', len(blocked_added))

# ---------- 디버그 그림 ----------
SC = 4.0
im = Image.new('RGB', (int(WX * SC), int(WZ * SC)), (20, 30, 60)); d = ImageDraw.Draw(im)
COL = {'p': (196, 200, 140), 'h': (170, 150, 95), 'm': (105, 80, 60), 'w': (60, 120, 220), 's': (30, 60, 130), 'f': (70, 130, 70), 'd': (225, 205, 150), 'x': (60, 58, 55)}
def poly(c, r, k=1.0):
    x, z = center(c, r)
    return [((x + k * math.cos(math.radians(60 * i - 30))) * SC, (z + k * math.sin(math.radians(60 * i - 30))) * SC) for i in range(6)]
for r in range(H):
    for c in range(W):
        t = tt(c, r); col = COL[t]
        if t == 'x':
            raw = COL[T[(c, r)]]; col = tuple(int(v * 0.45) for v in raw)
        d.polygon(poly(c, r), fill=col)
        if (c, r) in ROAD: d.polygon(poly(c, r, 0.5), fill=(150, 40, 20))
for n, v in PLOTS.items():
    for h in v: d.polygon(poly(*h, k=0.7), fill=(255, 255, 255))
for rv in RIVERS:
    if not rv['major']: d.line([(x * SC, z * SC) for x, z in rv['pts']], fill=(90, 150, 240), width=1)
try: font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 13)
except Exception: font = None
for i, b in enumerate(BASES):
    x, z = center(b['c'], b['r']); col = (255, 230, 0) if b['kind'] == 'city' else (255, 60, 60)
    d.ellipse([x * SC - 5, z * SC - 5, x * SC + 5, z * SC + 5], fill=col, outline=(0, 0, 0))
    d.text((x * SC + 6, z * SC - 7), str(i), fill=(255, 255, 255), font=font)
im.save(OUT_DBG)
