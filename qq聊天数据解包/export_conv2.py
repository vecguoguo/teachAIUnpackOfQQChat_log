# -*- coding: utf-8 -*-
"""稳健导出目标会话：按主键分块，跳过损坏行，统计缺失"""
import sys, sqlite3, json, collections
sys.path.insert(0, r'C:\Users\20535\AppData\Local\Temp\opencode\QQNT_Export')
import element_pb2

DB = r'C:\Users\20535\AppData\Local\Temp\opencode\dec_out\nt_msg_plain3.db'
TARGET = 'u_VjGLU3TISJx5yA4_aT7mSQ'
SELF_UID = 'u_41g4HcqHTQvouw6T6qhh2g'
OUT = r'C:\Users\20535\AppData\Local\Temp\opencode\qqtask\conv.json'

con = sqlite3.connect(DB)

# 收集全部主键
ids = [r[0] for r in con.execute('SELECT "40001" FROM c2c_msg_table WHERE "40021"=? ORDER BY "40001"', (TARGET,)).fetchall()]
print('目标会话主键总数:', len(ids))

def parse_elements(body):
    els = element_pb2.Elements()
    try:
        els.ParseFromString(bytes(body))
    except Exception:
        return None
    out = []
    for e in els.elements:
        t = e.type
        if t == 1 and e.text:
            out.append({'t': 'text', 'text': e.text})
        elif t == 2:
            out.append({'t': 'image'})
        elif t == 4:
            out.append({'t': 'voice', 'text': e.voiceText or ''})
        elif t == 6:
            out.append({'t': 'emoji', 'text': e.emojiText or str(e.emojiId)})
        elif t == 7:
            out.append({'t': 'quote', 'text': (e.quotedElement.text if e.quotedElement else '')})
        elif t == 8:
            out.append({'t': 'notice', 'text': e.noticeInfo or ''})
        elif t == 3:
            out.append({'t': 'file', 'text': e.fileName or ''})
        elif t == 5:
            out.append({'t': 'video'})
        elif t == 9:
            out.append({'t': 'redpacket', 'text': (e.redPacket.greeting or '')})
        elif t == 10:
            out.append({'t': 'app', 'text': e.applicationMessage or ''})
        elif t == 21:
            out.append({'t': 'call', 'text': e.callText or ''})
        elif t == 26:
            out.append({'t': 'feed', 'text': (e.feedTitle.text if e.feedTitle else '')})
        else:
            out.append({'t': 'type%d' % t})
    return out

msgs = []
stat = collections.Counter()
sender_stat = collections.Counter()
bad_rows = 0
# 每 200 个主键一批读取
for i in range(0, len(ids), 200):
    batch = ids[i:i+200]
    q = ('SELECT "40001","40020","40030","40011","40012","40050","40800" FROM c2c_msg_table '
         'WHERE "40001" IN (%s)' % ','.join('?' * len(batch)))
    try:
        rows = con.execute(q, batch).fetchall()
        byid = {r[0]: r for r in rows}
    except Exception:
        # 逐行读取，跳过坏行
        rows = []
        for mid in batch:
            try:
                r = con.execute('SELECT "40001","40020","40030","40011","40012","40050","40800" FROM c2c_msg_table WHERE "40001"=?', (mid,)).fetchone()
                if r:
                    rows.append(r)
            except Exception:
                bad_rows += 1
        byid = {r[0]: r for r in rows}
    for mid in batch:
        r = byid.get(mid)
        if not r:
            bad_rows += 1
            continue
        _, sender, sender_num, mt, smt, ts, body = r
        parsed = parse_elements(body)
        is_self = (sender == SELF_UID)
        sender_stat['self' if is_self else 'peer'] += 1
        for p in parsed or []:
            stat[p['t']] += 1
        msgs.append({'id': mid, 'self': is_self, 'sender_num': sender_num,
                     'type': mt, 'sub': smt, 'time': ts, 'els': parsed})

msgs.sort(key=lambda m: m['time'])
with open(OUT, 'w', encoding='utf8') as f:
    json.dump(msgs, f, ensure_ascii=False)

print('成功导出:', len(msgs), ' 坏行跳过:', bad_rows)
print('发送者分布:', dict(sender_stat))
print('元素类型分布:', dict(stat))
print('时间范围:', msgs[0]['time'], '->', msgs[-1]['time'])
print('导出:', OUT)
con.close()
