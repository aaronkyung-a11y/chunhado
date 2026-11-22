#!/usr/bin/env python3
"""버전 스냅샷을 나눈 꼴로 둔다(v0.18~): python3 tools/snap_split.py <버전>     (먼저 tools/build.py --split)
   왜: 한 파일로 만든 판(dist/index.html)이 21MiB 를 넘어, 아티팩트에 올릴 수 있는 파일 하나의 크기(20MiB)를 넘었다.
   그래서 스냅샷도 아티팩트에 올리는 판처럼 둘로 둔다 — versions/chunhado-v<버전>.html + versions/chunhado-v<버전>.scenes.json
   (dist/artifact/index.html 에서 큰 그림을 받아 오는 주소 data/scenes.json 한 곳만 옆의 파일 이름으로 바꾼 것이다. 나머지는 바이트까지 같다)"""
import os, sys, shutil
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
ver = sys.argv[1]
src = open(os.path.join(ROOT, 'dist', 'artifact', 'index.html'), encoding='utf-8').read()
a, b = "fetch('data/scenes.json')", "fetch('chunhado-v%s.scenes.json')" % ver
assert src.count(a) == 1, src.count(a)
out = os.path.join(ROOT, 'versions', 'chunhado-v%s.html' % ver)
open(out, 'w', encoding='utf-8', newline='\n').write(src.replace(a, b))
shutil.copy(os.path.join(ROOT, 'dist', 'artifact', 'data', 'scenes.json'), os.path.join(ROOT, 'versions', 'chunhado-v%s.scenes.json' % ver))
print('snapshot', out, os.path.getsize(out), '+ scenes', os.path.getsize(os.path.join(ROOT, 'versions', 'chunhado-v%s.scenes.json' % ver)))
