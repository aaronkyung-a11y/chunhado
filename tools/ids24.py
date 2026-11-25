#!/usr/bin/env python3
"""generate_image_batch 의 답("- index N: <작업번호> (pending)")을 표준입력으로 받아 art/por<POR>_ids.tsv(번호 key 작업번호)에 덧붙인다. 주소는 적지 않는다.
usage: POR=24 ids24.py < 답"""
import sys, os, re
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); POR = os.environ.get('POR', '24')
key = {}
for l in open(os.path.join(ROOT, 'art/por%s_scenes.tsv' % POR), encoding='utf8'):
    if l.strip() and not l.startswith('#'): a = l.split('\t'); key[int(a[0])] = a[1]
P = os.path.join(ROOT, 'art/por%s_ids.tsv' % POR)
have = {}
if os.path.exists(P):
    for l in open(P, encoding='utf8'):
        if l.strip() and not l.startswith('#'): a = l.split(); have[a[1]] = a[2]
else: open(P, 'w', encoding='utf8').write('# v0.%s 초상: 번호 key 작업번호(주소는 남기지 않는다)\n' % POR)
n = 0
with open(P, 'a', encoding='utf8') as f:
    for m in re.finditer(r'index (\d+): ([0-9a-f]{8}-[0-9a-f-]{27})', sys.stdin.read()):
        i, job = int(m.group(1)), m.group(2); k = key[i]
        if have.get(k) == job: continue
        f.write('%d\t%s\t%s\n' % (i, k, job)); have[k] = job; n += 1
print('added', n, 'total', len(have))
