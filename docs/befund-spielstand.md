# Befund: Spielstandformat `.an3` (15.11.2026)

Grundlage: Disassembly von `original/anstoss3.exe` (Patch 1.40, Build 02.07.2003, VC++ 6/MFC) mit `dumpbin`.
Getestet an `original/saves/Karriere109.an3`. Werkzeuge: `tools/a3lz.py`, `tools/a3save.py`.

## Gesichert (im Code gelesen und am Spielstand bestätigt)

- **Autosave** (0x006ECFEB): löscht `saves/Auto2.`, benennt `Auto1.`→`Auto2.` und `Autos.`→`Auto1.` um, ruft dann die Speicherroutine 0x006ED31E auf.
- **Blockschreiber** (0x006ED175): packt einen Puffer über 0x0075EADA (Packer 0x007D2AF0) und schreibt `int32 gepackte_Länge` + gepackte Daten per `fwrite`.
- **Spieler** (0x006ED1FB): Spieler-Array bei 0x00C02550, 852 Byte (0x354) je Spieler, 17006 Einträge.
  Serialisiert in Paketen zu 1000 Spielern in einen 852 000-Byte-Puffer, je Paket ein Block.
- **Entpacker** (0x0075EB0B → 0x007D30F0, handgeschriebener Assembler), Format eines gepackten Blocks:
  - `int32 n`: 0 = leer, < 0 = −n Bytes ungepackt, > 0 = n Bytes entpackt, danach Bitstrom.
  - Bitstrom aus 32-Bit-Wörtern (little endian), Bits LSB zuerst.
  - Flag 0 → Literal (8 Bit). Flag 1 → Verweis: 3 Bit Auswahl, Distanz = read(Auswahl+1) + {0,2,6,14,30,62,126,254}[Auswahl], Quelle = Ziel − Distanz − 1;
    Länge = 2 + Summe von Feldern mit 2, 3, 4 … Bit, solange ein Feld alle Bits gesetzt hat.
  - Tabellen statisch in `.data` (0x008B3E78, 0x008B3EB8, 0x008B3EDC).
- **Dateiaufbau**: 0x000–0x1EE ungepackter Kopf, ab 0x1EF Blöcke `[int32 Länge][gepackter Block]`, dazwischen wenige ungepackte Felder.
  `Karriere109.an3`: 4570 Blöcke, entpackt 19,6 MB, 8 ungepackte Lücken (4 × 24 Byte bei 0x1DDCF ff., sowie 10 808, 2, 234 und 432 Byte weiter hinten – Inhalt noch offen).
- **Vereine**: 609 Datensätze zu je 2416 Byte, je ein Block. Beispiel `analyse/save109/block_301.bin`:

  | Offset | Typ | Wert | Bedeutung |
  |---|---|---|---|
  | 0x000 | char[20] | `Borussia M'gladbach` | Name |
  | 0x014 / 0x018 | char[4] | `BMG` | Kürzel |
  | 0x04A | char[] | `Fohlen` | Spitzname |
  | 0x2EE | int16 | 193 | unbekannt, identisch mit Stammdatenfeld (Zeile 7558 in `LandDeut.sav`) |
  | 0x2F0 | int16 | 153 | unbekannt, identisch mit Stammdatenfeld (Zeile 7559) |
  | 0x900 / 0x901 / 0x902 | u8 / u8 / int16 | 1 / 8 / 1900 | Gründungsdatum 01.08.1900 |

## Vermutet (nicht geprüft)

- Ungepackte Blöcke (n < 0) akzeptiert der Entpacker. Geänderte Spielstände ließen sich daher ohne eigenen Packer schreiben – im Spiel noch nicht getestet.
- 0x8F0 im Vereinssatz: Ganzzahlen in Millionenhöhe, möglicherweise Geldwerte.
- Die Stammdaten in `Data.a3` werden nur beim Start einer neuen Karriere gelesen.

## Offen

- Bedeutung der Felder im Vereins- (2416 Byte) und Spielersatz (852 Byte); Weg: Serialisierungsroutinen in der exe (z. B. 0x007CFFF4 für Spieler).
- Inhalt der ungepackten Lücken und der übrigen Blocktypen (Größen 52, 208, 264, 624, 948 … Byte).
