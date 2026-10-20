/* faq-index.js: the /faq/ page (tools/faq_pages.py). Every question is already in the page. This searches them as you type,
   filters by topic, opens the answers, and keeps the search and topic in the address (?q=&topic=) so a view can be shared.
   Without it the page is the full list, and the topics are plain links to their own pages. */
(function () {
  'use strict';
  var d = document;
  var root = d.querySelector('.fh');
  if (!root) return;

  var $ = function (s, c) { return (c || d).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || d).querySelectorAll(s)); };

  var input = d.getElementById('fh-q'), clear = $('.fh-search__x'), count = d.getElementById('fh-count');
  var active = d.getElementById('fh-active'), empty = d.getElementById('fh-empty'), tog = d.getElementById('fh-tog');
  var groups = $$('.fh-g'), items = $$('.fh-q'), topicLinks = $$('.fh-topics a'), tries = $$('[data-try]');
  var total = items.length;
  var label = {};
  topicLinks.forEach(function (a) { label[a.getAttribute('data-topic')] = a.firstChild.textContent.trim(); });
  var titles = items.map(function (q) { return $('.fh-q__t', q); });
  var plainTitle = titles.map(function (t) { return t.textContent; });

  var S = { q: '', topic: 'all' };

  function esc(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  function words() { return S.q.toLowerCase().split(/\s+/).filter(Boolean); }
  var reCache = {};
  function wordRe(w) {                       // "fee" finds fee and fees, not feel; longer words match the start of a word
    if (reCache[w]) return reCache[w];
    var e = w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    return (reCache[w] = new RegExp('(^|[^a-z0-9])(' + e + (w.length <= 3 ? 's?(?![a-z0-9])' : '') + ')', 'ig'));
  }
  function has(text, w) { var re = wordRe(w); re.lastIndex = 0; return re.test(text); }

  function fromURL() {
    var p = new URLSearchParams(location.search);
    S.q = (p.get('q') || '').slice(0, 80);
    S.topic = label[p.get('topic')] ? p.get('topic') : 'all';
  }
  function toURL() {
    var p = new URLSearchParams();
    if (S.q) p.set('q', S.q);
    if (S.topic !== 'all') p.set('topic', S.topic);
    var s = p.toString();
    try { history.replaceState(null, '', location.pathname + (s ? '?' + s : '')); } catch (e) {}
  }

  function mark(text, ws) {
    var ranges = [];
    ws.forEach(function (w) {
      var re = wordRe(w), m;
      re.lastIndex = 0;
      while ((m = re.exec(text.toLowerCase())) !== null) {
        var start = m.index + m[1].length;
        ranges.push([start, start + m[2].length]);
        if (m[0].length === 0) re.lastIndex++;
      }
    });
    if (!ranges.length) return esc(text);
    ranges.sort(function (x, y) { return x[0] - y[0]; });
    var merged = [ranges[0]];
    ranges.slice(1).forEach(function (r) { var l = merged[merged.length - 1]; if (r[0] <= l[1]) l[1] = Math.max(l[1], r[1]); else merged.push(r); });
    var out = '', pos = 0;
    merged.forEach(function (r) { out += esc(text.slice(pos, r[0])) + '<mark>' + esc(text.slice(r[0], r[1])) + '</mark>'; pos = r[1]; });
    return out + esc(text.slice(pos));
  }

  function render(auto) {
    var ws = words(), shown = 0;
    items.forEach(function (q, i) {
      var g = q.parentNode.parentNode;
      var ok = (S.topic === 'all' || g.getAttribute('data-topic') === S.topic) && ws.every(function (w) { return has(q.getAttribute('data-q'), w); });
      q.hidden = !ok;
      titles[i].innerHTML = ok && ws.length ? mark(plainTitle[i], ws) : esc(plainTitle[i]);
      if (ok) shown++;
    });
    groups.forEach(function (g) {
      g.hidden = !$$('.fh-q', g).some(function (q) { return !q.hidden; });
    });
    if (auto && ws.length && shown > 0 && shown <= 3) items.forEach(function (q) { if (!q.hidden) q.open = true; });   // a few matches: show their answers

    topicLinks.forEach(function (a) {
      var on = a.getAttribute('data-topic') === S.topic;
      a.classList.toggle('is-on', on);
      a.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    count.textContent = shown === 0 ? 'No questions' : (shown === total ? total + ' questions' : 'Showing ' + shown + ' of ' + total + ' questions');
    var pills = '';
    if (S.topic !== 'all') pills += '<button type="button" class="fh-pill" data-clear="topic">' + esc(label[S.topic]) + ' <span aria-hidden="true">&times;</span><span class="fh-sr">remove filter</span></button>';
    if (S.q) pills += '<button type="button" class="fh-pill" data-clear="q">Search: &ldquo;' + esc(S.q) + '&rdquo; <span aria-hidden="true">&times;</span><span class="fh-sr">remove search</span></button>';
    active.innerHTML = pills;
    active.hidden = !pills;
    empty.hidden = shown > 0;
    clear.hidden = !S.q;
    var all = items.filter(function (q) { return !q.hidden; });
    var open = all.length > 0 && all.every(function (q) { return q.open; });
    tog.textContent = open ? 'Collapse all' : 'Expand all';
    tog.setAttribute('aria-pressed', open ? 'true' : 'false');
    toURL();
  }

  /* ---------------------------------------------------------------- events */
  var timer = 0;
  input.addEventListener('input', function () {
    clearTimeout(timer);
    timer = setTimeout(function () { S.q = input.value.trim().slice(0, 80); render(true); }, 120);
  });
  clear.addEventListener('click', function () { input.value = ''; S.q = ''; render(true); input.focus(); });
  tries.forEach(function (b) {
    b.addEventListener('click', function () {
      input.value = b.getAttribute('data-try'); S.q = input.value; S.topic = 'all'; render(true);
      var top = $('.fh').getBoundingClientRect().top + (window.scrollY || 0) - 90;
      window.scrollTo({ top: top, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
    });
  });
  topicLinks.forEach(function (a) {
    a.addEventListener('click', function (e) {
      if (e.ctrlKey || e.metaKey || e.shiftKey || e.button) return;     // "open in a new tab" still opens the topic page
      e.preventDefault();
      S.topic = a.getAttribute('data-topic'); render(true);
    });
  });
  active.addEventListener('click', function (e) {
    var b = e.target.closest('[data-clear]');
    if (!b) return;
    if (b.getAttribute('data-clear') === 'topic') S.topic = 'all'; else { S.q = ''; input.value = ''; }
    render(true);
  });
  d.getElementById('fh-clear').addEventListener('click', function () { S.q = ''; S.topic = 'all'; input.value = ''; render(true); });
  tog.addEventListener('click', function () {
    var open = tog.getAttribute('aria-pressed') !== 'true';
    items.forEach(function (q) { if (!q.hidden) q.open = open; });
    render(false);
  });
  items.forEach(function (q) { q.addEventListener('toggle', function () { clearTimeout(timer); timer = setTimeout(function () { render(false); }, 0); }); });

  fromURL();
  input.value = S.q;
  root.classList.add('is-ready');
  d.documentElement.classList.add('fh-ready');
  render(true);
})();
