# -*- coding: utf-8 -*-
"""천하도 v0.2 — 3D 지형 굽기: 높이맵 + 바탕 텍스처 + 강·도로 선.
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

# ---------- 색 ----------
def C(r, g, b): return np.array([r, g, b], f32) / 255.0
def lerp3(a, b, t): return a[None, None, :] * (1 - t[..., None]) + b[None, None, :] * t[..., None]
south = np.clip((34.5 - LATM) / 7.0, 0, 1)
arid = np.clip(np.clip((LATM - 34.0) / 5.0, 0, 1) * np.clip((110.5 - LONM) / 6.0, 0, 1) + np.clip((LATM - 39.5) / 2.5, 0, 1) * np.clip((118.0 - LONM) / 4.0, 0, 1), 0, 1)
moist = np.clip(south * 0.8 + 0.4 * (vnoise(PPU * 6, 88) - 0.5), 0, 1)
col = lerp3(C(166, 172, 106), C(122, 156, 84), moist)                      # 평지: 북쪽 밀밭빛 ↔ 남쪽 초록
col = col * (1 - arid[..., None] * 0.75) + C(205, 182, 128)[None, None, :] * (arid[..., None] * 0.75)
col *= (0.90 + 0.20 * vnoise(PPU * 2.2, 5))[..., None]
hillc = lerp3(C(158, 142, 92), C(112, 132, 74), np.clip(south * 0.9, 0, 1))
hillc = hillc * (1 - arid[..., None] * 0.7) + C(196, 168, 116)[None, None, :] * (arid[..., None] * 0.7)
col = col * (1 - Mh[..., None]) + hillc * Mh[..., None]
forc = lerp3(C(76, 108, 62), C(52, 96, 52), south) * (0.80 + 0.40 * fbm(PPU * 0.45, 13, 2))[..., None]
col = col * (1 - Mf[..., None]) + forc * Mf[..., None]
col = col * (1 - Md[..., None]) + (C(214, 190, 136)[None, None, :] * (0.90 + 0.2 * n_mid)[..., None]) * Md[..., None]
hi = np.clip((HGT - B) / 1.0, 0, 1)
rock = lerp3(C(126, 112, 88), C(152, 142, 124), np.clip(hi * 0.9 + (ELEV - 1500) / 5000.0, 0, 1))
rock = rock * (1 - (south * 0.45 * (1 - hi))[..., None]) + C(86, 108, 70)[None, None, :] * (south * 0.45 * (1 - hi))[..., None]   # 남쪽 산은 숲이 덮는다
snow = np.clip((ELEV + 900 * hi - 4500) / 500.0, 0, 1) * Mm
rock = rock * (1 - snow[..., None]) + C(238, 240, 244)[None, None, :] * snow[..., None]
col = col * (1 - Mm[..., None]) + rock * Mm[..., None]
col *= (shade * occ)[..., None]
col *= (0.94 + 0.12 * n_fine)[..., None]

# 길(희미하게) — 선명한 길은 런타임에 띠로 그린다
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
ov = Image.new('L', (TEXW * SS, TEXH * SS), 0); od = ImageDraw.Draw(ov)
for pts in ROADS: od.line([(x * PPU * SS, z * PPU * SS) for x, z in pts], fill=255, width=max(2, int(PPU * 0.20 * SS)), joint='curve')
roadm = np.asarray(ov.resize((TEXW, TEXH), Image.LANCZOS), dtype=f32) / 255.0
col = col * (1 - 0.62 * roadm[..., None]) + C(196, 170, 124)[None, None, :] * (0.62 * roadm[..., None])

# 물: 작은 강(선) → 큰 강·호수·바다
ov = Image.new('L', (TEXW * SS, TEXH * SS), 0); od = ImageDraw.Draw(ov)
for rv in M['rivers']:
    if not rv['major']: od.line([(x * PPU * SS, z * PPU * SS) for x, z in smooth([tuple(p) for p in rv['pts']], 1)], fill=255, width=max(2, int(PPU * 0.22 * SS)), joint='curve')
minor = np.asarray(ov.resize((TEXW, TEXH), Image.LANCZOS), dtype=f32) / 255.0 * (1 - np.clip(Mm * 0.5, 0, 1))
ov = Image.new('L', (TEXW * SS, TEXH * SS), 0); od = ImageDraw.Draw(ov)
for rv in M['rivers']:
    if rv['major']: od.line([(x * PPU * SS, z * PPU * SS) for x, z in smooth([tuple(p) for p in rv['pts']], 1)], fill=255, width=int(PPU * 0.95 * SS), joint='curve')
major = ndi.gaussian_filter(np.asarray(ov.resize((TEXW, TEXH), Image.LANCZOS), dtype=f32) / 255.0, 1.2)
del ov
wn = 0.92 + 0.16 * vnoise(PPU * 0.8, 71)
rivc = C(74, 128, 156)[None, None, :] * wn[..., None]
bank = np.clip(ndi.gaussian_filter(major, PPU * 0.35) * 1.6 - major, 0, 1)
col = col * (1 - 0.28 * bank[..., None]) + C(196, 186, 140)[None, None, :] * (0.28 * bank[..., None])
col = col * (1 - 0.85 * minor[..., None]) + rivc * (0.85 * minor[..., None])
col = col * (1 - major[..., None]) + rivc * major[..., None]
deep = np.clip(ndi.gaussian_filter(Ms, PPU * 2.6) * 1.7 - 0.6, 0, 1)
seac = lerp3(C(92, 150, 160), C(38, 84, 118), deep) * wn[..., None]
sm = np.clip(Ms * 1.5 - 0.25, 0, 1)
shore = np.clip(1 - np.abs(ndi.gaussian_filter(Ms, PPU * 0.18) - 0.30) / 0.22, 0, 1)
col = col * (1 - 0.35 * shore[..., None]) + C(226, 212, 170)[None, None, :] * (0.35 * shore[..., None])
col = col * (1 - sm[..., None]) + seac * sm[..., None]

# 변경: 채도를 빼고 어둡게
gray = col.mean(axis=2, keepdims=True)
vcol = (col * 0.35 + gray * 0.65) * 0.60 + C(22, 20, 18)[None, None, :]
vk = np.clip(Mvoid * 1.15, 0, 1)[..., None] * 0.92
col = col * (1 - vk) + vcol * vk

img = Image.fromarray(np.clip(col * 255.0, 0, 255).astype(np.uint8), 'RGB').filter(ImageFilter.UnsharpMask(1.6, 55, 2))
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
