# Feldkarte Spieler (15.11.2026)

Hergeleitet aus `anstoss3.exe` 1.40:
- Stammdaten-Lader `SPIELER` (0x0068C257): Textzeile → Zwischen-Datensatz (Import).
- Umkopierroutine (0x0068C903): Import → Spielerobjekt (Array bei 0x00C02550, 852 Byte Abstand).
- Spielstand-Serialisierung (0x007CFFF4): kopiert ab Objekt-Offset 0x20 → **Spielstand-Offset = Objekt-Offset − 0x20**.
- Spielstand: 17 Blöcke zu 852 000 Byte, je 1000 Spieler à **820 Byte (0x334)**, Rest des Blocks leer.
- Beschriftungen aus den Spielerdialogen von `Editor.exe` (Dialoge 159, 160, 161, 217, 346).

Geprüft an `Karriere109.an3`: 17 000 belegte Sätze, Wertebereiche je Feld ausgezählt.
Sicherheit: **G** = im Code gelesen, **V** = Vermutung aus Wertebereich und Editor-Beschriftung.

## Spielersatz im Spielstand (820 Byte)

| Offset | Typ | Stammdaten-Zeile | Herkunft im Code | Bedeutung | Sicherheit |
|---|---|---|---|---|---|
| 0x144 | u8 | – | beim Laden 0 | unbekannt | G (Ort) |
| 0x146 | int16 | – | beim Laden −1 | unbekannt (Verweis, −1 = keiner) | G (Ort) |
| 0x148 | Datum | 22 | Import 0x7A | Geburtsdatum (u8 Tag, u8 Monat, int16 Jahr) | G |
| 0x190 | int32 Bits | 21 | Bit 16 bei Zeile 21 = 2, Bit 10 bei Zeile 21 = 3 | Flags | G (Ort) |
| 0x194 | int32 Bits | 16 | Bit 31, wenn Zeile 16 ≠ 0 | Flags | G (Ort) |
| 0x19E | u16 | 2 | Namensindex aus Import 0x02 (19 Zeichen) | Vorname (Index in Namenstabelle) | V |
| 0x1A0 | u16 | 1 | Namensindex aus Import 0x16 (29 Zeichen) | Nachname (Index) | V |
| 0x1A2 | u16 | 17 | Namensindex aus Import 0x34 | Künstlername (Index) | V |
| 0x1A4 | u16 Bits | 12 | max. 3 Bits | Stärken: 16 Fähigkeiten (Kopfball, Zweikampf, Schnelligkeit, Schusskraft, Elfmeter, Freistöße, Flanken, Torinstinkt, Laufstärke, Technik, Ballzauberer, Spielmacher, Viererkette, Spielübersicht, Ball halten, Dribbling; Torwart eigene Liste) | V (stark) |
| 0x1A6 | u16 Bits | 13 | max. 3 Bits, nie zugleich Stärke | Schwächen, gleiche Liste | V (stark) |
| 0x1A8 | u16 Bits | 14 (Wert / 2) | ±1000 auf 0x1AE/0x1B0 bei Bit 1/2 | Eigenschaften (Kämpfernatur, Trainingsweltmeister, trainingsfaul, Treter …) | V (stark) |
| 0x1AA | u16 Bits | 15 (Wert / 2) | ±1000 auf 0x1AE/0x1B0 bei Bit 0, 5, 8 | Charakter (Führungsperson, Hitzkopf, Frohnatur …) | V (stark) |
| 0x1AC | u16 | 26 (Wert / 2) | Import 0x70 | unbekannt, im Spielstand überall 0 | G (Ort) |
| 0x1AE | int16 | – | 3500 + Zufall(1600), ±1000 je nach Eigenschaft/Charakter | verdeckter Wert, vermutlich Trainingseinstellung | V |
| 0x1B0 | int16 | – | 6000 + Zufall(2100), ±1000 wie oben | verdeckter Wert | V |
| 0x1F8 | u16 Bits | 20 | 1 << (Zeile 20 − 1) | unbekannt | G (Ort) |
| 0x1FA | u8 | 4, 30 | Zeile 4 + (Zeile 30 & 0xF) << 4 | zwei 4-Bit-Werte, vermutlich Aussehen | V |
| 0x1FB | u8 | 5, 30 | Zeile 5 + (Zeile 30 >> 16) << 4 | zwei 4-Bit-Werte, vermutlich Aussehen | V |
| 0x1FC | u8 | 7 | beim Laden auf 1…12 begrenzt | Stärke (im Spiel bis 13) | V (stark) |
| 0x1FD | u8 | 9 | 1…10, über Tabelle 0x008A3D9B umgesetzt | Hauptposition | V (stark) |
| 0x1FE | u8 | 10 | wie oben, ≠ Hauptposition | Nebenposition 1 | V (stark) |
| 0x1FF | u8 | 11 | wie oben, ≠ beiden anderen | Nebenposition 2 | V (stark) |
| 0x200 / 0x201 | u8 | – | beim Laden 0 | unbekannt | G (Ort) |
| 0x202 | u8 | 19 | Import 0x67 | Talent (0…4, fünf Stufen) | V (stark) |
| 0x203 | u8 | 29 | Import 0x74 | unbekannt (0…48) | G (Ort) |
| 0x205 | u8 | 8 | Import 0x68, Bit 7 → Flag 0x10 in 0x262 | Nationalität (14 = Deutschland, wie Vereins-Landcode) | V (stark) |
| 0x206 | u8 | 24 | Import 0x69 | unbekannt, fast immer 0 | G (Ort) |
| 0x207 | u8 | (8) | Tabelle 0x0089DE50[Nationalität] | aus Nationalität abgeleitet (Kontinent/EU?) | V |
| 0x24F | u8 Bits | 25 | Bit 1 aus Zeile 25 | Flags | G (Ort) |
| 0x25D | u8 | 23 | Import 0x6E | 0…10, vermutlich Konstanz | V |
| 0x262 | u8 Bits | 18, 21, 25, 27, 28 | Zeile 21 (Wert), Zeile 18 << 2, Bit 7/6/5/4 aus Zeilen 25/28/27/Nationalität | Flags | G (Ort) |
| 0x26F–0x276 | u8 × 8 | – | beim Laden 100 | Teilwerte der Motivation (0–120 gespeichert, 0–100 angezeigt): 0x26F Trainer (G), 0x270 Team, 0x271 Verein, 0x272 Presse (V stark), 0x273 Privat, 0x274 Ablenk., 0x275 Angebote (V, aus der Reihenfolge der Spielerdetails); 0x276 offen. Siehe `befund-notenschnitt.md` | G / V |
| 0x2CB | u8 × 46 | – | – | je Spieltag zwei Halbbytes (weitere Balken der Seite „Noten“) | G (Ort) |
| 0x2F9 | u8 × 46 | – | – | je Spieltag: Bits 6–7 Einsatz (0x40 durchgespielt, 0x80 eingewechselt, 0xC0 ausgewechselt), Bits 2–5 Note × 2 (0 = keine Note), Bits 0–1 Karte; wird beim Saisonwechsel nicht gelöscht | G |

Stammdaten-Zeilen gezählt ab der ersten Zeile nach `%SECT%SPIELER` (1 = Nachname, 2 = Vorname).
Zeile 3 und 6 (bei `Fist, Frank` 0 und 26 = Alter) liest der Lader, verwirft sie aber.

## Offen

- **Namenstabelle**: Die Namensindizes zeigen auf ein Objekt bei 0x00BA0CC8. In welchem Spielstandblock es liegt, ist noch nicht ermittelt.
  Ein Block mit Vornamen-Pool (149 176 Byte, `Der Teamchef`, `Alexander` …) ist gefunden, aber nicht zugeordnet.
- Die Stammdaten in `Data.a3` (GOG-Ordner) haben 33 Werte je Spieler, der Lader liest 30. Ob die übrigen 3 ignoriert werden, ist ungeprüft.
- Felder 0x000–0x143 und 0x208–0x333 werden beim Laden der Stammdaten nicht gesetzt: Laufzeitwerte (Vertrag, Gehalt, Statistik, Verletzungen …).
  Die lassen sich nur über die Stellen im Spiel kartieren, die sie lesen oder schreiben.
