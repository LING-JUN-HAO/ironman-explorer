import type { ThemeId } from './themes'

export const PERSONAL_TIERS = ['冠軍', '優選', '佳作', '佛心分享推薦'] as const
export const TEAM_TIERS = ['最佳團隊獎', '眾志成城'] as const
export const BASE = 'https://ithelp.ithome.com.tw'

export type Tier = (typeof PERSONAL_TIERS)[number] | (typeof TEAM_TIERS)[number]

type RawSeries = { id: number, userId: number, name: string, group: string, title: string, desc: string, day: number, avatar?: number | null }
type RawTeam = { id: number, name: string, intro: string, status: string, leaderId: number | null, memberIds: number[] }
export type PersonalAward = { seriesId: number, userId: number, tier: Tier, name: string, group: string, title: string }
export type TeamAward = { tier: Tier, name: string, seriesIds: number[] }
type RawYear = { series: RawSeries[], teams: RawTeam[], personalAwards: PersonalAward[], teamAwards: TeamAward[] }
export type Raw = { updatedAt: string, years: Record<string, RawYear> }

export type Series = RawSeries & { year: number, tier: Tier | null, team: string | null, theme: ThemeId }
export type Team = RawTeam & { year: number, tier: Tier | null, members: Series[], wins: number }
export type YearData = { series: Series[], teams: Team[], personalAwards: PersonalAward[], teamAwards: TeamAward[] }
export type Ironman = {
  years: number[]
  db: Record<number, YearData>
  series: Series[]
  teams: Team[]
  updatedAt: string
  /** 最近一屆已公布得獎名單的年度 */
  latestAwardedYear: number
}

export const tierRank = (tiers: readonly string[], tier: string | null) => (tier ? tiers.indexOf(tier) : 99)
export const seriesUrl = (s: { userId: number, id: number }) => `${BASE}/users/${s.userId}/ironman/${s.id}`
export const profileUrl = (userId: number) => `${BASE}/users/${userId}/profile`
export const avatarUrl = (avatar: number) => `https://member.ithome.com.tw/avatars/${avatar}?s=ithelp`

/** 沒有任何條件時的系列排序：獎項 → 年度新到舊 → 完成天數 */
export const compareSeries = (a: Series, b: Series) =>
  tierRank(PERSONAL_TIERS, a.tier) - tierRank(PERSONAL_TIERS, b.tier) || b.year - a.year || b.day - a.day || a.id - b.id

/** 把每屆的系列掛上個人獎項與所屬團隊，團隊掛上成員系列與團體獎項。 */
function buildYear(year: number, y: RawYear): YearData {
  const award = new Map(y.personalAwards.map(a => [a.seriesId, a.tier]))
  const series: Series[] = y.series.map(s => ({ ...s, year, tier: award.get(s.id) ?? null, team: null, theme: themeOf(s.group) }))

  // 得獎系列偶爾不在報名列表上（上游名單異動），用得獎資料補進來
  const known = new Set(series.map(s => s.id))
  for (const a of y.personalAwards) {
    if (!known.has(a.seriesId)) {
      series.push({ id: a.seriesId, userId: a.userId, name: a.name, group: a.group, title: a.title, desc: '', day: 30, year, tier: a.tier, team: null, theme: themeOf(a.group) })
    }
  }

  const byUser = Map.groupBy(series, s => s.userId)
  const teamAward = new Map(y.teamAwards.map(a => [a.name.trim(), a.tier]))
  const teams: Team[] = y.teams.map((t) => {
    const members = t.memberIds.flatMap(u => byUser.get(u) ?? [])
    members.forEach((m) => { m.team = t.name })
    return { ...t, year, members, tier: teamAward.get(t.name.trim()) ?? null, wins: members.filter(m => m.tier).length }
  })

  return { series, teams, personalAwards: y.personalAwards, teamAwards: y.teamAwards }
}

export function buildIronman(raw: Raw): Ironman {
  const years = Object.keys(raw.years).map(Number).sort((a, b) => b - a)
  const db = Object.fromEntries(years.map(y => [y, buildYear(y, raw.years[y]!)])) as Record<number, YearData>
  return {
    years,
    db,
    series: years.flatMap(y => db[y]!.series),
    teams: years.flatMap(y => db[y]!.teams),
    updatedAt: raw.updatedAt,
    latestAwardedYear: years.find(y => db[y]!.personalAwards.length) ?? years[0]!,
  }
}

// 資料放在 public/data，只在瀏覽器端抓一次；JSON 解析比把資料打包進 JS 快得多
const data = shallowRef<Ironman | null>(null)
const error = ref<string | null>(null)
let loading: Promise<void> | null = null

export function useIronman() {
  if (import.meta.client && !loading) {
    loading = $fetch<Raw>('/data/ironman.json')
      .then((raw) => { data.value = buildIronman(raw) })
      .catch(() => { error.value = '資料載入失敗，請重新整理頁面。' })
  }
  return { data, error }
}
