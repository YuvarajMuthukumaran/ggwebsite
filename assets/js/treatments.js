/* Services: treatment-card motion. */
(function () {
  'use strict';
  var root = document.getElementById('treatments');
  if (!root) return;
  var row = root.querySelector('.tx__row'), cards = [].slice.call(root.querySelectorAll('.tx__c'));
  var scene = root.querySelector('.tx__scene'), glow = root.querySelector('.tx__glow');
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
  var process = document.getElementById('how-treatment-works'), askFab;
  if (process && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    process.classList.add('tx-process--motion');
    if ('IntersectionObserver' in window) {
      var processIO = new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting) {
          process.classList.add('tx-process--in');
          processIO.disconnect();
        }
      }, { threshold: .2 });
      processIO.observe(process);
    } else process.classList.add('tx-process--in');
  }
  var fabTracking = false, fabMO;
  function setupAskFabTracking() {
    if (!process || fabTracking || !matchMedia('(max-width: 700px)').matches) return false;
    askFab = document.querySelector('.askfab');
    if (!askFab) return false;
      function updateAskFab() {
        var rect = process.getBoundingClientRect();
        askFab.classList.toggle('is-muted', rect.bottom > 0 && rect.top < innerHeight);
      }
      fabTracking = true;
      updateAskFab();
      requestAnimationFrame(updateAskFab);
      if ('IntersectionObserver' in window) {
        var fabIO = new IntersectionObserver(function (entries) {
          askFab.classList.toggle('is-muted', entries[0].isIntersecting);
        });
        fabIO.observe(process);
      }
      addEventListener('scroll', updateAskFab, { passive: true });
      if (fabMO) fabMO.disconnect();
      return true;
  }
  setupAskFabTracking();
  document.addEventListener('DOMContentLoaded', setupAskFabTracking, { once: true });
  addEventListener('load', setupAskFabTracking, { once: true });
  addEventListener('resize', setupAskFabTracking, { passive: true });
  if (process && 'MutationObserver' in window) {
    fabMO = new MutationObserver(setupAskFabTracking);
    fabMO.observe(document.body, { childList: true, subtree: true });
  }

  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      if (entries[0].isIntersecting) { root.classList.add('tx--in'); io.disconnect(); }
    }, { threshold: .15 });
    io.observe(row);
  } else root.classList.add('tx--in');

  if (reduce) return;
  if (!fine) { root.classList.add('tx--float'); return; }

  var states = cards.map(function () { return { rx: 0, ry: 0, trx: 0, try_: 0 }; });
  var gx = 0, gy = 0, tgx = 0, tgy = 0, raf = 0;
  function frame() {
    raf = 0; var moving = false;
    cards.forEach(function (card, i) {
      var state = states[i];
      state.rx += (state.trx - state.rx) * .1;
      state.ry += (state.try_ - state.ry) * .1;
      if (Math.abs(state.trx - state.rx) > .01 || Math.abs(state.try_ - state.ry) > .01) moving = true;
      card.style.setProperty('--rx', state.rx.toFixed(2) + 'deg');
      card.style.setProperty('--ry', state.ry.toFixed(2) + 'deg');
      card.style.setProperty('--sx', (-state.ry * 2).toFixed(1) + 'px');
      card.style.setProperty('--sy', (state.rx * 2).toFixed(1) + 'px');
    });
    gx += (tgx - gx) * .06; gy += (tgy - gy) * .06;
    if (Math.abs(tgx - gx) > .1 || Math.abs(tgy - gy) > .1) moving = true;
    glow.style.setProperty('--gx', gx.toFixed(1) + 'px');
    glow.style.setProperty('--gy', gy.toFixed(1) + 'px');
    if (moving) raf = requestAnimationFrame(frame);
  }
  function animate() { if (!raf) raf = requestAnimationFrame(frame); }
  cards.forEach(function (card, i) {
    card.addEventListener('pointermove', function (event) {
      var rect = card.getBoundingClientRect();
      var px = (event.clientX - rect.left) / rect.width - .5;
      var py = (event.clientY - rect.top) / rect.height - .5;
      states[i].try_ = px * 12; states[i].trx = -py * 12;
      card.style.setProperty('--mx', ((px + .5) * 100).toFixed(0) + '%');
      card.style.setProperty('--my', ((py + .5) * 100).toFixed(0) + '%');
      animate();
    }, { passive: true });
    card.addEventListener('pointerleave', function () { states[i].trx = 0; states[i].try_ = 0; animate(); });
  });
  scene.addEventListener('pointermove', function (event) {
    var rect = scene.getBoundingClientRect();
    tgx = -((event.clientX - rect.left) / rect.width - .5) * 28;
    tgy = -((event.clientY - rect.top) / rect.height - .5) * 18;
    animate();
  }, { passive: true });
  scene.addEventListener('pointerleave', function () { tgx = 0; tgy = 0; animate(); });
})();
