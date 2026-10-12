#!/usr/bin/env python3
"""One-off importer: the old WordPress site (goravgupta.com) -> this site's sources.

    python tools/import_wp.py [--cache DIR] [--refresh]

Reads   the public WordPress REST API (cached as JSON in --cache, default .wp-cache/)
Writes  src/content/pages/*.html   one source file per imported page
        src/content/posts/*.html   one source file per blog post
        assets/img/blog/*.webp     every image those pages use, resized to 1200px wide

The doctor's team supplied consent for this content to be carried over. Each source
file starts with a <!--meta {...}--> block (title, path, SEO title and description,
group, date) followed by a cleaned body: headings, paragraphs, lists, tables, images
and YouTube embeds only. Old forms, widgets and contact boilerplate are removed, FAQ
accordions become <details>, ALL-CAPS headings are sentence-cased, internal links point
at the new paths and images are localised. After the import the source files are the
source of truth: edit them, not the old site.
"""
import argparse
import html
import io
import json
import pathlib
import re
import sys
import urllib.parse
import urllib.request

from bs4 import BeautifulSoup, Comment, NavigableString
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
OLD = 'https://www.goravgupta.com'
UA = {'User-Agent': 'Mozilla/5.0 (migration; goravgupta.com)'}

# Pages that already exist as hand-designed pages in this project, or are not wanted.
SKIP_PAGES = {'home', 'about-us', 'services', 'publication', 'video-gallery', 'contactus', 'blog', 'video-gallery-draft'}

# Links the old site itself left broken (404): point them at the closest live page.
DEAD_LINK_FIXES = {
    'best-alcohol-addiction-treatment-centre-in-india': 'alcohol-addiction-treatment-india',
    'best-anxiety-treatment-in-delhi': 'anxiety-treatment-delhi',
    'bipolar-disorder': 'best-bipolar-disorder-psychiatrist-delhi-gurgaon',
    'de-addiction-treatment-delhi-india': 'psychiatrist-de-addiction-treatment-delhi-gurgaon',
    'depression-treatment-delhi-india': 'depression-psychiatrist-doctor-in-delhi-gurgaon',
}

# The doctor's own "N years of experience" claims across the old site disagree (20, 25, 28 and 30).
# The new site uses the client's figure, "40+ years of experience" (EXPERIENCE in tools/build_site.py),
# so claims about the doctor are reworded to match. Claims about other things are left alone.
YEARS_RULES = [
    (re.compile(r'\b(?:more than|over|around)\s+\d+\+?\s+years?\s+of\s+(?:experience|expertise)', re.I), '40+ years of experience'),
    (re.compile(r'\bfor\s+(?:more than\s+)?(?:the\s+)?(?:last\s+)?25\s+years', re.I), 'for 40+ years'),
    (re.compile(r'\bof\s+(?:more than|over|around)\s+\d+\+?\s+years?\s+of\s+practice', re.I), 'for 40+ years'),
]

# A line the old site printed above the page that is not in the page content itself.
SUBTITLES = {'psychiatrist-alcohol-deaddiction-treatment-delhi-gurgaon': 'Psychiatrist for Alcohol Addiction Treatment'}

# Which section each imported page belongs to (drives breadcrumb, nav state and hub lists).
MENTAL_HEALTH = {'mental-health-assessment-tests', 'early-warning-signs-scale-for-bipolar-disorder',
                 'early-relapse-signs-of-schizophrenia', 'substance-use-disorder', 'substance-use-disorder-vs-social-use'}
LOCAL = {'psychiatrist-in-delhi', 'psychiatrist-in-gurgaon', 'psychiatrist-in-india'}
STANDALONE = {'frequently-asked-questions-psychiatrist-near-me-consultation', 'ask-the-doctor'}

# Condition grouping for the Services hub (title shown, then slugs in display order).
CONDITION_GROUPS = [
    ('De-addiction and substance use', ['psychiatrist-de-addiction-treatment-delhi-gurgaon', 'psychiatrist-alcohol-deaddiction-treatment-delhi-gurgaon',
                                        'alcohol-addiction-treatment-india', 'smoking-cessation']),
    ('Schizophrenia', ['schizophrenia-psychiatrist-delhi-gurgaon-ncr']),
    ('Mood disorders', ['depression-psychiatrist-doctor-in-delhi-gurgaon', 'best-bipolar-disorder-psychiatrist-delhi-gurgaon']),
    ('Anxiety, OCD and stress', ['best-psychiatrist-anxiety-specialist-delhi-gurgaon', 'anxiety-treatment-delhi',
                                 'ocd-psychiatrist-in-gurgaon-delhi-ncr', 'stress-management-psychologist-counselling-delhi-gurgaon']),
    ('Personality disorders', ['personality-disorder-treatment-delhi-india', 'borderline-personality-disorder',
                               'narcissistic-personality-disorder', 'schizotypal-personality-disorder']),
    ('Eating disorders', ['eating-disorder-psychiatrist-delhi-gurgaon']),
]

ACRONYMS = {'OCD', 'TMS', 'CBT', 'DBT', 'ADHD', 'NCR', 'PTSD', 'MD', 'ECT', 'BPD', 'NPD', 'OPD', 'UK', 'USA', 'MBBS', 'IAPP', 'FAQ', 'FAQS', 'AIIMS', 'PTSD.', 'COVID', 'GAD', 'MDD', 'ICD', 'DSM', 'CUD', 'SUD', 'NGO', 'HIV', 'AIDS'}

# Text that is old-site furniture, not content: dropped wherever it appears as a whole block.
BOILERPLATE = {
    'contact & reach us', 'have any queries', 'head office address:', 'call for help:', 'mail for information:',
    '2/6 sarvapriya vihar, new delhi-110016.', '+91-8800000255', 'drgoravgupta@tulasihealthcare.com',
    'goravgupta@tulasihealthcare.com', 'your name', 'your email', 'phone', 'your message (optional)', 'submit', 'book appointment',
    'holistic treatment of anxiety and stress',
}


def get_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(io.TextIOWrapper(r, encoding='utf-8'))


def load(cache, refresh):
    cache.mkdir(parents=True, exist_ok=True)
    out = {}
    for kind in ('pages', 'posts'):
        f = cache / (kind + '.json')
        if refresh or not f.exists():
            fields = 'id,slug,link,title,date,modified,status,content,excerpt,yoast_head_json'
            data = get_json('%s/wp-json/wp/v2/%s?per_page=100&status=publish&_fields=%s' % (OLD, kind, fields))
            f.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        out[kind] = json.loads(f.read_text(encoding='utf-8'))
    return out


def clean_text(s):
    s = html.unescape(s or '')
    s = s.replace('�', '').replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', s).strip()


def sentence_case_caps(text):
    """ALL-CAPS heading -> readable case, keeping known acronyms."""
    letters = re.sub(r'[^A-Za-z]', '', text)
    if len(letters) < 5 or letters != letters.upper():
        return text
    words = []
    for w in text.split(' '):
        bare = w.strip('.,:;()')
        if w.upper() == 'DR.':
            words.append('Dr.')
        elif bare.upper() in ACRONYMS or w.upper() in ACRONYMS:
            words.append(w)
        elif w.upper() == w and len(re.sub(r'[^A-Za-z]', '', w)) > 0:
            words.append(w[:1] + w[1:].lower())
        else:
            words.append(w)
    return ' '.join(words)


class Importer:
    def __init__(self, data):
        self.pages = {p['slug']: p for p in data['pages']}
        self.posts = {urllib.parse.unquote(p['slug']): p for p in data['posts']}
        self.images = {}
        self.adapted = []
        self.unmapped = set()
        self.slug_paths = {}
        for s in self.pages:
            if s not in SKIP_PAGES or s in ('about-us', 'services', 'publication', 'video-gallery', 'contactus', 'blog'):
                self.slug_paths[s] = s + '/'
        self.slug_paths['home'] = ''
        for s in self.posts:
            self.slug_paths[s] = 'blog/' + urllib.parse.quote(s) + '/'

    # ---- links -------------------------------------------------------------
    def map_link(self, href):
        u = urllib.parse.urlsplit(href)
        if u.netloc and 'goravgupta.com' not in u.netloc:
            return href, True
        path = urllib.parse.unquote(u.path).strip('/')
        if not u.netloc and not path and not href.startswith('/'):
            return href, False
        if '/wp-content/' in '/' + path:
            return href, True
        if path == '':
            return '{{root}}' + ('#' + u.fragment if u.fragment else ''), False
        parts = path.split('/')
        if parts[0] in ('tag', 'category', 'author') or (parts[0] == 'blog' and len(parts) == 1):
            return '{{root}}blog/', False
        slug = DEAD_LINK_FIXES.get(parts[-1], parts[-1])
        if slug in self.slug_paths:
            return '{{root}}' + self.slug_paths[slug] + ('#' + u.fragment if u.fragment else ''), False
        self.unmapped.add(href)
        return href, True

    # ---- images ------------------------------------------------------------
    def localise_image(self, src, out_dir):
        src = src.split('?')[0]
        if src in self.images:
            return self.images[src]
        name = re.sub(r'[^A-Za-z0-9._-]+', '-', urllib.parse.unquote(src.rsplit('/', 1)[-1]).rsplit('.', 1)[0]).strip('-').lower() or 'image'
        dest = out_dir / (name + '.webp')
        n = 2
        while dest.exists() and self.images.get('__' + dest.name) not in (None, src):
            dest = out_dir / ('%s-%d.webp' % (name, n)); n += 1
        if not dest.exists():
            req = urllib.request.Request(src, headers=UA)
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read()
            im = Image.open(io.BytesIO(raw))
            im.load()
            if im.mode not in ('RGB', 'RGBA'):
                im = im.convert('RGBA' if 'transparency' in im.info or im.mode in ('LA', 'P') else 'RGB')
            if im.width > 1200:
                im = im.resize((1200, round(im.height * 1200 / im.width)), Image.LANCZOS)
            im.save(dest, 'WEBP', quality=82, method=6)
        with Image.open(dest) as im:
            w, h = im.size
        self.images['__' + dest.name] = src
        self.images[src] = (dest.name, w, h)
        return self.images[src]

    # ---- body --------------------------------------------------------------
    def home_faq_extra(self, pages_by_slug, existing_body, img_dir):
        """The old home page carried its own FAQ. Add its questions to the FAQ page (skipping repeats)."""
        home = self.body(pages_by_slug['home']['content']['rendered'], 'Home', img_dir)
        soup = BeautifulSoup(home, 'lxml')
        have = {clean_text(m).lower() for m in re.findall(r'<summary>(.*?)</summary>', existing_body, re.S)}
        keep = [d for d in soup.find_all('details') if clean_text(d.summary.get_text()).lower() not in have]
        if not keep:
            return ''
        return '<h2>More frequently asked questions</h2>' + ''.join(str(d) for d in keep)

    def body(self, raw, title, img_dir):
        soup = BeautifulSoup(raw, 'lxml')
        root = soup.body or soup
        for el in root.find_all(string=lambda t: isinstance(t, Comment)):
            el.extract()
        for t in root.find_all(['script', 'style', 'noscript', 'form', 'input', 'select', 'textarea', 'button', 'svg', 'link', 'meta', 'option', 'label']):
            t.decompose()

        # FAQ accordions -> <details>
        for tab in root.select('[role="tab"]'):
            q = clean_text(tab.get_text(' '))
            panel_body = tab.find_next_sibling('div')
            parent = tab.parent
            if not q or panel_body is None:
                continue
            d = soup.new_tag('details')
            d['class'] = 'qa'
            s = soup.new_tag('summary'); s.string = q
            d.append(s)
            inner = soup.new_tag('div')
            for child in list(panel_body.children):
                inner.append(child.extract())
            d.append(inner)
            parent.replace_with(d)

        # YouTube embeds -> lazy, privacy-friendly player
        for fr in root.find_all('iframe'):
            m = re.search(r'youtube(?:-nocookie)?\.com/embed/([\w-]+)', fr.get('src', ''))
            if not m:
                fr.decompose(); continue
            wrap = soup.new_tag('div'); wrap['class'] = 'video'
            f2 = soup.new_tag('iframe', src='https://www.youtube-nocookie.com/embed/' + m.group(1), title=clean_text(fr.get('title', '')) or 'Video from Dr. Gorav Gupta',
                              loading='lazy', allowfullscreen='')
            f2['referrerpolicy'] = 'strict-origin-when-cross-origin'
            wrap.append(f2)
            host = fr.find_parent('figure') or fr
            host.replace_with(wrap)

        # images -> local webp
        for img in root.find_all('img'):
            src = img.get('src') or img.get('data-src') or ''
            if not src.startswith('http') or 'goravgupta.com' not in src:
                img.decompose(); continue
            try:
                name, w, h = self.localise_image(src, img_dir)
            except Exception as e:
                print('  ! image failed', src, e, file=sys.stderr); img.decompose(); continue
            alt = clean_text(img.get('alt', ''))
            img.attrs = {'src': '{{root}}assets/img/blog/' + name, 'alt': alt, 'width': str(w), 'height': str(h), 'loading': 'lazy', 'decoding': 'async'}
            a = img.find_parent('a')
            if a and a.get('href', '').split('?')[0].lower().endswith(('.webp', '.jpg', '.jpeg', '.png')):
                a.unwrap()

        # links
        for a in root.find_all('a'):
            href = a.get('href', '')
            if not href or href.startswith(('javascript:', '#')) and href == '#':
                a.unwrap(); continue
            if href.startswith('tel:'):
                digits = re.sub(r'\D', '', href)
                if len(digits) in (10, 12) and not href.startswith('tel:http'):
                    a.attrs = {'href': 'tel:+91' + digits[-10:]}
                else:
                    a.unwrap()          # a leftover template placeholder number
                continue
            new, external = self.map_link(href)
            keep = {'href': new}
            if external and new.startswith('http'):
                keep.update({'target': '_blank', 'rel': 'noopener'})
            a.attrs = keep

        # structure: drop wrappers, keep content tags
        for t in root.find_all(['div', 'section', 'article', 'header', 'footer', 'main', 'aside', 'span', 'font', 'center', 'small', 'u', 'mark', 'abbr', 'cite', 'time', 'nav', 'fieldset']):
            if t.name == 'div' and ('video' in t.get('class', []) or 'tbl' in t.get('class', [])):
                continue
            t.unwrap()
        for b in root.find_all('b'):
            b.name = 'strong'
        for i_ in root.find_all('i'):
            i_.name = 'em'

        # long text set as h5/h6 is a paragraph
        for h in root.find_all(['h5', 'h6']):
            h.name = 'p' if len(clean_text(h.get_text())) > 90 else 'h4'

        # attributes
        allowed = {'a': {'href', 'target', 'rel'}, 'img': {'src', 'alt', 'width', 'height', 'loading', 'decoding'}, 'td': {'colspan', 'rowspan'}, 'th': {'colspan', 'rowspan', 'scope'},
                   'iframe': {'src', 'title', 'loading', 'allowfullscreen', 'referrerpolicy'}, 'div': {'class'}, 'details': {'class'}, 'ol': {'start'}}
        for t in root.find_all(True):
            keep = allowed.get(t.name, set())
            t.attrs = {k: v for k, v in t.attrs.items() if k in keep}

        # stray top-level text -> paragraphs
        for node in list(root.children):
            if isinstance(node, NavigableString) and clean_text(str(node)):
                p = soup.new_tag('p'); p.string = clean_text(str(node)); node.replace_with(p)

        # tables scroll on small screens
        for tb in root.find_all('table'):
            if not (tb.parent and 'tbl' in tb.parent.get('class', [])):
                w = soup.new_tag('div'); w['class'] = 'tbl'; tb.wrap(w)

        # boilerplate and duplicates
        tnorm = clean_text(title).lower()
        for t in root.find_all(['p', 'li', 'h2', 'h3', 'h4', 'h1']):
            tx = clean_text(t.get_text()).lower()
            if tx in BOILERPLATE or (t.name.startswith('h') and tx == tnorm):
                t.decompose()

        # a heading that only restates the page title, before any text, is redundant under the H1
        first = root.find(['p', 'ul', 'ol', 'h2', 'h3', 'h4', 'details', 'figure', 'div'])
        if first is not None and first.name in ('h2', 'h3', 'h4'):
            ft = clean_text(first.get_text()).lower()
            if ft and (ft in tnorm or tnorm in ft):
                first.decompose()

        # headings: smallest level present becomes h2, others follow in order, capped at h4
        levels = sorted({int(h.name[1]) for h in root.find_all(['h1', 'h2', 'h3', 'h4'])})
        remap = {lv: min(2 + i, 4) for i, lv in enumerate(levels)}
        for h in root.find_all(['h1', 'h2', 'h3', 'h4']):
            h.name = 'h%d' % remap[int(h.name[1])]
            txt = clean_text(h.get_text())
            if txt.lower() in ('faqs', 'faq', 'faq\'s'):
                h.string = 'Frequently asked questions'
            elif h.find(True) is None or True:
                fixed = sentence_case_caps(txt)
                if fixed != txt and not h.find('a'):
                    h.string = fixed
            for strong in h.find_all('strong'):
                strong.unwrap()

        # the old site sometimes repeated a whole question and answer: keep the first
        seen = set()
        for h in root.find_all(['h2', 'h3', 'h4']):
            nxt = h.find_next_sibling()
            key = (clean_text(h.get_text()).lower(), clean_text(nxt.get_text()).lower() if nxt is not None and nxt.name in ('p', 'ul', 'ol') else '')
            if key[1] and key in seen:
                nxt.decompose(); h.decompose()
            else:
                seen.add(key)

        # empties, repeatedly (unwrapping can expose new ones)
        for _ in range(4):
            for t in root.find_all(['p', 'li', 'h2', 'h3', 'h4', 'strong', 'em', 'a', 'ul', 'ol', 'div', 'details', 'td', 'th', 'tr', 'table', 'blockquote']):
                if t.name in ('div', 'a') and (t.find('img') or t.find('iframe')):
                    continue
                if not clean_text(t.get_text()) and not t.find(['img', 'iframe']):
                    t.decompose()
        for br in root.find_all('br'):
            nxt = br.next_sibling
            prev = br.previous_sibling
            if (prev is None and br.parent.name == 'p') or (nxt is None and br.parent.name == 'p'):
                br.decompose()

        out = root.decode_contents().replace('&nbsp;', ' ').replace(' ', ' ')
        for rx, new in YEARS_RULES:
            def repl(m, rx=rx, new=new):
                self.adapted.append((title, m.group(0), new))
                return new
            out = rx.sub(repl, out)
        out = re.sub(r'>\s+<', '><', out)
        out = re.sub(r'\s{2,}', ' ', out).strip()
        # collapse leftovers such as consecutive duplicate headings
        return out


def trim_words(text, limit):
    """Cut text at a whole word, with an ellipsis, so a summary never ends mid-word."""
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit]
    cut = cut[:cut.rfind(' ')] if ' ' in cut else cut
    return cut.rstrip(' -,;:.') + '…'


def words(html_body):
    return len(re.sub(r'<[^>]+>', ' ', html_body).split())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cache', default=str(ROOT / '.wp-cache'))
    ap.add_argument('--refresh', action='store_true')
    args = ap.parse_args()

    data = load(pathlib.Path(args.cache), args.refresh)
    imp = Importer(data)
    img_dir = ROOT / 'assets' / 'img' / 'blog'
    img_dir.mkdir(parents=True, exist_ok=True)
    out_pages = ROOT / 'src' / 'content' / 'pages'
    out_posts = ROOT / 'src' / 'content' / 'posts'
    out_pages.mkdir(parents=True, exist_ok=True)
    out_posts.mkdir(parents=True, exist_ok=True)

    def group_of(slug):
        if slug in MENTAL_HEALTH:
            return 'mental-health'
        if slug in LOCAL:
            return 'local'
        if slug in STANDALONE:
            return 'standalone'
        return 'services'

    pages_by_slug = {p['slug']: p for p in data['pages']}
    n_pages = n_posts = 0
    for p in data['pages']:
        slug = p['slug']
        if slug in SKIP_PAGES:
            continue
        title = clean_text(p['title']['rendered'])
        body = imp.body(p['content']['rendered'], title, img_dir)
        yo = p.get('yoast_head_json') or {}
        if slug == 'frequently-asked-questions-psychiatrist-near-me-consultation':
            body += imp.home_faq_extra(pages_by_slug, body, img_dir)
        meta = {'kind': 'page', 'slug': slug, 'path': slug, 'title': title, 'group': group_of(slug),
                'seo_title': clean_text(yo.get('title', '')) or title, 'description': clean_text(yo.get('description', '')) or clean_text(re.sub(r'<[^>]+>', ' ', p['excerpt']['rendered']))[:160],
                'modified': p['modified'][:10], 'words': words(body)}
        if slug in SUBTITLES:
            meta['subtitle'] = SUBTITLES[slug]
        (out_pages / (slug + '.html')).write_text('<!--meta\n%s\n-->\n%s\n' % (json.dumps(meta, ensure_ascii=False, indent=1), body), encoding='utf-8', newline='\n')
        n_pages += 1

    for p in data['posts']:
        slug = urllib.parse.unquote(p['slug'])
        title = clean_text(p['title']['rendered'])
        body = imp.body(p['content']['rendered'], title, img_dir)
        yo = p.get('yoast_head_json') or {}
        plain = re.sub(r'<[^>]+>', ' ', body)
        deva = len(re.findall(r'[ऀ-ॿ]', plain))
        # the old excerpts end mid-word, so build one from the post itself, cut at a whole word
        paras = [clean_text(re.sub(r'<[^>]+>', ' ', x)) for x in re.findall(r'<p>(.*?)</p>', body, re.S)]
        lead = next((x for x in paras if len(x) >= 60), '') or clean_text(plain)
        excerpt = trim_words(lead, 200)
        ascii_slug = re.sub(r'[^a-z0-9-]+', '-', slug.lower()).strip('-')
        fname = ('%s.html' % ascii_slug) if ascii_slug and len(ascii_slug) > 5 else 'post-%d.html' % p['id']
        meta = {'kind': 'post', 'slug': slug, 'path': 'blog/' + slug, 'title': title, 'group': 'blog', 'date': p['date'][:10], 'modified': p['modified'][:10],
                'seo_title': clean_text(yo.get('title', '')) or title, 'description': clean_text(yo.get('description', '')) or trim_words(excerpt, 160),
                'excerpt': excerpt, 'words': words(body)}
        if deva > 0.3 * max(1, len(re.sub(r'\s', '', plain))):
            meta['lang'] = 'hi'
        (out_posts / fname).write_text('<!--meta\n%s\n-->\n%s\n' % (json.dumps(meta, ensure_ascii=False, indent=1), body), encoding='utf-8', newline='\n')
        n_posts += 1

    notes = ['# Wording adapted during the WordPress import', '',
             "The old site gave the doctor's years of experience as 20, 25, 28 and 30 in different places. Claims about the doctor were reworded to",
             '"40+ years" to match the rest of this site (`EXPERIENCE` in `tools/build_site.py`). Nothing else was reworded.', '',
             '| Page or post | Original | Now |', '| --- | --- | --- |']
    for t, a, b in imp.adapted:
        notes.append('| %s | %s | %s |' % (t.replace('|', '/'), a.replace('|', '/'), b))
    (ROOT / 'docs').mkdir(exist_ok=True)
    (ROOT / 'docs' / 'migration-adaptations.md').write_text('\n'.join(notes) + '\n', encoding='utf-8', newline='\n')
    groups = {'condition_groups': CONDITION_GROUPS}
    (ROOT / 'src' / 'content' / 'groups.json').write_text(json.dumps(groups, ensure_ascii=False, indent=1), encoding='utf-8', newline='\n')
    print('pages: %d  posts: %d  images: %d' % (n_pages, n_posts, sum(1 for k in imp.images if not k.startswith('__'))))
    if imp.unmapped:
        print('internal links that point nowhere on the new site (left as absolute old URLs):')
        for u in sorted(imp.unmapped):
            print('  ', u)


if __name__ == '__main__':
    main()
