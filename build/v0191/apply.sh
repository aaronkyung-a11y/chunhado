#!/bin/bash
# v0.19 의 소스(build/*.v019.*)에 build/v0191/r*.py 를 입혀 src/ 를 만든다(다시 돌려도 같다).  bash build/v0191/apply.sh
# 열전 · 그림 · 영상 파일은 0.19 그대로다.
set -e
cd "$(dirname "$0")/../.."
for f in ai core data fx ui3d ui_panels duel voice bios cine; do cp build/$f.v019.js src/$f.js; done
cp build/style.v019.css src/style.css; cp build/index.v019.html src/index.html
n=0
for p in build/v0191/r*.py; do python3 "$p" > /dev/null; n=$((n+1)); done
for f in ai core data fx ui3d ui_panels duel voice bios cine; do node --check src/$f.js; done
echo "applied: $n patches"
