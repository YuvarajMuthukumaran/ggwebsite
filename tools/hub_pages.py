"""Services dropdown and the Resources hub page, used by tools/build_site.py."""
import re

# Both hubs are served at the old site's URLs, because those carry the search traffic: the tests hub
# at /mental-health-assessment-tests/ (306 clicks a month) and the FAQ at the long URL (284). /tests/
# and /faq/ 301 to them (see vercel.json). Defined here because every generator imports this module.
TESTS_HUB = 'mental-health-assessment-tests'
FAQ_HUB = 'psychiatrist-near-me-consultation'

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
    'smoke': '<path d="M3 16h13v3.5H3z"/><path d="M16 16h4.5v3.5H16"/><path d="M13.5 4.5c0 2 2.5 2 2.5 4.5"/><path d="M17.5 3.5c0 2 2.5 2 2.5 4.5"/>',
    'brain': '<path d="M9 4a3 3 0 0 0-3 3 3 3 0 0 0-2 5 3 3 0 0 0 2 5 3 3 0 0 0 3 3 2 2 0 0 0 3-1.5V5.5A2 2 0 0 0 9 4z"/><path d="M15 4a3 3 0 0 1 3 3 3 3 0 0 1 2 5 3 3 0 0 1-2 5 3 3 0 0 1-3 3 2 2 0 0 1-3-1.5"/>',
    'cloud': '<path d="M6.5 14.5a4 4 0 1 1 1-7.9A5.5 5.5 0 0 1 18 9a3 3 0 0 1-.5 5.5z"/><path d="M8 17.5V20M12 17.5V20M16 17.5V20"/>',
    'swing': '<path d="M7 20V6"/><path d="m3.5 9.5 3.5-3.5 3.5 3.5"/><path d="M17 4v14"/><path d="m13.5 14.5 3.5 3.5 3.5-3.5"/>',
    'repeat': '<path d="m17 3 3 3-3 3"/><path d="M4 11V9a3 3 0 0 1 3-3h13"/><path d="m7 21-3-3 3-3"/><path d="M20 13v2a3 3 0 0 1-3 3H4"/>',
    'gauge': '<path d="M4 17a8 8 0 1 1 16 0"/><path d="m12 17 4-5"/><path d="M12 9V8M7.5 11l-.7-.7M16.5 11l.7-.7"/>',
    'layers': '<path d="m12 3 9 5-9 5-9-5z"/><path d="m3 13 9 5 9-5"/>',
    'split': '<circle cx="9" cy="12" r="5.5"/><circle cx="15" cy="12" r="5.5"/>',
    'mirror': '<ellipse cx="12" cy="10" rx="6" ry="7"/><path d="M12 17v4M8.5 21h7"/><path d="M9 7.5c.8-1 1.8-1.5 3-1.5"/>',
    'spark': '<path d="M12 3v4M12 17v4M3 12h4M17 12h4"/><path d="m6 6 2.5 2.5M15.5 15.5 18 18M18 6l-2.5 2.5M8.5 15.5 6 18"/>',
    'fork': '<path d="M7 3v8M5 3v5a2 2 0 0 0 4 0V3"/><path d="M7 11v10"/><path d="M17 3c-2 2-2 6 0 8v10"/>',
    'help': '<circle cx="12" cy="12" r="9"/><path d="M9.6 9.4a2.5 2.5 0 1 1 3.5 2.3c-.7.4-1.1.9-1.1 1.7"/><path d="M12 17h.01"/>',
    'play': '<rect x="3" y="4.5" width="18" height="13" rx="2.5"/><path d="M10 8.3v4.4l3.8-2.2z" fill="currentColor" stroke="none"/><path d="M8 20h8"/>',
    'quote': '<path d="M7.5 6h3v6a4 4 0 0 1-4 4H6v-2h.5A2 2 0 0 0 8.5 12H7.5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1zM15.5 6h3v6a4 4 0 0 1-4 4H14v-2h.5a2 2 0 0 0 2-2h-1a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1z"/>',
    'press': '<rect x="3" y="5" width="18" height="15" rx="2"/><path d="M3 9h18M8 13h3M8 16h7"/>',
}


def icon(name, cls='dd__ic'):
    return ('<span class="%s" aria-hidden="true"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" '
            'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">%s</svg></span>' % (cls, ICONS[name]))


GROUP_ICON = [(r'addiction|substance', 'pill'), (r'schizo', 'eye'), (r'mood|depress', 'wave'), (r'anxiety|ocd|stress', 'wind'),
              (r'personality', 'user'), (r'eating', 'leaf')]


# one icon per condition link, chosen from the page's address (the specific words first)
LINK_ICON = [(r'dual', 'split'), (r'borderline', 'split'), (r'narcissis', 'mirror'), (r'schizotypal', 'spark'), (r'personality', 'layers'),
             (r'eating|anorexia|bulimia', 'fork'), (r'smok', 'smoke'), (r'alcohol', 'glass'), (r'de-?addiction', 'shield'),
             (r'schizo', 'brain'), (r'depress', 'cloud'), (r'bipolar', 'swing'), (r'anxiety', 'pulse'), (r'ocd', 'repeat'), (r'stress', 'gauge')]


def link_icon(slug):
    return next((n for pat, n in LINK_ICON if re.search(pat, slug.lower())), 'grid')


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


CARDS = 'assets/img/cards/'   # six framings of each topic photograph (a whole frame, b to f close-ups), cut from assets/img/pages
def _c(name, keys):
    return [name + '-' + k for k in keys]
_X = lambda *f: ['blog/' + x for x in f]
_ADD = _c('alcohol-recovery', 'abcf') + _c('group-support', 'abcf') + ['alcohol-recovery-d', 'alcohol-recovery-e', 'consultation-c']
CARD_PHOTOS = [   # (pattern on slug and title, pictures in order of preference); None keeps the post's own picture
    (r'postpartum|seasonal|anger|sleep|hallucinat|delirium|recovery journey|psychiatrist near me|डर', None),
    (r'smok|quit', _c('smoking', 'af') + _X('smoking-cessation-treatment-by-psychiatrist-in-delhi_11zon')),
    (r'eating|anorexia|nutrition|diet', _c('eating', 'abcdef')),
    (r'schizotypal', _c('schizotypal-fog', 'adef')),
    (r'schizo|psychos|antipsychotic', _c('schizophrenia-fog', 'adefc') + _c('schizotypal-fog', 'adef')),
    (r'narciss|npd', _c('narcissism-mirror', 'abcdef')),
    (r'borderline|bpd', _c('borderline', 'adf') + _c('narcissism-mirror', 'dae')),
    (r'personality', _c('personality-masks', 'afe') + _c('borderline', 'adf')),
    (r'bipolar|bi polar', ['bipolar-light-a', 'bipolar-shadow-a', 'bipolar-light-d', 'bipolar-shadow-b', 'bipolar-light-f'] + _c('bipolar-shadow', 'cdef')),
    (r'ocd|obsess|ओसीडी', _c('ocd-handwashing', 'abcdef') + ['anxiety-d']),
    (r'alcohol|drink|withdrawal|sobriety', _ADD),
    (r'substance|addict|drug|cannabis|marijuana|rehab|relapse|buprenorphine|dual diagnosis', _ADD),
    (r'depress|self harm|suicid|mood|therapy actually', _c('depression', 'abcef') + ['anxiety-d', 'anxiety-f']),
    (r'anxiety|panic|stress|worry|phobia', _c('anxiety', 'abdf') + _c('stress-calm', 'af')),
    (r'psychiatrist|psychologist|counsel|consult|prescribe|online|test|habits|questions|dtms', _c('consultation', 'abcdef') + _c('stress-calm', 'af') + _c('group-support', 'abc')),
    (r'.', _c('stress-calm', 'af') + _c('group-support', 'abcf') + _c('depression', 'cef') + _c('anxiety', 'abdf')),
]


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


TREATMENT_LINKS = [('Deep TMS', 'https://www.tulasihealthcare.com/deep-tms-treatment/', 'brain'),
                   ('Modified ECT', 'https://www.tulasihealthcare.com/modified-electroconvulsive-therapy/', 'spark'),
                   ('Virtual reality therapy', 'https://www.tulasihealthcare.com/virtual-reality-therapy/', 'eye')]


# One line per page on the service group pages (/services/<group>/): what the page covers, in plain words.
SERVICE_BLURB = {
    'psychiatrist-de-addiction-treatment-delhi-gurgaon': 'Supervised detox and structured relapse prevention for alcohol and drug dependence.',
    'dual-diagnosis-treatment-delhi-gurgaon': 'Addiction treated together with the depression, anxiety, bipolar disorder or psychosis alongside it.',
    'psychiatrist-alcohol-deaddiction-treatment-delhi-gurgaon': 'Safe withdrawal, medication and follow-up for alcohol dependence.',
    'smoking-cessation': 'Assessment and support to help you stop smoking.',
    'schizophrenia-psychiatrist-delhi-gurgaon-ncr': 'Medication, family involvement and long-term care for schizophrenia.',
    'depression-psychiatrist-doctor-in-delhi-gurgaon': 'Assessment and treatment for persistent low mood and depression.',
    'best-bipolar-disorder-psychiatrist-delhi-gurgaon': 'Care for the highs and lows of bipolar disorder, built around early warning signs.',
    'best-psychiatrist-anxiety-specialist-delhi-gurgaon': 'The types, symptoms and treatment of anxiety disorders.',
    'ocd-psychiatrist-in-gurgaon-delhi-ncr': 'Assessment and treatment for obsessive-compulsive disorder.',
    'stress-management-psychiatrist-delhi-gurgaon': 'Help when stress starts to affect sleep, work or relationships.',
    'personality-disorder-treatment-delhi-india': 'Assessment and treatment for personality disorders.',
    'borderline-personality-disorder': 'Common signs, possible causes and treatment of borderline personality disorder.',
    'narcissistic-personality-disorder': 'Common signs, possible causes and treatment of narcissistic personality disorder.',
    'schizotypal-personality-disorder': 'Common signs and treatment of schizotypal personality disorder.',
    'eating-disorder-psychiatrist-delhi-gurgaon': 'Treatment for eating disorders and a troubled relationship with food.',
}
TREATMENT_BLURB = {
    'Deep TMS': 'Non-invasive magnetic stimulation of the brain, offered at Tulasi Healthcare for depression and OCD.',
    'Modified ECT': 'Electroconvulsive therapy under anaesthesia and close monitoring, a long-recognised option when other treatment has not worked.',
    'Virtual reality therapy': 'Gradual, guided exposure to difficult situations in a safe virtual setting.',
}
TREATMENTS = 'Treatments'


def group_slug(title):
    return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')


def group_href(title, slugs, by_slug):
    """Where a group leads: its own page, or straight to the condition when the group holds only one."""
    slugs = [x for x in slugs if x in by_slug]
    return by_slug[slugs[0]]['path'] if len(slugs) == 1 else 'services/' + group_slug(title)


def service_group_items(groups, by_slug):
    """One page per service group at /services/<group>/, listing the pages in it; the treatments are a group of their own.
    A group of one condition gets no page: the menu links to the condition itself."""
    out = []
    for title, slugs in list(groups['condition_groups']) + [(TREATMENTS, [])]:
        slugs = [x for x in slugs if x in by_slug]
        if title != TREATMENTS and len(slugs) < 2:
            continue
        desc = ('Deep TMS, modified ECT and virtual reality therapy, offered at Tulasi Healthcare.' if title == TREATMENTS else
                'Dr. Gorav Gupta on %s: each condition, how it is assessed and how it is treated, in Delhi, Gurugram and online.' % title.lower())
        out.append({'kind': 'svc-group', 'path': 'services/' + group_slug(title), 'nav': 'services', 'crumb': title, 'group_title': title,
                    'slugs': slugs, 'title': '%s | Dr. Gorav Gupta' % title, 'description': desc})
    return out


def service_group_body(pg, root, by_slug):
    """The body of /services/<group>/: the page header and one tile per page in the group, as on /resources/."""
    title = pg['group_title']
    tile = '<li><a class="hb-x2__c" href="%s"%s>%s<span class="hb-x2__b"><b>%s</b><span>%s</span></span><i aria-hidden="true">%s</i></a></li>'
    if title == TREATMENTS:
        tiles = ''.join(tile % (u, ' target="_blank" rel="noopener"', icon(ic, 'hb-x2__ic'), esc(n), TREATMENT_BLURB.get(n, ''), '&#8599;')
                        for n, u, ic in TREATMENT_LINKS)
        lede = 'Treatments Dr. Gupta uses alongside medication and therapy. Each opens on the Tulasi Healthcare website.'
    else:
        tiles = ''.join(tile % ('%s%s/' % (root, by_slug[x]['path']), '', icon(link_icon(x), 'hb-x2__ic'),
                                esc(by_slug[x].get('menu_title') or by_slug[x]['title']), SERVICE_BLURB.get(x, ''), '&rarr;')
                        for x in pg['slugs'])
        lede = 'Choose a condition to read what it involves and how Dr. Gupta assesses and treats it.'
    hero = ('<header class="hb2-hero hb2-hero--s"><div class="hb2-hero__in"><nav class="crumb" aria-label="Breadcrumb"><a href="%s">Home</a><span aria-hidden="true">/</span>'
            '<a href="%sservices/">Services</a><span aria-hidden="true">/</span><span aria-current="page">%s</span></nav><h1>%s</h1><p>%s</p></div></header>'
            % (root, root, esc(title), esc(title), lede))
    return hero + '<section class="sec hb-x2" aria-label="%s"><ul class="hb-x2__g">%s</ul></section>' % (esc(title), tiles)


def services_menu(root, groups, by_slug, path):
    """The Services dropdown in the header, laid out like the Resources one: "All services", then one row per group, each opening
    its own page (or the condition itself, for a group of one)."""
    def a(href, label, sub, ic):
        cur = ' aria-current="page"' if href == path else ''
        return '<a href="%s%s/"%s>%s<span class="dd__tx"><b>%s</b><small>%s</small></span></a>' % (root, href, cur, icon(ic), label, sub)
    rows = []
    for t, ss in groups['condition_groups']:
        ss = [x for x in ss if x in by_slug]
        if ss:
            sub = esc(by_slug[ss[0]].get('menu_title') or by_slug[ss[0]]['title']) if len(ss) == 1 else '%d conditions' % len(ss)
            rows.append(a(group_href(t, ss, by_slug), esc(t), sub, group_icon(t)))
    rows.append(a('services/' + group_slug(TREATMENTS), TREATMENTS, 'Deep TMS, modified ECT, VR therapy', 'pulse'))
    return '<div class="dd__in">' + a('services', 'All services', 'Every condition Dr. Gupta treats', 'grid') + ''.join(rows) + '</div>'

# Tags that describe the clinic or the search rather than a subject. They stay filterable, but are not offered first.
GENERIC_TAGS = {'psychiatrist', 'best-psychiatrist-in-delhi', 'top-psychiatrist-in-delhi', 'psychiatrist-in-delhi', 'psychiatrist-in-gurgaon',
                'psychiatrist-near-me', 'dr-gorav-gupta', 'drug-psychiatrist', 'addiction-psychiatrist', 'ocd-psychiatrist', 'psychiatric-clinic-in-delhi'}
FIRST_TAGS = 14

HERO_ART = (
    '<img class="hb2-hero__art" src="%sassets/img/resources-banner.webp" alt="Residents reading and talking together in the library at the Gurugram centre" width="960" height="624" decoding="async">')
SEARCH_ICON = ('<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
               '<circle cx="11" cy="11" r="6.500"/><path d="m16 16 4.500 4.500"/></svg>')
FILTER_ICON = ('<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
               '<path d="M4 6h16M7 12h10M10 18h4"/></svg>')


def resources_landing(root, posts):
    """The body of /resources/: a banner and one set of tiles into every part of the site that
    helps a visitor (articles, videos, tests, FAQ...). A directory, not the article list itself --
    that is its own page, articles_hub() at /blog/."""
    explore = [
        ('blog', 'Articles &amp; Blogs', '%d guides on mental health and addiction, searchable by condition.' % len(posts), 'book'),
        ('video-gallery', 'Video library', 'Short videos and real patient voices, in Hindi and English.', 'play'),
        (FAQ_HUB, 'Frequently asked questions', 'Answers on consulting, treatment, fees and Dr. Gupta.', 'help'),
        ('ask-the-doctor', 'Ask the Doctor', 'Questions patients and families often ask, answered directly.', 'quote'),
        ('psychiatrist-in-delhi', 'Psychiatrist in Delhi', 'Credentials, the Tulasi centres, achievements and OPD timings.', 'pin'),
        ('psychiatrist-in-gurgaon', 'Psychiatrist in Gurugram', 'What a psychiatrist does and when to see one, for NCR residents.', 'pin'),
        ('psychiatrist-in-india', 'Psychiatrist in India', 'Why to consult a psychiatrist, with national figures and FAQs.', 'pin'),
        ('publication', 'Publications', 'Articles and press coverage featuring Dr. Gupta.', 'press'),
        ('testimonials', 'Testimonials', 'What clients and families say about their care.', 'user'),
    ]
    explore_html = ''.join(
        '<li><a class="hb-x2__c" href="%s%s/">%s<span class="hb-x2__b"><b>%s</b><span>%s</span></span><i aria-hidden="true">&rarr;</i></a></li>'
        % (root, s, icon(ic, 'hb-x2__ic'), t, d) for s, t, d, ic in explore)
    facts = ('<ul class="tqh__facts" aria-label="About these resources"><li><b>%d</b> articles</li><li>Videos in <b>Hindi</b> and <b>English</b></li>'
             '<li><b>Free</b> to read</li></ul>' % len(posts))
    # a small illustration of what is inside, drawn in CSS like the tests banner: the newest article and a video
    p = posts[0] if posts else {'title': 'Mental health, explained', 'words': 1000}
    art = ('<div class="rsh__art" aria-hidden="true"><div class="rsh__c rsh__c--a"><span class="rsh__k">Article</span><b class="rsh__t">%s</b>'
           '<i class="rsh__l"></i><i class="rsh__l rsh__l--s"></i><span class="rsh__m">%d min read</span></div>'
           '<div class="rsh__c rsh__c--v"><span class="rsh__th"><span class="rsh__pl"></span></span><b class="rsh__t">Hear it from the doctor</b>'
           '<span class="rsh__m">Video &middot; Hindi and English</span></div></div>' % (esc(p['title']), max(1, round(p.get('words', 0) / 200))))
    hero = ('<header class="hb2-hero hb2-hero--s hb2-hero--rs"><div class="hb2-hero__in"><nav class="crumb" aria-label="Breadcrumb"><a href="%s">Home</a><span aria-hidden="true">/</span>'
            '<span aria-current="page">Resources</span></nav><h1>Resources</h1>'
            '<p>Articles, guides, answers and videos from Dr. Gorav Gupta, to help you make sense of mental health and addiction.</p>%s</div>%s</header>'
            % (root, facts, art))
    return hero + '<section class="sec hb-x2" aria-label="Explore resources"><ul class="hb-x2__g">%s</ul></section>' % explore_html


def articles_hub(root, posts, tests, href, pretty_date, tag_map=None):
    """The body of /blog/: a banner, a sidebar of categories, tags and quick links, a filterable and searchable article grid
    (assets/js/hub.js). Every article is in the HTML; hub.js filters, sorts and pages them in the browser."""
    tag_map = tag_map or {}

    taken = {}   # picture -> times used on this page, so a card takes the first picture of its subject that no card has yet

    def img(p):
        # a picture that matches the subject comes first; the post's own picture stays only where it already says exactly what the article is about
        text = (p['slug'] + ' ' + p['title']).lower().replace('-', ' ')
        for pat, pool in CARD_PHOTOS:
            if re.search(pat, text):
                if pool:
                    pick = min(pool, key=lambda n: (taken.get(n, 0), pool.index(n)))
                    taken[pick] = taken.get(pick, 0) + 1
                    return root + ((IMG + pick[5:] + '.webp') if pick.startswith('blog/') else (CARDS + pick + '.webp'))
                break
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

    hero = ('<header class="hb2-hero hb2-hero--s"><div class="hb2-hero__in"><nav class="crumb" aria-label="Breadcrumb"><a href="%s">Home</a><span aria-hidden="true">/</span>'
            '<a href="%sresources/">Resources</a><span aria-hidden="true">/</span><span aria-current="page">Articles &amp; Blogs</span></nav><h1>Mental Health &amp; Wellness Blog by Dr. Gorav Gupta</h1>'
            '<p>%d guides on mental health and addiction from Dr. Gorav Gupta, searchable by condition. '
            'Looking for an overview instead? Visit <a href="%sresources/">Resources</a>.</p></div></header>' % (root, root, len(posts), root))
    side = ('<div class="hb2-side" id="hb2-side" role="group" aria-label="Filter articles">'
            '<div class="hb2-box hb2-search"><label class="hb2-sr" for="hb2-q">Search articles</label><input id="hb2-q" type="search" placeholder="Search articles" autocomplete="off" spellcheck="false">%s</div>'
            '<div class="hb2-box hb2-catbox"><h2 class="hb2-k">Categories</h2><ul class="hb2-cats">%s</ul></div>'
            '<div class="hb2-box"><h2 class="hb2-k">Tags</h2><ul class="hb2-tags">%s</ul>'
            '<ul class="hb2-tags hb2-tags--more" id="hb2-tags-more" hidden>%s</ul>'
            '<button type="button" class="hb2-link" id="hb2-tagtog" aria-expanded="false" aria-controls="hb2-tags-more">Show all tags (%d)</button></div>'
            '<div class="hb2-box hb2-quick"><h2 class="hb2-k">Take a quick test</h2><ul>%s</ul><a class="hb2-link" href="%s%s/">All tests &rarr;</a></div></div>'
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
    return hero + '<section class="sec hb2" aria-label="Articles"><div class="hb2-layout">' + side + bar + main + '</div></section>'
