# -*- coding: utf-8 -*-
"""查询目标会话 u_VjGLU3TISJx5yA4_aT7mSQ 的名称字段"""
import sqlite3

DB = r'C:\Users\20535\AppData\Local\Temp\opencode\dec_out\nt_msg_plain2.db'
con = sqlite3.connect(DB)

for uid in ['u_VjGLU3TISJx5yA4_aT7mSQ', 'u_wVWSNGKXKwJKPsRTyNs3Hg']:
    print('=== UID %s ===' % uid)
    rows = con.execute('SELECT * FROM recent_contact_v3_table WHERE "40021"=?', (uid,)).fetchall()
    print(' 匹配行数:', len(rows))
    for r in rows:
        d = dict(zip([x[1] for x in con.execute('PRAGMA table_info(recent_contact_v3_table)')], r))
        for k in ['40055','40010','40027','40021','40030','40041','40056','40050','40003','40094','40093','40090','40095','40096','40001','41103','41104','40020','40033','41220','40600','40011','41114','49102','49103']:
            v = d.get(k)
            if isinstance(v, bytes):
                v = v.hex()[:80]
            print('  %s = %r' % (k, v))
    print()
con.close()
