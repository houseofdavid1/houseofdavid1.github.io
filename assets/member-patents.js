/* Registered patents shown in each member's publication pop-up (not on the Publications page).
   Add an entry: { en: "English title", ko: "국문 명칭(특허증 그대로)", inventors: ["H. Ki", "..."], url: "https://patents.google.com/patent/KR10xxxxxxxB1/ko" (optional), no: "10-xxxxxxx", reg: "YYYY.MM.DD" }
   url: add once the patent page opens on Google Patents (new grants can take a few months to appear).
   The member's own name is highlighted automatically (token below). Newest first. */
window.MEMBER_PATENTS = {
  "kimoon-nam": { token: "K. Nam", items: [
    { en: "Welding process monitoring apparatus and method",
      ko: "용접공정 모니터링 장치 및 방법",
      inventors: ["H. Ki", "K. Nam"], url: "https://patents.google.com/patent/KR102986065B1/ko", no: "10-2986065", reg: "2026.06.30" },
    { en: "Laser welding monitoring apparatus, method and system using prediction of laser absorptance in a keyhole",
      ko: "키홀 내 레이저 흡수율 예측을 통한 레이저 용접 모니터링 장치, 방법 및 시스템",
      inventors: ["H. Ki", "K. Nam"], url: "https://patents.google.com/patent/KR102844769B1/ko", no: "10-2844769", reg: "2025.08.06" }
  ] },
  "myungrin-woo": { token: "M. Woo", items: [
    { en: "Method and apparatus for aligning wafers in a temporary bonding process",
      ko: "임시 본딩 공정에서 웨이퍼를 정렬시키기 위한 방법 및 장치",
      inventors: ["H. Ki", "M. Woo", "G. S. Oh", "B. S. Lee"], url: "https://patents.google.com/patent/KR102943452B1/ko", no: "10-2943452", reg: "2026.03.18" }
  ] },
  "yeonsu-kim": { token: "Y. Kim", items: [
    { en: "Laser processing apparatus and method",
      ko: "레이저 가공 장치 및 방법",
      inventors: ["H. Ki", "Y. Kim"], no: "10-3031265", reg: "2026.10.06" }
  ] }
};
window.renderPatent = function (p, token) {
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var inv = p.inventors.map(function (n) {
    if (n === token) return '<mark class="me">' + esc(n) + '</mark>';
    if (n === 'H. Ki') return '<strong>H. Ki</strong>';
    return esc(n);
  }).join(', ');
  return '<span class="pub-title">' + esc(p.en) + '</span>' +
    '<span class="pub-ko">' + esc(p.ko) + '</span>' +
    '<span class="pub-authors">' + inv + '</span>' +
    '<span class="pub-venue"><em>Korean Patent</em> No. ' + esc(p.no) + ' (registered ' + esc(p.reg) + ')' +
    (p.url ? ' <a href="' + esc(p.url) + '" target="_blank" rel="noopener">Google Patents</a>' : '') + '</span>';
};
