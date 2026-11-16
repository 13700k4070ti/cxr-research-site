// 讀 pages.json，產生側欄、首頁清單和上下頁連結。
// 每個頁面的 <body data-root> 指向網站根目錄（根目錄頁是 "./"，子資料夾頁是 "../"）。

(function () {
  const root = document.body.dataset.root || "./";
  const currentId = (document.querySelector('meta[name="page-id"]') || {}).content;

  // 側欄分組的順序與標題
  const GROUPS = [
    { type: "method", label: "研究方法" },
    { type: "glossary", label: "名詞解釋" },
    { type: "results", label: "研究結果" },
  ];

  function el(tag, attrs, children) {
    const node = document.createElement(tag);
    Object.entries(attrs || {}).forEach(([k, v]) => {
      if (k === "text") node.textContent = v;
      else node.setAttribute(k, v);
    });
    (children || []).forEach((c) => node.appendChild(c));
    return node;
  }

  function byType(pages, type) {
    return pages.filter((p) => p.type === type).sort((a, b) => a.order - b.order);
  }

  function buildSidebar(site, pages) {
    const nav = document.getElementById("site-nav");
    if (!nav) return;
    nav.innerHTML = "";
    nav.setAttribute("aria-label", "網站導覽");

    nav.appendChild(el("a", { class: "site-name", href: root + "index.html", text: site.title }));

    const toggle = el("button", { class: "nav-toggle", type: "button", "aria-expanded": "false", text: "目錄" });
    toggle.addEventListener("click", () => {
      const open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(open));
    });
    nav.appendChild(toggle);

    const body = el("div", { class: "nav-body" });
    GROUPS.forEach((g) => {
      const items = byType(pages, g.type);
      if (!items.length) return;
      const ul = el("ul");
      items.forEach((p) => {
        const a = el("a", { href: root + p.file, text: p.title });
        if (p.id === currentId) a.setAttribute("aria-current", "page");
        ul.appendChild(el("li", {}, [a]));
      });
      body.appendChild(el("div", { class: "nav-group" }, [el("h2", { text: g.label }), ul]));
    });
    nav.appendChild(body);
  }

  // 首頁：<ul data-list="method"> 會被填入該類型的所有頁面
  function buildLists(pages) {
    document.querySelectorAll("[data-list]").forEach((ul) => {
      ul.innerHTML = "";
      byType(pages, ul.dataset.list).forEach((p) => {
        const title = el("span", { class: "pl-title", text: p.title });
        if (p.subtitle) title.appendChild(el("small", { text: p.subtitle }));
        const a = el("a", { href: root + p.file }, [title, el("span", { class: "pl-summary", text: p.summary })]);
        ul.appendChild(el("li", {}, [a]));
      });
    });
  }

  // 內頁：同類型的上一頁／下一頁
  function buildPager(pages) {
    const main = document.querySelector("main.page");
    const me = pages.find((p) => p.id === currentId);
    if (!main || !me || me.type === "results" || currentId === "home") return;
    const list = byType(pages, me.type);
    const i = list.indexOf(me);
    const pager = el("nav", { class: "pager", "aria-label": "上一頁與下一頁" });
    if (list[i - 1]) {
      pager.appendChild(el("a", { class: "prev", href: root + list[i - 1].file }, [el("small", { text: "上一頁" }), document.createTextNode(list[i - 1].title)]));
    }
    if (list[i + 1]) {
      pager.appendChild(el("a", { class: "next", href: root + list[i + 1].file }, [el("small", { text: "下一頁" }), document.createTextNode(list[i + 1].title)]));
    }
    const source = main.querySelector(".source");
    main.insertBefore(pager, source);
  }

  Promise.all([
    fetch(root + "site.json").then((r) => r.json()),
    fetch(root + "pages.json").then((r) => r.json()),
  ])
    .then(([site, pages]) => {
      buildSidebar(site, pages);
      buildLists(pages);
      buildPager(pages);
    })
    .catch(() => {
      const nav = document.getElementById("site-nav");
      if (nav) nav.innerHTML = '<a class="site-name" href="' + root + 'index.html">CXR 跨資料集泛化研究筆記</a><p class="noscript-note">目錄載入失敗。在本機預覽請用 python -m http.server 開啟。</p>';
    });
})();
