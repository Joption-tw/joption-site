# joption-site 進度

## 這是什麼
Joption 官網（https://www.joption.com.tw）。`content/*.md` 由 `build.py` 產生網站，推到 main 會自動部署（GitHub Actions）。

## 目前狀態（2026-11-23）
- **群益安裝說明**（`content/選單/群益安裝說明.md`，隱藏頁）已換成「群益安裝包」新流程，圖片在 `content/images/群益安裝說明/`。舊版內容與舊圖只留在 git 歷史。
- `群益安裝說明_2.md` 只剩轉址，轉到 `/選單/群益安裝說明/`（之前分享過的 _2 網址仍可用）。
- 入口：「群益下載點及安裝說明」頁第 2 張圖連到群益安裝說明。
- **FAQ 新增「排程小幫手」頁**（`content/faq/排程小幫手.md`，order 475）：下載、功能表、Joption 推薦設定（05:40 重開機、08:31 開 Joption）、按鈕說明、常見問題。圖片借用 `/images/群益安裝說明/10.png、11.png`。
- 「登入失敗」FAQ 已改成「通用設定 → 更新帳密」，連到更換金鑰流程（不再叫人刪 pw.txt）。
- 群益安裝說明第 8 節有兩個按鈕：下載排程小幫手、排程小幫手完整說明（連到 FAQ）。
- **FAQ 新增「一鍵上傳 Log 報錯」**（`content/faq/上傳log報錯.md`，order 365，11/23 已公開（拿掉 hidden），UPLOAD_URL 仍空白時顯示「即將開放」）：上傳工具在 `content/tools/log上傳.html`，檔案送到歐大 Google 帳號的 Apps Script（程式碼不在這個 repo）。工具裡 `UPLOAD_URL` 還是空白，空白時頁面顯示「上傳功能準備中」。Apps Script 部署好後把 `.../exec` 網址填進 `UPLOAD_URL`，
  - 11/23 改版：拿掉版本欄（從 Log 判讀）、聯絡改填 E-mail、可貼截圖（Ctrl+V／選檔／拖曳，最多 6 張，縮到 1920）並在頁上畫紅圈；Log、截圖、描述都選填，有一樣就能送；Log 上限 100 MB（網頁端）。步驟標題的說明文字另起一行，手機不會擠成三行。送出多了 `images:[{name,type,data}]`，沒 Log 時 `file` 是空字串——**Apps Script 要能接這兩種情況**。完成畫面教使用者截圖＋報編號給歐大、加 LINE。

## 重要做法
- 下載檔放 `content/files/`（原樣複製，網址 `/files/檔名`）；`content/tools/` 只能放 html。
- 排程小幫手改版時：換 `content/files/` 裡的安裝檔，並改兩個地方的連結版本號（群益安裝說明第 8 節、FAQ 排程小幫手頁）。
- 轉址用 front matter `redirect: /路徑/`。
- 部署確認：查 GitHub Actions 最新 run 的 head_sha 完成，再 curl 正式網址看新文字。

## 試過失敗的
- 把 exe 放 `content/tools/` → build.py 當文字讀，UnicodeDecodeError。
- 電腦螢幕鎖住時截程式畫面會全黑；改用 PIL 修舊圖數字。

## 下一步 / 待決定
- 排程小幫手截圖的 08:31 是修圖的，螢幕開著時可以重截。
