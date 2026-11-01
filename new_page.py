"""新增一頁：問分類和標題，建好檔案後用記事本打開。

    python new_page.py
"""
import os, re, subprocess, sys

from build import CONTENT

TEMPLATE = """---
title: {title}
summary:
---

在這裡開始寫內容。一行字就是一行，空一行就是新段落。

## 小標題

**粗體字**、==紅色強調==、[連結文字](https://www.joption.com.tw/)

- 項目一
- 項目二

圖片先放進 content/images/ 資料夾，再這樣寫：

![圖片說明](/images/檔名.png)

YouTube 影片（網址 v= 後面那一串）：

[[youtube:影片代碼]]
"""


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")
    choices = [("FAQ 常見問題", "faq"), ("策略說明", "選單/全策略說明"), ("參數介紹", "選單/參數設定介紹與建議"),
               ("選擇權知識", "選單/選擇權知識"), ("選單其他頁面", "選單"), ("初學者知識", "首頁/初學者必備的選擇權知識")]
    for i, (label, _) in enumerate(choices, 1):
        print(f"{i}. {label}")
    pick = input("放在哪一類？輸入數字：").strip()
    if not pick.isdigit() or not 1 <= int(pick) <= len(choices):
        print("沒有這個選項")
        return
    title = input("頁面標題：").strip()
    name = re.sub(r'[\\/:*?"<>|\s]+', "-", title).strip("-").lower()
    if not name:
        print("標題不能空白")
        return
    path = os.path.join(CONTENT, *choices[int(pick) - 1][1].split("/"), name + ".md")
    if os.path.exists(path):
        print("這個標題已經有了：" + path)
    else:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(TEMPLATE.format(title=title))
        print("已建立：" + path)
    subprocess.Popen(["notepad.exe", path])


if __name__ == "__main__":
    main()
