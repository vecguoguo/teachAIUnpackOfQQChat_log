# -*- coding: utf-8 -*-
"""补充：emoji/颜文字、戳一戳、情绪场景、深夜活跃"""
import json, re, collections, datetime

d = json.load(open(r'C:\Users\20535\AppData\Local\Temp\opencode\qqtask\conv.json', encoding='utf8'))

def text_of(m):
    parts = []
    for e in m['els'] or []:
        if e['t'] == 'text':
            parts.append(e['text'])
        elif e['t'] == 'emoji':
            parts.append('[E:' + e['text'] + ']')
        elif e['t'] == 'notice':
            parts.append(e['text'])
    return ' '.join(parts)

# 1) 颜文字/表情符号（非 emoji 元素，文本里的）
for who, msgs, label in [('self', [m for m in d if m['self']], '猫猫(我)'), ('peer', [m for m in d if not m['self']], 'app(对方)')]:
    allt = ''.join(text_of(m) for m in msgs)
    print('== %s 颜文字/符号 ==' % label)
    pats = {'(*^▽^*)':0, '(≧▽≦)':0, '(〃＞皿＜)':0, '≡ω≡':0, 'QAQ':0, 'o(≧口≦)o':0, '>_<':0, '~':0, '～':0, '🐱':0, '🐈':0, '😅':0, '🥺':0, '❤':0, '💕':0, '✨':0, '🥹':0, '🙄':0, '😭':0, '😤':0, '🥰':0}
    for p in pats:
        pats[p] = allt.count(p)
    print(' ', {k:v for k,v in pats.items() if v})

# 2) emoji 元素消息
for who, msgs, label in [('self', [m for m in d if m['self']], '猫猫(我)'), ('peer', [m for m in d if not m['self']], 'app(对方)')]:
    em = collections.Counter()
    for m in msgs:
        for e in m['els'] or []:
            if e['t'] == 'emoji':
                em[e['text']] += 1
    print('== %s emoji 元素 TOP10 ==' % label, em.most_common(10))

# 3) 戳一戳动作（notice 中 "捏了捏"/"亲了亲"）发送方分布
print()
for action in ['捏了捏', '亲了亲', '拍了拍', '戳了戳', '点了点', '蹭了蹭', '揉了揉']:
    cnt = {'self': 0, 'peer': 0}
    for m in d:
        t = text_of(m)
        if action in t:
            cnt['self' if m['self'] else 'peer'] += 1
    print('动作 %s: 猫猫发起 %d, app发起 %d' % (action, cnt['self'], cnt['peer']))

# 4) 情绪场景抽样
print()
print('=== 负面/冲突场景抽样 ===')
kws = ['对不起', '生气', '烦', '哭', 'emo', '难受', '讨厌', '不理', '分手', '删', '拉黑', '委屈', '难过', '伤心', '冷战', '吵架', '吵']
hits = []
for m in d:
    t = text_of(m)
    if any(k in t for k in kws) and m['type'] in (2, 17):
        hits.append((m['time'], m['self'], t))
hits.sort()

def ts2(t):
    return datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M')

print('含负面词消息数:', len(hits))
n = 0
for t, self, txt in hits:
    if len(txt) < 200:
        print('[%s %s] %s' % (ts2(t), '我' if self else '对方', txt[:150]))
        n += 1
        if n >= 40:
            break

# 5) 深夜活跃（0-6点）
print()
for who, msgs, label in [('self', [m for m in d if m['self']], '猫猫(我)'), ('peer', [m for m in d if not m['self']], 'app(对方)')]:
    night = sum(1 for m in msgs if 0 <= datetime.datetime.fromtimestamp(m['time']).hour < 6)
    print('%s 深夜(0-6点)消息: %d (%.1f%%)' % (label, night, 100*night/len(msgs)))
