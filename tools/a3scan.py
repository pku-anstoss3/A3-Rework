"""Read many Anstoss 3 savegames (.an3) once and keep the unpacked blocks in a compact cache.

Usage: python a3scan.py <folder with .an3 files> <cache folder> [workers]
Per savegame two files are written to the cache folder (skipped if already there and the savegame is unchanged):
  <name>.idx.json   file size, modification time, SHA-256, header (hex), block table [file pos, packed len, unpacked len], gaps
  <name>.blk.z      all unpacked blocks concatenated, zlib compressed
Other tools read the cache with load(cache_folder, name) -> (index, [block bytes ...]) in savegame order.
The savegames are only read. Format: see docs/befund-spielstand.md; the decoder here is a faster variant of tools/a3lz.py.
"""
import hashlib
import json
import os
import struct
import sys
import time
import zlib
from multiprocessing import Pool

FIRST_BLOCK = 0x1EF
_U32 = struct.Struct('<I').unpack_from
OFF_BASE = (0, 2, 6, 14, 30, 62, 126, 254)


def unpack(buf, pos=0):
    """Return (data, end_pos) like a3lz.unpack. end_pos = word-aligned position after the bitstream."""
    n = struct.unpack_from('<i', buf, pos)[0]
    pos += 4
    if n == 0:
        return b'', pos
    if n < 0:
        return bytes(buf[pos:pos - n]), pos - n
    out = bytearray()
    blen, p, acc, nb = len(buf), pos, 0, 0
    while len(out) < n:
        if nb < 12:                                   # flag + literal, or flag + selector + offset
            if p + 4 <= blen:
                acc |= _U32(buf, p)[0] << nb
            p += 4
            nb += 32
        if not acc & 1:
            out.append((acc >> 1) & 0xFF)
            acc >>= 9
            nb -= 9
            continue
        sel = (acc >> 1) & 7
        ob = sel + 1
        off = ((acc >> 4) & ((1 << ob) - 1)) + OFF_BASE[sel]
        acc >>= 4 + ob
        nb -= 4 + ob
        length, k = 2, 2
        while True:
            if nb < k:
                if p + 4 <= blen:
                    acc |= _U32(buf, p)[0] << nb
                p += 4
                nb += 32
            full = (1 << k) - 1
            v = acc & full
            acc >>= k
            nb -= k
            length += v
            if v != full:
                break
            k += 1
        src = len(out) - off - 1
        if src < 0:
            raise ValueError('match before start')
        if off + 1 >= length:
            out += out[src:src + length]
        else:                                         # overlapping copy = repeating pattern
            pat = bytes(out[src:src + off + 1])
            out += (pat * (length // (off + 1) + 1))[:length]
    used_bits = (p - pos) * 8 - nb
    return bytes(out[:n]), pos + 4 * ((used_bits + 31) // 32)


def try_block(d, p):
    if p + 8 > len(d):
        return None
    L, n = struct.unpack_from('<ii', d, p)
    if not (4 <= L <= len(d) - p - 4):
        return None
    if n == 0 and L != 4:
        return None
    if n < 0 and L != 4 - n:
        return None
    if n > 0 and not (L <= n + 64 and n <= 64 * 1024 * 1024):
        return None
    try:
        out, end = unpack(d[:p + 4 + L], p + 4)
    except (ValueError, IndexError, struct.error):
        return None
    slack = (p + 4 + L) - end
    if n > 0 and not (0 <= slack <= 4):
        return None
    return L, out


def walk(d):
    p, blocks, gaps = FIRST_BLOCK, [], []
    while p < len(d):
        r = try_block(d, p)
        if r:
            blocks.append((p, r[0], r[1]))
            p += 4 + r[0]
            continue
        q = p + 1
        while q < len(d) and not try_block(d, q):
            q += 1
        gaps.append((p, q - p))
        p = q
    return blocks, gaps


def scan_one(args):
    path, cache = args
    name = os.path.splitext(os.path.basename(path))[0]
    idx_file, blk_file = os.path.join(cache, name + '.idx.json'), os.path.join(cache, name + '.blk.z')
    st = os.stat(path)
    if os.path.exists(idx_file) and os.path.exists(blk_file):
        old = json.load(open(idx_file, encoding='utf-8'))
        if old['size'] == st.st_size and old['mtime'] == int(st.st_mtime):
            return name, 0.0, len(old['blocks']), 'vorhanden'
    t = time.time()
    d = open(path, 'rb').read()
    blocks, gaps = walk(d)
    idx = {
        'file': os.path.basename(path), 'size': st.st_size, 'mtime': int(st.st_mtime),
        'sha256': hashlib.sha256(d).hexdigest().upper(), 'header': d[:FIRST_BLOCK].hex(),
        'blocks': [[p, L, len(o)] for p, L, o in blocks],
        'gaps': [[p, n, d[p:p + n].hex() if n <= 512 else ''] for p, n in gaps],
    }
    with open(blk_file, 'wb') as f:
        f.write(zlib.compress(b''.join(o for _, _, o in blocks), 6))
    json.dump(idx, open(idx_file, 'w', encoding='utf-8'))
    return name, time.time() - t, len(blocks), 'gelesen'


def local_name(cache, name):
    """Savegame names are private. Documents and scripts say 'Karriere<N>'; the optional file tools/lokal.json (not part
    of the repository) maps such a prefix to the real one, e.g. {"Karriere": "<real name>"}."""
    if os.path.exists(os.path.join(cache, name + '.idx.json')):
        return name
    cfg = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lokal.json')
    if os.path.exists(cfg):
        for alias, real in json.load(open(cfg, encoding='utf-8')).items():
            if name.startswith(alias) and os.path.exists(os.path.join(cache, real + name[len(alias):] + '.idx.json')):
                return real + name[len(alias):]
    return name


def load(cache, name):
    name = local_name(cache, name)
    idx = json.load(open(os.path.join(cache, name + '.idx.json'), encoding='utf-8'))
    raw = zlib.decompress(open(os.path.join(cache, name + '.blk.z'), 'rb').read())
    blocks, o = [], 0
    for _, _, n in idx['blocks']:
        blocks.append(raw[o:o + n])
        o += n
    return idx, blocks


def main():
    src, cache = sys.argv[1], sys.argv[2]
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else max(1, (os.cpu_count() or 2) - 2)
    os.makedirs(cache, exist_ok=True)
    jobs = [(os.path.join(src, f), cache) for f in sorted(os.listdir(src)) if f.lower().endswith('.an3')]
    t = time.time()
    with Pool(workers) as pool:
        for name, sec, n, what in pool.imap_unordered(scan_one, jobs):
            print(f'{what:9s} {name:22s} {n:5d} Bloecke {sec:6.1f} s', flush=True)
    print(f'{len(jobs)} Spielstaende in {time.time() - t:.0f} s')


if __name__ == '__main__':
    main()
