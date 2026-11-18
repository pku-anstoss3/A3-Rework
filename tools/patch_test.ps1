# Test of the current patch installer without its window, in build\patch-test (never in the game folder).
#   pwsh -File tools\patch_test.ps1 [-Version 1.44]
# Needs the reference files build\endpaket-<Version>\ written by tools\patch_bauen.py, the untouched files in original\
# and the earlier states build\endpaket (1.41), build\endpaket-1.42, build\endpaket-1.43,
# build\kandidat-1.43 and build\kandidat-1.44 (test builds), build\anstoss3.exe.
# Every case compares the SHA-256 of the three target files and of their backups with the expected values and checks
# the exit code; the last cases check the state shown by the window (-Probe). Ends with a summary, exit code 1 on failure.
param([string]$Version = '1.44')
$a = Split-Path -Parent $PSScriptRoot
$ps1 = Join-Path $a "patch-$Version\Anstoss3-Patch-$Version.ps1"
$t = Join-Path $a 'build\patch-test'
$ref = Join-Path $a "build\endpaket-$Version"
$script:faelle = 0; $script:fehler = 0

function Leeren {
    if (Test-Path -LiteralPath $t) {
        Get-ChildItem -LiteralPath $t -Force -Recurse -File | ForEach-Object { $_.IsReadOnly = $false }
        Get-ChildItem -LiteralPath $t -Force | Remove-Item -Recurse -Force
    } else { New-Item -ItemType Directory -Force $t | Out-Null }
}
# Copies files into the test folder: Lege @{ 'anstoss3.exe' = '<source>'; 'deb\MeineDialoge.rch' = '<source>' }
function Lege($dateien) {
    foreach ($ziel in $dateien.Keys) {
        $p = Join-Path $t $ziel
        New-Item -ItemType Directory -Force (Split-Path -Parent $p) | Out-Null
        Copy-Item -LiteralPath (Join-Path $a $dateien[$ziel]) -Destination $p -Force
        (Get-Item -LiteralPath $p).IsReadOnly = $false       # the files in original\ are read-only; case A sets it itself
    }
}
function Kurz($f) { if (Test-Path -LiteralPath $f) { (Get-FileHash -LiteralPath $f).Hash.Substring(0, 8) } else { '--------' } }
function Pruefe([string]$soll) {
    $ist = "exe $(Kurz "$t\anstoss3.exe") rch $(Kurz "$t\deb\MeineDialoge.rch") ddraw $(Kurz "$t\ddraw.dll") | Sicherung exe $(Kurz "$t\anstoss3.exe.vor-patch") rch $(Kurz "$t\deb\MeineDialoge.rch.vor-patch") ddraw $(Kurz "$t\ddraw.dll.vor-patch")"
    $script:faelle++
    if ($ist -eq $soll) { "   OK    $ist" } else { $script:fehler++; "   ABWEICHUNG"; "   Ist:  $ist"; "   Soll: $soll" }
}
function Lauf([int]$rueckgabe, [string[]]$arg) {
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ps1 -Still -Ordner $t @arg | ForEach-Object { "      $_" }
    if ($LASTEXITCODE -ne $rueckgabe) { $script:fehler++; "   ABWEICHUNG: Rückgabe $LASTEXITCODE statt $rueckgabe" }
}
# Window state: runs -Probe on the test folder and looks for the given text in the reported state
function Fenster([string]$erwartet) {
    $bild = Join-Path $a 'build\patch-test-fenster.png'
    $aus = (& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ps1 -Ordner $t -Probe $bild) -join "`n"
    $script:faelle++
    if ($aus.Contains($erwartet)) { "   OK    Fenster: $erwartet" } else { $script:fehler++; "   ABWEICHUNG Fenster, erwartet: $erwartet"; $aus }
}

$N = '--------'
$O = Kurz "$a\original\anstoss3.exe"; $F = Kurz "$ref\anstoss3.exe"; $FO = Kurz "$ref\anstoss3-ohne-spiellogik.exe"
$RO = Kurz "$a\original\deb\MeineDialoge.rch"; $RF = Kurz "$ref\MeineDialoge.rch"
$DO = Kurz "$a\original\ddraw.dll"; $DF = Kurz "$ref\ddraw.dll"
$V141 = Kurz "$a\build\endpaket\anstoss3.exe"; $V142 = Kurz "$a\build\endpaket-1.42\anstoss3.exe"
$K = Kurz "$a\build\kandidat-1.43\anstoss3.exe"; $T4 = Kurz "$a\build\anstoss3.exe"
$V143 = Kurz "$a\build\endpaket-1.43\anstoss3.exe"; $V143o = Kurz "$a\build\endpaket-1.43\anstoss3-ohne-spiellogik.exe"; $K144 = Kurz "$a\build\kandidat-1.44\anstoss3.exe"
"Referenz $Version`: exe $F, ohne Spiellogik $FO, rch $RF, ddraw $DF | Original: exe $O, rch $RO, ddraw $DO"
"Frühere Stände: 1.41 $V141, 1.42 $V142, 1.43 $V143 / ohne Spiellogik $V143o, Testfassungen $K und $K144, Teilstand $T4"
if ($O -ne '89B88EF5' -or $RO -ne 'AA68E14E' -or $DO -ne 'B2CB0FD0' -or $N -in $F, $FO, $RF, $DF, $V141, $V142, $V143, $V143o, $K, $K144, $T4) { 'Ausgangsdateien fehlen oder sind verändert.'; exit 1 }
$orig = @{ 'anstoss3.exe' = 'original\anstoss3.exe'; 'deb\MeineDialoge.rch' = 'original\deb\MeineDialoge.rch'; 'ddraw.dll' = 'original\ddraw.dll' }

'A) Original, exe und Textdatei schreibgeschützt, Installation mit -Ddraw: alles installiert, drei Sicherungen'
Leeren; Lege $orig
(Get-Item "$t\anstoss3.exe").IsReadOnly = $true; (Get-Item "$t\deb\MeineDialoge.rch").IsReadOnly = $true
Fenster 'Spiellogik-Option: gesetzt=True'
Lauf 0 '-Ddraw'; Pruefe "exe $F rch $RF ddraw $DF | Sicherung exe $O rch $RO ddraw $DO"
$script:faelle++
if ((Get-Item "$t\anstoss3.exe").IsReadOnly -and (Get-Item "$t\deb\MeineDialoge.rch").IsReadOnly) { '   OK    Schreibschutz erhalten' } else { $script:fehler++; '   ABWEICHUNG: Schreibschutz nicht erhalten' }
Fenster 'Spiellogik-Option: gesetzt=True'
'B) Wiederholung: keine Änderung'
Lauf 0 '-Ddraw'; Pruefe "exe $F rch $RF ddraw $DF | Sicherung exe $O rch $RO ddraw $DO"
'C) Spiellogik nachträglich abwählen: nur die Gruppe geht zurück'
Lauf 0 '-Ddraw', '-OhneSpiellogik'; Pruefe "exe $FO rch $RF ddraw $DF | Sicherung exe $O rch $RO ddraw $DO"
Fenster 'Spiellogik-Option: gesetzt=False'
'D) Spiellogik wieder hinzufügen'
Lauf 0 '-Ddraw'; Pruefe "exe $F rch $RF ddraw $DF | Sicherung exe $O rch $RO ddraw $DO"
'E) Deinstallation: alle drei Dateien wieder Original'
Lauf 0 '-Entfernen'; Pruefe "exe $O rch $RO ddraw $DO | Sicherung exe $O rch $RO ddraw $DO"

'F) Original, Installation ohne Spiellogik und ohne -Ddraw: ddraw unberührt'
Leeren; Lege $orig
Lauf 0 '-OhneSpiellogik'; Pruefe "exe $FO rch $RF ddraw $DO | Sicherung exe $O rch $RO ddraw $N"
'G) Deinstallation aus dem Stand ohne Spiellogik'
Lauf 0 '-Entfernen'; Pruefe "exe $O rch $RO ddraw $DO | Sicherung exe $O rch $RO ddraw $N"

'H) Stand 1.41 (mit dessen Sicherungen) + angepasste ddraw: Aktualisierung, neue Sicherung nur für die Textdatei'
Leeren; Lege $orig; Lege @{ 'anstoss3.exe' = 'build\endpaket\anstoss3.exe'; 'ddraw.dll' = 'build\ddraw.dll'; 'anstoss3.exe.vor-1.41' = 'original\anstoss3.exe'; 'ddraw.dll.vor-1.41' = 'original\ddraw.dll' }
Fenster 'Patch 1.41 ist installiert'
Lauf 0 '-Ddraw'; Pruefe "exe $F rch $RF ddraw $DF | Sicherung exe $N rch $RO ddraw $N"
'I) Deinstallation aus dem aktualisierten Stand: zurück auf 1.40'
Lauf 0 '-Entfernen'; Pruefe "exe $O rch $RO ddraw $DO | Sicherung exe $N rch $RO ddraw $N"
'J) Stand 1.41, Aktualisierung ohne Spiellogik: Trainer-Korrekturen gehen zurück'
Leeren; Lege $orig; Lege @{ 'anstoss3.exe' = 'build\endpaket\anstoss3.exe' }
Lauf 0 '-OhneSpiellogik'; Pruefe "exe $FO rch $RF ddraw $DO | Sicherung exe $V141 rch $RO ddraw $N"
'K) Stand 1.41 ohne Sicherungen: Deinstallation direkt'
Leeren; Lege $orig; Lege @{ 'anstoss3.exe' = 'build\endpaket\anstoss3.exe' }
Lauf 0 '-Entfernen'; Pruefe "exe $O rch $RO ddraw $DO | Sicherung exe $N rch $N ddraw $N"

'L) Stand 1.42 (mit dessen Sicherungen) + angepasste ddraw: Aktualisierung mit Spiellogik'
Leeren; Lege $orig; Lege @{ 'anstoss3.exe' = 'build\endpaket-1.42\anstoss3.exe'; 'ddraw.dll' = 'build\ddraw.dll'; 'anstoss3.exe.vor-patch' = 'original\anstoss3.exe'; 'ddraw.dll.vor-patch' = 'original\ddraw.dll' }
Fenster 'Patch 1.42 ist installiert'
Fenster 'Spiellogik-Option: gesetzt=True'
Lauf 0 '-Ddraw'; Pruefe "exe $F rch $RF ddraw $DF | Sicherung exe $O rch $RO ddraw $DO"
'M) Stand 1.42, Aktualisierung ohne Spiellogik'
Leeren; Lege $orig; Lege @{ 'anstoss3.exe' = 'build\endpaket-1.42\anstoss3.exe'; 'anstoss3.exe.vor-patch' = 'original\anstoss3.exe' }
Lauf 0 '-OhneSpiellogik'; Pruefe "exe $FO rch $RF ddraw $DO | Sicherung exe $O rch $RO ddraw $N"
'N) Stand 1.42: Deinstallation direkt'
Leeren; Lege $orig; Lege @{ 'anstoss3.exe' = 'build\endpaket-1.42\anstoss3.exe'; 'anstoss3.exe.vor-patch' = 'original\anstoss3.exe' }
Lauf 0 '-Entfernen'; Pruefe "exe $O rch $RO ddraw $DO | Sicherung exe $O rch $N ddraw $N"

'N1) Stand 1.43 mit Spiellogik (mit dessen Sicherungen): Aktualisierung'
Leeren; Lege $orig; Lege @{ 'anstoss3.exe' = 'build\endpaket-1.43\anstoss3.exe'; 'deb\MeineDialoge.rch' = 'build\endpaket-1.43\MeineDialoge.rch'; 'anstoss3.exe.vor-patch' = 'original\anstoss3.exe'; 'deb\MeineDialoge.rch.vor-patch' = 'original\deb\MeineDialoge.rch' }
Fenster 'Patch 1.43 ist installiert'
Fenster 'Spiellogik-Option: gesetzt=True'
Lauf 0; Pruefe "exe $F rch $RF ddraw $DO | Sicherung exe $O rch $RO ddraw $N"
'N2) Stand 1.43 ohne Spiellogik: Option bleibt abgewählt, Aktualisierung ohne Spiellogik'
Leeren; Lege $orig; Lege @{ 'anstoss3.exe' = 'build\endpaket-1.43\anstoss3-ohne-spiellogik.exe'; 'deb\MeineDialoge.rch' = 'build\endpaket-1.43\MeineDialoge.rch'; 'anstoss3.exe.vor-patch' = 'original\anstoss3.exe' }
Fenster 'Spiellogik-Option: gesetzt=False'
Lauf 0 '-OhneSpiellogik'; Pruefe "exe $FO rch $RF ddraw $DO | Sicherung exe $O rch $N ddraw $N"
'N3) Stand 1.43 ohne Spiellogik: Aktualisierung mit Spiellogik, danach Deinstallation'
Lauf 0; Pruefe "exe $F rch $RF ddraw $DO | Sicherung exe $O rch $N ddraw $N"
Lauf 0 '-Entfernen'; Pruefe "exe $O rch $RO ddraw $DO | Sicherung exe $O rch $N ddraw $N"
'N4) Testfassung 1.44 (1.43 + Konto-Korrektur): Installation ändert nur die Versionsangabe'
Leeren; Lege $orig; Lege @{ 'anstoss3.exe' = 'build\kandidat-1.44\anstoss3.exe'; 'deb\MeineDialoge.rch' = 'build\endpaket-1.43\MeineDialoge.rch' }
Lauf 0; Pruefe "exe $F rch $RF ddraw $DO | Sicherung exe $K144 rch $N ddraw $N"

'O) Testfassung 1.43 (exe und Textdatei des Kandidaten): Aktualisierung'
Leeren; Lege $orig; Lege @{ 'anstoss3.exe' = 'build\kandidat-1.43\anstoss3.exe'; 'deb\MeineDialoge.rch' = 'build\kandidat-1.43\MeineDialoge.rch'; 'ddraw.dll' = 'build\ddraw.dll' }
Lauf 0 '-Ddraw'; Pruefe "exe $F rch $RF ddraw $DF | Sicherung exe $K rch $N ddraw $N"
'P) Testfassung 1.43: Installation ohne Spiellogik'
Leeren; Lege $orig; Lege @{ 'anstoss3.exe' = 'build\kandidat-1.43\anstoss3.exe'; 'deb\MeineDialoge.rch' = 'build\kandidat-1.43\MeineDialoge.rch' }
Lauf 0 '-OhneSpiellogik'; Pruefe "exe $FO rch $RF ddraw $DO | Sicherung exe $K rch $N ddraw $N"
'Q) Testfassung 1.43: Deinstallation direkt'
Leeren; Lege $orig; Lege @{ 'anstoss3.exe' = 'build\kandidat-1.43\anstoss3.exe'; 'deb\MeineDialoge.rch' = 'build\kandidat-1.43\MeineDialoge.rch'; 'ddraw.dll' = 'build\ddraw.dll' }
Lauf 0 '-Entfernen'; Pruefe "exe $O rch $RO ddraw $DO | Sicherung exe $N rch $N ddraw $N"

'R) Teilstand (vier Korrekturen) + angepasste ddraw, Installation ohne -Ddraw: exe vervollständigen, ddraw zurück'
Leeren; Lege $orig; Lege @{ 'anstoss3.exe' = 'build\anstoss3.exe'; 'ddraw.dll' = 'build\ddraw.dll' }
Lauf 0; Pruefe "exe $F rch $RF ddraw $DO | Sicherung exe $T4 rch $RO ddraw $N"

'S) Textdatei fehlt: exe wird installiert, Hinweis'
Leeren; Lege @{ 'anstoss3.exe' = 'original\anstoss3.exe' }
Lauf 0; Pruefe "exe $F rch $N ddraw $N | Sicherung exe $O rch $N ddraw $N"
'T) fremde Textdatei: bleibt unverändert, exe wird installiert; danach Deinstallation'
Leeren; Lege @{ 'anstoss3.exe' = 'original\anstoss3.exe'; 'deb\MeineDialoge.rch' = 'original\deb\ListeDerTexte.rh' }
$fremd = Kurz "$t\deb\MeineDialoge.rch"
Lauf 0; Pruefe "exe $F rch $fremd ddraw $N | Sicherung exe $O rch $N ddraw $N"
Lauf 0 '-Entfernen'; Pruefe "exe $O rch $fremd ddraw $N | Sicherung exe $O rch $N ddraw $N"
'U) fremde Datei als anstoss3.exe: keine Datei wird geändert'
Leeren; Lege $orig; Lege @{ 'anstoss3.exe' = 'original\Editor.exe' }
$fremd = Kurz "$t\anstoss3.exe"
Lauf 1 '-Ddraw'; Pruefe "exe $fremd rch $RO ddraw $DO | Sicherung exe $N rch $N ddraw $N"
Fenster 'Installieren=False Deinstallieren=False'
'V) ohne ddraw.dll, Installation mit -Ddraw'
Leeren; Lege @{ 'anstoss3.exe' = 'original\anstoss3.exe'; 'deb\MeineDialoge.rch' = 'original\deb\MeineDialoge.rch' }
Lauf 0 '-Ddraw'; Pruefe "exe $F rch $RF ddraw $N | Sicherung exe $O rch $RO ddraw $N"
'W) Ordner ohne Spiel'
$script:faelle++
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ps1 -Still -Ordner (Join-Path $a 'docs') | ForEach-Object { "      $_" }
if ($LASTEXITCODE -eq 1) { '   OK    Rückgabe 1' } else { $script:fehler++; "   ABWEICHUNG: Rückgabe $LASTEXITCODE statt 1" }

Leeren; Remove-Item -LiteralPath (Join-Path $a 'build\patch-test-fenster.png') -ErrorAction SilentlyContinue
''
if ($script:fehler -eq 0) { "Ergebnis: alle $($script:faelle) Prüfungen bestanden."; exit 0 }
"Ergebnis: $($script:fehler) Abweichungen bei $($script:faelle) Prüfungen."; exit 1
