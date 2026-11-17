(function () {
  var data = window.MEMBER_PUBS || {};
  var dialog = document.getElementById('pub-dialog');
  if (!dialog) return;
  var titleEl = dialog.querySelector('.pd-name');
  var countEl = dialog.querySelector('.pd-count');
  var listEl = dialog.querySelector('.pd-list');

  document.querySelectorAll('.pub-btn').forEach(function (btn) {
    var entry = data[btn.dataset.member];
    var n = entry ? entry.items.length : 0;
    btn.querySelector('.pub-btn-count').textContent = 'Publications';
    if (!n) {  // no papers yet: keep the button for a consistent card layout, but inactive
      btn.disabled = true; btn.classList.add('pub-btn-off'); btn.removeAttribute('title'); btn.setAttribute('aria-hidden', 'true'); btn.tabIndex = -1;
      return;
    }
    btn.setAttribute('aria-label', 'Publications of ' + entry.name);
    btn.addEventListener('click', function () {
      titleEl.textContent = entry.name;
      countEl.textContent = '';
      listEl.innerHTML = entry.items.map(function (li) { return '<li>' + li + '</li>'; }).join('');
      listEl.scrollTop = 0;
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
