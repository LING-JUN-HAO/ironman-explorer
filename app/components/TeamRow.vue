<script setup lang="ts">
import { BASE, type Team } from '~/composables/useIronman'

const props = defineProps<{ team: Team }>()
const emit = defineEmits<{ author: [userId: number] }>()
const leader = computed(() => props.team.members.find(m => m.userId === props.team.leaderId))
</script>

<template>
  <li class="row" :class="{ won: team.tier || team.wins }">
    <span class="yr">{{ team.year }}</span>
    <div class="main">
      <span class="title">
        <TierBadge :tier="team.tier" />
        <a :href="`${BASE}/${team.year}ironman/signup/team/${team.id}`" target="_blank" rel="noopener">{{ team.name }}</a>
      </span>
      <span class="names">
        <template v-for="(m, i) in team.members" :key="m.id"><template v-if="i">、</template><button type="button" class="name" :class="{ won: m.tier }" :title="`看 ${m.name} 的所有作品`" @click="emit('author', m.userId)">{{ m.name }}</button></template>
      </span>
    </div>
    <span class="stat">{{ team.members.length }} 個系列<template v-if="team.wins"> · 得獎 {{ team.wins }}</template></span>
    <button v-if="leader" type="button" class="author" :title="`看 ${leader.name} 的所有作品`" @click="emit('author', leader.userId)">團長 {{ leader.name }}</button>
    <span v-else />
    <FavButton :fav-key="favKey('t', team.year, team.id)" :label="team.name" inline />
  </li>
</template>

<style scoped>
.row {
  display: grid; grid-template-columns: 3rem minmax(0, 1fr) 9rem 10rem auto;
  gap: .25rem 1rem; align-items: center; padding: .55rem .5rem; border-bottom: 1px solid var(--line);
}
.row:hover { background: var(--wash); }
.row.won .title a { font-weight: 700; }
.main { min-width: 0; display: grid; gap: .1rem; }
.names { font-size: .78rem; color: var(--ink-soft); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.name { border: 0; background: none; padding: 0; font: inherit; color: inherit; cursor: pointer; }
.name.won { color: var(--ink); font-weight: 600; }
.name:hover { color: var(--accent-ink); text-decoration: underline; }
.title { display: flex; align-items: baseline; gap: .45rem; min-width: 0; }
.title a { min-width: 0; overflow-wrap: anywhere; font-weight: 500; }
.stat { font-size: .8rem; color: var(--ink-soft); white-space: nowrap; }
.author {
  border: 0; background: none; padding: 0; font: inherit; font-size: .85rem; color: var(--ink-soft); cursor: pointer;
  text-align: left; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.author:hover { color: var(--accent-ink); text-decoration: underline; text-underline-offset: 3px; }

@media (max-width: 720px) {
  .row {
    grid-template-columns: auto minmax(0, 1fr) auto;
    grid-template-areas: "yr title fav" "stat author author";
    gap: .2rem .6rem; padding: .7rem .25rem;
  }
  .main { grid-area: title; }
  .stat { grid-area: stat; }
  .author { grid-area: author; }
  .row > :last-child { grid-area: fav; }
}
</style>
