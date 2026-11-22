# v0.18 소리 — 출진의 북을 새 소리에 맞춘다. 북 표본 둘(drum · drums)은 패치가 아니라 도구로 새로 만든 것이다: python3 tools/make_audio_v018.py → src/sfxdata.js
#   그동안: 출진(deploy) = 여덟 번 터지는 소리(drums) + 0.3초 뒤 뿔나팔. 새 drums 는 "둥 — 둥 — 둥둥둥"(1.5초, 마지막 센 박이 0.87초)이라
#   이제: 뿔나팔을 마지막 센 박(0.9초)에 맞춰 조금 여리게 얹는다.
#   CH_ROOT=<폴더> 로 다른 나무에 입힐 수 있다(시험용).
import io, os
ROOT = os.environ.get('CH_ROOT') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, ('count', s.count(a), a[:70])
    return s.replace(a, b)
s = rd('src/ui3d.js')
s = rep(s, "  deploy:   { s: [['drums', 0.85, 0.02], ['horn', 0.5, 0.01, 0.3]], gap: 600, syn: 'drum' },",
           "  deploy:   { s: [['drums', 0.85, 0.02], ['horn', 0.42, 0.01, 0.9]], gap: 600, syn: 'drum' },      // v0.18: 북 \"둥 — 둥 — 둥둥둥\"의 마지막 센 박에 뿔나팔")
wr('src/ui3d.js', s)
print('p6_sound18: ok')
