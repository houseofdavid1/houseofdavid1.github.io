(function () {
  var boxes = document.querySelectorAll('details.thesis-box');
  boxes.forEach(function (d) {
    d.addEventListener('toggle', function () {
      if (d.open) boxes.forEach(function (o) { if (o !== d) o.open = false; });
    });
  });
  document.addEventListener('click', function (e) {
    boxes.forEach(function (d) { if (d.open && !d.contains(e.target)) d.open = false; });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') boxes.forEach(function (d) { d.open = false; });
  });
})();
