# Liest die D3D9-Geraetefaehigkeiten (D3DCAPS9) des Grafiktreibers, so wie der GOG-Wrapper sie abfragt
# (IDirect3D9::GetDeviceCaps, Adapter 0, HAL). Startet kein Spiel, legt kein Geraet an. In 32-Bit-PowerShell starten.
Add-Type @'
using System; using System.Runtime.InteropServices;
public static class Caps9 {
  [DllImport("d3d9.dll")] static extern IntPtr Direct3DCreate9(uint sdk);
  [UnmanagedFunctionPointer(CallingConvention.StdCall)] delegate int GetDeviceCapsD(IntPtr self, uint adapter, uint devType, IntPtr caps);
  [UnmanagedFunctionPointer(CallingConvention.StdCall)] delegate uint ReleaseD(IntPtr self);
  public static byte[] Get(out int hr) {
    IntPtr d3d = Direct3DCreate9(32); hr = -1; if (d3d == IntPtr.Zero) return null;
    IntPtr vt = Marshal.ReadIntPtr(d3d);
    var gdc = (GetDeviceCapsD)Marshal.GetDelegateForFunctionPointer(Marshal.ReadIntPtr(vt, 14 * IntPtr.Size), typeof(GetDeviceCapsD));
    var rel = (ReleaseD)Marshal.GetDelegateForFunctionPointer(Marshal.ReadIntPtr(vt, 2 * IntPtr.Size), typeof(ReleaseD));
    IntPtr mem = Marshal.AllocHGlobal(512); byte[] b = new byte[304];
    for (int i = 0; i < 512; i++) Marshal.WriteByte(mem, i, 0);
    hr = gdc(d3d, 0, 1, mem); Marshal.Copy(mem, b, 0, 304);
    Marshal.FreeHGlobal(mem); rel(d3d); return b;
  }
}
'@
$hr = 0; $b = [Caps9]::Get([ref]$hr)
"IntPtr-Groesse: $([IntPtr]::Size)   GetDeviceCaps hr = 0x$('{0:X8}' -f $hr)"
if ($b) {
  function U($o) { [BitConverter]::ToUInt32($b, $o) }
  $pmc = U 0x20
  'DevCaps              = 0x{0:X8}  (HWTRANSFORMANDLIGHT 0x10000: {1}, PUREDEVICE 0x100000: {2})' -f (U 0x1C), [bool]((U 0x1C) -band 0x10000), [bool]((U 0x1C) -band 0x100000)
  'PrimitiveMiscCaps    = 0x{0:X8}  (CLIPTLVERTS 0x200: {1}, CLIPPLANESCALEDPOINTS 0x100: {2})' -f $pmc, [bool]($pmc -band 0x200), [bool]($pmc -band 0x100)
  'VertexProcessingCaps = 0x{0:X8}' -f (U 0xD4)
  'VertexShaderVersion  = 0x{0:X8}' -f (U 0xC4)
  'PixelShaderVersion   = 0x{0:X8}' -f (U 0xCC)
  'GuardBand L/T/R/B    = {0} / {1} / {2} / {3}' -f [BitConverter]::ToSingle($b,0x74), [BitConverter]::ToSingle($b,0x78), [BitConverter]::ToSingle($b,0x7C), [BitConverter]::ToSingle($b,0x80)
}
