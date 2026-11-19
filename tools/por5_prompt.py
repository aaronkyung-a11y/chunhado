#!/usr/bin/env python3
"""v0.5 초상 프롬프트: 머리말 + 장면(art/por5_scenes*.tsv) + 맺음말. usage: por5_prompt.py plan | text <key>"""
import sys, os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A_M = "Image 1 = the character and the painting style. Keep his face, age, facial hair, hairstyle, headgear and costume, and the same freehand East Asian ink-brush manner: bold black brush shapes, soft gray wash, dry-brush edges, face in fine ink lines on blank paper, with the same single accent color as image 1 and no other colors. New composition, not a frontal bust: "
A_F = "Image 1 = the character and the painting style. Keep her face, age, hairstyle, hair ornaments and costume, and the same freehand East Asian ink-brush manner: bold black brush shapes, soft gray wash, dry-brush edges, face in fine ink lines on blank paper, with the same single accent color as image 1 and no other colors. New composition, not a frontal bust: "
B = " Vertical half-length figure in three-quarter view, never facing the viewer straight on; head in the upper half of the picture, large (headgear top to chin about a third of the picture height), face fully visible. Props may run off the edges. At least a third of the picture is empty white paper; the lower body dissolves into dry brush strokes. Pure white #FFFFFF background, no paper texture, border, text or seal."
PILOT = ['guanyu', 'zhangfei', 'liubei', 'caocao', 'lubu', 'zhugeliang', 'zhaoyun', 'diaochan', 'sunce', 'xiahoudun', 'huangzhong', 'zhouyu']
plan = [l.rstrip('\n').split('\t') for l in open(os.path.join(ROOT, 'art/por5_plan.tsv'), encoding='utf8') if l.strip()]
sc = {}; fem = set()
for fn in ('por5_scenes.tsv', 'por5_scenes_f.tsv'):
    for l in open(os.path.join(ROOT, 'art', fn), encoding='utf8'):
        if l.startswith('#') or not l.strip(): continue
        k, t = l.rstrip('\n').split('\t'); sc[k] = t
        if fn.endswith('_f.tsv'): fem.add(k)
def text(k): return (A_F if k in fem else A_M) + sc[k] + B
if __name__ == '__main__':
    if sys.argv[1] == 'plan':
        rest = [p for p in plan if p[1] not in PILOT]
        for i in range(0, len(rest), 12):
            print('# batch', i // 12 + 1)
            for p in rest[i:i + 12]: print(p[0], p[1], p[3], 'F' if p[1] in fem else '')
    elif sys.argv[1] == 'text': print(text(sys.argv[2]))
