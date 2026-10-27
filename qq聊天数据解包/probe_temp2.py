# -*- coding: utf-8 -*-
"""深入探查 msgbackup 临时库：字段语义、类型分布、疑似会话"""
import sqlite3

DB = r'C:\Users\20535\AppData\Local\Temp\opencode\temp_3523605313_3.db'
con = sqlite3.connect(DB)

print('=== chatType 分布 ===')
for r in con.execute('SELECT chatType, COUNT(*) FROM msg GROUP BY chatType'):
    print(' chatType=%s count=%s' % r)

print('=== msgType 分布 ===')
for r in con.execute('SELECT msgType, COUNT(*) FROM msg GROUP BY msgType ORDER BY 2 DESC LIMIT 30'):
    print(' msgType=%s count=%s' % r)

print('=== 按 chatUin 分组（消息数>1，疑似真实会话） top30 ===')
for r in con.execute('SELECT chatUin, chatType, COUNT(*), MIN(msgTime), MAX(msgTime) FROM msg GROUP BY chatUin, chatType HAVING COUNT(*)>1 ORDER BY COUNT(*) DESC LIMIT 30'):
    print(' chatUin=%s chatType=%s count=%s range=[%s, %s]' % r)

print('=== 按 chatUin 分组 count>1 的会话总数 ===')
row = con.execute('SELECT COUNT(*) FROM (SELECT chatUin FROM msg GROUP BY chatUin HAVING COUNT(*)>1)').fetchone()
print(' sessions=', row[0])

print('=== 单会话消息数 >50 的候选 ===')
for r in con.execute('SELECT chatUin, COUNT(*), MIN(msgTime), MAX(msgTime) FROM msg GROUP BY chatUin HAVING COUNT(*)>50 ORDER BY COUNT(*) DESC'):
    print(' chatUin=%s count=%s range=[%s, %s]' % r)

print('=== res 表 ===')
for r in con.execute('SELECT * FROM res LIMIT 5'):
    print(' ', str(r)[:200])

print('=== msg 前 3 条原始字段 ===')
for r in con.execute('SELECT _id, chatType, chatUin, msgRandom, msgSeq, msgTime, msgType, length(extensionData), substr(extensionData,1,16) FROM msg ORDER BY _id LIMIT 3'):
    print(' ', r)

con.close()
