"""檢查網站是否符合 AGENTS.md 的規則。

用法（在專案根目錄）：python tools/check.py
全部通過時結束碼為 0；有任何錯誤時列出錯誤並以 1 結束。
只用 Python 標準函式庫，不需要安裝任何套件。
"""

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 頁面類型 → 所在資料夾（AGENTS.md 第 3、4 節）
TYPE_DIRS = {"method": "methods", "glossary": "glossary", "results": "results"}

# 各類型的必備區塊：(說明, 判斷函式)
REQUIRED = {
    "method": [
        ("<h1>", lambda p: p.has_tag("h1")),
        ('<p class="lead">', lambda p: p.has_class("p", "lead")),
        ('<section class="why">，標題「為什麼這樣設計」', lambda p: p.has_class("section", "why") and "為什麼這樣設計" in p.h2s),
        ('<section class="terms">，標題「相關名詞」', lambda p: p.has_class("section", "terms") and "相關名詞" in p.h2s),
        ('<footer class="source">', lambda p: p.has_class("footer", "source")),
    ],
    "glossary": [
        ('<h1> 內含 <span class="zh">', lambda p: p.has_tag("h1") and p.has_class("span", "zh")),
        ('<p class="definition">', lambda p: p.has_class("p", "definition")),
        ("<h2>白話解釋</h2>", lambda p: "白話解釋" in p.h2s),
        ("<h2>在這個研究裡</h2>", lambda p: "在這個研究裡" in p.h2s),
        ("<h2>容易搞錯的地方</h2>", lambda p: "容易搞錯的地方" in p.h2s),
        ('<section class="terms">', lambda p: p.has_class("section", "terms") and "相關名詞" in p.h2s),
        ('<footer class="source">', lambda p: p.has_class("footer", "source")),
    ],
    "results": [
        ('<main class="... embargo">', lambda p: p.has_class("main", "embargo")),
    ],
}

# AGENTS.md 7.1：大陸用語
BANNED_TERMS = ["數據", "質量", "默認", "優化", "信息", "文檔", "視頻", "分辨率", "運行",
                "軟件", "硬件", "網絡", "屏幕", "鏈接"]
# AGENTS.md 7.2：專有名詞用英文，不要用中文譯名
BANNED_TRANSLATIONS = ["拔靴法", "自助法", "約登指數", "批次正規化", "梯度累積", "資料增強", "最佳化器",
                       "損失函數", "提早停止", "資料集轉移", "混合精度", "梯度加權類別活化圖", "二元交叉熵",
                       "學習率", "特徵圖", "自然語言處理"]
# AGENTS.md 7.3：空泛語句
BANNED_PHRASES = ["值得注意的是", "總而言之", "讓我們", "深入探討", "至關重要", "賦能"]
# 常見的簡體字（只收繁體中不會出現的字）
SIMPLIFIED = set("这们个为时说据对发关应质图学习试训练层网络类数实验结统计")

# AGENTS.md 第 2 節：publish_results 為 false 時，看起來像結果的數字
RESULT_PATTERNS = [
    (re.compile(r"(?<![\d.])0\.\d{3,}"), "三位以上小數（像 AUROC）"),
    (re.compile(r"\bp\s*[<=≤＜＝]\s*0?\.\d"), "p 值"),
]

KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*\.html$")


class PageParser(HTMLParser):
    """收集檢查需要的資訊：標籤、class、h2 文字、連結、page-id、純文字。"""

    def __init__(self):
        super().__init__()
        self.tags = []          # (tag, class 集合)
        self.h2s = []
        self.links = []
        self.page_id = None
        self.data_root = None
        self.text = []
        self._in_h2 = False
        self._h2_buf = ""
        self._skip = 0          # script/style 內的文字不算

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags.append((tag, set((a.get("class") or "").split())))
        if tag == "meta" and a.get("name") == "page-id":
            self.page_id = a.get("content")
        if tag == "body":
            self.data_root = a.get("data-root")
        if tag in ("a", "link", "script", "img") :
            ref = a.get("href") or a.get("src")
            if ref:
                self.links.append(ref)
        if tag == "h2":
            self._in_h2, self._h2_buf = True, ""
        if tag in ("script", "style"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag == "h2" and self._in_h2:
            self.h2s.append(self._h2_buf.strip())
            self._in_h2 = False
        if tag in ("script", "style"):
            self._skip -= 1

    def handle_data(self, data):
        if self._in_h2:
            self._h2_buf += data
        if not self._skip:
            self.text.append(data)

    def has_tag(self, tag):
        return any(t == tag for t, _ in self.tags)

    def has_class(self, tag, cls):
        return any(t == tag and cls in c for t, c in self.tags)


def parse(path):
    p = PageParser()
    p.feed(path.read_text(encoding="utf-8"))
    return p


def main():
    errors = []

    def err(where, msg):
        errors.append(f"{where}: {msg}")

    site = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
    pages = json.loads((ROOT / "pages.json").read_text(encoding="utf-8"))
    publish = site.get("publish_results") is True

    # ---- pages.json 本身 ----
    ids = set()
    listed_files = set()
    for i, p in enumerate(pages):
        where = f"pages.json 第 {i + 1} 筆"
        for key in ("id", "type", "title", "file", "summary", "order"):
            if key not in p:
                err(where, f"缺少欄位 {key}")
        if p.get("id") in ids:
            err(where, f"id 重複：{p.get('id')}")
        ids.add(p.get("id"))
        if p.get("type") == "glossary" and not p.get("subtitle"):
            err(where, "名詞頁需要 subtitle")
        if len(p.get("summary", "")) > 30 or p.get("summary", "").endswith("。"):
            err(where, "summary 要 30 字以內，且不以句號結尾")
        f = p.get("file", "")
        listed_files.add(f)
        if f == "index.html":
            continue
        t = p.get("type")
        if t not in TYPE_DIRS:
            err(where, f"未知的 type：{t}")
            continue
        folder, _, name = f.partition("/")
        if folder != TYPE_DIRS[t]:
            err(where, f"type 為 {t} 的頁面要放在 {TYPE_DIRS[t]}/")
        if not KEBAB.match(name):
            err(where, f"檔名要用小寫 kebab-case：{name}")
        # 一般頁面：id = 檔名去掉 .html；資料夾的 index.html：id = 資料夾名稱
        expect_id = folder if name == "index.html" else Path(name).stem
        if expect_id != p.get("id"):
            err(where, f"id 應為 {expect_id}，目前是 {p.get('id')}")
        if not (ROOT / f).exists():
            err(where, f"檔案不存在：{f}")

    # ---- 沒列進 pages.json 的頁面 ----
    for folder in TYPE_DIRS.values():
        for html in sorted((ROOT / folder).glob("*.html")):
            rel = html.relative_to(ROOT).as_posix()
            if rel not in listed_files:
                err(rel, "沒有列在 pages.json")

    if not publish:
        extra = [p["file"] for p in pages if p.get("type") == "results" and p["file"] != "results/index.html"]
        for f in extra:
            err(f, "publish_results 為 false 時，results/ 只能有 index.html")

    # ---- 逐頁檢查 ----
    for p in pages:
        f = p.get("file")
        path = ROOT / f
        if not path.exists():
            continue
        doc = parse(path)
        depth = f.count("/")
        expect_root = "./" if depth == 0 else "../" * depth

        if doc.page_id != p["id"]:
            err(f, f'<meta name="page-id"> 應為 {p["id"]}，目前是 {doc.page_id}')
        if doc.data_root != expect_root:
            err(f, f'<body data-root> 應為 "{expect_root}"')
        resolved = {(path.parent / ref).resolve() for ref in doc.links}
        if (ROOT / "assets/style.css").resolve() not in resolved or (ROOT / "assets/site.js").resolve() not in resolved:
            err(f, "要引用 assets/style.css 與 assets/site.js")
        if not doc.has_class("nav", "sidebar"):
            err(f, '缺少 <nav class="sidebar" id="site-nav">')

        for label, test in REQUIRED.get(p["type"], []):
            if not test(doc):
                err(f, f"缺少必備區塊 {label}")

        # 站內連結
        for ref in doc.links:
            if re.match(r"^(https?:|mailto:|#)", ref):
                continue
            target = (path.parent / ref.split("#")[0]).resolve()
            if not target.exists():
                err(f, f"連結失效：{ref}")

        text = "".join(doc.text)
        for term in BANNED_TERMS:
            if term in text:
                err(f, f"出現大陸用語「{term}」（見 AGENTS.md 7.1）")
        for term in BANNED_TRANSLATIONS:
            if term in text:
                err(f, f"出現中文譯名「{term}」，專有名詞請用英文（見 AGENTS.md 7.2）")
        for phrase in BANNED_PHRASES:
            if phrase in text:
                err(f, f"出現禁用語「{phrase}」（見 AGENTS.md 7.3）")
        simp = sorted(SIMPLIFIED & set(text))
        if simp:
            err(f, f"出現簡體字：{''.join(simp)}")
        if "！" in text or "!" in text:
            err(f, "不要用驚嘆號（見 AGENTS.md 7.3）")

        if not publish:
            for pattern, label in RESULT_PATTERNS:
                m = pattern.search(text)
                if m:
                    err(f, f"publish_results 為 false，但出現疑似結果的{label}：「{m.group(0)}」")

    if errors:
        print(f"檢查未通過，共 {len(errors)} 個問題：")
        for e in errors:
            print("  - " + e)
        return 1
    print(f"檢查通過：{len(pages)} 個頁面。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
