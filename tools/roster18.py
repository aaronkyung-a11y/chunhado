#!/usr/bin/env python3
"""v0.18 — 공용 초상(gm · gc)을 쓰던 이름난 무장 60명에게 제 초상을 준다. 이름 → 초상 키(art/raw18/<key>.png, 문구는 art/por18_scenes.tsv).
tools/make_roster.py 가 읽는다: 그림 파일이 있는 것만 잇는다(없으면 그대로 공용 초상). 능력치 · 소속 · 번호는 건드리지 않는다."""
PORTRAIT18 = {
  '조진': 'caozhen', '조휴': 'caoxiu', '하후상': 'xiahoushang', '하후패': 'xiahouba', '조식': 'caozhi', '주환': 'zhuhuan',
  '주연': 'zhuran', '정봉': 'dingfeng', '전종': 'quancong', '보즐': 'buzhi', '올돌골': 'wutugu', '목록대왕': 'mulu',
  '타사대왕': 'duosi', '망아장': 'mangyachang', '가비능': 'kebineng', '관색': 'guansuo', '주창': 'zhoucang', '교현': 'qiaoxuan',
  '진교': 'chenjiao', '최염': 'cuiyan', '이통': 'litong', '손익': 'sunyi', '관해': 'guanhai', '부동': 'futong',
  '양의': 'yangyi', '반준': 'panjun', '요화': 'liaohua', '손건': 'sunqian', '미방': 'mifang', '채모': 'caimao',
  '이회': 'lihui', '등지': 'dengzhi', '장억': 'zhangni', '가규': 'jiakui', '전예': 'tianyu', '견초': 'qianzhao',
  '여범': 'lvfan', '능조': 'lingcao', '주치': 'zhuzhi', '장제': 'zhangji2', '번조': 'fanchou', '곽도': 'guotu',
  '신평': 'xinping', '순우경': 'chunyuqiong', '고간': 'gaogan', '원상': 'yuanshang', '조순': 'caochun', '오의': 'wuyi',
  '오란': 'wulan', '냉포': 'lengbao', '마충': 'mazhong', '손분': 'sunben', '호진': 'huzhen', '무안국': 'wuanguo',
  '한호': 'hanhao', '염포': 'yanpu', '양봉': 'yangfeng', '공손강': 'gongsunkang', '장막': 'zhangmiao', '진도': 'chendao'
}
