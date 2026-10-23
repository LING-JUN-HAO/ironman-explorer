<script setup lang="ts">
import type { Series } from '~/composables/useIronman'
import type { Article } from '~/composables/useArticles'

const props = defineProps<{ series: Series }>()
const emit = defineEmits<{ close: [], author: [userId: number] }>()

const articles = ref<Article[] | null>(null)
const failed = ref(false)
const panel = ref<HTMLElement>()

watch(() => props.series.id, async (id) => {
  articles.value = null
  failed.value = false
  try {
    const list = await fetchOutline(id)
    if (props.series.id === id) articles.value = list
  }
  catch {
    failed.value = true
  }
}, { immediate: true })

function onKey(e: KeyboardEvent) {
  if (e.key === 'Escape') emit('close')
}
onMounted(() => {
  document.addEventListener('keydown', onKey)
  document.documentElement.style.overflow = 'hidden'
  panel.value?.focus()
})
onBeforeUnmount(() => {
  document.removeEventListener('keydown', onKey)
  document.documentElement.style.overflow = ''
})
</script>

<template>
  <div class="layer">
    <div class="backdrop" aria-hidden="true" @click="emit('close')" />
    <aside ref="panel" class="panel" role="dialog" aria-modal="true" aria-labelledby="outline-title" tabindex="-1">
      <header class="panel-head">
        <div class="meta">
          <span class="yr">{{ series.year }}</span>
          <TierBadge :tier="series.tier" />
          <span class="grp">{{ series.group }}</span>
        </div>
        <button type="button" class="close" aria-label="關閉大綱" @click="emit('close')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18" /></svg>
        </button>
      </header>

      <div class="panel-body">
        <h2 id="outline-title">{{ series.title }}</h2>
        <p class="by">
          <button type="button" class="author" @click="emit('author', series.userId)">{{ series.name }}</button>
          <template v-if="series.team"> · 團隊 {{ series.team }}</template>
        </p>
        <p v-if="series.desc" class="desc">{{ series.desc }}</p>

        <div class="list-head">
          <h3>文章大綱</h3>
          <span v-if="articles" class="count">{{ articles.length }} 篇</span>
        </div>
        <p v-if="failed" class="note">這個系列的大綱還沒抓到，可以直接到系列頁看。</p>
        <ol v-else-if="articles" class="articles">
          <li v-for="(a, i) in articles" :key="a.id">
            <span class="day">{{ String(i + 1).padStart(2, '0') }}</span>
            <a :href="articleUrl(a.id)" target="_blank" rel="noopener">{{ a.title }}</a>
            <time :datetime="a.date">{{ a.date.slice(5).replace('-', '/') }}</time>
          </li>
        </ol>
        <div v-else class="loading" aria-live="polite">
          <span v-for="i in 8" :key="i" />
        </div>
      </div>

      <footer class="panel-foot">
        <a class="primary" :href="seriesUrl(series)" target="_blank" rel="noopener">前往整個系列</a>
        <button type="button" class="ghost" @click="emit('author', series.userId)">{{ series.name }} 的其他作品</button>
      </footer>
    </aside>
  </div>
</template>

<style scoped>
.layer { position: fixed; inset: 0; z-index: 30; }
.backdrop { position: absolute; inset: 0; background: color-mix(in srgb, var(--ink) 35%, transparent); }
.panel {
  position: absolute; top: 0; right: 0; bottom: 0; width: min(34rem, 100%);
  display: grid; grid-template-rows: auto 1fr auto;
  background: var(--paper); border-left: 1px solid var(--line);
  box-shadow: -16px 0 40px -24px color-mix(in srgb, var(--ink) 60%, transparent);
  padding-top: env(safe-area-inset-top, 0px);
  animation: slide-in .2s ease;
  outline: none;
}
@keyframes slide-in { from { transform: translateX(24px); opacity: 0; } }

.panel-head { display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: .9rem 1.25rem .5rem; }
.meta { display: flex; align-items: center; gap: .4rem; flex-wrap: wrap; min-width: 0; }
.grp { font-family: var(--font-mono); font-size: .75rem; color: var(--ink-soft); }
.close { flex: none; width: 2.25rem; height: 2.25rem; display: grid; place-items: center; border: 0; border-radius: 999px; background: none; cursor: pointer; color: var(--ink-soft); }
.close:hover { background: var(--wash); color: var(--ink); }
.close svg { width: 1.2rem; height: 1.2rem; }

.panel-body { overflow-y: auto; overscroll-behavior: contain; padding: 0 1.25rem 1.25rem; min-height: 0; }
h2 { margin: .25rem 0 .35rem; font-size: 1.3rem; line-height: 1.4; text-wrap: balance; overflow-wrap: anywhere; }
.by { margin: 0 0 .75rem; color: var(--ink-soft); font-size: .9rem; }
.author { border: 0; background: none; padding: 0; cursor: pointer; color: var(--accent-ink); font-weight: 500; text-decoration: underline; text-underline-offset: 3px; text-decoration-color: color-mix(in srgb, var(--accent) 40%, transparent); }
.desc { margin: 0 0 1.25rem; color: var(--ink-soft); font-size: .9rem; }

.list-head { display: flex; align-items: baseline; gap: .6rem; border-top: 1px solid var(--line); padding-top: 1rem; margin-bottom: .5rem; }
.list-head h3 { margin: 0; font-size: 1rem; }
.count { font-family: var(--font-mono); font-size: .8rem; color: var(--ink-soft); }
.articles { list-style: none; margin: 0; padding: 0; display: grid; }
.articles li { display: grid; grid-template-columns: 2rem 1fr auto; gap: .6rem; align-items: baseline; padding: .5rem 0; border-bottom: 1px dashed var(--line); min-width: 0; }
.articles .day { font-family: var(--font-mono); font-size: .78rem; color: var(--accent-ink); }
.articles a { line-height: 1.5; overflow-wrap: anywhere; }
.articles time { font-family: var(--font-mono); font-size: .72rem; color: var(--ink-soft); }
.note { color: var(--ink-soft); font-size: .9rem; }
.loading { display: grid; gap: .6rem; padding-top: .5rem; }
.loading span { height: 1.1rem; border-radius: 4px; background: var(--wash); animation: pulse 1.2s ease-in-out infinite alternate; }
.loading span:nth-child(odd) { width: 85%; }
@keyframes pulse { to { opacity: .5; } }

.panel-foot {
  display: flex; gap: .6rem; flex-wrap: wrap; border-top: 1px solid var(--line);
  padding: .85rem 1.25rem calc(.85rem + env(safe-area-inset-bottom, 0px));
}
.primary, .ghost { display: inline-flex; align-items: center; justify-content: center; min-height: 2.5rem; padding: .4rem 1.1rem; border-radius: 999px; font-size: .92rem; cursor: pointer; }
.primary { background: var(--ink); color: var(--paper); font-weight: 600; }
.primary:hover { color: var(--paper); background: var(--accent-ink); }
.ghost { border: 1px solid var(--line); background: var(--paper); }
.ghost:hover { border-color: var(--accent); color: var(--accent-ink); }

@media (max-width: 720px) {
  .panel {
    top: auto; left: 0; width: 100%; max-height: 88dvh; border-left: 0; border-top: 1px solid var(--line);
    border-radius: 1rem 1rem 0 0; padding-top: 0; animation-name: slide-up;
  }
  @keyframes slide-up { from { transform: translateY(32px); opacity: 0; } }
  .panel-foot > * { flex: 1; }
}
@media (prefers-reduced-motion: reduce) { .panel, .loading span { animation: none; } }
</style>
