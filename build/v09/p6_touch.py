# v0.9 손질: 조언 줄에 적중률, 인재 탭의 등용 단추 강조(응할 듯한 사람이 있을 때), 시작 안내 한 줄
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:100])
    return s.replace(a, b)
p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "' — 군사 ' + hs[0].adv.adv.n + '의 조언', go: ['recruit', b.id], lb: '등용', info: 1 });",
           "' — 군사 ' + hs[0].adv.adv.n + '의 조언(적중률 ' + hs[0].adv.acc + '%)', go: ['recruit', b.id], lb: '등용', info: 1 });")
s = rep(s, "[fr.length ? '재야 ' + fr.length : '', cp ? '포로 ' + cp : '', nbO ? '이웃 ' + nbO : ''].filter(function (x) { return x; }).join(' · ') : '대상 없음', fr.length + cp > 0, !(fr.length + cp + nbO))",
           "[fr.length ? '재야 ' + fr.length : '', cp ? '포로 ' + cp : '', nbO ? '이웃 ' + nbO : ''].filter(function (x) { return x; }).join(' · ') : '대상 없음', fr.length + cp > 0 || poachHints(b).length > 0, !(fr.length + cp + nbO))")
s = rep(s, "        '<li>자세한 규칙은 메뉴 → 도움말에 있습니다.</li></ul></div></div>",
           "        '<li><b>군사</b>(STATUS 창의 군사 단추)는 등용과 계략이 통할지 미리 말해 줍니다. <b>인재 → 등용</b>에서 이웃 거점에 있는 다른 세력의 무장도 부를 수 있습니다.</li>' +\n        '<li>자세한 규칙은 메뉴 → 도움말에 있습니다.</li></ul></div></div>")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')

# (덧붙임) STATUS 창의 군사 단추에 작은 한자 軍師(군사 탭의 '군사(軍事)'와 헷갈리지 않게), 도움말 '아직 없는 것'의 '군사 시설'을 '진·요새 같은 야전 시설'로 — 손으로 고침
