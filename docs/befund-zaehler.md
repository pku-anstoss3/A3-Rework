# Befund: Zähler-Überlauf und eingefrorene Statistiken (16.11.2026)

Anlass: Forum anstoss-juenger.de, topic 796 („Manche Statistiken funktionieren … nur bis zu einem Wert von 127 (bzw. 255) und
fangen dann wieder bei 0 an“, ohne Angabe welche). Geprüft an allen 97 Spielständen in `analyse/scan` (2019–2047, 2113) und den
Test-Spielständen in `analyse/scan_test`. **G** = im Code gelesen und an Spielständen belegt, **V** = Vermutung.
Kein Patch gebaut.

## Methode
1. Feste Blöcke 0–3763 (in allen Spielständen gleich groß, ohne die Spielerblöcke 279–295): je Byte-Stelle über die 96
   aufeinanderfolgenden Spielstände 1–97 Anstiege, Abnahmen und Rücksprünge (≥ 150 → < 100, Nachbarbyte unverändert) gezählt;
   zusätzlich Stand 97 gegen Stand 383. Skripte im Scratchpad: `zaehler1.py` (Statistik → `zaehler1.npz`), `zaehler3.py`.
2. Spielersätze (820 B): dasselbe je Spalte, nur für Plätze mit gleichem Namen und Geburtsdatum in beiden Spielständen
   (`zaehler6.py`).
3. Eingefrorene Listen: Bereiche der Blöcke 0–296, die bis Stand 97 mindestens fünfmal geändert wurden und zwischen Stand 97
   und 383 (66 Saisons) gleich blieben (`frozen1.py`).

## Fund: „Wann trafen die Clubs?“ läuft bei 255 über (G)
- Daten: Vereinssatz **0x86C–0x871 = Tore, 0x872–0x877 = Gegentore je Viertelstunde** (1.–15., 16.–30. … 76.–90. Minute),
  je **ein Byte**. Speicher `0x01A73884` / `0x01A7388A` + Verein × 0x990.
- Code: Zählen in `0x0069E224` (Tore) und `0x0069E2B9` (Gegentore): Minute auf 1…90 begrenzt, `(Minute − 1) / 15`, dann
  `add cl,1` ohne Prüfung. Aufrufer: zwölf Stellen `0x006591DB` … `0x0065A652`. Lesen in `0x0069E16A` / `0x0069E1C7`
  (einziger Aufrufer `0x007244E2`, kopiert die 12 Bytes in die Liga-Tabelle 10 der Liga-Gruppe: 24 Vereine × 16 B =
  Land, Verein, 6 + 6 Bytes; Speicher `0x00AED340 + Liga × 0x1A0`, im Spielstand Block 4 + Liga × 20 + 10).
  Anzeige `0x0044EF11` (sortiert nach Toren, Summe `0x00724454`) und `0x0044F358` (nach Gegentoren, `0x0072449B`),
  Überschrift Text 4748 `IDS_STAT_UEBER_WANN_TRAFEN_CLUBS`.
- Es gibt im Programm keine weitere Stelle, die diese Bytes schreibt: Sie werden **nie zurückgesetzt**, auch nicht beim
  Saisonwechsel (Test-Spielstände `vorher` → `nachher`: unverändert). Die Nachbarstatistiken derselben Gruppe (z. B. die
  6-Byte-Tabelle mit 189 / 158 / 131 nach 28 Saisons) zählen ebenfalls über alle Saisons, aber in 16 Bit.
- Verlauf: etwa 7–8 je Feld und Saison. 2019: 0–3, 2027: 50–100, 2039: 110–225, erster Überlauf 2043 (Celta Vigo), 2047
  bei vielen Erstligisten. 2113 sind alle Werte mehrfach übergelaufen (Gladbach, Stand 383: Tore 209, 216, 229, 61, 25, 21).
  Uerdingen, letztes Feld: 253 (Stand 383) → 4 (`vorher`), also Überlauf in der laufenden Saison.
- Folge: Der Bildschirm zeigt ab etwa der 25. Saison zufällig wirkende Zahlen und eine falsche Reihenfolge.

### Möglichkeiten (nicht entschieden)
1. Nichts ändern.
2. Bei 255 stehen bleiben (kleiner Patch in den beiden Zählroutinen). Kein Rücksprung mehr, aber nach etwa 30 Saisons stehen
   alle Felder auf 255 – die Statistik wird ebenfalls wertlos, nur ruhiger.
3. Echte Korrektur (16 Bit je Feld) bräuchte 24 statt 12 Byte im Vereinssatz und 28 statt 16 Byte je Zeile der Liga-Tabelle,
   also ein geändertes Spielstandformat samt neuer Anzeige. Sehr großer Eingriff; nicht empfohlen.
Für laufende Karrieren (Nutzer: Saison 2113) sind die Werte in jedem Fall schon unbrauchbar.

## Kein Fehler (geprüft)
- Managersatz 0x230 ff. (Liste Datum + Level): Die „Rücksprünge“ sind das untere Byte der Jahreszahl (2047 = 0x7FF → 2048).
- Bytes, die nur zwischen 0 und 255 wechseln (Liga-Tabellen 1 und 8, Block 3, 1440-B-Blöcke): obere Hälfte negativer
  16-Bit-Zahlen (z. B. Tordifferenz).
- Spielersätze: keine Spalte mit sauberem Zählermuster und Überlauf. Die Laufbahnwerte (Tore 0x170, Spiele 0x180) sind
  16 Bit; Länderspiele (0x246, ein Byte) hatten im Bestand höchstens 196.
- Eingefrorene Listen: außer den behobenen („Beste Mannschaft“, Vereinsliste „Meiste Spiele“) keine. Die gleich gebliebenen
  Bereiche sind einzelne Zeilen (Rekorde, die nie überboten wurden, Vereine ohne Erstligaspiele). Der 440-B-Block je Land
  (Deutschland Block 205) ist eine Top-20-Liste mit Höchstwert 4 (V: meiste Tore in einem Spiel); neue Einträge mit
  gleichem Wert rücken hinter die alten – arbeitet.

## Nicht prüfbar mit den Spielständen
- Überlauf bei 127 (vorzeichenbehaftete Anzeige eines Bytes): an Daten nicht erkennbar, nur über die jeweilige Anzeige im Code.
  Kandidat für später (V): Spalten der Liste „Erfolgreichste Trainer“ und der Stationenliste, falls sie Bytes sind
  (Manager A: Sonstige 84).
- „Torjäger Plus“ und „Schirilieblinge“ nur Nullen (topic 796): **beim Nutzer kein Fehler** (Aussage 16.11.2026):
  „Schirilieblinge“ (Liga) funktioniert, „Torjäger“ und „Torjäger Plus“ (Mannschaft) funktionieren und werden zu
  Saisonbeginn zurückgesetzt, „Torjäger ewig“ (Mannschaft) addiert weiter. Die Forumsmeldung hängt vermutlich an der
  Statistikabteilung (V). Nicht weiter verfolgen.
- Rekordablösen: tatsächliche Transfers nicht bekannt.

## Nachtrag: Liga-Statistik „Tagesform“ (16.11.2026, Meldung des Nutzers: Werte passen nicht, hohe Werte eher bei schlechter Form)
- Anzeige `0x0044EB33` (Überschrift Text 4746 „Pl. / Verein / Form“, Zeile „%d.\t%s\t%d“), Daten über `0x00721191` aus
  `0x00AEC9B8 + Liga × 0xF4`; im Spielstand Liga-Tabelle 9 (192 B, 24 × 8 B: Land, Verein, Wert, Spieler in der Elf des Tages).
- Aufbau je Verein in `0x007230E1` (G): über alle Kaderspieler mit Bit 0 in +0x57 (V: im letzten Spiel dabei) wird
  `0x00705E9B` = unteres Halbbyte von +0xB8 = **Notencode des letzten Spiels (Note × 2)** addiert;
  Wert = Summe × 10 / Anzahl. Das ist also der Notenschnitt der Mannschaft im letzten Spiel × 20 (62 = Note 3,1).
- Folgen (G an `test5`: Jahn Regensburg 88 … Gladbach 58 … Augsburg 49, absteigend sortiert):
  1. **Hoher Wert = schlechte Noten**, und die Liste führt die schlechteste Mannschaft auf Platz 1.
  2. Spieler ohne Note (Code 0) zählen im Teiler mit und drücken den Wert (Bayern: Tabelle 50, mit allen Einsätzen
     gerechnet 51, nur benotete Spieler 67).
- Keine Korrektur gebaut. Möglich: nur benotete Spieler zählen (wie beim Notenschnitt); Reihenfolge umdrehen (beste zuerst);
  Wert als Note × 10 zeigen. Was davon gewollt ist, entscheidet der Nutzer – die Absicht der Entwickler ist nicht belegt (V).
- Berichtigung: Text 4746 = 0x128A (Tagesform, `0x0044EB33`), 4747 = 0x128B (Spielplan, `0x0044EDBA`).

### Tagesform: Entscheidung des Nutzers (16.11.2026) und Patch `tagesform`
Wörtlich: „Tagesform korrigieren, also richtig rum zeigen, nur Spieler einbeziehen, die auch eine Note erhalten haben“;
zur Skala: „ob man dann den Wert mal 20 oder mal 10 nimmt, ist egal“. Umgesetzt in `tools/a3patch.py` (drei Stellen):
- `0x00723162` (25 B): Summe + Notencode, Zähler nur bei Code ≥ 1,
- `0x00723189`: `imul eax,eax,10` → `5`, der Wert ist damit Note × 10 (31 = Note 3,1) – meine Wahl, weil lesbar,
- `0x007230B9`: Vergleichsroutine `0x00723094` `jle` → `jge`, Liste aufsteigend (beste Noten auf Platz 1).
Belegt: Die Tabelle 9 gehört zur Klasse mit Konstruktor `0x00645F50` (fünfter Tabellentyp in der Startinitialisierung
`0x00644FEB`), deren Liste die Funktionstabelle `0x00831A24` mit genau dieser Vergleichsroutine benutzt; sie wird nur dort
verwendet. Die Tabelle wird nach jedem Spieltag neu aufgebaut, alte Spielstände stellen sich von selbst um.
Bekannte Randerscheinung: Eine Mannschaft ohne benoteten Spieler bekommt den Wert 0 und steht dann oben.
Gebaut in `build/kandidat-1.43/anstoss3.exe` (`A9DA5C3C…`). **Im Spiel ungetestet.**

### Rückmeldung aus dem Spiel (16.11.2026): Tagesform-Seite leer – Sortierumkehr zurückgenommen
Mit `jle` → `jge` in `0x007230B9` war die Seite beim Nutzer komplett leer. Ursache (V, stark): Die 24 Plätze der Tabelle sind
vorbelegt (Land 0, Wert 0); aufsteigend sortiert stehen die leeren Plätze oben, und die Anzeige `0x0044ECB2` bricht beim
ersten Platz mit Land 0 ab. Die Stelle ist aus `a3patch.py` wieder entfernt (als Kommentar vermerkt); die Test-exe
`build/kandidat-1.43/anstoss3.exe` ist neu gebaut (Prüfsumme siehe HANDOFF). Geblieben sind bei der Tagesform: nur benotete
Spieler, Wert = Note × 10; Reihenfolge wieder wie im Original (höchster Wert = schlechteste Noten oben).
Offen: „beste zuerst“ anders lösen, z. B. den Wert umkehren (hoch = gut) statt die Sortierung – erst mit dem Nutzer klären.
**Im Spielordner liegt noch die fehlerhafte Fassung `A9DA5C3C…`** – erst nach „Spiel ist zu“ ersetzen.

### Unfertig: weitere Stellen mit Notenauswertung (Prüfauftrag des Nutzers, 16.11.2026, abgebrochen wegen Nutzungslimit)
Vier Routinen lesen die Spieltagsbytes mit anderen Masken als der Schreiber (`0x006FF2F7`: Einsatz 0xC0, Note 0x3C):
`0x00705EB6`, `0x00705F60`, `0x00706015`, `0x0070607A` prüfen den Einsatz nur mit 0x80 (volle Spiele 0x40 fehlen) und lesen
die Note mit 0x1C (nur 3 von 4 Bits: Noten ab 4,0 werden zu 0–3,5). Aufrufer: `0x005E572C` (Ereignis 0x5EF, Bedingung
„Saisonschnitt > 40“ kann so nie wahr werden, Höchstwert 35), `0x005FEC09` (Ereignis 0x4D3, Schnitt der letzten 3),
`0x00493490` (Dialog, „letzter Einsatz vor 6 oder mehr Spieltagen“). Wirkung der Ereignisse: `0x00700FA2` / `0x007007A1`
ändern Spielersatz-Bytes 0x272 / 0x26F (0–120). Welche Meldungen das im Spiel sind, ist nicht ermittelt. Nichts gepatcht.
Noch nicht angesehen: Notenleser im Spielbericht (`0x006580B2`-Aufrufer), `0x0048E36F`, `0x005E1741`, `0x0072796F`.

### Tagesform, zweite Fassung (16.11.2026 nachts): „beste zuerst“ über den umgekehrten Wert
Ursache der leeren Seite jetzt im Code belegt (G): Die Einfügeroutine `0x006C5BAC` nimmt einen Eintrag nur auf, wenn er
gegenüber dem **letzten Platz** (leer = Wert 0) „größer“ vergleicht, und hält den größten Wert oben. Mit umgedrehtem
Vergleich wäre nur ein Wert kleiner als 0 aufgenommen worden – also keiner.
Neue Lösung in `tools/a3patch.py`, Patch `tagesform` (drei Stellen):
- `0x00723162`: nur benotete Spieler zählen (unverändert),
- `0x0072317D` (34 B): gespeicherter Wert = **100 − Note × 10** (größer = besser); ohne benoteten Spieler 0 = nicht gelistet,
- `0x0044ECB9` (32 B, Anzeige): zeigt 100 − gespeicherter Wert, also wieder Note × 10 (31 = Note 3,1).
Die Sortierung selbst bleibt unangetastet; oben steht damit die Mannschaft mit den besten Noten.
Übergang: Ein alter Spielstand zeigt bis zum nächsten Spieltag verdrehte Zahlen (die Tabelle wird je Spieltag neu gebaut).
Zweiter Leser der Tabelle `0x006BF384` überträgt sie nur im Netzwerkspiel. Test-exe: siehe HANDOFF. **Im Spiel ungetestet.**

### Tagesform: Noten oder Spielerform? (Rückfrage des Nutzers, 16.11.2026)
Der Nutzer fragte, ob hier nicht die Form der Spieler (0–20, bei ihm nie unter 8–9) gemeint oder beigemischt ist.
Ergebnis (G): Die Statistik rechnet **nur mit der Note des letzten Spiels**, nicht mit der Form.
- `0x007230E1` addiert je Spieler `0x00705E9B` = unteres Halbbyte von +0xB8. Derselbe Wert wird im Einzelgespräch als
  Feld `IDC_EINZEL_NOTE_LETZTES` (5836, `0x0048E36F`, geteilt durch 2, „%.1f“) angezeigt und vom Schreiber `0x006FF2F7`
  als Notenbits in das Spieltagsbyte übernommen. Die Form ist ein anderer Wert: `0x006FF037` (Feld `IDC_EINZEL_FORM`
  bzw. `…_FORM_VORWOCHE`, 0–20, berechnet u. a. aus Spielersatz 0x333).
- Daten (`test5`, unveränderte Rechnung der alten exe, Skript `tform3.py`): Für alle 18 Vereine liegt der Tabellenwert
  beim Mittel der Notencodes × 10 der am letzten Spieltag eingesetzten Spieler (exakt bei Braunschweig 80, Bayern 50,
  Dresden 87, Werder 71, Kaiserslautern 79, Fürth 67; sonst ±1–4, weil sich die genaue Spielerauswahl aus dem Spielstand
  nicht eindeutig bestimmen lässt). Als Form gelesen wären das 4,9–8,8 – unter allem, was der Nutzer je gesehen hat.
- Offen (V): Überschrift „Form“ und die ursprüngliche absteigende Sortierung könnten darauf deuten, dass die Entwickler
  einen Wert im Sinn hatten, bei dem hoch gut ist. Belegbar ist das nicht. Der Nutzer findet die Reihenfolge der
  korrigierten Tabelle richtig (16.11.2026).

### Tagesform, dritte Fassung (16.11.2026): Anzeige als Note
Vorgabe des Nutzers: „dann sollten wir den Wert als Notenschnitt anzeigen und es auch so im Patch benennen und erklären“.
- Die Seite zeigt jetzt je Verein die Durchschnittsnote des letzten Spiels mit einer Nachkommastelle („3.1“, Punkt wie bei
  den übrigen Noten des Spiels). Gespeichert bleibt 100 − Note × 10 (wegen der Sortierung), die Zeile rechnet zurück.
- Technik (`tools/asm_tagesform.py`, vier Stellen in `a3patch.py`): `0x00723158` `je` direkt zum Schleifenkopf;
  `0x00723162` Schleifenrumpf, dahinter in 13 frei gewordenen Bytes die neue Formatzeile „%d.\t%s\t%d.%d“ (`0x00723170`);
  `0x0072317D` Wertberechnung; `0x0044ECB9` (89 B) Zeilenausgabe mit sechs statt fünf Werten. Die alte Formatzeile
  `0x0087A074` hatte nur diesen einen Benutzer und wird nicht mehr verwendet.
- Übergang: Vor dem ersten Spieltag nach dem Laden eines älteren Spielstands können unsinnige (auch negative) Werte stehen.
- **Nicht geändert: die Spaltenüberschrift „Form“** (Text 4746 „Pl. / Verein / Form“). Der Text steht in keiner Datei des
  Spiels im Klartext (weder ANSI noch UTF-16, auch nicht mit der XOR-Kette der `.saq`-Dateien); die Texte von
  `0x00730300` kommen über `0x007B7F68`, Quelle nicht ermittelt. Offen.
- Für die Patch-Texte: Eintrag als „Liga-Statistik ‚Tagesform‘: zeigt die Durchschnittsnote der Mannschaft im letzten
  Spiel …“ formulieren und erklären (niedriger = besser, nur benotete Spieler, beste Mannschaft oben).
- Test-exe `build/kandidat-1.43/anstoss3.exe`, SHA-256 `F52EF8CF…4171`, mit `dumpbin` gegengelesen, **im Spiel
  ungetestet, noch nicht im Spielordner** (dort `95122B7A…` mit ganzzahliger Anzeige).

### Tagesform im Spiel bestätigt (16.11.2026 nachts, `test6.an3`)
Aussage des Nutzers: Die Reihenfolge der Tabelle sieht korrekt aus. Am Spielstand nachgerechnet (`test6.py`): 18 Vereine
gelistet, gespeicherte Werte 73 … 53 absteigend = Anzeige 2,7 … 4,7 aufsteigend; die Werte entsprechen dem Notenmittel
der benoteten Spieler des letzten Spieltags (Gladbach 3,1 bei zwei Einsätzen ohne Note, Bayern 3,1, Köln 4,0 exakt;
übrige ±0,1–0,2 wegen der nicht eindeutig bestimmbaren Spielerauswahl). **Noch ungetestet: die Anzeige mit
Nachkommastelle** (dritte Fassung, exe `F52EF8CF…`, seit 16.11.2026 nachts im Spielordner).

### Quelle der Oberflächentexte gefunden; Überschrift „Form“ → „Note“ (16.11.2026 nachts)
- **Alle Oberflächentexte und Dialoge stehen in `deb\MeineDialoge.rch`** (873 393 B, SHA-256 `AA68E14E…7536`, im
  Spielordner identisch zur Kopie in `original/deb/`). Geladen von `0x004318FA` (`fopen("deb/MeineDialoge.rch","rb")`),
  Zugriff über `0x00730300` → `0x007B7F68` → Tabelle mit 12-Byte-Einträgen (Nummer, Text), binäre Suche `0x007B7B91`.
  Im Textteil der Datei: `[Nummer als Wort][Text, nullterminiert]`, deutsch; **`\t` steht ausgeschrieben als Backslash + t**
  (deshalb fand die erste Suche nichts). Eine Prüfsumme wurde im Lader nicht gesehen (V).
- Text 4746 „Pl.\tVerein\tForm“ liegt bei Datei-Offset 0x2FC26; „Form“ ab 0x2FC33. Patch `tagesform-ueberschrift`
  (neues Ziel in `tools/a3patch.py`): `466F726D` → `4E6F7465` („Note“, gleiche Länge). Gebaut:
  `build/kandidat-1.43/MeineDialoge.rch`, SHA-256 `72285A6A…8AB1`. **Noch nicht im Spielordner, im Spiel ungetestet.**
- Folge für den Installer 1.43: dritte Zieldatei (`deb\MeineDialoge.rch`) neben exe und ddraw.dll.
- Der Seitenname „Tagesform“ (Text 4009, Offset 0x29192) ist unverändert; „Tagesnote“ hätte dieselbe Länge – Entscheidung
  des Nutzers offen.

### Tagesform vollständig bestätigt (16.11.2026)
Der Nutzer bestätigt: Das Spiel startet mit der geänderten `deb\MeineDialoge.rch` normal, die Spaltenüberschrift lautet
„Note“, und die Werte stehen mit Nachkommastelle da („ja beides passt“). Damit hat die Textdatei keine Prüfsumme, die das
Laden verhindert. Offen bleibt bei 1.43 nur, dass `verhasst-noten`, `totalausfall` und `goldkettchen` nicht gezielt
prüfbar sind.
