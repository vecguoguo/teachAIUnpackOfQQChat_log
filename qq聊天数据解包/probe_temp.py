# -*- coding: utf-8 -*-
"""探查 msgbackup 临时库的会话分布（只读，不解密消息体）"""
import sqlite3

DB = r'C:\Users\20535\AppData\Local\Temp\opencode\temp_3523605313_3.db'

con = sqlite3.connect(DB)
print('tables:', [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")])
print('msg cols:', [d[1] for d in con.execute('PRAGMA table_info(msg)')])
print('--- chatUin distribution ---')
for r in con.execute('SELECT chatUin, chatType, COUNT(*), MIN(msgTime), MAX(msgTime) FROM msg GROUP BY chatUin, chatType'):
    print(' chatUin=%s chatType=%s count=%s min=%s max=%s' % r)
print('--- ex_info ---')
for r in con.execute('SELECT * FROM ex_info'):
    print(' ', r)
con.close()
