# Fehler: Statistik „Historisches → Beste Mannschaft“ zeigt nur Doppelungen (15.11.2026)

## Befund (G = im Code gelesen und am Spielstand bestätigt)

- **Anzeige** 0x004665DD: holt per 0x007215E7 eine Kopie von 200 Byte ab 0x00B08010 (20 Einträge à 10 Byte)
  und gibt die Zeilen korrekt indiziert aus. Die Anzeige ist nicht die Ursache. **G**
- **Daten** (Objekt 0x00B07FF0, Daten ab +0x20, im Spielstand ein eigener 200-Byte-Block):
  Eintrag = `int16 Saison, u8 Land, u8 –, int16 Verein, int16 Stärkesumme, int16 Spielerzahl`.
  In `Karriere383.an3` sind **alle 20 Einträge identisch**: Saison 2103, Borussia M'gladbach, 363 / 32. **G**
- **Fortschreibung** 0x00726660 (aufgerufen je Verein, z. B. aus 0x00725569), Argumente Verein und Stärkesumme:
  1. `idx = aktuelles Jahr − Startjahr`.
  2. Ab der 21. Saison (`idx ≥ 20`): Wenn `Eintrag[19].Saison ≠ aktuelles Jahr`, werden die Einträge 1…19 um eins nach vorn geschoben
     und der letzte Eintrag soll für die neue Saison geleert werden; danach `idx = 19`.
  3. Ist die Stärke größer als `Eintrag[idx].Stärke`, wird `Eintrag[idx]` mit Saison, Land, Verein, Stärke, Spielerzahl überschrieben.

## Ursache (G)

Das Leeren in Schritt 2 trifft den falschen Eintrag:

```
007266F1  mov  edx,[ebp-8]            ; Schleifenzähler, nach der Schleife = 20
007266F4  imul edx,edx,0Ah
007266FA  mov  word ptr [eax+edx+26h],0   ; setzt Eintrag[20].Stärke = 0
```

Gemeint ist `Eintrag[19]`. `Eintrag[20]` liegt hinter der Tabelle (Objekt+0xEE = 0x00B080DE, schon im Kopf des nächsten Objekts 0x00B080D8).

Folge:
- `Eintrag[19]` behält Saison und Stärke des Vorjahres. Ein schwächerer Saisonbester ersetzt ihn nicht.
- Weil `Eintrag[19].Saison` dann nie dem aktuellen Jahr entspricht, wird bei **jedem** Aufruf (also für jeden Verein) erneut geschoben.
- Nach wenigen Aufrufen stehen in allen 20 Zeilen Kopien desselben Rekords – genau das Bild im Spiel.
- Der Fehler tritt erst ab der 21. Saison auf; die ersten 20 Saisons werden richtig geführt.

## Korrektur (Vorschlag, nicht angewendet)

Ein Byte in `anstoss3.exe` 1.40 (SHA-256 `89B88EF5…6B2A`):

| VA | Dateioffset | alt | neu | Wirkung |
|---|---|---|---|---|
| 0x007266FE | 0x003266FE | `26` | `1C` | `mov word ptr [eax+edx+1Ch],0` → setzt `Eintrag[19].Stärke = 0` |

Die Befehlslänge bleibt gleich (`66 C7 44 10 1C 00 00`).

Nicht rückgängig zu machen: Die überschriebenen Einträge früherer Saisons im Spielstand sind verloren.
Nach der Korrektur füllt sich die Tabelle ab der nächsten Saison wieder richtig, die alten Doppelungen wandern nach und nach heraus.

## Im Spiel bestätigt (15.11.2026)
Saisonwechsel 2113/14 → 2114/15 mit dem Patch (`saves/patchtest/vorher.an3`, `nachher.an3`): vorher 20-mal „2103 Borussia
M'gladbach 363/32“, nachher Zeilen 1–19 unverändert und Zeile 20 = „2113 Borussia M'gladbach 292/27“.

## Zweiter Fehler: Die Anzeige lässt ab der 21. Saison die letzte Zeile weg (G, 15.11.2026)
Beobachtung des Nutzers nach dem Saisonwechsel: Der Bildschirm zeigt weiter nur „Gladbach 2103/04“, die neue Saison fehlt.
Im Spielstand steht sie aber (Eintrag 20). Der Satz oben „Die Anzeige ist nicht die Ursache“ gilt nur für die Doppelungen.

```
004666BF  movsx edx,[00B5CBCA] / movsx eax,[00B5CBCC] / sub edx,eax   ; n = aktuelles Jahr − Startjahr
004666D7  cmp  ecx,14h / jl 004666E2
004666DC  mov  word ptr [ebp-0Eh],13h                                  ; n ≥ 20 → n = 19
004666FD  Schleife i = 0 … n−1                                         ; zeigt also höchstens Eintrag 0 … 18
```

Der Eintrag einer Saison wird erst beim Saisonwechsel geschrieben (97 Spielstände: der Eintrag der laufenden Saison ist während
der Saison immer leer). In den ersten 20 Saisons ist Eintrag n−1 deshalb die zuletzt beendete Saison und wird gezeigt. Ab der
21. Saison steht die zuletzt beendete Saison in Eintrag 19, die Anzeige hört aber bei Eintrag 18 auf: Sie hinkt eine Saison hinterher.

Korrektur `beste-mannschaft-anzeige` in `tools/a3patch.py`: VA 0x004666DC `66 C7 45 F2 13 00` → `… 14 00` (Dateioffset 0x666E0:
13 → 14). Die lokale Kopie hat 200 Byte = 20 Einträge, die Schleife bleibt innerhalb. Gebaut in `build/endpaket/anstoss3.exe`
(sechs Patches, SHA-256 `CD656CB5…5669CA`), mit `dumpbin` gegengelesen. Zum Prüfen reicht es, den Spielstand nach dem
Saisonwechsel zu laden und den Bildschirm anzusehen; ein neuer Saisonwechsel ist nicht nötig.

## Testkopie (15.11.2026)

- Erzeugt mit `python tools/a3patch.py original/anstoss3.exe build/anstoss3.exe beste-mannschaft`.
- `build/anstoss3.exe`: genau 1 Byte geändert (Dateioffset 0x3266FE, 0x26 → 0x1C), Disassembly an 0x007266FA geprüft.
- SHA-256 gepatcht: `A7F93C5AD21AD264A04D5F596AB9471FD098DFC08EE605711D93323D05A733CA`.

Test im Spiel:
1. Auf dem Spiel-PC prüfen, ob die dortige `anstoss3.exe` dieselbe Version ist (SHA-256 wie oben unter „Korrektur“). Sonst passt der Patch nicht.
2. Den Spielordner komplett kopieren und in der Kopie `anstoss3.exe` durch `build/anstoss3.exe` ersetzen. Das Original nicht anfassen.
3. Einen Spielstand laden und über ein Saisonende spielen.
4. Erwartung: In „Historisches → Beste Mannschaft“ steht in der letzten Zeile die neue Saison mit ihrem stärksten Team; die übrigen Zeilen bleiben vorerst Doppelungen und wandern mit jeder weiteren Saison heraus.

Wann im Saisonverlauf die Fortschreibung läuft (Aufrufer 0x00725569), ist noch nicht ermittelt (V: Saisonende).

## Offen (V)

- Ob das Schreiben auf 0x00B080DE (Kopf des Objekts 0x00B080D8) Folgefehler verursacht hat. Mit der Korrektur entfällt es.
- Ob weitere Ranglisten nach demselben Muster gebaut sind (gleiche Schiebe-Logik, gleicher Indexfehler).
