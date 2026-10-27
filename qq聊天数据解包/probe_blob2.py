# -*- coding: utf-8 -*-
"""精确定位损坏：逐列测试 + 找坏行"""
import sqlite3, sys

DB = r'C:\Users\20535\AppData\Local\Temp\opencode\dec_out\nt_msg_plain3.db'
TARGET = 'u_VjGLU3TISJx5yA4_aT7mSQ'
con = sqlite3.connect(DB)

cols = ['40001','40002','40003','40010','40011','40012','40013','40020','40026','40021','40027','40040','40041','40050','40052','40090','40093','40800','40900','40105','40005','40058','40006','40100','40600','40060','40850','40851','40601','40801','40605','40030','40033','40062','40083','40084','40008','40009','40722']
for c in cols:
    try:
        n = con.execute('SELECT COUNT(*) FROM (SELECT "%s" FROM c2c_msg_table WHERE "40021"=?)' % c, (TARGET,)).fetchone()[0]
        print('%-7s OK %d' % (c, n))
    except Exception as e:
        print('%-7s FAIL %s' % (c, str(e)[:60]))

# 全字段 SELECT 定位坏行：按 40050 排序逐块读全字段
print()
print('=== 全字段分块读取 ===')
lo = 0
step = 500
bad = []
while True:
    try:
        rows = con.execute(
            'SELECT * FROM c2c_msg_table WHERE "40021"=? ORDER BY "40050" LIMIT ? OFFSET ?',
            (TARGET, step, lo)).fetchall()
    except Exception as e:
        bad.append((lo, str(e)[:80]))
        print('块 %d: FAIL %s' % (lo, str(e)[:80]))
        # 缩小步长重试
        try:
            rows = con.execute(
                'SELECT * FROM c2c_msg_table WHERE "40021"=? ORDER BY "40050" LIMIT 50 OFFSET ?',
                (TARGET, lo)).fetchall()
            print('  子块 50: OK %d 行' % len(rows))
            if len(rows) < 50:
                break
            lo += 50
            continue
        except Exception as e2:
            print('  子块 50: FAIL %s' % str(e2)[:80])
            break
    if not rows:
        break
    lo += len(rows)
    if lo % 2000 < step:
        print('进度: %d 行 OK' % lo)
    if lo > 42000:
        break
print('完成，坏块:', bad[:10])
con.close()
