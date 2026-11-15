# -*- coding: utf-8 -*-
"""Static site generator for Artlify.  python3 build.py [netlify|preview]"""
import os, sys, json, shutil, hashlib, html
from urllib.parse import quote
from content import SITE, SERVICES, AUDIENCES, PROCESS, WHY, ENGAGEMENTS, IMPACT, FAQS, AUTHOR, CATEGORIES

MODE = sys.argv[1] if len(sys.argv) > 1 else "netlify"
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "dist" if MODE == "netlify" else "preview")
BASE = SITE["url"].rstrip("/")
E = lambda s: html.escape(str(s), quote=True)

COL = {"orange": ("var(--orange)", False), "gold": ("var(--gold)", False), "sage": ("var(--sage)", False),
       "peach": ("var(--peach)", False), "lemon": ("var(--lemon)", False), "teal": ("var(--teal)", True),
       "lpeach": ("var(--lpeach)", False), "cream": ("var(--paper)", False), "ink": ("var(--ink)", True)}
ICON_EXT = {"pen": "svg", "bolt": "svg"}

def sha(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()[:8]

class Page:
    def __init__(self, path):
        self.path = path  # e.g. "/" or "/services/paid-ads/"
        self.depth = 0 if path == "/" else path.strip("/").count("/") + 1
    def href(self, target):
        """link to a site path (with optional ?query / #hash)"""
        if target.startswith(("http", "mailto:", "#")): return target
        q = ""
        for sep in ("?", "#"):
            if sep in target:
                target, rest = target.split(sep, 1); q = sep + rest; break
        if MODE == "netlify": return target + q
        rel = "../" * self.depth
        if target.endswith("/"): return rel + target.lstrip("/") + "index.html" + q
        return rel + target.lstrip("/") + q
    def asset(self, a):
        return self.href("/assets/" + a)

def icon(p, name, cls="ic", style=""):
    url = p.asset(f"icons/{name}.{ICON_EXT.get(name, 'png')}")
    return f'<span class="{cls}" style="{style}" aria-hidden="true"><i style="--m:url({url})"></i></span>'

BRANDMARK = '<svg viewBox="0 0 300 323" aria-hidden="true"><path d="M100 96V46a46 46 0 0 1 92 0v50z" fill="#DF8919"/><path d="M45 187v-46.5a47.5 47.5 0 0 1 95 0V187zM155 187v-46.5a47.5 47.5 0 0 1 95 0V187z" fill="#F0B83D"/><path d="M7 216h17C34 282 88 312 150 312s116-30 126-96h17" fill="none" stroke="currentColor" stroke-width="15" stroke-linecap="round" stroke-linejoin="round"/></svg>'

def logo(p, dark=False):
    return f'<a href="{p.href("/")}" class="logo" aria-label="Artlify home"><span style="color:{"#F1EAD8" if dark else "#1C1913"}">{BRANDMARK}</span><span><b>Artlify</b><small>Marketing Agency</small></span></a>'

def org_schema():
    same = [u for u in (SITE["instagram"], SITE["linkedin"]) if u]
    o = {"@type": "Organization", "@id": BASE + "/#organization", "name": SITE["name"], "alternateName": SITE["legal_name"],
         "url": BASE + "/", "logo": {"@type": "ImageObject", "url": BASE + "/assets/img/icon-512.png", "width": 512, "height": 512},
         "image": BASE + "/assets/img/og-image.jpg", "description": SITE["description"], "foundingDate": SITE["founded"],
         "areaServed": "Worldwide",
         "knowsAbout": [s["name"] for s in SERVICES] + ["Digital marketing", "Marketing for coaches", "E-commerce marketing"],
         "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Marketing services", "itemListElement": [
             {"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["name"], "url": f'{BASE}/services/{s["slug"]}/'}} for s in SERVICES]}}
    if same: o["sameAs"] = same
    if SITE["email"] or SITE.get("phone"):
        cp = {"@type": "ContactPoint", "contactType": "sales", "availableLanguage": ["English"]}
        if SITE["email"]: cp["email"] = SITE["email"]
        if SITE.get("phone"): cp["telephone"] = SITE["phone"]
        o["contactPoint"] = cp
    return o

def crumbs_schema(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + u} for i, (n, u) in enumerate(items)]}

def faq_schema(faqs):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}

def crumbs_html(p, items):
    parts = []
    for i, (n, u) in enumerate(items):
        if i: parts.append('<span aria-hidden="true">/</span>')
        parts.append(f'<a href="{p.href(u)}">{E(n)}</a>' if i < len(items) - 1 else f'<span aria-current="page">{E(n)}</span>')
    return f'<nav class="crumbs" aria-label="Breadcrumb">{"".join(parts)}</nav>'

def header(p, active):
    def a(label, url, key):
        return f'<a href="{p.href(url)}"{" class=\"on\" aria-current=\"page\"" if key == active else ""}>{label}</a>'
    drop = "".join(f'<a href="{p.href("/services/" + s["slug"] + "/")}">{icon(p, s["icon"], style="--bgc:" + COL[s["color"]][0] + (";--fgc:var(--cream)" if COL[s["color"]][1] else ""))}{E(s["name"])}</a>' for s in SERVICES)
    subs = "".join(f'<a href="{p.href("/services/" + s["slug"] + "/")}">{E(s["short"])}</a>' for s in SERVICES)
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="hdr"><div class="wrap nav">{logo(p)}
<nav aria-label="Main"><ul class="menu">
<li>{a("About Us", "/about/", "about")}</li>
<li><a href="{p.href("/services/")}"{' class="on"' if active == "services" else ""} aria-haspopup="true">Services <span class="caret" aria-hidden="true"></span></a><div class="drop">{drop}<a class="all" href="{p.href("/services/")}">All services →</a></div></li>
<li>{a("Work", "/work/", "work")}</li>
<li>{a("Blog", "/blog/", "blog")}</li>
</ul></nav>
<a href="{p.href("/work-with-us/")}" class="btn b-or desk">Work With Us <span class="arr">→</span></a>
<button class="burger" aria-label="Open menu" aria-expanded="false" aria-controls="mnav"><i></i><i></i></button>
</div></header>
<nav class="mnav" id="mnav" aria-label="Mobile">
<a href="{p.href("/about/")}" style="background:var(--peach)">About Us <span>→</span></a>
<a href="{p.href("/services/")}" style="background:var(--lemon)">Services <span>→</span></a>
<div class="subs">{subs}</div>
<a href="{p.href("/work/")}" style="background:var(--sage)">Work <span>→</span></a>
<a href="{p.href("/blog/")}" style="background:var(--lpeach)">Blog <span>→</span></a>
<a href="{p.href("/work-with-us/")}" style="background:var(--ink);color:var(--cream)">Work With Us <span>→</span></a>
</nav>'''

SOC = {
 "ig": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/></svg>',
 "li": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9.75h4V21H3zM9.5 9.75h3.8v1.6h.06c.53-1 1.84-2.06 3.79-2.06 4.05 0 4.8 2.67 4.8 6.13V21h-4v-4.98c0-1.19-.02-2.72-1.66-2.72-1.66 0-1.92 1.3-1.92 2.63V21h-4z"/></svg>',
 "em": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="5" width="18" height="14" rx="3"/><path d="m4 7 8 6 8-6"/></svg>',
 "wa": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38c1.45.79 3.08 1.21 4.74 1.21 5.46 0 9.91-4.45 9.91-9.91C21.95 6.45 17.5 2 12.04 2zm0 18.15c-1.48 0-2.93-.4-4.2-1.15l-.3-.18-3.12.82.83-3.04-.2-.31a8.25 8.25 0 0 1-1.26-4.38c0-4.54 3.7-8.24 8.25-8.24 4.54 0 8.24 3.7 8.24 8.24 0 4.55-3.7 8.24-8.24 8.24zm4.52-6.16c-.25-.12-1.47-.72-1.69-.81-.23-.08-.39-.12-.56.12-.17.25-.64.81-.78.97-.14.17-.29.19-.54.06-.25-.12-1.05-.39-1.99-1.23-.74-.66-1.23-1.47-1.38-1.72-.14-.25-.02-.38.11-.51.11-.11.25-.29.37-.43.13-.15.17-.25.25-.42.08-.17.04-.31-.02-.43-.06-.12-.56-1.34-.76-1.84-.2-.48-.41-.42-.56-.43h-.48c-.17 0-.43.06-.66.31-.22.25-.86.85-.86 2.07 0 1.22.89 2.4 1.01 2.56.12.17 1.75 2.67 4.23 3.74.59.26 1.05.41 1.41.52.59.19 1.13.16 1.56.1.48-.07 1.47-.6 1.67-1.18.21-.58.21-1.08.14-1.18-.06-.11-.22-.17-.47-.29z"/></svg>',
}

def footer(p):
    ig = SITE["instagram"] or "#"; li = SITE["linkedin"] or "#"
    em = ("mailto:" + SITE["email"]) if SITE["email"] else p.href("/work-with-us/")
    ext = lambda u: ' target="_blank" rel="noopener"' if u.startswith("http") else ""
    svc = "".join(f'<a href="{p.href("/services/" + s["slug"] + "/")}">{E(s["name"])}</a>' for s in SERVICES[:6])
    ph = SITE.get("phone", ""); wa = "https://wa.me/" + ph.lstrip("+") if ph else ""
    wa_icon = f'<a href="{wa}" target="_blank" rel="noopener" aria-label="Chat with Artlify on WhatsApp">{SOC["wa"]}</a>' if ph else ""
    phone_line = (f'<p class="f-contact">Call or WhatsApp: <a href="tel:{ph}">{E(SITE["phone_display"])}</a><br>Email: <a href="mailto:{E(SITE["email"])}">{E(SITE["email"])}</a></p>') if ph else ""
    wa_float = (f'<a class="wa-float" href="{wa}?text=' + quote("Hi Artlify, I'd like to talk about growing my business.") + f'" target="_blank" rel="noopener" aria-label="Chat with Artlify on WhatsApp">{SOC["wa"]}</a>') if ph else ""
    return f'''<footer class="ftr"><div class="wrap">
<div class="f-cta">
<span class="eyebrow" style="color:#B3A894">Let’s grow together</span>
<h2>Ready to be <span class="c-le">impossible to ignore?</span></h2>
<p class="lead">Tell us about your brand and goals. We’ll come back with ideas, a plan and the right next step — no pressure, no templates.</p>
<div class="cta-row dark" style="background:none"><a href="{p.href("/work-with-us/")}" class="btn b-le" style="border-color:var(--lemon)">Work With Us <span class="arr">→</span></a><a href="{p.href("/services/")}" class="btn b-gh">Explore Services <span class="arr">→</span></a></div>
<a class="badge" href="{p.href("/work-with-us/")}" aria-label="Start a project"><svg viewBox="0 0 200 200" aria-hidden="true"><defs><path id="fc" d="M100,100 m-80,0 a80,80 0 1,1 160,0 a80,80 0 1,1 -160,0"/></defs><circle cx="100" cy="100" r="98" fill="#DF8919"/><text font-family="Garute, sans-serif" font-weight="600" font-size="13" fill="#1C1913"><textPath href="#fc" textLength="498" lengthAdjust="spacing">WORK WITH ARTLIFY ✦ WORK WITH ARTLIFY ✦</textPath></text></svg><b>↗</b></a>
</div>
<div class="f-grid">
<div class="f-brand">{logo(p, True)}<p>A full-service marketing agency helping coaches and growing brands with strategy, social, content, ads, funnels and automation.</p>
<div class="socials"><a href="{ig}"{ext(ig)} aria-label="Artlify on Instagram">{SOC["ig"]}</a><a href="{li}"{ext(li)} aria-label="Artlify on LinkedIn">{SOC["li"]}</a><a href="{em}" aria-label="Email Artlify">{SOC["em"]}</a>{wa_icon}</div>{phone_line}</div>
<div class="f-col big"><h4>Explore</h4><a href="{p.href("/about/")}">About</a><a href="{p.href("/services/")}">Services</a><a href="{p.href("/work/")}">Work</a><a href="{p.href("/blog/")}">Blog</a><a href="{p.href("/work-with-us/")}">Contact</a></div>
<div class="f-col sm"><h4>Services</h4>{svc}<a href="{p.href("/services/")}">All services →</a></div>
<div class="f-col sm"><h4>Studio</h4><a href="{p.href("/work-with-us/")}">Work With Us</a><a href="{p.href("/faq/")}">FAQ</a><a href="{p.href("/terms/")}">Terms &amp; Conditions</a><a href="{p.href("/privacy/")}">Privacy Policy</a></div>
</div>
<div class="f-word" aria-hidden="true">{"".join(f"<span>{c}</span>" for c in "Artlify")}</div>
</div>
<div class="wrap f-bot"><span>© 2026 Artlify Agency. All rights reserved.</span><nav aria-label="Legal"><a href="{p.href("/terms/")}">Terms &amp; Conditions</a><a href="{p.href("/privacy/")}">Privacy Policy</a><a href="#" id="toTop">Back to top ↑</a></nav></div>
</footer>
{wa_float}'''

PAGES = []  # (path, priority, indexable)

def write(path, title, desc, body, active="", schema=None, og_type="website", noindex=False, priority="0.7", preload_img=None, lastmod=None):
    p = Page(path)
    css_v = sha(os.path.join(ROOT, "src/assets/site.css")); js_v = sha(os.path.join(ROOT, "src/assets/site.js"))
    url = BASE + path
    graph = [{"@type": "WebSite", "@id": BASE + "/#website", "url": BASE + "/", "name": SITE["name"], "publisher": {"@id": BASE + "/#organization"}, "inLanguage": "en"},
             org_schema()] + (schema or [])
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    pre = f'<link rel="preload" as="image" href="{p.asset(preload_img)}" fetchpriority="high">' if preload_img else ""
    doc = f'''<!DOCTYPE html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="{"noindex, follow" if noindex else "index, follow, max-image-preview:large, max-snippet:-1"}">
<meta name="theme-color" content="#F1EAD8">
<meta name="author" content="{E(AUTHOR["name"]) if og_type == "article" else "Artlify Agency"}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Artlify">
<meta property="og:locale" content="en_GB">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/assets/img/og-image.jpg">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Artlify — marketing that makes brands grow">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{E(title)}">
<meta name="twitter:description" content="{E(desc)}">
<meta name="twitter:image" content="{BASE}/assets/img/og-image.jpg">
<link rel="icon" href="{p.href("/favicon.ico")}" sizes="48x48">
<link rel="icon" type="image/png" sizes="96x96" href="{p.asset("img/favicon-96.png")}">
<link rel="apple-touch-icon" href="{p.href("/apple-touch-icon.png")}">
<link rel="manifest" href="{p.href("/site.webmanifest")}">
<link rel="alternate" type="application/rss+xml" title="Artlify Blog" href="{BASE}/blog/feed.xml">
<link rel="preload" href="{p.asset("fonts/lost-sarafin.woff2")}" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{p.asset("fonts/garute-400.woff2")}" as="font" type="font/woff2" crossorigin>
{pre}
<link rel="stylesheet" href="{p.asset("site.css")}?v={css_v}">
<script type="application/ld+json">{ld}</script>
</head>
<body>
{header(p, active)}
<main id="main">
{body(p)}
</main>
{footer(p)}
<script src="{p.asset("site.js")}?v={js_v}" defer></script>
</body>
</html>
'''
    fp = os.path.join(OUT, path.strip("/"), "index.html") if path != "/404" else os.path.join(OUT, "404.html")
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, "w").write(doc)
    if not noindex and path != "/404": PAGES.append((path, priority, lastmod or SITE["updated"]))

def img(p, name, alt, cls="", w=1400, h=933, eager=False, sizes="(max-width: 1000px) 100vw, 50vw"):
    return (f'<img class="{cls}" src="{p.asset(f"img/{name}-1400.webp")}" srcset="{p.asset(f"img/{name}-720.webp")} 720w, {p.asset(f"img/{name}-1400.webp")} 1400w" '
            f'sizes="{sizes}" width="{w}" height="{h}" alt="{E(alt)}" {"fetchpriority=\"high\"" if eager else "loading=\"lazy\""} decoding="async">')

from PIL import Image as _I
_SH = {n: _I.open(os.path.join(ROOT, f"src/assets/img/shape-{n}.webp")).size for n in range(1, 9)}
def shape(p, n, alt="", cls="", w=None):
    sw, sh = _SH[n]
    return f'<img class="{cls}" src="{p.asset(f"img/shape-{n}.webp")}" alt="{alt}" width="{sw}" height="{sh}" loading="lazy" decoding="async">'

def colstyle(c):
    bg, dk = COL[c]; return f'--bg:{bg}', dk

def svc_card(p, s, wide=False, tag="h3"):
    st, dk = colstyle(s["color"])
    return (f'<a href="{p.href("/services/" + s["slug"] + "/")}" class="svc rv{" wide" if wide else ""}{" dk" if dk else ""}" style="{st}">'
            f'{icon(p, s["icon"])}<span class="go" aria-hidden="true">→</span><{tag}>{E(s["name"])}</{tag}><p>{E(s["card"])}</p></a>')

def faq_html(faqs):
    return "".join(f'<details class="qa"{" open" if i == 0 else ""}><summary>{E(q)}<span class="pm" aria-hidden="true"></span></summary><div class="ans"><p>{E(a)}</p></div></details>' for i, (q, a) in enumerate(faqs))

def stats_html():
    return "".join(f'<div class="stat rv d{i}"><div class="v">{v}</div><div class="lb">{E(l)}</div></div>' for i, (v, l) in enumerate(IMPACT))

def testimonials_html():
    one = '<div class="tc rv"><span class="q" aria-hidden="true">“</span><p>[Insert verified client testimonial here, with permission.]</p><div class="who"><span class="av"></span><div style="flex:1"><div class="ln" style="width:60%"></div><div class="ln" style="width:38%;margin-top:8px"></div></div></div></div>'
    return one * 3

def band(p, h, btn="Work With Us", url="/work-with-us/"):
    return f'<section class="s dark" style="padding:clamp(60px,8vw,100px) 0"><div class="wrap band"><h2 class="rv">{h}</h2><a href="{p.href(url)}" class="btn b-le rv d1" style="border-color:var(--lemon)">{btn} <span class="arr">→</span></a></div></section>'

def phero(p, eyebrow, h1, leads, crumbs, decos=(6, 3, 7)):
    d = "".join(f'<span class="deco z{i+1}" aria-hidden="true">{shape(p, n)}</span>' for i, n in enumerate(decos))
    ls = "".join(f'<p class="lead rv d2">{l}</p>' for l in leads)
    return f'<section class="ph">{d}<div class="wrap">{crumbs_html(p, crumbs)}<span class="pill rv"><i></i>{eyebrow}</span><h1 class="rv d1">{h1}</h1>{ls}</div></section>'

# =================================================================== HOME
def home(p):
    spans = [True, False, False, False, False, False, True, False, False, False]
    svc = "".join(svc_card(p, s, w) for s, w in zip(SERVICES, spans))
    tabs = "".join(f'<button class="tab" role="tab" id="t-{k}" aria-controls="p-{k}" aria-selected="{"true" if i == 0 else "false"}" tabindex="{0 if i == 0 else -1}">For {E(n)}</button>' for i, (k, n, w, c, t) in enumerate(AUDIENCES))
    shapes_for = {"coaches": 2, "ecommerce": 6, "business": 8}
    panels = "".join(f'''<div class="panel" role="tabpanel" id="p-{k}" aria-labelledby="t-{k}"{"" if i == 0 else " hidden"}>
<div class="l"><h3>{E(n)}</h3><p>{E(t)}</p><div><a href="{p.href("/work-with-us/")}" class="btn b-ink">Let’s talk growth <span class="arr">→</span></a></div></div>
<div class="r" style="--bg:{COL[c][0]};{"color:var(--cream)" if COL[c][1] else ""}">{shape(p, shapes_for[k], cls="", w=360).replace('class=""', 'style="right:-6%;bottom:-8%"')}<span class="word">{w.replace(" ", "<br>")}</span></div></div>''' for i, (k, n, w, c, t) in enumerate(AUDIENCES))
    why = "".join(f'<div class="wy rv d{i}"><span class="n">{i+1}</span><h3>{E(h)}</h3><p>{E(t)}</p></div>' for i, (h, t) in enumerate(WHY))
    pcols = ["var(--peach)", "var(--lemon)", "var(--orange)", "var(--sage)", "var(--lpeach)"]
    proc = "".join(f'<div class="st rv d{i}" style="--bg:{pcols[i]}"><span class="k">0{i+1}</span><h3>{E(h)}</h3><p>{E(t)}</p></div>' for i, (h, t) in enumerate(PROCESS))
    ecol = [("var(--sage)", ""), ("var(--teal)", " f"), ("var(--lemon)", "")]
    eng = "".join(f'<div class="en rv d{i}{ecol[i][1]}" style="--bg:{ecol[i][0]}"><span class="k">{E(k)}</span><h3>{E(h)}</h3><p>{E(t)}</p></div>' for i, (k, h, t) in enumerate(ENGAGEMENTS))
    marq = "".join(f"<span>{E(s['short'])}</span>" for s in SERVICES) * 2
    ring = '<svg class="ring" viewBox="0 0 200 200" aria-hidden="true"><defs><path id="circ" d="M100,100 m-88,0 a88,88 0 1,1 176,0 a88,88 0 1,1 -176,0"/></defs><text font-family="Garute, sans-serif" font-weight="600" font-size="11" fill="#1C1913"><textPath href="#circ" textLength="548" lengthAdjust="spacing">ARTLIFY ✦ STRATEGY ✦ CONTENT ✦ SOCIAL ✦ ADS ✦ FUNNELS ✦ AUTOMATION ✦</textPath></text></svg>'
    return f'''
<section class="hero"><div class="wrap hero-grid">
<div>
<span class="pill rv"><i></i>Full-service marketing agency</span>
<h1 class="rv d1">The marketing agency that makes coaches &amp; brands <span class="hl">impossible to ignore.</span></h1>
<p class="lead rv d2">Strategy, social media, content, copy, paid ads, funnels and automation — personalised to your brand, never copied from a template.</p>
<div class="cta-row rv d3"><a href="{p.href("/services/")}" class="btn b-ink">Our Services <span class="arr">→</span></a><a href="{p.href("/work/")}" class="btn b-or">See Our Work <span class="arr">→</span></a></div>
<p class="alt rv d4">Ready to grow? <a href="{p.href("/work-with-us/")}" class="txtlink">Work with us <span>→</span></a></p>
</div>
<div class="stage rv d2">
<div class="arch">{img(p, "team-smiling", "The Artlify team celebrating a successful marketing campaign with a client", eager=True, sizes="(max-width: 1000px) 80vw, 420px")}</div>
<div class="float f-shape" style="width:24%;right:0;top:0">{shape(p, 6)}</div>
<div class="float f-shape" style="width:13%;left:6%;top:2%;animation-delay:-2s">{shape(p, 3)}</div>
<div class="float f-shape" style="width:20%;right:4%;bottom:-2%;animation-delay:-3s">{shape(p, 7)}</div>
<div class="float post" style="left:-2%;top:16%;transform:rotate(-5deg)" aria-hidden="true"><div class="pt"><span>{BRANDMARK}</span>Artlify</div><div class="bd" style="background:var(--lemon)"><b>How good is your content strategy?</b><em>Read caption</em></div><div class="ft">♥ ✦ ↗</div></div>
<div class="float growth" style="right:-3%;top:44%" aria-hidden="true"><div class="t"><span>Growth</span><span>↗</span></div><div class="bars"><i></i><i></i><i></i><i></i><i></i><i></i></div></div>
<div class="float notif" style="left:2%;bottom:9%" aria-hidden="true"><span class="dot">{icon(p, "chat", cls="ic", style="background:none;width:100%;height:100%;--fgc:var(--cream)")}</span><span>New enquiry<small>just now · via your funnel</small></span></div>
<span class="chip" style="top:-2%;left:36%;background:var(--peach);transform:rotate(-4deg)">Social</span>
<span class="chip" style="top:30%;right:-5%;background:var(--sage);transform:rotate(5deg);animation-delay:-1.4s">Ads</span>
<span class="chip" style="bottom:-1%;left:40%;background:var(--paper);transform:rotate(-3deg);animation-delay:-2.6s">Funnels</span>
</div>
</div></section>

<div class="marq" aria-hidden="true"><div class="tr">{marq}</div></div>

<section class="s"><div class="wrap intro">
<div>
<span class="eyebrow rv">Why Artlify</span>
<h2 class="rv d1" style="margin-top:18px">No templates. Just marketing that <span class="c-or">fits.</span></h2>
<p class="big rv d2">There is no one-size-fits-all approach to marketing — so we don’t sell one.</p>
<p class="rv">Artlify is a full-stack marketing agency for coaches and growing brands. We take the time to understand your business, your audience and your goals, then build a personalised marketing system around them: the right strategy, the right content, the right channels and the follow-up that turns attention into revenue.</p>
<p class="rv">Sociable, organised and seriously strategic — we make marketing feel collaborative again.</p>
<div class="cta-row rv" style="margin-top:28px"><a href="{p.href("/about/")}" class="btn">About Us <span class="arr">→</span></a></div>
</div>
<div class="seal rv d2" aria-hidden="true">{ring}<div class="disc"><p>Marketing with personality.</p></div>{shape(p, 6, cls="smile")}</div>
</div></section>

<section class="s" style="padding-top:0"><div class="wrap">
<div class="sec-head"><div><span class="eyebrow rv">Our services</span><h2 class="rv d1">Everything marketing. <span class="c-te">One team.</span></h2></div><p class="lead rv d2">From the first strategy session to the automation that follows up while you sleep — choose one service or combine them into a complete growth system.</p></div>
<div class="svc-grid">{svc}</div>
<div class="cta-row rv" style="margin-top:34px"><a href="{p.href("/services/")}" class="btn b-ink">Explore All Services <span class="arr">→</span></a></div>
</div></section>

<section class="s" style="background:var(--cream2)"><div class="wrap">
<div class="sec-head"><div><span class="eyebrow rv">Who we work with</span><h2 class="rv d1">Built around <span class="c-or">your</span> growth.</h2></div><p class="lead rv d2">Different businesses, different goals. A marketing approach shaped around each.</p></div>
<div class="tabs rv" role="tablist" aria-label="Who we work with">{tabs}</div>
{panels}
</div></section>

<section class="s dark" style="background:var(--teal)"><div class="wrap">
<div class="sec-head"><div><span class="eyebrow rv" style="color:var(--lemon)">The Artlify difference</span><h2 class="rv d1">Strategic like an agency. <span class="c-le">Personal like a partner.</span></h2></div></div>
<div class="why">{why}</div>
</div></section>

<section class="s"><div class="wrap">
<div class="sec-head"><div><span class="eyebrow rv">How we work</span><h2 class="rv d1">A clear process. <span class="c-or">Real momentum.</span></h2></div><a href="{p.href("/work-with-us/")}" class="btn b-ink rv d2">Start Your Project <span class="arr">→</span></a></div>
<div class="proc">{proc}</div>
</div></section>

<section class="s" style="padding-top:0"><div class="wrap">
<div class="sec-head"><div><span class="eyebrow rv">Ways to work together</span><h2 class="rv d1">Support that fits <span class="c-te">your stage.</span></h2></div><p class="lead rv d2">Start with one service or combine several. Every option is a monthly retainer with a three-month minimum.</p></div>
<div class="eng">{eng}</div>
<div class="eng-foot rv"><p>Every engagement starts with understanding your goals.</p><a href="{p.href("/work-with-us/")}" class="btn b-le" style="border-color:var(--lemon)">Find Your Fit <span class="arr">→</span></a></div>
</div></section>

<section class="s" style="background:var(--lpeach)"><div class="wrap">
<div class="sec-head"><div><span class="eyebrow rv">Client love</span><h2 class="rv d1">In their words.</h2></div><p class="lead rv d2">We value the relationships behind the results as much as the results themselves.</p></div>
<div class="tg">{testimonials_html()}</div>
</div></section>

<section class="s impact"><div class="wrap">
<div class="sec-head"><div><span class="eyebrow rv" style="color:var(--cream)">Our impact</span><h2 class="rv d1">Results that <span class="c-le">speak.</span></h2></div><p class="lead rv d2" style="color:#E3EDE6">What strategic, personalised marketing has helped our clients achieve.</p></div>
<div class="stats">{stats_html()}</div>
</div></section>

<section class="s feat"><span class="bgword" aria-hidden="true">Featured</span><div class="wrap feat-grid">
<div>
<span class="eyebrow rv">Featured work</span>
<h2 class="rv d1">Content that <span class="c-or">converts.</span></h2>
<p class="lead rv d2">A look at the kind of scroll-stopping, on-brand content we create — designed to educate, build trust and turn followers into clients.</p>
<div class="cta-row rv d3" style="margin-top:30px"><a href="{p.href("/work/")}" class="btn b-ink">View Full Work <span class="arr">→</span></a></div>
<div class="meta-card rv d3"><dl>
<div><dt>Client</dt><dd class="phx">[Client / brand name]</dd></div>
<div><dt>Services</dt><dd>Content Strategy · Social Media</dd></div>
<div><dt>The goal</dt><dd class="phx">[What the client wanted to achieve]</dd></div>
<div><dt>The result</dt><dd class="phx">[Verified results, with permission]</dd></div>
</dl></div>
</div>
<div class="phone-wrap rv d1"><span class="b1" aria-hidden="true"></span><span class="b2" aria-hidden="true">{shape(p, 6)}</span>
<div class="phone"><div class="screen"><span class="notch" aria-hidden="true"></span>
<video data-autoplay muted loop playsinline preload="none" poster="{p.asset("img/reel-poster.webp")}" width="540" height="960" aria-label="Looping preview of Artlify social media carousel designs"><source src="{p.asset("img/reel.mp4")}" type="video/mp4"></video>
</div></div></div>
</div></section>

<section class="s" style="padding-top:0"><div class="wrap faq">
<div class="side"><span class="eyebrow">FAQ</span><h2 style="margin:18px 0 18px">Questions, <span class="c-or">answered.</span></h2><p class="lead">Everything you need to know before we start growing together.</p><div class="cta-row" style="margin-top:26px"><a href="{p.href("/faq/")}" class="btn">All FAQs <span class="arr">→</span></a></div></div>
<div>{faq_html(FAQS[:5])}</div>
</div></section>
'''

# =================================================================== SERVICES INDEX
def services_index(p):
    spans = [True, False, False, False, False, False, True, False, False, False]
    cards = "".join(svc_card(p, s, w, "h2") for s, w in zip(SERVICES, spans))
    return phero(p, "Our services", 'Full-stack marketing, <span class="c-or">personalised</span> to your brand.',
                 ["Choose a single service or combine several into one growth system. Every engagement is built around your audience, your offer and your goals."],
                 [("Home", "/"), ("Services", "/services/")]) + f'''
<section class="s" style="padding-top:10px"><div class="wrap"><div class="svc-grid">{cards}</div></div></section>
<section class="s" style="background:var(--cream2)"><div class="wrap split">
<div><span class="eyebrow rv">Better together</span><h2 class="rv d1" style="margin:18px 0 20px">One team. <span class="c-te">Every channel.</span></h2>
<p class="lead rv d2">When strategy, content, ads, funnels and automation are planned together, every part makes the others work harder. No gaps between agencies, no mixed messages — just one connected marketing system.</p>
<div class="cta-row rv d3" style="margin-top:28px"><a href="{p.href("/work-with-us/")}" class="btn b-or">Build My Growth System <span class="arr">→</span></a></div></div>
<div class="photo-frame rv d1">{img(p, "strategy-board", "Marketing strategy planning board with sticky notes", w=1400, h=2100)}</div>
</div></section>
''' + band(p, 'Not sure what you need? <span class="c-le">Let’s figure it out.</span>')

# =================================================================== SERVICE PAGE
def service_page(s):
    def body(p):
        st, dk = colstyle(s["color"])
        inc = "".join(f"<li>{E(x)}</li>" for x in s["included"])
        intro = "".join(f"<p>{E(x)}</p>" for x in s["intro"])
        tags = f'<div class="tagrow">{"".join(f"<span>{E(t)}</span>" for t in s["platforms"])}</div>' if s["platforms"] else ""
        others = [o for o in SERVICES if o["slug"] != s["slug"]]
        idx = SERVICES.index(s); rel = [others[(idx + k) % len(others)] for k in range(3)]
        relh = "".join(f'<a href="{p.href("/services/" + r["slug"] + "/")}" class="rel rv{" dk" if COL[r["color"]][1] else ""}" style="--bg:{COL[r["color"]][0]}">{icon(p, r["icon"])}<h3>{E(r["name"])}</h3><p style="font-size:15px">{E(r["card"])}</p></a>' for r in rel)
        cta = p.href("/work-with-us/?service=" + quote(s["name"]))
        audience = "".join(f'<li><strong>{E(n)}</strong> — {E(t.split(".")[0])}.</li>' for k, n, w, c, t in AUDIENCES)
        return f'''
<section class="ph"><span class="deco z1" aria-hidden="true">{shape(p, 6)}</span><div class="wrap sv-hero">
<div>{crumbs_html(p, [("Home", "/"), ("Services", "/services/"), (s["name"], f'/services/{s["slug"]}/')])}
<div class="rv" style="display:flex;align-items:center;gap:16px;margin-bottom:6px">{icon(p, s["icon"], style=st.replace("--bg", "--bgc") + (";--fgc:var(--cream)" if dk else ""))}<span class="pill"><i></i>{E(s["name"])}</span></div>
<h1 class="rv d1" style="font-size:clamp(42px,5.6vw,80px)">{E(s["h1"])}</h1>
<p class="lead rv d2">{E(s["meta"])}</p>
<div class="cta-row rv d3" style="margin-top:30px"><a href="{cta}" class="btn b-ink">Get a Proposal <span class="arr">→</span></a><a href="{p.href("/work/")}" class="btn">See Our Work <span class="arr">→</span></a></div>
</div>
<div class="sv-card rv d2{" dk" if dk else ""}" style="{st}"><h2>What’s included</h2><ul>{inc}</ul></div>
</div></section>
<section class="s" style="padding-top:10px"><div class="wrap sv-body">
<div><span class="eyebrow rv">Overview</span><h2 class="rv d1" style="margin-top:18px">{E(s["name"])}, the <span class="c-or">Artlify</span> way.</h2></div>
<div class="txt rv d2">{intro}{tags}</div>
</div></section>
<section class="s" style="background:var(--cream2)"><div class="wrap sv-body">
<div><span class="eyebrow rv">Who it’s for</span><h2 class="rv d1" style="margin-top:18px">Made for brands ready to grow.</h2></div>
<div class="txt rv d2"><ul class="prose" style="font-size:18px">{audience}</ul><p>Every {E(s["name"].lower())} engagement is personalised — we shape the scope, channels and deliverables around your business, never a fixed template.</p></div>
</div></section>
<section class="s"><div class="wrap faq">
<div class="side"><span class="eyebrow">FAQ</span><h2 style="margin:18px 0">{E(s["short"])} questions.</h2><div class="cta-row" style="margin-top:20px"><a href="{cta}" class="btn b-or">Ask Us Anything <span class="arr">→</span></a></div></div>
<div>{faq_html(s["faqs"])}</div>
</div></section>
<section class="s" style="padding-top:0"><div class="wrap">
<div class="sec-head"><div><span class="eyebrow rv">Pairs well with</span><h2 class="rv d1">Related services</h2></div><a href="{p.href("/services/")}" class="btn rv d2">All Services <span class="arr">→</span></a></div>
<div class="related">{relh}</div>
</div></section>
''' + band(p, f'Ready to talk <span class="c-le">{E(s["short"].lower())}?</span>', "Get a Proposal", "/work-with-us/?service=" + quote(s["name"]))
    schema = [crumbs_schema([("Home", "/"), ("Services", "/services/"), (s["name"], f'/services/{s["slug"]}/')]),
              {"@type": "Service", "name": s["name"], "serviceType": s["name"], "description": s["meta"], "url": f'{BASE}/services/{s["slug"]}/',
               "provider": {"@id": BASE + "/#organization"}, "areaServed": "Worldwide",
               "audience": {"@type": "Audience", "audienceType": "Coaches, consultants, e-commerce brands and growing businesses"}},
              faq_schema(s["faqs"])]
    write(f'/services/{s["slug"]}/', s["title"], s["meta"], body, "services", schema, priority="0.9")

# =================================================================== ABOUT
def about(p):
    vcols = ["var(--orange)", "var(--teal)", "var(--lemon)", "var(--sage)"]
    vals = [("Sociable.", "We build brands people want to talk to — and talk about."), ("Organised.", "Clear plans, clear timelines, clear reporting. Always."),
            ("Collaborative.", "Your knowledge plus our expertise. We build it together."), ("Fun.", "Good marketing has personality. So do we.")]
    vh = "".join(f'<div class="vl rv d{i}{" dk" if i == 1 else ""}" style="--bg:{vcols[i]}"><h3>{h}</h3><p>{t}</p></div>' for i, (h, t) in enumerate(vals))
    return phero(p, "About Artlify", 'A marketing agency with <span class="c-or">personality</span> — and a plan.',
                 ["Artlify helps coaches and growing brands show up, stand out and grow with marketing that is vibrant, organised and built around them."],
                 [("Home", "/"), ("About", "/about/")], decos=(2, 3, 5)) + f'''
<section class="s" style="padding-top:10px"><div class="wrap split">
<div class="photo-frame rv">{img(p, "team-workshop", "The Artlify team in a collaborative marketing strategy workshop", w=1400, h=934)}</div>
<div><span class="eyebrow rv">Our story</span><h2 class="rv d1" style="margin:18px 0 22px">Marketing should feel like <span class="c-te">collaboration</span>, not a black box.</h2>
<p class="rv" style="font-size:18.5px;color:var(--ink2)">Artlify was founded on a simple belief: there is no one-size-fits-all approach to marketing. Every brand has its own audience, offer, voice and goals — so every brand deserves a strategy built for it.</p>
<p class="rv" style="font-size:18.5px;color:var(--ink2)">We started by helping coaches grow with vibrant, organised marketing, and today we partner with coaches, consultants, e-commerce brands and growing businesses. Our team brings strategy, content, social media, copywriting, paid ads, funnels and automation together under one roof, so your marketing works as one connected system.</p>
<p class="rv" style="font-size:18.5px;color:var(--ink2)">We’re all about fun, connection and collaboration — and about results you can actually measure.</p></div>
</div></section>
<section class="s" style="padding-top:0"><div class="wrap"><div class="mission rv"><span class="eyebrow" style="margin-bottom:18px">Our mission</span><p>To create a friendly space where coaches and brands feel empowered, supported and equipped to thrive — with marketing that is as organised as it is unforgettable.</p></div></div></section>
<section class="s" style="padding-top:0"><div class="wrap">
<div class="sec-head"><div><span class="eyebrow rv">What we value</span><h2 class="rv d1">The Artlify way.</h2></div></div>
<div class="vals">{vh}</div></div></section>
<section class="s" style="background:var(--cream2)"><div class="wrap split">
<div><span class="eyebrow rv">What we do</span><h2 class="rv d1" style="margin:18px 0 20px">Full-stack marketing, <span class="c-or">one team.</span></h2>
<ul class="prose rv d2" style="font-size:18px">{"".join(f'<li><a href="{p.href("/services/" + s["slug"] + "/")}" style="text-decoration:underline;text-underline-offset:3px">{E(s["name"])}</a></li>' for s in SERVICES)}</ul></div>
<div class="photo-frame rv d1">{img(p, "client-meeting", "Artlify strategists reviewing a marketing plan with a client", w=1400, h=933)}</div>
</div></section>
''' + band(p, 'Let’s build something <span class="c-le">people remember.</span>')

# =================================================================== WORK
REAL_CASES = {
    0: ("Coach of Success", "A coach",
        "She wasn't attracting qualified leads, and her social media account wasn't set up to turn followers into clients.",
        "Built her content strategy and content pillars, then a full marketing funnel: ad creative direction, a sales landing page, lead nurturing and the email copy that leads to conversion.",
        "She landed her first five clients for her $5,000 coaching programme."),
}
def case_body(i):
    if i in REAL_CASES:
        name, who, ch, did, res = REAL_CASES[i]
        return (f'<h3>{E(name)}</h3><dl><dt>Client</dt><dd>{E(who)}</dd><dt>Challenge</dt><dd>{E(ch)}</dd><dt>What we did</dt><dd>{E(did)}</dd>'
                f'<dt>Results</dt><dd>{E(res)}</dd></dl>')
    return ('<h3>[Client / brand name]</h3><dl><dt>Challenge</dt><dd class="phx">[What the client needed]</dd><dt>What we did</dt>'
            '<dd class="phx">[Services and work delivered]</dd><dt>Results</dt><dd class="phx">[Verified results, with permission]</dd></dl>')

def work(p):
    cases = [("funnels", "Content & Funnels", "orange", 2), ("ads", "Paid Ads", "teal", 6), ("content", "Content", "lemon", 7),
             ("funnels", "Funnels & Automation", "sage", 8), ("social", "Social Media", "peach", 3), ("strategy", "Strategy", "gold", 5)]
    cards = "".join(f'''<article class="card rv" data-cat="{k}"><div class="cv" style="--bg:{COL[c][0]}"><span class="tag">{E(n)}</span>{shape(p, sh, cls="shape")}<span class="g"{' style="color:var(--cream)"' if COL[c][1] else ""}>0{i+1}</span></div>
<div class="bd">{case_body(i)}</div></article>''' for i, (k, n, c, sh) in enumerate(cases))
    return phero(p, "Our work", 'Marketing that <span class="c-or">moves the needle.</span>',
                 ["Selected projects across social media, content, paid ads, funnels and automation for coaches and growing brands."],
                 [("Home", "/"), ("Work", "/work/")], decos=(7, 3, 6)) + f'''
<section class="s" style="padding-top:10px"><div class="wrap">
<div class="filters" data-filters="#cases" role="group" aria-label="Filter case studies"><button class="fbtn" data-f="all" aria-pressed="true">All work</button><button class="fbtn" data-f="social" aria-pressed="false">Social Media</button><button class="fbtn" data-f="ads" aria-pressed="false">Paid Ads</button><button class="fbtn" data-f="content" aria-pressed="false">Content</button><button class="fbtn" data-f="funnels" aria-pressed="false">Funnels</button><button class="fbtn" data-f="strategy" aria-pressed="false">Strategy</button></div>
<div class="cards" id="cases">{cards}</div>
</div></section>
<section class="s impact"><div class="wrap"><div class="sec-head"><div><span class="eyebrow rv" style="color:var(--cream)">Our impact</span><h2 class="rv d1">Results that <span class="c-le">speak.</span></h2></div></div><div class="stats">{stats_html()}</div></div></section>
''' + band(p, 'Your brand could be <span class="c-le">next.</span>')

# =================================================================== BLOG
import re, datetime, markdown as _md
CAT = {c["slug"]: c for c in CATEGORIES}

def fdate(d):
    return datetime.date.fromisoformat(d).strftime("%-d %B %Y")

def load_posts():
    posts = []
    for fn in sorted(os.listdir(os.path.join(ROOT, "posts"))):
        if not fn.endswith(".md") or fn.startswith(("_", "README")): continue
        raw = open(os.path.join(ROOT, "posts", fn), encoding="utf-8").read()
        _, fm, body = raw.split("---", 2)
        m = {}
        for line in fm.strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1); m[k.strip().lower()] = v.strip()
        if m.get("draft", "").lower() in ("yes", "true"): continue
        body = re.sub(r"^\s*# .*\n", "", body.lstrip(), count=1)  # drop a pasted H1 (the title is the H1)
        faqs = []
        fq = re.search(r"^## (?:FAQs?|Frequently asked questions)\s*$", body, re.M | re.I)
        if fq:
            tail = body[fq.end():]; body = body[:fq.start()]
            for q, a in re.findall(r"^### (.+?)\s*\n(.*?)(?=^### |\Z)", tail, re.M | re.S):
                faqs.append((q.strip(), " ".join(a.split())))
        md = _md.Markdown(extensions=["tables", "toc", "sane_lists"], extension_configs={"toc": {"toc_depth": "2"}})
        htm = md.convert(body)
        words = len(re.sub(r"<[^>]+>", " ", htm).split())
        cat = CAT[m["category"]]
        posts.append(dict(m, slug=m.get("slug") or fn[:-3], cat=cat, html=htm, faqs=faqs, words=words,
                          read=f"{max(3, round(words / 220))} min", updated=m.get("updated") or m["date"],
                          toc=[(t["id"], t["name"]) for t in md.toc_tokens], pillar=m.get("pillar", "").lower() in ("yes", "true"),
                          excerpt=m.get("excerpt") or m["description"], color=cat["color"]))
    posts.sort(key=lambda x: x["date"], reverse=True)
    return posts

POSTS = load_posts()
def cat_posts(c): return [b for b in POSTS if b["cat"] is c]
LIVE_CATS = [c for c in CATEGORIES if cat_posts(c)]
def purl(b): return f'/blog/{b["slug"]}/'
def curl(c): return f'/blog/{c["slug"]}/'
def plural(n, w): return f"{n} {w}{'' if n == 1 else 's'}"
TAGSTYLE = 'style="font-size:12px;font-weight:700;letter-spacing:.1em;text-transform:uppercase"'

def post_card(p, b, i, tag="h3"):
    bg, dk = COL[b["color"]]
    g = ('<span class="g"' + (' style="color:var(--cream)"' if dk else "") + '>Guide</span>') if b["pillar"] else ""
    return (f'<article class="card rv"><a href="{p.href(purl(b))}" style="display:contents">'
            f'<div class="cv" style="--bg:{bg}"><span class="tag">{E(b["cat"]["short"])}</span>{shape(p, [2, 6, 7][i % 3], cls="shape")}{g}</div>'
            f'<div class="bd"><{tag} style="font-size:clamp(23px,2vw,28px)">{E(b["title"])}</{tag}><p>{E(b["excerpt"])}</p>'
            f'<div class="meta"><time datetime="{b["updated"]}">{fdate(b["updated"])}</time><span>{E(b["read"])} read</span></div></div></a></article>')

def cat_nav(p, current=None):
    cur = ' aria-current="page"'
    a = [f'<a href="{p.href("/blog/")}" class="fbtn"{cur if current is None else ""}>All articles</a>']
    for c in LIVE_CATS:
        a.append(f'<a href="{p.href(curl(c))}" class="fbtn"{cur if current is c else ""}>{E(c["name"])} <small>{len(cat_posts(c))}</small></a>')
    return f'<nav class="filters cat-nav" aria-label="Blog topics">{"".join(a)}</nav>'

def itemlist(posts):
    return {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": BASE + purl(b), "name": b["title"]} for i, b in enumerate(posts)]}

def hub_card(p, c):
    bg, dk = COL[c["color"]]
    return (f'<a href="{p.href(curl(c))}" class="rel rv{" dk" if dk else ""}" style="--bg:{bg}"><span class="tag" {TAGSTYLE}>{plural(len(cat_posts(c)), "article")}</span>'
            f'<h3>{E(c["name"])}</h3><p style="font-size:15.5px">{E(c["intro"])}</p><span style="font-weight:600">Explore &rarr;</span></a>')

def blog_index(p):
    pillars = [b for b in POSTS if b["pillar"]]
    start = ('<div class="sec-head" style="margin-top:70px"><div><span class="eyebrow">Start here</span><h2 style="margin-top:14px">Our complete guides</h2></div></div>'
             f'<div class="cards">{"".join(post_card(p, b, i) for i, b in enumerate(pillars))}</div>') if pillars else ""
    return phero(p, "The Artlify blog", 'Marketing ideas you can <span class="c-or">actually use.</span>',
                 ["Practical guides on hiring an agency, social media, Meta ads, funnels and automation, for coaches and growing brands in the US, the UK and beyond."],
                 [("Home", "/"), ("Blog", "/blog/")], decos=(5, 3, 2)) + f'''
<section class="s" style="padding-top:10px"><div class="wrap">
{cat_nav(p)}
<div class="sec-head"><div><span class="eyebrow">Browse by topic</span><h2 style="margin-top:14px">Pick what you need help with</h2></div></div>
<div class="related">{"".join(hub_card(p, c) for c in LIVE_CATS)}</div>
{start}
<div class="sec-head" style="margin-top:70px"><div><span class="eyebrow">Latest</span><h2 style="margin-top:14px">New articles</h2></div></div>
<div class="cards">{"".join(post_card(p, b, i) for i, b in enumerate(POSTS))}</div>
</div></section>''' + band(p, 'Rather we do it <span class="c-le">for you?</span>')

def cat_page(c):
    posts = cat_posts(c)
    pillars = [b for b in posts if b["pillar"]]; rest = [b for b in posts if not b["pillar"]]
    svcs = [s for s in SERVICES if s["slug"] in c["services"]]
    def body(p):
        guide = ""
        if pillars:
            g = pillars[0]
            guide = (f'<a href="{p.href(purl(g))}" class="guide rv" style="--bg:{COL[c["color"]][0]}"><span class="eyebrow">Start here: the complete guide</span>'
                     f'<h2>{E(g["title"])}</h2><p>{E(g["excerpt"])}</p><span class="btn b-ink">Read the guide <span class="arr">&rarr;</span></span></a>')
        mt = ' style="margin-top:60px"' if guide else ""
        listing = "" if (guide and not rest) else (f'<div class="sec-head"{mt}><div><span class="eyebrow">All {E(c["short"].lower())} articles</span><h2 style="margin-top:14px">{plural(len(posts), "article")} on {E(c["name"].lower())}</h2></div></div>'
                                                   f'<div class="cards">{"".join(post_card(p, b, i, "h2") for i, b in enumerate(rest or pillars))}</div>')
        return phero(p, "Blog topic", E(c["name"]), [E(c["intro"])],
                     [("Home", "/"), ("Blog", "/blog/"), (c["name"], curl(c))], decos=(6, 2, 7)) + f'''
<section class="s" style="padding-top:10px"><div class="wrap">
{cat_nav(p, c)}
{guide}
{listing}
<div class="sec-head" style="margin-top:70px"><div><span class="eyebrow">Want it done for you?</span><h2 style="margin-top:14px">Related services</h2></div></div>
<div class="related">{"".join(svc_card(p, s) for s in svcs)}</div>
</div></section>''' + band(p, 'Rather we do it <span class="c-le">for you?</span>')
    schema = [crumbs_schema([("Home", "/"), ("Blog", "/blog/"), (c["name"], curl(c))]),
              {"@type": "CollectionPage", "@id": BASE + curl(c), "url": BASE + curl(c), "name": c["name"], "description": c["desc"],
               "isPartOf": {"@id": BASE + "/#website"}, "mainEntity": itemlist(posts)}]
    write(curl(c), c["title"], c["desc"], body, "blog", schema, priority="0.6", lastmod=max(b["updated"] for b in posts))

def author_schema():
    a = {"@type": "Person", "@id": BASE + "/#author", "name": AUTHOR["name"], "jobTitle": AUTHOR["role"], "url": BASE + AUTHOR["url"],
         "worksFor": {"@id": BASE + "/#organization"}}
    if AUTHOR["same_as"]: a["sameAs"] = AUTHOR["same_as"]
    return a

def post_page(b):
    c = b["cat"]
    def body(p):
        prose = re.sub(r'href="(/[^"]*)"', lambda m: f'href="{p.href(m.group(1))}"', b["html"])
        same = [o for o in cat_posts(c) if o is not b]
        others = (same + [o for o in POSTS if o is not b and o not in same])[:3]
        rel = "".join(f'<a href="{p.href(purl(o))}" class="rel rv{" dk" if COL[o["color"]][1] else ""}" style="--bg:{COL[o["color"]][0]}"><span class="tag" {TAGSTYLE}>{E(o["cat"]["short"])}</span><h3>{E(o["title"])}</h3></a>' for o in others)
        toc = ""
        if len(b["toc"]) >= 3:
            lis = "".join(f'<li><a href="#{i}">{E(n)}</a></li>' for i, n in b["toc"])
            if b["faqs"]: lis += '<li><a href="#faqs">Frequently asked questions</a></li>'
            toc = f'<nav class="toc" aria-label="Table of contents"><details open><summary>In this article</summary><ol>{lis}</ol></details></nav>'
        faqs = f'<section class="post-faq" id="faqs"><h2>Frequently asked questions</h2>{faq_html(b["faqs"])}</section>' if b["faqs"] else ""
        quick = f'<aside class="quick" aria-label="Quick answer"><span class="eyebrow">Quick answer</span><p>{E(b["quick"])}</p></aside>' if b.get("quick") else ""
        svcs = "".join(f'<a href="{p.href("/services/" + s["slug"] + "/")}">{E(s["name"])}</a>' for s in SERVICES if s["slug"] in c["services"])
        upd = f'<span>&middot;</span><span>Updated <time datetime="{b["updated"]}">{fdate(b["updated"])}</time></span>' if b["updated"] != b["date"] else ""
        dk = ' style="color:var(--cream)"' if COL[b["color"]][1] else ""
        return f'''<section class="s" style="padding-top:clamp(30px,5vw,60px)"><article class="wrap"><div class="article">
{crumbs_html(p, [("Home", "/"), ("Blog", "/blog/"), (c["name"], curl(c)), (b["title"], purl(b))])}
<a href="{p.href(curl(c))}" class="pill"><i></i>{E(c["name"])}</a>
<h1 style="font-size:clamp(38px,5vw,66px);margin:20px 0 14px">{E(b["title"])}</h1>
<div class="byline"><span>By <a href="{p.href(AUTHOR["url"])}" rel="author">{E(AUTHOR["name"])}</a></span><span>&middot;</span><span>Published <time datetime="{b["date"]}">{fdate(b["date"])}</time></span>{upd}<span>&middot;</span><span>{E(b["read"])} read</span></div>
<div class="cover" style="--bg:{COL[b["color"]][0]};margin-top:30px" aria-hidden="true">{shape(p, [2, 6, 7][POSTS.index(b) % 3])}<span class="g"{dk}>{E(c["short"])}</span></div>
{quick}
{toc}
<div class="prose">{prose}</div>
{faqs}
<aside class="author-box"><span class="av" aria-hidden="true">{E(AUTHOR["name"][0])}</span><div><span class="eyebrow">Written by</span><h2>{E(AUTHOR["name"])}</h2><p class="role">{E(AUTHOR["role"])}</p><p>{E(AUTHOR["bio"])}</p></div></aside>
<aside class="post-cta"><h2>Want this done for you?</h2><p>Artlify plans and runs marketing for coaches and growing brands.</p><p class="svc-links">{svcs}</p><a href="{p.href("/work-with-us/")}" class="btn b-le" style="border-color:var(--ink)">Work With Us <span class="arr">&rarr;</span></a></aside>
</div></article></section>
<section class="s" style="padding-top:0"><div class="wrap"><div class="sec-head"><div><span class="eyebrow">Keep reading</span><h2 style="margin-top:14px">More from the blog</h2></div><a href="{p.href(curl(c))}" class="btn">All {E(c["short"])} Articles <span class="arr">&rarr;</span></a></div><div class="related">{rel}</div></div></section>'''
    post = {"@type": "BlogPosting", "@id": BASE + purl(b) + "#article", "headline": b["title"], "description": b["description"],
            "datePublished": b["date"], "dateModified": b["updated"], "wordCount": b["words"], "inLanguage": "en",
            "mainEntityOfPage": BASE + purl(b), "image": BASE + "/assets/img/og-image.jpg", "articleSection": c["name"],
            "author": author_schema(), "publisher": {"@id": BASE + "/#organization"},
            "isPartOf": {"@type": "Blog", "@id": BASE + "/blog/#blog", "name": "Artlify Blog", "url": BASE + "/blog/"}}
    schema = [crumbs_schema([("Home", "/"), ("Blog", "/blog/"), (c["name"], curl(c)), (b["title"], purl(b))]), post]
    if b["faqs"]: schema.append(faq_schema(b["faqs"]))
    write(purl(b), b["seo"], b["description"], body, "blog", schema, "article", priority="0.6", lastmod=b["updated"])

def rss():
    items = "".join(f'<item><title>{E(b["title"])}</title><link>{BASE}{purl(b)}</link><guid>{BASE}{purl(b)}</guid>'
                    f'<pubDate>{datetime.date.fromisoformat(b["date"]).strftime("%a, %d %b %Y 09:00:00 +0000")}</pubDate>'
                    f'<category>{E(b["cat"]["name"])}</category><description>{E(b["description"])}</description></item>' for b in POSTS)
    os.makedirs(os.path.join(OUT, "blog"), exist_ok=True)
    open(os.path.join(OUT, "blog", "feed.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>Artlify Blog</title><link>{BASE}/blog/</link><description>Marketing guides for coaches and growing brands.</description><language>en</language>{items}</channel></rss>\n')

# =================================================================== WORK WITH US
def opts(name, items, kind="checkbox"):
    return '<div class="opts">' + "".join(f'<label class="opt"><input type="{kind}" name="{name}" value="{E(v)}"><span>{E(v)}</span></label>' for v in items) + "</div>"

def wwu(p):
    biz = ["Coach / Consultant", "Course creator", "E-commerce brand", "Service business", "Personal brand / Creator", "Startup", "Other"]
    goals = ["More leads & booked calls", "More sales", "Grow my audience", "Launch an offer or product", "Build brand awareness", "Save time with automation"]
    form = f'''<form id="enq" name="enquiry" method="POST" data-netlify="true" netlify-honeypot="bot-field" novalidate>
<input type="hidden" name="form-name" value="enquiry"><p hidden><label>Leave empty <input name="bot-field"></label></p>
<div class="prog"><div class="bar"><i id="progBar"></i></div><span id="progTxt">Step 1 of 6</span></div>
<div class="step" data-step="who"><fieldset><legend>What best describes your business?</legend>{opts("business", biz, "radio")}</fieldset></div>
<div class="step" data-step="services"><fieldset><legend>Which services are you interested in?</legend><p class="help">Choose as many as you like.</p>{opts("services", [s["name"] for s in SERVICES] + ["Not sure yet"])}</fieldset></div>
<div class="step" data-step="details"><span class="q">A few quick details.</span><p class="help">Based on what you picked — this helps us prepare for our call.</p>
<div class="sub" data-if="Social Media Management"><span class="lbl">Which platforms matter most to you?</span>{opts("platforms", ["Instagram", "LinkedIn", "TikTok", "Facebook", "Pinterest", "X", "YouTube"])}</div>
<div class="sub" data-if="Paid Ads &amp; Sponsored Ads"><span class="lbl">What is your current monthly ad spend?</span>{opts("adSpend", ["Not running ads yet", "Under $500", "$500 – $2,000", "$2,000 – $5,000", "$5,000+"], "radio")}</div>
<div class="sub" data-if="Content Creation"><span class="lbl">What content do you need?</span>{opts("contentTypes", ["Reels / short-form video", "Carousels", "Graphics", "Shoot direction", "UGC-style content"])}</div>
<div class="sub" data-if="Funnel Building|Marketing Automation"><span class="lbl">Which tools do you already use?</span>{opts("tools", ["Systeme.io", "GoHighLevel", "Kajabi", "Shopify", "Klaviyo", "Mailchimp", "None yet", "Other"])}</div>
<div class="sub" data-if="Not sure yet"><p style="padding:16px 18px;border-radius:14px;background:var(--sage);border:2px solid var(--ink)"><strong>No problem.</strong> Tell us about your goals next and we’ll recommend the right mix of services.</p></div>
</div>
<div class="step" data-step="goals"><fieldset><legend>What are your main goals right now?</legend>{opts("goals", goals)}</fieldset>
<div class="fl" style="margin-top:24px"><label for="f-about">Tell us about your business <em>(optional)</em></label><textarea id="f-about" name="about" placeholder="What you sell, who you serve, what’s working and what isn’t…"></textarea></div></div>
<div class="step" data-step="engagement"><fieldset><legend>How would you like to work together?</legend>{opts("engagement", ["Single service", "Combination of services", "Full growth partnership", "Not sure yet"], "radio")}</fieldset></div>
<div class="step" data-step="contact"><span class="q">Where can we reach you?</span><p class="help">We review every enquiry and reply with the best next step.</p>
<div class="fields">
<div class="fl"><label for="f-name">Full name</label><input id="f-name" name="name" autocomplete="name"></div>
<div class="fl"><label for="f-email">Email address</label><input id="f-email" name="email" type="email" autocomplete="email"></div>
<div class="fl"><label for="f-brand">Business name <em>(optional)</em></label><input id="f-brand" name="brand" autocomplete="organization"></div>
<div class="fl"><label for="f-link">Website or Instagram</label><input id="f-link" name="link" placeholder="https:// or @handle"></div>
<div class="fl"><label for="f-budget">Marketing budget</label><select id="f-budget" name="budget"></select></div>
<div class="fl"><label for="f-start">When would you like to start?</label><select id="f-start" name="start"><option value="">Select</option><option>As soon as possible</option><option>Within a month</option><option>In 1–3 months</option><option>Just exploring</option></select></div>
<div class="fl full"><label for="f-hear">How did you hear about Artlify?</label><select id="f-hear" name="hear"><option value="">Select</option><option>Instagram</option><option>LinkedIn</option><option>Google search</option><option>Referral</option><option>Other</option></select></div>
</div></div>
<div class="err-msg" id="err" role="alert"></div>
<div class="fnav"><button type="button" class="back" id="back" hidden>← Back</button><button type="submit" class="btn b-ink" id="next">Continue <span class="arr">→</span></button></div>
</form>
<div class="done" id="done" role="status" aria-live="polite"><div class="tick">✓</div><h2>Thank you — we’ve got it!</h2><p>Your enquiry is in. We’ll review your goals and get back to you with the best next step.</p><p>Keep an eye on your inbox (and your spam folder, just in case).</p>
<div class="cta-row" style="margin-top:26px"><a href="{p.href("/work/")}" class="btn b-or">See Our Work <span class="arr">→</span></a><a href="{p.href("/blog/")}" class="btn">Read the Blog</a></div></div>'''
    return phero(p, "Work with us", 'Let’s make your brand <span class="c-or">impossible to ignore.</span>',
                 ["Tell us about your business and goals. It takes about two minutes, and we review every enquiry personally."],
                 [("Home", "/"), ("Work With Us", "/work-with-us/")], decos=(6, 3, 7)) + f'''
<section class="s" style="padding-top:10px"><div class="wrap wwu">
<aside class="wwu-side"><div class="side-card"><h2>What happens next</h2><ol>{"".join(f"<li><b>0{i+1}</b>{E(h)}</li>" for i, (h, t) in enumerate(PROCESS))}</ol></div>
<p style="margin-top:20px;font-size:15.5px;color:var(--muted)">Have a question first? <a href="{p.href("/faq/")}" class="txtlink" style="color:var(--ink)">Read the FAQ <span>→</span></a></p>
{f'<p style="margin-top:12px;font-size:15.5px;color:var(--muted)">Prefer email? <a href="mailto:{E(SITE["email"])}" class="txtlink" style="color:var(--ink)">{E(SITE["email"])}</a></p>' if SITE["email"] else ""}
{f'<p style="margin-top:12px;font-size:15.5px;color:var(--muted)">Or WhatsApp us: <a href="https://wa.me/{SITE["phone"].lstrip("+")}" target="_blank" rel="noopener" class="txtlink" style="color:var(--ink)">{E(SITE["phone_display"])}</a></p>' if SITE.get("phone") else ""}</aside>
<div class="fbox" id="fbox" data-tally="{E(SITE["tally_id"])}"><div class="tally-wrap" id="tallyWrap" hidden></div>{form}</div>
</div></section>'''

# =================================================================== FAQ / LEGAL / 404
def faq_page(p):
    return phero(p, "FAQ", 'Questions, <span class="c-or">answered.</span>', ["Everything you need to know about working with Artlify."], [("Home", "/"), ("FAQ", "/faq/")], decos=(8, 3, 5)) + f'''
<section class="s" style="padding-top:10px"><div class="wrap faq"><div class="side"><p class="lead">Can’t find what you’re looking for?</p><div class="cta-row" style="margin-top:22px"><a href="{p.href("/work-with-us/")}" class="btn b-or">Ask Us Directly <span class="arr">→</span></a></div></div><div>{faq_html(FAQS)}</div></div></section>'''

def legal(name):
    return lambda p: f'<section class="ph"><div class="wrap">{crumbs_html(p, [("Home", "/"), (name, "/")])}<span class="pill"><i></i>Legal</span><h1>{name}</h1></div></section><section class="s" style="padding-top:0"><div class="wrap legal"><p>[{name} content to be added before launch.]</p></div></section>'

def e404(p):
    return f'<section class="e404"><div class="wrap"><div class="big">404</div><h1 style="font-size:clamp(36px,5vw,64px);margin:16px 0 18px">This page wandered off.</h1><p class="lead" style="margin:0 auto 30px">Let’s get you back to something useful.</p><div class="cta-row" style="justify-content:center"><a href="{p.href("/")}" class="btn b-ink">Go Home <span class="arr">→</span></a><a href="{p.href("/services/")}" class="btn">Our Services</a></div></div></section>'

# =================================================================== BUILD
def build():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    shutil.copytree(os.path.join(ROOT, "src"), OUT)
    write("/", "Artlify | Marketing Agency for Coaches & Growing Brands",
          "Artlify is a full-service marketing agency for coaches and brands: social media, content, copywriting, paid ads, funnels and marketing automation.",
          home, "home", [faq_schema(FAQS[:5])] if False else [], priority="1.0", preload_img="img/team-smiling-720.webp")
    write("/services/", "Marketing Services | Social, Content, Ads & Funnels | Artlify",
          "Explore Artlify’s marketing services: social media, content strategy and creation, copywriting, paid ads, influencer marketing, funnels and automation.",
          services_index, "services", [crumbs_schema([("Home", "/"), ("Services", "/services/")])], priority="0.9")
    for s in SERVICES: service_page(s)
    write("/about/", "About Artlify | Personalised Marketing Agency for Coaches & Brands",
          "Meet Artlify — a sociable, organised, full-stack marketing agency helping coaches and growing brands with personalised strategy, content, ads, funnels and automation.",
          about, "about", [crumbs_schema([("Home", "/"), ("About", "/about/")])], priority="0.8")
    write("/work/", "Our Work & Case Studies | Artlify Marketing Agency",
          "See how Artlify helps coaches and brands grow with social media, content, paid ads, funnels and marketing automation.",
          work, "work", [crumbs_schema([("Home", "/"), ("Work", "/work/")])], priority="0.7")
    write("/blog/", "Marketing Blog for Coaches & Brands | Artlify",
          "Practical marketing guides from Artlify on social media strategy, content, Meta ads, funnels and automation for coaches and growing brands.",
          blog_index, "blog", [crumbs_schema([("Home", "/"), ("Blog", "/blog/")]),
          {"@type": "Blog", "@id": BASE + "/blog/#blog", "url": BASE + "/blog/", "name": "Artlify Blog", "publisher": {"@id": BASE + "/#organization"},
           "blogPost": [{"@id": BASE + purl(b) + "#article"} for b in POSTS]}],
          priority="0.7", lastmod=POSTS[0]["updated"] if POSTS else None)
    for c in LIVE_CATS: cat_page(c)
    for b in POSTS: post_page(b)
    rss()
    write("/work-with-us/", "Work With Us | Get a Marketing Proposal | Artlify",
          "Tell Artlify about your business and goals. Enquire about social media management, content, paid ads, funnels, automation or a full growth partnership.",
          wwu, "", [crumbs_schema([("Home", "/"), ("Work With Us", "/work-with-us/")])], priority="0.9")
    write("/faq/", "FAQ | Working With Artlify Marketing Agency",
          "Answers to common questions about Artlify: services, who we work with, pricing, ad spend, timelines and how to get started.",
          faq_page, "", [crumbs_schema([("Home", "/"), ("FAQ", "/faq/")]), faq_schema(FAQS)], priority="0.6")
    write("/privacy/", "Privacy Policy | Artlify", "How Artlify Agency collects, uses and protects personal information shared through this website.", legal("Privacy Policy"), noindex=True)
    write("/terms/", "Terms & Conditions | Artlify", "The terms and conditions for using the Artlify Agency website and working with Artlify.", legal("Terms & Conditions"), noindex=True)
    write("/404", "Page not found | Artlify", "Sorry, this page could not be found. Explore Artlify’s marketing services, work and blog instead.", e404, noindex=True)

    up = SITE["updated"]
    sm = "".join(f"<url><loc>{BASE}{pth}</loc><lastmod>{lm}</lastmod><priority>{pr}</priority></url>" for pth, pr, lm in PAGES)
    open(os.path.join(OUT, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")
    open(os.path.join(OUT, "site.webmanifest"), "w").write(json.dumps({"name": "Artlify Marketing Agency", "short_name": "Artlify", "start_url": "/", "display": "standalone",
        "background_color": "#F1EAD8", "theme_color": "#F1EAD8", "icons": [{"src": "/assets/img/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "/assets/img/icon-512.png", "sizes": "512x512", "type": "image/png"}]}))
    open(os.path.join(OUT, "_headers"), "w").write("""/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  X-Frame-Options: SAMEORIGIN

/assets/*
  Cache-Control: public, max-age=31536000, immutable
""")
    open(os.path.join(OUT, "_redirects"), "w").write("/contact  /work-with-us/  301\n/contact/  /work-with-us/  301\n/home  /  301\n")
    llms = f"# Artlify\n\n> {SITE['description']}\n\n## Services\n" + "".join(f"- [{s['name']}]({BASE}/services/{s['slug']}/): {s['card']}\n" for s in SERVICES) + \
           "\n## Blog topics\n" + "".join(f"- [{c['name']}]({BASE}{curl(c)}): {c['intro']}\n" for c in LIVE_CATS) + \
           "\n## Articles\n" + "".join(f"- [{b['title']}]({BASE}{purl(b)}): {b['description']}\n" for b in POSTS) + \
           f"\n## Pages\n- [About]({BASE}/about/)\n- [Work]({BASE}/work/)\n- [Blog]({BASE}/blog/)\n- [FAQ]({BASE}/faq/)\n- [Work With Us]({BASE}/work-with-us/)\n"
    open(os.path.join(OUT, "llms.txt"), "w").write(llms)
    print(MODE, "built", len(PAGES), "indexable pages ->", OUT)

if __name__ == "__main__":
    build()
