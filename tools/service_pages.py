"""Condition, local and guide pages (the imported 'page' content): a designed template instead of a plain article.

  hero      breadcrumb, a short label with the topic icon, the title, a one-line summary, three facts, and a profile card with
            the way to book (build() below)
  content   the imported text, regrouped so it reads as a designed page: runs of small headings with a paragraph become a
            two-column list, the questions become the same accordion as the FAQ pages, long short-item lists become two columns
  sidebar   an "On this page" list that follows the scroll (assets/js/service.js) and a booking card
  end       three related pages, then the author box

Needs beautifulsoup4 and lxml (pip install beautifulsoup4 lxml). Styles: assets/css/service.css.
"""
import datetime
import re
import urllib.parse

from bs4 import BeautifulSoup

from hub_pages import icon, group_icon

LEDE = ('Assessment, treatment and long-term support from Dr. Gorav Gupta, a senior psychiatrist with {exp} years of experience, '
        'in New Delhi, Gurugram and online.')
CHECK = ('<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
         '<path d="m5 12.500 4.500 4.500L19 7.500"/></svg>')
ARROW = '<i aria-hidden="true">&rarr;</i>'


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def text_of(tag):
    return re.sub(r'\s+', ' ', tag.get_text(' ')).strip()


def arrange_local_content(soup, items):
    """Give location-page article sections explicit, predictable layouts.

    The imported pages have very different amounts of copy and imagery. Keeping all of that
    content in one CSS multi-column flow sends headings and figures into unrelated columns.
    A short editorial section wrapper lets each heading stay beside its own content instead.
    """
    sections, title, body = [], None, []

    def flush():
        nonlocal title, body
        if title is None:
            return
        intro = ('sp-opener' in (title.get('class') or []) or not sections)
        section = soup.new_tag('section', attrs={'class': 'sp-content-section'})
        heading = soup.new_tag('div', attrs={'class': 'sp-content-section__head'})
        copy = soup.new_tag('div', attrs={'class': 'sp-content-section__body'})
        heading.append(title.extract())
        section['aria-labelledby'] = heading.find(['h2', 'h3', 'h4']).get('id')

        if intro:
            section['class'].append('sp-content-section--intro')
            visual_item = next((node for node in body if node.name in ('figure', 'img')), None)
            if visual_item is not None:
                body.remove(visual_item)
                if visual_item.name == 'img':
                    visual = soup.new_tag('figure', attrs={'class': 'sp-article-visual'})
                    visual.append(visual_item.extract())
                else:
                    visual = visual_item.extract()
                    visual['class'] = list(dict.fromkeys(visual.get('class', []) + ['sp-article-visual']))
                section.append(heading)
                section.append(visual)
            else:
                section.append(heading)

        for node in body:
            copy.append(node.extract())
        section.append(copy)
        if not intro:
            section.insert(0, heading)
        sections.append(section)
        title, body = None, []

    for node in items:
        classes = node.get('class') or []
        starts_section = node.name in ('h2', 'h3', 'h4') and 'sp-sub' not in classes
        if starts_section:
            flush()
            title = node
        elif title is None:
            # All three location pages start with a heading. Keep this fallback for future
            # imported page variants instead of silently dropping any leading content.
            title = soup.new_tag('h3')
            title['class'] = ['sp-visually-hidden']
            title['id'] = 'location-page-introduction'
            body.append(node)
        else:
            body.append(node)
    flush()
    return sections


# ---------------------------------------------------------------------------------------------------- the content
def prepare(html, pg):
    """-> (content html, table of contents [(id, text)], lede html or '')"""
    soup = BeautifulSoup('<div id="r">%s</div>' % html, 'lxml')
    r = soup.find(id='r')
    items = [c for c in r.children if getattr(c, 'name', None)]

    # a short opening paragraph becomes the summary under the title
    lede = ''
    for t in items[:3]:
        if t.name == 'p' and text_of(t):
            if len(text_of(t)) <= 300:
                lede = ''.join(str(c) for c in t.children).strip()
                t.extract()
                items.remove(t)
            break

    # runs of "small heading + text" (three or more) become a two-column list
    nodes, i = [], 0
    while i < len(items):
        if items[i].name != 'h4':
            nodes.append(items[i]); i += 1; continue
        groups, j = [], i
        while j < len(items) and items[j].name == 'h4':
            h, body, k = items[j], [], j + 1
            while k < len(items) and items[k].name not in ('h2', 'h3', 'h4', 'details'):
                body.append(items[k]); k += 1
            groups.append((h, body)); j = k
        # On location pages the imported h4s are real subsections, not a uniform list. Putting
        # them into equal table-like columns leaves empty cells beneath short groups and splits
        # the long biography from its heading, so keep them for the editorial section layout.
        if len(groups) >= 3 and pg.get('group') != 'local':
            dl = soup.new_tag('div', attrs={'class': 'sp-dl'})
            hoist = []
            for h, body in groups:
                row = soup.new_tag('section', attrs={'class': 'sp-dl__r'})
                for br in h.find_all('br'):
                    br.decompose()
                row.append(h.extract())
                d = soup.new_tag('div')
                for b in body:
                    if b.name == 'figure':
                        hoist.append(b)
                    else:
                        d.append(b.extract())
                row.append(d)
                dl.append(row)
            nodes.append(dl)
            nodes.extend(hoist)
        else:
            nodes.extend(items[i:j])
        i = j
    items = nodes

    # questions: the accordion used on the FAQ pages
    out, run = [], None
    for t in items:
        if t.name == 'details':
            if run is None:
                run = soup.new_tag('div', attrs={'class': 'fq-list sp-faq'})
                out.append(run)
            t['class'] = ['fq-q']
            summ = t.find('summary')
            rest = [c for c in list(t.children) if c is not summ]
            wrap = soup.new_tag('div', attrs={'class': 'fq-a'})
            if any(getattr(c, 'name', None) in ('p', 'ul', 'ol') for c in rest):
                for c in rest:
                    wrap.append(c.extract())
            else:
                p = soup.new_tag('p')
                for c in rest:
                    p.append(c.extract())
                wrap.append(p)
            if wrap.get_text(strip=True):
                t.append(wrap)
            run.append(t.extract())
        else:
            run = None
            out.append(t)
    items = out

    # pictures: wide ones fill the column, small ones (badges, portraits) keep their size
    for fig in r.find_all('figure'):
        img = fig.find('img')
        try:
            wide = int(img.get('width', 0)) >= 900
        except (TypeError, ValueError):
            wide = False
        fig['class'] = fig.get('class', []) + ['sp-fig' if wide else 'sp-fig sp-fig--small']

    # long lists of short items run in two columns; every bulleted list's items reveal in with a light stagger
    # as the reader scrolls to them, instead of just appearing with the rest of the paragraph
    for ul in r.find_all('ul'):
        if 'sp-chips' in (ul.get('class') or []):
            continue
        lis = ul.find_all('li', recursive=False)
        if len(lis) >= 6 and sum(len(text_of(x)) for x in lis) / len(lis) < 60:
            ul['class'] = ul.get('class', []) + ['sp-ul2']
        for i, li in enumerate(lis):
            li['class'] = li.get('class', []) + ['reveal']
            li['style'] = (li.get('style', '') + ';--i:%d' % (i % 8)).lstrip(';')

    # headings: ids, the questions heading, and a table of contents of the sections
    toc, used = [], set()
    prev = None
    for t in items:
        # the headings regrouped into a two-column block are sections too, nested under the last one
        if t.name == 'div' and 'sp-dl' in (t.get('class') or []):
            for h in t.find_all('h4'):
                txt = text_of(h)
                if not txt:
                    continue
                base = re.sub(r'[^a-z0-9]+', '-', txt.lower()).strip('-')[:40] or 'part'
                sid, n = base, 2
                while sid in used:
                    sid = '%s-%d' % (base, n); n += 1
                used.add(sid)
                h['id'] = sid
                toc.append((sid, txt, True))
            prev = t
            continue
        if t.name in ('h2', 'h3', 'h4'):
            txt = text_of(t)
            label = t.name == 'h3' and prev is not None and prev.name in ('h2', 'h3')
            nested = t.name == 'h4' or label
            if label:
                t['class'] = t.get('class', []) + ['sp-sub']
            elif txt:
                base = re.sub(r'[^a-z0-9]+', '-', txt.lower()).strip('-')[:40] or 'section'
                sid, n = base, 2
                while sid in used:
                    sid = '%s-%d' % (base, n); n += 1
                used.add(sid)
                t['id'] = sid
                toc.append((sid, txt, nested))
                if re.search(r'frequently asked', txt, re.I):
                    t['class'] = t.get('class', []) + ['sp-faq-h']
        prev = t
    h2 = next((t for t in items if t.name == 'h2'), None)
    if h2 is not None:
        h2['class'] = h2.get('class', []) + ['sp-opener']

    # Keep the award image beside its caption and description so the low-resolution badge
    # does not occupy a full line with an empty column beside it.
    for i, t in enumerate(items):
        img = t.find('img') if t.name == 'figure' else None
        next_heading = items[i + 1] if i + 1 < len(items) else None
        description = items[i + 2] if i + 2 < len(items) else None
        if (img and next_heading and next_heading.name in ('h2', 'h3')
                and text_of(next_heading).strip() == 'Psychiatrist of the Year'
                and description and description.name == 'p'):
            feature = soup.new_tag('div', attrs={'class': 'sp-award'})
            copy = soup.new_tag('div', attrs={'class': 'sp-award__copy'})
            for node in (t, next_heading, description):
                node.extract()
            copy.append(next_heading)
            copy.append(description)
            feature.append(t)
            feature.append(copy)
            items[i:i + 3] = [feature]
            break

    if pg.get('group') == 'local':
        items = arrange_local_content(soup, items)

    for c in list(r.children):
        c.extract()
    for t in items:
        r.append(t)
    return r.decode_contents(), toc, lede


# ---------------------------------------------------------------------------------------------------- the page
def label_for(pg, group_of):
    slug, g = pg['slug'], pg.get('group')
    if slug == 'psychiatrist-near-me-consultation':
        return 'Frequently asked questions', 'help'
    if slug in group_of:
        return group_of[slug], group_icon(group_of[slug])
    if g == 'local':
        return 'Psychiatrist in Delhi NCR', 'pin'
    if g == 'mental-health':
        return 'Self-assessment guide', 'clipboard'
    return 'Resources', 'book'


def related(pg, root, groups, by_slug, href):
    if pg['slug'] == 'psychiatrist-near-me-consultation':
        import faq_pages
        lis = '<li><a href="%sfaq/"><b>All questions, searchable</b>%s</a></li>' % (root, ARROW) + ''.join('<li><a href="%sfaq/%s/"><b>%s</b>%s</a></li>' % (root, t['slug'], esc(t['menu_title']), ARROW) for t in faq_pages.load())
        return '<section class="sp-rel" aria-labelledby="sp-rel-h"><h2 id="sp-rel-h">More from the FAQ</h2><ul>%s</ul></section>' % lis
    flat = [(t, s) for t, ss in groups['condition_groups'] for s in ss if s in by_slug]
    mine = next((t for t, s in flat if s == pg['slug']), None)
    if mine:
        pool = [s for t, s in flat if t == mine and s != pg['slug']] + [s for t, s in flat if t != mine and s != pg['slug']]
        head = 'More conditions we treat'
    elif pg.get('group') == 'local':
        pool = [c['slug'] for c in by_slug.values() if c.get('group') == 'local' and c['slug'] != pg['slug']]
        head = 'Dr. Gorav Gupta in other cities'
    else:
        pool = [c['slug'] for c in by_slug.values() if c.get('group') == pg.get('group') and c['slug'] != pg['slug']]
        head = 'Related guides'
    pool = pool[:3]
    if not pool:
        return ''
    lis = ''.join('<li><a href="%s"><b>%s</b>%s</a></li>' % (href(by_slug[s], root), esc(by_slug[s]['title']), ARROW) for s in pool)
    return ('<section class="sp-rel" aria-labelledby="sp-rel-h"><h2 id="sp-rel-h">%s</h2><ul>%s</ul>'
            '<a class="more__a" href="%sservices/">All services <i>&rarr;</i></a></section>' % (head, lis, root))


# The shared facts (data/site.json), set by build_site.py.
VARS = {}
GLANCE = {}
PAGE_CENTRE = {'psychiatrist-in-delhi': 'delhi', 'psychiatrist-in-gurgaon': 'gurugram'}


def glance(pg, root, tests_link=''):
    """A short "At a glance" box under the H1: who the page is for, where, and the first step.

    Clinical rows (treatments, how long it takes) come from data/glance.json and are empty
    until Dr. Gupta confirms them, so nothing is claimed on his behalf.
    """
    if pg.get('group') != 'services':
        return ''
    g = GLANCE.get(pg.get('slug'), {})
    rows = [('Who it is for', g.get('who')),
            ('Treatments', g.get('treatments')),
            ('How long it takes', g.get('duration')),
            ('Seen at', VARS.get('seen_at')),
            ('First step', 'An assessment, then a treatment plan matched to severity')]
    items = ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (k, esc(v)) for k, v in rows if v)
    if not items:
        return ''
    return ('<aside class="sp-glance" aria-label="At a glance"><p class="sp-glance__t">At a glance</p>'
            '<dl>%s</dl>%s</aside>' % (items, tests_link))


def practical(pg, root, wa):
    """What someone on a location page actually needs: where, when, and how to be seen.

    It opens the page, above the prose, because that is the question the page is being
    asked. A detail nobody has recorded yet (the metro, the parking) is left out.
    """
    key = PAGE_CENTRE.get(pg.get('slug'))
    if not key:
        return ''
    c = VARS.get('centres', {}).get(key, {})
    rows = [('Address', c.get('address')), ('OPD', c.get('opd')),
            ('Nearest metro', c.get('metro')), ('Parking', c.get('parking')),
            ('Online', VARS.get('online_opd'))]
    dl = ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (k, esc(v)) for k, v in rows if v)
    mapsrc = ('https://www.google.com/maps?q=%s&output=embed' % urllib.parse.quote(c['address'])) if c.get('address') else ''
    frame = ('<div class="lp-map"><iframe src="%s" title="Map of the %s consulting room" loading="lazy" '
             'referrerpolicy="no-referrer-when-downgrade" width="600" height="320"></iframe></div>' % (mapsrc, esc(c.get('label', '')))) if mapsrc else ''
    return ('<section class="lp-prac" aria-labelledby="lp-prac-h"><div class="lp-prac__in">'
            '<div class="lp-prac__txt"><h2 id="lp-prac-h">%s</h2><dl class="ct-dl">%s</dl>'
            '<p class="lp-prac__a"><a class="btn" href="#book">Ask for a call back</a>'
            '<a class="btn ghost" href="%s" target="_blank" rel="noopener">WhatsApp</a>'
            '%s</p></div>%s</div></section>'
            % (esc(c.get('clinic_name', 'Where to come')), dl, wa,
               ('<a class="more__a" href="%s" target="_blank" rel="noopener">Directions <i aria-hidden="true">&nearr;</i></a>' % c['maps']) if c.get('maps') else '',
               frame))


def conditions_here(pg, root, groups, by_slug, href):
    """One line per condition, each linking to the page that covers it.

    A location page should say what is treated and send you to the real guide, rather than
    repeat a paragraph about every condition.
    """
    if pg.get('group') != 'local':
        return ''
    icons = {
        'De-addiction and substance use': '<path d="M10.6 13.4a4.2 4.2 0 0 0 5.9 0l2.1-2.1a4.2 4.2 0 0 0-5.9-5.9l-1.2 1.2"/><path d="M13.4 10.6a4.2 4.2 0 0 0-5.9 0l-2.1 2.1a4.2 4.2 0 0 0 5.9 5.9l1.2-1.2"/>',
        'Schizophrenia': '<path d="M12 4.1a3 3 0 0 0-5.8 1.1 3.2 3.2 0 0 0-1.5 5.7 3.2 3.2 0 0 0 2 5.2A3 3 0 0 0 12 18V4.1Z"/><path d="M12 4.1a3 3 0 0 1 5.8 1.1 3.2 3.2 0 0 1 1.5 5.7 3.2 3.2 0 0 1-2 5.2A3 3 0 0 1 12 18"/><path d="M8 8.5c1.2 0 2 .7 2 1.7M7 14c1.5-.2 2.4.4 2.8 1.5m6.2-7c-1.2 0-2 .7-2 1.7m3 3.8c-1.5-.2-2.4.4-2.8 1.5"/>',
        'Mood disorders': '<path d="M4 14.5c2.1 0 2.1-5 4.2-5s2.1 5 4.2 5 2.1-5 4.2-5S18.7 12 20 12"/><path d="M4 19h16"/>',
        'Anxiety, OCD and stress': '<path d="M4 8c2.3 0 2.3 8 4.6 8s2.3-8 4.7-8 2.3 8 4.7 8 2.3-8 4.6-8"/>',
        'Personality disorders': '<circle cx="12" cy="8" r="3.2"/><path d="M5.5 19a6.5 6.5 0 0 1 13 0"/>',
        'Eating disorders': '<circle cx="12" cy="12" r="7.3"/><path d="M4.8 5.5v5m-1.6-5v3.2a1.6 1.6 0 0 0 3.2 0V5.5M4.8 10v8.5m14.4-13v13m0-13c-1.8 1.4-2.6 3.2-2.6 5.4h2.6"/>'
    }
    cols = []
    for title, slugs in groups['condition_groups']:
        items = ''.join('<li><a href="%s">%s</a></li>' % (href(by_slug[x], root), esc(by_slug[x].get('menu_title') or by_slug[x]['title']))
                        for x in slugs if x in by_slug)
        if items:
            icon = icons.get(title, '<circle cx="12" cy="12" r="7"/><path d="M12 8v8m-4-4h8"/>')
            heading = ('<h3><span class="lp-cond__icon" aria-hidden="true"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">%s</svg></span>%s</h3>'
                       % (icon, esc(title)))
            cols.append('<div>%s<ul>%s</ul></div>' % (heading, items))
    if not cols:
        return ''
    return ('<section class="lp-cond" aria-labelledby="lp-cond-h"><h2 id="lp-cond-h">What Dr. Gorav Gupta treats here</h2>'
            '<div class="lp-cond__g">%s</div></section>' % ''.join(cols))


def reviewed(pg, root):
    """"Medically reviewed by ...".

    The date comes from the page's own "reviewed" field. It falls back to "modified", which is
    when the text last changed rather than when a clinician last read it, so those dates need
    confirming with Dr. Gupta before launch (see docs/url-rules.md).
    """
    iso = pg.get('reviewed') or pg.get('modified') or ''
    if not iso:
        return ''
    try:
        d = datetime.date.fromisoformat(iso)
        when = '%d %s %d' % (d.day, d.strftime('%B'), d.year)
    except ValueError:
        return ''
    return ('<p class="sp-review">Medically reviewed by <a href="%sabout-us/">Dr. Gorav Gupta</a>, '
            'M.B.B.S., M.D. (Psychiatry) &middot; <time datetime="%s">%s</time></p>' % (root, iso, when))


CITY_PHOTO = {
    'psychiatrist-in-delhi': ('assets/img/gallery/consulting-room.webp', 'Dr. Gorav Gupta at his desk in the New Delhi consulting room', 'New Delhi', 'Tulasi Psychiatric Clinic', 1360, 907),
    'psychiatrist-in-gurgaon': ('assets/img/centre/gurugram-photo-1.webp', 'The brick building of Tulasi Healthcare in Sector 64, Gurugram', 'Gurugram', 'Tulasi Healthcare, Sector 64', 1280, 720),
    'psychiatrist-in-india': ('assets/img/portrait-wide-col.webp', 'Dr. Gorav Gupta, smiling, in his garden', 'Across India', 'In person and online', 1152, 987),
}

CITY_HERO_COPY = {
    'psychiatrist-in-delhi': (
        'Psychiatric care in Delhi',
        'Visit Dr. Gorav Gupta at his New Delhi clinic or book an online consultation.',
        'New Delhi clinic',
    ),
    'psychiatrist-in-gurgaon': (
        'Psychiatric care in Gurugram',
        'Consult Dr. Gorav Gupta at Tulasi Healthcare’s Gurugram clinic or online.',
        'Gurugram clinic',
    ),
    'psychiatrist-in-india': (
        'Psychiatric care across India',
        'Online consultations are available across India, with clinic visits in Delhi NCR.',
        'Delhi NCR clinics',
    ),
}


def city_photo(pg, root):
    """A framed photograph with a glass caption on the hero of the three city pages."""
    c = CITY_PHOTO.get(pg['slug'])
    if not c:
        return ''
    return ('<figure class="sp-hero__ph"><img src="%s%s" alt="%s" width="%d" height="%d" decoding="async"><figcaption><b>%s</b><span>%s</span></figcaption></figure>'
            % (root, c[0], esc(c[1]), c[4], c[5], esc(c[2]), esc(c[3])))


def build(pg, root, content, callout, after, crumbs, groups, by_slug, href, wa, exp):
    group_of = {s: t for t, ss in groups['condition_groups'] for s in ss}
    label, ic = label_for(pg, group_of)
    body, toc, lede_html = prepare(content, pg)
    lede = pg.get('subtitle') or lede_html or LEDE.format(exp=exp)
    city_copy = CITY_HERO_COPY.get(pg.get('slug'))
    chips = ''.join('<li>%s%s</li>' % (CHECK, c) for c in (
        ('%s years’ experience' % exp, city_copy[2], 'Online consultations') if city_copy else
        ('%s years of experience' % exp, 'New Delhi and Gurugram', 'Online consultations')
    ))
    hero_label = '' if city_copy else '<p class="sp-eyebrow">%s<span>%s</span></p>' % (icon(ic, 'sp-eyebrow__ic'), esc(label))
    hero = ('<header class="sp-hero sp-hero--solo"><div class="sp-hero__txt">%s%s'
            '<h1>%s</h1>%s<p class="sp-lede">%s</p><ul class="sp-chips">%s</ul>'
            '<p class="sp-hero__act"><a class="btn" href="#book">Ask for a call back</a>'
            '<a class="btn ghost" href="%s" target="_blank" rel="noopener">WhatsApp</a></p></div>%s</header>'
            % (crumbs, hero_label, esc(city_copy[0] if city_copy else pg['title']), reviewed(pg, root),
               city_copy[1] if city_copy else lede, chips, wa, city_photo(pg, root)))
    toc_html = ''
    if len(toc) >= 2:
        rows, open_sub = [], False
        for sid, text, nested in toc:
            if nested and not open_sub:
                rows.append('<li><ul class="sp-toc__sub">'); open_sub = True
            elif not nested and open_sub:
                rows.append('</ul></li>'); open_sub = False
            rows.append('<li><a href="#%s">%s</a></li>' % (sid, esc(text)))
        if open_sub:
            rows.append('</ul></li>')
        toc_html = ('<nav class="sp-toc" aria-label="On this page"><p class="sp-side__t">On this page</p><ol>%s</ol></nav>'
                    % ''.join(rows))
    side = ('<aside class="sp__side">%s<div class="sp-book"><p class="sp-side__t">Book a consultation</p>'
            '<p>Leave your number on this page and the team calls you back, or message them now.</p>'
            '<a class="btn" href="#book">Ask for a call back</a><a class="btn ghost" href="%s" target="_blank" rel="noopener">WhatsApp</a></div></aside>'
            % (toc_html, wa))
    part_of = ('<p class="sp-partof">Dr. Gupta&rsquo;s practice is part of <a href="https://tulasihealthcare.com" '
               'target="_blank" rel="noopener">Tulasi Healthcare</a>, with centres across Delhi NCR and Noida.</p>')
    return (hero + practical(pg, root, wa) + conditions_here(pg, root, groups, by_slug, href)
            + glance(pg, root) + '<article class="sec sp"><div class="sp__grid"><div class="sp__main">%s<div class="prose__in sp__in">%s</div>%s%s'
            '<div class="prose__after sp__after">%s</div></div>%s</div></article>'
            % (callout, body, related(pg, root, groups, by_slug, href), part_of, after, side))
