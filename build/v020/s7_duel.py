# v0.20 (7) 일기토 · 설전 화면의 아래쪽 — 합마다 적히는 기록
#   "일기토가 아래 쪽이 너무 아무것도 없는데?" — 지켜보기만 하는 판(맡긴 일기토 · 다시 보기)에서는 수를 고르는 단추가 없어 화면 아래 절반이 비어 있었다.
#   · 합별 기록: 합마다 두 사람이 낸 수(攻 守 必 …)와 누가 얼마를 잃었는지가 한 줄씩 쌓인다(새 합이 위).
#   · 지켜보는 판에서는 초상을 조금 키우고, 바닥에 옅은 붓글씨(一騎討 · 舌戰)를 깐다.
import io, os
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)

s = rd('src/duel.js')
s = rep(s, "  e.className = 'on ' + S.kind;\n", "  e.className = 'on ' + S.kind + (human ? '' : ' watch');      // v0.20: 지켜보는 판(.watch)\n")
s = rep(s, """    '<div class="du-res" id="duRes"></div></div>';""",
        """    '<div class="du-log" id="duLog"><div class="du-logh"><span>' + off(S.a.id).n + '</span><b>합별 기록</b><span>' + off(S.d.id).n + '</span></div><ol id="duLogL"></ol><i class="du-wm" aria-hidden="true">' + (S.kind === 'duel' ? '一騎討' : '舌戰') + '</i></div>' +
    '<div class="du-res" id="duRes"></div></div>';""")
s = rep(s, """function duBars() {""", """/* v0.20 합별 기록 한 줄: 두 사람의 수와 결과(새 합이 위에 쌓인다) */
function duLogRow(R) {
  var L = $('duLogL'); if (!L || !DU) return;
  var S = DU.S, K = DUEL_KIND[S.kind], w = R.win, mid;
  function mv(m, side) { var g = '<i class="g ' + m + '">' + K.moves[m].han + '</i>', nm = '<em>' + K.moves[m].name + '</em>'; return '<span class="' + side + (w === side ? ' win' : '') + '">' + (side === 'a' ? g + nm : nm + g) + '</span>'; }
  if (R.how === 'rest') mid = '<b class="heal">숨 고름 +' + R.heal + '</b>';
  else if (R.how === 'both') mid = '<b>-' + R.toA + ' · -' + R.toD + '</b>';
  else mid = w === 'a' ? '<b class="hit">▶ -' + R.toD + '</b>' : '<b class="hit">-' + R.toA + ' ◀</b>';
  var li = document.createElement('li'); li.className = 'w' + (w || 'x');
  li.innerHTML = '<span class="n">' + R.n + K.unit + '</span>' + mv(R.ma, 'a') + '<span class="m">' + mid + '</span>' + mv(R.md, 'd');
  L.insertBefore(li, L.firstChild);
}
function duBars() {""")
s = rep(s, "  at(620, duBars);\n", "  at(620, duBars);\n  at(640, function () { duLogRow(R); });\n")
wr('src/duel.js', s)

s = rd('src/style.css')
s = s.rstrip('\n') + """
/* ── v0.20 일기토 · 설전: 합별 기록(화면 아래) ── */
.du-in { min-height: 0; }
.du-log { position: relative; flex: 1 1 0; min-height: 0; margin-top: 10px; overflow: hidden; display: flex; flex-direction: column; }
.du-logh { display: flex; align-items: baseline; gap: 8px; padding: 0 2px 5px; font: 700 12px var(--font-body); color: var(--dim); position: relative; }
.du-logh::after { content: ''; position: absolute; left: 0; right: 0; bottom: -2px; height: 5px; background: var(--stroke-b) center / 100% 100% no-repeat; opacity: .7; }
.du-logh b { flex: none; font: 900 13px var(--font-display); color: var(--ink); letter-spacing: .1em; }
.du-logh span { flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; } .du-logh span:last-child { text-align: right; }
.du-log ol { list-style: none; margin: 4px 0 0; padding: 0; overflow: hidden; position: relative; z-index: 1; }
.du-log li { display: grid; grid-template-columns: 34px 1fr auto 1fr; align-items: center; gap: 6px; padding: 5px 2px; border-bottom: 1px solid var(--line); font-size: 13px; animation: duRow .32s cubic-bezier(.2, .9, .3, 1); }
.du-log li .n { font: 900 12.5px var(--font-display); color: var(--dim); }
.du-log li .a, .du-log li .d { display: flex; align-items: center; gap: 5px; min-width: 0; color: var(--dim); } .du-log li .d { justify-content: flex-end; }
.du-log li em { font-style: normal; font-weight: 700; white-space: nowrap; }
.du-log li .win em { color: var(--ink); font-weight: 900; }
.du-log li .g { flex: none; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font: 900 14px var(--font-display); font-style: normal; color: var(--paper); background: var(--ink); border-radius: var(--rad-s); opacity: .55; }
.du-log li .win .g { opacity: 1; } .du-log li .g.sp, .du-log li .g.tide { background: var(--seal); } .du-log li .g.def, .du-log li .g.gain { background: #2f4f6f; }
.du-log li .m { text-align: center; min-width: 78px; font-variant-numeric: tabular-nums; }
.du-log li .m b { font: 900 14px var(--font-display); color: var(--ink); } .du-log li .m b.hit { color: var(--seal); } .du-log li .m b.heal { color: #2f4f6f; font-size: 12.5px; }
.du-log li:first-child { background: #fffdf6a6; }
@keyframes duRow { from { opacity: 0; transform: translateY(-8px); } to { opacity: 1; transform: none; } }
.du-wm { position: absolute; left: 0; right: 0; bottom: 4px; text-align: center; font: 900 clamp(54px, 21vw, 104px)/1 var(--font-display); font-style: normal; letter-spacing: .14em; color: #1b1a180d; pointer-events: none; white-space: nowrap; }
#duel.talk .du-wm { color: #2f4f6f12; }
#duel.watch .du-por { height: min(37vh, 60vw); }
.du-res.on { position: relative; left: auto; right: auto; bottom: auto; order: 5; margin-top: 10px; } .du-log { order: 6; }      /* 끝나면 결과가 기록 위에 선다(기록을 덮지 않게) */
#duel.watch .du-hint:empty, #duel.watch .du-moves:empty, #duel.watch .du-foot:empty { display: none; }
#duel:not(.watch) .du-log { margin-top: 6px; } #duel:not(.watch) .du-wm { display: none; }
@media (prefers-reduced-motion: reduce) { .du-log li { animation: none; } }
"""
wr('src/style.css', s)
print('s7 ok')
