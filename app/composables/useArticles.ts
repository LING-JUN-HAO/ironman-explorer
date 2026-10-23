export type Article = { id: number, title: string, date: string }

export const articleUrl = (id: number) => `https://ithelp.ithome.com.tw/articles/${id}`

// ── 文章標題索引：每個系列的每日標題，供搜尋用。檔案較大，第一次搜尋時才載入，
//    依年度由新到舊逐檔載入，載完一年就能搜那一年 ──
const index = shallowRef(new Map<number, string[]>())
const pending = ref(0)
let started = false

export function useArticleIndex() {
  function load(years: number[]) {
    if (!import.meta.client || started || !years.length) return
    started = true
    pending.value = years.length
    years.reduce((chain, year) => chain
      .then(() => $fetch<Record<string, string[]>>(`/data/articles-${year}.json`))
      .then((raw) => {
        const next = new Map(index.value)
        for (const [id, titles] of Object.entries(raw)) next.set(Number(id), titles)
        index.value = next
      })
      .catch(() => {})
      .finally(() => { pending.value-- }), Promise.resolve())
  }
  return { index, loading: computed(() => pending.value > 0), load }
}

// ── 單一系列的大綱：打開面板時才抓，抓過的留在記憶體 ──
const outlines = new Map<number, Promise<Article[]>>()

export function fetchOutline(seriesId: number): Promise<Article[]> {
  if (!outlines.has(seriesId)) {
    const p = $fetch<Article[]>(`/data/outline/${seriesId}.json`).catch((err) => {
      outlines.delete(seriesId)
      throw err
    })
    outlines.set(seriesId, p)
  }
  return outlines.get(seriesId)!
}
