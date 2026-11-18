"""Find ASCII strings in a PE file and print their virtual addresses.

Usage: python pe_strings.py <file.exe> <regex>
"""
import re, struct, sys

d = open(sys.argv[1], 'rb').read()
pe = struct.unpack_from('<I', d, 0x3C)[0]
nsec = struct.unpack_from('<H', d, pe + 6)[0]
optsz = struct.unpack_from('<H', d, pe + 20)[0]
base = struct.unpack_from('<I', d, pe + 24 + 28)[0]
secs = []
for i in range(nsec):
    o = pe + 24 + optsz + i * 40
    name = d[o:o + 8].rstrip(b'\0').decode()
    vsz, va, rsz, rptr = struct.unpack_from('<IIII', d, o + 8)
    secs.append((name, va, vsz, rptr, rsz))

def off2va(off):
    for name, va, vsz, rptr, rsz in secs:
        if rptr <= off < rptr + rsz:
            return base + va + off - rptr, name
    return None, None

pat = re.compile(sys.argv[2].encode('cp1252'))
for m in re.finditer(rb'[\x20-\x7e\xa0-\xff]{3,}', d):
    s = m.group()
    if pat.search(s):
        va, sec = off2va(m.start())
        print(f'{va:08X} {sec:6s} {s.decode("cp1252")}' if va else f'file 0x{m.start():X} {s!r}')
