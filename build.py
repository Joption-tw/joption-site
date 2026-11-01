"""把 content/ 裡的 Markdown 組成整個網站，輸出到 dist/。

    python build.py            產生網站
    python build.py --serve    產生網站並開本機預覽，存檔後自動更新
"""
import concurrent.futures, hashlib, html, http.server, json, os, re, shutil, sys, threading, time, tomllib, urllib.parse, webbrowser

import markdown
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(ROOT, "content")
THEME = os.path.join(ROOT, "theme")
DIST = os.path.join(ROOT, "dist")
CACHE = os.path.join(ROOT, ".imgcache")
IMAGE_WIDTHS = (800, 1280)
PORT = 8770


def read_page(path):
    raw = open(path, encoding="utf-8").read()
    meta, body = {}, raw
    m = re.match(r"---\n(.*?)\n---\n?(.*)", raw, re.S)
    if m:
        body = m.group(2)
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta, body


def collect_pages():
    pages = []
    for folder, dirs, files in os.walk(CONTENT):
        rel = os.path.relpath(folder, CONTENT).replace("\\", "/")
        if rel.split("/")[0] in ("images", "tools"):
            dirs[:] = []
            continue
        for name in files:
            if not name.endswith(".md"):
                continue
            meta, body = read_page(os.path.join(folder, name))
            parts = [] if rel == "." else rel.split("/")
            if name != "index.md":
                parts = parts + [name[:-3]]
            url = "/" + "".join(p + "/" for p in parts)
            pages.append({
                "url": url,
                "parts": parts,
                "title": meta.get("title", parts[-1] if parts else "首頁"),
                "order": int(meta.get("order", 100000)),
                "hidden": meta.get("hidden") == "true",
                "summary": meta.get("summary", ""),
                "layout": meta.get("layout", "page"),
                "redirect": meta.get("redirect"),
                "body": body,
            })
    return pages


def build_tree(pages):
    """資料夾就是選單：不必另外維護目錄。"""
    by_url = {p["url"]: p for p in pages}
    nodes = {}

    def node(parts):
        key = tuple(parts)
        if key not in nodes:
            url = "/" + "".join(p + "/" for p in parts)
            page = by_url.get(url)
            nodes[key] = {"url": url, "page": page, "title": page["title"] if page else parts[-1],
                          "order": page["order"] if page else 100000, "children": [], "hidden": bool(page and page["hidden"])}
            if not page:  # 只有資料夾沒有頁面（例如「選單」）時，順序跟著第一個子頁
                nodes[key]["order"] = min((p["order"] for p in pages if p["parts"][:len(parts)] == parts), default=100000)
            if len(parts) > 1:
                node(parts[:-1])["children"].append(nodes[key])
            else:
                top.append(nodes[key])
        return nodes[key]

    top = []
    for p in pages:
        if p["parts"]:
            node(p["parts"])

    def sort(items):
        items.sort(key=lambda n: (n["order"], n["title"]))
        for n in items:
            sort(n["children"])

    sort(top)
    return top


def esc(t):
    return html.escape(t, quote=True)


def page_link(n):
    p = n["page"]
    if p and p["redirect"]:
        return p["redirect"]
    return n["url"] if p else None


def render_nav(items, current, depth=0):
    out = ['<ul>']
    for n in items:
        if n["hidden"]:
            continue
        kids = [k for k in n["children"] if not k["hidden"]]
        link = page_link(n)
        active = current == n["url"]
        # 只是分類、沒有自己頁面的群組（例如「選單」）預設展開
        inside = current.startswith(n["url"]) or not link
        label = (f'<a href="{esc(link)}"{" aria-current=page" if active else ""}>{esc(n["title"])}</a>'
                 if link else f'<span>{esc(n["title"])}</span>')
        if kids:
            out.append(f'<li><details{" open" if inside else ""}><summary>{label}</summary>'
                       f'{render_nav(kids, current, depth + 1)}</details></li>')
        else:
            out.append(f'<li>{label}</li>')
    out.append('</ul>')
    return "".join(out)


def macro(m):
    kind, value = m.group(1), m.group(2).strip()
    if kind == "youtube":
        return (f'<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/{esc(value)}" '
                'title="YouTube 影片" loading="lazy" allowfullscreen></iframe></div>')
    if kind == "tool":
        return (f'<div class="tool-box"><iframe class="tool" src="/tools/{esc(value)}.html" '
                f'title="{esc(value)}" loading="lazy"></iframe></div>')
    # Google 試算表要有這組 sandbox 才顯示得出來，和 Google Sites 內嵌時用的相同
    return (f'<iframe class="embed" src="{esc(value)}" title="內嵌內容" sandbox="allow-scripts allow-popups '
            'allow-forms allow-same-origin allow-popups-to-escape-sandbox allow-downloads allow-modals '
            'allow-storage-access-by-user-activation"></iframe>')


def make_variant(job):
    """壓成 WebP，做好的存在 .imgcache，下次產生網站就不用重做。"""
    path, width, key = job
    cached = os.path.join(CACHE, f"{key}-{width}.webp")
    if not os.path.exists(cached):
        with Image.open(path) as im:
            im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
            if im.width > width:
                im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
            part = f"{cached}.{os.getpid()}.tmp"
            im.save(part, "WEBP", quality=80, method=4)
        os.replace(part, cached)
    return cached


def build_variants(tmp):
    """每張圖做手機用和電腦用兩種大小，回傳 {原圖網址: [(壓縮圖網址, 寬度), ...]}。"""
    os.makedirs(CACHE, exist_ok=True)
    jobs, out = [], {}
    root = os.path.join(CONTENT, "images")
    for folder, _, files in os.walk(root):
        for name in files:
            stem, ext = os.path.splitext(name)
            if ext.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
                continue
            path = os.path.join(folder, name)
            rel = os.path.relpath(path, CONTENT).replace("\\", "/")
            stat = os.stat(path)
            key = hashlib.sha1(f"{rel}|{stat.st_size}|{stat.st_mtime_ns}".encode()).hexdigest()[:16]
            with Image.open(path) as im:
                full = im.width
            widths = sorted({min(w, full) for w in IMAGE_WIDTHS})
            url_dir = "/" + rel.rsplit("/", 1)[0]
            out["/" + rel] = [(f"{url_dir}/{stem}-{w}.webp", w) for w in widths]
            jobs += [((path, w, key), os.path.join(tmp, os.path.dirname(rel), f"{stem}-{w}.webp")) for w in widths]
    with concurrent.futures.ThreadPoolExecutor(os.cpu_count() or 4) as pool:
        for cached, (_, dest) in zip(pool.map(make_variant, [j[0] for j in jobs]), jobs):
            shutil.copyfile(cached, dest)
    return out


def render_md(body, used, variants):
    body = re.sub(r"^\[\[(youtube|tool|embed):(.+?)\]\]\s*$", macro, body, flags=re.M)
    body = re.sub(r"(?<![=\\])==(?=\S)(.+?)(?<=\S)==(?!=)", r'<span class="hl">\1</span>', body)
    md = markdown.Markdown(extensions=["extra", "sane_lists", "nl2br"])
    out = md.convert(body)

    def img(m):
        size, tag, src = "", m.group(0), m.group(1)
        if src.startswith("/"):
            used.add(src)
            path = os.path.join(CONTENT, src.lstrip("/"))
            if os.path.exists(path):  # 先留好圖片的位置，載入時版面才不會跳動
                with Image.open(path) as im:
                    size = f'width="{im.width}" height="{im.height}" '
            if src in variants:
                # sizes 故意寫小一點：高解析手機才不會每張都抓電腦版大圖
                srcset = ", ".join(f'{u.replace(" ", "%20")} {w}w' for u, w in variants[src])
                size += (f'srcset="{srcset}" sizes="(max-width: 640px) 60vw, 860px" data-full="{src}" ')
                tag = tag.replace(f'src="{src}"', f'src="{variants[src][-1][0]}"')
        return tag.replace("<img ", f'<img {size}loading="lazy" decoding="async" ')

    return re.sub(r'<img [^>]*?src="([^"]+)"[^>]*>', img, out)


def crumbs(page, by_url):
    bits = ['<a href="/">首頁</a>']
    parts = page["parts"]
    for i in range(len(parts)):
        url = "/" + "".join(p + "/" for p in parts[: i + 1])
        target = by_url.get(url)
        if parts[i] == "首頁" and i == 0:
            continue
        if url == page["url"]:
            break
        bits.append(f'<a href="{esc(url)}">{esc(target["title"])}</a>' if target else f'<span>{esc(parts[i])}</span>')
    return '<nav class="crumbs" aria-label="目前位置">' + " / ".join(bits) + "</nav>"


ICONS = {
    "coin": '<circle cx="12" cy="12" r="10"/><path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3"/><path d="M12 17h.01"/>',
    "seesaw": '<path d="M2 9l20-4"/><path d="M12 7l-4 13h8z"/><circle cx="4.5" cy="5" r="2"/><circle cx="19.5" cy="2.5" r="1.5"/>',
    "book": '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
    "monitor": '<rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8"/><path d="M12 17v4"/>',
    "sliders": '<path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6"/>',
    "payoff": '<path d="M2 20L8 7h8l6 13"/><path d="M2 14h20" stroke-dasharray="2 3"/>',
    "person": '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    "download": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M7 10l5 5 5-5"/><path d="M12 15V3"/>',
    "chat": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    "clock": '<circle cx="12" cy="13" r="8"/><path d="M12 9v4l2 2"/><path d="M5 3L2 6M19 3l3 3"/>',
}

# 首頁底邊的雙賣損益圖：中間平台賺時間價值，兩邊是 Put、Call 的風險
PAYOFF = ('<svg class="payoff" viewBox="0 0 1200 92" preserveAspectRatio="none" aria-hidden="true">'
          '<path class="payoff-fill" d="M0 92L0 88L400 14H800L1200 88V92Z"/>'
          '<path class="payoff-line" d="M0 88L400 14H800L1200 88"/></svg>'
          '<span class="payoff-tag put" aria-hidden="true">Put</span>'
          '<span class="payoff-tag theta" aria-hidden="true">時間價值</span>'
          '<span class="payoff-tag call" aria-hidden="true">Call</span>')


def card(title, url, summary="", icon=None):
    desc = f"<p>{esc(summary)}</p>" if summary else ""
    badge = f'<span class="card-icon"><svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[icon]}</svg></span>' if icon in ICONS else ""
    return f'<a class="card" href="{esc(url)}">{badge}<div><h3>{esc(title)}</h3>{desc}</div></a>'


def flatten(items):
    for n in items:
        if n["hidden"]:
            continue
        if n["page"] and not n["page"]["redirect"]:
            yield n
        yield from flatten(n["children"])


def with_base(text, base):
    """網站放在子路徑（例如 /joption-site）時，站內連結都要加上這段。"""
    text = text.replace("{{base}}", base)
    if base:
        text = re.sub(r'\b(href|src|data-full)="/(?!/)', rf'\1="{base}/', text)
        text = re.sub(r'\bsrcset="([^"]*)"', lambda m: 'srcset="' + re.sub(r"(^|, )/", rf"\1{base}/", m.group(1)) + '"', text)
    return text


def sync_dist(tmp):
    """逐檔更新 dist/：Windows 上預覽伺服器開著時，整個資料夾不能直接換掉。"""
    fresh = set()
    for folder, _, files in os.walk(tmp):
        rel = os.path.relpath(folder, tmp)
        os.makedirs(os.path.join(DIST, rel), exist_ok=True)
        fresh.add(os.path.normpath(os.path.join(DIST, rel)))
        for name in files:
            dest = os.path.join(DIST, rel, name)
            fresh.add(os.path.normpath(dest))
            shutil.copyfile(os.path.join(folder, name), dest)
    for folder, dirs, files in os.walk(DIST, topdown=False):
        for name in files:
            path = os.path.normpath(os.path.join(folder, name))
            if path not in fresh:
                os.remove(path)
        for name in dirs:
            path = os.path.normpath(os.path.join(folder, name))
            if path not in fresh:
                os.rmdir(path)
    shutil.rmtree(tmp, ignore_errors=True)


def build(base=None):
    site = tomllib.load(open(os.path.join(ROOT, "site.toml"), "rb"))
    site_url = site["url"].rstrip("/")
    parsed = urllib.parse.urlparse(site_url)
    if base is None:
        base = parsed.path
    template = open(os.path.join(THEME, "page.html"), encoding="utf-8").read()
    # 樣式改了版本號就變，訪客才不會一直看到瀏覽器存著的舊版
    digest = hashlib.sha1()
    for name in ("site.css", "site.js"):
        digest.update(open(os.path.join(THEME, name), "rb").read())
    template = template.replace("{{ver}}", digest.hexdigest()[:8])
    pages = collect_pages()
    by_url = {p["url"]: p for p in pages}
    tree = build_tree(pages)
    order = list(flatten(tree))
    position = {n["url"]: i for i, n in enumerate(order)}
    tmp = f"{DIST}.tmp{os.getpid()}"
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp)

    for folder in ("images", "tools"):
        src = os.path.join(CONTENT, folder)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(tmp, folder))
    shutil.copytree(THEME, os.path.join(tmp, "assets"), ignore=shutil.ignore_patterns("page.html"))
    variants = build_variants(tmp)
    tools = os.path.join(tmp, "tools")
    for name in os.listdir(tools) if os.path.isdir(tools) else []:
        path = os.path.join(tools, name)
        code = open(path, encoding="utf-8").read()
        open(path, "w", encoding="utf-8", newline="\n").write(with_base(code, base))

    foot = "".join(f'<a href="{esc(l["url"])}" rel="noopener">{esc(l["title"])}</a>' for l in site["footer_links"])
    search, used, html_pages = [], set(), {}
    for p in pages:
        if p["redirect"]:
            continue
        content = render_md(p["body"], used, variants)
        node = next((n for n in order if n["url"] == p["url"]), None)
        extra = ""
        kids = sorted((q for q in pages if q["parts"][:-1] == p["parts"] and q["parts"] and not q["hidden"] and not q["redirect"]),
                      key=lambda q: (q["order"], q["title"]))
        if kids and p["layout"] != "home":
            extra = '<section class="children"><h2>本單元內容</h2><div class="cards">' + "".join(
                card(k["title"], k["url"], k["summary"]) for k in kids) + "</div></section>"
        pager = ""
        if node:
            i = position[p["url"]]
            prev_n = order[i - 1] if i else None
            next_n = order[i + 1] if i + 1 < len(order) else None
            pager = '<nav class="pager" aria-label="上一頁與下一頁">'
            pager += f'<a class="prev" href="{esc(prev_n["url"])}"><small>上一頁</small>{esc(prev_n["title"])}</a>' if prev_n else "<span></span>"
            pager += f'<a class="next" href="{esc(next_n["url"])}"><small>下一頁</small>{esc(next_n["title"])}</a>' if next_n else "<span></span>"
            pager += "</nav>"
        if p["layout"] == "home":
            cards = "".join(card(c["title"], c["url"], c.get("summary", ""), c.get("icon")) for c in site["home_cards"])
            main = (f'<div class="home-body"><div class="prose">{content}</div>'
                    f'<div class="cards home-cards">{cards}</div></div>')
            art = variants[site["hero_art"]]
            srcset = ", ".join(f"{u} {w}w" for u, w in art)
            hero = (f'<section class="hero"><div class="hero-inner"><div class="hero-copy">'
                    f'<p class="hero-kicker">{esc(site["hero_kicker"])}</p>'
                    f'<h1><b>{esc(site["hero_brand"])}</b>{esc(site["hero_title"])}</h1>'
                    f'<p class="hero-slogan">{esc(site["hero_slogan"])}</p></div>'
                    f'<div class="hero-art"><img src="{art[0][0]}" srcset="{srcset}" sizes="(max-width: 640px) 72vw, 460px" '
                    f'width="1120" height="1120" alt="" fetchpriority="high"></div></div>{PAYOFF}</section>')
            body_class, full_title = "home", site["name"]
        else:
            main = (f'{crumbs(p, by_url)}<article class="prose"><h1>{esc(p["title"])}</h1>{content}</article>'
                    f'{extra}{pager}')
            hero, body_class = "", "doc"
            full_title = f'{p["title"]} | {site["name"]}'
        html_pages[p["url"]] = (template
                                .replace("{{title}}", esc(full_title))
                                .replace("{{description}}", esc(p["summary"] or site["description"]))
                                .replace("{{canonical}}", esc(site_url + p["url"]))
                                .replace("{{site_name}}", esc(site["name"]))
                                .replace("{{logo}}", esc(site["logo"]))
                                .replace("{{ga_id}}", esc(site.get("ga_id", "")))
                                .replace("{{nav}}", render_nav(tree, p["url"]))
                                .replace("{{hero}}", hero)
                                .replace("{{body_class}}", body_class)
                                .replace("{{main}}", main)
                                .replace("{{footer_links}}", foot))
        if not p["hidden"]:
            text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(content))).strip()
            search.append({"t": p["title"], "u": base + p["url"], "x": text})

    # 檢查站內連結與圖片，打錯檔名時才不會默默壞掉
    problems = []
    known = {p["url"] for p in pages}
    for url, page_html in html_pages.items():
        for href in re.findall(r'href="(/[^"#?]*)', page_html):
            target = html.unescape(href)
            if target.startswith("/assets/") or os.path.exists(os.path.join(CONTENT, target.lstrip("/"))):
                continue
            if (target if target.endswith("/") else target + "/") not in known:
                problems.append(f"{url} 連到不存在的頁面：{target}")
    for src in sorted(used):
        if not os.path.exists(os.path.join(CONTENT, src.lstrip("/"))):
            problems.append(f"找不到圖片：{src}")

    for url, page_html in html_pages.items():
        dest = os.path.join(tmp, url.lstrip("/"), "index.html")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, "w", encoding="utf-8", newline="\n").write(with_base(page_html, base))
    for p in pages:
        if p["redirect"]:
            dest = os.path.join(tmp, p["url"].lstrip("/"), "index.html")
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            open(dest, "w", encoding="utf-8", newline="\n").write(
                f'<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url={esc(base + p["redirect"])}">'
                f'<link rel="canonical" href="{esc(site_url + p["redirect"])}"><title>{esc(p["title"])}</title>')

    json.dump(search, open(os.path.join(tmp, "search.json"), "w", encoding="utf-8"), ensure_ascii=False)
    notfound = template.replace("{{title}}", "找不到頁面").replace("{{description}}", "").replace("{{canonical}}", esc(site_url + "/")) \
        .replace("{{site_name}}", esc(site["name"])).replace("{{logo}}", esc(site["logo"])) \
        .replace("{{ga_id}}", "").replace("{{nav}}", render_nav(tree, "")).replace("{{hero}}", "").replace("{{body_class}}", "doc") \
        .replace("{{main}}", '<article class="prose"><h1>找不到這個頁面</h1><p>網址可能已經更動，請從左側選單或搜尋找找看，或<a href="/">回首頁</a>。</p></article>') \
        .replace("{{footer_links}}", foot)
    open(os.path.join(tmp, "404.html"), "w", encoding="utf-8", newline="\n").write(with_base(notfound, base))
    urls = "".join(f"<url><loc>{esc(site_url + n['url'])}</loc></url>" for n in order)
    open(os.path.join(tmp, "sitemap.xml"), "w", encoding="utf-8").write(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
    open(os.path.join(tmp, "robots.txt"), "w", encoding="utf-8").write(f"User-agent: *\nAllow: /\nSitemap: {site_url}/sitemap.xml\n")
    if not parsed.netloc.endswith(".github.io"):
        open(os.path.join(tmp, "CNAME"), "w", encoding="utf-8").write(parsed.netloc + "\n")
    open(os.path.join(tmp, ".nojekyll"), "w").close()

    sync_dist(tmp)
    print(f"完成：{len(html_pages)} 頁、{len(used)} 張圖")
    for line in problems:
        print("注意：" + line)
    return problems


def snapshot():
    state = {}
    for base in (CONTENT, THEME):
        for folder, _, files in os.walk(base):
            for name in files:
                path = os.path.join(folder, name)
                state[path] = os.path.getmtime(path)
    state["site"] = os.path.getmtime(os.path.join(ROOT, "site.toml"))
    return state


def watch():
    last = snapshot()
    while True:
        time.sleep(1)
        now = snapshot()
        if now != last:
            last = now
            try:
                build("")
            except Exception as e:
                print("產生失敗：", e)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    # 本機預覽一律從根目錄開，不用管正式網址的子路徑
    problems = build("" if "--serve" in sys.argv else None)
    if "--serve" in sys.argv:
        threading.Thread(target=watch, daemon=True).start()

        class Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *a, **k):
                super().__init__(*a, directory=DIST, **k)

            def log_message(self, *a):
                pass

        print(f"預覽網址：http://localhost:{PORT}/")
        server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
        if "--open" in sys.argv:
            webbrowser.open(f"http://localhost:{PORT}/")
        server.serve_forever()
