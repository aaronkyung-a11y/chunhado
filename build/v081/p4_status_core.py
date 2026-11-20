# v0.8.1 상태 이상 표시: "그리고 혼란이나 특수효과에 걸린 애들이 걸린건지 아닌건지 모르겠어."
#  0.8까지: 지도에서는 병력 숫자 앞에 '혼란 '/'위보 ' 글자가 붙을 뿐이고(이름표 색·그림은 그대로), 부대 창에는 붉은 두 글자, 걸리는 순간의 소용돌이는 연출이 끝나면 사라졌다. 몇 턴 남았는지는 어디에도 없었다.
#  규칙은 그대로 두고 '보이는 것'만 고친다. 이 파일은 규칙 쪽 준비:
#   - statusLeft(u): 지금부터 잃는 차례 수(지금 건너뛰는 차례가 있으면 그것까지). stT 는 '앞으로 더 건너뛸 차례 수'라서, 내 부대가 지금 묶여 있는 턴에는 +1 해야 맞다 → 건너뛴 턴을 u.stSkip 에 적어 둔다
#   - 계략·전법 결과(res)에 걸린 상태와 턴 수(res.st, res.stN)를 실어 화면과 기록에 쓴다
#   - 내 부대가 상태 이상으로 묶여 있거나 풀려난 것을 '지난 열흘의 일'에 적는다
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:100])
    return s.replace(a, b)
p = 'src/core.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "function setStatus(u, st, turns) { if (!alive(u)) return; u.status = st; u.stT = turns; }",
"""function setStatus(u, st, turns) { if (!alive(u)) return; u.status = st; u.stT = turns; u.stSkip = -1; }
/* 상태 이상(혼란·위보)으로 잃는 차례 수 — 지금부터 셈. 지금 건너뛰고 있는 차례가 있으면 그것까지 넣는다. 0 이면 '다음 차례에 풀린다'(그때까지는 아직 걸려 있다) */
function statusLeft(u) { return u.status ? (u.stT || 0) + (u.stSkip === G.turn ? 1 : 0) : 0; }
function statusName(st) { return st === 'confuse' ? '혼란' : (st === 'rumor' ? '위보' : ''); }
function unitOnFire(u) { return !!G.fires[K(u.c, u.r)]; }""")
s = rep(s, """    if (u.status) {
      if (u.stT <= 0) { u.status = null; }
      else {
        u.stT--;
        if (u.status === 'rumor') autoRetreat(u);
        if (UMAP[u.id]) u.done = true;
      }
    }""", """    if (u.status) {
      if (u.stT <= 0) { if (f === G.player && !G.aiOnly) logMsg(uName(u) + ' ' + statusName(u.status) + '에서 벗어남 — 다시 명령을 받습니다', u.c, u.r, f, 1); u.status = null; }
      else {
        u.stT--;
        if (u.status === 'rumor') autoRetreat(u);
        if (UMAP[u.id]) {
          u.done = true; u.stSkip = G.turn;                         // 이 턴을 건너뛴다(화면이 '이번 턴 포함 N턴'을 셀 수 있게 적어 둔다)
          if (f === G.player && !G.aiOnly) logMsg(uName(u) + ' ' + statusName(u.status) + (u.status === 'rumor' ? ' — 명령을 듣지 않고 물러남' : ' — 움직이지 못함') + (u.stT > 0 ? ' (이번 턴 포함 ' + (u.stT + 1) + '턴)' : ' (다음 턴에 풀림)'), u.c, u.r, f, 1);
        }
      }
    }""")
s = rep(s, "    if (cp) { res.pConf = cp; if (cp >= 100 || chance(cp)) { setStatus(d, 'confuse', 1); res.confused = true; } }",
           "    if (cp) { res.pConf = cp; if (cp >= 100 || chance(cp)) { setStatus(d, 'confuse', 1); res.confused = true; res.st = 'confuse'; res.stN = 1; } }")
s = rep(s, "  } else if (tu && alive(tu)) setStatus(tu, ploy.id, 2 + ext);",
           "  } else if (tu && alive(tu)) { setStatus(tu, ploy.id, 2 + ext); res.st = ploy.id; res.stN = 2 + ext; }")
s = rep(s, "      else if (!uHas(u, '통찰') && !uHas(u, '명경')) setStatus(u, ploy.id, 2);",
           "      else if (!uHas(u, '통찰') && !uHas(u, '명경')) { setStatus(u, ploy.id, 2); res.selfSt = ploy.id; res.selfStN = 2; }")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/ai.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "    if (res.kind === 'ploy') txt += '의 ' + res.ploy + (res.success ? ' 성공' : ' 실패') + ' → ' + (uLeaderSafe(tg)) + (res.dmg ? ' (-' + nf(res.dmg) + ')' : '');",
           "    if (res.kind === 'ploy') txt += '의 ' + res.ploy + (res.success ? ' 성공' : ' 실패') + ' → ' + (uLeaderSafe(tg)) + (res.dmg ? ' (-' + nf(res.dmg) + ')' : '') + (res.success && res.st ? ' — ' + statusName(res.st) + ' ' + res.stN + '턴' : '');")
s = rep(s, "    else if (res.kind === 'tactic') txt += '의 ' + res.tac + (res.fail ? ' 실패' : (res.crit ? ' 대성공' : '')) + ' → ' + uLeaderSafe(tg) + ' (-' + nf(res.dmg) + ')';",
           "    else if (res.kind === 'tactic') txt += '의 ' + res.tac + (res.fail ? ' 실패' : (res.crit ? ' 대성공' : '')) + ' → ' + uLeaderSafe(tg) + ' (-' + nf(res.dmg) + ')' + (res.confused ? ' — 혼란 ' + res.stN + '턴' : '');")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
