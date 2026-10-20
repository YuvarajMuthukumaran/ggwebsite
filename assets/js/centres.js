/* "Our centres": a row of photo panels. On a mouse, hovering or focusing a panel
   expands it and reveals its details, narrowing the others — one open at a time.
   On touch, tapping a closed panel opens it in place (tapping it again, or another
   panel, closes/switches); the details are always reachable by keyboard either way. */
(function () {
  [].forEach.call(document.querySelectorAll('[data-cenr-row]'), function (row) {
    var panels = [].slice.call(row.querySelectorAll('[data-cenr]'));
    var hoverable = matchMedia('(hover: hover) and (pointer: fine)').matches;

    function setOpen(panel, open) {
      panel.classList.toggle('is-open', open);
      var hit = panel.querySelector('.cenr__hit');
      hit.setAttribute('aria-expanded', open ? 'true' : 'false');
    }
    function closeAll(except) {
      panels.forEach(function (p) { if (p !== except) setOpen(p, false); });
    }

    panels.forEach(function (panel) {
      var hit = panel.querySelector('.cenr__hit');
      hit.addEventListener('click', function (e) {
        if (hoverable) return; // desktop: hover/focus already shows the detail; the click just follows the link area
        e.preventDefault();
        var isOpen = panel.classList.contains('is-open');
        closeAll();
        setOpen(panel, !isOpen);
      });
      if (hoverable) {
        panel.addEventListener('mouseenter', function () { closeAll(panel); setOpen(panel, true); });
        panel.addEventListener('focusin', function () { closeAll(panel); setOpen(panel, true); });
      }
    });
    row.addEventListener('mouseleave', function () { if (hoverable) closeAll(); });

    // the jump chips above the row open the matching panel instead of just scrolling to it
    var bar = row.parentElement.querySelector('[data-cenr-jumpbar]');
    if (bar) {
      bar.querySelectorAll('[data-cenr-jump]').forEach(function (a) {
        a.addEventListener('click', function () {
          var target = row.querySelector('#centre-' + a.dataset.cenrJump);
          if (!target) return;
          closeAll();
          setOpen(target, true);
        });
      });
    }
  });

  /* "Play video walkthrough": one shared player, filled in only when a button is pressed, so no video is downloaded until then */
  var dlg = null;
  function player() {
    if (dlg) return dlg;
    dlg = document.createElement('dialog');
    dlg.className = 'vw';
    dlg.innerHTML = '<div class="vw__box"><button type="button" class="vw__x" aria-label="Close video"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg></button>' +
      '<video class="vw__v" controls playsinline preload="none"></video><p class="vw__bar"><b></b></p></div>';
    document.body.appendChild(dlg);
    var v = dlg.querySelector('video');
    v.addEventListener('loadedmetadata', function () { dlg.classList.toggle('vw--tall', v.videoHeight > v.videoWidth); });   // a phone-shaped film gets a narrow player
    function close() { if (dlg.open) dlg.close(); }
    dlg.querySelector('.vw__x').addEventListener('click', close);
    dlg.addEventListener('click', function (e) { if (e.target === dlg) close(); });   // the dark area around the box
    dlg.addEventListener('close', function () { v.pause(); v.removeAttribute('src'); v.load(); document.documentElement.classList.remove('vw-lock'); });
    return dlg;
  }
  [].forEach.call(document.querySelectorAll('[data-vid]'), function (panel) {
    var btn = panel.querySelector('[data-play]');
    if (!btn || typeof HTMLDialogElement === 'undefined') { if (btn) btn.hidden = true; return; }
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var d = player(), v = d.querySelector('video');
      d.querySelector('.vw__bar b').textContent = panel.getAttribute('data-vid-title') || '';
      v.src = panel.getAttribute('data-vid');
      document.documentElement.classList.add('vw-lock');
      d.showModal();
      var p = v.play(); if (p && p.catch) p.catch(function () {});   // if the browser refuses, the controls are right there
    });
  });
})();
