# v0.19.1 — 오프닝 영상이 뚝 끊기지 않게: 끝나기 0.9초 전부터(누르면 그 자리에서) 서서히 걷힌다
#   그동안: 영상이 끝나거나 건너뛰면 덮고 있던 화면을 한 번에 치웠다 — 영상에서 지도로 갑자기 바뀌었다.
#   이제: 걷히기 시작할 때 다음 창(첫 창)을 그 아래에 먼저 띄우고, 영상은 그 위에서 투명해진다(저절로 끝날 때 0.9초 · 눌러 건너뛸 때 0.32초).
#         걷히는 동안에는 누름을 받지 않는다(아래의 창이 받는다). 끝 화면(천하통일 · 패망)은 전처럼 마지막 장면을 남긴다.
#   CH_ROOT=<폴더> 로 다른 나무에 입힐 수 있다(시험용).
import io, os
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)

s = rd('src/data.js')
s = rep(s, "var GAME_VERSION = 'v0.19';", "var GAME_VERSION = 'v0.19.1';")
wr('src/data.js', s)

s = rd('src/cine.js')
s = rep(s, """var CINE = { on: false, held: false, name: '', t: 0, fin: null, n: 0 };""",
        """var CINE = { on: false, held: false, name: '', t: 0, fin: null, n: 0 };
var CINE_FADE = { end: 900, skip: 320, lead: 0.9 };         // v0.19.1: 걷히는 시간(ms) — 저절로 끝날 때 · 눌러 건너뛸 때, 끝나기 몇 초 전부터 걷기 시작하는가""")
s = rep(s, """      if (opt.hold && !bad && box) { var v0 = box.querySelector('video'); if (v0) { try { v0.pause(); } catch (e) { /* */ } } box.classList.add('held'); CINE.on = false; CINE.held = true; }
      else cineHide();
""", """      if (opt.hold && !bad && box) { var v0 = box.querySelector('video'); if (v0) { try { v0.pause(); } catch (e) { /* */ } } box.classList.add('held'); CINE.on = false; CINE.held = true; }
      else if (bad || !box || !box.classList.contains('play')) cineHide();      // 돌지 못했다 — 걷을 것이 없다
      else cineFade(skipped ? CINE_FADE.skip : CINE_FADE.end, my);             // v0.19.1: 뚝 끊지 않고 서서히 걷는다(done 이 띄우는 다음 창이 그 아래에 먼저 선다)
""")
s = rep(s, """  v.addEventListener('ended', function () { fin(false); });
""", """  v.addEventListener('ended', function () { fin(false); });
  if (!opt.hold) v.addEventListener('timeupdate', function () { if (v.duration && isFinite(v.duration) && v.duration - v.currentTime <= CINE_FADE.lead) fin(false); });      // v0.19.1: 끝나기 조금 전부터 걷기 시작한다
""")
s = rep(s, """function cineHide() {
  var box = $('cine'); clearTimeout(CINE.t); CINE.on = false; CINE.held = false; CINE.fin = null;
  if (!box) return;
  var v = box.querySelector('video'); if (v) { try { v.pause(); } catch (e) { /* */ } }
  box.onclick = null; box.className = ''; box.innerHTML = '';
}""", """/* 덮고 있던 영상을 ms 동안 투명하게 걷는다. 걷히는 동안 영상은 남은 만큼 더 돌고, 누름은 아래의 화면이 받는다 */
function cineFade(ms, my) {
  var box = $('cine'); clearTimeout(CINE.t); CINE.on = false; CINE.held = false; CINE.fin = null;
  if (!box) return;
  box.onclick = null; box.style.transitionDuration = ms + 'ms'; box.classList.add('out');
  CINE.t = setTimeout(function () { if (my === CINE.n) cineHide(); }, ms + 80);
}
function cineHide() {
  var box = $('cine'); clearTimeout(CINE.t); CINE.on = false; CINE.held = false; CINE.fin = null;
  if (!box) return;
  var v = box.querySelector('video'); if (v) { try { v.pause(); } catch (e) { /* */ } }
  box.onclick = null; box.className = ''; box.style.transitionDuration = ''; box.innerHTML = '';
}""")
wr('src/cine.js', s)

s = rd('src/style.css')
s = rep(s, """#cine.on { display: block; }
""", """#cine.on { display: block; }
#cine { transition: opacity .9s ease; }                       /* v0.19.1: 끝날 때 서서히 걷힌다(시간은 cine.js 가 넣는다) */
#cine.out { opacity: 0; pointer-events: none; }
""")
wr('src/style.css', s)
print('ok')
