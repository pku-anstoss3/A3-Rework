# Zuordnung: Historisches-Bildschirme ↔ Tabellen im Spielstand (15.11.2026)

Grundlage: 36 Bildschirmfotos des Nutzers aus Spielstand 383 (Spieldatum 15.1.2114, nur im Chat, nicht als Datei) und die Suche mit
`tools/a3suche.py` (Proben: `analyse/bildschirme-383.json`, `analyse/bildschirme-383b.json`).
Blocknummern = Position im Spielstand (in allen 97 Ständen gleich bis Index 3763). Alle Werte int16, wenn nicht anders angegeben.
**G** = an den Werten des Bildschirmfotos bestätigt, **T** = nur Fundstelle/teilweise.

## Gefunden

| Bildschirm | Ort | Satz | Aufbau | |
|---|---|---|---|---|
| Nat. Meister | Block 3 @ 51960 | 12 B, 5 Länder × 20 | Saison, Land, Verein, Punkte, Tore, Gegentore | G, im Werkzeug |
| Herbstmeister | Block 3 @ 53160 | 12 B, 5 × 20 | wie Meister, mit laufender Saison | G, im Werkzeug |
| Rekordmeister | Block 3 @ 0x101A8 / 0x105E0 / 0x10A18 | 2 B je Verein | Meister / Pokal / Euro | G (47/25/30, 37/17/30, 33/22/11) |
| Torrekorde | Block 3 @ ~49860 | 10 B | Vorname, Nachname, Verein, Tore, Saison | G |
| Ewige Torjägerliste | Block 3 @ ~50360 | 16 B | Vorname, Nachname, ?, Geburtsjahr, Verein+Aktiv (2 Bytes), Tore, Elfmetertore, Spiele | G (4 Zeilen) |
| Ewige Einsätze | Block 3 @ ~50550 | 16 B | Spiele, 3 Namensindizes, Jahr, Verein+Flag, ?, ? | T (Camara 767) |
| Rekordnationalspieler | Block 3 @ ~63560 | 10 B | ?, Vorname, Nachname, Geburtsjahr, Länderspiele | G (7 Zeilen) |
| Supertransfers | Block 3 @ ~64572 | 28 B | Ablöse in 10 000 (11500 = 115,00 Mio), ?, ?, ?, Land, Verein (ging zu), ?, ?, Namen … | G (4 Beträge) |
| Europameister / EM-Torschützenkönige | Block 3 @ ~78228 | 24 B | Jahr, Gastgeber, Sieger, 200, Finalgegner, 200, Ergebnis (2 Bytes), 0, ?, Namen, ? | G (Jahre, Länder) |
| Tabellenführungen | Block 3 @ ~32684 (Wert 1173) | ? | je Verein ein Zähler; Aufbau offen | T |
| Erfolgreichste Trainer | Block 210 (840 B) | 42 B × 20 | Nr., Name als Text, …, Meister, Pokale, EPs, Aufstiege, Sonstige | G (41/21/1/3/59, 37/16/4/2/53) |
| Trainerrauswürfe | Block 211 (800 B) | 40 B × 20 | Nr., Name als Text, …, Entlassungen, Trainerzeit, ?, Verein | G (20/82, 20/93, 19/88) |
| Meiste Zuschauer national | je Liga-Gruppe Tabelle 16 (Block 20 für die Bundesliga) | 24 B × 20 | int32 Zuschauer, Land/Verein Heim, Land/Verein Gast, Ergebnis (2 Bytes) … | G (147120, 146929) |
| Meiste Zuschauer intern. | Block 259 (480 B) | 24 B × 20 | int32 Zuschauer, …, Land/200 = Nationalelf oder Land/Verein, Ergebnis | G (488000 … 151306) |
| Rekordaufsteiger | Block 260 (2144 B) | 8 B je Verein | gesamt, in 1., in 2., in 3. | G, siehe `befund-auf-abstiege.md` |
| Rekordabsteiger | Block 261 (2680 B) | 10 B je Verein | gesamt, aus 1., aus 2., aus 3., aus 4. | G |
| Beste Mannschaft | Block 262 (200 B) | 10 B × 20 | siehe `fehler-beste-mannschaft.md` | G |
| Meiste Aufstiege (Spieler) | Block 263 (240 B) | 12 B × 20 | Spieler, ?, ?, Land+1, Verein, Anzahl | G (Brenkus 12 … Coleman 11) |
| Meiste Abstiege (Spieler) | Block 264 (240 B) | 12 B × 20 | wie oben | G (Cork 7, Ndure 7 …) |
| Rekorde | Block 1 (5520 B), Daten bei 404 / 728 / 866 | ? | Datum, Land, Verein, Managername als Text | T |
| Trainererfolge (Manager) | Manager-Pakete, siehe HANDOFF | – | – | G, im Werkzeug |

### Nachtrag: weitere Funde in Block 3 (alle G, im Werkzeug als `wett` ausgelesen und über alle Stände zusammengeführt)

| Bildschirm | Ort | Satz | Aufbau |
|---|---|---|---|
| Nat. Pokalsieger | 54360, je Land 320 B | 16 B × 20 | Saison, Land A (Low-Byte; High-Byte = Kennzeichen), Verein A, Land B, Verein B, Tore A, Tore B (Bytes), ?, Kennzahl |
| Ligapokal/Supercup | 55960, je Land 320 B | 16 B × 20 | wie Pokal; enthält die laufende Saison |
| Torschützenkönige | 57560, je Land 600 B | 10 B, bis 60 Einträge | Vorname, Nachname, Verein, Tore, Saison (mehrere je Saison bei Gleichstand) |
| Int. Wettbewerbe | 60560 + 320 × k, k = 0…4 | 16 B × 20 | wie Pokal. k = 0 Champions League (G), k = 1 leer, k = 2 vermutlich Europa League, k = 3 vermutlich Europ. Supercup, k = 4 Weltpokal (Gegner Land 33) |
| Weltmeister / WM-Torschützenkönige | 77722 | 24 B × 20 | Jahr, Gastgeber, Land A, 200, Land B, 200, Tore A, Tore B (Bytes), 0, Kennzahl, Vorname, Nachname, Tore << 8 \| Land |
| Europameister / EM-Torschützenkönige | 78204 | 24 B × 20 | wie WM |
| Häufigstes Ergebnis | Block 1324 (1536 B) für die Bundesliga; weitere Ligen 1326, 1328 … | int32-Matrix [Heimtore][Auswärtstore], 16 Spalten | 0:0 = 2572, 0:1 = 2723, 1:0 = 3080, 1:1 = 3455 – wie im Bild; „diese Saison“ vermutlich im hinteren Teil |
| Abs. ewige Tabelle | berechnet | – | Grundwert im Vereinssatz (0x85C Tore, 0x860 Gegentore, 0x864 Spiele, 0x868 Punkte; Gladbach 2946 : 2521, 1738, 2560) **plus** ewige Heim- und Auswärtstabelle: 2560 + 3106 + 3052 = 8718 Punkte, 1738 + 1573 + 1572 = 4883 Spiele ✓ |

Zusammenführung über 97 Spielstände: je Liste 48 bzw. 49 Saisons (2019–2046, 2093–2112/13), EM 24, WM 23 Turniere, **0 Widersprüche**.

Weiter offen: Endtabellen und Resultate der letzten 10 Saisons, ewige Heim- und Auswärtstabelle (Werte stehen nicht als ganze Zahl im
Spielstand, vermutlich je Liga getrennt), Tabellenführungen (Aufbau), 5-Jahreswertung, „Für die Ewigkeit“, Manager des Jahres,
Spieler des Jahres, Fußballer Europas, Ewige Einsätze (Aufbau), Rekorde (Aufbau).

### Zweiter Nachtrag (15.11.2026)

| Bildschirm | Ort | Aufbau | |
|---|---|---|---|
| Manager des Jahres | Block 4567 (3612 B) | je Land: int16 Anzahl, dann 20 × 36 B: Jahr, Name als Text (30 B), Land, Verein | G (2093 Möhlmann/Hertha, 2094 Manager B/Uerdingen, 2095 Kohler/Hoffenheim) |
| Rekorde | Block 1 (5520 B) | Sätze zu ~54 B: Wert, Datum (Tag, Monat, int16 Jahr), Land, Verein, …, Initial + Nachname als Text | T (Schlechteste Serie 11.4.2020, Meiste Punkte 24.5.2066 gefunden) |
| Für die Ewigkeit | **nicht im Spielstand**: Datei `alltimes.saq` (1056 B) im Spielordner, Speicher 0x00AE44F8 | 18 Sätze zu 58 B: echtes Datum (Tag, Monat, Jahr), Land (+4), Verein (+6), Initial (+0x1A), Name (+0x1C), Werte ab +0x2C | G (Datei gelesen, Kopie in `analyse/alltimes.saq`) |
| Platzierungen je Verein (für „Entwicklung Verein“, Endtabellen-Reihenfolge) | je Land ein 8640-B-Block (Deutschland: Block 213) | 108 Vereine × 20 Saisons × (Liga-Index, Platz) als int16 | G (Gladbach …, 1, 2 = 2111/12 Platz 1, 2112/13 Platz 2; Uerdingen …, 3, 1) |
| Ewige Torjägerliste je Land | je Land ein 320-B-Block (Deutschland: Block 206) | 16 B × 20: ?, Vorname, Nachname, Land, Verein, Tore, Spiele, aktiv | T (Sörloth 424 / 684) |

Blöcke 204–258 sind fünf gleich aufgebaute Pakete, eines je Land (Deutschland 204–214): 320, 440, 320, 320, 320, 704,
840 (Erfolgreichste Trainer), 800 (Trainerrauswürfe), 2160 (je Verein 5 Wertepaare, Bedeutung offen), 8640 (Platzierungen), 1440.

**„Für die Ewigkeit“ (G zum Mechanismus, V zur Erklärung):** Laden 0x006D616E (`fopen("alltimes.saq","rb")`, 0x420 Byte), Speichern
0x006D61C7, Standardwerte 0x006D5EB9 / 0x006D5E5D (Halter fest „R“ „Langenberg“, Land 14, Verein 104 bzw. 99, Datum = Systemdatum).
Jede Rekordroutine (ab 0x006D4D50) vergleicht ein neues Ergebnis nacheinander mit dem Karriere-Rekord (0x00B5CD1C …, im Spielstand,
Bildschirm „Rekorde“, Spieldatum) und mit dem Allzeit-Rekord (0x00AE44F8 …, Datei, echtes Datum) und ruft 0x006D5D6A.
Die Datei auf diesem Rechner enthält nur die Startwerte vom 13.10.2023 (Erstellungsdatum des GOG-Pakets). „R. Langenberg“ ist der
feste Platzhaltername für Nicht-Menschen. Wahrscheinliche Erklärung: Die Karriere wird meist auf einem anderen Rechner gespielt
(Remote Desktop, Spielstände 98–382 liegen beim Bruder) – dort liegt die fortgeschriebene `alltimes.saq`. Nicht bewiesen.
Auffällig im Code (nicht untersucht): Der Allzeit-Vergleich bei 0x006D4E32 weicht vom Karriere-Vergleich ab (überschreibt die
Tordifferenz und prüft nur „≠ 0“).

Weiter offen: Punkte und Tore der Endtabellen, Resultate, ewige Heim-/Auswärtstabelle, Tabellenführungen, 5-Jahreswertung,
Spieler des Jahres, Fußballer Europas, Ewige Einsätze.

### Dritter Nachtrag (15.11.2026): Rekorde, Spieler des Jahres, Fußballer Europas, Spielerwerte

| Bildschirm | Ort | Aufbau | |
|---|---|---|---|
| Rekorde | Block 1 ab Offset 404 (Speicher 0x00B5CD1C), 1056 B | **gleicher Aufbau wie `alltimes.saq`** (21 Einträge), aber Spieldatum | G: alle 10 sichtbaren Zeilen des Bildschirms stimmen |
| Spieler des Jahres | zweiter 3612-B-Block (Block 4568) | wie Manager des Jahres: je Land Anzahl + 20 × (Jahr, Name 30 B, Land, Verein) | G (2112 Schmid, 2111 Graovac, 2110 Sörloth) |
| Fußballer Europas | 724-B-Block (Block 4569) | Anzahl + 20 × 36 B wie oben | G (2112 Jagiello, 2111 Lucumí) |
| Ewige Einsätze / Torjäger / Länderspiele | Spielersatz 0x180 / 0x170 / 0x246 (Byte) | je Spieler, über alle Spielstände zusammengeführt | G / G / V stark |

Block 1 Kopf: int16 bei 64 = laufendes Managerjahr (95), bei 66 = Startjahr der laufenden Saison (2113), bei 68 = Startjahr des Spiels (2019).

Negativbefunde zur ewigen Heim-/Auswärtstabelle und zu den Tabellenführungen: Die angezeigten Werte (Spiele, Punkte, Tore) stehen
weder im Vereinssatz noch in irgendeinem anderen Block als int16/int32, auch nicht als Summe von 2–4 gleichabständigen Feldern
und nicht als Sieg/Unentschieden/Niederlage in einem 6er-Fenster. Sie werden also aus mehreren, anders geschnittenen Teilen berechnet.
Weg: über den Code der Anzeige.

### Über den Code gefunden: Archiv der letzten zehn Saisons je Liga (15.11.2026, G zum Ort, Aufbau erst teilweise)

- Verteiler der Historisches-Bildschirme: 0x0045E8A5, Index `[this+0x343C]` (0…60) über Bytetabelle 0x0045EB82 und Sprungtabelle
  0x0045EADE. Reihenfolge wie in der Seitenleiste: 0–9 Endtabelle → 0x0045EBBF(9 − Index), 10–19 Resultate → 0x00463E8D(19 − Index),
  dann u. a. 0x0045FEAC, 0x0045FAC1, 0x0045F3C0, 0x004608CE, 0x00460C7A (5-Jahreswertung?), 0x0045F0D4, 0x00461E6A, 0x0045F7A5,
  0x0045F8E5 (Für die Ewigkeit, liest 0x00AE44F8), 0x004629FE, 0x00463213, 0x0046364C, 0x00463A9B (Tabellenführungen?),
  0x00460F97 (ewige Tabelle?) … 0x00466C6F, 0x00466E72, 0x004665DD (Beste Mannschaft), 0x00467075. Zuordnung der mittleren
  Einträge noch nicht einzeln geprüft.
- Endtabelle: 0x0045EBBF ruft 0x0072B18A(Land, Liga, Saisons zurück, Ziel) und danach 0x0072AF32 (berechnet die Tabelle aus dem
  Ligaobjekt, Einträge zu 20 Byte). 0x0072B18A kopiert 0x972 = 2418 Byte aus
  `0x00B21ADC + Liga-Nr. × 0x5E74 + Saisons zurück × 0x972` (Liga-Nr. = 0x00677B07(Land, Liga)).
- Im Spielstand ist das **Block 2 (250628 B): ab Offset 8828 zehn Ligen × zehn Saisons × 2418 Byte** (8828 + 10 × 24180 = 250628 ✓).
  Ligaobjekt: int16 Land (14), Mannschaften (18), …, 34 Spieltage, ab int16-Index 9 achtzehn Werte (Vereine, Kodierung offen),
  ab Byte ~114 die Ergebnismatrix zu 4 Byte je Paarung (0xFF × 4 = Diagonale; vermutlich Tore, Gegentore und Halbzeitstand).
  „Saisons zurück“ 0 ist die laufende Saison. Noch offen: Reihenfolge der Mannschaften in der Matrix und die genaue Bedeutung
  der 4 Bytes – die erste Zeile passt noch nicht zum Bildschirmfoto „Resultate 2112/13“.
- Damit sind Endtabellen (aus den Ergebnissen berechnet) und Resultate grundsätzlich lesbar; vermutlich entstehen auch die ewige
  Heim-/Auswärtstabelle und die Tabellenführungen aus solchen Ligaobjekten bzw. eigenen Zählern – noch zu prüfen.

### Suche nach Endtabellen und Resultaten – bisher ohne Erfolg (15.11.2026)

- Blöcke 1323, 1325, … (6760 B, je Liga, gefolgt vom 1536-B-Block „Häufigstes Ergebnis“) sind die **laufende** Saison:
  Liganame als Text („1. Bundesliga“, „1. BL“), Spielplan, Ergebnisse als 4 Bytes (Tore, Gegentore, Halbzeit), 0xFF = noch nicht gespielt.
  Keine vergangenen Saisons.
- Blöcke 4555–4564 (je 130408 B; in Spielstand 1 keiner, in 61 acht, in 383 zehn) beginnen mit 8-Byte-Sätzen (2, fortlaufende Nummer,
  Wert, 1) und enthalten weiter hinten Felder mit fortlaufenden Zahlen und 0xFF-Füllung. Kein erkennbares Tabellen- oder
  Ergebnisformat; Bedeutung offen.
- Der Bildschirm „Resultate 2112/13“ ordnet die Vereine nach der Abschlusstabelle der **Vorsaison** (Aufsteiger am Ende) –
  das ist die Reihenfolge der Liga zu Saisonbeginn, kein Fehler.
- Nächster Weg: im Code die Anzeige der Endtabellen suchen (Text-IDs `IDS_STAT_ABSCHLUSSTABELLEN`, `IDS_STAT_RESULTATE_LETZTE_SAISON`
  in `original/deb/ListeDerTexte.rh`) und von dort die gelesenen Speicherobjekte bestimmen.

### Geplant: vollständige alltimes.saq (Wunsch des Nutzers)

Aus der Datei des Nutzers (`alltimes_1.saq`, bis Oktober 2022) und der des Bruders eine Datei bauen, in der je Eintrag der bessere
Rekord steht. Vergleich je Eintrag wie im Spiel (Routinen ab 0x006D4D50). Dafür müssen die sechs Spieler-Einträge (11–15, 17) noch
entschlüsselt werden. Einspielen in den Spielordner erst mit dem Endpaket und nach Zustimmung.

## Bestätigung des Aufstiegsfehlers am Bildschirm (G)

„Rekordaufsteiger“ zeigt genau die falsch gezählten Werte: TSV 1860 München 40 Aufstiege bei „in 1.“ 5, „in 2.“ 17, „in 3.“ 0.
Rekordabsteiger: 22 Abstiege (5 / 16 / 1). Richtig wären 5 + 17 + 1 = 23 Aufstiege; die 40 entstehen aus 5 + 2 × 17 + 1.
FC Energie Cottbus: 40 = 2 + 2 × 18 + 2, angezeigt „in 3.“ 20 (davon 18 die Doppelzählung über die Regionalliga Nord).

## Abschluss (15.11.2026, Nachtarbeit): alle 34 Bildschirme zugeordnet

Die weiter oben als offen genannten Punkte sind erledigt. Block 3 (82340 B) liegt im Speicher bei `0x00B0B6B8`
(`mov ecx,0B0B6B8h` in `0x00460D57`); Blockoffset = Speicheradresse − `0x00B0B6B8`.

| Bildschirm | Ort | Aufbau | |
|---|---|---|---|
| Endtabellen / Resultate | Block 2 @ 8828 + Liga × 24180 + Fach × 2418 | Liga-Objekt: +0 Land, +2 Vereine, +4 zweite Serie, +0x10 Sortierart, +0x12 Verein je Platz (Byte), +0x2A Kennzeichen (Bit 0–1 × 3 = Punktabzug, 0x80 = letzter Platz), +0x72 + i × 96 + j × 4 = Tore, Gegentore, Halbzeit; Fach 9 = letzte beendete Saison | G (190/190 Meister, 4440/4440 Plätze) |
| Laufende Saison je Liga | Blöcke 1323, 1325, … 1337 (6760 B) | +0 Name, +0x30 Vereine, +0x32 Spieltage, +0x34 Land, +0x52 Verein je Platz (int16), +0xB2 + Platz × 46 Tabellenplatz je Spieltag, +0x53B Paarungen je Spieltag (24 B), +0xE4A + i × 96 + j × 4 Ergebnis | G |
| Ewige Tabellen | Block 3 @ 31500 + Abschnitt × 2592 + Verein × 24 | 3 × (Spiele, Punkte, Tore, Gegentore) int16: gesamt, heim, auswärts; Anzeige zählt die laufende Saison der ersten Liga dazu (`0x0072B25B`), relativ = nach Punkten je Spiel umsortiert (`0x0072B6C2`) | G (alle Werte der Bildschirmfotos) |
| Tabellenführungen | Block 3 @ 47700 + Abschnitt × 432 + Verein × 4 | Anzahl, Saisons (int16) | G (1173/93, 1031/83, 160/83, 103/87) |
| 5-Jahreswertung | Block 1 @ 1568, 37 × 36 B | Land (int32), Summe, 7 Saisonwerte (float): vor 6 Saisons, fünf gewertete (älteste zuerst), laufende | G (14,86 … 16,83 = 72,94) |
| Meiste Zuschauer national | Block 3-Index + 1 + Liga × 20 + 16 | wie bisher, jetzt für alle 8 Ligen | G für Liga 0, T für die übrigen (passende Vereine) |
| Häufigstes Ergebnis | 1536-B-Block hinter jedem Liga-Objekt (1324, 1326, …) | int32-Matrix [Heim][Gast], 16 breit | G für Liga 0 |
| Punktabzug / Zwangsabstieg | Vereinssatz 0x10A | Bit 0–1 × 3 Punkte Abzug, 0x80 = wird Letzter (`0x0063E470`) | G: Kaiserslautern 2021 Wert 3; zehn Fälle mit 0x80 |

Verteiler `0x0045E8A5`, Index → Routine (über die gelesenen Speicheradressen bestimmt): 0–9 Endtabellen, 10–19 Resultate,
20 Int. Wettbewerbe (`0x0045FEAC`), 24 Ewige Torjäger (`0x0045F3C0`), 25 Torschützenkönige (`0x004608CE`), 26 Torrekorde
(`0x00460C7A`), 28 Rekordnationalspieler (`0x00461E6A`), 29 Rekorde (`0x0045F7A5`), 30 Für die Ewigkeit (`0x0045F8E5`),
33 Tabellenführungen (`0x00463A9B`), 35 abs. ewige Tabelle (`0x00460F97`), 36 rel. ewige Tabelle (`0x00461AC7`),
39 Supertransfers (`0x0046217A`), 50 Erfolgreichste Trainer (`0x00465ABB`), 54/55 ewige Heim-/Auswärtstabelle
(`0x004613DB`, `0x00461751`), 56 Beste Mannschaft (`0x004665DD`). Die übrigen Indizes sind nicht einzeln zugeordnet.
Die Anzeige der 5-Jahreswertung im Code ist nicht gesucht worden; der Ort ist über die Daten bewiesen.

Auffälligkeit im Spiel: Die relative ewige Tabelle vergleicht in `0x0072B6C2` den letzten Verein eines Landes nie (Schleifen
laufen bis Anzahl − 2 bzw. Anzahl − 1). Sichtbar wäre das nur, wenn der letzte Verein der Landesliste Erstligaspiele hätte.

„Erfolgreichste Trainer“, Spalte EPs: siehe `befund-trainer-eps.md`.

## Noch nicht gefunden

Nichts mehr aus der Seitenleiste. Offen sind nur noch die sechs Spieler-Einträge der `alltimes.saq` (11–15, 17).

## Beobachtung zu „Rekorde“ und „Für die Ewigkeit“ (V)

„Für die Ewigkeit“ zeigt bei allen Einträgen „R. Langenberg“, 13.10.2023 und runde Werte (70 Punkte, 80 Tore, 70000 Zuschauer).
Das sieht nach fest vorgegebenen Startwerten aus, die nie überboten bzw. nie fortgeschrieben wurden; „Rekorde“ enthält dagegen
laufend aktualisierte Werte der beiden Manager. Ursache nicht untersucht.
