#!/usr/bin/env python3
"""v0.5 초상 확인용 시트: 인물마다 [장면 | 흉상 | 작은 칸 56·44·76·92px 모양]. usage: qa_por5.py <out_dir(make_assets_v05)> <sheet.jpg> key [key…]"""
import sys, os
from PIL import Image, ImageDraw
OUT, SHEET, keys = sys.argv[1], sys.argv[2], sys.argv[3:]
PAPER = (241, 235, 220)
def thumb(b, box, zoom, K=3):
    """CSS: background-size zoom%, position 50% 6% — K배로 그려 본다"""
    S = int(round(box * K * zoom)); im = b.resize((S, S), Image.LANCZOS)
    ox = int(round((box * K - S) * 0.5)); oy = int(round((box * K - S) * 0.06))
    t = Image.new('RGB', (box * K, box * K), PAPER); t.paste(im, (ox, oy)); return t
cols = 4; cw, ch = 560, 250; rows = (len(keys) + cols - 1) // cols
sh = Image.new('RGB', (cols * cw, rows * ch), (200, 196, 186)); d = ImageDraw.Draw(sh)
for i, k in enumerate(keys):
    x0 = (i % cols) * cw + 6; y0 = (i // cols) * ch + 6
    sp = os.path.join(OUT, 'scene', k + '.webp'); bp = os.path.join(OUT, 'bust', k + '.webp')
    if not os.path.exists(bp): d.text((x0, y0), k + ' (없음)', fill=(0, 0, 0)); continue
    b = Image.open(bp).convert('RGB')
    if os.path.exists(sp):
        s = Image.open(sp).convert('RGB').resize((176, 235), Image.LANCZOS); sh.paste(s, (x0, y0))
    sh.paste(b.resize((150, 150), Image.LANCZOS), (x0 + 184, y0))
    x = x0 + 184
    for box, zoom in ((56, 1.42), (44, 1.50)):
        t = thumb(b, box, zoom, 1); sh.paste(t, (x, y0 + 158)); x += box + 8
    x = x0 + 342
    for box, zoom in ((92, 1.16), (76, 1.28)):
        t = thumb(b, box, zoom, 1); sh.paste(t, (x, y0)); x += box + 8
    t = thumb(b, 56, 1.42, 2); sh.paste(t, (x0 + 342, y0 + 100))
    t = thumb(b, 44, 1.50, 2).resize((88, 88)); sh.paste(t, (x0 + 342 + 120, y0 + 100))
    d.text((x0 + 296, y0 + 200), k, fill=(0, 0, 0))
sh.save(SHEET, quality=88); print(SHEET, sh.size)
