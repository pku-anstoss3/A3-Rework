# Befund: Lesbarkeit der Spieldaten (14.11.2026)

Untersucht an der GOG-Version (`D:\GOG Galaxy\Games\ANSTOSS 3`, Kopie unter `original/`).
Gesichertes und Vermutetes sind getrennt gekennzeichnet.

## Version

- `anstoss3.exe`: Dateiversion 1.1.0.0, im Programm die Strings „Version 1.40“ und „Patch1_4“
  → Patchstand vermutlich 1.40 (ob letzter offizieller Patch: ungeprüft).
- SHA-256 `anstoss3.exe`: `89B88EF522574098014E9F1E68448593E2A992A8EBD0318760E552C3B15F6B2A`
- `A3V13.txt`: Änderungslisten zu 1.10, 1.20 und der finalen Version.

## Dateiübersicht

| Ort | Inhalt | Lesbarkeit |
|---|---|---|
| `Data.a3\*.sav`, `Data.org\*.sav` (je 65) | Stammdaten: Länder, Vereine, Spieler, Ligen, Sponsoren … | Klartext |
| `saves\*.an3` (~4,2 MB) | Spielstände | Kopf lesbar, Rumpf komprimiert |
| `Archives\*.cpr`, `Data\*.cpr` | Grafik, Ton, Kommentare | Archiv, Kennung `BAUM` |
| `Data\*.tex`, `*.bmp`, `*.tga`, `Palette\*.pal` | Texturen, Grafiken | Standard- bzw. eigene Bildformate |
| `texte\*.txt`, `REST.SAV` | Texte | Klartext Windows-1252 |
| `texte\Interv.saq`, `alltimes.saq` | Interviews, Rekordliste (vermutet) | binär, unkomprimiert |
| `deb\*.rh`, `MeineDialoge.rch` | Ressourcen-Header (IDs für Texte, Grafiken, Dialoge) | Klartext |
| `anstoss3.exe`, `activesim.dll`, `Archiver.dll`, … | Programm | – |

`Data.a3` und `Data.org` unterscheiden sich in `LandDeut.sav` nur in 10 Zeilen (jeweils +1).
Vermutung: `Data.a3` ist der vom Editor bearbeitete und vom Spiel gelesene Satz, `Data.org` das Original.

## Stammdaten (`*.sav` in `Data.a3`)

- Windows-1252, CRLF, eine Zeile pro Wert, erste Zeile `17373592`.
- Abschnitte `%SECT%NAME` … `%ENDSECT%NAME`, verschachtelt (VEREIN enthält TRAINER, MANAGER …).
- `LandDeut.sav`: 108 VEREIN, 2469 SPIELER, 108 STADION, 169 TRAINER, 148 MANAGER, 40 SCHIRI, 40 SPONSOR, 40 AMATEURV, 20 PROMI.
- Felder ohne Bezeichnung, Bedeutung nur über Position. Ein VEREIN-Block umfasst 74 Zeilen bis zum ersten SPIELER.
- Beispiel „Spfr. M\`Gladbach“: `%SECT%VEREIN` bei 0x008A68, Name bei 0x008A7A, Zahlenfelder ab 0x008B40
  (`85 | 0 | 11 | 11 | 80 | 5 | 0 | 0 | -200 | …`), später Präsident „Medops Wilfried“ und das Datum 17.08.1900 (vermutlich Gründung).
- Laut Editor-Hilfe kommen auch die vor Spielbeginn gewonnenen Titel aus den Stammdaten (Trophäenhalle).

## Spielstände (`*.an3`)

- 0x000–0x1FF: Kopf mit festen, nullterminierten Feldern (Manager-Vor- und Nachname, Verein, Land; zweiter Manager ab 0x7E).
- Ab 0x200: komprimiert, Verfahren unbekannt. Belege:
  - Entropie gesamt ~7,3 Bit/Byte, 1-KB-Blöcke meist 6–7,5 (Verschlüsselung läge bei ~8).
  - lzma schrumpft den Rumpf noch auf 74 % → nicht verschlüsselt.
  - Auffällig häufige Einzelbit-Bytes (0x80, 0x40, 0x20, 0x10 …) → vermutlich Flag-Bits eines LZ-Verfahrens.
  - Keine Namen außerhalb des Kopfs, auch nicht per XOR, Verschiebung oder UTF-16.
  - zlib und klassisches LZSS (Okumura-Varianten) passen nicht.
  - `Autos.an3` und `Karriere97.an3` (eine Minute auseinander, gleich groß) unterscheiden sich nur an sechs eng begrenzten Stellen
    und sind danach wieder identisch → kein durchgehender Huffman- oder zlib-Strom; dazwischen stehen unkomprimierte int32-Werte.
  - Vermutung: byteweises LZ-Verfahren, Eigenentwicklung, Entpackroutine vermutlich in `Archiver.dll` oder der exe.
- Die `.cpr`-Kennung `BAUM` kommt im Spielstand nicht vor.

## Folgen für die Überarbeitung

- Stammdaten lassen sich ohne Programmeingriff ändern (wirken vermutlich nur bei neuer Karriere).
- Laufende Karrieredaten und Statistiken sind erst nach Entschlüsselung des Spielstandformats lesbar.
- Spiellogik, Berechnung und Anzeige liegen in `anstoss3.exe` (Simulation vermutlich in `activesim.dll`);
  grundsätzliche Fehler sind nur dort behebbar: Byte-Patches, eigene Hook-DLL oder Neuimplementierung.
