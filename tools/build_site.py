#!/usr/bin/env python3
"""Static site build for goravgupta.com.

    python tools/build_site.py

Reads  src/pages/*.html            designed pages: a <!--meta {json} --> block, then the body
       src/content/pages|posts/    pages and blog posts imported from the old WordPress site
       src/partials/*.html         head, header, footer, floating, intro (shared by every page)
Writes index.html, <path>/index.html for every page, blog/ and blog/page/N/, 404.html,
       sitemap.xml and assets/css/bundle.css

Placeholders available in partials and designed pages:
    {{root}}   relative path back to the site root ("" on the home page, "../" one level down, ...)
    {{wa}} {{waicon}}              WhatsApp link and glyph
    {{delhi}} {{gurugram}}         the two Google Business listings
    {{since}} {{years}}            year of the M.D., and years since (see PRACTICE_SINCE)
    {{exp}}                        the experience figure, "40+" (see EXPERIENCE)
    {{bio_short}} {{bio_long}}     the doctor's biography blocks (one source for the whole site)
    {{index_conditions}} {{index_mental_health}} {{index_local}} {{latest_posts}}   generated link lists
    {{films_player}}   shared page fragment (see INCLUDES)
The build needs no server. Nothing runs in the browser to assemble a page.
"""
import datetime
import hashlib
import json
import math
import pathlib
import re
import sys
import urllib.parse

import hub_pages
import tests_pages
import faq_pages

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'src'
SITE = 'https://goravgupta.com'

# Same order the single page linked them, then the two newest layers.
CSS = ['site', 'cinematic', 'films', 'refine', 'warm', 'calm', 'bloom', 'pro', 'spatial',
       'fix', 'polish', 'touchup', 'tulasi', 'taste', 'refresh', 'pages', 'articles', 'booking', 'navy', 'home2', 'films2', 'about2', 'menu', 'tests', 'hub', 'faq', 'final']

WA = 'https://wa.me/918800000255?text=Hello%20Dr.%20Gupta%27s%20team%2C%20I%27d%20like%20to%20book%20a%20consultation.'
WAICON = ('<svg class="wai" viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true">'
          '<path d="M20.5 3.5A11 11 0 0 0 3.2 17.3L2 22l4.8-1.2A11 11 0 1 0 20.5 3.5zM12 20.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-2.8.7.8-2.7-.2-.3a8.2 8.2 0 1 1 6.7 3.7zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.6.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3a.5.5 0 0 0 0-.5l-.8-1.9c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.8 11.9 11.9 0 0 0 4.6 4c1.7.7 2.4.8 3.2.7a2.7 2.7 0 0 0 1.8-1.3 2.2 2.2 0 0 0 .2-1.3c-.1-.1-.3-.2-.6-.3z"/></svg>')
DELHI = 'https://share.google/T2NTrfaXPM0Pgc0wf'
GURUGRAM = 'https://share.google/ZI81WGD0iUjLSohvh'

# The one source for "years in practice". Change the year here, then rebuild.
# {{since}} is the year; {{years}} is how many years ago that was (it rolls forward each January).
PRACTICE_SINCE = 1997   # the year the M.D. was completed; used for the training dates
# The experience figure shown to visitors ({{exp}}), as given by the client. Change it here, then rebuild.
EXPERIENCE = '40+'

# Page fragments shared by more than one designed page: {{placeholder}} -> src/partials/<file>.
INCLUDES = {'films_player': 'films-player.html'}

NAV = ['home', 'about', 'journey', 'services', 'resources', 'contact']
POSTS_PER_PAGE = 12

# The doctor's biography, from the old site. Short form closes service pages; long form closes blog posts.
BIO_SHORT = ('Doctor Gorav Gupta is a reputed senior psychiatrist in Delhi. His educational qualification is M.B.B.S, M.D (Psychiatry). '
             'He has {exp} years of experience, with a keen interest in de-addiction medicine and rehabilitation.')
BIO_LONG = ('<p>Dr. Gorav Gupta, Senior Consultant Psychiatrist of the Indian Sub Continent, practices in Delhi NCR. He completed his MBBS from the '
            'prestigious institute, Maulana Azad Medical College (Delhi University) and M.D. from Lady Hardinge Medical College (Delhi University) in 1997. '
            'He is renowned for pioneering super specialized work in psychosocial rehabilitation in psychiatry.</p>'
            '<p>He holds eminent positions of responsibility and contributes actively in Professional Bodies and NGOs like:</p>'
            '<ul><li>President of Mental Research Society</li><li>Life Fellow, Indian Psychiatric Society</li><li>Life Member, Indian Medical Association</li>'
            '<li>Life Member of Indian Association of Private Psychiatry</li><li>Life Member of Delhi Psychiatric Society</li>'
            '<li>Member of the National Task Force on Brain Health NITI Aayog</li>'
            '<li>Member of Executive Council of National Institute of Mental Health Rehabilitation (NIMHR)</li></ul>')

ASSESS = ('<aside class="assess"><div><h2>Take a step towards better mental health</h2>'
          '<p>Discover your mental well-being with our comprehensive Mental Health Assessment Tests. '
          'Get personalized insights to guide your journey toward a healthier mind.</p></div>'
          '<a class="btn" href="{root}mental-health-assessment-tests/">Test your mental health wellbeing</a></aside>')


def read(p):
    return pathlib.Path(p).read_text(encoding='utf-8')


def digest(path):
    return hashlib.md5(pathlib.Path(path).read_bytes()).hexdigest()[:8]


def bundle_css():
    """Concatenate the layers in order and drop comments: one request instead of sixteen."""
    parts = []
    for name in CSS:
        css = read(ROOT / 'assets' / 'css' / (name + '.css'))
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
        parts.append(css.strip())
    out = '\n'.join(parts) + '\n'
    (ROOT / 'assets' / 'css' / 'bundle.css').write_text(out, encoding='utf-8', newline='\n')
    return hashlib.md5(out.encode('utf-8')).hexdigest()[:8]


def fill(tpl, vars_, where):
    def sub(m):
        k = m.group(1)
        if k not in vars_:
            sys.exit('build error: unknown placeholder {{%s}} in %s' % (k, where))
        return str(vars_[k])
    return re.sub(r'\{\{([a-z_]+)\}\}', sub, tpl)


def parse(text, name):
    m = re.match(r'\s*<!--meta\s*(\{.*?\})\s*-->\s*', text, re.S)
    if not m:
        sys.exit('build error: %s has no <!--meta {...}--> block' % name)
    return json.loads(m.group(1)), text[m.end():]


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def url_path(path):
    """Percent-encode a site path for use in URLs (some blog slugs are Hindi)."""
    return urllib.parse.quote(path, safe='/%')


def pretty_date(iso):
    d = datetime.date.fromisoformat(iso)
    return '%d %s %d' % (d.day, d.strftime('%B'), d.year)


def depth_root(path):
    n = len([p for p in path.split('/') if p])
    return '../' * n


def crumb_html(crumbs):
    """crumbs: list of (label, href or None). The last one is the current page."""
    out = []
    for i, (label, href) in enumerate(crumbs):
        if href is not None:
            out.append('<a href="%s">%s</a>' % (href, label))
        else:
            out.append('<span aria-current="page">%s</span>' % label)
        if i < len(crumbs) - 1:
            out.append('<span aria-hidden="true">/</span>')
    return '<nav class="crumb" aria-label="Breadcrumb">%s</nav>' % ''.join(out)


def ph(crumbs, h1, lede='', meta_line=''):
    return ('<header class="ph"><div class="ph__in">%s<h1>%s</h1>%s%s</div></header>'
            % (crumb_html(crumbs), h1, ('<p class="ph__meta">%s</p>' % meta_line) if meta_line else '',
               ('<p class="ph__lede">%s</p>' % lede) if lede else ''))


def add_toc(body):
    """Give every h2 an id and build an 'On this page' list from them (only worth it with 3 or more)."""
    heads = re.findall(r'<h2>(.*?)</h2>', body, re.S)
    if len(heads) < 3:
        return body, ''
    used = set()
    items = []

    def repl(m):
        text = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        base = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')[:48] or 'section'
        sid, n = base, 2
        while sid in used:
            sid = '%s-%d' % (base, n)
            n += 1
        used.add(sid)
        items.append('<li><a href="#%s">%s</a></li>' % (sid, text))
        return '<h2 id="%s">%s</h2>' % (sid, m.group(1))

    body = re.sub(r'<h2>(.*?)</h2>', repl, body, flags=re.S)
    return body, '<nav class="toc" aria-label="On this page"><p class="side__t">On this page</p><ul>%s</ul></nav>' % ''.join(items)


def author_box(root, long_form, years_text):
    bio = BIO_LONG if long_form else '<p>%s</p>' % years_text
    return ('<aside class="author" aria-label="About the author"><img class="author__img" src="%sassets/img/portrait-close-col.webp" '
            'alt="Dr. Gorav Gupta" width="96" height="112" loading="lazy"><div><p class="author__n">Dr. Gorav Gupta</p>%s'
            '<a class="more__a" href="%sabout-us/">More about Dr. Gupta <i>→</i></a></div></aside>' % (root, bio, root))


def main():
    css_v = bundle_css()
    js_v = {p.stem: digest(p) for p in (ROOT / 'assets' / 'js').glob('*.js')}
    head_t, header_t, footer_t, float_t, intro_t = (
        read(SRC / 'partials' / (n + '.html')) for n in ('head', 'header', 'footer', 'floating', 'intro'))
    home_ld = read(SRC / 'partials' / 'jsonld-home.json').strip()
    groups = json.loads(read(SRC / 'content' / 'groups.json')) if (SRC / 'content' / 'groups.json').exists() else {'condition_groups': []}
    years = datetime.date.today().year - PRACTICE_SINCE
    bio_short = BIO_SHORT.format(exp=EXPERIENCE)

    # ---------------------------------------------------------------- load sources
    designed = []
    for f in sorted((SRC / 'pages').glob('*.html')):
        meta, body = parse(read(f), f.name)
        meta['_body'] = body
        meta.setdefault('path', meta.get('slug', ''))
        meta['kind'] = 'designed'
        designed.append(meta)

    content = []
    for f in sorted((SRC / 'content').glob('*/*.html')):
        meta, body = parse(read(f), f.name)
        meta['_body'] = body
        content.append(meta)
    by_slug = {c['slug']: c for c in content if c['kind'] == 'page'}
    posts = sorted([c for c in content if c['kind'] == 'post'], key=lambda c: (c['date'], c['slug']), reverse=True)

    def href(item, root):
        return root + url_path(item['path']) + '/'

    # ---------------------------------------------------------------- generated link lists
    def lst(root, slugs, with_desc=False):
        out = []
        for s in slugs:
            c = by_slug.get(s)
            if not c:
                continue
            d = ('<span>%s</span>' % esc(c['description'])) if with_desc and c.get('description') else ''
            out.append('<li><a href="%s"><b>%s</b>%s</a></li>' % (href(c, root), c['title'], d))
        return '<ul class="idx">%s</ul>' % ''.join(out)

    def index_conditions(root):
        html = []
        for title, slugs in groups['condition_groups']:
            html.append('<div class="idx__g"><h3>%s</h3>%s</div>' % (title, lst(root, slugs)))
        return '<div class="idx__grid">%s</div>' % ''.join(html)

    def index_group(root, group):
        slugs = [c['slug'] for c in content if c['kind'] == 'page' and c['group'] == group]
        order = {'mental-health-assessment-tests': 0, 'early-warning-signs-scale-for-bipolar-disorder': 1,
                 'early-relapse-signs-of-schizophrenia': 2, 'substance-use-disorder': 3, 'substance-use-disorder-vs-social-use': 4,
                 'psychiatrist-in-delhi': 0, 'psychiatrist-in-gurgaon': 1, 'psychiatrist-in-india': 2}
        slugs.sort(key=lambda s: order.get(s, 9))
        return lst(root, slugs, with_desc=(group == 'mental-health'))

    def latest_posts(root, n=6):
        out = []
        for p in posts[:n]:
            out.append('<li><a href="%s"><time datetime="%s">%s</time><b>%s</b></a></li>' % (href(p, root), p['date'], pretty_date(p['date']), p['title']))
        return '<ul class="idx idx--posts">%s</ul>' % ''.join(out)

    # ---------------------------------------------------------------- blog index pages (generated)
    n_pages = max(1, math.ceil(len(posts) / POSTS_PER_PAGE))
    blog_pages = []
    for i in range(n_pages):
        chunk = posts[i * POSTS_PER_PAGE:(i + 1) * POSTS_PER_PAGE]
        path = 'blog' if i == 0 else 'blog/page/%d' % (i + 1)
        blog_pages.append({'kind': 'blog-index', 'path': path, 'page': i + 1, 'chunk': chunk, 'nav': 'resources',
                           'title': 'Blog | Dr. Gorav Gupta' if i == 0 else 'Blog, page %d | Dr. Gorav Gupta' % (i + 1),
                           'description': 'Articles by Dr. Gorav Gupta on mental health, addiction, anxiety, depression, OCD and treatment.',
                           'modified': chunk[0]['modified'] if chunk else ''})

    tests = tests_pages.load()   # data/tests/*.json -> /tests/ and /tests/<slug>/
    faq = faq_pages.load()       # data/faq/*.json -> /faq/ and /faq/<topic>/
    all_items = designed + content + blog_pages + tests_pages.items(tests) + faq_pages.items(faq)

    # ---------------------------------------------------------------- render
    sitemap = []
    for pg in all_items:
        path = pg['path']
        is404 = path == '404'
        root = '/' if is404 else depth_root(path)
        canonical = SITE + '/' + ((url_path(path) + '/') if path and not is404 else '')
        kind = pg['kind']

        v = {'root': root, 'wa': WA, 'waicon': WAICON, 'delhi': DELHI, 'gurugram': GURUGRAM,
             'since': PRACTICE_SINCE, 'years': years, 'exp': EXPERIENCE, 'bio_short': bio_short, 'bio_long': BIO_LONG,
             'index_conditions': index_conditions(root), 'index_mental_health': index_group(root, 'mental-health'),
             'index_local': index_group(root, 'local'), 'latest_posts': latest_posts(root),
             'resources_menu': tests_pages.menu(root, tests, path, faq_pages.menu_item(root, faq, path)),
             'services_menu': hub_pages.services_menu(root, groups, by_slug, path)}
        if path == 'resources':
            v['resources_hub'] = hub_pages.resources_hub(root, posts, tests, href, pretty_date)
        for key, name in INCLUDES.items():
            if (SRC / 'partials' / name).exists():
                v[key] = fill(read(SRC / 'partials' / name), v, name)

        title = pg.get('seo_title') or pg['title']
        if kind == 'designed':
            seo_title, desc = pg['title'], pg['description']
        else:
            seo_title, desc = (title if kind != 'blog-index' else pg['title']), pg.get('description') or ''
        desc = re.sub(r'\s+', ' ', desc).strip() or 'Dr. Gorav Gupta, senior psychiatrist in Delhi NCR.'

        # structured data
        if path == '':
            ld = '<script type="application/ld+json">%s</script>' % home_ld
        elif is404:
            ld = ''
        else:
            label = pg.get('crumb') or pg['title']
            items = [{'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE + '/'}]
            if kind == 'post':
                items.append({'@type': 'ListItem', 'position': 2, 'name': 'Blog', 'item': SITE + '/blog/'})
            items.append({'@type': 'ListItem', 'position': len(items) + 1, 'name': label, 'item': canonical})
            crumbs_ld = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': items}
            ld = '<script type="application/ld+json">%s</script>' % json.dumps(crumbs_ld, ensure_ascii=False)
            if kind == 'post':
                art = {'@context': 'https://schema.org', '@type': 'BlogPosting', 'headline': pg['title'], 'datePublished': pg['date'],
                       'dateModified': pg.get('modified') or pg['date'], 'mainEntityOfPage': canonical,
                       'author': {'@type': 'Person', 'name': 'Dr. Gorav Gupta', 'url': SITE + '/about-us/'}}
                ld += '<script type="application/ld+json">%s</script>' % json.dumps(art, ensure_ascii=False)
            ld += pg.get('ld_extra', '')

        scripts_list = pg.get('scripts', [])
        preload = ''.join('<link rel="preload" as="image" href="%s%s" fetchpriority="high">' % (root, p) for p in pg.get('preload', []))
        scripts = ''.join(
            '<script src="%sassets/js/%s.js?v=%s"%s></script>' % (root, s, js_v[s], '' if s == 'site' else ' defer')
            for s in ['site'] + scripts_list + ['calm', 'spatial'])
        v.update({'title': esc(seo_title), 'description': esc(desc), 'canonical': canonical,
                  'htmlclass': 'inner go' if path else '', 'jsonld': ld, 'preload': preload, 'cssv': css_v})

        head = fill(head_t, v, 'head')
        if pg.get('noindex') or (kind == 'blog-index' and pg['page'] > 1):
            head = head.replace('index,follow,max-image-preview:large', 'noindex,follow')

        # navigation state
        nav_key = pg.get('nav')
        if not nav_key and kind in ('page', 'post'):
            nav_key = 'services' if pg['group'] in ('services', 'local') else 'resources'
        header = header_t
        for n in NAV:
            header = header.replace('{{cur:%s}}' % n, ' aria-current="page" class="act"' if n == nav_key else '')
        header = fill(header, v, 'header')
        header = re.sub(r'class="dd__t"( href="[^"]*")( aria-current="page")? class="act"', lambda m: 'class="dd__t act"' + m.group(1) + (m.group(2) or '') , header)   # one class attribute
        if 'aria-current="page"' in v['resources_menu'] + v['services_menu']:   # the menu item is the current page, so the top link is only highlighted
            header = re.sub(r'(class="dd__t act" href="[^"]*") aria-current="page"', lambda m: m.group(1), header, count=1)

        # body
        if kind == 'designed':
            body = fill(pg['_body'], v, 'page ' + (path or 'home'))
        elif kind == 'tests-index':
            body = tests_pages.index_body(pg, root, ph)
        elif kind == 'test':
            body = tests_pages.test_body(pg, root, ph, WA)
        elif kind == 'faq-index':
            body = faq_pages.index_body(pg, root, ph, WA)
        elif kind == 'faq':
            body = faq_pages.topic_body(pg, root, ph, WA)
        elif kind == 'blog-index':
            cards = ''.join(
                '<li class="reveal"><a href="%s"><time datetime="%s">%s</time><h2>%s</h2><p>%s</p><span class="plist__go">Read article <i>→</i></span></a></li>'
                % (href(p, root), p['date'], pretty_date(p['date']), p['title'], esc(p.get('excerpt', ''))) for p in pg['chunk'])
            pager = ''
            if n_pages > 1:
                links = []
                for j in range(1, n_pages + 1):
                    target = root + ('blog/' if j == 1 else 'blog/page/%d/' % j)
                    links.append('<a href="%s"%s>%d</a>' % (target, ' aria-current="page"' if j == pg['page'] else '', j))
                prev = ('<a class="pager__s" href="%s">← Newer</a>' % (root + ('blog/' if pg['page'] == 2 else 'blog/page/%d/' % (pg['page'] - 1)))) if pg['page'] > 1 else ''
                nxt = ('<a class="pager__s" href="%sblog/page/%d/">Older →</a>' % (root, pg['page'] + 1)) if pg['page'] < n_pages else ''
                pager = '<nav class="pager" aria-label="Blog pages">%s<span class="pager__n">%s</span>%s</nav>' % (prev, ''.join(links), nxt)
            crumbs = [('Home', root), ('Blog', None)] if pg['page'] == 1 else [('Home', root), ('Blog', root + 'blog/'), ('Page %d' % pg['page'], None)]
            body = (ph(crumbs, 'Blog', 'Articles on mental health, addiction, anxiety, depression, OCD and treatment, by Dr. Gorav Gupta.')
                    + '<section class="sec plist__sec" aria-label="Articles"><ul class="plist">%s</ul>%s</section>' % (cards, pager))
        else:
            group = pg['group']
            if group in ('services', 'local'):
                crumbs = [('Home', root), ('Services', root + 'services/'), (pg['title'], None)]
            elif group == 'blog':
                crumbs = [('Home', root), ('Blog', root + 'blog/'), (esc(pg['title']), None)]
            else:
                crumbs = [('Home', root), ('Resources', root + 'resources/'), (pg['title'], None)]
            lede = pg.get('subtitle') or ''     # a post's first paragraph is its own opening, so it is not repeated as a subtitle
            meta_line = ('<time datetime="%s">%s</time>' % (pg['date'], pretty_date(pg['date']))) if kind == 'post' else ''
            lang = ' lang="%s"' % pg['lang'] if pg.get('lang') else ''
            inner = tests_pages.source_callout(root, tests, pg['slug']) + fill(pg['_body'], v, 'content ' + path)
            after = author_box(root, kind == 'post', bio_short)
            if group in ('services', 'local'):
                after += ASSESS.format(root=root)
            if kind == 'post':
                i = next((k for k, p in enumerate(posts) if p['slug'] == pg['slug']), 0)
                near = [p for p in posts[max(0, i - 1):i + 3] if p['slug'] != pg['slug']][:3]
                if near:
                    after += ('<section class="related" aria-labelledby="rel-h"><h2 id="rel-h">More from the blog</h2><ul class="idx idx--posts">%s</ul>'
                              '<p class="more"><a class="more__a" href="%sblog/">All articles <i>→</i></a></p></section>'
                              % (''.join('<li><a href="%s"><time datetime="%s">%s</time><b>%s</b></a></li>' % (href(p, root), p['date'], pretty_date(p['date']), p['title']) for p in near), root))
            inner, toc = add_toc(inner)
            side = ('<aside class="prose__side"><div class="side__box">%s<p class="side__t">Book a consultation</p>'
                    '<p>Call +91 88000 00255 or message the team on WhatsApp.</p>'
                    '<a class="btn" href="%scontactus/">Book Consultation</a></div></aside>' % (toc, root))
            body = (ph(crumbs, esc(pg['title']) if kind == 'post' else pg['title'], lede, meta_line)
                    + '<article class="sec prose"><div class="prose__main"><div class="prose__in"%s>%s</div><div class="prose__after">%s</div></div>%s</article>'
                    % (lang, inner, after, side))

        html = (head
                + (fill(intro_t, v, 'intro') if path == '' else '')
                + header
                + '<main id="main">' + body + '</main>'
                + fill(footer_t, v, 'footer') + fill(float_t, v, 'floating')
                + scripts + '</body></html>\n')

        if is404:
            out = ROOT / '404.html'
        elif path == '':
            out = ROOT / 'index.html'
        else:
            out = ROOT / pathlib.PurePosixPath(path) / 'index.html'
            out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding='utf-8', newline='\n')
        if not is404 and not pg.get('noindex') and not (kind == 'blog-index' and pg['page'] > 1):
            sitemap.append((canonical, pg.get('modified') or pg.get('date') or ''))

    urls = ''.join('<url><loc>%s</loc>%s</url>' % (u, ('<lastmod>%s</lastmod>' % m) if m else '') for u, m in sitemap)
    (ROOT / 'sitemap.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">%s</urlset>\n' % urls, encoding='utf-8', newline='\n')
    print('built %d pages (%d designed, %d imported pages, %d posts, %d blog index pages); sitemap has %d urls; css bundle %s'
          % (len(all_items), len(designed), len(by_slug), len(posts), len(blog_pages), len(sitemap), css_v))


if __name__ == '__main__':
    main()
