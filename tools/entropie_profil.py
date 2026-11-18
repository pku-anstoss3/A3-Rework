import sys,math,collections
d=open(sys.argv[1],'rb').read(); B=int(sys.argv[2])
def H(b):
    c=collections.Counter(b); n=len(b); return -sum(v/n*math.log2(v/n) for v in c.values())
row=[]
for i in range(0,len(d),B):
    h=H(d[i:i+B]); row.append('0123456789'[min(9,int(h*10/8.01))])
for k in range(0,len(row),64): print(f"{k*B:08x} {''.join(row[k:k+64])}")
