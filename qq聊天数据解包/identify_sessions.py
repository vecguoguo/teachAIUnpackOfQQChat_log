# -*- coding: utf-8 -*-
"""识别本机库中的会话：msg_backup 信息 + c2c 会话分布 + UID 映射"""
import sqlite3

DB = r'C:\Users\20535\AppData\Local\Temp\opencode\dec_out\nt_msg_plain2.db'
con = sqlite3.connect(DB)

print('=== msg_backup_storage_table ===')
try:
    for r in con.execute('SELECT * FROM msg_backup_storage_table'):
        print(' ', str(r)[:500])
except Exception as e:
    print(' err', e)

print()
print('=== nt_uid_mapping_table（UID -> QQ号）全部 ===')
try:
    cols = [d[1] for d in con.execute('PRAGMA table_info(nt_uid_mapping_table)')]
    print(' cols:', cols)
    for r in con.execute('SELECT * FROM nt_uid_mapping_table'):
        print(' ', str(r)[:300])
except Exception as e:
    print(' err', e)

print()
print('=== c2c_msg_table 会话分布 top 60（UID, 消息数, 时间范围）===')
try:
    cols = [d[1] for d in con.execute('PRAGMA table_info(c2c_msg_table)')]
    print(' cols:', cols)
    q = ('SELECT "chat_uid", COUNT(*), MIN(msg_time), MAX(msg_time) FROM c2c_msg_table '
         'GROUP BY "chat_uid" ORDER BY COUNT(*) DESC')
    for r in con.execute(q):
        print(' ', r)
except Exception as e:
    print(' err', e)

con.close()
