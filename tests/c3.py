# v0.3: 재생 건너뛰기·누르기·끄기, 행군 도착, 패망 처리, 초상 화면
from browser import *
import browser
browser.SHOTS = os.path.join(ROOT, 'shots3')
def end_turn(pg, wait=True, limit=150):
    pg.evaluate('if (MODAL) closeDialog(); clearSel()')
    tapsel(pg, '#btnEnd'); pg.wait_for_timeout(150)
    if not pg.evaluate('!!UI.play') and not pg.evaluate('!!MODAL'): tapsel(pg, '#btnEnd')
    if not wait: return 0
    t0 = time.time()
    while pg.evaluate('!!UI.play') and time.time() - t0 < limit: pg.wait_for_timeout(100)
    pg.wait_for_timeout(250); return time.time() - t0
def state(pg):
    return pg.evaluate('''() => ({ date: dateStr(), over: G.over, busy: UI.busy, play: !!UI.play, modal: MODAL ? (document.querySelector('#modal h2') || {}).innerText : null, stuck: Object.keys(R3.units).filter(function (id) { return R3.units[id].anim; }).length, sprites: Object.keys(R3.units).length, units: G.units.length, cls: $('app').className, sheet: SHEET ? (SHEET.home ? 'home' : 'other') : null, veil: $('veil').className })''')
def steps(pg):
    start(pg, 2)
    # ① 초상: 무장 정보(큰 초상) · 무장 고르기(얼굴 줄) · 목록
    tapsel(pg, '#sheet [data-a=lord]'); shot(pg, 'c3_officer', 500); pg.evaluate('closeDialog()')
    pg.evaluate('gotoBase(facBases(G.player)[0])'); pg.wait_for_timeout(500)
    tapsel(pg, '#sheet [data-a=patrol]'); tapsel(pg, '#modal [data-a=auto]'); shot(pg, 'c3_picker', 500)
    print('picker strip', pg.evaluate('document.querySelectorAll("#modal .selstrip span").length'))
    pg.evaluate('closeDialog()')
    pg.evaluate('showLists("off")'); shot(pg, 'c3_list_off', 500); pg.evaluate('showLists("fac")'); shot(pg, 'c3_list_fac', 500); pg.evaluate('closeDialog()')
    # ② 재생 끄기: 바로 요약
    pg.evaluate('UI.pspeed = 0')
    dt = end_turn(pg); print('speed0 turn %.1fs' % dt, state(pg))
    # ③ 빠르게 두 턴 넘겨 적을 끌어들인 뒤, 느리게 재생하다가 화면 누르기·건너뛰기
    pg.evaluate('UI.pspeed = 0'); end_turn(pg); end_turn(pg)
    pg.evaluate('UI.pspeed = 1')
    end_turn(pg, wait=False); pg.wait_for_timeout(900)
    caps = []
    for i in range(2):
        caps.append(pg.evaluate('$("plMsg").innerText')); pg.touchscreen.tap(195, 300); pg.wait_for_timeout(260)
    print('nudge captions', caps)
    shot(pg, 'c3_play_mid', 100)
    print('before skip', pg.evaluate('[!!UI.play, UI.play && UI.play.skip]'))
    if pg.evaluate('!!UI.play'): tapsel(pg, '#plSkip')
    pg.wait_for_timeout(700)
    print('after skip', state(pg))
    # ④ 속도 버튼
    pg.evaluate('if (MODAL) closeDialog()')
    end_turn(pg, wait=False); pg.wait_for_timeout(400)
    b0 = pg.evaluate('$("plSpeed").innerText'); tapsel(pg, '#plSpeed'); b1 = pg.evaluate('$("plSpeed").innerText'); print('speed button', b0, '->', b1, 'pspeed', pg.evaluate('UI.pspeed'))
    if pg.evaluate('!!UI.play'): tapsel(pg, '#plSkip')
    pg.wait_for_timeout(700); print('state', state(pg))
    # ⑤ 패망: 소패를 거의 빈 성으로 만들고 턴을 넘긴다
    pg.evaluate('if (MODAL) closeDialog(); var b = facBases(G.player)[0]; b.troops = 100; b.dur = 40; UI.pspeed = 2;')
    for i in range(4):
        dt = end_turn(pg); st = state(pg); print('lose-turn %d %.1fs' % (i, dt), st)
        if st['over']: break
    shot(pg, 'c3_over', 400)
run(steps, 390, 844, 2)
print('ERRORS', [e for e in errors if 'ReadPixels' not in e and 'ERR_FILE_NOT_FOUND' not in e and 'ERR_FAILED' not in e][:8])
