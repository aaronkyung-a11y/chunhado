#!/bin/bash
# v0.20 바탕 그림 손질: 0.19.1 의 그림 위에 물(쪽빛) · 높낮이(겹과 등고선) · 홍농 둘레의 여백을 덧칠하고 미니맵을 바꾼다.
# 먼저 bash build/v020/apply.sh (build/mapdata.json 에 홍농과 그 부지가 있어야 한다).
set -e
cd "$(dirname "$0")/../.."
cp build/map3d.v0191.js src/map3d.js
python3 tools/terrain20.py build/terrain.v0191.jpg build/mapdata.json src/map3d.js build/terrain.jpg 홍농
