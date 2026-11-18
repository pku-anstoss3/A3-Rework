import sys,re
d=open(sys.argv[1],'rb').read(); n=int(sys.argv[2]); lim=int(sys.argv[3])
r=list(re.finditer(rb'[\x20-\x7e\xc4\xd6\xdc\xe4\xf6\xfc\xdf]{%d,}'%n,d))
print('runs>=%d:'%n,len(r))
for m in r[:lim]: print(hex(m.start()), m.group().decode('cp1252'))
