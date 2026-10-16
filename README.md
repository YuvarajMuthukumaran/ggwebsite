# Dr. Gorav Gupta — personal flagship site

A single-page editorial site replacing the previous template build at
goravgupta.com. No framework, no build step: open `index.html`.

```bash
npx serve -l 4173 .
```

## Structure

```
index.html                     markup + content
assets/css/main.css            design system and every section
assets/js/main.js              motion layer (Lenis + GSAP ScrollTrigger)
assets/img/*.webp              graded portrait derivatives
assets/img/_source/            the untouched original photograph
tools/process-portraits.py     regenerates every image from that source
```

Dependencies are three pinned CDN scripts (GSAP 3.12.5, ScrollTrigger, Lenis
1.0.42). Nothing else. Fonts are Fraunces (display) and Instrument Sans (UI).

## Design system

| Token | Value | Use |
| --- | --- | --- |
| `--canvas` | `#EDF1EC` | soft mist page |
| `--ink` | `#14262A` | deep teal-slate text, dark sections |
| `--accent` | `#2F7A73` | the only accent: rules, indices, hovers (`--accent-2` `#86C4B8` on dark) |
| `--canvas-2` | `#E0E9E3` | pale sage, hover fills and the support band |

Calm, desaturated greens and teals instead of the earlier deep teal/bronze.
Hierarchy is still carried by type scale, hairlines and whitespace.

## Mental-healthcare additions

- **Breathing orb** (`.calm`): a slow 10-second in/out animation beside a
  support band. Respects `prefers-reduced-motion`.
- **Talk-to-us band** pointing to Tulasi Healthcare on +91 88000 00255, with the
  same number in the footer note.
- **"Before you come in" FAQ**: native `<details>`, no JS. Answers only restate
  what the site already says; nothing new is claimed about the practice.
- Softer section titles ("A steady hand", "What he treats").

## Photography

Three supplied photographs live in `assets/img/_source/`, each used once:

- `portrait-office.webp` (consulting room) drives the hero column.
- `portrait-outdoor.webp` (garden) drives the pinned reveal band.
- `portrait-formal.webp` (studio) drives the About crop.

All photographs are shown in natural colour (no black-and-white or duotone).
`tools/process-portraits.py` regenerates the three files; swap a source,
adjust the crop boxes at the bottom of that script, and re-run it.

## The five set pieces

1. **Opening** — counter, name rising through a mask, accent rule drawing, then
   a clip-path wipe. The hero is hidden before the wipe starts and rises while
   the panel is still lifting; a reload always scrolls back to the top so the
   intro replays cleanly.
2. **Pinned portrait** — a tall crop widens to full frame on scroll while
   "UNDERSTAND / YOUR MIND" parts outward.
   Driven by `clip-path`, so it composites rather than re-laying out.
3. **Expertise** — seven domains; hover or focus swaps the panel. Real tabs
   with `aria-selected` and arrow-key navigation.
4. **Philosophy** — his own sentence, each word igniting from 14% to full as
   you scrub past it.
5. **Appointment** — a magnetic circular CTA with spring return.

## Robustness

Nothing decorative is allowed to gate the content:

- **No JS** — a `<noscript>` block removes the opening panel, unlocks scroll
  and resolves every masked element.
- **Stalled ticker** — if the rAF ticker is throttled (hidden tab, backgrounded
  window), a 6s failsafe tears the opening panel down and applies final states
  directly. Without it a visitor could sit on a blank ivory screen.
- **`prefers-reduced-motion`** — the intro is skipped, the pinned section
  unpins into normal flow, and every masked element resolves. The design
  survives intact; only the movement goes.
- Mobile is composed, not compressed: a stacked hero with a full-bleed
  portrait band, a fullscreen menu, and a sticky booking dock.

## Content provenance

Everything is taken from goravgupta.com. **No credentials were invented.** The
philosophy quotation is verbatim. Nothing from the old site's leftover template
placeholders (a San Francisco address, `+1 987 123456`, `yourmail@email.com`)
was carried over.

Three things need your decision:

1. **Years in practice — confirmed as 40+ by the client (superseded in v11: now "since 1997").** The site then said
   "40+ years" / "four decades" throughout. Note this is higher than any figure
   on the old site, which stated 25+, 28 and 30 in three different places, and
   higher than directory listings implying an MD in 1997. Worth making sure the
   old site and directory profiles are updated to match, so the number is
   consistent wherever someone checks it.
2. **Press links.** The publications page lists the outlets but I could not
   resolve stable article URLs, so all four press items currently point at
   `goravgupta.com/publication/`. Send the real URLs and they will go straight in.
3. **Timeline dates.** Directory sites list MBBS 1993 / MD 1997, but his own
   site gives no dates, so the journey section uses named chapters
   (Foundation, Specialism, Tulasi, Beyond, 2024) rather than years I could not
   verify. Confirm the dates and it becomes a dated timeline.

The footer carries a plain-language disclaimer that the site is not medical
advice, plus an emergency note.

## v4 — blue palette and card components

The live files are `assets/css/site.css` and `assets/js/site.js` (the structure
list above predates them).

**Palette.** The sage and teal tokens are now blue. Token names changed with them.

| Token | Value | Use |
| --- | --- | --- |
| `--blue` | `#2F6FCB` | buttons, links, accents |
| `--blue-d` | `#1F4F9A` | deep blue for headings on tint, gradient ends |
| `--tint` / `--tint2` | `#E9F1FB` / `#D3E3F6` | pale blue fills and the "Coming in" band |
| `--ink` / `--mut` | `#13243A` / `#586B82` | text |
| `--navy` | `#0E2340` | announcement bar and footer |

**"Coming in" (`#pathway`)** is now a row of four expanding cards (`.stages`,
`.stg`). Click, focus or hover opens one; on phones they stack. Step text is
unchanged. Photos: `tile-office.webp` (Consultation) and `tile-garden.webp`
(Continued care), both cropped from `_source/`.

**"By the numbers"** is now a three-column tile mosaic (`.mos`, `.mt`): photo
tile, years-in-practice dial, stacked areas of care, online/consulting rooms,
countries globe, and the award tile. Every figure and name is taken from the
previous bento tiles and the About section.

**Fix.** A variable name clash in `site.js` made the scroll handler throw on
every scroll, so the progress bar and the nav shadow never updated. The hero
counter now uses its own variable. The nav "Journey" link now has a target
(`#journey`).

## v5 — UI fixes

All fixes are in the last block of `assets/css/site.css` ("v4.1 fixes").

- Nav switched to the menu button at 1000px (was 900px). Between 901 and about
  930px the brand name and the Book Consultation button wrapped onto two lines.
- Menu button now turns into a cross when open and reports `aria-expanded`.
- Portrait: replaced the boxy side-and-bottom fade with an oval fade, so the
  shoulders no longer end in hard vertical edges.
- "Coming in" cards: collapsed titles ("Consultation") no longer clip between
  901 and 1180px.
- "By the numbers": explicit 3, 2 and 1 column layouts. Before, the third column
  dropped below the others at tablet widths and left a large gap. Columns now end
  level, and the tiles no longer collapse on phones.
- Keyboard focus ring on links, buttons and FAQ rows; headings balance their
  line breaks (no more "Before you come / in").


## v6 — cinematic motion layer

No copy, credentials, palette or layout was changed. This version adds motion and
depth on top of v5. It is still dependency-free: no GSAP, no Lenis, no build step.

**Files.** `assets/css/cinematic.css` (new, loads after `site.css`) and a rewritten,
readable `assets/js/site.js`. `site.css` lost only two rules that clashed with the
split lettering (`.giant span`, `@keyframes nameIn`). `tools/build.py` is a leftover
from the legacy build. Do not run it: it regenerates an old `index.html` and would
overwrite this one.

**Set pieces**

1. **Opening** — a breathing-orb loader, then a curtain that lifts with a curved
   edge while the name rises letter by letter through a mask and the portrait
   resolves from blur. About 2.5s. Waits for fonts and the portrait (3.5s cap),
   click to skip, skipped entirely on deep links and restored scroll positions.
2. **Hero depth** — pointer parallax on name, portrait and floating chips, with
   eased follow and a soft light that tracks the cursor. On scroll the hero
   recedes (scales, rounds, fades) as the page rises.
3. **Pinned philosophy scene** — the sentence is lit word by word as you scroll,
   over a slow-moving glow, inside a panel that scales in. The screen-reader text
   is the full sentence.
4. **Journey** — the timeline line draws itself and each chapter's dot lights as
   you pass it.
5. **"By the numbers"** — tiles are alive: radar sweep with pulses, a turning globe
   with floating country labels, chips that stack in.
6. **"Coming in"** — cards unfold with the content sliding in, and the photo settles.

**Micro-interactions.** Headings rise word by word through a mask. Images open like
a curtain and drift with scroll. Cards get a cursor spotlight and a slight tilt.
Buttons are magnetic with a light sweep. The nav has a pill that glides between
links. In-page links use an eased glide. The FAQ opens and closes smoothly. The
press carousel can be dragged with a mouse. The footer carries a large wordmark. The
breathing orb says "Breathe in / Breathe out" in step with its 10-second cycle.

**Other fixes.** Revealed cards now switch to quick hover transitions (before, hover
inherited the slow reveal delay). Collapsed stage titles no longer break mid-word.

**Robustness**

- **Reduced motion** — the head script never adds `html.js`, so visitors get the
  complete, static page: no curtain, no pinned scroll, the whole quote visible.
- **No JS** — the same static page. Before v6, a JS failure left every revealed
  section invisible.
- **JS present but broken** — a 5s failsafe in `<head>` removes the motion state.
- Scroll is never hijacked: native scrolling throughout. Anchor glides cancel on
  wheel, touch or key press. Pointer effects only run on devices with a fine pointer.

**Tuning.** Intro length: the `1700` ms minimum in the last block of `site.js`.
Pinned scene length: `height:310svh` on `.film`. Parallax strength: the
`data-par` values near the top of the scroll engine in `site.js`.


## v7 — TL feedback round

New file `assets/css/refine.css` (loads last). `index.html` and `site.js` also changed.

- **Duplicate removed.** The "By the numbers / Four decades" mosaic is gone. "A steady hand" + "Five chapters" is the one place the experience story lives; "40+ years" still appears in the hero stats and the About fact list. The old `.mos`/`.mt` CSS is now unused and can be deleted.
- **Hero loading.** The old hero ran its entrance animations twice (once from `site.css` behind the curtain, again from `cinematic.css` when it lifted) and animated blur filters. Now: a light intro that cross-fades out (about 0.9s minimum instead of 1.7s), then one entrance per element, with no blur or clip-path.
- **"Not sure where to begin?" card.** Pale blue instead of the deep gradient. It is now a `div` with two real buttons (Book + WhatsApp), since a link cannot contain another link.
- **WhatsApp.** Floating button on desktop, a Call + WhatsApp dock on phones, plus inline buttons in the hero, CTA card, FAQ, reviews, booking section and closing band. All use `https://wa.me/918800000255` with a prefilled message. Edit the message in the URL `text=` parameter.
- **Films.** New titles, descriptions and a per-film meta line. Posters regenerated from frames without the large on-screen hook text. The footage itself is unchanged.
- **Reviews (`#reviews`).** Two Google listing cards (New Delhi, Gurugram), a filter and review cards. **All ratings, counts and review text are placeholders**, marked with amber chips. Replace them with the real data and delete the three "placeholder markers" rules at the end of the reviews block in `refine.css`. Do not add `aggregateRating` structured data until the numbers are real.
- **Closing band.** "You do not have to work it out on your own" is now the last section before the footer, with Call and WhatsApp buttons. The nav "Contact" link goes to it.


## v8 — gentle, premium components (original blue palette kept)

New file `assets/css/warm.css` (loads last), plus a Fraunces font link in `index.html`. It does not change colours: the blue palette is exactly as in v6/v7.

- **Reviews.** Filter removed. Sticky heading with links to both Google listings, six real reviews in a two-column masonry, first card featured. Two reviews that Google cut off with "More" stop at their last complete sentence.
- **Type.** Headlines, stats and FAQ questions use Fraunces, a soft serif (fallback Georgia). Body and UI stay Inter.
- **Motion.** One shared gentle easing curve (`--e`), longer durations, headline words that fade up through their mask. The 3D card tilt is replaced by a soft lift. Magnetic buttons, hero parallax, anchor glide and the FAQ are calmer. No blur filters are animated.
- **Reduced motion** still gives the full static page.

## v9 — warm palette and calm components

New: `assets/css/calm.css`, `assets/js/calm.js`, `docs/react-port.md`. The blue palette is re-mapped to cream, sage, forest, blush, clay and gold across every CSS file (tokens are in `:root` of `calm.css`).
- **Hero**: slow 10s breathing light behind the portrait; the primary button pulses gently.
- **Nav**: glass bar that narrows on scroll.
- **Breathe & Ground**: floating widget (bottom left). 4s in, 2s hold, 6s out, six rounds. Without motion preference it still guides by label only.
- **Request a time (`#request`)**: three-step form with progress bar. It stores nothing; it opens a prefilled WhatsApp message to +91 88000 00255.
- **Support band** above the footer: Tele-MANAS 14416 / 1-800-891-4416 (checked against Government of India sources) and 112. Re-check numbers before each release.
- Fonts: Figtree for UI, Fraunces for headlines. Placeholder review markers from v7 are unchanged and still need real data.

## v10 — bolder hero and clay cards

New `assets/css/bloom.css` (loads last): arched window of light behind the portrait, solid readable name (the old gradient faded out), glass intro and stats cards, clay-style cards with inner highlights, fine paper grain, calmer headline rhythm, rounded tinted sections. Also fixes the phone hero, where the name ran off the edge and the intro and stats were clipped.

## v16 — spatial layer, film descriptions removed

New `assets/css/spatial.css` (loads last) and `assets/js/spatial.js`. Frosted-glass cards and nav, layered shadows, a slow ambient light field behind the page, one section rhythm and eyebrow style, floating glass reel and player controls, and a soft pointer tilt with a lift on hover (fine pointers only). Reduced motion turns off the drift and the tilt. The three film descriptions are removed from the reel in `index.html`; titles and the film meta line stay.

## v17 — hero matches the approved composition

Last block of `assets/css/spatial.css`, desktop (1000px and up) only. The name now sits behind the portrait (the head overlaps the lower part of the name), the portrait is slightly larger, the hero keeps Book Consultation with the WhatsApp button beside it, and the intro text, stats and qualification block share the same inner edges. On desktop the floating Breathe widget tucks away while the hero is on screen so it never covers the hero buttons, and returns once you scroll past. Tablet and phone layouts are unchanged.

## v18 — hero fits at any screen size; WhatsApp back in the hero

Last block of `assets/css/spatial.css`. The hero name was sized from the window width, so on large monitors it outgrew the 1180px panel and the final "a" was clipped, and its "p" ran into the qualification text. The name now scales with the panel (container units, `--hn`) and always fits. Its vertical position is tied to the portrait's top edge so the head overlaps the name by the same amount at every size, and the qualification block sits just below the name's descenders. The WhatsApp button is back in the hero, in one row beside Book Consultation; when the panel is narrower than 1130px it wraps under Book, as before.

## v19 — UI fix pass

New `assets/css/fix.css` (loads last). Small edits in `index.html`, `calm.css` and `site.js`.

- **Hero name clipped on phones, too wide on desktop.** Root cause: the request form's chip class (`.ch`) had the same name as the hero name's per-letter class, so every letter picked up a `.45rem` right margin. The form chips are now `.rchip`. Name sizes were re-tuned for phone, tablet and desktop so it fits and fills the panel.
- **Portrait.** The shoulders ended in a hard vertical line (and a 1px hairline on some screens). A wider oval mask now dissolves them at every size.
- **WhatsApp.** The floating button is a pill with a badge icon, hover state, focus ring and a short attention pulse. The phone dock is one full-width bar instead of two pills on a square white strip.
- **Phone hero.** Book and WhatsApp buttons are centred under the centred text.
- **Review stars** were grey-blue (a rule meant for the quote mark hit them). They are gold again.
- **Nav.** The highlighted link no longer stays on "Contact" after scrolling back to the top.
- **Footer.** Text contrast raised (was about 3:1), aligned to the page column, "Films" link added, wordmark no longer clipped, and the pale strip under the footer on phones is gone.
- **Films.** Cream, peach and brown leftovers replaced with the blue palette; the section blends into the page; the active card no longer sticks out past the list.
- **Press carousel** fades out at the edge instead of cutting a card in half, and bleeds to the screen edge on phones.
- **Booking card, "first step" band, tablet credentials grid** spacing fixed.
- **Head.** One Google Fonts request instead of three, theme colour matches the navy, small heart favicon.


## v20 notes

- `index.html` is now edited by hand. `tools/build.py` regenerates an older layout from `legacy/` and **will overwrite the current page**; do not run it.
- `assets/css/polish.css` is the last stylesheet layer (tokens, press cards, credential chips, booking panel, breathe bubble).
- Removed: pinned quote band, "Coming in", Credentials section, Breathe orb band, Tele-MANAS band, separate "Request a time" and "Talk to us" sections. Treatment and aftercare now live in the FAQ; credentials sit inside each of the five chapters.
- Breathe reminder: `assets/js/calm.js` (first at ~45s, then ~4 min, max 3 per visit, never while typing or with the guide open, off after two dismissals).

## v21 — light UI refinement

New `assets/css/touchup.css` (loads last, after `polish.css`). No copy, colours or structure changed.

- **Ambient glow** now cool blue. The old cream/amber wash from the earlier palette showed as a warm patch behind "What he treats".
- **Phone announcement bar** is a single line (the "Consultations available online" text is hidden under 640px; the call link stays).
- **Service cards** are equal height with tags pinned to the bottom, plus a blue accent line and icon fill on hover.
- **Journey**: space around the award chip. **Films**: the playing film has a blue edge and title. **Reviews**: calmer heading. **FAQ**: heading stays beside the questions on desktop.
- **Small feedback**: nav link underline on hover, button press state, booking chips lift, tighter section spacing.
- Reduced-motion visitors get none of the new transitions.

## v22 — Tulasi logo and link to the Tulasi site

New `assets/css/tulasi.css` (loads last), `assets/img/tulasi-logo*.webp`, `tulasi-favicon.png`.

- **Logo.** Replaces the heart icon in the nav and the favicon; also in the footer and in a new "Visit the Tulasi Healthcare website" band above the footer.
- **Redirect.** Links to `https://tulasihealthcare.com` (new tab) from the announcement bar, nav ("Tulasi Healthcare ↗"), the band, and the footer. To change the target, search `index.html` for `tulasihealthcare.com`.
- **Mobile.** Checked at 1440, 820, 390 and 360px: no horizontal overflow, menu includes the new link, band stacks on phones.

## v23 — SEO pass

- **H1** is now "Leading Psychiatrist in Delhi NCR" (small caps line) + "Dr. Gorav Gupta", one `<h1>`; the design is unchanged.
- **Title / description** carry the same phrase plus de-addiction, dual diagnosis, depression, anxiety and OCD.
- Added canonical, robots, Open Graph and Twitter tags; JSON-LD (`Physician` + `Tulasi Healthcare` with both addresses and the phone); `robots.txt`, `sitemap.xml`.
- **Confirm before launch:** the domain `goravgupta.com` used in canonical, OG, JSON-LD and sitemap; and that the client is comfortable with the word "Leading" (a superlative claim).
- No ratings or review counts in the structured data (the reviews are not yet verified numbers).

---

## Taste pass (v23)

Applied with the `Leonxlnx/taste-skill` pack (`.agents/skills/`), following its
`redesign-existing-projects` audit sequence: scan → diagnose → targeted fixes,
working with the existing stack rather than rewriting it.

### What was wrong

The design had drifted into three patterns the audit flags as generic:

1. **Hospital blue.** `pro.css` redefined the whole palette (`--blue:#2F6FCB`,
   `--ink:#13243A`) on top of the warm cream + sage system the base `site.css`
   actually defined. Everything downstream inherited it. This also contradicted
   the original brief, which ruled out healthcare blue explicitly.
2. **Inter + Poppins.** Both are on the skill's banned list — the default
   geometric-sans pairing that reads as a template.
3. **A uniform grid of equal cards** (white + 1px border + shadow), which the
   audit calls the single most recognisable AI layout.

### What changed

- **Palette restored and unified.** Reverted the blue hijack, then remapped
  every remaining cool colour across all 14 stylesheets onto a warm sage ramp at
  matched luminance, so contrast relationships were preserved rather than
  eyeballed. 42 hexes plus the `rgba()` glows and shadow tints. Shadows now
  carry the background hue instead of neutral black.
- **Editorial type voice.** Fraunces (variable serif) for display, Instrument
  Sans for UI and body. The hero name dropped from Poppins 700 to Fraunces 300
  with tight tracking, and lost its gradient text fill — a flourish that reads
  as template. Added `text-wrap: balance` on headings, `pretty` on body.
- **Calmer surfaces.** Cards moved from white + border + shadow to warm paper
  with a tinted hairline, elevation only on hover. Hover travel cut from -8px to
  -3px with a custom cubic-bezier, plus a real `:active` press state. Icon
  badges lost the 360° spin.
- **Asymmetric bento** for areas of care: same markup, 12-column grid with
  uneven spans (7/5, 4/4/4, 5/4/3) and a weighted lead tile. Collapses to two
  columns at 860px and one below 600px.
- **Texture and spacing.** Fixed, pointer-events-none grain overlay; section
  padding roughly doubled; one accent (bronze `#8A6A3B`) used sparingly for
  timeline markers, press labels and focus rings.

All of this lives in `assets/css/taste.css`, loaded last, plus in-place colour
edits to the earlier layers. Verified at 1440px and 375px: no horizontal
overflow, no console errors.

### Worth doing next

The page now loads **14 stylesheets** applied in sequence, several of which fight
each other with `!important` (`pro.css` alone has 133). The taste pass works
within that, but the layers should be flattened into one stylesheet before much
more is added — right now a change in the wrong file silently does nothing.

### Brand mark at small sizes (v23.1)

The Tulasi logo is a word-cloud brain inside cupped hands, under arched
"tulasihealthcare" lettering. It is a detailed mark: below roughly 120px the
lettering and the word cloud stop resolving and it reads as a blue smudge in a
white box. No CSS fixes that — the detail is the problem.

So the logo is now used at three sizes, each with an appropriate asset:

| Place | Asset | Size |
| --- | --- | --- |
| Nav | `tulasi-mark.png` — hands only, transparent | 40px (34px mobile) |
| Footer credit | `tulasi-logo.webp` — full lockup | 84px (68px mobile) |
| Tulasi band | `tulasi-logo.webp` — full lockup | 220px |

`tulasi-mark.png` is generated from the full logo: cropped below the arched
lettering, then the hands isolated on their own by channel (they are a single
flat indigo) with soft alpha so the edges stay smooth. It holds up down to
about 24px.

**This is a modification of the Tulasi brand mark** — a cropped detail used as a
small-size variant. That is ordinary responsive-logo practice, but it is their
mark, so it is worth a nod from whoever owns the brand. If they would rather not
crop it, the better alternative is to drop the logo from the nav entirely and
run a typographic lockup there: this is Dr. Gupta's personal site, the full logo
already appears twice further down, and the top bar links to Tulasi by name.

## v10: client review round

Feedback came in over WhatsApp. Everything below is in `index.html` plus one new
last layer, `assets/css/refresh.css`, and one new script, `assets/js/gallery.js`.

| Feedback | What changed |
| --- | --- |
| "Logo is not complete" | The full Tulasi logo (hands, brain, lettering) now sits top-left of the doctor card (`.hero__logo`), from a new transparent asset `assets/img/tulasi-logo-nav.webp` (the white box is gone). The nav carries the name only; `tulasi-mark.png` is no longer used. |
| "Heading font can be changed" and the clipped "H" | Headings and body are now **Geist** (loaded in the `<link>` in the head). The clipped first letter came from the word-mask reveal on `h2` (`overflow:hidden` with about 3px of padding); that split was removed in `site.js`, and `.wd` can no longer clip. |
| "Leading psychiatrist in Delhi NCR, pls change" | The hero title, `<title>`, meta description, Open Graph and Twitter titles now say **Senior Psychiatrist in Delhi NCR**. It keeps the search keyword and drops the superlative "leading", which medical-advertising rules in India discourage. Say if you want different wording. |
| "Write professional journey" | New `#journey` section, **Professional journey**: six entries (Training, Clinical practice, Tulasi Healthcare, Public service, Recognition, 2024). Only facts already on the site are used. **No dates were added**; the README note on MBBS/MD years still applies. |
| "Add a picture section" | New `#gallery` section, **Seminars, conferences and OPD**: one real photograph (the consulting room) with a click-to-enlarge view, and three written items beside it (OPD and community camps, seminars and conferences, writing and public awareness). The text uses only facts already on the site. |
| "Relevant icons for each disease" | Phosphor icons (regular weight, inlined): pill, overlapping circles, brain, mood wave, rain cloud, spiral, mask. |
| Logo to the top-left of the doctor card | Done, see row one. |
| More description above the videos | Longer intro under "Hear it from the doctor", plus a one-line description under each film. These were written from each film's on-screen captions. |
| "Visit the Tulasi Healthcare website" band | Reworked as **Part of Tulasi Healthcare**: no pasted-in logo card, the two institutions listed, and a plain text link. |
| Locations to the two GMB listings | The consulting-room cards, the footer addresses and the two "on Google" pills now point to the share.google listings, and `hasMap` was added to the JSON-LD. The link ending `T2NTrf...` is mapped to New Delhi and `ZI81WG...` to Gurugram (the second resolves to "Dr. Gorav Gupta Psychiatrist in Gurgaon"); swap them if that is wrong. |

Also applied from the taste-skill checklist: no em-dashes in visible text, fewer
section eyebrows, middle-dots replaced by commas in the hero and footer, a solid
(not gradient) name, a nav that no longer shrinks to a width it cannot fill.

### Adding more gallery photos

The section is built around one photograph on purpose. To add another, copy the
`<figure class="gal__fig">` block in `index.html` (inside `#gallery`), point
`data-full` at the full photo and the `<img>` at a `-md` copy in
`assets/img/gallery/` (about 1600px and 1000px wide, WebP), and give it a
descriptive `alt` and a plain caption. Wrap two or more figures in their own grid
if you want a row of photos; the lightbox in `assets/js/gallery.js` works on any
`.gal__btn`.

### Open items

- **Seminars and conferences wording.** The text says he is a member of the
  three psychiatric societies and "a participant at professional seminars and
  conferences". That last part comes from the client asking for conference
  photos, not from a source on the old site. Event names and dates, if the client
  wants them, need to come from them.
- **Phone number in film 2.** The end card of `film-2.mp4` shows
  **7707070002**, not the site's +91 88000 00255. Confirm which is current.
- **Dark mode** was not added; it would mean reworking all fifteen CSS layers.

## v11: multi-page site

The single page is now seven real pages that share one header and footer. The
earlier sections of this README describe the single page (kept in
`legacy/single-page-v10.html`); this section is current.

### Pages and the journey

| URL | File | Job |
| --- | --- | --- |
| `/` | `index.html` | Landing: hero, areas of care, short About, journey milestones, film teaser, reviews |
| `/about-us/` | `about-us/index.html` | Trust: the doctor, Tulasi's centre, home and outreach, OPD, camps and seminars |
| `/journey/` | `journey/index.html` | Credibility: the dated timeline (education, positions, public service, memberships) |
| `/services/` | `services/index.html` | Need: all eight areas of care and how treatment works |
| `/video-gallery/` | `video-gallery/index.html` | Proof: the three films, and why to watch them |
| `/publication/` | `publication/index.html` | Proof: press and writing |
| `/contactus/` | `contactus/index.html` | Primary action: call, WhatsApp, 3-step request, both Google listings, FAQ |
| any other | `404.html` | Not found |

Every page ends in **Book Consultation**, which goes to `/contactus/`. The slugs
`about-us`, `services`, `publication`, `video-gallery` and `contactus` are the old
WordPress URLs, kept so existing links and search ranking carry over. `/journey/`
is new. The old site's condition, blog, "Ask the Doctor" and "Mental Health" pages
were **not** rebuilt; they need the doctor's review first.

### Editing and building

Edit the **sources**, then rebuild. Never edit the generated `index.html` or the
`*/index.html` files by hand; the next build overwrites them.

```
src/pages/*.html        one file per page: a <!--meta {...}--> block, then the body
src/partials/*.html     head, header, footer, floating buttons, intro (shared)
tools/build_site.py     the build
```

```bash
python tools/build_site.py      # writes the pages, sitemap.xml and assets/css/bundle.css
npx serve .                     # then open http://localhost:3000
```

The build also concatenates the sixteen CSS layers, in the old cascade order, into
one `assets/css/bundle.css`, so each page makes one stylesheet request. **Edit the
layers in `assets/css/`, not the bundle**, and rebuild. To add a page, copy a file in
`src/pages/`, change its meta (`slug`, `nav`, `title`, `description`, `crumb`) and
rebuild; add a `nav` key to `NAV` in the build and a link in `partials/header.html`
if it belongs in the menu.

Placeholders: `{{root}}` (path back to the site root), `{{wa}}`, `{{waicon}}`,
`{{delhi}}`, `{{gurugram}}`.

### What the build gives you

- One header and footer; the current page is marked `aria-current="page"` and
  highlighted in the menu (also in the phone menu).
- Skip link, one `<h1>` per page, breadcrumbs, per-page title, description,
  canonical and Open Graph tags, breadcrumb structured data (full practice graph on
  the home page), `sitemap.xml`.
- Page-to-page fade using cross-document view transitions (Chrome and Edge; other
  browsers navigate normally). The header stays still. Off under reduced motion.
- The opening curtain plays once per browser session, on the first visit only.
- Scripts load per page: `gallery.js` on About, `films.js` on Video Gallery.

### The journey page

Built from the LinkedIn experience and education the client supplied: M.B.B.S.
1987 to 1992 (Maulana Azad Medical College), M.D. 1994 to 1997 (Lady Hardinge
Medical College), Founder and CEO of Tulasi Healthcare (Jan 1999 to Jan 2025),
Head of Department, Psychiatry, Batra Hospital (2001 to 2009), Honorary Visiting
Consultant, Sir Ganga Ram Hospital (2001 to 2010), Founder, Tulasi Healthcare
(Apr 2002 to present), President, Mental Research Society (2005 to 2021), Member,
Central Mental Health Authority (2018 to 2021), plus the existing 2024 NITI Aayog
task force, free OPD, government work and the Economic Times award. LinkedIn shows
two of four education entries; ask for the other two.

### Open items for the client

- **Years in practice: resolved, but confirm the year.** "40+ years" was removed
  everywhere because the LinkedIn dates did not support it. The site now says "in
  practice since 1997" (the year the M.D. was completed) and the hero stat shows the
  years since then (29+ in 2026). The year lives in one place, `PRACTICE_SINCE` in
  `tools/build_site.py`; change it there and rebuild. If the client counts from the
  M.B.B.S. (1992) instead, set it to 1992 and the prose and the number follow.
- **M.D. subject.** LinkedIn gives the field as "Physical Medicine and
  Rehabilitation / Psychiatry Residency Program"; the site says "M.D. Psychiatry".
  The Journey page shows the LinkedIn wording verbatim.
- **Seminars and conferences** wording on About is general; real event names and
  dates, and more photographs, would strengthen it.
- **Film 2** ends on a card showing 7707070002, not +91 88000 00255.
- **Eating disorders** was added to Services from the old site's own page.

## v12: home restored, and the old site's content imported

The home page is the single-page design again (all twelve sections, `src/pages/home.html`),
keeping the "in practice since 1997" wording. It now links onward to the other pages.
This supersedes the v11 note that the old condition, blog, "Ask the Doctor" and "Mental
Health" pages were not rebuilt: **all of them are now on the site**, with the doctor's consent.

| What | Where |
| --- | --- |
| 26 pages (conditions, FAQ, Ask the Doctor, mental health tests, local pages) | at their old URLs, e.g. `/schizophrenia-psychiatrist-delhi-gurgaon-ncr/` |
| 98 blog posts | `/blog/<slug>/` (old URLs kept, including the Hindi ones) |
| Blog index, 12 per page | `/blog/`, `/blog/page/2/` and so on |
| Resources hub (tests, FAQ, videos, publications, testimonials, latest posts) | `/resources/` |
| Condition guides grouped by area | `/services/` (below the cards) |
| 6 client testimonials from the old home page | `/testimonials/` |
| 11 YouTube videos from the old gallery, plus the 3 films | `/video-gallery/` |
| Full publications list (10 links, Hindi ones included) | `/publication/` |

Text was imported verbatim from the old site through its public content API
(`tools/import_wp.py`, a one-off; its source files are now `src/content/pages|posts/`).
An audit against the live pages found the schizophrenia page 100% present (61 of 61
text blocks); across all 124 imported items 96% of blocks are identical and the rest are
template furniture (a leftover San Francisco placeholder address, contact boxes, forms)
and the doctor-bio blocks, which now appear as the author box. Images were localised
(77 imported, resized to WebP; 11 more were already 404 on the old site and are dropped).

What was changed rather than copied:

- **Years of experience.** The old site gives 20, 25, 28 and 30 in different places. Claims
  about the doctor were reworded to "since 1997"; every change is listed in
  `docs/migration-adaptations.md`. A few unrelated claims (research "over the past 25
  years", Tulasi "running for more than 28 years") were left alone.
- Old forms and widgets were dropped; FAQ accordions became `<details>`; ALL-CAPS headings
  were sentence-cased; five internal links that were already dead on the old site were
  pointed at the closest live page; a junk `tel:` placeholder was removed.

### For the doctor to review

- **Superlatives.** The old copy says "best", "top", "No. 1" and "leading" throughout, and
  it was carried over as written. That sits oddly with the earlier request to change the
  hero line "Leading psychiatrist in Delhi NCR", and Indian medical advertising rules
  discourage such claims. Decide whether to soften them in `src/content/`.
- **Facts that disagree on the old site.** Tulasi Home capacity is 40 patients on About Us
  and 45 on the home page (the newer 45 is used); camps are "bimonthly" on one page and
  "fortnightly" on another (fortnightly is used); Publications says he is an "active
  member of the Central Mental Health Authority" while LinkedIn shows 2018 to 2021.
- The old home page's hero slogans ("Best Psychiatrist in Gurgaon &amp; NCR" and similar)
  were not put on the new hero.
- Tag and category archives were not rebuilt; links to them go to `/blog/`.

### Booking block and the top line

(Superseded: `assets/css/navy.css` loads after `booking.css` and puts this block back on a navy
panel, the design the client preferred. `booking.css` is kept but is overridden.)
The "Book a consultation" block (`#appoint`, on the home and contact pages) was restyled in
`assets/css/booking.css` as an open layout on the page background: a hairline rule instead of
the dark rounded container, two address rows instead of nested boxes, and one form panel.
The older layers style it with `!important`, so the overrides are scoped to `#appoint`.
The line at the very top of the home hero, and the home page `<title>` and share preview,
read "Best doctor in Delhi NCR" (set in `src/pages/home.html`). The hero line itself now follows the
rewrite document (see v13).

## v13: homepage rewrite, tighter layouts, more films, About redesign

Source: "Gorav Sir Homepage Rewrite content.docx". Obvious typos were fixed ("wall of clinical
psychiatry", "issues,", "Delhi psychiatrist Society" to the name used elsewhere on the site).

- **Home copy** follows the document: hero, areas of treatment (7 cards, each with *Read more*
  to its condition page), Know your psychiatrist, How it all began (four stages on the original timeline layout), Voicing his
  own, Capturing insights, Real voices, Common questions. New layouts live in `assets/css/home2.css`
  (the last CSS layer); class names are `sv`, `hx-*` and `ab-*`.
- **Years.** The client confirmed "40+ years of experience", so that is the figure used everywhere
  (`EXPERIENCE` in `tools/build_site.py`, placeholder `{{exp}}`); the imported pages were reworded to
  match. The M.D. is dated 1997 on the old site, so the training dates still read 1997. That is the
  one place the two figures sit side by side.
- **Links to tulasihealthcare.com:** the two Tulasi pills in the memberships strip, the two cards
  in "Part of Tulasi Healthcare", and the Tulasi tags in the journey cards.
- **Press cards** show a short quote from Dr. Gupta taken from each article (OnlyMyHealth, Tribune,
  Firstpost, Day2Day, CrazyPundit). The Hindi Janta Serishta piece and the YouTube card have no
  quote, so they carry a one-line description marked "About the article". The OnlyMyHealth page
  is gone from the live site (HTTP 410); its quote was read from the web archive copy.
- **Floating buttons** are two circles: call (`tel:+918800000255`) and the official WhatsApp logo (`assets/img/whatsapp-logo.webp`). The old
  green "Chat on WhatsApp" pill and the phone dock are gone (`src/partials/floating.html`).
- **Films:** eight now. `src/partials/films-player.html` is the one list, included on the home and
  Video Gallery pages through `{{films_player}}`. Films 4 to 8 were compressed from the files
  dropped into `assets/video/` (about 100 MB down to about 38 MB); the originals are kept
  untracked in `assets/video/_originals/`. Titles and descriptions for them were written from an
  automatic transcript, so the doctor should check them. Film 5 (schizophrenia) has a banner burned
  into the video that reads "Saving lives & restoring families since 2002" and "Call +91 7707070001",
  which disagrees with the rest of the site (since 1997, 88000 00255); it needs a re-export to change.
- **About page** redesigned as a profile page: portrait hero with a stats row, profile text with an
  at-a-glance card, training and memberships, the four-stage journey (shared with the home page via
  `{{journey_stages}}` from `src/partials/journey-stages.html`), Tulasi Healthcare cards, gallery.
- **Reveal-on-scroll** now also reveals elements the reader has already scrolled past, and no longer
  holds back elements in the bottom 6% of the window. A section could stay blank after a fast jump
  or in a full-page screenshot.
- The line under the doctor's name in the header ("Psychiatrist") was removed.
- The hero top line reads "Best doctor in Delhi NCR" again. Cards on the home page lift and turn blue on hover.

## v14: swipeable film rail, About page back on its original structure

- **Films** are now a full-width swipeable rail (`src/partials/films-player.html`, `assets/js/films.js`,
  `assets/css/films2.css`) instead of a player with a pick-list. Native scroll-snap, so swipe, trackpad,
  mouse drag, arrow keys and the arrow buttons all work. `films.js` adds the depth layer: each card is placed
  in 3D from its distance to the centre, the deck gathers and fans out as the section scrolls into view, the
  playing card tilts toward the pointer, and the media inside each card moves slower than the card. Only the
  centred film plays (muted until the speaker button is used). With reduced motion it is a plain snap row.
  Five films: 1 to 4 as before, film 5 ("How Tulasi Healthcare began") is the video added on 12 Oct. Its
  description was written from an automatic transcript, so please check it. In that film he says Tulasi started
  "around 25 years ago", which does not match "40+ years".
- **About page** returns to the original structure (title bar, text beside the photo, facts panel, biography,
  Tulasi list, photo section) with the rewrite document's wording, no eyebrows or numerals, and one type scale
  (see `assets/css/about2.css`).
- **One typeface.** Older layers still named Poppins, Figtree and Inter on individual elements. The last rule in
  `home2.css` forces Geist everywhere (Devanagari falls back to Noto Sans Devanagari).
- **Impeccable** (`npx impeccable install`) is installed for this project: `PRODUCT.md` records the product
  context, `.impeccable/config.json` has the design hook on, and the skill lives in `.claude/skills/impeccable/`.
  `npx impeccable detect <files>` scans for design anti-patterns.
- **Scroll motion** (`assets/js/scrollfx.js`, About page only; the home and Journey pages have none): everything is
  a function of scroll position and reverses when you scroll back. Elements emerge from depth (scale, translateZ, a
  little tilt, and a blur that clears as they land, with a touch more during fast scrolling), layers drift at
  different rates (the plate behind the portrait moves against the photo), the facts panel and lists arrive one
  after another, paragraphs darken word by word, a soft light follows the pointer over the facts panel, and the
  timeline spine fills as you scroll. Small finishing touches play once when something lands. Reduced motion leaves
  the page static; the horizontal overflow from the side-in motion is clipped on `html.fx`.
  The About page layout was tightened too: text and photo share a height, the biography is two columns, and the
  positions list is two ruled columns. The photo section and the "News and awards" item were removed, and every
  inner page now ends with an open call-to-action instead of the dark band.
- **About: "How it all began"** is now four stacked boxes (`data-fx="stack"` in `scrollfx.js`, `.st-box` in `about2.css`): each box
  emerges from depth, pins under the one before it, and the earlier boxes recede (smaller, dimmer, lifted) as the next slides over.
  The icon and text inside a box drift at different rates and its tags arrive one by one. Under 700px the boxes are plain, unpinned.
  The home page's "Professional journey" uses the same stacked boxes (six of them, the original entries); it is the only animated block on the home page besides the film rail. `src/partials/journey-stages.html` and `{{journey_stages}}` were removed (no longer used).
- **Stacked boxes, tidied:** a covered box now collapses into a one-line title strip (icon, stage, title) instead of showing cut-off
  text, so the stack reads as a neat list of tabs. Step between pinned boxes is 60px (`--k` in CSS, `top` in `scrollfx.js`).
- **Polish pass** (end of `home2.css`, section 15): services grid balanced (the long seventh card spans two columns, the link tile
  fills the last cell), home About text on the About page's type scale, quieter film backdrop, the Breathe pill hidden under 900px,
  smaller floating buttons on phones, and browser-drawn details (selection colour, caret, form accent, focus ring, text wrapping).
- **Film rail loops.** `films.js` keeps three copies of the films side by side and, whenever the view settles on an outer copy,
  moves back to the middle one unseen (carrying the playing position), so after film 5 comes film 1 and the other way round.
  The heading above the rail is centred.
- **Whole cards are links** (home service cards and the Services page): the "Read more" link stretches over its card; a second link in
  a card (Anxiety and OCD) stays separately clickable. The Tulasi pills in the home journey link to tulasihealthcare.com.
- **Responsive check:** home, About, Services, Journey, Contact, Resources, Video Gallery, Blog and a condition page were measured at
  320, 375, 768, 1024, 1280, 1920 and 2560px: no horizontal overflow anywhere, the nav switches to the burger below 901px, and no
  readable text is set below 12.5px. The About page's facts panel was removed (the home page keeps its own).
- **Home follows the rewrite document again where it had drifted:** the journey is the document's "How it all began" (four stages with their
  recognition lists, same boxes as the About page), the hero carries "Pioneering the field of psychiatry / Renowned psychiatrist in Delhi NCR",
  the About block uses the document's heading line, and the films label is "Voicing his own". "New Delhi and Gurugram" was taken off the hero.
- **Scroll smoothness:** the stacked boxes now do all their work with transform and opacity (no blur, no custom-property writes), positions come
  from one read per frame, the glass-blur nav is a near-solid white pill, and the two infinite full-page background animations are still.
  In a software-rendered test the journey section went from about 66ms per frame to a 16.7ms median (60fps).
- **Names open something.** The home memberships strip is one consistent pill style and every pill links. Where an official site was found and
  checked it opens that: tulasihealthcare.com, niti.gov.in, socialwelfare.delhi.gov.in, indianpsychiatricsociety.org, mamc.delhi.gov.in,
  lhmc-hosp.gov.in, ima-india.org, economictimes.indiatimes.com and the Mental Healthcare Act on indiacode.nic.in. No official site could be
  found for the Delhi Psychiatric Society or the Indian Association of Private Psychiatry, so those pills go to the memberships list on the
  About page rather than to a guessed address. Same links apply to the tags in the journey boxes (home and About), the About memberships list,
  the About Tulasi cards (the whole card opens the Tulasi site; Clinics opens the Contact page) and the hero award badge.
  If the client has the real addresses for those two societies, add them in `tools`-free fashion by editing the pill in `src/pages/home.html`.

- **Team feedback round (journey, booking, rooms):** the scroll-stacked journey boxes are replaced on home and About by a non-interactive animated timeline (`assets/js/journey.js`, styles in `about2.css`): each milestone is a soft card hanging off a marker; the
  line fills with the scroll, a small glowing dot travels down it, each marker lights up as it arrives and the current card is lifted and
  blue-edged; each card also eases in once (card, label, heading, rule, text, tags in turn). Phones drop the card frame to keep the text wide.
  No clicking; reduced motion (or no script) shows the finished timeline. Press coverage cards are now exactly as tall as their own content (no blank
  band inside the shorter ones) and the section is tighter. The home "Not sure how to seek help?" block is removed (the floating call and
  WhatsApp buttons, the header button and the Contact page remain); "Book Consultation" on home now opens the Contact page. The two
  addresses are a framed "Consulting rooms across Delhi NCR" section (`#rooms`, `.rm*` in `home2.css`). Treatment-areas heading is now
  "Specialised psychiatric care for mental health and addiction".
- **FAQ section:** Resources menu > "Frequently asked questions (FAQ)" (a plain link; the five topics are listed on the FAQ pages). Pages `/faq/` and `/faq/<topic>/` are built
  by `tools/faq_pages.py` from `data/faq/*.json` (one file per topic: title, short, optional intro, questions with HTML answers; adding a file adds
  the page and the card). Content is regrouped from the FAQ page at goravgupta.com (kept at
  `/frequently-asked-questions-psychiatrist-near-me-consultation/`). The live page no longer carries the "More frequently asked questions"
  Q&As (why choose Dr. Gupta, alcoholism, OCD, therapy, ...); they come from the earlier import of the same page, so delete them from
  `data/faq/*.json` if the team does not want them. The consultation fee (Rs. 2700 for 20 minutes) is quoted from that page. Topic pages carry
  FAQPage structured data. Page styles `assets/css/faq.css`, `assets/js/faq.js`.
- **Parity with goravgupta.com:** every URL in the old site's sitemaps (pages, posts, categories, tags, authors) now exists here, checked against its
  five sub-sitemaps. The WordPress archives are rebuilt from `data/taxonomy.json` (copied from the old archive pages: which post is under which tag,
  category and author) by `tools/taxonomy_pages.py`: `/tag/<slug>/` (88), `/category/blog/`, `/author/admin/`, `/author/goravgupta/`; posts show their tags at
  the foot. The old `/video-gallery-draft/` is now the **Video Library** (Resources hub tile, linked from the Video Gallery): our 5 films, the draft page's
  Tulasi Healthcare centre and recovery films (8 new thumbnails in `assets/img/yt/`) and all the gallery's YouTube talks, 20 videos in total. Seven links on the old home page (`/bipolar-disorder/`, `/schizophrenia/`, `/stress-management/`, `/depression-treatment-delhi-india/`,
  `/de-addiction-treatment-delhi-india/`, `/eating-disorder-treatment-delhi-india/`, `/mental-health-assessment/`) are 404 on the old site itself.
- **Resources page redesign** (modelled on the layout of myndstories.com/stories, in our own palette): a blue banner, a sticky sidebar (search, categories with counts,
  tags, quick tests) and a grid of article cards with numbered paging. Filtering by category, tag (all 88 are reachable via "Show all tags") and search, plus
  sorting, runs in `assets/js/hub.js` and is kept in the address (`?topic=&tag=&q=&sort=&page=`). All 98 articles are in the HTML; without JavaScript it is a plain grid
  and the tags link to their `/tag/<slug>/` pages. Markup in `tools/hub_pages.py` (`resources_hub`, `GENERIC_TAGS` keeps the SEO-style tags out of the first row of
  tag chips), styles in `assets/css/hub.css`. Categories are the five condition topics plus Wellbeing; tags come from `data/taxonomy.json`.
- **Journey and About copy** now follow "Journey page Gorav Sir.docx" and "About Us Gorav Sir.docx" (text only, layout unchanged; sections the documents mark "same" are untouched).
  Style fixes made to the document text: "Dr Gupta" to "Dr. Gupta", "Deaddiction" to "de-addiction", obvious typos ("established away", "Tulasi home"), and "The Anju" to "The NGO" in Community initiatives. The Journey page keeps the five dated positions the document does not mention.
  The closing "Seeking help?" blocks in the documents are not on the pages because the inner-page closing band was removed earlier.
  The About intro says "senior consultant psychologist" as written in the document (confirmed by the client team); the rest of the site calls Dr. Gupta a psychiatrist (M.D. Psychiatry).
- **Condition, local and guide pages** (the 26 imported pages: services, Psychiatrist in Delhi/Gurgaon/India, guides, FAQ guide) use a designed template, `tools/service_pages.py`
  with `assets/css/service.css` and `assets/js/service.js`: a hero (topic label, title, summary, three facts, and a "Visit Tulasi to book a consultation" card that opens tulasihealthcare.com in a new tab), the text regrouped (runs of small
  headings become a two-column list, questions use the FAQ accordion, long short-item lists run in two columns), a scroll-following "On this page" list, and three related
  pages. No words are removed (checked per page); a short first paragraph becomes the hero summary, otherwise a standard line is used. Needs `pip install beautifulsoup4 lxml`
  to build. Blog posts keep their own article layout.
- **Photos on the condition and guide pages:** the stock illustrations and infographics were replaced by 16 relevant photographs from Unsplash (free to use under the Unsplash
  License), in `assets/img/pages/<name>-4k.webp` (up to 3840 px wide) and `-1600.webp`; pages serve the 1600 px file and the 4K one only to very high-density screens (`srcset`).
  Photographers and photo links are in `data/image-credits.json`. The doctor's own photos and the award picture were kept. The six "stress busters" tips and the bipolar I/II
  definition pictures were graphics with text and are now photos only. Blog posts and other pages still use their old images.
- **/faq/ is an answer finder:** a hero with search and suggestion chips, an "at a glance" card (experience, rooms, online, and a Visit Tulasi button), a topic sidebar with counts, and all
  22 questions in one list (first paragraph of each answer, with a link to the full answer on its topic page). Search matches whole words as you type and highlights them, topics
  filter, and both are kept in the address (`?q=&topic=`). Without JavaScript the page is the full list and the topics link to their pages. Logic: `assets/js/faq-index.js`;
  markup: `index_body` in `tools/faq_pages.py`; styles: the "/faq/" section of `assets/css/faq.css`. The index no longer carries FAQPage data (the topic pages do, with full answers).
- **Home:** the "Press coverage: raising awareness" carousel is removed (the Publications page still carries the press links).
- **Journey page links:** every organisation, position and membership pill now links (MAMC, LHMC, Tulasi, Batra Hospital, Sir Ganga Ram Hospital, NITI Aayog, Ministry of Health, Delhi Social
  Welfare, Economic Times, the Indian Psychiatric Society, IMA); an entry with one organisation is clickable as a whole. No official sites were found for the Mental Research Society, IAPP,
  Delhi Psychiatric Society or the Indian Association of Psychiatry; the Central Mental Health Authority has no site of its own, so it points to the Ministry; NIMHR's site (nimhr.ac.in) currently
  has an invalid security certificate, so it is not linked. Those pills point to the About page's membership list, and the About page's matching entries point back to the Journey page.
- **Journey page:** the "On this page" sidebar and its Book Consultation button are removed; the timeline keeps its design and now uses the full width (entries sit in two columns from 900px, honours in three from 1100px).
- **UI repair pass:** CSS pruning by class name is off (it dropped rules the scripts and cascade need; the `films` and `booking` layers are back). Home hero is taller on desktop so the left column clears the logo, and the logo stacks above the name on phones. The Services menu groups no longer inherit the site-wide FAQ-card `details` styles (the stray "x" marks and boxes); on phones they start collapsed. The booking panel is contained to the page width, and stacks (text above, form below) when it sits in a service or location article column.
- **Home trust strip:** four clickable cards (Economic Times, NITI Aayog, Mental Healthcare Act 2017 on Journey, Tulasi Healthcare) in a rotating row that pauses on hover/focus; the second copy is aria-hidden with tabindex -1; reduced motion shows a plain grid. The hero description sits under the name (placed from the name's height by `site.js`), and the OPD/fee line is removed from the hero.
- **Services menu:** every condition link has its own icon (`LINK_ICON` in `tools/hub_pages.py`). **About:** one link to the dated Journey, aligned section headers, Tulasi entries as even cards.
- **Polish layer (taste-skill audit):** the 29 tracked all-caps labels are sentence case; footer headings are real `h2`s (heading order was skipping on 226 pages); headings balance and paragraphs avoid a lone last word; press feedback on buttons and cards; anchors clear the sticky bar; services cards pin their links to one line. Markup audit (alt text, link and button names, one H1 per page, meta and canonical) found nothing else to fix.
