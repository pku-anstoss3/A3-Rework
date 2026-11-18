# Sampling profiler with stack scan for anstoss3.exe. Run in 32-bit PowerShell (SysWOW64).
# For each sample of the busiest thread: EIP plus the stack (from ESP, up to 64 KB) is scanned for values that point
# into the code of the given modules; the first hits per module are recorded as a call chain candidate.
# Return-address candidates are verified later (preceding CALL instruction) by tools/profil_auswertung.py.
# Usage: <SysWOW64 powershell> -File profil_stack.ps1 <seconds> <out.txt>
param([int]$Seconds = 150, [string]$Out = 'profil_stack.txt')
Add-Type @'
using System; using System.Runtime.InteropServices; using System.Collections.Generic; using System.Diagnostics; using System.Text;
public static class ProfS {
  [DllImport("kernel32.dll")] static extern IntPtr OpenThread(int a, bool i, int id);
  [DllImport("kernel32.dll")] static extern IntPtr OpenProcess(int a, bool i, int id);
  [DllImport("kernel32.dll")] static extern int SuspendThread(IntPtr h);
  [DllImport("kernel32.dll")] static extern int ResumeThread(IntPtr h);
  [DllImport("kernel32.dll")] static extern bool GetThreadContext(IntPtr h, IntPtr ctx);
  [DllImport("kernel32.dll")] static extern bool GetThreadTimes(IntPtr h, out long c, out long e, out long k, out long u);
  [DllImport("kernel32.dll")] static extern bool ReadProcessMemory(IntPtr p, IntPtr a, byte[] b, int n, out int r);
  [DllImport("kernel32.dll")] static extern bool CloseHandle(IntPtr h);
  public static List<string> Run(int pid, int seconds, uint[] lo, uint[] hi, string[] names) {
    var res = new List<string>();
    IntPtr proc = OpenProcess(0x0410, false, pid);
    IntPtr raw = Marshal.AllocHGlobal(1024 + 16);
    IntPtr ctx = new IntPtr((raw.ToInt64() + 15) & ~15L);
    var last = new Dictionary<int,long>(); var handles = new Dictionary<int,IntPtr>();
    byte[] buf = new byte[65536];
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
        IntPtr h = handles[best]; uint eip = 0, esp = 0; int got = 0;
        if (SuspendThread(h) != -1) {
          Marshal.WriteInt32(ctx, 0, 0x10001);
          if (GetThreadContext(h, ctx)) {
            eip = (uint)Marshal.ReadInt32(ctx, 0xB8); esp = (uint)Marshal.ReadInt32(ctx, 0xC4);
            for (int off = 0; off < buf.Length; off += 4096) {
              int r; byte[] page = new byte[4096];
              if (!ReadProcessMemory(proc, new IntPtr((long)esp + off), page, 4096, out r) || r == 0) break;
              Buffer.BlockCopy(page, 0, buf, off, r); got += r; if (r < 4096) break;
            }
          }
          ResumeThread(h);
        }
        if (eip != 0) {
          var sb = new StringBuilder(); sb.Append(eip.ToString("X8"));
          var cnt = new int[names.Length];
          for (int i = 0; i + 4 <= got; i += 4) {
            uint v = BitConverter.ToUInt32(buf, i);
            for (int m = 0; m < names.Length; m++)
              if (v >= lo[m] && v < hi[m] && cnt[m] < 12) { cnt[m]++; sb.Append(' ').Append(names[m]).Append(':').Append(v.ToString("X8")); }
          }
          res.Add(sb.ToString());
        }
      }
      System.Threading.Thread.Sleep(10);
    }
    foreach (var h in handles.Values) if (h != IntPtr.Zero) CloseHandle(h);
    CloseHandle(proc); Marshal.FreeHGlobal(raw);
    return res;
  }
}
'@
$wait = Get-Date
do { $p = Get-Process anstoss3 -ErrorAction SilentlyContinue | Select-Object -First 1; if (-not $p) { Start-Sleep 1 } }
while (-not $p -and ((Get-Date) - $wait).TotalSeconds -lt 300)
if (-not $p) { 'anstoss3 not running' | Set-Content $Out; exit 1 }
Start-Sleep -Seconds 3
$p.Refresh()
$want = @{ 'anstoss3.exe' = 'exe'; 'ddraw.dll' = 'ddraw'; 'd3d_dll.dll' = 'sgl'; 'd3d9.dll' = 'd3d9'; 'mfc42.dll' = 'mfc' }
$lo = @(); $hi = @(); $nm = @(); $mods = @()
foreach ($m in $p.Modules) {
  $k = $m.ModuleName.ToLower(); $mods += "$($m.ModuleName);$([int64]$m.BaseAddress);$($m.ModuleMemorySize);$($m.FileName)"
  if ($want.ContainsKey($k)) { $lo += [uint32][int64]$m.BaseAddress; $hi += [uint32]([int64]$m.BaseAddress + $m.ModuleMemorySize); $nm += $want[$k] }
}
$res = [ProfS]::Run($p.Id, $Seconds, [uint32[]]$lo, [uint32[]]$hi, [string[]]$nm)
'# modules' | Set-Content $Out
$mods | Add-Content $Out
'# samples' | Add-Content $Out
$res | Add-Content $Out
