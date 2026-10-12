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
     data-fx="stack"     boxes that pin one under another; earlier boxes recede as the next slides over

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
     Each box emerges from depth, pins just under the one before it, and the earlier boxes recede
     (a little smaller, dimmer, lifted) as the next one slides over them. Inside a box the icon and the
     text drift at different rates, and its tags arrive one by one once it has landed. */
  $$('[data-fx~="stack"]').forEach(function (stack) {
    var kids = [].slice.call(stack.children), arr = kids.map(function () { return 0; }), cov = kids.map(function () { return 0; });
    kids.forEach(function (k) { place(k, 0, { depth: .8 }); });
    jobs.push({ tick: function () {
      var busy = false, rs = kids.map(function (k) { return k.getBoundingClientRect(); });
      var pinned = innerWidth >= 700;
      kids.forEach(function (k, i) {
        var r = rs[i];
        var t = clamp((vh * .98 - r.top) / (vh * .5), 0, 1);
        arr[i] += (t - arr[i]) * K;
        var ct = 0;
        if (pinned && i < kids.length - 1) {
          var top = 96 + i * 60;
          ct = clamp((top + r.height - rs[i + 1].top) / (r.height * .9), 0, 1);
        }
        cov[i] += (ct - cov[i]) * K;
        if (Math.abs(t - arr[i]) > .002 || Math.abs(ct - cov[i]) > .002) busy = true;
        place(k, out(arr[i]), { depth: .8, cover: cov[i] });
        k.style.setProperty('--cov', cov[i].toFixed(3));
        k.style.setProperty('--fp', (-pos(r) * 26).toFixed(1));
      });
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
  addEventListener('resize', function () { vh = innerHeight; small = innerWidth < 700; wake(); });
  root.classList.add('fx');
  wake();
})();
