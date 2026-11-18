"""Assemble the new tail of 0x00744654 (patch 'vereinsliste-spiele' in a3patch.py) and print it as hex.

The bytes are fixed encodings; only the jump distances are computed here, so that no offset is counted by hand.
Usage: python tools/asm_vereinsliste.py
"""
START, END, SETTER = 0x007447B1, 0x007448BF, 0x00633384

CODE = [                                      # (label or None, hex bytes, jump target label or None, kind)
    (None,     '66837DDA00', None),           # cmp word ptr [ebp-26h],0      human-managed club?
    (None,     '0F84', 'END32'),              # je END
    # --- set every "at the club" flag of the games list from the current squad
    (None,     '8DBD80FBFFFF', None),         # lea edi,[ebp-480h]            first entry
    ('E_LOOP', '66833F00', None),             # cmp word ptr [edi],0          empty entry
    (None,     '74', 'E_NEXT'),               # je E_NEXT
    (None,     '66C747080000', None),         # mov word ptr [edi+8],0        flag = 0
    (None,     '8B5508', None),               # mov edx,[ebp+8]               club
    (None,     '0FBF8AE2000000', None),       # movsx ecx,word ptr [edx+0E2h] squad size
    (None,     '8DB2500B0000', None),         # lea esi,[edx+0B50h]           squad pointers
    ('S_LOOP', '49', None),                   # dec ecx
    (None,     '78', 'E_NEXT'),               # js E_NEXT
    (None,     '8B048E', None),               # mov eax,[esi+ecx*4]           player
    (None,     '668B10', None),               # mov dx,[eax]                  number
    (None,     '663B17', None),               # cmp dx,[edi]
    (None,     '75', 'S_LOOP'),               # jne S_LOOP
    (None,     '668B90CE000000', None),       # mov dx,[eax+0CEh]             year of birth
    (None,     '663B5706', None),             # cmp dx,[edi+6]
    (None,     '75', 'S_LOOP'),               # jne S_LOOP
    (None,     '66C747080100', None),         # mov word ptr [edi+8],1        flag = 1
    ('E_NEXT', '83C716', None),               # add edi,16h
    (None,     '8D45CC', None),               # lea eax,[ebp-34h]             end of the list
    (None,     '3BF8', None),                 # cmp edi,eax
    (None,     '72', 'E_LOOP'),               # jb E_LOOP
    # --- selection sort by games (+0Ah), descending, as before
    (None,     '8DBD80FBFFFF', None),         # lea edi,[ebp-480h]            entry i
    ('O_LOOP', '8BD7', None),                 # mov edx,edi                   best = i
    (None,     '8D7716', None),               # lea esi,[edi+16h]             j = i + 1
    ('I_LOOP', '8D45CC', None),               # lea eax,[ebp-34h]
    (None,     '3BF0', None),                 # cmp esi,eax
    (None,     '73', 'I_DONE'),               # jae I_DONE
    (None,     '668B420A', None),             # mov ax,[edx+0Ah]
    (None,     '663B460A', None),             # cmp ax,[esi+0Ah]
    (None,     '7D', 'I_NEXT'),               # jge I_NEXT
    (None,     '8BD6', None),                 # mov edx,esi                   best = j
    ('I_NEXT', '83C616', None),               # add esi,16h
    (None,     'EB', 'I_LOOP'),               # jmp I_LOOP
    ('I_DONE', '3BD7', None),                 # cmp edx,edi
    (None,     '74', 'NO_SWAP'),              # je NO_SWAP
    (None,     'B90B000000', None),           # mov ecx,11                    22 bytes = 11 words
    ('SWAP',   '668B07', None),               # mov ax,[edi]
    (None,     '668702', None),               # xchg ax,[edx]
    (None,     '668907', None),               # mov [edi],ax
    (None,     '83C702', None),               # add edi,2
    (None,     '83C202', None),               # add edx,2
    (None,     '49', None),                   # dec ecx
    (None,     '75', 'SWAP'),                 # jnz SWAP
    (None,     '83EF16', None),               # sub edi,16h                   back to entry i
    ('NO_SWAP', '83C716', None),              # add edi,16h
    (None,     '8D45B6', None),               # lea eax,[ebp-4Ah]             entry 49
    (None,     '3BF8', None),                 # cmp edi,eax
    (None,     '72', 'O_LOOP'),               # jb O_LOOP
    # --- write the list back
    (None,     '8D8580FBFFFF', None),         # lea eax,[ebp-480h]
    (None,     '50', None),                   # push eax
    (None,     'FF7508', None),               # push dword ptr [ebp+8]
    (None,     'E8', 'SETTER32'),             # call 00633384
    (None,     '83C408', None),               # add esp,8
    (None,     'EB', 'END'),                  # jmp END
]


def assemble():
    size = lambda h, t: len(h) // 2 + (0 if t is None else 4 if t.endswith('32') else 1)
    addr, pos = {}, START
    for label, h, t in CODE:
        if label:
            addr[label] = pos
        pos += size(h, t)
    addr.update(END=END, END32=END, SETTER32=SETTER)
    out, pos = bytearray(), START
    for label, h, t in CODE:
        out += bytes.fromhex(h)
        pos += size(h, t)
        if t:
            d = addr[t] - pos
            if t.endswith('32'):
                out += (d & 0xFFFFFFFF).to_bytes(4, 'little')
            else:
                assert -128 <= d <= 127, (t, d)
                out += (d & 0xFF).to_bytes(1, 'little')
    assert len(out) <= END - START, len(out)
    return bytes(out) + b'\x90' * (END - START - len(out)), len(out)


if __name__ == '__main__':
    code, used = assemble()
    print(f'{used} Byte Code, {len(code) - used} Byte aufgefüllt, zusammen {len(code)}')
    print(code.hex().upper())
