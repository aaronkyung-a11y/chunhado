# 음악: 파일이 없을 때 만든 음악으로 넘어가는지(오디오 컨텍스트 상태·스케줄러) 확인
from browser import *
def steps(pg):
    tapsel(pg, '#tNew'); pg.wait_for_timeout(1200)
    print('title', pg.evaluate('JSON.stringify({name: BGM.name, mode: BGM.mode, dead: BGM.dead, ac: AC && AC.state, timer: !!SYN.timer, step: SYN.step})'))
    tapsel(pg, '#modal .row', 0); tapsel(pg, '#modal [data-a=go]'); pg.wait_for_timeout(600); tapsel(pg, '#modal [data-a=close]'); pg.wait_for_timeout(1500)
    print('field', pg.evaluate('JSON.stringify({name: BGM.name, mode: BGM.mode, dead: BGM.dead, ac: AC && AC.state, timer: !!SYN.timer, step: SYN.step, bufs: Object.keys(SYN.bufs).length})'))
    tapsel(pg, '#btnMenu'); tapsel(pg, '#modal [data-a=mus]'); pg.wait_for_timeout(300)
    print('off', pg.evaluate('JSON.stringify({name: BGM.name, mode: BGM.mode, timer: !!SYN.timer, music: UI.music})'))
    tapsel(pg, '#modal [data-a=mus]'); pg.wait_for_timeout(900)
    print('on', pg.evaluate('JSON.stringify({name: BGM.name, mode: BGM.mode, timer: !!SYN.timer, music: UI.music, step: SYN.step})'))
run(steps)
print('ERRORS', [e for e in errors if 'ReadPixels' not in e and 'ERR_FILE_NOT_FOUND' not in e][:12])
