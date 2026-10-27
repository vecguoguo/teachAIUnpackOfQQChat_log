# -*- coding: utf-8 -*-
"""场景抽样：撒娇、求助、游戏、日常、贴贴回应"""
import json, datetime, random

d = json.load(open(r'C:\Users\20535\AppData\Local\Temp\opencode\qqtask\conv.json', encoding='utf8'))

def text_of(m):
    parts = []
    for e in m['els'] or []:
        if e['t'] == 'text':
            parts.append(e['text'])
        elif e['t'] == 'notice':
            parts.append(e['text'][:40])
        elif e['t'] == 'quote':
            parts.append('[引]' + (e['text'] or '')[:30])
        elif e['t'] == 'image':
            parts.append('[图]')
        elif e['t'] == 'voice':
            parts.append('[语音]' + e['text'][:20])
    return ' '.join(parts)

def ts(t):
    return datetime.datetime.fromtimestamp(t).strftime('%m-%d %H:%M')

# 1) 游戏开黑场景（三角洲/泰拉瑞亚/原神 附近上下文）
print('=== 游戏场景（含游戏词的消息及前后文）===')
game_kw = ['三角洲', '泰拉瑞亚', '原神', '崩铁', '我的世界', '联机', '开黑', '固排', '上号', '打本', '排位']
n = 0
for i, m in enumerate(d):
    t = text_of(m)
    if any(k in t for k in game_kw) and m['type'] == 2:
        ctx = d[max(0,i-1):i+3]
        for cm in ctx:
            print('[%s %s] %s' % (ts(cm['time']), '我' if cm['self'] else '对方', text_of(cm)[:80]))
        print('---')
        n += 1
        if n >= 8:
            break

# 2) app 撒娇/贴贴回应（对方消息中"哥哥/爱你/想你/抱抱"）
print()
print('=== app 撒娇/主动亲昵 ===')
n = 0
for m in d:
    if not m['self'] and m['type'] == 2:
        t = text_of(m)
        if any(k in t for k in ['哥哥', '想你', '爱你', '抱抱', '要抱', '亲亲', '贴贴', '哄', '陪我']):
            print('[%s 对方] %s' % (ts(m['time']), t[:90]))
            n += 1
            if n >= 25:
                break

# 3) 猫猫回应/关心（"在干嘛/吃饭/睡觉/晚安"）
print()
print('=== 猫猫 关心日常 ===')
n = 0
for m in d:
    if m['self'] and m['type'] == 2:
        t = text_of(m)
        if any(k in t for k in ['在干嘛', '吃饭', '睡觉', '晚安', '醒了', '起床', '喝', '冷', '记得', '别熬']):
            print('[%s 我] %s' % (ts(m['time']), t[:90]))
            n += 1
            if n >= 25:
                break

# 4) 随机 30 条完整对话流（看互动节奏）
print()
print('=== 随机对话流 40 条 ===')
random.seed(7)
idx = sorted(random.sample(range(len(d)), 40))
for i in idx:
    m = d[i]
    print('[%s %s] %s' % (ts(m['time']), '我' if m['self'] else '对方', text_of(m)[:90]))
