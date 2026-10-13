/* Resources hub: filter articles by topic and reveal them a page at a time. */
(function () {
  'use strict';
  var grid = document.getElementById('hb-grid'), more = document.getElementById('hb-more');
  if (!grid) return;
  var cards = Array.prototype.slice.call(grid.children), chips = Array.prototype.slice.call(document.querySelectorAll('.hb-chip')),
      empty = document.querySelector('.hb-empty'), topic = 'all', shown = 10, STEP = 9;

  function apply() {
    var match = cards.filter(function (c) { return topic === 'all' || c.getAttribute('data-topic') === topic; });
    cards.forEach(function (c) { c.hidden = true; });
    match.forEach(function (c, i) { c.hidden = i >= shown; });
    more.hidden = match.length <= shown;
    empty.hidden = match.length > 0;
  }
  chips.forEach(function (b) {
    b.addEventListener('click', function () {
      topic = b.getAttribute('data-topic'); shown = 10;
      chips.forEach(function (c) { c.setAttribute('aria-pressed', c === b ? 'true' : 'false'); });
      apply();
    });
  });
  more.addEventListener('click', function () {
    var first = shown; shown += STEP; apply();
    var next = cards.filter(function (c) { return !c.hidden; })[first];
    if (next) next.querySelector('a').focus({ preventScroll: true });
  });
  apply();
})();
