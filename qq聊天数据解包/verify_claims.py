# -*- coding: utf-8 -*-
"""验证人设卡中的关键断言"""
import json, re

d = json.load(open(r'C:\Users\20535\AppData\Local\Temp\opencode\qqtask\conv.json', encoding='utf8'))

def text_of(m):
    parts = []
    for e in m['els'] or []:
        if e['t'] == 'text':
            parts.append(e['text'])
    return ' '.join(parts)

for who, msgs, label in [('self', [m for m in d if m['self']], '猫猫'), ('peer', [m for m in d if not m['self']], 'app')]:
    allt = ' '.join(text_of(m) for m in msgs)
    print('== %s ==' % label)
    for pat in ['操','草','靠','艹','妈的','傻逼','贱','滚','TMD','tm','脏话','尼玛','我日','去死','废物','蠢货']:
        c = allt.count(pat)
        if c: print('  粗口 %r: %d' % (pat, c))
    for pat in ['我爱你','爱你的','爱你','我爱你哦']:
        c = allt.count(pat)
        if c: print('  %r: %d' % (pat, c))
    for pat in ['哈哈哈哈哈','嘿嘿嘿嘿','哈哈哈哈','哈哈哈']:
        c = allt.count(pat)
        if c: print('  笑 %r: %d' % (pat, c))
    print()
