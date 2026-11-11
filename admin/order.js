// 只在本機預覽載入：拖曳調整側邊選單、隱藏或刪除頁面，存回各頁的 order、menu、hidden。
(function () {
  var side = document.querySelector('.sidebar');
  var nav = side.querySelector('nav');
  var editing = false;

  var style = document.createElement('style');
  style.textContent = [
    '.order-bar { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin: 0 0 14px; padding: 10px; border: 2px dashed var(--ink); border-radius: 10px; background: #fff; }',
    '.order-bar button { padding: 6px 12px; border: 2px solid var(--ink); border-radius: 8px; background: var(--coin); color: var(--ink); font: inherit; font-weight: 900; cursor: pointer; }',
    '.order-bar button.quiet { background: #fff; font-weight: 400; }',
    '.order-bar button:disabled { opacity: .5; cursor: wait; }',
    '.order-bar p { flex-basis: 100%; margin: 0; font-size: 13px; line-height: 1.5; color: var(--muted); }',
    '.ordering nav ul { min-height: 14px; }',
    '.ordering nav li { border-radius: 6px; }',
    '.ordering nav a, .ordering nav span, .ordering nav summary { cursor: grab; user-select: none; -webkit-user-select: none; }',
    '.ordering nav li > a, .ordering nav li > span, .ordering nav summary { background: #fff; margin-bottom: 3px; box-shadow: 0 0 0 1px var(--line); }',
    '.ordering .sortable-ghost { opacity: .45; outline: 2px solid var(--indigo); }',
    '.ordering .sortable-fallback { opacity: .95; }',
    'nav li[data-hidden] { display: none; }',
    '.ordering nav li[data-hidden] { display: list-item; }',
    '.ordering nav li[data-hidden] > a, .ordering nav li[data-hidden] > span, .ordering nav li[data-hidden] > details > summary { opacity: .5; }',
    '.ordering nav li.to-delete > a, .ordering nav li.to-delete > span, .ordering nav li.to-delete > details > summary { text-decoration: line-through; color: #c62828; opacity: .7; }',
    '.order-ask { flex-basis: 100%; display: flex; flex-wrap: wrap; gap: 8px; padding: 10px; border: 2px solid #c62828; border-radius: 8px; background: #fff5f5; }',
    '.order-ask p { color: #c62828; font-weight: 700; }',
    '.row-tools { display: none; gap: 4px; margin: 0 0 6px 8px; }',
    '.ordering .row-tools { display: flex; }',
    '.row-tools button { padding: 1px 8px; border: 1px solid var(--ink); border-radius: 6px; background: #fff; color: var(--ink); font: inherit; font-size: 12px; cursor: pointer; }',
    '.row-tools button.on { background: var(--ink); color: #fff; }',
    '.row-tools button.del.on { background: #c62828; border-color: #c62828; }'
  ].join('\n');
  document.head.appendChild(style);

  var bar = document.createElement('div');
  bar.className = 'order-bar';
  side.insertBefore(bar, nav);

  function button(text, quiet, onclick) {
    var b = document.createElement('button');
    b.type = 'button';
    b.textContent = text;
    if (quiet) b.className = 'quiet';
    b.addEventListener('click', onclick);
    return b;
  }

  function note(text) {
    var p = document.createElement('p');
    p.textContent = text;
    bar.appendChild(p);
  }

  function read(ul) {
    return Array.prototype.filter.call(ul.children, function (li) { return li.tagName === 'LI'; }).map(function (li) {
      var sub = li.querySelector(':scope > details > ul');
      var row = { children: sub ? read(sub) : [] };
      if (li.dataset.file) {
        row.file = li.dataset.file;
        if (li.dataset.hidden) row.hidden = true;
        if (li.classList.contains('to-delete')) row.delete = true;
      } else row.group = li.dataset.group;
      return row;
    });
  }

  // 編輯時點連結不跳頁、點分類不收合
  side.addEventListener('click', function (e) {
    if (editing && e.target.closest('nav')) {
      e.preventDefault();
      e.stopPropagation();
      var b = e.target.closest('.row-tools button');
      if (b) act(b);
    }
  }, true);

  function title(li) {
    var a = li.querySelector(':scope > a, :scope > span, :scope > details > summary');
    return a ? a.textContent.trim() : '';
  }

  function paint(li) {
    var tools = li.querySelector(':scope > .row-tools, :scope > details > .row-tools');
    var hide = tools.querySelector('.hide'), del = tools.querySelector('.del');
    hide.textContent = li.dataset.hidden ? '已隱藏' : '隱藏';
    hide.classList.toggle('on', !!li.dataset.hidden);
    hide.title = li.dataset.hidden ? '按一下改回顯示' : '在選單裡藏起來，網址還在';
    del.textContent = li.classList.contains('to-delete') ? '取消刪除' : '刪除';
    del.classList.toggle('on', li.classList.contains('to-delete'));
  }

  function act(b) {
    var li = b.closest('li');
    if (b.classList.contains('hide')) {
      if (li.dataset.hidden) delete li.dataset.hidden; else li.dataset.hidden = '1';
    } else {
      li.classList.toggle('to-delete');
    }
    paint(li);
  }

  // 每個頁面加上「隱藏」「刪除」兩個小按鈕
  function addTools() {
    nav.querySelectorAll('li[data-file]').forEach(function (li) {
      var tools = document.createElement('div');
      tools.className = 'row-tools';
      ['hide', 'del'].forEach(function (k) {
        var b = document.createElement('button');
        b.type = 'button';
        b.className = k;
        tools.appendChild(b);
      });
      var details = li.querySelector(':scope > details');
      if (details) details.insertBefore(tools, details.querySelector(':scope > ul'));
      else li.appendChild(tools);
      paint(li);
    });
  }

  var opened = true, wasOpen = true;

  function setOpen(state) {
    opened = state;
    nav.querySelectorAll('details').forEach(function (d) { d.open = state; });
  }

  function start() {
    if (!window.Sortable) {
      bar.textContent = '';
      bar.appendChild(button('調整選單順序', false, start));
      note('拖曳元件載入失敗，請確認有連上網路，再重新整理。');
      return;
    }
    editing = true;
    side.classList.add('ordering');
    setOpen(true);
    addTools();
    var root = nav.querySelector('ul');
    nav.querySelectorAll('ul').forEach(function (ul) {
      new Sortable(ul, {
        // 分類只能在最上層移動，才不會在拖動途中掉進別的分類
        group: { name: 'menu', put: function (to, from, item) { return !item.dataset.group || to.el === root; } },
        draggable: 'li', filter: '.row-tools', preventOnFilter: false, animation: 150, forceFallback: true, fallbackOnBody: true, swapThreshold: 0.65, emptyInsertThreshold: 12,
        onStart: function (e) {
          wasOpen = opened;
          if (e.item.dataset.group) setOpen(false);
        },
        onEnd: function (e) {
          if (e.item.dataset.group) setOpen(wasOpen);
        }
      });
    });
    bar.textContent = '';
    // 有要刪的頁時，在選單上方先列出來確認（內建瀏覽器會擋掉跳出的確認視窗，所以不用 confirm）
    var ask = null;
    function closeAsk() {
      if (ask) ask.remove();
      ask = null;
    }
    var save = button('儲存', false, function () {
      var doomed = Array.prototype.map.call(nav.querySelectorAll('li.to-delete'), title);
      if (doomed.length) {
        if (ask) return;
        ask = document.createElement('div');
        ask.className = 'order-ask';
        var p = document.createElement('p');
        p.textContent = '確定要刪除這 ' + doomed.length + ' 頁？' + doomed.join('、') + '。還沒發布之前，可以找我救回來。';
        ask.appendChild(p);
        ask.appendChild(button('確定刪除並儲存', false, function () { send(); }));
        ask.appendChild(button('先不要', true, closeAsk));
        bar.appendChild(ask);
        ask.scrollIntoView({ block: 'nearest' });
        return;
      }
      send();
    });
    function send() {
      closeAsk();
      save.disabled = true;
      save.textContent = '儲存中…';
      fetch('/__order', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(read(nav.querySelector('ul'))) })
        .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, data: d }; }); })
        .then(function (res) {
          if (!res.ok) throw new Error(res.data.error);
          try { sessionStorage.setItem('order-saved', JSON.stringify(res.data)); } catch (e) {}
          // 刪掉的是現在這一頁，就回首頁
          if (nav.querySelector('li.to-delete [aria-current]')) location.href = '/'; else location.reload();
        })
        .catch(function (err) {
          save.disabled = false;
          save.textContent = '儲存';
          note('沒有存到：' + err.message);
        });
    }
    bar.appendChild(save);
    bar.appendChild(button('取消', true, function () { location.reload(); }));
    var toggle = button('全部收合', true, function () {
      setOpen(!opened);
      toggle.textContent = opened ? '全部收合' : '全部展開';
    });
    bar.appendChild(toggle);
    note('按住項目上下拖曳，也可以拖到別的分類裡。分類拖空了，存檔後就會消失。');
    note('「隱藏」：選單上看不到，網址還在，淡淡的就是隱藏中。「刪除」：存檔時把那一頁刪掉。都要按「儲存」才算數。');
  }

  bar.appendChild(button('調整選單順序', false, start));
  var saved = null;
  try {
    saved = sessionStorage.getItem('order-saved');
    sessionStorage.removeItem('order-saved');
    saved = saved && JSON.parse(saved);
  } catch (e) {}
  if (saved) {
    var msg = '存好了。';
    if (saved.removed && saved.removed.length) msg += '刪掉：' + saved.removed.join('、') + '。';
    note(msg + '線上網站還沒變，雙擊「發布網站.bat」才會更新。');
    (saved.problems || []).forEach(function (p) { note('⚠ ' + p.replace(/^\//, '')); });
  }
})();
