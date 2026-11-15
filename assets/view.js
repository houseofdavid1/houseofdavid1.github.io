/* View mode: desktop layout by default on every device; phones can switch to the mobile layout.
   Must load synchronously in <head>, right after the viewport meta. */
(function () {
  var KEY = 'ptl-view', DESK = 1280;
  var mode = 'desktop';
  try { if (localStorage.getItem(KEY) === 'mobile') mode = 'mobile'; } catch (e) {}
  var sw = Math.min(screen.width || DESK, screen.height || DESK);
  var small = sw < 900;                       // phones (and small tablets) get the switch
  var vp = document.querySelector('meta[name="viewport"]');
  if (vp) vp.setAttribute('content', mode === 'mobile' && small ? 'width=device-width, initial-scale=1' : 'width=' + DESK);
  if (!small) return;
  document.documentElement.classList.add('vm-' + (mode === 'mobile' ? 'mobile' : 'desktop'));
  // desktop layout on a phone is zoomed out by sw/DESK, so scale the button back up to a finger-friendly size
  var k = mode === 'mobile' ? 1 : DESK / sw;
  function set(m) { try { localStorage.setItem(KEY, m); } catch (e) {} location.reload(); }
  document.addEventListener('DOMContentLoaded', function () {
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'vm-btn';
    b.style.fontSize = (12.5 * k) + 'px';
    var icon = mode === 'mobile'
      ? '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="2" y="4" width="20" height="13" rx="2"/><path d="M8 21h8M12 17v4"/></svg>'
      : '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="6" y="2" width="12" height="20" rx="2.5"/><path d="M11 18h2"/></svg>';
    b.innerHTML = icon + '<span>' + (mode === 'mobile' ? '데스크톱 화면으로 보기' : '모바일 화면으로 보기') + '</span>';
    b.addEventListener('click', function () { set(mode === 'mobile' ? 'desktop' : 'mobile'); });
    document.body.appendChild(b);
    // tuck the button away while scrolling down, bring it back on scroll up / near the bottom
    var last = window.scrollY;
    window.addEventListener('scroll', function () {
      var y = window.scrollY, end = y + innerHeight >= document.documentElement.scrollHeight - 40;
      b.classList.toggle('vm-hide', y > last + 4 && y > 200 && !end);
      if (y < last - 4 || end) b.classList.remove('vm-hide');
      last = y;
    }, { passive: true });
  });
})();
