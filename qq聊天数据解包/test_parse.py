# -*- coding: utf-8 -*-
"""测试解析 c2c_msg_table 中目标会话的消息正文（protobuf 40800）"""
import sys, sqlite3
sys.path.insert(0, r'C:\Users\20535\AppData\Local\Temp\opencode\QQNT_Export')
import element_pb2

DB = r'C:\Users\20535\AppData\Local\Temp\opencode\dec_out\nt_msg_plain2.db'
TARGET = 'u_VjGLU3TISJx5yA4_aT7mSQ'

con = sqlite3.connect(DB)
rows = con.execute(
    'SELECT "40001","40020","40011","40012","40050","40800" FROM c2c_msg_table '
    'WHERE "40021"=? ORDER BY "40050" LIMIT 15', (TARGET,)).fetchall()

for r in rows:
    mid, sender, mt, smt, ts, body = r
    els = element_pb2.Elements()
    try:
        els.ParseFromString(bytes(body))
        parts = []
        for e in els.elements:
            if e.type == 1 and e.text:
                parts.append('TXT:' + e.text)
            elif e.type == 2:
                parts.append('[图片]')
            elif e.type == 4:
                parts.append('[语音]' + (('('+e.voiceText+')') if e.voiceText else ''))
            elif e.type == 6:
                parts.append('[表情]' + (e.emojiText or str(e.emojiId)))
            elif e.type == 7:
                parts.append('[引用]')
            elif e.type == 8:
                parts.append('[提示]' + e.noticeInfo)
            else:
                parts.append('[类型%d]' % e.type)
        print('%s mt=%s/%s ts=%s | %s' % (mid, mt, smt, ts, ' || '.join(parts)))
    except Exception as e:
        print('%s mt=%s/%s ts=%s | PARSE ERR %s | body=%s' % (mid, mt, smt, ts, e, bytes(body)[:40].hex()))
con.close()
