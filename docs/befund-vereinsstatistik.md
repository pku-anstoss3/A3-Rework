# Befund: Vereinsliste „meiste Spiele“ friert nach 50 Spielern ein (16.11.2026)

Anlass: Forum anstoss-juenger.de (topics 796, 1150): „Meiste Spiele für den Verein zählt nur die ersten 50 eingesetzten
Spieler“, „ewige Einsätze im eigenen Verein hören nach unter 20 Jahren auf“.
**G** = im Code gelesen und an Spielständen belegt, **V** = Vermutung. Kein Patch gebaut.

## Daten (G)
Je menschlichem Manager gibt es im Spielstand einen Block mit 10528 Byte (Speicher `0x00A58078 + (Nr − 1) × 0x2940`, Daten ab
+0x20). Darin zwei Listen mit je 50 Einträgen zu 22 Byte, beide werden beim Vereinswechsel des Managers geleert:

| Liste | Blockoffset | Lesen / Schreiben | Sortiert nach | Inhalt je Eintrag (int16) |
|---|---|---|---|---|
| 1 „Tore“ | 0x1590 | `0x00633115` / `0x006331E6` | Tore | +0 Spieler-Nr., +2/+4 Name, +6 Jahrgang, +8 Kennzeichen „im Verein“, +0xA Tore, +0x10 Spiele |
| 2 „Spiele“ | 0x19DC | `0x00633291` / `0x00633384` | Spiele | +0 … +8 wie oben, +0xA Spiele gesamt, +0xC/+0xE/+0x10 Spiele je Wettbewerbsart, +0x12 weiterer Zähler |

## Wie Liste 2 geführt wird (G)
Nach jedem Spiel eines menschlich geführten Vereins (`0x00744654`) wird für jeden eingesetzten Spieler `0x007441F4` aufgerufen:
1. Steht der Spieler (Nummer + Jahrgang) schon in der Liste: Zähler erhöhen, Kennzeichen = 1.
2. Sonst einen Platz suchen: zuerst einen leeren; ist die Liste voll, von unten her (Platz 50 bis 26) den ersten Eintrag,
   dessen **Kennzeichen 0** ist (Spieler nicht mehr im Verein). Die oberen 25 werden nie ersetzt.
3. Danach wird die Liste nach Spielen sortiert und zurückgeschrieben.

## Der Fehler (G)
Das Kennzeichen wird beim Zugang auf 1 gesetzt – für Liste 1 in `0x00742AF1`, für Liste 2 in `0x007448C5` (beide aus
`0x005DBEFC`). Beim Abgang (`0x005DBEF2` → `0x007429A0`) wird es **nur in Liste 1** auf 0 gesetzt. Für Liste 2 gibt es keine
Stelle im Programm, die das Kennzeichen je wieder löscht (einzige Schreiber: `0x007448B7`, `0x00744978`, `0x00744BC2`).
Sobald 50 Spieler eingetragen sind, gilt deshalb jeder Eintrag für immer als „im Verein“, und Schritt 2 findet nie einen Platz.

## Beleg an den Spielständen
Manager A, Borussia M'gladbach (seit 2029), Verlauf über 97 Spielstände + 383:
- Liste 2 füllt sich bis 2033 auf 50 Einträge (Jahrgänge 1994–2014). Danach ändert sich ihre Besetzung **nie wieder**:
  2047 und 2113 stehen dieselben 50 Spieler darin, Höchstwert 513 Spiele.
- 2113 haben alle 50 Einträge das Kennzeichen 1, obwohl die Spieler seit Jahrzehnten weg sind.
- Liste 1 arbeitet: 25 ehemalige Spieler mit Kennzeichen 0, 25 aktuelle mit 1; ihr Höchstwert bei den Spielen ist 684
  (Sörloth), der in Liste 2 fehlt – ebenso alle anderen Spieler nach 2033.
Bei Manager B (KFC Uerdingen) dasselbe Bild.

## Stand des Patches (16.11.2026)
`vereinsliste-spiele` steht in `tools/a3patch.py`; die neuen Bytes erzeugt `tools/asm_vereinsliste.py` (Sprungweiten werden
dort berechnet, 183 Byte Code + 87 × nop statt 270 Byte). Gebaut in `build/kandidat/anstoss3.exe` (SHA-256 `74D26348…`),
mit `dumpbin` Befehl für Befehl gegengelesen; einziges Sprungziel von außen ist der Anfang `0x007447B1`. Benutzt nur
`esi`/`edi` (von der Routine gesichert) und `eax`/`ecx`/`edx`. Kader des Vereinsobjekts: Anzahl +0xE2 (= Kadergröße des
Vereinssatzes, `0x006361E8`), Zeiger +0xB50. **Im Spiel ungetestet**, ein Emulator stand zum Vorabtest nicht zur Verfügung.
Test ohne Saisonwechsel: zwei Pflichtspiele spielen, speichern. Nach dem ersten Spiel tragen nur noch Kaderspieler das
Kennzeichen, ab dem zweiten rücken eingesetzte Spieler in die Liste.

## Im Spiel bestätigt (16.11.2026, `saves/patchtest/test4.an3` → `test5.an3`, exe `74D26348…`)
Der Nutzer hat einige Spieltage gespielt, kein Absturz.
- Manager A: vorher 50 Einträge, alle mit Kennzeichen 1 (keiner davon im Kader). Nachher tragen 16 Einträge das Kennzeichen,
  alle 16 sind Kaderspieler. 16 neue Einträge (u. a. Sörloth, Kühnel, Lucumí mit 1–2 Spielen), ersetzt wurden die 16
  untersten Altlasten (0–15 Spiele, Jahrgänge 1994–2014). Die oberen Plätze sind unverändert (513, 328, 270 …), die Liste ist
  absteigend sortiert.
- Manager B: 13 neue Einträge, 13 Altlasten ersetzt, Kennzeichen nur noch bei den 13 Kaderspielern.
- Ein neuer Eintrag steht mit 0 Spielen da: Er kam über den zweiten Zählweg (`0x00744A69`, erhöht nur +0x12) – altes Verhalten.
- Wie erwartet beginnen die Neuen bei 1; die Tore-Liste kennt ihre wahren Einsätze (Sörloth 702).

## Korrektur im Einzelnen
Ein Löschen nur beim Abgang würde alte Spielstände nicht heilen (die 50 Altlasten gehen nie mehr „ab“). Sauberer:
im Spielabschluss `0x00744654` vor dem Sortieren alle Kennzeichen der Liste 2 aus dem aktuellen Kader neu setzen
(1 = Spieler steht im Kader, sonst 0). Platz dafür entsteht, wenn die sehr ausführlich geschriebene Sortierschleife
(`0x007447BD`–`0x007448AB`, 237 Byte) kürzer neu geschrieben wird. Das ändert keine Spielregel: Das Kennzeichen bekommt nur
die Bedeutung, die es in Liste 1 schon hat.

Was der Patch nicht kann:
- Verlorene Einsätze der Jahre 2033–2113 kommen nicht zurück (sie wurden nie gezählt).
- Spieler, die schon lange im Verein sind, beginnen in Liste 2 bei 1 (Sörloth stünde zunächst mit 1 statt 684 da).
  Liste 1 kennt ihre Spiele; ein einmaliges Nachtragen aus Liste 1 wäre ein Eingriff in den Spielstand (Werkzeug), kein exe-Patch.

## Nicht geprüft (weitere Forumsmeldungen)
- „Zähler laufen bei 127 bzw. 255 über“: Im Spielabschluss werden mehrere Byte-Zähler je Spieler erhöht (Arbeitssatz +0x54,
  +0x55, +0x56, +0x59, +0xC2); welcher davon in welcher Statistik überläuft, ist nicht zugeordnet.
- „Rekordablösen fehlen“: an den Daten nicht prüfbar, weil die tatsächlichen Transfers nicht bekannt sind (die
  zusammengeführte Supertransfer-Liste über 97 Spielstände ist in sich widerspruchsfrei).
- „Torjäger Plus“ / „Schirilieblinge“ nur Nullen: nicht untersucht.
