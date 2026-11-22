#!/bin/bash
# v0.18 의 소스(build/*.v018.*)에 build/v0181/q*.py 를 차례로 입혀 src/ 를 만든다(다시 돌려도 같다).  bash build/v0181/apply.sh
# 명부 · 그림 · 소리(src/roster.js · assets.js · sfxdata.js)는 0.18 그대로다.
set -e
cd "$(dirname "$0")/../.."
for f in ai core data fx ui3d ui_panels duel voice; do cp build/$f.v018.js src/$f.js; done
cp build/style.v018.css src/style.css; cp build/index.v018.html src/index.html
n=0
for p in build/v0181/q*.py; do python3 "$p" > /dev/null; n=$((n+1)); done
for f in ai core data fx ui3d ui_panels duel voice; do node --check src/$f.js; done
echo "applied: $n patches"
