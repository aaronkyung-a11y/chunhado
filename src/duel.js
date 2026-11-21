/* 삼국지 천하도 — 대결 화면(v0.13): 일기토 · 설전
   규칙은 core.js 에 있다(duelNew · duelPlan · duelStep · duelPick · duelFinish, 숫자는 data.js 의 DUEL_K · DUEL_KIND).
   여기는 수를 고르게 하고, 한 합 한 합을 그려 보일 뿐이다.

   duelOpen(S, human, opt, done)
     S      판(duelNew 로 만든 것)
     human  사람이 두는 쪽 'a' | 'd'. null 이면 구경만 한다(둘 다 AI)
     opt    { sub: 제목 아래 한 줄, onEnd(S) → 끝난 뒤 결과 아래에 적을 글(HTML) — 결과를 판에 입히는 일도 여기서 한다 }
     done   [확인]을 눌러 화면을 닫은 뒤에 부른다
   duelReplay(rec, opt, done)   이미 끝난 일기토(core.js 의 duelRecOf)를 처음부터 그려 보인다 — 지난 열흘에 AI 가 건 싸움에서 벌어진 것. 끝나면 잠시 뒤 저절로 닫힌다(눌러서 바로 닫아도 된다) */
var DU = null;
var DU_HINT = { atk: '곧장 치고 들어올 기세다', def: '자세를 낮추고 기다린다', sp: '크게 벼르고 있다', ri: '이치를 따지려 든다', gain: '득실을 셈하는 눈치다', tide: '대세를 들먹일 듯하다' };
/* 합마다 뜨는 한마디: 수 → [이겼을 때 하는 말, …] */
var DU_SAY = {
  atk: ['받아라!', '간다!', '빈틈이다!'], def: ['어림없다!', '그 정도냐!', '다 보인다!'], sp: ['이것으로 끝이다!', '내 창을 받아라!', '하앗!'],
  ri: ['그것은 이치에 맞지 않소.', '의(義)를 저버리자는 말이오?', '명분이 서지 않소.'],
  gain: ['득실을 따져 보시오.', '그리하면 무엇이 남소?', '잃을 것이 더 크오.'],
  tide: ['천하의 흐름을 보시오.', '때는 이미 기울었소.', '대세를 거스를 수는 없소.']
};
var DU_LOSE = { duel: ['크윽…!', '제법이군!', '이럴 수가!'], talk: ['으음…', '그, 그것은…', '말문이 막히는군.'] };
function duEl() {
  var e = $('duel');
  if (!e) { e = document.createElement('div'); e.id = 'duel'; $('app').appendChild(e); e.addEventListener('click', duClick); }
  return e;
}
function duPor(o) { var u = sceneUrl(o.por) || POR_URL[o.por] || ''; return '<i class="du-por' + (sceneUrl(o.por) ? ' sc' : '') + '"' + (u ? ' style="background-image:url(' + u + '),var(--porbg)"' : '') + '></i>'; }
function duPips(n) { var s = ''; for (var i = 0; i < DUEL_K.momMax; i++) s += '<i' + (i < n ? ' class="on"' : '') + '></i>'; return s; }
function duSide(side) {
  var S = DU.S, K = DUEL_KIND[S.kind], P = S[side], o = off(P.id), me = DU.human ? DU.human === side : (DU.rec && o.f === G.player);
  return '<div class="du-f ' + side + (me ? ' me' : '') + '" id="duF' + side + '">' + duPor(o) +
    '<div class="du-nm">' + o.n + (me ? '<em>나</em>' : '') + '</div><div class="du-st">' + K.statName + ' <b>' + P.st + '</b></div>' +
    '<div class="du-bar"><i id="duB' + side + '" style="width:' + Math.round(P.hp / P.max * 100) + '%"></i></div>' +
    '<div class="du-hp"><b id="duH' + side + '">' + P.hp + '</b><small>/ ' + P.max + '</small><span class="du-mom" id="duM' + side + '" title="기세">' + duPips(P.mom) + '</span></div>' +
    '<div class="du-glyph" id="duG' + side + '"></div><div class="du-say" id="duS' + side + '"></div></div>';
}
function duMovesHtml() {
  var S = DU.S, K = DUEL_KIND[S.kind], h = '';
  for (var i = 0; i < K.order.length; i++) { var m = K.order[i], M = K.moves[m]; h += '<button class="du-mv" type="button" data-m="' + m + '"><i>' + M.han + '</i><b>' + M.name + '</b><small>' + M.desc + '</small></button>'; }
  return h;
}
function duelOpen(S, human, opt, done) {
  var K = DUEL_KIND[S.kind], e = duEl();
  DU = { S: S, human: human, opt: opt || {}, done: done, busy: false, auto: !human, ended: false, busy0: UI.busy, rec: (opt && opt.rec) || null, q: opt && opt.rec ? opt.rec.log.slice() : null };
  e.className = 'on ' + S.kind;
  e.innerHTML = '<div class="du-in"><div class="du-top"><span class="du-seal">' + K.name + '</span><b id="duR"></b><small>' + (DU.opt.sub || '') + '</small></div>' +
    '<div class="du-stage">' + duSide('a') + '<div class="du-mid"><span class="du-vs">對</span></div>' + duSide('d') + '<div class="du-fx" id="duFx"></div></div>' +
    '<div class="du-hint" id="duHint"></div>' +
    '<div class="du-moves" id="duMoves">' + (human ? duMovesHtml() : '') + '</div>' +
    '<div class="du-foot" id="duFoot">' + (human ? '<button class="btn" type="button" data-x="auto">맡기기</button><span class="du-tip">' + (S.kind === 'duel' ? '맹공 › 필살 › 방어 › 맹공' : '도리 › 이해 › 시세 › 도리') + '</span>' : '') + '</div>' +
    '<div class="du-res" id="duRes"></div></div>';
  UI.busy = true;
  sfx(S.kind === 'duel' ? 'duel' : 'gong');
  voiceSay(off(S.a.id), 'duel', { delay: 420, cap: function (ko) { if (DU) duFloat('a', '「' + ko + '」', 'vsay'); } });      // 건 쪽이 먼저 한마디(중국어 음성)
  setTimeout(duRound, DU.auto ? 500 : 350);
}
function duRound() {
  if (!DU || DU.ended) return;
  var S = DU.S, K = DUEL_KIND[S.kind];
  if (DU.q) return duReplayStep();
  if (S.over) return duEnd();
  duelPlan(S, DU.auto ? null : DU.human);
  $('duR').textContent = '제' + (S.round + 1) + K.unit + ' / ' + S.max;
  ['a', 'd'].forEach(function (s) { $('duG' + s).className = 'du-glyph'; $('duG' + s).textContent = ''; $('duS' + s).className = 'du-say'; $('duS' + s).textContent = ''; $('duF' + s).classList.remove('win', 'hit', 'lunge', 'rest'); });
  if (DU.auto) { DU.busy = true; setTimeout(function () { if (!DU) return; var p = S.plan, ma = p.a || duelPick(S, 'a'), md = p.d || duelPick(S, 'd'); duResolve(ma, md); }, DU.human ? 260 : 420); return; }
  var h = S.hint, op = off(S[duelOther(DU.human)].id);
  $('duHint').innerHTML = h ? '<b>' + op.n + '의 기색</b> ' + DU_HINT[h.move] + ' <em>' + K.moves[h.move].name + '?</em><small>읽기 ' + h.p + '%</small>' : '';
  $('duMoves').classList.remove('off'); DU.busy = false;
}
/* 다시 보기: 적혀 있는 합을 하나씩 꺼내 그대로 그린다(주사위는 굴리지 않는다) */
function duReplayStep() {
  var S = DU.S, K = DUEL_KIND[S.kind], R = DU.q.shift();
  if (!R) { S.over = true; S.win = DU.rec.win; S.ko = DU.rec.ko; return duEnd(); }
  $('duR').textContent = '제' + R.n + K.unit + ' / ' + S.max;
  ['a', 'd'].forEach(function (s) { $('duG' + s).className = 'du-glyph'; $('duG' + s).textContent = ''; $('duS' + s).className = 'du-say'; $('duS' + s).textContent = ''; $('duF' + s).classList.remove('win', 'hit', 'lunge', 'rest'); });
  S.a.hp = R.hpA; S.d.hp = R.hpD; S.round = R.n;
  if (R.win === 'a') { S.a.mom = Math.min(DUEL_K.momMax, S.a.mom + 1); S.d.mom = 0; } else if (R.win === 'd') { S.d.mom = Math.min(DUEL_K.momMax, S.d.mom + 1); S.a.mom = 0; }
  setTimeout(function () { if (DU) duAnim(R, duRound); }, 300);
}
function duelReplay(rec, opt, done) {
  var o = opt || {}, S = duelNew(rec.kind, off(rec.a.id), off(rec.d.id), { hpA: rec.a.max, hpD: rec.d.max, rounds: rec.max });
  S.a.st = rec.a.st; S.d.st = rec.d.st;
  duelOpen(S, null, { sub: o.sub, rec: rec, onEnd: function () { return o.out || ''; }, autoClose: o.autoClose === undefined ? 2600 : o.autoClose }, done);
}
function duClick(e) {
  if (!DU) return;
  var b = e.target.closest ? e.target.closest('button') : null; if (!b) return;
  if (b.getAttribute('data-x') === 'close') return duClose();
  if (DU.busy || DU.ended) return;
  if (b.getAttribute('data-x') === 'auto') { DU.auto = true; $('duMoves').classList.add('off'); $('duHint').innerHTML = '<b>맡겼습니다</b> ' + josa(off(DU.S[DU.human].id).n, '이가') + ' 알아서 겨룹니다'; b.disabled = true; sfx('ui'); duResolve(duelPick(DU.S, DU.human), null); return; }
  var m = b.getAttribute('data-m'); if (!m) return;
  sfx('ui'); duResolve(m, null);
}
/* 사람의 수(또는 둘 다)를 받아 한 합을 치르고 그려 보인다 */
function duResolve(m1, m2) {
  var S = DU.S, p = S.plan || {}, ma, md;
  if (m2 !== null && m2 !== undefined) { ma = m1; md = m2; }
  else { ma = DU.human === 'a' ? m1 : p.a; md = DU.human === 'd' ? m1 : p.d; }
  if (!ma) ma = duelPick(S, 'a'); if (!md) md = duelPick(S, 'd');
  DU.busy = true; $('duMoves').classList.add('off');
  var R = duelStep(S, ma, md);
  if (!R) { DU.busy = false; return; }
  duAnim(R, function () { if (!DU) return; if (S.over) duEnd(); else duRound(); });
}
function duFloat(side, text, cls) {
  var f = document.createElement('span'); f.className = 'du-float ' + (cls || ''); f.textContent = text;
  $('duF' + side).appendChild(f); setTimeout(function () { if (f.parentNode) f.parentNode.removeChild(f); }, cls === 'vsay' ? 2100 : 1300);
}
function duSlash(side, big) {
  var fx = $('duFx'); if (!fx) return;
  var s = document.createElement('i'); s.className = 'du-slash ' + side + (big ? ' big' : ''); fx.appendChild(s);
  setTimeout(function () { if (s.parentNode) s.parentNode.removeChild(s); }, 700);
}
function duBars() {
  var S = DU.S;
  ['a', 'd'].forEach(function (s) { var P = S[s]; $('duB' + s).style.width = Math.max(0, Math.round(P.hp / P.max * 100)) + '%'; $('duH' + s).textContent = P.hp; $('duM' + s).innerHTML = duPips(P.mom); $('duB' + s).classList.toggle('low', P.hp < P.max * 0.35); });
}
function duAnim(R, cb) {
  var S = DU.S, K = DUEL_KIND[S.kind], fast = DU.auto && !!DU.human, T = fast ? 0.42 : 1, duel = S.kind === 'duel';
  function at(ms, fn) { setTimeout(function () { if (DU) fn(); }, Math.round(ms * T)); }
  // ① 두 사람의 수가 드러난다
  ['a', 'd'].forEach(function (s) { var g = $('duG' + s), m = s === 'a' ? R.ma : R.md; g.textContent = K.moves[m].han; g.className = 'du-glyph on ' + m; g.setAttribute('aria-label', K.moves[m].name); });
  sfx(duel ? 'shout' : 'page');
  // ② 부딪친다
  at(480, function () {
    var w = R.win, l = w ? duelOther(w) : null;
    if (R.how === 'rest') { $('duFa').classList.add('rest'); $('duFd').classList.add('rest'); duFloat('a', '+' + R.heal, 'heal'); duFloat('d', '+' + R.heal, 'heal'); sfx('wind'); }
    else if (R.how === 'both') {
      $('duFa').classList.add('lunge', 'hit'); $('duFd').classList.add('lunge', 'hit'); duSlash('a'); duSlash('d');
      duFloat('a', '-' + R.toA); duFloat('d', '-' + R.toD); sfx(duel ? 'hit' : 'ui'); if (duel) sfx('counter');
    } else {
      var big = duel && (K.moves[w === 'a' ? R.ma : R.md].mult > 1 || R.how === 'clash');
      $('duF' + w).classList.add('lunge', 'win'); $('duF' + l).classList.add('hit'); duSlash(l, big);
      duFloat(l, '-' + (l === 'a' ? R.toA : R.toD), big ? 'big' : '');
      var wm = w === 'a' ? R.ma : R.md, sw = $('duS' + w), sl = $('duS' + l);
      sw.textContent = DU_SAY[wm][(R.n + S[w].id) % DU_SAY[wm].length]; sw.className = 'du-say on';
      sl.textContent = DU_LOSE[S.kind][(R.n + S[l].id) % 3]; sl.className = 'du-say on lose';
      if (duel) { if (R.how === 'clash') sfx('duel'); sfx(big ? 'big' : (wm === 'def' ? 'counter' : 'hit')); } else sfx('drum');
      var st = $('duel').querySelector('.du-stage'); st.classList.remove('shake'); void st.offsetWidth; st.classList.add('shake');
    }
  });
  at(620, duBars);
  at(fast ? 1250 : 1500, cb);
}
function duEnd() {
  if (!DU || DU.ended) return;
  DU.ended = true;
  var S = DU.S, K = DUEL_KIND[S.kind], A = off(S.a.id), D = off(S.d.id), w = S.win, extra = '';
  var mySide = DU.human || (DU.rec ? (A.f === G.player ? 'a' : (D.f === G.player ? 'd' : null)) : null), mine = mySide && w !== 'draw' ? w === mySide : null;
  try { extra = DU.opt.onEnd ? (DU.opt.onEnd(S) || '') : ''; } catch (e) { extra = ''; }
  $('duMoves').innerHTML = ''; $('duHint').innerHTML = ''; $('duFoot').innerHTML = '';
  if (w !== 'draw') { $('duF' + w).classList.add('victor'); $('duF' + duelOther(w)).classList.add(S.ko ? 'ko' : 'loser'); }
  var head = w === 'draw' ? '비김' : (w === 'a' ? A.n : D.n) + ' 승';
  var how = w === 'draw' ? S.round + K.unit + '을 겨뤄 가리지 못했습니다' : (S.ko ? S.round + K.unit + ' 만에 ' + (S.kind === 'duel' ? '쓰러뜨렸습니다' : '말문을 막았습니다') : '판정 — 남은 힘 ' + Math.round(S.a.hp / S.a.max * 100) + '% 대 ' + Math.round(S.d.hp / S.d.max * 100) + '%');
  $('duRes').innerHTML = '<div class="du-resin' + (mine === true ? ' won' : (mine === false ? ' lost' : '')) + '">' + (w !== 'draw' ? '<i class="du-stamp">' + (mine === false ? '敗' : '勝') + '</i>' : '') +
    '<h3>' + head + '</h3><p>' + how + '</p>' + (extra ? '<div class="du-out">' + extra + '</div>' : '') + '<button class="btn pri" type="button" data-x="close">확인</button></div>';
  $('duRes').classList.add('on');
  if (S.kind === 'duel') sfx(S.ko ? 'great' : 'drum'); else sfx('gong');
  if (mine === true) sfx('cheerlate');
  if (w !== 'draw') voiceSay(w === 'a' ? A : D, S.kind === 'duel' ? 'great' : 'ploy', { delay: 520, cap: function (ko) { if (DU) duFloat(w, '「' + ko + '」', 'vsay'); } });
  if (DU.opt.autoClose) { var d0 = DU; setTimeout(function () { if (DU === d0) duClose(); }, DU.opt.autoClose); }
}
function duClose() {
  if (!DU) return;
  var d = DU, e = $('duel'); DU = null;
  if (e) { e.className = ''; e.innerHTML = ''; }
  UI.busy = !!d.busy0 && !!d.rec; if (!d.rec) sfx('ui');                  // 다시 보기는 열흘 재생 도중이다 — 그때의 상태로 되돌린다
  if (d.done) d.done(d.S);
}
