(function () {
  var tabs = Array.prototype.slice.call(document.querySelectorAll('.rt-tab'));
  if (!tabs.length) return;
  var LEGACY = { 'r-monitor': 'ai-monitor', 'r-surrogate': 'ai-surrogate', 'r-v2c': 'ai-v2c', 'ht': 'proc', 'weld': 'proc', 'uf': 'proc', 'ai-reflect': 'ai-lipss', 'uf-tcf': 'uf-pld', 'ai-defect': 'ai-bead', 'sim-keyhole': 'sim', 'ht-hard-mon': 'ht-monitor' };
  var panels = Array.prototype.slice.call(document.querySelectorAll('.rp-panel'));
  var fbtns = Array.prototype.slice.call(document.querySelectorAll('.rf-b'));
  var fcount = document.querySelector('.rf-n');
  var cur = null;
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
  // posters load only when a video comes near the screen (hidden tabs / folded panels cost nothing)
  function setPoster(v) { if (!v.poster && v.dataset.poster) v.poster = v.dataset.poster; }
  var pio = 'IntersectionObserver' in window ? new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { setPoster(e.target); pio.unobserve(e.target); } });
  }, { rootMargin: '800px 0px' }) : null;
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelectorAll('.rm-video video').forEach(function (v) {
    if (pio) pio.observe(v); else setPoster(v);
    if (reduce || !io) {
      v.controls = true; v.preload = 'none';
      v.addEventListener('play', function () { if (!v.src) v.src = v.dataset.src; }, { once: true });
      if (!v.src) v.src = v.dataset.src;
    } else io.observe(v);
  });

  // lightbox: click any figure / video to view it large
  var lb = document.getElementById('rm-lb');
  if (lb) {
    var body = lb.querySelector('.rm-lb-body'), cap = lb.querySelector('.rm-lb-cap');
    document.querySelectorAll('.rm-frame[data-full]').forEach(function (b) {
      b.addEventListener('click', function () {
        var fc = b.parentNode.querySelector('figcaption');
        body.innerHTML = '';
        var el;
        if (b.dataset.kind === 'v') {
          el = document.createElement('video');
          el.src = b.dataset.full; el.controls = true; el.loop = true; el.muted = true; el.autoplay = true; el.playsInline = true;
          var pv = b.querySelector('video'); if (pv && (pv.poster || pv.dataset.poster)) el.poster = pv.poster || pv.dataset.poster;
        } else {
          el = document.createElement('img'); el.src = b.dataset.full; el.alt = fc ? fc.textContent : '';
        }
        var wm = b.querySelector('.wm');
        if (wm) { var box = document.createElement('span'); box.className = 'wm-box'; box.appendChild(el); box.appendChild(wm.cloneNode(true)); body.appendChild(box); }
        else body.appendChild(el);
        cap.textContent = fc ? fc.textContent : '';
        document.querySelectorAll('.rp-panel video').forEach(function (v) { if (!v.paused) v.pause(); });
        if (typeof lb.showModal === 'function') lb.showModal(); else lb.setAttribute('open', '');
        document.body.classList.add('dialog-open');
      });
    });
    function closeLb() { if (typeof lb.close === 'function') lb.close(); else { lb.removeAttribute('open'); onClose(); } }
    function onClose() {
      body.innerHTML = ''; document.body.classList.remove('dialog-open');
      if (io) document.querySelectorAll('.rp-panel:not([hidden]) .rm-video video').forEach(function (v) { io.unobserve(v); io.observe(v); });
    }
    lb.querySelector('.rm-lb-x').addEventListener('click', closeLb);
    lb.addEventListener('click', function (e) { if (e.target === lb) closeLb(); });
    lb.addEventListener('close', onClose);
  }

  function clearFilter() {
    document.body.classList.remove('rf-on');
    fbtns.forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.f ? 'false' : 'true'); });
    document.querySelectorAll('.rb[hidden], .rp-sec[hidden]').forEach(function (el) { el.hidden = false; });
    if (fcount) fcount.textContent = '';
  }
  function reobserve() {
    if (io) document.querySelectorAll('.rp-panel:not([hidden]) .rb:not([hidden]) .rm-video video').forEach(function (v) { io.unobserve(v); io.observe(v); });
  }
  function setFilter(f, push) {
    if (!f) { clearFilter(); show(cur || tabs[0].dataset.tab, null, push); return; }
    document.body.classList.add('rf-on');
    fbtns.forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.f === f ? 'true' : 'false'); });
    tabs.forEach(function (t) { t.setAttribute('aria-selected', 'false'); });
    var n = 0, np = 0;
    panels.forEach(function (p) {
      var any = false;
      p.querySelectorAll('.rb').forEach(function (b) {
        var on = (' ' + (b.dataset.tags || '') + ' ').indexOf(' ' + f + ' ') > -1;
        b.hidden = !on; if (on) { any = true; n++; }
      });
      p.querySelectorAll('.rp-sec').forEach(function (h) {
        var el = h.nextElementSibling, vis = false;
        while (el && !el.classList.contains('rp-sec')) { if (el.classList.contains('rb') && !el.hidden) vis = true; el = el.nextElementSibling; }
        h.hidden = !vis;
      });
      p.hidden = !any; if (any) np++;
    });
    document.querySelectorAll('.rp-panel[hidden] video, .rb[hidden] video').forEach(function (v) { if (!v.paused) v.pause(); });
    reobserve();
    if (fcount) fcount.textContent = n + '개 연구 · ' + np + '개 분야';
    if (push) { try { history.replaceState(null, '', '#f-' + f); } catch (e) {} }
  }
  function toBody() {
    var top = bar.getBoundingClientRect().top + window.scrollY - (parseInt(getComputedStyle(document.documentElement).getPropertyValue('--hdr-h')) || 0);
    if (window.scrollY > top) window.scrollTo({ top: top, behavior: 'smooth' });
  }
  fbtns.forEach(function (b) { b.addEventListener('click', function () { setFilter(b.dataset.f, true); }); });
  document.querySelectorAll('.rb-tag').forEach(function (b) {
    b.addEventListener('click', function () { setFilter(b.dataset.f, true); var r = document.querySelector('.rf'); if (r) { var y = r.getBoundingClientRect().top + window.scrollY - (bar ? bar.offsetHeight : 0) - (parseInt(getComputedStyle(document.documentElement).getPropertyValue('--hdr-h')) || 0) - 12; window.scrollTo({ top: y, behavior: 'smooth' }); } });
  });
  document.querySelectorAll('[data-go]').forEach(function (a) {
    a.addEventListener('click', function (e) { e.preventDefault(); clearFilter(); show(a.dataset.go, null, true); var y = bar.getBoundingClientRect().top + window.scrollY - (parseInt(getComputedStyle(document.documentElement).getPropertyValue('--hdr-h')) || 0); window.scrollTo({ top: y, behavior: 'smooth' }); });
  });
  function show(id, focusBlock, push) {
    clearFilter();
    var tab = tabs.filter(function (t) { return t.dataset.tab === id; })[0] || tabs[0];
    cur = tab.dataset.tab;
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
      toBody();
    });
    t.addEventListener('keydown', function (e) {
      var k = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
      if (!k) return; e.preventDefault();
      var n = tabs[(i + k + tabs.length) % tabs.length]; n.focus(); n.click();
    });
  });
  // fold / unfold block details
  document.querySelectorAll('.rbx-more').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var d = document.getElementById(btn.getAttribute('aria-controls'));
      var open = btn.getAttribute('aria-expanded') !== 'true';
      d.hidden = !open;
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.querySelector('.rbx-more-l').textContent = open ? '접기' : (btn.dataset.l || '자세히 보기');
      d.querySelectorAll('video').forEach(function (v) {
        if (open) { if (io) { io.unobserve(v); io.observe(v); } } else if (!v.paused) v.pause();
      });
      if (!open) {
        var off = (bar ? bar.offsetHeight : 0) + (parseInt(getComputedStyle(document.documentElement).getPropertyValue('--hdr-h')) || 0);
        var top = btn.getBoundingClientRect().top;
        if (top < off) window.scrollTo({ top: top + window.scrollY - off - 80, behavior: 'smooth' });
      }
    });
  });
  function fromHash() {
    var h = decodeURIComponent(location.hash.slice(1));
    h = LEGACY[h] || h;
    if (h.indexOf('f-') === 0 && fbtns.some(function (b) { return b.dataset.f === h.slice(2); })) { setFilter(h.slice(2), false); return; }
    var el = h && document.getElementById(h);
    if (el && el.classList.contains('rb')) { show(el.closest('.rp-panel').id.replace('panel-', ''), h, false); return; }
    show(h, null, false);
    if (h && tabs.some(function (t) { return t.dataset.tab === h; })) {
      // a link to a research area (e.g. from the home page) opens at that tab's first screen
      var top = bar.getBoundingClientRect().top + window.scrollY - (parseInt(getComputedStyle(document.documentElement).getPropertyValue('--hdr-h')) || 0);
      window.scrollTo(0, Math.max(0, top));
    }
  }
  window.addEventListener('hashchange', fromHash);
  fromHash();
})();
