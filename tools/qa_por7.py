#!/usr/bin/env python3
"""v0.7 확인용: 고른 인물의 원본을 1/3로 줄여 늘어놓고, 찾은 얼굴 상자(빨강)와 100픽셀 눈금을 그린다(손으로 상자를 잡을 때 쓴다).
usage: qa_por7.py <out.jpg> <key…>"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
names = {l.split('\t')[1]: l.split('\t')[2] for l in open(os.path.join(ROOT, 'art/por5_plan.tsv'), encoding='utf8') if l.strip()}
faces = {}
for fn in ('art/por7_faces.tsv', 'art/por7_focus.tsv'):
    for l in open(os.path.join(ROOT, fn), encoding='utf8'):
        p = l.split()
        if len(p) >= 5 and not p[0].startswith('#') and (len(p) < 6 or float(p[5]) > 0 or fn.endswith('focus.tsv')): faces[p[0]] = [float(v) for v in p[1:5]]
keys = sys.argv[2:]; k3 = 3.0; tw, th, cols = 294, 390, 5
rows = (len(keys) + cols - 1) // cols
F = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc', 16); f2 = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc', 11)
s = Image.new('RGB', (cols * (tw + 8) + 8, rows * (th + 30) + 8), (40, 40, 40)); d = ImageDraw.Draw(s)
for i, k in enumerate(keys):
    x, y = 8 + (i % cols) * (tw + 8), 8 + (i // cols) * (th + 30)
    im = Image.open(os.path.join(ROOT, 'art/raw7', k + '.png')).convert('RGB'); W, H = im.size
    s.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
    for g in range(100, W, 100):
        d.line([x + g / k3, y, x + g / k3, y + 6], fill=(0, 90, 255), width=1); d.text((x + g / k3 - 6, y + 6), str(g // 100), fill=(0, 90, 255), font=f2)
    for g in range(100, H, 100):
        d.line([x, y + g / k3, x + 6, y + g / k3], fill=(0, 90, 255), width=1); d.text((x + 8, y + g / k3 - 7), str(g // 100), fill=(0, 90, 255), font=f2)
    if k in faces:
        fx, fy, fw, fh = faces[k]; d.rectangle([x + fx / k3, y + fy / k3, x + (fx + fw) / k3, y + (fy + fh) / k3], outline=(255, 0, 0), width=2)
    d.text((x + 2, y + th + 2), '%s %s %s' % (names.get(k, ''), k, ('%d,%d %dx%d' % tuple(faces[k])) if k in faces else '상자 없음'), fill=(255, 255, 255), font=F)
s.save(sys.argv[1], quality=86); print(s.size)
