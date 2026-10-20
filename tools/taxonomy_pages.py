"""Tag, category and author archives, so every URL the WordPress site had still exists: /tag/<slug>/, /category/blog/ and
/author/<slug>/. Built from data/taxonomy.json (which post is in which archive, copied from the old site's archive pages) by
tools/build_site.py. Each archive is one compact list of posts. Posts also show their tags at the foot, linking here.
"""
import json
import pathlib
import re

DATA = pathlib.Path(__file__).resolve().parent.parent / 'data' / 'taxonomy.json'
AUTHOR_NAME = {'goravgupta': 'Dr. Gorav Gupta', 'admin': 'admin'}

# Archives that are 301'd in vercel.json instead of being served: the seven tags that drew large
# impressions and almost no clicks (they go to the page that answers the search), the WordPress
# "admin" author archive and the /category/blog/ archive. No page is built, and nothing links to them.
REDIRECTED_TAGS = {'best-psychiatrist-in-delhi', 'top-psychiatrist-in-delhi', 'ocd-psychiatrist',
                   'addiction-disorder', 'drug-psychiatrist', 'psychiatrist', 'psychiatrist-near-me'}
REDIRECTED_AUTHORS = {'admin'}
REDIRECTED_CATEGORIES = {'blog'}


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def load():
    return json.loads(DATA.read_text(encoding='utf-8')) if DATA.exists() else {'tags': {}, 'authors': {}, 'category': {}}


def items(tax):
    """Page records for build_site.py's render loop."""
    out = []
    for slug, t in tax['tags'].items():
        if slug in REDIRECTED_TAGS:
            continue
        # Tag archives carry large impressions and almost no clicks, and they compete with the service
        # pages for the same searches, so they stay crawlable but out of the index and the sitemap.
        out.append({'kind': 'tax', 'path': 'tag/' + slug, 'nav': 'resources', 'crumb': t['name'], 'tax': 'tag', 'name': t['name'], 'posts': t['posts'],
                    'noindex': True,
                    'title': 'Posts tagged “%s” | Dr. Gorav Gupta' % t['name'],
                    'description': 'Articles by Dr. Gorav Gupta on %s: %d %s on mental health, addiction and treatment.' % (t['name'], len(t['posts']), 'article' if len(t['posts']) == 1 else 'articles')})
    for slug, c in tax['category'].items():
        if slug in REDIRECTED_CATEGORIES:
            continue
        out.append({'kind': 'tax', 'path': 'category/' + slug, 'nav': 'resources', 'crumb': c['name'], 'tax': 'category', 'name': c['name'], 'posts': c['posts'],
                    'title': '%s articles | Dr. Gorav Gupta' % c['name'],
                    'description': 'Every article in the Blog category: mental health, addiction, anxiety, depression, OCD and treatment, by Dr. Gorav Gupta.'})
    for slug, a in tax['authors'].items():
        if slug in REDIRECTED_AUTHORS:
            continue
        name = AUTHOR_NAME.get(slug, a['name'])
        out.append({'kind': 'tax', 'path': 'author/' + slug, 'nav': 'resources', 'crumb': name, 'tax': 'author', 'name': name, 'posts': a['posts'],
                    'title': 'Articles by %s | Dr. Gorav Gupta' % name,
                    'description': 'Every article written by %s: mental health, addiction, anxiety, depression, OCD and treatment.' % name})
    return out


def tags_of(tax):
    """post slug -> [(tag slug, tag name)], in tag-name order"""
    m = {}
    for slug, t in sorted(tax['tags'].items(), key=lambda kv: kv[1]['name'].lower()):
        if slug in REDIRECTED_TAGS:
            continue
        for p in t['posts']:
            m.setdefault(p, []).append((slug, t['name']))
    return m


def tag_row(root, post_slug, tmap):
    tags = tmap.get(post_slug)
    if not tags:
        return ''
    return ('<nav class="ptags" aria-label="Tags"><span class="ptags__k">Tags</span><ul>%s</ul></nav>'
            % ''.join('<li><a href="%stag/%s/">%s</a></li>' % (root, s, esc(n)) for s, n in tags))


def body(pg, root, ph, by_slug, href, pretty_date):
    posts = [by_slug[s] for s in pg['posts'] if s in by_slug]
    posts.sort(key=lambda p: (p['date'], p['slug']), reverse=True)
    label = {'tag': 'Tag', 'category': 'Category', 'author': 'Author'}[pg['tax']]
    lede = {'tag': '%d %s tagged &ldquo;%s&rdquo;.' % (len(posts), 'article' if len(posts) == 1 else 'articles', esc(pg['name'])),
            'category': 'Every article in the blog, newest first.',
            'author': '%d %s by %s.' % (len(posts), 'article' if len(posts) == 1 else 'articles', esc(pg['name']))}[pg['tax']]
    h1 = esc(pg['name']) if pg['tax'] != 'author' else 'Articles by %s' % esc(pg['name'])
    crumbs = [('Home', root), ('Blog', root + 'blog/'), ('%s: %s' % (label, esc(pg['name'])), None)]
    lst = ''.join('<li><a href="%s"><time datetime="%s">%s</time><b>%s</b></a></li>' % (href(p, root), p['date'], pretty_date(p['date']), p['title']) for p in posts)
    return (ph(crumbs, h1, lede)
            + '<section class="sec tax" aria-label="Articles"><ul class="idx idx--posts">%s</ul>'
              '<p class="more"><a class="more__a" href="%sblog/">All articles <i>&rarr;</i></a></p></section>' % (lst, root))
