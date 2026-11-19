#!/usr/bin/env python3
"""v0.7 초상 보강 프롬프트. 인물마다 v0.5 그림을 본으로 넣고(얼굴·차림·포인트색 유지) 더 강한 연출로 다시 그린다.
usage: por7_prompt.py batch <key...>   → generate_image_batch 에 넣을 requests(JSON)
       por7_prompt.py text <key>       → 프롬프트 전문
장면은 art/por7_scenes.tsv(이번에 새로 쓴 것)가 있으면 그것, 없으면 v0.5 장면(art/por5_scenes*.tsv)."""
import sys, os, json
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A_M = "Image 1 = this character (keep his face, age, facial hair, headgear, costume and accent color). Repaint him far more powerfully as a dramatic East Asian ink-brush illustration: "
A_F = "Image 1 = this character (keep her hairstyle, ornaments, costume and accent color). Repaint her far more strikingly as a dramatic East Asian ink-brush illustration, an adult woman with a clearly beautiful face: "
B = " Dynamic camera angle, strong foreshortening, heroic proportions, intense expression, sweeping motion; thick black brushwork, gray wash, dry-brush, ink splatter; one accent color only. Vertical; head fully visible, at least 1/5 of picture height; a quarter left as blank white paper; lower body fades into dry brush. Pure white background, no text, seal or border."
sc = {}; fem = set()
for fn in ('por5_scenes_pilot.tsv', 'por5_scenes.tsv', 'por5_scenes_f.tsv', 'por7_scenes.tsv'):
    p = os.path.join(ROOT, 'art', fn)
    if not os.path.exists(p): continue
    for l in open(p, encoding='utf8'):
        if l.startswith('#') or not l.strip(): continue
        k, t = l.rstrip('\n').split('\t')[:2]; sc[k] = t
        if fn.endswith('_f.tsv'): fem.add(k)
fem |= {'diaochan', 'gf1'}
ids = {}; order = {}
for l in open(os.path.join(ROOT, 'art/por5_ids.tsv'), encoding='utf8'):
    if l.strip() and not l.startswith('#'): k, n, j = l.rstrip('\n').split('\t'); ids[k] = j
for l in open(os.path.join(ROOT, 'art/por5_plan.tsv'), encoding='utf8'):
    if l.strip(): p = l.rstrip('\n').split('\t'); order[p[1]] = int(p[0])
def text(k): return (A_F if k in fem else A_M) + sc[k] + B
if __name__ == '__main__':
    if sys.argv[1] == 'text': print(text(sys.argv[2]))
    elif sys.argv[1] == 'batch':
        reqs = [{"index": order[k], "params": {"model": "gpt_image_2_6", "aspect_ratio": "3:4", "resolution": "1k", "quality": "high", "medias": [{"role": "image_references", "value": ids[k]}], "prompt": text(k)}} for k in sys.argv[2:]]
        print(json.dumps(reqs, ensure_ascii=False, separators=(',', ':')))
    elif sys.argv[1] == 'fem': print(sorted(fem))
