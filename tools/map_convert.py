"""Pair import-struct offsets with game-struct offsets from a conversion routine.

Tracks which register holds the import struct (IMP) and which the game object (OBJ),
then reports 'load [IMP+a] -> store [OBJ+b]' pairs and string copies (call 007E0FFE = strcpy).

Usage: python map_convert.py <convert.asm> <imp_slot> <obj_slot>
  e.g. python map_convert.py analyse/verein_convert.asm ebp+FFFFFF78h ebp+8
"""
import re
import sys

STRCPY = '007E0FFE'


def off(expr):
    m = re.search(r'\[(e[a-d]x|esi|edi)(?:\+([0-9A-F]+)h)?\]', expr)
    if not m:
        return None, None
    return m.group(1), int(m.group(2), 16) if m.group(2) else 0


R32 = {'al': 'eax', 'ah': 'eax', 'ax': 'eax', 'bl': 'ebx', 'bx': 'ebx', 'cl': 'ecx', 'ch': 'ecx', 'cx': 'ecx',
       'dl': 'edx', 'dh': 'edx', 'dx': 'edx'}


def main():
    src, imp_slot, obj_slot = sys.argv[1], sys.argv[2], sys.argv[3]
    role = {}      # reg -> ('IMP'|'OBJ', add)
    val = {}       # data reg -> (imp offset, width)
    pushes = []
    width = {'byte': 1, 'word': 2, 'dword': 4}
    for ln in open(src, encoding='latin-1'):
        m = re.match(r'\s+([0-9A-F]{8}): (\w+)\s*(.*)', ln)
        if not m:
            continue
        addr, op, args = m.groups()
        a = [x.strip() for x in args.split(',')] if args else []
        if op == 'mov' and len(a) == 2 and '[' not in a[0]:
            dst = R32.get(a[0], a[0])
            if imp_slot in a[1]:
                role[dst] = ['IMP', 0]
                continue
            if obj_slot in a[1] and '[' in a[1] and a[1].endswith(obj_slot + ']'):
                role[dst] = ['OBJ', 0]
                continue
            r, o = off(a[1])
            if r and r in role and role[r][0] == 'IMP':
                w = re.match(r'(byte|word|dword) ptr', a[1])
                val[dst] = (role[r][1] + o, width[w.group(1)] if w else 4)
                continue
            role.pop(dst, None)
            val.pop(dst, None)
        elif op in ('movsx', 'movzx') and len(a) == 2:
            r, o = off(a[1])
            if r and r in role and role[r][0] == 'IMP':
                w = re.match(r'(byte|word|dword) ptr', a[1])
                val[R32.get(a[0], a[0])] = (role[r][1] + o, width[w.group(1)] if w else 4)
        elif op == 'mov' and len(a) == 2 and '[' in a[0]:
            r, o = off(a[0])
            srcreg = a[1]
            base = R32.get(srcreg, srcreg)
            if r and r in role and role[r][0] == 'OBJ':
                w = re.match(r'(byte|word|dword) ptr', a[0])
                tgt = role[r][1] + o
                if base in val:
                    io, _ = val[base]
                    print(f'{addr} imp 0x{io:03X} -> obj 0x{tgt:03X} ({w.group(1) if w else "?"})')
                elif re.match(r'^-?[0-9A-F]+h?$', srcreg):
                    print(f'{addr} const {srcreg} -> obj 0x{tgt:03X} ({w.group(1) if w else "?"})')
                else:
                    print(f'{addr} ?{srcreg} -> obj 0x{tgt:03X} ({w.group(1) if w else "?"})')
        elif op == 'add' and len(a) == 2 and a[0] in role:
            role[a[0]][1] += int(a[1][:-1], 16) if a[1].endswith('h') else int(a[1])
        elif op == 'push':
            pushes.append(tuple(role[a[0]]) if a[0] in role else a[0])
        elif op == 'call':
            if a[0] == STRCPY and len(pushes) >= 2:
                d, s = pushes[-1], pushes[-2]
                print(f'{addr} strcpy {s} -> {d}')
            pushes.clear()
            role.clear()
            val.clear()


if __name__ == '__main__':
    main()
