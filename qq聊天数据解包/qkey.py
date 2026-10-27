import ctypes
import ctypes.wintypes as wt
import re
import sys

PATTERN = re.compile(rb"x'([0-9a-fA-F]{64})([0-9a-fA-F]{32})'")

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
MEM_COMMIT = 0x1000
PAGE_NOACCESS = 0x01
PAGE_GUARD = 0x100

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
psapi = ctypes.WinDLL("psapi", use_last_error=True)

PROCESS_MEMORY_COUNTERS = None


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


def list_qq_pids():
    import subprocess
    out = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'QQ|wrapper' } | "
         "Select-Object ProcessId, Name, CommandLine | ConvertTo-Csv -NoTypeInformation"],
        capture_output=True, text=True)
    print(out.stdout)
    pids = []
    lines = []
    if out.stdout.strip():
        lines = out.stdout.strip().splitlines()
    for line in lines[1:]:
        fields = [f.strip('"') for f in line.split('","')]
        try:
            pids.append((int(fields[0]), fields[1]))
        except Exception:
            continue
    return pids


def scan_pid(pid):
    h = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
    if not h:
        return None
    results = set()
    addr = 0
    mbi = MEMORY_BASIC_INFORMATION()
    mbiSize = ctypes.sizeof(mbi)
    buf = ctypes.create_string_buffer(1 << 22)
    step = 0
    while True:
        r = kernel32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), mbiSize)
        if not r:
            break
        base = ctypes.cast(mbi.BaseAddress, ctypes.c_void_p).value or 0
        size = mbi.RegionSize
        prot = mbi.Protect
        state = mbi.State
        if state == MEM_COMMIT and prot not in (PAGE_NOACCESS, PAGE_GUARD):
            r = ctypes.c_size_t(0)
            ok = kernel32.ReadProcessMemory(h, ctypes.c_void_p(base), buf, min(size, 4096 * 1024),
                                            ctypes.byref(r))
            if ok:
                for m in PATTERN.finditer(buf.raw[:r.value]):
                    results.add((m.group(1).decode(), m.group(2).decode(), base))
        addr = base + size
        step += 1
        if size == 0:
            addr = ctypes.c_void_p(ctypes.c_size_t(addr).value).value
            break
        if addr > 0x7FFFFFFFFFFF:
            break
    kernel32.CloseHandle(h)
    return results


if __name__ == "__main__":
    pids = list_qq_pids()
    print("candidate pids:", pids)
    found = {}
    for pid, name in pids:
        try:
            res = scan_pid(pid)
        except Exception as e:
            print(pid, name, "ERR", e)
            continue
        if res:
            for key_hex, salt_hex, at in res:
                print(f"PID {pid}({name}): key={key_hex} salt={salt_hex} @ {at:#x}")
