"""Compare all cached savegames (a3scan.py cache) over time and report inconsistencies.

Usage: python a3verlauf.py <cache folder> <out.json>
Writes one summary per savegame (year estimate, managers, table "Beste Mannschaft", strongest squads, titles, squad
strength and account of every club) and prints:
  - the timeline of the table "Beste Mannschaft" (distinct entries per savegame, strongest squad at that time)
  - title counters that decrease between two savegames (they may only grow)
  - entries of "Beste Mannschaft" for a past season that change between two savegames
"""
import json
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a3scan      # noqa: E402
import a3export    # noqa: E402


# Best-of lists of the game (top 20 / top 60 of one savegame) that are continued over all savegames.
# key prefix of S['tab'] -> (columns that identify an entry, None = the whole row; value that only grows; sort key)
RANG = {
    'supertransfers': (None, lambda r: 0, lambda r: -float(r[4].replace(',', '.'))),
    'zuschauer': (None, lambda r: 0, lambda r: -r[1]),
    # order as in the game (0x00725E61): championships + cups + European cups, then championships, then all five columns
    'trainer': ([1], lambda r: sum(r[2:7]), lambda r: (-(r[2] + r[3] + r[4]), -r[2], -sum(r[2:7]))),
    'rauswuerfe': ([1], lambda r: (r[2], r[3]), lambda r: (-r[2], -r[3])),
    'spieleraufstiege': ([1], lambda r: r[2], lambda r: -r[2]),
    'spielerabstiege': ([1], lambda r: r[2], lambda r: -r[2]),
}


def number(name):
    m = re.search(r'(\d+)$', name)
    return int(m.group(1)) if m else 1          # a name without number = first savegame


def main():
    cache, out = sys.argv[1], sys.argv[2]
    names = sorted((f[:-9] for f in os.listdir(cache) if f.endswith('.idx.json')), key=number)
    saves, errors = [], []
    roll, conflicts = {'meister': {}, 'herbst': {}}, []
    wett, wett_conflicts = {}, []
    spieler, listen = {}, {}
    ligen, ligen_conf = {}, 0
    fj, fj_conf = {}, 0
    rang = {}
    for name in names:
        try:
            idx, blocks = a3scan.load(cache, name)
            S = a3export.read_blocks(blocks)
        except Exception as e:                   # keep going, report at the end
            errors.append((name, repr(e)))
            continue
        hdr = bytes.fromhex(idx['header'])
        strs = [m.group().decode('cp1252') for m in re.finditer(rb'[\x20-\x7e\x80-\xff]{3,}', hdr)]
        saves.append({
            'name': name, 'nr': number(name), 'mtime': idx['mtime'], 'blocks': len(blocks), 'year': S['year'],
            'mgr': [{'v': m['v'], 'club': m['club'], 'level': m['level'], 'titel': m['titel'], 'm': m['ehr'][0][1],
                     'spiele': sum(x[0] for x in m['spiele']), 'erf': m['erfolge']} for m in S['mgr']]
                   or [{'v': strs[i], 'club': strs[i + 2]} for i in range(0, len(strs) - 3, 4)],
            'best': [[b['s'], S['clubs'][b['c']]['n'] if b['c'] >= 0 else '', b['sum'], b['cnt']] for b in S['best']],
            'top': [[c['n'], c['ss'], c['sq']] for c in sorted(S['clubs'], key=lambda c: -c['ss'])[:5]],
            # money: fortune at season start, profit, current fortune, investments, credits, bank balance, market value
            'clubs': {c['n']: [c['t'], c['ss'], c['sq'], [c['vs'], c['gw'], c['va'], c['an'], c['kr'], c['ba'],
                                                         c['ag'][2] if c['ag'] else None]] for c in S['clubs']},
        })
        for key in ('meister', 'herbst'):             # rolling 20-season tables -> keep every season ever seen
            for s, l, club, p, g, a in S[key]:
                old = roll[key].get((l, s))
                if old and old[:4] != [club, p, g, a]:
                    conflicts.append((key, l, s, old, [club, p, g, a], number(name)))
                roll[key].setdefault((l, s), [club, p, g, a, number(name)])
        # Career values stand in the player record itself (checked on Soerloth and Quagliarella, savegame 383):
        # 0x170 goals, 0x180 games, 0x246 internationals. Keep the highest value ever seen per player (name + birth date).
        dec = [n.decode('cp1252', 'replace') for n in S['names']]
        for i, r in enumerate(S['raw_players']):
            y = struct.unpack_from('<h', r, 0x14A)[0]
            if y <= 0:
                continue
            goals, games = (struct.unpack_from('<h', r, o)[0] for o in (0x170, 0x180))
            caps = r[0x246]                           # one byte; the list "Rekordnationalspieler" stores the same number plus 256 while active
            if not (0 <= goals <= 3000 and 0 <= games <= 3000) or goals + games == 0:
                continue
            v, n = struct.unpack_from('<HH', r, 0x19E)
            if v >= len(dec) or n >= len(dec):
                continue
            pname = (dec[v] + ' ' + dec[n]).strip()
            e = spieler.setdefault((pname, r[0x148], r[0x149], y), [0, 0, 0, '', 0])
            e[0], e[1], e[2] = max(e[0], goals), max(e[1], games), max(e[2], caps)
            if i in S['member']:
                e[3] = S['clubs'][S['member'][i]]['n']
            e[4] = number(name)
        for land in a3export.TITLE_LANDS:             # the game's own top-20 lists also keep players whose record is gone
            for row in S['tab'].get(f'torjaeger-{land}', {}).get('rows', []):
                e = listen.setdefault((row[1], row[7]), [0, 0, 0, row[2]])
                e[0], e[1] = max(e[0], row[5]), max(e[1], row[4])
            for row in S['tab'].get(f'nationalspieler-{land}', {}).get('rows', []):
                e = listen.setdefault((row[1], row[3]), [0, 0, 0, ''])
                e[2] = max(e[2], row[2])
        for lg, L in S['ligen'].items():              # league archive: ten seasons per savegame, keep every season ever seen
            dst = ligen.setdefault(lg, {'name': L['name'], 'land': L['land'], 's': {}})
            for season, data in L['s'].items():
                old = dst['s'].get(str(season))
                if old and old['tab'] != data['tab']:
                    ligen_conf += 1
                dst['s'].setdefault(str(season), data)
        for key, t in S['tab'].items():               # best-of lists: keep every row ever seen
            rule = RANG.get(key.split('-')[0])
            if not rule:
                continue
            ident, value, _ = rule
            d = rang.setdefault(key, {})
            for r in t['rows']:
                k = json.dumps([r[i] for i in ident] if ident else r[1:], ensure_ascii=False)
                if k not in d or value(r) >= value(d[k]):
                    d[k] = r
        for land, total, *ys in S['fj']:              # five-year ranking: ys[0..5] are the seasons year-6 .. year-1
            d = fj.setdefault(land, {})
            for i, v in enumerate(ys[:6]):
                season = S['year'] - 6 + i
                if season in d and abs(d[season] - v) > 0.01:
                    fj_conf += 1
                d.setdefault(season, round(v, 3))
        for key, rows in S['wett'].items():           # finals and top scorers: rolling lists, keep every entry ever seen
            d = wett.setdefault(key, {})
            for r in rows:
                k = (r[0], r[1]) if key.startswith('torschuetzen') else (r[0],)
                if k in d and d[k][:-1] != r:
                    wett_conflicts.append((key, k, d[k], r, number(name)))
                d.setdefault(k, r + [number(name)])
    # "Beste Mannschaft" rebuilt: every distinct entry ever seen is a true value for its season (entries never change
    # afterwards, see the check below). Up to the 20th season the table is complete, later only record seasons survive.
    rebuilt = {}
    for s in saves:
        for b in s['best']:
            if b[0] and b[0] not in rebuilt:
                rebuilt[b[0]] = [b[0], b[1], b[2], b[3], s['nr']]
    last_of_season = {}
    for s in saves:
        last_of_season[s['year']] = s                 # last savegame of each season
    seasons = sorted(set(rebuilt) | set(last_of_season))
    table = [{'s': y, 'e': rebuilt.get(y), 'k': [last_of_season[y]['nr']] + last_of_season[y]['top'][0] if y in last_of_season else None}
             for y in seasons]
    # Manager titles without the game's limit of 49 entries: union of the lists of all savegames.
    # A title is identified by (season, type, club); the game keeps only the newest 49 per manager.
    titles = {}
    for s in saves:
        for m in s['mgr']:
            got = titles.setdefault(m['v'], {})
            for y, t, c in m.pop('erf', []):
                got.setdefault((y, t, c), s['nr'])
    mgr_titles = {v: sorted([y, t, c, nr] for (y, t, c), nr in got.items()) for v, got in titles.items()}
    hist = {key: sorted([l, s] + v for (l, s), v in d.items()) for key, d in roll.items()}
    wett_out = {key: [d[k] for k in sorted(d)] for key, d in wett.items() if d}
    # one row per player: [name, last club, birth year, games, goals, internationals, last savegame]
    rows = {}
    for (pname, d, m, y), (goals, games, caps, club, nr) in spieler.items():
        rows[(pname, y)] = [pname, club, y, games, goals, caps, nr]
    # merge the game's own lists; a player is name + birth year, because the game brings names back as new players
    for (pname, y), (goals, games, caps, club) in listen.items():
        r = rows.get((pname, y))
        if r:
            r[3], r[4], r[5] = max(r[3], games), max(r[4], goals), max(r[5], caps)
            r[1] = r[1] or club
        else:
            rows[(pname, y)] = [pname, club, y, games, goals, caps, 0]
    allrows = list(rows.values())
    top = lambda col, n=400: sorted((r for r in allrows if r[col] > 0), key=lambda r: -r[col])[:n]
    spieler_out = {'tore': top(4), 'spiele': top(3), 'laender': top(5)}
    rang_out = {}
    for key, d in rang.items():
        rows = sorted(d.values(), key=RANG[key.split('-')[0]][2])
        rang_out[key] = [[i + 1] + r[1:] for i, r in enumerate(rows)]
    print('Ranglisten ueber alle Spielstaende: ' + ', '.join(f'{k} {len(v)}' for k, v in rang_out.items()))
    json.dump({'rang': rang_out, 'saves': saves, 'best': table, 'mgr_titles': mgr_titles, 'meister': hist['meister'], 'herbst': hist['herbst'],
               'wett': wett_out, 'spieler': spieler_out, 'ligen': ligen, 'fj': fj}, open(out, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(f'5-Jahreswertung: {len(fj)} Laender, {len({s for d in fj.values() for s in d})} Saisons; Widersprueche: {fj_conf}')
    print('Liga-Archiv: ' + ', '.join(f'{L["name"]} ({L["land"]}): {len(L["s"])} Saisons' for L in ligen.values()) + f'; Widersprueche: {ligen_conf}')
    print(f'Spieler mit Laufbahnwerten: {len(allrows)}; meiste Tore: {spieler_out["tore"][:3]}')
    print(f'meiste Spiele: {spieler_out["spiele"][:3]}')
    print(f'meiste Laenderspiele: {spieler_out["laender"][:3]}')
    print('Wettbewerbe (Eintraege je Liste): ' + ', '.join(f'{k} {len(v)}' for k, v in wett_out.items()))
    print(f'Widersprueche zwischen Spielstaenden bei Endspielen/Torschuetzen: {len(wett_conflicts)}')
    for c in wett_conflicts[:15]:
        print('  ', c)
    for key in ('meister', 'herbst'):
        per_land = {}
        for l, s, *_ in hist[key]:
            per_land.setdefault(l, []).append(s)
        print(f'{key}: ' + ', '.join(f'Land {l}: {len(v)} Saisons ({min(v)}-{max(v)})' for l, v in per_land.items()))
    print(f'Widersprueche zwischen Spielstaenden bei Meister/Herbstmeister: {len(conflicts)}')
    for c in conflicts[:20]:
        print('  ', c)
    for v, lst in mgr_titles.items():
        total = next((m['titel'] for m in saves[-1]['mgr'] if m['v'] == v), None)
        years = sorted({x[0] for x in lst})
        print(f'Titel von {v}: {len(lst)} einzeln bekannt, Zaehler im letzten Spielstand {total}; Saisons {years[0]}-{years[-1]}, '
              f'Typen {sorted({x[1] for x in lst})}')

    print(f'{len(saves)} Spielstaende ausgewertet, {len(errors)} Fehler')
    for n, e in errors:
        print('  FEHLER', n, e)

    print('\n== Zeitleiste "Beste Mannschaft" ==')
    print(' Nr  Jahr  Bloecke  versch. Eintraege  letzter Eintrag                         staerkster Kader (berechnet)')
    for s in saves:
        ent = [tuple(b) for b in s['best'] if b[0]]
        uniq = sorted(set(ent))
        last = ent[-1] if ent else None
        print(f'{s["nr"]:3d}  {s["year"]}  {s["blocks"]:6d}  {len(uniq):3d} von {len(ent):2d}        '
              f'{str(last):40s} {s["top"][0]}')

    print('\n== Titelzaehler, die kleiner werden ==')
    bad = 0
    for a, b in zip(saves, saves[1:]):
        for n, ca in a['clubs'].items():
            cb = b['clubs'].get(n)
            if ca[0] and cb and cb[0]:
                for k, lab in enumerate(('Meister', 'Pokal', 'Europa')):
                    if cb[0][k] < ca[0][k]:
                        bad += 1
                        if bad <= 40:
                            print(f'  {n}: {lab} {ca[0][k]} -> {cb[0][k]}  (Spielstand {a["nr"]} -> {b["nr"]})')
    print(f'  {bad} Faelle')

    print('\n== Eintraege vergangener Saisons, die sich aendern ("Beste Mannschaft") ==')
    seen, bad = {}, 0
    for s in saves:
        for b in s['best']:
            if not b[0] or b[0] >= s['year']:         # only seasons that are over
                continue
            if b[0] in seen and seen[b[0]][1] != b[1:]:
                bad += 1
                if bad <= 40:
                    print(f'  Saison {b[0]}: {seen[b[0]][1]} (Spielstand {seen[b[0]][0]}) -> {b[1:]} (Spielstand {s["nr"]})')
            seen[b[0]] = (s['nr'], b[1:])
    print(f'  {bad} Faelle')


if __name__ == '__main__':
    main()
