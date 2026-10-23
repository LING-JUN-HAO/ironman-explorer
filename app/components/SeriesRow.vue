<script setup lang="ts">
import type { Series } from '~/composables/useIronman'

const props = defineProps<{ series: Series, hint?: string | null }>()
const emit = defineEmits<{ outline: [series: Series], author: [userId: number] }>()

// 整列都能點開大綱；點到列裡的其他按鈕（作者、收藏）時交給那些按鈕處理
function onRowClick(e: MouseEvent) {
  if ((e.target as HTMLElement).closest('a, button')) return
  emit('outline', props.series)
}
</script>

<template>
  <li class="row" :class="{ won: series.tier }" @click="onRowClick">
    <span class="yr">{{ series.year }}</span>
    <div class="main">
      <span class="title">
        <TierBadge :tier="series.tier" />
        <button type="button" class="open" :title="`看「${series.title}」每日文章標題`" @click="emit('outline', series)">{{ series.title }}</button>
      </span>
      <span v-if="hint" class="hint">{{ hint }}</span>
    </div>
    <span class="grp"><ThemeTag :theme="series.theme" /><span>{{ series.group }}</span></span>
    <button type="button" class="author" :title="`看 ${series.name} 的所有作品`" @click="emit('author', series.userId)">{{ series.name }}</button>
    <span class="day">{{ series.day }}/30</span>
    <span class="actions">
      <FavButton :fav-key="favKey('s', series.year, series.id)" :label="series.title" inline />
      <span class="chevron" aria-hidden="true">›</span>
    </span>
  </li>
</template>

<style scoped>
.row {
  display: grid; grid-template-columns: 3rem minmax(0, 1fr) 13rem 8rem 3.2rem auto;
  gap: .25rem 1rem; align-items: center; padding: .55rem .5rem; border-bottom: 1px solid var(--line);
  cursor: pointer; transition: background .12s;
}
.row:hover { background: var(--wash); }
.row:hover .open { color: var(--accent-ink); }
.row:hover .chevron { opacity: 1; transform: none; }
.row.won .open { font-weight: 700; }
.main { min-width: 0; display: grid; gap: .1rem; }
.title { display: flex; align-items: baseline; gap: .45rem; min-width: 0; }
.open {
  min-width: 0; border: 0; background: none; padding: 0; font: inherit; color: var(--ink); cursor: pointer;
  text-align: left; overflow-wrap: anywhere; line-height: 1.45; font-weight: 500;
}
.hint { font-size: .78rem; color: var(--accent-ink); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.grp { display: flex; align-items: center; gap: .4rem; min-width: 0; font-family: var(--font-mono); font-size: .74rem; color: var(--ink-soft); }
.grp > span:last-child { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.author {
  justify-self: start; max-width: 100%;
  border: 0; background: none; padding: 0; font: inherit; font-size: .85rem; color: var(--ink-soft); cursor: pointer;
  text-align: left; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.author:hover { color: var(--accent-ink); text-decoration: underline; text-underline-offset: 3px; }
.day { font-family: var(--font-mono); font-size: .75rem; color: var(--ink-soft); text-align: right; }
.actions { display: flex; align-items: center; gap: .1rem; }
.chevron {
  width: 1rem; text-align: center; font-size: 1.25rem; line-height: 1; color: var(--accent-ink);
  opacity: 0; transform: translateX(-4px); transition: opacity .12s, transform .12s;
}

/* 手機：年度、組別一行；標題一行；作者、天數、動作一行 */
@media (max-width: 720px) {
  .row {
    grid-template-columns: auto minmax(0, 1fr) auto;
    grid-template-areas: "yr grp grp" "main main main" "author day actions";
    gap: .2rem .6rem; padding: .7rem .25rem;
  }
  .yr { grid-area: yr; }
  .grp { grid-area: grp; }
  .main { grid-area: main; }
  .author { grid-area: author; }
  .day { grid-area: day; }
  .actions { grid-area: actions; }
  .chevron { opacity: 1; transform: none; }
}
@media (prefers-reduced-motion: reduce) { .row, .chevron { transition: none; } }
</style>
