"""Print a club's values and squad from an unpacked savegame (output dir of a3save.py).

Usage: python a3kader.py <unpacked_dir> "<club name>"

Layout (see docs/feldkarte-verein.md, docs/feldkarte-spieler.md):
  club records   blocks of 2416 bytes, in club-array order
  players        blocks of 852000 bytes, 1000 x 820 bytes, global index = position
  names          block whose strings (NUL separated) are the name table
  titles         block of 82340 bytes (memory 0x00B0B6B8)
"""
import glob
import os
import struct
import sys

R = 0x334
POS = ['-', 'Tor', 'Lib', 'IV', 'LV', 'RV', 'RM', 'LM', 'DM', 'OM', 'St']    # 6 RM, 7 LM, 8 DM: checked on the screen "Supertransfers"


def main():
    src, club = sys.argv[1], sys.argv[2]
    blocks = [open(f, 'rb').read() for f in sorted(glob.glob(os.path.join(src, 'block_*.bin')))]
    clubs = [b for b in blocks if len(b) == 2416]
    players = [b[k * R:(k + 1) * R] for b in blocks if len(b) == 852000 for k in range(1000)]
    names = max((b for b in blocks if b.startswith(b'Der\0Teamchef\0')), key=len).split(b'\0')
    titles = next(b for b in blocks if len(b) == 82340)

    ci = next(i for i, c in enumerate(clubs) if c[:20].split(b'\0')[0].decode('cp1252') == club)
    c = clubs[ci]
    print(f'{club}: Vereinsindex {ci}')
    print(f'  Kontostand (0x468)       {struct.unpack_from("<q", c, 0x468)[0]:,}')
    print(f'  Gründung (0x900)         {c[0x900]:02d}.{c[0x901]:02d}.{struct.unpack_from("<h", c, 0x902)[0]}')
    for name, va in (('Meisterschaften', 0xB1B860), ('Pokale', 0xB1BC98), ('Europapokale', 0xB1C0D0)):
        print(f'  {name:24s} {struct.unpack_from("<h", titles, va - 0xB0B6B8 + ci * 2)[0]}')

    def nm(i):
        r = players[i]
        v, n = struct.unpack_from('<HH', r, 0x19E)
        return f'{names[v].decode("cp1252")} {names[n].decode("cp1252")}'

    def row(i):
        r = players[i]
        pos = '/'.join(POS[p] for p in r[0x1FD:0x200] if p)
        return (f'{i:6d} {nm(i):28s} geb {r[0x148]:02d}.{r[0x149]:02d}.{struct.unpack_from("<h", r, 0x14A)[0]}  '
                f'Stärke {r[0x1FC]:2d}  Pos {pos:10s} Talent {r[0x202]}  Nat {r[0x205]:3d}  Konstanz? {r[0x25D]}')

    kader, seen = [], set()
    for i in struct.unpack_from('<40h', c, 0x1D2):
        if i <= 0 or i in seen:
            break
        seen.add(i)
        kader.append(i)
    print(f'\nKader (0x1D2, {len(kader)} Spieler):')
    for i in kader:
        print(' ', row(i))
    print('\nListe bei 0x128 (18 Einträge, vermutlich Aufstellung + Bank):')
    for i in struct.unpack_from('<18h', c, 0x128):
        print(' ', nm(i))


if __name__ == '__main__':
    main()
