# -*- coding: utf-8 -*-
"""探查 bak 库页1头部结构与 files 目录"""
import os, struct

BAK_DB = r'C:\Users\20535\AppData\Local\Temp\opencode\qqbak\db\160AA584B2A3EA6E6405296880BCB87B'
FILES = r'C:\Users\20535\AppData\Local\Temp\opencode\qqbak\files'

with open(BAK_DB, 'rb') as f:
    head = f.read(2048)

print('=== bak 库前 2048 字节 ===')
for off in range(0, 2048, 16):
    chunk = head[off:off+16]
    hexs = ' '.join('%02X' % b for b in chunk)
    asc = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
    print('%08X  %-48s  %s' % (off, hexs, asc))

print()
print('=== files 目录 ===')
for n in sorted(os.listdir(FILES)):
    p = os.path.join(FILES, n)
    with open(p, 'rb') as f:
        b = f.read(32)
    print('%s  size=%d  head=%s' % (n, os.path.getsize(p), b[:16].hex()))
