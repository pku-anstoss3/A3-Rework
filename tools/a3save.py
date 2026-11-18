"""Walk an Anstoss 3 savegame (.an3) and unpack its compressed blocks.

Layout found so far: raw header (0x000-0x1EE), then blocks [int32 packed_len][packed data].
Packed data is decoded by a3lz.unpack. Raw bytes between blocks are reported as gaps.

Usage:
  python a3save.py <save.an3>              list blocks
  python a3save.py <save.an3> <outdir>     also write every block as block_NNN.bin
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a3lz import unpack  # noqa: E402

FIRST_BLOCK = 0x1EF


def try_block(d, p):
    if p + 8 > len(d):
        return None
    L, n = struct.unpack_from('<ii', d, p)
    if not (4 <= L <= len(d) - p - 4):
        return None
    # cheap plausibility checks before decoding
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
            L, out = r
            blocks.append((p, L, out))
            p += 4 + L
            continue
        # resync: search next offset that decodes as a block
        q = p + 1
        while q < len(d) and not try_block(d, q):
            q += 1
        gaps.append((p, q - p))
        p = q
    return blocks, gaps


def main():
    d = open(sys.argv[1], 'rb').read()
    blocks, gaps = walk(d)
    total = sum(len(o) for _, _, o in blocks)
    print(f'file {len(d)} bytes, {len(blocks)} blocks, unpacked {total} bytes, gaps {len(gaps)}')
    for p, n in gaps[:20]:
        print(f'  gap at 0x{p:08X} len {n}')
    outdir = sys.argv[2] if len(sys.argv) > 2 else None
    if outdir:
        os.makedirs(outdir, exist_ok=True)
    for i, (p, L, out) in enumerate(blocks):
        if outdir:
            with open(os.path.join(outdir, f'block_{i:03d}.bin'), 'wb') as f:
                f.write(out)
        if not outdir or i < 400:
            print(f'{i:3d} 0x{p:08X} packed {L:8d} unpacked {len(out):9d}')


if __name__ == '__main__':
    main()
