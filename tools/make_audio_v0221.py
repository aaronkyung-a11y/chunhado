#!/usr/bin/env python3
"""v0.22.1 소리: 순찰의 소리 clack(딱따기 두 번 "딱 — 딱")을 셈으로 새로 만든다. 나머지 29개는 v0.22 의 것을 글자 하나 바꾸지 않고 옮긴다.
   왜: "순찰 실행할 때 나오는 효과음이 이상할 때가 있다. 깨지는 것 같기도 하다"는 말을 들었다. 재 보니
     · 순찰은 싸움에서 부대가 달려들 때 쓰는 발구름(stomp)을 한 번 틀었다. stomp 는 발소리 녹음의 맨 앞 0.31초를 자른 것인데,
       한 걸음이 아니라 0.2초 동안 이어지는 굵은 소리 뭉치다(10ms 마다의 봉우리가 0.4 ~ 0.8 로 이어지고, 힘의 84%가 150 ~ 3000Hz 에 퍼져 있다).
     · 거기에 틀 때마다 음높이를 ±8% 흔들었다. 싸움터에서는 다른 소리에 섞여 '우르르'로 들리지만, 조용한 내정 화면에서 혼자 나면 찢어진 소리처럼 들린다.
     · 표본 자체가 깨진 것은 아니다(봉우리 0.81, 0.98 을 넘는 점 0개).
   새 소리: 야경꾼의 딱따기(나무토막 두 개를 맞부딪치는 소리) 두 번. 맑고 짧아서 음성(명령을 받는 한마디)과 겹쳐도 뭉개지지 않는다.
     나무토막의 울림(1.18 · 2.65 · 4.1kHz 의 세 떨림이 저마다 빨리 잦아든다) + 맞닿는 순간의 짧은 딱 소리 + 나무 몸통의 낮은 울림(320Hz) + 옅은 방 울림.
   usage: make_audio_v0221.py [--check]   ffmpeg 필요"""
import sys, os, re, base64, subprocess
import numpy as np
from scipy import signal
from scipy.io import wavfile
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); SR = 44100
BASE = os.path.join(ROOT, 'build/sfxdata.v022.js'); OUT = os.path.join(ROOT, 'audio0221/sfx')
rng = np.random.default_rng(20261125)
def enc(x, out, kbps=64):
    tmp = out + '.wav'; wavfile.write(tmp, SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-c:a', 'libmp3lame', '-b:a', '%dk' % kbps, '-ac', '1', out], check=True); os.remove(tmp)
def dec_bytes(b):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', 'pipe:0', '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], input=b, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
def T(n): return np.arange(n) / SR
def hp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, 'highpass', fs=SR, output='sos'), x)
def bp(x, f0, f1, o=2): return signal.sosfilt(signal.butter(o, [f0, f1], 'bandpass', fs=SR, output='sos'), x)
def place(dst, src, at, g=1.0):
    a = int(at * SR)
    if a >= len(dst): return
    m = min(len(src), len(dst) - a); dst[a:a + m] += src[:m] * g
def norm(x): return x / max(np.abs(x).max(), 1e-9)
def clap(k=1.0, hard=1.0):
    """나무토막 한 번. k = 음높이(1 = 바탕), hard = 세기"""
    n = int(0.22 * SR); t = T(n); y = np.zeros(n)
    for f, a, d in ((1180, 1.00, 0.040), (2650, 0.55, 0.020), (4100, 0.26, 0.011), (320, 0.30, 0.030)):
        y += a * np.sin(2 * np.pi * f * k * t + rng.uniform(0, 0.4)) * np.exp(-t / d)
    y[:int(0.0012 * SR)] *= np.linspace(0, 1, int(0.0012 * SR))                    # 맨 앞 1.2ms: 갑자기 서지 않게(딸깍 소리 방지)
    click = bp(rng.standard_normal(n), 1500, 6500) * np.exp(-t / 0.0035) * 0.55    # 맞닿는 순간
    return (y + click) * hard
def make():
    n = int(0.62 * SR); y = np.zeros(n)
    place(y, clap(1.00, 1.00), 0.004)
    place(y, clap(0.965, 0.86), 0.004 + 0.27)                                      # 두 번째는 조금 낮고 여리게
    room = signal.fftconvolve(y, rng.standard_normal(int(0.07 * SR)) * np.exp(-T(int(0.07 * SR)) / 0.018), mode='full')[:n]
    y = y + 0.05 * norm(bp(room, 500, 5000)) * np.abs(y).max()                    # 옅은 방 울림
    y = hp(y, 150); b = int(0.10 * SR); y[n - b:] *= np.linspace(1, 0, b) ** 1.5
    return {'clack': norm(y) * 0.80}
def shape(x, name):
    """소리의 생김새: 길이 · 봉우리 · 0.98 을 넘는 점 · 가장 긴 굵은 덩어리(봉우리의 35%를 넘는 채로 이어지는 시간) · 대역별 힘 · 타격 수"""
    n10 = int(SR * 0.01); env = np.array([np.abs(x[i:i + n10]).max() for i in range(0, max(1, len(x) - n10), n10)]); pk = float(np.abs(x).max())
    run = best = 0
    for e in env:
        run = run + 1 if e > 0.35 * pk else 0; best = max(best, run)
    f = np.abs(np.fft.rfft(x)) ** 2; fr = np.fft.rfftfreq(len(x), 1 / SR); tot = max(f.sum(), 1e-12)
    band = lambda a, b: f[(fr >= a) & (fr < b)].sum() / tot * 100
    hits = [i for i in range(1, len(env) - 1) if env[i] > env[i - 1] and env[i] >= env[i + 1] and env[i] > 0.5 * pk]
    return '%-6s 길이 %.2fs  봉우리 %.2f  0.98 넘는 점 %d  굵은 덩어리 %3dms  150Hz 아래 %2.0f%% · 150~1000Hz %2.0f%% · 1~3kHz %2.0f%% · 3kHz 위 %2.0f%%  타격 %s' % (
        name, len(x) / SR, pk, int((np.abs(x) >= 0.98).sum()), best * 10, band(0, 150), band(150, 1000), band(1000, 3000), band(3000, 22050), [round(h / 100, 2) for h in hits])
def main():
    src = open(BASE, encoding='utf-8').read(); old = dict(re.findall(r'^\s*(\w+): "([A-Za-z0-9+/=]+)"', src, re.M)); assert len(old) == 29, len(old)
    os.makedirs(OUT, exist_ok=True); S = make(); new = {}
    for k, y in S.items():
        p = os.path.join(OUT, k + '.mp3'); enc(y, p); new[k] = base64.b64encode(open(p, 'rb').read()).decode()
    if '--check' in sys.argv:
        print('옛 소리(순찰에 쓰던 것)'); print('  ' + shape(dec_bytes(base64.b64decode(old['stomp'])), 'stomp'))
        print('새 소리'); [print('  ' + shape(dec_bytes(base64.b64decode(new[k])), k)) for k in new]
    data = dict(old); data.update(new); keep = [k for k in old if k not in new]
    head = src[:src.index('var SFX_DATA')].rstrip()
    assert head.endswith('*/'), head[-40:]
    head = head[:-2].rstrip() + ' +\n   v0.22.1 에 셈으로 새로 만든 순찰의 딱따기 clack(tools/make_audio_v0221.py — 순찰에 쓰던 발구름이 혼자 나면 깨진 소리처럼 들렸다) */\n'
    js = head + 'var SFX_DATA = {\n' + ',\n'.join('  %s: "%s"' % (k, v) for k, v in data.items()) + '\n};\n'
    open(os.path.join(ROOT, 'src/sfxdata.js'), 'w', encoding='utf-8').write(js)
    same = all(data[k] == old[k] for k in keep)
    print('옮긴 소리 %d개(바뀐 것 없음: %s) + 새로 만든 소리 %d개 → src/sfxdata.js %d바이트' % (len(keep), same, len(new), len(js)))
    for k in new: print('  %-6s %6d바이트' % (k, len(base64.b64decode(new[k]))))
if __name__ == '__main__': main()
