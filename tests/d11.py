# v0.6: 뒤로 가기 — 마구 눌러 보기. 창·아래 창·아래 단추·지도를 무작위로 누르면서
#   (1) 오류가 나지 않는지  (2) 창 겹침 상태가 어긋나지 않는지  (3) 어디서든 ×만 거듭 누르면 STATUS 창으로 돌아오는지 본다.
#   python3 tests/d11.py <걸음 수=400> <씨앗=1> <세력=4>
import sys, os, json, random, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
STEPS = int(sys.argv[1]) if len(sys.argv) > 1 else 400
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 1
FAC = int(sys.argv[3]) if len(sys.argv) > 3 else 4
rng = random.Random(SEED)
BAD = []
STAT = {'steps': 0, 'modal_titles': {}, 'maxdepth': 0, 'chip_shown': 0, 'chip_used': 0, 'unwinds': 0, 'unwind_hist': {}, 'turns': 0, 'acts': {}, 'sret': 0, 'via': 0, 'stack_pops': 0}
CANDS = '''() => {
  var out = [];
  function vis(e) { var r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && !e.disabled; }
  if (MODAL) {
    Array.prototype.forEach.call($('modal').querySelectorAll('[data-a]'), function (e, i) { if (vis(e)) out.push(['modal', i, e.getAttribute('data-a')]); });
    out.push(['outside', 0, '']); out.push(['esc', 0, '']);
    return out;
  }
  if (SHEET) Array.prototype.forEach.call($('sheet').querySelectorAll('[data-a]'), function (e, i) { if (vis(e)) out.push(['sheet', i, e.getAttribute('data-a')]); });
  ['btnList', 'btnLog', 'btnMenu', 'btnNext'].forEach(function (id) { out.push(['bar', id, '']); });
  if ($('ret').classList.contains('on')) { out.push(['ret', 0, '']); out.push(['ret', 0, '']); }
  facBases(G.player).forEach(function (b) { out.push(['hex', [b.c, b.r], 'mybase']); b.plots.forEach(function (p) { out.push(['hex', [p.c, p.r], 'plot']); }); });
  facUnits(G.player).forEach(function (u) { out.push(['hex', [u.c, u.r], 'myunit']); });
  if (UI.rc) Object.keys(UI.rc.stop).sort().forEach(function (ks) { var k = +ks; out.push(['hex', [k % W, (k - k % W) / W], 'move']); });
  if (UI.atk) UI.atk.forEach(function (t) { out.push(['hex', [t.c, t.r], 'target']); });
  G.bases.forEach(function (b) { if (b.owner !== G.player) out.push(['hex', [b.c, b.r], 'otherbase']); });
  G.units.forEach(function (u) { if (u.f !== G.player) out.push(['hex', [u.c, u.r], 'otherunit']); });
  out.push(['esc', 0, '']);
  return out;
}'''
STATE = '''() => {
  var m = document.querySelector('#modal .dlg-h h2'), ret = $('ret');
  return { modal: MODAL ? (m ? m.textContent.trim() : '?') : null, on: $('modal').classList.contains('on'), depth: MSTACK.length, lock: !!(MODAL && MODAL.lock),
    sheet: !SHEET ? null : (SHEET.home ? 'home' : 'sel'), sel: UI.sel ? UI.sel.kind + ':' + UI.sel.id : null, chip: ret.classList.contains('on'), ret: !!UI.ret, via: !!UI.via, sret: !!UI.sret,
    target: !!UI.target, march: !!UI.march, pick: !!UI.pickMarch, busy: !!UI.busy, play: !!UI.play, over: G ? G.over : 'noG', title: !$('title').classList.contains('off') };
}'''
def settle(pg, ms=70):
    pg.wait_for_timeout(ms)
    t0 = time.time()
    while pg.evaluate('!!(UI.busy && !UI.play)') and time.time() - t0 < 8: pg.wait_for_timeout(80)
def inv(pg, where):
    s = pg.evaluate(STATE)
    def bad(msg): BAD.append('%s: %s %s' % (where, msg, json.dumps(s, ensure_ascii=False)))
    if (s['modal'] is not None) != s['on']: bad('창 표시와 상태가 다름')
    if s['modal'] is None and s['depth'] != 0: bad('창이 없는데 겹친 창이 남음')
    if s['chip'] and (not s['ret'] or s['modal'] is not None): bad('돌아가기 단추가 잘못 떠 있음')
    if s['via'] and not s['sel']: bad('via 인데 고른 것이 없음')
    if s['sret'] and not s['sel']: bad('sret 인데 고른 것이 없음')
    if not s['play'] and not s['title'] and s['over'] is None:
        if s['sel'] and s['sheet'] != 'sel': bad('고른 것이 있는데 아래 창이 STATUS')
        if not s['sel'] and s['sheet'] != 'home': bad('고른 것이 없는데 아래 창이 STATUS 가 아님')
    if (s['target'] or s['march'] or s['pick']) and not (s['sel'] or '').startswith('unit:'): bad('대상·행군 표시가 부대 없이 남음')
    STAT['maxdepth'] = max(STAT['maxdepth'], s['depth'])
    if s['modal']: STAT['modal_titles'][s['modal'].split(' — ')[0][:14]] = STAT['modal_titles'].get(s['modal'].split(' — ')[0][:14], 0) + 1
    if s['chip']: STAT['chip_shown'] += 1
    if s['sret']: STAT['sret'] += 1
    if s['via']: STAT['via'] += 1
    return s
def unwind(pg, where):
    """×만 거듭 눌러 STATUS 창까지 — 몇 번 걸리는지 센다."""
    n = 0; trace = []
    while n < 12:
        s = pg.evaluate(STATE)
        if s['over'] is not None or s['title']: return
        if s['play']:                                   # 턴이 넘어가는 중(STATUS 창의 '턴 종료'를 누른 경우)에는 끝나기를 기다린다
            t0 = time.time()
            while pg.evaluate('!!UI.play') and time.time() - t0 < 120: pg.wait_for_timeout(100)
            pg.wait_for_timeout(400); continue
        trace.append('%s|%s|d%d%s%s%s%s%s' % (s['modal'], s['sel'], s['depth'], ' tgt' if s['target'] else '', ' march' if s['march'] else '', ' pick' if s['pick'] else '', ' via' if s['via'] else '', ' sret' if s['sret'] else ''))
        if s['modal'] is None and s['sheet'] == 'home': break
        pg.evaluate('MPAINT = 0')
        if s['modal'] is not None:
            d0 = s['depth']
            ok = pg.evaluate('''() => { var x = document.querySelector('#modal .dlg-h .x') || document.querySelector('#modal [data-a=close]'); if (!x) return false; x.click(); return true; }''')
            if not ok: BAD.append('%s: ×가 없는 창 %s' % (where, s['modal'])); pg.evaluate('closeDialog()')
            s2 = pg.evaluate(STATE)
            if d0 > 0:
                STAT['stack_pops'] += 1
                if s2['depth'] != d0 - 1 or s2['modal'] is None: BAD.append('%s: 겹친 창에서 ×가 한 단계만 가지 않음 %s → %s' % (where, json.dumps(s, ensure_ascii=False), json.dumps(s2, ensure_ascii=False)))
        else:
            pg.evaluate('''() => { var x = $('sheet').querySelector('[data-a=close]'); if (x) x.click(); else clearSel(); }''')
        n += 1; settle(pg, 40); inv(pg, where + ' unwind')
    s = pg.evaluate(STATE)
    if not (s['modal'] is None and s['sheet'] == 'home') and s['over'] is None and not s['title']: BAD.append('%s: × %d번으로도 STATUS 창에 닿지 못함 %s' % (where, n, json.dumps(s, ensure_ascii=False)))
    STAT['unwinds'] += 1; STAT['unwind_hist'][n] = STAT['unwind_hist'].get(n, 0) + 1
    if n >= 5: print('  [× %d번] %s: %s' % (n, where, '  →  '.join(trace)))
def steps(pg):
    B.tapsel(pg, '#tNew'); B.tapsel(pg, '#modal .row', FAC); B.tapsel(pg, '#modal [data-a=go]'); pg.wait_for_timeout(600)
    print('세력', pg.evaluate('G.factions[G.player].name'), '| 걸음', STEPS, '| 씨앗', SEED)
    # 판의 난수를 고정하고, 부대 둘과 가까운 적 부대 하나를 미리 세워 둔다(부대 쪽 길도 밟도록)
    print('준비', pg.evaluate('''(seed) => { G.seed = seed; var b = facBases(G.player).sort(function (x, y) { return idleOfficers(y).length - idleOfficers(x).length; })[0];
      G.factions[G.player].ap = 250; b.troops = 30000; b.food = 90000; b.w.spear = 9000; b.w.bow = 9000;
      var os = idleOfficers(b).sort(function (x, y) { return aiMilScore(y) - aiMilScore(x); }), out = [];
      ['spear', 'bow'].forEach(function (t, i) { var r = cmdDeploy(b, { type: t, ids: [os[i].id], troops: 4000, food: 4000 }); out.push(r.ok ? uName(r.unit) : r.msg); });
      var e = G.bases.filter(function (x) { return x.kind === 'city' && x.owner >= 0 && x.owner !== G.player && idleOfficers(x).length; })[0], u = facUnits(G.player)[0];
      if (e && u) { G.factions[e.owner].ap = 200; e.troops = Math.max(e.troops, 9000); var r2 = cmdDeploy(e, { type: 'sword', ids: [idleOfficers(e)[0].id], troops: 3000, food: 3000 });
        if (r2.ok) { var ns = nbrs(u.c, u.r).filter(function (q) { var t = terr(q[0], q[1]); return inMap(q[0], q[1]) && t !== 'm' && t !== 'w' && t !== 's' && t !== 'x' && !unitAt(q[0], q[1]) && !baseAt(q[0], q[1]) && !plotAt(q[0], q[1]); });
          if (ns.length) { placeUnit(r2.unit, ns[0][0], ns[0][1]); out.push('적 ' + uName(r2.unit)); } } }
      syncScene(); refreshHud(); showHome(); return out; }''', SEED * 7919 + 13))
    inv(pg, 'start')
    for i in range(STEPS):
        if i % 20 == 0:        # 명령이 계속 되도록 조금씩 채워 준다
            pg.evaluate('''() => { G.factions[G.player].ap = 200; facBases(G.player).forEach(function (b) { b.gold = Math.max(b.gold, 3000); b.troops = Math.max(b.troops, 12000); b.food = Math.max(b.food, 40000); b.w.spear = Math.max(b.w.spear, 4000); baseOfficers(b).forEach(function (o) { if (Math.random() < 0.5) o.acted = false; }); }); refreshHud(); }''')
        s = pg.evaluate(STATE)
        if s['over'] is not None: print('  판이 끝남', s['over'], '걸음', i); break
        if s['title']: BAD.append('step %d: 타이틀로 나가 버림' % i); break
        if s['play']: pg.wait_for_timeout(200); continue
        if s['modal'] is None and rng.random() < 0.012 and STAT['turns'] < 3:       # 가끔 턴을 넘긴다(재생은 끔)
            pg.evaluate('() => { UI.pspeed = 0; doEndTurn(); if (!UI.play) doEndTurn(); }'); t0 = time.time()
            while pg.evaluate('!!UI.play') and time.time() - t0 < 120: pg.wait_for_timeout(100)
            pg.wait_for_timeout(500); STAT['turns'] += 1; inv(pg, 'step %d endturn' % i)
            s2 = pg.evaluate(STATE)
            if s2['chip'] or s2['ret']: BAD.append('step %d: 턴을 넘겼는데 돌아가기 단추가 남음' % i)
            continue
        cs = pg.evaluate(CANDS)
        cs = [c for c in cs if c[2] not in ('title', 'load', 't', 'spd', 'fold')]
        closes = [c for c in cs if c[2] == 'close']
        WT = {'plot': 0.12, 'move': 0.0, 'target': 4.0, 'otherbase': 0.05, 'otherunit': 0.12, 'myunit': 2.0, 'mybase': 1.0}      # 종류별 가중치(지도 칸)
        mv = [c for c in cs if c[2] == 'move']
        ws = [(WT.get(c[2], 1.0) if c[0] == 'hex' else (2.5 if c[2] in ('deploy', 'trans', 'auto', 'ok', 'pickmarch', 'viewbase', 'march', 'act', 'u', 'b', 'f', 'j', 'help', 'produce', 'recruit', 'move', 'k', 'd') else 1.0)) for c in cs]
        if mv: cs.append(rng.choice(mv)); ws.append(3.0)                    # 갈 수 있는 칸 가운데 하나
        if s['pick']: ws = [(6.0 if c[2] == 'otherbase' else w) for c, w in zip(cs, ws)]
        if any(c[0] == 'sheet' and c[2] == 'deploy' for c in cs): cs.append(['macro', 0, 'deploy3']); ws.append(2.0)
        if any(c[0] == 'sheet' and c[2] == 'trans' for c in cs): cs.append(['macro', 0, 'trans2']); ws.append(1.0)
        if closes and rng.random() < 0.18: c = rng.choice(closes)          # ×를 넉넉히 누른다
        else: c = rng.choices(cs, weights=ws, k=1)[0]
        key = c[0] + ':' + (c[2] or str(c[1]) if c[0] != 'hex' else c[2]); STAT['acts'][key] = STAT['acts'].get(key, 0) + 1
        pg.evaluate('MPAINT = 0')
        if c[0] in ('modal', 'sheet'):
            if c[0] == 'modal' and c[2] == 'close' and s['depth'] > 0: STAT['stack_pops'] += 1
            pg.evaluate('([root, i]) => { var es = Array.prototype.filter.call($(root).querySelectorAll("[data-a]"), function () { return true; }); if (!es[i]) return; if (typeof es[i].click === "function") es[i].click(); else es[i].dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true })); }', [c[0], c[1]])   # SVG 칸(나갈 자리 고리)은 .click() 이 없다 — 눌림 사건을 직접 보낸다
        elif c[0] == 'bar': pg.evaluate('(id) => $(id).click()', c[1])
        elif c[0] == 'ret': STAT['chip_used'] += 1; pg.evaluate('() => $("ret").click()')
        elif c[0] == 'outside': pg.evaluate('() => $("modal").click()')
        elif c[0] == 'esc': pg.keyboard.press('Escape')
        elif c[0] == 'hex': pg.evaluate('([c, r]) => onTap(c, r)', c[1])
        elif c[0] == 'macro':
            seq = ['#sheet [data-a=deploy]', '#modal [data-a=auto]', '#modal [data-a=ok]'] if c[2] == 'deploy3' else ['#sheet [data-a=trans]', '#modal [data-a=ok]']
            for q in seq:
                pg.evaluate('(q) => { MPAINT = 0; var e = document.querySelector(q); if (e && !e.disabled) e.click(); }', q); pg.wait_for_timeout(60)
        STAT['steps'] += 1
        settle(pg)
        inv(pg, 'step %d %s' % (i, key))
        if rng.random() < 0.07: unwind(pg, 'step %d' % i)
    unwind(pg, 'end')
    errs = [e for e in B.errors if 'GPU stall' not in e and 'ERR_FILE_NOT_FOUND' not in e]
    print('걸음 %d · 턴 넘김 %d · 가장 깊은 창 겹침 %d · 겹친 창에서 × %d번 · 돌아가기 단추 보임 %d걸음/누름 %d번 · sret %d걸음 · via %d걸음' % (STAT['steps'], STAT['turns'], STAT['maxdepth'], STAT['stack_pops'], STAT['chip_shown'], STAT['chip_used'], STAT['sret'], STAT['via']))
    print('×만 눌러 STATUS 창까지: %d번 시험, 걸린 횟수 분포 %s' % (STAT['unwinds'], json.dumps(dict(sorted(STAT['unwind_hist'].items())), ensure_ascii=False)))
    print('본 창:', json.dumps(dict(sorted(STAT['modal_titles'].items(), key=lambda x: -x[1])), ensure_ascii=False))
    print('누른 것:', json.dumps(dict(sorted(STAT['acts'].items(), key=lambda x: -x[1])[:40]), ensure_ascii=False))
    print('어긋남 %d건' % len(BAD)); [print('  ', b[:700]) for b in BAD[:12]]
    print('콘솔 오류 %d건' % len(errs)); [print('  ', e[:400]) for e in errs[:10]]
    STAT['errs'] = len(errs)
B.run(steps, 412, 915, 1)
sys.exit(0 if not BAD and not STAT.get('errs') else 1)
