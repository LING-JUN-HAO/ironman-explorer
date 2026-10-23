<script setup lang="ts">
import { themeById, type ThemeId } from '~/composables/themes'

const props = defineProps<{ theme: ThemeId }>()
const t = computed(() => themeById.get(props.theme)!)
</script>

<template>
  <span class="tag theme-tint" :class="{ neutral: theme === 'other' }" :style="{ '--hue': t.hue }">{{ t.label }}</span>
</template>

<style scoped>
.tag {
  display: inline-flex; align-items: center; flex: none; white-space: nowrap;
  font-size: .72rem; font-weight: 600; padding: .05rem .5rem; border-radius: 4px;
  color: var(--tint-ink); background: var(--tint-wash);
}
</style>
