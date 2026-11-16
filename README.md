# CXR 跨資料集泛化研究筆記

胸腔 X 光模型換一家醫院還準嗎？這個網站整理我的研究「CNN 與 Transformer 的跨資料集泛化：NIH ChestX-ray14 → CheXpert」的研究動機、方法、實驗設計與名詞解釋。

網站：https://13700k4070ti.github.io/cxr-research-site/

## 這個 repo 的重點：AGENTS.md

這個專案的開發規則寫在 [`AGENTS.md`](AGENTS.md)（`CLAUDE.md` 只有一行 `@AGENTS.md`，讓 Claude Code 也讀同一份）。AI 讀完它就知道：

- 網站的目的與讀者
- 哪些內容可以公開、哪些不行（結果數字由 `site.json` 的 `publish_results` 控制）
- 方法頁、名詞頁各自的必備區塊與模板
- 檔案命名、`pages.json` 的格式
- 台灣用語、保留英文的名詞、視覺風格
- 還有哪些頁面待新增

規則由 `tools/check.py` 自動檢查，push 時 GitHub Actions 也會再跑一次。

## 新增一頁

對 AI 說「讀 AGENTS.md，新增名詞頁：Holm 校正」，它會照第 5 節的步驟複製模板、填內容、更新 `pages.json`、跑檢查。

本機預覽：

```bash
python -m http.server 8000
python tools/check.py
```

## 說明

- 研究程式碼在另一個私人 repo，不在這裡
- 網站不放任何 X 光影像
- 網頁與規則檔在 Claude Code 協助下完成
