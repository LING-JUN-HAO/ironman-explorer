#!/usr/bin/env python3
"""抓 iThome 鐵人賽近五年的系列、團隊與得獎名單，輸出 data/ironman.json。

用法：python3 scripts/scrape.py [起始年 結束年]，預設為今年往回五屆。
"""
from __future__ import annotations

import datetime
import html
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

BASE = "https://ithelp.ithome.com.tw"
UA = "Mozilla/5.0 (ironman-explorer)"
DELAY = 0.6  # 每次請求間隔，避免對 iThome 造成負擔
DESC_LIMIT = 120  # 卡片只顯示兩行簡介，截短以控制資料大小
OUT = Path(__file__).resolve().parent.parent / "public" / "data" / "ironman.json"

# 個人組得獎頁以 winner/flag-wreath[-N].svg 區隔獎項；團體組以 winner-group-* 區隔
PERSONAL_TIERS = {"": "冠軍", "-2": "優選", "-3": "佳作", "-4": "佛心分享推薦"}
TEAM_TIERS = {"best": "最佳團隊獎", "more": "眾志成城"}


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
            print(f"  ! {url} 失敗（{err}），{wait}s 後重試", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"無法取得 {url}")


def clean(s: str | None) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def short(s: str) -> str:
    return s if len(s) <= DESC_LIMIT else s[:DESC_LIMIT] + "…"


def paginate(url: str, splitter: str):
    page = 1
    while True:
        body = fetch(f"{url}?page={page}")
        blocks = body.split(splitter)[1:]
        if not blocks:
            return
        print(f"  {url} p{page}: {len(blocks)}")
        yield from blocks
        page += 1


def scrape_series(year: int) -> list[dict]:
    series = {}
    for b in paginate(f"{BASE}/{year}ironman/signup/list", '<div class="list-card">'):
        m = re.search(r"/users/(\d+)/ironman/(\d+)", b)
        if not m:
            continue
        day = re.search(r"team-dashboard__day[^>]*>\s*DAY\s*(\d+)", b)
        series[int(m.group(2))] = {
            "id": int(m.group(2)),
            "userId": int(m.group(1)),
            "name": clean(re.search(r'contestants-list__name">([^<]+)', b).group(1)),
            "group": clean((re.search(r'<div class="tag">[\s\S]*?<span>([^<]+)</span>', b) or [None, ""])[1]),
            "title": clean((re.search(r'contestants-list__title title">([^<]+)', b) or [None, ""])[1]),
            "desc": short(clean((re.search(r'contestants-list__desc content">([\s\S]*?)</p>', b) or [None, ""])[1])),
            "day": int(day.group(1)) if day else 0,
            # 頭像 ID 跟使用者 ID 不同，網址為 member.ithome.com.tw/avatars/{avatar}
            "avatar": int(avatar.group(1)) if (avatar := re.search(r"/avatars/(\d+)", b)) else None,
        }
    return list(series.values())


def scrape_teams(year: int) -> list[dict]:
    teams = {}
    for b in paginate(f"{BASE}/{year}ironman/signup/team_list", '<div class="list-card team-info-card">'):
        m = re.search(r'/signup/team/(\d+)">([^<]+)</a>', b)
        if not m:
            continue
        leader = re.search(r'team-leader">[\s\S]*?/users/(\d+)/ironman', b)
        members = [int(u) for u in re.findall(r'href="https://ithelp\.ithome\.com\.tw/users/(\d+)/ironman"', b)]
        teams[int(m.group(1))] = {
            "id": int(m.group(1)),
            "name": clean(m.group(2)),
            "intro": short(clean((re.search(r'content-full">([\s\S]*?)</div>', b) or [None, ""])[1])),
            "status": clean((re.search(r'fg-tag">([^<]+)', b) or [None, ""])[1]),
            "leaderId": int(leader.group(1)) if leader else None,
            "memberIds": list(dict.fromkeys(members)),
        }
    return list(teams.values())


def scrape_personal_awards(year: int) -> list[dict]:
    body = fetch(f"{BASE}/{year}ironman/reward")
    body = body.split("sec_reaward", 1)[-1]
    awards, tier = [], None
    for tok in re.finditer(r'winner/flag-wreath(-\d)?\.svg|winner-item__body([\s\S]*?)winner-item__topic">([^<]*)', body):
        if tok.group(0).startswith("winner/flag-wreath"):
            tier = PERSONAL_TIERS.get(tok.group(1) or "", "其他")
            continue
        chunk = tok.group(2)
        m = re.search(r"/users/(\d+)/ironman/(\d+)", chunk)
        if not m:
            continue
        awards.append({
            "seriesId": int(m.group(2)),
            "userId": int(m.group(1)),
            "tier": tier,
            "name": clean((re.search(r'winner-item__name">([^<]*)', chunk) or [None, ""])[1]),
            "group": clean((re.search(r'winner-item__group">([^<]*)', chunk) or [None, ""])[1]),
            "title": clean(tok.group(3)),
        })
    return awards


def scrape_team_awards(year: int) -> list[dict]:
    body = fetch(f"{BASE}/{year}ironman/reward_team")
    awards = []
    for part in re.split(r'class="winner-wrapper winner-group-', body)[1:]:
        kind = part.split('"', 1)[0]
        if kind not in TEAM_TIERS:
            continue
        for card in re.split(r'class="(?:list|reward)-card"', part)[1:]:
            name = re.search(r'class="team-name">([^<]+)', card)
            if not name:
                continue
            awards.append({
                "tier": TEAM_TIERS[kind],
                "name": clean(name.group(1)),
                "seriesIds": [int(s) for s in re.findall(r"/users/\d+/ironman/(\d+)", card)],
            })
    return awards


def main():
    this_year = datetime.date.today().year
    start, end = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) == 3 else (this_year - 4, this_year)
    years = {}
    for year in range(end, start - 1, -1):
        print(f"== {year}")
        years[year] = {
            "series": scrape_series(year),
            "teams": scrape_teams(year),
            "personalAwards": scrape_personal_awards(year),
            "teamAwards": scrape_team_awards(year),
        }
        y = years[year]
        print(f"  系列 {len(y['series'])}、團隊 {len(y['teams'])}、個人獎 {len(y['personalAwards'])}、團體獎 {len(y['teamAwards'])}")
    OUT.write_text(json.dumps({
        "updatedAt": datetime.datetime.now().isoformat(timespec="minutes"),
        "years": years,
    }, ensure_ascii=False, separators=(",", ":")))
    print(f"寫出 {OUT}（{OUT.stat().st_size // 1024} KB）")


if __name__ == "__main__":
    main()
