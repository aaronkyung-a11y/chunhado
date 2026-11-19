#!/usr/bin/env python3
"""v0.7 초상 보강 순서: 유명한 인물 먼저. usage: por7_plan.py <묶음 번호…>  → 묶음마다 'index|job|F|scene' 줄(프롬프트는 tools/por7_prompt.py 의 머리말+장면+맺음말)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import por7_prompt as P
DONE0 = ['lubu', 'diaochan', 'guanyu', 'caocao', 'liubei', 'jiaxu', 'dongzhao', 'yuanshao', 'zhangliao', 'xunyu', 'zhugeliang', 'zhurong', 'lulingqi', 'sunquan']
T1 = '''zhangfei zhaoyun sunce zhouyu xiahoudun xiahouyuan xuchu dianwei guojia chengong gaoshun taishici
huangzhong machao ganning lumeng luxun simayi pangtong weiyan jiangwei huanggai zhoutai lusu
yuanshu gongsunzan mateng liubiao liuzhang taoqian kongrong zhanglu lijue gongsundu zhangyang liuyao
yanbaihu wanglang xuhuang zhanghe yuejin yujin caoren wenchou anliang pangde madai menghuo
huatuo zuoci yuji caopi caohong caozhang lidian chengyu xunyou guosi zhangxiu jiling'''.split()
import re
gen = sorted(k for k in P.order if re.match(r'^g[cfm]\d$', k))
rest = sorted(k for k in P.order if k not in DONE0 and k not in T1 and k not in gen)
ORDER = T1 + rest + gen
assert len(set(ORDER)) == len(ORDER) and len(ORDER) + len(DONE0) == len(P.order), (len(ORDER), len(DONE0), len(P.order), [k for k in P.order if k not in ORDER and k not in DONE0], [k for k in ORDER if k not in P.order])
if __name__ == '__main__':
    if sys.argv[1] == 'n': print(len(ORDER), 'keys →', (len(ORDER) + 11) // 12, 'batches'); sys.exit()
    for b in sys.argv[1:]:
        b = int(b); ks = ORDER[(b - 2) * 12:(b - 1) * 12]          # 묶음 1은 시험 묶음(DONE0 의 뒤 12명)
        print('# batch', b, ' '.join(ks))
        for k in ks: print('%d|%s|%s|%s' % (P.order[k], P.ids[k], 'F' if k in P.fem else '', P.sc[k]))
