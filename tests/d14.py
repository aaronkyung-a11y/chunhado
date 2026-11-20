# 지도 가장자리 (v0.8)
#  ① 끝까지 끌었을 때 가려지지 않은 지도 영역에서 '지도 밖'이 차지하는 비율 — 확대 6단계 × 아래 창 펼침/접음 × 8방향
#  ② 모든 거점을 화면에 둘 수 있나 (확대 0.5 / 0.9 / 1.6)
#  ③ 지도 맨 끝 칸도 화면에 둘 수 있나
#  ④ 아래 창을 여닫으면 한도가 바뀐다 → 손대지 않아도 제자리로 오나
#  ⑤ 지도 밖 띠가 실제로 그려지나(땅 그물이 지도보다 넓다), 지도 안의 땅 높이는 그대로인가
# python3 tests/d14.py          → 지금 판 (합격/불합격)
# PAGE=../chunhado-v0.7-offline.html python3 tests/d14.py old   → 예전 판의 ①만 재서 견준다(합격 판정 없음)
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
OLD = len(sys.argv) > 1 and sys.argv[1] == 'old'
fails = []; out = {}
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)
MEASURE = '''() => {
  var sa = safeArea(), n = 0, off = 0, far = 0, A = (typeof APRON === 'number') ? APRON : 0;
  for (var j = 0; j < 11; j++) for (var i = 0; i < 11; i++) {
    var sx = (i + 0.5) / 11 * CW, sy = sa.top + (j + 0.5) / 11 * (sa.bottom - sa.top), h = planeHit(sx, sy, 0);
    n++;
    if (!h) { off++; far++; continue; }
    var dx = Math.max(-h[0], h[0] - MAP3D.WX, 0), dz = Math.max(-h[1], h[1] - MAP3D.WZ, 0), od = Math.sqrt(dx * dx + dz * dz);
    if (od > 0) off++;
    if (od > Math.max(A, 0.01)) far++;
  }
  return [off / n, far / n];
}'''
DIRS = [('북', 0, -1), ('남', 0, 1), ('서', -1, 0), ('동', 1, 0), ('북서', -1, -1), ('북동', 1, -1), ('남서', -1, 1), ('남동', 1, 1)]
ZOOMS = [0.14, 0.3, 0.5, 0.8, 1.2, 2.3]
def push(pg, z, dx, dz):
    pg.evaluate('''([z, dx, dz]) => { cam.z = z; cam.x = dx ? (dx < 0 ? -999 : 9999) : MAP3D.WX / 2; cam.y = dz ? (dz < 0 ? -999 : 9999) : MAP3D.WZ / 2; clampCam(); applyCam(); }''', [z, dx, dz])
def fold(pg, want_open):
    cur = pg.evaluate('() => HOME.open')
    if cur != want_open: B.tapsel(pg, '#sheet [data-a=fold]'); pg.wait_for_timeout(500)
def steps(pg):
    B.start(pg, 0)
    pg.evaluate('() => { clearSel(); }')
    # ① 지도 밖이 차지하는 비율
    table = {}
    for st in (True, False):
        fold(pg, st)
        for z in ZOOMS:
            worst = (0, 0, ''); edge = (0, 0, '')
            for name, dx, dz in DIRS:
                push(pg, z, dx, dz)
                m = pg.evaluate(MEASURE)
                if m[0] > worst[0]: worst = (m[0], m[1], name)
                if not (dx and dz) and m[0] > edge[0]: edge = (m[0], m[1], name)
            table[('펼침' if st else '접음') + ' z=' + str(z)] = {'side': round(edge[0], 3), 'side_dir': edge[2], 'corner': round(worst[0], 3), 'corner_dir': worst[2], 'blank': round(worst[1], 3)}
    out['offmap'] = table
    print('① 끝까지 끌었을 때 가려지지 않은 지도 영역 가운데 지도 밖의 비율 (변 / 모서리 / 그중 그림이 다 풀린 빈 종이)')
    for k in table: print('   %-12s 변 %4.0f%% (%s)  모서리 %4.0f%% (%s)  빈 종이 %4.0f%%' % (k, table[k]['side'] * 100, table[k]['side_dir'], table[k]['corner'] * 100, table[k]['corner_dir'], table[k]['blank'] * 100))
    if OLD: return
    ok(max(v['side'] for v in table.values()) <= 0.30, '변 쪽으로 끝까지 끌어도 지도 밖은 30%% 이하 (최대 %.0f%%)' % (100 * max(v['side'] for v in table.values())))
    ok(max(v['corner'] for v in table.values()) <= 0.52, '모서리로 끝까지 끌어도 지도 밖은 52%% 이하 (최대 %.0f%%)' % (100 * max(v['corner'] for v in table.values())))
    # ② 모든 거점
    bases = pg.evaluate('() => G.bases.map(function (b) { return [b.id, b.name, b.c, b.r]; })')
    bad = []
    for st in (True, False):
        fold(pg, st)
        for z in (0.5, 0.9, 1.6):
            for b in bases:
                pg.evaluate('([c, r, z]) => { jumpTo(c, r, z, 0, 1); }', [b[2], b[3], z]); pg.wait_for_timeout(40)
                pg.evaluate('() => { applyCam(); }')
                if not pg.evaluate('([c, r]) => onScreen(c, r, 0)', [b[2], b[3]]): bad.append((b[1], z, st))
    out['bases'] = len(bases); out['bases_bad'] = bad
    ok(not bad, '거점 %d곳 × 확대 3단계 × 창 펼침/접음 — 모두 화면(가려지지 않은 영역)에 둘 수 있다 %s' % (len(bases), bad[:5]))
    # ③ 맨 끝 칸
    W, H = pg.evaluate('() => [W, H]')
    spots = [(0, 0), (W - 1, 0), (0, H - 1), (W - 1, H - 1), (W // 2, 0), (W // 2, H - 1), (0, H // 2), (W - 1, H // 2), (0, 1), (W - 1, 1), (1, H - 1)]
    bad = []
    for st in (True, False):
        fold(pg, st)
        for z in (0.5, 1.2, 2.3):
            for c, r in spots:
                pg.evaluate('([c, r, z]) => { jumpTo(c, r, z, 0, 1); }', [c, r, z]); pg.wait_for_timeout(40)
                pg.evaluate('() => { applyCam(); }')
                if not pg.evaluate('([c, r]) => onScreen(c, r, 0)', [c, r]): bad.append((c, r, z, st))
    out['edge_hex_bad'] = bad
    ok(not bad, '맨 끝 칸 %d곳 × 확대 3단계 × 창 펼침/접음 — 모두 화면에 둘 수 있다 %s' % (len(spots), bad[:5]))
    # 끝 칸을 눌러 고를 수 있나(땅 찍기)
    fold(pg, True)
    pg.evaluate('([c, r]) => { jumpTo(c, r, 1.2, 0, 1); }', [0, H // 2]); pg.wait_for_timeout(80); pg.evaluate('() => applyCam()')
    hit = pg.evaluate('([c, r]) => { var p = hexPos(c, r), s = w2s(p[0], p[1], p[2]); return pickAt(s[0], s[1]); }', [0, H // 2])
    ok(hit == [0, H // 2], '서쪽 끝 칸을 누르면 그 칸이 잡힌다 %s' % hit)
    # ④ 아래 창을 접으면(남쪽 끝) 제자리로
    fold(pg, True)
    push(pg, 0.5, 0, 1)
    y_open = pg.evaluate('() => cam.y')
    fold(pg, False); pg.wait_for_timeout(700)
    y_fold = pg.evaluate('() => cam.y'); lim = pg.evaluate('() => camLimits().y1')
    ok(y_fold < y_open - 5 and abs(y_fold - lim) < 0.05, '남쪽 끝에서 아래 창을 접으면 손대지 않아도 지도가 제자리로 온다 (바라보는 점 %.1f → %.1f, 한도 %.1f)' % (y_open, y_fold, lim))
    m = pg.evaluate(MEASURE)
    ok(m[0] <= 0.30, '그 뒤 지도 밖 비율 %.0f%%' % (m[0] * 100))
    fold(pg, True); pg.wait_for_timeout(700)
    # 북쪽 끝: 창을 접으면 한도가 느슨해질 뿐(더 북쪽까지 볼 수 있다) 지도는 그대로. 거기서 더 북으로 간 뒤 창을 펴면 한도가 죄어지고 지도가 따라온다
    push(pg, 0.5, 0, -1)
    y_a = pg.evaluate('() => cam.y'); L_a = pg.evaluate('() => camLimits().y0')
    fold(pg, False); pg.wait_for_timeout(700)
    y_b = pg.evaluate('() => cam.y'); L_b = pg.evaluate('() => camLimits().y0')
    ok(L_b < L_a - 1 and abs(y_b - y_a) < 0.05, '북쪽 끝에서 창을 접으면 한도만 느슨해지고(%.1f → %.1f) 지도는 그대로 (%.2f)' % (L_a, L_b, y_b))
    push(pg, 0.5, 0, -1)
    fold(pg, True); pg.wait_for_timeout(700)
    y_c = pg.evaluate('() => cam.y'); L_c = pg.evaluate('() => camLimits().y0')
    ok(abs(y_c - L_c) < 0.05 and y_c > L_b + 1, '거기서 더 북으로 간 뒤 창을 펴면 지도가 따라온다 (%.1f → %.1f)' % (L_b, y_c))
    # ⑤ 지도 밖 띠와 높이
    info = pg.evaluate('''() => {
      var minx = 1e9, maxx = -1e9, minz = 1e9, maxz = -1e9, n = 0;
      R3.scene.traverse(function (o) { if (o.isMesh && o.material === R3.tmat) { n++; o.geometry.computeBoundingBox(); var b = o.geometry.boundingBox; minx = Math.min(minx, b.min.x); maxx = Math.max(maxx, b.max.x); minz = Math.min(minz, b.min.z); maxz = Math.max(maxz, b.max.z); } });
      var bin = atob(MAP3D.hm), k = (MAP3D.hmax - MAP3D.hmin) / 65535, bad = 0, GX = MAP3D.GX, GZ = MAP3D.GZ;
      for (var i = 0; i < GX * GZ; i++) { var h = MAP3D.hmin + (bin.charCodeAt(2 * i) | (bin.charCodeAt(2 * i + 1) << 8)) * k; if (Math.abs(h - HMAP[i]) > 1e-4) bad++; }
      return { n: n, minx: minx, maxx: maxx, minz: minz, maxz: maxz, apron: APRON, hbad: bad, y_out: apronY(-APRON - 1, 100), y_in: apronY(50, 100) - groundY(50, 100), base: MAP3D.hmin - 0.05, trees: R3.trees.length };
    }''')
    out['mesh'] = info
    ok(info['minx'] <= -info['apron'] and info['maxx'] >= 381.9 + info['apron'] and info['minz'] <= -info['apron'] and info['maxz'] >= 324.5 + info['apron'], '땅 그물이 지도 밖 %s 만큼 더 넓다 (x %.1f~%.1f, z %.1f~%.1f, %d조각)' % (info['apron'], info['minx'], info['maxx'], info['minz'], info['maxz'], info['n']))
    ok(info['hbad'] == 0 and abs(info['y_in']) < 1e-9, '지도 안의 땅 높이는 그대로 (달라진 점 %d)' % info['hbad'])
    ok(abs(info['y_out'] - info['base']) < 1e-6, '띠의 바깥 끝은 바닥 높이 (%.3f)' % info['y_out'])
    B.shot(pg, 'd14_end')
B.SHOTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shots14'); os.makedirs(B.SHOTS, exist_ok=True)
B.run(steps, 412, 915)
errs = [e for e in B.errors if 'GPU stall' not in e and 'ERR_FILE_NOT_FOUND' not in e]
if not OLD: ok(not errs, '콘솔 오류 없음 %s' % errs[:3])
json.dump(out, open(os.path.join(B.SHOTS, 'old.json' if OLD else 'now.json'), 'w'), ensure_ascii=False, indent=1)
print('\n' + ('(예전 판 — 수치만)' if OLD else ('불합격 %d' % len(fails) if fails else '모두 합격')))
sys.exit(1 if fails else 0)
