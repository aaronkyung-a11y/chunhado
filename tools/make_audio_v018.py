#!/usr/bin/env python3
"""v0.18 소리 고치기: 북 둘(drum · drums)을 셈으로 새로 만든다. 나머지 27개는 v0.17 의 것을 글자 하나 바꾸지 않고 옮긴다.
   왜: 출진할 때 "펑" 하는 소리가 어울리지 않는다는 말을 들었다. 재 보니
     · drums(출진 — 내 출진과 지난 열흘의 출진 장면): 0.1초 간격으로 여덟 번 터지는 소리. 200Hz 아래의 힘이 12%뿐이고 무게중심이 900Hz 쯤 — 북의 울림이 없는 '팡팡' 소리다.
     · drum(행군 시작 · 수송대 출발 · 턴 종료 …): 62Hz 에 봉우리가 있는 한 덩어리의 저음(힘의 81%가 200Hz 아래) — 음높이가 느껴지지 않는 '펑/쿵'.
   새 소리: 큰북(가죽 울림막)의 소리를 만든다 — 울림막의 배음(1 · 1.59 · 2.14 · 2.30 · 2.65 · 2.92 · 3.16 배)을 저마다 다르게 잦아들게 하고,
     맞는 순간 음이 조금 높았다가 내려앉게 하고(북을 세게 칠 때 그렇다), 북채가 가죽을 때리는 짧은 소리를 얹는다.
     · drum  = 한 번 "둥"(바탕음 104Hz).
     · drums = 출진의 북 "둥 — 둥 — 둥둥둥"(큰 북 96Hz 와 조금 높은 북 112Hz, 1.5초).
   usage: make_audio_v018.py [--check]   (--check: 옛 소리와 새 소리의 생김새를 숫자로 견준다)   ffmpeg 필요"""
import sys, os, re, base64, subprocess
import numpy as np
from scipy import signal
from scipy.io import wavfile
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); SR = 44100
BASE = os.path.join(ROOT, 'build/sfxdata.v017.js'); OUT = os.path.join(ROOT, 'audio18/sfx')
rng = np.random.default_rng(20261122)
def enc(x, out, kbps=64):
    tmp = out + '.wav'; wavfile.write(tmp, SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-c:a', 'libmp3lame', '-b:a', '%dk' % kbps, '-ac', '1', out], check=True); os.remove(tmp)
def dec_bytes(b):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', 'pipe:0', '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], input=b, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
def T(n): return np.arange(n) / SR
def bell(n, a, peak, d):
    t = T(n); return np.where(t < peak, 0.5 - 0.5 * np.cos(np.pi * np.clip((t - (peak - a)) / a, 0, 1)), np.exp(-(t - peak) / d))
def hp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, 'highpass', fs=SR, output='sos'), x)
def bp(x, f0, f1, o=2): return signal.sosfilt(signal.butter(o, [f0, f1], 'bandpass', fs=SR, output='sos'), x)
def place(dst, src, at, g=1.0):
    a = int(at * SR)
    if a >= len(dst): return
    m = min(len(src), len(dst) - a); dst[a:a + m] += src[:m] * g
def norm(x): return x / max(np.abs(x).max(), 1e-9)
RATIO = (1.00, 1.59, 2.14, 2.30, 2.65, 2.92, 3.16, 3.50, 4.06, 4.60)          # 둥근 울림막의 떨림꼴
AMP   = (1.00, 0.82, 0.62, 0.52, 0.42, 0.32, 0.26, 0.20, 0.15, 0.11)          # 높은 배음을 넉넉히: 휴대폰 스피커는 200Hz 아래를 거의 내지 못한다
DEC   = (0.34, 0.25, 0.19, 0.16, 0.13, 0.11, 0.09, 0.08, 0.07, 0.06)          # 저마다 잦아드는 시간(초, 1/e)
def buk(dur, f0, hard=1.0):
    """큰북 한 번. hard = 얼마나 세게 치는가(1 = 세게): 셀수록 높은 배음과 북채 소리가 크고, 맞는 순간의 음이 더 높다"""
    n = int(dur * SR); t = T(n); y = np.zeros(n)
    glide = 1.0 + 0.11 * hard * np.exp(-t / 0.032)                       # 맞는 순간 음이 높았다가 내려앉는다
    for i, (r, a, d) in enumerate(zip(RATIO, AMP, DEC)):
        ph = 2 * np.pi * np.cumsum(f0 * r * glide) / SR + rng.uniform(0, 0.6)
        y += a * (hard ** (0.5 * i)) * np.sin(ph) * np.exp(-t / (d * (1.0 if i else 1.0)))
    y = norm(y) * (1 - np.exp(-t / 0.0012))                              # 딸깍 소리가 나지 않게 1ms 에 걸쳐 올린다
    stick = norm(bp(rng.standard_normal(n), 700, 3200) * bell(n, 0.002, 0.003, 0.018))      # 북채가 가죽을 때리는 소리
    skin = norm(bp(rng.standard_normal(n), 200, 700) * bell(n, 0.003, 0.005, 0.055))        # 가죽이 눌리는 낮은 '툭'
    return y + stick * 0.30 * hard + skin * 0.38
def harm(x, k):
    """작은 스피커에서도 들리게: 낮은 소리에 배음을 더한다(부드럽게 포화) — tools/make_audio_v07.py · v012 와 같은 방법"""
    pk = max(np.abs(x).max(), 1e-9); y = np.tanh(x / pk * k) * pk; return x * 0.75 + hp(y, 150) * 0.6
def fin(y, fo, hpf=60, peak=0.84, hk=3.0):
    y = harm(hp(y, hpf), hk); y = y.copy(); n = len(y); b = int(fo * SR); y[n - b:] *= np.linspace(1, 0, b) ** 1.5; return norm(y) * peak
def make():
    S = {}
    # ① drum: 한 번 "둥"
    y = np.zeros(int(0.95 * SR)); place(y, buk(0.94, 104.0, 1.0), 0.004, 1.0)
    S['drum'] = fin(y, 0.22)
    # ② drums: 출진의 북 "둥 — 둥 — 둥둥둥". 큰 북(96Hz)으로 힘을 주고, 사이의 잔 박은 조금 높은 북(112Hz)으로 여리게
    y = np.zeros(int(1.50 * SR))
    for at, f0, g, h in ((0.004, 96.0, 1.00, 1.00), (0.330, 96.0, 0.86, 0.90), (0.585, 112.0, 0.58, 0.70), (0.725, 112.0, 0.66, 0.75), (0.870, 96.0, 1.00, 1.00)):
        place(y, buk(0.62, f0 * rng.uniform(0.992, 1.008), h), at, g)
    S['drums'] = fin(y, 0.25)
    return S
def shape(x, name):
    """소리의 생김새: 길이 · 오르는 시간(10% → 90%) · 무게중심 · 200Hz 아래 / 200~800Hz / 2kHz 위의 힘 · 가장 센 주파수 · 타격 수(포락선의 봉우리)"""
    env = np.abs(signal.sosfiltfilt(signal.butter(2, 400, 'lowpass', fs=SR, output='sos'), np.abs(x))); pk = env.max()
    i10 = int(np.argmax(env > 0.1 * pk)); i90 = int(np.argmax(env > 0.9 * pk)); rise = (i90 - i10) / SR * 1000
    f = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2; fr = np.fft.rfftfreq(len(x), 1 / SR); tot = max(f.sum(), 1e-12)
    cen = (f * fr).sum() / tot; lo = f[fr < 200].sum() / tot; mid = f[(fr >= 200) & (fr < 800)].sum() / tot; hi = f[fr > 2000].sum() / tot
    e = np.sqrt((x[:len(x) // 441 * 441].reshape(-1, 441) ** 2).mean(axis=1)); hits = []
    for i in range(1, len(e) - 1):
        if e[i] > e[i - 1] and e[i] >= e[i + 1] and e[i] > 0.35 * e.max() and (not hits or i - hits[-1] > 8): hits.append(i)
    return '%-6s 길이 %.2fs  오름 %5.1fms  무게중심 %4.0fHz  200Hz 아래 %2.0f%% · 200~800Hz %2.0f%% · 2kHz 위 %2.0f%%  가장 센 곳 %3.0fHz  타격 %s' % (name, len(x) / SR, rise, cen, lo * 100, mid * 100, hi * 100, fr[int(np.argmax(f))], [round(h / 100, 2) for h in hits])
def main():
    src = open(BASE, encoding='utf-8').read(); old = dict(re.findall(r'^\s*(\w+): "([A-Za-z0-9+/=]+)"', src, re.M)); assert len(old) == 29, len(old)
    os.makedirs(OUT, exist_ok=True); S = make(); new = {}
    for k, y in S.items():
        p = os.path.join(OUT, k + '.mp3'); enc(y, p); new[k] = base64.b64encode(open(p, 'rb').read()).decode()
    if '--check' in sys.argv:
        print('옛 소리'); [print('  ' + shape(dec_bytes(base64.b64decode(old[k])), k)) for k in ('drum', 'drums')]
        print('새 소리'); [print('  ' + shape(dec_bytes(base64.b64decode(new[k])), k)) for k in ('drum', 'drums')]
    data = dict(old); data.update(new); keep = [k for k in old if k not in new]
    js = ('/* 효과음: v0.7 에 Higgsfield mirelo_text_to_audio 로 만든 소리를 잘라 정규화한 mp3(모노 64kbps, tools/make_audio_v07.py) 23개 +\n'
          '   v0.12 에 셈으로 새로 만든 bow · arrows · thock · arrowland(tools/make_audio_v012.py) +\n'
          '   v0.18 에 셈으로 새로 만든 북 둘 drum · drums(tools/make_audio_v018.py — "펑" 하던 소리를 "둥"으로) */\nvar SFX_DATA = {\n') + ',\n'.join('  %s: "%s"' % (k, v) for k, v in data.items()) + '\n};\n'
    open(os.path.join(ROOT, 'src/sfxdata.js'), 'w', encoding='utf-8').write(js)
    same = all(data[k] == old[k] for k in keep)
    print('옮긴 소리 %d개(바뀐 것 없음: %s) + 새로 만든 소리 %d개 → src/sfxdata.js %d바이트' % (len(keep), same, len(new), len(js)))
    for k in new: print('  %-6s %6d바이트' % (k, len(base64.b64decode(new[k]))))
if __name__ == '__main__': main()
