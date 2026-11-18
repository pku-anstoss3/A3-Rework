"""Build the installer of the unofficial Anstoss 3 patch from the patch table in a3patch.py.

Usage: python tools/patch_bauen.py
Writes patch-<VERSION>/ with .cmd, .ps1, LIESMICH.txt, CHANGELOG.txt and the zip of these four files, and the reference
files build/endpaket-<VERSION>/ (patched copies of the files in original/, used by tools/patch_test.ps1).

The installer contains no game files, only offsets with old and new bytes and the old and new wording of 20 event
texts. It changes four files: anstoss3.exe, deb\\MeineDialoge.rch, texte\\Ereignis.saq and (optional) ddraw.dll. The
corrections of anstoss3.exe form two installer groups (wish of the user, 18.11.2026: only these two):
  B  "Optische Änderungen" (statistics, display, texts), always installed
  L  "Berechnungskorrekturen und -änderungen", can be deselected; decided by the kind-of-error group of the entry
     (GRUPPEN). Internal names keep the older word "Spiellogik" (switch -OhneSpiellogik, tools/patch_test.ps1).
Expected SHA-256 values are computed here by applying the patches to the untouched files in original/.

All texts shipped with the patch are defined in this file. Rules of the user: factual and formal, no names of persons,
change log grouped by kind of error. Every entry has a short title and three parts: the error, the correction and its
effect. Entries of the messages and events (since 1.45, tools/patch_meldungen.py) have a fourth part: the estimated
frequency of the message (wish of the user, 18.11.2026).
The window shows the entries as a list; "Details ..." opens the three parts of the selected entry (wish of the user,
16.11.2026: larger window, clean list, details per entry).
"""
import hashlib
import os
import re
import textwrap
import zipfile
import struct
import a3patch
from patch_meldungen import MELDUNGEN

VERSION = '1.46'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, f'patch-{VERSION}')
REF = os.path.join(ROOT, 'build', f'endpaket-{VERSION}')
EXE_SHA = '89B88EF522574098014E9F1E68448593E2A992A8EBD0318760E552C3B15F6B2A'
RCH_SHA = 'AA68E14E697CE944CBF3AF4F8AE1769965597B3BB6087A9BE01B32006E927536'
DDRAW_SHA = 'B2CB0FD03C1D1A0401E0468DAADE7B6D2A33D3EA75897F3E836D68E1E85C3440'
RCH_IDS = ['tagesform-ueberschrift']
DDRAW_IDS = ['hw-vertexverarbeitung']
# Former contents that are accepted in addition to the original bytes: file offset -> [(patch version, hex string)].
# "%s Version 1.4x/%s" was written by the earlier patches.
FRUEHER = {0x00482378: [(v, '25732056657273696F6E20' + v.encode('ascii').hex().upper() + '2F257300')
                        for v in ('1.41', '1.42', '1.43', '1.44', '1.45')]}
# Test build of 17./18.11.2026 (build/kandidat-1.45-nacht before the correction of K15, installed by the user for a
# test): 'trennung-1083' with the 'push 0' before the random call. Accepted so that this state can be updated.
FRUEHER[0x001F9F76] = [('1.45 (Testfassung)',
                        '8B4D0CE8E98410006A006A0AE8890819000FBFC8BAF6FFFFFF2BD1528B4D0CE83F71100050FF75FC6A028B4D0CE8B4781000'
                        '50FF750C683B0400006A60FF7508E8887000009090')]
NB = chr(0xA0)      # no line break here in wrapped texts; written as a normal space
# Patches of a3patch.py that are candidates only: built into test files, not part of this installer.
# Empty since 1.45: all points of docs/korrekturliste-meldungen.md released by the user are part of the installer;
# 'jugend-abwerben-vertrag' was a candidate on 18.11.2026 and is part of 1.46.
KANDIDATEN = set()

# Kinds of error: (title, belongs to the game-logic group of the installer)
GRUPPEN = [('Statistik „Historisches“', False), ('Vereinsstatistik', False), ('Liga-Statistik', False),
           ('Spielerdetails', False), ('Saisonabschluss', False),
           ('Trainer, Co-Trainer und Torwarttrainer', True), ('Fans und Presse', True), ('Finanzen', True),
           ('Allgemein', False), ('Darstellung', False),
           ('Meldungen und Ereignisse: Anzeige und Texte', False), ('Meldungen und Ereignisse: Wirkung', True),
           ('Jugendspieler', True)]
G_ALLGEMEIN, G_DARSTELLUNG, G_MELD_OPTISCH, G_MELD_LOGIK, G_JUGEND = 8, 9, 10, 11, 12
REIHENFOLGE = [0, 1, 2, 3, 4, 5, G_JUGEND, 6, 7, G_MELD_OPTISCH, G_MELD_LOGIK, G_ALLGEMEIN, G_DARSTELLUNG]    # order of the lists
LOGIK_MARKE = ' (Berechnung, abwählbar)'
LOGIK_TEXT = ('Die Berechnungskorrekturen und -änderungen greifen in den Spielverlauf ein. Sie betreffen Funktionen und '
              'Ereignisse, die im Spiel angelegt sind, wegen eines Programmfehlers aber nie, zu selten oder fehlerhaft '
              'gearbeitet haben; einige Ereignisse treten dadurch erstmals oder häufiger ein. Die geschätzte Häufigkeit '
              'steht bei den Einträgen unter „Details ...“. Diese Gruppe kann abgewählt werden; die optischen Änderungen '
              '(Anzeigen, Statistiken, Texte) werden immer installiert.')

# One entry per corrected error: patch ids, kind of error, version of introduction, short title, and the three parts
# shown under "Details": fehler (the error), korrektur (what the correction does), auswirkung (effect and extent).
# Numbers: docs/befund-personal.md, docs/befund-notenschnitt.md, docs/befund-finanzen.md, analyse/skripte/wirkung*.py.
EINTRAEGE = [
    dict(ids=['beste-mannschaft'], gruppe=0, seit='1.41',
         titel='„Beste Mannschaft“: Tabelle wurde ab der 21. Saison überschrieben',
         fehler='Ab der 21. Saison wurde beim Weiterrücken der Tabelle der falsche Eintrag geleert. Ein Eintrag '
         'vervielfachte sich dadurch von Saison zu Saison, bis alle 20 Zeilen dieselbe Mannschaft zeigten.',
         korrektur='Beim Weiterrücken wird wieder der letzte Eintrag freigemacht; die Tabelle wird saisonweise '
         'fortgeschrieben.',
         auswirkung='Wirkt ab dem nächsten Saisonwechsel. Bereits mehrfach vorhandene Einträge werden nicht berichtigt; '
         'sie rücken mit jeder weiteren Saison aus der Tabelle.'),
    dict(ids=['beste-mannschaft-anzeige'], gruppe=0, seit='1.41',
         titel='„Beste Mannschaft“: zuletzt abgeschlossene Saison fehlte',
         fehler='Ab der 21. Saison zeigte der Bildschirm nur 19 der 20 Einträge; die zuletzt abgeschlossene Saison '
         'fehlte.',
         korrektur='Der Bildschirm zeigt wieder alle 20 Einträge.',
         auswirkung='Sofort sichtbar. Reine Anzeige.'),
    dict(ids=['aufstieg-doppelt'], gruppe=0, seit='1.41',
         titel='„Rekordaufsteiger“: Aufstiege in die 2. Bundesliga doppelt gezählt',
         fehler='Aufstiege aus den Regionalligen in die 2. Bundesliga wurden an zwei Stellen gemeldet und deshalb '
         'doppelt gezählt.',
         korrektur='Die zweite Meldung zählt nicht mehr mit.',
         auswirkung='Ab dem nächsten Saisonwechsel wird richtig gezählt. Bereits zu hoch gezählte Aufstiege bleiben '
         'stehen.'),
    dict(ids=['aufstieg-rl-sued'], gruppe=0, seit='1.41',
         titel='„Rekordaufsteiger“: Aufstiege in die Regionalliga Süd ohne Spalte',
         fehler='Aufstiege in die Regionalliga Süd wurden keiner Spalte zugeordnet; die Gesamtzahl wuchs, die Spalten '
         'nicht.',
         korrektur='Sie werden wie die Aufstiege in die Regionalliga Nord in der dritten Spalte geführt.',
         auswirkung='Ab dem nächsten Saisonwechsel. Frühere Aufstiege in die Regionalliga Süd fehlen weiterhin in den '
         'Spalten.'),
    dict(ids=['abstieg-spanien'], gruppe=0, seit='1.41',
         titel='„Rekordabsteiger“: Spanien in der falschen Spalte',
         fehler='Abstiege aus der spanischen 1. Liga wurden in der Spalte der 2. Liga geführt.',
         korrektur='Sie werden in der Spalte der 1. Liga geführt.',
         auswirkung='Ab dem nächsten Saisonwechsel. Ältere Einträge bleiben in der falschen Spalte.'),
    dict(ids=['trainer-eps'], gruppe=0, seit='1.41',
         titel='„Erfolgreichste Trainer“: Champions League und Europäischer Supercup fehlten',
         fehler='Im Eintrag eines menschlichen Managers zählte die Spalte „EPs“ nur den Europapokal. '
         'Champions-League-Siege und Europäische Supercups fehlten, während sie bei Computertrainern gezählt wurden.',
         korrektur='Champions-League-Siege zählen zu „EPs“, Europäische Supercups zu „Sonstige“, wie bei den '
         'Computertrainern.',
         auswirkung='Der Eintrag eines Managers wird mit dessen nächstem Titelgewinn berichtigt.'),
    dict(ids=['trainer-reihenfolge'], gruppe=0, seit='1.42',
         titel='„Erfolgreichste Trainer“: zuletzt gewonnener Titel fehlte',
         fehler='Der Eintrag eines menschlichen Managers wurde geschrieben, bevor der Zähler des gerade gewonnenen Titels '
         'erhöht war. Er lag deshalb stets einen Titel zurück.',
         korrektur='Der Zähler wird erhöht, bevor der Eintrag geschrieben wird.',
         auswirkung='Mit dem nächsten Titelgewinn stimmt der Eintrag.'),
    dict(ids=['vereinsliste-spiele'], gruppe=1, seit='1.42',
         titel='Vereinsliste „Meiste Spiele“: keine neuen Spieler nach 50 Einträgen',
         fehler='Das Kennzeichen „im Verein“ wurde beim Abgang eines Spielers für diese Liste nie gelöscht. War die '
         'Liste mit 50 Spielern gefüllt, wurde kein weiterer Spieler aufgenommen.',
         korrektur='Nach jedem Pflichtspiel werden die Kennzeichen aus dem aktuellen Kader neu gesetzt. Ehemalige '
         'Spieler können dadurch von Spielern des Kaders verdrängt werden.',
         auswirkung='Wirkt ab dem nächsten Pflichtspiel. Einsätze, die vor der Installation nicht erfasst wurden, können '
         'nicht nachgetragen werden; neu aufgenommene Spieler beginnen mit dem ersten erfassten Einsatz.'),
    dict(ids=['tagesform', 'tagesform-ueberschrift'], gruppe=2, seit='1.43',
         titel='„Tagesform“: Durchschnittsnote statt eines nicht erläuterten Werts',
         fehler='Die Statistik beruht auf den Noten der Spieler im letzten Spiel ihrer Mannschaft, zeigte aber das '
         'Zwanzigfache der Durchschnittsnote unter der Überschrift „Form“. Spieler ohne Note gingen mit der Note 0 in '
         'den Durchschnitt ein, und die Mannschaft mit den schlechtesten Noten stand auf Platz 1.',
         korrektur='Angezeigt wird die Durchschnittsnote der Mannschaft im letzten Spiel mit einer Nachkommastelle unter '
         'der Überschrift „Note“. Ein niedrigerer Wert ist besser, die beste Mannschaft steht oben; berücksichtigt '
         'werden nur Spieler, die in diesem Spiel eine Note erhalten haben. Für die Überschrift wird die Textdatei '
         'deb\\MeineDialoge.rch angepasst.',
         auswirkung='Reine Anzeige. Die Statistik wird nach jedem Spieltag neu berechnet; ein Spielstand, der vor der '
         'Installation gespeichert wurde, zeigt bis zum nächsten Spieltag unzutreffende Werte.'),
    dict(ids=['notenschnitt-details'], gruppe=3, seit='1.43',
         titel='Seite „Noten“: Notenschnitt der Saison zu gut',
         fehler='Der Notenschnitt der Saison wurde durch die Zahl aller Einsätze geteilt, auch der Einsätze ohne Note '
         '(zum Beispiel nach einer späten Einwechslung), und fiel dadurch zu gut aus.',
         korrektur='Geteilt wird nur durch die benoteten Einsätze, wie in der Statistik „Notenschnitt Mannschaft“.',
         auswirkung='Sofort sichtbar. Reine Anzeige. Beispiel: Bei fünf Einsätzen, davon einer ohne Note, stand 3,0 '
         'statt 3,8.'),
    dict(ids=['aufsteiger-liste'], gruppe=4, seit='1.42',
         titel='Übersicht der Auf- und Absteiger: falsche Vereine unter „Aufsteiger 3. Liga“',
         fehler='Unter „Aufsteiger 3. Liga“ wurden die Aufsteiger in die 2. Bundesliga erneut aufgeführt; dadurch '
         'fehlten je Regionalliga zwei der vier Neulinge.',
         korrektur='Die Liste führt nur noch die Aufsteiger in die Regionalligen.',
         auswirkung='Ab dem nächsten Saisonwechsel. Die Zusammensetzung der Ligen ändert sich nicht.'),
    dict(ids=['trainer-nachwuchs'], gruppe=5, seit='1.41',
         titel='Ehemalige Spieler wurden nie Trainer oder Torwarttrainer',
         fehler='Das Spiel sieht vor, dass Spieler nach dem Karriereende auf eine Warteliste für Trainer und '
         'Torwarttrainer gelangen und frei werdende Stellen übernehmen. Wegen einer fehlerhaften Abfrage wurde nie ein '
         'Spieler eingetragen; ausscheidende Trainer wurden daher stets über das Ersatzverfahren des Spiels durch einen '
         'Nachfolger mit Mindestkompetenz (1 bis 3) ersetzt.',
         korrektur='Die Abfrage ist berichtigt, die Warteliste arbeitet. Das Ersatzverfahren ist unverändert und greift '
         'weiterhin, wenn im jeweiligen Land niemand wartet.',
         auswirkung='In zwei Prüfläufen über einen Saisonwechsel wurden 3 von 24 beziehungsweise 5 von 34 frei '
         'gewordenen Trainerstellen aus der Warteliste besetzt (Kompetenz 12 bis 14). Stellen für Torwarttrainer wurden '
         'in diesen Läufen nur in einem Land frei, in dem kein ehemaliger Torhüter wartete. Trainer aus der Warteliste '
         'erscheinen erst, wenn eine Stelle frei wird, und in der Angebotsliste erst, sobald das Spiel sie dort '
         'aufnimmt.'),
    dict(ids=['trainer-geburt'], gruppe=5, seit='1.41',
         titel='Trainer aus der Warteliste übernahmen das Geburtsdatum des Vorgängers',
         fehler='Trainer, die aus der Warteliste übernommen werden, erhielten nicht ihr eigenes Geburtsdatum, sondern '
         'behielten das ihres Vorgängers.',
         korrektur='Das Geburtsdatum wird übernommen, wie es das Spiel bei Torwarttrainern bereits tut.',
         auswirkung='Betrifft ausschließlich die Trainer aus der Warteliste; ohne die vorstehende Korrektur blieb der '
         'Fehler ohne Wirkung.'),
    dict(ids=['trainer-ausgleich'], gruppe=5, seit='1.41',
         titel='Jährliche Anhebung der Trainer- und Managerkompetenz wurde nicht gespeichert',
         fehler='Das Spiel hebt einmal jährlich in Ländern, in denen die durchschnittliche Kompetenz der Trainer und '
         'Manager unter 6 liegt, jede zehnte Person um 1 bis 2 Punkte an. Der Zuschlag wurde berechnet, aber nicht im '
         'Wert der Person gespeichert.',
         korrektur='Der Zuschlag wird gespeichert. Die übrigen Stufen dieses Ausgleichs, darunter die Absenkung bei '
         'einem Durchschnitt über 10, arbeiteten bereits und sind unverändert.',
         auswirkung='Im Prüflauf über einen Saisonwechsel stieg der Wert bei 49 Trainern und Managern ab 46 Jahren um '
         '1 oder 2 Punkte (Skala 0 bis 15); ohne die Korrektur waren es in zwei Vergleichsläufen 7 und 0. Das '
         f'Spiel führt insgesamt rund 1{NB}440 Trainer und Manager.'),
    dict(ids=['verhasst-noten'], gruppe=6, seit='1.43',
         titel='Fan-Status „verhasst“: Einsätze ohne Note zählten mit',
         fehler='Bei der Prüfung des Notenschnitts der letzten zehn Spieltage zählten Einsätze ohne Note als Einsätze '
         'mit der Note 0. Der Schnitt fiel dadurch zu gut aus, und die verlangte Mindestzahl von Einsätzen wurde auch '
         'durch Einsätze ohne Note erreicht.',
         korrektur='Es zählen nur benotete Einsätze, wie in der Statistik „Notenschnitt Mannschaft“. Die Schwellen '
         'des Spiels (Schnitt 4,5 oder schlechter, bei bestimmten Spielereigenschaften 3,8 oder schlechter) sind '
         'unverändert.',
         auswirkung='Nachgerechnet an einer vollständigen Saison der 1. Bundesliga (18 Vereine, 397 eingesetzte '
         f'Spieler): Die Bedingung mit der Schwelle 4,5 war an 45 statt 33 von 13{NB}498 Spieler-Spieltagen erfüllt, '
         'bei 16 statt 13 Spielern. Bei der Schwelle 3,8 steigt die Zahl der Fälle um etwa ein Viertel.'),
    dict(ids=['totalausfall'], gruppe=6, seit='1.43',
         titel='Zeitungsmeldung „… erneut ein Totalausfall“ konnte nie erscheinen',
         fehler='Die Meldung ist im Spiel enthalten, konnte aber nie erscheinen. Der dafür berechnete Saisonschnitt eines '
         'Spielers wurde fehlerhaft ausgelesen und erreichte höchstens den Wert 3,5; die Meldung verlangt einen Schnitt '
         'schlechter als 4,0.',
         korrektur='Der Saisonschnitt wird richtig ausgelesen; es gehen nur benotete Einsätze der laufenden Saison ein. '
         'Die Meldung erscheint unter den im Spiel festgelegten Bedingungen (letzte Note 5,0 oder schlechter, mehr als '
         'zehn Einsätze, Saisonschnitt schlechter als 4,0 sowie eine unveränderte Bedingung zum Abschneiden des Vereins) '
         'mit dem dort festgelegten Abzug von 6 Punkten beim Teilwert „Presse“ der Motivation.',
         auswirkung='Nachgerechnet an derselben Saison: Die Notenbedingungen waren 30-mal erfüllt, bei 13 von 383 '
         'benoteten Spielern, im Mittel also weniger als zweimal je Verein und Saison; die Bedingung zum Verein kommt '
         'hinzu. Der Abzug entspricht knapp einem Punkt der Gesamtmotivation (Skala 0 bis 100).'),
    dict(ids=['goldkettchen'], gruppe=6, seit='1.43',
         titel='Zeitungsmeldung „Goldkettchen und teure Autos“: falsche Noten, Abzug nie angewendet',
         fehler='Die Meldung gehört zu den Zufallsereignissen aus dem Privatleben eines Spielers. Der Notenschnitt der '
         'letzten drei Einsätze wurde fehlerhaft ausgelesen, sodass mittlere Noten (2,5 bis 3,5) die Meldung auslösten, '
         'schlechte Noten dagegen nicht. Der mit der Meldung übergebene Abzug von 2 Punkten beim Teilwert „Presse“ der '
         'Motivation wurde nie angewendet.',
         korrektur='Ausgewertet werden die letzten drei benoteten Einsätze der laufenden Saison; die Meldung setzt einen '
         'Schnitt schlechter als 4,0 voraus, und der Abzug wird angewendet. Die übrigen Bedingungen (Spielerstärke, '
         'Abschneiden des Vereins, Auslosung des Ereignisses) sind unverändert. Der Schwellenwert des Programms wird '
         'dabei wie bei der Meldung „Totalausfall“ als Note 4,0 gelesen; aus dem Programm selbst ist diese Lesart '
         'nicht zweifelsfrei zu belegen.',
         auswirkung=f'Nachgerechnet an derselben Saison: Die Notenbedingung galt an 14,7{NB}% der Spieler-Spieltage. '
         'Die Meldung setzt zusätzlich die Auslosung des Ereignisses und die Bedingung zum Verein voraus. Der Abzug '
         'entspricht rund 0,3 Punkten der Gesamtmotivation.'),
    dict(ids=['konto-anlagen'], gruppe=7, seit='1.44',
         titel='Bilanz: Bankguthaben bei laufenden Geldanlagen zu niedrig',
         fehler='Das Vereinsvermögen führt eine Geldanlage mit dem eingezahlten Betrag; ihr Wertzuwachs wird erst beim '
         'Auflösen als Einnahme gebucht. Das Bankguthaben wurde dagegen als Vermögen abzüglich des aktuellen Werts der '
         'Anlagen berechnet. Mit jedem Wertzuwachs sank deshalb das Bankguthaben, obwohl kein Geld abgeflossen war, und '
         'das „Aktuelle Vereinsvermögen“ enthielt den Zuwachs nicht. Beim Auflösen stieg das Bankguthaben um die '
         'Auszahlung und zusätzlich um den gesamten Zuwachs seit dem Anlegen.',
         korrektur='Das Bankguthaben wird als Vermögen abzüglich der eingezahlten Beträge berechnet. Die Zeile '
         '„Aktuelles Vereinsvermögen“ der Bilanz zeigt das Bankguthaben zuzüglich des aktuellen Werts der Anlagen und '
         'abzüglich der Kredite. Gespeicherte Werte, die Einnahmen und Ausgaben der Saison und die Besteuerung bleiben '
         'unverändert.',
         auswirkung='Der bisher abgezogene Zuwachs steht sofort im Bankguthaben; beim Auflösen steigt es nur noch um die '
         'Auszahlung. Es entsteht und verschwindet kein Geld: Nach dem Auflösen aller Anlagen ergibt sich derselbe '
         'Betrag wie ohne die Korrektur. Das Bankguthaben ist auch für die Dispozinsen und für die Prüfung beim Anlegen '
         'maßgeblich; Dispozinsen fallen nur noch bei tatsächlichem Minus an. In einem Prüfspielstand stand das '
         'Bankguthaben zweier Vereine um 755 Mio. und 571 Mio. zu niedrig (Anlagen im Wert von 1,005 Mrd. und '
         '871 Mio. bei eingezahlten 250 Mio. und 300 Mio.). Die Zeile „Vereinsvermögen am Anfang der Saison“ ist '
         'unverändert und enthält den Zuwachs der Anlagen weiterhin nicht.'),
    dict(ids=['jugend-abwerben-vertrag'], gruppe=G_JUGEND, seit='1.46',
         titel='Abgeworbene Jugendspieler erhielten keine Vertragslaufzeit',
         fehler='Wird ein Jugendspieler ohne Vertrag über die Liste der vertragslosen Jugendspieler von einem anderen '
         'Verein in die eigene Jugend geholt, trug das Programm das Gehalt ein, nicht aber die Laufzeit des '
         'Jugendvertrags. Der Spieler stand mit einer Restlaufzeit von 0 Jahren in der Jugend. An den beiden '
         'vergleichbaren Stellen des Programms, darunter der Jugendvertrag im eigenen Jugendbereich, werden zusammen '
         'mit dem Gehalt zehn Jahre eingetragen. Ein Spieler ohne Restlaufzeit gilt im Profikader als abwesend: In der '
         'vierwöchigen Probezeit wurde er mit dem Symbol „abwesend“ angezeigt und war nicht einsetzbar.',
         korrektur='Beim Abwerben wird wie an den beiden anderen Stellen eine Laufzeit von zehn Jahren eingetragen.',
         auswirkung='Betrifft nur Vereine menschlicher Manager und nur Jugendspieler, die nach der Installation '
         'abgeworben werden. Bereits abgeworbene Spieler in bestehenden Spielständen behalten die Restlaufzeit von '
         '0 Jahren. Die Altersgrenze der Jugend und das Gehalt sind unverändert.'),
    dict(ids=['versionsanzeige'], gruppe=G_ALLGEMEIN, seit=VERSION,
         titel=f'Versionsangabe {VERSION}',
         fehler='',
         korrektur=f'Die Versionsangabe des Spiels lautet {VERSION}.',
         auswirkung='An der Versionsangabe ist die installierte Fassung des Patches erkennbar.'),
    dict(ids=['hw-vertexverarbeitung'], gruppe=G_DARSTELLUNG, seit='1.41', ziel='ddraw',
         titel='Eingabeverzögerung nach Mausklicks (optional, nur GOG-Ausgabe)',
         fehler='Mit aktuellen Grafikkarten kann das Spiel nach jedem Mausklick 2 bis 3 Sekunden verzögert reagieren '
         '(festgestellt mit einer Radeon RX 6800 XT). Die ddraw.dll der GOG-Ausgabe schaltet auf eine langsame '
         'Verarbeitung im Hauptprozessor um, wenn der Grafiktreiber eine bestimmte Fähigkeit nicht meldet.',
         korrektur='Die Umschaltung unterbleibt (Komponente „Angepasste ddraw.dll“).',
         auswirkung='Auf Systemen ohne dieses Verhalten bleibt die Anpassung ohne Wirkung. Geprüft wurde sie in der '
         '2D-Oberfläche des Spiels. Treten Darstellungsfehler auf, kann die Option abgewählt werden; die Datei wird '
         'dann auf ihren ursprünglichen Stand zurückgesetzt.'),
]
# Messages and events (docs/korrekturliste-meldungen.md), with the estimated frequency as a fourth part
EINTRAEGE += [dict(ids=m['ids'], gruppe=G_MELD_LOGIK if m['logik'] else G_MELD_OPTISCH, seit='1.45', titel=m['titel'],
                   fehler=m['fehler'], korrektur=m['korrektur'], auswirkung=m['auswirkung'], haeufigkeit=m['haeufigkeit'])
              for m in MELDUNGEN]
EINTRAEGE.append(dict(
    ids=[], gruppe=G_MELD_OPTISCH, seit='1.45', ziel='saq',
    titel='Texte von 20 Meldungen berichtigt (Datei texte\\Ereignis.saq)',
    fehler='In 20 Texten fehlten Namen (im Spiel erschien stattdessen „%s“), waren Namen vertauscht oder der Text '
    'nannte eine andere Wirkung als die tatsächliche, zum Beispiel einen Ausfall statt einer Beeinträchtigung.',
    korrektur='Die Texte sind berichtigt: Platzhalter und Reihenfolge der Namen, Angaben zu Dauer und Wirkung. Die '
    'Länge der Datei bleibt unverändert, weil das Spiel sie sonst nicht lädt.',
    auswirkung='Nur der Wortlaut der Meldungen. Die Datei wird nur angepasst, wenn alle 20 Texte im ursprünglichen '
    'Wortlaut vorliegen; andernfalls bleibt sie unverändert.',
    haeufigkeit='Betrifft 20 Meldungen unterschiedlicher Häufigkeit; siehe die Einträge zu den einzelnen Meldungen.'))

# Corrected event texts of texte\Ereignis.saq: (number, [(old part, new part)]). The loader 0x005EF298 demands exactly
# 273692 bytes of text (0x005EF303), so the total length must stay the same: text SAQ_FUELL is padded with blanks.
SAQ_SHA = None      # set in saq_build()
SAQ_FUELL = 1210
SAQ_TEXTE = [
    (285, [('und 20 Punkte Beliebtheit in der Öffentlichkeit und bei den Medien kosten',
            'und je 5 Punkte Beliebtheit in der Öffentlichkeit, bei den Fans und bei den Medien kosten')]),
    (888, [('einer Fanblockade ', 'einer Fanblockade')]),
    (889, [('wegen schlechtem Wetter', 'schlechten Wetters')]),
    (954, [('%s', '%1')]),
    (1083, [('mit Ihrem Freund', 'mit ihrem Freund')]),
    (1094, [('%1, die Freundin von %2, entdeckt in der Jackentasche Ihres Freundes',
             '%2, die Freundin von %1, entdeckt in der Jackentasche ihres Freundes')]),
    (1115, [('%s, die Frau von %s ist', '%2, die Frau von %1, ist')]),
    (1116, [('%s', '%1')]),
    (1117, [('%s', '%1')]),
    (1127, [('%1, die Frau von %2, setzt', '%2, die Frau von %1, setzt')]),
    (1178, [('Ihrem Mann', 'ihrem Mann')]),
    (1194, [('Er fällt zwei Wochen aus.', 'Er ist zwei Wochen angeschlagen.')]),
    (1207, [('Seit Single %1', 'Seit %1')]),
    (1210, [(' Seine Frau %2 ist darüber so entsetzt, daß Sie ihm sein Hobby einfach verbietet. Der Spieler kann in den '
             'nächsten Tagen nur eingeschränkt trainieren.', ' Er gibt sein Hobby daraufhin auf.')]),
    (1224, [('Die nächste Woche ist er ziemlich angeschlagen.', 'Er fällt zwei Wochen aus.')]),
    (1276, [('%s', '%1')]),
    (1294, [(' "Der Rasen', 'Ihr Spieler %1 bricht das Training ab. "Der Rasen')]),
    (1296, [('bei meiner Frau %2 bleiben', 'bei meiner Frau bleiben')]),
    (1338, [('für %s', 'für %1')]),
    (1355, [('%s', '%1')]),
]


def saq_build():
    """(original file, patched file, [(number, old bytes, new bytes)]) for texte\\Ereignis.saq."""
    d = open(os.path.join(ROOT, 'original', 'texte', 'Ereignis.saq'), 'rb').read()
    size, count = struct.unpack_from('<ii', d, 0)
    assert size == 273692 and count == 2483
    plain, key = bytearray(), size & 0xFF
    for c in d[8:8 + size]:
        plain.append(c ^ key)
        key = c
    parts = bytes(plain).split(b'\0')
    texte, delta = [], 0
    for nr, pairs in SAQ_TEXTE:
        alt = parts[nr - 1]
        neu = alt.decode('cp1252')
        for a, b in pairs:
            assert neu.count(a) == 1, (nr, a)
            neu = neu.replace(a, b)
        neu = neu.encode('cp1252')
        delta += len(neu) - len(alt)
        texte.append([nr, alt, neu])
    assert delta <= 0, delta                                   # shorter in total: pad one text with blanks
    for t in texte:
        if t[0] == SAQ_FUELL:
            t[2] += b' ' * -delta
    for nr, alt, neu in texte:
        parts[nr - 1] = neu
    new = b'\0'.join(parts)
    assert len(new) == size
    out, key = bytearray(), size & 0xFF
    for c in new:
        key = c ^ key
        out.append(key)
    return d, d[:8] + bytes(out) + d[8 + size:], [tuple(t) for t in texte]


def ps_texte(texte):
    return '\n'.join("        @{{ Nr = {}; Alt = '{}'; Neu = '{}' }}".format(nr, alt.hex().upper(), neu.hex().upper())
                     for nr, alt, neu in texte)


# Further sections of the change log that are not corrections of the game: version -> [(title, [texts])]
ZUSATZ = {
    '1.45': [('Installationsprogramm', [
        'Die Korrekturen sind in zwei Gruppen geteilt: optische Änderungen (Anzeigen, Statistiken, Texte; werden immer '
        'installiert) und Berechnungskorrekturen und -änderungen (abwählbar). Die frühere Gruppe „Spiellogik“ gehört '
        'zur zweiten Gruppe.',
        'Neu sind 42 Einträge zu Meldungen und Ereignissen. Bei ihnen nennt „Details ...“ zusätzlich die geschätzte '
        'Häufigkeit der Meldung. Die Angaben sind aus den Lostabellen des Programms berechnet, nicht im Spiel gemessen: '
        'Die täglichen Ereignisse laufen nur für Vereine menschlicher Manager und an rund 230 Tagen je Saison; die '
        'Schätzung gilt jeweils unter der genannten Voraussetzung.',
        'Zusätzlich wird die Textdatei texte\\Ereignis.saq angepasst (20 Meldungstexte).'])],
    '1.44': [('Installationsprogramm', [
        'Das Fenster ist größer und in der Größe veränderbar. Die behobenen Fehler stehen in einer Liste nach '
        'Fehlerart; „Details ...“ (oder ein Doppelklick) zeigt zu jedem Eintrag den Fehler, die Korrektur und die '
        'Auswirkung.'])],
    '1.43': [('Installationsprogramm', [
        'Die Korrekturen der Spiellogik bilden eine eigene Gruppe, die bei der Installation abgewählt und später '
        'wieder hinzugefügt werden kann. Zur Gruppe gehören auch die mit Version 1.41 eingeführten Korrekturen zu '
        'Trainern, Co-Trainern und Torwarttrainern.',
        'Neben der Programmdatei anstoss3.exe wird die Textdatei deb\\MeineDialoge.rch angepasst '
        '(Spaltenüberschrift der Liga-Statistik „Tagesform“).'])],
}
VERSIONEN = [('1.46', '18.11.2026'), ('1.45', '18.11.2026'), ('1.44', '16.11.2026'), ('1.43', '16.11.2026'), ('1.42', '16.11.2026'), ('1.41', '15.11.2026')]   # newest first


def is_logic(e):
    return GRUPPEN[e['gruppe']][1]


def installer_group(pid):
    """'L' (game logic, can be deselected) or 'B' (always installed) for a patch id."""
    for e in EINTRAEGE:
        if pid in e['ids']:
            return 'L' if is_logic(e) else 'B'
    raise KeyError(pid)


def group_title(e):
    title = GRUPPEN[e['gruppe']][0]
    return title + (LOGIK_MARKE if is_logic(e) else ' (optional)' if e['gruppe'] == G_DARSTELLUNG else '')


def kind(e):
    """Column "Art" of the window list."""
    if e['gruppe'] == G_DARSTELLUNG:
        return 'optional'
    if e['gruppe'] == G_ALLGEMEIN:
        return 'allgemein'
    return 'Berechnung (abwählbar)' if is_logic(e) else 'Optische Änderung'


def sites(sha, ids, group=installer_group):
    """[(patch id, installer group, offset, [accepted old contents, original first], [their names], new content)]"""
    out = []
    for pid in ids:
        for off, old, new in a3patch.TARGETS[sha][pid]:
            former = FRUEHER.get(off, [])
            alt = [old.upper()] + [h for _, h in former]
            names = ['1.40'] + [v for v, _ in former] if former else []
            assert all(len(a) == len(new) for a in alt), (pid, hex(off))
            out.append((pid, group(pid), off, alt, names, new.upper()))
    return out


def patched(name, sha, st, groups='BL'):
    """Content of original/<name> with the sites of the given installer groups applied."""
    data = bytearray(open(os.path.join(ROOT, 'original', name), 'rb').read())
    assert hashlib.sha256(data).hexdigest().upper() == sha, name
    for pid, g, off, alt, _, new in st:
        assert data[off:off + len(new) // 2] == bytes.fromhex(alt[0]), (name, pid, hex(off))
        if g in groups:
            data[off:off + len(new) // 2] = bytes.fromhex(new)
    return bytes(data)


def sha256(data):
    return hashlib.sha256(data).hexdigest().upper()


def ps_sites(st):
    out = []
    for pid, g, off, alt, names, new in st:
        extra = ' AltName = @({});'.format(', '.join(f"'{n}'" for n in names)) if names else ''
        out.append("        @{{ Name = '{}'; Gruppe = '{}'; Offset = 0x{:X}; Alt = @({});{} Neu = '{}' }}".format(
            pid, g, off, ', '.join(f"'{a}'" for a in alt), extra, new))
    return '\n'.join(out)


def ps_text(s):
    """Windows PowerShell treats typographic quotes as quote characters: use guillemets inside the script."""
    return (s.replace('„', '»').replace('“', '«').replace('‚', '›').replace('‘', '‹').replace('’', '‹')
            .replace("'", "''").replace(NB, ' '))


def ordered(version=None):
    """Entries in the order of GRUPPEN, optionally only those introduced in one version."""
    return [e for g in REIHENFOLGE for e in EINTRAEGE
            if e['gruppe'] == g and (version is None or e['seit'] == version)]


def wrap(text, width, first, rest):
    text = re.sub(r'(\d\.) ', lambda m: m.group(1) + NB, text)    # keep "2. Bundesliga", "21. Saison" on one line
    return textwrap.fill(text, width=width, initial_indent=first, subsequent_indent=rest,
                         break_on_hyphens=False).replace(NB, ' ')


def entry_lines(e, width):
    """Change log: title, then the labelled parts with a hanging indent."""
    out = [wrap(e['titel'], width, '  * ', '    ')]
    for label, key in (('Fehler:     ', 'fehler'), ('Korrektur:  ', 'korrektur'), ('Auswirkung: ', 'auswirkung'),
                       ('Häufigkeit: ', 'haeufigkeit')):
        if e.get(key):
            out.append(wrap(e[key], width, '      ' + label, '      ' + ' ' * len(label)))
    return out


def changelog():
    out = ['ANSTOSS 3 - Inoffizieller Patch', 'Änderungsprotokoll', '=' * 31, '',
           wrap('Je Version sind die behobenen Fehler nach Fehlerart gegliedert. Zu jedem Eintrag stehen der Fehler, '
                'die Korrektur und ihre Auswirkung, bei Meldungen und Ereignissen außerdem die geschätzte Häufigkeit.',
                100, '', ''), '',
           wrap('Gruppen mit dem Zusatz „Berechnung, abwählbar“ (bis Version 1.44: „Spiellogik, abwählbar“): '
                + LOGIK_TEXT, 100, '', ''), '']
    for v, datum in VERSIONEN:
        out += ['', f'Version {v} ({datum})', '=' * (len(f'Version {v} ({datum})'))]
        sections = []
        for e in ordered(v):
            if not sections or sections[-1][0] != group_title(e):
                sections.append((group_title(e), []))
            sections[-1][1].extend(entry_lines(e, 100) + [''])
        sections += [(title, [line for t in texts for line in (wrap(t, 100, '  * ', '    '), '')])
                     for title, texts in ZUSATZ.get(v, [])]
        sections.sort(key=lambda s: s[0] == GRUPPEN[G_ALLGEMEIN][0])           # the version entry stays last
        for title, lines in sections:
            out += ['', title, '-' * len(title)] + lines[:-1]
        out += ['']
    return '\n'.join(out).rstrip() + '\n'


def window_entries():
    """PowerShell hashtables for the list and the details dialog of the window."""
    out = []
    for e in ordered():
        f = {k: ps_text(e.get(k, '')) for k in ('titel', 'fehler', 'korrektur', 'auswirkung', 'haeufigkeit')}
        out.append("    @{{ Bereich = '{}'; Art = '{}'; Seit = '{}'; Titel = '{}'\n"
                   "       Fehler = '{}'\n       Korrektur = '{}'\n       Auswirkung = '{}'\n"
                   "       Haeufigkeit = '{}' }}".format(
                       ps_text(GRUPPEN[e['gruppe']][0]), ps_text(kind(e)), e['seit'],
                       f['titel'], f['fehler'], f['korrektur'], f['auswirkung'], f['haeufigkeit']))
    return '\n'.join(out)


LIESMICH = '''ANSTOSS 3 - Inoffizieller Patch <<VERSION>>
=====================================

1. Überblick
------------
Dieser Patch behebt Programmfehler in ANSTOSS 3, Version 1.40. Die optischen Änderungen lassen den Spielverlauf
unverändert; die Berechnungskorrekturen und -änderungen greifen in ihn ein und können abgewählt werden (Abschnitt 4).
Der Patch ist ein Fanprojekt und steht in keiner Verbindung zu den Rechteinhabern des Spiels. Er enthält keine
Dateien des Spiels: Das Installationsprogramm ändert ausschließlich einzelne Stellen vorhandener Dateien
(anstoss3.exe, deb\\MeineDialoge.rch, texte\\Ereignis.saq und wahlweise ddraw.dll) und prüft jede Stelle vor der
Änderung. Die Verwendung
erfolgt auf eigene Verantwortung; eine Gewähr wird nicht übernommen.

Die behobenen Fehler sind im Installationsprogramm aufgelistet; die Schaltfläche "Details ..." zeigt zu jedem
Eintrag den Fehler, die Korrektur und die Auswirkung, bei Meldungen und Ereignissen außerdem die geschätzte
Häufigkeit. Dieselben Angaben enthält die Datei CHANGELOG.txt.

2. Voraussetzungen
------------------
- ANSTOSS 3 in Version 1.40. Entwickelt und geprüft wurde der Patch mit der Ausgabe von GOG.
- Windows mit Windows PowerShell 5.1 (Bestandteil von Windows 10 und Windows 11).
- Eine vorhandene Installation von Patch 1.41 bis 1.45 wird auf Version <<VERSION>> aktualisiert.
Erkennt das Installationsprogramm eine abweichende Fassung der anstoss3.exe, wird keine Datei verändert. Das gilt
auch für Installationen, deren Programmdatei durch andere Modifikationen verändert wurde; die Verträglichkeit mit
anderen Modifikationen wurde nicht geprüft. Liegt die Textdatei deb\\MeineDialoge.rch in einer abweichenden Fassung
vor, bleibt nur diese Datei unverändert; die Spaltenüberschrift der Liga-Statistik "Tagesform" lautet dann weiterhin
"Form". Dasselbe gilt für die Textdatei texte\\Ereignis.saq: Weicht einer der 20 betroffenen Texte vom ursprünglichen
Wortlaut ab, bleibt die Datei unverändert und die Meldungen behalten ihren bisherigen Text.

3. Installation
---------------
1. Beenden Sie ANSTOSS 3.
2. Entpacken Sie das Archiv vollständig und starten Sie die Datei "Anstoss3-Patch-<<VERSION>>.cmd" per Doppelklick.
   Die Dateien mit den Endungen .cmd und .ps1 müssen im selben Ordner liegen.
3. Der Installationsordner des Spiels wird automatisch ermittelt und vorausgewählt. Über "Durchsuchen ..." kann
   ein anderer Ordner gewählt werden; maßgeblich ist der Ordner, in dem die Datei anstoss3.exe liegt.
4. Prüfen Sie die beiden Optionen (Abschnitte 4 und 5) und wählen Sie "Installieren".
Befindet sich das Spiel in einem geschützten Ordner (zum Beispiel unter "C:\\Programme"), starten Sie die .cmd-Datei
über das Kontextmenü mit der Option "Als Administrator ausführen". Meldet Windows eine unbekannte Datei, kann die
Ausführung über "Weitere Informationen" und "Trotzdem ausführen" zugelassen werden.

4. Option "Berechnungskorrekturen und -änderungen"
--------------------------------------------------
Die Korrekturen sind in zwei Gruppen geteilt.
- Optische Änderungen: Statistiken, Anzeigen und Texte. Sie werden immer installiert und ändern den Spielverlauf nicht.
- Berechnungskorrekturen und -änderungen: Sie greifen in den Spielverlauf ein. Sie betreffen Funktionen und
  Ereignisse, die im Spiel angelegt sind, wegen eines Programmfehlers aber nie, zu selten oder fehlerhaft gearbeitet
  haben; einige Ereignisse treten dadurch erstmals oder häufiger ein. Diese Gruppe kann abgewählt werden. Bis Version
  1.44 hieß sie "Korrekturen der Spiellogik".
Zur zweiten Gruppe gehören:
- Trainer, Co-Trainer und Torwarttrainer: Übernahme ehemaliger Spieler als Trainer und Torwarttrainer, deren
  Geburtsdatum sowie die jährliche Anhebung der Kompetenz bei niedrigem Landesdurchschnitt.
- Fans und Presse: Fan-Status "verhasst" sowie die Zeitungsmeldungen "... erneut ein Totalausfall" und
  "Goldkettchen und teure Autos".
- Jugendspieler (seit Version 1.46): Vertragslaufzeit von Jugendspielern, die aus der Jugend eines anderen Vereins
  geholt werden.
- Finanzen: Berechnung des Bankguthabens und des aktuellen Vereinsvermögens bei laufenden Geldanlagen.
- Meldungen und Ereignisse (seit Version 1.45): Wirkungen, die eine Meldung nennt, die aber nicht oder falsch
  eintraten (zum Beispiel Dauer einer Verletzung, Trennung, Führerscheinentzug), sowie Ereignisse, die wegen eines
  Fehlers nie oder fast nie ausgelost wurden. Zu jedem Eintrag nennt "Details ..." die geschätzte Häufigkeit.
  Die Schätzungen sind aus den Lostabellen des Programms berechnet und nicht im Spiel gemessen; sie gelten unter der
  jeweils genannten Voraussetzung. Die täglichen Ereignisse betreffen nur Vereine menschlicher Manager.
Die Option ist vorausgewählt. Die Auswahl kann jederzeit geändert werden: Starten Sie das Installationsprogramm
erneut, setzen oder entfernen Sie die Option und wählen Sie "Installieren". Ohne die Option werden die Korrekturen
dieser Gruppe auf den ursprünglichen Stand zurückgesetzt; das gilt auch für die Korrekturen zu Trainern aus den
Versionen 1.41 und 1.42. Wurde die Gruppe bei einer früheren Installation abgewählt, bleibt sie bei der
Aktualisierung abgewählt, solange Sie die Option nicht selbst setzen.

5. Option "Angepasste ddraw.dll"
--------------------------------
Die Komponente steht nur für die GOG-Ausgabe zur Verfügung. Sie behebt eine Eingabeverzögerung von 2 bis 3 Sekunden
nach Mausklicks, die mit aktuellen Grafikkarten auftreten kann (festgestellt mit einer Radeon RX 6800 XT). Auf
Systemen ohne dieses Verhalten bleibt die Anpassung ohne Wirkung. Geprüft wurde sie in der 2D-Oberfläche des Spiels.
Treten nach der Installation Darstellungsfehler auf, deaktivieren Sie die Option und wählen Sie erneut "Installieren";
die Datei ddraw.dll wird dann auf ihren ursprünglichen Stand zurückgesetzt.

6. Deinstallation
-----------------
Starten Sie das Installationsprogramm und wählen Sie "Deinstallieren". Alle Änderungen an den vier Dateien werden
zurückgenommen. Zusätzlich legt das Installationsprogramm vor der ersten Änderung einer Datei eine Sicherungskopie
im selben Ordner an (Endung ".vor-patch" beziehungsweise ".vor-1.41" bei einer Installation von Patch 1.41).

7. Liga-Statistik "Tagesform"
-----------------------------
Die Statistik zeigt je Mannschaft die Durchschnittsnote im letzten Spiel mit einer Nachkommastelle (Spalte "Note").
- Ein niedrigerer Wert ist besser; die Mannschaft mit der besten Durchschnittsnote steht auf Platz 1.
- Berücksichtigt werden nur Spieler, die in diesem Spiel eine Note erhalten haben. Spieler ohne Note, zum Beispiel
  nach einer späten Einwechslung, gehen nicht in den Durchschnitt ein.
- Die Statistik wird nach jedem Spieltag neu berechnet. Der Name der Seite ("Tagesform") ist unverändert.

8. Bilanz: Bankguthaben und Geldanlagen (Gruppe "Berechnung")
-------------------------------------------------------------
Ohne die Korrektur zieht das Spiel vom Bankguthaben den aktuellen Wert der Geldanlagen ab, obwohl im Vereinsvermögen
nur die eingezahlten Beträge stehen. Mit jedem Wertzuwachs einer Anlage sinkt dadurch das angezeigte Bankguthaben;
beim Auflösen steigt es um die Auszahlung und zusätzlich um den gesamten Zuwachs.
- Mit der Korrektur steht der bisher abgezogene Zuwachs sofort im Bankguthaben. Beim Auflösen einer Anlage steigt
  das Bankguthaben nur noch um die Auszahlung.
- "Aktuelles Vereinsvermögen" ist das Bankguthaben zuzüglich des aktuellen Werts der Anlagen, abzüglich der Kredite.
- Es entsteht und verschwindet kein Geld; gespeicherte Werte, Einnahmen, Ausgaben und Steuern bleiben unverändert.
- Die Zeile "Vereinsvermögen am Anfang der Saison" ist unverändert und enthält den Zuwachs der Anlagen nicht.

9. Hinweise zu Spielständen
---------------------------
- Vorhandene Spielstände bleiben verwendbar. Die Korrekturen wirken ab dem jeweils nächsten Ereignis, überwiegend
  ab dem nächsten Saisonwechsel. Wann eine Korrektur im Einzelnen wirkt, steht unter "Details ..." beziehungsweise
  in der Datei CHANGELOG.txt beim jeweiligen Eintrag.
- Bereits fehlerhaft gespeicherte Statistikwerte werden nicht nachträglich berichtigt.
- Die installierte Fassung ist an der Versionsangabe des Spiels (<<VERSION>>) erkennbar.
'''


def main():
    exe_ids = [pid for e in EINTRAEGE for pid in e['ids'] if pid not in RCH_IDS and e.get('ziel') not in ('ddraw', 'saq')]
    assert sorted(exe_ids) == sorted(set(a3patch.TARGETS[EXE_SHA]) - KANDIDATEN), 'EINTRAEGE und a3patch.py passen nicht zusammen'
    assert sorted(RCH_IDS) == sorted(a3patch.TARGETS[RCH_SHA]) and sorted(DDRAW_IDS) == sorted(a3patch.TARGETS[DDRAW_SHA])
    exe = sites(EXE_SHA, exe_ids)
    rch = sites(RCH_SHA, RCH_IDS)
    dd = sites(DDRAW_SHA, DDRAW_IDS, lambda pid: 'B')
    assert {g for _, g, *_ in rch} == {'B'}
    exe_voll = patched('anstoss3.exe', EXE_SHA, exe)
    exe_ohne = patched('anstoss3.exe', EXE_SHA, exe, 'B')
    rch_neu = patched(os.path.join('deb', 'MeineDialoge.rch'), RCH_SHA, rch)
    dd_neu = patched('ddraw.dll', DDRAW_SHA, dd)
    saq_alt, saq_neu, saq_texte = saq_build()
    ps = (TEMPLATE
          .replace('<<VERSION>>', VERSION)
          .replace('<<EXE_ORIGINAL>>', EXE_SHA).replace('<<EXE_FERTIG>>', sha256(exe_voll))
          .replace('<<EXE_OHNE>>', sha256(exe_ohne)).replace('<<EXE_STELLEN>>', ps_sites(exe))
          .replace('<<RCH_ORIGINAL>>', RCH_SHA).replace('<<RCH_FERTIG>>', sha256(rch_neu))
          .replace('<<RCH_STELLEN>>', ps_sites(rch))
          .replace('<<DD_ORIGINAL>>', DDRAW_SHA).replace('<<DD_FERTIG>>', sha256(dd_neu))
          .replace('<<DD_STELLEN>>', ps_sites(dd))
          .replace('<<SAQ_ORIGINAL>>', sha256(saq_alt)).replace('<<SAQ_FERTIG>>', sha256(saq_neu))
          .replace('<<SAQ_TEXTE>>', ps_texte(saq_texte))
          .replace('<<LOGIK_TEXT>>', ps_text(LOGIK_TEXT))
          .replace('<<EINTRAEGE>>', window_entries()))
    assert '<<' not in ps
    for bad in '„“‚‘’':                     # would end or start a string in Windows PowerShell
        assert bad not in ps, bad
    os.makedirs(OUT, exist_ok=True)
    name = f'Anstoss3-Patch-{VERSION}'
    with open(os.path.join(OUT, name + '.ps1'), 'w', encoding='utf-8-sig', newline='\r\n') as f:
        f.write(ps)                         # BOM: Windows PowerShell 5.1 reads umlauts correctly only with it
    with open(os.path.join(OUT, name + '.cmd'), 'w', encoding='ascii', newline='\r\n') as f:
        f.write('@echo off\n'
                f'rem ANSTOSS 3 - Inoffizieller Patch {VERSION}: startet das Installationsprogramm\n'
                f'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0{name}.ps1" %*\n'
                'if errorlevel 1 pause\n')
    with open(os.path.join(OUT, 'LIESMICH.txt'), 'w', encoding='utf-8-sig', newline='\r\n') as f:
        f.write(LIESMICH.replace('<<VERSION>>', VERSION))
    with open(os.path.join(OUT, 'CHANGELOG.txt'), 'w', encoding='utf-8-sig', newline='\r\n') as f:
        f.write(changelog())
    files = [name + '.cmd', name + '.ps1', 'LIESMICH.txt', 'CHANGELOG.txt']
    with zipfile.ZipFile(os.path.join(OUT, name + '.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
        for fn in files:
            z.write(os.path.join(OUT, fn), fn)
    # reference files for tools/patch_test.ps1 (build/ is not part of the repository)
    os.makedirs(REF, exist_ok=True)
    for fn, data in (('anstoss3.exe', exe_voll), ('anstoss3-ohne-spiellogik.exe', exe_ohne),
                     ('MeineDialoge.rch', rch_neu), ('ddraw.dll', dd_neu), ('Ereignis.saq', saq_neu)):
        with open(os.path.join(REF, fn), 'wb') as f:
            f.write(data)
    n_l = len({pid for pid, g, *_ in exe if g == 'L'})
    print(f'Patch {VERSION}: {len(exe)} Stellen in anstoss3.exe ({len(exe_ids)} Korrekturen, davon {n_l} Berechnung), '
          f'{len(rch)} in deb\\MeineDialoge.rch, {len(dd)} in ddraw.dll -> {OUT}')
    print(f'  anstoss3.exe mit Spiellogik {sha256(exe_voll)[:8]}, ohne {sha256(exe_ohne)[:8]}; '
          f'MeineDialoge.rch {sha256(rch_neu)[:8]}; ddraw.dll {sha256(dd_neu)[:8]}; '
          f'Ereignis.saq {sha256(saq_neu)[:8]} ({len(saq_texte)} Texte, {len(EINTRAEGE)} Einträge)')


TEMPLATE = r'''# ANSTOSS 3 - Inoffizieller Patch <<VERSION>>
# Erzeugt von tools/patch_bauen.py - nicht von Hand ändern.
# Enthält keine Spieldateien: Es werden nur einzelne Stellen der vorhandenen Dateien geändert (mit Prüfung des alten Inhalts).
#   Fenster:       Anstoss3-Patch-<<VERSION>>.cmd starten
#   ohne Fenster:  -Still -Ordner "<Installationsordner>" [-OhneSpiellogik] [-Ddraw] [-Entfernen]
#   Prüfhilfe:     -Probe "<bild.png>" baut das Fenster unsichtbar, meldet den erkannten Zustand und ändert nichts;
#                  mit -ProbeEintrag <Nr> wird stattdessen der Details-Dialog dieses Eintrags (ab 0) als Bild gespeichert
param([string]$Ordner = '', [switch]$Still, [switch]$Ddraw, [switch]$OhneSpiellogik, [switch]$Entfernen, [string]$Probe = '', [int]$ProbeEintrag = -1)
$ErrorActionPreference = 'Stop'
$Version = '<<VERSION>>'
$GogId = '1886141726'

# Gruppe einer Stelle: B = optische Änderungen (immer), L = Berechnungskorrekturen und -änderungen (abwählbar).
# Alt: zulässige bisherige Inhalte einer Stelle; der erste ist der Originalzustand (Version 1.40), AltName nennt die Fassungen.
# Summen: Prüfsumme der Datei je Sollzustand der Gruppen (in der Reihenfolge von Gruppen).
$Exe = @{
    Datei = 'anstoss3.exe'; Sicherungen = @('anstoss3.exe.vor-patch', 'anstoss3.exe.vor-1.41')
    Gruppen = @('B', 'L')
    Summen = @{
        'original/original' = '<<EXE_ORIGINAL>>'
        'neu/original' = '<<EXE_OHNE>>'
        'neu/neu' = '<<EXE_FERTIG>>'
    }
    Stellen = @(
<<EXE_STELLEN>>
    )
}
$Rch = @{
    Datei = 'deb\MeineDialoge.rch'; Sicherungen = @('deb\MeineDialoge.rch.vor-patch')
    Gruppen = @('B')
    Summen = @{
        'original' = '<<RCH_ORIGINAL>>'
        'neu' = '<<RCH_FERTIG>>'
    }
    Stellen = @(
<<RCH_STELLEN>>
    )
}
$Dd = @{
    Datei = 'ddraw.dll'; Sicherungen = @('ddraw.dll.vor-patch', 'ddraw.dll.vor-1.41')
    Gruppen = @('B')
    Summen = @{
        'original' = '<<DD_ORIGINAL>>'
        'neu' = '<<DD_FERTIG>>'
    }
    Stellen = @(
<<DD_STELLEN>>
    )
}
# Textdatei der Ereignisse: 20 Texte mit altem und neuem Wortlaut (Bytes in Windows-1252, hexadezimal).
# Das Spiel lädt die Datei nur mit unveränderter Länge; die neuen Texte sind zusammen genauso lang wie die alten.
$Saq = @{
    Datei = 'texte\Ereignis.saq'; Sicherungen = @('texte\Ereignis.saq.vor-patch')
    Summen = @{
        'original' = '<<SAQ_ORIGINAL>>'
        'neu' = '<<SAQ_FERTIG>>'
    }
    Texte = @(
<<SAQ_TEXTE>>
    )
}
# Behobene Fehler für die Liste und den Details-Dialog, in der Reihenfolge der Fehlerarten.
$Eintraege = @(
<<EINTRAEGE>>
)

function HexZuBytes([string]$h) {
    $b = New-Object byte[] ($h.Length / 2)
    for ($i = 0; $i -lt $b.Length; $i++) { $b[$i] = [Convert]::ToByte($h.Substring(2 * $i, 2), 16) }
    return ,$b
}
function Gleich([byte[]]$b, [int]$off, [byte[]]$x) {
    if ($off + $x.Length -gt $b.Length) { return $false }
    for ($i = 0; $i -lt $x.Length; $i++) { if ($b[$off + $i] -ne $x[$i]) { return $false } }
    return $true
}
function Pruefsumme([string]$pfad) { return (Get-FileHash -LiteralPath $pfad -Algorithm SHA256).Hash.ToUpper() }

# Inhalt einer Stelle: -1 = neu, 0 = original, 1.. = früherer Inhalt (Index in Alt), -2 = fremd
function StandNr([byte[]]$b, $s) {
    if (Gleich $b $s.Offset (HexZuBytes $s.Neu)) { return -1 }
    for ($i = 0; $i -lt $s.Alt.Count; $i++) { if (Gleich $b $s.Offset (HexZuBytes $s.Alt[$i])) { return $i } }
    return -2
}
function Einordnen($z) {
    if ($z.Original -eq $z.Gesamt) { return 'original' }
    if ($z.Neu -eq $z.Gesamt) { return 'fertig' }
    return 'teilweise'
}

# Zustand einer Datei und ihrer Gruppen: fehlt | original | fertig | teilweise | fremd
# Vorversion: Fassung des Patches, die an einem früheren Inhalt erkannt wurde (zum Beispiel 1.42).
function Zustand([string]$ordner, $def) {
    $r = @{ Status = 'fehlt'; Original = 0; Neu = 0; Frueher = 0; Gesamt = 0; Vorversion = ''; Gruppe = @{} }
    foreach ($g in $def.Gruppen) { $r.Gruppe[$g] = @{ Status = 'fehlt'; Original = 0; Neu = 0; Frueher = 0; Gesamt = 0 } }
    if (-not $ordner) { return $r }
    $pfad = Join-Path $ordner $def.Datei
    if (-not (Test-Path -LiteralPath $pfad -PathType Leaf)) { return $r }
    $b = [IO.File]::ReadAllBytes($pfad)
    $fremd = 0
    foreach ($s in $def.Stellen) {
        $g = $r.Gruppe[$s.Gruppe]
        $g.Gesamt++; $r.Gesamt++
        $nr = StandNr $b $s
        if ($nr -eq -1) { $g.Neu++; $r.Neu++ }
        elseif ($nr -eq 0) { $g.Original++; $r.Original++ }
        elseif ($nr -gt 0) { $g.Frueher++; $r.Frueher++; if ($s.AltName) { $r.Vorversion = $s.AltName[$nr] } }
        else { $fremd++ }
    }
    if ($fremd -gt 0) {
        $r.Status = 'fremd'
        foreach ($g in $def.Gruppen) { $r.Gruppe[$g].Status = 'fremd' }
        return $r
    }
    $r.Status = Einordnen $r
    foreach ($g in $def.Gruppen) { $r.Gruppe[$g].Status = Einordnen $r.Gruppe[$g] }
    return $r
}

# Setzt die Stellen jeder Gruppe auf den Sollzustand ($soll: Gruppe -> 'neu' oder 'original').
# Gibt eine Meldung zurück, wirft bei Fehlern. $sichern: vor der ersten Änderung eine Sicherungskopie anlegen.
function Anwenden([string]$ordner, $def, $soll, [bool]$sichern) {
    $pfad = Join-Path $ordner $def.Datei
    $b = [IO.File]::ReadAllBytes($pfad)
    $hin = 0; $weg = 0
    foreach ($s in $def.Stellen) {
        $nr = StandNr $b $s
        if ($nr -eq -2) { throw "$($def.Datei): Unerwarteter Inhalt an Position 0x$('{0:X}' -f $s.Offset) ($($s.Name)). Die Datei wurde nicht verändert." }
        if ($soll[$s.Gruppe] -eq 'neu') {
            if ($nr -eq -1) { continue }
            $nach = HexZuBytes $s.Neu; $hin++
        } else {
            if ($nr -eq 0) { continue }
            $nach = HexZuBytes $s.Alt[0]; $weg++
        }
        [Array]::Copy($nach, 0, $b, $s.Offset, $nach.Length)
    }
    if (($hin + $weg) -eq 0) { return "$($def.Datei): Keine Änderung erforderlich." }
    $vorhanden = $false
    foreach ($name in $def.Sicherungen) { if (Test-Path -LiteralPath (Join-Path $ordner $name)) { $vorhanden = $true } }
    if ($sichern -and -not $vorhanden) { Copy-Item -LiteralPath $pfad -Destination (Join-Path $ordner $def.Sicherungen[0]) }
    $attr = [IO.File]::GetAttributes($pfad)                      # schreibgeschützte Datei: Schutz für das Schreiben aufheben
    $schutz = [bool]($attr -band [IO.FileAttributes]::ReadOnly)
    if ($schutz) { [IO.File]::SetAttributes($pfad, ($attr -band (-bnot [IO.FileAttributes]::ReadOnly))) }
    try { [IO.File]::WriteAllBytes($pfad, $b) } finally { if ($schutz) { [IO.File]::SetAttributes($pfad, $attr) } }
    $teile = @()
    if ($hin -gt 0) { $teile += "$hin Änderungen übernommen" }
    if ($weg -gt 0) { $teile += "$weg Änderungen zurückgenommen" }
    $was = $teile -join ', '
    $schluessel = @(foreach ($g in $def.Gruppen) { $soll[$g] }) -join '/'
    if ((Pruefsumme $pfad) -eq $def.Summen[$schluessel]) { return "$($def.Datei): $was, Prüfsumme bestätigt." }
    return "$($def.Datei): $was. Die Prüfsumme der Datei weicht vom Referenzwert ab (abweichende Ausgabe); die geänderten Stellen wurden einzeln geprüft."
}

# ---------- Textdatei texte\Ereignis.saq ----------
# Aufbau: 4 Bytes Länge, 4 Bytes Anzahl, dann die Texte (durch 0 getrennt); jedes Byte ist mit dem vorigen gespeicherten
# Byte verknüpft (XOR), das erste mit dem unteren Byte der Länge.
function SaqLesen([string]$pfad) {
    $d = [IO.File]::ReadAllBytes($pfad)
    if ($d.Length -lt 8) { return $null }
    $n = [BitConverter]::ToInt32($d, 0)
    if ($n -le 0 -or (8 + $n) -gt $d.Length) { return $null }
    $p = New-Object byte[] $n
    $key = $n -band 0xFF
    for ($i = 0; $i -lt $n; $i++) { $c = $d[8 + $i]; $p[$i] = $c -bxor $key; $key = $c }
    $anf = New-Object 'System.Collections.Generic.List[int]'
    $anf.Add(0)
    for ($i = 0; $i -lt $n; $i++) { if ($p[$i] -eq 0) { $anf.Add($i + 1) } }
    return @{ Roh = $d; Klar = $p; Anfang = $anf; Laenge = $n }
}
# Stand eines Textes: -1 = neu, 0 = original, -2 = fremd
function SaqStandNr($s, $t) {
    if ($t.Nr -ge $s.Anfang.Count) { return -2 }
    $a = $s.Anfang[$t.Nr - 1]; $l = $s.Anfang[$t.Nr] - 1 - $a
    foreach ($paar in @(@(-1, $t.Neu), @(0, $t.Alt))) {
        $x = HexZuBytes $paar[1]
        if ($x.Length -eq $l -and (Gleich $s.Klar $a $x)) { return $paar[0] }
    }
    return -2
}
function SaqZustand([string]$ordner) {
    $r = @{ Status = 'fehlt'; Original = 0; Neu = 0; Gesamt = $Saq.Texte.Count }
    if (-not $ordner) { return $r }
    $pfad = Join-Path $ordner $Saq.Datei
    if (-not (Test-Path -LiteralPath $pfad -PathType Leaf)) { return $r }
    $summe = Pruefsumme $pfad
    if ($summe -eq $Saq.Summen['original']) { $r.Status = 'original'; $r.Original = $r.Gesamt; return $r }
    if ($summe -eq $Saq.Summen['neu']) { $r.Status = 'fertig'; $r.Neu = $r.Gesamt; return $r }
    $s = SaqLesen $pfad
    if ($null -eq $s) { $r.Status = 'fremd'; return $r }
    foreach ($t in $Saq.Texte) {
        $nr = SaqStandNr $s $t
        if ($nr -eq -1) { $r.Neu++ } elseif ($nr -eq 0) { $r.Original++ } else { $r.Status = 'fremd'; return $r }
    }
    $r.Status = Einordnen $r
    return $r
}
# Setzt alle 20 Texte auf den Sollzustand ('neu' oder 'original'). Gibt eine Meldung zurück, wirft bei Fehlern.
function SaqAnwenden([string]$ordner, [string]$soll, [bool]$sichern) {
    $pfad = Join-Path $ordner $Saq.Datei
    $s = SaqLesen $pfad
    if ($null -eq $s) { throw "$($Saq.Datei): Unerwarteter Aufbau. Die Datei wurde nicht verändert." }
    $aus = New-Object System.IO.MemoryStream
    $pos = 0; $n = 0
    foreach ($t in ($Saq.Texte | Sort-Object { $_.Nr })) {
        $nr = SaqStandNr $s $t
        if ($nr -eq -2) { throw "$($Saq.Datei): Text $($t.Nr) hat einen unerwarteten Wortlaut. Die Datei wurde nicht verändert." }
        $a = $s.Anfang[$t.Nr - 1]; $e = $s.Anfang[$t.Nr] - 1
        $aus.Write($s.Klar, $pos, $a - $pos)
        if ($soll -eq 'neu') { $x = HexZuBytes $t.Neu; if ($nr -ne -1) { $n++ } } else { $x = HexZuBytes $t.Alt; if ($nr -ne 0) { $n++ } }
        $aus.Write($x, 0, $x.Length)
        $pos = $e
    }
    $aus.Write($s.Klar, $pos, $s.Laenge - $pos)
    if ($n -eq 0) { return "$($Saq.Datei): Keine Änderung erforderlich." }
    $p = $aus.ToArray()
    if ($p.Length -ne $s.Laenge) { throw "$($Saq.Datei): Die Länge der Texte würde sich ändern. Die Datei wurde nicht verändert." }
    $b = New-Object byte[] $s.Roh.Length
    [Array]::Copy($s.Roh, 0, $b, 0, $s.Roh.Length)
    $key = $s.Laenge -band 0xFF
    for ($i = 0; $i -lt $p.Length; $i++) { $key = $p[$i] -bxor $key; $b[8 + $i] = $key }
    $vorhanden = $false
    foreach ($name in $Saq.Sicherungen) { if (Test-Path -LiteralPath (Join-Path $ordner $name)) { $vorhanden = $true } }
    if ($sichern -and -not $vorhanden) { Copy-Item -LiteralPath $pfad -Destination (Join-Path $ordner $Saq.Sicherungen[0]) }
    $attr = [IO.File]::GetAttributes($pfad)
    $schutz = [bool]($attr -band [IO.FileAttributes]::ReadOnly)
    if ($schutz) { [IO.File]::SetAttributes($pfad, ($attr -band (-bnot [IO.FileAttributes]::ReadOnly))) }
    try { [IO.File]::WriteAllBytes($pfad, $b) } finally { if ($schutz) { [IO.File]::SetAttributes($pfad, $attr) } }
    if ($soll -eq 'neu') { $was = "$n Texte berichtigt" } else { $was = "$n Texte zurückgesetzt" }
    if ((Pruefsumme $pfad) -eq $Saq.Summen[$soll]) { return "$($Saq.Datei): $was, Prüfsumme bestätigt." }
    return "$($Saq.Datei): $was. Die Prüfsumme der Datei weicht vom Referenzwert ab (abweichende Ausgabe); die Texte wurden einzeln geprüft."
}
function SaqText($z) {
    switch ($z.Status) {
        'fehlt'     { 'texte\Ereignis.saq: Nicht vorhanden. Die Meldungstexte bleiben unverändert.' }
        'original'  { 'texte\Ereignis.saq: Originalfassung.' }
        'fertig'    { 'texte\Ereignis.saq: Die 20 berichtigten Meldungstexte sind installiert.' }
        'teilweise' { 'texte\Ereignis.saq: Die berichtigten Meldungstexte sind unvollständig installiert.' }
        default     { 'texte\Ereignis.saq: Abweichende Fassung, wird nicht verändert. Die Meldungstexte bleiben unverändert.' }
    }
}

$KeinZugriff = "Auf den Installationsordner kann nicht schreibend zugegriffen werden. Bitte starten Sie die Datei Anstoss3-Patch-$Version.cmd über das Kontextmenü mit der Option »Als Administrator ausführen«."
function FehlerText($fehler) {
    $e = $fehler.Exception
    while ($e.InnerException) { $e = $e.InnerException }
    if ($e -is [System.UnauthorizedAccessException]) { return $KeinZugriff }
    return "Fehler: $($e.Message)"
}

function SpielLaeuft { return [bool](Get-Process -Name 'anstoss3' -ErrorAction SilentlyContinue) }

function SpielSuchen {
    $k = New-Object System.Collections.ArrayList
    foreach ($key in "HKLM:\SOFTWARE\WOW6432Node\GOG.com\Games\$GogId", "HKLM:\SOFTWARE\GOG.com\Games\$GogId") {
        try { $p = (Get-ItemProperty -LiteralPath $key -ErrorAction Stop).path; if ($p) { [void]$k.Add($p) } } catch {}
    }
    foreach ($root in 'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall', 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall', 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall') {
        try {
            foreach ($e in Get-ChildItem -LiteralPath $root -ErrorAction Stop) {
                $v = Get-ItemProperty -LiteralPath $e.PSPath -ErrorAction SilentlyContinue
                if ($v -and $v.DisplayName -match 'ANSTOSS 3' -and $v.InstallLocation) { [void]$k.Add($v.InstallLocation) }
            }
        } catch {}
    }
    if ($PSScriptRoot) { [void]$k.Add($PSScriptRoot); [void]$k.Add((Split-Path -Parent $PSScriptRoot)) }
    $unter = 'GOG Games\ANSTOSS 3', 'GOG Galaxy\Games\ANSTOSS 3', 'Program Files (x86)\GOG Galaxy\Games\ANSTOSS 3', 'Program Files (x86)\GOG.com\ANSTOSS 3',
             'Games\ANSTOSS 3', 'Spiele\ANSTOSS 3', 'Program Files (x86)\Ascaron\Anstoss 3', 'Ascaron\Anstoss 3', 'Anstoss 3'
    foreach ($d in [IO.DriveInfo]::GetDrives()) {
        if ($d.DriveType -ne 'Fixed' -or -not $d.IsReady) { continue }
        foreach ($u in $unter) { [void]$k.Add((Join-Path $d.Name $u)) }
    }
    foreach ($p in $k) {
        $p = "$p".Trim().TrimEnd('\')
        if ($p -and (Test-Path -LiteralPath (Join-Path $p 'anstoss3.exe') -PathType Leaf)) { return $p }
    }
    return ''
}

function ExeText($z) {
    if ($z.Status -eq 'fehlt') { return 'anstoss3.exe: Die Datei wurde im angegebenen Ordner nicht gefunden.' }
    if ($z.Status -eq 'fremd') { return 'anstoss3.exe: Unbekannte Dateifassung. Der Patch setzt Version 1.40 voraus; die Datei wird nicht verändert.' }
    if ($z.Status -eq 'original') { return 'anstoss3.exe: Version 1.40, Patch nicht installiert.' }
    $l = $z.Gruppe['L']
    if ($z.Gruppe['B'].Status -eq 'fertig') {
        if ($l.Status -eq 'fertig') { return "anstoss3.exe: Patch $Version ist installiert, einschließlich der Berechnungskorrekturen und -änderungen." }
        if ($l.Status -eq 'original') { return "anstoss3.exe: Patch $Version ist installiert, ohne die Berechnungskorrekturen und -änderungen." }
        return "anstoss3.exe: Patch $Version ist installiert; die Berechnungskorrekturen und -änderungen sind unvollständig ($($l.Neu) von $($l.Gesamt) Änderungen)."
    }
    if ($z.Vorversion) { return "anstoss3.exe: Patch $($z.Vorversion) ist installiert ($($z.Neu) von $($z.Gesamt) Änderungen der Version $Version). Mit »Installieren« wird auf Version $Version aktualisiert." }
    return "anstoss3.exe: Der Patch ist unvollständig installiert ($($z.Neu) von $($z.Gesamt) Änderungen). Mit »Installieren« wird Version $Version vollständig installiert."
}
function RchText($z) {
    switch ($z.Status) {
        'fehlt'     { 'deb\MeineDialoge.rch: Nicht vorhanden. Die Spaltenüberschrift der Tagesform bleibt »Form«.' }
        'original'  { 'deb\MeineDialoge.rch: Originalfassung.' }
        'fertig'    { 'deb\MeineDialoge.rch: Die Anpassung ist installiert.' }
        'teilweise' { 'deb\MeineDialoge.rch: Die Anpassung ist unvollständig installiert.' }
        default     { 'deb\MeineDialoge.rch: Unbekannte Fassung, wird nicht verändert. Die Spaltenüberschrift der Tagesform bleibt »Form«.' }
    }
}
function DdText($z) {
    switch ($z.Status) {
        'fehlt'     { 'ddraw.dll: Nicht vorhanden. Die Komponente steht nur für die GOG-Ausgabe zur Verfügung.' }
        'original'  { 'ddraw.dll: Originalfassung der GOG-Ausgabe.' }
        'fertig'    { 'ddraw.dll: Die Anpassung ist installiert.' }
        'teilweise' { 'ddraw.dll: Die Anpassung ist unvollständig installiert.' }
        default     { 'ddraw.dll: Unbekannte Dateifassung; die Datei wird nicht verändert.' }
    }
}
function Geaendert($z) { return ($z.Status -eq 'fertig' -or $z.Status -eq 'teilweise') }
# Spiellogik bei einer früheren Installation abgewählt: Patch vorhanden, Gruppe vollständig im Originalzustand
function LogikAbgewaehlt($z) {
    if ($z.Status -ne 'teilweise' -and $z.Status -ne 'fertig') { return $false }
    $b = $z.Gruppe['B']
    return (($b.Neu + $b.Frueher) -gt 0 -and $z.Gruppe['L'].Status -eq 'original')
}

# Führt Installation oder Deinstallation aus und gibt die Meldungen zurück.
function Ausfuehren([string]$ordner, [bool]$mitDdraw, [bool]$mitLogik, [bool]$entfernen) {
    $m = New-Object System.Collections.ArrayList
    if (SpielLaeuft) { throw 'ANSTOSS 3 wird derzeit ausgeführt. Bitte beenden Sie das Spiel und wiederholen Sie den Vorgang.' }
    $ze = Zustand $ordner $Exe; $zr = Zustand $ordner $Rch; $zd = Zustand $ordner $Dd; $zs = SaqZustand $ordner
    if ($ze.Status -eq 'fehlt') { throw 'Im angegebenen Ordner wurde keine anstoss3.exe gefunden.' }
    if ($ze.Status -eq 'fremd') { throw 'Die Datei anstoss3.exe entspricht nicht Version 1.40 oder wurde anderweitig verändert. Es wurden keine Änderungen vorgenommen.' }
    $an = @{ B = 'neu'; L = 'neu' }; $aus = @{ B = 'original'; L = 'original' }
    if ($entfernen) {
        [void]$m.Add((Anwenden $ordner $Exe $aus $false))
        if (Geaendert $zr) { [void]$m.Add((Anwenden $ordner $Rch $aus $false)) }
        if (Geaendert $zd) { [void]$m.Add((Anwenden $ordner $Dd $aus $false)) }
        if (Geaendert $zs) { [void]$m.Add((SaqAnwenden $ordner 'original' $false)) }
        [void]$m.Add('Die Deinstallation ist abgeschlossen.')
    } else {
        $sollExe = @{ B = 'neu'; L = 'neu' }
        if (-not $mitLogik) { $sollExe.L = 'original' }
        [void]$m.Add((Anwenden $ordner $Exe $sollExe $true))
        if ($zr.Status -eq 'fehlt' -or $zr.Status -eq 'fremd') { [void]$m.Add((RchText $zr)) }
        else { [void]$m.Add((Anwenden $ordner $Rch $an $true)) }
        if ($zs.Status -eq 'fehlt' -or $zs.Status -eq 'fremd') { [void]$m.Add((SaqText $zs)) }
        else { [void]$m.Add((SaqAnwenden $ordner 'neu' $true)) }
        if ($zd.Status -eq 'fehlt' -or $zd.Status -eq 'fremd') {
            if ($mitDdraw) { [void]$m.Add((DdText $zd)) }
        } elseif ($mitDdraw) {
            [void]$m.Add((Anwenden $ordner $Dd $an $true))
        } elseif ($zd.Status -ne 'original') {
            [void]$m.Add((Anwenden $ordner $Dd $aus $false))
        }
        if ($mitLogik) { [void]$m.Add("Die Installation von Patch $Version ist abgeschlossen (einschließlich der Berechnungskorrekturen und -änderungen).") }
        else { [void]$m.Add("Die Installation von Patch $Version ist abgeschlossen (ohne die Berechnungskorrekturen und -änderungen).") }
    }
    return $m
}

# ---------- ohne Fenster ----------
if ($Still) {
    try {
        if (-not $Ordner) { $Ordner = SpielSuchen }
        if (-not $Ordner) { throw 'Der Installationsordner wurde nicht gefunden. Bitte geben Sie ihn mit -Ordner an.' }
        "Installationsordner: $Ordner"
        Ausfuehren $Ordner ([bool]$Ddraw) (-not [bool]$OhneSpiellogik) ([bool]$Entfernen)
        exit 0
    } catch {
        FehlerText $_
        exit 1
    }
}

# ---------- Fenster ----------
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()

$Schrift = New-Object System.Drawing.Font('Segoe UI', 9)
$Fett = New-Object System.Drawing.Font('Segoe UI', 9, [System.Drawing.FontStyle]::Bold)
$Gross = New-Object System.Drawing.Font('Segoe UI', 12, [System.Drawing.FontStyle]::Bold)

$f = New-Object System.Windows.Forms.Form
$f.Text = "ANSTOSS 3 - Inoffizieller Patch $Version"
$f.ClientSize = New-Object System.Drawing.Size(1040, 860)
$f.StartPosition = 'CenterScreen'
$f.FormBorderStyle = 'Sizable'
$f.MinimumSize = New-Object System.Drawing.Size(860, 640)
$f.Font = $Schrift

# $anker: Seiten, an denen das Element beim Vergrößern des Fensters hängt
function Neu($typ, $x, $y, $w, $h, $text, $anker = 'Top,Left') {
    $c = New-Object "System.Windows.Forms.$typ"
    $c.Location = New-Object System.Drawing.Point($x, $y)
    $c.Size = New-Object System.Drawing.Size($w, $h)
    if ($null -ne $text) { $c.Text = $text }
    $c.Anchor = [System.Windows.Forms.AnchorStyles]$anker
    $f.Controls.Add($c)
    return $c
}

$kopf = Neu 'Label' 16 12 1008 24 "ANSTOSS 3 - Inoffizieller Patch $Version" 'Top,Left,Right'
$kopf.Font = $Gross
[void](Neu 'Label' 16 40 1008 18 'Behebt Programmfehler der Version 1.40. Es werden ausschließlich einzelne Stellen und Texte vorhandener Dateien geändert; zuvor werden Sicherungskopien angelegt.' 'Top,Left,Right')

[void](Neu 'Label' 16 68 400 18 'Installationsordner:')
$tb = Neu 'TextBox' 16 88 880 24 '' 'Top,Left,Right'
$suche = Neu 'Button' 904 86 120 27 'Durchsuchen ...' 'Top,Right'
$lblExe = Neu 'Label' 16 120 1008 18 '' 'Top,Left,Right'
$lblRch = Neu 'Label' 16 140 1008 18 '' 'Top,Left,Right'
$lblDd = Neu 'Label' 16 160 1008 18 '' 'Top,Left,Right'
$lblSaq = Neu 'Label' 16 180 1008 18 '' 'Top,Left,Right'

$cbL = Neu 'CheckBox' 16 208 1008 22 'Berechnungskorrekturen und -änderungen installieren (abwählbar)' 'Top,Left,Right'
$cbL.Font = $Fett
[void](Neu 'Label' 34 230 990 52 '<<LOGIK_TEXT>>' 'Top,Left,Right')

$cb = Neu 'CheckBox' 16 288 1008 22 'Angepasste ddraw.dll installieren (optional, nur GOG-Ausgabe)' 'Top,Left,Right'
$cb.Font = $Fett
[void](Neu 'Label' 34 310 990 18 'Behebt eine Eingabeverzögerung von 2 bis 3 Sekunden nach Mausklicks, die mit aktuellen Grafikkarten auftreten kann.' 'Top,Left,Right')

$lblListe = Neu 'Label' 16 342 500 18 "Behobene Fehler ($($Eintraege.Count) Einträge)"
$lblListe.Font = $Fett
$lblHinweis = Neu 'Label' 424 342 600 18 'Eintrag auswählen und »Details ...« wählen oder doppelt anklicken.' 'Top,Right'
$lblHinweis.TextAlign = 'TopRight'
$lv = Neu 'ListView' 16 364 1008 360 $null 'Top,Bottom,Left,Right'
$lv.View = 'Details'; $lv.FullRowSelect = $true; $lv.MultiSelect = $false; $lv.HideSelection = $false
$lv.ShowGroups = $true; $lv.HeaderStyle = 'Nonclickable'; $lv.ShowItemToolTips = $true
[void]$lv.Columns.Add('Behobener Fehler', 700)
[void]$lv.Columns.Add('Art', 180)
[void]$lv.Columns.Add('Seit Version', 90)
$bereiche = @{}
for ($i = 0; $i -lt $Eintraege.Count; $i++) {
    $e = $Eintraege[$i]
    if (-not $bereiche.ContainsKey($e.Bereich)) {
        $g = New-Object System.Windows.Forms.ListViewGroup($e.Bereich)
        [void]$lv.Groups.Add($g)
        $bereiche[$e.Bereich] = $g
    }
    $it = New-Object System.Windows.Forms.ListViewItem($e.Titel)
    [void]$it.SubItems.Add($e.Art)
    [void]$it.SubItems.Add($e.Seit)
    $it.Tag = $i
    $it.Group = $bereiche[$e.Bereich]
    [void]$lv.Items.Add($it)
}
function SpaltenAnpassen { $lv.Columns[0].Width = [Math]::Max(300, $lv.ClientSize.Width - $lv.Columns[1].Width - $lv.Columns[2].Width - 4) }
$lv.Add_Resize({ SpaltenAnpassen })

$det = Neu 'Button' 16 732 150 30 'Details ...' 'Bottom,Left'
$det.Enabled = $false
$ok = Neu 'Button' 554 732 150 30 'Installieren' 'Bottom,Right'
$weg = Neu 'Button' 714 732 150 30 'Deinstallieren' 'Bottom,Right'
$zu = Neu 'Button' 874 732 150 30 'Schließen' 'Bottom,Right'
$log = Neu 'TextBox' 16 772 1008 72 '' 'Bottom,Left,Right'
$log.Multiline = $true; $log.ReadOnly = $true; $log.ScrollBars = 'Vertical'; $log.TabStop = $false

# Ein Textabsatz im Details-Dialog; gibt die nächste freie Höhe zurück.
function Absatz($flaeche, [int]$y, [string]$text, $schrift, [int]$breite, [int]$abstand, $farbe = $null) {
    $l = New-Object System.Windows.Forms.Label
    $l.UseMnemonic = $false; $l.AutoSize = $false; $l.Font = $schrift; $l.Text = $text
    if ($farbe) { $l.ForeColor = $farbe }
    $h = $l.GetPreferredSize((New-Object System.Drawing.Size($breite, 0))).Height
    $l.Location = New-Object System.Drawing.Point(20, $y)
    $l.Size = New-Object System.Drawing.Size($breite, $h)
    $flaeche.Controls.Add($l)
    return ($y + $h + $abstand)
}
# Details eines Eintrags: Fehler, Korrektur, Auswirkung. Mit $bild wird der Dialog nur als Bild gespeichert.
function DetailsZeigen([int]$nr, [string]$bild = '') {
    $e = $Eintraege[$nr]
    $d = New-Object System.Windows.Forms.Form
    $d.Text = "Details zum Eintrag $($nr + 1) von $($Eintraege.Count)"
    $d.ClientSize = New-Object System.Drawing.Size(820, 600)
    $d.StartPosition = 'CenterParent'; $d.FormBorderStyle = 'FixedDialog'
    $d.MaximizeBox = $false; $d.MinimizeBox = $false; $d.ShowInTaskbar = $false; $d.Font = $Schrift
    $fl = New-Object System.Windows.Forms.Panel
    $fl.Location = New-Object System.Drawing.Point(0, 0)
    $fl.Size = New-Object System.Drawing.Size(820, 548)
    $fl.AutoScroll = $true; $fl.BackColor = [System.Drawing.SystemColors]::Window
    $d.Controls.Add($fl)
    $breite = 820 - 40 - [System.Windows.Forms.SystemInformation]::VerticalScrollBarWidth
    $y = Absatz $fl 16 $e.Titel $Gross $breite 4
    $y = Absatz $fl $y "$($e.Bereich)  |  $($e.Art)  |  seit Version $($e.Seit)" $Schrift $breite 16 ([System.Drawing.SystemColors]::GrayText)
    foreach ($teil in @(@('Fehler', $e.Fehler), @('Korrektur', $e.Korrektur), @('Auswirkung', $e.Auswirkung), @('Geschätzte Häufigkeit', $e.Haeufigkeit))) {
        if (-not $teil[1]) { continue }
        $y = Absatz $fl $y $teil[0] $Fett $breite 2
        $y = Absatz $fl $y $teil[1] $Schrift $breite 16
    }
    $zuD = New-Object System.Windows.Forms.Button
    $zuD.Text = 'Schließen'; $zuD.Size = New-Object System.Drawing.Size(150, 30)
    $zuD.Location = New-Object System.Drawing.Point(654, 559)
    $zuD.DialogResult = 'Cancel'
    $d.Controls.Add($zuD); $d.AcceptButton = $zuD; $d.CancelButton = $zuD
    if ($bild) {
        $d.StartPosition = 'Manual'; $d.Location = New-Object System.Drawing.Point(-4000, -4000)
        $d.Show(); [System.Windows.Forms.Application]::DoEvents()
        $b = New-Object System.Drawing.Bitmap($d.Width, $d.Height)
        $d.DrawToBitmap($b, (New-Object System.Drawing.Rectangle(0, 0, $d.Width, $d.Height)))
        $b.Save($bild); $d.Close()
        return
    }
    [void]$d.ShowDialog($f)
    $d.Dispose()
}
function DetailsGewaehlt { if ($lv.SelectedItems.Count -gt 0) { DetailsZeigen ([int]$lv.SelectedItems[0].Tag) } }
$lv.Add_SelectedIndexChanged({ $det.Enabled = $lv.SelectedItems.Count -gt 0 })
$lv.Add_DoubleClick({ DetailsGewaehlt })
$lv.Add_KeyDown({ if ($_.KeyCode -eq 'Return') { DetailsGewaehlt; $_.Handled = $true } })
$det.Add_Click({ DetailsGewaehlt })

# gesetzt / gesetztL: Der Benutzer hat die Option selbst gewählt; sie wird dann nicht mehr vorbelegt.
$gesetzt = $false
$gesetztL = $false
function Auffrischen {
    $o = $tb.Text.Trim().TrimEnd('\')
    $ze = Zustand $o $Exe; $zr = Zustand $o $Rch; $zd = Zustand $o $Dd; $zs = SaqZustand $o
    $lblExe.Text = ExeText $ze
    $lblRch.Text = RchText $zr
    $lblDd.Text = DdText $zd
    $lblSaq.Text = SaqText $zs
    $geht = $ze.Status -eq 'original' -or $ze.Status -eq 'teilweise' -or $ze.Status -eq 'fertig'
    $ok.Enabled = $geht
    $weg.Enabled = $geht -and ($ze.Status -ne 'original' -or (Geaendert $zr) -or (Geaendert $zd) -or (Geaendert $zs))
    # Spiellogik: vorausgewählt, außer sie wurde bei einer früheren Installation abgewählt
    $cbL.Enabled = $geht
    if (-not $geht) { $cbL.Checked = $false }
    elseif (-not $script:gesetztL) { $cbL.Checked = -not (LogikAbgewaehlt $ze) }
    $ddGeht = $geht -and ($zd.Status -eq 'original' -or (Geaendert $zd))
    $cb.Enabled = $ddGeht
    if (-not $ddGeht) { $cb.Checked = $false } elseif (-not $script:gesetzt) { $cb.Checked = $true }
}
$tb.Add_TextChanged({ $script:gesetzt = $false; $script:gesetztL = $false; Auffrischen })
$cb.Add_Click({ $script:gesetzt = $true })
$cbL.Add_Click({ $script:gesetztL = $true })
$suche.Add_Click({
    $d = New-Object System.Windows.Forms.FolderBrowserDialog
    $d.Description = 'Bitte wählen Sie den Ordner, in dem die Datei anstoss3.exe liegt.'
    if ($tb.Text -and (Test-Path -LiteralPath $tb.Text)) { $d.SelectedPath = $tb.Text }
    if ($d.ShowDialog() -eq 'OK') { $tb.Text = $d.SelectedPath }
})
function Los([bool]$entfernen) {
    $o = $tb.Text.Trim().TrimEnd('\')
    try {
        $m = Ausfuehren $o $cb.Checked $cbL.Checked $entfernen
        $log.AppendText(($m -join "`r`n") + "`r`n")
    } catch {
        $log.AppendText((FehlerText $_) + "`r`n")
    }
    # nach einer Installation bleibt die Auswahl stehen; nach einer Deinstallation gilt wieder die Vorbelegung
    $script:gesetzt = -not $entfernen; $script:gesetztL = -not $entfernen
    Auffrischen
}
$ok.Add_Click({ Los $false })
$weg.Add_Click({ Los $true })
$zu.Add_Click({ $f.Close() })

# Fenster nie größer als der nutzbare Bildschirm; die Liste nimmt den übrigen Platz ein
$platz = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
if ($f.Width -gt $platz.Width) { $f.Width = $platz.Width }
if ($f.Height -gt $platz.Height) { $f.Height = $platz.Height }
SpaltenAnpassen

if ($Ordner) { $tb.Text = $Ordner } else { $tb.Text = SpielSuchen }
if (-not $tb.Text) { $log.AppendText("Der Installationsordner wurde nicht automatisch ermittelt. Bitte wählen Sie ihn über »Durchsuchen ...« aus.`r`n") }
Auffrischen
if ($Probe) {
    if ($ProbeEintrag -ge 0) {
        DetailsZeigen $ProbeEintrag $Probe
        "Details-Dialog für Eintrag $ProbeEintrag ($($Eintraege[$ProbeEintrag].Titel))"
        exit 0
    }
    $f.StartPosition = 'Manual'; $f.Location = New-Object System.Drawing.Point(-4000, -4000); $f.ShowInTaskbar = $false
    $f.Show(); [System.Windows.Forms.Application]::DoEvents()
    $bild = New-Object System.Drawing.Bitmap($f.Width, $f.Height)
    $f.DrawToBitmap($bild, (New-Object System.Drawing.Rectangle(0, 0, $f.Width, $f.Height)))
    $bild.Save($Probe)
    "Ordner: $($tb.Text)"; $lblExe.Text; $lblRch.Text; $lblDd.Text; $lblSaq.Text
    "Spiellogik-Option: gesetzt=$($cbL.Checked) wählbar=$($cbL.Enabled) | ddraw-Option: gesetzt=$($cb.Checked) wählbar=$($cb.Enabled) | Installieren=$($ok.Enabled) Deinstallieren=$($weg.Enabled)"
    "Liste: $($lv.Items.Count) Einträge in $($lv.Groups.Count) Gruppen | Fenster $($f.Width)x$($f.Height)"
    $f.Close()
    exit 0
}
[void]$f.ShowDialog()
'''

if __name__ == '__main__':
    main()
