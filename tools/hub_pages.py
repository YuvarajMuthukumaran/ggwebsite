"""Services dropdown and the Resources hub page, used by tools/build_site.py."""
import re

# Both hubs are served at the old site's URLs, because those carry the search traffic: the tests hub
# at /mental-health-assessment-tests/ (306 clicks a month) and the FAQ at the long URL (284). /tests/
# and /faq/ 301 to them (see vercel.json). Defined here because every generator imports this module.
TESTS_HUB = 'mental-health-assessment-tests'
FAQ_HUB = 'frequently-asked-questions-psychiatrist-near-me-consultation'

# Small line icons for the nav dropdowns (24px grid, drawn with currentColor)
ICONS = {
    'book': '<path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z"/><path d="M4 21V5"/><path d="M9 7.5h6"/>',
    'clipboard': '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4V2.8h6V4"/><path d="m9 13 2 2 4-4"/>',
    'pulse': '<path d="M20.8 8.6a5 5 0 0 0-8.8-3 5 5 0 0 0-8.8 3c0 5.4 8.8 11 8.8 11s8.8-5.6 8.8-11z"/><path d="M3.6 12h4l2-3 3 6 2-3h5.8"/>',
    'wave': '<path d="M2 12c2.5-6 5-6 7.5 0s5 6 7.5 0c1.2-2.8 2.6-3.6 5-2"/>',
    'eye': '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    'shield': '<path d="M12 3 4.5 6v6c0 4.8 3.2 8.2 7.5 9 4.3-.8 7.5-4.2 7.5-9V6z"/><path d="m9 12 2 2 4-4"/>',
    'glass': '<path d="M7.5 3h9l-1 8.5a3.5 3.5 0 0 1-7 0z"/><path d="M12 15v6M8.5 21h7"/>',
    'grid': '<rect x="3.5" y="3.5" width="7" height="7" rx="2"/><rect x="13.5" y="3.5" width="7" height="7" rx="2"/><rect x="3.5" y="13.5" width="7" height="7" rx="2"/><rect x="13.5" y="13.5" width="7" height="7" rx="2"/>',
    'pill': '<path d="M10.5 20.5a5 5 0 0 1-7-7l6-6a5 5 0 0 1 7 7z"/><path d="m7 10 7 7"/>',
    'wind': '<path d="M3 8h10a3 3 0 1 0-3-3"/><path d="M3 12h15a3 3 0 1 1-3 3"/><path d="M3 16h6"/>',
    'user': '<circle cx="12" cy="8" r="4"/><path d="M4.5 21a7.5 7.5 0 0 1 15 0"/>',
    'leaf': '<path d="M5 19c0-8 5-13 15-14-1 10-6 15-14 15"/><path d="M5 19 13 11"/>',
    'pin': '<path d="M12 21s-7-5.6-7-11a7 7 0 0 1 14 0c0 5.4-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    'help': '<circle cx="12" cy="12" r="9"/><path d="M9.6 9.4a2.5 2.5 0 1 1 3.5 2.3c-.7.4-1.1.9-1.1 1.7"/><path d="M12 17h.01"/>',
}


def icon(name, cls='dd__ic'):
    return ('<span class="%s" aria-hidden="true"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" '
            'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">%s</svg></span>' % (cls, ICONS[name]))


GROUP_ICON = [(r'addiction|substance', 'pill'), (r'schizo', 'eye'), (r'mood|depress', 'wave'), (r'anxiety|ocd|stress', 'wind'),
              (r'personality', 'user'), (r'eating', 'leaf')]


def group_icon(title):
    return next((n for pat, n in GROUP_ICON if re.search(pat, title.lower())), 'grid')

TOPICS = [   # (key, label, pattern matched against a post's slug and title)
    ('addiction', 'Addiction', r'alcohol|addict|drink|drug|substance|smok|cannabis|marijuana|relapse|buprenorphine|withdrawal|delirium|sobri'),
    ('anxiety', 'Anxiety &amp; OCD', r'anxiety|ocd|panic|stress|obsess|phobia'),
    ('mood', 'Depression &amp; bipolar', r'depress|bipolar|bi-polar|postpartum|mood|seasonal|suicid|self-harm'),
    ('schizophrenia', 'Schizophrenia', r'schizo|hallucinat|antipsychotic|psychos'),
    ('personality', 'Personality', r'personality|narciss|borderline|bpd'),
]
OTHER = ('wellbeing', 'Wellbeing')
HINDI = ('hindi', 'हिंदी')

# Stand-in pictures for posts that have none: a close keyword match first, then the topic's pool (rotated).
IMG = 'assets/img/blog/'
KEYWORD_IMG = [
    (r'sleep', 'healthy-sleep.webp'), (r'panic', 'panic-disorder-treatment-psychiatrist.webp'),
    (r'health anxiety|anxiety', 'anxiety-disorder_11zon.webp'), (r'ocd|obsess', 'ocd-psychiatrist.webp'),
    (r'stress|remote|work', 'work-related-stress-700x525.webp'), (r'postpartum', 'postpartum-depression.webp'),
    (r'seasonal', 'seasonal-affective-disorder.webp'), (r'bipolar|bi-polar', 'bipolar-i-symptoms.webp'),
    (r'depress', 'depression-depression-causes-in-delhi.webp'), (r'self-harm|suicid', 'self-harm_11zon.webp'),
    (r'hallucinat', 'hallucination-700x525.webp'), (r'relapse', 'relapse-prevention.webp'),
    (r'schizo', 'intricacies-of-schizophrenia.webp'), (r'narciss', 'narcissistic-personality-disorder.webp'),
    (r'borderline|bpd', 'bpd-treatment_11zon.webp'), (r'personality', 'personality-disorders.webp'),
    (r'eating|anorexia|nutrition', 'rise-of-eating-disorders_11zon.webp'), (r'smok', 'smoking-cessation-treatment-by-psychiatrist-in-delhi_11zon.webp'),
    (r'teen|child', 'behavioral-problems2.webp'), (r'cannabis|marijuana|drug', 'drug-addiction-how-to-help-your-loved-one-fight-marijuana-addiction.webp'),
    (r'binge|drink', 'how-to-overcome-binge-drinkinggg.webp'), (r'alcohol', 'alcohol-addiction.webp'),
    (r'rehab', 'rehabitation-centre.webp'), (r'substance|addict', 'substance-use-disorder.webp'),
    (r'anger', 'anger-management-a-guide-to-a-healthier-life_11zon.webp'), (r'elderly|age', 'early-mental-health-issues.webp'),
    (r'stigma|misconception|myth', 'mental-health-moving-past-the-stigma_11zon.webp'),
    (r'psychiatrist|psychologist|counsel|therap|medication|prescribe', 'psychiatrist-near-me_11zon.webp'),
]
TOPIC_IMG = {
    'addiction': ['de-adiction-treatment.webp', 'manage-addiction-disorder-with-expert-intervention_11zon.webp', 'psychiatrist-for-alcohol-addiction-700x371.webp'],
    'anxiety': ['stress-_-anxiety.webp', 'anxiety.webp', 'anxiety-to-ocd.webp'],
    'mood': ['bipolar-ii-symptoms.webp', 'depression-depression-causes-in-delhi.webp'],
    'schizophrenia': ['schizophrenia-1-700x700.webp', 'signs-of-relapse-in-schizophrenia.webp'],
    'personality': ['personality-disorder.webp', 'personality-disordergg-700x467.webp'],
    'wellbeing': ['mental-health.webp', 'mental-health-2.webp', 'pink-self-care-mental-health-graph-1_11zon.webp', 'early-mental-health-issues.webp', 'stress-management_11zon.webp'],
}


def stand_in(p, n):
    text = (p['slug'] + ' ' + p['title']).lower().replace('-', ' ')
    for pat, f in KEYWORD_IMG:
        if re.search(pat, text):
            return IMG + f
    pool = TOPIC_IMG.get(topic(p)[0], TOPIC_IMG['wellbeing'])
    return IMG + pool[n % len(pool)]


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def topic(p):
    if p.get('lang') == 'hi':        # a Hindi reader is filtering for language, not for subject
        return HINDI
    text = (p['slug'] + ' ' + p['title']).lower()
    for key, label, pat in TOPICS:
        if re.search(pat, text):
            return key, label
    return OTHER


def services_menu(root, groups, by_slug, path):
    def a(href, label, sub='', ic=''):
        cur = ' aria-current="page"' if href == path else ''
        body = '<b>%s</b>%s' % (label, ('<small>%s</small>' % sub) if sub else '')
        return '<a href="%s%s/"%s>%s</a>' % (root, href, cur, (icon(ic) + '<span class="dd__tx">%s</span>' % body) if ic else body)
    cols = ''.join('<div class="dd__g"><p class="dd__k">%s%s</p>%s</div>'
                   % (icon(group_icon(title), 'dd__kic'), esc(title), ''.join(a(by_slug[s]['path'], esc(by_slug[s].get('menu_title') or by_slug[s]['title'])) for s in slugs if s in by_slug))
                   for title, slugs in groups['condition_groups'])
    return ('<div class="dd__in dd__in--wide">' + a('services', 'All services', 'Every condition Dr. Gupta treats', 'grid')
            + '<div class="dd__cols">%s</div></div>' % cols)

# Tags that describe the clinic or the search rather than a subject. They stay filterable, but are not offered first.
GENERIC_TAGS = {'psychiatrist', 'best-psychiatrist-in-delhi', 'top-psychiatrist-in-delhi', 'psychiatrist-in-delhi', 'psychiatrist-in-gurgaon',
                'psychiatrist-near-me', 'dr-gorav-gupta', 'drug-psychiatrist', 'addiction-psychiatrist', 'ocd-psychiatrist', 'psychiatric-clinic-in-delhi'}
FIRST_TAGS = 14

HERO_ART = (
    '<svg class="hb2-hero__art" viewBox="0 0 440 220" fill="none" aria-hidden="true" focusable="false">'
    '<circle cx="318" cy="112" r="132" fill="#ffffff" fill-opacity=".09"/><circle cx="318" cy="112" r="88" fill="#ffffff" fill-opacity=".08"/>'
    '<rect x="250" y="46" width="112" height="146" rx="14" transform="rotate(-9 306 119)" fill="#ffffff" fill-opacity=".32"/>'
    '<rect x="262" y="40" width="112" height="146" rx="14" transform="rotate(-3 318 113)" fill="#dbe9fb"/>'
    '<rect x="276" y="34" width="112" height="148" rx="14" fill="#ffffff"/>'
    '<rect x="296" y="62" width="58" height="9" rx="4.5" fill="#2f6fcb"/><circle cx="372" cy="66.500" r="5" fill="#2f6fcb"/>'
    '<rect x="296" y="86" width="76" height="6" rx="3" fill="#cfe0f5"/><rect x="296" y="102" width="76" height="6" rx="3" fill="#cfe0f5"/>'
    '<rect x="296" y="118" width="60" height="6" rx="3" fill="#cfe0f5"/><rect x="296" y="142" width="40" height="14" rx="7" fill="#e9f1fb"/>'
    '<path d="M408 40l4.500 11 11 4.500-11 4.500-4.500 11-4.500-11-11-4.500 11-4.500z" fill="#ffffff"/>'
    '<path d="M236 150l3 7 7 3-7 3-3 7-3-7-7-3 7-3z" fill="#ffffff" fill-opacity=".8"/>'
    '<circle cx="238" cy="78" r="5" fill="#ffffff" fill-opacity=".7"/><circle cx="410" cy="150" r="4" fill="#ffffff" fill-opacity=".5"/></svg>')
SEARCH_ICON = ('<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
               '<circle cx="11" cy="11" r="6.500"/><path d="m16 16 4.500 4.500"/></svg>')
FILTER_ICON = ('<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
               '<path d="M4 6h16M7 12h10M10 18h4"/></svg>')


def resources_hub(root, posts, tests, href, pretty_date, tag_map=None):
    """The body of /resources/: a banner, a sidebar of categories, tags and quick links, a filterable and searchable article grid
    (assets/js/hub.js), and more resources. Every article is in the HTML; hub.js filters, sorts and pages them in the browser."""
    tag_map = tag_map or {}

    def img(p):
        m = re.search(r'<img[^>]*src="\{\{root\}\}([^"]+)"', p['_body'])
        return root + (m.group(1) if m else stand_in(p, posts.index(p)))

    counts, names = {}, {}
    for p in posts:
        for s, n in tag_map.get(p['slug'], []):
            counts[s] = counts.get(s, 0) + 1
            names[s] = n

    def card(p, first=False):
        key, label = topic(p)
        tags = tag_map.get(p['slug'], [])
        minutes = max(1, round(p.get('words', 0) / 200))
        shown = [n for s, n in tags if s not in GENERIC_TAGS][:2]
        extra = ('<em>%s</em>' % ', '.join(esc(n) for n in shown)) if shown else ''
        text = ' '.join([p['title'], p.get('excerpt', ''), label.replace('&amp;', '&')] + [n for s, n in tags]).lower()
        return ('<li class="hb2-c" data-topic="%s" data-tags="%s" data-date="%s" data-title="%s" data-q="%s"><a href="%s"><span class="hb2-c__img">'
                '<img src="%s" alt="" loading="%s" decoding="async" width="640" height="360"></span><span class="hb2-c__b">'
                '<span class="hb2-c__k">%s%s</span><b class="hb2-c__t">%s</b><span class="hb2-c__x">%s</span>'
                '<span class="hb2-c__f"><span class="hb2-c__by">Dr. Gorav Gupta</span><span><time datetime="%s">%s</time> &middot; %d min read</span></span></span></a></li>'
                % (key, ' '.join(s for s, n in tags), p['date'], esc(p['title'].lower()), esc(text), href(p, root), img(p), 'eager' if first else 'lazy',
                   label, extra, esc(p['title']), esc(p.get('excerpt', '')), p['date'], pretty_date(p['date']), minutes))

    used = {topic(p)[0] for p in posts}
    tcount = {}
    for p in posts:
        tcount[topic(p)[0]] = tcount.get(topic(p)[0], 0) + 1
    cats = ('<li><button type="button" class="hb2-cat" data-topic="all" aria-pressed="true">All articles <span>%d</span></button></li>' % len(posts)
            + ''.join('<li><button type="button" class="hb2-cat" data-topic="%s" aria-pressed="false">%s <span>%d</span></button></li>' % (k, l, tcount[k])
                      for k, l, _ in TOPICS + [OTHER + ('',), HINDI + ('',)] if k in used))

    ranked = sorted(counts, key=lambda s: (-counts[s], names[s].lower()))
    first = [s for s in ranked if s not in GENERIC_TAGS][:FIRST_TAGS]
    rest = sorted((s for s in ranked if s not in first), key=lambda s: names[s].lower())

    def tag(s):
        return '<li><a class="hb2-tag" href="%stag/%s/" data-tag="%s">%s <span>%d</span></a></li>' % (root, s, s, esc(names[s]), counts[s])

    quick = ''.join('<li><a href="%stests/%s/">%s <i aria-hidden="true">&rarr;</i></a></li>' % (root, t['slug'], esc(t['menu_title'])) for t in tests)
    more = [(FAQ_HUB, 'Frequently asked questions (FAQ)', 'Answers on consulting, treatment, fees and Dr. Gupta.'),
            ('ask-the-doctor', 'Ask the Doctor', 'Questions often asked about mental illness and addiction.'),
            ('video-gallery', 'Video Gallery', 'Films and YouTube videos from Dr. Gupta.'),
            ('publication', 'Publications', 'Articles and press coverage.'),
            ('testimonials', 'Testimonials', 'What clients and families say.'),
            ('services', 'Conditions we treat', 'Guides to every condition and its treatment.')]

    hero = ('<header class="hb2-hero"><div class="hb2-hero__in"><nav class="crumb" aria-label="Breadcrumb"><a href="%s">Home</a><span aria-hidden="true">/</span>'
            '<span aria-current="page">Resources</span></nav><h1>Resources</h1>'
            '<p>Articles, guides, answers and films from Dr. Gorav Gupta, to help you make sense of mental health and addiction.</p></div>%s</header>' % (root, HERO_ART))
    side = ('<aside class="hb2-side" id="hb2-side" aria-label="Filter articles">'
            '<div class="hb2-box hb2-search"><label class="hb2-sr" for="hb2-q">Search articles</label><input id="hb2-q" type="search" placeholder="Search articles" autocomplete="off" spellcheck="false">%s</div>'
            '<div class="hb2-box hb2-catbox"><h2 class="hb2-k">Categories</h2><ul class="hb2-cats">%s</ul></div>'
            '<div class="hb2-box"><h2 class="hb2-k">Tags</h2><ul class="hb2-tags">%s</ul>'
            '<ul class="hb2-tags hb2-tags--more" id="hb2-tags-more" hidden>%s</ul>'
            '<button type="button" class="hb2-link" id="hb2-tagtog" aria-expanded="false" aria-controls="hb2-tags-more">Show all tags (%d)</button></div>'
            '<div class="hb2-box hb2-quick"><h2 class="hb2-k">Take a quick test</h2><ul>%s</ul><a class="hb2-link" href="%s%s/">All tests &rarr;</a></div></aside>'
            % (SEARCH_ICON, cats, ''.join(tag(s) for s in first), ''.join(tag(s) for s in rest), len(ranked), quick, root, TESTS_HUB))
    bar = ('<div class="hb2-bar"><button type="button" class="hb2-ftog" id="hb2-ftog" aria-expanded="false" aria-controls="hb2-side">%s Filters <b class="hb2-badge" hidden></b></button>'
           '<p class="hb2-count" id="hb2-count" aria-live="polite" tabindex="-1">%d articles</p>'
           '<label class="hb2-sort"><span class="hb2-sr">Sort articles</span><select id="hb2-sort"><option value="new">Newest first</option><option value="old">Oldest first</option>'
           '<option value="az">A to Z</option></select></label></div>' % (FILTER_ICON, len(posts)))
    main = ('<div class="hb2-main">'
            '<div class="hb2-active" id="hb2-active" hidden></div>'
            '<ul class="hb2-grid" id="hb2-grid">%s</ul>'
            '<div class="hb2-empty" id="hb2-empty" hidden><b>No articles match.</b><p>Try a different word, or clear the filters.</p><button type="button" class="btn ghost" id="hb2-clear">Clear filters</button></div>'
            '<nav class="hb2-pager" id="hb2-pager" aria-label="Article pages" hidden></nav></div>'
            % ''.join(card(p, i < 3) for i, p in enumerate(posts)))
    tiles = ''.join('<li><a href="%s%s/"><b>%s</b><span>%s</span><i aria-hidden="true">&rarr;</i></a></li>' % (root, s, t, d) for s, t, d in more)
    return (hero + '<section class="sec hb2" aria-label="Articles"><div class="hb2-layout">' + side + bar + main + '</div></section>'
            + '<section class="sec hb-x" aria-labelledby="hb-x-h"><h2 id="hb-x-h">More resources</h2><ul class="hb-tiles">%s</ul></section>' % tiles)
