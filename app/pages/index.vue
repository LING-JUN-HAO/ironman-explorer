<script setup lang="ts">
import { PERSONAL_TIERS, TEAM_TIERS, buildIronman, compareSeries, type Raw, type Series, type Team } from '~/composables/useIronman'
import { THEMES, themeById, type ThemeId } from '~/composables/themes'

const PAGE = 36
/** 依主題瀏覽時，每個主題先列幾個 */
const PER_THEME = 6
const { data, error } = useIronman()
const { index: articleIndex, loading: articlesLoading, load: loadIndex } = useArticleIndex()
const loadArticles = () => data.value && loadIndex(data.value.years)
const fav = useFavorites()
onMounted(fav.load)

// ── 網址狀態：分頁、年度、主題、搜尋字都寫進網址，方便分享搜尋結果 ──
type Tab = 'series' | 'teams' | 'awards'
const route = useRoute()
const router = useRouter()
const setQuery = (patch: Record<string, string | undefined>) => router.replace({ query: { ...route.query, ...patch } })

const tab = computed<Tab>({
  get: () => (route.query.tab === 'teams' || route.query.tab === 'awards' ? route.query.tab : 'series'),
  set: v => setQuery({ tab: v === 'series' ? undefined : v }),
})
const pickedYears = computed<number[]>({
  get: () => String(route.query.y ?? '').split(',').map(Number).filter(Boolean),
  set: v => setQuery({ y: v.length ? [...v].sort((a, b) => b - a).join(',') : undefined }),
})
const theme = computed<ThemeId | ''>({
  get: () => (THEMES.some(t => t.id === route.query.t) ? (route.query.t as ThemeId) : ''),
  set: v => setQuery({ t: v || undefined }),
})
const awardYear = computed<number>({
  get: () => {
    const y = Number(route.query.ay)
    return data.value?.years.includes(y) ? y : (data.value?.latestAwardedYear ?? 0)
  },
  set: v => setQuery({ ay: String(v) }),
})

// 作者（u）與打開大綱的系列（s）也放網址，點作者、看大綱都能直接分享
const author = computed<number | null>(() => Number(route.query.u) || null)
const openId = computed<number | null>({
  get: () => Number(route.query.s) || null,
  set: v => setQuery({ s: v ? String(v) : undefined }),
})
const openSeries = computed(() => (openId.value ? data.value?.series.find(s => s.id === openId.value) ?? null : null))
const authorName = computed(() => (author.value ? data.value?.series.find(s => s.userId === author.value)?.name ?? '' : ''))

const q = ref(String(route.query.q ?? ''))
let qTimer: ReturnType<typeof setTimeout> | undefined
watch(q, (v) => {
  clearTimeout(qTimer)
  qTimer = setTimeout(() => setQuery({ q: v.trim() || undefined }), 300)
})
const onlyWon = ref(false)
const onlyFav = ref(false)
const shown = ref(PAGE)
const sheetOpen = ref(false)

// 顯示方式：卡片或列表，記在這台裝置
const VIEW_KEY = 'ironman-explorer:view'
const view = ref<'card' | 'list'>('card')
onMounted(() => {
  try { if (localStorage.getItem(VIEW_KEY) === 'list') view.value = 'list' }
  catch { /* 無痕模式讀不到就用預設 */ }
})
function setView(v: 'card' | 'list') {
  view.value = v
  try { localStorage.setItem(VIEW_KEY, v) }
  catch { /* 只在本次瀏覽生效 */ }
}

// 預設畫面（依主題瀏覽）在 build 時就寫進 HTML，不用等整份資料下載完才畫得出來
type Section = { id: ThemeId, total: number, wins: number, items: Series[] }
function toSections(series: Series[]): Section[] {
  const byTheme = Map.groupBy(series, s => s.theme)
  return THEMES.map((t) => {
    const list = (byTheme.get(t.id) ?? []).toSorted(compareSeries)
    return { id: t.id, total: list.length, wins: list.filter(s => s.tier).length, items: list.slice(0, PER_THEME) }
  }).filter(sec => sec.total)
}
const { data: initialSections } = await useAsyncData('initial-sections', async () => {
  if (!import.meta.server) return []
  const { readFile } = await import('node:fs/promises')
  const raw = JSON.parse(await readFile('public/data/ironman.json', 'utf8')) as Raw
  return toSections(buildIronman(raw).series)
}, { default: () => [] as Section[] })

watch([tab, pickedYears, theme, q, onlyWon, onlyFav, author], () => { shown.value = PAGE })
// 有搜尋字才需要文章標題索引
watch([q, data], ([v]) => { if (v.trim()) loadArticles() }, { immediate: true })

// 點作者前先記住當下的條件，看完可以回到剛才的結果（按鈕或瀏覽器上一頁都行）
type Snapshot = { query: typeof route.query, q: string, onlyWon: boolean, onlyFav: boolean }
const beforeAuthor = shallowRef<Snapshot | null>(null)

/** 點作者：跨年度列出他的所有系列 */
function showAuthor(userId: number) {
  if (!author.value) {
    beforeAuthor.value = { query: { ...route.query, s: undefined }, q: q.value, onlyWon: onlyWon.value, onlyFav: onlyFav.value }
  }
  clearTimeout(qTimer)
  q.value = ''
  onlyWon.value = false
  onlyFav.value = false
  sheetOpen.value = false
  router.push({ query: { u: String(userId) } })
  window.scrollTo({ top: 0 })
}

// 離開作者頁（按鈕或上一頁）時還原搜尋字與只看得獎／最愛
watch(author, (now, before) => {
  if (!before || now || !beforeAuthor.value) return
  const prev = beforeAuthor.value
  beforeAuthor.value = null
  q.value = prev.q
  onlyWon.value = prev.onlyWon
  onlyFav.value = prev.onlyFav
})
/** 點網站名稱：清掉所有條件回到首頁 */
function goHome() {
  clearTimeout(qTimer)
  q.value = ''
  onlyWon.value = false
  onlyFav.value = false
  sheetOpen.value = false
  router.replace({ query: {} })
  window.scrollTo({ top: 0 })
}
function leaveAuthor() {
  router.push({ query: beforeAuthor.value?.query ?? {} })
}
watch(tab, () => { sheetOpen.value = false; window.scrollTo({ top: 0 }) })

function toggleYear(y: number) {
  pickedYears.value = pickedYears.value.includes(y) ? pickedYears.value.filter(x => x !== y) : [...pickedYears.value, y]
}
function clearFilters() {
  setQuery({ y: undefined, t: undefined })
  onlyWon.value = false
  onlyFav.value = false
}
const activeFilters = computed(() => pickedYears.value.length + Number(!!theme.value) + Number(onlyWon.value) + Number(onlyFav.value))

// ── 搜尋：每個詞都要出現。命中位置依序為系列標題、某一篇文章標題、簡介、作者／團隊 ──
const tokens = computed(() => q.value.toLowerCase().split(/\s+/).filter(Boolean))
const hasAll = (text: string) => { const t = text.toLowerCase(); return tokens.value.every(tok => t.includes(tok)) }

type Hit = { s: Series, hit: number, note: string | null }
function hitOf(s: Series): Hit | null {
  if (!tokens.value.length || hasAll(s.title)) return { s, hit: 0, note: null }
  const article = articleIndex.value.get(s.id)?.find(hasAll)
  if (article) return { s, hit: 1, note: `文章：${article}` }
  if (hasAll(`${s.title} ${s.desc}`)) return { s, hit: 2, note: '簡介提到' }
  if (hasAll(`${s.name} ${s.team ?? ''} ${s.group}`) || hasAll(`${s.title} ${s.desc} ${s.name} ${s.team ?? ''} ${s.group}`)) {
    return { s, hit: 3, note: hasAll(s.name) ? null : '作者／團隊符合' }
  }
  return null
}

const inYears = (y: number) => !pickedYears.value.length || pickedYears.value.includes(y)

// 排序：獎項 → 命中位置（標題優先）→ 年度新到舊 → 完成天數
// 沒選主題、沒搜尋時改成依主題分區瀏覽，每區列最值得看的幾個，避免全部都是各年冠軍擠在一起
const browseByTheme = computed(() => tab.value === 'series' && !theme.value && !q.value.trim() && !author.value && !onlyFav.value)
const sections = computed<Section[]>(() => {
  if (!data.value) return pickedYears.value.length || onlyWon.value ? [] : initialSections.value
  return toSections(data.value.series.filter(s => inYears(s.year) && (!onlyWon.value || s.tier)))
})
function openTheme(id: ThemeId) {
  theme.value = id
  window.scrollTo({ top: 0 })
}

const seriesList = computed<Hit[]>(() => {
  if (!data.value) return []
  return data.value.series
    .filter(s => inYears(s.year)
      && (!author.value || s.userId === author.value)
      && (!theme.value || s.theme === theme.value)
      && (!onlyWon.value || s.tier)
      && (!onlyFav.value || fav.has(favKey('s', s.year, s.id))))
    .map(hitOf)
    .filter((r): r is Hit => r !== null)
    .sort((a, b) => tierRank(PERSONAL_TIERS, a.s.tier) - tierRank(PERSONAL_TIERS, b.s.tier)
      || a.hit - b.hit || b.s.year - a.s.year || b.s.day - a.s.day || a.s.id - b.s.id)
})

// 排序：團體獎 → 成員得獎數 → 年度新到舊 → 系列數
const teamList = computed<Team[]>(() => {
  if (!data.value) return []
  return data.value.teams
    .filter(t => inYears(t.year)
      && (!author.value || t.members.some(m => m.userId === author.value))
      && (!theme.value || t.members.some(m => m.theme === theme.value))
      && (!onlyWon.value || t.tier || t.wins)
      && (!onlyFav.value || fav.has(favKey('t', t.year, t.id)))
      && (!tokens.value.length || hasAll(`${t.name} ${t.intro} ${t.members.map(m => `${m.name} ${m.title}`).join(' ')}`)))
    .sort((a, b) => tierRank(TEAM_TIERS, a.tier) - tierRank(TEAM_TIERS, b.tier)
      || b.wins - a.wins || b.year - a.year || b.members.length - a.members.length || a.id - b.id)
})

const authorWorks = computed(() => (author.value ? data.value?.series.filter(s => s.userId === author.value) ?? [] : []))

const total = computed(() => (tab.value === 'teams' ? teamList.value.length : seriesList.value.length))
const wonCount = computed(() => (tab.value === 'teams'
  ? teamList.value.filter(t => t.tier || t.wins).length
  : seriesList.value.filter(r => r.s.tier).length))

// 主題 chip 上的數字：只套用年度條件，讓人知道每個主題有多少可看
const themeCounts = computed(() => {
  const counts = new Map<string, number>()
  for (const s of data.value?.series ?? []) {
    if (inYears(s.year)) counts.set(s.theme, (counts.get(s.theme) ?? 0) + 1)
  }
  return counts
})

// 清單標題寫成完整的一句話，例如「全部年度的系列」「2025 年的團隊（主題：AI）」
const listTitle = computed(() => {
  const kind = tab.value === 'teams' ? '團隊' : '系列'
  if (author.value) return tab.value === 'teams' ? `${authorName.value} 參加過的團隊` : `${authorName.value} 的所有作品`
  const ys = pickedYears.value
  const years = ys.length ? `${ys.join('、')} 年` : '全部年度'
  const t = THEMES.find(x => x.id === theme.value)?.label
  if (browseByTheme.value) return `${years}的系列，依主題`
  return `${years}的${kind}${t ? `（主題：${t}）` : ''}`
})
</script>

<template>
  <div>
    <header class="site-head">
      <div class="wrap head-row">
        <div class="brand">
          <h1><a href="/" class="home" @click.prevent="goHome">iThome 鐵人賽<b>作品查詢</b></a></h1>
          <small v-if="data">{{ data.years.at(-1) }}–{{ data.years[0] }}</small>
        </div>

        <div v-if="tab !== 'awards'" class="search-wrap">
          <label class="search" for="q">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" /></svg>
            <input id="q" v-model="q" type="search" :placeholder="tab === 'teams' ? '搜尋團隊、成員或系列標題' : '搜尋系列、文章標題或作者'" autocomplete="off" enterkeyhint="search" @focus="loadArticles">
            <button v-if="q" type="button" class="clear" aria-label="清除搜尋" @click="q = ''">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M7 7l10 10M17 7 7 17" /></svg>
            </button>
          </label>
          <button v-if="!author" type="button" class="filter-btn" :aria-expanded="sheetOpen" aria-controls="filters" @click="sheetOpen = true">
            篩選<span v-if="activeFilters" class="dot">{{ activeFilters }}</span>
          </button>
        </div>

        <nav class="tabs" aria-label="檢視">
          <button type="button" :aria-pressed="tab === 'series'" @click="tab = 'series'">系列</button>
          <button type="button" :aria-pressed="tab === 'teams'" @click="tab = 'teams'">團隊</button>
          <button type="button" :aria-pressed="tab === 'awards'" @click="tab = 'awards'">得獎主題</button>
        </nav>
      </div>
    </header>

    <main class="wrap">
      <p v-if="error" class="empty">{{ error }}</p>

      <template v-else-if="tab === 'awards'">
        <div v-if="data" class="chips" role="group" aria-label="得獎年度">
          <button v-for="y in data.years" :key="y" type="button" class="chip" :aria-pressed="y === awardYear" @click="awardYear = y">{{ y }}</button>
        </div>
        <AwardTopics v-if="data" :year="awardYear" :data="data.db[awardYear]!" />
      </template>

      <template v-else>
        <div v-if="!author" id="filters" class="filters" :class="{ open: sheetOpen }" role="region" aria-label="篩選條件">
          <div class="sheet-head">
            <strong>篩選</strong>
            <button type="button" class="link" @click="clearFilters">清除</button>
            <button type="button" class="done" @click="sheetOpen = false">完成</button>
          </div>
          <div class="frow">
            <span class="flabel">主題</span>
            <div class="chips">
              <button type="button" class="chip" :aria-pressed="!theme" @click="theme = ''">全部</button>
              <button
                v-for="t in THEMES"
                :key="t.id"
                type="button"
                class="chip theme-chip theme-tint"
                :class="{ neutral: t.id === 'other' }"
                :style="{ '--hue': t.hue }"
                :aria-pressed="theme === t.id"
                @click="theme = theme === t.id ? '' : t.id"
              >
                {{ t.label }}<span class="n">{{ themeCounts.get(t.id) ?? 0 }}</span>
              </button>
            </div>
          </div>
          <div class="frow">
            <span class="flabel">年度</span>
            <div class="chips">
              <button type="button" class="chip" :aria-pressed="!pickedYears.length" @click="pickedYears = []">全部</button>
              <button v-for="y in data?.years ?? []" :key="y" type="button" class="chip" :aria-pressed="pickedYears.includes(y)" @click="toggleYear(y)">{{ y }}</button>
              <span class="divider" aria-hidden="true" />
              <button type="button" class="chip" :aria-pressed="onlyWon" @click="onlyWon = !onlyWon">只看得獎</button>
              <button type="button" class="chip" :aria-pressed="onlyFav" @click="onlyFav = !onlyFav">我的最愛<span class="n">{{ fav.count.value }}</span></button>
            </div>
          </div>
        </div>
        <div v-if="sheetOpen" class="backdrop" aria-hidden="true" @click="sheetOpen = false" />

        <section aria-labelledby="list-title">
          <div class="list-head">
            <AuthorHeader v-if="author && authorWorks.length" :user-id="author" :works="authorWorks" :back-label="beforeAuthor ? '回到剛才的結果' : '回到全部作品'" @back="leaveAuthor" />
            <h2 v-else id="list-title" class="sec">{{ listTitle }}</h2>
            <div class="list-tools">
              <span v-if="data" class="meta"><template v-if="q.trim()">符合「{{ q.trim() }}」</template>{{ total }} 筆 · 得獎 {{ wonCount }}<template v-if="q.trim() && articlesLoading"> · 文章標題載入中</template></span>
              <div class="seg" role="group" aria-label="顯示方式">
                <button type="button" :aria-pressed="view === 'card'" @click="setView('card')">卡片</button>
                <button type="button" :aria-pressed="view === 'list'" @click="setView('list')">列表</button>
              </div>
            </div>
          </div>

          <!-- 依主題分區 -->
          <template v-if="browseByTheme && sections.length">
            <section
              v-for="sec in sections"
              :key="sec.id"
              class="theme-sec theme-tint"
              :class="{ neutral: sec.id === 'other' }"
              :style="{ '--hue': themeById.get(sec.id)!.hue }"
              :aria-labelledby="`sec-${sec.id}`"
            >
              <div class="theme-head">
                <h3 :id="`sec-${sec.id}`">{{ themeById.get(sec.id)!.label }}</h3>
                <span class="theme-meta">{{ sec.total }} 個系列<template v-if="sec.wins"> · 得獎 {{ sec.wins }}</template></span>
                <button type="button" class="see-all" @click="openTheme(sec.id)">看全部 {{ sec.total }} 個 →</button>
              </div>
              <ul v-if="view === 'list'" class="rows">
                <SeriesRow v-for="item in sec.items" :key="item.id" :series="item" @outline="openId = $event.id" @author="showAuthor" />
              </ul>
              <div v-else class="cards">
                <SeriesCard v-for="item in sec.items" :key="item.id" :series="item" @outline="openId = $event.id" @author="showAuthor" />
              </div>
            </section>
          </template>

          <div v-else-if="!data" class="cards">
            <div v-for="i in 6" :key="i" class="card skeleton" aria-hidden="true" />
          </div>

          <ul v-else-if="view === 'list'" class="rows">
            <template v-if="tab === 'series'">
              <SeriesRow
                v-for="r in seriesList.slice(0, shown)"
                :key="`${r.s.year}-${r.s.id}`"
                :series="r.s"
                :hint="r.note"
                @outline="openId = $event.id"
                @author="showAuthor"
              />
            </template>
            <template v-else>
              <TeamRow v-for="t in teamList.slice(0, shown)" :key="`${t.year}-${t.id}`" :team="t" @author="showAuthor" />
            </template>
            <li v-if="!total" class="empty">沒有符合條件的項目，試著換個關鍵字或清除篩選。</li>
          </ul>

          <div v-else class="cards">
            <template v-if="tab === 'series'">
              <SeriesCard
                v-for="r in seriesList.slice(0, shown)"
                :key="`${r.s.year}-${r.s.id}`"
                :series="r.s"
                :hint="r.note"
                @outline="openId = $event.id"
                @author="showAuthor"
              />
            </template>
            <template v-else>
              <TeamCard
                v-for="t in teamList.slice(0, shown)"
                :key="`${t.year}-${t.id}`"
                :team="t"
                @outline="openId = $event.id"
                @author="showAuthor"
              />
            </template>
            <div v-if="!total" class="empty">
              <template v-if="onlyFav && !fav.count.value">還沒有加入最愛。點卡片右上角的愛心就會收進這裡，資料只存在這台裝置的瀏覽器。</template>
              <template v-else>沒有符合條件的項目，試著換個關鍵字或清除篩選。</template>
            </div>
          </div>

          <div v-if="!browseByTheme && total > shown" class="more">
            <button type="button" @click="shown += PAGE">
              再顯示 {{ Math.min(PAGE, total - shown) }} 筆（剩 {{ total - shown }}）
            </button>
          </div>
        </section>
      </template>
    </main>

    <OutlinePanel v-if="openSeries" :series="openSeries" @close="openId = null" @author="showAuthor" />

    <footer v-if="data" class="wrap foot">
      資料來源：iThome 鐵人賽報名列表、團隊列表與得獎名單，抓取時間 {{ data.updatedAt.replace('T', ' ') }}。
      賽季結束後 iThome 的報名列表只保留完賽或達標的系列。我的最愛只存在這台裝置的瀏覽器（localStorage）。
    </footer>
  </div>
</template>

<style scoped>
/* ── 頁首：品牌、搜尋、分頁同一排；手機上搜尋換到第二排 ── */
.site-head {
  position: sticky; top: env(safe-area-inset-top, 0px); z-index: 5;
  background: color-mix(in srgb, var(--paper) 92%, transparent);
  backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--line);
}
.head-row { display: flex; align-items: center; gap: .6rem 1.5rem; padding-block: .7rem; }
.brand { display: flex; align-items: baseline; gap: .6rem; min-width: 0; flex: none; }
.brand h1 { margin: 0; font-family: var(--font-display); font-size: 1.3rem; font-weight: 700; white-space: nowrap; }
.brand h1 b { color: var(--accent); }
.home { color: inherit; }
.home:hover { color: inherit; opacity: .85; }
.brand small { color: var(--ink-soft); font-size: .78rem; font-family: var(--font-mono); white-space: nowrap; }
.tabs { display: flex; gap: .2rem; margin-left: auto; flex: none; }
.tabs button {
  border: 0; background: none; cursor: pointer; padding: .35rem .75rem; border-radius: 999px;
  color: var(--ink-soft); font-size: .95rem; font-weight: 500;
}
.tabs button:hover { color: var(--ink); background: var(--wash); }
.tabs button[aria-pressed="true"] { color: var(--paper); background: var(--ink); }

.search-wrap { flex: 1 1 auto; max-width: 30rem; display: flex; gap: .5rem; align-items: center; min-width: 0; }
.search {
  flex: 1; min-width: 0; display: flex; align-items: center; gap: .5rem;
  border: 1px solid var(--line); border-radius: 999px; padding: .4rem .5rem .4rem .9rem; background: var(--wash);
  transition: border-color .15s, background .15s;
}
.search:focus-within { border-color: color-mix(in srgb, var(--accent) 45%, var(--line)); background: var(--paper); }
.search input { border: 0; outline: 0; background: none; width: 100%; min-width: 0; font-size: .95rem; padding-block: .1rem; }
.search input::-webkit-search-cancel-button { -webkit-appearance: none; appearance: none; }
.search > svg { flex: none; color: var(--ink-soft); }
.clear { flex: none; width: 1.6rem; height: 1.6rem; display: grid; place-items: center; border: 0; border-radius: 999px; background: none; cursor: pointer; color: var(--ink-soft); }
.clear:hover { background: var(--line); color: var(--ink); }
.clear svg { width: .9rem; height: .9rem; }
.filter-btn {
  display: none; align-items: center; gap: .35rem; flex: none; cursor: pointer;
  border: 1px solid var(--line); border-radius: 999px; padding: .45rem 1rem; background: var(--paper); font-size: .92rem;
}
.dot { display: inline-grid; place-items: center; min-width: 1.25rem; height: 1.25rem; padding-inline: .3rem; border-radius: 999px; background: var(--accent); color: var(--paper); font-size: .72rem; font-family: var(--font-mono); }

/* ── chip：取代下拉選單，點擊範圍至少 36px 高 ── */
.chips { display: flex; flex-wrap: wrap; gap: .4rem; min-width: 0; }
.chip {
  display: inline-flex; align-items: center; gap: .35rem; min-height: 2.25rem; cursor: pointer;
  border: 1px solid var(--line); border-radius: 999px; padding: .3rem .85rem; background: var(--paper); font-size: .9rem;
}
.chip:hover { border-color: color-mix(in srgb, var(--accent) 45%, var(--line)); }
.chip[aria-pressed="true"] { border-color: color-mix(in srgb, var(--accent) 50%, transparent); background: var(--accent-wash); color: var(--accent-ink); font-weight: 600; }
.chip .n { font-family: var(--font-mono); font-size: .74rem; color: var(--ink-soft); font-weight: 400; }
/* 主題 chip 帶主題色，選中時整顆上色 */
.theme-chip::before { content: ""; width: .5rem; height: .5rem; border-radius: 2px; background: var(--tint-ink); }
.theme-chip[aria-pressed="true"] { color: var(--tint-ink); background: var(--tint-wash); border-color: var(--tint-line); }
.divider { width: 1px; align-self: stretch; margin-inline: .3rem; background: var(--line); }

/* ── 依主題分區 ── */
.theme-sec + .theme-sec { margin-top: 2.25rem; }
.theme-head {
  display: flex; align-items: baseline; gap: .75rem; flex-wrap: wrap;
  margin-bottom: .9rem; padding-bottom: .5rem; border-bottom: 2px solid var(--tint-line);
}
.theme-head h3 { margin: 0; font-size: 1.15rem; color: var(--tint-ink); }
.theme-meta { font-size: .82rem; color: var(--ink-soft); }
.see-all { margin-left: auto; border: 0; background: none; cursor: pointer; font-size: .88rem; color: var(--tint-ink); padding: .2rem 0; }
.see-all:hover { text-decoration: underline; text-underline-offset: 3px; }

/* ── 篩選：桌機攤在清單上方；手機變成底部滑出面板 ── */
main { padding-block: 1.25rem 4rem; display: grid; gap: 1.5rem; }
.filters { display: grid; gap: .5rem; padding-bottom: 1.25rem; border-bottom: 1px solid var(--line); }
.frow { display: grid; grid-template-columns: 3rem 1fr; gap: .75rem; align-items: start; }
.flabel { font-size: .82rem; color: var(--ink-soft); padding-top: .45rem; }
.sheet-head { display: none; }
.backdrop { display: none; }

.list-head { display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem; }
.list-tools { display: flex; align-items: center; gap: .75rem; flex-wrap: wrap; }
.list-tools .seg button { padding: .25rem .8rem; font-size: .85rem; }
.rows { list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--line); }
.list-head .meta { color: var(--ink-soft); font-size: .85rem; font-family: var(--font-mono); }
.more { display: flex; justify-content: center; margin-top: 1.25rem; }
.more button { border: 1px solid var(--line); background: var(--paper); border-radius: 999px; padding: .6rem 1.4rem; cursor: pointer; }
.more button:hover { border-color: var(--accent); color: var(--accent-ink); }
.empty { grid-column: 1 / -1; padding: 3rem 1rem; text-align: center; color: var(--ink-soft); border: 1px dashed var(--line); border-radius: var(--radius); }
.skeleton { min-height: 9.5rem; background: var(--wash); border-color: transparent; animation: pulse 1.2s ease-in-out infinite alternate; }
@keyframes pulse { to { opacity: .55; } }
.foot { padding-block: 0 3rem; color: var(--ink-soft); font-size: .8rem; }

@media (max-width: 900px) {
  .head-row { flex-wrap: wrap; padding-block: .6rem; }
  .search-wrap { order: 3; flex-basis: 100%; max-width: none; }
}
@media (max-width: 720px) {
  .brand small { display: none; }
  .tabs { margin-left: auto; }
  .tabs button { padding: .35rem .6rem; font-size: .9rem; }
  .filter-btn { display: inline-flex; }

  .filters {
    position: fixed; z-index: 20; left: 0; right: 0; bottom: 0;
    max-height: 80dvh; overflow-y: auto;
    padding: 0 max(16px, env(safe-area-inset-right, 0px)) calc(1.25rem + env(safe-area-inset-bottom, 0px)) max(16px, env(safe-area-inset-left, 0px));
    background: var(--paper); border: 1px solid var(--line); border-radius: 1rem 1rem 0 0;
    box-shadow: 0 -12px 32px -16px color-mix(in srgb, var(--ink) 50%, transparent);
    transform: translateY(105%); transition: transform .2s ease; visibility: hidden;
  }
  .filters.open { transform: none; visibility: visible; }
  .frow { grid-template-columns: 1fr; gap: .4rem; }
  .flabel { padding-top: 0; }
  .sheet-head {
    display: flex; align-items: center; gap: 1rem; position: sticky; top: 0; z-index: 1;
    padding-block: 1rem .5rem; background: var(--paper);
  }
  .sheet-head strong { font-size: 1.05rem; margin-right: auto; }
  .sheet-head .link { border: 0; background: none; color: var(--ink-soft); cursor: pointer; padding: .4rem; }
  .sheet-head .done { border: 0; border-radius: 999px; background: var(--ink); color: var(--paper); padding: .45rem 1.1rem; cursor: pointer; }
  .backdrop { display: block; position: fixed; inset: 0; z-index: 15; background: color-mix(in srgb, var(--ink) 35%, transparent); }
}
@media (prefers-reduced-motion: reduce) { .skeleton { animation: none; } }
</style>
