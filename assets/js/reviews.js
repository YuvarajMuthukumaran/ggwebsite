/* Reviews: two rows that drift in opposite directions. Drag, wheel, arrows and keys all
   steer the same motion; hover or focus eases it to a stop. Cards near the middle of the
   screen sit slightly larger. Reduced motion gets a plain scrollable row instead. */
(function () {
  var root = document.querySelector('[data-rvm]');
  if (!root) return;
  var rows = [].slice.call(root.querySelectorAll('.rvm__row'));
  var still = matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (still) { root.classList.add('rvm--still'); return; }
  root.classList.add('rvm--live');

  var BASE = 34;                 // px per second
  var state = rows.map(function (row) {
    var track = row.querySelector('.rvm__track');
    var originals = [].slice.call(track.children);
    var gap = parseFloat(getComputedStyle(track).columnGap) || 0;
    var s = { row: row, track: track, originals: originals, dir: +row.dataset.dir || 1, x: 0, v: 0, speed: BASE, hold: false, drag: false, setW: 0, cards: originals.slice(), visible: true };
    build(s, gap);
    return s;
  });

  function build(s, gap) {
    var first = s.originals[0], lastO = s.originals[s.originals.length - 1];
    s.setW = lastO.offsetLeft + lastO.offsetWidth + gap - first.offsetLeft;
    var need = Math.ceil((s.row.clientWidth * 2) / s.setW) + 1, i, j;
    for (i = 0; i < need; i++) {
      for (j = 0; j < s.originals.length; j++) {
        var c = s.originals[j].cloneNode(true);
        c.setAttribute('aria-hidden', 'true');
        s.track.appendChild(c);
        s.cards.push(c);
      }
    }
    s.x = s.dir > 0 ? 0 : s.setW * 0.5;
  }

  function wrap(s) { s.x = ((s.x % s.setW) + s.setW) % s.setW; }

  var last = performance.now();
  function frame(now) {
    var dt = Math.min((now - last) / 1000, 0.05); last = now;
    state.forEach(function (s) {
      if (!s.visible) return;
      var target = (s.hold || s.drag) ? 0 : BASE;
      s.speed += (target - s.speed) * Math.min(1, dt * 4);          // ease to a stop and back
      if (!s.drag) { s.x += (s.speed * s.dir + s.v) * dt; s.v *= Math.exp(-dt * 3.2); }
      if (Math.abs(s.v) < 0.5) s.v = 0;
      wrap(s);
      s.track.style.transform = 'translate3d(' + (-s.x).toFixed(2) + 'px,0,0)';
      var rect = s.row.getBoundingClientRect(), mid = rect.left + rect.width / 2, half = rect.width / 2;
      for (var i = 0; i < s.cards.length; i++) {
        var c = s.cards[i], cr = c.getBoundingClientRect(), d = Math.abs(cr.left + cr.width / 2 - mid) / half;
        d = d > 1 ? 1 : d;
        c.style.transform = 'scale(' + (1 - d * d * 0.07).toFixed(3) + ')';
        c.style.opacity = (1 - d * d * 0.35).toFixed(3);
      }
    });
    requestAnimationFrame(frame);
  }

  state.forEach(function (s) {
    var row = s.row, px = 0, t0 = 0, moved = false, id = null;
    row.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse') s.hold = true; });
    row.addEventListener('pointerleave', function (e) { if (e.pointerType === 'mouse' && !s.drag) s.hold = false; });
    row.addEventListener('focusin', function () { s.hold = true; });
    row.addEventListener('focusout', function () { s.hold = false; });
    row.addEventListener('pointerdown', function (e) {
      if (e.button) return;
      s.drag = true; moved = false; px = e.clientX; t0 = performance.now(); id = e.pointerId; s.v = 0;
    });
    row.addEventListener('pointermove', function (e) {
      if (!s.drag) return;
      var dx = e.clientX - px;
      if (!moved && Math.abs(dx) < 4) return;
      if (!moved) { moved = true; try { row.setPointerCapture(id); } catch (_) {} row.classList.add('is-drag'); }
      var now = performance.now(), dt = Math.max((now - t0) / 1000, 0.008);
      s.x -= dx; s.vel = -dx / dt; px = e.clientX; t0 = now; wrap(s);
    });
    function end() {
      if (!s.drag) return;
      s.drag = false; row.classList.remove('is-drag');
      if (moved) s.v = Math.max(-2200, Math.min(2200, (s.vel || 0))) - s.speed * s.dir * 0;
      s.hold = row.matches(':hover');
    }
    row.addEventListener('pointerup', end);
    row.addEventListener('pointercancel', end);
    row.addEventListener('wheel', function (e) {
      if (Math.abs(e.deltaX) > Math.abs(e.deltaY)) { e.preventDefault(); s.x += e.deltaX; wrap(s); }
    }, { passive: false });
    row.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { s.v += 900; e.preventDefault(); }
      if (e.key === 'ArrowLeft') { s.v -= 900; e.preventDefault(); }
    });
    new IntersectionObserver(function (en) { s.visible = en[0].isIntersecting; }, { rootMargin: '200px' }).observe(row);
  });

  [].forEach.call(root.querySelectorAll('.rvm__b'), function (b) {
    b.addEventListener('click', function () {
      var d = +b.dataset.dir;
      state.forEach(function (s) { s.v += d * 1100; });
    });
  });

  document.addEventListener('visibilitychange', function () { last = performance.now(); });
  requestAnimationFrame(frame);
})();
