# -*- coding: utf-8 -*-
"""深入：长消息样本、每日首尾句、回复节奏、话题关键词"""
import json, re, collections, datetime

d = json.load(open(r'C:\Users\20535\AppData\Local\Temp\opencode\qqtask\conv.json', encoding='utf8'))

def text_of(m):
    parts = []
    for e in m['els'] or []:
        if e['t'] == 'text':
            parts.append(e['text'])
        elif e['t'] == 'notice':
            parts.append('[通知]')
    return ' '.join(parts)

def ts(t):
    return datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M')

print('=== 对方(app) 的 50+ 字长消息样本 12 条 ===')
n = 0
for m in d:
    if not m['self']:
        t = text_of(m)
        if len(t) >= 50:
            who = '对方'
            print('[%s] %s: %s' % (ts(m['time']), who, t[:200]))
            n += 1
            if n >= 12:
                break

print()
print('=== 猫猫(我) 的 50+ 字长消息样本 8 条 ===')
n = 0
for m in d:
    if m['self']:
        t = text_of(m)
        if len(t) >= 50:
            print('[%s] 我: %s' % (ts(m['time']), t[:200]))
            n += 1
            if n >= 8:
                break

print()
print('=== 每日首条/末条消息（抽样 8 天）===')
days = collections.OrderedDict()
for m in d:
    day = datetime.datetime.fromtimestamp(m['time']).strftime('%Y-%m-%d')
    days.setdefault(day, []).append(m)
for day in list(days.keys())[:8]:
    ms = days[day]
    first, last = ms[0], ms[-1]
    print('%s 首[%s %s]: %s' % (day, ts(first['time']), '我' if first['self'] else '对方', text_of(first)[:60]))
    print('   末[%s %s]: %s' % (ts(last['time']), '我' if last['self'] else '对方', text_of(last)[:60]))

print()
print('=== 回复间隔统计（交替发言的平均等待秒数）===')
# 简化：连续消息中，前一条是对方、后一条是我（或反之），时间差
import statistics
for target in ['self', 'peer']:
    gaps = []
    prev = None
    for m in d:
        if prev is not None and m['self'] != prev['self']:
            g = m['time'] - prev['time']
            if 0 <= g <= 3600:
                gaps.append(g)
        prev = m
    print(' 切换到%s: 样本%d, 中位数%.0f秒, 平均%.1f秒, <60秒占比%.1f%%' % (
        target, len(gaps), statistics.median(gaps), statistics.mean(gaps),
        100*sum(1 for g in gaps if g<60)/len(gaps)))

print()
print('=== 话题关键词（游戏/动漫/其他）===')
allt = ' '.join(text_of(m) for m in d)
for kw in ['崩铁','原神','泰拉瑞亚','我的世界','MC','金铲铲','王者','星铁','明日方舟','崩坏','绝区零','塞尔达','CS','永劫','蛋仔','第五人格','光遇','三角洲','鸣潮','喵','猫','鱼鱼','吃饭','睡觉','上班','上学','作业','考试','工作','快递','外卖','皮肤','抽卡','打本','联机','熬夜','洗澡','感冒','医院']:
    c = allt.count(kw)
    if c:
        print('  %s: %d' % (kw, c))
