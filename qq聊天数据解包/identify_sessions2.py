# -*- coding: utf-8 -*-
"""c2c_msg_table 会话分布（用 protobuf 数字字段名）"""
import sqlite3

DB = r'C:\Users\20535\AppData\Local\Temp\opencode\dec_out\nt_msg_plain2.db'
con = sqlite3.connect(DB)

print('=== c2c_msg_table 按对端 QQ号(40030) 分组 ===')
try:
    for r in con.execute('SELECT "40030", COUNT(*), MIN("40050"), MAX("40050") FROM c2c_msg_table GROUP BY "40030" ORDER BY COUNT(*) DESC'):
        print('  对端QQ=%s 条数=%s 时间=[%s, %s]' % r)
except Exception as e:
    print(' err', e)

print()
print('=== c2c_msg_table 按对端UID(40021) 分组 top20 ===')
try:
    for r in con.execute('SELECT "40021", COUNT(*), MIN("40050"), MAX("40050") FROM c2c_msg_table GROUP BY "40021" ORDER BY COUNT(*) DESC LIMIT 20'):
        print('  对端UID=%s 条数=%s 时间=[%s, %s]' % r)
except Exception as e:
    print(' err', e)

print()
print('=== msgType 分布 ===')
try:
    for r in con.execute('SELECT "40011", "40012", COUNT(*) FROM c2c_msg_table GROUP BY "40011","40012" ORDER BY COUNT(*) DESC LIMIT 20'):
        print('  40011=%s 40012=%s 条数=%s' % r)
except Exception as e:
    print(' err', e)

con.close()
