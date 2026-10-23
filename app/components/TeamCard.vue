<script setup lang="ts">
import { BASE, PERSONAL_TIERS, type Series, type Team } from '~/composables/useIronman'

const props = defineProps<{ team: Team }>()
const emit = defineEmits<{ outline: [series: Series], author: [userId: number] }>()

// 團長排第一，其餘成員依個人獎項排序
const members = computed(() => [...props.team.members].sort((a, b) =>
  Number(b.userId === props.team.leaderId) - Number(a.userId === props.team.leaderId)
  || tierRank(PERSONAL_TIERS, a.tier) - tierRank(PERSONAL_TIERS, b.tier),
))

// 大隊伍先收合，避免同一排卡片高低差太多
const PREVIEW = 4
const expanded = ref(false)
const visible = computed(() => (expanded.value ? members.value : members.value.slice(0, PREVIEW)))
const hidden = computed(() => members.value.length - PREVIEW)
</script>

<template>
  <article class="card" :class="{ won: team.tier || team.wins }">
    <FavButton :fav-key="favKey('t', team.year, team.id)" :label="team.name" />
    <div class="card-top">
      <span class="yr">{{ team.year }}</span>
      <TierBadge :tier="team.tier" />
      <span v-if="team.wins" class="wins">成員得獎 {{ team.wins }}</span>
      <span v-if="team.status" class="grp">{{ team.status }}</span>
    </div>
    <h3>
      <a :href="`${BASE}/${team.year}ironman/signup/team/${team.id}`" target="_blank" rel="noopener">{{ team.name }}</a>
    </h3>
    <p v-if="team.intro" class="desc">{{ team.intro }}</p>
    <ul class="members">
      <li v-for="m in visible" :key="m.id">
        <span class="title">
          <TierBadge :tier="m.tier" />
          <button type="button" class="link" :title="`看「${m.title}」每日文章標題`" @click="emit('outline', m)">{{ m.title }}</button>
        </span>
        <button type="button" class="who" :class="{ lead: m.userId === team.leaderId }" :title="`看 ${m.name} 的所有作品`" @click="emit('author', m.userId)">{{ m.name }}</button>
      </li>
      <li v-if="!members.length"><span class="who">成員系列不在名單上</span></li>
    </ul>
    <div class="card-foot">
      <span>{{ team.members.length }} 個系列</span>
      <button v-if="hidden > 0" type="button" class="more" :aria-expanded="expanded" @click="expanded = !expanded">
        {{ expanded ? '收合' : `還有 ${hidden} 個系列` }}
      </button>
    </div>
  </article>
</template>

<style scoped>
.wins { font-size: .74rem; padding: .1rem .5rem; border-radius: 999px; color: var(--ink-soft); background: var(--wash); }
.members { list-style: none; margin: 0; padding: .55rem 0 0; display: grid; gap: .3rem; border-top: 1px dashed var(--line); }
.members li { display: grid; grid-template-columns: 1fr auto; gap: .5rem; align-items: baseline; font-size: .85rem; min-width: 0; }
.title { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; display: flex; gap: .35rem; align-items: baseline; }
.link { min-width: 0; overflow: hidden; text-overflow: ellipsis; border: 0; background: none; padding: 0; font: inherit; color: var(--ink); cursor: pointer; text-align: left; }
.link:hover { color: var(--accent-ink); }
.who { color: var(--ink-soft); white-space: nowrap; border: 0; background: none; padding: 0; font: inherit; cursor: pointer; }
button.who:hover { color: var(--accent-ink); text-decoration: underline; text-underline-offset: 3px; }
.more { border: 0; background: none; padding: 0; font: inherit; color: var(--accent-ink); cursor: pointer; }
.more:hover { text-decoration: underline; text-underline-offset: 3px; }
.lead::after { content: "團長"; font-size: .68rem; margin-left: .3rem; color: var(--accent-ink); }
</style>
