/* ============================================================
   DR. GORAV GUPTA — motion layer
   Lenis (smooth scroll) + GSAP ScrollTrigger (scroll-linked art direction)
   Everything degrades: no JS = readable site, reduced-motion = still reveals.
   ============================================================ */
(function () {
  'use strict';

  var q  = function (s, c) { return (c || document).querySelector(s); };
  var qa = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine    = window.matchMedia('(hover:hover) and (pointer:fine)').matches;
  var hasGSAP = typeof window.gsap !== 'undefined' && typeof window.ScrollTrigger !== 'undefined';

  var body = document.body;

  /* A reload (or back/forward) must always replay the intro from the top.
     Otherwise the browser restores the old scroll offset underneath the
     opening panel and the hero / pinned sections start half-played. */
  if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
  if (!location.hash) window.scrollTo(0, 0);
  window.addEventListener('pageshow', function (e) { if (e.persisted) location.reload(); });

  var yr = q('#year'); if (yr) yr.textContent = new Date().getFullYear();

  if (hasGSAP) gsap.registerPlugin(ScrollTrigger);

  /* ----------------------------------------------------------
     SMOOTH SCROLL
     ---------------------------------------------------------- */
  var lenis = null;
  function initLenis() {
    if (reduced || typeof window.Lenis === 'undefined') return;
    lenis = new Lenis({
      duration: 1.1,
      easing: function (t) { return Math.min(1, 1.001 - Math.pow(2, -10 * t)); },
      smoothWheel: true,
      wheelMultiplier: 1,
      touchMultiplier: 1.6
    });
    if (hasGSAP) {
      lenis.on('scroll', ScrollTrigger.update);
      gsap.ticker.add(function (time) { lenis.raf(time * 1000); });
      gsap.ticker.lagSmoothing(0);
    } else {
      requestAnimationFrame(function raf(t) { lenis.raf(t); requestAnimationFrame(raf); });
    }
  }

  function scrollTo(target) {
    if (lenis) lenis.scrollTo(target, { offset: 0, duration: 1.25 });
    else {
      var el = typeof target === 'string' ? q(target) : target;
      if (el) el.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth' });
    }
  }

  /* ----------------------------------------------------------
     OPENING SEQUENCE  (wow #1)
     ---------------------------------------------------------- */
  var heroTl = null;
  var HERO_FADE = '.hero__meta, .hero__statement, .hero__scroll, .nav__inner > *';

  // Hidden start states, applied BEFORE the opening panel starts to wipe so the
  // hero never shows its finished state underneath and then snaps back.
  function heroPrime() {
    if (!hasGSAP) return;
    gsap.set('.hero__name .row > span', { yPercent: 110 });
    gsap.set('.hero__meta',      { y: 18,  opacity: 0 });
    gsap.set('.hero__statement', { y: 22,  opacity: 0 });
    gsap.set('.hero__scroll',    { opacity: 0 });
    gsap.set('.nav__inner > *',  { y: -14, opacity: 0 });
  }

  function hero() {
    if (!hasGSAP || heroTl) return;
    heroTl = gsap.timeline({ defaults: { ease: 'power3.out' } });
    heroTl.to('.hero__name .row > span', { yPercent: 0, duration: 1.15, stagger: 0.085 }, 0)
      .to('#heroPortrait', { clipPath: 'inset(0% 0% 0% 0%)', duration: 1.4, ease: 'expo.out' }, 0.15)
      .to('.hero__meta',      { y: 0, opacity: 1, duration: .9 }, 0.5)
      .to('.hero__statement', { y: 0, opacity: 1, duration: 1 }, 0.62)
      .to('.hero__scroll',    { opacity: 1, duration: .8 }, 0.9)
      .to('.nav__inner > *',  { y: 0, opacity: 1, duration: .8, stagger: .06 }, 0.35);
  }

  /* Final states applied without animation — used whenever the intro is
     skipped, GSAP is unavailable, or the failsafe trips. Nothing decorative
     is ever allowed to keep the content hidden. */
  function setStatic() {
    qa('.hero__name .row > span').forEach(function (s) { s.style.transform = 'none'; });
    var hp = q('#heroPortrait'); if (hp) hp.style.clipPath = 'inset(0% 0% 0% 0%)';
    if (heroTl) heroTl.kill();
    if (hasGSAP) gsap.set(HERO_FADE, { y: 0, opacity: 1, clearProps: 'transform,opacity' });
    var rf = q('#revealFrame');  if (rf) rf.style.transform = 'none';
    var ri = q('#revealInner');  if (ri) ri.style.transform = 'none';
  }

  function opening() {
    var panel = q('#opening');
    var finished = false;

    function finish(animate) {
      if (finished) return;
      finished = true;
      if (!animate && tl) tl.kill();
      if (panel && panel.parentNode) panel.parentNode.removeChild(panel);
      body.classList.remove('is-loading');
      if (lenis) lenis.start();
      if (animate && hasGSAP) {
        ScrollTrigger.refresh();
      } else {
        setStatic();
        if (hasGSAP) ScrollTrigger.refresh();
      }
    }

    if (!panel || reduced || !hasGSAP) { finish(false); return; }

    heroPrime();
    // CSS parks these off-screen in px; GSAP's yPercent:0 would NOT clear that,
    // which is why the name and role never appeared. Reset y, then drive %.
    gsap.set('.opening__name .word i', { y: 0, yPercent: 105 });
    gsap.set('.opening__role span',    { y: 0, yPercent: 110 });
    if (lenis) { lenis.scrollTo(0, { immediate: true }); lenis.stop(); }

    // Failsafe: if the ticker is throttled (hidden tab, backgrounded window)
    // or anything stalls, unlock the page anyway.
    var guard = setTimeout(function () { finish(false); }, 6000);

    var counter = { v: 0 };
    var countEl = q('#count');

    var tl = gsap.timeline({
      onComplete: function () { clearTimeout(guard); finish(true); }
    });

    tl.to('.opening__name .word i', { yPercent: 0, duration: 1.1, stagger: .09, ease: 'expo.out' }, .15)
      .to(counter, {
        v: 100, duration: 1.7, ease: 'power2.inOut',
        onUpdate: function () { if (countEl) countEl.textContent = String(Math.round(counter.v)).padStart(2, '0'); }
      }, .2)
      .to('.opening__role span', { yPercent: 0, duration: .9, ease: 'expo.out' }, .75)
      .to(panel, { clipPath: 'inset(0% 0% 100% 0%)', duration: 1.15, ease: 'expo.inOut' }, 2.1)
      .to('.opening__center, .opening__foot', { opacity: 0, duration: .5 }, 2.1)
      // the hero rises while the panel is still wiping away, so the two read as one move
      .call(hero, null, 2.55);

    // accent rule draw — pseudo-element can't be tweened, so drive a real node
    var line = q('.opening__line');
    if (line) {
      var fill = document.createElement('span');
      fill.style.cssText = 'position:absolute;inset:0;background:var(--accent);transform:scaleX(0);transform-origin:left;';
      line.appendChild(fill);
      tl.to(fill, { scaleX: 1, duration: 1.5, ease: 'power2.inOut' }, .3);
    }
  }

  /* ----------------------------------------------------------
     HERO PORTRAIT — parallax out  (part of wow #2)
     ---------------------------------------------------------- */
  function heroScroll() {
    if (!hasGSAP || reduced) return;
    var p = q('#heroPortrait');
    if (p) {
      gsap.to(p.querySelectorAll('img'), {
        yPercent: -12, scale: 1.08, ease: 'none',
        scrollTrigger: { trigger: '#hero', start: 'top top', end: 'bottom top', scrub: true }
      });
    }
    gsap.to('.hero__type', {
      yPercent: -18, opacity: .25, ease: 'none',
      scrollTrigger: { trigger: '#hero', start: 'top top', end: 'bottom top', scrub: true }
    });
  }

  /* ----------------------------------------------------------
     THE REVEAL — pinned portrait transformation  (wow #2)
     ---------------------------------------------------------- */
  function revealSection() {
    if (!hasGSAP || reduced) return;
    var sec = q('#reveal');
    var frame = q('#revealFrame');
    var inner = q('#revealInner');
    if (!sec || !frame || !inner) return;

    // matchMedia so the opening crop is rebuilt (not left stale) if the viewport
    // crosses the breakpoint; GSAP reverts the old context for us.
    gsap.matchMedia().add(
      { narrow: '(max-width:719px)', wide: '(min-width:720px)' },
      function (ctx) {
        var crop = { x: ctx.conditions.narrow ? 0.64 : 0.36 };

        // The frame narrows on X and the inner wrapper widens by exactly 1/x, so
        // the image stays undistorted at every intermediate value. Tweening the
        // two independently would NOT stay reciprocal mid-tween — one proxy
        // drives both.
        function apply() {
          gsap.set(frame, { scaleX: crop.x });
          gsap.set(inner, { scaleX: 1 / crop.x });
        }
        apply();

        var tl = gsap.timeline({
          // scrub:true couples motion directly to scroll position; Lenis already
          // smooths the input, so extra scrub lag only feels disconnected.
          scrollTrigger: { trigger: sec, start: 'top top', end: 'bottom bottom', scrub: true }
        });

        tl.to(crop, { x: 1, ease: 'power2.inOut', duration: 1, onUpdate: apply }, 0)
          .fromTo(frame.querySelectorAll('img'),
            { scale: 1.18 }, { scale: 1, ease: 'power2.inOut', duration: 1 }, 0)
          .to(frame.querySelector('.layer-col'), { opacity: 1, ease: 'none', duration: .7 }, .25)
          .fromTo('.reveal__words .w-a',
            { xPercent: 0 }, { xPercent: -16, ease: 'none', duration: 1 }, 0)
          .fromTo('.reveal__words .w-b',
            { xPercent: 0 }, { xPercent: 16, ease: 'none', duration: 1 }, 0)
          .fromTo('.reveal__caption', { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: .3 }, .45);
      }
    );
  }

  /* ----------------------------------------------------------
     GENERIC REVEALS + PARALLAX
     ---------------------------------------------------------- */
  function reveals() {
    if (!hasGSAP) { qa('[data-journey],[data-step]').forEach(function (n) { n.classList.add('is-in'); }); return; }

    if (!reduced) {
      qa('[data-reveal="fade"]').forEach(function (el) {
        gsap.from(el, {
          y: 26, opacity: 0, duration: 1, ease: 'power3.out',
          scrollTrigger: { trigger: el, start: 'top 86%' }
        });
      });

      qa('[data-reveal="lines"]').forEach(function (el) {
        gsap.from(el, {
          y: 34, opacity: 0, duration: 1.1, ease: 'power3.out',
          scrollTrigger: { trigger: el, start: 'top 85%' }
        });
      });

      qa('[data-parallax]').forEach(function (el) {
        var amt = parseFloat(el.getAttribute('data-parallax')) || .1;
        var img = el.querySelector('img') || el;
        gsap.fromTo(img, { yPercent: -amt * 100 }, {
          yPercent: amt * 100, ease: 'none',
          scrollTrigger: { trigger: el, start: 'top bottom', end: 'bottom top', scrub: true }
        });
      });
    }

    // hairline draw-ins for timeline + pathway
    qa('[data-journey],[data-step]').forEach(function (el) {
      ScrollTrigger.create({
        trigger: el, start: 'top 88%', once: true,
        onEnter: function () { el.classList.add('is-in'); }
      });
      if (!reduced) {
        gsap.from(el.children, {
          y: 20, opacity: 0, duration: .9, ease: 'power3.out', stagger: .07,
          scrollTrigger: { trigger: el, start: 'top 88%' }
        });
      }
    });

    // credential lists
    qa('.impact__col ul').forEach(function (ul) {
      if (reduced) return;
      gsap.from(ul.children, {
        y: 18, opacity: 0, duration: .8, ease: 'power3.out', stagger: .06,
        scrollTrigger: { trigger: ul, start: 'top 88%' }
      });
    });

    // media wall
    if (!reduced) {
      gsap.from('.media__feature', {
        y: 30, opacity: 0, duration: 1, ease: 'power3.out',
        scrollTrigger: { trigger: '.media__feature', start: 'top 86%' }
      });
      gsap.from('.media__item', {
        y: 24, opacity: 0, duration: .85, ease: 'power3.out', stagger: .08,
        scrollTrigger: { trigger: '.media__list', start: 'top 88%' }
      });
      gsap.from('.footer__statement .line > span', {
        yPercent: 110, duration: 1.1, ease: 'expo.out', stagger: .1,
        scrollTrigger: { trigger: '.footer__statement', start: 'top 88%' }
      });
    }
  }

  /* ----------------------------------------------------------
     PHILOSOPHY — scrubbed word ignition  (wow #4)
     ---------------------------------------------------------- */
  function philosophy() {
    var quote = q('#quote');
    if (!quote) return;
    var words = qa('.word', quote);
    if (!hasGSAP || reduced) { words.forEach(function (w) { w.classList.add('is-lit'); }); return; }

    // one scrubbed timeline: each word ignites slightly after the one before it
    var tl = gsap.timeline({
      scrollTrigger: { trigger: quote, start: 'top 80%', end: 'bottom 45%', scrub: .7 }
    });
    words.forEach(function (w, i) {
      tl.to(w, {
        color: w.classList.contains('is-accent') ? '#86C4B8' : '#EDF1EC',
        duration: .4, ease: 'none'
      }, i * 0.12);
    });
  }

  /* ----------------------------------------------------------
     THE WORK — interactive expertise  (wow #3)
     ---------------------------------------------------------- */
  function work() {
    var rows = qa('.work__row');
    var panes = qa('.work__pane');
    if (!rows.length) return;

    panes.forEach(function (p) { p.removeAttribute('hidden'); });

    function activate(i) {
      rows.forEach(function (r, n) {
        var on = n === i;
        r.classList.toggle('is-active', on);
        r.setAttribute('aria-selected', on ? 'true' : 'false');
      });
      panes.forEach(function (p, n) { p.classList.toggle('is-shown', n === i); });
    }

    rows.forEach(function (r, i) {
      r.addEventListener('click', function () { activate(i); });
      r.addEventListener('focus', function () { activate(i); });
      if (fine) r.addEventListener('mouseenter', function () { activate(i); });
      r.addEventListener('keydown', function (e) {
        var n = null;
        if (e.key === 'ArrowDown' || e.key === 'ArrowRight') n = (i + 1) % rows.length;
        if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') n = (i - 1 + rows.length) % rows.length;
        if (n !== null) { e.preventDefault(); rows[n].focus(); }
      });
    });
  }

  /* ----------------------------------------------------------
     NAVIGATION
     ---------------------------------------------------------- */
  function nav() {
    var navEl = q('#nav');
    var burger = q('#burger');
    var menu = q('#menu');
    var last = 0;

    function onScroll() {
      var y = window.scrollY || document.documentElement.scrollTop;
      navEl.classList.toggle('is-stuck', y > 40);
      if (!body.classList.contains('menu-open')) {
        navEl.classList.toggle('is-hidden', y > last && y > 420);
      }
      last = y;
      var dock = q('#dock');
      if (dock) dock.classList.toggle('is-up', y > window.innerHeight * .9);
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    function closeMenu() {
      body.classList.remove('menu-open');
      burger.setAttribute('aria-expanded', 'false');
      burger.setAttribute('aria-label', 'Open menu');
      menu.setAttribute('aria-hidden', 'true');
      if (lenis) lenis.start();
    }

    if (burger) {
      burger.addEventListener('click', function () {
        var open = !body.classList.contains('menu-open');
        body.classList.toggle('menu-open', open);
        burger.setAttribute('aria-expanded', open ? 'true' : 'false');
        burger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
        menu.setAttribute('aria-hidden', open ? 'false' : 'true');
        if (lenis) { open ? lenis.stop() : lenis.start(); }
      });
    }
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && body.classList.contains('menu-open')) closeMenu();
    });

    // anchor handling through Lenis
    qa('a[href^="#"]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        var id = a.getAttribute('href');
        if (!id || id === '#') return;
        var t = q(id);
        if (!t) return;
        e.preventDefault();
        if (body.classList.contains('menu-open')) closeMenu();
        setTimeout(function () { scrollTo(t); }, body.classList.contains('menu-open') ? 400 : 0);
      });
    });

    // active link
    if (hasGSAP) {
      qa('.nav__link').forEach(function (link) {
        var id = link.getAttribute('href');
        var sec = q(id);
        if (!sec) return;
        ScrollTrigger.create({
          trigger: sec, start: 'top 45%', end: 'bottom 45%',
          onToggle: function (self) { link.classList.toggle('is-active', self.isActive); }
        });
      });
    }
  }

  /* ----------------------------------------------------------
     CURSOR + MAGNETIC CTA  (wow #5)
     ---------------------------------------------------------- */
  function cursor() {
    if (!fine || reduced || !hasGSAP) return;
    var el = q('#cursor');
    if (!el) return;
    var label = q('span', el);
    body.classList.add('has-cursor');

    var xTo = gsap.quickTo(el, 'x', { duration: .38, ease: 'power3' });
    var yTo = gsap.quickTo(el, 'y', { duration: .38, ease: 'power3' });

    window.addEventListener('mousemove', function (e) {
      xTo(e.clientX); yTo(e.clientY);
    }, { passive: true });

    document.addEventListener('mouseleave', function () { el.classList.add('is-hidden'); });
    document.addEventListener('mouseenter', function () { el.classList.remove('is-hidden'); });

    qa('[data-cursor]').forEach(function (t) {
      t.addEventListener('mouseenter', function () {
        label.textContent = t.getAttribute('data-cursor');
        el.classList.add('is-label');
      });
      t.addEventListener('mouseleave', function () {
        el.classList.remove('is-label');
      });
    });

    // magnetic
    var mag = q('#magnet');
    if (mag) {
      var inner = q('.magnet__inner', mag);
      var mx = gsap.quickTo(mag, 'x', { duration: .6, ease: 'elastic.out(1,0.5)' });
      var my = gsap.quickTo(mag, 'y', { duration: .6, ease: 'elastic.out(1,0.5)' });
      var ix = gsap.quickTo(inner, 'x', { duration: .7, ease: 'power3' });
      var iy = gsap.quickTo(inner, 'y', { duration: .7, ease: 'power3' });

      mag.addEventListener('mousemove', function (e) {
        var r = mag.getBoundingClientRect();
        var dx = e.clientX - (r.left + r.width / 2);
        var dy = e.clientY - (r.top + r.height / 2);
        mx(dx * .28); my(dy * .28);
        ix(dx * .12); iy(dy * .12);
      });
      mag.addEventListener('mouseleave', function () {
        mx(0); my(0); ix(0); iy(0);
      });
    }
  }

  /* ----------------------------------------------------------
     BOOT
     ---------------------------------------------------------- */
  function boot() {
    initLenis();
    nav();
    work();
    cursor();
    heroScroll();
    revealSection();
    reveals();
    philosophy();
    opening();
    if (hasGSAP) {
      window.addEventListener('load', function () { ScrollTrigger.refresh(); });
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
