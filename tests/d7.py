# v0.8: 성역에서 멈추지 않는다 / 출진한 턴에는 거점을 칠 수 없다 — 화면 조작으로 확인
#  (v0.4~v0.7 의 이 시험은 '성역에 막 들어선 부대는 그 턴에 그 성을 칠 수 없다'를 봤다. 그 규칙은 없어졌다)
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
from browser import taphex, tapsel
B.SHOTS = os.path.join(B.ROOT, 'shots4')
fails = []
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)
def steps(pg):
    B.start(pg, 0)
    info = pg.evaluate('''(() => {
      var b = G.bases[baseByName("진류")], t = G.bases[baseByName("복양")];
      G.factions[G.player].ap = 200; b.troops = 20000; b.w.bow = 9000; b.food = 30000;
      var os = idleOfficers(b).sort((x, y) => aiMilScore(y) - aiMilScore(x));
      var u = cmdDeploy(b, {type: "bow", ids: [os[0].id], troops: 4000, food: 3000}).unit;
      function free(c, r) { var t2 = terr(c, r); return t2 !== "m" && t2 !== "w" && t2 !== "s" && t2 !== "x" && !unitAt(c, r) && !facAt(c, r) && !baseAt(c, r); }
      // 복양에서 4칸 떨어진(성역 밖) 빈 칸 가운데, 성역 안 2칸째 칸까지 평지로 이어진 곳
      var best = null;
      for (var c = t.c - 5; c <= t.c + 5 && !best; c++) for (var r = t.r - 5; r <= t.r + 5 && !best; r++) {
        if (!inMap(c, r) || hdist(c, r, t.c, t.r) !== 4 || !free(c, r) || zoneAt(c, r) >= 0) continue;
        placeUnit(u, c, r); u.mp = uMaxMp(u);
        var rc = unitReach(u), inn = null;
        for (var k in rc.stop) { k = +k; var cc = k % W, rr = (k - cc) / W; if (hdist(cc, rr, t.c, t.r) === 2 && zoneAt(cc, rr) === t.id && !plotAt(cc, rr) && rc.cost[k] <= u.mp - 3) { inn = [cc, rr, rc.cost[k]]; break; } }
        if (inn) best = { out: [c, r], inn: inn };
      }
      placeUnit(u, best.out[0], best.out[1]); u.mp = uMaxMp(u); u.done = false; u.moved = false; u.ox = -1; u.morale = 90;
      syncScene(); requestDraw(); refreshHud();
      return { id: u.id, out: best.out, inn: [best.inn[0], best.inn[1]], cost: best.inn[2], mp: u.mp, t: [t.c, t.r], tid: t.id, tn: t.n, range: uRange(u), born: u.born, turn: G.turn, troops: t.troops };
    })()''')
    print('staged', info)
    pg.evaluate('(id) => gotoUnit(UMAP[id])', info['id']); pg.wait_for_timeout(700)
    ok(info['born'] == info['turn'], '막 출진한 부대(born = 이번 턴)')
    ok(pg.evaluate('([c, r]) => !!(UI.rc && UI.rc.stop[K(c, r)])', info['inn']), '성역 밖 4칸에서 성역 안 2칸째 칸이 파랗게 보인다')
    taphex(pg, *info['inn']); pg.wait_for_timeout(1700)
    st = pg.evaluate('(tid) => { var u = selUnit(); return { pos: [u.c, u.r], mp: u.mp, d: hdist(u.c, u.r, G.bases[tid].c, G.bases[tid].r), zone: zoneAt(u.c, u.r), reach: Object.keys(UI.rc.stop).length, baseTarget: attackTargets(u).some(function (x) { return x.kind === "base"; }), toast: $("toast").textContent }; }', info['tid'])
    print('entered zone', st)
    ok(st['zone'] == info['tid'] and st['d'] == 2, '성역 안으로 들어섰다(성에서 2칸)')
    ok(st['mp'] == info['mp'] - info['cost'] and st['mp'] > 0, '성역의 경계를 넘어도 이동력이 남는다 (%s − %s = %s)' % (info['mp'], info['cost'], st['mp']))
    ok(st['reach'] > 0, '그 턴에 더 움직일 수 있다(갈 수 있는 칸 %d)' % st['reach'])
    ok('성역' not in st['toast'] and '여기까지' not in st['toast'], '멈췄다는 안내가 뜨지 않는다 [%s]' % st['toast'])
    ok(not st['baseTarget'], '출진한 턴에는 성이 공격 대상에 없다')
    B.shot(pg, 'd7_1_entered', 200)
    taphex(pg, *info['t']); pg.wait_for_timeout(400)
    toast = pg.evaluate('$("toast").textContent')
    ok(pg.evaluate('!(UI.target && UI.target.kind)') and '출진한 턴' in toast, '성을 누르면 안내만 뜬다 [%s]' % toast)
    r = pg.evaluate('(tid) => { var u = selUnit(), b = G.bases[tid], res = unitAttack(u, { kind: "base", b: b, c: b.c, r: b.r }); return [res.ok, res.msg, u.done]; }', info['tid'])
    ok(r[0] is False and r[2] is False, '규칙 쪽에서도 거절하고 행동을 쓰지 않는다 [%s]' % r[1])
    # 앞서 나온 부대라면(다음 턴부터) 바로 칠 수 있다
    pg.evaluate('(id) => { UMAP[id].born = -1; UI.atk = allTargets(UMAP[id]); refreshSheet(); requestDraw(); }', info['id']); pg.wait_for_timeout(300)
    taphex(pg, *info['t']); pg.wait_for_timeout(500)
    acts = [pg.locator('#sheet [data-a=act]').nth(i).inner_text().replace('\n', ' / ') for i in range(pg.locator('#sheet [data-a=act]').count())]
    print('acts', acts)
    ok(len(acts) >= 1 and '공격' in acts[0] and '다음 턴' not in acts[0], '출진한 턴이 아니면 성역에 들어선 그 턴에 성을 칠 수 있다 %s' % acts[:1])
    tapsel(pg, '#sheet [data-a=act]', 0); pg.wait_for_timeout(3200)
    after = pg.evaluate('(tid) => [G.bases[tid].troops, G.bases[tid].dur, $("toast").textContent]', info['tid'])
    ok(after[0] < info['troops'], '실제로 공격이 들어갔다 (복양 병력 %s → %s) [%s]' % (info['troops'], after[0], after[2]))
    B.shot(pg, 'd7_2_attacked', 200)
B.run(steps)
errs = [e for e in B.errors if 'GPU stall' not in e and 'ERR_FILE_NOT_FOUND' not in e]
ok(not errs, '콘솔 오류 없음 %s' % errs[:3])
print('\n검사 %d개 가운데 실패 %d' % (len(fails) + sum(1 for _ in []) , len(fails)) if fails else '\n모두 합격')
sys.exit(1 if fails else 0)
