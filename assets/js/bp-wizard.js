/* Turns the booking form into one question at a time: Your name -> Mobile number -> Who it's
 * for -> Where -> What's the concern -> send. Pure progressive enhancement: tools/booking.py
 * wraps each field in a plain <div class="bp-step">, and without this script every step shows
 * at once -- the form is exactly what it always was, one page, one submit, same required
 * fields. This script only changes how it's presented.
 *
 * Required-ness is never changed here: a step only blocks "Continue" if its own field already
 * carries the `required` attribute from booking.py (name, phone). The optional steps (who has
 * a default, clinic and concern have none) always let you continue, exactly as a plain
 * one-page form would accept them.
 *
 * Server-side errors (booking.js, after a failed submit) land as aria-invalid on a field that
 * may be on an earlier, hidden step -- a MutationObserver here jumps back to it automatically.
 */
(function () {
  'use strict';
  var form = document.getElementById('bp-form');
  if (!form) return;
  var steps = [].slice.call(form.querySelectorAll('.bp-step'));
  if (steps.length < 2) return; // nothing to turn into a wizard

  form.classList.add('is-wizard');
  var submit = form.querySelector('.bp-submit');
  var current = 0;

  var LABELS = { name: 'Your name', phone: 'Mobile number', who: 'Who it’s for', clinic: 'Where', concern: 'Your message' };

  // ---- progress chrome, inserted once, right before the first step ------------------------
  var prog = document.createElement('div');
  prog.className = 'bp-prog';
  prog.innerHTML = '<span class="bp-prog__n" id="bp-prog-n"></span><span class="bp-prog__track"><i class="bp-prog__b"></i></span>';
  steps[0].parentNode.insertBefore(prog, steps[0]);
  var progN = prog.querySelector('#bp-prog-n');
  var progB = prog.querySelector('.bp-prog__b');
  var live = document.createElement('p');
  live.className = 'bp-sr'; live.setAttribute('aria-live', 'polite');
  form.insertBefore(live, prog);

  // ---- nav buttons: a Back on every step but the first, a Continue on every step but the last
  steps.forEach(function (step, i) {
    if (i > 0) {
      var back = document.createElement('button');
      back.type = 'button'; back.className = 'btn ghost bp-back';
      back.textContent = '← Back';
      back.addEventListener('click', function () { go(i - 1); });
      step.insertBefore(back, step.firstChild);
    }
    if (i < steps.length - 1) {
      var cont = document.createElement('button');
      cont.type = 'button'; cont.className = 'btn bp-continue';
      cont.textContent = 'Continue →';
      cont.addEventListener('click', function () { if (stepValid(step)) go(i + 1); });
      step.appendChild(cont);
    }
  });

  // Enter in a single-line field continues instead of attempting to submit the whole form
  form.addEventListener('keydown', function (e) {
    if (e.key !== 'Enter') return;
    var t = e.target;
    if (t.tagName === 'TEXTAREA') return;
    var step = t.closest ? t.closest('.bp-step') : null;
    if (!step) return;
    var i = steps.indexOf(step);
    if (i < 0 || i === steps.length - 1) return; // last step: let Enter submit normally
    e.preventDefault();
    if (stepValid(step)) go(i + 1);
  });

  function stepValid(step) {
    var invalid = [].slice.call(step.querySelectorAll('input[required], textarea[required]')).find(function (el) { return !el.checkValidity(); });
    if (invalid) { invalid.reportValidity(); return false; }
    return true;
  }

  function go(i) {
    current = i;
    steps.forEach(function (s, n) { s.classList.toggle('is-active', n === i); });
    progN.textContent = 'Step ' + (i + 1) + ' of ' + steps.length;
    progB.style.width = ((i + 1) / steps.length * 100) + '%';
    var name = steps[i].dataset.step;
    live.textContent = 'Step ' + (i + 1) + ' of ' + steps.length + ': ' + (LABELS[name] || '');
    var field = steps[i].querySelector('input:not([type=hidden]),textarea');
    if (field) field.focus({ preventScroll: true });
    steps[i].scrollIntoView({ block: 'nearest', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  }
  go(0);

  // a server-side error (booking.js, after submit) can land on a field in a step that is
  // currently hidden -- surface it by jumping back to that step
  new MutationObserver(function (muts) {
    muts.forEach(function (m) {
      if (m.attributeName !== 'aria-invalid') return;
      var step = m.target.closest('.bp-step');
      if (step) go(steps.indexOf(step));
    });
  }).observe(form, { attributes: true, attributeFilter: ['aria-invalid'], subtree: true });

  // the real submit button lives on the last step already; nothing else to wire here
  if (submit) submit.classList.add('bp-submit--wiz');
})();
