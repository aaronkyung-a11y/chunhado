#!/usr/bin/env python3
"""버전 스냅샷을 나눈 꼴로 둔다(v0.18~): python3 tools/snap_split.py <버전> [큰 그림을 빌려 쓸 버전]     (먼저 tools/build.py --split)
   둘째 인자(v0.18.1~): 그림이 그 버전과 바이트까지 같으면 큰 그림 파일을 새로 두지 않고 그 버전의 것을 받아 온다(다르면 멈춘다) — 9MiB 를 또 올리지 않으려고.
   왜: 한 파일로 만든 판(dist/index.html)이 21MiB 를 넘어, 아티팩트에 올릴 수 있는 파일 하나의 크기(20MiB)를 넘었다.
   그래서 스냅샷도 아티팩트에 올리는 판처럼 둘로 둔다 — versions/chunhado-v<버전>.html + versions/chunhado-v<버전>.scenes.json
   (dist/artifact/index.html 에서 큰 그림을 받아 오는 주소 data/scenes.json 한 곳만 옆의 파일 이름으로 바꾼 것이다. 나머지는 바이트까지 같다)"""
import os, sys, shutil, hashlib
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
ver = sys.argv[1]; borrow = sys.argv[2] if len(sys.argv) > 2 else None
def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()
new = os.path.join(ROOT, 'dist', 'artifact', 'data', 'scenes.json')
if borrow:
    old = os.path.join(ROOT, 'versions', 'chunhado-v%s.scenes.json' % borrow)
    assert sha(old) == sha(new), '큰 그림이 v%s 와 다르다 — 빌려 쓸 수 없다' % borrow
src = open(os.path.join(ROOT, 'dist', 'artifact', 'index.html'), encoding='utf-8').read()
a, b = "fetch('data/scenes.json')", "fetch('chunhado-v%s.scenes.json')" % (borrow or ver)
assert src.count(a) == 1, src.count(a)
out = os.path.join(ROOT, 'versions', 'chunhado-v%s.html' % ver)
src = src.replace(a, b)
# v0.19: 영상은 스냅샷 옆이 아니라 한 칸 위의 video/ 에 있다(판마다 따로 두지 않는다 — 지금 올라 있는 영상을 같이 쓴다)
for va, vb in (("a.src = 'video/' + name + '.mp4'", "a.src = '../video/' + name + '.mp4'"), ("b.src = 'video/' + name + '.webm'", "b.src = '../video/' + name + '.webm'")):
    if va in src: assert src.count(va) == 1; src = src.replace(va, vb)
# v0.24: 그림 묶음(data/por-… · data/scn-… — 이름에 내용의 지문이 있다)도 한 칸 위의 data/ 에 있는 것을 같이 쓴다
src = src.replace('"data/por-', '"../data/por-').replace('"data/scn-', '"../data/scn-')
open(out, 'w', encoding='utf-8', newline='\n').write(src)
if borrow: print('snapshot', out, os.path.getsize(out), '· 큰 그림은 v%s 의 것(지문이 같다)' % borrow)
else:
    shutil.copy(new, os.path.join(ROOT, 'versions', 'chunhado-v%s.scenes.json' % ver))
    print('snapshot', out, os.path.getsize(out), '+ scenes', os.path.getsize(os.path.join(ROOT, 'versions', 'chunhado-v%s.scenes.json' % ver)))
