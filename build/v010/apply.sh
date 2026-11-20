#!/bin/bash
# v0.9.3 의 소스에 build/v010/p*.py 를 차례로 입혀 src/ 를 만든다(다시 돌려도 같다).  bash build/v010/apply.sh
set -e
cd "$(dirname "$0")/../.."
S=""; [ -d build/v093src ] && S=build/v093src      # (작업용 사본에서는 build/v093src, 본 폴더에서는 build/*.v093.*)
for f in ai core data fx ui3d ui_panels; do if [ -n "$S" ]; then cp $S/$f.js src/$f.js; else cp build/$f.v093.js src/$f.js; fi; done
if [ -n "$S" ]; then cp $S/style.css src/style.css; cp $S/index.html src/index.html; else cp build/style.v093.css src/style.css; cp build/index.v093.html src/index.html; fi
n=0
for p in build/v010/p*.py; do python3 "$p" > /dev/null; n=$((n+1)); done
for f in ai core data fx ui3d ui_panels; do node --check src/$f.js; done
echo "applied: $n patches"
