#!/usr/bin/env python3
"""PWA 아이콘 만들기(v0.7): 관우 초상(art/raw7/guanyu.png)의 윗부분 + 붉은 낙관. v0.18: 낙관을 '天下' 에서 '天下圖'(세 글자)로.
   pwa/icons/icon-192.png, icon-512.png, icon-maskable-512.png, apple-touch-icon.png(180), favicon-48.png
usage: make_icons.py [preview.jpg]"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
PAPER = (244, 239, 227); SEAL = (181, 51, 42); SEAL_INK = (251, 243, 228)
FONT = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc'
src = Image.open(os.path.join(ROOT, 'art/raw7/guanyu.png')).convert('RGB')
def art(size, box, pad):
    """box = 원본에서 잘라 낼 정사각형(x, y, 한 변). pad = 가장자리 여백 비율(마스크형 아이콘은 크게)"""
    x, y, s = box
    crop = src.crop((x, y, x + s, y + s))
    inner = int(round(size * (1 - 2 * pad)))
    crop = crop.resize((inner, inner), Image.LANCZOS)
    bg = Image.new('RGB', (size, size), PAPER)
    lay = Image.new('RGB', (size, size), (255, 255, 255)); lay.paste(crop, ((size - inner) // 2, (size - inner) // 2))
    if pad > 0:                                   # 잘린 가장자리가 보이지 않게 흰 쪽으로 풀어 준다
        m = Image.new('L', (size, size), 0); d = ImageDraw.Draw(m); o = (size - inner) // 2
        d.rectangle((o + inner * 0.11, o + inner * 0.10, o + inner * 0.90, o + inner * 0.90), fill=255)
        m = m.filter(ImageFilter.GaussianBlur(inner * 0.055))
        lay = Image.composite(lay, Image.new('RGB', (size, size), (255, 255, 255)), m)
    return ImageChops.multiply(bg, lay)           # 흰 바탕 → 종이색, 먹은 그대로
def seal(im, cx, cy, w, text='天下圖'):
    """붉은 낙관: 세로로 글자 수만큼(v0.18: 세 글자 '天下圖')"""
    n = len(text); pad = 0.215; step = 0.865                    # 위아래 여백 · 글자 사이(모두 폭 w 에 대한 비)
    d = ImageDraw.Draw(im); h = int(w * (2 * pad + step * (n - 1) + 0.80)); r = max(2, int(w * 0.09))
    d.rounded_rectangle((cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2), radius=r, fill=SEAL)
    f = ImageFont.truetype(FONT, int(w * 0.80), index=1)        # index 1 = KR
    for i, ch in enumerate(text):
        bb = d.textbbox((0, 0), ch, font=f); tw, th = bb[2] - bb[0], bb[3] - bb[1]
        ty = cy - h // 2 + int(w * (pad + 0.40 + step * i)) - th // 2 - bb[1]
        d.text((cx - tw // 2 - bb[0], ty), ch, font=f, fill=SEAL_INK)
    return im
def make(size, maskable=False):
    S = 1024                                                    # 크게 그린 뒤 줄인다
    if maskable: im = art(S, (270, 20, 590), 0.13); seal(im, int(S * 0.272), int(S * 0.628), int(S * 0.108))
    else:        im = art(S, (270, 20, 590), 0.0);  seal(im, int(S * 0.150), int(S * 0.700), int(S * 0.140))
    return im.resize((size, size), Image.LANCZOS)
out = os.path.join(ROOT, 'pwa/icons'); os.makedirs(out, exist_ok=True)
files = {'icon-192.png': (192, False), 'icon-512.png': (512, False), 'icon-maskable-512.png': (512, True), 'apple-touch-icon.png': (180, False), 'favicon-48.png': (48, False)}
for n, (sz, mk) in files.items():
    make(sz, mk).save(os.path.join(out, n), optimize=True); print('  %-24s %4dpx %6d바이트' % (n, sz, os.path.getsize(os.path.join(out, n))))
if len(sys.argv) > 1:                                           # 미리 보기: 큰 것, 마스크(원·둥근 네모로 잘린 모습), 작은 것
    a = make(512); b = make(512, True); pv = Image.new('RGB', (512 * 3 + 40 + 200, 512), (60, 60, 60)); pv.paste(a, (0, 0))
    for k, shape in enumerate(['circle', 'squircle']):
        m = Image.new('L', (512, 512), 0); d = ImageDraw.Draw(m)
        if shape == 'circle': d.ellipse((0, 0, 511, 511), fill=255)
        else: d.rounded_rectangle((0, 0, 511, 511), radius=120, fill=255)
        pv.paste(b, (532 + k * 522, 0), m)
    for k, sz in enumerate([96, 48]): pv.paste(make(sz), (512 * 3 + 60, 20 + k * 130))
    pv.save(sys.argv[1], quality=88)
