# 삼국지 천하도 (三國志 天下圖)

삼국지 11 PK식 시스템의 모바일 단일 HTML 게임. **현재 v0.20**(붓으로 두른 틀 · 홍농(弘農) · 물빛과 높낮이가 보이는 지도 · 성의 내구 막대 · 출진의 두 단계와 지도에서 고르는 나갈 자리 · 싸움터의 조언은 부장이 · 화살과 불의 그림 · 일기토의 합별 기록 — `build/v020/`, `tools/add_base20.py`, `tools/terrain20.py`). v0.19.1(오프닝 영상이 서서히 걷힌다 — `build/v0191/`). v0.19(무장 창의 열전 425편 `src/bios.js` · 제목/오프닝/끝의 영상 `src/cine.js` + `video/` · 한쪽으로 몰린 초상 24장을 다시 자름 — `build/v019/`, CHANGELOG). v0.18.1(수송을 마친 무장이 머물지 · 돌아올지 고르기 · '지금 할 일'의 × 표시를 말로 — `build/v0181/`, CHANGELOG). v0.18(무장 카드 · 확률을 말로 · 전법의 한자 이름과 견인 · 관우 전신의 제목 화면 · 초상 60장 · 행군 단추 없이 누르면 행군 · 공격 명령 · 충차 · 군단의 출격 금지 — 아래 "v0.18에서 바뀐 것의 자리"). 그 앞의 판은 CHANGELOG.md 에. 아래는 v0.12.1 때의 머리말: v0.12.1(Claude 앱 안에서 세이브 파일 내보내기). v0.12(쏘는 소리를 새로 만듦 · 전법 실패의 피해 85% · 시설 칸을 지나가고 설 수 있음 · 세이브 파일 보내기와 가져오기 · 나갈 자리 고르기 · 아래에 더 있다는 표시). v0.11(시설의 레벨 표시 · 무장 줄의 적성 · 치안 풀이 · 출진 군량 90~360일분 · 공유 · 등용과 옛 관계 · 수송대의 보급 · 군사의 헌책과 탐색 조언 · 확대한 지도). v0.10.1(고른 시설의 표시 · 군사의 적중률 = 지력 · 공사장 그림 · 세이브 칸). v0.10(군단에 맡기기). v0.9.3(부지 번호 · 대화창). v0.9.2(화면의 글을 덜어 냄 · 건설을 고르면 지도가 어두워지고 지을 수 있는 빈 부지만 밝게 — 규칙은 0.9.1 그대로) — 변경 내역은 `CHANGELOG.md`. v0.9.1(기간을 턴 수가 아니라 날짜·날수·개월로 적는다 · 초반 보호 6·4·3개월 · 전법: 성공해도 반격은 통상 공격만큼, 무장의 차이를 더 크게, 전법 풀이에 기대값). v0.9: 군사(軍師)를 두고 등용·계략 전에 조언을 듣는다 · 이웃 거점에 있는 다른 세력의 무장을 등용한다. v0.8.1: 초반 보호 · 혼란·위보·불길 표시. v0.8: 건설 담당 묶기·성역 멈춤 없앰·돈과 병량 약 2배·전법 균형·부지 10·13·16곳·충성과 인연·지도 끝·초상 가운데 맞춤.

- **바로 하기 / 앱으로 설치**: https://aaronkyung-a11y.github.io/chunhado/ — 휴대폰 크롬에서 열고 제목 화면의 **앱으로 설치**(또는 브라우저 메뉴의 *홈 화면에 추가*)를 누르면 앱처럼 전체 화면으로 열리고, 한 번 연 뒤에는 인터넷 없이도 된다.
- 저장소에 올라 있는 것: 맨 위의 `index.html`·`manifest.webmanifest`·`sw.js`·`icons/`·`bgm/`가 게임(= `tools/build.py --pwa`의 결과), 나머지가 소스.

## 구조
- `src/` — 손으로 쓰는 소스
  - `data.js` 정적 수치, `core.js` 규칙 엔진(DOM 없음), `ai.js` AI
  - `ui3d.js` 3D 지도(three.js)·입력·효과음·음악, `fx.js` 이동·공격·전법·계략 연출(v0.4)과 그 순간의 소리(v0.7), `ui_panels.js` 패널·대화상자·조작 흐름
  - `bios.js` 무장 열전 425편(v0.19), `cine.js` 영상 — 제목 · 오프닝 · 끝(v0.19. 영상 파일은 `video/`) — 둘 다 그대로 두는 새 소스
  - `voice.js` 중국어 음성 엔진(v0.13), `duel.js` 일기토 · 설전 화면(v0.13) — 둘은 패치가 아니라 그대로 두는 새 소스다(`build/v013/apply.sh` 참고). `voicedata.js`는 생성물
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
- `bgm/` — 음악 8곡(v0.7, HTML 옆에 두면 재생 — 없으면 코드로 만든 음악). `audio7/` — 소리 원본 기록(`jobs.tsv`). `versions/` — 버전별 스냅샷(아티팩트에는 v0.10부터, v0.1~v0.9.3은 깃허브 저장소의 `versions/`에 — 아티팩트 한 판의 크기 한도 256MiB 때문에 v0.13에서 옮겼다. 옛 소스 묶음 `dev/sources-v0.1~0.6.txt`도 저장소에).

## 소리(v0.7, 쏘는 소리는 v0.12)
- **효과음**: `src/sfxdata.js`의 표본 29개를 처음 누를 때 풀어 두고(`sndLoad`), 장면 이름으로 부른다 — `sfx('hit')`. 장면 → 표본·크기·음높이 흔들림·늦춤은 `src/ui3d.js`의 `CUES` 표 한 곳에서 정한다. 같은 장면은 `gap`(ms) 안에 다시 나지 않는다. 표본이 아직 안 풀렸으면 예전의 만든 소리(`sfxSyn`)가 대신 난다.
  - 움직이는 동안의 소리는 `sfxMove(병과, ms)`(보병 발소리·기병 말발굽·수레), 전투 연출 도중의 소리는 `src/fx.js`의 시간표(`tracks`)에 `on: function () { sfx(...) }`로, 타격 순간의 소리는 `ui_panels.js`의 `resultFx`에서.
- **음악**: `BGM_TRACKS`가 장면(title·field·tense·battle·victory·defeat)마다 곡을 정한다. 여러 곡이면 끝날 때마다 다음 곡으로 돌아간다. 지금의 장면은 `bgmForState()` — 싸운 지 한 턴 안이거나 적이 내 성 2칸 안이면 전투, 적 부대가 내 성 7칸·내 부대 4칸 안이거나 내 부대가 남의 성역에 있으면 긴장, 아니면 평시.
  - 곡을 바꾸려면 `bgm/<이름>.mp3`를 바꿔 넣으면 된다(앱판은 `pwa/sw.js`의 `BGM` 번호도 올린다). 곡을 늘리려면 `BGM_TRACKS`에 이름을 더한다.

## v0.18에서 바뀐 것의 자리
- **무장 카드**(얼굴을 누르면 겹쳐 뜬다): `ui_panels.js`의 `oidAttr(o)`가 초상(`porTag` · `sceneTag` · `duel.js`의 `duPor`)에 `data-oid`를 달고, `ocardInit()`의 잡는 단계 누름 처리기가 `#ocard` 층에 `officerBody(o)`를 띄운다. 창(`MODAL`)의 흐름과 따로 논다 — 닫는 것은 × · 바깥 · Esc · 휴대폰의 뒤로(`appBack`). STATUS 창의 군주 초상 단추(`data-a=lord`)만은 제 일(무장 창)을 한다.
- **특기 풀이 · 적성**: `data.js`의 `SKILL_TAG`(18자 안의 짧은 풀이) → `skTag(o)`가 이름 옆에 붙인다. 무장을 고르는 표(`pickOfficers`)는 줄마다 둘째 줄(`.c-2`)에 `apt5(o)`와 특기.
- **가늠(확률을 말로)**: `ui_panels.js`의 `pcT`(한 마디) · `pcG`(말 + 눈금 다섯 칸) · `pcBest` · `pcWas` · `accT`(군사의 조언). 가늠하는 이는 `oddsEye()` — 군사와 군주 가운데 지력이 높은 쪽, `ODDS_FINE`(70) 미만이면 셋으로 어림. `UI.pct`(메뉴 → 확률 표시, `chunhado_opts`에 남는다)가 켜져 있으면 모두 예전의 `%` 글 그대로다. **시험 틀(`tests/browser.py`)은 `UI.pct`를 켜 둔다** — 말로 보는 화면은 `tests/d31.py`가 끄고 본다.
- **군사의 추천(薦) · 공격 명령이 고르는 수**: `core.js`의 `bestStrike(u, d)` 한 곳 — 보통 공격과 쓸 수 있는 전법 가운데 `주는 피해 − 받는 반격`의 기대값(`attackExpect` · `tacticExpect`)이 가장 큰 것. 전법은 보통 공격보다 5% 넘게 나을 때만.
- **전법의 이름**: `data.js`의 `TACTICS` — id는 그대로, `name`(새 이름) · `han`(한자) · `tag`(단추의 효과 한 줄). 화면(`fx.js` · `ui_panels.js`)은 이름 글자가 아니라 `tacIdOf(res)`로 가린다(`res.tacId`, 옛 기록은 `TACTIC_OLD`로). **견인**(`pull: true`)의 끌어당김은 `unitTactic0`, 미리 아는 것은 `pullRoom(u, d)`.
- **부대 이름표**: `ui3d.js`의 `drawLabel(…, face)` — 얼굴 딱지(`faceAt`)를 판의 왼쪽 위 모서리에 걸쳐 한 장으로 그린다. 스프라이트의 기준점은 `L.ax · L.ay`(판의 윗변 가운데).
- **제목 화면**: 그림은 `tools/make_title18.py`(`art/title18/guanyu_full.png` → `title.jpg`) → `TITLE=… tools/make_assets_v08.py`가 `src/assets.js`의 `TITLE_IMG`로. `tools/build.py`가 그것을 **CSS(`#title { background-image }`)로 옮겨** 큰 스크립트를 읽기 전에 그려지게 한다. 아이콘의 낙관은 `tools/make_icons.py`(天下圖) — 아이콘을 바꾸면 `pwa/sw.js`의 `SHELL` 번호를 올린다(지금 2).
- **초상 60장**: `tools/roster18.py`(이름 → 키) · `art/por18_scenes.tsv`(장면) · `tools/por18_prompt.py` → `POR=18 tools/dl_por17.py` → `art/raw18/` → `tools/facebox.py` → `art/raw18m`(= `raw17m` + `raw18`) → `tools/make_assets_v08.py`. 명부는 `por`만 바뀐다(번호 · 능력치 그대로).
- **레벨이 없는 시설**: `FAC[t].noLv`(공방 · 조폐 · 곡창) → `facHasLv(t)`. `mergeCandidates`가 내놓지 않아 합칠 수 없고(AI도), 화면은 `facLv(fc)`로 레벨을 적지 않는다. 옛 저장의 Lv2 · Lv3은 `deserialize`에서 1로.
- **소리**: 북 둘(`drum` · `drums`)은 `tools/make_audio_v018.py`가 셈으로 만든다(`build/sfxdata.v017.js` → `src/sfxdata.js` = `build/sfxdata.v018.js`). 출진의 장면은 `CUES.deploy`.
- **충차**: `UNIT_TYPES.ram`(이동력 10 · 공성 8) · `ROAD_COST`(길의 칸값은 셋 다 2). 재는 것은 `build/logs/v018/ramspeed.js`(이웃 거점 사이의 날수) · `capt18.js`(AI 끼리의 판에서 성이 넘어가는 빠르기).
- **행군 · 공격 명령**: [행군] 단추가 없다. `ui_panels.js`의 `onTap` — 파란 칸 밖의 땅 → `orderMarch`(곧바로 `marchStep`), 닿지 않는 적 → `orderAim`(`core.js`의 `aimSet` + `aimApproach`), 내 성 · 빈 성 → 그 성의 창 + `[data-a=marchhere]`(`UI.mfrom`). [이동 취소]가 방금 내린 명령의 첫걸음을 물리면 명령도 되돌린다(`UI.mNew`). 규칙은 `core.js`: `u.aim = { k, id }` · `aimTarget` · `aimStep`(턴을 마칠 때 `turnStepper`가 행군 다음 · 군단보다 먼저 한 부대씩 — 단계의 `kind`는 `'aim'`).
- **군단**: `corpsSortie(cp)`(공격 방침은 늘 · 내정 방침은 나가지 않는다 · 군비 · 지원은 `cp.hold`) · `corpsSetHold` · `corpsRecall`. `ai.js`의 `corpsOrders`가 `aiDefense`를 그에 따라 부르고, `aiUnitAct`가 `corpsHolds(u)`인 부대를 귀환시킨다. 군단의 거점 창의 [수송]은 `flowTransport`(군단장은 뺀다).
- **스냅샷**: 한 파일이 20MiB를 넘어 `python3 tools/snap_split.py <버전>`이 `versions/chunhado-v<버전>.html` + `.scenes.json`으로 둔다(아티팩트에 올리는 판과 같은 꼴).
- 시험: `node tests/tac18.js`(전법 · 견인 · 특기 풀이 · 시설) · `node tests/aim18.js`(공격 명령 · 충차 · 군단의 출격) · `python3 tests/d31.py`(화면).

## 무장 명부(v0.17 — 301 → 425명)
- **명부**: `tools/make_roster.py <群雄割據 삼국지 index.html> src/roster.js`. 더한 124명은 `tools/roster17.py`에 있다 — `WOMEN`(여자 38명: 능력치 · 매력 · 적성 · 특기 · 초상 키, 모두 자체 산정) · `ACTIVE17`(194년에 세력에 있는 사람) · `FUTURE17`(재야 · 뒷날 나오는 사람: 이름 · 연도 · 도시 · 합류할 군주) · `CHA17` · `SKILL17`. 남자 86명의 능력치는 원본의 무장 표에서 온다.
  - **더한 사람은 모두 명부의 맨 뒤에 붙는다**(앞쪽 301명의 번호가 바뀌지 않게 — 저장은 무장을 번호로 가리킨다). `SCENARIO.women`은 여성의 이름 표(목소리가 쓴다).
- **초상 39장**(여성 38명 + 대교): `tools/por17_prompt.py`(문구 — 장면은 `art/por17_scenes.tsv`) → Higgsfield → `tools/dl_por17.py`(→ `art/raw17/`) → `tools/facebox.py art/raw17 art/por17_faces.tsv` → `tools/make_assets_v08.py`(본은 `art/raw17m` = `art/raw93m` + `art/raw17`, 얼굴은 `art/por17_faces_all.tsv`). 작업 번호는 `art/por17_ids.tsv`, 자른 틀은 `art/por17_out/crops.tsv`. 순서는 `build/v017/apply.sh` 머리에. 있던 초상 166장은 바이트까지 그대로다.
- **옛 저장**: `rosterGrow(g)`(`deserialize` 안) — 저장의 무장 수가 명부보다 적으면 뒤쪽을 덧붙인다. 세력에 있던 사람은 그 세력이 살아 있으면 그 세력의 거점으로, 망했으면 그 도시의 재야로.
- **인연**: `src/data.js`의 `BONDS`에 더했다. **목소리**: `voice.js`의 `VOICE_WOMEN`(= `SCENARIO.women`).
- 시험: `OLD=<0.16의 src> node tests/roster17.js`(명부 · 번호 · 새 판 · 옛 저장 20가지) · `python3 tests/d29.py`(화면).
- **아티팩트에 올리는 판**(v0.17~): 아티팩트의 페이지 하나는 16MiB까지라서 `python3 tools/build.py --split`이 `dist/artifact/index.html`과 `dist/artifact/data/scenes.json`(무장의 큰 그림 — `SCENES`)으로 나눠 만든다. 페이지가 뜬 뒤 `fetch('data/scenes.json')`으로 받아 `SCENES`를 채우고 `SCENE_URL`을 비운다(받기 전에는 `sceneTag` · `duPor`가 작은 초상을 쓴다). 올릴 때: `index.html` ← `dist/artifact/index.html`, `data/scenes.json` ← `dist/artifact/data/scenes.json`, `versions/chunhado-vX.html` ← `dist/index.html`(한 파일에 다 든 판). 시험은 `python3 tests/d30.py`(http로 내어 본다).

## AI의 일기토 · AI끼리의 협정 · 출병 요청(v0.16)
- **AI가 거는 일기토**(`src/core.js`, 숫자는 `DUEL_K`의 `aiAsk` · `aiLead` · `aiMinWar` · `aiMorale`): `aiWantsDuel(u, d)` → `aiChallenge(u, d)`(`ai.js`가 계략보다 먼저 부른다).
  - 내 부대에 걸면 그 자리에서 정하지 않고 `G.asks`(`{ a, d, turn }`)에 적는다 → 내 차례에 `duelAskAnswer(aid, did, yes)`: 받으면 겨룰 판(`res.duelS`)을 돌려주고 화면이 `duelOpen(S, 'd', …)` → `duelFinish(S, res)`. 답하지 않으면 턴을 넘길 때 `duelAsksLapse()`가 받지 않은 것으로 친다. 지금도 유효한 것만 `duelAsks()`.
  - AI끼리(와 내 군단 → AI)는 `unitChallenge` 그대로. 재생은 `presentEvent`의 `e.t === 'ask'` · `e.res.kind === 'challenge'` 가지.
- **AI끼리의 협정**(`DIP_K`의 `threat` · `aiPact` · `aiPactUp`): 달이 바뀔 때 `dipMonthAI()` — `dipNbrs()`(이웃한 세력) · `dipThreat(f)`(병력이 `threat`배 이상인 가장 센 이웃)가 같은 이웃끼리 정전 → 동맹.
- **출병 요청**(`aimBase` · `aimWar` · `aimTurns` · `aimRel` · `aimRefuse` · `aimCool` · `aimScore` · `aimNeed`): `aimCan(f, t, x)`(청할 수 없는 까닭) · `aimTerms(f, t, x, 사신)` · `cmdAim(b, id, t, x)` → `G.dip.aim[t] = { f: x, until, by }`. AI는 `dipAimOf(f)`인 세력의 거점에 점수를 더하고 필요한 병력을 낮춘다(`ai.js`).
- **화면**: `flowDuelAsk(aid, did)`(답하는 창) · `askSoon()`(요약을 닫은 뒤 저절로) · `todoList`의 `go: ['duelask', a, d]` / `flowAim(b, t)`(칠 상대 고르기) · `pactsLine(f)`(다른 세력끼리의 협정 한 줄).
- 시험: `node tests/ai16.js`(규칙 26가지) · `python3 tests/d28.py`(화면). 화면 시험은 `aiAsk` · `aiPact` · `aiPactUp`을 0으로 두고 돈다(`tests/browser.py` — `AI_ASK` · `AI_PACT`로 바꿀 수 있다).

## 지형(v0.15)
- **지도**: `MAPDATA.t`(지형) · `MAPDATA.t0`(산을 넓히기 전의 지형) · `MAPDATA.e`(칸의 높이 단계, 36진수 한 글자). `tools/terrain15.py`가 만든다:
  `steep`(산에 붙은 가파른 칸을 산으로 — `mapdata.json`의 `traw`도 고친다. 그림을 굽는 `bake3d_ink.py`가 그것을 본다) → `bake3d_ink.py`(그림 · 높이맵) → `elev`(높이 단계). 순서는 `build/v015/apply.sh` 머리에.
- **규칙**(`src/core.js`, 숫자는 `src/data.js`의 `ELEV_K` · `TERR_K`): `terrMods(a, d, ranged)`가 이 싸움에 곱해지는 값의 내역을 돌려주고 `dmgBase`가 그 곱(`terrMul`)을 쓴다. 높이는 `ELV[k]` · `elevOf(c, r)` · `elevDiff(a, d)`.
- 옛 저장: `terrainFix()`(`deserialize` 안) — 못 가는 칸에 선 부대를 옮긴다.
- **화면**: `terrLine(u)`(부대 창) · `terrNote(a, d)`(대상 창). 칸 줄은 `ui3d.js`의 `stTex`(갈 수 있는 칸 = 255) — 지형이 바뀌면 저절로 따라간다.
- 시험: `node tests/terr15.js` · `python3 tests/d27.py`.

## 외교(v0.14)
- **규칙**(`src/core.js`, 숫자는 `src/data.js`의 `DIP_K`): 상태는 `G.dip`(우호 `rel` · 협정 `pact` · 다시 청할 수 있는 턴 `cd` · 선물한 턴 `gift` · 마지막으로 싸운 턴 `war` · 청해 온 제안 `offers`). 없으면 `dipOf()`가 그 자리에서 만든다(옛 저장).
  - 읽기: `relOf(a, b)` · `pactOf(a, b)` · `pactOn` · `dipTerms(f, t, kind, 사신)`(받아들일 확률과 내역) · `dipCan`(청할 수 없는 까닭) · `dipOffers()`.
  - 명령: `cmdGift(b, id, t)` · `cmdTreaty(b, id, t, 'truce' | 'ally', S)`(S = 끝난 설전) · `cmdBreak(f, t)` · `dipAnswer(from, kind, yes)`. 설전은 `dipTalkNew`.
  - 협정의 효과는 다섯 곳에서 건다: `attackTargets` · `ployTargets` · `challengeTargets`(대상에서 뺀다), `pactErr`(공격 · 전법 · 계략 · 일기토의 문턱), `aiMayStrike`(AI). 그 밖에 `canPoach`, `ai.js`의 `enemyUnitsNear`.
  - 때: 칠 때 `dipHit`(actEv), 턴이 바뀔 때 `dipTurn`(협정의 끝), 달이 바뀔 때 `dipMonth`(우호가 돌아감 · AI의 제안).
- **화면**(`src/ui_panels.js`): `flowDip(b)` → `flowDipFac(b, t)` → 사신 고르기(`pickOfficers`, [설전]은 `flowDipTalk`). 청해 온 제안은 `flowDipOffer`, [지금 할 일]에는 `todoList`의 `go: ['dip', 세력, 종류]`. 칠 수 없는 상대는 `targetActions` 첫머리에서.
- 시험: `node tests/dip14.js`(규칙 37가지) · `python3 tests/d26.py`(화면).

## 음성(v0.13)
- **소리**: `src/voicedata.js`(생성물) — `VOICE_DATA['<갈래>_<상황>_<1|2>']` = mp3(base64) 120개, `VOICE_TEXT` = [中文, 뜻]. 만드는 법: `voice13/raw/NNN.mp3`(뽑은 원본, 순서는 `voice13/lines.py`의 `all_lines()`) → `python3 tools/make_voice_v013.py`.
- **엔진**: `src/voice.js`. `voiceKind(o)`가 목소리 갈래를 고르고, `voiceSay(o, 상황, opt)`가 말한다(확률 `p` · 늦춤 `delay` · 뜻풀이 자리 `at`/`cap`). 겹칠 때의 차례는 `VOICE_PRI`. 효과음과 같은 길(`sndBus`)로 나간다.
- **부르는 곳**: 대화창 — `sayLine`이 고른 말의 열쇠를 `SAYV`에 적고 `talk`가 `voiceTalk`를 부른다(열쇠 → 상황은 `VOICE_KEY`). 싸움 — `fx.js`의 `animAct` 시작에서 `voiceAct(res, 0)`, `ui_panels.js`의 `resultFx` 끝에서 `voiceAct(res, 1)`. 대결 화면 — `duel.js`의 `duelOpen` · `duEnd`.
- 대사를 바꾸거나 늘리려면: `voice13/lines.py`를 고치고 그 줄만 다시 뽑아 `voice13/raw/`에 넣은 뒤 도구를 돌린다. 상황을 늘리려면 `VOICE_PRI`에도 더한다.
- 시험: `python3 tests/d25.py`. 받아쓰기 점검에 쓴 것: `voice13/qa.py`(길이 · 크기 · 음색).

## 일기토 · 설전(v0.13)
- **규칙**(`src/core.js`, 숫자는 `src/data.js`의 `DUEL_K` · `DUEL_KIND`): `duelNew(kind, A, D, opt)` → 합마다 `duelPlan` · `duelStep(S, ma, md)` → `duelFinish(S, res)`가 결과를 부대에 입힌다. 저절로 겨루는 것은 `duelAuto`, 끝난 판의 기록은 `duelRecOf`.
  - 싸움에서 벌어지는 일기토: `duelBattle(a, d, res)`. 화면이 `DUEL_DEFER`를 켜 두면 판만 만들어 `res.duelS`로 넘기고(내가 수를 고른다), 아니면 그 자리에서 판정하고 `res.duelRec`를 남긴다.
  - 신청: `unitChallenge(u, t)`(응할 확률 `challengeChance`). 설전으로 등용: `talkRecruitNew` → 끝난 판을 `cmdRecruit(b, id, tid, S)`에 넘긴다.
- **화면**(`src/duel.js`): `duelOpen(S, human, opt, done)` — 수 고르기 · 한 합의 연출(`duAnim`) · 결과. `duelReplay(rec, opt, done)`는 적힌 합을 그대로 그린다(지난 열흘의 재생에서).
- 시험: `node tests/duel13.js`(규칙 · 승률) · `python3 tests/d24.py`(화면).

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

## v0.12에서 바뀐 것의 자리
바뀐 기록은 `build/v012/p1_tactic`(전법 실패의 피해) · `p2_fac`(시설 칸의 통행) · `p3_share`(세이브 파일 보내기 · 가져오기) · `p4_sound`(쏘는 소리의 큐) · `p5_deploy`(나갈 자리) · `p6_more`(아래에 더 있다는 표시). `bash build/v012/apply.sh`가 v0.11의 소스에서 다시 만든다. 효과음은 따로 `python3 tools/make_audio_v012.py`(바탕은 `build/sfxdata.v011.js`, ffmpeg 필요 — 다시 돌려도 바이트까지 같다).
- **전법 실패**(`data.js`): `TACTIC_K.failDmg` 0.4 → 0.85. 실패 갈래는 `core.js`의 `unitTactic0`, AI의 기대값은 `tacticExpect`, 도움말 · 전법 풀이는 이 상수로 글을 만든다. 두 규칙을 같은 장면에 대어 보려면 `SETS='{…}' node tests/tac91.js`.
- **시설 칸**(`core.js`): 길을 막던 세 곳(`unitReach` · `longPath` · `canPushInto`)에서 시설 검사를 뺐다. 출진 자리(`deploySpot`의 점수)는 시설 칸에 +4(가는 곳이 정해져 있으면 +0.5) — 빈 땅이 먼저다. `facUnder(u)` = 부대가 올라선 남의 시설(대상 꼴 `{ kind: 'fac', d: 0 }`), `attackTargets`의 끝에 붙는다.
  - 화면(`ui_panels.js`): 부대 창의 `data-a="facunder"`(발밑의 시설을 대상으로) · 대상 창의 `data-a="moveon"`(그 칸으로 이동), `onTap`에서 칠 수 없는 남의 시설 칸은 이동으로. 그림(`ui3d.js`의 `syncScene`): 부대가 선 시설은 불투명도 ×0.38(`fo.sig` 끝의 `u`).
- **세이브 파일**(`ui_panels.js`): 보내기 `showSaveSend()` — `saveFileText(칸)` → `{ name, meta, text }`(머리말 두 줄 + 저장본), `saveFileObj` · `canShareFile`(공유 창이 파일을 받는가) · `saveDownload` · `copyLong`. 받기 `flowImport(글, 넣은 뒤 할 일)` — `saveParse`(꼴 · 글자 · 색) → `saveShapeOk`(지도 · 세력 · 병과와 맞는가) → `saveProbe`(열어 보고 하던 판을 되돌린다) → `firstEmptySlot()` 또는 덮어쓸 칸 고르기. 파일 고르기 `pickSaveFile`, 붙여넣기 `showSavePaste`. `loadFrom`은 실패하면 하던 판을 되돌린다.
  - Claude 아티팩트 안(v0.12.1, `build/v0121/p1_dlcap`): `inClaude()`(= `window.claude.use`가 있다) · `dlCapAsk(cb)` → `DLCAP`(undefined 아직 · 0 묻는 중 · null 없음 · 객체). 그 안에서는 `DLCAP.save({ filename, data })`로만 내보내고 공유 창 단추는 내지 않는다. 아티팩트에는 `downloads` 기능이 선언되어 있어야 한다(`declare_capabilities`).
- **쏘는 소리**: 표본 `bow` · `arrows` · `thock` · `arrowland` · `drum`(`tools/make_audio_v012.py`의 `make()` · `drum_fix()`), 큐 `arrowhit` · `arrowbig` · `arrowgreat` · `arrowfail`(`ui3d.js`의 `CUES`), 고르는 곳은 `ui_panels.js`의 `shot`(두 칸 밖이거나 화시 · 관시 · 난사).
- **나갈 자리**(`core.js`): `deploySpots(b)` = 둘레의 나갈 수 있는 칸들, `cmdDeploy`의 `spec.at = [c, r]`(없으면 전처럼 `deploySpot(b, spec.toward)`). 화면은 `deployRing(b, st)`(여섯 칸 그림 — `hexCenter`의 차이로 자리를 잡으므로 지도와 방향이 같다) · `ringOn(st)`(`at` · `atauto` 두 단추) · `spotWhat(c, r)`(칸에 적는 말) · `dirName`. CSS `.dring` · `.dpat`.
- **아래에 더 있다는 표시**(`ui_panels.js`): `moreInit()`이 `#modal` · `#sheet`의 내용이 바뀌는 것을 지켜보다가 `moreScan()`으로 굴러가는 몸통(`.dlg-b` · `.sh-body`)의 끝에 `.morehint`(높이 0 · sticky)를 붙이고, `moreSet(body)`가 남은 길이(`MORE_GAP` 10px)로 켜고 끈다. 새 굴림 몸통을 만들면 `moreScan`의 선택자에 더한다.
- **중국어 음성**: 아직 없다. 계획과 견적은 `dev/v012_voice_plan.md`.

## v0.11에서 바뀐 것의 자리
바뀐 기록은 `build/v011/p1_small`(시설의 레벨 표시 · 적성 줄 · 치안 풀이 · 출진 군량 · 공유) · `p2_recruit`(등용과 옛 관계) · `p3_supply`(수송대의 보급) · `p4_counsel`(군사의 헌책 · 탐색) · `p5_zoom`(확대한 지도). `bash build/v011/apply.sh`가 0.10.1의 소스에 차례로 입힌다. 규칙이 바뀐 곳은 등용 · 탐색 · 보급 · 출진 군량의 선택지다.
- **시설의 글**(`ui_panels.js`): `facDesc(fac)` = 지금 레벨의 값이 먼저인 한 줄(줄 · 창), `facYield(b, pi)` = 그 시설 하나를 뺀 수입 셈과의 차이(실제로 보태는 수입), `facNow(b, pi)` = 창의 둘째 줄(까닭 · "보탬이 없습니다"), `mergeGain` · `mergeNote` = 합치면 달라지는 수입과 비는 부지. `FAC[t].desc`는 새로 지을 때(Lv1)의 카드에만 쓴다.
- **적성 줄**: `apt5(무장, 밑줄 칠 칸)`을 `offRow`가 능력치 아래에 붙인다(`opt.noapt`로 뺄 수 있다). CSS `.ap5`.
- **치안**: `incPct(치안)` · `draftPct(치안)`(셈은 `goldIncome` · `draftAmount`와 같다), 풀이 창 `showOrderInfo(b)` — 거점 창의 치안 칸(`data-a="order"`).
- **출진 군량**: `DEPLOY_FOOD = [9, 18, 27, 36]`(턴 수), 처음 값은 둘째. `flowDeploy`의 `foodNote()`가 모자랄 때의 날수를 적는다.
- **공유**: `SHARE_URL` · `SHARE_QR`(그 주소의 QR 33줄 — 주소를 바꾸면 다시 만든다), `shareUrl()`(manifest가 있는 빌드면 지금 주소) · `shareGame()`(공유 창 → 안 되면 `showShare()`) · `qrSvg` · `copyText`.
- **등용과 옛 관계**(`core.js`, 상수 `TIES`): 무장의 `pf`(마지막으로 섬긴 세력) · `past`(그 앞의 세력들) — `pastNote(o)` · `pastSweep()`(턴이 넘어갈 때 · 등용 직후 · 불러올 때), `servedF(o)`(섬겼던 세력, 지금 세력은 뺀다) · `lastF(o)` · `fallenOf(t)`. 사이는 `tieOf(보내는 무장, 대상, 권하는 세력)` → `{ k: bond|lord|kin|vassal|mate, v, label, short }`, 원한은 `grudgeOf(세력, 대상)`(참수한 쪽이 `exBy`에 남는다). 성공률은 `recruitTerms(b, o, t)` → `{ p, why: [[글, 값]…], tie, no }`이고 `recruitChance`는 `p`만 돌려준다. 화면은 `originTxt` · `whyTxt` · `servedTxt`, 등용 창의 `tieSub`.
- **보급**(`core.js`): `supplyTargets(수송대)` · `supplySources(부대)` · `supplyMax(t, u)` → `{ food, troops, why }` · `cmdSupply(t, u, { food, troops })`. 화면은 `supplyPairs(부대)` · `pickSupply` · `flowSupply`, 수송대 창의 `cargoLine`.
- **탐색**(`core.js`): `searchSkill(o)` · `searchChance(b, o)`(숨은 인재가 없으면 0) · `searchKey(b)`(도시 · 턴 · 그 턴의 몇 번째 — 도시의 `sN` · `sT`) · `searchRoll` · `searchRollA`. `cmdSearch`는 그 주사위로 정한다. 조언은 `searchAdvice(b, o)`.
- **헌책**(`core.js`, 상수 `COUNSEL`): `counselRaw(세력)` = 후보 `{ kind, b, w, d, x }`(직접 다스리는 거점만) → `counsel(세력)` = 군사의 지력으로 거른 `{ adv, lvl, list }`. 무엇을 지을지는 `buildPick(b, 이웃의 위협)`, 이웃의 위협은 `nbrThreat(b)`. 말은 화면 쪽 `counselText(후보)` → `{ say, tip, go }`, 지금 말할 것은 `counselPick`(되풀이를 `UI.cSaid`로 막고 `UI.cSkip`으로 넘긴다). `advTop`의 차례: 급한 알림 → 헌책 → 그 밖. 재 보는 것은 `node tests/cns11.js`.
- **확대한 지도**(`ui3d.js`): 땅 셰이더의 `#ifdef MAGFIX` 토막 — `magK`(화면 한 점에 그림 몇 점인가 × `pxr`로 정한다), `texBic`(3차 B-스플라인), `nz`(잡음을 맞는 축소본에서 읽는다). 켜는 조건은 `R3.magfix`(WebGL2 또는 `EXT_shader_texture_lod`). 문턱(0.28 · 0.45), 흔드는 폭(1.2), 종이 결의 세기(0.06 · 0.045)는 셰이더 안의 숫자다.

## v0.10.1에서 바뀐 것의 자리
바뀐 기록은 `build/v0101/p1_adv`(군사의 적중률) · `p2_fsel_site`(고른 시설의 표시 · 부지 번호 · 공사장 그림) · `p3_saves`(세이브 칸). `bash build/v0101/apply.sh`가 0.10의 소스에 차례로 입힌다. 규칙이 바뀐 곳은 `adviceAcc` 하나다.
- **군사의 적중률**(`core.js`의 `adviceAcc`, 상수 `ADVISE`): 군사의 지력 그대로, 상대가 더 똑똑하면 그 차이 × `ADVISE.k`(0.5)만큼 깎고 `ADVISE.min`(50)~100. 재 보는 것은 `node tests/adv101.js`(세력마다 대상별 평균).
- **고른 시설**: 시설 창(`flowFacility`)은 `fsel: { b, pi }` · `see: true`를 달고 뜬다 — `fselOf()`가 그것을 찾고, `buildView()`가 `fi`(고른 시설의 부지)와 시설마다 `{ i, no, left }`를 넘기면 `ui3d.js`의 `spotDraw`가 그 칸을 환하게 뚫고(둥글게 번지는 구멍) 붉은 테두리를 두르고 이름표를 붉은 딱지로 그린다. 지도를 누르면 `fselTap` — 같은 거점의 다른 시설이면 그 시설로, 빈 부지면 `flowDevelop`으로, 그 밖이면 닫는다(`devTap`도 시설을 누르면 `flowFacility`로 간다). 건설 자리를 보는 동안(`SPOT.on`) `pickAt`은 그 거점의 부지를 성의 그림보다 먼저 집는다.
- **부지 번호**: `lotNo(b, pi)`(v0.9.3)가 지은 시설에도 붙는다 — 지도의 이름 앞 딱지(`spotDraw`의 `facLabels`), 시설 탭의 줄 앞(`lotChip`, CSS `.lno`), 시설 창의 제목(`lotMark`). 시설 탭의 줄은 번호 차례.
- **공사장 그림**(`ui3d.js`): `siteCanvas(시설, 단계)`가 그 시설의 그림(`SITE_IMG`)을 먹빛만 옅게 남기고(`SITE_INK` · `SITE_A`) 비계 · 통나무 · 깃발을 덧그린다. `siteTexKey(시설, 단계)`가 `TEX['market@1']` 꼴로 만들어 두고 `syncScene`이 짓는 중인 시설에 쓴다(단계 = `siteStage(fc)`, 공사의 3분의 1마다). 작은 그림은 `siteUrl(시설)` → `facThumb(fc)`.
- **세이브 칸**(`ui_panels.js`): 칸 id는 `auto`(자동 — 전부터 쓰던 `SAVE_KEY`) · `prev`(직전 판) · `s1`~`s6`(`SAVE_SLOTS`), 열쇠는 `slotKey(id)`. 요약은 `SAVE_KEY + '_meta'`에 `{ id: { f, c, d, turn, n, tr, t, len } }` — `slotInfo(id)`가 읽고, 없거나 길이가 어긋나면 저장본에서 다시 만든다. `saveGame()`(자동) · `saveTo(id)`(그 칸 + 자동) · `loadFrom(id)`(하던 판은 `keepPrev`로 직전 칸에, 불러온 판은 자동 저장에) · `slotDrop(id)`. 창은 `showSaves('save' | 'load')`, 제목 화면의 단추는 `#tLoad`(`titleBtns()`가 켜고 끈다). 새 게임은 `keepPrev()` → `newGame` → `saveGame()`.

## 군단(v0.10)
바뀐 기록은 `build/v010/p1_core`(규칙) · `p2_ai`(군단장의 판단) · `p3_ui`(화면). `bash build/v010/apply.sh`가 0.9.3의 소스에 차례로 입힌다. AI 세력의 규칙은 건드리지 않았다(AI 대전 216턴의 출력이 0.9.3과 같다).
- **자료**: `G.corps = [{ id, n(제n군단), lead(군단장 무장 id, 비면 -1), dir, target, ap, t0, note, wait }]`, 거점 `b.corps` · 부대 `u.corps` = 군단 id(직할이면 0 · 없음). 방침 `dir`: `dev` 내정 · `arm` 군비 · `atk` 공격(`target` = 칠 거점) · `sup` 지원(`target` = 보낼 내 거점). 상수는 `data.js`의 `CORPS_MAX`·`CORPS_DIR`·`CORPS_AP`·`CORPS_ATK`.
- **규칙**(`core.js`): `corpsCreate(거점들)` · `corpsAssign` · `corpsRelease`(직할로) · `corpsTakeUnit`(부대를 직할로) · `corpsDisband` · `corpsSetDir` · `corpsSetLead`. 뒤처리는 `corpsFix()` — 잃은 거점의 표시 지우기, 거점이 없는 군단 해산, 빈 군단장 자리 채우기, 이룬 방침을 군비로 돌리기(내 차례가 시작될 때와 군단의 차례 앞뒤에 부른다). 거점의 주인이 바뀔 때(`captureBase`) 군단의 부대가 차지했으면 그 군단에 든다.
- **행동력**: 군단은 `cp.ap`을 따로 쓴다 — 차례마다 `corpsRegen` = 20 + 도시 × 8 + 군단장 매력 ÷ 5(120까지), 255까지 쌓인다. 직할의 `apRegen`은 직할 도시만 센다.
- **차례**: `turnStepper`의 첫 단계 — 내가 턴 종료를 누른 직후, 다른 세력보다 먼저. `corpsStart`(행동력을 채우고 장부 `JOT`를 연다) → `ai.js`의 `corpsStepper`(한 행동씩) → `corpsEnd`(한 일을 `corpsNoteText`로 한 줄 — 기록에 `corps: id`가 붙는다).
- **군단장의 판단**(`ai.js`): AI 세력의 판단을 그대로 쓰되 `AISCOPE`(지금 도는 군단)로 볼 거점·부대를 좁힌다(`aiBases`·`aiCities`·`aiNearBase`). 도는 동안 세력의 행동력 자리에 군단의 행동력을 잠깐 넣는다. 방침에 따른 차이는 `aiInternal`의 `DIR`(징병 한도 · 한꺼번에 벌이는 공사 수 · 탐색 · 병기), 공격은 `corpsTargets`·`corpsNeed`·`corpsDef`·`corpsFoeK`·`corpsAvail`·`corpsPool`(나서는 문턱과 낼 수 있는 병력), 지원은 `corpsSupply`. 화면이 쓰는 가늠은 `corpsOutlook(cp, 거점)` → `{ need, have, going, len, k }`.
- **화면**(`ui_panels.js`): STATUS 창의 군단 줄 `corpsStrip`, 군단 창 `showCorps`, 새 군단 `showCorpsNew`, 목표 고르기 `pickCorpsTarget` · 보낼 곳 `pickCorpsDest` · 거점 넣기 `pickCorpsBase`. 거점 창은 `baseCorps(b)`가 있으면 군단 띠(`.cpbn`)와 [군단] · [직할로]만, 직할 거점에는 `corps` 탭. 부대 창은 `unitCorps(u)`가 있으면 하는 일(`unitMission`)과 [군단] · [직할로]. '지금 할 일'과 `pendingUnits`는 `directBases`·`directUnits`만 본다. 군단장의 대답은 `corpsSaid`(말은 `SAY.corps`·`cdev`·`carm`·`catk`·`csup`). 지도의 딱지는 `ui3d.js`의 `corpsMark`.

## v0.9.3에서 바뀐 것의 자리
바뀐 기록은 `build/v093/p1~p3`(`bash build/v093/apply.sh`가 0.9.2의 소스에 차례로 입힌다). 규칙이 바뀐 곳은 `tacticCrit` 하나다.
- **대화창**: `index.html`의 `#talk`, `ui_panels.js`의 `talk(무장, 말, 결과 한 줄, 뜨는 시간)`·`talkHide()`. 화면 위쪽에 초상 · 이름 · 딱지(`roleOf` — 군주/군사) · 세력 · 말 · 결과가 뜨고 2.6~5.2초 뒤(말의 길이에 따라) 사라진다. 누르면 바로 닫힌다(`ui3d.js`의 누름 처리). 창(`#modal`)보다 위에 뜨고 명령의 흐름은 막지 않는다. 메뉴의 '대화창 켜짐/꺼짐'(`UI.talk`, 설정 `chunhado_opts.talk`)을 끄면 `talk`이 결과 한 줄만 태그를 떼어 알림 줄(`toast`)로 넘긴다.
- **말**: `SAY[일][말투]`(일 18가지 × 말투 셋 — `toneOf`: 군주 `L` · 무인 `W`(무력 70 이상이고 지력보다 10 넘게 높다) · 문관 `C`)와 `SAY_OWN[이름][일]`(이름난 무장의 제 말). `sayLine(무장, 일, 넣을 말)`이 하나를 고른다 — `{x}{을}`·`{x}{이라}`는 받침에 맞춰 붙인다. 화면의 말뿐이라 판의 주사위(`rnd`)는 쓰지 않는다.
- **명령의 결과**: `done(결과, 한 줄, 소리, 말하는 무장, 일, 넣을 말)` — 말하는 무장이 있으면 대화창, 없으면 전처럼 알림 줄. 말하는 사람: 징병·순찰·훈련·생산·건설·흡수합병·탐색·이동은 맨 먼저 고른 무장, 출진·수송은 주장, 등용·포상·포로 해방은 상대, 거래는 군사(없으면 군주). 안 되는 명령의 까닭, 참수 · 철거 · 공사 중단, 부대의 공격 · 전법 · 계략의 결과는 알림 줄 그대로다.
- **군사의 말**: ① STATUS 창 맨 위 `.hm-advp` — 초상 + '지금 할 일' 가운데 맨 위 것의 말(`todoList`의 줄마다 `say`, `advTop`이 고른다; 누르면 `advgo` → `goTodo`) + [바꾸기]/[임명](`adv` → `showAdvisor`). ② 내 차례가 시작되면 `advBrief()`가 그 말을 대화창으로(한 턴에 한 번 — `UI.briefT`; 같은 말은 세 턴에 한 번 — `UI.briefSay`·`UI.briefAt`; 요약 창이 닫힌 뒤: `closeDialog`가 창의 `onClose`를 부른다). 대화창을 꺼 두면 뜨지 않는다. ③ 창 안의 한 줄 `sayRow`·`advSay` — 등용할 무장을 고르는 표 아래(`pickOfficers`의 `opts.say` → `.pksay`), 계략을 쓸 수 있는 대상을 골랐을 때의 부대 창(`.advn`). ④ 조언이 빗나가면 `advAfter`가 덧붙일 말을 준다(등용은 결과 줄 뒤 `.tk-adv`, 계략은 군사의 대화창).
- **군사 임명**: `showAdvisor()` — 후보 줄마다 [임명] 단추(`data-a="set"`). 임명하면 새 군사가 대화창에서 답한다.
- **건설 번호**: `lotNos(b)` — 성을 가운데 두고 북쪽에서 시계 방향으로 부지마다 1, 2, 3 …(같은 방향이면 가까운 것 먼저). 거점마다 한 번 셈해 둔다(`LOTNO`). 창의 단추와 `buildView().lots`는 번호 차례(`emptyLotsByNo`)이고, 지은 칸의 번호는 건너뛴다.
- **전법의 대성공**: `core.js`의 `tacticCrit(u, d)` — 보통 공격이 치명타가 되는 조건(`critNormal`: 비장·용장·신장 + 상대보다 무력이 높다)이면 전법도 성공했을 때 대성공(`TACTIC_K.crit` 1.25배, 신장은 `critGod` 1.375배). 병과 특기(창장·극장·궁장·기장·투신·궁신·기신)의 대성공과 겹치면 큰 쪽.
- **초상 17장**: `tools/por93_prompt.py`(문구) → Higgsfield → `tools/dl_por93.py` → `tools/facebox.py` → `tools/make_assets_v08.py`(본은 `art/raw93m` = v0.7 그림에 17장만 바꾼 것). 작업 번호는 `art/por93_ids.tsv`, 얼굴 위치는 `art/por93_out/crops.tsv`.

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
python3 tools/make_audio_v012.py         # v0.12: build/sfxdata.v011.js → src/sfxdata.js (쏘는 소리 넷을 새로 만들고 북에 배음)
python3 tools/make_voice_v013.py         # v0.13: voice13/raw/*.mp3 → voice13/out/*.mp3, src/voicedata.js (중국어 음성 120개)
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
