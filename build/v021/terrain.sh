#!/bin/bash
# v0.21 바탕 그림: 0.20 의 그림 위에 관문의 능선을 그려 넣고 미니맵을 바꾼다.  먼저 bash build/v021/apply.sh (build/mapdata.json 에 walls 가 있어야 한다).
set -e
cd "$(dirname "$0")/../.."
cp build/map3d.v020.js src/map3d.js
python3 tools/terrain21.py build/terrain.v020.jpg build/mapdata.json src/map3d.js build/terrain.jpg
