# -*- coding: utf-8 -*-
"""v0.4 수묵 스프라이트: 흰 바탕을 걷어 내되, 바깥으로 번진 담묵은 반투명 먹으로 남긴다 → 여백 잘라내기 → WebP → src/sprites.js
사용: make_sprites_ink.py <raw_dir> <out_dir> <out_js>"""
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
PAPER = np.array([250, 247, 239], np.float32)
out = {}
for key, (size, ay) in SPEC.items():
    im = np.asarray(Image.open(os.path.join(RAW, key + '.png')).convert('RGB')).astype(np.float32)
    # 흰 점 맞추기(종이처럼 찍힌 바탕 보정): 가장자리 띠의 밝은 쪽
    edge = np.concatenate([im[:10].reshape(-1, 3), im[-10:].reshape(-1, 3), im[:, :10].reshape(-1, 3), im[:, -10:].reshape(-1, 3)])
    wp = np.maximum(np.percentile(edge, 60, axis=0), 215.0)
    im = np.clip(im / wp[None, None, :] * 255.0, 0, 255)
    mn = im.min(axis=2); mx = im.max(axis=2); unit = key.startswith('u_')
    # 바깥: 가장자리에서 '밝은 칸'으로 이어진 곳. 선 사이의 좁은 틈으로 안까지 새어 들지 않게 한 번 깎았다가 되돌린다
    light = (mn >= (232 if unit else 198)) & (mx - mn <= 26)
    core = ndi.binary_erosion(light, iterations=3, border_value=1)
    lab, n = ndi.label(core)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    outside = ndi.binary_dilation(np.isin(lab, list(border)), iterations=4) & light
    # 바깥의 먹은 흰 종이 위의 먹으로 보고 투명도로 바꾼다: 밝을수록 투명
    a_out = np.clip((252.0 - mn) / (26.0 if unit else 64.0), 0.0, 1.0)
    alpha = np.where(outside, a_out, 1.0).astype(np.float32)
    alpha = np.minimum(alpha, ndi.gaussian_filter(alpha, 0.6) + 0.5)          # 톱니 완화
    a3 = np.clip(alpha, 0.03, 1)[..., None]
    rgb = np.where(outside[..., None], np.clip((im - 255.0 * (1 - a3)) / a3, 0, 255), im)
    # 안쪽의 흰 곳은 종이 빛으로(지도 위에서 너무 새하얗지 않게)
    rgb = rgb * (PAPER / 255.0)[None, None, :]
    rgba = np.dstack([rgb, alpha * 255.0]).astype(np.uint8)
    ys, xs = np.where(alpha > 0.06)
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    sp = Image.fromarray(rgba, 'RGBA').crop(box)
    k = size / max(sp.size)
    sp = sp.resize((max(1, round(sp.width * k)), max(1, round(sp.height * k))), Image.LANCZOS)
    arr = np.asarray(sp).astype(np.float32); rgbf = arr[..., :3] / 255.0; al = arr[..., 3] / 255.0
    rgbf = np.clip(rgbf ** (1.55 if unit else 1.15), 0, 1)                     # 줄이면서 옅어진 먹을 눌러 준다(부대는 더 짙게)
    if unit:                                                                   # 부대: 종이 빛 테(짙은 산·숲 위에서도 보이게)
        ring = np.clip(ndi.gaussian_filter(ndi.grey_dilation(al, size=(3, 3)), 0.8), 0, 1)
        oc = PAPER / 255.0
        out_a = np.maximum(al, ring * 0.88)
        rgbf = rgbf * al[..., None] + oc[None, None, :] * (1 - al[..., None])
        al = out_a
    sp = Image.fromarray(np.dstack([rgbf * 255.0, al * 255.0]).astype(np.uint8), 'RGBA')
    sp.save(os.path.join(OUT, key + '.png'))
    bio = io.BytesIO(); sp.save(bio, 'WEBP', quality=86, method=6)
    out[key] = dict(u='data:image/webp;base64,' + base64.b64encode(bio.getvalue()).decode('ascii'), w=sp.width, h=sp.height, ay=ay)
    print(key, sp.size, len(bio.getvalue()), 'wp', [int(v) for v in wp])
with open(OUT_JS, 'w', encoding='utf-8') as f: f.write('var SPRITES=' + json.dumps(out, separators=(',', ':')) + ';\n')
print('sprites.js', os.path.getsize(OUT_JS))
