"""Assemble the two code blocks of the patch 'konto-anlagen' in a3patch.py and print them as hex.

Background (docs/befund-finanzen.md): the club fortune [P] + profit of the season carries every investment with the amount
paid in; the growth of an investment is booked once, when it is dissolved. The bank balance 0x0061FD97 nevertheless
subtracts the CURRENT value of the investments (0x00648947), so the balance is too low by the whole growth for as long
as an investment runs, and jumps by payout + growth when it is dissolved.

Block 1, 0x0061FD97 (bank balance, cdecl, P = club + 210h on the stack, result in edx:eax):
    [P] + int32 [P+C0h] + profit 0x0061FC81(P, P+18h) - paid-in amounts of the active investments + credits 0x006488CA(P)
    Investments: 6 slots of 18h bytes from P+1C8h, int64 paid in at +0, active = bit 0 of the byte at +13h.
Block 2, 0x00481426 (balance screen, line "Aktuelles Vereinsvermögen", inside 0x004813AD; this = [ebp-220h],
    P = [this+1404h]): bank balance + current value of the investments - credits, left in edi:esi for the unchanged
    "push edi / push esi / call 004DB27E" that follows at 0x00481477.
Usage: python tools/asm_konto.py
"""
TARGETS = {'GEWINN32': 0x0061FC81, 'KREDITE32': 0x006488CA, 'ANLAGEN32': 0x00648947, 'KONTO32': 0x0061FD97}

KONTO = (0x0061FD97, 0x0061FDFA, 'CC', [      # (label or None, hex bytes, jump target label or None)
    (None,   '56', None),                     # push esi
    (None,   '57', None),                     # push edi
    (None,   '53', None),                     # push ebx
    (None,   '8B5C2410', None),               # mov ebx,[esp+10h]             P
    (None,   '8B83C0000000', None),           # mov eax,[ebx+0C0h]
    (None,   '99', None),                     # cdq
    (None,   '8B33', None),                   # mov esi,[ebx]                 fortune at the start of the season
    (None,   '8B7B04', None),                 # mov edi,[ebx+4]
    (None,   '03F0', None),                   # add esi,eax
    (None,   '13FA', None),                   # adc edi,edx
    (None,   '8D4318', None),                 # lea eax,[ebx+18h]
    (None,   '50', None),                     # push eax
    (None,   '53', None),                     # push ebx
    (None,   'E8', 'GEWINN32'),               # call 0061FC81                 profit of the season
    (None,   '83C408', None),                 # add esp,8
    (None,   '03F0', None),                   # add esi,eax
    (None,   '13FA', None),                   # adc edi,edx
    (None,   '8D8BC8010000', None),           # lea ecx,[ebx+1C8h]            first investment slot
    (None,   '6A06', None),                   # push 6
    (None,   '58', None),                     # pop eax                       six slots
    ('LOOP', 'F6411301', None),               # test byte ptr [ecx+13h],1     active?
    (None,   '74', 'NEXT'),                   # je NEXT
    (None,   '2B31', None),                   # sub esi,[ecx]                 amount paid in (was: current value)
    (None,   '1B7904', None),                 # sbb edi,[ecx+4]
    ('NEXT', '83C118', None),                 # add ecx,18h
    (None,   '48', None),                     # dec eax
    (None,   '75', 'LOOP'),                   # jne LOOP
    (None,   '53', None),                     # push ebx
    (None,   'E8', 'KREDITE32'),              # call 006488CA                 credits
    (None,   '59', None),                     # pop ecx
    (None,   '03C6', None),                   # add eax,esi
    (None,   '13D7', None),                   # adc edx,edi
    (None,   '5B', None),                     # pop ebx
    (None,   '5F', None),                     # pop edi
    (None,   '5E', None),                     # pop esi
    (None,   'C3', None),                     # ret
])

VERMOEGEN = (0x00481426, 0x00481477, '90', [
    (None,   '8B85E0FDFFFF', None),           # mov eax,[ebp-220h]            this
    (None,   'FFB004140000', None),           # push dword ptr [eax+1404h]    P
    (None,   'E8', 'KONTO32'),                # call 0061FD97                 bank balance (block 1)
    (None,   '59', None),                     # pop ecx
    (None,   '8BF0', None),                   # mov esi,eax
    (None,   '8BFA', None),                   # mov edi,edx
    (None,   '8B85E0FDFFFF', None),           # mov eax,[ebp-220h]
    (None,   'FFB004140000', None),           # push dword ptr [eax+1404h]
    (None,   'E8', 'ANLAGEN32'),              # call 00648947                 investments at their current value
    (None,   '59', None),                     # pop ecx
    (None,   '03F0', None),                   # add esi,eax
    (None,   '13FA', None),                   # adc edi,edx
    (None,   '8B85E0FDFFFF', None),           # mov eax,[ebp-220h]
    (None,   'FFB004140000', None),           # push dword ptr [eax+1404h]
    (None,   'E8', 'KREDITE32'),              # call 006488CA                 credits
    (None,   '59', None),                     # pop ecx
    (None,   '2BF0', None),                   # sub esi,eax
    (None,   '1BFA', None),                   # sbb edi,edx
])


def assemble(block):
    start, end, fill, code = block
    size = lambda h, t: len(h) // 2 + (0 if t is None else 4 if t.endswith('32') else 1)
    addr, pos = dict(TARGETS), start
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
    assert used <= end - start, used
    return bytes(out) + bytes.fromhex(fill) * (end - start - used), used


if __name__ == '__main__':
    for name, block in (('Kontorechnung 0x0061FD97', KONTO), ('Bilanzzeile 0x00481426', VERMOEGEN)):
        code, used = assemble(block)
        print(f'{name}: Dateioffset 0x{block[0] - 0x400000:06X}, {used} Byte Code, {len(code) - used} Byte aufgefüllt, zusammen {len(code)}')
        print(code.hex().upper())
