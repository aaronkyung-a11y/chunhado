#!/usr/bin/env python3
"""v0.18 제목 화면 그림: 관우의 전신(art/title18/guanyu_full.png, 9:16) → art/title18/title.jpg (폭 960, JPEG)
   종이 빛을 화면의 종이색(#f4efe3)에 맞춘다 — 밝은 쪽 60% 의 가운데값을 그 색으로 끌어온다(먹은 그대로 어둡다).
usage: make_title18.py [원본.png] [나올.jpg]"""
import os, sys
import numpy as np
from PIL import Image
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'art', 'title18', 'guanyu_full.png')
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'art', 'title18', 'title.jpg')
W, Q, PAPER = 960, 80, (244, 239, 227)
im = Image.open(SRC).convert('RGB')
a = np.asarray(im).astype(np.float32)
lum = a.mean(axis=2); paper = np.median(a[lum >= np.percentile(lum, 60)], axis=0)
b = np.clip(a * (np.array(PAPER, dtype=np.float32) / paper), 0, 255).astype(np.uint8)
o = Image.fromarray(b).resize((W, round(im.height * W / im.width)), Image.LANCZOS)
o.save(OUT, quality=Q, optimize=True, progressive=True)
print('title %dx%d → %dx%d, 종이 %s → %s, %d바이트' % (im.width, im.height, o.width, o.height, [int(v) for v in paper], list(PAPER), os.path.getsize(OUT)))
