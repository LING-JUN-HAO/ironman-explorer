<script setup lang="ts">
import { PERSONAL_TIERS, type PersonalAward, type YearData } from '~/composables/useIronman'

const props = defineProps<{ year: number, data: YearData }>()
const view = ref<'tier' | 'group'>('tier')

const byTier = computed(() => PERSONAL_TIERS
  .map(tier => ({ tier, list: props.data.personalAwards.filter(a => a.tier === tier) }))
  .filter(b => b.list.length))

// 佛心分享排在主題競賽之後
const byGroup = computed(() => {
  const groups = Map.groupBy(props.data.personalAwards, a => a.group)
  return [...groups.entries()]
    .sort(([a], [b]) => Number(a.startsWith('佛心')) - Number(b.startsWith('佛心')) || a.localeCompare(b, 'zh-Hant'))
    .map(([group, list]) => ({ group, list: list.toSorted((a, b) => tierRank(PERSONAL_TIERS, a.tier) - tierRank(PERSONAL_TIERS, b.tier)) }))
})

const teamAwards = computed(() => props.data.teamAwards.map((a) => {
  const team = props.data.teams.find(t => t.name.trim() === a.name.trim())
  const leader = team?.members.find(m => m.userId === team.leaderId)?.name
  return { ...a, leader }
}))

const url = (a: PersonalAward) => seriesUrl({ userId: a.userId, id: a.seriesId })
</script>

<template>
  <section aria-labelledby="awards-title">
    <div class="head">
      <div>
        <h2 id="awards-title" class="sec">
          {{ year }} 得獎主題
          <span v-if="data.personalAwards.length" class="meta">個人 {{ data.personalAwards.length }} 件 · 團體 {{ data.teamAwards.length }} 隊</span>
        </h2>
        <p v-if="data.personalAwards.length" class="lead">點標題可直接前往 iT 邦幫忙的系列頁面。</p>
      </div>
      <div v-if="data.personalAwards.length" class="seg" role="group" aria-label="得獎主題排列方式">
        <button type="button" :aria-pressed="view === 'tier'" @click="view = 'tier'">依獎項</button>
        <button type="button" :aria-pressed="view === 'group'" @click="view = 'group'">依組別</button>
      </div>
    </div>

    <div v-if="!data.personalAwards.length" class="pending">
      {{ year }} 的得獎名單還沒公布。iThome 通常在賽季結束後的 11～12 月公告，公布後執行 <code>pnpm scrape</code> 重新抓資料就會出現在這裡。
    </div>

    <template v-else-if="view === 'tier'">
      <div v-for="b in byTier" :key="b.tier" class="tier-block">
        <h3 class="tier-title"><TierBadge :tier="b.tier" /><span class="count">{{ b.list.length }} 件</span></h3>
        <ul class="topic-grid">
          <li v-for="a in b.list" :key="a.seriesId">
            <a class="t" :href="url(a)" target="_blank" rel="noopener">{{ a.title }}</a>
            <span class="s"><span class="g">{{ a.group }}</span><span>{{ a.name }}</span></span>
          </li>
        </ul>
      </div>
      <div v-if="teamAwards.length" class="tier-block">
        <h3 class="tier-title">團體組</h3>
        <ul class="topic-grid">
          <li v-for="a in teamAwards" :key="a.name">
            <span class="t"><TierBadge :tier="a.tier" /> {{ a.name }}</span>
            <span class="s">{{ a.seriesIds.length }} 個系列<template v-if="a.leader"> · 團長 {{ a.leader }}</template></span>
          </li>
        </ul>
      </div>
    </template>

    <template v-else>
      <div v-for="g in byGroup" :key="g.group" class="group-block">
        <h3>{{ g.group }}</h3>
        <ul>
          <li v-for="a in g.list" :key="a.seriesId">
            <TierBadge :tier="a.tier" />
            <a :href="url(a)" target="_blank" rel="noopener">{{ a.title }}</a>
            <span class="who">{{ a.name }}</span>
          </li>
        </ul>
      </div>
    </template>
  </section>
</template>

<style scoped>
.head { display: flex; align-items: flex-end; justify-content: space-between; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.25rem; }
.lead { margin: 0; color: var(--ink-soft); font-size: .9rem; }
.pending { padding: 1.5rem; border: 1px dashed var(--line); border-radius: var(--radius); color: var(--ink-soft); background: var(--wash); }
.pending code { font-family: var(--font-mono); font-size: .85em; color: var(--ink); }

.tier-block + .tier-block { margin-top: 1.75rem; }
.tier-title { display: flex; align-items: center; gap: .6rem; margin: 0 0 .5rem; font-size: 1rem; font-weight: 700; }
.count { font-family: var(--font-mono); font-size: .8rem; color: var(--ink-soft); font-weight: 400; }
.topic-grid { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 20rem), 1fr)); gap: 0 1.75rem; }
.topic-grid li { min-width: 0; padding: .55rem 0; border-top: 1px dashed var(--line); display: grid; gap: .1rem; }
.t { font-weight: 500; line-height: 1.45; overflow-wrap: anywhere; }
.s { font-size: .8rem; color: var(--ink-soft); display: flex; gap: .5rem; flex-wrap: wrap; }
.g { font-family: var(--font-mono); font-size: .74rem; }

.group-block { display: grid; grid-template-columns: 11rem 1fr; gap: .5rem 1.5rem; padding: .75rem 0; border-top: 1px solid var(--line); }
.group-block h3 { margin: 0; font-size: .95rem; font-family: var(--font-mono); font-weight: 600; }
.group-block ul { list-style: none; margin: 0; padding: 0; display: grid; gap: .35rem; min-width: 0; }
.group-block li { display: flex; gap: .5rem; align-items: baseline; min-width: 0; }
.group-block li a { min-width: 0; overflow-wrap: anywhere; }
.who { color: var(--ink-soft); font-size: .8rem; white-space: nowrap; margin-left: auto; }

@media (max-width: 640px) {
  .group-block { grid-template-columns: 1fr; }
}
</style>
