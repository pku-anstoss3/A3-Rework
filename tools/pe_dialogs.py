"""List dialog resources (RT_DIALOG) of a PE file with their controls.

Usage: python pe_dialogs.py <file.exe> [filter-regex]
Prints, per dialog: id, caption, then each control as  id  class  (x,y,w,h)  text
"""
import re
import struct
import sys

d = open(sys.argv[1], 'rb').read()
flt = re.compile(sys.argv[2], re.I) if len(sys.argv) > 2 else None
pe = struct.unpack_from('<I', d, 0x3C)[0]
nsec = struct.unpack_from('<H', d, pe + 6)[0]
opt = pe + 24
optsz = struct.unpack_from('<H', d, pe + 20)[0]
res_rva = struct.unpack_from('<I', d, opt + 96 + 2 * 8)[0]
secs = []
for i in range(nsec):
    o = opt + optsz + i * 40
    vsz, va, rsz, rp = struct.unpack_from('<IIII', d, o + 8)
    secs.append((va, max(vsz, rsz), rp))


def r2o(rva):
    for va, sz, rp in secs:
        if va <= rva < va + sz:
            return rva - va + rp
    raise ValueError(hex(rva))


res = r2o(res_rva)


def entries(off):
    nn, ni = struct.unpack_from('<HH', d, off + 12)
    for k in range(nn + ni):
        name, ptr = struct.unpack_from('<II', d, off + 16 + 8 * k)
        yield name, ptr


def wstr(off):
    """Read sz_Or_Ord at off; return (value, new_off)."""
    w = struct.unpack_from('<H', d, off)[0]
    if w == 0:
        return '', off + 2
    if w == 0xFFFF:
        return f'#{struct.unpack_from("<H", d, off + 2)[0]}', off + 4
    e = off
    while struct.unpack_from('<H', d, e)[0]:
        e += 2
    return d[off:e].decode('utf-16-le'), e + 2


CLS = {'#128': 'Button', '#129': 'Edit', '#130': 'Static', '#131': 'ListBox', '#132': 'ScrollBar', '#133': 'ComboBox'}


def dialog(off):
    ex = struct.unpack_from('<HH', d, off) == (1, 0xFFFF)
    if ex:
        style = struct.unpack_from('<I', d, off + 12)[0]
        n = struct.unpack_from('<H', d, off + 16)[0]
        p = off + 26
    else:
        style = struct.unpack_from('<I', d, off)[0]
        n = struct.unpack_from('<H', d, off + 8)[0]
        p = off + 18
    _, p = wstr(p)          # menu
    _, p = wstr(p)          # class
    cap, p = wstr(p)        # caption
    if style & 0x40:        # DS_SETFONT
        p += 6 if ex else 2
        _, p = wstr(p)
    ctrls = []
    for _ in range(n):
        p = (p + 3) & ~3
        if ex:
            x, y, w, h = struct.unpack_from('<hhhh', d, p + 12)
            cid = struct.unpack_from('<I', d, p + 20)[0]
            p += 24
        else:
            x, y, w, h = struct.unpack_from('<hhhh', d, p + 8)
            cid = struct.unpack_from('<H', d, p + 16)[0]
            p += 18
        cls, p = wstr(p)
        txt, p = wstr(p)
        extra = struct.unpack_from('<H', d, p)[0]
        p += 2 + extra
        ctrls.append((cid, CLS.get(cls, cls), x, y, w, h, txt))
    return cap, ctrls


for tname, tptr in entries(res):
    if tname != 5:
        continue
    for nname, nptr in entries(res + (tptr & 0x7FFFFFFF)):
        for lname, lptr in entries(res + (nptr & 0x7FFFFFFF)):
            rva = struct.unpack_from('<I', d, res + lptr)[0]
            cap, ctrls = dialog(r2o(rva))
            blob = cap + ' ' + ' '.join(c[6] for c in ctrls)
            if flt and not flt.search(blob):
                continue
            print(f'== dialog {nname & 0xFFFF} "{cap}" ({len(ctrls)} controls)')
            for cid, cls, x, y, w, h, txt in sorted(ctrls, key=lambda c: (c[3], c[2])):
                print(f'   {cid:5d} {cls:12s} ({x:3d},{y:3d},{w:3d},{h:3d}) {txt}')
