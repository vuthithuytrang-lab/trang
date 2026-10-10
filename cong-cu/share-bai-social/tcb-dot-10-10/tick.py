import subprocess,re,os,sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
nx=[]
for s in ('wf_step.py','wix_step.py'):
  o=subprocess.run([sys.executable,s],capture_output=True,text=True); out=o.stdout+o.stderr
  print('==',s); print(out.strip()[-1500:])
  m=re.search(r'NEXT (\S+)',out); m and m.group(1)!='None' and nx.append(m.group(1))
if subprocess.run(['pgrep','-f','^python3 wp_thumbs'],capture_output=True).returncode!=0 and len(open('thumbs_done.jsonl').read().split('"ok": true'))-1<40:
  subprocess.Popen('setsid nohup python3 wp_thumbs.py >> wp_thumbs.log 2>&1 < /dev/null &',shell=True)
print('WAKE_AT',min(nx) if nx else None)
