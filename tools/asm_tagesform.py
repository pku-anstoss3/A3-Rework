"""Assemble the blocks of the patch 'tagesform' in a3patch.py and print them as hex.

League statistic "Tagesform" (class CTagesform; table built per club in 0x007230E1, page 0x0044EB33). The value is the
team's average grade of the last match. Patch: graded players only, the stored value is 100 - grade x 10 (the sorted
list keeps the greatest value on top and only takes values greater than an empty slot, see docs/befund-zaehler.md),
and the page prints it as a grade with one decimal ("3.1"). The format string of the page lives in 13 bytes freed in
the builder loop (0x00723170); the page is its only user.
Usage: python tools/asm_tagesform.py
"""
FORMAT = 0x00723170
BLOCKS = {
    # builder loop 0x00723162..0x0072317C: add the grade code, count graded players, back to the loop head, then data
    'schleife': (0x00723162, 0x0072317D, {'HEAD': 0x0072311C}, [
        (None, '660145EA', None),                 # add word ptr [ebp-16h],ax      sum of grade codes (eax = 0..15)
        (None, '83F801', None),                   # cmp eax,1
        (None, '66835DEEFF', None),               # sbb word ptr [ebp-12h],-1      graded players + 1 - carry
        (None, 'EB', 'HEAD'),                     # jmp 0072311C
        (None, b'%d.\t%s\t%d.%d\0'.hex(), None),  # 00723170: format string of the page
    ]),
    # builder tail 0x0072317D..0x0072319E: value = 100 - grade x 10, or 0 without a graded player
    'wert': (0x0072317D, 0x0072319F, {'ZERO': 0x00723199, 'STORE': 0x0072319B}, [
        (None, '0FBF4DEE', None),                 # movsx ecx,word ptr [ebp-12h]   graded players
        (None, '85C9', None),                     # test ecx,ecx
        (None, '7E', 'ZERO'),                     # jle 00723199
        (None, '0FBF45EA', None),                 # movsx eax,word ptr [ebp-16h]
        (None, '6BC005', None),                   # imul eax,eax,5                 code x 5 = grade x 10
        (None, '99', None),                       # cdq
        (None, 'F7F9', None),                     # idiv ecx
        (None, 'F7D8', None),                     # neg eax
        (None, '83C064', None),                   # add eax,64h                    100 - grade x 10
        (None, 'EB', 'STORE'),                    # jmp 0072319B
        (None, '909090', None),
        (None, '33C0', None),                     # 00723199: xor eax,eax
        (None, '668945F8', None),                 # 0072319B: mov word ptr [ebp-8],ax
    ]),
    # page 0x0044ECB9..0x0044ED11: one row = place, club, grade with one decimal
    'zeile': (0x0044ECB9, 0x0044ED12, {'NAME32': 0x0063E52F}, [
        (None, '0FBF853AFDFFFF', None),           # movsx eax,word ptr [ebp-2C6h]  row index
        (None, '8D94C534FFFFFF', None),           # lea edx,[ebp+eax*8-0CCh]       record: land, club, value, count
        (None, '6A6458', None),                   # push 64h / pop eax
        (None, '662B4204', None),                 # sub ax,word ptr [edx+4]        100 - value = grade x 10
        (None, '98', None),                       # cwde
        (None, '52', None),                       # push edx                       keep the record pointer
        (None, '99', None),                       # cdq
        (None, '6A0A59', None),                   # push 0Ah / pop ecx
        (None, 'F7F9', None),                     # idiv ecx                       eax = grade, edx = tenths
        (None, '59', None),                       # pop ecx                        record pointer
        (None, '52', None),                       # push edx                       tenths
        (None, '50', None),                       # push eax                       grade
        (None, '668B4102', None),                 # mov ax,word ptr [ecx+2]        club
        (None, '50', None),                       # push eax
        (None, '668B11', None),                   # mov dx,word ptr [ecx]          land
        (None, '52', None),                       # push edx
        (None, 'E8', 'NAME32'),                   # call 0063E52F                  club name
        (None, '83C408', None),                   # add esp,8
        (None, '50', None),                       # push eax
        (None, '0FBF853AFDFFFF', None),           # movsx eax,word ptr [ebp-2C6h]
        (None, '40', None),                       # inc eax
        (None, '50', None),                       # push eax                       place
        (None, '68' + FORMAT.to_bytes(4, 'little').hex(), None),   # push 00723170h
        (None, '8D8D3CFDFFFF', None),             # lea ecx,[ebp-2C4h]             text buffer
        (None, '51', None),                       # push ecx
        (None, 'FF15B8D58000', None),             # call dword ptr [0080D5B8h]     sprintf
        (None, '83C418', None),                   # add esp,18h
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
    return bytes(out) + b'\x90' * (end - start - used), used


if __name__ == '__main__':
    for name in BLOCKS:
        code, used = assemble(name)
        print(f'{name}: {used} Byte Code, {len(code) - used} Byte aufgefüllt, zusammen {len(code)}')
        print(code.hex().upper())
