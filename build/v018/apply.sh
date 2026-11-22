#!/bin/bash
# v0.17 의 소스에 build/v018/p*.py 를 차례로 입혀 src/ 를 만든다(다시 돌려도 같다).  bash build/v018/apply.sh
# 명부(src/roster.js)와 초상·제목 그림(src/assets.js), 아이콘(pwa/icons)은 패치가 아니라 도구로 다시 만든 것이다 — 한 번만 하면 된다(그 전의 것은 build/roster.v017.js · build/assets.v017.js):
#   python3 tools/make_roster.py <群雄割據 삼국지 index.html> src/roster.js        # 초상을 새로 받은 60명은 tools/roster18.py 에(번호 · 능력치 · 소속은 그대로, por 만 바뀐다)
#   새 초상 60장: tools/por18_prompt.py(문구) → Higgsfield → POR=18 tools/dl_por17.py → art/raw18/ → tools/facebox.py art/raw18 art/por18_faces.tsv
#   art/raw18m = art/raw17m(그동안의 그림) + art/raw18(새 그림), art/por18_faces_all.tsv = art/por17_faces_all.tsv + art/por18_faces.tsv
#   제목 그림: python3 tools/make_title18.py   (art/title18/guanyu_full.png → art/title18/title.jpg)
#   TITLE=art/title18/title.jpg FOCUS=art/por7_focus.tsv python3 tools/make_assets_v08.py art/raw18m art/por18_faces_all.tsv art/por18_out src/assets.js build/assets.v093.js src/roster.js 256 320 72 52
#   아이콘(낙관 天下 → 天下圖): python3 tools/make_icons.py
#   효과음: python3 tools/make_audio_v018.py   (→ src/sfxdata.js. 그 결과를 build/sfxdata.v018.js 로 둔다)
set -e
cd "$(dirname "$0")/../.."
for f in ai core data fx ui3d ui_panels duel voice; do cp build/$f.v017.js src/$f.js; done
cp build/style.v017.css src/style.css; cp build/index.v017.html src/index.html
cp build/sfxdata.v018.js src/sfxdata.js      # 북 둘(drum · drums)을 새로 만든 것 — python3 tools/make_audio_v018.py (build/sfxdata.v017.js 에서 출발, ffmpeg 필요)
n=0
for p in build/v018/p*.py; do python3 "$p" > /dev/null; n=$((n+1)); done
for f in ai core data fx ui3d ui_panels duel voice; do node --check src/$f.js; done
echo "applied: $n patches"
