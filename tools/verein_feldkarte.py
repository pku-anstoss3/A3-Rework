"""Build the club field map: master-data line -> import offset -> save offset, checked against one club.

Usage: python verein_feldkarte.py <LandXXX.sav> <club name in master data> <club block .bin>
"""
import re
import struct
import sys

def parse_map(path, pat):
    out = []
    for l in open(path, encoding='utf-8'):
        m = re.match(pat, l)
        if m:
            out.append(m.groups())
    return out

loader = parse_map('analyse/verein_map.txt', r'\s*(\d+) \w+ (\w+)\s+-> 0x([0-9A-F]+)')
conv = parse_map('analyse/verein_convert_map.txt', r'\w+ imp 0x([0-9A-F]+) -> obj 0x([0-9A-F]+) \((\w+)\)')
imp2obj = {}
for io, oo, w in conv:
    io, oo = int(io, 16), int(oo, 16)
    n = {'byte': 1, 'word': 2, 'dword': 4}[w]
    for k in range(n):                 # dword copies move several byte fields at once
        imp2obj.setdefault(io + k, oo + k)
# string copies (strcpy imp -> obj)
for io, oo in ((0x00, 0x20), (0x14, 0x34), (0x18, 0x38), (0x4A, 0x6A)):
    imp2obj[io] = oo

text = open(sys.argv[1], 'rb').read().split(b'\r\n')
i = text.index(sys.argv[2].encode('cp1252'))
# values of the VEREIN section without nested TRAINER/MANAGER blocks
vals, j, depth = [], i - 2, 0
while True:
    l = text[j]
    if l.startswith(b'%SECT%SPIELER'):
        break
    if l.startswith(b'%SECT%') and j != i - 2:
        depth += 1
    elif l.startswith(b'%ENDSECT%'):
        depth -= 1
    elif depth == 0 and not l.startswith(b'%'):
        vals.append(l.decode('cp1252'))
    j += 1
rec = open(sys.argv[3], 'rb').read()
fmt = {'u8': '<B', 'i8': '<b', 'i16': '<h', 'i32': '<i', 'i32l': '<i'}
print('Zeile | Typ | Stammdaten | Import | Spielstand | Wert im Spielstand')
strings = {3: 0x00, 4: 0x14, 39: None, 40: None}
for n, kind, off in loader:
    n, off = int(n), int(off, 16)
    tv = vals[n - 2] if 0 <= n - 2 < len(vals) else '?'
    so = imp2obj.get(off)
    if so is None:
        print(f'{n:3d} | {kind:4s} | {tv:>12s} | 0x{off:03X} | -      | (nicht übernommen)')
        continue
    so -= 0x20
    if kind == 'date':
        sv = f'{rec[so]:02d}.{rec[so+1]:02d}.{struct.unpack_from("<h", rec, so+2)[0]}'
    elif kind == 'str':
        sv = rec[so:so + 20].split(b'\0')[0].decode('cp1252')
    else:
        sv = struct.unpack_from(fmt[kind], rec, so)[0]
    print(f'{n:3d} | {kind:4s} | {tv:>12s} | 0x{off:03X} | 0x{so:03X} | {sv}')
