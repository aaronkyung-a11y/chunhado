# v0.9.3 (2/…): 대화창 — 군사의 말 · 업무 진행 · 군사 임명
#  요청: "군사의 말이 대화창으로 뜨게해서 더 잘 보이게, 군사 임명을 할 수 있도록. 그리고 어떤 업무를 진행시킬 때, 대화창이 뜨면 좋겠다."
#  - 대화창(#talk): 초상 + 이름 + 한마디 + 결과 한 줄. 화면 위쪽에 떴다가 저절로 사라진다(누르면 바로 닫힘). 명령의 흐름을 막지 않는다.
#  - 업무 진행: 징병·순찰·훈련·생산·탐색·등용·포상·이동·건설·합병·출진·수송을 시키면 맡은 무장(등용·포상은 상대)이 한마디 하고, 그 아래 결과가 한 줄로 붙는다(전에는 글자만 뜨는 알림 줄).
#    말투는 군주 · 무인(무력이 지력보다 10 넘게 높고 70 이상) · 문관 셋. 이름난 무장 몇은 제 말이 있다.
#  - 군사의 말: ① STATUS 창 맨 위에 군사의 초상과 지금 가장 급한 일 한마디(누르면 그 일로) + [임명] 단추 ② 내 차례가 시작될 때 그 한마디가 대화창으로 ③ 등용할 무장을 고르는 표의 아래와
#    계략을 쓸 수 있는 대상을 골랐을 때의 부대 창에 초상과 함께 "통할 것입니다 / 어렵겠습니다" ④ 조언이 틀렸으면 결과 뒤에 한마디
#  - 군사 임명: STATUS 창의 [임명] → '군사 임명' 창(후보마다 [임명] 단추). 임명하면 새 군사가 대화창으로 답한다. 군사가 없으면 STATUS 창에 붉게 알린다.
#  - 메뉴에 '대화창 켜짐/꺼짐'(끄면 전처럼 알림 줄만).
#  규칙(core.js)은 건드리지 않는다.
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)

# ---------------------------------------------------------------- index.html
p = 'src/index.html'; s = io.open(p, encoding='utf-8').read()
s = rep(s, '  <div id="toast" role="status"></div>\n', '  <div id="talk" role="status"></div>\n  <div id="toast" role="status"></div>\n')
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- ui_panels.js
p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()

# ---- 1. 대화창과 말
s = rep(s, "function showSheet(s) { SHEET = s;", '''/* ---------- 대화창(v0.9.3) ----------
   초상 + 이름 + 한마디(+ 결과 한 줄). 화면 위쪽에 떴다가 저절로 사라지고, 누르면 바로 닫힌다. 명령의 흐름을 막지 않는다.
   끄면(UI.talk === false) 결과 한 줄만 전처럼 알림 줄로 나온다. */
var talkT = 0, TALK = null;
function roleOf(o) { return isLord(o) ? '군주' : (o.f >= 0 && facAdv(o.f) === o ? '군사' : ''); }
function talkHide() { clearTimeout(talkT); TALK = null; var t = $('talk'); if (t) t.classList.remove('on'); }
function talk(o, say, sub, ms) {
  if (!o || UI.talk === false) { var m0 = String(sub || say || '').replace(/<[^>]*>/g, ' ').replace(/\\s+/g, ' ').trim(); if (m0) toast(m0, ms); return; }      // 꺼 두었으면 결과 한 줄만 알림 줄로
  var t = $('talk'), rl = roleOf(o);
  t.innerHTML = porTag(o, 'md') + '<div class="tk-tx"><div class="tk-who"><b>' + o.n + '</b>' + (rl ? '<em>' + rl + '</em>' : '') + (o.f >= 0 ? facChip(o.f) : '') + '</div><div class="tk-say">' + say + '</div>' + (sub ? '<div class="tk-sub">' + sub + '</div>' : '') + '</div>';
  t.classList.add('on'); $('toast').classList.remove('on');
  TALK = { o: o.id, say: say, sub: sub || '' };
  clearTimeout(talkT); talkT = setTimeout(talkHide, ms || Math.max(2600, Math.min(5200, 1500 + (say.length + (sub ? sub.length : 0)) * 70)));
}
/* 말투: 군주(L) · 무인(W: 무력이 지력보다 10 넘게 높고 70 이상) · 문관(C) */
function toneOf(o) { return isLord(o) ? 'L' : (o.war >= 70 && o.war > o.int + 10 ? 'W' : 'C'); }
var SAY = {
  draft:    { W: ['장정들을 모아 오겠소!', '싸울 놈들을 긁어모으겠소.'], C: ['장정을 모으겠습니다.', '고을마다 방을 붙이겠습니다.'], L: ['내가 직접 병사를 모으겠다.'] },
  patrol:   { W: ['수상한 놈은 그냥 두지 않겠소.', '성 안을 한 바퀴 돌고 오겠소.'], C: ['성 안을 두루 살피겠습니다.', '민심을 다독이겠습니다.'], L: ['백성의 삶을 내 눈으로 보겠다.'] },
  train:    { W: ['단단히 조련하겠소!', '군기를 바짝 잡겠소.'], C: ['군기를 바로잡겠습니다.', '진법을 익히게 하겠습니다.'], L: ['함께 땀을 흘리자.'] },
  produce:  { W: ['{x}, 넉넉히 마련하겠소.'], C: ['{x}{을} 넉넉히 마련하겠습니다.', '장인들을 독려하겠습니다.'], L: ['{x}{을} 마련하라.'] },
  develop:  { W: ['{x}? 맡겨만 주시오.', '{x}{을} 세우겠소.'], C: ['{x}{을} 세우겠습니다.', '곧 {x}{을} 올리겠습니다.'], L: ['{x}{을} 짓도록 하라.'] },
  merge:    { W: ['{x}{을} 더 크게 키우겠소.'], C: ['{x}{을} 넓히겠습니다.'], L: ['{x}{을} 넓히도록 하라.'] },
  found:    { W: ['{x}{이라} 하는 자를 데려왔소.'], C: ['쓸 만한 인물을 찾았습니다. {x}입니다.'], L: ['좋은 인물을 만났다. {x}{이라} 한다.'] },
  gold:     { W: ['묻혀 있던 재물을 찾았소!'], C: ['숨겨진 재물을 찾았습니다.'], L: ['뜻밖의 재물을 얻었다.'] },
  nothing:  { W: ['허탕이오…'], C: ['면목 없습니다. 아무도 찾지 못했습니다.'], L: ['이번에는 헛걸음이었다.'] },
  joined:   { W: ['이 한 몸, {x} 공께 맡기겠소.', '{x} 공을 따르겠소!'], C: ['미력하나마 힘을 보태겠습니다.', '{x} 공을 모시겠습니다.'], L: ['…'] },
  refused:  { W: ['두 주인을 섬길 수는 없소.', '돌아가시오.'], C: ['뜻은 고마우나 사양하겠습니다.', '아직은 때가 아닙니다.'], L: ['…'] },
  reward:   { W: ['이 은혜, 싸움으로 갚겠소!'], C: ['황공합니다. 더욱 힘쓰겠습니다.'], L: ['…'] },
  move:     { W: ['곧 떠나겠소.'], C: ['곧 떠나겠습니다.'], L: ['자리를 옮기겠다.'] },
  deploy:   { W: ['출진이다! 나를 따르라!', '적의 목을 베어 오겠소!'], C: ['출진합니다. 무운을 빌어 주십시오.', '군을 이끌고 나가겠습니다.'], L: ['내가 직접 나서겠다. 전군, 출진!'] },
  trans:    { W: ['물자는 내가 지키겠소.'], C: ['물자를 무사히 전하겠습니다.'], L: ['내가 직접 실어 가겠다.'] },
  advisor:  { W: ['머리 쓰는 일이라… 힘껏 해 보겠소.'], C: ['미력하나마 지혜를 다하겠습니다.', '삼가 명을 받들겠습니다.'], L: ['…'] }
};
var SAY_OWN = {                                   // 이름난 무장의 제 말
  '장비': { deploy: ['연인 장익덕이 나간다! 길을 비켜라!'], train: ['게으름 피우는 놈은 내가 가만두지 않겠소!'] },
  '관우': { deploy: ['관운장, 출진하오.'], reward: ['형님의 은혜, 잊지 않겠소.'] },
  '여포': { deploy: ['천하에 이 여포를 막을 자가 있느냐!'] },
  '조운': { deploy: ['상산의 조자룡, 나갑니다!'] },
  '조조': { deploy: ['내가 간다. 따르라!'], found: ['인재로다! {x}{을} 얻었구나.'] },
  '유비': { patrol: ['백성이 편안해야 나라가 선다.'], found: ['반가운 분을 만났소. {x} 공이오.'] },
  '손책': { deploy: ['강동의 호랑이가 나간다!'] },
  '제갈량': { advisor: ['삼가 명을 받들겠습니다. 몸이 다할 때까지.'] },
  '초선': { reward: ['과분한 은혜이옵니다.'] }
};
function sayLine(o, key, x) {
  var own = SAY_OWN[o.n] && SAY_OWN[o.n][key], L = own || (SAY[key] && (SAY[key][toneOf(o)] || SAY[key].C)) || ['…'];
  var t = L[Math.floor(Math.random() * L.length)];                                   // 화면의 말뿐이라 판의 주사위(rnd)는 쓰지 않는다
  if (x !== undefined) t = t.replace(/\\{x\\}\\{을\\}/g, josa(String(x), '을를')).replace(/\\{x\\}\\{이라\\}/g, x + (hasBatchim(String(x)) ? '이라' : '라')).replace(/\\{x\\}/g, x);
  return t;
}
function hasBatchim(w) { var c = w.charCodeAt(w.length - 1); return c >= 0xAC00 && c <= 0xD7A3 && (c - 0xAC00) % 28 !== 0; }
/* 군사의 말을 초상과 함께 한 줄로(창 안에 넣는 꼴) */
function sayRow(o, say, sub, cls) { return '<div class="say' + (cls ? ' ' + cls : '') + '">' + porTag(o, 'sm') + '<div><b>' + o.n + '</b> <span>' + say + '</span>' + (sub ? '<small>' + sub + '</small>' : '') + '</div></div>'; }
function advSay(a, what, yes, no) { return a ? sayRow(a.adv, (what ? what + ' ' : '') + '<b class="' + (a.says ? 'ok' : 'bad') + '">' + (a.says ? (yes || '통할 것입니다.') : (no || '어렵겠습니다.')) + '</b>', '적중률 ' + a.acc + '%', 'adv') : ''; }
/* 조언이 빗나갔을 때 군사가 덧붙이는 말('' = 덧붙일 말 없음) */
function advAfter(a, ok) { return (a && a.says !== ok) ? (a.says ? '…제 헤아림이 모자랐습니다.' : '…뜻밖입니다. 제가 잘못 보았습니다.') : ''; }
function showSheet(s) { SHEET = s;''')

# ---- 2. 명령의 결과: 맡은 무장이 한마디(who, key, x)
s = rep(s, """function done(res, msg, snd) {
  if (!res.ok) { toast(res.msg); return false; }
  if (snd) sfx(snd);
  if (msg) toast(msg);""",
"""function done(res, msg, snd, who, key, x) {
  if (!res.ok) { toast(res.msg); return false; }
  if (snd) sfx(snd);
  if (who && key) talk(who, sayLine(who, key, x), msg); else if (msg) toast(msg);""")
s = rep(s, "return done(r, r.ok ? '징병 +' + fmt(r.n) + '명' : '', 'drums'); });", "return done(r, r.ok ? '징병 +' + fmt(r.n) + '명' : '', 'drums', os[0], 'draft'); });")
s = rep(s, "return done(r, r.ok ? '치안 +' + r.n : '', 'step'); });", "return done(r, r.ok ? '치안 +' + r.n : '', 'step', os[0], 'patrol'); });")
s = rep(s, "return done(r, r.ok ? '기력 +' + r.n : '', 'shout'); });", "return done(r, r.ok ? '기력 +' + r.n : '', 'shout', os[0], 'train'); });")
s = rep(s, "return done(r, r.ok ? k[1] + ' +' + fmt(r.n) : '', 'hammer'); });", "return done(r, r.ok ? k[1] + ' +' + fmt(r.n) : '', 'hammer', os[0], 'produce', k[1]); });")
s = rep(s, """      if (r.found !== undefined) { sfx('drum'); done(r, josa(off(r.found).n, '을를') + ' 찾았습니다'); }
      else if (r.gold) done(r, '금 ' + josa(String(r.gold), '을를') + ' 찾았습니다');
      else done(r, '아무것도 찾지 못했습니다');""",
"""      if (r.found !== undefined) { sfx('drum'); done(r, josa(off(r.found).n, '을를') + ' 찾았습니다', '', os[0], 'found', off(r.found).n); }
      else if (r.gold) done(r, '금 ' + josa(String(r.gold), '을를') + ' 찾았습니다', '', os[0], 'gold');
      else done(r, '아무것도 찾지 못했습니다', '', os[0], 'nothing');""")
# 등용: 상대가 답한다. 군사의 조언이 빗나갔으면 한 줄 덧붙는다
s = rep(s, """          var r = cmdRecruit(b, os[0].id, t.id); if (r.ok && r.joined) sfx('cheer');
          var ok = done(r, r.ok ? (r.joined ? (r.far ? josa(t.n, '이가') + ' ' + facName(r.from) + '군을 떠나 합류했습니다!' : josa(t.n, '이가') + ' 합류했습니다!') : josa(t.n, '이가') + ' 거절했습니다' + (r.far ? ' (충성 +' + POACH.up + ')' : '')) : '');""",
"""          var a0 = recruitAdvice(b, os[0], t), r = cmdRecruit(b, os[0].id, t.id); if (r.ok && r.joined) sfx('cheer');
          var miss = r.ok ? advAfter(a0, !!r.joined) : '';
          var ok = done(r, r.ok ? (r.joined ? (r.far ? josa(t.n, '이가') + ' ' + facName(r.from) + '군을 떠나 합류했습니다!' : josa(t.n, '이가') + ' 합류했습니다!') : josa(t.n, '이가') + ' 거절했습니다' + (r.far ? ' (충성 +' + POACH.up + ')' : '')) + (miss ? '<i class="tk-adv">군사 ' + a0.adv.n + ': ' + miss + '</i>' : '') : '', '', t, r.joined ? 'joined' : 'refused', G.factions[G.player].name);""")
s = rep(s, "    on: { r: function (el) { var r = cmdReward(b, +el.getAttribute('data-v')); if (!r.ok) return toast(r.msg); sfx('coin'); toast('충성 +' + r.n); refreshDialog(); refreshSheet(); refreshHud(); } }",
           "    on: { r: function (el) { var ro = off(+el.getAttribute('data-v')), r = cmdReward(b, ro.id); if (!r.ok) return toast(r.msg); sfx('coin'); talk(ro, sayLine(ro, 'reward'), '충성 +' + r.n + ' (' + ro.loy + ')'); refreshDialog(); refreshSheet(); refreshHud(); } }")
s = rep(s, "done(r, r.ok ? os.length + '명 출발 — ' + days(r.turns) + ' 뒤 도착' : ''); } }", "done(r, r.ok ? os.length + '명 출발 — ' + days(r.turns) + ' 뒤 도착' : '', '', os[0], 'move'); } }")
s = rep(s, "return done(r, r.ok ? F.name + ' 착공 — ' + days(r.turns) + ' 뒤 완공' : '', 'hammer'); });", "return done(r, r.ok ? F.name + ' 착공 — ' + days(r.turns) + ' 뒤 완공' : '', 'hammer', os[0], 'develop', F.name); });")
s = rep(s, "return done(r, r.ok ? F.name + ' Lv' + r.lv + '로 올랐습니다' : '', 'hammer'); });", "return done(r, r.ok ? F.name + ' Lv' + r.lv + '로 올랐습니다' : '', 'hammer', os[0], 'merge', F.name); });")
s = rep(s, "          if (alive(u)) { selectUnit(u); UI.sret = backToBase(b.id); toast(name + ' 출진', 1800); }",
           "          if (alive(u)) { selectUnit(u); UI.sret = backToBase(b.id); talk(uLeader(u), sayLine(uLeader(u), 'deploy'), name + ' 출진 — ' + UNIT_TYPES[u.type].name + ' ' + fmt(u.troops) + '명', 2600); }")
s = rep(s, "      closeDialog(); sfx('drum'); toast('수송대 출발 — 아군 거점에 들이면 물자가 합쳐집니다', 2600); syncScene(); selectUnit(r.unit); UI.sret = backToBase(b.id); afterAction();",
           "      closeDialog(); sfx('drum'); talk(uLeader(r.unit), sayLine(uLeader(r.unit), 'trans'), '수송대 출발 — 아군 거점에 들이면 물자가 합쳐집니다', 3200); syncScene(); selectUnit(r.unit); UI.sret = backToBase(b.id); afterAction();")

# ---- 3. 군사의 말: 등용할 무장을 고르는 표
s = rep(s, "        preview: function (os) { var a = recruitAdvice(b, os[0], t); return '성공률 <b>' + recruitChance(b, os[0], t) + '%</b>' + (farT ? ' · 충성 ' + t.loy : '') + (a ? '<br>' + advLine(a) : ''); } },",
           "        preview: function (os) { return '성공률 <b>' + recruitChance(b, os[0], t) + '%</b>' + (farT ? ' · 충성 ' + t.loy : ''); },\n        say: function (os) { return advSay(recruitAdvice(b, os[0], t), josa(t.n, '은는'), '응할 것입니다.', '응하지 않을 것입니다.'); } },")
s = rep(s, "      h += '</div>' + strip + '<div class=\"dlg-f\"><div class=\"pv\">'", "      h += '</div>' + strip + (opts.say && os.length ? '<div class=\"pksay\">' + opts.say(os) + '</div>' : '') + '<div class=\"dlg-f\"><div class=\"pv\">'")
# 부대 창: 계략을 쓸 수 있는 대상을 골랐을 때
s = rep(s, """          var adv1 = null; st.acts.forEach(function (a0) { if (a0.adv && !adv1) adv1 = a0.adv; });
          if (adv1) h += '<p class="note advn">군사 <b>' + adv1.adv.n + '</b> — <i class="adv y">○</i> 통함 · <i class="adv n">×</i> 어려움 <small>적중률 ' + adv1.acc + '%</small></p>';""",
"""          var adv1 = null, ys = [], ns = []; st.acts.forEach(function (a0) { if (!a0.adv) return; if (!adv1) adv1 = a0.adv; (a0.adv.says ? ys : ns).push(a0.label); });
          if (adv1) h += sayRow(adv1.adv, (ys.length ? '<b class="ok">' + ys.join('·') + josa(ys[ys.length - 1], '은는').slice(-1) + ' 통하겠' + (ns.length ? '으나' : '습니다.') + '</b> ' : '') + (ns.length ? '<b class="bad">' + ns.join('·') + josa(ns[ns.length - 1], '은는').slice(-1) + ' 어렵겠습니다.</b>' : ''), '적중률 ' + adv1.acc + '%', 'adv advn');""")
# 계략의 결과 뒤: 조언이 빗나갔으면 군사가 한마디
s = rep(s, """  var name = uName(u), res;
  if (a.kind === 'attack') res = unitAttack(u, t);
  else if (a.kind === 'tactic') res = unitTactic(u, a.tac, t);
  else res = unitPloy(u, a.ploy, t);
  if (!res.ok) { toast(res.msg); return; }""",
"""  var name = uName(u), res, pa = a.kind === 'ploy' ? (a.adv || null) : null;
  if (a.kind === 'attack') res = unitAttack(u, t);
  else if (a.kind === 'tactic') res = unitTactic(u, a.tac, t);
  else res = unitPloy(u, a.ploy, t);
  if (!res.ok) { toast(res.msg); return; }
  var miss = pa ? advAfter(pa, !!res.success) : '';""")
s = rep(s, """      if (fellB) fxFall(fellB, fellB.kind === 'gate' ? '점령' : '함락');
      toast(msg, 3200);""",
"""      if (fellB) fxFall(fellB, fellB.kind === 'gate' ? '점령' : '함락');
      if (miss) talk(pa.adv, miss, msg, 3600); else toast(msg, 3200);""")

# ---- 4. STATUS 창: 군사의 초상과 한마디 + [임명]
s = rep(s, """            '<button class="hm-adv" type="button" data-a="adv">군사 ' + (A ? '<b>' + A.n + '</b>' : '<b class="bad">없음</b>') + ' <span>▸</span></button></div>'""",
           """            '</div>'""")
s = rep(s, """      h += '<div class="sh-body"><div class="sec">지금 할 일' + (need ? ' <em class="cnt">' + need + '</em>' : '') + '</div><div class="todos">';""",
"""      var top = advTop(st.todo);
      h += '<div class="sh-body"><div class="hm-advp' + (A ? '' : ' none') + '">' + (A ? '<button class="hm-say" type="button" data-a="advgo"' + (top && top.go ? '' : ' disabled') + '>' + porTag(A, 'md') + '<span class="tx"><i>군사 <b>' + A.n + '</b></i><span>' + (top ? top.say : '…') + '</span></span></button>'
          : '<div class="hm-say"><i class="por md none"></i><span class="tx"><i>군사</i><span class="bad">군사가 없습니다. 임명하면 조언을 듣습니다.</span></span></div>') +
        '<button class="btn' + (A ? '' : ' pri') + ' hm-adv" type="button" data-a="adv">' + (A ? '바꾸기' : '임명') + '</button></div>' +
        '<div class="sec">지금 할 일' + (need ? ' <em class="cnt">' + need + '</em>' : '') + '</div><div class="todos">';""")
s = rep(s, "      adv: function () { showAdvisor(); },\n      peace: function () { showPeaceInfo(); }",
           "      adv: function () { showAdvisor(); },\n      advgo: function () { var t = advTop(st.todo); if (t && t.go) goTodo(t.go); },\n      peace: function () { showPeaceInfo(); }")
# 지금 가장 급한 일을 군사의 말로
s = rep(s, "function gotoBase(b, tab) {", """/* 군사의 한마디: '지금 할 일'의 맨 위(가장 급한 것)를 말로 옮긴다 → { say, go } */
function advTop(list) {
  for (var i = 0; i < list.length; i++) if (list[i].say) return list[i];
  return null;
}
function gotoBase(b, tab) {""")

# 할 일마다 말로 옮긴 꼴(say)
s = rep(s, "s: facName(es[0].f) + '군 ' + fmt(t) + '명 · ' + hdist(b.c, b.r, es[0].c, es[0].r) + '칸', go: ['unit', es[0].id], lb: '보기' });",
           "s: facName(es[0].f) + '군 ' + fmt(t) + '명 · ' + hdist(b.c, b.r, es[0].c, es[0].r) + '칸', go: ['unit', es[0].id], lb: '보기', say: b.n + ' 가까이 ' + facName(es[0].f) + '군 ' + es.length + '부대가 와 있습니다. 대비하십시오.' });")
s = rep(s, "t: uName(u) + ' — 적과 맞닿음', s: '', go: ['unit', u.id], lb: '명령' });", "t: uName(u) + ' — 적과 맞닿음', s: '', go: ['unit', u.id], lb: '명령', say: josa(uName(u), '이가') + ' 적과 맞닿아 있습니다. 명을 내리십시오.' });")
s = rep(s, "s: '', go: ['unit', u.id], lb: '보기', info: 1 });\n    if (unitOnFire(u)", "s: '', go: ['unit', u.id], lb: '보기', info: 1, say: josa(uName(u), '이가') + ' ' + statusName(u.status) + '에 빠졌습니다.' });\n    if (unitOnFire(u)")
s = rep(s, "t: uName(u) + ' — 불길 속', s: '', go: ['unit', u.id], lb: '보기', info: 1 });", "t: uName(u) + ' — 불길 속', s: '', go: ['unit', u.id], lb: '보기', info: 1, say: josa(uName(u), '이가') + ' 불길 속에 있습니다. 어서 빼내십시오.' });")
s = rep(s, "s: UNIT_TYPES[u.type].name + ' ' + fmt(u.troops) + '명', go: ['unit', u.id], lb: '명령' });", "s: UNIT_TYPES[u.type].name + ' ' + fmt(u.troops) + '명', go: ['unit', u.id], lb: '명령', say: josa(uName(u), '이가') + ' 명을 기다립니다.' });")
s = rep(s, "t: uName(u) + ' — 군량 ' + days(ft) + '분', s: '', go: ['unit', u.id], lb: '보기' });", "t: uName(u) + ' — 군량 ' + days(ft) + '분', s: '', go: ['unit', u.id], lb: '보기', say: uName(u) + '의 군량이 ' + days(ft) + '분뿐입니다.' });")
s = rep(s, "go: ['recruit', b.id], lb: '등용', info: 1 });", "go: ['recruit', b.id], lb: '등용', info: 1, say: b.n + '에서 ' + josa(hs[0].t.n, '을를') + ' 부르면 응할 것입니다.' });")
s = rep(s, "go: ['base', b.id, 'men'], lb: '포상', info: 1 });", "go: ['base', b.id, 'men'], lb: '포상', info: 1, say: rk[0].o.n + '의 마음이 흔들립니다. 포상으로 붙잡으십시오.' });")
s = rep(s, "      out.push({ ic: String(a.n), num: 1, t: b.n + ' — 쉬는 무장 ' + a.n + '명', s: a.tips.join(' · '), go: ['base', b.id, a.tab], lb: '열기' });",
           "      out.push({ ic: String(a.n), num: 1, t: b.n + ' — 쉬는 무장 ' + a.n + '명', s: a.tips.join(' · '), go: ['base', b.id, a.tab], lb: '열기', say: b.n + ' — ' + a.say });")
s = rep(s, "  } else out.push({ ic: '…', t: '행동력 부족 (' + F.ap + ') — 다음 턴에', s: '' });", "  } else out.push({ ic: '…', t: '행동력 부족 (' + F.ap + ') — 다음 턴에', s: '', say: '행동력이 다했습니다. 턴을 넘기시지요.' });")
s = rep(s, "t: '할 일을 모두 마쳤습니다', s: '', go: ['end'], lb: '턴 종료' });", "t: '할 일을 모두 마쳤습니다', s: '', go: ['end'], lb: '턴 종료', say: '할 일을 모두 마쳤습니다. 턴을 넘기시지요.' });")
# 거점의 권고를 말로
s = rep(s, "    if (b.order < 60) tips.push(['치안 ' + b.order + ' → 순찰', 'home']);", "    if (b.order < 60) tips.push(['치안 ' + b.order + ' → 순찰', 'home', '치안이 어지럽습니다. 순찰을 돌리십시오.']);")
s = rep(s, "    if (men) tips.push(['등용할 인재 ' + men + '명', 'men']);", "    if (men) tips.push(['등용할 인재 ' + men + '명', 'men', '부를 만한 인재가 ' + men + '명 있습니다. 등용하시지요.']);")
s = rep(s, "tips.push(['빈 부지 ' + empty + '곳 → 시설 건설', 'fac']);", "tips.push(['빈 부지 ' + empty + '곳 → 시설 건설', 'fac', '빈 부지가 ' + empty + '곳 있습니다. 시설을 지으시지요.']);")
s = rep(s, "tips.push(['징병', 'home']);", "tips.push(['징병', 'home', '병사를 더 모으시지요.']);")
s = rep(s, "    if (b.morale < 60 && b.troops >= 1000) tips.push(['기력 ' + b.morale + ' → 훈련', 'home']);", "    if (b.morale < 60 && b.troops >= 1000) tips.push(['기력 ' + b.morale + ' → 훈련', 'home', '군의 기력이 낮습니다. 훈련하십시오.']);")
s = rep(s, "    if (!tips.length) tips.push(['탐색으로 인재·재물 찾기', 'men']);", "    if (!tips.length) tips.push(['탐색으로 인재·재물 찾기', 'men', '탐색으로 인재를 찾아보시지요.']);")
s = rep(s, "    if (b.morale < 60 && b.troops >= 1000) tips.push(['기력 ' + b.morale + ' → 훈련', 'mil']);", "    if (b.morale < 60 && b.troops >= 1000) tips.push(['기력 ' + b.morale + ' → 훈련', 'mil', '군의 기력이 낮습니다. 훈련하십시오.']);")
s = rep(s, "    if (b.troops >= 1000) tips.push(['출진 가능', 'mil']);", "    if (b.troops >= 1000) tips.push(['출진 가능', 'mil', '군을 낼 수 있습니다.']);")
s = rep(s, "  return { n: n, tips: tips.slice(0, 2).map(function (t) { return t[0]; }), tab: tips[0][1] };", "  return { n: n, tips: tips.slice(0, 2).map(function (t) { return t[0]; }), tab: tips[0][1], say: tips[0][2] };")

# ---- 5. 군사 임명 창
s = rep(s, """      var A = facAdv(f), cs = advCandidates(f), i, h = dlgHead('군사') + '<div class="dlg-b"><p class="cap">등용·계략 전에 <i class="adv y">○</i> 통함 · <i class="adv n">×</i> 어려움으로 알려 줍니다. 지력이 높을수록 잘 맞습니다.</p>';""",
           """      var A = facAdv(f), cs = advCandidates(f), i, h = dlgHead('군사 임명') + '<div class="dlg-b"><p class="cap">군사는 등용·계략이 통할지 미리 말해 줍니다. 지력이 높을수록 잘 맞습니다.</p>';""")
s = rep(s, """      else h += '<p class="note">군사가 없습니다 — 아래에서 고르세요.</p>';
      h += '<div class="sec">바꾸기 <small>누르면 바뀝니다</small></div><div class="rows">';
      for (i = 0; i < cs.length; i++) { var o = cs[i], cur = A && A.id === o.id; h += offRow(o, { a: 'set', sel: cur, badge: cur ? '군사' : '', hi: 'int', rt: '지력 <b>' + o.int + '</b><br>' + (o.unit !== null ? '출진' : G.bases[o.st === 'travel' ? o.dest : o.loc].n) }); }""",
"""      else h += '<p class="note bad">군사가 없습니다 — 아래에서 임명하세요.</p>';
      h += '<div class="sec">후보 <em class="cnt">' + cs.length + '</em></div><div class="rows advl">';
      for (i = 0; i < cs.length; i++) {
        var o = cs[i], cur = A && A.id === o.id;
        h += '<div class="row' + (cur ? ' sel' : '') + '">' + porTag(o) + '<span class="mid"><span class="nm">' + o.n + (cur ? ' <em class="advt">군사</em>' : '') + '</span><span class="ds">지력 <b>' + o.int + '</b> · ' + (o.unit !== null ? '출진 중' : G.bases[o.st === 'travel' ? o.dest : o.loc].n) + '</span></span>' +
          (cur ? '<span class="rt hi">지금의 군사</span>' : '<button class="btn pri" type="button" data-a="set" data-v="' + o.id + '">임명</button>') + '</div>';
      }""")
s = rep(s, "    on: { set: function (el) { var o = off(+el.getAttribute('data-v')), r = setAdvisor(f, o.id); if (!r.ok) return toast(r.msg); sfx('ui'); toast(josa(o.n, '을를') + ' 군사로 삼았습니다 (지력 ' + o.int + ')'); refreshDialog(); refreshSheet(); } }\n  }, true);\n}",
           "    on: { set: function (el) { var o = off(+el.getAttribute('data-v')), r = setAdvisor(f, o.id); if (!r.ok) return toast(r.msg); sfx('ui'); talk(o, sayLine(o, 'advisor'), josa(o.n, '을를') + ' 군사로 삼았습니다 (지력 ' + o.int + ')'); refreshDialog(); refreshSheet(); } }\n  }, true);\n}")
s = rep(s, "    }, on: { adv: function () { var r = setAdvisor(G.player, o.id); if (!r.ok) return toast(r.msg); sfx('ui'); toast(josa(o.n, '을를') + ' 군사로 삼았습니다 (지력 ' + o.int + ')'); refreshDialog(); refreshSheet(); } }",
           "    }, on: { adv: function () { var r = setAdvisor(G.player, o.id); if (!r.ok) return toast(r.msg); sfx('ui'); talk(o, sayLine(o, 'advisor'), josa(o.n, '을를') + ' 군사로 삼았습니다 (지력 ' + o.int + ')'); refreshDialog(); refreshSheet(); } }")

# ---- 6. 내 차례가 시작될 때: 군사의 한마디가 대화창으로 (창 객체의 onClose: 그 창이 완전히 닫힐 때 한 번 부른다)
s = rep(s, "function closeDialog() { MSTACK.length = 0; MODAL = null; var m = $('modal'); m.classList.remove('on'); m.classList.remove('see'); $('app').classList.remove('seeing'); m.innerHTML = ''; paintRet(); }",
           "function closeDialog() { var d0 = MODAL; MSTACK.length = 0; MODAL = null; var m = $('modal'); m.classList.remove('on'); m.classList.remove('see'); $('app').classList.remove('seeing'); m.innerHTML = ''; paintRet(); if (d0 && d0.onClose) d0.onClose(); }")
s = rep(s, """  if (!n) { toast(dateStr() + ' — 조용한 열흘', 2200); return; }
  clearRet();""",
"""  if (!n) { toast(dateStr() + ' — 조용한 열흘', 2200); advBrief(1200); return; }
  clearRet();""")
s = rep(s, """function showReport(list) {""", """/* 내 차례가 시작될 때 군사가 지금 가장 급한 일을 말한다(창이 떠 있으면 닫힌 뒤에) */
function advBrief(wait) {
  var turn = G.turn;
  setTimeout(function () {
    if (!G || G.over || UI.play || G.turn !== turn || UI.briefT === turn) return;      // 한 턴에 한 번
    if (MODAL) { advBrief(700); return; }
    var A = facAdv(G.player), top = A ? advTop(todoList()) : null;
    UI.briefT = turn;
    if (!top || UI.talk === false) return;                                  // 대화창을 꺼 두었으면 차례 첫머리의 한마디도 띄우지 않는다(STATUS 창에는 그대로 있다)
    if (UI.briefSay === top.say && turn - UI.briefAt < 3) return;            // 같은 말을 턴마다 되풀이하지 않는다 — 한 달(세 턴)에 한 번만
    UI.briefSay = top.say; UI.briefAt = turn;
    talk(A, top.say, '', 4200);
  }, wait || 300);
}
function showReport(list) {""")
s = rep(s, """      return h + '</div><div class="dlg-f"><div class="pv">이제 <b>' + G.factions[G.player].name + '군</b>의 차례입니다</div><button class="btn pri" type="button" data-a="close">확인</button></div>';
    },
    on: { j:""", """      return h + '</div><div class="dlg-f"><div class="pv">이제 <b>' + G.factions[G.player].name + '군</b>의 차례입니다</div><button class="btn pri" type="button" data-a="close">확인</button></div>';
    },
    onClose: function () { advBrief(300); },
    on: { j:""")
s = rep(s, """        '</ul></div></div><div class="dlg-f"><div class="pv">도시 42곳을 모두 차지하면 천하통일</div><button class="btn pri" type="button" data-a="close">시작</button></div>';
    }, on: {}""", """        '</ul></div></div><div class="dlg-f"><div class="pv">도시 42곳을 모두 차지하면 천하통일</div><button class="btn pri" type="button" data-a="close">시작</button></div>';
    }, onClose: function () { advBrief(400); }, on: {}""")

s = rep(s, "  refreshHud(); showHome(); requestDraw(); playBgm(bgmForState());\n}", "  UI.briefT = undefined; UI.briefSay = ''; UI.briefAt = 0; talkHide();\n  refreshHud(); showHome(); requestDraw(); playBgm(bgmForState());\n  advBrief(900);                                               // 이어 하기로 들어왔을 때도 군사가 한마디\n}")

# ---- 7. 메뉴: 대화창 켜고 끄기 / 저장
s = rep(s, """<button class="cmd" type="button" data-a="snd"><b>효과음 ' + (UI.sound ? '켜짐' : '꺼짐') + '</b></button>""",
           """<button class="cmd" type="button" data-a="talk"><b>대화창 ' + (UI.talk === false ? '꺼짐' : '켜짐') + '</b></button><button class="cmd" type="button" data-a="snd"><b>효과음 ' + (UI.sound ? '켜짐' : '꺼짐') + '</b></button>""")
s = rep(s, "      snd: function () { UI.sound = !UI.sound; if (UI.sound) audioInit(); saveOpts(); refreshDialog(); },",
           "      talk: function () { UI.talk = UI.talk === false; if (UI.talk === false) talkHide(); saveOpts(); toast(UI.talk ? '대화창 켬 — 맡은 무장이 한마디 합니다' : '대화창 끔 — 결과만 알림 줄로', 2000); refreshDialog(); },\n      snd: function () { UI.sound = !UI.sound; if (UI.sound) audioInit(); saveOpts(); refreshDialog(); },")
s = rep(s, "JSON.stringify({ sound: UI.sound, music: UI.music, pspeed: UI.pspeed, home: HOME.open })", "JSON.stringify({ sound: UI.sound, music: UI.music, pspeed: UI.pspeed, home: HOME.open, talk: UI.talk !== false })")
s = rep(s, "    if (o.home === false) HOME.open = false;", "    if (o.home === false) HOME.open = false;\n    if (o.talk === false) UI.talk = false;")

# ---- 8. 도움말
s = rep(s, "'<h3>군사(軍師)</h3><p>세력마다 군사를 한 사람 둡니다(STATUS 창의 <b>군사</b> 단추, 또는 무장 창의 <b>군사로 삼기</b>).",
           "'<h3>군사(軍師)</h3><p>세력마다 군사를 한 사람 둡니다. <b>STATUS 창 맨 위</b>에 군사의 초상과 한마디가 있고, 그 옆의 <b>임명(바꾸기)</b> 단추로 고릅니다(무장 창의 <b>군사로 삼기</b>도 같습니다). 군사는 지금 가장 급한 일을 말해 주고 — 누르면 그 일로 갑니다 — 내 차례가 시작될 때도 대화창으로 알립니다.")
s = rep(s, "통할지 미리 말해 줍니다 — 무장을 고르는 표와 계략 단추의 <i class=\"adv y\">○</i>(통한다)·<i class=\"adv n\">×</i>(어렵다).",
           "통할지 미리 말해 줍니다 — 무장을 고르는 표 아래와 부대 창에 초상과 함께 \"통할 것입니다 / 어렵겠습니다\", 단추에는 <i class=\"adv y\">○</i>(통한다)·<i class=\"adv n\">×</i>(어렵다).")
s = rep(s, "'<h3>군사(軍師)</h3>", "'<h3>대화창</h3><p>명령을 내리면 맡은 무장이 화면 위쪽의 <b>대화창</b>에서 한마디 하고, 그 아래에 결과가 한 줄로 붙습니다(등용·포상은 상대가 답합니다). 잠깐 뒤 저절로 사라지고 누르면 바로 닫힙니다. 메뉴의 <b>대화창</b>으로 끌 수 있습니다 — 끄면 결과만 알림 줄로 나옵니다.</p>' +\n  '<h3>군사(軍師)</h3>")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- ui3d.js: 대화창을 누르면 닫힌다
p = 'src/ui3d.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "    $('app').classList.toggle('building', SPOT.on);", "    $('app').classList.toggle('building', SPOT.on);\n    if (SPOT.on && typeof talkHide === 'function') talkHide();       // 건설 자리를 볼 때는 앞서 뜬 대화창이 칸을 가리지 않게")
s = rep(s, "/* ---------- 건설 자리 비추기 ----------", "document.addEventListener('click', function (e) { var t = document.getElementById('talk'); if (t && t.classList.contains('on') && t.contains(e.target)) talkHide(); });      // 대화창: 누르면 닫힌다\n\n/* ---------- 건설 자리 비추기 ----------")
io.open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- style.css
p = 'src/style.css'; s = io.open(p, encoding='utf-8').read()
s += """
/* ---- v0.9.3 대화창 ---- */
#talk { position: absolute; left: 8px; right: 8px; top: 92px; z-index: 31; display: flex; gap: 10px; align-items: center; padding: 8px 12px 8px 8px; max-width: 544px; margin: 0 auto;
  background-color: var(--paper); background-image: var(--hanji); background-size: 240px 240px; border: 1px solid var(--ink); border-radius: 2px;
  box-shadow: 0 0 0 3px var(--paper), 0 0 0 4px var(--line-2), 0 8px 22px #1b1a1848; opacity: 0; transform: translateY(-8px); transition: opacity .18s, transform .18s; pointer-events: none; }
#talk.on { opacity: 1; transform: none; pointer-events: auto; cursor: pointer; }
#talk .por { flex: none; width: 60px; height: 60px; border: 1px solid var(--ink); }
#talk .tk-tx { min-width: 0; flex: 1; }
#talk .tk-who { display: flex; align-items: center; gap: 6px; font: 900 15px var(--font-display); color: var(--ink); }
#talk .tk-who em { font: 700 11px var(--font-body); font-style: normal; color: var(--paper); background: var(--seal); padding: 0 5px; border-radius: 2px; }
#talk .tk-who .chip { font-size: 10.5px; }
#talk .tk-say { margin-top: 1px; font: 600 15px/1.35 var(--font-body); color: var(--ink); }
#talk .tk-say::before { content: "\\201C"; color: var(--dim); margin-right: 1px; }
#talk .tk-say::after { content: "\\201D"; color: var(--dim); margin-left: 1px; }
#talk .tk-sub { margin-top: 3px; padding-top: 3px; border-top: 1px solid var(--line-2); font: 700 12.5px var(--font-body); color: var(--ink-2); font-variant-numeric: tabular-nums; }
#talk .tk-sub .tk-adv { display: block; font-style: normal; font-weight: 600; color: var(--seal); }
#app.building #talk.on ~ #toast { top: 194px; }
@media (prefers-reduced-motion: reduce) { #talk { transition: none; } }
/* 창 안에 넣는 한 줄(군사의 말) */
.say { display: flex; gap: 8px; align-items: center; margin: 6px 0 2px; padding: 5px 9px 5px 5px; border: 1px solid var(--line-2); border-left: 3px solid var(--ink); background: var(--paper-2); border-radius: 2px; text-align: left; }
.say .por { flex: none; width: 34px; height: 34px; border: 1px solid var(--ink); }
.say > div { min-width: 0; font-size: 13.5px; line-height: 1.35; color: var(--ink); }
.say > div > b { font-family: var(--font-display); font-weight: 900; margin-right: 2px; }
.say small { display: block; font-size: 11.5px; color: var(--dim); }
.say .ok { color: #2f6b4f; } .say .bad { color: var(--seal); }
.pksay { padding: 0 12px 2px; }
.pksay .say { margin: 4px 0 6px; }
/* STATUS 창의 군사 */
.hm-advp { display: flex; gap: 8px; align-items: stretch; margin: 2px 0 10px; }
.hm-advp .hm-say { flex: 1; min-width: 0; display: flex; gap: 9px; align-items: center; padding: 5px 9px 5px 5px; border: 1px solid var(--ink); border-radius: 2px; background: var(--paper-2); text-align: left; color: var(--ink); }
.hm-advp button.hm-say:active { background: var(--paper-3, #e4dccb); }
.hm-advp .hm-say .por { flex: none; width: 46px; height: 46px; border: 1px solid var(--ink); }
.hm-advp .hm-say .por.none { background: repeating-linear-gradient(45deg, var(--line-2) 0 4px, transparent 4px 8px); }
.hm-advp .tx { min-width: 0; display: flex; flex-direction: column; gap: 1px; }
.hm-advp .tx > i { font: 700 11.5px var(--font-body); font-style: normal; color: var(--dim); }
.hm-advp .tx > i b { font: 900 13.5px var(--font-display); color: var(--ink); }
.hm-advp .tx > span { font: 600 13.5px/1.35 var(--font-body); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.hm-advp .hm-adv { flex: none; align-self: stretch; min-width: 58px; min-height: 44px; padding: 0 10px; display: flex; align-items: center; justify-content: center; }
.hm-advp.none .hm-say { border-color: var(--seal); }
.rows.advl .row { cursor: default; }
.rows.advl .row .btn { flex: none; min-width: 58px; }
"""
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
