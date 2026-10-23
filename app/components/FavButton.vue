<script setup lang="ts">
// inline：放在列表列裡，不浮在卡片右上角
const props = defineProps<{ favKey: string, label: string, inline?: boolean }>()
const { has, toggle } = useFavorites()
const on = computed(() => has(props.favKey))
</script>

<template>
  <button
    type="button"
    class="fav"
    :class="{ inline }"
    :aria-pressed="on"
    :aria-label="`${on ? '移出' : '加入'}我的最愛：${label}`"
    @click="toggle(favKey)"
  >
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
      <path d="M12 20.5s-7.5-4.6-7.5-10.2A4.3 4.3 0 0 1 12 7.6a4.3 4.3 0 0 1 7.5 2.7c0 5.6-7.5 10.2-7.5 10.2Z" />
    </svg>
  </button>
</template>

<style scoped>
.fav {
  position: absolute; top: .7rem; right: .7rem; width: 2rem; height: 2rem; display: grid; place-items: center;
  border: 0; background: none; cursor: pointer; border-radius: 999px; color: var(--ink-soft);
}
.fav.inline { position: static; flex: none; }
.fav:hover { background: var(--wash); color: var(--accent); }
.fav[aria-pressed="true"] { color: var(--accent); }
.fav[aria-pressed="true"] path { fill: currentColor; }
svg { width: 1.15rem; height: 1.15rem; }
</style>
