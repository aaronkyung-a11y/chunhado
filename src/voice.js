/* 삼국지 천하도 — 중국어 음성(v0.13)
   소리: src/voicedata.js 의 VOICE_DATA — '<갈래>_<상황>_<1|2>' → mp3(base64) 120개. VOICE_TEXT 는 그 대사 [中文, 뜻].
   갈래 다섯: 맹장 brave · 지장 sage · 군주 lord · 무장 gen · 여장 lady (voiceKind 가 무장마다 고른다)
   상황 열둘: 출진 deploy · 공격 attack · 전법 tactic · 대성공 great · 실패·피격 hurt · 적 부대 궤멸 rout · 거점 함락 fall · 퇴각 retreat
              · 일기토 duel · 계략 성공 ploy · 명령 받음 order · 등용에 응함 join
   voiceSay(o, sit, opt)  무장 o 가 한마디 한다. 못 하면(꺼 둠 · 소리를 아직 못 냄 · 더 무거운 말이 나오는 중) 조용히 넘어간다.
     opt.p      이 확률로만 말한다(같은 말이 너무 잦지 않게)
     opt.delay  이만큼 뒤에(밀리초)
     opt.at     [c, r] — 그 칸 위에 뜻(우리말)을 잠깐 띄운다
     opt.cap    function (뜻, 中文) — 뜻을 다른 곳에 적을 때
   화면의 소리일 뿐이라 판의 주사위(rnd)는 쓰지 않는다. 소리는 효과음과 같은 길(sndBus)로 나간다 — 효과음을 끄면 음성도 꺼진다. */
var VOICE = { buf: {}, order: [], cur: null, tok: 0, last: {}, alt: {}, said: 0 };
var SAYV = null;                                   // 방금 고른 대화창의 말(sayLine 이 적어 둔다) — talk 가 같은 무장의 것이면 음성을 붙인다
var VOICE_KEEP = 24;                               // 풀어서 쥐고 있는 소리의 수(나머지는 쓸 때 다시 푼다)
var VOICE_LADY = { '초선': 1, '축융': 1, '대교': 1, '소교': 1, '여령기': 1, '손상향': 1, '황월영': 1, '채염': 1, '왕이': 1, '마운록': 1, '견씨': 1 };
var VOICE_PRI = { fall: 5, duel: 5, join: 4, rout: 4, great: 4, tactic: 3, ploy: 3, retreat: 3, deploy: 2, order: 2, attack: 2, hurt: 1 };
/* 대화창의 말 갈래(SAY 의 열쇠) → 음성의 상황. 여기 없는 말에는 음성이 붙지 않는다 */
var VOICE_KEY = { deploy: 'deploy', joined: 'join', draft: 'order', patrol: 'order', train: 'order', produce: 'order', develop: 'order', merge: 'order', move: 'order', trans: 'order', advisor: 'order', trade: 'order', corps: 'order', cdev: 'order', carm: 'order', catk: 'order', csup: 'order', envoy: 'order' };
function voiceKind(o) {
  if (VOICE_LADY[o.n] || /^gf\d/.test(o.por || '')) return 'lady';
  if (o.war >= 88 && o.int < 72) return 'brave';             // 여포 · 장비 · 손책 같은 이는 군주여도 맹장의 목소리
  if (isLord(o)) return 'lord';
  if (o.war < 70 && o.int >= o.war) return 'sage';           // 싸움보다 머리를 쓰는 이
  return 'gen';
}
function voiceOn() { return UI.voice !== false && !!UI.sound && typeof VOICE_DATA !== 'undefined' && !!AC; }
function voiceBuf(name, cb) {
  var b = VOICE.buf[name]; if (b) { cb(b); return; }
  var d = VOICE_DATA[name]; if (!d) return;
  try {
    var bin = atob(d), u8 = new Uint8Array(bin.length), i;
    for (i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
    var ok = function (buf) {
      if (!VOICE.buf[name]) { VOICE.buf[name] = buf; VOICE.order.push(name); while (VOICE.order.length > VOICE_KEEP) delete VOICE.buf[VOICE.order.shift()]; }
      cb(buf);
    }, bad = function () { /* 이 말은 건너뛴다 */ };
    var pr = AC.decodeAudioData(u8.buffer, ok, bad);
    if (pr && pr.catch) pr.catch(bad);
  } catch (e) { /* */ }
}
function voiceStop(quick) {
  var c = VOICE.cur; VOICE.cur = null; VOICE.tok++;
  if (!c || !c.g || !AC) return;
  try { var t = AC.currentTime; c.g.gain.cancelScheduledValues(t); c.g.gain.setValueAtTime(Math.max(0.0001, c.g.gain.value), t); c.g.gain.exponentialRampToValueAtTime(0.0001, t + (quick ? 0.03 : 0.09)); c.s.stop(t + 0.12); } catch (e) { /* */ }
}
/* 칸 위에 잠깐 뜨는 뜻풀이(우리말) */
function voiceCap(c, r, text, delay) {
  try {
    var el = document.createElement('div'); el.className = 'flt vsay'; el.textContent = '「' + text + '」'; el.style.opacity = 0;
    $('fx').appendChild(el);
    UI.floats.push({ p: hexPos(c, r), el: el, t0: performance.now() + (delay || 0), dur: 1900, dy: -50 }); UI.render = true;
  } catch (e) { /* */ }
}
function voiceSay(o, sit, opt) {
  if (!o || !VOICE_PRI[sit] || !voiceOn()) return false;
  opt = opt || {};
  if (opt.p !== undefined && Math.random() >= opt.p) return false;
  var now = performance.now(), pri = VOICE_PRI[sit], cur = VOICE.cur, delay = opt.delay || 0, kind = voiceKind(o), key = kind + '_' + sit;
  if (now - (VOICE.last[o.id + ':' + sit] || 0) < 1200) return false;            // 같은 이의 같은 말이 겹쳐 불렸다
  if (cur && now + delay < cur.end) {                                              // 다른 말이 나오는 중
    if (pri <= cur.pri) return false;
    var left = cur.end - now;
    if (left <= Math.max(700, delay)) delay = Math.max(delay, left + 60);          // 곧 끝난다 → 그 뒤에 잇는다
    else voiceStop();                                                              // 길게 남았다 → 앞의 말을 줄이고 이 말을 한다
  }
  try {
    if (AC.state === 'suspended') AC.resume();
    var n = VOICE.alt[key] = VOICE.alt[key] ? 3 - VOICE.alt[key] : 1 + Math.floor(Math.random() * 2), name = key + '_' + n;
    if (!VOICE_DATA[name]) return false;
    var tok = ++VOICE.tok, slot = VOICE.cur = { pri: pri, end: now + delay + 1600, name: name, s: null, g: null };
    VOICE.last[o.id + ':' + sit] = now;
    voiceBuf(name, function (buf) {
      if (tok !== VOICE.tok || VOICE.cur !== slot || !voiceOn()) return;           // 그 사이에 다른 말이 차지했다
      var wait = Math.max(0, delay - (performance.now() - now)) / 1000, s = AC.createBufferSource(), g = AC.createGain();
      s.buffer = buf; g.gain.value = 0.95; s.connect(g); g.connect(sndBus()); s.start(AC.currentTime + wait);
      slot.s = s; slot.g = g; slot.end = performance.now() + (wait + buf.duration) * 1000;
      s.onended = function () { if (VOICE.cur === slot) VOICE.cur = null; };
      VOICE.said++;
      var tx = typeof VOICE_TEXT !== 'undefined' && VOICE_TEXT[name];
      if (tx) { if (opt.cap) setTimeout(function () { try { opt.cap(tx[1], tx[0]); } catch (e) { /* */ } }, wait * 1000); else if (opt.at) voiceCap(opt.at[0], opt.at[1], tx[1], wait * 1000); }
    });
    return name;
  } catch (e) { return false; }
}
/* 대화창이 뜰 때: 그 말이 sayLine 으로 방금 고른 것이면 갈래에 맞는 음성을 붙인다 */
function voiceTalk(o) {
  var v = SAYV; SAYV = null;
  if (!o || !v || v.o !== o.id || performance.now() - v.t > 150) return;
  var sit = VOICE_KEY[v.key];
  if (sit) voiceSay(o, sit, sit === 'order' ? { p: 0.7 } : null);
}
/* 싸움 한 번의 음성. phase 0 = 시작할 때(치는 쪽의 기합 — 말이 나갔으면 그 이름을 돌려준다), 1 = 맞은 뒤(결과에 따른 한마디). 내가 낀 싸움에만 붙는다 */
function voiceAct(res, phase) {
  if (!res || !voiceOn() || G.over) return false;
  if (res.af !== G.player && res.tf !== G.player) return false;
  var A = res.alead >= 0 ? off(res.alead) : null, T = res.tlead >= 0 ? off(res.tlead) : null, mineA = res.af === G.player;
  var a0 = [res.ac0, res.ar0], a1 = [res.ac1 !== undefined ? res.ac1 : res.ac0, res.ar1 !== undefined ? res.ar1 : res.ar0], t1 = [res.tc1 !== undefined ? res.tc1 : res.c, res.tr1 !== undefined ? res.tr1 : res.r];
  if (!phase) {
    if (!A) return false;
    if (res.kind === 'tactic') return voiceSay(A, 'tactic', { at: a0 });
    if (res.kind === 'attack') return voiceSay(A, 'attack', { at: a0, p: mineA ? 0.7 : 0.4 });
    return false;
  }
  if (res.fell) { if (A) voiceSay(A, 'fall', { at: a1, delay: 700 }); return; }
  if (res.tid >= 0 && res.tAlive === false) {                                   // 맞은 부대가 무너졌다: 친 쪽이 외치거나, 진 쪽이 물러나며 한마디
    if (A && (!T || Math.random() < 0.6)) voiceSay(A, 'rout', { at: a1, delay: 450 });
    else if (T) voiceSay(T, 'retreat', { at: [res.c, res.r], delay: 450 });
    return;
  }
  if (res.aAlive === false) { if (A) voiceSay(A, 'retreat', { at: a0, delay: 450 }); return; }
  if (res.kind === 'ploy') { if (A) voiceSay(A, res.success ? 'ploy' : 'hurt', { at: a0, delay: 350, p: res.success ? 1 : 0.6 }); return; }
  if (res.kind === 'tactic' && res.fail) { if (A) voiceSay(A, 'hurt', { at: a1, delay: 400, p: 0.7 }); return; }
  if (res.crit && A) { voiceSay(A, 'great', { at: a1, delay: 400 }); return; }
  var tu = res.tid >= 0 ? UMAP[res.tid] : null;
  if (T && tu && res.dmg && res.dmg >= 0.3 * (tu.troops + res.dmg)) voiceSay(T, 'hurt', { at: t1, delay: 450, p: 0.5 });      // 한 번에 셋 중 하나 넘게 잃었다
}
