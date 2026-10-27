import hashlib
import hmac as hmac_mod
import os
import re
import struct
import sqlite3
import ctypes
import ctypes.wintypes as wt

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

EXT_HEADER = 1024
PAGE_SIZE = 4096
SALT_SIZE = 16
KEY_SIZE = 32
IV_SIZE = 16
HMAC_SIZE = 20
RESERVE = 48
HMAC_MASK = 0x3A
KDF_ITER = 4000
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
    computed = hmac_mod.new(hmac_key, content + iv + struct.pack('<I', 1), hashlib.sha1).digest()
    return hmac_mod.compare_digest(computed, stored)


def decrypt_page(page_data, enc_key, skip_salt=0):
    data = page_data[skip_salt:]
    encrypted = data[:len(data) - RESERVE]
    iv = data[len(data) - RESERVE:len(data) - RESERVE + IV_SIZE]
    cipher = Cipher(algorithms.AES(enc_key), modes.CBC(iv))
    dec = cipher.decryptor()
    return dec.update(encrypted) + dec.finalize()


def page_salt(path):
    with open(path, 'rb') as f:
        dbg = f.read(EXT_HEADER + PAGE_SIZE)
    if len(dbg) < EXT_HEADER + PAGE_SIZE:
        return None
    if dbg[:16] != b'SQLite header 3\x00':
        return None
    return dbg[EXT_HEADER:EXT_HEADER + PAGE_SIZE]


def decrypt_db(input_path, output_path, enc_key):
    with open(input_path, 'rb') as f:
        file_data = f.read()
    sc = file_data[EXT_HEADER:]
    if len(sc) < PAGE_SIZE:
        return False
    npages = len(sc) // PAGE_SIZE
    out = bytearray()
    for pgno in range(1, npages + 1):
        page_raw = sc[(pgno - 1) * PAGE_SIZE: pgno * PAGE_SIZE]
        skip = SALT_SIZE if pgno == 1 else 0
        try:
            dec = decrypt_page(page_raw, enc_key, skip_salt=skip)
        except Exception:
            dec = b'\x00' * PAGE_SIZE
        if pgno == 1:
            full = bytearray(b'SQLite format 3\x00')
            full.extend(dec)
            full[16:18] = struct.pack('>H', PAGE_SIZE)
            # 保留解密出的 read/write version (18/19)
            # 保留字节数必须等于实际数据区与页长之差（RESERVE=48），
            # 使 SQLite 按 [0,4048) 解析数据区（cell 指针数组位置正确）
            full[20] = RESERVE
            if len(full) < PAGE_SIZE:
                full.extend(b'\x00' * (PAGE_SIZE - len(full)))
            out.extend(bytes(full[:PAGE_SIZE]))
        else:
            out.extend(dec)
            if len(dec) < PAGE_SIZE:
                out.extend(b'\x00' * (PAGE_SIZE - len(dec)))
    with open(output_path, 'wb') as f:
        f.write(out)
    try:
        con = sqlite3.connect(output_path)
        tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        con.close()
        return len(tables) > 0
    except Exception:
        return False


# ---- targeted memory scan for given salt needles ----
windll = ctypes.windll
PATTERN_RE = re.compile(rb"x'([0-9a-fA-F]{64})([0-9a-fA-F]{32})'")


class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", wt.DWORD),
        ("RegionSize", ctypes.c_size_t),
        ("State", wt.DWORD),
        ("Protect", wt.DWORD),
        ("Type", wt.DWORD),
    ]


def scan_pid_for_salts(pid, salt_hexes):
    h = windll.kernel32.OpenProcess(0x0400 | 0x0010, False, pid)
    if not h:
        return {}
    hits = {}
    needles = {sh.encode('ascii'): sh for sh in salt_hexes}
    chunk = 4 * 1024 * 1024
    buf = ctypes.create_string_buffer(chunk)
    addr = 0
    mbi = MEMORY_BASIC_INFORMATION()
    mbiSize = ctypes.sizeof(mbi)
    while True:
        r = windll.kernel32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), mbiSize)
        if not r:
            break
        base = (ctypes.cast(mbi.BaseAddress, ctypes.c_void_p).value or 0)
        size = mbi.RegionSize
        state, prot = mbi.State, mbi.Protect
        if state == 0x1000 and prot not in (0x01, 0x100) and prot and not (prot & 0x100):
            remaining = size
            cur = base
            while remaining > 0:
                n = min(chunk, remaining)
                read = ctypes.c_size_t(0)
                if windll.kernel32.ReadProcessMemory(h, ctypes.c_void_p(cur), buf, n, ctypes.byref(read)):
                    raw = buf.raw[:read.value]
                    for needle, sh in needles.items():
                        if needle in raw:
                            hits.setdefault(sh, []).append((pid, cur))
                cur += n
                remaining -= n
        addr = base + size
        if size == 0:
            break
    windll.kernel32.CloseHandle(h)
    return hits


def pagescan_keys(pid):
    """Full regex scan for x'key salt'."""
    h = windll.kernel32.OpenProcess(0x0400 | 0x0010, False, pid)
    if not h:
        return []
    out = set()
    chunk = 4 * 1024 * 1024
    buf = ctypes.create_string_buffer(chunk)
    addr = 0
    mbi = MEMORY_BASIC_INFORMATION()
    mbiSize = ctypes.sizeof(mbi)
    while True:
        r = windll.kernel32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), mbiSize)
        if not r:
            break
        base = (ctypes.cast(mbi.BaseAddress, ctypes.c_void_p).value or 0)
        size = mbi.RegionSize
        state, prot = mbi.State, mbi.Protect
        if state == 0x1000 and prot not in (0x01, 0x100) and prot and not (prot & 0x100):
            remaining = size
            cur = base
            while remaining > 0:
                n = min(chunk, remaining)
                read = ctypes.c_size_t(0)
                if windll.kernel32.ReadProcessMemory(h, ctypes.c_void_p(cur), buf, n, ctypes.byref(read)):
                    for m in PATTERN_RE.finditer(buf.raw[:read.value]):
                        out.add((m.group(1).decode(), m.group(2).decode()))
                cur += n
                remaining -= n
        addr = base + size
        if size == 0:
            break
    windll.kernel32.CloseHandle(h)
    return sorted(out)
