# v0.18 화면 — ① 얼굴을 누르면 어디서든 겹쳐 뜨는 무장 카드  ② 특기가 무엇을 하는지 · 고르는 표에서도 병종 적성이 보이게  ③ 확률을 숫자 대신 말로(가늠)
#   규칙은 건드리지 않는다(확률 자체는 그대로 — 보여 주는 말만 바뀐다. 메뉴의 '확률 표시'로 예전처럼 % 로 볼 수 있다).
#   CH_ROOT=<폴더> 로 다른 나무에 입힐 수 있다(시험용).
import io, os
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)
def cut(s, a, b):                       # a 로 시작해 b 바로 앞까지를 돌려준다(한 번만 나와야 한다)
    assert s.count(a) == 1 and s.count(b) == 1, ('cut', s.count(a), s.count(b), a[:50])
    i = s.index(a); j = s.index(b); assert i < j
    return s[i:j]

# ───────────────────────── data.js: 특기의 짧은 풀이 ─────────────────────────
s = rd('src/data.js')
s = rep(s, "var SKILLS = {\n",
"""/* v0.18 특기의 짧은 풀이 — 목록의 이름 옆에 곁들인다(18자 안). 자세한 풀이는 SKILLS */
var SKILL_TAG = {
  '비장': '통제 무시 · 약한 적에 치명', '신장': '약한 적 치명 · 전법 +10%', '투신': '창·극 전법 대성공', '용장': '약한 적에 치명',
  '창장': '창병 전법 대성공', '극장': '극병 전법 대성공', '궁장': '노병 전법 대성공', '기장': '기병 전법 대성공', '기신': '기병 전법 대성공 +10%', '궁신': '노병 전법 대성공 +10%',
  '위풍': '적 기력 −10 더', '연전': '절반은 두 번 공격', '금강': '통상 피해 −35%', '철벽': '전법 피해 −30%', '불굴': '병력 적을 때 피해 −50%', '급습': '절반은 반격 없음', '공심': '준 피해 10% 흡수',
  '강행': '이동력 +3', '답파': '숲·구릉을 평지처럼', '포박': '사로잡기 2배', '공성': '성 내구 피해 +50%',
  '신산': '지력 낮은 적에 계략 필중', '허실': '계략 성공 +20', '귀모': '계략 사거리 +1', '통찰': '계략에 안 걸림', '명경': '교란·위보 안 걸림', '간파': '지력 낮은 적 계략 무효',
  '반계': '실패한 계략 되돌림', '연환': '계략이 옆 적에도', '심모': '계략 +10일 · 화계 +50%', '화신': '화계 필중 · 피해 2배', '화공': '화계 +20 · 피해 +50%',
  '부호': '금 수입 +20%', '미도': '병량 수입 +20%', '명성': '징병 +50%', '능리': '창·극·노 생산 +50%', '번식': '군마 생산 +50%', '발명': '충차 반값', '축성': '건설 2배 빠름', '둔전': '군량 소모 절반',
  '인덕': '징병 치안 하락 절반', '위압': '순찰 효과 2배', '안력': '인재 탐색 2배', '논객': '등용 성공 +20', '지도': '행동력 회복 +10', '왕좌': '행동력 회복 +15'
};
var SKILLS = {
""")
wr('src/data.js', s)

# ───────────────────────── ui_panels.js ─────────────────────────
s = rd('src/ui_panels.js')

# ── ① 얼굴(초상)에 무장 번호를 실어, 누르면 카드가 뜨게 ──
s = rep(s, "function porTag(o, cls) { var u = o ? POR_URL[o.por] : ''; return '<i class=\"por' + (cls ? ' ' + cls : '') + '\"' + (u ? ",
"""/* v0.18: 지금 판의 무장이면 data-oid 를 단다 — 얼굴을 누르면 어디서든 무장 카드가 겹쳐 뜬다(ocardInit). 세력을 고르는 창처럼 판 밖의 얼굴에는 달지 않는다 */
function oidAttr(o) { return o && typeof o.id === 'number' && G && G.officers && G.officers[o.id] === o ? ' data-oid="' + o.id + '"' : ''; }
function porTag(o, cls) { var u = o ? POR_URL[o.por] : ''; return '<i class="por' + (cls ? ' ' + cls : '') + '"' + oidAttr(o) + (u ? """)
s = rep(s, "return u ? '<i class=\"por sc\" style=\"background-image:url(' + u + '),var(--porbg)\"></i>' : porTag(o, 'lg'); }",
           "return u ? '<i class=\"por sc\"' + oidAttr(o) + ' style=\"background-image:url(' + u + '),var(--porbg)\"></i>' : porTag(o, 'lg'); }")

# ── ② 특기: 이름 옆에 짧은 풀이 ──
s = rep(s, "function skTag(o) { return o.sk ? '<em>' + o.sk + '</em>' : ''; }",
           "function skGist(o) { return o && o.sk && SKILL_TAG[o.sk] ? SKILL_TAG[o.sk] : ''; }\n"
           "function skTag(o) { return o.sk ? '<em>' + o.sk + '</em>' + (skGist(o) ? '<small class=\"skg\">' + skGist(o) + '</small>' : '') : ''; }      // v0.18: 무엇을 하는 특기인지 한 줄")
# 무장 선택 표: 줄마다 둘째 줄에 병종 적성 다섯 칸 + 특기와 그 풀이(이동·수송·등용처럼 적성이 보이지 않던 표에서도)
s = rep(s, "        h += '<span class=\"c-x\">' + (opts.rt ? opts.rt(o) : (o.sk || '—')) + '</span></button>';",
           "        h += '<span class=\"c-x\">' + (opts.rt ? opts.rt(o) : (o.sk || '—')) + '</span>' +\n"
           "          '<span class=\"c-2\">' + apt5(o, opts.apt) + (o.sk ? '<span class=\"sk2\"><b>' + o.sk + '</b>' + (skGist(o) ? ' ' + skGist(o) : '') + '</span>' : '') + '</span></button>';      // v0.18")

# ── ① 무장 상세: 몸통을 떼어 창과 카드가 함께 쓴다 ──
old = cut(s, "/* 무장 상세 */\nfunction showOfficer(o) {", "/* ---------- HUD ---------- */")
assert "'<p class=\"note aptn\">부대의 공격·방어에 곱해집니다" in old and "군사로 삼기" in old
new = """/* 무장 상세 — 몸통(officerBody)은 창(showOfficer)과, 얼굴을 누르면 겹쳐 뜨는 카드(ocardOpen, v0.18)가 함께 쓴다 */
function officerBody(o) {
  var apt = ['창', '극', '노', '기', '병기'], a = '', i;
  for (i = 0; i < 5; i++) a += '<div class="' + o.apt.charAt(i) + '">' + apt[i] + '<b>' + o.apt.charAt(i) + '</b></div>';
  var bars = '', ks = [['ldr', '통솔'], ['war', '무력'], ['int', '지력'], ['pol', '정치'], ['cha', '매력']];
  for (i = 0; i < 5; i++) bars += '<div class="bar"><span>' + ks[i][1] + '</span><i><u style="width:' + o[ks[i][0]] + '%"></u></i><b>' + o[ks[i][0]] + '</b></div>';
  var un = o.unit !== null && o.unit !== undefined ? UMAP[o.unit] : null;
  var where = o.st === 'free' ? '재야 (' + G.bases[o.loc].n + ')' : o.st === 'captive' ? '포로 (' + G.bases[o.loc].n + ')' : (o.unit !== null ? '출진 중' : G.bases[o.loc].n);
  return '<div class="card">' + sceneTag(o) + '<div class="bars">' + bars + '</div></div>' +
    '<div class="sec">병종 적성</div><div class="apt">' + a + '</div>' +
    '<p class="note aptn">부대의 공격·방어에 곱해집니다 — C ×' + APT_MUL.C + ' · B ×' + APT_MUL.B + ' · A ×' + APT_MUL.A + ' · S ×' + APT_MUL.S + ' (주장·부장 가운데 가장 높은 적성). 전법은 C 하나 · B 둘 · A부터 셋을 쓰고, 높을수록 잘 통합니다.</p>' +
    (o.sk ? '<p class="skp"><b class="hi">특기 · ' + o.sk + '</b><br>' + SKILLS[o.sk] + '</p>' : '<p class="note">특기 없음</p>') +
    '<div class="stats"><div><span>소재</span><b>' + where + '</b></div>' + (o.f >= 0 ? '<div><span>충성</span><b>' + (isLord(o) ? '군주' : o.loy + (bondOf(o) ? ' <em class="bond">' + bondOf(o) + '</em>' : '')) + '</b></div><div><span>지휘</span><b>' + fmt(cmdCap(o)) + '</b></div><div><span>공적</span><b>' + fmt(o.merit) + '</b></div>' : '') + '</div>' +
    (un ? '<p class="note ocu">' + (uLeader(un) === o ? '주장' : '부장') + ' — ' + UNIT_TYPES[un.type].name + ' <b>' + fmt(un.troops) + '</b>명 · 기력 ' + un.morale + (APT_IDX[un.type] !== undefined ? ' · 부대 적성 ' + uApt(un) : '') + '</p>' : '') +
    (servedF(o).length ? '<p class="note">섬겼던 세력 — ' + servedTxt(o) + '</p>' : '');
}
function showOfficer(o) {
  showDialog({
    render: function () {
      return dlgHead(o.n + ' ' + (o.f >= 0 ? facChip(o.f) : '') + (advTag(o) ? ' <em class="advt">군사</em>' : '')) + '<div class="dlg-b">' + officerBody(o) + '</div>' +
        ((o.f === G.player && advOk(o, G.player)) ? '<div class="dlg-f"><div class="pv">' + (advTag(o) ? '지금의 <b>군사</b>' : '') + '</div>' + (advTag(o) ? '' : '<button class="btn" type="button" data-a="adv">군사로 삼기</button>') + '</div>' : '');
    }, on: { adv: function () { var r = setAdvisor(G.player, o.id); if (!r.ok) return toast(r.msg); sfx('ui'); talk(o, sayLine(o, 'advisor'), josa(o.n, '을를') + ' 군사로 삼았습니다 (지력 ' + o.int + ')'); refreshDialog(); refreshSheet(); } }
  }, true);                                              // 목록 같은 창 위에서 열었으면 ×로 그 창에 돌아간다
}
/* v0.18 무장 카드: 얼굴(초상)을 누르면 어디서든 겹쳐 뜬다 — 창 · STATUS 창 · 대화창 · 일기토 위에. 닫으면(× · 바깥 · Esc) 하던 일이 그대로 남는다.
   창(MODAL)의 흐름과 따로 놀도록 제 층(#ocard)을 쓴다: 무장을 고르던 표도, 겨루던 일기토도 건드리지 않는다 */
var OCARD = -1;
function ocardEl() { var e = $('ocard'); if (!e) { e = document.createElement('div'); e.id = 'ocard'; e.setAttribute('role', 'dialog'); e.setAttribute('aria-label', '무장 정보'); $('app').appendChild(e); } return e; }
function ocardOpen(o) {
  if (!o || !G) return;
  OCARD = o.id;
  var e = ocardEl();
  e.innerHTML = '<div class="oc"><div class="dlg-h"><h2>' + o.n + ' ' + (o.f >= 0 ? facChip(o.f) : '') + (o.f >= 0 && isLord(o) ? ' <em class="advt">군주</em>' : '') + (advTag(o) ? ' <em class="advt">군사</em>' : '') + '</h2><button class="x" data-oc="x" type="button" aria-label="닫기">×</button></div><div class="oc-b">' + officerBody(o) + '</div></div>';
  e.classList.add('on');
  try { sfx('ui'); } catch (err) { /* 소리가 없어도 */ }
}
function ocardClose() { OCARD = -1; var e = $('ocard'); if (e) { e.classList.remove('on'); e.innerHTML = ''; } }
function ocardOn() { var e = $('ocard'); return !!(e && e.classList.contains('on')); }
function ocardInit() {
  document.addEventListener('click', function (e) {              // 잡는 단계에서 먼저 본다: 얼굴 위의 누름은 줄·단추의 일(고르기 등)로 내려가지 않는다
    var t = e.target;
    if (ocardOn()) { if (!t.closest || !t.closest('.oc') || t.closest('[data-oc="x"]')) ocardClose(); e.stopPropagation(); e.preventDefault(); return; }
    var el = t.closest ? t.closest('[data-oid]') : null; if (!el || !G) return;
    if (el.closest('[data-a=lord]')) return;                     // STATUS 창의 군주 초상 단추는 제 일(군주의 무장 창)을 한다
    var o = G.officers[+el.getAttribute('data-oid')]; if (!o) return;
    e.stopPropagation(); e.preventDefault(); ocardOpen(o);
  }, true);
}
"""
s = s.replace(old, new)
s = rep(s, "  delegate($('modal'), function () { return MODAL; }, function () { backDialog(); });\n",
           "  delegate($('modal'), function () { return MODAL; }, function () { backDialog(); });\n  ocardInit();                                                   // v0.18: 얼굴을 누르면 무장 카드\n")
s = rep(s, "    if (e.key !== 'Escape') return;\n    if (MODAL) { backDialog(); return; }",
           "    if (e.key !== 'Escape') return;\n    if (ocardOn()) { ocardClose(); return; }\n    if (MODAL) { backDialog(); return; }")
# 판이 바뀌면(처음으로 · 불러오기) 카드는 닫는다
s = rep(s, "function showTitle() {\n  $('title').classList.remove('off');\n", "function showTitle() {\n  ocardClose();\n  $('title').classList.remove('off');\n")
s = rep(s, "function startGame() {\n  $('title').classList.add('off');\n", "function startGame() {\n  ocardClose();\n  $('title').classList.add('off');\n")

# ── ③ 가늠: 확률을 말로 ──
s = rep(s, "/* ---------- 군사의 조언(v0.9) ---------- */\n",
"""/* ---------- v0.18 가늠: 확률을 숫자 대신 말로 ----------
   UI.pct(메뉴 → 확률 표시)가 켜져 있으면 예전처럼 % 로. 꺼져 있으면(기본) 말로 보인다 — 가늠하는 이는 군사와 군주 가운데 지력이 높은 쪽.
   그 지력이 ODDS_FINE 이상이면 다섯 단계로 또렷이, 아니면 셋으로 어림해서만 보인다(똑똑한 군사를 둘 까닭이 하나 더 생긴다). 규칙의 확률은 그대로다.
   pcT = 글 속의 한 마디 · pcG = 말 + 눈금 다섯 칸 · pcBest = '최고 N%' 자리 · pcWas = 지난 일의 '(성공률 N%)' 자리 · accT = 군사의 조언이 맞을 확률 */
var ODDS_FINE = 70;
var ODDS_W = ['불가', '매우 낮음', '낮음', '반반', '높음', '매우 높음', '확실'], ODDS_WC = ['불가', '낮은 듯', '낮은 듯', '반반인 듯', '높은 듯', '높은 듯', '확실'];
function oddsEye() {
  if (!G || !(G.player >= 0)) return { o: null, adv: false, fine: true };
  var L = off(G.factions[G.player].lord), A = facAdv(G.player), J = A && A.int >= L.int ? A : L;
  return { o: J, adv: J === A, fine: J.int >= ODDS_FINE };
}
function oddsLv(p, fine) {                               // 0 불가 · 1~5 · 6 확실
  if (!(p > 0)) return 0;
  if (p >= 100) return 6;
  if (fine) return p >= 85 ? 5 : (p >= 65 ? 4 : (p >= 45 ? 3 : (p >= 25 ? 2 : 1)));
  return p >= 65 ? 4 : (p >= 35 ? 3 : 2);
}
function oddsWord(p) { var e = oddsEye(); return (e.fine ? ODDS_W : ODDS_WC)[oddsLv(p, e.fine)]; }
function pcT(p) { return UI.pct ? p + '%' : oddsWord(p); }
function pcG(p) {
  if (UI.pct) return p + '%';
  var e = oddsEye(), lv = oddsLv(p, e.fine), n = Math.min(5, lv), g = '';
  for (var i = 1; i <= 5; i++) g += '<u' + (i <= n ? ' class="on"' : '') + '></u>';
  return (e.fine ? ODDS_W : ODDS_WC)[lv] + '<i class="odg lv' + lv + (e.fine ? '' : ' dim') + '">' + g + '</i>';
}
function pcBest(p) { return UI.pct ? '최고 <b>' + p + '%</b>' : '<b>' + oddsWord(p) + '</b>'; }
function pcWas(p, label) { return UI.pct ? label + ' ' + p + '%' : '가늠은 ' + oddsWord(p); }
function accT(acc) { return UI.pct ? '적중률 ' + acc + '%' : (acc >= 90 ? '거의 틀림없음' : (acc >= 75 ? '믿을 만함' : (acc >= 60 ? '반신반의' : '미덥지 않음'))); }
function eyeNote() {                                     // 누가 가늠하는가 한 줄
  var e = oddsEye(); if (UI.pct || !e.o) return '';
  return '<p class="note eye">가늠 — ' + (e.adv ? '군사 ' : '군주 ') + '<b>' + e.o.n + '</b> (지력 ' + e.o.int + ') · ' + (e.fine ? '또렷이 봅니다' : '어림으로만 봅니다 <small>지력 ' + ODDS_FINE + ' 이상의 군사를 두면 또렷해집니다</small>') + '</p>';
}
/* ---------- 군사의 조언(v0.9) ---------- */
""")
# 군사의 조언이 맞을 확률
s = rep(s, "(a.says ? (yes || '통할 것입니다.') : (no || '어렵겠습니다.')) + '</b>', '적중률 ' + a.acc + '%', 'adv') : ''; }",
           "(a.says ? (yes || '통할 것입니다.') : (no || '어렵겠습니다.')) + '</b>', accT(a.acc), 'adv') : ''; }")
s = rep(s, "(a.says ? '통할 것입니다' : '어렵겠습니다') + '</b> <small>적중률 ' + a.acc + '%</small>' : ''; }",
           "(a.says ? '통할 것입니다' : '어렵겠습니다') + '</b> <small>' + accT(a.acc) + '</small>' : ''; }")
s = rep(s, "</p><p class=\"note\">적중률 <b>' + adviceAcc(A, 0) + '%</b>' + (A.int < 95 ? ' <small>· 지력 95인 상대에게는 ' + adviceAcc(A, 95) + '%</small>' : '') + '</p>",
           "</p><p class=\"note\">' + (UI.pct ? '적중률 <b>' + adviceAcc(A, 0) + '%</b>' + (A.int < 95 ? ' <small>· 지력 95인 상대에게는 ' + adviceAcc(A, 95) + '%</small>' : '') : '조언 — <b>' + accT(adviceAcc(A, 0)) + '</b>' + (A.int < 95 ? ' <small>· 지력 95인 상대에게는 ' + accT(adviceAcc(A, 95)) + '</small>' : '')) + '</p>")
s = rep(s, "' 어렵겠습니다.</b>' : ''), '적중률 ' + adv1.acc + '%', 'adv advn');", "' 어렵겠습니다.</b>' : ''), adv1 ? accT(adv1.acc) : '', 'adv advn');")
# 군사의 추천(v0.18): 보통 공격과 쓸 수 있는 전법 가운데 '주는 피해 − 받는 반격'의 기대값이 가장 큰 것에 薦. 전법은 보통 공격보다 5% 넘게 나을 때만 권한다. 군사가 없으면 추천도 없다
s = rep(s, "    var chOk = challengeTargets(u).some(function (x) { return x.u === t.u; }), chW = ",
"""    var advR = facAdv(u.f);
    if (advR && d <= rg) {
      var N0 = attackExpect(u, t.u), recA = out[0], recV = (N0.dealt - N0.recv) * 1.05;
      out.forEach(function (a0) { if (a0.kind !== 'tactic' || !a0.ok) return; var X0 = tacticExpect(u, t.u, a0.tac), v0 = X0.dealt - X0.recv; if (v0 > recV) { recV = v0; recA = a0; } });
      if (recV > 0) recA.rec = true;
    }
    var chOk = challengeTargets(u).some(function (x) { return x.u === t.u; }), chW = """)
s = rep(s, "          if (adv1) h += sayRow(adv1.adv, (ys.length ? ",
           "          var recA = null; st.acts.forEach(function (a0) { if (a0.rec) recA = a0; });\n"
           "          var advO = adv1 ? adv1.adv : (recA ? facAdv(x.f) : null);\n"
           "          if (advO) h += sayRow(advO, (recA ? '<b class=\"rc\">' + recA.label + josa(recA.label, '이가').slice(-1) + ' 가장 낫겠습니다.</b> ' : '') + (ys.length ? ")
s = rep(s, "(a.fx ? '<small class=\"fx\">' + a.fx + '</small>' : '') + (a.sub ? '<small>' + a.sub + '</small>' : '') + '</button>'; }", "(a.fx ? '<small class=\"fx\">' + a.fx + '</small>' : '') + (a.sub ? '<small>' + a.sub + '</small>' : '') + (a.rec ? '<i class=\"rec\" title=\"군사의 추천\">薦</i>' : '') + '</button>'; }")      # 薦은 맨 뒤에(단추의 글은 이름으로 시작한다)
# 지금 할 일
s = rep(s, "s: hs.slice(0, 3).map(function (x) { return x.t.n + ' ' + x.p + '%'; }).join(' · '),", "s: hs.slice(0, 3).map(function (x) { return x.t.n + ' ' + pcT(x.p); }).join(' · '),")
s = rep(s, "return x.o.n + ' 충성 ' + x.o.loy + ' (' + x.r.p + '%)'; }", "return x.o.n + ' 충성 ' + x.o.loy + ' (' + (UI.pct ? x.r.p + '%' : '떠날 낌새 ' + oddsWord(x.r.p)) + ')'; }")
# 대상에게 할 수 있는 일
s = rep(s, "(d > rg ? '사거리 밖' : '숲에서는 불가') : '<em class=\"pc\">' + od.ok + '%</em> · 기력 ' + tac.cost));",
           "(d > rg ? '사거리 밖' : '숲에서는 불가') : '<em class=\"pc\">' + pcG(od.ok) + '</em> · 기력 ' + tac.cost));")
s = rep(s, "'응할 확률 <em class=\"pc\">' + challengeChance(u, t.u) + '%</em> · 무력 ' + chW)", "'응할 확률 <em class=\"pc\">' + pcT(challengeChance(u, t.u)) + '</em> · 무력 ' + chW)")
s = rep(s, "sub: inP ? '<em class=\"pc\">' + ployChance(u, pl, t.u) + '%</em>' + advMark(ployAdvice(u, pl, t))", "sub: inP ? '<em class=\"pc\">' + pcG(ployChance(u, pl, t.u)) + '</em>' + advMark(ployAdvice(u, pl, t))")
# 전법 풀이
s = rep(s, "      function sg(v) { return (v > 0 ? '+' : '') + v; }\n",
           "      function sg(v) { return UI.pct ? (v > 0 ? '+' : '') + v : (v > 0 ? (v >= 8 ? '▲▲' : '▲') : (v < 0 ? (v <= -8 ? '▼▼' : '▼') : '–')); }      // v0.18: 말로 볼 때는 보탬·깎임을 화살표로\n")
s = rep(s, "        '<div class=\"odds\"><span class=\"g\"><i>대성공</i><b>' + od.crit + '%</b></span><span><i>성공</i><b>' + (od.ok - od.crit) + '%</b></span><span class=\"f\"><i>실패</i><b>' + (100 - od.ok) + '%</b></span></div>';",
           "        (UI.pct ? '<div class=\"odds\"><span class=\"g\"><i>대성공</i><b>' + od.crit + '%</b></span><span><i>성공</i><b>' + (od.ok - od.crit) + '%</b></span><span class=\"f\"><i>실패</i><b>' + (100 - od.ok) + '%</b></span></div>'\n"
           "          : '<div class=\"odds w\"><span><i>통할 가능성</i><b>' + pcG(od.ok) + '</b></span><span class=\"g\"><i>대성공</i><b>' + (od.sure ? '통하면 반드시' : pcT(od.crit)) + '</b></span></div>' + eyeNote());")
s = rep(s, "'<div class=\"tl\"><i>성공</i><span>' + tac.fx + (c0 ? ' — <b>' + c0 + '%</b>' : '') + '</span></div>' +", "'<div class=\"tl\"><i>성공</i><span>' + tac.fx + (c0 ? ' — <b>' + pcT(c0) + '</b>' : '') + '</span></div>' +")
s = rep(s, "'<div class=\"tl g\"><i>대성공</i><span>' + tac.gfx + (c1 && c1 < 100 ? ' — <b>' + c1 + '%</b>' : '') + '</span></div></div>';", "'<div class=\"tl g\"><i>대성공</i><span>' + tac.gfx + (c1 && c1 < 100 ? ' — <b>' + pcT(c1) + '</b>' : '') + '</span></div></div>';")
s = rep(s, "        '<p class=\"sum\">성공률 ' + od.ok + '% = 적성 ' + P.apt + ' · 무장 ' + sg(P.stat)", "        '<p class=\"sum\">' + (UI.pct ? '성공률 ' + od.ok + '% = 적성 ' + P.apt : '통할 가능성 ' + pcT(od.ok) + ' ← 적성 ' + uApt(u)) + ' · 무장 ' + sg(P.stat)")
# 결과 한 줄
s = rep(s, "    else msg += res.ploy + ' 실패 (성공률 ' + res.p + '%)'", "    else msg += res.ploy + ' 실패 (' + pcWas(res.p, '성공률') + ')'")
s = rep(s, "    if (res.fail && res.pOk !== undefined) msg += ' (성공률 ' + res.pOk + '%)';", "    if (res.fail && res.pOk !== undefined) msg += ' (' + pcWas(res.pOk, '성공률') + ')';")
s = rep(s, "' 일기토를 받지 않았습니다 — 기력 -' + res.mor + ' (응할 확률 ' + res.p + '%)', 3400);", "' 일기토를 받지 않았습니다 — 기력 -' + res.mor + ' (' + pcWas(res.p, '응할 확률') + ')', 3400);")
# 설전 · 담판
s = rep(s, "sub: t.n + ' 등용 · 그냥 권하면 ' + S.rp + '%',", "sub: t.n + ' 등용 · 그냥 권하면 ' + pcT(S.rp),")
s = rep(s, "' 담판 · 그냥 청하면 ' + S.dp + '%',", "' 담판 · 그냥 청하면 ' + pcT(S.dp),")
# 출병 요청
s = rep(s, "(x.why ? x.why : '받아들일 확률 최고 <b>' + best(x.f).p + '%</b> · 병력 '", "(x.why ? x.why : '받아들일 확률 ' + pcBest(best(x.f).p) + ' · 병력 '")
s = rep(s, "rt: function (o) { return '<b>' + aimTerms(me, t, x, o).p + '%</b>'; }, rtHead: '받아들일 확률',", "rt: function (o) { return '<b>' + pcT(aimTerms(me, t, x, o).p) + '</b>'; }, rtHead: '받아들일 확률',")
s = rep(s, "return '받아들일 확률 <b>' + q.p + '%</b> · 행동력 ' + AP.treaty", "return '받아들일 확률 <b>' + pcG(q.p) + '</b> · 행동력 ' + AP.treaty")
s = rep(s, "' 뒤에 다시 (받아들일 확률 ' + r.p + '%)', 4200); }", "' 뒤에 다시 (' + pcWas(r.p, '받아들일 확률') + ')', 4200); }")
# 정전 · 동맹
s = rep(s, "    return '받아들일 확률 최고 <em class=\"pc\">' + bestEnvoy(kind).p + '%</em> · 행 ' + AP.treaty;", "    return '받아들일 확률 ' + (UI.pct ? '최고 ' : '') + '<em class=\"pc\">' + pcT(bestEnvoy(kind).p) + '</em> · 행 ' + AP.treaty;")
s = rep(s, "rt: function (o) { return '<b>' + dipChance(me, t, kind, o) + '%</b>'; }, rtHead: '받아들일 확률',", "rt: function (o) { return '<b>' + pcT(dipChance(me, t, kind, o)) + '</b>'; }, rtHead: '받아들일 확률',")
s = rep(s, "return '받아들일 확률 <b>' + x.p + '%</b> · ' + PACT_NAME[kind]", "return '받아들일 확률 <b>' + pcG(x.p) + '</b> · ' + PACT_NAME[kind]")
# 등용
s = rep(s, "(idle ? bestM(t) + '최고 <b>' + bestP(t) + '%</b>' : '')", "(idle ? bestM(t) + pcBest(bestP(t)) : '')")
s = rep(s, "(idle ? (L[i].p ? bestM(t) : '') + '최고 <b>' + L[i].p + '%</b>' + (L[i].p ? tieSub(t, false) : '') : '')", "(idle ? (L[i].p ? bestM(t) : '') + pcBest(L[i].p) + (L[i].p ? tieSub(t, false) : '') : '')")
s = rep(s, "return advMark(recruitAdvice(b, o, t)) + '<b>' + x.p + '%</b>' + (x.tie ?", "return advMark(recruitAdvice(b, o, t)) + '<b>' + pcT(x.p) + '</b>' + (x.tie ?")
s = rep(s, "return '성공률 <b>' + x.p + '%</b>' + (farT ? ' · 충성 ' + t.loy : '')", "return '성공률 <b>' + pcG(x.p) + '</b>' + (farT ? ' · 충성 ' + t.loy : '')")

# ── 메뉴: 확률 표시(말 ↔ 숫자) ──
s = rep(s, "<button class=\"cmd\" type=\"button\" data-a=\"spd\"><b>열흘 재생</b><small>' + SPEEDS[UI.pspeed][0] + '</small></button>",
           "<button class=\"cmd\" type=\"button\" data-a=\"spd\"><b>열흘 재생</b><small>' + SPEEDS[UI.pspeed][0] + '</small></button><button class=\"cmd\" type=\"button\" data-a=\"pct\"><b>확률 표시</b><small>' + (UI.pct ? '숫자(%)' : '말로 가늠') + '</small></button>")
s = rep(s, "      help: function () { showHelp(); },\n      share: function () { shareGame(); },",
           "      pct: function () { UI.pct = !UI.pct; saveOpts(); toast(UI.pct ? '확률을 숫자(%)로 보여 줍니다' : '확률을 말로 가늠해 보여 줍니다 — 높음 · 반반 · 낮음', 2400); refreshDialog(); refreshSheet(); },\n      help: function () { showHelp(); },\n      share: function () { shareGame(); },")
s = rep(s, "talk: UI.talk !== false, voice: UI.voice !== false }));", "talk: UI.talk !== false, voice: UI.voice !== false, pct: !!UI.pct }));")
s = rep(s, "    if (o.voice === false) UI.voice = false;\n", "    if (o.voice === false) UI.voice = false;\n    if (o.pct === true) UI.pct = true;                         // v0.18: 확률을 숫자로(기본은 말)\n")
# ── 도움말 ──
s = rep(s, "  '<h3>충성과 인연</h3><p>군주와 <b>인연</b>",
"""  '<h3>무장 카드와 특기</h3><p>어느 창에서든 <b>무장의 얼굴을 누르면</b> 그 무장의 능력 · 병종 적성 · 특기 풀이 · 있는 곳이 겹쳐 뜹니다. ×나 바깥을 누르면 닫히고, 하던 일(무장 고르기 · 일기토 등)은 그대로 남습니다. 목록의 특기 이름 옆에는 무엇을 하는 특기인지 한 줄이 붙고, 무장을 고르는 표에는 줄마다 <b>병종 적성</b>(창 · 극 · 노 · 기 · 병기)과 특기가 함께 보입니다.</p>' +
  '<h3>가늠 — 확률을 말로</h3><p>성공할 가능성은 숫자 대신 <b>매우 높음 · 높음 · 반반 · 낮음 · 매우 낮음</b>과 눈금 다섯 칸으로 보입니다. 가늠하는 이는 군사와 군주 가운데 지력이 높은 쪽입니다 — 그 지력이 ' + ODDS_FINE + ' 미만이면 <b>높은 듯 · 반반인 듯 · 낮은 듯</b> 셋으로만 어림합니다. 적을 고르면 뜨는 단추 가운데 <i class="rec" style="position:static;display:inline-flex;transform:none">薦</i>이 붙은 것은 <b>군사가 권하는 수</b>입니다(주는 피해에서 받는 반격을 뺀 기대값이 가장 큰 것 — 군사가 없으면 권하지 않습니다). 숫자로 보고 싶으면 <b>메뉴 → 확률 표시</b>. 어느 쪽으로 보든 규칙의 확률은 같습니다.</p>' +
  '<h3>충성과 인연</h3><p>군주와 <b>인연</b>""")
s = rep(s, "  '<h3>계략과 상태 이상</h3><p>부대는 기력을 써서",
"""  '<p><b>전법 열두 가지</b> — 이름만 보고 효과가 떠오르도록 한자 두 글자로 지었습니다.</p><ul>' + ['spear', 'halberd', 'bow', 'cav'].map(function (k) { return '<li><b>' + UNIT_TYPES[k].name + '</b> — ' + TACTICS[k].map(function (t) { return t.name + ' <i class="hj">' + t.han + '</i> ' + t.tag; }).join(' / ') + '</li>'; }).join('') + '</ul>' +
  '<p><b>견인</b>은 한 칸 물러서며 적을 내가 섰던 자리로 끌어당깁니다 — 숲 · 언덕에 버틴 적을 끌어내거나, 아군이 둘러쌀 자리로 데려올 때 씁니다. 내 뒤가 막혔거나(산 · 부대 · 거점) 불타고 있으면 끌지 못합니다(피해와 반격 없음은 그대로).</p>' +
  '<h3>계략과 상태 이상</h3><p>부대는 기력을 써서""")
wr('src/ui_panels.js', s)

# ───────────────────────── duel.js ─────────────────────────
s = rd('src/duel.js')
s = rep(s, "return '<i class=\"du-por' + (sceneUrl(o.por) ? ' sc' : '') + '\"' + (u ? ", "return '<i class=\"du-por' + (sceneUrl(o.por) ? ' sc' : '') + '\"' + (typeof oidAttr === 'function' ? oidAttr(o) : '') + (u ? ")
s = rep(s, "<small>읽기 ' + h.p + '%</small>'", "<small>읽기 ' + (typeof pcT === 'function' ? pcT(h.p) : h.p + '%') + '</small>'")
wr('src/duel.js', s)

# ───────────────────────── ui3d.js: 선택지의 처음 값 ─────────────────────────
s = rd('src/ui3d.js')
s = rep(s, "sound: true, music: true, hide: -1, play: null, pspeed: 1 };", "sound: true, music: true, hide: -1, play: null, pspeed: 1, pct: false };      // pct(v0.18): 확률을 숫자로 보는가 — 기본은 말")
wr('src/ui3d.js', s)

# ───────────────────────── style.css ─────────────────────────
s = rd('src/style.css')
s += """
/* ── v0.18 무장 카드(얼굴을 누르면 겹쳐 뜬다) ── */
[data-oid] { cursor: pointer; }
#ocard { position: absolute; inset: 0; z-index: 70; display: none; align-items: center; justify-content: center; padding: max(14px, env(safe-area-inset-top)) 12px max(14px, env(safe-area-inset-bottom)); background: #1b1a1885; }
#ocard.on { display: flex; animation: ocIn .16s ease-out; }
@keyframes ocIn { from { opacity: 0; } to { opacity: 1; } }
.oc { width: 100%; max-width: 430px; max-height: 100%; display: flex; flex-direction: column; background-color: var(--paper); background-image: var(--hanji, none); border: 1.5px solid var(--ink); border-radius: 3px; box-shadow: 0 0 0 3px var(--paper), 0 0 0 4px var(--line-2), 6px 8px 0 #1b1a1833; }
.oc .dlg-h { flex: none; }
.oc-b { overflow-y: auto; -webkit-overflow-scrolling: touch; padding: 12px 14px 14px; }
.oc-b > * + * { margin-top: 10px; }
.oc-b .skp, .dlg-b .skp { line-height: 1.5; }
.note.ocu b { color: var(--ink); }
/* ── v0.18 특기의 짧은 풀이 · 고르는 표의 둘째 줄(병종 적성 + 특기) ── */
.row .nm small.skg { font: 500 11px var(--font-body); color: var(--ink-2); margin-left: 5px; }
.tr { grid-template-rows: auto auto; row-gap: 0; padding-top: 4px; padding-bottom: 5px; }
.tr > .por { grid-row: 1 / 3; align-self: center; }
.tr .c-2 { grid-column: 2 / -1; display: flex; align-items: baseline; gap: 10px; min-width: 0; margin-top: -3px; font-size: 11.5px; color: var(--dim); }
.tr .c-2 .ap5 { display: inline-flex; gap: 7px; flex: none; }
.tr .c-2 .sk2 { min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: var(--ink-2); }
.tr .c-2 .sk2 b { color: var(--seal); font-weight: 700; margin-right: 2px; }
/* ── v0.18 가늠(확률을 말로): 눈금 다섯 칸 ── */
.odg { display: inline-flex; gap: 2px; margin-left: 5px; vertical-align: 1px; }
.odg u { width: 5px; height: 9px; border: 1px solid currentColor; border-radius: 1px; opacity: .45; text-decoration: none; }
.odg u.on { background: currentColor; opacity: 1; }
.odg.dim u.on { opacity: .62; }
.odg.lv1 u.on, .odg.lv2 u.on { background: var(--seal); border-color: var(--seal); }
.act.pri .odg u.on, .act:active .odg u.on { background: currentColor; border-color: currentColor; }
.tacs .odds.w { display: grid; grid-template-columns: 1.3fr 1fr; }
.tacs .odds.w b { font-size: 17px; }
.tacs .odds i.odg { display: inline-flex; color: var(--ink); margin-left: 6px; vertical-align: 2px; }
.tacs .odds i.odg u { width: 6px; height: 11px; }
/* 군사의 추천 */
.act { position: relative; }
.act .rec { position: absolute; top: 3px; right: 3px; width: 17px; height: 17px; display: flex; align-items: center; justify-content: center; font: 900 11px var(--font-display); font-style: normal; color: var(--seal-ink); background: var(--seal); border: 1px solid var(--seal-2); border-radius: 2px; box-shadow: 1px 1px 0 #1b1a1833; }
.act.pri .rec { background: var(--paper); color: var(--seal); }
.say b.rc { color: var(--ink); }
.note.eye { margin-top: 6px; }
.note.eye small { display: block; color: var(--dim); }
"""
wr('src/style.css', s)
print('p3_ui18: ok')
