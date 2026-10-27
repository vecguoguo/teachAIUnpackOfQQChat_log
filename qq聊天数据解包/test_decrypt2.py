# -*- coding: utf-8 -*-
"""重新解密 nt_msg.db（reserved=48 修复版），验证 quick_check 与完整性"""
import sys, os, time, sqlite3
sys.path.insert(0, r'C:\Users\20535\AppData\Local\Temp\opencode')
from qqdec import decrypt_db

KEY = bytes.fromhex('<数据库密钥，从临时目录 keys.txt 读取，勿外传>')
SRC = r'C:\Users\20535\Documents\Tencent Files\2053554689\nt_qq\nt_db\nt_msg.db'
DST = r'C:\Users\20535\AppData\Local\Temp\opencode\dec_out\nt_msg_plain3.db'

t0 = time.time()
ok = decrypt_db(SRC, DST, KEY)
print('decrypt ok=%s 用时=%.1fs 大小=%d' % (ok, time.time()-t0, os.path.getsize(DST)))

con = sqlite3.connect(DST)
qc = con.execute('PRAGMA quick_check').fetchall()
errs = [x[0] for x in qc if not x[0].startswith('ok')]
print('quick_check: %s | 错误数: %d' % (qc[0][0][:40], len(errs)))
for e in errs[:8]:
    print('  ', e[:100])
print('tables:', [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")])
con.close()
