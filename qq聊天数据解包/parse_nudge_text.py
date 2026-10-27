# -*- coding: utf-8 -*-
"""解析戳一戳完整文本：按 uin 分发起者，统计各自动作说辞"""
import json, re, collections

d = json.load(open(r'C:\Users\20535\AppData\Local\Temp\opencode\qqtask\conv.json', encoding='utf8'))

SELF_UID = 'u_41g4HcqHTQvouw6T6qhh2g'
PEER_UID = 'u_VjGLU3TISJx5yA4_aT7mSQ'

def text_of(m):
    parts = []
    for e in m['els'] or []:
        if e['t'] == 'text':
            parts.append(e['text'])
        elif e['t'] == 'notice':
            parts.append(e['text'])
    return ' '.join(parts)

# 提取 gtip 文本中的关键片段：动作 + 说辞
pat = re.compile(r'<nor txt="([^"]*)"|<qq uin="([^"]+)"')

by_initiator = {'猫猫': collections.Counter(), 'app': collections.Counter()}
by_action = {'猫猫': collections.Counter(), 'app': collections.Counter()}

for m in d:
    t = text_of(m)
    if not any(a in t for a in ['捏了捏', '亲了亲', '揉了揉']):
        continue
    m1 = re.search(r'<qq uin="([^"]+)"', t)
    if not m1:
        continue
    uid = m1.group(1)
    init = '猫猫' if uid == SELF_UID else ('app' if uid == PEER_UID else None)
    if not init:
        continue
    for a in ['捏了捏', '亲了亲', '揉了揉']:
        if a in t:
            by_action[init][a] += 1
    # 提取说辞：<nor txt="...">
    says = re.findall(r'<nor txt="([^"]*)"', t)
    for s in says:
        s2 = s.strip()
        if s2 and len(s2) <= 20:
            by_initiator[init][s2] += 1

print('=== 发起者 x 动作 ===')
for who in ['猫猫', 'app']:
    print(who, dict(by_action[who]))

print()
print('=== 发起者 x 说辞 TOP12 ===')
for who in ['猫猫', 'app']:
    print('--', who)
    for s, c in by_initiator[who].most_common(12):
        print('   %r: %d' % (s, c))
