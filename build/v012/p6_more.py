# v0.12 (6/…): 아래에 더 있다는 표시  (ui_panels.js · style.css)
#  요청(15:55) "그리고 메뉴나 리스트가 아래에 더 있는지 잘 모를때가 많아"
#   창의 몸통(.dlg-b)과 아래 판의 몸통(.sh-body)은 내용이 길면 굴러가는데, 아래에 더 있다는 표시가 없었다(휴대폰에서는 굴림 막대가 평소에 보이지 않는다).
#   - 아래에 내용이 더 있으면 몸통의 아래 끝에 종이빛으로 흐려지는 띠와 [▼ 아래에 더 있습니다] 딱지를 띄운다. 끝까지 내리면 사라진다.
#   - 딱지를 누르면 한 화면쯤 내려간다.
#   - 창이나 판이 다시 그려질 때마다(#modal · #sheet 의 내용이 바뀔 때) 저절로 다시 붙는다 — 창마다 따로 손댈 것이 없다.
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)

p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "/* 창은 겹쳐 열 수 있다. push 로 열면 지금 창을 아래에 깔아 두고,",
           "/* ---------- 아래에 더 있다는 표시(v0.12) ----------\n"
           "   굴러가는 몸통(.dlg-b · .sh-body)의 맨 끝에 높이 0 인 붙박이(sticky) 토막을 넣는다 — 아래에 더 있을 때만 몸통의 아래 끝에 보인다. */\n"
           "var MORE_GAP = 10;                                                 // 이만큼(픽셀)도 안 남았으면 끝으로 본다\n"
           "function moreSet(body) {\n"
           "  var h = body.querySelector(':scope > .morehint'); if (!h) return;\n"
           "  h.classList.toggle('on', body.scrollHeight - body.scrollTop - body.clientHeight > MORE_GAP);\n"
           "}\n"
           "function moreScan() {\n"
           "  var list = document.querySelectorAll('#modal .dlg-b, #sheet .sh-body');\n"
           "  for (var i = 0; i < list.length; i++) (function (body) {\n"
           "    if (!body.querySelector(':scope > .morehint')) {\n"
           "      var h = document.createElement('div'); h.className = 'morehint'; h.setAttribute('aria-hidden', 'true'); h.innerHTML = '<i>▼ 아래에 더 있습니다</i>';\n"
           "      h.firstChild.addEventListener('click', function (e) { e.stopPropagation(); try { body.scrollBy({ top: Math.round(body.clientHeight * 0.8), behavior: 'smooth' }); } catch (err) { body.scrollTop += Math.round(body.clientHeight * 0.8); } });\n"
           "      body.appendChild(h);\n"
           "    }\n"
           "    if (!body._more) { body._more = true; body.addEventListener('scroll', function () { moreSet(body); }, { passive: true }); }\n"
           "    moreSet(body);\n"
           "  })(list[i]);\n"
           "}\n"
           "function moreSoon() { moreScan(); if (moreSoon.t) return; moreSoon.t = setTimeout(function () { moreSoon.t = 0; moreScan(); }, 350); }      // 곧바로(다시 그린 그 자리에서 — 깜빡이지 않게) + 그림이 늦게 뜨거나 판이 미끄러져 올라온 뒤에 한 번 더\n"
           "function moreInit() {\n"
           "  try { var mo = new MutationObserver(moreSoon); mo.observe($('modal'), { childList: true }); mo.observe($('sheet'), { childList: true }); } catch (e) { /* 표시는 없어도 된다 */ }\n"
           "  window.addEventListener('resize', moreSoon);\n"
           "  document.addEventListener('toggle', moreSoon, true);              // 접힌 풀이(<details>)를 펼쳤을 때\n"
           "}\n"
           "/* 창은 겹쳐 열 수 있다. push 로 열면 지금 창을 아래에 깔아 두고,")
s = rep(s, "  $('tShare').addEventListener('click', function () { audioInit(); sfx('ui'); shareGame(); });",
           "  $('tShare').addEventListener('click', function () { audioInit(); sfx('ui'); shareGame(); });\n  moreInit();")
s = rep(s, "<h3>공유</h3>", "<h3>긴 창</h3><p>창이나 아래 판의 내용이 화면보다 길면 아래 끝에 <b>▼ 아래에 더 있습니다</b>가 뜹니다. 밀어 올리거나 그 딱지를 누르면 내려갑니다.</p><h3>공유</h3>")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/style.css'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "/* 나갈 자리(v0.12): 성 둘레 여섯 칸 */",
           "/* 아래에 더 있다는 표시(v0.12) */\n"
           ".dlg-b { --mhx: 14px; --mhb: 12px; } .sh-body { --mhx: 12px; --mhb: 13px; }\n"
           ".morehint { position: sticky; bottom: calc(-1 * var(--mhb, 12px)); height: 0; z-index: 6; pointer-events: none; opacity: 0; transition: opacity .16s; }\n"
           ".morehint.on { opacity: 1; }\n"
           ".morehint::before { content: ''; position: absolute; left: calc(-1 * var(--mhx, 12px)); right: calc(-1 * var(--mhx, 12px)); bottom: 0; height: 54px; background: linear-gradient(to bottom, #f4efe300, #f4efe3f2 62%, #f4efe3); }\n"
           ".morehint i { position: absolute; left: 50%; bottom: 7px; transform: translateX(-50%); font: 800 12px var(--font-body); font-style: normal; white-space: nowrap; color: var(--paper); background: var(--ink); padding: 5px 13px; border-radius: 13px; box-shadow: 0 1px 5px #1b1a1855; }\n"
           ".morehint.on i { pointer-events: auto; cursor: pointer; animation: mhbob 1.6s ease-in-out infinite; }\n"
           "@keyframes mhbob { 0%, 100% { transform: translate(-50%, 0); } 50% { transform: translate(-50%, 3px); } }\n"
           "@media (prefers-reduced-motion: reduce) { .morehint.on i { animation: none; } }\n"
           "/* 나갈 자리(v0.12): 성 둘레 여섯 칸 */")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
