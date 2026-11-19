# -*- coding: utf-8 -*-
"""천하도 v0.4 — 3D 지형 굽기(수묵): 높이맵은 v0.2와 같고, 바탕 텍스처만 먹의 농담으로 칠한다.
사용: bake3d.py <geo_dir> <mapdata.json> <out terrain.jpg> <out map3d.js> [TEXW]
"""
import sys, os, json, math, base64, io
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo import lcc_inv

GEO, MAPJSON, OUT_TEX, OUT_JS = sys.argv[1:5]
TEXW = int(sys.argv[5]) if len(sys.argv) > 5 else 3072
Image.MAX_IMAGE_PIXELS = None
SQ3 = math.sqrt(3)
M = json.load(open(MAPJSON, encoding='utf-8'))
W, H = M['W'], M['H']; G = M['grid']; WX, WZ = G['WX'], G['WZ']
PPU = TEXW / WX; TEXH = int(round(WZ * PPU))
print('texture %dx%d  %.2f px/unit  %.1f px/hex' % (TEXW, TEXH, PPU, PPU * SQ3))
f32 = np.float32

def center(c, r): return (SQ3 * (c + 0.5 * (r & 1)) + SQ3 / 2, 1.5 * r + 1.0)
def hexpoly(c, r, k=1.0):
    x, z = center(c, r)
    return [((x + k * math.cos(math.radians(60 * i - 30))) * PPU, (z + k * math.sin(math.radians(60 * i - 30))) * PPU) for i in range(6)]

# ---------- 지형 분류 래스터 ----------
CLS = {'p': 0, 'f': 1, 'h': 2, 'm': 3, 'd': 4, 'w': 5, 's': 6}
cim = Image.new('L', (TEXW, TEXH), 0); cd = ImageDraw.Draw(cim)
vim = Image.new('L', (TEXW, TEXH), 0); vd = ImageDraw.Draw(vim)
rim = Image.new('L', (TEXW, TEXH), 0); rd = ImageDraw.Draw(rim)     # 거점·부지 주변(평탄)
for r in range(H):
    for c in range(W):
        t = M['traw'][r * W + c]; pl = hexpoly(c, r, 1.03)
        if CLS[t]: cd.polygon(pl, fill=CLS[t])
        if M['t'][r * W + c] == 'x': vd.polygon(pl, fill=255)
for b in M['bases']: rd.polygon(hexpoly(b['c'], b['r'], 1.6), fill=255)
for n, v in M['plots'].items():
    for (c, r) in v: rd.polygon(hexpoly(c, r, 1.05), fill=255)
cls = np.asarray(cim)

def vnoise(cell, seed, shape=(TEXH, TEXW)):
    rs = np.random.RandomState(seed)
    gh, gw = int(shape[0] / cell) + 4, int(shape[1] / cell) + 4
    z = ndi.zoom(rs.rand(gh, gw).astype(f32), cell, order=3)
    return np.clip(z[int(cell):int(cell) + shape[0], int(cell):int(cell) + shape[1]], 0, 1)
def fbm(cell, seed, octs=4, ridged=False):
    out = np.zeros((TEXH, TEXW), f32); amp = 1.0; tot = 0.0
    for o in range(octs):
        n = vnoise(max(2.0, cell / 2 ** o), seed + o * 17)
        if ridged: n = 1.0 - np.abs(2.0 * n - 1.0); n *= n
        out += amp * n; tot += amp; amp *= 0.5
    return out / tot

# 경계를 흐트러뜨린 뒤 부드럽게
yy, xx = np.mgrid[0:TEXH, 0:TEXW].astype(f32)
wamp = PPU * 0.42
wx_ = xx + (vnoise(PPU * 1.3, 101) - 0.5) * 2 * wamp; wy_ = yy + (vnoise(PPU * 1.3, 102) - 0.5) * 2 * wamp
clsw = ndi.map_coordinates(cls, [wy_, wx_], order=0, mode='nearest')
del wx_, wy_
SIG = PPU * 0.36
def mask(v, sig=SIG, src=None): return ndi.gaussian_filter(((clsw if src is None else src) == v).astype(f32), sig)
Mm, Mh, Mf, Md = mask(3), mask(2), mask(1), mask(4)
_lm = np.load(os.path.join(os.path.dirname(MAPJSON), 'landmask.npy'))
_zy, _zx = np.mgrid[0:TEXH, 0:TEXW].astype(f32)
_land = ndi.map_coordinates(_lm, [_zy / PPU / 0.2, _zx / PPU / 0.2], order=1, mode='nearest'); del _zy, _zx
_land = ndi.gaussian_filter(_land, PPU * 0.10) + (vnoise(PPU * 0.5, 444) - 0.5) * 0.25
Ms = ndi.gaussian_filter((_land < 0.5).astype(f32), PPU * 0.12); del _land
Mw = ndi.gaussian_filter((cls == 5).astype(f32), PPU * 0.30)
Mvoid = ndi.gaussian_filter(np.asarray(vim, dtype=f32) / 255.0, PPU * 0.9)
Mbase = ndi.gaussian_filter(np.asarray(rim, dtype=f32) / 255.0, PPU * 0.5)

# ---------- 고도 ----------
dem = np.asarray(Image.open(os.path.join(GEO, 'elev_bump_4k.jpg')).convert('L'), dtype=f32)
q = 4
qy, qx = np.mgrid[0:TEXH:q, 0:TEXW:q].astype(np.float64)
lat, lon = lcc_inv(G['X0'] + (qx + q / 2) / PPU * G['U'], G['Y0'] - (qy + q / 2) / PPU * G['U'])
E = ndi.map_coordinates(dem, [(90.0 - lat) / 180.0 * dem.shape[0] - 0.5, (lon + 180.0) / 360.0 * dem.shape[1] - 0.5], order=1, mode='nearest')
def up(a): return ndi.zoom(a.astype(f32), q, order=1)[:TEXH, :TEXW]
ELEV = np.clip((up(ndi.gaussian_filter(E, 1.0)) - 24.5) * 30.0, 0, None)          # m (근사)
LATM = up(lat); LONM = up(lon)
B_raw = 0.03 + 1.45 * (ELEV / 4000.0) ** 0.85
B = ndi.gaussian_filter(B_raw, PPU * 1.6)
ridge = fbm(PPU * 2.6, 7, 5, ridged=True)
n_mid = fbm(PPU * 1.8, 31, 4)
n_fine = fbm(PPU * 0.5, 57, 3)
flat = 1.0 - 0.85 * Mbase
HGT = B + (B_raw - B) * (0.6 + 1.2 * Mm) * flat
HGT += Mm * (0.26 + 0.95 * ridge ** 1.25) * flat
HGT += Mh * (0.04 + 0.20 * n_mid) * flat
HGT += 0.012 * (n_fine - 0.5)
HGT -= 0.06 * Mw
HGT = HGT * (1 - Ms) + (-0.22) * Ms
HGT = ndi.gaussian_filter(HGT, 0.8)
print('height range %.2f .. %.2f' % (HGT.min(), HGT.max()))

# ---------- 음영 ----------
gy, gx = np.gradient(HGT); gy *= PPU; gx *= PPU
ZX = 1.15
nx, ny, nz = -gx * ZX, np.ones_like(gx), -gy * ZX
nl = np.sqrt(nx * nx + ny * ny + nz * nz)
L = np.array([-0.55, 0.62, -0.56]); L /= np.linalg.norm(L)
shade = (nx * L[0] + ny * L[1] + nz * L[2]) / nl
shade = np.clip(0.50 + 0.80 * (shade - L[1]) / max(1e-6, 1 - L[1]) * 0.5 + 0.5 * (shade / L[1]), 0.52, 1.24)
occ = np.clip(1.0 + 1.2 * (HGT - ndi.gaussian_filter(HGT, PPU * 0.8)), 0.78, 1.12)
del gx, gy, nx, ny, nz, nl

# ---------- 색: 수묵담채 ----------
# 종이 바탕 위에 먹의 농담으로 지형을 올린다. 평지는 여백, 산은 준법(皴法) 같은 마른 붓 결과 그늘, 숲은 먹점, 물은 비워 두고 물가만 선과 번짐.
def C(r, g, b): return np.array([r, g, b], f32) / 255.0
PAPER = C(239, 233, 219); INKC = C(30, 28, 26)
south = np.clip((34.5 - LATM) / 7.0, 0, 1)
arid = np.clip(np.clip((LATM - 34.0) / 5.0, 0, 1) * np.clip((110.5 - LONM) / 6.0, 0, 1) + np.clip((LATM - 39.5) / 2.5, 0, 1) * np.clip((118.0 - LONM) / 4.0, 0, 1), 0, 1)
hi = np.clip((HGT - B) / 1.0, 0, 1)
blot = vnoise(PPU * 1.1, 201)                                   # 번짐의 얼룩
blot2 = vnoise(PPU * 3.2, 202)
dry = fbm(PPU * 0.22, 203, 2)                                   # 마른 붓의 갈라짐
sh = np.clip((1.02 - shade) / 0.50, 0, 1)                       # 빛 반대쪽 비탈
lit = np.clip((shade - 1.02) / 0.22, 0, 1)
D = np.zeros((TEXH, TEXW), f32)
# 산: 그늘 + 능선 결 + 마른 붓. 산자락은 안개처럼 비운다
rl = np.clip((ridge - 0.60) / 0.26, 0, 1)
mt = (0.16 + 0.62 * sh ** 0.85 + 0.30 * rl * (0.45 + 0.55 * sh)) * (0.40 + 0.60 * np.clip(hi * 1.25 + 0.12, 0, 1))
mt *= 0.62 + 0.62 * blot
mt = mt * (0.66 + 0.34 * np.clip((dry - 0.28) / 0.30, 0, 1))
mt *= 1.0 - 0.55 * lit
snow = np.clip((ELEV + 900 * hi - 4500) / 500.0, 0, 1)
mt *= 1.0 - 0.85 * snow
# 덧칠한 먹의 층: 농담을 몇 단으로 끊고, 층의 가장자리(물 마른 자국)를 조금 짙게
lay = np.floor(np.clip(mt, 0, 1) * 4.0 + 0.35 * (blot - 0.5)) / 4.0
lay = ndi.gaussian_filter(lay, 0.7)
gyl, gxl = np.gradient(lay)
wet = np.clip(np.sqrt(gxl * gxl + gyl * gyl) * 9.0, 0, 1)
mt = 0.45 * mt + 0.55 * lay + 0.10 * wet
del gyl, gxl, lay
# 능선: 높이의 볼록한 줄기를 가는 붓선으로
Hr = ndi.gaussian_filter(HGT, 1.1)
curv = -ndi.laplace(Hr)
crest = np.clip((curv - 0.004) / 0.010, 0, 1) * np.clip(hi * 1.6, 0, 1)
crest = ndi.gaussian_filter(crest, 0.6) * (0.45 + 0.75 * dry)
mt = mt + 0.42 * crest
del Hr, curv
D += Mm * mt
edge_m = np.clip(1 - np.abs(Mm - 0.42) / 0.20, 0, 1) * np.clip(sh * 1.4 + 0.25, 0, 1)      # 번진 가장자리가 짙게 마른 자국
D += 0.16 * edge_m * (0.5 + blot)
# 구릉: 옅은 번짐과 그늘
D += Mh * (1 - Mm) * (0.06 + 0.30 * sh + 0.10 * np.clip((n_mid - 0.52) / 0.2, 0, 1)) * (0.6 + 0.7 * blot)
# 숲: 먹점(米點). 남쪽일수록 촘촘
rsd = np.random.RandomState(13)
imp = (rsd.rand(TEXH, TEXW) < (0.050 + 0.022 * south)).astype(f32)                 # 점을 찍을 자리
imp *= (0.55 + 0.9 * rsd.rand(TEXH, TEXW)).astype(f32)                             # 점마다 먹의 양이 다르다
dab = np.clip(ndi.gaussian_filter(imp, 1.15) * 9.5 - 0.42, 0, 1)
dab2 = np.clip(ndi.gaussian_filter(np.roll(imp, (3, 2), (0, 1)), 2.1) * 22.0 - 0.55, 0, 1)   # 번진 옅은 점
D += Mf * (1 - Mm) * (0.05 + 0.62 * dab * (0.75 + 0.4 * blot2) + 0.16 * dab2)
del imp
# 황무지: 성긴 점
st = np.clip((fbm(PPU * 0.16, 77, 2) - 0.66) / 0.08, 0, 1)
D += Md * (0.03 + 0.20 * st)
# 평지: 거의 여백. 아주 옅은 얼룩만
D += (1 - np.clip(Mm + Mh + Mf + Md, 0, 1)) * 0.035 * blot2
D *= 1.0 - 0.80 * Mbase                                          # 성과 부지 둘레는 비워 둔다
D = np.clip(D, 0, 1) ** 1.12
col = PAPER[None, None, :] * (1 - D[..., None]) + INKC[None, None, :] * D[..., None]
# 담채: 숲과 남쪽 산에 녹청, 북서의 마른 땅에 황토를 아주 옅게
gk = np.clip(Mf * 0.20 + Mm * south * 0.10 + Mh * south * 0.06, 0, 0.26) * (0.6 + 0.8 * blot2)
col = col * (1 - gk[..., None]) + (col * C(150, 188, 160)[None, None, :] / PAPER[None, None, :]) * gk[..., None]
ok = np.clip(arid * 0.16 * (0.5 + blot2), 0, 0.22)
col = col * (1 - ok[..., None]) + (col * C(226, 196, 142)[None, None, :] / PAPER[None, None, :]) * ok[..., None]

def smooth(pts, it=2):
    for _ in range(it):
        out = [pts[0]]
        for i in range(len(pts) - 1):
            (x0, z0), (x1, z1) = pts[i], pts[i + 1]
            out.append((0.75 * x0 + 0.25 * x1, 0.75 * z0 + 0.25 * z1)); out.append((0.25 * x0 + 0.75 * x1, 0.25 * z0 + 0.75 * z1))
        out.append(pts[-1]); pts = out
    return pts
ROADS = [smooth([center(c, r) for c, r in p]) for p in M['paths']]
SS = 2
# 물: 작은 강은 가는 쪽빛 먹선, 큰 강·호수·바다는 종이를 비우고 물가에 선과 번짐
ov = Image.new('L', (TEXW * SS, TEXH * SS), 0); od = ImageDraw.Draw(ov)
for rv in M['rivers']:
    if not rv['major']: od.line([(x * PPU * SS, z * PPU * SS) for x, z in smooth([tuple(p) for p in rv['pts']], 1)], fill=255, width=max(2, int(PPU * 0.13 * SS)), joint='curve')
minor = np.asarray(ov.resize((TEXW, TEXH), Image.LANCZOS), dtype=f32) / 255.0 * (1 - np.clip(Mm * 0.5, 0, 1))
ov = Image.new('L', (TEXW * SS, TEXH * SS), 0); od = ImageDraw.Draw(ov)
for rv in M['rivers']:
    if rv['major']: od.line([(x * PPU * SS, z * PPU * SS) for x, z in smooth([tuple(p) for p in rv['pts']], 1)], fill=255, width=int(PPU * 0.95 * SS), joint='curve')
major = ndi.gaussian_filter(np.asarray(ov.resize((TEXW, TEXH), Image.LANCZOS), dtype=f32) / 255.0, 1.2)
del ov
WATERC = C(232, 232, 226); INDIGO = C(96, 124, 146)
mk = (0.50 * minor * (0.7 + 0.5 * blot))[..., None]
col = col * (1 - mk) + INDIGO[None, None, :] * 0.72 * mk
rb = np.clip(major * 1.25, 0, 1)[..., None]
col = col * (1 - rb) + (WATERC * 0.985)[None, None, :] * rb
bankl = np.clip(1 - np.abs(major - 0.46) / 0.22, 0, 1) ** 1.5 * (0.45 + 0.5 * blot)             # 강기슭 먹선
col = col * (1 - 0.62 * bankl[..., None]) + INKC[None, None, :] * (0.62 * bankl[..., None])
rw = np.clip(major - 0.6, 0, 1)[..., None] * 0.10                                               # 강 한가운데 옅은 쪽빛
col = col * (1 - rw) + INDIGO[None, None, :] * rw
sm = np.clip(Ms * 1.5 - 0.25, 0, 1)
deep = np.clip(ndi.gaussian_filter(Ms, PPU * 2.6) * 1.7 - 0.6, 0, 1)
near = np.clip(ndi.gaussian_filter(Ms, PPU * 0.9) * 2.0 - 0.15, 0, 1) * (1 - deep)             # 물가에서 바깥으로 번지는 띠
waves = np.clip((np.sin(yy / (PPU * 0.33) + 5.0 * vnoise(PPU * 2.4, 301)) - 0.93) / 0.07, 0, 1) * (0.35 + 0.65 * vnoise(PPU * 1.6, 302)) * np.clip(deep * 1.4 + 0.2, 0, 1)
seac = WATERC[None, None, :] * (1 - (0.10 * near + 0.05 * deep)[..., None]) 
seac = seac * (1 - (0.16 * near + 0.07 * deep)[..., None]) + INDIGO[None, None, :] * (0.16 * near + 0.07 * deep)[..., None]
seac = seac * (1 - 0.20 * waves[..., None]) + INDIGO[None, None, :] * (0.20 * waves[..., None])
col = col * (1 - sm[..., None]) + seac * sm[..., None]
shore = np.clip(1 - np.abs(ndi.gaussian_filter(Ms, PPU * 0.10) - 0.36) / 0.13, 0, 1) ** 1.6 * (0.5 + 0.5 * blot)     # 해안 먹선
col = col * (1 - 0.70 * shore[..., None]) + INKC[None, None, :] * (0.70 * shore[..., None])

# 변경(갈 수 없는 땅): 안개 속으로 — 옅게 비운다
vk = np.clip(Mvoid * 1.15, 0, 1)[..., None] * 0.72
col = col * (1 - vk) + (PAPER * 0.992)[None, None, :] * vk
# 종이 결
col *= (0.985 + 0.03 * n_fine)[..., None]

img = Image.fromarray(np.clip(col * 255.0, 0, 255).astype(np.uint8), 'RGB').filter(ImageFilter.UnsharpMask(1.2, 30, 2))
img.save(OUT_TEX, quality=84, optimize=True, subsampling=1)
print('texture bytes', os.path.getsize(OUT_TEX))
mini = img.resize((220, int(round(220 * TEXH / TEXW))), Image.LANCZOS); mb = io.BytesIO(); mini.save(mb, 'JPEG', quality=72)

# ---------- 높이맵(메시용) ----------
GX = 2 * W + 2; GZ = int(round(WZ / (WX / (GX - 1)))) + 1
Hs = ndi.gaussian_filter(HGT, PPU * 0.22)
ix = np.linspace(0, TEXW - 1, GX); iz = np.linspace(0, TEXH - 1, GZ)
IZ, IX = np.meshgrid(iz, ix, indexing='ij')
HM = ndi.map_coordinates(Hs, [IZ, IX], order=1, mode='nearest')
hmin, hmax = float(HM.min()), float(HM.max())
hm16 = np.round((HM - hmin) / (hmax - hmin) * 65535.0).astype('<u2')
out = dict(WX=round(WX, 4), WZ=round(WZ, 4), GX=GX, GZ=GZ, hmin=round(hmin, 4), hmax=round(hmax, 4),
           hm=base64.b64encode(hm16.tobytes()).decode('ascii'),
           roads=[[round(v, 2) for p in pts for v in p] for pts in ROADS],
           mini='data:image/jpeg;base64,' + base64.b64encode(mb.getvalue()).decode('ascii'))
with open(OUT_JS, 'w', encoding='utf-8') as f: f.write('var MAP3D=' + json.dumps(out, separators=(',', ':')) + ';\n')
print('mesh grid %dx%d  h %.2f..%.2f  map3d.js %d bytes' % (GX, GZ, hmin, hmax, os.path.getsize(OUT_JS)))
