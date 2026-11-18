# A3-Rework – inoffizieller Fehler-Patch für ANSTOSS 3

Dieser Patch behebt Programmfehler in ANSTOSS 3 (Ascaron, 2000), Version 1.40 in der Ausgabe von GOG.
Er korrigiert ausschließlich Fehler: Stellen, an denen das Programm nachweislich nicht das tut, was es selbst
vorsieht. Spielwerte, Wahrscheinlichkeiten und das Balancing bleiben unverändert, neue Funktionen kommen nicht hinzu.

Das Projekt ist ein Fanprojekt und steht in keiner Verbindung zu den Rechteinhabern des Spiels. Es enthält keine
Dateien des Spiels und setzt eine gekaufte Fassung voraus.

## Stand

Aktuelle Version: **1.46** (72 Korrekturen an 96 Stellen der `anstoss3.exe`, dazu eine Spaltenüberschrift,
20 Meldungstexte und eine optionale Anpassung der `ddraw.dll`).

Geprüft wurde der Patch an mehreren Spielständen einer langen Karriere, einzelne Korrekturen gezielt im Spiel, andere
nur am Programmcode. Tests über viele Saisons stehen aus. **Die Verwendung erfolgt auf eigene Verantwortung; bitte
sichern Sie vorher Ihre Spielstände.** Welche Korrektur wie geprüft ist, steht in den Befunden unter `docs/`.

## Was korrigiert wird

- **Jugendspieler:** Aus der Jugend eines anderen Vereins abgeworbene Spieler erhielten ein Gehalt, aber keine
  Vertragslaufzeit. Im Profikader galten sie deshalb als abwesend (Haus-Symbol) und waren in der Probezeit nicht
  einsetzbar.
- **Geldanlagen:** Mit jedem Wertzuwachs einer Geldanlage sank das angezeigte Bankguthaben um denselben Betrag; beim
  Auflösen kam alles auf einmal zurück (bekannt als „doppelte Zinsen“).
- **Trainer, Co-Trainer und Torwarttrainer:** Ehemalige Spieler rückten wegen einer fehlerhaften Abfrage nie als
  Trainer nach. Frei werdende Stellen wurden über Jahrzehnte nur durch Nachfolger mit Mindestkompetenz besetzt.
- **Statistiken:** „Beste Mannschaft“, Rekordauf- und -absteiger, „Erfolgreichste Trainer“, „Meiste Spiele für den
  Verein“, Notenschnitt in den Spielerdetails, Liga-Statistik „Tagesform“.
- **Meldungen und Ereignisse:** über 40 Einträge, darunter fehlende oder vertauschte Namen, Wirkungen, die der Text
  nennt, die aber nicht oder falsch eintraten, und Ereignisse, die wegen eines Fehlers nie ausgelost wurden.
- **Optional:** Eingabeverzögerung nach Mausklicks mit aktuellen Grafikkarten (angepasste `ddraw.dll` der GOG-Ausgabe).

Die vollständige Liste mit Fehler, Korrektur und Auswirkung je Eintrag steht in
[`patch-1.46/CHANGELOG.txt`](patch-1.46/CHANGELOG.txt).

## Installation

1. Laden Sie das Archiv `Anstoss3-Patch-1.46.zip` unter „Releases“ herunter und entpacken Sie es vollständig.
2. Beenden Sie das Spiel und starten Sie `Anstoss3-Patch-1.46.cmd` per Doppelklick.
3. Wählen Sie den Ordner des Spiels und „Installieren“.

Das Installationsprogramm ist ein PowerShell-Skript im Klartext. Es prüft jede Stelle vor der Änderung, legt
Sicherungen an und verändert nichts, wenn es eine abweichende Fassung der Programmdatei vorfindet. Über
„Deinstallieren“ wird der ursprüngliche Stand wiederhergestellt. Einzelheiten stehen in
[`patch-1.46/LIESMICH.txt`](patch-1.46/LIESMICH.txt).

Die Korrekturen sind in zwei Gruppen geteilt:

- **Optische Änderungen** (Statistiken, Anzeigen, Texte): werden immer installiert und ändern den Spielverlauf nicht.
- **Berechnungskorrekturen und -änderungen:** greifen in den Spielverlauf ein und können abgewählt werden.

Die Verträglichkeit mit anderen Modifikationen, die ebenfalls die `anstoss3.exe` oder die `ddraw.dll` ändern, wurde
nicht geprüft.

## Aufbau des Repositorys

| Ordner | Inhalt |
|---|---|
| `patch-1.46/` | Installationsprogramm (`.cmd`, `.ps1`), `LIESMICH.txt`, `CHANGELOG.txt` |
| `tools/` | Patch-Tabelle (`a3patch.py`: jede Stelle mit alten und neuen Bytes und Begründung), Erzeuger und Test des Installers (`patch_bauen.py`, `patch_test.ps1`), Handassembler der größeren Umbauten (`asm_*.py`), Werkzeuge zum Lesen von Spielständen und Texten |
| `docs/` | Befunde zu den einzelnen Fehlern (`befund-*.md`, `fehler-*.md`), Korrekturliste der Meldungen, Feldkarten der Datensätze, Fundstellen und Adressindex |

In den Befunden ist Gesichertes von Vermutetem getrennt gekennzeichnet. Interne Arbeitsnotizen, auf die einzelne
Befunde verweisen („siehe HANDOFF“), sind nicht Teil der Veröffentlichung.

## Selbst bauen

Der Installer wird aus der Patch-Tabelle erzeugt. Dazu werden die unveränderten Dateien einer eigenen Installation
in den Ordner `original/` kopiert (`anstoss3.exe`, `ddraw.dll`, `deb\MeineDialoge.rch`, `texte\Ereignis.saq`); der
Ordner ist nicht Teil des Repositorys.

```
python tools/patch_bauen.py
pwsh -File tools\patch_test.ps1 -Version 1.46
```

## Fehler melden

Fehlerberichte sind willkommen, am besten mit einem Spielstand unmittelbar vor und nach dem Fehler und einer
Beschreibung der Schritte. Aufgenommen werden nur Fehler des Programms, keine Wünsche zum Balancing.

## Entstehung

Die Analyse des Programmcodes, die Befunde und die Werkzeuge sind mit Unterstützung von Claude Code (Anthropic)
entstanden; die Fehler wurden im Spiel beobachtet, nachgestellt und geprüft.

## Lizenz und Rechte

Der Code und die Dokumentation dieses Projekts stehen unter der [MIT-Lizenz](LICENSE). ANSTOSS 3 und alle Inhalte
des Spiels gehören den jeweiligen Rechteinhabern; die Lizenz erstreckt sich nicht darauf.
