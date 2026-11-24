#!/bin/bash
# v0.21 의 소스(build/*.v021.*)에 build/v022/s*.py 를 차례로 입혀 src/ 를 만든다(다시 돌려도 같다).  bash build/v022/apply.sh
# 지도 자료(관문의 능선): 능선이 없는 0.20 의 mapdata 에 tools/gates22.py(부지와 성역을 피한다) — 0.21 의 능선을 버리고 다시 세운다.
# 부대 그림(src/sprites.js): 0.21 의 그림에 tools/units22.py(창병의 크기 · 병과의 빛깔).
# 바탕 그림(build/terrain.jpg — 능선을 그려 넣는다)은 따로: bash build/v022/terrain.sh
set -e
cd "$(dirname "$0")/../.."
for f in ai core data fx ui3d ui_panels duel voice bios cine roster; do cp build/$f.v021.js src/$f.js; done
cp build/style.v021.css src/style.css; cp build/index.v021.html src/index.html
cp build/mapdata.v020.js src/mapdata.js; cp build/mapdata.v020.json build/mapdata.json
python3 tools/gates22.py src/mapdata.js build/mapdata.json --r=16 > build/v022/gates.log
if [ -e tools/units22.py ]; then python3 tools/units22.py build/sprites.v021.js src/sprites.js > build/v022/units.log; fi
n=0
for p in build/v022/s*.py; do [ -e "$p" ] || continue; python3 "$p" > /dev/null; n=$((n+1)); done
for f in ai core data fx ui3d ui_panels duel voice bios cine roster mapdata sprites; do node --check src/$f.js; done
echo "applied: $n patches"
