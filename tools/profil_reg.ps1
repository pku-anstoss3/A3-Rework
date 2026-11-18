# Register-Profiler fuer anstoss3.exe. In 32-Bit-PowerShell (SysWOW64) starten. Aendert nichts am Spiel.
# Fragt, was d3d9.dll in der heissen Schleife (Clip-Code-Berechnung, RVA 0x14A1F3-0x14A726) liest:
#  - Register (EDI = Zeiger auf Eckpunkt, ESI = Geraeteobjekt, EDX = Restzaehler)
#  - Anzahl/Basis/Schrittweite aus dem Geraeteobjekt, Aufrufparameter des GOG-Wrappers (globale Variablen)
#  - Art des gelesenen Speichers (VirtualQueryEx) und Lesegeschwindigkeit (ReadProcessMemory, Vergleich mit normalem Speicher)
# Aufruf: <SysWOW64 powershell> -File profil_reg.ps1 <Sekunden> <Ausgabedatei> [-WaitSeconds n] [-CompileOnly]
# Gilt fuer d3d9.dll 10.0.26100.9818 (SHA-256 DA332F72...21E5) und GOG-ddraw.dll (Basis 0x18000000).
param([int]$Seconds = 90, [string]$Out = 'profil_reg.txt', [int]$WaitSeconds = 900, [switch]$CompileOnly)
Add-Type @'
using System; using System.Runtime.InteropServices; using System.Collections.Generic; using System.Diagnostics; using System.Text;
public static class ProfR {
  [DllImport("kernel32.dll")] static extern IntPtr OpenThread(int a, bool i, int id);
  [DllImport("kernel32.dll")] static extern IntPtr OpenProcess(int a, bool i, int id);
  [DllImport("kernel32.dll")] static extern int SuspendThread(IntPtr h);
  [DllImport("kernel32.dll")] static extern int ResumeThread(IntPtr h);
  [DllImport("kernel32.dll")] static extern bool GetThreadContext(IntPtr h, IntPtr ctx);
  [DllImport("kernel32.dll")] static extern bool GetThreadTimes(IntPtr h, out long c, out long e, out long k, out long u);
  [DllImport("kernel32.dll")] static extern bool ReadProcessMemory(IntPtr p, IntPtr a, byte[] b, int n, out int r);
  [DllImport("kernel32.dll")] static extern int VirtualQueryEx(IntPtr p, IntPtr a, byte[] mbi, int len);
  [DllImport("kernel32.dll")] static extern bool CloseHandle(IntPtr h);
  static byte[] b4 = new byte[4];
  static string RU(IntPtr proc, uint addr) {
    int r; if (!ReadProcessMemory(proc, new IntPtr((long)addr), b4, 4, out r) || r != 4) return "?";
    return BitConverter.ToUInt32(b4, 0).ToString("X8");
  }
  // Zeit in Mikrosekunden fuer das Lesen von n Byte ab addr (Minimum aus 3 Laeufen); -1 = nicht lesbar
  static double TimeRead(IntPtr proc, uint addr, int n, byte[] buf) {
    double best = -1;
    for (int i = 0; i < 3; i++) {
      int r; long t0 = Stopwatch.GetTimestamp();
      bool ok = ReadProcessMemory(proc, new IntPtr((long)addr), buf, n, out r);
      long t1 = Stopwatch.GetTimestamp();
      if (!ok || r != n) return -1;
      double us = (t1 - t0) * 1e6 / Stopwatch.Frequency;
      if (best < 0 || us < best) best = us;
    }
    return best;
  }
  public static List<string> Run(int pid, int seconds, uint d3d9, uint ddraw) {
    var res = new List<string>();
    IntPtr proc = OpenProcess(0x0410, false, pid);
    IntPtr raw = Marshal.AllocHGlobal(1024 + 16);
    IntPtr ctx = new IntPtr((raw.ToInt64() + 15) & ~15L);
    var last = new Dictionary<int,long>(); var handles = new Dictionary<int,IntPtr>();
    var timed = new Dictionary<uint,int>();
    byte[] mbi = new byte[28]; byte[] big = new byte[16384];
    uint hotLo = d3d9 + 0x14A1F3, hotHi = d3d9 + 0x14A726;
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
          Marshal.WriteInt32(ctx, 0, 0x10007);
          string line = null;
          if (GetThreadContext(h, ctx)) {
            double tms = sw.Elapsed.TotalMilliseconds;
            uint edi = (uint)Marshal.ReadInt32(ctx, 0x9C), esi = (uint)Marshal.ReadInt32(ctx, 0xA0);
            uint edx = (uint)Marshal.ReadInt32(ctx, 0xA8), ecx = (uint)Marshal.ReadInt32(ctx, 0xAC), eax = (uint)Marshal.ReadInt32(ctx, 0xB0);
            uint eip = (uint)Marshal.ReadInt32(ctx, 0xB8), esp = (uint)Marshal.ReadInt32(ctx, 0xC4);
            if (eip >= hotLo && eip < hotHi) {
              var sb = new StringBuilder();
              sb.Append("H\t").Append(tms.ToString("F3")).Append('\t').Append((eip - d3d9).ToString("X6"));
              sb.Append("\tedi=").Append(edi.ToString("X8")).Append("\tesi=").Append(esi.ToString("X8"));
              sb.Append("\teax=").Append(eax.ToString("X8")).Append("\tecx=").Append(ecx.ToString("X8")).Append("\tedx=").Append(edx.ToString("X8"));
              sb.Append("\tcnt=").Append(RU(proc, esi + 0x173A0)).Append("\tbase=").Append(RU(proc, esi + 0x173DC));
              sb.Append("\tstride=").Append(RU(proc, esi + 0x173E0)).Append("\tmode=").Append(RU(proc, esi + 0x1739C));
              sb.Append("\tflags=").Append(RU(proc, esi + 0x173BC)).Append("\tclipout=").Append(RU(proc, esi + 0x173CC));
              sb.Append("\trem=").Append(RU(proc, esp + 0x0C));
              // Aufrufparameter des Wrappers (globale Variablen in ddraw.dll, siehe Disassembly 0x18042D2F-0x18042DB7)
              sb.Append("\twNumVerts=").Append(RU(proc, ddraw + 0x16F654)).Append("\twStride=").Append(RU(proc, ddraw + 0x16FCA0));
              sb.Append("\twPrimCnt=").Append(RU(proc, ddraw + 0x49F0E0)).Append("\twPrimType=").Append(RU(proc, ddraw + 0x16F628));
              sb.Append("\twIndexed=").Append(RU(proc, ddraw + 0x44DF24));
              uint ab = 0;
              if (VirtualQueryEx(proc, new IntPtr((long)edi), mbi, 28) == 28) {
                ab = BitConverter.ToUInt32(mbi, 4);
                sb.Append("\tmbiBase=").Append(BitConverter.ToUInt32(mbi, 0).ToString("X8")).Append("\tallocBase=").Append(ab.ToString("X8"));
                sb.Append("\tallocProt=").Append(BitConverter.ToUInt32(mbi, 8).ToString("X")).Append("\tsize=").Append(BitConverter.ToUInt32(mbi, 12).ToString("X"));
                sb.Append("\tstate=").Append(BitConverter.ToUInt32(mbi, 16).ToString("X")).Append("\tprot=").Append(BitConverter.ToUInt32(mbi, 20).ToString("X"));
                sb.Append("\ttype=").Append(BitConverter.ToUInt32(mbi, 24).ToString("X"));
                uint regEnd = BitConverter.ToUInt32(mbi, 0) + BitConverter.ToUInt32(mbi, 12);
                int n; timed.TryGetValue(ab, out n);
                uint pg = edi & 0xFFFFF000u;
                if (n < 4 && regEnd - pg >= 4096) {
                  timed[ab] = n + 1;
                  int len = (int)Math.Min(16384u, regEnd - pg);
                  double tv = TimeRead(proc, pg, len, big);
                  double tr = TimeRead(proc, d3d9 + 0x1000, len, big);
                  sb.Append("\treadLen=").Append(len).Append("\treadVtx_us=").Append(tv.ToString("F1")).Append("\treadRef_us=").Append(tr.ToString("F1"));
                }
              }
              line = sb.ToString();
            } else {
              line = "S\t" + tms.ToString("F3") + "\t" + eip.ToString("X8");
            }
          }
          ResumeThread(h);
          if (line != null) res.Add(line);
        }
      }
      System.Threading.Thread.Sleep(2);
    }
    foreach (var h in handles.Values) if (h != IntPtr.Zero) CloseHandle(h);
    CloseHandle(proc); Marshal.FreeHGlobal(raw);
    return res;
  }
}
'@
if ($CompileOnly) { "kompiliert, IntPtr-Groesse $([IntPtr]::Size)"; exit 0 }
if ([IntPtr]::Size -ne 4) { 'Fehler: bitte 32-Bit-PowerShell benutzen' | Set-Content -LiteralPath $Out; exit 2 }
$wait = Get-Date
do { $p = Get-Process anstoss3 -ErrorAction SilentlyContinue | Select-Object -First 1; if (-not $p) { Start-Sleep 1 } }
while (-not $p -and ((Get-Date) - $wait).TotalSeconds -lt $WaitSeconds)
if (-not $p) { 'anstoss3 laeuft nicht' | Set-Content -LiteralPath $Out; exit 1 }
# warten, bis d3d9.dll geladen ist
$d3d9 = $null; $dd = $null
for ($i = 0; $i -lt 60 -and -not ($d3d9 -and $dd); $i++) {
  Start-Sleep -Seconds 1; $p.Refresh()
  foreach ($m in $p.Modules) { $k = $m.ModuleName.ToLower(); if ($k -eq 'd3d9.dll') { $d3d9 = $m }; if ($k -eq 'ddraw.dll') { $dd = $m } }
}
if (-not ($d3d9 -and $dd)) { 'd3d9.dll oder ddraw.dll nicht geladen' | Set-Content -LiteralPath $Out; exit 3 }
$head = @('# start ' + (Get-Date -Format s),
  "# d3d9;$('{0:X8}' -f [int64]$d3d9.BaseAddress);$($d3d9.FileName);$($d3d9.FileVersionInfo.FileVersion)",
  "# ddraw;$('{0:X8}' -f [int64]$dd.BaseAddress);$($dd.FileName)")
foreach ($m in $p.Modules) { $head += "# mod;$('{0:X8}' -f [int64]$m.BaseAddress);$('{0:X}' -f $m.ModuleMemorySize);$($m.FileName)" }
$res = [ProfR]::Run($p.Id, $Seconds, [uint32][int64]$d3d9.BaseAddress, [uint32][int64]$dd.BaseAddress)
$head | Set-Content -LiteralPath $Out
$res | Add-Content -LiteralPath $Out
