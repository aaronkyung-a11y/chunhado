#!/usr/bin/env python3
"""음성 120개 점검: 길이 · 크기 · 음높이 · 음색(기준 목소리와의 거리) · 글자당 길이. 결과는 qa.json"""
import sys, os, json, re, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voiceqa as Q, lines
L = lines.all_lines(); D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'raw')
ANCH = {'brave': 0, 'sage': 2, 'lord': 4, 'gen': 6, 'lady': 18}
I = [Q.info(os.path.join(D, '%03d.mp3' % i)) for i in range(120)]
def speech(i):
    """말하는 구간의 길이(앞뒤 조용한 곳 빼고)"""
    x = Q.dec(os.path.join(D, '%03d.mp3' % i)); n = int(0.02 * Q.SR)
    e = np.array([np.sqrt((x[k:k + n] ** 2).mean()) for k in range(0, len(x) - n, n)]); th = e.max() * 0.06
    on = np.where(e > th)[0]
    return (on[-1] - on[0] + 1) * 0.02 if len(on) else 0, on[0] * 0.02 if len(on) else 0
rows = []
for i, (kind, sit, n, zh, ko) in enumerate(L):
    v = I[i]; a = I[ANCH[kind]]; sp, lead = speech(i)
    ch = len(re.sub(r'[^一-鿿]', '', zh))
    rows.append(dict(i=i, kind=kind, sit=sit, n=n, zh=zh, dur=round(v['dur'], 2), sp=round(sp, 2), lead=round(lead, 2), ch=ch, spc=round(sp / ch, 3), peak=round(v['peak'], 1), rms=round(v['rms'], 1), f0=round(v['f0']), dist=round(float(np.linalg.norm(v['m'] - a['m'])), 1)))
json.dump(rows, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'qa.json'), 'w'), ensure_ascii=False, indent=0)
for k in ANCH:
    R = [r for r in rows if r['kind'] == k]
    print('%-6s n=%d  f0 %d~%d (중앙 %d)  거리 중앙 %.1f 최대 %.1f  글자당 %.2f~%.2f초  rms %.1f~%.1f  peak %.1f~%.1f' % (k, len(R), min(r['f0'] for r in R), max(r['f0'] for r in R), np.median([r['f0'] for r in R]), np.median([r['dist'] for r in R]), max(r['dist'] for r in R), min(r['spc'] for r in R), max(r['spc'] for r in R), min(r['rms'] for r in R), max(r['rms'] for r in R), min(r['peak'] for r in R), max(r['peak'] for r in R)))
print('--- 눈여겨볼 것')
for r in rows:
    R = [x for x in rows if x['kind'] == r['kind']]; mf = np.median([x['f0'] for x in R]); why = []
    if r['spc'] > 0.55: why.append('길다(글자당 %.2f초)' % r['spc'])
    if r['spc'] < 0.13: why.append('짧다(글자당 %.2f초)' % r['spc'])
    if r['dist'] > 6.5: why.append('음색 거리 %.1f' % r['dist'])
    if r['f0'] and (r['f0'] > mf * 1.45 or r['f0'] < mf / 1.45): why.append('음높이 %d (중앙 %d)' % (r['f0'], mf))
    if r['rms'] < -32: why.append('작다 rms %.1f' % r['rms'])
    if r['peak'] > -0.2: why.append('peak %.1f' % r['peak'])
    if r['dur'] > 6: why.append('전체 %.1f초' % r['dur'])
    if why: print('%3d %-5s %-7s %d  %-14s %.2fs(말 %.2fs)  %s' % (r['i'], r['kind'], r['sit'], r['n'], r['zh'], r['dur'], r['sp'], ' · '.join(why)))
