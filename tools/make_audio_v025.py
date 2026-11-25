#!/usr/bin/env python3
"""v0.25 소리: 순찰(치안)의 소리를 바꾼다 — 딱따기(clack)를 빼고 순라군의 발걸음(patrol)을 넣는다. 나머지 29개는 v0.24 의 것을 글자 하나 바꾸지 않고 옮긴다.
   왜: (요청 11-25 20:42) "치안 할 때 소리가 이상한 땡똥 하는 소리가 되었어. 바꿔줘"
     · 0.22.1 의 딱따기는 셈으로 만든 소리였다: 맑은 떨림 셋(1.18 · 2.65 · 4.1kHz)이 잦아드는 것을 두 번, 두 번째를 3.5% 낮게.
       나무토막이 아니라 실로폰의 두 음("땡 — 똥")처럼 들린다. 셈으로 만든 맑은 음은 여기에 맞지 않는다.
   새 소리(후보 셋 — PATROL=a|b|c, 기본 a): 모두 만들어 둔 소리(Higgsfield mirelo_text_to_audio)를 잘라 맞춘 것이고, 맑은 음(사인파)은 쓰지 않는다.
     a 발걸음 셋 "저벅 저벅 저벅": 걸음마다 발뒤꿈치의 쿵(audio25/raw/patrol1 — 돌길을 걷는 순라군의 걸음에서 뗀 것) + 바닥을 밟는 자박(patrol5 — 자갈길)을 겹친다. 0.36초 간격.
     b 발걸음 둘 + 칼집 "저벅 저벅 철컥": a 의 걸음 둘 뒤에 칼집 소리(audio7/raw/sfx_sheath — v0.7 의 원본).
     c 자갈길 행군 "자박자박": patrol5 를 0.9초 잘라 앞뒤를 다듬은 것.
   usage: [PATROL=a] make_audio_v025.py [--check]   ffmpeg 필요. 후보는 audio25/sfx/patrol_a.mp3 … 로도 남긴다(들어 보고 고르게)."""
import sys, os, re, base64, subprocess
import numpy as np
from scipy import signal
from scipy.io import wavfile
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); SR = 44100
BASE = os.path.join(ROOT, 'build/sfxdata.v024.js'); RAW = os.path.join(ROOT, 'audio25/raw'); OUT = os.path.join(ROOT, 'audio25/sfx')
PICK = os.environ.get('PATROL', 'a')
def enc(x, out, kbps=64):
    tmp = out + '.wav'; wavfile.write(tmp, SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-c:a', 'libmp3lame', '-b:a', '%dk' % kbps, '-ac', '1', out], check=True); os.remove(tmp)
def dec(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
def dec_bytes(b):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', 'pipe:0', '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], input=b, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
def T(n): return np.arange(n) / SR
def hp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, 'highpass', fs=SR, output='sos'), x)
def lp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, 'lowpass', fs=SR, output='sos'), x)
def norm(x): return x / max(np.abs(x).max(), 1e-9)
def place(dst, src, at, g=1.0):
    a = int(at * SR)
    if a >= len(dst): return
    m = min(len(src), len(dst) - a); dst[a:a + m] += src[:m] * g
def fade(x, a=0.004, b=0.03):
    x = x.copy(); na, nb = int(a * SR), int(b * SR)
    x[:na] *= np.linspace(0, 1, na); x[-nb:] *= np.linspace(1, 0, nb) ** 1.5
    return x
def onset(x, t0, t1):
    """t0 ~ t1 초 사이에서 가장 큰 봉우리의 조금 앞(걸음이 시작되는 곳)"""
    a, b = int(t0 * SR), int(t1 * SR); pk = a + int(np.argmax(np.abs(x[a:b]))); th = 0.08 * abs(x[pk]); i = pk
    while i > a and i > pk - int(0.03 * SR) and abs(x[i]) > th: i -= 1
    return max(a, i - int(0.004 * SR))
def steps():
    """걸음 셋: (쿵, 자박) 의 짝"""
    p1 = dec(os.path.join(RAW, 'patrol1.mp3')); p5 = dec(os.path.join(RAW, 'patrol5.mp3'))
    out = []
    for (t0, t1), ct in zip(((0.78, 0.95), (1.40, 1.56), (1.62, 1.80)), (0.52, 1.18, 1.60)):
        a = onset(p1, t0, t1); thud = p1[a:a + int(0.13 * SR)].copy()
        thud = thud + 1.6 * hp(thud, 450)                                           # 작은 스피커(전화기)에서도 들리게 400Hz 위를 올린다(쿵의 힘은 150 ~ 400Hz 에 몰려 있다)
        thud = fade(norm(hp(thud, 90)), 0.002, 0.05)
        c = int(ct * SR); n = int(0.12 * SR); cr = hp(p5[c:c + n].copy(), 600)
        cr = norm(cr * np.minimum(1, T(n) / 0.006) * np.exp(-T(n) / 0.040))         # 자박: 빠르게 올랐다 0.04초에 잦아든다
        s = np.zeros(int(0.16 * SR)); place(s, thud, 0.0, 1.0); place(s, cr, 0.010, 0.50)
        out.append(norm(s))
    return out
def make_a():
    S = steps(); y = np.zeros(int(0.98 * SR))
    for s, at, g in zip(S, (0.02, 0.38, 0.74), (1.0, 0.84, 0.94)): place(y, s, at, g)
    return fade(norm(y) * 0.82, 0.002, 0.06)
def make_b():
    S = steps(); sh = dec(os.path.join(ROOT, 'audio7/raw/sfx_sheath.mp3')); a = onset(sh, 0.0, 0.2); sh = fade(norm(hp(sh[a:a + int(0.30 * SR)], 200)), 0.002, 0.10)
    y = np.zeros(int(1.04 * SR)); place(y, S[0], 0.02, 1.0); place(y, S[1], 0.38, 0.86); place(y, sh, 0.72, 0.62)
    return fade(norm(y) * 0.82, 0.002, 0.06)
def make_c():
    p5 = dec(os.path.join(RAW, 'patrol5.mp3')); a = int(0.40 * SR); y = hp(p5[a:a + int(0.90 * SR)].copy(), 120)
    return fade(norm(y) * 0.70, 0.05, 0.25)
def shape(x, name):
    n10 = int(SR * 0.01); env = np.array([np.abs(x[i:i + n10]).max() for i in range(0, max(1, len(x) - n10), n10)]); pk = float(np.abs(x).max())
    f = np.abs(np.fft.rfft(x)) ** 2; fr = np.fft.rfftfreq(len(x), 1 / SR); tot = max(f.sum(), 1e-12)
    band = lambda a, b: f[(fr >= a) & (fr < b)].sum() / tot * 100
    hits = [i for i in range(1, len(env) - 1) if env[i] > env[i - 1] and env[i] >= env[i + 1] and env[i] > 0.5 * pk]
    med = np.median(f[(fr > 100) & (fr < 8000)]) + 1e-15; tone = f[(fr > 100) & (fr < 8000)].max() / med
    return '%-9s 길이 %.2fs  봉우리 %.2f  실효값 %.3f  0.98 넘는 점 %d  150Hz 아래 %2.0f%% · 150~1000Hz %2.0f%% · 1~3kHz %2.0f%% · 3kHz 위 %2.0f%%  가장 센 줄/가운데값 %.0f  타격 %s' % (
        name, len(x) / SR, pk, float(np.sqrt((x ** 2).mean())), int((np.abs(x) >= 0.98).sum()), band(0, 150), band(150, 1000), band(1000, 3000), band(3000, 22050), tone, [round(h / 100, 2) for h in hits])
def main():
    src = open(BASE, encoding='utf-8').read(); old = dict(re.findall(r'^\s*(\w+): "([A-Za-z0-9+/=]+)"', src, re.M)); assert len(old) == 30 and 'clack' in old, len(old)
    os.makedirs(OUT, exist_ok=True); C = {'a': make_a(), 'b': make_b(), 'c': make_c()}; b64 = {}
    for k, y in C.items():
        p = os.path.join(OUT, 'patrol_%s.mp3' % k); enc(y, p); b64[k] = base64.b64encode(open(p, 'rb').read()).decode()
    if '--check' in sys.argv:
        print('옛 소리'); print('  ' + shape(dec_bytes(base64.b64decode(old['clack'])), 'clack'))
        print('후보'); [print('  ' + shape(dec_bytes(base64.b64decode(b64[k])), 'patrol_' + k)) for k in C]
    assert 'patrol' not in old                                                    # 있던 이름과 겹치지 않게(march 는 부대가 걷는 소리로 이미 있다)
    data = {k: v for k, v in old.items() if k != 'clack'}; data['patrol'] = b64[PICK]
    head = src[:src.index('var SFX_DATA')].rstrip()
    assert head.endswith('*/'), head[-40:]
    head = head[:-2].rstrip() + ' +\n   v0.25 에 순찰의 소리를 순라군의 발걸음 patrol 로 바꿨다(tools/make_audio_v025.py — 딱따기 clack 은 뺐다: 셈으로 만든 맑은 두 음이 "땡 — 똥"처럼 들렸다) */\n'
    js = head + 'var SFX_DATA = {\n' + ',\n'.join('  %s: "%s"' % (k, v) for k, v in data.items()) + '\n};\n'
    open(os.path.join(ROOT, 'src/sfxdata.js'), 'w', encoding='utf-8').write(js)
    same = all(data[k] == old[k] for k in old if k != 'clack') and len(data) == len(old)
    print('옮긴 소리 %d개(바뀐 것 없음: %s) · 뺀 소리 clack · 넣은 소리 patrol(후보 %s) → src/sfxdata.js %d바이트' % (len(data) - 1, same, PICK, len(js)))
    for k in C: print('  patrol_%s %6d바이트' % (k, len(base64.b64decode(b64[k]))))
if __name__ == '__main__': main()
