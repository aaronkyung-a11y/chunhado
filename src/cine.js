/* 영상 (v0.19) — 제목 화면의 움직이는 그림 · 새 판의 오프닝 · 판의 끝(천하통일 / 패망).
   · 영상 파일은 HTML 옆의 video/ 폴더에서 읽는다(음악 bgm/ 과 같다): title · opening · win · lose, 저마다 .mp4(H.264) 와 .webm(VP9).
   · 파일이 없거나 틀 수 없으면 조용히 건너뛴다 — 제목 그림과 대화창은 전처럼 나온다. 글자는 영상에 넣지 않고 화면 위에 얹는다.
   · 틀지 않는 때: 메뉴에서 영상을 껐을 때(UI.video === false), 기기에서 '동작 줄이기'를 켰을 때.
   소리는 없다(무음 영상) — 음악은 전처럼 playBgm 이 튼다. */
var CINE = { on: false, held: false, name: '', t: 0, fin: null, n: 0 };
function videoOk() {
  if (UI.video === false) return false;
  try { if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) return false; } catch (e) { /* */ }
  return true;
}
function vidSet(v, name, bad) {                                // mp4 를 먼저, 못 트는 브라우저는 webm. 둘 다 안 되면 bad()
  v.muted = true; v.setAttribute('muted', ''); v.playsInline = true; v.setAttribute('playsinline', ''); v.setAttribute('webkit-playsinline', '');
  var a = document.createElement('source'), b = document.createElement('source');
  a.src = 'video/' + name + '.mp4'; a.type = 'video/mp4'; b.src = 'video/' + name + '.webm'; b.type = 'video/webm';
  b.addEventListener('error', function () { if (bad) bad(); });
  v.appendChild(a); v.appendChild(b);
}
/* 제목 화면: 그림(#title 의 바탕) 위에 같은 그림에서 뽑은 영상을 겹쳐 돌린다. 돌기 시작하면 서서히 드러난다 */
function titleVideo(on) {
  var v = $('tVid'); if (!v) return;
  if (!on || !videoOk()) { try { v.pause(); } catch (e) { /* */ } v.classList.remove('on'); return; }
  if (v.getAttribute('data-bad')) return;
  if (!v.getAttribute('data-set')) {
    v.setAttribute('data-set', '1'); v.loop = true;
    v.addEventListener('playing', function () { v.classList.add('on'); });
    vidSet(v, 'title', function () { v.setAttribute('data-bad', '1'); v.classList.remove('on'); });
  }
  try { var p = v.play(); if (p && p.catch) p.catch(function () { /* 자동 재생이 막혔다 — 그림 그대로 */ }); } catch (e) { /* */ }
}
/* 화면을 덮는 영상 한 편.  name = opening | win | lose
   opt = { cap: 큰 글(한자), sub: 작은 글, hold: 끝난 뒤 마지막 장면을 바탕으로 남긴다(끝 화면 — 그 위에 창이 뜬다) }
   끝나거나 · 건너뛰거나(아무 데나 누른다) · 틀 수 없으면 done(skipped) 을 꼭 한 번 부른다 */
function cinePlay(name, opt, done) {
  opt = opt || {};
  var box = $('cine'), called = false, bad = false, my = ++CINE.n;
  function fin(skipped) {
    if (called) return; called = true; clearTimeout(CINE.t); CINE.fin = null;
    if (my === CINE.n) {
      if (opt.hold && !bad && box) { var v0 = box.querySelector('video'); if (v0) { try { v0.pause(); } catch (e) { /* */ } } box.classList.add('held'); CINE.on = false; CINE.held = true; }
      else cineHide();
    }
    if (done) done(!!skipped);
  }
  if (!box || !videoOk()) { if (done) done(true); return; }
  cineHide(); CINE.n = my;
  CINE.on = true; CINE.held = false; CINE.name = name; CINE.fin = fin;
  box.innerHTML = '<video preload="auto" aria-hidden="true"></video><div class="cn-tx">' + (opt.cap ? '<b>' + opt.cap + '</b>' : '') + (opt.sub ? '<span>' + opt.sub + '</span>' : '') + '</div><button type="button" class="cn-skip">건너뛰기 ▸</button>';
  var v = box.querySelector('video');
  box.className = 'on';
  v.addEventListener('playing', function () {
    box.classList.add('play'); clearTimeout(CINE.t);
    CINE.t = setTimeout(function () { fin(false); }, ((v.duration && isFinite(v.duration)) ? v.duration : 10) * 1000 + 1500);      // ended 가 오지 않을 때를 대비
  });
  v.addEventListener('ended', function () { fin(false); });
  vidSet(v, name, function () { bad = true; fin(true); });
  CINE.t = setTimeout(function () { if (!box.classList.contains('play')) { bad = true; fin(true); } }, 3500);                      // 3.5초 안에 돌지 않으면 건너뛴다
  box.onclick = function () { if (!CINE.held) fin(true); };
  try { var p = v.play(); if (p && p.catch) p.catch(function () { bad = true; fin(true); }); } catch (e) { bad = true; fin(true); }
}
function cineSkip() { if (CINE.on && CINE.fin) { CINE.fin(true); return true; } return false; }      // Esc · 휴대폰의 뒤로
function cineHide() {
  var box = $('cine'); clearTimeout(CINE.t); CINE.on = false; CINE.held = false; CINE.fin = null;
  if (!box) return;
  var v = box.querySelector('video'); if (v) { try { v.pause(); } catch (e) { /* */ } }
  box.onclick = null; box.className = ''; box.innerHTML = '';
}
