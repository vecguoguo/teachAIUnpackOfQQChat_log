# -*- coding: utf-8 -*-
"""从 recent_contact / 会话表识别 app 与 猫猫 的名称"""
import sqlite3

DB = r'C:\Users\20535\AppData\Local\Temp\opencode\dec_out\nt_msg_plain2.db'
con = sqlite3.connect(DB)

for t in ['recent_contact_v3_table', 'hidden_session_storage_table_v1', 'recent_contact_top_table', 'msg_unread_info_table']:
    print('=== %s ===' % t)
    try:
        cols = [d[1] for d in con.execute('PRAGMA table_info("%s")' % t)]
        print(' cols:', cols)
        for r in con.execute('SELECT * FROM "%s" LIMIT 300' % t):
            s = str(r)
            if len(s) > 400:
                s = s[:400] + '...'
            print(' ', s)
    except Exception as e:
        print(' err', e)
    print()

con.close()
