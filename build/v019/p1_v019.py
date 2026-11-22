# v0.19 — ① 무장 창: 병종 적성의 계산법 글을 빼고 열전을 넣는다(src/bios.js — 425명)
#         ② 영상: 제목 화면의 움직이는 그림 · 새 판의 오프닝 · 끝(천하통일 / 패망)  (src/cine.js + video/*.mp4 · *.webm)
#   · 열전은 무장 창과, 얼굴을 누르면 뜨는 무장 카드에 같이 나온다(둘 다 officerBody). 적성의 곱(C ×0.85 …)은 도움말로 옮겼다.
#   · 영상은 메뉴에서 끌 수 있다(UI.video). 파일이 없거나 틀 수 없으면 건너뛴다 — 한 파일로 만든 판(dist/index.html · offline.html)은 영상 없이 전처럼 돈다.
#   src/bios.js · src/cine.js 는 패치가 아니라 그대로 두는 새 소스다(build/v019/apply.sh 가 지우지 않는다).
#   CH_ROOT=<폴더> 로 다른 나무에 입힐 수 있다(시험용).
import io, os
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)

# ───────────────────────── data.js ─────────────────────────
s = rd('src/data.js')
s = rep(s, "var GAME_VERSION = 'v0.18.1';", "var GAME_VERSION = 'v0.19';")
wr('src/data.js', s)

# ───────────────────────── index.html ─────────────────────────
s = rd('src/index.html')
s = rep(s, '  <div id="title">\n', '  <div id="title">\n    <video id="tVid" preload="none" aria-hidden="true"></video>\n')
s = rep(s, '      <div class="t-ver" id="tVer"></div>\n    </div>\n  </div>\n</div>', '      <div class="t-ver" id="tVer"></div>\n    </div>\n  </div>\n  <div id="cine"></div>\n</div>')
wr('src/index.html', s)

# ───────────────────────── ui_panels.js ─────────────────────────
s = rd('src/ui_panels.js')
# ① 무장 창: 계산법 글을 빼고 열전
s = rep(s, """    '<p class="note aptn">부대의 공격·방어에 곱해집니다 — C ×' + APT_MUL.C + ' · B ×' + APT_MUL.B + ' · A ×' + APT_MUL.A + ' · S ×' + APT_MUL.S + ' (주장·부장 가운데 가장 높은 적성). 전법은 C 하나 · B 둘 · A부터 셋을 쓰고, 높을수록 잘 통합니다.</p>' +
    (o.sk ? '<p class="skp"><b class="hi">특기 · ' + o.sk + '</b><br>' + SKILLS[o.sk] + '</p>' : '<p class="note">특기 없음</p>') +
""", """    (o.sk ? '<p class="skp"><b class="hi">특기 · ' + o.sk + '</b><br>' + SKILLS[o.sk] + '</p>' : '<p class="note">특기 없음</p>') +
    (bioOf(o) ? '<div class="sec bioh">열전</div><p class="bio">' + bioOf(o) + '</p>' : '') +                  // v0.19: 어떤 사람인가(적성의 곱은 도움말로 옮겼다)
""")
s = rep(s, """줄마다 <b>병종 적성</b>(창 · 극 · 노 · 기 · 병기)과 특기가 함께 보입니다.</p>' +""",
        """줄마다 <b>병종 적성</b>(창 · 극 · 노 · 기 · 병기)과 특기가 함께 보입니다.</p>' +
  '<p><b>병종 적성</b>은 부대의 공격 · 방어에 곱해집니다 — C ×' + APT_MUL.C + ' · B ×' + APT_MUL.B + ' · A ×' + APT_MUL.A + ' · S ×' + APT_MUL.S + '(주장 · 부장 가운데 가장 높은 적성). 전법은 C 하나 · B 둘 · A부터 셋을 쓰고, 높을수록 잘 통합니다.</p>' +
  '<p><b>열전</b> — 무장 창과 무장 카드에는 그 사람이 누구인지 두세 문장이 붙습니다. 사서에 적힌 일을 바탕으로 했고, 연의나 민간 전승에만 나오는 사람 · 일은 그렇다고 적었습니다.</p>' +
  '<h3>영상</h3><p>제목 화면의 그림이 움직이고, 새 판을 시작할 때와 판이 끝날 때(천하통일 · 패망) 짧은 영상이 나옵니다. <b>화면을 누르면 건너뜁니다.</b> 메뉴의 <b>영상</b>에서 끌 수 있고, 기기에서 「동작 줄이기」를 켜 두었으면 나오지 않습니다. 소리는 없습니다(음악이 그대로 흐릅니다).</p>' +""")
# ② 제목 화면의 움직이는 그림
s = rep(s, """function showTitle() {
  ocardClose();
  $('title').classList.remove('off');
""", """function showTitle() {
  ocardClose();
  $('title').classList.remove('off');
  titleVideo(true);                                           // v0.19: 제목 그림이 움직인다
""")
s = rep(s, """function startGame() {
  ocardClose();
  $('title').classList.add('off');
""", """function startGame() {
  ocardClose();
  $('title').classList.add('off');
  titleVideo(false);
""")
s = rep(s, """  $('tNew').addEventListener('click', function () { audioInit(); playBgm('title'); sfx('ui'); showFactionSelect(); });""",
        """  titleVideo(true);                                           // v0.19: 처음 뜬 제목 화면
  $('tNew').addEventListener('click', function () { audioInit(); playBgm('title'); sfx('ui'); showFactionSelect(); });""")
# ② 오프닝
s = rep(s, """closeDialog(); keepPrev(); newGame(st.f); saveGame(); startGame(); sfx('gong'); showIntro(); }""",
        """closeDialog(); keepPrev(); newGame(st.f); saveGame(); startGame(); sfx('gong'); cinePlay('opening', { cap: '群雄割據', sub: '194년 — 천하는 어지럽고 영웅들이 일어선다' }, function () { showIntro(); }); }      // v0.19: 오프닝 영상(끄면 곧바로 다음 창)""")
# ② 끝
s = rep(s, """function showGameOver() {
  dropSave();
  var win = G.over === 'win';
  playBgm(win ? 'victory' : 'defeat', true);
  showDialog({""", """function showGameOver() {
  if (UI.ending === G && (CINE.on || MODAL)) return;         // v0.19: 끝 화면은 한 번만 연다(영상이 도는 동안 다시 불려도)
  UI.ending = G;
  dropSave();
  var win = G.over === 'win';
  playBgm(win ? 'victory' : 'defeat', true);
  cinePlay(win ? 'win' : 'lose', { cap: win ? '天下統一' : '敗亡', hold: true }, function () { showOverDialog(win); });      // 영상이 끝나면 그 마지막 장면 위에 창이 뜬다
}
function showOverDialog(win) {
  showDialog({""")
s = rep(s, """    on: { t: function () { closeDialog(); G = null; UI.ret = null; hideSheet(); showTitle(); playBgm('title'); } }""",
        """    on: { t: function () { closeDialog(); cineHide(); UI.ending = null; G = null; UI.ret = null; hideSheet(); showTitle(); playBgm('title'); } }""")
# ② 메뉴 · 기억
s = rep(s, """data-a="pct"><b>확률 표시</b><small>' + (UI.pct ? '숫자(%)' : '말로 가늠') + '</small></button>""",
        """data-a="pct"><b>확률 표시</b><small>' + (UI.pct ? '숫자(%)' : '말로 가늠') + '</small></button><button class="cmd" type="button" data-a="vid"><b>영상 ' + (UI.video === false ? '꺼짐' : '켜짐') + '</b><small>제목 · 오프닝 · 끝</small></button>""")
s = rep(s, """      pct: function () { UI.pct = !UI.pct; saveOpts();""", """      vid: function () { UI.video = UI.video === false; saveOpts(); toast(UI.video ? '영상 켬 — 제목 화면 · 새 판의 오프닝 · 끝' : '영상 끔', 2200); refreshDialog(); },
      pct: function () { UI.pct = !UI.pct; saveOpts();""")
s = rep(s, """pct: !!UI.pct, tback: !!UI.tback }));""", """pct: !!UI.pct, tback: !!UI.tback, video: UI.video !== false }));""")
s = rep(s, """    if (o.tback === true) UI.tback = true;""", """    if (o.video === false) UI.video = false;                   // v0.19: 영상 끔
    if (o.tback === true) UI.tback = true;""")
# ② 뒤로 · Esc 는 영상부터 건너뛴다
s = rep(s, """function appBack() {
  if (ocardOn()) { ocardClose(); return true; }""", """function appBack() {
  if (cineSkip()) return true;                                // v0.19: 도는 영상부터 건너뛴다
  if (ocardOn()) { ocardClose(); return true; }""")
s = rep(s, """    if (e.key !== 'Escape') return;
    if (ocardOn()) { ocardClose(); return; }""", """    if (e.key !== 'Escape') return;
    if (cineSkip()) return;
    if (ocardOn()) { ocardClose(); return; }""")
wr('src/ui_panels.js', s)

# ───────────────────────── style.css ─────────────────────────
s = rd('src/style.css')
s = rep(s, """.note.aptn { margin: 0 0 8px; }""", """.note.aptn { margin: 0 0 8px; }
/* v0.19 — 열전 */
.sec.bioh { margin-top: 10px; }
.bio { margin: 2px 0 10px; font: 500 14px/1.62 var(--font-body); color: var(--ink); word-break: keep-all; }
#ocard .bio { font-size: 13.5px; }""")
s += """
/* v0.19 — 영상. 제목: 그림(#title 의 바탕) 위에 같은 그림에서 뽑은 영상을 겹친다(돌기 시작하면 서서히 드러난다) */
#tVid { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: center top; opacity: 0; transition: opacity .9s ease; pointer-events: none; z-index: 0; }
#tVid.on { opacity: 1; }
.t-name { z-index: 1; }
.t-menu { position: relative; z-index: 1; }
/* 화면을 덮는 영상(오프닝 · 끝). 끝 화면에서는 마지막 장면을 남겨 그 위에 창이 뜬다(.held — 창 #modal 바로 아래) */
#cine { position: absolute; inset: 0; z-index: 60; display: none; background: #f1ecdf; overflow: hidden; }
#cine.on { display: block; }
#cine.held { z-index: 19; }
#cine video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; opacity: 0; transition: opacity .5s ease; }
#cine.play video { opacity: 1; }
#cine .cn-tx { position: absolute; left: 0; right: 0; top: 11%; text-align: center; pointer-events: none; opacity: 0; transition: opacity 1.4s ease .7s; }
#cine.play .cn-tx { opacity: 1; }
#cine .cn-tx b { display: block; font: 900 44px/1.15 var(--font-display); letter-spacing: .14em; margin-right: -.14em; color: #1b1a18; text-shadow: 0 0 16px #f4efe3, 0 0 5px #f4efe3; }
#cine .cn-tx span { display: block; margin-top: 12px; font: 700 14.5px var(--font-body); color: #2a2824; text-shadow: 0 0 9px #f4efe3, 0 0 3px #f4efe3; }
#cine .cn-skip { position: absolute; right: 12px; bottom: calc(14px + env(safe-area-inset-bottom, 0px)); padding: 9px 14px; font: 700 13px var(--font-body); color: #f4efe3; background: #1b1a18b3; border: 1px solid #f4efe366; border-radius: 3px; }
#cine.held .cn-skip { display: none; }
#cine.held .cn-tx { top: 7%; }
"""
wr('src/style.css', s)
print('ok')
