#!/usr/bin/env python3
"""초상 가공: 흰 배경 → 테두리 플러드필 투명화, WebP, JS 데이터로 묶기.
usage: make_portraits.py <new_png_dir[,dir2...]> <old_portrait_dir> <out_dir> <out_js> <title_png> <roster_js> [size=288] [quality=70]
  - new_png_dir: 흰 바탕(#FFFFFF) 원본 1024px PNG. 쉼표로 여러 폴더(뒤쪽이 우선).
  - roster_js: 여기에 쓰인 초상 키만 묶는다(안 쓰는 그림은 뺀다).
v0.3: 144px → 288px, 지도 그림(MAP_IMG)은 더 이상 묶지 않음, 아래 테두리에 닿는 흰 조각은 작거나 순백일 때만 배경으로 봄(흰 옷이 뚫리지 않게).
"""
import sys, os, base64, io
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

import json, re
NEW, OLD, OUTDIR, OUTJS, TITLE, ROSTER = sys.argv[1:7]
SIZE = int(sys.argv[7]) if len(sys.argv) > 7 else 288
Q = int(sys.argv[8]) if len(sys.argv) > 8 else 70
GEN_SIZE = min(SIZE, 224)          # 여럿이 같이 쓰는 일반 초상은 조금 작게
_r = open(ROSTER, encoding='utf-8').read()
USED = set(o['por'] for o in json.loads(_r[_r.index('{'):_r.rindex('}') + 1])['officers'])
os.makedirs(OUTDIR, exist_ok=True)

def cut_white(im):
    im = im.convert('RGB')
    a = np.asarray(im).astype(np.int16)
    white = (a[:, :, 0] > 236) & (a[:, :, 1] > 236) & (a[:, :, 2] > 236)
    lab, n = ndimage.label(white)
    top = int(a.shape[0] * 0.62)
    border = set(np.unique(np.concatenate([lab[0, :], lab[:top, 0], lab[:top, -1]])))
    border.discard(0)
    bg = np.isin(lab, list(border))
    # 아래쪽·옆 아랫부분 테두리에만 닿는 흰 조각: 어깨 옆 구석이나 팔과 몸 사이의 배경.
    # 흰 옷자락을 지우지 않도록, 작거나(1만5천 화소 미만) 거의 순백(92% 이상)인 것만 배경으로 본다.
    low = set(np.unique(np.concatenate([lab[-1, :], lab[top:, 0], lab[top:, -1]]))) - border
    low.discard(0)
    for wl in low:
        comp = lab == wl; area = int(comp.sum())
        if area < 15000 or float(((a.min(2) >= 252) & comp).sum()) / area >= 0.92: bg |= comp
    pure = (a[:, :, 0] >= 252) & (a[:, :, 1] >= 252) & (a[:, :, 2] >= 252)
    lab2, n2 = ndimage.label(pure)
    if n2:
        sizes = ndimage.sum(pure, lab2, range(1, n2 + 1))
        for i2, sz in enumerate(sizes):
            if sz >= 2500:
                comp = lab2 == (i2 + 1)
                # 순백 덩어리가 속한 '흰색' 영역 전체가 거의 순백일 때만 배경 처리
                wl = lab[comp][0]
                if wl and ndimage.sum(white, lab, wl) <= sz * 1.25: bg |= (lab == wl)
    alpha = np.where(bg, 0, 255).astype(np.uint8)
    al = Image.fromarray(alpha, 'L').filter(ImageFilter.GaussianBlur(1.2))
    # 가장자리 흰 테두리 줄이기: 알파를 살짝 깎는다
    al = al.point(lambda v: 0 if v < 110 else min(255, int((v - 110) * 1.9)))
    out = im.convert('RGBA'); out.putalpha(al)
    return out

def clean_specks(im):
    im = im.convert('RGBA')
    a = np.asarray(im).copy()
    # 구워진 체커보드(무채색 밝은 칸)가 투명 영역에 닿아 있으면 배경으로 본다
    rgb = a[:, :, :3].astype(np.int16)
    neutral = (rgb.max(2) - rgb.min(2) <= 6) & (rgb.min(2) >= 188) & (a[:, :, 3] > 40)
    transp = a[:, :, 3] <= 40
    near = ndimage.binary_dilation(transp, iterations=2)
    lab0, n0 = ndimage.label(neutral)
    if n0:
        touch = np.unique(lab0[near & neutral]); touch = touch[touch > 0]
        kill = np.isin(lab0, touch)
        # 윤곽선 안쪽에 갇힌 체커보드 조각(흰색+회색 칸이 섞인 덩어리)
        vmin = rgb.min(2)
        sizes0 = ndimage.sum(neutral, lab0, range(1, n0 + 1))
        for i0, sz in enumerate(sizes0):
            if sz < 120 or (i0 + 1) in touch: continue
            comp = lab0 == (i0 + 1)
            v = vmin[comp]
            if (v >= 248).mean() >= 0.2 and ((v >= 188) & (v <= 216)).mean() >= 0.2: kill |= comp
        a[:, :, 3] = np.where(kill, 0, a[:, :, 3])
    m = a[:, :, 3] > 40
    lab, n = ndimage.label(m)
    if n > 1:
        sizes = ndimage.sum(m, lab, range(1, n + 1))
        big = sizes.max()
        keep = [i + 1 for i, s in enumerate(sizes) if s >= big * 0.015]
        a[:, :, 3] = np.where(np.isin(lab, keep), a[:, :, 3], 0)
    return Image.fromarray(a, 'RGBA')

def enc(im, key, q=None):
    sz = GEN_SIZE if re.match(r'g[mcf]\d$', key) else SIZE
    im = im.resize((sz, sz), Image.LANCZOS)
    q = q or Q
    buf = io.BytesIO(); im.save(buf, 'WEBP', quality=q, method=6)
    return buf.getvalue()

data = {}
for fn in sorted(os.listdir(OLD)):
    if not fn.endswith('.png') or fn[:-4] not in USED: continue
    key = fn[:-4]
    data[key] = enc(clean_specks(Image.open(os.path.join(OLD, fn))), key)
for d in NEW.split(','):
    for fn in sorted(os.listdir(d)):
        if not fn.endswith('.png') or fn[:-4] not in USED: continue
        key = fn[:-4]
        data[key] = enc(cut_white(Image.open(os.path.join(d, fn))), key)
miss = sorted(USED - set(data))
assert not miss, '초상 원본 없음: %s' % miss
total = 0
for fn in os.listdir(OUTDIR):
    if fn.endswith('.webp'): os.remove(os.path.join(OUTDIR, fn))
for k, b in data.items():
    open(os.path.join(OUTDIR, k + '.webp'), 'wb').write(b); total += len(b)
# 타이틀
t = Image.open(TITLE).convert('RGB').resize((720, 1290), Image.LANCZOS)
buf = io.BytesIO(); t.save(buf, 'JPEG', quality=78, optimize=True, progressive=True); tb = buf.getvalue()
with open(OUTJS, 'w') as f:
    f.write('var PORTRAITS={' + ','.join('"%s":"%s"' % (k, base64.b64encode(b).decode()) for k, b in sorted(data.items())) + '};\n')
    f.write('var TITLE_IMG="data:image/jpeg;base64,' + base64.b64encode(tb).decode() + '";\n')
print(len(data), 'portraits', total, 'bytes (avg %d); title' % (total // len(data)), len(tb), 'js', os.path.getsize(OUTJS))
