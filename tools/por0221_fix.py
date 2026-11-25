#!/usr/bin/env python3
"""v0.22.1 초상: 얼굴 상자가 틀렸던 인물만 다시 자른다(다른 그림은 글자 하나 바꾸지 않는다).
   이각: 얼굴 찾기(YuNet)가 술잔을 든 손을 얼굴로 봤다(상자 198 255 231 270, 점수 0.65) → 흉상(정사각)이 손을 가운데 두고 잘려 얼굴이 오른쪽 끝으로 밀렸다.
   손으로 고친 상자(art/por0221_focus.tsv — lijue 490 190 150 170)로 tools/make_assets_v08.py 를 0.18 과 같은 인자로 돌려, 거기서 나온 흉상만 옮긴다.
   장면(3:4)은 그대로 둔다 — 장면은 얼굴과 먹의 무게중심으로 잘라서 이각의 것도 얼굴이 가운데에 있었고, 장면이 바뀌면 아티팩트의 data/scenes.json(9.9MB)을 새로 올려야 한다.
   usage: por0221_fix.py <in_assets.js> <out_assets.js> <key> [key…]"""
import sys, os, io, re, subprocess, tempfile
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC, DST, KEYS = sys.argv[1], sys.argv[2], sys.argv[3:]
tmp = os.path.join(tempfile.mkdtemp(prefix='por0221_'), 'assets_recrop.js')
env = dict(os.environ, TITLE=os.path.join(ROOT, 'art/title18/title.jpg'), FOCUS=os.path.join(ROOT, 'art/por0221_focus.tsv'))
r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools/make_assets_v08.py'), os.path.join(ROOT, 'art/raw18m'), os.path.join(ROOT, 'art/por18_faces_all.tsv'), os.path.join(ROOT, 'art/por0221_out'), tmp,
                    os.path.join(ROOT, 'build/assets.v093.js'), os.path.join(ROOT, 'src/roster.js'), '256', '320', '72', '52'], env=env, capture_output=True, text=True, cwd=ROOT)
assert r.returncode == 0, r.stderr[-600:]
a = io.open(SRC, encoding='utf-8').read(); b = io.open(tmp, encoding='utf-8').read()
def parts(s):
    i0, i1, i2 = s.index('var PORTRAITS'), s.index('var SCENES'), s.index('var TITLE_IMG'); return i0, i1, i2
def get(s, lo, hi, k):
    m = re.search(r'"%s":"([A-Za-z0-9+/=]+)"' % re.escape(k), s[lo:hi]); assert m, k; return m.group(1), lo + m.start(1), lo + m.end(1)
n = 0
for k in KEYS:
    for sec in (0,):                                            # 0 = 흉상(PORTRAITS). 1 = 장면(SCENES)은 옮기지 않는다
        pa, pb = parts(a), parts(b)
        old, s0, s1 = get(a, pa[sec], pa[sec + 1], k); new, _, _ = get(b, pb[sec], pb[sec + 1], k)
        if old != new: a = a[:s0] + new + a[s1:]; n += 1
        print('%s %s: %d → %d 글자%s' % (k, ('흉상', '장면')[sec], len(old), len(new), '' if old != new else ' (같음)'))
io.open(DST, 'w', encoding='utf-8', newline='\n').write(a)
print('바꾼 그림 %d장 → %s %d바이트' % (n, os.path.relpath(DST, ROOT), len(a.encode('utf-8'))))
