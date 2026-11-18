# Befund: Vereinsvermögen, Bankguthaben, Geldanlagen, Börsenwert (16.11.2026)

Anlass: In der Auswertung des Statistik-Werkzeugs passen „Konto“ und „Mit Anlagen“ nicht zu dem, was das Spiel zeigt.
Vermutung des Nutzers: Einer der beiden gespeicherten Werte ist der Börsenwert des Vereins, der andere das
Vereinsvermögen (Kontostand einschließlich Anlagen). **G** = im Code gelesen und/oder an Daten belegt, **V** = Vermutung.

## Ergebnis in Kürze
- Der **Börsenwert** steht nicht im Vereinssatz. Das Spiel rechnet ihn aus Aktienzahl × Kurs eines eigenen
  Börsen-Objekts (G). Keiner der beiden Werte 0x468 / 0x470 ist der Börsenwert.
- **0x468** ist der Wert, den der Bilanz-Bildschirm als **„Vereinsvermögen am Anfang der Saison“** zeigt (G).
  Das Werkzeug nennt ihn bisher „Konto“ – diese Beschriftung ist falsch.
- **0x470** wird beim Saisonwechsel als 0x468 − Kredite + Anlagen geschrieben (G, Code und 464 von 468 Vereinen).
  Kein Bildschirm, der diesen Wert anzeigt, ist bisher gefunden.
- Das Spiel behandelt 0x468 **an zwei Stellen verschieden** (G): Der Bilanz-Bildschirm zieht die Anlagen davon ab
  (0x468 = Vermögen einschließlich Anlagen), die Vermögensroutine `0x00621EAC` und der Saisonwechsel zählen die
  Anlagen dazu (0x468 = Geld ohne Anlagen). Eine der beiden Rechnungen zählt die Anlagen falsch.
- **Nachtrag (Bildschirmfotos des Nutzers, Karriere383):** Alle Werte des Bilanz-Bildschirms sind aus dem Spielstand
  auf die Mark nachgerechnet (G, Abschnitt „Gegenprobe“). Eine neue Anlage steht weder in den Ausgaben der Saison noch
  ändert sie 0x468 (G). Damit enthält 0x468 die Anlagen bereits; **0x470 und `0x00621EAC` zählen sie doppelt**
  (Folgerung aus diesen beiden Belegen). Später im Code gelesen und genauer: 0x468 führt jede Anlage mit dem
  **eingezahlten Betrag**, nicht mit dem aktuellen Wert – siehe Abschnitt „Geldanlagen: Anlegen, Auflösen“.

## Finanzblock im Vereinsobjekt (G)
Laufzeit-Vereinsobjekt +0x210 = Spielstand-Offset 0x468 (der Vereinssatz liegt um 0x258 versetzt). `P` = dieser Block.
| P + | Spielstand | Inhalt |
|---|---|---|
| 0x00 | 0x468 | int64, Grundwert der Saison („Vereinsvermögen am Anfang der Saison“) |
| 0x08 | 0x470 | int64, beim Saisonwechsel = `0x00621F0D` = [P] − Kredite + Anlagen (Schreiber `0x00772FC4`) |
| 0x18 | 0x480 | Tabelle der Einnahmen und Ausgaben der laufenden Saison (Summe: `0x0061FC81`, Teilroutinen `0x0061FAFA`, `0x0067447D` … `0x006744E3`) |
| 0xC0 | 0x528 | int32, wird zum Grundwert addiert; in allen geprüften Spielständen 0 |
| 0x108 | 0x570 | Kredite: 8 Fächer × 24 B, int64 Betrag (+0), Byte +0x0F Bit 0 = aktiv (Summe `0x006488CA`) |
| 0x1C8 | 0x630 | Geldanlagen: 6 Fächer × 24 B, Byte +0x13 Bit 0 = aktiv, Wert über `0x00647D30` (Summe `0x00648947`) |
| 0x2E0 | 0x748 | int16, Dispokreditrahmen (× Faktor `0x00A3B37C`) |

## Bilanz-Bildschirm (Dialog 349 `IDD_BILANZ_NEU`, Füllroutine `0x004813AD`) (G)
| Feld (Nummer) | Rechnung |
|---|---|
| Vereinsvermögen am Anfang der Saison (4466) | [P] |
| Gewinn in dieser Saison, aktuell (4467) | `0x0061FC81(P, P+0x18)` |
| Aktuelles Vereinsvermögen (4472) | [P] + [P+0xC0] + Gewinn (auch `0x0061F1D9`) |
| Bankguthaben (4463) | Aktuelles Vereinsvermögen − Anlagen + Kredite (`0x0061FD97`) |
| Anlagen (4464) / Kredite (4465) | `0x00648947(P)` / `0x006488CA(P)` |
| Prognosen (4468, 4475), Kreditlimit (4473), investierbarer Betrag (4474) | `0x00622326`, `0x0062218E`, `0x00622A87`, `0x00622BD9` |
| Anzahl Aktien / Kurs / Börsenwert (5511–5513) | nur wenn `0x0069D71D(Verein)` ≠ 0 (Aktiengesellschaft): Börsen-Objekt `0x00405DBE(Land, Verein)` auf `0x008BE408`; Aktienzahl [Objekt+0x20], Kurs `0x00407520(0)`, Börsenwert = Kurs × Aktienzahl |

## Die zweite Rechnung (G)
- `0x00621EAC(Verein)` = [P] + [P+0xC0] + `0x00621F50` (Saisonergebnis) − Kredite + Anlagen. Rund 45 Aufrufer im
  ganzen Spiel (unter anderem Verhandlungen und Computer-Entscheidungen) – das ist „das Vermögen des Vereins“, wie es
  die Spiellogik benutzt.
- `0x00621F0D(Verein)` = [P] − Kredite + Anlagen, einziger Aufrufer `0x00772FC4` im Saisonwechsel (`0x00772BEE`),
  Ergebnis nach [P+8]. Dieselbe Routine gleicht vorher bei Computervereinen den Grundwert aus (Schuldenerlass,
  Kappung über Grenzwerten `0x00A3B2A8`, `0x00A3B2E8`, `0x00A3B314`).
- Daten: 0x470 − 0x468 = Anlagen − Kredite bei 464 von 468 Vereinen (Karriere59, 84), 465 (Karriere93); bei den
  menschlichen Vereinen in 54 von 58 Saisonanfängen (die vier Ausnahmen sind Spielstände, die nicht direkt nach dem
  Saisonwechsel gespeichert wurden und neue Anlagen enthalten).

## Gegenprobe: Bilanz und Finanzen von Manager A in Karriere383 (15.1.2114, Bildschirmfotos des Nutzers) (G)
| Bildschirm | Anzeige | Aus dem Spielstand gerechnet |
|---|---|---|
| Vereinsvermögen am Anfang der Saison | 900,46 Mio | 0x468 = 900 466 234 |
| Gewinn in dieser Saison, aktuell | 92,55 Mio (Bildschirm „Finanzen“: 92 553 864) | nicht nachgerechnet (Summe der Saisontabelle); Erträge 221 801 516 − Aufwand 129 247 652 der 13 Zeilen des Bildschirms ergeben genau diesen Wert |
| Aktuelles Vereinsvermögen | 993,02 Mio | 900 466 234 + 92 553 864 = 993 020 098 |
| Anlagen | 1,005 Mrd | 1 005 014 763 (Formel unten) |
| Bankguthaben | −11,99 Mio | 993 020 098 − 1 005 014 763 = −11 994 665 |
| Zinssatz / Dispokredit | 7,75 % / 6,25 % | Block 1, Wort 0xF8 = 775, Wort 0xFC = 625 (`0x00B5CC80`, `0x00B5CC84`) |
| Anzahl Aktien / Kurs / Börsenwert | 2 475 600 / 307,23 / 760,57 Mio | Börsen-Datensatz: 2 475 600 × 307,23 = 760 578 615 |

- **Wert einer Anlage** (`0x00647D30`): Wert (+8) × Index der Anlageart ÷ Kaufindex (int16 +0x10). Die Anlageart ist
  das Byte +0x12, der Index steht in `0x00B5CC8C` + Art × 4 = Block 1 ab 0x104 (Karriere383: 1020, 1321, 1234, 1532,
  728 …; alle Anlagen des Vereins haben Art 0). Die Summe der gespeicherten Werte (985,8 Mio) ist also nicht der
  angezeigte Betrag.
- **Neue Anlagen sind keine Ausgabe:** Seit Saisonbeginn sind zwei Anlagen zu je 50 Mio. dazugekommen (Summe der aktiven
  Werte 885,8 → 985,8 Mio). Der Bildschirm „Finanzen“ führt dafür keinen Posten, und 0x468 bleibt innerhalb einer Saison
  gleich, auch wenn angelegt wird (Karriere54 → Karriere56).
- **Zinsen:** Der Wertzuwachs der Anlagen seit Saisonbeginn (19,2 Mio) steckt in „Anlagen“, aber nicht im Gewinn. Das
  angezeigte Bankguthaben sinkt deshalb mit dem Zuwachs. (Überholt: Es fehlt nicht nur der Zuwachs der laufenden
  Saison, sondern der gesamte Zuwachs seit dem Anlegen – Abschnitt „Geldanlagen: Anlegen, Auflösen“.)
- **Börsen-Datensatz:** im Block mit 123 572 Byte (Karriere383: Block 4029), Aufbau im Abschnitt „Börse“.
- Werkzeug vor dem Umbau: „Konto“ 900,47 Mio, „Mit Anlagen“ 1,786 Mrd, „Geldanlagen jetzt“ 985,8 Mio – keiner der
  drei Werte stimmte mit dem Spiel überein (dort −11,99 Mio, 993,02 Mio, 1,005 Mrd).

## Gewinn der Saison: `0x0061FC81` nachgebaut (G, 16.11.2026)
`T` = Saisontabelle = Spielstand 0x480, int32 je Feld, wenn nicht anders vermerkt. Der Gewinn ist
- \+ T[0x08…0x14] (`0x0061FAFA`) + T[0x18, 0x1C] (`0x0067449A`) + T[0x20, 0x24, 0x28] (`0x0067447D`)
- \+ T[0xCC] + T[0xD0] + T[0xD4] − T[0xE0] + T[0xE4] (vorzeichenlos)
- \+ int64 Spielstand 0x6C8 − int64 0x6D0 (Transfereinnahmen und -ausgaben: 111 239 000 und 34 050 000 wie am Bildschirm)
- − (int64 T[0xB0] + int64 T[0xC0] + T[0xC8]) (`0x006744E3`) + T[0xB8] − T[0x58]
- − (T[0x5C] + T[0x60] − T[0x64] + T[0x68] + T[0x6C] + T[0x88]) (`0x0067444B`)
- − (T[0x74] + T[0x78] + T[0x7C] + T[0x80] + T[0x84]) (`0x00674522`) + T[0x70]
- − (T[0x90] + T[0x98] + T[0xA0] + T[0xE8] + T[0x8C] + Stufe A × 10 000 + Stufe B × 100 000) (`0x006743DB`)
- \+ (T[0x9C] + T[0x2C] + T[0xA4] + T[0xEC] + T[0x70]) (`0x006744B1`; T[0x70] zählt das Spiel also zweimal).

Stufe A = Tabelle `0x0089E450` (0, 2, 20, 100) am Byte Spielstand 0x839, Stufe B = Tabelle `0x0089E458`
(0, 2, 10, 30, 15, 50, 20, 80) am Byte 0x83A; welche Ausbaustufen das sind, ist nicht zugeordnet (V: Vereinsgelände).
Die Faktoren 10 000 und 100 000 sind die Laufzeitwerte `0x00A3B3BC` und `0x00A3B37C` (gesetzt ab `0x00627DAD` aus
einer Grundeinheit); sie sind hier aus zwei unabhängigen Anzeigen bestimmt: Dispokreditrahmen 500 × 100 000 = 50 Mio.
und Gewinn auf die Mark genau. **Nur für eine Karriere in DM belegt.**
Ergebnis für Manager A in Karriere383: 92 553 864 = Anzeige. Welche Felder zu welcher Zeile des Bildschirms „Finanzen“
gehören, ist nicht zugeordnet.

## Börse (G)
- Aktiengesellschaft: Bit 0 des Bytes Spielstand 0x904 (`0x0069D71D`, statisch `0x01A7391C`).
- Börsen-Objekt `0x008BE408`: Anzahl benutzter Datensätze int32 bei +0x20, Datensätze ab +0x34 zu je 264 Byte
  (`0x00405DBE` sucht Land +0x1C und Verein +0x1E). Im Spielstand der Block mit 123 572 Byte = 20 + 468 × 264
  (Anzahl bei 0, Datensätze ab 20). Aktienzahl +0x20; Kurs = Gleitkommawert +0x38 + 4 × ((Wort +0x24) mod 52)
  (`0x00407520`, Ring aus 52 Kursen). Firmen (Sponsoren) stehen im selben Block ohne gültiges Land.
- Karriere383: 211 benutzte Datensätze, davon 17 Vereine. Beide menschlichen Vereine sind Aktiengesellschaften
  (seit einem Zeitpunkt zwischen Karriere1 und Karriere97).

## Werkzeug (umgebaut am 16.11.2026)
`tools/a3export.py`: `finance()` rechnet je Verein `vs` (Vermögen Saisonbeginn), `gw` (Gewinn), `va` (aktuelles
Vermögen), `an` (Anlagen zum aktuellen Wert), `kr` (Kredite), `ba` (Bankguthaben); `stock_market()` liefert Aktienzahl,
Kurs und Börsenwert (`ag`). 0x470 wird nicht mehr verwendet. `a3verlauf.py` führt die sieben Geldwerte je Verein und
Spielstand mit. Die Vorlage zeigt sie in der Vereinsliste, im Vereinskopf und im Managerverlauf.
Geprüft: Für Manager A in Karriere383 liefert das Werkzeug 900 466 234 / 92 553 864 / 993 020 098 / 1 005 014 763 /
0 / −11 994 665 und den Börsenwert 760 578 615 – die Werte des Spiels.
**Zweite Gegenprobe (Bildschirmfotos „Bilanz“ und „Finanzen“ von Manager B, Karriere383), nach dem Umbau gemacht:**
| Wert | Spiel | Werkzeug |
|---|---|---|
| Vereinsvermögen am Anfang der Saison | 1,043 Mrd | 1 043 793 717 |
| Gewinn in dieser Saison | 54 049 556 | 54 049 556 |
| Aktuelles Vereinsvermögen | 1,097 Mrd | 1 097 843 273 |
| Anlagen | 870,57 Mio | 870 573 587 |
| Bankguthaben | 227,26 Mio | 227 269 686 |
| Aktien / Kurs / Börsenwert | 832 100 / 506,26 / 421,25 Mio | 832 100 / 506,26 / 421 258 954 |

Alle Werte stimmen (das Spiel schneidet die Anzeige nach zwei Stellen ab, es rundet nicht). Der Gewinn stimmt auch hier
auf die Mark, obwohl die Formel an diesem Verein nicht angepasst wurde. Für die übrigen Vereine und Spielstände ist
dieselbe Rechnung angewandt, aber nicht einzeln mit dem Spiel verglichen.

**Seite als Datei:** Die gebaute Seite zeigte als lokal geöffnete Datei alle Reiter gleichzeitig und Umlaute falsch,
weil ihr zwei Dinge fehlten, die die Artefakt-Hülle sonst mitbringt: die Regel `[hidden] { display: none }` (wird von
`section.view { display: flex }` überstimmt) und die Zeichensatz-Angabe. Beides steht jetzt in der Vorlage.

## Geldanlagen: Anlegen, Auflösen, „doppelte Zinsen“ (16.11.2026)
### Code (G)
- **Anlegen** (`0x00444359`, Dialog): Fach +0 (eingezahlt) = Fach +8 (Wert) = Betrag, +0x12 Anlageart, +0x10 = aktueller
  Index der Art, +0x13 Bit 0 gesetzt, +0x14 Datum (`0x00676A74`). **Sonst wird nichts gebucht**: weder der Grundwert
  0x468 noch die Saisontabelle ändern sich.
- **Jährliche Fortschreibung** (`0x00648D8F`, je Verein über `0x00648D1A`): Wert (+8) = Wert × Index ÷ Kaufindex,
  Kaufindex = 1000, +0x14 = 0. Der eingezahlte Betrag (+0) bleibt stehen; eine Buchung ins Vermögen gibt es hier nicht.
- **Auflösen** (`0x00648788(P, Fach)`; vom Dialog `0x00444471`, automatisch für Anlagen der Art ≠ 0 über `0x00648847`):
  Differenz = aktueller Wert − eingezahlter Betrag. Positiv → T[0xA4] += Differenz, negativ → T[0xA0] += Verlust (beide
  int32, je Auflösung bei 2 147 483 647 gekappt), dann +0x13 = 0. T[0xA4] gehört zu den „Sonstigen Einnahmen“
  (`0x006744B1`: T[0x9C] + T[0x2C] + T[0xA4] + T[0xEC] + T[0x70]; die Bildschirmzeile ist diese Summe + T[0x70]).
- **Verfügbares Geld** (`0x00622BD9`, rund 30 Aufrufer, am Bildschirm „Maximal noch investierbarer Betrag“):
  Grundwert + Gewinn + Kreditlimit ± laufende Transfers. Die Anlagen werden **nicht** abgezogen.
- **Wöchentliche Kreditroutine** (`0x006482A6`): rechnet mit dem Bankguthaben `0x0061FD97`; ist es negativ, fallen
  Dispozinsen an (Satz `0x00B5CC82`, bis zum Dispokreditrahmen).
- **Saisonabschluss** (Routine um `0x00621A42`–`0x00621D4F`): auf einen positiven Saisongewinn (`0x00621F50`) Steuer
  (`0x006218DF`, Satz Byte `0x00B5DFA9` in Prozent) und bei Aktiengesellschaften ein Fünftel als Dividende (höchstens
  2 Mrd.); der Rest wird als Saisonergebnis abgelegt (Verein +0xE10, zwei ältere dahinter).

### Test des Nutzers (G): `saves/patchtest/anlage-vorher.an3` (15.1.2114) → `anlage-nachher.an3` (22.1.2114)
Aufgelöst wurde eine Anlage von Manager A: eingezahlt 50 000 000, gespeicherter Wert 400 641 900, Index 1020 →
aktueller Wert 408 654 738. Vorhersage aus dem Code: T[0xA4] += 358 654 738.
| | vorher | nachher | Änderung |
|---|---|---|---|
| T[0xA4] | 507 973 | 359 162 711 | +358 654 738 (genau die Vorhersage) |
| Gewinn | 92 553 864 | 451 127 602 | +358 573 738 (dazu eine Woche Spielbetrieb) |
| Aktuelles Vereinsvermögen | 993 020 098 | 1 351 593 836 | +358 573 738 |
| Anlagen | 1 005 014 763 | 596 360 025 | −408 654 738 |
| Bankguthaben (Anzeige) | −11 994 665 | 755 233 811 | **+767 228 476** |
Der Verein von Manager B ist in derselben Woche unverändert bis auf −138 000 Gewinn.

### Deutung
- Das angezeigte Bankguthaben steigt beim Auflösen um Auszahlung **plus** Wertzuwachs (2 × Wert − Einzahlung). Das ist
  die im Forum gemeldete „doppelte Zinsen beim Auflösen“ (G).
- **Ursache (G für die Rechnung):** Das Vermögen (Grundwert + Gewinn) führt eine Anlage mit dem eingezahlten Betrag – der
  Zuwachs wird erst beim Auflösen als Einnahme gebucht. Die Anzeige „Bankguthaben“ zieht dagegen den **aktuellen** Wert
  ab. Solange eine Anlage läuft, steht das Bankguthaben deshalb um ihren ganzen bisherigen Zuwachs zu niedrig da
  (Manager A vor dem Test: 1 005,0 Mio. Wert bei 250 Mio. Einzahlung → 755 Mio. zu niedrig); beim Auflösen
  verschwindet der Fehlbetrag.
- **Der Zuwachs wird nur einmal ins Vermögen gebucht (G, Code):** Der Saisonabschluss schreibt den Grundwert so fort
  (`0x00621E73`–`0x00621EA4`): [P] += Saisonergebnis `0x00621F50` − Steuer − Dividende, danach [P] += [P+0xC0]. Die
  Anlagen kommen darin nicht vor, und die jährliche Fortschreibung der Fächer bucht nichts. Der Zuwachs einer Anlage
  erreicht das Vermögen also genau einmal: beim Auflösen.
- **Der Index steigt einmal im Quartal** (Aussage des Nutzers, 16.11.2026: Wertzuwachs je Quartal nach gewählter
  Anlageart, mit unterschiedlichen Zinsen und Risikostufen). Dazu passen die Daten der Saison 2113/14 und 2114/15 für
  Art 0: 1000 (9.7. bis 17.9.), 1010 (Kaufindex einer im Herbst getätigten Anlage), 1020 (15.1.), 1031 (21.5.), rund
  1043 zum Saisonende; die übrigen Arten stehen in Karriere383 bei 1321, 1234, 1532 und 728.
- **Beleg an Daten innerhalb einer Saison (G, Skript `anlage2.py`):** Manager A, 15.1.2114 (`anlage-vorher`) → 21.5.2114
  (`vorher`), dazwischen keine Anlage getätigt oder aufgelöst: Index 1020 → 1031, Anlagen +10 838 393, Gewinn und Vermögen
  +9 871 311, angezeigtes Bankguthaben −967 082. Kein Feld der Saisontabelle wächst im Takt der Anlagen (T[0x2C], T[0x38],
  T[0x3C], T[0x40] sind feste Wochenraten eines Jahresbetrags). Der Zuwachs der Anlagen erhöht das Vermögen also nicht,
  solange die Anlage läuft; er wird vom angezeigten Bankguthaben abgezogen.
- **Der Nutzer widerspricht (16.11.2026):** Er hatte laut Bilanz sein ganzes Vermögen in den Anlagen (Bankguthaben
  −12 Mio.), löst 408 Mio. auf und hat 755 Mio. auf dem Konto – also 50 + 358 + 358. Die Beobachtung stimmt (G). Strittig
  ist, welche Zahl falsch ist: Nach den Buchungen stammen die 993 Mio. Vermögen allein aus den Saisonergebnissen, und in
  die fünf Anlagen sind zusammen nur 250 Mio. eingezahlt; die Anzeige zieht aber 1 005 Mio. ab. Prüfbar im Spiel: ob im
  Stand vor dem Auflösen Ausgaben weit über Dispo und Kreditlimit möglich sind.
- **Echte Folgen der falschen Anzeige (G im Code, Größe nicht gemessen):** (1) Dispozinsen auf ein Minus, das es nicht
  gibt; (2) `0x00621EAC` und 0x470 zählen den eingezahlten Betrag doppelt; (3) der beim Auflösen auf einmal gebuchte
  Zuwachs vieler Jahre wird am Saisonende versteuert und bei einer AG zu einem Fünftel als Dividende ausgeschüttet.
- **Einfache Gegenprobe im Spiel:** In `anlage-vorher` (Bankguthaben −12 Mio.) prüfen, ob ein Transfer über deutlich
  mehr als 66 Mio. (Dispo + Kreditlimit) möglich ist. Wenn ja, ist das Geld da und nur die Anzeige falsch.

## Korrektur `konto-anlagen` (16.11.2026) – im Spiel bestätigt, seit Installer 1.44 enthalten (Gruppe Spiellogik)
**Bestätigt (Aussage des Nutzers, 16.11.2026):** Mit der Testfassung im Spielordner beide Spielstände geladen und die
Bilanz abgelesen – „ja passt alles, hab's getestet“ (der Test wurde nicht gespeichert). Welche Einzelwerte er verglichen
hat und ob er im Stand „vor Auflösung“ erneut aufgelöst hat, ist nicht festgehalten.
Einordnung durch den Nutzer: Konto = verfügbares Geld ohne Anlagen; die Anlagen gehören ins Gesamtvermögen; Dispozinsen
bei echtem Minus sind richtig. Auftrag: „Ja, vorbereiten“.
- **Stelle 1, `0x0061FD97` (99 B, Dateioffset 0x21FD97):** Kontorechnung zieht die eingezahlten Beträge der aktiven Anlagen
  ab (Fach +0) statt der aktuellen Werte (`0x00648947`). Alle zehn Aufrufer erwarten dort das Geld ohne Anlagen:
  Bilanz `0x0048163F`; Anzeigen `0x00443F25`, `0x004FB900`, `0x005414F8`, `0x005D7C98`; Prüfung beim Anlegen gegen den
  Dispokreditrahmen `0x0044449F`; Prüfung `0x0047ECE7` (Konto unter −`0x00A3B2E8` und Vereinskennzeichen 0x80);
  wöchentliche Kreditroutine `0x00648375`, `0x006484A6`, `0x0064857C`.
- **Stelle 2, `0x00481426` (81 B, Dateioffset 0x081426):** Bilanzzeile „Aktuelles Vereinsvermögen“ = Konto + aktueller
  Wert der Anlagen − Kredite.
- Kredite: Aufnehmen und Tilgen (`0x0064800A`) buchen nichts in die Saisontabelle außer den Zinsen (`0x00647EFA`); der
  Kreditanteil der Kontorechnung bleibt unverändert.
- Bytes aus `tools/asm_konto.py`, Eintrag `konto-anlagen` in `tools/a3patch.py`; im Erzeuger als Kandidat ausgenommen
  (`KANDIDATEN`), der Installer 1.43 bleibt bytegleich. Testfassung `build/kandidat-1.44/anstoss3.exe`, SHA-256
  `323F968A…2DD4` = 1.43 mit Spiellogik + diese zwei Stellen (Versionsangabe weiter 1.43), mit `dumpbin` gegengelesen,
  kein Sprungziel in den geänderten Bereichen.
- **Unverändert und damit bewusst offen:** Zeile „Vereinsvermögen am Anfang der Saison“ (Buchwert ohne Zuwachs),
  `0x00621EAC` und 0x470 (zählen die Einzahlung doppelt), „Maximal noch investierbarer Betrag“ `0x00622BD9` (zieht die
  Anlagen nicht ab), Kreditrahmen `0x00622DB2` (rechnet die Hälfte der Anlagen zum aktuellen Wert an), weitere
  Vermögensanzeigen (`0x004C82B5`, `0x0061F1D9`).
- **Erwartete Bilanz mit der Testfassung** (Skript `konto_erwartung.py`):
  | Spielstand, Verein | Bankguthaben | Anlagen | Aktuelles Vereinsvermögen |
  |---|---|---|---|
  | `anlage-vorher`, Manager A | 743 020 098 | 1 005 014 763 | 1 748 034 861 |
  | `anlage-vorher`, Manager B | 797 843 273 | 870 573 587 | 1 668 416 860 |
  | `anlage-nachher`, Manager A | 1 151 593 836 | 596 360 025 | 1 747 953 861 |
  | `anlage-nachher`, Manager B | 797 705 273 | 870 573 587 | 1 668 278 860 |

## Offen
1. Entscheidung des Nutzers: Ist die Anzeige „Bankguthaben“ (aktueller Wert statt eingezahltem Betrag abgezogen) ein
   Fehler, der korrigiert werden soll? Betroffen wären `0x0061FD97` (Anzeige und Dispozinsen) und `0x00621EAC` / 0x470.
   Nichts gepatcht.
2. Gegenprobe im Spiel, ob das Geld vor dem Auflösen ausgegeben werden kann (siehe Abschnitt „Geldanlagen“).
3. Ob die doppelte Zählung in `0x00621EAC` ein Fehler mit Folgen ist (Computer-Entscheidungen, Verhandlungen) – nichts
   untersucht, nichts gepatcht.
4. Zuordnung der Felder der Saisontabelle zu den 13 Zeilen des Bildschirms „Finanzen“ (für eine Aufschlüsselung im
   Werkzeug); die beiden Prognosen (`0x00622326`, `0x0062218E`) sind nicht nachgebaut.
5. Gegenprobe an einem älteren Spielstand und an einem Computerverein steht aus (zwei menschliche Vereine in
   Karriere383 sind geprüft).
