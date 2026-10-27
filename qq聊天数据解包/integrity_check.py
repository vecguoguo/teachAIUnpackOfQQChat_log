# -*- coding: utf-8 -*-
"""完整完整性检查 + 逐块定位 c2c 表损坏位置"""
import sqlite3, sys

DB = r'C:\Users\20535\AppData\Local\Temp\opencode\dec_out\nt_msg_plain3.db'
con = sqlite3.connect(DB)

print('=== PRAGMA integrity_check（完整，较慢）===')
rows = con.execute('PRAGMA integrity_check').fetchall()
errs = [r[0] for r in rows if not r[0].startswith('ok')]
print('总结果数:', len(rows), ' 错误行数:', len(errs))
from collections import Counter
c = Counter()
for e in errs[:2000]:
    print(' ', e[:120])
print('...共', len(errs), '条错误')
con.close()
