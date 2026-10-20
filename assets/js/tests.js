/* Interactive self-assessment tests: intro -> one question per screen -> result.
   The test is the JSON in #tq-data (built from data/tests/<slug>.json). Everything is worked out
   here, in the browser; answers are never stored or sent anywhere. */
(function () {
  'use strict';
  var d = document, app = d.getElementById('tq'), src = d.getElementById('tq-data');
  if (!app || !src) return;

  var T = JSON.parse(src.textContent);
  var N = T.questions.length;
  var screens = {};
  Array.prototype.forEach.call(app.querySelectorAll('[data-screen]'), function (s) { screens[s.getAttribute('data-screen')] = s; });
  var answers = [], at = 0, sub = T.placeholder ? T.placeholder['default'] : '', pointer = false, advanceT = 0;

  var CHECK = '<svg viewBox="0 0 256 256" fill="currentColor" aria-hidden="true"><path d="M229.66,77.66l-128,128a8,8,0,0,1-11.32,0l-56-56a8,8,0,0,1,11.32-11.32L96,188.69,218.34,66.34a8,8,0,0,1,11.32,11.32Z"/></svg>';
  var ALERT = '<svg viewBox="0 0 256 256" fill="currentColor" aria-hidden="true"><path d="M178,40c-20.65,0-38.73,8.88-50,23.89C116.73,48.88,98.65,40,78,40a62.07,62.07,0,0,0-62,62c0,70,103.79,126.66,108.21,129a8,8,0,0,0,7.58,0C136.21,228.66,240,172,240,102A62.07,62.07,0,0,0,178,40ZM128,214.8C109.74,204.16,32,155.69,32,102A46.06,46.06,0,0,1,78,56c19.45,0,35.78,10.36,42.6,27a8,8,0,0,0,14.8,0c6.82-16.67,23.15-27,42.6-27a46.06,46.06,0,0,1,46,46C224,155.61,146.24,204.15,128,214.8Z"/></svg>';

  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
  function words(s) { return T.placeholder ? s.split(T.placeholder.token).join(sub) : s; }
  function opts(q) { return q.options || T.scale; }
  /* Scored tests show each option's score (0-4) and take that number as its key; yes/no tests number from 1. */
  function keyOf(opt, k) { return T.scoring.type === 'sum' ? String(opt.value) : String(k + 1); }

  function show(name, focusEl) {
    Object.keys(screens).forEach(function (k) { screens[k].hidden = k !== name; });
    app.setAttribute('data-at', name);
    if (focusEl) focusEl.focus({ preventScroll: true });
    reveal(true);
  }

  /* Keep the card's top in view below the sticky nav (measured after the new screen has laid out). */
  function reveal(always) {
    requestAnimationFrame(function () {
      var top = app.getBoundingClientRect().top, nav = d.getElementById('nav'), gap = (nav ? nav.getBoundingClientRect().bottom : 0) + 16;
      if (top < gap || (always && top > innerHeight * .3)) glide(window.scrollY + top - gap);
    });
  }
  function glide(y) {   // a short eased scroll of our own, as in site.js (native smooth scrolling is not reliable everywhere)
    var y0 = window.scrollY, dy = y - y0, t0 = performance.now(), dur = 520;
    if (matchMedia('(prefers-reduced-motion: reduce)').matches || Math.abs(dy) < 4) { window.scrollTo(0, y); return; }
    (function f(now) {
      var p = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - p, 3);
      window.scrollTo(0, y0 + dy * e);
      if (p < 1) requestAnimationFrame(f);
    })(t0);
  }

  /* ---------------------------------------------------------------- intro */
  var startBtn = app.querySelector('[data-act="start"]'), subIn = d.getElementById('tq-sub');
  startBtn.disabled = false;
  startBtn.addEventListener('click', function () {
    if (subIn && subIn.value.trim()) sub = subIn.value.trim();
    answers = []; at = 0; render(); show('q', legend());
  });
  if (subIn) subIn.addEventListener('keydown', function (e) { if (e.key === 'Enter') startBtn.click(); });

  /* ---------------------------------------------------------------- questions */
  var qs = screens.q;
  qs.innerHTML =
    '<div class="tq-top"><p class="tq-count"><span id="tq-count" aria-live="polite"></span><span class="tq-pct" aria-hidden="true"></span></p>' +
    '<div class="tq-bar" role="progressbar" aria-label="Test progress" aria-valuemin="0" aria-valuemax="' + N + '"><i></i></div></div>' +
    '<div class="tq-stage"></div>' +
    '<div class="tq-nav"><button class="btn ghost tq-back" type="button"><i aria-hidden="true">←</i> Back</button>' +
    '<button class="btn tq-next" type="button" disabled>Next <i aria-hidden="true">→</i></button></div>' +
    '<p class="tq-kbd" aria-hidden="true">Keyboard: press an option’s number to answer · Enter for next · ← to go back</p>';
  var stage = qs.querySelector('.tq-stage'), bar = qs.querySelector('.tq-bar'), fill = bar.firstChild,
      count = d.getElementById('tq-count'), pct = qs.querySelector('.tq-pct'),
      back = qs.querySelector('.tq-back'), next = qs.querySelector('.tq-next');

  function legend() { return stage.querySelector('legend'); }

  function render() {
    var q = T.questions[at], o = opts(q), done = answers.filter(function (a) { return a != null; }).length;
    count.textContent = 'Question ' + (at + 1) + ' of ' + N;
    pct.textContent = Math.round(done / N * 100) + '% done';
    bar.setAttribute('aria-valuenow', String(at + 1));
    bar.setAttribute('aria-valuetext', 'Question ' + (at + 1) + ' of ' + N);
    fill.style.transform = 'scaleX(' + ((at + (answers[at] != null ? 1 : 0)) / N) + ')';
    var kicker = q.section ? q.section : (q.title || '');
    stage.innerHTML =
      '<fieldset class="tq-q"><legend tabindex="-1">' +
      (kicker ? '<span class="tq-q__k">' + esc(kicker) + '</span>' : '') +
      '<span class="tq-q__t">' + esc(words(q.text)) + '</span></legend>' +
      (q.help ? '<p class="tq-q__h">' + esc(q.help) + '</p>' : '') +
      (q.sensitive ? crisis(true) : '') +
      '<div class="tq-opts' + (o.length <= 2 ? ' tq-opts--2' : '') + '">' +
      o.map(function (opt, k) {
        return '<label class="tq-opt"><input type="radio" name="tq-a" value="' + k + '"' + (answers[at] === k ? ' checked' : '') + '>' +
          '<span class="tq-opt__k" aria-hidden="true">' + keyOf(opt, k) + '</span>' +
          '<span class="tq-opt__b"><b>' + esc(opt.label) + '</b>' + (opt.hint ? '<small>' + esc(opt.hint) + '</small>' : '') + '</span>' +
          '<span class="tq-opt__c" aria-hidden="true">' + CHECK + '</span></label>';
      }).join('') + '</div></fieldset>';
    stage.classList.remove('tq-enter'); void stage.offsetWidth; stage.classList.add('tq-enter');
    next.disabled = answers[at] == null;
    next.innerHTML = at === N - 1 ? 'See my result <i aria-hidden="true">→</i>' : 'Next <i aria-hidden="true">→</i>';
  }

  function go(step) {
    clearTimeout(advanceT);
    if (step > 0 && answers[at] == null) return;
    at += step;
    if (at < 0) { at = 0; show('intro', screens.intro.querySelector('.tq-h')); return; }
    if (at >= N) { at = N - 1; result(); return; }
    render(); legend().focus({ preventScroll: true }); reveal(false);
  }

  function choose(k, auto) {
    answers[at] = k;
    var r = stage.querySelector('input[value="' + k + '"]');
    if (r) r.checked = true;
    next.disabled = false;
    fill.style.transform = 'scaleX(' + ((at + 1) / N) + ')';
    clearTimeout(advanceT);
    if (auto && at < N - 1) advanceT = setTimeout(function () { go(1); }, 420);   // a beat to see the choice land
    if (auto && at === N - 1) next.focus();
  }

  stage.addEventListener('pointerdown', function (e) { pointer = !!e.target.closest('.tq-opt'); });
  stage.addEventListener('change', function (e) {
    if (e.target.name !== 'tq-a') return;
    choose(+e.target.value, pointer);   // arrow keys inside the group change the choice without moving on
    pointer = false;
  });
  back.addEventListener('click', function () { go(-1); });
  next.addEventListener('click', function () { go(1); });

  d.addEventListener('keydown', function (e) {
    if (qs.hidden || e.altKey || e.ctrlKey || e.metaKey) return;
    var tag = e.target.tagName, o = opts(T.questions[at]);
    if (tag === 'INPUT' && e.target.type === 'text') return;
    var hit = o.map(keyOf).indexOf(e.key);
    if (hit > -1) { e.preventDefault(); choose(hit, true); return; }
    if (e.target.type === 'radio' && (e.key === 'ArrowLeft' || e.key === 'ArrowRight')) return;
    if (e.key === 'ArrowLeft') { e.preventDefault(); go(-1); }
    else if (e.key === 'ArrowRight' || (e.key === 'Enter' && tag !== 'BUTTON' && tag !== 'A')) {
      if (answers[at] != null) { e.preventDefault(); go(1); }
    }
  });

  /* ---------------------------------------------------------------- result */
  function crisis(strong) {
    return '<div class="tq-crisis' + (strong ? ' tq-crisis--on' : '') + '" role="note" aria-label="Crisis support">' + ALERT +
      '<div><p class="tq-crisis__t">Need support right now?</p>' +
      '<p>If you feel unsafe or are having thoughts of harming yourself, please reach out now. Call <a href="tel:14416">Tele-MANAS 14416</a> ' +
      '(or <a href="tel:18008914416">1-800-891-4416</a>), India’s free, confidential 24×7 mental health helpline, or dial <a href="tel:112">112</a> ' +
      'for emergency services. You can also go to the nearest hospital emergency department.</p></div></div>';
  }

  function result() {
    var sc = T.scoring, score = 0, keyHit = false, sensitiveHit = false;
    T.questions.forEach(function (q, i) {
      var opt = opts(q)[answers[i]];
      if (sc.type === 'count') { if (opt.flag) { score++; if (q.key) keyHit = true; } }
      else score += opt.value;
      if (q.sensitive && opt.value > 0) sensitiveHit = true;
    });
    var band = sc.bands.filter(function (b) { return score >= b.min && score <= b.max; })[0] || sc.bands[sc.bands.length - 1];
    var urgent = !!band.urgent || sensitiveHit;

    var meter = sc.bands.map(function (b) {
      return '<span class="tq-seg" data-level="' + b.level + '" style="flex-grow:' + (b.max - b.min + 1) + '"' + (b === band ? ' data-on' : '') + '></span>';
    }).join('');
    var pos = (score - sc.bands[0].min + .5) / (sc.max - sc.bands[0].min + 1) * 100;   // centre of its unit, matching the segment widths
    var scoreLine = sc.type === 'count'
      ? '<b>' + score + '</b> <span>of ' + N + ' ' + esc(sc.score_label || 'answers') + '</span>'
      : '<b>' + score + '</b> <span>out of ' + sc.max + '</span>';
    var list = T.questions.map(function (q, i) {
      return '<li><span>' + esc(words(q.text)) + '</span><b>' + esc(opts(q)[answers[i]].label) + '</b></li>';
    }).join('');

    /* Each band earns a different next step: a low score does not need a consultation,
       and a high one should not be offered a reading list. */
    var root = app.getAttribute('data-root') || '';
    var phone = app.getAttribute('data-phone') || 'tel:+918800000255';
    var article = T.source && T.source.page && T.source.page !== 'mental-health-assessment-tests'
      ? root + T.source.page + '/' : root + 'services/';
    var level = band.level === 'mild' ? 'low' : band.level;
    var step = {
      low: {
        t: 'Keep an eye on it',
        p: 'Nothing here points to a problem that needs treatment today. If this changes, or it has been going on a while, a conversation is still worth having.',
        a: '<a class="btn ghost" href="' + article + '">Read more about this <i aria-hidden="true">→</i></a>' +
           '<a class="btn ghost" href="' + app.getAttribute('data-contact') + '">Book a consultation</a>'
      },
      moderate: {
        t: 'Worth talking to someone',
        p: 'A score in this range is usually worth an assessment. Dr. Gupta consults in New Delhi, Gurugram and online; bring this result with you.',
        a: '<a class="btn" href="' + app.getAttribute('data-contact') + '">Book a consultation</a>' +
           '<a class="btn ghost" href="' + article + '">Read more about this</a>'
      },
      high: {
        t: 'Please speak to someone soon',
        p: 'A score in this range should not wait. Call the clinic and the team will find you a time; if you feel unsafe, use the helpline above instead.',
        a: '<a class="btn" href="' + phone + '">Call the clinic now</a>' +
           '<a class="btn ghost" href="' + app.getAttribute('data-contact') + '">Book a consultation</a>'
      }
    }[level] || null;

    /* Sending the result is the patient's choice: it goes nowhere unless this is tapped. */
    var wanum = app.getAttribute('data-wanum');
    var shareWa = '';
    if (wanum) {
      var msg = "Hello Dr. Gupta's team, I took the " + T.title + ' on goravgupta.com. My result was "'
        + band.label + '" (' + (sc.type === 'count' ? score + ' of ' + N : score + ' out of ' + sc.max)
        + '). I would like to book a consultation.';
      shareWa = '<a class="btn wa" href="https://wa.me/' + wanum + '?text=' + encodeURIComponent(msg)
        + '" target="_blank" rel="noopener">Share my result with the team</a>';
    }

    screens.result.innerHTML =
      '<div class="tq-res__head" data-level="' + band.level + '">' +
      '<p class="tq-res__k">Your result</p>' +
      '<h2 class="tq-h" tabindex="-1"><span class="tq-res__band"><i aria-hidden="true"></i>' + esc(band.label) + '</span></h2>' +
      '<p class="tq-res__score">' + scoreLine + '</p>' +
      '<div class="tq-meter" aria-hidden="true"><div class="tq-meter__bar">' + meter + '</div><span class="tq-meter__pin" style="left:' + pos + '%"></span>' +
      '<div class="tq-meter__ends"><span>0</span><span>' + sc.max + '</span></div></div>' +
      '<p class="tq-res__txt">' + esc(band.text) + '</p>' +
      (keyHit && sc.key_note ? '<p class="tq-res__txt tq-res__key">' + esc(sc.key_note) + '</p>' : '') +
      '</div>' +
      crisis(urgent) +
      '<div class="tq-res__next" data-level="' + band.level + '"><h3>' + (step ? esc(step.t) : 'What to do next') + '</h3>' +
      (step ? '<p>' + esc(step.p) + '</p>' : '') +
      (T.next_steps ? '<p>' + esc(T.next_steps) + '</p>' : '') + '<p>' + esc(T.note) + '</p>' +
      (step ? '<div class="tq-res__acts">' + step.a + '</div>' : '') + '</div>' +
      '<div class="tq-cta"><img class="tq-cta__doc" src="' + app.getAttribute('data-doc') + '" alt="Dr. Gorav Gupta" width="72" height="84" loading="lazy"><div><p class="tq-cta__t">Talk it through with a specialist</p>' +
      '<p>Dr. Gorav Gupta consults in New Delhi, Gurugram and online. Bring this result along; it is a good place to start the conversation.</p></div>' +
      '<div class="tq-cta__a"><a class="btn" href="' + app.getAttribute('data-contact') + '">Book a consultation with Dr. Gorav Gupta</a>' +
      '<a class="btn ghost" href="' + phone + '">Call the clinic</a>' + shareWa + '</div></div>' +
      '<div class="tq-acts"><button type="button" class="tq-act" data-act="retake">Retake the test</button>' +
      '<button type="button" class="tq-act" data-act="print">Print</button>' +
      '<button type="button" class="tq-act" data-act="share">Share this test</button>' +
      '<a class="tq-act" href="' + app.getAttribute('data-index') + '">Other tests</a>' +
      '<span class="tq-status" role="status" aria-live="polite"></span></div>' +
      '<details class="tq-ans"><summary>Your answers</summary><ol>' + list + '</ol></details>' +
      '<p class="tq-disc">This is a screening tool, not a diagnosis. Only a qualified professional can assess and diagnose a mental health condition. ' +
      'Your answers were worked out on this device and have not been saved or sent.</p>';

    show('result', screens.result.querySelector('.tq-h'));
  }

  screens.result.addEventListener('click', function (e) {
    var b = e.target.closest('[data-act]');
    if (!b) return;
    var act = b.getAttribute('data-act'), status = screens.result.querySelector('.tq-status');
    if (act === 'retake') { answers = []; at = 0; render(); show('q', legend()); }
    else if (act === 'print') {
      var det = screens.result.querySelector('.tq-ans'), was = det.open;
      det.open = true; window.print(); det.open = was;
    } else if (act === 'share') {
      var url = location.href.split('#')[0];   // the test page only; results are never part of the link
      if (navigator.share) navigator.share({ title: T.title, text: 'A private self-assessment from Dr. Gorav Gupta', url: url }).catch(function () {});
      else if (navigator.clipboard) navigator.clipboard.writeText(url).then(function () { status.textContent = 'Link to this test copied.'; }, function () { status.textContent = url; });
      else status.textContent = url;
    }
  });
})();
