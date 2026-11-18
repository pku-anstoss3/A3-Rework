"""Assemble the new body of 0x00705EB6 (patch 'totalausfall' in a3patch.py) and print it as hex.

0x00705EB6 returns a player's season average grade x 10 for the newspaper headline 1519 ("... erneut ein Totalausfall").
The original reads the match-day bytes with the masks 0x80 / 0x1C instead of 0xC0 / 0x3C and scans all 46 slots, so the
result never exceeds 35 and the headline (needs > 40) can never appear. New body: only the match days played so far,
appearance = bits 0xC0, grade code = bits 0x3C, appearances without a grade are skipped.
The number of match days comes from 0x00692744(club); the club pointer is taken from the frame of the ONLY caller
(0x005E572C, club = [ebp+8]) - this routine sets up no frame of its own, so ebp is still the caller's.
Usage: python tools/asm_totalausfall.py
"""
START, END = 0x00705EB6, 0x00705F60
TARGETS = {'MATCHDAYS32': 0x00692744}

CODE = [                                      # (label or None, hex bytes, jump target label or None)
    (None,    '56', None),                    # push esi
    (None,    '57', None),                    # push edi
    (None,    '53', None),                    # push ebx
    (None,    '8BD9', None),                  # mov ebx,ecx                   player
    (None,    '8B4508', None),                # mov eax,[ebp+8]               club (frame of the caller 0x005E572C)
    (None,    '50', None),                    # push eax
    (None,    'E8', 'MATCHDAYS32'),           # call 00692744                 match days played
    (None,    '83C404', None),                # add esp,4
    (None,    '0FBFF8', None),                # movsx edi,ax
    (None,    '83FF2E', None),                # cmp edi,2Eh
    (None,    '7E', 'OK'),                    # jle OK
    (None,    '6A2E5F', None),                # push 2Eh / pop edi            at most 46 slots
    ('OK',    '0FBF03', None),                # movsx eax,word ptr [ebx]      player number
    (None,    '69C054030000', None),          # imul eax,eax,354h
    (None,    '33D2', None),                  # xor edx,edx                   sum of grade codes
    (None,    '33F6', None),                  # xor esi,esi                   graded games
    (None,    'EB', 'CHECK'),                 # jmp CHECK
    ('LOOP',  '0FB68C386928C000', None),      # movzx ecx,byte ptr [eax+edi+00C02869h]
    (None,    'F6C1C0', None),                # test cl,0C0h                  appearance?
    (None,    '74', 'CHECK'),                 # jz CHECK
    (None,    'C1E902', None),                # shr ecx,2
    (None,    '83E10F', None),                # and ecx,0Fh                   grade code
    (None,    '74', 'CHECK'),                 # jz CHECK                      no grade
    (None,    '03D1', None),                  # add edx,ecx
    (None,    '46', None),                    # inc esi
    ('CHECK', '4F', None),                    # dec edi
    (None,    '79', 'LOOP'),                  # jns LOOP
    (None,    '33C0', None),                  # xor eax,eax
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
]


def assemble():
    size = lambda h, t: len(h) // 2 + (0 if t is None else 4 if t.endswith('32') else 1)
    addr, pos = dict(TARGETS), START
    for label, h, t in CODE:
        if label:
            addr[label] = pos
        pos += size(h, t)
    out, pos = bytearray(), START
    for label, h, t in CODE:
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
    assert used <= END - START, used
    return bytes(out) + b'\xCC' * (END - START - used), used


if __name__ == '__main__':
    code, used = assemble()
    print(f'{used} Byte Code, {len(code) - used} Byte aufgefüllt, zusammen {len(code)}')
    print(code.hex().upper())
