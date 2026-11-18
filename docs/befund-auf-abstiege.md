# Befund: Zähler für Auf- und Abstiege (Rekordaufsteiger / Rekordabsteiger), 15.11.2026

Grundlage: 97 Spielstände (`analyse/scan`), verglichen jeweils letzter Spielstand einer Saison mit dem der nächsten.
**G** = an Daten oder im Code belegt, **V** = Vermutung.

## Tabellen (G)

Zwei Blöcke direkt vor „Beste Mannschaft“ im Spielstand, Index = Verein (Deutschland 0–107, danach England, Frankreich,
Italien, Spanien je 26; 212 von 268 Plätzen belegt):

| Block | Speicherobjekt | Satz | Felder (int16) |
|---|---|---|---|
| Aufstiege | 0x00B06CD8 | 8 Byte | gesamt, in Liga-Index 0, in Liga-Index 1, in Liga-Index 2 |
| Abstiege | 0x00B07558 | 10 Byte | gesamt, aus Liga-Index 0, 1, 2, 3 |

Schreibroutinen: Aufstieg 0x00726382, Abstieg 0x007264BF (Argumente Land, Verein, Liga-Index). Beide erhöhen immer „gesamt“
und danach das Feld zum Liga-Index. Die Aufstiegsroutine kennt nur die Indizes 0, 1, 2; bei Index 3 erhöht sie nur „gesamt“.
Aufrufer: 0x006B6A33 (Aufstieg) und 0x006B6B22 (Abstieg), für Deutschland aus der Saisonabschluss-Routine um 0x006AE400–0x006AF2E5.
Dort ist Liga-Index 2 = Regionalliga Nord (Kandidatenliste [ebp-0x3EE0]) und 3 = Regionalliga Süd ([ebp-0x4108]).

## Auffälligkeiten

### 1. Deutschland: „Aufstiege gesamt“ ist größer als die Summe der Spalten (G an Daten)

Jede Saison, ohne Ausnahme in allen 28 verglichenen Saisonwechseln (2019–2047):

| Vereine je Saison | Änderung (gesamt, Liga 1, Liga 2, Liga 3) | Deutung |
|---|---|---|
| 3 | +1, +1, 0, 0 | Aufstieg in die 1. Liga – stimmt |
| 2 | +2, 0, +1, +1 | Aufstieg in die 2. Liga, **doppelt gezählt**, zusätzlich ein Aufstieg „in Liga 3“ |
| 2 | +2, 0, +1, 0 | Aufstieg in die 2. Liga, **doppelt gezählt** |
| 4 | +1, 0, 0, +1 | Aufstieg in die Regionalliga Nord – stimmt |
| 4 | +1, 0, 0, 0 | Aufstieg in die Regionalliga Süd – **in keiner Spalte** |

Summe: gesamt +19 je Saison, die Spalten ergeben +13. Stand Spielstand 383: gesamt 1797, Spalten 282 + 376 + 574 = 1232.

Ursachen:
- **Regionalliga Süd fehlt (G im Code):** 0x00726382 hat für Liga-Index 3 kein Feld (Abfragen bei 0x007263F4, 0x00726439, 0x0072647C
  enden bei Index 2). Der Datensatz hat auch nur Platz für drei Spalten.
- **Doppelzählung der Aufsteiger in die 2. Liga (V zur Ursache):** Die vier Aufsteiger bekommen einen Aufruf mit Liga-Index 1
  (0x006AE792 ff.) und offenbar noch einen mit Index 2 oder 3. In Frage kommt die Auffüllschleife 0x006AF0E0–0x006AF2F7, die
  Vereine nachrückt, bis die Regionalliga 36 Vereine hat. Welche Vereine dort in den Kandidatenlisten stehen, ist nicht nachvollzogen.

Kein Widerspruch dagegen: Kein Verein hat in einer Saison zugleich einen Auf- und einen Abstieg, kein Zähler fällt je.

### 2. Spanien: Abstiege aus der 1. Liga stehen in der Spalte „aus Liga 2“ (G an Daten)

Je Saison steigen im Ausland 13 Vereine auf (alle in Spalte „Liga 1“) und 13 ab. Bei England, Frankreich und Italien stehen die
Abstiege in Spalte „aus Liga 1“, bei allen spanischen Vereinen in Spalte „aus Liga 2“ (z. B. Espanyol, Alavés, Albacete 2038/39).
Ursache nicht untersucht (V: Liga-Index, den der Aufrufer 0x006915D9 bzw. die Auslandsroutine um 0x00691000 übergibt).

### 3. Deutschland: Abstiege aus beiden Regionalligen stehen gemeinsam in einer Spalte (G an Daten)

Abstiege je Saison: 3 aus Liga 1, 4 aus Liga 2, 6–8 in der dritten Spalte, vierte Spalte immer 0. Anders als bei den Aufstiegen
wird hier nicht nach Nord und Süd getrennt. Das ist in sich stimmig, passt aber nicht zur Zählweise der Aufstiege.

## Ursachen im Code (Nachtrag, alle drei G)

### Zu 1a: Doppelzählung der Aufsteiger in die 2. Liga

Derselbe Aufstieg wird an zwei Stellen gemeldet, beide Male mit Statistik-Flag 1 (viertes Argument von 0x006B6A33; nur dann
ruft 0x006B6A33 die Zähler 0x00634D9C und 0x00726382 sowie 0x006143D2 auf):

1. 0x006AE792–0x006AE7E3: die vier Aufsteiger (aus 0x006B3A90(0…3)) mit Liga-Index **1** – richtig.
2. 0x0069139B in der Routine 0x0069128A, die je eine Regionalliga abarbeitet (Aufrufe 0x006AE8E1 mit Liga-Index 2 und 0x006AE916
   mit 3): Für die ersten `[Liga+0x22]` aufstiegsberechtigten Vereine der Abschlusstabelle wird 0x006B6A33 mit dem **eigenen**
   Liga-Index der Regionalliga (2 oder 3) aufgerufen. Der Listeneintrag wird gebraucht (0x00680569 schließt diese Vereine danach
   aus der neuen Regionalliga aus), die Statistik zählt dabei aber ein zweites Mal: Nord → Spalte „Liga 3“, Süd → nur „gesamt“.

Das passt exakt zu den Daten: je Saison 2 Vereine mit (+2, 0, +1, +1) und 2 mit (+2, 0, +1, 0).
Mögliche Korrektur: Statistik-Flag an Stelle 2 auf 0 – VA 0x0069137D `6A 01` → `6A 00` (Dateioffset 0x29137E: 01 → 00).

### Zu 1b: Regionalliga Süd ohne Spalte

0x00726382 prüft den Liga-Index nacheinander auf 0, 1, 2 (0x007263F4, 0x00726439, 0x0072647C `83 F8 02 75 38`) und tut bei 3 nichts.
Die Abstiege aus beiden Regionalligen werden dagegen fest mit Index 2 gemeldet (0x006915D3 `push 2`).
Mögliche Korrektur: Index 2 **und** 3 in die dritte Spalte – VA 0x0072647F `75` → `7C` (jne → jl; Dateioffset 0x32647F).

### Zu 2: Spanien

Die Spanien-Routine 0x006B1F12 lädt Liga-Index 0 (`push 0 / push 3Fh / call 0x00692045`), trägt Absteiger mit Index 0 in die Liste
ein (0x006B201C `push 0`, 0x006B6BBC) und meldet den Abstieg direkt danach mit Liga-Index **1** (0x006B2042 und 0x006B208C, je `6A 01`).
Aufstiege meldet sie mit Index 0 (0x006B21C1). Der Block entspricht dem der deutschen 2. Liga (0x006AE61A–0x006AE6B1) – offenbar
von dort übernommen, ohne den Index anzupassen. Die allgemeine Auslandsroutine 0x006B2212 nimmt Index 0 (0x006B233F, 0x006B2392).
Mögliche Korrektur: beide `6A 01` → `6A 00` (Dateioffsets 0x2B2043 und 0x2B208D).

### Wirkung der Korrekturen

Sie greifen erst beim nächsten Saisonwechsel und ändern nur künftige Zählungen. Erwartung danach für Deutschland: gesamt +15 je
Saison, Spalten +3 / +4 / +8. Die bisher zu hoch gezählten Werte im Spielstand bleiben stehen. Nachweis wie bei „Beste Mannschaft“:
Spielstand vor und nach einem Saisonwechsel vergleichen (`tools/a3verlauf.py` bzw. die Tabellen direkt).
Nebenwirkung von 1a: Auch 0x00634D9C (Vereinstabelle bei 0x00AE5C97-Index, vermutlich Vereinschronik) und 0x006143D2 werden für
diese Vereine nur noch einmal aufgerufen – gewollt, aber im Spiel nicht geprüft.

## Nachtrag 15.11.2026: doppelte Vereine in der Anzeige „Aufsteiger 2. Liga / 3. Liga“ (G im Code, Patch gebaut, ungetestet)
Meldung aus dem Forum (anstoss-juenger.de, topic 7313, 30.10.2026). Ursache ist dieselbe Stelle wie bei 1a.

Das Ergebnisobjekt des Saisonabschlusses (lokal in der Deutschland-Routine, `[ebp-0x360]`) führt je Liga-Index eine Liste mit
**höchstens 4 Vereinen**: Absteiger (Anzahl +0x110, Liste +0x124), Aufsteiger (Anzahl +0x118, Liste +0x144), eine dritte Liste
(+0x120 / +0x164). `0x006B6A33(Objekt, Liga-Index, Verein, Statistik)` trägt einen Aufsteiger ein, `0x00680569` fragt die Liste ab.
Im Spielstand ist das Objekt nicht enthalten, die Anzeige lässt sich also nur im Spiel prüfen.

Reihenfolge in der Saisonabschluss-Routine:
1. `0x006AE792`–`0x006AE7E3`: die vier Aufsteiger in die 2. Liga → Liste 1 (richtig).
2. `0x006AE8E1` / `0x006AE916` → `0x0069128A` je Regionalliga: die ersten zwei aufstiegsberechtigten Vereine der Abschlusstabelle
   werden noch einmal eingetragen, in die Liste des **eigenen** Liga-Index (2 bzw. 3). Gebraucht wird das nur für die Abfrage
   bei `0x00691440`, die diese Vereine aus der neuen Regionalliga herauslässt.
3. `0x006AEFFC` ff.: die echten Neulinge der Regionalligen → Liste 2 bzw. 3.

Folge: In „Aufsteiger 3. Liga“ stehen je Regionalliga zuerst die zwei Vereine, die in die 2. Liga aufgestiegen sind, und von
den vier Neulingen passen nur noch zwei in die Liste.

Patch `aufsteiger-liste` (zwei Stellen, je `66 8B 4D 14 51` → `6A 01 90 90 90`):
- `0x00691392` (Dateioffset 0x291392): Eintragen mit Liga-Index 1 statt dem eigenen. Liste 1 ist dort schon voll, es passiert nichts.
- `0x00691438` (Dateioffset 0x291438): Nachschlagen in Liste 1 statt in der eigenen.
Begründung, dass Liste 1 dieselben Vereine enthält: In allen 28 verglichenen Saisonwechseln waren die doppelt gemeldeten
Vereine genau die vier Aufsteiger in die 2. Liga (zwei je Regionalliga). Die Nachbarroutinen `0x006916D0` und `0x006918AB`
fragen ebenfalls Liste 1 ab.
**Risiko:** Der Patch greift in die Zusammenstellung der neuen Regionalligen ein. Test nach einem Saisonwechsel: Ligagrößen
unverändert, kein Verein in zwei Ligen, die vier Aufsteiger nicht mehr in der Regionalliga; im Spiel die Übersicht ansehen.
Gebaut in `build/kandidat/anstoss3.exe`.

**Im Spiel bestätigt (16.11.2026, `saves/patchtest/test4-auto.an3` → `test4.an3`, exe `5FA6A60B…`):**
- Bildschirmfoto des Nutzers: „Aufsteiger 2. Liga“ Alemannia Aachen, FSV Zwickau, FSV Frankfurt, SV Waldhof Mannheim;
  „Aufsteiger 3. Liga“ Wuppertaler SV, SV Babelsberg 03, SG Wattenscheid 09, SC Fortuna Köln – keine Überschneidung, vier Neulinge.
- Spielstand der neuen Saison: alle acht Ligen mit unveränderter Größe (18/18/18/18/20/18/18/20), kein Verein in zwei Ligen.
  Die vier Aufsteiger stehen in der 2. Bundesliga und in keiner Regionalliga mehr. Regionalliga Nord: 6 raus (2 auf, 4 ab),
  6 rein (1 Absteiger, 4 Neulinge, 1 Wechsel aus der Süd-Staffel); Regionalliga Süd: 7 raus, 7 rein.

## Nicht geprüft

- Wie die Bildschirme „Rekordaufsteiger“ und „Rekordabsteiger“ die Felder anzeigen (welche Spalten sie zeigen).
- Ob die Doppelzählung auch Folgen außerhalb der Statistik hat.
- Die übrigen Tabellen dieser Gruppe: zwei Top-20-Listen mit Spielern (12 Byte je Eintrag, absteigend sortiert, keine Doppelungen,
  Einträge bleiben über Jahrzehnte erhalten), 20 Einträge zu 24 Byte mit Geldbeträgen (vermutlich Supertransfers),
  30 Einträge zu 20 Byte mit Kommazahlen je Verein, ein Block mit 3924 Byte. Aufbau nur grob erkannt, keine Doppelungen gefunden.

## Stand der Patches

Die Ursachen sind im Code belegt, die Korrekturen sind in `tools/a3patch.py` als `aufstieg-doppelt`, `aufstieg-rl-sued` und
`abstieg-spanien` eingetragen. Seit 15.11.2026 sind alle drei zusammen mit `beste-mannschaft` gebaut (`build/anstoss3.exe`, SHA-256 `3FAA39C6…5CFA`) und im
Spielordner eingebaut.

**Im Spiel nachgewiesen (15.11.2026):** Saisonwechsel 2113/14 → 2114/15 mit den Patches (`saves/patchtest/vorher.an3`, `nachher.an3`).
Deutschland Aufstiege: gesamt +15, Spalten +3 / +4 / +8 (3 Vereine (1,1,0,0), 4 Vereine (1,0,1,0), 8 Vereine (1,0,0,1)); kein Verein
mit +2. Abstiege Deutschland +15 / 3 / 4 / 8 / 0. Spanien: 3 Absteiger mit (1,1,0,0,0), also Spalte „aus Liga 1“.
