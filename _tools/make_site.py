"""Build the GitHub Pages version (site/index.html) from index.html: full HTML skeleton + password gate."""
import hashlib, sys
# usage: python3 make_site.py SRC_INDEX OUT_INDEX [--hash HEX | --keep-hash-from OLD_INDEX]
import re
src, out_path = sys.argv[1], sys.argv[2]
if sys.argv[3] == '--hash': H = sys.argv[4]
else: H = re.search(r"const H='([0-9a-f]{64})'", open(sys.argv[4]).read()).group(1)
s = open(src).read()
call = "fetch('data.json',{cache:'no-store'})"
assert call in s
s = s.replace(call, "window.GATE.then(()=>" + call + ")", 1)
gate = """<style>
#gate{position:fixed;inset:0;z-index:999;display:grid;place-items:center;background:var(--bg,#0f0c18);padding:16px}
#gate form{width:100%;max-width:340px;text-align:center}
#gate img{width:64px}#gate h2{font-size:20px;margin:12px 0 4px;letter-spacing:.06em}#gate p{color:var(--muted,#999);font-size:14px;margin:0 0 18px}
#gate input{width:100%;box-sizing:border-box;padding:13px 16px;border-radius:12px;border:1px solid var(--line,#333);background:var(--surface,#1b1726);color:inherit;font-size:16px}
#gate button{margin-top:10px;width:100%;padding:13px;border:0;border-radius:12px;background:#e84a8a;color:#fff;font-size:16px;font-weight:600;cursor:pointer}
#gate .er{color:#ff6b6b;font-size:13px;min-height:18px;margin-top:8px}
</style>
<div id="gate" hidden><form><img src="logo.png" alt=""><h2>LOTUS ARENA</h2><p>Материалы · вход по паролю</p>
<input type="password" placeholder="Пароль" autocomplete="current-password" autofocus><button>Войти</button><div class="er"></div></form></div>
<script>
window.GATE=new Promise(ok=>{const H='@@H@@',K='lotus-pass';
const sha=async t=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(t)))].map(b=>b.toString(16).padStart(2,'0')).join('');
let saved='';try{saved=localStorage.getItem(K)||''}catch(e){}
if(saved===H){ok();return}
const g=document.getElementById('gate');g.hidden=false;
g.querySelector('form').onsubmit=async e=>{e.preventDefault();const v=await sha(g.querySelector('input').value.trim());
 if(v===H){try{localStorage.setItem(K,H)}catch(e){}g.remove();ok()}else{g.querySelector('.er').textContent='Неверный пароль'}};});
</script>
""".replace('@@H@@', H)
out = '<!doctype html>\n<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n<meta name="robots" content="noindex,nofollow">\n' + s.replace('</style>', '</style>\n</head><body>', 1)
i = out.index('<script>')  # gate must run before the page script
out = out[:i] + gate + out[i:] + '\n</body></html>'
open(out_path, 'w').write(out)
print('ok')
