/* yt.js: click-to-play YouTube thumbnails. No dependencies.
   A thumbnail stays an image until it is clicked, then becomes the privacy-friendly
   (youtube-nocookie) player. Twelve videos therefore cost twelve small images, not twelve players. */
(function () {
  'use strict';
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.yt__btn');
    if (!btn) return;
    var id = btn.getAttribute('data-id');
    if (!id) return;
    var f = document.createElement('iframe');
    f.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(id) + '?autoplay=1&rel=0';
    f.title = btn.getAttribute('aria-label') || 'Video';
    f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
    f.setAttribute('allowfullscreen', '');
    f.referrerPolicy = 'strict-origin-when-cross-origin';
    btn.parentNode.replaceChild(f, btn);
    f.focus();
  });
})();
