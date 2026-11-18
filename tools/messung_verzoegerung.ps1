# Samples anstoss3.exe every 200 ms: CPU time (total and busiest thread), bytes read, window responsiveness.
# Usage: powershell -File messung_verzoegerung.ps1 <seconds> <output.csv>
param([int]$Seconds = 90, [string]$Out = 'messung.csv')
$wait = Get-Date
do { $p = Get-Process anstoss3 -ErrorAction SilentlyContinue | Select-Object -First 1; if (-not $p) { Start-Sleep -Seconds 1 } }
while (-not $p -and ((Get-Date) - $wait).TotalSeconds -lt 300)
if (-not $p) { "anstoss3 not started within 300 s" | Set-Content $Out; exit 1 }
$cores = [Environment]::ProcessorCount
"t_ms;cpu_ms;cpu_pct_1core;top_thread_ms;read_bytes;responding" | Set-Content $Out
$t0 = Get-Date; $lastCpu = $p.TotalProcessorTime.TotalMilliseconds; $lastT = 0
$threadPrev = @{}
while (((Get-Date) - $t0).TotalSeconds -lt $Seconds) {
    Start-Sleep -Milliseconds 200
    $p.Refresh()
    if ($p.HasExited) { break }
    $t = [int]((Get-Date) - $t0).TotalMilliseconds
    $cpu = $p.TotalProcessorTime.TotalMilliseconds
    $pct = [math]::Round(100 * ($cpu - $lastCpu) / [math]::Max(1, $t - $lastT))
    $top = 0
    foreach ($th in $p.Threads) {
        try { $v = $th.TotalProcessorTime.TotalMilliseconds } catch { continue }
        $d = $v - ($threadPrev[$th.Id] | ForEach-Object { $_ })
        if ($threadPrev.ContainsKey($th.Id) -and $d -gt $top) { $top = $d }
        $threadPrev[$th.Id] = $v
    }
    $io = (Get-CimInstance Win32_Process -Filter "ProcessId=$($p.Id)").ReadTransferCount
    "$t;$([int]$cpu);$pct;$([int]$top);$io;$($p.Responding)" | Add-Content $Out
    $lastCpu = $cpu; $lastT = $t
}
