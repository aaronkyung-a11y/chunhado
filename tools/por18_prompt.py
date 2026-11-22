#!/usr/bin/env python3
"""v0.18 초상 60장 — 공용 초상을 쓰던 이름난 무장에게 제 초상을. 본(참조 그림) 없이 글만으로 그린다(화풍 문구는 v0.7 · v0.9.3 · v0.17 과 같은 것을 줄인 것).
usage: por18_prompt.py keys | text <key> | batch <key...>"""
import sys, os, json
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = "A dramatic East Asian ink-brush illustration of a man of the Three Kingdoms era of China (around AD 200). Subject: "
B = (" Composition: his head on the vertical center line, figure centered, equal blank white paper left and right. Dynamic angle, heroic proportions, intense expression, sweeping motion; "
     "thick black brushwork, gray wash, dry-brush, ink splatter; one accent color only (%s). Vertical; head fully visible, at least 1/5 of picture height; lower body fades into dry brush. "
     "Pure white background, no text, seal or border.")
rows = {}; order = []
for l in open(os.path.join(ROOT, 'art/por18_scenes.tsv'), encoding='utf8'):
    if l.startswith('#') or not l.strip(): continue
    i, k, n, c, t = l.rstrip('\n').split('\t'); rows[k] = (int(i), n, c, t); order.append(k)
def text(k): return A + rows[k][3] + (B % rows[k][2])
if __name__ == '__main__':
    if sys.argv[1] == 'keys': print(' '.join('%d:%s:%s' % (rows[k][0], k, rows[k][1]) for k in order))
    elif sys.argv[1] == 'text': print(text(sys.argv[2]))
    elif sys.argv[1] == 'batch':
        ks = order if sys.argv[2:] == ['all'] else sys.argv[2:]
        print(json.dumps([{"index": rows[k][0], "params": {"model": "gpt_image_2_6", "aspect_ratio": "3:4", "resolution": "1k", "quality": "high", "prompt": text(k)}} for k in ks], ensure_ascii=False, separators=(',', ':')))
