---
title: CALL點數控管
order: 190
---

<a id="h.kqpao1rnf73l"></a>

![](/images/call點數控管/01.png)

---

<div class="cols" markdown="1">

<div markdown="1">

![](/images/call點數控管/02.png)

</div>

<div markdown="1">

總開關選擇(開啟)，呈現綠色

表示策略已開啟，等待執行

</div>

</div>

---

<div class="cols" markdown="1">

<div markdown="1">

![](/images/call點數控管/03.png)

</div>

<div markdown="1">

本策略刪單的時間

</div>

</div>

---

![](/images/call點數控管/04.png)

**==當點數大於：==**

第一行
CALL點數大於 960點以上時，【BUY CALL】，買在價外14檔，用更優價二檔買入1口 + 【SELL CALL】賣在此買方的價外1檔 (價外15檔)，以 更優價一檔 賣出 0 口；每 6 秒下單一次

第二行
CALL點數大於 800點以上時，【BUY CALL】，買在價外14檔，用更優價一檔買入1口 + 【SELL CALL】賣在此買方的價外1檔 (價外15檔)，以 更優價一檔 賣出 0 口；每 6 秒下單一次

第一行與第二行 為點數大於程度上的不同

下單價格選項為示意，可依需求選擇，下單價格說明請參考([價格說明](/選單/通用設定#h.ufxedp5ot527))

---

![](/images/call點數控管/05.png)

**==當點數小於：==**

第三行
CALL點數小於 500點以下時，【SELL CALL】，買在價外14檔，用更優價一檔賣入1口 + 【BUY CALL】賣在此賣方的價外1檔 (價外15檔)，以 更優價一檔 買入 0 口；每 6 秒下單一次

第四行
CALL點數小於 4170點以下時，【SELL CALL】，買在價外14檔，用更優價一檔賣入1口 + 【BUY CALL】賣在此賣方的價外1檔 (價外15檔)，以 更優價一檔 買入 0 口；每 6 秒下單一次

第三行與第四行 為點數大於程度上的不同

下單價格選項為示意，可依需求選擇，下單價格說明請參考([價格說明](/選單/通用設定#h.ufxedp5ot527))

---

<div class="cols" markdown="1">

<div markdown="1">

![](/images/call點數控管/06.png)

</div>

<div markdown="1">

當保證金低於10萬時，則停止下單

下單的位置權利金不足30點，則往價內大於30點的一檔位置下單

</div>

</div>

---

<div class="cols" markdown="1">

<div markdown="1">

![](/images/call點數控管/07.png)

</div>

<div markdown="1">

每6秒下單一次

優先平倉價內:下單時，若比原測定下單位置價內有更貴的口數可以平倉，則優先下單平倉之

</div>

</div>

---

![](/images/call點數控管/08.png)

==因為有勾選優先平倉價內，以及建新倉在30點以上，==

==則平倉時，不會去平倉價外14檔..會去尋找比14檔更價內的優先平倉==

==也不會真的加倉在價外14檔，會去尋找權利金30點的檔位下單==

---

[回 全策略說明](/選單/全策略說明){.btn}
