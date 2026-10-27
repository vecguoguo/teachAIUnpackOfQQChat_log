# -*- coding: utf-8 -*-
"""专门测试 40900 列与全字段损坏点"""
import sqlite3, sys

DB = r'C:\Users\20535\AppData\Local\Temp\opencode\dec_out\nt_msg_plain3.db'
TARGET = 'u_VjGLU3TISJx5yA4_aT7mSQ'
con = sqlite3.connect(DB)

for c in ['40090','40093','40600','40800','40801','40605','40900']:
    try:
        n = con.execute('SELECT COUNT(*) FROM (SELECT "%s" FROM c2c_msg_table WHERE "40021"=?)' % c, (TARGET,)).fetchone()[0]
        print('%-6s OK %d' % (c, n))
    except Exception as e:
        print('%-6s FAIL %s' % (c, str(e)[:70]))

print()
# 用 40001 主键排序（唯一），读 40900
try:
    rows = con.execute('SELECT "40001", length("40900") FROM c2c_msg_table WHERE "40021"=? AND "40900" IS NOT NULL ORDER BY "40001" LIMIT 200', (TARGET,)).fetchall()
    print('40900 前200条 OK, 行数:', len(rows), '长度示例:', [r[1] for r in rows[:5]])
except Exception as e:
    print('40900 查询失败:', str(e)[:70])

# 全字段但按 40001 排序
print()
for off, lim in [(0,10),(10,10),(20,10),(30,10),(40,10),(50,10),(60,10),(70,10),(80,10),(90,10),(100,10),(200,10),(500,10),(1000,10),(2000,10),(5000,10),(10000,10),(20000,10),(30000,10),(40000,10)]:
    try:
        rows = con.execute('SELECT * FROM c2c_msg_table WHERE "40021"=? ORDER BY "40001" LIMIT ? OFFSET ?', (TARGET, lim, off)).fetchall()
        print('offset %d: OK %d 行' % (off, len(rows)))
    except Exception as e:
        print('offset %d: FAIL %s' % (off, str(e)[:70]))
con.close()
