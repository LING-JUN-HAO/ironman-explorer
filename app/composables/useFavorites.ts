const KEY = 'ironman-explorer:favorites'

export type FavKind = 's' | 't'
export const favKey = (kind: FavKind, year: number, id: number) => `${kind}:${year}:${id}`

/** 我的最愛只存在這台裝置的 localStorage；伺服器端渲染時一律視為空集合。 */
export function useFavorites() {
  const favs = useState<string[]>('favorites', () => [])

  /** 由頁面在 onMounted 呼叫一次 */
  function load() {
    try {
      favs.value = JSON.parse(localStorage.getItem(KEY) ?? '[]')
    }
    catch {
      favs.value = []
    }
  }

  const set = computed(() => new Set(favs.value))

  function toggle(key: string) {
    favs.value = set.value.has(key) ? favs.value.filter(k => k !== key) : [...favs.value, key]
    try {
      localStorage.setItem(KEY, JSON.stringify(favs.value))
    }
    catch {
      // 無痕模式或封鎖儲存時，只在本次瀏覽生效
    }
  }

  return { load, favs: set, count: computed(() => favs.value.length), toggle, has: (key: string) => set.value.has(key) }
}
