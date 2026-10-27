# -*- coding: utf-8 -*-
"""检查明文 SQLite header 的保留字节字段真实值"""
import sys, struct
sys.path.insert(0, r'C:\Users\20535\AppData\Local\Temp\opencode')
from qqdec import EXT_HEADER, PAGE_SIZE, RESERVE, decrypt_page

KEY = bytes.fromhex('<数据库密钥，从临时目录 keys.txt 读取，勿外传>')
SRC = r'C:\Users\20535\Documents\Tencent Files\2053554689\nt_qq\nt_db\nt_msg.db'

with open(SRC, 'rb') as f:
    hdr = f.read(EXT_HEADER)
    p1 = f.read(PAGE_SIZE)

dec = decrypt_page(p1, KEY, skip_salt=16)
print('页1解密明文长度:', len(dec))
print('offset 16-20 原始字节:', dec[16:21].hex())
print('  page_size(16:18, 大端):', struct.unpack('>H', dec[16:18])[0])
print('  reserved(20):', dec[20])
print('  offset 21-24:', dec[21:24].hex())
print('  offset 24-28(可读页数?):', dec[24:28].hex())
print('  offset 28-32(页计数?):', dec[28:32].hex())

# 检查页2解密结果（非首页）头部与页尾
with open(SRC, 'rb') as f:
    f.seek(EXT_HEADER + PAGE_SIZE)
    p2 = f.read(PAGE_SIZE)
dec2 = decrypt_page(p2, KEY)
print()
print('页2解密明文长度:', len(dec2))
print('页2前16字节:', dec2[:16].hex())
print('页2尾48字节:', dec2[PAGE_SIZE - 48:].hex() if len(dec2) == PAGE_SIZE else dec2[-48:].hex())

# 检查加密页2的原始尾 48 字节（IV+HMAC+?）
print()
print('加密页2尾48字节:', p2[-48:].hex())
print('加密页2尾16字节(IV候选):', p2[-16:].hex())
