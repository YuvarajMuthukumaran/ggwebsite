"""Frequently asked questions: /faq/ and /faq/<topic>/, built from data/faq/*.json by tools/build_site.py.

One JSON file per topic (title, short, optional intro, and a list of questions with HTML answers). Adding a file adds a
page at /faq/<slug>/, a card on /faq/ and a link on the FAQ pages' topic lists. The answers
come from the FAQ page on goravgupta.com (the page kept at SOURCE_PATH), grouped by topic. Every topic page also carries
FAQPage structured data.
"""
import json
import pathlib
import re

from hub_pages import icon, FAQ_HUB, TESTS_HUB

DATA = pathlib.Path(__file__).resolve().parent.parent / 'data' / 'faq'
SITE = 'https://www.goravgupta.com'
# The hub is served at the long URL the old site ranked on (284 clicks a month); /faq/ 301s to it
# (see vercel.json and hub_pages.FAQ_HUB). The topic pages keep their own /faq/<topic>/ paths.
SOURCE_PATH = FAQ_HUB
TITLE = 'Frequently Asked Questions (FAQ)'
LEDE = ('Answers to the questions people ask most before they see a psychiatrist: when to seek help, how treatment works, '
        'what a consultation involves and who Dr. Gorav Gupta is.')


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def load():
    topics = [json.loads(f.read_text(encoding='utf-8')) for f in sorted(DATA.glob('*.json'))] if DATA.exists() else []
    for t in topics:
        t['n'] = len(t['qas'])
        for q in t['qas']:
            q['id'] = 'q-' + re.sub(r'[^a-z0-9]+', '-', re.sub(r'<[^>]+>', '', q['q']).lower()).strip('-')[:60]
    return sorted(topics, key=lambda t: (t.get('order', 99), t['slug']))


def plain(html):
    """Answer text for structured data: tags out, list items separated."""
    s = re.sub(r'</li>', '; ', html)
    s = re.sub(r'</(p|h4|section)>', ' ', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = s.replace('&rsquo;', '’').replace('&ldquo;', '“').replace('&rdquo;', '”').replace('&rarr;', '').replace('&amp;', '&')
    s = re.sub(r'\{\{root\}\}', '', s)
    return re.sub(r'\s+', ' ', s).replace('; ;', ';').strip().rstrip(';').strip()


def faq_ld(qas):
    return ('<script type="application/ld+json">%s</script>' % json.dumps({
        '@context': 'https://schema.org', '@type': 'FAQPage',
        'mainEntity': [{'@type': 'Question', 'name': plain(q['q']), 'acceptedAnswer': {'@type': 'Answer', 'text': plain(q['a'])}} for q in qas]},
        ensure_ascii=False))


def items(topics):
    """Page records for build_site.py's render loop."""
    out = [{'kind': 'faq-index', 'path': FAQ_HUB, 'nav': 'resources', 'crumb': 'Frequently asked questions',
            'title': '%s | Dr. Gorav Gupta' % TITLE,
            'description': 'Frequently asked questions about seeing a psychiatrist in Delhi NCR: when to seek help, treatment and therapy, '
                           'consultation and fees, and about Dr. Gorav Gupta.',
            'scripts': ['faq-index'], 'faq': topics, 'ld_extra': ''}]
    for t in topics:
        out.append({'kind': 'faq', 'path': 'faq/' + t['slug'], 'nav': 'resources', 'crumb': t['menu_title'],
                    'title': '%s | FAQ | Dr. Gorav Gupta' % t['title'], 'description': t['description'],
                    'scripts': ['faq'], 'topic': t, 'faq': topics, 'ld_extra': faq_ld(t['qas'])})
    return out


def topics_by(topics, slug):
    return next((t for t in topics if t['slug'] == slug), None)


def menu_item(root, topics, path):
    """The FAQ entry in the Resources dropdown: one plain link to /faq/ (the topics are listed on the FAQ pages themselves)."""
    if not topics:
        return ''
    cur = ' aria-current="page"' if path == FAQ_HUB else ''
    return ('<a href="%s%s/"%s>%s<span class="dd__tx"><b>Frequently asked questions (FAQ)</b><small>Answers on consulting, treatment and fees</small></span></a>'
            % (root, FAQ_HUB, cur, icon('help')))


# The shared facts from data/site.json, set by build_site.py before rendering, so an answer can say
# {{fee}} or {{exp}} instead of carrying its own copy of a number that changes.
VARS = {}


def r(html, root):
    html = html.replace('{{root}}', root)
    for k, v in VARS.items():
        html = html.replace('{{%s}}' % k, str(v))
    return html


def first_part(html):
    """The opening paragraph (or the whole answer when it starts with a list)."""
    m = re.match(r'\s*(<p>.*?</p>)', html, re.S)
    return m.group(1) if m else html


def help_band(root, wa):
    return ('<aside class="fq-help"><div><p class="fq-help__t">Didn&rsquo;t find your answer?</p>'
            '<p>Call the clinic or message the team on WhatsApp. Consultations are available online and at both consulting rooms.</p></div>'
            '<div class="fq-help__a"><a class="btn" href="tel:+918800000255">Call +91 88000 00255</a>'
            '<a class="btn ghost" href="%s" target="_blank" rel="noopener">WhatsApp</a></div></aside>' % wa)


SUGGEST = ['fee', 'online', 'OCD', 'alcohol', 'therapy', 'psychologist']
SEARCH_ICON = ('<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
               '<circle cx="11" cy="11" r="6.500"/><path d="m16 16 4.500 4.500"/></svg>')
FACT_ICON = {
    'exp': '<circle cx="12" cy="9" r="5.500"/><path d="m9.200 13.600-1.700 7 4.500-2.500 4.500 2.500-1.700-7"/>',
    'pin': '<path d="M12 21s-7-5.6-7-11a7 7 0 0 1 14 0c0 5.400-7 11-7 11z"/><circle cx="12" cy="10" r="2.500"/>',
    'video': '<rect x="3" y="6" width="13" height="12" rx="2.500"/><path d="m16 10.500 5-3v9l-5-3z"/>',
}


def fact(ic, k, v):
    return ('<li><span class="fh-glance__ic"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg></span>'
            '<span><b>%s</b><small>%s</small></span></li>' % (FACT_ICON[ic], k, v))


def index_body(pg, root, ph, wa, exp='40+'):
    topics = pg['faq']
    total = sum(t['n'] for t in topics)
    head = ph([('Home', root), ('Resources', root + 'resources/'), ('Frequently asked questions', None)], TITLE, '')
    # the standard header is replaced by the hero below (keeps the h1 and breadcrumb markup)
    crumbs = head[head.index('<nav class="crumb"'):head.index('</nav>') + 6]
    hero = ('<header class="fh-hero"><div class="fh-hero__txt">%s<p class="fh-eyebrow">%s<span>Answers from Dr. Gorav Gupta</span></p>'
            '<h1>%s</h1><p class="fh-lede">%s</p>'
            '<div class="fh-search"><label class="fh-sr" for="fh-q">Search the questions</label>%s'
            '<input id="fh-q" type="search" placeholder="Search %d questions" autocomplete="off" spellcheck="false">'
            '<button type="button" class="fh-search__x" aria-label="Clear the search" hidden>&times;</button></div>'
            '<p class="fh-suggest"><span>Try</span>%s</p></div>'
            '<aside class="fh-glance" aria-label="At a glance"><p class="fh-glance__t">At a glance</p><ul>%s%s%s</ul>'
            '<a class="fh-glance__go" href="https://tulasihealthcare.com" target="_blank" rel="noopener">Visit Tulasi to book a consultation <i aria-hidden="true">&nearr;</i></a></aside></header>'
            % (crumbs, icon('help', 'fh-eyebrow__ic'), esc(TITLE), LEDE, SEARCH_ICON, total,
               ''.join('<button type="button" data-try="%s">%s</button>' % (esc(w), esc(w)) for w in SUGGEST),
               fact('exp', 'Experience', '%s years in psychiatry' % exp), fact('pin', 'Consulting rooms', 'New Delhi and Gurugram'),
               fact('video', 'Online', 'Consultations available online')))
    side = ('<aside class="fh__side" aria-label="Topics"><p class="fh__k">Topics</p><ul class="fh-topics">'
            '<li><a href="%s%s/" class="is-on" data-topic="all" aria-pressed="true">All questions <span>%d</span></a></li>%s</ul>'
            '<div class="fh__more"><a href="%s%s/">Take a private self-assessment <i>&rarr;</i></a></div></aside>'
            % (root, FAQ_HUB, total, ''.join('<li><a href="%sfaq/%s/" data-topic="%s" aria-pressed="false">%s <span>%d</span></a></li>' % (root, t['slug'], t['slug'], esc(t['menu_title']), t['n']) for t in topics),
               root, TESTS_HUB))
    groups = ''
    for t in topics:
        items = ''
        for q in t['qas']:
            text = (q['q'] + ' ' + plain(q['a'])).lower()
            items += ('<details class="fq-q fh-q" id="fh-%s" data-q="%s"><summary><span class="fh-q__t">%s</span></summary><div class="fq-a">%s'
                      '<p class="fq-a__more"><a href="%sfaq/%s/#%s">Read the full answer <i>&rarr;</i></a></p></div></details>'
                      % (q['id'], esc(text), q['q'], r(first_part(q['a']), root), root, t['slug'], q['id']))
        groups += ('<section class="fh-g" data-topic="%s" aria-labelledby="fh-g-%s"><header class="fh-g__h"><div><h2 id="fh-g-%s">%s</h2><p>%s</p></div>'
                   '<a class="fh-g__all" href="%sfaq/%s/">Open this topic <i>&rarr;</i></a></header><div class="fq-list">%s</div></section>'
                   % (t['slug'], t['slug'], t['slug'], esc(t['title']), esc(t['short']), root, t['slug'], items))
    main = ('<div class="fh__main"><div class="fh-bar"><p class="fh-count" id="fh-count" aria-live="polite" tabindex="-1">%d questions</p>'
            '<button type="button" class="fq-tog" id="fh-tog" aria-pressed="false">Expand all</button></div>'
            '<div class="fh-active" id="fh-active" hidden></div>%s'
            '<div class="fh-empty" id="fh-empty" hidden><b>No question matches that.</b><p>Try another word, or browse a topic. You can also ask the team directly.</p>'
            '<div><button type="button" class="btn ghost" id="fh-clear">Clear the search</button> <a class="btn" href="%s" target="_blank" rel="noopener">Ask on WhatsApp</a></div></div></div>'
            % (total, groups, wa))
    return (hero + '<section class="sec fh"><div class="fh__grid">' + side + main + '</div></section>'
            + '<section class="sec fq-end">%s</section>' % help_band(root, wa))


def topic_body(pg, root, ph, wa):
    t, topics = pg['topic'], pg['faq']
    side = ''.join('<li><a href="%sfaq/%s/"%s>%s</a></li>' % (root, x['slug'], ' aria-current="page"' if x['slug'] == t['slug'] else '', esc(x['menu_title'])) for x in topics)
    qs = ''.join(
        '<details class="fq-q" id="%s"%s><summary><span>%s</span></summary><div class="fq-a">%s</div></details>'
        % (q['id'], ' open' if i == 0 else '', q['q'], r(q['a'], root)) for i, q in enumerate(t['qas']))
    intro = ('<div class="fq-intro">%s</div>' % r(t['intro'], root)) if t.get('intro') else ''
    head = ph([('Home', root), ('Resources', root + 'resources/'), ('Frequently asked questions', root + FAQ_HUB + '/'), (esc(t['menu_title']), None)], esc(t['title']), esc(t['short']))
    return (head
            + '<section class="sec fq"><div class="fq__grid"><aside class="fq__side"><nav aria-label="FAQ topics"><p class="fq__k">FAQ topics</p>'
              '<ul>%s</ul><a class="fq__all" href="%s%s/">All FAQs <i>&rarr;</i></a></nav></aside>' % (side, root, FAQ_HUB)
            + '<div class="fq__main">%s<div class="fq-bar"><span>%d questions</span><button type="button" class="fq-tog" data-fq-all aria-pressed="false">Expand all</button></div>'
              '<div class="fq-list">%s</div>' % (intro, t['n'], qs)
            + help_band(root, wa) + '</div></div></section>')
