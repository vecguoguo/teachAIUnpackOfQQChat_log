# -*- coding: utf-8 -*-
"""假设验证：header 内 128-hex 字符串是否为 bak 库密钥"""
import os, re, struct, hmac, hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

EXT_HEADER = 1024
PAGE_SIZE = 4096
SALT_SIZE = 16
KEY_SIZE = 32
IV_SIZE = 16
HMAC_SIZE = 20
RESERVE = 48
HMAC_MASK = 0x3A
FAST_ITER = 2

def derive_hmac_key(enc_key_bytes, salt):
    hmac_salt = bytes(b ^ HMAC_MASK for b in salt)
    return hashlib.pbkdf2_hmac('sha512', enc_key_bytes, hmac_salt, FAST_ITER, KEY_SIZE)

def verify_key_hmac(page1, enc_key):
    salt = page1[:SALT_SIZE]
    hmac_key = derive_hmac_key(enc_key, salt)
    data_end = PAGE_SIZE - RESERVE
    content = page1[SALT_SIZE:data_end]
    iv = page1[data_end:data_end + IV_SIZE]
    stored = page1[data_end + IV_SIZE:data_end + IV_SIZE + HMAC_SIZE]
    computed = hmac.new(hmac_key, content + iv + struct.pack('<I', 1), hashlib.sha1).digest()
    return hmac.compare_digest(computed, stored)

# 注意：该 64 字节字符串是 bak 库头部中的 key_meta（元数据，非数据库密钥）。
# 已实测验证：无论取前 32B / 后 32B / 整体，HMAC 均不匹配，它不是直接解密密钥。
HEXSTR = '668320f77150908ce7f21f8b594ecae7b6e16f4f53200938c464084c950e7b9cd42c9b3c852f0008ee6ed39ddf63bd475c9b7740e4871af9665515640a5cd78e'
print('hex 长度:', len(HEXSTR), '=> 二进制字节数:', len(bytes.fromhex(HEXSTR)))

cands = {
    'full64B': bytes.fromhex(HEXSTR),
    'first32B': bytes.fromhex(HEXSTR[:64]),
    'last32B': bytes.fromhex(HEXSTR[64:]),
}
for name, p in [('160AA5', r'C:\Users\20535\AppData\Local\Temp\opencode\qqbak\db\160AA584B2A3EA6E6405296880BCB87B'),
                ('428214', r'C:\Users\20535\AppData\Local\Temp\opencode\qqbak\db\428214DED43C55194A5C3BF4AF1AB4E9'),
                ('742BB4', r'C:\Users\20535\AppData\Local\Temp\opencode\qqbak\db\742BB4A718BC3D02B1F98B4917C32089'),
                ('DCD02E', r'C:\Users\20535\AppData\Local\Temp\opencode\qqbak\db\DCD02E17A4695507A1A8A3584C383A3B')]:
    with open(p, 'rb') as f:
        dbg = f.read(EXT_HEADER + PAGE_SIZE)
    page1 = dbg[EXT_HEADER:EXT_HEADER + PAGE_SIZE]
    salt = page1[:16].hex()
    print('%s salt=%s' % (name, salt))
    for cname, key in cands.items():
        try:
            ok = verify_key_hmac(page1, key)
            print('  %s hmac=%s' % (cname, ok))
        except Exception as e:
            print('  %s err=%s' % (cname, e))
