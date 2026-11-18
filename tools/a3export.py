"""Export clubs, squads, players and title tables from an unpacked savegame as JSON for the interactive view.

Usage: python a3export.py <unpacked_dir> <template.html> <out.html> <label> [--save file.an3] [--hist dir=label ...]
  --save   the .an3 file itself; its plain header names the human managers and their clubs
  --hist   further unpacked savegames (oldest first) for the development over time
The template contains the marker /*DATEN*/ which is replaced by the JSON object.

Sources (see docs/feldkarte-verein.md, docs/feldkarte-spieler.md, docs/fehler-beste-mannschaft.md):
  clubs    blocks of 2416 bytes; name 0x000, short 0x014, land code 0x10D, squad list 0x1D2 (40 x int16),
           finance block from 0x468 (see finance() and docs/befund-finanzen.md), founding date 0x900
  players  blocks of 852000 bytes = 1000 x 820 bytes; birth 0x148, names 0x19E/0x1A0, strengths 0x1A4,
           weaknesses 0x1A6, strength 0x1FC, positions 0x1FD-0x1FF, talent 0x202, nationality 0x205
  titles   block of 82340 bytes: championships 0x101A8, cups 0x105E0, European cups 0x10A18; int16 per club,
           5 sections of 108 clubs (Germany, England, France, Italy, Spain), index = rank of the club among the
           named clubs of its country in club-array order (checked against real title counts, 15.11.2026)
  best     block of 200 bytes following the 2144- and 2680-byte blocks: 20 x (season, land, -, club, sum, count)
Blocks must be read in numeric order (block_1000 comes after block_999, not after block_100).
"""
import collections
import glob
import json
import os
import re
import struct
import sys

R = 0x334
TITLE_LANDS = [14, 16, 20, 28, 63]          # section order in the title tables
T_OFF = {'m': 0x101A8, 'p': 0x105E0, 'e': 0x10A18}
RANG_TEXT = {       # notes for the lists merged over all savegames (a3verlauf.py, RANG)
    'supertransfers': 'Enthalten ist jeder Transfer, der in irgendeinem Spielstand unter den teuersten stand.',
    'zuschauer': 'Enthalten ist jedes Spiel, das in irgendeinem Spielstand unter den ersten 20 stand.',
    'trainer': 'Je Trainer der höchste bekannte Stand. Trainer, die nie unter den ersten 20 eines Spielstands waren, fehlen.',
    'rauswuerfe': 'Je Trainer der höchste bekannte Stand.',
    'spieleraufstiege': 'Je Spieler der höchste bekannte Stand; Spieler gleichen Namens lassen sich hier nicht trennen.',
    'spielerabstiege': 'Je Spieler der höchste bekannte Stand; Spieler gleichen Namens lassen sich hier nicht trennen.',
}

# Finance, as the balance screen of the game computes it (dialog 349, 0x004813AD; docs/befund-finanzen.md).
# Two cost steps of the club are looked up in tables of the exe (0x0089E450, 0x0089E458) and multiplied by two
# money factors (0x00A3B3BC, 0x00A3B37C); the factors are the values of a career played in DM.
FIN_STUFE_A = (0, 2, 20, 100)
FIN_STUFE_B = (0, 2, 10, 30, 15, 50, 20, 80)
FIN_FAKTOR_A, FIN_FAKTOR_B = 10000, 100000


def finance(c, index):
    """Money of one club record c (2416 bytes); index = index values of the investment kinds (block 1 from 0x104).

    vs  fortune at the start of the season (0x468, written at the season change only)
    gw  profit of the running season (0x0061FC81 over the season table from 0x480)
    va  current fortune = vs + int32 0x528 + gw            kr  credits (8 slots from 0x570)
    an  investments at their current value (0x00647D30)    ba  bank balance = va - an + kr (0x0061FD97)
    Checked to the unit against the screens "Bilanz" and "Finanzen" of savegame 383 (16.11.2026).
    """
    P, T = 0x468, 0x480
    i = lambda o: struct.unpack_from('<i', c, T + o)[0]
    u = lambda o: struct.unpack_from('<I', c, T + o)[0]
    q = lambda o: struct.unpack_from('<q', c, o)[0]
    step = lambda tab, o: tab[c[o]] if c[o] < len(tab) else 0
    gw = (i(0x08) + i(0x0C) + i(0x10) + i(0x14) + i(0x18) + i(0x1C) + i(0x20) + i(0x24) + i(0x28)
          + u(0xCC) + u(0xD0) + u(0xD4) - u(0xE0) + u(0xE4) - q(P + 0x268) + q(P + 0x260)
          - (q(T + 0xB0) + q(T + 0xC0) + i(0xC8)) + u(0xB8) - i(0x58)
          - (i(0x5C) + i(0x60) - i(0x64) + i(0x68) + i(0x6C) + i(0x88))
          - (i(0x74) + i(0x78) + i(0x7C) + i(0x80) + i(0x84)) + i(0x70)
          - (i(0x90) + i(0x98) + i(0xA0) + i(0xE8) + i(0x8C)
             + step(FIN_STUFE_A, P + 0x3D1) * FIN_FAKTOR_A + step(FIN_STUFE_B, P + 0x3D2) * FIN_FAKTOR_B)
          + (i(0x9C) + i(0x2C) + i(0xA4) + i(0xEC) + i(0x70)))      # 0x70 is counted twice by the game as well
    an = 0
    for k in range(6):
        o = 0x630 + k * 24
        base = struct.unpack_from('<h', c, o + 0x10)[0]
        if c[o + 0x13] & 1 and base and c[o + 0x12] < len(index):
            an += int(q(o + 8) * index[c[o + 0x12]] / base)
    kr = sum(q(0x570 + k * 24) for k in range(8) if c[0x570 + k * 24 + 0x0F] & 1)
    vs = q(P)
    va = vs + struct.unpack_from('<i', c, P + 0xC0)[0] + gw
    return {'vs': vs, 'gw': gw, 'va': va, 'an': an, 'kr': kr, 'ba': va - an + kr}


def stock_market(blocks):
    """{(land, club rank): (shares, current price)} from the stock exchange object (0x008BE408, lookup 0x00405DBE).

    Block (123572 bytes) = int32 number of used records, 16 further bytes, then room for 468 records of 264 bytes:
    name, land +0x1C, club +0x1E, shares +0x20, position in the ring of 52 prices +0x24 (int16), prices as float
    from +0x38 (0x00407520). Companies (sponsors) have no valid land / club.
    """
    out = {}
    for b in blocks:
        if len(b) != 20 + 468 * 264:
            continue
        for k in range(min(struct.unpack_from('<i', b, 0)[0], 468)):
            o = 20 + k * 264
            land, club, shares, pos = struct.unpack_from('<hhih', b, o + 0x1C)
            if 0 < land < 256 and 0 <= club < 256 and shares > 0 and b[o] >= 0x20:
                out[(land, club)] = (shares, struct.unpack_from('<f', b, o + 0x38 + (pos % 52) * 4)[0])
    return out


def read_save(src):
    files = sorted(glob.glob(os.path.join(src, 'block_*.bin')), key=lambda f: int(os.path.basename(f)[6:-4]))
    return read_blocks([open(f, 'rb').read() for f in files])


def read_blocks(blocks):
    """blocks = unpacked blocks of one savegame in savegame order (from a3save.py output or the a3scan.py cache)."""
    raw_clubs = [b for b in blocks if len(b) == 2416]
    raw_players = [b[k * R:(k + 1) * R] for b in blocks if len(b) == 852000 for k in range(1000)]
    names = max((b for b in blocks if b.startswith(b'Der\0Teamchef\0')), key=len).split(b'\0')
    titles = next(b for b in blocks if len(b) == 82340)
    bi = next(i for i, b in enumerate(blocks) if len(b) == 200 and len(blocks[i - 1]) == 2680 and len(blocks[i - 2]) == 2144)
    head = blocks[1] if len(blocks[1]) == 5520 else next(b for b in blocks if len(b) == 5520)
    anl_index = struct.unpack_from('<8i', head, 0x104)      # index of each investment kind (0x00B5CC8C)
    boerse = stock_market(blocks)
    best_raw = [struct.unpack_from('<hBBhhh', blocks[bi], k * 10) for k in range(20)]

    rank, clubs, gidx2id, member, dup, by_land, land_rank2id = {}, [], {}, {}, 0, {}, {}
    club_flags = {}
    for gi, c in enumerate(raw_clubs):
        name = c[:20].split(b'\0')[0].decode('cp1252')
        if not name:
            continue
        land = c[0x10D]
        lr = rank.get(land, 0)
        rank[land] = lr + 1
        by_land[(land, lr)] = name
        club_flags[(land, lr)] = c[0x10A]             # 0x0063E470: bits 0-1 = points deducted / 3, 0x80 = placed last
        land_rank2id[(land, lr)] = len(clubs)
        squad = []
        for i in struct.unpack_from('<40h', c, 0x1D2):
            if i <= 0 or i in squad or i >= len(raw_players):
                break
            squad.append(i)
        cid = len(clubs)
        gidx2id[gi] = cid
        own = []
        for i in squad:
            if i in member:
                dup += 1
                continue
            member[i] = cid
            own.append(i)
        tt = None
        if land in TITLE_LANDS and lr < 108:
            base = TITLE_LANDS.index(land) * 108 + lr
            tt = [struct.unpack_from('<h', titles, T_OFF[k] + base * 2)[0] for k in 'mpe']
        ag = boerse.get((land, lr)) if c[0x904] & 1 else None       # 0x904 bit 0 = stock corporation (0x0069D71D)
        clubs.append({
            'n': name, 'k': c[0x14:0x18].split(b'\0')[0].decode('cp1252'), 'l': land, 'g': gi,
            # money as on the balance screen of the game, see finance(); 0x470 (= 0x468 - credits + investments at the
            # season change) is not used: it counts the investments twice
            **finance(c, anl_index),
            # stock corporations only: [shares, price, market value = price x shares]
            'ag': [ag[0], round(ag[1], 2), round(ag[1] * ag[0])] if ag else None,
            'gr': struct.unpack_from('<h', c, 0x902)[0],
            't': tt, 'sq': len(own), 'ss': sum(raw_players[i][0x1FC] for i in own),
        })
    # club number in this table = rank within its country (land code in the entry), not the global club index:
    # 2019 = land 28 / club 0 = Juventus with 275/27, exactly the strongest squad in the first savegame
    best = [{'s': b[0], 'l': b[1], 'c': land_rank2id.get((b[1], b[3]), -1) if b[0] else -1, 'sum': b[4], 'cnt': b[5]} for b in best_raw]
    # current year is not mapped yet: estimate from the youngest age group that is common in the squads (17-year-olds)
    years = collections.Counter(struct.unpack_from('<h', raw_players[i], 0x14A)[0] for i in member)
    year = max(y for y, n in years.items() if n >= 20) + 17
    mgr = read_managers(blocks, by_land)
    if mgr and mgr[0]['jahre'] > 0:
        year = 2018 + mgr[0]['jahre']            # exact: n-th manager year = season (2018 + n)/(2019 + n), start 7.7.2019

    def season_table(off):
        """5 countries x 20 seasons x (season, land, club, points, goals for, goals against), int16 each."""
        rows = []
        for k in range(100):
            s, l, c, p, g, a = struct.unpack_from('<6h', titles, off + k * 12)
            if 2000 <= s <= 2300 and (l, c) in by_land:
                rows.append([s, l, by_land[(l, c)], p, g, a])
        return rows

    def team(land, club):
        land &= 0xFF                                  # high byte of the first team's land field carries a flag
        if club == 200:
            return ['L', land]                        # national team
        return ['V', by_land.get((land, club), f'Verein {club}'), land]

    def finals(off, count, size=16):
        """Finals: season, team A (land, club), team B (land, club), result (goals A, goals B as bytes), ... (int16)."""
        rows = []
        for k in range(count):
            o = off + k * size
            s, la, ca, lb, cb = struct.unpack_from('<5h', titles, o)
            if 2000 <= s <= 2300:
                rows.append([s, team(la, ca), team(lb, cb), titles[o + 10], titles[o + 11]])
        return rows

    def nat_finals(off):
        """EM / WM: year, host, team A, 200, team B, 200, result bytes, 0, code, top scorer (first, last name), goals<<8 | land."""
        rows = []
        for k in range(20):
            o = off + k * 24
            y, host, la, _, lb = struct.unpack_from('<5h', titles, o)
            vn, nn, gl = struct.unpack_from('<3h', titles, o + 18)
            if 2000 <= y <= 2300:
                nm = lambda i: names[i].decode('cp1252') if 0 <= i < len(names) else '?'
                rows.append([y, host, la & 0xFF, lb & 0xFF, titles[o + 12], titles[o + 13], (nm(vn) + ' ' + nm(nn)).strip(), gl >> 8, gl & 0xFF])
        return rows

    def scorers(off):
        """Torschuetzenkoenige of one country: first name, last name, club, goals, season (int16), up to 60 entries."""
        rows = []
        for k in range(60):
            vn, nn, c, g, s = struct.unpack_from('<5h', titles, off + k * 10)
            if 2000 <= s <= 2300 and 0 <= vn < len(names) and 0 <= nn < len(names):
                rows.append([s, (names[vn].decode('cp1252') + ' ' + names[nn].decode('cp1252')).strip(), c, g])
        return rows

    wett = {}
    for k, land in enumerate(TITLE_LANDS):
        wett[f'pokal-{land}'] = finals(54360 + k * 320, 20)
        wett[f'supercup-{land}'] = finals(55960 + k * 320, 20)
        wett[f'torschuetzen-{land}'] = [[s, n, by_land.get((land, c), f'Verein {c}'), g] for s, n, c, g in scorers(57560 + k * 600)]
    for k in range(5):                                # 0 = Champions League, 4 = Weltpokal; 1-3 not yet matched to a screen
        wett[f'international-{k}'] = finals(60560 + k * 320, 20)
    wett['em'] = nat_finals(78204)
    wett['wm'] = nat_finals(77722)

    # ---- further screens of "Historisches": current top lists, one table per key (docs/zuordnung-bildschirme.md) ----
    nm = lambda i: names[i].decode('cp1252') if 0 <= i < len(names) else '?'
    full = lambda v, n: (nm(v) + ' ' + nm(n)).strip()
    cl = lambda land, c: by_land.get((land & 0xFF, c), f'Verein {c}')
    cstr = lambda raw: raw.split(b'\0')[0].decode('cp1252', 'replace')
    bi3 = next(i for i, b in enumerate(blocks) if b is titles)
    tab = {}
    for k, land in enumerate(TITLE_LANDS):
        rows = []
        for j in range(10):                                       # Torrekorde: first name, last name, club, goals, season
            vn, nn, c, g, s = struct.unpack_from('<5h', titles, 49860 + k * 100 + j * 10)
            if g > 0:
                rows.append([s, full(vn, nn), cl(land, c), g])
        tab[f'torrekorde-{land}'] = {'cols': ['Saison', 'Name', 'Verein', 'Treffer'], 'num': [3], 'saison': [0], 'rows': rows}
        rows = []
        for j in range(20):                                       # Ewige Torjaegerliste
            vn, nn, _, yr, cf, g, pen, sp = struct.unpack_from('<8h', titles, 50360 + k * 320 + j * 16)
            if g > 0:
                rows.append([j + 1, full(vn, nn), cl(land, (cf >> 8) & 0xFF), 'ja' if cf & 0xFF else '', sp, g, pen, yr])
        tab[f'torjaeger-{land}'] = {'cols': ['Nr.', 'Name', 'Verein', 'Aktiv', 'Spiele', 'Tore', 'Elfmetertore', 'Jahrgang'], 'num': [0, 4, 5, 6, 7], 'rows': rows}
        rows = []
        for j in range(20):                                       # Rekordnationalspieler
            _, vn, nn, yr, caps = struct.unpack_from('<5h', titles, 63560 + k * 200 + j * 10)
            if caps > 0:                                          # low byte = internationals, high byte = still active
                rows.append([j + 1, full(vn, nn), caps & 0xFF, yr, 'ja' if caps >> 8 else ''])
        tab[f'nationalspieler-{land}'] = {'cols': ['Nr.', 'Name', 'Länderspiele', 'Jahrgang', 'Noch aktiv'], 'num': [0, 2, 3], 'rows': rows}
        if bi3 + 207 + k * 11 + 1 < len(blocks):                  # five per-country packages of 11 blocks start at block 204
            tr, rw = blocks[210 + k * 11], blocks[211 + k * 11]
            rows = []
            for j in range(len(tr) // 42):
                r = tr[j * 42:(j + 1) * 42]
                v = struct.unpack_from('<5h', r, 32)
                if r[2]:
                    rows.append([j + 1, cstr(r[2:32]), v[0], v[1], v[2], v[4], v[3]])
            tab[f'trainer-{land}'] = {'cols': ['Pl.', 'Trainer', 'Meister', 'Pokale', 'EPs', 'Sonstige', 'Aufstiege'], 'num': [0, 2, 3, 4, 5, 6], 'rows': rows,
                                      'hinweis': 'So zählt das Spiel. Bei menschlichen Managern fehlen dabei die Champions-League-Siege in „EPs“ und die Europäischen Supercups in „Sonstige“; bei Computertrainern zählen sie mit. Das ist ein Fehler im Spiel, die richtigen Zahlen stehen im Reiter „Manager“.'}
            rows = []
            for j in range(len(rw) // 40):
                r = rw[j * 40:(j + 1) * 40]
                ent, zeit, _, c = struct.unpack_from('<4h', r, 32)
                if r[2]:
                    rows.append([j + 1, cstr(r[2:32]), ent, zeit, cl(land, c)])
            tab[f'rauswuerfe-{land}'] = {'cols': ['Pl.', 'Trainer', 'Entlassungen', 'Trainerzeit', 'Letzter Verein'], 'num': [0, 2, 3], 'rows': rows}
    rows = []
    for j in range(60):                                           # Supertransfers
        o = 64560 + j * 28
        _, vn, nn = struct.unpack_from('<3h', titles, o)
        amount = struct.unpack_from('<i', titles, o + 12)[0]
        fl, fc, tl, tc, ps = struct.unpack_from('<5h', titles, o + 16)
        if amount <= 0:
            break
        pos = POS_CODE[ps & 0xFF] if (ps & 0xFF) < len(POS_CODE) else str(ps & 0xFF)
        rows.append([j + 1, full(vn, nn), pos, ps >> 8, f'{amount / 100.0:.2f}'.replace('.', ','), cl(fl, fc), cl(tl, tc)])
    tab['supertransfers'] = {'cols': ['Nr.', 'Name', 'Pos', 'Stärke', 'Ablöse in Mio.', 'kam von', 'ging zu'], 'num': [0, 3, 4], 'rows': rows}

    def crowd(b):
        rows = []
        for j in range(len(b) // 24):
            z = struct.unpack_from('<i', b, j * 24)[0]
            hl, hc, al, ac = struct.unpack_from('<4h', b, j * 24 + 8)
            if z > 0:
                t = lambda l, c: ['L', l & 0xFF] if c == 200 else ['V', by_land.get((l & 0xFF, c), f'Verein {c}'), l & 0xFF]
                rows.append([j + 1, z, t(hl, hc), t(al, ac), f'{b[j * 24 + 16]}:{b[j * 24 + 17]}'])
        return {'cols': ['Pl.', 'Zuschauer', 'Heim', 'Gast', 'Ergebnis'], 'num': [0, 1], 'team': [2, 3], 'rows': rows}
    # per league (index as in the season archive: 0-3 Germany, 6 England, 7 France, 8 Italy, 9 Spain):
    # league group g = 20 tables from block bi3 + 1 + g * 20, table 16 = "Meiste Zuschauer national";
    # the g-th block of 1536 bytes behind the league objects = "Haeufigstes Ergebnis": int32 matrix [home][away], 16 wide
    hbs = [b for i, b in enumerate(blocks) if len(b) == 1536 and i > 1000]
    hbs = dict(zip((0, 1, 2, 3, 6, 7, 8, 9), hbs))                # the league objects are stored without the two empty leagues
    for g in (0, 1, 2, 3, 6, 7, 8, 9):
        b = blocks[bi3 + 1 + g * 20 + 16]
        if len(b) % 24 == 0:
            t = crowd(b)
            if t['rows']:
                tab[f'zuschauer-national-{g}'] = t
        if g in hbs:
            rows = [[f'{h}:{a}', struct.unpack_from('<i', hbs[g], (h * 16 + a) * 4)[0]] for h in range(16) for a in range(16)]
            rows = sorted((r for r in rows if r[1] > 0), key=lambda r: -r[1])
            total = sum(r[1] for r in rows)
            if rows:
                tab[f'ergebnis-{g}'] = {'cols': ['Pl.', 'Ergebnis', 'insgesamt', 'Anteil'], 'num': [0, 2, 3],
                                        'hinweis': 'Alle Ergebnisse dieser Liga seit Spielbeginn 2019, Heimtore zuerst. Das Spiel zeigt nur die häufigsten.',
                                        'rows': [[i + 1] + r + [f'{100 * r[1] / total:.1f} %'.replace('.', ',')] for i, r in enumerate(rows)]}
    tab['zuschauer-international'] = crowd(blocks[bi3 + 256])
    i262 = next(i for i, b in enumerate(blocks) if len(b) == 200 and len(blocks[i - 1]) == 2680 and len(blocks[i - 2]) == 2144)
    auf, ab = blocks[i262 - 2], blocks[i262 - 1]
    rows = [[clubs[k]['n']] + list(struct.unpack_from('<4h', auf, k * 8)) for k in range(min(268, len(clubs)))]
    for land in TITLE_LANDS:
        sel = sorted((r for r, c in zip(rows, clubs) if c['l'] == land and r[1] > 0), key=lambda r: -r[1])
        tab[f'aufsteiger-{land}'] = {'cols': ['Verein', 'Aufstiege', 'in 1.', 'in 2.', 'in 3.'], 'num': [1, 2, 3, 4], 'rows': sel,
                                     'hinweis': 'So zählt das Spiel. Für Deutschland ist „Aufstiege“ zu hoch: jeder Aufstieg in die 2. Liga zählt doppelt, und Aufstiege in die Regionalliga Süd fehlen in der Spalte „in 3.“.' if land == 14 else ''}
    rows = [[clubs[k]['n']] + list(struct.unpack_from('<5h', ab, k * 10)) for k in range(min(268, len(clubs)))]
    for land in TITLE_LANDS:
        sel = sorted((r for r, c in zip(rows, clubs) if c['l'] == land and r[1] > 0), key=lambda r: -r[1])
        tab[f'absteiger-{land}'] = {'cols': ['Verein', 'Abstiege', 'aus 1.', 'aus 2.', 'aus 3.', 'aus 4.'], 'num': [1, 2, 3, 4, 5], 'rows': sel}
    for key, b in (('spieleraufstiege', blocks[i262 + 1]), ('spielerabstiege', blocks[i262 + 2])):
        rows = []
        for j in range(20):
            p, _, _, lf, c, n = struct.unpack_from('<6h', b, j * 12)
            if n > 0 and 0 < p < len(raw_players):
                v, nn2 = struct.unpack_from('<HH', raw_players[p], 0x19E)
                rows.append([j + 1, full(v, nn2), n, cl(lf, c)])
        tab[key] = {'cols': ['Pl.', 'Spieler', 'Anzahl', 'Verein'], 'num': [0, 2], 'rows': rows}
    def of_the_year(b, base):                                     # count + 20 x (year, name[30], land, club)
        rows = []
        for j in range(20):
            r = b[base + 2 + j * 36: base + 2 + (j + 1) * 36]
            if len(r) < 36:
                break
            y, (l2, c2) = struct.unpack_from('<h', r, 0)[0], struct.unpack_from('<hh', r, 32)
            if 2000 <= y <= 2300:
                rows.append([y, cstr(r[2:32]), cl(l2, c2)])
        return rows
    b3612 = [b for b in blocks if len(b) == 3612]                 # first = Manager des Jahres, second = Spieler des Jahres
    for key, b in zip(('mgrjahr', 'spielerjahr'), b3612):
        for k, land in enumerate(TITLE_LANDS):
            wett[f'{key}-{land}'] = of_the_year(b, k * 722)
    b724 = next((b for b in blocks if len(b) == 724), None)       # Fussballer Europas
    if b724:
        wett['fussballer-europas'] = of_the_year(b724, 0)
    # "Rekorde" of the career: same layout as alltimes.saq, in block 1 from offset 404 (memory 0x00B5CD1C), game dates
    tab['rekorde'] = {'cols': ['Rekord', 'Wert', 'Manager', 'Verein', 'Datum im Spiel'], 'num': [],
                      'rows': [[r[0], r[4], r[2], r[3], r[1]] for r in parse_alltimes(blocks[bi3 - 2][404:404 + 1056], by_land)]}

    # ---- archive of the last ten seasons per league: block 2 from offset 8828, 10 leagues x 10 seasons x 2418 bytes ----
    # (memory 0x00B21ADC + league * 0x5E74 + slot * 0x972, read by 0x0072B18A; slot 9 = last finished season.)
    # League object: +0 land, +2 teams, +4 second set of fixtures, +0x12 club per team (byte), +0x2A flags (bits 0-1 = points
    # deducted / 3), +0x72 + i * 96 + j * 4 result of team i at home against j: goals, goals against, half time.
    # Checked: 2112/13 gives Uerdingen 83 points 68:18, Gladbach 60 points 74:44 and Gladbach's home results as in the game.
    LG_NAME = {0: '1. Bundesliga', 1: '2. Bundesliga', 2: 'Regionalliga Nord', 3: 'Regionalliga Süd'}
    c36 = lambda v: '0123456789abcdefghijklmnopqrstuvwxyz'[min(v, 35)]
    arch, ligen = blocks[bi3 - 1], {}
    if len(arch) >= 8828 + 10 * 24180:
        for lg in range(10):
            for slot in range(10):
                r = arch[8828 + lg * 24180 + slot * 2418: 8828 + lg * 24180 + (slot + 1) * 2418]
                land, n, dbl = struct.unpack_from('<3h', r, 0)
                if not (0 < n <= 24) or land <= 0:
                    continue
                teams = list(r[0x12:0x12 + n])
                st = {k: [0, 0, 0, 0, 0, 0, 0] for k in range(n)}          # games, points, goals, against, won, drawn, lost
                res, played = [], 0
                for i in range(n):
                    row = ''
                    for j in range(n):
                        cells = [r[0x72 + i * 96 + j * 4: 0x72 + i * 96 + j * 4 + 4]]
                        if dbl:
                            cells.append(r[0x72 + i * 96 + (j + n) * 4: 0x72 + i * 96 + (j + n) * 4 + 4])
                        c = cells[0]
                        row += '--' if i == j or c[0] == 255 else c36(c[0]) + c36(c[1])
                        for c in cells:
                            if i == j or len(c) < 4 or c[0] == 255:
                                continue
                            played += 1
                            for k, f, a in ((i, c[0], c[1]), (j, c[1], c[0])):
                                e = st[k]
                                e[0] += 1; e[2] += f; e[3] += a
                                e[1] += 3 if f > a else 1 if f == a else 0
                                e[4 if f > a else 5 if f == a else 6] += 1
                    res.append(row)
                if not played:
                    continue
                for k in range(n):                                          # 0x0072AFD3: points minus (flag & 3) * 3
                    st[k][1] -= (r[0x2A + k] & 3) * 3
                # order as the game sorts (0x0072BC49: points, goal difference, goals; 0x0072BD12 if word +0x10 is 1:
                # points, goals, goal difference)
                if struct.unpack_from('<h', r, 0x10)[0] == 1:
                    order = sorted(range(n), key=lambda k: (-st[k][1], -st[k][2], -(st[k][2] - st[k][3])))
                else:
                    order = sorted(range(n), key=lambda k: (-st[k][1], -(st[k][2] - st[k][3]), -st[k][2]))
                tname = [by_land.get((land, t), f'Verein {t}') for t in teams]
                name = LG_NAME.get(lg, '1. Liga') if land == 14 else '1. Liga'
                entry = {'teams': tname, 'res': res, 'tab': [[tname[k]] + st[k] for k in order]}
                # Flag 0x80: the game's own list of placements (block of 8640 bytes) puts this club last, whatever its
                # points (checked on six seasons of the Regionalliga in savegame 383). Meaning (licence withdrawn?) is a guess.
                zw = [tname[k] for k in range(n) if r[0x2A + k] & 0x80]
                abz = {tname[k]: (r[0x2A + k] & 3) * 3 for k in range(n) if r[0x2A + k] & 3}
                if zw:
                    entry['zw'] = zw
                if abz:
                    entry['abz'] = abz
                ligen.setdefault(f'{lg}', {'name': name, 'land': land, 's': {}})['s'][year - 10 + slot] = entry

    # ---- all-time tables: block 3 at 31500, 5 lands x 108 clubs x 24 bytes ----
    # Memory 0x00B131C4 + section * 0xA20, read by 0x00641D53; block 3 lies at 0x00B0B6B8 (see 0x00460D57). Per club three
    # sets of games, points, goals, goals against (int16): all, home, away. The screens (0x00460F97 all, 0x004613DB home,
    # 0x00461751 away, 0x00461AC7 relative) add the running season of the land's first league (0x0072B25B).
    # Running season: league object of 6760 bytes, +0x30 teams, +0x34 land, +0x52 club per team (int16),
    # +0xE4A + i * 96 + j * 4 result of team i at home against j, 0xFF = not played.
    # Checked on savegame 383: Gladbach 4883 games, 8718 points, 8970:5719; home 1573, 3106, 3067:1540 as on the screens.
    cur_tab = {}                                                  # land -> {club: 12 values} of the running season
    for b in blocks:
        if len(b) != 6760:
            continue
        n, _, land = struct.unpack_from('<3h', b, 0x30)
        if land in cur_tab or not 0 < n <= 24:                    # the first object of a land is its first league
            continue
        ids = struct.unpack_from(f'<{n}h', b, 0x52)
        st = {c: [0] * 12 for c in ids}
        for i in range(n):
            for j in range(n):
                c = b[0xE4A + i * 96 + j * 4: 0xE4A + i * 96 + j * 4 + 2]
                if i == j or c[0] == 255:
                    continue
                for club, f, a, o in ((ids[i], c[0], c[1], 4), (ids[j], c[1], c[0], 8)):
                    for base in (0, o):
                        e = st[club]
                        e[base] += 1; e[base + 1] += 3 if f > a else 1 if f == a else 0; e[base + 2] += f; e[base + 3] += a
        for club, e in st.items():                                # 0x007294B2: points deducted in the running season, in every view
            for base in (0, 4, 8):
                e[base + 1] -= (club_flags.get((land, club), 0) & 3) * 3
        cur_tab[land] = st
    komma = lambda x, d=2: f'{x:.{d}f}'.replace('.', ',')
    for k, land in enumerate(TITLE_LANDS):
        allrows = []
        for c in range(108):
            v = list(struct.unpack_from('<12h', titles, 31500 + k * 2592 + c * 24))
            add = cur_tab.get(land, {}).get(c)
            if add:
                v = [x + y for x, y in zip(v, add)]
            if any(v):
                allrows.append((by_land.get((land, c), f'Verein {c}'), v))
        for key, o, rel, text in (
                ('abs', 0, False, 'Wie im Spiel: der gespeicherte Stand plus die laufende Saison der ersten Liga. Gezählt werden nur Spiele in der höchsten Liga; der Startwert von 2019 ist schon enthalten.'),
                ('rel', 0, True, 'Dieselben Werte wie in der absoluten Tabelle, wie im Spiel nach Punkten je Spiel geordnet.'),
                ('heim', 4, False, 'Nur Heimspiele seit Spielbeginn 2019, einschließlich der laufenden Saison.'),
                ('ausw', 8, False, 'Nur Auswärtsspiele seit Spielbeginn 2019, einschließlich der laufenden Saison.')):
            sel = [(n, v[o:o + 4]) for n, v in allrows if v[o] > 0]
            sel.sort(key=lambda r: (-r[1][1], -(r[1][2] - r[1][3]), -r[1][2]))
            if rel:     # 0x0072B6C2: the absolute table re-ordered by points per game; equal quotients keep the absolute order
                sel.sort(key=lambda r: -r[1][1] / r[1][0])
            tab[f'ewigtab-{key}-{land}'] = {
                'cols': ['Pl.', 'Verein', 'Spiele', 'Punkte', 'Tore', 'Diff.', 'Punkte je Spiel'], 'num': [0, 2, 3, 4, 5, 6], 'hinweis': text,
                'rows': [[i + 1, n, g, p, f'{f}:{a}', f'{f - a:+d}', komma(p / g)] for i, (n, (g, p, f, a)) in enumerate(sel)]}
        # ---- "Tabellenführungen": block 3 at 47700, per land 108 clubs x (count, seasons) int16 ----
        # Memory 0x00B1710C + section * 0x1B0, read by 0x00642B23, shown by 0x00463A9B.
        rows = []
        for c in range(108):
            cnt, seas = struct.unpack_from('<2h', titles, 47700 + k * 432 + c * 4)
            if cnt:
                rows.append([by_land.get((land, c), f'Verein {c}'), cnt, seas])
        rows.sort(key=lambda r: (-r[1], r[2]))
        tab[f'fuehrungen-{land}'] = {'cols': ['Pl.', 'Verein', 'Tabellenführungen', 'Saisons'], 'num': [0, 2, 3],
                                     'hinweis': 'Anzahl der Spieltage an der Tabellenspitze der ersten Liga und Zahl der Saisons in dieser Liga, jeweils seit Spielbeginn 2019.',
                                     'rows': [[i + 1] + r for i, r in enumerate(rows)]}
    # ---- five-year ranking: block 1 at 1568, per land 36 bytes: land (int32), total and seven seasons (float) ----
    # Seasons: [0] six seasons ago, [1..5] the last five finished seasons (oldest first, their sum is the total),
    # [6] the running season. Checked on savegame 383: Germany 14.86, 14.54, 13.57, 13.14, 16.83 = 72.94 as on the screen;
    # in consecutive savegames the values move one place per season and only [6] changes within a season.
    b1, fj = blocks[bi3 - 2], []
    for j in range(80):
        o = 1568 + j * 36
        if len(b1) != 5520 or o + 36 > len(b1):
            break
        land = struct.unpack_from('<i', b1, o)[0]
        if not 0 < land < 256:
            break
        fj.append([land] + [round(x, 4) for x in struct.unpack_from('<8f', b1, o + 4)])
    sai = lambda y: f'{y % 100:02d}/{(y + 1) % 100:02d}'
    tab['fuenfjahres'] = {
        'cols': ['Pl.', 'Land'] + [sai(year - 5 + i) for i in range(5)] + ['Gesamt', f'laufend {sai(year)}'], 'num': [0, 2, 3, 4, 5, 6, 7, 8], 'team': [1],
        'hinweis': 'Die Wertung des Spiels: fünf abgeschlossene Saisons und ihre Summe. Die letzte Spalte ist die laufende Saison, die noch nicht mitzählt.',
        'rows': [[i + 1, ['L', r[0]]] + [komma(x) for x in r[3:8]] + [komma(r[1]), komma(r[8])] for i, r in enumerate(fj)]}

    # Privacy: the game lists the human managers as "last name, initial" (last name at +10 of the manager block).
    # The page and all merged lists show the first name only.
    priv = []                                                     # (first name, last name) of the human managers, never written out
    for i, b in enumerate(blocks[:-2]):
        if len(b) == 8504 and len(blocks[i + 2]) == 2132 and 65 <= b[0] <= 255:
            v, nn = (b[o:o + 20].split(b'\0')[0].decode('cp1252') for o in (0, 10))
            priv.append((v, nn))
            for key, t in tab.items():
                if key.startswith(('trainer-', 'rauswuerfe-')):
                    for r in t['rows']:
                        if r[1] == f'{nn}, {v[:1]}':
                            r[1] = v

    # Block of 82340 bytes, all offsets checked against the game screens of savegame 383 (docs/zuordnung-bildschirme.md):
    # "Nat. Meister" 51960, "Herbstmeister" 53160, cup finals 54360, Supercup 55960, top scorers 57560, international finals 60560,
    # World Cup 77722, European Championship 78204
    return {'clubs': clubs, 'raw_players': raw_players, 'names': names, 'member': member, 'best': best, 'dup': dup, 'year': year,
            'mgr': mgr, 'meister': season_table(51960), 'herbst': season_table(53160), 'wett': wett, 'by_land': by_land, 'tab': tab, 'ligen': ligen, 'fj': fj, 'priv': priv}


# Position codes as shown by the game screen "Supertransfers" (savegame 383, 16 rows compared): 3 IV, 4 LV, 5 RV, 6 RM, 7 LM,
# 8 DM, 9 OM, 10 ST. The older list in a3kader.py (6 DM, 7 LM, 8 RM) was a guess and is wrong.
POS_CODE = ['-', 'TW', 'LIB', 'IV', 'LV', 'RV', 'RM', 'LM', 'DM', 'OM', 'ST']


# alltimes.saq ("Fuer die Ewigkeit"): records across all careers of one installation, real dates. Entry offsets from the
# calls of 0x006D5D6A in anstoss3.exe; entries 11-15 and 17 have another layout (player records) and are skipped.
AT_OFF = [0, 58, 116, 174, 232, 278, 324, 370, 416, 462, 508, 558, 608, 660, 712, 764, 812, 864, 912, 960, 1006, 1056]
AT_NAME = {0: 'Höchster Heimsieg', 1: 'Höchster Auswärtssieg', 2: 'Höchste Heimniederlage', 3: 'Höchste Auswärtsniederlage',
           4: 'Beste Serie', 5: 'Schlechteste Serie', 6: 'Meiste Punkte', 7: 'Meiste Tore Saison', 8: 'Meiste Gegentore Saison',
           9: 'Minuten ohne Gegentor', 15: 'Höchste Werbeeinnahme', 17: 'Meiste Zuschauer', 18: 'Höchster Zuschauerschnitt',
           19: 'Eintrag 20 (Bedeutung offen)', 20: 'Eintrag 21 (Bedeutung offen)'}


def read_alltimes(path, by_land):
    return parse_alltimes(open(path, 'rb').read(), by_land)


def parse_alltimes(b, by_land):
    rows = []
    for k, title in AT_NAME.items():
        r = b[AT_OFF[k]:AT_OFF[k + 1]]
        pay = r[0x2C:]
        club = by_land.get((r[4], struct.unpack_from('<h', r, 6)[0]), '?')
        if k < 4:
            hg, ag = struct.unpack_from('<hh', pay, 4)
            opp = by_land.get((struct.unpack_from('<h', pay, 10)[0], struct.unpack_from('<h', pay, 12)[0]), '?')
            val = f'{hg}:{ag} ' + ('gegen ' if k in (0, 2) else 'in ') + opp
        elif k < 6:
            val = f'{pay[0]} Punkte aus {pay[1]} Spielen'
        elif k in (15, 17, 18):
            val = f'{struct.unpack_from("<i", pay, 0)[0]:,}'.replace(',', '.')
        elif k == 20:
            val = str(struct.unpack_from('<h', pay, 4)[0])
        else:
            val = str(struct.unpack_from('<h', pay, 0)[0])
        holder = (r[0x1A:0x1B] + b'. ' + r[0x1C:0x2C].split(b'\0')[0]).decode('cp1252', 'replace')
        rows.append([title, f'{r[0]}.{r[1]}.{struct.unpack_from("<h", r, 2)[0]}', holder, club, val])
    return rows


HONOURS = ['Meisterschaften', 'Pokalsiege', 'Finalteilnahmen', 'Liga-/Supercupsiege', 'Champions-League-Siege', 'Finalteilnahmen CL',
           'Europapokale', 'Finalteilnahmen EP', None, 'Europäische Supercups', 'Weltpokale', 'Sonstige Titel', None,
           'Europameisterschaften', 'Finalteilnahmen EM', 'Weltmeisterschaften', 'Finalteilnahmen WM', 'Trainer des Monats', 'Manager des Jahres']


def read_managers(blocks, by_land):
    """Human managers: main record (8504 bytes, name at 0) followed two blocks later by the honours record (2132 bytes).
    Field positions matched against the in-game screen "Trainererfolge" of both managers in savegame 383 (15.11.2026):
      main     0x1E land, 0x20 club, 0x24 level, 0x2E birth date, 0x124 manager years, 0x17C date joined, 0x180 years at club,
               0x21C/0x220 league games/wins, 0x224/0x226 cup, 0x228/0x22A European cup, 0x22C/0x22E internationals
               (the "wins" are inferred: together they give the 60 % shown in the game for both managers)
      honours  19 x int16 counters (order = HONOURS), [19] entries in list, [20] titles in total,
               0x2A list of (type, season index, land, club) x int16, season = 2018 + index,
               0x1BA dismissed, 0x1BC left, 0x1BE stations, 0x1C4 stations of 28 bytes:
               land, club, from, to, reason (3 dismissed, 1 contract ended, 0 current) ... +25 championships, +26 European cups, +24..27
    """
    out = []
    for i, b in enumerate(blocks[:-2]):
        if len(b) != 8504 or len(blocks[i + 2]) != 2132 or not (65 <= b[0] <= 255):
            continue
        h = blocks[i + 2]
        cnt = struct.unpack_from('<21h', h, 0)
        club = lambda land, c: by_land.get((land, c), f'Verein {c} (Land {land})')
        stations = []
        for k in range(struct.unpack_from('<h', h, 0x1BE)[0]):
            o = 0x1C4 + k * 28
            if o + 28 > len(h):
                break
            land, c = struct.unpack_from('<hh', h, o)
            stations.append({'club': club(land, c), 'von': [h[o + 4], h[o + 5], struct.unpack_from('<h', h, o + 6)[0]],
                             'bis': [h[o + 8], h[o + 9], struct.unpack_from('<h', h, o + 10)[0]], 'grund': h[o + 12],
                             'm': h[o + 24], 'pe': h[o + 25] + h[o + 26], 's': h[o + 27]})
        erfolge = []
        for k in range(max(0, min(cnt[19], 49))):
            t, s, land, c = struct.unpack_from('<4h', h, 0x2A + k * 8)
            erfolge.append([2018 + s, t, club(land, c)])
        g = lambda o: struct.unpack_from('<h', b, o)[0]
        out.append({
            'v': b[:10].split(b'\0')[0].decode('cp1252'), 'club': club(g(0x1E), g(0x20)), 'level': b[0x24],
            'geb': [b[0x2E], b[0x2F], g(0x30)], 'jahre': g(0x124), 'seit': [b[0x17C], b[0x17D], g(0x17E)], 'imverein': g(0x180),
            'spiele': [[struct.unpack_from('<i', b, 0x21C)[0], struct.unpack_from('<i', b, 0x220)[0]], [g(0x224), g(0x226)],
                       [g(0x228), g(0x22A)], [g(0x22C), g(0x22E)]],
            'ehr': [[HONOURS[k], cnt[k]] for k in range(19) if HONOURS[k]], 'titel': cnt[20],
            'entlassen': struct.unpack_from('<h', h, 0x1BA)[0], 'gegangen': struct.unpack_from('<h', h, 0x1BC)[0],
            'stationen': stations, 'erfolge': erfolge,
        })
    return out


def managers(save_file):
    """Header of the .an3 file: per human manager the strings first name, last name, club, country."""
    hdr = open(save_file, 'rb').read()[:0x1EF]
    s = [m.group().decode('cp1252') for m in re.finditer(rb'[\x20-\x7e\x80-\xff]{3,}', hdr)]
    return [{'v': s[i], 'club': s[i + 2]} for i in range(0, len(s) - 3, 4)]      # first name only


def main():
    src, tpl, out, label = sys.argv[1:5]
    save_file, hist_args, verlauf, rest = None, [], None, sys.argv[5:]
    alltimes_args = []
    while rest:
        a = rest.pop(0)
        if a == '--save':
            save_file = rest.pop(0)
        elif a == '--verlauf':                         # output of a3verlauf.py: all savegames, replaces --hist
            verlauf = json.load(open(rest.pop(0), encoding='utf-8'))
        elif a == '--alltimes':                        # alltimes.saq files as path=label, shown side by side
            while rest and not rest[0].startswith('--'):
                alltimes_args.append(rest.pop(0).rsplit('=', 1))
        elif a == '--hist':
            while rest and not rest[0].startswith('--'):
                hist_args.append(rest.pop(0).split('=', 1))
    S = read_save(src)
    names = S['names']

    def pname(r):
        v, n = struct.unpack_from('<HH', r, 0x19E)
        s = lambda i: names[i].decode('cp1252') if i < len(names) else '?'
        return (s(v) + ' ' + s(n)).strip()

    players = []
    for i, r in enumerate(S['raw_players']):
        year = struct.unpack_from('<h', r, 0x14A)[0]
        st = r[0x1FC]
        if year <= 0 or st == 0:
            continue
        players.append([pname(r), r[0x148], r[0x149], year, st, r[0x1FD], r[0x1FE], r[0x1FF], r[0x202], r[0x205],
                        S['member'].get(i, -1), struct.unpack_from('<H', r, 0x1A4)[0], struct.unpack_from('<H', r, 0x1A6)[0]])

    mgr = S['mgr'] or (managers(save_file) if save_file else [])
    watch = [m['club'] for m in mgr]
    hist = []
    for d, lab in hist_args + [[src, label]]:
        H = S if d == src else read_save(d)
        b = H['best'][0]
        top = sorted(H['clubs'], key=lambda c: -c['ss'])[:3]
        hist.append({
            'label': lab, 'year': H['year'], 'same': all(x == b for x in H['best']),
            'rec': {'s': b['s'], 'n': H['clubs'][b['c']]['n'] if b['c'] >= 0 else '?', 'sum': b['sum'], 'cnt': b['cnt']},
            'top': [[c['n'], c['ss'], c['sq']] for c in top],
            'clubs': {c['n']: {'t': c['t'], 'ss': c['ss'], 'sq': c['sq'], 'fin': [c['vs'], c['gw'], c['va'], c['an'], c['kr'], c['ba'], c['ag'][2] if c['ag'] else None]}
                      for c in H['clubs'] if c['n'] in watch},
        })
        print(f'  {lab}: etwa {H["year"]}, Rekord {hist[-1]["rec"]}, staerkster Kader {hist[-1]["top"][0]}')

    rebuilt = []
    if verlauf:
        hist = [{'label': f'Spielstand {s["nr"]}', 'year': s['year'],
                 'rec': None, 'top': s['top'][:1], 'mgr': s['mgr'],
                 'clubs': {n: {'t': v[0], 'ss': v[1], 'sq': v[2], 'fin': v[3]} for n, v in s['clubs'].items()
                           if n in watch or any(m.get('club') == n for m in s['mgr'])}} for s in verlauf['saves']]
        rebuilt = verlauf['best']
        sp = verlauf.get('spieler')
        if sp:                                         # eternal lists over all players of all savegames, no top-20 limit
            cols = ['Nr.', 'Name', 'Letzter Verein', 'Jahrgang', 'Spiele', 'Tore', 'Länderspiele', 'Zuletzt in Spielstand']
            note = ('Aus den Datensätzen aller Spieler in allen Spielständen, je Spieler der höchste Wert. Das Spiel zeigt nur die ersten 20. '
                    'Spieler, die nur in fehlenden Spielständen aktiv waren, fehlen oder stehen mit einem zu niedrigen Wert da.')
            for key, src in (('ewig-tore', 'tore'), ('ewig-spiele', 'spiele'), ('ewig-laender', 'laender')):
                S['tab'][key] = {'cols': cols, 'num': [0, 4, 5, 6, 7], 'hinweis': note,
                                 'rows': [[i + 1, r[0], r[1], r[2] or '', r[3], r[4], r[5], r[6] or ''] for i, r in enumerate(sp[src])]}
        for land in TITLE_LANDS:                       # goal records without the limit of 10: all season top scorers, by goals
            rows = sorted(verlauf.get('wett', {}).get(f'torschuetzen-{land}', []), key=lambda r: (-r[3], r[0]))
            if rows:
                S['tab'][f'torrekorde-{land}'] = {'cols': ['Saison', 'Name', 'Verein', 'Treffer'], 'num': [3], 'saison': [0],
                                                  'hinweis': 'Alle bekannten Torschützenkönige, nach Treffern geordnet. Das Spiel zeigt nur die besten zehn.',
                                                  'rows': [r[:4] for r in rows]}
        for key, rows in verlauf.get('rang', {}).items():      # best-of lists of the game without their limit of 20 / 60 rows
            if key in S['tab'] and len(rows) >= len(S['tab'][key]['rows']):
                was = len(S['tab'][key]['rows'])
                S['tab'][key]['rows'] = rows
                S['tab'][key]['hinweis'] = (f'Aus allen Spielständen zusammengeführt. Der letzte Spielstand selbst enthält {was} Einträge. '
                                            + RANG_TEXT.get(key.split('-')[0], '') + ' ' + S['tab'][key].get('hinweis', '')).strip()
        fjv = verlauf.get('fj')
        if fjv:                                        # five-year ranking: every season of every land ever seen
            seasons = sorted({int(s) for d in fjv.values() for s in d}, reverse=True)
            rows = []
            for s in seasons:
                vals = {int(l): d[str(s)] for l, d in fjv.items() if str(s) in d}
                best = max(vals, key=vals.get)
                rows.append([s] + [f'{vals[l]:.2f}'.replace('.', ',') if l in vals else '' for l in TITLE_LANDS]
                            + [['L', best], f'{vals[best]:.2f}'.replace('.', ',')])
            S['tab']['fuenfjahres-verlauf'] = {
                'cols': ['Saison', 'Deutschland', 'England', 'Frankreich', 'Italien', 'Spanien', 'Bestes Land', 'Wert'],
                'num': [1, 2, 3, 4, 5, 7], 'saison': [0], 'team': [6],
                'hinweis': 'Der Saisonwert je Land aus allen Spielständen. Das Spiel selbst hebt nur sieben Saisons auf. '
                           'Die Werte vor 2019/20 sind die Startwerte des Spiels. Saisons ohne Spielstand fehlen.',
                'rows': rows}
        for m in mgr:                                  # all titles known from any savegame, not only the newest 49
            m['alle'] = verlauf.get('mgr_titles', {}).get(m['v'])
    meister = verlauf['meister'] if verlauf else [[r[1], r[0]] + r[2:] + [0] for r in S['meister']]
    herbst = verlauf['herbst'] if verlauf else [[r[1], r[0]] + r[2:] + [0] for r in S['herbst']]
    wett = verlauf['wett'] if verlauf and 'wett' in verlauf else {k: [r + [0] for r in v] for k, v in S['wett'].items() if v}
    data = {'label': label, 'year': S['year'], 'clubs': S['clubs'], 'players': players, 'best': S['best'], 'hist': hist, 'mgr': mgr,
            'rebuilt': rebuilt, 'meister': meister, 'herbst': herbst, 'wett': wett, 'tab': S['tab'],
            'ligen': verlauf['ligen'] if verlauf and 'ligen' in verlauf else S['ligen'],
            'ewig': [{'label': lab, 'rows': read_alltimes(path, S['by_land'])} for path, lab in alltimes_args]}
    html = open(tpl, encoding='utf-8').read()
    if '/*DATEN*/' not in html:
        sys.exit('marker /*DATEN*/ missing in template')
    js = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    for v, nn in S['priv']:                            # privacy: every spelling of a human manager becomes the first name
        if len(nn) >= 3:
            for pat in (f'{v} {nn}', f'{v[:1]}. {nn}', f'{nn}, {v[:1]}.', f'{nn}, {v[:1]}'):
                js = js.replace(pat, v)
    html = html.replace('/*DATEN*/', js)
    open(out, 'w', encoding='utf-8').write(html)
    print(f'{len(S["clubs"])} Vereine, {len(players)} Spieler, davon {sum(1 for p in players if p[10] >= 0)} in Kadern, '
          f'{S["dup"]} doppelte Kadereintraege uebersprungen, {len(hist)} Spielstaende im Verlauf, {os.path.getsize(out)} Byte -> {out}')


if __name__ == '__main__':
    main()
