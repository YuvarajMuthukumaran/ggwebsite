"""Services dropdown and the Resources hub page, used by tools/build_site.py."""
import re

TOPICS = [   # (key, label, pattern matched against a post's slug and title)
    ('addiction', 'Addiction', r'alcohol|addict|drink|drug|substance|smok|cannabis|marijuana|relapse|buprenorphine|withdrawal|delirium|sobri'),
    ('anxiety', 'Anxiety &amp; OCD', r'anxiety|ocd|panic|stress|obsess|phobia'),
    ('mood', 'Depression &amp; bipolar', r'depress|bipolar|bi-polar|postpartum|mood|seasonal|suicid|self-harm'),
    ('schizophrenia', 'Schizophrenia', r'schizo|hallucinat|antipsychotic|psychos'),
    ('personality', 'Personality', r'personality|narciss|borderline|bpd'),
]
OTHER = ('wellbeing', 'Wellbeing')

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
    pool = TOPIC_IMG[topic(p)[0]]
    return IMG + pool[n % len(pool)]


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def topic(p):
    text = (p['slug'] + ' ' + p['title']).lower()
    for key, label, pat in TOPICS:
        if re.search(pat, text):
            return key, label
    return OTHER


def services_menu(root, groups, by_slug, path):
    def a(href, label, sub=''):
        cur = ' aria-current="page"' if href == path else ''
        return '<a href="%s%s/"%s><b>%s</b>%s</a>' % (root, href, cur, label, ('<small>%s</small>' % sub) if sub else '')
    cols = ''.join('<div class="dd__g"><p class="dd__k">%s</p>%s</div>'
                   % (esc(title), ''.join(a(by_slug[s]['path'], esc(by_slug[s]['title'])) for s in slugs if s in by_slug))
                   for title, slugs in groups['condition_groups'])
    return ('<div class="dd__in dd__in--wide">' + a('services', 'All services', 'Every condition Dr. Gupta treats')
            + '<div class="dd__cols">%s</div></div>' % cols)


def resources_hub(root, posts, tests, href, pretty_date):
    """The body of /resources/: quick-test band, topic filter, featured article, article grid, more resources."""
    def img(p):
        m = re.search(r'<img[^>]*src="\{\{root\}\}([^"]+)"', p['_body'])
        return root + (m.group(1) if m else stand_in(p, posts.index(p)))

    def card(p, big=False):
        key, label = topic(p)
        src = img(p)
        pic = ('<img src="%s" alt="" loading="%s" decoding="async">' % (src, 'eager' if big else 'lazy')) if src \
            else '<span class="hb-ph" aria-hidden="true">%s</span>' % label.split(' ')[0].replace('&amp;', '')
        return ('<li class="hb-a%s" data-topic="%s"><a href="%s"><span class="hb-a__img">%s</span><span class="hb-a__b">'
                '<span class="hb-a__m"><span class="hb-tag">%s</span><time datetime="%s">%s</time></span>'
                '<b>%s</b>%s<span class="hb-a__go">Read article <i aria-hidden="true">→</i></span></span></a></li>'
                % (' hb-a--big' if big else '', key, href(p, root), pic, label, p['date'], pretty_date(p['date']), esc(p['title']),
                   ('<span class="hb-a__x">%s</span>' % esc(p.get('excerpt', ''))) if big else ''))

    used = {topic(p)[0] for p in posts}
    chips = '<button type="button" class="hb-chip" aria-pressed="true" data-topic="all">All topics</button>' + ''.join(
        '<button type="button" class="hb-chip" aria-pressed="false" data-topic="%s">%s</button>' % (k, l)
        for k, l, _ in TOPICS + [OTHER + ('',)] if k in used)
    quick = ''.join('<li><a href="%stests/%s/">%s <i aria-hidden="true">→</i></a></li>' % (root, t['slug'], esc(t['menu_title'])) for t in tests)
    more = [('frequently-asked-questions-psychiatrist-near-me-consultation', 'Frequently asked questions', 'About psychiatrists, consultation and treatment.'),
            ('ask-the-doctor', 'Ask the Doctor', 'Questions often asked about mental illness and addiction.'),
            ('video-gallery', 'Video Gallery', 'Films and YouTube videos from Dr. Gupta.'),
            ('publication', 'Publications', 'Articles and press coverage.'),
            ('testimonials', 'Testimonials', 'What clients and families say.'),
            ('services', 'Conditions we treat', 'Guides to every condition and its treatment.')]
    return (
        '<header class="ph hb-hdr"><div class="ph__in hb-head"><nav class="crumb" aria-label="Breadcrumb"><a href="%s">Home</a>'
        '<span aria-hidden="true">/</span><span aria-current="page">Resources</span></nav><h1>Resources</h1>'
        '<p class="ph__lede">Articles, guides, answers and films from Dr. Gorav Gupta, to help you make sense of mental health and addiction.</p></div>'
        '</div><nav class="hb-quick" aria-label="Take a quick test"><img class="hb-quick__doc" src="%sassets/img/portrait-close-col.webp" alt="" width="40" height="40">'
        '<span class="hb-quick__k"><b>Take a quick test</b><small>Private, 2 to 4 minutes</small></span><ul>%s</ul>'
        '<a class="btn hb-quick__all" href="%stests/">All tests <i aria-hidden="true">→</i></a></nav></header>'
        % (root, root, quick, root)
        + '<section class="sec hb" aria-labelledby="hb-h"><div class="hb-bar"><h2 id="hb-h">Articles</h2>'
          '<div class="hb-chips" role="group" aria-label="Filter articles by topic">%s</div></div>'
          '<ul class="hb-grid" id="hb-grid">%s%s</ul>'
          '<p class="hb-empty" hidden>No articles on this topic yet.</p>'
          '<div class="hb-moreb"><button type="button" class="btn ghost" id="hb-more">Show more articles</button>'
          '<a class="more__a" href="%sblog/">Browse the blog <i>→</i></a></div></section>'
        % (chips, card(posts[0], True), ''.join(card(p) for p in posts[1:]), root)
        + '<section class="sec hb-x" aria-labelledby="hb-x-h"><h2 id="hb-x-h">More resources</h2><ul class="hb-tiles">%s</ul></section>'
        % ''.join('<li><a href="%s%s/"><b>%s</b><span>%s</span><i aria-hidden="true">→</i></a></li>' % (root, s, t, d) for s, t, d in more))
