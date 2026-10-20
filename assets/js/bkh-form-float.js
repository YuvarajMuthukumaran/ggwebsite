/* Contact page only: floats the booking form card into the hero, top-right, overlapping the
 * scrolling photo strip. Above a width where it can actually sit over the strip without
 * crowding it, the rest of the booking section -- the "Ask for a call back" facts card, which
 * just repeats what the floated form already says -- is hidden rather than left behind as an
 * empty, titled gap; any link that points at #book (the hero's own CTA, "Ask for an online
 * consultation", etc.) is retargeted to scroll to and focus the floated form instead, since the
 * section it would normally jump to is the one just hidden. Below that width everything moves
 * straight back to its original, stacked place (restoring the exact original position, not
 * just appending), so narrow screens get the plain, full layout, #book included.
 */
(function () {
  var hero = document.querySelector('.bkh');
  var strip = hero && hero.querySelector('.bkh__strip');
  var formCol = document.querySelector('.bp__r');
  var bpIn = document.querySelector('.bp__in');
  var bp = bpIn && bpIn.closest('.bp');
  if (!hero || !strip || !formCol || !bpIn || !bp) return;

  var anchor = document.createComment('bkh-form-anchor');
  formCol.parentNode.insertBefore(anchor, formCol);
  var floating = false;
  var mq = matchMedia('(min-width: 900px)');
  var reduceMq = matchMedia('(prefers-reduced-motion: reduce)');

  function float() {
    if (floating) return;
    strip.appendChild(formCol);
    hero.classList.add('bkh--has-form');
    bpIn.classList.add('bp__in--solo');
    bp.hidden = true;
    floating = true;
  }
  function restore() {
    if (!floating) return;
    anchor.parentNode.insertBefore(formCol, anchor);
    hero.classList.remove('bkh--has-form');
    bpIn.classList.remove('bp__in--solo');
    bp.hidden = false;
    floating = false;
  }
  function sync() { if (mq.matches) float(); else restore(); }
  sync();
  mq.addEventListener ? mq.addEventListener('change', sync) : mq.addListener(sync);

  document.addEventListener('click', function (e) {
    if (!floating) return;
    var a = e.target.closest && e.target.closest('a[href="#book"]');
    if (!a) return;
    e.preventDefault();
    formCol.scrollIntoView({ behavior: reduceMq.matches ? 'auto' : 'smooth', block: 'center' });
    var first = formCol.querySelector('#bp-name');
    if (first) first.focus({ preventScroll: true });
  });
})();
