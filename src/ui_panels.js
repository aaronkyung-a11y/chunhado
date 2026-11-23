/* ===== 천하도 — 패널·대화상자·조작 흐름 ===== */
var SHEET = null, MODAL = null, toastT = 0;
var SIZE_NAME = { L: '대도시', M: '중도시', S: '소도시', G: '관문' };
var ICO = {
  gold: '<svg viewBox="0 0 16 16"><circle cx="8" cy="8" r="6.5" fill="#c9a23f" stroke="#1b1a18"/><rect x="5.6" y="5.6" width="4.8" height="4.8" fill="#1b1a18"/></svg>',
  food: '<svg viewBox="0 0 16 16"><path d="M5 2.6h6l-1.2 2.3c2.6 1.4 3.7 4 3.2 6.5-.4 1.8-1.7 2.8-5 2.8s-4.6-1-5-2.8c-.5-2.5.6-5.1 3.2-6.5z" fill="#e6dcc0" stroke="#1b1a18"/><path d="M6 5h4" stroke="#1b1a18"/></svg>',
  troops: '<svg viewBox="0 0 16 16"><circle cx="8" cy="5" r="2.7" fill="#e2ddd0" stroke="#1b1a18"/><path d="M2.8 14c.3-3.4 2.3-5 5.2-5s4.9 1.6 5.2 5z" fill="#b9b3a4" stroke="#1b1a18"/></svg>',
  morale: '<svg viewBox="0 0 16 16"><path d="M8 1.5c.6 2.8 4 4.2 4 7.8A4 4 0 0 1 8 13.5 4 4 0 0 1 4 9.3c0-1.7 1-2.6 1.7-3.6.4 1 .9 1.5 1.5 1.7C6.9 5.2 7.3 3.2 8 1.5z" fill="#b5332a" stroke="#1b1a18"/></svg>',
  order: '<svg viewBox="0 0 16 16"><path d="M8 1.5l5 1.8v4.2c0 3.2-2.1 5.5-5 6.9-2.9-1.4-5-3.7-5-6.9V3.3z" fill="#8fa698" stroke="#1b1a18"/></svg>',
  dur: '<svg viewBox="0 0 16 16"><path d="M2 14V5h2.4v2h2.2V5h2.8v2h2.2V5H14v9z" fill="#d3ccba" stroke="#1b1a18"/></svg>',
  spear: '<svg viewBox="0 0 16 16"><path d="M3 13L11 5" stroke="#4a4037" stroke-width="1.6"/><path d="M10 6l4-4-1 5z" fill="#e2ddd0" stroke="#1b1a18" stroke-width=".8"/></svg>',
  halberd: '<svg viewBox="0 0 16 16"><path d="M3 13L12 4" stroke="#4a4037" stroke-width="1.6"/><path d="M11 5l3-3-.5 3.5z" fill="#e2ddd0" stroke="#1b1a18" stroke-width=".8"/><path d="M7.6 5.4c1.9-1 3.6-.4 4.2 1.4-1.4-.4-2.4 0-3.1 1z" fill="#e2ddd0" stroke="#1b1a18" stroke-width=".8"/></svg>',
  bow: '<svg viewBox="0 0 16 16"><path d="M2.5 6c3-3.2 8-3.2 11 0" fill="none" stroke="#4a4037" stroke-width="1.7"/><path d="M8 3.5v10" stroke="#4a4037" stroke-width="1.7"/><path d="M2.5 6L8 8.6 13.5 6" fill="none" stroke="#e2ddd0" stroke-width=".9"/></svg>',
  horse: '<svg viewBox="0 0 16 16"><path d="M3.6 13.5V7.2a4.4 4.4 0 0 1 8.8 0v6.3h-2.3V7.2a2.1 2.1 0 0 0-4.2 0v6.3z" fill="#b9a37c" stroke="#1b1a18"/></svg>',
  ram: '<svg viewBox="0 0 16 16"><rect x="2" y="5.6" width="9.6" height="3.8" rx="1" fill="#a8946c" stroke="#1b1a18"/><path d="M11.6 5.6l2.9 1.9-2.9 1.9z" fill="#e2ddd0" stroke="#1b1a18" stroke-width=".8"/><circle cx="4.8" cy="12" r="1.7" fill="#3a332a"/><circle cx="9.6" cy="12" r="1.7" fill="#3a332a"/></svg>'
};
function ico(k) { return '<i class="ico">' + ICO[k] + '</i>'; }
function thumb(key, cls) { return '<img class="th' + (cls ? ' ' + cls : '') + '" alt="" src="' + SPRITES[key].u + '">'; }
function facThumb(fc, cls) { var u = (!fc.done && typeof siteUrl === 'function') ? siteUrl(fc.t) : ''; return u ? '<img class="th' + (cls ? ' ' + cls : '') + '" alt="" src="' + u + '">' : thumb(fc.t, cls); }      // 짓는 중인 시설은 공사장 그림
function lotChip(b, pi) { return '<i class="lno">' + lotNo(b, pi) + '</i>'; }                                   // 부지 번호 딱지(지도의 번호와 같다)
function days(turns) { return fmt(turns * 10) + '일'; }
function months(turns) { var m = turns / 3; return turns % 3 ? days(turns) : (m % 12 ? m + '개월' : (m / 12) + '년'); }   // 3턴 = 한 달. 달로 나누어떨어지지 않으면 일수로
function shortDate(t) { var d = dateOfTurn(t), y = G.year + '년 '; return d.indexOf(y) === 0 ? d.slice(y.length) : d; }      // 올해면 해를 뺀다
function unitFoodTurns(x) { return x.troops > 0 ? Math.floor(x.food / Math.ceil(x.troops / (uHas(x, '둔전') ? 40 : 20))) : 0; }

function toast(msg, ms) {
  var t = $('toast'); t.textContent = msg; t.classList.add('on');
  clearTimeout(toastT); toastT = setTimeout(function () { t.classList.remove('on'); }, ms || 2400);
}
/* ---------- 대화창(v0.9.3) ----------
   초상 + 이름 + 한마디(+ 결과 한 줄). 화면 위쪽에 떴다가 저절로 사라지고, 누르면 바로 닫힌다. 명령의 흐름을 막지 않는다.
   끄면(UI.talk === false) 결과 한 줄만 전처럼 알림 줄로 나온다. */
var talkT = 0, TALK = null;
function roleOf(o) { return isLord(o) ? '군주' : (o.f >= 0 && facAdv(o.f) === o ? '군사' : ''); }
function talkHide() { clearTimeout(talkT); TALK = null; var t = $('talk'); if (t) t.classList.remove('on'); }
function talk(o, say, sub, ms, role) {      // v0.20: role = 이름 옆 딱지를 따로 정할 때(싸움터의 조언: 부장 · 주장)
  voiceTalk(o);                                             // v0.13: 방금 고른 말이면 갈래에 맞는 음성을 붙인다(대화창을 꺼 두어도)
  if (!o || UI.talk === false) { var m0 = String(sub || say || '').replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim(); if (m0) toast(m0, ms); return; }      // 꺼 두었으면 결과 한 줄만 알림 줄로
  var t = $('talk'), rl = role || roleOf(o);
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
  advisor:  { W: ['머리 쓰는 일이라… 힘껏 해 보겠소.'], C: ['미력하나마 지혜를 다하겠습니다.', '삼가 명을 받들겠습니다.'], L: ['…'] },
  trade:    { W: ['셈을 마쳤소.'], C: ['거래를 마쳤습니다.', '상인들과 셈을 마쳤습니다.'], L: ['거래를 마쳤다.'] },
  released: { W: ['이 은혜는 잊지 않겠소.'], C: ['베푸신 은혜, 잊지 않겠습니다.'], L: ['…이 일은 기억해 두겠소.'] },
  corps:    { W: ['맡겨 주시오. 실망시키지 않겠소.', '이 땅은 내가 지키겠소.'], C: ['맡겨 주십시오. 빈틈없이 다스리겠습니다.', '삼가 맡겠습니다.'], L: ['…'] },
  cdev:     { W: ['고을을 일구는 일도 싸움이라 여기겠소.'], C: ['고을을 살찌우겠습니다.', '백성부터 돌보겠습니다.'], L: ['…'] },
  carm:     { W: ['병사를 모으고 칼을 갈겠소.'], C: ['군비를 갖추겠습니다.', '병사와 병기를 모으겠습니다.'], L: ['…'] },
  catk:     { W: ['{x}{을} 치겠소. 채비가 되는 대로 나서겠소!'], C: ['{x}{을} 치겠습니다. 채비가 되는 대로 나서겠습니다.'], L: ['…'] },
  csup:     { W: ['{x}{으로} 병력과 물자를 보내겠소.'], C: ['{x}{으로} 병력과 물자를 보내겠습니다.'], L: ['…'] },
  envoy:    { W: ['말솜씨는 없으나, 다녀오겠소.', '{x} 공을 만나고 오겠소.'], C: ['사신의 소임을 다하겠습니다.', '{x} 공을 뵙고 오겠습니다.'], L: ['내가 직접 만나 보겠다.'] },
  dipYes:   { W: ['좋소. 그리합시다.'], C: ['뜻을 받들겠습니다.'], L: ['좋소. 그리합시다.', '귀공의 뜻, 잘 알았소.'] },
  dipNo:    { W: ['그럴 수는 없소.'], C: ['받아들이기 어렵습니다.'], L: ['그럴 수는 없소.', '아직은 때가 아니오.'] },
  dipGift:  { W: ['후한 선물이오. 잊지 않겠소.'], C: ['후의에 감사드립니다.'], L: ['후한 선물, 고맙게 받겠소.'] },
  dipAsk:   { W: ['서로 칼을 거둡시다.'], C: ['서로 칼을 거두기를 청합니다.'], L: ['서로 칼을 거둡시다. 어떻소?', '손을 잡읍시다. 어떻소?'] },
  dipBreak: { W: ['이 일은 잊지 않겠소!'], C: ['신의를 저버리시다니…'], L: ['신의를 저버리다니… 이 일은 잊지 않겠소.'] },
  duelAsk:  { W: ['나와라! 나와 겨룰 자가 없느냐!', '네 솜씨를 보자. 나와라!'], C: ['한 수 겨루어 보시겠소?'], L: ['장수끼리 겨루어 승부를 가립시다.'] },
  duelNo:   { W: ['…오늘은 상대하지 않겠다.'], C: ['장수의 싸움에 말려들 까닭이 없습니다.'], L: ['필부의 용맹에 응할 것 없다.'] },
  aimYes:   { W: ['좋소. 군사를 내겠소.'], C: ['뜻을 받들어 군사를 내겠습니다.'], L: ['좋소. 함께 칩시다.', '때가 좋소. 군사를 내겠소.'] },
  aimNo:    { W: ['지금은 군사를 낼 수 없소.'], C: ['지금은 군사를 내기 어렵습니다.'], L: ['지금은 군사를 낼 형편이 아니오.'] }
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
  SAYV = { o: o.id, key: key, t: performance.now() };
  var own = SAY_OWN[o.n] && SAY_OWN[o.n][key], L = own || (SAY[key] && (SAY[key][toneOf(o)] || SAY[key].C)) || ['…'];
  var t = L[Math.floor(Math.random() * L.length)];                                   // 화면의 말뿐이라 판의 주사위(rnd)는 쓰지 않는다
  if (x !== undefined) t = t.replace(/\{x\}\{으로\}/g, euro(String(x))).replace(/\{x\}\{을\}/g, josa(String(x), '을를')).replace(/\{x\}\{이라\}/g, x + (hasBatchim(String(x)) ? '이라' : '라')).replace(/\{x\}/g, x);
  return t;
}
function euro(w) { var c = w.charCodeAt(w.length - 1), j = (c >= 0xAC00 && c <= 0xD7A3) ? (c - 0xAC00) % 28 : 0; return w + (j && j !== 8 ? '으로' : '로'); }      // 여남으로 · 소패로 · 강릉으로 · 서울로
function hasBatchim(w) { var c = w.charCodeAt(w.length - 1); return c >= 0xAC00 && c <= 0xD7A3 && (c - 0xAC00) % 28 !== 0; }
/* 군사의 말을 초상과 함께 한 줄로(창 안에 넣는 꼴) */
function sayRow(o, say, sub, cls, role) { return '<div class="say' + (cls ? ' ' + cls : '') + '">' + porTag(o, 'sm') + '<div>' + (role ? '<em class="role">' + role + '</em>' : '') + '<b>' + o.n + '</b> <span>' + say + '</span>' + (sub ? '<small>' + sub + '</small>' : '') + '</div></div>'; }
function advSay(a, what, yes, no) { return a ? sayRow(a.adv, (what ? what + ' ' : '') + '<b class="' + (a.says ? 'ok' : 'bad') + '">' + (a.says ? (yes || '통할 것입니다.') : (no || '어렵겠습니다.')) + '</b>', accT(a.acc), 'adv') : ''; }
/* 조언이 빗나갔을 때 군사가 덧붙이는 말('' = 덧붙일 말 없음) */
function advAfter(a, ok) { return (a && a.says !== ok) ? (a.says ? '…제 헤아림이 모자랐습니다.' : '…뜻밖입니다. 제가 잘못 보았습니다.') : ''; }
function showSheet(s) { SHEET = s; var el = $('sheet'); el.className = 'on' + (s.cls ? ' ' + s.cls : ''); el.innerHTML = s.render(); }
function refreshSheet() {
  if (!SHEET) return;
  var el = $('sheet'), body = el.querySelector('.sh-body'), st = body ? body.scrollTop : 0;
  el.innerHTML = SHEET.render();
  body = el.querySelector('.sh-body'); if (body) body.scrollTop = st;
}
function closeSheet() { showHome(); }
/* ---------- 아래에 더 있다는 표시(v0.12) ----------
   굴러가는 몸통(.dlg-b · .sh-body)의 맨 끝에 높이 0 인 붙박이(sticky) 토막을 넣는다 — 아래에 더 있을 때만 몸통의 아래 끝에 보인다. */
var MORE_GAP = 10;                                                 // 이만큼(픽셀)도 안 남았으면 끝으로 본다
function moreSet(body) {
  var h = body.querySelector(':scope > .morehint'); if (!h) return;
  h.classList.toggle('on', body.scrollHeight - body.scrollTop - body.clientHeight > MORE_GAP);
}
function moreScan() {
  var list = document.querySelectorAll('#modal .dlg-b, #sheet .sh-body');
  for (var i = 0; i < list.length; i++) (function (body) {
    if (!body.querySelector(':scope > .morehint')) {
      var h = document.createElement('div'); h.className = 'morehint'; h.setAttribute('aria-hidden', 'true'); h.innerHTML = '<i>▼ 아래에 더 있습니다</i>';
      h.firstChild.addEventListener('click', function (e) { e.stopPropagation(); try { body.scrollBy({ top: Math.round(body.clientHeight * 0.8), behavior: 'smooth' }); } catch (err) { body.scrollTop += Math.round(body.clientHeight * 0.8); } });
      body.appendChild(h);
    }
    if (!body._more) { body._more = true; body.addEventListener('scroll', function () { moreSet(body); }, { passive: true }); }
    moreSet(body);
  })(list[i]);
}
function moreSoon() { moreScan(); if (moreSoon.t) return; moreSoon.t = setTimeout(function () { moreSoon.t = 0; moreScan(); }, 350); }      // 곧바로(다시 그린 그 자리에서 — 깜빡이지 않게) + 그림이 늦게 뜨거나 판이 미끄러져 올라온 뒤에 한 번 더
function moreInit() {
  try { var mo = new MutationObserver(moreSoon); mo.observe($('modal'), { childList: true }); mo.observe($('sheet'), { childList: true }); } catch (e) { /* 표시는 없어도 된다 */ }
  window.addEventListener('resize', moreSoon);
  window.addEventListener('resize', function () { if (typeof barFit === 'function') barFit(); });
  document.addEventListener('toggle', moreSoon, true);              // 접힌 풀이(<details>)를 펼쳤을 때
}
/* 창은 겹쳐 열 수 있다. push 로 열면 지금 창을 아래에 깔아 두고, ×(또는 바깥 누르기)는 한 단계만 뒤로 간다.
   명령을 마쳤을 때처럼 한꺼번에 닫을 때는 closeDialog(). */
var MSTACK = [], MPAINT = 0;
function dlgScroll() { var b = $('modal').querySelector('.dlg-b'); return b ? b.scrollTop : 0; }
var PICKING = false;                                              // v0.20: 지도에서 고르는 창이 떠 있는가(MODAL.pick)
function paintDialog(st) {
  var m = $('modal'); m.innerHTML = '<div class="dlg">' + MODAL.render() + '</div>'; m.classList.add('on');
  m.classList.toggle('see', !!MODAL.see); $('app').classList.toggle('seeing', !!(devOf() || fselOf() || MODAL.pick));
  $('app').classList.toggle('picking', !!MODAL.pick);                // v0.20: 지도에서 고르는 창 — 고를 칸의 딱지를 띄운다(없으면 걷는다)
  if (MODAL.pick && MODAL.pick.show) MODAL.pick.show(); else marksClear();
  if (MODAL.pick || PICKING) requestDraw();                          // 지도는 고르는 창이 뜨거나 걷힐 때만 다시 그린다(여느 창을 열 때마다 그리면 느리다)
  PICKING = !!MODAL.pick;
  if (st) { var b = m.querySelector('.dlg-b'); if (b) b.scrollTop = st; }
  MPAINT = Date.now();
  paintRet();
}
function showDialog(d, push) { if (push && MODAL) MSTACK.push({ d: MODAL, st: dlgScroll() }); else MSTACK.length = 0; MODAL = d; paintDialog(0); }
function backDialog() {
  if (MODAL && MODAL.lock) return;                                   // 끝난 판의 창처럼 닫으면 안 되는 창
  if (MSTACK.length) { var p = MSTACK.pop(); MODAL = p.d; paintDialog(p.st); } else closeDialog();
}
function refreshDialog() {
  if (!MODAL) return;
  var m = $('modal'), b = m.querySelector('.dlg-b'), st = b ? b.scrollTop : 0;
  m.innerHTML = '<div class="dlg">' + MODAL.render() + '</div>';
  b = m.querySelector('.dlg-b'); if (b) b.scrollTop = st;
}
function closeDialog() { var d0 = MODAL; MSTACK.length = 0; MODAL = null; var m = $('modal'); m.classList.remove('on'); m.classList.remove('see'); $('app').classList.remove('seeing'); $('app').classList.remove('picking'); marksClear(); if (PICKING) { PICKING = false; requestDraw(); } m.innerHTML = ''; paintRet(); if (d0 && d0.onClose) d0.onClose(); }
function dlgHead(title) { return '<div class="dlg-h"><h2>' + title + '</h2><button class="x" data-a="close" type="button" aria-label="닫기">×</button></div>'; }
function delegate(root, getH, onClose) {
  root.addEventListener('click', function (e) {
    var el = e.target.closest ? e.target.closest('[data-a]') : null;
    if (root.id === 'modal' && Date.now() - MPAINT < 200) return;      // 창이 막 바뀐 직후의 누름(연달아 두 번 누름)은 버린다 — 새 창의 엉뚱한 단추에 닿지 않게
    if (!el || !root.contains(el)) { if (root.id === 'modal' && e.target === root) backDialog(); return; }
    var a = el.getAttribute('data-a'), hs = getH();
    if (root.id === 'sheet' && UI.busy) return;                         // 움직이는 장면이 나오는 동안에는 아래 창의 단추를 받지 않는다
    audioInit(); bgmKick(); sfx('ui');
    if (a === 'close') { onClose(); return; }
    if (hs && hs.on && hs.on[a]) hs.on[a](el);
  });
  root.addEventListener('input', function (e) {
    var el = e.target.closest ? e.target.closest('[data-i]') : null; if (!el) return;
    var hs = getH(), a = el.getAttribute('data-i');
    if (hs && hs.on && hs.on[a]) hs.on[a](el);
  });
}

/* ---------- 공통 조각 ---------- */
/* v0.18: 지금 판의 무장이면 data-oid 를 단다 — 얼굴을 누르면 어디서든 무장 카드가 겹쳐 뜬다(ocardInit). 세력을 고르는 창처럼 판 밖의 얼굴에는 달지 않는다 */
function oidAttr(o) { return o && typeof o.id === 'number' && G && G.officers && G.officers[o.id] === o ? ' data-oid="' + o.id + '"' : ''; }
function porTag(o, cls) { var u = o ? POR_URL[o.por] : ''; return '<i class="por' + (cls ? ' ' + cls : '') + '"' + oidAttr(o) + (u ? ' style="background-image:url(' + u + '),var(--porbg)"' : '') + '></i>'; }
/* 장면 초상(3:4): 장수 정보·소개 창에서 쓴다. 장면이 없으면 큰 흉상 */
function sceneTag(o) { var u = o ? sceneUrl(o.por) : ''; return u ? '<i class="por sc"' + oidAttr(o) + ' style="background-image:url(' + u + '),var(--porbg)"></i>' : porTag(o, 'lg'); }
function st5(o, hi) {
  var ks = [['ldr', '통'], ['war', '무'], ['int', '지'], ['pol', '정'], ['cha', '매']], s = '<span class="st5">';
  for (var i = 0; i < 5; i++) s += '<span><i>' + ks[i][1] + '</i> <b' + (hi === ks[i][0] ? ' class="hi"' : '') + '>' + o[ks[i][0]] + '</b></span>';
  return s + '</span>';
}
function skGist(o) { return o && o.sk && SKILL_TAG[o.sk] ? SKILL_TAG[o.sk] : ''; }
function skTag(o) { return o.sk ? '<em>' + o.sk + '</em>' + (skGist(o) ? '<small class="skg">' + skGist(o) + '</small>' : '') : ''; }      // v0.18: 무엇을 하는 특기인지 한 줄
/* 적성 한 줄(v0.11): 창 극 노 기 병기 — S 붉은빛 · A 황토빛 · C 흐리게. on = 지금 고른 병과(출진 창)의 칸에 밑줄 */
function apt5(o, on) {
  var ks = ['창', '극', '노', '기', '병기'], s = '<span class="ds ap5">';
  for (var i = 0; i < 5; i++) { var a = o.apt.charAt(i); s += '<span' + (on === i ? ' class="on"' : '') + '><i>' + ks[i] + '</i><b class="' + a + '">' + a + '</b></span>'; }
  return s + '</span>';
}
function facChip(f) { return '<span class="chip" style="background:' + (f >= 0 ? G.factions[f].color : '#8d877b') + '">' + (f >= 0 ? G.factions[f].name : '빈 땅') + '</span>'; }
function offStatus(o) {
  if (o.st === 'travel') return (o.dest >= 0 && G.bases[o.dest] ? euro(G.bases[o.dest].n) + ' ' : '') + '이동 중 (' + days(o.eta) + ')';      // v0.20: 가는 곳을 적는다
  if (o.unit !== null) return '출진 중';
  var j = jobOf(o);
  if (j) return '<b class="job">' + FAC[j.fac.t].name + ' 건설 중</b> (' + days(j.left) + ')';      // 완공될 때까지 다른 일을 못 한다
  return o.acted ? '행동 완료' : '대기';
}
function offRow(o, opt) {
  opt = opt || {};
  return '<button class="row' + (opt.sel ? ' sel' : '') + (opt.dim ? ' dim' : '') + '" type="button" data-a="' + (opt.a || 'off') + '" data-v="' + o.id + '">' + porTag(o) +
    '<span class="mid"><span class="nm">' + (opt.badge ? '<span class="hi">' + opt.badge + '</span> ' : '') + o.n + skTag(o) + '</span><span class="ds">' + (opt.ds !== undefined ? opt.ds : st5(o, opt.hi)) + '</span>' + (opt.noapt ? '' : apt5(o, opt.apt)) + '</span>' +
    (opt.rt ? '<span class="rt">' + opt.rt + '</span>' : '') + '</button>';
}

/* 무장 선택 표(열 제목을 누르면 정렬). opts: {title, list, min, max, hi, key(o), rt(o), rtHead, preview(os), ok, auto(n)→ids} */
function pickOfficers(opts, cb) {
  var sel = [], max = opts.max || 1, min = opts.min || 1, sortK = null, sortDir = -1, autoN = 0;
  if (!opts.list.length) { toast('행동할 수 있는 무장이 없습니다'); return; }
  var COLS = [['ldr', '통'], ['war', '무'], ['int', '지'], ['pol', '정'], ['cha', '매']];
  function sorted() {
    var L = opts.list.slice();
    if (sortK) L.sort(function (a, b) { return (b[sortK] - a[sortK]) * -sortDir; }); else L.sort(function (a, b) { return opts.key(b) - opts.key(a); });
    return L;
  }
  showDialog({
    render: function () {
      var list = sorted(), i, j, h = dlgHead(opts.title) + '<div class="dlg-b tbl"><div class="th-row"><span class="c-n">무장</span>';
      for (j = 0; j < 5; j++) h += '<button type="button" class="c-s' + (sortK === COLS[j][0] ? ' on' : (!sortK && opts.hi === COLS[j][0] ? ' hi' : '')) + '" data-a="sort" data-v="' + COLS[j][0] + '">' + COLS[j][1] + (sortK === COLS[j][0] ? (sortDir < 0 ? '▾' : '▴') : '') + '</button>';
      h += '<span class="c-x">' + (opts.rtHead || '특기') + '</span></div>';
      for (i = 0; i < list.length; i++) {
        var o = list[i], si = sel.indexOf(o.id);
        h += '<button class="tr' + (si >= 0 ? ' sel' : '') + '" type="button" data-a="pick" data-v="' + o.id + '">' + porTag(o, 'sm') + '<span class="c-n">' + (si >= 0 && max > 1 ? '<i class="ord">' + (si + 1) + '</i>' : '') + o.n + '</span>';
        for (j = 0; j < 5; j++) h += '<span class="c-s' + (opts.hi === COLS[j][0] ? ' hi' : '') + '">' + o[COLS[j][0]] + '</span>';
        h += '<span class="c-x">' + (opts.rt ? opts.rt(o) : (o.sk || '—')) + '</span>' +
          '<span class="c-2">' + apt5(o, opts.apt) + (o.sk ? '<span class="sk2"><b>' + o.sk + '</b>' + (skGist(o) ? ' ' + skGist(o) : '') + '</span>' : '') + '</span></button>';      // v0.18
      }
      var os = sel.map(off), strip = '';
      if (os.length) { strip = '<div class="selstrip">'; for (i = 0; i < os.length; i++) strip += '<span>' + porTag(os[i], 'md') + '<b>' + (max > 1 ? (i + 1) + '. ' : '') + os[i].n + '</b></span>'; strip += '</div>'; }
      h += '</div>' + strip + (opts.say && os.length ? '<div class="pksay">' + opts.say(os) + '</div>' : '') + '<div class="dlg-f"><div class="pv">' + (os.length ? (opts.preview ? opts.preview(os) : os.length + '명 선택') : (max > 1 ? (max >= 99 ? '무장을 고르세요 (몇 명이든)' : '무장을 고르세요 (최대 ' + max + '명)') : '무장을 고르세요')) + '</div>' +
        (opts.auto ? '<button class="btn auto" type="button" data-a="auto">자동</button>' : '') +
        (opts.all && opts.list.length > 1 ? '<button class="btn auto" type="button" data-a="all">' + (sel.length === opts.list.length ? '모두 풀기' : '모두') + '</button>' : '') +      // v0.21
        (opts.alt ? '<button class="btn alt' + (os.length >= min && opts.alt.can(os) ? '' : ' off') + '" type="button" data-a="alt">' + opts.alt.label + '</button>' : '') +
        '<button class="btn pri" type="button" data-a="ok"' + (os.length < min ? ' disabled' : '') + '>' + (opts.ok || '실행') + '</button></div>';
      return h;
    },
    on: {
      sort: function (el) { var k = el.getAttribute('data-v'); if (sortK === k) sortDir = -sortDir; else { sortK = k; sortDir = -1; } refreshDialog(); },
      all: function () { sel = sel.length === opts.list.length ? [] : sorted().map(function (o) { return o.id; }); refreshDialog(); },
      pick: function (el) {
        var id = +el.getAttribute('data-v'), i = sel.indexOf(id);
        if (i >= 0) sel.splice(i, 1); else if (max === 1) sel = [id]; else if (sel.length < max) sel.push(id); else { toast('최대 ' + max + '명입니다'); return; }
        refreshDialog();
      },
      auto: function () {                       // 누를 때마다: 효과가 가장 큰 조합 ↔ 한 명만
        var n = (max > 1 && autoN % 2 === 1) ? 1 : max; autoN++;
        sel = opts.auto(n);
        toast(max === 1 ? '자동 선택' : (n > 1 ? '자동 ' + sel.length + '명 — 다시 누르면 1명' : '자동 1명'), 1800);
        refreshDialog();
      },
      alt: function () {                                           // 덧붙는 단추(등용의 [설전] 등): 표를 닫고 그 일을 한다
        if (sel.length < min) return toast('무장을 먼저 고르세요');
        var os = sel.map(off);
        if (!opts.alt.can(os)) return toast(opts.alt.why(os), 3000);
        closeDialog(); opts.alt.go(os);
      },
      ok: function () {
        if (sel.length < min) return;
        var os = sel.map(off);
        if (opts.keep) { cb(os); return; }                       // 다음 창이 이 표 위에 겹쳐 열린다
        var m = MODAL, stk = MSTACK.slice(), sc = dlgScroll();
        closeDialog();
        if (cb(os) === false && !MODAL) { MSTACK = stk; MODAL = m; paintDialog(sc); }   // 명령이 안 됐으면(금·행동력 부족 등) 표를 그대로 둔다
      }
    }
  }, !!opts.push);
}
function ids(os) { return os.map(function (o) { return o.id; }); }

/* 무장 상세 — 몸통(officerBody)은 창(showOfficer)과, 얼굴을 누르면 겹쳐 뜨는 카드(ocardOpen, v0.18)가 함께 쓴다 */
function officerBody(o) {
  var apt = ['창', '극', '노', '기', '병기'], a = '', i;
  for (i = 0; i < 5; i++) a += '<div class="' + o.apt.charAt(i) + '">' + apt[i] + '<b>' + o.apt.charAt(i) + '</b></div>';
  var bars = '', ks = [['ldr', '통솔'], ['war', '무력'], ['int', '지력'], ['pol', '정치'], ['cha', '매력']];
  for (i = 0; i < 5; i++) bars += '<div class="bar"><span>' + ks[i][1] + '</span><i><u style="width:' + o[ks[i][0]] + '%"></u></i><b>' + o[ks[i][0]] + '</b></div>';
  var un = o.unit !== null && o.unit !== undefined ? UMAP[o.unit] : null;
  var where = o.st === 'free' ? '재야 (' + G.bases[o.loc].n + ')' : o.st === 'captive' ? '포로 (' + G.bases[o.loc].n + ')' : (o.unit !== null ? '출진 중' : G.bases[o.loc].n);
  return '<div class="card">' + sceneTag(o) + '<div class="bars">' + bars + '</div></div>' +
    '<div class="sec">병종 적성</div><div class="apt">' + a + '</div>' +
    (o.sk ? '<p class="skp"><b class="hi">특기 · ' + o.sk + '</b><br>' + SKILLS[o.sk] + '</p>' : '<p class="note">특기 없음</p>') +
    (bioOf(o) ? '<div class="sec bioh">열전</div><p class="bio">' + bioOf(o) + '</p>' : '') +                  // v0.19: 어떤 사람인가(적성의 곱은 도움말로 옮겼다)
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
/* ---------- HUD ---------- */
function pendingUnits() { return directUnits(G.player).filter(function (u) { return !u.done && !(u.dest >= 0) && !u.moved; }); }      // v0.10: 군단의 부대는 군단장이 움직인다
function refreshHud() {
  if (!G) return;
  var F = G.factions[G.player], L = off(F.lord);
  $('hudY').textContent = G.year + '년'; $('hudM').textContent = G.month + '월 ' + ['상순', '중순', '하순'][G.xun];
  var hf = $('hudFac'); hf.children[0].style.background = F.color; hf.children[1].style.backgroundImage = POR_URL[L.por] ? 'url(' + POR_URL[L.por] + '),var(--porbg)' : ''; hf.children[2].textContent = F.name + '군';
  $('hudAPv').textContent = F.ap; $('hudAPb').style.width = Math.round(F.ap / 255 * 100) + '%';
  var g = 0, fd = 0, t = 0;
  facBases(G.player).forEach(function (b) { g += b.gold; fd += b.food; t += b.troops; });
  facUnits(G.player).forEach(function (u) { t += u.troops; });
  $('hudRes').innerHTML = '<span>' + ico('gold') + '<b>' + fmt(g) + '</b></span><span>' + ico('food') + '<b>' + fmt(fd) + '</b></span><span>' + ico('troops') + '<b>' + fmt(t) + '</b></span><span>' + ico('dur') + '<b>' + facCities(G.player).length + '</b>성</span>';
  var n = pendingUnits().length;
  $('btnNext').querySelector('.n').textContent = n ? n : '';
  $('btnNext').style.display = facUnits(G.player).length ? '' : 'none';
  barFit();
}
/* v0.20: 아래 줄이 화면보다 넓으면(좁은 화면에서 '다음 부대 N'이 떴을 때) 글씨와 여백을 한 단계씩 줄인다 — '턴 종료'가 잘리지 않게 */
function barOver(b) {
  var bs = b.querySelectorAll('button'), r = b.getBoundingClientRect();      // 줄 전체의 너비(scrollWidth)는 보지 않는다 — 붓 획(가짜 요소)이 양옆으로 조금 나와 있다
  for (var i = 0; i < bs.length; i++) { if (bs[i].style.display === 'none') continue; if (bs[i].scrollWidth > bs[i].clientWidth + 1 || bs[i].getBoundingClientRect().right > r.right - 5) return true; }
  return false;
}
function barFit() {
  var b = $('bar'), cls = ['t1', 't2', 't3'], i; if (!b || !b.clientWidth) return;
  b.classList.remove('t1', 't2', 't3');
  for (i = 0; i < cls.length && barOver(b); i++) b.classList.add(cls[i]);
}
/* ---------- v0.18 가늠: 확률을 숫자 대신 말로 ----------
   UI.pct(메뉴 → 확률 표시)가 켜져 있으면 예전처럼 % 로. 꺼져 있으면(기본) 말로 보인다 — 가늠하는 이는 군사와 군주 가운데 지력이 높은 쪽.
   그 지력이 ODDS_FINE 이상이면 다섯 단계로 또렷이, 아니면 셋으로 어림해서만 보인다(똑똑한 군사를 둘 까닭이 하나 더 생긴다). 규칙의 확률은 그대로다.
   pcT = 글 속의 한 마디 · pcG = 말 + 눈금 다섯 칸 · pcBest = '최고 N%' 자리 · pcWas = 지난 일의 '(성공률 N%)' 자리 · accT = 군사의 조언이 맞을 확률 */
var ODDS_FINE = 70;
var ODDS_W = ['불가', '매우 낮음', '낮음', '반반', '높음', '매우 높음', '확실'], ODDS_WC = ['불가', '낮은 듯', '낮은 듯', '반반인 듯', '높은 듯', '높은 듯', '확실'];
function oddsEye() {
  if (!G || !(G.player >= 0)) return { o: null, adv: false, fine: true };
  var su = typeof selUnit === 'function' ? selUnit() : null;       // v0.20: 부대를 고른 동안(싸움터)에는 그 부대의 참모가 가늠한다
  if (su && su.f === G.player && su.off && su.off.length) { var S = uStaff(su); return { o: S, adv: false, staff: true, lead: S === uLeader(su), fine: S.int >= ODDS_FINE }; }
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
  if (e.staff) return '<p class="note eye">가늠 — ' + (e.lead ? '주장 ' : '부장 ') + '<b>' + e.o.n + '</b> (통솔 ' + e.o.ldr + ' · 지력 ' + e.o.int + ') · ' + (e.fine ? '또렷이 봅니다' : '어림으로만 봅니다 <small>지력 ' + ODDS_FINE + ' 이상의 부장을 붙이면 또렷해집니다</small>') + '</p>';
  return '<p class="note eye">가늠 — ' + (e.adv ? '군사 ' : '군주 ') + '<b>' + e.o.n + '</b> (지력 ' + e.o.int + ') · ' + (e.fine ? '또렷이 봅니다' : '어림으로만 봅니다 <small>지력 ' + ODDS_FINE + ' 이상의 군사를 두면 또렷해집니다</small>') + '</p>';
}
/* ---------- 군사의 조언(v0.9) ---------- */
function advMark(a) { return a ? '<i class="adv ' + (a.says ? 'y' : 'n') + '">' + (a.says ? '○' : '×') + '</i>' : ''; }
function advLine(a) { return a ? '군사 ' + a.adv.n + ': <b class="' + (a.says ? 'ok' : 'bad') + '">' + (a.says ? '통할 것입니다' : '어렵겠습니다') + '</b> <small>' + accT(a.acc) + '</small>' : ''; }
function searchAdvice(b, o) { return advise(G.player, searchRoll(b), searchRollA(b), searchChance(b, o), 0); }      // 탐색(v0.11): 숨은 인재를 오늘 만나는가
function recruitAdvice(b, o, t) { return advise(G.player, recruitRoll(t), recruitRollA(t), recruitChance(b, o, t), t.int); }
function ployAdvice(u, pl, t) { return adviseBy(uStaff(u), ployRoll(pl, t), ployRollA(pl, t), ployChance(u, pl, t.u || null), t.u ? uInt(t.u) : 0); }      // v0.20: 싸움터의 조언은 부대의 참모가
/* v0.20 예상 피해: 참모의 통솔이 낮을수록 실제와 벌어진다(같은 턴 · 같은 상대에게는 같은 값). 숫자로 보기를 켜면 정확한 값 */
function dmgEst(u, t, v) {
  var err = staffErr(uStaff(u)); v = Math.round(v);
  if (UI.pct || err <= 0 || v <= 0) return '-' + fmt(v);
  var g = v * (1 + (omenRoll('est|' + u.id + '|' + (t && t.id !== undefined ? t.id : 'b')) / 50 - 1) * err), st = g >= 1000 ? 100 : (g >= 200 ? 50 : 10);
  return '약 -' + fmt(Math.max(st, Math.round(g / st) * st));
}
/* 거점 b 에서 대상 t 에게 가장 잘 권하는 쉬는 무장과 그때의 성공률·조언 { o, p, adv } (쉬는 무장이 없으면 o = null) */
function bestRecruiter(b, t) {
  var bo = null, bp = -1; idleOfficers(b).forEach(function (o) { var q = recruitChance(b, o, t); if (q > bp) { bp = q; bo = o; } });
  return { o: bo, p: Math.max(0, bp), adv: bo ? recruitAdvice(b, bo, t) : null };
}
/* 옛 관계(v0.11)를 글로 */
function originTxt(t) {                                    // 어디 출신인가: 지금 섬기는 세력(포로) 또는 마지막으로 섬긴 세력
  var f = t.f >= 0 ? t.f : lastF(t); if (f < 0 || !G.factions[f]) return '';
  return (t.f >= 0 ? '' : '옛 ') + G.factions[f].name + '군' + (G.factions[f].alive ? '' : ' · 멸망');
}
function whyTxt(x) { return x.why.map(function (w) { return w[0] + ' <b' + (w[1] < 0 ? ' class="bad"' : '') + '>' + (w[1] >= 0 ? '+' : '−') + Math.abs(w[1]) + '</b>'; }).join(' · '); }
function servedTxt(o) { return servedF(o).map(function (f) { return G.factions[f].name + '군' + (G.factions[f].alive ? '' : '(멸망)'); }).join(' · '); }
/* 군사가 "응할 것"이라고 보는 이웃 무장(가장 잘하는 무장을 보냈을 때) */
function poachHints(b) {
  var out = [];
  if (!idleOfficers(b).length) return out;
  poachTargets(b).forEach(function (t) { if (askWait(t)) return; var x = bestRecruiter(b, t); if (x.p >= COUNSEL.poachMin && x.adv && x.adv.says) out.push({ t: t, p: x.p, adv: x.adv }); });      // v0.11: 성공률이 낮은 '응할 것'은 거의 헛짚은 것이라 먼저 권하지 않는다
  return out.sort(function (x, y) { return y.p - x.p; });
}
function advTag(o) { return (o.f >= 0 && facAdv(o.f) === o) ? '군사' : ''; }
function showAdvisor() {
  var f = G.player;
  showDialog({
    render: function () {
      var A = facAdv(f), cs = advCandidates(f), i, h = dlgHead('군사 임명') + '<div class="dlg-b"><p class="cap">군사는 등용·계략이 통할지 미리 말해 줍니다. 지력이 곧 적중률입니다.</p>';
      if (A) h += '<div class="card advc">' + porTag(A, 'md') + '<div><p><b class="hi">' + A.n + '</b> 지력 ' + A.int + '</p><p class="note">' + (UI.pct ? '적중률 <b>' + adviceAcc(A, 0) + '%</b>' + (A.int < 95 ? ' <small>· 지력 95인 상대에게는 ' + adviceAcc(A, 95) + '%</small>' : '') : '조언 — <b>' + accT(adviceAcc(A, 0)) + '</b>' + (A.int < 95 ? ' <small>· 지력 95인 상대에게는 ' + accT(adviceAcc(A, 95)) + '</small>' : '')) + '</p></div></div>';
      else h += '<p class="note bad">군사가 없습니다 — 아래에서 임명하세요.</p>';
      h += '<div class="sec">후보 <em class="cnt">' + cs.length + '</em></div><div class="rows advl">';
      for (i = 0; i < cs.length; i++) {
        var o = cs[i], cur = A && A.id === o.id;
        h += '<div class="row' + (cur ? ' sel' : '') + '">' + porTag(o) + '<span class="mid"><span class="nm">' + o.n + (cur ? ' <em class="advt">군사</em>' : '') + '</span><span class="ds">지력 <b>' + o.int + '</b> · ' + (o.unit !== null ? '출진 중' : G.bases[o.st === 'travel' ? o.dest : o.loc].n) + '</span></span>' +
          (cur ? '<span class="rt hi">지금의 군사</span>' : '<button class="btn pri" type="button" data-a="set" data-v="' + o.id + '">임명</button>') + '</div>';
      }
      if (!cs.length) h += '<p class="note">군사로 삼을 무장이 없습니다.</p>';
      return h + '</div></div>';
    },
    on: { set: function (el) { var o = off(+el.getAttribute('data-v')), r = setAdvisor(f, o.id); if (!r.ok) return toast(r.msg); sfx('ui'); talk(o, sayLine(o, 'advisor'), josa(o.n, '을를') + ' 군사로 삼았습니다 (지력 ' + o.int + ')'); refreshDialog(); refreshSheet(); } }
  }, true);
}
/* ---------- 상태 이상(혼란·위보·불길)을 글로 ---------- */
function stChips(u) {
  var h = '', n = statusLeft(u);
  if (u.status) h += '<b class="stc st-' + u.status + '">' + statusName(u.status) + (n > 0 ? ' ' + days(n) : ' · 곧 풀림') + '</b>';
  if (unitOnFire(u)) h += '<b class="stc st-fire">불길</b>';
  return h;
}
function statusLeftText(u) {
  var n = statusLeft(u);
  if (n <= 0) return '다음 차례에 풀립니다';
  if (u.f === G.player && u.stSkip === G.turn) return n === 1 ? '이번 턴만 — 다음 턴에 풀립니다' : '이번 턴 포함 ' + days(n);
  return '앞으로 ' + days(n);
}
function statusBanner(u) {
  var h = '';
  if (u.status === 'confuse') h += '<div class="stb st-confuse"><b>혼란</b><i>' + statusLeftText(u) + '</i><span>행동 불가 · 받는 피해 +25% · 반격 없음</span></div>';
  else if (u.status === 'rumor') h += '<div class="stb st-rumor"><b>위보</b><i>' + statusLeftText(u) + '</i><span>명령 불가 · 자기 거점 쪽으로 후퇴 · 반격 없음</span></div>';
  if (unitOnFire(u)) {
    var ft = G.fires[K(u.c, u.r)];
    h += '<div class="stb st-fire"><b>불길 속</b><i>' + (ft <= 1 ? '이번 턴이 지나면 꺼집니다' : '불은 ' + days(ft) + ' 더 탑니다') + '</i><span>' + (uHas(u, '화신') ? '화신 — 불에 다치지 않음' : '턴마다 병력 −250~400 · 기력 −5') + '</span></div>';
  }
  return h;
}
function afterAction() { requestDraw(); refreshHud(); if (SHEET && SHEET.home) refreshSheet(); if (G.over) showGameOver(); }

/* ---------- STATUS 창: 늘 떠 있는 세력 현황 + 지금 할 일 ---------- */
var HOME = { open: true };
function facTotals(f) {
  var t = { gold: 0, food: 0, troops: 0, gi: 0, fi: 0, cities: 0, gates: 0, off: 0, units: 0, idle: 0 };
  facBases(f).forEach(function (b) {
    t.gold += b.gold; t.food += b.food; t.troops += b.troops; t.gi += goldIncome(b); t.fi += foodIncome(b);
    if (b.kind === 'city') t.cities++; else t.gates++;
    t.idle += idleOfficers(b).length;
  });
  facUnits(f).forEach(function (u) { t.troops += u.troops; t.units++; });
  t.off = facOfficers(f).length;
  return t;
}
function minFacCost() { var m = 1e9; for (var i = 0; i < FAC_ORDER.length; i++) m = Math.min(m, FAC[FAC_ORDER[i]].cost); return m; }
/* 쉬는 무장이 있는 거점에서 지금 해 볼 만한 일 (많아야 두 가지). tab = 첫 번째 일을 할 수 있는 탭 */
/* 빈 부지 옆에 무엇이 있는가(조폐는 시장 옆, 곡창은 농장 옆에 지어야 하므로) */
function plotNear(b, i) {
  var p = b.plots[i], ns = nbrs(p.c, p.r), cnt = {}, out = [];
  for (var j = 0; j < ns.length; j++) { var q = PAT[K(ns[j][0], ns[j][1])]; if (q && q.b === b.id) { var f = b.plots[q.i].fac; if (f) cnt[f.t] = (cnt[f.t] || 0) + 1; } }
  FAC_ORDER.forEach(function (t) { if (cnt[t]) out.push(FAC[t].name + (cnt[t] > 1 ? ' ' + cnt[t] : '')); });
  return out.length ? '옆: ' + out.join(' · ') : '옆에 시설 없음';
}
/* ---------- 건설 자리 ----------
   건설을 고른 동안(거점의 시설 탭, '무엇을 지을까요' 창과 그 위에 겹친 담당 무장 표) 지도는 어두워지고 지을 수 있는 빈 부지만 밝다 — 그리는 일은 ui3d.js 의 spotDraw.
   빈 부지에는 목록과 지도에서 같은 번호가 붙는다(b.plots 의 순서대로 1, 2, 3 …). */
function emptyLots(b) { var out = []; for (var i = 0; i < b.plots.length; i++) if (!b.plots[i].fac) out.push(i); return out; }
/* 부지의 번호(v0.9.3): 성을 가운데 두고 북쪽에서 시계 방향으로 1, 2, 3 …(같은 방향이면 가까운 것 먼저). 부지마다 정해져 있어 무엇을 지어도 바뀌지 않는다 */
var LOTNO = {};
function lotNos(b) {
  var m = LOTNO[b.id], i;
  if (m && m.length === b.plots.length) return m;
  var c0 = hexCenter(b.c, b.r), idx = [];
  for (i = 0; i < b.plots.length; i++) { var q = hexCenter(b.plots[i].c, b.plots[i].r), dx = q[0] - c0[0], dz = q[1] - c0[1]; idx.push({ i: i, a: Math.round(((Math.atan2(dx, -dz) + 2 * Math.PI) % (2 * Math.PI)) * 1e6), d: dx * dx + dz * dz }); }
  idx.sort(function (x, y) { return x.a - y.a || x.d - y.d; });
  m = []; for (i = 0; i < idx.length; i++) m[idx[i].i] = i + 1;
  return (LOTNO[b.id] = m);
}
function lotNo(b, pi) { return lotNos(b)[pi]; }
function emptyLotsByNo(b) { return emptyLots(b).sort(function (x, y) { return lotNo(b, x) - lotNo(b, y); }); }      // 빈 부지를 번호 차례로
function lotMark(n) { return n >= 1 && n <= 20 ? String.fromCharCode(0x245F + n) : '(' + n + ')'; }      // ① ② ③ …
function buildWhy(b) {                                         // 지금 이 거점에서 아무것도 지을 수 없는 까닭('' = 지을 수 있다)
  if (!idleOfficers(b).length) return '쉬는 무장이 없습니다';
  if (b.gold < minFacCost()) return '금이 모자랍니다 (' + minFacCost() + ' 필요)';
  if (!needAP(b.owner, AP.develop)) return '행동력이 모자랍니다';
  return '';
}
function devOf() { if (MODAL && MODAL.dev) return MODAL.dev; for (var i = MSTACK.length - 1; i >= 0; i--) if (MSTACK[i].d.dev) return MSTACK[i].d.dev; return null; }
/* 시설 창(흡수합병 · 철거)이 떠 있으면 그 시설 { b, pi } — 지도에서 그 시설을 표시한다(v0.10.1) */
function fselOf() { if (MODAL && MODAL.fsel) return MODAL.fsel; for (var i = MSTACK.length - 1; i >= 0; i--) if (MSTACK[i].d.fsel) return MSTACK[i].d.fsel; return null; }
function buildView() {
  if (!G || G.over || UI.play || UI.busy) return null;
  var d = devOf(), fs = d ? null : fselOf(), b = d ? G.bases[d.b] : (fs ? G.bases[fs.b] : (SHEET && SHEET.fac ? SHEET.fac() : null));
  if (!b || b.owner !== G.player || b.kind !== 'city') return null;
  var why = buildWhy(b), pi = d ? d.pi : -1, fi = (fs && b.plots[fs.pi] && b.plots[fs.pi].fac) ? fs.pi : -1, sig = b.id + '/' + pi + '/' + fi + '/' + why + '/', lots = [], facs = [];
  for (var i = 0; i < b.plots.length; i++) {
    var p = b.plots[i];
    if (p.fac) { var left = p.fac.done ? '' : days(Math.max(1, Math.ceil((p.fac.need - p.fac.prog) / Math.max(1, p.fac.rate)))); facs.push({ i: i, no: lotNo(b, i), c: p.c, r: p.r, n: FAC[p.fac.t].name, done: p.fac.done, left: left }); sig += 'f' + i + p.fac.t + (p.fac.done ? '' : 'c' + left) + ','; }
    else { var ok = !why && !UAT[K(p.c, p.r)]; lots.push({ i: i, c: p.c, r: p.r, n: lotNo(b, i), ok: ok }); sig += i + (ok ? '' : 'x') + ','; }
  }
  if (!lots.length && fi < 0) return null;                     // 빈 부지도, 고른 시설도 없으면 비출 것이 없다
  lots.sort(function (x, y) { return x.n - y.n; });
  return { b: b, pi: pi, fi: fi, why: why, lots: lots, facs: facs, sig: sig };
}
/* '무엇을 지을까요' 창이 떠 있는 동안 지도를 눌렀다: 다른 빈 부지면 자리를 바꾸고, 이 거점의 시설이면 그 시설의 창으로, 그 밖이면 창을 닫는다 */
function devTap(c, r) {
  var d = MODAL.dev, b = G.bases[d.b], pl = plotAt(c, r);
  if (pl && pl.base === b && pl.plot.fac) { sfx('ui'); flowFacility(b, pl.i); return; }
  if (pl && pl.base === b && !pl.plot.fac) {
    if (UAT[K(c, r)]) { toast('부대가 서 있는 칸에는 지을 수 없습니다'); return; }
    if (pl.i !== d.pi) { d.pi = pl.i; sfx('ui'); refreshDialog(); }
    return;
  }
  backDialog();
}
/* 시설 창이 떠 있는 동안 지도를 눌렀다: 같은 거점의 다른 시설이면 그 시설로, 빈 부지면 '무엇을 지을까요'로, 그 밖이면 창을 닫는다(v0.10.1) */
function fselTap(c, r) {
  var f = MODAL.fsel, b = G.bases[f.b], pl = plotAt(c, r);
  if (pl && pl.base === b) {
    if (pl.plot.fac) { if (pl.i !== f.pi) { sfx('ui'); flowFacility(b, pl.i); } return; }
    flowDevelop(b, pl.i); return;                              // 지을 수 없으면 까닭을 알리고 이 창은 그대로 둔다
  }
  backDialog();
}
/* 이 자리에 지으면 늘어나는 수입(금/월, 병량/분기) — 수입 셈(goldIncome·foodIncome)을 그대로 돌려 본 값이라 인접·치안·특기가 다 들어 있다 */
function gainAt(b, pi, t) {
  var p = b.plots[pi], g0 = goldIncome(b), f0 = foodIncome(b);
  p.fac = { t: t, lv: 1, done: true };
  var g1 = goldIncome(b), f1 = foodIncome(b);
  p.fac = null;
  return { gold: g1 - g0, food: f1 - f0 };
}
/* ---------- 시설의 풀이(v0.11): 지금 레벨의 값을 먼저 적는다. FAC[t].desc 는 새로 지을 때(Lv1) 보는 카드용 ---------- */
function facLv(fc) { return facHasLv(fc.t) ? ' Lv' + fc.lv : ''; }                               // v0.18: 레벨이 없는 시설(공방 · 조폐 · 곡창)에는 적지 않는다
function lvTail(lv, f) { return lv >= 3 ? ' · 최고 레벨' : ' · Lv' + (lv + 1) + ' ' + f(lv + 1); }
function mulTxt(n) { return '×' + LV_MUL[n].toFixed(1); }
function facDesc(fc) {
  var lv = fc.lv || 1, t = fc.t;
  if (t === 'market') return '금 +' + fmt(MARKET_INC[lv]) + '/월' + lvTail(lv, function (n) { return '+' + fmt(MARKET_INC[n]); });
  if (t === 'farm') return '병량 +' + fmt(FARM_INC[lv]) + '/분기' + lvTail(lv, function (n) { return '+' + fmt(FARM_INC[n]); });
  if (t === 'barracks') return (lv > 1 ? '징병량 ' + mulTxt(lv) : '징병 가능') + lvTail(lv, function (n) { return (lv > 1 ? '' : '징병량 ') + mulTxt(n); });
  if (t === 'smithy') return (lv > 1 ? '창·극·노 생산량 ' + mulTxt(lv) : '창·극·노 생산') + lvTail(lv, function (n) { return (lv > 1 ? '' : '생산량 ') + mulTxt(n); });
  if (t === 'stable') return (lv > 1 ? '군마 생산량 ' + mulTxt(lv) : '군마 생산') + lvTail(lv, function (n) { return (lv > 1 ? '' : '생산량 ') + mulTxt(n); });
  if (t === 'workshop') return '충차 생산';
  if (t === 'mint') return '옆 시장의 수입 +50%';
  if (t === 'granary') return '옆 농장의 수입 +50%';
  return FAC[t].desc;
}
/* 이 시설이 실제로 보태는 수입 = 이 시설만 뺀 수입 셈과의 차이(옆의 조폐·곡창, 치안, 특기가 다 들어 있다). 짓는 중이면 다 지어졌다고 치고 센다 */
function facYield(b, pi) {
  var p = b.plots[pi], fc = p.fac, was = fc.done;
  fc.done = true; var g1 = goldIncome(b), f1 = foodIncome(b);
  p.fac = null; var g0 = goldIncome(b), f0 = foodIncome(b);
  p.fac = fc; fc.done = was;
  return { gold: g1 - g0, food: f1 - f0 };
}
/* 시설 창의 둘째 줄: 지금 이 자리에서 실제로 얼마를 보태는가, 왜 그 값인가 */
function facNow(b, pi) {
  var fc = b.plots[pi].fac, t = fc.t, lv = fc.lv, y = facYield(b, pi), pre = fc.done ? '지금 ' : '다 지으면 ', op = incPct(b.order), why = [], n, i;
  if (t === 'market' || t === 'farm') {
    var sup = t === 'market' ? 'mint' : 'granary', skl = t === 'market' ? '부호' : '미도';
    n = Math.min(2, adjFacCount(b, pi, sup));
    if (n) why.push('옆 ' + FAC[sup].name + ' ' + n + '곳 +' + n * 50 + '%');
    if (op < 100) why.push('치안 ' + b.order + ' → ' + op + '%');
    if (baseHasSkill(b, skl)) why.push(skl + ' +20%');
    return pre + (t === 'market' ? '금 <b>+' + fmt(y.gold) + '</b>/월' : '병량 <b>+' + fmt(y.food) + '</b>/분기') + (why.length ? ' <small>(' + why.join(' · ') + ')</small>' : '');
  }
  if (t === 'mint' || t === 'granary') {
    var v = t === 'mint' ? y.gold : y.food, pair = t === 'mint' ? '시장' : '농장';
    n = adjFacCount(b, pi, t === 'mint' ? 'market' : 'farm');
    if (!n) return '<span class="bad">옆에 다 지은 ' + pair + '이 없어 ' + (fc.done ? '지금은' : '다 지어도') + ' 보탬이 없습니다</span>';
    if (v <= 0) return '<span class="bad">옆 ' + pair + '에 이미 ' + FAC[t].name + ' 둘이 붙어 있어 보탬이 없습니다</span> <small>(한 곳에 둘까지)</small>';
    return pre + (t === 'mint' ? '금 <b>+' + fmt(v) + '</b>/월' : '병량 <b>+' + fmt(v) + '</b>/분기') + ' <small>(옆 ' + pair + ' ' + n + '곳)</small>';
  }
  if (t === 'workshop') { for (i = 0; i < b.plots.length; i++) { var g0 = b.plots[i].fac; if (i !== pi && g0 && g0.done && g0.t === t) return '이 도시에 공방이 또 있습니다 — <b>하나면 충분합니다</b>'; } return ''; }
  if (t === 'barracks' || t === 'smithy' || t === 'stable') {
    var best = 0, what = t === 'barracks' ? '징병량' : '생산량';
    for (i = 0; i < b.plots.length; i++) { var g = b.plots[i].fac; if (i !== pi && g && g.done && g.t === t && g.lv > best) best = g.lv; }
    if (best > lv) return '<span class="bad">이 도시에 Lv' + best + ' ' + FAC[t].name + '이 있어 이곳은 보탬이 없습니다</span> <small>(가장 높은 한 곳만 셉니다)</small>';
    if (best === lv) return '같은 레벨의 ' + FAC[t].name + '이 또 있습니다 — <b>한 곳만</b> 셉니다';
    return (fc.done ? '이 도시의 ' : '다 지으면 이 도시의 ') + what + ' <b>' + mulTxt(lv) + '</b> <small>(가장 높은 한 곳만 셉니다)</small>';
  }
  return '';
}
/* 흡수합병을 하면 달라지는 수입(금/월, 병량/분기) — 한 곳이 레벨 +1, 합쳐진 곳은 빈 부지가 된다 */
function mergeGain(b, pi, pj) {
  var f = b.plots[pi].fac, g = b.plots[pj].fac, g0 = goldIncome(b), f0 = foodIncome(b);
  f.lv++; b.plots[pj].fac = null;
  var g1 = goldIncome(b), f1 = foodIncome(b);
  f.lv--; b.plots[pj].fac = g;
  return { gold: g1 - g0, food: f1 - f0 };
}
function mergeNote(b, pi, pj) {
  var fc = b.plots[pi].fac, t = fc.t, mg = mergeGain(b, pi, pj), free = lotMark(lotNo(b, pj)) + ' 부지가 빕니다';
  function sg(v) { return (v >= 0 ? '+' : '−') + fmt(Math.abs(v)); }
  if (t === 'market' || t === 'mint') return '금 수입 <b' + (mg.gold < 0 ? ' class="bad"' : '') + '>' + sg(mg.gold) + '</b>/월 · ' + free;
  if (t === 'farm' || t === 'granary') return '병량 수입 <b' + (mg.food < 0 ? ' class="bad"' : '') + '>' + sg(mg.food) + '</b>/분기 · ' + free;
  if (t === 'workshop') return '충차 생산은 그대로 · ' + free;
  var cur = bestFacLv(b, t), nx = Math.max(cur, fc.lv + 1);
  return (t === 'barracks' ? '징병량 ' : '생산량 ') + mulTxt(cur) + ' → <b>' + mulTxt(nx) + '</b> · ' + free;
}
/* 카드 한 줄: 이 자리에 이 시설을 지으면 [글, 빛깔('' · ok · no · warn)] */
function lotEffect(b, pi, t) {
  var g, pair = { mint: 'market', granary: 'farm' }[t];
  if (t === 'market') return ['금 +' + fmt(gainAt(b, pi, t).gold) + '/월', ''];
  if (t === 'farm') return ['병량 +' + fmt(gainAt(b, pi, t).food) + '/분기', ''];
  if (pair) {                                                  // 조폐·곡창: 옆의 시장·농장 수입을 늘린다(한 곳에 둘까지)
    g = gainAt(b, pi, t); g = t === 'mint' ? g.gold : g.food;
    if (g > 0) return [(t === 'mint' ? '금 +' + fmt(g) + '/월' : '병량 +' + fmt(g) + '/분기'), ''];
    if (adjFacCount(b, pi, pair)) return ['효과 없음 (2곳까지)', 'no'];                              // 옆의 시장·농장에 이미 둘이 붙어 있다
    var p = b.plots[pi], soon = nbrs(p.c, p.r).some(function (q) { var x = PAT[K(q[0], q[1])], f = x && x.b === b.id ? b.plots[x.i].fac : null; return !!f && f.t === pair && !f.done; });
    return soon ? ['옆 ' + FAC[pair].name + ' 완공 뒤 효과', 'warn'] : ['옆에 ' + FAC[pair].name + ' 없음', 'no'];
  }
  var lv = bestFacLv(b, t), use = { barracks: '징병', smithy: '창·극·노 생산', stable: '군마 생산', workshop: '충차 생산' }[t];
  if (!lv) return b.plots.some(function (q) { return q.fac && q.fac.t === t; }) ? ['이미 짓는 중', 'warn'] : [use, ''];
  if (facHasLv(t) && lv < 3 && adjFacCount(b, pi, t)) return ['옆 ' + FAC[t].name + '과 합병 가능', 'ok'];      // 같은 시설이 옆에 있으면 합쳐서 레벨을 올릴 수 있다
  return ['이미 있음' + (facHasLv(t) ? ' (Lv' + lv + ')' : ''), 'warn'];                                                  // 떨어진 자리에 하나 더 지어도 쓰이는 것은 레벨 높은 쪽 하나다
}
/* ---------- 군사의 헌책(v0.11): 후보(core.js 의 counsel)를 말로 옮긴다 ----------
   lvl 2 = 숫자와 사람까지 · 1 = 무엇을 할지 · 0 = 두루뭉술하게.  → { say(군사의 말), tip(할 일 줄의 짧은 글), go, key, w } */
function counselText(c) {
  var b = G.bases[c.b], x = c.x, L = c.lvl, say = '', tip = '', go = ['base', b.id, 'home'], nb = x.nb !== undefined ? G.bases[x.nb] : null, t, o, P;
  function nbName() { return nb.n + (nb.owner >= 0 ? '(' + facName(nb.owner) + '군)' : ''); }
  function send(q, from) { return isLord(q) ? '주공께서 직접 권하십시오' : (from ? from + '의 ' : '') + josa(q.n, '을를') + ' 보내십시오'; }      // 군주가 가장 잘 권할 때
  if (c.kind === 'patrol') {
    o = off(x.by); tip = '치안 ' + x.order + ' → 순찰';
    say = L === 2 ? b.n + '의 치안이 ' + x.order + '까지 떨어져 수입이 ' + incPct(x.order) + '%뿐입니다. ' + (isLord(o) ? '주공께서 직접 순찰을 도십시오.' : o.n + '에게 순찰을 맡기십시오.') : (L === 1 ? b.n + '의 치안이 낮아 수입이 줄고 있습니다. 순찰을 돌리십시오.' : b.n + ' — 치안이 어지럽습니다. 순찰을 돌리십시오.');
  } else if (c.kind === 'patrol2') {
    tip = '치안 ' + x.order + ' → 순찰';
    say = L === 2 ? b.n + '의 치안은 ' + x.order + '(수입 ' + incPct(x.order) + '%)입니다. 여유가 있을 때 순찰로 더 올려 두시지요.' : b.n + ' — 여유가 있으면 순찰로 치안을 다져 두시지요.';
  } else if (c.kind === 'recruit') {
    P = x.pick; t = off(P.t); o = off(P.o); go = ['recruit', b.id];
    var kindN = t.st === 'captive' ? '포로' : '재야', tie = tieOf(o, t, b.owner);
    if (x.says === null || L === 0) { tip = '등용할 인재 ' + x.ts.length + '명'; say = b.n + ' — 부를 만한 인재가 ' + x.ts.length + '명 있습니다. 등용하시지요.'; }
    else if (x.says) { tip = t.n + ' 등용 <i class="adv y">응할 듯</i>'; say = L === 2 ? b.n + '의 ' + kindN + ' ' + t.n + '에게 ' + send(o) + (tie ? '(' + tie.short + ')' : '') + '. 응할 것입니다.' : b.n + '의 ' + josa(t.n, '은는') + ' 지금 부르면 응할 것입니다.'; }
    else { tip = kindN + ' ' + x.ts.length + '명 <i class="adv n">오늘은 불응</i>'; say = b.n + '의 ' + josa(t.n, '은는') + ' 오늘은 응하지 않겠습니다. 다음 턴에 다시 권하시지요.'; }
  } else if (c.kind === 'poach') {
    P = x.pick; t = off(P.t); o = off(P.o); go = ['recruit', b.id]; tip = L === 0 ? '이웃 무장 등용' : t.n + ' 등용 <i class="adv y">응할 듯</i>';
    say = L === 0 ? b.n + ' — 이웃 세력의 무장을 불러 보시지요.' : (L === 2 ? G.bases[t.loc].n + '의 ' + t.n + '(' + facName(t.f) + '군)에게 ' + send(o, b.n) + '. 응할 것입니다.' : b.n + '에서 ' + josa(t.n, '을를') + ' 부르면 응할 것입니다.');
  } else if (c.kind === 'search') {
    o = off(x.o); go = ['base', b.id, 'men'];
    if (L === 0) { tip = '탐색'; say = b.n + ' — 탐색으로 인재를 찾아보시지요.'; }
    else if (x.says) { tip = '탐색 <i class="adv y">만날 듯</i>'; say = L === 2 ? b.n + '에 숨은 인재가 있습니다. ' + (isLord(o) ? '주공께서 직접' : josa(o.n, '이가')) + ' 찾아 나서면 오늘 만날 것입니다.' : b.n + '에 숨은 인재가 있는 듯합니다. 탐색해 보시지요.'; }
    else { tip = '숨은 인재 <i class="adv n">오늘은 못 만남</i>'; say = b.n + '에 숨은 인재가 있는 듯하나, 오늘은 만나기 어렵겠습니다. 다음 턴에 찾아보시지요.'; }
  } else if (c.kind === 'reward') {
    t = off(x.t); go = ['base', b.id, 'men']; tip = t.n + ' 충성 ' + x.loy + ' → 포상';
    say = L === 2 ? b.n + '의 ' + josa(t.n, '은는') + ' 충성이 ' + x.loy + '입니다. 포상으로 마음을 잡아 두십시오.' : b.n + ' — 마음이 뜬 무장이 있습니다. 포상하시지요.';
  } else if (c.kind === 'train') {
    go = ['base', b.id, b.kind === 'city' ? 'home' : 'mil']; tip = '기력 ' + x.morale + ' → 훈련';
    say = L === 2 ? b.n + ' 병사들의 기력이 ' + x.morale + '입니다. 싸움에 앞서 훈련해 두십시오.' : b.n + ' — 군의 기력이 낮습니다. 훈련하십시오.';
  } else if (c.kind === 'draft') {
    tip = '병력 ' + fmt(x.troops) + ' < 이웃 ' + fmt(x.thr) + ' → 징병';
    if (L === 0) say = b.n + ' — 병사를 더 모으시지요.';
    else if (x.soon) say = L === 2 ? '이웃 ' + nbName() + '의 병력이 ' + fmt(x.thr) + '인데 ' + josa(b.n, '은는') + ' ' + fmt(x.troops) + '뿐입니다. 징병하십시오.' + (x.pl > 0 ? ' 보호는 ' + days(x.pl) + ' 남았습니다.' : '') : b.n + '의 병력이 이웃 ' + nb.n + '보다 적습니다. 징병하십시오.';
    else say = L === 2 ? '보호가 끝나기 전에 ' + b.n + '의 병력을 길러 두십시오. 이웃 ' + nbName() + '의 병력은 ' + fmt(x.thr) + '입니다.' : '보호가 끝나기 전에 ' + b.n + '의 병력을 길러 두시지요.';
  } else if (c.kind === 'build') {
    var FN = FAC[x.t].name, lm = lotMark(lotNo(b, x.pi)), gt = x.gain.gold ? '금 +' + fmt(x.gain.gold) + '/월' : (x.gain.food ? '병량 +' + fmt(x.gain.food) + '/분기' : '');
    go = ['base', b.id, 'fac'];
    if (L === 0) { tip = '빈 부지 ' + x.empty + '곳 → 건설'; say = b.n + ' — 빈 부지가 ' + x.empty + '곳 있습니다. 시설을 지으시지요.'; }
    else {
      tip = lm + ' ' + FN + (gt ? ' ' + gt : '');
      if (x.why === 'nobarracks') say = b.n + '에 병영이 없어 징병을 못 합니다. ' + (L === 2 ? lm + ' 부지에 ' : '') + '병영을 지으십시오.';
      else if (x.why === 'food') say = L === 2 ? b.n + '의 병량 수입(분기 +' + fmt(x.fi) + ')이 군량(분기 −' + fmt(x.upkeep) + ')에 못 미칩니다. ' + lm + ' 부지에 농장을 지으십시오.' : b.n + '의 병량 수입이 군량에 못 미칩니다. 농장을 지으십시오.';
      else say = L === 2 ? b.n + ' ' + lm + ' 부지에 ' + josa(FN, '을를') + ' 지으면 ' + gt + '입니다.' : b.n + '에 ' + josa(FN, '을를') + ' 더 지으시지요.';
    }
  } else if (c.kind === 'produce') {
    tip = '무기 ' + fmt(x.arms) + ' → 생산';
    say = L === 2 ? b.n + '의 병력 ' + fmt(x.troops) + '에 창·극·노가 ' + fmt(x.arms) + '뿐입니다. 대장간을 돌리십시오.' : b.n + ' — 무기가 모자랍니다. 생산하시지요.';
  } else if (c.kind === 'buyfood') {
    tip = '병량 ' + days(x.ft) + '분 → 거래';
    say = L === 2 ? b.n + '의 병량이 ' + days(x.ft) + '분뿐입니다. 금으로 병량을 사 두십시오(금 1에 병량 4).' : b.n + ' — 병량이 모자랍니다. 거래로 사 두십시오.';
  } else if (c.kind === 'sellfood') {
    tip = '금 ' + fmt(x.gold) + ' → 병량 팔기';
    say = L === 2 ? b.n + '의 금이 ' + fmt(x.gold) + '뿐입니다. 남는 병량을 팔아 금을 마련하시지요(병량 6에 금 1).' : b.n + ' — 금이 모자랍니다. 남는 병량을 파시지요.';
  } else if (c.kind === 'vacant') {
    go = ['base', b.id, 'mil']; tip = '빈 ' + nb.n + ' → 출진';
    say = L === 0 ? b.n + ' — 군을 낼 수 있습니다.' : '이웃 ' + josa(nb.n, '이가') + ' 주인 없이 비어 있습니다. ' + b.n + '에서 군을 보내 차지하십시오.';
  } else if (c.kind === 'strike') {
    go = ['base', b.id, 'mil']; tip = nb.n + ' 수비 ' + fmt(x.def) + ' → 출진';
    say = L === 0 ? b.n + ' — 군을 낼 수 있습니다.' : (L === 2 ? nbName() + '의 수비는 ' + fmt(x.def) + '뿐입니다. ' + b.n + '의 ' + fmt(x.troops) + '이면 칠 만합니다.' : nb.n + '의 수비가 허술합니다. ' + b.n + '에서 군을 내시지요.') + (x.brk ? ' 다만 먼저 치면 그 세력과의 보호가 풀립니다.' : '');
  }
  return { say: say, tip: tip, go: go, key: c.key, w: c.w, kind: c.kind };
}
/* 거점 줄의 조언: 그 거점에 대한 헌책 가운데 앞의 둘 */
function baseAdvice(b, cs) {
  var n = idleOfficers(b).length; if (!n) return null;
  var L = (cs || counsel(G.player)).list.filter(function (c) { return c.b === b.id; }); if (!L.length) return null;
  var tx = L.slice(0, 2).map(counselText);
  return { n: n, tips: tx.map(function (t) { return t.tip; }), tab: tx[0].go[0] === 'recruit' ? 'men' : tx[0].go[2], say: tx[0].say };
}
/* 지금 군사가 말할 헌책 하나: 한 번 한 말은 COUNSEL.keep 턴 동안 맨 앞에 세우지 않는다(급한 것은 예외). [다른 조언]을 누르면 다음 것 */
function counselPick(cs) {
  if (!cs || !cs.list.length) return null;
  if (UI.cGame !== G.seed0 || UI.cTurn > G.turn) { UI.cGame = G.seed0; UI.cSaid = {}; UI.cKind = {}; UI.cTurn = -1; }      // 다른 판을 열었다
  if (UI.cTurn !== G.turn) { UI.cTurn = G.turn; UI.cSkip = 0; }
  function ok(c, t) { return c.w >= COUNSEL.urgent || t === undefined || t === G.turn || G.turn - t > COUNSEL.keep; }
  var fresh = cs.list.filter(function (c) { return ok(c, UI.cSaid[c.key]); });
  var L = fresh.length ? fresh : cs.list, front = [], back = [];
  L.forEach(function (c) { (ok(c, UI.cKind[c.kind]) ? front : back).push(c); });      // 같은 종류의 말(징병 · 건설 …)도 잇달아 하지 않는다: 지난 두 턴에 한 종류는 뒤로 돌린다
  L = front.concat(back);
  var i = UI.cSkip % L.length, x = counselText(L[i]);
  UI.cSaid[L[i].key] = G.turn; UI.cKind[L[i].kind] = G.turn;
  x.n = L.length; x.i = i; x.cns = 1;
  return x;
}
/* 지금 할 일: 급한 것부터. 항목 {cls, ic, num, t, s, go:[종류, id], lb} */
function peaceNote() {                       // 초반 보호 풀이(창과 도움말에서 함께 쓴다)
  var P = G.peace, left = peaceLeft(), br = peaceBroken().map(function (k) { return facName(k) + '군'; });
  var h = '<div class="help">';
  if (left > 0) h += '<p><b>' + dateOfTurn(P.until - 1) + '까지</b> (' + days(left) + ' 남음) 다른 세력이 우리 <b>거점과 시설</b>을 먼저 치지 않습니다.</p>';
  else h += '<p>초반 보호는 <b>' + dateOfTurn(P.until - 1) + '</b>에 끝났습니다.' + (G.turn < P.until + PEACE_RAMP ? ' <b>' + dateOfTurn(P.until + PEACE_RAMP - 1) + '</b>까지는 완충 기간입니다.' : '') + '</p>';
  if (br.length) h += '<p class="bad"><b>먼저 친 세력: ' + br.join(' · ') + '</b> — 이 세력은 지금도 우리를 칠 수 있습니다.</p>';
  return h + '<ul><li><b>우리가 먼저 친 세력</b>과는 보호가 풀립니다.</li>' +
    '<li>들판의 부대끼리는 싸울 수 있고, 빈 성은 누구나 차지합니다.</li>' +
    '<li>끝난 뒤 ' + months(PEACE_RAMP) + '은 <b>완충 기간</b> — 한 번에 한 세력만 치러 옵니다.</li></ul></div>';
}
function showPeaceInfo() { showDialog({ render: function () { return dlgHead('초반 보호') + '<div class="dlg-b">' + peaceNote() + '</div>'; }, on: {} }); }
function todoList() {
  var f = G.player, F = G.factions[f], out = [], all = facBases(f), bs = directBases(f), us = directUnits(f), seen = {};      // v0.10: 할 일은 직할 거점·직할 부대만. 적이 다가온 것은 군단의 거점도 알린다
  all.forEach(function (b) {
    var es = enemyUnitsNear(f, b.c, b.r, 4); if (!es.length) return;
    var t = 0; es.forEach(function (e) { t += e.troops; });
    es.sort(function (x, y) { return hdist(b.c, b.r, x.c, x.r) - hdist(b.c, b.r, y.c, y.r); });
    out.push({ cls: 'warn', ic: '!', t: b.n + ' 가까이 적 ' + es.length + '부대', s: facName(es[0].f) + '군 ' + fmt(t) + '명 · ' + hdist(b.c, b.r, es[0].c, es[0].r) + '칸', go: ['unit', es[0].id], lb: '보기', info: baseCorps(b) ? 1 : 0, say: b.n + ' 가까이 ' + facName(es[0].f) + '군 ' + es.length + '부대가 와 있습니다. 대비하십시오.' });
  });
  us.forEach(function (u) {
    if (u.done || !attackTargets(u).length) return;
    seen[u.id] = 1;
    out.push({ cls: 'warn', ic: '⚔', t: uName(u) + ' — 적과 맞닿음', s: '', go: ['unit', u.id], lb: '명령', say: josa(uName(u), '이가') + ' 적과 맞닿아 있습니다. 명을 내리십시오.' });
  });
  us.forEach(function (u) {
    if (u.status) out.push({ cls: 'warn', ic: u.status === 'confuse' ? '亂' : '僞', t: uName(u) + ' — ' + statusName(u.status) + ' (' + statusLeftText(u) + ')', s: '', go: ['unit', u.id], lb: '보기', info: 1, say: josa(uName(u), '이가') + ' ' + statusName(u.status) + '에 빠졌습니다.' });
    if (unitOnFire(u) && !uHas(u, '화신')) out.push({ cls: 'warn', ic: '火', t: uName(u) + ' — 불길 속', s: '', go: ['unit', u.id], lb: '보기', info: 1, say: josa(uName(u), '이가') + ' 불길 속에 있습니다. 어서 빼내십시오.' });
  });
  duelAsks().forEach(function (x) {                             // v0.16: AI 가 걸어온 일기토
    var a = UMAP[x.a], d = UMAP[x.d], la = uLeader(a), ld = uLeader(d);
    out.push({ cls: 'warn', ic: '鬪', t: facName(a.f) + '군 ' + josa(la.n, '이가') + ' ' + ld.n + '에게 일기토를 걸어왔습니다', s: '무력 ' + la.war + ' 대 ' + ld.war + ' · 이번 턴 안에 답해야 합니다', go: ['duelask', x.a, x.d], lb: '답하기', say: josa(la.n, '이가') + ' ' + ld.n + '에게 일기토를 걸어왔습니다. 받을지 정하십시오.' });
  });
  dipOffers().forEach(function (x) {                            // v0.14: AI 가 청해 온 정전 · 동맹
    out.push({ cls: 'cool', ic: '盟', t: facName(x.from) + '군이 ' + PACT_NAME[x.kind] + '을 청해 왔습니다', s: '이번 턴 안에 답해야 합니다 · 우호 ' + relOf(f, x.from), go: ['dip', x.from, x.kind], lb: '답하기', say: facName(x.from) + '군이 ' + PACT_NAME[x.kind] + '을 청해 왔습니다. 답을 정하십시오.' });
  });
  pendingUnits().forEach(function (u) {
    if (seen[u.id]) return; seen[u.id] = 1;
    out.push({ ic: '▶', t: uName(u) + ' — 명령 대기', s: UNIT_TYPES[u.type].name + ' ' + fmt(u.troops) + '명', go: ['unit', u.id], lb: '명령', say: josa(uName(u), '이가') + ' 명을 기다립니다.' });
  });
  us.forEach(function (u) {
    var ft = unitFoodTurns(u);
    if (ft <= 3) out.push({ cls: 'warn', ic: '!', t: uName(u) + ' — 군량 ' + days(ft) + '분', s: '', go: ['unit', u.id], lb: '보기', say: uName(u) + '의 군량이 ' + days(ft) + '분뿐입니다.' });
  });
  if (F.ap >= AP.recruit) bs.forEach(function (b) {            // 군사가 '응할 것'이라고 보는 이웃 무장
    var hs = poachHints(b); if (!hs.length) return;
    out.push({ cls: 'cool advh', ic: '招', t: b.n + ' — 등용할 만한 무장 ' + hs.length + '명', s: hs.slice(0, 3).map(function (x) { return x.t.n + ' ' + pcT(x.p); }).join(' · '), go: ['recruit', b.id], lb: '등용', info: 1, say: b.n + '에서 ' + josa(hs[0].t.n, '을를') + ' 부르면 응할 것입니다.' });
  });
  if (!peaceLeft()) bs.forEach(function (b) {                  // 이웃 세력이 데려갈 수 있는 무장(초반 보호 중에는 권하지 않으므로 그 뒤부터)
    var rk = baseOfficers(b).map(function (o) { return { o: o, r: poachRisk(o) }; }).filter(function (x) { return x.r && x.r.p >= POACH_AI.min; }).sort(function (x, y) { return y.r.p - x.r.p; });
    if (rk.length) out.push({ cls: 'warn', ic: '離', t: b.n + ' — 떠날 수 있는 무장 ' + rk.length + '명', s: rk.slice(0, 3).map(function (x) { return x.o.n + ' 충성 ' + x.o.loy + ' (' + (UI.pct ? x.r.p + '%' : '떠날 낌새 ' + oddsWord(x.r.p)) + ')'; }).join(' · '), go: ['base', b.id, 'men'], lb: '포상', info: 1, say: rk[0].o.n + '의 마음이 흔들립니다. 포상으로 붙잡으십시오.' });
  });
  var CS = counsel(f);                                              // 군사의 헌책(v0.11) — 거점 줄과 군사의 한마디가 여기서 나온다
  if (F.ap >= 10) {
    var nb = 0, more = 0, lordLoc = off(F.lord).unit === null ? off(F.lord).loc : -1;
    bs.slice().sort(function (x, y) { return (y.id === lordLoc) - (x.id === lordLoc) || (y.kind === 'city') - (x.kind === 'city') || idleOfficers(y).length - idleOfficers(x).length; }).forEach(function (b) {
      var a = baseAdvice(b, CS); if (!a) return;
      if (nb >= 5) { more++; return; }
      nb++;
      out.push({ ic: String(a.n), num: 1, t: b.n + ' — 쉬는 무장 ' + a.n + '명', s: a.tips.join(' · '), go: ['base', b.id, a.tab], lb: '열기', say: b.n + ' — ' + a.say });
    });
    if (more) out.push({ ic: '+', t: '다른 거점 ' + more + '곳에도 쉬는 무장', s: '', go: ['list', 'city'], lb: '목록' });
  } else out.push({ ic: '…', t: '행동력 부족 (' + F.ap + ') — 다음 턴에', s: '', say: '행동력이 다했습니다. 턴을 넘기시지요.' });
  if (!corpsAll().length && all.length >= 4) out.push({ cls: 'cool', ic: '軍', t: '거점 ' + all.length + '곳 — 군단에 맡길 수 있습니다', s: '방침만 주면 군단장이 다스립니다', go: ['corpsnew'], lb: '군단', info: 1, say: '거점이 늘었습니다. 먼 곳은 군단에 맡기시지요.' });
  var mar = us.filter(function (u) { return u.dest >= 0; });
  if (mar.length) out.push({ cls: 'cool', ic: '▸', t: '행군 중 ' + mar.length + '부대', s: mar.slice(0, 2).map(function (u) { return uName(u) + ' → ' + destName(u.dest); }).join(' · ') + (mar.length > 2 ? ' …' : ''), go: ['unit', mar[0].id], lb: '보기' });
  var need = 0; out.forEach(function (t) { if (t.cls !== 'cool' && !t.info && t.go) need++; });
  out.need = need; out.cs = CS;
  if (!need) out.push({ cls: 'end', ic: '✓', t: '할 일을 모두 마쳤습니다', s: '', go: ['end'], lb: '턴 종료', say: '할 일을 모두 마쳤습니다. 턴을 넘기시지요.' });      // 남은 일이 있을 때는 아래의 턴 종료 단추로 충분하다
  return out;
}
/* 군사의 한마디: '지금 할 일'의 맨 위(가장 급한 것)를 말로 옮긴다 → { say, go } */
function advTop(list) {
  var i;
  for (i = 0; i < list.length; i++) if (list[i].say && list[i].cls && /warn/.test(list[i].cls)) return list[i];      // 급한 알림이 먼저
  var c = counselPick(list.cs); if (c) return c;                                                                  // 평소의 헌책(v0.11)
  for (i = 0; i < list.length; i++) if (list[i].say) return list[i];
  return null;
}
function gotoBase(b, tab) { selectBase(b, true, tab); jumpTo(b.c, b.r, Math.max(cam.z, 0.8)); }
function gotoUnit(u) { selectUnit(u, true); jumpTo(u.c, u.r, Math.max(cam.z, 0.8)); }
function goTodo(g) {
  if (g[0] === 'unit') { var u = UMAP[g[1]]; if (u) gotoUnit(u); }
  else if (g[0] === 'base') gotoBase(G.bases[g[1]], g[2]);
  else if (g[0] === 'list') showLists(g[1]);
  else if (g[0] === 'peace') showPeaceInfo();
  else if (g[0] === 'recruit') { gotoBase(G.bases[g[1]], 'men'); flowRecruit(G.bases[g[1]]); }
  else if (g[0] === 'end') doEndTurn();
  else if (g[0] === 'corpsnew') showCorpsNew();
  else if (g[0] === 'dip') flowDipOffer(g[1], g[2]);
  else if (g[0] === 'duelask') flowDuelAsk(g[1], g[2]);
}
function homeSheet() {
  var st = { todo: [] };
  return {
    home: true, cls: 'home' + (HOME.open ? '' : ' fold'),
    on: {
      fold: function () { HOME.open = !HOME.open; saveOpts(); showHome(); requestDraw(); },
      go: function (el) { var t = st.todo[+el.getAttribute('data-v')]; if (t && t.go) goTodo(t.go); },
      lord: function () { showOfficer(off(G.factions[G.player].lord)); },
      adv: function () { showAdvisor(); },
      advgo: function () { var t = advTop(st.todo); if (t && t.go) goTodo(t.go); },
      advnext: function () { UI.cSkip = (UI.cSkip || 0) + 1; sfx('ui'); refreshSheet(); },
      corps: function (el) { showCorps(+el.getAttribute('data-v')); },
      corpsnew: function () { showCorpsNew(); },
      peace: function () { showPeaceInfo(); }
    },
    render: function () {
      if (!G) return '';
      var f = G.player, F = G.factions[f], L = off(F.lord), T = facTotals(f), i;
      st.todo = todoList();
      var need = st.todo.need;
      var pl = peaceLeft(), A = facAdv(f);
      var pz = pl > 0 ? '<button class="pz' + (pl <= 3 ? ' end' : '') + '" type="button" data-a="peace">' + (pl <= 3 ? '보호 ' + days(pl) + ' 남음' : shortDate(G.peace.until - 1) + '까지 보호') + '</button>' : '';
      var h = '<div class="sh-head hm-head"><button class="porb" type="button" data-a="lord" aria-label="군주 정보">' + porTag(L, 'md') + '</button><div class="hm-id">' +
        '<div class="sh-title">' + F.name + '군' + pz + '</div>' +
        (HOME.open ? '<div class="hm-line"><span class="inc">' + ico('gold') + '+' + fmt(T.gi) + '<i>/월</i></span><span class="inc">' + ico('food') + '+' + fmt(T.fi) + '<i>/분기</i></span>' +
            '</div>'
          : '<div class="sh-sub">' + (need ? '<b class="hi">할 일 ' + need + '건</b>' : '<b class="ok">할 일 없음</b>') + '</div>') + '</div>' +
        '<button class="x fold" data-a="fold" type="button" aria-label="' + (HOME.open ? 'STATUS 창 접기' : 'STATUS 창 펼치기') + '">' + (HOME.open ? '▾' : '▴') + '</button></div>';
      if (!HOME.open) return h;
      var top = advTop(st.todo);
      h += '<div class="sh-body"><div class="hm-advp' + (A ? '' : ' none') + '">' + (A ? '<button class="hm-say" type="button" data-a="advgo"' + (top && top.go ? '' : ' disabled') + '>' + porTag(A, 'md') + '<span class="tx"><i>군사 <b>' + A.n + '</b>' + (top && top.cns && top.n > 1 ? ' <em class="cnt2">' + (top.i + 1) + '/' + top.n + '</em>' : '') + '</i><span>' + (top ? top.say : '…') + '</span></span></button>'
          : '<div class="hm-say"><i class="por md none"></i><span class="tx"><i>군사</i><span class="bad">군사가 없습니다. 임명하면 조언을 듣습니다.</span></span></div>') +
        '<div class="hm-advb">' + (A && top && top.cns && top.n > 1 ? '<button class="btn hm-nx" type="button" data-a="advnext">다른 조언</button>' : '') + '<button class="btn' + (A ? '' : ' pri') + ' hm-adv" type="button" data-a="adv">' + (A ? '바꾸기' : '임명') + '</button></div></div>' +
        corpsStrip() +
        '<div class="sec">지금 할 일' + (need ? ' <em class="cnt">' + need + '</em>' : '') + '</div><div class="todos">';
      for (i = 0; i < st.todo.length; i++) {
        var t = st.todo[i];
        h += '<button class="todo' + (t.cls ? ' ' + t.cls : '') + '" type="button" data-a="go" data-v="' + i + '"' + (t.go ? '' : ' disabled') + '><span class="n' + (t.num ? ' num' : '') + '">' + t.ic + '</span><span class="mid"><b>' + t.t + '</b>' + (t.s ? '<small>' + t.s + '</small>' : '') + '</span>' + (t.go ? '<span class="go">' + t.lb + ' ▸</span>' : '') + '</button>';
      }
      return h + '</div></div>';
    }
  };
}
function hideSheet() { SHEET = null; var el = $('sheet'); el.className = ''; el.innerHTML = ''; }
function showHome() { if (!G || UI.play) { hideSheet(); return; } showSheet(homeSheet()); }

/* ---------- 뒤로 가기 ---------- */
/* 목록·기록·요약에서 줄을 눌러 지도로 건너뛰면 그 창을 '돌아갈 곳'(UI.ret)으로 남긴다.
   - 왼쪽 위 '‹ 목록' 단추를 누르면 그 창이 보던 자리 그대로 다시 열린다.
   - 건너뛰면서 열린 거점·부대 창(UI.via)의 ×도 그 창으로 돌아간다. */
function paintRet() {
  var el = $('ret'); if (!el) return;
  var on = !!(UI.ret && G && !G.over && !UI.play && !MODAL);
  el.className = on ? 'on' : ''; el.textContent = on ? '\u2039 ' + UI.ret.label : '';
}
function clearRet() { UI.ret = null; UI.via = false; paintRet(); }
function goRet() { var r = UI.ret; if (!r) return false; UI.ret = null; clearSel(); r.open(); return true; }
function jumpFromDialog(label, fn) {
  var keep = { d: MODAL, st: dlgScroll() };
  closeDialog();
  UI.ret = { label: label, open: function () { showDialog(keep.d); var b = $('modal').querySelector('.dlg-b'); if (b) b.scrollTop = keep.st; } };
  fn(); UI.via = !!UI.sel; paintRet();
}
/* 아래 창의 ×: 한 단계만 뒤로 */
function backSheet() {
  if (selUnit() && (UI.target || UI.march || UI.pickMarch)) {        // 대상·행군을 고르던 중이면 그것만 물린다
    UI.target = null; UI.march = null; UI.pickMarch = false; refreshSheet(); requestDraw(); return;
  }
  if (UI.sret) { var r = UI.sret; UI.sret = null; r(); return; }     // 잠깐 다른 것을 보러 갔던 경우(거점 보기·출진 직후) → 보던 곳으로
  if (UI.via && UI.ret) { goRet(); return; }                         // 목록에서 건너온 경우 → 목록으로
  clearSel();
}

/* ---------- 선택 ---------- */
function selUnit() {
  if (!G || !UI.sel || UI.sel.kind !== 'unit') return null;
  var u = UMAP[UI.sel.id];
  return (u && u.f === G.player && !u.done) ? u : null;
}
function clearSel() { UI.sel = null; UI.rc = null; UI.atk = null; UI.target = null; UI.march = null; UI.pickMarch = false; UI.via = false; UI.sret = null; UI.mfrom = -1; UI.mpath = null; closeSheet(); requestDraw(); }
function selectBase(b, noCam, tab) {
  UI.sel = { kind: 'base', id: b.id }; UI.rc = null; UI.atk = null; UI.target = null; UI.march = null; UI.via = false; UI.sret = null; UI.mfrom = -1; UI.mpath = null;
  showSheet(baseSheet(b, tab)); if (!noCam) ensureVisible(b.c, b.r); requestDraw();
}
function selectUnit(u, noCam) {
  UI.sel = { kind: 'unit', id: u.id }; UI.target = null; UI.march = null; UI.pickMarch = false; UI.via = false; UI.sret = null; UI.mfrom = -1; mpathOf(u);
  if (u.f === G.player && !u.done && !unitCorps(u)) { UI.rc = unitReach(u); UI.atk = allTargets(u); } else { UI.rc = null; UI.atk = null; }
  showSheet(unitSheet(u)); if (!noCam) ensureVisible(u.c, u.r); requestDraw();
}
/* 공격·계략이 닿는 대상 전부 */
function allTargets(u) {
  var out = attackTargets(u), seen = {};
  out.forEach(function (t) { seen[K(t.c, t.r)] = 1; });
  for (var i = 0; i < 3; i++) ployTargets(u, PLOYS[i]).forEach(function (t) { var k = K(t.c, t.r); if (!seen[k]) { seen[k] = 1; out.push(t.u ? { kind: 'unit', u: t.u, c: t.c, r: t.r } : { kind: 'fac', b: plotAt(t.c, t.r).base, i: plotAt(t.c, t.r).i, c: t.c, r: t.r }); } });
  return out;
}
function onTap(c, r) {
  if (UI.play) { playNudge(); return; }
  if (UI.busy || !G || G.over) return;
  if (MODAL) { if (MODAL.dev) devTap(c, r); else if (MODAL.fsel) fselTap(c, r); else if (MODAL.pick) MODAL.pick.tap(c, r); return; }
  var k = K(c, r), u = UAT[k] || null, b = baseAt(c, r), pl = plotAt(c, r), su = selUnit();
  if (su && unitCorps(su)) su = null;                                  // 군단의 부대를 보고 있을 때: 다른 곳을 누르면 그것을 고를 뿐이다
  if (su) {
    if (u === su) return;
    var t = null;
    if (u && u.f !== G.player) t = { kind: 'unit', u: u, c: c, r: r };
    else if (b && b.owner >= 0 && b.owner !== G.player) t = { kind: 'base', b: b, c: c, r: r };
    else if (pl && pl.plot.fac && pl.base.owner >= 0 && pl.base.owner !== G.player) t = { kind: 'fac', b: pl.base, i: pl.i, c: c, r: r };
    if (t) {
      var acts = targetActions(su, t), any = acts.some(function (a) { return a.ok; });
      if (!any) {
        if (t.kind === 'fac' && UI.rc && UI.rc.stop[k]) { UI.march = null; doMove(su, c, r); return; }
        if ((t.kind === 'base' || t.kind === 'fac') && justOut(su) && hdist(su.c, su.r, c, r) <= (t.kind === 'fac' ? 1 : uRange(su))) toast('출진한 턴에는 거점을 칠 수 없습니다', 2400);
        else if (t.kind === 'fac') { if (MC[clsIdx(su)][k] < 99 && !u) orderMarch(su, c, r); else toast('닿지 않습니다'); }      // 먼 시설: 그 칸으로 행군
        else orderAim(su, t);                                          // v0.18: 닿지 않는 적(부대 · 거점) → 공격 명령(다가가서 알아서 친다)
        return;
      }
      UI.target = t; UI.march = null; refreshSheet(); requestDraw(); return;
    }
    if (UI.rc && UI.rc.stop[k]) { UI.march = null; doMove(su, c, r); return; }
    if (!u && !b && !(pl && pl.base.owner === G.player) && MC[clsIdx(su)][k] < 99) { orderMarch(su, c, r); return; }      // v0.18: 파란 칸 밖의 땅 → 곧바로 그곳으로 행군([이동 취소]로 물린다)
  }
  UI.target = null;
  if (u) { selectUnit(u); return; }
  if (b) {
    var mf = (su && (b.owner === G.player || b.owner < 0)) ? su.id : -1;      // v0.18: 부대를 고른 채 누른 내 성 · 빈 성 — 창을 열되, 그 부대를 이 성으로 보내는 단추를 낸다
    selectBase(b);
    if (mf >= 0) { UI.mfrom = mf; UI.sret = function () { var u2 = UMAP[mf]; if (u2 && u2.f === G.player && !u2.done) selectUnit(u2); else clearSel(); }; refreshSheet(); }
    return;
  }
  if (pl && pl.base.owner === G.player && baseCorps(pl.base)) { selectBase(pl.base); return; }      // 군단에 맡긴 거점의 부지: 거점 창만 연다
  if (pl && pl.base.owner === G.player) {                              // 내 부지: 고른 것은 그대로 두고 창만 띄운다 — 창을 닫으면 보던 곳 그대로다
    if (su) { refreshSheet(); requestDraw(); }
    if (pl.plot.fac) flowFacility(pl.base, pl.i); else flowDevelop(pl.base, pl.i);
    return;
  }
  if (su || UI.sel) { clearSel(); return; }
  var tt = terr(c, r);
  toast(TERRAIN_NAME[tt] + (isRoad(c, r) && tt !== 'w' ? ' (길)' : (isRoad(c, r) ? ' (나루)' : '')) + (tt === 'm' || tt === 's' || tt === 'x' ? '' : ' · 높이 ' + elevOf(c, r)) + ' — ' + TERRAIN_DESC[tt], 2600);
}

/* ---------- 행군(여러 턴 걸리는 이동) · 공격 명령(v0.18) ----------
   UI.mNew = 이번 턴에 내린 명령 { id, turn, from(그때 서 있던 칸), prev(그 전의 목적지), aim0(그 전의 공격 명령) } — [이동 취소]가 그 첫걸음을 물리면 명령도 되돌린다
   UI.mpath = 고른 부대의 갈 길 { id, path } (지도에 그린다)   UI.mfrom = 성의 창에 [이 성으로 행군] 단추를 낼 부대 */
function mpathOf(u) { UI.mpath = (u && u.f === G.player && UMAP[u.id] && u.dest >= 0) ? { id: u.id, path: marchPath(u, u.dest) } : null; if (UI.mpath && !UI.mpath.path) UI.mpath = null; }
function noteOrder(u) { UI.mNew = { id: u.id, turn: G.turn, from: K(u.c, u.r), prev: u.dest >= 0 ? u.dest : -1, aim0: u.aim ? { k: u.aim.k, id: u.aim.id, n: u.aim.n } : null }; }
/* v0.18.1: 거점에 들어갔을 때의 한마디 — 돌아가기로 한 수송대면 무장이 어디로 며칠 걸려 돌아가는지 */
function backSay(res) { return res && res.back ? ' · 무장은 ' + euro(G.bases[res.back.to].n) + ' 돌아갑니다(' + days(res.back.turns) + ')' : ''; }
function enterToast(res) { var bn = G.bases[res.entered].n; if (res.back) toast(bn + ' — 수송 완료' + backSay(res), 3400); else toast(bn + (res.ask ? ' — 수송 완료' : ' 입성')); if (res.ask) setTimeout(function () { askNext(); }, 60); }
/* v0.21 수송을 마친 호송 무장: 머물지 · 돌아갈지(G.tdone 의 맨 앞부터). 닫을 수 없는 창 — 둘 가운데 하나를 고른다. then = 다 물은 뒤에 할 일 */
function askNext(then) {
  var v = null;
  while (G && G.tdone && G.tdone.length && !(v = transAskInfo(G.tdone[0]))) G.tdone.shift();
  if (!v || G.over) { if (then) then(); return; }
  if (MODAL) { setTimeout(function () { askNext(then); }, 500); return; }
  var L = v.os[0], who = L.n + (v.os.length > 1 ? ' 외 ' + (v.os.length - 1) + '명' : '');
  function fin() { closeDialog(); refreshSheet(); refreshHud(); requestDraw(); askNext(then); }
  showDialog({
    lock: true, ask: 'trans',
    render: function () {
      return '<div class="dlg-h"><h2>수송 완료 — ' + v.b.n + '</h2></div><div class="dlg-b"><div class="card supc">' + porTag(L, 'md') + '<p><b>' + who + '</b><br><small>실어 온 것을 ' + v.b.n + '에 모두 들였습니다. 이제 어떻게 할까요?</small></p></div></div>' +
        '<div class="dlg-f two"><button class="btn" type="button" data-a="tstay"><b>' + v.b.n + '에 머문다</b></button><button class="btn" type="button" data-a="tgo"><b>' + euro(v.home.n) + ' 돌아간다</b> <small>' + days(v.turns) + '</small></button></div>';
    },
    on: {
      tstay: function () { cmdTransAsk(false); toast(josa(L.n, '은는') + ' ' + v.b.n + '에 머뭅니다', 2200); fin(); },
      tgo: function () { var r = cmdTransAsk(true); if (r.ok && r.back) toast(josa(L.n, '은는') + ' ' + euro(v.home.n) + ' 돌아갑니다 — ' + days(r.back.turns), 2800); fin(); }
    }
  });
}
/* 부대에 보급을 마친 수송대: 남을지 · 떠나온 거점으로 돌아갈지 */
function askSupplyDone(t) {
  var hb = transHomeOf(t);
  if (!t || !alive(t) || !hb || t.f !== G.player || t.corps || t.back) return;
  var L = uLeader(t), path = marchPath(t, K(hb.c, hb.r)); if (!path) return;
  showDialog({
    lock: true, ask: 'supply',
    render: function () {
      return '<div class="dlg-h"><h2>보급 완료</h2></div><div class="dlg-b"><div class="card supc">' + porTag(L, 'md') + '<p><b>' + uName(t) + '</b><br><small>남은 짐 — 병량 ' + fmt(t.food) + ' · 병력 ' + fmt(t.troops) + '명. 이제 어떻게 할까요?</small></p></div></div>' +
        '<div class="dlg-f two"><button class="btn" type="button" data-a="tstay"><b>이곳에 남는다</b></button><button class="btn" type="button" data-a="tgo"><b>' + euro(hb.n) + ' 돌아간다</b> <small>' + days(marchTurns(t, path)) + '</small></button></div>';
    },
    on: {
      tstay: function () { closeDialog(); refreshSheet(); },
      tgo: function () { closeDialog(); if (alive(t)) { if (t.aim) delete t.aim; t.dest = K(hb.c, hb.r); toast(uName(t) + ' — 다음 턴부터 ' + euro(hb.n) + ' 돌아갑니다', 2800); } refreshSheet(); requestDraw(); }
    }
  });
}
function transHomeOf(x) { var hb = x && x.type === 'trans' ? G.bases[x.home] : null; return hb && hb.owner === x.f ? hb : null; }
function tbackBtn(x) { var hb = transHomeOf(x), on = !!(x.back && hb); return '<button class="act tbk' + (on ? ' on' : '') + '" type="button" data-a="tback"><b>짐 내린 뒤</b><small>' + (on ? euro(hb.n) + ' 돌아옴' : '그곳에 머묾') + '</small></button>'; }
function gohomeBtn(x) { var hb = transHomeOf(x); return hb && x.dest !== K(hb.c, hb.r) && hdist(x.c, x.r, hb.c, hb.r) > 1 ? '<button class="act" type="button" data-a="gohome"><b>귀환</b><small>' + euro(hb.n) + ' 행군</small></button>' : ''; }
function marchDone(x, res, say) {                            // 행군의 한 구간이 끝난 뒤(명령을 내린 직후)
  if (res && res.ok && res.entered !== undefined) { enterToast(res); selectBase(G.bases[res.entered]); }
  else if (res && res.ok && res.captured !== undefined) { sfx('fall'); sfx('cheerlate'); fxFall(G.bases[res.captured], '점령'); toast(G.bases[res.captured].n + ' 점령!'); selectBase(G.bases[res.captured]); }
  else if (alive(x)) {
    if (res && res.front !== undefined && !x.aim) toast(G.bases[res.front].n + ' 앞 — 성을 눌러 공격', 3200);
    else if (res && res.lost) toast('그곳으로 가는 길이 없습니다');
    else toast(say || (x.dest >= 0 ? '행군 시작' : '도착'), 3000);
    UI.rc = unitReach(x); UI.atk = allTargets(x); mpathOf(x); refreshSheet();
  } else clearSel();
  afterAction();
}
/* 파란 칸 밖의 땅(또는 성)으로: 곧바로 행군을 시작한다 */
function orderMarch(u, c, r) {
  var k = K(c, r), path = marchPath(u, k);
  if (!path) { toast('그곳으로 가는 길이 없습니다'); return false; }
  var b = baseAt(c, r), nm = b ? b.n : TERRAIN_NAME[terr(c, r)], turns = marchTurns(u, path), food = unitFoodTurns(u);
  noteOrder(u);
  if (u.aim) delete u.aim;                                    // 새 행군은 공격 명령을 지운다
  u.dest = k; UI.target = null; UI.march = null; UI.pickMarch = false; sfx('drum');
  var say = nm + ' 방면 행군 — 약 ' + days(turns) + (turns > food ? ' · 군량이 모자랍니다(' + days(food) + '분)' : '') + ' · 잘못 눌렀으면 이동 취소';
  marchStep(u, true, function (res) { marchDone(u, res, say); });
  return true;
}
/* 닿지 않는 적(부대 · 거점)으로: 공격 명령 — 지금 다가가고, 턴을 마칠 때마다 알아서 다가가 닿으면 친다 */
function orderAim(u, t) {
  noteOrder(u);
  var r = aimSet(u, t);
  if (!r.ok) { UI.mNew = null; toast(r.msg, 2600); return false; }
  var nm = aimName(u), of = t.kind === 'base' ? t.b.owner : t.u.f;
  UI.target = null; UI.march = null; UI.pickMarch = false; sfx('drum');
  var say = nm + ' 공격 명령 — 다가가서 알아서 칩니다' + (t.kind === 'base' && peaceWouldBreak(of) ? ' · 치면 ' + facName(of) + '군과의 보호가 풀립니다' : '') + ' · 잘못 눌렀으면 이동 취소';
  if (R3 && R3.ready && !R3.units[u.id]) syncScene();
  var vis = unitVis(u), name = uName(u), res = aimApproach(u);
  if (!res) { marchDone(u, null, say); return true; }
  UI.hide = alive(u) ? u.id : -1; UI.rc = null; UI.atk = null;
  animMove(vis, res.from, res.path, function () { marchLog(u, name, res); marchDone(u, res, say); });
  return true;
}
function destName(k) { var c = k % W, r = (k - c) / W, b = baseAt(c, r); return b ? b.n : TERRAIN_NAME[terr(c, r)]; }
function marchStep(u, animate, cb) {
  if (animate && R3 && R3.ready && !R3.units[u.id]) syncScene();          // 막 출진한 부대는 먼저 지도에 세운다
  var vis = unitVis(u), name = uName(u), res = unitMarch(u);
  if (!res || !res.ok) { if (cb) cb(res); return; }
  function fin() { marchLog(u, name, res); if (cb) cb(res); }
  if (animate) { UI.hide = alive(u) ? u.id : -1; UI.rc = null; UI.atk = null; animMove(vis, res.from, res.path, fin); } else fin();
}

/* ---------- 부대 조작 ---------- */
function doMove(u, c, r) {
  var vis = unitVis(u), rc = UI.rc;
  var res = unitMove(u, c, r, rc);
  if (!res.ok) { toast(res.msg); return; }
  UI.hide = alive(u) ? u.id : -1; UI.rc = null; UI.atk = null; UI.target = null;
  animMove(vis, res.from, res.path, function () {
    if (res.entered !== undefined) { enterToast(res); selectBase(G.bases[res.entered]); }
    else if (res.captured !== undefined) { sfx('fall'); sfx('cheerlate'); fxFall(G.bases[res.captured], '점령'); toast(G.bases[res.captured].n + ' 점령!'); selectBase(G.bases[res.captured]); }
    else if (res.dead) { toast('불길 속에서 부대가 흩어졌습니다'); clearSel(); }
    else {
      if (res.burn) { floatText(c, r, '-' + fmt(res.burn), '#b5332a'); sfx('fire'); }
      UI.rc = unitReach(u); UI.atk = allTargets(u); refreshSheet();
    }
    afterAction();
  });
}
function estBase(u, b) {
  var T = UNIT_TYPES[u.type];
  return { t: Math.min(b.troops, Math.round(620 * Math.pow(uAtk(u) / baseDefVal(b), 0.9) * troopFactor(u.troops) * T.vsBase)), d: durDmgUB(u) };
}
/* ---------- 지형 풀이(v0.15) ---------- */
function pctTxt(m) { var p = Math.round((m - 1) * 100); return (p > 0 ? '+' : '−') + Math.abs(p) + '%'; }
var TERRAIN_SHORT = { p: '', f: '받는 피해 −15%', h: '받는 피해 −15%', d: '', w: '공격 −30% · 받는 피해 +20%' };
/* 부대가 선 칸: 지형 · 높이 · 그 칸의 효과 */
function terrLine(u) {
  var t = terr(u.c, u.r), cav = UNIT_TYPES[u.type].cls === 'horse', tx = TERRAIN_SHORT[t] || '';
  if (cav && (t === 'f' || t === 'h')) tx += (tx ? ' · ' : '') + '기병 공격 −15%'; else if (cav && t === 'p') tx = '기병 · 평지의 적에게 +10%';
  return '<div class="terrl"><i class="tmk">地</i><b>' + (isRoad(u.c, u.r) && t !== 'w' ? TERRAIN_NAME[t] + '(길)' : TERRAIN_NAME[t]) + '</b> · 높이 <b>' + elevOf(u.c, u.r) + '</b>' + (tx ? '<span>' + tx + '</span>' : '') + '</div>';
}
/* 이 싸움에 걸리는 지형의 값: a 가 d 를 칠 때(둘 다 부대) */
function terrNote(a, d) {
  var far = hdist(a.c, a.r, d.c, d.r) > 1, ms = terrMods(a, d, far), cs = far ? [] : terrMods(d, a, false), x = 1, y = 1, i;
  if (!ms.length && !cs.length) return '';
  for (i = 0; i < ms.length; i++) x *= ms[i].m;
  for (i = 0; i < cs.length; i++) y *= cs[i].m;
  var h = '<p class="note tnote"><b>지형</b> ';
  if (ms.length) h += ms.map(function (m) { return m.k + ' <em class="' + (m.m >= 1 ? 'good' : 'bad') + '">' + pctTxt(m.m) + '</em>'; }).join(' · ') + (ms.length > 1 ? ' → 내 피해 <em class="' + (x >= 1 ? 'good' : 'bad') + '">' + pctTxt(x) + '</em>' : '');
  else h += '내 피해는 그대로';
  if (cs.length) h += '<br>반격 ' + cs.map(function (m) { return m.k + ' <em class="' + (m.m <= 1 ? 'good' : 'bad') + '">' + pctTxt(m.m) + '</em>'; }).join(' · ') + (cs.length > 1 ? ' → <em class="' + (y <= 1 ? 'good' : 'bad') + '">' + pctTxt(y) + '</em>' : '');
  return h + '</p>';
}
function targetActions(u, t) {
  var out = [], d = hdist(u.c, u.r, t.c, t.r), rg = uRange(u), i;
  var tf0 = t.kind === 'unit' ? t.u.f : (t.b ? t.b.owner : -1), pk = tf0 >= 0 ? pactOf(u.f, tf0) : null;
  if (pk) return [{ kind: 'attack', label: PACT_NAME[pk.t] + ' 중', sub: days(pk.until - G.turn) + ' 남음 · 칠 수 없습니다', ok: false, pri: true }];      // v0.14: 협정을 맺은 세력
  if (t.kind === 'unit') {
    out.push({ kind: 'attack', label: '공격', sub: d <= rg ? '예상 ' + dmgEst(u, t.u, attackExpect(u, t.u).dealt) : '사거리 밖', ok: d <= rg, pri: true });
    var all = TACTICS[u.type] || [], can = tacticList(u);
    for (i = 0; i < all.length; i++) {
      var tac = all[i], have = can.indexOf(tac) >= 0, inT = have && tacticTargets(u, tac).some(function (x) { return x.u === t.u; });
      var od = tacticOdds(u, t.u);
      var sub = !have ? '적성 ' + tac.need + ' 필요' : (u.morale < tac.cost ? '기력 부족' : (!inT ? (d > rg ? '사거리 밖' : '숲에서는 불가') : '<em class="pc">' + pcG(od.ok) + '</em> · 기력 ' + tac.cost));
      var tg = tac.tag || ''; if (tac.pull && inT && !pullRoom(u, t.u)) tg = '뒤가 막혀 끌지 못함 · 반격 없음';
      out.push({ kind: 'tactic', tac: tac, label: tac.name, han: tac.han, fx: tg, sub: sub, ok: inT });
    }
    if (d <= rg) {                                               // v0.20 참모(부장)의 추천: 공격 명령이 고르는 수(bestStrike)를 짚되, 헤아림(통솔 · 지력)이 모자라면 가끔 다른 수를 권한다
      var bs0 = bestStrike(u, t.u), recA = bs0.tac ? out.filter(function (a0) { return a0.tac === bs0.tac; })[0] : out[0];
      if (recA && bs0.v > 0) {
        if (omenRoll('rec|' + u.id + '|' + t.u.id) >= staffRead(uStaff(u))) {
          var alts = out.filter(function (a0) { return a0.ok && a0 !== recA && (a0.kind === 'attack' || a0.kind === 'tactic'); });
          if (alts.length) recA = alts[Math.floor(omenRoll('rec2|' + u.id + '|' + t.u.id) / 100 * alts.length) % alts.length];
        }
        recA.rec = true;
      }
    }
    var chOk = challengeTargets(u).some(function (x) { return x.u === t.u; }), chW = uLeader(u).war + ' : ' + uLeader(t.u).war;      // 일기토 신청(v0.13)
    out.push({ kind: 'challenge', label: '일기토', sub: !chOk ? (d > 1 ? '옆 칸에서만' : '응할 수 없는 상대') : (u.morale < DUEL_K.ask ? '기력 부족' : '응할 확률 <em class="pc">' + pcT(challengeChance(u, t.u)) + '</em> · 무력 ' + chW), ok: chOk && u.morale >= DUEL_K.ask });
    for (i = 0; i < 3; i++) {
      var pl = PLOYS[i], inP = ployTargets(u, pl).some(function (x) { return x.u === t.u; });
      out.push({ kind: 'ploy', ploy: pl, label: pl.name, adv: inP ? ployAdvice(u, pl, t) : null, sub: inP ? '<em class="pc">' + pcG(ployChance(u, pl, t.u)) + '</em>' + advMark(ployAdvice(u, pl, t)) + ' · 기력 ' + pl.cost : (u.morale < pl.cost ? '기력 부족' : (t.u.status && i > 0 ? '이미 걸림' : '사거리 밖')), ok: inP });
    }
  } else if (t.kind === 'base') {
    var e = estBase(u, t.b), fresh = justOut(u);
    out.push({ kind: 'attack', label: '공격', sub: fresh ? '다음 턴부터' : (d <= rg ? '병력 -' + fmt(e.t) + ' · 내구 -' + fmt(e.d) : '사거리 밖'), ok: d <= rg && !fresh, pri: true });
  } else {
    out.push({ kind: 'attack', label: '시설 파괴', sub: justOut(u) ? '다음 턴부터' : (d <= 1 ? '' : '옆 칸에서만'), ok: d <= 1 && !justOut(u), pri: true });
    var inF = ployTargets(u, PLOYS[0]).some(function (x) { return x.c === t.c && x.r === t.r; });
    out.push({ kind: 'ploy', ploy: PLOYS[0], label: '화계', adv: inF ? ployAdvice(u, PLOYS[0], t) : null, sub: inF ? '기력 10' + advMark(ployAdvice(u, PLOYS[0], t)) : '불가', ok: inF });
  }
  return out;
}
/* v0.18: 전법 이름에 한자를 곁들인다 */
function tacHan(tac) { return tac && tac.han ? ' <i class="hj">' + tac.han + '</i>' : ''; }
function tacNameH(tac) { return tac.name + tacHan(tac); }
/* 전법 풀이: 고른 상대에 대한 성공·대성공 확률과, 결과에 따라 달라지는 효과 */
function showTacticInfo(u, d) {
  showDialog({
    render: function () {
      var all = TACTICS[u.type] || [], can = tacticList(u), od = tacticOdds(u, d), P = od.parts, i, tac, N = attackExpect(u, d), rows = '';
      function vs(a, b, moreIsGood) { if (b < 1) return ''; var q = Math.round((a / b - 1) * 100); return q ? ' <em class="' + ((q > 0) === moreIsGood ? 'good' : 'bad') + '">' + (q > 0 ? '+' : '−') + Math.abs(q) + '%</em>' : ''; }      // 보통 공격과 견준 %: 피해는 많을수록, 반격은 적을수록 좋다
      function sg(v) { return UI.pct ? (v > 0 ? '+' : '') + v : (v > 0 ? (v >= 8 ? '▲▲' : '▲') : (v < 0 ? (v <= -8 ? '▼▼' : '▼') : '–')); }      // v0.18: 말로 볼 때는 보탬·깎임을 화살표로
      var h = dlgHead('전법 풀이') + '<div class="dlg-b"><div class="tacs">' +
        '<p class="who"><b>' + uName(u) + '</b> → <b>' + uName(d) + '</b></p>' +
        (UI.pct ? '<div class="odds"><span class="g"><i>대성공</i><b>' + od.crit + '%</b></span><span><i>성공</i><b>' + (od.ok - od.crit) + '%</b></span><span class="f"><i>실패</i><b>' + (100 - od.ok) + '%</b></span></div>'
          : '<div class="odds w"><span><i>통할 가능성</i><b>' + pcG(od.ok) + '</b></span><span class="g"><i>대성공</i><b>' + (od.sure ? '통하면 반드시' : pcT(od.crit)) + '</b></span></div>' + eyeNote());
      // 보통 공격과 나란히: 쓸 수 있는 전법마다 기대 피해 · 받는 반격
      for (i = 0; i < all.length; i++) {
        tac = all[i];
        if (can.indexOf(tac) < 0 || u.morale < tac.cost || !tacticTargets(u, tac).some(function (x) { return x.u === d; })) continue;
        var X = tacticExpect(u, d, tac);
        rows += '<tr data-t="' + tac.name + '"><th>' + tac.name + (X.others ? ' <small>+' + X.others + '부대</small>' : '') + '</th><td><b>' + fmt(Math.round(X.dealt)) + '</b>' + vs(X.dealt, N.dealt, true) + '</td><td><b>' + fmt(Math.round(X.recv)) + '</b>' + vs(X.recv, N.recv, false) + '</td></tr>';
      }
      h += '<table class="tcmp"><tr><th></th><th>피해</th><th>받는 반격</th></tr><tr class="nrm"><th>보통 공격</th><td><b>' + fmt(Math.round(N.dealt)) + '</b></td><td><b>' + fmt(Math.round(N.recv)) + '</b></td></tr>' + rows + '</table>' +
        (rows ? '<p class="cap">전법은 성공·실패를 확률대로 섞은 값 · 대성공이면 피해 ×' + od.mult + '</p>' : '');
      for (i = 0; i < all.length; i++) {
        tac = all[i];
        var have = can.indexOf(tac) >= 0, c0 = confuseOdds(tac, d), c1 = confuseOdds(tacticEff(tac, true), d);
        h += '<div class="tac' + (have ? '' : ' off') + '" data-t="' + tac.id + '"><div class="tn"><b>' + tacNameH(tac) + '</b><span>기력 ' + tac.cost + ' · 피해 ×' + tac.mult + (have ? '' : ' · 적성 ' + tac.need + ' 필요') + '</span></div>' +
          '<div class="tl"><i>성공</i><span>' + tac.fx + (c0 ? ' — <b>' + pcT(c0) + '</b>' : '') + '</span></div>' +
          '<div class="tl g"><i>대성공</i><span>' + tac.gfx + (c1 && c1 < 100 ? ' — <b>' + pcT(c1) + '</b>' : '') + '</span></div></div>';
      }
      h += '<details class="more"><summary>셈법</summary>' +
        '<p class="sum"><b>' + uName(u) + '</b> ' + UNIT_TYPES[u.type].name + ' 적성 ' + uApt(u) + ' · 무력 ' + uWar(u) + ' · 통솔 ' + uLeader(u).ldr + ' · ' + fmt(u.troops) + '명<br><b>' + uName(d) + '</b> ' + UNIT_TYPES[d.type].name + ' 적성 ' + uApt(d) + ' · 통솔 ' + uLdr(d) + ' · 지력 ' + uInt(d) + ' · ' + fmt(d.troops) + '명</p>' +
        '<p class="sum">' + (UI.pct ? '성공률 ' + od.ok + '% = 적성 ' + P.apt : '통할 가능성 ' + pcT(od.ok) + ' ← 적성 ' + uApt(u)) + ' · 무장 ' + sg(P.stat) + ' · 병력 ' + sg(P.troops) + ' · 상대 적성 ' + sg(P.dapt) + (P.terr ? ' · 지형 ' + sg(P.terr) : '') + (P.conf ? ' · 혼란 ' + sg(P.conf) : '') + (P.skill ? ' · 특기 ' + sg(P.skill) : '') + '</p>' +
        '<ul class="rules"><li>성공해도 반격은 통상 공격만큼 받습니다. 견인·관진, 멀리서 쏜 전법, 밀려나 떨어진 적은 반격하지 못합니다.</li>' +
        '<li>실패하면 피해가 통상 공격의 ' + Math.round(TACTIC_K.failDmg * 100) + '%, 반격은 ' + (TACTIC_K.failCounter / 0.55).toFixed(2).replace(/0$/, '') + '배. 기력은 그대로 씁니다.</li>' +
        '<li>무장 = (내 부대 최고 무력×0.6 + 주장 통솔×0.4 − 상대 부대 최고 통솔) × ' + TACTIC_K.stat + ' (' + TACTIC_K.statLo + ' ~ +' + TACTIC_K.statHi + ')</li>' +
        '<li>병력 = 내 병력이 상대의 절반이면 −8, 두 배면 +8. 피해에도 병력 차가 들어갑니다(지금 ×' + tacticSizeK(u, d).toFixed(2) + ').</li>' +
        '<li>창장·극장·궁장·기장 같은 특기가 맞으면 성공한 전법은 모두 대성공입니다. 비장·용장·신장은 무력이 낮은 적을 칠 때 그렇습니다.</li></ul></details>';
      return h + '</div></div>';
    }, on: {}
  });
}
/* 행동 결과를 한 줄로 */
function resultMsg(name, res) {
  if (res.kind === 'challenge') return name + ' 일기토 신청 → ' + res.tname + (res.accepted ? (res.duel ? ' — ' + (res.duel.draw ? '비김' : (res.duel.win ? res.duel.a : res.duel.d) + ' 승' + (res.duel.ko ? '(쓰러뜨림)' : '')) : ' — 응함') : ' — 받지 않음 (기력 -' + res.mor + ')');      // v0.16: AI 도 건다
  var msg = name + ' ';
  if (res.kind === 'ploy') {
    if (res.success) msg += res.ploy + ' 성공' + (res.dmg ? ' (-' + fmt(res.dmg) + ')' : '') + (res.st ? ' — ' + statusName(res.st) + ' ' + days(res.stN) : '') + (res.chain ? ' · 연환!' : '');
    else msg += res.ploy + ' 실패 (' + pcWas(res.p, '성공률') + ')' + (res.reflected ? ' — 반계에 당했습니다!' + (res.selfSt ? ' 우리 부대가 ' + statusName(res.selfSt) + ' ' + days(res.selfStN) : '') : '');
  } else {
    if (res.kind === 'tactic') msg += res.tac + (res.fail ? ' 실패' : (res.crit ? ' 대성공' : ' 성공')); else msg += '공격';
    msg += ' → ' + res.tname + ' -' + fmt(res.dmg);
    if (res.fail && res.pOk !== undefined) msg += ' (' + pcWas(res.pOk, '성공률') + ')';
    if (res.dur) msg += ' · 내구 -' + fmt(res.dur);
    if (res.dmg2) msg += ' · 연전 -' + fmt(res.dmg2);
    if (res.pushed >= 2) msg += ' · 두 칸 밀어냄'; else if (res.pushed === 1) msg += ' · 밀어냄';
    if (res.pulled) msg += ' · 끌어당김'; else if (res.noPull) msg += ' · 뒤가 막혀 끌지 못함';
    if (res.slam) msg += ' · 뒤가 막혀 추가 피해';
    if (res.mor) msg += ' · 기력 -' + res.mor;
    if (res.confused) msg += ' · 혼란 ' + days(res.stN || 1);
  }
  if (res.counter) msg += ' (반격 -' + fmt(res.counter) + ')';
  if (res.duel) msg += duelTxt(res.duel);
  if (res.killed) msg += ' · 궤멸!';
  if (res.destroyed) msg += ' · 파괴!';
  if (res.selfDead) msg += ' · 아군 부대 궤멸…';
  if (res.fell) msg = res.tname + ' 함락!';
  return msg;
}
/* 타격 순간에 띄우는 숫자·글씨와 소리. 피해는 인주색, 전법 이름은 먹, 계략은 쪽빛 */
function resultFx(res) {
  var C_DMG = '#b5332a', C_INK = '#1b1a18', C_PLOY = '#2f4f6f', C_DIM = '#6a645a', C_CNT = '#8a5a12';
  var tc = res.tc1 !== undefined ? res.tc1 : (res.tc !== undefined ? res.tc : res.c), tr = res.tr1 !== undefined ? res.tr1 : (res.tr !== undefined ? res.tr : res.r);
  var ac = res.ac1 !== undefined ? res.ac1 : res.ac, ar = res.ar1 !== undefined ? res.ar1 : res.ar;
  if (res.kind === 'ploy') {
    if (res.success) {
      floatText(res.c, res.r, res.ploy + '!', res.ploy === '화계' ? '#c8551f' : C_PLOY, 0, true, -34);
      if (res.dmg) floatText(res.c, res.r, '-' + fmt(res.dmg), C_DMG, 260);
      if (res.st) floatText(res.c, res.r, statusName(res.st) + ' ' + days(res.stN), C_PLOY, 420, false, 26);      // 걸린 상태와 턴 수
      sfx(res.ploy === '화계' ? 'fire' : (res.ploy === '소화' ? 'douse' : 'wind'));
    } else {
      floatText(res.c, res.r, '실패', C_DIM); sfx('miss');
      if (res.reflected) { floatText(res.ac, res.ar, '반계!', C_PLOY, 300, true); if (res.selfSt) floatText(res.ac, res.ar, statusName(res.selfSt) + ' ' + days(res.selfStN), C_PLOY, 640, false, 26); }
    }
  } else {
    // 글씨가 한자리에 겹치지 않게: 전법 이름은 위, 피해는 가운데, 덧붙는 것은 아래로 차례차례
    var tcH = res.kind === 'tactic' ? TACTIC_BY_ID[tacIdOf(res)] : null, tcN = tcH && tcH.han ? tcH.han + ' ' + tcH.name : res.tac;      // v0.18: 한자 이름을 앞세운다(옛 기록은 그때의 이름 그대로)
    if (res.kind === 'tactic') floatText(res.c, res.r, res.fail ? res.tac + ' 실패' : tcN + (res.crit ? ' 대성공!' : '!'), res.fail ? C_DIM : (res.crit ? C_DMG : C_INK), 0, true, -34);
    else if (res.crit) floatText(res.c, res.r, '크리티컬!', C_INK, 0, true, -34);
    floatText(tc, tr, '-' + fmt(res.dmg), C_DMG, res.kind === 'tactic' || res.crit ? 200 : 0, res.crit || (res.kind === 'tactic' && !res.fail));
    if (res.dur) floatText(tc, tr, '내구 -' + fmt(res.dur), C_CNT, 380, false, 26);
    if (res.dmg2) floatText(tc, tr, '연전 -' + fmt(res.dmg2), C_DMG, 620, false, 26);
    if (res.extra) res.extra.forEach(function (x, i) { floatText(x.c, x.r, '-' + fmt(x.dmg), C_DMG, 300 + i * 80); if (x.mor) floatText(x.c, x.r, '기력 -' + x.mor, C_PLOY, 560 + i * 80, false, 26); });
    // 전법에 딸린 효과를 글씨로(차례로 아래에)
    var fxs = [];
    if (res.pushed >= 2) fxs.push('두 칸 밀어냄'); else if (res.pushed === 1) fxs.push('밀어냄');
    if (res.pulled) fxs.push('끌어당김'); else if (res.noPull) fxs.push('끌지 못함');
    if (res.slam) fxs.push('뒤가 막혀 충돌!');
    if (res.mor) fxs.push('기력 -' + res.mor);
    if (res.confused) fxs.push('혼란 ' + days(res.stN || 1));
    fxs.forEach(function (tx, i) { floatText(tc, tr, tx, C_PLOY, 480 + i * 240, false, 26 + i * 22); });
    if (res.fire) sfx('fire');
    var far = res.ac0 !== undefined && hdist(res.ac0, res.ar0, res.c, res.r) > 1;
    var tid0 = tacIdOf(res), shot = far || tid0 === 'hwasi' || tid0 === 'gwansi' || tid0 === 'nansa';      // 쏘는 공격: 맞는 소리도 화살 소리로(v0.12)
    if (shot) sfx(res.fail ? 'arrowfail' : (res.kind === 'tactic' ? (res.crit ? 'arrowgreat' : 'arrowbig') : (res.crit ? 'arrowbig' : 'arrowhit')));
    else sfx(res.fail ? 'fail' : (res.kind === 'tactic' ? (res.crit ? 'great' : 'big') : (res.crit ? 'big' : (res.tk === 'base' || res.tk === 'fac' ? 'siege' : 'hit'))));
  }
  if (res.counter) floatText(ac, ar, '-' + fmt(res.counter), C_CNT, 520);
  if (res.duel && !res.duel.draw) floatText(res.duel.win ? tc : ac, res.duel.win ? tr : ar, '일기토 패 -' + fmt(res.duel.loss), C_INK, 1150, true, -8);   // 소리는 연출(fx.js) 쪽에서 엇갈리는 순간에
  if (res.selfDmg) floatText(res.ac, res.ar, '-' + fmt(res.selfDmg), C_CNT, 500);
  if (res.fell) { sfx('fall'); if (res.af === G.player) sfx('cheerlate'); }
  voiceAct(res, 1);                                         // v0.13: 결과에 따른 한마디
}
function duelTxt(d) { return ' · 일기토! ' + d.a + ' 대 ' + d.d + ' — ' + (d.draw ? '비김' : (d.win ? d.a : d.d) + ' 승' + (d.ko ? '(쓰러뜨림)' : '')); }
/* 일기토가 끝난 뒤 화면에 적는 것: 두 부대가 얻고 잃은 것 */
function duelOutHtml(S, o, an, dn) {
  if (!o) return '';
  if (o.draw) return '<p>두 주장 모두 공적 +' + DUEL_K.drawMerit + '</p>';
  var wn = o.win ? an : dn, ln = o.win ? dn : an;
  return '<p><b>' + ln + '</b> 기력 -' + (o.ko ? DUEL_K.koMor : DUEL_K.morLose) + ' · 병력 -' + fmt(o.loss) + (o.confused ? ' · 혼란 ' + days(DUEL_K.koTurns) : '') + '</p><p><b>' + wn + '</b> 기력 +' + DUEL_K.morWin + ' · 주장 공적 +' + DUEL_K.merit + '</p>';
}
function presentResult(name, res, quiet) { var msg = resultMsg(name, res); resultFx(res); if (!quiet) toast(msg, 3200); return msg; }
var C_DIM0 = '#6a645a', C_PLOY0 = '#2f4f6f';
function doAct(a) {
  var u = selUnit(), t = UI.target;
  if (!u || !t || UI.busy) return;
  var name = uName(u), res, pa = a.kind === 'ploy' ? (a.adv || null) : null, paRole = pa ? (pa.adv === uLeader(u) ? '주장' : '부장') : '';
  var an = uName(u), dn = t.u ? uName(t.u) : '';
  DUEL_DEFER = a.kind !== 'ploy';                                  // 내가 직접 건 싸움에서 벌어진 일기토는 여기서 끝내지 않고 화면에서 수를 고른다(v0.13)
  try {
    if (a.kind === 'attack') res = unitAttack(u, t);
    else if (a.kind === 'tactic') res = unitTactic(u, a.tac, t);
    else if (a.kind === 'challenge') res = unitChallenge(u, t);
    else res = unitPloy(u, a.ploy, t);
  } finally { DUEL_DEFER = false; }
  if (!res.ok) { toast(res.msg); return; }
  function duelThen(next) {                                        // 일기토가 벌어졌으면: 화면 → 결과를 부대에 입힌다 → next
    var S = res.duelS; if (!S) return next();
    duelOpen(S, 'a', { sub: an + ' 대 ' + dn, onEnd: function () { return duelOutHtml(S, duelFinish(S, res), an, dn); } }, function () { syncScene(); next(); });
  }
  if (a.kind === 'challenge') {                                    // 일기토 신청: 공격 연출 없이 곧바로
    UI.battleTurn = G.turn; playBgm('battle'); UI.rc = null; UI.atk = null; UI.target = null; requestDraw();
    if (!res.accepted) {
      floatText(t.c, t.r, '일기토 거절', C_DIM0, 0, true, -20); floatText(t.c, t.r, '기력 -' + res.mor, C_PLOY0, 320, false, 22); sfx('miss');
      talk(uLeader(t.u), '…상대할 까닭이 없다.', josa(dn, '이가') + ' 일기토를 받지 않았습니다 — 기력 -' + res.mor + ' (' + pcWas(res.p, '응할 확률') + ')', 3400);
      clearSel(); afterAction(); return;
    }
    UI.busy = true;
    duelThen(function () { UI.busy = false; toast(name + duelTxt(res.duel).replace(' · ', ' — '), 3200); clearSel(); afterAction(); });
    return;
  }
  var miss = pa ? advAfter(pa, !!res.success) : '';
  UI.battleTurn = G.turn; playBgm('battle');
  var msg = resultMsg(name, res), fellB = res.fell && t.kind === 'base' ? t.b : null;
  if (res.brokePeace !== undefined) msg += ' — ' + facName(res.brokePeace) + '군과의 보호가 풀림';
  UI.busy = true; UI.rc = null; UI.atk = null; UI.target = null;
  requestDraw();
  actZoom(res.ac0, res.ar0, t.c, t.r, function (back) {      // 싸우는 곳을 가까이 당겨서 보여 준다
    animAct(res, function () {
      duelThen(function () {
        UI.busy = false;
        if (res.duelS && res.duel) msg += duelTxt(res.duel) + (res.duelS.done && (res.killed || res.selfDead) ? ' · 궤멸!' : '');
        if (fellB) fxFall(fellB, fellB.kind === 'gate' ? '점령' : '함락');
        if (miss) talk(pa.adv, miss, msg, 3600, paRole); else toast(msg, 3200);
        clearSel();
        if (fellB && fellB.owner === G.player) selectBase(fellB);
        back();
        afterAction();
      });
    }, function () { resultFx(res); });
  });
}
/* 두 칸 사이를 화면 가운데로 당긴다. 이미 충분히 가까우면 그대로. cb(back) — back() 을 부르면 원래 시점으로 돌아간다 */
function actZoom(c1, r1, c2, r2, cb) {
  var c0 = { x: cam.x, y: cam.y, z: cam.z }, near = cam.z >= 1.45 && onScreen(c1, r1, 30) && onScreen(c2, r2, 30);
  function back() { if (near) return; var x0 = cam.x, y0 = cam.y, z0 = cam.z; anim(360, function (t) { var e = t * (2 - t); cam.x = x0 + (c0.x - x0) * e; cam.y = y0 + (c0.y - y0) * e; cam.z = z0 + (c0.z - z0) * e; clampCam(); }); }
  if (near) { cb(back); return; }
  var a = hexCenter(c1, r1), b = hexCenter(c2, r2), z1 = Math.max(cam.z, 1.75), x0 = cam.x, y0 = cam.y, z0 = cam.z;
  var D = 62 / z1, pt = (68 - 27 * clamp(Math.log(z1 / Z_MIN) / Math.log(Z_MAX / Z_MIN), 0, 1)) * Math.PI / 180;
  var tx = (a[0] + b[0]) / 2, ty = (a[1] + b[1]) / 2 + (0.5 - safeArea().fy) * D * K3 / Math.sin(pt);
  anim(300, function (t) { var e = t * (2 - t); cam.x = x0 + (tx - x0) * e; cam.y = y0 + (ty - y0) * e; cam.z = z0 + (z1 - z0) * e; clampCam(); }, function () { cb(back); });
}
/* 행군 중인 부대의 남은 길(어림) */
function marchLeft(x) {
  var p = marchPath(x, x.dest); if (!p) return '';
  return ' (약 ' + days(marchTurns(x, p)) + ' 남음)';
}
function unitSheet(u) {
  var st = { acts: [] };
  return {
    cls: 'unit',
    on: {
      wait: function () { var x = UMAP[u.id]; if (x) unitWait(x); clearSel(); afterAction(); },
      undo: function () {
        var x = UMAP[u.id]; if (!x) return;
        var mn = UI.mNew, mine0 = mn && mn.id === x.id && mn.turn === G.turn && x.ox >= 0 && K(x.ox, x.oy) === mn.from;      // 물리는 걸음이 방금 내린 행군 · 공격 명령의 첫걸음인가
        if (!unitUndoMove(x)) return;
        if (mine0) { if (x.aim) delete x.aim; x.dest = mn.prev; if (mn.aim0) x.aim = mn.aim0; UI.mNew = null; toast('제자리로 — 방금 내린 명령도 거두었습니다', 2400); }
        UI.rc = unitReach(x); UI.atk = allTargets(x); UI.target = null; mpathOf(x); refreshSheet(); requestDraw();
      },
      unmarch: function () { UI.march = null; UI.pickMarch = false; UI.mNew = null; UI.mpath = null; var x = UMAP[u.id]; if (x) { if (x.aim) aimClear(x); x.dest = -1; } refreshSheet(); requestDraw(); },      // 행군 취소 · 공격 명령 취소
      douse: function () { var x = selUnit(); if (!x || UI.busy) return; var res = unitPloy(x, PLOYS[3], { c: x.c, r: x.r }); if (!res.ok) { toast(res.msg); return; } UI.busy = true; animAct(res, function () { UI.busy = false; toast('주위의 불을 껐습니다'); clearSel(); afterAction(); }, function () { sfx('douse'); }); requestDraw(); },
      act: function (el) { var a = st.acts[+el.getAttribute('data-v')]; if (a && a.ok) doAct(a); else if (a) toast(a.sub); },
      untarget: function () { UI.target = null; refreshSheet(); requestDraw(); },
      moveon: function () { var x = selUnit(), t = UI.target; if (!x || !t || !UI.rc || !UI.rc.stop[K(t.c, t.r)]) return; UI.target = null; UI.march = null; doMove(x, t.c, t.r); },
      facunder: function () { var x = selUnit(), t = x ? facUnder(x) : null; if (!t) return; UI.target = t; UI.march = null; UI.pickMarch = false; refreshSheet(); requestDraw(); },
      tacinfo: function () { var x = selUnit(), t = UI.target; if (x && t && t.kind === 'unit' && alive(t.u)) showTacticInfo(x, t.u); },
      off: function (el) { showOfficer(off(+el.getAttribute('data-v'))); },
      corps: function () { var x = UMAP[u.id], cp = x && unitCorps(x); if (cp) showCorps(cp.id); },
      supply: function () { var x = UMAP[u.id]; if (x) pickSupply(x); },
      tback: function () {                                       // v0.18.1: 짐을 내린 뒤 머물지 · 돌아올지(가는 길에도 바꾼다)
        var x = UMAP[u.id]; if (!x || x.type !== 'trans' || x.f !== G.player) return;
        var hb = transHomeOf(x);
        if (!hb && !x.back) return toast('떠나온 거점이 남의 손에 있어 돌아갈 곳이 없습니다', 2600);
        transSetBack(x, !x.back);
        toast(x.back ? '짐을 내리면 ' + josa(uLeader(x).n, '은는') + ' ' + euro(hb.n) + ' 돌아옵니다' : '짐을 내린 곳에 머뭅니다', 2600); refreshSheet();
      },
      gohome: function () { var x = UMAP[u.id], hb = transHomeOf(x); if (x && hb && !x.done && x.f === G.player) orderMarch(x, hb.c, hb.r); },
      direct: function () { var x = UMAP[u.id]; if (!x) return; var r = corpsTakeUnit(x); if (!r.ok) return toast(r.msg); sfx('ui'); toast(uName(x) + ' — 직할로 되돌렸습니다'); selectUnit(x, true); syncScene(); afterAction(); }
    },
    render: function () {
      var x = UMAP[u.id];
      if (!x) return '';
      var T = UNIT_TYPES[x.type], mine = x.f === G.player, ms = uMembers(x), i;
      var turns = unitFoodTurns(x);
      var h = '<div class="sh-head">' + porTag(ms[0], 'hd') + '<div><div class="sh-title">' + uName(x) + ' ' + facChip(x.f) + pactChip(G.player, x.f) + '</div><div class="sh-sub">' + T.name + (APT_IDX[x.type] !== undefined ? ' 적성 ' + uApt(x) : '') + (stChips(x) ? ' ' + stChips(x) : '') + '</div></div>' +
        '<button class="x" data-a="close" type="button" aria-label="닫기">×</button></div><div class="sh-body">' +
        '<div class="stats ust"><div><span>' + ico('troops') + '병력</span><b>' + fmt(x.troops) + '</b></div><div><span>' + ico('morale') + '기력</span><b>' + x.morale + '</b></div><div><span>' + ico('food') + '군량</span><b' + (turns <= 3 ? ' class="bad"' : '') + '>' + days(turns) + '분</b></div></div>' + (x.type === 'trans' && mine ? cargoLine(x) : '') + terrLine(x) + statusBanner(x);
      var su = selUnit(), cpU = mine ? unitCorps(x) : null;
      if (cpU) {                                                 // 군단의 부대: 하는 일과 [군단] · [직할로]
        var Lu = corpsLead(cpU);
        h += '<div class="cpbn">' + (Lu ? porTag(Lu, 'sm') : '<i class="por sm none"></i>') + '<div><b>' + corpsName(cpU) + '</b> · ' + unitMission(x) + '<small>군단장' + (Lu ? ' ' + Lu.n : '') + '의 명을 따릅니다</small></div></div>' +
          '<div class="cmds"><button class="cmd" type="button" data-a="corps"><b>군단</b><small>' + corpsDirText(cpU) + '</small></button><button class="cmd" type="button" data-a="direct"><b>직할로</b><small>내가 직접 움직인다</small></button></div><div class="rows">';
        for (i = 0; i < ms.length; i++) h += offRow(ms[i], { badge: i === 0 ? '주장' : '부장' });
        return h + '</div></div>';
      }
      if (su === x) {
        if (UI.target) {
          var t = UI.target;
          var tn = t.kind === 'unit' ? uName(t.u) + ' · ' + UNIT_TYPES[t.u.type].name + ' ' + fmt(t.u.troops) + '명 · 기력 ' + t.u.morale : (t.kind === 'base' ? t.b.n + ' · 병력 ' + fmt(t.b.troops) + ' · 내구 ' + fmt(t.b.dur) : t.b.n + '의 ' + FAC[t.b.plots[t.i].fac.t].name);
          st.acts = targetActions(x, t);
          h += '<div class="tgt">대상 — <b>' + tn + '</b>' + (t.kind === 'unit' && stChips(t.u) ? ' ' + stChips(t.u) : '') + '</div>';
          if (t.kind === 'unit') h += terrNote(x, t.u);                                    // v0.15: 이 싸움에 걸리는 지형
          if (t.kind === 'unit' && t.u.status) h += '<p class="note stn">' + (t.u.status === 'confuse' ? '반격 없음 · 받는 피해 +25% · 전법 성공률 +10' : '반격 없음') + '</p>';
          if (t.kind !== 'unit' && peaceWouldBreak(t.b.owner)) h += '<p class="note pzw">먼저 치면 <b>' + facName(t.b.owner) + '군과의 보호가 풀립니다</b></p>';
          var adv1 = null, ys = [], ns = []; st.acts.forEach(function (a0) { if (!a0.adv) return; if (!adv1) adv1 = a0.adv; (a0.adv.says ? ys : ns).push(a0.label); });
          var recA = null; st.acts.forEach(function (a0) { if (a0.rec) recA = a0; });
          var advO = adv1 ? adv1.adv : (recA ? uStaff(x) : null);      // v0.20: 말하는 이는 이 부대의 참모(부장 — 없으면 주장)
          if (advO) h += sayRow(advO, (recA ? '<b class="rc">' + recA.label + josa(recA.label, '이가').slice(-1) + ' 가장 낫겠습니다.</b> ' : '') + (ys.length ? '<b class="ok">' + ys.join('·') + josa(ys[ys.length - 1], '은는').slice(-1) + ' 통하겠' + (ns.length ? '으나' : '습니다.') + '</b> ' : '') + (ns.length ? '<b class="bad">' + ns.join('·') + josa(ns[ns.length - 1], '은는').slice(-1) + ' 어렵겠습니다.</b>' : ''), adv1 ? accT(adv1.acc) : '', 'adv advn', advO === uLeader(x) ? '주장' : '부장');
          h += '<div class="acts">';
          for (i = 0; i < st.acts.length; i++) { var a = st.acts[i]; h += '<button class="act' + (a.pri && a.ok ? ' pri' : '') + (a.ok ? '' : ' off') + (a.fx ? ' tac' : '') + '" type="button" data-a="act" data-v="' + i + '"><b>' + a.label + (a.han ? ' <i class="hj">' + a.han + '</i>' : '') + '</b>' + (a.fx ? '<small class="fx">' + a.fx + '</small>' : '') + (a.sub ? '<small>' + a.sub + '</small>' : '') + (a.rec ? '<i class="rec" title="부장의 추천">薦</i>' : '') + '</button>'; }
          if (t.kind === 'unit' && (TACTICS[x.type] || []).length && !pactOn(x.f, t.u.f)) h += '<button class="act" type="button" data-a="tacinfo"><b>전법 풀이</b></button>';      // 칠 수 없는 상대에게는 풀이도 내지 않는다
          if (t.kind === 'fac' && UI.rc && UI.rc.stop[K(t.c, t.r)]) h += '<button class="act" type="button" data-a="moveon"><b>이 칸으로 이동</b></button>';
          h += '<button class="act" type="button" data-a="untarget"><b>대상 취소</b></button></div>';
        } else {
          var canDouse = ployTargets(x, PLOYS[3]).length > 0;
          var fu = facUnder(x);
          h += '<div class="acts">' + (fu ? '<button class="act' + (justOut(x) ? ' off' : ' pri') + '" type="button" data-a="facunder"><b>시설 파괴</b><small>' + (justOut(x) ? '다음 턴부터' : '발밑의 ' + FAC[fu.b.plots[fu.i].fac.t].name) + '</small></button>' : '') +
            '<button class="act" type="button" data-a="wait"><b>대기</b></button>' +
            '<button class="act' + (x.ox >= 0 ? '' : ' off') + '" type="button" data-a="undo"><b>이동 취소</b></button>' +
            (canDouse ? '<button class="act" type="button" data-a="douse"><b>소화</b><small>기력 10</small></button>' : '') +
            (x.type === 'trans' ? '<button class="act' + (supplyPairs(x).length ? ' pri' : ' off') + '" type="button" data-a="supply"><b>보급</b><small>' + (supplyPairs(x).length ? '옆의 아군 부대에' : '아군 부대 옆에서') + '</small></button>' : (supplyPairs(x).length ? '<button class="act pri" type="button" data-a="supply"><b>보급 받기</b><small>옆의 수송대에서</small></button>' : '')) +
            (x.type === 'trans' ? gohomeBtn(x) : '') +
            ((x.dest >= 0 || x.aim) ? '<button class="act" type="button" data-a="unmarch"><b>' + (x.aim ? '명령 취소' : '행군 취소') + '</b></button>' : '') + '</div>' +
            (x.aim ? '<p class="note aimn"><b class="hi">' + aimName(x) + ' 공격 명령</b> — 턴을 마칠 때마다 다가가고, 닿으면 알아서 칩니다</p>' : (x.dest >= 0 ? '<p class="note"><b class="hi">' + destName(x.dest) + ' 방면 행군 중</b>' + marchLeft(x) + '</p>' : '<p class="note">파란 칸 = 이동 · 적 = 공격 · <b>먼 곳을 누르면 그곳으로 행군</b> · 먼 적을 누르면 가서 칩니다</p>'));
        }
      } else if (mine && x.done && x.status) h += '<p class="note">' + statusName(x.status) + ' — 명령을 내릴 수 없습니다</p>';
      else if (mine && x.done) h += '<p class="note">이번 턴 행동 끝' + (x.dest >= 0 ? ' · ' + destName(x.dest) + ' 방면 행군 중' : '') + '</p>' + (x.type !== 'trans' && supplyPairs(x).length ? '<div class="acts"><button class="act pri" type="button" data-a="supply"><b>보급 받기</b><small>옆의 수송대에서</small></button></div>' : '') + (x.type === 'trans' && !x.status ? '<div class="acts">' + tbackBtn(x) + '</div>' : '');
      h += '<div class="rows">';
      for (i = 0; i < ms.length; i++) h += offRow(ms[i], { badge: i === 0 ? '주장' : '부장' });
      h += '</div></div>';
      return h;
    }
  };
}

/* ---------- 보급(v0.11): 수송대 t → 옆의 아군 부대 u ---------- */
function foodDays(food, u, troops) { var per = Math.ceil(troops / (uHas(u, '둔전') ? 40 : 20)); return per > 0 ? Math.floor(food / per) : 0; }
function cargoLine(t) {                                    // 수송대에 실은 것
  var c = t.cargo || {}, h = '<div class="wp cgo"><span>' + ico('food') + '병량 <b>' + fmt(t.food) + '</b></span>' + (t.gold ? '<span>' + ico('gold') + '금 <b>' + fmt(t.gold) + '</b></span>' : '');
  [['spear', '창'], ['halberd', '극'], ['bow', '노'], ['horse', '군마']].forEach(function (w) { if (c[w[0]]) h += '<span>' + ico(w[0]) + w[1] + ' <b>' + fmt(c[w[0]]) + '</b></span>'; });
  if (c.ram) h += '<span>' + ico('ram') + '충차 <b>' + c.ram + '</b></span>';
  return h + '</div>';
}
function supplyPairs(x) {                                  // 이 부대가 낄 수 있는 보급: [수송대, 받는 부대] 들(군단의 부대는 빼고)
  var out = [];
  if (x.type === 'trans') { if (!x.done && !x.status && !unitCorps(x)) supplyTargets(x).forEach(function (u) { if (!unitCorps(u)) out.push([x, u]); }); }
  else if (!unitCorps(x)) supplySources(x).forEach(function (t) { if (!unitCorps(t)) out.push([t, x]); });
  return out;
}
function flowSupply(t, u) {
  if (!alive(t) || !alive(u)) return;
  var mx = supplyMax(t, u), own = Math.ceil(t.troops / 20) * 3;                 // 수송대가 30일 버틸 몫은 남기는 것을 처음 값으로
  var st = { food: Math.max(0, Math.floor((mx.food - own) / 100) * 100), troops: 0 };
  function pv() {
    var a = foodDays(u.food, u, u.troops), b2 = foodDays(u.food + st.food, u, u.troops + st.troops), left = t.food - st.food, ld = foodDays(left, t, t.troops - st.troops);
    return uName(u) + ' 군량 <b>' + days(a) + '분 → ' + days(b2) + '분</b>' + (st.troops ? ' · 병력 <b>' + fmt(u.troops) + ' → ' + fmt(u.troops + st.troops) + '</b>' : '') +
      '<br><small>수송대에 남는 병량 ' + fmt(left) + ' (' + days(ld) + '분)' + (ld < 3 ? ' — <b class="bad">돌아갈 길이 멀면 굶습니다</b>' : '') + '</small>';
  }
  showDialog({
    render: function () {
      var T = UNIT_TYPES[u.type], wp = T.weapon;
      var h = dlgHead('보급 — ' + uName(t) + ' → ' + uName(u)) + '<div class="dlg-b">' +
        '<div class="card supc">' + porTag(uLeader(u), 'md') + '<p><b>' + uName(u) + '</b> · ' + T.name + ' ' + fmt(u.troops) + '명<br><small>군량 ' + fmt(u.food) + ' (' + days(foodDays(u.food, u, u.troops)) + '분) · 지휘 한도 ' + fmt(cmdCap(uLeader(u))) + '</small></p></div>' +
        '<div class="fld"><label><span>병량 (수송대에 ' + fmt(mx.food) + ')</span><b id="spFv">' + fmt(st.food) + '</b></label><input type="range" min="0" max="' + Math.floor(mx.food / 100) * 100 + '" step="100" value="' + st.food + '" data-i="food"></div>';
      if (mx.troops >= 100) h += '<div class="fld"><label><span>병력 (' + fmt(mx.troops) + '명까지 — ' + mx.why + ')</span><b id="spTv">' + fmt(st.troops) + '</b></label><input type="range" min="0" max="' + mx.troops + '" step="100" value="' + st.troops + '" data-i="troops"></div>';
      else h += '<p class="note">병력은 넘길 수 없습니다 — ' + (t.troops <= 100 ? '수송대에 100명은 남깁니다' : mx.why) + (wp && wp !== 'ram' ? ' · ' + T.name + '에게는 ' + WEAPON_NAMES[wp] + '도 실어 와야 합니다' : '') + '</p>';
      h += '<p class="note">보급하면 수송대는 이번 턴의 행동을 마칩니다 · 행동력은 들지 않습니다</p></div>' +
        '<div class="dlg-f"><div class="pv" id="spP">' + pv() + '</div><button class="btn pri" type="button" data-a="ok">보급</button></div>';
      return h;
    },
    on: {
      food: function (el) { st.food = +el.value; $('spFv').textContent = fmt(st.food); $('spP').innerHTML = pv(); },
      troops: function (el) { st.troops = +el.value; $('spTv').textContent = fmt(st.troops); $('spP').innerHTML = pv(); },
      ok: function () {
        var r = cmdSupply(t, u, st);
        if (!r.ok) return toast(r.msg);
        closeDialog(); sfx('drum');
        talk(uLeader(t), sayLine(uLeader(t), 'trans'), uName(u) + '에 보급 — ' + (r.food ? '병량 ' + fmt(r.food) : '') + (r.food && r.troops ? ' · ' : '') + (r.troops ? '병력 ' + fmt(r.troops) + '명' : '') + (r.home !== undefined ? ' · 다음 턴부터 ' + euro(G.bases[r.home].n) + ' 돌아갑니다' : ''), r.home !== undefined ? 3800 : 3000);
        if (R3 && R3.ready) syncScene();
        var su = selUnit(); if (su) { UI.rc = unitReach(su); UI.atk = allTargets(su); } else { UI.rc = null; UI.atk = null; }
        refreshSheet(); requestDraw(); afterAction();
        if (r.home === undefined) setTimeout(function () { if (!MODAL) askSupplyDone(t); }, 900);      // v0.21: 보급을 마쳤으니 묻는다
      }
    }
  }, true);
}
/* [보급] · [보급 받기]: 짝이 하나면 바로, 여럿이면 고른다 */
function pickSupply(x) {
  var ps = supplyPairs(x);
  if (!ps.length) return toast(x.type === 'trans' ? '아군 부대의 옆 칸으로 가면 병량과 병력을 넘길 수 있습니다' : '옆에 보급해 줄 수송대가 없습니다', 2800);
  if (ps.length === 1) return flowSupply(ps[0][0], ps[0][1]);
  showDialog({
    render: function () {
      var h = dlgHead(x.type === 'trans' ? '보급 — 어느 부대에' : '보급 — 어느 수송대에서') + '<div class="dlg-b"><div class="rows">';
      ps.forEach(function (pr, i) { var o = pr[x.type === 'trans' ? 1 : 0]; h += '<button class="row" type="button" data-a="go" data-v="' + i + '">' + porTag(uLeader(o)) + '<span class="mid"><span class="nm">' + uName(o) + '</span><span class="ds">' + UNIT_TYPES[o.type].name + ' ' + fmt(o.troops) + '명 · 군량 ' + fmt(o.food) + ' (' + days(unitFoodTurns(o)) + '분)</span></span></button>'; });
      return h + '</div></div>';
    },
    on: { go: function (el) { var pr = ps[+el.getAttribute('data-v')]; if (pr) flowSupply(pr[0], pr[1]); } }
  });
}

/* ---------- 거점 패널 ---------- */
function baseSheet(b0, tab0) {
  var st = { tab: b0.kind === 'gate' ? (tab0 === 'men' ? 'men' : 'mil') : (tab0 || 'home') };
  function B() { return G.bases[b0.id]; }
  var on = {
    tab: function (el) { st.tab = el.getAttribute('data-v'); refreshSheet(); },
    off: function (el) { showOfficer(off(+el.getAttribute('data-v'))); },
    draft: function () { flowDraft(B()); }, patrol: function () { flowPatrol(B()); }, train: function () { flowTrain(B()); },
    produce: function () { flowProduce(B()); }, trade: function () { flowTrade(B()); }, deploy: function () { flowDeploy(B()); },
    trans: function () { flowTransport(B()); }, search: function () { flowSearch(B()); }, recruit: function () { flowRecruit(B()); },
    reward: function () { flowReward(B()); }, move: function () { flowMove(B()); }, captive: function () { flowCaptive(B()); }, dip: function () { flowDip(B()); },
    plot: function (el) { var i = +el.getAttribute('data-v'), b = B(); if (b.plots[i].fac) flowFacility(b, i); else flowDevelop(b, i); },
    corps: function () { var cp = baseCorps(B()); if (cp) showCorps(cp.id); },
    direct: function () { var b = B(), cp = baseCorps(b); if (!cp) return; var nm = corpsName(cp), r = corpsRelease(b.id); if (!r.ok) return toast(r.msg); sfx('ui'); toast(b.n + ' — 직할로 되돌렸습니다' + (r.gone ? ' (' + nm + ' 해산)' : '')); syncScene(); refreshSheet(); afterAction(); },
    cjoin: function (el) { var b = B(), cp = corpsById(+el.getAttribute('data-v')); if (!cp) return; var r = corpsAssign(cp, b.id); if (!r.ok) return toast(r.msg); corpsSaid(cp, 'corps', undefined, josa(b.n, '을를') + ' ' + corpsName(cp) + '에 맡겼습니다'); syncScene(); refreshSheet(); afterAction(); },
    cnew: function () { showCorpsNew(B().id); },
    order: function () { showOrderInfo(B()); },
    marchhere: function () {                                   // v0.18: 방금 고르고 있던 부대를 이 성으로
      var b = B(), mu = UMAP[UI.mfrom]; if (!mu || mu.f !== G.player || mu.done) { UI.mfrom = -1; refreshSheet(); return; }
      selectUnit(mu, true); orderMarch(mu, b.c, b.r);
    }
  };
  function cmd(a, name, sub, pri, offc) { return '<button class="cmd' + (pri ? ' pri' : '') + (offc ? ' off' : '') + '" type="button" data-a="' + a + '"><b>' + name + '</b><small>' + sub + '</small></button>'; }
  return {
    on: on,
    fac: function () { var b = B(); return (st.tab === 'fac' && b.owner === G.player && b.kind === 'city' && !baseCorps(b)) ? b : null; },      // 시설 탭을 보는 중 = 건설 자리를 비춘다
    render: function () {
      var b = B(), mine = b.owner === G.player, city = b.kind === 'city', i;
      var gov = null; baseOfficers(b).forEach(function (o) { if (!gov || (isLord(o) ? 1000 : 0) + o.ldr + o.pol > (isLord(gov) ? 1000 : 0) + gov.ldr + gov.pol) gov = o; });
      var h = '<div class="sh-head">' + (gov ? porTag(gov, 'hd') : thumb(city ? 'city_' + b.sz : 'gate')) + '<div><div class="sh-title">' + b.n + ' ' + facChip(b.owner) + pactChip(G.player, b.owner) + '</div><div class="sh-sub">' + SIZE_NAME[b.sz] + (gov ? ' · ' + (isLord(gov) ? '군주 ' : '태수 ') + gov.n : '') + (mine ? ' · 대기 무장 ' + idleOfficers(b).length + '명' : '') + '</div></div><button class="x" data-a="close" type="button" aria-label="닫기">×</button></div><div class="sh-body">';
      var mfu = UI.mfrom >= 0 ? UMAP[UI.mfrom] : null;
      if (mfu && mfu.f === G.player && !mfu.done && (b.owner === G.player || b.owner < 0)) {
        var mfp = marchPath(mfu, K(b.c, b.r));
        h += '<div class="acts mfrom"><button class="act' + (mfp ? ' pri' : ' off') + '" type="button" data-a="marchhere"><b>' + uName(mfu) + ' — 이 ' + (city ? '성' : '관문') + '으로 행군</b><small>' + (mfp ? '약 ' + days(marchTurns(mfu, mfp)) + (b.owner < 0 ? ' · 닿으면 차지합니다' : ' · 닿으면 입성') : '갈 길이 없습니다') + '</small></button></div>';
      }
      h += '<div class="stats">' +
        '<div class="w"><span>' + ico('gold') + '금</span><b>' + fmt(b.gold) + (city && b.owner >= 0 ? ' <small>+' + fmt(goldIncome(b)) + '</small>' : '') + '</b></div><div class="w"><span>' + ico('food') + '병량</span><b>' + fmt(b.food) + (city && b.owner >= 0 ? ' <small>+' + fmt(foodIncome(b)) + '</small>' : '') + '</b></div>' +
        '<div><span>' + ico('troops') + '병력</span><b>' + fmt(b.troops) + '</b></div><div><span>' + ico('morale') + '기력</span><b>' + b.morale + '</b></div>' + (city ? '<div class="tap" data-a="order"><span>' + ico('order') + '치안</span><b' + (b.order < 50 ? ' class="bad"' : '') + '>' + b.order + (b.owner >= 0 ? '<small>수입 ' + incPct(b.order) + '% ›</small>' : '') + '</b></div>' : '') +
        '<div><span>' + ico('dur') + '내구</span><b' + (b.dur < b.maxDur * 0.5 ? ' class="bad"' : '') + '>' + fmt(b.dur) + (b.owner >= 0 && b.dur < b.maxDur ? (durHealAt(b, G.turn + 1) ? ' <small>+' + fmt(durHealAt(b, G.turn + 1)) + '</small>' : ' <small class="bad">회복 멈춤</small>') : '') + '</b></div></div>';
      h += '<div class="wp"><span>' + ico('spear') + '창 <b>' + fmt(b.w.spear) + '</b></span><span>' + ico('halberd') + '극 <b>' + fmt(b.w.halberd) + '</b></span><span>' + ico('bow') + '노 <b>' + fmt(b.w.bow) + '</b></span><span>' + ico('horse') + '군마 <b>' + fmt(b.w.horse) + '</b></span>' + (b.w.ram ? '<span>' + ico('ram') + '충차 <b>' + b.w.ram + '</b></span>' : '') + '</div>';
      var cpB = mine ? baseCorps(b) : null;
      if (cpB) {                                                 // 군단에 맡긴 거점: 명령은 군단장이 내린다
        var Lb = corpsLead(cpB), ob = baseOfficers(b);
        h += '<div class="cpbn">' + (Lb ? porTag(Lb, 'sm') : '<i class="por sm none"></i>') + '<div><b>' + corpsName(cpB) + '</b> · ' + corpsDirText(cpB) + '<small>군단장' + (Lb ? ' ' + Lb.n : ' 없음') + ' — 이 거점의 명령은 군단장이 내립니다</small></div></div>' +
          '<div class="cmds"><button class="cmd pri" type="button" data-a="corps"><b>군단</b><small>방침 · 군단장</small></button><button class="cmd" type="button" data-a="direct"><b>직할로</b><small>내가 직접 다스린다</small></button><button class="cmd" type="button" data-a="trans"><b>수송</b><small>내가 직접 보낸다</small></button></div>' +      // v0.18: 군단의 거점에서도 수송은 내가
          '<div class="sec">무장 <em class="cnt">' + ob.length + '</em></div><div class="rows">';
        ob.sort(function (x, y) { return (isLord(y) ? 1000 : 0) + (y.ldr + y.war + y.int + y.pol) / 4 - (isLord(x) ? 1000 : 0) - (x.ldr + x.war + x.int + x.pol) / 4; });
        for (i = 0; i < ob.length; i++) h += offRow(ob[i], { badge: isLord(ob[i]) ? '군주' : (cpB.lead === ob[i].id ? '군단장' : advTag(ob[i])), rt: '<span class="' + (ob[i].loy < 70 ? 'bad' : '') + '">충 ' + ob[i].loy + '</span><br>' + offStatus(ob[i]) });
        return h + '</div></div>';
      }
      if (!mine) {
        var os = baseOfficers(b);
        h += '<div class="sec">' + (b.owner >= 0 ? '주둔 무장 ' + os.length + '명' : '빈 거점 — 부대가 들어가면 차지') + '</div><div class="rows">';
        os.sort(function (x, y) { return (isLord(y) ? 1000 : 0) + aiMilScore(y) - (isLord(x) ? 1000 : 0) - aiMilScore(x); });
        for (i = 0; i < os.length; i++) h += offRow(os[i], { badge: isLord(os[i]) ? '군주' : '' });
        var fr0 = freeOfficers(b); for (i = 0; i < fr0.length; i++) h += offRow(fr0[i], { badge: '재야' });
        return h + '</div></div>';
      }
      var tabs = city ? [['home', '내정'], ['mil', '출진'], ['men', '인재'], ['fac', '건설']] : [['mil', '출진'], ['men', '인재']];
      if (facBases(G.player).length >= 2) tabs.push(['corps', '군단']); else if (st.tab === 'corps') st.tab = tabs[0][0];      // v0.10: 거점이 둘 이상이면 군단에 맡길 수 있다      // v0.9.2: '군사' → '출진'(STATUS 창의 군사 = 軍師 와 같은 소리)
      h += '<div class="tabs">'; for (i = 0; i < tabs.length; i++) h += '<button type="button" data-a="tab" data-v="' + tabs[i][0] + '"' + (st.tab === tabs[i][0] ? ' class="on"' : '') + '>' + tabs[i][1] + '</button>'; h += '</div>';
      if (st.tab === 'corps') {
        var cps = corpsAll(), canLead = baseOfficers(b).some(function (o) { return !isLord(o); });
        h += '<p class="note">직할 거점입니다. 군단에 맡기면 군단장이 <b>방침</b>대로 다스리고, 언제든 직할로 되돌릴 수 있습니다.</p><div class="rows">';
        for (i = 0; i < cps.length; i++) { var Lj = corpsLead(cps[i]); h += '<div class="row">' + (Lj ? porTag(Lj) : '<i class="por none"></i>') + '<span class="mid"><span class="nm">' + corpsName(cps[i]) + '</span><span class="ds">' + (Lj ? Lj.n + ' · ' : '') + corpsDirText(cps[i]) + ' · 거점 ' + corpsBases(cps[i]).length + '</span></span><button class="btn pri" type="button" data-a="cjoin" data-v="' + cps[i].id + '">맡기기</button></div>'; }
        h += '</div><div class="cmds"><button class="cmd' + (cps.length ? '' : ' pri') + (cps.length >= CORPS_MAX ? ' off' : '') + '" type="button" data-a="cnew"><b>새 군단</b><small>' + (cps.length >= CORPS_MAX ? CORPS_MAX + '개까지' : (canLead ? '이 거점부터' : '거점을 골라서')) + '</small></button></div>';
      } else if (st.tab === 'home') {
        h += '<div class="cmds">' + cmd('draft', '징병', '금 ' + COST.draft + ' · 행 ' + AP.draft, false, !hasFac(b, 'barracks')) + cmd('patrol', '순찰', '금 ' + COST.patrol + ' · 행 ' + AP.patrol) + cmd('train', '훈련', '행 ' + AP.train) +
          cmd('produce', '생산', '금 ' + COST.produce + '~ · 행 ' + AP.produce, false, !hasFac(b, 'smithy') && !hasFac(b, 'stable') && !hasFac(b, 'workshop')) + cmd('trade', '거래', '행 ' + AP.trade, false, !hasFac(b, 'market')) + '</div>';
      } else if (st.tab === 'mil') {
        h += '<div class="cmds">' + cmd('deploy', '출진', '행 ' + AP.deploy, true) + cmd('trans', '수송', '행 ' + AP.deploy) + (city ? '' : cmd('train', '훈련', '행 ' + AP.train)) + '</div>';
        var mu = facUnits(G.player).filter(function (u) { return u.home === b.id; });
        if (mu.length) h += '<p class="note">이 거점에서 나간 부대 ' + mu.length + '개</p>';
      } else if (st.tab === 'men') {
        var fr = freeOfficers(b), cp = b.captives.length, nbO = poachTargets(b).length;
        h += '<div class="cmds">' + (city ? cmd('search', '탐색', '행 ' + AP.search) : '') + cmd('recruit', '등용', (fr.length || cp || nbO) ? [fr.length ? '재야 ' + fr.length : '', cp ? '포로 ' + cp : '', nbO ? '이웃 ' + nbO : ''].filter(function (x) { return x; }).join(' · ') : '대상 없음', fr.length + cp > 0 || poachHints(b).length > 0, !(fr.length + cp + nbO)) + cmd('reward', '포상', '금 ' + COST.reward + ' · 행 ' + AP.reward) + cmd('dip', '외교', dipSub(), dipOffers().length > 0) +
          cmd('move', '이동', '행 ' + AP.move) + (cp ? cmd('captive', '포로', cp + '명') : '') + '</div><div class="sec">무장</div><div class="rows">';
        var all = G.officers.filter(function (o) { return o.f === b.owner && ((o.st === 'active' && o.loc === b.id && o.unit === null) || (o.st === 'travel' && o.dest === b.id)); });
        all.sort(function (x, y) { return (isLord(y) ? 1000 : 0) + (y.ldr + y.war + y.int + y.pol) / 4 - (isLord(x) ? 1000 : 0) - (x.ldr + x.war + x.int + x.pol) / 4; });
        for (i = 0; i < all.length; i++) h += offRow(all[i], { badge: isLord(all[i]) ? '군주' : advTag(all[i]), dim: all[i].acted || all[i].st === 'travel', rt: '<span class="' + (all[i].loy < 70 ? 'bad' : '') + '">충 ' + all[i].loy + '</span><br>' + offStatus(all[i]) });
        if (fr.length) { h += '</div><div class="sec">재야</div><div class="rows">'; for (i = 0; i < fr.length; i++) h += offRow(fr[i], {}); }
        h += '</div>';
      } else {
        var why = buildWhy(b), nE = emptyLots(b).length, nF = b.plots.length - nE;
        if (nE) h += '<div class="sec">빈 부지 <em class="cnt">' + nE + '</em></div>' + (why ? '<p class="note lotw">지금은 지을 수 없습니다 — ' + why + '</p>' : '') + '<div class="lots">';       // 빈 부지는 번호 단추 한 줄(지도의 번호와 같다) — 옆에 무엇이 있는지는 지도와 고르는 창이 알려 준다
        var em = emptyLotsByNo(b);
        for (i = 0; i < em.length; i++) h += '<button class="lot' + (why || UAT[K(b.plots[em[i]].c, b.plots[em[i]].r)] ? ' no' : '') + '" type="button" data-a="plot" data-v="' + em[i] + '" aria-label="빈 부지 ' + lotNo(b, em[i]) + '">' + lotNo(b, em[i]) + '</button>';
        h += (nE ? '</div>' : '') + (nF ? '<div class="sec">지은 시설 <em class="cnt">' + nF + '</em></div>' : '') + '<div class="rows">';
        var built = []; for (i = 0; i < b.plots.length; i++) if (b.plots[i].fac) built.push(i);
        built.sort(function (x, y) { return lotNo(b, x) - lotNo(b, y); });                                     // 번호 차례(지도의 딱지와 같다)
        for (var bi = 0; bi < built.length; bi++) {
          i = built[bi];
          var fc = b.plots[i].fac;
          h += '<button class="row" type="button" data-a="plot" data-v="' + i + '">' + facThumb(fc) + '<span class="mid"><span class="nm">' + lotChip(b, i) + FAC[fc.t].name + facLv(fc) + '</span><span class="ds">' + (fc.done ? facDesc(fc) : '건설 중 — ' + days(Math.max(1, Math.ceil((fc.need - fc.prog) / fc.rate))) + ' 남음') + '</span></span>' + (mergeCandidates(b, i).length ? '<span class="rt hi">합병 가능</span>' : '') + '</button>';
        }
        h += '</div>';
      }
      return h + '</div>';
    }
  };
}
/* 치안의 효과(v0.11) — 셈은 core.js 의 goldIncome · foodIncome · draftAmount 와 같다 */
function incPct(order) { return Math.round(50 + order / 2); }            // 금·병량 수입에 곱해지는 몫(%)
function draftPct(order) { return Math.round(40 + order * 0.6); }         // 징병량에 곱해지는 몫(%)
function showOrderInfo(b) {
  showDialog({
    render: function () {
      var o = b.order;
      return dlgHead(b.n + ' 치안 ' + o) + '<div class="dlg-b"><div class="stats ordst"><div><span>' + ico('gold') + '금·병량 수입</span><b' + (o < 50 ? ' class="bad"' : '') + '>' + incPct(o) + '%</b></div><div><span>' + ico('troops') + '징병량</span><b' + (o < 50 ? ' class="bad"' : '') + '>' + (o < 20 ? '징병 불가' : draftPct(o) + '%') + '</b></div></div>' +
        '<div class="help"><ul><li>수입은 치안 100일 때 100%, 0일 때 50%입니다. 징병량은 100일 때 100%, 0일 때 40%이고 <b>치안이 20 아래면 징병할 수 없습니다</b>.</li>' +
        '<li><b>내려갈 때</b> — 징병할 때마다 −10(인덕 −5) · 50을 넘으면 매월 −1 · 도시의 병량이 바닥나면 턴마다 −3 · 성이 함락되면 −25</li>' +
        '<li><b>올릴 때</b> — <b>순찰</b>(금 ' + COST.patrol + '). 무력이나 통솔이 높은 무장일수록, 여럿이 할수록 많이 오릅니다(위압은 두 배).</li>' +
        '<li>가만히 두면 50으로 내려가 수입이 75%에 머뭅니다. 치안이 낮다고 민란이 나거나 무장이 떠나지는 않습니다.</li></ul></div></div>';
    }, on: {}
  }, true);
}
function done(res, msg, snd, who, key, x) {
  if (!res.ok) { toast(res.msg); return false; }
  if (snd) sfx(snd);
  if (who && key) talk(who, sayLine(who, key, x), msg); else if (msg) toast(msg);
  refreshSheet(); afterAction();
  return true;
}

/* ---------- 내정 흐름 ---------- */
function flowDraft(b) {
  if (!hasFac(b, 'barracks')) return toast('병영이 필요합니다');
  pickOfficers({ title: '징병 — 담당 무장', list: idleOfficers(b), max: 3, hi: 'cha', key: function (o) { return o.cha + (o.sk === '명성' ? 40 : 0); }, auto: function (n) { return autoPick('draft', b, null, n); },
    preview: function (os) { return '예상 <b>+' + fmt(draftAmount(b, os)) + '명</b> · 치안 -' + (anyHas(os, '인덕') ? 5 : 10) + ' · 금 ' + COST.draft; } },
    function (os) { var r = cmdDraft(b, ids(os)); return done(r, r.ok ? '징병 +' + fmt(r.n) + '명' : '', 'drums', os[0], 'draft'); });
}
function flowPatrol(b) {
  pickOfficers({ title: '순찰 — 담당 무장', list: idleOfficers(b), max: 3, hi: 'war', key: function (o) { return Math.max(o.war, o.ldr) + (o.sk === '위압' ? 40 : 0); }, auto: function (n) { return autoPick('patrol', b, null, n); },
    preview: function (os) { var v = Math.round(5 + Math.max(bestOf(os, 'war'), bestOf(os, 'ldr')) / 9 + (os.length - 1) * 2); if (anyHas(os, '위압')) v *= 2; v = Math.min(v, 100 - b.order); return '치안 <b>+' + v + '</b> · 금 ' + COST.patrol + '<br><small>수입 ' + incPct(b.order) + '% → ' + incPct(b.order + v) + '%</small>'; } },
    function (os) { var r = cmdPatrol(b, ids(os)); return done(r, r.ok ? '치안 +' + r.n : '', 'step', os[0], 'patrol'); });
}
function flowTrain(b) {
  pickOfficers({ title: '훈련 — 담당 무장', list: idleOfficers(b), max: 3, hi: 'ldr', key: function (o) { return o.ldr; }, auto: function (n) { return autoPick('train', b, null, n); },
    preview: function (os) { return '기력 <b>+' + Math.min(Math.round(8 + bestOf(os, 'ldr') / 8 + (os.length - 1) * 2), 100 - b.morale) + '</b>'; } },
    function (os) { var r = cmdTrain(b, ids(os)); return done(r, r.ok ? '기력 +' + r.n : '', 'shout', os[0], 'train'); });
}
function flowProduce(b) {
  var kinds = [['spear', '창', 'smithy'], ['halberd', '극', 'smithy'], ['bow', '노', 'smithy'], ['horse', '군마', 'stable'], ['ram', '충차', 'workshop']];
  showDialog({
    render: function () {
      var h = dlgHead('생산 — 무엇을 만들까요') + '<div class="dlg-b"><div class="opts">';
      for (var i = 0; i < kinds.length; i++) { var ok = !!hasFac(b, kinds[i][2]); h += '<button class="opt' + (ok ? '' : ' off') + '" type="button" data-a="k" data-v="' + i + '"><b>' + ico(kinds[i][0]) + kinds[i][1] + '</b><small>' + (ok ? '재고 ' + fmt(b.w[kinds[i][0]]) : FAC[kinds[i][2]].name + ' 필요') + '</small></button>'; }
      return h + '</div><p class="note">금 ' + COST.produce + ' · 충차는 금 ' + COST.ram + '</p></div>';
    },
    on: { k: function (el) {
      var k = kinds[+el.getAttribute('data-v')];
      if (!hasFac(b, k[2])) return toast(josa(FAC[k[2]].name, '이가') + ' 필요합니다');
      pickOfficers({ push: true, title: k[1] + ' 생산 — 담당 무장', list: idleOfficers(b), max: k[0] === 'ram' ? 1 : 3, hi: 'int', key: function (o) { return o.int; }, auto: function (n) { return autoPick('produce', b, { kind: k[0] }, n); },
        preview: function (os) { return k[0] === 'ram' ? '충차 1대 · 금 ' + (anyHas(os, '발명') ? COST.ramInv : COST.ram) : '예상 <b>+' + fmt(produceAmount(b, k[0], os)) + '</b> · 금 ' + COST.produce; } },
        function (os) { var r = cmdProduce(b, k[0], ids(os)); return done(r, r.ok ? k[1] + ' +' + fmt(r.n) : '', 'hammer', os[0], 'produce', k[1]); });
    } }
  });
}
function flowTrade(b) {
  if (!hasFac(b, 'market')) return toast('시장이 필요합니다');
  var st = { dir: 'buy', v: 0 };
  function mx() { return st.dir === 'buy' ? Math.floor(b.gold / 50) * 50 : Math.floor(b.food / 6 / 50) * 50; }
  function pv() { return st.dir === 'buy' ? '금 -' + fmt(st.v) + ' → 병량 <b>+' + fmt(st.v * 4) + '</b>' : '병량 -' + fmt(st.v * 6) + ' → 금 <b>+' + fmt(st.v) + '</b>'; }
  st.v = Math.min(300, mx());
  showDialog({
    render: function () {
      return dlgHead('거래 — ' + b.n) + '<div class="dlg-b"><div class="opts"><button class="opt' + (st.dir === 'buy' ? ' on' : '') + '" type="button" data-a="dir" data-v="buy"><b>병량 구입</b><small>금 1 → 병량 4</small></button>' +
        '<button class="opt' + (st.dir === 'sell' ? ' on' : '') + '" type="button" data-a="dir" data-v="sell"><b>병량 판매</b><small>병량 6 → 금 1</small></button></div>' +
        '<div class="fld"><label><span>금 기준 수량</span><b id="trV">' + fmt(st.v) + '</b></label><input type="range" id="trR" min="0" max="' + mx() + '" step="50" value="' + st.v + '" data-i="v"></div>' +
        '<p class="note">보유: 금 ' + fmt(b.gold) + ' · 병량 ' + fmt(b.food) + '</p></div><div class="dlg-f"><div class="pv" id="trP">' + pv() + '</div><button class="btn pri" type="button" data-a="ok">거래</button></div>';
    },
    on: {
      dir: function (el) { st.dir = el.getAttribute('data-v'); st.v = Math.min(300, mx()); refreshDialog(); },
      v: function (el) { st.v = +el.value; $('trV').textContent = fmt(st.v); $('trP').innerHTML = pv(); },
      ok: function () { if (st.v <= 0) return toast('수량을 정하세요'); var r = cmdTrade(b, st.dir, st.v); if (r.ok) closeDialog(); done(r, r.ok ? (st.dir === 'buy' ? '병량 +' + fmt(r.n) + ' (금 −' + fmt(Math.floor(st.v)) + ')' : '금 +' + fmt(r.n) + ' (병량 −' + fmt(Math.floor(st.v) * 6) + ')') : '', 'coin', facAdv(G.player) || off(G.factions[G.player].lord), 'trade'); }
    }
  });
}
function flowSearch(b) {
  pickOfficers({ title: '탐색 — 담당 무장', list: idleOfficers(b), max: 1, hi: 'pol', key: function (o) { return o.pol + (o.sk === '안력' ? 50 : 0); }, auto: function (n) { return autoPick('search', b, null, 1); }, preview: function () { return '인재나 재물을 찾습니다'; },
      rt: function (o) { return advMark(searchAdvice(b, o)) + (o.sk || '—'); },
      say: function (os) { return advSay(searchAdvice(b, os[0]), '', '오늘 숨은 인재를 만날 것입니다.', '오늘은 인재를 만나지 못할 것입니다.'); } },
    function (os) {
      var a0 = searchAdvice(b, os[0]), r = cmdSearch(b, os[0].id);
      if (!r.ok) return done(r);
      var miss = advAfter(a0, r.found !== undefined), tail = miss ? '<i class="tk-adv">군사 ' + a0.adv.n + ': ' + miss + '</i>' : '';
      if (r.found !== undefined) { sfx('good'); done(r, josa(off(r.found).n, '을를') + ' 찾았습니다' + tail, '', os[0], 'found', off(r.found).n); }
      else if (r.gold) done(r, '금 ' + josa(String(r.gold), '을를') + ' 찾았습니다' + tail, 'good', os[0], 'gold');
      else done(r, '아무것도 찾지 못했습니다' + tail, 'bad', os[0], 'nothing');
    });
}
/* 설전으로 등용(v0.13): 주사위 대신 설전의 승패로 정한다. 이기면 합류, 지거나 비기면 거절(주사위로 실패한 것과 같은 뒷일) */
function flowTalkRecruit(b, o, t) {
  var S = talkRecruitNew(b, o, t), farT = t.st === 'active', r = null;
  duelOpen(S, 'a', { sub: t.n + ' 등용 · 그냥 권하면 ' + pcT(S.rp),
    onEnd: function () {
      r = cmdRecruit(b, o.id, t.id, S);
      if (!r.ok) return '<p class="bad">' + r.msg + '</p>';
      return r.joined ? '<p><b>' + josa(t.n, '이가') + (r.far ? ' ' + facName(r.from) + '군을 떠나' : '') + ' 합류했습니다</b></p>' : '<p><b>' + josa(t.n, '은는') + ' 뜻을 굽히지 않았습니다</b>' + (r.far ? ' — 충성 +' + POACH.up + ' · 다음 달에 다시 권할 수 있습니다' : ' — 다음 달에 다시 권할 수 있습니다') + '</p>';
    } },
    function () {
      if (r && r.ok && r.joined) { sfx('good'); sfx('cheer'); talk(t, sayLine(t, 'joined', G.factions[G.player].name), josa(t.n, '이가') + ' 합류했습니다!', 3000); }
      else if (r && r.ok) sfx('bad');
      refreshSheet(); afterAction();
    });
}
/* ================= 외교(v0.14) ================= */
function relBar(v) { return '<span class="relbar" title="우호 ' + v + '"><i class="' + (v >= 60 ? 'hi' : (v < 20 ? 'lo' : '')) + '" style="width:' + v + '%"></i><em style="left:' + DIP_K.rel0 + '%"></em></span>'; }
function pactChip(a, b) { var p = pactOf(a, b); return p ? '<span class="pact ' + p.t + '">' + PACT_NAME[p.t] + ' <small>' + days(p.until - G.turn) + '</small></span>' : ''; }
function facLord(f) { return off(G.factions[f].lord); }
function dipFacs() {
  var me = G.player, out = [];
  for (var i = 0; i < G.factions.length; i++) if (i !== me && G.factions[i].alive) out.push(i);
  return out.sort(function (a, b) { return (pactOn(me, b) ? 1 : 0) - (pactOn(me, a) ? 1 : 0) || relOf(me, b) - relOf(me, a) || dipPower(b) - dipPower(a); });
}
/* 외교 단추 아래의 한 줄 */
function dipSub() {
  var n = dipOffers().length, me = G.player, ps = dipFacs().filter(function (f) { return pactOn(me, f); }).length;
  return n ? '청해 온 제안 ' + n : (ps ? '협정 ' + ps : '친선 · 정전 · 동맹');
}
function termsTxt(x) {
  function sg(v) { return (v > 0 ? '+' : (v < 0 ? '−' : '')) + Math.abs(v); }
  return '우호 ' + x.rel + ' · 바탕 ' + sg(x.base) + (x.envoy ? ' · 사신 ' + sg(x.envoy) : '') + (x.pow ? ' · 힘의 비 ' + sg(x.pow) : '') + (x.busy ? ' · 저쪽이 싸우는 중 ' + sg(x.busy) : '');
}
/* 청해 온 제안에 답한다 */
function flowDipOffer(from, kind) {
  var L = facLord(from), me = G.player;
  showDialog({
    render: function () {
      var live = dipOffers().some(function (x) { return x.from === from && x.kind === kind; });
      return dlgHead(facName(from) + '군의 제안 — ' + PACT_NAME[kind]) + '<div class="dlg-b">' + sayRow(L, sayLine(L, 'dipAsk'), PACT_NAME[kind] + ' ' + days(kind === 'ally' ? DIP_K.allyTurns : DIP_K.truceTurns)) +
        '<div class="stats dipst"><div><span>우호</span><b>' + relOf(me, from) + ' <small>' + relWord(relOf(me, from)) + '</small></b></div><div><span>병력</span><b>' + fmt(dipPower(me)) + ' : ' + fmt(dipPower(from)) + '</b></div></div>' +
        '<p class="note">' + (kind === 'ally' ? '동맹' : '정전') + '을 맺으면 ' + days(kind === 'ally' ? DIP_K.allyTurns : DIP_K.truceTurns) + ' 동안 서로의 부대 · 거점 · 시설을 칠 수 없습니다. 물리치면 우호 −' + DIP_K.refuse + '. <b>이번 턴 안에</b> 답하지 않으면 없던 일이 됩니다.</p>' +
        (live ? '<div class="cmds two"><button class="cmd pri" type="button" data-a="yes"><b>받아들인다</b></button><button class="cmd" type="button" data-a="no"><b>물리친다</b></button></div>' : '<p class="note bad">이미 지나간 제안입니다</p>') + '</div>';
    },
    on: {
      yes: function () { var r = dipAnswer(from, kind, true); closeDialog(); if (!r.ok) return toast(r.msg); sfx('gong'); talk(L, sayLine(L, 'dipYes'), facName(from) + '군과 ' + (kind === 'ally' ? '동맹을 맺었습니다' : '정전했습니다') + ' — ' + days(pactLeft(me, from))); refreshSheet(); afterAction(); },
      no: function () { var r = dipAnswer(from, kind, false); closeDialog(); if (!r.ok) return toast(r.msg); sfx('ui'); toast(facName(from) + '군의 제안을 물리쳤습니다 (우호 −' + DIP_K.refuse + ')'); refreshSheet(); afterAction(); }
    }
  }, true);
}
/* v0.16: AI 가 걸어온 일기토에 답한다. 받으면 내가 수를 고르며 겨룬다(상대가 건 쪽 a, 내가 d) */
function askLive(aid, did) { return duelAsks().some(function (x) { return x.a === aid && x.d === did; }); }
function askSoon(wait) {                                           // 내 차례 첫머리: 창이 닫힌 뒤에 한 번 띄운다
  var turn = G.turn;
  setTimeout(function () {
    if (!G || G.over || UI.play || G.turn !== turn || !inGame() || UI.busy) return;
    if (MODAL) { askSoon(600); return; }
    var x = duelAsks()[0]; if (!x) return;
    flowDuelAsk(x.a, x.d);
  }, wait || 400);
}
function flowDuelAsk(aid, did) {
  if (!askLive(aid, did)) { toast('이미 지나간 신청입니다'); refreshSheet(); return; }
  var a = UMAP[aid], d = UMAP[did], la = uLeader(a), ld = uLeader(d), an = uName(a), dn = uName(d), K = DUEL_K;
  jumpTo(d.c, d.r, Math.max(cam.z, 0.8)); flashHex(a.c, a.r, '#b5332a');
  function card(u, o, mine) { return '<div class="dk' + (mine ? ' me' : '') + '">' + porTag(o, 'md') + '<div><b>' + o.n + '</b><span>무력 <em>' + o.war + '</em></span><small>지력 ' + o.int + ' · ' + UNIT_TYPES[u.type].name + ' ' + fmt(u.troops) + '명 · 기력 ' + u.morale + '</small></div></div>'; }
  showDialog({
    render: function () {
      var live = askLive(aid, did);
      return dlgHead('일기토 신청 — ' + la.n) + '<div class="dlg-b">' + sayRow(la, sayLine(la, 'duelAsk'), facName(a.f) + '군 ' + an) +
        '<div class="dks">' + card(a, la, false) + '<span class="vs">對</span>' + card(d, ld, true) + '</div>' +
        '<ul class="plain"><li><b>이기면</b> 상대 부대 기력 -' + K.morLose + ' · 병력 -' + Math.round(K.loss * 100) + '% (쓰러뜨리면 기력 -' + K.koMor + ' · 병력 -' + Math.round(K.koLoss * 100) + '% · 혼란), 우리 부대 기력 +' + K.morWin + '</li>' +
        '<li><b>지면</b> 그 반대입니다. 비기면 두 주장의 공적만 오릅니다.</li>' +
        '<li><b>받지 않으면</b> 우리 부대 기력 -' + K.refuse + '. 답하지 않고 턴을 넘겨도 받지 않은 것이 됩니다.</li></ul>' +
        '<p class="note">피해는 두 사람의 무력 차로 정해집니다 — ' + (la.war === ld.war ? '무력이 같습니다' : (la.war > ld.war ? '상대가 ' + (la.war - ld.war) + ' 높습니다' : '우리가 ' + (ld.war - la.war) + ' 높습니다')) + '. 받으면 합마다 수를 직접 고릅니다.</p>' +
        (live ? '<div class="cmds two"><button class="cmd pri" type="button" data-a="yes"><b>받아들인다</b><small>직접 겨룹니다</small></button><button class="cmd" type="button" data-a="no"><b>받지 않는다</b><small>기력 -' + K.refuse + '</small></button></div>' : '<p class="note bad">이미 지나간 신청입니다</p>') + '</div>';
    },
    on: {
      yes: function () {
        var res = duelAskAnswer(aid, did, true); closeDialog();
        if (!res.ok) { toast(res.msg); refreshSheet(); return; }
        var S = res.duelS;
        UI.battleTurn = G.turn; playBgm('battle');
        duelOpen(S, 'd', { sub: an + ' 대 ' + dn, onEnd: function () { return duelOutHtml(S, duelFinish(S, res), an, dn); } }, function () {
          syncScene(); toast(an + duelTxt(res.duel).replace(' · ', ' — '), 3200); refreshSheet(); afterAction(); askSoon(900);
        });
      },
      no: function () {
        var r = duelAskAnswer(aid, did, false); closeDialog();
        if (!r.ok) { toast(r.msg); refreshSheet(); return; }
        sfx('ui'); talk(ld, sayLine(ld, 'duelNo'), josa(dn, '이가') + ' 일기토를 받지 않았습니다 — 기력 -' + r.mor, 3000);
        refreshSheet(); afterAction(); askSoon(900);
      }
    }
  });
}
/* v0.16: 다른 세력끼리 맺은 협정과, 동맹의 청으로 치기로 한 상대 */
function pactsOthers(f) {
  var me = G.player, out = [];
  for (var i = 0; i < G.factions.length; i++) { if (i === f || i === me || !G.factions[i].alive) continue; var p = pactOf(f, i); if (p) out.push({ f: i, t: p.t, left: p.until - G.turn }); }
  return out;
}
function pactsLine(f, brief) {
  var L = pactsOthers(f), x = dipAimOf(f), h = [];
  L.forEach(function (p) { h.push(facName(p.f) + '군과 ' + PACT_NAME[p.t] + (brief ? '' : ' ' + days(p.left))); });
  if (x >= 0) h.push('<em>' + facName(x) + '군을 치기로 함' + (brief ? '' : ' ' + days(dipAimLeft(f))) + '</em>');
  return h.length ? '<span class="ds px">' + h.join(' · ') + '</span>' : '';
}
/* v0.16: 동맹에게 — 어느 세력을 쳐 달라고 청한다 */
function aimList(t) {                                              // 동맹 t 의 이웃 세력: 청할 수 있는 것 먼저
  var me = G.player, N = dipNbrs(), out = [];
  for (var i = 0; i < G.factions.length; i++) if (i !== me && i !== t && G.factions[i].alive && dipNear(t, i, N)) out.push({ f: i, why: aimCan(me, t, i) });
  return out.sort(function (a, b) { return (a.why ? 1 : 0) - (b.why ? 1 : 0) || dipPower(a.f) - dipPower(b.f); });
}
function aimSub(b, t) {
  var me = G.player, p = pactOf(me, t);
  if (!p || p.t !== 'ally') return '동맹을 맺은 세력에게만';
  if (dipAimOf(t) >= 0) return facName(dipAimOf(t)) + '군을 치기로 함 · ' + days(dipAimLeft(t)) + ' 남음';
  var L = aimList(t), ok = L.filter(function (x) { return !x.why; });
  if (!ok.length) return L.length ? L[0].why.replace(' 청할 수 있습니다', '') : '이웃한 다른 세력이 없습니다';
  if (!idleOfficers(b).length) return '쉬는 무장이 없습니다';
  return '이웃 ' + ok.length + '세력 가운데 칠 상대를 고릅니다 · 행 ' + AP.treaty;
}
function aimOff(b, t) { var me = G.player, p = pactOf(me, t); return !p || p.t !== 'ally' || dipAimOf(t) >= 0 || !idleOfficers(b).length || !aimList(t).some(function (x) { return !x.why; }); }
function aimTermsTxt(q) {
  function sg(v) { return (v > 0 ? '+' : (v < 0 ? '−' : '')) + Math.abs(v); }
  return '우호 ' + q.rel + ' · 바탕 ' + sg(q.base) + (q.envoy ? ' · 사신 ' + sg(q.envoy) : '') + (q.pow ? ' · 힘의 비 ' + sg(q.pow) : '') + (q.war ? ' · 이미 싸우는 사이 ' + sg(q.war) : '');
}
function flowAim(b, t) {
  var me = G.player, L = facLord(t);
  function best(x) { var os = idleOfficers(b), bp = -1, bo = null; os.forEach(function (o) { var p = aimTerms(me, t, x, o).p; if (p > bp) { bp = p; bo = o; } }); return { o: bo, p: Math.max(0, bp) }; }
  showDialog({
    render: function () {
      var rows = aimList(t), h = dlgHead(facName(t) + '군에 출병 요청') + '<div class="dlg-b"><p class="note">동맹 ' + facName(t) + '군이 받아들이면 <b>' + days(DIP_K.aimTurns) + '</b> 동안 그 세력을 먼저 노립니다(' + facName(t) + '군의 거점과 이웃한 세력만). 우리 성에 원군이 들어오는 것은 아닙니다.</p><div class="rows dipl">';
      if (!rows.length) h += '<p class="note bad">' + facName(t) + '군과 이웃한 다른 세력이 없습니다</p>';
      rows.forEach(function (x) {
        h += '<button class="row' + (x.why ? ' off' : '') + '" type="button" data-a="x" data-v="' + x.f + '">' + porTag(facLord(x.f), 'sm') + '<span class="mid"><span class="nm">' + facChip(x.f) + pactChip(me, x.f) + '</span><span class="ds">' +
          (x.why ? x.why : '받아들일 확률 ' + pcBest(best(x.f).p) + ' · 병력 ' + fmt(dipPower(t)) + ' : ' + fmt(dipPower(x.f))) + '</span></span></button>';
      });
      return h + '</div><p class="note">받아들일 확률 = 우호 + 바탕 ' + DIP_K.aimBase + ' + 사신의 매력 + 힘의 비 + 이미 싸우는 사이면 ' + DIP_K.aimWar + '. 거절당하면 우호 −' + DIP_K.aimRefuse + ', ' + days(DIP_K.aimCool) + ' 뒤에 다시 청할 수 있습니다.</p></div>';
    },
    on: {
      x: function (el) {
        var x = +el.getAttribute('data-v'), why = aimCan(me, t, x); if (why) return toast(why);
        if (!idleOfficers(b).length) return toast('쉬는 무장이 없습니다');
        pickOfficers({ push: true, title: facName(t) + '군에 출병 요청(' + facName(x) + '군) — 누구를 보낼까요', list: idleOfficers(b), max: 1, hi: 'cha', key: function (o) { return aimTerms(me, t, x, o).p * 100 + o.cha; },
          rt: function (o) { return '<b>' + pcT(aimTerms(me, t, x, o).p) + '</b>'; }, rtHead: '받아들일 확률', auto: function () { var e = best(x).o; return e ? [e.id] : []; },
          preview: function (os) { var q = aimTerms(me, t, x, os[0]); return '받아들일 확률 <b>' + pcG(q.p) + '</b> · 행동력 ' + AP.treaty + '<br><small>' + aimTermsTxt(q) + '</small>'; } },
          function (os) {
            var r = cmdAim(b, os[0].id, t, x);
            if (!r.ok) { toast(r.msg); return false; }
            if (r.success) { sfx('gong'); sfx('good'); talk(L, sayLine(L, 'aimYes'), facName(t) + '군이 ' + days(DIP_K.aimTurns) + ' 동안 ' + facName(x) + '군을 먼저 치기로 했습니다 (사신 ' + os[0].n + ')', 4200); }
            else { sfx('bad'); talk(L, sayLine(L, 'aimNo'), facName(t) + '군이 출병 요청을 물리쳤습니다 — 우호 −' + DIP_K.aimRefuse + ' · ' + days(DIP_K.aimCool) + ' 뒤에 다시 (' + pcWas(r.p, '받아들일 확률') + ')', 4200); }
            refreshSheet(); afterAction(); requestDraw();
            return true;
          });
      }
    }
  }, true);
}
/* 외교 창: 세력 표 */
function flowDip(b) {
  var me = G.player;
  showDialog({
    render: function () {
      var fs = dipFacs(), ofs = dipOffers(), h = dlgHead('외교 — ' + b.n) + '<div class="dlg-b"><p class="note">금 ' + fmt(b.gold) + ' · 행동력 ' + G.factions[me].ap + ' · 사신은 ' + b.n + '의 쉬는 무장(' + idleOfficers(b).length + '명)</p>';
      if (ofs.length) {
        h += '<div class="sec">청해 온 제안 <em class="cnt">' + ofs.length + '</em></div><div class="rows">';
        ofs.forEach(function (x) { h += '<button class="row offer" type="button" data-a="offer" data-v="' + x.from + '" data-k="' + x.kind + '">' + porTag(facLord(x.from), 'sm') + '<span class="mid"><span class="nm">' + facChip(x.from) + ' ' + PACT_NAME[x.kind] + '을 청해 왔습니다</span><span class="ds">이번 턴 안에 답해야 합니다</span></span><span class="rt hi">답하기</span></button>'; });
        h += '</div>';
      }
      h += '<div class="sec">세력 <em class="cnt">' + fs.length + '</em></div><div class="rows dipl">';
      fs.forEach(function (f) {
        var v = relOf(me, f);
        h += '<button class="row" type="button" data-a="f" data-v="' + f + '">' + porTag(facLord(f), 'sm') + '<span class="mid"><span class="nm">' + facChip(f) + pactChip(me, f) + '</span><span class="ds">' + relBar(v) + '<b>' + v + '</b> ' + relWord(v) + ' · 도시 ' + facCities(f).length + ' · 병력 ' + fmt(dipPower(f)) + '</span>' + pactsLine(f, true) + '</span></button>';
      });
      return h + '</div><p class="note">우호는 처음 ' + DIP_K.rel0 + '. 친선으로 올리고, 치면 내려가며, 달마다 ' + DIP_K.rel0 + ' 쪽으로 ' + DIP_K.drift + '씩 돌아갑니다(협정 중에는 그대로).</p></div>';
    },
    on: {
      f: function (el) { flowDipFac(b, +el.getAttribute('data-v')); },
      offer: function (el) { flowDipOffer(+el.getAttribute('data-v'), el.getAttribute('data-k')); }
    }
  });
}
/* 세력 하나와의 외교 */
function flowDipFac(b, t) {
  var me = G.player, L = facLord(t);
  function bestEnvoy(kind) { var os = idleOfficers(b), best = null, bp = -1; os.forEach(function (o) { var p = dipChance(me, t, kind, o); if (p > bp) { bp = p; best = o; } }); return { o: best, p: Math.max(0, bp) }; }
  function askSub(kind) {
    if (kind === 'ally' && !pactOf(me, t) && relOf(me, t) < DIP_K.allyRel || (kind === 'ally' && pactOf(me, t) && pactOf(me, t).t !== 'ally' && relOf(me, t) < DIP_K.allyRel)) return '우호 ' + DIP_K.allyRel + ' 이상 필요';      // 단추에는 짧게
    var why = dipCan(me, t, kind); if (why) return why.replace(' 청할 수 있습니다', '');
    if (!idleOfficers(b).length) return '쉬는 무장이 없습니다';
    return '받아들일 확률 ' + (UI.pct ? '최고 ' : '') + '<em class="pc">' + pcT(bestEnvoy(kind).p) + '</em> · 행 ' + AP.treaty;
  }
  function ask(kind) {
    var why = dipCan(me, t, kind); if (why) return toast(why);
    pickOfficers({ push: true, title: facName(t) + '군에 ' + PACT_NAME[kind] + ' 제안 — 누구를 보낼까요', list: idleOfficers(b), max: 1, hi: kind === 'ally' ? 'cha' : 'pol', key: function (o) { return dipChance(me, t, kind, o) * 100 + (kind === 'ally' ? o.cha : o.pol); },
      rt: function (o) { return '<b>' + pcT(dipChance(me, t, kind, o)) + '</b>'; }, rtHead: '받아들일 확률', auto: function () { var e = bestEnvoy(kind).o; return e ? [e.id] : []; },
      preview: function (os) { var x = dipTerms(me, t, kind, os[0]); return '받아들일 확률 <b>' + pcG(x.p) + '</b> · ' + PACT_NAME[kind] + ' ' + days(kind === 'ally' ? DIP_K.allyTurns : DIP_K.truceTurns) + '<br><small>' + termsTxt(x) + '</small>'; },
      alt: { label: '설전',
        can: function (os) { return dipTalkOk(b, os[0], t, kind) && G.factions[me].ap >= AP.treaty; },
        why: function (os) { var p0 = dipChance(me, t, kind, os[0]); return G.factions[me].ap < AP.treaty ? '행동력이 부족합니다' : (p0 >= 100 ? '설전이 필요 없습니다' : '말이 통할 형편이 아닙니다 — 받아들일 확률이 ' + DIP_K.talkMin + '% 이상일 때만 설전을 걸 수 있습니다'); },
        go: function (os) { flowDipTalk(b, os[0], t, kind); } } },
      function (os) {
        var r = cmdTreaty(b, os[0].id, t, kind);
        if (!r.ok) { toast(r.msg); return false; }
        dipTold(r, t, kind);
        return true;
      });
  }
  showDialog({
    render: function () {
      var v = relOf(me, t), p = pactOf(me, t), idle = idleOfficers(b), giftAdd = idle.length ? DIP_K.giftBase + Math.round(idle.slice().sort(function (x, y) { return y.pol - x.pol; })[0].pol / DIP_K.giftPol) : 0;
      var gifted = dipOf().gift[me + ':' + t] === G.turn;
      var giftSub = gifted ? '이번 턴에는 이미 보냈습니다' : (v >= 100 ? '우호가 가장 높습니다' : (!idle.length ? '쉬는 무장이 없습니다' : (b.gold < DIP_K.giftGold ? '금 부족' : '금 ' + fmt(DIP_K.giftGold) + ' · 행 ' + AP.gift + ' · 우호 +' + giftAdd + ' 안팎')));
      function cmd(a, name, sub, pri, offc) { return '<button class="cmd' + (pri ? ' pri' : '') + (offc ? ' off' : '') + '" type="button" data-a="' + a + '"><b>' + name + '</b><small>' + sub + '</small></button>'; }
      return dlgHead(facName(t) + '군과의 외교') + '<div class="dlg-b"><div class="diph">' + porTag(L, 'md') + '<div><div class="nm">' + facChip(t) + ' <b>' + L.n + '</b>' + pactChip(me, t) + '</div><div class="rl">' + relBar(v) + '<b>' + v + '</b> ' + relWord(v) + '</div>' +
        '<div class="pw">병력 ' + fmt(dipPower(me)) + ' : ' + fmt(dipPower(t)) + ' · 도시 ' + facCities(me).length + ' : ' + facCities(t).length + (dipBusy(t, me) ? ' · <em>다른 세력과 싸우는 중</em>' : '') + '</div>' + pactsLine(t) + '</div></div>' +
        '<div class="cmds">' + cmd('gift', '친선', giftSub, false, gifted || v >= 100 || !idle.length || b.gold < DIP_K.giftGold) +
        cmd('truce', '정전 제안', askSub('truce'), !p, !!dipCan(me, t, 'truce') || !idle.length) + cmd('ally', '동맹 제안', askSub('ally'), false, !!dipCan(me, t, 'ally') || !idle.length) +
        cmd('aim', '출병 요청', aimSub(b, t), false, aimOff(b, t)) +
        (p ? cmd('brk', PACT_NAME[p.t] + ' 파기', '우호 −' + DIP_K.breakRel + ' · 다른 세력 −' + DIP_K.breakOthers, false, false) : '') + '</div>' +
        '<p class="note">' + (p ? '<b>' + PACT_NAME[p.t] + ' 중</b> — ' + days(p.until - G.turn) + ' 남았습니다. 그동안 서로의 부대 · 거점 · 시설을 칠 수 없습니다.' : '정전 ' + days(DIP_K.truceTurns) + ' · 동맹 ' + days(DIP_K.allyTurns) + '(우호 ' + DIP_K.allyRel + ' 이상). 맺으면 서로의 부대 · 거점 · 시설을 칠 수 없습니다. 거절당하면 우호 −' + DIP_K.refuse + ', ' + days(DIP_K.cool) + ' 뒤에 다시 청할 수 있습니다.') + '</p></div>';
    },
    on: {
      gift: function () {
        var r0 = cmdGiftCheck(b, t); if (r0) return toast(r0);
        pickOfficers({ push: true, title: facName(t) + '군에 선물 — 누구를 보낼까요', list: idleOfficers(b), max: 1, hi: 'pol', key: function (o) { return o.pol; },
          rt: function (o) { return '우호 <b>+' + (DIP_K.giftBase + Math.round(o.pol / DIP_K.giftPol)) + '</b>'; }, rtHead: '효과', auto: function () { var L2 = idleOfficers(b).slice().sort(function (x, y) { return y.pol - x.pol; }); return L2.length ? [L2[0].id] : []; },
          preview: function (os) { return '금 ' + fmt(DIP_K.giftGold) + ' · 행동력 ' + AP.gift + ' → 우호 <b>+' + (DIP_K.giftBase + Math.round(os[0].pol / DIP_K.giftPol)) + '</b> <small>(' + DIP_K.giftBase + ' + 정치 ÷ ' + DIP_K.giftPol + ')</small>'; } },
          function (os) {
            var v0 = relOf(me, t), r = cmdGift(b, os[0].id, t);
            if (!r.ok) { toast(r.msg); return false; }
            sfx('coin'); talk(L, sayLine(L, 'dipGift'), josa(os[0].n, '이가') + ' ' + facName(t) + '군에 선물을 전했습니다 — 우호 ' + v0 + ' → ' + r.rel);
            refreshSheet(); afterAction(); return true;
          });
      },
      truce: function () { ask('truce'); },
      aim: function () { var p0 = pactOf(me, t); if (!p0 || p0.t !== 'ally') return toast('동맹을 맺은 세력에게만 청할 수 있습니다'); if (dipAimOf(t) >= 0) return toast('이미 ' + facName(dipAimOf(t)) + '군을 치기로 했습니다 (' + days(dipAimLeft(t)) + ' 남음)'); flowAim(b, t); },
      ally: function () { ask('ally'); },
      brk: function () {
        var p = pactOf(me, t); if (!p) return;
        showDialog({
          render: function () { return dlgHead(PACT_NAME[p.t] + ' 파기 — ' + facName(t) + '군') + '<div class="dlg-b"><p>' + facName(t) + '군과의 ' + PACT_NAME[p.t] + '(' + days(p.until - G.turn) + ' 남음)을 깹니다.</p><ul class="plain"><li>' + facName(t) + '군과의 우호 <b class="bad">−' + DIP_K.breakRel + '</b></li><li>다른 모든 세력과의 우호 <b class="bad">−' + DIP_K.breakOthers + '</b></li><li>' + days(DIP_K.breakCool) + ' 동안 ' + facName(t) + '군에 다시 청하지 못합니다</li><li>깨는 그 순간부터 서로 칠 수 있습니다</li></ul><div class="cmds two"><button class="cmd" type="button" data-a="go"><b>깬다</b></button><button class="cmd pri" type="button" data-a="back"><b>그만둔다</b></button></div></div>'; },
          on: { go: function () { var r = cmdBreak(me, t); backDialog(); if (!r.ok) return toast(r.msg); sfx('fail'); talk(L, sayLine(L, 'dipBreak'), facName(t) + '군과의 ' + PACT_NAME[r.kind] + '을 깼습니다 — 우호 ' + relOf(me, t)); refreshDialog(); refreshSheet(); afterAction(); requestDraw(); },
                back: function () { backDialog(); } }
        }, true);
      }
    }
  }, true);
}
function cmdGiftCheck(b, t) {
  if (dipOf().gift[G.player + ':' + t] === G.turn) return '이번 턴에는 이미 선물을 보냈습니다';
  if (relOf(G.player, t) >= 100) return '우호가 이미 가장 높습니다';
  if (b.gold < DIP_K.giftGold) return '금이 부족합니다(금 ' + fmt(DIP_K.giftGold) + ')';
  if (!needAP(G.player, AP.gift)) return '행동력이 부족합니다';
  return '';
}
/* 제안의 결과를 알린다(저쪽 군주의 한마디) */
function dipTold(r, t, kind) {
  var L = facLord(t), me = G.player, o = off(r.o);
  if (r.success) { sfx('gong'); sfx('good'); sfx('cheerlate'); talk(L, sayLine(L, 'dipYes'), facName(t) + '군과 ' + (kind === 'ally' ? '동맹을 맺었습니다' : '정전했습니다') + ' — ' + days(pactLeft(me, t)) + ' (사신 ' + o.n + ')', 4200); }
  else { sfx('bad'); talk(L, sayLine(L, 'dipNo'), facName(t) + '군이 ' + PACT_NAME[kind] + ' 제안을 물리쳤습니다 — 우호 −' + DIP_K.refuse + ' · ' + days(DIP_K.cool) + ' 뒤에 다시', 4200); }
  refreshSheet(); afterAction(); requestDraw();
}
/* 설전으로 담판 */
function flowDipTalk(b, o, t, kind) {
  var S = dipTalkNew(b, o, t, kind), r = null;
  duelOpen(S, 'a', { sub: facName(t) + '군과 ' + PACT_NAME[kind] + ' 담판 · 그냥 청하면 ' + pcT(S.dp),
    onEnd: function () {
      r = cmdTreaty(b, o.id, t, kind, S);
      if (!r.ok) return '<p class="bad">' + r.msg + '</p>';
      return r.success ? '<p><b>' + facName(t) + '군과 ' + (kind === 'ally' ? '동맹을 맺었습니다' : '정전했습니다') + '</b> — ' + days(pactLeft(G.player, t)) + '</p>' : '<p><b>' + facName(t) + '군은 뜻을 굽히지 않았습니다</b> — 우호 −' + DIP_K.refuse + ' · ' + days(DIP_K.cool) + ' 뒤에 다시 청할 수 있습니다</p>';
    } },
    function () { if (r && r.ok && r.success) { sfx('good'); sfx('cheer'); } else if (r && r.ok) sfx('bad'); if (MODAL) refreshDialog(); refreshSheet(); afterAction(); requestDraw(); });
}
function flowRecruit(b) {
  var here = freeOfficers(b).concat(baseCaptives(b).filter(function (o) { return o.capF === b.owner; })), far = poachTargets(b);
  if (!here.length && !far.length) return toast('등용할 대상이 없습니다');
  function bestP(t) { return bestRecruiter(b, t).p; }
  function bestM(t) { return advMark(bestRecruiter(b, t).adv); }
  function tieSub(t, org) {                                    // 줄 오른쪽의 작은 글: 가장 잘 권할 무장과 대상의 사이(있으면), 없으면 출신
    var x = bestRecruiter(b, t), tie = x.o ? tieOf(x.o, t, b.owner) : null, og = org ? originTxt(t) : '';
    return tie ? '<br><small class="tie">' + x.o.n + ' · ' + tie.short + '</small>' : (og ? '<br><small>' + og + '</small>' : '');
  }
  function why(t) {                                            // 권할 수 없는 까닭(없으면 '')
    if (askWait(t)) return '다음 달에 다시';
    if (t.st === 'active' && bondOf(t)) return '주군과 ' + bondOf(t);
    if (t.st === 'active' && t.loy >= 100) return '충성 100';
    if (t.st === 'active' && t.loy >= POACH.wall && !bondWith(t, b.owner) && !idleOfficers(b).some(function (o) { var ti = tieOf(o, t, b.owner); return ti && ti.k === 'bond'; })) return '충성 ' + POACH.wall + ' 이상';
    return '';
  }
  var srt = 'p';                                               // v0.20 정렬: p 가능성 · sum 능력 합 · ldr/war/int/pol/cha · a0~a4 적성(창 극 노 기 병기)
  var SRT = [['p', '가능성'], ['sum', '능력'], ['ldr', '통솔'], ['war', '무력'], ['int', '지력'], ['pol', '정치'], ['cha', '매력'], ['a0', '창'], ['a1', '극'], ['a2', '노'], ['a3', '기'], ['a4', '병기']];
  function sval(t) {
    if (srt === 'sum') return t.ldr + t.war + t.int + t.pol + t.cha;
    if (srt.charAt(0) === 'a') return APT_RANK[t.apt.charAt(+srt.charAt(1))] * 1000 + t.ldr + t.war;
    return t[srt];
  }
  function sopt() { return srt === 'p' || srt === 'sum' ? {} : (srt.charAt(0) === 'a' ? { apt: +srt.charAt(1) } : { hi: srt }); }
  function mixo(a, x) { for (var k in x) a[k] = x[k]; return a; }
  showDialog({
    render: function () {
      var idle = idleOfficers(b).length, i, t, w, h = dlgHead('등용 — 누구를 부를까요') + '<div class="dlg-b">';
      h += '<div class="srt" role="group" aria-label="정렬"><i>정렬</i>'; for (i = 0; i < SRT.length; i++) h += '<button type="button" data-a="srt" data-v="' + SRT[i][0] + '"' + (srt === SRT[i][0] ? ' class="on"' : '') + (i === 7 ? ' data-g="1"' : '') + '>' + SRT[i][1] + '</button>'; h += '</div>';
      if (!idle) h += '<p class="note">쉬는 무장이 없어 지금은 권할 수 없습니다</p>';
      if (here.length) {
        var HL = here.slice(); if (srt !== 'p') HL.sort(function (x, y) { return sval(y) - sval(x); });
        h += '<div class="sec">이 거점의 재야·포로</div><div class="rows">';
        for (i = 0; i < HL.length; i++) { t = HL[i]; w = why(t); h += offRow(t, mixo({ a: 't', dim: !!w, badge: t.st === 'captive' ? '포로' : '재야', rt: (w ? '<span class="bad">' + w + '</span>' : (idle ? bestM(t) + pcBest(bestP(t)) : '')) + (w || !idle ? (originTxt(t) ? '<br><small>' + originTxt(t) + '</small>' : '') : tieSub(t, true)) }, sopt())); }
        h += '</div><p class="note">한 사람에게 <b>한 달에 한 번</b> 권할 수 있습니다</p>';
      }
      if (far.length) {
        var L = far.map(function (x) { return { t: x, p: bestP(x), w: why(x) }; }).sort(function (x, y) { return srt === 'p' ? ((x.w ? 1 : 0) - (y.w ? 1 : 0) || y.p - x.p || x.t.loy - y.t.loy) : (sval(y.t) - sval(x.t) || y.p - x.p); });
        h += '<div class="sec">이웃 거점의 다른 세력 무장</div><div class="rows">';
        for (i = 0; i < L.length; i++) { t = L[i].t; w = L[i].w; h += offRow(t, mixo({ a: 't', dim: !!w || !L[i].p, badge: facName(t.f) + '·' + G.bases[t.loc].n, rt: '충성 <b>' + t.loy + '</b><br>' + (w ? '<span class="bad">' + w + '</span>' : (idle ? (L[i].p ? bestM(t) : '') + pcBest(L[i].p) + (L[i].p ? tieSub(t, false) : '') : '')) }, sopt())); }
        h += '</div><p class="note">한 무장에게 <b>한 달에 한 번</b> · 거절하면 충성 +' + POACH.up + '</p>';
      }
      return h + '</div>';
    },
    on: { srt: function (el) { srt = el.getAttribute('data-v'); refreshDialog(); var bd = document.querySelector('#modal .dlg-b'); if (bd) bd.scrollTop = 0; }, t: function (el) {
      var t = off(+el.getAttribute('data-v')), w = why(t), farT = t.st === 'active';
      if (w) return toast(t.n + ' — ' + w + (farT && !askWait(t) ? '이라 응하지 않습니다' : ''));
      if (farT && !canPoach(b, t)) return toast('지금은 권할 수 없습니다 — 자리를 옮겼습니다');
      pickOfficers({ push: true, title: t.n + ' 등용 — 누구를 보낼까요', list: idleOfficers(b), max: 1, hi: 'cha', key: function (o) { return recruitChance(b, o, t); },
        rt: function (o) { var x = recruitTerms(b, o, t); return advMark(recruitAdvice(b, o, t)) + '<b>' + pcT(x.p) + '</b>' + (x.tie ? '<small class="tie">' + x.tie.short + '</small>' : ''); }, rtHead: '성공률', auto: function () { return autoPick('recruit', b, { target: t }, 1); },
        preview: function (os) { var x = recruitTerms(b, os[0], t); return '성공률 <b>' + pcG(x.p) + '</b>' + (farT ? ' · 충성 ' + t.loy : '') + (x.no ? ' · <span class="bad">' + x.no + '</span>' : '') + (x.why.length ? '<br><small>' + whyTxt(x) + '</small>' : ''); },
        say: function (os) { return advSay(recruitAdvice(b, os[0], t), josa(t.n, '은는'), '응할 것입니다.', '응하지 않을 것입니다.'); },
        alt: { label: '설전',
          can: function (os) { return talkRecruitOk(b, os[0], t) && G.factions[b.owner].ap >= AP.recruit; },
          why: function (os) { var p0 = recruitChance(b, os[0], t); return G.factions[b.owner].ap < AP.recruit ? '행동력이 부족합니다' : (p0 >= 100 ? '설전이 필요 없습니다 — 그냥 권하면 응합니다' : '말이 통할 상대가 아닙니다 — 등용 확률이 ' + DUEL_K.talkMin + '% 이상일 때만 설전을 걸 수 있습니다'); },
          go: function (os) { flowTalkRecruit(b, os[0], t); } } },
        function (os) {
          var a0 = recruitAdvice(b, os[0], t), r = cmdRecruit(b, os[0].id, t.id); if (r.ok && r.joined) { sfx('good'); sfx('cheer'); } else if (r.ok) sfx('bad');
          var miss = r.ok ? advAfter(a0, !!r.joined) : '';
          var ok = done(r, r.ok ? (r.joined ? (r.far ? josa(t.n, '이가') + ' ' + facName(r.from) + '군을 떠나 합류했습니다!' : josa(t.n, '이가') + ' 합류했습니다!') : josa(t.n, '이가') + ' 거절했습니다' + (r.far ? ' (충성 +' + POACH.up + ')' : '')) + (miss ? '<i class="tk-adv">군사 ' + a0.adv.n + ': ' + miss + '</i>' : '') : '', '', t, r.joined ? 'joined' : 'refused', G.factions[G.player].name);
          if (ok) { here = freeOfficers(b).concat(baseCaptives(b).filter(function (o) { return o.capF === b.owner; })); far = poachTargets(b); }
          return ok;
        });
    } }
  });
}
function flowReward(b) {
  showDialog({
    render: function () {
      var os = baseOfficers(b).filter(function (o) { return !isLord(o); }).sort(function (x, y) { return x.loy - y.loy; });
      var h = dlgHead('포상 — 금 ' + COST.reward + ' · 행동력 ' + AP.reward) + '<div class="dlg-b"><p class="note">보유 금 ' + fmt(b.gold) + ' · 행동력 ' + G.factions[b.owner].ap + '</p><div class="rows">';
      for (var i = 0; i < os.length; i++) h += offRow(os[i], { a: 'r', dim: os[i].loy >= 100, rt: '<span class="' + (os[i].loy < 70 ? 'bad' : '') + '">충성 <b>' + os[i].loy + '</b></span>' });
      if (!os.length) h += '<p class="note">포상할 무장이 없습니다.</p>';
      return h + '</div></div>';
    },
    on: { r: function (el) { var ro = off(+el.getAttribute('data-v')), r = cmdReward(b, ro.id); if (!r.ok) return toast(r.msg); sfx('coin'); talk(ro, sayLine(ro, 'reward'), '충성 +' + r.n + ' (' + ro.loy + ')'); refreshDialog(); refreshSheet(); refreshHud(); } }
  });
}
function flowMove(b) {
  var dests = facBases(b.owner).filter(function (x) { return x.id !== b.id; });
  if (!dests.length) return toast('옮겨 갈 다른 거점이 없습니다');
  pickOfficers({ keep: true, title: '이동 — 보낼 무장', list: idleOfficers(b), max: 99, all: true, key: function (o) { return o.ldr + o.war + o.int + o.pol; }, ok: '다음', preview: function (os) { return os.length + '명 선택'; } },
    function (os) {
      dests.sort(function (x, y) { return hdist(b.c, b.r, x.c, x.r) - hdist(b.c, b.r, y.c, y.r); });
      var mv = { sel: -1 };
      function go(id) { var r = cmdMoveOfficers(b, ids(os), id); if (r.ok) closeDialog(); done(r, r.ok ? os.length + '명 출발 — ' + euro(G.bases[id].n) + ' ' + days(r.turns) + ' 뒤 도착' : '', '', os[0], 'move'); }
      function marks() {                                         // v0.20: 지도에 우리 성마다 이름과 걸리는 날수
        var list = [{ c: b.c, r: b.r, cls: 'ex src', html: '<b>' + b.n + '</b><small>여기서</small>', dy: -30 }];
        dests.forEach(function (x) { list.push({ c: x.c, r: x.r, cls: 'ex' + (x.id === mv.sel ? ' on' : ''), html: '<b>' + x.n + '</b><small>' + days(travelTurns(b, x)) + '</small>', dy: -30 }); });
        marksSet(list); requestDraw();
      }
      var D = {
        see: true,
        pick: {
          list: function () { return dests.map(function (x) { return { c: x.c, r: x.r, on: x.id === mv.sel }; }); },
          has: function (c, r) { return dests.some(function (x) { return x.c === c && x.r === r; }); },
          show: marks,
          tap: function (c, r) {
            var bb = baseAt(c, r);
            if (!bb || dests.indexOf(bb) < 0) return toast(bb && bb.id === b.id ? '보내는 성입니다 — 다른 우리 성을 누르세요' : '우리 성을 누르세요(이름이 뜬 곳)', 1700);
            mv.sel = bb.id; sfx('ui'); refreshDialog(); marks();
            var row = document.querySelector('#modal .row.sel'); if (row && row.scrollIntoView) row.scrollIntoView({ block: 'nearest' });
          }
        },
        render: function () {
          var h = dlgHead('이동 — 어디로 보낼까요') + '<div class="dlg-b"><p class="note">지도에서 <b>우리 성</b>을 누르거나 아래에서 고르세요 · ' + os.length + '명</p><div class="rows">';
          for (var i = 0; i < dests.length; i++) h += '<button class="row' + (dests[i].id === mv.sel ? ' sel' : '') + '" type="button" data-a="d" data-v="' + dests[i].id + '"><span class="mid"><span class="nm">' + dests[i].n + '</span><span class="ds">' + SIZE_NAME[dests[i].sz] + ' · 무장 ' + baseOfficers(dests[i]).length + '명 · 병력 ' + fmt(dests[i].troops) + '</span></span><span class="rt"><b>' + days(travelTurns(b, dests[i])) + '</b></span></button>';
          h += '</div></div>';
          if (mv.sel >= 0) h += '<div class="dlg-f"><div class="pv">' + G.bases[mv.sel].n + ' — ' + days(travelTurns(b, G.bases[mv.sel])) + '</div><button class="btn pri" type="button" data-a="go">' + euro(G.bases[mv.sel].n) + ' 보낸다</button></div>';
          return h;
        },
        on: { d: function (el) { go(+el.getAttribute('data-v')); }, go: function () { if (mv.sel >= 0) go(mv.sel); } }
      };
      showDialog(D, true);
      var dl = document.querySelector('#modal .dlg'), top = $('hud') ? $('hud').getBoundingClientRect().bottom : 90, bot = dl ? dl.getBoundingClientRect().top : CH * 0.5;
      frameHexes([[b.c, b.r]].concat(dests.map(function (x) { return [x.c, x.r]; })), top + 64, bot - 34, 1.1);
    });
}
function flowCaptive(b) {
  showDialog({
    render: function () {
      var cs = baseCaptives(b), h = dlgHead('포로 ' + cs.length + '명') + '<div class="dlg-b"><p class="note">등용은 인재 → 등용에서 · <b>옛 군주를 참수하면</b> 그 신하였던 무장들이 우리의 등용에 잘 응하지 않습니다(' + TIES.grudge + ', 인연이 있던 무장은 거의 불가)</p>';
      for (var i = 0; i < cs.length; i++) h += '<div class="row cpv">' + porTag(cs[i]) + '<span class="mid"><span class="nm">' + cs[i].n + skTag(cs[i]) + (originTxt(cs[i]) ? ' <small class="org">' + originTxt(cs[i]) + '</small>' : '') + '</span><span class="ds">' + st5(cs[i]) + '</span>' + apt5(cs[i]) + '</span><button class="btn" type="button" data-a="rel" data-v="' + cs[i].id + '">해방</button><button class="btn" type="button" data-a="exe" data-v="' + cs[i].id + '">참수</button></div>';
      return h + '</div>';
    },
    on: {
      rel: function (el) { var o = off(+el.getAttribute('data-v')); var say0 = sayLine(o, 'released'); cmdCaptive(b, o.id, 'release'); talk(o, say0, josa(o.n, '을를') + ' 풀어 주었습니다'); if (!b.captives.length) closeDialog(); else refreshDialog(); refreshSheet(); },
      exe: function (el) { var o = off(+el.getAttribute('data-v')); if (el.getAttribute('data-c')) { cmdCaptive(b, o.id, 'execute'); toast(josa(o.n, '을를') + ' 참수했습니다'); if (!b.captives.length) closeDialog(); else refreshDialog(); refreshSheet(); } else { el.setAttribute('data-c', '1'); el.textContent = '정말?'; el.classList.add('pri'); } }
    }
  });
}

/* ---------- 시설 ---------- */
function flowDevelop(b, pi) {
  if (b.owner !== G.player || baseCorps(b)) return;
  var why = buildWhy(b);
  if (why) return toast('지금은 지을 수 없습니다 — ' + why);
  if (UAT[K(b.plots[pi].c, b.plots[pi].r)]) return toast('부대가 서 있는 칸에는 지을 수 없습니다');
  var dev = { b: b.id, pi: pi };                                  // 고른 자리 — 창이 떠 있는 동안 지도에서 다른 빈 부지를 누르면 바뀐다(devTap)
  showDialog({
    dev: dev, see: true,
    render: function () {
      var h = dlgHead(b.n + ' ' + lotMark(lotNo(b, dev.pi)) + ' — 무엇을 지을까요') + '<div class="dlg-b"><p class="note fnote"><span>' + plotNear(b, dev.pi) + '</span><span>보유 금 ' + fmt(b.gold) + ' · 행동력 −' + AP.develop + '</span></p><div class="lst-opt fgrid">';
      for (var i = 0; i < FAC_ORDER.length; i++) {
        var F = FAC[FAC_ORDER[i]], ok = b.gold >= F.cost, ef = lotEffect(b, dev.pi, FAC_ORDER[i]);
        h += '<button class="row fcard' + (ok ? '' : ' dim') + '" type="button" data-a="f" data-v="' + FAC_ORDER[i] + '">' + thumb(FAC_ORDER[i]) + '<span class="mid"><span class="nm">' + F.name + '<i class="cost">금 ' + F.cost + '</i></span><span class="ds' + (ef[1] ? ' ' + ef[1] : '') + '">' + ef[0] + '</span></span></button>';
      }
      return h + '</div></div>';
    },
    on: { f: function (el) {
      var t = el.getAttribute('data-v'), F = FAC[t], pi = dev.pi;
      if (b.gold < F.cost) return toast('금이 부족합니다 (' + F.cost + ' 필요)');
      pickOfficers({ push: true, title: F.name + ' 건설 ' + lotMark(lotNo(b, pi)) + ' — 담당 무장', list: idleOfficers(b), max: 3, hi: 'pol', key: function (o) { return o.pol + (o.sk === '축성' ? 60 : 0); }, auto: function (n) { return autoPick('develop', b, null, n); },
        preview: function (os) { var rate = 60 + Math.round((bestOf(os, 'pol') + sumOthers(os, 'pol') * 0.5) * 0.6); if (anyHas(os, '축성')) rate *= 2; return '완공까지 <b>' + days(Math.ceil(F.build / rate)) + '</b> · 금 ' + F.cost + '<br><span class="warn">담당 무장은 완공까지 묶입니다</span>'; } },
        function (os) { var r = cmdDevelop(b, pi, t, ids(os)); if (r.ok) { flashHex(b.plots[pi].c, b.plots[pi].r, SEAL); floatText(b.plots[pi].c, b.plots[pi].r, F.name + ' 착공', SEAL); } return done(r, r.ok ? F.name + ' 착공 — ' + days(r.turns) + ' 뒤 완공' : '', 'hammer', os[0], 'develop', F.name); });
    } }
  });
}
function flowFacility(b, pi) {
  var fc = b.plots[pi].fac; if (!fc || baseCorps(b)) return;
  var F = FAC[fc.t];
  showDialog({
    fsel: { b: b.id, pi: pi }, see: true,                          // 지도에서 이 시설이 표시된다 — 다른 시설을 누르면 그 시설로 바뀐다(fselTap)
    render: function () {
      var cands = mergeCandidates(b, pi), now = facNow(b, pi);
      var h = dlgHead(b.n + ' ' + lotMark(lotNo(b, pi)) + ' ' + F.name + facLv(fc)) + '<div class="dlg-b"><div class="card fcd">' + facThumb(fc, 'lg') + '<p><b class="fcv">' + facDesc(fc) + '</b>' + (now ? '<span class="fcn">' + now + '</span>' : '') + '</p></div>' + (fc.done ? '' : '<p class="note">건설 중 — ' + days(Math.max(1, Math.ceil((fc.need - fc.prog) / fc.rate))) + ' 남음' + (builders(fc).length ? ' · 담당 <b>' + builders(fc).map(function (o) { return o.n; }).join('·') + '</b>' : '') + '</p>') +
        '<div class="cmds">' + (facHasLv(fc.t) ? '<button class="cmd' + (cands.length ? ' pri' : ' off') + '" type="button" data-a="merge"><b>흡수합병</b><small>' + (fc.lv >= 3 ? '최고 레벨' : (cands.length ? '금 ' + COST.merge * fc.lv + ' · 행 ' + AP.merge : '인접한 같은 시설 필요')) + '</small></button>' : '') +      // v0.18: 레벨이 없는 시설에는 합병 단추가 없다
        '<button class="cmd" type="button" data-a="demo"><b>' + (fc.done ? '철거' : '공사 중단') + '</b><small>' + (!fc.done && builders(fc).length ? '담당 무장이 풀려납니다' : '부지를 비웁니다') + '</small></button></div>' +
        (facHasLv(fc.t) ? '<p class="note">흡수합병 = 옆의 같은 시설을 합쳐 레벨 +1 (최대 3)' + (cands.length ? ' — ' + mergeNote(b, pi, cands[0]) : '') + '</p>'
          : '<p class="note nolv"><b>' + josa(F.name, '은는') + ' 레벨이 없는 시설입니다</b> — ' + (fc.t === 'workshop' ? '하나만 있으면 충차를 만들 수 있습니다.' : '옆의 ' + (fc.t === 'mint' ? '시장' : '농장') + ' 한 곳에 둘까지, 하나마다 수입을 +50% 보탭니다.') + '</p>') + '</div>';
      return h;
    },
    on: {
      merge: function () {
        var cands = mergeCandidates(b, pi);
        if (!cands.length) return toast(fc.lv >= 3 ? '이미 최고 레벨입니다' : '옆에 같은 시설이 있어야 합니다');
        pickOfficers({ push: true, title: '흡수합병 — 담당 무장', list: idleOfficers(b), max: 1, hi: 'pol', key: function (o) { return -statSum(o); }, auto: function () { return autoPick('merge', b, null, 1); }, preview: function () { return F.name + ' Lv' + fc.lv + ' → <b>Lv' + (fc.lv + 1) + '</b> · 금 ' + COST.merge * fc.lv + '<br><small>' + mergeNote(b, pi, cands[0]) + '</small>'; } },
          function (os) { var r = cmdMerge(b, pi, cands[0], ids(os)); return done(r, r.ok ? F.name + ' Lv' + r.lv + '로 올랐습니다' : '', 'hammer', os[0], 'merge', F.name); });
      },
      demo: function (el) {
        if (el.getAttribute('data-c')) {
          var was = fc.done, rd = cmdDemolish(b, pi), names = (rd.freed || []).map(function (id) { return off(id).n; });
          closeDialog(); sfx('miss');
          toast(was ? F.name + ' 철거' : F.name + ' 공사 중단' + (names.length ? ' — ' + names.join('·') + (off(rd.freed[0]).acted ? ' 풀려남(이번 턴은 쉼)' : ' 풀려남') : ''));
          refreshSheet(); afterAction();
        } else { el.setAttribute('data-c', '1'); el.querySelector('b').textContent = fc.done ? '정말 철거?' : '정말 중단?'; }
      }
    }
  });
}

/* ---------- 출진·수송 ---------- */
/* 앱으로 설치해 열었을 때 휴대폰의 '뒤로' 단추: ×와 같은 규칙으로 한 단계 물러난다(tools/build.py 의 앱판 스크립트가 부른다).
   물러났으면 true, 더 물러날 곳이 없으면 false(그러면 앱이 '한 번 더 누르면 나갑니다'를 띄운다) */
function appBack() {
  if (cineSkip()) return true;                                // v0.19: 도는 영상부터 건너뛴다
  if (ocardOn()) { ocardClose(); return true; }               // v0.18: 겹쳐 뜬 무장 카드부터 닫는다
  if (!G || !$('title').classList.contains('off')) {       // 제목 화면: 떠 있는 창(군주 고르기·도움말)만 닫는다
    if (MODAL && !MODAL.lock) { backDialog(); return true; }
    return false;
  }
  if (UI.play) return true;                                 // 지난 열흘을 보여 주는 중에는 그대로 둔다
  if (MODAL) { backDialog(); return true; }                 // 끝난 판의 창(lock)은 backDialog 가 닫지 않는다
  if (UI.busy) return true;                                 // 움직이는 장면이 나오는 중
  if (SHEET && !SHEET.home) { backSheet(); return true; }
  return false;
}
function backToBase(id) { return function () { var bb = G.bases[id]; if (bb && bb.owner === G.player) selectBase(bb, false, 'mil'); else clearSel(); }; }
/* 나갈 자리(v0.12): 성 둘레 여섯 칸을 지도와 같은 방향으로 그린다. st.at = 고른 칸 [c, r] 또는 null(게임이 고른다 — 그 칸은 점선) */
function dirName(dx, dz) { var a = Math.atan2(dz, dx) * 180 / Math.PI; return Math.abs(a) < 15 ? '동' : (Math.abs(a) > 165 ? '서' : (a < 0 ? (a > -90 ? '북동' : '북서') : (a < 90 ? '남동' : '남서'))); }
function spotWhat(c, r) {
  var k = K(c, r), t = terr(c, r), pf = PAT[k], fc = pf ? G.bases[pf.b].plots[pf.i].fac : null;
  if (UAT[k]) return '부대';
  if (fc) return FAC[fc.t].name;
  if (G.fires[k]) return '불';
  return isRoad(c, r) ? (t === 'w' ? '나루' : '길') : TERRAIN_NAME[t];
}
/* v0.20 나갈 자리: 지도 위에서 고른다(전에는 창 속에 여섯 칸을 그려 골랐다). 성 둘레 여섯 칸이 빛나고(나갈 수 있는 칸은 금빛 · 고른 칸은 붉게) 칸마다 방향과 땅이 적힌다.
   st.at = 고른 칸 [c, r] 또는 null(게임이 고른다). D = 떠 있는 창 — open() 이 D.pick 을 달아 지도 누름을 받는다(onTap). */
function stepTag(n, of, label) { return ' <small class="stp">' + n + '/' + of + ' ' + label + '</small>'; }
function exitPick(b, st, D) {
  function spots() { var ok = {}; deploySpots(b).forEach(function (q) { ok[K(q[0], q[1])] = 1; }); return ok; }
  function cur() { var ok = spots(); if (st.at && !ok[K(st.at[0], st.at[1])]) st.at = null; return st.at || deploySpot(b); }      // 고른 칸이 막혔으면(다른 부대가 섰으면) 자동으로 되돌린다
  function marks() {
    var ok = spots(), ns = nbrs(b.c, b.r), p0 = hexCenter(b.c, b.r), at = cur(), list = [];
    for (var i = 0; i < ns.length; i++) {
      var c = ns[i][0], r = ns[i][1], p = hexCenter(c, r), on = !!(at && at[0] === c && at[1] === r), good = !!ok[K(c, r)];
      list.push({ c: c, r: r, cls: 'ex' + (on ? ' on' : '') + (good ? '' : ' no'), html: '<b>' + dirName(p[0] - p0[0], p[1] - p0[1]) + '</b><small>' + spotWhat(c, r) + '</small>' });
    }
    marksSet(list); requestDraw();
  }
  var P = {
    list: function () { var ok = spots(), at = cur(), out = []; for (var k in ok) { var c = +k % W, r = (+k - c) / W; out.push({ c: c, r: r, on: !!(at && at[0] === c && at[1] === r) }); } return out; },
    has: function (c, r) { return hdist(c, r, b.c, b.r) === 1; },
    show: marks,
    tap: function (c, r) {
      if (c === b.c && r === b.r) return;
      if (hdist(c, r, b.c, b.r) !== 1) return toast('성 둘레의 빛나는 칸을 누르세요', 1600);
      if (!spots()[K(c, r)]) return toast('그 칸으로는 나갈 수 없습니다 — ' + spotWhat(c, r));
      st.at = [c, r]; sfx('ui'); refreshDialog(); marks();
    }
  };
  return {
    open: function () {
      D.see = true; D.pick = P; if (typeof talkHide === 'function') talkHide(); paintDialog(0);
      var dl = document.querySelector('#modal .dlg'), top = $('hud') ? $('hud').getBoundingClientRect().bottom : 90, bot = dl ? dl.getBoundingClientRect().top : CH * 0.5;
      frameHexes([[b.c, b.r]].concat(nbrs(b.c, b.r)), top + 30, bot - 12, 2.1);
    },
    close: function () { D.see = false; D.pick = null; },
    line: function () {
      var at = cur(), p0 = hexCenter(b.c, b.r), p = at ? hexCenter(at[0], at[1]) : null;
      return '<div class="sec">나갈 자리 <small>지도에서 빛나는 칸을 누르세요</small>' + (st.at ? '<button class="btn auto" type="button" data-a="atauto">자동</button>' : '') + '</div>' +
        '<p class="dpat-t wide" id="dpAt">' + (at ? '<b>' + dirName(p[0] - p0[0], p[1] - p0[1]) + '쪽</b> ' + spotWhat(at[0], at[1]) + ' <small>' + (st.at ? '고른 자리' : '자동 — 길이 난 쪽부터') + '</small>' : '<b class="bad">나갈 자리가 없습니다</b>') + '</p>';
    },
    auto: function () { st.at = null; refreshDialog(); marks(); }
  };
}
function flowDeploy(b) {
  var list = idleOfficers(b).sort(function (x, y) { return aiMilScore(y) - aiMilScore(x); });
  if (!list.length) return toast('행동할 수 있는 무장이 없습니다');
  if (b.troops < 100) return toast('주둔 병력이 없습니다');
  var st = { step: 1, type: 'sword', ids: [], troops: 0, turns: DEPLOY_FOOD[1], auto: true, at: null }, D, EX;
  function stock(t) { var wp = UNIT_TYPES[t].weapon; return wp === 'ram' ? b.w.ram : (wp ? b.w[wp] : 1e9); }
  function usable(t) { return t === 'ram' ? stock(t) >= 1 : stock(t) >= 100; }
  ['spear', 'halberd', 'bow', 'cav'].forEach(function (t) { if (usable(t) && (st.type === 'sword' || stock(t) > stock(st.type))) st.type = t; });
  function mx() {
    if (!st.ids.length) return 0;
    var m = Math.min(b.troops, cmdCap(off(st.ids[0]))), wp = UNIT_TYPES[st.type].weapon;
    if (wp && wp !== 'ram') m = Math.min(m, b.w[wp]);
    return Math.floor(m / 100) * 100;
  }
  function food() { return Math.min(b.food, Math.ceil(st.troops / 20) * st.turns); }
  function foodNote() {                                        // 도시 병량이 모자라면 실제로 실리는 날수를 적는다
    var per = Math.max(1, Math.ceil(st.troops / 20)), need = per * st.turns;
    return '도시 병량 ' + fmt(b.food) + (need > b.food ? ' · <b class="bad">모자랍니다 — ' + days(Math.floor(b.food / per)) + '분만 실립니다</b>' : ' · 이웃 거점까지 20~50일');
  }
  function fix() { var m = mx(); if (st.auto || st.troops > m) st.troops = m; }
  function pv() {
    if (!st.ids.length) return '주장을 고르세요';
    var tmp = { type: st.type, off: st.ids, troops: st.troops, max: st.troops };
    return '공격 <b>' + Math.round(uAtk(tmp)) + '</b> · 방어 <b>' + Math.round(uDef(tmp)) + '</b>' + (st.step === 2 ? ' · 군량 <b>' + fmt(food()) + '</b>' : ' · 이동 <b>' + uMaxMp(tmp) + '</b>');
  }
  D = {
    render: function () {
      var h, i;
      if (st.step === 1) {                                         // ① 병과 · 무장
        h = dlgHead('출진 — ' + b.n + stepTag(1, 2, '병과 · 무장')) + '<div class="dlg-b"><div class="sec">병과</div><div class="opts">';
        var UKEY = { sword: 'u_sword', spear: 'u_spear', halberd: 'u_halberd', bow: 'u_bow', cav: 'u_cav', ram: 'u_ram' };
        for (i = 0; i < COMBAT_TYPES.length; i++) {
          var t = COMBAT_TYPES[i], T = UNIT_TYPES[t], ok = usable(t);
          h += '<button class="opt' + (st.type === t ? ' on' : '') + (ok ? '' : ' off') + '" type="button" data-a="type" data-v="' + t + '">' + thumb(UKEY[t]) + '<b>' + T.name + '</b><small>' + (t === 'sword' ? '무기 불필요' : (t === 'ram' ? '충차 ' + b.w.ram + '대' : WEAPON_NAMES[T.weapon] + ' ' + fmt(stock(t)))) + '</small></button>';
        }
        h += '</div><div class="sec">무장 <small>첫 번째가 주장 · 3명까지</small><button class="btn auto" type="button" data-a="auto">자동 편성</button></div><div class="rows">';
        var ai = APT_IDX[st.type];
        for (i = 0; i < list.length; i++) {
          var o = list[i], si = st.ids.indexOf(o.id);
          h += offRow(o, { a: 'pick', sel: si >= 0, apt: ai, badge: si === 0 ? '주장' : (si > 0 ? '부장' : ''), rt: (ai !== undefined ? '적성 <b class="' + (o.apt.charAt(ai) === 'S' ? 'bad' : (o.apt.charAt(ai) === 'A' ? 'hi' : '')) + '">' + o.apt.charAt(ai) + '</b><br>' : '') + '지휘 ' + fmt(cmdCap(o)) });
        }
        return h + '</div></div><div class="dlg-f"><div class="pv" id="dpP">' + pv() + '</div><button class="btn pri" type="button" data-a="next"' + (st.ids.length && mx() >= 100 ? '' : ' disabled') + '>다음 ›</button></div>';
      }
      // ② 병력 · 군량 · 나갈 자리(지도에서)
      h = dlgHead('출진 — ' + b.n + stepTag(2, 2, '병력 · 군량 · 나갈 자리')) + '<div class="dlg-b"><p class="note team">' + UNIT_TYPES[st.type].name + ' · ' + st.ids.map(function (id, k) { return (k ? '부장 ' : '주장 ') + '<b>' + off(id).n + '</b>'; }).join(' · ') + '</p>';
      h += EX.line();
      h += '<div class="fld"><label><span>병력 (주둔 ' + fmt(b.troops) + ')</span><b id="dpV">' + fmt(st.troops) + '</b></label><input type="range" id="dpR" min="0" max="' + mx() + '" step="100" value="' + st.troops + '" data-i="troops"></div><div class="sec">군량</div><div class="opts c4">';
      DEPLOY_FOOD.forEach(function (n) { h += '<button class="opt' + (st.turns === n ? ' on' : '') + '" type="button" data-a="turns" data-v="' + n + '"><b>' + days(n) + '분</b><small>' + fmt(Math.ceil(st.troops / 20) * n) + '</small></button>'; });
      h += '</div><p class="note" id="dpN">' + foodNote() + '</p>';
      return h + '</div><div class="dlg-f"><button class="btn" type="button" data-a="prev">‹ 무장</button><div class="pv" id="dpP">' + pv() + '</div><button class="btn pri" type="button" data-a="ok"' + (st.ids.length && st.troops >= 100 ? '' : ' disabled') + '>출진</button></div>';
    },
    on: {
      type: function (el) { var t = el.getAttribute('data-v'); if (!usable(t)) return toast(t === 'ram' ? '충차가 없습니다' : WEAPON_NAMES[UNIT_TYPES[t].weapon] + ' 재고가 없습니다'); st.type = t; st.auto = true; fix(); refreshDialog(); },
      pick: function (el) { var id = +el.getAttribute('data-v'), i = st.ids.indexOf(id); if (i >= 0) st.ids.splice(i, 1); else if (st.ids.length < 3) st.ids.push(id); else return toast('최대 3명입니다'); st.auto = true; fix(); refreshDialog(); },
      turns: function (el) { st.turns = +el.getAttribute('data-v'); refreshDialog(); },
      atauto: function () { EX.auto(); },
      auto: function () { st.ids = autoTeam(b, st.type, Math.min(b.troops, 8000)); st.auto = true; fix(); toast(st.ids.length ? '자동 편성 ' + st.ids.length + '명' : '편성할 무장이 없습니다', 1800); refreshDialog(); },
      next: function () { if (!st.ids.length) return toast('주장을 고르세요'); fix(); if (st.troops < 100) return toast('데리고 나갈 병력이 없습니다'); st.step = 2; EX.open(); },
      prev: function () { st.step = 1; EX.close(); paintDialog(0); },
      troops: function (el) {
        st.troops = +el.value; st.auto = false; $('dpV').textContent = fmt(st.troops); $('dpP').innerHTML = pv();
        var bs = document.querySelectorAll('#modal [data-a="turns"]');                 // 군량 칸의 수량과 모자람 표시도 바로 고친다
        for (var k = 0; k < bs.length; k++) bs[k].querySelector('small').textContent = fmt(Math.ceil(st.troops / 20) * +bs[k].getAttribute('data-v'));
        if ($('dpN')) $('dpN').innerHTML = foodNote();
        var ok = document.querySelector('#modal [data-a="ok"]'); if (ok) ok.disabled = !(st.troops >= 100);
      },
      ok: function () {
        if (st.step !== 2) return;
        var r = cmdDeploy(b, { type: st.type, ids: st.ids, troops: st.troops, food: food(), at: st.at || undefined });
        if (!r.ok) return toast(r.msg);
        closeDialog(); sfx('deploy');
        var u = r.unit, name = uName(u);
        clearSel(); refreshHud(); syncScene();                       // 막 나온 부대를 지도에 세우고
        if (!onScreen(u.c, u.r, 20)) jumpTo(u.c, u.r, Math.max(cam.z, 0.8));
        UI.busy = true;
        fxDeploy(u, b, function () {                                // 성에서 걸어 나오는 모습을 보인 뒤 고른 상태로
          UI.busy = false;
          if (alive(u)) { selectUnit(u); UI.sret = backToBase(b.id); talk(uLeader(u), sayLine(uLeader(u), 'deploy'), name + ' 출진 — ' + UNIT_TYPES[u.type].name + ' ' + fmt(u.troops) + '명', 2600); }
          afterAction();
        });
      }
    }
  };
  EX = exitPick(b, st, D);
  showDialog(D);
}
function destPick(b, st, D) {
  var bs = facBases(b.owner).filter(function (x) { return x.id !== b.id; }).sort(function (x, y) { return hdist(b.c, b.r, x.c, x.r) - hdist(b.c, b.r, y.c, y.r); });
  var us = G.units.filter(function (u) { return u.f === b.owner && u.type !== 'trans'; }).sort(function (x, y) { return hdist(b.c, b.r, x.c, x.r) - hdist(b.c, b.r, y.c, y.r); });
  var memo = {};
  function all() { return bs.map(function (x) { return { k: 'b', id: x.id, c: x.c, r: x.r, n: x.n }; }).concat(us.filter(function (u) { return UMAP[u.id]; }).map(function (u) { return { k: 'u', id: u.id, c: u.c, r: u.r, n: uName(u) }; })); }
  function same(a, t) { return !!a && !!t && a.k === t.k && a.id === t.id; }
  function goal(t) {                                             // 가서 설 칸: 거점은 그 칸, 부대는 그 옆의 빈 칸 가운데 이 성에서 가까운 곳
    if (t.k === 'b') return K(t.c, t.r);
    var best = -1, bd = 1e9;
    nbrs(t.c, t.r).forEach(function (n) { var k = K(n[0], n[1]), tt = terr(n[0], n[1]); if (tt === 'm' || tt === 's' || tt === 'x' || UAT[k] || BAT[k] !== undefined) return; var d = hdist(n[0], n[1], b.c, b.r); if (d < bd) { bd = d; best = k; } });
    return best;
  }
  function plan(t, best) { var id = t.k + t.id + (best ? '!' : '') + ':' + st.id; if (memo[id] === undefined) { var g = goal(t); memo[id] = g < 0 ? null : transPlan(b, st.id, g, best); } return memo[id]; }
  function eta(p) { return p.turns ? days(p.turns) : '바로 옆'; }
  function marks() {
    var list = [{ c: b.c, r: b.r, cls: 'ex src', html: '<b>' + b.n + '</b><small>여기서</small>', dy: -30 }];
    all().forEach(function (t) { var p = plan(t); list.push({ c: t.c, r: t.r, cls: 'ex' + (same(st.to, t) ? ' on' : '') + (p ? '' : ' no'), html: '<b>' + t.n + '</b><small>' + (p ? eta(p) : '길 없음') + '</small>', dy: -30 }); });
    marksSet(list); requestDraw();
  }
  function pickT(t) {
    if (t.k !== 'x' && !plan(t)) return toast(t.n + ' — 그곳으로 가는 길이 없습니다', 2000);
    st.to = t; sfx('ui'); refreshDialog(); marks();
    var row = document.querySelector('#modal .row.sel'); if (row && row.scrollIntoView) row.scrollIntoView({ block: 'nearest' });
  }
  var P = {
    list: function () { return all().map(function (t) { return { c: t.c, r: t.r, on: same(st.to, t) }; }); },
    has: function (c, r) { return all().some(function (t) { return t.c === c && t.r === r; }); },
    show: marks,
    tap: function (c, r) {
      var t = all().filter(function (x) { return x.c === c && x.r === r; })[0];
      if (!t) return toast(c === b.c && r === b.r ? '떠나는 성입니다 — 다른 우리 성이나 우리 부대를 누르세요' : '우리 성이나 우리 부대를 누르세요(이름이 뜬 곳)', 1800);
      pickT(t);
    }
  };
  return {
    open: function () {
      D.see = true; D.pick = P; if (typeof talkHide === 'function') talkHide(); paintDialog(0);
      var dl = document.querySelector('#modal .dlg'), top = $('hud') ? $('hud').getBoundingClientRect().bottom : 90, bot = dl ? dl.getBoundingClientRect().top : CH * 0.5;
      frameHexes([[b.c, b.r]].concat(all().map(function (t) { return [t.c, t.r]; })), top + 64, bot - 34, 1.1);
    },
    close: function () { D.see = false; D.pick = null; },
    find: function (v) { return v === 'x0' ? { k: 'x', id: 0, n: '성 앞' } : all().filter(function (t) { return t.k + t.id === v; })[0]; },
    pickT: pickT, plan: plan, eta: eta,
    rows: function () {
      var h = '', L = all(), i;
      for (i = 0; i < L.length; i++) {
        var t = L[i], p = plan(t), ds;
        if (t.k === 'b') { var x = G.bases[t.id]; ds = (x.kind === 'city' ? SIZE_NAME[x.sz] : '관문') + ' · 병력 ' + fmt(x.troops) + ' · 병량 ' + fmt(x.food); }
        else { var u = UMAP[t.id]; ds = '들판의 부대 · ' + UNIT_TYPES[u.type].name + ' ' + fmt(u.troops) + '명 · 군량 ' + days(unitFoodTurns(u)) + '분'; }
        h += '<button class="row' + (same(st.to, t) ? ' sel' : '') + (p ? '' : ' dim') + '" type="button" data-a="to" data-v="' + t.k + t.id + '"><span class="mid"><span class="nm">' + t.n + '</span><span class="ds">' + ds + '</span></span><span class="rt"><b>' + (p ? eta(p) : '길 없음') + '</b></span></button>';
      }
      h += '<button class="row' + (st.to && st.to.k === 'x' ? ' sel' : '') + '" type="button" data-a="to" data-v="x0"><span class="mid"><span class="nm">성 앞에 나가 기다린다</span><span class="ds">갈 곳을 정하지 않고 나갑니다 — 부대를 눌러 직접 움직입니다</span></span><span class="rt"><b>—</b></span></button>';
      return h;
    }
  };
}
function flowTransport(b) {
  var cp0 = baseCorps(b);                                       // v0.18: 군단에 맡긴 거점에서도 보낸다(군단장은 자리를 지킨다 · 행동력은 직할의 것 · 나간 수송대는 직할)
  var list = idleOfficers(b).filter(function (o) { return !(cp0 && cp0.lead === o.id); }).sort(function (x, y) { return aiMilScore(x) - aiMilScore(y); });
  if (!list.length) return toast('행동할 수 있는 무장이 없습니다');
  if (b.troops < 100) return toast('호위할 병력이 없습니다');
  var st = { step: 1, id: list[0].id, troops: Math.min(1000, Math.floor(b.troops / 100) * 100), gold: 0, food: 0, spear: 0, halberd: 0, bow: 0, horse: 0, ram: 0, to: null }, D, DP;
  var fs = [['troops', '병력', b.troops, 100], ['gold', '금', b.gold, 50], ['food', '병량', b.food, 500], ['spear', '창', b.w.spear, 100], ['halberd', '극', b.w.halberd, 100], ['bow', '노', b.w.bow, 100], ['horse', '군마', b.w.horse, 100], ['ram', '충차', b.w.ram, 1]];
  function load() { var a = []; fs.forEach(function (f) { if (st[f[0]] > 0) a.push(f[1] + ' ' + fmt(st[f[0]])); }); return a.join(' · '); }
  var on = {
    pick: function (el) { st.id = +el.getAttribute('data-v'); refreshDialog(); },
    auto: function () { var t = autoTeam(b, 'trans', 0); if (t.length) st.id = t[0]; toast('자동 선택', 1500); refreshDialog(); },
    next: function () { st.step = 2; DP.open(); },
    prev: function () { st.step = 1; DP.close(); paintDialog(0); },
    to: function (el) { var t = DP.find(el.getAttribute('data-v')); if (t) DP.pickT(t); },
    ok: function () {
      if (st.step !== 2) return;
      if (!st.to) return toast('갈 곳을 고르세요 — 지도의 우리 성이나 아래 목록', 2000);
      var free = st.to.k === 'x', p = free ? null : (DP.plan(st.to, true) || DP.plan(st.to)); if (!free && !p) return toast('그곳으로 가는 길이 없습니다');
      var need = Math.ceil(st.troops / 20) * 8, tn = st.to.n;
      var r = cmdDeploy(b, { type: 'trans', ids: [st.id], troops: st.troops, food: Math.max(st.food, Math.min(b.food, need)), gold: st.gold, cargo: { spear: st.spear, halberd: st.halberd, bow: st.bow, horse: st.horse, ram: st.ram }, at: p ? p.spot : undefined });
      if (!r.ok) return toast(r.msg);
      closeDialog(); sfx('drum'); talk(uLeader(r.unit), sayLine(uLeader(r.unit), 'trans'), free ? '수송대 출발 — 부대를 눌러 갈 곳을 정하세요' : '수송대 출발 — ' + tn + (p.turns ? ' · 약 ' + days(p.turns) : ''), 3200); syncScene(); selectUnit(r.unit); UI.sret = backToBase(b.id);
      if (free || K(r.unit.c, r.unit.r) === p.goal) { afterAction(); return; }
      orderMarch(r.unit, p.goal % W, (p.goal - p.goal % W) / W);          // 나오자마자 그곳으로 행군(이번 턴에 갈 수 있는 만큼)
    }
  };
  fs.forEach(function (f) { on[f[0]] = function (el) { st[f[0]] = +el.value; $('tv_' + f[0]).textContent = fmt(st[f[0]]); }; });
  D = {
    render: function () {
      var h, i;
      if (st.step === 1) {                                         // ① 호송 무장 · 실을 것
        h = dlgHead('수송 — ' + b.n + stepTag(1, 2, '호송 무장 · 짐')) + '<div class="dlg-b"><div class="sec">호송 무장<button class="btn auto" type="button" data-a="auto">자동</button></div><div class="rows">';
        for (i = 0; i < list.length; i++) h += offRow(list[i], { a: 'pick', sel: list[i].id === st.id });
        h += '</div><div class="sec">실을 것</div>';
        for (i = 0; i < fs.length; i++) { var f = fs[i], m = Math.floor(f[2] / f[3]) * f[3]; if (m <= 0 && f[0] !== 'troops') continue; h += '<div class="fld"><label><span>' + f[1] + ' (보유 ' + fmt(f[2]) + ')</span><b id="tv_' + f[0] + '">' + fmt(st[f[0]]) + '</b></label><input type="range" id="tr_' + f[0] + '" min="' + (f[0] === 'troops' ? 100 : 0) + '" max="' + m + '" step="' + f[3] + '" value="' + st[f[0]] + '" data-i="' + f[0] + '"></div>'; }
        return h + '<p class="note">군량 80일분은 자동으로 실립니다</p></div><div class="dlg-f"><div class="pv">행동력 ' + AP.deploy + '</div><button class="btn pri" type="button" data-a="next">다음 ›</button></div>';
      }
      // ② 어디로(지도에서)
      var free = !!st.to && st.to.k === 'x', p = st.to && !free ? DP.plan(st.to) : null;
      h = dlgHead('수송 — ' + b.n + stepTag(2, 2, '어디로')) + '<div class="dlg-b"><p class="note team">호송 <b>' + off(st.id).n + '</b> · ' + load() + '</p>';
      h += '<p class="note">지도에서 <b>우리 성 · 우리 부대</b>를 누르거나 아래에서 고르세요 — 나오자마자 그곳으로 갑니다. 머물지 · 돌아올지는 <b>수송을 마쳤을 때</b> 묻습니다.</p><div class="rows">' + DP.rows() + '</div></div>';
      return h + '<div class="dlg-f"><button class="btn" type="button" data-a="prev">‹ 짐</button><div class="pv">' + (free ? '<b>성 앞</b> — 직접 움직입니다' : (st.to ? '<b>' + st.to.n + '</b> — ' + (p ? DP.eta(p) : '길 없음') : '갈 곳을 고르세요')) + '</div><button class="btn pri' + (free || (st.to && p) ? '' : ' off') + '" type="button" data-a="ok">출발</button></div>';
    },
    on: on
  };
  DP = destPick(b, st, D);
  showDialog(D);
}

/* ---------- 목록·기록·메뉴 ---------- */
/* 부대가 있는 곳을 말로: 성역 안이면 그 성, 아니면 가장 가까운 거점에서 몇 칸 */
function unitWhere(u) {
  var z = zoneAt(u.c, u.r);
  if (z >= 0) return G.bases[z].n + ' 성역';
  var best = null, bd = 1e9;
  for (var i = 0; i < G.bases.length; i++) { var b = G.bases[i], d = hdist(u.c, u.r, b.c, b.r); if (d < bd) { bd = d; best = b; } }
  return best ? best.n + '에서 ' + bd + '칸' : '';
}
function unitState(u) {
  var ch = stChips(u);
  if (u.status) return ch;
  if (u.f !== G.player) return ch;
  if (ch) return ch + ' ' + (u.dest >= 0 ? destName(u.dest) + ' 방면 행군' : (u.done ? '행동 완료' : '<b class="hi">명령 대기</b>'));
  if (u.dest >= 0) return destName(u.dest) + ' 방면 행군';
  return u.done ? '행동 완료' : '<b class="hi">명령 대기</b>';
}
var FOE_NEAR = 10;
/* 내 거점·부대에서 rad 칸 안에 있는 다른 세력의 부대(가까운 순). to = 가장 가까운 내 거점·부대 */
function nearbyFoes(rad) {
  var mine = [], out = [];
  facBases(G.player).forEach(function (b) { mine.push({ c: b.c, r: b.r, n: b.n }); });
  facUnits(G.player).forEach(function (u) { mine.push({ c: u.c, r: u.r, n: uName(u) }); });
  G.units.forEach(function (u) {
    if (u.f === G.player) return;
    var bd = 1e9, bn = '';
    for (var i = 0; i < mine.length; i++) { var d = hdist(u.c, u.r, mine[i].c, mine[i].r); if (d < bd) { bd = d; bn = mine[i].n; } }
    if (bd <= rad) out.push({ u: u, d: bd, to: bn });
  });
  return out.sort(function (a, b) { return a.d - b.d || b.u.troops - a.u.troops; });
}
function unitRow(u, x) {
  var mine = u.f === G.player, stt = unitState(u);
  var l2 = mine ? '기력 ' + u.morale + ' · 군량 ' + days(unitFoodTurns(u)) + '분' : '기력 ' + u.morale + (x && x.to ? ' · 내 ' + x.to + '에서 ' + x.d + '칸' : '');
  return '<button class="row' + (mine && u.done ? ' dim' : '') + '" type="button" data-a="u" data-v="' + u.id + '">' + porTag(uLeader(u)) + '<span class="mid"><span class="nm">' + uName(u) + ' <em>' + UNIT_TYPES[u.type].name + '</em>' + (mine ? '' : ' ' + facChip(u.f)) + '</span>' +
    '<span class="ds">' + unitWhere(u) + (stt ? ' · ' + stt : '') + '</span><span class="ds">' + l2 + '</span></span><span class="rt"><b>' + fmt(u.troops) + '</b></span></button>';
}
function showLists(tab) {
  clearRet();
  var st = { tab: tab || 'city' };
  showDialog({
    render: function () {
      var h = dlgHead('목록') + '<div class="dlg-b"><div class="tabs">', tabs = [['city', '거점'], ['unit', '부대'], ['off', '무장'], ['fac', '세력']], i;
      for (i = 0; i < 4; i++) h += '<button type="button" data-a="tab" data-v="' + tabs[i][0] + '"' + (st.tab === tabs[i][0] ? ' class="on"' : '') + '>' + tabs[i][1] + '</button>';
      h += '</div><div class="rows">';
      if (st.tab === 'city') {
        facBases(G.player).forEach(function (b) { h += '<button class="row" type="button" data-a="b" data-v="' + b.id + '"><span class="mid"><span class="nm">' + b.n + ' <em>' + SIZE_NAME[b.sz] + '</em>' + (baseCorps(b) ? ' <em class="advt">' + corpsName(baseCorps(b)) + '</em>' : '') + '</span><span class="ds">금 ' + fmt(b.gold) + ' · 병량 ' + fmt(b.food) + ' · 치안 ' + b.order + '</span></span><span class="rt"><b>' + fmt(b.troops) + '</b><br>대기 ' + idleOfficers(b).length + '명</span></button>'; });
      } else if (st.tab === 'unit') {
        // 내 부대(명령을 기다리는 부대가 위로) + 다른 세력의 부대(가까운 순)
        var us = facUnits(G.player).sort(function (x, y) { return (x.done ? 1 : 0) - (y.done ? 1 : 0); }), ready = us.filter(function (u) { return !u.done && !u.status && !unitCorps(u); }).length;
        h += '</div><div class="sec">내 부대 ' + us.length + '개' + (us.length ? ' <small>명령을 기다리는 부대 ' + ready + '개</small>' : '') + '</div><div class="rows">';
        if (!us.length) h += '<p class="note">출진한 부대가 없습니다</p>';
        us.forEach(function (u) { h += unitRow(u); });
        var total = G.units.length - us.length, foes = nearbyFoes(st.allU ? 9999 : FOE_NEAR);
        h += '</div><div class="sec">' + (st.allU ? '다른 세력의 부대 ' + foes.length + '개' : '가까이 있는 다른 세력 부대 ' + foes.length + '개') + ' <small>가까운 순</small></div><div class="rows">';
        if (!foes.length) h += '<p class="note">' + (st.allU ? '지도에 다른 세력의 부대가 없습니다.' : '내 거점과 부대에서 ' + FOE_NEAR + '칸 안에는 다른 세력의 부대가 없습니다.') + '</p>';
        foes.forEach(function (x) { h += unitRow(x.u, x); });
        if (!st.allU && total > foes.length) h += '<button class="row more" type="button" data-a="allu"><span class="mid"><span class="nm">다른 세력 부대 모두 보기</span><span class="ds">천하에 ' + total + '개</span></span><span class="rt">▸</span></button>';
      } else if (st.tab === 'off') {
        var os = facOfficers(G.player).sort(function (x, y) { return (isLord(y) ? 1000 : 0) + (y.ldr + y.war + y.int + y.pol) - (isLord(x) ? 1000 : 0) - (x.ldr + x.war + x.int + x.pol); });
        os.forEach(function (o) { h += offRow(o, { badge: isLord(o) ? '군주' : advTag(o), rt: (o.unit !== null ? '출진' : G.bases[o.st === 'travel' ? o.dest : o.loc].n) + '<br><span class="' + (o.loy < 70 ? 'bad' : '') + '">충 ' + o.loy + '</span>' }); });
      } else {
        G.factions.filter(function (F) { return F.alive; }).map(function (F) { var t = 0; facBases(F.id).forEach(function (b) { t += b.troops; }); facUnits(F.id).forEach(function (u) { t += u.troops; }); return { F: F, t: t, c: facCities(F.id).length }; })
          .sort(function (x, y) { return y.c - x.c || y.t - x.t; })
          .forEach(function (x) { var L = off(x.F.lord); h += '<button class="row" type="button" data-a="f" data-v="' + x.F.id + '">' + porTag(L) + '<span class="mid"><span class="nm">' + x.F.name + (x.F.id === G.player ? ' <em>나</em>' : '') + '</span><span class="ds">도시 ' + x.c + ' · 무장 ' + facOfficers(x.F.id).length + '명</span></span><span class="rt"><b>' + fmt(x.t) + '</b><br><span class="chip" style="background:' + x.F.color + '">&nbsp;</span></span></button>'; });
      }
      return h + '</div></div>';
    },
    on: {
      tab: function (el) { st.tab = el.getAttribute('data-v'); refreshDialog(); },
      allu: function () { st.allU = true; refreshDialog(); },
      b: function (el) { var b = G.bases[+el.getAttribute('data-v')]; jumpFromDialog('목록', function () { gotoBase(b); }); },
      u: function (el) { var u = UMAP[+el.getAttribute('data-v')]; if (u) jumpFromDialog('목록', function () { gotoUnit(u); }); },
      off: function (el) { showOfficer(off(+el.getAttribute('data-v'))); },
      f: function (el) { var f = +el.getAttribute('data-v'), L = off(G.factions[f].lord), b = L.unit !== null ? null : G.bases[L.loc]; if (!b) b = facBases(f)[0]; if (b) jumpFromDialog('목록', function () { gotoBase(b); }); }
    }
  });
}
function logRows(list) {
  var h = '';
  for (var i = list.length - 1; i >= 0; i--) { var e = list[i]; h += '<button class="row" type="button" data-a="j" data-v="' + i + '"><span class="mid"><span class="ds">' + e.d + '</span><span style="white-space:normal;display:block' + (e.imp >= 3 ? ';color:var(--gold);font-weight:700' : '') + '">' + e.t + '</span></span></button>'; }
  return h || '<p class="note">아직 기록이 없습니다.</p>';
}
function showLog(list, title) {
  clearRet();
  showDialog({
    render: function () { return dlgHead(title) + '<div class="dlg-b"><div class="rows">' + logRows(list) + '</div></div>'; },
    on: { j: function (el) { var e = list[+el.getAttribute('data-v')]; if (e && e.c !== undefined) jumpFromDialog(title, function () { clearSel(); jumpTo(e.c, e.r, Math.max(cam.z, 0.8)); flashHex(e.c, e.r, '#b5332a'); }); } }
  });
}
var HELP_HTML = '<div class="help">' +
  '<h3>목표</h3><p>도시 42곳을 모두 차지하면 천하통일입니다. 거점을 모두 잃으면 끝납니다.</p>' +
  '<h3>턴 종료와 지난 열흘</h3><p>턴 종료를 누르면 열흘이 흐릅니다. 먼저 행군을 맡겨 둔 내 부대가 움직이고, 이어서 다른 세력의 움직임 가운데 <b>나와 관련된 일, 내 땅 가까이에서 일어난 일, 성의 주인이 바뀐 일</b>을 차례로 보여 줍니다. 화면을 누르면 다음 장면으로 넘어가고, 건너뛰기를 누르면 바로 내 차례가 됩니다. 속도는 재생 중 아래 버튼이나 메뉴에서 바꿉니다. 끝나면 지난 열흘의 일을 한데 모아 보여 줍니다.</p>' +
  '<h3>턴과 행동력</h3><p>한 턴은 10일입니다. 내정·출진 명령은 행동력을 씁니다. 행동력은 매 턴 돌아오고, 도시가 많고 군주의 매력이 높을수록 많이 돌아옵니다. 무장 한 사람은 한 턴에 한 가지 일만 합니다.</p>' +
  '<h3>자동</h3><p>무장을 고르는 창의 <b>자동</b> 버튼은 그 일을 가장 잘하는 무장을 골라 줍니다. 한 번 더 누르면 한 명만 쓰는 편성으로 바뀝니다. 열 제목(통·무·지·정·매)을 누르면 그 능력으로 정렬합니다.</p>' +
  '<h3>도시와 시설</h3><p>도시를 누르면 명령 창이 열립니다. <b>건설</b> 탭을 열면 지도가 어두워지고 <b>지을 수 있는 빈 부지만 밝게</b> 번호와 함께 보입니다 — 밝은 칸이나 같은 번호의 줄을 누르고 시설을 고르면 됩니다(고른 자리는 붉은 테두리). 칸이 점선으로만 보이면 지금은 지을 수 없다는 뜻이고, 까닭(쉬는 무장·금·행동력)이 창에 적힙니다. <b>지은 시설</b>에도 같은 번호가 붙어 있고, 줄이나 지도에서 누르면 그 시설만 환해지고 <b>붉은 테두리와 붉은 이름표</b>가 붙습니다. 짓는 중인 시설은 비계를 두른 공사장으로 보입니다. 같은 시설이 붙어 있으면 흡수합병으로 레벨을 올립니다(최대 3). 조폐는 옆의 시장, 곡창은 옆의 농장 수입을 50% 늘립니다(한 곳에 둘까지). 금은 매월 초, 병량은 1·4·7·10월 초에 들어옵니다.</p>' +
  '<p><b>시설의 레벨</b> — 지은 시설의 줄에는 <b>지금 레벨의 값</b>이 먼저 적혀 있습니다(시장 ' + MARKET_INC[1] + ' · ' + MARKET_INC[2] + ' · ' + MARKET_INC[3] + ', 농장 ' + fmt(FARM_INC[1]) + ' · ' + fmt(FARM_INC[2]) + ' · ' + fmt(FARM_INC[3]) + '). 시설을 누르면 옆 시설과 치안까지 넣은 <b>실제 수입</b>이 나옵니다. 병영·대장간·마구간은 레벨마다 징병량·생산량이 ×' + LV_MUL[1].toFixed(1) + ' · ×' + LV_MUL[2].toFixed(1) + ' · ×' + LV_MUL[3].toFixed(1) + '이고 <b>도시에서 가장 높은 한 곳만</b> 셉니다. <b>조폐·곡창·공방은 레벨이 없습니다</b>(레벨이 효과에 쓰이지 않아 적지 않고, 합칠 수도 없습니다). 합병하면 두 곳이 한 곳이 되므로 당장의 수입은 조금 줄고 <b>부지가 하나 빕니다</b>(합병 창에 얼마가 달라지는지 적혀 있습니다).</p>' +
  '<p><b>치안</b> — 금·병량 수입에 (50 + 치안 ÷ 2)%, 징병량에 (40 + 치안 × 0.6)%가 곱해지고, 20 아래면 징병할 수 없습니다. 징병할 때마다 10씩, 50을 넘으면 매월 1씩 내려가고 <b>순찰</b>로 올립니다. 거점 창의 치안 칸을 누르면 지금의 값이 나옵니다. 민란은 없습니다.</p>' +
  '<h3>STATUS 창</h3><p>화면 아래에 늘 떠 있는 창입니다. 아무것도 고르지 않았을 때는 <b>지금 할 일</b>이 보이고, 줄을 누르면 그 거점이나 부대로 바로 갑니다. 거점이나 부대를 고르면 같은 자리에 그 정보와 명령이 나옵니다. 이름 아래의 +숫자는 금(매월)·병량(분기) 수입입니다. 오른쪽 ▾로 접을 수 있고, 맨 위 날짜 줄을 누르면 다시 펼쳐집니다.</p><p>아래 <b>목록</b> 단추는 거점·부대·무장·세력의 목록을 엽니다 — 부대 목록에는 내 부대의 위치와 상태, 그리고 가까이 있는 다른 세력의 부대가 나옵니다.</p>' +
  '<h3>출진과 이동</h3><p>거점의 출진 탭에서 병과, 무장(주장과 부장 둘), 병력, 군량(' + days(DEPLOY_FOOD[0]) + '~' + days(DEPLOY_FOOD[DEPLOY_FOOD.length - 1]) + '분)을 정하면 부대가 성 앞에 나옵니다. <b>두 단계</b>입니다 — ① 병과와 무장을 고르고 [다음] ② 병력 · 군량과 <b>나갈 자리</b>를 정하고 [출진]. ②단계에서는 창이 낮아지고 지도에 성 둘레 여섯 칸이 빛납니다(칸마다 방향과 땅이 적혀 있습니다): <b>지도의 칸을 누르면</b> 그 자리로 나갑니다. 고르지 않으면 길이 난 쪽으로 나갑니다(붉은 칸). 창병·극병·노병·기병은 무기 재고가 병력만큼 필요합니다. 부대를 누르면 이번 턴에 갈 수 있는 칸이 <b>파랗게</b> 보이고, 그 칸을 누르면 움직입니다. 적이나 적의 성을 누르면 공격합니다. 적 부대 옆 칸에 들어서면 그 턴에는 더 나아가지 못합니다. 자기 거점으로 들어가면 입성하고, 주인 없는 거점은 들어가면 차지합니다.</p>' +
  '<h3>성역과 행군</h3><p>성 둘레 ' + ZONE_R + '칸(붓으로 두른 고리 안)은 그 성의 <b>성역</b>입니다. 성역을 드나들 때 멈추지 않습니다 — 이동력이 남아 있으면 그대로 나아가고, 닿으면 바로 칠 수 있습니다. 다만 <b>출진한 그 턴에는 거점과 시설을 칠 수 없습니다</b>(부대끼리는 싸울 수 있습니다). 성에서 나와 다른 성을 치기까지 가까운 성끼리는 20일, 대개는 30일 넘게 걸립니다.</p>' +
  '<h3>관문과 능선</h3><p>관문(호관 · 호로관 · 함곡관 · 동관 · 무관 · 양평관 · 검각) 양옆으로는 <b>능선</b>이 이어집니다(지도에 좁은 산줄기로 그려져 있습니다). 능선은 넘을 수 없습니다 — 능선 너머의 칸은 바로 옆이어도 갈 수 없고 맞붙어 칠 수 없습니다(노병은 두 칸 거리에서 넘겨 쏘고, 계략은 넘어갑니다). <b>내 관문은 그냥 지나갑니다</b>(관문 칸에 서면 입성). <b>남의 관문은 빼앗아야</b> 지나고, 주인 없는 관문은 들어가면 내 것이 됩니다. 능선은 관문에서 열 몇 칸까지 이어지므로 멀리 돌아가는 길이 남아 있는 곳도 있습니다(호로관은 보병으로 관문 길 32일 · 돌아가면 59일쯤). 호로관은 낙양의 동쪽을 모두 막습니다 — 허창에서 낙양으로 가는 길도 호로관을 지납니다. 장안에서 무관으로 가는 길은 동관을, 한중에서 검각으로 가는 길은 양평관을 지납니다.</p>' +
  '<h3>성의 내구</h3><p>성과 관문의 내구는 <b>맞지 않은 지 ' + days(DUR_HEAL.wait) + '이 지나면</b> 턴마다 최대 내구의 ' + DUR_HEAL.pct + '%씩 저절로 돌아옵니다(대도시 ' + Math.round(MAX_DUR.L * DUR_HEAL.pct / 100) + ' · 관문 ' + Math.round(MAX_DUR.G * DUR_HEAL.pct / 100) + '). 공격을 받는 동안에는 돌아오지 않습니다 — 거점 창의 내구 옆에 다음 턴에 돌아올 양(+숫자)이나 <b>회복 멈춤</b>이 적혀 있습니다.</p>' +
  '<h3>등용</h3><p>재야 · 포로 · 이웃한 다른 세력의 무장 모두 <b>한 사람에게 한 달에 한 번</b> 권할 수 있습니다. 응할지는 달마다 한 번 정해집니다(같은 달에는 누가 권해도 군사의 ○×가 같습니다 — 권하는 무장에 따라 가능성은 달라집니다). <b>충성 100</b>인 무장은 누가 권해도 응하지 않습니다.</p>' +
  '<h3>초반 보호</h3><p>판을 시작하면 한동안 다른 세력이 우리 <b>거점과 시설</b>을 먼저 치지 않습니다. 기간은 <b>시작할 때의 병력</b>으로 정해집니다 — 1만 미만이면 ' + months(PEACE_PLAYER[0][1]) + ', 2만 미만이면 ' + months(PEACE_PLAYER[1][1]) + ', 그 밖은 ' + months(PEACE_ALL) + '. 언제까지인지는 STATUS 창의 이름 옆 표에 보입니다(누르면 풀이).</p>' +
  '<ul><li>들판의 부대끼리는 싸울 수 있고, 주인 없는 성은 누구나 차지합니다.</li><li><b>우리가 어떤 세력의 거점이나 시설을 먼저 치면</b> 그 세력에 대해서는 보호가 풀립니다(치기 전에 알려 줍니다). 다른 세력과의 보호는 그대로입니다.</li><li>처음 ' + months(PEACE_ALL) + '은 다른 세력끼리도 서로의 거점을 치지 않습니다.</li><li>보호가 끝난 뒤 ' + months(PEACE_RAMP) + '은 완충 기간입니다 — 한 번에 한 세력만 우리를 치러 오고, 출진에 필요한 병력 우위가 평소의 1.25배 대신 2배에서 시작해 차츰 내려옵니다.</li><li>0.8에서 하던 판을 이어 해도, 아직 그 기간 안이면 보호받습니다.</li></ul>' +
  '<h3>수송과 보급</h3><p>거점의 출진 탭 <b>수송</b>으로 병력·금·병량·무기를 실은 수송대를 냅니다 — ① 호송 무장과 짐 ② <b>어디로</b>: 지도에 우리 성과 들판의 우리 부대마다 이름과 걸리는 날수가 뜹니다. 누르고 [출발]하면 수송대가 그쪽으로 나와 <b>곧바로 행군</b>합니다(턴을 마칠 때마다 한 구간씩 알아서 갑니다). 아군 거점에 들어가면 실은 것이 그 거점에 합쳐집니다. <b>아군 부대의 옆 칸</b>에 가면 부대 창의 <b>보급</b>으로 병량과 병력을 넘길 수 있습니다(받는 부대 쪽에서는 <b>보급 받기</b>). 병력은 받는 주장의 지휘 한도까지이고, 창병·극병·노병·기병에게는 그 무기도 실어 와야 합니다. 보급한 수송대는 그 턴의 행동을 마칩니다.</p>' +
  '<p><b>수송을 마친 뒤</b> — 머물지 · 돌아갈지는 떠날 때가 아니라 <b>수송이 끝났을 때</b> 묻습니다. 수송대가 우리 거점에 들어가면 창이 뜹니다(턴을 넘기는 사이에 닿았으면 내 차례가 돌아오자마자): <b>머문다</b>면 호송 무장은 그 거점에 남고, <b>돌아간다</b>면 떠나온 거점으로 걸어서 돌아갑니다(무장 [이동]과 같은 날수 · 행동력은 들지 않습니다). 부대에 보급한 뒤에도 묻습니다 — 남아서 더 나눠 주거나, 떠나온 거점으로 행군합니다. 떠나온 거점을 잃었으면 묻지 않습니다. 부대 창의 <b>귀환</b>은 수송대를 지금 떠나온 거점으로 행군시킵니다.</p>' +
  '<h3>행군과 공격 명령</h3><p>부대를 고른 채 <b>파란 칸 밖의 땅을 누르면 곧바로 그곳으로 행군</b>합니다 — 이번 턴에 갈 수 있는 만큼 바로 가고, 턴을 마칠 때마다 한 구간씩 알아서 갑니다. 잘못 눌렀으면 <b>이동 취소</b>(제자리로 돌아오고 명령도 거둡니다). <b>닿지 않는 적 부대나 적의 성을 누르면 공격 명령</b>입니다: 다가가서, 턴을 마칠 때 닿으면 알아서 칩니다(주는 피해에서 받는 반격을 뺀 기대값이 가장 큰 수 — 군사의 추천 薦과 같습니다. 계략 · 일기토는 걸지 않습니다). 닿는 적을 누르면 전처럼 수를 직접 고릅니다. 도중에 직접 움직이거나 쳐도 되고, 부대 창의 <b>명령 취소</b>로 거둡니다. 내 성이나 빈 성으로 보내려면 그 성을 누르고 맨 위의 <b>이 성으로 행군</b>을 누르세요.</p>' +
  '<h3>전투</h3><p>부대를 고르고 적을 누르면 공격·전법·계략 가운데 고를 수 있습니다. 전법은 기력을 쓰고, 병과 적성(C→S)이 높을수록 쓸 수 있는 전법이 늘고 잘 통합니다. 적성은 부대의 공격·방어에도 곱해집니다(C ×' + APT_MUL.C + ' ~ S ×' + APT_MUL.S + ') — 주장과 부장 가운데 가장 높은 적성을 씁니다. 무장 줄마다 능력치 아래에 <b>창 · 극 · 노 · 기 · 병기</b> 적성이 적혀 있습니다.</p>' +
  '<p><b>전법의 결과는 세 가지</b>입니다. <b>실패</b>하면 피해가 통상 공격의 ' + Math.round(TACTIC_K.failDmg * 100) + '%로 줄고 효과가 없으며 반격을 통상 공격의 ' + (TACTIC_K.failCounter / 0.55).toFixed(2).replace(/0$/, '') + '배로 받습니다. <b>성공</b>하면 전법의 피해와 효과가 들어가고 반격은 통상 공격만큼 받습니다(견인·관진, 멀리서 쏜 전법, 밀려나 떨어진 적은 반격하지 못합니다). <b>대성공</b>이면 피해가 ' + TACTIC_K.crit + '배가 되고 <b>효과 자체가 세집니다</b> — 격퇴·축출은 두 칸 밀어내고, 난진은 반드시 혼란시키고, 탈기는 기력을 30 깎는 식입니다. <b>성공률은 양쪽을 다 봅니다</b>: 내 병과 적성, 내 무력·통솔과 상대 통솔의 차이, 양쪽 병력, 상대의 병과 적성, 상대가 선 지형. 병력이 훨씬 많은 부대나 통솔이 높은 장수에게는 잘 통하지 않고, 병력 차만큼 피해도 줄어듭니다. <b>전법이 늘 이득은 아닙니다</b> — 무장이 상대보다 강할수록 이득이 크고, 약한 쪽이 쓰면 보통 공격보다 손해입니다. 대성공률은 적성·무력·(내 무력 − 상대 통솔)로 정해지며, 혼란은 상대의 지력·통솔이 높을수록 덜 걸립니다. 적을 고른 뒤 <b>전법 풀이</b>를 누르면 그 상대에 대한 확률과 효과, 그리고 전법마다 <b>기대 피해 · 받는 반격</b>을 보통 공격과 나란히 볼 수 있습니다.</p>' +
  '<ul><li>창병은 기병에, 기병은 극병에, 극병은 창병에 강합니다.</li><li>노병은 두 칸 밖에서 반격 없이 쏩니다.</li><li><b>충차</b>는 성의 내구를 크게 깎습니다 — 한 번에 창병의 네댓 배(중도시의 내구 2,400이 네 번쯤이면 무너집니다). 싸움에는 약하니 다른 부대로 지켜 주세요. 길에서는 보병보다 조금 느린 정도로 가고, 길 밖에서는 느립니다.</li><li>거점은 병력이나 내구가 0이 되면 함락됩니다.</li><li>출진 · 수송 창의 <b>나갈 자리</b>에서 성 둘레의 어느 칸으로 나갈지 고를 수 있습니다(고르지 않으면 길이 난 쪽부터).</li><li>시설이 선 칸도 지나가고 설 수 있습니다. 남의 시설은 옆 칸이나 그 위에서 부술 수 있습니다.</li><li>숲·구릉의 부대는 피해를 덜 받고, 강 위의 부대는 약해집니다.</li></ul>' +
  '<p><b>전법 열두 가지</b> — 이름만 보고 효과가 떠오르도록 한자 두 글자로 지었습니다.</p><ul>' + ['spear', 'halberd', 'bow', 'cav'].map(function (k) { return '<li><b>' + UNIT_TYPES[k].name + '</b> — ' + TACTICS[k].map(function (t) { return t.name + ' <i class="hj">' + t.han + '</i> ' + t.tag; }).join(' / ') + '</li>'; }).join('') + '</ul>' +
  '<p><b>견인</b>은 한 칸 물러서며 적을 내가 섰던 자리로 끌어당깁니다 — 숲 · 언덕에 버틴 적을 끌어내거나, 아군이 둘러쌀 자리로 데려올 때 씁니다. 내 뒤가 막혔거나(산 · 부대 · 거점) 불타고 있으면 끌지 못합니다(피해와 반격 없음은 그대로).</p>' +
  '<h3>계략과 상태 이상</h3><p>부대는 기력을 써서 <b>화계·교란·위보</b>를 겁니다(성공률은 양쪽 지력의 차이로 정해집니다). 걸린 부대는 지도에서 바로 알아볼 수 있습니다 — <b>머리 위에 색 딱지</b>가 뜨고(혼란은 쪽빛, 위보는 황토빛, 불길은 붉은빛) 딱지에 <b>남은 날수</b>가 적힙니다. 혼란·위보에 걸린 부대는 머리 위에 소용돌이가 돌고 빛이 바래며, 혼란이면 비틀거립니다.</p>' +
  '<ul><li><b>혼란</b>: 움직이지도 싸우지도 못합니다. 받는 피해가 25% 늘고 반격하지 못하며, 전법이 더 잘 통합니다. 교란으로 걸면 20일, 전법(난진 등)으로 걸면 10일입니다.</li><li><b>위보</b>: 20일 동안 명령을 듣지 않고 가까운 자기 거점 쪽으로 물러납니다. 반격하지 못합니다.</li><li><b>불길</b>: 불 위에 머무는 부대는 턴마다 병력 250~400명과 기력 5를 잃습니다. 불 밖으로 옮기거나 <b>소화</b>로 끕니다.</li><li>이미 혼란·위보에 걸린 부대에는 교란·위보를 다시 걸 수 없습니다.</li><li>부대를 누르면 창 맨 위에 걸린 상태·남은 날수·효과가 적혀 있습니다. 내 부대가 걸리면 <b>지금 할 일</b>과 <b>지난 열흘의 일</b>에도 나옵니다.</li></ul>' +
  '<h3>인재</h3><p>탐색으로 재야의 인재를 찾아 등용합니다. 사로잡은 적장도 등용할 수 있습니다. 해가 바뀌면 새 인물이 세상에 나옵니다.</p>' +
  '<p><b>옛 관계</b> — 등용은 누구를 보내느냐에 따라 달라집니다. 보내는 무장이 대상과 <b>직접 인연</b>(의형제·혈연·부부·인척·심복)이면 +' + TIES.bond + ', 대상의 <b>옛 주군</b>이면 +' + TIES.lord + ', 같은 주군과 인연으로 묶인 사이면 +' + TIES.kin + ', 옛 신하면 +' + TIES.vassal + ', <b>옛 동료</b>(같은 세력에 있던 적이 있다)면 +' + TIES.mate + '입니다(가장 큰 것 하나). 대상이 예전에 우리 세력을 섬겼다면 +' + TIES.home + '.</p>' +
  '<p><b>멸망한 세력 출신</b>은 돌아갈 곳이 없어 더 잘 응합니다 — 포로는 전보다 +' + (15 + TIES.fallen) + '(포로라서 깎이던 15가 없어지고 +' + TIES.fallen + '), 재야는 +' + TIES.fallen + '. 그 세력의 군주였던 사람은 그대로입니다. 반대로 <b>옛 군주를 참수하면</b> 그 신하였던 무장들은 우리에게 ' + TIES.grudge + ', 그 군주와 인연이 있던 무장은 ' + TIES.grudgeCap + '% 아래입니다. 등용 창의 대상 줄에 출신과 가장 잘 권할 무장이, 무장을 고르는 표에 그 사이가, 아래에 더해진 까닭이 적혀 있습니다.</p>' +
  '<p><b>다른 세력의 무장</b>도 등용할 수 있습니다 — 내 거점과 길로 바로 이어진 <b>이웃 거점에 머무는 무장</b>이 대상입니다(인재 → 등용). 응하면 그 자리에서 내 거점으로 넘어옵니다. 성공률은 보내는 무장의 매력·정치, 두 군주의 매력 차이, 그리고 <b>대상의 충성</b>으로 정해집니다(옛 관계는 ' + Math.round(TIES.poach * 100) + '%만 셉니다). 제 주군과 인연이 있거나 충성이 ' + POACH.wall + ' 이상이면 응하지 않고(대상과 직접 인연이 있는 무장을 보내면 충성이 높아도 권할 수 있습니다), 군주와 출진 중인 무장에게는 권할 수 없습니다. 성공률은 <b>그 달에 응할 확률</b>입니다 — 다른 세력 무장의 마음은 달마다 한 번 정해지고, 한 무장에게는 한 달에 한 번 권할 수 있습니다. 거절한 무장은 충성이 ' + POACH.up + ' 오르고, 한 사람이 넘어가면 그 세력에 남은 무장들의 충성이 ' + POACH.tighten + '씩 오릅니다.</p>' +
  '<p>다른 세력도 같은 규칙으로 <b>내 무장을 데려갑니다</b>(초반 보호 기간에는 권하지 않고, 무장이 ' + POACH_AI.spare + '명 이하인 세력의 무장에게도 권하지 않습니다). 위험한 무장이 있으면 지금 할 일에 "떠날 수 있는 무장"이 뜹니다 — <b>포상</b>으로 충성을 ' + POACH.wall + '까지 올리면 응하지 않습니다.</p>' +
  '<h3>대화창</h3><p>명령을 내리면 맡은 무장이 화면 위쪽의 <b>대화창</b>에서 한마디 하고, 그 아래에 결과가 한 줄로 붙습니다(등용·포상은 상대가 답합니다). 잠깐 뒤 저절로 사라지고 누르면 바로 닫힙니다. 메뉴의 <b>대화창</b>으로 끌 수 있습니다 — 끄면 결과만 알림 줄로 나옵니다.</p>' +
  '<h3>군단</h3><p>거점이 늘면 먼 곳은 <b>군단</b>에 맡길 수 있습니다. STATUS 창의 <b>+ 군단</b>(또는 거점 창의 <b>군단</b> 탭)에서 맡길 거점을 고르면 그 거점의 무장 가운데 한 사람이 <b>군단장</b>이 되어 다스립니다. 군단 창에서 <b>방침</b>을 줍니다 — <b>내정</b>(시설 · 치안, 병력은 지킬 만큼만) · <b>군비</b>(징병 · 병기 · 훈련) · <b>공격</b>(고른 거점을 친다) · <b>지원</b>(병력과 물자를 고른 내 거점으로 보낸다). <b>내정 방침의 군단은 성 밖으로 나가 싸우지 않습니다</b>(적이 오면 성이 스스로 막습니다). 군비 · 지원 방침에서는 군단 창의 <b>출격</b>에서 허용 · 금지를 고릅니다 — 허용이면 적 부대가 성 가까이 올 때 나가서 막습니다. 군단에 맡긴 거점에서도 <b>수송</b>은 직접 보낼 수 있습니다(거점 창의 수송 — 나간 수송대는 직할입니다).</p>' +
  '<p>군단은 내가 <b>턴 종료</b>를 누른 직후, 다른 세력보다 먼저 움직입니다. 한 일은 <b>지난 열흘의 일</b>에 군단마다 한 줄로 나옵니다. 군단은 <b>제 행동력</b>을 따로 씁니다(턴마다 ' + CORPS_AP.base + ' + 도시 × ' + CORPS_AP.city + ' + 군단장 매력 ÷ 5) — 맡긴 도시는 내 행동력에서 빠집니다.</p>' +
  '<p><b>공격</b>은 군단장이 이길 만하다고 볼 때만 나섭니다: 낼 수 있는 병력이 <b>(수비 + 가는 동안 늘어날 몫) × ' + CORPS_ATK.mul + ' + ' + fmt(CORPS_ATK.add) + '</b>을 넘고 행동력이 60 모였을 때(지키는 장수의 무력·통솔이 75를 넘으면 그만큼 더 — 100이면 1.5배). 수비에는 그 세력이 12칸 안에 내놓은 부대도 셉니다. 한번 나서면 남은 도시들도 뒤따라 보탭니다. 군단 창에 지금의 병력과 필요한 병력이 적혀 있습니다. 군단이 차지한 거점은 그 군단에 들고, 목표를 손에 넣으면 방침은 군비로 돌아갑니다. 먼저 치면 그 세력과의 초반 보호가 풀리는 것은 내가 칠 때와 같습니다.</p>' +
  '<p>맡긴 거점과 군단의 부대에는 직접 명령할 수 없습니다. 거점 창 · 부대 창 · 군단 창의 <b>직할로</b>를 누르면 언제든 되돌아옵니다. 포로는 군단장이 풀어 주지 않습니다(등용만 권합니다).</p>' +
  '<h3>군사(軍師)</h3><p>세력마다 군사를 한 사람 둡니다. <b>STATUS 창 맨 위</b>에 군사의 초상과 한마디가 있고, 그 옆의 <b>임명(바꾸기)</b> 단추로 고릅니다(무장 창의 <b>군사로 삼기</b>도 같습니다). 군사는 지금 가장 급한 일을 말해 주고 — 누르면 그 일로 갑니다 — 내 차례가 시작될 때도 대화창으로 알립니다. 급한 알림이 없을 때는 <b>헌책</b>(평소의 조언)을 하나씩 말하고, <b>다른 조언</b>을 누르면 다음 것을 듣습니다. 처음에는 지력이 가장 높은 무장이 맡고, 군주는 될 수 없습니다. 군사는 <b>등용과 계략을 하기 전에</b> 통할지 미리 말해 줍니다 — 무장을 고르는 표 아래와 부대 창에 초상과 함께 "통할 것입니다 / 어렵겠습니다", 단추에는 <i class="adv y">○</i>(통한다)·<i class="adv n">×</i>(어렵다). 맞힐 확률은 <b>군사의 지력 그대로</b>입니다(지력 84면 84%). 상대가 군사보다 똑똑하면 그 차이의 절반만큼 더 틀립니다(지력 70인 군사가 지력 90인 상대를 보면 60%). ' + ADVISE.min + '% 아래로는 내려가지 않고, 지력 100이라야 늘 맞습니다.</p>' +
  '<p><b>헌책과 지력</b> — 헌책은 순찰·등용·탐색·포상·훈련·징병·건설·무기·거래·출진 가운데 지금 할 만한 일입니다. 군사의 지력이 높을수록 <b>정말 급한 것부터</b> 말하고(지력이 낮으면 순위가 뒤섞입니다), <b>알아채기 어려운 일</b>(숨은 인재 · 허술한 이웃 거점 · 무엇을 지을지)을 놓치지 않으며, 말이 자세합니다 — 지력 ' + COUNSEL.detail + ' 이상이면 숫자와 보낼 사람까지, ' + COUNSEL.some + ' 이상이면 무엇을 할지, 그 아래는 두루뭉술하게. 징병은 길로 이어진 이웃 세력의 병력이 우리보다 많을 때만 권합니다. 한 번 한 말은 ' + days(COUNSEL.keep) + ' 동안 맨 앞에 다시 세우지 않고, 같은 종류의 말(징병 · 건설 …)도 잇달아 하지 않습니다(급한 일은 예외).</p>' +
  '<p><b>탐색</b>의 결과도 미리 정해져 있습니다(도시 · 턴 · 그 턴의 몇 번째인가). 탐색할 무장을 고르면 군사가 <b>오늘 숨은 인재를 만날지</b> 말해 줍니다. 숨은 인재가 있는 도시는 헌책으로 귀띔해 주는데, 있는지 없는지를 아는 것도 지력만큼만 맞습니다(달마다 정해집니다).</p>' +
  '<p>등용과 계략의 성패는 <b>대상마다 미리 정해져 있습니다</b>(계략과 재야·포로 등용은 턴마다, 다른 세력 무장의 등용은 달마다). 그래서 그동안에는 누구에게 다시 물어도 답이 같고, 가장 잘하는 무장이 안 되면 누구도 안 됩니다. 군사를 바꿔 물어도 새로 알 수 있는 것은 없습니다 — 지력이 더 높은 군사의 말이 더 자주 맞을 뿐입니다.</p>' +
  '<h3>무장 명부</h3><p>무장은 모두 ' + SCENARIO.officers.length + '명입니다(v0.17에서 124명이 늘었습니다 — 여성 ' + SCENARIO.women.length + '명). 194년에 이미 세력에 있는 사람 말고는 <b>등장 연도</b>가 되어야 나옵니다: 재야의 사람은 그 도시에서 <b>탐색</b>으로 찾고, 군주의 집안사람은 해가 바뀔 때 스스로 찾아옵니다. 예전 판의 저장을 불러오면 새 무장이 그 판에 덧붙습니다 — 세력에 있던 사람은 그 세력이 살아 있으면 그 세력으로, 망했으면 그 도시의 재야로 갑니다.</p>' +
  '<h3>무장 카드와 특기</h3><p>어느 창에서든 <b>무장의 얼굴을 누르면</b> 그 무장의 능력 · 병종 적성 · 특기 풀이 · 있는 곳이 겹쳐 뜹니다. ×나 바깥을 누르면 닫히고, 하던 일(무장 고르기 · 일기토 등)은 그대로 남습니다. 목록의 특기 이름 옆에는 무엇을 하는 특기인지 한 줄이 붙고, 무장을 고르는 표에는 줄마다 <b>병종 적성</b>(창 · 극 · 노 · 기 · 병기)과 특기가 함께 보입니다.</p>' +
  '<p><b>병종 적성</b>은 부대의 공격 · 방어에 곱해집니다 — C ×' + APT_MUL.C + ' · B ×' + APT_MUL.B + ' · A ×' + APT_MUL.A + ' · S ×' + APT_MUL.S + '(주장 · 부장 가운데 가장 높은 적성). 전법은 C 하나 · B 둘 · A부터 셋을 쓰고, 높을수록 잘 통합니다.</p>' +
  '<p><b>열전</b> — 무장 창과 무장 카드에는 그 사람이 누구인지 두세 문장이 붙습니다. 사서에 적힌 일을 바탕으로 했고, 연의나 민간 전승에만 나오는 사람 · 일은 그렇다고 적었습니다.</p>' +
  '<h3>영상</h3><p>제목 화면의 그림이 움직이고, 새 판을 시작할 때와 판이 끝날 때(천하통일 · 패망) 짧은 영상이 나옵니다. <b>화면을 누르면 건너뜁니다.</b> 메뉴의 <b>영상</b>에서 끌 수 있고, 기기에서 「동작 줄이기」를 켜 두었으면 나오지 않습니다. 소리는 없습니다(음악이 그대로 흐릅니다).</p>' +
  '<h3>가늠 — 확률을 말로</h3><p>성공할 가능성은 숫자 대신 <b>매우 높음 · 높음 · 반반 · 낮음 · 매우 낮음</b>과 눈금 다섯 칸으로 보입니다. 가늠하는 이는 군사와 군주 가운데 지력이 높은 쪽입니다 — 그 지력이 ' + ODDS_FINE + ' 미만이면 <b>높은 듯 · 반반인 듯 · 낮은 듯</b> 셋으로만 어림합니다.</p><p><b>싸움터에서는 그 부대의 부장이 헤아립니다</b>(부장이 없으면 주장이 스스로). 부장의 <b>지력</b>이 높을수록 계략이 통할지(○ ×)를 잘 맞히고 가능성을 또렷이 보며, <b>통솔</b>이 높을수록 예상 피해를 정확히 내다보고(통솔 ' + STAFF.errAt + ' 이상이면 그대로 · 낮으면 \'약 N\'이 실제와 벌어집니다) 어느 수가 가장 나은지를 바르게 짚습니다. 적을 고르면 뜨는 단추 가운데 <i class="rec" style="position:static;display:inline-flex;transform:none">薦</i>이 붙은 것이 <b>부장이 권하는 수</b>입니다(주는 피해에서 받는 반격을 뺀 기대값이 가장 큰 것 — 헤아림이 모자란 부장은 가끔 다른 수를 권합니다). 숫자로 보고 싶으면 <b>메뉴 → 확률 표시</b>. 어느 쪽으로 보든 규칙의 확률은 같습니다.</p>' +
  '<h3>충성과 인연</h3><p>군주와 <b>인연</b>(의형제·혈연·부부·인척·심복)이 있는 무장은 충성이 100이고 내려가지 않습니다 — 무장 창의 충성 옆에 그 사이가 적혀 있습니다. 포로가 되어도 주군의 세력이 남아 있는 한 등용에 거의 응하지 않습니다. 그 밖의 무장은 군주의 매력에 따라 80~98 사이에 자리를 잡습니다. 새로 등용한 무장은 70~85에서 시작해 분기마다 2씩 오르고, 포상으로 올린 충성은 천천히 제자리로 돌아옵니다.</p>' +
  '<h3>닫기(×)와 뒤로 가기</h3><p><b>×는 한 단계만 뒤로</b> 갑니다. 무장 정보를 닫으면 보던 목록으로, 무장 고르는 표를 닫으면 그 앞 창으로 돌아갑니다. 부대에서 대상이나 행군을 고르던 중이면 그것만 물립니다. 막 출진한 부대의 창을 닫으면 나온 성의 출진 탭으로 돌아갑니다.</p>' +
  '<p>목록·기록·지난 열흘의 일에서 줄을 눌러 지도로 건너뛰면 왼쪽 위에 <b>‹ 목록</b> 같은 단추가 생깁니다. 누르면 보던 자리 그대로 다시 열립니다. 그렇게 열린 거점·부대 창은 ×로도 목록에 돌아갑니다.</p>' +
  '<h3>조작</h3><p>끌어서 지도를 옮기고, 두 손가락으로 확대·축소합니다. 오른쪽 위 작은 지도를 누르면 그곳으로 건너뜁니다. 거점 이름표의 붉은 낙관 숫자는 아직 일하지 않은 무장 수입니다. 부대 이름표에는 주장의 얼굴이 붙습니다.</p>' +
  '<h3>지형</h3><p>먹으로 짙게 그린 <b>산</b>과 바다 · 변경은 지나갈 수 없고, 그런 칸에는 <b>칸 줄이 없습니다</b>. 칸 줄이 보이는 곳은 모두 갈 수 있는 땅입니다. 빈 땅을 누르면 지형과 높이가 뜹니다.</p><p><b>높낮이 읽는 법</b> — 땅이 높을수록 <b>누런빛(대자빛)이 한 겹씩 짙어지고</b>, 겹이 바뀌는 곳에 가는 먹선(등고선)이 그어져 있습니다. 한 겹은 높이 3단 — 싸움에서 치는 높이 차의 끝(±' + Math.round(ELEV_K.step * ELEV_K.max * 100) + '%)입니다. 선 하나를 넘어 위에서 치면 높은 곳의 덕을 다 봅니다. <b>강 · 호수 · 바다는 쪽빛</b>입니다.</p><ul>' +
  '<li><b>높낮이</b> — 칸마다 높이가 있습니다. 치는 칸이 맞는 칸보다 한 단 높을 때마다 주는 피해 <b>+' + Math.round(ELEV_K.step * 100) + '%</b>, 낮을 때마다 −' + Math.round(ELEV_K.step * 100) + '% (' + ELEV_K.max + '단까지). 반격에도 같습니다 — 높은 곳을 차지하면 덜 맞고 더 세게 받아칩니다.</li>' +
  '<li><b>숲 · 구릉</b> — 이동이 느립니다. 그 위의 부대는 받는 피해 −15%. 숲 속의 부대를 화살로 쏘면 −15% 더. 숲에서는 기병 전법을 쓸 수 없고 불이 번집니다.</li>' +
  '<li><b>기병</b> — 평지에서 평지의 적을 치면 +10%. 숲 · 구릉에서 치거나 숲 · 구릉의 적을 치면 −15%.</li>' +
  '<li><b>강</b> — 건너는 데 이동력이 많이 듭니다(나루는 덜). 물 위에서는 공격 −30%, 받는 피해 +20%.</li>' +
  '<li>부대 창에 선 칸의 지형과 높이가, 적 부대를 고르면 대상 창에 <b>그 싸움에 걸리는 지형의 값</b>이 적힙니다. 예상 피해에는 이미 들어 있습니다.</li></ul>' +
  '<h3>지도</h3><p>실제 지형(고도·강·해안)과 거점의 실제 위치를 바탕으로 만들었습니다. 한 칸은 약 ' + MAPDATA.km + 'km입니다. 황하 하류는 후한 때의 물길을 따릅니다. 바탕 그림은 지도 전체가 한 장이라, 가장 크게 당기면 붓자국이 먹이 번진 듯 부드럽게 보입니다.</p>' +
  '<h3>일기토</h3><p>무력 ' + DUEL_K.minWar + ' 이상의 주장끼리 붙어 싸우면 낮은 확률로 일기토가 벌어집니다. 옆의 적 부대를 누르고 <b>일기토</b>를 눌러 직접 걸 수도 있습니다(기력 ' + DUEL_K.ask + ' · 응하지 않으면 상대 기력 -' + DUEL_K.refuse + '). 약한 상대일수록 응하지 않습니다.</p>' +
  '<p><b>AI 도 일기토를 걸어옵니다</b> — 주장의 무력이 ' + DUEL_K.aiMinWar + ' 이상이고 상대보다 ' + (-DUEL_K.aiLead) + ' 넘게 처지지 않을 때(' + DUEL_K.aiAsk + '%). 내 부대에 걸어오면 [지금 할 일]에 뜨고 내 차례에 답합니다: <b>받아들이면</b> 합마다 수를 직접 고르며 겨루고, <b>받지 않으면</b> 내 부대의 기력이 ' + DUEL_K.refuse + ' 내립니다(답하지 않고 턴을 넘겨도 같습니다). 두 부대가 떨어지면 없던 일이 됩니다.</p>' +
  '<p>합마다 수를 하나 고릅니다 — <b>맹공</b>은 필살을 이기고, <b>필살</b>은 방어를 부수며(피해 1.6배), <b>방어</b>는 맹공을 받아칩니다. 피해는 두 사람의 무력 차로 정해지고, 합을 이기면 기세가 올라 더 세게 칩니다. 화면의 <b>기색</b>은 상대가 낼 수의 낌새입니다(맞을 확률이 적혀 있습니다 — 지력이 높을수록 잘 읽습니다). ' + DUEL_K.rounds + '합 안에 쓰러뜨리지 못하면 남은 힘으로 판정합니다.</p>' +
  '<p>진 부대는 기력 -' + DUEL_K.morLose + ' · 병력 -' + Math.round(DUEL_K.loss * 100) + '%, 쓰러졌으면 기력 -' + DUEL_K.koMor + ' · 병력 -' + Math.round(DUEL_K.koLoss * 100) + '% · 혼란. AI끼리의 일기토와 내 군단의 일기토는 같은 규칙으로 저절로 판정됩니다.</p>' +
  '<h3>설전</h3><p>등용할 때 보낼 무장을 고르고 <b>설전</b>을 누르면 주사위 대신 말로 겨룹니다(등용 확률 ' + DUEL_K.talkMin + '% 이상일 때). <b>도리</b>는 이해를, <b>이해</b>는 시세를, <b>시세</b>는 도리를 이깁니다. 피해는 지력 차로 정해지고, 응할 마음이 적은 상대일수록 오래 버팁니다. 이기면 합류하고, 지거나 비기면 거절한 것과 같습니다.</p>' +
  '<h3>외교</h3><p>거점 창의 [인재] 탭 → <b>[외교]</b>. 사신은 그 거점의 쉬는 무장이고, 금도 그 거점에서 나갑니다.</p><ul>' +
  '<li><b>우호</b>(0~100, 처음 ' + DIP_K.rel0 + ') — 세력 사이의 값입니다. <b>친선</b>(금 ' + DIP_K.giftGold + ' · 행동력 ' + AP.gift + ')으로 ' + DIP_K.giftBase + ' + 사신의 정치 ÷ ' + DIP_K.giftPol + '만큼 오르고(한 세력에 턴마다 한 번), 칠 때마다 −' + DIP_K.hitRel + ', 거점을 빼앗으면 −' + DIP_K.fallRel + ' 더, 달마다 ' + DIP_K.rel0 + ' 쪽으로 ' + DIP_K.drift + '씩 돌아갑니다.</li>' +
  '<li><b>정전</b>(' + (DIP_K.truceTurns * 10) + '일) · <b>동맹</b>(' + (DIP_K.allyTurns * 10) + '일, 우호 ' + DIP_K.allyRel + ' 이상) — 맺으면 그동안 서로의 부대 · 거점 · 시설을 칠 수 없고 계략도 걸 수 없으며, 서로의 무장에게 등용을 권하지 않습니다. AI 도 지킵니다.</li>' +
  '<li><b>받아들일 확률</b> = 우호 + 바탕(정전 ' + DIP_K.truceBase + ' · 동맹 ' + DIP_K.allyBase + ') + 사신의 능력(정전은 정치, 동맹은 매력이 70을 넘는 만큼 × ' + DIP_K.envoyK + ') + 힘의 비(우리가 두 배면 +' + DIP_K.powK + ', 저쪽이 두 배면 −' + DIP_K.powK + ') + 저쪽이 다른 세력과 싸우는 중이면 ' + DIP_K.busy + '. 거절당하면 우호 −' + DIP_K.refuse + ', ' + (DIP_K.cool * 10) + '일 뒤에 다시 청할 수 있습니다.</li>' +
  '<li><b>설전으로 담판</b> — 확률이 ' + DIP_K.talkMin + '% 이상이면 주사위 대신 말로 겨룰 수 있습니다. 상대는 저쪽의 군사(없으면 지력이 가장 높은 무장)이고, 받아들일 마음이 적을수록 오래 버팁니다.</li>' +
  '<li><b>파기</b> — 그 세력과의 우호 −' + DIP_K.breakRel + ', 다른 모든 세력과의 우호 −' + DIP_K.breakOthers + ', ' + (DIP_K.breakCool * 10) + '일 동안 그 세력에 다시 청하지 못합니다. 깨는 순간부터 서로 칠 수 있습니다.</li>' +
  '<li>AI 세력이 달이 바뀔 때 <b>정전 · 동맹을 청해 오기도</b> 합니다(약하거나 다른 싸움에 바쁜 세력, 우호가 높은 세력). [지금 할 일]에 뜨고, 그 턴 안에 답해야 합니다.</li>' +
  '<li><b>출병 요청</b>(행동력 ' + AP.treaty + ') — <b>동맹</b>에게 그 동맹과 이웃한 세력 하나를 쳐 달라고 청합니다. 받아들이면 ' + (DIP_K.aimTurns * 10) + '일 동안 그 세력을 먼저 노립니다(우리 성에 원군이 들어오는 것은 아닙니다). 받아들일 확률 = 우호 + 바탕 ' + DIP_K.aimBase + ' + 사신의 매력(70을 넘는 만큼 × ' + DIP_K.envoyK + ') + 힘의 비 + 둘이 이미 싸우는 사이면 ' + DIP_K.aimWar + '. 거절당하면 우호 −' + DIP_K.aimRefuse + ', ' + (DIP_K.aimCool * 10) + '일 뒤에 다시.</li>' +
  '<li><b>AI 끼리도 손을 잡습니다</b> — 병력이 ' + DIP_K.threat + '배 이상인 같은 이웃을 둔 세력끼리 달이 바뀔 때 ' + DIP_K.aiPact + '%로 정전하고, 정전 중이면 ' + DIP_K.aiPactUp + '%로 동맹으로 올립니다. 외교 창의 세력마다 누구와 협정을 맺었는지 적혀 있습니다.</li></ul>' +
  '<h3>소리</h3><p><b>음성</b> — 무장이 중국어로 한마디 합니다(출진 · 공격 · 전법 · 대성공 · 실패 · 적 부대 궤멸 · 함락 · 퇴각 · 일기토 · 계략 · 명령 · 등용). 목소리는 다섯 갈래입니다: 맹장(무력 88 이상 · 지력 72 미만) · 군주 · 지장(무력 70 미만) · 무장 · 여장. 싸움에서는 내가 낀 싸움에만 나오고, 칸 위에 뜻이 잠깐 뜹니다. 메뉴의 [음성]으로 끌 수 있고, 효과음을 끄면 함께 꺼집니다.</p><p>효과음과 음악은 메뉴에서 따로 끌 수 있습니다. 음악은 형편에 따라 바뀝니다 — 평시에는 두 곡이 번갈아 나오고, 다른 세력의 부대가 가까이 오면 긴장된 곡으로, 싸움이 벌어지면 전투 곡으로 넘어갑니다.</p>' +
  '<h3>저장</h3><p>턴이 끝날 때와 화면을 떠날 때 저절로 저장됩니다(<b>자동</b>) — 제목 화면의 <b>이어하기</b>가 이것을 엽니다. 메뉴의 <b>저장</b>에서 번호 칸 ' + SAVE_SLOTS + '개에 따로 남길 수 있고(찬 칸은 한 번 더 눌러 덮어씁니다), <b>불러오기</b>에서 골라 엽니다. 새 게임을 시작하거나 다른 칸을 불러오면 하던 판은 <b>직전</b> 칸에 한 번 남습니다. 저장은 이 기기의 이 주소에만 남습니다.</p>' +
  '<h3>긴 창</h3><p>창이나 아래 판의 내용이 화면보다 길면 아래 끝에 <b>둥근 큰 화살표</b>가 뜹니다. 밀어 올리거나 그 화살표를 누르면 내려갑니다.</p><h3>성의 내구 막대</h3><p>지도의 성 이름표 아래에 <b>내구 막대</b>가 있습니다 — 가득하면 종이 빛, 60% 아래로 누런빛, 30% 아래로 붉은빛입니다.</p><h3>이동과 등용의 창</h3><p><b>이동</b>(인재 → 이동): 보낼 곳을 목록에서 누르거나, <b>지도에서 우리 성을 눌러</b> 고른 뒤 [보낸다]. 지도에는 성마다 이름과 걸리는 날수가 뜹니다. 길을 떠난 무장의 상태에는 가는 곳이 적힙니다(허창으로 이동 중). <b>등용</b>: 위의 <b>정렬</b> 줄로 가능성 · 능력(다섯 능력치의 합) · 통솔 · 무력 · 지력 · 정치 · 매력 · 병종 적성(창 · 극 · 노 · 기 · 병기) 순으로 볼 수 있습니다.</p><h3>공유</h3><p>제목 화면과 메뉴의 <b>공유</b>를 누르면 주소와 QR이 적힌 창이 열립니다(<b>보내기</b>로 휴대폰의 공유 창). 주소만 보내면 받는 사람은 새 게임으로 시작합니다.</p><p><b>하던 판을 보내려면</b> 같은 창의 <b>세이브 파일 보내기</b>에서 판을 고르세요 — 공유 창에 파일로 싣거나, 파일로 저장하거나, 글자로 복사할 수 있습니다. 받는 사람은 <b>불러오기 → 파일에서 가져오기</b>(복사해 받았으면 <b>붙여넣기로 가져오기</b>)로 빈 저장 칸에 넣고 불러옵니다.</p>' +
  '<h3>앱으로 설치</h3><p>휴대폰 브라우저에서 <b>aaronkyung-a11y.github.io/chunhado</b> 를 열면 제목 화면에 <b>앱으로 설치</b> 단추가 나옵니다(안 나오면 브라우저 메뉴의 <b>홈 화면에 추가</b>). 설치하면 앱처럼 전체 화면으로 열리고, 한 번 연 뒤에는 인터넷이 없어도 됩니다. 저장은 여는 곳마다 따로라서, 다른 주소에서 하던 판은 넘어오지 않습니다.</p>' +
  '<h3>무장이 묶이는 일</h3><p>대부분의 명령은 그 턴에 끝나서, 맡은 무장은 다음 턴에 다시 쓸 수 있습니다. <b>시설 건설</b>만은 여러 턴이 걸리고, 맡은 무장은 <b>완공될 때까지</b> 다른 명령도 출진도 이동도 못 합니다(무장 목록에 "○○ 건설 중"). 급하면 그 시설을 눌러 <b>공사 중단</b>을 하면 풀려납니다 — 들인 금은 돌아오지 않습니다. 성이 함락되면 짓다 만 시설은 버려집니다.</p>' +
  '<h3>이번 판에 아직 없는 것</h3><p>기교·능력 연구, 진·요새 같은 야전 시설, 항구와 수군은 다음 판에서 넣습니다.</p></div>';
/* 도움말은 제목만 보이게 접어 둔다(v0.9.2) — 누른 토막만 펼쳐진다 */
function helpSections() {
  var body = HELP_HTML.replace(/^<div class="help">/, '').replace(/<\/div>$/, ''), parts = body.split('<h3>'), h = '<div class="help acc">';
  for (var i = 1; i < parts.length; i++) { var k = parts[i].indexOf('</h3>'); h += '<details><summary>' + parts[i].slice(0, k) + '</summary>' + parts[i].slice(k + 5) + '</details>'; }
  return h + '</div>';
}
function showHelp() { showDialog({ render: function () { return dlgHead('도움말') + '<div class="dlg-b">' + helpSections() + '</div>'; }, on: {} }, true); }
/* ---------- 공유(v0.11) ----------
   보내는 주소: 앱(깃허브 페이지 등 manifest 가 있는 빌드)으로 열려 있으면 지금 그 주소, Claude 아티팩트 안처럼 남이 열 수 없는 곳이면 SHARE_URL.
   휴대폰의 공유 창(navigator.share)을 먼저 쓰고, 없거나 막혀 있으면 주소·QR이 적힌 창을 연다. */
function shareUrl() {
  try { if (document.querySelector('link[rel="manifest"]') && /^https?:$/.test(location.protocol) && !/^(localhost|127\.|\[::1\])/.test(location.host)) return location.origin + location.pathname.replace(/index\.html$/, ''); } catch (e) { /* */ }
  return SHARE_URL;
}
function qrSvg(rows) {
  var n = rows.length, q = 3, d = '';
  for (var y = 0; y < n; y++) { var v = parseInt(rows[y], 16); for (var x = 0; x < n; x++) if (Math.floor(v / Math.pow(2, n - 1 - x)) % 2) d += 'M' + (x + q) + ' ' + (y + q) + 'h1v1h-1z'; }
  return '<svg class="qr" viewBox="0 0 ' + (n + 2 * q) + ' ' + (n + 2 * q) + '" shape-rendering="crispEdges" role="img" aria-label="주소 QR"><rect width="100%" height="100%" fill="#fff"/><path d="' + d + '" fill="#111"/></svg>';
}
function copyText(txt, el) {                               // 복사: 새 방식 → 옛 방식(입력 칸을 골라 execCommand) → 안 되면 false
  var ok = false;
  try { if (el) { el.focus(); el.select(); el.setSelectionRange(0, txt.length); ok = document.execCommand('copy'); } } catch (e) { ok = false; }
  if (!ok) { try { if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(txt).then(function () { toast('주소를 복사했습니다'); }, function () { toast('복사가 막혀 있습니다 — 주소를 길게 눌러 복사하세요', 3200); }); return true; } } catch (e2) { /* */ } }
  return ok;
}
function showShare() {
  var url = shareUrl();
  showDialog({
    render: function () {
      return dlgHead('공유') + '<div class="dlg-b shr"><p>이 주소를 보내면 누구나 바로 할 수 있습니다 — 설치 없이 브라우저에서 열리고, 휴대폰이면 앱으로 설치할 수도 있습니다.</p>' +
        '<input class="shurl" id="shU" type="text" readonly value="' + url + '">' +
        '<div class="cmds ' + (navigator.share && !inClaude() ? 'c2' : 'c1') + '"><button class="cmd pri" type="button" data-a="copy"><b>주소 복사</b></button>' + (navigator.share && !inClaude() ? '<button class="cmd" type="button" data-a="send"><b>보내기</b><small>앱 고르기</small></button>' : '') + '</div>' +
        (url === SHARE_URL ? '<div class="qrw">' + qrSvg(SHARE_QR) + '<small>옆 사람은 카메라로 QR을 비추면 됩니다</small></div>' : '') +
        '<h3 class="shh">하던 판 보내기</h3><p>주소만 보내면 받는 사람은 새 게임으로 시작합니다. 하던 판을 이어서 하게 하려면 세이브 파일을 함께 보내세요.</p>' +
        '<div class="cmds c1"><button class="cmd" type="button" data-a="savesend"><b>세이브 파일 보내기</b><small>보낼 판 고르기</small></button></div></div>';
    },
    on: {
      copy: function () { if (copyText(url, $('shU'))) toast('주소를 복사했습니다'); else toast('복사가 막혀 있습니다 — 주소를 길게 눌러 복사하세요', 3200); },
      send: function () { shareSend(url, true); },
      savesend: function () { showSaveSend(); }
    }
  }, true);
}
function shareSend(url, quiet) {
  try {
    navigator.share({ title: '삼국지 천하도', text: '삼국지 천하도 — 수묵 지도 위의 삼국지 전략 게임', url: url }).then(function () { /* 보냈다 */ }, function (e) {
      if (e && e.name === 'AbortError') return;                    // 사용자가 공유 창을 닫았다
      if (quiet) toast('이 화면에서는 공유 창을 열 수 없습니다 — 주소를 복사해 보내세요', 3200); else showShare();
    });
    return true;
  } catch (e) { return false; }
}
function shareGame() { showShare(); }                          // v0.12: 늘 창을 먼저 연다(주소 · 세이브 파일 가운데 고른다)
/* ---------- 세이브 파일 보내기 · 가져오기(v0.12) ---------- */
function saveFileName(m) { return '천하도_' + m.f + '_' + String(m.d).replace(/\s+/g, '') + '.txt'; }
/* 칸의 저장본 → 보낼 글(머리말 두 줄 + 저장본). 비었거나 열 수 없는 칸이면 null */
function saveFileText(id) {
  var sv = lsGet(slotKey(id)), m = slotInfo(id); if (!sv || !m || m.bad) return null;
  return { name: saveFileName(m), meta: m, text: '삼국지 천하도 세이브 — ' + m.f + ' · ' + m.d + ' · ' + m.n + '성 · ' + fmt(m.tr) + '명 (' + GAME_VERSION + ')\n여는 법: ' + SHARE_URL + ' → 불러오기 → 파일에서 가져오기\n' + sv + '\n' };
}
/* Claude 아티팩트 안인가(v0.12.1). 그곳에서는 공유 창과 페이지가 시작하는 내려받기가 막혀 있고, 파일은 downloads 기능으로만 내보낼 수 있다.
   DLCAP: undefined = 아직 묻지 않음 · 0 = 묻는 중 · null = 쓸 수 없음 · 객체 = downloads(그 save 를 부른다) */
var DLCAP;
function inClaude() { try { return !!(window.claude && typeof window.claude.use === 'function'); } catch (e) { return false; } }
function dlCapAsk(cb) {
  if (DLCAP !== undefined) return;
  if (!inClaude()) { DLCAP = null; return; }
  DLCAP = 0;
  var done = function (ns) { DLCAP = ns && typeof ns.save === 'function' ? ns : null; if (cb) cb(); };
  try { window.claude.use('downloads').then(done, function () { done(null); }); } catch (e) { done(null); }
}
function saveFileObj(p) { try { return new File([p.text], p.name, { type: 'text/plain' }); } catch (e) { return null; } }
function canShareFile(f) { try { return !!(f && navigator.share && navigator.canShare && navigator.canShare({ files: [f] })); } catch (e) { return false; } }
function saveDownload(p) {
  try {
    var url = URL.createObjectURL(new Blob([p.text], { type: 'text/plain' })), a = document.createElement('a');
    a.href = url; a.download = p.name; a.style.display = 'none'; document.body.appendChild(a); a.click();
    setTimeout(function () { if (a.parentNode) a.parentNode.removeChild(a); URL.revokeObjectURL(url); }, 1500);
    return true;
  } catch (e) { return false; }
}
function copyLong(txt, okMsg) {                                 // 긴 글 복사: 새 방식 → 옛 방식(숨긴 칸을 골라 execCommand)
  function old() {
    var ok = false, ta = document.createElement('textarea');
    try { ta.value = txt; ta.setAttribute('readonly', ''); ta.style.cssText = 'position:fixed;left:0;top:0;width:1px;height:1px;opacity:0'; document.body.appendChild(ta); ta.focus(); ta.select(); ta.setSelectionRange(0, txt.length); ok = document.execCommand('copy'); } catch (e) { ok = false; }
    if (ta.parentNode) ta.parentNode.removeChild(ta);
    toast(ok ? okMsg : '복사가 막혀 있습니다 — [파일로 저장]을 써 보세요', ok ? 2000 : 3200);
  }
  try { if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(txt).then(function () { toast(okMsg); }, old); return; } } catch (e) { /* */ }
  old();
}
function saveRowHtml(id, m, btn) {
  return '<div class="row" data-slot="' + id + '"><i class="svn' + (id.charAt(0) === 's' ? '' : ' au') + '">' + slotName(id) + '</i><span class="mid"><span class="nm"><span class="chip" style="background:' + m.c + '">' + m.f + '</span> ' + m.d + '</span>' +
    '<span class="ds">' + m.n + '성 · ' + fmt(m.tr) + '명' + (m.t ? ' · ' + saveWhen(m.t) : '') + '</span></span>' + (btn || '') + '</div>';
}
function showSaveSend() {
  if (inGame() && !UI.play) saveGame();                          // 지금 모습을 자동 저장에 먼저 적는다 — '자동' 칸이 곧 지금 하는 판이다
  var st = { id: '' }, game = inGame(), dlg;
  dlCapAsk(function () { if (MODAL === dlg) refreshDialog(); });
  showDialog(dlg = {
    render: function () {
      var h = dlgHead('세이브 파일 보내기') + '<div class="dlg-b shr">', p = st.id ? saveFileText(st.id) : null;
      if (!p) {
        var ids = slotIds(), n = 0, rows = '';
        for (var i = 0; i < ids.length; i++) { var m = slotInfo(ids[i]); if (!m || m.bad) continue; n++; rows += saveRowHtml(ids[i], m, '<button class="btn" type="button" data-a="spick" data-v="' + ids[i] + '">고르기</button>'); }
        h += n ? '<p>보낼 판을 고르세요.' + (game ? ' <b>자동</b> = 지금 하는 판.' : '') + '</p><div class="rows svl">' + rows + '</div>' : '<p class="note">저장된 판이 없습니다 — 게임을 시작하면 턴마다 자동으로 저장됩니다.</p>';
      } else {
        var kb = Math.max(1, Math.round(p.text.length / 1024)), inC = inClaude(), can = !inC && canShareFile(saveFileObj(p)), fileBtn;
        if (!inC) fileBtn = '<button class="cmd' + (can ? '' : ' pri') + '" type="button" data-a="sdown"><b>파일로 저장</b><small>' + p.name + ' · 약 ' + kb + 'KB</small></button>';
        else if (DLCAP) fileBtn = '<button class="cmd pri" type="button" data-a="sdown"><b>파일로 내보내기</b><small>저장하거나 다른 앱으로 보냅니다 · 약 ' + kb + 'KB</small></button>';
        else fileBtn = DLCAP === 0 ? '<button class="cmd" type="button" disabled><b>파일로 내보내기</b><small>준비하는 중…</small></button>' : '';
        h += '<div class="rows svl">' + saveRowHtml(st.id, p.meta, '<button class="btn" type="button" data-a="sback">다른 판</button>') + '</div>' +
          '<div class="cmds c1">' + (can ? '<button class="cmd pri" type="button" data-a="sshare"><b>보내기</b><small>앱 고르기 · 파일로 갑니다</small></button>' : '') +
          fileBtn +
          '<button class="cmd" type="button" data-a="scopy"><b>글자로 복사</b><small>붙여 넣어 보낼 때 · 글이 깁니다</small></button></div>' +
          '<p class="note">받는 사람: 게임을 열고 <b>불러오기 → 파일에서 가져오기</b>(복사해 보냈으면 <b>붙여넣기로 가져오기</b>).' + (inC ? (DLCAP === null ? ' <b class="bad">이 화면에서는 파일로 내보낼 수 없습니다</b> — [글자로 복사]를 쓰거나 앱 주소(' + SHARE_URL + ')에서 여세요.' : '') : (can ? '' : ' 이 화면에서는 공유 창에 파일을 실을 수 없어 저장 · 복사만 됩니다.')) + '</p>';
      }
      return h + '</div>';
    },
    on: {
      spick: function (el) { st.id = el.getAttribute('data-v'); refreshDialog(); },
      sback: function () { st.id = ''; refreshDialog(); },
      sshare: function () {
        var p = saveFileText(st.id), f = p ? saveFileObj(p) : null; if (!canShareFile(f)) { toast('이 화면에서는 파일을 공유 창에 실을 수 없습니다 — [파일로 저장]을 쓰세요', 3200); return; }
        try { navigator.share({ files: [f], title: '삼국지 천하도 세이브', text: '삼국지 천하도 세이브(' + p.meta.f + ' · ' + p.meta.d + ') — ' + SHARE_URL + ' 에서 불러오기 → 파일에서 가져오기' }).then(function () { /* 보냈다 */ }, function (e) { if (!(e && e.name === 'AbortError')) toast('공유 창을 열지 못했습니다 — [파일로 저장]을 쓰세요', 3200); }); }
        catch (e) { toast('공유 창을 열지 못했습니다 — [파일로 저장]을 쓰세요', 3200); }
      },
      sdown: function () {
        var p = saveFileText(st.id); if (!p) return;
        if (inClaude()) {                                           // 아티팩트 안: downloads 기능으로(보는 사람이 확인해야 저장된다)
          var no = function () { toast('파일을 내보내지 못했습니다 — [글자로 복사]를 쓰세요', 3200); };
          if (!DLCAP) return no();
          try { DLCAP.save({ filename: p.name, data: p.text }).then(function () { toast('파일을 내보냈습니다', 2400); }, function (e) { var c = e && e.code; if (c === 'declined') return; if (c === 'rate_limited') toast('잠시 뒤에 다시 눌러 주세요', 2400); else no(); }); } catch (e) { no(); }
          return;
        }
        if (saveDownload(p)) toast('파일로 내보냈습니다 — 내려받은 파일을 보내면 됩니다', 2800); else toast('이 화면에서는 파일을 내보낼 수 없습니다 — [글자로 복사]를 쓰세요', 3200);
      },
      scopy: function () { var p = saveFileText(st.id); if (p) copyLong(p.text, '세이브를 복사했습니다'); }
    }
  }, true);
}
/* 저장본의 뼈대가 이 판의 지도 · 세력 · 병과와 맞는가(deserialize 는 너그러워서 뼈대가 어긋난 글도 받아들인다 — 그런 판은 열고 나서 멈춘다) */
function saveShapeOk(g) {
  function num(v) { return typeof v === 'number' && isFinite(v); }
  var i, j, nf = g.factions.length, no = g.officers.length;
  if (!num(g.year) || !num(g.month) || !(g.xun === 0 || g.xun === 1 || g.xun === 2) || g.turn < 0 || g.player < 0 || g.player >= nf) return false;
  if (g.bases.length > MAPDATA.bases.length || g.bases.length < BASES_OLD || nf !== SCENARIO.factions.length || no < 1) return false;      // v0.20: 옛 저장은 거점이 적다(홍농이 없다) — 열 때 덧붙인다
  for (i = 0; i < nf; i++) { var f = g.factions[i]; if (!f || typeof f.name !== 'string' || !f.name) return false; }
  for (i = 0; i < no; i++) { var o = g.officers[i]; if (!o || typeof o.n !== 'string' || !num(o.f) || o.f < -1 || o.f >= nf || !num(o.ldr) || !num(o.war) || !num(o.int) || !num(o.pol) || !num(o.cha)) return false; }
  for (i = 0; i < g.bases.length; i++) {
    var b = g.bases[i]; if (!b || b.n !== MAPDATA.bases[i].n || !num(b.owner) || b.owner < -1 || b.owner >= nf || !num(b.troops) || b.troops < 0 || !num(b.gold) || !num(b.food) || !num(b.dur) || !b.w || typeof b.w !== 'object') return false;
    if (b.plots !== undefined && !Array.isArray(b.plots)) return false;
    for (j = 0; b.plots && j < b.plots.length; j++) { var p = b.plots[j]; if (!p || !num(p.c) || !num(p.r) || (p.fac && !FAC[p.fac.t])) return false; }
  }
  for (i = 0; i < g.units.length; i++) {
    var u = g.units[i]; if (!u || !num(u.f) || u.f < 0 || u.f >= nf || !num(u.c) || !num(u.r) || !inMap(u.c, u.r) || !UNIT_TYPES[u.type] || !num(u.troops) || !Array.isArray(u.off) || !u.off.length) return false;
    for (j = 0; j < u.off.length; j++) if (!num(u.off[j]) || u.off[j] < 0 || u.off[j] >= no) return false;
  }
  return true;
}
/* 열어 본다(하던 판은 그대로 둔다). 열린 뒤 화면이 처음에 쓰는 것들도 한 번 불러 본다 */
function saveProbe(sv) {
  var g0 = G, r0 = REPORT, e0 = EVQ, j0 = JOT, ok = false;
  try { ok = deserialize(sv); if (ok) { facBases(G.player); G.units.forEach(function (u) { uLeader(u); uName(u); }); saveMetaOf(G, sv.length); serialize(); } } catch (e) { ok = false; }
  G = g0; REPORT = r0; EVQ = e0; JOT = j0; if (g0) reindex();
  return ok;
}
/* 받은 글 → { ok, s: 저장본, meta } 또는 { ok: false, why }. 남이 보낸 파일이므로 꼼꼼히 본다(머리말은 이 파일의 p3 에) */
function saveParse(txt) {
  function bad(w) { return { ok: false, why: w }; }
  if (typeof txt !== 'string' || !txt.replace(/\s+/g, '')) return bad('내용이 비어 있습니다');
  if (txt.length > 6e6) return bad('파일이 너무 큽니다');
  var a = txt.indexOf('{"'), z = txt.lastIndexOf('}'), g = null;
  if (a < 0 || z < a) return bad('천하도의 세이브 파일이 아닙니다');
  try { g = JSON.parse(txt.slice(a, z + 1)); } catch (e) { return bad('세이브가 중간에 끊겼거나 깨졌습니다'); }
  if (!g || g.ver !== 2 || !Array.isArray(g.factions) || !Array.isArray(g.officers) || !Array.isArray(g.bases) || !Array.isArray(g.units) || !Array.isArray(g.log) || typeof g.player !== 'number' || typeof g.turn !== 'number' || !g.factions[g.player]) return bad('천하도의 세이브 파일이 아닙니다');
  var clean = true, n = 0, i;
  (function walk(o, d) {
    if (!clean) return;
    if (typeof o === 'string') { if (o.length > 600 || /[<>"]/.test(o)) clean = false; return; }
    if (o && typeof o === 'object') { if (d > 14 || ++n > 400000) { clean = false; return; } for (var k in o) { if (/[<>"]/.test(k)) { clean = false; return; } walk(o[k], d + 1); } }
  })(g, 0);
  for (i = 0; clean && i < g.factions.length; i++) if (!g.factions[i] || !/^#[0-9a-fA-F]{3,8}$/.test(String(g.factions[i].color))) clean = false;
  if (!clean) return bad('알 수 없는 내용이 들어 있어 받지 않았습니다');
  if (!saveShapeOk(g)) return bad('이 판에서는 열 수 없는 세이브입니다');
  var sv = JSON.stringify(g);
  if (!saveProbe(sv)) return bad('이 판에서는 열 수 없는 세이브입니다');
  var m = saveMetaOf(g, sv.length); m.t = Date.now();
  return { ok: true, s: sv, meta: m };
}
function firstEmptySlot() { for (var i = 1; i <= SAVE_SLOTS; i++) if (!lsGet(slotKey('s' + i))) return 's' + i; return ''; }
function saveImportTo(id, res) {
  var ok = slotWrite(id, res.s, res.meta);
  toast(ok ? slotLabel(id) + '에 넣었습니다 — ' + res.meta.f + ' · ' + res.meta.d : (canStore() ? '넣지 못했습니다 — 저장 공간이 모자랍니다(안 쓰는 칸을 지워 주세요)' : '이 환경에서는 저장할 수 없습니다'), ok ? 2600 : 3400);
  titleBtns(); return ok;
}
/* 받은 글을 저장 칸에 넣는다: 빈 번호 칸이 있으면 거기, 없으면 덮어쓸 칸을 고르게 한다. done = 넣은 뒤 할 일 */
function flowImport(txt, done) {
  var res = saveParse(txt);
  if (!res.ok) { toast(res.why, 3600); return; }
  var id = firstEmptySlot();
  if (id) { saveImportTo(id, res); if (done) done(); return; }
  var arm = '';
  showDialog({
    render: function () {
      var h = dlgHead('넣을 칸 고르기') + '<div class="dlg-b"><p>빈 칸이 없습니다. 받은 판(<b>' + res.meta.f + ' · ' + res.meta.d + '</b>)으로 덮어쓸 칸을 고르세요.</p><div class="rows svl">';
      for (var i = 1; i <= SAVE_SLOTS; i++) { var sid = 's' + i, m = slotInfo(sid); if (!m) continue; h += m.bad ? '<div class="row" data-slot="' + sid + '"><i class="svn">' + i + '</i><span class="mid"><span class="nm">열 수 없는 저장</span></span><button class="btn" type="button" data-a="over" data-v="' + sid + '">덮어쓰기</button></div>' : saveRowHtml(sid, m, '<button class="btn' + (arm === sid ? ' pri' : '') + '" type="button" data-a="over" data-v="' + sid + '">' + (arm === sid ? '정말 덮어쓰기' : '덮어쓰기') + '</button>'); }
      return h + '</div></div>';
    },
    on: { over: function (el) { var sid = el.getAttribute('data-v'); if (arm !== sid) { arm = sid; refreshDialog(); return; } var ok = saveImportTo(sid, res); backDialog(); if (ok && done) done(); } }
  }, true);
}
function pickSaveFile(cb) {
  var old = $('svPick'); if (old && old.parentNode) old.parentNode.removeChild(old);
  var inp = document.createElement('input'); inp.type = 'file'; inp.id = 'svPick'; inp.accept = '.txt,.json,text/plain,application/json'; inp.style.cssText = 'position:fixed;left:0;top:0;width:1px;height:1px;opacity:0';
  inp.addEventListener('change', function () {
    var f = inp.files && inp.files[0]; if (inp.parentNode) inp.parentNode.removeChild(inp);
    if (!f) return;
    if (f.size > 6e6) { toast('파일이 너무 큽니다'); return; }
    var rd = new FileReader(); rd.onload = function () { cb(String(rd.result || '')); }; rd.onerror = function () { toast('파일을 읽지 못했습니다'); }; rd.readAsText(f);
  });
  document.body.appendChild(inp); inp.click();
}
function showSavePaste(done) {
  showDialog({
    render: function () {
      return dlgHead('붙여넣기로 가져오기') + '<div class="dlg-b shr"><p>받은 세이브 글 전체를 아래 칸에 붙여 넣으세요.</p><textarea class="svta" id="svTa" spellcheck="false" placeholder="삼국지 천하도 세이브 — …"></textarea>' +
        '<div class="cmds c2"><button class="cmd" type="button" data-a="clip"><b>붙여넣기</b><small>복사해 둔 글</small></button><button class="cmd pri" type="button" data-a="take"><b>가져오기</b></button></div></div>';
    },
    on: {
      clip: function () {
        var no = function () { toast('붙여넣기가 막혀 있습니다 — 칸을 길게 눌러 붙여 넣으세요', 3200); };
        try { if (navigator.clipboard && navigator.clipboard.readText) navigator.clipboard.readText().then(function (t) { var ta = $('svTa'); if (ta) ta.value = t; }, no); else no(); } catch (e) { no(); }
      },
      take: function () { var ta = $('svTa'), t = ta ? ta.value : ''; if (!t.replace(/\s+/g, '')) { toast('붙여 넣은 글이 없습니다'); return; } backDialog(); flowImport(t, done); }
    }
  }, true);
}
function showMenu() {
  showDialog({
    render: function () {
      return dlgHead('메뉴 — ' + GAME_VERSION) + '<div class="dlg-b"><div class="cmds"><button class="cmd" type="button" data-a="save"><b>저장</b></button><button class="cmd" type="button" data-a="load"><b>불러오기</b></button>' +
        '<button class="cmd" type="button" data-a="talk"><b>대화창 ' + (UI.talk === false ? '꺼짐' : '켜짐') + '</b></button><button class="cmd" type="button" data-a="snd"><b>효과음 ' + (UI.sound ? '켜짐' : '꺼짐') + '</b></button><button class="cmd" type="button" data-a="voi"><b>음성 ' + (UI.voice === false ? '꺼짐' : '켜짐') + '</b><small>' + (UI.sound ? '중국어' : '효과음이 꺼져 있음') + '</small></button><button class="cmd" type="button" data-a="mus"><b>음악 ' + (UI.music ? '켜짐' : '꺼짐') + '</b>' + (UI.music && BGM.mode === 'file' ? '<small>연주곡</small>' : (UI.music && BGM.mode === 'syn' ? '<small>만든 음악</small>' : '')) + '</button><button class="cmd" type="button" data-a="spd"><b>열흘 재생</b><small>' + SPEEDS[UI.pspeed][0] + '</small></button><button class="cmd" type="button" data-a="pct"><b>확률 표시</b><small>' + (UI.pct ? '숫자(%)' : '말로 가늠') + '</small></button><button class="cmd" type="button" data-a="vid"><b>영상 ' + (UI.video === false ? '꺼짐' : '켜짐') + '</b><small>제목 · 오프닝 · 끝</small></button><button class="cmd" type="button" data-a="help"><b>도움말</b></button><button class="cmd" type="button" data-a="share"><b>공유</b></button>' +
        '<button class="cmd" type="button" data-a="title"><b>처음으로</b></button></div><p class="note">턴마다 자동 저장 · 저장 칸 ' + SAVE_SLOTS + '개 · 이 기기에만 남습니다(다른 기기로는 공유 → 세이브 파일 보내기)</p></div>';
    },
    on: {
      save: function () { showSaves('save'); },
      load: function () { showSaves('load'); },
      talk: function () { UI.talk = UI.talk === false; if (UI.talk === false) talkHide(); saveOpts(); toast(UI.talk ? '대화창 켬 — 맡은 무장이 한마디 합니다' : '대화창 끔 — 결과만 알림 줄로', 2000); refreshDialog(); },
      snd: function () { UI.sound = !UI.sound; if (UI.sound) audioInit(); else voiceStop(true); saveOpts(); refreshDialog(); },
      voi: function () { UI.voice = UI.voice === false; if (UI.voice === false) voiceStop(true); saveOpts(); toast(UI.voice ? '음성 켬 — 무장이 중국어로 한마디 합니다' : '음성 끔', 2000); refreshDialog(); },
      mus: function () { UI.music = !UI.music; saveOpts(); if (UI.music) playBgm(bgmForState()); else stopBgm(); refreshDialog(); },
      spd: function () { UI.pspeed = (UI.pspeed + 1) % 4; saveOpts(); toast(UI.pspeed ? '열흘 재생: ' + SPEEDS[UI.pspeed][0] : '열흘 재생 끔 — 요약만', 2000); refreshDialog(); },
      vid: function () { UI.video = UI.video === false; saveOpts(); toast(UI.video ? '영상 켬 — 제목 화면 · 새 판의 오프닝 · 끝' : '영상 끔', 2200); refreshDialog(); },
      pct: function () { UI.pct = !UI.pct; saveOpts(); toast(UI.pct ? '확률을 숫자(%)로 보여 줍니다' : '확률을 말로 가늠해 보여 줍니다 — 높음 · 반반 · 낮음', 2400); refreshDialog(); refreshSheet(); },
      help: function () { showHelp(); },
      share: function () { shareGame(); },
      title: function () { saveGame(); closeDialog(); clearRet(); clearSel(); showTitle(); playBgm('title'); }
    }
  });
}

/* ---------- 저장 ---------- */
function saveOpts() { try { localStorage.setItem('chunhado_opts', JSON.stringify({ sound: UI.sound, music: UI.music, pspeed: UI.pspeed, home: HOME.open, talk: UI.talk !== false, voice: UI.voice !== false, pct: !!UI.pct, tback: !!UI.tback, video: UI.video !== false })); } catch (e) { /* */ } }
function loadOpts() {
  try {
    var o = JSON.parse(localStorage.getItem('chunhado_opts') || '{}');
    if (o.sound === false) UI.sound = false; if (o.music === false) UI.music = false;
    if (o.pspeed >= 0 && o.pspeed <= 3) UI.pspeed = o.pspeed | 0;
    if (o.home === false) HOME.open = false;
    if (o.talk === false) UI.talk = false;
    if (o.voice === false) UI.voice = false;
    if (o.pct === true) UI.pct = true;                         // v0.18: 확률을 숫자로(기본은 말)
    if (o.video === false) UI.video = false;                   // v0.19: 영상 끔
    if (o.tback === true) UI.tback = true;                     // v0.18.1: 수송 창의 '짐을 내린 뒤 돌아온다'
  } catch (e) { /* */ }
}
/* 지금 틀 음악의 장면: 싸운 지 한 턴 안이거나 적이 내 성 코앞이면 전투, 적이 가까이 있으면 긴장, 아니면 평시 */
function bgmForState() {
  if (!G) return 'title';
  if (G.turn - (UI.battleTurn === undefined ? -9 : UI.battleTurn) <= 1) return 'battle';
  var bs = facBases(G.player), us = facUnits(G.player), i, tense = false;
  for (i = 0; i < bs.length; i++) {
    if (enemyUnitsNear(G.player, bs[i].c, bs[i].r, 2).length) return 'battle';
    if (!tense && enemyUnitsNear(G.player, bs[i].c, bs[i].r, 7).length) tense = true;
  }
  for (i = 0; i < us.length && !tense; i++) {
    var z = zoneAt(us[i].c, us[i].r);
    if ((z >= 0 && G.bases[z].owner >= 0 && G.bases[z].owner !== G.player) || enemyUnitsNear(G.player, us[i].c, us[i].r, 4).length) tense = true;   // 남의 성역에 들어섰거나 적 부대가 가깝다
  }
  return tense ? 'tense' : 'field';
}
/* 저장 칸(v0.10.1): 'auto' = 자동 저장(턴마다 · 화면을 떠날 때. 전부터 쓰던 SAVE_KEY 그대로) · 'prev' = 직전 판(새 게임이나 불러오기로 밀려난 판) · 's1'~ = 직접 저장.
   칸마다 요약(세력 · 날짜 · 거점 · 병력 · 저장한 때)을 SAVE_KEY + '_meta' 에 따로 적어 둔다 — 없거나 저장본과 길이가 다르면 저장본을 읽어 다시 만든다. */
function slotKey(id) { return id === 'auto' ? SAVE_KEY : SAVE_KEY + '_' + id; }
function slotIds() { var a = ['auto', 'prev']; for (var i = 1; i <= SAVE_SLOTS; i++) a.push('s' + i); return a; }
function slotName(id) { return id === 'auto' ? '자동' : (id === 'prev' ? '직전' : id.slice(1)); }
function slotLabel(id) { return id === 'auto' ? '자동 저장' : (id === 'prev' ? '직전 판' : id.slice(1) + '번 칸'); }
function lsGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
function lsSet(k, v) { try { localStorage.setItem(k, v); return true; } catch (e) { return false; } }
function lsDel(k) { try { localStorage.removeItem(k); } catch (e) { /* */ } }
function canStore() { if (!lsSet(SAVE_KEY + '_probe', '1')) return false; lsDel(SAVE_KEY + '_probe'); return true; }      // 저장 자체가 되는 환경인가(안 되면 공간이 모자란 것과 구별한다)
function saveMetaOf(g, len) {
  var tr = 0, nb = 0, i;
  for (i = 0; i < g.bases.length; i++) if (g.bases[i].owner === g.player) { nb++; tr += g.bases[i].troops; }
  for (i = 0; i < g.units.length; i++) if (g.units[i].f === g.player) tr += g.units[i].troops;
  return { f: g.factions[g.player].name, c: g.factions[g.player].color, d: g.year + '년 ' + g.month + '월 ' + ['상순', '중순', '하순'][g.xun], turn: g.turn, n: nb, tr: tr, t: Date.now(), len: len };
}
function metaAll() { try { return JSON.parse(lsGet(SAVE_KEY + '_meta') || '{}') || {}; } catch (e) { return {}; } }
function metaPut(id, m) { var a = metaAll(); if (m) a[id] = m; else delete a[id]; lsSet(SAVE_KEY + '_meta', JSON.stringify(a)); }
/* 칸의 요약. 비었으면 null, 열 수 없는 저장이면 { bad: true } */
function slotInfo(id) {
  var s = lsGet(slotKey(id)); if (!s) return null;
  var m = metaAll()[id];
  if (m && m.len === s.length) return m;
  try { var g = JSON.parse(s); if (!g || g.ver !== 2) return { bad: true }; m = saveMetaOf(g, s.length); m.t = 0; metaPut(id, m); return m; } catch (e) { return { bad: true }; }
}
function slotWrite(id, s, m) { if (!lsSet(slotKey(id), s)) return false; metaPut(id, m); return true; }
function slotDrop(id) { lsDel(slotKey(id)); metaPut(id, null); }
function inGame() { return !!G && !G.over && $('title').classList.contains('off'); }
function saveGame() { if (!G || G.over || UI.play) return false; var s = serialize(); return slotWrite('auto', s, saveMetaOf(G, s.length)); }
/* 직접 저장: 그 칸에 적고, 자동 저장도 같은 모습으로 맞춘다([이어하기]가 늘 가장 나중의 모습이 되게) */
function saveTo(id) { if (!G || G.over || UI.play) return false; var s = serialize(), m = saveMetaOf(G, s.length); if (!slotWrite(id, s, m)) return false; slotWrite('auto', s, m); return true; }
function hasSave() { return !!lsGet(SAVE_KEY); }
function anySave() { var ids = slotIds(); for (var i = 0; i < ids.length; i++) if (lsGet(slotKey(ids[i]))) return true; return false; }
/* 자동 저장이 다른 판으로 바뀌기 전에 '직전' 칸에 남긴다(새 게임 · 불러오기). keep = 남길 저장본(없으면 지금의 자동 저장) */
function keepPrev(keep) {
  var s = keep || lsGet(SAVE_KEY); if (!s) return;
  var m = null; try { m = saveMetaOf(JSON.parse(s), s.length); } catch (e) { return; }
  var old = metaAll().auto; if (!keep && old && old.len === s.length) m.t = old.t;       // 자동 저장을 그대로 옮길 때는 저장한 때도 그대로
  slotWrite('prev', s, m);
}
/* 칸을 불러온다. 하던 판의 지금 모습(제목 화면에서는 자동 저장)은 '직전' 칸에 남고, 불러온 판이 자동 저장이 된다 */
function loadFrom(id) {
  var s = lsGet(slotKey(id)); if (!s) return false;
  var keep = (inGame() && !UI.play) ? serialize() : lsGet(SAVE_KEY), ok = false, g0 = G, r0 = REPORT, e0 = EVQ, j0 = JOT;
  try { ok = deserialize(s); } catch (e) { ok = false; }
  if (!ok) { G = g0; REPORT = r0; EVQ = e0; JOT = j0; if (g0) reindex(); return false; }      // v0.12: 열지 못했으면 하던 판을 그대로 되돌린다
  if (keep && keep !== s) keepPrev(keep);
  if (id !== 'auto') { var m = metaAll()[id], m2 = saveMetaOf(G, s.length); if (m && m.len === s.length) { m2.n = m.n; m2.tr = m.tr; } slotWrite('auto', s, m2); }
  return true;
}
function loadGame() { return loadFrom('auto'); }
function dropSave() { slotDrop('auto'); }
function saveWhen(t) {
  if (!t) return '';
  var d = new Date(t), n = new Date(), p2 = function (v) { return (v < 10 ? '0' : '') + v; }, hm = p2(d.getHours()) + ':' + p2(d.getMinutes());
  return (d.toDateString() === n.toDateString() ? '오늘 ' : (d.getMonth() + 1) + '월 ' + d.getDate() + '일 ') + hm;
}
/* 저장 · 불러오기 창. mode 'save' | 'load'. 제목 화면에서는 불러오기만 */
function showSaves(mode) {
  var game = inGame(), st = { mode: game ? mode : 'load', arm: '' };
  showDialog({
    render: function () {
      var ids = slotIds(), h = dlgHead(game ? '저장 · 불러오기' : '불러오기') + '<div class="dlg-b">';
      if (game) h += '<div class="seg"><button type="button" data-a="smode" data-v="save"' + (st.mode === 'save' ? ' class="on"' : '') + '>저장</button><button type="button" data-a="smode" data-v="load"' + (st.mode === 'load' ? ' class="on"' : '') + '>불러오기</button></div>';
      h += '<div class="rows svl">';
      for (var i = 0; i < ids.length; i++) {
        var id = ids[i], m = slotInfo(id), manual = id.charAt(0) === 's', act = '', del = '';
        if (!manual && (!m || st.mode === 'save')) continue;       // 자동 · 직전: 있을 때만, 불러올 때만 보인다(저장은 번호 칸에만)
        if (st.mode === 'load' && !m) continue;                    // 불러올 때는 찬 칸만
        if (st.mode === 'save') act = '<button class="btn' + (st.arm === 'w' + id ? ' pri' : '') + '" type="button" data-a="ssave" data-v="' + id + '">' + (st.arm === 'w' + id ? '덮어쓰기' : '저장') + '</button>';
        else if (m && !m.bad) act = '<button class="btn" type="button" data-a="sload" data-v="' + id + '">불러오기</button>';
        if (m && id !== 'auto') del = '<button class="btn del' + (st.arm === 'd' + id ? ' pri' : '') + '" type="button" data-a="sdel" data-v="' + id + '" aria-label="' + slotLabel(id) + ' 지우기">' + (st.arm === 'd' + id ? '지움' : '×') + '</button>';
        h += '<div class="row' + (m ? '' : ' emp') + '" data-slot="' + id + '"><i class="svn' + (manual ? '' : ' au') + '">' + slotName(id) + '</i><span class="mid">' +
          (!m ? '<span class="ds">빈 칸</span>' : (m.bad ? '<span class="nm">열 수 없는 저장</span>' : '<span class="nm"><span class="chip" style="background:' + m.c + '">' + m.f + '</span> ' + m.d + '</span><span class="ds">' + m.n + '성 · ' + fmt(m.tr) + '명' + (m.t ? ' · ' + saveWhen(m.t) : '') + '</span>')) +
          '</span>' + act + del + '</div>';
      }
      if (st.mode === 'load' && !anySave()) h += '<p class="note">저장된 판이 없습니다.</p>';
      if (st.mode === 'load') h += '</div><div class="cmds c2 svimp"><button class="cmd" type="button" data-a="simport"><b>파일에서 가져오기</b><small>받은 세이브 파일</small></button><button class="cmd" type="button" data-a="spaste"><b>붙여넣기로 가져오기</b><small>복사해 받은 글</small></button>';
      return h + '</div><p class="note">' + (st.mode === 'save' ? '자동 저장은 턴마다 따로 됩니다.' : '<b>자동</b> = 턴마다 저절로 · <b>직전</b> = 새 게임 · 불러오기 바로 앞의 판') + '</p></div>';
    },
    on: {
      smode: function (el) { st.mode = el.getAttribute('data-v'); st.arm = ''; refreshDialog(); },
      ssave: function (el) {
        var id = el.getAttribute('data-v');
        if (slotInfo(id) && st.arm !== 'w' + id) { st.arm = 'w' + id; refreshDialog(); return; }      // 찬 칸: 한 번 더 눌러야 덮어쓴다
        var ok = saveTo(id); st.arm = '';
        toast(ok ? slotLabel(id) + '에 저장했습니다' : (canStore() ? '저장하지 못했습니다 — 저장 공간이 모자랍니다(안 쓰는 칸을 지워 주세요)' : '이 환경에서는 저장할 수 없습니다'), ok ? 1800 : 3200);
        refreshDialog();
      },
      sload: function (el) {
        var id = el.getAttribute('data-v');
        if (!loadFrom(id)) { toast('불러오지 못했습니다'); return; }
        closeDialog(); if (game) clearSel(); startGame(); toast(dateStr() + ' — ' + slotLabel(id) + '을 불러왔습니다', 2200);
      },
      sdel: function (el) {
        var id = el.getAttribute('data-v');
        if (st.arm !== 'd' + id) { st.arm = 'd' + id; refreshDialog(); return; }
        slotDrop(id); st.arm = ''; refreshDialog(); titleBtns();
      },
      simport: function () { pickSaveFile(function (t) { flowImport(t, function () { st.arm = ''; refreshDialog(); }); }); },
      spaste: function () { showSavePaste(function () { st.arm = ''; refreshDialog(); }); }
    }
  }, true);
}
function titleBtns() { $('tCont').disabled = !hasSave(); $('tLoad').disabled = false; }      // v0.12: [불러오기]는 늘 열린다 — 받은 세이브 파일을 가져올 수 있다

/* ---------- 턴 종료: 지난 열흘을 차례로 보여 주기 ----------
   1) 행군 중인 내 부대가 한 구간 나아간다  2) 다른 세력이 차례로 움직인다(나와 관련된 일·가까운 일·성의 주인이 바뀐 일만 보여 줌)
   3) 날짜가 넘어간다  4) 요약.  화면을 누르면 다음 장면으로, '건너뛰기'는 남은 장면을 모두 넘긴다. */
var endAsk = '';
var SPEEDS = [['끄기', 0], ['느리게', 1.5], ['보통', 1], ['빠르게', 0.5]];
function spdK() { return SPEEDS[UI.pspeed][1] || 1; }
function doEndTurn() {
  if (UI.busy || !G || G.over || MODAL || UI.play) return;
  var left = pendingUnits().length;
  if (left && endAsk !== G.turn + ':' + left) { endAsk = G.turn + ':' + left; toast('명령 대기 ' + left + '부대 — 한 번 더 누르면 턴 종료', 3000); return; }
  endAsk = '';
  clearRet(); clearSel();
  startPlayback();
}
/* 재생 중 콜백 보호: 재생이 끝났으면 무시, 오류가 나면 재생을 정리하고 알린다 */
function pg(fn) {
  return function () {
    if (!UI.play) return;
    try { return fn.apply(null, arguments); } catch (e) { UI.play.err = e; if (window.console) console.error(e); finishPlayback(); }
  };
}
function pwait(ms, cb, fixed) {
  var P = UI.play; if (!P) return;
  if (P.skip) { cb(); return; }
  var f = pg(function () { P.wake = null; cb(); });
  P.wake = function () { clearTimeout(P.timer); f(); };
  P.timer = setTimeout(f, fixed ? ms : ms * spdK());
}
function playNudge() {
  var P = UI.play; if (!P) return;
  if (P.wake) P.wake();
  else if (P.ans.length) { P.ans.forEach(function (a) { a.t0 = -1e12; }); UI.render = true; }
}
function playSkip() {
  var P = UI.play; if (!P || P.skip) return;
  P.skip = true; $('veil').classList.add('on');
  if (typeof DU !== 'undefined' && DU && DU.rec) duClose();              // 일기토를 다시 보던 중이면 닫고 넘어간다
  playNudge();
}
function setCaption(f, html, cls, porF) {
  var F = f >= 0 ? G.factions[f] : null, PF = porF >= 0 ? G.factions[porF] : F, L = PF ? off(PF.lord) : null, u = L ? POR_URL[L.por] : '';      // v0.20: porF = 그림만 이 세력의 군주로(멸망 장면)
  $('plPor').classList.toggle('gone', porF >= 0);
  $('plPor').style.backgroundImage = u ? 'url(' + u + '),var(--porbg)' : '';
  var pcp = (f === G.player && UI.play && UI.play.cp) ? corpsById(UI.play.cp) : null;
  $('plFac').innerHTML = F ? '<span class="chip" style="background:' + F.color + '">' + F.name + '군' + (f === G.player ? (pcp ? ' · ' + corpsName(pcp) : ' · 아군') : '') + '</span>' : '<span class="chip" style="background:#8d877b">천하</span>';
  var m = $('plMsg'); m.innerHTML = html; m.className = 'pl-msg' + (cls ? ' ' + cls : '');
}
function showBanner(t, sub) { var b = $('banner'); b.innerHTML = t + (sub ? '<small>' + sub + '</small>' : ''); b.classList.add('on'); }
function hideBanner() { $('banner').classList.remove('on'); }
function clearAnimFlags() { if (!R3) return; for (var id in R3.units) { var o = R3.units[id]; o.held = false; if (o.anim) { o.anim = false; o.c = -1; o.sig = ''; } } }
/* 그 칸이 화면에 보이게 한 뒤 cb. 이미 잘 보이면 바로. */
function focus(c, r, cb, zWant) {
  var P = UI.play;
  if (P && P.skip) { cb(); return; }
  if (onScreen(c, r, 26) && cam.z >= 0.55 && cam.z <= 1.7) { cb(); return; }
  jumpTo(c, r, zWant || clamp(cam.z, 0.78, 1.25), 0, 340);
  pwait(400, cb, true);
}
/* 싸움 장면용: 충분히 가까이(확대 1.3 이상) 보이게 한 뒤 cb */
function focusNear(c, r, cb) {
  var P = UI.play;
  if (P && P.skip) { cb(); return; }
  if (onScreen(c, r, 40) && cam.z >= 1.3) { cb(); return; }
  jumpTo(c, r, 1.6, 0, 340);
  pwait(400, cb, true);
}
function startPlayback() {
  saveGame();                                             // 재생 도중 창을 닫아도 '턴 종료 직전'으로 돌아오게
  var P = UI.play = { next: null, skip: UI.pspeed === 0, cam0: { x: cam.x, y: cam.y, z: cam.z }, timer: 0, wake: null, ans: [], batch: [], err: null, minor: 0, shown: 0, save0: null };
  try { P.save0 = serialize(); } catch (e) { P.save0 = null; }
  UI.busy = true; REPORT = []; EVQ = [];
  hideSheet(); $('app').classList.add('playing');
  $('plSpeed').textContent = '속도: ' + SPEEDS[UI.pspeed || 1][0];
  setCaption(G.player, '턴을 마칩니다 — <b>열흘</b>이 흐릅니다');
  requestDraw();
  var go = pg(function () { playMarch(pg(function () { EVQ.length = 0; P.next = turnStepper(); pump(); })); });
  if (P.skip) { $('veil').classList.add('on'); setTimeout(go, 40); } else pwait(420, go);
}
function marchLog(u, name, res) {
  var b;
  if (res.entered !== undefined) { b = G.bases[res.entered]; logMsg(name + ' ' + b.n + ' 입성' + backSay(res).replace('돌아갑니다', '돌아간다'), b.c, b.r, G.player, 1); }
  else if (res.captured !== undefined) { /* 차지한 일은 규칙 쪽에서 이미 기록한다 */ }
  else if (res.dead) logMsg(name + ' 불길 속에서 흩어짐', res.from[0], res.from[1], G.player, 2);
  else if (res.front !== undefined) { b = G.bases[res.front]; if (!(alive(u) && u.aim)) logMsg(name + ' ' + b.n + ' 앞에 도착 — 공격 명령을 내리세요', b.c, b.r, G.player, 2); }
  else if (alive(u) && u.dest < 0) logMsg(name + ' 목적지에 도착', u.c, u.r, G.player, 1);
}
/* 1) 행군 중인 내 부대: 한 부대씩 한 구간 */
function playMarch(done) {
  var P = UI.play, us = marchList(G.player), i = 0;
  var step = pg(function () {
    while (i < us.length) {
      var u = us[i++];
      if (!alive(u) || u.done || u.dest < 0) continue;
      var name = uName(u), dn = destName(u.dest), vis = unitVis(u), o = R3.units[u.id];
      var res = unitMarch(u);
      if (!res) continue;
      if (!res.ok) {
        if (res.front !== undefined) logMsg(name + ' ' + G.bases[res.front].n + ' 앞에 도착 — 공격 명령을 내리세요', u.c, u.r, G.player, 2);
        else if (res.lost) logMsg(name + ' 길이 막혀 행군을 멈춤', u.c, u.r, G.player, 1);
        continue;
      }
      marchLog(u, name, res);
      if (P.skip || !o) continue;
      o.anim = true;                                     // 연출이 시작될 때까지 제자리에 둔다
      P.shown++;
      playMarchShow(name, dn, vis, res, step);
      return;
    }
    done();
  });
  step();
}
function playMarchShow(name, dn, vis, res, next) {
  var P = UI.play, mid = res.path[Math.floor(res.path.length / 2)], mc = mid % W;
  focus(mc, (mid - mc) / W, pg(function () {
    var tail = res.entered !== undefined ? ' — <b>' + G.bases[res.entered].n + '</b> 입성' + backSay(res) : (res.captured !== undefined ? ' — <b>' + G.bases[res.captured].n + '</b> 점령!' : (res.front !== undefined ? ' — <b>' + G.bases[res.front].n + '</b> 앞에 도착' : ''));
    setCaption(G.player, '<b>' + name + '</b> ' + dn + ' 방면으로 행군' + tail);
    animMove(vis, res.from, res.path, pg(function () {
      P.ans = []; if (res.captured !== undefined) { sfx('fall'); sfx('cheerlate'); fxFall(G.bases[res.captured], '점령'); }
      requestDraw(); pwait(tail ? 800 : 240, next);
    }), 1.2 * spdK());
    P.ans = [UI.anims[UI.anims.length - 1]];
  }));
}
/* 2)~3) 다른 세력의 차례를 한 단계씩 돌리며 보여 줄 것만 골라 보여 준다 */
function nearMine(c, r, d) {
  var i, f = G.player;
  for (i = 0; i < G.bases.length; i++) if (G.bases[i].owner === f && hdist(c, r, G.bases[i].c, G.bases[i].r) <= d) return true;
  for (i = 0; i < G.units.length; i++) if (G.units[i].f === f && hdist(c, r, G.units[i].c, G.units[i].r) <= d) return true;
  return false;
}
/* 2 = 나와 직접 관련(천천히) · 1 = 가까운 곳의 일(짧게) · 0 = 보여 주지 않음 */
function evClass(e) {
  if (e.t === 'fall') {
    var fb = G.bases[e.b];
    if (e.old === G.player || e.by === G.player) return 2;
    if (e.old >= 0 && fb.kind === 'city') return 2;                 // 성의 주인이 바뀜: 어디서든 보여 준다
    return nearMine(fb.c, fb.r, 12) ? 1 : 0;                        // 빈 성을 차지했거나 관문: 가까울 때만 짧게
  }
  if (e.t === 'fallen' || e.t === 'news' || e.t === 'ask') return 2;
  if (e.t === 'act') return (e.tf === G.player || e.f === G.player) ? 2 : (nearMine(e.tc, e.tr, 7) ? 1 : 0);      // v0.10: 내 군단이 치는 싸움도 천천히
  if (e.t === 'move') return nearMine(e.c, e.r, 6) ? 1 : 0;
  if (e.t === 'deploy') return nearMine(e.c, e.r, 8) ? 1 : 0;
  return 0;
}
/* 사건에 얽힌 부대 그림을 붙잡아 둔다(규칙 쪽 상태는 이미 앞서가 있으므로) */
function holdEv(e) {
  if (!R3 || !e.cls) return;
  var o;
  if (e.t === 'move') { o = R3.units[e.id]; if (o) o.anim = true; }
  else if (e.t === 'act' && e.res) { o = R3.units[e.res.aid]; if (o) o.anim = true; if (e.res.tid >= 0) { o = R3.units[e.res.tid]; if (o) o.anim = true; } }
}
function pump() {
  var P = UI.play;
  for (;;) {
    var s = P.next(), evs = EVQ.splice(0, EVQ.length), show = [], i, e, big = false, onlyMoves = false;
    if (s) { if (s.corps) P.cp = s.corps; else if (s.kind !== 'step') P.cp = 0; }             // 군단의 차례인가(자막의 칩에 군단 이름을 붙인다)
    if (P.skip) { P.batch = []; if (!s) { finishPlayback(); return; } continue; }
    if (s) {
      for (i = 0; i < evs.length; i++) { evs[i].cls = evClass(evs[i]); if (evs[i].cls === 2) big = true; }
      for (i = 0; i < evs.length; i++) holdEv(evs[i]);          // 보여 줄 때까지 그림을 지금 모습 그대로 둔다
      for (i = 0; i < evs.length; i++) {
        e = evs[i];
        if (e.cls === 2 || (e.cls === 1 && (big || P.minor < 16))) { show.push(e); if (e.cls === 1 && !big) P.minor++; }
      }
      if (!show.length && s.kind !== 'round') continue;
      onlyMoves = show.length > 0 && show.every(function (x) { return x.t === 'move' && x.cls === 1; });
      if (onlyMoves && P.batch.length < 4 && (!P.batch.length || P.batch[0].f === show[0].f) && !P.batch.some(function (b) { return show.some(function (x) { return x.id === b.id; }); })) { P.batch = P.batch.concat(show); continue; }
    }
    pumpShow(s, show, onlyMoves);
    return;
  }
}
/* 모아 둔 이동을 먼저 보여 주고, 이어서 이번 단계의 장면을 보여 준다 */
function pumpShow(s, show, onlyMoves) {
  var P = UI.play;
  var after = pg(function () {
    if (!s) { finishPlayback(); return; }
    if (s.kind === 'round') { presentRound(pg(pump)); return; }
    if (onlyMoves) { P.batch = show; pump(); return; }
    if (show.length) presentEvents(show, pg(pump)); else pump();
  });
  if (P.batch.length) { var b = P.batch; P.batch = []; presentMoves(b, after); } else after();
}
function presentMoves(evs, done) {
  var P = UI.play, live = [], names = [], i;
  for (i = 0; i < evs.length; i++) { var o = R3.units[evs[i].id]; if (o) { o.anim = true; live.push(evs[i]); if (names.length < 3) names.push(evs[i].n); } }
  if (!live.length) { done(); return; }
  P.shown += live.length;
  var e0 = live[0];
  focus(e0.c, e0.r, pg(function () {
    var tail = live.length === 1 && e0.into !== undefined ? G.bases[e0.into].n + (G.bases[e0.into].owner === e0.f ? ' 입성' : ' 점령') : '이동';
    setCaption(e0.f, '<b>' + names.join(' · ') + '</b>' + (live.length > names.length ? ' 등 ' + live.length + '개 부대' : '') + ' ' + tail);
    var left = live.length, n0 = UI.anims.length;
    for (var j = 0; j < live.length; j++) animMove({ id: live[j].id }, live[j].from, live[j].path, pg(function () { if (--left > 0) return; P.ans = []; requestDraw(); pwait(160, done); }), 0.8 * spdK());
    P.ans = UI.anims.slice(n0);
  }));
}
function presentEvents(evs, done) {
  var P = UI.play, i;
  for (i = 0; i < evs.length; i++) holdEv(evs[i]);
  syncScene();                                             // 새로 나온 부대를 만들고, 움직일 부대는 출발점에 둔 채로
  for (i = 0; i < evs.length; i++) if (evs[i].t === 'deploy') {   // 막 출진한 부대는 성 앞 칸에 세워 둔다(뒤따르는 이동은 거기서 시작)
    var od = R3.units[evs[i].id];
    if (od && !od.held) { od.anim = true; od.held = true; fxPut(od, hexPos(evs[i].c, evs[i].r)); }
  }
  i = 0;
  var one = pg(function () {
    if (P.skip || i >= evs.length) { clearAnimFlags(); requestDraw(); done(); return; }
    P.shown++;
    presentEvent(evs[i++], one);
  });
  one();
}
function presentEvent(e, cb) {
  var P = UI.play, b, k = e.cls === 2 ? 1 : 0.45;
  if (e.t === 'move') {
    var o = R3.units[e.id];
    if (!o) { cb(); return; }
    focus(e.c, e.r, pg(function () {
      setCaption(e.f, '<b>' + e.n + '</b> ' + (e.into !== undefined ? G.bases[e.into].n + (G.bases[e.into].owner === e.f ? ' 입성' : ' 점령') : '이동'));
      animMove({ id: e.id }, e.from, e.path, pg(function () { P.ans = []; requestDraw(); pwait(140, cb); }), 0.8 * spdK());
      P.ans = [UI.anims[UI.anims.length - 1]];
    }));
  } else if (e.t === 'ask') {                                      // v0.16: 내 부대에 일기토를 걸어왔다 — 답은 내 차례에
    if (UI.battleTurn !== G.turn) { UI.battleTurn = G.turn; playBgm('battle'); }
    focusNear(e.tc, e.tr, pg(function () {
      setCaption(e.f, '<b>' + e.name + '</b> 일기토 신청 → ' + e.tname + ' <small>내 차례에 답합니다</small>', 'hit');
      sfx('duel'); floatText(e.c, e.r, '일기토 신청!', '#b5332a', 0, true, -20); flashHex(e.tc, e.tr, '#b5332a');
      var au = UMAP[e.id]; if (au && typeof voiceSay === 'function') voiceSay(uLeader(au), 'duel', { at: [e.c, e.r] });
      pwait(1500, cb);
    }));
  } else if (e.t === 'act' && e.res && e.res.kind === 'challenge') {   // v0.16: AI 가 건 일기토(공격 연출 없이)
    var mineD = e.f === G.player || e.tf === G.player;
    if (mineD && UI.battleTurn !== G.turn) { UI.battleTurn = G.turn; playBgm('battle'); }
    focusNear(e.tc, e.tr, pg(function () {
      var r = e.res;
      setCaption(e.f, resultMsg(e.name, r), e.tf === G.player ? 'hit' : '');
      floatText(r.ac, r.ar, '일기토 신청', '#1b1a18', 0, true, -20);
      if (!r.accepted) { sfx('miss'); floatText(r.c, r.r, '받지 않음 · 기력 -' + r.mor, '#2f4f6f', 320, false, 22); pwait(1100 * k, cb); return; }
      if (r.duelRec && r.duel && !P.skip && mineD) {                // 내 군단이 얽혔으면 처음부터 그려 보인다
        duelReplay(r.duelRec, { sub: e.name + ' 대 ' + (r.tname || ''), out: duelOutHtml(null, r.duel, e.name, r.tname || '') }, pg(function () { pwait(300 * k, cb); }));
        return;
      }
      sfx('duel');
      if (r.duel && !r.duel.draw) floatText(r.duel.win ? r.c : r.ac, r.duel.win ? r.r : r.ar, '일기토 패 -' + fmt(r.duel.loss), '#b5332a', 420, true, 22);
      else if (r.duel) floatText(r.c, r.r, '비김', '#6a645a', 420, false, 22);
      pwait(1300 * k, cb);
    }));
  } else if (e.t === 'act') {
    if ((e.f === G.player || e.tf === G.player) && UI.battleTurn !== G.turn) { UI.battleTurn = G.turn; playBgm('battle'); }   // 내가 얽힌 싸움이면 전투 음악으로
    focusNear(e.tc, e.tr, pg(function () {
      setCaption(e.f, resultMsg(e.name, e.res), e.tf === G.player ? 'hit' : '');
      var n0 = UI.anims.length;
      animAct(e.res, pg(function () {
        P.ans = []; requestDraw();
        var rec = e.res.duelRec;
        if (rec && e.res.duel && !P.skip && (e.f === G.player || e.tf === G.player)) {      // v0.13: 내 부대가 얽힌 일기토는 처음부터 다시 그려 보인다
          duelReplay(rec, { sub: e.name + ' 대 ' + (e.res.tname || ''), out: duelOutHtml(null, e.res.duel, e.name, e.res.tname || '') }, pg(function () { pwait(300 * k, cb); }));
          return;
        }
        pwait((e.res.fell ? 200 : 700) * k, cb);
      }), function () { resultFx(e.res); });   // 함락이면 바로 뒤에 함락 장면이 따로 나온다
      P.ans = UI.anims.slice(n0);
    }));
  } else if (e.t === 'fall') {
    b = G.bases[e.b];
    focus(b.c, b.r, pg(function () {
      var mine = e.old === G.player;
      setCaption(e.by, e.old < 0 ? '<b>' + josa(facName(e.by) + '군', '이가') + ' 주인 없는 ' + josa(b.n, '을를') + ' 차지</b>' : '<b>' + josa(facName(e.by) + '군', '이가') + ' ' + josa(b.n, '을를') + (b.kind === 'gate' ? ' 점령' : ' 함락') + '!</b> (' + facName(e.old) + '군 → ' + facName(e.by) + '군)' + (mine ? '<br>우리 거점을 잃었습니다' : ''), mine ? 'hit' : 'big');
      sfx('fall'); if (e.by === G.player) sfx('cheerlate');
      fxFall(b, e.old < 0 || b.kind === 'gate' ? '점령' : '함락');
      requestDraw(); pwait(2000 * k, cb);
    }), 0.8);
  } else if (e.t === 'deploy') {
    focus(e.c, e.r, pg(function () {
      setCaption(e.f, G.bases[e.base].n + '에서 <b>' + e.n + '</b> 출진');
      sfx('drums');
      var odp = R3.units[e.id], bb = G.bases[e.base];
      if (odp && bb) {                                           // 성에서 걸어 나온다(뒤따르는 이동 장면을 위해 붙잡아 둔 채로)
        var q0 = hexPos(bb.c, bb.r), q1 = hexPos(e.c, e.r);
        anim(420, function (t) { var w = 1 - (1 - t) * (1 - t), px = q0[0] + (q1[0] - q0[0]) * w, pz = q0[2] + (q1[2] - q0[2]) * w; fxPut(odp, [px, groundY(px, pz) + Math.sin(Math.PI * t) * 0.16, pz]); });
        P.ans = [UI.anims[UI.anims.length - 1]];
      }
      pwait(640, cb);
    }));
  } else if (e.t === 'news') {
    focus(e.c, e.r, pg(function () {
      setCaption(e.f, e.text, e.warn ? 'hit' : '');
      flashHex(e.c, e.r, '#b5332a'); sfx('drum');
      requestDraw(); pwait(1900, cb);
    }));
  } else if (e.t === 'fallen') {
    setCaption(-1, '<b>' + facName(e.f) + '군 멸망</b>', 'big', e.f); sfx('gong');
    pwait(2200, cb);
  } else cb();
}
function presentRound(cb) {
  refreshHud(); requestDraw();
  showBanner(dateStr(), '열흘이 지났습니다');
  setCaption(G.player, '<b>' + dateStr() + '</b> — 새 턴이 시작됩니다');
  sfx('gong');
  pwait(1000, function () { hideBanner(); cb(); });
}
function finishPlayback() {
  var P = UI.play; if (!P) return;
  UI.play = null; clearTimeout(P.timer);
  clearAnimFlags(); UI.hide = -1; UI.busy = false; EVQ.length = 0;
  hideBanner(); $('veil').classList.remove('on'); $('app').classList.remove('playing');
  if (P.err) toast('오류가 발생했습니다: ' + P.err.message, 6000);
  sfxMoveStop(); sfx('drum'); saveGame(); refreshHud();
  if (P.shown) jumpBack(P.cam0);
  showHome(); requestDraw();
  if (G.over) { showGameOver(); return; }
  playBgm(bgmForState());
  askNext(function () { showReport(REPORT); });      // v0.21: 수송을 마친 무장이 있으면 먼저 묻는다
}
function jumpBack(c0) {
  var x0 = cam.x, y0 = cam.y, z0 = cam.z;
  anim(380, function (t) { var e = t * (2 - t); cam.x = x0 + (c0.x - x0) * e; cam.y = y0 + (c0.y - y0) * e; cam.z = z0 + (c0.z - z0) * e; clampCam(); });
}
/* 4) 요약: 중요한 일 → 우리 세력 → 천하 */
/* 내 차례가 시작될 때 군사가 지금 가장 급한 일을 말한다(창이 떠 있으면 닫힌 뒤에) */
function advBrief(wait) {
  var turn = G.turn;
  setTimeout(function () {
    if (!G || G.over || UI.play || G.turn !== turn || UI.briefT === turn || !inGame()) return;      // 한 턴에 한 번(제목 화면으로 나갔으면 말하지 않는다)
    if (MODAL) { advBrief(700); return; }
    var A = facAdv(G.player), top = A ? advTop(todoList()) : null;
    UI.briefT = turn;
    if (!top || UI.talk === false) return;                                  // 대화창을 꺼 두었으면 차례 첫머리의 한마디도 띄우지 않는다(STATUS 창에는 그대로 있다)
    if (UI.briefSay === top.say && turn - UI.briefAt < 3) return;            // 같은 말을 턴마다 되풀이하지 않는다 — 한 달(세 턴)에 한 번만
    UI.briefSay = top.say; UI.briefAt = turn;
    talk(A, top.say, '', 4200);
  }, wait || 300);
}
function repMark(x, s) {                            // 줄 머리: 군단의 보고는 군단장의 초상
  var cp = x.corps ? corpsById(x.corps) : null, L = cp ? corpsLead(cp) : null;
  if (L && x.imp < 2) return porTag(L, 'sm');
  return '<span class="mk">' + (x.imp >= 3 ? '★' : (s === 0 ? '●' : '·')) + '</span>';
}
function showReport(list) {
  var secs = [['중요한 일', []], ['군단', []], ['우리 세력', []], ['천하의 움직임', []]], i, n = 0;
  for (i = 0; i < list.length; i++) {
    var e = list[i]; if (e.imp < 1) continue;
    secs[e.imp >= 2 ? 0 : (e.corps ? 1 : (e.f === G.player ? 2 : 3))][1].push(i); n++;
  }
  if (!n) { toast(dateStr() + ' — 조용한 열흘', 2200); advBrief(1200); askSoon(900); return; }
  clearRet();
  showDialog({
    render: function () {
      var h = dlgHead('지난 열흘의 일') + '<div class="dlg-b"><div class="rep-date">' + dateStr() + '<small>' + n + '건</small></div>';
      for (var s = 0; s < secs.length; s++) {
        var ids = secs[s][1]; if (!ids.length) continue;
        h += '<div class="sec">' + secs[s][0] + '</div><div class="rows">';
        for (var j = 0; j < ids.length; j++) { var x = list[ids[j]]; h += '<button class="row rep' + (x.imp >= 3 ? ' top' : (s === 0 ? ' imp' : '')) + '" type="button" data-a="j" data-v="' + ids[j] + '">' + repMark(x, s) + '<span class="mid">' + x.t + '</span>' + (x.c !== undefined ? '<span class="go">▸</span>' : '') + '</button>'; }
        h += '</div>';
      }
      return h + '</div><div class="dlg-f"><div class="pv">이제 <b>' + G.factions[G.player].name + '군</b>의 차례입니다</div><button class="btn pri" type="button" data-a="close">확인</button></div>';
    },
    onClose: function () { advBrief(300); askSoon(500); },
    on: { j: function (el) { var e = list[+el.getAttribute('data-v')]; if (e && e.c !== undefined) jumpFromDialog('지난 열흘의 일', function () { clearSel(); jumpTo(e.c, e.r, Math.max(cam.z, 0.8)); flashHex(e.c, e.r, '#b5332a'); }); } }
  });
}
function nextUnit() {
  var us = pendingUnits();
  if (!us.length) us = facUnits(G.player).filter(function (u) { return !u.done; });
  if (!us.length) { toast('움직일 부대가 없습니다'); return; }
  var cur = UI.sel && UI.sel.kind === 'unit' ? UI.sel.id : -1, i = 0;
  for (var j = 0; j < us.length; j++) if (us[j].id === cur) i = (j + 1) % us.length;
  gotoUnit(us[i]);
}
function showGameOver() {
  if (UI.ending === G && (CINE.on || MODAL)) return;         // v0.19: 끝 화면은 한 번만 연다(영상이 도는 동안 다시 불려도)
  UI.ending = G;
  dropSave();
  var win = G.over === 'win';
  playBgm(win ? 'victory' : 'defeat', true);
  cinePlay(win ? 'win' : 'lose', { cap: win ? '天下統一' : '敗亡', hold: true }, function () { showOverDialog(win); });      // 영상이 끝나면 그 마지막 장면 위에 창이 뜬다
}
function showOverDialog(win) {
  showDialog({
    render: function () {
      return '<div class="dlg-h"><h2>' + (win ? '천하통일' : '패망') + '</h2></div><div class="dlg-b"><p>' + (win ? dateStr() + ', ' + josa(G.factions[G.player].name, '이가') + ' 천하를 하나로 만들었습니다.' : dateStr() + ', ' + G.factions[G.player].name + ' 세력은 역사 속으로 사라졌습니다.') + '</p></div>' +
        '<div class="dlg-f"><div class="pv">' + fmt(G.turn * 10) + '일째</div><button class="btn pri" type="button" data-a="t">처음으로</button></div>';
    },
    lock: true,                                                    // 바깥을 눌러도 닫히지 않는다(닫히면 끝난 판에 갇힌다)
    on: { t: function () { closeDialog(); cineHide(); UI.ending = null; G = null; UI.ret = null; hideSheet(); showTitle(); playBgm('title'); } }
  });
}

/* ---------- 시작 ---------- */
function showTitle() {
  ocardClose();
  $('title').classList.remove('off');
  titleVideo(true);                                           // v0.19: 제목 그림이 움직인다
  titleBtns(); talkHide();                                    // 제목 화면에는 대화창을 남기지 않는다
  $('tVer').textContent = GAME_VERSION + ' · 삼국지 천하도 · 194년 군웅할거';
}
function startGame() {
  ocardClose();
  $('title').classList.add('off');
  titleVideo(false);
  resize();
  var L = off(G.factions[G.player].lord), b = L.unit !== null ? UMAP[L.unit] : G.bases[L.loc];
  var p = hexCenter(b.c, b.r);
  cam.x = p[0]; cam.y = p[1] + 4; cam.z = 0.9; clampCam();
  UI.battleTurn = undefined; UI.sel = null; UI.rc = null; UI.atk = null; UI.target = null; UI.march = null; UI.ret = null; UI.via = false; UI.sret = null; MSTACK.length = 0; paintRet();
  UI.briefT = undefined; UI.briefSay = ''; UI.briefAt = 0; talkHide();
  refreshHud(); showHome(); requestDraw(); playBgm(bgmForState());
  advBrief(900);                                               // 이어 하기로 들어왔을 때도 군사가 한마디
}
function showFactionSelect() {
  var st = { f: -1 };
  var info = SCENARIO.factions.map(function (sf, i) {
    var os = SCENARIO.officers.filter(function (o) { return o.f === i; }), lord = null;
    os.forEach(function (o) { if (o.n === sf.n) lord = o; });
    return { i: i, n: sf.n, color: sf.color, cities: sf.cities, cnt: os.length, lord: lord, troops: startTroops(i), peace: peaceFor(startTroops(i)) };
  });
  showDialog({
    render: function () {
      var h = dlgHead('194년 군웅할거 — 군주를 고르세요') + '<div class="dlg-b"><div class="rows">';
      for (var i = 0; i < info.length; i++) {
        var x = info[i];
        h += '<button class="row' + (st.f === x.i ? ' sel' : '') + '" type="button" data-a="f" data-v="' + x.i + '">' + porTag(x.lord) + '<span class="mid"><span class="nm">' + x.n + ' <span class="chip" style="background:' + x.color + '">' + x.cities.join('·') + '</span></span><span class="ds" style="white-space:normal">' + FACTION_DESC[x.n] + '</span><span class="ds fs-st">병력 <b>' + fmt(x.troops) + '</b> · 초반 보호 <b' + (x.peace > PEACE_ALL ? ' class="ok"' : '') + '>' + months(x.peace) + '</b></span></span><span class="rt">무장<br><b>' + x.cnt + '</b></span></button>';
      }
      return h + '</div></div><div class="dlg-f"><div class="pv">' + (st.f >= 0 ? '<b>' + info[st.f].n + '</b> · 도시 ' + info[st.f].cities.length + ' · 무장 ' + info[st.f].cnt + '명<br>병력 ' + fmt(info[st.f].troops) + ' · 초반 보호 ' + months(info[st.f].peace) + '(' + dateOfTurn(info[st.f].peace) + '까지)' : '군주를 고르세요') + '</div><button class="btn pri" type="button" data-a="go"' + (st.f < 0 ? ' disabled' : '') + '>시작</button></div>';
    },
    on: {
      f: function (el) { st.f = +el.getAttribute('data-v'); refreshDialog(); },
      go: function () { if (st.f < 0) return; closeDialog(); keepPrev(); newGame(st.f); saveGame(); startGame(); sfx('gong'); cinePlay('opening', { cap: '群雄割據', sub: '194년 — 천하는 어지럽고 영웅들이 일어선다' }, function () { showIntro(); }); }      // v0.19: 오프닝 영상(끄면 곧바로 다음 창)
    }
  });
}
function showIntro() {
  var F = G.factions[G.player], L = off(F.lord);
  showDialog({
    render: function () {
      return dlgHead(dateStr() + ' — ' + F.name) + '<div class="dlg-b"><div class="card">' + sceneTag(L) + '<div><p>' + FACTION_DESC[F.name] + '</p></div></div><div class="help"><ul>' +
        '<li>아래 <b>지금 할 일</b>을 위에서부터 누르면 됩니다.</li>' +
        '<li><b>도시</b>를 누르면 명령이 열립니다. <b>부대</b>는 파란 칸으로 움직이고, 적을 누르면 공격합니다.</li>' +
        '<li>다 했으면 <b>턴 종료</b> — 열흘이 흐릅니다.</li>' +
        (peaceLeft() > 0 ? '<li><b>초반 보호</b> — <b>' + dateOfTurn(G.peace.until - 1) + '까지(' + months(peaceLeft()) + ')</b> 아무도 우리 성을 먼저 치지 않습니다.</li>' : '') +
        '</ul></div></div><div class="dlg-f"><div class="pv">도시 42곳을 모두 차지하면 천하통일</div><button class="btn pri" type="button" data-a="close">시작</button></div>';
    }, onClose: function () { advBrief(400); }, on: {}
  });
}
function boot(data) {
  loadOpts();
  try { init3d(); } catch (e) { document.body.innerHTML = '<p style="padding:24px;color:#1b1a18;font:16px sans-serif">이 기기에서는 3D 지도를 그릴 수 없습니다(WebGL을 쓸 수 없음).<br>' + e.message + '</p>'; return; }
  loadAssets(); initInput(); resize();
  delegate($('sheet'), function () { return SHEET; }, function () { backSheet(); });
  delegate($('modal'), function () { return MODAL; }, function () { backDialog(); });
  ocardInit();                                                   // v0.18: 얼굴을 누르면 무장 카드
  $('btnEnd').addEventListener('click', function () { audioInit(); doEndTurn(); });
  $('hud').addEventListener('click', function () { if (!G || G.over || UI.busy || UI.play || MODAL) return; audioInit(); sfx('ui'); HOME.open = true; saveOpts(); clearSel(); });
  $('play').addEventListener('click', function () { playNudge(); });
  $('plSkip').addEventListener('click', function (e) { e.stopPropagation(); sfx('ui'); playSkip(); });
  $('plSpeed').addEventListener('click', function (e) { e.stopPropagation(); sfx('ui'); UI.pspeed = UI.pspeed % 3 + 1; saveOpts(); $('plSpeed').textContent = '속도: ' + SPEEDS[UI.pspeed][0]; });
  $('btnNext').addEventListener('click', function () { audioInit(); sfx('ui'); nextUnit(); });
  $('btnList').addEventListener('click', function () { audioInit(); sfx('ui'); if (G) showLists(); });
  $('btnLog').addEventListener('click', function () { audioInit(); sfx('ui'); if (G) showLog(G.log, '기록'); });
  $('btnMenu').addEventListener('click', function () { audioInit(); sfx('ui'); if (G) showMenu(); });
  $('ret').addEventListener('click', function () { if (!G || G.over || UI.busy || UI.play || MODAL) return; audioInit(); sfx('ui'); goRet(); });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    if (cineSkip()) return;
    if (ocardOn()) { ocardClose(); return; }
    if (MODAL) { backDialog(); return; }
    if (G && !G.over && !UI.busy && !UI.play && SHEET && !SHEET.home) backSheet();
  });
  titleVideo(true);                                           // v0.19: 처음 뜬 제목 화면
  $('tNew').addEventListener('click', function () { audioInit(); playBgm('title'); sfx('ui'); showFactionSelect(); });
  $('tCont').addEventListener('click', function () { audioInit(); if (loadGame()) { startGame(); toast(dateStr() + ' — 이어서 합니다'); } else toast('저장된 게임이 없습니다'); });
  $('tLoad').addEventListener('click', function () { audioInit(); playBgm('title'); sfx('ui'); showSaves('load'); });
  $('tHelp').addEventListener('click', function () { audioInit(); playBgm('title'); showHelp(); });
  $('tShare').addEventListener('click', function () { audioInit(); sfx('ui'); shareGame(); });
  moreInit();
  document.addEventListener('visibilitychange', function () { if (document.hidden) saveGame(); });
  if (data && data.save && deserialize(data.save)) startGame(); else { showTitle(); BGM.want = 'title'; }
  requestAnimationFrame(tick);
}
(function () {
  var hot = window.claude && window.claude.hot;
  if (hot && hot.snapshot) hot.snapshot(function () { return { save: (G && !G.over) ? (UI.play ? UI.play.save0 : serialize()) : null }; });
  // three.js는 허용된 CDN에서 불러온다. 첫 주소가 막히면 같은 파일을 다른 곳에서 차례로 받는다.
  var ALT = ['https://cdn.jsdelivr.net/npm/three@0.149.0/build/three.min.js', 'https://unpkg.com/three@0.149.0/build/three.min.js'];
  function start() { if (hot && hot.ready) hot.ready(boot); else boot((hot && hot.data) || {}); }
  function need() {
    if (window.THREE) { start(); return; }
    var u = ALT.shift();
    if (!u) { document.body.innerHTML = '<p style="padding:24px;color:#1b1a18;font:16px/1.6 sans-serif">3D 지도 라이브러리(three.js)를 불러오지 못했습니다.<br>네트워크 연결을 확인하고 다시 열어 주세요.</p>'; return; }
    var s = document.createElement('script'); s.src = u; s.onload = need; s.onerror = need; document.head.appendChild(s);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', need); else need();
})();

/* ---------- 군단(v0.10) ---------- */
var DIR_KEYS = ['dev', 'arm', 'atk', 'sup'];
var DIR_SUB = { dev: '시설 · 치안 · 출격 안 함', arm: '징병 · 병기 · 훈련', atk: '고른 거점을 친다', sup: '병력 · 물자를 보낸다' };
/* 군단의 부대가 지금 하는 일 */
function unitMission(u) {
  var ai = u.ai || {}, T = (ai.target !== undefined && ai.target >= 0) ? G.bases[ai.target] : null, H = (ai.home !== undefined && ai.home >= 0) ? G.bases[ai.home] : null;
  if (u.type === 'trans') return T ? euro(T.n) + ' 수송' : '수송';
  if (ai.mode === 'attack' && T) return T.owner === G.player ? T.n + ' 입성' : T.n + ' 공격';
  if (ai.mode === 'defend' && H) return H.n + ' 방어';
  if (ai.mode === 'garrison' && T) return T.n + ' 입성';
  return '귀환';
}
/* 군단장이 대화창에서 답한다(군단장이 없으면 알림 줄) */
function corpsSaid(cp, key, x, sub) { var L = corpsLead(cp); if (L) talk(L, sayLine(L, key, x), sub); else if (sub) toast(String(sub).replace(/<[^>]*>/g, '')); }
/* STATUS 창의 군단 줄 */
function corpsStrip() {
  var f = G.player, cps = corpsAll(), n = facBases(f).length, i, h = '';
  if (!cps.length && n < 2) return '';
  h = '<div class="hm-corps">';
  for (i = 0; i < cps.length; i++) {
    var cp = cps[i], L = corpsLead(cp);
    h += '<button class="cpb" type="button" data-a="corps" data-v="' + cp.id + '">' + (L ? porTag(L, 'sm') : '<i class="por sm none"></i>') + '<span><b>' + corpsName(cp) + '</b><small>' + corpsDirText(cp) + '</small></span></button>';
  }
  if (cps.length < CORPS_MAX && directBases(f).length) h += '<button class="cpb new" type="button" data-a="corpsnew"><span><b>+ 군단</b><small>거점 맡기기</small></span></button>';
  return h + '</div>';
}
/* 공격 방침: 지금 나설 수 있는가를 한 줄로 */
function corpsWaitText(cp) {
  var T = G.bases[cp.target], o = cp.dir === 'atk' ? corpsOutlook(cp, T) : null;
  if (!o) return '';
  var tot = o.have + o.going;
  if (o.going >= o.need && o.going > 0) return '<b class="ok">' + fmt(o.going) + '명이 가고 있습니다</b>';
  if (T.owner < 0) return tot >= o.need ? '<b class="ok">빈 거점 — 곧 차지하러 나섭니다</b>' : '<b class="bad">보낼 병력이 없습니다</b>';
  if (tot >= o.need) return '<b class="ok">나설 수 있습니다</b> — 낼 수 있는 병력 ' + fmt(tot) + ' / 필요 ' + fmt(o.need) + (cp.ap < 60 && !o.going ? ' · 행동력 60이 모이면' : '');
  return '<b class="bad">아직 모자랍니다</b> — 낼 수 있는 병력 ' + fmt(tot) + ' / 필요 ' + fmt(o.need);
}
function corpsRefresh() { syncScene(); refreshDialog(); refreshSheet(); refreshHud(); requestDraw(); }
/* 군단 창 */
function showCorps(id) {
  showDialog({
    render: function () {
      var cp = corpsById(id), i;
      if (!cp) return dlgHead('군단') + '<div class="dlg-b"><p class="note">이 군단은 해산되었습니다.</p></div>';
      var L = corpsLead(cp), bs = corpsBases(cp), us = corpsUnits(cp), T = (cp.target !== undefined && cp.target >= 0) ? G.bases[cp.target] : null;
      var h = dlgHead(corpsName(cp)) + '<div class="dlg-b">' +
        '<div class="card cpc">' + (L ? porTag(L, 'md') : '<i class="por md none"></i>') + '<div><p>군단장 <b class="hi">' + (L ? L.n : '없음') + '</b></p><p class="note">행동력 <b>' + cp.ap + '</b> <small>(+' + corpsRegen(cp) + '/턴)</small> · 병력 <b>' + fmt(corpsTroops(cp)) + '</b> · 무장 ' + corpsOfficers(cp).length + '명</p></div><button class="btn" type="button" data-a="lead">바꾸기</button></div>' +
        '<div class="sec">방침</div><div class="opts cpd">';
      for (i = 0; i < DIR_KEYS.length; i++) h += '<button class="opt' + (cp.dir === DIR_KEYS[i] ? ' on' : '') + '" type="button" data-a="dir" data-v="' + DIR_KEYS[i] + '"><b>' + CORPS_DIR[DIR_KEYS[i]] + '</b><small>' + DIR_SUB[DIR_KEYS[i]] + '</small></button>';
      h += '</div>';
      if (cp.dir === 'atk' && T) h += '<div class="cpg"><p>목표 <b>' + T.n + '</b> ' + (T.owner >= 0 ? facChip(T.owner) + ' 병력 ' + fmt(T.troops) + (corpsFoeK(T) >= 1.2 ? ' · 맹장 ' + foeBest(T) : '') : '<em class="advt">빈 거점</em>') + '<button class="btn sm" type="button" data-a="tgt">바꾸기</button></p><p class="note">' + corpsWaitText(cp) + '</p>' + (peaceWouldBreak(T.owner) ? '<p class="note pzw">먼저 치면 <b>' + facName(T.owner) + '군과의 보호가 풀립니다</b></p>' : '') + '</div>';
      else if (cp.dir === 'sup' && T) h += '<div class="cpg"><p>보낼 곳 <b>' + T.n + '</b> ' + (baseCorps(T) ? '<em class="advt">' + corpsName(baseCorps(T)) + '</em>' : '<em class="advt">직할</em>') + '<button class="btn sm" type="button" data-a="tgt">바꾸기</button></p><p class="note">한 달에 한 번, 지킬 만큼만 남기고 보냅니다</p></div>';
      if (cp.dir !== 'atk') h += '<div class="cpg cph"><p>출격 <b' + (corpsSortie(cp) ? '' : ' class="bad"') + '>' + (corpsSortie(cp) ? '허용' : '금지') + '</b>' + (cp.dir === 'dev' ? '' : '<button class="btn sm" type="button" data-a="hold">' + (cp.hold ? '허용으로' : '금지로') + '</button>') + '</p><p class="note">' +
        (cp.dir === 'dev' ? '내정 방침에서는 성 밖으로 나가 싸우지 않습니다 — 적이 오면 성이 스스로 막습니다. 나가서 막게 하려면 방침을 군비로 바꾸세요.' : (cp.hold ? '적이 다가와도 성 밖으로 나가 싸우지 않습니다(나가 있던 부대는 돌아옵니다).' : '적 부대가 성 가까이 오면 부대를 내어 막습니다.')) + '</p></div>';      // v0.18
      h += '<div class="sec">거점 <em class="cnt">' + bs.length + '</em><button class="btn sm" type="button" data-a="add">+ 넣기</button></div><div class="rows cpl">';
      for (i = 0; i < bs.length; i++) h += '<div class="row">' + thumb(bs[i].kind === 'city' ? 'city_' + bs[i].sz : 'gate') + '<span class="mid"><span class="nm">' + bs[i].n + '</span><span class="ds">' + SIZE_NAME[bs[i].sz] + ' · 병력 ' + fmt(bs[i].troops) + ' · 무장 ' + baseOfficers(bs[i]).length + '명</span></span><button class="btn" type="button" data-a="rel" data-v="' + bs[i].id + '">직할로</button></div>';
      h += '</div>';
      if (us.length) {
        h += '<div class="sec">부대 <em class="cnt">' + us.length + '</em></div><div class="rows cpl">';
        for (i = 0; i < us.length; i++) h += '<div class="row">' + porTag(uLeader(us[i])) + '<span class="mid"><span class="nm">' + uName(us[i]) + '</span><span class="ds">' + UNIT_TYPES[us[i].type].name + ' ' + fmt(us[i].troops) + '명 · ' + unitMission(us[i]) + '</span></span><button class="btn" type="button" data-a="take" data-v="' + us[i].id + '">직할로</button></div>';
        h += '</div>';
      }
      if (cp.note) h += '<div class="sec">지난 보고</div><p class="note cpn">' + (cp.note.s || '한 일 없음') + '</p>';
      return h + '<div class="cmds"><button class="cmd" type="button" data-a="disband"><b>해산</b><small>모두 직할로</small></button></div></div>';
    },
    on: {
      dir: function (el) {
        var cp = corpsById(id), k = el.getAttribute('data-v'); if (!cp) return;
        if (k === 'atk') return pickCorpsTarget(cp);
        if (k === 'sup') return pickCorpsDest(cp);
        if (cp.dir === k) return;
        var r = corpsSetDir(cp, k, -1); if (!r.ok) return toast(r.msg);
        sfx('ui'); corpsSaid(cp, k === 'dev' ? 'cdev' : 'carm', undefined, corpsName(cp) + ' 방침 — <b>' + CORPS_DIR[k] + '</b>'); corpsRefresh();
      },
      tgt: function () { var cp = corpsById(id); if (!cp) return; if (cp.dir === 'atk') pickCorpsTarget(cp); else pickCorpsDest(cp); },
      hold: function () { var cp = corpsById(id); if (!cp || cp.dir === 'dev' || cp.dir === 'atk') return; var r = corpsSetHold(cp, !cp.hold); sfx('ui'); toast(corpsName(cp) + ' — 출격 ' + (cp.hold ? '금지' + (r.back ? ' · ' + r.back + '개 부대를 불러들입니다' : '') : '허용'), 2400); corpsRefresh(); },
      lead: function () {
        var cp = corpsById(id); if (!cp) return;
        pickOfficers({ push: true, title: corpsName(cp) + ' — 군단장', list: corpsLeadCands(cp), max: 1, hi: 'ldr', key: corpsLeadScore, rtHead: '자리', rt: function (o) { return o.unit !== null ? '출진 중' : G.bases[o.loc].n; }, auto: function () { return corpsLeadCands(cp).slice(0, 1).map(function (o) { return o.id; }); }, preview: function (os) { return '행동력 +' + (CORPS_AP.base + CORPS_AP.city * corpsCities(cp).length + Math.floor(os[0].cha / 5)) + '/턴 <small>(매력 ' + os[0].cha + ')</small>'; }, ok: '맡기기' },
          function (os) { var r = corpsSetLead(cp, os[0].id); if (!r.ok) { toast(r.msg); return false; } sfx('ui'); showCorps(cp.id); talk(os[0], sayLine(os[0], 'corps'), josa(os[0].n, '이가') + ' ' + corpsName(cp) + '의 군단장이 되었습니다'); corpsRefresh(); return true; });      // 표는 창을 모두 닫으므로 군단 창을 다시 연다
      },
      add: function () { var cp = corpsById(id); if (cp) pickCorpsBase(cp); },
      rel: function (el) {
        var cp = corpsById(id), b = G.bases[+el.getAttribute('data-v')]; if (!cp || !b) return;
        var nm = corpsName(cp), r = corpsRelease(b.id); if (!r.ok) return toast(r.msg);
        sfx('ui'); toast(b.n + ' — 직할로 되돌렸습니다' + (r.gone ? ' (' + nm + ' 해산)' : ''));
        if (r.gone) closeDialog();
        corpsRefresh();
      },
      take: function (el) { var u = UMAP[+el.getAttribute('data-v')]; if (!u) return; var r = corpsTakeUnit(u); if (!r.ok) return toast(r.msg); sfx('ui'); toast(uName(u) + ' — 직할로 되돌렸습니다'); corpsRefresh(); },
      disband: function (el) {
        var cp = corpsById(id); if (!cp) return;
        if (!el.getAttribute('data-c')) { el.setAttribute('data-c', '1'); el.querySelector('b').textContent = '정말 해산?'; el.classList.add('pri'); return; }
        var nm = corpsName(cp); corpsDisband(cp); closeDialog(); sfx('ui'); toast(nm + ' 해산 — 거점과 부대를 모두 직할로 되돌렸습니다'); corpsRefresh();
      }
    }
  });
}
/* 그 거점을 지키는 가장 뛰어난 장수(무력·통솔 가운데 큰 쪽) — '필요'가 높은 까닭을 알린다 */
function foeBest(b) { var best = null, bv = 0; baseOfficers(b).forEach(function (o) { var v = Math.max(o.war, o.ldr); if (v > bv) { bv = v; best = o; } }); return best ? best.n : ''; }
/* 공격 목표 고르기: 가까운 곳부터, 거점마다 '필요' 병력 */
function pickCorpsTarget(cp) {
  var L = G.bases.filter(function (b) { return b.owner !== G.player; }).map(function (b) { return { b: b, o: corpsOutlook(cp, b) }; }).sort(function (x, y) { return x.o.len - y.o.len || x.b.id - y.b.id; }).slice(0, 14);
  showDialog({
    render: function () {
      var have = L.length ? L[0].o.have : 0, h = dlgHead(corpsName(cp) + ' — 어디를 칠까요') + '<div class="dlg-b"><p class="cap">지금 낼 수 있는 병력 <b>' + fmt(have) + '</b>. <b>필요</b>를 넘으면 군단장이 나섭니다.</p><div class="rows cptl">';
      for (var i = 0; i < L.length; i++) {
        var b = L[i].b, o = L[i].o, ok = o.have + o.going >= o.need;
        h += '<button class="row' + (cp.dir === 'atk' && cp.target === b.id ? ' sel' : '') + '" type="button" data-a="t" data-v="' + b.id + '">' + thumb(b.kind === 'city' ? 'city_' + b.sz : 'gate') + '<span class="mid"><span class="nm">' + b.n + ' ' + (b.owner >= 0 ? facChip(b.owner) : '<em class="advt">빈 거점</em>') + '</span><span class="ds">' + (b.owner >= 0 ? '병력 ' + fmt(b.troops) + ' · ' : '') + days(Math.max(1, Math.ceil(o.len / 5))) + ' 거리' + (peaceWouldBreak(b.owner) ? ' · <b class="bad">보호가 풀림</b>' : '') + (o.k >= 1.2 ? ' · 맹장 <b>' + foeBest(b) + '</b>' : '') + '</span></span><span class="rt' + (ok ? ' ok' : '') + '">필요 <b>' + fmt(o.need) + '</b></span></button>';
      }
      return h + '</div></div>';
    },
    on: { t: function (el) {
      var T = G.bases[+el.getAttribute('data-v')], r = corpsSetDir(cp, 'atk', T.id); if (!r.ok) return toast(r.msg);
      sfx('drum'); backDialog(); corpsSaid(cp, 'catk', T.n, corpsName(cp) + ' 방침 — <b>공격 → ' + T.n + '</b>'); corpsRefresh();
    } }
  }, true);
}
/* 지원할 곳 고르기: 이 군단 밖의 내 거점 */
function pickCorpsDest(cp) {
  var from = corpsBases(cp)[0], L = facBases(G.player).filter(function (b) { return b.corps !== cp.id; });
  if (!L.length) return toast('보낼 다른 거점이 없습니다');
  L.sort(function (x, y) { return (from ? hdist(from.c, from.r, x.c, x.r) - hdist(from.c, from.r, y.c, y.r) : 0) || x.id - y.id; });
  showDialog({
    render: function () {
      var h = dlgHead(corpsName(cp) + ' — 어디로 보낼까요') + '<div class="dlg-b"><p class="cap">병력 · 금 · 병량 · 병기를 한 달에 한 번 실어 보냅니다.</p><div class="rows">';
      for (var i = 0; i < L.length; i++) { var b = L[i], oc = baseCorps(b); h += '<button class="row' + (cp.dir === 'sup' && cp.target === b.id ? ' sel' : '') + '" type="button" data-a="d" data-v="' + b.id + '">' + thumb(b.kind === 'city' ? 'city_' + b.sz : 'gate') + '<span class="mid"><span class="nm">' + b.n + ' <em class="advt">' + (oc ? corpsName(oc) : '직할') + '</em></span><span class="ds">병력 ' + fmt(b.troops) + ' · 금 ' + fmt(b.gold) + ' · 병량 ' + fmt(b.food) + '</span></span><span class="rt">' + (from ? days(Math.max(1, Math.ceil(hdist(from.c, from.r, b.c, b.r) / 5))) : '') + '</span></button>'; }
      return h + '</div></div>';
    },
    on: { d: function (el) {
      var D = G.bases[+el.getAttribute('data-v')], r = corpsSetDir(cp, 'sup', D.id); if (!r.ok) return toast(r.msg);
      sfx('ui'); backDialog(); corpsSaid(cp, 'csup', D.n, corpsName(cp) + ' 방침 — <b>지원 → ' + D.n + '</b>'); corpsRefresh();
    } }
  }, true);
}
/* 군단에 거점 넣기: 이 군단 밖의 내 거점(직할이든 다른 군단의 것이든) */
function pickCorpsBase(cp) {
  showDialog({
    render: function () {
      var L = facBases(G.player).filter(function (b) { return b.corps !== cp.id; }), h = dlgHead(corpsName(cp) + ' — 넣을 거점') + '<div class="dlg-b"><div class="rows cpl">';
      for (var i = 0; i < L.length; i++) { var b = L[i], oc = baseCorps(b); h += '<div class="row">' + thumb(b.kind === 'city' ? 'city_' + b.sz : 'gate') + '<span class="mid"><span class="nm">' + b.n + ' <em class="advt">' + (oc ? corpsName(oc) : '직할') + '</em>' + (baseOfficers(b).some(isLord) ? ' <em class="advt">군주</em>' : '') + '</span><span class="ds">' + SIZE_NAME[b.sz] + ' · 병력 ' + fmt(b.troops) + ' · 무장 ' + baseOfficers(b).length + '명</span></span><button class="btn pri" type="button" data-a="b" data-v="' + b.id + '">넣기</button></div>'; }
      if (!L.length) h += '<p class="note">넣을 거점이 없습니다.</p>';
      return h + '</div></div>';
    },
    on: { b: function (el) { var b = G.bases[+el.getAttribute('data-v')], r = corpsAssign(cp, b.id); if (!r.ok) return toast(r.msg); sfx('ui'); corpsSaid(cp, 'corps', undefined, josa(b.n, '을를') + ' ' + corpsName(cp) + '에 맡겼습니다'); corpsRefresh(); } }
  }, true);
}
/* 새 군단: 맡길 직할 거점 고르기 */
function showCorpsNew(pre) {
  var sel = {};
  if (pre !== undefined && G.bases[pre] && !baseCorps(G.bases[pre])) sel[pre] = 1;
  showDialog({
    render: function () {
      var bs = directBases(G.player), i, n = 0, h = dlgHead('새 군단 — 맡길 거점') + '<div class="dlg-b"><p class="cap">고른 거점을 군단장이 방침대로 다스립니다. 언제든 직할로 되돌릴 수 있습니다.</p><div class="rows">';
      for (i = 0; i < bs.length; i++) {
        var b = bs[i], on = !!sel[b.id], os = baseOfficers(b);
        if (on) n++;
        h += '<button class="row' + (on ? ' sel' : '') + '" type="button" data-a="b" data-v="' + b.id + '">' + thumb(b.kind === 'city' ? 'city_' + b.sz : 'gate') + '<span class="mid"><span class="nm">' + b.n + (os.some(isLord) ? ' <em class="advt">군주</em>' : '') + '</span><span class="ds">' + SIZE_NAME[b.sz] + ' · 병력 ' + fmt(b.troops) + ' · 무장 ' + os.length + '명</span></span><span class="rt ck">' + (on ? '✓' : '') + '</span></button>';
      }
      return h + '</div></div><div class="dlg-f"><div class="pv">' + (n ? '거점 <b>' + n + '</b>곳' : '거점을 고르세요') + '</div><button class="btn pri" type="button" data-a="ok"' + (n ? '' : ' disabled') + '>군단 만들기</button></div>';
    },
    on: {
      b: function (el) { var id = +el.getAttribute('data-v'); if (sel[id]) delete sel[id]; else sel[id] = 1; refreshDialog(); },
      ok: function () {
        var ids = Object.keys(sel).map(Number); if (!ids.length) return;
        var r = corpsCreate(ids); if (!r.ok) return toast(r.msg, 3200);
        var cp = r.corps; sfx('drum'); closeDialog(); clearSel(); showHome(); showCorps(cp.id);
        corpsSaid(cp, 'corps', undefined, corpsName(cp) + ' — 거점 ' + ids.length + '곳을 맡았습니다'); corpsRefresh();
      }
    }
  });
}
