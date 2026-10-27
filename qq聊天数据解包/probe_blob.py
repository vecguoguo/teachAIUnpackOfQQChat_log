# -*- coding: utf-8 -*-
"""逐块定位 c2c_msg_table 读取损坏的位置"""
import sqlite3, sys

DB = r'C:\Users\20535\AppData\Local\Temp\opencode\dec_out\nt_msg_plain3.db'
TARGET = 'u_VjGLU3TISJx5yA4_aT7mSQ'
con = sqlite3.connect(DB)

# 1) 元数据查询（不带 blob）
try:
    n = con.execute('SELECT COUNT(*) FROM c2c_msg_table WHERE "40021"=?', (TARGET,)).fetchone()[0]
    print('目标会话消息数(元数据):', n)
except Exception as e:
    print('元数据查询失败:', e)

# 2) 只读 40800 长度
try:
    n2 = con.execute('SELECT COUNT(*) FROM (SELECT "40800" FROM c2c_msg_table WHERE "40021"=?)', (TARGET,)).fetchone()[0]
    print('带 40800 的计数:', n2)
except Exception as e:
    print('40800 计数失败:', e)

# 3) 二分定位：读取 id 排序后某范围，看是否报错
def probe(off, lim, tag):
    try:
        rows = con.execute(
            'SELECT "40001", length("40800") FROM c2c_msg_table WHERE "40021"=? '
            'ORDER BY "40050" LIMIT ? OFFSET ?', (TARGET, lim, off)).fetchall()
        print('%s: OK %d 行' % (tag, len(rows)))
        return True
    except Exception as e:
        print('%s: FAIL %s' % (tag, str(e)[:80]))
        return False

probe(0, 1000, '0-1000')
probe(1000, 1000, '1000-2000')
probe(2000, 1000, '2000-3000')
probe(4000, 1000, '4000-5000')
probe(8000, 1000, '8000-9000')
probe(16000, 1000, '16000-17000')
probe(32000, 1000, '32000-33000')
probe(40000, 1000, '40000-41000')
con.close()
