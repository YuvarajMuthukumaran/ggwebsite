/* Polish layer: progress bar, ambient light, cursor glow, tilt, heartbeat draw. */
(function () {
  'use strict';
  var reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = matchMedia('(hover:hover) and (pointer:fine)').matches;
  var b = document.body;
  function el(tag, cls, html) { var n = document.createElement(tag); n.className = cls; if (html) n.innerHTML = html; return n; }

  /* scroll progress */
  var bar = el('div', 'pl-progress'); bar.setAttribute('aria-hidden', 'true'); b.appendChild(bar);
  var amb = el('div', 'pl-ambient', '<i></i><i></i><i></i>'); amb.setAttribute('aria-hidden', 'true'); b.insertBefore(amb, b.firstChild);

  /* one rAF loop drives progress, glow lerp and tilt */
  var gx = innerWidth / 2, gy = innerHeight / 2, tx = gx, ty = gy, glow = null;
  if (fine && !reduced) {
    glow = el('div', 'pl-glow'); glow.setAttribute('aria-hidden', 'true'); b.appendChild(glow);
    addEventListener('pointermove', function (e) { tx = e.clientX; ty = e.clientY; glow.classList.add('on'); }, { passive: true });
    document.addEventListener('pointerleave', function () { glow.classList.remove('on'); });
  }
  var tilts = [];
  if (fine && !reduced) {
    Array.prototype.forEach.call(document.querySelectorAll('.who__frame'), function (f) {
      var s = { f: f, rx: 0, ry: 0, trx: 0, try_: 0 };
      f.addEventListener('pointermove', function (e) {
        var r = f.getBoundingClientRect();
        s.ry = ((e.clientX - r.left) / r.width - .5) * 8;
        s.rx = -((e.clientY - r.top) / r.height - .5) * 8;
      });
      f.addEventListener('pointerleave', function () { s.rx = s.ry = 0; });
      tilts.push(s);
    });
  }
  (function loop() {
    var h = document.documentElement.scrollHeight - innerHeight;
    bar.style.transform = 'scaleX(' + (h > 0 ? Math.min(1, scrollY / h) : 0) + ')';
    if (glow) {
      gx += (tx - gx) * .08; gy += (ty - gy) * .08;
      glow.style.transform = 'translate3d(' + gx + 'px,' + gy + 'px,0)';
    }
    tilts.forEach(function (s) {
      s.trx += (s.rx - s.trx) * .09; s.try_ += (s.ry - s.try_) * .09;
      s.f.style.transform = 'perspective(900px) rotateX(' + s.trx + 'deg) rotateY(' + s.try_ + 'deg)';
    });
    requestAnimationFrame(loop);
  })();

  /* heartbeat divider at the head of each section */
  var path = 'M0 18 H120 L138 18 L150 4 L166 32 L180 10 L190 18 H260 L276 18 L288 8 L300 28 L310 18 H560';
  var io = 'IntersectionObserver' in window ? new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } });
  }, { threshold: .6 }) : null;
  Array.prototype.forEach.call(document.querySelectorAll('.section .section__head'), function (head) {
    var s = el('div', 'pl-ecg', '<svg class="pl-ecg" viewBox="0 0 560 36" preserveAspectRatio="none" aria-hidden="true"><path pathLength="1" d="' + path + '"/></svg>');
    var svg = s.firstChild; head.parentNode.insertBefore(svg, head);
    if (io) io.observe(svg); else svg.classList.add('is-in');
  });
})();
