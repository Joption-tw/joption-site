(function () {
  // 手機與首頁的抽屜選單
  var btn = document.querySelector('.menu-btn');
  var scrim = document.querySelector('.scrim');
  function setNav(open) {
    document.body.classList.toggle('nav-open', open);
    scrim.hidden = !open;
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  document.querySelector('.sidebar').addEventListener('click', function (e) {
    if (e.target.closest('a')) setNav(false);
  });
  btn.addEventListener('click', function () { setNav(!document.body.classList.contains('nav-open')); });
  scrim.addEventListener('click', function () { setNav(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setNav(false); });
  // 只捲選單本身，不要動到頁面的捲動位置
  var current = document.querySelector('.sidebar [aria-current]');
  if (current) {
    var side = document.querySelector('.sidebar');
    side.scrollTop = current.getBoundingClientRect().top - side.getBoundingClientRect().top - side.clientHeight / 2;
  }

  // 點圖放大：手機上用原始大小顯示，可以左右滑動或兩指縮放
  var zoom = document.getElementById('zoom');
  var zoomImg = zoom.querySelector('img');
  document.querySelector('.prose') && document.querySelector('.prose').addEventListener('click', function (e) {
    var img = e.target;
    if (img.tagName !== 'IMG' || img.closest('a')) return;
    zoomImg.src = img.dataset.full || img.currentSrc || img.src;
    zoom.showModal();
    zoom.scrollTo(0, 0);
  });
  zoom.addEventListener('click', function () {
    zoom.close();
    zoomImg.removeAttribute('src');
  });

  // 內嵌工具的高度跟著內容走
  document.querySelectorAll('iframe.tool').forEach(function (frame) {
    function fit() {
      try {
        var doc = frame.contentDocument;
        if (!doc || !doc.documentElement) return;
        var h = Math.max(doc.documentElement.scrollHeight, doc.body ? doc.body.scrollHeight : 0);
        if (h > 100) frame.style.height = h + 'px';
      } catch (e) {}
    }
    frame.addEventListener('load', function () {
      fit();
      try {
        new ResizeObserver(fit).observe(frame.contentDocument.body);
      } catch (e) {}
    });
  });

  // 互動績效網頁：照它手機版的做法，用 1040 寬排好再縮到框的寬度，版面才不會擠
  document.querySelectorAll('.report-box').forEach(function (box) {
    var frame = box.querySelector('iframe');
    var h = Math.min(screen.width, screen.height) < 600 ? 1800 : 960; // 手機上兩頁排成一整頁，比較高
    frame.style.width = '1040px';
    frame.style.height = h + 'px';
    function fit() {
      var w = box.clientWidth;
      frame.style.transform = 'scale(' + w / 1040 + ')';
      box.style.height = h * w / 1040 + 'px';
    }
    fit();
    window.addEventListener('resize', fit);
  });

  // 全站搜尋：逐字比對，中文不需要斷詞
  var input = document.getElementById('q');
  var box = document.getElementById('results');
  var data = null;
  function load() {
    if (data) return Promise.resolve(data);
    return fetch((document.documentElement.dataset.base || '') + '/search.json').then(function (r) { return r.json(); }).then(function (d) { data = d; return d; });
  }
  function clean(s) {
    var div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML;
  }
  function run() {
    var words = input.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    if (!words.length) { box.hidden = true; return; }
    load().then(function (pages) {
      var hits = pages.map(function (p) {
        var title = p.t.toLowerCase(), text = p.x.toLowerCase(), score = 0;
        for (var i = 0; i < words.length; i++) {
          var inTitle = title.indexOf(words[i]) >= 0, inText = text.indexOf(words[i]) >= 0;
          if (!inTitle && !inText) return null;
          score += inTitle ? 10 : 1;
        }
        return { p: p, score: score, at: text.indexOf(words[0]) };
      }).filter(Boolean).sort(function (a, b) { return b.score - a.score; }).slice(0, 12);
      if (!hits.length) { box.innerHTML = '<p>找不到相關內容，換個關鍵字試試。</p>'; box.hidden = false; return; }
      box.innerHTML = hits.map(function (h) {
        var snippet = h.at >= 0 ? h.p.x.slice(Math.max(0, h.at - 20), h.at + 50) : '';
        var safe = clean(snippet);
        words.forEach(function (w) {
          var re = new RegExp(clean(w).replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
          safe = safe.replace(re, function (m) { return '<mark>' + m + '</mark>'; });
        });
        return '<a href="' + encodeURI(h.p.u) + '"><b>' + clean(h.p.t) + '</b>' + (safe ? '<small>' + safe + '</small>' : '') + '</a>';
      }).join('');
      box.hidden = false;
    });
  }
  input.addEventListener('input', run);
  input.addEventListener('focus', function () { load(); if (input.value.trim()) run(); });
  document.addEventListener('click', function (e) { if (!e.target.closest('.search')) box.hidden = true; });
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') { var first = box.querySelector('a'); if (first) location.href = first.href; }
    if (e.key === 'Escape') { box.hidden = true; input.blur(); }
  });
})();
