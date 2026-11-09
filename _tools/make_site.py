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
#gate[hidden]{display:none!important}
#gate{position:fixed;inset:0;z-index:999;display:grid;place-items:center;background:var(--bg,#0f0c18);padding:16px}
#gate form{width:100%;max-width:340px;text-align:center}
#gate img{width:64px}#gate h2{font-size:20px;margin:12px 0 4px;letter-spacing:.06em}#gate p{color:var(--muted,#999);font-size:14px;margin:0 0 18px}
#gate input{width:100%;box-sizing:border-box;padding:13px 16px;border-radius:12px;border:1px solid var(--line,#333);background:var(--surface,#1b1726);color:inherit;font-size:16px}
#gate button{margin-top:10px;width:100%;padding:13px;border:0;border-radius:12px;background:#e84a8a;color:#fff;font-size:16px;font-weight:600;cursor:pointer}
#gate .vv{font-size:11px;color:var(--muted,#888);margin-top:18px;opacity:.6}
#gate .er{color:#ff6b6b;font-size:15px;font-weight:600;min-height:20px;margin-top:12px}
#gate form.bad input{border-color:#ff6b6b;animation:sh .3s}@keyframes sh{25%{transform:translateX(-6px)}75%{transform:translateX(6px)}}
</style>
<div id="gate" hidden><form action="javascript:void(0)" onsubmit="return false"><img src="logo.png" alt=""><h2>LOTUS ARENA</h2><p>Материалы · вход по паролю</p><!--v3-->
<input type="password" placeholder="Пароль" autocomplete="current-password" autocapitalize="off" autocorrect="off" spellcheck="false" autofocus><button type="submit">Войти</button><div class="er"></div><div class="vv">версия 4</div></form></div>
<script>
window.GATE=new Promise(ok=>{const H='@@H@@',K='lotus-pass';
const shaJS=t=>{const u=unescape(encodeURIComponent(t)),K=[],H0=[];let n=2,c=0;const f=x=>(x-Math.floor(x))*4294967296|0;
 while(c<64){let p=1;for(let d=2;d*d<=n;d++)if(n%d===0){p=0;break}if(p){if(c<8)H0[c]=f(Math.pow(n,1/2));K[c++]=f(Math.pow(n,1/3))}n++}
 const b=[];for(let i=0;i<u.length;i++)b.push(u.charCodeAt(i));const l=b.length*8;b.push(128);while(b.length%64!==56)b.push(0);
 for(let i=7;i>=0;i--)b.push(i>3?0:(l>>>(i*8))&255);const h=H0.slice(),r=(x,k)=>x>>>k|x<<(32-k);
 for(let o=0;o<b.length;o+=64){const w=[];for(let i=0;i<64;i++){if(i<16)w[i]=b[o+i*4]<<24|b[o+i*4+1]<<16|b[o+i*4+2]<<8|b[o+i*4+3];else{const x=w[i-15],y=w[i-2];w[i]=(w[i-16]+(r(x,7)^r(x,18)^x>>>3)+w[i-7]+(r(y,17)^r(y,19)^y>>>10))|0}}
  let [A,B,C,D,E,F,G,I]=h;for(let i=0;i<64;i++){const t1=(I+(r(E,6)^r(E,11)^r(E,25))+(E&F^~E&G)+K[i]+w[i])|0,t2=((r(A,2)^r(A,13)^r(A,22))+(A&B^A&C^B&C))|0;I=G;G=F;F=E;E=(D+t1)|0;D=C;C=B;B=A;A=(t1+t2)|0}
  [A,B,C,D,E,F,G,I].forEach((v,i)=>h[i]=(h[i]+v)|0)}return h.map(v=>(v>>>0).toString(16).padStart(8,'0')).join('')};
const sha=async t=>{try{if(window.crypto&&crypto.subtle)return [...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(t)))].map(b=>b.toString(16).padStart(2,'0')).join('')}catch(e){}return shaJS(t)};
const norm0=v=>v.replace(/[‐-―−]/g,'-').replace(/\\s+/g,'');
const RU='йцукенгшщзхъфывапролджэячсмитьбю',EN="qwertyuiop[]asdfghjkl;'zxcvbnm,.";
const lat=v=>[...v].map(ch=>{const lo=ch.toLowerCase(),i=RU.indexOf(lo);if(i<0)return ch;const e=EN[i];return ch!==lo?e.toUpperCase():e}).join('');
const norm=v=>lat(norm0(v));
let saved='';try{saved=localStorage.getItem(K)||''}catch(e){}
if(saved!==H){const m=document.cookie.match(/(?:^|; )lotus_pass=([0-9a-f]{64})/);if(m)saved=m[1]}
const keep=()=>{try{localStorage.setItem(K,H)}catch(e){}try{document.cookie='lotus_pass='+H+'; max-age=31536000; path=/; SameSite=Lax; Secure'}catch(e){}};
if(saved===H){keep();const g0=document.getElementById('gate');if(g0)g0.remove();ok();return}
const g=document.getElementById('gate');g.hidden=false;
const go=async e=>{if(e)e.preventDefault();const er=g.querySelector('.er');er.textContent='Проверяю…';let v='';try{v=await sha(norm(g.querySelector('input').value))}catch(x){er.textContent='Ошибка браузера: '+x;return}
 if(v===H){keep();g.remove();ok()}else{const fm=g.querySelector('form');fm.classList.remove('bad');void fm.offsetWidth;fm.classList.add('bad');er.textContent='Неверный пароль. Проверьте большие и маленькие буквы.'}};
const f=g.querySelector('form');f.addEventListener('submit',go);g.querySelector('button').addEventListener('click',go);});
</script>
""".replace('@@H@@', H)
out = '<!doctype html>\n<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n<meta name="robots" content="noindex,nofollow">\n<meta name="theme-color" content="#110e1c">\n<meta name="description" content="Все материалы Lotus Arena: промо артистов, афиши, видео. Пхукет · Паттайя · Нячанг">\n<meta property="og:type" content="website">\n<meta property="og:site_name" content="Lotus Arena">\n<meta property="og:title" content="Lotus Arena — материалы">\n<meta property="og:description" content="Промо артистов, афиши, видео. Пхукет · Паттайя · Нячанг">\n<meta property="og:url" content="https://gerohelr.github.io/lotus-arena/">\n<meta property="og:image" content="https://gerohelr.github.io/lotus-arena/og-image.png">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:image" content="https://gerohelr.github.io/lotus-arena/og-image.png">\n<link rel="icon" href="favicon.ico" sizes="any">\n<link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png">\n<link rel="apple-touch-icon" href="apple-touch-icon.png">\n<link rel="manifest" href="manifest.webmanifest">\n<meta name="apple-mobile-web-app-capable" content="yes">\n<meta name="mobile-web-app-capable" content="yes">\n<meta name="apple-mobile-web-app-title" content="Lotus Arena">\n<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">\n' + s.replace('</style>', '</style>\n</head><body>', 1)
i = out.index('<script>')  # gate must run before the page script
out = out[:i] + gate + out[i:] + '\n</body></html>'
open(out_path, 'w').write(out)
print('ok')
