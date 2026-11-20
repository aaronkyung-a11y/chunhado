# 삼국지 천하도 (三國志 天下圖)

삼국지 11 PK식 시스템의 모바일 단일 HTML 게임. 현재 v0.9.2(화면의 글을 덜어 냄 · 건설을 고르면 지도가 어두워지고 지을 수 있는 빈 부지만 밝게 — 규칙은 0.9.1 그대로) — 변경 내역은 `CHANGELOG.md`. v0.9.1(기간을 턴 수가 아니라 날짜·날수·개월로 적는다 · 초반 보호 6·4·3개월 · 전법: 성공해도 반격은 통상 공격만큼, 무장의 차이를 더 크게, 전법 풀이에 기대값). v0.9: 군사(軍師)를 두고 등용·계략 전에 조언을 듣는다 · 이웃 거점에 있는 다른 세력의 무장을 등용한다. v0.8.1: 초반 보호 · 혼란·위보·불길 표시. v0.8: 건설 담당 묶기·성역 멈춤 없앰·돈과 병량 약 2배·전법 균형·부지 10·13·16곳·충성과 인연·지도 끝·초상 가운데 맞춤.

- **바로 하기 / 앱으로 설치**: https://aaronkyung-a11y.github.io/chunhado/ — 휴대폰 크롬에서 열고 제목 화면의 **앱으로 설치**(또는 브라우저 메뉴의 *홈 화면에 추가*)를 누르면 앱처럼 전체 화면으로 열리고, 한 번 연 뒤에는 인터넷 없이도 된다.
- 저장소에 올라 있는 것: 맨 위의 `index.html`·`manifest.webmanifest`·`sw.js`·`icons/`·`bgm/`가 게임(= `tools/build.py --pwa`의 결과), 나머지가 소스.

## 구조
- `src/` — 손으로 쓰는 소스
  - `data.js` 정적 수치, `core.js` 규칙 엔진(DOM 없음), `ai.js` AI
  - `ui3d.js` 3D 지도(three.js)·입력·효과음·음악, `fx.js` 이동·공격·전법·계략 연출(v0.4)과 그 순간의 소리(v0.7), `ui_panels.js` 패널·대화상자·조작 흐름
  - v0.5부터 `src/`의 파일은 모두 직접 고침. `build/patch_v04_ui3d.py`·`build/patch_v04_panels.py`는 v0.3 → v0.4 작업 기록(다시 돌리면 v0.5 변경이 사라지니 돌리지 않음). 판별 원본은 `build/*.v03.js`·`build/*.v04.js`·`build/*.v05.js`·`build/*.v06.*`. v0.6 → v0.7에서 고친 자리는 `build/v07/p1~p4_*.py`에, v0.7 → v0.8에서 고친 자리는 `build/v071/p1~p9_*.py`에 기록(역시 다시 돌리지 않음 — 순서대로 p1 건설 담당 묶기, p2 그 화면, p3 수송, p4 지도 끝, p5·p5b·p5c 성역 멈춤 없애기, p6 돈과 병량, p7·p7b 전법, p8·p8b 부지, p9 충성과 인연), v0.8 → v0.8.1에서 고친 자리는 `build/v081/p1~p8_*.py`에(p1·p1b·p2 초반 보호의 규칙과 AI, p3 그 화면, p4 상태 이상의 규칙 쪽 준비, p5 지도의 딱지·소용돌이, p6 창과 글, p7 손질, p8 옛 저장), v0.8.1 → v0.9에서 고친 자리는 `build/v09/p1~p7_*.py`에(p1 규칙 — 미리 정해 둔 결과·군사·다른 세력 무장 등용, p2 AI, p3 화면, p4 달 단위와 단속, p5·p6 화면 손질, p7 작은 세력은 건드리지 않기). 판별 원본에 `build/*.v07.*`·`build/*.v08.*`·`build/*.v081.*` 추가
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
- `tests/` — **`regress.sh [로그 폴더]`(전체 회귀: 세 판을 모두 빌드한 뒤 돌린다. 끝나면 `<로그 폴더>/_summary.txt`에 시험마다 종료 코드)**, v0.9.2 화면 `d18.py`(글 덜어내기: STATUS 창의 구조·한 줄씩인지·글자 수 한도·접힌 도움말 / 건설 자리: 덮개가 켜지고 꺼지는지, 밝은 칸만 뚫려 있는지 — 덮개 캔버스의 점을 읽어 본다 —, 창과 지도의 번호, 고른 칸이 창 위로 보이는지, 카드의 수입이 수입 셈과 같은지, 고른 그 칸에 지어지는지, 못 짓는 네 경우. 그림은 `tests/shots18/`)·`text92.py`(화면마다 보이는 글자 수를 잰다. `PAGE=../chunhado-v0.9.1-offline.html`처럼 옛 판을 주면 그 판을 잰다), v0.9.1 `tac91.js [턴=144] [씨앗=1]`(전법이 보통 공격보다 얼마나 이득인지 재기: AI 대전의 싸움 장면마다 전법의 기대 피해·기대 반격을 식으로 셈해, 같은 장면 위에서 규칙 묶음끼리 견준다. `SETS='{…}'`로 다른 숫자를 넣어 볼 수 있다)·`exp91.js [시행 수]`(그 식 `tacticExpect`·`attackExpect`가 실제 판정의 평균과 맞는지 — 맞붙음·뒤가 막힘·옆에 적·혼란 중·원거리, 강 위)·`peace91.js`(보호 기간과 옛 저장 옮기기)·화면 `d17.py`(날짜·날수 표기, 전법 풀이의 기대값, 0.9에서 하던 판 이어 하기 — 그림은 `tests/shots17/`), v0.9 `adv9.js`(미리 정해 둔 결과의 고름·되풀이, 군사의 적중률, 다른 세력 무장 등용의 대상·성공률·넘어옴·거절, AI가 보호 중에는 권하지 않음, 옛 저장)·`poach9.js ai|player …`(등용이 얼마나 자주 일어나는지 재기)·화면 `d16.py`(군사 임명, 조언의 ○·×, 이웃 무장 등용, 데려갈 위험 알림 — 그림은 `tests/shots16/`), v0.8.1 `rush8.js [턴=72] [씨앗 수=5]`(초반 압박 재기: 약한 일곱 세력을 플레이어 자리에 두고 첫 피격·첫 함락·멸망 턴을 셈. `PASSIVE=1`이면 그 세력은 손을 놓음, `SRC=<폴더>`로 다른 판과 견줌, `PEACE=a,b,c`·`RAMP=n`으로 보호 기간을 바꿔 가며 잼. 보호가 어겨지면 종료 코드 1)·화면 `d15.py`(초반 보호의 표시·경고·풀림, 상태 이상의 딱지·소용돌이·풀이 띠·남은 날수 — 그림은 `tests/shots15/`), `sim.js`(AI 대 AI + 불변식), `fuzz.js`(무작위 명령 — v0.8.1부터 보호 어김도 셈), 행군 규칙 `floor.js`(빈 지도 전수 탐색: 출진한 턴에 거점·시설을 칠 수 있는 길이 없는가)·`zonecheck.js`(AI 대전에서 규칙 위반 감시) — v0.7까지는 성역 멈춤 규칙을 봤고 `dist.js`는 그때의 것, v0.8 규칙 `job8.js`(건설 담당 묶기)·`loy8.js`(충성·인연·부지 채우기)·`tac7.js`(전법 — v0.8 항목 포함)·`bal8.js <턴> <씨앗>`(균형 재기: 돈·병량·병력·시설·전투 집계, `SRC=<폴더>`로 다른 판과 견줌), 화면 `d14.py`(지도 끝 — `PAGE=../chunhado-v0.7-offline.html python3 tests/d14.py old`로 예전 판의 수치를 잼), `browser.py`와 v0.4 화면 `d1.py`(둘러보기)·`d2.py`/`d2b.py`(전투 연출: 장면 찍기 / 전법·계략 전부)·`d3.py`(회귀)·`d4.py`/`d5.py`(적 턴 재생·시간)·`d6.py`(모든 창)·`d7.py`(v0.8: 성역에서 멈추지 않음·출진한 턴에는 거점을 못 침)·`d8.py <옛 판.html>`(옛 저장 호환), `d9.py`(여는 시간 비교), `b9.py`(CDN), v0.6 뒤로 가기 `d10.py`(경로마다 눌러서 확인 — `PAGE=../chunhado-v0.5-offline.html`로 예전 판과 견줌)·`d11.py <걸음> <씨앗> <세력>`(마구 눌러 보기), v0.7 `tac7.js [횟수]`(전법의 성공·대성공 확률과 효과를 되풀이해 확인)·`d12.py`(소리·음악·전법 표시·부대 목록 — `PAGE=pwa/index.html`로 돌려야 음악 파일까지 봄)·`d13.py`(앱판을 내 컴퓨터의 http 서버로 띄워 서비스 워커·오프라인을 확인)·`d11.py <걸음> <씨앗> <세력>`(마구 눌러 보기: 상태 어긋남·오류·×만으로 STATUS 창까지). 헤드리스 Chrome, 기본은 `dist/offline.html`. `c1~c7.py`는 v0.3, `b1~b6.py`는 v0.2 화면 기준이라 지금은 맞지 않음(기록용)
- `build/` — 중간 산출물과 판별 백업(`*.v03.js`, `*.v04.js`, `*.v05.js` 등). `patch_v04_*.py`는 v0.3 → v0.4 패치 기록. `patch_c.py`·`v03_home.js`·`v03_play.js`는 v0.2 → v0.3 작업 기록(다시 돌리지 않음)
- `pwa/` — 앱판에만 들어가는 것: `manifest.webmanifest`, `sw.js`(서비스 워커), `icons/`
- `bgm/` — 음악 8곡(v0.7, HTML 옆에 두면 재생 — 없으면 코드로 만든 음악). `audio7/` — 소리 원본 기록(`jobs.tsv`). `versions/` — 버전별 스냅샷.

## 소리(v0.7)
- **효과음**: `src/sfxdata.js`의 표본 27개를 처음 누를 때 풀어 두고(`sndLoad`), 장면 이름으로 부른다 — `sfx('hit')`. 장면 → 표본·크기·음높이 흔들림·늦춤은 `src/ui3d.js`의 `CUES` 표 한 곳에서 정한다. 같은 장면은 `gap`(ms) 안에 다시 나지 않는다. 표본이 아직 안 풀렸으면 예전의 만든 소리(`sfxSyn`)가 대신 난다.
  - 움직이는 동안의 소리는 `sfxMove(병과, ms)`(보병 발소리·기병 말발굽·수레), 전투 연출 도중의 소리는 `src/fx.js`의 시간표(`tracks`)에 `on: function () { sfx(...) }`로, 타격 순간의 소리는 `ui_panels.js`의 `resultFx`에서.
- **음악**: `BGM_TRACKS`가 장면(title·field·tense·battle·victory·defeat)마다 곡을 정한다. 여러 곡이면 끝날 때마다 다음 곡으로 돌아간다. 지금의 장면은 `bgmForState()` — 싸운 지 한 턴 안이거나 적이 내 성 2칸 안이면 전투, 적 부대가 내 성 7칸·내 부대 4칸 안이거나 내 부대가 남의 성역에 있으면 긴장, 아니면 평시.
  - 곡을 바꾸려면 `bgm/<이름>.mp3`를 바꿔 넣으면 된다(앱판은 `pwa/sw.js`의 `BGM` 번호도 올린다). 곡을 늘리려면 `BGM_TRACKS`에 이름을 더한다.

## 전법(v0.7 세 결과 → v0.8 양쪽을 다 보는 판정 → v0.9.1 성공해도 반격은 통상 공격만큼)
- 판정은 `src/core.js`의 `tacticOdds(u, d)` 한 곳. 성공률의 조각은 `tacticParts`가 돌려준다(화면의 "성공률 72% = 적성 80 · 무장 +4 · …"가 이것).
  - 성공률 = 적성(`TACTIC_RATE` C 55·B 63·A 71·S 80) + 무장 (내 부대 최고 무력×0.6 + 주장 통솔×0.4 − 상대 부대 최고 통솔)×0.8 [−30~+15] + 병력 log2(내 병력÷상대 병력)×8 [−16~+8] + 상대 적성(C +3·B 0·A −3·S −6) + 상대가 선 곳(숲·구릉 −5, 강 +5) + 상대 혼란 +10 + 맞는 특기 +5 → 10~95%. (무장 항은 v0.8~0.9에서 ×0.6 [−24~+12])
  - 대성공률 = 적성(C 4·B 8·A 12·S 18) + (무력−70)×0.5 [−4~+15] + (내 무력−상대 통솔)×0.15 [−6~+6], 2~45%. 대성공은 성공 안에 들어 있다. 특기(창장·극장·궁장·기장·투신·신장·기신·궁신)가 맞으면 **성공한 전법은 모두 대성공**(v0.7에서는 성공까지 보장했다).
- 피해 = 통상 공격의 식 × 전법 배수 × 병력 비 `tacticSizeK` = (내 병력÷상대 병력)^0.25, 0.75~1.1. 배수는 `TACTICS` — v0.9.1: 돌출 1.15 나선첨 1.3 이단첨 1.45 / 갈퀴 1.0 횡치 1.15 선풍 1.05 / 화시 1.05 관시 1.25 난사 1.0 / 돌격 1.25 돌파 1.1 돌진 1.5 (v0.8~0.9: 1.25 1.35 1.55 / 1.25 1.15 1.05 / 1.1 1.3 1.05 / 1.3 1.35 1.6).
- 숫자는 `data.js`의 `TACTIC_K` 한곳: 성공했을 때 받는 반격 `okCounter` 0.55(= 통상 공격의 반격. v0.8~0.9: 0.4), 실패했을 때 피해 `failDmg` 0.4(0.5)·반격 `failCounter` 0.85(0.7), 대성공 배수 `crit` 1.25(1.3)·`critGod` 1.375(기신·궁신, 1.43), 무장 항 `stat`·`statLo`·`statHi`. 원거리 전법은 노병에게만(그것도 실패했을 때만) 반격을 받는다. 갈퀴·돌파, 밀려나 떨어진 적, 이 전법으로 혼란에 빠진 적은 반격하지 못한다. 대성공이면 `TACTICS[..].great`가 효과를 덮어쓴다(`tacticEff`).
- 혼란 확률은 `confuseOdds`: 기본 확률 + (70 − 상대의 (지력+통솔)/2) × 0.6, 5~95%. `confuse`가 1이면 반드시.
- **기대값(v0.9.1)**: `attackExpect(u, d)`(통상 공격의 기대 피해·반격), `tacticExpect(u, d, tac)`(전법의 기대 피해·반격 — 성공·대성공·실패를 확률대로 섞음. 함께 맞는 적은 `tacticOthers`, 밀어낼 자리는 `pushRoom`). 주사위를 뺀 피해는 `dmgBase`(`dmgUU` = `dmgBase` × 0.92~1.08). 화면과 AI가 같은 값을 쓴다.
- AI는 (기대 피해의 차이 − 받는 반격의 차이 × 0.6) ÷ 통상 공격의 피해가 0.1을 넘을 때만 전법을 쓴다(`ai.js`). v0.8~0.9에서는 주는 피해만 보고 1.1배를 넘으면 썼다.
- 화면: 대상 창의 전법 단추에 성공률·대성공률, **전법 풀이**(`showTacticInfo`)에 양쪽의 적성·무력·통솔·병력과 성공률의 조각, 결과별 효과, 그리고 전법마다 **기대 피해 · 받는 반격**(통상 공격과 견준 %). 공격 단추의 '예상'도 `attackExpect`.

## v0.8에서 바뀐 규칙의 자리
- **건설 담당 묶기**: `core.js`의 `jobOf`·`builders`·`freeBuilders`. 시설에 `by`(담당 무장), 무장에 `job`(거점·부지 번호). `phaseStart`에서 `acted = !!jobOf(o)`.
- **행군**: 성역(`ZONE`, 성 둘레 2칸)은 이름·고리·음악의 기준으로만 남고 이동을 막지 않는다. 급습 막이는 `justOut(u)`(출진한 턴 = `u.born === G.turn`) 하나 — 그 턴에는 거점과 시설을 칠 수 없다.
- **돈과 병량**: `data.js`의 `BASE_GOLD`·`MARKET_INC`·`BASE_FOOD`·`FARM_INC`·`FAC[..].cost`와 `COST`(징병·순찰·생산·충차·포상·합병). 화면과 AI의 문턱도 이 표를 읽는다.
- **부지**: `mapdata.js`의 `plots`(성마다 S 10·M 13·L 16). 옛 저장은 `deserialize`가 모자란 부지를 뒤에 채운다.
- **충성과 인연**: `data.js`의 `BONDS`(군주 이름 → { 무장: 사이 }), `core.js`의 `bondWith`·`bondOf`·`loyNat`. 분기마다 `roundEnd`에서 자리 잡는 값 쪽으로 움직인다.
- **지도 끝**: `ui3d.js`의 `APRON`(지도 밖 띠의 폭)·`apronY`(띠의 높이)·`TERRAIN_FS`의 `edge`(거울 비춤 + 번짐 + 종이로 풀림)·`camLimits`(지도 끝이 화면에 들어오는 한도)·`settleCam`(아래 창 높이가 바뀌면 제자리로).

## v0.9.2에서 바뀐 화면의 자리
규칙(`core.js`·`ai.js`)은 0.9.1과 같다. 바뀐 기록은 `build/v092/p1~p6`(0.9.1의 소스에 차례로 입히면 0.9.2가 된다).
- **STATUS 창**: `ui_panels.js`의 `homeSheet`·`todoList`. 거점·부대·무장·천하 네 칸과 숫자 띠를 없앴다(아래 [목록] 단추와 맨 위 띠에 있다). '지금 할 일'의 줄은 제목 한 줄 + 풀이 한 줄(`.todo b`·`.todo small` — 넘치면 말줄임). 초반 보호는 이름 옆의 표(`button.pz` → `showPeaceInfo`).
- **거점 창의 탭**: 내정 · 출진(`mil`) · 인재 · 건설(`fac`). 열쇠(`data-v`)는 그대로다.
- **전법 풀이**: `showTacticInfo` — 표(`table.tcmp`: 첫 줄 `tr.nrm`이 보통 공격, `tr[data-t]`가 전법)와 접어 둔 셈법(`details.more`). **도움말**: `helpSections`가 `HELP_HTML`의 `<h3>` 토막마다 `<details>`로 접는다.
- **건설 자리 비추기**:
  - 무엇을 비출지: `ui_panels.js`의 `buildView()` — '무엇을 지을까요' 창(`MODAL.dev`, 그 위에 겹친 창이 있어도 `devOf()`가 찾는다)이 떠 있거나 거점 창이 건설 탭이면(`SHEET.fac()`) `{ b, pi(고른 부지, 없으면 -1), why(지금 못 짓는 까닭), lots[{ i, c, r, n(번호), ok }], facs, sig }`, 아니면 `null`. 창을 여닫는 곳마다 상태를 맞추지 않는다 — `ui3d.js`의 `tick`이 장면마다 `spotCheck()`로 읽어 달라졌을 때만 다시 그린다.
  - 그리기: `ui3d.js`의 `SPOT`·`spotDraw()` — 지도 위의 2D 캔버스 `#spot`을 어둡게 칠하고(`SPOT_DARK`), `ok`인 부지의 칸(`hexRing` — 화면 좌표 12점)을 뚫고, 테두리·번호·'여기'를 그린다. 땅의 덧칠(`rebuildOverlay`)도 고른 칸은 붉게. 그동안 그 성의 이름표와 작은 지도는 숨긴다(`#app.building`).
  - 화면 맞추기: `spotCam` → `frameHexes(칸들, 위, 아래, 가장 가까운 확대)` → `flyTo(지도 좌표, 확대, 화면에서의 세로 자리)`. 가려지지 않은 영역은 `safeArea()` — 지도를 보여 주는 창(`#modal.see`)이 떠 있으면 그 창의 높이를 뺀다.
  - 지도를 보여 주는 창: 창 객체에 `see: true`(바탕을 덮지 않고 창 밖의 누름은 지도가 받는다 — `onTap`이 `devTap`으로 넘긴다: 다른 빈 부지면 자리 바꾸기, 그 밖이면 닫기). 건설 창이 떠 있는 동안에는 아래 창과 단추 줄을 숨긴다(`#app.seeing`).
  - 못 짓는 까닭: `buildWhy(b)`(쉬는 무장 · 금 · 행동력). 번호: `emptyLots`·`lotNo`·`lotMark`(①②③). 카드의 효과: `lotEffect(b, pi, 시설)` — 수입은 `gainAt`이 `goldIncome`·`foodIncome`을 그 자리에 지은 것으로 돌려 뺀 값.

## v0.9.1에서 바뀐 규칙의 자리
- **기간 표기**: `ui_panels.js`의 `days(턴)`(날수)·`months(턴)`(달로 나누어떨어지면 "6개월"·"1년", 아니면 날수)·`shortDate(턴)`(올해면 해를 뺀 날짜). 화면에 기간을 "N턴"으로 적지 않는다 — '이번 턴'·'다음 턴'·'턴 종료'처럼 차례를 가리키는 말만 남긴다. 규칙 쪽 문구(`core.js`의 기록, `ai.js`의 `aiReport`, `ui3d.js`의 `statusSegs`, `data.js`의 전법·계략·특기 풀이)도 같다.
- **초반 보호 기간**: `data.js`의 `PEACE_PLAYER = [[10000, 18], [20000, 12]]`·`PEACE_ALL = 9`(턴). `G.peace.v = 2`는 이 기간 표로 셈한 판이라는 표시 — 표시가 없는 저장(0.8.1~0.9)은 `deserialize`가 한 번 당긴다(불러온 때부터 적어도 30일은 남김, 기록에 한 줄).
- **전법**: 위 "전법" 절. 숫자는 `TACTIC_K`·`TACTICS`, 기대값은 `tacticExpect`.

## v0.9에서 바뀐 규칙의 자리
- **미리 정해 둔 결과**: `core.js`의 `omenRoll(key, monthly)` — 판의 고정 씨앗(`G.seed0`)·때(턴 또는 달)·대상으로 0~100의 주사위를 만든다. 난수 흐름(`rnd`, `G.seed`)과는 따로 논다. 성공률이 p일 때 주사위 < p이면 성공.
  - 등용 `recruitRoll(t)`: 대상에만 건다. 재야·포로는 턴마다, 다른 세력의 무장(`st === 'active'`)은 달마다 한 번. 계략 `ployRoll(ploy, t)`: 종류 + 대상 부대(없으면 칸), 턴마다. `cmdRecruit`·`unitPloy0`이 `chance()` 대신 이것을 쓴다(AI도 같다).
  - '누가 하는가'에 걸지 않는 까닭: 걸면 무장마다 주사위가 따로라서, 군사에게 무장을 바꿔 가며 물어 통하는 사람만 보내면 성공률이 1 − Π(1 − p)로 뛴다.
- **군사(軍師)**: 세력에 `adv`(무장 번호, 없으면 −1). `facAdv`·`advOk`·`advCandidates`·`autoAdvisor`·`setAdvisor`. 새 판과 옛 저장에서는 지력이 가장 높은 무장(군주 제외). 자리가 비면 그 세력의 `phaseStart`에서 채운다.
  - 조언 `advise(f, roll, rollA, p, tInt)` → `{ adv, acc, says }`. 적중률 `adviceAcc` = 지력 + (지력 − 상대 지력) × `ADVISE.k`(0.5), `ADVISE.min`(50)~100. '맞는가'의 주사위(`recruitRollA`·`ployRollA`)도 대상에만 걸려 있어 군사를 바꿔 물어도 새 정보가 없다.
  - 화면: `ui_panels.js`의 `showAdvisor`(임명), `advMark`·`advLine`(○·×와 말), `recruitAdvice`·`ployAdvice`, `bestRecruiter`·`poachHints`(지금 할 일의 "등용에 응할 듯한 이웃 무장"), STATUS 창의 `.hm-adv`.
- **다른 세력 무장 등용**: `core.js`의 `poachTargets(b)`(내 거점과 길로 바로 이어진 이웃 거점에 머무는 무장, 군주·출진·이동 중 제외)·`canPoach`·`recruitChance`의 `t.st === 'active'` 갈래. 수치는 `data.js`의 `POACH`(base 15 · 매력 0.5 · 정치 0.2 · 군주 매력 차 0.25 · 충성 −2.5/점 · 논객 +20 · 내 군주와의 인연 +30 · 최고 85% · 충성 95 이상과 제 주군과 인연이 있는 무장은 0 · 거절 +3 · 떠나면 남은 무장 +2).
  - 한 무장에게는 한 달에 한 번(`t.ask` = 다시 권할 수 있는 턴, `askWait`). 응하면 그 자리에서 `t.loc`·`t.f`가 바뀌고 맡던 공사(`job`)와 군사 자리를 내려놓는다.
  - AI: `ai.js`의 `aiPoach`(`POACH_AI` — 턴마다 25%의 확률로 한 번, 성공률 12% 이상인 대상에게). 플레이어가 초반 보호를 받는 동안에는 플레이어의 무장에게 권하지 않고, 무장이 4명 이하(`spare`)인 세력의 무장에게도 권하지 않는다.
  - 위험 알림: `poachRisk(o)`(이웃 거점에서 가장 잘 권하는 사람과 그 성공률) → `todoList`의 "다른 세력이 데려갈 수 있는 무장".

## v0.8.1에서 바뀐 규칙의 자리
- **초반 보호**: `data.js`의 `PEACE_ALL`(12턴 — AI끼리도 서로의 거점을 먼저 치지 않는 기간)·`PEACE_PLAYER`(시작 병력 → 플레이어의 보호 턴 수: 1만 미만 36, 2만 미만 24, 그 밖 `PEACE_ALL`)·`PEACE_RAMP`(보호가 끝난 뒤의 완충 24턴).
  - 판에 `G.peace = { until, broken }` — `until` 턴부터 AI가 플레이어의 거점·시설을 칠 수 있다. `broken[f]`는 플레이어가 세력 f의 거점·시설을 먼저 쳤다는 표시(그 세력은 바로 칠 수 있고 완충도 없다). 0.8까지의 저장은 `deserialize`가 시작 병력으로 `until`을 정해 붙인다.
  - 판정은 `core.js`의 `aiMayStrike(f, owner)` 한 곳. AI는 `ai.js`의 `aiOffense`(출진 목표에서 뺌)·`aiUnitAct`(거점 공격·길을 막는 시설 공격·시설 위의 화계)에서 이것을 묻는다. 치러 가던 거점의 주인이 '아직 칠 수 없는 세력'으로 바뀌면 돌아간다.
  - 지켜지는 것은 거점과 시설뿐이다 — 들판의 부대끼리는 싸우고, 주인 없는 성은 누구나 차지한다.
  - '먼저 쳤다'는 `actEv`에서 행동 **전**의 주인(`actHoldF`)으로 잰다: 거점·시설 공격, 남의 시설이 있는 칸에 놓는 화계.
  - 완충: `aiNeedMul`(출진에 필요한 병력 우위 2.0 → 1.25배, `PEACE_RAMP` 턴에 걸쳐. '국력이 압도적이면 파상 공세'의 문턱 4배도 같은 비율로 올린다)·`peaceRamp`·`othersOnPlayer`(다른 AI 세력이 이미 플레이어를 치러 가고 있으면 기다린다). v0.8까지 플레이어의 성에 주던 가산점 +3은 없앴다.
  - 화면: `ui_panels.js`의 `peaceNote`·`showPeaceInfo`(풀이), `todoList`의 맨 윗줄, STATUS 창 날짜 옆의 `.pz`, 대상 줄 아래의 경고(`peaceWouldBreak`), 군주 고르기의 `startTroops`·`peaceFor`. 3턴 남았을 때와 끝났을 때는 `phaseStart`가 기록과 `news` 사건을 낸다.
- **상태 이상 표시**(규칙은 그대로): `core.js`의 `statusLeft(u)`(지금부터 잃는 차례 수 — 건너뛰고 있는 턴은 `u.stSkip`에 적어 둔다)·`statusName`·`unitOnFire`. 계략·전법 결과에 `res.st`·`res.stN`(걸린 상태와 턴 수), 반계로 되돌아오면 `res.selfSt`·`res.selfStN`.
  - 지도: `ui3d.js`의 `statusSegs`·`drawChips`(머리 위 딱지: 혼란 쪽빛·위보 황토·불길 인주, 숫자는 남은 턴), 부대마다 `o.st`(딱지)·`o.sw`(소용돌이 — `fx.js`의 `fxTex('swirl')`), `ST_TINT`(바랜 빛). `tick`에서 소용돌이를 돌리고 혼란이면 그림을 좌우로 기울인다(불과 같은 박자로 초당 20번만 다시 그림).
  - 창: `ui_panels.js`의 `stChips`(딱지)·`statusBanner`(풀이 띠)·`statusLeftText`, `todoList`의 내 부대 줄, `resultMsg`·`resultFx`의 "혼란 2턴".

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
