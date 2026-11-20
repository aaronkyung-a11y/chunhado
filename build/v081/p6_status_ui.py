# v0.8.1 상태 이상 표시 — 창과 글
#  ① 부대 창: 머리말에 색 딱지(혼란 2턴 · 불길), 본문 맨 위에 풀이 띠(무엇을 못 하는지, 몇 턴 남았는지)
#  ② 대상 줄: 고른 적이 걸려 있으면 딱지와 한 줄 풀이
#  ③ 지금 할 일: 내 부대가 혼란·위보에 걸렸거나 불길 속에 있으면 한 줄씩
#  ④ 걸리는 순간: 떠오르는 글씨와 알림에 '혼란 2턴'처럼 턴 수까지
#  ⑤ 목록의 부대 줄도 같은 딱지. 도움말 '계략과 상태 이상'
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:100])
    return s.replace(a, b)
p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()
# 공용 도우미
s = rep(s, "function afterAction() {", """/* ---------- 상태 이상(혼란·위보·불길)을 글로 ---------- */
function stChips(u) {
  var h = '', n = statusLeft(u);
  if (u.status) h += '<b class="stc st-' + u.status + '">' + statusName(u.status) + (n > 0 ? ' ' + n + '턴' : ' · 곧 풀림') + '</b>';
  if (unitOnFire(u)) h += '<b class="stc st-fire">불길</b>';
  return h;
}
function statusLeftText(u) {
  var n = statusLeft(u);
  if (n <= 0) return '다음 차례에 풀립니다';
  if (u.f === G.player && u.stSkip === G.turn) return n === 1 ? '이번 턴만 — 다음 턴에 풀립니다' : '이번 턴 포함 ' + n + '턴';
  return '앞으로 ' + n + '턴';
}
function statusBanner(u) {
  var h = '', mine = u.f === G.player;
  if (u.status === 'confuse') h += '<div class="stb st-confuse"><b>혼란</b><i>' + statusLeftText(u) + '</i><span>움직이지도 싸우지도 못합니다 · 받는 피해 +25% · 반격하지 못합니다 · 전법 성공률 +10</span></div>';
  else if (u.status === 'rumor') h += '<div class="stb st-rumor"><b>위보</b><i>' + statusLeftText(u) + '</i><span>거짓 소식에 속아 명령을 듣지 않고 가까운 자기 거점 쪽으로 물러납니다 · 반격하지 못합니다</span></div>';
  if (unitOnFire(u)) {
    var ft = G.fires[K(u.c, u.r)];
    h += '<div class="stb st-fire"><b>불길 속</b><i>' + (ft <= 1 ? '이번 턴이 지나면 꺼집니다' : '불은 ' + ft + '턴 더 탑니다') + '</i><span>' + (uHas(u, '화신') ? '화신 특기라 불에 다치지 않습니다' : '불 위에 머무는 동안 턴마다 병력 250~400명과 기력 5를 잃습니다' + (mine ? ' — 불 밖으로 옮기거나 소화하세요' : '')) + '</span></div>';
  }
  return h;
}
function afterAction() {""")
# ① 부대 창
s = rep(s, """ + (x.status ? ' · <b class="bad">' + (x.status === 'confuse' ? '혼란' : '위보') + '</b>' : '') + '</div></div>' +
        '<button class="x" data-a="close" type="button" aria-label="닫기">×</button></div><div class="sh-body">';""",
""" + (stChips(x) ? ' ' + stChips(x) : '') + '</div></div>' +
        '<button class="x" data-a="close" type="button" aria-label="닫기">×</button></div><div class="sh-body">' + statusBanner(x);""")
# ② 대상 줄
s = rep(s, """          h += '<div class="tgt">대상 — <b>' + tn + '</b></div>';""",
"""          h += '<div class="tgt">대상 — <b>' + tn + '</b>' + (t.kind === 'unit' && stChips(t.u) ? ' ' + stChips(t.u) : '') + '</div>';
          if (t.kind === 'unit' && t.u.status) h += '<p class="note stn">' + (t.u.status === 'confuse' ? '<b>혼란 중</b> — 반격하지 못하고 피해를 25% 더 받습니다. 전법도 더 잘 통합니다.' : '<b>위보에 속은 중</b> — 반격하지 못하고 자기 거점 쪽으로 물러나고 있습니다.') + ' ' + statusLeftText(t.u) + '.</p>';""")
s = rep(s, """      } else if (mine && x.done) h += '<p class="note">이번 턴 행동을 마쳤습니다.'""",
           """      } else if (mine && x.done && x.status) h += '<p class="note">' + statusName(x.status) + '에 걸려 명령을 내릴 수 없습니다.</p>';
      else if (mine && x.done) h += '<p class="note">이번 턴 행동을 마쳤습니다.'""")
# ③ 지금 할 일
s = rep(s, """  pendingUnits().forEach(function (u) {
    if (seen[u.id]) return; seen[u.id] = 1;""", """  us.forEach(function (u) {
    if (u.status) out.push({ cls: 'warn', ic: u.status === 'confuse' ? '亂' : '僞', t: uName(u) + ' — ' + statusName(u.status) + ' (' + statusLeftText(u) + ')', s: u.status === 'confuse' ? '움직이지 못하고 피해를 25% 더 받습니다 · 반격 못 함' : '명령을 듣지 않고 가까운 거점 쪽으로 물러납니다 · 반격 못 함', go: ['unit', u.id], lb: '보기', info: 1 });
    if (unitOnFire(u) && !uHas(u, '화신')) out.push({ cls: 'warn', ic: '火', t: uName(u) + ' — 불길 속에 있습니다', s: '턴마다 병력 250~400명을 잃습니다 · 불 밖으로 옮기거나 소화', go: ['unit', u.id], lb: '보기', info: 1 });
  });
  pendingUnits().forEach(function (u) {
    if (seen[u.id]) return; seen[u.id] = 1;""")
# ④ 알림·떠오르는 글씨
s = rep(s, "    if (res.success) msg += res.ploy + ' 성공' + (res.dmg ? ' (-' + fmt(res.dmg) + ')' : '') + (res.chain ? ' · 연환!' : '');",
           "    if (res.success) msg += res.ploy + ' 성공' + (res.dmg ? ' (-' + fmt(res.dmg) + ')' : '') + (res.st ? ' — ' + statusName(res.st) + ' ' + res.stN + '턴' : '') + (res.chain ? ' · 연환!' : '');")
s = rep(s, "    else msg += res.ploy + ' 실패 (성공률 ' + res.p + '%)' + (res.reflected ? ' — 반계에 당했습니다!' : '');",
           "    else msg += res.ploy + ' 실패 (성공률 ' + res.p + '%)' + (res.reflected ? ' — 반계에 당했습니다!' + (res.selfSt ? ' 우리 부대가 ' + statusName(res.selfSt) + ' ' + res.selfStN + '턴' : '') : '');")
s = rep(s, "    if (res.confused) msg += ' · 혼란';", "    if (res.confused) msg += ' · 혼란 ' + (res.stN || 1) + '턴';")
s = rep(s, """      if (res.dmg) floatText(res.c, res.r, '-' + fmt(res.dmg), C_DMG, 260);
      sfx(res.ploy === '화계' ? 'fire' : (res.ploy === '소화' ? 'douse' : 'wind'));""",
"""      if (res.dmg) floatText(res.c, res.r, '-' + fmt(res.dmg), C_DMG, 260);
      if (res.st) floatText(res.c, res.r, statusName(res.st) + ' ' + res.stN + '턴', C_PLOY, 420, false, 26);      // 걸린 상태와 턴 수
      sfx(res.ploy === '화계' ? 'fire' : (res.ploy === '소화' ? 'douse' : 'wind'));""")
s = rep(s, "      if (res.reflected) floatText(res.ac, res.ar, '반계!', C_PLOY, 300, true);",
           "      if (res.reflected) { floatText(res.ac, res.ar, '반계!', C_PLOY, 300, true); if (res.selfSt) floatText(res.ac, res.ar, statusName(res.selfSt) + ' ' + res.selfStN + '턴', C_PLOY, 640, false, 26); }")
s = rep(s, "    if (res.confused) fxs.push('혼란');", "    if (res.confused) fxs.push('혼란 ' + (res.stN || 1) + '턴');")
# ⑤ 목록
s = rep(s, """function unitState(u) {
  if (u.status) return '<b class="bad">' + (u.status === 'confuse' ? '혼란' : '위보') + '</b>';
  if (u.f !== G.player) return '';""", """function unitState(u) {
  var ch = stChips(u);
  if (u.status) return ch;
  if (u.f !== G.player) return ch;
  if (ch) return ch + ' ' + (u.dest >= 0 ? destName(u.dest) + ' 방면 행군' : (u.done ? '행동 완료' : '<b class="hi">명령 대기</b>'));""")
# 도움말
s = rep(s, """  '<h3>인재</h3>""", """  '<h3>계략과 상태 이상</h3><p>부대는 기력을 써서 <b>화계·교란·위보</b>를 겁니다(성공률은 양쪽 지력의 차이로 정해집니다). 걸린 부대는 지도에서 바로 알아볼 수 있습니다 — <b>머리 위에 색 딱지</b>가 뜨고(혼란은 쪽빛, 위보는 황토빛, 불길은 붉은빛) 딱지의 숫자는 <b>남은 턴</b>입니다. 혼란·위보에 걸린 부대는 머리 위에 소용돌이가 돌고 빛이 바래며, 혼란이면 비틀거립니다.</p>' +
  '<ul><li><b>혼란</b>: 움직이지도 싸우지도 못합니다. 받는 피해가 25% 늘고 반격하지 못하며, 전법이 더 잘 통합니다. 교란으로 걸면 2턴, 전법(나선첨 등)으로 걸면 1턴입니다.</li><li><b>위보</b>: 2턴 동안 명령을 듣지 않고 가까운 자기 거점 쪽으로 물러납니다. 반격하지 못합니다.</li><li><b>불길</b>: 불 위에 머무는 부대는 턴마다 병력 250~400명과 기력 5를 잃습니다. 불 밖으로 옮기거나 <b>소화</b>로 끕니다.</li><li>이미 혼란·위보에 걸린 부대에는 교란·위보를 다시 걸 수 없습니다.</li><li>부대를 누르면 창 맨 위에 걸린 상태·남은 턴·효과가 적혀 있습니다. 내 부대가 걸리면 <b>지금 할 일</b>과 <b>지난 열흘의 일</b>에도 나옵니다.</li></ul>' +
  '<h3>인재</h3>""")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/style.css'; s = io.open(p, encoding='utf-8').read()
s += """
/* v0.8.1 상태 이상: 딱지(.stc)와 풀이 띠(.stb). 지도 위 딱지와 같은 빛 — 혼란 쪽빛 · 위보 황토 · 불길 인주 */
.stc { display: inline-block; padding: 0 6px; border-radius: 3px; color: #fbf6ea; font: 800 12px var(--font-body); white-space: nowrap; vertical-align: 1px; margin-left: 2px; }
.stc.st-confuse, .stb.st-confuse b { background: var(--indigo); }
.stc.st-rumor, .stb.st-rumor b { background: var(--ochre); }
.stc.st-fire, .stb.st-fire b { background: var(--seal); }
.stb { display: flex; flex-wrap: wrap; align-items: baseline; gap: 2px 8px; margin: 0 0 8px; padding: 6px 9px; background: var(--paper-2); border-left: 4px solid var(--indigo); font-size: 12.5px; line-height: 1.4; }
.stb.st-rumor { border-left-color: var(--ochre); }
.stb.st-fire { border-left-color: var(--seal); }
.stb b { padding: 0 7px; border-radius: 3px; color: #fbf6ea; font-weight: 800; font-size: 13px; }
.stb i { font-style: normal; font-weight: 800; color: var(--ink); }
.stb span { flex-basis: 100%; color: var(--ink-2); }
.note.stn { margin: -2px 0 8px; color: var(--ink-2); }
.todo.warn .n { font-family: var(--font-display); }
"""
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
