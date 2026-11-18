"""Build docs/adressindex.md: every code or data address ever noted in docs/*.md and in the patch tools, sorted.

Usage: python tools/fundstellen_index.py [--oeffentlich AUSGABEDATEI]
With --oeffentlich the index is written to AUSGABEDATEI and leaves out the internal notes that are not published
(INTERN); tools/veroeffentlichen.py uses it for the public repository.
Sources: docs/*.md (except the index itself), tools/a3patch.py, tools/asm_*.py. One line per mention with file and line.
"""
import glob, os, re, sys
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'docs', 'adressindex.md')
INTERN = ('HANDOFF.md', 'forum-anstoss-juenger.md')
PUBLIC = sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == '--oeffentlich' else None
src = sorted(glob.glob(os.path.join(BASE, 'docs', '*.md'))) + [os.path.join(BASE, 'tools', 'a3patch.py')] + \
      sorted(glob.glob(os.path.join(BASE, 'tools', 'asm_*.py')))
pat = re.compile(r'0x0?([0-9A-Fa-f]{6,8})\b')
found = {}
for f in src:
    if os.path.abspath(f) == os.path.abspath(OUT) or (PUBLIC and os.path.basename(f) in INTERN):
        continue
    rel = '/'.join(os.path.relpath(f, BASE).split(os.sep))
    for no, line in enumerate(open(f, encoding='utf-8', errors='replace'), 1):
        for m in pat.finditer(line):
            a = int(m.group(1), 16)
            if not (0x00400000 <= a < 0x02000000):
                continue                                   # code 0x004…–0x007…, data up to 0x01C…
            txt = re.sub(r'\s+', ' ', line.strip())
            i = txt.find(m.group(0))
            snip = txt[max(0, i - 70):i + 110]
            found.setdefault(a, []).append((rel, no, snip))
lines = ['# Adressindex (erzeugt, nicht von Hand ändern)', '',
         'Jede in den Unterlagen und Patch-Werkzeugen genannte Adresse von `anstoss3.exe` 1.40, aufsteigend.',
         'Neu erzeugen: `python tools/fundstellen_index.py`. Überblick nach Themen: `docs/fundstellen.md`.', '',
         f'{len(found)} Adressen, {sum(len(v) for v in found.values())} Nennungen.', '']
sect = None
for a in sorted(found):
    s = 'Code' if a < 0x00800000 else 'Daten'
    if s != sect:
        sect = s; lines += [f'## {s}', '']
    lines.append(f'- `0x{a:08X}`')
    seen = set()
    for rel, no, snip in found[a]:
        if (rel, snip) in seen: continue
        seen.add((rel, snip)); lines.append(f'  - {rel}:{no} – {snip}')
text = '\n'.join(lines) + '\n'
OUT = PUBLIC or OUT
with open(OUT, 'w', encoding='utf-8', newline='\n') as fh:
    fh.write(text)
print(f'{OUT}: {len(found)} Adressen, {text.count(chr(10))} Zeilen')
