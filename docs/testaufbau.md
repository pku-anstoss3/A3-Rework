# Testaufbau auf diesem PC (15.11.2026)

Freigabe des Nutzers: Die GOG-Installation `D:\GOG Galaxy\Games\ANSTOSS 3` darf zum Testen verändert werden.
Unveränderte Gesamtkopie: `original/`.

## Änderungen an der Installation

| Datei | Zustand | Rückweg |
|---|---|---|
| `anstoss3.exe` | gepatcht (`build/anstoss3.exe`, Patch `beste-mannschaft`) | `anstoss3.exe.orig` zurückbenennen |
| `anstoss3.exe.orig` | Original 1.40 (SHA-256 `89B88EF5…6B2A`) | – |
| `Grafik-Modus.cmd` | neu: schaltet den Grafik-Wrapper um | löschen |
| `ddraw.dll` | GOG-Wrapper wieder aktiv (ohne ihn bleibt das Fenster weiß) | – |
| `dxcfg.ini` | `presentation=windowed`, `display=1600x1200@60` → Fenster 1600×1200 | Werte aus `original/dxcfg.ini` |
| `saves/Karriere383.an3` | Kopie des aktuellen Spielstands zum Testen | löschen |

## Wichtig für Kopien der Installation

Das Spiel liest beim Start `HKLM\SOFTWARE\WOW6432Node\Ascaron\Anstoss 3\1.00\InstalledTo` und wechselt per
`SetCurrentDirectoryA` (Aufruf bei 0x0040E177) in diesen Ordner. Eine kopierte Installation benutzt deshalb
Daten und Spielstände des registrierten Ordners, nicht die der Kopie. **G**

## Messung Verzögerung (15.11.2026)

- `tools/messung_verzoegerung.ps1`: nach jedem Klick 2–8 s lang ein Thread mit 100 % auf einem Kern, kaum Lesezugriffe. **G**
- `tools/profil.ps1` (Stichproben-Profiler, 3322 Proben): **95,6 % in `d3d9.dll`**, 0,03 % in `anstoss3.exe`. **G**
  Alle d3d9-Proben auf 4 Adressen in einer Schleife (RVA 0x14A5BB–0x14A5C9, SysWOW64\d3d9.dll), die Gleitkommawerte lädt –
  vermutlich Vertex-Verarbeitung in Software oder Lesen aus Grafikspeicher. Auslöser ist der GOG-Wrapper, nicht der Spielcode. **V**
- Versuch 1: `vsync=disabled` in `dxcfg.ini` (Erwartung gering, da kein Warte-, sondern Rechenschleife).
  Ergebnis: keine Besserung.
- Versuch 2: cnc-ddraw 7.1.0.0 (`downloads/cnc-ddraw-7.1.0.0/`, im Spielordner als `ddraw.dll.cnc` + `ddraw.ini`).
  Ergebnis: Endlosschleife der Meldung „SGL: CreateZBuffer returned DDERR_GENERIC“. Die 3D-Engine `D3D_Dll.dll`
  legt beim Start einen Z-Buffer an, auch ohne 3D-Ansicht; cnc-ddraw kann kein Direct3D. Zurück auf GOG-Wrapper.
- Versuch 3: dgVoodoo2 2.87.6 (`downloads/dgVoodoo2-2.87.6/`, im Spielordner `ddraw.dll.dgv`, `D3DImm.dll.dgv`, `dgVoodoo.conf`).
  a) `FullScreenMode=false`, `Resolution=h:1600, v:1200`, `ScalingMode=stretched_ar`: Darstellung kaputt, nichts anklickbar.
  b) dazu `Resolution=unforced`: Spiel stellt den Bildschirm auf niedrige Auflösung um (vermutlich Vollbild, weil
     `AppControlledScreenMode=true` dem Spiel die Wahl lässt). Unbenutzbar. Zurück auf GOG-Wrapper.
  Offener Versuch: `AppControlledScreenMode=false` (erzwingt Fenster).

## Ursache eingegrenzt (Stapel-Profiler, 15.11.2026)

- Auftreten laut Nutzer erst seit Wechsel Radeon Vega 56 → Radeon RX 6800 XT; schon im Hauptmenü, vor allem bei Bildwechseln und Klicks in Listen.
- `tools/profil_stack.ps1` + `tools/profil_auswertung.py`: 1648 von 1834 Stichproben in d3d9.dll; davon 1587 unter
  `D3D_Dll.dll` 0x0502D2B6 = `IDirect3DDevice3::SetTexture(0, tex)` in der Hilfsroutine 0x0502D290, aufgerufen mit tex = NULL
  (0x0501BAD8 „Textur aus“). Die Routine prüft nicht, ob die Textur schon gesetzt ist. **G**
- Versuchspatch `settexture-cache` für `D3D_Dll.dll` (`tools/a3patch.py`): überspringt den Aufruf, wenn dieselbe Textur
  bereits gesetzt ist. Installiert; Original als `D3D_Dll.dll.orig`. Ergebnis laut Nutzer: weiterhin langsam.
- Genauer: der Wrapper ruft an der heißen Stelle `IDirect3DDevice9::DrawPrimitiveUP`/`DrawIndexedPrimitiveUP`
  (ddraw.dll 0x18042D5A/0x18042DB7); die d3d9-Schleife verarbeitet Eckpunkte auf der CPU. SGL setzt
  `D3DRENDERSTATE_CLIPPING` nie (Standard: an). **G**
- Versuchspatch `clipping-aus`: am Ende der Zustandsroutine 0x0502D8F0 zusätzlich `SetRenderState(CLIPPING, FALSE)`.
  Installiert zusammen mit `settexture-cache` (SHA-256 `321444FE…CC52`). Vermutung (V): d3d9 schneidet mit dem
  RX-6800-XT-Treiber vortransformierte Eckpunkte in Software zu. Ergebnis: offen.

## Test Verzögerung bei Menüs/Bildschirmwechseln

Ursache noch nicht gemessen. Vermutung (V): Der GOG-Wrapper (D3D9-basiert, „GOG.com DirectX 1-7 wrapper“ 1.1.0.1506)
bremst das Zeichnen der Menüs über GDI auf der DirectDraw-Oberfläche.

1. Spiel mit Windows-DirectDraw starten (aktueller Zustand) und Menüwechsel vergleichen.
2. Falls Grafikfehler oder Absturz: `Grafik-Modus.cmd gog` ausführen (stellt den Ursprungszustand her).
3. Ergebnis melden; nächster Kandidat wäre ein anderer Wrapper (z. B. DDrawCompat oder cnc-ddraw, Download nötig).
