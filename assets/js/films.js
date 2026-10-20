/* films.js: the swipeable film rail.
   A native scroll-snap row (so touch swipe, trackpad, keyboard and drag all work) with a
   scroll-driven 3D layer on top: each card is placed in depth from its distance to the centre,
   the whole deck gathers and fans out as the section scrolls into view, the playing card tilts
   toward the pointer, and the media inside each card moves slower than the card (parallax).
   Only the centred film plays. The rail loops: three copies of the films sit side by side and the view is
   moved back to the middle copy, unseen, whenever it settles on an outer one, so after the last film the
   first one comes round again (and the other way). */
(function () {
  var root = document.querySelector('[data-vr]');
  if (!root) return;

  var sec = root.closest('.vr'), rail = root.querySelector('.vr__rail'), glow = root.querySelector('.vr__glow');
  var originals = [].slice.call(rail.querySelectorAll('.vr__slide'));
  var N = originals.length;
  function copyOf(s) {
    var c = s.cloneNode(true);
    c.classList.add('is-clone'); c.setAttribute('aria-hidden', 'true');
    ['role', 'aria-roledescription', 'aria-label'].forEach(function (a) { c.removeAttribute(a); });
    [].slice.call(c.querySelectorAll('button')).forEach(function (b) { b.tabIndex = -1; });
    return c;
  }
  if (N > 1) {
    var before = d_frag(), after = d_frag();
    originals.forEach(function (s) { before.appendChild(copyOf(s)); after.appendChild(copyOf(s)); });
    rail.insertBefore(before, originals[0]);
    rail.appendChild(after);
  }
  function d_frag() { return document.createDocumentFragment(); }
  var slides = [].slice.call(rail.querySelectorAll('.vr__slide'));
  // Only the first poster ships in the markup. The rest are 100 KB that would otherwise
  // load with the hero, now that the films sit second on the page, so they wait until the
  // slide is close to view. Without IntersectionObserver they simply all load.
  var pending = [].slice.call(rail.querySelectorAll('video[data-poster]'));
  if (pending.length) {
    var show = function (v) {
      if (v.dataset.poster) { v.poster = v.dataset.poster; delete v.dataset.poster; }
    };
    if ('IntersectionObserver' in window) {
      var po = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) { if (e.isIntersecting) { show(e.target); po.unobserve(e.target); } });
      }, { root: null, rootMargin: '300px' });
      pending.forEach(function (v) { po.observe(v); });
    } else {
      pending.forEach(show);
    }
  }

  var cards = slides.map(function (s) { return s.querySelector('.vr__card'); });
  var vids = slides.map(function (s) { return s.querySelector('video'); });
  var caps = slides.map(function (s) { return s.querySelector('.vr__cap'); });
  var dots = [].slice.call(root.querySelectorAll('.vr__dot'));
  var prev = root.querySelector('.vr__prev'), next = root.querySelector('.vr__next');
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = false; /* pointer-following motion is off: the hero, buttons, cards and films no longer move toward the cursor */

  var cur = -1, wantSound = false, inView = false, ticking = false, settleT = 0, glowT = 0;
  var px = 0, py = 0, pointerIn = false;
  var clamp = function (v, a, b) { return Math.min(b, Math.max(a, v)); };
  var easeOut = function (t) { return 1 - Math.pow(1 - t, 3); };

  if (reduce) sec.classList.add('vr--flat');

  /* ---------------------------------------------------------------- layout pass */
  function frame() {
    ticking = false;
    var n = slides.length, w = slides[0].offsetWidth, rw = rail.clientWidth, sl = rail.scrollLeft;
    var vh = innerHeight, sr = sec.getBoundingClientRect();
    var small = innerWidth < 700;

    // vertical entry: 0 while the section is still below the fold, 1 once its top is a quarter up the screen
    var e = reduce ? 1 : easeOut(clamp((vh - sr.top) / (vh * .78), 0, 1));
    // exit: the deck settles back as the section leaves through the top
    var x = reduce ? 1 : clamp(sr.bottom / (vh * .55), 0, 1);
    var best = 0, bd = 1e9;

    for (var i = 0; i < n; i++) {
      var s = slides[i];
      var c = s.offsetLeft + w / 2 - sl;            // centre of the slide inside the visible rail
      var d = (c - rw / 2) / (w + 28);               // signed distance from the centre, in slide widths
      var a = Math.abs(d);
      if (a < bd) { bd = a; best = i; }
      if (reduce) continue;

      // side cards keep the centre card's shape: no tilt, no depth stretch, only a little smaller and softer
      var rotY = 0;
      var tz = -(1 - e) * 260;
      var tx = -d * w * .66 * (1 - e);               // gathered toward the middle until the section arrives
      var ty = (1 - e) * 70 + (1 - x) * -26;
      var rotX = (1 - e) * 8 + (1 - x) * 4;
      var sc = (1 - Math.min(a, 2.4) * .08) * (.9 + .1 * e) * (.94 + .06 * x);
      var op = clamp((.25 + .75 * e) * (1 - Math.min(a, 2.6) * .2), .18, 1) * (.4 + .6 * x);
      var blur = Math.min(a, 2) * 1.1;

      var tiltX = 0, tiltY = 0;
      if (i === cur && fine && pointerIn && a < .4) { tiltX = -py * 3; tiltY = px * 3.5; }

      cards[i].style.transform = 'translate3d(' + tx.toFixed(1) + 'px,' + ty.toFixed(1) + 'px,' + tz.toFixed(1) + 'px) rotateY(' + (rotY + tiltY).toFixed(2) + 'deg) rotateX(' + (rotX + tiltX).toFixed(2) + 'deg) scale(' + sc.toFixed(3) + ')';
      cards[i].style.opacity = op.toFixed(3);
      /* no blur filter here: it forced a repaint of the playing video on every scrolled frame */
      cards[i].style.setProperty('--shift', clamp(d * -5, -5, 5).toFixed(2) + '%');     // media parallax
      caps[i].style.opacity = (clamp(1 - a * .85, .12, 1) * e).toFixed(3);
      caps[i].style.transform = 'translate3d(0,' + ((1 - e) * 24).toFixed(1) + 'px,0)';
    }

    if (glow && !reduce) glow.style.transform = 'translate3d(0,' + ((.5 - clamp(sr.top / vh, -.5, 1)) * 70).toFixed(1) + 'px,0) scale(' + (1 + (1 - e) * .15).toFixed(3) + ')';
    if (best !== cur) activate(best, false);
  }

  function queue() { if (!ticking) { ticking = true; requestAnimationFrame(frame); } }

  /* ---------------------------------------------------------------- active film */
  function activate(i, user) {
    if (i === cur) return;
    if (cur > -1) { vids[cur].pause(); slides[cur].classList.remove('is-on', 'is-playing'); }
    cur = i;
    slides.forEach(function (s, k) { s.classList.toggle('is-near', Math.abs(k - i) === 1); });
    slides[i].classList.add('is-on');
    var real = ((i % N) + N) % N;
    dots.forEach(function (d, k) { d.classList.toggle('is-on', k === real); d.setAttribute('aria-current', k === real ? 'true' : 'false'); });
    [i - 1, i, i + 1].forEach(function (k) { if (vids[k] && vids[k].preload === 'none') vids[k].preload = 'metadata'; });
    vids[i].muted = !wantSound;
    syncSound();
    if (glow) {
      clearTimeout(glowT); glow.classList.add('sw');
      glowT = setTimeout(function () { glow.style.backgroundImage = 'url(' + vids[i].getAttribute('poster') + ')'; glow.classList.remove('sw'); }, 380);
    }
    clearTimeout(settleT);
    // start playing only once the rail has stopped moving, so a fast swipe never starts five films
    settleT = setTimeout(function () { if (inView && !reduce) play(); }, user ? 120 : 420);
  }

  function play() {
    var v = vids[cur];
    if (!v) return;
    var p = v.play();
    if (p && p.catch) p.catch(function () { slides[cur].classList.remove('is-playing'); });
  }

  function syncSound() {
    slides.forEach(function (s, k) {
      var b = s.querySelector('.vr__snd'), on = k === cur && wantSound;
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      s.classList.toggle('is-sound', on);
    });
  }

  function go(i, instant) {
    i = clamp(i, 0, slides.length - 1);
    var s = slides[i];
    var left = s.offsetLeft + s.offsetWidth / 2 - rail.clientWidth / 2;
    rail.scrollTo({ left: left, behavior: (reduce || instant) ? 'auto' : 'smooth' });
    activate(i, true);
  }

  vids.forEach(function (v, i) {
    v.addEventListener('play', function () { slides[i].classList.add('is-playing'); });
    v.addEventListener('pause', function () { slides[i].classList.remove('is-playing'); });
    v.addEventListener('timeupdate', function () {
      if (v.duration) cards[i].style.setProperty('--p', (v.currentTime / v.duration).toFixed(4));
    });
    v.addEventListener('ended', function () { if (i === cur) go(i + 1 < slides.length ? i + 1 : N); });
  });

  /* ---------------------------------------------------------------- controls */
  var moved = 0;
  slides.forEach(function (s, i) {
    s.querySelector('.vr__tap').addEventListener('click', function (e) {
      if (moved > 6) { e.preventDefault(); return; }
      if (i !== cur) { go(i); return; }
      var v = vids[i];
      if (v.paused) { v.muted = !wantSound; play(); } else { v.pause(); }
    });
    s.querySelector('.vr__snd').addEventListener('click', function (e) {
      e.stopPropagation();
      if (i !== cur) { go(i); return; }
      wantSound = !wantSound; vids[i].muted = !wantSound; syncSound();
      if (vids[i].paused) play();
    });
  });
  dots.forEach(function (d, k) {
    d.addEventListener('click', function () {
      var best = k + N, bd = 1e9;
      [k, k + N, k + 2 * N].forEach(function (c) { var dd = Math.abs(c - cur); if (dd < bd) { bd = dd; best = c; } });
      go(best);
    });
  });
  prev.addEventListener('click', function () { go(cur - 1); });
  next.addEventListener('click', function () { go(cur + 1); });
  rail.addEventListener('keydown', function (e) {
    var k = e.key;
    if (k === 'ArrowRight') { e.preventDefault(); go(cur + 1); }
    else if (k === 'ArrowLeft') { e.preventDefault(); go(cur - 1); }
    else if (k === 'Home') { e.preventDefault(); go(N); }
    else if (k === 'End') { e.preventDefault(); go(2 * N - 1); }
  });

  /* mouse drag (touch and trackpads already scroll natively) */
  var down = false, sx = 0, sl0 = 0;
  rail.addEventListener('pointerdown', function (e) {
    if (e.pointerType !== 'mouse' || e.button !== 0) return;
    down = true; moved = 0; sx = e.clientX; sl0 = rail.scrollLeft;
  });
  addEventListener('pointermove', function (e) {
    if (down) {
      var dx = e.clientX - sx; moved = Math.max(moved, Math.abs(dx));
      if (moved > 6) { rail.classList.add('is-drag'); rail.scrollLeft = sl0 - dx; }
    }
    if (fine) {
      var r = root.getBoundingClientRect();
      px = clamp(((e.clientX - r.left) / r.width - .5) * 2, -1, 1);
      py = clamp(((e.clientY - r.top) / r.height - .5) * 2, -1, 1);
      pointerIn = e.clientX >= r.left && e.clientX <= r.right && e.clientY >= r.top && e.clientY <= r.bottom;
      if (pointerIn && cards[cur]) {
        cards[cur].style.setProperty('--mx', ((px + 1) * 50).toFixed(1) + '%');
        cards[cur].style.setProperty('--my', ((py + 1) * 50).toFixed(1) + '%');
        queue();
      }
    }
  });
  addEventListener('pointerup', function () {
    if (!down) return;
    down = false;
    if (rail.classList.contains('is-drag')) {
      rail.classList.remove('is-drag');
      go(nearest());
      setTimeout(function () { moved = 0; }, 0);
    }
  });
  function nearest() {
    var w = slides[0].offsetWidth, c = rail.scrollLeft + rail.clientWidth / 2, b = 0, bd = 1e9;
    slides.forEach(function (s, i) { var d = Math.abs(s.offsetLeft + w / 2 - c); if (d < bd) { bd = d; b = i; } });
    return b;
  }

  /* ---------------------------------------------------------------- visibility and scroll */
  new IntersectionObserver(function (es) {
    inView = es[0].isIntersecting && es[0].intersectionRatio > .35;
    if (cur < 0) return;
    if (inView) { if (!reduce) play(); } else { vids[cur].pause(); }
  }, { threshold: [0, .35, .6] }).observe(root);
  document.addEventListener('visibilitychange', function () {
    if (document.hidden) { if (cur > -1) vids[cur].pause(); } else if (inView && !reduce && cur > -1) { play(); }
  });

  /* the loop: when the rail settles on an outer copy, jump to the same film in the middle copy */
  var endT = 0;
  function recentre() {
    if (N < 2 || cur < 0 || down) return;
    var t = cur < N ? cur + N : cur >= 2 * N ? cur - N : -1;
    if (t < 0) return;
    var from = vids[cur], to = vids[t], playing = !from.paused;
    try { to.currentTime = from.currentTime; } catch (err) {}
    from.pause();
    var s = slides[t];
    rail.style.scrollSnapType = 'none';
    rail.scrollLeft = s.offsetLeft + s.offsetWidth / 2 - rail.clientWidth / 2;
    rail.style.scrollSnapType = '';
    activate(t, true);
    if (playing && inView && !reduce) play();
    queue();
  }
  rail.addEventListener('scroll', function () { clearTimeout(endT); endT = setTimeout(recentre, 170); }, { passive: true });
  rail.addEventListener('scroll', queue, { passive: true });
  addEventListener('scroll', queue, { passive: true });
  addEventListener('resize', function () { go(cur < 0 ? N : cur, true); queue(); });

  /* start on the first film (of the middle copy), centred */
  go(N, true);
  frame();
  requestAnimationFrame(function () { go(N, true); frame(); });
})();
