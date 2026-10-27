# -*- coding: utf-8 -*-
"""按通知文本中的 <qq uin> 精确统计戳一戳发起者"""
import json, re, collections, datetime

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

# 所有含动作词的 notice 消息
actions = ['捏了捏', '亲了亲', '揉了揉', '拍了拍', '戳了戳', '蹭了蹭']
total = collections.Counter()
by_msg_self = collections.Counter()
by_uin = collections.Counter()
unparsed = 0
samples = []

for m in d:
    t = text_of(m)
    hit = [a for a in actions if a in t]
    if not hit:
        continue
    act = hit[0]
    total[act] += 1
    by_msg_self['self' if m['self'] else 'peer'] += 1
    # 解析 uin：第一个 <qq uin="..." 是发起者
    m1 = re.search(r'<qq uin="([^"]+)"', t)
    if m1:
        uid = m1.group(1)
        if uid == SELF_UID:
            by_uin['猫猫发起'] += 1
        elif uid == PEER_UID:
            by_uin['app发起'] += 1
        else:
            by_uin['其他:%s' % uid[:12]] += 1
    else:
        unparsed += 1
    if len(samples) < 15 and ('捏了捏' in t or '亲了亲' in t):
        samples.append((m['time'], m['self'], act, t[:150]))

print('动作通知总数(按消息归属 self/peer):', dict(by_msg_self))
print('动作通知总数(按 uin 发起者):', dict(by_uin))
print('未解析 uin:', unparsed)
print()
for act in actions:
    c = collections.Counter()
    for m in d:
        t = text_of(m)
        if act in t:
            m1 = re.search(r'<qq uin="([^"]+)"', t)
            if m1:
                uid = m1.group(1)
                c['猫猫发起' if uid == SELF_UID else ('app发起' if uid == PEER_UID else '其他')] += 1
            else:
                c['未解析'] += 1
    print('%-4s: %s' % (act, dict(c)))

print()
print('=== 样本（时间 / 消息归属 / 动作 / 文本）===')
for t, self, act, txt in samples:
    dt = datetime.datetime.fromtimestamp(t).strftime('%m-%d %H:%M')
    print('[%s 归属=%s] %s: %s' % (dt, 'self' if self else 'peer', act, txt))
