from browser import *
def steps(pg):
    shot(pg, '01_title')
    start(pg, 0)
    shot(pg, '02_game', 900)
    print('cam', pg.evaluate('JSON.stringify(cam)'), 'fps test...')
    print(pg.evaluate('''() => { var t0 = performance.now(), n = 20; for (var i = 0; i < n; i++) { cam.x += 0.01; applyCam(); R3.renderer.render(R3.scene, R3.cam); } R3.renderer.getContext().finish(); return 'render ms/frame ' + ((performance.now() - t0) / n).toFixed(1) + ' | calls ' + R3.renderer.info.render.calls + ' tris ' + R3.renderer.info.render.triangles; }'''))
    pg.evaluate('cam.z = 0.45; clampCam()'); shot(pg, '03_zoom045')
    pg.evaluate('cam.z = 0.16; clampCam()'); shot(pg, '04_zoom016')
    pg.evaluate('cam.z = 1.8; clampCam()'); shot(pg, '05_zoom18')
run(steps)
print('ERRORS', errors[:12])
