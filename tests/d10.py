# v0.6: 뒤로 가기 점검 — ×·바깥 누르기·Esc 는 '바로 전 단계'로만 간다. 화면을 실제로 눌러 가며 확인한다.
#   python3 tests/d10.py            → dist/offline.html (지금 판)
#   PAGE=../chunhado-v0.5-offline.html python3 tests/d10.py   → 예전 판에서 같은 검사가 어디서 틀리는지 본다
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser as B
B.SHOTS = os.path.join(B.ROOT, 'shots4')
RES = []
NOTE = []
TAG = 'd10old' if os.environ.get('PAGE') else 'd10'      # 예전 판으로 돌릴 때는 화면 그림을 따로 둔다
def st(pg):
    return pg.evaluate('''() => {
      var m = document.querySelector('#modal .dlg-h h2'), sh = $('sheet'), tab = sh.querySelector('.tabs button.on'), dtab = document.querySelector('#modal .tabs button.on');
      var ret = $('ret'), b = document.querySelector('#modal .dlg-b');
      return {
        modal: MODAL ? (m ? m.textContent.trim() : '?') : null,
        depth: typeof MSTACK !== 'undefined' ? MSTACK.length : -1,
        dtab: dtab ? dtab.getAttribute('data-v') : null,
        scroll: b ? Math.round(b.scrollTop) : 0,
        sheet: !SHEET ? null : (SHEET.home ? 'home' : (UI.sel ? UI.sel.kind + ':' + UI.sel.id : '?')),
        tab: tab ? tab.getAttribute('data-v') : null,
        chip: ret && ret.classList.contains('on') ? ret.textContent : null,
        target: !!UI.target, march: !!UI.march, pick: !!UI.pickMarch,
        title: !$('title').classList.contains('off')
      };
    }''')
def check(name, cond, got=None):
    RES.append((name, bool(cond)))
    print(('  ok   ' if cond else '  FAIL ') + name + ('' if cond else '  ← ' + json.dumps(got, ensure_ascii=False)))
def tap(pg, sel, nth=0, wait=280):
    loc = pg.locator(sel)
    if loc.count() <= nth or not loc.nth(nth).is_visible(): NOTE.append('없는 단추: ' + sel); return False
    loc.nth(nth).tap(); pg.wait_for_timeout(wait); return True
def X(pg): return tap(pg, '#modal .dlg-h .x')            # 맨 위 창의 ×
def SX(pg): return tap(pg, '#sheet [data-a=close]')      # 아래 창의 ×
def outside(pg):                                         # 창 바깥(어두운 곳) 누르기
    pg.touchscreen.tap(206, 14); pg.wait_for_timeout(280)
def maptap(pg, c, r, wait=350):                          # 지도의 칸을 누른다. 다른 것에 가려 있으면 onTap 을 바로 부른다(그 사실을 적어 둔다)
    x, y = B.hexpos(pg, c, r)
    el = pg.evaluate('([x, y]) => { var e = document.elementFromPoint(x, y); return e ? e.id : ""; }', [x, y])
    if el == 'map': pg.touchscreen.tap(x, y)
    else: NOTE.append('칸 (%d,%d)는 %s에 가려 onTap 으로 누름' % (c, r, el or '화면 밖')); pg.evaluate('([c, r]) => onTap(c, r)', [c, r])
    pg.wait_for_timeout(wait)
def reset(pg):
    pg.evaluate('''() => { closeDialog(); clearSel(); if (typeof clearRet === 'function') clearRet();
      var b = G.bases[baseByName("업")]; G.factions[G.player].ap = 250; b.gold = 30000; b.food = 90000; b.troops = 40000; b.w.spear = 9000; b.w.bow = 9000; b.w.horse = 9000; b.order = 90;
      baseOfficers(b).forEach(function (o) { o.acted = false; }); refreshHud(); }''')
    pg.wait_for_timeout(150)
def open_base(pg, tab=None):
    pg.evaluate('() => { var b = G.bases[baseByName("업")]; gotoBase(b); }'); pg.wait_for_timeout(700)
    if tab: tap(pg, '#sheet .tabs button[data-v=%s]' % tab)
def end_turn(pg):
    pg.evaluate('() => { UI.pspeed = 3; }'); pg.locator('#btnEnd').tap(); pg.wait_for_timeout(250)
    if not pg.evaluate('!!UI.play'): pg.locator('#btnEnd').tap()
    t0 = time.time()
    while pg.evaluate('!!UI.play') and time.time() - t0 < 180: pg.wait_for_timeout(100)
    for i in range(25):
        pg.wait_for_timeout(100)
        if pg.evaluate('!!MODAL'): break
    return time.time() - t0

def steps(pg):
    ver = pg.evaluate('GAME_VERSION'); print('판:', ver)
    # ---- 0. 타이틀 ----
    print('[타이틀]')
    tap(pg, '#tHelp'); s = st(pg); check('타이틀 → 도움말이 뜬다', s['modal'] == '도움말', s)
    X(pg); s = st(pg); check('도움말 × → 타이틀', s['modal'] is None and s['title'], s)
    tap(pg, '#tNew'); s = st(pg); check('새로 시작 → 군주 고르기', s['modal'] and '군주' in s['modal'], s)
    X(pg); s = st(pg); check('군주 고르기 × → 타이틀', s['modal'] is None and s['title'], s)
    tap(pg, '#tNew'); tap(pg, '#modal .row', 4); tap(pg, '#modal [data-a=go]', 0, 600)
    s = st(pg); check('시작 → 소개 창', s['modal'] is not None and not s['title'], s)
    X(pg); pg.wait_for_timeout(500); s = st(pg); check('소개 × → STATUS 창', s['modal'] is None and s['sheet'] == 'home', s)
    info = pg.evaluate('''() => { var b = G.bases[baseByName("업")]; return { me: G.factions[G.player].name, id: b.id, bases: facBases(G.player).map(function (x) { return x.n; }), idle: idleOfficers(b).length }; }''')
    print('  세력', info)
    reset(pg)

    # ---- 1. 무장 정보 ----
    print('[무장 정보]')
    tap(pg, '#btnList'); tap(pg, '#modal .tabs button[data-v=off]')
    pg.evaluate('() => { document.querySelector("#modal .dlg-b").scrollTop = 420; }'); pg.wait_for_timeout(150)
    y0 = st(pg)['scroll']
    idx = pg.evaluate('''() => { var rs = document.querySelectorAll('#modal .row[data-a=off]'), bb = document.querySelector('#modal .dlg-b').getBoundingClientRect();
      for (var i = 0; i < rs.length; i++) { var r = rs[i].getBoundingClientRect(); if (r.top > bb.top + 30 && r.bottom < bb.bottom - 30) return i; } return 0; }''')
    name = pg.locator('#modal .row[data-a=off] .nm').nth(idx).inner_text()
    tap(pg, '#modal .row[data-a=off]', idx); s = st(pg)
    check('목록(무장) → 무장 정보가 그 위에 뜬다', s['modal'] is not None and s['modal'] != '목록' and s['depth'] == 1, s)
    B.shot(pg, TAG + '_01_officer_over_list', 200)
    X(pg); s = st(pg)
    check('무장 정보 × → 목록으로(처음이 아니라)', s['modal'] == '목록', s)
    check('  … 무장 탭 그대로', s['dtab'] == 'off', s)
    check('  … 보던 자리 그대로(스크롤 %d)' % y0, y0 > 0 and abs(s['scroll'] - y0) <= 2, s)
    B.shot(pg, TAG + '_02_back_to_list', 200)
    tap(pg, '#modal .row[data-a=off]', idx); outside(pg); s = st(pg)
    check('무장 정보에서 바깥 누르기 → 목록으로', s['modal'] == '목록' and s['dtab'] == 'off', s)
    tap(pg, '#modal .row[data-a=off]', idx); pg.keyboard.press('Escape'); pg.wait_for_timeout(250); s = st(pg)
    check('무장 정보에서 Esc → 목록으로', s['modal'] == '목록', s)
    tap(pg, '#modal .row[data-a=off]', idx)
    r = pg.evaluate('''() => { var x = document.querySelector('#modal .dlg-h .x'); if (!x) return [null, -1]; x.click(); var row = document.querySelector('#modal .row[data-a=off]'); if (row) row.click();
      var m = document.querySelector('#modal .dlg-h h2'); return [MODAL && m ? m.textContent.trim() : null, typeof MSTACK !== 'undefined' ? MSTACK.length : -1]; }''')
    pg.wait_for_timeout(300)
    check('×를 연달아 두 번 누른 꼴(뒤의 누름이 목록의 줄에 닿음) → 목록에서 멈춤', r[0] == '목록' and r[1] == 0, r)
    X(pg); s = st(pg); check('목록 × → STATUS 창', s['modal'] is None and s['sheet'] == 'home', s)

    reset(pg); open_base(pg, 'men')
    tap(pg, '#sheet .row[data-a=off]', 1); s = st(pg); check('거점(인재) → 무장 정보', s['modal'] is not None, s)
    X(pg); s = st(pg); check('무장 정보 × → 거점 창 인재 탭 그대로', s['modal'] is None and s['sheet'] == 'base:%d' % info['id'] and s['tab'] == 'men', s)
    SX(pg); s = st(pg); check('거점 창 × → STATUS 창', s['sheet'] == 'home', s)
    tap(pg, '#sheet [data-a=lord]'); s = st(pg); check('STATUS 창 군주 초상 → 무장 정보', s['modal'] is not None, s)
    X(pg); s = st(pg); check('무장 정보 × → STATUS 창', s['modal'] is None and s['sheet'] == 'home', s)

    # ---- 2. 두 단계짜리 명령 ----
    print('[두 단계 명령]')
    reset(pg); open_base(pg, 'home')
    tap(pg, '#sheet [data-a=produce]'); s = st(pg); t1 = s['modal']; check('생산 창', s['modal'] and '생산' in s['modal'], s)
    tap(pg, '#modal .opt[data-a=k]', 0); s = st(pg); check('생산 → 창 → 담당 무장 표가 그 위에', s['modal'] and '담당 무장' in s['modal'] and s['depth'] == 1, s)
    X(pg); s = st(pg); check('담당 무장 표 × → 생산 창으로', s['modal'] == t1 and s['depth'] == 0, s)
    X(pg); s = st(pg); check('생산 창 × → 거점 창 내정 탭', s['modal'] is None and s['sheet'] == 'base:%d' % info['id'] and s['tab'] == 'home', s)
    tap(pg, '#sheet [data-a=produce]'); tap(pg, '#modal .opt[data-a=k]', 0); tap(pg, '#modal [data-a=auto]'); w0 = pg.evaluate('G.bases[baseByName("업")].w.spear')
    tap(pg, '#modal [data-a=ok]'); s = st(pg); w1 = pg.evaluate('G.bases[baseByName("업")].w.spear')
    check('생산 실행 → 창이 모두 닫히고 거점 창 (창 %d → %d)' % (w0, w1), s['modal'] is None and s['depth'] in (0, -1) and s['sheet'] == 'base:%d' % info['id'] and w1 > w0, s)

    # 명령이 안 될 때(금·행동력 부족): 창이 닫혀 버리지 않는다
    reset(pg); open_base(pg, 'home')
    tap(pg, '#sheet [data-a=produce]'); tap(pg, '#modal .opt[data-a=k]', 0); tap(pg, '#modal [data-a=auto]'); t2 = st(pg)['modal']
    pg.evaluate('() => { G.bases[baseByName("업")].gold = 0; }')
    tap(pg, '#modal [data-a=ok]'); s = st(pg); n = pg.locator('#modal .tr.sel').count(); msg = pg.evaluate('$("toast").textContent')
    check('금이 모자라 생산이 안 됨(%s) → 담당 무장 표가 그대로, 고른 %d명 그대로' % (msg, n), s['modal'] == t2 and s['depth'] == 1 and n >= 1, [s, n])
    X(pg); s = st(pg); check('  … × → 생산 창으로', s['modal'] and '무엇을 만들까요' in s['modal'], s)
    X(pg); s = st(pg); check('  … × → 거점 창', s['modal'] is None and s['sheet'] == 'base:%d' % info['id'], s)
    reset(pg); open_base(pg, 'home')
    tap(pg, '#sheet [data-a=patrol]'); tap(pg, '#modal [data-a=auto]'); t2 = st(pg)['modal']
    pg.evaluate('() => { G.factions[G.player].ap = 0; }')
    tap(pg, '#modal [data-a=ok]'); s = st(pg); msg = pg.evaluate('$("toast").textContent')
    check('행동력이 모자라 순찰이 안 됨(%s) → 표가 그대로' % msg, s['modal'] == t2, s)
    pg.evaluate('() => { G.factions[G.player].ap = 250; }'); o0 = pg.evaluate('G.bases[baseByName("업")].order')
    pg.evaluate('() => { G.bases[baseByName("업")].order = 60; }')
    tap(pg, '#modal [data-a=ok]'); s = st(pg); o1 = pg.evaluate('G.bases[baseByName("업")].order')
    check('행동력을 채우고 다시 실행 → 순찰 되고 창 닫힘 (치안 60 → %d)' % o1, s['modal'] is None and o1 > 60 and s['sheet'] == 'base:%d' % info['id'], s)

    reset(pg); open_base(pg, 'fac')
    tap(pg, '#sheet .lot[data-a=plot]', 0); s = st(pg); t1 = s['modal']; check('건설 탭 → 빈 부지 단추(v0.9.2: 번호 단추) → 무엇을 지을까요', s['modal'] and '무엇을 지을까요' in s['modal'], s)
    tap(pg, '#modal .row[data-a=f]', 0); s = st(pg); check('시설 고르기 → 담당 무장 표가 그 위에', s['modal'] and '건설' in s['modal'] and s['depth'] == 1, s)
    X(pg); s = st(pg); check('담당 무장 표 × → 시설 고르기로', s['modal'] == t1, s)
    X(pg); s = st(pg); check('시설 고르기 × → 거점 창 시설 탭', s['modal'] is None and s['sheet'] == 'base:%d' % info['id'] and s['tab'] == 'fac', s)

    mg = pg.evaluate('''() => { var b = G.bases[baseByName("업")], i, j;
      for (i = 0; i < b.plots.length; i++) for (j = 0; j < b.plots.length; j++) { if (i === j || b.plots[i].fac || b.plots[j].fac) continue;
        b.plots[i].fac = { t: 'market', lv: 1, done: true, prog: 0, need: 0, rate: 0, hp: FAC_HP }; b.plots[j].fac = { t: 'market', lv: 1, done: true, prog: 0, need: 0, rate: 0, hp: FAC_HP };      // v0.18: 조폐는 레벨이 없어 합칠 수 없다 → 시장으로
        if (mergeCandidates(b, i).length) { syncScene(); refreshSheet(); return [i, j]; }
        b.plots[i].fac = null; b.plots[j].fac = null; }
      return null; }''')
    if mg:
        tap(pg, '#sheet .row[data-a=plot][data-v="%d"]' % mg[0]); s = st(pg); t1 = s['modal']; check('시설 창(시장)', s['modal'] is not None, s)
        tap(pg, '#modal [data-a=merge]'); s = st(pg); check('흡수합병 → 담당 무장 표가 그 위에', s['modal'] and '흡수합병' in s['modal'] and s['depth'] == 1, s)
        X(pg); s = st(pg); check('담당 무장 표 × → 시설 창으로', s['modal'] == t1, s)
        X(pg); s = st(pg); check('시설 창 × → 거점 창 시설 탭', s['modal'] is None and s['tab'] == 'fac', s)
    else: NOTE.append('흡수합병: 이웃한 빈 부지 두 곳을 찾지 못해 건너뜀')

    reset(pg)
    fo = pg.evaluate('''() => { var b = G.bases[baseByName("업")], o = G.officers.filter(function (x) { return x.st === 'hidden'; })[0]; o.st = 'free'; o.loc = b.id; o.f = -1; return o.n; }''')
    open_base(pg, 'men')
    tap(pg, '#sheet [data-a=recruit]'); s = st(pg); t1 = s['modal']; check('등용 창(재야 %s)' % fo, s['modal'] and '등용' in s['modal'], s)
    tap(pg, '#modal .row[data-a=t]', 0); s = st(pg); check('대상 고르기 → 보낼 무장 표가 그 위에', s['modal'] and '누구를 보낼까요' in s['modal'] and s['depth'] == 1, s)
    X(pg); s = st(pg); check('보낼 무장 표 × → 등용 대상 창으로', s['modal'] == t1, s)
    X(pg); s = st(pg); check('등용 창 × → 거점 창 인재 탭', s['modal'] is None and s['tab'] == 'men', s)

    tap(pg, '#sheet [data-a=move]'); s = st(pg); t1 = s['modal']; check('이동 → 보낼 무장 표', s['modal'] and '보낼 무장' in s['modal'], s)
    tap(pg, '#modal .tr[data-a=pick]', 2); tap(pg, '#modal .tr[data-a=pick]', 4); tap(pg, '#modal [data-a=ok]'); s = st(pg)
    check('다음 → 목적지 창이 그 위에', s['modal'] and '어디로' in s['modal'] and s['depth'] == 1, s)
    X(pg); s = st(pg); n = pg.locator('#modal .tr.sel').count()
    check('목적지 창 × → 보낼 무장 표로, 고른 2명 그대로', s['modal'] == t1 and n == 2, [s, n])
    tap(pg, '#modal [data-a=ok]'); tap(pg, '#modal .row[data-a=d]', 0); s = st(pg)
    check('이동 실행 → 창이 모두 닫힘', s['modal'] is None and s['sheet'] == 'base:%d' % info['id'], s)

    # 거점 창의 명령을 하나씩: 창을 열고 × → 거점 창의 같은 탭
    print('[명령 창마다]')
    reset(pg); open_base(pg)
    for tabv in ['home', 'mil', 'men']:
        tap(pg, '#sheet .tabs button[data-v=%s]' % tabv)
        acts = pg.evaluate('''() => Array.prototype.map.call(document.querySelectorAll('#sheet .cmds [data-a]'), function (e) { return e.getAttribute('data-a'); })''')
        for a in acts:
            tap(pg, '#sheet .cmds [data-a=%s]' % a); s = st(pg)
            if s['modal'] is None: NOTE.append('%s: 창이 뜨지 않음 — %s' % (a, pg.evaluate('$("toast").textContent'))); continue
            ttl = s['modal']; X(pg); s = st(pg)
            check('%s 창(%s) × → 거점 창 %s 탭 그대로' % (a, ttl, tabv), s['modal'] is None and s['sheet'] == 'base:%d' % info['id'] and s['tab'] == tabv, s)

    # ---- 3. 메뉴 ----
    print('[메뉴]')
    reset(pg)
    tap(pg, '#btnMenu'); s = st(pg); t1 = s['modal']; tap(pg, '#modal [data-a=help]'); s = st(pg); check('메뉴 → 도움말이 그 위에', s['modal'] == '도움말' and s['depth'] == 1, s)
    X(pg); s = st(pg); check('도움말 × → 메뉴로', s['modal'] == t1, s)
    X(pg); s = st(pg); check('메뉴 × → 닫힘', s['modal'] is None, s)

    # ---- 4. 목록·기록에서 지도로 건너뛰기 ----
    print('[목록 → 지도]')
    reset(pg)
    tap(pg, '#btnList'); tap(pg, '#modal .tabs button[data-v=city]'); bid = int(pg.locator('#modal .row[data-a=b]').nth(1).get_attribute('data-v'))
    tap(pg, '#modal .row[data-a=b]', 1, 800); s = st(pg)
    check('목록 → 거점 줄 → 그 거점 창', s['modal'] is None and s['sheet'] == 'base:%d' % bid, s)
    check('  … 왼쪽 위에 ‹ 목록 단추', s['chip'] is not None and '목록' in s['chip'], s)
    B.shot(pg, TAG + '_03_chip', 300)
    SX(pg); s = st(pg); check('거점 창 × → 목록으로(거점 탭)', s['modal'] == '목록' and s['dtab'] == 'city', s)
    r = pg.evaluate('''() => { var row = document.querySelectorAll('#modal .row[data-a=b]')[1]; if (!row) return 'no row'; row.click(); if (!SHEET || SHEET.home) return 'no sheet';
      $('sheet').querySelector('[data-a=close]').click(); var r2 = document.querySelectorAll('#modal .row[data-a=b]')[0]; if (r2) r2.click();
      var m = document.querySelector('#modal .dlg-h h2'); return [MODAL && m ? m.textContent.trim() : null, SHEET && SHEET.home ? 'home' : 'sheet']; }''')
    pg.wait_for_timeout(700)
    check('거점 창 ×를 연달아 두 번 누른 꼴 → 목록에서 멈춤(다른 거점으로 튀지 않음)', isinstance(r, list) and r[0] == '목록' and r[1] == 'home', r)
    X(pg); s = st(pg); check('목록 × → STATUS 창, 단추 없음', s['modal'] is None and s['sheet'] == 'home' and s['chip'] is None, s)

    tap(pg, '#btnList'); tap(pg, '#modal .tabs button[data-v=fac]'); tap(pg, '#modal .row[data-a=f]', 3, 800); s = st(pg)
    check('목록 → 세력 줄 → 그 세력의 거점 창', s['modal'] is None and s['sheet'] and s['sheet'].startswith('base:'), s)
    SX(pg); s = st(pg); check('거점 창 × → 목록으로(세력 탭)', s['modal'] == '목록' and s['dtab'] == 'fac', s)
    tap(pg, '#modal .row[data-a=f]', 3, 800)
    other = pg.evaluate('() => { var b = G.bases[baseByName("업")]; jumpTo(b.c, b.r, 1.0); return [b.c, b.r]; }'); pg.wait_for_timeout(800)
    maptap(pg, other[0], other[1]); s = st(pg)
    check('건너뛴 뒤 지도에서 다른 거점을 누름 → 그 거점 창', s['sheet'] == 'base:%d' % info['id'], s)
    SX(pg); s = st(pg); check('  … 그 창 × → STATUS 창(목록 단추는 남음)', s['modal'] is None and s['sheet'] == 'home' and s['chip'] is not None, s)
    tap(pg, '#ret'); s = st(pg); check('‹ 목록 단추 → 목록으로(세력 탭)', s['modal'] == '목록' and s['dtab'] == 'fac', s)
    X(pg)

    pg.evaluate('''() => { var b = G.bases[baseByName("업")]; for (var i = 0; i < 40; i++) G.log.push({ d: dateStr(), t: '시험 기록 ' + i, c: b.c + (i % 5) - 2, r: b.r + (i % 3) - 1, imp: 1, f: G.player }); }''')
    tap(pg, '#btnLog'); pg.evaluate('() => { document.querySelector("#modal .dlg-b").scrollTop = 500; }'); pg.wait_for_timeout(150); y0 = st(pg)['scroll']
    idx = pg.evaluate('''() => { var rs = document.querySelectorAll('#modal .row[data-a=j]'), bb = document.querySelector('#modal .dlg-b').getBoundingClientRect();
      for (var i = 0; i < rs.length; i++) { var r = rs[i].getBoundingClientRect(); if (r.top > bb.top + 30 && r.bottom < bb.bottom - 30) return i; } return 0; }''')
    tap(pg, '#modal .row[data-a=j]', idx, 700); s = st(pg)
    check('기록 → 줄 → 지도, ‹ 기록 단추', s['modal'] is None and s['chip'] is not None and '기록' in s['chip'], s)
    tap(pg, '#ret'); s = st(pg); check('‹ 기록 단추 → 기록 창, 보던 자리 그대로(스크롤 %d)' % y0, s['modal'] == '기록' and y0 > 0 and abs(s['scroll'] - y0) <= 2, s)
    X(pg); s = st(pg); check('기록 × → 닫힘, 단추 없음', s['modal'] is None and s['chip'] is None, s)

    # ---- 5. 출진·부대 ----
    print('[출진·부대]')
    reset(pg); open_base(pg, 'mil')
    tap(pg, '#sheet [data-a=deploy]'); s = st(pg); check('출진 창', s['modal'] and '출진' in s['modal'], s)
    X(pg); s = st(pg); check('출진 창 × → 거점 창 군사 탭', s['modal'] is None and s['tab'] == 'mil', s)
    tap(pg, '#sheet [data-a=deploy]'); tap(pg, '#modal [data-a=auto]'); tap(pg, '#modal [data-a=next]', 0, 700); tap(pg, '#modal [data-a=ok]', 0, 2600); s = st(pg)      # v0.20: 출진은 두 단계
    check('출진 → 막 나온 부대 창', s['modal'] is None and s['sheet'] and s['sheet'].startswith('unit:'), s)
    uid = int(s['sheet'].split(':')[1]) if s['sheet'] and s['sheet'].startswith('unit:') else -1
    tap(pg, '#sheet .row[data-a=off]', 0); s = st(pg); check('부대 창 → 무장 정보', s['modal'] is not None, s)
    X(pg); s = st(pg); check('무장 정보 × → 부대 창 그대로', s['modal'] is None and s['sheet'] == 'unit:%d' % uid, s)
    SX(pg); s = st(pg); check('막 출진한 부대 창 × → 나온 성의 군사 탭', s['sheet'] == 'base:%d' % info['id'] and s['tab'] == 'mil', s)
    SX(pg); s = st(pg); check('  … 거점 창 × → STATUS 창', s['sheet'] == 'home', s)

    # v0.18: [행군] 단추가 없어졌다 — 부대를 고른 채 내 성을 누르면 그 성의 창 + [이 성으로 행군], ×는 부대 창으로
    pg.evaluate('(id) => gotoUnit(UMAP[id])', uid); pg.wait_for_timeout(700)
    check('부대 창에 [행군] 단추가 없다', pg.locator('#sheet [data-a=pickmarch]').count() == 0 and pg.locator('#sheet [data-a=undo]').count() == 1)
    own = pg.evaluate('''(id) => { var u = UMAP[id], rc = unitReach(u), bs = G.bases.filter(function (b) { return b.owner === G.player && !rc.stop[K(b.c, b.r)] && marchPath(u, K(b.c, b.r)); }).sort(function (x, y) { return hdist(u.c, u.r, x.c, x.r) - hdist(u.c, u.r, y.c, y.r); });
      if (!bs.length) return null; onTap(bs[0].c, bs[0].r); return { id: bs[0].id, n: bs[0].n }; }''', uid)
    pg.wait_for_timeout(500); s = st(pg)
    if own:
        check('부대를 고른 채 먼 내 성(%s)을 누름 → 그 성의 창 + [이 성으로 행군]' % own['n'], s['sheet'] == 'base:%d' % own['id'] and pg.locator('#sheet [data-a=marchhere]').count() == 1, s)
        B.shot(pg, TAG + '_04_march', 300)
        SX(pg); pg.wait_for_timeout(500); s = st(pg); check('그 성의 창 × → 부대 창으로', s['sheet'] == 'unit:%d' % uid, s)
    else: NOTE.append('이 성으로 행군: 닿지 않는 내 성이 없어 건너뜀')

    foe = pg.evaluate('''(id) => { var u = UMAP[id], e = G.bases.filter(function (b) { return b.kind === 'city' && b.owner >= 0 && b.owner !== G.player && idleOfficers(b).length; })[0];
      G.factions[e.owner].ap = 200; e.troops = Math.max(e.troops, 9000);
      var os = idleOfficers(e), r = cmdDeploy(e, { type: 'sword', ids: [os[0].id], troops: 3000, food: 2000 }); if (!r.ok) return r.msg;
      var ns = nbrs(u.c, u.r).filter(function (q) { var t = terr(q[0], q[1]); return inMap(q[0], q[1]) && t !== 'm' && t !== 'w' && t !== 's' && t !== 'x' && !unitAt(q[0], q[1]) && !baseAt(q[0], q[1]) && !plotAt(q[0], q[1]); });
      if (!ns.length) return 'no hex'; placeUnit(r.unit, ns[0][0], ns[0][1]); syncScene(); selectUnit(u, true); jumpTo(u.c, u.r, 1.3); return ns[0]; }''', uid)
    pg.wait_for_timeout(900)
    if isinstance(foe, list):
        maptap(pg, foe[0], foe[1]); s = st(pg); check('적 부대를 누름 → 대상 선택', s['target'] and s['sheet'] == 'unit:%d' % uid, s)
        B.shot(pg, TAG + '_05_target', 200)
        SX(pg); s = st(pg); check('대상 선택에서 × → 대상만 물리고 부대 창 그대로', (not s['target']) and s['sheet'] == 'unit:%d' % uid, s)
        SX(pg); s = st(pg); check('  … 한 번 더 × → STATUS 창', s['sheet'] == 'home', s)
    else: NOTE.append('대상 시험: 적 부대를 세우지 못함 — ' + str(foe))

    # 움직이는 동안에는 아래 창의 ×를 받지 않는다
    mv = pg.evaluate('''(id) => { var u = UMAP[id]; selectUnit(u, true); var ks = Object.keys(UI.rc.stop).filter(function (k) { return +k !== K(u.c, u.r) && !baseAt(+k % W, (+k - +k % W) / W); }); if (!ks.length) return null;
      var k = +ks[ks.length - 1], c = k % W, r = (k - c) / W; onTap(c, r); var busy = UI.busy; $('sheet').querySelector('[data-a=close]').click(); return { busy: busy, sel: UI.sel ? UI.sel.kind + ':' + UI.sel.id : null }; }''', uid)
    pg.wait_for_timeout(2000)
    if mv: check('이동 장면이 나오는 동안 × → 무시(고른 부대 그대로)', mv['busy'] and mv['sel'] == 'unit:%d' % uid, mv)
    else: NOTE.append('이동 중 × 시험: 갈 수 있는 칸이 없어 건너뜀')

    # 목록 → 부대 줄 → × → 목록
    reset(pg)
    tap(pg, '#btnList'); tap(pg, '#modal .tabs button[data-v=unit]'); tap(pg, '#modal .row[data-a=u]', 0, 800); s = st(pg)
    check('목록 → 부대 줄 → 그 부대 창', s['modal'] is None and s['sheet'] and s['sheet'].startswith('unit:'), s)
    SX(pg); s = st(pg); check('부대 창 × → 목록으로(부대 탭)', s['modal'] == '목록' and s['dtab'] == 'unit', s)
    X(pg)

    # 수송
    reset(pg); open_base(pg, 'mil')
    tap(pg, '#sheet [data-a=trans]'); s = st(pg); check('수송 창', s['modal'] and '수송' in s['modal'], s)
    # v0.22: 수송은 세 걸음(무장 → 물자 → 어디로) — [다음]을 두 번
    tap(pg, '#modal [data-a=next]', 0, 700); tap(pg, '#modal [data-a=next]', 0, 700); tap(pg, '#modal [data-a=to][data-v=x0]', 0, 400); tap(pg, '#modal [data-a=ok]', 0, 900); s = st(pg); check('수송 출발 → 수송대 창', s['modal'] is None and s['sheet'] and s['sheet'].startswith('unit:'), s)
    SX(pg); s = st(pg); check('수송대 창 × → 나온 성의 군사 탭', s['sheet'] == 'base:%d' % info['id'] and s['tab'] == 'mil', s)

    # ---- 6. 지도에서 내 부지 누르기 ----
    print('[부지]')
    reset(pg)
    pl = pg.evaluate('''() => { var b = G.bases[baseByName("업")]; selectBase(b, true); jumpTo(b.c, b.r, 1.5); for (var i = 0; i < b.plots.length; i++) if (!b.plots[i].fac && !unitAt(b.plots[i].c, b.plots[i].r)) return [b.plots[i].c, b.plots[i].r]; return null; }''')
    pg.wait_for_timeout(900)
    if pl:
        maptap(pg, pl[0], pl[1]); s = st(pg); check('거점 창을 연 채 지도에서 그 성의 빈 부지를 누름 → 시설 고르기', s['modal'] and '무엇을 지을까요' in s['modal'], s)
        X(pg); s = st(pg); check('시설 고르기 × → 거점 창 그대로(처음이 아니라)', s['modal'] is None and s['sheet'] == 'base:%d' % info['id'], s)
        us = pg.evaluate('''([c, r]) => { var u = facUnits(G.player).filter(function (x) { return !x.done; })[0]; if (!u) return null; selectUnit(u, true); return { id: u.id, reach: !!(UI.rc && UI.rc.stop[K(c, r)]) }; }''', pl)
        if us and not us['reach']:
            maptap(pg, pl[0], pl[1]); s = st(pg); check('부대를 고른 채 내 부지를 누름 → 시설 고르기', s['modal'] and '무엇을 지을까요' in s['modal'], s)
            X(pg); s = st(pg); check('시설 고르기 × → 고른 부대 그대로', s['modal'] is None and s['sheet'] == 'unit:%d' % us['id'], s)
        else: NOTE.append('부대를 고른 채 부지 누르기: 조건이 안 맞아 건너뜀 ' + str(us))

    # ---- 7. 턴 종료와 요약 ----
    print('[턴 종료]')
    reset(pg)
    tap(pg, '#btnList'); tap(pg, '#modal .row[data-a=b]', 0, 700); s = st(pg); check('(준비) 목록 단추가 떠 있음', s['chip'] is not None, s)
    pg.evaluate('() => { facUnits(G.player).forEach(function (u) { u.done = true; }); }')
    dt = end_turn(pg); s = st(pg)
    print('  턴 넘김 %.1f초 → %s' % (dt, s['modal']))
    check('턴을 넘기면 예전 단추는 사라짐', s['chip'] is None and pg.evaluate('!UI.ret'), s)
    if s['modal'] != '지난 열흘의 일':
        NOTE.append('요약 창이 뜨지 않아(조용한 턴) 시험용 요약을 띄움')
        pg.evaluate('''() => { var b = G.bases[baseByName("업")]; showReport([{ t: '시험 요약 1', imp: 2, f: G.player, c: b.c, r: b.r }, { t: '시험 요약 2', imp: 1, f: G.player, c: b.c + 2, r: b.r }]); }'''); pg.wait_for_timeout(300)
    n = pg.locator('#modal .row.rep .go').count()
    if n:
        pg.locator('#modal .row.rep:has(.go)').first.tap(); pg.wait_for_timeout(700); s = st(pg)
        check('요약 → 줄 → 지도, ‹ 지난 열흘의 일 단추', s['modal'] is None and s['chip'] is not None and '지난 열흘의 일' in s['chip'], s)
        B.shot(pg, TAG + '_06_report_chip', 300)
        tap(pg, '#ret'); s = st(pg); check('단추 → 요약 창으로', s['modal'] == '지난 열흘의 일', s)
        tap(pg, '#modal .dlg-f [data-a=close]'); s = st(pg); check('확인 → 닫힘, 단추 없음', s['modal'] is None and s['chip'] is None, s)
    else: NOTE.append('요약에 위치가 있는 줄이 없어 건너뜀')

    # ---- 8. 끝난 판 ----
    print('[끝난 판]')
    reset(pg)
    pg.evaluate('() => { G.over = "win"; showGameOver(); }'); pg.wait_for_timeout(300)
    outside(pg); s = st(pg); check('끝난 판의 창은 바깥을 눌러도 닫히지 않음', s['modal'] is not None, s)
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200); s = st(pg); check('  … Esc 로도 닫히지 않음', s['modal'] is not None, s)
    tap(pg, '#modal [data-a=t]', 0, 500); s = st(pg); check('처음으로 → 타이틀', s['modal'] is None and s['title'], s)

    ok = sum(1 for r in RES if r[1])
    print('\n결과: %d개 가운데 %d개 통과, %d개 실패' % (len(RES), ok, len(RES) - ok))
    for r in RES:
        if not r[1]: print('  실패:', r[0])
    if NOTE: print('메모:'); [print('  -', x) for x in NOTE]
    errs = [e for e in B.errors if 'GPU stall' not in e and 'WebGL' not in e and 'ERR_FILE_NOT_FOUND' not in e]   # bgm/*.mp3 는 시험 폴더에 없다(없으면 합성음으로 넘어감)
    print('콘솔 오류 %d건' % len(errs)); [print('  ', e[:300]) for e in errs[:10]]

B.run(steps, 412, 915, 1)
sys.exit(0 if all(r[1] for r in RES) and RES else 1)
