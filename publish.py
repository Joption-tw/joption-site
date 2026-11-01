"""把改好的內容送到 GitHub，網站會自動更新。

    python publish.py
"""
import subprocess, sys

from build import ROOT, build


def git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True, encoding="utf-8", errors="replace")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    problems = build()
    if problems:
        print("\n上面有「注意」的項目，請先修好再發布。")
        return 1
    git("add", "-A")
    if git("diff", "--cached", "--quiet").returncode:
        done = git("commit", "-q", "-m", "Update site content")
        if done.returncode:
            print(done.stdout + done.stderr)
            print("\n發布失敗，網站沒有更新。請把這個畫面截圖給 Claude。")
            return 1
    elif git("status", "-sb").stdout.find("ahead") < 0:
        print("\n沒有新的變更，不用發布。")
        return 0
    done = git("push", "-q", "origin", "main")
    if done.returncode:
        print(done.stdout + done.stderr)
        print("\n發布失敗，網站沒有更新。請把這個畫面截圖給 Claude。")
        return 1
    print("\n已送出，約 1 分鐘後更新：https://joption-tw.github.io/joption-site/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
