# 삼국지 천하도 (三國志 天下圖)

삼국지 11 PK식 시스템의 모바일 단일 HTML 게임. 현재 v0.8(건설 담당 묶기·성역 멈춤 없앰·돈과 병량 약 2배·전법 균형·부지 10·13·16곳·충성과 인연·지도 끝·초상 가운데 맞춤) — 변경 내역은 `CHANGELOG.md`.

- **바로 하기 / 앱으로 설치**: https://aaronkyung-a11y.github.io/chunhado/ — 휴대폰 크롬에서 열고 제목 화면의 **앱으로 설치**(또는 브라우저 메뉴의 *홈 화면에 추가*)를 누르면 앱처럼 전체 화면으로 열리고, 한 번 연 뒤에는 인터넷 없이도 된다.
- 저장소에 올라 있는 것: 맨 위의 `index.html`·`manifest.webmanifest`·`sw.js`·`icons/`·`bgm/`가 게임(= `tools/build.py --pwa`의 결과), 나머지가 소스.

## 구조
- `src/` — 손으로 쓰는 소스
  - `data.js` 정적 수치, `core.js` 규칙 엔진(DOM 없음), `ai.js` AI
  - `ui3d.js` 3D 지도(three.js)·입력·효과음·음악, `fx.js` 이동·공격·전법·계략 연출(v0.4)과 그 순간의 소리(v0.7), `ui_panels.js` 패널·대화상자·조작 흐름
  - v0.5부터 `src/`의 파일은 모두 직접 고침. `build/patch_v04_ui3d.py`·`build/patch_v04_panels.py`는 v0.3 → v0.4 작업 기록(다시 돌리면 v0.5 변경이 사라지니 돌리지 않음). 판별 원본은 `build/*.v03.js`·`build/*.v04.js`·`build/*.v05.js`·`build/*.v06.*`. v0.6 → v0.7에서 고친 자리는 `build/v07/p1~p4_*.py`에, v0.7 → v0.8에서 고친 자리는 `build/v071/p1~p9_*.py`에 기록(역시 다시 돌리지 않음 — 순서대로 p1 건설 담당 묶기, p2 그 화면, p3 수송, p4 지도 끝, p5·p5b·p5c 성역 멈춤 없애기, p6 돈과 병량, p7·p7b 전법, p8·p8b 부지, p9 충성과 인연). 판별 원본에 `build/*.v07.*` 추가
  - `style.css`, `index.html`(틀)
  - 생성물: `mapdata.js`(지형·거점·도로), `map3d.js`(높이맵·도로 선·미니맵), `sprites.js`(지도 그림), `assets.js`(초상 `PORTRAITS` = 얼굴 중심 정사각 흉상, `SCENES` = 3:4 장면, 타이틀, 한지 무늬), `roster.js`(세력·무장), `sfxdata.js`(효과음 27개 — mp3를 base64로, v0.7)
- `tools/` — 생성 스크립트
  - `geo.py` 거점의 실제 위·경도와 도법
  - `mapgen2.py <geo_dir> <mapdata.js> <mapdata.json> <debug.png>` 실제 지형 → 헥스 지도
  - `bake3d.py <geo_dir> <mapdata.json> <terrain.jpg> <map3d.js> [텍스처 폭]` 높이맵·바탕 텍스처
  - `make_sprites.py <raw_dir> <out_dir> <sprites.js>` 흰 배경 제거·테두리
  - `make_roster.py <群雄割據 삼국지 index.html> <src/roster.js>` 세력·무장 명부(초상 키는 `art/manifest.tsv`와 `art/por2_jobs.tsv`)
  - `make_portraits.py <원본 폴더[,폴더…]> <옛 초상 폴더> <out_dir> <src/assets.js> <title.png> <src/roster.js> [크기=288] [품질=70]` 흰 배경 제거 → WebP, 명부에 쓰인 초상만 묶음
  - `dl_por2.py` 초상 원본 내려받기(작업 ID ↔ 키)
  - v0.4 수묵: `bake3d_ink.py <geo_dir> <mapdata.json> <terrain.jpg> <map3d.js> [텍스처 폭]`(바탕 텍스처만 수묵으로, 높이맵은 `bake3d.py`와 같음), `make_assets_ink.py <원본 폴더> <out_dir> <src/assets.js> <title.png> <src/roster.js> [크기=288] [품질=74]`(흰 바탕 그대로 — 화면에서 곱하기로 얹음), `make_sprites_ink.py <raw_dir> <out_dir> <sprites.js>`(가장자리와 이어진 흰 바탕만 투명하게), `dl_por3.py`(초상 원본 내려받기)
  - `build.py` → `dist/index.html`(three.js를 CDN에서 불러오는 게시판), `build.py --embed` → `dist/offline.html`(three.js까지 넣은 완전 단일 파일: 오프라인·시험용), `build.py --pwa` → `dist/pwa/`(앱판: three.js 포함 `index.html` + `manifest.webmanifest`·`sw.js`·`icons/`·`bgm/` — GitHub Pages에 올리는 것), `dist/code.js`(문법 검사용)
  - v0.5 초상: `por5_prompt.py plan|text <key>`(묶음 계획·프롬프트 전문), `dl_por5.py`(내려받기), `facebox.py <raw_dir> <faces.tsv>`(YuNet 얼굴 검출 — 모델 파일 `face_detection_yunet_2023mar.onnx`는 opencv_zoo에서 받음), `make_assets_v05.py <raw5_dir> <faces.tsv> <out_dir> <src/assets.js> <앞 판 assets.js> <src/roster.js> [흉상=288] [장면 폭=360] [품질 흉상] [품질 장면]`, `qa_por5.py`(확인용 시트). 절차는 `art/por5_progress.md`
  - v0.7 초상: `por7_prompt.py batch|text <key>`(v0.5 그림을 본으로 더 세게 다시 그리는 문구), `por7_plan.py`(순서·묶음), `dl_por7.py`(내려받기), `qa_por7.py <out.jpg> <key…>`(얼굴 상자 확인), `make_assets_v05.py`는 환경 변수 `FOCUS=<손으로 정한 얼굴 자리.tsv>`를 받음
  - v0.7 소리: `dl_audio7.py`(내려받기), `make_audio_v07.py [music] [sfx]`(`audio7/raw/` → `bgm/*.mp3`, `src/sfxdata.js`)
  - v0.7 앱: `make_icons.py [미리 보기.jpg]`(관우 초상 + 낙관 → `pwa/icons/`)
  - v0.8: `add_plots.py <mapdata.js> [mapdata.json…]`(성마다 부지를 10·13·16곳으로 — 있던 부지는 순서까지 그대로 두고 뒤에 덧붙임. 두 번 돌려도 같음), `make_assets_v08.py`(초상을 가운데로 다시 자름 — 인자는 `make_assets_v05.py`와 같고, `<out_dir>/crops.tsv`에 인물마다 자른 틀과 전후 수치를 남김. `KEEP=키,키`로 장면을 그대로 둘 인물을 정함)
- `tests/` — `sim.js`(AI 대 AI + 불변식), `fuzz.js`(무작위 명령), 행군 규칙 `floor.js`(빈 지도 전수 탐색: 출진한 턴에 거점·시설을 칠 수 있는 길이 없는가)·`zonecheck.js`(AI 대전에서 규칙 위반 감시) — v0.7까지는 성역 멈춤 규칙을 봤고 `dist.js`는 그때의 것, v0.8 규칙 `job8.js`(건설 담당 묶기)·`loy8.js`(충성·인연·부지 채우기)·`tac7.js`(전법 — v0.8 항목 포함)·`bal8.js <턴> <씨앗>`(균형 재기: 돈·병량·병력·시설·전투 집계, `SRC=<폴더>`로 다른 판과 견줌), 화면 `d14.py`(지도 끝 — `PAGE=../chunhado-v0.7-offline.html python3 tests/d14.py old`로 예전 판의 수치를 잼), `browser.py`와 v0.4 화면 `d1.py`(둘러보기)·`d2.py`/`d2b.py`(전투 연출: 장면 찍기 / 전법·계략 전부)·`d3.py`(회귀)·`d4.py`/`d5.py`(적 턴 재생·시간)·`d6.py`(모든 창)·`d7.py`(v0.8: 성역에서 멈추지 않음·출진한 턴에는 거점을 못 침)·`d8.py <옛 판.html>`(옛 저장 호환), `d9.py`(여는 시간 비교), `b9.py`(CDN), v0.6 뒤로 가기 `d10.py`(경로마다 눌러서 확인 — `PAGE=../chunhado-v0.5-offline.html`로 예전 판과 견줌)·`d11.py <걸음> <씨앗> <세력>`(마구 눌러 보기), v0.7 `tac7.js [횟수]`(전법의 성공·대성공 확률과 효과를 되풀이해 확인)·`d12.py`(소리·음악·전법 표시·부대 목록 — `PAGE=pwa/index.html`로 돌려야 음악 파일까지 봄)·`d13.py`(앱판을 내 컴퓨터의 http 서버로 띄워 서비스 워커·오프라인을 확인)·`d11.py <걸음> <씨앗> <세력>`(마구 눌러 보기: 상태 어긋남·오류·×만으로 STATUS 창까지). 헤드리스 Chrome, 기본은 `dist/offline.html`. `c1~c7.py`는 v0.3, `b1~b6.py`는 v0.2 화면 기준이라 지금은 맞지 않음(기록용)
- `build/` — 중간 산출물과 판별 백업(`*.v03.js`, `*.v04.js`, `*.v05.js` 등). `patch_v04_*.py`는 v0.3 → v0.4 패치 기록. `patch_c.py`·`v03_home.js`·`v03_play.js`는 v0.2 → v0.3 작업 기록(다시 돌리지 않음)
- `pwa/` — 앱판에만 들어가는 것: `manifest.webmanifest`, `sw.js`(서비스 워커), `icons/`
- `bgm/` — 음악 8곡(v0.7, HTML 옆에 두면 재생 — 없으면 코드로 만든 음악). `audio7/` — 소리 원본 기록(`jobs.tsv`). `versions/` — 버전별 스냅샷.

## 소리(v0.7)
- **효과음**: `src/sfxdata.js`의 표본 27개를 처음 누를 때 풀어 두고(`sndLoad`), 장면 이름으로 부른다 — `sfx('hit')`. 장면 → 표본·크기·음높이 흔들림·늦춤은 `src/ui3d.js`의 `CUES` 표 한 곳에서 정한다. 같은 장면은 `gap`(ms) 안에 다시 나지 않는다. 표본이 아직 안 풀렸으면 예전의 만든 소리(`sfxSyn`)가 대신 난다.
  - 움직이는 동안의 소리는 `sfxMove(병과, ms)`(보병 발소리·기병 말발굽·수레), 전투 연출 도중의 소리는 `src/fx.js`의 시간표(`tracks`)에 `on: function () { sfx(...) }`로, 타격 순간의 소리는 `ui_panels.js`의 `resultFx`에서.
- **음악**: `BGM_TRACKS`가 장면(title·field·tense·battle·victory·defeat)마다 곡을 정한다. 여러 곡이면 끝날 때마다 다음 곡으로 돌아간다. 지금의 장면은 `bgmForState()` — 싸운 지 한 턴 안이거나 적이 내 성 2칸 안이면 전투, 적 부대가 내 성 7칸·내 부대 4칸 안이거나 내 부대가 남의 성역에 있으면 긴장, 아니면 평시.
  - 곡을 바꾸려면 `bgm/<이름>.mp3`를 바꿔 넣으면 된다(앱판은 `pwa/sw.js`의 `BGM` 번호도 올린다). 곡을 늘리려면 `BGM_TRACKS`에 이름을 더한다.

## 전법(v0.7 세 결과 → v0.8 양쪽을 다 보는 판정)
- 판정은 `src/core.js`의 `tacticOdds(u, d)` 한 곳. 성공률의 조각은 `tacticParts`가 돌려준다(화면의 "성공률 72% = 적성 80 · 무장 +4 · …"가 이것).
  - 성공률 = 적성(`TACTIC_RATE` C 55·B 63·A 71·S 80) + 무장 (내 부대 최고 무력×0.6 + 주장 통솔×0.4 − 상대 부대 최고 통솔)×0.6 [−24~+12] + 병력 log2(내 병력÷상대 병력)×8 [−16~+8] + 상대 적성(C +3·B 0·A −3·S −6) + 상대가 선 곳(숲·구릉 −5, 강 +5) + 상대 혼란 +10 + 맞는 특기 +5 → 10~95%.
  - 대성공률 = 적성(C 4·B 8·A 12·S 18) + (무력−70)×0.5 [−4~+15] + (내 무력−상대 통솔)×0.15 [−6~+6], 2~45%. 대성공은 성공 안에 들어 있다. 특기(창장·극장·궁장·기장·투신·신장·기신·궁신)가 맞으면 **성공한 전법은 모두 대성공**(v0.7에서는 성공까지 보장했다).
- 피해 = 통상 공격의 식 × 전법 배수 × 병력 비 `tacticSizeK` = (내 병력÷상대 병력)^0.25, 0.75~1.1. 배수는 `TACTICS`(v0.8에서 7~14%, 평균 9.7% 내림: 돌출 1.25 나선첨 1.35 이단첨 1.55 / 갈퀴 1.25 횡치 1.15 선풍 1.05 / 화시 1.1 관시 1.3 난사 1.05 / 돌격 1.3 돌파 1.35 돌진 1.6).
- 반격은 `TACTIC_K`: 성공했을 때 0.4(통상 공격의 반격 0.55의 73%), 실패했을 때 피해 0.5·반격 0.7. 원거리 전법은 노병에게만 반격을 받는다. 대성공: 피해 1.3배(기신·궁신 1.43배) + `TACTICS[..].great`가 효과를 덮어씀(`tacticEff`).
- 혼란 확률은 `confuseOdds`: 기본 확률 + (70 − 상대의 (지력+통솔)/2) × 0.6, 5~95%. `confuse`가 1이면 반드시.
- AI는 기대 피해(성공률 × 배수 × 병력 비 × 대성공 몫 + 실패 때의 피해)가 통상 공격의 1.1배를 넘을 때만 전법을 쓴다(`ai.js`).
- 화면: 대상 창의 전법 단추에 성공률·대성공률, **전법 풀이**(`showTacticInfo`)에 양쪽의 적성·무력·통솔·병력과 성공률의 조각, 결과별 효과.

## v0.8에서 바뀐 규칙의 자리
- **건설 담당 묶기**: `core.js`의 `jobOf`·`builders`·`freeBuilders`. 시설에 `by`(담당 무장), 무장에 `job`(거점·부지 번호). `phaseStart`에서 `acted = !!jobOf(o)`.
- **행군**: 성역(`ZONE`, 성 둘레 2칸)은 이름·고리·음악의 기준으로만 남고 이동을 막지 않는다. 급습 막이는 `justOut(u)`(출진한 턴 = `u.born === G.turn`) 하나 — 그 턴에는 거점과 시설을 칠 수 없다.
- **돈과 병량**: `data.js`의 `BASE_GOLD`·`MARKET_INC`·`BASE_FOOD`·`FARM_INC`·`FAC[..].cost`와 `COST`(징병·순찰·생산·충차·포상·합병). 화면과 AI의 문턱도 이 표를 읽는다.
- **부지**: `mapdata.js`의 `plots`(성마다 S 10·M 13·L 16). 옛 저장은 `deserialize`가 모자란 부지를 뒤에 채운다.
- **충성과 인연**: `data.js`의 `BONDS`(군주 이름 → { 무장: 사이 }), `core.js`의 `bondWith`·`bondOf`·`loyNat`. 분기마다 `roundEnd`에서 자리 잡는 값 쪽으로 움직인다.
- **지도 끝**: `ui3d.js`의 `APRON`(지도 밖 띠의 폭)·`apronY`(띠의 높이)·`TERRAIN_FS`의 `edge`(거울 비춤 + 번짐 + 종이로 풀림)·`camLimits`(지도 끝이 화면에 들어오는 한도)·`settleCam`(아래 창 높이가 바뀌면 제자리로).

## 앱(PWA)과 GitHub Pages(v0.7)
- `python3 tools/build.py --pwa` → `dist/pwa/`를 저장소 맨 위에 그대로 올린다(GitHub Pages: main 브랜치 / 루트).
- `pwa/sw.js`: 화면은 저장해 둔 것을 열되, 인터넷이 되면 먼저 서버의 것이 바뀌었는지만 짧게 묻고(HEAD) 바뀌었으면 새로 받는다 — 새 판을 올리면 다음에 열 때 바로 바뀐다. 음악은 화면이 뜬 뒤 차례로 받아 둔다. 아이콘을 바꾸면 `SHELL`, 음악을 바꾸면 `BGM`의 번호를 올린다.
- 서비스 워커 등록, '앱으로 설치' 단추, 휴대폰 '뒤로' 처리는 앱판에만 들어간다(`tools/build.py`의 `PWA_HEAD`·`PWA_JS`). 아티팩트판에는 없다.
  - '뒤로'는 앱으로 열렸을 때(`display-mode: standalone/fullscreen`)만 받는다: `appBack()`(`src/ui_panels.js`)이 ×와 같은 규칙으로 한 단계 물러나고, 더 물러날 곳이 없으면 "한 번 더 누르면 나갑니다".
- 같은 계정의 다른 GitHub Pages 앱과 **저장 공간을 같이 쓴다**(주소의 앞부분 `aaronkyung-a11y.github.io`가 같아서). 그래서 캐시 이름은 `chunhado-`로, 저장 키는 `chunhado_`로 시작하고, 이 서비스 워커는 `chunhado-`로 시작하는 캐시만 정리한다. 다른 앱의 서비스 워커가 남의 캐시까지 지우면 이 게임은 다음에 열 때 다시 받는다(그때는 인터넷이 필요).
- 올리는 법: `python3 tools/build.py --pwa && python3 tools/deploy_repo.py <저장소 폴더>` → 저장소 폴더에서 커밋·푸시. `deploy_repo.py`는 내려받은 주소가 적힌 로컬 기록을 빼고, 주소·열쇠 같은 글자가 섞인 파일이 있으면 멈춘다. 저장소에는 그림·소리 원본과 옛 판 스냅샷을 올리지 않는다.

## 창과 뒤로 가기(v0.6)
`src/ui_panels.js`의 규칙. 새 창·새 흐름을 넣을 때 이대로 맞춘다.
- 화면은 **아래 창**(`SHEET`: STATUS·거점·부대)과 **창**(`MODAL`, 겹쳐 쌓임 `MSTACK`) 두 층.
- `showDialog(d)` 새로 열기(쌓인 것은 버림) / `showDialog(d, true)` 지금 창 **위에 겹쳐** 열기 / `backDialog()` **한 단계 뒤로**(쌓인 것이 없으면 닫힘) / `closeDialog()` 모두 닫기(명령을 마쳤을 때).
  - ×(`data-a="close"`)·바깥 누르기·Esc는 모두 `backDialog()`. `lock: true`인 창(끝난 판)은 닫히지 않음.
  - 겹쳐 여는 것: 무장 정보(`showOfficer`), 도움말, 두 단계 명령의 무장 표(`pickOfficers({push: true})` — 생산·등용·건설·흡수합병), 이동의 목적지 창(`pickOfficers({keep: true})` 뒤에 `showDialog(d, true)`).
  - 무장 표는 명령이 안 되면(콜백이 `false`를 돌려줌 — `return done(...)`) 닫히지 않음.
- 창에서 지도로 건너뛸 때는 `jumpFromDialog(이름, fn)`: 그 창을 `UI.ret`에 남기고 왼쪽 위 `#ret` 단추(‹ 목록)를 띄움. 건너뛰면서 열린 아래 창에는 `UI.via`가 켜져 ×로도 그 창에 돌아감. 목록·기록·요약을 새로 열거나 턴을 넘기면 `clearRet()`.
- 아래 창의 ×는 `backSheet()`: ① 대상·행군 제안·목적지 고르기 중이면 그것만 물림 → ② `UI.sret`(거점 보기에서 보던 부대, 출진·수송 직후에는 나온 성의 군사 탭) → ③ `UI.via`면 `UI.ret`의 창 → ④ STATUS 창. `selectBase`·`selectUnit`·`clearSel`은 `UI.via`·`UI.sret`을 지움.
- 창이 그려진 뒤 0.2초 동안의 누름은 버림(`MPAINT` — 연달아 두 번 누름 방지). 움직이는 장면이 나오는 동안(`UI.busy`)에는 아래 창의 단추를 받지 않음.

## 빌드
```
python3 tools/mapgen2.py <geo_dir> build/mapdata.js build/mapdata.json build/map_debug.png
python3 tools/bake3d.py <geo_dir> build/mapdata.json build/terrain.jpg build/map3d.js 3072
cp build/mapdata.js build/map3d.js src/
python3 tools/make_sprites.py art/spr_raw art/spr src/sprites.js
python3 tools/make_roster.py <threekingdoms/index.html> src/roster.js
python3 tools/make_portraits.py art/raw,art/raw2 <threekingdoms/portraits> art/portraits src/assets.js art/title_raw.png src/roster.js 288 70
# v0.4(수묵)
python3 tools/bake3d_ink.py <geo_dir> build/mapdata.json build/terrain.jpg src/map3d.js 3072
python3 tools/make_sprites_ink.py art/spr_raw3 art/spr3 src/sprites.js
python3 tools/make_assets_ink.py art/raw3 art/portraits3 src/assets.js art/title_raw3.png src/roster.js 288 74
# v0.5(초상): 얼굴 상자 → 흉상·장면 → assets.js
python3 tools/facebox.py art/raw5 art/por5_faces.tsv
python3 tools/make_assets_v05.py art/raw5 art/por5_faces.tsv art/por5_out src/assets.js build/assets.v04.js src/roster.js 256 320 72 56
# v0.7(초상 보강·소리·아이콘)
python3 tools/facebox.py art/raw7 art/por7_faces.tsv
FOCUS=art/por7_focus.tsv python3 tools/make_assets_v05.py art/raw7 art/por7_faces.tsv art/por7_out src/assets.js build/assets.v04.js src/roster.js 256 320 72 56
python3 tools/make_audio_v07.py          # audio7/raw → bgm/*.mp3, src/sfxdata.js
python3 tools/make_icons.py              # pwa/icons/
# v0.8(부지·초상 다시 자르기)
python3 tools/add_plots.py src/mapdata.js src/mapdata.json build/mapdata.json && cp src/mapdata.js build/mapdata.js
FOCUS=art/por7_focus.tsv python3 tools/make_assets_v08.py art/raw7 art/por7_faces.tsv art/por8_out src/assets.js build/assets.v07.js src/roster.js 256 320 72 52
python3 tools/build.py && python3 tools/build.py --embed && python3 tools/build.py --pwa && node --check dist/code.js
node tests/sim.js 540 101 && node tests/fuzz.js 200 201 0 && node tests/floor.js && node tests/zonecheck.js 360 1 && node tests/tac7.js 4000
python3 tests/d10.py && python3 tests/d11.py 400 1 4      # v0.6 뒤로 가기
PAGE=pwa/index.html python3 tests/d12.py && python3 tests/d13.py   # v0.7 소리·전법·부대 목록 / 앱판
node tests/job8.js && node tests/loy8.js && node tests/bal8.js 216 1 && python3 tests/d7.py && python3 tests/d14.py   # v0.8
```
`<geo_dir>`에 필요한 파일: `elev_bump_4k.jpg`, `land10.geojson`, `lakes10.geojson`, `rivers10.geojson`.

## 자료 출처
- 고도: `turban/webgl-earth` 저장소의 `images/elev_bump_4k.jpg`(전지구 고도 이미지 4096×2048). 지형 분류와 높이맵을 뽑는 데만 쓰고 이미지 자체는 넣지 않음.
- 해안·호수·강: Natural Earth 1:10m(`nvkelso/natural-earth-vector`의 geojson, 퍼블릭 도메인).
- 거점 좌표: `tools/geo.py` — 현대 지명·유적 기준 근사값(기억에 의존, 약 0.1°).
- three.js r149(MIT) — `vendor/package/build/three.min.js`.
- 지도 그림 19장: Higgsfield(Nano Banana Pro, 1:1, 1k, 흰 배경). 작업 ID는 `art/spr_jobs.tsv`. v0.4에서 같은 19장을 수묵으로 다시 그림(`art/spr3_jobs.tsv`, v0.3 그림을 본으로 넣음).
- 초상·타이틀: v0.1에서 만든 73장 가운데 명부에 쓰이는 72장(`art/manifest.tsv`) + v0.3의 79장(`art/por2_jobs.tsv`, Higgsfield Nano Banana Pro, 1:1, 1k, 흰 배경, 조조·유비 초상을 화풍 참고로 넣음) + 群雄割據 삼국지 저장소의 `portraits/` 가운데 명부에 쓰이는 16장.
- v0.4 초상 167장·타이틀: Higgsfield(Nano Banana Pro, 1:1 1k / 타이틀 9:16 2k, 순백 바탕). v0.3 초상을 인물 본으로, 화풍 견본 한 장을 화풍 본으로 넣음. 작업 ID는 `art/por3_ids.tsv`, 프롬프트는 `dev/sources-v0.4.txt`의 `art/prompts-v0.4.txt`.
- v0.5 초상 167장: Higgsfield(Nano Banana Pro, 3:4, 1k). v0.4 수묵 초상 한 장을 인물·화풍 본으로 넣고 인물마다 장면을 지시. 작업 ID는 `art/por5_ids.tsv`, 장면은 `art/por5_scenes*.tsv`, 문구와 다시 그린 내역은 `art/prompts-v0.5.txt`.
- 얼굴 검출 모델: OpenCV Zoo의 YuNet(`face_detection_yunet_2023mar.onnx`) — 빌드할 때만 쓰고 게임에는 들어가지 않음.
- v0.7 초상 167장: Higgsfield(GPT Image, `gpt_image_2_6`, 3:4, 1k, quality high). 인물마다 v0.5 그림을 본으로 넣고 더 강한 연출로 다시 그림. 작업 ID는 `art/por7_ids.tsv`, 문구는 `art/prompts-v0.7.txt`.
- v0.7 음악 8곡: Higgsfield(ElevenLabs Music, `elevenlabs_music_v2_5`, 연주곡). 효과음: Higgsfield(`mirelo_text_to_audio`) 31개 가운데 25개를 잘라 표본 27개로. 작업 ID는 `audio7/jobs.tsv`, 문구는 `art/prompts-v0.7.txt`.
- v0.6까지 음악 자리에 넣을 수 있던 파일(群雄割據 삼국지 저장소의 `bgm/`, Suno)은 이제 쓰지 않음.
