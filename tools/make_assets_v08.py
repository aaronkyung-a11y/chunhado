#!/usr/bin/env python3
"""v0.8 자산: 초상을 가운데로 다시 자른다(그림은 v0.7 그대로 — 다시 그리지 않는다).
 왜: v0.7 그림 167장 가운데 128장이 얼굴이 가로 55% 지점보다 오른쪽에 있었다(문구에 여백의 '쪽'을 정하지 않았다). 작은 칸 흉상 25장은 그림 끝에 걸려 틀이 밀려 있었다.
 ① 흉상(정사각): 얼굴 중심이 가로 가운데·세로 41%에 오게. 그림 밖으로 나가면 예전에는 틀을 안으로 밀었는데(→ 얼굴이 치우침), 이제는 모자란 쪽을 흰 종이로 채우고
    그림이 끊기는 가장자리를 흰색으로 풀어 준다. 채우는 폭은 틀의 PAD_MAX 까지.
 ② 장면(3:4): 먹의 무게중심과 얼굴 사이(TX_INK : 1-TX_INK)를 틀의 가운데로. 그 점을 가운데 두고 그림 안에 들어가는 가장 큰 3:4 틀로 자른다(틀은 원본의 S_MIN 배보다 작아지지 않는다).
    위쪽(머리·무기)은 남기고 아래쪽(마른 붓으로 풀리는 하반신)을 덜어 낸다. 이미 가운데에 가까운 그림(틀이 원본의 S_KEEP 배 이상 = 가운데서 7% 안쪽)과 KEEP 에 적은 인물은 그대로.
usage: make_assets_v08.py <raw_dir> <faces.tsv> <out_dir> <out_js> <prev_assets.js> <roster_js> [bust=256] [sceneW=320] [qBust=72] [qScene=56]
 - 환경 변수 FOCUS=<손으로 고친 얼굴 상자.tsv>, FALLBACK=<raw 에 없는 키의 정사각 그림 폴더>, TITLE=<제목 화면 그림.jpg>(v0.18 — 없으면 앞 판의 것 그대로)
 - <out_dir>/crops.tsv 에 인물마다 자른 틀과 전후 수치를 남긴다."""
import sys, os, io, re, base64
import numpy as np
from PIL import Image, ImageFilter
RAW, FACES, OUTDIR, OUTJS, PREV, ROSTER = sys.argv[1:7]
BUST = int(sys.argv[7]) if len(sys.argv) > 7 else 256
SW = int(sys.argv[8]) if len(sys.argv) > 8 else 320
QB = int(sys.argv[9]) if len(sys.argv) > 9 else 72
QS = int(sys.argv[10]) if len(sys.argv) > 10 else 56
PAD_MAX, FADE, S_MIN, S_KEEP, TX_INK = 0.20, 0.13, 0.76, 0.86, 0.55
# v0.19: 인물이 한쪽으로 몰린 장면을 다시 맞춘다. SKEW=<여백 차이의 문턱(그림 폭에 대한 비)> 를 주면 켜진다(안 주면 0.18까지와 똑같이 자른다).
#   짙은 먹(인물)의 좌우 끝을 재서 한쪽 여백이 다른 쪽보다 문턱 넘게 넓으면, 그 좌우 끝의 한가운데가 틀의 가운데로 오게 좁혀 자른다(넓은 쪽 여백을 덜어 낸다).
#   그동안의 셈(먹 전체의 무게중심 + 얼굴)은 옅은 붓 자국에 끌려, 인물이 오른쪽 끝에 붙고 왼쪽이 빈 그림을 '가운데'로 보았다.
SKEW = float(os.environ.get('SKEW', '0') or 0); DENSE, S_MIN_SKEW = 0.32, 0.74
KEEP = set(os.environ.get('KEEP', 'diaochan,lubu').split(','))     # 장면을 그대로 두는 인물(따로 견줘 고른 그림)
FALLBACK = os.environ.get('FALLBACK', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'art', 'raw3'))
os.makedirs(os.path.join(OUTDIR, 'bust'), exist_ok=True); os.makedirs(os.path.join(OUTDIR, 'scene'), exist_ok=True)
used = sorted(set(re.findall(r'"por":"([a-z0-9_]+)"', open(ROSTER, encoding='utf8').read())))
faces = {}
for ln in open(FACES):
    p = ln.split('\t')
    if len(p) >= 6 and float(p[5]) > 0: faces[p[0]] = [float(v) for v in p[1:5]]
fo = os.environ.get('FOCUS', '')
if fo and os.path.exists(fo):
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
def ink(im):
    """먹(과 색)의 무게: 0 = 흰 종이, 1 = 짙은 먹/짙은 색"""
    a = np.asarray(im).astype(np.float32)
    lum = a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114
    sat = (a.max(axis=2) - a.min(axis=2)) / 255.0
    return np.maximum(np.clip((244.0 - lum) / 244.0, 0, 1), np.clip(sat * 1.2 - 0.05, 0, 1))
def quant(prof, q):
    c = np.cumsum(prof); return int(np.searchsorted(c, c[-1] * q))
def smooth(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
busts = {}; scenes = {}; tb = ts = 0; noface = []; fb = []; rows = []
for k in used:
    p = os.path.join(RAW, k + '.png')
    if not os.path.exists(p):                                   # 새 그림이 없는 인물: 앞 판의 정사각 초상
        im, wp = clean(Image.open(os.path.join(FALLBACK, k + '.png')))
        s = 224 if re.match(r'g[mcf]\d$', k) else BUST
        b = im.resize((s, s), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.0, 40, 2))
        busts[k] = webp(b, QB); tb += len(busts[k]); fb.append(k); continue
    im, wp = clean(Image.open(p)); W, H = im.size
    if k not in faces: noface.append(k); f = [W * 0.5 - W * 0.08, H * 0.2, W * 0.16, H * 0.16]
    else: f = faces[k]
    fx, fy, fw, fh = f; cx = fx + fw / 2; cy = fy + fh / 2
    # ① 흉상
    side = min(W, max(fh / 0.30, fw / 0.24)); side = min(side, H)
    old_x0 = min(max(cx - side / 2, 0), W - side)
    x0 = cx - side / 2; x0 = min(max(x0, -PAD_MAX * side), W - side + PAD_MAX * side)
    y0 = min(max(cy - side * 0.41, 0), H - side)
    S = int(round(side)); X0 = int(round(x0)); Y0 = int(round(y0))
    canvas = Image.new('RGB', (S, S), (255, 255, 255))
    sx0 = max(0, X0); sx1 = min(W, X0 + S)
    part = im.crop((sx0, Y0, sx1, Y0 + S))
    padL = max(0, -X0); padR = max(0, X0 + S - W)
    if padL or padR:                                            # 그림이 끊기는 쪽을 흰색으로 풀어 준다
        a = np.asarray(part).astype(np.float32); w = a.shape[1]; xs = np.arange(w, dtype=np.float32); F = FADE * S
        m = np.ones(w, np.float32)
        if padR: m *= smooth((w - 1 - xs) / F)
        if padL: m *= smooth(xs / F)
        a = 255.0 - (255.0 - a) * m[None, :, None]
        part = Image.fromarray((a + 0.5).astype(np.uint8), 'RGB')
    canvas.paste(part, (padL, 0))
    s = 224 if re.match(r'g[mcf]\d$', k) else BUST
    b = canvas.resize((s, s), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.0, 40, 2))
    b.save(os.path.join(OUTDIR, 'bust', k + '.webp'), 'WEBP', quality=QB, method=6)
    busts[k] = webp(b, QB); tb += len(busts[k])
    # ② 장면
    wgt = ink(im); colp = wgt.sum(axis=0); rowp = wgt.sum(axis=1)
    xc = float((colp * np.arange(W)).sum() / max(1e-6, colp.sum()))
    tx = TX_INK * xc + (1 - TX_INK) * cx
    def frame(tx, smin, keep):
        w = min(W, 2 * min(tx, W - tx))
        if keep and (w >= S_KEEP * W or k in KEEP): w = W      # 이미 가운데에 가까운 그림(가운데서 7% 안쪽)은 그대로
        w = max(w, smin * W)
        x0 = min(max(tx - w / 2, 0), W - w)
        x0 = min(max(x0, cx - 0.80 * w), cx - 0.20 * w); x0 = min(max(x0, 0), W - w)      # 얼굴이 틀 가장자리에 붙지 않게
        return w, x0
    w, cx0 = frame(tx, S_MIN, True)
    skew = 0.0
    if SKEW > 0 and k not in KEEP:                              # v0.19: 그렇게 자른 틀 안에서 인물이 한쪽으로 몰려 있으면 다시 자른다
        dcol = np.where(wgt > DENSE, wgt, 0.0).sum(axis=0)
        def margins(x0, w):                                     # 틀 [x0, x0 + w) 안에서 짙은 먹의 왼쪽 · 오른쪽 여백(틀 폭에 대한 비)
            seg = dcol[int(round(x0)):int(round(x0 + w))]; tot = float(seg.sum())
            if tot <= 0: return 0.0, 0.0
            c = np.cumsum(seg); return float(np.searchsorted(c, tot * 0.03)) / len(seg), 1.0 - float(np.searchsorted(c, tot * 0.97)) / len(seg)
        mL, mR = margins(cx0, w)
        if abs(mL - mR) >= SKEW:
            dtot = float(dcol.sum()); dc = np.cumsum(dcol); dl = float(np.searchsorted(dc, dtot * 0.03)); dr = float(np.searchsorted(dc, dtot * 0.97))
            w2, x2 = frame((dl + dr) / 2.0, S_MIN_SKEW, False); nL, nR = margins(x2, w2)
            if abs(nL - nR) <= abs(mL - mR) - 0.04: skew = mL - mR; w, cx0 = w2, x2       # 나아질 때만 바꾼다
    h = w * H / W
    ytop = quant(rowp, 0.012)
    cy0 = min(max(ytop - 0.02 * H, 0), H - h)
    if (cy - cy0) / h > 0.62: cy0 = min(max(cy - 0.62 * h, 0), H - h)
    if fy - 0.55 * fh < cy0: cy0 = max(0, fy - 0.55 * fh)                                 # 머리 꼭대기는 남긴다
    box = (int(round(cx0)), int(round(cy0)), int(round(cx0 + w)), int(round(cy0 + h)))
    sc = im.crop(box).resize((SW, int(round(SW * H / W))), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.0, 30, 2))
    sc.save(os.path.join(OUTDIR, 'scene', k + '.webp'), 'WEBP', quality=QS, method=6)
    scenes[k] = webp(sc, QS); ts += len(scenes[k])
    rows.append((k, W, H, cx / W, xc / W, (cx - old_x0) / side, (cx - x0) / side, max(padL, padR) / S, w / W, (cx - cx0) / w, (xc - cx0) / w, box, skew))
print('busts', len(busts), 'bytes', tb, 'avg', tb // max(1, len(busts)), '| scenes', len(scenes), 'bytes', ts, 'avg', ts // max(1, len(scenes)))
if fb: print('fallback to previous square portraits:', len(fb))
if noface: print('NO FACE BOX (centre guess used):', noface)
with open(os.path.join(OUTDIR, 'crops.tsv'), 'w', encoding='utf8') as f:
    f.write('# key\tW\tH\t얼굴x(원본)\t먹중심x(원본)\t흉상 얼굴x(전)\t흉상 얼굴x(후)\t흉상 채움\t장면 틀/원본\t장면 얼굴x(후)\t장면 먹중심x(후)\t장면 틀\n')
    for r in rows: f.write('%s\t%d\t%d\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%s\n' % (r[:11] + (','.join(str(v) for v in r[11]),)))
A = np.array([r[3:11] for r in rows])
def cnt(v, lo, hi): return int(((v < lo) | (v > hi)).sum())
print('n = %d' % len(rows))
print('흉상 얼굴 x: 전 평균 %.3f, 0.48~0.52 밖 %d장(0.56 넘음 %d) → 후 평균 %.3f, 밖 %d장(0.56 넘음 %d) | 흰 종이로 채운 그림 %d장(최대 %.0f%%)' % (A[:, 2].mean(), cnt(A[:, 2], 0.48, 0.52), int((A[:, 2] > 0.56).sum()), A[:, 3].mean(), cnt(A[:, 3], 0.48, 0.52), int((A[:, 3] > 0.56).sum()), int((A[:, 4] > 0).sum()), 100 * A[:, 4].max()))
print('장면 얼굴 x: 전 평균 %.3f, 0.55 넘음 %d · 0.65 넘음 %d · 0.45 미만 %d → 후 평균 %.3f, 0.55 넘음 %d · 0.65 넘음 %d · 0.45 미만 %d' % (A[:, 0].mean(), int((A[:, 0] > 0.55).sum()), int((A[:, 0] > 0.65).sum()), int((A[:, 0] < 0.45).sum()), A[:, 6].mean(), int((A[:, 6] > 0.55).sum()), int((A[:, 6] > 0.65).sum()), int((A[:, 6] < 0.45).sum())))
print('장면 먹 중심 x: 전 평균 %.3f, 0.45~0.55 밖 %d → 후 평균 %.3f, 밖 %d | 자른 그림 %d장, 틀 크기 평균 %.2f(최소 %.2f)' % (A[:, 1].mean(), cnt(A[:, 1], 0.45, 0.55), A[:, 7].mean(), cnt(A[:, 7], 0.45, 0.55), int((A[:, 5] < 0.999).sum()), A[:, 5].mean(), A[:, 5].min()))
prev = open(PREV, encoding='utf8').read()
title = re.search(r'^var TITLE_IMG=.*$', prev, re.M).group(0); hanji = re.search(r'^var HANJI_IMG=.*$', prev, re.M).group(0)
if os.environ.get('TITLE'):                                    # v0.18: 제목 그림을 바꾼다(TITLE=<jpg>)
    title = 'var TITLE_IMG="data:image/jpeg;base64,' + base64.b64encode(open(os.environ['TITLE'], 'rb').read()).decode() + '";'
with open(OUTJS, 'w', encoding='utf8') as f:
    f.write('var PORTRAITS={' + ','.join('"%s":"%s"' % (k, base64.b64encode(b).decode()) for k, b in sorted(busts.items())) + '};\n')
    f.write('var SCENES={' + ','.join('"%s":"%s"' % (k, base64.b64encode(b).decode()) for k, b in sorted(scenes.items())) + '};\n')
    f.write(title + '\n' + hanji + '\n')
print('assets.js', os.path.getsize(OUTJS))
