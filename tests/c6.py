# v0.3: 군주 고르기·처음 안내·접힌 STATUS 창에서 거점 열기 — 화면 확인
from browser import *
import browser
browser.SHOTS = os.path.join(ROOT, 'shots3')
def steps(pg):
    tapsel(pg, '#tNew'); shot(pg, 'c6_factions', 500)
    tapsel(pg, '#modal .row', 4); tapsel(pg, '#modal [data-a=go]'); shot(pg, 'c6_intro', 900)
    tapsel(pg, '#modal [data-a=close]'); pg.wait_for_timeout(500)
    shot(pg, 'c6_home_yuanshao', 600)
    pg.evaluate('document.querySelector("#sheet .sh-body").scrollTop = 400'); shot(pg, 'c6_home_scrolled', 300)
    tapsel(pg, '#btnMenu'); shot(pg, 'c6_menu', 300); tapsel(pg, '#modal [data-a=help]'); shot(pg, 'c6_help', 300)
    pg.evaluate('closeDialog()')
    pg.evaluate('showLists("off")'); shot(pg, 'c6_list_off', 400); pg.evaluate('closeDialog()')
run(steps, 390, 844, 2)
print('ERRORS', [e for e in errors if 'ReadPixels' not in e and 'ERR_FILE_NOT_FOUND' not in e and 'ERR_FAILED' not in e][:8])
