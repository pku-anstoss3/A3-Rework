# Spielstand: Herkunft der Blöcke (15.11.2026)

Aus der Speicherroutine 0x006ED31E von `anstoss3.exe` 1.40, in Schreibreihenfolge.
„Objekt“ = Speicherobjekt, geschrieben ab Objekt+0x20 mit Länge [Objekt+0x14]−8 (0x007CFF69).
„variabel“ = Adresse wird zur Laufzeit berechnet, meist in einer Schleife (z. B. 609 Vereine).
Die Zuordnung der Aufrufe zu Blocknummern im Spielstand ist wegen der Schleifen noch nicht durchgezählt.

| Codestelle | Art | Quelle | Länge |
|---|---|---|---|
| 006ED593 | Objekt | 0x01BA4B68 (Daten ab +0x20) | aus Objekt |
| 006ED5B3 | Objekt | 0x00B5CB68 (Daten ab +0x20) | aus Objekt |
| 006ED5CB | Puffer | 0x00B1F860 | 1 |
| 006ED5E6 | Puffer | 0x00B0B6B8 | 1 |
| 006ED63C | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006ED65F | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006ED682 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006ED6A5 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006ED6C8 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006ED6EB | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006ED70E | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006ED731 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006ED754 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006ED777 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006ED79A | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006ED7BD | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006ED7E0 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006ED803 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006ED826 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006ED849 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006ED86C | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006ED88F | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006ED8B2 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006ED8D5 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006ED92D | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006ED950 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006ED973 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006ED996 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006ED9B9 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006ED9DC | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006ED9FF | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EDA22 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EDA45 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EDA68 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EDA8B | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EDAA6 | Objekt | 0x00AF723C (Daten ab +0x20) | aus Objekt |
| 006EDABC | Objekt | 0x00B06CD8 (Daten ab +0x20) | aus Objekt |
| 006EDAD2 | Objekt | 0x00B07558 (Daten ab +0x20) | aus Objekt |
| 006EDAE8 | Objekt | 0x00B07FF0 (Daten ab +0x20) | aus Objekt |
| 006EDAFE | Objekt | 0x00B06BB4 (Daten ab +0x20) | aus Objekt |
| 006EDB14 | Objekt | 0x00B06A90 (Daten ab +0x20) | aus Objekt |
| 006EDB2A | Objekt | 0x00B0A088 (Daten ab +0x20) | aus Objekt |
| 006EDB40 | Objekt | 0x00B080D8 (Daten ab +0x20) | aus Objekt |
| 006EDB89 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EDBAC | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EDBCC | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EDBE3 | Puffer | 0x0089DCC0 | 1 |
| 006EDBFB | Puffer | 0x0089DCC4 | 1 |
| 006EDC13 | Puffer | 0x00AE6DE8 | 1 |
| 006EDC2B | Puffer | 0x00AE6DD4 | 1 |
| 006EDC42 | Spieler | 0x00C02550 (17 × 1000 Spieler) | 852000 je Block |
| 006EDC97 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EDCE3 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EDD2F | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EDD47 | Objekt | 0x00A6D348 (Daten ab +0x20) | aus Objekt |
| 006EDD5D | Objekt | 0x00A75968 (Daten ab +0x20) | aus Objekt |
| 006EDDA4 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EDDF5 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EDE18 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EDE61 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EDEB1 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EDF0B | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EDF2E | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EDF51 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EDF74 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EDF97 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EDFBA | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EDFDD | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EE000 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EE023 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EE046 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EE069 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EE08C | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EE0AF | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EE0D2 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EE0F7 | Puffer | 0x00B68EA8 | 1 |
| 006EE112 | Puffer | 0x00B628D8 | 1 |
| 006EE15C | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EE1A2 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EE1EB | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EE20E | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EE228 | Puffer | 0x008E1D88 | 1 |
| 006EE243 | Puffer | 0x008E0F78 | 1 |
| 006EE264 | Objekt | 0x008E91E0 (Daten ab +0x20) | aus Objekt |
| 006EE27A | Objekt | 0x008E8940 (Daten ab +0x20) | aus Objekt |
| 006EE290 | Objekt | 0x008E7C88 (Daten ab +0x20) | aus Objekt |
| 006EE2DF | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EE2FF | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EE322 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EE33A | Objekt | 0x01BA7488 (Daten ab +0x20) | aus Objekt |
| 006EE358 | Objekt | 0x01C51940 (Daten ab +0x20) | aus Objekt |
| 006EE36E | Objekt | 0x01C4BE78 (Daten ab +0x20) | aus Objekt |
| 006EE386 | Puffer | 0x01BAB640 | 1 |
| 006EE3A1 | Puffer | 0x01BAB498 | 1 |
| 006EE3EB | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EE40B | Objekt | 0x01C5C468 (Daten ab +0x20) | aus Objekt |
| 006EE421 | Objekt | 0x00B77338 (Daten ab +0x20) | aus Objekt |
| 006EE468 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EE480 | Objekt | 0x01C49278 (Daten ab +0x20) | aus Objekt |
| 006EE49E | Objekt | 0x01C54000 (Daten ab +0x20) | aus Objekt |
| 006EE4B4 | Objekt | 0x01C53EE8 (Daten ab +0x20) | aus Objekt |
| 006EE4CA | Objekt | 0x01C53D98 (Daten ab +0x20) | aus Objekt |
| 006EE4E0 | Objekt | 0x00BDE1A8 (Daten ab +0x20) | aus Objekt |
| 006EE524 | Puffer | variabel (ecx) | 1 |
| 006EE53E | Puffer | variabel (eax) | 1 |
| 006EE561 | Puffer | variabel (eax) | 1 |
| 006EE582 | Objekt | 0x01BA0438 (Daten ab +0x20) | aus Objekt |
| 006EE598 | Objekt | 0x00A2E420 (Daten ab +0x20) | aus Objekt |
| 006EE5AD | Puffer | 0x00B620EC | 1 |
| 006EE5DC | Objekt | 0x00BDEE80 (Daten ab +0x20) | aus Objekt |
| 006EE5EF | Objekt | 0x00BDED80 (Daten ab +0x20) | aus Objekt |
| 006EE605 | Objekt | 0x01C44370 (Daten ab +0x20) | aus Objekt |
| 006EE63E | Puffer | variabel (edx) | 1 |
| 006EE657 | Objekt | 0x00A2E0D8 (Daten ab +0x20) | aus Objekt |
| 006EE66F | Puffer | 0x01BA9F38 | 1 |
| 006EE688 | Objekt | 0x01C53B88 (Daten ab +0x20) | aus Objekt |
| 006EE69E | Objekt | 0x01C53A48 (Daten ab +0x20) | aus Objekt |
| 006EE6ED | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EE710 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EE728 | Objekt | 0x00A7C240 (Daten ab +0x20) | aus Objekt |
| 006EE746 | Objekt | 0x01BA07C0 (Daten ab +0x20) | aus Objekt |
| 006EE75C | Objekt | 0x00AE5B18 (Daten ab +0x20) | aus Objekt |
| 006EE773 | Puffer | variabel (edx) | 1 |
| 006EE7D4 | Puffer | variabel (edx) | 1 |
| 006EE7ED | Objekt | 0x01BAA1E0 (Daten ab +0x20) | aus Objekt |
| 006EE805 | Puffer | 0x01B9FFC8 | 1 |
| 006EE831 | Puffer | 0x01C53CC8 | 1 |
| 006EE852 | Objekt | 0x00B9F8F8 (Daten ab +0x20) | aus Objekt |
| 006EE899 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EE8BC | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EE8D4 | Objekt | 0x01C65E88 (Daten ab +0x20) | aus Objekt |
| 006EE8EA | Objekt | 0x01C645D8 (Daten ab +0x20) | aus Objekt |
| 006EE900 | Objekt | 0x01C68450 (Daten ab +0x20) | aus Objekt |
| 006EE91E | Objekt | 0x008BE408 (Daten ab +0x20) | aus Objekt |
| 006EE965 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EE9AE | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EEA44 | Objekt | variabel ([edx+eax+01A2C2F8h]) | aus Objekt |
| 006EEA66 | Objekt | 0x008EF338 (Daten ab +0x20) | aus Objekt |
| 006EEAC0 | Objekt | variabel (dword ptr [ebp+FFFFFF2Ch]) | aus Objekt |
| 006EEAD5 | Objekt | 0x00B9F6A8 (Daten ab +0x20) | aus Objekt |
| 006EEAEB | Objekt | 0x01BAF6F0 (Daten ab +0x20) | aus Objekt |
| 006EEB01 | Objekt | 0x01C46F48 (Daten ab +0x20) | aus Objekt |
| 006EEB17 | Objekt | 0x01C45838 (Daten ab +0x20) | aus Objekt |
| 006EEB2D | Objekt | 0x01C449F8 (Daten ab +0x20) | aus Objekt |
| 006EEB43 | Objekt | 0x01C44700 (Daten ab +0x20) | aus Objekt |
| 006EEB59 | Objekt | 0x008EABE8 (Daten ab +0x20) | aus Objekt |
| 006EEB6F | Objekt | 0x00A3B640 (Daten ab +0x20) | aus Objekt |
| 006EEB85 | Objekt | 0x00B9F028 (Daten ab +0x20) | aus Objekt |
| 006EEB9B | Objekt | 0x01C1E4C8 (Daten ab +0x20) | aus Objekt |

Bekannt: Puffer 0x00B0B6B8 (82 340 Byte) enthält die Titeltabellen der Trophäenhalle, siehe `feldkarte-verein.md`.
