#!/bin/bash
# v0.16 의 소스에 build/v017/p*.py 를 차례로 입혀 src/ 를 만든다(다시 돌려도 같다).  bash build/v017/apply.sh
# 명부(src/roster.js)와 초상(src/assets.js)은 패치가 아니라 도구로 다시 만든 것이다 — 한 번만 하면 된다(그 전의 것은 build/roster.v016.js · build/assets.v016.js):
#   python3 tools/make_roster.py <群雄割據 삼국지 index.html> src/roster.js        # 더한 무장은 tools/roster17.py 에(맨 뒤에 붙는다 — 앞쪽 301명의 번호는 그대로)
#   새 초상 39장: tools/por17_prompt.py(문구) → Higgsfield → tools/dl_por17.py → art/raw17/ → tools/facebox.py art/raw17 art/por17_faces.tsv
#   art/raw17m = art/raw93m(그동안의 그림) + art/raw17(새 그림), art/por17_faces_all.tsv = art/por93_faces_all.tsv + art/por17_faces.tsv
#   FOCUS=art/por7_focus.tsv python3 tools/make_assets_v08.py art/raw17m art/por17_faces_all.tsv art/por17_out src/assets.js build/assets.v093.js src/roster.js 256 320 72 52
set -e
cd "$(dirname "$0")/../.."
for f in ai core data fx ui3d ui_panels duel voice; do cp build/$f.v016.js src/$f.js; done
cp build/style.v016.css src/style.css; cp build/index.v016.html src/index.html; cp build/sfxdata.v016.js src/sfxdata.js
n=0
for p in build/v017/p*.py; do python3 "$p" > /dev/null; n=$((n+1)); done
for f in ai core data fx ui3d ui_panels duel voice; do node --check src/$f.js; done
echo "applied: $n patches"
