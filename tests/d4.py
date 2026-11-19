# v0.4: 턴 종료 재생에서 적의 공격·이동이 붓질 연출로 보이는지 — 내 부대 옆에 적을 세워 두고 턴을 넘기며 화면을 찍는다
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
import d2
B.SHOTS = os.path.join(B.ROOT, 'shots4')
def steps(pg):
    B.start(pg, 0)
    pg.evaluate('UI.pspeed = 2')                     # 보통
    s = pg.evaluate(d2.SETUP); print('setup', s)
    pg.wait_for_timeout(700)
    pg.evaluate('clearSel()')
    B.tapsel(pg, '#btnEnd'); pg.wait_for_timeout(150)
    if not pg.evaluate('!!UI.play'): B.tapsel(pg, '#btnEnd')
    t0 = time.time(); n = 0; caps = []; last = ''
    while pg.evaluate('!!UI.play') and time.time() - t0 < 150:
        m = pg.evaluate('$("plMsg").innerText')
        if m != last:
            last = m; caps.append('%.1fs %s' % (time.time() - t0, m.replace('\n', ' ')))
            if n < 10: pg.wait_for_timeout(260); pg.screenshot(path=os.path.join(B.SHOTS, 'd4_scene%02d.png' % n)); n += 1
        pg.wait_for_timeout(60)
    print('playback %.1fs, scenes %d' % (time.time() - t0, len(caps)))
    for c in caps[:24]: print('  ', c)
    pg.wait_for_timeout(600); pg.screenshot(path=os.path.join(B.SHOTS, 'd4_report.png'))
    print('after', pg.evaluate('[dateStr(), UI.busy, UI.anims.length, FX.live.length, Object.keys(R3.units).length, G.units.length]'))
    print('stuck sprites', pg.evaluate('Object.keys(R3.units).filter(function (id) { return R3.units[id].anim; }).length'))
    print('ERRORS', [e for e in B.errors if 'ReadPixels' not in e and 'ERR_FILE_NOT_FOUND' not in e][:8])
if __name__ == '__main__': B.run(steps, 390, 844, 2)
