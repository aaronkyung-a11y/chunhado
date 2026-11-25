#!/bin/bash
# v0.24 의 소스(build/*.v024.*)에 build/v025/s*.py 를 입혀 src/ 를 만든다(다시 돌려도 같다).  bash build/v025/apply.sh
# 그림 묶음(src/assets_p253.js): 개별 초상 253장 — tools/por25_prompt.py(글 — 장면은 art/por25_scenes.tsv) → art/raw25(그림) → tools/facebox.py → tools/make_pack24.py. 원본 그림이 없으면 있던 묶음을 그대로 쓴다.
# 명부(src/roster.js): tools/roster23.py 를 POOL=1 P253=… 로 — 공용 초상을 쓰던 253명에게 제 초상(묶음에 그림이 있는 사람만), 나머지는 공용 초상.
# 소리(src/sfxdata.js): tools/make_audio_v025.py — 순찰의 소리를 바꾼다(원본 소리 audio25/raw 가 없으면 build/sfxdata.v025.js 를 그대로 쓴다).
set -e
cd "$(dirname "$0")/../.."
for f in ai core data fx ui3d ui_panels duel voice bios cine roster mapdata map3d sprites sfxdata assets assets_pool; do cp build/$f.v024.js src/$f.js; done
cp build/style.v024.css src/style.css; cp build/index.v024.html src/index.html
if [ -d art/raw25 ] && [ -f art/por25_faces.tsv ]; then python3 tools/make_pack24.py p253 art/raw25 art/por25_faces.tsv art/por25_out > build/v025/pack.log 2>&1; fi
POOL=1 P253=art/por25_scenes.tsv python3 tools/roster23.py > build/v025/roster.log
if [ -f tools/make_audio_v025.py ] && [ -d audio25/raw ]; then python3 tools/make_audio_v025.py > build/v025/audio.log; elif [ -f build/sfxdata.v025.js ]; then cp build/sfxdata.v025.js src/sfxdata.js; fi
for p in build/v025/s*.py; do python3 "$p"; done
for f in roster ai core data fx ui3d ui_panels duel voice bios cine; do node --check src/$f.js; done
echo "v0.25 applied"
