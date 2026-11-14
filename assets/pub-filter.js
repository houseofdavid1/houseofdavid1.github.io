(function () {
  var box = document.querySelector('.topic-filter');
  var list = document.getElementById('pub-main');
  if (!box || !list) return;
  var chips = Array.prototype.slice.call(box.querySelectorAll('.topic-chip'));
  var items = Array.prototype.slice.call(list.children);
  var clear = box.querySelector('.tf-clear');
  var empty = box.querySelector('.tf-empty');
  var sel = {};

  function apply(push) {
    var keys = Object.keys(sel);
    var shown = 0;
    items.forEach(function (li) {
      var tags = (li.getAttribute('data-tags') || '').split(' ');
      var ok = !keys.length || keys.every(function (k) { return tags.indexOf(k) !== -1; });
      li.hidden = !ok;
      if (ok) {
        shown++;
        if (keys.length) { li.classList.remove('tf-in'); void li.offsetWidth; li.classList.add('tf-in'); }
      }
    });
    chips.forEach(function (c) {
      var on = !!sel[c.dataset.topic];
      c.classList.toggle('is-on', on);
      c.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    clear.hidden = !keys.length;
    empty.hidden = shown > 0;
    box.classList.toggle('has-sel', keys.length > 0);
    if (push) {
      var h = keys.length ? '#topics=' + keys.join(',') : ' ';
      try { history.replaceState(null, '', h === ' ' ? location.pathname + location.search : h); } catch (e) {}
    }
  }

  chips.forEach(function (c) {
    c.addEventListener('click', function () {
      var k = c.dataset.topic;
      if (sel[k]) delete sel[k]; else sel[k] = true;
      apply(true);
    });
  });
  clear.addEventListener('click', function () { sel = {}; apply(true); });

  var m = /topics=([\w,]+)/.exec(location.hash);
  if (m) m[1].split(',').forEach(function (k) {
    if (chips.some(function (c) { return c.dataset.topic === k; })) sel[k] = true;
  });
  apply(false);
})();
