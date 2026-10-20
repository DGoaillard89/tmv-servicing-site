#!/usr/bin/env python3
"""Static page builder for tmv-servicing.com.

Page bodies live in _src/ (pages) and _src/blog/ (posts). Each file starts with
an HTML comment holding JSON metadata:  <!--meta { ... } -->
This script wraps each body in the shared head/header/footer and writes the
finished HTML to the site root (or /blog/). It also writes sitemap.xml.

Run from anywhere:  python3 _tools/build.py
"""
import json
import re
import html
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_src"
DOMAIN = "https://tmv-servicing.com"
BRAND = "TMV Servicing"
TODAY = date.today().isoformat()
PHONE = "020 3633 6064"
TEL = "tel:+442036336064"
FONTS = "https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Sora:wght@400;600;700;800&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&display=swap"

LOGO_MARK = (
    '<svg viewBox="0 0 48 48"><path class="logo__cold" d="M11.01 33.5A15 15 0 0 1 20.12 11.51" />'
    '<path class="logo__hot" d="M27.88 11.51A15 15 0 0 1 36.99 33.5" />'
    '<path class="logo__needle" d="M24 26V14.2" /><circle class="logo__hub" cx="24" cy="26" r="4.4" />'
    '<circle class="logo__pin" cx="24" cy="26" r="1.6" /></svg>'
)

NAV = [
    ("servicing", "tmv-servicing.html", "Servicing"),
    ("installation", "tmv-installation.html", "Installation"),
    ("compliance", "tmv-compliance.html", "Compliance"),
    ("sectors", "sectors.html", "Sectors"),
    ("registers", "asset-registers.html", "Asset registers"),
    ("blog", "blog/", "Advice"),
]

# Service pages that posts can link back to
SERVICE_LINKS = {
    "servicing": ("tmv-servicing.html", "TMV servicing &amp; testing", "valve"),
    "installation": ("tmv-installation.html", "TMV installation &amp; replacement", "wrench"),
    "compliance": ("tmv-compliance.html", "TMV compliance guide", "shield"),
    "sectors": ("sectors.html", "Sectors we work in", "care"),
    "registers": ("asset-registers.html", "Asset registers &amp; reminders", "register"),
    "faqs": ("faqs.html", "TMV FAQs", "book"),
    "process": ("process.html", "How it works", "calendar"),
    "guide": ("htm-04-01-tmv-testing.html", "HTM 04-01 &amp; D 08 testing guide", "book"),
}


BUSINESS_REF = {
    "@type": "ProfessionalService", "@id": DOMAIN + "/#business", "name": BRAND, "url": DOMAIN + "/",
    "telephone": "+44 20 3633 6064",
    "address": {"@type": "PostalAddress", "streetAddress": "The Lightbox G16, 111 Power Road",
                "addressLocality": "London", "addressRegion": "Chiswick", "postalCode": "W4 5PY", "addressCountry": "GB"},
}


def icon(name, prefix):
    return f'<svg class="icon" aria-hidden="true"><use href="{prefix}assets/icons.svg#{name}" /></svg>'


def parse(path):
    text = path.read_text()
    m = re.match(r"\s*<!--meta(.*?)-->\s*", text, re.S)
    if not m:
        raise SystemExit(f"No meta block in {path}")
    meta = json.loads(m.group(1))
    meta["body"] = text[m.end():]
    meta["src"] = path
    return meta


def nice_date(iso):
    d = date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%B %Y')}"


def ld(obj):
    return '<script type="application/ld+json">\n' + json.dumps(obj, indent=2, ensure_ascii=False) + "\n</script>"


def org():
    return {"@type": "Organization", "name": BRAND, "url": DOMAIN + "/",
            "logo": {"@type": "ImageObject", "url": DOMAIN + "/assets/apple-touch-icon.png", "width": 180, "height": 180}}


def breadcrumbs(crumbs):
    items = [{"@type": "ListItem", "position": i + 1, "name": html.unescape(n), "item": DOMAIN + u}
             for i, (n, u) in enumerate(crumbs)]
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}


def faq_schema(body):
    qas = re.findall(r"<summary>(.*?)</summary>\s*<div>(.*?)</div>\s*</details>", body, re.S)
    strip = lambda s: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": strip(q),
                            "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in qas]}


def head(meta, prefix, schemas):
    url = DOMAIN + meta["url"]
    og_type = "article" if meta.get("post") else "website"
    t = meta["title"]
    d = meta["description"]
    blocks = "\n  ".join(ld(s) for s in schemas)
    extra = ""
    if meta.get("post"):
        extra = (f'\n  <meta property="article:published_time" content="{meta["date"]}" />'
                 f'\n  <meta property="article:modified_time" content="{meta.get("updated", meta["date"])}" />')
    robots = '\n  <meta name="robots" content="noindex" />' if meta.get("noindex") else ""
    return f"""<!doctype html>
<html lang="en-GB">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <script>document.documentElement.classList.add("js")</script>
  <title>{t}</title>
  <meta name="description" content="{d}" />{robots}
  <link rel="canonical" href="{url}" />
  <meta property="og:site_name" content="{BRAND}" />
  <meta property="og:locale" content="en_GB" />
  <meta property="og:type" content="{og_type}" />
  <meta property="og:title" content="{meta.get('og_title', t)}" />
  <meta property="og:description" content="{d}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:image" content="{DOMAIN}/assets/og-image.png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="TMV Servicing: thermostatic mixing valve testing, servicing and installation" />{extra}
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{meta.get('og_title', t)}" />
  <meta name="twitter:description" content="{d}" />
  <meta name="twitter:image" content="{DOMAIN}/assets/og-image.png" />
  <meta name="theme-color" content="#13202c" />
  <link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml" />
  <link rel="apple-touch-icon" href="{prefix}assets/apple-touch-icon.png" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="{FONTS}" rel="stylesheet" />
  <link rel="stylesheet" href="{prefix}styles.css" />
  {blocks}
</head>"""


def header(prefix, active):
    links = "\n".join(
        f'        <a href="{prefix}{href}" data-nav="{key}">{label}</a>' for key, href, label in NAV)
    return f"""  <a class="skip" href="#main">Skip to content</a>

  <header class="site-header">
    <div class="wrap">
      <a class="logo" href="{prefix or './'}" aria-label="{BRAND} home">
        <span class="logo__mark" aria-hidden="true">{LOGO_MARK}</span>
        <span class="logo__text"><span class="logo__tmv">TMV</span><span class="logo__svc">Servicing</span></span>
      </a>

      <button class="nav-toggle" type="button" aria-label="Menu" aria-expanded="false" aria-controls="site-nav">
        <svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16" /></svg>
      </button>

      <nav class="nav" id="site-nav" aria-label="Main">
{links}
      </nav>

      <div class="header-cta">
        <a class="header-phone" href="{TEL}" aria-label="Call {PHONE}">
          {icon('phone', prefix)}
          <span>{PHONE}</span>
        </a>
        <button class="btn btn--hot" type="button" data-open-enquiry>Get a quote</button>
      </div>
    </div>
  </header>"""


def footer(prefix):
    p = prefix
    home = p or "./"
    return f"""  <footer class="site-footer on-dark">
    <div class="wrap">
      <div class="footer-grid">
        <div>
          <a class="logo" href="{home}" aria-label="{BRAND} home">
            <span class="logo__mark" aria-hidden="true">{LOGO_MARK}</span>
            <span class="logo__text"><span class="logo__tmv">TMV</span><span class="logo__svc">Servicing</span></span>
          </a>
          <p class="footer-blurb">Thermostatic mixing valve servicing, testing and installation. Nationwide, specialising in London and the Home Counties.</p>
        </div>
        <div>
          <h4>Services</h4>
          <ul>
            <li><a href="{p}tmv-servicing.html">TMV servicing</a></li>
            <li><a href="{p}tmv-installation.html">Installation &amp; replacement</a></li>
            <li><a href="{p}tmv-compliance.html">TMV compliance</a></li>
            <li><a href="{p}asset-registers.html">Asset registers &amp; reminders</a></li>
            <li><a href="{p}htm-04-01-tmv-testing.html">HTM 04-01 &amp; D 08 testing guide</a></li>
          </ul>
        </div>
        <div>
          <h4>Company</h4>
          <ul>
            <li><a href="{p}about.html">About us</a></li>
            <li><a href="{p}sectors.html">Sectors</a></li>
            <li><a href="{p}process.html">How it works</a></li>
            <li><a href="{p}faqs.html">FAQs</a></li>
            <li><a href="{p}blog/">Advice &amp; blog</a></li>
            <li><a href="{p}privacy.html">Privacy notice</a></li>
          </ul>
        </div>
        <div>
          <h4>Get in touch</h4>
          <address>The Lightbox G16, 111 Power Road<br />Chiswick, London W4 5PY</address>
          <a class="footer-phone" href="{TEL}">{PHONE}</a>
          <p style="margin-top:16px"><button class="btn btn--light" type="button" data-open-enquiry>Request a quote</button></p>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; <span data-year>2026</span> {BRAND}. All rights reserved. <button class="footer-cookie" type="button" data-cookie-settings hidden>Cookie settings</button></p>
        <p>Nationwide TMV servicing, specialising in London &amp; the Home Counties.</p>
      </div>
    </div>
  </footer>

  <div class="mobile-bar">
    <a href="{TEL}">{icon('phone', p)} Call us</a>
    <button type="button" data-open-enquiry>Get a quote</button>
  </div>

  <script src="{p}consent.js" defer></script>
  <script src="{p}script.js" defer></script>
  <script src="{p}enquiry.js" defer></script>
</body>
</html>
"""


def post_card(post, prefix):
    return f"""<a class="post-card" href="{prefix}blog/{post['slug']}.html">
            <time datetime="{post['date']}">{nice_date(post['date'])}</time>
            <h3>{post['title_h1']}</h3>
            <p>{post['excerpt']}</p>
            <span class="link-arrow">Read the article {icon('arrow', prefix)}</span>
          </a>"""


def related_block(posts, prefix, tag, heading="Related articles", exclude=None, limit=3, tags=None):
    """Pick the best-matching posts from the full set.

    Score: 3 if the post's primary tag is the wanted tag, +1 for every other
    shared tag. Ties go to the newest post. Posts that share nothing fill any
    remaining slots, newest first.
    """
    wanted = tags or [tag]

    def score(p):
        ptags = p.get("tags", [])
        s = 3 if ptags and ptags[0] == wanted[0] else 0
        s += sum(1 for t in ptags if t in wanted)
        return s

    pool = [p for p in posts if p["slug"] != exclude]  # posts are newest first
    chosen = sorted(pool, key=lambda p: -score(p))[:limit]
    if not chosen:
        return ""
    cards = "\n          ".join(post_card(p, prefix) for p in chosen)
    return f"""<section class="section section--stone" aria-labelledby="related-heading">
      <div class="wrap">
        <div class="section-head section-head--row">
          <div>
            <span class="eyebrow">From the blog</span>
            <h2 id="related-heading">{heading}</h2>
          </div>
          <a class="link-arrow" href="{prefix}blog/">All articles {icon('arrow', prefix)}</a>
        </div>
        <div class="post-grid">
          {cards}
        </div>
      </div>
    </section>"""


def gauge(angle, readout, caption):
    dial = (Path(__file__).parent / "gauge-dial.svg").read_text()
    return f"""<div class="gauge" aria-hidden="true">
            <svg viewBox="0 24 400 300" width="400" height="300">
{dial}
<path class="gauge__needle" style="--angle:{angle}deg" d="M200 210V126" />
<circle cx="200" cy="210" r="14" fill="#13202c" /><circle cx="200" cy="210" r="5" fill="#fff" />
<text class="gauge__readout" x="200" y="282" text-anchor="middle">{readout}</text>
<text class="gauge__caption" x="200" y="312" text-anchor="middle">{caption}</text>
            </svg>
          </div>"""


def expand(body, posts, prefix, meta):
    body = re.sub(r"\{\{gauge:([-\d.]+):([^:}]+):([^}]+)\}\}", lambda m: gauge(*m.groups()), body)
    body = body.replace("{{P}}", prefix)
    body = re.sub(r"\{\{icon:([\w-]+)\}\}", lambda m: icon(m.group(1), prefix), body)
    body = body.replace("{{PHONE}}", PHONE).replace("{{TEL}}", TEL)
    body = re.sub(r"\{\{related:(\w+)\}\}", lambda m: related_block(posts, prefix, m.group(1)), body)
    body = body.replace("{{latest_posts}}", related_block(posts, prefix, "__none__", "Latest advice"))
    if "{{post_list}}" in body:
        items = "\n".join(
            f"""          <li><a href="{p['slug']}.html"><time datetime="{p['date']}">{nice_date(p['date'])}</time><h2>{p['title_h1']}</h2><p>{p['excerpt']}</p></a></li>"""
            for p in posts)
        body = body.replace("{{post_list}}", items)
    return body


def page_hero_crumbs(crumbs, prefix):
    out = []
    for i, (name, url) in enumerate(crumbs):
        if i == len(crumbs) - 1:
            out.append(f'<li aria-current="page">{name}</li>')
        else:
            href = prefix + url.lstrip("/") if url != "/" else (prefix or "./")
            if prefix == "/" and url == "/":
                href = "/"
            out.append(f'<li><a href="{href}">{name}</a></li>')
    return '<ol class="crumbs">' + "".join(out) + "</ol>"


def render(meta, posts):
    prefix = meta.get("prefix", "")
    schemas = list(meta.get("schemas", []))
    crumbs = meta.get("crumbs")
    if crumbs:
        schemas.append(breadcrumbs(crumbs))
    if meta.get("service"):
        s = meta["service"]
        schemas.insert(0, {"@context": "https://schema.org", "@type": "Service", "name": s["name"],
                           "serviceType": s.get("type", s["name"]), "description": s["description"],
                           "url": DOMAIN + meta["url"], "provider": BUSINESS_REF,
                           "areaServed": [{"@type": "Country", "name": "United Kingdom"},
                                          {"@type": "Place", "name": "London"},
                                          {"@type": "Place", "name": "Home Counties"}]})
    body = expand(meta["body"], posts, prefix, meta)
    if meta.get("faq"):
        schemas.append(faq_schema(body))
    if meta.get("post"):
        schemas.insert(0, {
            "@context": "https://schema.org", "@type": "BlogPosting",
            "headline": html.unescape(meta["title_h1"]), "description": html.unescape(meta["description"]),
            "datePublished": meta["date"], "dateModified": meta.get("updated", meta["date"]),
            "author": org(), "publisher": org(),
            "image": DOMAIN + "/assets/og-image.png",
            "mainEntityOfPage": {"@type": "WebPage", "@id": DOMAIN + meta["url"]}})
    if crumbs:
        body = body.replace("{{crumbs}}", page_hero_crumbs(crumbs, prefix))
    page = (head(meta, prefix, schemas) + "\n"
            + f'<body data-page="{meta.get("nav", "")}" data-root="{prefix}">\n'
            + header(prefix, meta.get("nav")) + "\n\n  <main id=\"main\">\n"
            + body.rstrip() + "\n  </main>\n\n" + footer(prefix))
    return page


def post_body(meta, posts):
    """Wrap a post's article HTML in the standard post layout."""
    prefix = "../"
    links = "".join(
        f'<li><a href="{prefix}{SERVICE_LINKS[k][0]}">{SERVICE_LINKS[k][1]}</a></li>' for k in meta.get("services", []))
    hero = f"""    <section class="page-hero on-dark">
      <div class="wrap">
        <div>
          {{{{crumbs}}}}
          <span class="eyebrow">{meta.get('kicker', 'Advice')}</span>
          <h1>{meta['title_h1']}</h1>
          <p class="page-hero__lede">{meta['description']}</p>
          <p class="post-meta"><span>By {BRAND}</span><time datetime="{meta['date']}">{nice_date(meta['date'])}</time><span>{meta['read']} min read</span></p>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap post-layout">
        <article class="article">
{meta['body'].strip()}

          <div class="post-cta">
            <h2>{meta.get('cta_title', 'Want us to take a look at your valves?')}</h2>
            <p>{meta.get('cta_text', "Tell us roughly how many TMVs you've got and where you are. We'll come back with a clear, fixed quote.")}</p>
            <div class="actions">
              <button class="btn btn--hot" type="button" data-open-enquiry="{meta.get('topic', 'TMV servicing')}">Get a quote</button>
              <a class="btn btn--line" href="{{{{TEL}}}}">Call {{{{PHONE}}}}</a>
            </div>
          </div>
        </article>

        <aside class="post-aside" aria-label="Related">
          <div class="contact-panel on-dark">
            <h3>Talk to an engineer</h3>
            <p>Questions about your valves? Give us a ring, we're happy to help.</p>
            <a class="big-phone" href="{{{{TEL}}}}">{{{{PHONE}}}}</a>
            <button class="btn btn--hot" type="button" data-open-enquiry="{meta.get('topic', 'TMV servicing')}">Request a quote</button>
          </div>
          <div class="aside-links">
            <h3>Related services</h3>
            <ul>{links}</ul>
          </div>
        </aside>
      </div>
    </section>

    {{{{related:{meta['tags'][0]}:{meta['slug']}}}}}
"""
    return hero


def main():
    posts = []
    for f in sorted((SRC / "blog").glob("*.html")):
        m = parse(f)
        m["post"] = True
        m["prefix"] = "../"
        m["url"] = f"/blog/{m['slug']}.html"
        m["out"] = f"blog/{m['slug']}.html"
        m["nav"] = "blog"
        m.setdefault("title_h1", m["title"])
        words = len(re.sub(r"<[^>]+>", " ", m["body"]).split())
        m["words"] = words
        m["read"] = max(3, round(words / 220))
        m["crumbs"] = [["Home", "/"], ["Advice", "/blog/"], [m.get("crumb", m["title"]), m["url"]]]
        posts.append(m)
    posts.sort(key=lambda p: p["date"], reverse=True)

    pages = [parse(f) for f in sorted(SRC.glob("*.html"))]
    built = []
    for m in pages:
        out = ROOT / m["out"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(m, posts))
        built.append(m)

    for m in posts:
        m_body = post_body(m, posts)
        # related block for posts: same tag, excluding itself
        m_body = re.sub(r"\{\{related:(\w+):([\w-]+)\}\}",
                        lambda x: related_block(posts, "../", x.group(1), "Keep reading", exclude=x.group(2),
                                                tags=m.get("tags")), m_body)
        m2 = dict(m, body=m_body)
        (ROOT / m["out"]).write_text(render(m2, posts))
        print(f"post {m['slug']}: {m['words']} words")

    # sitemap
    urls = []
    for m in built:
        if m.get("noindex"):
            continue
        urls.append((DOMAIN + m["url"], m.get("lastmod", TODAY)))
    for m in posts:
        urls.append((DOMAIN + m["url"], m.get("updated", m["date"])))
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    xml += [f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>" for u, d in urls]
    xml.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(xml) + "\n")
    print(f"Built {len(built)} pages, {len(posts)} posts, sitemap with {len(urls)} URLs")


if __name__ == "__main__":
    main()
