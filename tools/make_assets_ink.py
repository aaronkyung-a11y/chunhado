#!/usr/bin/env python3
"""v0.4 수묵 자산: 초상(흰 바탕 그대로 — 화면에서 한지 위에 multiply 로 겹친다) + 타이틀 + 한지 결 → src/assets.js
usage: make_assets_ink.py <raw3_dir> <out_dir> <out_js> <title_png> <roster_js> [size=288] [quality=74]"""
import sys, os, io, re, base64, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
RAW, OUTDIR, OUTJS, TITLE, ROSTER = sys.argv[1:6]
SIZE = int(sys.argv[6]) if len(sys.argv) > 6 else 288
Q = int(sys.argv[7]) if len(sys.argv) > 7 else 74
os.makedirs(OUTDIR, exist_ok=True)
used = sorted(set(re.findall(r'"por":"([a-z0-9_]+)"', open(ROSTER, encoding='utf8').read())))
data = {}; tot = 0; warn = []
for k in used:
    im = Image.open(os.path.join(RAW, k + '.png')).convert('RGB')
    a = np.asarray(im).astype(np.float32)
    # 바탕을 순백으로: 가장자리 띠의 밝기 중앙값을 흰 점으로 삼는다(크림빛 바탕 보정)
    edge = np.concatenate([a[:14].reshape(-1, 3), a[-6:].reshape(-1, 3), a[:, :10].reshape(-1, 3), a[:, -10:].reshape(-1, 3)])
    wp = np.percentile(edge, 80, axis=0)
    if wp.min() < 244: warn.append((k, [int(v) for v in wp]))
    a = np.clip(a / np.maximum(wp - 1.0, 200.0)[None, None, :] * 255.0, 0, 255)
    # 먹을 조금 눌러 준다(작게 줄여도 선이 살아 있게)
    g = a / 255.0
    g = np.where(g < 0.985, g ** 1.12, g)
    im = Image.fromarray((g * 255.0 + 0.5).astype(np.uint8), 'RGB')
    s = 224 if re.match(r'g[mcf]\d$', k) else SIZE
    im = im.resize((s, s), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.0, 40, 2))
    im.save(os.path.join(OUTDIR, k + '.webp'), 'WEBP', quality=Q, method=6)
    buf = io.BytesIO(); im.save(buf, 'WEBP', quality=Q, method=6); data[k] = buf.getvalue(); tot += len(buf.getvalue())
print('portraits', len(data), 'bytes', tot, 'avg', tot // len(data))
if warn: print('white point adjusted:', warn)

# 타이틀: 세로 수묵 산수
t = Image.open(TITLE).convert('RGB')
tw = 760; t = t.resize((tw, int(round(tw * t.height / t.width))), Image.LANCZOS)
buf = io.BytesIO(); t.save(buf, 'JPEG', quality=80, optimize=True, progressive=True); tb = buf.getvalue()
print('title', t.size, len(tb))

# 한지 결: 이어 붙여도 티 나지 않는 240px 조각. 옅은 섬유(어두운 것·밝은 것)와 얼룩
N = 240; rs = np.random.RandomState(7)
big = Image.new('RGBA', (N * 3, N * 3), (0, 0, 0, 0)); d = ImageDraw.Draw(big)
for i in range(150):
    x, y = rs.rand() * N, rs.rand() * N; L = 8 + rs.rand() * 44; ang = rs.rand() * math.pi; cv = (rs.rand() - 0.5) * 0.9
    pts = []
    for j in range(7):
        tt = j / 6.0; aa = ang + cv * (tt - 0.5)
        pts.append((x + math.cos(aa) * L * (tt - 0.5), y + math.sin(aa) * L * (tt - 0.5)))
    dark = rs.rand() < 0.55
    colr = (70, 58, 40, int(4 + rs.rand() * 7)) if dark else (255, 252, 244, int(16 + rs.rand() * 24))
    for ox in (0, N, 2 * N):
        for oy in (0, N, 2 * N):
            d.line([(px + ox, py + oy) for px, py in pts], fill=colr, width=1)
tile = big.crop((N, N, 2 * N, 2 * N)).filter(ImageFilter.GaussianBlur(0.6))
ta = np.asarray(tile).astype(np.float32)
# 얼룩(이음매 없이): 주기적인 사인 몇 개의 합
yy, xx = np.mgrid[0:N, 0:N].astype(np.float32) / N * 2 * math.pi
mot = (np.sin(xx * 1 + 1.3) * np.cos(yy * 2 + 0.4) + np.sin(xx * 3 + yy * 2 + 2.1) * 0.6 + np.cos(xx * 2 - yy * 3 + 0.7) * 0.5) / 2.1
ma = np.clip(mot, 0, 1) * 5.0
out = ta.copy()
al = out[..., 3] / 255.0; al2 = ma / 255.0
out[..., :3] = (out[..., :3] * al[..., None] + np.array([90, 76, 52], np.float32)[None, None, :] * al2[..., None] * (1 - al[..., None])) / np.maximum(al + al2 * (1 - al), 1e-4)[..., None]
out[..., 3] = (al + al2 * (1 - al)) * 255.0
hz = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGBA')
hz.save(os.path.join(OUTDIR, '_hanji.png'))
buf = io.BytesIO(); hz.save(buf, 'WEBP', lossless=True, method=6); hb = buf.getvalue()
print('hanji', len(hb))
with open(OUTJS, 'w', encoding='utf8') as f:
    f.write('var PORTRAITS={' + ','.join('"%s":"%s"' % (k, base64.b64encode(b).decode()) for k, b in sorted(data.items())) + '};\n')
    f.write('var TITLE_IMG="data:image/jpeg;base64,' + base64.b64encode(tb).decode() + '";\n')
    f.write('var HANJI_IMG="data:image/webp;base64,' + base64.b64encode(hb).decode() + '";\n')
print('assets.js', os.path.getsize(OUTJS))
