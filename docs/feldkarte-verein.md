# Feldkarte Verein (15.11.2026)

Hergeleitet aus `anstoss3.exe` 1.40:
- Stammdaten-Lader `VEREIN` (0x0068CDFA): Textzeile → Zwischen-Datensatz (Import).
- Umkopierroutine (0x0068D411): Import → Vereinsobjekt im Speicher.
- Spielstand: Vereinsobjekt ab Objekt-Offset 0x20, 2416 Byte je Verein → **Spielstand-Offset = Objekt-Offset − 0x20**.
- Beschriftungen aus dem Vereinsdialog von `Editor.exe` (Dialog 353).

Geprüft an `Karriere109.an3`, Verein Borussia M'gladbach. Werkzeuge: `tools/map_loader.py`, `tools/map_convert.py`,
`tools/verein_feldkarte.py`, `tools/pe_dialogs.py`.

Sicherheit: **G** = im Code und an Daten bestätigt, **V** = Vermutung.

## Vereinsdatensatz im Spielstand (2416 Byte)

| Offset | Typ | Stammdaten-Zeile | Bedeutung | Sicherheit |
|---|---|---|---|---|
| 0x000 | char[20] | Name | Vereinsname | G |
| 0x014 | char[4] | Kürzel | Kürzel (`BMG`) | G |
| 0x018 | char[] | 5 | Anfeuerungsname für Fangesänge (`Borussia`, `BVB`) | V |
| 0x04A | char[] | 6 | Fanbezeichnung/Spitzname (`Fohlen`) | V |
| 0x0F2 | int16 | 52 | unbekannt | – |
| 0x0F4–0x0FB | u8 × 8 | 7–14 | unbekannt, im Spiel verändert | – |
| 0x0FC–0x106 | u8 | 16–23 | unbekannt (Flags/Stufen) | – |
| 0x10D | u8 | 2 | Land-/Ligacode (14 bei allen deutschen Vereinen) | V |
| 0x2EE | int16 | 25 | unbekannt, Wert unverändert 193 | G (Ort) |
| 0x2F0 | int16 | 26 | unbekannt, Wert unverändert 153 | G (Ort) |
| 0x468 | int64 | 15 „Guthaben bei Spielbeginn“ | Kontostand; beim Laden auf −2000…1500 begrenzt und mit Faktor (0x00A3B3BC) multipliziert | V (stark) |
| 0x468 / 0x470 | int64 / int64 | – | 0x468 = „Vereinsvermögen am Anfang der Saison“ des Bilanz-Bildschirms; 0x470 = 0x468 − Kredite + Anlagen, beim Saisonwechsel geschrieben. Die frühere Deutung „Konto ohne / mit Geldanlagen“ ist nicht gesichert, siehe `befund-finanzen.md` (16.11.2026) | G (Rechnung), V (Bedeutung) |
| 0x480 | Tabelle | – | Einnahmen und Ausgaben der laufenden Saison (Summe `0x0061FC81`) | G (Ort) |
| 0x570 | 8 × 24 B | – | Kredite: int64 Betrag, Byte +0x0F Bit 0 = aktiv | G |
| 0x630 | 6 × 24 B | – | Geldanlagen: int64 eingezahlt, int64 aktueller Wert, int16 +0x10, Byte +0x13 = 1 solange aktiv, int16 +0x14 | G (Summe), V (Einzelfelder) |
| 0x6C8 / 0x6D0 | int64 / int64 | – | Transfereinnahmen / Transferausgaben der laufenden Saison (gehen in den Gewinn ein, `befund-finanzen.md`) | G |
| 0x748 | int16 | – | Dispokreditrahmen in Einheiten von 100 000 | G |
| 0x839 / 0x83A | u8 / u8 | – | zwei Ausbaustufen mit festen Saisonkosten (Tabellen `0x0089E450` / `0x0089E458`), Bedeutung nicht zugeordnet | G (Rechnung) |
| 0x850–0x858 | u8 | 27–34 | unbekannt | – |
| 0x85C–0x868 | int32 × 4 | 35–38 | unbekannt, im Spiel gewachsen (2172 → 2946 …); zusätzlich als int16 in eine Verlaufstabelle (0x00B131C4) kopiert | G (Ort) |
| 0x8D4 | Datum | 41 | Geburtsdatum Präsident | V (stark) |
| 0x904 | u8 | – | Bit 0 = Aktiengesellschaft (`0x0069D71D`) | G |
| 0x900 | Datum (u8 Tag, u8 Monat, int16 Jahr) | 50 „Gründungsjahr“ | Gründungsdatum (01.08.1900) | G |
| 0x904 | int32 Bits | 42, 49 | Bit 0 aus Zeile 42, Bit 1 gesetzt wenn Zeile 49 ≠ 2 | G (Ort) |

## Titel (Trophäenhalle)

Die sechs Titelzähler der Stammdaten (Zeilen 43–48, im Editor: Meisterschaft, Pokal, Ligapokal/Supercup,
europ. Verbandspokal, Pokal der Meister, Weltpokal) stehen **nicht** im Vereinsdatensatz.
Die Umkopierroutine verteilt sie auf globale Tabellen, die als ein Block von 82 340 Byte gespeichert werden
(Speicherbereich ab 0x00B0B6B8; in `Karriere109.an3` Block 3):

| Tabelle | Speicher | Offset im Block | Inhalt |
|---|---|---|---|
| Meisterschaften | 0x00B1B860 | 0x101A8 | Zeile 43 |
| Pokal | 0x00B1BC98 | 0x105E0 | Zeile 44 |
| Europapokale | 0x00B1C0D0 | 0x10A18 | **Summe** aus Zeile 46 und 47 |

Je Tabelle int16, Index = Land × 216 + Verein × 2. Verein = Position im Vereins-Array des Spielstands.
Am Spielstand: Bayern 33 / 22 / 9, Dortmund 8 / 6 / 2, Gladbach 18 / 10 / 8 (Meister / Pokal / Europa). Land 0 = Deutschland.

- Ligapokal/Supercup (Zeile 45) und Weltpokal (Zeile 48) gehen nur in einen lokalen Datensatz, der an 0x0064067F übergeben wird – Verbleib offen.
- Dass die Zeilenreihenfolge 43–48 der Dialogreihenfolge im Editor entspricht, ist V.
- Die Europapokal-Tabelle führt Verbandspokal und Pokal der Meister zusammen. Ob die Anzeige das wieder trennt, ist offen – möglicher Ansatz für falsche Pokalzahlen (V).

### Fortschreibung im Spiel (G, Aufrufkette noch nicht ausgewertet)

| Tabelle | +1-Routine | Aufgerufen aus |
|---|---|---|
| Meisterschaften | 0x00634A1D (über 0x00634A8E, 0x0071D54B) | 0x0071D3C0, 0x0071D4F2 |
| Pokal | 0x00634B32 (über 0x00634BA3) | 4 Stellen in 0x006CE00E |
| Europapokale | 0x00634C47 (über 0x00634CB8) | 2 Stellen in 0x0041EF40, 2 in 0x00421D45 |

Lesen für die Anzeige über 0x0064260D / 0x00642697 / 0x00642721 (kopieren eine Landeszeile, im Netzwerkspiel per Nachricht 0x91).
Stand `Karriere383.an3`: Gladbach 47 / 25 / 30, Bayern 33 / 22 / 11.

## Offen

- Bedeutung der mit „unbekannt“ markierten Felder: über den Schreibweg des Editors (welches Dialogfeld welche Zeile schreibt).
- Spieler: Lader `SPIELER` (0x0068C257) ist kartiert (`analyse/spieler_map.txt`), die Umkopierroutine noch nicht.
