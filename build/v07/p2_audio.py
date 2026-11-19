# v0.7 소리: 녹음된 효과음(SFX_DATA) + 여러 곡이 돌아가는 배경 음악
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:80])
    return s.replace(a, b)
p = 'src/ui3d.js'; s = io.open(p, encoding='utf-8').read()

a = s.index("/* ---------- 소리 (잡음 기반 효과음) ---------- */")
b = s.index("/* ---------- 배경 음악 ----------")
new_sfx = r"""/* ---------- 소리 ----------
   효과음은 녹음된 소리다(src/sfxdata.js 의 SFX_DATA — 짧은 mp3 를 base64 로 담은 것). 처음 누를 때 풀어 둔다.
   아직 풀리지 않았거나 풀지 못한 소리만 예전의 만든 소리(잡음 + 사인파)로 대신한다. */
var AC = null, NOISE = null;
var SND = { buf: {}, off: {}, last: {}, bus: null, loaded: false, mv: null };
/* 장면 → 낼 소리들 [표본, 크기, 음높이 흔들림, 늦춤(초)]. gap = 같은 장면 소리를 다시 낼 수 있는 가장 짧은 간격(ms). syn = 표본이 없을 때 대신할 만든 소리 */
var CUES = {
  ui:       { s: [['tick', 0.5, 0.06]], gap: 50, syn: 'ui' },
  page:     { s: [['page', 0.55, 0.05]], gap: 150, syn: 'ui' },
  step:     { s: [['stomp', 0.5, 0.08]], gap: 60, syn: 'step' },
  hit:      { s: [['slash', 0.8, 0.06]], gap: 70, syn: 'hit' },
  counter:  { s: [['slash', 0.5, 0.05]], gap: 70, syn: 'hit' },
  arrowhit: { s: [['thud', 0.6, 0.1]], gap: 70, syn: 'hit' },
  siege:    { s: [['crush', 0.6, 0.05], ['thud', 0.7, 0.05, 0.03]], gap: 120, syn: 'hit' },
  big:      { s: [['crush', 0.95, 0.04], ['clang', 0.55, 0.05, 0.03]], gap: 120, syn: 'big' },
  great:    { s: [['crush', 1.0, 0.03], ['clang', 0.75, 0.04, 0.02], ['gong', 0.3, 0, 0.06]], gap: 200, syn: 'big' },
  fail:     { s: [['clang', 0.5, 0.05], ['thud', 0.55, 0.05, 0.03]], gap: 120, syn: 'fail' },
  miss:     { s: [['thud', 0.6, 0.05]], gap: 120, syn: 'fail' },
  fire:     { s: [['fire', 0.8, 0.04]], gap: 300, syn: 'fire' },
  douse:    { s: [['douse', 0.8, 0.03]], gap: 300, syn: 'fire' },
  wind:     { s: [['wind', 0.7, 0.04]], gap: 300, syn: 'fail' },
  drum:     { s: [['drum', 0.85, 0.03]], gap: 150, syn: 'drum' },
  drums:    { s: [['drums', 0.9, 0.02]], gap: 400, syn: 'drum' },
  horn:     { s: [['horn', 0.7, 0.01]], gap: 800, syn: 'drum' },
  deploy:   { s: [['drums', 0.85, 0.02], ['horn', 0.5, 0.01, 0.3]], gap: 600, syn: 'drum' },
  gong:     { s: [['gong', 0.8, 0.01]], gap: 500, syn: 'drum' },
  fall:     { s: [['fall', 0.95, 0]], gap: 1500, syn: 'fall' },
  capture:  { s: [['fall', 0.95, 0], ['cheer', 0.6, 0.02, 1.0]], gap: 1500, syn: 'fall' },
  cheer:    { s: [['cheer', 0.7, 0.02]], gap: 800, syn: 'drum' },
  rout:     { s: [['rout', 0.7, 0.03]], gap: 500, syn: 'big' },
  coin:     { s: [['coin', 0.7, 0.03]], gap: 200, syn: 'ui' },
  hammer:   { s: [['hammer', 0.8, 0.03]], gap: 300, syn: 'drum' },
  duel:     { s: [['duel', 0.95, 0.02]], gap: 800, syn: 'big' },
  shout:    { s: [['shout', 0.6, 0.05]], gap: 250, syn: '' },
  bow:      { s: [['bow', 0.7, 0.08]], gap: 60, syn: 'ui' },
  arrows:   { s: [['arrows', 0.8, 0.04]], gap: 200, syn: 'step' },
  charge:   { s: [['cavalry', 0.85, 0.03]], gap: 500, syn: 'step' }
};
function acMake() {
  if (AC) return AC;
  try {
    AC = new (window.AudioContext || window.webkitAudioContext)();
    var n = AC.sampleRate, b = AC.createBuffer(1, n, AC.sampleRate), d = b.getChannelData(0);
    for (var i = 0; i < n; i++) d[i] = Math.random() * 2 - 1;
    NOISE = b;
  } catch (e) { AC = null; }
  return AC;
}
function audioInit() { if (!UI.sound || !acMake()) return; sndLoad(); }
function sndBus() {                                           // 여러 소리가 겹쳐도 찢어지지 않게 한데 모아 누른다
  if (!SND.bus) {
    var g = AC.createGain(); g.gain.value = 0.9;
    try {
      var c = AC.createDynamicsCompressor();
      c.threshold.value = -10; c.knee.value = 8; c.ratio.value = 6; c.attack.value = 0.003; c.release.value = 0.2;
      g.connect(c); c.connect(AC.destination);
    } catch (e) { g.connect(AC.destination); }
    SND.bus = g;
  }
  return SND.bus;
}
function sndLoad() {
  if (SND.loaded || typeof SFX_DATA === 'undefined' || !AC) return;
  SND.loaded = true;
  Object.keys(SFX_DATA).forEach(function (k) {
    try {
      var bin = atob(SFX_DATA[k]), u8 = new Uint8Array(bin.length), i;
      for (i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
      var ok = function (b) {
        // mp3 를 풀면 앞에 짧은 무음이 붙는다 → 소리가 시작되는 곳부터 틀어 누른 순간과 맞춘다(최대 60ms)
        var d = b.getChannelData(0), lim = Math.min(d.length, Math.floor(b.sampleRate * 0.06)), j = 0;
        while (j < lim && Math.abs(d[j]) < 0.02) j++;
        SND.off[k] = j >= lim ? 0 : Math.max(0, j / b.sampleRate - 0.002);
        SND.buf[k] = b;
      }, bad = function () { /* 이 소리는 만든 소리로 대신한다 */ };
      var pr = AC.decodeAudioData(u8.buffer, ok, bad);
      if (pr && pr.catch) pr.catch(bad);
    } catch (e) { /* */ }
  });
}
function sndPlay(name, vol, jit, delay) {
  var b = SND.buf[name]; if (!b) return null;
  var s = AC.createBufferSource(); s.buffer = b;
  if (jit) s.playbackRate.value = 1 + (Math.random() * 2 - 1) * jit;
  var g = AC.createGain(); g.gain.value = vol;
  s.connect(g); g.connect(sndBus());
  s.start(AC.currentTime + (delay || 0), SND.off[name] || 0);
  return { s: s, g: g };
}
function nz(t, dur, type, freq, q, vol) {
  var s = AC.createBufferSource(); s.buffer = NOISE; s.loop = true;
  var f = AC.createBiquadFilter(); f.type = type; f.frequency.value = freq; f.Q.value = q;
  var g = AC.createGain(); g.gain.setValueAtTime(vol, t); g.gain.exponentialRampToValueAtTime(0.001, t + dur);
  s.connect(f); f.connect(g); g.connect(AC.destination); s.start(t, Math.random() * 0.5); s.stop(t + dur + 0.02);
}
function thump(t, f0, f1, dur, vol) {
  var o = AC.createOscillator(); o.type = 'sine'; o.frequency.setValueAtTime(f0, t); o.frequency.exponentialRampToValueAtTime(f1, t + dur);
  var g = AC.createGain(); g.gain.setValueAtTime(vol, t); g.gain.exponentialRampToValueAtTime(0.001, t + dur);
  o.connect(g); g.connect(AC.destination); o.start(t); o.stop(t + dur + 0.02);
}
function sfxSyn(kind) {                                       // 만든 소리(대신 쓰는 것)
  var t = AC.currentTime;
  if (kind === 'step') nz(t, 0.06, 'lowpass', 420, 0.7, 0.10);
  else if (kind === 'ui') nz(t, 0.035, 'bandpass', 1900, 1.2, 0.06);
  else if (kind === 'hit') { nz(t, 0.16, 'bandpass', 1100, 0.9, 0.34); nz(t + 0.03, 0.22, 'lowpass', 300, 0.7, 0.3); thump(t, 120, 48, 0.18, 0.5); }
  else if (kind === 'big') { nz(t, 0.3, 'bandpass', 800, 0.7, 0.45); thump(t, 110, 38, 0.4, 0.8); nz(t + 0.08, 0.5, 'lowpass', 220, 0.6, 0.4); }
  else if (kind === 'fire') { nz(t, 0.7, 'bandpass', 2600, 0.6, 0.16); nz(t, 0.9, 'lowpass', 500, 0.5, 0.18); }
  else if (kind === 'drum') { thump(t, 95, 42, 0.5, 0.8); nz(t, 0.12, 'lowpass', 260, 0.7, 0.25); }
  else if (kind === 'fall') { thump(t, 95, 40, 0.5, 0.8); thump(t + 0.28, 95, 40, 0.6, 0.8); nz(t, 0.9, 'lowpass', 350, 0.6, 0.3); }
  else if (kind === 'fail') nz(t, 0.2, 'lowpass', 240, 0.8, 0.2);
}
function sfx(kind) {
  if (!AC || !UI.sound) return;
  try {
    if (AC.state === 'suspended') AC.resume();
    var q = CUES[kind];
    if (!q) { sfxSyn(kind); return; }
    var now = performance.now();
    if (now - (SND.last[kind] || 0) < q.gap) return;
    SND.last[kind] = now;
    var n = 0;
    for (var i = 0; i < q.s.length; i++) if (sndPlay(q.s[i][0], q.s[i][1], q.s[i][2], q.s[i][3])) n++;
    if (!n && q.syn) sfxSyn(q.syn);
  } catch (e) { /* 소리는 없어도 된다 */ }
}
/* 부대가 움직이는 동안의 소리: 보병은 발소리, 기병은 말발굽, 충차·수송대는 수레. ms 뒤에 잦아든다 */
function sfxMoveStop(quick) {
  var m = SND.mv; SND.mv = null;
  if (!m || !AC) return;
  try { var t = AC.currentTime; m.g.gain.cancelScheduledValues(t); m.g.gain.setValueAtTime(Math.max(0.0001, m.g.gain.value), t); m.g.gain.exponentialRampToValueAtTime(0.0001, t + (quick ? 0.05 : 0.14)); m.s.stop(t + 0.2); } catch (e) { /* */ }
}
function sfxMove(type, ms) {
  if (!AC || !UI.sound) return;
  try {
    if (AC.state === 'suspended') AC.resume();
    sfxMoveStop(true);
    var name = type === 'cav' ? 'gallop' : (type === 'ram' || type === 'trans' ? 'cart' : 'march'), b = SND.buf[name];
    if (!b) { sfxSyn('step'); return; }
    var s = AC.createBufferSource(), g = AC.createGain(), t = AC.currentTime, dur = Math.max(0.25, ms / 1000), off = SND.off[name] || 0, vol = name === 'cart' ? 0.55 : 0.5;
    s.buffer = b; s.playbackRate.value = 1 + (Math.random() * 2 - 1) * 0.04;
    if (dur > b.duration - off - 0.3) { s.loop = true; s.loopStart = off + 0.05; s.loopEnd = Math.max(off + 0.4, b.duration - 0.45); }   // 길게 가면 가운데 토막을 되풀이
    g.gain.setValueAtTime(vol, t); g.gain.setValueAtTime(vol, t + Math.max(0.05, dur - 0.16)); g.gain.exponentialRampToValueAtTime(0.0001, t + dur + 0.06);
    s.connect(g); g.connect(sndBus()); s.start(t, off); s.stop(t + dur + 0.1);
    var m = { s: s, g: g }; SND.mv = m;
    s.onended = function () { if (SND.mv === m) SND.mv = null; };
  } catch (e) { /* */ }
}

"""
s = s[:a] + new_sfx + s[b:]

# 이동: 칸마다 내던 소리 대신 병과에 맞는 소리를 한 번
s = rep(s, "    if (i2 !== last) { last = i2; sfx('step'); if (typeof fxDust === 'function')", "    if (i2 !== last) { last = i2; if (typeof fxDust === 'function')")
s = rep(s, """  if (!vis.type) { var uu = UMAP[vis.id]; if (uu) hop = uu.type === 'cav' ? 0.16 : (uu.type === 'ram' || uu.type === 'trans' ? 0.04 : 0.10); }
""", """  var mtype = vis.type;
  if (!vis.type) { var uu = UMAP[vis.id]; if (uu) { mtype = uu.type; hop = uu.type === 'cav' ? 0.16 : (uu.type === 'ram' || uu.type === 'trans' ? 0.04 : 0.10); } }
  sfxMove(mtype, dur);
""")

# 배경 음악: 장면마다 여러 곡이 차례로
s = rep(s, """/* ---------- 배경 음악 ----------
   1) bgm/<이름>.mp3 가 같이 놓여 있으면 그 파일을 튼다(GitHub 등에 올릴 때 Suno 곡을 넣는 자리).
   2) 없으면 코드로 만든 음악을 튼다: 뜯는 현(Karplus–Strong), 피리, 북, 낮게 깔리는 현. 오음 음계. */
var BGM = { el: null, name: '', want: '', vol: 0.5, dead: {}, tok: 0, mode: '' };""", """/* ---------- 배경 음악 ----------
   1) 같이 놓인 bgm/<곡>.mp3 를 튼다. 장면(제목·평시·긴장·전투·승리·패배)마다 곡이 정해져 있고, 여러 곡이면 차례로 돌아간다.
   2) 파일이 없거나 틀 수 없으면 코드로 만든 음악을 튼다: 뜯는 현(Karplus–Strong), 피리, 북, 낮게 깔리는 현. 오음 음계. */
var BGM_TRACKS = { title: ['title'], field: ['field1', 'field2'], tense: ['tense'], battle: ['battle1', 'battle2'], victory: ['victory'], defeat: ['defeat'] };
var BGM = { el: null, name: '', want: '', vol: 0.5, dead: {}, tok: 0, mode: '', idx: {}, file: '' };""")

a = s.index("function synStart(name) {"); b = s.index("  try { if (AC.state === 'suspended') AC.resume(); } catch (e) { /* */ }\n  synStop();")
s = s[:a] + "function synStart(name) {\n  if (!acMake()) return;\n" + s[b:]

a = s.index("function playBgm(name, once) {"); b = s.index("function stopBgm() {")
new_bgm = """function playBgm(name, once) {
  BGM.want = name;
  if (!UI.music) { stopBgm(); return; }
  if (BGM.name === name) return;
  var a0 = BGM.el, was = BGM.mode === 'file' && a0 && !a0.paused;
  stopBgm(was);                                            // 틀던 곡이 있으면 끊지 않고 잦아들게 한 뒤 바꾼다
  var tok = BGM.tok; BGM.name = name;
  if (was) bgmFade(a0, 0, 320, function () { bgmTrack(name, once, true, tok); }, tok);
  else bgmTrack(name, once, true, tok);
}
/* 장면의 다음 곡을 튼다. 못 트는 곡은 건너뛰고, 다 못 틀면 만든 음악 */
function bgmTrack(name, once, fadeIn, tok) {
  if (tok !== BGM.tok) return;
  var list = (BGM_TRACKS[name] || [name]).filter(function (f) { return !BGM.dead[f]; });
  if (!list.length) { synStart(SYN_STYLE[name] ? name : 'field'); return; }
  var i = (BGM.idx[name] || 0) % list.length, file = list[i], a = bgmEl();
  BGM.idx[name] = i + 1; BGM.file = file;
  var next = function () { if (tok === BGM.tok && !BGM.dead[file]) { BGM.dead[file] = 1; bgmTrack(name, once, fadeIn, tok); } };
  a.loop = !once && list.length === 1;
  a.onerror = next;                                         // 파일이 없다 → 다음 곡, 없으면 만든 음악
  a.onended = function () { if (tok === BGM.tok && !once) bgmTrack(name, once, false, tok); };
  a.src = 'bgm/' + file + '.mp3';
  try { a.volume = fadeIn ? 0 : BGM.vol; } catch (e) { /* */ }
  var p = a.play();
  if (p && p.then) p.then(function () { if (tok === BGM.tok) { BGM.mode = 'file'; if (fadeIn) bgmFade(a, BGM.vol, 900, null, tok); } })
    .catch(function (e) { if (tok !== BGM.tok) return; if (e && e.name === 'NotAllowedError') BGM.name = ''; else if (!e || e.name !== 'AbortError') next(); });
}
"""
s = s[:a] + new_bgm + s[b:]
s = rep(s, """function stopBgm() {
  BGM.tok++; BGM.name = ''; BGM.mode = '';
  var a = BGM.el; if (a) { a.onerror = null; try { a.pause(); } catch (e) { /* */ } }""", """function stopBgm(keep) {
  BGM.tok++; BGM.name = ''; BGM.mode = '';
  var a = BGM.el; if (a) { a.onerror = null; a.onended = null; if (!keep) { try { a.pause(); } catch (e) { /* */ } } }""")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
