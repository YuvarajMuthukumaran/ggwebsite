/* hub.js: the Resources page (tools/hub_pages.py). Every article is already in the HTML; this filters, searches, sorts and pages them
   in the browser, and keeps the choices in the address (?topic=&tag=&q=&sort=&page=) so a filtered view can be shared or reloaded.
   Without it the page is a plain grid of all articles and the tags link to their own archive pages. */
(function () {
  'use strict';
  var d = document;
  var grid = d.getElementById('hb2-grid');
  if (!grid) return;

  var PER = 12;
  var $ = function (s, c) { return (c || d).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || d).querySelectorAll(s)); };

  var cards = $$('.hb2-c', grid);
  var catBtns = $$('.hb2-cat');
  var tagLinks = $$('.hb2-tag');
  var q = d.getElementById('hb2-q'), sortSel = d.getElementById('hb2-sort');
  var count = d.getElementById('hb2-count'), active = d.getElementById('hb2-active'), empty = d.getElementById('hb2-empty');
  var pager = d.getElementById('hb2-pager'), side = d.getElementById('hb2-side');
  var ftog = d.getElementById('hb2-ftog'), badge = $('.hb2-badge', ftog);
  var tagTog = d.getElementById('hb2-tagtog'), tagMore = d.getElementById('hb2-tags-more');
  var layout = $('.hb2');

  var catLabel = {}, tagLabel = {};
  catBtns.forEach(function (b) { catLabel[b.getAttribute('data-topic')] = b.firstChild.textContent.trim(); });
  tagLinks.forEach(function (a) { tagLabel[a.getAttribute('data-tag')] = a.firstChild.textContent.trim(); });
  var tagsOf = cards.map(function (c) { return ' ' + c.getAttribute('data-tags') + ' '; });

  var S = { topic: 'all', tag: '', q: '', sort: 'new', page: 1 };

  function fromURL() {
    var p = new URLSearchParams(location.search);
    S.topic = catLabel[p.get('topic')] ? p.get('topic') : 'all';
    S.tag = tagLabel[p.get('tag')] ? p.get('tag') : '';
    S.q = (p.get('q') || '').slice(0, 80);
    S.sort = ['new', 'old', 'az'].indexOf(p.get('sort')) > -1 ? p.get('sort') : 'new';
    S.page = Math.max(1, parseInt(p.get('page'), 10) || 1);
  }
  function toURL() {
    var p = new URLSearchParams();
    if (S.topic !== 'all') p.set('topic', S.topic);
    if (S.tag) p.set('tag', S.tag);
    if (S.q) p.set('q', S.q);
    if (S.sort !== 'new') p.set('sort', S.sort);
    if (S.page > 1) p.set('page', S.page);
    var s = p.toString();
    try { history.replaceState(null, '', location.pathname + (s ? '?' + s : '')); } catch (e) {}
  }

  function matches(c, i) {
    if (S.topic !== 'all' && c.getAttribute('data-topic') !== S.topic) return false;
    if (S.tag && tagsOf[i].indexOf(' ' + S.tag + ' ') < 0) return false;
    if (S.q) {
      var hay = c.getAttribute('data-q');
      return S.q.toLowerCase().split(/\s+/).every(function (w) { return !w || hay.indexOf(w) > -1; });
    }
    return true;
  }

  function order(a, b) {
    if (S.sort === 'az') return a.getAttribute('data-title') < b.getAttribute('data-title') ? -1 : 1;
    var x = a.getAttribute('data-date'), y = b.getAttribute('data-date');
    if (x === y) return 0;
    return (S.sort === 'old') === (x < y) ? -1 : 1;
  }

  function pill(label, kind) {
    return '<button type="button" class="hb2-pill" data-clear="' + kind + '">' + label + ' <span aria-hidden="true">&times;</span><span class="hb2-sr">remove filter</span></button>';
  }
  function esc(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;'); }

  function render(scroll) {
    var list = cards.filter(matches).sort(order);
    var pages = Math.max(1, Math.ceil(list.length / PER));
    if (S.page > pages) S.page = pages;
    var from = (S.page - 1) * PER, to = from + PER;

    cards.forEach(function (c) { c.hidden = true; });
    list.forEach(function (c, i) { grid.appendChild(c); c.hidden = i < from || i >= to; });   // appendChild also puts them in sort order

    // controls
    catBtns.forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-topic') === S.topic ? 'true' : 'false'); });
    tagLinks.forEach(function (a) { a.setAttribute('aria-pressed', a.getAttribute('data-tag') === S.tag ? 'true' : 'false'); });
    if (S.tag && tagMore && tagMore.hidden && $('.hb2-tag[data-tag="' + S.tag + '"]', tagMore)) toggleTags(true);

    // count and active filters
    var n = list.length;
    count.textContent = n ? (n > PER ? 'Showing ' + (from + 1) + '–' + Math.min(to, n) + ' of ' + n + ' articles' : n + (n === 1 ? ' article' : ' articles')) : 'No articles';
    var pills = '', k = 0;
    if (S.topic !== 'all') { pills += pill(esc(catLabel[S.topic]), 'topic'); k++; }
    if (S.tag) { pills += pill('Tag: ' + esc(tagLabel[S.tag]), 'tag'); k++; }
    if (S.q) { pills += pill('Search: “' + esc(S.q) + '”', 'q'); k++; }
    active.innerHTML = pills + (k > 1 ? '<button type="button" class="hb2-link" data-clear="all">Clear all</button>' : '');
    active.hidden = !k;
    badge.textContent = k; badge.hidden = !k;
    empty.hidden = n > 0;
    grid.hidden = n === 0;

    // pager
    if (pages < 2) { pager.hidden = true; pager.innerHTML = ''; }
    else {
      var h = '<button type="button" class="hb2-pg hb2-pg--s" data-page="' + (S.page - 1) + '"' + (S.page === 1 ? ' disabled' : '') + ' aria-label="Previous page">&larr;</button>';
      var shown = {};
      [1, pages, S.page - 1, S.page, S.page + 1].forEach(function (p) { if (p >= 1 && p <= pages) shown[p] = 1; });
      var prev = 0;
      Object.keys(shown).map(Number).sort(function (a, b) { return a - b; }).forEach(function (p) {
        if (prev && p - prev > 1) h += '<span class="hb2-pg__gap" aria-hidden="true">…</span>';
        h += '<button type="button" class="hb2-pg" data-page="' + p + '"' + (p === S.page ? ' aria-current="page"' : '') + ' aria-label="Page ' + p + '">' + p + '</button>';
        prev = p;
      });
      h += '<button type="button" class="hb2-pg hb2-pg--s" data-page="' + (S.page + 1) + '"' + (S.page === pages ? ' disabled' : '') + ' aria-label="Next page">&rarr;</button>';
      pager.innerHTML = h; pager.hidden = false;
    }
    toURL();
    if (scroll) {
      var top = $('.hb2-bar').getBoundingClientRect().top + (window.scrollY || 0) - 100;
      window.scrollTo({ top: top, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
    }
  }

  function toggleTags(open) {
    tagMore.hidden = !open;
    tagTog.setAttribute('aria-expanded', open ? 'true' : 'false');
    tagTog.textContent = open ? 'Show fewer tags' : tagTog.getAttribute('data-all');
  }

  /* ---------------------------------------------------------------- events */
  catBtns.forEach(function (b) {
    b.addEventListener('click', function () { S.topic = b.getAttribute('data-topic'); S.page = 1; render(false); });
  });
  tagLinks.forEach(function (a) {
    a.setAttribute('role', 'button');
    a.addEventListener('click', function (e) {
      if (e.ctrlKey || e.metaKey || e.shiftKey || e.button) return;     // let "open in a new tab" still open the tag page
      e.preventDefault();
      var t = a.getAttribute('data-tag');
      S.tag = S.tag === t ? '' : t; S.page = 1; render(false);
    });
  });
  tagTog.setAttribute('data-all', tagTog.textContent);
  tagTog.addEventListener('click', function () { toggleTags(tagMore.hidden); });
  var timer = 0;
  q.addEventListener('input', function () {
    clearTimeout(timer);
    timer = setTimeout(function () { S.q = q.value.trim().slice(0, 80); S.page = 1; render(false); }, 140);
  });
  sortSel.addEventListener('change', function () { S.sort = sortSel.value; S.page = 1; render(false); });
  pager.addEventListener('click', function (e) {
    var b = e.target.closest('[data-page]');
    if (!b || b.disabled) return;
    S.page = parseInt(b.getAttribute('data-page'), 10); render(true);
    count.focus({ preventScroll: true });
  });
  function clearBy(kind) {
    if (kind === 'topic' || kind === 'all') S.topic = 'all';
    if (kind === 'tag' || kind === 'all') S.tag = '';
    if (kind === 'q' || kind === 'all') { S.q = ''; q.value = ''; }
    S.page = 1; render(false);
  }
  active.addEventListener('click', function (e) { var b = e.target.closest('[data-clear]'); if (b) clearBy(b.getAttribute('data-clear')); });
  d.getElementById('hb2-clear').addEventListener('click', function () { clearBy('all'); });
  ftog.addEventListener('click', function () {
    var o = side.classList.toggle('is-open');
    ftog.setAttribute('aria-expanded', o ? 'true' : 'false');
  });

  fromURL();
  q.value = S.q; sortSel.value = S.sort;
  layout.classList.add('is-ready');
  render(false);
})();
