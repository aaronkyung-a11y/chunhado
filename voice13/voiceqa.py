import sys, subprocess, numpy as np
from scipy import signal
SR = 16000
def dec(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768
def f0s(x):
    """프레임마다 자기상관으로 음높이(70~400Hz). 목소리가 있는 프레임만"""
    n = int(0.04 * SR); h = int(0.01 * SR); out = []
    pk = np.abs(x).max() or 1
    for i in range(0, len(x) - n, h):
        s = x[i:i + n] * np.hanning(n)
        if np.sqrt((s ** 2).mean()) < 0.04 * pk: continue
        ac = np.correlate(s, s, 'full')[n - 1:]; ac /= ac[0] + 1e-12
        lo, hi = SR // 400, SR // 70; j = lo + int(np.argmax(ac[lo:hi]))
        if ac[j] > 0.45: out.append(SR / j)
    return np.array(out)
def mfcc_mean(x):
    f, t, S = signal.spectrogram(x, SR, nperseg=400, noverlap=240); S = S + 1e-12
    mel = lambda hz: 2595 * np.log10(1 + hz / 700); imel = lambda m: 700 * (10 ** (m / 2595) - 1)
    edges = imel(np.linspace(mel(80), mel(7000), 28)); fb = np.zeros((26, len(f)))
    for k in range(26):
        a, b, c = edges[k], edges[k + 1], edges[k + 2]; fb[k] = np.clip(np.minimum((f - a) / (b - a), (c - f) / (c - b)), 0, None)
    E = np.log(fb @ S + 1e-12); en = E.mean(0); keep = en > np.percentile(en, 40)
    from scipy.fft import dct
    C = dct(E[:, keep], axis=0, norm='ortho')[1:13]
    return C.mean(1)
def info(p):
    x = dec(p); f = f0s(x)
    mx = 20 * np.log10(np.abs(x).max() + 1e-9); rms = 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9)
    return dict(dur=len(x) / SR, peak=mx, rms=rms, f0=float(np.median(f)) if len(f) else 0, voiced=len(f), m=mfcc_mean(x))
if __name__ == '__main__':
    I = {p: info(p) for p in sys.argv[1:]}
    for p, v in I.items(): print('%-18s %.2fs  peak %6.1fdB  rms %6.1fdB  f0 %5.0fHz  (voiced %3d)' % (p, v['dur'], v['peak'], v['rms'], v['f0'], v['voiced']))
    ks = list(I)
    print('MFCC 거리:')
    for a in ks: print('  %-16s' % a, ' '.join('%5.1f' % np.linalg.norm(I[a]['m'] - I[b]['m']) for b in ks))
