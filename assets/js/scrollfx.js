/* scrollfx.js: scroll-driven storytelling for the About page.
   Nothing here is a one-off entrance. Every value is a function of where the element sits in the
   viewport, eased toward its target each frame, so scrolling back reverses the motion and a jump in
   scroll still travels smoothly. Elements emerge from depth (scale, translateZ, a little tilt and a
   soft blur that clears as they arrive), foreground and background layers drift at different rates,
   and a brief extra blur appears only on elements that are still arriving during a fast scroll.

     data-fx="rise"      one element emerging; data-d sets its depth (default 1)
     data-fx="stagger"   the children emerge one after another; data-dir="right" arrives from the side
     data-fx="words"     a paragraph darkens word by word as it crosses the screen
     data-fx="fig"       a photograph in layers: plate, image and frame move at different rates
     data-fx="glow"      a soft light follows the pointer across the element
     data-fx="stack"     boxes that pin one under another; earlier boxes collapse to title strips as the next slides over

   Elements get .landed once, the first time they settle, for the small finishing touch in CSS.
   Content is fully visible until this script runs; reduced motion leaves the page as it is. */
(function () {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  var d = document, root = d.documentElement;
  var $$ = function (s, c) { return Array.prototype.slice.call((c || d).querySelectorAll(s)); };
  var clamp = function (v, a, b) { return Math.min(b, Math.max(a, v)); };
  var out = function (t) { return 1 - Math.pow(1 - t, 4); };      // quartic ease-out: fast start, long calm landing
  var K = .1;                                                      // inertia: share of the remaining distance covered per frame
  var vh = innerHeight, small = innerWidth < 700, jobs = [], running = false, lastY = scrollY, vel = 0;
  var fine = matchMedia('(hover: hover) and (pointer: fine)').matches;

  /* ---------------------------------------------------------------- one element, one state */
  function place(el, e, o) {
    var inv = 1 - e, s = small ? .55 : 1, dep = o.depth || 1;
    var x = 0, y = inv * 46 * dep * s, z = -inv * 120 * dep * s, rx = inv * 7 * s, ry = 0;
    if (o.dir === 'right') { x = inv * 60 * s; y = inv * 10; rx = 0; ry = -inv * 10; }
    else if (o.dir === 'left') { x = -inv * 60 * s; y = inv * 10; rx = 0; ry = inv * 10; }
    y += (o.drift || 0);
    var cv = o.cover || 0;
    var sc = (.93 + .07 * e) * (1 - cv * .03);
    // blur clears as the element lands; fast scrolling adds a little more, but only while it is still arriving
    var b = small ? 0 : inv * 5 + (inv > .002 ? Math.min(vel * .045, 2.2) : 0);

    el.style.opacity = clamp(e * 1.18, 0, 1).toFixed(3);   // covered boxes stay opaque so the ones beneath never show through
    el.style.transform = 'perspective(1200px) translate3d(' + x.toFixed(1) + 'px,' + y.toFixed(1) + 'px,' + z.toFixed(1) + 'px) rotateX(' + rx.toFixed(2) + 'deg) rotateY(' + ry.toFixed(2) + 'deg) scale(' + sc.toFixed(4) + ')';
    el.style.filter = b > .12 ? 'blur(' + b.toFixed(2) + 'px)' : '';
    if (e > .985 && !el.__landed) { el.__landed = 1; el.classList.add('landed'); }
  }

  // where the element's centre sits relative to the middle of the screen: -0.5 (top) to +0.5 (bottom)
  function pos(r) { return clamp((r.top + r.height / 2 - vh / 2) / vh, -.8, .8); }

  /* ---------------------------------------------------------------- rise */
  $$('[data-fx~="rise"]').forEach(function (el) {
    el.classList.remove('reveal');
    var depth = parseFloat(el.getAttribute('data-d')) || 1, cur = 0;
    place(el, 0, { depth: depth });
    jobs.push({ tick: function () {
      var r = el.getBoundingClientRect();
      var t = clamp((vh * .97 - r.top) / (vh * .48), 0, 1);
      cur += (t - cur) * K;
      place(el, out(cur), { depth: depth, drift: -pos(r) * depth * 10 });
      return Math.abs(t - cur) > .002;
    } });
  });

  /* ---------------------------------------------------------------- stagger */
  $$('[data-fx~="stagger"]').forEach(function (box) {
    var kids = [].slice.call(box.children), dir = box.getAttribute('data-dir') || '';
    var depth = parseFloat(box.getAttribute('data-d')) || 1;
    kids.forEach(function (k) { k.classList.remove('reveal'); place(k, 0, { dir: dir, depth: depth }); });
    var st = kids.map(function () { return 0; });
    jobs.push({ tick: function () {
      var r = box.getBoundingClientRect(), busy = false;
      var pc = clamp((vh * .98 - r.top) / (vh * .6), 0, 1.8), dr = -pos(r) * depth * 8;
      kids.forEach(function (k, i) {
        var t = clamp((pc - i * .1) / .55, 0, 1);
        st[i] += (t - st[i]) * K;
        if (Math.abs(t - st[i]) > .002) busy = true;
        place(k, out(st[i]), { dir: dir, depth: depth, drift: dir ? 0 : dr });
      });
      return busy;
    } });
  });

  /* ---------------------------------------------------------------- words */
  function splitWords(p) {
    var list = [];
    (function walk(node) {
      [].slice.call(node.childNodes).forEach(function (c) {
        if (c.nodeType === 3) {
          var frag = d.createDocumentFragment();
          c.textContent.split(/(\s+)/).forEach(function (w) {
            if (!w) return;
            if (/^\s+$/.test(w)) { frag.appendChild(d.createTextNode(w)); return; }
            var s = d.createElement('span'); s.className = 'fx-w'; s.textContent = w; frag.appendChild(s); list.push(s);
          });
          node.replaceChild(frag, c);
        } else if (c.nodeType === 1) { walk(c); }
      });
    })(p);
    return list;
  }
  $$('[data-fx~="words"]').forEach(function (p) {
    p.classList.remove('reveal');
    var words = splitWords(p), cur = 0, shown = 0;
    p.classList.add('fx-ready');
    jobs.push({ tick: function () {
      var r = p.getBoundingClientRect();
      var t = clamp((vh * .9 - r.top) / (vh * .42 + r.height * .55), 0, 1);
      cur += (t - cur) * K;
      var n = Math.min(words.length, Math.round(cur * (words.length + 1)));
      if (n !== shown) {
        for (var i = Math.min(n, shown); i < Math.max(n, shown); i++) if (words[i]) words[i].classList.toggle('on', i < n);
        shown = n;
      }
      return Math.abs(t - cur) > .002;
    } });
  });

  /* ---------------------------------------------------------------- photograph, in layers */
  $$('[data-fx~="fig"]').forEach(function (fig) {
    fig.classList.remove('reveal');
    var img = fig.querySelector('img'), cur = .5, arrive = 0;
    jobs.push({ tick: function () {
      var r = fig.getBoundingClientRect();
      var t = clamp((vh - r.top) / (vh + r.height), 0, 1);
      cur += (t - cur) * K;
      var p = cur - .5;
      var ta = clamp((vh * .97 - r.top) / (vh * .55), 0, 1);
      arrive += (ta - arrive) * K;
      var e = out(arrive), inv = 1 - e, s = small ? .5 : 1;
      fig.style.opacity = clamp(e * 1.2, 0, 1).toFixed(3);
      fig.style.transform = 'perspective(1300px) translate3d(0,' + (inv * 40 * s).toFixed(1) + 'px,' + (-inv * 110 * s).toFixed(1) + 'px) rotateY(' + (-p * 10 - inv * 8).toFixed(2) + 'deg) rotateX(' + (p * 4 + inv * 5).toFixed(2) + 'deg) scale(' + (.94 + .06 * e).toFixed(4) + ')';
      fig.style.filter = !small && inv > .02 ? 'blur(' + (inv * 5).toFixed(2) + 'px)' : '';
      if (img) img.style.transform = 'translate3d(0,' + (p * -8).toFixed(2) + '%,0) scale(' + (1.16 - .02 * e).toFixed(3) + ')';
      fig.style.setProperty('--py', (p * 70).toFixed(1));            // the plate behind the photo moves the other way
      if (e > .985 && !fig.__landed) { fig.__landed = 1; fig.classList.add('landed'); }
      return Math.abs(t - cur) > .002 || Math.abs(ta - arrive) > .002;
    } });
  });

  /* ---------------------------------------------------------------- light that follows the pointer */
  if (fine) {
    $$('[data-fx~="glow"]').forEach(function (el) {
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect();
        el.style.setProperty('--mx', (e.clientX - r.left).toFixed(0) + 'px');
        el.style.setProperty('--my', (e.clientY - r.top).toFixed(0) + 'px');
        el.classList.add('is-lit');
      });
      el.addEventListener('pointerleave', function () { el.classList.remove('is-lit'); });
    });
  }

  /* ---------------------------------------------------------------- stacked boxes
     Each box emerges from depth, pins just under the one before it, and the earlier boxes recede into a
     title strip as the next slides over them. Built to be cheap while scrolling: positions come from one
     read per frame (the container, which never moves) plus measurements taken once, the boxes only get
     transform and opacity (compositor properties, no blur, no custom-property writes), and nothing is
     written when the rounded values have not changed. */
  var sm = function (t) { return t * t * t * (t * (t * 6 - 15) + 10); };   // smootherstep: eases in and out, no sudden start
  var measures = [];
  $$('[data-fx~="stack"]').forEach(function (stack) {
    var kids = [].slice.call(stack.children), n = kids.length;
    var shade = kids.map(function (k) { return k.querySelector('.st-box__shade'); });
    var body = kids.map(function (k) { return [k.querySelector('.st-box__l'), k.querySelector('.st-box__r')]; });
    var tab = kids.map(function (k) { return k.querySelector('.st-box__tab'); });
    var nat = [], hs = [], H = 0;
    var arr = kids.map(function () { return 0; }), cov = kids.map(function () { return 0; }), last = kids.map(function () { return ''; });

    function measure() {
      var gap = parseFloat(getComputedStyle(stack).rowGap) || 0, y = 0;
      kids.forEach(function (k, i) { hs[i] = k.offsetHeight; nat[i] = y; y += hs[i] + gap; });
      H = y - gap;
    }
    measure(); measures.push(measure);

    function apply(i, e, cv) {
      var k = kids[i];
      k.style.opacity = clamp(e * 1.2, 0, 1).toFixed(3);
      k.style.transform = 'translate3d(0,' + ((1 - e) * 56).toFixed(1) + 'px,0) scale(' + ((.95 + .05 * e) * (1 - cv * .03)).toFixed(4) + ')';
      if (shade[i]) shade[i].style.opacity = (cv * .8).toFixed(3);
      var bo = clamp(1 - (cv - .1) * 2.6, 0, 1).toFixed(3);
      if (body[i][0]) body[i][0].style.opacity = bo;
      if (body[i][1]) body[i][1].style.opacity = bo;
      if (tab[i]) tab[i].style.opacity = clamp((cv - .35) * 3, 0, 1).toFixed(3);
      if (e > .985 && !k.__landed) { k.__landed = 1; k.classList.add('landed'); }
    }
    kids.forEach(function (k, i) { apply(i, 0, 0); });

    var lastT = 0;
    jobs.push({ tick: function () {
      // time-based damping: the same softness at 60, 90 or 144 fps
      var now = performance.now(), dt = lastT ? Math.min(50, now - lastT) : 16; lastT = now;
      var al = 1 - Math.exp(-dt / 190);
      var cTop = stack.getBoundingClientRect().top, bottom = cTop + H, busy = false, pinned = innerWidth >= 700;
      var tops = [];
      for (var i = 0; i < n; i++) {
        var unst = cTop + nat[i];
        tops[i] = pinned ? Math.min(Math.max(unst, 96 + i * 60), bottom - hs[i]) : unst;
      }
      for (var i = 0; i < n; i++) {
        var t = clamp((vh * .98 - (cTop + nat[i])) / (vh * .8), 0, 1);
        arr[i] += (t - arr[i]) * al;
        var ct = (pinned && i < n - 1) ? clamp((tops[i] + hs[i] - tops[i + 1]) / (hs[i] * .9), 0, 1) : 0;
        cov[i] += (ct - cov[i]) * al;
        if (Math.abs(t - arr[i]) > .002 || Math.abs(ct - cov[i]) > .002) busy = true;
        var e = sm(arr[i]), cv = sm(cov[i]), key = Math.round(e * 400) + '|' + Math.round(cv * 400);
        if (key !== last[i]) { last[i] = key; apply(i, e, cv); }
      }
      return busy;
    } });
  });

  /* ---------------------------------------------------------------- loop */
  function frame() {
    var y = scrollY;
    vel += (Math.abs(y - lastY) - vel) * .22; lastY = y;
    var busy = vel > .4;
    for (var i = 0; i < jobs.length; i++) {
      try { if (jobs[i].tick()) busy = true; } catch (e) { jobs[i].tick = function () { return false; }; }
    }
    if (busy) requestAnimationFrame(frame); else running = false;
  }
  function wake() { if (!running) { running = true; requestAnimationFrame(frame); } }

  addEventListener('scroll', wake, { passive: true });
  function remeasure() { measures.forEach(function (m) { m(); }); wake(); }
  addEventListener('resize', function () { vh = innerHeight; small = innerWidth < 700; remeasure(); });
  addEventListener('load', remeasure);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(remeasure);
  root.classList.add('fx');
  wake();
})();
