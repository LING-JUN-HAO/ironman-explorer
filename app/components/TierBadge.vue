<script setup lang="ts">
defineProps<{ tier: string | null }>()
</script>

<template>
  <span v-if="tier" class="badge" :data-tier="tier">{{ tier }}</span>
</template>

<style scoped>
.badge {
  display: inline-flex; align-items: center; flex: none; white-space: nowrap;
  font-size: .74rem; font-weight: 700; letter-spacing: .04em; padding: .1rem .5rem; border-radius: 999px;
  color: var(--ink-soft); background: var(--wash);
}
.badge[data-tier="冠軍"], .badge[data-tier="最佳團隊獎"] { color: var(--gold); background: var(--gold-wash); }
.badge[data-tier="優選"], .badge[data-tier="眾志成城"] { color: var(--silver); background: var(--silver-wash); }
.badge[data-tier="佳作"] { color: var(--bronze); background: var(--bronze-wash); }
.badge[data-tier="佛心分享推薦"] { color: var(--heart); background: var(--heart-wash); }
</style>
