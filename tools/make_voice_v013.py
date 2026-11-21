#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""중국어 음성(v0.13)을 게임에 넣을 꼴로 다듬는다.
   입력: voice13/raw/NNN.mp3 (Higgsfield Seed Audio 로 뽑은 원본 120개 · 줄 순서는 voice13/lines.py 의 all_lines())
   출력: voice13/out/<갈래>_<상황>_<n>.mp3 (24kHz 모노 40kbps) · src/voicedata.js (VOICE_DATA · VOICE_TEXT)
   하는 일: ① 앞뒤 조용한 곳을 잘라 낸다(앞에 군소리가 붙은 둘은 그 뒤부터) ② 작게 시작해 크게 끝나는 것을 고르게(느린 눌러 주기)
            ③ 말하는 구간의 크기를 한 값으로 맞춘다 ④ 끝을 부드럽게 줄인다.  다시 뽑지 않는다(크레딧 0).
   usage: make_voice_v013.py [--check]"""
import sys, os, subprocess, json, base64, numpy as np
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, os.path.join(ROOT, 'voice13'))
import lines
SR = 24000
HEAD = {41: 1.80, 103: 1.56}          # 앞에 대본에 없는 소리가 붙은 것: 이 시각(초) 뒤에서 시작을 찾는다(받아쓰기 · 크기 곡선으로 본 자리)
TARGET = 10 ** (-19 / 20)             # 말하는 구간의 실효값
PEAK = 10 ** (-1.5 / 20)
def dec(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768
def env(x, win):
    n = max(1, int(win * SR)); k = np.ones(n) / n
    return np.sqrt(np.convolve(x * x, k, 'same') + 1e-12)
def proc(x, head):
    if head: x = x[int(head * SR):]
    e = env(x, 0.02); m = e.max()
    on = np.where(e > m * 0.02)[0]                    # 첫소리가 여린 자음(ㅊ · ㅋ 같은 소리)이 잘리지 않게 문턱을 낮추고 앞을 넉넉히 둔다
    if not len(on): return x
    a = max(0, on[0] - int(0.10 * SR)); b = min(len(x), on[-1] + int(0.16 * SR)); x = x[a:b].copy()
    # 느린 눌러 주기: 0.12초 창의 크기가 기준(전체의 75번째 백분위)보다 작으면 올리고 크면 내린다(절반만큼 · 올림은 +10dB 까지 · 아주 조용한 곳은 건드리지 않는다)
    e = env(x, 0.12); ref = np.percentile(e[e > e.max() * 0.05], 75)
    g = (ref / np.maximum(e, 1e-6)) ** 0.5
    g = np.clip(g, 10 ** (-8 / 20), 10 ** (10 / 20)); g[e < e.max() * 0.03] = 1.0
    k = int(0.05 * SR); g = np.convolve(g, np.ones(k) / k, 'same')
    x = x * g
    e = env(x, 0.02); act = e > e.max() * 0.1
    rms = np.sqrt((x[act] ** 2).mean()) if act.any() else np.sqrt((x ** 2).mean())
    x = x * (TARGET / max(rms, 1e-6))
    x = np.tanh(x / PEAK * 1.0) * PEAK if np.abs(x).max() > PEAK else x     # 넘치는 꼭대기만 둥글게
    fi = int(0.004 * SR); fo = int(0.07 * SR)
    x[:fi] *= np.linspace(0, 1, fi); x[-fo:] *= np.linspace(1, 0, fo) ** 1.5
    return x
def enc(x, out):
    pcm = (np.clip(x, -1, 1) * 32767).astype('<i2').tobytes()
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-', '-c:a', 'libmp3lame', '-b:a', '40k', '-ar', str(SR), '-ac', '1', '-write_xing', '0', '-id3v2_version', '0', '-map_metadata', '-1', '-fflags', '+bitexact', '-flags:a', '+bitexact', out], input=pcm, check=True)
def main():
    L = lines.all_lines(); OUT = os.path.join(ROOT, 'voice13', 'out'); os.makedirs(OUT, exist_ok=True)
    data = {}; text = {}; rep = []
    for i, (kind, sit, n, zh, ko) in enumerate(L):
        x = proc(dec(os.path.join(ROOT, 'voice13', 'raw', '%03d.mp3' % i)), HEAD.get(i))
        name = '%s_%s_%d' % (kind, sit, n); p = os.path.join(OUT, name + '.mp3'); enc(x, p)
        b = open(p, 'rb').read(); data[name] = base64.b64encode(b).decode(); text[name] = [zh, ko]
        e = env(x, 0.02); act = e > e.max() * 0.1
        rep.append((i, name, len(x) / SR, len(b), 20 * np.log10(np.sqrt((x[act] ** 2).mean())), 20 * np.log10(np.abs(x).max())))
    if '--check' in sys.argv:
        for r in rep: print('%3d %-18s %.2fs %6d B  rms %.1f  peak %.1f' % r)
    js = '/* 생성물: tools/make_voice_v013.py 가 만든다. 중국어 음성 120개(갈래 다섯 × 상황 열둘 × 둘) — 24kHz 모노 mp3 를 base64 로. */\nvar VOICE_DATA = ' + json.dumps(data, separators=(',', ':')) + ';\nvar VOICE_TEXT = ' + json.dumps(text, ensure_ascii=False, separators=(',', ':')) + ';\n'
    open(os.path.join(ROOT, 'src', 'voicedata.js'), 'w', encoding='utf-8').write(js)
    d = [r[2] for r in rep]; s = [r[3] for r in rep]
    print('clips %d  길이 %.2f~%.2f초(합 %.1f초, 평균 %.2f)  mp3 합 %d B  voicedata.js %d B' % (len(rep), min(d), max(d), sum(d), sum(d) / len(d), sum(s), len(js.encode())))
    print('rms %.1f~%.1f dB  peak %.1f~%.1f dB' % (min(r[4] for r in rep), max(r[4] for r in rep), min(r[5] for r in rep), max(r[5] for r in rep)))
main()
