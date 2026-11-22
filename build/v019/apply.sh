#!/bin/bash
# v0.18.1 의 소스(build/*.v0181.*)에 build/v019/p*.py 를 차례로 입혀 src/ 를 만든다(다시 돌려도 같다).  bash build/v019/apply.sh
# 새 소스 src/bios.js(열전) · src/cine.js(영상)는 패치가 아니라 그대로 두는 파일이다. 영상 파일은 video/ 에(만든 길은 CHANGELOG 의 v0.19).
# 초상(src/assets.js)은 도구로 다시 만든 것이다 — 한쪽으로 몰린 장면 24장을 다시 잘랐다(그 전의 것은 build/assets.v0181.js):
#   SKEW=0.12 TITLE=art/title18/title.jpg FOCUS=art/por7_focus.tsv python3 tools/make_assets_v08.py art/raw18m art/por18_faces_all.tsv art/por19_out src/assets.js build/assets.v093.js src/roster.js 256 320 72 52
set -e
cd "$(dirname "$0")/../.."
for f in ai core data fx ui3d ui_panels duel voice; do cp build/$f.v0181.js src/$f.js; done
cp build/style.v0181.css src/style.css; cp build/index.v0181.html src/index.html
n=0
for p in build/v019/p*.py; do python3 "$p" > /dev/null; n=$((n+1)); done
for f in ai core data fx ui3d ui_panels duel voice bios cine; do node --check src/$f.js; done
echo "applied: $n patches"
