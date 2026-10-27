import os
import sys

sys.path.insert(0, r'C:\Users\20535\AppData\Local\Temp\opencode')
from qqdec import (
    verify_key_hmac, page_salt, decrypt_db, pagescan_keys, scan_pid_for_salts, EXT_HEADER, PAGE_SIZE,
)

OUT = r'C:\Users\20535\AppData\Local\Temp\opencode\dec_out'
os.makedirs(OUT, exist_ok=True)

# 1) verify memory keys against every local db + bak db (using stored salt of each db)
keys_file = r'C:\Users\20535\AppData\Local\Temp\opencode\keys.txt'
pairs = []
for line in open(keys_file, encoding='utf8'):
    line = line.strip()
    if line:
        k, s = line.split()
        pairs.append((k, s))

bak_dir = r'C:\Users\20535\AppData\Local\Temp\opencode\qqbak\db'
local_dir = r'C:\Users\20535\Documents\Tencent Files\2053554689\nt_qq\nt_db'

targets = []
for n in os.listdir(bak_dir):
    targets.append(('bak_' + n[:6], os.path.join(bak_dir, n)))
for n in ['nt_msg.db', 'profile_info.db', 'group_info.db']:
    p = os.path.join(local_dir, n)
    if os.path.exists(p):
        targets.append(('local_' + n, p))

for name, p in targets:
    pg = page_salt(p)
    if pg is None:
        print(name, 'no valid page1')
        continue
    matches = [k for k, s in pairs if verify_key_hmac(pg, bytes.fromhex(k))]
    print(name, 'salt=' + pg[:16].hex(), 'matches:', matches)

# 2) if the user just imported bak (msgbackup temp file exists), also try global PRE key
# 3) targeted rescan for bak salts
print('\n-- targeted salt rescan --')
bak_salts = []
for name, p in targets:
    if name.startswith('bak_'):
        pg = page_salt(p)
        if pg is not None:
            bak_salts.append(pg[:16].hex())
print('bak salts:', bak_salts)
hits = {}
for pid in [6752, 21404, 2960, 24644, 22280, 16148, 16684, 28444]:
    try:
        hv = scan_pid_for_salts(pid, bak_salts)
        for sh, lst in hv.items():
            hits.setdefault(sh, []).extend(lst)
            print(f'PID {pid}: salt hit {sh[:16]}... x{len(lst)}')
    except Exception as e:
        print(pid, 'err', e)
print('targeted hits:', {k: len(v) for k, v in hits.items()})

# 4) full key list rescan (maybe new keys appeared since first scan)
print('\n-- full regex rescan of main pid --')
allkeys = pagescan_keys(6752)
print(f'{len(allkeys)} key/salt pairs')
km = {}
for k, s in allkeys:
    km.setdefault(s, []).append(k)
for name, p in targets:
    pg = page_salt(p)
    if pg is None:
        continue
    salt_hex = pg[:16].hex()
    cand = km.get(salt_hex, [])
    matched = [k for k in cand if verify_key_hmac(pg, bytes.fromhex(k))]
    if matched:
        print('KEY FOUND for', name, matched[0])
