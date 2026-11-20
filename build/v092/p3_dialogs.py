# v0.9.2 글 덜어내기(3/…): 창마다의 설명 문단
#  원칙: 창에는 숫자와 짧은 말만. 규칙 풀이는 도움말에(도움말은 제목만 보이고 눌러야 펼쳐지게), 그때 꼭 알아야 하는 것만 한 줄로 남긴다.
#   - 시작 안내: 항목 여덟 → 넷
#   - 군사 창, 초반 보호 풀이, 등용·생산·출진·수송·시설·포로 창의 설명 문단을 한 줄로 줄이거나 뺌
#   - 거점 창 내정 탭의 "금은 매월 초 …" 문단, 메뉴 단추 아래의 '누르면 전환' 따위
#   - 알림(잠깐 떴다 사라지는 글)도 짧게
#   - 도움말: 열여덟 토막을 제목만 보이게 접는다(누르면 펼쳐짐). 바뀐 화면에 맞게 문구를 고침
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)
p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()

# ---- 군사 창 ----
s = rep(s, """h = dlgHead('군사(軍師)') + '<div class="dlg-b"><div class="help"><p>군사는 <b>등용</b>과 <b>계략</b>을 하기 전에 통할지 미리 말해 줍니다 — <i class="adv y">○</i> 통한다 · <i class="adv n">×</i> 어렵다. 맞힐 확률은 <b>군사의 지력 + (군사의 지력 − 상대의 지력) × ' + ADVISE.k + '</b>이고 ' + ADVISE.min + '~100% 사이입니다. 지력이 높을수록, 상대의 지력이 낮을수록 잘 맞습니다. 군주는 군사가 될 수 없습니다.</p></div>';""",
           """h = dlgHead('군사') + '<div class="dlg-b"><p class="cap">등용·계략 전에 <i class="adv y">○</i> 통함 · <i class="adv n">×</i> 어려움으로 알려 줍니다. 지력이 높을수록 잘 맞습니다.</p>';""")
s = rep(s, """<p><b class="hi">지금의 군사 · ' + A.n + '</b> 지력 ' + A.int + '</p><p class="note">조언 적중률 — 지력 60인 상대 <b>' + adviceAcc(A, 60) + '%</b> · 75인 상대 <b>' + adviceAcc(A, 75) + '%</b> · 90인 상대 <b>' + adviceAcc(A, 90) + '%</b></p></div></div>';""",
           """<p><b class="hi">' + A.n + '</b> 지력 ' + A.int + '</p><p class="note">적중률 <b>' + adviceAcc(A, 60) + '%</b> · <b>' + adviceAcc(A, 75) + '%</b> · <b>' + adviceAcc(A, 90) + '%</b> <small>(상대 지력 60 · 75 · 90)</small></p></div></div>';""")
s = rep(s, """<div class="sec">군사로 삼을 무장 <small>지력 순 · 누르면 바꿉니다(행동력을 쓰지 않습니다)</small></div>""", """<div class="sec">바꾸기 <small>누르면 바뀝니다</small></div>""")
s = rep(s, """(advTag(o) ? '지금의 <b>군사</b>입니다 · 적중률은 지력에 따릅니다' : '군사로 삼으면 등용·계략 전에 조언합니다') + '</div>'""", """(advTag(o) ? '지금의 <b>군사</b>' : '') + '</div>'""")

# ---- 초반 보호 풀이 ----
a = s[s.index("  if (left > 0) h += '<p><b>' + dateOfTurn(P.until - 1) + '까지(' + days(left) + ' 남음)</b>"):s.index("function showPeaceInfo()")]
b = """  if (left > 0) h += '<p><b>' + dateOfTurn(P.until - 1) + '까지</b> (' + days(left) + ' 남음) 다른 세력이 우리 <b>거점과 시설</b>을 먼저 치지 않습니다.</p>';
  else h += '<p>초반 보호는 <b>' + dateOfTurn(P.until - 1) + '</b>에 끝났습니다.' + (G.turn < P.until + PEACE_RAMP ? ' <b>' + dateOfTurn(P.until + PEACE_RAMP - 1) + '</b>까지는 완충 기간입니다.' : '') + '</p>';
  if (br.length) h += '<p class="bad"><b>먼저 친 세력: ' + br.join(' · ') + '</b> — 이 세력은 지금도 우리를 칠 수 있습니다.</p>';
  return h + '<ul><li><b>우리가 먼저 친 세력</b>과는 보호가 풀립니다.</li>' +
    '<li>들판의 부대끼리는 싸울 수 있고, 빈 성은 누구나 차지합니다.</li>' +
    '<li>끝난 뒤 ' + months(PEACE_RAMP) + '은 <b>완충 기간</b> — 한 번에 한 세력만 치러 옵니다.</li></ul></div>';
}
"""
s = rep(s, a, b)

# ---- 시작 안내 ----
a = s[s.index("""        '<li><b>도시</b>를 누르면 내정·군사·인재 명령이 열립니다. 도시 둘레 <b>밝은 칸</b>에 시설을 짓습니다.</li>' +"""):s.index("""<div class="dlg-f"><div class="pv">도시 42곳을 모두 차지하면 천하통일</div>""")]
b = """        '<li>아래 <b>지금 할 일</b>을 위에서부터 누르면 됩니다.</li>' +
        '<li><b>도시</b>를 누르면 명령이 열립니다. <b>부대</b>는 파란 칸으로 움직이고, 적을 누르면 공격합니다.</li>' +
        '<li>다 했으면 <b>턴 종료</b> — 열흘이 흐릅니다.</li>' +
        (peaceLeft() > 0 ? '<li><b>초반 보호</b> — <b>' + dateOfTurn(G.peace.until - 1) + '까지(' + months(peaceLeft()) + ')</b> 아무도 우리 성을 먼저 치지 않습니다.</li>' : '') +
        '</ul></div></div>"""
s = rep(s, a, b)

# ---- 군주 고르기 ----
s = rep(s, "'세력을 누르면 선택됩니다<br><small>병력이 적은 세력일수록 초반 보호가 깁니다</small>')", "'군주를 고르세요')")

# ---- 거점 창 ----
s = rep(s, """ + '</div>' +
          '<p class="note">금은 매월 초, 병량은 1·4·7·10월 초에 들어옵니다. 치안이 낮으면 수입과 징병량이 줄어듭니다.</p>';""", """ + '</div>';""")
s = rep(s, "(b.owner >= 0 ? '주둔 무장 ' + os.length + '명' : '주인 없는 거점 — 부대를 들여보내면 점령합니다')", "(b.owner >= 0 ? '주둔 무장 ' + os.length + '명' : '빈 거점 — 부대가 들어가면 차지')")

# ---- 흐름 창 ----
s = rep(s, "return toast('병영이 필요합니다 — 시설 탭에서 지으세요');", "return toast('병영이 필요합니다');")
s = rep(s, """return h + '</div><p class="note">창·극·노·군마는 금 ' + COST.produce + ', 충차는 금 ' + COST.ram + '. 지력이 높은 무장일수록 많이 만듭니다.</p></div>';""",
           """return h + '</div><p class="note">금 ' + COST.produce + ' · 충차는 금 ' + COST.ram + '</p></div>';""")
s = rep(s, "preview: function () { return '재야의 인재나 숨은 재물을 찾습니다'; } },", "preview: function () { return '인재나 재물을 찾습니다'; } },")
s = rep(s, "done(r, josa(off(r.found).n, '을를') + ' 찾았습니다! 등용해 보세요'); }", "done(r, josa(off(r.found).n, '을를') + ' 찾았습니다'); }")
s = rep(s, "return toast('등용할 대상이 없습니다 — 탐색으로 재야 인재를 찾으세요');", "return toast('등용할 대상이 없습니다');")
s = rep(s, """if (!idle) h += '<p class="note">이 거점에 쉬는 무장이 없어 지금은 권할 수 없습니다.</p>';""", """if (!idle) h += '<p class="note">쉬는 무장이 없어 지금은 권할 수 없습니다</p>';""")
s = rep(s, """<div class="sec">이웃 거점의 다른 세력 무장 <small>응하면 이 거점으로 넘어옵니다</small></div>""", """<div class="sec">이웃 거점의 다른 세력 무장</div>""")
a = s[s.index("""        h += '</div><p class="note">성공률은 <b>그 달에 응할 확률</b>입니다"""):s.index("""      return h + '</div>';
    },
    on: { t: function (el) {
      var t = off(+el.getAttribute('data-v')), w = why(t), farT = t.st === 'active';""")]
s = rep(s, a, """        h += '</div><p class="note">한 무장에게 <b>한 달에 한 번</b> · 거절하면 충성 +' + POACH.up + '</p>';
      }
""")
s = rep(s, "josa(t.n, '이가') + ' 거절했습니다' + (r.far ? ' — 다음 달에 다시 권할 수 있습니다 (충성 +' + POACH.up + ')' : ' — 다음 턴에 다시 권할 수 있습니다')) : '');",
           "josa(t.n, '이가') + ' 거절했습니다' + (r.far ? ' (충성 +' + POACH.up + ')' : '')) : '');")
s = rep(s, """<p class="note">등용은 인재 → 등용에서 합니다. 풀어 주면 원래 세력으로 돌아갑니다.</p>""", """<p class="note">등용은 인재 → 등용에서</p>""")
s = rep(s, """'<br><span class="warn">담당 무장은 완공될 때까지 다른 일을 못 합니다</span>'; } },""", """'<br><span class="warn">담당 무장은 완공까지 묶입니다</span>'; } },""")
s = rep(s, "F.name + ' 착공 — ' + days(r.turns) + ' 뒤 완공. ' + josa(os.map(function (o) { return o.n; }).join('·'), '은는') + ' 그때까지 공사에 매입니다' : '', 'hammer'); });",
           "F.name + ' 착공 — ' + days(r.turns) + ' 뒤 완공' : '', 'hammer'); });")
s = rep(s, """(builders(fc).length ? ' · 담당 <b>' + builders(fc).map(function (o) { return o.n; }).join('·') + '</b> (완공될 때까지 다른 일을 못 합니다)' : '') + '</p>') +""",
           """(builders(fc).length ? ' · 담당 <b>' + builders(fc).map(function (o) { return o.n; }).join('·') + '</b>' : '') + '</p>') +""")
s = rep(s, """<small>' + (fc.done ? '부지를 비웁니다' : (builders(fc).length ? '부지를 비우고 담당 무장을 풉니다' : '부지를 비웁니다')) + '</small></button></div>' +
        '<p class="note">흡수합병: 바로 옆의 같은 종류 시설 하나를 흡수해 레벨을 올립니다(최대 3). 흡수된 부지는 비워집니다.</p></div>';""",
           """<small>' + (!fc.done && builders(fc).length ? '담당 무장이 풀려납니다' : '부지를 비웁니다') + '</small></button></div>' +
        '<p class="note">흡수합병 = 옆의 같은 시설을 합쳐 레벨 +1 (최대 3)</p></div>';""")
s = rep(s, """h += '</div><div class="sec">무장 — 첫 번째가 주장, 최대 3명<button class="btn auto" type="button" data-a="auto">자동 편성</button></div><div class="rows">';""",
           """h += '</div><div class="sec">무장 <small>첫 번째가 주장 · 3명까지</small><button class="btn auto" type="button" data-a="auto">자동 편성</button></div><div class="rows">';""")
s = rep(s, """h += '</div><p class="note">도시 병량 ' + fmt(b.food) + '. 이웃 거점까지는 가까우면 20일, 보통 30~50일이 걸립니다. 군량이 떨어지면 병사가 흩어집니다.</p>';""",
           """h += '</div><p class="note">도시 병량 ' + fmt(b.food) + ' · 이웃 거점까지 20~50일</p>';""")
s = rep(s, "toast(st.ids.length ? UNIT_TYPES[st.type].name + '에 가장 알맞은 ' + st.ids.length + '명을 골랐습니다' : '편성할 무장이 없습니다', 2200);", "toast(st.ids.length ? '자동 편성 ' + st.ids.length + '명' : '편성할 무장이 없습니다', 1800);")
s = rep(s, "toast(name + ' 출진 — 파란 칸을 눌러 이동하세요', 2600); }", "toast(name + ' 출진', 1800); }")
s = rep(s, "toast('싸움에 덜 쓰이는 무장을 골랐습니다', 2000);", "toast('자동 선택', 1500);")
s = rep(s, "toast('수송대 출발 — 파란 칸을 눌러 이동하세요. 아군 거점으로 들여보내면 물자가 합쳐집니다', 3200);", "toast('수송대 출발 — 아군 거점에 들이면 물자가 합쳐집니다', 2600);")
s = rep(s, """return h + '<p class="note">수송대는 싸움에 약합니다. 병력이 먹을 군량은 최소 80일분이 자동으로 실립니다.</p></div>""", """return h + '<p class="note">군량 80일분은 자동으로 실립니다</p></div>""")
s = rep(s, "toast(max === 1 ? '가장 알맞은 무장을 골랐습니다' : (n > 1 ? '효과가 가장 큰 조합 ' + sel.length + '명 — 한 번 더 누르면 한 명만' : '한 명만 쓸 때 가장 나은 무장'), 2200);",
           "toast(max === 1 ? '자동 선택' : (n > 1 ? '자동 ' + sel.length + '명 — 다시 누르면 1명' : '자동 1명'), 1800);")

# ---- 목록 · 지난 열흘 · 메뉴 ----
s = rep(s, """<p class="note">출진한 부대가 없습니다. 거점의 <b>군사 → 출진</b>에서 내보냅니다.</p>""", """<p class="note">출진한 부대가 없습니다</p>""")
s = rep(s, "'<small>' + n + '건 · 줄을 누르면 그곳을 보여 줍니다</small></div>';", "'<small>' + n + '건</small></div>';")
s = rep(s, "toast(dateStr() + ' — 새 턴입니다. 지난 열흘은 조용했습니다', 2600);", "toast(dateStr() + ' — 조용한 열흘', 2200);")
s = rep(s, """<b>저장</b><small>이 기기에 저장</small></button><button class="cmd" type="button" data-a="load"><b>불러오기</b><small>마지막 저장</small></button>""", """<b>저장</b></button><button class="cmd" type="button" data-a="load"><b>불러오기</b></button>""")
s = rep(s, """<b>효과음 ' + (UI.sound ? '켜짐' : '꺼짐') + '</b><small>누르면 전환</small></button>""", """<b>효과음 ' + (UI.sound ? '켜짐' : '꺼짐') + '</b></button>""")
s = rep(s, """'</b><small>' + (!UI.music ? '누르면 켬' : (BGM.mode === 'file' ? '연주곡 · 누르면 끔' : (BGM.mode === 'syn' ? '곡 파일을 못 읽어 만든 음악 · 누르면 끔' : '누르면 끔'))) + '</small></button>""",
           """'</b>' + (UI.music && BGM.mode === 'file' ? '<small>연주곡</small>' : (UI.music && BGM.mode === 'syn' ? '<small>만든 음악</small>' : '')) + '</button>""")
s = rep(s, """<b>열흘 재생</b><small>' + SPEEDS[UI.pspeed][0] + ' · 누르면 전환</small></button><button class="cmd" type="button" data-a="help"><b>도움말</b><small>규칙·조작</small></button>""",
           """<b>열흘 재생</b><small>' + SPEEDS[UI.pspeed][0] + '</small></button><button class="cmd" type="button" data-a="help"><b>도움말</b></button>""")
s = rep(s, """<b>처음으로</b><small>타이틀 화면</small></button></div><p class="note">턴을 마칠 때마다 자동으로 저장됩니다. 저장은 이 기기의 브라우저에만 남습니다.</p></div>';""",
           """<b>처음으로</b></button></div><p class="note">턴마다 자동 저장 · 이 기기에만 남습니다</p></div>';""")
s = rep(s, "toast(UI.pspeed ? '턴을 마치면 지난 열흘을 ' + SPEEDS[UI.pspeed][0] + ' 보여 줍니다' : '재생을 끕니다 — 턴을 마치면 바로 요약만 보여 줍니다', 2600);", "toast(UI.pspeed ? '열흘 재생: ' + SPEEDS[UI.pspeed][0] : '열흘 재생 끔 — 요약만', 2000);")

# ---- 도움말: 접히는 토막 + 바뀐 화면에 맞춘 문구 ----
s = rep(s, "아무것도 고르지 않았을 때는 세력 현황과 <b>지금 할 일</b>이 보이고, 줄을 누르면 그 거점이나 부대로 바로 갑니다. 거점이나 부대를 고르면 같은 자리에 그 정보와 명령이 나옵니다. <b>거점·부대·무장·천하</b> 단추는 그 목록을 엽니다 — 부대 목록에는 내 부대의 위치와 상태, 그리고 가까이 있는 다른 세력의 부대가 나옵니다. 오른쪽 위 ▾로 접을 수 있고, 맨 위 날짜 줄을 누르면 다시 펼쳐집니다.</p>' +",
           "아무것도 고르지 않았을 때는 <b>지금 할 일</b>이 보이고, 줄을 누르면 그 거점이나 부대로 바로 갑니다. 거점이나 부대를 고르면 같은 자리에 그 정보와 명령이 나옵니다. 이름 아래의 +숫자는 금(매월)·병량(분기) 수입입니다. 오른쪽 ▾로 접을 수 있고, 맨 위 날짜 줄을 누르면 다시 펼쳐집니다.</p><p>아래 <b>목록</b> 단추는 거점·부대·무장·세력의 목록을 엽니다 — 부대 목록에는 내 부대의 위치와 상태, 그리고 가까이 있는 다른 세력의 부대가 나옵니다.</p>' +")
s = rep(s, "<h3>출진과 이동</h3><p>군사 → 출진에서 병과,", "<h3>출진과 이동</h3><p>거점의 출진 탭에서 병과,")
s = rep(s, "언제까지인지는 STATUS 창의 날짜 옆과 <b>지금 할 일</b> 맨 위에 보입니다.</p>' +", "언제까지인지는 STATUS 창의 이름 옆 표에 보입니다(누르면 풀이).</p>' +")
s = rep(s, '위험한 무장이 있으면 지금 할 일에 "다른 세력이 데려갈 수 있는 무장"이 뜹니다', '위험한 무장이 있으면 지금 할 일에 "떠날 수 있는 무장"이 뜹니다')
s = rep(s, "막 출진한 부대의 창을 닫으면 나온 성의 군사 탭으로 돌아갑니다.</p>' +", "막 출진한 부대의 창을 닫으면 나온 성의 출진 탭으로 돌아갑니다.</p>' +")
s = rep(s, "function showHelp() { showDialog({ render: function () { return dlgHead('도움말') + '<div class=\"dlg-b\">' + HELP_HTML + '</div>'; }, on: {} }, true); }",
"""/* 도움말은 제목만 보이게 접어 둔다(v0.9.2) — 누른 토막만 펼쳐진다 */
function helpSections() {
  var body = HELP_HTML.replace(/^<div class="help">/, '').replace(/<\\/div>$/, ''), parts = body.split('<h3>'), h = '<div class="help acc">';
  for (var i = 1; i < parts.length; i++) { var k = parts[i].indexOf('</h3>'); h += '<details><summary>' + parts[i].slice(0, k) + '</summary>' + parts[i].slice(k + 5) + '</details>'; }
  return h + '</div>';
}
function showHelp() { showDialog({ render: function () { return dlgHead('도움말') + '<div class="dlg-b">' + helpSections() + '</div>'; }, on: {} }, true); }""")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/style.css'; s = io.open(p, encoding='utf-8').read()
s += """
/* ---- v0.9.2 도움말: 접히는 토막 ---- */
.help.acc details { border-bottom: 1px solid var(--line); }
.help.acc summary { list-style: none; cursor: pointer; padding: 12px 2px; font: 900 15.5px var(--font-display); color: var(--ink); display: flex; align-items: center; justify-content: space-between; }
.help.acc summary::-webkit-details-marker { display: none; }
.help.acc summary::after { content: "▸"; color: var(--seal); font: 800 13px var(--font-body); }
.help.acc details[open] > summary::after { content: "▾"; }
.help.acc details[open] { padding-bottom: 8px; }
.help.acc details > p:first-of-type { margin-top: 0; }
.cap { margin: 0 0 10px; font-size: 12.5px; color: var(--ink-2); line-height: 1.5; }
"""
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
