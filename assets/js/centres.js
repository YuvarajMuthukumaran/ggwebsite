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
      // thumbnail swap inside the expanded panel
      panel.querySelectorAll('.cenr__th').forEach(function (b) {
        b.addEventListener('click', function (e) {
          e.stopPropagation();
          var img = panel.querySelector('.cenr__img');
          img.src = b.dataset.src; img.alt = b.dataset.alt;
          panel.querySelectorAll('.cenr__th').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        });
      });
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
})();
