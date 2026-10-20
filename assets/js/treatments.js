/* Services: Treatments and "How treatment works" as one component.
 *
 * Four treatment cards. Pointing at one (or tapping it, or focusing it with the keyboard) makes it the stage: the others recede, and the
 * "How treatment works" panel under the row changes from a slim rail into the full three-step timeline for that treatment. Nothing selected
 * means the rail. Esc, the Close button, or a second tap clears it. Arrow keys move between the cards.
 *
 * Motion: the cards tilt a few degrees toward a mouse pointer, and the soft background light shifts a little the other way (fine pointers
 * only). On touch screens there is a gentle idle float instead. With prefers-reduced-motion there is no tilt, parallax or float, only fades.
 * Only transform and opacity move (plus a small blur on the receded cards).
 */
(function () {
  'use strict';
  var root = document.getElementById('treatments');
  if (!root) return;
  var row = root.querySelector('.tx__row'), cards = [].slice.call(root.querySelectorAll('.tx__c')), how = document.getElementById('tx-how');
  var scene = root.querySelector('.tx__scene'), glow = root.querySelector('.tx__glow'), forEl = how.querySelector('.tx__for');
  var caps = [].slice.call(how.querySelectorAll('.tx__cap'));
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
  var narrow = matchMedia('(max-width: 700px)');
  var cur = -1, pinned = false, hoverT = 0, leaveT = 0;

  function setCaps(i) {
    var list = cards[i].getAttribute('data-caps').split('|');
    caps.forEach(function (c, k) {
      c.classList.remove('is-in');
      c.textContent = list[k] || '';
    });
    // a frame later, so the caption fades in rather than appearing with the text swap
    requestAnimationFrame(function () { requestAnimationFrame(function () { caps.forEach(function (c) { c.classList.add('is-in'); }); }); });
  }

  function place() {
    // on a phone the panel sits straight under the chosen card, so nothing needs scrolling to; otherwise it stays under the row
    if (narrow.matches && cur > -1) cards[cur].insertAdjacentElement('afterend', how);
    else scene.appendChild(how);
    if (cur > -1) {
      var r = cards[cur].getBoundingClientRect(), s = how.getBoundingClientRect();
      how.style.setProperty('--tx-arrow', Math.max(24, Math.min(s.width - 24, r.left + r.width / 2 - s.left)).toFixed(0) + 'px');
    }
  }

  function select(i, pin) {
    clearTimeout(leaveT);
    if (i === cur) { if (pin) pinned = true; return; }
    cur = i; pinned = !!pin;
    root.setAttribute('data-active', i);
    cards.forEach(function (c, k) {
      c.classList.toggle('is-on', k === i);
      c.classList.toggle('is-away', k !== i);
      c.querySelector('.tx__face').setAttribute('aria-expanded', k === i ? 'true' : 'false');
    });
    forEl.textContent = 'For ' + cards[i].querySelector('.tx__h').textContent;
    setCaps(i);
    place();
    // restart the ring fills and the progress line every time a treatment is chosen
    how.classList.remove('is-open'); void how.offsetWidth; how.classList.add('is-open');
  }

  function clear() {
    clearTimeout(hoverT); clearTimeout(leaveT);
    if (cur === -1) return;
    cur = -1; pinned = false;
    root.removeAttribute('data-active');
    cards.forEach(function (c) { c.classList.remove('is-on', 'is-away'); c.querySelector('.tx__face').setAttribute('aria-expanded', 'false'); });
    how.classList.remove('is-open');
    place();
  }

  cards.forEach(function (card, i) {
    var face = card.querySelector('.tx__face');
    var fresh = false;      // a tap or click focuses the button first; that focus must not count as a second press
    face.addEventListener('click', function () { if (fresh) { fresh = false; pinned = true; return; } if (cur === i && (pinned || !fine)) clear(); else select(i, true); });
    face.addEventListener('focus', function () { if (!pinned) { var was = cur; select(i, false); if (was !== i) { fresh = true; setTimeout(function () { fresh = false; }, 400); } } });
    if (fine) {
      card.addEventListener('pointerenter', function () { clearTimeout(leaveT); clearTimeout(hoverT); if (!pinned) hoverT = setTimeout(function () { select(i, false); }, 140); });
    }
    card.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') { e.preventDefault(); var n = cards[(i + 1) % cards.length].querySelector('.tx__face'); n.focus(); select((i + 1) % cards.length, true); }
      if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') { e.preventDefault(); var m = cards[(i + cards.length - 1) % cards.length].querySelector('.tx__face'); m.focus(); select((i + cards.length - 1) % cards.length, true); }
    });
  });
  scene.addEventListener('pointerleave', function () { clearTimeout(hoverT); if (!pinned && fine) leaveT = setTimeout(clear, 500); });
  scene.addEventListener('pointerenter', function () { clearTimeout(leaveT); });
  how.querySelector('.tx__x').addEventListener('click', function () { var b = cur > -1 ? cards[cur].querySelector('.tx__face') : null; clear(); if (b) b.focus(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && cur > -1) { var b = cards[cur].querySelector('.tx__face'); clear(); if (root.contains(document.activeElement)) b.focus(); } });
  narrow.addEventListener('change', place);
  addEventListener('resize', function () { if (cur > -1) place(); }, { passive: true });

  /* entrance: the header rises (the page's own reveal), then the cards stagger in */
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) { if (es[0].isIntersecting) { root.classList.add('tx--in'); io.disconnect(); } }, { threshold: .15 });
    io.observe(row);
  } else root.classList.add('tx--in');

  if (reduce) return;

  /* idle float on touch screens */
  if (!fine) { root.classList.add('tx--float'); return; }

  /* tilt toward the pointer, eased; the shadow and the background light move the other way */
  var st = cards.map(function () { return { rx: 0, ry: 0, trx: 0, try_: 0 }; }), gx = 0, gy = 0, tgx = 0, tgy = 0, raf = 0;
  function frame() {
    raf = 0; var more = false;
    cards.forEach(function (c, i) {
      var s = st[i];
      s.rx += (s.trx - s.rx) * .1; s.ry += (s.try_ - s.ry) * .1;
      if (Math.abs(s.trx - s.rx) > .01 || Math.abs(s.try_ - s.ry) > .01) more = true;
      c.style.setProperty('--rx', s.rx.toFixed(2) + 'deg'); c.style.setProperty('--ry', s.ry.toFixed(2) + 'deg');
      c.style.setProperty('--sx', (-s.ry * 2).toFixed(1) + 'px'); c.style.setProperty('--sy', (s.rx * 2).toFixed(1) + 'px');
    });
    gx += (tgx - gx) * .06; gy += (tgy - gy) * .06;
    if (Math.abs(tgx - gx) > .1 || Math.abs(tgy - gy) > .1) more = true;
    glow.style.setProperty('--gx', gx.toFixed(1) + 'px'); glow.style.setProperty('--gy', gy.toFixed(1) + 'px');
    if (more) raf = requestAnimationFrame(frame);
  }
  function go() { if (!raf) raf = requestAnimationFrame(frame); }
  cards.forEach(function (c, i) {
    c.addEventListener('pointermove', function (e) {
      var r = c.getBoundingClientRect(), px = (e.clientX - r.left) / r.width - .5, py = (e.clientY - r.top) / r.height - .5;
      st[i].try_ = px * 12; st[i].trx = -py * 12;                       // up to 6 degrees either way
      c.style.setProperty('--mx', ((px + .5) * 100).toFixed(0) + '%'); c.style.setProperty('--my', ((py + .5) * 100).toFixed(0) + '%');
      go();
    }, { passive: true });
    c.addEventListener('pointerleave', function () { st[i].trx = 0; st[i].try_ = 0; go(); });
  });
  scene.addEventListener('pointermove', function (e) {
    var r = scene.getBoundingClientRect(); tgx = -((e.clientX - r.left) / r.width - .5) * 28; tgy = -((e.clientY - r.top) / r.height - .5) * 18; go();
  }, { passive: true });
  scene.addEventListener('pointerleave', function () { tgx = 0; tgy = 0; go(); });
})();
