/* faq.js: FAQ pages (tools/faq_pages.py). Two small things:
   1. "Expand all" / "Collapse all" for the questions on a topic page.
   2. A link to a question (/faq/<topic>/#q-...) opens that question and scrolls to it. */
(function () {
  var d = document;
  var list = d.querySelector('.fq__main .fq-list');
  var tog = d.querySelector('[data-fq-all]');

  function items() { return [].slice.call(d.querySelectorAll('.fq__main .fq-q')); }

  if (list && tog) {
    var label = function () {
      var all = items().every(function (q) { return q.open; });
      tog.textContent = all ? 'Collapse all' : 'Expand all';
      tog.setAttribute('aria-pressed', all ? 'true' : 'false');
    };
    tog.addEventListener('click', function () {
      var open = tog.getAttribute('aria-pressed') !== 'true';
      items().forEach(function (q) { q.open = open; });
      label();
    });
    items().forEach(function (q) { q.addEventListener('toggle', label); });
    label();
  }

  function fromHash() {
    var id = decodeURIComponent((location.hash || '').slice(1));
    var q = id && d.getElementById(id);
    if (q && q.tagName === 'DETAILS') {
      q.open = true;
      setTimeout(function () { q.scrollIntoView({ block: 'start', behavior: 'smooth' }); }, 150);
    }
  }
  addEventListener('hashchange', fromHash);
  fromHash();
})();
