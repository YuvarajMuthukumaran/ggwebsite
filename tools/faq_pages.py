"""Frequently asked questions: /faq/ and /faq/<topic>/, built from data/faq/*.json by tools/build_site.py.

One JSON file per topic (title, short, optional intro, and a list of questions with HTML answers). Adding a file adds a
page at /faq/<slug>/, a card on /faq/ and a link on the FAQ pages' topic lists. The answers
come from the FAQ page on goravgupta.com (the page kept at SOURCE_PATH), grouped by topic. Every topic page also carries
FAQPage structured data.
"""
import json
import pathlib
import re

from hub_pages import icon

DATA = pathlib.Path(__file__).resolve().parent.parent / 'data' / 'faq'
SITE = 'https://goravgupta.com'
SOURCE_PATH = 'frequently-asked-questions-psychiatrist-near-me-consultation'
TITLE = 'Frequently Asked Questions (FAQ)'
LEDE = ('Answers to the questions people ask most before they see a psychiatrist: when to seek help, how treatment works, '
        'what a consultation involves and who Dr. Gorav Gupta is.')
# questions shown on /faq/ (topic slug, question number within the topic)
POPULAR = [('when-to-see-a-psychiatrist', 1), ('psychiatrist-vs-psychologist', 2), ('consultation-and-fees', 0),
           ('treatment-and-therapy', 0), ('treatment-and-therapy', 4), ('about-dr-gorav-gupta', 0)]

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
    popular = [topics_by(topics, s)['qas'][i] for s, i in POPULAR if topics_by(topics, s)]
    out = [{'kind': 'faq-index', 'path': 'faq', 'nav': 'resources', 'crumb': 'Frequently asked questions',
            'title': '%s | Dr. Gorav Gupta' % TITLE,
            'description': 'Frequently asked questions about seeing a psychiatrist in Delhi NCR: when to seek help, treatment and therapy, '
                           'consultation and fees, and about Dr. Gorav Gupta.',
            'scripts': ['faq'], 'faq': topics, 'ld_extra': faq_ld(popular)}]
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
    cur = ' aria-current="page"' if path == 'faq' else ''
    return ('<a href="%sfaq/"%s>%s<span class="dd__tx"><b>Frequently asked questions (FAQ)</b><small>Answers on consulting, treatment and fees</small></span></a>'
            % (root, cur, icon('help')))


def r(html, root):
    return html.replace('{{root}}', root)


def first_part(html):
    """The opening paragraph (or the whole answer when it starts with a list)."""
    m = re.match(r'\s*(<p>.*?</p>)', html, re.S)
    return m.group(1) if m else html


def help_band(root, wa, full_guide=True):
    return ('<aside class="fq-help"><div><p class="fq-help__t">Didn&rsquo;t find your answer?</p>'
            '<p>Call the clinic or message the team on WhatsApp. Consultations are available online and at both consulting rooms.</p></div>'
            '<div class="fq-help__a"><a class="btn" href="tel:+918800000255">Call +91 88000 00255</a>'
            '<a class="btn ghost" href="%s" target="_blank" rel="noopener">WhatsApp</a>%s</div></aside>'
            % (wa, ('<a class="more__a" href="%s%s/">Read the full guide <i>&rarr;</i></a>' % (root, SOURCE_PATH)) if full_guide else ''))


def index_body(pg, root, ph, wa):
    topics = pg['faq']
    cards = ''.join(
        '<li class="reveal" style="--i:%d"><a class="tq-card fq-card" href="%sfaq/%s/"><span class="tq-card__n" aria-hidden="true">%02d</span>'
        '<h2>%s</h2><p>%s</p><ul class="tq-chips"><li>%d questions</li></ul><span class="tq-card__go">View answers <i aria-hidden="true">&rarr;</i></span></a></li>'
        % (i, root, t['slug'], i + 1, esc(t['title']), esc(t['short']), t['n']) for i, t in enumerate(topics))
    pop = ''
    for s, i in POPULAR:
        t = topics_by(topics, s)
        if not t:
            continue
        q = t['qas'][i]
        pop += ('<details class="fq-q"><summary><span>%s</span></summary><div class="fq-a">%s<p class="fq-a__more"><a href="%sfaq/%s/#%s">More in &ldquo;%s&rdquo; <i>&rarr;</i></a></p></div></details>'
                % (q['q'], r(first_part(q['a']), root), root, s, q['id'], esc(t['menu_title'])))
    head = ph([('Home', root), ('Resources', root + 'resources/'), ('Frequently asked questions', None)], TITLE, LEDE)
    return (head
            + '<section class="sec tq-idx" aria-label="FAQ topics"><ul class="tq-grid">%s</ul></section>' % cards
            + '<section class="sec fq-pop" aria-labelledby="fq-pop-h"><div class="head"><h2 id="fq-pop-h">Popular questions</h2></div><div class="fq-list">%s</div></section>' % pop
            + '<section class="sec fq-end">%s</section>' % help_band(root, wa))


def topic_body(pg, root, ph, wa):
    t, topics = pg['topic'], pg['faq']
    side = ''.join('<li><a href="%sfaq/%s/"%s>%s</a></li>' % (root, x['slug'], ' aria-current="page"' if x['slug'] == t['slug'] else '', esc(x['menu_title'])) for x in topics)
    qs = ''.join(
        '<details class="fq-q" id="%s"%s><summary><span>%s</span></summary><div class="fq-a">%s</div></details>'
        % (q['id'], ' open' if i == 0 else '', q['q'], r(q['a'], root)) for i, q in enumerate(t['qas']))
    intro = ('<div class="fq-intro">%s</div>' % r(t['intro'], root)) if t.get('intro') else ''
    head = ph([('Home', root), ('Resources', root + 'resources/'), ('Frequently asked questions', root + 'faq/'), (esc(t['menu_title']), None)], esc(t['title']), esc(t['short']))
    return (head
            + '<section class="sec fq"><div class="fq__grid"><aside class="fq__side"><nav aria-label="FAQ topics"><p class="fq__k">FAQ topics</p>'
              '<ul>%s</ul><a class="fq__all" href="%sfaq/">All FAQs <i>&rarr;</i></a></nav></aside>' % (side, root)
            + '<div class="fq__main">%s<div class="fq-bar"><span>%d questions</span><button type="button" class="fq-tog" data-fq-all aria-pressed="false">Expand all</button></div>'
              '<div class="fq-list">%s</div>' % (intro, t['n'], qs)
            + help_band(root, wa) + '</div></div></section>')
