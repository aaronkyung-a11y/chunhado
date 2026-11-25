#!/usr/bin/env python3
"""dl_por17.py 에 줄 '~HHMMSS key key …' 줄을 만든다: 번호 구간마다 그 묶음을 넣은 시각(UTC, 어림)을 준다.
usage: POR=25 dl_lines.py HHMMSS:from-to[,n,n…] …      예) 114535:1-24 115355:253,157,170,183"""
import sys, os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); POR = os.environ.get('POR', '25')
key = {}
for l in open(os.path.join(ROOT, 'art/por%s_ids.tsv' % POR), encoding='utf8'):
    if l.strip() and not l.startswith('#'): a = l.split(); key[int(a[0])] = a[1]
for arg in sys.argv[1:]:
    t, spec = arg.split(':'); idx = []
    for p in spec.split(','):
        if '-' in p: a, b = p.split('-'); idx += list(range(int(a), int(b) + 1))
        else: idx.append(int(p))
    print('~' + t + ' ' + ' '.join(key[i] for i in idx if i in key))
