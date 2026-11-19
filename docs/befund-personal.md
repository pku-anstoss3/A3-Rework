# Befund: Trainer, Co-Trainer und Torwarttrainer werden zu schwach nachgebildet (15.11.2026)

Meldung des Nutzers: „Es werden keine neuen Co-Trainer und Torwarttrainer mehr generiert, die da sind, sind alle unter Stärke 8.“
**G** = an Daten belegt, **V** = Vermutung. Am Spiel ist nichts geändert, die Stelle im Code ist noch nicht gefunden.

## Personensätze im Spielstand (G)
Blöcke mit 52 Byte, ab Block 1606 (Spielstand 383), ein Block je Person; Index 0 = „Teamchef“.
- Index 1 … etwa 1444: Trainer und Manager, anfangs paarweise je Verein (Trainer, Manager), in Stammdaten-Reihenfolge.
- Index etwa 1500 … 1601: 100 Torwarttrainer.
- Dahinter folgen andere 52-Byte-Sätze (keine Personen).

| Offset | Inhalt | Status |
|---|---|---|
| +0 / +2 | Vorname / Nachname (Index in die Namensliste) | G |
| +4 | Kompetenz als Trainer bzw. Torwarttrainer (0–15) | G (Verteilung 2019 wie in der Editor-Hilfe; Trainer haben hier den höheren Wert) |
| +5 | Kompetenz als Manager | V (Manager haben hier den höheren Wert) |
| +6 | Ruf des Trainers (0–6) | V |
| +8, +9, +0xA | Geburtstag, -monat, -jahr (int16) | G |
| +0x10 | Gehalt (int32) | V |

Co-Trainer kommen laut Editor-Hilfe aus demselben Topf wie die Trainer („jede arbeitslose Person kann Trainer oder Co-Trainer sein“).

## Was über die Jahre passiert (G, Spielstände 1–97 Person für Person verfolgt, dazu 383)
Es werden sehr wohl neue Personen erzeugt, aber **mit demselben Namen** und sehr niedriger Kompetenz:

| | Torwarttrainer | Trainer / Manager |
|---|---|---|
| Ersatz im Alter von | 65–69 | 65–80, meist 66–68 |
| Neue Person | 36 Jahre, Kompetenz **2** (101 von 110 Fällen) | 30 Jahre, Kompetenz **1–3** (alle 845 Fälle) |
| Zuwachs | +1, nur im Alter 36–49, im Mittel etwa 4 Punkte | meist +1, selten +2/+3, bis etwa 59 |
| Abbau | −1 ab 55 | −1 ab 60 |

Verteilung der Kompetenz der 100 Torwarttrainer:

| Saison | 0–5 | 6–10 | 11–15 | höchster Wert |
|---|---|---|---|---|
| 2019 | 21 | 41 | 38 | 15 |
| 2034 | 51 | 38 | 11 | 15 |
| 2047 | 49 | 49 | 2 | 13 |
| 2113 | 50 | 50 | 0 | 9 (viermal 9, dreizehnmal 8) |

Trainer/Manager mit Kompetenz ≥ 11: 2019 98, 2113 15.

Folge: Die guten Leute der Startdatenbank sterben bis etwa 2050 aus. Ein nachgebildeter Torwarttrainer kann rechnerisch kaum über 9
kommen. Die wenigen mit 8 oder 9 sind vermutlich unter Vertrag (V), frei bleiben die schwachen. Weil die Namen gleich bleiben,
sieht es im Spiel so aus, als kämen keine neuen nach.

## Ursache im Code (G, 15.11.2026) – kein Patch gebaut

Speicher: Trainer `0x00BE3920 + Nr × 0x54` (1500 Plätze), Torwarttrainer `0x00BE17F8 + Nr × 0x54` (101 Plätze), Daten ab +0x20.
Lesen/Schreiben über Kopien: Trainer `0x006317C6` / `0x006318F4`, Torwarttrainer `0x00631A0E` / `0x00631B30`
(Kopie: +2/+4 Name, +6 Kompetenz Trainer bzw. Torwarttrainer, +7 Kompetenz Manager, +0xA Geburtsdatum, +0xC Geburtsjahr).

**Gedacht ist es so:** Beendet ein Spieler die Karriere (`0x0066D975` → `0x0066DF9E`), kommt er auf eine Warteliste:
- Bedingungen: Nationalität eines aktiven Landes, älter als 35, mehr als 300 Spiele (Summe der Zähler 0x180, 0x188–0x18E;
  in den Saisons 1–9 eine kleinere Schwelle aus der Tabelle `0x008A00F8`).
- Torhüter mit Wahrscheinlichkeit 2/3 auf die Liste der Torwarttrainer (`0x008E1D88`, 10 je Land, Block mit 1800 Byte),
  alle anderen auf die Liste der Trainer (`0x008E0F78`, 20 je Land, Block mit 3600 Byte).
- Kompetenz = (Alter − 30) / 3 + Zufall 0–4 + Spielerstärke + 1, höchstens 12. Gute Ex-Profis kämen also mit 12 an.
- Wird ein Trainer ersetzt (`0x0066E374`) oder ein Torwarttrainer (`0x0066E4E7`), nimmt das Spiel zuerst jemanden von der Liste.
  Nur wenn sie leer ist, entsteht der Notbehelf: gleicher Name, Jahrgang = Jahr − 35 und Kompetenz 2 (Torwarttrainer)
  bzw. Jahr − 30 und Kompetenz 2/1 (Trainer).

**Der Fehler:** Am Anfang von `0x0066DF9E` steht

```
0066DFCA  call 006FEB05        ; liefert einen Zeiger auf den Sondernamen des Spielers
0066DFCF  test eax,eax
0066DFD1  je   0066DFD8        ; weiter nur bei Zeiger 0
0066DFD3  jmp  0066E36F        ; sonst Ende
```

`0x006FEB05` gibt aber nie 0 zurück: ohne Sondernamen (Kennzeichen Bit 31 in 0x194 nicht gesetzt) liefert es die feste
Adresse `0x01BE0B18`. Die Routine endet deshalb immer sofort, **nie kommt jemand auf eine Warteliste**.

**Bestätigt an den Daten:** Beide Wartelisten sind in allen geprüften Spielständen von 2019 bis 2113 vollständig leer. In den
Spielständen 1–97 hat kein einziger der 1601 Personensätze je den Namen gewechselt (845 Trainer und 95 Torwarttrainer wurden
ersetzt, alle über den Notbehelf). Das Kennzeichen „Sondername“ trägt im Spielstand 383 kein Spieler.

**Jährliche Entwicklung (G im Code):**
- Torwarttrainer `0x006B6663`: unter 45 mit 50 % Chance +1 (höchstens 15); über 55 mit 20 % Chance −1 (nicht unter 5);
  über 65 und ohne Vertrag → Ersatz.
- Trainer (Schleife um `0x006B5B5B`): Ersatz ab 65 + Zufall 0–2, wenn ohne Vertrag.

**Zweiter Fehler, bisher ohne Wirkung:** `0x0066E374` übernimmt von der Trainer-Warteliste Name und Kompetenz, aber nicht das
Geburtsdatum (die Torwarttrainer-Routine tut es, `0x0066E5AC`). Ein nachgerückter Ex-Profi behielte das Alter des Vorgängers
und würde im nächsten Jahr gleich wieder ersetzt, falls er keinen Vertrag hat.

## Stand der Patches (15.11.2026)
Punkt 1 und 2 stehen als `trainer-nachwuchs` und `trainer-geburt` in `tools/a3patch.py` und sind in
`build/endpaket/anstoss3.exe` gebaut (acht exe-Patches, SHA-256 `0421D6B8…1EF34D`), beide Stellen mit `dumpbin` gegengelesen,
keine Sprungziele im umgeschriebenen Bereich. Seit 15.11.2026 im Spielordner eingebaut (Rückweg:
`build/anstoss3-sechs-patches.exe`). **Im Spiel ungeprüft.** Der Code hinter der Abfrage ist in 95 Spieljahren nie
gelaufen; gelesen wirkt er in Ordnung, ein Restrisiko bleibt bis zum Test. Punkt 3 ist nicht umgesetzt.
Test: über einen Saisonwechsel spielen, danach im Spielstand die Blöcke mit 3600 und 1800 Byte (Wartelisten) und
Namenswechsel in den 52-Byte-Personensätzen prüfen.

## Im Spiel bestätigt (15.11.2026, 22:47)
Der Nutzer hat vom Spielstand „kurz vor Saisonende“ (2113/14) aus mit der exe mit acht Patches erneut über den Saisonwechsel
gespielt. Vergleich `saves/patchtest/vorher.an3` → `saves/patchtest/test2.an3` (Cache `analyse/scan_test`):
- **Wartelisten gefüllt** (vorher und in allen älteren Spielständen leer): Trainer 3 wartend (Deutschland, England, Frankreich),
  Torwarttrainer 3 wartend (Deutschland 2, Frankreich 1), alle mit Kompetenz 12. Zwei weitere Plätze tragen nur noch Reste
  (erstes Namenswort 0 = Platz frei; die Ersetzroutine löscht nur dieses Wort).
- **Drei Trainer sind durch Ex-Profis ersetzt**, jeweils mit neuem Namen, eigenem Geburtsdatum und hoher Kompetenz
  (Trainer/Manager): Nr. 19 → 12/7, Nr. 32 → 8/13, Nr. 638 → 12/7. Die drei Spieler stehen im Spielstand vorher mit Stärke
  11–12, Jahrgang 2076–2078 und 362–415 Spielen. Das Geburtsdatum stimmt mit dem des Spielers überein (`trainer-geburt` wirkt).
- 21 Trainer und 2 Torwarttrainer wurden weiter per Notbehelf ersetzt. Die zwei Torwarttrainer sind in Italien, wo kein
  Ex-Torhüter wartete; die wartenden kommen bei der nächsten Ablösung in ihrem Land zum Zug.
- Kein Absturz beim Saisonwechsel (der Nutzer hat danach einige Wochen weitergespielt).
Je Saison also rund 9 Ex-Profis gegenüber rund 26 Ablösungen; der Bestand bessert sich langsam. Punkt 3 (Notbehelf anheben)
ist weiter offen und Entscheidung des Nutzers.

## Entscheidung des Nutzers (15.11.2026): Notbehelf NICHT anheben
Wörtlich: „will fehler korrigieren nicht das Ballancing ändern“. Der Startwert 2 ist Absicht der Entwickler für den Fall, dass
kein Ex-Profi wartet, und bleibt. Der Abschnitt unten ist nur noch Dokumentation der Rechnung. Als echter Fehler in Frage
kommt dagegen die Ausgleichsroutine (siehe „Dritter Fehler“): Sie stellt nur her, was das Spiel selbst vorsieht, und begrenzt
sich selbst (Anheben nur bei Schnitt unter 6, Senken bei Schnitt über 10).

**Patch `trainer-ausgleich` (gebaut und seit 15.11.2026 im Spielordner eingebaut, im Spiel ungeprüft; Rückweg
`build/anstoss3-acht-patches.exe`):** Die 180 Bytes ab VA 0x006B6057 (Dateioffset 0x2B6057)
sind kürzer neu geschrieben, mit dem fehlenden Schreiben (`add word ptr [esi+2],ax`); Rest `jmp 006B610B` und nop. Kein
Sprungziel von außen im Bereich, `esi` ist dort frei. Steht in `tools/a3patch.py`, gebaut in `build/endpaket/anstoss3.exe`
(neun exe-Patches, SHA-256 `B5EEE69C…6FBA8A70`), mit `dumpbin` gegengelesen. Prüfbar nach einem Saisonwechsel im Spielstand:
Trainer oder Manager **ab 45 Jahren**, deren höherer Wert um 1–2 gestiegen ist (ohne den Patch ist das für nicht ersetzte
Personen ausgeschlossen, Zuwachs gibt es sonst nur bis 44), etwa jede zehnte Person in Ländern mit Schnitt unter 6.

## Test3 (15.11.2026, 23:04, exe mit neun Patches) – `saves/patchtest/test3.an3`
Wieder vom Spielstand „kurz vor Saisonende“ aus gespielt (dritter Durchlauf desselben Saisonwechsels). Vergleich vorher → test3:
- `trainer-ausgleich` **wirkt (G):** 49 nicht ersetzte Trainer/Manager ab 46 Jahren sind beim höheren Wert gestiegen (26 × +1,
  23 × +2). In den Durchläufen ohne diesen Patch waren es 7 (nachher) und 0 (test2); die 7 stammen aus den Stufen der
  Routine, die schon vorher arbeiteten.
- 5 Trainer durch Ex-Profis ersetzt (Trainer/Manager 13/8, 9/14, 13/8, 8/13, 12/7), 29 per Notbehelf; Torwarttrainer 2 per
  Notbehelf (beide Italien). Wartend: 1 Trainer (Deutschland), 3 Torwarttrainer (Deutschland 2, Frankreich 1), alle 12.
- **Feld 0x0C im Personensatz = unter Vertrag (G):** genau 936 Personen ≠ 0 = 468 Vereine × (Trainer + Manager).
- Frei sind 505 Trainer/Manager, davon 29 mit Trainerwert ab 10, darunter drei der neuen Ex-Profis (38 J./13, 36 J./13,
  36 J./12). Einer der fünf (9/14) hat bereits einen Vertrag als Manager.
- Torwarttrainer: höchster Wert 9, nur 2 von 100 unter Vertrag (vermutlich die der zwei Manager).
- **Offen:** Der Nutzer findet in der Liste der verfügbaren Co-Trainer niemand Starken. Wie der Bildschirm seine Liste
  auswählt, ist nicht untersucht (rund 120 Aufrufstellen des Trainer-Lesers `0x006317C6`). Erst mit dem Nutzer klären, ob
  die drei freien Ex-Profis in seiner Liste stehen. Feld 0x2E ist bei allen Personen 0 (kein Co-Trainer-Kennzeichen).

## Wie die Listen „verfügbare Co-Trainer / Torwarttrainer“ entstehen (G im Code + an Test3, 15.11.2026)
Je aktivem Land gibt es zwei gespeicherte Marktlisten (Klasse mit höchstens **30 Einträgen** zu je 4 Byte: Nummer, Wert):
Trainer `0x008E27A0 + Land × 0x9C`, Torwarttrainer `0x008E2490 + Land × 0x9C`; im Spielstand die Blöcke mit 124 Byte
(Test3: 3207, 3209, … = Trainer Deutschland, England, Frankreich, Italien, Spanien; 3208, 3210, … = Torwarttrainer).
Die Bildschirme (Trainer/Co-Trainer `0x00486602` ff., Torwarttrainer `0x00592C40`) zeigen genau die Liste des **eigenen
Landes** des Vereins, nach Wert sortiert, ohne weiteren Filter.

**Trainer/Co-Trainer** – Neuaufbau `0x00409A3F` (aufgerufen aus `0x007719A6` und zweimal aus `0x0065E805`, beides im
Saisonstart-Zweig der Ereignisverteilung um `0x006DA52E`; genauer Zeitpunkt V):
1. Liste leeren (`0x0040AD6B`).
2. Alle Trainer des Landes in Nummernfolge durchgehen. Aufgenommen wird, wer keinen Vertrag hat (Feld 0x0C = 0) **und** als
   Trainer zählt (`0x00408D19`: Trainerwert > Managerwert + 4 oder Managerwert < 2).
3. `0x0040AE73`: Solange unter 30 Einträge, anhängen. Ist die Liste voll, ersetzt jeder weitere Kandidat mit 50 % einen
   zufälligen Platz (`rand(60) < 30`).
Es ist also eine Auslosung von 30 Plätzen, nichts ist für KI-Vereine reserviert; die KI bedient sich aus derselben Liste
(`0x00409588`, Auswahl nach Wertbereich `0x0040AF0C`).

Test3, Deutschland: 107 freie Trainer/Manager, 104 zählen als Trainer, 30 stehen in der Liste. Der beste Listeneintrag hat 9.
Nicht ausgelost wurden u. a. Ambrozej (38 J., 13/8, neuer Ex-Profi), Berbig (11), Rapolder (11), Ziegner (10). Chance je
Auslosung rund 29 % (frühe Nummern) bis 50 % (letzte Nummern). England: 74 Kandidaten; Cox (13) und Farke (12) nicht in der
Liste, fünf mit 10–11 sind drin. Ex-Profis anderer Länder sieht ein deutscher Verein nie.

**Torwarttrainer** – `0x00409BE0`: Die Liste wird nie geleert; jeder vertragslose Torwarttrainer des Landes wird ergänzt, falls
er fehlt. Ein Land hat nur 20 Torwarttrainer, die Liste fasst 30 → es wird niemand ausgeblendet. (Die gespeicherten
Listenwerte sind noch die von 2019, 15 … 1; angezeigt wird der aktuelle Wert der Person.) Deutschland in Test3: bester freier
Torwarttrainer 8, die zwei mit Vertrag haben 9 und 8.

Bewertung: Das ist gewollte Spielmechanik (Marktliste mit 30 Plätzen), kein Fehler. Kein Patch vorgeschlagen.

## Vorschlag zum Notbehelf (verworfen, nicht gebaut)
Zuwachsregeln im Code (G): Torwarttrainer +1 mit 50 % je Jahr bis 44, −1 mit 20 % ab 56 solange über 5 (`0x006B6663`).
Trainer/Manager: nur die höhere der zwei Kompetenzen, +1 mit 20 % je Jahr bis 44, −1 mit 20 % ab 61 (`0x006B5BEB` ff.).
Durchgerechnet (Simulation; Start 2 trifft den heutigen Bestand: Mittel 5,7, 49 % / 51 % / 0 %):

| Startwert | Torwarttrainer: Mittel, Anteil ab 8, Anteil 11–15 | Trainer: Mittel, Anteil ab 8, Anteil 11–15 |
|---|---|---|
| 2 (heute) | 5,7 – 15 % – 0 % | 4,3 – 4 % – 0 % |
| 4 | 7,5 – 51 % – 5 % | 6,3 – 23 % – 1 % |
| 5 | 8,5 – 69 % – 14 % | 7,3 – 43 % – 4 % |
| 6 | 9,5 – 84 % – 31 % | 8,3 – 66 % – 10 % |

Zum Vergleich Startdatenbank 2019 (Torwarttrainer): Mittel etwa 8,8, 38 % mit 11–15.
Empfehlung: Startwert **5** (Trainer: Hauptwert 5, Nebenwert 2). Fünf einzelne Bytes:
`0x26E5F2` 02→05 (Torwarttrainer), `0x26E4CB` 02→05, `0x26E4D2` 01→02, `0x26E4DB` 01→02, `0x26E4E2` 02→05 (Trainer/Manager).
Alternative mit Zufall beim Startwert: ginge nur mit Umschreiben von rund 100 Bytes der Ersetzroutine – größeres Risiko.

### Dritter Fehler im Umfeld (G im Code, kein Patch)
Die jährliche Ausgleichsroutine für Trainer und Manager je Land (`0x006B6000`) soll bei einem Schnitt unter 6 jede zehnte
Person um 1–2 anheben (Zweig `0x006B6021`–`0x006B610B`). Sie rechnet den Zuschlag aus und bucht ihn in Summe und Zählliste,
**schreibt ihn aber nicht in den Wert der Person** (im Gegenzweig für einen Schnitt über 10 steht das Schreiben bei `0x006B61E3`).
Die übrigen Stufen arbeiten: unter 10 Personen mit 5–9 → Schwache anheben, Starke senken; unter 5 Personen mit 10–15 →
Personen mit 6–9 anheben. Deshalb gibt es bei den Trainern je Land immer noch einige mit 10 und mehr. Für Torwarttrainer
gibt es keine solche Routine.

## Korrektur im Einzelnen
1. **Warteliste freischalten** (9 Bytes ab VA 0x0066DFCF, Dateioffset 0x26DFCF):
   `85 C0 74 05 E9 97 03 00 00` → `3D 18 0B BE 01 75 EC 90 90`
   (`cmp eax,01BE0B18h` / `jne 0066DFC2` = vorhandener Sprung zum Ende / 2 × nop). Spieler mit Sondernamen bleiben ausgeschlossen,
   alle anderen laufen weiter. Die exe hat keine Relocations, die feste Adresse ist unkritisch.
2. **Geburtsdatum bei Trainern übernehmen**: Block 0x0066E3CA–0x0066E409 (64 Bytes, kopiert die zwei Namensworte) kürzer
   schreiben und `mov edx,[Eintrag+8]` / `mov [Kopie+0Ah],edx` ergänzen (48 Bytes Code + 16 × nop, Dateioffset 0x26E3CA).
3. Optional, Entscheidung des Nutzers: Notbehelf anheben (Konstante 2 bei `0x0066E5EF`, 2/1 bei `0x0066E4C8`–`0x0066E4DF`).

Erwartete Wirkung (V): Im Spielstand 383 erfüllen derzeit etwa 12 Feldspieler und 5 Torhüter über 35 die Bedingungen. Bedarf je
Saison: etwa 3–4 Torwarttrainer und etwa 30 Trainer. Die Torwarttrainer würden also großteils, die Trainer zu etwa einem Drittel
durch Ex-Profis mit Kompetenz bis 12 ersetzt; der Rest bleibt Notbehelf. Der Bestand bessert sich nur langsam (etwa 3–4 von 100
Torwarttrainern je Saison). Nachweis nach einem Saisonwechsel direkt im Spielstand: Die Blöcke mit 3600 und 1800 Byte sind nicht mehr leer.

## Nebenbefund
Im Spielstand 383 stehen rund 60 Feldspieler im Alter von 102 bis 123 Jahren in Kadern: Es gibt Spieler, die nie aufhören (nicht untersucht).
**Berichtigt 19.11.2026: sehr wahrscheinlich kein Fehler.** Nachgesehen am Stand `vertrag-neu` (2114): Die Treffer ab 100 Jahren
haben ein Vertragsende zwischen 2025 und 2030 (z. B. Nr. 2172, 2264, 10671), es sind also alte, nie wiederverwendete
Spielersätze. Gefunden wurden sie über die 40 Worte ab 0x1D2 eines Blocks, ohne die Kaderanzahl zu beachten und auch in
Blöcken, die keine Vereine sind (Wettbewerbe); die Liste enthält hinter der Anzahl Reste. Bei den Vereinen der beiden
Manager steht keiner. Nicht mit der echten Kaderanzahl gegengeprüft.

## Offen
- Entscheidung des Nutzers zu den drei Punkten oben; danach Patches bauen und über einen Saisonwechsel prüfen.
- Ob der Bestand im Spielstand zusätzlich einmalig angehoben werden soll (Eingriff in den Spielstand, nicht in die exe).

## Die zwei anderen gemeldeten Fehler (nur aufgenommen, nichts belegt)
- Verletzungsmeldung ohne Art der Verletzung („fällt 7 Wochen aus“): Die Spieltexte liegen nicht im Klartext in exe oder `texte\`
  (Textlader 0x007B7CBA, Objekt 0x01C6BF98). Am schnellsten mit einem Beispiel: Spielstand direkt nach so einer Meldung + Name des Spielers.
- Jugendspieler lassen sich trotz Profivertrag nicht übernehmen oder stehen mit einem Häuschen im Kader und sind nicht einsetzbar:
  Beispiel nötig (Spielstand + Name). Hinweis aus dem Werkzeug: Im Spielstand 383 stehen 125 Spieler in zwei Kaderlisten zugleich (V: Zusammenhang offen).

### Häuschen bei einem getesteten Jugendspieler – Zwischenstand 18.11.2026 (Beispiel vom Nutzer)
Zwei Spielstände des Nutzers, unter neutralen Namen in `build/haus/` (nicht im Repository): `vorher.an3` und `haus.an3`
(entpackt in `build/haus/vorher/` und `build/haus/entpackt/`). Zwischen beiden wurden bei Manager B zwei Jugendspieler
„4 Wochen getestet“: Spieler 9517 (mit Häuschen) und Spieler 4164 (zum Vergleich).

**Gesichert (Spielstand):**
- Beide stehen danach in der Kaderliste (Vereinssatz 0x1D2) und haben Spielstand 0x24F = 0x10 (Probezeit-Merker,
  Laufzeit +0xB3) und 0x251 = 8 (Zustandsbyte +0xB6, Restdauer auf dem Anfangswert).
- Unterschied: Bei 9517 ist Spielstand 0x209 = 0x40 (vorher 0), bei 4164 bleibt es 0. Bei 9517 wechselt außerdem 0x332
  von 8 auf 0; bei 4164 wird Bit 30 des Flagworts gelöscht (vorher gesetzt), bei 9517 war es schon vorher 0.
- Vertragsende (Spielstand 0x13C, Wort): 9517 = 2113, 4164 = 2121. Im Kopf des Satzes von 9517 steht das Datum
  19.02.2113.

**Gesichert (Code):**
- Zuordnung beim Laden (`0x00636790` ff., `0x00636FC1` ff., `0x00637035` ff.; statischer Satz = Spielstand + 0x20):
  Spielstand 0x209 → Laufzeit +0x30 (Sperren-Byte), 0x13C → +0x94 = Vertragsende (untere 12 Bits) minus laufendes
  Jahr `0x00B5CBCA`, mindestens 0 (= Restjahre des Vertrags), 0x24F → +0xB3, 0x251 → +0xB6, 0x252 → +0xB7.
- `0x0062F66D(Wettbewerb, Spieler)` berechnet das Sperren-Byte +0x30 (Hülle `0x0062F609` über den ganzen Kader, zwölf
  Aufrufer, zweiter Aufrufer `0x00407AD4`). Dort: **Restjahre +0x94 = 0 und unteres Halbbyte von +0xB6 = 0 → +0x30 =
  0x40** (`0x0062F6BE`–`0x0062F6E1`); sonst 0 und danach die Sperren.
- **Berichtigt 18.11.2026 (zweite Sitzung):** Das Häuschen hängt in der Anzeige **nicht** am Sperren-Byte. Die Kaderliste
  (`0x0050B661` ff.) zeigt für +0x30 ≠ 0 nur die Sperren-Symbole 2 (gelb), 15 (Europapokal), 16 (Gelb-Rot) oder 3 (rot);
  `0x0062F9DE` prüft Bit 0x40 in den Bytes +0x36 / +0x3B (Gelb-Rot), nicht in +0x30. Das Häuschen ist Symbol 7 (Legende:
  Text 5181 „abwesend“ ist der siebte Eintrag) und wird bei `0x0050B795`–`0x0050B84A` gewählt: Verein ≠ 200, Wort +0x6A
  = 0, **Restjahre +0x94 ≤ 0 und `0x00706ACD` = 0** (Art in +0xB6 Bits 6–7 weder 1 noch 3, also kein Amateur). Die
  Probezeit (unteres Halbbyte von +0xB6, Merker +0xB3) wird dort nicht berücksichtigt.
- „4 Wochen testen“ (`0x004D8900` ff.): `0x0070DF0B` (in den Kader), dann `0x007069EB` (Restdauer 8, Merker 0x10), dann
  `0x00706BC8(0)` (Bit 30 löschen). Die wöchentliche Routine `0x0074CEB1` halbiert die Restdauer (8, 4, 2, 1) und beendet
  die Probezeit (`0x00706A45`, aus dem Kader `0x0070E01A`, zurück in die Jugend `0x0066AE46`, höchstens 20 Plätze).
  Sie läuft nur, wenn der Schalter `0x00B5CC04` („gerade geladen“, gesetzt in `0x00678F07`) 0 ist.

### Stand 18.11.2026, zweite Sitzung (Jugendspieler testen, Häuschen, vereinbarter Wechsel)
Spielstände in `build/haus/` (neutral benannt, jeweils entpackt im gleichnamigen Ordner): `vorher`, `haus` (Ordner
`entpackt`), `nachwechsel` (getestet, eine Woche nach Saisonwechsel), `vertrag` (9517 aus der Jugend heraus mit
Zweijahresvertrag), `vertrag-neu` (derselbe Verlauf nach dem Saisonwechsel). Achtung: Skripte, die die Blockdateien mit
`sorted(glob)` laden, zählen in Namensreihenfolge (block_1000 vor block_101) – solche Indizes sind keine Blocknummern.

**Einordnung des Nutzers (18.11.2026):** Das Häuschen ist ein Fehler, aber nicht das eigentliche Problem. Bekannt und
richtig ist, dass 18-Jährige ohne Profivertrag zur neuen Saison gehen. **Der eigentliche Fehler: Ein Jugendspieler hat
schon während der laufenden Saison einen Vertrag bei einem anderen Verein („Spielt nächste Saison bei …“), obwohl er
erst am Saisonende vereinslos wäre.** Früher beobachtet: Profivertrag nicht möglich oder später ignoriert.

**Gesichert (Code):**
- Sperren-Byte beim Testen: Der Dialog „Jugendspieler“ (`0x00441ACA`, Knopf `0x00441DC9`) ruft `0x00407ABB` (Sperren-Byte
  über `0x0062F66D`, dazu Rückennummer) auf, **bevor** `0x004D8BA3` die Probezeit einträgt; bei Restjahren 0 entsteht
  0x40 und bleibt bis zur nächsten Neuberechnung (`0x0062F609`). Der Weg über die Ja/Nein-Abfrage (`0x004D8900`, nur wenn
  Tageszähler `0x00B5CBD4` mod 7 = 6) rechnet nicht. Zuordnung Knopf ↔ Dialog aus gleichen Feldern (+0xED0 Verein,
  +0xED8 Spieler) geschlossen.
- Einsetzbarkeit `0x0069692B` (13 Aufrufer): 0, wenn Restjahre = 0 und kein Amateur (`0x00706ACD`); gleiche Regel wie
  die Anzeige. Nur `0x0062F66D` kennt die Ausnahme „Probezeit läuft“ (unteres Halbbyte +0xB6 ≠ 0).
- Wöchentlich `0x0074CEB1(Verein, Zwang, …)`: Art 1 (Amateur beim Profitraining) oder Merker +0xB3 & 0x10 (`0x00696B61`);
  bei Restdauer 1 oder Zwang: `0x00706A45`, aus dem Kader (`0x0070E01A`), Jugend `0x0066AE46` (nur bei < 20 Plätzen).
  Zwang = 1 bei Manager-Ereignissen (`0x005DFF60`, `0x006D9FA1`, `0x006DA24D`) und im Saisonwechsel für alle
  Manager-Vereine (`0x0074D52B`, Aufruf `0x006DB2C1`, **vor** der Wechsel-Abwicklung `0x006B3EE0` bei `0x006DB2F3`).
- Vertrag in der Probezeit (`0x0076B2BA`, Merker 0x10 erkannt bei `0x0076B3A7`): Restjahre werden für die Verhandlung
  auf 0 gesetzt; bei Erfolg +0xB6 = 0 (`0x0076B9FF`), **+0xB3 Bit 0x10 bleibt gesetzt** (`0x00706A45` hat nur die zwei
  Aufrufer in `0x0074CEB1`). Folgen nicht zu Ende gelesen.
- Feld „nächster Verein“: Laufzeit +0x70 (Land, Byte) / +0x72 (Verein, Wort) = Spielstand 0x12C / 0x12E; Anzeige
  `0x0055BBC2` (Steuerelement 0x12EE). Setzer: `0x0070CA69` (Aufrufer `0x00769C0D`, `0x0076D334`), `0x0070D3A6`
  (`0x0076C5E0`), `0x0070D5EF` (`0x006821CE`, `0x006829D9`); gelöscht in `0x0070DB4B`, `0x0070F7CF`, `0x0040EC50` und im
  Saisonwechsel je **Kaderspieler** (`0x0070665A`, Schleife `0x006B465F`). Welcher Setzer einen Jugendspieler trifft,
  ist **nicht geklärt**.
- Saisonwechsel: `0x0070F7CF` (Liste der Vereinbarungen, Objekt `0x01BE0B40`) sucht den Spieler im **Kader** des
  abgebenden Vereins (`0x0070F861`); nicht gefunden → Eintrag gestrichen. `0x004271FB`: Spieler mit mehr als 1 Restjahr
  bleibt (Eintrag gestrichen). Jugend: `0x006B4230` entfernt, wer vor dem 1.7.(neues Jahr − 18) geboren ist
  (`0x007068C9`). `0x0070665A` löscht bei jedem Kaderspieler das untere Halbbyte von +0xB6.

**Gesichert (Spielstände):**
- 9517 (geb. 8.7.2095): bis 19.02.2113 Jugend von Verein (14, 57), danach Uerdingen; Vertragsende 2113; Feld „nächster
  Verein“ = (67, 3) schon in `vorher`. Getestet: nach dem Saisonwechsel bei (14, 98) FC Augsburg, Ende 2119, Eintritt
  2.7.2114. Mit Zweijahresvertrag (21.5.2114): geblieben, Ende 2115, Feld nach dem Saisonwechsel gelöscht.
- Jugendliste Uerdingen (Anzahl in Byte 7 des 52-Byte-Blocks): vier Spieler vor dem 1.7.2096 geboren (12034, 9517, 79,
  4164) sind nach dem Saisonwechsel nicht mehr in der Jugend, in beiden Verläufen; 4164 seit 2.7.2114 bei (14, 7).
- Restjahre in der Jugend: vier von 15 haben 0 (180, 1755, 9517, 14743), die anderen 7–10.

**Jugendvertrag (Hinweis des Nutzers, 18.11.2026: zugekaufte Jugendspieler mit zu kurzem Vertrag?):**
- Restjahre = 10 setzen nur zwei Stellen: `0x004D8DA9` (Jugend-Bildschirm `0x004D86A3`, Zweig `0x004D8CAE`: Spieler mit
  Gehalt +0x88 = 0 → Dialog `0x005CB00F`, bei Zusage Gehalt aus `0x0066B648` und 10 Jahre) und `0x006C3D7F` (Routine
  `0x006C3BAB`, einziger Aufrufer `0x006C4526`: holt einen Spieler aus dem Vorrat `0x00B77338`; gehört er schon einem
  Verein (+6 ≠ 0), wird er aus dessen Jugend in die Jugend des Zielvereins umgetragen und bekommt Gehalt und 10 Jahre).
- Uerdinger Jugend in `vorher`: Gehalt 0 ↔ Restjahre 0 (180, 1755, 14743: nie ein Jugendvertrag); Gehalt > 0 ↔ Restjahre
  7–10 (zehn Jahre ab Vertrag, je Saison eins weniger – das erklärt die unterschiedlichen Jahre bei gleichem Alter).
  **Einzige Ausnahme: 9517 mit Gehalt 36 und Restjahren 0** – zugleich der einzige mit zweiter Station (von Verein
  (14, 57) am 19.02.2113) und der einzige mit gesetztem „nächstem Verein“. In allen Jugendlisten des Spielstands hat
  kein anderer Jugendspieler eine zweite Station.
- **Ursache gefunden (18.11.2026, vom Nutzer nachgestellt: drei 17-Jährige über die Maske „Jugendspieler ohne Vertrag“
  aus anderen Vereinen geholt, alle drei beim Testen mit Häuschen):** Die Abwerbe-Routine des Managers `0x004D7038`
  (Zweig `0x004D766E`: Dialog `0x005CB00F`, Gehalt aus `0x0066B648`) trägt den Spieler aus der fremden Jugend aus
  (`0x0066AEA3`) und in die eigene ein (`0x0066AE46`), schreibt das Gehalt (`0x004D7793`) und die Station
  (`0x00707BD4`, `0x00707C10`), **setzt aber die Restjahre +0x94 nicht**. Die zwei anderen Wege setzen direkt nach dem
  Gehalt 10 Jahre (`0x004D8D9F`/`0x004D8DA9`, `0x006C3D75`/`0x006C3D7F`). Der abgeworbene Spieler hat also Gehalt, aber
  0 Restjahre – genau der Zustand von 9517. Korrektur `jugend-abwerben-vertrag` (Testfassung `build/kandidat-1.46`, vom Nutzer
  am 18.11.2026 im Spiel bestätigt: nach dem Abwerben kein Häuschen mehr beim Testen; nicht im Installer):
  die 15 Bytes `0x004D779A`–`0x004D77A8` (Aufruf der Hülle `0x00707BD4`) ersetzen durch `mov byte ptr [ecx+94h],0Ah`,
  `call 0070429C` (ecx = Spieler, keine Stapelargumente) und drei `nop`.
- Früherer Stand der Frage: auf welchem Weg 9517 nach Uerdingen kam (nicht über `0x006C3BAB`, das hätte 10 Jahre gesetzt) und wo
  dabei Restjahre 0 und der nächste Verein entstanden. Kandidaten: die Verhandlungs-Routinen `0x0076BB38` ff.
  (Restjahre = 0 bei `0x0076BE42`, `0x0076C106`, `0x0076C363`, `0x0076C8B2`; Setzer `0x0070D3A6` bei `0x0076C5E0`).

**Offen:** woher das Feld bei 9517 stammt (ein Eintrag in der Vereinbarungsliste ließ sich im Spielstand nicht
zuordnen; Blockformat der Liste unbekannt); Stelle der Meldung „wechselt bereits“ beim Vertragsangebot im Profikader
und warum sie aus der Jugend heraus nicht kommt; Spielstand 0x332.

**Folgerung vom ersten Zwischenstand (in Teilen überholt, siehe Berichtigung oben):** Das Häuschen bekommt ein getesteter Jugendspieler, dessen Vertrag im
laufenden Jahr endet (Restjahre 0); Spieler 4164 mit Vertragsende 2121 bekommt es nicht. Nach der Regel dürfte das
Bit bei laufender Probezeit (Restdauer ≠ 0) nicht gesetzt sein – im Spielstand sind aber beide gesetzt. **Offen:** an
welcher Stelle das Bit beim Testen gesetzt wurde, warum es stehen bleibt, was am Ende der Probezeit mit einem Spieler
ohne Restjahre geschieht und was 0x332 bedeutet.

