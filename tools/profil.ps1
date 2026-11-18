# Sampling profiler for anstoss3.exe. Must run in 32-bit PowerShell (SysWOW64) so thread contexts and
# module list are those of the 32-bit game.
# Every few ms the busiest thread is briefly suspended and its instruction pointer (EIP) recorded.
# Usage: <SysWOW64 powershell> -File profil.ps1 <seconds> <out.csv>
param([int]$Seconds = 120, [string]$Out = 'profil.csv')
Add-Type @'
using System; using System.Runtime.InteropServices; using System.Collections.Generic; using System.Diagnostics;
public static class Prof {
  [DllImport("kernel32.dll")] static extern IntPtr OpenThread(int a, bool i, int id);
  [DllImport("kernel32.dll")] static extern int SuspendThread(IntPtr h);
  [DllImport("kernel32.dll")] static extern int ResumeThread(IntPtr h);
  [DllImport("kernel32.dll")] static extern bool GetThreadContext(IntPtr h, IntPtr ctx);
  [DllImport("kernel32.dll")] static extern bool GetThreadTimes(IntPtr h, out long c, out long e, out long k, out long u);
  [DllImport("kernel32.dll")] static extern bool CloseHandle(IntPtr h);
  public static Dictionary<uint,int> Run(int pid, int seconds) {
    var counts = new Dictionary<uint,int>();
    IntPtr raw = Marshal.AllocHGlobal(1024 + 16);
    IntPtr ctx = new IntPtr((raw.ToInt64() + 15) & ~15L);
    var last = new Dictionary<int,long>(); var handles = new Dictionary<int,IntPtr>();
    var sw = Stopwatch.StartNew();
    while (sw.Elapsed.TotalSeconds < seconds) {
      Process p; try { p = Process.GetProcessById(pid); } catch { break; }
      int best = -1; long bestD = 0;
      foreach (ProcessThread t in p.Threads) {
        IntPtr h; if (!handles.TryGetValue(t.Id, out h)) { h = OpenThread(0x004A, false, t.Id); handles[t.Id] = h; }
        if (h == IntPtr.Zero) continue;
        long c, e, k, u; if (!GetThreadTimes(h, out c, out e, out k, out u)) continue;
        long cur = k + u, prev; last.TryGetValue(t.Id, out prev); last[t.Id] = cur;
        if (prev != 0 && cur - prev > bestD) { bestD = cur - prev; best = t.Id; }
      }
      if (best >= 0) {
        IntPtr h = handles[best];
        if (SuspendThread(h) != -1) {
          Marshal.WriteInt32(ctx, 0, 0x10001);           // CONTEXT_i386 | CONTEXT_CONTROL
          if (GetThreadContext(h, ctx)) {
            uint eip = (uint)Marshal.ReadInt32(ctx, 0xB8);
            int n; counts.TryGetValue(eip, out n); counts[eip] = n + 1;
          }
          ResumeThread(h);
        }
      }
      System.Threading.Thread.Sleep(5);
    }
    foreach (var h in handles.Values) if (h != IntPtr.Zero) CloseHandle(h);
    Marshal.FreeHGlobal(raw);
    return counts;
  }
}
'@
$wait = Get-Date
do { $p = Get-Process anstoss3 -ErrorAction SilentlyContinue | Select-Object -First 1; if (-not $p) { Start-Sleep 1 } }
while (-not $p -and ((Get-Date) - $wait).TotalSeconds -lt 300)
if (-not $p) { 'anstoss3 not running' | Set-Content $Out; exit 1 }
$mods = $p.Modules | ForEach-Object { "$($_.ModuleName);$([int64]$_.BaseAddress);$($_.ModuleMemorySize)" }
$counts = [Prof]::Run($p.Id, $Seconds)
'# modules' | Set-Content $Out
$mods | Add-Content $Out
'# samples eip;count' | Add-Content $Out
$counts.GetEnumerator() | Sort-Object Value -Descending | ForEach-Object { "{0:X8};{1}" -f $_.Key, $_.Value } | Add-Content $Out
