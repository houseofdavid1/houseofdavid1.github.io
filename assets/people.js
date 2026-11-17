(function () {
  var data = window.MEMBER_PUBS || {};
  var dialog = document.getElementById('pub-dialog');
  if (!dialog) return;
  var titleEl = dialog.querySelector('.pd-name');
  var countEl = dialog.querySelector('.pd-count');
  var listEl = dialog.querySelector('.pd-list:not(.pd-pat)');

  var pats = window.MEMBER_PATENTS || {};
  var eyebrow = dialog.querySelector('.pd-eyebrow');
  var body = dialog.querySelector('.pd-body') || listEl;
  var secs = dialog.querySelectorAll('.pd-sec');
  var patSec = dialog.querySelector('.pd-sec-pat'), patEl = dialog.querySelector('.pd-pat');

  document.querySelectorAll('.pub-btn').forEach(function (btn) {
    var entry = data[btn.dataset.member];
    var pat = pats[btn.dataset.member];
    var n = entry ? entry.items.length : 0, np = pat ? pat.items.length : 0;
    btn.querySelector('.pub-btn-count').textContent = 'Publications';
    if (!n && !np) {  // no papers yet: keep the button for a consistent card layout, but inactive
      btn.disabled = true; btn.classList.add('pub-btn-off'); btn.removeAttribute('title'); btn.setAttribute('aria-hidden', 'true'); btn.tabIndex = -1;
      return;
    }
    var name = entry ? entry.name : btn.closest('.member').querySelector('h3').textContent;
    btn.setAttribute('aria-label', 'Publications of ' + name);
    btn.addEventListener('click', function () {
      titleEl.textContent = name;
      countEl.textContent = '';
      listEl.innerHTML = n ? entry.items.map(function (li) { return '<li>' + li + '</li>'; }).join('') : '';
      var hasPat = np > 0 && patEl;
      if (patEl) {
        patEl.innerHTML = hasPat ? pat.items.map(function (p) { return '<li>' + window.renderPatent(p, pat.token) + '</li>'; }).join('') : '';
        patEl.hidden = !hasPat;
      }
      for (var i = 0; i < secs.length; i++) secs[i].hidden = !hasPat;
      if (eyebrow) eyebrow.textContent = hasPat ? 'PUBLICATIONS & PATENTS' : 'PUBLICATIONS';
      body.scrollTop = 0;
      if (typeof dialog.showModal === 'function') dialog.showModal(); else dialog.setAttribute('open', '');
      document.body.classList.add('dialog-open');
    });
  });

  function close() {
    if (typeof dialog.close === 'function') dialog.close(); else dialog.removeAttribute('open');
  }
  dialog.querySelector('.pd-close').addEventListener('click', close);
  dialog.addEventListener('click', function (e) { if (e.target === dialog) close(); });
  dialog.addEventListener('close', function () { document.body.classList.remove('dialog-open'); });
})();
