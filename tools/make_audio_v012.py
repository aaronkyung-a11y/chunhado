#!/usr/bin/env python3
"""v0.12 소리 고치기: 쏘는 소리 넷(bow · arrows · thock · arrowland)을 셈으로 새로 만들고, 북(drum)에 배음을 더한다. 나머지 소리는 v0.11 의 것을 글자 하나 바꾸지 않고 옮긴다.
   왜: v0.7 의 bow 는 0.07초짜리 넓은 대역의 '팍' 소리, arrows 는 갑자기 시작되는 잡음 세 덩어리, 맞는 소리는 날카로운 thud 였다 → 총소리처럼 들렸다.
   새 소리: 시위가 울리는 낮은 음(줄 울림) + 살이 바람을 가르는 소리(천천히 커졌다 사라지는 잡음, 높은 데서 낮은 데로) + 나무·흙에 박히는 둔한 소리.
   usage: make_audio_v012.py [--check]   (--check: 옛 소리와 새 소리의 생김새를 숫자로 견준다)"""
import sys, os, re, base64, subprocess
import numpy as np
from scipy import signal
from scipy.io import wavfile
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); SR = 44100
BASE = os.path.join(ROOT, 'build/sfxdata.v011.js'); OUT = os.path.join(ROOT, 'audio12/sfx')
rng = np.random.default_rng(20261121)
def enc(x, out, kbps=64):
    tmp = out + '.wav'; wavfile.write(tmp, SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-c:a', 'libmp3lame', '-b:a', '%dk' % kbps, '-ac', '1', out], check=True); os.remove(tmp)
def dec_bytes(b):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', 'pipe:0', '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], input=b, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
def T(n): return np.arange(n) / SR
def bell(n, a, peak, d):
    """천천히 커졌다가 사라지는 꼴: a초 동안 오르고(코사인) d초 상수로 잦아든다. peak = 가장 클 때(초)"""
    t = T(n); e = np.where(t < peak, 0.5 - 0.5 * np.cos(np.pi * np.clip((t - (peak - a)) / a, 0, 1)), np.exp(-(t - peak) / d)); return e
def lp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, 'lowpass', fs=SR, output='sos'), x)
def hp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, 'highpass', fs=SR, output='sos'), x)
def bp(x, f0, f1, o=2): return signal.sosfilt(signal.butter(o, [f0, f1], 'bandpass', fs=SR, output='sos'), x)
def sweep(n, f0, f1, q):
    """가운데 주파수가 f0 → f1 로 흘러내리는 띠 잡음(상태 변수 필터). 살이 스쳐 지나가는 소리"""
    x = rng.standard_normal(n); y = np.zeros(n); lo = 0.0; band = 0.0; fc = f0 * (f1 / f0) ** (np.arange(n) / max(n - 1, 1)); fk = 2 * np.sin(np.pi * fc / SR); dq = 1.0 / q
    for i in range(n):
        hi = x[i] - lo - dq * band; band += fk[i] * hi; lo += fk[i] * band; y[i] = band
    return y / max(np.abs(y).max(), 1e-9)
def string(n, f0, damp, bright=2600):
    """뜯긴 줄(Karplus–Strong): 잡음 한 토막이 줄 길이만큼 돌며 낮아지고 잦아든다. damp = 한 바퀴에 남는 크기"""
    N = int(round(SR / f0)); buf = lp(rng.standard_normal(N), bright); buf -= buf.mean(); buf /= max(np.abs(buf).max(), 1e-9); y = np.zeros(n); p = buf.copy(); i = 0
    while i < n:
        m = min(N, n - i); y[i:i + m] = p[:m]; q = np.empty(N); q[0] = 0.5 * (p[0] + p[-1]); q[1:] = 0.5 * (p[1:] + p[:-1]); p = q * damp; i += m
    return y
def place(dst, src, at, g=1.0):
    a = int(at * SR)
    if a >= len(dst): return
    m = min(len(src), len(dst) - a); dst[a:a + m] += src[:m] * g
def twang(n, f0, g=1.0):
    """시위 울림: 살짝 어긋난 두 줄 + 활채가 떠는 낮은 음. 3ms 에 걸쳐 올라온다(딱 끊어지는 '팍'이 없게)"""
    y = string(n, f0, 0.88) + 0.7 * string(n, f0 * 1.035, 0.86) + 0.55 * np.sin(2 * np.pi * (f0 * 0.5) * T(n)) * np.exp(-T(n) / 0.07)
    y = lp(y, 1900, 2) * np.minimum(1, T(n) / 0.004); return y / max(np.abs(y).max(), 1e-9) * g
def clack(n, g=1.0):
    """쇠뇌의 방아쇠·활채가 '탁' 하고 풀리는 나무 소리: 600–1700Hz 띠, 5ms 에 올라 25ms 에 사라진다"""
    y = bp(rng.standard_normal(n), 600, 1700) * bell(n, 0.005, 0.005, 0.022); return y / max(np.abs(y).max(), 1e-9) * g
def whoosh(dur, f0, f1, peak, rise, fall, flutter=0.0):
    n = int(dur * SR); y = (sweep(n, f0, f1, 3.2) + 0.45 * sweep(n, f0 * 1.9, f1 * 1.9, 6.0)) * bell(n, rise, peak, fall)   # 좁은 띠 둘: '쉬익' 하는 휘파람 기운(넓은 잡음은 '팍'처럼 들린다)
    if flutter: y *= 1 - flutter * (0.5 + 0.5 * np.sin(2 * np.pi * 31 * T(n) + rng.uniform(0, 6.28)))
    return y / max(np.abs(y).max(), 1e-9)
def thock1(n, k=1.0):
    """살 하나가 박히는 소리: 둔한 '툭'(낮은 음이 금세 잦아듦) + 나무 두드림 조금 + 살대가 떠는 소리"""
    t = T(n); f = 200 * k
    low = np.sin(2 * np.pi * (f * t - 0.22 * f * 0.05 * (1 - np.exp(-t / 0.05)))) * np.exp(-t / 0.045) + 0.55 * np.sin(2 * np.pi * 2.4 * f * t) * np.exp(-t / 0.022)   # 둘째 음(나무의 울림): 작은 스피커에서도 '톡'이 들리게
    knock = bp(rng.standard_normal(n), 500 * k, 1500 * k) * bell(n, 0.003, 0.003, 0.014)
    quiver = np.sin(2 * np.pi * 410 * k * t) * (0.5 + 0.5 * np.cos(2 * np.pi * 37 * t)) * np.exp(-t / 0.085)
    y = (low + 0.42 * knock / max(np.abs(knock).max(), 1e-9) + 0.16 * quiver) * np.minimum(1, t / 0.003); return y / max(np.abs(y).max(), 1e-9)
def harm(x, k):
    """작은 스피커에서도 들리게: 낮은 소리에 배음을 더한다(포화) — tools/make_audio_v07.py 와 같은 방법"""
    pk = max(np.abs(x).max(), 1e-9); y = np.tanh(x / pk * k) * pk; return x * 0.75 + hp(y, 150) * 0.6
def fin(y, fo, hpf=70, peak=0.84, hk=0):
    y = hp(y, hpf)
    if hk: y = harm(y, hk)
    y = y.copy(); n = len(y); b = int(fo * SR); y[n - b:] *= np.linspace(1, 0, b) ** 1.5; return y / max(np.abs(y).max(), 1e-9) * peak
def drum_fix(x):
    """북(drum): v0.7 의 표본은 힘의 99%가 300Hz 아래(무게중심 76Hz)라 휴대폰 스피커로는 거의 들리지 않았다.
       같은 소리에 ① 배음(세게 포화시킨 것의 220Hz 위) ② 북채가 가죽을 때리는 짧은 소리(500–2200Hz, 35ms)를 더한다. 낮은 울림은 그대로 둔다."""
    pk = max(np.abs(x).max(), 1e-9); sat = np.tanh(x / pk * 6.0) * pk; hi = signal.sosfilt(signal.butter(4, 220, 'highpass', fs=SR, output='sos'), sat)
    env = np.abs(signal.sosfiltfilt(signal.butter(2, 60, 'lowpass', fs=SR, output='sos'), np.abs(x))); i0 = max(0, int(np.argmax(env > 0.1 * env.max())) - int(0.004 * SR))
    n = len(x); slap = np.zeros(n); m = min(int(0.12 * SR), n - i0); sl = bp(rng.standard_normal(m), 500, 2200) * bell(m, 0.004, 0.006, 0.035); slap[i0:i0 + m] = sl / max(np.abs(sl).max(), 1e-9)
    y = x * 0.75 + hi * 0.95 + slap * 0.30 * pk; return y / max(np.abs(y).max(), 1e-9) * 0.84
def make(old):
    S = {}
    S['drum'] = drum_fix(dec_bytes(base64.b64decode(old['drum'])))
    # ① bow: 한 발. 시위 울림(0s) → 살이 떠나는 바람 소리(0.02s 부터 커져 0.09s 에 가장 크고 0.3s 쯤 사라진다)
    n = int(0.50 * SR); y = np.zeros(n)
    place(y, twang(int(0.30 * SR), 185), 0.0, 1.0); place(y, clack(int(0.08 * SR)), 0.0, 0.30)
    place(y, whoosh(0.42, 3400, 1100, 0.095, 0.085, 0.075, 0.25), 0.01, 0.50)
    S['bow'] = fin(y, 0.15)
    # ② arrows: 한꺼번에 쏘는 여러 발. 0.3초에 걸쳐 시위 열두 번(높이·크기가 다 다르게) + 겹쳐 흐르는 바람 소리 열여섯 줄기
    n = int(1.25 * SR); y = np.zeros(n)
    for i in range(12):
        at = 0.02 + 0.30 * (i / 11.0) ** 1.15 + rng.uniform(-0.012, 0.012); place(y, twang(int(0.26 * SR), rng.uniform(150, 265)), max(0, at), rng.uniform(0.30, 0.60))
        if i % 3 == 0: place(y, clack(int(0.08 * SR)), max(0, at), 0.10)
    for i in range(16):
        at = 0.03 + 0.42 * rng.uniform(0, 1) ** 0.9; d = rng.uniform(0.34, 0.60)
        place(y, whoosh(d, rng.uniform(2800, 4200), rng.uniform(900, 1500), d * 0.36, d * 0.33, d * 0.24, 0.3), at, rng.uniform(0.22, 0.42))
    air = lp(hp(rng.standard_normal(n), 900), 3800) * bell(n, 0.30, 0.34, 0.26); place(y, air / np.abs(air).max(), 0, 0.20)   # 살 무리가 날아가는 바탕 소리
    S['arrows'] = fin(y, 0.35, 90)
    # ③ thock: 살 하나가 박힌다(보통 원거리 공격·관시)
    n = int(0.34 * SR); y = np.zeros(n); place(y, thock1(n, 1.0), 0, 1.0); place(y, thock1(int(0.2 * SR), 1.22), 0.055, 0.42)
    S['thock'] = fin(y, 0.12, 60, hk=2.0)
    # ④ arrowland: 살 무리가 후두둑 박힌다(전법·크게 맞음)
    n = int(0.80 * SR); y = np.zeros(n)
    for i in range(11):
        at = 0.40 * (i / 10.0) ** 0.8 + rng.uniform(0, 0.02); place(y, thock1(int(0.24 * SR), rng.uniform(0.78, 1.32)), at, rng.uniform(0.35, 1.0) * (1.0 if i < 7 else 0.6))
    pat = lp(rng.standard_normal(n), 520) * bell(n, 0.10, 0.14, 0.16); place(y, pat / np.abs(pat).max(), 0, 0.22)          # 흙에 떨어지는 낮은 소리
    S['arrowland'] = fin(y, 0.25, 60, hk=2.0)
    return S
def shape(x, name):
    """소리의 생김새: 오르는 시간(가장 큰 소리의 10% → 90%), 처음 30ms 에서 4kHz 위 힘의 비율, 처음 60ms 의 '잡음다움'(0 = 음, 1 = 흰 잡음), 뾰족함"""
    env = np.abs(signal.sosfiltfilt(signal.butter(2, 400, 'lowpass', fs=SR, output='sos'), np.abs(x))); pk = env.max(); ip = int(np.argmax(env))
    i10 = int(np.argmax(env > 0.1 * pk)); i90 = int(np.argmax(env > 0.9 * pk)); rise = (i90 - i10) / SR * 1000
    def band(seg):
        f = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))) ** 2; fr = np.fft.rfftfreq(len(seg), 1 / SR); return f, fr
    s30 = x[i10:i10 + int(0.03 * SR)]; f, fr = band(s30); hi = f[fr > 4000].sum() / max(f.sum(), 1e-12)
    s60 = x[i10:i10 + int(0.06 * SR)]; f, fr = band(s60); m = (fr > 100) & (fr < 8000); flat = np.exp(np.mean(np.log(f[m] + 1e-12))) / max(np.mean(f[m]), 1e-12)
    crest = np.abs(x).max() / max(np.sqrt((x ** 2).mean()), 1e-9)
    return '%-10s 길이 %.2fs  오름 %5.1fms  4kHz 위 %4.1f%%  잡음다움 %.2f  뾰족함 %4.1f' % (name, len(x) / SR, rise, hi * 100, flat, crest)
def main():
    src = open(BASE, encoding='utf-8').read(); old = dict(re.findall(r'^\s*(\w+): "([A-Za-z0-9+/=]+)"', src, re.M)); assert len(old) == 27, len(old)
    os.makedirs(OUT, exist_ok=True); S = make(old); new = {}
    for k, y in S.items():
        p = os.path.join(OUT, k + '.mp3'); enc(y, p); new[k] = base64.b64encode(open(p, 'rb').read()).decode()
    if '--check' in sys.argv:
        print('옛 소리'); [print('  ' + shape(dec_bytes(base64.b64decode(old[k])), k)) for k in ('bow', 'arrows', 'thud', 'drum')]
        print('새 소리'); [print('  ' + shape(dec_bytes(base64.b64decode(new[k])), k)) for k in ('bow', 'arrows', 'thock', 'arrowland', 'drum')]
    data = dict(old); data.update(new); keep = [k for k in old if k not in new]
    js = ('/* 효과음: v0.7 에 Higgsfield mirelo_text_to_audio 로 만든 소리를 잘라 정규화한 mp3(모노 64kbps, tools/make_audio_v07.py) %d개 +\n'
          '   v0.12 에 고친 소리 %d개(tools/make_audio_v012.py): 셈으로 새로 만든 bow · arrows · thock · arrowland, 배음을 더한 drum */\nvar SFX_DATA = {\n' % (len(keep), len(new))) + ',\n'.join('  %s: "%s"' % (k, v) for k, v in data.items()) + '\n};\n'
    open(os.path.join(ROOT, 'src/sfxdata.js'), 'w', encoding='utf-8').write(js)
    same = all(data[k] == old[k] for k in keep)
    print('옮긴 소리 %d개(바뀐 것 없음: %s) + 고친 소리 %d개 → src/sfxdata.js %d바이트' % (len(keep), same, len(new), len(js)))
    for k in new: print('  %-10s %6d바이트' % (k, len(base64.b64decode(new[k]))))
main()
