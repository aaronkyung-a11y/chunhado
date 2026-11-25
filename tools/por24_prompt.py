#!/usr/bin/env python3
"""v0.24 공용 초상 120장(남 60 · 여 60) — 이 판에서 태어나는 아이들이 쓴다(3-2 에서 제 초상이 생기기 전까지는 명부의 공용 초상 253명도).
가장 뛰어난 능력에 맞는 모습 다섯 갈래: 1 무력(무기를 든 무인) · 2 통솔(지휘하는 장수) · 3 지력(책사) · 4 정치(문관) · 5 매력(귀인). 갈래마다 14 · 14 · 12 · 10 · 10 장.
열쇠: gm101 ~ gm114(남 · 무력) … gm501 ~ gm510(남 · 매력), gf101 … gf510(여). 화풍 문구는 v0.17(여) · v0.18(남)과 같다. 본(참조 그림) 없이 글만으로 그린다.
usage: por24_prompt.py keys | text <key> | tsv <art/por24_scenes.tsv> | batches <dir>      (batches: <dir>/b01.json … — generate_image_batch 의 requests, 12장씩)
이 파일 하나로 돈다(다른 파일을 읽지 않는다 — Higgsfield 샌드박스에서도 그대로 돌린다)."""
import sys, os, json
AM = "A dramatic East Asian ink-brush illustration of a man of the Three Kingdoms era of China (around AD 200). Subject: "
BM = (" Composition: his head on the vertical center line, figure centered, equal blank white paper left and right. Dynamic angle, heroic proportions, intense expression, sweeping motion; "
      "thick black brushwork, gray wash, dry-brush, ink splatter; one accent color only (%s). Vertical; head fully visible, at least 1/5 of picture height; lower body fades into dry brush. "
      "Pure white background, no text, seal or border.")
AF = "A dramatic East Asian ink-brush illustration of a woman of the late Han dynasty of China (around AD 200), an adult woman with a clearly beautiful face. Subject: "
BF = (" Composition (important): her head sits on the vertical center line of the picture - horizontally centered, not toward the right or left edge - and the figure is centered, "
      "with about equal blank white paper on the left and on the right. Dynamic camera angle, sweeping motion of sleeves and hair, lively expression; "
      "thick black brushwork, gray wash, dry-brush, ink splatter; one accent color only (%s). Vertical; head fully visible, at least 1/5 of picture height; lower body fades into dry brush. "
      "Pure white background, no text, seal or border.")
COL = ['crimson red', 'indigo blue', 'jade green', 'ochre gold', 'violet purple', 'teal', 'vermilion orange', 'deep blue', 'dark green', 'plum purple']
CAT = [('무력', 14), ('통솔', 14), ('지력', 12), ('정치', 10), ('매력', 10)]
M = dict(
  role=['A fierce young warrior', 'A commanding young general', 'A keen young strategist', 'An upright young civil official', 'A noble, charismatic young lord'],
  face=['about twenty, smooth-faced with sharp bright eyes', 'in his early twenties, clean-shaven with a strong jaw', 'in his mid twenties with a thin mustache', 'about thirty with a short trimmed beard',
        'in his early thirties with a neat goatee', 'in his early twenties with a round face and thick brows', 'in his late twenties, lean, with hollow cheeks and narrow eyes', 'in his mid thirties with a full dark beard'],
  hair=['hair in a topknot bound with a cloth band', 'hair in a topknot held by a jade pin', 'long hair tied back', 'a cloth headband over a topknot'],
  expr=[['a fierce battle cry', 'teeth bared in a wild grin', 'a cold, killing stare', 'blazing eyes'], ['a steady, commanding gaze', 'stern and resolute', 'a confident half-smile'],
        ['calm and calculating', 'a faint knowing smile', 'piercing, thoughtful eyes'], ['composed and dignified', 'earnest and upright', 'shrewd and attentive'], ['a warm, magnetic smile', 'gentle and noble', 'bright, confident eyes']],
  body=[[
    'in black lamellar armor with a wolf-fur collar, thrusting a long spear straight toward the viewer',
    'in iron scale armor, swinging a heavy crescent glaive overhead',
    'bare-armed in a leather cuirass, gripping twin short halberds crossed before his chest',
    'in battered lamellar armor, drawing a great recurve bow to full stretch',
    'in a tiger-pelt mantle over armor, hefting a huge battle axe on his shoulder',
    'in dark armor with a plumed helmet, lunging with a serpent-bladed spear',
    'in light scale armor, mid-leap with a curved saber raised',
    'in heavy armor, whirling a spiked iron mace on a chain',
    'helmetless in spiked pauldrons, both hands on a two-handed great sword held forward',
    'in rough leather-and-iron armor, hurling a javelin',
    'in black armor, crouched low behind a round shield with a short spear',
    'in armor with a torn war cloak, a trident halberd leveled',
    'wearing a horned iron helmet, bringing down a long-handled war hammer',
    'in scale armor, twirling a red-tasseled spear behind his back'], [
    "in ornate general's armor with a long cape, pointing a straight sword forward as if ordering a charge",
    "in a commander's lamellar armor and plumed helmet, raising a war banner high",
    "in armor under an officer's surcoat, arms folded, studying the battlefield",
    "in a general's armor with a tiger-head belt, lifting a command baton",
    'in dark armor and a billowing cloak, one hand on his sword hilt, the other raised to halt his men',
    "wearing a winged commander's helmet, holding a signal flag across his chest",
    'in layered armor with a silk sash, one arm raised to beat a war drum',
    "in a cavalry general's armor, shading his eyes to look far ahead, a spear resting on his shoulder",
    'in polished scale armor and cape, unrolling a battle map across his forearm while glancing up',
    'in armor with a high-crested helmet tucked under his arm, calm and upright',
    "in a general's armor, drawing a jeweled command sword halfway from its scabbard",
    'in armor and a storm-blown cloak, pointing with a folded fan toward distant hills',
    'wearing a lion-crest helmet, both hands resting on the pommel of a long sword set point-down',
    "in a commander's armor, raising a horn-shaped signal trumpet"], [
    "in a plain scholar's robe and tall cap, half-hiding his mouth behind a white feather fan",
    'in a long dark robe, holding an unrolled bamboo-slip scroll, eyes lifted in thought',
    'in a layered robe with wide sleeves, placing a stone on a small go board held in his other hand',
    "in a hooded traveling cloak over a scholar's robe, tracing a route on a map with one finger",
    'in a robe with a crane-pattern sash, counting on his fingers with a sly sidelong glance',
    "in a strategist's robe and cloth cap, writing with a brush on a bamboo slip",
    'in a pale robe, holding a small oil lamp over a stack of scrolls',
    'in a dark robe, holding a star chart and pointing up at the sky',
    "in a scholar's robe, stroking his chin while a folded fan taps his palm",
    'in a robe and feathered headcloth, releasing a carrier pigeon from his hand',
    "in a simple hermit's robe with a wicker hat on his back, leaning on a bamboo staff",
    "in an adviser's robe, whispering behind a raised sleeve"], [
    "in a court official's robe and winged black hat, holding an ivory tablet upright before his chest with both hands",
    "in an official's robe and hat, stamping a document with a bronze seal",
    "in a magistrate's robe and hat, weighing grain on a small hand scale",
    'in a court robe with a jade belt and tall hat, unrolling an edict',
    "in an official's robe and hat, tallying with bamboo counting rods beside a ledger",
    "in a plain official's robe with sleeves tied back, inspecting a sheaf of rice",
    'in a court robe and tall hat, bowing slightly with hands clasped inside his sleeves',
    "in an envoy's robe and hat, standing straight with a tasseled envoy's staff",
    "in an official's robe and hat, reading a petition at arm's length with a slight frown",
    "in a treasurer's robe and hat, holding a string of bronze coins and an account book"], [
    'in a fine embroidered silk robe with a jade pendant, extending an open hand in welcome',
    'in a lordly robe with a fur-lined mantle, laughing warmly with his head slightly back',
    'in an elegant robe and jeweled hair crown, raising a wine cup in a toast',
    "in a noble's robe, cradling a seven-string zither under one arm",
    'in a rich robe with long sleeves, reaching out an arm to help someone up',
    "in a prince's robe with a dragon-pattern sash, standing tall with hands behind his back",
    'in a flowing robe, a falcon perched on his raised gloved fist',
    "in a noble's hunting attire with a short cape, a bow slung at his back",
    "in a scholar-lord's robe, holding a blossoming plum branch",
    'in ceremonial robes and a tall crown-like cap, hands clasped in a courteous salute']])
F = dict(
  role=['A fierce young woman warrior', 'A commanding young woman general', 'A keen young woman strategist', 'A poised young woman court official', 'A graceful, charismatic young noblewoman'],
  face=['about twenty, with a delicate oval face and bright eyes', 'in her early twenties, with high cheekbones and a calm gaze', 'in her mid twenties, with sharp phoenix eyes', 'about thirty, with mature graceful features',
        'in her early twenties, with a round face and a small beauty mark', 'in her late twenties, with strong brows and a proud chin'],
  hair=['hair in a high ponytail tied with a ribbon', 'hair in twin coiled buns with hairpins', 'long hair bound low with a jade clasp', 'hair in a single tall bun with a gold pin', 'braided hair wrapped around her head', 'side-swept hair with a flower pin'],
  expr=[['a fierce battle cry', 'a bold, fearless grin', 'a cold, focused stare', 'blazing eyes'], ['a steady, commanding gaze', 'stern and resolute', 'a confident half-smile'],
        ['calm and calculating', 'a faint knowing smile', 'piercing, thoughtful eyes'], ['composed and dignified', 'earnest and upright', 'shrewd and attentive'], ['a warm, radiant smile', 'gentle and noble', 'bright, confident eyes']],
  body=[[
    'in fitted lamellar armor over a short robe, spinning a long spear',
    'in light scale armor, drawing a short recurve bow to full stretch',
    'in a leather cuirass and arm guards, twin curved sabers crossed before her',
    'in dark armor with a fur collar, thrusting a slender halberd',
    "in a rider's armor and flying cloak, cracking a long whip",
    'in layered light armor, hurling a throwing dagger, more daggers at her belt',
    'in a breastplate over battle robes, swinging a crescent-bladed pole arm',
    'in a tiger-pelt half cape over armor, raising a pair of iron war fans',
    'in scale armor, leaping with a straight sword held in a reverse grip',
    'in light armor, whirling a rope dart around her',
    'in armor and a red-tasseled helmet, leveling a lance',
    'in armor with sleeves tied back, gripping a heavy saber two-handed',
    'in feathered southern warrior armor, holding a javelin and a round rattan shield',
    "in archer's armor with a quiver at her hip, nocking two arrows at once"], [
    "in a commander's armor and long cape, pointing a straight sword forward to order a charge",
    'in ornate armor, raising a war banner with both hands',
    "in armor under a general's surcoat, arms folded, steady eyes on the field",
    "in armor and a plumed commander's helmet, lifting a command baton",
    'in dark armor and a storm-blown cloak, one hand raised to halt her troops',
    "in a general's armor, holding a signal flag across her chest",
    'in armor with a silk sash, one arm raised to strike a war drum',
    'in cavalry armor, shading her eyes to look far ahead, a spear on her shoulder',
    'in polished armor, unrolling a battle map over her forearm while glancing up',
    "in a general's armor with her helmet under her arm, calm and upright",
    "in a commander's armor, drawing a jeweled command sword halfway",
    'in armor and cloak, pointing a folded fan toward distant hills',
    'in lion-crest armor, both hands resting on the pommel of a long sword set point-down',
    "in a commander's armor, raising a signal horn"], [
    "in a scholar's layered robe, half-hiding a knowing smile behind a round silk fan",
    'in a long dark robe, holding an unrolled bamboo-slip scroll, eyes lifted in thought',
    'in a wide-sleeved robe, placing a stone on a small go board held in her other hand',
    'in a hooded traveling cloak, tracing a route on a map with one finger',
    'in a robe with a crane-pattern sash, writing with a brush on a bamboo slip',
    'in a pale robe, holding a small oil lamp over a stack of scrolls',
    'in a dark robe, holding a star chart and pointing up at the night sky',
    'in a layered robe, a folded fan tapping her chin, with a sly sidelong glance',
    "in a healer-scholar's robe, grinding herbs in a small mortar while reading a scroll",
    'in a robe with a veil pushed back, releasing a carrier pigeon from her hands',
    "in an inventor's plain robe with sleeves tied back, holding a small wooden mechanism",
    "in an adviser's robe, whispering behind a raised sleeve"], [
    'in formal court robes and a tall headdress, holding an ivory tablet upright with both hands',
    "in a court official's robe, stamping a document with a bronze seal",
    "in a steward's robe, weighing grain on a small hand scale",
    'in court robes with a jade belt, unrolling an edict',
    "in an official's robe, tallying with bamboo counting rods beside a ledger",
    'in a plain robe with sleeves tied back, inspecting a sheaf of rice',
    'in court robes, bowing slightly with hands clasped inside her sleeves',
    "in an envoy's robe, standing straight with a tasseled envoy's staff",
    "in an official's robe, reading a petition at arm's length with a slight frown",
    "in a treasurer's robe, holding a string of bronze coins and an account book"], [
    'in fine embroidered silk robes with a jade pendant, extending an open hand in welcome',
    "in a noble lady's robe with a fur-lined mantle, laughing warmly",
    'in elegant robes with gold hair ornaments, raising a wine cup in a toast',
    'in flowing robes, playing a pipa lute',
    'in rich long-sleeved robes, mid-dance with her sleeves sweeping in an arc',
    "in a princess's robe with a phoenix-pattern sash, serene, hands folded",
    'in flowing robes, a small falcon perched on her raised gloved fist',
    "in a noble's hunting attire with a short cape, a bow at her back",
    "in a lady's robe, holding a blossoming plum branch",
    'in ceremonial robes and a tall jeweled crown, hands clasped in a courteous salute']])
HEAD = ('helmet', 'hat', 'cap', 'crown', 'headcloth', 'headdress', 'hood', 'veil', 'hair ornaments')
rows = []                                              # (번호, 열쇠, 이름표, 포인트색, 장면, 여성인가)
def build():
    n = 0
    for sex, D in (('m', M), ('f', F)):
        for c, (cn, cnt) in enumerate(CAT):
            for i in range(cnt):
                n += 1
                body = D['body'][c][i]
                face = D['face'][(i * 3 + c * 2 + (1 if sex == 'f' else 0)) % len(D['face'])]
                hair = '' if (sex == 'm' and any(h in body for h in HEAD)) or (sex == 'f' and any(h in body for h in ('helmet', 'headdress', 'crown', 'hood', 'hair ornaments'))) else ', ' + D['hair'][(i + c) % len(D['hair'])]
                expr = D['expr'][c][i % len(D['expr'][c])]
                scene = '%s, %s%s, %s. Expression: %s.' % (D['role'][c], face, hair, body, expr)
                rows.append((n, 'g%s%d%02d' % (sex, c + 1, i + 1), ('남' if sex == 'm' else '여') + '·' + cn + ' %d' % (i + 1), COL[(i * 3 + c + (5 if sex == 'f' else 0)) % len(COL)], scene, sex == 'f'))
build()
BY = {r[1]: r for r in rows}
def text(k): r = BY[k]; return (AF if r[5] else AM) + r[4] + ((BF if r[5] else BM) % r[3])
def req(k): return {"index": BY[k][0], "params": {"model": "gpt_image_2_6", "aspect_ratio": "3:4", "resolution": "1k", "quality": "high", "prompt": text(k)}}
if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'keys': print(len(rows), ' '.join('%d:%s' % (r[0], r[1]) for r in rows))
    elif cmd == 'text': print(text(sys.argv[2]))
    elif cmd == 'tsv':
        with open(sys.argv[2], 'w', encoding='utf8') as f:
            f.write('# v0.24 공용 초상 120장: 번호 <TAB> key <TAB> 이름표 <TAB> 포인트색 <TAB> 장면(영문). tools/por24_prompt.py 가 만든다(손으로 고치지 않는다)\n')
            for r in rows: f.write('%d\t%s\t%s\t%s\t%s\n' % r[:5])
        print('tsv', len(rows))
    elif cmd == 'batches':
        os.makedirs(sys.argv[2], exist_ok=True)
        ks = [r[1] for r in rows]
        for b in range(0, len(ks), 12):
            json.dump({"requests": [req(k) for k in ks[b:b + 12]]}, open(os.path.join(sys.argv[2], 'b%02d.json' % (b // 12 + 1)), 'w', encoding='utf8'), ensure_ascii=False)
        print('batches', (len(ks) + 11) // 12, 'keys', len(ks), 'chars', sum(len(text(k)) for k in ks))
