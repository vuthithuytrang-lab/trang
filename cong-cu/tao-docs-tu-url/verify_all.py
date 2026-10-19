# verify_all.py — quét mọi bản PDF đã tải về, khớp id với uploaded.json, so chữ với bản final
import json,glob,subprocess,os
W='/tmp/claude-0/-home-user-trang/3ba9cdf0-f0cf-51c4-a48f-adbd1e263eb3/scratchpad/pil/'
T='/root/.claude/projects/-home-user-trang/3ba9cdf0-f0cf-51c4-a48f-adbd1e263eb3/tool-results/'
reg=json.load(open(W+'uploaded.json')); rev={i:rel for rel,ids in reg.items() for i in ids}
done=json.load(open(W+'verified.json')) if os.path.exists(W+'verified.json') else {}
seen={v['id'] for v in done.values()} | set(json.load(open(W+'trashed.json')) if os.path.exists(W+'trashed.json') else [])
for f in sorted(glob.glob(T+'mcp-Google_Drive-download_file_content-*.txt')):
    try: i=json.load(open(f))['id']
    except Exception: continue
    if i in rev and i not in seen:
        subprocess.run(['python3',W+'verify.py',rev[i],f]); seen.add(i)
