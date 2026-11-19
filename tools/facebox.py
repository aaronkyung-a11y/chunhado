#!/usr/bin/env python3
"""초상(3:4 장면)에서 얼굴 상자를 찾는다. YuNet(onnx) + OpenCV. usage: facebox.py <raw_dir> <out.tsv> [model.onnx]
   out.tsv: key, x, y, w, h(원본 픽셀), score, 이미지 폭, 높이. 못 찾으면 score 0."""
import sys, os, glob, cv2, numpy as np
RAW, OUT = sys.argv[1], sys.argv[2]
M = sys.argv[3] if len(sys.argv) > 3 else '/home/claude/dl_yunet/yunet_2023mar.onnx'
def detect(im):
    H, W = im.shape[:2]; cands = []
    for S, thr in ((640, 0.5), (448, 0.5), (960, 0.5), (800, 0.3), (512, 0.3), (1200, 0.3), (384, 0.3)):
        k = S / max(W, H); w, h = int(round(W * k)), int(round(H * k))
        small = cv2.resize(im, (w, h), interpolation=cv2.INTER_AREA if k < 1 else cv2.INTER_LINEAR)
        r = cv2.FaceDetectorYN.create(M, '', (w, h), thr, 0.3, 50).detect(small)[1]
        if r is not None:
            for f in r: cands.append((float(f[14]), [float(v) / k for v in f[:4]]))
        if cands and max(c[0] for c in cands) >= 0.7 and S == 960: break
    if not cands: return None
    # 가장 믿을 만한 것. 비슷하면 위쪽·큰 얼굴(품에 안긴 아기 같은 작은 얼굴을 피한다)
    top = max(c[0] for c in cands)
    good = [c for c in cands if c[0] >= top - 0.12]
    good.sort(key=lambda c: -(c[1][2] * c[1][3]) * (1.0 if c[1][1] < H * 0.5 else 0.5))
    # 같은 얼굴에 대한 여러 축척의 결과를 평균
    b0 = good[0][1]; same = [c for c in cands if abs((c[1][0] + c[1][2] / 2) - (b0[0] + b0[2] / 2)) < b0[2] * 0.4 and abs((c[1][1] + c[1][3] / 2) - (b0[1] + b0[3] / 2)) < b0[3] * 0.4]
    ws = np.array([c[0] for c in same]); bs = np.array([c[1] for c in same])
    b = (bs * ws[:, None]).sum(0) / ws.sum()
    return float(ws.max()), [float(v) for v in b]
rows = []
for p in sorted(glob.glob(os.path.join(RAW, '*.png'))):
    k = os.path.basename(p)[:-4]; im = cv2.imread(p); H, W = im.shape[:2]
    d = detect(im)
    rows.append([k] + ([round(v, 1) for v in d[1]] + [round(d[0], 3)] if d else [0, 0, 0, 0, 0]) + [W, H])
with open(OUT, 'w') as f:
    for r in rows: f.write('\t'.join(str(v) for v in r) + '\n')
miss = [r[0] for r in rows if r[5] == 0]
print('faces', len(rows) - len(miss), '/', len(rows), 'missing:', miss)
