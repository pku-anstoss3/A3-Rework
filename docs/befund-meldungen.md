# Befund: Meldungen des Spiels – Auslöser, Erreichbarkeit, Wirkung (Stand 16.11.2026 abends)

Auftrag des Nutzers: alle Meldungen (Zufallsereignisse, Zeitungsmeldungen und so weiter) daraufhin prüfen, ob ihre
Auslöser überhaupt eintreten können und richtig gerechnet werden. Untersucht ist die unveränderte `anstoss3.exe` 1.40;
nichts ist gepatcht. **G** = im Code gelesen oder an der Programmdatei nachgezählt, **V** = Vermutung.
Dieses Dokument ist von Hand geführt (nicht mehr mit `meld7.py` erzeugen). Der Arbeitsstand der Analyse steht in
`analyse/meldungen/notizen.md` (lokal).

## Stand und Umfang
**Fertig (G):**
- Zuordnung Text ↔ Stelle über alle Routinen mit Textparameter (zweite, vollständigere Zählung, Abschnitt 1);
- Erreichbarkeit aller Meldungsroutinen (Abschnitt 2);
- Kennzeichen, Werte und Argumentzahl aller 70 Aufrufe der Zeitungsroutine (Abschnitt 4);
- Aufbau und Benutzer der 80 Fragen-Datensätze (Abschnitte 1 und 6);
- einzelne von Hand nachgeprüfte Fehler (Abschnitte 3, 5 und 6).

**Offen:**
- Die Bedingungen der einzelnen Auslöser (Schwellen, gelesene Felder, Masken) sind nicht durchgehend gelesen. Dafür
  sind 175 Routinen (64 996 Befehle) in die Lesepakete P01–P14 aufgeteilt. Teilweise gelesen: P02, P04, P06, P07.
  Nicht begonnen oder nur angelesen: P01, P03, P05, P08a, P08b, P09, P13, P14.
- **P02, P04 und P06:** Die als Fehler oder „nie“ markierten Einträge dieser Kataloge sind von Hand am Code
  nachgeprüft und alle bestätigt (P02: Abschnitte 6.6–6.12, P04: Abschnitt 6.13, P06: Abschnitt 6.14).
- **P07:** beide Teile sind ebenso nachgeprüft und bestätigt (Hobby-Ereignisse `0x005FD59D`: Abschnitt 6.15;
  Ereignisse zwischen zwei Spielern `0x005FEDB0` und privater Trainer `0x005FFF0F`: Abschnitt 6.16). Damit sind die
  markierten Einträge aller vier halbfertigen Kataloge durch.
- Eine Einordnung „bewusst stillgelegt oder Versehen“ steht in Abschnitt 6.17 (Vermutung, nicht beweisbar).

**Im Nachgang (aufgeschoben, nicht gestrichen):**
1. Die noch ungelesenen Routinen der Pakete: in P02 vier (`0x005E50BA`, `0x005E56A5`, `0x005E5A01`, `0x005E60BC`,
   1034 Befehle), in P04 22 von 37 (darunter `0x005F0A47`, `0x005F125B`, `0x005F3BAF` mit zusammen rund 2360
   Befehlen).
   In P06 fehlen im Katalog 8 der 19 Routinen.
2. Die in den Katalogen als „OK“ eingestuften Einträge (in P04 142, in P06 32, in P02 der Rest): gegenlesen oder
   Stichprobe.
3. Ob das Muster „Vorher mit Zuschlägen, Nachher ohne“ (Abschnitt 6.9) auch an anderen Stellen vorkommt.
4. Was im Platz hinter dem letzten Kaderspieler steht (Abschnitt 6.14, Vorroutine `0x005FA5F8`): nur im Speicher
   des laufenden Spiels oder in einem Test zu sehen.
5. In P07 71 „OK“-Einträge und drei von neun Routinen, die im Katalog fehlen; in der Hobby-Routine haben 18 von 38
   Hobbys kein Ereignis (Angabe des Katalogs); die weiteren Fehler, die der Katalog in den nie erreichbaren Fällen
   von `0x005FEDB0` meldet (nur wichtig, falls diese Ereignisse freigeschaltet werden sollen).
6. Danach die Pakete P09, P13, P14, P03, P05, P08, P01.
- Die Hilfsläufe (Hilfsroutinen A–D, Tabellenstellen, Pakete) haben Auffälligkeiten gemeldet, die noch nicht von Hand
  am Code bestätigt sind. Sie stehen getrennt in Abschnitt 7 und sind **keine Ergebnisse**.
- Offene Reste der bestätigten Befunde sind dort jeweils als „offen“ vermerkt (Folge der falschen Managernummer bei
  1880; Häufigkeit der Halbzeit-Schlagzeilen; Wertebereiche einzelner Indizes).
- Die Gesamtabrechnung aller 2483 Texte (erreichbar / nie erreichbar / ungenutzt) fehlt.
- Im Spiel ist kein Befund dieses Dokuments nachgestellt.

**Nicht geprüft (Entscheidung des Nutzers, 16.11.2026):** die Spieltexte – Fangesänge und Zuschauerreaktionen ab
Text 2075 (Routinen `0x00615225`, `0x0061804F`–`0x0061C24B`), Lesepakete P10/P11 und P12. Für diesen Bereich gibt es
nur die maschinelle Erreichbarkeitsprüfung aus Abschnitt 2.

**Arbeitsweise:** Die Hilfsläufe sind gestoppt und werden nicht fortgesetzt. Weiter nur in einzelnen, vorher
freigegebenen Schritten, nie parallel.

## Ergebnis in Kürze
- **Umfang (G):** `texte\Ereignis.saq` enthält 2483 Texte. 1414 davon haben mindestens eine Stelle mit fester Nummer
  (1442 Stellen, davon 70 Aufrufe der Zeitungsroutine); 1069 haben keine feste Stelle (Auswahl über Tabellen,
  Fragen-Datensätze oder ungenutzt – nicht abschließend bewertet). Die erste Fassung dieses Befunds nannte 1355
  Stellen, 1326 Texte und 1157 Texte ohne Stelle; sie verfolgte nur einen Textparameter je Routine.
- **Nie erreichbar (G): 94 Texte in 18 Routinen, die nie ausgeführt werden** (erste Fassung: 65 Texte in 11
  Routinen) – darunter die Spieler-Ereignisse 1315–1325 (Lottogewinn, Geldanlagen der Spieler), 1417–1427 (Gruppen
  im Kader), 1029–1034 (Hochzeitstag), 1087–1092 (Vaterschaft), 1238–1242 (Beziehungskrise), neu die Verfehlungen
  der Spieler 459–476 (unentschuldigt gefehlt, Alkoholfahrt, negatives Interview …). Abschnitt 2.
- **Fehlalarme (G):** Die zwischenzeitlichen Treffer „Stelle in unerreichbarem Code“ für die Texte 273 und 285 sind
  keine Fehler; das Disassembly war an diesen Stellen verstümmelt. Abschnitt 2.
- **Nie erreichbar durch falschen Zufallsbereich oder falsche Bedingung (G):** Texte 1178 und 1179 (Verteiler mit
  vier Fällen, Zufall 0–1), 888 und 889 (Tabelle mit 12 Einträgen, Zufall 0–9), 1289 (Fall ohne Los-Nummer), 1481
  (Bedingung „Alter unter 20“ im Zweig „Alter ab 25“). Abschnitt 3.
- **Wirkung nicht angewendet (G): acht Zeitungsmeldungen** übergeben einen Abzug bei „Presse“, der nie beim Spieler
  ankommt: 1125, 1188, 1197, 1201, 1269, 1528, 1530 und 1235 („Goldkettchen“, bereits Korrektur `goldkettchen`).
  Abschnitt 4.
- **Falsche Argumentzahl (G): vier Zeitungsmeldungen** (1743, 1744, 1750, 1880) übergeben nicht die Argumente, die
  ihre Kennzeichen verlangen. Bei 1880 wird dadurch −5 als Managernummer gespeichert. Abschnitt 4.
- **Vereinszähler läuft über (G für die Rechnung):** der Zähler in Verein +0xDF8 springt bei der achten Erhöhung
  einer Saison von 7 auf 0. Abschnitt 5. (Berichtigt 17.11.2026: das Löschen von Bit 21 bei jeder Erhöhung ist
  Absicht, kein Fehler.)
- **Weitere bestätigte Fehler (G), Abschnitt 6:** falsche Liste beim Streichen eines Spielers (`0x00703930`);
  Straf-Frage Stufe 1 wertet die Antworten vertauscht aus; drei fest abgeschaltete Zweige; acht Fragen-Datensätze
  mit eigenem Inhalt, die nie benutzt werden; Texte 1728 und 1733 fehlen in der Tabelle der Eigenschaften.
- **Aus Lesepaket P02 bestätigt (G), Abschnitte 6.6–6.12:** vier Texte mit „%s“ statt „%1“ (Spielername erscheint
  nicht: 954, 1276, 1338, 1355); der Name der Frau bleibt leer (969, 1296); Frage 1294 nennt keinen Spieler; falsche
  Vorher-Werte in der Meldung (1309–1311) und falsche Beschriftung (1312); Karriereende 1342 findet nicht statt;
  der enttarnte Spitzel bleibt Spitzel (983); ein Zweig der Gruppenbildung ist unerreichbar (1412); sieben Ereignisse
  hängen an fest eingetragenen Spielernamen, die in den Stammdaten nicht vorkommen (1348–1351, 1353–1355).
- **Aus Lesepaket P04 bestätigt (G), Abschnitt 6.13:** Ersparnis wird als Ausgabe gebucht (690), Kosten als Einnahme
  (697); erfolgreiche Verhandlung bringt nicht den höheren Betrag (224/225); Text 281 „Staatsbürgerschaft“ kann nie
  erscheinen; bei Randale kommt die Entwarnung 283 statt 284, obwohl 100 000 abgezogen werden; Text 285 nennt 20
  Punkte, abgezogen werden je 5; die Aufhebung der Ausländerbeschränkung (769) hat keine Wirkung.
- **Aus Lesepaket P06 bestätigt (G), Abschnitt 6.14 (Privatleben der Spieler):** die Affären-Ereignisse 1126–1128
  und 1236 treten nie ein (ein Bit wird nie gesetzt); alle Ehefrau-Ereignisse verlangen eine Geliebte; „Hochzeit
  platzt“ trifft den falschen Spieler (Zeiger hinter dem Kader, möglicher Absturz), die abgesagte Hochzeit findet
  trotzdem statt; Trennungen aus den Texten 1083 und 1115 werden nicht vollzogen; Namen vertauscht in 1094, 1104,
  1109; Wirkungen von 1109 und 1110 vertauscht; „%s“ statt „%1“ in 1115–1117; Abitur 1565 ohne Merker; 1076 fünf
  statt vier Wochen; 1982 ohne Rückgabe; ein Bit doppelt belegt (Gruppen-Anführer / Schüler-Merker).
- **Aus Lesepaket P07 Teil 1 bestätigt (G), Abschnitt 6.15 (Hobby-Ereignisse):** sechs Verletzungen mit falscher
  Dauer oder Art (1193 16 statt 3 Wochen, 1215 1 statt 3 Wochen, 1225 und 1227 ohne Ausfall, 1194, 1224);
  angekündigte Wirkung fehlt (1180, 1210); Streit bei 1172 zwischen den Falschen; Name der Frau leer (1176, 1177,
  1210); 1168 falsch beschriftet; 1217 zwei statt ein Monat; 1173 und 1226 nie erreichbar; der Führerschein-Zähler
  wird nie zurückgesetzt.
- **Aus Lesepaket P07 Teil 2 bestätigt (G), Abschnitt 6.16:** acht Texte ohne Los-Nummer (1377, 1395, 1396, 1399,
  1402–1405) und sechs leere Lose bei den Ereignissen zwischen zwei Spielern; 1363 mit nie beschriebenem
  Namenspuffer; 1365 mit vertauschten Namen; 1388 statt 1389; der Konditionsbonus des privaten Trainers (1358,
  1359) wird nie gerechnet.
- **Absicht oder Fehler:** Einordnung in Abschnitt 6.17 (V).
- **Bereits bekannt und teils korrigiert:** 1519 „Totalausfall“ (konnte nie erscheinen, Korrektur `totalausfall`),
  1235 „Goldkettchen“, Antwort „Spielpraxis für Mitspieler“ im Auswechsel-Gespräch (falsche Bitmasken, unverändert) –
  `befund-notenschnitt.md`.
- **Nicht geleistet:** siehe „Stand und Umfang“ und Abschnitt 8.

## 1. Wie die Meldungen ausgelöst werden (G)
- **Texte:** Die Tabelle `0x00A2FAE8` wird ausschließlich über `0x005EF430(Nummer)` gelesen (262 Aufrufe). 39
  Routinen haben einen oder mehrere Textparameter und reichen die Nummer dorthin weiter (zum Beispiel `0x00600F2F`,
  `0x00601043`, `0x005EE5C0`). Die vollständige Rückverfolgung (`meld10.py`, mehrere Textparameter je Routine, mit
  Versatz) ergibt 1442 Stellen mit fester Nummer für 1414 Texte (`analyse/meldungen/stellen2.tsv`), 38 Stellen mit
  Nummer aus Tabelle oder Variable (`unklar2.txt`) und 1069 Texte ohne feste Stelle (`texte_ohne_stelle.tsv`).
  Die erste Zählung (`meld2.py`: 40 Hüllroutinen, 1355 Stellen) ist damit überholt.
- **Fragen mit Antworten (Dialog 253):** 80 Datensätze `0x0088F090 + n × 44`: +0 Kennzeichen, +4 Frage (−1 = vom
  Aufrufer vorbereiteter Text bei `0x00A32210`), +8 / +0xC / +0x10 drei Antworten, +0x14 / +0x18 / +0x1C
  Ergebnistexte, +0x20 Routine für die Frage, +0x24 für die Antworten, +0x28 Auswertung. Geöffnet wird der Dialog
  (Klasse ab `0x00496A0F`, Anzeige `0x00496B94`) nur über `0x005F2813(Manager, Verein, Datensatz)` und
  `0x005F29BC(Manager, Verein, Text, Spieler, Art 1–3)` (Datensatz = Art + 33). Globale Nachricht `0x00A321E8`:
  +0 Manager, +2 Land, +4 Verein, +6 Antwort, +0xC Datensatz, +0x14 Betrag, +0x22 Zusatzindex, +0x28 Text.
  Die Texte dieser Datensätze haben keine „Stelle mit fester Nummer“ und stecken in den 1069 Texten ohne Stelle.
  Sechs Routinen mit Textparameter ohne direkten Aufrufer (`0x005EE98D`, `0x005EE9C2`, `0x005EEA5D`, `0x005EEBFA`,
  `0x005EECBA`, `0x0060B898`) stehen als Routine in diesen Datensätzen (+0x20 / +0x24) und sind damit erreichbar.
- **Tägliche Ereignisse je Verein:** `0x005EF842` ruft `0x005EF8CC` (Ereignisse rund um die Spieler) und, wenn dort
  nichts geschah und der Verein einen menschlichen Manager hat, `0x005F0133` (Ereignisse für Verein und Manager).
- **Gewichtete Auslosung:** `0x0060BE4D(Tabelle)` zieht eine Zufallszahl 0 bis Gesamt−1 und geht die Gewichte durch;
  liegt die Zahl über der Summe der Gewichte, kommt 0 = kein Ereignis. Tabellenobjekte legt `0x0060BDB7(Anzahl,
  Einträge, Gesamt)` an; ein Eintrag ist (Gewicht, Nummer) als zwei int16. Objekt: +0 Anzahl, +2 Summe der Gewichte,
  +4 Gesamt; ist Gesamt kleiner als die Summe, gilt die Summe (die Angaben −1 und 1 bedeuten also „Summe“).
- **Spieler-Ereignisse** (`0x005EF8CC`, Tabelle `0x0088E128`, Gesamt 10000, Summe der Gewichte 2100 – in 21 % der
  Aufrufe wird eine Ereignisart gezogen). Jede der 24 Nummern hat im Verteiler `0x005EFADA` eine eigene Routine:

  | Nummer | Gewicht | Routine | | Nummer | Gewicht | Routine |
  |---|---|---|---|---|---|---|
  | 1 | 100 | `0x005F8CA8` | | 19 | 110 | `0x005FED08` → `0x005FD59D` (Privatleben) |
  | 2 | 100 | `0x005F9A2D` | | 20 | 30 | `0x005E56A5` (Leistungs-Schlagzeilen) |
  | 3 | 100 | `0x005FA890` → `0x005FA6CE` | | 21 | 11 | `0x005E5DE6` → `0x005E5A01` |
  | 4 | 100 | `0x005FB17A` → `0x005FAA76` | | 22 | 22 | `0x005F9FD0` |
  | 5 | 100 | `0x005FB634` → `0x005FB264` | | 23 | 11 | `0x005F9D6D` → `0x005F9B90` |
  | 6 | 100 | `0x005FB916` → `0x005FB751` | | 24 | 55 | `0x00600098` |
  | 7 | 100 | `0x005FBAF9` | | 25 | 100 | `0x005FFEB7` |
  | 8 | 100 | `0x005FC5B5` | | 50 | 66 | `0x005E4DDE` → `0x005E4A3E` |
  | 9 | 100 | `0x005FA5F8` → `0x005FA394` | | 51 | 44 | `0x005E4FD6` |
  | 10 | 55 | `0x005FC8E6` → `0x005FC6BC` | | 52 | 500 | `0x005E50BA` („Maulwurf“) |
  | 11 | 55 | `0x005FCFCD` → `0x005FCD9D` | | 55 | 20 | `0x005FFF0F` |
  | 12 | 11 | `0x005FD1D1` | | | | |
  | 18 | 110 | `0x005FD4AE` (Hobby, Text 1233) | | | | |

  Hat die gezogene Art nichts ausgelöst (oder wurde keine gezogen): Zufall 0–999 kleiner als die Kadergröße →
  `0x005E20FD` → `0x005E08F1` (45 Texte ab 1254, für einen zufälligen Kaderspieler).
- **Verein und Manager** (`0x005F0133`, Tabelle `0x0088E188`, Gesamt 10000, Summe 1761): 16 Nummern, alle mit Routine
  (`0x0060EC50`, `0x005E60BC` → `0x005E6153`, `0x005F3BAF`, `0x006024FD` → `0x00602594`, `0x005F4BAB`, `0x005F54BF`,
  `0x005F72F0`, `0x005E993A`, `0x0060AA05`, `0x005E9B22`, `0x005E9ED1`, `0x006018CE`, `0x0060229F`, `0x005F0778`,
  `0x005F76E1`, `0x00610192`); Gewichte 300, 250, 250, 250, 50, 200, 30, 50, 60, 10, 20, 50, 30, 1, 200, 10.
- Die meisten dieser Routinen losen ihr einzelnes Ereignis mit einer eigenen Gewichtstabelle aus (72 Aufrufe von
  `0x0060BE4D`; Liste mit Gewichten in `analyse/meldungen/gewichte.txt`).

## 2. Routinen, die nie ausgeführt werden (G)
Methode (`meld14.py`, Ausgaben `tot2.txt` und `erreichbar.tsv`): Auf den Anfang der Routine gibt es keinen relativen
Aufruf oder Sprung (Rohbytes E8/E9) aus einer lebenden Routine, und ihre Anfangsadresse steht nirgends als 4-Byte-Wert
in der Datei. Werte, die nur zufällig in die Mitte einer Routine zeigen, zählen nicht als Verweis, Einträge von
Sprungtabellen auch nicht. Drei der Routinen werden nur von einer Hüllroutine aufgerufen, die selbst niemand aufruft
(`0x005E3F39` → `0x005E3CA8`, `0x005FCC29` → `0x005FC9EE`, `0x0060B430` → `0x0060AE6C` und `0x0060B11E`).
Texte, die auch an einer erreichbaren Stelle vorkommen, sind nicht mitgezählt.
Die erste Fassung (`meld4.py`) nannte 11 Routinen mit 65 Texten; sie prüfte nicht, ob der Aufrufer selbst lebt.

| Routine | Texte (nur dort) | Inhalt |
|---|---|---|
| `0x005DFC63` | 850 | Der Verein wird den Vertrag mit Ihnen nicht mehr verlängern. |
| `0x005E1C68` | 1315–1325 | Geld der Spieler: Lottogewinn, Steuernachforderung, Börsenverluste … |
| `0x005E3CA8` | 1417, 1418, 1420–1422 | Gruppen im Kader: Auftreten gegenüber dem Präsidenten |
| `0x005E447D` | 1423–1427 | Gruppen im Kader: Beitritt, Austritt |
| `0x005F05CE` | 871 | Ihr Amateurspieler %s verläßt den Verein. |
| `0x005F8393` | 1024 | Blumen zum Geburtstag der Frau |
| `0x005F84CB` | 1029–1034 | Hochzeitstag vergessen |
| `0x005FA0C7` | 1087–1092 | Spieler steht kurz davor, Vater zu werden |
| `0x005FC9EE` | 1238–1242 | Beziehungskrise |
| `0x005FD0F5` | 1250 | Spieler will nichts mehr mit Frauen zu tun haben |
| `0x0060AE6C`, `0x0060B11E` | 459, 460, 462–464, 471–476 | Verfehlungen der Spieler: unentschuldigt gefehlt, Alkoholfahrt, negatives Interview, ohne Abmeldung in die Heimat … |
| `0x0061A033`, `0x0061A1A0`, `0x0061A29A`, `0x0061A31C` | 305, 307, 315–317, 2346–2362 | alte Ereignistexte und Fangesänge |
| `0x0061B464` | 2423–2429 | Fangesänge |
| `0x0061B898` | 2444–2455 | Fangesänge |

Zusammen 18 Routinen und 94 Texte.

- `0x005E1C68`: Die ältere Fassung einzelner dieser Ereignisse ist erreichbar (zum Beispiel Text 300 „Marmorgrube in
  Peru“ in `0x00602594`).
- `0x0060B430(Verein, Manager)` geht den Kader durch und lost aus den Tabellen `0x00A3271C` / `0x00A32710`; da niemand
  die Routine aufruft, gibt es die Verfehlungen der Spieler im Spiel nicht.
- Die Routinen ab `0x0061A033` liegen im Bereich der Spieltexte, der sonst nicht geprüft wird („Stand und Umfang“).
- Im Ereignisbereich werden 63 weitere Routinen ohne feste Textstelle nie ausgeführt (Liste in der Ausgabe von
  `meld14.py`), darunter `0x005F1E1A` und `0x005F1E3A`.
- Ob diese Ereignisse absichtlich stillgelegt wurden, ist nicht erkennbar (V).

**Zwei Fehlalarme (G):** Zwischenzeitlich galten die Stellen `0x005EA581` (Text 285) und `0x005F4997` (Text 273) als
„Stelle in unerreichbarem Code“. Ursache war das Disassembly: 192 Routinenanfänge direkt hinter Sprungtabellen waren im
dumpbin-Listing verstümmelt (`dis_reparatur.py` hat sie neu zerlegt und in `dis.pkl` eingefügt; die Textdatei des
Listings ist unverändert). Die beiden Stellen gehören zu den erreichbaren Routinen `0x005EA51C` (Fragen-Datensatz 19,
Frage formatieren) und `0x005F4972` (Fragen-Datensatz 2, Auswertung). Beide Texte sind erreichbar.

## 3. Einzelne Texte, die nie erscheinen können (G)
### 3.1 Verteiler mit zu kleiner Zufallszahl: 1178, 1179
In `0x005FD59D` (Privatleben) steht bei `0x005FDBAE`: Zufall 0–1 (`push 2 / call 0x0078A810`), danach ein Verteiler
über vier Fälle (Tabelle `0x005FECC0`: `0x005FDBD8`, `0x005FDC60`, `0x005FDCE8`, `0x005FDD4C`). Die Fälle 2 und 3 sind
nie erreichbar:
- Fall 2: Text 1178 („… beim Spielen eines 3D-Shooters zugeschaut …“),
- Fall 3: Text 1179 („Bei Motion Capturing-Aufnahmen für ein Computerspiel hat sich Ihr Spieler %1 den Arm gebrochen …“).
Erreichbar sind die Fälle 0 und 1 (Texte 1174–1177, Namenswahl für ein Kind).

### 3.2 Tabelle größer als der Zufallsbereich: 888, 889
Die Gründe für eine Bauverzögerung stehen in der Tabelle `0x0088EC8C` mit 12 Einträgen (Texte 878–889). Gewürfelt
wird bei `0x00602373` aber nur Zufall 0–9. Die beiden letzten Einträge, 888 und 889, werden nie gewählt.

### 3.3 Fall ohne Los-Nummer: 1289
Im Verteiler der allgemeinen Spieler-Ereignisse `0x005E08F1` gibt es einen Fall 48 (Text 1289), aber die
Gewichtstabelle enthält die Nummer 48 nicht. Die Variable kommt nur aus der Auslosung; der Fall ist unerreichbar.

### 3.4 Bedingung im falschen Zweig: 1481
Bei `0x0076898B` steht die Bedingung „Alter unter 20“ innerhalb des Zweigs „Alter ab 25“ (`0x0076894B` →
`0x00768962`). Sie ist nie wahr, Text 1481 erscheint nie.

### 3.5 Fest abgeschalteter Block: Stelle `0x0060C687` (Texte 832–847)
Der Block ist durch `mov eax,1 / test / je` fest abgeschaltet. Nach Angabe des Tabellenlaufs sind dieselben Texte an
`0x0060C754` / `0x0060C7E4` erreichbar; das ist nicht von Hand bestätigt (Abschnitt 7).

## 4. Zeitungsmeldungen: übergebene Wirkung (G)
`0x00789C32(Rang, Text, Anzahl Namen, Kennzeichen, Namen …, Nummern …, Werte …)`: Mit `0x40000000` folgt eine
Managernummer, mit `0x80000000` eine Spielernummer, mit `0x20000000` Land und Verein; für jedes gesetzte Bit 0–28 folgt
ein Wert, abgelegt bei Satz + 8 + 4 × Bit. Die Namen werden nach `0x008AD230[i]` kopiert. Die Reihenfolge der
Argumente ist am Code bestätigt: Rang, Text, Anzahl Namen, Kennzeichen, Namen, Managernummer (→ Satz +0),
Spielernummer (→ +2), Land/Verein (→ +4/+6), Werte. Die oberste Schlagzeile des Tages (Platz `0x01C6AC84`) wendet
`0x0078A0F5` an, und nur wenn `0x00789998` ≠ 0 liefert:
- Manager (nur wenn eine Managernummer im Satz steht): Werte der Bits 0–3 über `0x0041849A`, Bit 4 über `0x006A58FC`;
- Spieler (nur mit Spielernummer): Bit 8 = „Presse“ (`0x00700FA2`), Bit 9 = Spielersatz 0x274 (`0x00701210`);
- Verein (nur mit Land und Verein): Bit 10 über `0x0069EFE8`, Bit 11 über `0x00698EF6`.

Berichtigung gegenüber der ersten Fassung: `0x00701210` ändert im Spielersatz das Byte 0x274, `0x007010D9` das Byte
0x273 (beides Teilwerte der Motivation; früher stand `0x00701210` als „V: Privat“). 0x274 ist die Ablenkung
(Abschnitt 6.9).

Eine Schlagzeile, die einen Wert ohne die passende Nummer übergibt, ändert auf diesem Weg nichts. Viele Stellen
wenden den Wert deshalb direkt nach dem Aufruf selbst an. Acht tun das nicht:

| Text | Schlagzeile | Übergeben | Was die Stelle sonst tut |
|---|---|---|---|
| 1125 | Frau von %1 bei Banküberfall erwischt | Presse −3 | ändert stattdessen Spielersatz 0x274 (`0x00701210`) und 0x273 (`0x007010D9`) |
| 1188 | Schönheitsoperation bei %1 | Presse −4 | nur Meldung 1187 an den Manager |
| 1197 | %1 steht vor dem Nichts | Presse −3 | Spielersatz 0x274 (`0x00701210`) −10, Meldung 1196 |
| 1201 | %1 geht lieber Golfen – Millionengehalt für nichts | Presse −2 | nichts |
| 1235 | Goldkettchen und teure Autos | Presse −2 | nichts (Korrektur `goldkettchen` wendet den Abzug an) |
| 1269 | %1 pöbelt friedliche Passanten an | Presse −4 | setzt ein Kennzeichen beim Spieler (`0x00702D95(2)`), Meldung 1268 |
| 1528 | %1 mit schweren Vorwürfen gegen den Trainer | Presse −4 | nur Meldung 1527 |
| 1530 | %1 kritisiert Trainer %2 | Presse −4 | nur Meldung 1529 |

Ob der Abzug an diesen Stellen gewollt war und vergessen wurde, ist nicht belegbar (V); bei den Schwestermeldungen
derselben Routinen (zum Beispiel 1186, 1218, 1229, 1231, 1234, 1520–1524) wird er angewendet.
Bei elf weiteren Aufrufen wird ein Managerwert ohne Managernummer übergeben; fünf davon ändern direkt danach den
Vereinszähler über `0x0069FE73` (Abschnitt 5), bei den übrigen ist nicht geprüft, ob der Wert auf anderem Weg ankommt.

### Falsche Argumentzahl (G, `meld13.py` → `zeitung_argumente.tsv`)
66 der 70 Aufrufe übergeben genau so viele Argumente, wie ihre Kennzeichen verlangen. Vier nicht:
- **1743** (`0x00537ADD`) und **1744** (`0x00537B15`), Routine `0x005378D6`: Kennzeichen 8, übergeben werden aber
  Name, Managernummer und Wert (+5 bzw. −10). Das Kennzeichen `0x40000000` fehlt. Als Wert für Bit 3 wird deshalb die
  Managernummer gelesen, der eigentliche Wert bleibt liegen, und weil keine Managernummer im Satz steht, wird nichts
  angewendet.
- **1750** (`0x0053CD00`), Routine `0x0053CBDF`: Kennzeichen 1, aber kein Wert übergeben. Der Wert für Bit 0 ist ein
  zufälliger Stapelinhalt; ohne Managernummer wird er nicht angewendet. Die Schwestermeldung 1751 (`0x0053CD32`)
  übergibt −4, ebenfalls ohne Managernummer.
- **1880** (`0x005F47A7`), Routine `0x005F3BAF`, Los-Nummer 29 mit Gewicht 1 von 69 (Meldung 1879 an den Manager):
  Kennzeichen `0x40000001`, übergeben werden zwei Namen und −5. Die Managernummer fehlt. Als Managernummer wird −5
  (0xFFFB) in den Satz geschrieben, als Wert für Bit 0 ein zufälliger Stapelinhalt. Wird die Schlagzeile die oberste
  des Tages, ruft `0x0078A0F5` damit `0x006A426B(−5)` auf. Diese Routine rechnet mit dem statischen Managersatz
  `0x00A62578 + (Nr−1) × 0x2158`, dem Merker `word [Nr×2 + 0x00B5CB9A]` und dem Zähler `word [Nr×2 + 0x01B9FFAA]` –
  mit Nr = −5 liegt alles außerhalb der Felder. **Offen:** was dabei genau gelesen oder überschrieben wird
  (`0x006A426B`, `0x0041849A`, `0x006A4917` sind dafür nicht zu Ende gelesen).

Gelesene Auslöser dieser Meldungen:
- 1201: Spielerfeld +0x88 über 1000 (V: Gehalt), mehr als 10 gespielte Spieltage, kein Einsatz in der Saison (+0x54 = 0).
- 1188: mehr als 10 Spieltage, Verein mehr als 2 hinter den Erwartungen (`0x00775F0A`), `0x0069947B(Verein)` ≠ 0.
- 1528 / 1530: Verein hinter den Erwartungen (`0x00775F0A` > 0), Wert von `0x007701B2` unter 80.
- 1269: Spielereigenschaft Bit 0x200 im Wort +0x12, Verein nicht hinter den Erwartungen (`0x00775F0A` = 0).

### Alle 70 Aufrufe der Zeitungsroutine
Spalte „Wirkung“: maschinell aus den Kennzeichen und den Aufrufen direkt hinter der Stelle bestimmt (`meld6.py`);
fett markierte Zeilen sind zusätzlich von Hand gelesen, wenn kein Vermerk dabeisteht.

| Text | Wortlaut | Stelle | Rang | Kennzeichen | Wirkung |
|---|---|---|---|---|---|
| 1697 | Trainer unzufrieden mit der Leistung - %1 machte %2 in der Halbzeit z… | `0x004917FB` | 7 | 0x4 | Managerwert ohne Managernummer übergeben; direkt danach geändert: Vereinswert 0xDF8 |
| 1698 | "Bei einigen liegen die Nerven blank!" - Trainer %1 bei %2 als Psycho… | `0x00491F4A` | 7 | 0x4 | Managerwert ohne Managernummer übergeben; direkt danach geändert: Vereinswert 0xDF8, Trainer |
| 1743 | %1 der richtige Mann am richtigen Ort - Weiß das Präsidium überhaupt,… | `0x00537ADD` | 6 | 0x8 | **falsche Argumentzahl:** Kennzeichen 0x40000000 fehlt, Managernummer wird als Wert gelesen; nichts wird angewendet |
| 1744 | %1 kritisiert den Vorstand - Vereinsführung ist nicht professionell g… | `0x00537B15` | 7 | 0x8 | **falsche Argumentzahl:** Kennzeichen 0x40000000 fehlt, Managernummer wird als Wert gelesen; nichts wird angewendet |
| ? | (Nummer aus einer Variablen) | `0x00537B8C` | 6 | 0x1 | Managerwert ohne Managernummer übergeben; ob er auf anderem Weg angewendet wird, ist nicht geprüft |
| ? | (Nummer aus einer Variablen) | `0x00537BDA` | 6 | 0x1 | Managerwert ohne Managernummer übergeben; ob er auf anderem Weg angewendet wird, ist nicht geprüft |
| 1750 | %1 hat die Schnauze voll - %2 als Schiedsrichter wird in Zukunft abge… | `0x0053CD00` | 5 | 0x1 | **falsche Argumentzahl:** kein Wert übergeben (zufälliger Stapelinhalt); ohne Managernummer nicht angewendet |
| 1751 | %1 sauer auf %2 - %3 lehnt den Schiedsrichter für die Zukunft ab | `0x0053CD32` | 5 | 0x1 | Managerwert ohne Managernummer übergeben; ob er auf anderem Weg angewendet wird, ist nicht geprüft |
| 1269 | %1 pöbelt friedliche Passanten an - Kann sich %2 einen solchen Spiele… | `0x005E0F36` | 7 | 0x100 | **übergebener Wert bleibt ohne Wirkung** |
| 1701 | "Mehrheit der Spieler ist gegen den Trainer!" - Neue, eigentlich gehe… | `0x005E52C8` | 6 | 0x0 | kein Wert übergeben |
| 1702 | "Mindestens 5 wollen weg!" - Nur bei uns: Internes aus dem Mannschaft… | `0x005E5335` | 6 | 0x0 | kein Wert übergeben |
| 1703 | Maulwurf %1 verrät Interna - %2 ist die undichte Stelle noch ein Räts… | `0x005E543D` | 8 | 0x4 | Managerwert ohne Managernummer übergeben; ob er auf anderem Weg angewendet wird, ist nicht geprüft |
| 1704 | Trainer %1 hat freie Hand - Präsident schließt harte Maßnahmen nicht … | `0x005E54AE` | 8 | 0x0 | kein Wert übergeben |
| 1705 | %1 vollkommen hilflos - Wer ist der geheimnisvolle Maulwurf %2? | `0x005E54E2` | 8 | 0x4 | Managerwert ohne Managernummer übergeben; ob er auf anderem Weg angewendet wird, ist nicht geprüft |
| 1706 | Maulwurfsaffäre weitet sich aus - Präsident %1 fordert %2 zum Handeln… | `0x005E5553` | 8 | 0x40000008 | Wert wird über die Schlagzeile angewendet (nur als oberste Schlagzeile) |
| 1707 | %1 läßt Maulwurf gewähren - Atmosphäre %2 total vergiftet | `0x005E55B2` | 8 | 0x20000800 | Wert wird über die Schlagzeile angewendet (nur als oberste Schlagzeile) |
| 1708 | Präsident %1: "Akzeptiere Tatenlosingkeit nicht!" -%2 gerät in der Ma… | `0x005E5630` | 9 | 0x40000008 | Wert wird über die Schlagzeile angewendet (nur als oberste Schlagzeile) |
| 1519 | %1 erneut ein Totalausfall - %2: Wie lange müssen wir ihn noch ertrag… | `0x005E57E0` | 7 | 0x4 | Managerwert ohne Managernummer übergeben; direkt danach geändert: Presse |
| 1520 | %1 als Symbol für die Krise - Der Liebling des Trainers vor dem Aus? | `0x005E584B` | 7 | 0x100 | Wert ohne Spielernummer übergeben; direkt danach angewendet (Presse) |
| 1521 | Sensibelchen %1 völlig verunsichert - Hat ihn auch der Trainerstab au… | `0x005E58B2` | 7 | 0x100 | Wert ohne Spielernummer übergeben; direkt danach angewendet (Presse) |
| 1522 | %1 vor Wechsel ins Ausland - Das Fußball-Magazin kennt alle Fakten | `0x005E5904` | 7 | 0x100 | Wert ohne Spielernummer übergeben; direkt danach angewendet (Presse) |
| 1523 | %1 reif für die Nationalelf - Berufung nur noch eine Frage der Zeit | `0x005E595D` | 7 | 0x200 | Wert ohne Spielernummer übergeben; direkt danach angewendet (Spielersatz 0x274) |
| 1524 | Millionär und doch nicht glücklich? - Alle Details über das Privatleb… | `0x005E59BD` | 6 | 0x100 | Wert ohne Spielernummer übergeben; direkt danach angewendet (Presse) |
| 1528 | %1 mit schweren Vorwürfen gegen den Trainer - Trainingsmethodik von %… | `0x005E5C07` | 8 | 0x100 | **übergebener Wert bleibt ohne Wirkung** |
| 1530 | %1 kritisiert Trainer %2 - Ungenügende Fitneß der Mannschaft für schl… | `0x005E5D2D` | 8 | 0x100 | **übergebener Wert bleibt ohne Wirkung** |
| 1573 | Feiern, feiern, feiern - %1 und %2 auf seltsamen Abwegen | `0x005F0BA7` | 7 | 0x0 | kein Wert übergeben |
| 1575 | Alkohol als Therapie - Erfahrener Trainerfuchs %1 greift zum letzten … | `0x005F0C5F` | 3 | 0x0 | kein Wert übergeben |
| 1576 | Spieler %1 auf Sauftour - Wie weit sinkt dieser Club noch? | `0x005F0CC3` | 8 | 0x0 | kein Wert übergeben |
| 1577 | %1 voll wie ein Eimer - Sauftour %2 sorgt für viel Wirbel | `0x005F0CFE` | 7 | 0x0 | kein Wert übergeben |
| 1578 | Randale in Nobelkneipe - Torkelnde Spieler und Trainer %1 lag unter d… | `0x005F0D1A` | 5 | 0x0 | kein Wert übergeben |
| 1579 | Alkohol gegen den Frust - %1 mit %2 endgültig am Boden | `0x005F0D52` | 5 | 0x0 | kein Wert übergeben |
| 1580 | Schlägerei bei Saufabend - Unglaubliche Ereignisse %1 | `0x005F0E00` | 9 | 0x0 | kein Wert übergeben |
| 1581 | Mannschaft ignoriert "verordneten" Saufabend - %1 von Polizei völlig … | `0x005F0E26` | 9 | 0x0 | kein Wert übergeben |
| 1591 | %1 als Knecht Ruprecht - Trainer erwartet Leistungssteigerung im neue… | `0x005F0F8A` | 6 | 0x0 | kein Wert übergeben |
| 1590 | Weihnachtsfeier %1 - Viel Lob für ein erfolgreiches Jahr | `0x005F0FF4` | 5 | 0x0 | kein Wert übergeben |
| 1621 | Mißstimmung beim Sponsorentag - %2 und %1 werden keine Freunde mehr | `0x005F1535` | 3 | 0x0 | kein Wert übergeben |
| 1637 | %1 muß Meisterfeier absagen - Hohn und Spott für %2 | `0x005F1A18` | 9 | 0x0 | kein Wert übergeben |
| 1638 | Ein historischer Tag! - %1 erstmals in der Vereinsgeschichte Meister | `0x005F1A5B` | 10 | 0x0 | kein Wert übergeben |
| 1639 | Nach so vielen Jahren! - Meisterfeier %1 mobilisierte die Massen | `0x005F1AA3` | 9 | 0x0 | kein Wert übergeben |
| 1640 | Alle Jahre wieder... - Meisterfeier %1 | `0x005F1AE9` | 8 | 0x0 | kein Wert übergeben |
| 1641 | %1 im Freudentaumel - Die ganze Stadt war auf den Beinen! | `0x005F1B1F` | 9 | 0x0 | kein Wert übergeben |
| 1880 | Trauer in %1 - %2 stirbt vollgepumpt mit Drogen an Herzversagen | `0x005F47A7` | 10 | 0x40000001 | **falsche Argumentzahl:** Managernummer fehlt, −5 wird als Managernummer gespeichert; Folge offen |
| 1125 | Frau von %1 bei Banküberfall erwischt - Verdient man %2 so schlecht? | `0x005FB535` | 7 | 0x100 | **übergebener Wert bleibt ohne Wirkung**; geändert wird stattdessen: Spielersatz 0x274 und 0x273 |
| 1170 | Skandalbuch von %1 sorgt für Wirbel - Helle Aufregung um Dopingenthül… | `0x005FDADA` | 8 | 0x0 | kein Wert übergeben |
| 1186 | Frauen ziehen ihn magisch an - Exklusive Bilder der neuen Freundin vo… | `0x005FDEDA` | 6 | 0x100 | Wert ohne Spielernummer übergeben; direkt danach angewendet (Presse) |
| 1188 | Schönheitsoperation bei %1 - Von 100% Konzentration auf den Fußball n… | `0x005FDF80` | 6 | 0x100 | **übergebener Wert bleibt ohne Wirkung** |
| 1197 | %1 steht vor dem Nichts - Spieler %2 verspielte auch seinen letzten P… | `0x005FE0E9` | 6 | 0x100 | **übergebener Wert bleibt ohne Wirkung**; geändert wird stattdessen: Spielersatz 0x274 |
| 1201 | %1 geht lieber Golfen - %2 Millionengehalt für nichts | `0x005FE290` | 5 | 0x100 | **übergebener Wert bleibt ohne Wirkung** |
| 1218 | %1 beim Rasen erwischt - Fußballprofi mußte Führerschein abgeben | `0x005FE6CA` | 5 | 0x100 | Wert ohne Spielernummer übergeben; direkt danach angewendet (Presse) |
| 1229 | Sportwagen von Frau im Pool versenkt - %1 konnte es nicht fassen | `0x005FEA4E` | 6 | 0x100 | Wert ohne Spielernummer übergeben; direkt danach angewendet (Presse) |
| 1231 | Frau %1 parkte im Wohnzimmer - %2 konnte es nicht fassen | `0x005FEADA` | 6 | 0x100 | Wert ohne Spielernummer übergeben; direkt danach angewendet (Presse) |
| 1234 | %1 beim Rasen erwischt - Fußballprofi mußte Führerschein abgeben | `0x005FEB92` | 6 | 0x100 | Wert ohne Spielernummer übergeben; direkt danach angewendet (Presse) |
| 1235 | Goldkettchen und teure Autos - %1 ein Prototyp des verzogenen Fußball… | `0x005FEC31` | 6 | 0x100 | **übergebener Wert bleibt ohne Wirkung** |
| 1938 | %1 lehnt Bungeesprung ab - Ist der harte Hund nur ein kleiner Feiglin… | `0x00608F32` | 6 | 0x40000001 | Wert wird über die Schlagzeile angewendet (nur als oberste Schlagzeile) |
| 1940 | Meisterschale geklaut - Trainer %1 unter den Verdächtigen | `0x00608FF6` | 7 | 0x40000001 | Wert wird über die Schlagzeile angewendet (nur als oberste Schlagzeile) |
| 1693 | Trainer %1 hatte Schaum vor dem Mund - Spieler lachten ihn nach der H… | `0x0064B3F2` | 8 | 0x4 | Managerwert ohne Managernummer übergeben; direkt danach geändert: Vereinswert 0xDF8 |
| 1692 | %1 rastete in der Halbzeit aus - Trainer %2 beschimpfte seine Spieler | `0x0064B40E` | 7 | 0x0 | kein Wert übergeben |
| 1695 | "%1 macht sich zum Idioten!" - Spieler lachen nicht mehr nur hinter v… | `0x0064B59F` | 10 | 0x2 | Managerwert ohne Managernummer übergeben; direkt danach geändert: Vereinswert 0xDF8 |
| 1694 | Trainer %1 griff zum letzten Mittel - %2 appellierte flehend an die E… | `0x0064B5C4` | 10 | 0x2 | Managerwert ohne Managernummer übergeben; direkt danach geändert: Vereinswert 0xDF8 |
| 1643 | Meisterfeier einfach vergessen - Titel %1 nur noch Routine? | `0x006A75B5` | 8 | 0x0 | kein Wert übergeben |
| 1644 | %1 vergißt die Meisterfeier - Spieler und Fans sind stocksauer | `0x006A75E2` | 8 | 0x0 | kein Wert übergeben |
| 1645 | Keine Feier trotz Titel %1 - Peinliches Versäumnis trübt die Freude | `0x006A75FE` | 8 | 0x0 | kein Wert übergeben |
| 1652 | %1 zunächst Interimstrainer - %2 auf der Suche nach endgültiger Lösung | `0x006C2BC5` | 2 | 0x0 | kein Wert übergeben |
| 1653 | %1 nur Übergangslösung? - Vorstand %2 weiter auf Trainersuche | `0x006C2DD9` | 8 | 0x0 | kein Wert übergeben |
| 1654 | %1 muß sich bewähren - Vorstand %2 über Cheftrainernachfolge uneins | `0x006C2E6C` | 8 | 0x0 | kein Wert übergeben |
| 1655 | Vorstand spricht %1 das Vertrauen aus - Präsident %2 hält Ex-Amateurt… | `0x006C2FC2` | 8 | 0x0 | kein Wert übergeben |
| 1655 | Vorstand spricht %1 das Vertrauen aus - Präsident %2 hält Ex-Amateurt… | `0x006C3131` | 8 | 0x0 | kein Wert übergeben |
| 1667 | %1 wechselt %2 - Wechsel zum Saisonende ist ablösefrei | `0x0070CAEA` | 6 | 0x0 | kein Wert übergeben |
| 1668 | %1 wechselt zum Nulltarif %2 - Einsatz ab sofort möglich | `0x0070CCF3` | 6 | 0x0 | kein Wert übergeben |
| 1669 | %1 %2 verpflichtet - %4 gehen an %3 | `0x0070CD63` | 6 | 0x0 | kein Wert übergeben |

Zählung: 32 × kein Wert übergeben; 11 × Managerwert ohne Managernummer übergeben; 10 × Wert ohne Spielernummer übergeben; 8 × **übergebener Wert bleibt ohne Wirkung**; 5 × Wert wird über die Schlagzeile angewendet; 4 × **falsche Argumentzahl**

## 5. Vereinszähler in Verein +0xDF8, Bits 18–20 (G)
- `0x0069FE73(Änderung)`: Wert = Bits 18–20 (0–7) + Änderung, begrenzt auf 0–15, zurückgeschrieben mit `<< 18`,
  danach wird Bit 21 gelöscht. Ein Ergebnis von 8 bis 15 verliert dadurch sein oberstes Bit (aus 7 + 1 wird 0).
- Bit 21 ist der Merker „Schlagzeile zu diesem Zählerstand schon erschienen“ (gesetzt bei `0x005E5650` am Ende der
  Maulwurf-Folge, geprüft bei `0x005E536D`). Jeder Aufruf von `0x0069FE73` löscht ihn, ebenso `0x0069FF06` – das ist
  Absicht: nach einer Änderung des Zählers soll die Schlagzeile zum neuen Stand kommen können. (Berichtigt
  17.11.2026; vorher stand hier, es werde ein fremder Merker gelöscht.)
- Der Zähler hat überall 3 Bits (Maske `0x1C0000` im Leser `0x0069FE57`, in `0x0069FE73` und im Setzer
  `0x0069FF06`), ausgewertet werden aber die Stände 2, 3, 5, 6, 8 und 10 (Texte 1703–1708, `0x005E5408` ff.): die
  Schlagzeilen 1707 und 1708 können nie erscheinen.
- Alle sechs Aufrufer übergeben +1: die Halbzeit-Schlagzeilen `0x0049180E` (1697), `0x00491F5D` (1698), `0x0064B41B`
  (1692/1693), `0x0064B5D1` (1694/1695) und die Maulwurf-Routine `0x005E50BA` bei 1701 (`0x005E52EC`, einmal je Saison
  wegen Merker 0x10000) und 1702 (`0x005E535A`, Merker 0x20000).
- Gelesen wird der Zähler nur in `0x005E50BA` (`0x005E53F5`: Stufe 2 → Text 1703 …). Auf 0 gesetzt wird er nur beim
  Saisonwechsel (`0x0077360D` in `0x00772BEE` ruft `0x0069FF06(0)`); dort werden auch die Merker gelöscht.
- Folge (G für die Rechnung): Ab der achten Erhöhung innerhalb einer Saison springt der Zähler von 7 auf 0, und die
  Schlagzeilen 1703–1706 können ein zweites Mal kommen.
- Nachgelesen am 17.11.2026 (vorher offen): Alle vier Halbzeit-Stellen verlangen über `0x006493E0` einen Maulwurf
  (Bit 16 im Flagwort des Spielers) unter den 11 + 7 Spielern der Aufstellung; eine Grenze je Saison gibt es dort
  nicht. Einen Maulwurf bestimmt `0x005E50BA` nur unter Spielern mit Gesamtmotivation unter 70 und mindestens zwei
  von drei Teilwerten unter 88; er bleibt es, bis die Motivation über 85 steigt. Ohne Maulwurf erscheint keine dieser
  Schlagzeilen (Beobachtung des Nutzers: nie eine gesehen). Der Überlauf ist also möglich, aber nur in einer Saison
  mit Maulwurf und acht Schlagzeilen. Einzelheiten und Korrektur: `docs/korrekturliste-meldungen.md` (K11, K11-B).

## 6. Weitere bestätigte Fehler (G)
### 6.1 Streichen aus der zweiten Dreierliste eines Spielers löscht in der ersten (`0x00703930`)
Jeder Spieler hat zwei Listen mit je drei Spielernummern: die erste im statischen Satz bei +0x1F8 (Spielstand 0x1D8),
die zweite bei +0x1FE (Spielstand 0x1DE). Nach den Aufrufstellen ist die erste die Liste der Freunde, die zweite die
zu Streit und Feinden (V). `0x00703930` streicht einen Spieler aus der zweiten Liste. Nach dem Aufrücken schreibt
`0x007039D0` die abschließende 0 aber nach `+0x1F8 + 2·i` (erste Liste) statt nach `+0x1FE + 2·i`. Die
Schwesterroutine `0x00703854` für die erste Liste schreibt richtig nach +0x1F8.
Folge: Der dritte Platz der ersten Liste wird gelöscht, der dritte Platz der zweiten bleibt stehen.
Aufrufer: `0x00703C28`, `0x00703CE5`, `0x00703D61`, `0x00703D8C`, `0x00703DF4` (Texte 1362, 1366, 1377, 1380 …).

### 6.2 Straf-Frage, Stufe 1: Antworten und Wirkung passen nicht zusammen (`0x005F29BC`)
`0x005F29BC(Manager, Verein, Text, Spieler, Stufe 1–3)` stellt die Frage nach einer Strafe für einen Spieler
(26 Aufrufe, vor allem in `0x005E08F1`).

| Stufe (Datensatz) | Antwort 0 | Antwort 1 | Antwort 2 |
|---|---|---|---|
| 1 (34) | 1566 „1 Spiel interne Sperre“ | 1567 „%4 Strafe“ | 1568 „Nicht so schlimm“ |
| 2 (35) | 1569 „3 Spiele interne Sperre“ | 1566 „1 Spiel …“ | 1570 „%4 Strafe“ |
| 3 (36) | 1571 „Suspendieren“ | 1569 „3 Spiele …“ | 1572 „%4 Strafe“ |

Der Code wertet alle drei Stufen nach demselben Muster aus: Antwort 0 und 1 = Abzug beim Trainer-Teilwert,
Antwort 2 = Betrag auf Verein +0x28C. Das passt zu den Stufen 2 und 3. Bei Stufe 1 (`0x005F2C3C`–`0x005F2C93`) passt
es nicht:
- „1 Spiel interne Sperre“ setzt keine Sperre (kein Aufruf von `0x0070302D`), nur −10;
- „%4 Strafe“ bucht kein Geld, nur −2;
- „Nicht so schlimm“ bucht die Strafe als Betrag.

### 6.3 Fest abgeschaltete Zweige
- `0x005F2E43` und `0x005F2F07` (in derselben Routine): `xor eax,eax / test / je`. Die Zweige „+2“ (Stufe 2) und
  „+3“ (Stufe 3) für das Byte Verein +0xA7 sind fest abgeschaltet; es gilt immer +1 bzw. +2.
- `0x0060C687`: siehe Abschnitt 3.5.

### 6.4 Fragen-Datensätze, die nie benutzt werden
Von den 80 Datensätzen (Abschnitt 1) haben diese einen eigenen Inhalt, werden aber nie geöffnet (`meld11.py`,
`fragen.txt`):

| Datensatz | Texte |
|---|---|
| 12 | 415, 416, 418 |
| 20 und 21 | 852, 853, 854, 855 |
| 22 | 856–858 |
| 24 | 577–579 |
| 31 | 897 |
| 33 | 901 |
| 64 | 1911, 1912 |

Die übrigen unbenutzten Datensätze sind Platzhalter (Frage 1646). **Offen:** Die Datensätze 10 und 11 werden über
`0x006062FE` mit Index = Variable + 10 angesprochen; der Wertebereich der Variablen ist nicht gelesen. Zu
Datensatz 12 siehe auch Abschnitt 7.

### 6.5 Ehefrau des Managers: Texte 1728 und 1733 fehlen in der Tabelle
Datensatz 42 (Frage 1725, Routinen `0x005EECBA` / `0x005EEDF9`, aufgerufen aus `0x005F5556`): Die Eigenschaft kommt
aus der Tabelle `0x0088E0D8` mit sieben Einträgen (1726, 1727, 1729, 1730, 1731, 1732, 1734), Index aus `0x00A3220A`.
Die Texte 1728 und 1733 aus derselben Reihe stehen nicht in der Tabelle. Antworttexte: Zufall 0–3 ≠ 0 →
`0x0088E0EC[Zufall 0–3]` = 1735–1738, sonst `0x0088E0F4[Zufall 0–1]` = 1739, 1740.
**Offen:** der Wertebereich des Index aus `0x00A3220A` (ob alle sieben Einträge erreicht werden).

Die Abschnitte 6.6 bis 6.12 stammen aus dem Katalog des Lesepakets P02 und sind am 16.11.2026 einzeln von Hand am Code
nachgeprüft.

### 6.6 „%s“ statt „%1“: der Spielername erscheint nicht (954, 1276, 1338, 1355)
Die Meldungsroutinen `0x00600F2F` und `0x00601043` setzen Namen nur über `0x005EEE7F` ein. Diese Routine ersetzt
allein „%“ gefolgt von einer Ziffer 1–9 (`0x005EEEA6`–`0x005EEEC9`); alles andere kopiert sie unverändert. Vier Texte,
die über diese Routinen ausgegeben werden, enthalten aber „%s“:

| Text | Stelle | Routine | Wortlaut |
|---|---|---|---|
| 954 | `0x005E4B5B` | `0x00600F2F` | Ihr Spieler %s kommt nach dem Training zu Ihnen … |
| 1276 | `0x005E112F` | `0x00600F2F` | Ihr Spieler %s wurde bei einer Bordellrazzia von der Polizei verhaftet. |
| 1338 | `0x005E25B2` | `0x00601043` | Die Computerfirma Ihres Spielers %1 muß leider Konkurs anmelden. Die Geschichte ist für %s ein teurer Spaß … |
| 1355 | `0x005E2B2B` | `0x00601043` | Ihr Spieler %s macht in den nächsten Tagen einen Werbespot … |

Das „%s“ bleibt im Meldungstext stehen. Die Meldungsdialoge geben den Text aus dem Puffer `0x00A2F700` unverändert
an ihr Textfeld weiter (`0x004951DB`, `0x004959AC`, `0x0049622E`, `0x004966E0`, jeweils eine virtuelle Methode); das
Textfeld selbst ist nicht gelesen. Dass wörtlich „%s“ erscheint, ist damit sehr wahrscheinlich und im Spiel zu sehen.
(1355 ist zusätzlich von 6.12 betroffen.)

### 6.7 Der Name der Frau bleibt leer (969, 1296)
- 969 („Seine Frau %2 fände diese Idee auch einfach großartig“): Der Aufruf bei `0x005E4D2A` übergibt als zweiten
  Namen 0 (`0x005E4D17`–`0x005E4D19`); `0x00600F2F` setzt dafür eine leere Zeichenkette ein (`0x00600F90`).
- 1296 („Ich möchte lieber bei meiner Frau %2 bleiben“): Die Frage läuft über `0x005F29BC` (`0x005E15ED`), das als
  zweiten Namen immer eine leere Zeichenkette übergibt (`0x005F2A66`, `0x005F2A7B`).
Der Name der Frau (`0x0070173F`) wird in beiden Fällen nicht geholt; an anderer Stelle derselben Routine wird er
übergeben (`0x005E0EC1`, Text 1267).

### 6.8 Frage ohne Spielernamen (1294)
Text 1294 („Der Rasen auf diesem Trainingsplatz …“, meint er und geht nach Hause.) enthält keinen Platzhalter. Er wird
bei `0x005E1541` als Straf-Frage Stufe 2 gestellt; der Manager wählt also eine Strafe für einen Spieler, den die Frage
nicht nennt.

### 6.9 Meldung mit Vorher/Nachher: falscher Vorher-Wert, falsche Beschriftung (1309–1312)
- Die Leser der Teilwerte rechnen Zu- und Abschläge je gesetztem Spieler-Flag ein: `0x007008B9` (Trainer, −10 je
  Flag), `0x00700C42` (Mannschaft), `0x00700E3F` (Verein). Die Schreiber `0x007007A1`, `0x00700A6D`, `0x00700D27`
  liefern dagegen den gespeicherten Wert ohne diese Zuschläge zurück. Die Fälle zu 1309 (`0x005E184F`–`0x005E189B`),
  1310 (`0x005E1906`) und 1311 nehmen „Vorher“ vom Leser und „Nachher“ vom Schreiber. Hat der Spieler eines der
  Flags, zeigt die Meldung eine falsche Differenz. Die Wirkung selbst ist richtig; betroffen ist nur die Anzeige.
  Ob andere Stellen des Programms dasselbe Muster haben, ist nicht geprüft.
- 1312 (`0x005E19DC`): Geändert und angezeigt wird Spielersatz 0x274 (`0x00701328`, `0x00701210(−5)`), als Art wird
  aber 1 übergeben (`0x005E19C9`). Die Stelle zu 1256 übergibt für denselben Teilwert Art 3 (`0x005E0A81`); Art 1
  benutzen die Fälle zu 1310/1311, die Spielersatz 0x270 ändern. Die Art wählt die Beschriftung in der Meldung:
  `0x005F1F42` legt sie in `0x00A2F6EE` ab (Vorher `0x00A2F6F4`, Nachher `0x00A2F6F6`), der Dialog holt damit bei
  `0x004953E1` einen Text aus der Tabelle `0x008808B0` (Texte 4771–4782): 0 Trainer, 1 Mannschaft, 2 Privates,
  3 Ablenkung, 4 Presse, 5 Verein, 6 Presse, 7 Verhandlung, 8–10 Beliebtheit Fans / Medien / Öffentlichkeit,
  11 Stimmung. Die Meldung zu 1312 zeigt die Änderung der Ablenkung also unter „Mannschaft“. Damit ist auch belegt,
  dass Spielersatz 0x274 die Ablenkung ist.

### 6.10 Karriereende findet nicht statt (1342)
Text 1342: Der Spieler „beschließt, seine Karriere als Fußballprofi zu beenden und sich ab sofort ganz seiner
Computerfirma zu widmen“. Der Fall (`0x005E26BC`–`0x005E26E6`) setzt nur den Firmen-Stand von 5 auf 6 (Bits 4–6 von
Spielstand 0x261, `0x00703276`) und gibt die Meldung aus. Der Stand wird über die Zugriffsroutine `0x0070324F` nur
in dieser einen Routine gelesen (acht Stellen), über `0x00703225` nur in der toten Routine `0x005E1C68`. Der Spieler
bleibt im Kader; mit Stand 6 passt kein Fall mehr, die Firmenereignisse dieses Spielers enden.

### 6.11 Der enttarnte Spitzel bleibt Spitzel (983)
Text 983: „… %1 teilt Ihnen danach mit, daß er Ihnen ab jetzt nichts mehr sagen wird.“ Der Fall (`0x005E4F10`–
`0x005E4F7C`) zieht bei allen Kaderspielern den Trainer-Teilwert um 10 ab, setzt beim Spitzel Bit 0x20000 im Flagwort
Spielersatz 0x194 (`0x0070031F`) und den Mannschafts-Teilwert auf 0 (`0x00700BCF`). Das Spitzel-Bit 0x8000 wird nicht
gelöscht (kein Aufruf von `0x0070020F`; dessen einzige Aufrufer sind `0x0048FC80`, `0x0048FD30`, `0x0048FDD0` und
`0x007074FB`). Die Hülle `0x005E4FD6` wählt den Spitzel allein nach Bit 0x8000 (`0x007001ED` bei `0x005E5031`), und
die Routine `0x005E4EC2` prüft Bit 0x20000 nicht. Der enttarnte Spieler wird deshalb weiter als Spitzel gezogen: Er
kann weiter Verdächtige melden (Text 982), und die Enttarnung mit −10 für den ganzen Kader kann sich wiederholen.

### 6.12 Weitere Stellen aus P02
- **Gruppenbildung, Text 1412 (`0x005E3885`):** Die Routine läuft nur weiter, wenn Byte Verein +0x9E unter 100 liegt
  (`0x005E3899`). Der Zweig `0x005E3C19`–`0x005E3C28` (Bit der Gruppe = 1) verlangt aber Verein +0x9E über 100
  (`0x005E3C14`). Weder die Routine selbst noch eines der 190 von ihr aus erreichbaren Unterprogramme schreibt ein
  Byte bei +0x9E (alle 30 Schreibstellen des Programms liegen in anderen Routinen; zehn Aufrufe über Register sind
  dabei nicht verfolgt). Der Zweig ist nie erreichbar, die Gruppe der „Starspieler“ bekommt immer Bit 0. Die Meldung
  selbst erscheint.
- **Fest eingetragene Spielernamen, Texte 1348–1351 und 1353–1355 (`0x005E2152`):** Sieben Fälle (Werbespots und
  Ähnliches, Ablenkung −2) verlangen, dass der Nachname oder der volle Name des Spielers gleich einer festen
  Zeichenkette im Programm ist (`strcmp` bei `0x005E286F`, `0x005E28CB`, `0x005E2927`, `0x005E2983`, `0x005E2A33`,
  `0x005E2A8F`, `0x005E2AEE`; Zeichenketten bei `0x0088D980`, `0x0088D988`, `0x0088D994`, `0x0088D99C`, `0x0088D9A4`,
  `0x0088D9B4`, `0x0088D9C0`). Gegenprobe in den Stammdaten `original/Data.a3` (771 Textdateien, ein Name je
  Zeile): Fünf der sieben Namen kommen dort gar nicht vor (Texte 1349, 1350, 1353, 1354, 1355). Die beiden anderen
  Zeichenketten haben je einen Treffer, der nicht passt: bei 1348 (`LandHoll.sav`) ist sie nur der Anfang eines
  längeren Wortes, bei 1351 (`Jugend6.sav`, Liste aus Paaren Vorname / Nachname) steht sie auf einer Vornamen-Zeile,
  verglichen wird aber der Nachname. Keines der sieben Ereignisse kann mit den Originaldaten eintreten. Die Methode
  ist am Nachbarfall 1347 (`0x005E2813`, Zeichenkette `0x0088D970`) gegengeprüft: dessen Nachname steht als eigene
  Zeile in `LandDeut.sav`. Erreichbar wären die Ereignisse, wenn ein Spieler im Editor so benannt wird.

### 6.13 Aus Lesepaket P04
Alle sieben markierten Einträge des Katalogs P04, am 16./17.11.2026 von Hand am Code nachgeprüft.

- **Ersparnis als Ausgabe, Kosten als Einnahme (690, 697):** Die einfachen Geld-Ereignisse (`0x005E9A4F`, Tabelle
  `0x0088DC58` mit 108 Paaren Text / Wert) buchen nach dem Vorzeichen des Tabellenwerts: negativ → Verein +0x2C0
  (`0x005E9AEE`), sonst → Verein +0x2C4 (`0x005E9B05`); die Meldung zeigt den Betrag ohne Vorzeichen. Bei den
  Nachbarn passt das (689, 691 „kostet“ negativ, 698 „nehmen ein“ positiv). Text 690 („Sie sparen %s ein“) hat aber
  den Wert −120 und wird wie Kosten gebucht (12 000), Text 697 („Kostenpunkt: %s“) hat +80 und wird wie eine
  Einnahme gebucht (8 000). Dass +0x2C0 Ausgaben und +0x2C4 Einnahmen sammelt, folgt aus diesen Nachbarn.
- **Verhandlung bringt nicht mehr (224/225):** Frage 224 bietet %4 und stellt bei erfolgreicher Verhandlung %5 in
  Aussicht. Der doppelte Betrag wird nur für den Fragetext nach `0x00A32200` geschrieben (`0x005E89B1`). Bei Erfolg
  (Text 225) wird derselbe einfache Betrag gutgeschrieben (`0x005E89FA`–`0x005E8A09`) wie ohne Verhandlung
  (`0x005E8A27`); einziger Unterschied ist `0x0041849A(0, 0, 0, +3)`, bei Misserfolg −3 und kein Geld.
- **Text 281 kann nie erscheinen:** In `0x005E9ED1` (Auslosung `0x0088E04C`: Nummern 1, 2, 3, 4 mit Gewichten
  1, 3, 1, 1) zeigt Fall 2 der Sprungtabelle `0x005EA50C` auf `0x005EA012` (nur Rückgabe 1). Der Block
  `0x005EA01B`–`0x005EA0D7` mit dem Text „… hat die hiesige Staatsbürgerschaft erhalten“ wird von außen nicht
  erreicht (Sprünge dorthin nur aus dem Block selbst, kein Tabelleneintrag, kein Adresswert in der Datei). In der
  Hälfte der Aufrufe dieser Routine geschieht also nichts.
- **Randale: Entwarnung trotz Abzug (283/284):** Im ungünstigen Zweig (`0x005EA167`–`0x005EA204`) werden 100 000 auf
  Verein +0x2C0 gebucht, als zweiter Text wird aber wieder 283 („schnell unter Kontrolle gebracht“) geholt
  (`0x005EA1B1`) statt 284 („… auf mehr als %s verklagt … auf %s einigen“). Text 283 hat keine Platzhalter, die zwei
  übergebenen Beträge verfallen. Text 284 hat im Programm keine Stelle. Für eine Korrektur wichtig: Beide Beträge
  kommen aus `0x004DAF8F`, das immer in denselben Puffer `0x008EC88C` schreibt und dessen Adresse zurückgibt
  (`0x004DB0E7`); auch mit Text 284 stünde an beiden Stellen der zuletzt gebildete Betrag (500 000).
- **Text 285 nennt 20 Punkte, abgezogen werden je 5:** „… %s Strafe und 20 Punkte Beliebtheit in der Öffentlichkeit
  und bei den Medien“. Bei „Ja“ ruft `0x005EA42E` `0x0041849A(−5, −5, −5, −10, Manager)`. Zuordnung aus dem
  Beliebtheits-Dialog (`0x0047E6E0`–`0x0047E741`): Manager +0x3A Öffentlichkeit, +0x3B Fans, +0x3C Medien
  (`0x006A5A7D`). Abgezogen werden also Öffentlichkeit 5, Fans 5, Medien 5 und 10 beim vierten Wert (Manager +0x9C,
  im Dialog nicht angezeigt, Bedeutung offen). Die Strafe von 200 000 stimmt.
- **Aufhebung der Ausländerbeschränkung ohne Wirkung (769):** Das Ereignis (`0x005EA7B3`–`0x005EA7F8`, ab dem Jahr
  2006, einmalig) setzt nur Bit 0x10 im Byte `0x00B5DFA8`. Von allen 31 direkten Zugriffen auf dieses Byte liest nur
  `0x005EA7CF` das Bit 0x10 – die Wiederholungssperre desselben Ereignisses; alle anderen betreffen die Bits 1, 2
  und 4. Geprüft sind die direkten Zugriffe auf die Adresse.

### 6.14 Aus Lesepaket P06: Wehrdienst, Schule, Privatleben der Spieler
Alle markierten Einträge des Katalogs P06, am 17.11.2026 von Hand am Code nachgeprüft. Beziehungsdaten im
Spielersatz (Spielstand): 0x25E Bits 0–1 Status (0 keine Beziehung, 1 Freundin, 3 verheiratet), Bits 2–4 Krisenstufe;
0x263 Namensindex der Partnerin, 0x264 der Geliebten, 0x265 der früheren Partnerin; 0x266 / 0x267 Namensgruppe der
Partnerin / der früheren Partnerin; 0x150 Termin der Hochzeit; 0x1D6 Zahl der Kinder; Flagwort 0x194.

**Ereignisse, die nie oder nur unter falscher Bedingung eintreten**
- **Affäre fliegt auf (1126, 1127, 1128, 1236) – nie:** Die Vorroutine `0x005FB916` (täglicher Verteiler,
  Los-Nummer 6, Gewicht 100) nimmt nur verheiratete Spieler mit gesetztem Bit 2 im Flagwort 0x194 (`0x00702A5B` bei
  `0x005FB98E`). Dieses Bit wird nie gesetzt: Von den 46 Schreibstellen des Flagworts (`0x00C02704 + Nr × 0x354`)
  setzt keine den Wert 4; es wird nur gelöscht. Die Routine `0x005FB751` läuft deshalb nie. (`0x007029A7`, das die
  Geliebte einträgt, setzt nur den Namensindex 0x264 und kein Bit.) In der toten Routine wären außerdem bei 1127 die
  Platzhalter vertauscht und bei 1126 der Name der Geliebten falsch.
- **Alle Ehefrau-Ereignisse verlangen eine Geliebte:** Die Vorroutine `0x005FB634` (Los-Nummer 5, Gewicht 100) nimmt
  nur Spieler mit Status 3 **und** Byte 0x264 ≠ 0 (`0x005FB6B2`, `0x005FB6C5`). Byte 0x264 wird nur in `0x007029A7`
  gesetzt (`0x007029CC`), aufgerufen an drei Stellen (`0x005FD2C9`, `0x005FD304`, `0x005FD347`; Texte 1251–1253,
  Los-Nummer 12, Gewicht 11). Schwiegermutter, Banküberfall, Weihnachtsgeschenk und die übrigen Meldungen von
  `0x005FB264` setzen also voraus, dass der Spieler vorher eine Geliebte bekommen hat.
- **Leere Los-Zweige:** `0x005F9ED7` (Tabelle `0x0088E6F0`, Nummern 1 und 2): Nummer 2 ist nur „Rückgabe 1“
  (`0x005F9FC3`). `0x005FA394` (Tabelle `0x0088E700`, Nummern 1–3): Fall 3 ist leer (`0x005FA54E`); Fall 4 (zweite
  Stelle von Text 1094, `0x005FA5AD`) hat keine Los-Nummer. `0x005FB264` (Tabelle `0x0088E74C`, Nummern 1–9 je
  Gewicht 3, 10 und 11 je 1): die Fälle 4–7 sind leer (`0x005FB42A`–`0x005FB445`), also 12 von 29 Losen. Die
  dazugehörigen Texte 1084–1086, 1095, 1096 und 1118–1121 haben keine Stelle mit fester Nummer.

**Text und Wirkung passen nicht zusammen**
- **„Hochzeit platzt“ trifft den falschen Spieler (1093, 1094):** Die Vorroutine `0x005FA5F8` sammelt die Kandidaten
  (Spieler mit Hochzeitstermin) in ein Feld, liest das Feld aber nie. Übergeben wird der Zeiger `[Verein + 0xB50 +
  i × 4]` mit i = Schleifenzähler nach dem Schleifenende, also gleich der Kadergröße (`0x005FA688`–`0x005FA69B`) –
  der Platz hinter dem letzten Kaderspieler. Die Schwester-Vorroutinen ziehen Zufall 0 bis Anzahl−1 aus ihrem Feld.
  Der Inhalt dieses Platzes ist aus dem Code nicht bestimmbar (die Zeigerliste wird beim Aufbau in `0x00635F76`
  nicht geleert); möglich ist ein alter Spielerzeiger oder ein ungültiger Zeiger, also auch ein Absturz.
  Nachgelesen 17.11.2026: Auch `0x00636120` ff. und `0x006362A0` schreiben nur die Plätze 0 bis Kadergröße−1. Hat
  der alte Zeiger einen Spieler mit Status „Freundin“, bekommt dieser die Meldung ohne Hochzeitstermin.
- **1093, Hochzeit „abgesagt“:** Der Fall streicht den Termin mit `0x004377B7(Nummer, Zeiger auf [ebp-8])`
  (`0x005FA46F`). `[ebp-8]` wird in der ganzen Routine nie beschrieben, das Datum im Suchschlüssel ist also
  zufällig; der Termin bleibt in der Liste, und Byte 0x150 wird nicht gelöscht. Am Termin ruft `0x005FD386`
  (aus `0x005F0465`) `0x00702B15`: Status 3, Krisenstufe 0 – die Hochzeit findet trotz Absage statt. Die Freundin
  bleibt Partnerin (nur Krisenstufe 3, Geliebte gelöscht), obwohl der Text die Trennung von beiden Frauen meldet.
- **1094, Namen vertauscht:** Text „%1, die Freundin von %2, entdeckt … seiner anderen Freundin %3“. `0x006012DF`
  setzt immer %1 = Spielername; als %2 wird der Name der Freundin übergeben (`0x0070185C` bei `0x005FA528`).
  %3 (`0x007017DB` bei `0x005FA51F`) wird erst gelesen, nachdem `0x0070282A` die Geliebte zur Partnerin gemacht und
  Byte 0x264 auf 0 gesetzt hat – gelesen wird der Name mit Index 0 statt der Name der Geliebten.
- **1083, „Es kommt zur Trennung“:** Der Fall (`0x005F9F6A`–`0x005F9FB5`) senkt nur Spielersatz 0x273 um 10–19. Der
  Aufruf `0x00702467` (Beziehung beenden), den die gleich gebaute Stelle zu Text 1079 hat (`0x005F9816`), fehlt.
- **1104, „%1 hat %2 die Freundin ausgespannt“:** Im Code übernimmt der zweite Spieler q die Partnerin des
  gewählten Spielers p (`q.0x00702668(p)` bei `0x005FABEC`), p verliert sie (`0x005FABF4`). Die Meldung nennt aber p
  als %1 und q als %2 (`0x005FAC25`–`0x005FAC3D`) – also umgekehrt.
- **1109 und 1110, Ex-Freundin:** Text 1109 („spricht seine Freundin mit dem Namen der Ex-Freundin an … sagt künftig
  Schatzi“) ruft `0x00702762` (`0x005FAE79`, einziger Aufrufer): die jetzige Freundin wird frühere Partnerin, die
  Ex-Freundin wird wieder eingetragen – der Status bleibt dabei 0 (keine Beziehung). Die Namen werden erst danach
  gelesen und sind deshalb vertauscht. Der bei `0x005FAE6D` geprüfte Merker (Bit 25 im Flagwort, `0x007028D7`) wird
  nie gesetzt; sein Setzer `0x007028F9` hat keinen Aufrufer. Text 1110 („hat seine Sachen gepackt und ist auf dem
  Weg zu ihr“) ändert dagegen nichts (`0x005FAED2`–`0x005FAF11`).
- **1115, Frau zieht mit Kind aus:** Der Text enthält zweimal „%s“ (Abschnitt 6.6: beide Namen fehlen). Geändert
  wird nur Spielersatz 0x273 (−40 bis −50); die Trennung und der angekündigte Verlust eines Stärkepunkts finden
  nicht statt. Als zweiter Name wird die frühere Partnerin übergeben (`0x005FB354`) statt der Ehefrau. Bedingung
  ist unter anderem Byte Spieler +2 genau gleich 1 (`0x005FB2FA`; +2 ist nach den Unterlagen vermutlich die Stärke, V).
- **1116 und 1117, Schwiegermutter:** „%s“ statt „%1“ (Spielername fehlt). Geändert wird die Ablenkung (0x274,
  `0x00701210` bei `0x005FB3A3` / `0x005FB3FB`), als Art wird 2 = „Privates“ übergeben (`0x005FB3AE`, `0x005FB406`).
- **1565, Abitur bestanden:** Der Fall (`0x005F9D31`–`0x005F9D44`) gibt nur die Meldung aus. Die Vorroutine schließt
  Spieler mit Schüler-Merker 3 aus (`0x005F9DD0`), der Wert 3 wird aber nirgends gesetzt (`0x0070654A` nur mit 1 und
  2, `0x005F9CB7`, `0x005F9CF9`). Derselbe Spieler kann das Abitur im Juni mehrfach bestehen und bekommt danach
  weiter die Schul-Meldungen 1561–1564.
- **1076, Bänderriss beim Wehrdienst:** Text „fällt vier Wochen aus“. `0x00766B92(Spieler, Art 10, −1)` nimmt die
  Dauer aus der Tabelle `0x008AC340` (Art 10: 35). Die Einheit ist Tage (Vergleich: 7 bei Text 1101 „nächste Woche“,
  42 bei 1219 und 1223 „sechs Wochen“) – also fünf Wochen.
- **1982, kein Weihnachtsgeschenk:** Nach der Meldung läuft der Code in `0x005FB601` (`xor ax,ax`) und gibt 0
  zurück; alle anderen Fälle geben 1 zurück. Der Tagesverteiler lost danach am selben Tag weiter aus.

**Dabei mit bestätigt (bisher nur gemeldet)**
- **Bit 4 von Spielstand 0x260 doppelt belegt:** Es ist der Merker „Anführer einer Gruppe“ (setzen `0x007006E8` an
  vier Stellen der Gruppenbildung, löschen `0x00700690` und `0x0070071C`) und zugleich das obere Bit des
  Schüler-Merkers in den Bits 3–4 (lesen `0x007064C9`, `0x007064F6`, setzen `0x0070654A`). Ein Schüler, der Anführer
  wird, erhält den Schüler-Wert 2 oder 3; ein Schul-Ereignis mit `0x0070654A(1)` löscht den Anführer-Merker.
- **`0x0070185C` (Name der früheren Partnerin):** liest den Namensindex aus 0x265, die Namensgruppe aber aus 0x266
  (Gruppe der jetzigen Partnerin) statt aus 0x267, wohin `0x00702467` die Gruppe der früheren Partnerin kopiert.
  Falsch wird der Name nur, wenn die Gruppen verschieden sind.

### 6.15 Aus Lesepaket P07, Teil 1: Hobby-Ereignisse (`0x005FD59D`)
Alle markierten Einträge dieser Routine aus dem Katalog P07, am 17.11.2026 von Hand am Code nachgeprüft. Die Routine
(täglicher Verteiler, Los-Nummer 19, Gewicht 110; Hülle `0x005FED08` wählt einen zufälligen Kaderspieler) verteilt
bei `0x005FD5FA` nach der gespeicherten Hobby-Nummer des Spielers (Spielstand 0x26D).

**Verletzungen: Dauer oder Art passt nicht zum Text.** `0x00766B92(Spieler, Art, −1)` nimmt die Dauer in Tagen aus
der Tabelle `0x008AC340` (Abschnitt 6.14); `0x00766AF9(Spieler, n)` setzt nur Byte Spieler +0x2F („angeschlagen“,
Anzeige `0x00731E54` mit Text 1320), keinen Ausfall.

| Text | Meldung | Stelle | Code |
|---|---|---|---|
| 1193 | Spaten in den Fuß, „fällt drei Wochen aus“ | `0x005FDFE7` | Art 37: 112 Tage (16 Wochen) |
| 1215 | Hand verstaucht, „die nächsten drei Wochen“ | `0x005FE626` | Art 90: 7 Tage |
| 1194 | Hornissen, „fällt zwei Wochen aus“ | `0x005FE026` | nur „angeschlagen“ 14 Tage, kein Ausfall |
| 1224 | Qualle, „die nächste Woche … angeschlagen“ | `0x005FE901` | Art 91: 14 Tage Ausfall |
| 1225 | Stickstoffvergiftung, „nächste Woche nicht trainieren“ | `0x005FE92E` | Art 92: Dauer 0 – kein Ausfall; ein laufender Ausfall wird auf 0 gesetzt |
| 1227 | Sportwagen, „fällt damit zwei Wochen aus“ | `0x005FE9F0` | Art 93: Dauer 0 – kein Ausfall |

Die Tabellenzeilen der Arten 92 und 93 bestehen aus Nullen (die Tabelle hat nur bis Art 91 Werte).

**Angekündigte Wirkung fehlt oder trifft die Falschen**
- **1180** („… ist heute sehr müde und verliert einen Frischepunkt“): Der Zweig `0x005FDDAD`–`0x005FDDC0` gibt nur
  die Meldung aus.
- **1210** (Bienen, „Seine Frau %2 … verbietet ihm sein Hobby … kann in den nächsten Tagen nur eingeschränkt
  trainieren“): Der Fall (`0x005FE45E`–`0x005FE47B`) setzt die Hobby-Nummer auf 0 und gibt die Meldung aus. Die
  Einschränkung fehlt, als zweiter Name wird 0 übergeben (%2 leer), der Beziehungsstand wird nicht geprüft, und es
  gibt weder Bedingung noch Zufall – das erste Los beendet das Hobby.
- **1172** (Autobiographie, „%2 und %3 mögen ihn jedenfalls jetzt nicht mehr“): Eingetragen wird der Streit zwischen
  den beiden Mitspielern A und B (`A.0x00703DF4(B)` bei `0x005FDB45`–`0x005FDB4C`), nicht zwischen ihnen und dem Autor.
- **1176, 1177** („%2, die Frau Ihres Spielers %1 …“): als zweiter Name wird 0 übergeben (`0x005FDCAD`, `0x005FDCCA`);
  die Meldung beginnt mit „, die Frau Ihres Spielers …“.
- **1207** („Seit Single %1 einen Kochkurs besucht hat …“): Der Zweig (`0x005FE3C9`–`0x005FE3E1`) prüft den
  Beziehungsstand nicht.
- **1168** (Tagebuch, „Die Stimmung in der Mannschaft sinkt um zwei Punkte“): Die Wirkung stimmt
  (`0x00698EF6(−20)` auf Verein +0x9E, `0x005FDA11`). Als Art wird 10 übergeben (`0x005FDA33`), das ist nach der
  Tabelle aus Abschnitt 6.9 „Beliebtheit Öffentlichkeit“; „Stimmung“ wäre Art 11.
- **1217** (Führerschein „für einen Monat“ entzogen): Gesetzt wird der Zähler Spielstand 0x26E = 2 (`0x005FE6AA`).
  Die Schwesterstellen setzen für „einen Monat“ 1 (Texte 1232 bei `0x005FEB9F`, 1150 bei `0x005FC760`) und für
  „sechs Monate“ 6 (1151 bei `0x005FC79F`). Die Schlagzeile 1218 übergibt Presse −2, direkt angewendet werden −5
  (`0x005FE6D9`); bei 1232/1234 sind beide Werte −3.

**Nie erreichbar**
- **1173** (Handbuch für Fußballprofis): Zufall 0–2 bei `0x005FDA79`, die Werte 0, 1 und 2 sind vergeben; der Sprung
  `0x005FDAA4` zum Zweig mit Text 1173 wird nie genommen.
- **1226** (Tauchgänge mit der Freundin): bei Hobby 35 Zufall 0–1 (`0x005FE8D5`); der dritte Zweig `0x005FE953` ist
  nie erreichbar und enthält keine Meldung. Der Text hat keine Stelle.

**Der Führerschein kommt nie zurück (beim Nachlesen gefunden):** Der Zähler Spielstand 0x26E wird nur in `0x00702D31`
geschrieben, und alle zwölf Aufrufer übergeben 1, 2, 6 oder −1 (nur lesen). Er wird nirgends heruntergezählt oder
gelöscht (kein weiterer direkter Zugriff, auch nicht über einen Zeiger +0x28E). Alle Führerschein- und Raser-
Ereignisse verlangen den Wert 0 (`0x005FC73F`, `0x005FE68B`, `0x005FE9B4`, `0x005FEB2E` …) – ein Spieler erlebt sie
höchstens einmal. Nicht ausgeschlossen ist ein pauschales Löschen größerer Satzteile an anderer Stelle.

### 6.16 Aus Lesepaket P07, Teil 2: Ereignisse zwischen zwei Spielern, privater Trainer
Alle 13 markierten Einträge der Routinen `0x005FEDB0` und `0x005FFF0F`, am 17.11.2026 von Hand am Code nachgeprüft.

**Ereignisse zwischen zwei Spielern (`0x005FEDB0`; täglicher Verteiler Los-Nummer 25, Gewicht 100, Hülle `0x005FFEB7`).**
Auslosung aus der Tabelle `0x0088E8C8` mit 25 Einträgen: Nummern 1–15 und 20–24 je Gewicht 30, 25 Gewicht 20, 26 und
27 je 30, 28 und 29 je 6 (Summe 722). Die Verteiler-Variable wird nur aus der Los-Nummer gesetzt (`0x005FEDEE`,
`0x005FEDFD`); Verteiler `0x005FEE1E` mit Fällen bis 92.
- **Acht Texte können nie erscheinen:** Die Fälle 16 (Text 1377), 52 (1395), 60 (1396), 70 (1402), 71 (1403),
  72 (1404), 73 (1405) und 90 (1399) haben keine Los-Nummer. Ebenso ohne Los-Nummer, aber auch ohne Text: die Fälle
  50, 51, 80, 81, 82, 91, 92. Text 1399 ist doppelt unerreichbar: Die Vorprüfungen `0x005EE2F5` und `0x005EE2FC`
  sind leere Routinen (`xor eax,eax / ret`).
- **Sechs Lose ohne Inhalt:** Die Fälle 9, 13, 15, 26, 27 und 29 bestehen nur aus „Rückgabe 1“ (`0x005FF3BC`,
  `0x005FF4BE`, `0x005FF51A`, `0x005FF913`, `0x005FF91C`, `0x005FF9AA`) – zusammen Gewicht 156 von 722. Die Texte
  1370, 1374, 1376, 1386, 1387 und 1389 haben keine Stelle mit fester Nummer.
- **1363** („Da auch ihre Frauen %3 und %4 sehr viel zusammen machen …“): Als dritter Name wird der Puffer
  `[ebp+FFFFFEE8h]` übergeben (`0x005FF03E`), der nur in Fall 1 beschrieben wird (`0x005FEF0B`); in Fall 2 enthält
  er zufälligen Stapelinhalt, der ohne Längenprüfung weiterkopiert wird. Der vierte Name ist 0 (`0x005FF03C`).
  `0x0070173F` (Name der Partnerin) wird nicht aufgerufen.
- **1365** („%1 … erzählt ihm, was ihm zur Zeit bei diesem Verein alles stinkt. %2 muß ihm … recht geben“): Der Fall
  (`0x005FF120`–`0x005FF1D1`) sortiert zwei Freunde so, dass A den höheren Zufriedenheitswert hat (`0x006FF14D`,
  Mittel aus drei Teilwerten), und verlangt A über 100 und B unter 85. Als %1 wird A genannt, als %2 B – der
  Zufriedene klagt. Die Wirkung `B.0x00705539(A)` hebt in zwei Durchgängen den jeweils kleinsten Teilwert von B
  (Spielstand 0x26F–0x271) um die Hälfte seines Abstands zu 100 und senkt denselben Teilwert von A um denselben
  Betrag, ohne Begrenzung nach unten.
- **1388 statt 1389:** Der Fall 28 (`0x005FF925`–`0x005FF999`) wählt zwei Spieler derselben Position und trägt Streit
  ein (`0x00703DF4`). Dazu passt Text 1389 („… die die gleiche Position spielen, verstehen sich privat nicht
  besonders gut“), der keine Stelle hat. Ausgegeben wird 1388 („… haben sich beide in %3, die Schwester Ihres
  Spielers %4, verliebt. Diese entscheidet sich … für %5“) über `0x00600F2F`, das nur zwei Namen übergibt. Was für
  %3 bis %5 im Text erscheint, ist nicht zu Ende gelesen (Abschnitt 7: laut Lauf B ein „?“).

**Privater Trainer (`0x005FFF0F`; Los-Nummer 55, Gewicht 20).**
- **1358, 1359** („erhält einen Konditionsbonus von 5%“ / „verliert … seinen Konditionsbonus“): Das Ereignis setzt
  bzw. löscht nur Bit 13 (0x2000) im Flagwort Spielstand 0x194 (`0x00700105` bei `0x0060003F`, `0x00600076`). Gelesen
  wird das Bit nur über `0x007000E3`, mit drei Aufrufern: die beiden Abfragen des Ereignisses (`0x00600016`,
  `0x0060004D`) und die Anzeige im Spielerdialog (`0x0055F96E`). Die Konditionsroutine `0x00457E00` (Spieler +0x16
  geteilt durch 100) zieht für Raucher (Bit 0x800, `0x006FFFD9`) 5 ab und kennt keinen Zuschlag. Der Bonus wird
  nie gerechnet.

### 6.17 Absicht oder Fehler? (Einordnung, V)
Aus dem Code lässt sich nicht beweisen, was die Entwickler wollten. Die Befunde zeigen aber zwei deutlich
verschiedene Muster:

**Sieht nach bewusst stillgelegt oder nie fertiggestellt aus (V):**
- Routinen ohne jeden Aufrufer (Abschnitt 2, 18 Routinen mit 94 Texten) und leere Routinen, die nur 0 liefern
  (`0x005EE2F5`, `0x005EE2FC`);
- Blöcke, die mit einer festen Bedingung abgeschaltet sind (`mov eax,1 / test / je`, `xor eax,eax / test / je`:
  `0x0060C687`, `0x005F2E43`, `0x005F2F07`) – so übersetzt der Compiler ein „if (0)“ im Quelltext;
- Fälle, die nur aus „Rückgabe 1“ bestehen, und Fälle ohne Los-Nummer (6.14, 6.16, Text 281 in 6.13, 1289 in 3.3):
  Platzhalter für Ereignisse, die geplant, aber nicht eingebaut oder wieder herausgenommen wurden. Dafür sprechen
  die runden Nummernblöcke (50, 60, 70, 80, 90) und dass in den toten Fällen selbst noch Fehler stecken;
- Texte ohne jede Stelle und die Fragen-Datensätze ohne Benutzer (6.4).
Diese Punkte sind keine Rechenfehler. Sie zu „reparieren“ hieße, Inhalte freizuschalten, die das ausgelieferte Spiel
nie hatte, und wäre eine Entscheidung des Nutzers, kein Fehlerpatch.

**Sieht nach Versehen aus (V stark):**
- falsche oder vertauschte Platzhalter und Namen, „%s“ statt „%1“, falsche Textnummer (283/284, 1388/1389);
- Wirkung, die der Text ankündigt, fehlt oder trifft den Falschen; Dauer und Beträge, die dem Text widersprechen;
- technische Fehler: nie beschriebene Variablen (1093, 1363), falscher Zeiger (`0x005FA5F8`), falsche Liste
  (`0x00703930`), doppelt belegtes Bit, Zähler mit Überlauf (`0x0069FE73`), Zähler, der nie zurückgesetzt wird (0x26E),
  falsche Argumentzahl bei Zeitungsmeldungen, Vorzeichenfehler in Tabellen (690, 697);
- Bedingungen, die nie wahr werden können, obwohl der Fall eine Los-Nummer hat und vollständig ausgearbeitet ist
  (Affären-Routine wegen eines nie gesetzten Bits, 1178/1179, 888/889, 1173, 1481).

Unklar bleibt die Mitte, zum Beispiel ob die Ehefrau-Ereignisse wirklich eine Geliebte voraussetzen sollten.

## 7. Gemeldet, nicht nachgeprüft
Alles in diesem Abschnitt stammt aus den Hilfsläufen oder aus maschinellen Listen und ist **nicht** von Hand am Code
bestätigt. Es sind Hinweise, keine Ergebnisse. Frühere maschinelle Hinweise dieser Art waren teils Fehlalarme.

**Verteiler der allgemeinen Spieler-Ereignisse `0x005E08F1`** (maschinell, `meld9.py` → `faelle.txt`):
- Fälle 44, 55, 56 leer (nur Eigenschaftsprüfung, keine Wirkung, kein Text); Fall 46 ruft nur `0x00406B4F` und
  verwirft das Ergebnis; die Nummern 57, 58, 59 haben keinen Fall.
- Dazu passende Texte ohne jede Stelle: 1283, 1285–1287, 1290, 1292, 1293, 1297–1303.
- Weitere Auffälligkeiten anderer Verteiler nur in der Ausgabe von `meld9.py` (leer / keine Nummer / Nummer ohne Fall).

**Hilfsroutinen der Spieler (Lauf A):**
- `0x007033A5`: bei voller Dreierliste landet die neue Nummer auf Index 3 (Wort Spielstand 0x1E4).
- (Die beiden Punkte „Bit 4 von Spielstand 0x260 doppelt belegt“ und „`0x0070185C` mit falscher Namensgruppe“
  sind inzwischen bestätigt, siehe Abschnitt 6.14.)
- `0x006FF5D5`: der Ersatzzweig liefert von Januar bis Juni negative Werte.

**Ereignis-Helfer (Lauf B):**
- `0x005E409C` (Spielernummer als Index statt Vergleich); `0x005EB669` (verlangt mehr als einen Kandidaten);
  `0x005EC9D8` (Vergleich ohne Wirkung); `0x005ECCCC` / `0x005ECDC8` / `0x005ECF3B` (ohne Kandidaten ein
  uninitialisierter Stapelplatz als Spielernummer); `0x00614A99` (Maske 0x7F000000 gegen 0x3F); `0x005F1EAF`
  (Argument ohne Wirkung).
- Mechanik: `0x005F2813` liefert die Antwort 0/1/2, ohne Frage 0 bzw. 1; `0x005EEE7F` ersetzt %n durch den n-ten
  Zeiger und schreibt „?“, wenn er fehlt.

**Verein und Liga (Lauf C):**
- `0x006A7CFE` (Stärke eines Spielers ändert sich, Texte 902–905): Prüfung „Textnummer < 0“ nie wahr (mit 0xFFFF
  maskiert); trifft keine der vier Bedingungen zu, wird die Stärke trotzdem gesetzt und Text 0 (leer) gemeldet –
  möglicher Ursprung einer Meldung ohne Text.
- `0x00698D01(Änderung)`: Byte Verein +0x10F, begrenzt 10–50; die Kopplung an +0x110 ± 10 wird am alten Wert
  gerechnet und sofort überschrieben.
- `0x006DC2A6`: Suchschleife läuft bis zur Kadergröße, die Liste hat 35 Plätze.
- `0x006A03FB` (V: Transferbedarf eines Computervereins): Zweig `0x006A0D83` unerreichbar.
- `0x00636459` / `0x006363D7`: bei Nummer 0 ein uninitialisierter Rückgabezeiger.
- `0x00638335` / `0x0063865C` (V: Stadiondaten): im Zweig Verein = 200 gesetzte Werte werden sofort überschrieben;
  Leser und Schreiber behandeln „Teil < 0“ verschieden.
- `0x0069CB5C`: der Sonst-Zweig löscht von einem dword nur ein Byte.
- Verein (Laufzeit) Wort +0: Bits 0–12 Index des statischen Satzes, Bits 13–15 Art.

**Übrige Helfer (Lauf D):**
- `0x0041849A(d1, d2, d3, d4, Manager)`: Bytes Manager +0x3A bis +0x3C und Wort +0x9C, je 0–100. In `0x004184D4` wird
  die Summe als Byte gespeichert und vorzeichenbehaftet zurückgelesen, bevor begrenzt wird: eine Summe über 127 würde
  0 statt 100. Dasselbe in `0x00418065` und `0x00418394`. Ungeklärt: der größte übergebene Zuwachs.
- `0x00789C32`: ein Zeitungstext ohne Bindestrich ergäbe einen Nullzeiger als Vorlage (`0x00789E6B`). Ob alle
  Zeitungstexte einen Bindestrich haben, ist in den Notizen nicht festgehalten. Die Tabelle `0x008AD230` hat nur sechs
  Namenspuffer.
- `0x007793EE` (V: Börsenkurven): Platz 49 wird sofort überschrieben.
- `0x00418394` liest anders als `0x00418065` weder Verein +0x8A noch +0x80.
- `0x004DAF8F` (Geldbetrag als Text) benutzt einen einzigen festen Puffer `0x008EC88C`; zwei Aufrufe in einem
  `sprintf` würden sich überschreiben (betrifft Texte mit zwei Geldbeträgen).
- `0x00775FA0` liefert 0 in der Zielzone und auf dem Rang direkt davor (nicht symmetrisch).

**Tabellenstellen (Lauf „Tabellen“, `tabellen_aufgeloest.md`, 336 Zeilen; meldet 40 Texte als „nie“ und 1 offen):**
- 1024–1027: Termin-Art 105 wird nie angelegt.
- 1499, 1502, 1503: kein Schreiber.
- 93–96 an `0x0060CCC8`; Maskenfehler in `0x0060C1C0`, Fälle 106/107 (Tabellen `0x0088FFA4` / `0x0088FFB0` mit fünf
  Einträgen, gelesen mit Index 0–9; die Zehnertabellen `0x0088FFBC` / `0x0088FFD0` unbenutzt).
- Datensatz 12 (415, 416, 418); Text 115 bei Index 0; Text 908 offen.
- 832–847: an `0x0060C754` / `0x0060C7E4` erreichbar.
- Hüllroutine `0x005C2A29` (Vertragsverhandlung; 1479, 1480, 1482, 1491–1498, 1500, 1501).
- Die 38 Stellen mit Nummer aus Tabelle oder Variable (Tabellen `0x0088DC58`, `0x0088E070`, `0x0088EF80`,
  `0x0088EF90` ff., `0x0088FFFC`, `0x00890024`, `0x00890040`, `0x008A5458`, `0x008A5484`, `0x0088761C`, lokales Feld in
  `0x00602594`) sind nur durch diesen Lauf aufgelöst.

**Sonstiges:**
- `0x007899D9` und `0x00789EE0` (Routinen mit Textparameter): kein Verweis gefunden.
- Katalog P07, nicht nachgeprüft: die Einzelheiten der nie erreichbaren Fälle von `0x005FEDB0` (zum Beispiel Wirkung
  am vorab gezogenen Spieler statt am genannten in den Fällen 60 und 70–72).
- Katalog P04, nicht als Fehler markiert und nicht nachgeprüft: In `0x005EA5CE` hat die Los-Nummer 5 (Gewicht 30 von
  57) keinen Fall und Fall 2 (Gewicht 12) ist leer – in 42 von 57 Aufrufen geschähe nichts.
- Katalog P02, nicht als Fehler markiert und nicht nachgeprüft: 25 Ereignisroutinen teilen sich eine Merkerliste
  „schon geschehen“ mit 20 Plätzen (`0x00A32738`, Prüfen `0x005E5E90`, Eintragen `0x005E5EE0`); eine gezogene Nummer
  wird eingetragen, bevor die Bedingungen ihres Falls geprüft sind. `0x005E3885` liefert nach der Auslosung immer 1,
  auch wenn nichts ausgelöst wurde; der Tagesverteiler lost dann an diesem Tag nichts weiter aus. Bei Text 982
  liefert die Routine 0, obwohl eine Meldung erschien. Alle als „OK“ eingestuften Einträge des Katalogs.
- `namen.tsv` (400 Hilfsroutinen mit Kurzbeschreibung aus den Läufen A–D): Arbeitsmittel, nicht einzeln bestätigt.

## 8. Was geprüft ist und was nicht
Maschinell über alle Stellen (G):
- Erreichbarkeit der Routine (Abschnitt 2), Skript `meld14.py`, Ausgabe `analyse/meldungen/tot2.txt`;
- Zufallsvergleiche, die nie wahr werden können, und Verteiler direkt hinter einer Zufallszahl (Abschnitt 3),
  Skript `meld3.py`: zwölf Treffer. Einer ist echt (Abschnitt 3). Zwei sind von Hand gelesen und Fehlalarme
  (`0x005F6353`: die Zahl wird vor dem Vergleich um 21 erhöht; `0x0074B8F8`: verglichen wird ein anderer Wert). Bei
  sechs hat der Verteiler weniger Fälle als die Zufallszahl Werte, es ist also kein Fall unerreichbar (`0x005FDE07`,
  `0x005FE312`, `0x005FE989`, `0x0060D6F2`, `0x0061B4C0`, `0x006F5303`). Drei liegen außerhalb der Meldungsroutinen
  und sind nicht gelesen (`0x00630266`, `0x006BDA51`, `0x0073D43C`);
- Kennzeichen, Werte und Argumentzahl aller 70 Zeitungsaufrufe (Abschnitt 4);
- Benutzer der 80 Fragen-Datensätze (Abschnitt 6.4).

Nicht geprüft:
- die Bedingungen der einzelnen Ereignisse innerhalb der Routinen (Schwellen, gelesene Felder, Masken), außer bei den
  in den Abschnitten 3 bis 6 genannten und den schon bekannten Meldungen 1519 und 1235;
- alles aus Abschnitt 7;
- die Spieltexte ab Text 2075 (Entscheidung des Nutzers, siehe „Stand und Umfang“);
- ob jede Nummer der 72 Gewichtstabellen im zugehörigen Verteiler einen Fall hat und umgekehrt. Die maschinelle
  Auswertung (`meld5.py`, `gewichte.txt`) liefert dafür Hinweise, ist aber unzuverlässig (eine Stichprobe bei
  `0x005FC6BC` war ein Fehlalarm). Auffällig und ungeprüft: `0x005FEDB0` (Verteiler mit 41 Zielen, Tabelle mit 25
  Nummern) und `0x005F3BAF`;
- die 1069 Texte ohne Stelle mit fester Nummer (`texte_ohne_stelle.tsv`), soweit sie nicht in den Abschnitten 3 und 6
  behandelt sind;
- die 38 Stellen, an denen die Textnummer aus einer Variablen oder Tabelle kommt (`analyse/meldungen/unklar2.txt`);
- Meldungen außerhalb von `Ereignis.saq` (Dialogtexte aus `deb\MeineDialoge.rch`, Interviews, Texte der
  Spielberichte);
- alles im Spiel: Kein Befund dieses Dokuments ist im Spiel nachgestellt.

## 9. Dateien
- Arbeitsstand (lokal): `analyse/meldungen/notizen.md`.
- Skripte (lokal, `analyse/skripte/`): `meld1.py` Aufrufstellen, `meld2.py` Hüllroutinen und Zuordnung Text ↔ Stelle,
  `meld3.py` Musterprüfung, `meld4.py` Verweis-Analyse, `meld5.py` Gewichtstabellen, `meld6.py` / `meld7.py` Tabellen
  und die erste Fassung dieses Dokuments, `zeig.sh` Ausschnitt des Disassemblys. Zweiter Durchgang: `a3dis.py`
  (beschriftetes Listing), `ctx.py`, `tab.py`, `uses.py`, `faelle.py`, `meld8.py`–`meld14.py` (`meld9.py` Verteiler,
  `meld10.py` Rückverfolgung der Textnummern, `meld11.py` Fragen-Datensätze, `meld12.py` Lesepakete, `meld13.py`
  Zeitungsargumente, `meld14.py` Erreichbarkeit), `dis_reparatur.py`, `namen_mischen.py`.
- Ausgaben (lokal, `analyse/meldungen/`): erste Fassung `aufrufe.tsv`, `texte_stellen.tsv`, `unbenutzt.tsv`,
  `unklar.tsv`, `pruefung.txt`, `tot.txt`, `gewichte.txt`, `tabellen.md`; zweiter Durchgang `stellen2.tsv`,
  `unklar2.txt`, `texte_ohne_stelle.tsv`, `fragen.txt`, `faelle.txt`, `zeitung_argumente.tsv`, `tot2.txt`,
  `erreichbar.tsv`, `dis.pkl`, `namen.tsv`, `tabellen_aufgeloest.md`, Lesepakete `pakete/P01.txt`–`P14.txt`,
  Kataloge `katalog/P*.md` (unvollständig).
