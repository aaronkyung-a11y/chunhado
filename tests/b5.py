from browser import *
def steps(pg):
    shot(pg, '60_title', 800)
    tapsel(pg, '#tNew'); shot(pg, '61_factions')
    tapsel(pg, '#modal .row', 0); tapsel(pg, '#modal [data-a=go]'); pg.wait_for_timeout(500); shot(pg, '62_intro'); tapsel(pg, '#modal [data-a=close]')
    for i, (n, z, dy) in enumerate([('낙양', 0.62, 0), ('한중', 0.5, 4), ('건업', 0.42, 6), ('성도', 0.33, 0), ('무위', 0.5, 0), ('함곡관', 1.5, 1)]):
        pg.evaluate('([n, z, dy]) => { var b = G.bases[baseByName(n)], p = hexCenter(b.c, b.r); cam.x = p[0]; cam.y = p[1] + dy; cam.z = z; clampCam(); }', [n, z, dy])
        shot(pg, '63_view_%d' % i, 1200)
run(steps, dpr=2)
print('ERRORS', [e for e in errors if 'ReadPixels' not in e][:12])
