#!/usr/bin/env python3
"""Static site build for goravgupta.com.

    python tools/build_site.py

Reads  src/pages/*.html            designed pages: a <!--meta {json} --> block, then the body
       src/content/pages|posts/    pages and blog posts imported from the old WordPress site
       src/partials/*.html         head, header, footer, floating, intro (shared by every page)
Writes index.html, <path>/index.html for every page, blog/ and blog/p/N/, 404.html,
       sitemap.xml and assets/css/bundle.css

Placeholders available in partials and designed pages:
    {{root}}   relative path back to the site root ("" on the home page, "../" one level down, ...)
    {{wa}} {{waicon}}              WhatsApp link and glyph
    {{delhi}} {{gurugram}}         the two Google Business listings
    {{since}} {{years}}            year of the M.D., and years since (see PRACTICE_SINCE)
    {{exp}} {{fee}} {{opd_delhi}} ...  the shared facts from data/site.json (see PLACEHOLDERS)
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

import booking
import hub_pages
import tests_pages
import faq_pages
import taxonomy_pages
import service_pages

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'src'
# Search Console shows the live site on the www host, so canonicals, OG URLs, structured data and the
# sitemap all use it. The single 301 from the bare host to www lives in vercel.json.
SITE = 'https://www.goravgupta.com'

# Same order the single page linked them, then the two newest layers.
CSS = ['fonts', 'site', 'cinematic', 'films', 'refine', 'warm', 'calm', 'bloom', 'pro', 'spatial',
       'fix', 'polish', 'touchup', 'tulasi', 'taste', 'refresh', 'pages', 'articles', 'booking', 'navy', 'home2', 'films2', 'about2', 'menu', 'tests', 'hub', 'faq', 'service', 'form', 'final', 'elevate']

WA_NUMBER = '918800000255'
# Where a page has a subject, the WhatsApp message says so, so the call centre opens with context.
LOCAL_TOPIC = {'psychiatrist-in-delhi': 'in New Delhi', 'psychiatrist-in-gurgaon': 'in Gurugram'}


def wa_link(topic=''):
    """topic is a phrase that follows "a consultation": "about de-addiction", "in New Delhi"."""
    msg = "Hello Dr. Gupta's team, I'd like to book a consultation%s." % ((' ' + topic) if topic else '')
    return 'https://wa.me/%s?text=%s' % (WA_NUMBER, urllib.parse.quote(msg))


WA = wa_link()
WAICON = ('<svg class="wai" viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true">'
          '<path d="M20.5 3.5A11 11 0 0 0 3.2 17.3L2 22l4.8-1.2A11 11 0 1 0 20.5 3.5zM12 20.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-2.8.7.8-2.7-.2-.3a8.2 8.2 0 1 1 6.7 3.7zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.6.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3a.5.5 0 0 0 0-.5l-.8-1.9c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.8 11.9 11.9 0 0 0 4.6 4c1.7.7 2.4.8 3.2.7a2.7 2.7 0 0 0 1.8-1.3 2.2 2.2 0 0 0 .2-1.3c-.1-.1-.3-.2-.6-.3z"/></svg>')
DELHI = 'https://share.google/T2NTrfaXPM0Pgc0wf'
GURUGRAM = 'https://share.google/Mvj2ZQKXahLxnIGjO'

# Every fact that appears on more than one page lives in data/site.json: experience, the centres, timings,
# the fee. Edit it there and rebuild; no page carries its own copy of a shared fact.
FACTS = json.loads((ROOT / 'data' / 'site.json').read_text(encoding='utf-8'))

# {{placeholder}} -> the dotted key in data/site.json it prints.
PLACEHOLDERS = {
    'exp': 'doctor.experience', 'reg_no': 'doctor.registration_number', 'md_subject': 'doctor.md_subject',
    'fee': 'consultation.fee', 'session': 'consultation.minutes',
    'phone': 'consultation.phone', 'phone_href': 'consultation.phone_href', 'email': 'consultation.email',
    'opd_delhi': 'centres.delhi.opd', 'opd_gurugram': 'centres.gurugram.opd', 'opd_online': 'consultation.online_opd',
    'clinic_delhi': 'centres.delhi.clinic_name', 'clinic_gurugram': 'centres.gurugram.clinic_name',
    'clinic_mehrauli': 'centres.mehrauli.clinic_name',
    'clinic_delhi_womens': 'centres.delhi_womens.clinic_name', 'clinic_delhi_mandi': 'centres.delhi_mandi.clinic_name',
    'clinic_noida': 'centres.noida.clinic_name',
    'addr_delhi': 'centres.delhi.address', 'addr_gurugram': 'centres.gurugram.address',
    'addr_mehrauli': 'centres.mehrauli.address',
    'addr_delhi_womens': 'centres.delhi_womens.address', 'addr_delhi_mandi': 'centres.delhi_mandi.address',
    'addr_noida': 'centres.noida.address',
    'beds_gurugram': 'centres.gurugram.beds', 'beds_mehrauli': 'centres.mehrauli.beds',
    'gmap_delhi': 'centres.delhi.maps', 'gmap_gurugram': 'centres.gurugram.maps', 'gmap_mehrauli': 'centres.mehrauli.maps',
    'gmap_delhi_womens': 'centres.delhi_womens.maps', 'gmap_delhi_mandi': 'centres.delhi_mandi.maps',
    'gmap_noida': 'centres.noida.maps',
    'role_gurugram': 'centres.gurugram.role', 'role_mehrauli': 'centres.mehrauli.role',
    'area_delhi': 'centres.delhi.area', 'area_gurugram': 'centres.gurugram.area', 'area_mehrauli': 'centres.mehrauli.area',
    'area_delhi_womens': 'centres.delhi_womens.area', 'area_delhi_mandi': 'centres.delhi_mandi.area',
    'area_noida': 'centres.noida.area',
    'badge_delhi': 'centres.delhi.badge', 'badge_gurugram': 'centres.gurugram.badge', 'badge_mehrauli': 'centres.mehrauli.badge',
    'badge_delhi_womens': 'centres.delhi_womens.badge', 'badge_delhi_mandi': 'centres.delhi_mandi.badge',
    'badge_noida': 'centres.noida.badge',
    'crisis_name': 'crisis.name', 'tulasi_url': 'tulasi.url',
    'founded': 'tulasi.founded', 'award_year': 'award.year', 'award_url': 'award.url',
    'rating': 'reviews.rating', 'review_count': 'reviews.count',
    'rpwd_act': 'tulasi.act', 'crisis_line': 'crisis.line', 'crisis_number': 'crisis.number',
}


def fact(key):
    """One fact from data/site.json, by dotted key ("centres.delhi.opd")."""
    v = FACTS
    for part in key.split('.'):
        v = v[part]
    return v


PRACTICE_SINCE = fact('doctor.md_year')   # {{since}} is the year; {{years}} is how many years ago (rolls forward each January)
EXPERIENCE = fact('doctor.experience')    # {{exp}}, the experience figure shown to visitors

# Page fragments shared by more than one designed page: {{placeholder}} -> src/partials/<file>.
INCLUDES = {'films_player': 'films-player.html', 'review_wall': 'review-wall.html'}

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


def css_blocks(css):
    """Split CSS into top-level blocks: (prelude, body)."""
    out, i, depth, start, pre, body_start = [], 0, 0, 0, '', 0
    while i < len(css):
        c = css[i]
        if c == '{':
            if depth == 0:
                pre = css[start:i]
                body_start = i + 1
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                out.append((pre.strip(), css[body_start:i]))
                start = i + 1
        i += 1
    return out


# Classes the scripts add at runtime, which no page's markup contains.
RUNTIME_CLASSES = {'js', 'open', 'ready', 'seen', 'go', 'fx', 'lock', 'hero-in', 'is-on', 'is-playing',
                   'is-clone', 'in', 'out', 'act', 'show', 'hide', 'on', 'off', 'sticky', 'stuck',
                   'reveal', 'vis', 'done', 'active', 'current', 'light', 'dark', 'scrolled'}
KEEP_AT = ('@keyframes', '@font-face', '@property', '@page', '@counter-style', '@import', '@charset')


def required_names(selector):
    """The classes and ids an element must actually have for this selector to match.

    Anything inside a functional pseudo-class is ignored. ":not(#s)" is a specificity
    hack whose id deliberately exists nowhere, and treating it as required would drop a
    rule that in fact matches everything. The same caution covers :is(), :where() and
    :has(), where a name is one alternative rather than a requirement.
    """
    stripped, prev = selector, None
    while stripped != prev:
        prev = stripped
        stripped = re.sub(r':[A-Za-z-]+\([^()]*\)', ' ', stripped)
    return set(re.findall(r'[.#]([A-Za-z0-9_-]+)', stripped))


def prune_css(css, tokens):
    """Drop selectors naming a class or id that exists nowhere in the built site.

    Conservative on purpose. A selector part goes only when every class and id it names is
    absent from every page, from the scripts and from RUNTIME_CLASSES. A part naming none
    of them (a tag, a pseudo-element, an attribute) is always kept, and so is anything
    inside @keyframes or @font-face. Selector lists are split on commas so a dead part
    never takes a live one with it; a list with a comma inside brackets (:is(), :not()) is
    left alone rather than parsed.
    """
    known = tokens | RUNTIME_CLASSES
    stats = [0, 0]

    def walk(body):
        out = []
        for pre, inner in css_blocks(body):
            low = pre.lower()
            if low.startswith(KEEP_AT):
                out.append('%s{%s}' % (pre, inner))
                continue
            if low.startswith('@'):
                nested = walk(inner)
                if nested.strip():
                    out.append('%s{%s}' % (pre, nested))
                continue
            if '(' in pre and ',' in pre[pre.find('('):]:
                out.append('%s{%s}' % (pre, inner))
                stats[0] += 1
                continue
            live = []
            for part in pre.split(','):
                names = required_names(part)
                if not names or names <= known:
                    live.append(part); stats[0] += 1
                else:
                    stats[1] += 1
            if live:
                out.append('%s{%s}' % (','.join(live), inner))
        return ''.join(out)

    pruned = walk(css)
    return pruned, stats[0], stats[1]


def minify_css(css):
    """Whitespace only: nothing here can change which rules match.

    Runs of whitespace collapse, and spaces are removed around the characters that cannot
    appear inside a selector or a value ({ } ; ,). A space before a colon is left alone,
    because "a :hover" and "a:hover" are different rules.
    """
    css = re.sub(r'\s+', ' ', css)
    css = re.sub(r'\s*([{};,])\s*', r'\1', css)
    css = re.sub(r';\}', '}', css)
    # inside a declaration block a colon always separates property from value, so the space
    # after it is never meaningful; in a selector it would be ("a :hover"), hence block-only
    css = re.sub(r'\{([^{}]*)\}', lambda m: '{' + re.sub(r':\s+', ':', m.group(1)) + '}', css)
    # combinators cannot be part of a name
    css = re.sub(r'\s*([>~])\s*', r'\1', css)
    return css.strip()


def bundle_css(tokens=None):
    """Concatenate the layers in order and drop comments: one request instead of sixteen."""
    parts = []
    for name in CSS:
        css = read(ROOT / 'assets' / 'css' / (name + '.css'))
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
        parts.append(css.strip())
    joined = minify_css('\n'.join(parts))
    if tokens:
        before = len(joined)
        joined, kept, dropped = prune_css(joined, tokens)
        print('css: dropped %d dead selectors of %d; %.1f KB -> %.1f KB'
              % (dropped, kept + dropped, before / 1024, len(joined) / 1024))
    out = joined + '\n'
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


FILMS_PUBLISHED = '2026-10-09'   # when the films were first published here (git history of assets/video/)


def films_ld(home_ld_text):
    """VideoObject for each film, from the titles and posters in the player partial."""
    src = read(SRC / 'partials' / 'films-player.html')
    titles = [re.sub(r'<[^>]+>', '', t).strip() for t in re.findall(r'<h3[^>]*>(.*?)</h3>', src, re.S)]
    posters = re.findall(r'poster="\{\{root\}\}([^"]+)"', src)
    mp4s = re.findall(r'src="\{\{root\}\}([^"]+\.mp4)"', src)
    out = []
    for i, name in enumerate(titles):
        if i >= len(posters) or i >= len(mp4s):
            break
        out.append({'@context': 'https://schema.org', '@type': 'VideoObject', 'name': name,
                    'description': name + ' — a short film with Dr. Gorav Gupta, Tulasi Healthcare.',
                    'thumbnailUrl': SITE + '/' + posters[i], 'contentUrl': SITE + '/' + mp4s[i],
                    'uploadDate': FILMS_PUBLISHED, 'publisher': {'@type': 'Organization', 'name': 'Dr. Gorav Gupta'}})
    return ''.join('<script type="application/ld+json">%s</script>' % json.dumps(v, ensure_ascii=False) for v in out)


def clinic_ld(centre, name_url):
    """MedicalClinic for a location page, from data/site.json."""
    node = {'@context': 'https://schema.org', '@type': 'MedicalClinic',
            'name': centre['clinic_name'], 'url': name_url,
            'medicalSpecialty': 'Psychiatric',
            'telephone': fact('consultation.phone'),
            'address': {'@type': 'PostalAddress', 'streetAddress': centre['address'], 'addressCountry': 'IN'}}
    if centre.get('opd'):
        node['openingHours'] = centre['opd']
    return '<script type="application/ld+json">%s</script>' % json.dumps(node, ensure_ascii=False)


LOCATION_CENTRE = {'psychiatrist-in-delhi': 'delhi', 'psychiatrist-in-gurgaon': 'gurugram'}


def fix_levels(html):
    """Imported posts jump from an h2 to an h4. Each heading is brought down to at most one level below the one before it."""
    prev, cur = 1, [2]
    def sub(m):
        if m.group(1):                       # a closing tag takes the level its opening tag was given
            return '</h%d' % cur[0]
        lvl = int(m.group(2)); new = min(lvl, prev_box[0] + 1)
        prev_box[0] = new; cur[0] = new
        return '<h%d' % new
    prev_box = [prev]
    return re.sub(r'<(/?)h([2-6])\b', lambda m: sub(m), html)


def main():
    CSSV = '__CSSV__'          # stands in until the pruned bundle has been hashed
    css_v = CSSV
    pages_out = []             # (path, html), written once the hash is known
    site_tokens = set()        # every class and id the built site uses
    js_v = {p.stem: digest(p) for p in (ROOT / 'assets' / 'js').glob('*.js')}
    head_t, header_t, footer_t, float_t, intro_t = (
        read(SRC / 'partials' / (n + '.html')) for n in ('head', 'header', 'footer', 'floating', 'intro'))
    home_ld = read(SRC / 'partials' / 'jsonld-home.json').strip()
    physician = next((n for n in json.loads(home_ld).get('@graph', []) if n.get('@type') == 'Physician'), None)
    physician_ld = ('<script type="application/ld+json">%s</script>'
                    % json.dumps(dict(physician, **{'@context': 'https://schema.org'}), ensure_ascii=False)) if physician else ''
    film_ld = films_ld(home_ld)
    groups = json.loads(read(SRC / 'content' / 'groups.json')) if (SRC / 'content' / 'groups.json').exists() else {'condition_groups': []}
    group_of = {slug: title for title, slugs in groups['condition_groups'] for slug in slugs}
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
    retired = []
    for f in sorted((SRC / 'content').glob('*/*.html')):
        meta, body = parse(read(f), f.name)
        # A "retired" page is kept as a source but not built: either a new page is served at its URL,
        # or vercel.json 301s it. The meta says which. Nothing links to one (see "no stale links" below).
        if meta.get('retired'):
            retired.append((meta['slug'], meta['retired']))
            continue
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
            out.append('<li><a href="%s"><b>%s</b>%s</a></li>' % (href(c, root), c.get('menu_title') or c['title'], d))
        return '<ul class="idx">%s</ul>' % ''.join(out)

    CG_ICONS = {
        'De-addiction and substance use': '<path d="M10.5 20.5a5 5 0 0 1-7-7l10-10a5 5 0 0 1 7 7z"/><path d="m8.5 8.5 7 7"/>',
        'Schizophrenia': '<path d="M9 4a3 3 0 0 0-3 3 3 3 0 0 0-2 5 3 3 0 0 0 2 5 3 3 0 0 0 3 3 2 2 0 0 0 3-1.5V5.5A2 2 0 0 0 9 4z"/><path d="M15 4a3 3 0 0 1 3 3 3 3 0 0 1 2 5 3 3 0 0 1-2 5 3 3 0 0 1-3 3 2 2 0 0 1-3-1.5"/>',
        'Mood disorders': '<path d="M2 12c2.5-6 5-6 7.5 0s5 6 7.5 0 3-4 5-4"/>',
        'Anxiety, OCD and stress': '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.2"/>',
        'Personality disorders': '<path d="M12 3 4 6v6c0 4.5 3.2 7.8 8 9 4.8-1.2 8-4.5 8-9V6z"/><path d="M9 12.5c.8 1.2 1.8 1.8 3 1.8s2.2-.6 3-1.8"/>',
        'Eating disorders': '<path d="M7 3v7a2 2 0 0 0 4 0V3M9 3v18M17 3c-2 2-3 5-3 8h3v10"/>',
    }

    def index_conditions(root):
        html = []
        for title, slugs in groups['condition_groups']:
            items = [by_slug[s] for s in slugs if s in by_slug]
            if not items:
                continue
            ico = '<span class="cg__ico" aria-hidden="true"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">%s</svg></span>' % CG_ICONS.get(title, '')
            rows = ''.join('<li><a href="%s"><span>%s</span><i aria-hidden="true">&rarr;</i></a></li>' % (href(c, root), c.get('menu_title') or c['title']) for c in items)
            html.append('<article class="cg reveal">%s<h3>%s</h3><p class="cg__n">%d %s</p><ul class="cg__l">%s</ul></article>'
                        % (ico, title, len(items), 'guide' if len(items) == 1 else 'guides', rows))
        return '<div class="cg__grid">%s</div>' % ''.join(html)

    def index_group(root, group):
        slugs = [c['slug'] for c in content if c['kind'] == 'page' and c['group'] == group]
        order = {'early-warning-signs-scale-for-bipolar-disorder': 1,
                 'early-relapse-signs-of-schizophrenia': 2, 'substance-use-disorder': 3, 'substance-use-disorder-vs-social-use': 4,
                 'psychiatrist-in-delhi': 0, 'psychiatrist-in-gurgaon': 1, 'psychiatrist-in-india': 2}
        slugs.sort(key=lambda s: order.get(s, 9))
        return lst(root, slugs, with_desc=(group == 'mental-health'))

    def latest_posts(root, n=6):
        out = []
        for p in posts[:n]:
            out.append('<li><a href="%s"><time datetime="%s">%s</time><b>%s</b></a></li>' % (href(p, root), p['date'], pretty_date(p['date']), p['title']))
        return '<ul class="idx idx--posts">%s</ul>' % ''.join(out)

    # ---------------------------------------------------------------- blog index page (generated)
    # One page now, not nine: articles_hub() pages the full set client-side (assets/js/hub.js),
    # same as /resources/ did before the two were split apart. Old /blog/p/N/ URLs 301 (vercel.json).
    blog_pages = [{'kind': 'blog-index', 'path': 'blog', 'page': 1, 'chunk': posts, 'nav': 'resources', 'scripts': ['hub'],
                   'title': 'Mental Health & Wellness Blog | Dr. Gorav Gupta',
                   'description': 'Read expert articles by psychiatrist Dr. Gorav Gupta on anxiety, depression, OCD, addiction, bipolar disorder and schizophrenia treatment.',
                   'modified': posts[0]['modified'] if posts else ''}]

    shared = {k: fact(key) for k, key in PLACEHOLDERS.items()}

    def fill_facts(text):
        """The shared facts, for text used outside a template: excerpts, titles, card copy."""
        for k, val in shared.items():
            text = text.replace('{{%s}}' % k, str(val))
        return text.replace('{{root}}', '')

    def tidy_title(s):
        """Imported titles arrive as ALL CAPS or all lowercase; the template shows one case."""
        letters = [c for c in s if c.isalpha()]
        if letters and all(c.isupper() for c in letters):
            s = s.capitalize()
        elif letters and all(c.islower() for c in letters):
            s = s[0].upper() + s[1:]
        return s

    for item in content:
        if item.get('kind') == 'post' and item.get('title'):
            item['title'] = tidy_title(item['title'])

    for item in content:            # a card or a search result must never show {{exp}}
        for key in ('excerpt', 'title', 'subtitle'):
            if item.get(key):
                item[key] = fill_facts(item[key])
    faq_pages.VARS = shared          # FAQ answers pull facts too
    tests_pages.VARS = dict(shared, wa_number=WA_NUMBER)
    service_pages.VARS = dict(shared, centres=FACTS['centres'], online_opd=fact('consultation.online_opd'),
                              seen_at='New Delhi, Gurugram, or online')
    service_pages.GLANCE = json.loads(read(ROOT / 'data' / 'glance.json'))['pages']
    tests = tests_pages.load()   # data/tests/*.json -> /tests/ and /tests/<slug>/
    faq = faq_pages.load()       # data/faq/*.json -> /faq/ and /faq/<topic>/
    tax = taxonomy_pages.load()  # data/taxonomy.json -> /tag/<slug>/, /category/blog/, /author/<slug>/ (kept from the old WordPress site)
    tag_map = taxonomy_pages.tags_of(tax)
    post_by_slug = {p['slug']: p for p in posts}
    all_items = designed + content + blog_pages + tests_pages.items(tests) + faq_pages.items(faq) + taxonomy_pages.items(tax)

    # ---------------------------------------------------------------- render
    sitemap = []
    for pg in all_items:
        path = pg['path']
        is404 = path == '404'
        root = '/' if is404 else depth_root(path)
        canonical = SITE + '/' + ((url_path(path) + '/') if path and not is404 else '')
        kind = pg['kind']

        topic = ''
        if kind == 'page':
            topic = (LOCAL_TOPIC.get(pg['slug'], '') if pg.get('group') == 'local'
                     else ('about ' + group_of[pg['slug']].lower()) if pg['slug'] in group_of else '')
        wa = wa_link(topic)

        v = {'root': root, 'wa': wa, 'waicon': WAICON, 'delhi': DELHI, 'gurugram': GURUGRAM,
             'since': PRACTICE_SINCE, 'years': years, 'exp': EXPERIENCE, 'bio_short': bio_short, 'bio_long': BIO_LONG,
             'index_conditions': index_conditions(root), 'index_mental_health': index_group(root, 'mental-health'),
             'index_local': index_group(root, 'local'), 'latest_posts': latest_posts(root),
             'resources_menu': tests_pages.menu(root, tests, path, faq_pages.menu_item(root, faq, path)),
             'services_menu': hub_pages.services_menu(root, groups, by_slug, path)}
        v.update({k: fact(key) for k, key in PLACEHOLDERS.items()})    # the shared facts, from data/site.json
        # map embeds are derived from the one address, so they cannot point somewhere else
        for key in ('delhi', 'gurugram'):
            v['mapsrc_' + key] = ('https://www.google.com/maps?q=%s&output=embed'
                                  % urllib.parse.quote(fact('centres.%s.address' % key))) if fact('centres.%s.address' % key) else ''
        v['booking_panel'] = booking.panel(root, v, url_path(path) + ('/' if path else ''))
        # the star line only appears once there is a rating to show
        v['rating_line'] = ('<p class="rv-rating"><b>%s</b><span class="rv-rating__s" aria-hidden="true">★★★★★</span>'
                            '<span>from %s Google reviews</span></p>'
                            % (esc(str(fact('reviews.rating'))), esc(str(fact('reviews.count')))))             if fact('reviews.rating') and fact('reviews.count') else ''
        for key in ('delhi', 'gurugram'):     # each Google listing's own rating, shown on its link
            r, c = fact('reviews.%s.rating' % key), fact('reviews.%s.count' % key)
            v['rv_' + key] = ('<span class="rv-pill__r">%s <em aria-hidden="true">&#9733;</em> (%s)</span>' % (esc(str(r)), esc(str(c)))) if r and c else ''
        v['reg_line'] = ('<span class="fb__reg">Medical registration: %s</span>' % esc(str(fact('doctor.registration_number')))) if fact('doctor.registration_number') else ''
        v['book_href'] = '#book' if (path == 'contactus' or (kind == 'page' and pg.get('group') in ('services', 'local'))) else root + 'contactus/#book'
        if path == 'resources':
            v['resources_hub'] = hub_pages.resources_landing(root, posts)
        for key, name in INCLUDES.items():
            if (SRC / 'partials' / name).exists():
                v[key] = fill(read(SRC / 'partials' / name), v, name)

        title = pg.get('seo_title') or pg['title']
        if kind == 'designed':
            seo_title, desc = pg['title'], pg['description']
        else:
            seo_title, desc = (title if kind != 'blog-index' else pg['title']), pg.get('description') or ''
        desc = re.sub(r'\s+', ' ', desc).strip() or 'Dr. Gorav Gupta, senior psychiatrist in Delhi NCR.'
        # titles and descriptions pull from data/site.json as well, so a fact cannot drift in a meta tag
        seo_title, desc = fill(seo_title, v, 'title ' + path), fill(desc, v, 'description ' + path)

        # structured data
        if path == '':
            ld = '<script type="application/ld+json">%s</script>' % home_ld + film_ld
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
            if path == 'about-us':
                ld += physician_ld
            if path in LOCATION_CENTRE:
                ld += clinic_ld(fact('centres.' + LOCATION_CENTRE[path]), canonical)
            if path in ('video-gallery',):
                ld += film_ld

        has_panel = path == 'contactus' or (kind == 'page' and pg.get('group') in ('services', 'local'))
        scripts_list = pg.get('scripts', []) + (['service'] if kind == 'page' else []) + (['booking'] if has_panel and 'booking' not in pg.get('scripts', []) else [])
        if has_panel and 'bp-wizard' not in scripts_list:
            scripts_list = scripts_list + ['bp-wizard']
        # a preload entry is a path, or {src, srcset, sizes} so the phone preloads the small file
        def preload_tag(item):
            if isinstance(item, str):
                return '<link rel="preload" as="image" href="%s%s" fetchpriority="high">' % (root, item)
            srcset = ', '.join('%s%s' % (root, part.strip()) for part in item['srcset'].split(','))
            return ('<link rel="preload" as="image" href="%s%s" imagesrcset="%s" imagesizes="%s" fetchpriority="high">'
                    % (root, item['src'], srcset, esc(item['sizes'])))

        preload = ''.join(preload_tag(p) for p in pg.get('preload', []))
        scripts = ''.join(
            '<script src="%sassets/js/%s.js?v=%s"%s></script>' % (root, s, js_v[s], '' if s == 'site' else ' defer')
            for s in ['site'] + scripts_list + ['calm', 'spatial'])
        v.update({'lang': pg.get('lang', 'en'),
                  'title': esc(seo_title), 'description': esc(desc), 'canonical': canonical,
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
            body = tests_pages.test_body(pg, root, ph, wa)
        elif kind == 'tax':
            body = taxonomy_pages.body(pg, root, ph, post_by_slug, href, pretty_date)
        elif kind == 'faq-index':
            body = faq_pages.index_body(pg, root, ph, wa, EXPERIENCE)
        elif kind == 'faq':
            body = faq_pages.topic_body(pg, root, ph, wa)
        elif kind == 'blog-index':
            body = hub_pages.articles_hub(root, posts, tests, href, pretty_date, tag_map)
        else:
            group = pg['group']
            if group in ('services', 'local'):
                crumbs = [('Home', root), ('Services', root + 'services/'), (pg['title'], None)]
            elif group == 'blog':
                crumbs = [('Home', root), ('Blog', root + 'blog/'), (esc(pg['title']), None)]
            elif pg['slug'] == faq_pages.SOURCE_PATH:
                crumbs = [('Home', root), ('Resources', root + 'resources/'), ('Frequently asked questions', root + 'faq/'), ('Full guide', None)]
            else:
                crumbs = [('Home', root), ('Resources', root + 'resources/'), (pg['title'], None)]
            lede = pg.get('subtitle') or ''     # a post's first paragraph is its own opening, so it is not repeated as a subtitle
            meta_line = ('<time datetime="%s">%s</time>' % (pg['date'], pretty_date(pg['date']))) if kind == 'post' else ''
            lang = ' lang="%s"' % pg['lang'] if pg.get('lang') else ''
            inner = tests_pages.source_callout(root, tests, pg['slug']) + (fix_levels if kind == 'post' else (lambda x: x))(fill(pg['_body'], v, 'content ' + path))
            after = (taxonomy_pages.tag_row(root, pg['slug'], tag_map) if kind == 'post' else '') + author_box(root, kind == 'post', bio_short)
            if group in ('services', 'local'):
                after += tests_pages.page_callout(root, tests, pg['slug']) or ASSESS.format(root=root)
            if group in ('services', 'local') or kind == 'page':     # every page built on the service template has #book buttons, so it carries the panel they point to
                after += v['booking_panel']
            if kind == 'post':
                i = next((k for k, p in enumerate(posts) if p['slug'] == pg['slug']), 0)
                near = [p for p in posts[max(0, i - 1):i + 3] if p['slug'] != pg['slug']][:3]
                if near:
                    after += ('<section class="related" aria-labelledby="rel-h"><h2 id="rel-h">More from the blog</h2><ul class="idx idx--posts">%s</ul>'
                              '<p class="more"><a class="more__a" href="%sblog/">All articles <i>→</i></a></p></section>'
                              % (''.join('<li><a href="%s"><time datetime="%s">%s</time><b>%s</b></a></li>' % (href(p, root), p['date'], pretty_date(p['date']), p['title']) for p in near), root))
            if kind == 'page':        # condition, local and guide pages: the designed service template
                body = service_pages.build(pg, root, fill(pg['_body'], v, 'content ' + path), tests_pages.source_callout(root, tests, pg['slug']), after,
                                           crumb_html(crumbs), groups, by_slug, href, wa, EXPERIENCE)
            else:
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
        for m in re.finditer(r'class="([^"]*)"', html):
            site_tokens.update(m.group(1).split())
        site_tokens.update(re.findall(r'id="([^"]+)"', html))
        site_tokens.update(re.findall(r"classList\.(?:add|remove|toggle)\('([^']+)'", html))
        pages_out.append((out, html))
        if not is404 and not pg.get('noindex') and not (kind == 'blog-index' and pg['page'] > 1):
            sitemap.append((canonical, pg.get('modified') or pg.get('date') or ''))

    for js in sorted((ROOT / 'assets' / 'js').glob('*.js')):
        src = read(js)
        site_tokens.update(re.findall(r"classList\.(?:add|remove|toggle)\('([^']+)'", src))
        site_tokens.update(re.findall(r"querySelector(?:All)?\('[.#]([A-Za-z0-9_-]+)", src))
        site_tokens.update(re.findall(r"\.(?:closest|matches)\('[.#]([A-Za-z0-9_-]+)", src))
        # markup the scripts build as strings: class="wd", class="sr" and the rest
        for m in re.finditer(r'class="([^"]*)"', src):
            site_tokens.update(m.group(1).split())
        for m in re.finditer(r"class='([^']*)'", src):
            site_tokens.update(m.group(1).split())
        site_tokens.update(re.findall(r"className\s*=\s*'([^']*)'", src))
    # Pruning by class name is switched off: it dropped rules the scripts and the cascade rely on and broke the hero.
    css_v = bundle_css()
    for out, html in pages_out:
        out.write_text(html.replace(CSSV, css_v), encoding='utf-8', newline='\n')

    urls = ''.join('<url><loc>%s</loc>%s</url>' % (u, ('<lastmod>%s</lastmod>' % m) if m else '') for u, m in sitemap)
    (ROOT / 'sitemap.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">%s</urlset>\n' % urls, encoding='utf-8', newline='\n')
    for slug, why in retired:
        print('retired: %-62s %s' % (slug, why))
    print('built %d pages (%d designed, %d imported pages, %d posts, %d blog index pages); sitemap has %d urls; css bundle %s'
          % (len(all_items), len(designed), len(by_slug), len(posts), len(blog_pages), len(sitemap), css_v))

    # Facts still waiting on a decision (data/site.json "pending"), so none is forgotten at cutover.
    pending = FACTS.get('pending', {})
    empty = [(row, key) for key, row in pending.items() if not str(fact(key)).strip()]
    if pending:
        print('%d facts wait on decisions %s; %d of them have nothing to publish yet'
              % (len(pending), ', '.join(str(r) for r in sorted(set(pending.values()))), len(empty)))
        for row, key in sorted(empty):
            print('  decision %-2s %-32s %s' % (row, key, FACTS['decisions'][str(row)]))


if __name__ == '__main__':
    main()
