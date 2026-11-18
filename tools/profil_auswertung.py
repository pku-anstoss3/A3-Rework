"""Evaluate profil_stack.ps1 output: which game code leads to the hot samples.

Usage: python profil_auswertung.py <profil_stack.txt> [hot-module, default d3d9.dll]

Return-address candidates from the stack scan are kept only if the bytes before them form a CALL
(E8 rel32, FF 15 abs, FF /2 with register or memory operand). Prints, for samples whose EIP lies in the
hot module, the most frequent first verified frames in anstoss3.exe and D3D_Dll.dll and the most frequent chains.
"""
import collections
import struct
import sys


def load_pe(path):
    d = open(path, 'rb').read()
    pe = struct.unpack_from('<I', d, 0x3C)[0]
    n = struct.unpack_from('<H', d, pe + 6)[0]
    osz = struct.unpack_from('<H', d, pe + 20)[0]
    secs = []
    for i in range(n):
        o = pe + 24 + osz + i * 40
        vsz, va, rsz, rp = struct.unpack_from('<IIII', d, o + 8)
        secs.append((va, max(vsz, rsz), rp, rsz))
    return d, secs


def byte_at(pe, rva):
    d, secs = pe
    for va, sz, rp, rsz in secs:
        if va <= rva < va + sz:
            off = rva - va
            return d[rp + off] if off < rsz else 0
    return None


def is_call_return(pe, rva):
    b = lambda k: byte_at(pe, rva - k)
    if b(5) == 0xE8:
        return True
    if b(6) == 0xFF and b(5) is not None and (b(5) & 0x38) == 0x10:          # FF /2 with disp32 or abs
        return True
    if b(2) == 0xFF and b(1) is not None and (b(1) & 0x38) == 0x10 and (b(1) >> 6) in (0, 3):
        return True
    if b(3) == 0xFF and b(2) is not None and (b(2) & 0x38) == 0x10 and (b(2) >> 6) == 1:
        return True
    if b(7) == 0xFF and b(6) is not None and (b(6) & 0x38) == 0x14 - 4 and (b(6) >> 6) == 2:
        return True
    return False


def main():
    src = sys.argv[1]
    hot = (sys.argv[2] if len(sys.argv) > 2 else 'd3d9.dll').lower()
    lines = open(src, encoding='latin-1').read().splitlines()
    i = lines.index('# samples')
    mods = {}
    for l in lines[1:i]:
        name, base, size, path = l.split(';', 3)
        mods[name.lower()] = (int(base), int(size), path)
    hb, hs, _ = mods[hot]
    pes = {'exe': ('anstoss3.exe', None), 'sgl': ('d3d_dll.dll', None), 'ddraw': ('ddraw.dll', None)}
    loaded = {}
    for tag, (mname, _) in pes.items():
        if mname in mods:
            loaded[tag] = (mods[mname][0], load_pe(mods[mname][2]))
    total = hot_n = 0
    first = {t: collections.Counter() for t in loaded}
    chains = collections.Counter()
    for l in lines[i + 1:]:
        if not l:
            continue
        parts = l.split()
        total += 1
        eip = int(parts[0], 16)
        if not (hb <= eip < hb + hs):
            continue
        hot_n += 1
        seen = {t: [] for t in loaded}
        for p in parts[1:]:
            tag, val = p.split(':')
            if tag not in loaded:
                continue
            base, pe = loaded[tag]
            v = int(val, 16)
            if is_call_return(pe, v - base) and v not in seen[tag]:
                seen[tag].append(v)
        for t in loaded:
            if seen[t]:
                first[t][seen[t][0]] += 1
        chains[' > '.join(f'{v:08X}' for v in seen.get('exe', [])[:4])] += 1
    print(f'samples {total}, in {hot}: {hot_n}')
    for t in loaded:
        print(f'\nfirst verified return address in {t}:')
        for v, c in first[t].most_common(8):
            print(f'  {v:08X} {c:5d}')
    print('\nexe chains (innermost first):')
    for k, c in chains.most_common(8):
        print(f'  {c:5d}  {k}')


if __name__ == '__main__':
    main()
