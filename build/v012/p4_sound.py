# v0.12 (4/…): 쏘는 소리  (ui3d.js · ui_panels.js)   — 소리 자체는 tools/make_audio_v012.py 가 만든다(src/sfxdata.js)
#  요청 "활 쏠 때 총 쏘는 소리가 난다. 소리를 잘 봐야할 것 같고 …"
#   까닭(파형 · 스펙트로그램으로 본 것): ① bow 표본이 0.07초짜리 넓은 대역의 '팍' 하나였다(원본 1초 가운데 소리는 앞 0.1초뿐)
#     ② arrows 는 갑자기 시작되는 잡음 세 덩어리 ③ 화살이 맞을 때 날카로운 thud, 쏘는 전법이 맞을 때는 crush + clang(쇠가 부서지는 큰 소리)이 났다 → '탕 … 쾅'.
#   고침: bow · arrows 를 새로 만들고(시위 울림 + 바람 가르는 소리), 맞는 소리 thock(한 발) · arrowland(여러 발)를 더했다.
#     쏘는 공격(두 칸 밖 · 화시 · 관시 · 난사)이 맞을 때는 화살 소리만 낸다: 보통 = thock, 전법 · 크게 맞음 = arrowland(+ 대성공이면 징), 실패 = 작은 thock 둘.
import io
def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:110])
    return s.replace(a, b)

p = 'src/ui3d.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "  arrowhit: { s: [['thud', 0.6, 0.1]], gap: 70, syn: 'hit' },\n",
           "  arrowhit: { s: [['thock', 0.75, 0.1]], gap: 70, syn: 'hit' },                                   // 화살 한 차례가 박힌다(v0.12 — 전에는 thud)\n"
           "  arrowbig: { s: [['arrowland', 0.95, 0.05]], gap: 120, syn: 'big' },                            // 쏘는 전법 · 크게 맞음: 후두둑\n"
           "  arrowgreat: { s: [['arrowland', 1.0, 0.04], ['thock', 0.6, 0.04, 0.12], ['gong', 0.3, 0, 0.1]], gap: 200, syn: 'big' },\n"
           "  arrowfail: { s: [['thock', 0.4, 0.14], ['thock', 0.3, 0.14, 0.11]], gap: 120, syn: 'fail' },      // 빗나간 살 몇 대\n")
s = rep(s, "  bow:      { s: [['bow', 0.7, 0.08]], gap: 60, syn: 'ui' },\n  arrows:   { s: [['arrows', 0.8, 0.04]], gap: 200, syn: 'step' },",
           "  bow:      { s: [['bow', 0.8, 0.08]], gap: 60, syn: 'ui' },                                       // v0.12: 새로 만든 소리(시위 울림 + 바람 가르는 소리)\n  arrows:   { s: [['arrows', 0.8, 0.04]], gap: 200, syn: 'step' },")
io.open(p, 'w', encoding='utf-8').write(s)

p = 'src/ui_panels.js'; s = io.open(p, encoding='utf-8').read()
s = rep(s, "    sfx(res.fail ? 'fail' : (res.kind === 'tactic' ? (res.crit ? 'great' : 'big') : (res.crit ? 'big' : (res.tk === 'base' || res.tk === 'fac' ? 'siege' : (far ? 'arrowhit' : 'hit')))));",
           "    var shot = far || (res.kind === 'tactic' && (res.tac === '화시' || res.tac === '관시' || res.tac === '난사'));      // 쏘는 공격: 맞는 소리도 화살 소리로(v0.12)\n"
           "    if (shot) sfx(res.fail ? 'arrowfail' : (res.kind === 'tactic' ? (res.crit ? 'arrowgreat' : 'arrowbig') : (res.crit ? 'arrowbig' : 'arrowhit')));\n"
           "    else sfx(res.fail ? 'fail' : (res.kind === 'tactic' ? (res.crit ? 'great' : 'big') : (res.crit ? 'big' : (res.tk === 'base' || res.tk === 'fac' ? 'siege' : 'hit'))));")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
