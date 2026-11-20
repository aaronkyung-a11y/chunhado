#!/usr/bin/env python3
"""v0.9.3 초상 17장 다시 그리기: 큰 그림에서 얼굴이 가로 65%보다 오른쪽에 놓인 그림(art/por8_out/crops.tsv 의 '장면 얼굴x(후)' > 0.65).
 v0.7 문구는 "4분의 1은 빈 종이"라고만 쓰고 어느 쪽인지 정하지 않아 얼굴이 오른쪽으로 몰렸다. 이번에는 지금의 v0.7 그림을 본으로 넣고(얼굴·차림·무기·포인트색·화풍 유지)
 장면은 그대로 두되 '머리를 가로 한가운데에'를 못 박는다.
usage: por93_prompt.py keys            → 다시 그릴 17명
       por93_prompt.py text <key>      → 프롬프트 전문
       por93_prompt.py batch <key...>  → generate_image_batch 에 넣을 requests(JSON)"""
import sys, os, json
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = "Image 1 = the current ink painting of this character. Repaint the same man in exactly the same East Asian ink-brush style: keep his face, age, facial hair, headgear, armor or robe, weapon and the single accent color. Scene: "
B = (" Composition (important): his head sits on the vertical center line of the picture - horizontally centered, not toward the right or left edge - and the figure is centered, "
     "with about equal blank white paper on the left and on the right. Dynamic camera angle, strong foreshortening, heroic proportions, intense expression, sweeping motion; "
     "thick black brushwork, gray wash, dry-brush, ink splatter; one accent color only. Vertical; head fully visible, at least 1/5 of picture height; lower body fades into dry brush. "
     "Pure white background, no text, seal or border.")
def keys():
    out = []
    for l in open(os.path.join(ROOT, 'art/por8_out/crops.tsv'), encoding='utf8'):
        if l.startswith('#') or not l.strip(): continue
        p = l.rstrip('\n').split('\t')
        if float(p[9]) > 0.65: out.append((float(p[9]), p[0]))
    return [k for _, k in sorted(out, reverse=True)]
sc = {}
for fn in ('por5_scenes_pilot.tsv', 'por5_scenes.tsv', 'por5_scenes_f.tsv', 'por7_scenes.tsv'):
    p = os.path.join(ROOT, 'art', fn)
    if not os.path.exists(p): continue
    for l in open(p, encoding='utf8'):
        if l.startswith('#') or not l.strip(): continue
        k, t = l.rstrip('\n').split('\t')[:2]; sc[k] = t
ids = {}; order = {}
for l in open(os.path.join(ROOT, 'art/por7_ids.tsv'), encoding='utf8'):          # 본 = 지금의 v0.7 그림
    if l.strip() and not l.startswith('#'): k, n, j = l.rstrip('\n').split('\t'); ids[k] = j
for l in open(os.path.join(ROOT, 'art/por5_plan.tsv'), encoding='utf8'):
    if l.strip(): p = l.rstrip('\n').split('\t'); order[p[1]] = int(p[0])
def text(k): return A + sc[k] + B
if __name__ == '__main__':
    if sys.argv[1] == 'keys': print(' '.join(keys()))
    elif sys.argv[1] == 'text': print(text(sys.argv[2]))
    elif sys.argv[1] == 'batch':
        reqs = [{"index": order[k], "params": {"model": "gpt_image_2_6", "aspect_ratio": "3:4", "resolution": "1k", "quality": "high", "medias": [{"role": "image_references", "value": ids[k]}], "prompt": text(k)}} for k in sys.argv[2:]]
        print(json.dumps(reqs, ensure_ascii=False, separators=(',', ':')))
