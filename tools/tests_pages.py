"""Interactive self-assessment tests, built from data/tests/*.json by tools/build_site.py.

One JSON file per test. Adding a file adds a page at /tests/<slug>/, a card on /tests/ and an entry
in the Resources menu; no template or script needs to change. assets/js/tests.js runs the test
in the browser from the JSON embedded in the page. Answers never leave the device.
"""
import json
import pathlib

from hub_pages import icon, TESTS_HUB as HUB

TEST_ICON = {'mental-health-self-assessment': 'pulse', 'bipolar-early-warning-signs': 'wave', 'schizophrenia-relapse-signs': 'eye',
             'relapse-risk-assessment': 'shield', 'substance-use-vs-social-use': 'glass'}

DATA = pathlib.Path(__file__).resolve().parent.parent / 'data' / 'tests'

# A condition page and the test that belongs to it. The page that a test was written from
# gets source_callout(); these are the pages that should offer a test but are not its source.
PAGE_TEST = {
    'psychiatrist-de-addiction-treatment-delhi-gurgaon': 'relapse-risk-assessment',
    'psychiatrist-alcohol-deaddiction-treatment-delhi-gurgaon': 'substance-use-vs-social-use',
    'smoking-cessation': 'substance-use-vs-social-use',
    'best-bipolar-disorder-psychiatrist-delhi-gurgaon': 'bipolar-early-warning-signs',
    'schizophrenia-psychiatrist-delhi-gurgaon-ncr': 'schizophrenia-relapse-signs',
    'depression-psychiatrist-doctor-in-delhi-gurgaon': 'mental-health-self-assessment',
    'best-psychiatrist-anxiety-specialist-delhi-gurgaon': 'mental-health-self-assessment',
    'ocd-psychiatrist-in-gurgaon-delhi-ncr': 'mental-health-self-assessment',
    'stress-management-psychologist-counselling-delhi-gurgaon': 'mental-health-self-assessment',
}

# The hub lives at HUB (see hub_pages). The individual tests keep their own /tests/<slug>/ paths:
# they are new URLs with no search history, so moving them would only add redirects.

ICON_CLOCK = ('<svg viewBox="0 0 256 256" fill="currentColor" aria-hidden="true"><path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24Zm0,192a88,88,0,1,1,88-88A88.1,88.1,0,0,1,128,216Zm64-88a8,8,0,0,1-8,8H128a8,8,0,0,1-8-8V72a8,8,0,0,1,16,0v48h48A8,8,0,0,1,192,128Z"/></svg>')
ICON_LIST = ('<svg viewBox="0 0 256 256" fill="currentColor" aria-hidden="true"><path d="M224,128a8,8,0,0,1-8,8H104a8,8,0,0,1,0-16H216A8,8,0,0,1,224,128ZM104,72H216a8,8,0,0,0,0-16H104a8,8,0,0,0,0,16ZM216,184H104a8,8,0,0,0,0,16H216a8,8,0,0,0,0-16ZM56,116a12,12,0,1,0,12,12A12,12,0,0,0,56,116Zm0-64A12,12,0,1,0,68,64,12,12,0,0,0,56,52Zm0,128a12,12,0,1,0,12,12A12,12,0,0,0,56,180Z"/></svg>')
ICON_LOCK = ('<svg viewBox="0 0 256 256" fill="currentColor" aria-hidden="true"><path d="M208,80H176V56a48,48,0,0,0-96,0V80H48A16,16,0,0,0,32,96V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V96A16,16,0,0,0,208,80ZM96,56a32,32,0,0,1,64,0V80H96ZM208,208H48V96H208V208Z"/></svg>')

# The shared facts (data/site.json), set by build_site.py: the crisis line comes from there.
VARS = {}

DISCLAIMER = ('This is a screening tool, not a diagnosis. Only a qualified professional can assess and diagnose a mental health condition.')
PRIVACY = ('Private by design: your answers are worked out in your browser only. Nothing is saved, sent or shared.')


def _test_desc(short, n, m):
    """The short line plus the length of the test, kept under about 160 characters for search results."""
    suf = ' %d questions, about %d minutes. Private, not a diagnosis.' % (n, m)
    sh = short.rstrip('.')
    room = 160 - len(suf)
    if len(sh) > room:
        k = max(sh.rfind(',', 0, room), sh.rfind(' to ', 0, room))
        sh = sh[:k] if k > 40 else sh[:room].rsplit(' ', 1)[0]
    return sh + '.' + suf


def load():
    tests = [json.loads(f.read_text(encoding='utf-8')) for f in sorted(DATA.glob('*.json'))] if DATA.exists() else []
    for t in tests:
        t['n'] = len(t['questions'])
    return sorted(tests, key=lambda t: (t.get('order', 99), t['slug']))


def items(tests):
    """Page records for build_site.py's render loop."""
    out = [{'kind': 'tests-index', 'path': HUB, 'nav': 'resources', 'crumb': 'Interactive tests',
            'title': 'Mental Health Assessment Tests: Free, Private Screening | Dr. Gorav Gupta',
            'description': 'Free, private self-assessment tests by Dr. Gorav Gupta: mental health, bipolar early signs, '
                           'schizophrenia relapse signs and substance use. Not a diagnosis.',
            'tests': tests}]
    for t in tests:
        out.append({'kind': 'test', 'path': 'tests/' + t['slug'], 'nav': 'resources', 'crumb': t['menu_title'],
                    'title': '%s | Interactive Test | Dr. Gorav Gupta' % t['title'],
                    'description': _test_desc(t['short'], t['n'], t['minutes']),
                    'scripts': ['tests'], 'test': t})
    return out


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def menu(root, tests, path, extra=''):
    """The Resources dropdown in the header. The current page gets aria-current."""
    def a(href, label, sub='', ic='clipboard'):
        cur = ' aria-current="page"' if href == path else ''
        return '<a href="%s%s/"%s>%s<span class="dd__tx"><b>%s</b>%s</span></a>' % (
            root, href, cur, icon(ic), label, ('<small>%s</small>' % sub) if sub else '')
    return ('<div class="dd__in">'
            + a('resources', 'Articles &amp; resources', 'Guides, conditions and the blog', 'book')
            + a(HUB, 'Interactive tests', 'Private self-assessment tools', 'clipboard')
            + extra
            + '</div>')


def meta_chips(t):
    return ('<ul class="tq-chips" aria-label="About this test"><li>%s%d questions</li><li>%sAbout %d min</li><li>%sPrivate</li></ul>'
            % (ICON_LIST, t['n'], ICON_CLOCK, t['minutes'], ICON_LOCK))


def crisis_note():
    """Shown wherever someone might be taking a test in a bad moment."""
    line = VARS.get('crisis_line', '')
    if not line:
        return ''
    return ('<aside class="tq-help" role="note" aria-label="Crisis support"><p><b>If you need support right now</b></p>'
            '<p>%s</p></aside>' % esc(line).replace('14416', '<a href="tel:14416">14416</a>'))


def index_body(pg, root, ph):
    cards = ''.join(
        '<li class="reveal" style="--i:%d"><a class="tq-card" href="%stests/%s/"><span class="tq-card__n" aria-hidden="true">%02d</span>'
        '<h2>%s</h2><p>%s</p>%s<span class="tq-card__go">Start test <i aria-hidden="true">→</i></span></a></li>'
        % (i, root, t['slug'], i + 1, esc(t['title']), esc(t['short']), meta_chips(t))
        for i, t in enumerate(pg['tests']))
    lede = ('A quick way to check whether what you are experiencing looks like the symptoms of a mental health condition. '
            'Each test is private, takes a few minutes, and is a starting point for a conversation with Dr. Gorav Gupta.')
    head = ph([('Home', root), ('Resources', root + 'resources/'), ('Interactive tests', None)], 'Interactive tests', lede)
    head = head.replace('<header class="ph">', '<header class="ph ph--c">', 1)      # centred header
    return (head
            + '<section class="sec tq-idx" aria-label="Tests"><ul class="tq-grid">%s</ul>%s'
              '<div class="tq-fine reveal"><p>%s<span>%s</span></p><p>%s</p></div></section>'
            % (cards, crisis_note(), ICON_LOCK, PRIVACY, DISCLAIMER))


def test_body(pg, root, ph, wa):
    t = pg['test']
    numbered = t['scoring']['type'] == 'sum'   # show the 0-4 values the old site printed; yes/no answers have none
    legend = ''.join('<li>%s<b>%s</b>%s</li>' % (('<i>%d</i>' % o['value']) if numbered else '', esc(o['label']),
                                                (' <span>%s</span>' % esc(o['hint'])) if o.get('hint') else '')
                     for o in t['scale'])
    ph_field = ''
    if t.get('placeholder'):
        p = t['placeholder']
        ph_field = ('<div class="tq-field"><label for="tq-sub">%s</label><input id="tq-sub" type="text" autocomplete="off" '
                    'spellcheck="false" maxlength="40" placeholder="%s" aria-describedby="tq-sub-h"><p id="tq-sub-h">%s</p></div>'
                    % (esc(p['label']), esc(p['default'].capitalize()), esc(p['hint'])))
    data = json.dumps(t, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    intro = ('<div class="tq-screen tq-intro" data-screen="intro">%s'
             '<h2 class="tq-h" tabindex="-1">What this test measures</h2><p>%s</p>'
             '<h3>How to answer</h3><p>%s</p><ul class="tq-legend">%s</ul>%s'
             '<div class="tq-notes"><p>%s<span>%s</span></p><p class="tq-notes__d"><span>%s</span></p></div>'
             '<div class="tq-start"><button class="btn tq-go" type="button" data-act="start" disabled>Start the test <i aria-hidden="true">→</i></button>'
             '%s</div></div>'
             % (meta_chips(t), esc(t['intro']['measures']), esc(t['intro']['instructions']), legend, ph_field,
                ICON_LOCK, PRIVACY, DISCLAIMER,
                '' if t['source']['page'] == HUB else '<a class="tq-src" href="%s%s/">Read about this topic</a>' % (root, t['source']['page'])))
    return (ph([('Home', root), ('Interactive tests', root + HUB + '/'), (esc(t['menu_title']), None)], esc(t['title']), esc(t['short']))
            + '<section class="sec tq-sec" aria-label="%s">' % esc(t['title'])
            + '<div class="tq-card tq-app" id="tq" data-contact="%scontactus/" data-wa="%s" data-index="%s%s/" data-doc="%sassets/img/portrait-close-col.webp" data-root="%s" data-wanum="%s" data-phone="%s">%s'
              '<div class="tq-screen tq-qs" data-screen="q" hidden></div><div class="tq-screen tq-res" data-screen="result" hidden></div>'
              '<noscript><p class="tq-ns">This test runs in your browser and needs JavaScript. You can read the questions on '
              '<a href="%s%s/">the article page</a>.</p></noscript></div>'
            % (root, wa, root, HUB, root, root, VARS.get('wa_number', ''), VARS.get('phone_href', ''), intro, root, t['source']['page'])
            + '<p class="tq-more"><a class="more__a" href="%smental-health-assessment-tests/">All interactive tests <i>→</i></a></p></section>' % root
            + '<script type="application/json" id="tq-data">%s</script>' % data)


def page_callout(root, tests, slug):
    """The test that matches this condition page, for the end of the page."""
    want = PAGE_TEST.get(slug)
    t = next((x for x in tests if x['slug'] == want), None) if want else None
    if not t:
        return ''
    return ('<aside class="tq-call tq-call--end"><div><p class="tq-call__k">Before your consultation</p>'
            '<p class="tq-call__t">%s</p><p>%d questions, about %d minutes. Private: your answers stay on your '
            'device, and nothing is saved or sent.</p></div>'
            '<a class="btn" href="%stests/%s/">Take the test <i aria-hidden="true">&rarr;</i></a></aside>'
            % (esc(t['title']), t['n'], t['minutes'], root, t['slug']))


def source_callout(root, tests, slug):
    """On an old-site article that carried a test, point to the interactive version."""
    for t in tests:
        if t['source']['page'] == slug:
            return ('<aside class="tq-call"><div><p class="tq-call__k">Interactive test</p><p class="tq-call__t">%s</p>'
                    '<p>%d questions, about %d minutes. Private: answers stay on your device.</p></div>'
                    '<a class="btn" href="%stests/%s/">Take the test <i aria-hidden="true">→</i></a></aside>'
                    % (esc(t['title']), t['n'], t['minutes'], root, t['slug']))
    return ''
