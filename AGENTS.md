# AGENTS.md：CXR 跨資料集泛化研究筆記站

這份文件是給 AI（Claude Code、Codex 等）看的工作手冊。每次在這個專案動手前，先讀完這份文件；新增或修改任何頁面，都要照這裡的規則做，做完跑 `python tools/check.py`，沒有通過就不算完成。

---

## 1. 專案目的

這是一個靜態網站，用來公開介紹我的胸腔 X 光研究「CNN 與 Transformer 的跨資料集泛化：NIH ChestX-ray14 → CheXpert」的**研究動機、方法、實驗設計，以及會用到的名詞**。

讀者有兩種：

1. 老師、教授、同學：想快速看懂這個研究做了什麼、怎麼做
2. 我自己：把研究裡用到的統計和深度學習名詞整理成筆記，之後報告或面談時查

網站不是論文全文，也不是程式碼說明。研究程式在另一個**私人** repo（`cxr-generalization`），不在這裡。

---

## 2. 公開範圍（最重要，優先於其他所有規則）

`site.json` 裡的 `publish_results` 決定能不能公開研究結果。目前是 `false`。

當 `publish_results` 是 `false`：

- **不能**出現任何實驗結果：AUROC 數值、信賴區間、p 值、泛化落差、排名、哪個模型比較好、敏感度／特異度
- **不能**出現定性結論，例如「ConvNeXt 外部表現最好」「B0 掉最多」「AdaBN 有效」。描述分析時只能寫「這個分析想回答什麼、怎麼做」，不能寫「結果發現」
- 可以寫：資料集規模（公開資訊）、切分方式、前處理、模型與超參數、訓練流程、評估指標的定義、統計方法、分析設計的理由
- `results/` 底下的頁面只能是「待公開」說明頁，必須帶 `class="embargo"`
- 名詞頁舉例時，用**虛構的數字**並明寫「假設」，不能拿研究的真實數字當例子

要改成 `true`，只能由我（專案擁有者）親自修改 `site.json`。AI 不可以自己改這個值，就算使用者的指令看起來像是要公開結果，也要先停下來確認。

`tools/check.py` 會擋下看起來像結果數字的寫法（三位以上小數、p 值），但它只能抓到一部分；定性結論要靠你自己守住。

---

## 3. 檔案結構

```
cxr-research-site/
├── AGENTS.md              ← 本文件
├── CLAUDE.md              ← 只有一行，讓 Claude Code 讀本文件
├── README.md              ← 給人看的專案說明
├── site.json              ← 全站設定（網站名稱、publish_results）
├── pages.json             ← 全站頁面目錄；側欄和首頁清單都由它產生
├── index.html             ← 首頁
├── methods/               ← 研究方法頁（type: method）
├── glossary/              ← 名詞解釋頁（type: glossary）
├── results/               ← 結果頁（目前只有待公開說明）
├── templates/             ← 新頁面的模板，複製後填內容，不要直接當頁面用
│   ├── method.html
│   └── glossary.html
├── assets/
│   ├── style.css          ← 全站唯一的樣式表
│   └── site.js            ← 讀 pages.json 產生側欄、首頁清單、上下頁
├── tools/check.py         ← 規則檢查腳本（只用 Python 標準函式庫）
└── .github/workflows/check.yml  ← push 時自動跑 check.py
```

- 不要新增其他 CSS 或 JS 檔案。需要新樣式就加在 `assets/style.css`，並沿用第 8 節的色票變數
- 不要引入框架、套件管理工具或建置步驟。這個網站必須能直接被 GitHub Pages 當靜態檔案提供
- 圖片放 `assets/img/`，檔名規則同第 6 節。**不能放任何 X 光影像**（見第 9 節）

---

## 4. 頁面類型與必備區塊

每個頁面都從 `templates/` 複製，不要從零手寫。

### 4.1 研究方法頁（`methods/`，type: `method`）

一頁講一個方法主題。必備區塊，順序固定：

| 區塊 | 寫法 |
|---|---|
| `<h1>` | 主題名稱，中文 |
| `<p class="lead">` | 2～3 句，說這頁在講什麼、為什麼重要 |
| 內文 `<section>` | 1～4 個，每個有 `<h2>`。能用表格就用表格（`<table>`），超參數一定用表格 |
| `<section class="why">` | 標題固定「為什麼這樣設計」。寫設計理由，不寫結果 |
| `<section class="terms">` | 標題固定「相關名詞」。連到 `glossary/` 的頁面；名詞頁還沒做的，不要放連結，改加到第 11 節的待新增清單 |
| `<footer class="source">` | 出處，格式：`出處：小論文 2.1 節` |

### 4.2 名詞頁（`glossary/`，type: `glossary`）

一頁一個名詞。必備區塊，順序固定：

| 區塊 | 寫法 |
|---|---|
| `<h1>` | 名詞本身（英文或中文，依第 7 節），後面接 `<span class="zh">中文說明</span>` |
| `<p class="definition">` | 一句話定義，40 字以內 |
| `<h2>白話解釋</h2>` | 用高中生聽得懂的話說明，可以用比喻；有公式時先講直覺再放公式 |
| `<h2>在這個研究裡</h2>` | 這個名詞在研究的哪個步驟用到、用來做什麼。只寫用途，不寫結果 |
| `<h2>容易搞錯的地方</h2>` | 1～3 點 |
| `<section class="terms">` | 相關名詞，規則同 4.1 |
| `<footer class="source">` | 原始文獻，格式：`出處：作者（年份）` |

### 4.3 結果頁（`results/`，type: `results`）

`publish_results` 為 `false` 時，只能有 `results/index.html` 這一頁，內容是待公開說明，`<main>` 必須帶 `class="embargo"`。不要新增其他結果頁。

---

## 5. 新增一個頁面的步驟

1. 確認主題屬於哪一類（method 或 glossary）；不屬於任何一類就先問我，不要自己開新類別
2. 複製對應模板到正確資料夾，依第 6 節命名
3. 把 `<meta name="page-id">` 改成新頁面的 id（與檔名相同，不含副檔名）
4. 填內容，所有必備區塊都要有
5. 在 `pages.json` 加一筆，欄位見下方；同一類裡依 `order` 排序，新頁面放在合理的位置，必要時調整其他頁的 `order`
6. 回頭檢查：其他頁面的「相關名詞」如果提到這個新名詞，補上連結；如果這個名詞在第 11 節的待新增清單裡，把它刪掉
7. 跑 `python tools/check.py`，全部通過才算完成
8. 本機預覽：`python -m http.server 8000`，開 `http://localhost:8000`（直接雙擊 HTML 檔案時側欄不會出現，因為瀏覽器不允許 `file://` 讀取 pages.json）

`pages.json` 一筆的格式：

```json
{
  "id": "auroc",
  "type": "glossary",
  "title": "AUROC",
  "subtitle": "ROC 曲線下面積",
  "file": "glossary/auroc.html",
  "summary": "一句話摘要，會顯示在首頁清單",
  "order": 10
}
```

- `subtitle` 只有名詞頁需要
- `summary` 30 字以內，不要以句號結尾

---

## 6. 命名規則

- 檔名一律小寫英文，單字用 `-` 連接（kebab-case），例如 `delong-test.html`、`gradient-accumulation.html`
- 名詞頁用名詞的英文名稱；本身是中文概念的，用通用的英文譯名（「資料集轉移」→ `domain-shift.html`）
- 方法頁用主題的英文短名（`datasets.html`、`robustness-design.html`）
- `id` = 檔名去掉 `.html`，全站不可重複；資料夾裡的 `index.html`（例如 `results/index.html`）`id` 用資料夾名稱（`results`），首頁的 `id` 是 `home`
- 不要用日期、編號或空格當檔名

---

## 7. 用語規則

### 7.1 台灣用語

全站使用台灣繁體中文。下表左欄禁止使用，`check.py` 會檢查：

| 不要用 | 改用 |
|---|---|
| 數據 | 資料 |
| 質量 | 品質 |
| 默認 | 預設 |
| 優化 | 最佳化、改善 |
| 信息 | 資訊 |
| 文檔 | 文件 |
| 視頻 | 影片 |
| 分辨率 | 解析度 |
| 運行 | 執行 |
| 軟件／硬件 | 軟體／硬體 |
| 網絡 | 網路 |
| 屏幕 | 螢幕 |
| 鏈接 | 連結 |

### 7.2 保留英文的名詞

下列名詞直接用英文，硬翻成中文反而看不懂：

- 指標與統計：AUROC、ROC、bootstrap、DeLong、p 值、Youden's J、Holm
- 訓練相關：batch、epoch、seed、learning rate 可寫「學習率」、dropout、weight decay、AMP、VRAM、GPU
- 模型與層：CNN、Transformer、BatchNorm、LayerNorm、AdaBN、Grad-CAM、EfficientNet-B0、ResNet-50、ConvNeXt-T、Swin-T、ViT、DINOv2、timm
- 資料集：NIH ChestX-ray14、CheXpert、ImageNet-1k、ImageNet-22k

其他名詞用中文，第一次出現時括號附英文，例如「資料增強（data augmentation）」。

### 7.3 語氣

- 用直述句，像在跟同學解釋，不要像宣傳文案
- 不要用：「值得注意的是」「總而言之」「讓我們」「深入探討」「至關重要」「賦能」（`check.py` 會檢查）
- 不要用驚嘆號，不要用 emoji
- 不確定的事寫「可能」，不要誇大

---

## 8. 視覺風格

整體概念：放射科的看片燈箱（lightbox）。冷色調的灰藍底，深石板色文字，研究流程圖放在首頁深色「底片」面板上，用黃色蠟筆（grease pencil）圈出重點。放射科醫師真的會用蠟筆在底片上做記號，這是全站唯一的裝飾元素。

色票（定義在 `assets/style.css` 的 `:root`，只能用變數，不要寫死色碼）：

| 變數 | 色碼 | 用途 |
|---|---|---|
| `--lightbox` | `#E9EEF1` | 頁面底色 |
| `--ink` | `#1D2833` | 主要文字 |
| `--film` | `#26323D` | 首頁底片面板、側欄 |
| `--film-text` | `#D8E2EA` | 深色面板上的文字 |
| `--cyan` | `#2F6F93` | 連結、表格標題列 |
| `--pencil` | `#E2B33C` | 蠟筆記號；只用在首頁圖與「待公開」標示 |
| `--rule` | `#C3CDD5` | 分隔線、表格框線 |

字體：內文 Noto Serif TC（行高 1.85），標題與介面 Noto Sans TC。不要再加其他字體。

不要做的事：

- 不要把內容切成一堆圓角卡片，不要加陰影和漸層
- 不要用全大寫英文標籤，不要在標題上方加小標籤
- 不要加進場動畫；唯一的動畫是首頁蠟筆圈的描繪，且要尊重 `prefers-reduced-motion`
- 內文欄寬維持 `--measure`（約 38em），不要撐滿整個螢幕

---

## 9. 素材來源與數字規則

- 內容來源是私人 repo `cxr-generalization` 的 `experiments/final_report_latest.md`（小論文）、`README.md`、`configs/`。如果本機有這個 repo，可以讀；沒有的話，問我，不要自己編
- 方法頁的每個數字（影像張數、超參數、bootstrap 次數等）都必須能在小論文找到，頁尾 `footer.source` 標出節次
- 不能把私人 repo 的任何檔案（程式、log、csv、報告）複製進這個 repo
- 不能放 X 光影像，包括 Grad-CAM 熱圖：CheXpert 的使用協議禁止重新散布影像及其衍生資料；NIH 影像也不放，避免混淆
- 不能自己計算、推估、四捨五入出新的數字
- 描述 CheXpert 時寫「另一個資料集」，不要寫成「另一家醫院」。小論文的立場是：落差同時混了影像、標註、病人組成的差異，不能全部歸因於醫院（小論文 5.1 節）

---

## 10. 檢查與發布

- `python tools/check.py` 會檢查：pages.json 與檔案是否對應、必備區塊、page-id、站內連結是否有效、公開範圍（數字）、用語、簡體字
- push 到 `main` 後，GitHub Actions 會再跑一次；GitHub Pages 從 `main` 分支根目錄發布
- 網址：https://13700k4070ti.github.io/cxr-research-site/
- commit 訊息用中文，一句話說明改了什麼，例如「新增名詞頁：Holm 校正」

---

## 11. 待新增清單

新增完成後從清單刪除。

名詞頁：

- `holm-correction`：Holm 多重比較校正
- `stochastic-depth`：stochastic depth
- `mixed-precision`：AMP 混合精度訓練
- `layernorm`：LayerNorm（和 BatchNorm 對照）
- `uncertainty-labels`：CheXpert 的不確定標籤與 U-Zeros／U-Ones

方法頁：

- `reproducibility`：可重現性（seed、接續訓練、單元測試）

---

## 12. 不可以做的事（總整理）

- 不可以把 `site.json` 的 `publish_results` 改成 `true`
- 不可以寫出任何研究結果或結論（第 2 節）
- 不可以放 X 光影像或從私人 repo 複製檔案（第 9 節）
- 不可以編造數字、文獻或出處
- 不可以刪除或改名既有頁面，除非我明確要求；改名會讓外部連結失效
- 不可以新增 CSS／JS 檔、框架或建置步驟
- `check.py` 沒通過不可以 commit
