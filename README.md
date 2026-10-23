# iThome 鐵人賽作品查詢

👉 https://ironman.antonio-ling.com

每年鐵人賽結束，我都想回頭找「某個主題有哪些人寫得不錯」。但 iThome 官網一次只能看一屆，得獎名單跟系列文章又分在不同頁面，翻起來很累。所以乾脆自己做一個，把 2022 到 2026 這五屆的系列、團隊和得獎名單都放在一起。

## 可以拿來做什麼

- **跨年度找系列**：搜尋系列標題、作者，連**每一天的文章標題**都搜得到。例如搜「Signal」，就算只有 Day 12 提到，也會把那個系列找出來，還會告訴你是哪一篇。
- **得獎的排前面**：冠軍 → 優選 → 佳作 → 佛心分享推薦，好東西不用自己挖。
- **依主題逛**：iThome 每年的組別名稱都不太一樣，我把它們整理成 AI、前端與 Web、軟體開發、雲端與維運等十個主題，每個主題都有自己的顏色。
- **先看大綱再決定要不要點**：點任一個系列，會從側邊滑出 30 天的文章標題，每篇都能直接點過去看。
- **點作者看他歷年所有作品**：會顯示 iThome 頭像、參賽幾次、得過幾次獎。
- **團隊**：看每屆有哪些隊伍、成員各寫了什麼，最佳團隊獎和眾志成城也會標出來。
- **每年的得獎主題**：單獨一個分頁，可以依獎項或依組別看。
- **我的最愛**：按愛心收藏，資料只存在你自己的瀏覽器（localStorage），換台電腦就不見了。
- 卡片跟列表兩種顯示方式都有，深色模式會跟著系統切換。

## 資料是怎麼來的

全部都是從 iThome 鐵人賽官網公開的頁面抓的：

| 資料 | 來源 |
| --- | --- |
| 系列、作者、頭像 | 每屆的報名列表 `/{年}ironman/signup/list` |
| 團隊 | 團隊列表 `/{年}ironman/signup/team_list` |
| 得獎名單 | `/{年}ironman/reward`（個人）、`/{年}ironman/reward_team`（團體） |
| 每日文章標題 | 每個系列的 RSS `/rss/series/{系列 ID}` |

有幾件事要先知道：

- **賽季結束後，iThome 的報名列表只會留下完賽或達標的系列**，所以中途放棄的系列在這裡是看不到的。
- 2026 的得獎名單還沒公布，通常是 11～12 月，公布後重抓一次就會出現。
- 爬蟲每次請求都會停 0.6 秒，不要對 iThome 造成負擔。改這個數字之前請三思 🙏

## 本機跑起來

需要 Node.js 24 以上、pnpm，還有 Python 3.9 以上（只有爬資料時才用到）。

```bash
pnpm install
pnpm dev        # 開在 http://localhost:3000
```

資料已經放在 `public/data/` 裡了，不用先爬也能直接跑。

## 更新資料

```bash
pnpm scrape
```

這個指令會依序做三件事：

1. `scripts/scrape.py`：抓報名列表、團隊、得獎名單，輸出 `public/data/ironman.json`。大概 5～6 分鐘。
2. `scripts/scrape_outlines.py`：抓每個系列的每日文章標題，輸出 `public/data/outline/{系列 ID}.json`。**已經抓過的會跳過**，所以第一次要 40 分鐘左右，之後只會補新的。
3. `scripts/build_search.py`：把文章標題整理成搜尋用的索引 `public/data/articles-{年}.json`。

還在進行中的那一屆，文章會一直增加，可以強制重抓：

```bash
python3 scripts/scrape_outlines.py --refresh 2026
python3 scripts/build_search.py
```

想抓別的年份範圍的話：`python3 scripts/scrape.py 2021 2025`。

## 部署

部署在 Cloudflare Workers（靜態資源），網域是 `ironman.antonio-ling.com`，設定都寫在 `wrangler.jsonc`。

```bash
pnpm run deploy   # = nuxt generate && wrangler deploy
```

第一次部署前要先 `npx wrangler login`。

如果要換網域，記得一起改這三個地方：`wrangler.jsonc` 的 `routes`、`nuxt.config.ts` 的 `siteUrl`（也可以用環境變數 `NUXT_PUBLIC_SITE_URL`），以及 `public/robots.txt`、`public/sitemap.xml`。

## 專案裡有什麼

```
app/
  pages/index.vue          唯一的一頁：搜尋、篩選、主題分區、清單
  components/              卡片、列表、大綱面板、作者頁頭、得獎主題…
  composables/
    useIronman.ts          載入資料、把獎項跟團隊掛到系列上
    useArticles.ts         文章標題索引、單一系列的大綱
    useFavorites.ts        我的最愛（localStorage）
    themes.ts              組別 → 主題的對照表
  assets/css/main.css      色票、字型、共用樣式
public/
  data/                    爬下來的資料
  fonts/                   自己架的字型子集
  _headers                 快取設定
scripts/                   三支爬蟲／整理資料的 Python
```

### 新的一屆出現新組別怎麼辦？

打開 `app/composables/themes.ts`，把新組別名稱加到對應主題的 `groups` 裡就好。沒加的話也不會漏，會先歸到「其他」。

## 幾個做法上的小決定

- **資料不打包進 JS**：五年的資料大約 1.2 MB，放在 `public/data/` 讓瀏覽器自己抓，比塞進 JS 裡解析快很多。
- **首頁先畫好再說**：預設畫面（依主題分區的 60 張卡片）在 build 的時候就寫進 HTML 了，手機上不用等資料下載完才看到東西。
- **文章標題索引很大，所以晚點才載**：全部大概 4 MB，按年度拆成五個檔，你第一次點搜尋框時才從最新的一年開始載，載完一年就能搜那一年。
- **字型很省**：內文用系統字型（蘋方、微軟正黑），只有網站名稱用霞鶩文楷，而且只放那幾個字，三個字型檔加起來不到 50 KB。

## 致謝

靈感來自 [鐵人觀察家 Next](https://ithome-ironman-observer.happyhacking.ninja/)，它追蹤的是當屆每天的進度，這裡則是把歷屆的作品整理起來方便回頭找。

資料版權屬於 iThome 與各位鐵人作者，這個網站只做整理和連結，文章請到 iT 邦幫忙看原文。
