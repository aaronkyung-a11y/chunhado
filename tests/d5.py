# v0.4: 재생 장면 사이의 시간을 화면 캡처 없이 잰다
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
import d2
def steps(pg):
    B.start(pg, 0)
    pg.evaluate('UI.pspeed = %s' % os.environ.get('SPD', '2'))
    s = pg.evaluate(d2.SETUP)
    pg.wait_for_timeout(500)
    pg.evaluate('''() => { window.LOGT = []; var t0 = performance.now(), _sc = setCaption; setCaption = function (f, html, cls) { LOGT.push([Math.round(performance.now() - t0), html.replace(/<[^>]+>/g, '')]); return _sc(f, html, cls); };
      var _aa = animAct; animAct = function (res, done, imp) { var a = performance.now(); LOGT.push([Math.round(a - t0), 'animAct start ' + res.kind + ' ' + (res.tac || res.ploy || '')]); return _aa(res, function () { LOGT.push([Math.round(performance.now() - t0), 'animAct end (' + Math.round(performance.now() - a) + 'ms)']); if (done) done(); }, imp); };
      var _fp = finishPlayback; finishPlayback = function () { LOGT.push([Math.round(performance.now() - t0), 'finish']); return _fp(); }; clearSel(); doEndTurn(); if (!UI.play) doEndTurn(); }''')
    t0 = time.time()
    while pg.evaluate('!!UI.play') and time.time() - t0 < 150: pg.wait_for_timeout(100)
    for r in pg.evaluate('LOGT'): print('  %6d ms  %s' % (r[0], r[1]))
    print('ERRORS', [e for e in B.errors if 'ReadPixels' not in e and 'ERR_FILE_NOT_FOUND' not in e][:8])
B.run(steps, 390, 844, 1)
