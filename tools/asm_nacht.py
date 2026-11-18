"""Assemble further in-place rewrites for the points of docs/korrekturliste-meldungen.md worked through on 17./18.11.2026
and print old and new bytes. Same table format and rules as tools/asm_presse.py (labels, 'Fxxxxxx_32' = call target).
Usage: python tools/asm_nacht.py [path of the original anstoss3.exe] [block name]
"""
import sys
import asm_presse

BLOCKS = {
    # K15, text 1083 "... Es kommt zur Trennung." (0x005F9ED7, case 1; club [ebp+8], player [ebp+0Ch]): the relationship
    # was not ended. New: 0x00702467 (end the relationship) as at the sister text 1079 (0x005F9816), name of the former
    # partner 0x0070185C afterwards as there. Room: add esp dropped (routine ends with mov esp,ebp), push forms.
    'trennung-1083': (0x005F9F76, 0x005F9FBD, {}, [
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F702467_32'),               # call 00702467                 end the relationship (new)
        (None, '6A0A', None),                     # push 0Ah
        (None, 'E8', 'F78A810_32'),               # call 0078A810                 random 0..9 (add esp,4 dropped)
        (None, '0FBFC8', None),                   # movsx ecx,ax
        (None, 'BAF6FFFFFF', None),               # mov edx,-10
        (None, '2BD1', None),                     # sub edx,ecx
        (None, '6A00', None),                     # push 0                        w4; only after the random call, whose
                                                  #                               argument stays on the stack below it
        (None, '52', None),                       # push edx
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F7010D9_32'),               # call 007010D9
        (None, '50', None),                       # push eax
        (None, 'FF75FC', None),                   # push dword [ebp-4]            was: mov ax,[ebp-4] / push eax
        (None, '6A02', None),                     # push 2
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F70185C_32'),               # call 0070185C                 name of the former partner (was 0070173F)
        (None, '50', None),                       # push eax
        (None, 'FF750C', None),                   # push dword [ebp+0Ch]          was: mov ecx / push ecx
        (None, '683B040000', None),               # push 43Bh                     message 1083
        (None, '6A60', None),                     # push 60h
        (None, 'FF7508', None),                   # push dword [ebp+8]            was: mov edx / push edx
        (None, 'E8', 'F601043_32'),               # call 00601043                 (add esp,24h dropped)
    ]),
    # K17, texts 1109 / 1110 (0x005FA6AC ff., club [ebp+8], player [ebp+0Ch]). 1109 ("... sagt künftig nur noch Schatzi")
    # called 0x00702762 (go back to the former partner) and 1110 ("... ist auf dem Weg zu ihr") changed nothing. New: 1109
    # sets the marker bit 25 that its own condition tests (0x007028D7; setter 0x007028F9 had no caller; 0x00702467 clears
    # it when a relationship ends), 1110 calls 0x00702762 after the message (the names are read before the change).
    'ex-1109': (0x005FAE76, 0x005FAEAB, {}, [
        (None, '6A01', None),                     # push 1
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F7028F9_32'),               # call 007028F9                 set the marker (was: call 00702762)
        (None, '6A00', None),                     # push 0
        (None, '6A00', None),                     # push 0
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F70185C_32'),               # call 0070185C                 %3 former partner
        (None, '50', None),                       # push eax
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F70173F_32'),               # call 0070173F                 %2 partner
        (None, '50', None),                       # push eax
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, '51', None),                       # push ecx
        (None, '6855040000', None),               # push 455h                     message 1109
        (None, '6A60', None),                     # push 60h
        (None, '8B5508', None),                   # mov edx,[ebp+8]
        (None, '52', None),                       # push edx
        (None, 'E8', 'F601166_32'),               # call 00601166                 (add esp,20h dropped)
    ]),
    'ex-1110': (0x005FAEDB, 0x005FAF19, {'END': 0x005FAF19}, [
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F702C12_32'),               # call 00702C12
        (None, '84C0', None),                     # test al,al                    was: and eax,0FFh / test eax,eax
        (None, '75', 'END'),                      # jne 005FAF19
        (None, '6A00', None),                     # push 0
        (None, '6A00', None),                     # push 0
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F70185C_32'),               # call 0070185C                 %3 former partner
        (None, '50', None),                       # push eax
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F70173F_32'),               # call 0070173F                 %2 partner
        (None, '50', None),                       # push eax
        (None, 'FF750C', None),                   # push dword [ebp+0Ch]          was: mov eax / push eax
        (None, '6856040000', None),               # push 456h                     message 1110
        (None, '6A60', None),                     # push 60h
        (None, 'FF7508', None),                   # push dword [ebp+8]            was: mov ecx / push ecx
        (None, 'E8', 'F601166_32'),               # call 00601166                 (add esp,20h dropped)
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F702762_32'),               # call 00702762                 back to the former partner (new here)
    ]),
    # 0x00702762 (only caller now 0x005FAEDB ff.): same steps as before without the repeated reloads, and at the end the
    # status "Freundin" (0x00702BB0(1)); before, the status stayed "no relationship" (set by 0x00702467 inside).
    'ex-702762': (0x00702762, 0x0070282A, {}, [
        (None, '55', None),                       # push ebp
        (None, '8BEC', None),                     # mov ebp,esp
        (None, '83EC0C', None),                   # sub esp,0Ch
        (None, '894DF4', None),                   # mov [ebp-0Ch],ecx             this
        (None, '0FBF01', None),                   # movsx eax,word [ecx]          player number
        (None, '69C054030000', None),             # imul eax,eax,354h
        (None, '8A90D527C000', None),             # mov dl,[eax+00C027D5h]        name index of the former partner
        (None, '8855FB', None),                   # mov [ebp-5],dl
        (None, '8A90D727C000', None),             # mov dl,[eax+00C027D7h]        her name group
        (None, '8855FA', None),                   # mov [ebp-6],dl
        (None, '8B90DC26C000', None),             # mov edx,[eax+00C026DCh]       her date
        (None, '8955FC', None),                   # mov [ebp-4],edx
        (None, 'E8', 'F702467_32'),               # call 00702467                 end the present relationship (ecx = this)
        (None, '8B4DF4', None),                   # mov ecx,[ebp-0Ch]
        (None, '0FBF01', None),                   # movsx eax,word [ecx]
        (None, '69C054030000', None),             # imul eax,eax,354h
        (None, '8A55FB', None),                   # mov dl,[ebp-5]
        (None, '8890D327C000', None),             # mov [eax+00C027D3h],dl        partner = former partner
        (None, '8A55FA', None),                   # mov dl,[ebp-6]
        (None, '8890D627C000', None),             # mov [eax+00C027D6h],dl
        (None, '8B55FC', None),                   # mov edx,[ebp-4]
        (None, '8990D826C000', None),             # mov [eax+00C026D8h],edx
        (None, '05C026C000', None),               # add eax,00C026C0h             address of the wedding date
        (None, '50', None),                       # push eax
        (None, '0FBF11', None),                   # movsx edx,word [ecx]
        (None, '52', None),                       # push edx
        (None, 'E8', 'F4377B7_32'),               # call 004377B7                 remove the date from the list
        (None, '83C408', None),                   # add esp,8
        (None, '8B4DF4', None),                   # mov ecx,[ebp-0Ch]
        (None, '0FBF01', None),                   # movsx eax,word [ecx]
        (None, '69C054030000', None),             # imul eax,eax,354h
        (None, 'C680C026C00000', None),           # mov byte [eax+00C026C0h],0
        (None, '6A01', None),                     # push 1
        (None, 'E8', 'F702BB0_32'),               # call 00702BB0                 status "Freundin" (new; ecx = this)
        (None, '8BE5', None),                     # mov esp,ebp
        (None, '5D', None),                       # pop ebp
        (None, 'C3', None),                       # ret
    ]),
    # K20, text 1172 "%1 veröffentlicht seine Autobiographie ... %2 und %3 mögen ihn jedenfalls jetzt nicht mehr" (0x005FD59D,
    # player [ebp+8] = author, club [ebp+0Ch]). 0x005EC9D8(club, author) draws two team-mates A, B who are not his arch
    # enemy; the quarrel was entered between A and B (A.0x00703DF4(B)). New: author with A and author with B.
    'autobio-1172': (0x005FDB07, 0x005FDB8C, {'END': 0x005FDBA9}, [
        (None, 'FF7508', None),                   # push dword [ebp+8]            was: mov edx / push edx
        (None, 'FF750C', None),                   # push dword [ebp+0Ch]          was: mov eax / push eax
        (None, 'E8', 'F5EC9D8_32'),               # call 005EC9D8                 (add esp,8 dropped)
        (None, '894590', None),                   # mov [ebp-70h],eax             A
        (None, 'FF7508', None),                   # push dword [ebp+8]
        (None, 'FF750C', None),                   # push dword [ebp+0Ch]
        (None, 'E8', 'F5EC9D8_32'),               # call 005EC9D8
        (None, '89458C', None),                   # mov [ebp-74h],eax             B
        (None, '837D9000', None),                 # cmp dword [ebp-70h],0
        (None, '74', 'SKIP'),                     # je SKIP
        (None, '837D8C00', None),                 # cmp dword [ebp-74h],0
        (None, '75', 'GO'),                       # jne GO
        ('SKIP', 'EB', 'END'),                    # jmp 005FDBA9
        ('GO', '8B4590', None),                   # mov eax,[ebp-70h]
        (None, '3B458C', None),                   # cmp eax,[ebp-74h]
        (None, '75', 'DO'),                       # jne DO
        (None, 'EB', 'END'),                      # jmp 005FDBA9                  the same player twice: nothing
        ('DO', 'FF7590', None),                   # push dword [ebp-70h]          A
        (None, '8B4D08', None),                   # mov ecx,[ebp+8]               author
        (None, 'E8', 'F703DF4_32'),               # call 00703DF4                 quarrel author - A (was A - B)
        (None, 'FF758C', None),                   # push dword [ebp-74h]          B
        (None, '8B4D08', None),                   # mov ecx,[ebp+8]
        (None, 'E8', 'F703DF4_32'),               # call 00703DF4                 quarrel author - B (new)
        (None, '6A00', None),                     # push 0
        (None, '6A00', None),                     # push 0
        (None, '8D9558FFFFFF', None),             # lea edx,[ebp-0A8h]
        (None, '52', None),                       # push edx
        (None, '8B4D8C', None),                   # mov ecx,[ebp-74h]
        (None, 'E8', 'F6FEB4D_32'),               # call 006FEB4D                 %3 name of B
        (None, '50', None),                       # push eax
        (None, '8D8524FFFFFF', None),             # lea eax,[ebp-0DCh]
        (None, '50', None),                       # push eax
        (None, '8B4D90', None),                   # mov ecx,[ebp-70h]
        (None, 'E8', 'F6FEB4D_32'),               # call 006FEB4D                 %2 name of A
        (None, '50', None),                       # push eax
        (None, 'FF7508', None),                   # push dword [ebp+8]            was: mov ecx / push ecx
        (None, '6894040000', None),               # push 494h                     message 1172
        (None, '6A60', None),                     # push 60h
        (None, 'FF750C', None),                   # push dword [ebp+0Ch]          was: mov edx / push edx
        (None, 'E8', 'F601166_32'),               # call 00601166
        (None, '83C420', None),                   # add esp,20h
    ]),
    # K28, text 1180 "... ist deshalb heute sehr müde und verliert einen Frischepunkt" (0x005FD59D, hobby case at
    # 0x005FDD89: random 0..1, 0 -> this message, 1 -> 0x005FDDCA). Only the message was shown. New: 0x005E5F40(-1) on the
    # player ([ebp+8]), the routine text 1329 "verliert fünf Frischepunkte" uses with -5 (0x005E2303).
    'frische-1180': (0x005FDD89, 0x005FDDCA, {'OTHER': 0x005FDDCA, 'END': 0x005FDE00}, [
        (None, '6A02', None),                     # push 2
        (None, 'E8', 'F78A810_32'),               # call 0078A810                 random 0..1 (add esp,4 dropped)
        (None, '8985FCFEFFFF', None),             # mov [ebp-104h],eax
        (None, '85C0', None),                     # test eax,eax                  was: cmp [ebp-104h],0 / 1 with three jumps
        (None, '75', 'OTHER'),                    # jne 005FDDCA
        (None, '6AFF', None),                     # push -1
        (None, '8B4D08', None),                   # mov ecx,[ebp+8]
        (None, 'E8', 'F5E5F40_32'),               # call 005E5F40                 freshness - 1 (new)
        (None, '6A00', None),                     # push 0
        (None, '6A00', None),                     # push 0
        (None, 'FF7508', None),                   # push dword [ebp+8]            was: mov edx / push edx
        (None, '689C040000', None),               # push 49Ch                     message 1180
        (None, '6A60', None),                     # push 60h
        (None, 'FF750C', None),                   # push dword [ebp+0Ch]          was: mov eax / push eax
        (None, 'E8', 'F600F2F_32'),               # call 00600F2F                 (add esp,18h dropped)
        (None, 'EB', 'END'),                      # jmp 005FDE00
    ]),
    # K33, text 983 "... %1 teilt Ihnen danach mit, daß er Ihnen ab jetzt nichts mehr sagen wird" (0x005E4EC2, club [ebp+8],
    # spy [ebp+0Ch]): the whole squad gets -10 on the trainer part, the spy gets bit 0x20000 and team part 0, but the spy
    # bit 0x8000 stayed, so he was drawn as spy again. New: 0x0070020F(0) clears it. The loop is written shorter.
    'spitzel-983': (0x005E4F10, 0x005E4F7C, {}, [
        (None, '66C745F60000', None),             # mov word [ebp-0Ah],0
        (None, 'EB', 'CHECK'),                    # jmp CHECK
        ('NEXT', '66FF45F6', None),               # inc word [ebp-0Ah]            was: mov ax / add ax,1 / mov
        ('CHECK', '8B5508', None),                # mov edx,[ebp+8]
        (None, '0FBF4DF6', None),                 # movsx ecx,word [ebp-0Ah]
        (None, '663B8AE2000000', None),           # cmp cx,[edx+0E2h]             squad size
        (None, '7D', 'DONE'),                     # jge DONE
        (None, '6AF6', None),                     # push -10
        (None, '8B8C8A500B0000', None),           # mov ecx,[edx+ecx*4+0B50h]
        (None, 'E8', 'F7007A1_32'),               # call 007007A1                 trainer part - 10
        (None, 'EB', 'NEXT'),                     # jmp NEXT
        ('DONE', '6A01', None),                   # push 1
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F70031F_32'),               # call 0070031F                 bit 0x20000
        (None, '6A00', None),                     # push 0
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F700BCF_32'),               # call 00700BCF                 team part = 0
        (None, '6A00', None),                     # push 0
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F70020F_32'),               # call 0070020F                 clear the spy bit 0x8000 (new)
        (None, '6A00', None),                     # push 0
        (None, '6A00', None),                     # push 0
        (None, 'FF750C', None),                   # push dword [ebp+0Ch]          was: mov eax / push eax
        (None, '68D7030000', None),               # push 3D7h                     message 983
        (None, '6A60', None),                     # push 60h
        (None, 'FF7508', None),                   # push dword [ebp+8]            was: mov ecx / push ecx
        (None, 'E8', 'F600F2F_32'),               # call 00600F2F                 (add esp,18h dropped)
    ]),
    # K40 (part), texts 1176 / 1177 "%2, die Frau Ihres Spielers %1 möchte unbedingt, daß ihr erstes / nächstes Kind ..."
    # (0x005FD59D, player [ebp+8], club [ebp+0Ch]; the case requires flag bit 24, which exists only with a partner):
    # 0 was passed as %2. New: name of the partner (0x0070173F). The two branches (no child yet -> 1176, else 1177) are
    # merged: text number = 498h + (number of children != 0).
    'frau-1176-1177': (0x005FDC9C, 0x005FDCE3, {}, [
        (None, '6A00', None),                     # push 0                        w
        (None, '8B4D08', None),                   # mov ecx,[ebp+8]
        (None, 'E8', 'F70173F_32'),               # call 0070173F                 name of the partner (new)
        (None, '50', None),                       # push eax                      %2
        (None, 'FF7508', None),                   # push dword [ebp+8]            player
        (None, '8B4D08', None),                   # mov ecx,[ebp+8]
        (None, 'E8', 'F6FFD8A_32'),               # call 006FFD8A                 number of children
        (None, '6685C0', None),                   # test ax,ax
        (None, '0F95C0', None),                   # setne al
        (None, '0FB6C0', None),                   # movzx eax,al
        (None, '0598040000', None),               # add eax,498h                  1176 or 1177
        (None, '50', None),                       # push eax
        (None, '6A60', None),                     # push 60h
        (None, 'FF750C', None),                   # push dword [ebp+0Ch]
        (None, 'E8', 'F600F2F_32'),               # call 00600F2F
    ]),
    # K18, text 1115 "%s, die Frau von %s ist zusammen mit dem gemeinsamen Kind zu ihrem neuen Freund gezogen. Er ... verliert
    # einen Punkt seiner Spielstärke" (0x005FB264 case 1, club [ebp+8], player [ebp+0Ch]). The case required strength
    # (byte player +2) == 1 and only lowered savegame 0x273. The sister texts with a lost strength point require
    # strength > 1 and subtract 1 directly (1163 at 0x005FD891 ff., 367 at 0x00604FA8 ff.). New: strength > 1,
    # strength - 1, 0x00702467 (end the relationship; clears the child list, the wife becomes the former partner, whose
    # name the message already read). Room: shorter compares, push forms, add esp dropped.
    'frau-weg-1115': (0x005FB2F5, 0x005FB371, {'END': 0x005FB371}, [
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, '80790201', None),                 # cmp byte [ecx+2],1            strength
        (None, '7E', 'END'),                      # jle END                       was: jne (== 1 required)
        (None, 'E8', 'F6FFB14_32'),               # call 006FFB14                 married
        (None, '85C0', None),                     # test eax,eax
        (None, '74', 'END'),                      # je END
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F6FFD8A_32'),               # call 006FFD8A                 number of children
        (None, '6683F801', None),                 # cmp ax,1                      was: movsx eax,ax / cmp eax,1
        (None, '75', 'END'),                      # jne END
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F7011F1_32'),               # call 007011F1                 part value 0x273 before
        (None, '6689458E', None),                 # mov [ebp-72h],ax
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'FE4902', None),                   # dec byte [ecx+2]              strength - 1 (new)
        (None, 'E8', 'F702467_32'),               # call 00702467                 end the relationship (new; ecx = player)
        (None, '6A0B', None),                     # push 0Bh
        (None, 'E8', 'F78A810_32'),               # call 0078A810                 random 0..10 (add esp,4 dropped)
        (None, '0FBFC8', None),                   # movsx ecx,ax
        (None, 'BAD8FFFFFF', None),               # mov edx,-40
        (None, '2BD1', None),                     # sub edx,ecx
        (None, '6A00', None),                     # push 0                        w4 (after the random call)
        (None, '52', None),                       # push edx
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F7010D9_32'),               # call 007010D9                 part value 0x273 - 40..50
        (None, '50', None),                       # push eax                      w3 after
        (None, 'FF758E', None),                   # push dword [ebp-72h]          w2 before (was: mov ax / push eax)
        (None, '6A02', None),                     # push 2                        w1 kind
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F70185C_32'),               # call 0070185C                 name of the former partner = the wife
        (None, '50', None),                       # push eax
        (None, 'FF750C', None),                   # push dword [ebp+0Ch]
        (None, '685B040000', None),               # push 45Bh                     message 1115
        (None, '6A60', None),                     # push 60h
        (None, 'FF7508', None),                   # push dword [ebp+8]
        (None, 'E8', 'F601043_32'),               # call 00601043                 (add esp,24h dropped)
    ]),
    # K31, driving-licence counter (byte savegame 0x26E = static record +0x28E, 0x00C027DE + nr * 0x354). The setter/reader
    # 0x00702D31(v) stored "months left" (1, 2 or 6) and nothing ever counted it down. The daily routines are not run on
    # every day (0x0064F981: events only with 2 of 3 per club and day), so nothing is counted. New meaning of the byte: 0 =
    # licence present, otherwise the month of expiry E = (year * 12 + month + v) & 0xFF (today: words 0x00B5CBDE year,
    # 0x00B5CBDC month, as 0x0067582A reads them). Every read checks (E - today) & 0xFF: 0..7 = still withdrawn, anything
    # else = expired -> the byte is cleared. v > 0 stores E (a result of 0 becomes 1), v = 0 clears, v < 0 only reads.
    # Returns 0 or a positive value, as all callers only test the sign/zero (0x005FC744 ... 0x005FEB6B). Old savegames
    # hold 1, 2 or 6, which count as expired at the first read.
    'fuehrerschein-zaehler': (0x00702D31, 0x00702D95, {}, [
        (None, '0FBF01', None),                   # movsx eax,word [ecx]          player number
        (None, '69C054030000', None),             # imul eax,eax,354h
        (None, '8D88DE27C000', None),             # lea ecx,[eax+00C027DEh]       -> the byte
        (None, '0FB715DECBB500', None),           # movzx edx,word [00B5CBDEh]    year
        (None, '6BD20C', None),                   # imul edx,edx,0Ch
        (None, '0215DCCBB500', None),             # add dl,[00B5CBDCh]            + month: dl = today in months
        (None, '8B442404', None),                 # mov eax,[esp+4]               v
        (None, '6685C0', None),                   # test ax,ax
        (None, '78', 'READ'),                     # js READ                       v < 0: read only
        (None, '74', 'STORE'),                    # jz STORE                      v = 0: clear
        (None, '00D0', None),                     # add al,dl                     month of expiry
        (None, '75', 'STORE'),                    # jnz STORE
        (None, '40', None),                       # inc eax                       0 is reserved for "licence present"
        ('STORE', '8801', None),                  # mov [ecx],al
        ('READ', '0FB601', None),                 # movzx eax,byte [ecx]
        (None, '85C0', None),                     # test eax,eax
        (None, '74', 'RET'),                      # jz RET
        (None, '28D0', None),                     # sub al,dl                     months until expiry
        (None, '3C07', None),                     # cmp al,7
        (None, '76', 'OK'),                       # jbe OK
        (None, 'C60100', None),                   # mov byte [ecx],0              expired
        (None, '33C0', None),                     # xor eax,eax
        (None, 'C20400', None),                   # ret 4
        ('OK', '40', None),                       # inc eax                       1..8
        ('RET', 'C20400', None),                  # ret 4
        # reader "licence present?" (was at 0x00702D6F; its two callers 0x005FE9B4 and 0x005FEB2E are redirected)
        ('READER', '6AFF', None),                 # push -1
        (None, 'E8', 'F702D31_32'),               # call 00702D31                 ecx = this
        (None, 'F7D8', None),                     # neg eax
        (None, '1BC0', None),                     # sbb eax,eax
        (None, '40', None),                       # inc eax                       1 = present, 0 = withdrawn
        (None, 'C3', None),                       # ret
    ]),
    # K32, text 1565 "... hat sein Abitur mit sehr guten Noten bestanden" (0x005F9B90 case 5, club [ebp+8], player [ebp+0Ch];
    # only in June). The pre-routine 0x005F9D6D excludes pupils with marker 3 (0x007064F6 at 0x005F9DD0), but nothing ever
    # set 3. New: 0x0070654A(3) before the message. Needs K38 (marker moved to bits 5-6), otherwise 3 would also set the
    # group-leader bit. The default target 0x005F9D52 (xor ax,ax) stays where it is.
    'abitur-1565': (0x005F9D1F, 0x005F9D52, {'END': 0x005F9D55}, [
        (None, '66833DDCCBB50006', None),         # cmp word [00B5CBDCh],6        month = June?
        (None, '75', 'ONE'),                      # jne ONE
        (None, '6A03', None),                     # push 3
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F70654A_32'),               # call 0070654A                 pupil marker = 3 "school finished" (new)
        (None, '6A00', None),                     # push 0
        (None, '6A00', None),                     # push 0
        (None, 'FF750C', None),                   # push dword [ebp+0Ch]
        (None, '681D060000', None),               # push 61Dh                     message 1565
        (None, '6A60', None),                     # push 60h
        (None, 'FF7508', None),                   # push dword [ebp+8]
        (None, 'E8', 'F600F2F_32'),               # call 00600F2F                 (add esp,18h dropped)
        ('ONE', '66B80100', None),                # mov ax,1
        (None, 'EB', 'END'),                      # jmp 005F9D55
    ]),
    # K35, texts 1358 / 1359 "... erhält einen Konditionsbonus von 5%" (private trainer): the event only sets / clears bit 13
    # of the flag word (0x00700105), and the condition routine 0x00457E00 (player word +0x16 / 100, minus 5 for smokers,
    # bit 11, at least 0; the smoker text 1356 calls its 5 points "Konditionshandicap von 5%") never read it. New: plus 5
    # for bit 13 (0x007000E3), at most 100 (the stored value is limited to 10000). 65 of 80 bytes (71 + 9 int3).
    'konditionsbonus': (0x00457E00, 0x00457E50, {}, [
        (None, '51', None),                       # push ecx                      this
        (None, '0FBF4116', None),                 # movsx eax,word [ecx+16h]
        (None, '99', None),                       # cdq
        (None, 'B964000000', None),               # mov ecx,64h
        (None, 'F7F9', None),                     # idiv ecx                      condition 0..100
        (None, '50', None),                       # push eax
        (None, '8B4C2404', None),                 # mov ecx,[esp+4]
        (None, 'E8', 'F6FFFD9_32'),               # call 006FFFD9                 smoker?
        (None, '85C0', None),                     # test eax,eax
        (None, '58', None),                       # pop eax                       (flags stay)
        (None, '74', 'BONUS'),                    # jz BONUS
        (None, '83E805', None),                   # sub eax,5
        (None, '79', 'BONUS'),                    # jns BONUS
        (None, '33C0', None),                     # xor eax,eax                   at least 0
        ('BONUS', '50', None),                    # push eax
        (None, '8B4C2404', None),                 # mov ecx,[esp+4]
        (None, 'E8', 'F7000E3_32'),               # call 007000E3                 private trainer? (new)
        (None, '85C0', None),                     # test eax,eax
        (None, '58', None),                       # pop eax
        (None, '59', None),                       # pop ecx                       drop this
        (None, '74', 'RET'),                      # jz RET
        (None, '83C005', None),                   # add eax,5
        (None, '83F864', None),                   # cmp eax,64h
        (None, '7E', 'RET'),                      # jle RET
        (None, 'B864000000', None),               # mov eax,64h                   at most 100
        ('RET', 'C3', None),                      # ret
    ]),
    # K36, text 1342 "... beschließt, seine Karriere als Fußballprofi zu beenden" (0x005E2152 case at 0x005E26B9, club
    # [ebp+0Ch], player [ebp+10h]): only the firm state went from 5 to 6, the player stayed. New: 0x0070E29E(player, club)
    # after the message, as text 338 does (0x00604132) and text 716 in the same daily dispatcher (0x006A71CF). The wrapper
    # 0x005E2BB9 and the dispatcher (0x005EFEA4) do not touch the player afterwards. Room: cmp al, push forms, add esp
    # dropped; the club for 0x0070E29E is the first argument of 0x00600F2F still on the stack (that routine only reads its
    # [ebp+8], 0x00601016).
    'karriereende-1342': (0x005E26B9, 0x005E26EE, {'END': 0x005E26EE}, [
        (None, '8B4D10', None),                   # mov ecx,[ebp+10h]
        (None, 'E8', 'F70324F_32'),               # call 0070324F                 firm state
        (None, '3C05', None),                     # cmp al,5                      was: movsx edx,ax / cmp edx,5
        (None, '75', 'END'),                      # jne END
        (None, '6A06', None),                     # push 6
        (None, '8B4D10', None),                   # mov ecx,[ebp+10h]
        (None, 'E8', 'F703276_32'),               # call 00703276                 firm state = 6
        (None, '6A00', None),                     # push 0
        (None, '6A00', None),                     # push 0
        (None, 'FF7510', None),                   # push dword [ebp+10h]
        (None, '683E050000', None),               # push 53Eh                     message 1342
        (None, '6A60', None),                     # push 60h
        (None, 'FF750C', None),                   # push dword [ebp+0Ch]          club
        (None, 'E8', 'F600F2F_32'),               # call 00600F2F                 (arguments stay: [esp] = club)
        (None, 'FF7510', None),                   # push dword [ebp+10h]          player
        (None, 'E8', 'F70E29E_32'),               # call 0070E29E                 the player leaves club and game (new)
    ]),
    # K43, messages 1309 / 1310 / 1311 (0x005E1694 ff., club [ebp+0Ch], player [ebp+10h]): "before" came from the readers
    # 0x00700E3F / 0x007008B9 / 0x00700C42, which add or subtract allowances per player flag, "after" from the writers
    # (stored value). New: "before" is the stored value too, fetched with the writer and a change of 0 (as other sites do
    # with 0x00701210(0)); a writer with 0 changes nothing and recomputes the motivation.
    'vorher-1309': (0x005E184C, 0x005E18A3, {}, [
        (None, '6A00', None),                     # push 0
        (None, '8B4D10', None),                   # mov ecx,[ebp+10h]
        (None, 'E8', 'F700D27_32'),               # call 00700D27                 stored 0x271 before (was reader 0x00700E3F)
        (None, '668945FC', None),                 # mov [ebp-4],ax
        (None, '6A00', None),                     # push 0
        (None, '8B4D10', None),                   # mov ecx,[ebp+10h]
        (None, 'E8', 'F7007A1_32'),               # call 007007A1                 stored 0x26F before (was reader 0x007008B9)
        (None, '668945F8', None),                 # mov [ebp-8],ax
        (None, '6A00', None),                     # push 0                        w7
        (None, '6A0A', None),                     # push 0Ah
        (None, '8B4D10', None),                   # mov ecx,[ebp+10h]
        (None, 'E8', 'F7007A1_32'),               # call 007007A1                 0x26F + 10
        (None, '50', None),                       # push eax                      w6 after
        (None, 'FF75F8', None),                   # push dword [ebp-8]            w5 before
        (None, '6A00', None),                     # push 0                        w4
        (None, '6AF6', None),                     # push -10
        (None, '8B4D10', None),                   # mov ecx,[ebp+10h]
        (None, 'E8', 'F700D27_32'),               # call 00700D27                 0x271 - 10
        (None, '50', None),                       # push eax                      w3 after
        (None, 'FF75FC', None),                   # push dword [ebp-4]            w2 before
        (None, '6A05', None),                     # push 5
        (None, '6A00', None),                     # push 0
        (None, 'FF7510', None),                   # push dword [ebp+10h]
        (None, '681D050000', None),               # push 51Dh                     message 1309
        (None, '6A60', None),                     # push 60h
        (None, 'FF750C', None),                   # push dword [ebp+0Ch]
        (None, 'E8', 'F6015FE_32'),               # call 006015FE                 (add esp,30h dropped)
    ]),
    'vorher-1310': (0x005E18D5, 0x005E190E, {}, [
        (None, '6A00', None),                     # push 0
        (None, '8B4D10', None),                   # mov ecx,[ebp+10h]
        (None, 'E8', 'F700A6D_32'),               # call 00700A6D                 stored value before (was the reader 0x00700C42)
        (None, '668945FC', None),                 # mov [ebp-4],ax
        (None, '6A00', None),                     # push 0                        w4
        (None, '6AFD', None),                     # push -3
        (None, '8B4D10', None),                   # mov ecx,[ebp+10h]
        (None, 'E8', 'F700A6D_32'),               # call 00700A6D
        (None, '50', None),                       # push eax                      after
        (None, 'FF75FC', None),                   # push dword [ebp-4]            before
        (None, '6A01', None),                     # push 1
        (None, '6A00', None),                     # push 0
        (None, 'FF7510', None),                   # push dword [ebp+10h]
        (None, '681E050000', None),               # push 51Eh                     message 1310
        (None, '6A60', None),                     # push 60h
        (None, 'FF750C', None),                   # push dword [ebp+0Ch]
        (None, 'E8', 'F601043_32'),               # call 00601043                 (add esp,24h dropped)
    ]),
    'vorher-1311': (0x005E1940, 0x005E1979, {}, [
        (None, '6A00', None),                     # push 0
        (None, '8B4D10', None),                   # mov ecx,[ebp+10h]
        (None, 'E8', 'F700A6D_32'),               # call 00700A6D                 stored value before (was the reader 0x00700C42)
        (None, '668945FC', None),                 # mov [ebp-4],ax
        (None, '6A00', None),                     # push 0                        w4
        (None, '6AFB', None),                     # push -5
        (None, '8B4D10', None),                   # mov ecx,[ebp+10h]
        (None, 'E8', 'F700A6D_32'),               # call 00700A6D
        (None, '50', None),                       # push eax                      after
        (None, 'FF75FC', None),                   # push dword [ebp-4]            before
        (None, '6A01', None),                     # push 1
        (None, '6A00', None),                     # push 0
        (None, 'FF7510', None),                   # push dword [ebp+10h]
        (None, '681F050000', None),               # push 51Fh                     message 1311
        (None, '6A60', None),                     # push 60h
        (None, 'FF750C', None),                   # push dword [ebp+0Ch]
        (None, 'E8', 'F601043_32'),               # call 00601043                 (add esp,24h dropped)
    ]),
    # F01, "the affair comes out" (0x005FB751: texts 1126, 1127, 1128, 1236; pre-routine 0x005FB916). The pre-routine
    # admits married players with flag bit 2 (0x00702A5B at 0x005FB98E), which nothing ever set: 0x00702A02 clears it and
    # sets bit 3 ("the wife suspects", after 1123 and 1236), 0x00702962 clears both when the affair ends, and 0x007029A7
    # ("new lover", the three callers of texts 1251-1253) only stored her name index. New: 0x007029A7 also sets bit 2.
    # Same steps as before: index = 50 + random 0..49, repeated while equal to the partner's index.
    'geliebte-7029A7': (0x007029A7, 0x00702A02, {}, [
        (None, '51', None),                       # push ecx                      this
        ('AGAIN', '6A32', None),                  # push 32h
        (None, 'E8', 'F78A810_32'),               # call 0078A810                 random 0..49
        (None, '5A', None),                       # pop edx                       drop the argument
        (None, '0432', None),                     # add al,32h
        (None, '8B0C24', None),                   # mov ecx,[esp]
        (None, '0FBF11', None),                   # movsx edx,word [ecx]
        (None, '69D254030000', None),             # imul edx,edx,354h
        (None, '8882D427C000', None),             # mov [edx+00C027D4h],al        name index of the lover
        (None, '3A82D327C000', None),             # cmp al,[edx+00C027D3h]        same as the partner?
        (None, '74', 'AGAIN'),                    # je AGAIN
        (None, '838A0427C00004', None),           # or dword [edx+00C02704h],4    flag bit 2 "affair running" (new)
        (None, '59', None),                       # pop ecx
        (None, 'C3', None),                       # ret
    ]),
    # F01, text 1126 "... erwischt seine Frau %2, wie diese versucht, ihm auf dem Weg zu seiner Freundin %3
    # nachzuspionieren ... Er gibt klein bei" (0x005FB751 case 1, club [ebp+8], player [ebp+0Ch]): 0x00702962 (affair
    # ended, clears the lover's index) ran before her name was read. New: after the message.
    'affaere-1126': (0x005FB7AB, 0x005FB80F, {'END': 0x005FB80F}, [
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F702C12_32'),               # call 00702C12                 crisis level
        (None, '84C0', None),                     # test al,al
        (None, '75', 'END'),                      # jne END
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F7011F1_32'),               # call 007011F1
        (None, '668945FC', None),                 # mov [ebp-4],ax
        (None, '6A00', None),                     # push 0                        w4
        (None, '6AFB', None),                     # push -5
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F7010D9_32'),               # call 007010D9
        (None, '50', None),                       # push eax                      w3
        (None, 'FF75FC', None),                   # push dword [ebp-4]            w2
        (None, '6A02', None),                     # push 2                        w1
        (None, '6A00', None),                     # push 0                        s4
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F7017DB_32'),               # call 007017DB                 %3 lover (still entered)
        (None, '50', None),                       # push eax
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F70173F_32'),               # call 0070173F                 %2 wife
        (None, '50', None),                       # push eax
        (None, 'FF750C', None),                   # push dword [ebp+0Ch]
        (None, '6866040000', None),               # push 466h                     message 1126
        (None, '6A60', None),                     # push 60h
        (None, 'FF7508', None),                   # push dword [ebp+8]
        (None, 'E8', 'F6012DF_32'),               # call 006012DF                 (add esp,2Ch dropped)
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F702962_32'),               # call 00702962                 affair ended (moved behind the message)
    ]),
    # F05, text 1481 "... der Spielervermittler von %1 ... möchte, daß der Spieler noch eine Weile bei Ihrem Verein bleibt:
    # 'Dort hast Du die besten Entwicklungschancen'" (0x00768940 ff., negotiation with an agent, player [ebp-18h]). The test
    # "age < 20" stood inside the branch "age >= 25" and was never true. New order: age < 20 with the two unchanged
    # conditions (byte +0x54 > 10, byte +8 < 1) -> 1481; otherwise age < 25 -> 1480 with flag 4 as before; otherwise 1 in
    # 100 -> 1482 as before. Players under 20 who miss the two conditions get 1480 as before.
    'vermittler-1481': (0x00768940, 0x007689A7, {'END': 0x007689A7}, [
        (None, '8B4DE8', None),                   # mov ecx,[ebp-18h]
        (None, 'E8', 'F6FF01B_32'),               # call 006FF01B                 age
        (None, '6683F814', None),                 # cmp ax,14h
        (None, '7D', 'NOT20'),                    # jge NOT20
        (None, '8B55E8', None),                   # mov edx,[ebp-18h]
        (None, '807A540A', None),                 # cmp byte [edx+54h],0Ah
        (None, '76', 'NOT20'),                    # jbe NOT20                     (was: zero-extended, jle)
        (None, '807A0801', None),                 # cmp byte [edx+8],1
        (None, '7D', 'NOT20'),                    # jge NOT20                     (was: sign-extended, jge)
        (None, '66C745E6C905', None),             # mov word [ebp-1Ah],5C9h       text 1481
        (None, 'EB', 'END'),                      # jmp END
        ('NOT20', '6683F819', None),              # cmp ax,19h
        (None, '7D', 'OLD'),                      # jge OLD
        (None, '66834DC404', None),               # or word [ebp-3Ch],4
        (None, '66C745E6C805', None),             # mov word [ebp-1Ah],5C8h       text 1480
        (None, 'EB', 'END'),                      # jmp END
        ('OLD', '6A64', None),                    # push 64h
        (None, 'E8', 'F78A810_32'),               # call 0078A810                 random 0..99
        (None, '83C404', None),                   # add esp,4
        (None, '85C0', None),                     # test eax,eax
        (None, '75', 'END'),                      # jne END
        (None, '66C745E6CA05', None),             # mov word [ebp-1Ah],5CAh       text 1482
    ]),
    # K40 (part), text 969 "... Seine Frau %2 fände diese Idee auch einfach großartig" (club [ebp+8], player [ebp+0Ch]; the
    # case requires "married", 0x006FFB14): 0 was passed as %2. New: name of the partner. The tail (push 60h / club /
    # call 0x00600F2F / return 1) is taken from the neighbouring case at 0x005E4CF7, which is identical.
    'frau-969': (0x005E4D17, 0x005E4D32, {'TAIL': 0x005E4CF7}, [
        (None, '6A00', None),                     # push 0                        w
        (None, '8B4D0C', None),                   # mov ecx,[ebp+0Ch]
        (None, 'E8', 'F70173F_32'),               # call 0070173F                 name of the wife (new)
        (None, '50', None),                       # push eax                      %2
        (None, 'FF750C', None),                   # push dword [ebp+0Ch]          player
        (None, '68C9030000', None),               # push 3C9h                     message 969
        (None, 'EB', 'TAIL'),                     # jmp 005E4CF7                  push 60h / push club / call / mov ax,1
    ]),
}

if __name__ == '__main__':
    asm_presse.BLOCKS = BLOCKS
    exe = open(sys.argv[1], 'rb').read() if len(sys.argv) > 1 else None
    for name in BLOCKS:
        if len(sys.argv) > 2 and name != sys.argv[2]:
            continue
        code, used = asm_presse.assemble(name)
        start = BLOCKS[name][0]
        print(f'{name}: VA 0x{start:08X}, Datei-Offset 0x{start - 0x400000:08X}, {used} Byte Code, '
              f'{len(code) - used} Byte aufgefüllt, zusammen {len(code)}')
        if exe:
            print('  alt', exe[start - 0x400000:start - 0x400000 + len(code)].hex().upper())
        print('  neu', code.hex().upper())
