# Fundstellen in Code und Daten (Nachschlagewerk, Stand 16.11.2026)

Zweck: Alles, was in `anstoss3.exe` 1.40 (GOG, Image Base 0x400000, **Datei-Offset = Adresse − 0x400000**) und in den
Spieldaten bereits gefunden wurde, an einer Stelle – damit niemand neu suchen muss. Einzelheiten und Belege stehen in den
genannten Befunden; ein vollständiger Index aller je notierten Adressen ist `docs/adressindex.md` (erzeugt mit
`tools/fundstellen_index.py`). **G** = im Code gelesen und/oder an Daten belegt, **V** = Vermutung.
Disassembly: `analyse/anstoss3.disasm.txt` (dumpbin). Gepatchte Stellen: `tools/a3patch.py`.

## 1. Feste Speicherobjekte
| Was | Adresse | Abstand | Spielstand | Hinweis |
|---|---|---|---|---|
| Spieler (statisch) | `0x00C02550 + Nr × 0x354` | 852 B | 17 Blöcke à 852 000 B, je Spieler 820 B ab Objekt +0x20 | **Spielstand-Offset = Objekt-Offset − 0x20**, z. B. `0x00C02869` = Offset 0x2F9 |
| Vereine (statisch) | `0x01A72FF8 + Index × 0x990` | 2448 B | 2416-B-Blöcke ab Block 297 | Offset X ↔ `0x01A73018 + X`; erster Index je Land `word [Land×2 + 0x00AE5EF0]`, Anzahl `[Land×2 + 0x00AE5E06]`; Land gültig? `0x00676C03` |
| Trainer / Torwarttrainer | `0x00BE3920` / `0x00BE17F8 + Nr × 0x54` | 84 B | 52-B-Blöcke ab Block 1606 | `befund-personal.md` |
| Managerblöcke (10528 B) | `0x00A58078 + (Nr−1) × 0x2940` | – | Manager-Pakete ab Block 1548/1562 | `befund-vereinsstatistik.md`, HANDOFF-Protokoll |
| Block 3 (Historisches, 82340 B) | `0x00B0B6B8` | – | Block 3 | `zuordnung-bildschirme.md` |
| Saison-Archiv | `0x00B21ADC + Liga × 0x5E74 + Saison × 0x972` | – | Block 2 ab 8828 | `zuordnung-bildschirme.md` |
| Rekorde (Karriere) / „Für die Ewigkeit“ | `0x00B5CD1C` / `0x00AE44F8` | – | Block 1 ab 404 / Datei `alltimes.saq` | ebd. |
| Wartelisten Ex-Profis | Trainer `0x008E0F78`, Torwarttrainer `0x008E1D88`; Marktlisten `0x008E27A0 + Land×0x9C`, `0x008E2490` | – | 3600-/1800-B- bzw. 124-B-Blöcke | `befund-personal.md` |
| Datum | Tag `0x00B5CBDA`, Monat `0x00B5CBDC`, Jahr `0x00B5CBDE`; Tageszähler `0x00B5CBD4` (mod 7 = Wochentag) | – | Block 1 Kopf (+64 Managerjahr, +66 Saisonjahr, +68 Startjahr) | G |
| Zeitung (Schlagzeilen) | `0x01C6AC60`, drei Plätze ab +0x24 je 0x474 B | – | – | Abschnitt 6 |
| Texttabellen | Oberfläche: Objekt bei `0x01C6BFA4`; Ereignisse: `0x00A2FAE8` (+4 + Nr×4) | – | Dateien, Abschnitt 8 | G |
| Elf des Tages | `0x00B1300C + Liga × 0x2C` (11 Spielernummern) | – | – | G |

## 2. Spielersatz im Spielstand (820 B) – bisher bekannte Felder
Grundlage `feldkarte-spieler.md`; hier die im Spiel veränderlichen Felder (alle G, wenn nicht anders vermerkt).
| Offset | Inhalt |
|---|---|
| 0x130–0x13B | int16-Werte, u. a. Geldbeträge (Gehalt …, V); 0x13C int16 Jahr (V: Vertragsende) |
| 0x148 | Geburtsdatum (Tag, Monat, int16 Jahr bei 0x14A) |
| 0x170 / 0x180 | Tore / Spiele der Laufbahn (int16) |
| 0x190 | Flagwort = Laufzeitobjekt +0x20: Bit 10 (0x400) „verhasst“, Bit 16 (0x10000) „Liebling“ |
| 0x194 | Flagwort: Bit 30 wird beim „4 Wochen testen“ gelöscht (`0x00706BC8`) |
| 0x19C | eigene Spielernummer (int16); 0x19E/0x1A0/0x1A2 Namensindizes |
| 0x1D8 / 0x1DE | zwei Listen mit je drei Spielernummern (statischer Satz +0x1F8 / +0x1FE; V: Freunde / Streit und Feinde); Streichen `0x00703854` (erste) und `0x00703930` (zweite, schreibt die Endmarke bei `0x007039D0` fälschlich in die erste – `befund-meldungen.md` 6.1) |
| 0x1FC | Stärke; 0x1FD–0x1FF Positionen; 0x202 Talent (0 = bestes) |
| 0x246 | Länderspiele (1 Byte) |
| 0x24F | Flags; Bit 0x10 vermutlich Probezeit (Laufzeit +0xB3), V |
| 0x251 | Zustandsbyte (0, 2, 16, 64, 80, 96, 192), vermutlich Laufzeit +0xB6, V |
| 0x260 | Bits 3–4: Wert 0–3 (`0x007064C9`/`0x007064F6`), Bedeutung offen |
| 0x262 | Bits 0–1: dauerhafter Fan-Status 1 normal, 2 Liebling, 3 verhasst (`0x00706443` lesen, `0x00706467` setzen) |
| 0x26F–0x275 | Teilwerte der Motivation, 0–120 gespeichert: Trainer (G), Team, Verein, Presse (V stark), Privat, Ablenk., Angebote (V) |
| 0x2CB | 46 Bytes, je Spieltag zwei Halbbytes (aus Laufzeit +0x4A / +0x4B) |
| 0x2F9 | 46 Bytes, je Spieltag: Bits 6–7 Einsatz (0x40 durchgespielt, 0x80 eingewechselt, 0xC0 ausgewechselt), Bits 2–5 Note × 2 (0 = keine), Bits 0–1 Karte (1–3); **wird zum Saisonwechsel nicht gelöscht** |
| 0x333 | Byte, geht in die Formberechnung `0x006FF037` ein (V) |

## 3. Laufzeitobjekt „Spieler“ (das `this` der Routinen `0x006FExxx`–`0x0070xxxx`)
Wird aus dem statischen Satz gebildet; Zeiger stehen im Vereinsobjekt (`[Verein + 0xB50 + i×4]`).
| Offset | Inhalt |
|---|---|
| +0 | Spielernummer (int16) |
| +2 | Byte, vermutlich Stärke (V) |
| +3 | Position (1 Torwart … 10 Sturm) |
| +0x12 | Eigenschafts-Flags (Wort): 0x20, 0x40 senken die Verhasst-Schwelle auf 3,8; 0x400 „Sensibelchen“ (V) |
| +0x20 | Flagwort (siehe Spielersatz 0x190) |
| +0x3E | Saisontore (V) |
| +0x49, +0x50 | Zähler für die „Liebling“-Regel (Bedeutung offen) |
| +0x4A, +0x4B | zwei Werte 0–15 des letzten Spiels (→ Spielersatz 0x2CB) |
| +0x54 / +0x55 / +0x56 | Einsätze / Ein- und Auswechslungen der Saison (Bytes; V für 0x55/0x56) |
| +0x57 | Bits zum letzten Spiel: 0x01 eingesetzt, 0x02 eingewechselt, 0x04 ausgewechselt, 0x08/0x10/0x20 Karte |
| +0x58 | Minute der Ein-/Auswechslung (`0x00705E67` = gespielte Minuten) |
| +0xB3 | Flags: 0x10/0x20 Probezeit (gesetzt in `0x007069EB`, gelöscht in `0x00706A45`) |
| +0xB6 | Zustandsbyte: Bits 6–7 Art (1 = `0x00706B1E`, 3 = `0x00706B65`), unteres Halbbyte Restdauer (Probezeit: 8) |
| +0xB8 | unteres Halbbyte = **Note des letzten Spiels × 2** (`0x00705E9B`; Anzeige `IDC_EINZEL_NOTE_LETZTES`) |
| +0xCA | Motivation gesamt 0–100 (`IDC_EINZEL_MOTIVATION`) |
| +0xCC | Geburtsdatum (Tag, Monat, Jahr bei +0xCE); **Alter = `0x006FF01B`** (über `0x0067582A`) |
Zugriff: Spieler aus Nummer `0x00636459(Nr)` (Freigabe `0x006364CF`), aus Nummer + Verein `0x006968C4(Nr, Verein)`;
Name `0x006FEB4D(0)`; Form (0–20) `0x006FF037`; Flag setzen/löschen `0x00770800(Maske, Spieler)` / `0x00770942`
(Ausschlusstabelle `0x008AC7C0`), danach `0x0070147E` (Motivation neu rechnen).
Motivation: lesen `0x007008B9` (Trainer), `0x00700C42`, `0x00700E3F`, `0x007010BA` (Presse), `0x007011F1`, `0x00701328`,
`0x0070145F`; ändern `0x007007A1(±n)` Trainer, `0x00700FA2(±n)` Presse, `0x007010D9(±n)` Spielstand 0x273,
`0x00701210(±n)` Spielstand 0x274; Gesamturteil 0–3 `0x00770877`.
**Berichtigung (16.11.2026):** `0x00701210` ändert Spielstand 0x274, `0x007010D9` ändert 0x273; früher stand hier
`0x00701210` als „V: Privat“.

## 4. Laufzeitobjekt „Verein“ und Liga
- Verein (gebildet in `0x0063B75A` aus dem statischen Satz; holen `0x0063DD1C(Land, Verein, 0xFFFF)`, freigeben
  `0x0063DF96`): +0xE2 Kadergröße, +0xB50 Spielerzeiger, +0x103 Vereinsindex im Land, +0x104 Land, +0x105 Liga,
  +0x8A Managernummer (0 = Computer), +0x109/+0x10C/+0x10D Zielwerte (für `0x00775F0A` = „hinter den Erwartungen“, V).
- Gespielte Spieltage `0x00692744(Verein)`; `0x006927B3(Land, Liga)`; Liga-Nr. 0–9 `0x00677B07(Land, Liga)`;
  Vereinsname `0x0063E52F(Land, Verein)`.
- **Finanzen** (`befund-finanzen.md`): Finanzblock = Laufzeit-Verein +0x210 = Vereinssatz 0x468 (Grundwert der Saison),
  0x470 (Saisonwechsel, `0x00621F0D`, Schreiber `0x00772FC4` in `0x00772BEE`), 0x480 Saisontabelle, 0x570 Kredite,
  0x630 Geldanlagen. Bilanz-Bildschirm `0x004813AD` (Dialog 349); Gewinn `0x0061FC81`, Bankguthaben `0x0061FD97`,
  Anlagen `0x00648947` (Wert einer Anlage `0x00647D30`, Index je Anlageart `0x00B5CC8C` = Block 1 ab 0x104),
  Kredite `0x006488CA`, Vermögen der Spiellogik `0x00621EAC`; Zinssatz / Dispozins `0x00B5CC80` / `0x00B5CC84`
  (Block 1, 0xF8 / 0xFC); Geldfaktoren `0x00A3B3BC` (10 000) und `0x00A3B37C` (100 000), gesetzt ab `0x00627DAD`.
  Aktiengesellschaft? `0x0069D71D` (Vereinssatz 0x904 Bit 0), Börsen-Objekt `0x008BE408` (Block mit 123 572 B,
  Datensätze 264 B ab 20), Suche `0x00405DBE(Land, Verein)`, Kurs `0x00407520`.
  Im Werkzeug: `a3export.finance()` und `a3export.stock_market()`.
- Vereinssatz (2416 B): 0x10A Punktabzug/Zwangsabstieg; 0x1D2 Kaderliste (40 × int16); 0x468/0x470 Vermögen;
  0x630 Geldanlagen; 0x85C–0x868 Grundwerte der ewigen Tabelle; **0x86C–0x871 Tore, 0x872–0x877 Gegentore je
  Viertelstunde (Bytes, Überlauf)** – zählen `0x0069E224`/`0x0069E2B9`, lesen `0x0069E16A`/`0x0069E1C7`.
  Siehe `feldkarte-verein.md`.
- Liga-Objekt der laufenden Saison (Blöcke 1323, 1325 … 1337, 6760 B): +0x30 Vereine, +0x32 Spieltage,
  **+0x46 gespielte Spieltage**, +0x52 Verein je Platz, +0xE4A Ergebnisse. Dahinter je ein 1536-B-Block „Häufigstes Ergebnis“.

## 5. Liga-Statistiktabellen (10 Gruppen × 20 Tabellen im Spielstand, Blöcke 4–203)
Im Speicher nach Tabellenart gruppiert (je 10 Ligen), im Spielstand nach Liga (Block = 4 + Liga × 20 + Tabelle).
Sortierte Listen: Einfügen `0x006C5BAC` bzw. `0x006C58FE` (nimmt nur Einträge „größer“ als der letzte Platz, größter
oben), gleicher Schlüssel `0x006C5B66`; Leeren `0x007CFF4B`; Neuaufbau aller Tabellen je Verein ab ca. `0x00724900`.
Startinitialisierung der Tabellenarten ab `0x00644F5C` (Vektor-Konstruktoren).
| Tabelle | Speicher (Abstand) | Daten | Aufbau / Vergleich | Seite | Inhalt |
|---|---|---|---|---|---|
| 7 | `0x00AEB4C8` (0x154) | 288 B | `0x00722F4E` | – | offen |
| 8 | `0x00AEC210` (0xC4) | 144 B = 24 × 6 | `0x0072303E`, Vergleich `0x00722FF1`, Tabelle `0x008319F8` | `0x0044F79F` (Text 4751) | „Zu Null“ (V) |
| 9 | `0x00AEC9B8` (0xF4) | 192 B = 24 × (Land, Verein, Wert, Spieler in Elf des Tages) | `0x007230E1`, Vergleich `0x00723094`, Tabelle `0x00831A24`, Konstruktor `0x00645F50` | `0x0044EB33` (Text 4746), Kopie `0x00721191` | **Tagesform** (Klasse `CTagesform`); gepatcht |
| 10 | `0x00AED340` (0x1A0) | 384 B = 24 × (Land, Verein, 6 + 6 Bytes) | `0x007244E2` | `0x0044EF11` / `0x0044F358` (Text 4748), Summen `0x00724454` / `0x0072449B` | Wann trafen die Clubs / Gegner |
| – | `0x00AEFA50` (0x154), `0x00AF0798` (0xF4) | 288 / 192 B | `0x0072344D`, `0x007235E2` | – | offen |
| 16 | – | 480 B | – | – | Meiste Zuschauer national (`zuordnung-bildschirme.md`) |
Seite „Spielplan“ `0x0044EDBA` (Text 4747) mit Spieltags-Element `0x006E0649`. Rollende Liste 20 × 0xC4 B: `0x0072457F`
(V: Block 265).

## 6. Noten, Fan-Status, Zeitung, Ereignisse (Einzelheiten: `befund-notenschnitt.md`)
- Spielobjekt: +0x156 Spielernummern Mannschaft A (18 × int16), +0x19E Notenbytes (Bits 6–7 Kennzeichen, 0x3F Wert);
  Mannschaft B +0x34A / +0x392; Note eines Spielers zur Minute `0x006580B2(Spiel, Nr, Minute)`, Varianten `0x006581CD`,
  `0x0065803C`; Spielbericht-Sätze `0x01BDD7D8 + n × 0x238`.
- Spieltagsbyte schreiben `0x006FF2F7` (endet `0x006FF431`), lesen `0x006FF47F` (0x2F9) und `0x006FF43E` (0x2CB).
- Auswertungen: Statistik „Notenschnitt Mannschaft“ `0x0046E7DC` (richtig); Spielerdetails „Noten“ `0x00561C46`
  (Zähler `0x00561CD3`, gepatcht); Texte „Liebling“/„verhasst“ in den Spielerdetails `0x0055B167`;
  Saisonschnitt `0x00705EB6`, Schnitt der letzten n `0x00705F60` (beide neu geschrieben), Spieltage seit letztem Einsatz
  `0x0070607A` und `0x00706015` (unverändert, falsche Masken).
- Fan-Status: Kaderschleife `0x00770BAE` → „Liebling“ `0x007709E8`, „verhasst“ `0x00770A72` (gepatcht bei `0x00770B2E`).
  **Berichtigung:** In `0x007709E8` heißt die dritte Bedingung „Alter über 33 Jahre (`0x006FF01B`) und mehr als 30
  Einsätze ohne Ein-/Auswechslung“, nicht „nach dem 33. Spieltag“.
- Zeitung: `0x00789C32(Rang, Textnummer, Anzahl Namen, Kennzeichen, Namen …, Zusatzwerte …)`; Satz 0x88 B (mit 0 vorbelegt
  in `0x0078A2D0`): +2 Spielernummer (Kennzeichen 0x80000000), +4/+6 Land/Verein (0x20000000), +8 + 4·i Zusatzwert i
  (Bit i; Bit 8 = „Presse“, Bit 9 = Spielstand 0x274 über `0x00701210`). Namen werden nach `0x008AD230[i]` kopiert.
  Einsortieren `0x00789895` (drei Plätze, Rang entscheidet), Anwenden der obersten Schlagzeile (Platz `0x01C6AC84`)
  `0x0078A0F5`, nur wenn `0x00789998` ≠ 0; Manager dort über `0x0041849A(Wert0–3, Manager)`, `0x006A58FC(0x10)` bei
  Wert4 ≠ 0 und `0x006A426B(Managernummer)`. Vier Aufrufe mit falscher Argumentzahl: `0x00537ADD`, `0x00537B15`
  (Routine `0x005378D6`), `0x0053CD00` (Routine `0x0053CBDF`), `0x005F47A7` (Routine `0x005F3BAF`) –
  `befund-meldungen.md` Abschnitt 4.
- Zweiter statischer Managersatz `0x00A62578 + (Nr−1) × 0x2158`, Merker `word [Nr×2 + 0x00B5CB9A]`, Zähler
  `word [Nr×2 + 0x01B9FFAA]` (benutzt von `0x006A426B`).
- Leistungs-Schlagzeilen (Kaderschleife um `0x005E5715`): 1519 „Totalausfall“ (gepatcht über `0x00705EB6`), 1520, 1521.
- **Ereignisverteiler** (`befund-meldungen.md`): täglich je Verein `0x005EF842` → `0x005EF8CC` (Spieler-Ereignisse,
  Verteiler `0x005EFADA`, Gewichte `0x0088E128`) und `0x005F0133` (Verein/Manager, Gewichte `0x0088E188`);
  gewichtete Auslosung `0x0060BE4D(Tabelle)`, Tabellen anlegen `0x0060BDB7(Anzahl, Einträge, Gesamt)`.
  Textroutine `0x005EF430` (262 Aufrufe, einziger Leser der Tabelle) mit 39 Routinen mit Textparameter (u. a.
  `0x00600F2F`, `0x00601043`, `0x005EE5C0`). Auslosungsobjekt: +0 Anzahl, +2 Summe der Gewichte, +4 Gesamt.
  Allgemeine Spieler-Ereignisse: Verteiler `0x005E08F1` (Fall 48 = Text 1289 unerreichbar).
  Zeitungssatz: +0 Managernummer (`0x40000000`), +2 Spielernummer, +4/+6 Land/Verein, Werte ab +8; Anwenden
  `0x0078A0F5` (Manager `0x0041849A`, Verein `0x0069EFE8` / `0x00698EF6`).
- **Vereinszähler** Verein +0xDF8 Bits 18–20: ändern `0x0069FE73(±n)` (begrenzt 0–15 statt 0–7, löscht Bit 21);
  Aufrufer `0x0049180E`, `0x00491F5D`, `0x0064B41B`, `0x0064B5D1`, `0x005E52EC`, `0x005E535A` (alle +1); lesen
  `0x005E53F5` in der Maulwurf-Routine `0x005E50BA`; Merker Bit 21 setzen `0x005E5650`, prüfen `0x005E536D`;
  Zurücksetzen beim Saisonwechsel `0x0077360D` (in `0x00772BEE`, ruft `0x0069FF06(0)`). Bit 21 = „Schlagzeile zu
  diesem Stand schon erschienen“; das Löschen in `0x0069FE73` / `0x0069FF06` ist Absicht (17.11.2026). Zähler an allen
  Stellen 3 Bits (Maske `0x1C0000`, Leser `0x0069FE57`), ausgewertet werden Stände bis 10 (`0x005E5408` ff.).
- **Patch-Phase Meldungen, am 17.11.2026 gelesen** (Einzelheiten in `docs/korrekturliste-meldungen.md`, „Nachgelesen“):
  Maulwurf = Bit 16 im Flagwort des Spielers (lesen `0x00700272`, setzen/löschen `0x00700294`), erster Maulwurf der
  Aufstellung `0x006493E0`, Bestimmung in `0x005E50BA` (`0x005E5693`, Kandidaten Motivation +0xCA < 70), Aufrufer
  `0x005EFDE5`. Gedopt = Bit 1 in Spielstand 0x24D (lesen `0x006FF99A`, setzen `0x006FF715`; Doping-Dialog
  `0x00516F7A` mit `0x0051731D`, `0x00517551`; dritter Setzer `0x0074EE7B`). Strafenzähler Spielstand 0x286 (hoch
  `0x007049CC`, lesen `0x007049AF`: Spielerdialog `0x0055CEB6`, Bedingung `0x0070B417` in `0x0070AFA0`). Sperre in
  Spielen setzen `0x0070302D`. Kader-Zeigerliste Verein +0xB50: Aufbau `0x00635F76`, `0x00636120` ff., `0x006362A0`,
  nur Plätze 0 bis Kadergröße−1. Freunde-Liste Spielstand 0x1D8[3] (lesen `0x007015C6`), Streit-Liste 0x1DE[3]
  (lesen `0x007015EB`), streichen `0x00703854` / `0x00703930`, Aufräumen nach Abgängen `0x007105DF` / `0x0071064A`.
  Geldbeträge: Grundeinheit `0x00A3B3E4` (= 1 000), Vielfache in `0x00627E73` ff. (`0x00A3B370` = × 150, `0x00A3B37C`
  = × 100, `0x00A3B348` = × 500); Betrag als Text `0x004DAF8F` (fester Puffer `0x008EC88C`). Verein +0x2F8:
  Summand der Einnahmensumme `0x006200BB` (mit +0x2F4, +0x2FC), verwendet in `0x00622201` und `0x004A21F7`.
  Merkerliste „schon geschehen“ `0x00A32738`: nur die letzten 20 Kennungen (`0x005E5E90` / `0x005E5EE0`).
  Schlagzeile des Tages: Satz `0x01C6AC84`, Werte liest nur `0x0078A0F5`, Anzeige `0x005D8624` nur die Textpuffer.
- **Fragen mit Antworten** (Dialog 253, Klasse ab `0x00496A0F`, Anzeige `0x00496B94`): 80 Datensätze
  `0x0088F090 + n × 44` (+4 Frage, +8/+0xC/+0x10 Antworten, +0x14/+0x18/+0x1C Ergebnistexte, +0x20/+0x24/+0x28
  Routinen); öffnen `0x005F2813(Manager, Verein, Datensatz)` und Straf-Frage `0x005F29BC(Manager, Verein, Text,
  Spieler, Stufe 1–3)` (Datensatz = Stufe + 33; Auswertung Stufe 1 bei `0x005F2C3C`–`0x005F2C93`, abgeschaltete
  Zweige `0x005F2E43`, `0x005F2F07`; Sperre setzen `0x0070302D`). Globale Nachricht `0x00A321E8` (+6 Antwort
  `0x00A321EE`, +0xC Datensatz `0x00A321F4`, +0x22 Zusatzindex `0x00A3220A`, +0x28 Text `0x00A32210`).
  Routinen aus den Datensätzen: `0x005EE98D`, `0x005EE9C2`, `0x005EEA5D`, `0x005EEBFA`, `0x005EECBA`, `0x0060B898`,
  `0x005EA51C` (Datensatz 19), `0x005F4972` (Datensatz 2). Datensätze 10/11 über `0x006062FE`.
  Ehefrau des Managers (Datensatz 42): `0x005EECBA` / `0x005EEDF9` aus `0x005F5556`, Tabellen `0x0088E0D8`
  (Eigenschaften), `0x0088E0EC`, `0x0088E0F4` (Antworten).
- **Einzelne Textstellen** (`befund-meldungen.md` Abschnitt 3): Gründe für Bauverzögerung Tabelle `0x0088EC8C`
  (12 Einträge, Zufall 0–9 bei `0x00602373`); Text 1481 bei `0x0076898B` (Zweig `0x0076894B` → `0x00768962`);
  fest abgeschalteter Block `0x0060C687` (Texte 832–847).
- **Nie ausgeführt** (18 Routinen): `0x005DFC63`, `0x005E1C68`, `0x005E3CA8` (Hülle `0x005E3F39`), `0x005E447D`,
  `0x005F05CE`, `0x005F8393`, `0x005F84CB`, `0x005FA0C7`, `0x005FC9EE` (Hülle `0x005FCC29`), `0x005FD0F5`,
  `0x0060AE6C` und `0x0060B11E` (Hülle `0x0060B430`, Verfehlungen der Spieler, Tabellen `0x00A3271C` / `0x00A32710`),
  `0x0061A033`, `0x0061A1A0`, `0x0061A29A`, `0x0061A31C`, `0x0061B464`, `0x0061B898`; ohne Textstelle u. a.
  `0x005F1E1A`, `0x005F1E3A`.
- **Meldungen mit Namen und Werten:** `0x00600F2F(Verein, K, Text, Spieler, zweiter Name oder 0, w)` und
  `0x00601043(…, w1–w4)`, mit sieben Werten `0x006015FE`; Namen einsetzen `0x005EEE7F` (ersetzt nur %1–%9, „%s“
  bleibt stehen); Grundroutinen `0x005F1EAF`, `0x005F1F42`. Name der Frau `0x0070173F`, Nachname `0x006FEA7C`.
- **Teilwerte der Motivation, Leser mit Flag-Zuschlägen / Schreiber mit Rohwert:** Trainer `0x007008B9` /
  `0x007007A1`, Mannschaft (0x270) `0x00700C42` / `0x00700A6D` (direkt setzen `0x00700BCF`), Verein (0x271)
  `0x00700E3F` / `0x00700D27`; 0x274 lesen `0x00701328` (ohne Zuschläge).
- **Ereignisroutinen aus Lesepaket P02** (`befund-meldungen.md` 6.6–6.12): Hülle `0x005E20FD` → `0x005E08F1`;
  Hülle `0x005E2BB9` → `0x005E2152` (andere Ablenkung; Firmen-Stand Bits 4–6 von Spielstand 0x261, lesen
  `0x0070324F`, setzen `0x00703276`; feste Namen `0x0088D970`–`0x0088D9C0`); Gruppenbildung `0x005E3885` (Verein
  +0x9E, Gruppenbit setzen `0x0069A882`); Hülle `0x005E4DDE` → `0x005E4A3E` (Spieler biedert sich an); Hülle
  `0x005E4FD6` → `0x005E4EC2` (Spitzel: Flagwort Spielstand 0x194 Bit 0x8000, lesen `0x007001ED`, setzen/löschen
  `0x0070020F`; Bit 0x20000 „enttarnt“ `0x0070031F`).
- **Meldungsdialog mit Vorher/Nachher:** `0x005F1F42` legt Art / Vorher / Nachher in `0x00A2F6EE` / `0x00A2F6F4` /
  `0x00A2F6F6` ab, Text im Puffer `0x00A2F700`; Anzeige `0x005F2234`; Beschriftung je Art bei `0x004953E1` aus Tabelle
  `0x008808B0` (Texte 4771–4782: 0 Trainer, 1 Mannschaft, 2 Privates, 3 Ablenkung, 4 Presse, 5 Verein, 6 Presse,
  7 Verhandlung, 8–10 Beliebtheit Fans / Medien / Öffentlichkeit, 11 Stimmung). Spielstand 0x274 = Ablenkung (G).
- **Beliebtheit des Managers** (Laufzeit-Manager): +0x3A Öffentlichkeit, +0x3B Fans, +0x3C Medien (lesen
  `0x006A5A7D`), Wort +0x9C offen; ändern `0x0041849A(d1, d2, d3, d4, Manager)`; Dialog füllt bei `0x0047E6E0`.
- **Ereignisroutinen aus Lesepaket P04** (`befund-meldungen.md` 6.13): einfache Geld-Ereignisse `0x005E993A` →
  `0x005E9A4F` (Tabelle `0x0088DC58`, 108 Paare Text / Wert; negativ → Verein +0x2C0, sonst +0x2C4; Meldung
  `0x005E9CFB`); Ereignisse „Recht“ `0x005E9ED1` (Auslosung `0x0088E04C`, Sprungtabelle `0x005EA50C`, toter Block
  `0x005EA01B`); Verbands-Ereignisse `0x005EA5CE` (Merker-Byte `0x00B5DFA8`); Schokoladen-Frage in `0x005E6153`
  ab `0x005E8979`, Auswertung `0x005E9E01`; Geldbetrag als Text `0x004DAF8F` (fester Puffer `0x008EC88C`).
- **Privatleben der Spieler** (`befund-meldungen.md` 6.14). Spielersatz: 0x25E Bits 0–1 Status (0 keine Beziehung,
  1 Freundin, 3 verheiratet; lesen `0x00702B8C`, setzen `0x00702BB0`), Bits 2–4 Krisenstufe (`0x00702C12` /
  `0x00702C39`); 0x263 / 0x264 / 0x265 Namensindex Partnerin / Geliebte / frühere Partnerin (Namen `0x0070173F`,
  `0x007017DB`, `0x0070185C`), 0x266 / 0x267 Namensgruppen; 0x150 Hochzeitstermin (`0x00702AC7` anlegen,
  `0x00702A9B` prüfen); 0x1D6 Zahl der Kinder (`0x006FFD8A`); Flagwort 0x194 = `0x00C02704 + Nr × 0x354` (Bit 2
  `0x00702A5B`, nie gesetzt; Bit 19 Schwiegermutter `0x00700413` / `0x00700435` / `0x0070046A`; Bit 25 `0x007028D7`,
  Setzer `0x007028F9` ohne Aufrufer). Beziehung beenden `0x00702467`, Geliebte wird Partnerin `0x0070282A`, Geliebte
  eintragen `0x007029A7` / löschen `0x00702962`, Partnerin übernehmen `0x00702668`, Ex-Freundin zurück `0x00702762`,
  heiraten `0x00702B15` (Termin-Routine `0x005FD386`). Terminliste `0x008EB8B0`: streichen `0x004377B7(Nummer,
  Datum*)`, eintragen `0x0043779F`. Verletzung setzen `0x00766B92(Spieler, Art, Dauer)` mit Tabelle `0x008AC340`
  (10 Bytes je Art, Byte +1 = Dauer in Tagen; Spieler +0x2C Dauer, +0x2E Art, +0x2A Beginn). Schüler-Merker
  Spielstand 0x260 Bits 3–4 (`0x007064C9`, `0x007064F6`, `0x0070654A`), Bit 4 zugleich Gruppen-Anführer
  (`0x007006E8`, `0x00700690`, `0x0070071C`).
  Ereignisroutinen (Vorroutine → Routine): `0x005F9A2D` → `0x005F95AD` Wehrdienst / `0x005F98B1` Zivildienst;
  `0x005F9D6D` → `0x005F9B90` Schüler; `0x005F9FD0` → `0x005F9ED7` Neuzugang; `0x005FA5F8` → `0x005FA394` Hochzeit
  platzt; `0x005FA890` → `0x005FA6CE` ohne Partnerin; `0x005FB17A` → `0x005FAA76` mit Freundin; `0x005FB634` →
  `0x005FB264` verheiratet; `0x005FB916` → `0x005FB751` Affäre (nie erreicht). Meldung mit drei Namen `0x006012DF`,
  `0x00601166`.
- **Hobby-Ereignisse** (`befund-meldungen.md` 6.15): Hülle `0x005FED08` → `0x005FD59D(Spieler, Verein, Manager)`,
  Verteiler `0x005FD5FA` nach Hobby-Nummer (Spielstand 0x26D; setzen `0x00702CBD`). „Angeschlagen“ setzen
  `0x00766AF9(Spieler, Tage)` (Byte Spieler +0x2F, Anzeige `0x00731E54`). Führerschein-Zähler Spielstand 0x26E:
  einzige Routine `0x00702D31(wert)` (wert < 0 = nur lesen), Leser `0x00702D6F`; wird nie heruntergezählt.
  Stimmung des Vereins: Laufzeit-Verein +0x9E (0–200), ändern `0x00698EF6(±n)`. Streit zwischen zwei Spielern
  eintragen `0x00703DF4`; Mitspieler wählen `0x005EC9D8(Verein, Spieler)`.
- **Ereignisse zwischen zwei Spielern / privater Trainer** (`befund-meldungen.md` 6.16): Hülle `0x005FFEB7` →
  `0x005FEDB0(Verein, Spieler)`, Los-Tabelle `0x0088E8C8` (25 Einträge), Verteiler `0x005FEE1E`; Zufriedenheit eines
  Spielers `0x006FF14D` (Mittel aus Trainer, Verein, Mannschaft), Teilwerte zweier Freunde angleichen `0x00705539`;
  leere Routinen `0x005EE2F5`, `0x005EE2FC`. Raucher / privater Trainer `0x005FFF0F`: Flagwort Spielstand 0x194
  Bit 0x800 Raucher (lesen `0x006FFFD9`), Bit 0x2000 privater Trainer (lesen `0x007000E3`, setzen `0x00700105`);
  Kondition `0x00457E00` (Spieler +0x16 / 100, Raucher −5).
- Nur gemeldete, nicht nachgeprüfte Adressen stehen nicht hier, sondern in `befund-meldungen.md` Abschnitt 7.
- Zufallsereignisse Privatleben `0x005FE987` (Sprungtabelle `0x005FECF8`): 1232/1234 Führerschein, 1233 Hobby,
  1235 „Goldkettchen“ ab `0x005FEBDF` (Aufruf `0x005FEC04` gepatcht). Meldung an den Manager mit Vorher/Nachher:
  `0x00601043`, `0x00600F2F`.
- Gespräch bei Auswechslung: Dialog 496, Klasse ab `0x00492A78`, Auswertung der Antwort `0x00493228` (Sprungtabelle
  `0x00493745`, acht Antworten), Anzeige der Werte `0x0048E32E`.
- Jugendspieler „4 Wochen testen“: Abfrage Text 4302 bei `0x004D888B` (nur an einem bestimmten Wochentag, `0x004D87E5`),
  Setzen `0x007069EB`, Ende `0x00706A45`; Haus-Symbol = Text 5181 „abwesend“, Legende `0x0050A5B2`.
  Die Ursache des Jugendspieler-Fehlers ist **nicht** gefunden.
- **Wechsel-/Taktikfenster im laufenden Spiel (19.11.2026, nur gelesen):**
  - Taktikfenster: Klasse ab `0x004BFC69` (Abbau `0x004C2090`), Aufbau/Neuladen `0x004C059D`, Steuerelemente in den
    Arbeitssatz schreiben `0x004C1798` (Spielweise = Steuerelement +0x1C7C → Arbeitssatz +0x40; weitere +0x41, +0x42,
    Wort +0x3E), Klick Spielweise `0x004C1C87` (Kontroll-Nr. 3737, Textnummern-Tabelle `0x0088AC08`). Die gleich
    gebaute Klasse ab `0x0058A9E5` ist das Taktikfenster außerhalb des Spiels (schreibt Verein +0xA8, +0xA9, +0xAA,
    Wort +0xAC, `0x0058C6F5`). Wechselfenster: Klasse ab `0x004B8875`, Aufbau `0x004B98AD`.
  - Arbeitssatz: laden `0x006495B1` (Ziel +0x18 → Arbeitssatz +0x10, 500 Bytes), zurückschreiben `0x0064951F`.
    Eintrag je Mannschaft 0x20C Bytes ab `0x00B5E188` (Gruppe 0x858 ab `0x00B5E160`, Anzahl `0x00B5E180`): füllen
    `0x0064975D` (aus Partie +0x5C Heim / +0x250 Gast), zurück in die Partie `0x006497F8`. Partie = 0x498 Bytes ab
    `0x01BAF714`; Wort +0x474: Bit 0 Heim menschlich, Bit 1 Gast menschlich, Bits 8–11 / 12–15 Managernummer.
    Spielweise im Taktikblock +0x30 (Partie +0x8C Heim, +0x280 Gast).
  - Fenster öffnen: Schleife `0x0064A816` (Zustand 100 Wechselfenster `0x0064A68A`, 200 Taktikfenster `0x0064A750`),
    Aufträge 181 (`0x00412B4D`) und 182 (`0x0064AB09`) im Verteiler `0x006AA226`.
  - Manager-Satz im Spiel: 0x38 Bytes je Manager ab `0x01BDD6B8`, Spielweise Byte +0x20 (`0x01BDD6D8`), Fenster
    angefordert dword +0x28; lesen `0x006FB730`, schreiben `0x006FB811`. Die Spielschleife kopiert daraus laufend die
    Spielweise in den Taktikblock (`0x006F4744` → `0x006FB8F5`, nur dieser eine Wert). Regler auf dem Spielbildschirm
    `0x00543077` / `0x00543178`, Knopf „Fenster anfordern“ `0x00543279` / `0x005432CA`.
  - Drei Wege zum Fenster: `0x004123D1` (im Spiel, alle menschlichen Mannschaften; „Fall 2“ der Spielschleife bei
    `0x006F1B48` und `0x006F22F6`) und `0x0064987A` (u. a. `0x006F1C08`) schreiben nach dem Fenster die Spielweise in
    den Manager-Satz (`0x0041289F`, `0x00412986`, `0x0064A5AC`, `0x0064A62B`). **`0x00412CF2`** (Fenster nach einem
    Ereignis, aufgerufen aus `0x00413115`, wenn Partie +0x240 Heim / +0x434 Gast gesetzt ist) schreibt nur den
    Taktikblock zurück – **der Schritt in den Manager-Satz fehlt, die Spielweise fällt beim nächsten Durchlauf auf
    den alten Wert zurück (G am Code; mit der Korrektur in 1.47 vom Nutzer im Spiel bestätigt, 19.11.2026).**
  - Merker +0x240 / +0x434 setzt `0x004131B0`; Aufrufer `0x0065A9BD`, `0x0065AE69`, `0x0065B56A`, `0x0065B860`,
    `0x0065BC8E`, `0x0065C349`, `0x0065CA8D`, `0x0065CCED`, `0x0073DA99`, `0x0073DBBF`. Ganz gelesen sind `0x0065A6B0`
    (setzt ein Positionsbit in Partie +0x112; V: Platzverweis) und `0x0065C8B1` (nimmt den Spieler aus der
    Aufstellung, Bit in +0x112 nur bei erschöpften Wechseln; V: Verletzung). Die sechs weiteren Routinen
    (`0x0065AB3A`, `0x0065B2BF`, `0x0065B59E`, `0x0065B894`, `0x0065BF36`, `0x0065CB2C`) sind nur auf ihre Schreibstellen
    durchgesehen: alle leeren den Platz in der Aufstellung (Verein +0xA9A) und setzen das Positionsbit (+0x112 Heim /
    +0x306 Gast); `0x0065CB2C` ist das Gast-Gegenstück zu `0x0065C8B1`, die beiden Stellen in `0x0073AE43` rufen es
    direkt davor auf.
  - Korrektur `spielweise-ereignisfenster` in `tools/a3patch.py` (19.11.2026, Teil von Installer 1.47): Blöcke `0x00412FBB`–`0x00413041` und
    `0x0041305A`–`0x004130E7` neu geschrieben, zusätzlich Spielweise (Partie +0x8C / +0x280) → `0x01BDD6D8`. Nur
    statisch geprüft.
  - Nebenbefund (V): In `0x004123D1` und `0x0064987A` steht das Schreiben der Spielweise vor dem Sichern des
    Datenblocks (`0x007CFB99`), der Abgleich `0x007CFBFB` findet dann keinen Unterschied – im Netzwerkspiel käme die
    Änderung vermutlich nicht beim Mitspieler an. Ohne Netzwerk (`0x01CB8BE3` = 0) tun diese Routinen nichts.

## 7. Historisches, Trainer, Auf-/Abstieg, Personal (bereits ausgeliefert)
Nur die Einstiegspunkte; Rest in den Befunden.
- Verteiler der Historisches-Bildschirme `0x0045E8A5` (Index → Routine: `zuordnung-bildschirme.md`).
- Beste Mannschaft: Schieben `0x007266FA`, Anzeige `0x004665DD` (`fehler-beste-mannschaft.md`).
- Auf-/Abstieg: Statistikroutine `0x00726382`, zweite Meldestelle `0x0069139B`, Spanien `0x006B1F12`; Saisonergebnis-
  Objekt nur im Speicher (`befund-auf-abstiege.md`).
- Erfolgreichste Trainer: `0x00725FBA` (Mensch), `0x006B53D4` (Computer), Listeneintrag `0x006B5497`, Zähler
  `0x006B583A`, Sortierung `0x00725E61` (`befund-trainer-eps.md`).
- Vereinslisten „Tore“/„Spiele“: `0x007441F4`, Spielabschluss `0x00744654`, Zu-/Abgang `0x005DBEFC`/`0x005DBEF2`
  (`befund-vereinsstatistik.md`).
- Trainer-Nachwuchs `0x0066DF9E`, Ausgleich `0x006B6000` (`befund-personal.md`).
- Spielstand schreiben `0x006ED31E` / `0x007CFFF4`, laden: `spielstand-bloecke.md`, `befund-spielstand.md`.

## 8. Dateien und Formate
| Datei | Inhalt | Format / Lader |
|---|---|---|
| `saves\*.an3` | Spielstand | Blöcke, eigenes LZ77; `tools/a3scan.py`, `a3lz.py`, `befund-spielstand.md` |
| `alltimes.saq` | „Für die Ewigkeit“ | 21 Einträge, `a3export.read_alltimes` |
| `texte\Ereignis.saq` | 2483 Meldungs-/Ereignistexte | int32 Länge (0x42D1C), int32 Anzahl (0x9B3), dann jedes Byte XOR voriges gespeichertes Byte (erstes mit Länge & 0xFF); Lader `0x005EF298`, Zugriff `0x005EF430(Nr)`; **`tools/a3ereignis.py`** |
| `deb\MeineDialoge.rch` | alle Oberflächentexte und Dialoge | Klartext; Texte als `[Nummer int16][Text\0]`, Tabulator ausgeschrieben als `\t`; Lader `0x004318FA`, Zugriff `0x00730300` → `0x007B7F68` → Suche `0x007B7B91` |
| `deb\ListeDerTexte.rh`, `ListeDerIDs.rh`, `DialogIDs.rh` | Namen und Nummern aller Texte, Bedienelemente, Dialoge (mit deutschem/englischem Text als Kommentar) | zum Nachschlagen; Texte dort können vom Spiel abweichen |
| `texte\*.txt`, `*.saq`, `textmodus.bin` | weitere Texte (Interviews, Präsident …) | nicht untersucht |
| `Data.a3\*.sav` | Stammdaten | Lader `0x0068C257` (Spieler), `0x0068CDFA` (Vereine); Feldkarten |
C-Laufzeit im Spiel: `sprintf` = `[0x0080D5B8]`, `fopen`/`fread`/`fclose` = `[0x0080D694]`/`[0x0080D698]`/`[0x0080D69C]`,
`strcpy` `0x007E0FFE`, `memcpy` `0x007E11C6`, `memset` `0x007E1010`, Zufall 0…n−1 `0x0078A810(n)`,
Gleitkommakonstante 2,0 bei `0x0080DAF0`.

## 9. Bekannte Fallen
- Texte, die das Spiel über `0x005EF430` holt, sind Nummern in `Ereignis.saq` – **nicht** die gleich großen Nummern aus
  `ListeDerTexte.rh` (dort z. B. 1519 = „Runde 1“). Über `0x00730300` geholte Texte sind die aus `ListeDerTexte.rh`.
- Hexwerte bei `push` in dezimale Textnummern umrechnen (4746 = 0x128A, 4747 = 0x128B, 4748 = 0x128C).
- `block_NNN.bin` numerisch sortieren; Vereinsnummern in Statistiken sind der Rang im Land.
- Die neuen Routinen `0x00705EB6` und `0x00705F60` lesen den Verein aus dem Rahmen ihres einzigen Aufrufers.
- Sortierte Statistiklisten lassen sich nicht durch Umdrehen des Vergleichs umkehren (leere Plätze haben den Wert 0).
