/* Services: each area-of-care circle opens a dialog with the full text for that area, so the page shows each area once.
   The circle is still a normal link to the guide, so it works without JavaScript. Arrow keys and the Previous / Next buttons step through the eight areas. */
(function () {
  var sec = document.querySelector('[data-areas]');
  if (!sec || typeof HTMLDialogElement === 'undefined') return;
  var cards = [].slice.call(sec.querySelectorAll('.bb'));
  var ids = cards.map(function (c) { return c.id; });
  var dlg = document.createElement('dialog');
  dlg.className = 'am';
  dlg.setAttribute('aria-labelledby', 'am-title');
  dlg.innerHTML = '<div class="am__box"><button type="button" class="am__x" aria-label="Close"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg></button>' +
    '<div class="am__body"></div><div class="am__nav"><button type="button" class="am__p">&larr; Previous area</button><span class="am__c" aria-live="polite"></span><button type="button" class="am__n">Next area &rarr;</button></div></div>';
  document.body.appendChild(dlg);
  var body = dlg.querySelector('.am__body'), cnt = dlg.querySelector('.am__c'), cur = 0, opener = null;
  function show(i) {
    cur = (i + ids.length) % ids.length;
    var t = document.getElementById('area-' + ids[cur]);
    if (!t) return;
    body.innerHTML = ''; body.appendChild(t.content.cloneNode(true));
    cnt.textContent = (cur + 1) + ' of ' + ids.length;
    body.classList.remove('is-in'); void body.offsetWidth; body.classList.add('is-in');
    body.scrollTop = 0;
  }
  function open(i, from) {
    opener = from || null; show(i);
    document.documentElement.classList.add('am-lock');
    if (!dlg.open) dlg.showModal();
    dlg.querySelector('.am__x').focus({ preventScroll: true });
  }
  cards.forEach(function (card, i) {
    var a = card.querySelector('.bb__c');
    a.addEventListener('click', function (e) { if (e.metaKey || e.ctrlKey || e.shiftKey || e.button) return; e.preventDefault(); open(i, a); });
  });
  dlg.querySelector('.am__x').addEventListener('click', function () { dlg.close(); });
  dlg.querySelector('.am__p').addEventListener('click', function () { show(cur - 1); });
  dlg.querySelector('.am__n').addEventListener('click', function () { show(cur + 1); });
  dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
  dlg.addEventListener('keydown', function (e) { if (e.key === 'ArrowRight') { show(cur + 1); } else if (e.key === 'ArrowLeft') { show(cur - 1); } });
  dlg.addEventListener('close', function () { document.documentElement.classList.remove('am-lock'); if (opener) opener.focus({ preventScroll: true }); });
})();
