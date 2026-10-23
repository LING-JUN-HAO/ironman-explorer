<script setup lang="ts">
import type { Series } from '~/composables/useIronman'

const props = defineProps<{ userId: number, works: Series[], backLabel?: string }>()
const emit = defineEmits<{ back: [] }>()

// 名稱與頭像取最近一屆的，作者可能改過暱稱
const latest = computed(() => props.works.toSorted((a, b) => b.year - a.year)[0])
const avatar = computed(() => props.works.find(w => w.avatar)?.avatar ?? null)
// iThome 的圖片載不出來時改顯示名字第一個字
const broken = ref(false)
watch(() => props.userId, () => { broken.value = false })
const years = computed(() => [...new Set(props.works.map(w => w.year))].sort((a, b) => a - b))
const wins = computed(() => props.works.filter(w => w.tier).length)
</script>

<template>
  <div class="author-head">
    <img v-if="avatar && !broken" class="avatar" :src="avatarUrl(avatar)" :alt="`${latest?.name} 的頭像`" width="64" height="64" @error="broken = true">
    <span v-else class="avatar placeholder" aria-hidden="true">{{ latest?.name.slice(0, 1) }}</span>
    <div class="info">
      <h2 id="list-title" class="sec">{{ latest?.name }} 的所有作品</h2>
      <p class="stats">
        參賽 {{ works.length }} 次<template v-if="years.length"> · {{ years.join('、') }}</template><template v-if="wins"> · 得獎 {{ wins }} 次</template>
      </p>
      <p class="links">
        <a :href="profileUrl(userId)" target="_blank" rel="noopener">iT 邦幫忙個人頁</a>
        <button type="button" class="back" @click="emit('back')">{{ backLabel ?? '回到全部作品' }}</button>
      </p>
    </div>
  </div>
</template>

<style scoped>
.author-head { display: flex; align-items: center; gap: 1rem; min-width: 0; }
.avatar { flex: none; width: 4rem; height: 4rem; border-radius: 999px; object-fit: cover; background: var(--wash); border: 1px solid var(--line); }
.placeholder { display: grid; place-items: center; font-size: 1.5rem; font-weight: 700; color: var(--ink-soft); }
.info { min-width: 0; display: grid; gap: .15rem; }
.info h2 { margin: 0; overflow-wrap: anywhere; }
.stats { margin: 0; font-size: .85rem; color: var(--ink-soft); }
.links { margin: .2rem 0 0; display: flex; align-items: center; gap: .75rem; flex-wrap: wrap; font-size: .85rem; }
.links a { color: var(--accent-ink); text-decoration: underline; text-underline-offset: 3px; text-decoration-color: color-mix(in srgb, var(--accent) 40%, transparent); }
.back {
  border: 1px solid var(--line); border-radius: 999px; background: var(--paper); cursor: pointer;
  font-size: .82rem; padding: .25rem .8rem; color: var(--ink-soft);
}
.back:hover { border-color: var(--accent); color: var(--accent-ink); }
</style>
