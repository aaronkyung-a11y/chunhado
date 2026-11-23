#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.21 바탕 그림에 관문의 능선을 그려 넣는다 — 0.20 의 그림(build/terrain.v020.jpg) 위에 덧칠한다.
 능선은 칸과 칸 사이의 변(MAPDATA.walls)을 따라 선다: 엷은 먹 번짐 한 겹 + 작은 봉우리(ㅅ) 줄.
 usage: terrain21.py <terrain.v020.jpg> <build/mapdata.json> <src/map3d.js> <out terrain.jpg>"""
import sys, json, math, io, os, re, base64, random, collections
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
SRC, MAPJSON, M3, OUT = sys.argv[1:5]
Image.MAX_IMAGE_PIXELS = None
SQ3 = math.sqrt(3)
M = json.load(open(MAPJSON, encoding='utf-8')); G = M['grid']; WX = G['WX']
img = Image.open(SRC).convert('RGB'); TEXW, TEXH = img.size; PPU = TEXW / WX
def center(c, r): return (SQ3 * (c + 0.5 * (r & 1)) + SQ3 / 2, 1.5 * r + 1.0)
# ---- 변 → 꼭짓점 두 개 ----
segs = []
for c1, r1, c2, r2, gi in M['walls']:
    ax, az = center(c1, r1); bx, bz = center(c2, r2); mx, mz = (ax + bx) / 2, (az + bz) / 2
    dx, dz = bx - ax, bz - az; L = math.hypot(dx, dz); px, pz = -dz / L, dx / L
    segs.append(((round(mx + 0.5 * px, 3), round(mz + 0.5 * pz, 3)), (round(mx - 0.5 * px, 3), round(mz - 0.5 * pz, 3))))
# ---- 이어 붙이기 ----
adj = collections.defaultdict(list)
for i, (a, b) in enumerate(segs): adj[a].append(i); adj[b].append(i)
used = set(); lines = []
def walk(p0, i0):
    line = [p0]; p, i = p0, i0
    while i is not None and i not in used:
        used.add(i); a, b = segs[i]; p = b if a == p else a; line.append(p)
        nx = [j for j in adj[p] if j not in used]; i = nx[0] if len(adj[p]) == 2 and nx else None
    return line
for p in sorted(adj):
    if len(adj[p]) != 2:
        for i in adj[p]:
            if i not in used: lines.append(walk(p, i))
for i in range(len(segs)):
    if i not in used: lines.append(walk(segs[i][0], i))
print('walls', len(segs), 'lines', len(lines), 'longest', max(len(l) for l in lines))
# ---- 그리기: 좁은 산줄기 — 이미 있는 산과 같은 결(먹의 그늘 + 엷은 담채 + 가는 테두리) ----
from scipy import ndimage as ndi
f32 = np.float32
def vnoise(cell, seed, shape=(TEXH, TEXW)):
    rs = np.random.RandomState(seed)
    gh, gw = int(shape[0] / cell) + 4, int(shape[1] / cell) + 4
    z = ndi.zoom(rs.rand(gh, gw).astype(f32), cell, order=3)
    return np.clip(z[int(cell):int(cell) + shape[0], int(cell):int(cell) + shape[1]], 0, 1)
def sstep(a, b, x): t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)
SS = 3; S = PPU * SS
mk = Image.new('L', (TEXW * SS, TEXH * SS), 0); md = ImageDraw.Draw(mk)
rnd = random.Random(2126)
for line in lines:
    pts = [((x + rnd.uniform(-0.10, 0.10)) * S, (z + rnd.uniform(-0.10, 0.10)) * S) for x, z in line]
    md.line(pts, fill=255, width=int(0.40 * S), joint='curve')
    for x, z in pts: md.ellipse([x - 0.20 * S, z - 0.20 * S, x + 0.20 * S, z + 0.20 * S], fill=255)
m = np.asarray(mk.resize((TEXW, TEXH), Image.LANCZOS), dtype=f32) / 255.0; del mk
h = ndi.gaussian_filter(m, 0.34 * PPU); h = h / max(1e-6, np.percentile(h[h > 0.02], 97))            # 능선의 단면(마루 ≈ 1)
n1 = vnoise(PPU * 1.3, 211); n2 = vnoise(PPU * 0.42, 212); n3 = vnoise(PPU * 0.20, 213)
hh = h * (0.50 + 0.95 * n1) + h * 0.34 * (n2 - 0.5) + h * 0.16 * (n3 - 0.5)                            # 봉우리와 안부
gz, gx = np.gradient(ndi.gaussian_filter(hh, 0.6) * 5.0)
shade = gx * 0.62 + gz * 0.78                                                                        # 빛은 북서에서 — 남동 비탈이 그늘
body = sstep(0.10, 0.34, h)
dark = np.clip(-shade * 2.6, 0, 1) * body
lit = np.clip(shade * 1.6, 0, 1) * body
crest = sstep(0.62, 0.96, hh) * (0.35 + 0.65 * n2)
ai = np.clip(dark * (0.55 + 0.5 * n3) * 0.92 + crest * 0.38, 0, 0.9)
aw = body * (0.20 + 0.16 * n1)
edge = np.clip(1 - np.abs(h - 0.115) / 0.030, 0, 1) * 0.42                                           # 가는 테두리
col = np.asarray(img, dtype=f32) / 255.0
INK = np.array([32, 29, 27], f32) / 255.0; UMBER = np.array([150, 138, 124], f32) / 255.0; PAPER = np.array([244, 239, 228], f32) / 255.0
col = col * (1 - aw[..., None]) + UMBER[None, None, :] * aw[..., None]
al = (lit * 0.30).astype(f32); col = col * (1 - al[..., None]) + PAPER[None, None, :] * al[..., None]  # 볕 든 비탈은 종이빛으로
col = col * (1 - edge[..., None]) + (col * 0.42) * edge[..., None]
col = col * (1 - ai[..., None]) + INK[None, None, :] * ai[..., None]
out = Image.fromarray(np.clip(col * 255.0, 0, 255).astype(np.uint8), 'RGB')
out.save(OUT, quality=85, optimize=True, subsampling=1)
print('texture', out.size, 'bytes', os.path.getsize(OUT))
m3s = open(M3, encoding='utf-8').read(); m3 = re.match(r'^(.*?=\s*)(\{.*\})(;\s*)$', m3s, re.S); D3 = json.loads(m3.group(2))
mini = out.resize((220, int(round(220 * TEXH / TEXW))), Image.LANCZOS); mb = io.BytesIO(); mini.save(mb, 'JPEG', quality=74)
D3['mini'] = 'data:image/jpeg;base64,' + base64.b64encode(mb.getvalue()).decode('ascii')
open(M3, 'w', encoding='utf-8').write(m3.group(1) + json.dumps(D3, ensure_ascii=False, separators=(',', ':')) + m3.group(3))
print('mini bytes', len(mb.getvalue()))
