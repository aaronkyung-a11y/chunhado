#!/bin/bash
# v0.9.2 의 소스(build/*.v092.*)에 build/v093/p*.py 를 차례로 입혀 src/ 를 만든다(다시 돌려도 같다).  bash build/v093/apply.sh
set -e
cd "$(dirname "$0")/../.."
for f in ai core data fx ui3d ui_panels; do cp build/$f.v092.js src/$f.js; done
cp build/style.v092.css src/style.css; cp build/index.v092.html src/index.html
n=0
for p in build/v093/p*.py; do python3 "$p" > /dev/null; n=$((n+1)); done
for f in ai core data fx ui3d ui_panels; do node --check src/$f.js; done
echo "applied: $n patches"
