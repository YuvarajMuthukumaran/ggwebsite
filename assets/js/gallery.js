/* gallery.js: lightbox for the photograph in #gallery. No dependencies. */
(function () {
  'use strict';
  var root = document.getElementById('gallery');
  if (!root || typeof HTMLDialogElement === 'undefined') return;

  var dlg = document.createElement('dialog');
  dlg.className = 'lb';
  dlg.setAttribute('aria-label', 'Photograph');
  dlg.innerHTML = '<button type="button" class="lb__x" aria-label="Close photograph">\u00d7</button>' +
                  '<img class="lb__img" alt=""><p class="lb__cap"></p>';
  document.body.appendChild(dlg);
  var img = dlg.querySelector('.lb__img');
  var cap = dlg.querySelector('.lb__cap');
  var opener = null;

  root.addEventListener('click', function (e) {
    var btn = e.target.closest('.gal__btn');
    if (!btn) return;
    var thumb = btn.querySelector('img');
    var fig = btn.closest('figure');
    var fc = fig && fig.querySelector('figcaption');
    opener = btn;
    img.src = btn.getAttribute('data-full');
    img.alt = thumb ? thumb.alt : '';
    cap.textContent = fc ? fc.textContent : '';
    dlg.showModal();
  });
  dlg.addEventListener('click', function (e) {
    /* a click on the backdrop (the dialog itself) or the cross closes it */
    if (e.target === dlg || e.target.classList.contains('lb__x')) dlg.close();
  });
  dlg.addEventListener('close', function () {
    img.removeAttribute('src');
    if (opener) opener.focus();
  });
})();
