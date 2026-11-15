/* View mode + mobile menu.
   Default: responsive (mobile layout on phones). Phones may opt into the desktop layout; the choice is remembered.
   Must load synchronously in <head>, right after the viewport meta. */
(function () {
  var KEY = 'ptl-view', DESK = 1280;
  var sw = Math.min(screen.width || DESK, screen.height || DESK);
  var small = sw < 900;
  var mode = 'mobile';
  try { if (localStorage.getItem(KEY) === 'desktop') mode = 'desktop'; } catch (e) {}
  if (!small) mode = 'mobile';                       // large screens: plain responsive layout
  var vp = document.querySelector('meta[name="viewport"]');
  if (vp) vp.setAttribute('content', mode === 'desktop' ? 'width=' + DESK : 'width=device-width, initial-scale=1');
  if (small) document.documentElement.classList.add('vm-' + mode);

  function set(m) { try { localStorage.setItem(KEY, m); } catch (e) {} location.reload(); }
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
    // ---- footer link (mobile) / floating button (desktop layout on a phone) ----
    if (!small) return;
    var foot = document.querySelector('.site-footer .copy');
    if (mode === 'mobile' && foot) {
      var a = document.createElement('button');
      a.type = 'button'; a.className = 'vm-link'; a.textContent = '데스크톱 화면으로 보기';
      a.addEventListener('click', function () { set('desktop'); });
      foot.appendChild(a);
    }
    if (mode === 'desktop') {
      var k = DESK / sw;                             // desktop layout is zoomed out: scale the button back up
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'vm-btn'; b.style.fontSize = (12.5 * k) + 'px';
      b.innerHTML = ICON_PHONE + '<span>모바일 화면으로 보기</span>';
      b.addEventListener('click', function () { set('mobile'); });
      document.body.appendChild(b);
      var last = window.scrollY;
      window.addEventListener('scroll', function () {
        var y = window.scrollY, end = y + innerHeight >= document.documentElement.scrollHeight - 40;
        if (y > last + 4 && y > 200 && !end) b.classList.add('vm-hide');
        else if (y < last - 4 || end) b.classList.remove('vm-hide');
        last = y;
      }, { passive: true });
    }
  });
})();
