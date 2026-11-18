# Rebuild everything from the savegames in saves\ and check the page:
#   powershell -File tools\seite_bauen.ps1            (only merge + page)
#   powershell -File tools\seite_bauen.ps1 -Scan      (read new savegames first)
param([switch]$Scan, [string]$Stand = 'Karriere383')
$a = Split-Path -Parent $PSScriptRoot
if ($Scan) { python "$a\tools\a3scan.py" "$a\saves" "$a\analyse\scan"; if ($LASTEXITCODE) { throw 'a3scan fehlgeschlagen' } }
python "$a\tools\a3verlauf.py" "$a\analyse\scan" "$a\analyse\verlauf.json" 2>&1 | Out-File -LiteralPath "$a\analyse\verlauf.txt" -Encoding utf8
if ($LASTEXITCODE) { Get-Content -LiteralPath "$a\analyse\verlauf.txt" -Encoding utf8 -Tail 15; throw 'a3verlauf fehlgeschlagen' }
Get-Content -LiteralPath "$a\analyse\verlauf.txt" -Encoding utf8 | Select-String -Pattern '^(Liga-Archiv|Ranglisten|Widerspr|\d+ Spielst|  FEHLER)' | ForEach-Object { $_.Line }
python "$a\tools\a3export.py" "$a\analyse\save383" "$a\ansicht\vorlage.html" "$a\ansicht\spielstand-383.html" "Spielstand 383" --verlauf "$a\analyse\verlauf.json" --alltimes "$a\saves\alltime-rechner-1\alltimes_1.saq=Dein Rechner, Stand Oktober 2022 (alltimes_1)" "$a\saves\alltime-rechner-1\alltimes_2.saq=Dein Rechner, am 21.3.2023 neu angelegt (alltimes_2)" "$a\analyse\alltimes.saq=Dein Rechner heute, Startwerte vom 13.10.2023"
if ($LASTEXITCODE) { throw 'a3export fehlgeschlagen' }
"Seite: $([math]::Round((Get-Item -LiteralPath "$a\ansicht\spielstand-383.html").Length / 1MB, 2)) MB"
node "$a\tools\seite_pruefen.js" "$a\ansicht\spielstand-383.html"
