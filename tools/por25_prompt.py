#!/usr/bin/env python3
"""v0.25 개별 초상 253장 — 새 무장 83명 + 공용 초상을 쓰던 170명(모두 남성). 장면은 art/por25_scenes.tsv(손으로 쓴 것: 번호 · key · 이름 · 포인트색 · 장면).
화풍 문구는 v0.18(남) · v0.24 공용 초상과 같다. 본(참조 그림) 없이 글만으로 그린다.
usage: por25_prompt.py keys [tsv] | text <key> [tsv] | batches <dir> [tsv]      (batches: <dir>/b01.json … — generate_image_batch 의 requests, 12장씩)
tsv 를 주지 않으면 이 파일 옆의 por25_scenes.tsv, 없으면 ../art/por25_scenes.tsv 를 읽는다(Higgsfield 샌드박스에서는 두 파일을 같은 곳에 받아 돌린다)."""
import sys, os, json
AM = "A dramatic East Asian ink-brush illustration of a man of the Three Kingdoms era of China (around AD 200). Subject: "
BM = (" Composition: his head on the vertical center line, figure centered, equal blank white paper left and right. Dynamic angle, heroic proportions, intense expression, sweeping motion; "
      "thick black brushwork, gray wash, dry-brush, ink splatter; one accent color only (%s). Vertical; head fully visible, at least 1/5 of picture height; lower body fades into dry brush. "
      "Pure white background, no text, seal or border.")
HERE = os.path.dirname(os.path.abspath(__file__))
def find(arg):
    for p in ([arg] if arg else []) + [os.path.join(HERE, 'por25_scenes.tsv'), os.path.join(HERE, '..', 'art', 'por25_scenes.tsv')]:
        if p and os.path.exists(p): return p
    sys.exit('por25_scenes.tsv 를 찾지 못했다')
def load(arg=None):
    rows = []                                          # (번호, 열쇠, 이름, 포인트색, 장면)
    for l in open(find(arg), encoding='utf8'):
        l = l.rstrip('\n')
        if not l or l.startswith('#'): continue
        a = l.split('\t')
        if len(a) == 5: a = a[1:]                      # 번호가 앞에 붙은 꼴(번호 key 이름 색 장면 — tools/ids24.py · dl_por17.py 가 읽는 꼴)도, 번호 없는 꼴도 읽는다. 번호는 늘 줄 차례
        k, name, col, scene = a
        rows.append((len(rows) + 1, k, name, col, scene))
    assert len({r[1] for r in rows}) == len(rows), '열쇠가 겹친다'
    return rows
def text(r): return AM + r[4] + (BM % r[3])
def req(r): return {"index": r[0], "params": {"model": "gpt_image_2_6", "aspect_ratio": "3:4", "resolution": "1k", "quality": "high", "prompt": text(r)}}
if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'keys':
        rows = load(sys.argv[2] if len(sys.argv) > 2 else None)
        print(len(rows), ' '.join('%d:%s' % (r[0], r[1]) for r in rows))
    elif cmd == 'text':
        rows = load(sys.argv[3] if len(sys.argv) > 3 else None)
        print(text({r[1]: r for r in rows}[sys.argv[2]]))
    elif cmd == 'batches':
        rows = load(sys.argv[3] if len(sys.argv) > 3 else None)
        os.makedirs(sys.argv[2], exist_ok=True)
        for b in range(0, len(rows), 12):
            json.dump({"requests": [req(r) for r in rows[b:b + 12]]}, open(os.path.join(sys.argv[2], 'b%02d.json' % (b // 12 + 1)), 'w', encoding='utf8'), ensure_ascii=False)
        print('batches', (len(rows) + 11) // 12, 'keys', len(rows), 'chars', sum(len(text(r)) for r in rows))
