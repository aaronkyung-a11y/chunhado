# v0.3: 여러 턴 재생 — 적이 다가오고 공격하는 장면이 차례로 나오는지, 끝나면 정리가 되는지
from browser import *
import browser
browser.SHOTS = os.path.join(ROOT, 'shots3')
TURNS = int(os.environ.get('TURNS', '8'))
def steps(pg):
    start(pg, int(os.environ.get('FAC', '2')))
    pg.evaluate('UI.pspeed = %s' % os.environ.get('SPD', '2'))
    shots = 0
    for t in range(TURNS):
        pg.evaluate('if (MODAL) closeDialog(); clearSel()')
        tapsel(pg, '#btnEnd'); pg.wait_for_timeout(150)
        if not pg.evaluate('!!UI.play'): tapsel(pg, '#btnEnd')
        t0 = time.time(); seen = []; hit = False
        while pg.evaluate('!!UI.play') and time.time() - t0 < 150:
            m = pg.evaluate('[$("plFac").innerText, $("plMsg").innerText, $("plMsg").className]')
            key = m[0] + ' | ' + m[1]
            if not seen or seen[-1] != key:
                seen.append(key)
                if ('hit' in m[2] or 'big' in m[2]) and shots < 6: pg.wait_for_timeout(350); shot(pg, 'c2_scene%d' % shots, 50); shots += 1
            pg.wait_for_timeout(120)
        pg.wait_for_timeout(300)
        st = pg.evaluate('''() => ({ date: dateStr(), over: G.over, busy: UI.busy, play: !!UI.play, modal: MODAL ? document.querySelector('#modal h2') && document.querySelector('#modal h2').innerText : null, rep: REPORT.filter(function (e) { return e.imp >= 1; }).map(function (e) { return e.imp + ':' + e.t; }), stuck: Object.keys(R3.units).filter(function (id) { return R3.units[id].anim; }).length, sprites: Object.keys(R3.units).length, units: G.units.length, playing: $('app').classList.contains('playing') })''')
        print('T%d %.1fs' % (t, time.time() - t0), st['date'], 'over', st['over'], 'busy', st['busy'], 'stuck', st['stuck'], 'sprites/units', st['sprites'], st['units'], 'modal', st['modal'])
        for s in seen: print('     >', s.replace('\n', ' '))
        for r in st['rep']: print('     #', r)
        if st['over']: break
    shot(pg, 'c2_end', 300)
run(steps, 390, 844, 1)
print('ERRORS', [e for e in errors if 'ReadPixels' not in e and 'ERR_FILE_NOT_FOUND' not in e and 'ERR_FAILED' not in e][:8])
