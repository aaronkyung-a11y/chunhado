#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.20 바탕 그림 손질 — 다시 굽지 않고 0.19.1 의 그림(build/terrain.v0191.jpg) 위에 덧칠한다.
 (1) 물: 큰 강 · 호수 · 바다에 쪽빛 담채를 올린다(전에는 종이를 비운 잿빛이라 물인지 알기 어려웠다). 바다에는 물결 선, 작은 강은 쪽빛 선을 짙게.
 (2) 높낮이: 높이맵(MAP3D.hm)에서 높이 0.3 마다 한 겹씩 옅은 대자(代赭)빛을 올리고 겹의 경계에 가는 먹선(등고선)을 긋는다.
     0.3 = 높이 3단 = 전투에서 치는 높이 차의 끝(ELEV_K.max). 겹 하나를 넘으면 '높은 곳'의 덕을 끝까지 본다.
 (3) 새 성(홍농)과 그 부지 둘레의 먹을 걷어 낸다(다른 성처럼 여백으로).
 미니맵(MAP3D.mini)도 새 그림으로 바꾼다.
usage: terrain20.py <build/terrain.v0191.jpg> <build/mapdata.json> <src/map3d.js> <out build/terrain.jpg> [새 거점 이름 …]"""
import sys, os, json, math, base64, io, re
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi
SRC, MAPJSON, M3, OUT = sys.argv[1:5]; NEWB = sys.argv[5:]
Image.MAX_IMAGE_PIXELS = None
f32 = np.float32; SQ3 = math.sqrt(3)
M = json.load(open(MAPJSON, encoding='utf-8')); W, H = M['W'], M['H']; G = M['grid']; WX, WZ = G['WX'], G['WZ']
col = np.asarray(Image.open(SRC).convert('RGB'), dtype=f32) / 255.0
TEXH, TEXW = col.shape[:2]; PPU = TEXW / WX
def C(r, g, b): return np.array([r, g, b], f32) / 255.0
PAPER = C(239, 233, 219); INKC = C(30, 28, 26); WATERC = C(229, 230, 224); INDIGO = C(74, 112, 140)
WASH = C(158, 196, 210)                                       # 쪽빛 담채(물)
OCHRE = C(196, 158, 112)                                      # 대자빛 담채(높은 땅)
def center(c, r): return (SQ3 * (c + 0.5 * (r & 1)) + SQ3 / 2, 1.5 * r + 1.0)
def hexpoly(c, r, k=1.0):
    x, z = center(c, r)
    return [((x + k * math.cos(math.radians(60 * i - 30))) * PPU, (z + k * math.sin(math.radians(60 * i - 30))) * PPU) for i in range(6)]
def vnoise(cell, seed, shape=(TEXH, TEXW)):
    rs = np.random.RandomState(seed)
    gh, gw = int(shape[0] / cell) + 4, int(shape[1] / cell) + 4
    z = ndi.zoom(rs.rand(gh, gw).astype(f32), cell, order=3)
    return np.clip(z[int(cell):int(cell) + shape[0], int(cell):int(cell) + shape[1]], 0, 1)
def smooth(pts, it=2):
    for _ in range(it):
        out = [pts[0]]
        for i in range(len(pts) - 1):
            (x0, z0), (x1, z1) = pts[i], pts[i + 1]
            out.append((0.75 * x0 + 0.25 * x1, 0.75 * z0 + 0.25 * z1)); out.append((0.25 * x0 + 0.75 * x1, 0.25 * z0 + 0.75 * z1))
        out.append(pts[-1]); pts = out
    return pts
def sstep(a, b, x): t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)
def tint(col, target, base, a): return col * (1 - a[..., None]) + (col * (target / base)[None, None, :]) * a[..., None]
def mix(col, target, a): return col * (1 - a[..., None]) + target[None, None, :] * a[..., None]

# ---------- 가림판 ----------
vim = Image.new('L', (TEXW, TEXH), 0); vd = ImageDraw.Draw(vim)
mim = Image.new('L', (TEXW, TEXH), 0); md = ImageDraw.Draw(mim)
for r in range(H):
    for c in range(W):
        t = M['t'][r * W + c]
        if t == 'x': vd.polygon(hexpoly(c, r, 1.03), fill=255)
        elif t == 'm': md.polygon(hexpoly(c, r, 1.03), fill=255)
Mvoid = np.clip(ndi.gaussian_filter(np.asarray(vim, dtype=f32) / 255.0, PPU * 0.9) * 1.15, 0, 1)
Mm = ndi.gaussian_filter(np.asarray(mim, dtype=f32) / 255.0, PPU * 0.36)
blot = vnoise(PPU * 1.1, 201)

# ---------- (3) 새 성 둘레의 먹을 걷는다 ----------
if NEWB:
    rim = Image.new('L', (TEXW, TEXH), 0); rdw = ImageDraw.Draw(rim)
    for b in M['bases']:
        if b['n'] in NEWB:
            rdw.polygon(hexpoly(b['c'], b['r'], 1.6), fill=255)
            for (c, r) in M['plots'].get(b['n'], []): rdw.polygon(hexpoly(c, r, 1.05), fill=255)
    Mb = ndi.gaussian_filter(np.asarray(rim, dtype=f32) / 255.0, PPU * 0.5)
    col = PAPER[None, None, :] - (PAPER[None, None, :] - col) * (1 - 0.80 * Mb)[..., None]
    print('cleared around', NEWB, 'px', int((Mb > 0.5).sum()))

# ---------- (2) 높낮이 ----------
s3 = open(M3, encoding='utf-8').read(); m3 = re.match(r'^(var MAP3D\s*=\s*)(.*?)(;\s*)$', s3, re.S); D3 = json.loads(m3.group(2))
GX, GZ = D3['GX'], D3['GZ']
hm = np.frombuffer(base64.b64decode(D3['hm']), dtype='<u2').astype(f32).reshape(GZ, GX)
hm = D3['hmin'] + hm * (D3['hmax'] - D3['hmin']) / 65535.0
zy, zx = np.mgrid[0:TEXH, 0:TEXW].astype(f32)
Hh = ndi.map_coordinates(hm, [(zy + 0.5) / PPU / WZ * (GZ - 1), (zx + 0.5) / PPU / WX * (GX - 1)], order=1, mode='nearest')
Hh = ndi.gaussian_filter(Hh, 1.6)
STEP = 0.30
lv = np.clip(np.floor(Hh / STEP), 0, 9)                       # 겹(0 = 낮은 땅)
gy, gx = np.gradient(Hh); gr = np.sqrt(gx * gx + gy * gy) + 1e-5
fr = Hh / STEP - np.floor(Hh / STEP); dpx = np.minimum(fr, 1 - fr) * STEP / gr      # 가장 가까운 겹 경계까지(그림 점)
land = (1 - Mvoid) * sstep(-0.10, -0.02, Hh)
edge = sstep(0.0, 1.2, STEP * 0.5 / gr)                       # 겹 경계가 그림 한 점보다 촘촘한 곳(가파른 산)은 선을 긋지 않는다
band = sstep(0.75, 0.0, dpx)                                  # 겹의 경계에서 살짝 진해지는 띠(번짐)
a_h = np.clip(0.105 * lv, 0, 0.52) * (0.82 + 0.36 * blot) * land * (1 - 0.50 * Mm)
col = tint(col, OCHRE, PAPER, a_h.astype(f32))
line = sstep(1.05, 0.25, dpx) * edge * (Hh > STEP * 0.6) * land * (1 - 0.70 * Mm) * (0.55 + 0.45 * blot)
col = mix(col, INKC, (0.40 * line + 0.06 * band * edge * land * (lv > 0)).astype(f32))
print('height layers: share of land by level', [round(float(((lv == i) * (land > 0.5)).sum() / max(1.0, (land > 0.5).sum())), 3) for i in range(8)])
del gy, gx, gr, fr, dpx, band, line, a_h

# ---------- (1) 물 ----------
_lm = np.load(os.path.join(os.path.dirname(os.path.abspath(MAPJSON)), 'landmask.npy'))
_land = ndi.map_coordinates(_lm, [zy / PPU / 0.2, zx / PPU / 0.2], order=1, mode='nearest')
_land = ndi.gaussian_filter(_land, PPU * 0.10) + (vnoise(PPU * 0.5, 444) - 0.5) * 0.25
Ms = ndi.gaussian_filter((_land < 0.5).astype(f32), PPU * 0.12); del _land, _lm
sm = np.clip(Ms * 1.5 - 0.25, 0, 1)
deep = np.clip(ndi.gaussian_filter(Ms, PPU * 2.6) * 1.7 - 0.6, 0, 1)
near = np.clip(ndi.gaussian_filter(Ms, PPU * 0.9) * 2.0 - 0.15, 0, 1) * (1 - deep)
col = tint(col, WASH, WATERC, (sm * (0.58 + 0.20 * near) * (0.85 + 0.30 * blot)).astype(f32))
waves = np.clip((np.sin(zy / (PPU * 0.33) + 5.0 * vnoise(PPU * 2.4, 301)) - 0.90) / 0.10, 0, 1) * (0.35 + 0.65 * vnoise(PPU * 1.6, 302)) * np.clip(deep * 1.4 + 0.35, 0, 1)
col = mix(col, INDIGO, (0.34 * waves * sm).astype(f32))
SS = 2
ov = Image.new('L', (TEXW * SS, TEXH * SS), 0); od = ImageDraw.Draw(ov)
for rv in M['rivers']:
    if rv['major']: od.line([(x * PPU * SS, z * PPU * SS) for x, z in smooth([tuple(p) for p in rv['pts']], 1)], fill=255, width=int(PPU * 0.95 * SS), joint='curve')
major = ndi.gaussian_filter(np.asarray(ov.resize((TEXW, TEXH), Image.LANCZOS), dtype=f32) / 255.0, 1.2)
ov = Image.new('L', (TEXW * SS, TEXH * SS), 0); od = ImageDraw.Draw(ov)
for rv in M['rivers']:
    if not rv['major']: od.line([(x * PPU * SS, z * PPU * SS) for x, z in smooth([tuple(p) for p in rv['pts']], 1)], fill=255, width=max(2, int(PPU * 0.17 * SS)), joint='curve')
minor = np.asarray(ov.resize((TEXW, TEXH), Image.LANCZOS), dtype=f32) / 255.0 * (1 - np.clip(Mm * 0.4, 0, 1)); del ov
inside = sstep(0.42, 0.72, major) * (1 - sm)
col = tint(col, WASH, WATERC, (inside * 0.92 * (0.85 + 0.30 * blot)).astype(f32))
core = sstep(0.80, 0.98, major) * (1 - sm)                     # 강 한가운데는 한 번 더 짙게
col = mix(col, INDIGO, (0.16 * core).astype(f32))
col = mix(col, INDIGO, (0.62 * minor * (0.75 + 0.4 * blot) * (1 - sm) * (1 - np.clip(major * 1.4, 0, 1))).astype(f32))
img = Image.fromarray(np.clip(col * 255.0, 0, 255).astype(np.uint8), 'RGB')
img.save(OUT, quality=85, optimize=True, subsampling=1)
print('texture', img.size, 'bytes', os.path.getsize(OUT))
mini = img.resize((220, int(round(220 * TEXH / TEXW))), Image.LANCZOS); mb = io.BytesIO(); mini.save(mb, 'JPEG', quality=74)
D3['mini'] = 'data:image/jpeg;base64,' + base64.b64encode(mb.getvalue()).decode('ascii')
open(M3, 'w', encoding='utf-8').write(m3.group(1) + json.dumps(D3, ensure_ascii=False, separators=(',', ':')) + m3.group(3))
print('mini bytes', len(mb.getvalue()))
