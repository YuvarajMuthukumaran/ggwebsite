/* service.js: the "On this page" list on condition, local and guide pages follows the scroll.
   The heading nearest the top of the screen is marked in the list (aria-current), and the list scrolls to keep it in view. */
(function () {
  'use strict';
  var toc = document.querySelector('.sp-toc');
  if (!toc || !('IntersectionObserver' in window)) return;

  var links = [].slice.call(toc.querySelectorAll('a[href^="#"]'));
  var map = {};
  links.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
  var heads = Object.keys(map).map(function (id) { return document.getElementById(id); }).filter(Boolean);
  if (!heads.length) return;

  var current = null, visible = {};
  function mark(id) {
    if (current === id) return;
    current = id;
    links.forEach(function (a) { a.removeAttribute('aria-current'); });
    var a = map[id];
    if (!a) return;
    a.setAttribute('aria-current', 'true');
    var list = a.closest('ol');
    if (list && list.scrollHeight > list.clientHeight) {
      var top = a.offsetTop - list.clientHeight / 2 + a.offsetHeight / 2;
      list.scrollTo({ top: top, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
    }
  }

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { visible[e.target.id] = e.isIntersecting; });
    // the first heading (in page order) that is inside the band near the top; otherwise the last one above it
    var inBand = heads.filter(function (h) { return visible[h.id]; });
    if (inBand.length) { mark(inBand[0].id); return; }
    var above = heads.filter(function (h) { return h.getBoundingClientRect().top < 0; });
    if (above.length) mark(above[above.length - 1].id);
  }, { rootMargin: '-90px 0px -62% 0px' });
  heads.forEach(function (h) { io.observe(h); });
})();
