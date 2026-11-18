"""Anstoss 3 LZ decompressor, rebuilt from anstoss3.exe 1.40 (routine at 0x007D30F0).

Packed buffer layout:
  int32 n      0 -> empty, < 0 -> -n raw bytes follow, > 0 -> n unpacked bytes, bitstream follows
  bitstream    32-bit little-endian words, bits taken LSB first
    flag bit 0 -> literal: next 8 bits
    flag bit 1 -> match:
        sel   = 3 bits
        off   = read(OFF_BITS[sel]) + OFF_BASE[sel]; source = dest - off - 1
        len   = 2; k = 2; loop: v = read(k); len += v; stop if v != 2**k - 1; k += 1
"""
import struct

OFF_BITS = [1, 2, 3, 4, 5, 6, 7, 8]          # 0x8B3E78, even entries
OFF_BASE = [0, 2, 6, 14, 30, 62, 126, 254]   # 0x8B3E7C, odd entries


class _Bits:
    def __init__(self, buf, pos):
        self.buf, self.pos = buf, pos
        self.acc, self.n = 0, 0

    def read(self, k):
        while self.n < k:
            w = struct.unpack_from('<I', self.buf, self.pos)[0] if self.pos + 4 <= len(self.buf) else 0
            self.pos += 4
            self.acc |= w << self.n
            self.n += 32
        v = self.acc & ((1 << k) - 1)
        self.acc >>= k
        self.n -= k
        return v


def unpack(buf, pos=0):
    """Return (data, end_pos). end_pos is the word-aligned position after the bitstream."""
    n = struct.unpack_from('<i', buf, pos)[0]
    pos += 4
    if n == 0:
        return b'', pos
    if n < 0:
        return bytes(buf[pos:pos - n]), pos - n
    out = bytearray()
    br = _Bits(buf, pos)
    while len(out) < n:
        if br.read(1) == 0:
            out.append(br.read(8))
        else:
            sel = br.read(3)
            off = br.read(OFF_BITS[sel]) + OFF_BASE[sel]
            length, k = 2, 2
            while True:
                v = br.read(k)
                length += v
                if v != (1 << k) - 1:
                    break
                k += 1
            src = len(out) - off - 1
            if src < 0:
                raise ValueError(f'match before start at out={len(out)}')
            for i in range(length):
                out.append(out[src + i])
    return bytes(out[:n]), br.pos
