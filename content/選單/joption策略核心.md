---
title: Joption策略核心
order: 350
---

**Joption=雙賣策略+平衡策略**

[**當沖策略說明**](/faq/當沖策略說明)

**策略核心**：自動化雙賣＋即時平衡調整。

**獲利來源**：時間價值衰減 + 區間震盪 + 系統化風險控制。

**優勢**：避免人性弱點（貪婪、恐慌、遲疑），追求穩定、可持續的收益曲線。

![](/images/joption策略核心/01.png)

---

---

<div class="cols" markdown="1">

<div markdown="1">

<a id="h.tob03vly3afn"></a>

### 一、Joption 的策略原則

1. **核心策略：雙賣平衡**
    - 透過同時賣出 Call 與 Put（選擇權賣方），建立「中立偏套利」的部位。
    - 系統自動計算 Call/Put 部位的價值比，並持續監控是否失衡。
    - 若失衡超過設定範圍（如 ±5%），則自動進行調整，避免一邊部位過度暴露風險。
2. **風險即時監控**
    - 系統自動偵測部位保證金、履約價分布與 Delta 風險。
    - 一旦出現過度集中或單邊行情，會觸發「部位清倉」或「偏移調整」。
3. **自動化調整邏輯**
    - **比值調整**：當 Put/Call 的市值比過度傾斜，系統會補單或平倉修正。
    - **多口清倉**：當部位超過設定口數或保證金風險提升時，自動分批出場。
    - **時間與價差控制**：接近結算日或行情急劇變動時，自動收斂部位，避免暴雷。

</div>

<div markdown="1">

<a id="h.fzr9xra1ydlm"></a>

### 二、Joption 的獲利來源

1. **時間價值衰減（Theta 收益）**
    - 選擇權在時間流逝下會不斷失去價值。
    - Joption 把握這個「時間換錢」的特性，透過賣方收取權利金並持續控管風險。
2. **維持部位平衡**
    - 傳統人工交易容易因情緒延遲導致失衡，造成一邊暴增虧損。
    - Joption 透過自動化調整，維持長期「小賺大穩」的結構，避免一次性大賠。
3. **波動率收斂效應**
    - 在無趨勢或區間震盪行情中，賣方策略獲利機率最高。
    - Joption 把握這種「行情無方向但時間在走」的市場特性，持續累積權利金收益。
4. **系統化風險控制**
    - 不靠預測方向，而靠「控風險、穩保證金」來確保獲利持續性。
    - 系統可避免爆倉或一次大虧的狀況，使整體策略具備長期正期望值。

</div>

</div>

---

![](/images/joption策略核心/02.png)

---

![](/images/joption策略核心/03.png)

---

![](/images/joption策略核心/04.png)

---

![](/images/joption策略核心/05.png)

---

![](/images/joption策略核心/06.png)

**Joption的優勢**

![](/images/joption策略核心/07.png)

---

![](/images/joption策略核心/08.png)

---

![](/images/joption策略核心/09.png)

---

![](/images/joption策略核心/10.png)

---

![](/images/joption策略核心/11.png)

---

![](/images/joption策略核心/12.png)

---

![](/images/joption策略核心/13.png)

---

![](/images/joption策略核心/14.png)

---

![](/images/joption策略核心/15.png)

---

**雙賣+平衡策略的實單績效**

[![](/images/joption策略核心/16.png)](https://docs.google.com/spreadsheets/d/1AsY4_MJipaMp_cNLpyeXTpFGnG0FD4vWJu-SDRdvtME/edit?gid=1908704661#gid=1908704661)

---

[![](/images/joption策略核心/17.png)](https://docs.google.com/spreadsheets/d/1AsY4_MJipaMp_cNLpyeXTpFGnG0FD4vWJu-SDRdvtME/edit?gid=1908704661#gid=1908704661)

[![](/images/joption策略核心/18.png)](https://docs.google.com/spreadsheets/d/1AsY4_MJipaMp_cNLpyeXTpFGnG0FD4vWJu-SDRdvtME/edit?gid=1908704661#gid=1908704661)

[![](/images/joption策略核心/19.png)](https://docs.google.com/spreadsheets/d/1AsY4_MJipaMp_cNLpyeXTpFGnG0FD4vWJu-SDRdvtME/edit?gid=1908704661#gid=1908704661)

[![](/images/joption策略核心/20.png)](https://docs.google.com/spreadsheets/d/1AsY4_MJipaMp_cNLpyeXTpFGnG0FD4vWJu-SDRdvtME/edit?gid=1908704661#gid=1908704661)

![](/images/joption策略核心/21.png)

**即時績效，持續更新中, 點擊即可進入即時績效畫面** [**點擊**](https://docs.google.com/spreadsheets/d/1AsY4_MJipaMp_cNLpyeXTpFGnG0FD4vWJu-SDRdvtME/edit?gid=1908704661#gid=1908704661)

[即時績效，持續更新中, 點擊即可進入即時績效畫面](https://docs.google.com/spreadsheets/d/1AsY4_MJipaMp_cNLpyeXTpFGnG0FD4vWJu-SDRdvtME/edit?gid=1908704661#gid=1908704661){.btn}

---

**榮譽榜**

**2023年人機對決個人賽總冠軍賽_ 第三名**

<div class="cols" markdown="1">

<div markdown="1">

![](/images/joption策略核心/22.png)

![](/images/joption策略核心/23.png)

</div>

<div markdown="1">

![](/images/joption策略核心/24.png)

</div>

</div>

<div class="cols" markdown="1">

<div markdown="1">

**排名第三、成績穩定** → 戰績不是偶然，而是長期有效策略。

**無大幅回測** → 充分展現 Joption 系統化控風險的優勢。

**報酬曲線平穩向上** → 避免暴雷，展現複利的力量。

</div>

<div markdown="1">

[2023年人機對決參考網站](https://activity.capitalfutures.com.tw/AC230630/Profile/c6db2651-108e-4141-9036-280ce5bfb50a){.btn}

[群益贏家名人堂參考網站](https://activity.capitalfutures.com.tw/Winner/Ranking){.btn}

</div>

</div>

---

**群益贏家名人堂大聯盟23名**

![](/images/joption策略核心/25.png)

---

**2025年人機對決**

**個人賽_ 第二名**

**團體賽_ 冠 軍**

<div class="cols" markdown="1">

[![](/images/joption策略核心/26.png)](https://activity.capitalfutures.com.tw/AC250915/Rank/ScoreRank?Gaoup=all&Finals=1)

![](/images/joption策略核心/27.png)

</div>

<div class="cols" markdown="1">

![](/images/joption策略核心/28.png)

![](/images/joption策略核心/29.png)

</div>

<div class="cols" markdown="1">

![](/images/joption策略核心/30.png)

![](/images/joption策略核心/31.png)

</div>

---

**2025年 上海期貨日報 全球賽重量組 第七名**

<div class="cols" markdown="1">

![](/images/joption策略核心/32.png)

![](/images/joption策略核心/33.jpg)

</div>

<div class="cols" markdown="1">

![](/images/joption策略核心/34.jpg)

![](/images/joption策略核心/35.jpg)

</div>

---

**Joption是正規軍，擁有多項專利證書**

<div class="cols" markdown="1">

![](/images/joption策略核心/36.jpg)

![](/images/joption策略核心/37.jpg)

![](/images/joption策略核心/38.jpg)

</div>

<div class="cols" markdown="1">

<div markdown="1">

![](/images/joption策略核心/39.jpg)

</div>

<div markdown="1">

![](/images/joption策略核心/40.jpg)

</div>

<div markdown="1">

更多專利申請中

</div>

</div>

---
