# -*- coding: utf-8 -*-
"""统计 + 抽样阅读聊天内容，寻找身份线索"""
import json, random, datetime

d = json.load(open(r'C:\Users\20535\AppData\Local\Temp\opencode\qqtask\conv.json', encoding='utf8'))
print('总条数:', len(d))

from collections import Counter
sc = Counter(m['self'] for m in d)
tc = Counter()
for m in d:
    for e in m['els'] or []:
        tc[e['t']] += 1
print('发送者分布:', dict(sc))
print('元素类型:', dict(tc))
print('消息类型分布:', Counter(m['type'] for m in d))

def ts(t):
    return datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M')

def text_of(m):
    parts = []
    for e in m['els'] or []:
        if e['t'] == 'text':
            parts.append(e['text'])
        elif e['t'] == 'notice':
            parts.append('[通知]' + e['text'][:60])
        elif e['t'] == 'quote':
            parts.append('[引]' + (e['text'] or '')[:40])
        elif e['t'] in ('image',):
            parts.append('[图]')
        elif e['t'] == 'voice':
            parts.append('[语音]' + e['text'])
        elif e['t'] == 'emoji':
            parts.append('[表情]' + e['text'])
    return ' '.join(parts)

print()
print('=== 最早 40 条 ===')
for m in d[:40]:
    who = '我' if m['self'] else '对方'
    print('%s %s %s: %s' % (ts(m['time']), who, m['type'], text_of(m)[:120]))

print()
print('=== 随机 60 条（分散抽样）===')
random.seed(42)
for m in random.sample(d, 60):
    who = '我' if m['self'] else '对方'
    print('%s %s %s: %s' % (ts(m['time']), who, m['type'], text_of(m)[:120]))
