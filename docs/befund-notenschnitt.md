# Befund: Notenschnitt in den Spielerdetails zu gut (16.11.2026)

Anlass: Meldung des Nutzers („der Notenschnitt der Spieler stimmt oft nicht in den Spielerdetails“, Vermutung: Einwechselspieler
ohne Note werden als Spiel mitgezählt). **G** = im Code gelesen und an Spielständen nachgerechnet, **V** = Vermutung.
Kein Patch gebaut, im Spiel noch nicht gegengelesen.

## Daten (G)
Spielersatz **0x2F9, 46 Bytes = ein Byte je Spieltag** der laufenden Saison (Speicher `0x00C02869 + Nr × 0x354 + Spieltag`,
Lesen `0x006FF47F`, Schreiben endet bei `0x006FF431`):
- Bits 6–7 (0xC0): Einsatz (≠ 0 = hat gespielt; 0x80 und 0xC0 werden in der Anzeige anders eingefärbt),
- Bits 2–5 (0x3C): Notencode = Note × 2 (0 = **keine Note**, z. B. spät eingewechselt),
- die Bytes werden beim Saisonwechsel nicht gelöscht; die Anzeigen lesen nur bis zum aktuellen Spieltag
  (`0x006927B3`; im Liga-Objekt Wort +0x46 = gespielte Spieltage).
Ein zweites Feld gleicher Länge liegt bei 0x2CB (`0x006FF43E`, Halbbytes für die weiteren Balken der Seite).

## Die zwei Rechenwege (G)
| Stelle | Summe | Teiler |
|---|---|---|
| Statistik „Notenschnitt Mannschaft“ (`0x0046E7DC` ff., Text 3043) | Notencodes | nur Einsätze **mit** Note (`0x0046E856`: bei Note 0 wird nichts gezählt) |
| Spielerdetails, Seite „Noten“ (`0x00561C46` ff., Ausgabe „%1.1f“ in Feld 0x1312) | Notencodes | **alle** Einsätze, auch ohne Note (`0x00561CD3`: Zähler + 1 ohne Prüfung) |

Beide teilen danach durch 2,0 (`0x0080DAF0`). In den Spielerdetails zieht also jeder Einsatz ohne Note den Schnitt nach
unten (= besser). Das ist die erste Theorie des Nutzers; die zweite (Note ohne gezähltes Spiel) kommt im Code nicht vor.

## Beleg am Spielstand `saves/patchtest/vorher.an3` (Saisonende 2112/13, 34 Spieltage)
Von 67 Spielern beider Manager mit Einsatz haben 30 mindestens einen Einsatz ohne Note. Beispiele
(Einsätze / davon ohne Note: Spielerdetails → richtig):
- Gladbach: Soudani 34 / 5: 2,8 → 3,3; Chakvetadze 19 / 2: 3,5 → 3,9; Rischke 34 / 3: 2,8 → 3,1; Iglesias 7 / 1: 2,5 → 2,9.
- Uerdingen: Ruiz 16 / 6: 2,4 → 3,9; Augustin 15 / 3: 2,4 → 3,0; Dizdarevic 26 / 4: 2,8 → 3,3; Martins 5 / 1: 2,3 → 2,9.
Skript: Scratchpad `note2.py <Spielstand> <Cache>` (liest alle 46 Bytes, daher nur für Spielstände am Saisonende gültig).

## Korrekturvorschlag (nicht gebaut)
In `0x00561CD3` den Zähler nur erhöhen, wenn die Note ≠ 0 ist. Datei-Offset 0x161CD3, 18 Bytes:
- alt `668B85BEFDFFFF 66050100 668985BEFDFFFF` (Zähler laden, + 1, speichern),
- neu `83F901 66839DBEFDFFFFFF 90909090909090` (`cmp ecx,1` – ecx enthält noch die Note –, `sbb word ptr [ebp-242h],-1`
  = + 1 nur bei Note ≥ 1, dann 7 × nop).
Hat ein Spieler nur Einsätze ohne Note, bleibt der Zähler 0 und die Seite zeigt wie bisher „-“.
Das ändert nur die Anzeige. Test: Spielerdetails → Noten eines Spielers mit spätem Kurzeinsatz gegen die Statistik
„Notenschnitt Mannschaft“ halten; beide müssen danach gleich sein.

## Bewusst nicht anfassen
`0x00770A72` (Spiellogik: prüft die letzten zehn Spieltage, Schnitt ≥ 4,5 bzw. ≥ 3,8) rechnet ebenfalls mit allen Einsätzen.
Das beeinflusst Entscheidungen im Spiel; eine Änderung wäre ein Eingriff ins Verhalten, kein Anzeigefehler.

## Stand 16.11.2026 abends: Patch gebaut, zweite Stelle erklärt
- Der Nutzer hat der Anzeige-Korrektur zugestimmt. Patch `notenschnitt-details` steht in `tools/a3patch.py`; gebaut in
  `build/kandidat-1.43/anstoss3.exe` (SHA-256 `B93E5688…1527`, 1.42 + diese 18 Bytes), mit `dumpbin` gegengelesen, kein
  Sprungziel im geänderten Bereich. **Noch nicht im Spielordner, im Spiel ungetestet.**
  Hinweis: `tools/patch_bauen.py` (1.42) kennt den neuen Patch noch nicht – für 1.43 Text und Version ergänzen.

### Was `0x00770A72` rechnet (G für den Ablauf, V für die Bedeutung einzelner Felder)
Aufrufer `0x00770FE6` in der Kaderschleife von `0x00770BAE`. Je Spieler:
1. `0x007709E8` „Liebling“: wahr, wenn Feld +0x3E ≥ 20 (V: Saisontore), oder Torwart und +0x50 > 4, oder Spieltag > 33 und
   +0x54 − (+0x55 + +0x56) > 30 (V: Einsätze ohne Ein-/Auswechslungen), oder +0x49 > 5.
   → Kennzeichen 0x10000 im Flagwort +0x20 (Spielersatz 0x190) = Text 4186 „Liebling“; mit 1 % Zufall dauerhaft (Wert 2 in
   Spielersatz 0x262, Bits 0–1, `0x00706467`).
2. sonst `0x00770A72` „verhasst“: wahr, wenn
   a) Stürmer (Position 10) mit +0x54 > 20 und +0x3E < 5, oder
   b) in den letzten zehn Spieltagen mehr als 3 Einsätze und Summe der Notencodes × 5 / Einsätze ≥ 45 (Schnitt ≥ 4,5), oder
   c) Wort +0x12 hat Bit 0x40 oder 0x20 (Eigenschaft, nicht entschlüsselt), mehr als 3 Einsätze und Schnitt ≥ 3,8.
   → Kennzeichen 0x400 = Text 4187 „verhasst“; mit 2 % Zufall dauerhaft (Wert 3).
3. sonst beide Kennzeichen löschen; mit 1 % Zufall dauerhaft zurück auf 1.
Anzeige der beiden Texte in den Spielerdetails: `0x0055B167` ff.
**Der Fehler:** In b) und c) zählen Einsätze ohne Note als Einsatz mit Note 0. Der Schnitt fällt zu gut aus, und die
Schwelle „mehr als 3 Einsätze“ wird früher erreicht. Beispiel: 5,0 / 5,0 und zwei Kurzeinsätze ohne Note → gerechnet 2,5,
richtig 5,0. Folge: Spieler werden seltener „verhasst“ als vorgesehen. Was „verhasst“ im Spiel sonst bewirkt, ist nicht
verfolgt. Entscheidung des Nutzers offen.

## Entscheidung des Nutzers (16.11.2026) und Patch `verhasst-noten`
Wörtlich: „Verhasst-Regel auch korrigieren, es verursacht, dass die Motivation sinkt, und ja, sie triggert schneller nach der
Korrektur, aber die Spieler werden auch nur bei Spielen bewertet, wo sie auch eine Note bekommen haben – das ist für mich
richtig!“ (Dass „verhasst“ die Motivation senkt, ist Aussage des Nutzers, im Code nicht verfolgt.)
Patch in `tools/a3patch.py`: 22 Bytes ab Datei-Offset 0x370B2E (`0x00770B2E`): Notencode zur Summe addieren, Zähler nur bei
Code ≥ 1 erhöhen (`add [ebp-0Ch],ax` / `cmp eax,1` / `sbb word ptr [ebp-2],-1`). Die Schwelle „mehr als 3“ gilt damit für
benotete Einsätze. Gebaut in `build/kandidat-1.43/anstoss3.exe` (SHA-256 `A9DA5C3C…50C3`), mit `dumpbin` gegengelesen.
**Im Spiel ungetestet**; direkt prüfbar ist nur, dass nichts abstürzt und „verhasst“ weiter vergeben wird.

## Prüfauftrag des Nutzers (16.11.2026): weitere Stellen, die Noten oder Einsätze ohne Note auswerten
Vollständig durchgesehen: alle Zugriffe auf die Spieltagsbytes (`0x00C02869`, `+0x319`), auf die Note des letzten Spiels
(`0x00705E9B`) und die Aufrufer der Spielnoten im Spielobjekt (`0x006580B2`, `0x006581CD`).

| Stelle | Zweck | Befund |
|---|---|---|
| `0x0046E7DC` Statistik „Notenschnitt Mannschaft“ | Schnitt gesamt / heim / auswärts | richtig (zählt nur benotete Einsätze) |
| `0x00561C46` Spielerdetails „Noten“ | Saisonschnitt | Fehler, Patch `notenschnitt-details` |
| `0x00770A72` Fan-Status „verhasst“ | Schnitt der letzten 10 Spieltage | Fehler, Patch `verhasst-noten` |
| `0x007230E1` Liga-Statistik „Tagesform“ | Mannschaftsschnitt letztes Spiel | Fehler, Patch `tagesform` |
| `0x0048E36F`, `0x004BA0F3`, `0x0072796F` | Anzeige einer einzelnen Note | richtig (ohne Note bleibt das Feld leer) |
| `0x0065D53F`, `0x0065DC6F`, `0x006FAAB0` | bester/schlechtester Spieler eines Spiels | nur ein Spiel, kein Schnitt – unauffällig |
| `0x005E588A`, `0x005E1741` | Ereignisse nach einer einzelnen schlechten Note | nur ein Spiel – unauffällig |
| **`0x00705EB6`, `0x00705F60`, `0x0070607A`, `0x00706015`** | Saisonschnitt, Schnitt der letzten n Einsätze, „Spieltage seit dem letzten Einsatz“ | **Fehler (G): falsche Bitmasken**, siehe unten |

### Die vier Routinen mit falschen Masken (G für die Abweichung, V für die Absicht)
Der Schreiber `0x006FF2F7` legt je Spieltag ab: Bits 6–7 Einsatz (0x40 durchgespielt, 0x80 eingewechselt, 0xC0
ausgewechselt), Bits 2–5 Notencode, Bits 0–1 Karte. Drei Leser (Statistik, Spielerdetails, „verhasst“) lesen genau so.
Die vier Routinen prüfen dagegen den Einsatz nur mit 0x80 (durchgespielte Spiele fehlen) und lesen die Note mit 0x1C
(nur drei von vier Bits: Note 4,0 wird 0, 4,5 wird 0,5 … 6,0 wird 2,0). Folgen:
- `0x00705EB6` ← `0x005E572C` (Ereignis mit Textnummer 0x5EF, Wirkung −6 auf Spielersatz 0x272): Bedingung „letzte Note
  ≥ 5,0, mehr als 10 Einsätze und Saisonschnitt > 4,0“. Der gerechnete Schnitt kann höchstens 3,5 sein → **das Ereignis
  kann nie eintreten.**
- `0x00705F60(3)` ← `0x005FEC09` (Ereignis 0x4D3, Wirkung −2, nur Spieler mit Stärke ≥ 9): Schnitt der letzten drei
  Einsätze über einer Schwelle. Durch die Masken lösen ausgerechnet Noten zwischen 2,5 und 3,5 aus, schlechte Noten nicht.
- `0x0070607A` ← `0x00493490` (Dialog, Wirkung −6 bzw. −2 auf Spielersatz 0x26F): „letzter Einsatz liegt 6 bis 10
  Spieltage zurück“. Durchgespielte Spiele gelten nicht als Einsatz.
- `0x00706015`: kein Aufrufer.
Die Ereignistexte stehen in einer eigenen Texttabelle (`0x005EF430`, bis 2483 Einträge, aus `texte\…` in den gepackten
Archiven) und sind nicht ausgelesen – **welche Meldungen das im Spiel sind, ist unbekannt.**
Mögliche Korrektur: je Routine zwei Bytes (0x80 → 0xC0, 0x1C → 0x3C). Das würde ein bisher totes Ereignis aktivieren und
zwei weitere anders auslösen – Eingriff ins Verhalten, **Entscheidung des Nutzers offen, nichts gepatcht.**

## Wofür die vier Routinen gedacht sind (16.11.2026 nachts; Texte jetzt lesbar)
Neues Werkzeug `tools/a3ereignis.py <Ereignis.saq> [Nummer …]`: liest `texte\Ereignis.saq` (2483 Texte; int32 Länge,
int32 Anzahl, jedes Byte mit dem vorigen gespeicherten Byte XOR-verknüpft, Lader `0x005EF298`, Tabelle `0x00A2FAE8`).
Dialogtexte stehen in `original/deb/MeineDialoge.rch` (deutsch/englisch im Klartext).

| Routine | Verwendung | Text | Bedingung im Code | Wirkung |
|---|---|---|---|---|
| `0x00705EB6` Saisonschnitt | Zeitungsmeldung, `0x005E572C` | 1519 „%1 erneut ein Totalausfall - %2: Wie lange müssen wir ihn noch ertragen?“ | im letzten Spiel dabei, letzte Note ≥ 5,0, Saisonschnitt > 4,0, mehr als 10 Einsätze, Verein hinter den Erwartungen (`0x00775F0A` > 0, V) | −6 auf Spielersatz 0x272 (`0x00700FA2`) |
| `0x00705F60(3)` Schnitt der letzten 3 Einsätze | Zeitungsmeldung, `0x005FEC09` | 1235 „Goldkettchen und teure Autos - %1 ein Prototyp des verzogenen Fußballmillionärs“ | Stärke ≥ 9, Verein deutlich hinter den Erwartungen (> 2), Schnittwert > 40 | Meldung mit Wert −2 |
| `0x0070607A` Spieltage seit letztem Einsatz | Gespräch bei Auswechslung (Dialog 496 „Ihr Spieler %s möchte gerne den Grund der Auswechslung wissen!“), Antwort 5 „Spielpraxis für Mitspieler“, `0x00493490` | – | Einsatzquote des eingewechselten Mitspielers < 20 %: +1; sonst (ab Spieltag 11) letzter Einsatz des Mitspielers 6–10 Spieltage her: −6, andernfalls −2 | „Trainerzähler“ des ausgewechselten Spielers (Spielersatz 0x26F, `0x007007A1`; im Dialog als „Trainerzähler vorher/nachher“ beschriftet) |
| `0x00706015` | kein Aufrufer | – | – | – |

Antworten des Dialogs 496 in Reihenfolge: Sollte sich seinen Beifall abholen / Schonung für das nächste Spiel / Taktische
Gründe / Mußte irgend etwas ändern / Spielpraxis für Mitspieler / Schien müde zu sein / Schlechte Leistung / Schnauze voll
von ihm. Nachbarmeldungen ohne Notenschnitt: 1520 „%1 als Symbol für die Krise - Der Liebling des Trainers vor dem Aus?“,
1521 „Sensibelchen %1 völlig verunsichert - Hat ihn auch der Trainerstab aufgegeben?“.

Einschätzung (meine, V):
- 1519 „Totalausfall“: Absicht eindeutig (Saisonschnitt schlechter als 4,0), die Meldung ist heute tot. Mit richtigen Masken
  würde sie eintreten können; der Schnitt enthielte dann noch Einsätze ohne Note (gleicher Fehler wie beim Notenschnitt).
- 1235 „Goldkettchen“: Die Routine teilt nicht durch 2. Mit richtigen Masken hieße „> 40“ Schnitt schlechter als 2,0 –
  die Meldung käme für fast jeden Star eines Vereins in der Krise. Ob 2,0 oder 4,0 gemeint war, ist nicht belegbar.
- „Spielpraxis für Mitspieler“: kleine Wirkung, Absicht der −6-Regel unklar.
Nichts gepatcht. Entscheidung des Nutzers offen.

## Bewertung des Nutzers (16.11.2026 nachts) und Patch `totalausfall`
- **Totalausfall:** „klingt ganz klar nach Fehler und habe diese Zeitungsmeldung noch nie gesehen. Korrektur sinnvoll.“
  → Patch `totalausfall` in `tools/a3patch.py`, Bytes aus `tools/asm_totalausfall.py` (88 Byte Code im alten Rumpf von
  `0x00705EB6`, 170 Byte): nur die bisher gespielten Spieltage (`0x00692744(Verein)`), Einsatz = 0xC0, Note = 0x3C,
  Einsätze ohne Note übersprungen, Ergebnis wie bisher Note × 10. **Besonderheit:** Die Routine holt den Verein aus dem
  Rahmen ihres einzigen Aufrufers (`0x005E572C`, `[ebp+8]`); sie darf deshalb nie von anderer Stelle aufgerufen werden.
  Der Original-Fehler hatte zusätzlich alle 46 Plätze gelesen, also auch Reste der Vorsaison.
  Gebaut in `build/kandidat-1.43/anstoss3.exe` (SHA-256 `A72F95FF…1807`), mit `dumpbin` gegengelesen, **im Spiel
  ungetestet, noch nicht im Spielordner**. Gilt als Spiellogik → im Installer optional.
- **Goldkettchen (1235):** „schwer zu sagen … eventuell weitere Prüfungen“. Zusätzlich gelesen: Die Meldung gehört zu den
  Zufallsereignissen aus dem Privatleben (Nachbarn: 1232/1234 Führerschein, 1233 Hobby). Aus dem Code ist nicht
  entscheidbar, ob „Schnitt der letzten drei schlechter als 2,0“ (so stünde es mit richtigen Masken da) oder „schlechter
  als 4,0“ gemeint war. Nicht gepatcht. Offene Frage an den Nutzer: Hat er die Meldung schon gesehen, bei welchen Spielern?
- **Spielpraxis für Mitspieler:** bleibt unverändert („fühlte sich bisher nicht kaputt an“).
- **Feldnamen (Aussage des Nutzers):** Spielersatz 0x26F („Trainerzähler“ im Dialog) = **Motivation Trainer**; er geht davon
  aus, dass die meisten Spielerereignisse eines der Motivationsfelder treffen. Dazu passt (G): Die Zeitungsmeldungen ändern
  Spielersatz 0x272 über `0x00700FA2`; das Führerschein-Ereignis meldet dabei alten und neuen Wert mit der Kennzahl 4.
  Sieben Felder mit Lesern `0x007008B9` (0x26F), `0x00700C42`, `0x00700E3F`, `0x007010BA` (0x272), `0x007011F1`,
  `0x00701328`, `0x0070145F`; Namen der übrigen noch nicht zugeordnet (Reihenfolge der Motivationsanzeige erfragen).

## Motivationsfelder (Bildschirmfoto des Nutzers, 16.11.2026) und Wirkung von Schlagzeilen
Spielerdetails zeigen (0–100): Kondition, Frische, Motivation, dann die Teilwerte **Trainer, Team, Verein, Presse, Privat,
Ablenk., Angebote**; „Motivation“ ist der Schnitt der Teilwerte (Aussage des Nutzers). Zuordnung zu den sieben Bytes des
Spielersatzes ab 0x26F: 0x26F Trainer (G: Dialog 496 „Trainerzähler“ = `0x007007A1`), 0x272 Presse (V stark: viertes
Feld, wird von den Zeitungsmeldungen über `0x00700FA2` geändert), dazwischen 0x270 Team, 0x271 Verein, danach 0x273
Privat (`0x00701210`), 0x274 Ablenk., 0x275 Angebote (V, nur aus der Reihenfolge).

Zeitungsmeldungen (`0x00789C32(Rang, Textnummer, Anzahl Namen, Kennzeichen, …)`): Die drei ranghöchsten Schlagzeilen werden
gehalten (`0x00789895`, Rang 7 schlägt 6). Kennzeichen 0x100 = Zusatzwert für „Presse“ (Satz +0x28), 0x200 = für das Feld
von `0x00701210` (Satz +0x2C). Angewendet werden sie in `0x0078A0F5` nur für die oberste Schlagzeile und nur, wenn im Satz
eine Spielernummer steht (Kennzeichen 0x80000000). Die Leistungs-Schlagzeilen (1519–1521) geben keine Nummer mit und
ziehen den Wert deshalb direkt über `0x00700FA2` ab.

### „Goldkettchen“ (1235) genau
- Ort: Zufallsereignisse eines Spielers (`0x005FE987`): Zufallszahl 0–5; 0–3 sind vier andere Ereignisse (u. a. Führerschein
  1232/1234, Hobby 1233), **4 und 5 führen zur Goldkettchen-Prüfung** (`0x005FEBDF`).
- Bedingungen: Feld +2 des Spielers ≥ 9 (V: Stärke), Verein mehr als 2 hinter den Erwartungen (`0x00775F0A`, V), und
  `0x00705F60(3)` > 40 (Schnitt der letzten drei Einsätze, fehlerhaft gelesen).
- Folge: Schlagzeile mit Rang 6 und Zusatzwert −2 für „Presse“ – **aber ohne Spielernummer und ohne direkten Abzug**. Der
  Wert −2 wird daher nie angewendet (G: Satz wird mit 0 vorbelegt, `0x0078A192` überspringt bei Nummer 0).
  Die Meldung ist also reiner Text ohne Wirkung auf den Spieler.

## Entscheidung des Nutzers (16.11.2026): auch „Goldkettchen“ korrigieren, Wirkung im Patch beschreiben
Wörtlich: „was ist wenn wir Korrekturen doch einbauen, im Patch können wir dann dazu schreiben welche Auswirkungen es hat.
Und wie groß diese sind.“ Seine Vermutung: Manche Meldungen könnten von den Entwicklern stillgelegt worden sein, weil sie zu
oft kamen oder der Rechenfehler nicht gefunden wurde (nicht belegbar).
Patch `goldkettchen` in `tools/a3patch.py`, Bytes aus `tools/asm_goldkettchen.py`:
- `0x00705F60` (181 B neu belegt, 93 B Code): Schnitt der letzten drei **benoteten** Einsätze der laufenden Saison,
  richtige Masken, Ergebnis Note × 10. Kein Stapelargument mehr; Verein aus dem Rahmen des einzigen Aufrufers
  (`[ebp+0Ch]`, `0x005FEC09`).
- `0x005FEC04` (59 B): Aufruf, Vergleich „> 40“ (= schlechter als 4,0), Schlagzeile wie bisher, danach **neu** der Abzug
  von 2 bei „Presse“ (`0x00700FA2`), den das Original zwar übergibt, aber nie anwendet.
Meine Festlegung (V, vom Nutzer nicht ausdrücklich bestätigt): Schwelle 4,0, weil die Schwesterroutine für „Totalausfall“
denselben Vergleich „> 40“ auf Note × 10 anwendet. Mit der anderen Lesart (2,0) käme die Meldung fast immer.
„Spielpraxis für Mitspieler“ bleibt unverändert.
Test-exe `build/kandidat-1.43/anstoss3.exe`, SHA-256 `95122B7A…D094` (enthält auch `totalausfall`), mit `dumpbin`
gegengelesen. **Im Spiel ungetestet, noch nicht im Spielordner.**

### Größe der Auswirkungen (für die Patch-Texte; gerechnet an `vorher.an3`, 1. Bundesliga 2112/13, Skript `wirkung1.py`)
- **Totalausfall (1519):** Notenbedingung (mehr als 10 benotete Einsätze, Saisonschnitt schlechter als 4,0, aktuelle Note 5,0
  oder schlechter) war in der ganzen Liga 30-mal erfüllt, bei 13 von 383 eingesetzten Spielern – im Mittel unter zwei
  Anlässe je Verein und Saison. Zusätzlich muss der Verein hinter den Erwartungen liegen. Wirkung je Meldung: „Presse“ −6
  (einer von sieben Teilwerten der Motivation, also knapp ein Punkt Motivation).
- **Goldkettchen (1235):** Die Notenbedingung (letzte drei benotete Einsätze schlechter als 4,0) galt an 14,7 % der
  Spieler-Spieltage (1481 von 10 098; 297 Spieler mit Stärke ≥ 9, davon 245 mindestens einmal). Die Meldung braucht
  außerdem ein ausgelostes Privat-Ereignis (davon ein Drittel) und einen Verein deutlich hinter den Erwartungen. Wirkung:
  „Presse“ −2 (rund 0,3 Punkte Motivation). In diesem Spielstand haben fast alle Erstligaspieler Stärke ≥ 9.
- **Verhasst-Regel:** Wirkung laut Nutzer auf die Motivation. Größe nachgerechnet am 16.11.2026 (Skript `wirkung2.py`,
  derselbe Spielstand, 18 Vereine, 34 Spieltage, 397 eingesetzte Spieler, Prüfung nach jedem Spieltag über die Plätze
  d−1 … d−10 wie in `0x00770A72`): Regel b (Schwelle 4,5) alt an 33, neu an 45 von 13 498 Spieler-Spieltagen erfüllt,
  bei 13 bzw. 16 Spielern; kein Fall, der nur mit der alten Zählung auslöst. Regel c (Schwelle 3,8, nur Spieler mit den
  Eigenschaften 0x20/0x40) für alle Spieler gerechnet, weil das Flagwort im Spielersatz nicht zugeordnet ist: 2262 → 2825
  (+25 %), 251 → 274 Spieler. Regel a (Stürmer ohne Tore) ist von der Korrektur nicht berührt.

## Im Spiel bestätigt (16.11.2026 nachts, `saves/patchtest/test6.an3`, Saison 2114, 5 Spieltage)
- **`notenschnitt-details`:** Aussage des Nutzers: „die Durchschnittsnoten-Bewertung in den Spielerinfo stimmt zu 100 %,
  hab extra drei Spieler spät eingewechselt, damit sie keine Note bekommen.“ Im Spielstand dazu: Rohloff (5 Einsätze,
  1 ohne Note: alt 3,0, richtig 3,8), Benzar (4/1: 2,2 → 3,0), Augustin (4/1: 2,2 → 3,0), Dizdarevic (3/1: 2,0 → 3,0),
  Martins (1/1: „-“). Skript `test6.py` im Scratchpad.
- `verhasst-noten`, `totalausfall`, `goldkettchen`: kein Absturz gemeldet; Wirkung nicht gezielt prüfbar.

## Berichtigung (16.11.2026): „Liebling“-Regel
`0x006FF01B` liefert das **Alter** des Spielers (über `0x0067582A`, Geburtsdatum im Laufzeitobjekt +0xCC, aktuelles Datum
`0x00B5CBDA/DC/DE`), nicht den Spieltag. Die dritte Bedingung in `0x007709E8` lautet daher: älter als 33 Jahre und mehr
als 30 Einsätze ohne Ein-/Auswechslung in der Saison. Die frühere Angabe „nach dem 33. Spieltag“ war falsch.
Dieselbe Routine erklärt im Führerschein-Ereignis die Schwelle „über 17“.
