# Befund: „Erfolgreichste Trainer“ – Champions League und Europ. Supercup fehlen bei menschlichen Managern

Stand 15.11.2026. Nutzer hat der Aufnahme ins Endpaket zugestimmt. Patch `trainer-eps` steht in `tools/a3patch.py` und ist in
`build/endpaket/anstoss3.exe` gebaut (mit `dumpbin` gegengelesen). Seit 15.11.2026 im Spielordner eingebaut.

**Im Spiel bestätigt (15.11.2026, `saves/patchtest/`):** Manager B steht nach einem Titelgewinn mit EPs 30 (4 Europapokale + 26
Champions League) und Sonstige 77 (54 + 23 Europ. Supercups) in der Liste, vorher 4 / 53. Die fehlenden Titel kommen also
rückwirkend dazu. Der Eintrag wird nur beim Gewinn eines Titels neu geschrieben: Manager A gewann im Testzeitraum nichts und
steht noch mit 1 / 59 da (erwartet bei seinem nächsten Titel: 27 / 83). Der Eintrag entsteht, bevor der Zähler des gerade
gewonnenen Titels erhöht ist; daher die Differenz von 1 bei der zuletzt gewonnenen Titelart (altes Verhalten des Spiels).

**Eintrag von Manager A bestätigt (16.11.2026, `test5.an3`):** Nach dem Gewinn des Ligapokals steht er mit Meister 41, Pokale 21,
EPs 27 (1 + 26 CL), Sonstige 84 (Liga-/Supercup 34 + Weltpokal 23 + EM 2 + WM 2 + Europ. Supercup 23) in der Liste – genau
die Zähler, einschließlich des gerade gewonnenen Titels. Der Nutzer: „die Werte für mich stimmen nun perfekt“.

## Nebenbefund: Liste liegt beim zuletzt gewonnenen Titel um 1 zurück (G im Code, 15.11.2026; kein Patch gebaut)
Beispiel: Manager B gewann 2113/14 den Pokal, Zähler Pokalsiege 17 (richtig), Liste 16.
Beide Aufrufer der Titelvergabe arbeiten in dieser Reihenfolge auf einer lokalen Kopie des Erfolgssatzes (`0x006311DA`):
1. `0x006B5497` (Manager, Kopie, Verein, Titelart): trägt den Titel in die Einzelliste ein und ruft am Ende `0x00725FBA`
   → Listeneintrag „Erfolgreichste Trainer“ aus den Zählern, **die den neuen Titel noch nicht enthalten**.
2. `0x006B583A` (Kopie, Titelart): erhöht erst danach genau einen Zähler (Sprungtabelle `0x006B59BD`), sonst nichts.

Aufrufstellen: `0x006B4EE1`–`0x006B4F10` (Titelart 2 fest) und `0x006B51DC`–`0x006B520E` (Titelart aus `[ebp+0Ch]`).
Korrektur `trainer-reihenfolge` (15.11.2026 gebaut, ungetestet): an beiden Stellen die zwei Aufrufblöcke getauscht (erst
`0x006B583A`, dann `0x006B5497`), Bytes gleich, nur die zwei Sprungweiten der Aufrufe neu berechnet; keine Sprungziele im
Bereich. `0x006B5497` liest die Zähler selbst nicht, nur Listenlänge +0x26, Summe +0x28 und die Einzelliste.
Steht in `tools/a3patch.py`, gebaut in `build/kandidat/anstoss3.exe`.
**Im Spiel bestätigt (16.11.2026):** Der Nutzer sieht die Pokalsiege an beiden Stellen gleich; im Spielstand `test4.an3`
stehen bei Manager B Zähler und Liste auf Meister 38 / Pokale 17 (im Durchlauf ohne den Patch, `nachher.an3`: Zähler 17, Liste 16).

## Was der Nutzer beobachtet hat
Spalte „EPs“ zeigt bei Manager A 1 und bei Manager B 4, obwohl beide 26-mal die Champions League gewonnen haben.

## Ursache (G – im Code gelesen und an den Zählern von Spielstand 383 bestätigt)
Die Liste liegt je Land im Speicher bei `0x00AF7450 + Abschnitt × 0x37C` (Liste ab +0x20, 20 Einträge × 42 B:
+0 Nr., +2 Name, +0x20 Meister, +0x22 Pokale, +0x24 EPs, +0x26 Aufstiege, +0x28 Sonstige).
Sortiert wird nach Meister + Pokale + EPs (`0x00725DC6`), dann Meister, dann Summe aller fünf (`0x00725DEA`).

Es gibt zwei getrennte Wege, einen Eintrag zu füllen:

| | Computertrainer (`0x006B53D4`, Sprungtabelle `0x006B5473`) | Menschlicher Manager (`0x00725FBA`) |
|---|---|---|
| Meister | Titelart 1 | Zähler 0 (Meisterschaften) |
| Pokale | Titelart 4 | Zähler 1 (Pokalsiege) |
| **EPs** | Titelarten **6 (Champions League)**, 7, 8 (Europa League) | **nur Zähler 6 (Europapokale)** |
| Sonstige | Titelarten 5 (Supercup), **9 (Europ. Supercup)**, 10 (Weltpokal), 11, 12 | Zähler 3 (Liga-/Supercup) + 10 (Weltpokal) + 13 (EM) + 15 (WM) |
| Aufstiege | Titelart 2 | Zähler 11 |

Beim menschlichen Manager fehlen also **Zähler 4 (Champions-League-Siege)** in „EPs“ und **Zähler 9 (Europ. Supercups)** in
„Sonstige“. Beim Computertrainer zählen beide mit. Das ist ein Fehler im Spiel, keine Absicht.

Probe an Spielstand 383 (Zähler aus dem 2132-Byte-Block des Managers):

| | Zähler 0, 1, 6 | 3 + 10 + 13 + 15 | Liste des Spiels | fehlt |
|---|---|---|---|---|
| Manager A | 41, 21, 1 | 33 + 23 + 2 + 2 = 60 | 41 / 21 / 1 / Sonstige 59 | 26 CL-Siege, 23 Europ. Supercups |
| Manager B | 37, 16, 4 | 29 + 18 + 4 + 3 = 54 | 37 / 16 / 4 / Sonstige 53 | 26 CL-Siege, 22 Europ. Supercups |

„Sonstige“ liegt in der Liste jeweils um 1 unter der Rechnung. Vermutung (V): Die Liste wird nicht bei jedem Titel neu
geschrieben, sondern zu festen Zeitpunkten; ein Supercup der laufenden Saison ist im Zähler schon enthalten, in der Liste noch nicht.

## Stelle im Code
`anstoss3.exe` 1.40, `0x00725FF0`–`0x00726040` (Dateioffset `0x325FF0`, 81 Bytes). Original:

```
8b 45 0c 66 8b 08 66 89 4d f4 8b 55 0c 66 8b 42 02 66 89 45 f6 8b 4d 0c 66 8b 51 0c 66 89 55 f8
8b 45 0c 0f bf 48 14 8b 55 0c 0f bf 42 06 03 c8 8b 55 0c 0f bf 42 1e 03 c8 8b 55 0c 0f bf 42 1a
03 c8 66 89 4d fc 8b 4d 0c 66 8b 51 16 66 89 55 fa
```

Der Bereich lädt den Zeiger auf die Zähler vor jedem Zugriff neu und lässt sich deshalb ohne Sprung kürzer schreiben.

## Patch `trainer-eps` (gebaut, nicht im Spiel getestet)
EPs = Zähler 6 + Zähler 4, Sonstige zusätzlich + Zähler 9. Gleiche Länge, Rest mit `90` aufgefüllt:

```
8b 45 0c          mov eax,[ebp+0Ch]      ; Zeiger auf die Zähler
66 8b 08          mov cx,[eax]           ; Meister
66 89 4d f4       mov [ebp-0Ch],cx
66 8b 48 02       mov cx,[eax+2]         ; Pokale
66 89 4d f6       mov [ebp-0Ah],cx
66 8b 48 0c       mov cx,[eax+0Ch]       ; Europapokale
66 03 48 08       add cx,[eax+8]         ; + Champions-League-Siege   (neu)
66 89 4d f8       mov [ebp-8],cx
66 8b 48 14       mov cx,[eax+14h]       ; Weltpokale
66 03 48 06       add cx,[eax+6]         ; + Liga-/Supercup
66 03 48 1e       add cx,[eax+1Eh]       ; + WM
66 03 48 1a       add cx,[eax+1Ah]       ; + EM
66 03 48 12       add cx,[eax+12h]       ; + Europ. Supercups         (neu)
66 89 4d fc       mov [ebp-4],cx
66 8b 48 16       mov cx,[eax+16h]       ; Aufstiege
66 89 4d fa       mov [ebp-6],cx
90 × 19
```

Erwartung nach dem Patch (V, erst im Spiel zu prüfen): Der Eintrag wird aus den Gesamtzählern neu gebildet, die fehlenden Titel
kämen also beim nächsten Schreiben der Liste rückwirkend dazu: Manager A EPs 27, Manager B EPs 30.

Offen: wann genau `0x00725FBA` aufgerufen wird (Aufrufer `0x006B5801`), und ob Zähler 9/10 wirklich Europ. Supercup/Weltpokal
sind (Bezeichnungen aus dem Bildschirm „Trainererfolge“ abgeleitet; die Rechnung oben passt nur mit Zähler 10 in „Sonstige“).
