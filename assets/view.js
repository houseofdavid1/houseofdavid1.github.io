/* View mode + mobile menu.
   Default: responsive (mobile layout on phones). Phones may opt into the desktop layout; the choice is remembered.
   Must load synchronously at the top of <head>; it writes the viewport meta itself. */
(function () {
  var KEY = 'ptl-view', DESK = 1280;
  var sw = Math.min(screen.width || DESK, screen.height || DESK);
  var small = sw < 900;
  var mode = 'mobile';
  // The desktop choice lasts for this visit only (sessionStorage): every new visit starts in the mobile layout.
  try { localStorage.removeItem(KEY); } catch (e) {}          // drop the old, permanent preference
  try { if (sessionStorage.getItem(KEY) === 'desktop') mode = 'desktop'; } catch (e) {}
  if (!small) mode = 'mobile';                       // large screens: plain responsive layout
  // The viewport meta is written here (not in the HTML) so the browser sees the right width AND zoom on first layout.
  // Desktop layout on a phone: give an explicit zoom so the full 1280px page fits edge to edge.
  // (Some browsers, notably iOS Safari, keep scale 1 if only the width changes.)
  function deskVP() {
    var land = window.matchMedia && matchMedia('(orientation: landscape)').matches;
    var w = land ? Math.max(screen.width, screen.height) : Math.min(screen.width, screen.height);
    var z = Math.min(1, w / DESK).toFixed(4);
    return 'width=' + DESK + ', initial-scale=' + z + ', minimum-scale=' + z;
  }
  document.write('<meta name="viewport" content="' + (mode === 'desktop' ? deskVP() : 'width=device-width, initial-scale=1') + '">');
  var vp = document.querySelector('meta[name="viewport"]');
  if (mode === 'desktop' && vp) window.addEventListener('orientationchange', function () {
    setTimeout(function () { vp.setAttribute('content', deskVP()); }, 150);
  });
  if (small) document.documentElement.classList.add('vm-' + mode);

  // Switch by a fresh navigation (not reload): a reload keeps the old zoom level, so the desktop page would stay zoomed in.
  function set(m) {
    try { sessionStorage.setItem(KEY, m); } catch (e) {}
    var u = location.pathname + '?view=' + m + location.hash;
    location.replace(u);
  }
  if (/[?&]view=/.test(location.search) && history.replaceState) {
    try { history.replaceState(null, '', location.pathname + location.hash); } catch (e) {}
  }
  var ICON_DESK = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="2" y="4" width="20" height="13" rx="2"/><path d="M8 21h8M12 17v4"/></svg>';
  var ICON_PHONE = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="6" y="2" width="12" height="20" rx="2.5"/><path d="M11 18h2"/></svg>';

  document.addEventListener('DOMContentLoaded', function () {
    // ---- mobile menu (hamburger) ----
    var hdr = document.querySelector('.site-header .wrap'), nav = document.querySelector('.site-nav');
    if (hdr && nav) {
      nav.id = nav.id || 'site-nav';
      var t = document.createElement('button');
      t.type = 'button'; t.className = 'nav-toggle'; t.setAttribute('aria-controls', nav.id); t.setAttribute('aria-expanded', 'false');
      t.setAttribute('aria-label', '메뉴 열기');
      t.innerHTML = '<span></span><span></span><span></span>';
      hdr.appendChild(t);
      function openNav(on) {
        document.documentElement.classList.toggle('nav-open', on);
        t.setAttribute('aria-expanded', on ? 'true' : 'false');
        t.setAttribute('aria-label', on ? '메뉴 닫기' : '메뉴 열기');
      }
      t.addEventListener('click', function () { openNav(!document.documentElement.classList.contains('nav-open')); });
      document.addEventListener('keydown', function (e) { if (e.key === 'Escape') openNav(false); });
      document.addEventListener('click', function (e) { if (!e.target.closest('.site-header')) openNav(false); });
      // desktop-view switch lives inside the mobile menu
      if (small && mode === 'mobile') {
        var d = document.createElement('button');
        d.type = 'button'; d.className = 'nav-desk';
        d.innerHTML = ICON_DESK + '<span>데스크톱 화면으로 보기</span>';
        d.addEventListener('click', function () { set('desktop'); });
        nav.appendChild(d);
      }
    }
    // ---- floating switch button (phones only), same style in both modes ----
    if (!small) return;
    var desk = mode === 'desktop';
    var k = desk ? DESK / sw : 1;                    // desktop layout is zoomed out: scale the button back up
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'vm-btn'; b.style.fontSize = (12.5 * k) + 'px';
    b.innerHTML = (desk ? ICON_PHONE : ICON_DESK) + '<span>' + (desk ? '모바일 화면으로 보기' : '데스크톱 화면으로 보기') + '</span>';
    b.addEventListener('click', function () { set(desk ? 'mobile' : 'desktop'); });
    document.body.appendChild(b);
    // hidden while the page is scrolling (it would cover text), back once scrolling stops
    var idle = null;
    window.addEventListener('scroll', function () {
      b.classList.add('vm-hide');
      clearTimeout(idle);
      idle = setTimeout(function () { b.classList.remove('vm-hide'); }, 700);
    }, { passive: true });
  });
})();

/* Media protection (deterrent only): no right-click "save as", no dragging images out,
   no long-press save on phones, no download / picture-in-picture buttons on videos.
   A screenshot or the browser's developer tools cannot be blocked by any web page. */
(function () {
  var MEDIA = 'img, video, .rm-frame';
  function onMedia(t) { return t && t.closest && t.closest(MEDIA) && !t.closest('.site-header'); }
  document.addEventListener('contextmenu', function (e) { if (onMedia(e.target)) e.preventDefault(); }, true);
  document.addEventListener('dragstart', function (e) { if (onMedia(e.target)) e.preventDefault(); }, true);
  function harden(v) {
    v.setAttribute('controlslist', 'nodownload noremoteplayback');
    v.setAttribute('disablepictureinpicture', '');
    v.setAttribute('disableremoteplayback', '');
    try { v.disablePictureInPicture = true; } catch (e) {}
  }
  function sweep(n) {
    if (n.tagName === 'VIDEO') harden(n);
    if (n.querySelectorAll) Array.prototype.forEach.call(n.querySelectorAll('video'), harden);
  }
  document.addEventListener('DOMContentLoaded', function () {
    sweep(document);
    if ('MutationObserver' in window) new MutationObserver(function (ms) {
      ms.forEach(function (m) { Array.prototype.forEach.call(m.addedNodes, function (n) { if (n.nodeType === 1) sweep(n); }); });
    }).observe(document.body, { childList: true, subtree: true });
  });
})();
