<script setup lang="ts">
import type { Series } from '~/composables/useIronman'

// hint：搜尋不是命中系列標題時，標出命中的位置（例如哪一篇文章）
const props = defineProps<{ series: Series, hint?: string | null }>()
const emit = defineEmits<{ outline: [series: Series], author: [userId: number] }>()
const pct = computed(() => Math.min(100, Math.round((props.series.day / 30) * 100)))

// 整張卡片都能點開大綱；點到卡片裡的其他按鈕（作者、收藏）時交給那些按鈕處理
function onCardClick(e: MouseEvent) {
  if ((e.target as HTMLElement).closest('a, button')) return
  emit('outline', props.series)
}
</script>

<template>
  <article class="card clickable" :class="{ won: series.tier }" @click="onCardClick">
    <FavButton :fav-key="favKey('s', series.year, series.id)" :label="series.title" />
    <div class="card-top">
      <span class="yr">{{ series.year }}</span>
      <TierBadge :tier="series.tier" />
      <ThemeTag :theme="series.theme" />
      <span class="grp">{{ series.group }}</span>
    </div>
    <h3>
      <button type="button" class="open" :title="`看「${series.title}」每日文章標題`" @click="emit('outline', series)">{{ series.title }}</button>
    </h3>
    <p v-if="hint" class="hint">{{ hint }}</p>
    <p v-else-if="series.desc" class="desc">{{ series.desc }}</p>
    <div class="card-foot">
      <span class="who">
        <button type="button" class="author" :title="`看 ${series.name} 的所有作品`" @click="emit('author', series.userId)">{{ series.name }}</button>
        <template v-if="series.team"> · {{ series.team }}</template>
      </span>
      <span class="day" :title="`完成 ${series.day} 天`"><i :style="{ '--p': `${pct}%` }" />{{ series.day }}/30</span>
    </div>
    <span class="cue" aria-hidden="true">看每日文章標題 <span class="chev">›</span></span>
  </article>
</template>

<style scoped>
.hint {
  margin: 0; font-size: .82rem; color: var(--accent-ink); line-height: 1.5;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.author { border: 0; background: none; padding: 0; font: inherit; color: var(--ink); cursor: pointer; position: relative; z-index: 1; }
.author:hover { color: var(--accent-ink); text-decoration: underline; text-underline-offset: 3px; }
.day { font-family: var(--font-mono); font-size: .75rem; display: inline-flex; align-items: center; gap: .4rem; flex: none; }
.day i { display: block; width: 3.2rem; height: 4px; border-radius: 2px; background: var(--line); overflow: hidden; }
.day i::after { content: ""; display: block; height: 100%; width: var(--p); background: var(--accent); }
.clickable { cursor: pointer; }
.clickable:hover { border-color: color-mix(in srgb, var(--accent) 55%, var(--line)); transform: translateY(-2px); }
.clickable:hover .open { color: var(--accent-ink); }
.open {
  border: 0; background: none; padding: 0; font: inherit; color: var(--ink); cursor: pointer; text-align: left;
}
.cue {
  display: flex; align-items: center; justify-content: space-between; padding-top: .55rem;
  border-top: 1px dashed var(--line); font-size: .82rem; color: var(--ink-soft); transition: color .12s;
}
.chev { font-size: 1.15rem; line-height: 1; transition: transform .12s; }
.clickable:hover .cue { color: var(--accent-ink); }
.clickable:hover .chev { transform: translateX(3px); }
@media (prefers-reduced-motion: reduce) { .clickable:hover { transform: none; } .chev { transition: none; } }
</style>
