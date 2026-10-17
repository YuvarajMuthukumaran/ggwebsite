# URL rules at cutover

Every rule lives in [`vercel.json`](../vercel.json). The principle behind all of them: the live
WordPress site earns about 15,500 clicks a month across 228 URLs, so a URL may change what it shows,
but it may not stop resolving.

## The host

Search Console records the live site on `www.goravgupta.com`. The build now writes that host into
every canonical, Open Graph URL, structured-data URL and sitemap entry (`SITE` in
`tools/build_site.py`), `robots.txt` points at the www sitemap, and one 301 sends the bare host to
www. Launching on the bare host would have told Google the whole site had moved during a redesign.

`"trailingSlash": true` is the single rule that settles `/psychiatrist-in-gurgaon` against
`/psychiatrist-in-gurgaon/`. Vercel answers that one with a 308 rather than a 301; both pass full
ranking signal, and the status is not configurable for this rule.

## The two hubs moved to the URLs that carry the traffic

| Hub | Served at | 301 from |
| --- | --- | --- |
| Interactive tests | `/mental-health-assessment-tests/` (306 clicks) | `/tests/` |
| FAQ | `/frequently-asked-questions-psychiatrist-near-me-consultation/` (284 clicks) | `/faq/` |

The old imported page at each of those URLs is retired (see below) and the new hub is served there
instead. **Their child pages keep their own paths** — `/tests/<slug>/` and `/faq/<topic>/`. Those are
new URLs with no search history, so moving them would only have added redirects. The redirects are
exact-match on the parent, so the children are untouched.

## Retired pages

A page with `"retired"` in its `<!--meta>` block stays in `src/` as a source but is not built; the
value says why. The build prints them on every run. Nothing links to one: internal links were
repointed to the destination, so no internal link passes through a redirect.

- `mental-health-assessment-tests`, `frequently-asked-questions-psychiatrist-near-me-consultation` —
  the new hubs are served at these URLs
- `anxiety-treatment-delhi` → `best-psychiatrist-anxiety-specialist-delhi-gurgaon`
- `alcohol-addiction-treatment-india` → `psychiatrist-alcohol-deaddiction-treatment-delhi-gurgaon`

## Tag, category and author archives

The 88 tag archives drew large impressions and almost no clicks, and competed with the service pages
for the same searches. The seven strongest are 301'd to the page that answers the search; the other
81 are built as `noindex,follow` and dropped from the sitemap. `/category/blog/*` goes to
`/resources/` and `/author/admin/*` to `/about-us/`; neither is built any more.

`REDIRECTED_TAGS` in `tools/taxonomy_pages.py` holds the seven. A tag that is redirected is also
dropped from the tag rows at the foot of posts, so nothing links into a redirect.

## Still open

**`/wp-content/uploads/*` is done for the images the new site uses.** The old media library was read from the live site (`/wp-json/wp/v2/media`, 230 items, 1,651 URLs including the resized copies) and each URL was mapped to its new file the way the importer names them (lowercased basename, runs of non-alphanumerics become `-`, `.webp`). 427 URLs map to a file the new site has, and each is a 301 in `vercel.json`, resized copies included. The other 1,224 are images the new site no longer uses, and they are not redirected.

**`/blog/page/*` must not be redirected.** The review groups it with the WordPress archive paths and
sends it to `/resources/`, but this build uses `/blog/page/2/` … `/blog/page/9/` for the blog's own
pagination. Redirecting it would remove the blog's paging. Pages 2 and up are already `noindex`, so
the duplicate-content concern behind the item is handled. Raise with Niki before changing.

## Stale output removed

Two Hindi posts had three directories each — the correct Devanagari path plus two committed under
mangled encodings (`#U0913…` and a double-encoded form). All four junk copies served stale duplicates
at URLs no one links to, and only the correct paths are refreshed by the build, so they were removed.
The Hindi slugs themselves are unchanged: `/blog/ओसीडी-से-छुटकारा/` still resolves, and it ranks at
position 8.
