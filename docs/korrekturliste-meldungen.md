# Korrekturliste Meldungen – Kandidaten für einen Patch (Stand 17.11.2026)

Grundlage: `docs/befund-meldungen.md` (dort stehen Belege und Adressen; die Spalte „Befund“ nennt den Abschnitt).
Diese Liste ist aus dem Befund zusammengestellt, ohne neues Lesen im Code. **Nichts davon ist gepatcht.**

**Vorgaben des Nutzers (17.11.2026):**
- Es werden nur offensichtliche Fehler korrigiert.
- Absichtlich abgestellte oder nicht fertig entwickelte Ereignisse werden **nicht** aktiviert (Liste in Abschnitt E).
- Jeder Punkt wird einzeln vom Nutzer freigegeben, bevor er gebaut wird. Spalte „Freigabe“ ist dafür leer.
- Korrekturen mit starker Auswirkung auf den Spielablauf sollen im Installer zusätzlich ein- und ausschaltbar sein
  (eigene abwählbare Gruppe neben „Spiellogik“; Vorschlag: wenige Gruppen statt Einzelschalter, weil der Installer
  jede Kombination einzeln prüft). **Zu welcher Gruppe ein Punkt gehört, entscheidet der Nutzer erst, wenn der Punkt
  bearbeitet wird und seine Auswirkungen genau geklärt sind** – vorab wird nichts zugeordnet.
- **Gruppen im Installer (Nutzer, 17.11.2026, bei K01):** neben „rein optisch“ (Statistik, Anzeige) wird die
  Spiellogik getrennt in „Korrekturen mit kleiner Auswirkung“ und „Korrekturen mit größerer oder nicht bekannter
  Auswirkung“. Maßstab für klein oder groß ist, ob die Korrektur das Spielgefühl
  verändert; wer nur einen Text oder eine Anzeige berichtigt (auch wenn dabei eine Absturzgefahr wegfällt), ist „rein
  optisch“. Beide Spiellogik-Gruppen sind abwählbar. K01 gehört zu „kleine Auswirkung“. Die sieben bisherigen
  Spiellogik-Korrekturen (drei Trainer-Korrekturen, `verhasst-noten`, `totalausfall`, `goldkettchen`,
  `konto-anlagen`) gehören alle zu „kleine Auswirkung“ (Nutzer: Auswirkung klein und bekannt). Die zweite Gruppe ist
  damit vorerst leer. Im Installer noch nicht umgesetzt.

**Spalte „Aufwand“** ist eine Schätzung aus dem Befund und vor jedem Patch am Code zu prüfen:
klein = einzelne Bytes oder Konstanten an Ort und Stelle; mittel = zusätzlicher Code (Sprung in freien Bereich,
weiterer Aufruf); groß = neue Logik oder unklar, was richtig wäre. „Text“ = Änderung in `texte\Ereignis.saq` statt in
der exe; dafür braucht der Installer einmalig eine neue Stelle für diese Datei.

## A. Absturzgefahr und Speicherfehler
| Nr | Fehler | Vorschlag | Aufwand | Befund | Freigabe |
|---|---|---|---|---|---|
| K01 | „Hochzeit platzt“ (1093, 1094): Vorroutine `0x005FA5F8` übergibt den Zeiger hinter dem letzten Kaderspieler | einen der gesammelten Kandidaten übergeben | klein bis mittel | 6.14 | freigegeben 17.11.2026; in `tools/a3patch.py` als `hochzeit-platzt` (33 Bytes ab Datei-Offset `0x1FA687`, Zufall 0 bis Anzahl−1 wie in `0x005F9FD0`); Gruppe „Spiellogik, kleine Auswirkung“ (Nutzer, 17.11.2026; im Installer noch nicht umgesetzt), im Spiel nicht geprüft |
| K02 | 1363: Als Name der Frau wird ein nie beschriebener Puffer ausgegeben und ohne Längenprüfung kopiert | leeren Namen übergeben oder die Namen der Frauen holen | klein (leer) / mittel (Namen) | 6.16 | freigegeben 17.11.2026 (Namen beider Frauen); in `tools/a3patch.py` als `frauen-namen-1363` (56 Bytes ab Datei-Offset `0x1FF03A`); Gruppe „rein optisch“, im Spiel nicht geprüft |
| K03 | Zeitung 1880: −5 wird als Managernummer gespeichert, Zugriffe außerhalb der Felder | Kennzeichen an die übergebenen Argumente anpassen | klein | 4 | Fassung A freigegeben 17.11.2026; in `tools/a3patch.py` als `zeitung-1880` (Datei-Offset `0x1F479D`: `40` → `00`); Gruppe „rein optisch“, im Spiel nicht geprüft; Fassung B siehe „Eventuell später“ |
| K04 | Zeitung 1750: zufälliger Stapelinhalt als Wert (wird nicht angewendet) | Kennzeichen anpassen | klein | 4 | freigegeben 17.11.2026; in `tools/a3patch.py` als `zeitung-1750` (Datei-Offset `0x13CCF6`: `01` → `00`); Gruppe „rein optisch“, im Spiel nicht prüfbar (keine sichtbare Änderung) |

## B. Geld wird falsch gebucht
| Nr | Fehler | Vorschlag | Aufwand | Befund | Freigabe |
|---|---|---|---|---|---|
| K05 | 690 „Sie sparen %s ein“ wird als Ausgabe gebucht | Vorzeichen des Tabellenwerts umdrehen | klein | 6.13 | freigegeben 17.11.2026; `geld-690` (Datei-Offset `0x48DF34`: −120 → +120); Gruppe „Spiellogik, kleine Auswirkung“, im Spiel nicht geprüft |
| K06 | 697 „Kostenpunkt: %s“ wird als Einnahme gebucht | Vorzeichen des Tabellenwerts umdrehen | klein | 6.13 | freigegeben 17.11.2026; `geld-697` (Datei-Offset `0x48DF6C`: +80 → −80); Gruppe „Spiellogik, kleine Auswirkung“, im Spiel nicht geprüft |
| K07 | 224/225: erfolgreiche Verhandlung bringt nur den einfachen Betrag | den doppelten Betrag gutschreiben | klein | 6.13 | freigegeben 17.11.2026; `verhandlung-224` (26 Bytes ab Datei-Offset `0x1E89F7`); Gruppe „Spiellogik, kleine Auswirkung“, im Spiel nicht geprüft |
| K08 | Randale: 100 000 Abzug, aber Entwarnungstext 283 statt 284; beide Beträge aus demselben Puffer | Text 284 ausgeben und die Beträge getrennt bilden | mittel | 6.13 | freigegeben 17.11.2026; `randale-284` (48 Bytes ab Datei-Offset `0x1EA186`); Gruppe „rein optisch“, im Spiel nicht geprüft |
| K09 | Straf-Frage Stufe 1: „1 Spiel Sperre“ ohne Sperre, „Strafe“ ohne Geld, „Nicht so schlimm“ bucht die Strafe | Auswertung an die Antworttexte anpassen | mittel bis groß | 6.2 | freigegeben 17.11.2026; `straf-frage-stufe1` (87 Bytes ab Datei-Offset `0x1F2C3C`): Antwort 0 = Sperre 1 Spiel und Teilwert −3 (Werte aus Stufe 2), Antwort 1 = Geldstrafe, Antwort 2 = nichts; Gruppe „Spiellogik, kleine Auswirkung“, im Spiel nicht geprüft |

## C. Wirkung im Spiel falsch
| Nr | Fehler | Vorschlag | Aufwand | Befund | Freigabe |
|---|---|---|---|---|---|
| K10 | `0x00703930`: Streichen aus der zweiten Dreierliste löscht einen Platz der ersten | Endmarke in die richtige Liste schreiben | klein | 6.1 | freigegeben 17.11.2026; `streit-liste` (Datei-Offset `0x3039D4`: `F8` → `FE`); Gruppe „Spiellogik, kleine Auswirkung“, im Spiel nicht geprüft |
| K11 | Vereinszähler Verein +0xDF8: springt von 7 auf 0 | auf 0–7 begrenzen (~~Bit 21 nicht löschen~~: das Löschen ist Absicht, siehe „Nachgelesen“) | klein | 5 | einfache Fassung freigegeben 17.11.2026; `maulwurf-zaehler` (Datei-Offsets `0x29FEA0` und `0x29FEA6`: `0F` → `07`); Gruppe „Spiellogik, kleine Auswirkung“, im Spiel nicht geprüft; Erweiterung siehe „Eventuell später“ K11-B |
| K12 | Sieben Zeitungsmeldungen mit Presse-Abzug, der nie ankommt (1125, 1188, 1197, 1201, 1269, 1528, 1530) | Abzug anwenden wie bei der Korrektur `goldkettchen` (je Meldung einzeln freizugeben) | mittel je Stelle | 4 | alle sieben freigegeben 17.11.2026; `presse-1125`, `-1188`, `-1197`, `-1201`, `-1269`, `-1528`, `-1530` (Blöcke aus `tools/asm_presse.py`, 60 bis 102 Bytes je Stelle, an Ort und Stelle); Gruppe „Spiellogik, kleine Auswirkung“, im Spiel nicht geprüft |
| K13 | Zeitung 1743 / 1744: Wert +5 / −10 beim Manager wird nicht angewendet (Kennzeichen fehlt) | Kennzeichen ergänzen | klein | 4 | **freigegeben 18.11.2026** (in der Nacht allein ausgearbeitet, am 18.11. mit dem Nutzer durchgegangen), eingetragen als `presse-nutzen-vertrauen` (zwei Stellen, Datei-Offsets `0x137AD2` und `0x137B0A`, je 19 Bytes); Gruppe „Spiellogik, kleine Auswirkung“, im Spiel nicht geprüft |
| K14 | 1093: abgesagte Hochzeit findet trotzdem statt | Termin mit dem richtigen Datum streichen | mittel | 6.14 | **freigegeben 18.11.2026** (in der Nacht allein ausgearbeitet, am 18.11. mit dem Nutzer durchgegangen), eingetragen als `hochzeit-absage-1093` (19 Bytes ab Datei-Offset `0x1FA464`); Gruppe „Spiellogik, kleine Auswirkung“, im Spiel nicht geprüft |
| K15 | 1083 „Es kommt zur Trennung“: Trennung wird nicht vollzogen | Beziehung beenden wie bei Text 1079 | mittel | 6.14 | **freigegeben 18.11.2026** (in der Nacht allein ausgearbeitet, am 18.11. mit dem Nutzer durchgegangen), eingetragen als `trennung-1083` (71 Bytes ab Datei-Offset `0x1F9F76`, Block aus `tools/asm_nacht.py`); Gruppe „Spiellogik, kleine Auswirkung“, im Spiel nicht geprüft |
| K16 | 1104: Namen vertauscht (wer wem die Freundin ausgespannt hat) | Namen tauschen | klein | 6.14 | **freigegeben 18.11.2026** (in der Nacht allein ausgearbeitet, am 18.11. mit dem Nutzer durchgegangen), eingetragen als `freundin-ausgespannt-1104` (fünf vertauschte Operanden zwischen Datei-Offset `0x1FABF9` und `0x1FAC31`); Gruppe „rein optisch“, im Spiel nicht geprüft |
| K17 | 1109 / 1110: Wirkungen vertauscht (Wechsel zur Ex-Freundin steht beim falschen Text, Status bleibt „keine Beziehung“) | Wechsel zu 1110 verlegen, Status setzen | mittel | 6.14 | **freigegeben 18.11.2026** (in der Nacht allein ausgearbeitet, am 18.11. mit dem Nutzer durchgegangen), eingetragen als `ex-freundin-1109-1110` (drei Stellen: Datei-Offsets `0x1FAE76`, `0x1FAEDB`, Routine `0x302762`; Blöcke aus `tools/asm_nacht.py`); Gruppe „Spiellogik, kleine Auswirkung“|
| K18 | 1115: angekündigte Trennung und Verlust eines Stärkepunkts fehlen | Wirkung ergänzen | groß | 6.14 | **freigegeben 18.11.2026** (Nutzer: Vergleich „gleich“ statt „größer“ vertauscht; am Code belegt, siehe „Nachgelesen“), eingetragen als `frau-weg-1115` (124 Bytes ab Datei-Offset `0x1FB2F5`, Block aus `tools/asm_nacht.py`): Stärke über 1, Stärke −1, Beziehung beenden; Gruppe „Spiellogik, kleine Auswirkung“; **nur zusammen mit der Textkorrektur von 1115 ausliefern** („%2, die Frau von %1 …“, K39), im Spiel nicht geprüft |
| K19 | 1365: Namen vertauscht (der Zufriedene klagt) | Namen tauschen | klein | 6.16 | **freigegeben 18.11.2026** (in der Nacht allein ausgearbeitet, am 18.11. mit dem Nutzer durchgegangen), eingetragen als `freund-klagt-1365` (zwei vertauschte Operanden ab Datei-Offset `0x1FF1B9`); Gruppe „rein optisch“, im Spiel nicht geprüft |
| K20 | 1172: Streit zwischen den beiden Mitspielern statt mit dem Autor | Streit mit dem Autor eintragen | mittel | 6.15 | **freigegeben 18.11.2026** (in der Nacht allein ausgearbeitet, am 18.11. mit dem Nutzer durchgegangen), eingetragen als `autobiographie-1172` (133 Bytes ab Datei-Offset `0x1FDB07`, Block aus `tools/asm_nacht.py`); Gruppe „Spiellogik, kleine Auswirkung“, im Spiel nicht geprüft |
| K21 | 1193: 112 Tage statt drei Wochen | Dauer 21 ausdrücklich übergeben | klein | 6.15 | **freigegeben 18.11.2026** (in der Nacht allein ausgearbeitet, am 18.11. mit dem Nutzer durchgegangen), eingetragen als `dauer-1193` (Datei-Offset `0x1FDFE0`: `FF` → `15`); Gruppe „Spiellogik, kleine Auswirkung“ |
| K22 | 1215: 7 Tage statt drei Wochen | Dauer 21 übergeben | klein | 6.15 | **freigegeben 18.11.2026** (in der Nacht allein ausgearbeitet, am 18.11. mit dem Nutzer durchgegangen), eingetragen als `dauer-1215` (Datei-Offset `0x1FE61F`: `FF` → `15`); Gruppe „Spiellogik, kleine Auswirkung“; die Tabelle nennt für diese Art eigens 7 Tage, der Text drei Wochen – angeglichen ist an den Text (Entscheidung des Nutzers) |
| K23 | 1225: kein Ausfall statt einer Woche | Tabellenzeile der Art füllen | klein | 6.15 | **freigegeben 18.11.2026**, eingetragen als `verletzung-92-93` (gemeinsam für K23 und K24: Tabellenzeilen bei Datei-Offset `0x4AC6D8` und `0x4AC6E2` nach dem Muster der Arten 90/91; Art 92, 7 Tage); Gruppe „Spiellogik, kleine Auswirkung“, im Spiel nicht geprüft |
| K24 | 1227: kein Ausfall statt zwei Wochen | Tabellenzeile der Art füllen | klein | 6.15 | **freigegeben 18.11.2026**, eingetragen als `verletzung-92-93` (gemeinsam für K23 und K24: Tabellenzeilen bei Datei-Offset `0x4AC6D8` und `0x4AC6E2` nach dem Muster der Arten 90/91; Art 93, 14 Tage); Gruppe „Spiellogik, kleine Auswirkung“, im Spiel nicht geprüft |
| K25 | 1076: 35 Tage statt vier Wochen | Dauer 28 übergeben | klein | 6.14 | **freigegeben 18.11.2026** (in der Nacht allein ausgearbeitet, am 18.11. mit dem Nutzer durchgegangen), eingetragen als `dauer-1076` (Datei-Offset `0x1F9750`: `FF` → `1C`); Gruppe „Spiellogik, kleine Auswirkung“ |
| K26 | 1194: nur „angeschlagen“ statt zwei Wochen Ausfall | Text an die Wirkung anpassen | mittel | 6.15 | **entschieden 18.11.2026 (Nutzer): Text anpassen**, die Wirkung bleibt (14 Tage „angeschlagen“: `0x00766AF9(Spieler, 14)` bei `0x005FE026`; Byte Spieler +0x2F ist ein Zähler in Tagen, Anzeige „Er ist noch angeschlagen.“). Neuer Text 1194: „%1 wurde bei der Gartenarbeit von zwei Hornissen gestochen. Er ist zwei Wochen angeschlagen.“ Rein optisch; Textdatei, zusammen mit K39 |
| K27 | 1224: 14 Tage Ausfall statt eine Woche „angeschlagen“ | Text an die Wirkung anpassen | mittel | 6.15 | **entschieden 18.11.2026 (Nutzer): Text anpassen**, die Wirkung bleibt (Art 91 „Hautausschlag“, 14 Tage Ausfall). Neuer Schluss von Text 1224: „… was ein übles Hautbrennen verursacht. Er fällt zwei Wochen aus.“ Rein optisch; Textdatei, zusammen mit K39 |
| K28 | 1180: angekündigter Verlust eines Frischepunkts fehlt | Abzug ergänzen | mittel | 6.15 | **freigegeben 18.11.2026** (in der Nacht allein ausgearbeitet, am 18.11. mit dem Nutzer durchgegangen), eingetragen als `frische-1180` (65 Bytes ab Datei-Offset `0x1FDD89`, Block aus `tools/asm_nacht.py`); Gruppe „Spiellogik, kleine Auswirkung“ |
| K29 | 1210: angekündigte Trainingseinschränkung fehlt | Text an die Wirkung anpassen | mittel | 6.15 | **entschieden 18.11.2026 (Nutzer): Text neutral fassen**, die Wirkung bleibt (Hobby wird gelöscht, `0x00702CBD(0)` bei `0x005FE463`). Kein anderer Text nennt „eingeschränkt trainieren“, es gibt kein Vorbild für die Wirkung; die Stelle prüft keine Beziehung und übergibt keinen Namen. Neuer Text 1210: „Ihr Spieler %1 ist von einem seiner Bienenvölker angegriffen und mehrfach gestochen worden. Er gibt sein Hobby daraufhin auf.“ Rein optisch; Textdatei, zusammen mit K39. Damit ist auch der Rest 1210 von K40 erledigt |
| K30 | 1217: Führerschein zwei statt ein Monat | Wert 1 setzen | klein | 6.15 | **freigegeben 18.11.2026**, zusammen mit K31 eingetragen als `fuehrerschein` (Datei-Offset `0x1FE6A6`: `02` → `01`); Gruppe „Spiellogik, kleine Auswirkung“, im Spiel nicht geprüft |
| K31 | Führerschein-Zähler wird nie zurückgesetzt | Ablaufmonat speichern und beim Lesen prüfen | groß | 6.15 | **freigegeben 18.11.2026**, eingetragen als `fuehrerschein` (100 Bytes ab Datei-Offset `0x302D31`, Block `fuehrerschein-zaehler` aus `tools/asm_nacht.py`; zwei umgeleitete Aufrufe bei `0x1FE9B4` und `0x1FEB2E`); statt mitzuzählen hält das Byte den Ablaufmonat (siehe „Nachgelesen“); Gruppe „Spiellogik, kleine Auswirkung“, im Spiel nicht geprüft – **Test: Führerschein-Meldung abwarten, speichern, zwei Monate später prüfen** |
| K32 | 1565: Abitur ohne Merker, kann sich wiederholen | Merker setzen | mittel | 6.14 | **freigegeben 18.11.2026**, zusammen mit K38 eingetragen als `schueler-merker` (51 Bytes ab Datei-Offset `0x1F9D1F`, Block `abitur-1565` aus `tools/asm_nacht.py`: Merker 3 vor der Meldung); Gruppe „Spiellogik, kleine Auswirkung“, im Spiel nicht geprüft |
| K33 | 983: enttarnter Spitzel bleibt Spitzel | Spitzel-Bit löschen | mittel | 6.11 | **freigegeben 18.11.2026** (in der Nacht allein ausgearbeitet, am 18.11. mit dem Nutzer durchgegangen), eingetragen als `spitzel-983` (108 Bytes ab Datei-Offset `0x1E4F10`, Block aus `tools/asm_nacht.py`); Gruppe „Spiellogik, kleine Auswirkung“ |
| K34 | 1982: Rückgabe „nichts geschehen“ nach der Meldung | Rückgabe 1 | klein bis mittel | 6.14 | **freigegeben 18.11.2026** (in der Nacht allein ausgearbeitet, am 18.11. mit dem Nutzer durchgegangen), eingetragen als `rueckgabe-1982` (3 Bytes ab Datei-Offset `0x1FB5FE`); Gruppe „Spiellogik, kleine Auswirkung“|
| K35 | 1358 / 1359: Konditionsbonus des privaten Trainers wird nie gerechnet | Zuschlag in der Konditionsrechnung ergänzen | mittel | 6.16 | **freigegeben 18.11.2026**, eingetragen als `konditionsbonus` (80 Bytes ab Datei-Offset `0x57E00`, Block aus `tools/asm_nacht.py`): 5 Punkte Zuschlag für Bit 13, höchstens 100 – Vorbild ist der Raucher (Text 1356 „Konditionshandicap von 5%“ = 5 Punkte Abzug, `0x00457E3A`); `0x00457E00` hat 56 Aufrufer (Anzeige und Rechnung); Gruppe „Spiellogik, kleine Auswirkung“, im Spiel nicht geprüft – **Test: Konditionswerte müssen nach dem Einspielen aussehen wie vorher** |
| K36 | 1342: angekündigtes Karriereende findet nicht statt | Spieler scheidet aus wie bei Text 338 | groß | 6.10 | **freigegeben 18.11.2026**, eingetragen als `karriereende-1342` (53 Bytes ab Datei-Offset `0x1E26B9`): Vorbild `0x0070E29E(Spieler, Verein)` („Spieler scheidet aus Verein und Spiel aus“; fünf Aufrufer, u. a. Text 338 bei `0x00604132` und Text 716 bei `0x006A71CF` im selben Tagesverteiler). Die Hülle `0x005E2BB9` (zufälliger Kaderplatz, Aufruf `0x005E2C10`) und der Verteiler (`0x005EFEA4`, danach Rücksprung) fassen den Spieler nach der Rückkehr nicht mehr an. Block `karriereende-1342` in `tools/asm_nacht.py`; **Gruppe „Spiellogik, größere oder nicht bekannte Auswirkung“ (erster Eintrag dieser Gruppe)**, im Spiel nicht geprüft |
| K37 | `0x0070185C`: Name der früheren Partnerin mit falscher Namensgruppe | richtige Gruppe lesen | klein | 6.14 | **freigegeben 18.11.2026** (in der Nacht allein ausgearbeitet, am 18.11. mit dem Nutzer durchgegangen), eingetragen als `name-fruehere-partnerin` (Datei-Offset `0x301888`: `D6` → `D7`); Gruppe „rein optisch“ |
| K38 | Bit 4 von Spielstand 0x260 doppelt belegt (Gruppen-Anführer / Schüler-Merker) | Schüler-Merker auf freie Bits verlegen | groß | 6.14 | **freigegeben 18.11.2026**, eingetragen als `schueler-merker`: Schüler-Merker von den Bits 3–4 auf die Bits 5–6 verlegt (fünf Bytes bei den Datei-Offsets `0x3064E6`, `0x306513`, `0x306542`, `0x306567`, `0x306591`; siehe „Nachgelesen“); Gruppe „Spiellogik, kleine Auswirkung“, im Spiel nicht geprüft |

## D. Nur Text oder Anzeige
| Nr | Fehler | Vorschlag | Aufwand | Befund | Freigabe |
|---|---|---|---|---|---|
| K39 | „%s“ statt „%1“: 954, 1276, 1338, 1115, 1116, 1117 (Spielername fehlt) | Platzhalter im Text berichtigen | Text, klein je Text | 6.6, 6.14 | **freigegeben 18.11.2026** im Textpaket (954, 1276, 1338, 1355, 1115, 1116, 1117; siehe Abschnitt „Textpaket“); rein optisch; Umsetzung mit dem Installer: `Ereignis.saq` ist verkettet verschlüsselt (jedes Byte XOR dem vorigen gespeicherten Byte), stellenweise Patches gehen nicht |
| K40 | Name der Frau leer: 969, 1296, 1176, 1177, 1210 | Namen der Partnerin übergeben | mittel je Stelle | 6.7, 6.15 | **teilweise:** 1176 und 1177 **freigegeben 18.11.2026** (in der Nacht allein ausgearbeitet, am 18.11. mit dem Nutzer durchgegangen), eingetragen als `frau-1176-1177` (71 Bytes ab Datei-Offset `0x1FDC9C`, Block aus `tools/asm_nacht.py`); Gruppe „rein optisch“. 969 ebenso, eingetragen als `frau-969` (27 Bytes ab Datei-Offset `0x1E4D17`; der Fall verlangt „verheiratet“). 1296 und 1210 über das Textpaket (freigegeben 18.11.2026): 1296 ohne „%2“ (die Straf-Frage `0x005F29BC` übergibt als zweiten Namen immer eine leere Zeichenkette), 1210 neutral gefasst (K29) |
| K41 | 1094: Namen vertauscht, Name der Geliebten falsch | Reihenfolge und Zeitpunkt des Lesens berichtigen | mittel | 6.14 | **teilweise:** %3 **freigegeben 18.11.2026** (in der Nacht allein ausgearbeitet, am 18.11. mit dem Nutzer durchgegangen), eingetragen als `name-geliebte-1094` (Aufrufziel bei Datei-Offset `0x1FA51F`: `0x007017DB` → `0x0070173F`); Gruppe „rein optisch“. Die Reihenfolge von %1 und %2 wird im Textpaket berichtigt (freigegeben 18.11.2026) |
| K42 | 1294: Frage nennt keinen Spieler | Platzhalter in den Text aufnehmen | Text, klein | 6.8 | **freigegeben 18.11.2026** im Textpaket (vorangestellt „Ihr Spieler %1 bricht das Training ab.“); rein optisch |
| K43 | 1309–1311: „Vorher“ mit Zuschlägen, „Nachher“ ohne | beide Werte gleich bilden | mittel | 6.9 | **freigegeben 18.11.2026**, eingetragen als `vorher-1309-1311` (drei Stellen: 87 Bytes ab Datei-Offset `0x1E184C`, je 57 Bytes ab `0x1E18D5` und `0x1E1940`; Blöcke aus `tools/asm_nacht.py`): „Vorher“ ist wie „Nachher“ der gespeicherte Wert, geholt über die Schreiber mit Änderung 0 (`0x00700D27`, `0x007007A1`, `0x00700A6D`; mit 0 ändern sie nichts und rechnen die Motivation neu); Gruppe „rein optisch“, im Spiel nicht geprüft |
| K44 | 1312: Ablenkung als „Mannschaft“ beschriftet | Art 3 übergeben | klein | 6.9 | **freigegeben 18.11.2026** (in der Nacht allein ausgearbeitet, am 18.11. mit dem Nutzer durchgegangen), eingetragen als `art-1312` (Datei-Offset `0x1E19CA`: `01` → `03`); Gruppe „rein optisch“ |
| K45 | 1116 / 1117: Ablenkung als „Privates“ beschriftet | Art 3 übergeben | klein | 6.14 | **freigegeben 18.11.2026** (in der Nacht allein ausgearbeitet, am 18.11. mit dem Nutzer durchgegangen), eingetragen als `art-1116-1117` (Datei-Offsets `0x1FB3AF` und `0x1FB407`: `02` → `03`); Gruppe „rein optisch“ |
| K46 | 1168: Stimmung als „Beliebtheit Öffentlichkeit“ beschriftet | Art 11 übergeben | klein | 6.15 | **freigegeben 18.11.2026** (in der Nacht allein ausgearbeitet, am 18.11. mit dem Nutzer durchgegangen), eingetragen als `art-1168` (Datei-Offset `0x1FDA34`: `0A` → `0B`); Gruppe „rein optisch“ |
| K47 | 1388 statt 1389 (zwei Spieler derselben Position) | Text 1389 ausgeben | klein | 6.16 | **freigegeben 18.11.2026** (in der Nacht allein ausgearbeitet, am 18.11. mit dem Nutzer durchgegangen), eingetragen als `text-1389` (Datei-Offset `0x1FF98F`: `6C` → `6D`); Gruppe „rein optisch“ |
| K48 | 285 nennt „20 Punkte“, abgezogen werden je 5 | Text an die Wirkung anpassen | Text, klein | 6.13 | **freigegeben 18.11.2026** im Textpaket („je 5 Punkte Beliebtheit in der Öffentlichkeit, bei den Fans und bei den Medien“); rein optisch |
| K49 | 1207 „Single“ ohne Prüfung des Beziehungsstands | Text anpassen | mittel | 6.15 | **entschieden 18.11.2026 (Nutzer): Text anpassen**, das Wort „Single“ entfällt (Textpaket); die Wirkung bleibt; rein optisch |
| K50 | 1218: Schlagzeile nennt Presse −2, angewendet −5 | – (keine Korrektur) | klein | 6.15 | **gestrichen 18.11.2026 (Nutzer): keine Korrektur.** Der an die Schlagzeile übergebene Wert wird weder angezeigt noch angewendet (belegt bei K04); angewendet werden die −5 direkt an der Stelle |

## E. Nicht korrigieren (Vorgabe des Nutzers: nichts aktivieren, was abgestellt oder unfertig ist)
- Die 18 Routinen ohne Aufrufer mit ihren 94 Texten (Befund Abschnitt 2).
- Fest abgeschaltete Blöcke: `0x0060C687`, `0x005F2E43`, `0x005F2F07`.
- Leere Lose und Fälle ohne Los-Nummer: 1289; Block mit Text 281; 1377, 1395, 1396, 1399, 1402–1405; die leeren
  Lose in `0x005F9ED7`, `0x005FA394`, `0x005FB264`, `0x005FEDB0`, `0x005EA5CE`; zweite Stelle von 1094.
- Texte ohne jede Stelle (1084–1086, 1095, 1096, 1118–1121, 1226, 1370, 1374, 1376, 1386, 1387 …) und die
  Fragen-Datensätze ohne Benutzer; Texte 1728 und 1733.
- Ereignis 769 (Aufhebung der Ausländerbeschränkung): die versprochene Regel gibt es im Programm nicht.
- Die sieben Ereignisse mit fest eingetragenen Spielernamen (1348–1351, 1353–1355).
- 18 Hobbys ohne Ereignis.

## F. Vom Nutzer zu entscheiden: Fehler oder Absicht?
Fertig ausgearbeitete Ereignisse mit Los-Nummer, die an einer einzelnen Bedingung scheitern. Eine Korrektur wäre
jeweils klein, würde aber Meldungen bringen, die das Spiel bisher nie gezeigt hat.
Spalte „Einschätzung“ ist die Vermutung aus dem Gespräch vom 17.11.2026, keine Entscheidung; entschieden wird je
Punkt bei der Bearbeitung.
| Nr | Sachverhalt | mögliche Korrektur | Einschätzung (V) | Befund | Entscheidung |
|---|---|---|---|---|---|
| F01 | Affäre fliegt auf (1126, 1127, 1128, 1236): das nötige Bit wird nie gesetzt | Bit beim Eintragen der Geliebten setzen (dann auch Namen in 1126 / 1127 berichtigen) | Versehen, wahrscheinlich; starke Auswirkung (Ereignisse kommen dann überhaupt erst) | 6.14 | **freigegeben 18.11.2026**, eingetragen als `affaere-fliegt-auf` (Datei-Offsets `0x3029A7` und `0x1FB7AB`); **Gruppe „Spiellogik, größere oder nicht bekannte Auswirkung“**, im Spiel nicht geprüft; dass Bit 2 beim Eintragen der Geliebten gesetzt werden sollte, ist ein Schluss. Zustände der Affäre im Flagwort 0x194: Bit 2 „läuft unentdeckt“ (lesen `0x00702A5B`, einziger Leser die Vorroutine `0x005FB98E`), Bit 3 „Frau ahnt etwas“ (lesen `0x00702A7B`, Vorroutine `0x005FBB71` der Folgemeldungen 1129/1130); `0x00702A02` wechselt von 2 nach 3 (bei 1123 und 1236), `0x00702962` beendet die Affäre (löscht Index und beide Bits; bei 1126 und 1129). Bit 2 setzt niemand; `0x007029A7` („neue Geliebte“, Texte 1251–1253) trägt nur den Namensindex ein. Korrektur: (1) `0x007029A7` setzt zusätzlich Bit 2 (Block `geliebte-7029A7`, 46 von 91 Bytes); (2) bei 1126 `0x00702962` erst nach der Meldung, damit der Name der Geliebten noch gelesen wird (Block `affaere-1126`, 88 von 100 Bytes ab `0x005FB7AB`); (3) Text 1127 ins Textpaket: „%2, die Frau von %1, setzt einen Detektiv an …“. Alle vier Fälle verlangen Krisenstufe 0; Lose der Routine und Gewicht der Vorroutine (Los-Nummer 6, Gewicht 100) unverändert |
| F02 | 1178 / 1179: Zufall 0–1 vor vier Fällen | Zufall 0–3 | offen (Zählfehler oder bewusst abgeschaltet) | 3.1 | **freigegeben 18.11.2026**, eingetragen als `hobby-1178-1179`; Gruppe „Spiellogik, größere oder nicht bekannte Auswirkung“, im Spiel nicht geprüft. Die Fälle 2 und 3 sind vollständig gebaut: 1178 (verheiratet, ohne Kind; Teilwert 0x273 −10, Name der Frau wird übergeben) und 1179 (nicht verletzt; Verletzung Art 46 für 21 Tage). Korrektur: Datei-Offset `0x1FDBAE` `6A02` → `6A04` (Zufall 0–3); die Fälle 0 und 1 (Texte 1174–1177) kommen dann halb so oft. Dazu im Textpaket 1178 „ihrem Mann“. |
| F03 | 888 / 889: Zufall 0–9 vor zwölf Einträgen | Zufall 0–11 | Versehen, wahrscheinlich | 3.2 | **freigegeben 18.11.2026**, eingetragen als `bauverzoegerung-888-889`; Gruppe „Spiellogik, kleine Auswirkung“, im Spiel nicht geprüft. Es sind Gründe für eine Bauverzögerung im Stadion (Satz 876/877: „Die Bauarbeiten in Block %c Ihres Stadions verzögern sich wegen %s leider um eine Woche / zwei Wochen“), nicht für eine Spielabsage. Korrektur: Datei-Offset `0x202373` `6A0A` → `6A0C` (Zufall 0–11). Dazu im Textpaket 889 „schlechten Wetters“ (sonst „wegen wegen schlechtem Wetter“) und 888 ohne das Leerzeichen am Ende. |
| F04 | 1173: Zufall 0–2, vierter Zweig nie | Zufall 0–3 | Versehen, wahrscheinlich | 6.15 | **freigegeben 18.11.2026**, eingetragen als `handbuch-1173`; Gruppe „Spiellogik, kleine Auswirkung“, im Spiel nicht geprüft. Der vierte Zweig (`0x005FDB8E`) zeigt nur die Meldung 1173, ohne Wirkung. Korrektur: Datei-Offset `0x1FDA79` `6A03` → `6A04` (Zufall 0–3); die drei anderen Zweige (1169/1170, 1171, 1172) kommen dann in je einem von vier statt einem von drei Fällen. |
| F05 | 1481: Bedingung „Alter unter 20“ im Zweig „Alter ab 25“ | Bedingung an die richtige Stelle (vorher am Code klären, wohin) | Versehen | 3.4 | **freigegeben 18.11.2026**, eingetragen als `vermittler-1481`; Gruppe „Spiellogik, größere oder nicht bekannte Auswirkung“, im Spiel nicht geprüft. Verhandlung mit einem Spielervermittler (`0x00705DBE` = 2): Alter unter 25 → Text 1480 (Ausstiegsklausel, Merker 4); sonst „Alter unter 20 und Byte +0x54 > 10 und Byte +8 < 1“ → 1481, sonst 1 von 100 → 1482. Korrektur (Schluss aus dem Text „beste Entwicklungschancen“: gemeint sind die unter 20-Jährigen): die Prüfung „unter 20“ vor die Prüfung „unter 25“ stellen (Block `vermittler-1481`, 76 von 103 Bytes ab `0x00768940`). Spieler unter 20, die beide Zusatzbedingungen erfüllen, bekommen dann 1481 statt 1480 und damit keinen Merker 4. |
| F06 | Alle Ehefrau-Ereignisse verlangen eine Geliebte | Bedingung auf „verheiratet“ beschränken | Versehen, ziemlich sicher; starke Auswirkung (Ereignisse kommen dann regelmäßig) | 6.14 | **freigegeben 18.11.2026**, eingetragen als `ehefrau-ereignisse`; **Gruppe „Spiellogik, größere oder nicht bekannte Auswirkung“**, im Spiel nicht geprüft. Die Vorroutine `0x005FB634` verlangt Status „verheiratet“ und eine Geliebte (`0x005FB6C5` / `0x005FB6CC`). Beleg für ein Versehen: Der einzige Fall, der eine Geliebte braucht (Text 1123, `0x005FB49A`), prüft sie selbst noch einmal; alle anderen Fälle (1115, 1116, 1117, 1122, 1124/1125, 1982) nennen nur die Ehefrau. Korrektur: der Sprung `je` bei Datei-Offset `0x1FB6CC` ist gestrichen (`7422` → `9090`). Lose der Routine: Fälle 1–9 Gewicht 3, 10 und 11 Gewicht 1 (Tabelle `0x0088E74C`), Fälle 4–7 leer; Los-Nummer 5 im Tagesverteiler mit Gewicht 100 von 10000. |
| F07 | Gruppenbildung 1412: Zweig „Gruppe für den Trainer“ nie erreichbar | – (unklar, welche Schwelle gemeint war) | nicht korrigieren: die Gruppen sind unfertig (Auftreten, Beitritt und Austritt liegen in toten Routinen). Beobachtung des Nutzers: in mehreren tausend Spielstunden ist mit Gruppen nie etwas geschehen | 6.12 | |
| F08 | Schlagzeile 1201 („%1 geht lieber Golfen - %2 Millionengehalt für nichts“): als %2 wird eine leere Zeichenkette übergeben (`0x005FE272`, Platzhalter `0x00A326E2`), obwohl direkt davor der Vereinsname gebildet wird (`0x005FE268`, Fall 19 nach `[ebp-68h]`) | Puffer übergeben – aber Fall 19 liefert „den %c1%c“ / „die %c1%c“, eine Vorlage mit Steuerzeichen-Platzhaltern für eine zweite Formatierung (so benutzt in `0x0073AFCE` / `0x0073B00E`), die in einer Schlagzeile nicht verwendbar ist; welcher Fall gemeint war, ist nicht belegbar | eher Absicht oder aufgegebener Versuch: mit leerem %2 liest sich die Schlagzeile vollständig. Nicht korrigieren, solange unklar ist, was dort stehen soll (gefunden 17.11.2026 bei K12, vom Nutzer aufgenommen) | 4 | |

## Eventuell später (vom Nutzer zurückgestellt, nicht freigegeben)
| Nr | Was | Wirkung im Spiel | Aufwand | Stand |
|---|---|---|---|---|
| K03-B | Zeitung 1880 (`0x005F47A7`): zusätzlich die Managernummer (Byte Verein +0x8A) übergeben und das Kennzeichen `0x40000001` behalten, statt Fassung A | Wird 1880 die oberste Schlagzeile des Tages, sinkt die Beliebtheit des Managers in der Öffentlichkeit (Manager +0x3A) um 5 (Skala 0–100); bisher nie geschehen. Spiellogik | mittel (zusätzlicher `push`, geschätzt 40–80 Bytes in `0x005F3BAF`, Bytes nicht ausgearbeitet) | zurückgestellt 17.11.2026; ersetzt Fassung A, nicht zusätzlich |
| K11-B | Zähler der Maulwurf-Affäre von 3 auf 4 Bits erweitern (Verein +0xDF8, Bits 18–21), damit die Stände 8 und 10 erreichbar werden; den Merker „Schlagzeile schon erschienen“ von Bit 21 auf ein freies Bit verlegen (Bits 22–31 werden im Programm nirgends benutzt) | Die Schlagzeilen 1707 („… läßt Maulwurf gewähren …“) und 1708 („Präsident …: Akzeptiere Tatenlosigkeit nicht!“) können erscheinen; bisher nie möglich. Spiellogik; betrifft nur Spielstände mit einem Maulwurf im Kader | mittel bis groß: mindestens acht Stellen (Leser `0x0069FE67`, Erhöhung `0x0069FE85` / `0x0069FEC0` / `0x0069FEF2` und Grenze 15, Setzer `0x0069FF16` / `0x0069FF49`, Merker `0x005E536D` / `0x005E5650`); zu klären: alte Spielstände mit gesetztem Bit 21 | zurückgestellt 17.11.2026; baut auf K11 auf (Grenze dann wieder 15) |

Zu 1880 am Code belegt (17.11.2026): Das Ereignis verlangt Bit 1 im Merkerbyte Spielstand 0x24D (`0x006FF99A` bei
`0x005F4730`); gesetzt wird es von `0x006FF715` (Aufrufer `0x0051731D`, `0x00517551`, `0x0074EE7B`, nicht gelesen).
V: der Merker bedeutet „gedopt“.

## Nachgelesen zu K01–K10 (17.11.2026, am Code belegt, soweit nicht als V markiert)
- **K01:** `0x005FA394` zieht Los 1–3 mit gleichem Gewicht (Tabelle `0x0088E700`); Fall 1 (1093) verlangt Status
  „Freundin“ und Krisenstufe 0, Fall 2 (1094) Status „Freundin“ und eine Geliebte, Fall 3 ist leer; dazu der Merker
  der letzten 20 Ereignisse (`0x005E5E90`). Die Kader-Zeigerliste wird von `0x00635F76`, `0x00636120` ff. und
  `0x006362A0` immer nur für die Plätze 0 bis Kadergröße−1 neu geschrieben; der Platz dahinter behält, was vorher
  dort stand (Zeiger eines früheren Kaderspielers dieses Platzes, 0 oder nie beschrieben). Welcher Fall vorliegt,
  entscheidet sich zur Laufzeit; ein früherer Spieler mit Status „Freundin“ bekäme heute die Meldung ohne Termin.
- **K03:** Der Merker (Bit 1 in Spielstand 0x24D) wird von `0x006FF715` gesetzt; zwei Aufrufer (`0x0051731D`,
  `0x00517551`) liegen in der Routine `0x00516F7A`, die die Dialogtexte 4069 und 4070 („… nicht bereit, sich dopen zu
  lassen“) ausgibt, der dritte (`0x0074EE7B`) nach Zufall. Der Merker heißt also „gedopt“. `0x0078A0F5` prüft die
  Managernummer nur auf ≠ 0 und ruft mit −5 `0x006A426B` auf.
- **K04:** Die Werte im Satz der obersten Schlagzeile (`0x01C6AC84`) liest nur `0x0078A0F5`; die Anzeige
  (`0x005D8624`) übergibt nur die zwei Textpuffer. Der Wert wird also nirgends angezeigt.
- **K05/K06:** Der Merker 16000 + Index steht in der Liste `0x00A32738`, die nur die letzten 20 Ereignisse aller Arten
  behält (`0x005E5EE0`). Die Geld-Ereignisse können sich also über die Jahre wiederholen.
- **K07:** Verein +0x105 ist die Liga (in unteren Ligen halber Betrag: 75 000 statt 150 000). Verein +0x2F8 ist einer
  von drei Summanden (+0x2F4, +0x2F8, +0x2FC) der Einnahmensumme `0x006200BB`, die in die Abrechnung `0x00622201`
  und einen Dialog (`0x004A21F7`) eingeht; der Betrag wird also einmal als Einnahme geführt (V: Posten Sponsoren).
- **K09:** `0x007049CC` zählt Byte Spielstand 0x286 hoch. Gelesen wird es im Spielerdialog (`0x0055CEB6`, Feld 4994)
  und in `0x0070B417` als Bedingung (Zähler > 0 und Trainer-Teilwert unter 90). V: Zahl der Strafen.
- **K10:** Erste Liste = Freunde (eingetragen bei Text 1366), zweite = Streit (Text 1377); dazu Einzelplätze bester
  Freund (0x1E4, Text 1362) und Erzfeind (0x1E6, Text 1380). Gelesen werden die Listen im Spielerdialog
  (`0x0055F443`, `0x0055F4E9`, `0x00565969`, `0x00565A7A`: Namen), bei der Auswahl der Spieler für Ereignisse
  (`0x005ECE74`, `0x005ECF13`, `0x005E3187` ff., `0x0060A257` ff.), bei einem Abzug von 5 auf einen Teilwert der
  Motivation (`0x005F78A4`) und beim Aufräumen nach Abgängen (`0x007105DF`, `0x0071064A`).

- **K09, Nachtrag:** `0x0070B417` ist Fall 19 von 31 der Prüfroutine `0x0070AFA0` (einziger Aufrufer `0x0070AAE1`);
  die aufrufende Routine wählt per Zufall einen der Fälle und setzt daraus einen Text zusammen (CString, `strcpy`).
  Der Zähler entscheidet dort also nur, ob ein bestimmter Text in Frage kommt, er ändert keinen Spielwert.
- **K11 und die Maulwurf-Affäre:** Berichtigung zum Befund Abschnitt 5: Bit 21 von Verein +0xDF8 ist
  kein fremder Merker, sondern „Schlagzeile zu diesem Stand schon erschienen“ (gesetzt `0x005E5650`, geprüft
  `0x005E536D`); `0x0069FE73` und `0x0069FF06` löschen es absichtlich bei jeder Änderung des Zählers. Der Zähler hat
  an allen Stellen 3 Bits (Maske `0x1C0000`), ausgewertet werden aber die Stände 2, 3, 5, 6, 8 und 10 (Texte
  1703–1708): 1707 und 1708 sind nie erreichbar. Beim Saisonwechsel setzt `0x0069FF06(0)` (`0x0077360D`) Zähler und
  Bit 21 zurück. Maulwurf = Bit 16 im Flagwort des Spielers (`0x00700272` / `0x00700294`). `0x005E50BA` (täglicher
  Verteiler, Aufrufer `0x005EFDE5`): ist kein Maulwurf im Kader, wird unter den Kandidaten einer zufällig bestimmt
  (Gesamtmotivation Spieler +0xCA unter 70, Bits 0x120 in Wort +0x12 nicht gesetzt, mindestens zwei der drei
  Teilwerte `0x007008B9` / `0x00700C42` / `0x00700E3F` unter 88); er bleibt es, bis die Motivation über 85 steigt.
  Mit Maulwurf: 1701 bei mindestens 7 Spielern mit Trainer-Teilwert unter 90 (einmal je Saison, Merker 0x10000),
  1702 bei mindestens 5 Spielern mit Gesamturteil 3 (Merker 0x20000), sonst die Schlagzeile zum Zählerstand. Die
  Halbzeit-Schlagzeilen 1692–1695, 1697, 1698 verlangen über `0x006493E0` einen Maulwurf unter den 11 + 7 Spielern
  der Aufstellung; ohne ihn erscheint keine (Beobachtung des Nutzers: nie eine gesehen). Eine Grenze je Saison gibt
  es an diesen Stellen nicht.
- **K12:** `0x00700FA2(delta)` ändert Byte Spielstand 0x272 (Teilwert „Presse“, 0–120) und rechnet die Motivation neu
  (`0x0070147E`); die Zeitungsroutine wendet einen Presse-Wert nur mit Spielernummer an (`0x0078A0F5`), die keine der
  sieben Stellen übergibt. Vorbild: 1218 (`0x005FE6D9`). Alle vier Routinen (`0x005FB264`, `0x005FD59D`, `0x005E08F1`,
  die Routine um `0x005E5BDD`) enden mit `mov esp,ebp`; deshalb dürfen die `add esp` nach den Aufrufen entfallen.
  Stellen und Spielerzeiger: 1125 `0x005FB535` [ebp+0Ch]; 1188 `0x005FDF80`, 1197 `0x005FE0E9`, 1201 `0x005FE290`
  je [ebp+8]; 1269 `0x005E0F36`, 1528 `0x005E5C07`, 1530 `0x005E5D2D` je [ebp+10h].
  Text 1197 betrifft einen Spieler (%1 Spielername, %2 Vereinsname im Genitiv); die ähnlich klingende Meldung über
  einen Schiedsrichter ist Text 730 (Frage des Nutzers, 17.11.2026).
- **K13:** Die Routine `0x005378D6` ist die Funktion „Presse nutzen“ (einmal je Saison, Merker 0x800 in Manager
  +0x17DC, Dialogtext 4288; verlangt `0x006A5A7D` ≥ 80). Auswahl 0 macht die Ausstiegsklausel bekannt und wendet
  `0x0041849A(0, −5, 0, −10)` direkt an; Auswahl 1 → Schlagzeile 1743 mit +5, Auswahl 2 → 1744 mit −10, je mit
  Managernummer (word Manager +0x1A), aber Kennzeichen 8 statt `0x40000008`; Auswahl 3 → 1745–1747 mit richtigem
  Kennzeichen `0x20000400`. Bit 3 = vierter Wert von `0x0041849A` = Wort Manager +0x9C; das ist die Grundlage von
  `0x007701B2`, angezeigt im Hauptmenü als Prozentwert im Feld `IDC_HAUPTMENUE_VERTRAUEN` (`0x004C4582`, Format
  „%d%%“): das Vertrauen des Vorstands. Damit ist auch der in Befund 6.13 offene „vierte Wert“ geklärt. Angewendet
  wird der Wert wie bei allen Zeitungswerten nur, wenn die Schlagzeile die oberste des Tages wird.
- **K14 und K15:** `0x00702467` („Beziehung beenden“, neun Aufrufer, u. a. Text 1079 bei `0x005F9816`) setzt den
  Status auf „keine Beziehung“, macht die Partnerin zur früheren Partnerin (Byte 0x263 bleibt stehen, 0x265 ← 0x263),
  leert die Kinderliste, streicht den Hochzeitstermin mit dem gespeicherten Datum aus der Terminliste `0x008EB8B0`
  (`0x004377B7(Nr, Satz +0x170)`) und löscht das Datum. Der Hochzeitstermin entsteht in `0x00702AC7` (Datum in etwa 90
  Tagen nach Satz +0x170 und in die Terminliste); am Termin ruft `0x005FD386` `0x00702B15` (Status verheiratet, Termin
  gestrichen). Bei 1093 bleibt die vorher gesetzte Krisenstufe 3 im Satz stehen (ohne Beziehung wird sie nicht
  ausgewertet; „neue Freundin“ `0x00702571` setzt sie zurück). 1083 verlangt Status „Freundin“, keine Kinder und
  Krisenstufe 0.
- **K16:** Bei 1104 ist p = [ebp+0Ch] der gewählte Spieler (Status „Freundin“, Teilwert 0x273 unter 95, Krisenstufe 0,
  Bit 24 nicht gesetzt), q = [ebp-8] ein Spieler ohne Beziehung (`0x005FA981`). q beendet seine Beziehung, übernimmt
  die Partnerin von p (`0x00702668`), p beendet seine (`0x00702467`); beide bekommen +3 auf Teilwert 0x273. Die
  Meldung `0x00601043` setzt immer %1 = Name des übergebenen Spielers; nach der Korrektur wird q übergeben und p als
  %2, die angezeigten Vorher/Nachher-Werte sind die von q.
- **K17:** Beide Fälle verlangen Status „Freundin“, Beginn der Beziehung vor weniger als 365 Tagen (`0x006FFC0A`),
  eine frühere Partnerin (`0x006FFBBD`) und Krisenstufe 0; 1109 zusätzlich, dass Bit 25 im Flagwort nicht gesetzt ist
  (`0x007028D7`). Den Setzer dieses Bits (`0x007028F9`) ruft im Original niemand auf; gelöscht wird es zusammen mit
  Bit 24 beim Ende einer Beziehung (`0x00702467`, Maske `0xFCFFFFF3`) – es ist also ein Merker je Beziehung, und 1109
  („… nimmt sich vor, künftig nur noch Schatzi zu sagen“) ist die einzige Stelle, die ihn prüft (Schluss: 1109 sollte
  ihn setzen, damit die Meldung je Beziehung einmal kommt). `0x00702762` (einziger Aufrufer bisher bei 1109) merkt
  sich die frühere Partnerin, ruft `0x00702467`, trägt die frühere Partnerin als Partnerin ein und ließ den Status auf
  „keine Beziehung“. Neu: 1109 setzt nur den Merker; 1110 („… ist auf dem Weg zu ihr“) ruft nach der Meldung
  `0x00702762`, das am Ende den Status „Freundin“ setzt (`0x00702BB0(1)`).
- **K18 (zurückgelegt, nachgelesen 18.11.2026):** Fall 1 von `0x005FB264` (`0x005FB2F5`) verlangt Byte Spieler +2
  genau gleich 1 (`0x005FB2FD`: `cmp edx,1` / `jne`), Status „verheiratet“ und genau ein Kind; die Vorroutine
  `0x005FB634` lässt nur verheiratete Spieler mit Geliebter zu. Byte Spieler +2 ist die Spielstärke (Setzer
  `0x006A7CFE`, begrenzt 1–12, und `0x006A7E6B`, beide mit Meldung an den Manager). Die Meldung trifft also nur
  Spieler der Stärke 1, denen kein Punkt mehr abgezogen werden kann. Geändert wird nur Spielstand 0x273 (−40 bis
  −50); als zweiter Name wird die frühere Partnerin gelesen (`0x005FB354`), ohne dass vorher getrennt wurde.
  Die täglichen Ereignisse laufen nur für die bis zu vier Vereine menschlicher Manager (`0x006502A9` holt deren Liste,
  Aufruf `0x0065034E`). Schwesterstellen mit Stärkeverlust verlangen Stärke über 1 und ziehen direkt 1 ab: Text 1163
  (`0x005FD891` `cmp eax,1` / `jle`, `0x005FD89C` `sub dl,1`) und Text 367 (`0x00604FA8` / `0x00604FF9`). Der Text
  enthält „%s“ statt „%1“/„%2“ und erscheint deshalb wörtlich mit „%s“ (Abschnitt 6.6 des Befunds). Eingetragen
  nach Freigabe: Block `frau-weg-1115` in `tools/asm_nacht.py` (116 von 124 Bytes ab `0x005FB2F5`: Stärke über
  1, Stärke −1, `0x00702467`, Rest wie bisher).
- **K15, Berichtigung 18.11.2026:** Im Umbau stand `push 0` (vierter Wert der Meldung) vor dem Zufallsaufruf, dessen
  Argument wegen des weggelassenen `add esp,4` auf dem Stapel blieb; die Meldung hätte als vierten Wert 10 statt 0
  bekommen (`0x00601043` legt ihn nach `0x00A2F6EC`). Jetzt steht `push 0` nach dem Zufallsaufruf. Alle übrigen Blöcke
  in `tools/asm_nacht.py` und `tools/asm_presse.py` auf dasselbe Muster durchgesehen: kein weiterer Fall (dort bleibt
  ein Rest nur zwischen vollständigen Aufrufen liegen). Die Alpha (`139C1AC8`) enthält K15 nicht.
- **K19:** `0x00705539` (einziger Aufrufer bei 1365): beim aufgerufenen Spieler werden die zwei niedrigsten der drei
  Motivation-Teilwerte (Spielstand 0x26F, 0x270, 0x271), soweit unter 100, je um die Hälfte des Abstands zu 100
  angehoben und beim übergebenen Spieler um denselben Betrag gesenkt. Aufgerufen wird B (der Unzufriedene, Mittel
  unter 85) mit A (Mittel über 100): B klagt und wird zufriedener, A wird unzufriedener. Die Meldung nannte A als %1.
- **K20:** `0x005EC9D8(Verein, X)` zieht einen Mitspieler, der nicht X ist und X nicht als Erzfeind eingetragen hat –
  die Auswahl ist also auf einen Streit mit X (dem Autor) zugeschnitten. Eingetragen wurde `A.0x00703DF4(B)`; neu
  `Autor.0x00703DF4(A)` und `Autor.0x00703DF4(B)` (jeweils gegenseitiger Eintrag in die Streit-Liste, Freundschaft der
  beiden gelöst).
- **K21–K27 (Verletzungen):** `0x00766B92(Spieler, Art, Dauer)` nimmt bei Dauer ≤ 0 die Vorgabe der Tabelle
  `0x008AC340` (10 Bytes je Art, Byte +1 = Tage), sonst die übergebene Dauer in Tagen. Zeilen: Art 10 = 35 Tage, Art
  37 = 112, Art 90 = 7, Art 91 = 14; die Zeilen der Arten 92 und 93 sind leer (alle zehn Bytes 0). Die übrigen Felder
  der Tabelle (+0, +2 bis +6, +8) werden an rund dreißig Stellen des Verletzungsmoduls (`0x00766A15`–`0x00767857`,
  `0x005D7386` ff.) gelesen; was eine Verletzung mit leerer Zeile dort bewirkt, ist nicht gelesen – deshalb sind K23
  und K24 zurückgelegt. `0x00766AF9(Spieler, n)` setzt nur Byte Spieler +0x2F („angeschlagen“).
- **K23 / K24, nachgelesen 18.11.2026:** Die Arten 92 und 93 sind vorgesehene Arten, nur ihre Tabellenzeilen fehlen.
  Belege: Das Feld der Verletzungsnamen `0x01C57B98` hat 95 Plätze (`0x00766945`), gefüllt werden die Arten 0–93
  (`0x006862D0`: Schleife bis 94) aus der Nummerntabelle `0x008A8758`; dort stehen für 90–93 die Oberflächentexte 3988
  „Hand verstaucht“, 3989 „Hautausschlag“, 3990 „Stickstoffvergiftung“, 3991 „Autounfall“ (94 hat keinen). Die
  Tabelle `0x008AC340` belegt 950 Bytes (95 Zeilen, danach beginnt bei `0x008AC6F8` das nächste Objekt); die Zeilen
  70–91 der „sonstigen“ Arten haben alle das Muster `00 tt 02 00 07 00 …` (tt = Tage; 90: 7, 91: 14), 92–94 sind Nullen.
  Felder: +0 Ja/Nein-Angabe im Text der Routine `0x0076696E` (Texte 1028/1029) und Vergleich in `0x005D7386`, +1 Tage,
  +2 und +4 liefert `0x00766AB6`, +8 Maske (nur 65/66). Plan: die Zeilen 92 und 93 wie 90/91 füllen (Datei-Offsets
  `0x4AC6D8` und `0x4AC6E2`, je fünf Bytes `00 07 02 00 07` und `00 0E 02 00 07`), die Aufrufe bleiben unverändert.
- **K28:** `0x005E5F40(n)` ändert Wort Spieler +0x18 um n × 100 (begrenzt 0–10000) = Frische in Punkten; 29 Aufrufer,
  bei Text 1329 („verliert fünf Frischepunkte“) mit −5 (`0x005E2303`). Der Fall zu 1180 (`0x005FDD89`: Zufall 0–1, 0 →
  Meldung 1180) rief sie nicht auf.
- **K30 / K31, nachgelesen 18.11.2026:** Zähler = Byte Spielstand 0x26E (`0x00C027DE + Nr × 0x354`); einziger Schreiber
  `0x00702D31(v)` (v ≥ 0 schreibt, v < 0 liest nur), dazu der Leser `0x00702D6F` („Führerschein da?“, Aufrufer
  `0x005FE9B4`, `0x005FEB2E`); kein weiterer Zugriff auf die Adresse. Alle zwölf Aufrufer von `0x00702D31` übergeben −1,
  1, 2 oder 6 und prüfen von der Rückgabe nur null / nicht null bzw. größer null (`0x005FC882`). Der Fall `0x005FC873`
  (Text 1237 „… der zur Zeit ja keinen Führerschein …“, Teilwert 0x273 −3) verlangt einen Wert über 0.
  Mitzählen scheidet aus: Die Tagesroutine `0x0064F981` ruft die täglichen Ereignisse je Verein nur mit 2 von 3
  (`0x0064FA8A`) und in 1 von 20 Fällen gar nicht (`0x0064F9B6`), dabei entfällt auch die Monatsroutine `0x007489CB`
  (`0x0064FA47`). Lösung (eingetragen nach Freigabe, Block `fuehrerschein-zaehler` in `tools/asm_nacht.py`, 87
  von 100 Bytes ab `0x00702D31`): Das Byte hält statt der Restmonate den Ablaufmonat E = (Jahr × 12 + Monat + v) & 0xFF
  (heutiges Datum: Wörter `0x00B5CBDE` Jahr, `0x00B5CBDC` Monat, wie in `0x0067582A`); 0 = Führerschein da. Jedes
  Lesen prüft (E − heute) & 0xFF: 0 bis 7 = noch entzogen, sonst abgelaufen → Byte wird gelöscht. Der Leser zieht
  nach `0x00702D7B`, seine zwei Aufrufer werden umgeleitet (`E8C2431000`, `E848421000`). Dauer: Rest des laufenden
  Monats plus v volle Monate. Alte Spielstände (Werte 1, 2, 6) gelten beim ersten Lesen als abgelaufen. Dazu K30:
  `0x1FE6A6` `02` → `01`.
- **K32 / K38, nachgelesen 18.11.2026:** Byte Spielstand 0x260 (`0x00C027D0 + Nr × 0x354`), alle Zugriffe: Bits 0–1
  Gruppennummer (`0x0070060A` lesen, `0x0070062E` setzen), Bit 4 Anführer (`0x007006C4` lesen, `0x007006E8` setzen,
  `0x0070071C` löschen; `0x00700690` löscht Bits 0, 1 und 4), Bits 3–4 Schüler-Merker (`0x007064C9` = 2?,
  `0x007064F6` = 3?, `0x00706523` lesen, `0x0070654A` setzen). Schüler-Merker: 0 = noch kein Lehrer, 1 = Lehrer hasst
  Fußball (1563), 2 = Lehrer ist Fan (1564; verhindert 1561/1562), 3 = Schule beendet (schließt die Vorroutine
  `0x005F9DD0` aus, wird nie gesetzt). Wert 2 ist dasselbe Bit wie „Anführer“. Bits 2 und 5–7 benutzt keine Routine;
  in den Spielständen save383 und save109 haben alle 17000 Spieler dort 0 (Werte des Bytes: 0 und 8). Lösung
  (eingetragen nach Freigabe): Schüler-Merker auf die Bits 5–6 verlegen – fünf Bytes: `0x3064E6`, `0x306513`, `0x306542`
  je `03` → `05` (Schiebezahl beim Lesen), `0x306567` `E7` → `9F` (Löschmaske), `0x306591` `03` → `05` (Schiebezahl beim
  Setzen); dazu Block `abitur-1565` in `tools/asm_nacht.py` (48 von 51 Bytes ab `0x005F9D1F`: Merker 3 vor der
  Meldung). Alte Spielstände: vorhandene Schüler-Merker (Bit 3/4) werden nicht mehr gelesen, die Schüler beginnen bei
  0; ein dort schon fälschlich gesetztes Anführer-Bit bleibt stehen.
- **K33:** Der Spitzel des Managers ist Bit 15 (0x8000) im Flagwort des Spielers (lesen `0x007001ED`, setzen/löschen
  `0x0070020F(an)`, Aufrufer `0x0048FC80`, `0x0048FD30`, `0x0048FDD0`, `0x007074FB`) – ein anderer Merker als der
  Maulwurf (Bit 16). **Berichtigung:** der Hinweis „auch für K33“ beim Eintrag zur Maulwurf-Affäre war falsch. Der
  Fall zu 983 zieht allen Kaderspielern 10 Punkte Trainer-Teilwert ab, setzt beim Spitzel Bit 0x20000 und den
  Mannschafts-Teilwert auf 0; neu löscht er zusätzlich Bit 0x8000.
- **K34:** Einziger Aufrufer von `0x005FB264` ist `0x005FB634` (Los-Nummer im Verteiler `0x005EFADA`, Aufruf
  `0x005EFB69`), der die Rückgabe durchreicht. Bei Rückgabe ≠ 0 kehrt der Verteiler `0x005EF8CC` sofort mit 1 zurück;
  bei 0 läuft er weiter nach `0x005EFE1B` (weitere Zufallsereignisse dieses Tages, u. a. `0x005E20FD`), und liefert
  auch er 0, ruft `0x005EF842` bei einem menschlichen Manager zusätzlich die Vereins- und Manager-Ereignisse
  `0x005F0133`. Nach Meldung 1982 konnte am selben Tag also ein zweites Ereignis folgen; mit Rückgabe 1 nicht mehr.
- **K40 (1176 / 1177):** Der Fall verlangt Hobby-Kennung Byte Spieler +0x24 = 14, Bit 24 im Flagwort (`0x00701AC4`;
  gesetzt bei `0x00701A87`, gelöscht, wenn ein Kind eingetragen wird (`0x00701AE6`) oder die Beziehung endet
  (`0x00702467`) – es gibt also eine Partnerin) und `0x00702359` = 0. Ohne Kind (`0x006FFD8A` = 0) kommt 1176, sonst
  1177; als %2 wurde 0 übergeben.
- **K41:** `0x0070282A` beendet die Beziehung (`0x00702467`), macht die Geliebte zur Partnerin (Byte 0x263 ← 0x264),
  setzt ein neues Datum, Status „Freundin“, Krisenstufe 0, streicht den Hochzeitstermin und löscht Byte 0x264. Bei
  1094 werden die Namen erst danach gelesen: %2 = frühere Partnerin (`0x0070185C`, richtig), %3 = `0x007017DB` mit
  Index 0 (falsch). `0x006012DF` setzt als %1 immer den Spielernamen; der Text beginnt aber mit „%1, die Freundin von
  %2“.
- **K49 und K35 (zurückgelegt):** 1207 liegt im Übergewicht-Fall (`0x005FE310`: Zufall 0–5, Sprungtabelle
  `0x005FECE4`), setzt Bit 5 im Flagwort (`0x006FFF76(1)`) und zeigt die Meldung ohne jede Prüfung. Der
  Konditionsbonus ist Bit 13 im Flagwort (`0x007000E3` lesen, `0x00700105` setzen/löschen), der Raucher-Abzug Bit 11
  (`0x006FFFD9`).

## Entwürfe für Changelog und „Details“ (K01–K10)
Vom Nutzer am 17.11.2026 gewünscht: je freigegebenem Punkt gleich mitschreiben. Form wie in `tools/patch_bauen.py`
(Titel, Fehler, Korrektur, Auswirkung); beim Anpassen des Installers übernehmen und dabei prüfen. Gruppe in Klammern.

**K01 `hochzeit-platzt` (Spiellogik, kleine Auswirkung)**
- Titel: Ereignis „Hochzeit platzt“ traf nicht den Spieler mit Hochzeitstermin
- Fehler: Das Ereignis sucht im Kader die Spieler mit einem Hochzeitstermin, verwendete dann aber nicht einen dieser
  Spieler, sondern den Speicherplatz hinter dem letzten Kaderspieler. Dort steht je nach Verlauf ein früherer
  Kaderspieler oder kein gültiger Eintrag; die Meldung konnte einen Spieler ohne Hochzeitstermin treffen oder das
  Programm zum Absturz bringen.
- Korrektur: Unter den Spielern mit Hochzeitstermin wird einer zufällig gewählt, wie es die übrigen Ereignisse
  dieser Gruppe tun.
- Auswirkung: Die Meldungen „Hochzeit abgesagt“ und „Freundin entdeckt die andere Freundin“ betreffen den richtigen
  Spieler. Häufigkeit und Bedingungen des Ereignisses sind unverändert.

**K02 `frauen-namen-1363` (rein optisch)**
- Titel: Meldung über zwei befreundete Spieler nannte die Namen der Ehefrauen nicht
- Fehler: In der Meldung „… Da auch ihre Frauen … sehr viel zusammen machen …“ wurde anstelle des ersten Namens ein
  nicht belegter Speicherbereich ausgegeben, der zweite Name fehlte.
- Korrektur: Es werden die Namen der beiden Ehefrauen eingesetzt.
- Auswirkung: Nur der Text der Meldung. Das Ereignis setzt unverändert voraus, dass beide Spieler verheiratet sind.

**K03 `zeitung-1880` (rein optisch)**
- Titel: Schlagzeile zum Tod eines gedopten Spielers griff auf ungültige Managerdaten zu
- Fehler: Beim Anlegen der Schlagzeile „Trauer in … – … stirbt vollgepumpt mit Drogen an Herzversagen“ fehlte eine
  Angabe; der Wert −5 wurde als Managernummer gespeichert. Wurde die Schlagzeile die oberste des Tages, griff das
  Programm damit auf Daten außerhalb der Managertabellen zu.
- Korrektur: Die Schlagzeile wird ohne Managernummer angelegt; der fehlerhafte Zugriff entfällt.
- Auswirkung: Die Schlagzeile erscheint wie bisher. Es wird kein Wert verändert.

**K04 `zeitung-1750` (rein optisch)**
- Titel: Schlagzeile „… hat die Schnauze voll“ speicherte einen zufälligen Wert
- Fehler: Die Schlagzeile kündigte einen Wert an, der beim Anlegen nicht übergeben wurde; gespeichert wurde ein
  zufälliger Speicherinhalt. Der Wert wurde weder angezeigt noch angewendet.
- Korrektur: Die Schlagzeile wird ohne Wert angelegt.
- Auswirkung: Keine sichtbare Änderung.

**K05 `geld-690` (Spiellogik, kleine Auswirkung)**
- Titel: Ereignis „Kostenloser Kopierer“: Ersparnis wurde als Ausgabe gebucht
- Fehler: Die Meldung nennt eine Ersparnis von 12 000, gebucht wurde eine Ausgabe in dieser Höhe.
- Korrektur: Der Betrag wird als Einnahme gebucht.
- Auswirkung: 12 000 Einnahme statt 12 000 Ausgabe je Auftreten. Das Ereignis ist eines von 108 zufälligen
  Geld-Ereignissen und kann sich im Lauf der Jahre wiederholen.

**K06 `geld-697` (Spiellogik, kleine Auswirkung)**
- Titel: Ereignis „Preisausschreiben“: Kosten wurden als Einnahme gebucht
- Fehler: Die Meldung nennt Kosten von 8 000, gebucht wurde eine Einnahme in dieser Höhe.
- Korrektur: Der Betrag wird als Ausgabe gebucht.
- Auswirkung: 8 000 Ausgabe statt 8 000 Einnahme je Auftreten; sonst wie K05.

**K07 `verhandlung-224` (Spiellogik, kleine Auswirkung)**
- Titel: Sponsorenangebot des Schokoladenherstellers: erfolgreiche Verhandlung brachte nicht den höheren Betrag
- Fehler: Die Frage stellt bei erfolgreicher Verhandlung den doppelten Betrag in Aussicht (Chance 50 : 50, bei
  Misserfolg kein Vertrag). Bei Erfolg wurde nur der einfache Betrag gutgeschrieben, derselbe wie ohne Verhandlung.
- Korrektur: Bei Erfolg wird der in der Frage genannte doppelte Betrag gutgeschrieben.
- Auswirkung: 300 000 statt 150 000 bei erfolgreicher Verhandlung (in unteren Ligen 150 000 statt 75 000). Annehmen
  ohne Verhandlung und der Misserfolg sind unverändert.

**K08 `randale-284` (rein optisch)**
- Titel: Randale nach einem Heimspiel: Entwarnung trotz Schadenersatz
- Fehler: Im ungünstigen Verlauf werden 100 000 Schadenersatz gebucht; angezeigt wurde dennoch der Text des
  günstigen Verlaufs („… schnell unter Kontrolle gebracht“).
- Korrektur: Es wird der zugehörige Text angezeigt („… auf mehr als 500 000 verklagt … auf 100 000 einigen“), mit
  beiden Beträgen.
- Auswirkung: Nur der Text der Meldung. Buchung und Wahrscheinlichkeit der beiden Verläufe sind unverändert.

**K09 `straf-frage-stufe1` (Spiellogik, kleine Auswirkung)**
- Titel: Straf-Frage, mildeste Stufe: Antworten und Wirkung passten nicht zusammen
- Fehler: Bei den Antworten „1 Spiel interne Sperre“, „… Strafe“ und „Nicht so schlimm“ wurde ausgewertet: keine
  Sperre und 10 Punkte Abzug beim Trainer-Teilwert der Motivation; keine Geldstrafe und 2 Punkte Abzug; Geldstrafe.
  Die beiden strengeren Stufen der Frage werten ihre Antworten richtig aus.
- Korrektur: Die Auswertung folgt den Antworten, mit den Werten der nächsten Stufe für dieselbe Antwort: Sperre für
  ein Spiel und 3 Punkte Abzug; Geldstrafe ohne Abzug; keine Folge.
- Auswirkung: Betrifft jede Straf-Frage der mildesten Stufe. Die Bewertung der Strenge des Managers ist unverändert.

**K10 `streit-liste` (Spiellogik, kleine Auswirkung)**
- Titel: Ende eines Streits löschte einen Freund aus der Freundesliste
- Fehler: Jeder Spieler führt eine Liste von bis zu drei Freunden und eine von bis zu drei Spielern, mit denen er
  Streit hat. Beim Streichen aus der Streit-Liste wurde der dritte Platz der Freundesliste gelöscht; der dritte
  Platz der Streit-Liste blieb stehen, bei voller Liste stand ein Spieler danach doppelt darin.
- Korrektur: Der Platz wird in der Streit-Liste gelöscht.
- Auswirkung: Die Listen erscheinen im Spielerdialog und bestimmen, welche Spieler für die Ereignisse zwischen zwei
  Spielern in Frage kommen; beide stimmen nach einem beendeten Streit wieder.

**K11 `maulwurf-zaehler` (Spiellogik, kleine Auswirkung)**
- Titel: Maulwurf-Affäre konnte in derselben Saison von vorn beginnen
- Fehler: Das Spiel zählt je Saison die Schlagzeilen der Maulwurf-Affäre und lässt je nach Stand weitere folgen. Der
  Zähler fasst die Werte 0 bis 7, wurde aber erst bei 15 begrenzt; bei der achten Erhöhung sprang er auf 0, und die
  Folge-Schlagzeilen konnten ein zweites Mal erscheinen.
- Korrektur: Der Zähler bleibt bei 7 stehen.
- Auswirkung: Nur in Saisons mit mindestens acht Schlagzeilen der Affäre. Die Affäre setzt einen Spieler mit
  Gesamtmotivation unter 70 voraus, der als Maulwurf bestimmt wurde; ohne ihn tritt sie nicht auf.

**K12 `presse-1125`, `presse-1188`, `presse-1197`, `presse-1201`, `presse-1269`, `presse-1528`, `presse-1530`
(Spiellogik, kleine Auswirkung; ein gemeinsamer Eintrag)**
- Titel: Sieben Zeitungsmeldungen: vorgesehener Abzug beim Teilwert „Presse“ wurde nie angewendet
- Fehler: Die Schlagzeilen „Frau von … bei Banküberfall erwischt“, „Schönheitsoperation bei …“, „… steht vor dem
  Nichts“, „… geht lieber Golfen“, „… pöbelt friedliche Passanten an“, „… mit schweren Vorwürfen gegen den Trainer“
  und „… kritisiert Trainer …“ geben einen Abzug von 2 bis 4 Punkten beim Teilwert „Presse“ der Motivation des
  Spielers mit. Angewendet wurde er nie, weil die Angabe des Spielers fehlte; die übrigen Schlagzeilen derselben
  Ereignisgruppen wenden ihren Abzug an.
- Korrektur: Der Abzug wird beim betroffenen Spieler angewendet.
- Auswirkung: Je Schlagzeile sinkt der Teilwert „Presse“ eines Spielers um 2 bis 4 Punkte (Skala 0 bis 120); das
  entspricht etwa 0,3 bis 0,7 Punkten der Gesamtmotivation. Häufigkeit und Bedingungen der Meldungen sind
  unverändert.

**K13 `presse-nutzen-vertrauen` (Spiellogik, kleine Auswirkung)**
- Titel: „Presse nutzen“: Artikel über den Manager änderte das Vertrauen des Vorstands nicht
- Fehler: Lässt der Manager über die Presse einen lobenden Artikel über sich schreiben oder kritisiert er den
  Vorstand, gibt die Schlagzeile eine Änderung des Vertrauens mit (+5 beziehungsweise −10 Punkte). Wegen einer
  fehlenden Kennzeichnung wurde sie nie angewendet.
- Korrektur: Die Kennzeichnung ist ergänzt; die Änderung wird angewendet, wenn die Schlagzeile die oberste des Tages
  ist, wie bei den übrigen Schlagzeilen dieser Funktion.
- Auswirkung: Das im Hauptmenü angezeigte Vertrauen ändert sich um +5 beziehungsweise −10 Punkte. Die Funktion steht
  unverändert einmal je Saison und nur bei hoher Beliebtheit bei den Medien zur Verfügung.

**K14 `hochzeit-absage-1093` (Spiellogik, kleine Auswirkung)**
- Titel: Abgesagte Hochzeit fand trotzdem statt
- Fehler: Die Meldung „… muß seine Hochzeit … absagen … Die beiden Frauen wollen nichts mehr von ihm wissen“ strich
  den Hochzeitstermin mit einem unbestimmten Datum; der Termin blieb bestehen, der Spieler heiratete am vorgesehenen
  Tag und behielt seine Freundin.
- Korrektur: Die Beziehung wird beendet, wie es das Spiel bei den übrigen Trennungen tut; der Hochzeitstermin entfällt
  damit.
- Auswirkung: Der Spieler ist nach der Meldung ohne Beziehung. Häufigkeit und Bedingungen des Ereignisses sind
  unverändert.

**K15 `trennung-1083` (Spiellogik, kleine Auswirkung)**
- Titel: Meldung „Es kommt zur Trennung“: Beziehung blieb bestehen
- Fehler: Will die Freundin eines Spielers nicht mit in die neue Stadt ziehen, meldet das Spiel die Trennung; die
  Beziehung wurde aber nicht beendet, nur ein Teilwert der Motivation gesenkt.
- Korrektur: Die Beziehung wird beendet, wie bei der gleich gebauten Meldung über eine Trennung.
- Auswirkung: Der Spieler ist nach der Meldung ohne Beziehung; der Abzug bei der Motivation ist unverändert.

**K16 `freundin-ausgespannt-1104` (rein optisch)**
- Titel: Meldung „… hat … die Freundin ausgespannt“ nannte die Spieler vertauscht
- Fehler: Die Meldung nannte den Spieler, der seine Freundin verliert, als denjenigen, der sie ausgespannt hat, und
  umgekehrt.
- Korrektur: Die Namen stehen in der richtigen Reihenfolge; die angezeigte Änderung des Teilwerts gehört zum
  erstgenannten Spieler.
- Auswirkung: Nur der Text und die Anzeige der Meldung. Die Wirkung (beide Spieler +3, Wechsel der Partnerin) ist
  unverändert.

**K17 `ex-freundin-1109-1110` (Spiellogik, kleine Auswirkung)**
- Titel: Meldungen zur Ex-Freundin: Wirkungen waren vertauscht
- Fehler: Bei der Meldung, der Spieler spreche seine Freundin mit dem Namen der Ex-Freundin an, wechselte er zur
  Ex-Freundin zurück und galt danach als Spieler ohne Beziehung; die Namen in der Meldung waren dadurch vertauscht.
  Bei der Meldung, er sei auf dem Weg zu seiner Ex-Freundin, änderte sich nichts.
- Korrektur: Die erste Meldung ändert die Beziehung nicht mehr und erscheint je Beziehung einmal; bei der zweiten
  kehrt der Spieler zu seiner früheren Partnerin zurück und hat danach den Status „Freundin“.
- Auswirkung: Betrifft Spieler mit Freundin und früherer Partnerin im ersten Jahr der Beziehung. Häufigkeit der
  Auslosung unverändert.

**K18 `frau-weg-1115` (Spiellogik, kleine Auswirkung; zusammen mit der Textkorrektur)**
- Titel: Meldung „… die Frau von … ist zusammen mit dem gemeinsamen Kind zu ihrem neuen Freund gezogen“ ohne Wirkung
- Fehler: Die Meldung konnte nur bei Spielern der Stärke 1 erscheinen, zeigte „%s“ statt der Namen, und weder die
  Trennung noch der genannte Verlust eines Stärkepunkts fanden statt.
- Korrektur: Die Meldung trifft Spieler mit einer Stärke über 1, wie die übrigen Meldungen mit Stärkeverlust. Der
  Spieler verliert einen Stärkepunkt, die Ehe endet, die Namen erscheinen.
- Auswirkung: Betrifft nur Spieler der eigenen Mannschaft, die verheiratet sind, eine Affäre und genau ein Kind
  haben. Der Verlust des Stärkepunkts ist dauerhaft.

**K19 `freund-klagt-1365` (rein optisch)**
- Titel: Meldung über die Klage eines Spielers bei seinem Freund nannte die Spieler vertauscht
- Fehler: In der Meldung „… erzählt ihm, was ihm zur Zeit bei diesem Verein alles stinkt. … muß ihm in einigen Punkten
  recht geben“ stand der zufriedene Spieler als der klagende und umgekehrt.
- Korrektur: Die Namen stehen in der richtigen Reihenfolge.
- Auswirkung: Nur der Text der Meldung; die Wirkung auf die Motivation beider Spieler ist unverändert.

**K20 `autobiographie-1172` (Spiellogik, kleine Auswirkung)**
- Titel: Autobiographie eines Spielers: Streit entstand zwischen den Falschen
- Fehler: Nach der Meldung „… %2 und %3 mögen ihn jedenfalls jetzt nicht mehr“ wurde ein Streit zwischen den beiden
  genannten Mitspielern eingetragen, nicht zwischen ihnen und dem Autor.
- Korrektur: Der Streit wird zwischen dem Autor und jedem der beiden Mitspieler eingetragen.
- Auswirkung: Betrifft die Streit-Listen der drei Spieler (Anzeige im Spielerdialog, Auswahl für spätere Ereignisse
  zwischen Spielern).

**K21 `dauer-1193`, K22 `dauer-1215`, K25 `dauer-1076` (Spiellogik, kleine Auswirkung; ein gemeinsamer Eintrag)**
- Titel: Drei Verletzungsmeldungen: Ausfalldauer entsprach nicht der Meldung
- Fehler: Bei „Spaten in den Fuß … fällt drei Wochen aus“ fiel der Spieler 112 Tage aus, bei „Hand verstaucht … die
  nächsten drei Wochen“ 7 Tage und bei „Bänderriß … fällt vier Wochen aus“ 35 Tage, weil jeweils die Vorgabedauer der
  Verletzungsart statt der genannten Dauer galt.
- Korrektur: Die Dauer wird ausdrücklich gesetzt: 21, 21 und 28 Tage.
- Auswirkung: Der Ausfall dauert so lange, wie die Meldung angibt. Häufigkeit der Ereignisse unverändert.

**K23, K24 `verletzung-92-93` (Spiellogik, kleine Auswirkung; ein gemeinsamer Eintrag)**
- Titel: Stickstoffvergiftung und Autounfall: Spieler fiel nicht aus
- Fehler: Nach den Meldungen „… kann daher die nächste Woche nicht trainieren“ und „… fällt damit zwei Wochen aus“
  fiel der Spieler keinen Tag aus, weil für diese beiden Verletzungsarten keine Dauer hinterlegt war; eine laufende
  Verletzung wurde dabei sogar beendet.
- Korrektur: Für beide Arten ist die Dauer hinterlegt: 7 und 14 Tage.
- Auswirkung: Der Spieler fällt so lange aus, wie die Meldung angibt. Häufigkeit der Ereignisse unverändert.

**K28 `frische-1180` (Spiellogik, kleine Auswirkung)**
- Titel: Meldung „… verliert einen Frischepunkt“ ohne Wirkung
- Fehler: Die Meldung über den müden Football-Fan kündigt den Verlust eines Frischepunkts an; abgezogen wurde nichts.
- Korrektur: Der Spieler verliert einen Frischepunkt.
- Auswirkung: Ein Frischepunkt bei einem Spieler je Meldung.

**K30, K31 `fuehrerschein` (Spiellogik, kleine Auswirkung; ein gemeinsamer Eintrag)**
- Titel: Entzogener Führerschein kam nie zurück
- Fehler: Die Dauer des Entzugs wurde gespeichert, aber nie heruntergezählt. Ein Spieler, der den Führerschein einmal
  verloren hatte, bekam ihn nicht wieder: Die Führerschein-Meldungen konnten ihn nie mehr treffen, die Meldung über
  den Spieler ohne Führerschein dagegen immer wieder. Zusätzlich speicherte eine Meldung „für einen Monat“ zwei Monate.
- Korrektur: Gespeichert wird der Monat, in dem der Entzug endet; danach hat der Spieler den Führerschein wieder.
- Auswirkung: Der Entzug dauert den Rest des laufenden Monats und die genannten vollen Monate. In bestehenden
  Spielständen erhalten Spieler ohne Führerschein ihn zurück.

**K32, K38 `schueler-merker` (Spiellogik, kleine Auswirkung; ein gemeinsamer Eintrag)**
- Titel: Schüler und Anführer einer Gruppe teilten sich einen Merker; Abitur mehrfach bestanden
- Fehler: Der Merker für Spieler, die noch zur Schule gehen, und der Merker „Anführer einer Gruppe“ benutzten dasselbe
  Bit. Ein Schüler mit einem wohlgesinnten Klassenlehrer galt dadurch als Anführer einer Gruppe und umgekehrt. Nach
  der Meldung über das bestandene Abitur wurde zudem nicht vermerkt, dass die Schule beendet ist; die Meldung und die
  übrigen Schul-Meldungen konnten sich wiederholen.
- Korrektur: Der Schüler-Merker liegt auf eigenen Bits. Nach dem Abitur gilt die Schule als beendet.
- Auswirkung: In bestehenden Spielständen beginnen Schüler ohne Merker; die Meldung über den Klassenlehrer kann bei
  ihnen einmal erneut erscheinen.

**K33 `spitzel-983` (Spiellogik, kleine Auswirkung)**
- Titel: Enttarnter Spitzel blieb Spitzel
- Fehler: Nach der Meldung, der Spitzel werde dem Manager ab jetzt nichts mehr sagen, blieb der Spieler als Spitzel
  vermerkt; er konnte weiter Verdächtige melden, und die Enttarnung mit ihrem Abzug für den ganzen Kader konnte sich
  wiederholen.
- Korrektur: Der Vermerk wird bei der Enttarnung gelöscht.
- Auswirkung: Der Spieler ist nach der Enttarnung kein Spitzel mehr; der Manager kann einen neuen bestimmen.

**K34 `rueckgabe-1982` (Spiellogik, kleine Auswirkung)**
- Titel: Ereignis „Kein Weihnachtsgeschenk“ meldete sich als nicht eingetreten
- Fehler: Nach der Meldung gab das Ereignis an die Ereignisverteilung zurück, es sei nichts geschehen.
- Korrektur: Es meldet sich wie die übrigen Ereignisse als eingetreten.
- Auswirkung: Betrifft nur die Ereignisverteilung dieses Tages.

**K35 `konditionsbonus` (Spiellogik, kleine Auswirkung)**
- Titel: Konditionsbonus des privaten Trainers wirkte nicht
- Fehler: Engagiert ein Spieler privat einen Trainer, meldet das Spiel einen Konditionsbonus von 5 %. Der Bonus wurde
  beim Spieler vermerkt und angezeigt, aber nie gerechnet.
- Korrektur: Spieler mit privatem Trainer haben fünf Punkte mehr Kondition (höchstens 100), entsprechend dem Abzug von
  fünf Punkten bei Rauchern.
- Auswirkung: Betrifft Anzeige und Berechnung der Kondition dieser Spieler, auch in bestehenden Spielständen.

**K36 `karriereende-1342` (Spiellogik, größere oder nicht bekannte Auswirkung)**
- Titel: Angekündigtes Karriereende fand nicht statt
- Fehler: Nach der Meldung, ein Spieler beende seine Karriere, um sich ganz seiner Computerfirma zu widmen, blieb er im
  Kader.
- Korrektur: Der Spieler scheidet nach der Meldung aus, wie bei den übrigen Meldungen über ein Karriereende.
- Auswirkung: Der Spieler verlässt den Kader endgültig und ohne Ablöse. Betrifft nur Spieler der eigenen Mannschaft,
  deren Firma die letzte Stufe erreicht hat.

**K37 `name-fruehere-partnerin` (rein optisch)**
- Titel: Name der früheren Partnerin konnte falsch sein
- Fehler: Der Name der früheren Partnerin wurde mit der Namensgruppe der jetzigen Partnerin gebildet; gehören beide zu
  verschiedenen Namensgruppen, erschien ein falscher Name.
- Korrektur: Es wird die gespeicherte Namensgruppe der früheren Partnerin verwendet.
- Auswirkung: Nur der angezeigte Name in den Meldungen, die die frühere Partnerin nennen.

**K43 `vorher-1309-1311` (rein optisch)**
- Titel: Drei Meldungen zeigten eine falsche Veränderung des Werts
- Fehler: In den Meldungen über die Trainingskiebitze, die Teenager nach dem Training und den Fehlpaß im Training
  wurde der Wert „vorher“ mit Zu- und Abschlägen des Spielers angezeigt, der Wert „nachher“ ohne. Bei Spielern mit
  einem solchen Zu- oder Abschlag stimmte die angezeigte Veränderung nicht.
- Korrektur: Beide Werte werden gleich gebildet.
- Auswirkung: Nur die Anzeige in der Meldung; die Wirkung selbst war und ist richtig.

**K44 `art-1312`, K45 `art-1116-1117`, K46 `art-1168` (rein optisch; ein gemeinsamer Eintrag)**
- Titel: Vier Meldungen zeigten die Änderung unter der falschen Bezeichnung
- Fehler: Die Meldungen über die Verehrerin und über den Besuch der Schwiegermutter (zwei Meldungen) zeigten die
  Änderung der Ablenkung unter „Mannschaft“ beziehungsweise „Privates“; die Meldung über das veröffentlichte Tagebuch
  zeigte die Änderung der Stimmung unter „Beliebtheit Öffentlichkeit“.
- Korrektur: Die Änderungen stehen unter „Ablenkung“ beziehungsweise „Stimmung“.
- Auswirkung: Nur die Beschriftung in der Meldung; die Werte selbst waren und sind richtig.

**K47 `text-1389` (rein optisch)**
- Titel: Streit zweier Spieler derselben Position: falsche Meldung
- Fehler: Geraten zwei Spieler derselben Position in Streit, erschien die Meldung über zwei Spieler, die sich in
  dieselbe Frau verliebt haben, mit unvollständigen Namen.
- Korrektur: Es erscheint die zugehörige Meldung („… die die gleiche Position spielen, verstehen sich privat nicht
  besonders gut …“).
- Auswirkung: Nur der Text der Meldung; der Streit wird wie bisher eingetragen.

**K40 (Teil) `frau-1176-1177` (rein optisch)**
- Titel: Meldungen zum Namen des Kindes nannten die Frau des Spielers nicht
- Fehler: Die Meldungen „…, die Frau Ihres Spielers … möchte unbedingt, daß ihr erstes (nächstes) Kind ‚Kurt‘ heißen
  soll …“ begannen ohne Namen.
- Korrektur: Der Name der Partnerin wird eingesetzt.
- Auswirkung: Nur der Text der Meldung.

**K40 (Teil) `frau-969` (rein optisch)**
- Titel: Meldung „… Seine Frau … fände diese Idee auch einfach großartig“ ohne Namen
- Fehler: In der Meldung, der Spieler wolle sein nächstes Kind nach dem Manager benennen, fehlte der Name der Ehefrau.
- Korrektur: Der Name wird eingesetzt.
- Auswirkung: Nur der Text der Meldung.

**K41 (Teil) `name-geliebte-1094` (rein optisch)**
- Titel: Meldung zur geplatzten Hochzeit nannte die andere Freundin falsch
- Fehler: Der Name der anderen Freundin wurde erst gelesen, nachdem sie zur Partnerin geworden war; es erschien ein
  falscher Name.
- Korrektur: Es wird der Name der neuen Partnerin eingesetzt.
- Auswirkung: Nur der Text der Meldung; die vertauschte Nennung von Spieler und Freundin am Satzanfang bleibt bis zur
  Korrektur des Textes bestehen.

**F01 `affaere-fliegt-auf` (Spiellogik, größere oder nicht bekannte Auswirkung)**
- Titel: Die Affäre eines verheirateten Spielers konnte nie auffliegen
- Fehler: Nach der Meldung über eine heimliche Affäre sind vier Folgemeldungen vorgesehen, in denen die Ehefrau
  dahinterkommt. Sie setzen einen Vermerk „Affäre läuft“ voraus, der nie gesetzt wurde; die Meldungen kamen deshalb
  nie. In einer von ihnen wäre außerdem der Name der Freundin falsch gewesen, in einer anderen waren die Namen
  vertauscht.
- Korrektur: Der Vermerk wird mit dem Beginn der Affäre gesetzt; die Namen stimmen.
- Auswirkung: Bei verheirateten Spielern der eigenen Mannschaft kann eine neue Affäre auffliegen, mit den vorgesehenen
  Folgen (Abzug bei der Motivation, Ende der Affäre, Ehekrise bis zur Scheidung). Affären aus bestehenden
  Spielständen sind nicht betroffen.

**F06 `ehefrau-ereignisse` (Spiellogik, größere oder nicht bekannte Auswirkung)**
- Titel: Meldungen rund um die Ehefrau eines Spielers kamen praktisch nie
- Fehler: Die Meldungen über die Ehefrau (Besuch der Schwiegermutter, neue Haarfarbe, Banküberfall, Auszug mit dem
  Kind, vergessenes Weihnachtsgeschenk) konnten nur Spieler treffen, die verheiratet sind und zugleich eine Affäre
  haben, obwohl nur eine einzige dieser Meldungen von einer Affäre handelt.
- Korrektur: Für diese Meldungen genügt es, dass der Spieler verheiratet ist.
- Auswirkung: Bei verheirateten Spielern der eigenen Mannschaft erscheint etwa eine dieser Meldungen je Saison; sie
  verändern wie vorgesehen Teilwerte der Motivation.

**F02 `hobby-1178-1179` (Spiellogik, größere oder nicht bekannte Auswirkung)**
- Titel: Zwei Meldungen zu Computerspielen als Hobby kamen nie
- Fehler: Von vier vorgesehenen Meldungen wurden nur zwei ausgelost. Es fehlten die Meldung, die Ehefrau ziehe wegen
  eines Computerspiels zu ihren Eltern, und die Meldung über den Armbruch bei Aufnahmen für ein Computerspiel.
- Korrektur: Alle vier Meldungen werden ausgelost.
- Auswirkung: Die beiden neuen Meldungen wirken wie vorgesehen (Abzug bei der Motivation; drei Wochen Verletzung). Die
  beiden bisherigen Meldungen erscheinen entsprechend seltener.

**F03 `bauverzoegerung-888-889` (Spiellogik, kleine Auswirkung)**
- Titel: Zwei Gründe für eine Bauverzögerung im Stadion kamen nie
- Fehler: Von zwölf vorgesehenen Gründen wurden nur zehn ausgelost; „Fanblockade“ und „schlechtes Wetter“ fehlten.
- Korrektur: Alle zwölf Gründe werden ausgelost.
- Auswirkung: Nur der genannte Grund; Häufigkeit und Dauer der Verzögerungen sind unverändert.

**F04 `handbuch-1173` (Spiellogik, kleine Auswirkung)**
- Titel: Meldung „… veröffentlicht ein Handbuch für Fußballprofis“ kam nie
- Fehler: Von vier vorgesehenen Meldungen wurden nur drei ausgelost.
- Korrektur: Alle vier werden ausgelost.
- Auswirkung: Die neue Meldung hat keine Wirkung; die drei bisherigen erscheinen entsprechend seltener.

**F05 `vermittler-1481` (Spiellogik, größere oder nicht bekannte Auswirkung)**
- Titel: Hinweis vor Vertragsverhandlungen mit jungen Spielern kam nie
- Fehler: Der Hinweis, der Spielervermittler wolle den jungen Spieler noch eine Weile beim Verein lassen, war an eine
  Altersbedingung geknüpft, die an ihrer Stelle nie erfüllt sein konnte.
- Korrektur: Die Bedingung steht an der richtigen Stelle.
- Auswirkung: Junge Stammspieler unter 20 mit Spielervermittler erhalten diesen Hinweis statt der Forderung nach einer
  Ausstiegsklausel.

## Textpaket für `Ereignis.saq` (freigegeben 18.11.2026, rein optisch)

Vom Nutzer am 18.11.2026 als Paket freigegeben; umgesetzt wird es mit dem Installer (Datei entschlüsseln, Texte ersetzen,
neu verschlüsseln; jeder Text nur, wenn der alte Wortlaut genau stimmt; alle übrigen Texte müssen Byte für Byte gleich
bleiben). Text 1115 gehört zu K18 (`frau-weg-1115`) und muss mit ihm zusammen ausgeliefert werden. Die Sätze in 1294
(„Ihr Spieler %1 bricht das Training ab.“) und 1210 („Er gibt sein Hobby daraufhin auf.“) sind neu formuliert.

| Text | Punkt | Alt | Neu |
|---|---|---|---|
| 285 | K48 | Sie haben herausgefunden, daß Ihr Mitspieler %s eine schwarze Kasse führt. Es würde Ihn %s Strafe und 20 Punkte Beliebtheit in der Öffentlichkeit und bei den Medien kosten, wenn Sie den Fall aufdecken. Außerdem wäre sein Präsident sicher nicht begeistert. Wollen Sie? | Sie haben herausgefunden, daß Ihr Mitspieler %s eine schwarze Kasse führt. Es würde Ihn %s Strafe und je 5 Punkte Beliebtheit in der Öffentlichkeit, bei den Fans und bei den Medien kosten, wenn Sie den Fall aufdecken. Außerdem wäre sein Präsident sicher nicht begeistert. Wollen Sie? |
| 888 | F03 | einer Fanblockade  | einer Fanblockade |
| 889 | F03 | wegen schlechtem Wetter | schlechten Wetters |
| 1178 | F02 | Nachdem Frau %2 Ihrem Mann %1 heimlich eine halbe Stunde beim Spielen eines 3D-Shooters zugeschaut hat, beschließt sie für die nächste Zeit erst mal zu ihren Eltern zu ziehen. | Nachdem Frau %2 ihrem Mann %1 heimlich eine halbe Stunde beim Spielen eines 3D-Shooters zugeschaut hat, beschließt sie für die nächste Zeit erst mal zu ihren Eltern zu ziehen. |
| 954 | K39 | Ihr Spieler %s kommt nach dem Training zu Ihnen und meint, daß das eine der besten Trainingseinheiten seines Lebens gewesen sei. | Ihr Spieler %1 kommt nach dem Training zu Ihnen und meint, daß das eine der besten Trainingseinheiten seines Lebens gewesen sei. |
| 1083 | Tippfehler | %2, die Freundin von %1, hat keine Lust, mit Ihrem Freund in eine neue Stadt umzuziehen. %1 ist todunglücklich, hat aber keine andere Wahl. Es kommt zur Trennung. | %2, die Freundin von %1, hat keine Lust, mit ihrem Freund in eine neue Stadt umzuziehen. %1 ist todunglücklich, hat aber keine andere Wahl. Es kommt zur Trennung. |
| 1094 | K41 | %1, die Freundin von %2, entdeckt in der Jackentasche Ihres Freundes die Telefonnummer seiner anderen Freundin %3. Zusammen mit dem fremdem Lippenstift auf dem Kragen genügt das. Sie packt ihre Sachen. Die Hochzeit hat sich natürlich auch erledigt. | %2, die Freundin von %1, entdeckt in der Jackentasche ihres Freundes die Telefonnummer seiner anderen Freundin %3. Zusammen mit dem fremdem Lippenstift auf dem Kragen genügt das. Sie packt ihre Sachen. Die Hochzeit hat sich natürlich auch erledigt. |
| 1115 | K39 / K18 | %s, die Frau von %s ist zusammen mit dem gemeinsamen Kind zu ihrem neuen Freund gezogen. Er ist völlig geknickt, beginnt zu trinken und verliert einen Punkt seiner Spielstärke. | %2, die Frau von %1, ist zusammen mit dem gemeinsamen Kind zu ihrem neuen Freund gezogen. Er ist völlig geknickt, beginnt zu trinken und verliert einen Punkt seiner Spielstärke. |
| 1116 | K39 | Die Schwiegermutter Ihres Spielers %s ist nach einem längeren Besuch endlich wieder ausgezogen. Er fühlt sich gleich ein ganzes Stück besser. | Die Schwiegermutter Ihres Spielers %1 ist nach einem längeren Besuch endlich wieder ausgezogen. Er fühlt sich gleich ein ganzes Stück besser. |
| 1117 | K39 | Die Schwiegermutter Ihres Spielers %s ist bei diesem zu einem längeren Besuch eingezogen. Darüber ist er natürlich nicht besonders begeistert. | Die Schwiegermutter Ihres Spielers %1 ist bei diesem zu einem längeren Besuch eingezogen. Darüber ist er natürlich nicht besonders begeistert. |
| 1127 | F01 | %1, die Frau von %2, setzt einen Detektiv an, um herauszufinden, ob ihr Mann eine Affäre hat. Dieser schießt noch am ersten Abend seiner Tätigkeit eindeutige Photos. Frau %3 ist außer sich, läßt den Sperrmüll kommen und alle Sachen ihres Mannes abtransportieren. Dann wechselt sie das Schloß aus. Das war es. | %2, die Frau von %1, setzt einen Detektiv an, um herauszufinden, ob ihr Mann eine Affäre hat. Dieser schießt noch am ersten Abend seiner Tätigkeit eindeutige Photos. Frau %3 ist außer sich, läßt den Sperrmüll kommen und alle Sachen ihres Mannes abtransportieren. Dann wechselt sie das Schloß aus. Das war es. |
| 1194 | K26 | %1 wurde bei der Gartenarbeit von zwei Hornissen gestochen. Er fällt zwei Wochen aus. | %1 wurde bei der Gartenarbeit von zwei Hornissen gestochen. Er ist zwei Wochen angeschlagen. |
| 1207 | K49 | Seit Single %1 einen Kochkurs besucht hat, und er nicht mehr ständig Fertigpizza essen muß, hat er ganz schön zugelegt. Er schleppt locker zwei Kilo zuviel mit sich herum. | Seit %1 einen Kochkurs besucht hat, und er nicht mehr ständig Fertigpizza essen muß, hat er ganz schön zugelegt. Er schleppt locker zwei Kilo zuviel mit sich herum. |
| 1210 | K29 / K40 | Ihr Spieler %1 ist von einem seiner Bienenvölker angegriffen und mehrfach gestochen worden. Seine Frau %2 ist darüber so entsetzt, daß Sie ihm sein Hobby einfach verbietet. Der Spieler kann in den nächsten Tagen nur eingeschränkt trainieren. | Ihr Spieler %1 ist von einem seiner Bienenvölker angegriffen und mehrfach gestochen worden. Er gibt sein Hobby daraufhin auf. |
| 1224 | K27 | Ihr Spieler %1 hat bei einem Tauchgang Kontakt mit einer giftigen Qualle gehabt, was ein übles Hautbrennen verursacht. Die nächste Woche ist er ziemlich angeschlagen. | Ihr Spieler %1 hat bei einem Tauchgang Kontakt mit einer giftigen Qualle gehabt, was ein übles Hautbrennen verursacht. Er fällt zwei Wochen aus. |
| 1276 | K39 | Ihr Spieler %s wurde bei einer Bordellrazzia von der Polizei verhaftet. | Ihr Spieler %1 wurde bei einer Bordellrazzia von der Polizei verhaftet. |
| 1294 | K42 | "Der Rasen auf diesem Trainingsplatz ist so etwas von kaputt. Hier verletzt man sich nur.", meint er und geht nach Hause. | Ihr Spieler %1 bricht das Training ab. "Der Rasen auf diesem Trainingsplatz ist so etwas von kaputt. Hier verletzt man sich nur.", meint er und geht nach Hause. |
| 1296 | K40 | Ihr Starspieler %1 möchte nicht mit ins Trainingslager vor dem Spiel. "Das ist doch Quatsch. Ich möchte lieber bei meiner Frau %2 bleiben." Nur zähneknirrschend kommt er doch mit. | Ihr Starspieler %1 möchte nicht mit ins Trainingslager vor dem Spiel. "Das ist doch Quatsch. Ich möchte lieber bei meiner Frau bleiben." Nur zähneknirrschend kommt er doch mit. |
| 1338 | K39 | Die Computerfirma Ihres Spielers %1 muß leider Konkurs anmelden. Die Geschichte ist für %s ein teurer Spaß, da er in nicht unerheblichen Ausmaß für die Verluste haftet. Er sieht doch ziemlich mitgenommen aus. | Die Computerfirma Ihres Spielers %1 muß leider Konkurs anmelden. Die Geschichte ist für %1 ein teurer Spaß, da er in nicht unerheblichen Ausmaß für die Verluste haftet. Er sieht doch ziemlich mitgenommen aus. |
| 1355 | K39 | Ihr Spieler %s macht in den nächsten Tagen einen Werbespot für feine Nadelstreifenanzüge und ist daher ein wenig abgelenkt. | Ihr Spieler %1 macht in den nächsten Tagen einen Werbespot für feine Nadelstreifenanzüge und ist daher ein wenig abgelenkt. |

Text 1294 beginnt im Original mit einem Leerzeichen; es entfällt.

**Umsetzung im Installer 1.45 (18.11.2026):** maßgeblich ist `SAQ_TEXTE` in `tools/patch_bauen.py`. Der Lader
`0x005EF298` nimmt die Datei nur mit genau 273692 Bytes Text an (`0x005EF303`); die neuen Texte sind zusammen 93 Bytes
kürzer, deshalb ist Text 1210 mit 93 Leerzeichen aufgefüllt. Text 1276 behält sein Leerzeichen am Ende. Weicht einer der
20 Texte vom alten Wortlaut ab, ändert der Installer die Datei nicht (statt, wie zuerst gesagt, nur diesen Text
auszulassen – die Länge ginge sonst nicht auf).

## Häufigkeit der korrigierten Meldungen (gerechnet am 18.11.2026)

Auf Wunsch des Nutzers. Gerechnet aus den Lostabellen des Programms, nichts davon im Spiel gemessen. Die Zahlen gelten,
**wenn die Bedingung erfüllt ist**; wie oft sie erfüllt ist, hängt vom Spielstand ab (Auszählung unten).

**Grundlagen (am Code gelesen):**
- Die täglichen Ereignisse laufen nur für Vereine menschlicher Manager (`0x006502A9`, `0x0065034E`), und zwar nicht jeden
  Tag: In 1 von 20 Fällen fällt der Tag ganz aus (`0x0064F9B6`), sonst je Verein mit 2 von 3 (`0x0064FA8A`). Das sind
  rund 231 Ereignistage je Saison (365 × 0,95 × 2/3).
- An einem Ereignistag zieht `0x005EF8CC` eine Ereignisart mit Gewicht w von 10000 (Tabelle `0x0088E128`). Gewicht 100
  bedeutet 2,31 Züge je Saison.
- Danach lost die Routine der Art ihr einzelnes Ereignis aus (Lostabellen in `analyse/meldungen/gewichte.txt`); die
  Zuordnung Text → Los ist aus Sprungtabelle und Textstelle bestimmt.
- Nicht eingerechnet: der Merker der letzten 20 Ereignisse (`0x00A32738`, verhindert schnelle Wiederholungen) und die
  Fälle, in denen ein gezogenes Los seine eigene Bedingung nicht erfüllt.

### Ereignisse aus dem täglichen Verteiler

| Text | Punkt | Weg (Nummer im Verteiler, Gewicht) | je Saison, wenn die Bedingung erfüllt ist | Bedingung |
|---|---|---|---|---|
| 1093 / 1094 | K01, K14, K41 | Nr. 9 (100) → je Los 1 von 3 | 0,77 | ein Spieler hat einen Hochzeitstermin; 1093: Krisenstufe 0; 1094: dazu eine Geliebte |
| 1083 | K15 | Nr. 22 (22) → Los 1 von 2 | 0,25 (einmal in 4 Saisons) | Neuzugang mit Freundin, ohne Kind, Krisenstufe 0 |
| 1104, 1109, 1110 | K16, K17 | Nr. 4 (100) → je Los 1 von 12 | 0,19 (einmal in 5 Saisons) | Spieler mit Freundin; 1104: dazu ein Mitspieler ohne Beziehung; 1109 / 1110: frühere Partnerin, Beziehung jünger als ein Jahr |
| 1115, 1116, 1117, 1122, 1123 | K18, K45, F06 | Nr. 5 (100) → je Los 3 von 29 | 0,24 (einmal in 4 Saisons) | verheirateter Spieler (vor F06: zusätzlich eine Geliebte); 1115: genau ein Kind, Stärke über 1; 1123: Geliebte |
| 1124 / 1125 | K12, F06 | Nr. 5 (100) → Los 1 von 29 | 0,080 (einmal in 13 Saisons) | verheirateter Spieler |
| 1982 | K34, F06 | Nr. 5 (100) → Los 1 von 29, nur am 24.12. | 0,00022 (einmal in 4579 Saisons) | verheirateter Spieler |
| 1251–1253 (Affäre beginnt) | F01 | Nr. 12 (11) | 0,25 (einmal in 4 Saisons) | der gezogene Spieler ist verheiratet, Teilwert „Privat“ unter 100 |
| 1126, 1127, 1236 | F01 | Nr. 6 (100) → je Los 3 von 10 | 0,69 | verheirateter Spieler mit laufender Affäre, Krisenstufe 0 |
| 1128 | F01 | Nr. 6 (100) → Los 1 von 10 | 0,23 (einmal in 4 Saisons) | wie vorige Zeile |
| 1363, 1365 | K02, K19 | Nr. 25 (100) → je Los 30 von 692 | 0,10 (einmal in 10 Saisons) | 1363: zwei Spieler mit Partnerin; 1365: zwei Freunde, einer zufrieden, einer unzufrieden |
| 1389 | K47 | Nr. 25 (100) → Los 6 von 692 | 0,020 (einmal in 50 Saisons) | zwei Spieler derselben Position |
| 1565 | K32 | Nr. 23 (11) → Los 1 von 5, nur im Juni | 0,004 (einmal in 239 Saisons) | Schüler im Kader |
| 1150, 1151, 1152 | K31 | Nr. 10 (55) → je Los 3 von 99 | 0,039 (einmal in 26 Saisons) | Spieler mit Führerschein; je Fall weitere Bedingungen |
| 1237 | K31 | Nr. 10 (55) → Los 30 von 99 | 0,39 (einmal in 3 Saisons) | Spieler ohne Führerschein (nach K31 nur während des Entzugs) |
| 1358 / 1359 | K35 | Nr. 55 (20) → je 1 von 4 | 0,12 (einmal in 9 Saisons) | 1358: der gezogene Spieler hat keinen privaten Trainer; 1359: er hat einen |
| 969, 954 | K40, K39 | Nr. 50 (66) → je Los 200 von 3803 | 0,080 (einmal in 12 Saisons) | 969: verheiratet |
| 983 | K33 | Nr. 51 (44) → Los 10 von 60 | 0,17 (einmal in 6 Saisons) | ein Spieler ist Spitzel |
| 1076 | K25 | Nr. 2 (100) → Los 1 von 8 (dass Nr. 2 zur Routine `0x005F95AD` führt, ist aus der Lage im Code geschlossen) | 0,29 (einmal in 3 Saisons) | Spieler beim Wehrdienst |
| 1528, 1530 | K12 | Nr. 21 (11) → je Los 10 von 10000 | 0,00025 (einmal in 3933 Saisons) | Bedingungen des Falls |

Auffällig: Die Schlagzeilen 1528 und 1530 (Nr. 21) haben eine Lostabelle mit Gesamtzahl 10000 bei einer Summe der
Gewichte von 60 (`0x0088D8F8`) – jedes Los kommt nur in 1 von 1000 Zügen. Zusammen mit dem Gewicht 11 der Art erscheinen
sie praktisch nie. Ob die Gesamtzahl ein Versehen ist, ist nicht geprüft; kein Korrekturpunkt.

### Hobby-Meldungen (Nr. 19, Gewicht 110)

Der Verteiler zieht einen zufälligen Kaderspieler; nur wenn er ein Hobby hat, kommt dessen Fall. Bei 28 Spielern im Kader
sind das je Spieler mit Hobby 0,091 Züge je Saison, also ein Zug in 11 Saisons; danach der Wurf des Falls. Ein Hobby
bekommt ein Spieler über Nr. 18 (Gewicht 110, 2,54 Züge je Saison für einen zufälligen Spieler ohne Hobby; das
Hobby nach der Tabelle `0x0088E828`, Summe 1857).

| Text | Punkt | Hobby (Gewicht in der Hobby-Tabelle) | Wurf im Fall | je Saison und Spieler mit diesem Hobby |
|---|---|---|---|---|
| 1188 | K12 | 12 (50 von 1857) | 1 von 6 | 0,015 (einmal in 66 Saisons) |
| 1197 | K12 | 17 (50 von 1857) | 1 von 4 | 0,023 (einmal in 44 Saisons) |
| 1201 | K12 | 18 (80 von 1857) | 1 von 1 | 0,091 (einmal in 11 Saisons) |
| 1168 | K46 | 8 (10 von 1857) | 1 von 2 | 0,045 (einmal in 22 Saisons) |
| 1172, 1173 | K20, F04 | 8 (10 von 1857) | 1 von 2 × 4 (vor F04: 2 × 3) | 0,011 (einmal in 88 Saisons) |
| 1176 / 1177, 1178, 1179 | K40, F02 | 9 (100 von 1857) | 1 von 4 (vor F02: 2, ohne 1178 / 1179) | 0,023 (einmal in 44 Saisons) |
| 1180 | K28 | 11 (10 von 1857) | 1 von 2 | 0,045 (einmal in 22 Saisons) |
| 1193, 1194 | K21, K26 | 15 (5 von 1857) | 1 von 3 | 0,030 (einmal in 33 Saisons) |
| 1207 | K49 | 19 (50 von 1857) | 1 von 6 | 0,015 (einmal in 66 Saisons) |
| 1210 | K29 | 20 (20 von 1857) | 1 von 1 | 0,091 (einmal in 11 Saisons) |
| 1215, 1217 | K22, K30 | 28 (100 von 1857) | 1 von 6 | 0,015 (einmal in 66 Saisons) |
| 1224, 1225 | K27, K23 | 35 (50 von 1857) | 1 von 2 | 0,045 (einmal in 22 Saisons) |
| 1227, 1232 | K24, K31 | 38 (100 von 1857) | 1 von 6 | 0,015 (einmal in 66 Saisons) |

### Ereignisse hinter dem Verteiler

- **1269, 1276, 1294, 1296, 1309–1312 (K12, K39, K42, K40, K43, K44):** Hat die gezogene Art nichts ausgelöst, folgt mit
  Kadergröße von 1000 die Routine `0x005E08F1` für einen zufälligen Kaderspieler (bei 28 Spielern rund 5,83 Züge je
  Saison); jedes dieser Lose hat Gewicht 10 von 473: 0,12 (einmal in 8 Saisons) je Text, vor den Bedingungen des Falls.
- **1338, 1342, 1355 (K39, K36):** danach mit Kadergröße von 5000 die Firmen-Ereignisse `0x005E2152` (rund 1,17 Züge je
  Saison), jedes Los 10 von 300: 0,039 (einmal in 26 Saisons) je Los. 1342 (Karriereende) verlangt zusätzlich den Firmen-Stand 5, der
  nur über mehrere dieser Lose erreicht wird. In den Spielständen save383 und save109 hat keiner der 17000 Spieler eine
  Firma. **K36 wird praktisch nie eintreten.**

### Außerhalb des täglichen Verteilers (nur Bedingung, keine Zahl)

- **1880 (K03), 1750 (K04), 690 / 697 (K05, K06), 224 (K07), 283 / 284 (K08), 285 (K48):** hängen an Spielverlauf,
  Verhandlungen oder eigenen Auslösern; siehe „Nachgelesen“ zum jeweiligen Punkt.
- **Halbzeit-Schlagzeilen und Maulwurf (K11):** brauchen einen Maulwurf in der Aufstellung und Motivation unter 70.
- **888 / 889 (F03):** bei jeder Bauverzögerung 2 von 12 Gründen.
- **1481 (F05):** bei jeder Vertragsverhandlung mit einem Spielervermittler, wenn der Spieler unter 20 ist, mehr als 10
  Einsätze in der Saison hat und Byte Spieler +8 unter 1 liegt.
- **K13, K37, K38:** keine eigenen Meldungen.

### Auszählung an den Spielständen des Nutzers

Alle 17000 Spieler, save383 (save109 ähnlich): 180 mit Freundin, 52 verheiratet, keiner mit Geliebter, keiner mit Firma,
keiner ohne Führerschein (save109: einer), 318 mit Hobby, 3 mit Schüler-Merker. In den beiden Vereinen mit den meisten
Hobby-Spielern (die Vereine von Manager A und Manager B): 28 und
23 Spieler im Kader, davon je 9 bis 10 mit Hobby, 5 bis 6 mit Freundin, **keiner verheiratet**, keiner mit
Hochzeitstermin oder Geliebter, einer mit Schüler-Merker, 5 bis 6 Raucher, keiner mit privatem Trainer.

Folgerung: Die Ehefrau-Meldungen (F06, K18), die Affären-Kette (F01) und „Hochzeit platzt“ (K01, K14, K41) setzen
Zustände voraus, die in diesen Spielständen kein Spieler der beiden Vereine hat. Sie bleiben auch nach den Korrekturen
selten; am häufigsten sind die Meldungen für Spieler mit Freundin (Nr. 4) und die Hobby-Meldungen.

## Offen aus dem Befund (keine Korrektur möglich, bevor es geklärt ist)
- Folge der falschen Managernummer bei 1880 (was überschrieben wird); Inhalt des Platzes hinter dem Kader (K01).
- Noch ungelesene Routinen und „OK“-Einträge der Kataloge (Befund, „Im Nachgang“): dort können weitere Fehler
  stecken.
