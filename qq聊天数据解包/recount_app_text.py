# -*- coding: utf-8 -*-
"""重算 app 纯文本特征（排除 gtip 通知），及猫猫真实高频词复核"""
import json, re, collections

d = json.load(open(r'C:\Users\20535\AppData\Local\Temp\opencode\qqtask\conv.json', encoding='utf8'))

def text_of(m):
    parts = []
    for e in m['els'] or []:
        if e['t'] == 'text':
            parts.append(e['text'])
        elif e['t'] == 'notice':
            parts.append(e['text'])
    return ' '.join(parts)

def is_notice(t):
    return '<gtip' in t or '<qq uin=' in t

# app 纯文本（排除通知）
app_texts = []
for m in d:
    if not m['self']:
        t = text_of(m).strip()
        if t and not is_notice(t):
            app_texts.append(t)

print('app 非通知文本消息数:', len(app_texts))
print('app 非通知总字数:', sum(len(t) for t in app_texts))

allt = ' '.join(app_texts)
toks = re.findall(r'[\u4e00-\u9fff]{2,}', allt)
cnt = collections.Counter(toks)
stop = {'我们','你们','他们','什么','怎么','这个','那个','一个','没有','自己','就是','还是','知道','可以','不是','不会','这么','那么','真的','时候','现在','这样','那样','因为','所以','但是','如果','然后','而且','一直','已经','还有','那个','是不是','哈哈哈','哈哈哈哈','哈哈','在吗','嗯嗯','好的','好吧','没事','今天','明天','昨天','一下','一起','就是','的话','感觉','觉得','人家'}
print()
print('=== app 纯文本高频词 TOP25 ===')
for w, c in cnt.most_common():
    if len(w) >= 2 and w not in stop and c >= 5:
        print('  %s: %d' % (w, c))
        if sum(1 for _ in [0]) > 0:
            pass
    if sum(1 for ww, cc in cnt.most_common() if len(ww)>=2 and ww not in stop and cc>=5) >= 30:
        pass
# 简单实现 top30
res = [(w, c) for w, c in cnt.most_common() if len(w) >= 2 and w not in stop and c >= 5]
print('（合计候选词数:', len(res), '）')

print()
print('=== app 纯文本语气词 ===')
for pat, label in [('哦','哦'), ('吧','吧'), ('啊','啊'), ('呢','呢'), ('嘛','嘛'), ('呀','呀'), ('～','～'), ('~','~'), ('呜呜','呜呜'), ('嘿嘿','嘿嘿'), ('QAQ','QAQ'), ('哥哥','哥哥'), ('晚安','晚安'), ('早安','早安'), ('早','早'), ('怎么了','怎么了'), ('对不起','对不起'), ('抱抱','抱抱'), ('贴贴','贴贴'), ('亲亲','亲亲'), ('想你了','想你了'), ('想你','想你'), ('爱你','爱你'), ('我爱你','我爱你'), ('你在','你在'), ('我在','我在'), ('在的','在的'), ('嗯','嗯'), ('好','好'), ('ok','ok')]:
    c = allt.count(pat)
    if c:
        print('  %s: %d' % (label, c))

print()
print('=== app 纯文本感叹号/问号/句号 ===')
print('  ！:', allt.count('！'), ' ？:', allt.count('？'), ' 。:', allt.count('。'), ' ，:', allt.count('，'), ' ～:', allt.count('～') + allt.count('~'))

print()
print('=== 猫猫真实文本高频词复核（排除通知） ===')
self_texts = []
for m in d:
    if m['self']:
        t = text_of(m).strip()
        if t and not is_notice(t):
            self_texts.append(t)
allt2 = ' '.join(self_texts)
toks2 = re.findall(r'[\u4e00-\u9fff]{2,}', allt2)
cnt2 = collections.Counter(toks2)
res2 = [(w, c) for w, c in cnt2.most_common() if len(w) >= 2 and w not in stop and c >= 5]
print('猫猫非通知文本消息数:', len(self_texts))
for w, c in res2[:20]:
    print('  %s: %d' % (w, c))
