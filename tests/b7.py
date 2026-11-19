# 만든 음악을 오프라인으로 20초씩 그려서 크기(피크·RMS)를 잰다 — 무음·찢어짐이 없는지
from browser import *
import json, base64, struct, os
def steps(pg):
    for name in ['title', 'field', 'battle', 'victory', 'defeat']:
        r = pg.evaluate('''(name) => new Promise((res) => {
          var sr = 44100, secs = 20, oc = new OfflineAudioContext(2, sr * secs, sr), saveAC = AC, saveG = SYN.g, saveB = SYN.bufs, saveN = NOISE;
          AC = oc; SYN.bufs = {}; var nb = oc.createBuffer(1, sr, sr), nd = nb.getChannelData(0); for (var i = 0; i < sr; i++) nd[i] = Math.random() * 2 - 1; NOISE = nb;
          SYN.g = synBus(oc); SYN.g.gain.value = BGM.vol * SYN_STYLE[name].gain;
          var st = SYN_STYLE[name], sp = 60 / st.bpm / 2, t = 0.1, s = 0; SYN.last = 5; SYN.hold = 0;
          var pad = padOn(st.pad, name === 'battle' ? 0.07 : 0.05);
          while (t < secs - 2.6) { synStep(name, s, t, st); s++; t += sp; }
          oc.startRendering().then(function (buf) {
            var L = buf.getChannelData(0), R = buf.getChannelData(1), peak = 0, sum = 0, n = L.length, rms = [];
            for (var k = 0; k < secs; k++) { var q = 0; for (var i = k * sr; i < (k + 1) * sr; i++) { var v = Math.max(Math.abs(L[i]), Math.abs(R[i])); if (v > peak) peak = v; q += L[i] * L[i]; } rms.push(+Math.sqrt(q / sr).toFixed(3)); }
            // 8초를 16비트 모노로 내보낸다(스펙트럼 확인용)
            var pcm = new Int16Array(sr * 8); for (var i = 0; i < pcm.length; i++) pcm[i] = Math.max(-1, Math.min(1, (L[i + sr * 4] + R[i + sr * 4]) / 2)) * 32767;
            var u8 = new Uint8Array(pcm.buffer), bin = ''; for (var i = 0; i < u8.length; i += 8192) bin += String.fromCharCode.apply(null, u8.subarray(i, i + 8192));
            AC = saveAC; SYN.g = saveG; SYN.bufs = saveB; NOISE = saveN;
            res({ name: name, steps: s, peak: +peak.toFixed(3), rms: rms, pcm: btoa(bin) });
          });
        })''', name)
        pcm = base64.b64decode(r.pop('pcm'))
        open(os.path.join(SHOTS, 'bgm_%s.raw' % name), 'wb').write(pcm)
        print(json.dumps(r, ensure_ascii=False))
run(steps)
print('ERRORS', [e for e in errors if 'ReadPixels' not in e][:12])
