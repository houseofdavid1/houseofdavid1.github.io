/* Lab news — the home page shows every item from the past 12 months (newest first).
   Markup in text: {{Name}} = lab member, [[Journal]] = journal name.
   Add an entry: { date: "YYYY.MM.DD" or "YYYY.MM", tag: "논문|수상|학회|소식|졸업|입학", text: "...", link: "https://..." (optional) } */
window.LAB_NEWS = [
  { date: "2026.03", tag: "진로", text: "{{손명균}} 박사가 삼성SDI에 입사했습니다. 축하합니다!" },
  { date: "2026.08", tag: "입학", text: "{{장준희}} 학생이 석박사 통합과정으로 입학했습니다. 환영합니다!" },
  { date: "2025.12.17", tag: "학위", text: "{{남기문}}, {{진형국}} 학생이 박사학위 논문 심사(디펜스)를 성공적으로 마쳤습니다. 축하합니다!" },
  { date: "2026.02", tag: "논문", text: "{{우명린}} 학생의 논문 “A synthetic-data-trained deep learning model for predicting residual stress and melt pool characteristics in laser melting with arbitrary beam profiles”가 [[Materials & Design]]에 게재되었습니다.", link: "https://doi.org/10.1016/j.matdes.2026.115463" },
  { date: "2026", tag: "논문", text: "{{우명린}} 학생의 논문 “Industrial wafer edge segmentation for alignment: A dual resolution deep learning approach”가 [[Journal of Intelligent Manufacturing]]에 게재되었습니다.", link: "https://doi.org/10.1007/s10845-026-02912-5" },
  { date: "2025.12", tag: "논문", text: "{{남기문}} 박사의 논문 “Vision-to-code framework for automated weld seam tracking in laser welding”이 [[Journal of Manufacturing Processes]]에 게재되었습니다.", link: "https://doi.org/10.1016/j.jmapro.2025.10.111" },
  { date: "2025.12", tag: "논문", text: "{{손명균}} 박사의 논문 “Transient electrodynamic simulation of laser beam reflection on inclined surfaces using a GAN-based deep learning model”이 [[Engineering Applications of Artificial Intelligence]]에 게재되었습니다.", link: "https://doi.org/10.1016/j.engappai.2025.112561" },
  { date: "2025.10", tag: "논문", text: "{{손명균}} 박사의 논문 “AI-based real-time prediction of cross-sectional phase distribution during laser heat treatment”이 [[Materials & Design]]에 게재되었습니다.", link: "https://doi.org/10.1016/j.matdes.2025.114546" }
];
(function () {
  function key(d) { var p = String(d).split('.'); return (+p[0]) * 10000 + (+(p[1] || 0)) * 100 + (+(p[2] || 0)); }
  function fmt(s) { return esc(s).replace(/\{\{(.+?)\}\}/g, '<b class="nw-name">$1</b>').replace(/\[\[(.+?)\]\]/g, '<i class="nw-jr">$1</i>'); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  var all = (window.LAB_NEWS || []).slice().sort(function (a, b) { return key(b.date) - key(a.date); });
  function rows(items) {
    return items.map(function (n) {
      var inner = '<span class="nw-date">' + esc(n.date) + '</span>' +
        '<span class="nw-tag">' + esc(n.tag || '소식') + '</span>' +
        '<span class="nw-text">' + fmt(n.text) + '</span>' +
        (n.link ? '<span class="nw-go" aria-hidden="true">↗</span>' : '<span></span>');
      return n.link ? '<li><a class="nw-row" href="' + esc(n.link) + '" target="_blank" rel="noopener">' + inner + '</a></li>'
                    : '<li><div class="nw-row">' + inner + '</div></li>';
    }).join('');
  }
  var box = document.getElementById('news-list');
  // home list: everything from the past 12 months (falls back to the latest 3 if none)
  var now = new Date();
  var cutoff = (now.getFullYear() - 1) * 10000 + (now.getMonth() + 1) * 100 + now.getDate();
  var recent = all.filter(function (n) { return key(n.date) >= cutoff || String(n.date).split('.').length === 1 && +n.date >= now.getFullYear() - 1 + 1; });
  if (!recent.length) recent = all.slice(0, 3);
  if (box) box.innerHTML = rows(recent);
  var btn = document.getElementById('news-all'), dlg = document.getElementById('news-dialog');
  if (!btn || !dlg) return;
  var full = document.getElementById('news-full'), cnt = document.getElementById('nd-count');
  btn.addEventListener('click', function () {
    full.innerHTML = rows(all); cnt.textContent = '총 ' + all.length + '건'; full.scrollTop = 0;
    if (typeof dlg.showModal === 'function') dlg.showModal(); else dlg.setAttribute('open', '');
    document.body.classList.add('dialog-open');
  });
  function close() { if (typeof dlg.close === 'function') dlg.close(); else dlg.removeAttribute('open'); }
  dlg.querySelector('.pd-close').addEventListener('click', close);
  dlg.addEventListener('click', function (e) { if (e.target === dlg) close(); });
  dlg.addEventListener('close', function () { document.body.classList.remove('dialog-open'); });
})();
