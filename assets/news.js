/* Lab news — newest items are shown automatically (top 5 by date).
   Add an entry: { date: "YYYY.MM.DD" or "YYYY.MM", tag: "논문|수상|학회|소식|졸업|입학", text: "...", link: "https://..." (optional) } */
window.LAB_NEWS = [
  { date: "2025.12.17", tag: "학위", text: "남기문, 진형국 학생이 박사학위 논문 심사(디펜스)를 성공적으로 마쳤습니다. 축하합니다!" },
  { date: "2026.02", tag: "논문", text: "우명린 학생의 논문 “A synthetic-data-trained deep learning model for predicting residual stress and melt pool characteristics in laser melting with arbitrary beam profiles”가 Materials & Design에 게재되었습니다.", link: "https://doi.org/10.1016/j.matdes.2026.115463" },
  { date: "2026", tag: "논문", text: "우명린 학생의 논문 “Industrial wafer edge segmentation for alignment: A dual resolution deep learning approach”가 Journal of Intelligent Manufacturing에 게재되었습니다.", link: "https://doi.org/10.1007/s10845-026-02912-5" },
  { date: "2025.12", tag: "논문", text: "남기문 박사의 논문 “Vision-to-code framework for automated weld seam tracking in laser welding”이 Journal of Manufacturing Processes에 게재되었습니다.", link: "https://doi.org/10.1016/j.jmapro.2025.10.111" },
  { date: "2025.12", tag: "논문", text: "연구실 논문 “Transient electrodynamic simulation of laser beam reflection on inclined surfaces using a GAN-based deep learning model”이 Engineering Applications of Artificial Intelligence에 게재되었습니다.", link: "https://doi.org/10.1016/j.engappai.2025.112561" },
  { date: "2025.10", tag: "논문", text: "연구실 논문 “AI-based real-time prediction of cross-sectional phase distribution during laser heat treatment”이 Materials & Design에 게재되었습니다.", link: "https://doi.org/10.1016/j.matdes.2025.114546" }
];
(function () {
  var box = document.getElementById('news-list');
  if (!box) return;
  function key(d) { var p = String(d).split('.'); return (+p[0]) * 10000 + (+(p[1] || 0)) * 100 + (+(p[2] || 0)); }
  var items = (window.LAB_NEWS || []).slice().sort(function (a, b) { return key(b.date) - key(a.date); }).slice(0, 5);
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  box.innerHTML = items.map(function (n) {
    var inner = '<span class="nw-date">' + esc(n.date) + '</span>' +
      '<span class="nw-tag">' + esc(n.tag || '소식') + '</span>' +
      '<span class="nw-text">' + esc(n.text) + '</span>' +
      (n.link ? '<span class="nw-go" aria-hidden="true">↗</span>' : '');
    return n.link ? '<li><a class="nw-row" href="' + esc(n.link) + '" target="_blank" rel="noopener">' + inner + '</a></li>'
                  : '<li><div class="nw-row">' + inner + '</div></li>';
  }).join('');
})();
