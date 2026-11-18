"""Assemble the seven blocks of the patches 'presse-<text>' in a3patch.py and print old and new bytes as hex.

K12 of docs/korrekturliste-meldungen.md (see docs/befund-meldungen.md section 4): seven newspaper headlines pass a
deduction for the "Presse" part of the player's motivation (flag 0x100) without a player number, so the newspaper never
applies it, and - unlike the sister headlines of the same routines (e.g. 1218 at 0x005FE6D9) - the call sites do not
apply it themselves. New in every block: push <value> / mov ecx,<player> / call 0x00700FA2 right after the headline.
Room for these 10 bytes, everything else unchanged in effect:
  - "add esp,n" after cdecl calls dropped (all four routines end with mov esp,ebp and address locals through ebp),
  - "mov reg,[ebp+x] / push reg" -> "push dword [ebp+x]",
  - "mov reg16,[ebp+x] / push reg32" -> "push dword [ebp+x]" (the callee reads the low word only),
  - "movsx reg,ax / cmp reg,imm8" -> "cmp ax,imm8", "movsx eax,ax / test eax,eax" -> "test ax,ax".
Usage: python tools/asm_presse.py [path of the original anstoss3.exe]
"""
import sys

T = {'PRESSE32': 0x00700FA2, 'NAME32': 0x006FEB4D, 'NEWS32': 0x00789C32}
PRESSE = lambda value, player: [
    (None, '6A%02X' % (value & 0xFF), None),      # push value
    (None, '8B4D%02X' % player, None),            # mov ecx,[ebp+player]
    (None, 'E8', 'PRESSE32'),                     # call 00700FA2                 "Presse" + value (new)
]

BLOCKS = {
    # 1125 "Frau von %1 bei Banküberfall erwischt" (0x005FB264, player [ebp+0Ch], club [ebp+8]), value -3
    'presse-1125': (0x005FB53A, 0x005FB59D, dict(T, P7011F1='', ), [
        *PRESSE(-3, 0x0C),                        # was: add esp,1Ch
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F7011F1_32'),               # call 007011F1
        (None, '6689458E', None),                 # mov [ebp-72h],ax
        (None, '6A00', None),                     # push 0
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F701210_32'),               # call 00701210
        (None, '668945FE', None),                 # mov [ebp-2],ax
        (None, '6A00', None),                     # push 0
        (None, '6AFB', None),                     # push -5
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F701210_32'),               # call 00701210
        (None, '50', None),                       # push eax
        (None, '668B55FE', None),                 # mov dx,[ebp-2]
        (None, '52', None),                       # push edx
        (None, '6A03', None),                     # push 3
        (None, '6AFB', None),                     # push -5
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F7010D9_32'),               # call 007010D9
        (None, '50', None),                       # push eax
        (None, 'FF758E', None),                   # push dword [ebp-72h]          was: mov ax,[ebp-72h] / push eax
        (None, '6A02', None),                     # push 2
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F70173F_32'),               # call 0070173F
        (None, '50', None),                       # push eax
        (None, 'FF750C', None),                   # push dword [ebp+0Ch]          was: mov ecx / push ecx
        (None, '6864040000', None),               # push 464h                     message 1124
        (None, '6A60', None),                     # push 60h
        (None, 'FF7508', None),                   # push dword [ebp+8]            was: mov edx / push edx
        (None, 'E8', 'F6015FE_32'),               # call 006015FE                 (add esp,30h dropped)
    ]),
    # 1188 "Schönheitsoperation bei %1" (0x005FD59D, player [ebp+8], club [ebp+0Ch]), value -4
    'presse-1188': (0x005FDF3D, 0x005FDFA3, dict(T, END=0x005FDFA3), [
        (None, '6683F80A', None),                 # cmp ax,0Ah                    was: movsx edx,ax / cmp edx,0Ah
        (None, '7E', 'END'),                      # jle 005FDFA3
        (None, 'FF750C', None),                   # push dword [ebp+0Ch]          was: mov eax / push eax
        (None, 'E8', 'F775F0A_32'),               # call 00775F0A                 (add esp,4 dropped)
        (None, '6683F802', None),                 # cmp ax,2                      was: movsx ecx,ax / cmp ecx,2
        (None, '7E', 'END'),                      # jle 005FDFA3
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F69947B_32'),               # call 0069947B
        (None, '85C0', None),                     # test eax,eax
        (None, '74', 'END'),                      # je 005FDFA3
        (None, '6AFC', None),                     # push -4
        (None, '6A00', None),                     # push 0
        (None, '8B4D08', None),                   # mov ecx,[ebp+8]
        (None, 'E8', 'NAME32'),                   # call 006FEB4D
        (None, '50', None),                       # push eax
        (None, '6800010000', None),               # push 100h
        (None, '6A01', None),                     # push 1
        (None, '68A4040000', None),               # push 4A4h                     headline 1188
        (None, '6A06', None),                     # push 6
        (None, 'E8', 'NEWS32'),                   # call 00789C32                 (add esp,18h dropped)
        *PRESSE(-4, 0x08),
        (None, '6A00', None),                     # push 0
        (None, '6A00', None),                     # push 0
        (None, '8B5508', None),                   # mov edx,[ebp+8]
        (None, '52', None),                       # push edx
        (None, '68A3040000', None),               # push 4A3h                     message 1187
        (None, '6A60', None),                     # push 60h
        (None, '8B450C', None),                   # mov eax,[ebp+0Ch]
        (None, '50', None),                       # push eax
        (None, 'E8', 'F600F2F_32'),               # call 00600F2F
        (None, '83C418', None),                   # add esp,18h
    ]),
    # 1197 "%1 steht vor dem Nichts" (0x005FD59D, player [ebp+8], club [ebp+0Ch]), value -3
    'presse-1197': (0x005FE0EE, 0x005FE12A, dict(T), [
        *PRESSE(-3, 0x08),                        # was: add esp,1Ch
        (None, '8B4D08', None),                   # mov ecx,[ebp+8]
        (None, 'E8', 'F701328_32'),               # call 00701328
        (None, '66894596', None),                 # mov [ebp-6Ah],ax
        (None, '6A00', None),                     # push 0
        (None, '6AF6', None),                     # push -10
        (None, '8B4D08', None),                   # mov ecx,[ebp+8]
        (None, 'E8', 'F701210_32'),               # call 00701210
        (None, '50', None),                       # push eax
        (None, 'FF7596', None),                   # push dword [ebp-6Ah]          was: mov cx,[ebp-6Ah] / push ecx
        (None, '6A03', None),                     # push 3
        (None, '6A00', None),                     # push 0
        (None, 'FF7508', None),                   # push dword [ebp+8]            was: mov edx / push edx
        (None, '68AC040000', None),               # push 4ACh                     message 1196
        (None, '6A60', None),                     # push 60h
        (None, 'FF750C', None),                   # push dword [ebp+0Ch]          was: mov eax / push eax
        (None, 'E8', 'F601043_32'),               # call 00601043                 (add esp,24h dropped)
    ]),
    # 1201 "%1 geht lieber Golfen" (0x005FD59D, player [ebp+8], club [ebp+0Ch]), value -2
    'presse-1201': (0x005FE23E, 0x005FE298, dict(T, END=0x005FE298), [
        (None, 'FF750C', None),                   # push dword [ebp+0Ch]          was: mov eax / push eax
        (None, 'E8', 'F692744_32'),               # call 00692744                 (add esp,4 dropped)
        (None, '6683F80A', None),                 # cmp ax,0Ah                    was: movsx ecx,ax / cmp ecx,0Ah
        (None, '7E', 'END'),                      # jle 005FE298
        (None, '8B5508', None),                   # mov edx,[ebp+8]
        (None, '33C0', None),                     # xor eax,eax
        (None, '8A4254', None),                   # mov al,[edx+54h]
        (None, '85C0', None),                     # test eax,eax
        (None, '75', 'END'),                      # jne 005FE298
        (None, '6A13', None),                     # push 13h
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, '51', None),                       # push ecx
        (None, '8D5598', None),                   # lea edx,[ebp-68h]
        (None, '52', None),                       # push edx
        (None, 'E8', 'F732F44_32'),               # call 00732F44                 (add esp,0Ch dropped)
        (None, '6AFE', None),                     # push -2
        (None, '68E226A300', None),               # push 0A326E2h
        (None, '6A00', None),                     # push 0
        (None, '8B4D08', None),                   # mov ecx,[ebp+8]
        (None, 'E8', 'NAME32'),                   # call 006FEB4D
        (None, '50', None),                       # push eax
        (None, '6800010000', None),               # push 100h
        (None, '6A02', None),                     # push 2
        (None, '68B1040000', None),               # push 4B1h                     headline 1201
        (None, '6A05', None),                     # push 5
        (None, 'E8', 'NEWS32'),                   # call 00789C32                 (add esp,1Ch dropped)
        *PRESSE(-2, 0x08),
    ]),
    # 1269 "%1 pöbelt friedliche Passanten an" (0x005E08F1, manager [ebp+8], club [ebp+0Ch], player [ebp+10h]), -4
    'presse-1269': (0x005E0F0D, 0x005E0F63, dict(T, END=0x005E0F63), [
        (None, '6685C0', None),                   # test ax,ax                    was: movsx eax,ax / test eax,eax
        (None, '75', 'END'),                      # jne 005E0F63
        (None, '6AFC', None),                     # push -4
        (None, '8B4D08', None),                   # mov ecx,[ebp+8]
        (None, '83C10A', None),                   # add ecx,0Ah
        (None, '51', None),                       # push ecx
        (None, '6A00', None),                     # push 0
        (None, '8B4D10', None),                   # mov ecx,[ebp+10h]
        (None, 'E8', 'NAME32'),                   # call 006FEB4D
        (None, '50', None),                       # push eax
        (None, '6800010000', None),               # push 100h
        (None, '6A02', None),                     # push 2
        (None, '68F5040000', None),               # push 4F5h                     headline 1269
        (None, '6A07', None),                     # push 7
        (None, 'E8', 'NEWS32'),                   # call 00789C32                 (add esp,1Ch dropped)
        *PRESSE(-4, 0x10),
        (None, '6A02', None),                     # push 2
        (None, '8B4D10', None),                   # mov ecx,[ebp+10h]
        (None, 'E8', 'F702D95_32'),               # call 00702D95
        (None, '6A02', None),                     # push 2
        (None, 'FF7510', None),                   # push dword [ebp+10h]          was: mov edx / push edx
        (None, '68F4040000', None),               # push 4F4h                     question 1268
        (None, 'FF750C', None),                   # push dword [ebp+0Ch]          was: mov eax / push eax
        (None, 'FF7508', None),                   # push dword [ebp+8]            was: mov ecx / push ecx
        (None, 'E8', 'F5F29BC_32'),               # call 005F29BC                 (add esp,14h dropped)
    ]),
    # 1528 "%1 mit schweren Vorwürfen gegen den Trainer" (0x005E5A60 ff., same arguments as 1269), value -4
    'presse-1528': (0x005E5BDD, 0x005E5C2F, dict(T, END=0x005E5C2F), [
        (None, '6683F850', None),                 # cmp ax,50h                    was: movsx ecx,ax / cmp ecx,50h
        (None, '7D', 'END'),                      # jge 005E5C2F
        (None, '6AFC', None),                     # push -4
        (None, '8B5508', None),                   # mov edx,[ebp+8]
        (None, '83C20A', None),                   # add edx,0Ah
        (None, '52', None),                       # push edx
        (None, '6A00', None),                     # push 0
        (None, '8B4D10', None),                   # mov ecx,[ebp+10h]
        (None, 'E8', 'NAME32'),                   # call 006FEB4D
        (None, '50', None),                       # push eax
        (None, '6800010000', None),               # push 100h
        (None, '6A02', None),                     # push 2
        (None, '68F8050000', None),               # push 5F8h                     headline 1528
        (None, '6A08', None),                     # push 8
        (None, 'E8', 'NEWS32'),                   # call 00789C32                 (add esp,1Ch dropped)
        *PRESSE(-4, 0x10),
        (None, '6A00', None),                     # push 0
        (None, '8B4508', None),                   # mov eax,[ebp+8]
        (None, '83C00A', None),                   # add eax,0Ah
        (None, '50', None),                       # push eax
        (None, 'FF7510', None),                   # push dword [ebp+10h]          was: mov ecx / push ecx
        (None, '68F7050000', None),               # push 5F7h                     message 1527
        (None, '6A60', None),                     # push 60h
        (None, 'FF750C', None),                   # push dword [ebp+0Ch]          was: mov edx / push edx
        (None, 'E8', 'F600F2F_32'),               # call 00600F2F                 (add esp,18h dropped)
    ]),
    # 1530 "%1 kritisiert Trainer %2" (same routine), value -4
    'presse-1530': (0x005E5D03, 0x005E5D55, dict(T, END=0x005E5D55), [
        (None, '6683F850', None),                 # cmp ax,50h                    was: movsx ecx,ax / cmp ecx,50h
        (None, '7D', 'END'),                      # jge 005E5D55
        (None, '6AFC', None),                     # push -4
        (None, '8B5508', None),                   # mov edx,[ebp+8]
        (None, '83C20A', None),                   # add edx,0Ah
        (None, '52', None),                       # push edx
        (None, '6A00', None),                     # push 0
        (None, '8B4D10', None),                   # mov ecx,[ebp+10h]
        (None, 'E8', 'NAME32'),                   # call 006FEB4D
        (None, '50', None),                       # push eax
        (None, '6800010000', None),               # push 100h
        (None, '6A02', None),                     # push 2
        (None, '68FA050000', None),               # push 5FAh                     headline 1530
        (None, '6A08', None),                     # push 8
        (None, 'E8', 'NEWS32'),                   # call 00789C32                 (add esp,1Ch dropped)
        *PRESSE(-4, 0x10),
        (None, '6A00', None),                     # push 0
        (None, '8B4508', None),                   # mov eax,[ebp+8]
        (None, '83C00A', None),                   # add eax,0Ah
        (None, '50', None),                       # push eax
        (None, 'FF7510', None),                   # push dword [ebp+10h]          was: mov ecx / push ecx
        (None, '68F9050000', None),               # push 5F9h                     message 1529
        (None, '6A60', None),                     # push 60h
        (None, 'FF750C', None),                   # push dword [ebp+0Ch]          was: mov edx / push edx
        (None, 'E8', 'F600F2F_32'),               # call 00600F2F                 (add esp,18h dropped)
    ]),
}


def assemble(name):
    start, end, targets, code = BLOCKS[name]
    size = lambda h, t: len(h) // 2 + (0 if t is None else 4 if t.endswith('32') else 1)
    addr, pos = dict(targets), start
    for label, h, t in code:
        if label:
            addr[label] = pos
        if t and t.startswith('F') and t.endswith('_32'):
            addr[t] = int(t[1:-3], 16)            # 'F701210_32' = call target 0x00701210
        pos += size(h, t)
    out, pos = bytearray(), start
    for label, h, t in code:
        out += bytes.fromhex(h)
        pos += size(h, t)
        if t:
            d = addr[t] - pos
            if t.endswith('32'):
                out += d.to_bytes(4, 'little', signed=True)
            else:
                assert -128 <= d <= 127, (t, d)
                out += d.to_bytes(1, 'little', signed=True)
    used = len(out)
    assert used <= end - start, (name, used, end - start)
    return bytes(out) + b'\x90' * (end - start - used), used


if __name__ == '__main__':
    exe = open(sys.argv[1], 'rb').read() if len(sys.argv) > 1 else None
    for name in BLOCKS:
        code, used = assemble(name)
        start = BLOCKS[name][0]
        print(f'{name}: VA 0x{start:08X}, Datei-Offset 0x{start - 0x400000:08X}, {used} Byte Code, '
              f'{len(code) - used} Byte aufgefüllt, zusammen {len(code)}')
        if exe:
            print('  alt', exe[start - 0x400000:start - 0x400000 + len(code)].hex().upper())
        print('  neu', code.hex().upper())
