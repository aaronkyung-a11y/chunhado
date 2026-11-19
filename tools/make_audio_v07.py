#!/usr/bin/env python3
"""v0.7 소리 만들기: audio7/raw 의 원본(Higgsfield: 음악 elevenlabs_music_v2_5, 효과음 mirelo_text_to_audio)을 다듬어
   ① bgm/<곡>.mp3 (음량 맞춤, 앞뒤 무음 정리, 112kbps)  ② src/sfxdata.js (효과음 잘라 내기·정규화 → mp3 64kbps → base64)
usage: make_audio_v07.py [music] [sfx]   (인수가 없으면 둘 다)"""
import sys, os, subprocess, json, re, base64, io
import numpy as np
from scipy import signal
from scipy.io import wavfile
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
RAW = os.path.join(ROOT, 'audio7/raw'); SR = 44100
def dec(path, ch=1):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', str(ch), '-ar', str(SR), '-f', 's16le', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    return x.reshape(-1, ch) if ch > 1 else x
def enc(x, out, kbps, ch=1):
    tmp = out + '.wav'; wavfile.write(tmp, SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-c:a', 'libmp3lame', '-b:a', '%dk' % kbps, '-ac', str(ch), out], check=True); os.remove(tmp)
def fade(x, fin, fout):
    n = len(x); a = int(fin * SR); b = int(fout * SR); x = x.copy()
    if a > 0: x[:a] *= np.linspace(0, 1, a) ** 0.7
    if b > 0: x[n - b:] *= np.linspace(1, 0, b) ** 1.5
    return x
def harm(x, k):
    """작은 스피커에서도 들리게: 낮은 소리에 배음을 더한다(포화)"""
    pk = max(np.abs(x).max(), 1e-6); y = np.tanh(x / pk * k) * pk
    sos = signal.butter(2, 150, 'highpass', fs=SR, output='sos')
    return x * 0.75 + signal.sosfilt(sos, y) * 0.6
# 이름: (원본, 시작 방법, 길이, 사라짐, 배음, 고역통과Hz)   시작 방법: 숫자 = 초, 'auto' = 처음으로 소리가 커지는 곳
SFX = {
    'tick':   ('build', 'auto', 0.16, 0.06, 0, 180), 'page':  ('scroll', 'auto', 0.45, 0.15, 0, 150),
    'stomp':  ('step', 'auto', 0.30, 0.10, 0, 80),   'march': ('step', 'auto', 1.60, 0.35, 0, 80),
    'gallop': ('hoof', 'auto', 1.60, 0.35, 0, 80),   'cavalry': ('cavalry', 0.0, 1.80, 0.40, 0, 80),
    'cart':   ('cart', 0.0, 1.90, 0.45, 2.5, 60),    'slash': ('slash', 'auto', 0.70, 0.22, 0, 120),
    'clang':  ('clang', 'auto', 0.70, 0.25, 0, 150), 'crush': ('crush', 'auto', 1.30, 0.45, 0, 60),
    'bow':    ('bow', 'auto', 0.30, 0.12, 0, 100),   'arrows': ('arrows', 0.55, 1.45, 0.30, 0, 150),
    'fire':   ('fire', 0.0, 2.20, 0.55, 0, 80),      'drum':  ('drum', 'main', 1.10, 0.35, 3.0, 40),
    'drums':  ('drums', 1.95, 1.05, 0.12, 2.0, 40), 'horn': ('horn', 0.0, 2.40, 0.60, 4.0, 40),
    'gong':   ('gong', 'auto', 2.30, 0.90, 3.0, 50), 'fall':  ('fall', 0.0, 4.00, 0.50, 0, 60),
    'cheer':  ('cheer', 0.0, 2.40, 0.90, 0, 120),    'rout':  ('rout', 0.0, 2.20, 0.80, 0, 120),
    'coin':   ('coin', 'auto', 1.30, 0.25, 0, 300),  'thud':  ('thud', 'auto', 0.45, 0.18, 2.0, 60),
    'duel':   ('duel', 0.0, 2.40, 0.50, 0, 100),     'wind':  ('wind', 0.0, 1.60, 0.60, 0, 100),
    'douse':  ('douse', 0.0, 1.60, 0.50, 0, 150),    'shout': ('shout', 0.0, 1.20, 0.40, 0, 150),
}
def onset(x, thr=0.14, back=0.012):
    pk = np.abs(x).max(); env = np.abs(signal.sosfiltfilt(signal.butter(2, 60, 'lowpass', fs=SR, output='sos'), np.abs(x)))
    i = int(np.argmax(env > thr * env.max())); return max(0, i - int(back * SR))
def onset_main(x, back=0.015):
    """가장 큰 소리 덩어리가 시작되는 곳(앞의 작은 소리는 건너뛴다)"""
    env = np.abs(signal.sosfiltfilt(signal.butter(2, 30, 'lowpass', fs=SR, output='sos'), np.abs(x))); pk = int(np.argmax(env)); i = pk
    while i > 0 and env[i] > 0.08 * env[pk] and pk - i < 0.6 * SR: i -= 1
    return max(0, i - int(back * SR))
def do_sfx():
    os.makedirs(os.path.join(ROOT, 'audio7/sfx'), exist_ok=True); data = {}; rep = []
    for name, (src, st, dur, fo, hk, hp) in SFX.items():
        x = dec(os.path.join(RAW, 'sfx_%s.mp3' % src))
        i0 = onset(x) if st == 'auto' else (onset_main(x) if st == 'main' else int(st * SR))
        y = x[i0:i0 + int(dur * SR)].astype(np.float64)
        y = signal.sosfilt(signal.butter(2, hp, 'highpass', fs=SR, output='sos'), y)
        if hk: y = harm(y, hk)
        y = fade(y, 0.003, fo); y = y / max(np.abs(y).max(), 1e-6) * 0.84
        out = os.path.join(ROOT, 'audio7/sfx', name + '.mp3'); enc(y, out, 64)
        data[name] = open(out, 'rb').read(); rep.append((name, src, round(i0 / SR, 2), round(len(y) / SR, 2), len(data[name])))
    # 망치질: 나무 두드리는 소리(tick)를 세 번
    t = dec(os.path.join(ROOT, 'audio7/sfx', 'tick.mp3')); n = int(0.75 * SR); y = np.zeros(n)
    for k, (at, g, rate) in enumerate([(0.0, 1.0, 1.0), (0.22, 0.8, 1.06), (0.44, 0.95, 0.96)]):
        s = signal.resample(t, int(len(t) / rate)); a = int(at * SR); m = min(len(s), n - a); y[a:a + m] += s[:m] * g
    y = y / np.abs(y).max() * 0.84; out = os.path.join(ROOT, 'audio7/sfx', 'hammer.mp3'); enc(y, out, 64); data['hammer'] = open(out, 'rb').read(); rep.append(('hammer', 'tick x3', 0, 0.75, len(data['hammer'])))
    js = '/* 효과음(v0.7): Higgsfield mirelo_text_to_audio 로 만든 소리를 잘라 정규화한 mp3(모노 64kbps). 만드는 법: tools/make_audio_v07.py */\nvar SFX_DATA = {\n' + ',\n'.join('  %s: "%s"' % (k, base64.b64encode(v).decode()) for k, v in data.items()) + '\n};\n'
    open(os.path.join(ROOT, 'src/sfxdata.js'), 'w').write(js)
    for r in rep: print('  sfx %-8s ← %-8s 시작 %.2fs 길이 %.2fs %6d바이트' % r)
    print('sfx', len(data), '개', sum(len(v) for v in data.values()), '바이트 → src/sfxdata.js', len(js), '바이트')
MUSIC = {'title': -19.0, 'field1': -18.0, 'field2': -18.0, 'tense': -18.5, 'battle1': -16.5, 'battle2': -16.5, 'victory': -16.5, 'defeat': -20.0}   # 목표 음량(LUFS)
def loud(path):
    e = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    s = e[e.rfind('Summary:'):]
    return float(re.search(r'I:\s+([-\d.]+) LUFS', s).group(1)), float(re.search(r'Peak:\s+([-\d.]+) dBFS', s).group(1))
def do_music():
    os.makedirs(os.path.join(ROOT, 'bgm'), exist_ok=True); tot = 0
    for name, target in MUSIC.items():
        src = os.path.join(RAW, 'music_%s.mp3' % name); x = dec(src, 2)
        mono = np.abs(x).max(axis=1); thr = 10 ** (-48 / 20)
        idx = np.nonzero(mono > thr)[0]; a = max(0, idx[0] - int(0.05 * SR)); b = min(len(x), idx[-1] + int(0.4 * SR))      # 앞뒤 무음 정리
        y = x[a:b].astype(np.float64)
        tail = np.sqrt(np.mean(y[-int(0.5 * SR):] ** 2)); body = np.sqrt(np.mean(y ** 2))
        fo = 0.3 if tail < body * 0.05 else 2.0                                                                          # 끝이 아직 크면 2초에 걸쳐 줄인다
        n = int(fo * SR); y[-n:] *= (np.linspace(1, 0, n) ** 1.3)[:, None]; n2 = int(0.02 * SR); y[:n2] *= np.linspace(0, 1, n2)[:, None]
        tmp = os.path.join(ROOT, 'audio7', 'tmp_%s.wav' % name); wavfile.write(tmp, SR, (np.clip(y, -1, 1) * 32767).astype(np.int16))
        I, P = loud(tmp); g = min(target - I, -1.0 - P)                                                                   # 한 번에 같은 배율로(곡 안의 셈여림은 그대로)
        out = os.path.join(ROOT, 'bgm', name + '.mp3')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', 'volume=%.2fdB' % g, '-c:a', 'libmp3lame', '-b:a', '112k', '-joint_stereo', '1', out], check=True); os.remove(tmp)
        I2, P2 = loud(out); sz = os.path.getsize(out); tot += sz
        print('  bgm %-8s %6.1fs  %5.1f → %5.1f LUFS (목표 %.1f, 배율 %+.1fdB)  최대 %.1f dBFS  끝 줄임 %.1fs  %d바이트' % (name, len(y) / SR, I, I2, target, g, P2, fo, sz))
    print('bgm', len(MUSIC), '곡', tot, '바이트')
if __name__ == '__main__':
    a = sys.argv[1:] or ['music', 'sfx']
    if 'sfx' in a: do_sfx()
    if 'music' in a: do_music()
