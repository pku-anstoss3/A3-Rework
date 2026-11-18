"""Derive the field map (text line -> struct offset, type) from a master-data loader routine.

Input is a dumpbin disassembly excerpt of one loader function (e.g. analyse/verein_loader.asm).
The loader reads one text line per helper call and stores it at [this + offset].

Usage: python map_loader.py <loader.asm> [this_slot]
  this_slot: stack slot that holds the struct pointer, default 'ebp+FFFFFBF4h'
"""
import re
import sys

HELPERS = {
    '00402030': 'u8', '004020DD': 'i8', '00401F82': 'i16',
    '00401ED5': 'i32', '0040218A': 'i32l', '00402418': 'str', '00402586': 'date',
    '0040170D': 'section', '0068C06F': 'subsection', '0068C257': 'subsection2',
}
STRNCPY = 'dword ptr ds:[0080D608h]'


def main():
    lines = open(sys.argv[1], encoding='latin-1').read().splitlines()
    this = sys.argv[2] if len(sys.argv) > 2 else 'ebp+FFFFFBF4h'
    reg = {}        # register -> offset relative to this (None if unknown)
    stack = []      # pushed values: ('off', n) / ('local',) / ('imm', n) / ('?',)
    pending_str = False
    n = 0
    for ln in lines:
        m = re.match(r'\s+([0-9A-F]{8}): (\w+)\s*(.*)', ln)
        if not m:
            continue
        addr, op, args = m.groups()
        a = [x.strip() for x in args.split(',')] if args else []
        if op == 'mov' and len(a) == 2 and a[0] in ('eax', 'ecx', 'edx') and this in a[1]:
            reg[a[0]] = 0
        elif op == 'add' and len(a) == 2 and reg.get(a[0]) is not None:
            reg[a[0]] += int(a[1][:-1], 16) if a[1].endswith('h') else int(a[1])
        elif op == 'lea' and len(a) == 2:
            reg[a[0]] = None
            reg[a[0] + '_local'] = True
        elif op == 'push':
            if a[0] in reg and reg[a[0]] is not None:
                stack.append(('off', reg[a[0]]))
            elif a[0] in reg:
                stack.append(('local',))
            else:
                stack.append(('imm', a[0]))
        elif op == 'call':
            tgt = a[0]
            kind = HELPERS.get(tgt)
            if kind:
                arg = stack[-1] if stack else ('?',)
                if kind == 'str':
                    arg = stack[-1] if stack else ('?',)
                    if arg[0] == 'local':
                        pending_str = True
                        n += 1
                        print(f'{n:3d} {addr} str   -> (local, see strncpy)')
                        stack.clear()
                        continue
                n += 1 if kind not in ('subsection', 'subsection2') else 0
                where = f'0x{arg[1]:03X}' if arg[0] == 'off' else str(arg)
                tag = f'{n:3d}' if kind not in ('subsection', 'subsection2') else '  -'
                print(f'{tag} {addr} {kind:5s} -> {where}')
            elif tgt == STRNCPY and pending_str:
                dst = stack[-3] if len(stack) >= 3 else ('?',)
                ln_ = stack[-1]
                where = f'0x{dst[1]:03X}' if dst[0] == 'off' else str(dst)
                print(f'      {addr} strncpy -> {where} len {ln_[1] if ln_[0] == "imm" else "?"}')
                pending_str = False
            stack.clear()
            for k in list(reg):
                if k in ('eax', 'ecx', 'edx'):
                    reg[k] = None


if __name__ == '__main__':
    main()
