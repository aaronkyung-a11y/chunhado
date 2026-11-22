#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.20 거점 하나를 길 위에 더한다: 홍농(弘農) — 함곡관과 동관 사이.   ("낙양하고 장안 사이에 홍농이라는 도시가 있지 않나?")
 - 거점 목록의 '맨 뒤'에 붙인다(앞선 거점의 번호가 그대로라야 옛 저장이 맞는다).
 - 두 거점을 잇던 길(edge)을 둘로 나눈다. 길이 = 길 위의 걸음 수.
 - 성이 서는 칸은 평지(p)로, 길 표시는 지운다(다른 성과 같게). 부지는 tools/add_plots.py 가 붙인다.
usage: add_base20.py <src/mapdata.js> <build/mapdata.json>      두 번 돌려도 같다(이미 있으면 그만둔다)."""
import sys, json, re
SRC, JS = sys.argv[1], sys.argv[2]
NAME, A, B, AT, SZ = '홍농', '함곡관', '동관', (112, 100), 'S'
s = open(SRC, encoding='utf8').read()
m = re.match(r'^(var MAPDATA\s*=\s*)(.*?)(;\s*)$', s, re.S); D = json.loads(m.group(2))
M = json.load(open(JS, encoding='utf8'))
if any(b['n'] == NAME for b in D['bases']): print('already there'); sys.exit(0)
W = D['W']; names = [b['n'] for b in D['bases']]; ia, ib = names.index(A), names.index(B)
ei = [i for i, e in enumerate(D['edges']) if set(e[:2]) == {ia, ib}]; assert len(ei) == 1, ei
ei = ei[0]; path = [tuple(p) for p in M['paths'][ei]]
if path[0] != (D['bases'][ia]['c'], D['bases'][ia]['r']): path.reverse()
assert path[0] == (D['bases'][ia]['c'], D['bases'][ia]['r']) and path[-1] == (D['bases'][ib]['c'], D['bases'][ib]['r'])
k = path.index(AT); nid = len(D['bases'])
def put(st, i, ch): return st[:i] + ch + st[i + 1:]
hk = AT[1] * W + AT[0]
for T in (D, M):
    T['bases'].append({'n': NAME, 'k': 'city', 'c': AT[0], 'r': AT[1], 'sz': SZ})
    T['edges'][ei] = [ia, nid, k]; T['edges'].append([nid, ib, len(path) - 1 - k])
    for key in ('t', 't0', 'traw', 'traw0'):
        if key in T: T[key] = put(T[key], hk, 'p')
    T['road'] = put(T['road'], hk, '0')
    T['plots'][NAME] = []
M['paths'][ei] = [list(p) for p in path[:k + 1]]; M['paths'].append([list(p) for p in path[k:]])
if 'basesFull' in M: M['basesFull'].append({'name': NAME, 'kind': 'city', 'c': AT[0], 'r': AT[1], 'size': SZ, 'approx': True})
open(SRC, 'w', encoding='utf8').write(m.group(1) + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + m.group(3))
json.dump(M, open(JS, 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
print('added', NAME, 'id', nid, 'at', AT, '| edges', D['edges'][ei], D['edges'][-1], '| bases', len(D['bases']), 'edges', len(D['edges']))
