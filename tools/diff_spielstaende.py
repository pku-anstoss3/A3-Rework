"""Compare two savegames byte by byte and list the regions that differ.

Usage: python diff_spielstaende.py <save_a.an3> <save_b.an3>
"""
import sys

a = open(sys.argv[1], 'rb').read()
b = open(sys.argv[2], 'rb').read()
print(f'size a={len(a)} b={len(b)}')
n = min(len(a), len(b))

# 64 KB overview: share of differing bytes per block
B = 65536
row = ''
for i in range(0, n, B):
    d = sum(x != y for x, y in zip(a[i:i + B], b[i:i + B]))
    row += ' .123456789#'[min(11, (d * 11) // B + (1 if d else 0))]
print('overview (64 KB per char):', row)

# runs of differences; a run ends after 8 equal bytes
runs = []
i = 0
while i < n:
    if a[i] != b[i]:
        j = i
        while j < n and (a[j] != b[j] or a[j + 1:j + 9] != b[j + 1:j + 9]):
            j += 1
        runs.append((i, j - i))
        i = j + 1
    else:
        i += 1
print('diff runs:', len(runs))
for s, l in runs[:50]:
    print(f'  0x{s:08x}  len {l}')
