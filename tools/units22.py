#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.22 부대 그림 손질 — "그림 중 창병이 지나치게 크다. 그리고 창병 극병 노병 기병이 색으로 좀 구분지어지게하면 좋겠다"
 1) 창병의 크기: 부대 그림은 모두 '가로 2칸'에 맞춰 그리는데(UNIT_W), 창병 그림만 가로 162 · 세로 200 으로 좁게 잘려 있었다(다른 병과는 가로 200 안팎).
    그래서 같은 가로에 맞추면 창병만 1.23배로 커졌다. → 창병 그림의 좌우에 빈 자리를 대어 가로 200 으로 만든다(사람의 크기가 다른 병과와 같아진다. 무리의 가운데가 그림의 가운데에 온다).
 2) 병과의 빛깔: 먹 그림 위에 옅은 물감을 한 겹 올린다(담채) — 밝은 곳일수록 물이 들고 먹선은 그대로다. 붉은 깃 · 술도 그 병과의 빛으로 바꾼다.
      창병 = 푸른빛 · 극병 = 붉은빛 · 노병 = 초록빛 · 기병 = 누른빛.   검병 · 충차 · 수송대는 먹빛 그대로.
 새 그림을 만들지 않는다(생성 0회) — 있던 그림을 고쳐 쓴다.
 usage: units22.py <build/sprites.v021.js> <src/sprites.js>"""
import sys, io, json, re, base64, colorsys
import numpy as np
from PIL import Image
SRC, OUT = sys.argv[1], sys.argv[2]
WASH = 0.75                                                      # 물감의 진하기
TINT = {'u_spear': (0.56, 0.74, 0.98), 'u_halberd': (1.00, 0.66, 0.58), 'u_bow': (0.62, 0.88, 0.62), 'u_cav': (1.00, 0.84, 0.46)}
ACCENT = {'u_spear': 0.60, 'u_bow': 0.36, 'u_cav': 0.12}        # 붉은 깃 · 술을 바꿀 색상(0 ~ 1). 극병은 붉은 그대로
PAD_W = {'u_spear': 200}                                        # 가로를 이만큼으로(좌우에 빈 자리)
s = open(SRC, encoding='utf8').read()
m = re.match(r'^(var SPRITES\s*=\s*)(.*?)(;\s*)$', s, re.S); S = json.loads(m.group(2))
def wash(im, key):
    a = np.asarray(im).astype(np.float32) / 255.0; rgb = a[..., :3]; al = a[..., 3]
    t = np.array(TINT[key], np.float32)
    mx = rgb.max(axis=2); mn = rgb.min(axis=2); sat = (mx - mn) / np.maximum(mx, 1e-3)
    red = (sat > 0.35) & (rgb[..., 0] > rgb[..., 1] * 1.3) & (rgb[..., 0] > rgb[..., 2] * 1.3) & (mx > 0.3)      # 붉은 포인트(깃 · 술)
    lum = rgb[..., 0] * 0.3 + rgb[..., 1] * 0.59 + rgb[..., 2] * 0.11
    k = WASH * np.clip((lum - 0.12) / 0.5, 0, 1)                 # 밝은 곳일수록 물이 든다
    out = rgb * (1 - k[..., None] + k[..., None] * t[None, None, :])
    if key in ACCENT:
        ys, xs = np.where(red)
        for y, x in zip(ys, xs):
            h, l, sv = colorsys.rgb_to_hls(*[float(v) for v in rgb[y, x]])
            out[y, x] = colorsys.hls_to_rgb(ACCENT[key], l * (1.05 if key == 'u_cav' else 0.9), sv)
    else:
        out[red] = rgb[red]
    return Image.fromarray((np.dstack([np.clip(out, 0, 1), al]) * 255).round().astype(np.uint8), 'RGBA'), int(red.sum())
for key in sorted(TINT):
    e = S[key]; im = Image.open(io.BytesIO(base64.b64decode(e['u'].split(',', 1)[1]))).convert('RGBA')
    assert im.size == (e['w'], e['h']), (key, im.size)
    im2, nred = wash(im, key)
    note = ''
    if key in PAD_W and im2.width < PAD_W[key]:
        al = np.asarray(im2)[..., 3]; xs = np.where(al.max(axis=0) > 40)[0]; cx = (int(xs.min()) + int(xs.max()) + 1) / 2.0     # 무리의 가운데
        W = PAD_W[key]; x0 = int(round(W / 2.0 - cx)); x0 = max(0, min(W - im2.width, x0))
        pad = Image.new('RGBA', (W, im2.height), (0, 0, 0, 0)); pad.paste(im2, (x0, 0)); note = ' pad %d -> %d (x0 %d)' % (im2.width, W, x0); im2 = pad
    bio = io.BytesIO(); im2.save(bio, 'WEBP', quality=88, method=6)
    S[key] = dict(u='data:image/webp;base64,' + base64.b64encode(bio.getvalue()).decode('ascii'), w=im2.width, h=im2.height, ay=e['ay'])
    print(key, im.size, '->', im2.size, 'bytes', len(bio.getvalue()), 'accent px', nred, note)
open(OUT, 'w', encoding='utf8').write(m.group(1) + json.dumps(S, separators=(',', ':')) + m.group(3))
print('written', OUT)
