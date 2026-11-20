#!/usr/bin/env python3
"""v0.8 건설 부지 늘리기: 성마다 부지를 S 6→10, M 8→13, L 10→16 곳으로.   ("건설 공간이 너무 적어")
 - 이미 있는 부지는 순서까지 그대로 두고 뒤에 덧붙인다(저장 파일의 부지 번호가 그대로 맞는다).
 - 새 부지: 성에서 2~4칸, 길·거점·다른 부지가 아니고, 물·산·바다·변경이 아닌 땅. 다른 거점에서 2칸 넘게 떨어진 곳.
   고르는 순서: 이미 있는 부지와 붙은 칸 → 평지 > 황무지 > 구릉 > 숲 → 성에서 가까운 칸. 지형은 바꾸지 않는다(v0.2 생성기는 부지를 평지로 바꿨다).
 - 성 바로 옆 칸(1칸)은 더 쓰지 않는다: 출진할 자리와 성을 에워쌀 자리를 남겨 둔다.
usage: add_plots.py <mapdata.js> [더 고칠 mapdata.json …]      → 파일을 그 자리에서 고치고, 성마다 덧붙인 칸을 적는다
   이미 목표 수를 채운 성은 건드리지 않으므로 두 번 돌려도 같다."""
import sys, json, re
NPLOT = {'L': 16, 'M': 13, 'S': 10}
TPREF = {'p': 0, 'd': 1, 'h': 2, 'f': 3}
src = sys.argv[1]; s = open(src, encoding='utf8').read()
m = re.match(r'^(var MAPDATA\s*=\s*)(.*?)(;\s*)$', s, re.S); D = json.loads(m.group(2))
W, H, T, RD, bases = D['W'], D['H'], D['t'], D['road'], D['bases']
def K(c, r): return r * W + c
def cube(c, r): x = c - ((r - (r & 1)) >> 1); return x, -x - r, r
def dist(a, b):
    ax, ay, az = cube(*a); bx, by, bz = cube(*b); return max(abs(ax - bx), abs(ay - by), abs(az - bz))
def nbrs(c, r):
    d = [(1, 0), (-1, 0), (0, -1), (1, -1), (0, 1), (1, 1)] if r & 1 else [(1, 0), (-1, 0), (-1, -1), (0, -1), (-1, 1), (0, 1)]
    return [(c + a, r + b) for a, b in d if 0 <= c + a < W and 0 <= r + b < H]
basehex = {(b['c'], b['r']) for b in bases}
claimed = {tuple(h) for v in D['plots'].values() for h in v}
added = {}; short = []
for b in bases:
    if b['k'] != 'city': continue
    ch = (b['c'], b['r']); cur = [tuple(h) for h in D['plots'][b['n']]]; want = NPLOT[b['sz']]
    pool = []
    for r in range(ch[1] - 4, ch[1] + 5):
        for c in range(ch[0] - 5, ch[0] + 6):
            h = (c, r)
            if not (0 <= c < W and 0 <= r < H): continue
            d = dist(ch, h)
            if d < 2 or d > 4 or h in basehex or h in claimed or RD[K(c, r)] == '1' or T[K(c, r)] not in TPREF: continue
            if any(dist(h, (o['c'], o['r'])) <= 2 for o in bases if (o['c'], o['r']) != ch): continue
            pool.append(h)
    new = []
    while len(cur) + len(new) < want and pool:
        have = set(cur) | set(new)
        def key(h): return (0 if any(n in have for n in nbrs(*h)) else 1, TPREF[T[K(*h)]], dist(ch, h), h[1], h[0])
        pool.sort(key=key); new.append(pool.pop(0))
    for h in new: claimed.add(h)
    if len(cur) + len(new) < want: short.append((b['n'], len(cur) + len(new), want))
    if new: added[b['n']] = new; D['plots'][b['n']] = [list(h) for h in cur + new]
out = m.group(1) + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + m.group(3)
open(src, 'w', encoding='utf8').write(out)
for p in sys.argv[2:]:
    J = json.load(open(p, encoding='utf8')); J['plots'] = D['plots']; json.dump(J, open(p, 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
tot = sum(len(v) for v in D['plots'].values()); terr = {}
for n, v in added.items():
    for h in v: terr[T[K(*h)]] = terr.get(T[K(*h)], 0) + 1
print('cities', sum(1 for b in bases if b['k'] == 'city'), '| plots total', tot, '| added', sum(len(v) for v in added.values()), 'on terrain', terr, '| short', short)
for b in bases:
    if b['n'] in added: print('  %-3s %s %2d → %2d  + %s' % (b['n'], b['sz'], len(D['plots'][b['n']]) - len(added[b['n']]), len(D['plots'][b['n']]), ' '.join('%d,%d(%s%d)' % (h[0], h[1], T[K(*h)], dist((b['c'], b['r']), h)) for h in added[b['n']])))
