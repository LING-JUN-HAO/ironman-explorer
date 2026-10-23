#!/usr/bin/env python3
"""把 public/data/outline/*.json 的文章標題合併成搜尋索引 public/data/articles-{年度}.json。

格式：{ 系列ID: [文章標題, ...] }。前端第一次搜尋時才載入，依年度由新到舊逐檔載入。
為了縮小檔案，索引裡的標題會拿掉重複的系列名稱與「Day 09」「第 9 天」這類編號
（大綱面板顯示的仍是完整標題）。
"""
import json
import re
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "public" / "data"

DAY = re.compile(r"[\[【(（]?\s*(?:day|DAY|Day)\s*[-_.]?\s*\d+\s*[\]】)）]?|第\s*\d+\s*[天篇日]")
EDGE = re.compile(r"^[\s:：\-–—|｜,，.。/、]+|[\s:：\-–—|｜,，.。/、]+$")
EMPTY_BRACKETS = re.compile(r"[\[【(（]\s*[\]】)）]")


def squeeze(title: str, series_title: str) -> str:
    t = title.replace(series_title, " ") if len(series_title) >= 4 else title
    t = EMPTY_BRACKETS.sub(" ", DAY.sub(" ", t))
    t = EDGE.sub("", re.sub(r"\s+", " ", t))
    return t or title


years = json.loads((DATA / "ironman.json").read_text())["years"]
(DATA / "articles.json").unlink(missing_ok=True)  # 舊版的單一索引檔

for year, y in years.items():
    index = {}
    for s in y["series"]:
        path = DATA / "outline" / f"{s['id']}.json"
        if path.exists():
            index[s["id"]] = [squeeze(a["title"], s["title"]) for a in json.loads(path.read_text())]
    out = DATA / f"articles-{year}.json"
    out.write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")))
    print(f"寫出 {out.name}（{len(index)}/{len(y['series'])} 個系列，{out.stat().st_size // 1024} KB）")
