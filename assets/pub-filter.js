(function () {
  var box = document.querySelector('.topic-filter');
  var list = document.getElementById('pub-main');
  if (!box || !list) return;
  var chips = Array.prototype.slice.call(box.querySelectorAll('.topic-chip:not(.tc-all)'));
  var items = Array.prototype.slice.call(list.children);
  var clear = box.querySelector('.tc-all');
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
    clear.classList.toggle('is-on', !keys.length); clear.setAttribute('aria-pressed', keys.length ? 'false' : 'true');
    empty.hidden = shown > 0;
    box.classList.toggle('has-sel', keys.length > 0);
    if (push) {
      var h = keys.length ? '#topics=' + keys.join(',') : ' ';
      try { history.replaceState(null, '', h === ' ' ? location.pathname + location.search : h); } catch (e) {}
    }
  }

  var order = [];  // selection order, oldest first
  function count(keys) {
    return items.filter(function (li) {
      var tags = (li.getAttribute('data-tags') || '').split(' ');
      return keys.every(function (k) { return tags.indexOf(k) !== -1; });
    }).length;
  }
  chips.forEach(function (c) {
    c.addEventListener('click', function () {
      var k = c.dataset.topic;
      if (sel[k]) {
        delete sel[k]; order = order.filter(function (x) { return x !== k; });
      } else {
        // a group chip ("AI · all") and the topics inside the same group are mutually exclusive
        var grp = c.closest('.tf-group');
        if (grp) {
          // one selection per group (radio); different groups combine with AND
          Array.prototype.forEach.call(grp.querySelectorAll('.topic-chip'), function (o) {
            if (o !== c) {
              var ok = o.dataset.topic; order = order.filter(function (x) { return x !== ok; });
            }
          });
        }
        order.push(k);
        // if the combination has no papers, release the oldest selections until something matches
        while (order.length > 1 && !count(order)) order.shift();
        sel = {}; order.forEach(function (x) { sel[x] = true; });
      }
      apply(true);
    });
  });
  clear.addEventListener('click', function () { sel = {}; order = []; apply(true); });

  var m = /topics=([\w,]+)/.exec(location.hash);
  if (m) m[1].split(',').forEach(function (k) {
    if (chips.some(function (c) { return c.dataset.topic === k; })) { sel[k] = true; order.push(k); }
  });
  apply(false);
})();
