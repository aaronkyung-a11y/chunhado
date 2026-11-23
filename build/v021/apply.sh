#!/bin/bash
# v0.20 의 소스(build/*.v020.*)에 build/v021/s*.py 를 차례로 입혀 src/ 를 만든다(다시 돌려도 같다).  bash build/v021/apply.sh
# 지도 자료(관문의 능선): 0.20 의 mapdata 에 tools/gates21.py.
# 바탕 그림(build/terrain.jpg — 능선을 그려 넣는다)은 따로: bash build/v021/terrain.sh
set -e
cd "$(dirname "$0")/../.."
for f in ai core data fx ui3d ui_panels duel voice bios cine roster; do cp build/$f.v020.js src/$f.js; done
cp build/style.v020.css src/style.css; cp build/index.v020.html src/index.html
cp build/mapdata.v020.js src/mapdata.js; cp build/mapdata.v020.json build/mapdata.json
python3 tools/gates21.py src/mapdata.js build/mapdata.json --r=16 > build/v021/gates.log
n=0
for p in build/v021/s*.py; do [ -e "$p" ] || continue; python3 "$p" > /dev/null; n=$((n+1)); done
for f in ai core data fx ui3d ui_panels duel voice bios cine roster mapdata; do node --check src/$f.js; done
echo "applied: $n patches"
