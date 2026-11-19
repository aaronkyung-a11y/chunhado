#!/usr/bin/env python3
"""v0.5 자산: 장면 초상(3:4) → ① 얼굴 중심 정사각 흉상(작은 칸용) ② 장면 전체(장수 정보 창용) + 타이틀·한지(앞 판 것 그대로) → src/assets.js
usage: make_assets_v05.py <raw5_dir> <faces.tsv> <out_dir> <out_js> <prev_assets.js> <roster_js> [bust=288] [sceneW=360] [qBust=74] [qScene=66]
 - faces.tsv: tools/facebox.py 의 결과. art/por5_focus.tsv 가 있으면 그 줄이 우선(key, x, y, w, h — 손으로 고친 얼굴 상자).
 - raw5 에 없는 키는 <fallback_dir>(환경 변수 FALLBACK, 기본 art/raw3)의 정사각 그림을 그대로 쓴다(장면은 없음)."""
import sys, os, io, re, base64
import numpy as np
from PIL import Image, ImageFilter
RAW, FACES, OUTDIR, OUTJS, PREV, ROSTER = sys.argv[1:7]
BUST = int(sys.argv[7]) if len(sys.argv) > 7 else 288
SW = int(sys.argv[8]) if len(sys.argv) > 8 else 360
QB = int(sys.argv[9]) if len(sys.argv) > 9 else 74
QS = int(sys.argv[10]) if len(sys.argv) > 10 else 66
FALLBACK = os.environ.get('FALLBACK', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'art', 'raw3'))
os.makedirs(os.path.join(OUTDIR, 'bust'), exist_ok=True); os.makedirs(os.path.join(OUTDIR, 'scene'), exist_ok=True)
used = sorted(set(re.findall(r'"por":"([a-z0-9_]+)"', open(ROSTER, encoding='utf8').read())))
faces = {}
for ln in open(FACES):
    p = ln.split('\t')
    if len(p) >= 6 and float(p[5]) > 0: faces[p[0]] = [float(v) for v in p[1:5]]
fo = os.environ.get('FOCUS', os.path.join(os.path.dirname(os.path.abspath(FACES)), 'por5_focus.tsv'))    # v0.7: FOCUS=art/por7_focus.tsv
if os.path.exists(fo):
    for ln in open(fo, encoding='utf8'):
        p = ln.split()
        if len(p) >= 5 and not p[0].startswith('#'): faces[p[0]] = [float(v) for v in p[1:5]]
def clean(im):
    """바탕을 순백으로(가장자리 밝기를 흰 점으로), 먹을 조금 눌러 준다"""
    a = np.asarray(im.convert('RGB')).astype(np.float32)
    edge = np.concatenate([a[:14].reshape(-1, 3), a[-6:].reshape(-1, 3), a[:, :10].reshape(-1, 3), a[:, -10:].reshape(-1, 3)])
    wp = np.percentile(edge, 80, axis=0)
    a = np.clip(a / np.maximum(wp - 1.0, 200.0)[None, None, :] * 255.0, 0, 255)
    g = a / 255.0; g = np.where(g < 0.985, g ** 1.12, g)
    return Image.fromarray((g * 255.0 + 0.5).astype(np.uint8), 'RGB'), [int(v) for v in wp]
def webp(im, q):
    buf = io.BytesIO(); im.save(buf, 'WEBP', quality=q, method=6); return buf.getvalue()
busts = {}; scenes = {}; tb = ts = 0; noface = []; fb = []; warn = []
for k in used:
    p = os.path.join(RAW, k + '.png')
    if not os.path.exists(p):                                   # 아직 새 그림이 없는 인물: 앞 판의 정사각 초상
        im, wp = clean(Image.open(os.path.join(FALLBACK, k + '.png')))
        s = 224 if re.match(r'g[mcf]\d$', k) else BUST
        b = im.resize((s, s), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.0, 40, 2))
        busts[k] = webp(b, QB); tb += len(busts[k]); fb.append(k); continue
    im, wp = clean(Image.open(p)); W, H = im.size
    if min(wp) < 240: warn.append((k, wp))
    if k not in faces: noface.append(k); f = [W * 0.5 - W * 0.08, H * 0.2, W * 0.16, H * 0.16]
    else: f = faces[k]
    fx, fy, fw, fh = f; cx = fx + fw / 2; cy = fy + fh / 2
    # 흉상: 얼굴 높이가 정사각의 30%쯤, 얼굴 중심이 가로 가운데·세로 41% 자리에 오게. 그림 밖으로 나가면 안으로 민다.
    side = min(W, max(fh / 0.30, fw / 0.24)); side = min(side, H)
    x0 = min(max(cx - side / 2, 0), W - side); y0 = min(max(cy - side * 0.41, 0), H - side)
    b = im.crop((int(round(x0)), int(round(y0)), int(round(x0 + side)), int(round(y0 + side))))
    s = 224 if re.match(r'g[mcf]\d$', k) else BUST
    b = b.resize((s, s), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.0, 40, 2))
    b.save(os.path.join(OUTDIR, 'bust', k + '.webp'), 'WEBP', quality=QB, method=6)
    busts[k] = webp(b, QB); tb += len(busts[k])
    sc = im.resize((SW, int(round(SW * H / W))), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.0, 30, 2))
    sc.save(os.path.join(OUTDIR, 'scene', k + '.webp'), 'WEBP', quality=QS, method=6)
    scenes[k] = webp(sc, QS); ts += len(scenes[k])
print('busts', len(busts), 'bytes', tb, 'avg', tb // max(1, len(busts)), '| scenes', len(scenes), 'bytes', ts, 'avg', ts // max(1, len(scenes)))
if fb: print('fallback to previous square portraits:', len(fb))
if noface: print('NO FACE BOX (centre guess used):', noface)
if warn: print('white point adjusted:', warn[:12], len(warn))
prev = open(PREV, encoding='utf8').read()
title = re.search(r'^var TITLE_IMG=.*$', prev, re.M).group(0); hanji = re.search(r'^var HANJI_IMG=.*$', prev, re.M).group(0)
with open(OUTJS, 'w', encoding='utf8') as f:
    f.write('var PORTRAITS={' + ','.join('"%s":"%s"' % (k, base64.b64encode(b).decode()) for k, b in sorted(busts.items())) + '};\n')
    f.write('var SCENES={' + ','.join('"%s":"%s"' % (k, base64.b64encode(b).decode()) for k, b in sorted(scenes.items())) + '};\n')
    f.write(title + '\n' + hanji + '\n')
print('assets.js', os.path.getsize(OUTJS))
