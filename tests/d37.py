# v0.22 — 화면: 밀어내는 · 끄는 전법과 불도 '친 다음에' 바뀐다 (요청 10: "특기 공격을 하면 결과자리에 먼저 부대가 가 있거나 …")
#   규칙 쪽 자리는 명령을 내린 순간 이미 옮겨져 있다. 싸움터를 당겨 보이는 0.3초 동안 지도의 그림은 치기 전 자리 · 치기 전 병력에 머물러야 하고,
#   연출이 끝나면 규칙의 자리에 서며, 붙잡아 둔 것(o.keep · R3.bhold · R3.fhold)이 남지 않아야 한다.
#     격퇴(창병 — 밀어냄) · 축출(기병 — 밀어내고 따라 들어감) · 견인(극병 — 끌어당김) · 화전(노병 — 불) · 화계(계략 — 불)
#   전법은 성공해야 자리가 바뀌므로, 바라는 결과가 나올 때까지 되돌려 놓고 다시 건다(여덟 번까지).
#   python3 tests/d37.py          시계를 늦춰서 본다(d2 의 SLOWJS). 찍은 그림은 tests/shots38/
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
import d2 as D2
B.SHOTS = os.path.join(B.ROOT, 'shots38')
os.makedirs(B.SHOTS, exist_ok=True)
fails = []
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)
SETUP = D2.SETUP.replace("var mineSpec = [['spear', 0, 0], ['cav', 0, 1], ['bow', -2, 0]], foeSpec = [['spear', 1, 0], ['spear', 1, 1], ['sword', 2, -1]];",
                         "b.w.halberd = 9000; var mineSpec = [['spear', 0, 0], ['cav', 0, 1], ['bow', -1, 0], ['halberd', 0, -1]], foeSpec = [['spear', 1, 0], ['spear', 1, 1], ['sword', 1, -1]];")
assert SETUP != D2.SETUP
RESET = '''() => { var f = S.f, home = { 0: [0, 0], 1: [0, 1], 2: [-1, 0], 3: [0, -1] }, fh = { 0: [1, 0], 1: [1, 1], 2: [1, -1] }, i, u;
  for (i = 0; i < S.foe.length; i++) { u = UMAP[S.foe[i]]; if (!u) continue; u.troops = 3000; u.morale = 100; u.status = null; u.stT = 0; }
  for (i = 0; i < S.mine.length; i++) { u = UMAP[S.mine[i]]; if (!u) continue; u.troops = 4000; u.morale = 100; u.done = false; u.status = null; }
  for (var pass = 0; pass < 3; pass++) {
    for (i = 0; i < S.foe.length; i++) { u = UMAP[S.foe[i]]; if (u && (u.c !== f[0] + fh[i][0] || u.r !== f[1] + fh[i][1]) && !unitAt(f[0] + fh[i][0], f[1] + fh[i][1])) placeUnit(u, f[0] + fh[i][0], f[1] + fh[i][1]); }
    for (i = 0; i < S.mine.length; i++) { u = UMAP[S.mine[i]]; if (u && (u.c !== f[0] + home[i][0] || u.r !== f[1] + home[i][1]) && !unitAt(f[0] + home[i][0], f[1] + home[i][1])) placeUnit(u, f[0] + home[i][0], f[1] + home[i][1]); }
  }
  for (var k in G.fires) delete G.fires[k];
  clearSel(); syncScene(); requestDraw(); return G.units.length; }'''
PROBE = '''([mi, fi]) => { function P(id) { var x = R3.units[id], u = UMAP[id]; if (!x) return null; var hp = u ? hexPos(u.c, u.r) : null;
    return { p: [+x.g.position.x.toFixed(2), +x.g.position.z.toFixed(2)], rule: hp ? [+hp[0].toFixed(2), +hp[2].toFixed(2)] : null, keep: !!x.keep, anim: !!x.anim, lab: x.sig.split('|')[3] }; }
  return { a: P(S.mine[mi]), t: P(S.foe[fi]), busy: !!UI.busy, fires: Object.keys(R3.fires).length, fhold: Object.keys(R3.fhold).length, bhold: Object.keys(R3.bhold).length, gfire: Object.keys(G.fires).length,
    kept: Object.keys(R3.units).filter(function (k) { return R3.units[k].keep; }).length, toast: ($('toast').textContent || '').slice(0, 34) }; }'''
SLOW = 0.1
def steps(pg):
    B.start(pg, 0)
    ok(pg.evaluate('GAME_VERSION') == B.VER, '판 번호 ' + B.VER)
    pg.evaluate('() => { UI.pspeed = 1; uApt = function () { return "S"; }; talkHide(); UI.talk = false; }')
    s = pg.evaluate(SETUP); print('setup', s)
    ok(len(s['mine']) == 4 and len(s['foe']) == 3, '싸움터: 내 부대 넷(창 · 기 · 노 · 극) · 적 부대 셋')
    pg.evaluate('(s) => { window.S = s; }', s); pg.wait_for_timeout(700)
    pg.evaluate(D2.SLOWJS, SLOW)
    def case(name, mi, fi, actjs, want, tries=8, times=(60, 200)):
        """싸움터를 당겨 보이는 동안(늦춘 시계로 60 · 200ms)과 연출이 끝난 뒤의 모습. 바라는 결과(want)가 나올 때까지 되돌리고 다시 건다."""
        for n in range(tries):
            pg.evaluate(RESET); pg.wait_for_timeout(1500)
            p0 = pg.evaluate(PROBE, [mi, fi])
            r = pg.evaluate('''([mi, fi]) => { var u = UMAP[S.mine[mi]], t = UMAP[S.foe[fi]]; if (!u || !t) return 'gone'; selectUnit(u, true); UI.target = { kind: 'unit', u: t, c: t.c, r: t.r }; %s; return 'ok'; }''' % actjs, [mi, fi])
            last = 0; out = []
            for t in times:
                pg.wait_for_timeout(max(1, (t - last) / SLOW - 100)); last = t; out.append(pg.evaluate(PROBE, [mi, fi]))
            pg.wait_for_function('() => !UI.busy && UI.anims.length === 0 && FX.live.length === 0', timeout=180000); pg.wait_for_timeout(1500)
            fin = pg.evaluate(PROBE, [mi, fi])
            hit = r == 'ok' and bool(want(p0, out, fin))
            if hit or n == tries - 1:
                if hit: pg.screenshot(path=os.path.join(B.SHOTS, 'g_%s.png' % name))
                print('   %s — %d번째에 %s' % (name, n + 1, '바라던 결과' if hit else '끝내 바라던 결과가 나오지 않았다'))
                print('     앞  ', json.dumps(p0, ensure_ascii=False))
                for t, x in zip(times, out): print('     %3d ' % t, json.dumps(x, ensure_ascii=False))
                print('     끝  ', json.dumps(fin, ensure_ascii=False))
                return p0, out, fin, hit
    def moved(p0, out, fin): return fin['t'] and p0['t'] and fin['t']['rule'] != p0['t']['rule']
    def fire(p0, out, fin): return fin['gfire'] > 0
    def place(name, label, v, follow):
        p0, out, fin, hit = v
        ok(hit, '%s: 성공해서 자리가 바뀌었다(%s)' % (label, fin['toast']))
        if not hit: return
        ok(all(x['t']['rule'] != p0['t']['rule'] for x in out), '%s: 규칙으로는 명령을 내린 순간 이미 옮겨져 있다 %s → %s' % (label, p0['t']['rule'], out[0]['t']['rule']))
        ok(all(x['t']['p'] == p0['t']['p'] and x['a']['p'] == p0['a']['p'] and x['t']['keep'] and x['a']['keep'] for x in out), '%s: 싸움터를 당겨 보이는 동안 두 부대의 그림은 치기 전 자리에 서 있다' % label)
        ok(all(x['t']['lab'] == p0['t']['lab'] for x in out) and fin['t']['lab'] != p0['t']['lab'], '%s: 맞은 부대 이름표의 병력도 맞은 뒤에 줄어든다(%s → %s)' % (label, p0['t']['lab'], fin['t']['lab']))
        ok(fin['t']['p'] == fin['t']['rule'] and fin['a']['p'] == fin['a']['rule'] and (fin['a']['rule'] != p0['a']['rule']) == follow, '%s: 연출이 끝나면 규칙의 자리에 선다%s' % (label, ' — 친 부대도 자리를 옮겼다' if follow else ''))
        ok(fin['kept'] == 0 and fin['bhold'] == 0 and fin['fhold'] == 0 and not fin['busy'] and not fin['a']['anim'] and not fin['t']['anim'], '%s: 붙잡아 둔 것이 남지 않는다' % label)
    def flame(name, label, v):
        p0, out, fin, hit = v
        ok(hit, '%s: 불이 붙었다(%s)' % (label, fin['toast']))
        if not hit: return
        ok(all(x['gfire'] == 1 and x['fires'] == 0 and x['fhold'] == 1 for x in out), '%s: 규칙으로는 이미 불이 붙었지만 당겨 보이는 동안 지도에는 불길이 없다' % label)
        ok(fin['fires'] == 1 and fin['fhold'] == 0 and fin['kept'] == 0 and not fin['busy'], '%s: 연출이 끝나면 불길이 서고, 붙잡아 둔 것이 남지 않는다' % label)
    print('⑩ 밀어내는 전법 — 창병의 첫 전법')
    place('push', pg.evaluate('TACTICS.spear[0].name'), case('push', 0, 0, "doAct({ kind: 'tactic', tac: TACTICS.spear[0] })", moved), False)
    print('⑩ 밀어내고 따라 들어가는 전법 — 기병의 첫 전법')
    place('charge', pg.evaluate('TACTICS.cav[0].name'), case('charge', 1, 1, "doAct({ kind: 'tactic', tac: TACTICS.cav[0] })", moved), True)
    print('⑩ 끌어당기는 전법 — 극병의 첫 전법')
    place('pull', pg.evaluate('TACTICS.halberd[0].name'), case('pull', 3, 2, "doAct({ kind: 'tactic', tac: TACTICS.halberd[0] })", moved), True)
    print('⑩ 불 — 노병의 첫 전법')
    flame('hwasi', pg.evaluate('TACTICS.bow[0].name'), case('hwasi', 2, 0, "doAct({ kind: 'tactic', tac: TACTICS.bow[0] })", fire))
    print('⑩ 불 — 계략')
    flame('ploy', pg.evaluate('PLOYS[0].name'), case('ploy', 0, 0, "doAct({ kind: 'ploy', ploy: PLOYS[0] })", fire))
B.run(steps, 393, 852, 2)
errs = [e for e in B.errors if 'ReadPixels' not in e and 'ERR_FILE' not in e and 'GPU stall' not in e]
print('오류 기록:', errs[:6])
ok(not errs, '오류 · 경고 기록이 없다(%d건)' % len(errs))
print('\nd37: %d fail' % len(fails))
for f in fails: print('  ✗', f)
sys.exit(1 if fails else 0)
