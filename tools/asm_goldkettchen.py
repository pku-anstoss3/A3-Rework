"""Assemble the two blocks of the patch 'goldkettchen' in a3patch.py and print them as hex.

Newspaper headline 1235 ("Goldkettchen und teure Autos - %1 ein Prototyp des verzogenen Fußballmillionärs"), a random
private-life event (0x005FEBDF ff.) for a player with field +2 >= 9 in a club clearly below its target, if the average
of his last three appearances is "> 40".
Block 1, 0x00705F60 (average of the last appearances): the original reads the match-day bytes with the masks 0x80 /
  0x1C instead of 0xC0 / 0x3C, scans all 46 slots and does not divide the grade code by 2. New body: match days played
  so far only, correct masks, the last three GRADED games, result = grade x 10 like the sister routine 0x00705EB6
  (so "> 40" means worse than 4.0). No stack argument any more (the count 3 is fixed). The club pointer for
  0x00692744 is taken from the frame of the ONLY caller (0x005FEC09, club = [ebp+0Ch]).
Block 2, 0x005FEC04 (call site): same headline call, followed by the deduction of 2 from "Presse" (0x00700FA2) that the
  original passes to the headline but never applies (the record carries no player number).
Usage: python tools/asm_goldkettchen.py
"""
BLOCKS = {
    'routine': (0x00705F60, 0x00706015, {'MATCHDAYS32': 0x00692744}, [
        (None,    '56', None),                    # push esi
        (None,    '57', None),                    # push edi
        (None,    '53', None),                    # push ebx
        (None,    '8BD9', None),                  # mov ebx,ecx                   player
        (None,    '8B450C', None),                # mov eax,[ebp+0Ch]             club (frame of the caller 0x005FEC09)
        (None,    '50', None),                    # push eax
        (None,    'E8', 'MATCHDAYS32'),           # call 00692744                 match days played
        (None,    '83C404', None),                # add esp,4
        (None,    '0FBFF8', None),                # movsx edi,ax
        (None,    '83FF2E', None),                # cmp edi,2Eh
        (None,    '7E', 'OK'),                    # jle OK
        (None,    '6A2E5F', None),                # push 2Eh / pop edi
        ('OK',    '0FBF03', None),                # movsx eax,word ptr [ebx]      player number
        (None,    '69C054030000', None),          # imul eax,eax,354h
        (None,    '33D2', None),                  # xor edx,edx                   sum of grade codes
        (None,    '33F6', None),                  # xor esi,esi                   graded games found
        (None,    'EB', 'CHECK'),                 # jmp CHECK
        ('LOOP',  '0FB68C386928C000', None),      # movzx ecx,byte ptr [eax+edi+00C02869h]
        (None,    'F6C1C0', None),                # test cl,0C0h                  appearance?
        (None,    '74', 'CHECK'),                 # jz CHECK
        (None,    'C1E902', None),                # shr ecx,2
        (None,    '83E10F', None),                # and ecx,0Fh                   grade code
        (None,    '74', 'CHECK'),                 # jz CHECK                      no grade
        (None,    '03D1', None),                  # add edx,ecx
        (None,    '46', None),                    # inc esi
        (None,    '83FE03', None),                # cmp esi,3
        (None,    '7D', 'CALC'),                  # jge CALC                      three games are enough
        ('CHECK', '4F', None),                    # dec edi
        (None,    '79', 'LOOP'),                  # jns LOOP
        ('CALC',  '33C0', None),                  # xor eax,eax
        (None,    '85F6', None),                  # test esi,esi
        (None,    '74', 'DONE'),                  # jz DONE
        (None,    '6BC20A', None),                # imul eax,edx,0Ah
        (None,    '99', None),                    # cdq
        (None,    'F7FE', None),                  # idiv esi
        (None,    'D1F8', None),                  # sar eax,1                     grade x 10
        ('DONE',  '5B', None),                    # pop ebx
        (None,    '5F', None),                    # pop edi
        (None,    '5E', None),                    # pop esi
        (None,    'C3', None),                    # ret
    ]),
    'aufruf': (0x005FEC04, 0x005FEC3F, {'AVG32': 0x00705F60, 'NAME32': 0x006FEB4D, 'NEWS32': 0x00789C32,
                                        'PRESSE32': 0x00700FA2, 'END': 0x005FEC3F}, [
        (None,    '8B4D08', None),                # mov ecx,[ebp+8]               player
        (None,    'E8', 'AVG32'),                 # call 00705F60                 grade x 10, last three graded games
        (None,    '663D2800', None),              # cmp ax,28h
        (None,    '7E', 'END'),                   # jle 005FEC3F                  4.0 or better: nothing
        (None,    '6AFE', None),                  # push -2
        (None,    '6A00', None),                  # push 0
        (None,    '8B4D08', None),                # mov ecx,[ebp+8]
        (None,    'E8', 'NAME32'),                # call 006FEB4D                 player name
        (None,    '50', None),                    # push eax
        (None,    '6800010000', None),            # push 100h
        (None,    '6A01', None),                  # push 1
        (None,    '68D3040000', None),            # push 4D3h                     headline 1235
        (None,    '6A06', None),                  # push 6
        (None,    'E8', 'NEWS32'),                # call 00789C32
        (None,    '83C418', None),                # add esp,18h
        (None,    '6AFE', None),                  # push -2
        (None,    '8B4D08', None),                # mov ecx,[ebp+8]
        (None,    'E8', 'PRESSE32'),              # call 00700FA2                 "Presse" - 2 (new)
    ]),
}


def assemble(name):
    start, end, targets, code = BLOCKS[name]
    size = lambda h, t: len(h) // 2 + (0 if t is None else 4 if t.endswith('32') else 1)
    addr, pos = dict(targets), start
    for label, h, t in code:
        if label:
            addr[label] = pos
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
    return bytes(out) + (b'\xCC' if name == 'routine' else b'\x90') * (end - start - used), used


if __name__ == '__main__':
    for name in BLOCKS:
        code, used = assemble(name)
        print(f'{name}: {used} Byte Code, {len(code) - used} Byte aufgefüllt, zusammen {len(code)}')
        print(code.hex().upper())
