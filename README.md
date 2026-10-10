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

1. **Years in practice — confirmed as 40+ by the client.** The site now says
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
