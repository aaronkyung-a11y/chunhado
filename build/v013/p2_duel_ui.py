# v0.13 (2/…): 대결 화면을 싸움터와 등용에 물린다  (ui_panels.js · style.css)   — 화면 자체는 src/duel.js (새 파일)
#   - 내가 직접 건 공격 · 전법에서 일기토가 벌어지면: 공격 연출이 끝난 뒤 일기토 화면이 열리고, 내가 수를 고른다. 끝나면 결과를 부대에 입힌다.
#       (AI 가 건 싸움 · 군단의 싸움에서 벌어진 일기토는 전처럼 저절로 판정된다 — 판정의 규칙은 같다.)
#   - 대상 창에 [일기토](신청): 응할 확률을 보여 준다. 응하지 않으면 그렇다고 알리고 끝난다.
#   - 등용: 보낼 무장을 고르는 표에 [설전] — 확률이 10% 이상 100% 미만일 때. 설전을 이기면 등용, 지거나 비기면 거절(충성 +, 다시 권하려면 기다린다 — 주사위로 실패한 것과 같다).
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)

p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()
# 대상 창: 일기토 신청
s = rep(s, "    for (i = 0; i < 3; i++) {\n      var pl = PLOYS[i], inP = ployTargets(u, pl).some(function (x) { return x.u === t.u; });",
           "    var chOk = challengeTargets(u).some(function (x) { return x.u === t.u; }), chW = uLeader(u).war + ' : ' + uLeader(t.u).war;      // 일기토 신청(v0.13)\n"
           "    out.push({ kind: 'challenge', label: '일기토', sub: !chOk ? (d > 1 ? '옆 칸에서만' : '응할 수 없는 상대') : (u.morale < DUEL_K.ask ? '기력 부족' : '응할 확률 <em class=\"pc\">' + challengeChance(u, t.u) + '%</em> · 무력 ' + chW), ok: chOk && u.morale >= DUEL_K.ask });\n"
           "    for (i = 0; i < 3; i++) {\n      var pl = PLOYS[i], inP = ployTargets(u, pl).some(function (x) { return x.u === t.u; });")
# 결과의 말
s = rep(s, "  if (res.duel) msg += ' · 일기토! ' + res.duel.a + ' 대 ' + res.duel.d + ' — ' + (res.duel.win ? res.duel.a : res.duel.d) + ' 승';",
           "  if (res.duel) msg += duelTxt(res.duel);")
s = rep(s, "function presentResult(name, res, quiet) {",
           "function duelTxt(d) { return ' · 일기토! ' + d.a + ' 대 ' + d.d + ' — ' + (d.draw ? '비김' : (d.win ? d.a : d.d) + ' 승' + (d.ko ? '(쓰러뜨림)' : '')); }\n"
           "/* 일기토가 끝난 뒤 화면에 적는 것: 두 부대가 얻고 잃은 것 */\n"
           "function duelOutHtml(S, o, an, dn) {\n"
           "  if (!o) return '';\n"
           "  if (o.draw) return '<p>두 주장 모두 공적 +' + DUEL_K.drawMerit + '</p>';\n"
           "  var wn = o.win ? an : dn, ln = o.win ? dn : an;\n"
           "  return '<p><b>' + ln + '</b> 기력 -' + (o.ko ? DUEL_K.koMor : DUEL_K.morLose) + ' · 병력 -' + fmt(o.loss) + (o.confused ? ' · 혼란 ' + days(DUEL_K.koTurns) : '') + '</p><p><b>' + wn + '</b> 기력 +' + DUEL_K.morWin + ' · 주장 공적 +' + DUEL_K.merit + '</p>';\n"
           "}\n"
           "function presentResult(name, res, quiet) {")
s = rep(s, "  if (res.duel) floatText(res.duel.win ? tc : ac, res.duel.win ? tr : ar, '일기토 패 -' + fmt(res.duel.loss), C_INK, 1150, true, -8);",
           "  if (res.duel && !res.duel.draw) floatText(res.duel.win ? tc : ac, res.duel.win ? tr : ar, '일기토 패 -' + fmt(res.duel.loss), C_INK, 1150, true, -8);")
# 행동: 내가 건 싸움의 일기토는 화면에서
s = rep(s, "  if (a.kind === 'attack') res = unitAttack(u, t);\n  else if (a.kind === 'tactic') res = unitTactic(u, a.tac, t);\n  else res = unitPloy(u, a.ploy, t);\n  if (!res.ok) { toast(res.msg); return; }\n",
           "  var an = uName(u), dn = t.u ? uName(t.u) : '';\n"
           "  DUEL_DEFER = a.kind !== 'ploy';                                  // 내가 직접 건 싸움에서 벌어진 일기토는 여기서 끝내지 않고 화면에서 수를 고른다(v0.13)\n"
           "  try {\n"
           "    if (a.kind === 'attack') res = unitAttack(u, t);\n    else if (a.kind === 'tactic') res = unitTactic(u, a.tac, t);\n    else if (a.kind === 'challenge') res = unitChallenge(u, t);\n    else res = unitPloy(u, a.ploy, t);\n"
           "  } finally { DUEL_DEFER = false; }\n"
           "  if (!res.ok) { toast(res.msg); return; }\n"
           "  function duelThen(next) {                                        // 일기토가 벌어졌으면: 화면 → 결과를 부대에 입힌다 → next\n"
           "    var S = res.duelS; if (!S) return next();\n"
           "    duelOpen(S, 'a', { sub: an + ' 대 ' + dn, onEnd: function () { return duelOutHtml(S, duelFinish(S, res), an, dn); } }, function () { syncScene(); next(); });\n"
           "  }\n"
           "  if (a.kind === 'challenge') {                                    // 일기토 신청: 공격 연출 없이 곧바로\n"
           "    UI.battleTurn = G.turn; playBgm('battle'); UI.rc = null; UI.atk = null; UI.target = null; requestDraw();\n"
           "    if (!res.accepted) {\n"
           "      floatText(t.c, t.r, '일기토 거절', C_DIM0, 0, true, -20); floatText(t.c, t.r, '기력 -' + res.mor, C_PLOY0, 320, false, 22); sfx('miss');\n"
           "      talk(uLeader(t.u), '…상대할 까닭이 없다.', josa(dn, '이가') + ' 일기토를 받지 않았습니다 — 기력 -' + res.mor + ' (응할 확률 ' + res.p + '%)', 3400);\n"
           "      clearSel(); afterAction(); return;\n"
           "    }\n"
           "    UI.busy = true;\n"
           "    duelThen(function () { UI.busy = false; toast(name + duelTxt(res.duel).replace(' · ', ' — '), 3200); clearSel(); afterAction(); });\n"
           "    return;\n"
           "  }\n")
s = rep(s, "    animAct(res, function () {\n      UI.busy = false;\n      if (fellB) fxFall(fellB, fellB.kind === 'gate' ? '점령' : '함락');\n      if (miss) talk(pa.adv, miss, msg, 3600); else toast(msg, 3200);\n      clearSel();\n      if (fellB && fellB.owner === G.player) selectBase(fellB);\n      back();\n      afterAction();\n    }, function () { resultFx(res); });",
           "    animAct(res, function () {\n      duelThen(function () {\n        UI.busy = false;\n        if (res.duelS && res.duel) msg += duelTxt(res.duel) + (res.duelS.done && (res.killed || res.selfDead) ? ' · 궤멸!' : '');\n"
           "        if (fellB) fxFall(fellB, fellB.kind === 'gate' ? '점령' : '함락');\n        if (miss) talk(pa.adv, miss, msg, 3600); else toast(msg, 3200);\n        clearSel();\n        if (fellB && fellB.owner === G.player) selectBase(fellB);\n        back();\n        afterAction();\n      });\n    }, function () { resultFx(res); });")
s = rep(s, "function doAct(a) {\n", "var C_DIM0 = '#6a645a', C_PLOY0 = '#2f4f6f';\nfunction doAct(a) {\n")
# 지난 열흘의 재생: 내 부대가 얽힌 일기토(AI 가 건 싸움 · 내 군단의 싸움)는 화면으로 다시 보여 준다
s = rep(s, "      animAct(e.res, pg(function () { P.ans = []; requestDraw(); pwait((e.res.fell ? 200 : 700) * k, cb); }), function () { resultFx(e.res); });",
           "      animAct(e.res, pg(function () {\n"
           "        P.ans = []; requestDraw();\n"
           "        var rec = e.res.duelRec;\n"
           "        if (rec && e.res.duel && !P.skip && (e.f === G.player || e.tf === G.player)) {      // v0.13: 내 부대가 얽힌 일기토는 처음부터 다시 그려 보인다\n"
           "          duelReplay(rec, { sub: e.name + ' 대 ' + (e.res.tname || ''), out: duelOutHtml(null, e.res.duel, e.name, e.res.tname || '') }, pg(function () { pwait(300 * k, cb); }));\n"
           "          return;\n"
           "        }\n"
           "        pwait((e.res.fell ? 200 : 700) * k, cb);\n"
           "      }), function () { resultFx(e.res); });")
s = rep(s, "  P.skip = true; $('veil').classList.add('on');\n  playNudge();",
           "  P.skip = true; $('veil').classList.add('on');\n  if (typeof DU !== 'undefined' && DU && DU.rec) duClose();              // 일기토를 다시 보던 중이면 닫고 넘어간다\n  playNudge();")
# 무장 고르는 표: 덧붙는 단추(opts.alt = { label, can(os), why(os), go(os) })
s = rep(s, "        (opts.auto ? '<button class=\"btn auto\" type=\"button\" data-a=\"auto\">자동</button>' : '') +\n        '<button class=\"btn pri\" type=\"button\" data-a=\"ok\"",
           "        (opts.auto ? '<button class=\"btn auto\" type=\"button\" data-a=\"auto\">자동</button>' : '') +\n"
           "        (opts.alt ? '<button class=\"btn alt' + (os.length >= min && opts.alt.can(os) ? '' : ' off') + '\" type=\"button\" data-a=\"alt\">' + opts.alt.label + '</button>' : '') +\n"
           "        '<button class=\"btn pri\" type=\"button\" data-a=\"ok\"")
s = rep(s, "      ok: function () {\n        if (sel.length < min) return;\n        var os = sel.map(off);\n        if (opts.keep) { cb(os); return; }",
           "      alt: function () {                                           // 덧붙는 단추(등용의 [설전] 등): 표를 닫고 그 일을 한다\n"
           "        if (sel.length < min) return toast('무장을 먼저 고르세요');\n"
           "        var os = sel.map(off);\n"
           "        if (!opts.alt.can(os)) return toast(opts.alt.why(os), 3000);\n"
           "        closeDialog(); opts.alt.go(os);\n"
           "      },\n"
           "      ok: function () {\n        if (sel.length < min) return;\n        var os = sel.map(off);\n        if (opts.keep) { cb(os); return; }")
# 등용: [설전]
s = rep(s, "        say: function (os) { return advSay(recruitAdvice(b, os[0], t), josa(t.n, '은는'), '응할 것입니다.', '응하지 않을 것입니다.'); } },\n        function (os) {",
           "        say: function (os) { return advSay(recruitAdvice(b, os[0], t), josa(t.n, '은는'), '응할 것입니다.', '응하지 않을 것입니다.'); },\n"
           "        alt: { label: '설전',\n"
           "          can: function (os) { return talkRecruitOk(b, os[0], t) && G.factions[b.owner].ap >= AP.recruit; },\n"
           "          why: function (os) { var p0 = recruitChance(b, os[0], t); return G.factions[b.owner].ap < AP.recruit ? '행동력이 부족합니다' : (p0 >= 100 ? '설전이 필요 없습니다 — 그냥 권하면 응합니다' : '말이 통할 상대가 아닙니다 — 등용 확률이 ' + DUEL_K.talkMin + '% 이상일 때만 설전을 걸 수 있습니다'); },\n"
           "          go: function (os) { flowTalkRecruit(b, os[0], t); } } },\n        function (os) {")
s = rep(s, "function flowRecruit(b) {\n",
           "/* 설전으로 등용(v0.13): 주사위 대신 설전의 승패로 정한다. 이기면 합류, 지거나 비기면 거절(주사위로 실패한 것과 같은 뒷일) */\n"
           "function flowTalkRecruit(b, o, t) {\n"
           "  var S = talkRecruitNew(b, o, t), farT = t.st === 'active', r = null;\n"
           "  duelOpen(S, 'a', { sub: t.n + ' 등용 · 그냥 권하면 ' + S.rp + '%',\n"
           "    onEnd: function () {\n"
           "      r = cmdRecruit(b, o.id, t.id, S);\n"
           "      if (!r.ok) return '<p class=\"bad\">' + r.msg + '</p>';\n"
           "      return r.joined ? '<p><b>' + josa(t.n, '이가') + (r.far ? ' ' + facName(r.from) + '군을 떠나' : '') + ' 합류했습니다</b></p>' : '<p><b>' + josa(t.n, '은는') + ' 뜻을 굽히지 않았습니다</b>' + (r.far ? ' — 충성 +' + POACH.up + ' · 다음 달에 다시 권할 수 있습니다' : ' — 다음 턴에 다시 권할 수 있습니다') + '</p>';\n"
           "    } },\n"
           "    function () {\n"
           "      if (r && r.ok && r.joined) { sfx('cheer'); talk(t, sayLine(t, 'joined', G.factions[G.player].name), josa(t.n, '이가') + ' 합류했습니다!', 3000); }\n"
           "      refreshSheet(); afterAction();\n"
           "    });\n"
           "}\n"
           "function flowRecruit(b) {\n")
# 도움말
s = rep(s, "'<h3>일기토</h3><p>무력 75 이상의 주장끼리 붙어 싸우면 낮은 확률로 일기토가 벌어집니다. 지금은 자동으로 판정되며, 진 쪽은 병력과 기력을 잃습니다.</p>' +",
           "'<h3>일기토</h3><p>무력 ' + DUEL_K.minWar + ' 이상의 주장끼리 붙어 싸우면 낮은 확률로 일기토가 벌어집니다. 옆의 적 부대를 누르고 <b>일기토</b>를 눌러 직접 걸 수도 있습니다(기력 ' + DUEL_K.ask + ' · 응하지 않으면 상대 기력 -' + DUEL_K.refuse + '). 약한 상대일수록 응하지 않습니다.</p>' +\n"
           "  '<p>합마다 수를 하나 고릅니다 — <b>맹공</b>은 필살을 이기고, <b>필살</b>은 방어를 부수며(피해 1.6배), <b>방어</b>는 맹공을 받아칩니다. 피해는 두 사람의 무력 차로 정해지고, 합을 이기면 기세가 올라 더 세게 칩니다. 화면의 <b>기색</b>은 상대가 낼 수의 낌새입니다(맞을 확률이 적혀 있습니다 — 지력이 높을수록 잘 읽습니다). ' + DUEL_K.rounds + '합 안에 쓰러뜨리지 못하면 남은 힘으로 판정합니다.</p>' +\n"
           "  '<p>진 부대는 기력 -' + DUEL_K.morLose + ' · 병력 -' + Math.round(DUEL_K.loss * 100) + '%, 쓰러졌으면 기력 -' + DUEL_K.koMor + ' · 병력 -' + Math.round(DUEL_K.koLoss * 100) + '% · 혼란. AI끼리의 일기토와 내 군단의 일기토는 같은 규칙으로 저절로 판정됩니다.</p>' +\n"
           "  '<h3>설전</h3><p>등용할 때 보낼 무장을 고르고 <b>설전</b>을 누르면 주사위 대신 말로 겨룹니다(등용 확률 ' + DUEL_K.talkMin + '% 이상일 때). <b>도리</b>는 이해를, <b>이해</b>는 시세를, <b>시세</b>는 도리를 이깁니다. 피해는 지력 차로 정해지고, 응할 마음이 적은 상대일수록 오래 버팁니다. 이기면 합류하고, 지거나 비기면 거절한 것과 같습니다.</p>' +")
s = rep(s, "<p>직접 조작하는 일기토·설전, 외교, 기교·능력 연구,", "<p>외교, 기교·능력 연구,")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/style.css'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "/* 아래에 더 있다는 표시(v0.12) */",
           r'''/* ---------- 대결 화면(v0.13): 일기토 · 설전 ---------- */
#duel { position: absolute; inset: 0; z-index: 40; display: none; background: #f4efe3; }
#duel.on { display: flex; justify-content: center; }
#duel::before { content: ''; position: absolute; inset: 0; background: radial-gradient(120% 60% at 50% 0%, #1b1a1826, transparent 60%), radial-gradient(90% 40% at 50% 100%, #1b1a181a, transparent 70%); pointer-events: none; }
.du-in { position: relative; width: 100%; max-width: 560px; display: flex; flex-direction: column; padding: max(14px, env(safe-area-inset-top)) 14px max(12px, env(safe-area-inset-bottom)); }
.du-top { display: flex; align-items: center; gap: 10px; min-height: 36px; }
.du-seal { font: 900 19px var(--font-display); color: var(--seal-ink); background: var(--seal); padding: 3px 11px 4px; border-radius: 2px; letter-spacing: .12em; box-shadow: 2px 2px 0 #1b1a1826; }
#duel.talk .du-seal { background: #2f4f6f; }
.du-top b { font: 900 17px var(--font-display); font-variant-numeric: tabular-nums; }
.du-top small { margin-left: auto; color: var(--dim); font-size: 12.5px; text-align: right; }
.du-stage { position: relative; display: grid; grid-template-columns: 1fr 30px 1fr; gap: 2px; align-items: start; margin-top: 12px; }
.du-stage.shake { animation: duShake .32s; }
.du-mid { align-self: center; text-align: center; padding-bottom: 90px; }
.du-vs { font: 900 24px var(--font-display); color: var(--dim); }
.du-f { position: relative; text-align: center; min-width: 0; transition: filter .35s, opacity .35s; }
.du-por { display: block; margin: 0 auto; height: min(33vh, 56vw); max-width: 100%; aspect-ratio: 3 / 4; background-color: #e9e2d0; background-size: cover; background-position: 50% 12%; border: 1.5px solid var(--ink); box-shadow: 3px 4px 0 #1b1a1826; }
.du-por:not(.sc) { background-position: 50% 30%; }
.du-f.me .du-por { border-color: var(--seal-2); box-shadow: 3px 4px 0 #b3261e40; }
.du-nm { margin-top: 7px; font: 900 18px var(--font-display); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.du-nm em { font: 800 10.5px var(--font-body); font-style: normal; color: var(--seal-ink); background: var(--seal); padding: 1px 5px; border-radius: 2px; margin-left: 5px; vertical-align: 3px; }
.du-st { font-size: 12.5px; color: var(--dim); } .du-st b { color: var(--ink); font-size: 15px; font-variant-numeric: tabular-nums; }
.du-bar { height: 9px; border: 1px solid var(--ink); background: #fffdf6; margin: 5px 4px 3px; }
.du-bar i { display: block; height: 100%; background: var(--ink); transition: width .5s cubic-bezier(.2, .8, .3, 1), background .3s; }
.du-bar i.low { background: var(--seal); }
.du-hp { display: flex; align-items: baseline; justify-content: center; gap: 4px; font-variant-numeric: tabular-nums; }
.du-hp b { font: 900 17px var(--font-display); } .du-hp small { color: var(--dim); font-size: 11.5px; }
.du-mom { display: inline-flex; gap: 3px; margin-left: 6px; }
.du-mom i { width: 7px; height: 7px; border: 1px solid var(--ink); border-radius: 50%; } .du-mom i.on { background: var(--seal); border-color: var(--seal-2); }
.du-glyph { position: absolute; top: -9px; width: 46px; height: 46px; display: flex; align-items: center; justify-content: center; font: 900 27px var(--font-display); color: var(--paper); background: var(--ink); border-radius: 3px; opacity: 0; transform: scale(.4) rotate(-12deg); box-shadow: 2px 3px 0 #1b1a1833; z-index: 3; }
.du-f.a .du-glyph { left: -4px; } .du-f.d .du-glyph { right: -4px; }
.du-glyph.on { opacity: 1; transform: none; transition: transform .22s cubic-bezier(.2, 1.4, .4, 1), opacity .12s; }
.du-glyph.sp, .du-glyph.tide { background: var(--seal); color: var(--seal-ink); } .du-glyph.def, .du-glyph.gain { background: #2f4f6f; }
.du-say { min-height: 34px; margin: 4px 2px 0; font: 700 12.5px/1.3 var(--font-body); color: var(--ink); opacity: 0; transform: translateY(4px); }
.du-say.on { opacity: 1; transform: none; transition: opacity .2s, transform .2s; } .du-say.lose { color: var(--dim); font-weight: 500; }
.du-f.a.lunge { animation: duLungeA .5s cubic-bezier(.2, .9, .3, 1); } .du-f.d.lunge { animation: duLungeD .5s cubic-bezier(.2, .9, .3, 1); }
#duel.talk .du-f.a.lunge { animation-name: duLeanA; } #duel.talk .du-f.d.lunge { animation-name: duLeanD; }
.du-f.hit .du-por { animation: duHit .5s; } .du-f.rest .du-por { animation: duRest .9s; }
.du-f.victor .du-por { border-color: var(--seal-2); box-shadow: 0 0 0 3px #b3261e33, 3px 4px 0 #1b1a1826; }
.du-f.loser { filter: grayscale(.7); opacity: .82; }
.du-f.ko { filter: grayscale(1) brightness(.8); opacity: .7; } .du-f.a.ko .du-por { transform: rotate(-9deg) translateY(7%); transition: transform .5s cubic-bezier(.4, 0, .6, 1.4); } .du-f.d.ko .du-por { transform: rotate(9deg) translateY(7%); transition: transform .5s cubic-bezier(.4, 0, .6, 1.4); }
.du-fx { position: absolute; inset: 0; pointer-events: none; z-index: 4; }
.du-slash { position: absolute; top: 24%; width: 44%; height: 6px; border-radius: 3px; background: linear-gradient(90deg, #b3261e00, var(--seal) 18%, var(--ink) 82%, #1b1a1800); transform: rotate(-32deg) scaleX(0); opacity: .95; animation: duSlash .55s ease-out forwards; }
.du-slash.a { left: 1%; } .du-slash.d { right: 1%; transform: rotate(32deg) scaleX(0); animation-name: duSlashD; } .du-slash.big { height: 11px; top: 21%; }
.du-float { position: absolute; left: 50%; top: 26%; font: 900 26px var(--font-display); color: var(--seal); text-shadow: 0 0 6px var(--paper), 0 0 2px var(--paper); pointer-events: none; z-index: 5; animation: duFloat 1.2s ease-out forwards; white-space: nowrap; }
.du-float.big { font-size: 36px; } .du-float.heal { color: #2f4f6f; }
.du-hint { min-height: 46px; margin-top: 8px; padding: 8px 11px; border: 1px dashed var(--line-2); border-radius: 3px; font-size: 14px; line-height: 1.4; }
.du-hint:empty { visibility: hidden; }
.du-hint b { font: 900 14px var(--font-display); margin-right: 4px; } .du-hint em { font-style: normal; font-weight: 800; color: var(--seal); margin-left: 2px; } .du-hint small { float: right; color: var(--dim); font-size: 12px; margin-top: 1px; }
.du-moves { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 9px; } .du-moves.off { opacity: .4; pointer-events: none; }
.du-mv { display: flex; flex-direction: column; align-items: center; gap: 1px; min-height: 86px; padding: 8px 4px 9px; border: 1.5px solid var(--ink); border-radius: 3px; background: #fffdf6; color: var(--ink); touch-action: manipulation; }
.du-mv:active { background: var(--ink); color: var(--paper); } .du-mv:active small { color: #d9d3c4; }
.du-mv i { font: 900 26px var(--font-display); font-style: normal; line-height: 1.1; color: var(--seal); } .du-mv:active i { color: var(--paper); }
.du-mv b { font: 900 16px var(--font-display); } .du-mv small { font-size: 11px; line-height: 1.25; color: var(--dim); text-align: center; text-wrap: balance; }
.du-foot { display: flex; align-items: center; gap: 10px; margin-top: 9px; min-height: 40px; } .du-foot .btn { height: 38px; padding: 0 14px; } .du-tip { margin-left: auto; color: var(--dim); font-size: 12px; }
.du-res { position: absolute; left: 14px; right: 14px; bottom: max(12px, env(safe-area-inset-bottom)); display: none; z-index: 6; }
.du-res.on { display: block; animation: duRise .35s cubic-bezier(.2, .9, .3, 1); }
.du-resin { position: relative; background: #fffdf6; border: 1.5px solid var(--ink); border-radius: 3px; padding: 14px 16px 14px; box-shadow: 4px 5px 0 #1b1a1826; }
.du-resin h3 { margin: 0; font: 900 24px var(--font-display); } .du-resin > p { margin: 3px 0 0; color: var(--dim); font-size: 14px; }
.du-out { margin-top: 10px; padding-top: 9px; border-top: 1px solid var(--line-2); font-size: 14px; } .du-out p { margin: 2px 0; }
.du-resin .btn { width: 100%; height: 46px; margin-top: 12px; }
.du-stamp { position: absolute; right: 14px; top: 10px; width: 52px; height: 52px; display: flex; align-items: center; justify-content: center; font: 900 32px var(--font-display); font-style: normal; color: var(--seal); border: 3px solid var(--seal); border-radius: 5px; transform: rotate(8deg); animation: duStamp .4s cubic-bezier(.3, 1.6, .5, 1) .15s backwards; }
.du-resin.lost .du-stamp { color: var(--dim); border-color: var(--dim); }
@keyframes duLungeA { 0% { transform: none; } 38% { transform: translateX(24%) scale(1.07) rotate(3deg); } 100% { transform: translateX(5%); } }
@keyframes duLungeD { 0% { transform: none; } 38% { transform: translateX(-24%) scale(1.07) rotate(-3deg); } 100% { transform: translateX(-5%); } }
@keyframes duLeanA { 0% { transform: none; } 40% { transform: translateX(9%) scale(1.04); } 100% { transform: translateX(3%); } }
@keyframes duLeanD { 0% { transform: none; } 40% { transform: translateX(-9%) scale(1.04); } 100% { transform: translateX(-3%); } }
@keyframes duHit { 0% { transform: none; filter: none; } 15% { transform: translate(-5px, 2px) rotate(-2deg); filter: sepia(1) saturate(5) hue-rotate(-30deg) brightness(1.1); } 35% { transform: translate(5px, -2px) rotate(2deg); } 55% { transform: translate(-3px, 1px); filter: none; } 100% { transform: none; } }
@keyframes duRest { 0%, 100% { transform: none; } 50% { transform: scale(.975) translateY(2px); } }
@keyframes duShake { 0%, 100% { transform: none; } 25% { transform: translate(-4px, 2px); } 50% { transform: translate(4px, -2px); } 75% { transform: translate(-2px, 1px); } }
@keyframes duSlash { 0% { transform: rotate(-32deg) scaleX(0); opacity: 1; } 45% { transform: rotate(-32deg) scaleX(1.25); opacity: 1; } 100% { transform: rotate(-32deg) scaleX(1.3); opacity: 0; } }
@keyframes duSlashD { 0% { transform: rotate(32deg) scaleX(0); opacity: 1; } 45% { transform: rotate(32deg) scaleX(1.25); opacity: 1; } 100% { transform: rotate(32deg) scaleX(1.3); opacity: 0; } }
@keyframes duFloat { 0% { transform: translate(-50%, 0) scale(.6); opacity: 0; } 15% { transform: translate(-50%, -8px) scale(1.15); opacity: 1; } 70% { opacity: 1; } 100% { transform: translate(-50%, -46px) scale(1); opacity: 0; } }
@keyframes duRise { 0% { transform: translateY(24px); opacity: 0; } 100% { transform: none; opacity: 1; } }
@keyframes duStamp { 0% { transform: rotate(8deg) scale(2.2); opacity: 0; } 100% { transform: rotate(8deg) scale(1); opacity: 1; } }
@media (prefers-reduced-motion: reduce) { .du-f.lunge, .du-f.hit .du-por, .du-stage.shake, .du-stamp { animation: none !important; } }
.btn.alt.off { opacity: .45; }
/* 아래에 더 있다는 표시(v0.12) */''')
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
