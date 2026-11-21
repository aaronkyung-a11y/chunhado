#!/usr/bin/env python3
"""v0.17 여성 초상 39장(새 여성 무장 38명 + 그동안 공용 그림을 쓰던 대교). 본(참조 그림) 없이 글만으로 그린다 — 화풍 문구는 v0.7 · v0.9.3 과 같다.
usage: por17_prompt.py keys            → 번호 · key · 이름
       por17_prompt.py text <key>      → 프롬프트 전문
       por17_prompt.py batch <key...>  → generate_image_batch 에 넣을 requests(JSON)"""
import sys, os, json
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = "A dramatic East Asian ink-brush illustration of a woman of the late Han dynasty of China (around AD 200), an adult woman with a clearly beautiful face. Subject: "
A_OLD = "A dramatic East Asian ink-brush illustration of a woman of the late Han dynasty of China (around AD 200). Subject: "
B = (" Composition (important): her head sits on the vertical center line of the picture - horizontally centered, not toward the right or left edge - and the figure is centered, "
     "with about equal blank white paper on the left and on the right. Dynamic camera angle, sweeping motion of sleeves and hair, lively expression; "
     "thick black brushwork, gray wash, dry-brush, ink splatter; one accent color only (%s). Vertical; head fully visible, at least 1/5 of picture height; lower body fades into dry brush. "
     "Pure white background, no text, seal or border.")
OLD = {'wuguotai', 'xumu'}
rows = {}; order = []
for l in open(os.path.join(ROOT, 'art/por17_scenes.tsv'), encoding='utf8'):
    if l.startswith('#') or not l.strip(): continue
    i, k, n, c, t = l.rstrip('\n').split('\t'); rows[k] = (int(i), n, c, t); order.append(k)
def text(k): return (A_OLD if k in OLD else A) + rows[k][3] + (B % rows[k][2])
if __name__ == '__main__':
    if sys.argv[1] == 'keys': print(' '.join('%d:%s:%s' % (rows[k][0], k, rows[k][1]) for k in order))
    elif sys.argv[1] == 'text': print(text(sys.argv[2]))
    elif sys.argv[1] == 'batch':
        ks = order if sys.argv[2:] == ['all'] else sys.argv[2:]
        print(json.dumps([{"index": rows[k][0], "params": {"model": "gpt_image_2_6", "aspect_ratio": "3:4", "resolution": "1k", "quality": "high", "prompt": text(k)}} for k in ks], ensure_ascii=False, separators=(',', ':')))
