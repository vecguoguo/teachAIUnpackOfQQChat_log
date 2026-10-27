# -*- coding: utf-8 -*-
"""全面语言统计：双方的消息、时间、长度、高频词、语气词、标点、表情"""
import json, re, collections, datetime

d = json.load(open(r'C:\Users\20535\AppData\Local\Temp\opencode\qqtask\conv.json', encoding='utf8'))

def text_of(m):
    parts = []
    for e in m['els'] or []:
        if e['t'] == 'text':
            parts.append(e['text'])
        elif e['t'] == 'notice':
            parts.append(e['text'])
    return ' '.join(parts)

self_msgs = [m for m in d if m['self']]
peer_msgs = [m for m in d if not m['self']]

def basics(name, msgs):
    txts = [text_of(m) for m in msgs]
    texts = [t for t in txts if t.strip()]
    chars = sum(len(t) for t in texts)
    print('== %s ==' % name)
    print(' 消息数: %d, 纯文本消息: %d, 总字数: %d' % (len(msgs), len(texts), chars))
    if texts:
        print(' 单条平均字数: %.1f, 中位数: %d, 最长: %d' % (chars/len(texts), sorted(len(t) for t in texts)[len(texts)//2], max(len(t) for t in texts)))
    # 时间分布
    hours = collections.Counter(datetime.datetime.fromtimestamp(m['time']).hour for m in msgs)
    top_h = hours.most_common(5)
    print(' 活跃小时 TOP5:', top_h)
    # 消息长度分布
    lens = [len(t) for t in texts]
    seg = collections.Counter()
    for l in lens:
        if l <= 5: seg['1-5字'] += 1
        elif l <= 10: seg['6-10字'] += 1
        elif l <= 20: seg['11-20字'] += 1
        elif l <= 50: seg['21-50字'] += 1
        else: seg['50+字'] += 1
    print(' 长度分布:', dict(seg))

basics('我(猫猫)', self_msgs)
basics('对方(app)', peer_msgs)

# 标点与语气词统计
def punct_stats(msgs, name):
    allt = ''.join(text_of(m) for m in msgs)
    print('== %s 标点/符号统计 ==' % name)
    for sym, label in [('。','句号'), ('！','感叹号'), ('？','问号'), ('…','省略号'), ('~','波浪线'), ('～','波浪线2'), ('，','逗号'), ('！','!'), ('~','~'), ('(', '括号'), ('\n','换行')]:
        c = allt.count(sym)
        if c:
            print('  %s(%s): %d' % (label, sym, c))

punct_stats(self_msgs, '我(猫猫)')
punct_stats(peer_msgs, '对方(app)')

# 高频词（分双方，去掉单字与停用词）
def top_words(msgs, name, n=30):
    allt = ' '.join(text_of(m) for m in msgs)
    # 中文分词简化：按字符 bigram + 常见双字词
    toks = re.findall(r'[\u4e00-\u9fff]{2,}', allt)
    cnt = collections.Counter(toks)
    stop = {'我们','你们','他们','什么','怎么','这个','那个','一个','没有','自己','就是','还是','知道','可以','不是','不会','这么','那么','真的','时候','现在','这样','那样','因为','所以','但是','如果','然后','而且','一直','已经','还有','那个','是不是','哈哈哈','哈哈哈哈','哈哈','在吗','嗯嗯','好的','好吧','没事','今天','明天','昨天','一下','一起'}
    common = [(w, c) for w, c in cnt.items() if w not in stop and len(w) >= 2 and c >= 5]
    common.sort(key=lambda x: -x[1])
    print('== %s 高频双字词 TOP%d ==' % (name, n))
    for w, c in common[:n]:
        print('  %s: %d' % (w, c))

top_words(self_msgs, '我(猫猫)')
top_words(peer_msgs, '对方(app)')

# 语气词/口头禅候选
def modal(msgs, name):
    allt = ''.join(text_of(m) for m in msgs)
    print('== %s 语气词/口头禅候选 ==' % name)
    for pat, label in [('啊','啊'), ('吧','吧'), ('呢','呢'), ('嘛','嘛'), ('哦','哦'), ('呀','呀'), ('哈','哈'), ('诶','诶'), ('哎','哎'), ('喔','喔'), ('么','么'), ('呗','呗'), ('QAQ','QAQ'), ('qaq','qaq'), ('www','www'), ('www','www'), ('呜呜','呜呜'), ('哈哈哈','哈哈哈'), ('草','草'), ('卧槽','卧槽'), ('艹','艹'), ('靠','靠'), ('淦','淦'), ('完了','完了'), ('绝了','绝了'), ('可以','可以'), ('无语','无语'), ('牛逼','牛逼'), ('牛','牛')]:
        c = allt.count(pat)
        if c:
            print('  %s: %d' % (label, c))

modal(self_msgs, '我(猫猫)')
modal(peer_msgs, '对方(app)')
