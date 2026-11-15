(function () {
  var tabs = Array.prototype.slice.call(document.querySelectorAll('.rt-tab'));
  if (!tabs.length) return;
  var LEGACY = { 'r-monitor': 'ai-monitor', 'r-surrogate': 'ai-surrogate', 'r-v2c': 'ai-v2c' };
  var bar = document.querySelector('.rt-bar');
  function hdr() {
    var h = document.querySelector('.site-header');
    document.documentElement.style.setProperty('--hdr-h', (h ? h.offsetHeight : 0) + 'px');
  }
  hdr(); window.addEventListener('resize', hdr);

  // lazy, visibility-driven video playback
  var io = 'IntersectionObserver' in window ? new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      var v = e.target;
      if (e.isIntersecting && !v.closest('[hidden]')) {
        if (!v.src) { v.src = v.dataset.src; }
        var p = v.play(); if (p && p.catch) p.catch(function () {});
        v.parentNode.classList.add('is-playing');
      } else if (!v.paused) { v.pause(); }
    });
  }, { threshold: 0.35 }) : null;
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelectorAll('.rm-video video').forEach(function (v) {
    if (reduce || !io) {
      v.controls = true; v.preload = 'none';
      v.addEventListener('play', function () { if (!v.src) v.src = v.dataset.src; }, { once: true });
      if (!v.src) v.src = v.dataset.src;
    } else io.observe(v);
  });

  function show(id, focusBlock, push) {
    var tab = tabs.filter(function (t) { return t.dataset.tab === id; })[0] || tabs[0];
    tabs.forEach(function (t) {
      var on = t === tab;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      t.tabIndex = on ? 0 : -1;
      document.getElementById('panel-' + t.dataset.tab).hidden = !on;
    });
    document.querySelectorAll('.rp-panel[hidden] video').forEach(function (v) { if (!v.paused) v.pause(); });
    if (io) document.querySelectorAll('#panel-' + tab.dataset.tab + ' video').forEach(function (v) { io.unobserve(v); io.observe(v); });
    if (push) { try { history.replaceState(null, '', '#' + tab.dataset.tab); } catch (e) {} }
    var target = focusBlock && document.getElementById(focusBlock);
    if (target) {
      setTimeout(function () {
        var y = target.getBoundingClientRect().top + window.scrollY - (bar ? bar.offsetHeight : 0) - (parseInt(getComputedStyle(document.documentElement).getPropertyValue('--hdr-h')) || 0) - 16;
        window.scrollTo({ top: y, behavior: 'smooth' });
      }, 60);
    }
  }
  tabs.forEach(function (t, i) {
    t.addEventListener('click', function () {
      show(t.dataset.tab, null, true);
      var top = bar.getBoundingClientRect().top + window.scrollY - (parseInt(getComputedStyle(document.documentElement).getPropertyValue('--hdr-h')) || 0);
      if (window.scrollY > top) window.scrollTo({ top: top, behavior: 'smooth' });
    });
    t.addEventListener('keydown', function (e) {
      var k = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
      if (!k) return; e.preventDefault();
      var n = tabs[(i + k + tabs.length) % tabs.length]; n.focus(); n.click();
    });
  });
  function fromHash() {
    var h = decodeURIComponent(location.hash.slice(1));
    h = LEGACY[h] || h;
    var el = h && document.getElementById(h);
    if (el && el.classList.contains('rb')) { show(el.closest('.rp-panel').id.replace('panel-', ''), h, false); return; }
    show(h, null, false);
  }
  window.addEventListener('hashchange', fromHash);
  fromHash();
})();
