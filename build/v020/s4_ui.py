# v0.20 (4) 창과 판의 손질(스크립트 쪽)
#   · 아래 줄 맞춤(barFit) — s3_css.py 의 .t1 · .t2 · .t3 를 넘칠 때만 한 단계씩 붙인다
#   · 세력이 망하는 장면: 그림 자리가 비어 있었다(세력 번호 -1 로 자막을 띄워 초상이 없었다) — 망한 세력의 군주 초상을 띄운다(잿빛으로)
import io, os
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)

s = rd('src/ui_panels.js')
s = rep(s, """  $('btnNext').style.display = facUnits(G.player).length ? '' : 'none';
}
""", """  $('btnNext').style.display = facUnits(G.player).length ? '' : 'none';
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
""")
s = rep(s, "  window.addEventListener('resize', moreSoon);", "  window.addEventListener('resize', moreSoon);\n  window.addEventListener('resize', function () { if (typeof barFit === 'function') barFit(); });")
# 세력 멸망 장면의 그림
s = rep(s, """function setCaption(f, html, cls) {
  var F = f >= 0 ? G.factions[f] : null, L = F ? off(F.lord) : null, u = L ? POR_URL[L.por] : '';
""", """function setCaption(f, html, cls, porF) {
  var F = f >= 0 ? G.factions[f] : null, PF = porF >= 0 ? G.factions[porF] : F, L = PF ? off(PF.lord) : null, u = L ? POR_URL[L.por] : '';      // v0.20: porF = 그림만 이 세력의 군주로(멸망 장면)
  $('plPor').classList.toggle('gone', porF >= 0);
""")
s = rep(s, "    setCaption(-1, '<b>' + facName(e.f) + '군 멸망</b>', 'big'); sfx('gong');\n    pwait(1800, cb);",
        "    setCaption(-1, '<b>' + facName(e.f) + '군 멸망</b>', 'big', e.f); sfx('gong');\n    pwait(2200, cb);")
wr('src/ui_panels.js', s)

s = rd('src/style.css')
s = s.rstrip('\n') + """
/* v0.20 세력이 망하는 장면: 군주의 초상을 잿빛으로, 붉은 '亡' 낙관 */
#plPor.gone { filter: grayscale(1) contrast(.92) brightness(.96); }
.pl-main { position: relative; }
.pl-main:has(#plPor.gone)::after { content: '亡'; position: absolute; left: 72px; top: 70px; width: 26px; height: 26px; display: flex; align-items: center; justify-content: center; background: var(--seal); color: var(--seal-ink); font: 900 16px var(--font-display); border-radius: var(--rad-s); box-shadow: 0 1px 3px #1b1a1866; transform: rotate(-6deg); }
"""
wr('src/style.css', s)
print('s4 ok')
