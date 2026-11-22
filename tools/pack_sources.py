#!/usr/bin/env python3
"""소스 묶음: python3 tools/pack_sources.py <버전> <out.txt>  — 손으로 쓴 소스·도구·시험·그림 기록을 한 파일로(생성물은 index.html 안에 있음)"""
import os, sys
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
ver, out = sys.argv[1], sys.argv[2]
FILES = '''README.md CHANGELOG.md
src/index.html src/style.css src/data.js src/core.js src/ai.js src/ui3d.js src/fx.js src/voice.js src/duel.js src/ui_panels.js src/bios.js src/cine.js
build/patch_v04_ui3d.py build/patch_v04_panels.py build/v07/p1_core.py build/v07/p2_audio.py build/v07/p3_fx.py build/v07/p4_ui.py
build/v071/p1_job.py build/v071/p2_job_ui.py build/v071/p3_trans.py build/v071/p4_edge.py build/v071/p5_zone.py build/v071/p5b_zone_ui.py build/v071/p5c_fac.py build/v071/p6_econ.py build/v071/p7_tactic.py build/v071/p7b_tactic_ui.py build/v071/p8_plots.py build/v071/p8b_plots_ui.py build/v071/p9_loyalty.py
build/v081/p1_peace.py build/v081/p1b_peace_hook.py build/v081/p2_peace_ramp.py build/v081/p3_peace_ui.py build/v081/p4_status_core.py build/v081/p5_status_map.py build/v081/p6_status_ui.py build/v081/p7_touchup.py build/v081/p8_migrate.py
build/v09/p1_core.py build/v09/p2_ai.py build/v09/p3_ui.py build/v09/p4_monthly.py build/v09/p5_ui2.py build/v09/p6_touch.py build/v09/p7_spare.py
build/v091/p1_wording.py build/v091/p2_tactic_params.py build/v091/p3_tactics.py build/v091/p4_peace.py build/v091/p5_migrate.py
build/v092/p1_home.py build/v092/p2_unit.py build/v092/p3_dialogs.py build/v092/p4_logs.py build/v092/p5_polish.py build/v092/p6_build.py
build/v093/p1_lots_crit.py build/v093/p2_talk.py build/v093/p3_talk_more.py build/v093/apply.sh
build/v010/p1_core.py build/v010/p2_ai.py build/v010/p3_ui.py build/v010/apply.sh
build/v0101/p1_adv.py build/v0101/p2_fsel_site.py build/v0101/p3_saves.py build/v0101/apply.sh
build/v011/p1_small.py build/v011/p2_recruit.py build/v011/p3_supply.py build/v011/p4_counsel.py build/v011/p5_zoom.py build/v011/apply.sh
    build/v012/p1_tactic.py build/v012/p2_fac.py build/v012/p3_share.py build/v012/p4_sound.py build/v012/p5_deploy.py build/v012/p6_more.py build/v012/apply.sh dev/v012_voice_plan.md
build/v0121/p1_dlcap.py build/v0121/apply.sh
build/v013/p1_duel_core.py build/v013/p2_duel_ui.py build/v013/p3_voice.py build/v013/apply.sh tools/make_voice_v013.py voice13/lines.py voice13/jobs.tsv voice13/qa.py voice13/voiceqa.py tests/duel13.js tests/d24.py tests/d25.py
build/v014/p1_dip_core.py build/v014/p2_dip_ui.py build/v014/p3_touch.py build/v014/apply.sh tests/dip14.js tests/d26.py
build/v015/p1_terrain.py build/v015/p2_terrain_ui.py build/v015/apply.sh tools/terrain15.py tests/terr15.js tests/d27.py
build/v016/p1_core16.py build/v016/p2_ui16.py build/v016/apply.sh tests/ai16.js tests/d28.py
build/v017/p1_roster17.py build/v017/apply.sh tools/roster17.py tools/por17_prompt.py tools/dl_por17.py art/por17_scenes.tsv art/por17_ids.tsv tests/roster17.js tests/d29.py tests/d30.py
build/v018/p1_tactics18.py build/v018/p2_unit18.py build/v018/p3_ui18.py build/v018/p4_title18.py build/v018/p5_fac18.py build/v018/p6_sound18.py build/v018/p7_ram18.py build/v018/p8_march18.py build/v018/p9_corps18.py build/v018/apply.sh
tools/roster18.py tools/por18_prompt.py tools/make_title18.py tools/make_audio_v018.py tools/snap_split.py art/por18_scenes.tsv art/por18_ids.tsv tests/tac18.js tests/aim18.js tests/d31.py
build/v0181/q1_back181.py build/v0181/apply.sh tests/back181.js tests/d32.py
build/v019/p1_v019.py build/v019/apply.sh tests/bio19.js tests/d33.py
build/v0191/r1_fade191.py build/v0191/apply.sh
build/v020/s1_map.py build/v020/s2_scene.py build/v020/s3_css.py build/v020/s4_ui.py build/v020/s5_flow.py build/v020/s6_staff.py build/v020/s7_duel.py build/v020/s8_fx.py build/v020/apply.sh build/v020/terrain.sh tools/add_base20.py tools/terrain20.py tests/v20.js tests/d34.py
pwa/manifest.webmanifest pwa/sw.js
tools/geo.py tools/mapgen2.py tools/bake3d.py tools/bake3d_ink.py tools/make_sprites.py tools/make_sprites_ink.py tools/make_roster.py tools/make_portraits.py tools/make_assets_ink.py
tools/build.py tools/pack_sources.py tools/fetch_art.py tools/contact.py tools/dl_por2.py tools/dl_por3.py
tools/por5_prompt.py tools/dl_por5.py tools/facebox.py tools/make_assets_v05.py tools/qa_por5.py
tools/por7_prompt.py tools/por7_plan.py tools/dl_por7.py tools/qa_por7.py tools/dl_audio7.py tools/make_audio_v07.py tools/make_audio_v012.py tools/make_icons.py
tools/add_plots.py tools/make_assets_v08.py tools/por93_prompt.py tools/dl_por93.py
tests/sim.js tests/fuzz.js tests/dist.js tests/floor.js tests/zonecheck.js tests/tac7.js tests/job8.js tests/loy8.js tests/bal8.js tests/rush8.js tests/adv9.js tests/poach9.js tests/tac91.js tests/tacuse91.js tests/exp91.js tests/peace91.js tests/tac93.js tests/corps10.js tests/corpsatk10.js tests/corpsrun10.js tests/corpsbench10.js tests/corpsreal10.js tests/adv101.js tests/tie11.js tests/sup11.js tests/cns11.js tests/fac12.js tests/regress.sh tests/browser.py
tests/d1.py tests/d2.py tests/d2b.py tests/d3.py tests/d4.py tests/d5.py tests/d6.py tests/d7.py tests/d8.py tests/d9.py tests/d10.py tests/d11.py tests/d12.py tests/d13.py tests/d14.py tests/d15.py tests/d16.py tests/d17.py tests/d18.py tests/d19.py tests/d20.py tests/d21.py tests/d22.py tests/d23.py tests/text92.py tests/shot93.py tests/shot101.py tests/shot101b.py tests/shot11.py tests/shot11b.py tests/shot11c.py tests/b9.py
art/por3_ids.tsv art/spr3_jobs.tsv art/prompts-v0.4.txt
art/por5_ids.tsv art/por5_scenes.tsv art/por5_scenes_f.tsv art/por5_scenes_pilot.tsv art/por5_focus.tsv art/prompts-v0.5.txt art/por5_progress.md
art/por7_ids.tsv art/por7_scenes.tsv art/por7_focus.tsv art/por7_ab.tsv art/por7_submit.tsv art/prompts-v0.7.txt audio7/jobs.tsv
art/por8_out/crops.tsv art/por93_ids.tsv art/por93_submit.tsv art/por93_faces_all.tsv art/por93_out/crops.tsv'''.split()
BAD = ('X-Amz-', 'Signature=', 'AWSAccessKeyId', 'Bearer ', 'cloudfront.net', 'api_key', 'secret')
parts = ['삼국지 천하도 %s — 소스 묶음. 각 파일은 "=====8<===== 경로" 줄로 시작한다. 생성물(src/assets.js, mapdata.js, map3d.js, sprites.js, roster.js, sfxdata.js, voicedata.js)은 index.html 안에 들어 있다. 음악(bgm/*.mp3)과 아이콘(pwa/icons/)은 따로 올린 파일 그대로다. 이전 판의 그림 기록(art/manifest.tsv, spr_jobs.tsv, por2_jobs.tsv)은 dev/sources-v0.3.txt 에 있다.\n' % ver]
for f in FILES:
    s = open(os.path.join(root, f), encoding='utf-8').read()
    for b in BAD:
        if b in s and f != 'tools/pack_sources.py': raise SystemExit('refusing to pack %s: contains %r' % (f, b))
    parts.append('\n=====8<===== %s\n' % f); parts.append(s if s.endswith('\n') else s + '\n')
open(out, 'w', encoding='utf-8').write(''.join(parts))
print('packed', len(FILES), 'files →', out, os.path.getsize(out), 'bytes')
