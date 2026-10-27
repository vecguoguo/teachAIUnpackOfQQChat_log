# -*- coding: utf-8 -*-
"""用本机 nt_msg.db 密钥验证修复后的解密重组逻辑"""
import sys, os, time, sqlite3
sys.path.insert(0, r'C:\Users\20535\AppData\Local\Temp\opencode')
from qqdec import decrypt_db

KEY = bytes.fromhex('<数据库密钥，从临时目录 keys.txt 读取，勿外传>')
SRC = r'C:\Users\20535\Documents\Tencent Files\2053554689\nt_qq\nt_db\nt_msg.db'
DST = r'C:\Users\20535\AppData\Local\Temp\opencode\dec_out\nt_msg_plain2.db'

t0 = time.time()
ok = decrypt_db(SRC, DST, KEY)
print('decrypt_db ok=%s 用时=%.1fs 输出大小=%d' % (ok, time.time()-t0, os.path.getsize(DST)))

try:
    con = sqlite3.connect(DST)
    cur = con.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur]
    print('tables:', tables)
    for t in tables:
        try:
            n = con.execute('SELECT COUNT(*) FROM "%s"' % t).fetchone()[0]
            print('  %s rows=%d' % (t, n))
        except Exception as e:
            print('  %s count err: %s' % (t, e))
    con.close()
except Exception as e:
    print('SQLite open FAILED:', e)
