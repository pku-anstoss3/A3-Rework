import sys,math,collections
for p in sys.argv[1:]:
    d=open(p,'rb').read()
    def H(b):
        if not b: return 0
        c=collections.Counter(b); n=len(b)
        return -sum(v/n*math.log2(v/n) for v in c.values())
    blocks=[H(d[i:i+4096]) for i in range(0,len(d),4096)]
    pr=sum(1 for x in d if 32<=x<127 or x in (9,10,13) or x>=0xC0)/max(1,len(d))
    z=d.count(0)/max(1,len(d))
    print(f"{p:32s} {len(d):>9d}  H={H(d):.2f}  blkmin={min(blocks):.2f} blkmax={max(blocks):.2f}  print={pr:.2f} null={z:.2f}  head={d[:16].hex(' ')}")
