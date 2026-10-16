/* booking.js — the callback form on every page.
 *
 * The form works without this file: the browser posts it and lands on /thank-you/.
 * With it, the request is sent in the background and the thank-you panel takes the
 * form's place, so the page never reloads and nothing typed is lost on an error.
 *
 * It also: carries the UTM tags from a Google Business listing into the lead and
 * preselects the clinic they name, and hides the mobile action bar while the form
 * is on screen, so the bar never covers the field being typed into.
 */
(function () {
  'use strict';
  var form = document.getElementById('bp-form');
  if (!form) return;

  var thanks = document.getElementById('bp-thanks');
  var submit = form.querySelector('.bp-submit');
  var SENDING = 'Sending…';

  /* ---- the Google Business listing names the clinic, so start on it ---------- */
  var q = new URLSearchParams(location.search);
  ['utm_source', 'utm_medium', 'utm_campaign'].forEach(function (k) {
    var input = form.querySelector('input[name="' + k + '"]');
    if (input) input.value = q.get(k) || '';
  });
  var medium = (q.get('utm_medium') || '').toLowerCase();
  var named = { delhi: 'delhi', newdelhi: 'delhi', gurgaon: 'gurugram', gurugram: 'gurugram', online: 'online' }[medium.replace(/[^a-z]/g, '')];
  if (named) {
    var pick = form.querySelector('input[name="clinic"][value="' + named + '"]');
    if (pick) pick.checked = true;
  }

  /* ---- errors, shown next to the field they belong to ----------------------- */
  function clearErrors() {
    form.querySelectorAll('.bp-err').forEach(function (e) { e.hidden = true; e.textContent = ''; });
    form.querySelectorAll('[aria-invalid]').forEach(function (e) { e.removeAttribute('aria-invalid'); });
  }

  function showErrors(errors) {
    var first = null;
    Object.keys(errors).forEach(function (name) {
      var slot = document.getElementById('bp-' + name + '-e');
      if (slot) { slot.textContent = errors[name]; slot.hidden = false; }
      var field = form.querySelector('[name="' + name + '"]');
      if (field) {
        field.setAttribute('aria-invalid', 'true');
        if (!first) first = field;
      }
    });
    if (first) first.focus();
  }

  if (q.get('booking') === 'invalid') {
    showErrors({ name: 'Something in the form was not accepted. Please check the details and send it again.' });
  }

  /* ---- send ----------------------------------------------------------------- */
  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    clearErrors();
    submit.disabled = true;
    var was = submit.textContent;
    submit.textContent = SENDING;

    var data = {};
    new FormData(form).forEach(function (value, key) { data[key] = value; });

    fetch(form.action, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(function (r) {
      return r.json().then(function (body) { return { status: r.status, body: body }; });
    }).then(function (r) {
      if (r.status === 400 && r.body.errors) { showErrors(r.body.errors); return; }
      if (!r.body.ok) throw new Error('rejected');
      form.hidden = true;
      thanks.hidden = false;
      thanks.querySelector('h3').focus();
    }).catch(function () {
      showErrors({ name: 'That did not send. Please try again, or call the clinic and the team will book you in.' });
    }).then(function () {
      submit.disabled = false;
      submit.textContent = was;
    });
  });

  /* ---- the mobile bar steps aside while the form is on screen ---------------- */
  var bar = document.querySelector('.actbar');
  if (bar && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { bar.classList.toggle('actbar--away', e.isIntersecting); });
    }, { threshold: 0.2 }).observe(form.closest('.bp') || form);
  }
})();
