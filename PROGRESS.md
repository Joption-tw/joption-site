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
  - 11/23 改版：拿掉版本欄（從 Log 判讀）、聯絡改填 E-mail、可貼截圖（Ctrl+V／選檔／拖曳，最多 6 張，縮到 1920）並在頁上畫紅圈；Log、截圖、描述都選填，有一樣就能送；Log 上限 100 MB（網頁端）。11/24 加「Log 瘦身」：送出前在瀏覽器用 JSZip（`content/files/jszip.min.js`，MIT）解開 .zip，每個 Log 只留最後 1.5 MB、全部最多 4 MB，轉成一個 .txt 才上傳，解決大檔送不出去；送到 Apps Script 的檔名變成 `原檔名.txt`。步驟標題的說明文字另起一行，手機不會擠成三行。送出多了 `images:[{name,type,data}]`，沒 Log 時 `file` 是空字串——**Apps Script 要能接這兩種情況**。完成畫面教使用者截圖＋報編號給歐大、加 LINE。

- 11/24 價格名詞統一：圖片裡的「中間偏易價→更優價二檔」「中間偏難價→更優價一檔」已改（報價區及手動下單/12、13.png，下單價格選擇指南/01.jpg；12、13 也用在通用設定頁）。文字本來就是新名詞。修圖程式在 scratchpad（price/fix.py），用 mingliu 逐字重寫。

- **凱基安裝說明**（`content/選單/凱基安裝說明.md`，隱藏頁，11/24）改成「凱基安裝包」新流程（11/24 已發布），格式照群益安裝說明；圖 01～17.png 在 `content/images/凱基安裝說明/`（舊的 01～17.jpg 只留在 git 歷史）。
  下載按鈕連到雲端「凱基雙賣平衡下單機下載\凱基安裝包.exe」（id 16tMUt6Pfk5dRgPrVz8dOzoV5LtBcSWsR）。截圖來源與打馬賽克：D:\桌面\測試\凱基安裝教學截圖（安裝包原始碼在 D:\桌面\測試\packaging\kgi_setup）。
  頁面內容不可提到其他公司（群益等），排程、換授權碼步驟直接寫在本頁、不連群益頁和更換金鑰 FAQ。「凱基下載點及安裝說明」第 1 張圖還連到舊的雲端檔（1PH1aThKqdz4oeq6Ioalu4CScp-IpiVAF），要不要改成安裝包待使用者決定。

## 重要做法
- 下載檔放 `content/files/`（原樣複製，網址 `/files/檔名`）；`content/tools/` 只能放 html。
- 排程小幫手改版時：換 `content/files/` 裡的安裝檔，並改兩個地方的連結版本號（群益安裝說明第 8 節、FAQ 排程小幫手頁）。
- 部署：`.github/workflows/deploy.yml` 已拆成 build／deploy 兩個工作、Pages 元件用 v5（11/24 同一工作裡 deploy-pages 連續找不到剛上傳的 github-pages 產物，拆開才好）。不要改回同一個工作；重跑請推新 commit，不要 re-run（會出現兩份產物）。
- 轉址用 front matter `redirect: /路徑/`。
- 側邊選單最下面的外部連結都是 `content/` 根目錄的轉址頁（只有 title／order／redirect）：歐大選擇權教室 900、富台指轉換器 910、歷史時間價值比對 920（sample/time-value）、示範帳號投資報表 930（Investment-Report demo）、同學會監控中心 940（/tools/monitor.html，11/24 起放進選單）。要加新的照這樣做一個 .md。
- 不想在頁面下方列出「本單元內容」子頁卡片：front matter 加 `children: false`（側邊選單照樣有子頁）。11/24 用在「下載及安裝說明」，該頁只寫「請聯繫歐大官方客服」＋加 LINE@ 按鈕。
- **歐大專用頁**：front matter `owner: true`（通常配 `hidden: true`）→ 一般人只看到「請聯繫歐大官方客服」＋LINE@ 按鈕和小小的「歐大登入」；輸入歐大 E-mail（網站只存雜湊）後存在瀏覽器，才顯示內容。11/24 群益／凱基下載點和新增的台新、富邦期貨、統一期貨（後三頁目前只寫「準備中」，等歐大給下載點和圖）改成這樣；元富頁改成轉址到台新、元富圖已刪，入口在「下載及安裝說明」頁的「歐大專用」按鈕。注意這是藏起來不是加密，知道網址的人看原始碼還是看得到；hidden 頁另加 noindex。
- 部署確認：查 GitHub Actions 最新 run 的 head_sha 完成，再 curl 正式網址看新文字。

## 試過失敗的
- 把 exe 放 `content/tools/` → build.py 當文字讀，UnicodeDecodeError。
- 電腦螢幕鎖住時截程式畫面會全黑；改用 PIL 修舊圖數字。

## 下一步 / 待決定
- 排程小幫手截圖的 08:31 是修圖的，螢幕開著時可以重截。
