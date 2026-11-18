"""Read the event texts of Anstoss 3 (texte/Ereignis.saq) and print them as "number<TAB>text".

Usage: python a3ereignis.py <Ereignis.saq> [number ...]
Format (loader 0x005EF298): int32 size, int32 count (2483), then `size` bytes; every byte is XORed with the previous
stored byte, the first one with the low byte of `size`. The result is `count` zero-terminated strings, numbered from 1
(text table at 0x00A2FAE8, read by 0x005EF430). The file is only read.
"""
import struct
import sys


def read(path):
    d = open(path, 'rb').read()
    size, count = struct.unpack_from('<ii', d, 0)
    raw, key, out = d[8:8 + size], size & 0xFF, bytearray()
    for b in raw:
        out.append(b ^ key)
        key = b
    return [''] + [t.decode('cp1252') for t in bytes(out).split(b'\0')[:count]]


if __name__ == '__main__':
    texts = read(sys.argv[1])
    want = [int(a, 0) for a in sys.argv[2:]] or range(1, len(texts))
    for n in want:
        print(f'{n}\t{texts[n]}')
