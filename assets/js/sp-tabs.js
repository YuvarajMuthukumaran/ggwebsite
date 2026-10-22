/* sp-tabs.js: on the three city pages (Delhi, Gurugram, India), the long run of "Achievements / Experience /
   Professional bodies / ..." sections reads as a lot of scrolling. This turns that block into a tab strip --
   one section showing at a time -- without removing any text: every heading and paragraph stays in the DOM,
   full and findable by a page search or a screen reader's "show all"; only the inactive panels are hidden. */
(function () {
  'use strict';
  var dls = [].slice.call(document.querySelectorAll('.sp-dl'));
  if (!dls.length) return;

  // the full heading, just tidied -- CSS truncates it to one line by default and reveals it in full on hover,
  // so a screen reader (which ignores the visual clipping) always gets the complete label either way
  function cleanLabel(text) {
    return text.replace(/\s+/g, ' ').trim().replace(/[:–—-]\s*$/, '');
  }

  dls.forEach(function (dl, dlIndex) {
    var rows = [].slice.call(dl.children).filter(function (c) { return c.classList.contains('sp-dl__r'); });
    if (rows.length < 2) return;

    var uid = 'sp-dl' + dlIndex;
    var tabs = document.createElement('div');
    tabs.className = 'sp-tabs';
    tabs.setAttribute('role', 'tablist');
    tabs.setAttribute('aria-label', 'Sections');

    rows.forEach(function (row, i) {
      var h = row.querySelector('h4');
      var label = h ? cleanLabel(h.textContent) : 'Section ' + (i + 1);
      var tabId = uid + '-tab-' + i;
      var panelId = row.id || (row.id = uid + '-panel-' + i);

      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'sp-tabs__t';
      btn.id = tabId;
      btn.setAttribute('role', 'tab');
      btn.setAttribute('aria-controls', panelId);
      btn.setAttribute('aria-selected', i === 0 ? 'true' : 'false');
      btn.tabIndex = i === 0 ? 0 : -1;
      btn.textContent = label;
      tabs.appendChild(btn);

      row.classList.add('sp-tabs__panel');
      row.setAttribute('role', 'tabpanel');
      row.setAttribute('aria-labelledby', tabId);
      if (i !== 0) row.hidden = true;

      btn.addEventListener('click', function () { activate(i, true); });
    });

    dl.classList.add('sp-tabs-wrap');
    dl.insertBefore(tabs, rows[0]);

    function activate(idx, animate) {
      rows.forEach(function (row, i) {
        var on = i === idx;
        var btn = tabs.children[i];
        btn.setAttribute('aria-selected', on ? 'true' : 'false');
        btn.tabIndex = on ? 0 : -1;
        row.hidden = !on;
        row.classList.toggle('is-in', on && animate);
      });
    }

    tabs.addEventListener('keydown', function (e) {
      var i = [].indexOf.call(tabs.children, document.activeElement);
      if (i === -1) return;
      var n = null;
      if (e.key === 'ArrowRight') n = (i + 1) % rows.length;
      else if (e.key === 'ArrowLeft') n = (i - 1 + rows.length) % rows.length;
      else if (e.key === 'Home') n = 0;
      else if (e.key === 'End') n = rows.length - 1;
      if (n === null) return;
      e.preventDefault();
      tabs.children[n].focus();
      activate(n, true);
    });

    // a direct link into a hidden panel (the "On this page" list, a shared link) opens that tab first
    dl._spTabsActivateFor = function (el) {
      var row = el.closest ? el.closest('.sp-tabs__panel') : null;
      if (!row) return false;
      var idx = rows.indexOf(row);
      if (idx === -1) return false;
      activate(idx, false);
      return true;
    };
  });

  // capture phase, not bubble: site.js's own "a[href^=#]" smooth-scroll handler sits directly on the link and
  // measures the target's position the moment it fires. A bubble-phase listener here would reveal the panel too
  // late -- after that measurement -- and the page would glide to where the heading used to be (inside a hidden,
  // zero-height row). Capture runs on the way down, before the link's own handler, so the panel is already open
  // and visible by the time site.js reads getBoundingClientRect().
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href*="#"]');
    if (!a) return;
    var hash = a.getAttribute('href').split('#')[1];
    if (!hash) return;
    var target = document.getElementById(hash);
    if (!target) return;
    dls.forEach(function (dl) { if (dl._spTabsActivateFor) dl._spTabsActivateFor(target); });
  }, true);

  // a page loaded straight at a #hash: the browser already tried to jump there before this (deferred) script
  // ran, landing nowhere useful if the target was hidden. Reveal the right panel, then finish the scroll by hand.
  if (location.hash) {
    var initial = document.getElementById(location.hash.slice(1));
    if (initial) {
      var opened = false;
      dls.forEach(function (dl) { if (dl._spTabsActivateFor && dl._spTabsActivateFor(initial)) opened = true; });
      if (opened) initial.scrollIntoView({ block: 'start' });
    }
  }
})();
