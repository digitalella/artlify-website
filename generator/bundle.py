# Bundle the built site (dist/) into ONE self-contained HTML file with hash navigation.
import os, re, base64, json
D = "/home/claude/artlify/dist"
OUT = "/home/claude/artlify/single/index.html"
MIME = {"woff2": "font/woff2", "webp": "image/webp", "png": "image/png", "jpg": "image/jpeg", "svg": "image/svg+xml", "mp4": "video/mp4", "ico": "image/x-icon"}
_cache = {}
def data_uri(path):
    path = path.split("?")[0]
    if path not in _cache:
        fp = D + path
        if path.endswith("-1400.webp") and os.path.exists(fp.replace("-1400.webp", "-720.webp")):
            fp = fp.replace("-1400.webp", "-720.webp")
        ext = fp.rsplit(".", 1)[-1]
        _cache[path] = f"data:{MIME[ext]};base64," + base64.b64encode(open(fp, "rb").read()).decode()
    return _cache[path]

def key_for(path):
    path = path.split("?")[0].split("#")[0]
    if path in ("/", ""): return "home"
    return path.strip("/").replace("/", "-")

pages = []
for dp, dn, fn in os.walk(D):
    for f in fn:
        if f == "index.html":
            rel = "/" + os.path.relpath(dp, D).replace(".", "").strip("/")
            rel = "/" if rel == "/" else rel + "/"
            pages.append(rel)
pages.sort(key=lambda p: (p != "/", p))

home = open(D + "/index.html").read()
head = re.search(r"<head>(.*?)</head>", home, re.S).group(1)
header = re.search(r"(<a class=\"skip\".*?</nav>)\s*<main", home, re.S).group(1)
footer = re.search(r"(<footer.*?</footer>)", home, re.S).group(1)

sections = []
for p in pages:
    s = open(D + p + "index.html").read()
    main = re.search(r'<main id="main">(.*?)</main>', s, re.S).group(1)
    title = re.search(r"<title>(.*?)</title>", s).group(1)
    desc = re.search(r'name="description" content="(.*?)"', s).group(1)
    active = re.search(r'aria-current="page">([^<]+)</a>', re.search(r'<ul class="menu">(.*?)</ul>', s, re.S).group(1))
    sections.append(f'<div class="pg" data-key="{key_for(p)}" data-title="{title}" data-desc="{desc}" hidden>{main}</div>')

body = header + "\n<main id=\"main\">\n" + "\n".join(sections) + "\n</main>\n" + footer

def fix_links(html):
    # internal page links -> #key (keep ?service= as data attribute)
    def rep(m):
        url = m.group(1)
        if url.startswith("/assets/") or url.startswith("/favicon") or url.startswith("/apple"): return m.group(0)
        svc = ""
        if "?service=" in url:
            from urllib.parse import unquote
            svc = f' data-svc="{unquote(url.split("?service=")[1])}"'
        return f'href="#{key_for(url)}"{svc}'
    html = re.sub(r'href="(/[^"]*)"', rep, html)
    html = html.replace('href="#home"', 'href="#home"')
    # assets
    html = re.sub(r'srcset="[^"]*"\s*', "", html)
    html = re.sub(r'sizes="[^"]*"\s*', "", html)
    html = re.sub(r'(src|poster)="(/assets/[^"]+)"', lambda m: f'{m.group(1)}="{data_uri(m.group(2))}"', html)
    html = re.sub(r'--m:url\((/assets/[^)]+)\)', lambda m: f'--m:url({data_uri(m.group(1))})', html)
    return html

body = fix_links(body)
body = body.replace('href="#" id="toTop"', 'href="#home" id="toTop"')

css = open(D + "/assets/site.css").read()
css = re.sub(r"url\((fonts/[^)]+)\)", lambda m: f"url({data_uri('/assets/' + m.group(1))})", css)
css += "\n.pg[hidden]{display:none}\n"
js = open(D + "/assets/site.js").read()

router = r"""
(function(){
  var pages={}; document.querySelectorAll('.pg').forEach(function(p){pages[p.dataset.key]=p});
  var md=document.querySelector('meta[name="description"]');
  var navMap={'about':'about','services':'services','work':'work','blog':'blog'};
  function dec(s){var t=document.createElement('textarea');t.innerHTML=s;return t.value}
  function route(){
    var k=(location.hash||'').slice(1)||'home';
    if(k==='main') return;
    if(!pages[k]) k=pages[k.split('-')[0]]?k.split('-')[0]:'home';
    Object.keys(pages).forEach(function(x){pages[x].hidden=x!==k});
    document.title=dec(pages[k].dataset.title); if(md) md.content=dec(pages[k].dataset.desc);
    var top=k.split('-')[0]; if(k.indexOf('work-with-us')===0) top='wwu';
    document.querySelectorAll('.menu>li>a').forEach(function(a){var h=(a.getAttribute('href')||'').slice(1); var on=h===top; a.classList.toggle('on',on); if(on)a.setAttribute('aria-current','page'); else a.removeAttribute('aria-current')});
    document.body.classList.remove('menu-open'); var b=document.querySelector('.burger'); if(b)b.setAttribute('aria-expanded','false');
    window.scrollTo(0,0);
    pages[k].querySelectorAll('.rv:not(.in)').forEach(function(el){ if(el.getBoundingClientRect().top<innerHeight) el.classList.add('in') });
  }
  addEventListener('hashchange',route);
  document.addEventListener('click',function(e){
    var a=e.target.closest('a[data-svc]'); if(!a) return;
    var c=document.querySelector('#enq input[name=services][value="'+a.dataset.svc.replace(/"/g,'')+'"]'); if(c) c.checked=true;
  });
  route();
})();
"""

head = re.sub(r'<link rel="preload"[^>]*>\s*', "", head)
head = re.sub(r'<link rel="stylesheet"[^>]*>', f"<style>{css}</style>", head)
head = re.sub(r'<link rel="(icon|apple-touch-icon|manifest)"[^>]*>\s*', "", head)
head = head.replace("</title>", "</title>\n<link rel=\"icon\" type=\"image/png\" href=\"" + data_uri("/assets/img/favicon-96.png") + "\">", 1)

doc = f"""<!DOCTYPE html>
<html lang="en" class="no-js">
<head>{head}</head>
<body>
{body}
<script>{js}</script>
<script>{router}</script>
</body>
</html>
"""
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w").write(doc)
print("pages:", len(pages), "size KB:", os.path.getsize(OUT) // 1024)
