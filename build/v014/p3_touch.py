#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.14 — 작은 손질.
   · 칸 위에 뜨는 음성의 뜻풀이(.flt.vsay): 숲 · 산 위에서는 글씨가 묻혀서, 종이빛 바탕을 깔았다."""
import os, io
ROOT = os.environ.get('CH_ROOT') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
def rd(n): return io.open(os.path.join(ROOT, 'src', n), encoding='utf-8').read()
def wr(n, s): io.open(os.path.join(ROOT, 'src', n), 'w', encoding='utf-8').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:70])
    return s.replace(a, b)
s = rd('style.css')
s = rep(s, ".flt.vsay { font: 700 14px var(--font-body); color: #2a2620; letter-spacing: 0; }",
           ".flt.vsay { font: 700 13.5px var(--font-body); color: #2a2620; letter-spacing: 0; padding: 2px 7px; background: #f6f1e6ee; border: 1px solid #1b1a1833; border-radius: 2px; text-shadow: none; }")
wr('style.css', s)
print('p3_touch ok')
