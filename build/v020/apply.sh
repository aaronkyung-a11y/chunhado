#!/bin/bash
# v0.19.1 의 소스(build/*.v0191.*)에 build/v020/s*.py 를 차례로 입혀 src/ 를 만든다(다시 돌려도 같다).  bash build/v020/apply.sh
# 지도 자료(홍농): 0.19.1 의 mapdata 에 tools/add_base20.py + tools/add_plots.py.
# 바탕 그림 · 미니맵(build/terrain.jpg · src/map3d.js 의 mini)은 따로: bash build/v020/terrain.sh (1~2분 걸린다. 한 번 만들면 다시 돌릴 일이 없다)
set -e
cd "$(dirname "$0")/../.."
for f in ai core data fx ui3d ui_panels duel voice bios cine roster; do cp build/$f.v0191.js src/$f.js; done
cp build/style.v0191.css src/style.css; cp build/index.v0191.html src/index.html
cp build/mapdata.v0191.js src/mapdata.js; cp build/mapdata.v0191.json build/mapdata.json
python3 tools/add_base20.py src/mapdata.js build/mapdata.json > /dev/null
python3 tools/add_plots.py src/mapdata.js build/mapdata.json > /dev/null
n=0
for p in build/v020/s*.py; do python3 "$p" > /dev/null; n=$((n+1)); done
for f in ai core data fx ui3d ui_panels duel voice bios cine roster mapdata; do node --check src/$f.js; done
echo "applied: $n patches"
