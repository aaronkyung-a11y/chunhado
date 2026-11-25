# -*- coding: utf-8 -*-
"""fn.py <file> <name…> — 함수 본문을 찾아 찍는다(작업용)."""
import sys, re
s = open(sys.argv[1], encoding='utf-8').read()
for nm in sys.argv[2:]:
    m = re.search(r'(^|\n)(function ' + re.escape(nm) + r'\s*\()', s)
    if not m: print('?? ' + nm); continue
    i = m.start(2); j = s.index('{', i); d = 0; k = j
    while True:
        c = s[k]
        if c == '{': d += 1
        elif c == '}':
            d -= 1
            if d == 0: break
        k += 1
    ln = s.count('\n', 0, i) + 1
    print('@%d %s' % (ln, s[i:k + 1]))
