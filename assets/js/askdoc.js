/* Ask the Doctor: a chat with Dr. Gorav Gupta's assistant.
   Talks to the Tulasi chatbot service (POST /api/session, then POST /api/chat, a stream of "data: {...}" lines) on the "gorav" channel.
   The input is the "placeholders and vanish" field: placeholders rotate every 3 s, and on send the typed text breaks into particles.
   Nothing is stored in the browser except the session id for this tab. */
(function () {
  'use strict';
  var root = document.getElementById('gc');
  if (!root) return;
  var log = document.getElementById('gc-log'), chips = document.getElementById('gc-chips'), form = document.getElementById('gc-form'),
      input = document.getElementById('gc-in'), send = document.getElementById('gc-send'), ph = document.getElementById('gc-ph'),
      cv = document.getElementById('gc-cv'), statusEl = document.getElementById('gc-status'), newBtn = document.getElementById('gc-new');
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var local = /^(127\.0\.0\.1|localhost)$/.test(location.hostname);
  var bases = (local ? [root.getAttribute('data-api-local')] : []).concat(['/chat-api']);   // /chat-api is passed on to the chat service by the host (vercel.json), so no cross-site call
  var base = bases[0], sid = null, busy = false, crisisLines = null;
  var PLACEHOLDERS = ['Is mental illness treatable?', 'Will I need medicine for life?', 'When does someone need to be admitted?', 'How can my family help?', 'What happens at a first consultation?'];
  var SUGGEST = ['Is mental illness treatable?', 'What is the role of counselling?', 'Will medicine be needed for life?', 'When should someone be admitted?', 'How can family members help?', 'What happens at a first consultation?'];

  /* ------------------------------------------------------------ rendering */
  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function md(t) {   // only what the assistant uses: **bold**, paragraphs, line breaks and "- " lists
    var html = esc(t).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>');
    return html.split(/\n{2,}/).map(function (para) {
      var lines = para.split('\n');
      if (lines.every(function (l) { return /^\s*[-*•]\s+/.test(l); })) return '<ul>' + lines.map(function (l) { return '<li>' + l.replace(/^\s*[-*•]\s+/, '') + '</li>'; }).join('') + '</ul>';
      return lines.map(function (l) { return /^\s*[-*•]\s+/.test(l) ? '&bull; ' + l.replace(/^\s*[-*•]\s+/, '') : l; }).join('<br>');
    }).join('</p><p>');
  }
  function scroll() { log.scrollTop = log.scrollHeight; }
  function bubble(who, html, cls) {
    var row = document.createElement('div');
    row.className = 'gc__m gc__m--' + who + (cls ? ' ' + cls : '');
    if (who === 'bot') row.innerHTML = '<span class="gc__mav" aria-hidden="true"></span><div class="gc__b"><p>' + html + '</p></div>';
    else row.innerHTML = '<div class="gc__b"><p>' + html + '</p></div>';
    log.appendChild(row); scroll();
    return row;
  }
  function typing() { return bubble('bot', '<span class="gc__dots" aria-label="Typing"><i></i><i></i><i></i></span>', 'gc__m--typing'); }
  function setChips(list) {
    chips.innerHTML = '';
    (list || []).forEach(function (q) {
      var b = document.createElement('button'); b.type = 'button'; b.textContent = q;
      b.addEventListener('click', function () { ask(q); }); chips.appendChild(b);
    });
  }
  function actions(row, items) {
    if (!items.length) return;
    var d = document.createElement('div'); d.className = 'gc__acts'; d.innerHTML = items.join('');
    row.querySelector('.gc__b').appendChild(d); scroll();
  }

  /* ------------------------------------------------------------ service */
  function timeout(ms) { var c = new AbortController(); var t = setTimeout(function () { c.abort(); }, ms); return { signal: c.signal, done: function () { clearTimeout(t); } }; }
  function newSession() {
    statusEl.textContent = 'Connecting…';
    var i = 0;
    function tryBase() {
      var to = timeout(25000);   // a sleeping host can take a while to wake
      return fetch(bases[i] + (/^\//.test(bases[i]) ? '/session/' : '/api/session'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ channel: 'gorav' }), signal: to.signal })
        .then(function (r) { to.done(); if (!r.ok) throw new Error('session'); return r.json(); })
        .then(function (j) { if (j.channel !== 'gorav') { var o = new Error('old'); o.old = true; throw o; } base = bases[i]; sid = j.sessionId; crisisLines = j.crisisResources && j.crisisResources.lines; statusEl.textContent = 'AI assistant · replies in seconds'; })
        .catch(function (e) { to.done(); if (++i < bases.length) return tryBase(); statusEl.textContent = e && e.old ? 'Being set up' : 'Offline'; throw e; });
    }
    return tryBase();
  }
  function stream(message, onText, onEvent) {
    return fetch(base + (/^\//.test(base) ? '/chat/' : '/api/chat'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ sessionId: sid, message: message }) }).then(function (r) {
      if (r.status === 404) { var e = new Error('gone'); e.gone = true; throw e; }
      if (!r.ok) { return r.json().catch(function () { return {}; }).then(function (j) { var e = new Error('http'); e.msg = j.error; throw e; }); }
      var rd = r.body.getReader(), dec = new TextDecoder(), buf = '';
      function pump() {
        return rd.read().then(function (x) {
          if (x.done) return;
          buf += dec.decode(x.value, { stream: true });
          var parts = buf.split('\n\n'); buf = parts.pop();
          parts.forEach(function (p) {
            var line = p.replace(/^data:\s*/, '').trim();
            if (!line || line === '[DONE]') return;
            try { var o = JSON.parse(line); if (o.text) onText(o.text); onEvent(o); } catch (_) { /* a partial line; ignore */ }
          });
          return pump();
        });
      }
      return pump();
    });
  }

  function ask(message) {
    message = (message || '').trim();
    if (!message || busy) return;
    busy = true; send.disabled = true; setChips([]);
    bubble('me', esc(message));
    var t = typing(), row = null, text = '', events = {};
    function onText(chunk) {
      text += chunk;
      if (!row) { t.remove(); row = bubble('bot', ''); }
      row.querySelector('.gc__b').firstChild.innerHTML = md(text);
      scroll();
    }
    function onEvent(o) { Object.keys(o).forEach(function (k) { if (k !== 'text') events[k] = o[k]; }); }
    function finish() {
      if (t.parentNode) t.remove();
      if (row) {
        var items = [];
        if (events.error) { row.classList.add('gc__m--err'); items.push('<a class="btn ghost" href="' + esc(root.getAttribute('data-phone')) + '">Call ' + esc(root.getAttribute('data-phone-text')) + '</a>'); }
        if (events.crisis) {
          row.classList.add('gc__m--crisis');
          (crisisLines || []).filter(function (l) { return l.phone && l.type !== 'text'; }).forEach(function (l) {
            items.push('<a class="btn" href="tel:' + esc(String(l.phone).replace(/[^\d+]/g, '')) + '">Call ' + esc(l.name) + ' ' + esc(l.phone) + '</a>');
          });
        }
        if (events.action === 'book') items.push('<a class="btn" href="' + esc(root.getAttribute('data-book')) + '">Request a callback</a>');
        if (events.action === 'portal') items.push('<a class="btn" href="' + esc(root.getAttribute('data-phone')) + '">Call ' + esc(root.getAttribute('data-phone-text')) + '</a>');
        if (events.doctors && events.doctors.length) items.push('<a class="btn ghost" href="' + esc(root.getAttribute('data-book')) + '">Book with ' + esc(events.doctors[0].name) + '</a>');
        actions(row, items);
      }
      setChips(events.quickReplies && events.quickReplies.length ? events.quickReplies : []);
      busy = false; send.disabled = !input.value.trim(); input.focus({ preventScroll: true });
    }
    function failed(msg) {
      if (t.parentNode) t.remove();
      var r = bubble('bot', esc(msg || 'I could not reach the chat just now. Please try again, or call the clinic on ' + root.getAttribute('data-phone-text') + '.'), 'gc__m--err');
      actions(r, ['<a class="btn ghost" href="' + esc(root.getAttribute('data-phone')) + '">Call ' + esc(root.getAttribute('data-phone-text')) + '</a>']);
      busy = false; send.disabled = !input.value.trim();
    }
    var go = sid ? Promise.resolve() : newSession();
    go.then(function () { return stream(message, onText, onEvent); })
      .catch(function (e) {
        if (e.gone) { sid = null; return newSession().then(function () { return stream(message, onText, onEvent); }); }
        throw e;
      })
      .then(function () {
        if (events.error && !row) return failed(text);
        finish();
      })
      .catch(function (e) { failed(e && e.old ? 'The chat assistant is being set up and is not available just yet. Please call the clinic, or request a callback and the team will get back to you.' : e && e.msg); });
  }

  function start() {
    log.innerHTML = '';
    bubble('bot', 'Hello, I&rsquo;m Dr. Gorav Gupta&rsquo;s assistant. Ask me anything about mental health, addiction, treatment or what a consultation involves, and I&rsquo;ll answer in plain words.<br><br>I can&rsquo;t diagnose, and for anything personal Dr. Gupta or his team will need to see you.');
    setChips(SUGGEST);
    sid = null; busy = false;
    newSession().catch(function () { /* the first question retries */ });
  }
  newBtn.addEventListener('click', function () { if (sid) fetch(base + (/^\//.test(base) ? '/session/' : '/api/session/') + sid + (/^\//.test(base) ? '/' : ''), { method: 'DELETE' }).catch(function () {}); start(); input.value = ''; syncSend(); });

  /* ------------------------------------------------------------ the input: rotating placeholder and vanish */
  var pi = 0, timer = 0;
  function showPh() { ph.textContent = PLACEHOLDERS[pi]; ph.classList.remove('is-in'); void ph.offsetWidth; ph.classList.add('is-in'); }
  function startPh() { if (timer || reduce) return; timer = setInterval(function () { pi = (pi + 1) % PLACEHOLDERS.length; showPh(); }, 3000); }
  function stopPh() { clearInterval(timer); timer = 0; }
  document.addEventListener('visibilitychange', function () { if (document.hidden) stopPh(); else startPh(); });
  showPh(); startPh();
  function syncSend() { var v = input.value.trim(); send.disabled = !v || busy; ph.hidden = !!input.value; }
  input.addEventListener('input', syncSend);

  function vanish(text, done) {
    if (reduce || !cv.getContext) return done();
    var W = 800, ctx = cv.getContext('2d');
    cv.width = W; cv.height = 200; ctx.clearRect(0, 0, W, 200);
    var cs = getComputedStyle(input), fs = parseFloat(cs.fontSize);
    ctx.font = (fs * 2) + 'px ' + cs.fontFamily; ctx.fillStyle = '#fff'; ctx.fillText(text, 16, 70);
    var d = ctx.getImageData(0, 0, W, 200).data, pts = [];
    for (var y = 0; y < 200; y += 2) for (var x = 0; x < W; x += 2) { var k = (y * W + x) * 4; if (d[k + 3] > 90) pts.push({ x: x, y: y, r: 2 }); }
    if (!pts.length) return done();
    cv.classList.add('is-on'); input.classList.add('is-gone');
    var pos = pts.reduce(function (m, p) { return Math.max(m, p.x); }, 0), t0 = performance.now();
    (function frame() {
      var next = [];
      pts.forEach(function (p) {
        if (p.x < pos) { next.push(p); return; }
        p.r -= .1 * Math.random(); if (p.r <= 0) return;
        p.x += Math.random() > .5 ? 1 : -1; p.y += Math.random() > .5 ? 1 : -1; next.push(p);
      });
      pts = next; ctx.clearRect(0, 0, W, 200); ctx.fillStyle = '#17335f';
      pts.forEach(function (p) { if (p.x >= pos - 1 || true) ctx.fillRect(p.x, p.y, p.r, p.r); });
      pos -= 12;
      if (pts.length && performance.now() - t0 < 900) requestAnimationFrame(frame);
      else { cv.classList.remove('is-on'); input.classList.remove('is-gone'); ctx.clearRect(0, 0, W, 200); }
    })();
    done();   // the message goes at once; the particles are only the exit
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var v = input.value.trim();
    if (!v || busy) return;
    vanish(v, function () { input.value = ''; syncSend(); ask(v); });
  });

  start();
})();
