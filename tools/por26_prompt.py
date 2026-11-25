#!/usr/bin/env python3
"""v0.26 개별 초상 253장을 다시 그린다 — 자세 · 시점 · 크기를 사람마다 다르게.
   왜: (11-25 23:20) "초상화 포즈가 너무 비슷하네" · (23:24) "다시 그려. 초상화가 다양성이 있으면 좋겠어."
     0.25 의 253장은 거의 모두 '가운데에 선 반신 · 아래에서 올려다본 각도'였다 — 문구의 구도 줄이 모든 그림을 같은 틀에 넣었고, 덜 알려진 사람의 장면이 거의 같았다.
   고친 것: ① 구도 줄을 뺐다(얼굴이 잘리지 않게만 — 흉상은 얼굴을 찾아 자르므로 가운데가 아니어도 된다)
           ② 사람마다 방향(옆 · 비스듬히 · 뒤돌아봄 · 정면) × 시점(눈높이 · 내려다봄 · 올려다봄) × 크기(얼굴 가까이 · 반신 · 무릎 위 · 온몸)를 차례로 돌려 준다
           ③ 장면에 자세가 적혀 있지 않으면 자세(걷는 · 말 탄 · 무릎 꿇은 · 앉은 …)도, 나이 · 생김새가 적혀 있지 않으면 그것도 덧붙인다
   장면(누구인가 · 무엇을 들었나)은 0.25 와 같다: art/por25_scenes.tsv. 열쇠도 같다(그림만 바뀐다).
usage: por26_prompt.py keys [tsv] | text <key> [tsv] | poses <out.tsv> [tsv] | batches <dir> [tsv] | pick <out.json> <번호,번호,…> [tsv]"""
import sys, os, json
AM = "A dramatic East Asian ink-brush illustration of a man of the Three Kingdoms era of China (around AD 200). Subject: "
BM = (" Follow the pose and camera description exactly; do not fall back to a centered, front-facing hero pose. "
      "Thick black brushwork, gray wash, dry-brush, ink splatter; one accent color only (%s). Vertical picture; his whole head and face clearly visible and not cut off by the picture edge; "
      "the figure fades into dry brush at the bottom. Pure white background, no text, seal or border.")
VIEW = {'3qL': "Three-quarter view: his body angled toward the left edge of the picture, face turned partly toward the viewer.",
        '3qR': "Three-quarter view: his body angled toward the right edge of the picture, face turned partly toward the viewer.",
        'sideL': "Side view: he faces the left edge of the picture, seen almost in profile (the far eye just visible).",
        'sideR': "Side view: he faces the right edge of the picture, seen almost in profile (the far eye just visible).",
        'back': "Seen from behind at an angle: his back and one shoulder toward the viewer, head turned back over the shoulder so that his face is clearly visible.",
        'front': "Frontal view, squarely facing the viewer."}
VIEW_SEQ = ['3qL', 'sideR', 'back', '3qR', 'front', 'sideL', '3qR', '3qL', 'back', 'sideL', '3qL', 'front', 'sideR', '3qR']
CAM = {'eye': "Camera at eye level.", 'low': "Camera low, looking up at him.", 'high': "Camera high above, looking down on him; his face tilted up toward the viewer."}
CAM_SEQ = ['eye', 'high', 'low', 'eye', 'high', 'eye', 'low', 'eye', 'high']
FRAME = {'bust': "Close-up: head and shoulders only; the face large, about one third of the picture height.",
         'half': "Half-length figure, from the waist up.",
         'knee': "Three-quarter-length figure, from the knees up.",
         'full': "Full-length figure from head to feet, with wide blank white paper around him; the head about one sixth of the picture height."}
FRAME_SEQ = ['half', 'bust', 'full', 'knee', 'half', 'full', 'bust', 'knee', 'half', 'bust', 'knee']
STANCE_W = ['standing firm with feet planted wide', 'striding forward in mid-step', 'mounted on a galloping horse', 'kneeling on one knee', 'crouched low in a fighting stance',
            'mounted on a rearing horse', 'twisting sharply in mid-turn, cloak swirling', 'standing at ease with his weight on one leg']
STANCE_C = ['standing upright', 'seated on a mat behind a low desk', 'walking slowly, robe trailing', 'seated cross-legged on a mat', 'kneeling formally',
            'standing with one hand behind his back', 'leaning forward over a low table', 'seated on a stool']
PLACE_SEQ = ['', 'He is placed left of center, with open blank paper on the right.', '', 'He is placed right of center, with open blank paper on the left.', '', 'He is placed low in the frame, with blank paper above.', '']
FACE = ['in his twenties, clean-shaven, with a sharp jaw', 'about thirty with a thin mustache', 'in his forties with a full black beard', 'about fifty with a graying goatee',
        'weather-beaten, in his thirties, with a scar across one cheek', 'broad-faced with thick eyebrows and a short beard', 'narrow-eyed and hollow-cheeked, about forty',
        'round-faced and stocky, about thirty-five', 'long-faced with a long thin beard, about forty-five', 'square-jawed and stubbled, about thirty',
        'in his sixties with a white beard and deep wrinkles', 'youthful, about twenty-five, with long sideburns']
HAS_POSE = ('kneel', 'bow', 'seated', 'sitting', 'riding', 'horse', 'rider', 'mounted', 'lounging', 'leaning', 'climbing', 'leap', 'rushing', 'charging', 'walking', 'leading', 'crouch', 'lunging',
            'on a wall', 'on a city wall', 'prow', 'riverboat', 'night watch', 'playing a zither', 'reading', 'writing', 'drafting', 'studying a map', 'singing', 'flees', 'braced')
HAS_FACE = ('young', 'old', 'elder', 'aging', 'beard', 'white-haired', 'gray', 'in his ', 'of about', 'youth', 'gaunt', 'plump', 'fat', 'obese', 'stout', 'stocky', 'lean', 'thin', 'handsome',
            'giant', 'burly', 'sickly', 'soft-faced', 'portly', 'veteran', 'weathered', 'shaggy', 'wild-haired', 'tall', 'emperor', 'prince')
CIVIL = ('robe', 'scholar', 'official', 'adviser', 'minister', 'hermit', 'merchant', 'poet', 'envoy', 'courtier', 'clerk', 'nobleman', 'critic', 'attendant', 'censor', 'judge', 'statesman')
HERE = os.path.dirname(os.path.abspath(__file__))
def find(arg):
    for p in ([arg] if arg else []) + [os.path.join(HERE, 'por25_scenes.tsv'), os.path.join(HERE, '..', 'art', 'por25_scenes.tsv')]:
        if p and os.path.exists(p): return p
    sys.exit('por25_scenes.tsv 를 찾지 못했다')
def pose(i, scene):
    """번호(1 ~)와 장면 → (방향, 시점, 크기, 자세, 자리, 생김새). 길이가 서로소인 차례 넷을 돌려 이웃한 사람끼리 겹치지 않게 한다(14 × 11 × 9)."""
    s = scene.lower(); v = VIEW_SEQ[i % 14]; f = FRAME_SEQ[i % 11]; c = CAM_SEQ[i % 9]
    civil = 'armor' not in s and any(w in s for w in CIVIL)
    st = '' if f == 'bust' or any(w in s for w in HAS_POSE) else (STANCE_C if civil else STANCE_W)[(i * 3 + i // 8) % 8]
    if 'mounted' in st and f == 'full': st += ', horse and rider both in view'
    pl = '' if f == 'bust' else PLACE_SEQ[i % 7]
    fa = '' if any(w in s for w in HAS_FACE) else FACE[(i * 5 + i // 12) % 12]
    return v, c, f, st, pl, fa
def load(arg=None):
    rows = []                                          # (번호, 열쇠, 이름, 포인트색, 장면, 자세 …)
    for l in open(find(arg), encoding='utf8'):
        l = l.rstrip('\n')
        if not l or l.startswith('#'): continue
        a = l.split('\t')
        if len(a) == 5: a = a[1:]
        k, name, col, scene = a
        rows.append((len(rows) + 1, k, name, col, scene) + pose(len(rows) + 1, scene))
    return rows
def text(r):
    v, c, f, st, pl, fa = r[5:]
    return (AM + r[4] + (' He is ' + fa + '.' if fa else '') + ' Pose and camera: ' + VIEW[v] + ' ' + CAM[c] + ' ' + FRAME[f] + (' He is ' + st + '.' if st else '') + (' ' + pl if pl else '') + (BM % r[3]))
def req(r): return {"index": r[0], "params": {"model": "gpt_image_2_6", "aspect_ratio": "3:4", "resolution": "1k", "quality": "high", "prompt": text(r)}}
if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'keys':
        rows = load(sys.argv[2] if len(sys.argv) > 2 else None); print(len(rows), ' '.join('%d:%s' % (r[0], r[1]) for r in rows))
    elif cmd == 'text':
        rows = load(sys.argv[3] if len(sys.argv) > 3 else None); print(text({r[1]: r for r in rows}[sys.argv[2]]))
    elif cmd == 'poses':
        rows = load(sys.argv[3] if len(sys.argv) > 3 else None)
        with open(sys.argv[2], 'w', encoding='utf8') as o:
            o.write('# v0.26 초상의 자세 표(tools/por26_prompt.py 가 만든다 — 손으로 고치지 않는다): 번호 key 이름 방향 시점 크기 자세 자리 생김새\n')
            for r in rows: o.write('\t'.join([str(r[0]), r[1], r[2]] + [x or '-' for x in r[5:]]) + '\n')
        cnt = {}
        for r in rows:
            for j, n in ((5, '방향'), (6, '시점'), (7, '크기')): cnt.setdefault(n, {}); cnt[n][r[j]] = cnt[n].get(r[j], 0) + 1
        print('poses', len(rows), json.dumps(cnt, ensure_ascii=False), '자세를 덧붙인 사람', sum(1 for r in rows if r[8]), '생김새를 덧붙인 사람', sum(1 for r in rows if r[10]),
              '서로 다른 짝(방향 · 시점 · 크기)', len({r[5:8] for r in rows}))
    elif cmd == 'batches':
        rows = load(sys.argv[3] if len(sys.argv) > 3 else None); os.makedirs(sys.argv[2], exist_ok=True)
        for b in range(0, len(rows), 12):
            json.dump({"requests": [req(r) for r in rows[b:b + 12]]}, open(os.path.join(sys.argv[2], 'b%02d.json' % (b // 12 + 1)), 'w', encoding='utf8'), ensure_ascii=False)
        print('batches', (len(rows) + 11) // 12, 'keys', len(rows), 'chars', sum(len(text(r)) for r in rows))
    elif cmd == 'pick':
        rows = load(sys.argv[4] if len(sys.argv) > 4 else None); want = [int(x) for x in sys.argv[3].split(',')]; by = {r[0]: r for r in rows}
        json.dump({"requests": [req(by[i]) for i in want]}, open(sys.argv[2], 'w', encoding='utf8'), ensure_ascii=False)
        print('pick', len(want), ' | '.join('%d %s: %s' % (i, by[i][2], '·'.join(x for x in by[i][5:8])) for i in want))
