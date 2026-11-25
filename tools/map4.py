#!/usr/bin/env python3
"""v0.26 지도를 확대했을 때 쓸 4배 바탕 그림(조각).
   왜: (11-25 21:30) "맵을 확대하면 맵이 깨져보이거나 뭉개지는데, 완성도가 떨어져보이는데" · (23:41) "b 로해"
     바탕 그림(build/terrain.jpg 3072×2610)은 한 칸에 14점쯤이라, 가장 가까이 당기면 그림 한 점이 화면에서 7배쯤으로 늘어난다.
   하는 일:
     cut     바탕 그림을 4 × 3 조각(768 × 870, 사방 48점 겹침 → 864 × 966)으로 자른다 → art/map4/src/t<i>_<j>.png          (가장자리는 거울처럼 덧댄다)
             → 이것을 Higgsfield 업스케일(bytedance · 4k · 조각마다 2 크레딧)에 넣는다. 작업 번호는 art/map4/jobs.tsv
     get     업스케일한 조각을 내려받는다 → art/map4/up/t<i>_<j>.png      (HF_BASE = 주소의 앞부분 · TIMES = 조각=HHMMSS,… 넣은 시각. 주소는 저장소에 남기지 않는다)
     stitch  조각을 꼭 4배 크기로 맞추고(업스케일이 가로 · 세로를 조금 다르게 늘린다) 겹친 데를 부드럽게 이어 붙인다 → art/map4/full.png (12288 × 10440)
             낮은 주파수(큰 얼룩 · 빛깔)는 원본에서 가져온다 — 조각마다 빛깔이 조금씩 달라도 이음매가 생기지 않고, 원본 그림과 겹쳐도 어긋나지 않는다.
     tiles   8 × 8 조각(1536 × 1305, 사방 32점 겹침 → 1600 × 1369)으로 잘라 WebP 로 → art/map4/tiles/<i>_<j>.webp · art/map4/tiles.json
     check   이어 붙인 것을 1/4 로 줄여 원본과 견준다(빛깔이 얼마나 다른가)
   usage: map4.py cut|get|stitch|tiles|check"""
import sys, os, json, subprocess, hashlib
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, 'build', 'terrain.jpg'); D = os.path.join(ROOT, 'art', 'map4')
K = 4; NX, NY, TW, TH, M = 4, 3, 768, 870, 48                    # 업스케일에 넣는 조각
GX, GY, GM, Q = 8, 8, 32, 80                                     # 판에서 쓰는 조각(4배 그림에서) · 겹침 · WebP 품질
def src(): return np.asarray(Image.open(SRC).convert('RGB'))
def cut():
    im = src(); H, W, _ = im.shape; assert W == TW * NX and H == TH * NY, (W, H)
    pad = np.pad(im, ((M, M), (M, M), (0, 0)), mode='reflect'); os.makedirs(os.path.join(D, 'src'), exist_ok=True)
    for j in range(NY):
        for i in range(NX): Image.fromarray(pad[j * TH:j * TH + TH + 2 * M, i * TW:i * TW + TW + 2 * M]).save(os.path.join(D, 'src', 't%d_%d.png' % (i, j)))
    print('cut', NX * NY, '조각', (TW + 2 * M, TH + 2 * M))
def get():
    import datetime
    base = os.environ['HF_BASE']; date = os.environ.get('DATE', '20261125'); span = int(os.environ.get('SPAN', '150'))
    times = dict(x.split('=') for x in os.environ.get('TIMES', '').split(',') if x); t_def = os.environ.get('T0', '')
    os.makedirs(os.path.join(D, 'up'), exist_ok=True); last = t_def
    for l in open(os.path.join(D, 'jobs.tsv'), encoding='utf8'):
        if not l.strip() or l.startswith('#'): continue
        name, _, job = l.split()
        out = os.path.join(D, 'up', name + '.png')
        if name == 'trial' or os.path.exists(out): continue
        t0 = datetime.datetime.strptime(date + (times.get(name) or last), '%Y%m%d%H%M%S'); ok = False
        for d in sorted(range(-span, span + 1), key=abs) if name not in times else [0]:
            ts = (t0 + datetime.timedelta(seconds=d)).strftime('%Y%m%d_%H%M%S')
            r = subprocess.run(['curl', '-sS', '-o', out, '-w', '%{http_code}', '%s/hf_%s_%s.png' % (base, ts, job)], capture_output=True, text=True)
            if r.stdout.strip() == '200': ok = True; last = ts[9:]; break
        if not ok and os.path.exists(out): os.remove(out)
        print(name, 'ok' if ok else 'NOT FOUND', Image.open(out).size if ok else '')
def feather(n, m):
    """길이 n 의 띠에서 양 끝 m 점에 걸쳐 0 → 1 로 오르는 무게"""
    w = np.ones(n, np.float32); r = (np.arange(m, dtype=np.float32) + 0.5) / m; w[:m] = r; w[-m:] = r[::-1]; return w
def stitch():
    from scipy import ndimage as ndi
    im = src(); H, W, _ = im.shape; pad = np.pad(im, ((M, M), (M, M), (0, 0)), mode='reflect')
    acc = np.zeros((H * K, W * K, 3), np.float32); wsum = np.zeros((H * K, W * K), np.float32)
    tw, th = (TW + 2 * M) * K, (TH + 2 * M) * K; wx = feather(tw, 2 * M * K); wy = feather(th, 2 * M * K); wt = np.outer(wy, wx)
    for j in range(NY):
        for i in range(NX):
            up = np.asarray(Image.open(os.path.join(D, 'up', 't%d_%d.png' % (i, j))).convert('RGB').resize((tw, th), Image.LANCZOS), dtype=np.float32)
            ref = np.asarray(Image.fromarray(pad[j * TH:j * TH + TH + 2 * M, i * TW:i * TW + TW + 2 * M]).resize((tw, th), Image.BICUBIC), dtype=np.float32)
            for c in range(3): up[:, :, c] += ndi.gaussian_filter(ref[:, :, c] - up[:, :, c], 10 * K)        # 낮은 주파수는 원본의 것으로(원본 10점 = 4배 그림 40점보다 큰 얼룩)
            x0, y0 = (i * TW - M) * K, (j * TH - M) * K                                                      # 이 조각이 큰 그림에 놓일 자리(겹침 포함)
            ax0, ay0 = max(0, x0), max(0, y0); ax1, ay1 = min(W * K, x0 + tw), min(H * K, y0 + th)
            sx, sy = ax0 - x0, ay0 - y0; w = wt[sy:sy + ay1 - ay0, sx:sx + ax1 - ax0]
            acc[ay0:ay1, ax0:ax1] += up[sy:sy + ay1 - ay0, sx:sx + ax1 - ax0] * w[:, :, None]; wsum[ay0:ay1, ax0:ax1] += w
            print('  t%d_%d' % (i, j), flush=True)
    acc /= np.maximum(wsum, 1e-6)[:, :, None]
    Image.fromarray(np.clip(acc + 0.5, 0, 255).astype(np.uint8)).save(os.path.join(D, 'full.png'), compress_level=1)
    print('stitch', acc.shape[1], acc.shape[0], '무게의 가장 작은 값 %.3f' % float(wsum.min()))
def tiles():
    full = np.asarray(Image.open(os.path.join(D, 'full.png')).convert('RGB')); H, W, _ = full.shape; tw, th = W // GX, H // GY
    assert tw * GX == W and th * GY == H, (W, H)
    pad = np.pad(full, ((GM, GM), (GM, GM), (0, 0)), mode='reflect'); out = os.path.join(D, 'tiles'); os.makedirs(out, exist_ok=True); tot = 0; h = hashlib.sha256()
    for j in range(GY):
        for i in range(GX):
            p = os.path.join(out, '%d_%d.webp' % (i, j)); Image.fromarray(pad[j * th:j * th + th + 2 * GM, i * tw:i * tw + tw + 2 * GM]).save(p, 'WEBP', quality=Q, method=6)
            b = open(p, 'rb').read(); tot += len(b); h.update(b)
    meta = {'nx': GX, 'ny': GY, 'w': tw + 2 * GM, 'h': th + 2 * GM, 'm': GM, 'W': W, 'H': H, 'k': K, 'hash': h.hexdigest()[:8], 'bytes': tot}
    json.dump(meta, open(os.path.join(D, 'tiles.json'), 'w')); print('tiles', GX * GY, '장', meta)
def check():
    full = Image.open(os.path.join(D, 'full.png')).convert('RGB'); a = np.asarray(full.resize((full.size[0] // K, full.size[1] // K), Image.LANCZOS), dtype=np.float32); b = src().astype(np.float32)
    d = np.abs(a - b); lo = np.abs(np.asarray(Image.fromarray(a.astype(np.uint8)).resize((384, 326), Image.BOX), dtype=np.float32) - np.asarray(Image.fromarray(b.astype(np.uint8)).resize((384, 326), Image.BOX), dtype=np.float32))
    print('check 1/4 로 줄여 원본과: 평균 차이 %.2f · 99%% 점 %.1f · 큰 얼룩(8점 평균)의 차이 평균 %.2f · 최대 %.1f  (0 ~ 255)' % (d.mean(), np.percentile(d, 99), lo.mean(), lo.max()))
if __name__ == '__main__': {'cut': cut, 'get': get, 'stitch': stitch, 'tiles': tiles, 'check': check}[sys.argv[1]]()
