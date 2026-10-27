# -*- coding: utf-8 -*-
"""最终特征：敷衍模式、首尾频率、语料示例"""
import json, re, collections, datetime

d = json.load(open(r'C:\Users\20535\AppData\Local\Temp\opencode\qqtask\conv.json', encoding='utf8'))

def text_of(m):
    parts = []
    for e in m['els'] or []:
        if e['t'] == 'text':
            parts.append(e['text'])
    return ' '.join(parts)

def ts(t):
    return datetime.datetime.fromtimestamp(t).strftime('%m-%d %H:%M')

# 1) 敷衍/单字回复统计
print('=== 单字/敷衍回复 ===')
for who, msgs, label in [('self', [m for m in d if m['self']], '猫猫'), ('peer', [m for m in d if not m['self']], 'app')]:
    texts = [text_of(m).strip() for m in msgs if text_of(m).strip()]
    one = collections.Counter()
    for t in texts:
        if t in ('嗯','哦','啊','哈','嗯嗯','好','好的','哈哈','哈哈哈','ok','OK','行','嗯哼','哦哦','嗯呐','好叭','好哦','呜呜','乖','棒'):
            one[t] += 1
    print(' %s 敷衍单字 TOP: %s' % (label, dict(one.most_common(12))))

# 2) 开场/结束语统计（早安/晚安/早/晚安）
print()
print('=== 早晚问候 ===')
for who, msgs, label in [('self', [m for m in d if m['self']], '猫猫'), ('peer', [m for m in d if not m['self']], 'app')]:
    c = collections.Counter()
    for m in msgs:
        t = text_of(m).strip()
        if re.match(r'^(早|早安|早上好|早啊|早呀|早好|早！|早哇)', t):
            c['早安类'] += 1
        if re.match(r'^(晚安|晚|安|睡了|睡觉|睡觉了|晚安！|晚安~|晚安～)', t) or '晚安' in t[:6]:
            c['晚安类'] += 1
    print(' %s: %s' % (label, dict(c)))

# 3) 语料示例样本（双方各 20 条 2-15 字短句 + 8 条中长句）
print()
print('=== 猫猫 短句样本 25 条 ===')
n = 0
for m in d:
    if m['self']:
        t = text_of(m).strip()
        if 2 <= len(t) <= 15 and not t.startswith('[图]'):
            print('  [%s] %s' % (ts(m['time']), t))
            n += 1
            if n >= 25:
                break
print()
print('=== app 短句样本 25 条 ===')
n = 0
for m in d:
    if not m['self']:
        t = text_of(m).strip()
        if 2 <= len(t) <= 15 and not t.startswith('[图]'):
            print('  [%s] %s' % (ts(m['time']), t))
            n += 1
            if n >= 25:
                break

# 4) 双方对"游戏开黑"邀请的反应（配对样本）
print()
print('=== 游戏开黑配对（猫猫请求 -> app回应）===')
kws = ['带', '上号', '玩', '联机', '一起']
pairs = []
for i, m in enumerate(d):
    if m['self'] and m['type'] == 2:
        t = text_of(m)
        if any(k in t for k in ['带我', '带我玩', '上号', '来玩']):
            # 找后续 app 回应（60 秒内）
            for j in range(i+1, min(i+6, len(d))):
                cm = d[j]
                if not cm['self'] and cm['type'] == 2 and cm['time'] - m['time'] < 120:
                    pairs.append((t[:40], text_of(cm)[:40]))
                    break
for p in pairs[:10]:
    print('  猫猫: %s\n  app : %s' % p)

# 5) 双方被调侃反应样本
print()
print('=== 调侃互动配对 ===')
kws2 = ['笨蛋', '傻', '猪', '笨笨', '可爱', '主人']
n = 0
for i, m in enumerate(d):
    if m['type'] == 2:
        t = text_of(m)
        if any(k in t for k in kws2) and len(t) <= 30:
            who = '猫猫' if m['self'] else 'app'
            print('  [%s %s] %s' % (ts(m['time']), who, t[:50]))
            n += 1
            if n >= 20:
                break
