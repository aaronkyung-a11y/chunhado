# v0.5 초상 다시 그리기 — 작업 절차와 상태 (이 파일만 보고 이어 갈 수 있게)

요청(2026-11-19 21:24): "초상화가 너무 정면을 보고 밋밋하네. 특유의 포즈나 표정, 유명한 한 장면을 담으면 좋은데"

## 방식
- 모델 nano_banana_pro, aspect_ratio 3:4, resolution 1k(장당 2크레딧), medias = [{role: image_references, value: <v0.4 수묵 초상 작업 ID>}] 한 장.
- 프롬프트 = 머리말 + 장면 + 맺음말. `python3 tools/por5_prompt.py text <key>` 로 전문을 볼 수 있다. 장면은 `art/por5_scenes.tsv`(남성)·`art/por5_scenes_f.tsv`(여성 3명).
- 묶음: `python3 tools/por5_prompt.py plan` → 12개씩 13묶음(index key 참조작업ID). 견본 12명은 이미 끝남.
- 제출: mcp generate_image_batch(requests ≤12, index = por5_plan 의 index). 받은 작업 ID를 `art/por5_submit.tsv` 에 "index<TAB>job_id" 로 덧붙인다(다시 그리면 같은 index 로 한 줄 더 — 나중 줄이 이긴다).
- 기다리기: jobs_wait(≤12개, ≤15초) 반복. 결과 주소의 시각(HHMMSS)만 읽어 둔다.
- 내려받기: `printf '<index> <HHMMSS>\n…' | DATE=<YYYYMMDD(UTC)> python3 tools/dl_por5.py /tmp/sheet.jpg` → `art/raw5/<key>.png`(896×1200), `art/por5_jobs.tsv`.
- 얼굴 찾기: `python3 tools/facebox.py art/raw5 art/por5_faces.tsv` (YuNet 모델: /home/claude/dl_yunet/yunet_2023mar.onnx — opencv_zoo 에서 받음). 못 찾거나 틀리면 `art/por5_focus.tsv` 에 "key x y w h"(원본 픽셀) 로 직접 적는다.
- 자산: `python3 tools/make_assets_v05.py art/raw5 art/por5_faces.tsv art/por5_out src/assets.js build/assets.v04.js src/roster.js 256 320 72 56` → PORTRAITS(얼굴 중심 정사각 256px) + SCENES(3:4 장면 320px).
- 확인: `python3 tools/qa_por5.py art/por5_out /tmp/qa.jpg key…` (장면 | 흉상 | 작은 칸 모양).
- 다시 그릴 것은 첫 그림을 `art/raw5_alt/` 로 옮겨 두고 새로 받는다.

## 상태
- [x] 견본 12명(guanyu zhangfei liubei caocao lubu zhugeliang zhaoyun diaochan sunce xiahoudun huangzhong zhouyu) — 사용자에게 견본 보냄(art/ink_test/sample_portraits_v05.jpg)
- [x] 묶음 1~13 + 다시 그린 것 모두 끝남(아래 기록)
- 묶음 1 제출(21:5x KST): index 0,2~12
- 묶음 1 내려받음(확인: 좋음). 묶음 2 제출: index 13~16,18~25
- 묶음 3 제출: index 26~31,33~38
- 묶음 2 내려받음(index 21 만 아직). 묶음 4 제출: index 39~44,46~51
- 묶음 3 내려받음(index 38 만 아직). 묶음 5 제출: index 52~63
- 묶음 4 내려받음(index 44 만 아직). 묶음 6 제출: index 64,65,67~72,74~77. (dl_por5.py: '~HHMMSS idx…' 로 같은 묶음을 더듬어 받을 수 있음 — 묶음의 한 작업만 jobs_wait 로 시각을 확인)
- index 44(황권) nsfw 오탐 → 문구 바꿔 다시 제출할 것
- 묶음 5 내려받음. 묶음 7 제출: index 78~89
- 묶음 6 내려받음(index 74 여령기만 아직). 묶음 8 제출: index 90~95,97~102
- index 74(여령기) nsfw 오탐 → 문구 바꿔 다시 제출할 것
- 묶음 7 내려받음(index 78 마초만 아직; 82 모개는 리본 달린 선물 상자라 다시 그릴 후보). 묶음 9 제출: index 103~107,109~115
- 묶음 8·마초 내려받음. 묶음 10 제출: index 116~127
- 묶음 9 내려받음(index 107 문빙만 아직). 묶음 11 제출: index 128~132,134~140
- 묶음 10 내려받음(index 121 염상·123 엄안 아직; 107 문빙 queued). 묶음 12 제출: index 141~144,146~149,151,153~155 (축융은 'woman general … in full armor' 로 문구 조정)
- 묶음 13 제출: index 156~166 + 44(황권, 문구 바꿈: 조정에서 홀을 들고 간함). 남은 일: 107·121·123 확인, 74 여령기 다시, 82 모개 다시(선택), 묶음 11~13 내려받기
- 묶음 11·12·13 내려받음. 154 축융 nsfw 오탐. 남은 것: 107 문빙(진행 중), 74 여령기·154 축융(문구 바꿔 다시), 82 모개(선택)
- 다시 제출(문구 바꿈): 74 여령기, 154 축융, 82 모개(첫 그림은 raw5_alt/maojie_v1.png)
- 167장 모두 내려받음(21:5x~22:2x KST). 얼굴 상자: 자동 166 + 손으로 1(lijue). src/assets.js 생성. 남은 일: UI 확인·시험·문서·게시
- 80 마량 다시(흰 눈썹 강조; 첫 그림 raw5_alt/maliang_v1.png)
- 완료: 167장 확정(마량·모개 다시 그림 포함), src/assets.js 생성, v0.5 빌드·시험·문서.

## v0.6 (2026-11-20) — 그림 작업 없음
뒤로 가기만 고친 판. 초상·지도 그림은 v0.5 그대로(assets.js 동일). 게시 버전 1795102266-dd48(소스 묶음 보완 포함).
