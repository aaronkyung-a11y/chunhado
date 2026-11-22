# v0.4: 전투 연출 — 근접 공격, 화살, 전법(축출·밀어내기), 계략(화계), 성 공격, 궤멸을 차례로 걸어 보고 도중 화면을 찍는다
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
B.SHOTS = os.path.join(B.ROOT, 'shots4')
SETUP = '''() => {
  function field() {
    for (var r = 92; r < 112; r++) for (var c = 146; c < 168; c++) {
      var ok = true;
      for (var dr = -2; dr <= 2 && ok; dr++) for (var dc = -3; dc <= 3 && ok; dc++) { var k = K(c + dc, r + dr); if (TCH[k] !== 112 || ZONE[k] >= 0 || BAT[k] !== undefined || PAT[k] || UAT[k]) ok = false; }
      if (ok) return [c, r];
    }
    return null;
  }
  var f = field(), b = facBases(G.player)[0], eb = G.bases[baseByName('복양')], out = { f: f, mine: [], foe: [] };
  b.w.spear = 9000; b.w.horse = 9000; b.w.bow = 9000; b.troops = 30000; b.food = 90000; G.factions[G.player].ap = 250;
  eb.troops = 30000; eb.w.spear = 9000; eb.food = 90000; G.factions[eb.owner].ap = 250;
  var mineSpec = [['spear', 0, 0], ['cav', 0, 1], ['bow', -2, 0]], foeSpec = [['spear', 1, 0], ['spear', 1, 1], ['sword', 2, -1]];
  mineSpec.forEach(function (s) {
    var ids = autoTeam(b, s[0], 4000); if (!ids.length) ids = [idleOfficers(b)[0].id];
    var r = cmdDeploy(b, { type: s[0], ids: ids.slice(0, 1), troops: 4000, food: 4000 });
    if (!r.ok) { out.err = r.msg; return; }
    placeUnit(r.unit, f[0] + s[1], f[1] + s[2]); r.unit.mp = uMaxMp(r.unit); r.unit.done = false; r.unit.morale = 100; out.mine.push(r.unit.id);
  });
  foeSpec.forEach(function (s, i) {
    var os = idleOfficers(eb); if (!os.length) return;
    var r = cmdDeploy(eb, { type: s[0], ids: [os[0].id], troops: i === 2 ? 300 : 3000, food: 3000 });
    if (!r.ok) { out.err2 = r.msg; return; }
    placeUnit(r.unit, f[0] + s[1], f[1] + s[2]); out.foe.push(r.unit.id);
  });
  EVQ.length = 0; clearSel(); syncScene(); jumpTo(f[0], f[1], 1.5); requestDraw();
  return out;
}'''
SLOW = 0.08
SLOWJS = """(k) => { if (window.__slowed) return; window.__slowed = true;
  var A = performance.now(), _now = performance.now.bind(performance), _raf = window.requestAnimationFrame.bind(window);
  performance.now = function () { return A + (_now() - A) * k; };
  window.requestAnimationFrame = function (cb) { return _raf(function (ts) { cb(A + (ts - A) * k); }); }; }"""
def frames(pg, name, js, times=(90, 230, 420, 700), settle=1500):
    pg.evaluate(SLOWJS, SLOW)                      # 게임 시계를 늦춰서 연출 도중을 찍는다
    pg.evaluate(js)
    last = 0
    for i, t in enumerate(times):
        pg.wait_for_timeout(max(1, (t - last) / SLOW - 350)); last = t
        pg.screenshot(path=os.path.join(B.SHOTS, '%s_%d.png' % (name, i)))
    pg.wait_for_timeout(settle / SLOW)
    print(name, 'busy', pg.evaluate('UI.busy'), 'toast:', pg.evaluate('$("toast").textContent'), 'anims', pg.evaluate('UI.anims.length'), 'fx', pg.evaluate('FX.live.length'))
def act(mi, fi, kind):
    extra = {'attack': "{ kind: 'attack' }", 'dolgyeok': "{ kind: 'tactic', tac: TACTICS.cav[0] }", 'fire': "{ kind: 'ploy', ploy: PLOYS[0] }", 'hwasi': "{ kind: 'tactic', tac: TACTICS.bow[0] }", 'dolchul': "{ kind: 'tactic', tac: TACTICS.spear[0] }"}[kind]
    return '''() => { var u = UMAP[S.mine[%d]], t = UMAP[S.foe[%d]]; if (!u || !t) return 'gone'; u.done = false; u.morale = 100; selectUnit(u, true); UI.target = { kind: 'unit', u: t, c: t.c, r: t.r }; doAct(%s); return 'ok'; }''' % (mi, fi, extra)
def steps(pg):
    B.start(pg, 0)
    pg.evaluate('UI.pspeed = 1')
    s = pg.evaluate(SETUP); print('setup', s)
    pg.evaluate('(s) => { window.S = s; }', s)
    pg.wait_for_timeout(900); B.shot(pg, 'd2_00_field', 300)
    frames(pg, 'd2_1melee', act(0, 0, 'attack'))
    frames(pg, 'd2_2bow', act(2, 0, 'attack'), (120, 300, 480, 760))
    frames(pg, 'd2_3charge', act(1, 1, 'dolgyeok'), (120, 320, 520, 800))
    frames(pg, 'd2_4thrust', act(0, 0, 'dolchul'), (120, 320, 520, 800))
    frames(pg, 'd2_5fire', act(2, 0, 'fire'), (150, 380, 560, 800))
    frames(pg, 'd2_6firearrow', act(2, 1, 'hwasi'), (150, 380, 600, 900))
    # 약한 부대를 쳐서 궤멸시킨다
    pg.evaluate('''() => { var u = UMAP[S.mine[0]], t = UMAP[S.foe[2]]; if (u && t) { placeUnit(u, t.c - 1, t.r); u.done = false; syncScene(); } }''')
    pg.wait_for_timeout(400)
    frames(pg, 'd2_7kill', act(0, 2, 'attack'), (150, 420, 760, 1100))
    print('units left', pg.evaluate('[S.mine.map(function (i) { return UMAP[i] ? UMAP[i].troops : 0; }), S.foe.map(function (i) { return UMAP[i] ? UMAP[i].troops : 0; })]'))
    print('scene objs', pg.evaluate('Object.keys(R3.units).length'), 'G.units', pg.evaluate('G.units.length'))
    print('ERRORS', [e for e in B.errors if 'ReadPixels' not in e and 'ERR_FILE_NOT_FOUND' not in e][:8])
if __name__ == "__main__": B.run(steps, 390, 844, 2)
