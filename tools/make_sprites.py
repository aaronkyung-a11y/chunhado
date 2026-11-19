# -*- coding: utf-8 -*-
"""지도용 스프라이트: 흰 배경 제거(테두리에서 번지는 흰색 + 갇힌 순백 영역) → 여백 잘라내기 → WebP → src/sprites.js
사용: make_sprites.py <raw_dir> <out_dir> <out_js>"""
import sys, os, io, json, base64
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
RAW, OUT, OUT_JS = sys.argv[1:4]
os.makedirs(OUT, exist_ok=True)
# key: (최대 변 px, 기준점 y(아래에서의 비율))
SPEC = {'city_L': (360, 0.30), 'city_M': (340, 0.30), 'city_S': (320, 0.30), 'gate': (340, 0.24),
        'market': (240, 0.33), 'farm': (240, 0.33), 'barracks': (240, 0.30), 'smithy': (240, 0.30), 'stable': (240, 0.33), 'workshop': (240, 0.30), 'mint': (240, 0.30), 'granary': (240, 0.33),
        'u_sword': (200, 0.16), 'u_spear': (200, 0.14), 'u_halberd': (200, 0.14), 'u_bow': (200, 0.16), 'u_cav': (210, 0.16), 'u_ram': (210, 0.18), 'u_trans': (220, 0.16)}
out = {}
for key, (size, ay) in SPEC.items():
    im = np.asarray(Image.open(os.path.join(RAW, key + '.png')).convert('RGB')).astype(np.float32)
    mn = im.min(axis=2); mx = im.max(axis=2)
    white = (mn >= 236) & (mx - mn <= 14)
    lab, n = ndi.label(white)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(border))
    # 갇힌 순백 영역(다리 사이, 창 사이)
    pure = (mn >= 247) & ~bg
    lab2, n2 = ndi.label(pure)
    if n2:
        sizes = ndi.sum(pure, lab2, range(1, n2 + 1))
        bg |= np.isin(lab2, [i + 1 for i, s in enumerate(sizes) if s >= 24])
    alpha = (~bg).astype(np.float32)
    # 가장자리: 흰 기운을 걷어 낸다
    edge = ndi.binary_dilation(bg, iterations=2) & ~bg
    a_e = np.clip((255.0 - mn) / 70.0, 0.0, 1.0)
    alpha[edge] = np.minimum(alpha[edge], a_e[edge])
    a3 = np.clip(alpha, 0.02, 1)[..., None]
    rgb = np.where(edge[..., None], np.clip((im - 255.0 * (1 - a3)) / a3, 0, 255), im)
    rgba = np.dstack([rgb, alpha * 255.0]).astype(np.uint8)
    ys, xs = np.where(alpha > 0.05)
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    sp = Image.fromarray(rgba, 'RGBA').crop(box)
    k = size / max(sp.size)
    sp = sp.resize((max(1, round(sp.width * k)), max(1, round(sp.height * k))), Image.LANCZOS)
    if key.startswith('u_'):                       # 부대: 밝게 + 옅은 테두리(바탕과 구분)
        arr = np.asarray(sp).astype(np.float32); rgbf = arr[..., :3] / 255.0
        rgbf = np.clip(rgbf ** 0.78 * 1.12, 0, 1)
        al = arr[..., 3] / 255.0
        ring = np.clip(ndi.gaussian_filter(ndi.grey_dilation(al, size=(5, 5)), 0.8), 0, 1)
        oc = np.array([0.98, 0.94, 0.80], np.float32)
        out_a = np.maximum(al, ring * 0.9)
        out_rgb = rgbf * al[..., None] + oc[None, None, :] * (1 - al[..., None])
        sp = Image.fromarray(np.dstack([out_rgb * 255.0, out_a * 255.0]).astype(np.uint8), 'RGBA')
    sp.save(os.path.join(OUT, key + '.png'))
    bio = io.BytesIO(); sp.save(bio, 'WEBP', quality=86, method=6)
    out[key] = dict(u='data:image/webp;base64,' + base64.b64encode(bio.getvalue()).decode('ascii'), w=sp.width, h=sp.height, ay=ay)
    print(key, sp.size, len(bio.getvalue()))
with open(OUT_JS, 'w', encoding='utf-8') as f: f.write('var SPRITES=' + json.dumps(out, separators=(',', ':')) + ';\n')
print('sprites.js', os.path.getsize(OUT_JS))
