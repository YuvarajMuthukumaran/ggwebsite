/* journey.js: the animated journey timeline (home and About). Nothing here is clickable.
   Two things happen, both gentle:
   1. Entrance. Each milestone is shown once as it scrolls into view (the CSS staggers its marker, label,
      heading, rule, text and tags). Milestones that arrive together are staggered; ones already scrolled
      past are simply shown.
   2. Progress. A line fills down the timeline with the scroll and a small dot travels along it, eased so it
      glides rather than snaps; each marker lights up as the dot reaches it, and the latest one carries a halo.
      Only transforms are written each frame, and the loop stops as soon as the dot has settled.
   Nothing is hidden unless this script is running (html.js in the CSS). With reduced motion the finished
   timeline is shown as it is. */
(function () {
  var wrap = document.querySelector('.jt-w');
  if (!wrap) return;

  var items = [].slice.call(wrap.querySelectorAll('.jt__i'));
  var fills = items.map(function (li) { return li.querySelector('.jt__ln i'); });
  var dot = wrap.querySelector('.jt__dot');
  var clamp = function (v, a, b) { return Math.min(b, Math.max(a, v)); };

  if (!document.documentElement.classList.contains('js')) {
    items.forEach(function (li) { li.classList.add('in', 'is-reached'); });
    return;
  }

  /* ---------------------------------------------------------------- entrance */
  var STEP = .45;                                   // seconds between milestones that arrive together
  function show(list) {
    var wait = 0;
    list.forEach(function (li) {
      li.style.setProperty('--d', wait.toFixed(2) + 's');
      li.classList.add('in');
      wait += STEP;
    });
  }
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      var seen = [], past = [];
      entries.forEach(function (e) {
        if (e.isIntersecting) seen.push(e.target);
        else if (e.boundingClientRect.top < 0) past.push(e.target);
        else return;
        io.unobserve(e.target);
      });
      var order = function (a, b) { return items.indexOf(a) - items.indexOf(b); };
      past.forEach(function (li) { li.style.setProperty('--d', '0s'); li.classList.add('in'); });
      show(seen.sort(order));
    }, { rootMargin: '0px 0px -12% 0px' });
    items.forEach(function (li) { io.observe(li); });
  } else { show(items); }

  /* ---------------------------------------------------------------- progress */
  var n = 44, ys = [], vh = innerHeight, cur = 0, target = 0, running = false, lastT = 0, lastKey = '';

  function measure() {                              // marker centres, from the top of the timeline
    n = items[0].querySelector('.jt__n').offsetHeight;
    ys = items.map(function (li) { return li.offsetTop + n / 2; });
  }

  function paint() {
    var now = -1, key = '';
    for (var i = 0; i < items.length; i++) {
      if (fills[i]) {
        var s = ys[i] + n / 2 + 6, e = ys[i + 1] - n / 2 - 6;
        fills[i].style.transform = 'scaleY(' + clamp((cur - s) / (e - s), 0, 1).toFixed(4) + ')';
      }
      if (cur >= ys[i] - 1) now = i;
    }
    dot.style.transform = 'translate3d(0,' + (cur - 6).toFixed(1) + 'px,0)';
    key = String(now);
    if (key !== lastKey) {
      lastKey = key;
      items.forEach(function (li, i) { li.classList.toggle('is-reached', i <= now); li.classList.toggle('is-now', i === now); });
    }
  }

  function frame(t) {
    var dt = lastT ? Math.min(60, t - lastT) : 16;
    lastT = t;
    target = clamp(vh * .6 - wrap.getBoundingClientRect().top, ys[0], ys[ys.length - 1]);
    cur += (target - cur) * (1 - Math.exp(-dt / 260));       // time-based easing: the same glide at any frame rate
    if (Math.abs(target - cur) < .4) cur = target;
    paint();
    if (cur !== target) requestAnimationFrame(frame); else { running = false; lastT = 0; }
  }
  function wake() { if (!running) { running = true; requestAnimationFrame(frame); } }

  measure();
  cur = ys[0];
  paint();
  wrap.classList.add('is-live');
  addEventListener('scroll', wake, { passive: true });
  addEventListener('resize', function () { vh = innerHeight; measure(); wake(); });
  addEventListener('load', function () { measure(); wake(); });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { measure(); wake(); });
  wake();
})();
