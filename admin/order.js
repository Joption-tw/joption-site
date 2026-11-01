// 只在本機預覽載入：拖曳調整側邊選單，存回各頁的 order 和 menu。
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
    '.ordering .sortable-fallback { opacity: .95; }'
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
      if (li.dataset.file) row.file = li.dataset.file; else row.group = li.dataset.group;
      return row;
    });
  }

  // 編輯時點連結不跳頁、點分類不收合
  side.addEventListener('click', function (e) {
    if (editing && e.target.closest('nav')) {
      e.preventDefault();
      e.stopPropagation();
    }
  }, true);

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
    var root = nav.querySelector('ul');
    nav.querySelectorAll('ul').forEach(function (ul) {
      new Sortable(ul, {
        // 分類只能在最上層移動，才不會在拖動途中掉進別的分類
        group: { name: 'menu', put: function (to, from, item) { return !item.dataset.group || to.el === root; } },
        draggable: 'li', animation: 150, forceFallback: true, fallbackOnBody: true, swapThreshold: 0.65, emptyInsertThreshold: 12,
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
    var save = button('儲存', false, function () {
      save.disabled = true;
      save.textContent = '儲存中…';
      fetch('/__order', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(read(nav.querySelector('ul'))) })
        .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, data: d }; }); })
        .then(function (res) {
          if (!res.ok) throw new Error(res.data.error);
          try { sessionStorage.setItem('order-saved', '1'); } catch (e) {}
          location.reload();
        })
        .catch(function (err) {
          save.disabled = false;
          save.textContent = '儲存';
          note('沒有存到：' + err.message);
        });
    });
    bar.appendChild(save);
    bar.appendChild(button('取消', true, function () { location.reload(); }));
    var toggle = button('全部收合', true, function () {
      setOpen(!opened);
      toggle.textContent = opened ? '全部收合' : '全部展開';
    });
    bar.appendChild(toggle);
    note('按住項目上下拖曳，也可以拖到別的分類裡。分類拖空了，存檔後就會消失。');
  }

  bar.appendChild(button('調整選單順序', false, start));
  var saved = false;
  try {
    saved = sessionStorage.getItem('order-saved') === '1';
    sessionStorage.removeItem('order-saved');
  } catch (e) {}
  if (saved) note('順序存好了。線上網站還沒變，雙擊「發布網站.bat」才會更新。');
})();
