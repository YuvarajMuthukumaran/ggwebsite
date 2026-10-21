/* "More videos" carousel: a gentle continuous auto-scroll, paused by hover/touch/drag/focus;
   prev/next buttons and a slim progress bar instead of a plain scrollbar; mouse drag-to-scroll;
   and a scroll-reveal (heading, then each card staggered) the first time the section is seen.
   Reduced motion: no auto-scroll, no reveal transition (CSS shows everything immediately), the
   row is still a plain scrollable/draggable list. */
(function () {
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  [].forEach.call(document.querySelectorAll('.sec.yts'), function (sec) {
    var head = sec.querySelector('.head');
    var wrap = sec.querySelector('.ytl__wrap');
    if (!wrap) return;
    var row = wrap.querySelector('.ytl');
    var prev = sec.querySelector('.ytl__nav--prev');
    var next = sec.querySelector('.ytl__nav--next');
    var bar = sec.querySelector('.ytl__prog-b');
    var items = [].slice.call(row.children);

    // reveal once, on first approach
    var io = new IntersectionObserver(function (entries, obs) {
      if (!entries[0].isIntersecting) return;
      if (head) head.classList.add('is-in');
      row.classList.add('is-in');
      obs.disconnect();
    }, { rootMargin: '0px 0px -10% 0px' });
    io.observe(sec);

    // paused whenever the pointer, focus or a drag is anywhere on the carousel. A click on
    // prev/next pauses it directly first (not just on the hover event that preceded the
    // click), so the auto-scroll's own scrollLeft writes -- every frame -- can never cancel
    // the button's smooth-scroll animation mid-flight; it un-pauses the normal way, once the
    // pointer actually leaves, or after a timeout for a keyboard click with no pointer at all.
    var hold = false, holdTimer = null;
    function pause(ms) {
      hold = true; clearTimeout(holdTimer);
      if (ms) holdTimer = setTimeout(function () { hold = false; }, ms);
    }

    function step() { return (items[0] ? items[0].getBoundingClientRect().width : 300) + 20; }
    function updateNav() {
      if (prev) prev.disabled = row.scrollLeft <= 2;
      if (next) next.disabled = row.scrollLeft >= row.scrollWidth - row.clientWidth - 2;
      if (bar) {
        var max = row.scrollWidth - row.clientWidth;
        var frac = max > 0 ? row.scrollLeft / max : 0;
        var w = Math.max(12, (row.clientWidth / row.scrollWidth) * 100);
        bar.style.width = w + '%';
        bar.style.transform = 'translateX(' + (frac * (100 / w - 1) * 100) + '%)';
      }
    }
    row.addEventListener('scroll', updateNav, { passive: true });
    if (prev) prev.addEventListener('click', function () { pause(); row.scrollBy({ left: -step(), behavior: 'smooth' }); });
    if (next) next.addEventListener('click', function () { pause(); row.scrollBy({ left: step(), behavior: 'smooth' }); });
    new ResizeObserver(updateNav).observe(row);
    updateNav();

    // mouse drag-to-scroll (touch already scrolls natively)
    var dragging = false, startX = 0, startLeft = 0, moved = false;
    row.addEventListener('pointerdown', function (e) {
      if (e.pointerType === 'touch') return;
      dragging = true; moved = false; startX = e.clientX; startLeft = row.scrollLeft;
    });
    row.addEventListener('pointermove', function (e) {
      if (!dragging) return;
      var dx = e.clientX - startX;
      if (!moved && Math.abs(dx) > 4) { moved = true; row.classList.add('is-drag'); try { row.setPointerCapture(e.pointerId); } catch (_) {} }
      if (moved) { row.scrollLeft = startLeft - dx; }
    });
    function endDrag() { dragging = false; row.classList.remove('is-drag'); }
    row.addEventListener('pointerup', endDrag);
    row.addEventListener('pointercancel', endDrag);
    row.addEventListener('click', function (e) { if (moved) { e.preventDefault(); e.stopPropagation(); } }, true);

    if (reduce) return;

    // gentle continuous auto-scroll, paused on hover/touch/focus/drag anywhere on the carousel
    var on = true;
    wrap.addEventListener('mouseenter', function () { pause(0); });
    wrap.addEventListener('mouseleave', function () { if (!dragging) hold = false; });
    wrap.addEventListener('touchstart', function () { pause(0); }, { passive: true });
    wrap.addEventListener('focusin', function () { pause(0); });
    wrap.addEventListener('focusout', function () { if (!dragging) hold = false; });
    new IntersectionObserver(function (e) { on = e[0].isIntersecting; }).observe(row);
    function tick() {
      if (on && !hold && !dragging) {
        row.scrollLeft += 0.6;
        if (row.scrollLeft + row.clientWidth >= row.scrollWidth - 1) row.scrollLeft = 0;
      }
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  });
})();
