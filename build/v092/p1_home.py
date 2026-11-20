# v0.9.2 글 덜어내기(1/…): STATUS 창 — "전반적으로 텍스트가 너무 많아서 보기가 어려운 게 많다. 거점, 부대.. 뭐 이런 버튼들도 어디에 쓰는지 모르겠고.." (2026-11-20 17:11)
#  STATUS 창에서 뺀 것
#   - 거점·부대·무장·천하 네 칸: 아래 '목록' 단추와 같은 창을 여는 지름길이었다(숫자판처럼 보여 단추인지도 알기 어려웠다). 목록은 아래 단추 하나로
#   - 날짜 · 행동력 · 금/병량/병력: 화면 맨 위 띠에 이미 있다. 수입(월·분기)만 한 줄로 남긴다
#   - '군주 유비' 딱지(초상이 군주다), 군사 단추의 한자와 지력
#   - 지금 할 일의 '초반 보호' 줄: 이름 옆의 표(누르면 풀이)로 충분하다
#   - 지금 할 일의 설명 문장: 줄마다 제목 한 줄 + (있으면) 짧은 자료 한 줄. 두 줄 다 줄바꿈하지 않는다
#   - 할 일이 남아 있을 때의 '턴 종료' 줄(아래에 턴 종료 단추가 늘 있다). 다 마쳤을 때만 한 줄
#  거점 창의 '군사' 탭 → '출진': STATUS 창의 군사(軍師)와 같은 소리라 한자를 붙여 가르던 것을, 탭 이름을 바꿔 없앤다
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)
p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()

# ---- 지금 할 일 ----
a = s[s.index("  if (peaceLeft() > 0) {\n    var pl = peaceLeft(), pb = peaceBroken();"):s.index("  bs.forEach(function (b) {\n    var es = enemyUnitsNear(f, b.c, b.r, 4); if (!es.length) return;")]
s = rep(s, a, "")
s = rep(s, "out.push({ cls: 'warn', ic: '!', t: b.n + ' 가까이에 다른 세력 부대 ' + es.length + '개', s: facName(es[0].f) + '군 ' + uName(es[0]) + (es.length > 1 ? ' 등' : '') + ' · 모두 ' + fmt(t) + '명 · ' + hdist(b.c, b.r, es[0].c, es[0].r) + '칸 거리', go: ['unit', es[0].id], lb: '보기' });",
           "out.push({ cls: 'warn', ic: '!', t: b.n + ' 가까이 적 ' + es.length + '부대', s: facName(es[0].f) + '군 ' + fmt(t) + '명 · ' + hdist(b.c, b.r, es[0].c, es[0].r) + '칸', go: ['unit', es[0].id], lb: '보기' });")
s = rep(s, "out.push({ cls: 'warn', ic: '⚔', t: uName(u) + ' — 적과 맞닿았습니다', s: '부대를 고른 뒤 붉은 칸의 적을 누르면 공격·전법·계략', go: ['unit', u.id], lb: '명령' });",
           "out.push({ cls: 'warn', ic: '⚔', t: uName(u) + ' — 적과 맞닿음', s: '', go: ['unit', u.id], lb: '명령' });")
s = rep(s, "t: uName(u) + ' — ' + statusName(u.status) + ' (' + statusLeftText(u) + ')', s: u.status === 'confuse' ? '움직이지 못하고 피해를 25% 더 받습니다 · 반격 못 함' : '명령을 듣지 않고 가까운 거점 쪽으로 물러납니다 · 반격 못 함', go: ['unit', u.id], lb: '보기', info: 1 });",
           "t: uName(u) + ' — ' + statusName(u.status) + ' (' + statusLeftText(u) + ')', s: '', go: ['unit', u.id], lb: '보기', info: 1 });")
s = rep(s, "t: uName(u) + ' — 불길 속에 있습니다', s: '턴마다 병력 250~400명을 잃습니다 · 불 밖으로 옮기거나 소화', go: ['unit', u.id], lb: '보기', info: 1 });",
           "t: uName(u) + ' — 불길 속', s: '', go: ['unit', u.id], lb: '보기', info: 1 });")
s = rep(s, "out.push({ ic: '▶', t: uName(u) + ' — 명령을 기다립니다', s: UNIT_TYPES[u.type].name + ' ' + fmt(u.troops) + '명 · 갈 곳을 눌러 행군시키거나 대기', go: ['unit', u.id], lb: '명령' });",
           "out.push({ ic: '▶', t: uName(u) + ' — 명령 대기', s: UNIT_TYPES[u.type].name + ' ' + fmt(u.troops) + '명', go: ['unit', u.id], lb: '명령' });")
s = rep(s, "t: uName(u) + ' — 군량이 ' + days(ft) + '분뿐', s: '아군 거점에 들어가면 보급됩니다', go: ['unit', u.id], lb: '보기' });",
           "t: uName(u) + ' — 군량 ' + days(ft) + '분', s: '', go: ['unit', u.id], lb: '보기' });")
s = rep(s, "t: b.n + ' — 등용에 응할 듯한 이웃 무장 ' + hs.length + '명', s: hs.slice(0, 3).map(function (x) { return facName(x.t.f) + ' ' + x.t.n + '(' + x.p + '%)'; }).join(' · ') + ' — 군사 ' + hs[0].adv.adv.n + '의 조언(적중률 ' + hs[0].adv.acc + '%)', go: ['recruit', b.id], lb: '등용', info: 1 });",
           "t: b.n + ' — 등용할 만한 무장 ' + hs.length + '명', s: hs.slice(0, 3).map(function (x) { return x.t.n + ' ' + x.p + '%'; }).join(' · '), go: ['recruit', b.id], lb: '등용', info: 1 });")
s = rep(s, "t: b.n + ' — 다른 세력이 데려갈 수 있는 무장 ' + rk.length + '명', s: rk.slice(0, 3).map(function (x) { return x.o.n + ' 충성 ' + x.o.loy + '(' + x.r.p + '%)'; }).join(' · ') + ' — 포상으로 충성을 ' + POACH.wall + '까지 올리면 응하지 않습니다', go: ['base', b.id, 'men'], lb: '포상', info: 1 });",
           "t: b.n + ' — 떠날 수 있는 무장 ' + rk.length + '명', s: rk.slice(0, 3).map(function (x) { return x.o.n + ' 충성 ' + x.o.loy + ' (' + x.r.p + '%)'; }).join(' · '), go: ['base', b.id, 'men'], lb: '포상', info: 1 });")
s = rep(s, "if (more) out.push({ ic: '+', t: '다른 거점 ' + more + '곳에도 쉬는 무장이 있습니다', s: '목록에서 거점을 고르세요', go: ['list', 'city'], lb: '목록' });",
           "if (more) out.push({ ic: '+', t: '다른 거점 ' + more + '곳에도 쉬는 무장', s: '', go: ['list', 'city'], lb: '목록' });")
s = rep(s, "} else out.push({ ic: '…', t: '행동력이 거의 없습니다 (' + F.ap + ')', s: '내정·출진 명령은 다음 턴에 다시 내릴 수 있습니다' });",
           "} else out.push({ ic: '…', t: '행동력 부족 (' + F.ap + ') — 다음 턴에', s: '' });")
s = rep(s, "t: '행군 중인 부대 ' + mar.length + '개', s: mar.slice(0, 2).map(function (u) { return uName(u) + ' → ' + destName(u.dest); }).join(' · ') + (mar.length > 2 ? ' …' : '') + ' — 턴을 마치면 나아갑니다', go: ['unit', mar[0].id], lb: '보기' });",
           "t: '행군 중 ' + mar.length + '부대', s: mar.slice(0, 2).map(function (u) { return uName(u) + ' → ' + destName(u.dest); }).join(' · ') + (mar.length > 2 ? ' …' : ''), go: ['unit', mar[0].id], lb: '보기' });")
s = rep(s, "  out.push({ cls: 'end', ic: '✓', t: need ? '할 일을 마쳤으면 턴 종료' : '할 일을 모두 마쳤습니다', s: '턴 종료를 누르면 열흘이 흐르고, 그동안 일어난 일을 차례로 보여 줍니다', go: ['end'], lb: '턴 종료' });",
           "  if (!need) out.push({ cls: 'end', ic: '✓', t: '할 일을 모두 마쳤습니다', s: '', go: ['end'], lb: '턴 종료' });      // 남은 일이 있을 때는 아래의 턴 종료 단추로 충분하다")

# ---- STATUS 창 ----
a = s[s.index("      var h = '<div class=\"sh-head hm-head\"><button class=\"porb\" type=\"button\" data-a=\"lord\" aria-label=\"군주 정보\">'"):s.index("      for (i = 0; i < st.todo.length; i++) {\n        var t = st.todo[i];")]
b = """      var pl = peaceLeft(), A = facAdv(f);
      var pz = pl > 0 ? '<button class="pz' + (pl <= 3 ? ' end' : '') + '" type="button" data-a="peace">' + (pl <= 3 ? '보호 ' + days(pl) + ' 남음' : shortDate(G.peace.until - 1) + '까지 보호') + '</button>' : '';
      var h = '<div class="sh-head hm-head"><button class="porb" type="button" data-a="lord" aria-label="군주 정보">' + porTag(L, 'md') + '</button><div class="hm-id">' +
        '<div class="sh-title">' + F.name + '군' + pz + '</div>' +
        (HOME.open ? '<div class="hm-line"><span class="inc">' + ico('gold') + '+' + fmt(T.gi) + '<i>/월</i></span><span class="inc">' + ico('food') + '+' + fmt(T.fi) + '<i>/분기</i></span>' +
            '<button class="hm-adv" type="button" data-a="adv">군사 ' + (A ? '<b>' + A.n + '</b>' : '<b class="bad">없음</b>') + ' <span>▸</span></button></div>'
          : '<div class="sh-sub">' + (need ? '<b class="hi">할 일 ' + need + '건</b>' : '<b class="ok">할 일 없음</b>') + '</div>') + '</div>' +
        '<button class="x fold" data-a="fold" type="button" aria-label="' + (HOME.open ? 'STATUS 창 접기' : 'STATUS 창 펼치기') + '">' + (HOME.open ? '▾' : '▴') + '</button></div>';
      if (!HOME.open) return h;
      h += '<div class="sh-body"><div class="sec">지금 할 일' + (need ? ' <em class="cnt">' + need + '</em>' : '') + '</div><div class="todos">';
"""
s = rep(s, a, b)
s = rep(s, """(t.go ? '' : ' disabled') + '><span class="n' + (t.num ? ' num' : '') + '">' + t.ic + '</span><span class="mid"><b>' + t.t + '</b><small>' + t.s + '</small></span>' + (t.go ? '<span class="go">' + t.lb + ' ▸</span>' : '') + '</button>';""",
           """(t.go ? '' : ' disabled') + '><span class="n' + (t.num ? ' num' : '') + '">' + t.ic + '</span><span class="mid"><b>' + t.t + '</b>' + (t.s ? '<small>' + t.s + '</small>' : '') + '</span>' + (t.go ? '<span class="go">' + t.lb + ' ▸</span>' : '') + '</button>';""")
s = rep(s, "      lists: function (el) { showLists(el.getAttribute('data-v')); }\n    },", "      peace: function () { showPeaceInfo(); }\n    },")
# ---- 거점 창의 탭 이름 ----
s = rep(s, "var tabs = city ? [['home', '내정'], ['mil', '군사'], ['men', '인재'], ['fac', '시설']] : [['mil', '군사'], ['men', '인재']];",
           "var tabs = city ? [['home', '내정'], ['mil', '출진'], ['men', '인재'], ['fac', '시설']] : [['mil', '출진'], ['men', '인재']];      // v0.9.2: '군사' → '출진'(STATUS 창의 군사 = 軍師 와 같은 소리)")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/style.css'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "#sheet.home { max-height: 47%; }", "#sheet.home { max-height: 44%; }")
s = rep(s, ".todo { display: flex; align-items: center; gap: 11px; width: 100%; text-align: left; padding: 8px 4px 8px 2px; border-bottom: 1px solid var(--line); min-height: 56px; }",
           ".todo { display: flex; align-items: center; gap: 11px; width: 100%; text-align: left; padding: 6px 4px 6px 2px; border-bottom: 1px solid var(--line); min-height: 48px; }")
s = rep(s, ".todo b { display: block; font-size: 15px; font-weight: 800; }", ".todo b { display: block; font-size: 15px; font-weight: 800; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }")
s = rep(s, ".todo small { display: block; color: var(--dim); font-size: 12.5px; line-height: 1.35; }", ".todo small { display: block; color: var(--dim); font-size: 12.5px; line-height: 1.35; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }")
s += """
/* ---- v0.9.2 STATUS 창: 한 줄 머리 + 지금 할 일 ---- */
.hm-head { padding-top: 8px; padding-bottom: 8px; }
.hm-head .sh-title { display: flex; align-items: center; gap: 8px; }
.hm-head .sh-title .pz { margin-left: 0; height: 24px; line-height: 22px; font-size: 12.5px; }
button.pz:active { background: var(--paper-2); }
.hm-line { display: flex; align-items: center; gap: 12px; margin-top: 3px; font-size: 13px; color: var(--jade); font-variant-numeric: tabular-nums; white-space: nowrap; }
.hm-line .inc { display: inline-flex; align-items: center; gap: 1px; font-weight: 700; }
.hm-line .inc i { font-style: normal; font-weight: 500; color: var(--dim); font-size: 11.5px; }
.hm-line .hm-adv { margin: 0 0 0 auto; padding: 2px 0 2px 8px; }
.sec .cnt { font: 800 12px var(--font-body); font-style: normal; color: var(--seal-ink); background: var(--seal); border-radius: 9px; min-width: 18px; height: 18px; line-height: 18px; text-align: center; padding: 0 5px; }
"""
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
