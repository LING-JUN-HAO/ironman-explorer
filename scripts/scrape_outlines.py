#!/usr/bin/env python3
"""抓每個系列的文章標題大綱（來源：系列 RSS），輸出 public/data/outline/{seriesId}.json。

需先跑過 scrape.py。已存在的檔案會跳過，所以可以中斷後續跑；
加上 --refresh 年份（例如 --refresh 2026）可強制重抓還在更新的那一屆。
"""
from __future__ import annotations

import html
import json
import re
import sys
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "public" / "data" / "ironman.json"
OUT = ROOT / "public" / "data" / "outline"
UA = "Mozilla/5.0 (ironman-explorer)"
WORKERS = 2  # 同時請求數，保持對 iThome 友善
DELAY = 0.6

lock = threading.Lock()
done = 0


def fetch(url: str) -> str:
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as res:
                body = res.read().decode("utf-8", "replace")
            time.sleep(DELAY)
            return body
        except Exception as err:  # noqa: BLE001
            wait = 2 ** attempt * 3
            print(f"  ! {url} 失敗（{err}），{wait}s 後重試", file=sys.stderr, flush=True)
            time.sleep(wait)
    raise RuntimeError(f"無法取得 {url}")


def text(s: str) -> str:
    s = re.sub(r"^<!\[CDATA\[|\]\]>$", "", s.strip())
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def parse_rss(xml: str) -> list[dict]:
    articles = []
    for item in re.findall(r"<item>([\s\S]*?)</item>", xml):
        link = re.search(r"/articles/(\d+)", item)
        title = re.search(r"<title>([\s\S]*?)</title>", item)
        date = re.search(r"<pubDate>([^<]+)</pubDate>", item)
        if not (link and title):
            continue
        articles.append({
            "id": int(link.group(1)),
            "title": text(title.group(1)),
            "date": date.group(1).strip()[:10] if date else "",  # iThome 給的是 "2026-09-09 06:05:54"
        })
    # RSS 由新到舊，大綱要照 Day 1 → Day 30 的順序
    return sorted(articles, key=lambda a: a["id"])


def work(series_id: int, total: int):
    global done
    path = OUT / f"{series_id}.json"
    try:
        articles = parse_rss(fetch(f"https://ithelp.ithome.com.tw/rss/series/{series_id}"))
        path.write_text(json.dumps(articles, ensure_ascii=False, separators=(",", ":")))
    except Exception as err:  # noqa: BLE001
        print(f"  ! 系列 {series_id} 略過：{err}", file=sys.stderr, flush=True)
    with lock:
        done += 1
        if done % 100 == 0 or done == total:
            print(f"  {done}/{total}", flush=True)


def main():
    refresh = {int(y) for y in sys.argv[sys.argv.index("--refresh") + 1:]} if "--refresh" in sys.argv else set()
    OUT.mkdir(parents=True, exist_ok=True)
    data = json.loads(DATA.read_text())
    todo = [
        s["id"]
        for year, y in data["years"].items()
        for s in y["series"]
        if int(year) in refresh or not (OUT / f"{s['id']}.json").exists()
    ]
    print(f"要抓 {len(todo)} 個系列", flush=True)
    with ThreadPoolExecutor(WORKERS) as pool:
        for sid in todo:
            pool.submit(work, sid, len(todo))


if __name__ == "__main__":
    main()
