"""Find the table behind an in-game screen: search a cached savegame for rows of numbers read off a screenshot.

Usage: python a3suche.py <cache folder> <savegame name> <probe file.json>
Probe file: {"name": {"rows": [[v, v, ...], [v, ...]], "window": 40}, "name2": {"bytes": "0c020308"}}
  rows    numbers of consecutive table rows as shown in the game; a hit is a block in which, for every row, all numbers
          occur as int16 inside a window of <window> bytes, the rows in ascending order of position.
  bytes   hex string searched literally (dates: day, month, year as int16 little endian).
Prints block index, block size, the positions of the rows and the distance between rows (= record length).
"""
import json
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a3scan      # noqa: E402


def find_row(b, vals, window, start=0):
    """First position >= start where all values of the row occur as int16 within the window; -1 if none."""
    needles = [struct.pack('<h', v) for v in vals]
    rare = max(range(len(vals)), key=lambda i: abs(vals[i]))
    p = b.find(needles[rare], start)
    while p >= 0:
        lo, hi = max(0, p - window), min(len(b), p + window)
        seg = b[lo:hi]
        pos = []
        for nd in needles:
            q = seg.find(nd)
            if q < 0:
                break
            pos.append(lo + q)
        else:
            return min(pos)
        p = b.find(needles[rare], p + 1)
    return -1


def main():
    cache, name, probe_file = sys.argv[1:4]
    idx, blocks = a3scan.load(cache, name)
    probes = json.load(open(probe_file, encoding='utf-8'))
    for pname, pr in probes.items():
        hits = []
        for i, b in enumerate(blocks):
            if len(b) in (2416, 852000) or not b:
                continue
            if 'bytes' in pr:
                nd = bytes.fromhex(pr['bytes'])
                p = b.find(nd)
                if p >= 0:
                    hits.append((i, len(b), [p], b.count(nd)))
                continue
            pos, start = [], 0
            for row in pr['rows']:
                p = find_row(b, row, pr.get('window', 40), start)
                if p < 0:
                    break
                pos.append(p)
                start = p + 2
            else:
                hits.append((i, len(b), pos, None))
        print(f'== {pname}: {len(hits)} Treffer')
        for i, n, pos, cnt in hits[:6]:
            step = [b2 - a for a, b2 in zip(pos, pos[1:])]
            print(f'   Block {i:4d} ({n:6d} Byte)  Positionen {pos}  Abstaende {step}' + (f'  Vorkommen {cnt}' if cnt else ''))


if __name__ == '__main__':
    main()
