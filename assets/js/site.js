/* Dr. Gorav Gupta — behaviour and motion. No dependencies.
 *
 * Two kinds of code live here:
 *   - behaviour (menu, tabs, FAQ, carousel) always runs
 *   - motion runs only when <html> has .js, which the head script sets
 *     unless the visitor prefers reduced motion.
 */
(function () {
  'use strict';

  var d = document, root = d.documentElement;
  root.classList.add('ready');                       // tells the head failsafe that JS is alive

  var motion = root.classList.contains('js');
  var fine = matchMedia('(hover: hover) and (pointer: fine)').matches;

  var $ = function (s, c) { return (c || d).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || d).querySelectorAll(s)); };
  var clamp = function (v, a, b) { return Math.min(b == null ? 1 : b, Math.max(a == null ? 0 : a, v)); };

  var nav = $('#nav'), bar = $('#bar'), sticky = $('.sticky');
  var hero = $('.hero'), heroIn = $('.hero__in'), glow = $('.hero__glow');
  var film = $('.film'), tl = $('.tl'), aurora = $('.aurora');

  /* ------------------------------------------------------------------ *
   * 1. Split headings into words (and the name into letters).
   *    The original text stays in a visually hidden span for screen readers.
   * ------------------------------------------------------------------ */
  function split(el, chars) {
    var text = el.textContent.replace(/\s+/g, ' ').trim(), k = 0;
    var sr = d.createElement('span'); sr.className = 'sr'; sr.textContent = text;
    var vis = d.createElement('span'); vis.className = 'sp'; vis.setAttribute('aria-hidden', 'true');
    text.split(' ').forEach(function (w, i, all) {
      var wd = d.createElement('span'); wd.className = 'wd';
      if (chars) {
        Array.from(w).forEach(function (c) {
          var ch = d.createElement('span'); ch.className = 'ch'; ch.textContent = c;
          ch.style.setProperty('--k', k++); wd.appendChild(ch);
        });
      } else {
        var s = d.createElement('span'); s.textContent = w; s.style.setProperty('--k', k++); wd.appendChild(s);
      }
      vis.appendChild(wd);
      if (i < all.length - 1) vis.appendChild(d.createTextNode(' '));
    });
    el.textContent = ''; el.appendChild(sr); el.appendChild(vis);
  }

  var words = [];
  if (motion) {
    $$('.giant').forEach(function (h) { split(h, true); });
    $$('.head h2, .calm h2, .book h2').forEach(function (h) { split(h, false); });

    // the pinned sentence: each word is lit by scroll position
    var bq = $('.film blockquote');
    if (bq) {
      var cite = $('cite', bq), tn = bq.firstChild;
      if (tn && tn.nodeType === 3) {
        var text = tn.textContent.replace(/\s+/g, ' ').trim();
        var sr = d.createElement('span'); sr.className = 'sr'; sr.textContent = text;
        var vis = d.createElement('span'); vis.setAttribute('aria-hidden', 'true');
        text.split(' ').forEach(function (w, i, all) {
          var s = d.createElement('span'); s.className = 'fw'; s.textContent = w; vis.appendChild(s); words.push(s);
          if (i < all.length - 1) vis.appendChild(d.createTextNode(' '));
        });
        bq.insertBefore(vis, cite); bq.insertBefore(sr, vis); bq.removeChild(tn);
      }
    }
  }

  /* stagger siblings that have no explicit order */
  $$('.presses .press, .faq details, .tl li, .rooms > div').forEach(function (el, i) {
    if (!el.style.getPropertyValue('--i')) el.style.setProperty('--i', i % 5);
  });

  /* ------------------------------------------------------------------ *
   * 2. Reveal on scroll
   * ------------------------------------------------------------------ */
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (!e.isIntersecting) return;
      var el = e.target; el.classList.add('in'); io.unobserve(el);
      setTimeout(function () { el.classList.add('done'); }, 2400);
    });
  }, { threshold: .12, rootMargin: '0px 0px -6% 0px' });
  $$('.reveal').forEach(function (n) { io.observe(n); });

  /* ------------------------------------------------------------------ *
   * 3. Counters
   * ------------------------------------------------------------------ */
  function countTo(el, n, suffix, delay) {
    if (!motion) { el.textContent = n + suffix; return; }
    var t0 = performance.now() + (delay || 0);
    (function f(now) {
      if (now >= t0) {
        var p = clamp((now - t0) / 1800);
        el.textContent = Math.round(n * (1 - Math.pow(1 - p, 3))) + suffix;
        if (p >= 1) return;
      }
      requestAnimationFrame(f);
    })(performance.now());
  }
  if (motion) $$('[data-n]').forEach(function (el) { el.textContent = '0' + (el.dataset.s || ''); });
  var co = new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (!e.isIntersecting) return;
      co.unobserve(e.target);
      countTo(e.target, +e.target.dataset.n, e.target.dataset.s || '', 250);
    });
  }, { threshold: .6 });
  $$('[data-n]').forEach(function (n) { co.observe(n); });
  var heroCount = $('[data-count]');
  if (motion && heroCount) heroCount.textContent = '0+';

  /* ------------------------------------------------------------------ *
   * 4. Scroll engine: one rAF-throttled pass for every scroll-linked effect
   * ------------------------------------------------------------------ */
  var vh = innerHeight, heroEnd = 0, ticking = false, heroDone = false;
  var par = $$('[data-par]');
  // parallax targets (set here so markup stays clean)
  $$('.about figure img').forEach(function (i) { i.dataset.par = 24; par.push(i); });
  $$('.m-photo > img, .m-award > img').forEach(function (i) { i.dataset.par = 16; par.push(i); });
  var tlItems = tl ? $$('li', tl) : [];

  function measure() { vh = innerHeight; if (hero) heroEnd = hero.offsetTop + hero.offsetHeight; }

  function frame() {
    ticking = false;
    var y = window.scrollY, max = root.scrollHeight - vh;
    bar.style.transform = 'scaleX(' + (max > 0 ? y / max : 0) + ')';
    nav.classList.toggle('on', y > 20);
    if (sticky) sticky.classList.toggle('show', y > 520);
    if (!motion) return;

    // hero exit
    if (hero) {
      if (y < heroEnd) { hero.style.setProperty('--p', clamp(y / (heroEnd - 120)).toFixed(4)); heroDone = false; }
      else if (!heroDone) { hero.style.setProperty('--p', 1); heroDone = true; }
    }

    // pinned philosophy scene
    if (film) {
      var r = film.getBoundingClientRect();
      if (r.bottom > -vh * .2 && r.top < vh * 1.2) {
        var prog = clamp(-r.top / (r.height - vh));
        film.style.setProperty('--prog', prog.toFixed(4));
        film.style.setProperty('--enter', clamp((vh - r.top) / (vh * .9)).toFixed(3));
        var n = words.length, t = clamp((prog - .05) / .8) * (n + 2);
        for (var i = 0; i < n; i++) {
          var v = clamp(t - i);
          words[i].style.setProperty('--o', (.14 + .86 * v * v * (3 - 2 * v)).toFixed(3));
        }
      }
    }

    // journey line + dots
    if (tl) {
      var tr = tl.getBoundingClientRect();
      if (tr.bottom > -50 && tr.top < vh + 50) {
        var line = vh * .62;
        tl.style.setProperty('--prog', clamp((line - tr.top) / tr.height).toFixed(4));
        tlItems.forEach(function (li) { li.classList.toggle('on', li.getBoundingClientRect().top < line); });
      }
    }

    // image parallax
    par.forEach(function (el) {
      var pr = el.parentElement.getBoundingClientRect();
      if (pr.bottom < -60 || pr.top > vh + 60) return;
      var k = (pr.top + pr.height / 2 - vh / 2) / (vh / 2 + pr.height / 2);
      el.style.setProperty('--py', (clamp(k, -1, 1) * -el.dataset.par).toFixed(1) + 'px');
    });

    if (aurora) aurora.style.setProperty('--sy', y);
  }
  function queue() { if (!ticking) { ticking = true; requestAnimationFrame(frame); } }
  addEventListener('scroll', queue, { passive: true });
  addEventListener('resize', function () { measure(); movePill(); queue(); });
  addEventListener('load', function () { measure(); queue(); });
  measure(); frame();

  /* ------------------------------------------------------------------ *
   * 5. Hero depth: pointer-driven parallax with eased follow
   * ------------------------------------------------------------------ */
  if (motion && fine && hero) {
    var tx = 0, ty = 0, cx = 0, cy = 0, gx = 0, gy = 0, tgx = 0, tgy = 0, raf = 0;
    var follow = function () {
      cx += (tx - cx) * .07; cy += (ty - cy) * .07; gx += (tgx - gx) * .1; gy += (tgy - gy) * .1;
      hero.style.setProperty('--mx', cx.toFixed(4)); hero.style.setProperty('--my', cy.toFixed(4));
      if (glow) glow.style.transform = 'translate3d(' + gx.toFixed(1) + 'px,' + gy.toFixed(1) + 'px,0)';
      raf = (Math.abs(tx - cx) + Math.abs(ty - cy) + Math.abs(tgx - gx) + Math.abs(tgy - gy) > .01) ? requestAnimationFrame(follow) : 0;
    };
    addEventListener('pointermove', function (e) {
      if (window.scrollY > heroEnd) return;
      tx = (e.clientX / innerWidth - .5) * 2; ty = (e.clientY / innerHeight - .5) * 2;
      var r = heroIn.getBoundingClientRect(); tgx = e.clientX - r.left; tgy = e.clientY - r.top;
      if (!raf) raf = requestAnimationFrame(follow);
    }, { passive: true });
  }

  /* ------------------------------------------------------------------ *
   * 6. Micro-interactions: spotlight, tilt, magnetic buttons
   * ------------------------------------------------------------------ */
  if (motion && fine) {
    $$('.svc, .rec, .press, .mt, .rooms > div').forEach(function (el) {
      var s = d.createElement('span'); s.className = 'spot'; s.setAttribute('aria-hidden', 'true'); el.insertBefore(s, el.firstChild);
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect();
        el.style.setProperty('--sx', (e.clientX - r.left) + 'px'); el.style.setProperty('--sy', (e.clientY - r.top) + 'px');
      });
    });
    $$('.svc:not(.cta-card), .mt').forEach(function (el) {
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
        el.style.transform = 'perspective(900px) rotateX(' + (-y * 5).toFixed(2) + 'deg) rotateY(' + (x * 6).toFixed(2) + 'deg)';
      });
      el.addEventListener('pointerleave', function () { el.style.transform = ''; });
    });
    $$('.btn, .arrows button').forEach(function (b) {
      b.addEventListener('pointermove', function (e) {
        var r = b.getBoundingClientRect();
        b.style.translate = ((e.clientX - r.left - r.width / 2) * .22).toFixed(1) + 'px ' + ((e.clientY - r.top - r.height / 2) * .3).toFixed(1) + 'px';
      });
      b.addEventListener('pointerleave', function () { b.style.translate = ''; });
    });
  }

  /* ------------------------------------------------------------------ *
   * 7. Navigation: menu, scroll-spy, gliding pill, cinematic anchor scroll
   * ------------------------------------------------------------------ */
  var burger = $('#burger'), links = $('#links');
  function closeMenu() { nav.classList.remove('open'); burger.setAttribute('aria-expanded', 'false'); }
  burger.addEventListener('click', function () { burger.setAttribute('aria-expanded', nav.classList.toggle('open') ? 'true' : 'false'); });
  addEventListener('keydown', function (e) { if (e.key === 'Escape') closeMenu(); });

  var pill = d.createElement('span'); pill.className = 'nav-pill'; pill.setAttribute('aria-hidden', 'true'); links.insertBefore(pill, links.firstChild);
  var L = {}, active = null, navLinks = $$('a', links);
  navLinks.forEach(function (a) { L[a.getAttribute('href').slice(1)] = a; });
  function place(a) {
    if (!a) { pill.classList.remove('on'); return; }
    pill.style.width = (a.offsetWidth + 26) + 'px'; pill.style.height = (a.offsetHeight + 12) + 'px';
    pill.style.top = (a.offsetTop - 6) + 'px'; pill.style.translate = (a.offsetLeft - 13) + 'px 0';
    pill.classList.add('on');
  }
  function movePill() { place(active); }
  navLinks.forEach(function (a) { a.addEventListener('pointerenter', function () { place(a); }); });
  links.addEventListener('pointerleave', movePill);

  var so = new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (!e.isIntersecting) return;
      navLinks.forEach(function (a) { a.classList.remove('act'); });
      active = L[e.target.id] || null;
      if (active) active.classList.add('act');
      movePill();
    });
  }, { rootMargin: '-45% 0px -50% 0px' });
  Object.keys(L).forEach(function (k) { var n = d.getElementById(k); if (n) so.observe(n); });

  var scrollAnim = 0;
  function stopScroll() { if (scrollAnim) { cancelAnimationFrame(scrollAnim); scrollAnim = 0; } }
  ['wheel', 'touchstart', 'keydown'].forEach(function (ev) { addEventListener(ev, stopScroll, { passive: true }); });
  function glideTo(y, done) {
    stopScroll();
    var y0 = window.scrollY, dy = y - y0, dur = clamp(Math.abs(dy) * .55, 800, 1700), t0 = performance.now();
    if (!dy) return done && done();
    (function f(now) {
      var p = clamp((now - t0) / dur), e = p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
      window.scrollTo(0, y0 + dy * e);
      if (p < 1) scrollAnim = requestAnimationFrame(f); else { scrollAnim = 0; if (done) done(); }
    })(t0);
  }
  $$('a[href^="#"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var id = a.getAttribute('href').slice(1), t = id === 'top' ? d.body : d.getElementById(id);
      if (a.closest('#links')) closeMenu();
      if (!motion || !t) return;
      e.preventDefault();
      var y = id === 'top' ? 0 : t.getBoundingClientRect().top + window.scrollY - (parseFloat(getComputedStyle(root).scrollPaddingTop) || 90);
      glideTo(y, function () {
        history.replaceState(null, '', '#' + id);
        if (e.detail === 0 && t !== d.body) { t.setAttribute('tabindex', '-1'); t.focus({ preventScroll: true }); }
      });
    });
  });

  /* ------------------------------------------------------------------ *
   * 8. Components
   * ------------------------------------------------------------------ */
  // Expanding stage cards
  var sg = $('#stages');
  if (sg) {
    var cards = Array.prototype.slice.call(sg.children);
    var openCard = function (i) {
      cards.forEach(function (c, j) {
        c.classList.toggle('open', j === i);
        $('.stg-btn', c).setAttribute('aria-expanded', j === i ? 'true' : 'false');
      });
    };
    cards.forEach(function (c, i) {
      var b = $('.stg-btn', c);
      b.addEventListener('click', function () { openCard(i); });
      b.addEventListener('focus', function () { openCard(i); });
      if (fine) c.addEventListener('pointerenter', function () { openCard(i); });
    });
  }

  // Press carousel: arrows, plus mouse drag with snap on release
  var car = $('#car');
  if (car) {
    var step = function () { var f = car.firstElementChild; return f ? f.offsetWidth + 18 : 340; };
    $('#next').addEventListener('click', function () { car.scrollBy({ left: step(), behavior: 'smooth' }); });
    $('#prev').addEventListener('click', function () { car.scrollBy({ left: -step(), behavior: 'smooth' }); });
    var down = false, sx = 0, sl = 0, moved = 0;
    car.addEventListener('pointerdown', function (e) {
      if (e.pointerType !== 'mouse' || e.button !== 0) return;
      down = true; moved = 0; sx = e.clientX; sl = car.scrollLeft; car.classList.add('drag');
    });
    addEventListener('pointermove', function (e) {
      if (!down) return; var dx = e.clientX - sx; moved = Math.max(moved, Math.abs(dx)); car.scrollLeft = sl - dx;
    });
    addEventListener('pointerup', function () { if (down) { down = false; car.classList.remove('drag'); } });
    car.addEventListener('click', function (e) { if (moved > 6) { e.preventDefault(); e.stopPropagation(); moved = 0; } }, true);
  }

  // FAQ: animated open and close (falls back to native when motion is off)
  if (motion) {
    $$('.faq details').forEach(function (det) {
      var sum = $('summary', det);
      sum.addEventListener('click', function (e) {
        e.preventDefault();
        if (det._a) det._a.cancel();
        var closed = sum.offsetHeight + (det.offsetHeight - det.clientHeight);
        det.style.overflow = 'hidden';
        var from, to;
        if (!det.open) { from = det.offsetHeight; det.open = true; to = det.scrollHeight + (det.offsetHeight - det.clientHeight); }
        else { from = det.offsetHeight; to = closed; }
        var opening = det.open && to > from;
        det._a = det.animate({ height: [from + 'px', to + 'px'] }, { duration: 650, easing: 'cubic-bezier(.16,1,.3,1)' });
        det._a.onfinish = function () {
          if (!opening) det.open = false;
          det.style.overflow = ''; det._a = null;
        };
        det._a.oncancel = function () { det.style.overflow = ''; };
      });
    });
  }

  /* ------------------------------------------------------------------ *
   * 9. Opening sequence
   * ------------------------------------------------------------------ */
  function go() {
    if (root.classList.contains('go')) return;
    root.classList.add('go');
    if (heroCount) countTo(heroCount, +heroCount.dataset.count, '+', 900);
    queue();
  }
  var intro = $('#intro');
  if (!motion || !intro) {
    if (intro) intro.remove();
    go();
  } else if (location.hash || window.scrollY > 80) {
    intro.remove(); go();                       // deep link or restored scroll: no curtain
  } else {
    root.classList.add('lock');
    var skip, skipped = new Promise(function (r) { skip = r; });
    intro.addEventListener('pointerdown', function () { skip(); });
    var minimum = Promise.race([new Promise(function (r) { setTimeout(r, 1700); }), skipped]);
    var img = $('.cut');
    var assets = Promise.race([
      Promise.all([d.fonts ? d.fonts.ready : 0, img && img.decode ? img.decode().catch(function () {}) : 0]),
      new Promise(function (r) { setTimeout(r, 3500); })
    ]);
    Promise.all([minimum, assets]).then(function () {
      root.classList.add('open');               // curtain lifts
      setTimeout(go, 450);                      // hero starts while it is still rising
      setTimeout(function () { intro.remove(); root.classList.remove('lock'); }, 1500);
    });
  }
})();
