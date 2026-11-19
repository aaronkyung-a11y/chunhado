import sys, os, subprocess
man=sys.argv[1]; outdir=sys.argv[2]
os.makedirs(outdir,exist_ok=True)
for line in open(man,encoding='utf-8'):
    line=line.strip()
    if not line: continue
    key,name,url=line.split('\t')
    dst=os.path.join(outdir,key+'.png')
    if os.path.exists(dst) and os.path.getsize(dst)>10000: continue
    r=subprocess.run(['curl','-sS','-m','90','-o',dst,'-w','%{http_code}',url],capture_output=True,text=True)
    print(key,name,r.stdout,os.path.getsize(dst) if os.path.exists(dst) else 0)
