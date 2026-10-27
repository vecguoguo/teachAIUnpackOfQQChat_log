# -*- coding: utf-8 -*-
"""搜索 'app' '猫猫' '佩佩' '鱼鱼' 全部出现语境，核实身份对应"""
import json, datetime

d = json.load(open(r'C:\Users\20535\AppData\Local\Temp\opencode\qqtask\conv.json', encoding='utf8'))

def ts(t):
    return datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M')

def text_of(m):
    parts = []
    for e in m['els'] or []:
        if e['t'] == 'text':
            parts.append(e['text'])
        elif e['t'] == 'notice':
            parts.append('[通知]' + e['text'][:80])
    return ' '.join(parts)

for kw in ['app', '猫猫', '佩佩', '鱼鱼', '哥哥', '冷月']:
    print('======== 关键词: %r ========' % kw)
    n = 0
    for m in d:
        t = text_of(m)
        if kw in t and m['type'] in (2, 17, 5):
            who = '我' if m['self'] else '对方'
            print('%s %s: %s' % (ts(m['time']), who, t[:140]))
            n += 1
            if n >= 25:
                print('  ...(共出现≥25次)')
                break
    print()
